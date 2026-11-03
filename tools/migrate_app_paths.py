#!/usr/bin/env python3
# this_file: tools/migrate_app_paths.py
"""Rewrite App dotted references from the sibling issue-205 alias oracle.

Run before updating script hash pins and exact menu-revision edits. --check
reports pending rewrites without writing. Canonical paths are left unchanged,
including children of the six packages that also have legacy module names.
"""

import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def load_aliases(source: Path) -> dict[str, str]:
    """Import only the host-free oracle; do not load native App helpers."""
    spec = importlib.util.spec_from_file_location("_scriptmix_legacy", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ALIASES


def rewrite(text: str, aliases: dict[str, str]) -> str:
    """Replace whole dotted module components, longest old prefix first."""
    names = {old.removeprefix("fontlabapp."): new.removeprefix("fontlabapp.")
             for old, new in aliases.items()}
    ordered = sorted(names, key=lambda name: (-len(name), name))
    canonical = set(names.values())
    canonical.update(name.rpartition(".")[0] for name in tuple(canonical))
    canonical.difference_update(names)
    # Short ap references occur in scripts that import Fly's App alias.
    roots = r"fly\.ap|fontlabapp"
    if re.search(r"from fly import .*\bap\b|import fly\.ap as ap", text):
        roots += "|ap"
    pattern = re.compile(r"(?<![\w.])(" + roots + r")\.([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)")

    def replace(match: re.Match) -> str:
        root, tail = match.groups()
        if any(tail == name or tail.startswith(name + ".") for name in canonical):
            return match.group()
        for old in ordered:
            if tail == old or tail.startswith(old + "."):
                return root + "." + names[old] + tail[len(old):]
        return match.group()

    return pattern.sub(replace, text)


def sources(root: Path) -> list[Path]:
    """Limit writes to requested sources, never historical manifest fields."""
    paths = [root / name for name in ("AGENTS.md", "README.md", "menu_layout.py")]
    for folder in ("Scripts", "tests", "src_docs", "tests_docs", "docs"):
        paths.extend(path for path in (root / folder).rglob("*")
                     if path.suffix in {".py", ".md", ".yml", ".yaml", ".rst", ".txt"})
    return sorted(path for path in paths if path.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--app-source", type=Path,
                        default=ROOT.parent / "fontlab-fontlabapp/src/fontlabapp/_legacy.py")
    args = parser.parse_args()
    aliases = load_aliases(args.app_source)
    changed = []
    for path in sources(ROOT):
        before = path.read_text()
        after = rewrite(before, aliases)
        if before != after:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(after)
    print("\n".join(changed))
    print(f"{len(changed)} files {'need migration' if args.check else 'rewritten'}")
    raise SystemExit(bool(changed) if args.check else 0)


if __name__ == "__main__":
    main()
