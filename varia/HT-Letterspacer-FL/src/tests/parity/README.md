# Reproduce the native parity comparison

These verification tools are separate from the installed FontLab scripts. They use the installed Glyphs runtime through the official [Glyphs CLI](https://pypi.org/project/glyphs-cli/) and FontLab's local MCP bridge. FontLab must have external MCP clients enabled. Run from the adapter project directory.

The tools use the sibling HTLetterspacer checkout by default. `HTLS_UPSTREAM` overrides it; `HTLS_PARITY_DIR` overrides the default `.test-output/parity` output directory. Glyphs needs its normal PyObjC/Vanilla dependencies. `HTLS_VANILLA` can point to a directory containing the `vanilla` package.

Prepare the exact historical script without changing the original checkout:

```sh
mkdir -p .test-output/parity
git -C ../HTLetterspacer show 737964043b9890bd77a3552cab34fbe4c52a4402:HT_LetterSpacer_script.py > .test-output/parity/legacy_script.py
```

Run the Glyphs reference. On this machine, use the explicitly installed Python 3.11 framework because Glyphs' saved Python 3.9 preference points to a missing runtime:

```sh
glyphs run --app '/Applications/Glyphs/Glyphs 3.app' \
  --python "$HOME/Library/Application Support/Glyphs 3/Repositories/GlyphsPythonPlugin/Python.framework/Versions/3.11/Python" \
  --plugins '' tests/parity/glyphs_reference.py \
  -i ../HTLetterspacer/Examples/ExampleFont-Glyphs3.glyphs
```

Repeat with `-- --italic` at the end to generate the shared italic source and reference results. Source fonts are not overwritten; calculations and writes use detached layers in the CLI process. Plugins are disabled deliberately because the supplied test font has no plugin-specific strokes or effects.

The native FontLab tools use the stdlib MCP client from the sibling Proteus project's `docs/mcp` folder. Set `FONTLAB_MCP_CLIENT_DIR` if that client lives elsewhere. They open disposable source copies, close only their own fonts and restore the previously active font when one existed.

```sh
python3 tests/parity/fontlab_capture.py upright
python3 tests/parity/fontlab_capture.py italic
python3 tests/parity/replay.py upright
python3 tests/parity/replay.py italic
python3 tests/parity/fontlab_verify.py upright
python3 tests/parity/fontlab_verify.py italic
python3 tests/parity/summarize.py
```

`replay.py` covers every captured layer; `fontlab_verify.py` checks actual writes and readback on the representative 12-glyph set. `summarize.py` reports full-precision deltas, including every case above one unit; it does not hide fractional outliers.

For fast regression checks without either application's runtime:

```sh
python3 -m unittest discover -s tests -v
```
