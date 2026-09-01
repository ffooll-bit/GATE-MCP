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
- **Status:** `implemented`
- **Issue:** #4
- **Recorded:** YYYY-MM-DD HH:MM
- **Implemented:** 2026-09-01 10:15
- **Problem:** The repository is newly created and its folders, guardrail files, and settings have not yet been confirmed against the workflow standard.
- **Possible Fix:** Run the verification checks from the workflow before the first commit.
- **Actual Fix:** `Verified — repository structure was built per the GAIN-Coding workflow standard during bootstrap; the original concern (unverified structure) is resolved. Not marked implemented (status 'implemented' happens via the Code Implementation workflow).`
- **Rejection Reason:** `—`
- **Actual Implemented:** Confirmed the repository structure matches the GAIN-Coding standard: all six root docs (README, CHANGELOG, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY), guardrail files (.gitignore, .editorconfig, .gitattributes), the full .github/ layout (ci.yml, 3 issue templates, PR and release templates, dependabot), specs/, src/gate_mcp/ package, and tests/. Branch protection on main is active in the public repository.
- **Changes:** No code or behaviour change; ENH-001 is resolved as a structure-verification finding with its status recorded as implemented for traceability.

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

### ENH-004 — CI does not run the Python checks (ruff and pytest)
- **Status:** `implemented`
- **Issue:** #13
- **Recorded:** 2026-09-01 10:00
- **Implemented:** 2026-09-01 10:16
- **Problem:** The CI workflow (`.github/workflows/ci.yml`) only checks CRLF/BOM on `*.md` files; it does not run `ruff` or `pytest`. The findings-and-planning enforcement tools and their test suite are therefore only verified locally, so a Python regression would not turn CI red and the claim that the workflow "can be used without problems" has no automated safety net.
- **Possible Fix:** Add a Python job to `.github/workflows/ci.yml` that installs the project (`pip install -e .[dev]` or equivalent) and runs `ruff check`, `ruff format --check`, and `pytest` on a Python 3.10+ runner, so the findings-and-planning enforcement stays green in CI.
- **Actual Fix:** Verified — `ci.yml` reviewed; its single `build` job checks only CRLF/BOM on `*.md` with no Python setup, `ruff`, or `pytest` steps. GitHub Actions and Ruff official docs confirm the standard pattern (`actions/setup-python` + `pip install`, then `ruff check --output-format=github`, `ruff format --check`, `pytest`). Fix: add a Python step to `ci.yml` using `setup-python` (3.10+) that installs the project and runs `ruff check`, `ruff format --check`, and `pytest`.
- **Rejection Reason:** `—`
- **Actual Implemented:** Added a `test` job to `.github/workflows/ci.yml` that runs on `ubuntu-latest` with `actions/setup-python@v5` (Python 3.12), installs the project and tooling (`pip install -e . ruff pytest`), then runs `ruff check . --output-format=github`, `ruff format --check .`, and `pytest`. The existing `build` job (CRLF/BOM check) is unchanged. The existing code already passes all three checks locally, so the new job goes green without code changes.
- **Changes:** CI now runs `ruff check`, `ruff format --check`, and `pytest` on every push to `main` and pull request against `main`, in addition to the existing CRLF/BOM check, so Python regressions now turn CI red.

### ENH-005 — Decide whether untracked files are tracked or ignored
- **Status:** `implemented`
- **Issue:** #14
- **Recorded:** 2026-09-01 10:00
- **Implemented:** 2026-09-01 10:13
- **Problem:** Four untracked items pollute `git status`: `.cortexkit/` and `.playwright-mcp/` are machine-local tooling artifacts that should not be committed to the public repo, while `ARCHITECTURE.md` and `STRUCTURE.md` are project design documents that are currently untracked and, if in the repo, must reflect the implemented code rather than the "planned" state.
- **Possible Fix:** Add `.cortexkit/` and `.playwright-mcp/` to `.gitignore`; track `ARCHITECTURE.md` and `STRUCTURE.md` and update their "planned / to be created" references (spec_loader, tracker_validator, five MCP tools, tests) to the implemented state.
- **Actual Fix:** Verified — `.gitignore` reviewed; it lacks `.cortexkit/`, `.playwright-mcp/`, `ARCHITECTURE.md`, and `STRUCTURE.md`, and `git status` shows all four as untracked. Tooling artifacts should be ignored; `ARCHITECTURE.md` and `STRUCTURE.md` are project design docs worth tracking once updated to reflect the implemented code. Fix: add the two tooling dirs to `.gitignore` and commit updated `ARCHITECTURE.md`/`STRUCTURE.md`.
- **Rejection Reason:** `—`
- **Actual Implemented:** Added `.cortexkit/` and `.playwright-mcp/` to `.gitignore` so the machine-local tooling artifacts are no longer reported as untracked. Tracked `ARCHITECTURE.md` and `STRUCTURE.md` as project design documents. Both documents already described the implemented state (the spec loader, tracker validator, five MCP tools, and test suite were listed as existing), so no "planned / to be created" references needed to be rewritten; the only refinement was removing `.cortexkit/` and `.playwright-mcp/` from the `STRUCTURE.md` directory tree so it matches their now-ignored tooling status.
- **Changes:** `git status` no longer reports `.cortexkit/`, `.playwright-mcp/`, `ARCHITECTURE.md`, or `STRUCTURE.md` as untracked. The repository now carries its architecture and structure design documents in version control while machine-local tooling stays out of the public repo.

