"""Load unmodified upstream source with imports scoped to these modules only.

No fake Cocoa/Glyphs modules are installed into sys.modules. Other FontLab
scripts keep their own imports. The math, configuration and rule matcher are
executed byte-for-byte from the verified, pinned upstream source directory.
"""

import builtins
import hashlib
import json
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace


class Point:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index):
        return (self.x, self.y)[index]


class _Callbacks:
    @staticmethod
    def callbacksForType_(name):
        return []  # FL renders paths before measurement.


_cached = None


def load(root=None):
    global _cached
    if _cached is not None and root is None:
        return _cached
    project = Path(__file__).resolve().parents[1]
    vendored = project / "vendor" / "HTLetterspacer"
    default_root = (
        vendored
        if vendored.is_dir()
        else Path(
            os.environ.get("HTLS_UPSTREAM", "") or project.parent / "HTLetterspacer"
        )
    )
    root = Path(root or default_root).expanduser()
    resource = root / "HTLetterspacer.glyphsPlugin" / "Contents" / "Resources" / "htls"
    lock = json.loads((project / "upstream.lock.json").read_text())
    package = ModuleType("_htls_fontlab_upstream")
    cocoa = SimpleNamespace(
        NSMakePoint=Point,
        NSMinX=lambda b: b[0],
        NSMinY=lambda b: b[1],
        NSMaxX=lambda b: b[2],
        NSMaxY=lambda b: b[3],
    )
    imports = {
        "htls": package,
        "Foundation": cocoa,
        "GlyphsApp": SimpleNamespace(),
        "objc": SimpleNamespace(lookUpClass=lambda name: _Callbacks),
    }

    def scoped_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in imports:
            return imports[name]
        return builtins.__import__(name, globals, locals, fromlist, level)

    for name in ("config", "rules", "engine"):
        path = resource / (name + ".py")
        if not path.is_file():
            raise RuntimeError(
                "Original HTLetterspacer files are missing at %s. Run the HT Letterspacer installer again."
                % root
            )
        source = path.read_bytes()
        if hashlib.sha256(source).hexdigest() != lock["sha256"][name + ".py"]:
            raise RuntimeError(
                "Upstream %s differs from the tested revision %s. See README update instructions."
                % (name, lock["commit"])
            )
        module = ModuleType(package.__name__ + "." + name)
        module.__file__ = str(path)
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=scoped_import)
        exec(compile(source, str(path), "exec"), module.__dict__)
        setattr(package, name, module)
    package.root = root
    package.revision = lock["commit"]
    if root == Path(default_root).expanduser():
        _cached = package
    return package
