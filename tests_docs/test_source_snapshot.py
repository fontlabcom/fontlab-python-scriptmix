# this_file: tests_docs/test_source_snapshot.py
"""Public metadata retains exact source identity without rendering implementation."""
import hashlib
import importlib.util
from pathlib import Path
from urllib.parse import quote
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("name", ["A (B).py", "Accented Ż.py", "Tick's Proof.py", "Dots.A.py"])
def test_menu_source_when_filename_contains_punctuation_then_exact_safe_include(tmp_path, name):
    spec = importlib.util.spec_from_file_location("owned_menu_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "Scripts/Reports" / name
    source.parent.mkdir(parents=True)
    data = b'"""Owned report fixture."""\nprint("source is not executed")\n'
    source.write_bytes(data)
    module.catalogue(tmp_path, revision="a" * 40)
    pages = [p for p in (tmp_path / "src_docs/md/scripts").glob("*/*.md") if p.name != "index.md"]
    assert len(pages) == 1
    text = pages[0].read_text()
    digest = hashlib.sha256(data).hexdigest()
    assert "Owned report fixture." in text
    assert digest in text
    assert "https://github.com/fontlabcom/fontlab-python-scriptmix/blob/" + "a" * 40 + "/" + quote(source.relative_to(tmp_path).as_posix(), safe="/") in text
    assert "codeinclude" not in text and 'print("source is not executed")' not in text
    assert (tmp_path / ".build/menu-sources" / (digest + ".py")).read_bytes() == data
    assert source.read_bytes() == data


@pytest.mark.parametrize("revision", ["", "main", "0" * 39, "g" * 40])
def test_catalogue_when_revision_invalid_then_existing_output_survives(tmp_path, revision):
    spec = importlib.util.spec_from_file_location("owned_menu_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / "src_docs/md/scripts/sentinel.md"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"owned prior output")
    with pytest.raises(ValueError, match="complete source commit"):
        module.catalogue(tmp_path, revision=revision)
    assert output.read_bytes() == b"owned prior output"


def _build_module():
    spec = importlib.util.spec_from_file_location("owned_menu_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo, *args):
    import subprocess

    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo, check=True, capture_output=True,
    )


def _repo_with_scripts(tmp_path):
    scripts = tmp_path / "Scripts/Reports"
    scripts.mkdir(parents=True)
    (scripts / "Committed.py").write_bytes(b'"""Committed."""\n')
    (scripts / "Dirty.py").write_bytes(b'"""Dirty."""\n')
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "Scripts")
    _git(tmp_path, "commit", "-qm", "init")
    import subprocess

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    return scripts, head


def test_catalogue_when_menu_is_committed_then_link_is_kept(tmp_path):
    _, head = _repo_with_scripts(tmp_path)
    _build_module().catalogue(tmp_path, revision=head)
    page = (tmp_path / "src_docs/md/scripts/reports/committed.md").read_text()
    assert f"/blob/{head}/Scripts/Reports/Committed.py" in page


def test_catalogue_when_menu_is_dirty_then_no_false_immutable_link(tmp_path):
    scripts, head = _repo_with_scripts(tmp_path)
    (scripts / "Dirty.py").write_bytes(b'"""Dirty edited."""\n')
    _build_module().catalogue(tmp_path, revision=head)
    page = (tmp_path / "src_docs/md/scripts/reports/dirty.md").read_text()
    assert "/blob/" not in page
    assert "not committed at" in page and head[:12] in page
    assert hashlib.sha256(b'"""Dirty edited."""\n').hexdigest() in page
    assert "/blob/" in (tmp_path / "src_docs/md/scripts/reports/committed.md").read_text()


def test_catalogue_when_menu_is_untracked_then_no_false_immutable_link(tmp_path):
    scripts, head = _repo_with_scripts(tmp_path)
    (scripts / "Fresh.py").write_bytes(b'"""Fresh."""\n')
    _build_module().catalogue(tmp_path, revision=head)
    page = (tmp_path / "src_docs/md/scripts/reports/fresh.md").read_text()
    assert "/blob/" not in page and "not committed at" in page
