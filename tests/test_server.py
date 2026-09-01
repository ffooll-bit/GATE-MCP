"""Protocol-level tests for the five MCP tools in gate_mcp.server.

These exercise the real MCP protocol through an in-memory client session,
against an isolated temp tracker so the production docs/IMPROVEMENTS.md is
never modified.
"""

from __future__ import annotations

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from gate_mcp import server

PREAMBLE = """\
# IMPROVEMENTS

_The tracker for feature ideas, found bugs, and optimization plans. Each finding is recorded as an item under Items: copy the template below, fill it in, and place the item at the very bottom of the Items section._

## Item Template

```markdown
### <ID> \u2014 <Title>
- **Status:** `recorded` | `verified` | `rejected` | `implemented`
- **Issue:** <#NN> | `\u2014`
- **Recorded:** YYYY-MM-DD HH:MM
- **Implemented:** YYYY-MM-DD HH:MM | `\u2014`
- **Problem:** ...
- **Possible Fix:** ...
- **Actual Fix:** ...
- **Rejection Reason:** ...
- **Actual Implemented:** ...
- **Changes:** ...
```

Item IDs follow the format `<LABEL_CODE>-<NNN>` built from the default GitHub labels, with numbers counted per label code:

| GitHub Label | Code |
|--------------|------|
| `bug` | BUG |
| `documentation` | DOC |
| `enhancement` | ENH |
| `duplicate` | DUP |
| `good first issue` | GFI |
| `help wanted` | HW |
| `invalid` | INV |
| `question` | QST |
| `wontfix` | WFX |

## Items
"""


@pytest.fixture
def tracker(monkeypatch, tmp_path):
    """Point the server's tracker I/O at an isolated temp file."""
    path = tmp_path / "IMPROVEMENTS.md"
    path.write_text(PREAMBLE + "\n", encoding="utf-8")
    monkeypatch.setattr(
        server, "read_tracker", lambda: path.read_text(encoding="utf-8")
    )
    monkeypatch.setattr(
        server, "write_tracker", lambda text: path.write_text(text, encoding="utf-8")
    )
    monkeypatch.setattr(server, "TRACKER", path)
    return path


async def _session():
    return create_connected_server_and_client_session(server.mcp)


def _read(tracker):
    return tracker.read_text(encoding="utf-8")


async def test_record_finding(tracker):
    async with await _session() as session:
        await session.initialize()
        res = await session.call_tool(
            "record_finding", {"title": "A test", "problem": "P", "possible_fix": "F"}
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    assert payload["item_id"] == "ENH-001"
    assert "### ENH-001" in _read(tracker)
    assert "`recorded`" in _read(tracker)


async def test_record_uses_next_number(tracker):
    async with await _session() as session:
        await session.initialize()
        for i in range(2):
            await session.call_tool(
                "record_finding",
                {"title": f"T{i}", "problem": "P", "possible_fix": "F"},
            )
        await session.call_tool(
            "record_finding", {"title": "T2", "problem": "P", "possible_fix": "F"}
        )
    assert "### ENH-003" in _read(tracker)


async def test_record_unknown_label(tracker):
    async with await _session() as session:
        await session.initialize()
        res = await session.call_tool(
            "record_finding",
            {"title": "T", "problem": "P", "possible_fix": "F", "label_code": "XYZ"},
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is False
    assert "unknown label code" in payload["error"]


async def test_verify_finding(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        res = await session.call_tool(
            "verify_finding", {"item_id": "ENH-001", "actual_fix": "fixed"}
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    assert "`verified`" in _read(tracker)
    assert "- **Actual Fix:** fixed" in _read(tracker)


async def test_verify_missing_item(tracker):
    async with await _session() as session:
        await session.initialize()
        res = await session.call_tool(
            "verify_finding", {"item_id": "ENH-999", "actual_fix": "x"}
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is False
    assert "item not found" in payload["error"]


async def test_reject_finding(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        res = await session.call_tool(
            "reject_finding", {"item_id": "ENH-001", "rejection_reason": "not viable"}
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    text = _read(tracker)
    assert "`rejected`" in text
    assert "- **Rejection Reason:** not viable" in text


async def test_reject_missing_item(tracker):
    async with await _session() as session:
        await session.initialize()
        res = await session.call_tool(
            "reject_finding", {"item_id": "ENH-999", "rejection_reason": "x"}
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is False
    assert "item not found" in payload["error"]


async def test_deliver_finding(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        res = await session.call_tool(
            "deliver_finding",
            {"item_id": "ENH-001", "actual_implemented": "did it", "changes": "yes"},
        )
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    assert "`implemented`" in _read(tracker)
    assert "- **Actual Implemented:** did it" in _read(tracker)
    assert "- **Changes:** yes" in _read(tracker)


async def test_sync_tracker_clean(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        res = await session.call_tool("sync_tracker", {})
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    assert payload["reordered"] is False
    assert payload["issues"] == []


async def test_archive_refuses_when_unfinished(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        res = await session.call_tool("archive_finding", {})
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is False
    assert "not ready" in payload["error"]
    assert payload["unfinished"] == ["ENH-001"]


async def test_archive_succeeds_when_finished(tracker):
    async with await _session() as session:
        await session.initialize()
        await session.call_tool(
            "record_finding", {"title": "T", "problem": "P", "possible_fix": "F"}
        )
        await session.call_tool(
            "deliver_finding",
            {"item_id": "ENH-001", "actual_implemented": "did it", "changes": "yes"},
        )
        res = await session.call_tool("archive_finding", {})
    import json

    payload = json.loads(res.content[0].text)
    assert payload["ok"] is True
    assert payload["archived_to"].endswith(".md")
    assert "### ENH-" not in _read(tracker)
