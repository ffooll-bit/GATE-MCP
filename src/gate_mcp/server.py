"""GATE-MCP stdio server: findings-and-planning enforcement tools.

GATE = Guided Agent Through Enforcement. The full expansion is
"Guided Agent Through Enforcement MCP" (MCP stays unexpanded).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

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


def _gh(app: str, args: list[str]) -> subprocess.CompletedProcess:
    """Run a gh subcommand capturing output; errors surface as returncode."""
    return subprocess.run(
        ["gh", app, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


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
def sync_issue(item_id: str, issue: str) -> dict:
    """Sync the GitHub Issue number on a tracked item.

    Updates the Issue field of the item (e.g. '#28') so the agent never edits
    the tracker by hand when linking issues.
    """
    import re as _re

    if not _re.fullmatch(r"#\d+", issue):
        return {"ok": False, "error": f"invalid issue reference: {issue!r}"}
    try:
        text = read_tracker()
        text = _replace_item_field(text, item_id, "Issue", issue)
        write_tracker(text)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": f"tracker write failed: {exc}"}
    return {"ok": True, "message": f"{item_id} Issue set to {issue}"}


@mcp.tool()
def create_issue(item_id: str) -> dict:
    """Create a GitHub Issue for a verified item.

    Builds the issue body from the tracker item, validates it against the
    writing-quality policy, then creates the issue with gh. No issue is created
    when the body fails validation.
    """
    try:
        spec = _spec()
    except SpecError as exc:
        return {"ok": False, "error": str(exc)}
    try:
        items = parse_tracker(read_tracker())
    except OSError as exc:
        return {"ok": False, "error": f"tracker read failed: {exc}"}
    item = next((it for it in items if it["id"] == item_id), None)
    if item is None:
        return {"ok": False, "error": f"item not found: {item_id}"}
    fields = item["fields"]
    status = fields.get("Status", "").strip("`")
    if status != "verified":
        return {
            "ok": False,
            "error": f"create_issue requires a verified item, {item_id} is {status!r}",
        }
    label_codes = (spec.get("fields") or {}).get("id", {}).get("label_codes", {})
    code = item_id[: item_id.rfind("-")]
    label = label_codes.get(code)
    if not label:
        return {"ok": False, "error": f"no GitHub label for code {code!r}"}
    body = (
        f"## Summary\n\n{fields.get('Problem', '')}\n\n"
        f"## Suggested fix\n\n{fields.get('Possible Fix', '')}\n"
    )
    fd, raw_path = tempfile.mkstemp(suffix=".md", prefix="gate-mcp-issue-")
    os.close(fd)
    tmp = Path(raw_path)
    try:
        tmp.write_text(body, encoding="utf-8", newline="\n")
        result = validate_doc_file(str(tmp))
        errors = [f for f in result["findings"] if f["severity"] == "error"]
        if errors:
            return {
                "ok": False,
                "error": "issue body failed writing-quality validation",
                "findings": errors,
            }
        proc = _gh(
            "issue",
            [
                "create",
                "--title",
                item["title"],
                "--label",
                label,
                "--body-file",
                str(tmp),
            ],
        )
        if proc.returncode != 0:
            return {"ok": False, "error": f"gh failed: {proc.stderr.strip()}"}
        created = json.loads(proc.stdout) if proc.stdout.strip() else {}
        return {
            "ok": True,
            "issue": created.get("url"),
            "number": created.get("number"),
            "message": f"created issue {created.get('number')} for {item_id}",
        }
    except json.JSONDecodeError:
        return {"ok": False, "error": "gh returned non-JSON output"}
    except OSError as exc:
        return {"ok": False, "error": f"issue write failed: {exc}"}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


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
