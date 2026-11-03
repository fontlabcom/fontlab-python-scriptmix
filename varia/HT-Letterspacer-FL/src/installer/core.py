"""Verified, transactional per-user installation. Standard library only."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import ssl
import stat
import tempfile
import urllib.request
import uuid
from contextlib import contextmanager

PRODUCT = "org.fontlab.htletterspacer.gateway"
FOLDER = "HT Letterspacer"
MARKER = "# HTLS FontLab managed launcher\n"
OLD_MARKER = "# HTLS FontLab generated launcher\n"
SCRIPTS = {
    "HT Letterspacer.py": "show",
    "Apply HTLS Values.py": "show",
    "Apply HTLS Config.py": "apply_selection",
    "HTLS Manager.py": "show_manager",
    "Uninstall HT Letterspacer.py": "uninstall",
}


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_write(path, data):
    path = Path(path)
    temp = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temp), str(path))
    finally:
        if temp.exists():
            temp.unlink()


def safe_relative(name):
    p = PurePosixPath(name)
    if (
        not name
        or p.is_absolute()
        or "\\" in name
        or ":" in name
        or any(x in ("..", ".") for x in name.split("/"))
    ):
        raise ValueError("Unsafe archive or manifest path: " + name)
    return p


def extract_upstream(archive, destination):
    """Extract regular files only; Git's plugin symlinks are kept in the source ZIP."""
    import zipfile

    destination = Path(destination)
    seen = set()
    with zipfile.ZipFile(str(archive)) as z:
        entries = z.infolist()
        if sum(i.file_size for i in entries) > 100 * 1024 * 1024:
            raise ValueError("Upstream archive exceeds the extraction limit.")
        roots = {safe_relative(i.filename.rstrip("/")).parts[0] for i in entries}
        if len(roots) != 1:
            raise ValueError("Expected one upstream archive root.")
        for info in entries:
            parts = safe_relative(info.filename.rstrip("/")).parts[1:]
            if not parts:
                continue
            relative = "/".join(parts)
            key = relative.casefold()
            if key in seen:
                raise ValueError("Duplicate archive path: " + relative)
            seen.add(key)
            if stat.S_ISLNK(info.external_attr >> 16):
                continue
            target = destination.joinpath(*parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)


def verify_payload(payload):
    payload = Path(payload)
    manifest = read_json(payload / "payload-manifest.json")
    if manifest.get("product") != PRODUCT:
        raise ValueError("Not an HT Letterspacer installer.")
    for name, expected in manifest["files"].items():
        p = payload.joinpath(*safe_relative(name).parts)
        if p.is_symlink() or not p.is_file() or digest(p) != expected:
            raise ValueError("Damaged installer file: " + name)
    required = {
        "release.json",
        "upstream.lock.json",
        "htls_fontlab/__init__.py",
        "htls_installer.py",
        "htls_install_ui.py",
    }
    if not required.issubset(manifest["files"]):
        raise ValueError("Installer payload is incomplete.")
    return manifest


def verify_upstream(folder, lock):
    resource = (
        Path(folder) / "HTLetterspacer.glyphsPlugin" / "Contents" / "Resources" / "htls"
    )
    for name, expected in lock["sha256"].items():
        safe_relative(name)
        p = resource / name
        if not p.is_file() or digest(p) != expected:
            raise ValueError("Original HTLetterspacer verification failed: " + name)
    if not (Path(folder) / "LICENSE").is_file():
        raise ValueError("Upstream license is missing.")


def download_upstream(lock, destination, ca_file):
    spec = lock["archive"]
    expected_url = (
        "https://codeload.github.com/huertatipografica/HTLetterspacer/zip/"
        + lock["commit"]
    )
    if spec["url"] != expected_url:
        raise ValueError("Unexpected upstream download address.")
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=str(ca_file))
    request = urllib.request.Request(
        expected_url, headers={"User-Agent": "HTLetterspacer-FontLab-Installer/1.0"}
    )
    count = 0
    with urllib.request.urlopen(request, timeout=45, context=context) as response, Path(
        destination
    ).open("wb") as out:
        if not response.geturl().startswith("https://codeload.github.com/"):
            raise ValueError("Unexpected upstream redirect.")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > 32 * 1024 * 1024:
                raise ValueError("Upstream download is unexpectedly large.")
            out.write(chunk)
    if digest(destination) != spec["sha256"]:
        raise ValueError("Upstream download checksum failed. No scripts were changed.")


