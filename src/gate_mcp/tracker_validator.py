"""Parse and validate docs/IMPROVEMENTS.md (format, numbering, gate rules)."""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO_ROOT = Path(
    os.environ.get("GATE_MCP_REPO") or Path(__file__).resolve().parent.parent.parent
)
TRACKER = REPO_ROOT / "docs" / "IMPROVEMENTS.md"

ID_RE = re.compile(r"^([A-Z]+)-(\d{3})$")

# Field bullets that make up an item, in canonical order (matches the template).
ITEM_FIELDS = [
    "Status",
    "Issue",
    "Recorded",
    "Implemented",
    "Problem",
    "Possible Fix",
    "Actual Fix",
    "Rejection Reason",
    "Actual Implemented",
    "Changes",
]

EMPTY = "\u2014"  # em-dash placeholder, —


def _strip(value: str) -> str:
    return value.strip().strip("`").strip()


def _empty(value: str) -> bool:
    v = _strip(value)
    return v == "" or v == EMPTY


def _next_number(code: str, items: list[dict]) -> int:
    nums = [
        int(ID_RE.match(item["id"]).group(2))
        for item in items
        if item["id"] and ID_RE.match(item["id"]) and item["id"].startswith(f"{code}-")
    ]
    return (max(nums) + 1) if nums else 1


def read_tracker(path: Path = TRACKER) -> str:
    """Return the raw tracker text."""
    return path.read_text(encoding="utf-8")


def write_tracker(text: str, path: Path = TRACKER) -> None:
    """Write tracker text (UTF-8, no BOM) back to docs/IMPROVEMENTS.md."""
    path.write_text(text, encoding="utf-8")


def parse_tracker(text: str) -> list[dict]:
    """Parse the Items section of IMPROVEMENTS.md into item dicts.

    Each item has keys: id, title, fields (dict keyed by field name).
    """
    items: list[dict] = []
    in_items = False
    current: dict | None = None
    for line in text.splitlines():
        if line.startswith("## Items"):
            in_items = True
            continue
        if not in_items:
            continue
        if line.startswith("### "):
            current = {"id": None, "title": "", "fields": {}}
            items.append(current)
            heading = line[4:].strip()
            if " \u2014 " in heading:
                head, rest = heading.split(" \u2014 ", 1)
                if ID_RE.match(head.strip()):
                    current["id"] = head.strip()
                    current["title"] = rest.strip()
                    continue
            current["title"] = heading
            continue
        if current is not None:
            m = re.match(r"- \*\*(.+?):\*\*\s*(.*)$", line)
            if m:
                current["fields"][m.group(1)] = m.group(2).rstrip()
    return items


def validate_format(items: list[dict]) -> list[str]:
    """Check every item follows the '<LABEL>-<NNN> — <Title>' skeleton with all fields."""
    errors: list[str] = []
    for i, item in enumerate(items, 1):
        item_id = item["id"]
        if item_id is None:
            errors.append(f"item {i}: heading is not '<LABEL>-<NNN> — <Title>'")
            continue
        missing = [f for f in ITEM_FIELDS if f not in item["fields"]]
        if missing:
            errors.append(f"{item_id}: missing fields: {', '.join(missing)}")
    return errors


def validate_numbering(items: list[dict]) -> list[str]:
    """Check IDs are numbered per label code from 001 with no duplicates or gaps."""
    errors: list[str] = []
    by_code: dict[str, list[int]] = {}
    for item in items:
        if item["id"] is None:
            continue
        code, num = (
            ID_RE.match(item["id"]).group(1),
            int(ID_RE.match(item["id"]).group(2)),
        )
        by_code.setdefault(code, []).append(num)
    for code in sorted(by_code):
        nums = by_code[code]
        if len(nums) != len(set(nums)):
            errors.append(f"{code}: duplicate sequence numbers")
            continue
        expected = 1
        for num in sorted(nums):
            if num != expected:
                errors.append(
                    f"{code}: gap — expected {code}-{expected:03d}, found {code}-{num:03d}"
                )
                break
            expected += 1
    return errors


# Fields that must be filled (not empty/em-dash) per tracker Status.
STATUS_REQUIRED = {
    "recorded": ["Recorded", "Problem", "Possible Fix"],
    "verified": ["Recorded", "Problem", "Possible Fix", "Actual Fix"],
    "rejected": ["Recorded", "Problem", "Possible Fix", "Rejection Reason"],
    "implemented": [
        "Recorded",
        "Problem",
        "Possible Fix",
        "Implemented",
        "Actual Implemented",
        "Changes",
    ],
}


def validate_gate_rules(spec: dict, items: list[dict]) -> list[str]:
    """Check Status values and per-status required fields against the workflow spec."""
    errors: list[str] = []
    allowed = [
        v for v in ((spec.get("fields") or {}).get("status") or {}).get("values") or []
    ]
    for item in items:
        item_id = item["id"]
        if item_id is None:
            continue
        fields = item["fields"]
        status = _strip(fields.get("Status", "")).lower()
        if status not in allowed:
            errors.append(
                f"{item_id}: invalid Status {fields.get('Status', '')!r}; "
                f"allowed: {', '.join(allowed)}"
            )
            continue
        for field in STATUS_REQUIRED.get(status, []):
            if field not in fields or _empty(fields[field]):
                errors.append(f"{item_id}: Status={status} requires filled '{field}'")
    return errors


def validate_tracker(spec: dict, text: str) -> dict:
    """Run all validators over ``text``; returns {format, numbering, gate_rules} error lists."""
    items = parse_tracker(text)
    return {
        "format": validate_format(items),
        "numbering": validate_numbering(items),
        "gate_rules": validate_gate_rules(spec, items),
    }
