# this_file: Scripts/Font Info/Trial Font Maker.py
# SPDX-License-Identifier: Apache-2.0
"""Make prefixed trial copies of static fonts exported from the current font.

What: Keep selected FontLab glyphs in each matching exported OTF or TTF. Keep
.notdef and component dependencies. Ligature expansion is off by default;
tick Also keep ligatures to include the extra glyphs listed in the preview.
Keep kerning and positioning unless Remove kerning and positioning is ticked.
Keep the existing liga substitutions that survive this keep set. Prefix family,
full, unique and PostScript names, including CFF names. Preserve copyright and
licence records.
How: Read exported binaries with fontTools, subset detached copies and save new
files. Inspect the saved copies by reopening them in FontLab. No source font or
source binary is edited. There is no font edit and no Undo step.
Why: File > Export Font As produces the source binaries. This panel adds a selected
glyph keep set and consistent trial names across those static exports. It avoids
changing a live font or relying on Glyphs export-only custom parameters.
Usage: Export static OTF/TTF instances to a folder first. Select the trial glyphs
in FontLab. Open this panel, enter that folder, a different output folder and a
prefix. Inspect the per-file preview, then press Make Trial Copies. Use selection
reads the glyph selection again. Family name and UPM must match the current font;
other files get named kept rows. Existing destinations are kept. Variable fonts
are kept: export static instances before using this tool.
Benefit: Repeatable trial binaries without deleting work from the design source.
The keep set uses exported glyph names. Preserve glyph names in the export
profile; renamed or absent glyphs are reported instead of silently dropped.
Substitution features are limited to liga and the retained positioning feature
tags; ligatures are not invented.
Requires user-installed fontTools in FontLab's Python site-packages, such as
the dependency installed with fontlab-fontport. FontLab's private copy is not
used. Install it through Settings > Python if it is missing.
Source inspection is cached until the folder or selection changes, or Refresh
Exports is pressed. Prefix edits update destination names without opening fonts.

Independent behaviour rewrite of Fernando Díaz / Reset Type Studio,
Glyphs-Scripts/Exports/Trial Font Maker.py.
https://github.com/Reset-Type-Studio/Glyphs-Scripts
Apache-2.0, declared in the repository README; no separate LICENSE file.
No source code was copied.
"""

import io
import re
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any

TITLE = "Trial Font Maker"
KEY = "fontinfo_trial_font_maker"
NAME_IDS = frozenset({1, 3, 4, 6, 16, 18, 21, 25})


INSTALL_HINT = "Install fontTools into FontLab's Python environment (Settings > Python) to use this tool."


def fonttools_api() -> tuple[Any, Any, Any]:
    """Load the public user-installed package, with a useful refusal if absent."""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont, TTLibError
    except ImportError as error:
        raise ValueError(INSTALL_HINT) from error
    return subset, TTFont, TTLibError


def name_encoding(record: Any) -> str:
    """Refuse unknown name-table encodings before decoding or encoding text."""
    encoding = record.getEncoding(default=None)
    if encoding is None:
        raise ValueError(
            f"Unknown name encoding: platform {record.platformID}, encoding {record.platEncID}."
        )
    return str(encoding)


def prefix_text(text: str) -> str:
    """Require an explicit ASCII prefix usable in both file and PostScript names."""
    if any(c in text for c in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Prefix contains text that PythonQt cannot preserve.")
    value = text.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,29}", value):
        raise ValueError(
            "Use a prefix of 1–30 ASCII letters, digits, spaces, underscores or hyphens."
        )
    return value


def rename_binary(font: Any, prefix: str) -> None:
    """Prefix every localized identity record and the CFF identity, once."""
    ps_prefix = prefix.replace(" ", "-")
    for record in font["name"].names:
        if record.nameID not in NAME_IDS:
            continue
        encoding = name_encoding(record)
        old = record.toUnicode()
        head = ps_prefix + "-" if record.nameID in {6, 25} else prefix + " "
        value = old if old.startswith(head) else head + old
        if record.nameID == 6 and len(value) > 63:
            raise ValueError("Prefixed PostScript name exceeds 63 characters.")
        record.string = value.encode(encoding, errors="strict")
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [
            name if name.startswith(ps_prefix + "-") else ps_prefix + "-" + name
            for name in cff.fontNames
        ]
        for top in cff.topDictIndex:
            for field in ("FamilyName", "FullName"):
                old = str(getattr(top, field, ""))
                if old and not old.startswith(prefix + " "):
                    setattr(top, field, prefix + " " + old)


def inspect_binary(font: Any, names: list[str]) -> None:
    """Refuse variable fonts and missing names before creating an output file."""
    if "fvar" in font or "CFF2" in font:
        raise ValueError("Use static OTF/TTF exports; variable fonts are kept.")
    if not names:
        raise ValueError("Select glyphs in FontLab first.")
    missing = sorted(set(names) - set(font.getGlyphOrder()))
    if missing:
        raise ValueError("Export is missing selected glyphs: " + ", ".join(missing))


