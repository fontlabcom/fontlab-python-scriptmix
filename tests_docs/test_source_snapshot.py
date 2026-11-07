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
