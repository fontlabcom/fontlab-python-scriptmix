"""Native PythonQt control window. UI is separate from upstream mathematics."""

import copy
import json
import traceback
from pathlib import Path
from PythonQt import QtCore, QtGui

from .qt import prop
from .service import Session, DEFAULTS, validate_rules

_window = None


def text(widget):
    return str(prop(widget, "text"))


def checked(widget):
    return bool(prop(widget, "checked"))


def current(widget):
    return str(prop(widget, "currentText"))


def connect(widget, signal, fn):
    widget.connect(signal, fn)


def button(label, callback, layout):
    b = QtGui.QPushButton(label)
    connect(b, "clicked()", callback)
    layout.addWidget(b)
    return b


def combo(items):
    c = QtGui.QComboBox()
    c.addItems([str(x) for x in items])
    return c


def select(c, value):
    index = c.findText(str(value))
    if index < 0:
        c.addItem(str(value))
        index = c.findText(str(value))
    c.setCurrentIndex(index)


def spin(minimum=0, maximum=100000, decimals=2):
    s = QtGui.QDoubleSpinBox()
    s.setRange(minimum, maximum)
    s.setDecimals(decimals)
    return s


def page(tabs, label):
    w = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(w)
    tabs.addTab(w, label)
    return w, layout