def subset_binary(
    font: Any,
    names: list[str],
    *,
    keep_ligatures: bool = False,
    remove_positioning: bool = False,
) -> None:
    """Subset a detached font; expand GSUB only with explicit consent."""
    subset, _, _ = fonttools_api()
    options = subset.Options()
    tags = []
    if not remove_positioning and "GPOS" in font:
        features = font["GPOS"].table.FeatureList
        tags = (
            [record.FeatureTag for record in features.FeatureRecord] if features else []
        )
    options.layout_features = list(dict.fromkeys(["liga", *tags]))
    options.layout_closure = keep_ligatures
    options.legacy_kern = not remove_positioning
    options.name_IDs, options.name_languages = ["*"], ["*"]
    options.name_legacy, options.glyph_names, options.notdef_outline = True, True, True
    if remove_positioning:
        options.drop_tables += ["GPOS", "kern"]
    cutter = subset.Subsetter(options=options)
    cutter.populate(glyphs=list(dict.fromkeys(names)))
    cutter.subset(font)


def scan_exports(folder: Path, names: list[str], family: str, upm: int) -> list[Any]:
    """Read sources once; cache exact baseline and optional ligature glyph sets."""
    _, font_type, font_error = fonttools_api()
    records = []
    for source in sorted(folder.iterdir()):
        if not source.is_file() or source.suffix.lower() not in {".otf", ".ttf"}:
            continue
        note, digest, extra = "", "", ()
        try:
            data = source.read_bytes()
            digest = sha256(data).hexdigest()
            with font_type(io.BytesIO(data), recalcTimestamp=False) as font:
                if (
                    font["name"].getDebugName(16) or font["name"].getDebugName(1)
                ) != family or font["head"].unitsPerEm != upm:
                    raise ValueError("family name or UPM differs from the current font")
                inspect_binary(font, names)
                for record in font["name"].names:
                    if record.nameID in NAME_IDS:
                        name_encoding(record)
                subset_binary(font, names)
                baseline = set(font.getGlyphOrder())
            with font_type(io.BytesIO(data), recalcTimestamp=False) as font:
                subset_binary(font, names, keep_ligatures=True)
                extra = tuple(sorted(set(font.getGlyphOrder()) - baseline))
        except (OSError, ValueError, KeyError, LookupError, font_error) as error:
            note = f"kept: {error}"
        records.append(
            SimpleNamespace(source=source, note=note, digest=digest, extra=extra)
        )
    return records


def make_trial(
    source: Path,
    destination: Path,
    names: list[str],
    prefix: str,
    *,
    keep_ligatures: bool = False,
    remove_positioning: bool = False,
    expected_digest: str | None = None,
) -> dict[str, Any]:
    """Serialize a detached subset before an exclusive write; reject changed sources."""
    _, font_type, _ = fonttools_api()
    prefix = prefix_text(prefix)
    source, destination = (
        source.expanduser().resolve(),
        destination.expanduser().resolve(),
    )
    if destination.exists():
        raise FileExistsError(destination)
    if (
        source.suffix.lower() not in {".otf", ".ttf"}
        or destination.suffix.lower() != source.suffix.lower()
    ):
        raise ValueError("Keep the source .otf or .ttf extension.")
    original = source.read_bytes()
    if expected_digest is not None and sha256(original).hexdigest() != expected_digest:
        raise ValueError(
            "Source export changed; press Refresh Exports and review again."
        )
    with font_type(io.BytesIO(original), recalcTimestamp=False) as font:
        inspect_binary(font, names)
        subset_binary(
            font,
            names,
            keep_ligatures=keep_ligatures,
            remove_positioning=remove_positioning,
        )
        rename_binary(font, prefix)
        data = io.BytesIO()
        font.save(data)
    with font_type(io.BytesIO(data.getvalue())) as check:
        glyphs = set(check.getGlyphOrder())
        if not (check["name"].getDebugName(1) or "").startswith(prefix + " "):
            raise ValueError("Trial family name did not survive binary serialization.")
    extra = []
    if keep_ligatures:
        with font_type(io.BytesIO(original), recalcTimestamp=False) as baseline:
            subset_binary(baseline, names, remove_positioning=remove_positioning)
            extra = sorted(glyphs - set(baseline.getGlyphOrder()))
    with destination.open("xb") as output:
        output.write(data.getvalue())
    return {"path": str(destination), "glyphs": len(glyphs), "extra": extra}


def preview(
    folder: Path,
    destination: Path,
    names: list[str],
    prefix: str,
    family: str,
    upm: int,
    *,
    keep_ligatures: bool = False,
    sources: list[Any] | None = None,
) -> list[Any]:
    """Build file targets from source summaries; prefix changes need no font reads."""
    fonttools_api()
    prefix = prefix_text(prefix)
    if (
        not folder.is_absolute()
        or not folder.is_dir()
        or not destination.is_absolute()
        or not destination.is_dir()
    ):
        raise ValueError("Enter existing absolute input and output folder paths.")
    if folder.resolve() == destination.resolve():
        raise ValueError("Choose different input and output folders.")
    records = scan_exports(folder, names, family, upm) if sources is None else sources
    result = []
    for record in records:
        target = destination / (prefix.replace(" ", "-") + "-" + record.source.name)
        note = record.note or ("kept: destination exists" if target.exists() else "")
        result.append(
            SimpleNamespace(
                source=record.source,
                target=target,
                note=note,
                digest=record.digest,
                extra=record.extra if keep_ligatures else (),
            )
        )
    return result


