# this_file: src_docs/build.py
"""Build a source-backed menu catalogue without importing FontLab scripts."""

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def catalogue(root: Path) -> None:
    """Replace only the generated catalogue; include every current menu source."""
    output = root / "src_docs/md/scripts"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    snapshots = root / ".build/menu-sources"
    if snapshots.exists():
        shutil.rmtree(snapshots)
    snapshots.mkdir(parents=True)
    index = [
        "# Script catalogue",
        "",
        "Choose a category, then a script. Each page includes its actual menu source.",
        "",
    ]
    for folder in sorted((root / "Scripts").iterdir()):
        if not folder.is_dir():
            continue
        sources = sorted(folder.glob("*.py"))
        if not sources:
            continue
        category = output / slug(folder.name)
        category.mkdir()
        lines = [f"# {folder.name}", ""]
        index.append(f"## {folder.name}")
        index.append("")
        for source in sources:
            target = category / (slug(source.stem) + ".md")
            if target.exists():
                raise ValueError(f"Duplicate documentation slug: {source.name}")
            data = source.read_bytes()
            snapshot = snapshots / (hashlib.sha256(data).hexdigest() + ".py")
            snapshot.write_bytes(data)
            description = (
                ast.get_docstring(ast.parse(data))
                or "Read the source before running this script."
            )
            header = (
                f"this_file: {target.relative_to(root).as_posix()}\n"
                f"tags: {json.dumps([folder.name])}\n"
                f"categories: {json.dumps([folder.name])}\n"
            )
            text = f"---\n{header}---\n\n# {source.stem}\n\n{description}\n\n"
            text += f"Run **{folder.name} > {source.stem}** from FontLab's Scripts menu.\n\n"
            text += "Read [installation](../../install.md) and [working with scripts](../../use.md) before use.\n\n"
            text += (
                "## Source\n\n<!--codeinclude-->\n[Python source]("
                + os.path.relpath(snapshot, target.parent)
                + ")\n<!--/codeinclude-->\n"
            )
            target.write_text(text)
            lines.append(f"- [{source.stem}]({target.name})")
            index.append(f"- [{source.stem}]({slug(folder.name)}/{target.name})")
        (category / "index.md").write_text("\n".join(lines) + "\n")
        index.append("")
    (output / "index.md").write_text("\n".join(index).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline", action="store_true", help="use cached build dependencies"
    )
    parser.add_argument(
        "--serve", action="store_true", help="preview locally with Markdown editing"
    )
    args = parser.parse_args()
    catalogue(ROOT)
    command = [
        "properdocs",
        "serve" if args.serve else "build",
        "--strict",
        "-f",
        "src_docs/mkdocs.yml",
    ]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
