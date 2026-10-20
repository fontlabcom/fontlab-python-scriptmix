---
this_file: src_docs/md/plugins.md
tags:
- Python
categories:
- Guides
---

# Documentation plugins

The build uses ProperDocs 1.6.7 and MaterialX 10.1.5. `uv.lock` pins the full
environment. fltheme26 supplies the shared CSS and browser behavior.

| Plugin | Use |
| --- | --- |
| mkdocstrings and the Python handler | Source-derived API sections with runtime inspection disabled |
| autorefs | References between headings and API objects |
| PyMdown Extensions | Highlighted code, tabs, details and task lists |
| awesome-nav | Ordered navigation from `.nav.yml` |
| MaterialX meta | Directory metadata from `.meta.yml` |
| MaterialX tags | Page tags and a tag index |
| MaterialX search | Search over the built pages |
| categories | Topic pages under `topics/`, separate from the script catalogue |
| codeinclude | Complete source read from a script file |
| include-markdown | Shared authored Markdown |
| live-edit | Markdown editing during local `serve` only |
| print-site | A combined print page; this plugin runs last |

## Compatibility decisions

`mkdocs-toc-sidebar-plugin` 0.1.0 fails to load because it refers to the removed
`mkdocs.utils.string_types` attribute. The site uses MaterialX's native ToC.
The old breadcrumbs plugin generates index files in the source tree and brings
in the original Material package. MaterialX's `navigation.path` supplies breadcrumbs
without a second theme or source writes. Neither old plugin is installed.

The large API reference keeps its complete sharded search and verified archive.
It does not concatenate its thousands of API pages into a single print page.