def read_field(widget: Any) -> str:
    """Read literal Qt text and refuse characters that cannot round-trip safely."""
    import fly.ap.qt_literal_text as literal_text
    from fly import qt

    text = literal_text.read_text(qt, widget.text)
    if any(c in text for c in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Field contains text that PythonQt cannot preserve.")
    return text


def panel_type() -> type:
    """Return a non-modal, font-bound export panel with explicit file previews."""
    import fly.ap.selection_panel as selection_panel  # noqa: PLR0402
    from fly import qt

    base, gui = selection_panel.panel_type(), qt.QtGui

    class TrialPanel(base):
        TITLE, KEY = TITLE, KEY
        ACTION = "Make Trial Copies"
        HEADERS = ("Source export", "Trial copy", "Extra ligature glyphs", "Action")
        SCOPE, CONSENT, ALIGN = False, "", False

        def build_controls(self) -> None:
            """Keep the repeated workflow in three compact editable fields."""
            self._source_cache_key: Any = None
            self._source_cache: list[Any] = []
            self.input_edit = gui.QLineEdit("")
            self.target_edit = gui.QLineEdit("")
            self.prefix_edit = gui.QLineEdit("TRIAL")
            for label, edit in (
                ("Source export folder", self.input_edit),
                ("Output folder", self.target_edit),
                ("Trial prefix", self.prefix_edit),
            ):
                self.add_row(label, edit)
                self.watch(edit.textChanged)
            self.ligature_box = gui.QCheckBox(
                "Also keep ligatures formed by the selection"
            )
            self.position_box = gui.QCheckBox("Remove kerning and positioning")
            for box in (self.ligature_box, self.position_box):
                box.setChecked(False)
                self.add_row("", box)
                self.watch(box.toggled)
            self.rescan_button = gui.QPushButton("Refresh Exports")
            self.add_row("", self.rescan_button)
            self.watch(self.rescan_button.clicked, self.refresh_exports)

        def refresh_exports(self) -> None:
            """Invalidate source summaries only on an explicit refresh."""
            self._source_cache_key = None
            self.refresh()

        def on_reselect(self) -> None:
            """A new selection requires a fresh source and glyph-set scan."""
            self._source_cache_key = None

        def plan_rows(self, package: Any, masters: list[str]) -> list[Any]:
            """Preview the current font's exports against the captured selected names."""
            folder = Path(read_field(self.input_edit)).expanduser()
            destination = Path(read_field(self.target_edit)).expanduser()
            family, upm = str(package.info.familyName), int(package.info.unitsPerEm)
            # Validate paths before starting a costly scan. An empty summary reads no font.
            preview(
                folder,
                destination,
                self.names,
                read_field(self.prefix_edit),
                family,
                upm,
                sources=[],
            )
            cache_key = (folder.resolve(), tuple(self.names), family, upm)
            if self._source_cache_key != cache_key:
                self._source_cache = scan_exports(folder, self.names, family, upm)
                self._source_cache_key = cache_key
            return preview(
                folder,
                destination,
                self.names,
                read_field(self.prefix_edit),
                family,
                upm,
                keep_ligatures=bool(self.ligature_box.isChecked()),
                sources=self._source_cache,
            )

        def cells(self, row: Any) -> list[str]:
            """Show one explicit output path or kept reason for every source file."""
            return [
                row.source.name,
                str(row.target),
                ", ".join(row.extra) or "—",
                row.note or "create trial copy",
            ]

        def write(self, package: Any, rows: list[Any]) -> dict[str, Any]:
            """Create each ready file; retain all other files as named kept rows."""
            _, _, font_error = fonttools_api()

            made, kept = [], [f"{r.source.name}: {r.note}" for r in rows if r.note]
            for row in rows:
                if row.note:
                    continue
                try:
                    made.append(
                        make_trial(
                            row.source,
                            row.target,
                            self.names,
                            read_field(self.prefix_edit),
                            keep_ligatures=bool(self.ligature_box.isChecked()),
                            remove_positioning=bool(self.position_box.isChecked()),
                            expected_digest=row.digest,
                        )
                    )
                except (
                    OSError,
                    ValueError,
                    RuntimeError,
                    TimeoutError,
                    LookupError,
                    font_error,
                ) as error:
                    kept.append(f"{row.source.name}: kept: {error}")
            return {"files": made, "kept": kept}

        def result_text(self, result: dict[str, Any]) -> str:
            """Report every kept file instead of hiding a partial batch."""
            detail = "; ".join(result["kept"])
            return f"Created {len(result['files'])} trial copies." + (
                " " + detail if detail else ""
            )

    return TrialPanel


def main() -> Any:
    """Open or replace only this tool's font-bound panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
