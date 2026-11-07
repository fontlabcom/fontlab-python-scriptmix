---
this_file: src_docs/md/contribute.md
tags:
- Python
categories:
- Guides
---

# Build and edit the documentation

The source configuration is `src_docs/mkdocs.yml`. Authored pages are in
`src_docs/md`. The build writes the static site to `docs`.

```sh
./build.sh
./build.sh --offline
./build.sh --serve
```

The first build needs network access to install the packages pinned in `src_docs/requirements.txt`.
Use `--offline` after those packages are cached. The build needs Python 3.12 or
later and `uv`. It does not start FontLab or execute the scripts shown on a page.

**Serve** starts a local preview. Live Edit is available only in that preview;
it saves changes to the authored Markdown. The static site has no editing server.
Edit generated catalogue pages through their source generator, because the next
build replaces them.

## Include source and shared text

Keep usage and setup in the script docstring. The generator publishes descriptions, exact hashes and immutable source links; it keeps implementation snapshots outside the public site.
Use mkdocstrings with Python inspection disabled when documenting an importable
module. Menu scripts and archived host scripts are displayed as source instead.

## Writing rules

Name the action and its scope. Give one instruction per step where possible.
Put prerequisites before the action. Keep exact API identifiers and interface
labels. State a host limitation beside the operation that it affects. This is
ASD-STE100-inspired writing; it is not a claim of controlled-language certification.


Use page tags and categories to connect related tasks. The navigation follows
`.nav.yml`. Use the print page for a combined printable copy.

## Build function reference

This section documents the source-only build helper for contributors.

The generator reads source files and recorded hashes without importing menu scripts.
