"""FontLab scope, validation, preview, undoable writes, and setup exchange."""

import copy
import io
from contextlib import redirect_stdout
import json
import math
from pathlib import Path

from .model import Font, master_context, STORAGE_KEY
from .upstream import load

DEFAULTS = {"paramArea": 400.0, "paramDepth": 15.0, "paramOver": 0.0, "paramFreq": 5.0}


def finite_number(value, name, minimum=0):
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError("%s must be finite and at least %s." % (name, minimum))
    return value


def validate_parameters(params):
    for key, value in params.items():
        if key not in DEFAULTS:
            raise ValueError("Unknown parameter: " + key)
        finite_number(value, key, 1 if key == "paramFreq" else 0)


def validate_rules(rules):
    if not isinstance(rules, dict):
        raise ValueError("Rules must be an object keyed by rule ID.")
    for rid, rule in rules.items():
        if not isinstance(rule, dict):
            raise ValueError("Invalid rule " + str(rid))
        for key in ("area", "depth"):
            spec = rule.get(key)
            if spec is not None:
                if not isinstance(spec, dict) or spec.get("mode") not in (
                    "percent",
                    "absolute",
                ):
                    raise ValueError("Invalid %s spec in %s" % (key, rid))
                finite_number(spec.get("value"), key)
        if "glyphlist" in rule and (
            not isinstance(rule["glyphlist"], list)
            or not all(isinstance(n, str) for n in rule["glyphlist"])
        ):
            raise ValueError("glyphlist must be a list of names.")


