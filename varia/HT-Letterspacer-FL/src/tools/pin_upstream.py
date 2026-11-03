#!/usr/bin/env python3
"""Explicitly pin a reviewed upstream checkout and its verified GitHub archive."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import ssl
import subprocess
import urllib.request
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("checkout", type=Path)
parser.add_argument(
    "--archive",
    type=Path,
    help="Use a previously downloaded archive instead of downloading it",
)
args = parser.parse_args()
root = args.checkout.expanduser().resolve()
project = Path(__file__).resolve().parents[1]
commit = subprocess.check_output(
    ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
).strip()
resource = Path("HTLetterspacer.glyphsPlugin/Contents/Resources/htls")
hashes = {
    name
    + ".py": hashlib.sha256((root / resource / (name + ".py")).read_bytes()).hexdigest()
    for name in ("config", "rules", "engine")
}
url = "https://codeload.github.com/huertatipografica/HTLetterspacer/zip/" + commit
if args.archive:
    data = args.archive.read_bytes()
else:
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=str(project / "installer/ca.pem"))
    with urllib.request.urlopen(url, timeout=45, context=context) as response:
        data = response.read(32 * 1024 * 1024 + 1)
if len(data) > 32 * 1024 * 1024:
    raise ValueError("Archive exceeds size limit.")
with zipfile.ZipFile(io.BytesIO(data)) as z:
    prefix = "HTLetterspacer-" + commit + "/"
    for name, expected in hashes.items():
        if (
            hashlib.sha256(
                z.read(prefix + resource.as_posix() + "/" + name)
            ).hexdigest()
            != expected
        ):
            raise ValueError("Archive and checkout differ: " + name)
lock = {
    "url": "https://github.com/huertatipografica/HTLetterspacer",
    "commit": commit,
    "sha256": hashes,
    "archive": {
        "url": url,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    },
}
(project / "upstream.lock.json").write_text(
    json.dumps(lock, indent=2) + "\n", encoding="utf-8"
)
print("Pinned", commit, "— run the unit, in-app and parity tests before release.")
