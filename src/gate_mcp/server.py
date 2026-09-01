"""GATE-MCP stdio server: findings-and-planning enforcement tools.

GATE = Guided Agent Through Enforcement. The full expansion is
"Guided Agent Through Enforcement MCP" (MCP stays unexpanded).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from gate_mcp.policy_validator import validate_doc as validate_doc_file
from gate_mcp.spec_loader import SpecError, load_workflow_spec
from gate_mcp.tracker_validator import (
    EMPTY,
    ITEM_FIELDS,
    TRACKER,
    _next_number,
    parse_tracker,
    read_tracker,
    validate_tracker,
    write_tracker,
)

WORKFLOW = "findings-and-planning"

mcp = FastMCP("gate-mcp")


def _spec() -> dict:
    return load_workflow_spec(WORKFLOW)


def _field_line(field: str, value: str) -> str:
    return f"- **{field}:** {value}"


def _render_block(item: dict) -> str:
    lines = [f"### {item['id']} — {item['title']}"]
    for field in ITEM_FIELDS:
        lines.append(_field_line(field, item["fields"].get(field, f"`{EMPTY}`")))
    return "\n".join(lines)


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def _replace_item_field(text: str, item_id: str, field: str, value: str) -> str:
    """Replace one field line inside the ``item_id`` block; returns new text."""
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if (
            line.startswith("### ")
            and line[4:].split(" \u2014 ", 1)[0].strip() == item_id
        ):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"item not found: {item_id}")
    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        if line.startswith("### "):
            break
        mm = re.match(r"- \*\*(.+?):\*\*", line)
        if mm and mm.group(1) == field:
            lines[i] = _field_line(field, value)
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    raise ValueError(f"field {field!r} not found in item {item_id}")


@mcp.tool()
def record_finding(
    title: str,
    problem: str,
    possible_fix: str,
    label_code: str = "ENH",
) -> dict:
    """Record a new improvement finding in docs/IMPROVEMENTS.md (Status=recorded)."""
    try:
        spec = _spec()
    except SpecError as exc:
        return {"ok": False, "error": str(exc)}
    code = label_code.upper()
    label_codes = (spec.get("fields") or {}).get("id", {}).get("label_codes", {})
    if code not in label_codes:
        return {
            "ok": False,
            "error": f"unknown label code {code!r}; known: {', '.join(sorted(label_codes))}",
        }
    text = read_tracker()
    item_id = f"{code}-{_next_number(code, parse_tracker(text)):03d}"
    now = _now()
    block = _render_block(
        {
            "id": item_id,
            "title": title,
            "fields": {
                "Status": "`recorded`",
                "Issue": f"`{EMPTY}`",
                "Recorded": now,
                "Implemented": f"`{EMPTY}`",
                "Problem": problem,
                "Possible Fix": possible_fix,
                "Actual Fix": f"`{EMPTY}`",
                "Rejection Reason": f"`{EMPTY}`",
                "Actual Implemented": f"`{EMPTY}`",
                "Changes": f"`{EMPTY}`",
            },
        }
    )
    write_tracker(text.rstrip("\n") + "\n\n" + block + "\n")
    return {
        "ok": True,
        "item_id": item_id,
        "recorded": now,
        "message": f"recorded {item_id}",
    }


@mcp.tool()
def verify_finding(item_id: str, actual_fix: str) -> dict:
    """Verify a recorded item: set Status=verified and fill Actual Fix."""
    try:
        text = read_tracker()
        text = _replace_item_field(text, item_id, "Status", "`verified`")
        text = _replace_item_field(text, item_id, "Actual Fix", actual_fix)
        write_tracker(text)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": f"tracker write failed: {exc}"}
    return {"ok": True, "message": f"{item_id} verified"}


@mcp.tool()
def reject_finding(item_id: str, rejection_reason: str) -> dict:
    """Reject a verified item: set Status=rejected and fill Rejection Reason."""
    try:
        text = read_tracker()
        text = _replace_item_field(text, item_id, "Status", "`rejected`")
        text = _replace_item_field(text, item_id, "Rejection Reason", rejection_reason)
        write_tracker(text)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": f"tracker write failed: {exc}"}
    return {"ok": True, "message": f"{item_id} rejected"}


@mcp.tool()
def sync_tracker() -> dict:
    """Validate docs/IMPROVEMENTS.md and reorder items to canonical form."""
    try:
        spec = _spec()
    except SpecError as exc:
        return {"ok": False, "error": str(exc)}
    try:
        text = read_tracker()
    except OSError as exc:
        return {"ok": False, "error": f"tracker read failed: {exc}"}
    result = validate_tracker(spec, text)
    issues = result["format"] + result["numbering"] + result["gate_rules"]
    items = parse_tracker(text)
    try:
        order = list((spec["fields"]["id"]["label_codes"] or {}).keys())
    except (KeyError, TypeError):
        order = []
    by_index = {code: i for i, code in enumerate(order)}

    def sort_key(item):
        if item["id"] is None:
            return (len(order), 0)
        code, num = (
            item["id"][: item["id"].rfind("-")],
            int(item["id"].rsplit("-", 1)[1]),
        )
        return (by_index.get(code, len(order)), num)

    ordered = sorted(items, key=sort_key)
    unchanged = all(a is b for a, b in zip(ordered, items))
    if not unchanged:
        lines = text.splitlines()
        items_idx = next(
            (i for i, ln in enumerate(lines) if ln == "## Items"), len(lines)
        )
        preamble = "\n".join(lines[: items_idx + 1])
        body = "\n\n".join(_render_block(it) for it in ordered)
        write_tracker(preamble + "\n\n" + body + "\n")
    return {
        "ok": True,
        "reordered": not unchanged,
        "validation": result,
        "issues": issues,
    }


@mcp.tool()
def archive_finding() -> dict:
    """Archive the tracker when all items are finished; refuse otherwise.

    Copies docs/IMPROVEMENTS.md to docs/archived/IMPROVEMENT_<timestamp>.md and
    recreates an empty tracker (Items reset), mirroring the Archive interaction.
    """
    items = parse_tracker(read_tracker())
    if not items:
        return {"ok": False, "error": "tracker has no items to archive"}
    unfinished = [
        it["id"]
        for it in items
        if it["fields"].get("Status", "").strip("`") in ("recorded", "verified")
    ]
    if unfinished:
        return {
            "ok": False,
            "error": "not ready: unfinished items exist, nothing archived",
            "unfinished": unfinished,
        }
    try:
        archived_dir = TRACKER.parent / "archived"
        archived_dir.mkdir(parents=True, exist_ok=True)
        target = (
            archived_dir
            / f"IMPROVEMENT_{datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d-%H-%M')}.md"
        )
        target.write_text(read_tracker(), encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": f"archive write failed: {exc}"}
    # Recreate an empty tracker, keeping the preamble (header, template, label table).
    lines = read_tracker().splitlines()
    items_idx = next((i for i, ln in enumerate(lines) if ln == "## Items"), len(lines))
    write_tracker("\n".join(lines[: items_idx + 1]) + "\n\n")
    return {
        "ok": True,
        "archived_to": str(target),
        "message": "tracker archived and reset",
    }


@mcp.tool()
def deliver_finding(item_id: str, actual_implemented: str, changes: str) -> dict:
    """Deliver a finished item: set Status=implemented and fill implementation details."""
    try:
        text = read_tracker()
        text = _replace_item_field(text, item_id, "Status", "`implemented`")
        text = _replace_item_field(text, item_id, "Implemented", _now())
        text = _replace_item_field(
            text, item_id, "Actual Implemented", actual_implemented
        )
        text = _replace_item_field(text, item_id, "Changes", changes)
        write_tracker(text)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": f"tracker write failed: {exc}"}
    return {"ok": True, "message": f"{item_id} implemented"}


@mcp.tool()
def validate_doc(path: str) -> dict:
    """Validate a document against the writing-quality policy.

    Checks a committed doc for BOM, CRLF and trailing whitespace (errors) plus
    non-Latin script, hardwrapped sentences and Indonesian text (warnings).
    """
    try:
        return validate_doc_file(path)
    except OSError as exc:
        return {
            "ok": False,
            "path": path,
            "findings": [
                {
                    "severity": "error",
                    "code": "io",
                    "message": f"read failed: {exc}",
                }
            ],
        }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
