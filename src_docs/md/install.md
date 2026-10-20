---
this_file: src_docs/md/install.md
tags:
- Python
categories:
- Guides
---

# Install the scripts

These scripts use FontLab 9's Python 3.11 and its PythonQt binding. Install
`fontlab-fly` and `fontlab-fontlabapp` 0.2.23 or later in FontLab's Python
environment. Feature editors also need App's `fontedit` extra and native `fontpr`.
The documentation build uses a separate Python environment.

1. Open FontLab's Scripts folder.
2. Copy the contents of this repository's `Scripts` folder into that folder.
3. Keep the category folders. FontLab supports one folder level in the Scripts menu.
4. Open a font. Choose a script from the corresponding category in the Scripts menu.

Start with **Reports > Font Overview** to inspect the font. Read the script's
description before you run an editor. Test edits on a copy of the font.

Close a script's panel with its **Close** control. The shared lifecycle code
disconnects the script's signals and destroys its owned window.