class Window:
    def __init__(self):
        self.session = Session.current()
        self.loading = True
        self.active_rule = None
        self.dialog = QtGui.QDialog()
        self.dialog.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.dialog.setWindowTitle("HT Letterspacer — FontLab 9")
        self.dialog.resize(1040, 850)
        outer = QtGui.QVBoxLayout(self.dialog)
        header = QtGui.QHBoxLayout()
        outer.addLayout(header)
        self.font_label = QtGui.QLabel()
        header.addWidget(self.font_label)
        header.addStretch(1)
        header.addWidget(QtGui.QLabel("Master"))
        self.master_box = combo(self.session.font.master_by_name)
        header.addWidget(self.master_box)
        select(self.master_box, self.session.raw.master)
        button("Reload font", lambda: self.safe(self.reload), header)
        self.tabs = QtGui.QTabWidget()
        outer.addWidget(self.tabs)
        self.make_rules()
        self.make_masters()
        self.make_parameters()
        self.make_inspector()
        actions = QtGui.QHBoxLayout()
        outer.addLayout(actions)
        button(
            "Apply to selection",
            lambda: self.safe(lambda: self.apply("selection")),
            actions,
        )
        button(
            "Apply to current tab",
            lambda: self.safe(lambda: self.apply("tab")),
            actions,
        )
        self.all_masters = QtGui.QCheckBox("All masters")
        actions.addWidget(self.all_masters)
        self.live = QtGui.QCheckBox("Live tab apply")
        actions.addWidget(self.live)
        self.keep_components = QtGui.QCheckBox("Keep components")
        self.keep_components.setChecked(True)
        actions.addWidget(self.keep_components)
        actions.addStretch(1)
        button("Save configuration", lambda: self.safe(self.save), actions)
        self.status = QtGui.QLabel(
            "Ready. Preview is non-destructive. Apply writes spacing and supports Undo."
        )
        self.status.setWordWrap(True)
        outer.addWidget(self.status)
        self.timer = QtCore.QTimer(self.dialog)
        self.timer.setSingleShot(True)
        connect(self.timer, "timeout()", lambda: self.safe(self.refresh_preview))
        connect(
            self.master_box,
            "currentIndexChanged(int)",
            lambda *_: self.safe(self.master_changed),
        )
        connect(
            self.live,
            "toggled(bool)",
            lambda enabled: self.status.setText(
                "Live tab apply writes spacing after edits. Undo is available."
                if enabled
                else "Live tab apply off."
            ),
        )
        from .reporter import Reporter

        self.reporter = Reporter(self)
        connect(self.dialog, "finished(int)", lambda *_: self.closed())
        self.load_all()
        self.loading = False
        self.safe(self.refresh_preview)

    def safe(self, fn):
        try:
            return fn()
        except Exception as exc:
            self.live.setChecked(False)
            self.status.setText("Error: " + str(exc))
            traceback.print_exc()
            return None

    def make_rules(self):
        _, layout = page(self.tabs, "Font rules")
        toolbar = QtGui.QHBoxLayout()
        layout.addLayout(toolbar)
        button("+ Add", lambda: self.safe(self.add_rule), toolbar)
        button("From selection", lambda: self.safe(self.rule_from_selection), toolbar)
        button("Duplicate", lambda: self.safe(self.duplicate_rule), toolbar)
        button("Remove", lambda: self.safe(self.remove_rule), toolbar)
        toolbar.addStretch(1)
        button("Import…", lambda: self.safe(self.import_file), toolbar)
        button("Export setup…", lambda: self.safe(self.export_file), toolbar)
        button("Export legacy…", lambda: self.safe(self.export_legacy), toolbar)
        body = QtGui.QHBoxLayout()
        layout.addLayout(body)
        self.rule_list = QtGui.QListWidget()
        self.rule_list.setMinimumWidth(310)
        body.addWidget(self.rule_list, 1)
        form = QtGui.QFormLayout()
        body.addLayout(form, 2)
        self.rule_fields = {}
        fields = [
            ("name", "Rule name"),
            ("category", "Category"),
            ("script", "Script"),
            ("subcategory", "Subcategory"),
            ("case", "Case"),
            ("filter", "Name fragments"),
            ("reference", "Reference glyph"),
        ]
        for key, label in fields:
            if key == "category":
                widget = combo(
                    [
                        "Any",
                        "Letter",
                        "Number",
                        "Punctuation",
                        "Symbol",
                        "Mark",
                        "Separator",
                        "Other",
                    ]
                )
            elif key == "case":
                widget = combo(["Any", "upper", "lower", "smallCaps", "minor", "Other"])
            else:
                widget = QtGui.QLineEdit()
            self.rule_fields[key] = widget
            form.addRow(label, widget)
        self.rule_specs = {}
        for key in ("area", "depth"):
            row = QtGui.QHBoxLayout()
            mode = combo(["percent", "absolute"])
            val = spin()
            row.addWidget(val)
            row.addWidget(mode)
            form.addRow(key.capitalize(), row)
            self.rule_specs[key] = (mode, val)
        self.glyphlist = QtGui.QPlainTextEdit()
        self.glyphlist.setMaximumHeight(70)
        form.addRow("Glyph list (comma or newline)", self.glyphlist)
        row = QtGui.QHBoxLayout()
        self.lsb = QtGui.QCheckBox("LSB")
        self.rsb = QtGui.QCheckBox("RSB")
        self.tabular = QtGui.QCheckBox("Fixed width")
        for w in (self.lsb, self.rsb, self.tabular):
            row.addWidget(w)
        form.addRow("Write sides", row)
        b = QtGui.QPushButton("Update rule")
        connect(b, "clicked()", lambda: self.safe(self.update_rule))
        form.addRow(b)
        hint = QtGui.QLabel(
            "Script and subcategory use Glyphs names, e.g. latin, Currency, Decimal Digit.\nAny means unrestricted. Update rule keeps its ID and master overrides."
        )
        hint.setWordWrap(True)
        form.addRow(hint)
        connect(
            self.rule_list,
            "currentRowChanged(int)",
            lambda row: self.safe(lambda: self.load_rule(row)),
        )

    def make_masters(self):
        _, layout = page(self.tabs, "Master rules")
        layout.addWidget(
            QtGui.QLabel(
                "Override Area and Depth for the selected master. Uncheck to inherit the font rule."
            )
        )
        self.override_list = QtGui.QListWidget()
        layout.addWidget(self.override_list)
        form = QtGui.QFormLayout()
        layout.addLayout(form)
        self.override_specs = {}
        for key in ("area", "depth"):
            row = QtGui.QHBoxLayout()
            enabled = QtGui.QCheckBox("Override")
            value = spin()
            mode = combo(["percent", "absolute"])
            for w in (enabled, value, mode):
                row.addWidget(w)
            form.addRow(key.capitalize(), row)
            self.override_specs[key] = (enabled, value, mode)
        row = QtGui.QHBoxLayout()
        layout.addLayout(row)
        button("Update override", lambda: self.safe(self.update_override), row)
        button("Clear override", lambda: self.safe(self.clear_override), row)
        connect(
            self.override_list,
            "currentRowChanged(int)",
            lambda *_: self.safe(self.load_override),
        )

    def make_parameters(self):
        _, layout = page(self.tabs, "Parameters & preview")
        row = QtGui.QHBoxLayout()
        layout.addLayout(row)
        self.params = {}
        for key, label in [
            ("paramArea", "Area"),
            ("paramDepth", "Depth %"),
            ("paramOver", "Overshoot %"),
            ("paramFreq", "Step"),
        ]:
            row.addWidget(QtGui.QLabel(label))
            s = spin(
                1 if key == "paramFreq" else 0, 100000, 0 if key == "paramFreq" else 2
            )
            row.addWidget(s)
            self.params[key] = s
            connect(s, "valueChanged(double)", lambda *_: self.parameters_changed())
        row = QtGui.QHBoxLayout()
        layout.addLayout(row)
        self.copy_master = combo(self.session.font.master_by_name)
        row.addWidget(self.copy_master)
        button("Copy parameters", lambda: self.safe(self.copy_parameters), row)
        self.interpolate_a = combo(self.session.font.master_by_name)
        self.interpolate_b = combo(self.session.font.master_by_name)
        row.addWidget(self.interpolate_a)
        row.addWidget(self.interpolate_b)
        self.interpolate_t = spin(0, 100, 1)
        self.interpolate_t.setValue(50)
        row.addWidget(self.interpolate_t)
        button("Interpolate %", lambda: self.safe(self.interpolate_parameters), row)
        row = QtGui.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtGui.QLabel("Preview text"))
        self.preview_text = QtGui.QLineEdit("noon")
        row.addWidget(self.preview_text, 1)
        self.areas = QtGui.QCheckBox("Show areas")
        self.areas.setChecked(True)
        row.addWidget(self.areas)
        self.overlay = QtGui.QCheckBox("Areas in Glyph window")
        row.addWidget(self.overlay)
        connect(
            self.overlay,
            "toggled(bool)",
            lambda enabled: self.safe(
                self.reporter.start if enabled else self.reporter.stop
            ),
        )
        button("Refresh", lambda: self.safe(self.refresh_preview), row)
        connect(self.preview_text, "textChanged(QString)", lambda *_: self.schedule())
        connect(self.areas, "toggled(bool)", lambda *_: self.schedule())
        self.scene = QtGui.QGraphicsScene()
        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setMinimumHeight(220)
        layout.addWidget(self.view, 1)
        self.manual = QtGui.QGroupBox(
            "Apply HTLS Values — use these parameters without stored rules"
        )
        ml = QtGui.QHBoxLayout(self.manual)
        self.manual_lsb = QtGui.QCheckBox("LSB")
        self.manual_rsb = QtGui.QCheckBox("RSB")
        self.manual_tab = QtGui.QCheckBox("Fixed width")
        self.manual_lsb.setChecked(True)
        self.manual_rsb.setChecked(True)
        for w in (self.manual_lsb, self.manual_rsb, self.manual_tab):
            ml.addWidget(w)
        button("Apply values to selection", lambda: self.safe(self.apply_manual), ml)
        layout.addWidget(self.manual)
        hint = QtGui.QLabel(
            "Use /H /o /zero.tf for glyph names. Parameters are working values until Save configuration.\nComponent placements are preserved. Non-master layers and automatic layers are skipped."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def make_inspector(self):
        _, layout = page(self.tabs, "Inspector")
        button("Inspect selection", lambda: self.safe(self.inspect), layout)
        self.inspector = QtGui.QPlainTextEdit()
        self.inspector.setReadOnly(True)
        layout.addWidget(self.inspector)
        layout.addWidget(
            QtGui.QLabel("Classification overrides (JSON by glyph name; optional):")
        )
        self.classification_edit = QtGui.QPlainTextEdit()
        self.classification_edit.setMaximumHeight(110)
        layout.addWidget(self.classification_edit)
        button(
            "Update classifications",
            lambda: self.safe(self.update_classifications),
            layout,
        )

    def title_rule(self, r):
        return (
            r.get("name")
            or " / ".join(
                str(r.get(k))
                for k in ("category", "script", "case", "filter")
                if r.get(k) not in (None, "", 0, "Any")
            )
            or "All glyphs"
        )

    def refresh_rules(self, selected=None):
        self.loading = True
        self.ids = list(self.session.rules)
        self.rule_list.clear()
        self.override_list.clear()
        for rid in self.ids:
            r = self.session.rules[rid]
            title = self.title_rule(r)
            self.rule_list.addItem(title)
            self.override_list.addItem(title)
        index = self.ids.index(selected) if selected in self.ids else 0
        self.rule_list.setCurrentRow(index)
        self.override_list.setCurrentRow(index)
        self.loading = False
        self.load_rule(index)
        self.load_override()

    def load_all(self):
        self.font_label.setText(self.session.font.familyName or "Untitled font")
        self.refresh_rules()
        self.load_parameters()
        self.classification_edit.setPlainText(
            json.dumps(self.session.font.classifications, indent=2)
        )

    def load_rule(self, row):
        if self.loading or row < 0 or row >= len(self.ids):
            return
        self.active_rule = self.ids[row]
        r = self.session.rules[self.active_rule]
        for key, w in self.rule_fields.items():
            if key == "category":
                select(w, r.get(key) or "Any")
            elif key == "case":
                w.setCurrentIndex(int(r.get(key) or 0))
            else:
                w.setText(
                    str(
                        r.get(key)
                        or ("Any" if key in ("script", "subcategory") else "")
                    )
                )
        for key, (mode, value) in self.rule_specs.items():
            spec = r.get(key, {"mode": "percent", "value": 100})
            select(mode, spec["mode"])
            value.setValue(spec["value"])
        self.glyphlist.setPlainText(", ".join(r.get("glyphlist", [])))
        self.lsb.setChecked(r.get("sides", {}).get("LSB", True))
        self.rsb.setChecked(r.get("sides", {}).get("RSB", True))
        self.tabular.setChecked(bool(r.get("tabular")))

    def update_rule(self):
        if self.active_rule not in self.session.rules:
            return
        r = {}
        for key, w in self.rule_fields.items():
            r[key] = (
                int(prop(w, "currentIndex"))
                if key == "case"
                else current(w) if key == "category" else text(w).strip()
            )
        for key, (mode, value) in self.rule_specs.items():
            r[key] = {"mode": current(mode), "value": float(prop(value, "value"))}
        r["glyphlist"] = [
            n.strip()
            for n in str(prop(self.glyphlist, "plainText"))
            .replace("\n", ",")
            .split(",")
            if n.strip()
        ]
        r["sides"] = {"LSB": checked(self.lsb), "RSB": checked(self.rsb)}
        r["tabular"] = checked(self.tabular)
        validate_rules({self.active_rule: r})
        self.session.rules[self.active_rule] = self.session.upstream.config.make_rule(
            **r
        )
        self.refresh_rules(self.active_rule)
        self.edited()

    def structural_guard(self):
        if checked(self.live):
            raise ValueError("Turn off Live tab apply before adding or removing rules.")

    def add_rule(self):
        self.structural_guard()
        rid = self.session.upstream.config.new_rule_id()
        self.session.rules[rid] = self.session.upstream.config.make_rule(
            name="New rule"
        )
        self.refresh_rules(rid)
        self.schedule()

    def rule_from_selection(self):
        self.add_rule()
        self.session.rules[self.active_rule]["glyphlist"] = self.session.names()
        self.refresh_rules(self.active_rule)

    def duplicate_rule(self):
        self.structural_guard()
        if self.active_rule not in self.session.rules:
            return
        r = copy.deepcopy(self.session.rules[self.active_rule])
        r["name"] = self.title_rule(r) + " copy"
        rid = self.session.upstream.config.new_rule_id()
        self.session.rules[rid] = r
        self.refresh_rules(rid)

    def remove_rule(self):
        self.structural_guard()
        rid = self.active_rule
        self.session.rules.pop(rid, None)
        for m in self.session.font.masters:
            ov = m.userData[self.session.upstream.config.MASTER_RULES_KEY]
            if ov:
                ov.pop(rid, None)
        self.refresh_rules()
        self.schedule()

    def override_id(self):
        row = int(prop(self.override_list, "currentRow"))
        return self.ids[row] if 0 <= row < len(self.ids) else None

    def load_override(self):
        if self.loading:
            return
        rid = self.override_id()
        if rid is None:
            return
        master = self.session.master(current(self.master_box))
        ov = (master.userData[self.session.upstream.config.MASTER_RULES_KEY] or {}).get(
            rid, {}
        )
        for key, (enabled, value, mode) in self.override_specs.items():
            spec = ov.get(key) or self.session.rules[rid][key]
            enabled.setChecked(key in ov)
            value.setValue(spec["value"])
            select(mode, spec["mode"])

    def update_override(self):
        rid = self.override_id()
        if rid is None:
            return
        master = self.session.master(current(self.master_box))
        key = self.session.upstream.config.MASTER_RULES_KEY
        ov = dict(master.userData[key] or {})
        entry = {}
        for field, (enabled, value, mode) in self.override_specs.items():
            if checked(enabled):
                entry[field] = {
                    "mode": current(mode),
                    "value": float(prop(value, "value")),
                }
        if entry:
            ov[rid] = entry
        else:
            ov.pop(rid, None)
        master.userData[key] = ov
        self.edited()

    def clear_override(self):
        for enabled, _, _ in self.override_specs.values():
            enabled.setChecked(False)
        self.update_override()
        self.load_override()

    def load_parameters(self):
        self.loading = True
        m = self.session.master(current(self.master_box))
        for key, w in self.params.items():
            w.setValue(m.customParameters.get(key, DEFAULTS[key]))
        self.loading = False

    def parameters_changed(self):
        if self.loading:
            return
        m = self.session.master(current(self.master_box))
        for key, w in self.params.items():
            m.customParameters[key] = float(prop(w, "value"))
        self.edited()

    def master_changed(self):
        if self.loading:
            return
        self.load_parameters()
        self.load_override()
        self.schedule()

    def copy_parameters(self):
        source = self.session.master(current(self.copy_master))
        target = self.session.master(current(self.master_box))
        target.customParameters.update(source.customParameters)
        self.load_parameters()
        self.edited()

    def interpolate_parameters(self):
        a = self.session.master(current(self.interpolate_a))
        b = self.session.master(current(self.interpolate_b))
        target = self.session.master(current(self.master_box))
        t = float(prop(self.interpolate_t, "value")) / 100
        for key in ("paramArea", "paramDepth", "paramOver"):
            target.customParameters[key] = (1 - t) * a.customParameters.get(
                key, DEFAULTS[key]
            ) + t * b.customParameters.get(key, DEFAULTS[key])
        self.load_parameters()
        self.edited()

    def schedule(self):
        if not self.loading:
            self.timer.start(300)

    def edited(self):
        self.schedule()
        if checked(self.live):
            self.safe(lambda: self.apply("tab"))

    def preview_names(self):
        value = text(self.preview_text)
        if "/" in value:
            return [n for n in value.replace("/", " ").split() if n]
        names = []
        for char in value:
            raw = self.session.raw.findUnicode(ord(char))
            if raw is not None and not raw.isNull:
                names.append(raw.name)
        return names

    def refresh_preview(self):
        self.session.assert_current()
        names = self.preview_names()
        results = self.session.calculate(names=names, master=current(self.master_box))
        by_name = {r["name"]: r for r in results}
        self.scene.clear()
        x = 0.0
        palette = ["#008f9b", "#c36c31", "#6970b6", "#5c9146", "#ac568b"]
        for name in names[:64]:
            r = by_name.get(name)
            layer = r.get("layer") if r else None
            if layer is None:
                continue
            dx = r.get("after", r["before"])[0] - r["before"][0]
            transform = QtGui.QTransform(1.0, 0.0, 0.0, -1.0, x + dx, 0.0)
            ink = self.scene.addPath(
                transform.map(layer.path),
                QtGui.QPen(QtCore.Qt.NoPen),
                QtGui.QBrush(QtGui.QColor("#222222")),
            )
            if checked(self.areas) and r.get("polygons"):
                engine = r["engine"]
                rid = engine.matched_rule_id
                color = QtGui.QColor(
                    palette[self.ids.index(rid) % len(palette)]
                    if rid in self.ids
                    else "#888888"
                )
                color.setAlpha(90)
                for polygon in r["polygons"]:
                    path = QtGui.QPainterPath()
                    path.moveTo(polygon[0].x, polygon[0].y)
                    for p in polygon[1:]:
                        path.lineTo(p.x, p.y)
                    path.closeSubpath()
                    item = self.scene.addPath(
                        transform.map(path),
                        QtGui.QPen(QtCore.Qt.NoPen),
                        QtGui.QBrush(color),
                    )
                    item.setZValue(1)
            after = r.get("after", r["before"])
            label = self.scene.addText(
                "%s\n%.0f / %.0f → %.0f / %.0f"
                % (name, r["before"][0], r["before"][1], after[0], after[1])
            )
            label.setScale(2.5)
            label.setPos(x, 80)
            x += after[2] + 35
        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        self.view.fitInView(rect, QtCore.Qt.KeepAspectRatio)
        self.status.setText(
            "Preview: %d glyphs in %s. Changes are not saved until Save configuration."
            % (len(names), current(self.master_box))
        )

    def apply(self, scope, manual=None):
        kwargs = {
            "preserve_components": checked(self.keep_components),
            "scope": scope,
            "all_masters": checked(self.all_masters),
            "master": current(self.master_box),
        }
        if manual is not None:
            kwargs["manual"] = manual
            kwargs["params"] = {
                k: float(prop(w, "value")) for k, w in self.params.items()
            }
        results = self.session.apply(**kwargs)
        done = sum("after" in r for r in results)
        self.status.setText(
            "Applied spacing to %d layers; skipped %d. Edit → Undo restores the batch."
            % (done, len(results) - done)
        )
        self.render_report(results)

    def apply_manual(self):
        self.apply(
            "selection",
            {
                "LSB": checked(self.manual_lsb),
                "RSB": checked(self.manual_rsb),
                "tabular": checked(self.manual_tab),
            },
        )

    def render_report(self, results):
        lines = []
        for r in results:
            e = r.get("engine")
            g = r["layer"].parent if r.get("layer") else None
            lines.append(
                "%s [%s]  %s"
                % (
                    r["name"],
                    r["master"],
                    r.get("skip") or "%s → %s" % (r["before"], r.get("after")),
                )
            )
            if e:
                lines.append(
                    "  Category=%s, subcategory=%s, script=%s, case=%s"
                    % (g.category, g.subCategory, g.script, g.case)
                )
                lines.append(
                    "  Area=%s, depth=%s, reference=%s"
                    % (e.effectiveArea, e.effectiveDepth, e.reference_layer.parent.name)
                )
                for score, rid, rule in self.session.upstream.rules.rank_rules(
                    g, self.session.rules
                ):
                    lines.append(
                        "  %s %s (score %s)"
                        % (
                            "✓" if rid == e.matched_rule_id else " ",
                            self.title_rule(rule),
                            score,
                        )
                    )
        self.inspector.setPlainText("\n".join(lines))

    def inspect(self):
        self.render_report(
            self.session.calculate(
                master=current(self.master_box), all_masters=checked(self.all_masters)
            )
        )

    def update_classifications(self):
        data = json.loads(str(prop(self.classification_edit, "plainText")))
        if not isinstance(data, dict) or any(
            not isinstance(v, dict) for v in data.values()
        ):
            raise ValueError("Expected an object keyed by glyph name.")
        for name, attrs in data.items():
            if any(
                k not in ("category", "subCategory", "script", "case") for k in attrs
            ):
                raise ValueError("Unknown classification field for " + name)
            if "case" in attrs and attrs["case"] not in range(6):
                raise ValueError("case must be an integer from 0 to 5.")
        self.session.font.classifications = data
        self.session.font.glyphs.cache.clear()
        self.edited()

    def save(self):
        self.session.save()
        self.status.setText(
            "Configuration stored in the font. Save the font as VFJ/VFC to persist it on disk."
        )

    def choose_path(self, save=False, legacy=False):
        filters = (
            "Legacy rules (*.yml)"
            if legacy
            else "HTLS setup (*.json);;Legacy rules (*.yml *.py)"
        )
        method = (
            QtGui.QFileDialog.getSaveFileName
            if save
            else QtGui.QFileDialog.getOpenFileName
        )
        value = method(self.dialog, "HT Letterspacer", "", filters)
        return str(value[0] if isinstance(value, tuple) else value)

    def import_file(self):
        self.structural_guard()
        path = self.choose_path()
        if not path:
            return
        # Offer explicit master mapping when names do not match.
        raw = Path(path).read_text(encoding="utf-8")
        mapping = None
        if raw.lstrip().startswith("{"):
            data = self.session.upstream.config.parse_setup_text(raw)
            mapping = {}
            for m in data.get("masters", []):
                name = m["name"]
                if name in self.session.font.master_by_name:
                    mapping[name] = name
                    continue
                choices = ["Skip"] + list(self.session.font.master_by_name)
                result = QtGui.QInputDialog.getItem(
                    self.dialog,
                    "Map master",
                    "Import master " + name + " into:",
                    choices,
                    0,
                    False,
                )
                chosen = result[0] if isinstance(result, tuple) else result
                if str(chosen) in self.session.font.master_by_name:
                    mapping[name] = str(chosen)
        skipped = self.session.import_setup(path, mapping)
        self.load_all()
        self.schedule()
        self.status.setText(
            "Imported working setup. Save configuration to store it."
            + (" Unmapped masters: " + ", ".join(skipped) if skipped else "")
        )

    def export_file(self):
        path = self.choose_path(save=True)
        if path:
            self.session.export_setup(path)
            self.status.setText("Exported " + path)

    def export_legacy(self):
        path = self.choose_path(save=True, legacy=True)
        if path:
            Path(path).write_text(
                self.session.upstream.config.serialize_config_text(self.session.rules),
                encoding="utf-8",
            )
            self.status.setText(
                "Exported legacy rules (parameters, absolute values and master overrides are not represented)."
            )

    def closed(self):
        self.timer.stop()
        self.reporter.stop()
        self.overlay.setChecked(False)
        self.live.setChecked(False)

    def reload(self):
        self.reporter.stop()
        self.overlay.setChecked(False)
        self.live.setChecked(False)
        self.session = Session.current()
        self.loading = True
        for c in (
            self.master_box,
            self.copy_master,
            self.interpolate_a,
            self.interpolate_b,
        ):
            c.clear()
            c.addItems(list(self.session.font.master_by_name))
        select(self.master_box, self.session.raw.master)
        self.load_all()
        self.loading = False
        self.schedule()


def show():
    global _window
    if _window is not None:
        _window.dialog.show()
        _window.dialog.raise_()
        _window.dialog.activateWindow()
        return _window
    _window = Window()
    _window.dialog.show()
    _window.dialog.raise_()
    return _window
