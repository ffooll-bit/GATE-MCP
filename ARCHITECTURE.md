# Architecture

## Pattern Overview

**Overall:** Minimal MCP stdio server with YAML-driven workflow enforcement

**Key Characteristics:**
- Single runtime dependency (`mcp` SDK) + `pyyaml`
- Spec-driven: workflow and policy rules loaded from YAML files in `specs/`
- Vertical-slice delivery: `findings-and-planning` workflow + `IMPROVEMENTS.md` validator (complete)
- No markdown parsing at runtime — machine-oriented YAML specs mirror GAIN-Coding document structure

## Layers

**MCP Transport Layer:**
- Purpose: Handle stdio communication per MCP protocol
- Location: `src/gate_mcp/server.py`
- Contains: `FastMCP` instance, `main()` entry point
- Depends on: `mcp.server.fastmcp.FastMCP`
- Used by: CLI entry point (`gate-mcp` script)

**Workflow Enforcement Layer:**
- Purpose: Execute GAIN-Coding workflow gates as MCP tools
- Location: `src/gate_mcp/server.py` (tools registered on `mcp` instance)
- Contains: `record_finding`, `verify_finding`, `reject_finding`, `sync_issue`, `create_issue`, `create_pr`, `merge_pr`, `sync_tracker`, `archive_finding`, `deliver_finding`
- Depends on: Spec Loader, Tracker Validator, Policy Validator
- Used by: MCP clients (agents)

**Policy Validation Layer:**
- Purpose: Enforce writing-quality policy on committed documents (issues, PRs, arbitrary files)
- Location: `src/gate_mcp/policy_validator.py`
- Contains: `validate_doc(path, policy_name?)` — BOM, CRLF, trailing whitespace (errors); hardwrap, Indonesian detection (warnings)
- Depends on: Spec Loader (loads `specs/policies/writing-quality.yaml`)
- Used by: Workflow Enforcement Layer (`create_issue`, `create_pr`, `validate_doc` tools)

**Spec Loader:**
- Purpose: Load and validate YAML workflow/policy specs from `specs/`
- Location: `src/gate_mcp/spec_loader.py`
- Contains: `load_workflow_spec(name)`, `load_policy_spec(name)`, schema validation; cached via `functools.cache`; `GATE_MCP_REPO` env override for repo root
- Depends on: `pyyaml`
- Used by: Workflow Enforcement Layer, Policy Validation Layer

**Tracker Validator:**
- Purpose: Validate `docs/IMPROVEMENTS.md` format, numbering, and gate rules
- Location: `src/gate_mcp/tracker_validator.py`
- Contains: `parse_tracker()`, `validate_format()`, `validate_numbering()`, `validate_gate_rules()`, `validate_tracker()`, `read_tracker()`, `write_tracker()`, `_next_number()`; `GATE_MCP_REPO` env override for tracker path
- Depends on: Spec Loader (for gate definitions)
- Used by: Workflow Enforcement Layer (verify/sync/archive/deliver gates)

## Data Flow

**Findings-and-Planning Cycle:**

1. Agent calls `record_finding` tool — `src/gate_mcp/server.py`
2. Tool validates input against workflow spec — `src/gate_mcp/spec_loader.py`
3. Tool appends entry to `docs/IMPROVEMENTS.md` — `src/gate_mcp/tracker_validator.py`
4. Agent calls `verify_finding` tool — `src/gate_mcp/server.py`
5. Tool updates Status to `verified` and fills Actual Fix — `src/gate_mcp/tracker_validator.py`
6. Agent calls `reject_finding` tool (optional) — `src/gate_mcp/server.py`
7. Tool updates Status to `rejected` and fills Rejection Reason — `src/gate_mcp/tracker_validator.py`
8. Agent calls `sync_issue` tool (optional) — `src/gate_mcp/server.py`
9. Tool updates Issue field with GitHub issue reference (e.g., `#28`) — `src/gate_mcp/tracker_validator.py`
10. Agent calls `sync_tracker` tool — `src/gate_mcp/server.py`
11. Tool validates format/numbering/gates and reorders items to canonical form — `src/gate_mcp/tracker_validator.py`
12. Agent calls `archive_finding` tool — `src/gate_mcp/server.py`
13. Tool copies tracker to `docs/archived/` and recreates empty tracker — `src/gate_mcp/tracker_validator.py`
14. Agent calls `deliver_finding` tool — `src/gate_mcp/server.py`
15. Tool sets Status to `implemented` and fills implementation details — `src/gate_mcp/tracker_validator.py`

**Issue & PR Creation Flow:**

1. Agent calls `create_issue` tool with verified item ID — `src/gate_mcp/server.py`
2. Tool builds issue body from tracker fields, writes to temp file — `src/gate_mcp/server.py`
3. Tool validates body via `validate_doc` — `src/gate_mcp/policy_validator.py`
4. If valid, creates issue via `gh issue create` — `src/gate_mcp/server.py`
5. Agent calls `sync_issue` to link issue number back to tracker — `src/gate_mcp/server.py`

1. Agent calls `create_pr` tool with branch, title, body — `src/gate_mcp/server.py`
2. Tool validates body via `validate_doc` — `src/gate_mcp/policy_validator.py`
3. If valid, creates PR via `gh pr create` — `src/gate_mcp/server.py`
4. Agent calls `merge_pr` tool with PR number and method — `src/gate_mcp/server.py`
5. Tool merges via `gh pr merge --admin` — `src/gate_mcp/server.py`

**Doc Validation Flow:**

