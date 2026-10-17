---
this_file: DEPENDENCIES.md
---

# Dependencies

Runtime: FontLab 9 Python 3.11 native APIs and PythonQt, fontlab-fly aliases,
fontlab-fontlabapp scripting helpers. No new third-party runtime dependencies.
Tests: pytest and an explicit current fontlab-fontlabapp requirement, supplied
temporarily by uv via test.sh. A current wheel can be supplied before App 0.2.5
is published; see README. Ruff is a development check only.

Build Suffix Substitution and Feature Code Viewer use App's existing optional
`fontedit` dependency
(fontlab-fontport >=1.0.2) for exact feature source, safe ordered writes and
history preflight. Native fontpr availability is required. The other four Features tools
remain native FontLab/PythonQt only; no new Qt bindings are installed.

Names inspection tools use existing FontLab/PythonQt, fly and standard-library
Unicode/glob/regex modules; no new third-party dependencies. The new shared Names
panel requires the updated App sources/build beyond the v0.2.5 baseline.