def fontlab_data_dir():
    # FontLab's Scripts panel specifically scans dataPathDefault/Scripts.
    # Windows uses Documents (which may be redirected), macOS uses Application Support.
    import fontlab

    value = fontlab.flPreferences().dataPathDefault
    value = value() if callable(value) else value
    if not value:
        raise RuntimeError("FontLab did not report its user data folder.")
    return Path(str(value)).expanduser().resolve()


def launcher(label, action):
    return (
        MARKER
        + "#FLM: "
        + label
        + """
import json
import sys
from pathlib import Path
_data = Path(__file__).resolve().parents[2]
_home = _data / "Extensions" / "HT Letterspacer"
_state = json.loads((_home / "installation.json").read_text(encoding="utf-8"))
if _state.get("product") != "org.fontlab.htletterspacer.gateway":
    raise RuntimeError("HT Letterspacer installation is invalid. Run the installer again.")
_relative = Path(_state["active"])
_root = (_home / _relative).resolve()
if _relative.is_absolute() or _home.resolve() not in _root.parents or not (_root / "htls_fontlab").is_dir():
    raise RuntimeError("HT Letterspacer files are missing. Run the installer again.")
_old = sys.modules.get("htls_fontlab")
if _old and Path(_old.__file__).resolve().parent != _root / "htls_fontlab":
    raise RuntimeError("HT Letterspacer was updated. Restart FontLab to load the new version.")
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
"""
        + (
            """
from htls_install_ui import confirm_uninstall
confirm_uninstall(_data)
"""
            if action == "uninstall"
            else "\nfrom htls_fontlab import " + action + "\n" + action + "()\n"
        )
    )


def managed_script(path):
    if path.is_symlink():
        return False
    try:
        start = path.read_text(encoding="utf-8")
        return start.startswith((MARKER, OLD_MARKER))
    except (OSError, UnicodeError):
        return False


def check_paths(data):
    for path in (
        data / "Extensions",
        data / "Extensions" / FOLDER,
        data / "Scripts",
        data / "Scripts" / FOLDER,
    ):
        if path.is_symlink():
            raise ValueError("Installation target is a symbolic link: " + str(path))
        if path.exists() and not path.is_dir():
            raise ValueError("Installation target is not a folder: " + str(path))
    home = data / "Extensions" / FOLDER
    if home.exists():
        try:
            owner = read_json(home / "installation.json")
        except (OSError, ValueError):
            raise ValueError(
                "This folder is not a managed HTLS installation: " + str(home)
            )
        if owner.get("product") != PRODUCT:
            raise ValueError("Refusing to replace an unrelated installation.")
        if (home / "releases").is_symlink():
            raise ValueError("Release directory is a symbolic link.")
    scripts = data / "Scripts" / FOLDER
    for name in SCRIPTS:
        path = scripts / name
        if path.exists() or path.is_symlink():
            if not managed_script(path):
                raise ValueError(
                    "Refusing to replace your existing script: " + str(path)
                )
    return home, scripts


@contextmanager
def installation_lock(data):
    extensions = data / "Extensions"
    if extensions.is_symlink():
        raise ValueError("Extensions is a symbolic link.")
    extensions.mkdir(parents=True, exist_ok=True)
    lock = extensions / ".htls-install-lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError(
            "An HT Letterspacer installation is already in progress. If FontLab previously crashed, remove "
            + str(lock)
        )
    try:
        yield
    finally:
        lock.rmdir()


