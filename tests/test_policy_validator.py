"""Tests for the writing-quality document policy validator."""

import yaml

from gate_mcp import policy_validator, spec_loader

DEFAULT = {
    "policy": {
        "name": "writing-quality",
        "description": "International English only, no hardwrap, LF line endings, no BOM, no trailing whitespace",
        "scope": "committed_documents",
    },
    "bom": {"allowed": "none", "severity": "error"},
    "line_ending": {"allowed": "lf", "severity": "error"},
    "trailing_whitespace": {"allowed": "none", "severity": "error"},
    "hardwrap": {
        "enabled": True,
        "severity": "warning",
        "min_sentence_broken_lines": 2,
        "sentence_end_chars": ".?!:;",
        "skip_prefixes": ["#", "-", "*", "|", ">", "```"],
    },
    "language": {
        "enforced": True,
        "severity": "warning",
        "target": "international_english",
        "non_ascii_severity": "error",
        "indonesian_function_words": ["yang", "dan", "untuk", "dengan", "pada"],
        "indonesian_token_ratio_threshold": 0.02,
    },
}


_counter = 0


def _write_policy(tmp_path):
    global _counter
    _counter += 1
    name = f"wq{_counter}"
    d = tmp_path / "specs" / "policies"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.yaml").write_text(yaml.safe_dump(DEFAULT), encoding="utf-8")
    return name


def _validate(tmp_path, content, name):
    doc = tmp_path / "doc.md"
    doc.write_bytes(content)
    return policy_validator.validate_doc(doc, name)


def test_clean_markdown_passes(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    content = b"# Title\n\nThis is a single flowing English sentence that does not force-wrap at any fixed column and stays on one line.\n"
    result = _validate(tmp_path, content, name)
    assert result["ok"] is True
    assert result["findings"] == []


def test_bom_is_error(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    result = _validate(tmp_path, b"\xef\xbb\xbf# Title\n", name)
    assert result["ok"] is False
    codes = [f["code"] for f in result["findings"]]
    assert "bom" in codes


def test_crlf_is_error(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    result = _validate(tmp_path, b"# Title\r\n\r\nBody.\r\n", name)
    assert result["ok"] is False
    codes = [f["code"] for f in result["findings"]]
    assert "crlf" in codes


def test_trailing_whitespace_is_error(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    result = _validate(tmp_path, b"# Title  \n\nBody.\n", name)
    assert result["ok"] is False
    codes = [f["code"] for f in result["findings"]]
    assert "trailing_whitespace" in codes


def test_non_latin_script_is_error(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    result = _validate(
        tmp_path, "# \u041f\u0440\u0438\u0432\u0435\u0442\n".encode("utf-8"), name
    )
    assert result["ok"] is False
    codes = [f["code"] for f in result["findings"]]
    assert "non_latin_script" in codes


def test_indonesian_text_is_warning(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    body = b"# Ringkasan\n\nIni adalah ringkasan untuk dokumen pada repository dengan bahasa dan tujuan yang jelas.\n"
    result = _validate(tmp_path, body, name)
    codes = [f["code"] for f in result["findings"]]
    assert "language" in codes
    assert all(f["severity"] != "error" for f in result["findings"])


def test_hardwrap_is_warning(monkeypatch, tmp_path):
    name = _write_policy(tmp_path)
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    body = (
        "This is the first line of a sentence that has been\n"
        "wrapped onto a second line and then\n"
        "onto a third line without stopping.\n"
    )
    result = _validate(tmp_path, body.encode("utf-8"), name)
    codes = [f["code"] for f in result["findings"]]
    assert "hardwrap" in codes
    assert all(f["severity"] != "error" for f in result["findings"])
