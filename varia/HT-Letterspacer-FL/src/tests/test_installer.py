"""Installer regression tests run outside FontLab with a tiny verified upstream fixture."""

import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from installer import core
from tools.build_release import make_payload


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="htls-install-tests-")
        cls.root = Path(cls.temp.name)
        cls.payload = cls.root / "payload"
        make_payload(cls.payload)
        cls.archive = cls.root / "upstream.zip"
        contents = {
            name: b"VALUE = 17\n" for name in ("config.py", "rules.py", "engine.py")
        }
        with zipfile.ZipFile(cls.archive, "w") as z:
            for name, data in contents.items():
                z.writestr(
                    "HTLetterspacer-test/HTLetterspacer.glyphsPlugin/Contents/Resources/htls/"
                    + name,
                    data,
                )
            z.writestr("HTLetterspacer-test/LICENSE", "GPL-3.0 test fixture")
        lock = core.read_json(cls.payload / "upstream.lock.json")
        lock["sha256"] = {
            name: core.hashlib.sha256(data).hexdigest()
            for name, data in contents.items()
        }
        lock["archive"]["sha256"] = core.digest(cls.archive)
        (cls.payload / "upstream.lock.json").write_text(json.dumps(lock))
        manifest = core.read_json(cls.payload / "payload-manifest.json")
        manifest["files"]["upstream.lock.json"] = core.digest(
            cls.payload / "upstream.lock.json"
        )
        (cls.payload / "payload-manifest.json").write_text(json.dumps(manifest))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(dir=self.root))
        self.data = self.work / "Different User — Жан" / "FontLab 9"

    def install(self):
        return core.install(self.payload, self.data, archive=self.archive)

    def test_clean_install_and_relocation_without_developer_checkout(self):
        result = self.install()
        original = Path(result["runtime"])
        self.assertTrue((original / "vendor/HTLetterspacer/LICENSE").exists())
        destination = self.work / "relocated profile" / "FontLab 9"
        destination.parent.mkdir()
        shutil.move(str(self.data), str(destination))
        state = core.read_json(
            destination / "Extensions" / core.FOLDER / "installation.json"
        )
        runtime = destination / "Extensions" / core.FOLDER / state["active"]
        script = destination / "Scripts" / core.FOLDER / "HT Letterspacer.py"
        code = """import sys,os,runpy
sys.path.insert(0,%r)
os.environ['HTLS_UPSTREAM']='/missing/old/development/path'
import htls_fontlab
from htls_fontlab.upstream import load
assert load().engine.VALUE == 17
htls_fontlab.show=lambda: print('PORTABLE_OK')
runpy.run_path(%r,run_name='__main__')
""" % (
            str(runtime),
            str(script),
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("PORTABLE_OK", result.stdout)
        self.assertNotIn(str(self.payload), script.read_text())
        self.assertNotIn("Developer", script.read_text())

    def test_reinstall_repairs_changed_runtime(self):
        first = self.install()
        old = Path(first["runtime"])
        (old / "htls_fontlab/__init__.py").write_text("broken")
        second = self.install()
        new = Path(second["runtime"])
        self.assertNotEqual(old, new)
        self.assertEqual(
            core.digest(new / "htls_fontlab/__init__.py"),
            core.digest(self.payload / "htls_fontlab/__init__.py"),
        )
        state = core.read_json(
            self.data / "Extensions" / core.FOLDER / "installation.json"
        )
        self.assertEqual(state["previous"], "releases/" + old.name)
        self.assertTrue(old.exists())

    def test_development_launchers_migrate(self):
        folder = self.data / "Scripts" / core.FOLDER
        folder.mkdir(parents=True)
        (folder / "HT Letterspacer.py").write_text(
            core.OLD_MARKER + "runpy.run_path('/Users/developer/repo/script.py')"
        )
        self.install()
        self.assertTrue(
            (folder / "HT Letterspacer.py").read_text().startswith(core.MARKER)
        )

    def test_unowned_script_is_preserved(self):
        folder = self.data / "Scripts" / core.FOLDER
        folder.mkdir(parents=True)
        user = folder / "HTLS Manager.py"
        user.write_text("my personal script")
        with self.assertRaisesRegex(ValueError, "existing script"):
            self.install()
        self.assertEqual(user.read_text(), "my personal script")
        self.assertFalse((self.data / "Extensions" / core.FOLDER).exists())

    def test_bad_archive_keeps_previous_installation(self):
        self.install()
        receipt = self.data / "Extensions" / core.FOLDER / "installation.json"
        before = receipt.read_bytes()
        bad = self.work / "bad.zip"
        bad.write_bytes(b"not the original source")
        with self.assertRaisesRegex(ValueError, "checksum"):
            core.install(self.payload, self.data, archive=bad)
        self.assertEqual(receipt.read_bytes(), before)

    def test_failed_write_rolls_back_scripts_and_receipt(self):
        self.install()
        home = self.data / "Extensions" / core.FOLDER
        receipt = (home / "installation.json").read_bytes()
        scripts = self.data / "Scripts" / core.FOLDER
        before = {name: (scripts / name).read_bytes() for name in core.SCRIPTS}
        real = core.atomic_write
        failed = [False]

        def fail_once(path, data):
            if Path(path).name == "HTLS Manager.py" and not failed[0]:
                failed[0] = True
                raise OSError("simulated disk failure")
            real(path, data)

        with mock.patch.object(core, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "simulated"):
                self.install()
        self.assertEqual((home / "installation.json").read_bytes(), receipt)
        self.assertEqual(
            before, {name: (scripts / name).read_bytes() for name in core.SCRIPTS}
        )
        self.assertEqual(len(list((home / "releases").iterdir())), 1)

    def test_network_failure_keeps_previous_installation(self):
        self.install()
        receipt = self.data / "Extensions" / core.FOLDER / "installation.json"
        before = receipt.read_bytes()
        with mock.patch.object(
            core, "download_upstream", side_effect=OSError("offline")
        ):
            with self.assertRaisesRegex(OSError, "offline"):
                core.install(self.payload, self.data)
        self.assertEqual(receipt.read_bytes(), before)

    def test_uninstall_keeps_other_scripts_and_recoverable_runtime(self):
        result = self.install()
        scripts = Path(result["scripts_dir"])
        extra = scripts / "Personal.py"
        extra.write_text("personal")
        backup = Path(core.uninstall(self.data))
        self.assertTrue((backup / "installation.json").exists())
        self.assertTrue(extra.exists())
        self.assertFalse((scripts / "HT Letterspacer.py").exists())
        self.assertFalse((self.data / "Extensions" / core.FOLDER).exists())

    def test_zip_traversal_rejected(self):
        bad = self.work / "traversal.zip"
        with zipfile.ZipFile(bad, "w") as z:
            z.writestr("root/../../escaped.py", "bad")
        with self.assertRaises(ValueError):
            core.extract_upstream(bad, self.work / "extract")
        self.assertFalse((self.work / "escaped.py").exists())

    def test_target_symlinks_rejected(self):
        self.data.mkdir(parents=True)
        outside = self.work / "outside"
        outside.mkdir()
        (self.data / "Scripts").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            self.install()
        self.assertFalse(list(outside.iterdir()))

    def test_concurrent_installer_is_rejected(self):
        with core.installation_lock(self.data):
            with self.assertRaisesRegex(RuntimeError, "already in progress"):
                self.install()

    def test_native_data_path_uses_fontlab_not_os_guesses(self):
        for value in (
            "C:/Users/Jane/OneDrive/Documents/FontLab/FontLab 9",
            str(self.work / "Custom Mac Data/FontLab 9"),
        ):
            fake = mock.Mock()
            fake.flPreferences.return_value.dataPathDefault = value
            with mock.patch.dict(sys.modules, {"fontlab": fake}):
                self.assertEqual(core.fontlab_data_dir(), Path(value).resolve())


if __name__ == "__main__":
    unittest.main()