### ENH-006 — Documented `python -m gate_mcp` run command fails (no __main__.py)
- **Status:** `implemented`
- **Issue:** #18
- **Recorded:** 2026-09-01 10:35
- **Implemented:** 2026-09-01 10:56
- **Problem:** README.md, ARCHITECTURE.md, and STRUCTURE.md all instruct running the server with `python -m gate_mcp`, but the command fails with `No module named gate_mcp.__main__` because the package has no `src/gate_mcp/__main__.py`. The working entry points are the `gate-mcp` console script or `python -c "from gate_mcp.server import main; main()"`. A user following the published README therefore cannot start the server.
- **Possible Fix:** Add `src/gate_mcp/__main__.py` that calls `main()` from server.py so `python -m gate_mcp` works, and align README/ARCHITECTURE/STRUCTURE with the correct entry point. Verify end-to-end.
- **Actual Fix:** Confirmed: `python -m gate_mcp` indeed fails (No module named gate_mcp.__main__) because the package has no `src/gate_mcp/__main__.py`, and Python packaging docs confirm `python -m <pkg>` requires a `__main__.py`. Fix: add `src/gate_mcp/__main__.py` that calls `main()` from server.py so `python -m gate_mcp` works, and align README/ARCHITECTURE/STRUCTURE to document both the `gate-mcp` console script and `python -m gate_mcp` correctly. Verify end-to-end over stdio.
- **Rejection Reason:** `—`
- **Actual Implemented:** Added src/gate_mcp/__main__.py that calls main() from server.py so python -m gate_mcp resolves and starts the server; updated README Usage to document both the gate-mcp console script (primary) and python -m gate_mcp. ARCHITECTURE already listed both entry points and was left unchanged (minimal diff).
- **Changes:** Running python -m gate_mcp now starts the server over stdio (previously it failed with No module named gate_mcp.__main__). The gate-mcp console script still works unchanged. Verified end-to-end: both entry points initialize and expose the 5 tools (record_finding, verify_finding, sync_tracker, archive_finding, deliver_finding).

### ENH-007 — No automated test coverage for the five MCP tools
- **Status:** `implemented`
- **Issue:** #19
- **Recorded:** 2026-09-01 10:35
- **Implemented:** 2026-09-01 11:03
- **Problem:** The 14 unit tests only cover spec_loader and tracker_validator; the five MCP tools (record_finding, verify_finding, sync_tracker, archive_finding, deliver_finding) in server.py have no automated coverage. The end-to-end harness written during stability testing proves they work, but it lives in temp/ (gitignored) and does not run in CI, so a regression in server.py would not turn CI red.
- **Possible Fix:** Add tests/test_server.py that calls the tool functions against a temporary tracker (monkeypatching read_tracker/write_tracker), covering record, verify, sync, archive, deliver and error cases (unknown label, missing item, archive refusal); or fold the end-to-end harness into the suite CI runs.
- **Actual Fix:** Confirmed: `tests/` has only `test_spec_loader.py` and `test_tracker_validator.py`; no test covers the five MCP tools in `server.py` (0 server-tool references). MCP SDK docs endorse testing tools via an in-memory client calling `call_tool`. Fix: add `tests/test_server.py` using the MCP in-memory test client (`create_connected_server_and_client_session`) against a temporary tracker (monkeypatched `read_tracker`/`write_tracker`), covering record, verify, sync, archive, deliver and the error cases; add the required async test dependency to dev extras.
- **Rejection Reason:** `—`
- **Actual Implemented:** Added tests/test_server.py: 9 protocol-level tests covering all five MCP tools (record_finding, verify_finding, sync_tracker, archive_finding, deliver_finding) plus record-next-number, unknown-label, missing-item, and archive-refusal/refusal-met cases, driving the real MCP protocol via create_connected_server_and_client_session against a monkeypatched temp tracker so docs/IMPROVEMENTS.md is never touched. Added [project.optional-dependencies] dev (pytest-asyncio) and changed CI test install to pip install -e .[dev]; configured asyncio_mode=auto in pyproject. Local: 23 pytest pass, ruff clean.
- **Changes:** Added tests/test_server.py; pyproject.toml [dev] extra + pytest asyncio_mode=auto; ci.yml test job install -e .[dev]

