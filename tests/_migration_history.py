# this_file: tests/_migration_history.py
"""Keep frozen release checks exact across the owner-requested category rename."""

import hashlib
import json
import os
from pathlib import Path

from menu_layout import _menu_bytes

ROOT = Path(__file__).parents[1]


def preserved_source(original_root, source):
    """Resolve exact historical input bytes after the owner-authorized relocation."""
    original = original_root / source
    row = json.loads((ROOT / "rescue-index.json").read_text())["preserved_sources"][source]
    archive = os.environ.get("FONTLAB_PRESERVED_ROOT")
    if archive:
        target = Path(archive) / row["path"]
    else:
        target = original if original.is_file() else ROOT / row["path"]
    assert hashlib.sha256(target.read_bytes()).hexdigest() == row["sha256"], source
    return target


def previous_payload(destination, root=ROOT):
    """Read a historical menu while reversing only its recorded path header."""
    current = destination.replace("Scripts/Outlines/", "Scripts/Contours/")
    payload = _menu_bytes(root, current)
    if current != destination:
        old = f"# this_file: {destination}\n".encode()
        new = f"# this_file: {current}\n".encode()
        assert payload.startswith(new), f"Missing current path header: {current}"
        payload = old + payload[len(new):]
    return payload.replace(b"# FLM: Contours ", b"# FLM: Outlines ")


def before_contours_rename(rows, root=ROOT):
    """Reverse just the three destination/header changes, preserving all other data."""
    previous = []
    for row in rows:
        item = dict(row)
        if item["destination"].startswith("Scripts/Contours/"):
            assert hashlib.sha256(_menu_bytes(root, item["destination"])).hexdigest() == item["destination_sha256"], "Released manifest changed"
            item["destination"] = item["destination"].replace(
                "Scripts/Contours/", "Scripts/Outlines/", 1
            )
            item["destination_sha256"] = hashlib.sha256(
                previous_payload(item["destination"], root)
            ).hexdigest()
        previous.append(item)
    return previous