class Session:
    def __init__(self, raw):
        if raw is None or raw.isNull:
            raise ValueError("Open a font in FontLab first.")
        self.upstream = load()
        self.font = Font(raw)
        self.raw = raw
        self.rules = self.upstream.config.read_font_rules(self.font)
        # Distinguish an explicitly empty setup from a new font.
        if (
            self.font.userData[self.upstream.config.FONT_RULES_KEY] is None
            and not self.rules
        ):
            self.rules = self.upstream.config.default_rules()
        self.last_results = []

    @classmethod
    def current(cls):
        import fontlab as fl

        return cls(fl.flWorkspace.instance().currentPackage)

    def master(self, name=None):
        return self.font.master_by_name[name or self.raw.master]

    def assert_current(self):
        import fontlab as fl

        current = fl.flWorkspace.instance().currentPackage
        if current is None or current.isNull or current.id != self.raw.id:
            raise ValueError(
                "The active font changed. Click Reload font before applying."
            )

    def names(self, scope="selection"):
        self.assert_current()
        if scope == "font":
            return [g.name for g in self.font.glyphs]
        if scope == "tab":
            import fontlab as fl

            canvas = fl.flWorkspace.instance().getActiveCanvas()
            if canvas is None or canvas.isNull:
                raise ValueError("Open a Glyph window for Apply to current tab.")
            names = []
            for block in canvas.textBlocks():
                for info in block.getAllGlyphs():
                    if info.glyph.package.id == self.raw.id:
                        names.append(info.glyph.name)
        else:
            import fontpr

            response = fontpr.get_current_glyphs()
            names = [g["name"] for g in response.get("glyphs", [])]
        names = list(dict.fromkeys(names))
        if not names:
            raise ValueError(
                "Select glyphs in the Font window or open a Glyph window first."
            )
        return names

    def _engine(self, layer, params=None, manual=None):
        validate_parameters(params or {})
        if layer.master.xHeight <= 0:
            raise ValueError("Master %s needs a positive x-height." % layer.master.name)
        # Glyphs resolves metric keys on the glyph; FontLab has per-layer keys.
        layer.parent.leftMetricsKey = layer.raw.metricsLeft or None
        layer.parent.rightMetricsKey = layer.raw.metricsRight or None
        original_freq = layer.master.customParameters.get("paramFreq")
        if params and "paramFreq" in params:
            layer.master.customParameters["paramFreq"] = params["paramFreq"]
        try:
            engine = self.upstream.engine.HTLSEngine(
                layer,
                font_rules={} if manual is not None else self.rules,
                param_overrides=params,
            )
        finally:
            if original_freq is None:
                layer.master.customParameters.pop("paramFreq", None)
            else:
                layer.master.customParameters["paramFreq"] = original_freq
        if manual is not None:
            engine.LSB = manual.get("LSB", True)
            engine.RSB = manual.get("RSB", True)
            engine.tabVersion = manual.get("tabular", False)
            if engine.tabVersion and manual.get("width"):
                engine.width = finite_number(manual["width"], "Tabular width", 0)
        return engine

    def calculate(
        self,
        names=None,
        scope="selection",
        all_masters=False,
        master=None,
        params=None,
        manual=None,
    ):
        self.assert_current()
        validate_rules(self.rules)
        names = list(dict.fromkeys(names if names is not None else self.names(scope)))
        master_names = (
            list(self.font.master_by_name)
            if all_masters
            else [master or self.raw.master]
        )
        results = []
        for name in names:
            glyph = self.font.glyphs[name]
            if glyph is None:
                raise ValueError("Missing glyph: " + name)
            for master_name in master_names:
                layer = glyph.layers[master_name]
                if layer is None:
                    results.append(
                        {
                            "name": name,
                            "master": master_name,
                            "skip": "Missing master layer",
                            "layer": None,
                        }
                    )
                    continue
                layer.refresh()
                engine = self._engine(layer, params, manual)
                result = {
                    "name": name,
                    "master": master_name,
                    "layer": layer,
                    "engine": engine,
                    "before": (layer.LSB, layer.RSB, layer.width),
                }
                if layer.raw.isLocked:
                    result["skip"] = "Locked layer"
                elif layer.raw.metricsWidth:
                    result["skip"] = "Width metric expression"
                elif layer.bounds[3] - layer.bounds[1] < engine.paramFreq * 2:
                    result["skip"] = "Empty or too short for two sampling rows"
                else:
                    output = io.StringIO()
                    with redirect_stdout(output):
                        sb = engine.current_layer_sidebearings()
                    if output.getvalue():
                        raise RuntimeError(
                            "Upstream engine failed for %s [%s]:\n%s"
                            % (name, master_name, output.getvalue())
                        )
                    if sb is None:
                        result["skip"] = (
                            engine.output.strip() or "No measurable reference zone"
                        )
                    elif not all(math.isfinite(v) for v in sb):
                        raise ValueError("Non-finite spacing for " + name)
                    else:
                        left, right = sb
                        # Honor side locks also in upstream's tabular path.
                        left_locked = not engine.LSB or bool(layer.raw.metricsLeft)
                        right_locked = not engine.RSB or bool(layer.raw.metricsRight)
                        if engine.tabVersion and (left_locked or right_locked):
                            left, right = layer.LSB, layer.RSB
                        else:
                            if left_locked:
                                left = layer.LSB
                            if right_locked:
                                right = layer.RSB
                        width = (
                            (
                                layer.width
                                if left_locked or right_locked
                                else engine.newWidth or layer.width
                            )
                            if engine.tabVersion
                            else layer.width + (left - layer.LSB) + (right - layer.RSB)
                        )
                        if width < 0:
                            raise ValueError(
                                "Calculated negative advance width for " + name
                            )
                        if engine.tabVersion:
                            # Setting the final advance width overrides the engine's
                            # sampled RSB. Report the bearing the host will actually
                            # store after translating the outline by the new LSB.
                            right = layer.RSB + width - layer.width - (left - layer.LSB)
                        result.update(
                            after=(left, right, width),
                            polygons=engine.calculate_polygons(),
                        )
                results.append(result)
        self.last_results = results
        return results

    def apply(self, preserve_components=True, **kwargs):
        import fontlab as fl
        from PythonQt import QtGui
        from .components import references, compensate

        results = self.calculate(**kwargs)  # All validation before the first write.
        reverse = references(self.raw, {r["master"] for r in results})
        # Bases precede composites, also when preservation is disabled.
        by_key = {(r["name"], r["master"]): r for r in results}
        order = []
        visiting = set()
        visited = set()
        deps = {key: set() for key in by_key}
        for base, refs in reverse.items():
            for shape, layer, glyph in refs:
                owner = (glyph.name, layer.name)
                if owner in deps and base in by_key:
                    deps[owner].add(base)

        def visit(key):
            if key in visiting:
                raise ValueError("Cyclic component dependency: " + key[0])
            if key in visited:
                return
            visiting.add(key)
            for dep in sorted(deps[key]):
                visit(dep)
            visiting.remove(key)
            visited.add(key)
            order.append(by_key[key])

        for key in by_key:
            visit(key)
        layer_objects = {
            r["layer"].raw.id: r["layer"].raw for r in results if "after" in r
        }
        changed = {
            r["layer"].parent.raw.id: r["layer"].parent.raw
            for r in results
            if "after" in r
        }
        if preserve_components:
            for key in by_key:
                for shape, layer, glyph in reverse.get(key, []):
                    layer_objects[layer.id] = layer
                    changed[glyph.id] = glyph
        snapshots = [(raw, raw.clone()) for raw in layer_objects.values()]
        targets = list(changed.values())
        if targets:
            fl.flItems.notifyChangesApplied("HT Letterspacer", targets, True)
        preferences = fl.flPreferences()
        old_round = preferences.editorStrongRound
        preferences.editorStrongRound = False
        try:
            for r in order:
                if "after" not in r:
                    continue
                if not preserve_components and deps[(r["name"], r["master"])]:
                    fresh = self.calculate(
                        names=[r["name"]],
                        master=r["master"],
                        params=kwargs.get("params"),
                        manual=kwargs.get("manual"),
                    )[0]
                    r.update(fresh)
                    if "skip" in fresh:
                        continue
                layer = r["layer"]
                raw = layer.raw
                delta = r["after"][0] - r["before"][0]
                if abs(delta) < 1e-7 and abs(r["after"][2] - raw.advanceWidth) < 1e-7:
                    continue
                raw.applyTransform(
                    QtGui.QTransform(1.0, 0.0, 0.0, 1.0, float(delta), 0.0)
                )
                raw.advanceWidth = r["after"][2]
                raw.changed()
                layer.parent.raw.update()
                if preserve_components and delta:
                    compensate(reverse.get((r["name"], r["master"]), []), delta)
            if targets:
                fl.flItems.notifyChangesApplied("HT Letterspacer", targets, True)
                fl.flItems.notifyPackageContentUpdated(self.raw.fgPackage.id)
                fl.Update(self.raw)
        except Exception:
            for raw, snapshot in reversed(snapshots):
                glyph = raw.glyph
                glyph.removeLayer(raw)
                glyph.addLayer(snapshot)
            fl.Update(self.raw)
            raise
        finally:
            preferences.editorStrongRound = old_round
        self.last_results = results
        return results

    def save(self):
        import fontlab as fl

        self.assert_current()
        validate_rules(self.rules)
        for master in self.font.masters:
            validate_parameters(master.customParameters)
        self.upstream.config.write_font_rules(self.font, self.rules)
        fl.flItems.notifyChangesApplied("HTLS configuration", [self.raw], True)
        self.font.commit()
        fl.flItems.notifyChangesApplied("HTLS configuration", [self.raw], True)
        fl.Update(self.raw)

    def export_setup(self, path):
        # Serialize working state without mutating the font.
        self.upstream.config.write_font_rules(self.font, self.rules)
        data = json.loads(self.upstream.config.serialize_setup(self.font))
        data["fontlab"] = {
            "version": 1,
            "classifications": self.font.classifications,
            "sampling": {
                m.name: m.customParameters.get("paramFreq", 5)
                for m in self.font.masters
            },
        }
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def import_setup(self, path, master_map=None):
        text = Path(path).read_text(encoding="utf-8")
        if not text.lstrip().startswith("{"):
            rules = self.upstream.config.parse_config_text(text)
            if not rules:
                raise ValueError("No valid legacy rules in this file.")
            validate_rules(rules)
            self.rules = rules
            return []
        data = self.upstream.config.parse_setup_text(text)
        validate_rules(
            {r.get("id", str(i)): r for i, r in enumerate(data.get("rules", []))}
        )
        for m in data.get("masters", []):
            validate_parameters(m.get("parameters", {}))
            validate_rules(m.get("overrides", {}))
        mapping = (
            master_map
            if master_map is not None
            else {
                m["name"]: m["name"]
                for m in data.get("masters", [])
                if m["name"] in self.font.master_by_name
            }
        )
        self.rules = self.upstream.config.import_setup(
            self.font, data, master_map=mapping, import_params=True
        )
        extension = data.get("fontlab", {})
        self.font.classifications = copy.deepcopy(extension.get("classifications", {}))
        for name, freq in extension.get("sampling", {}).items():
            if name in mapping:
                self.font.master_by_name[mapping[name]].customParameters[
                    "paramFreq"
                ] = finite_number(freq, "paramFreq", 1)
        return [m["name"] for m in data.get("masters", []) if m["name"] not in mapping]
