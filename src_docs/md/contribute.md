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

The first build needs network access to install the packages pinned in `uv.lock`.
Use `--offline` after those packages are cached. The build needs Python 3.12 or
later and `uv`. It does not start FontLab or execute the scripts shown on a page.

**Serve** starts a local preview. Live Edit is available only in that preview;
it saves changes to the authored Markdown. The static site has no editing server.
Edit generated catalogue pages through their source generator, because the next
build replaces them.

## Include source and shared text

Use `codeinclude` for an executable script. The plugin reads the actual source
file, so the displayed code follows changes to that file. Do not paste a second
copy of the script into Markdown. Use `include-markdown` for shared prose.
Use mkdocstrings with Python inspection disabled when documenting an importable
module. Menu scripts and archived host scripts are displayed as source instead.

{% include-markdown "includes/writing.md" start="## Writing rules" %}

Use page tags and categories to connect related tasks. The navigation follows
`.nav.yml`. Use the print page for a combined printable copy.

## Build function reference

This section documents the source-only build helper for contributors.

::: build.catalogue
