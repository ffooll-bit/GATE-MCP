"""Load GAIN-Coding workflow/policy specs from the repo's specs/ directory.

Specs are cached in memory for the lifetime of the server; they are treated as
static per deployment (no runtime reloading).
"""

from functools import cache
from pathlib import Path

import yaml

# Repo root: src/gate_mcp/spec_loader.py -> .parent=src/gate_mcp, .parent.parent=src,
# .parent.parent.parent = repo root. This holds for editable/from-checkout installs,
# which is how the stdio server is run for this project.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class SpecError(Exception):
    """Raised when a workflow/policy spec is missing or invalid."""


def _load_spec(kind: str, name: str) -> dict:
    path = REPO_ROOT / "specs" / kind / f"{name}.yaml"
    if not path.is_file():
        raise SpecError(f"{kind} spec not found: {path.relative_to(REPO_ROOT)}")
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise SpecError(f"invalid YAML in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecError(f"invalid {kind} spec {name!r}: root must be a mapping")
    return data


@cache
def load_workflow_spec(name: str) -> dict:
    """Load and validate a workflow spec from specs/workflows/<name>.yaml."""
    data = _load_spec("workflows", name)
    workflow = data.get("workflow") or {}
    if workflow.get("name") != name:
        raise SpecError(f"workflow spec {name!r}: 'workflow.name' must equal {name!r}")
    for key in ("interactions", "fields", "gates"):
        if key not in data:
            raise SpecError(f"workflow spec {name!r}: missing top-level '{key}'")
    return data


@cache
def load_policy_spec(name: str) -> dict:
    """Load a policy spec from specs/policies/<name>.yaml."""
    return _load_spec("policies", name)
