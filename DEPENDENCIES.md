---
this_file: DEPENDENCIES.md
---

# Dependencies

Runtime: FontLab 9 Python 3.11 native APIs and PythonQt, fontlab-fly aliases,
fontlab-fontlabapp scripting helpers. No new third-party runtime dependencies.
Tests: pytest, supplied temporarily by uv. Ruff is a development check only.

Build Suffix Substitution and Feature Code Viewer use App's existing optional
`fontedit` dependency
(fontlab-fontport >=1.0.2) for exact feature source, safe ordered writes and
history preflight. Native fontpr availability is required. The other four Features tools
remain native FontLab/PythonQt only; no new Qt bindings are installed.