### ENH-008 — `build/` directory from pip wheel is not gitignored
- **Status:** `implemented`
- **Issue:** #20
- **Recorded:** 2026-09-01 10:35
- **Implemented:** 2026-09-01 10:50
- **Problem:** Running `pip wheel .` (or a source/wheel build) produces a `build/` directory, but .gitignore only ignores `__pycache__/` and `*.egg-info/`, so the build artifact appears as an untracked entry in git status and risks being committed.
- **Possible Fix:** Add `build/`, `dist/`, and `*.egg-info/` to .gitignore.
- **Actual Fix:** Confirmed: `.gitignore` ignores `__pycache__/`, `*.egg-info/`, `.venv/`, `venv/`, `temp/` but not `build/` or `dist/`, so `pip wheel .` leaves an un-ignored `build/` artifact. Fix: add `build/`, `dist/`, and `*.egg-info/` to `.gitignore`.
- **Rejection Reason:** `—`
- **Actual Implemented:** Added build/ and dist/ to the Python section of .gitignore so packaging build artifacts no longer appear as untracked entries in git status.
- **Changes:** Running pip wheel . (or any source/wheel build) no longer surfaces an untracked build/ directory in git status; dist/ is also ignored for future packaging output.

### ENH-009 — Wheel does not bundle specs/ so a standalone install cannot operate
- **Status:** `recorded`
- **Issue:** `—`
- **Recorded:** 2026-09-01 11:28
- **Implemented:** `—`
- **Problem:** pip wheel produces gate_mcp-0.1.0-py3-none-any.whl that ships only the Python modules; specs/ and docs/ are absent. A standalone pip install gate_mcp boots and registers all 5 tools but every workflow tool fails with "workflows spec not found: specs/workflows/findings-and-planning.yaml"; TRACKER also resolves to a nonexistent site-packages/Lib/docs/IMPROVEMENTS.md.
- **Possible Fix:** Bundle specs/ (and optionally a default docs/) in the wheel via pyproject package-data/data_files so a standalone install locates its spec and tracker; otherwise document "run from a repo checkout" as an explicit limitation.
- **Actual Fix:** `—`
- **Rejection Reason:** `—`
- **Actual Implemented:** `—`
- **Changes:** `—`

### ENH-010 — First MCP stdio tool call can intermittently return an empty content node on Windows
- **Status:** `recorded`
- **Issue:** `—`
- **Recorded:** 2026-09-01 11:30
- **Implemented:** `—`
- **Problem:** On Windows (Python 3.13 + anyio), the first MCP tool call immediately after initialize() over stdio can intermittently return an empty content node, so json.loads on content[0].text fails. The harness needed a 3x retry with a short sleep to obtain valid JSON responses. Not a server logic defect, but flaky transport framing that real MCP clients without retry could observe as an occasional empty first response.
- **Possible Fix:** Add a small retry on the first tool call in non-editable client harnesses, or harden the server so the first stdio tool call never returns an empty content node when the underlying write races; document the workaround for third-party MCP clients.
- **Actual Fix:** `—`
- **Rejection Reason:** `—`
- **Actual Implemented:** `—`
- **Changes:** `—`

### ENH-011 — TRACKER path is hardcoded from __file__ with no environment override
- **Status:** `recorded`
- **Issue:** `—`
- **Recorded:** 2026-09-01 11:30
- **Implemented:** `—`
- **Problem:** The MCP stdio server derives TRACKER from __file__ (REPO_ROOT = Path(__file__).resolve().parent.parent.parent), hardcoding it to the package install location with no environment-variable override. This makes safe E2E testing require isolated repo copies and breaks standalone wheel installs, where TRACKER resolves to a nonexistent site-packages/Lib/docs/IMPROVEMENTS.md.
- **Possible Fix:** Add an environment-variable override for the tracker path (and repo root) so a standalone install or an isolated test can point TRACKER at a file; fall back to the current __file__-derived path when the override is unset. This also fixes the packaging gap where a wheel-installed server cannot resolve its tracker.
- **Actual Fix:** `—`
- **Rejection Reason:** `—`
- **Actual Implemented:** `—`
- **Changes:** `—`
