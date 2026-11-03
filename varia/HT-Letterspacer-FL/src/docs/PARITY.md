# Native Glyphs / FontLab spacing comparison

29 October 2026. Acceptance: the user considers one font unit insignificant.

## Result

After correcting two adapter issues, all **9,996 measurable layer/scenario comparisons** agree with the current upstream Glyphs engine to within one unit when expressed at integer precision. Full-precision differences are below one unit except 11 synthetic-italic fixed-width cases, whose largest difference is **1.3703 units**. These are left-over host metric rounding differences, not differences in the area calculation.

An additional **504 actual FontLab Apply/readback checks** passed the same integer-precision tolerance. Their largest full-precision difference was 1.3246 units, again in italic fixed-width placement. No tolerance was silently widened: the fractional outliers are stated explicitly.

This does **not** establish equivalence to the historical standalone v1 script. That version differs even when both versions run inside Glyphs. For example, Light `colon`, Area 425 / Depth 25 / Overshoot 5, measures **22/22** in the current engine and **44/44** in the historical script. Its advance-width difference is 44 units. The upstream change in handling empty scanlines accounts for this class of differences. The adapter continues to use the pinned current upstream engine; it has not been switched to the older algorithm.

## Hosts and sources

- Native Glyphs **3.5, build 3528**, using the Glyphs CLI and the installed Glyphs Python 3.11 framework. Actual `GSLayer` intersections and metric setters were used; Glyphs was not emulated.
- Native FontLab **9.0.9797, build 9797**, embedded Python 3.11.6.
- Current engine: upstream commit `b4ad60bd36284f87edf9f2145d38bbf87b2e9909`, loaded unchanged.
- Historical standalone `HT_LetterSpacer_script.py`: commit `737964043b9890bd77a3552cab34fbe4c52a4402`, loaded unchanged. The harness calls its spacing class directly, avoiding only the UI startup.
- Font: upstream `Examples/ExampleFont-Glyphs3.glyphs`, SHA-256 `aa27bf242fa9978ac3b4369c931cb590ec1697ea6cbbce61b8d9af0f1fb32cb8`.
- 239 glyphs, Light / Regular / Bold. A second, shared source was generated in Glyphs with a 12-degree slant and opened unchanged in FontLab. This is a synthetic italic stress test, not a separately designed italic font.
- Step 5 in both hosts. Source outlines' bounding boxes agree to floating-point precision. The italic master names are mapped explicitly because FontLab imports them as LightItalic / Italic / BoldItalic.

## Test matrix

Every scenario runs over all 239 glyphs and all three masters in both source variants. The empty space layers are skipped in both implementations: 42 expected skipped cases out of 10,038 total cases.

| Scenario | Parameters / behavior | Largest final metric delta, upright | Largest final metric delta, italic |
| --- | --- | ---: | ---: |
| Manual defaults | Area 400, Depth 15, Overshoot 0 | 0.6875 | 0.9585 |
| Screenshot values | Area 425, Depth 25, Overshoot 5 | 0.6875 | 0.9585 |
| Left only | 425 / 25 / 5; RSB protected | 0.5000 | 0.4991 |
| Right only | 425 / 25 / 5; LSB protected | 0.5000 | 0.4991 |
| Tabular | 425 / 25 / 5; advance 595 | 0.9114 | 1.3703 |
| Supplied v2 setup | 21 rules, master parameters and overrides | 0.6875 | 0.9585 |
| Legacy default rules | Same parsed rules and 400 / 15 / 0 in current engine | 0.6875 | 0.9585 |

Deltas are the maximum absolute difference across LSB, RSB and advance width, not an average. For the default and screenshot manual cases, the computed bearing values themselves agree exactly; the small final metric differences come from host setters and fractional bounds. On fixed-width glyphs, final RSB is measured after setting the advance width, not assumed equal to the engine's preliminary RSB.

## Issues found and fixed

1. **Scanline endpoint handling.** The initial adapter included both endpoints and horizontal segments. Glyphs uses directed segments with a `(start, end]` convention and ignores coincident horizontal edges. HTLS samples exactly at extrema, so this changed some results by several units. The adapter now uses the measured Glyphs convention and keeps full numeric precision before the engine's `ceil` operations. The upstream math remains unchanged.
2. **Legacy names and classifications.** Encoded `Omega` (U+2126) and `mu` (U+00B5) were incorrectly treated as Greek letters rather than mathematical symbols. `florin` was treated as the modern `fhook` letter rather than Glyphs 3's currency symbol. This selected different rules; the Light florin LSB differed by 143 units. Encoding disambiguation and the Glyphs 3 florin classification fix these mismatches. Modern Greek Omega/mu and the explicit fhook name retain their letter classifications.
3. **Fixed-width reporting.** Preview/result reporting now calculates the final RSB after the fixed advance is imposed. This corrects the displayed result; placement already used the fixed advance.

## Method and evidence

The complete native Glyphs run uses detached copies of the source layers. It records input bounds, classifications, resolved parameters, computed bearings, and native readback after assigning bearings and width.

FontLab captures its actual rendered paths on fresh, disposable copies of the identical sources. The adapter's unchanged upstream engine is replayed over those captured inputs for all 10,038 cases. This replay is a numerical comparison, not 10,038 live UI edits. Actual native writes and readback were independently checked for 504 cases: A, H, i, o, colon, florin, Omega, mu, parenleft, T, pi and n across every scenario, master and source variant.

One early bulk live-write run was interrupted by the FontLab process exiting and produced incomplete results. It is excluded from the acceptance counts. The final bounded capture and 504-case live verification completed. This report does not certify unattended bulk-edit host stability.

Reproducible scripts: `tests/parity/`. Local raw measurements, outline snapshots, generated italic source, summaries and a SHA-256 manifest: `.test-output/parity/` (intentionally gitignored). The upstream repository is still clean. The updated 21 unit tests and disposable FontLab smoke suite pass.

## Boundaries

This validates the stated corpus and parameters against Glyphs 3.5. It does not prove every font, Glyphs 4, custom glyph database, alternate layer, complex brush, or third-party prepare-layer callback equivalent. The example font contains normal outlines; live-component preservation is covered by the separate FontLab smoke suite rather than this cross-host corpus. Historical v1 behavior remains a distinct algorithm choice.