def install(payload, data_dir, archive=None, progress=lambda message: None):
    payload = Path(payload).resolve()
    data = Path(data_dir).expanduser().resolve()
    manifest = verify_payload(payload)
    release = read_json(payload / "release.json")
    lock = read_json(payload / "upstream.lock.json")
    with installation_lock(data):
        home, scripts = check_paths(data)
        progress("Downloading original HT Letterspacer…")
        with tempfile.TemporaryDirectory(
            prefix=".htls-stage-", dir=str(data / "Extensions")
        ) as temp:
            stage = Path(temp) / "release"
            stage.mkdir()
            for name in manifest["files"]:
                target = stage.joinpath(*safe_relative(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(str(payload / name), str(target))
            shutil.copyfile(
                str(payload / "payload-manifest.json"),
                str(stage / "payload-manifest.json"),
            )
            source_zip = stage / "upstream-source.zip"
            if archive is None:
                download_upstream(lock, source_zip, stage / "ca.pem")
            else:
                shutil.copyfile(str(archive), str(source_zip))
            if digest(source_zip) != lock["archive"]["sha256"]:
                raise ValueError("Original plugin archive checksum failed.")
            progress("Verifying original plugin and installing scripts…")
            upstream = stage / "vendor" / "HTLetterspacer"
            upstream.mkdir(parents=True)
            extract_upstream(source_zip, upstream)
            verify_upstream(upstream, lock)
            # Check all new code before changing the active installation.
            for path in stage.rglob("*.py"):
                if "vendor" not in path.relative_to(stage).parts:
                    compile(path.read_bytes(), str(path), "exec")
            old_receipt = (
                (home / "installation.json").read_bytes() if home.exists() else None
            )
            old_scripts = {
                name: (
                    (scripts / name).read_bytes() if (scripts / name).exists() else None
                )
                for name in SCRIPTS
            }
            previous = json.loads(old_receipt)["active"] if old_receipt else None
            release_id = release["version"] + "-" + uuid.uuid4().hex[:12]
            destination = home / "releases" / release_id
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(str(stage), str(destination))
                scripts.mkdir(parents=True, exist_ok=True)
                for name, action in SCRIPTS.items():
                    atomic_write(
                        scripts / name,
                        launcher(Path(name).stem, action).encode("utf-8"),
                    )
                state = {
                    "product": PRODUCT,
                    "version": release["version"],
                    "active": "releases/" + release_id,
                    "previous": previous,
                    "upstream_commit": lock["commit"],
                    "scripts": list(SCRIPTS),
                }
                atomic_write(
                    home / "installation.json",
                    (json.dumps(state, indent=2) + "\n").encode("utf-8"),
                )
            except Exception:
                for name, content in old_scripts.items():
                    path = scripts / name
                    if content is None:
                        if path.exists() and managed_script(path):
                            path.unlink()
                    else:
                        atomic_write(path, content)
                if old_receipt is not None:
                    atomic_write(home / "installation.json", old_receipt)
                if destination.exists():
                    shutil.rmtree(destination)
                if old_receipt is None:
                    for path in (home / "releases", home, scripts):
                        if path.exists() and not any(path.iterdir()):
                            path.rmdir()
                raise
        progress("Installation complete.")
        return {
            "data_dir": str(data),
            "scripts_dir": str(scripts),
            "runtime": str(destination),
            "version": release["version"],
        }


def uninstall(data_dir):
    """Remove managed launchers; retain runtime as a recoverable local backup."""
    data = Path(data_dir).expanduser().resolve()
    with installation_lock(data):
        home, scripts = check_paths(data)
        if not home.exists():
            raise ValueError("HT Letterspacer is not installed.")
        backup = home.with_name(".HTLS-uninstalled-" + uuid.uuid4().hex[:12])
        old = {
            name: (scripts / name).read_bytes()
            for name in SCRIPTS
            if (scripts / name).exists()
        }
        os.replace(str(home), str(backup))
        try:
            for name in old:
                (scripts / name).unlink()
        except Exception:
            os.replace(str(backup), str(home))
            for name, content in old.items():
                atomic_write(scripts / name, content)
            raise
        if scripts.exists() and not any(scripts.iterdir()):
            scripts.rmdir()
        return str(backup)
