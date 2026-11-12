#!/usr/bin/env python3
"""Build the standalone .vfpy installer, customer ZIP and corresponding source ZIP."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def zip_files(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    return buffer.getvalue()


def source_archive(root):
    root = Path(root)
    version = json.loads((root / "release.json").read_text())["version"]
    stem = "HT-Letterspacer-FontLab-" + version
    source = {}
    roots = ["htls_fontlab", "installer", "tools", "scripts", "tests", "docs"]
    for folder in roots:
        for path in (root / folder).rglob("*"):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ):
                source[stem + "-source/" + path.relative_to(root).as_posix()] = (
                    path.read_bytes()
                )
    for name in [
        "install.py",
        "README.md",
        "LICENSE",
        "NOTICES.txt",
        "release.json",
        "upstream.lock.json",
    ]:
        source[stem + "-source/" + name] = (root / name).read_bytes()
    return zip_files(source)


def make_payload(destination, root=ROOT):
    root = Path(root)
    destination = Path(destination)
    release = json.loads((root / "release.json").read_text())
    lock = json.loads((root / "upstream.lock.json").read_text())
    if "archive" not in lock:
        raise ValueError(
            "Pin the GitHub archive URL and SHA-256 in upstream.lock.json before building a release."
        )
    files = {}
    for p in (root / "htls_fontlab").rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            files[p.relative_to(root).as_posix()] = p.read_bytes()
    for name in ("release.json", "upstream.lock.json", "LICENSE", "NOTICES.txt"):
        files[name] = (root / name).read_bytes()
    for source, name in [
        ("installer/core.py", "htls_installer.py"),
        ("installer/ui.py", "htls_install_ui.py"),
        ("installer/ca.pem", "ca.pem"),
        ("installer/CERTIFI-LICENSE", "CERTIFI-LICENSE"),
        ("docs/USER-GUIDE.md", "README.md"),
    ]:
        files[name] = (root / source).read_bytes()
    files["corresponding-source.zip"] = source_archive(root)
    manifest = {
        "product": release["product"],
        "version": release["version"],
        "files": {
            name: hashlib.sha256(data).hexdigest() for name, data in files.items()
        },
    }
    files["payload-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    for name, data in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return files


def bootstrap(payload):
    encoded = base64.b64encode(payload).decode("ascii")
    chunks = "\n".join(
        "    " + repr(encoded[i : i + 100]) for i in range(0, len(encoded), 100)
    )
    return (
        """#FLM: Install HT Letterspacer
# HT Letterspacer for FontLab 9 — Apache-2.0. Full source is included in the release.
# Double-click this file to run it in FontLab 9. No Git or external Python required.
import sys
if sys.version_info < (3, 9):
    raise RuntimeError("HT Letterspacer needs Python 3.9 or newer. Select Python 3 in FontLab 9's scripting preferences.")
import base64, hashlib, io, shutil, tempfile, types, zipfile
from pathlib import Path
import fontlab
_preferences = fontlab.flPreferences()
_data = _preferences.dataPathDefault
_data = _data() if callable(_data) else _data
if Path(str(_data)).name != "FontLab 9":
    raise RuntimeError("Open this installer with FontLab 9.")
_PAYLOAD = (
"""
        + chunks
        + """\n)
_bytes = base64.b64decode(_PAYLOAD)
if hashlib.sha256(_bytes).hexdigest() != """
        + repr(hashlib.sha256(payload).hexdigest())
        + """:
    raise RuntimeError("This installer is damaged. Please download it again.")
_temp = Path(tempfile.mkdtemp(prefix="htls-installer-"))
try:
    with zipfile.ZipFile(io.BytesIO(_bytes)) as _z:
        for _i in _z.infolist():
            _p = Path(_i.filename)
            if _p.is_absolute() or ".." in _p.parts or "\\\\" in _i.filename or ":" in _i.filename:
                raise RuntimeError("Invalid installer payload.")
        _z.extractall(str(_temp))
    _core = types.ModuleType("_htls_install_core")
    _core.__file__ = str(_temp / "htls_installer.py")
    exec(compile((_temp / "htls_installer.py").read_bytes(), _core.__file__, "exec"), _core.__dict__)
    _gui = types.ModuleType("_htls_installer_gui")
    _gui.__file__ = str(_temp / "htls_install_ui.py")
    sys.modules[_gui.__name__] = _gui
    exec(compile((_temp / "htls_install_ui.py").read_bytes(), _gui.__file__, "exec"), _gui.__dict__)
    _gui.run_fontlab_installer(_temp, core=_core, cleanup=_temp)
except Exception:
    shutil.rmtree(str(_temp), ignore_errors=True)
    raise
"""
    ).encode("utf-8")


def build(output, root=ROOT):
    root = Path(root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    version = json.loads((root / "release.json").read_text())["version"]
    stem = "HT-Letterspacer-FontLab-" + version
    with tempfile.TemporaryDirectory(prefix="htls-build-") as temp:
        payload = zip_files(make_payload(Path(temp), root))
    installer = bootstrap(payload)
    compile(installer, "Install HT Letterspacer.vfpy", "exec")
    (output / ("Install-HT-Letterspacer-" + version + ".vfpy")).write_bytes(installer)
    source_zip = source_archive(root)
    source_name = stem + "-source.zip"
    (output / source_name).write_bytes(source_zip)
    customer = {
        stem + "/Install HT Letterspacer.vfpy": installer,
        stem + "/READ ME.txt": (root / "docs/INSTALL.txt").read_bytes(),
        stem + "/LICENSE.txt": (root / "LICENSE").read_bytes(),
        stem + "/NOTICES.txt": (root / "NOTICES.txt").read_bytes(),
        stem + "/" + source_name: source_zip,
    }
    package = output / (stem + ".zip")
    package.write_bytes(zip_files(customer))
    published = [
        package,
        output / ("Install-HT-Letterspacer-" + version + ".vfpy"),
        output / source_name,
    ]
    sums = "".join(
        hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n"
        for path in published
    )
    (output / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    return published


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    for path in build(args.output):
        print(path)
