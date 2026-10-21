# Complete cross-font reports

Open at least two fonts and make the intended reference current. **Report Composite Differences** compares only the first other open font, with each font's selected named master. Component base names stay in their stored order, including repetitions. Different common glyphs use `name;source bases;target bases;` rows. Missing glyphs stay in reference order; only case-sensitive `.sc` and `.pcap` endings are excluded.

**Report Glyph Set Differences** compares every other open font in open-font order. Each raw filepath heading is followed by target-order Extra rows, then reference-order Missing rows. An unsaved empty native filepath maps to the original `None` heading. No chooser changes the reference or target policy.

Both reports are nonmodal, read-only and selectable. Refresh repeats the complete original scan and diagnoses changed sources. No font, selection, history, preferences or user Output is changed. Report text can contain source filepaths because that is an explicit original result, but packages/docs contain no local source paths. Literal copying is preserved by the shared editor; actual PythonQt literal-NUL and complete-font getter preservation remain native gates. Unknown selected-master mappings are diagnosed without activation or fallback; full original master domains remain required for native acceptance.

Originals by Jens Kutilek, MIT; full notice is in NOTICE. Source bodies/resources remain untouched and unexecuted. These are new workflows, not entries counted as completed in the historical130sample ledger.
