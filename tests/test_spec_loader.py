"""Tests for the GAIN-Coding workflow/policy spec loader."""

import pytest
import yaml

from gate_mcp import spec_loader


def test_load_valid_workflow():
    spec = spec_loader.load_workflow_spec("findings-and-planning")
    assert spec["workflow"]["name"] == "findings-and-planning"
    assert {"workflow", "interactions", "fields", "gates"} <= set(spec)


def test_missing_workflow_raises():
    with pytest.raises(spec_loader.SpecError):
        spec_loader.load_workflow_spec("no-such-workflow")


def test_missing_policy_raises():
    with pytest.raises(spec_loader.SpecError):
        spec_loader.load_policy_spec("no-such-policy")


def _write_spec(tmp_path, name, data):
    d = tmp_path / "specs" / "workflows"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return d


def test_workflow_name_mismatch_raises(tmp_path, monkeypatch):
    _write_spec(tmp_path, "mismatch", {"workflow": {"name": "other"}})
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    with pytest.raises(spec_loader.SpecError):
        spec_loader.load_workflow_spec("mismatch")


def test_missing_required_key_raises(tmp_path, monkeypatch):
    _write_spec(
        tmp_path,
        "missingkey",
        {"workflow": {"name": "missingkey"}, "interactions": {}},
    )
    monkeypatch.setattr(spec_loader, "REPO_ROOT", tmp_path)
    with pytest.raises(spec_loader.SpecError):
        spec_loader.load_workflow_spec("missingkey")
