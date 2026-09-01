# IMPROVEMENTS

_The tracker for feature ideas, found bugs, and optimization plans. Each finding is recorded as an item under Items: copy the template below, fill it in, and place the item at the very bottom of the Items section._

## Item Template

```markdown
### <ID> — <Title>
- **Status:** `verified` | `verified` | `rejected` | `implemented`
- **Issue:** <#NN> | `—`
- **Recorded:** YYYY-MM-DD HH:MM
- **Implemented:** YYYY-MM-DD HH:MM | `—`
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

### ENH-001 — Repository structure not verified against the standard
- **Status:** `verified`
- **Issue:** #4
- **Recorded:** YYYY-MM-DD HH:MM
- **Implemented:** `—`
- **Problem:** The repository is newly created and its folders, guardrail files, and settings have not yet been confirmed against the workflow standard.
- **Possible Fix:** Run the verification checks from the workflow before the first commit.
- **Actual Fix:** `Verified — repository structure was built per the GAIN-Coding workflow standard during bootstrap; the original concern (unverified structure) is resolved. Not marked implemented (status→implemented happens via the Code Implementation workflow).`
- **Rejection Reason:** `—`
- **Actual Implemented:** `—`
- **Changes:** `—`

### ENH-002 — Implement findings-and-planning vertical slice (core enforcement)
- **Status:** `implemented`
- **Issue:** #5
- **Recorded:** 2026-08-30 02:37
- **Implemented:** 2026-09-01 09:34
- **Problem:** `server.py` is still a skeleton (`FastMCP` + `mcp.run()`) with no tools or gate logic, so GATE-MCP cannot enforce any GAIN-Coding workflow and is not yet usable.
- **Possible Fix:** Add MCP tools in `server.py` that run the findings-and-planning cycle (record/verify/sync/archive/deliver) plus a `docs/IMPROVEMENTS.md` tracker validator (format + gate rules), loading rules from `specs/`.
- **Actual Fix:** `Verified — server.py confirmed skeleton (FastMCP + mcp.run()), no gate logic; the proposed fix (MCP tools + IMPROVEMENTS.md validator) is the correct approach.`
- **Rejection Reason:** `—`
- **Actual Implemented:** Added `src/gate_mcp/spec_loader.py` (loads/caches workflow specs from `specs/`), `src/gate_mcp/tracker_validator.py` (parses `docs/IMPROVEMENTS.md` and validates format, numbering, gate rules against the spec), and 5 MCP tools in `src/gate_mcp/server.py` (`record_finding`, `verify_finding`, `sync_tracker`, `archive_finding`, `deliver_finding`) that run the findings-and-planning cycle against the tracker. Pinned `mcp>=1.0,<2` and added `pyyaml` to `pyproject.toml`.
- **Changes:** GATE-MCP can now enforce the findings-and-planning workflow as MCP tools operating on `docs/IMPROVEMENTS.md`, with rules loaded from `specs/workflows/findings-and-planning.yaml`.

### DOC-001 — Create machine-oriented YAML spec `specs/workflows/findings-and-planning.yaml`
- **Status:** `implemented`
- **Issue:** #6
- **Recorded:** 2026-08-30 02:37
- **Implemented:** 2026-08-31 21:55
- **Problem:** `specs/` is empty (only `.gitkeep`); the server has no rule source to enforce, although the README states it loads one YAML spec per workflow/policy.
- **Possible Fix:** Write a YAML spec that mirrors the GAIN-Coding `findings-and-planning.md` structure (interactions, fields, gates) as the server's input. Dependency of ENH-002.
- **Actual Fix:** `Verified — specs/ confirmed empty; the proposed fix (YAML spec mirroring findings-and-planning.md) is the correct approach.`
- **Rejection Reason:** `—`
- **Actual Implemented:** Created `specs/workflows/findings-and-planning.yaml` mirroring the GAIN-Coding `findings-and-planning.md` workflow structure (5 interactions, field definitions, gate rules, merge strategy). Removed `specs/workflows/.gitkeep`.
- **Changes:** Server can now load machine-readable workflow rules from `specs/workflows/findings-and-planning.yaml` (data file only; loading logic belongs to ENH-002).

### ENH-003 — Add tests for validator and spec loader
- **Status:** `implemented`
- **Issue:** #7
- **Recorded:** 2026-08-30 02:37
- **Implemented:** 2026-09-01 10:05
- **Problem:** `tests/` is empty; there is no automated verification that enforcement and the tracker stay valid.
- **Possible Fix:** Add pytest coverage for the spec loader and the `IMPROVEMENTS.md` validator (format, numbering, gate rules).
- **Actual Fix:** `Verified — tests/ confirmed empty; the proposed fix (pytest for validator + spec loader) is the correct approach.`
- **Rejection Reason:** `—`
- **Actual Implemented:** Added `tests/test_spec_loader.py` (loads the real findings-and-planning spec; `SpecError` for missing spec, name mismatch, and missing required keys) and `tests/test_tracker_validator.py` (parse, format, numbering gap/duplicate, and gate-rule validation). Separated the `spec_loader`/`tracker_validator_as_tv` imports to satisfy ruff. Removed `tests/.gitkeep`. 14 pytest cases pass.
- **Changes:** The tracker validator and spec loader now have automated regression coverage that runs with `pytest`; `tests/` is no longer empty.