1. Agent calls `validate_doc` tool with file path — `src/gate_mcp/server.py`
2. Tool delegates to `validate_doc` — `src/gate_mcp/policy_validator.py`
3. Policy spec loaded from `specs/policies/writing-quality.yaml` — `src/gate_mcp/spec_loader.py`
4. Returns findings with severity (error/warning) — `src/gate_mcp/policy_validator.py`

**Spec Loading:**

1. Server startup — `src/gate_mcp/server.py`
2. Load `specs/workflows/findings-and-planning.yaml` on first tool call — `src/gate_mcp/spec_loader.py`
3. Load `specs/policies/writing-quality.yaml` on first policy check — `src/gate_mcp/spec_loader.py`
4. Cache parsed specs in memory via `functools.cache` for subsequent invocations — `src/gate_mcp/spec_loader.py`
5. Repo root resolved via `GATE_MCP_REPO` env or relative to `spec_loader.py` — `src/gate_mcp/spec_loader.py`

## Key Abstractions

**WorkflowSpec:**
- Purpose: Machine-readable representation of a GAIN-Coding workflow (interactions, fields, gates)
- Location: `src/gate_mcp/spec_loader.py` (returned as `dict` from `load_workflow_spec`)
- Pattern: Immutable data container loaded from YAML; validated for required keys (`workflow`, `interactions`, `fields`, `gates`)

**PolicySpec:**
- Purpose: Machine-readable representation of a GAIN-Coding policy (rules, constraints)
- Location: `src/gate_mcp/spec_loader.py` (returned as `dict` from `load_policy_spec`); currently `specs/policies/writing-quality.yaml`
- Pattern: Immutable data container loaded from YAML; declarative rules (bom, line_ending, trailing_whitespace, hardwrap, language) with severity levels

**TrackerEntry:**
- Purpose: Single item in `docs/IMPROVEMENTS.md` (ENH-001, BUG-002, etc.)
- Location: `src/gate_mcp/tracker_validator.py` (as `dict` from `parse_tracker`)
- Pattern: Parsed representation with typed fields (ID, title, fields dict with Status, Issue, Recorded, Implemented, Problem, Possible Fix, Actual Fix, Rejection Reason, Actual Implemented, Changes)

**GateRule:**
- Purpose: Validation rule for a specific workflow gate (e.g., "verify requires Status=verified")
- Location: `src/gate_mcp/spec_loader.py` (inside WorkflowSpec `gates` and `fields.status.values`)
- Pattern: Declarative rule evaluated by Tracker Validator via `validate_gate_rules()`

**PolicyRule:**
- Purpose: Validation rule for document writing quality (BOM, line endings, whitespace, hardwrap, language)
- Location: `specs/policies/writing-quality.yaml` (loaded via `load_policy_spec`)
- Pattern: Declarative rule with `severity` (error/warning); deterministic rules are errors, heuristic rules are warnings; evaluated by Policy Validator via `validate_doc()`

## Entry Points

**CLI Entry Point:**
- Location: `src/gate_mcp/server.py:main()`
- Triggers: `python -m gate_mcp` or installed `gate-mcp` script
- Responsibilities: Instantiate FastMCP, register tools, run stdio server

**MCP Tool Endpoints:**
- `record_finding(title, problem, possible_fix, label_code?)` — Create new tracker entry with Status=`recorded`
- `verify_finding(item_id, actual_fix)` — Set Status=`verified` and fill Actual Fix
- `reject_finding(item_id, rejection_reason)` — Set Status=`rejected` and fill Rejection Reason
- `sync_issue(item_id, issue)` — Set Issue field to GitHub issue reference (e.g., `#28`)
- `create_issue(item_id)` — Build issue body from verified tracker item, validate via writing-quality policy, create via `gh issue create`
- `create_pr(branch, title, body, base?)` — Validate PR body via writing-quality policy, create via `gh pr create`
- `merge_pr(number, method?)` — Merge PR via `gh pr merge --admin` (method: squash|rebase|merge)
- `sync_tracker()` — Validate format/numbering/gate rules; reorder items to canonical form
- `archive_finding()` — Copy tracker to `docs/archived/IMPROVEMENT_<timestamp>.md` and reset (requires all items finished)
- `deliver_finding(item_id, actual_implemented, changes)` — Set Status=`implemented` and fill implementation details
- `validate_doc(path)` — Validate a document against the writing-quality policy; returns findings with severity

## Error Handling

**Strategy:** Fail closed with structured MCP errors

- Spec loading errors: `SpecError` caught and returned as MCP error — server cannot operate without valid specs
- Tracker validation errors: Return structured error to agent via MCP (invalid format, missing fields, gate violation)
- I/O errors (file read/write): Caught as `OSError`, wrapped and returned as MCP error with context
- Item/field not found: Caught as `ValueError`, returned as MCP error
- Schema validation errors: Detailed field-level messages for agent self-correction

## Cross-Cutting Concerns

**Logging:** Stdlib `logging` module; structured JSON output for machine parsing; level configurable via env var

**Caching:** In-memory spec cache via `functools.cache` on `load_workflow_spec`/`load_policy_spec`; lazy-loaded on first tool call; no runtime reloading (specs are static per deployment)

**Storage:** Local filesystem only — `docs/IMPROVEMENTS.md` as source of truth; `specs/` as immutable rule source; `docs/archived/` for archive copies; no database

**Configuration:** `GATE_MCP_REPO` env var overrides repo root for spec and tracker paths (used by `spec_loader.py` and `tracker_validator.py`); enables standalone operation outside the repo checkout

**External Commands:** `gh` CLI required for `create_issue`, `create_pr`, `merge_pr`; subprocess calls with captured output; errors surfaced as MCP error responses