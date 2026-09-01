"""Tests for the docs/IMPROVEMENTS.md tracker validator."""

from gate_mcp import spec_loader
from gate_mcp import tracker_validator as tv

EMPTY = "\u2014"


def _spec():
    return spec_loader.load_workflow_spec("findings-and-planning")


def _item(ident, status, extra=None):
    fields = {
        "Status": f"`{status}`",
        "Issue": f"`{EMPTY}`",
        "Recorded": "2026-08-30 02:37",
        "Implemented": f"`{EMPTY}`",
        "Problem": "A problem.",
        "Possible Fix": "A fix.",
        "Actual Fix": f"`{EMPTY}`",
        "Rejection Reason": f"`{EMPTY}`",
        "Actual Implemented": f"`{EMPTY}`",
        "Changes": f"`{EMPTY}`",
    }
    if extra:
        fields.update(extra)
    lines = [f"### {ident} \u2014 Some title"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    return "\n".join(lines)


def _tracker(*blocks):
    return "## Items\n\n" + "\n\n".join(blocks) + "\n"


def test_parse_fields():
    items = tv.parse_tracker(_tracker(_item("ENH-001", "recorded")))
    assert len(items) == 1
    it = items[0]
    assert it["id"] == "ENH-001"
    assert it["title"] == "Some title"
    assert it["fields"]["Status"].strip("`") == "recorded"


def test_format_missing_field():
    text = "## Items\n\n### BAD-TITLE\n- **Status:** `recorded`\n"
    assert tv.validate_format(tv.parse_tracker(text))


def test_format_ok():
    text = _tracker(_item("ENH-001", "recorded"))
    assert tv.validate_format(tv.parse_tracker(text)) == []


def test_numbering_gap():
    text = _tracker(_item("ENH-001", "recorded"), _item("ENH-003", "recorded"))
    errs = tv.validate_numbering(tv.parse_tracker(text))
    assert any("gap" in err for err in errs)


def test_numbering_duplicate():
    text = _tracker(_item("ENH-001", "recorded"), _item("ENH-001", "recorded"))
    errs = tv.validate_numbering(tv.parse_tracker(text))
    assert any("duplicate" in err for err in errs)


def test_numbering_ok():
    text = _tracker(_item("ENH-001", "recorded"), _item("ENH-002", "recorded"))
    assert tv.validate_numbering(tv.parse_tracker(text)) == []


def test_invalid_status():
    text = _tracker(_item("ENH-001", "bogus"))
    errs = tv.validate_gate_rules(_spec(), tv.parse_tracker(text))
    assert any("invalid Status" in err for err in errs)


def test_status_requires_filled():
    text = _tracker(_item("ENH-001", "implemented"))
    errs = tv.validate_gate_rules(_spec(), tv.parse_tracker(text))
    assert any("requires filled 'Implemented'" in err for err in errs)


def test_status_ok():
    text = _tracker(
        _item(
            "ENH-001",
            "implemented",
            {
                "Implemented": "2026-09-01 09:00",
                "Actual Implemented": "did things",
                "Changes": "behaviour changed",
            },
        )
    )
    assert tv.validate_gate_rules(_spec(), tv.parse_tracker(text)) == []
