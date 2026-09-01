# Codebase Structure

## Directory Layout

```
GATE-MCP/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/      # GitHub issue templates
│   ├── dependabot.yml       # Dependabot configuration
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── RELEASE_NOTES_TEMPLATE.md
├── docs/
│   ├── social-preview.png   # Social card image
│   ├── social-preview.html  # Social card HTML source
│   ├── IMPROVEMENTS.md      # Tracker for findings (features/bugs/optimizations)
│   └── archived/            # Archived tracker snapshots (gitignored)
├── specs/
│   ├── policies/            # Policy YAML specs (one per policy)
│   └── workflows/           # Workflow YAML specs (one per workflow)
├── src/
│   └── gate_mcp/            # Python package (src layout)
│       ├── __init__.py      # Version metadata
│       ├── server.py        # MCP stdio server + tool registration
│       ├── spec_loader.py   # YAML spec loading + validation (cached)
│       └── tracker_validator.py  # IMPROVEMENTS.md parse/validate/rewrite
├── tests/                   # Pytest suite (co-located tests also allowed)
│   ├── test_spec_loader.py
│   └── test_tracker_validator.py
├── temp/                    # Temporary working files (gitignored)
├── CHANGELOG.md             # Release history
├── LICENSE                  # MIT license
├── README.md                # Project overview
├── CONTRIBUTING.md          # Contribution guidelines
├── CODE_OF_CONDUCT.md       # Community standards
├── SECURITY.md              # Security policy
├── pyproject.toml           # Build config, deps, entry points
├── .gitignore
├── .editorconfig
└── .gitattributes
```

## Directory Purposes

**.github/:**
- Purpose: GitHub automation (CI, issue templates, dependabot, PR template)
- Contains: Workflow YAML, markdown templates, YAML config
- Key files: `.github/workflows/ci.yml`, `.github/dependabot.yml`

**docs/:**
- Purpose: Human-facing documentation and tracker
- Contains: Markdown, images, HTML
- Key files: `docs/IMPROVEMENTS.md` (source of truth for findings tracker)

**specs/:**
- Purpose: Machine-oriented rule source for workflow enforcement
- Contains: YAML files (one per workflow, one per policy)
- Key files: `specs/workflows/findings-and-planning.yaml`, `specs/policies/*.yaml` (future)

**src/gate_mcp/:**
- Purpose: Python package implementing the MCP server
- Contains: Python modules (`.py`)
- Key files: `src/gate_mcp/__init__.py`, `src/gate_mcp/server.py`, `src/gate_mcp/spec_loader.py`, `src/gate_mcp/tracker_validator.py`

**tests/:**
- Purpose: Automated test suite
- Contains: Pytest test files (`test_*.py`), fixtures
- Key files: `tests/test_spec_loader.py`, `tests/test_tracker_validator.py`

**temp/:**
- Purpose: Scratch space for local development (not committed)
- Contains: Arbitrary temporary files
- Key files: (varies)

## Key File Locations

**Entry Points:** `src/gate_mcp/server.py:main()` — MCP stdio server bootstrap

**Configuration:** `pyproject.toml` — Build system, dependencies, entry points, package discovery

**Core Logic:**
- `src/gate_mcp/server.py` — FastMCP instance, 5 MCP tools (`record_finding`, `verify_finding`, `sync_tracker`, `archive_finding`, `deliver_finding`)
- `src/gate_mcp/spec_loader.py` — `load_workflow_spec`, `load_policy_spec` (cached via `functools.cache`)
- `src/gate_mcp/tracker_validator.py` — `parse_tracker`, `validate_format`, `validate_numbering`, `validate_gate_rules`, `validate_tracker`, `read_tracker`, `write_tracker`

**Tracker Source:** `docs/IMPROVEMENTS.md` — Canonical findings tracker (validated by server tools)

**Workflow Specs:** `specs/workflows/` — YAML specs driving enforcement (one file per workflow)

**Policy Specs:** `specs/policies/` — YAML specs for cross-cutting policies (one file per policy)

**Tests:** `tests/` — Pytest suite; `tests/test_spec_loader.py`, `tests/test_tracker_validator.py`; co-located `src/gate_mcp/test_*.py` also accepted

## Naming Conventions

**Files:** `snake_case.py` for Python modules: `spec_loader.py`, `tracker_validator.py`

**Directories:** `kebab-case` for top-level: `specs/workflows/`, `.github/workflows/`; `snake_case` for Python packages: `src/gate_mcp/`

**Workflow Spec Files:** `kebab-case.yaml` matching workflow name: `findings-and-planning.yaml`

**Policy Spec Files:** `kebab-case.yaml` matching policy name: `naming-conventions.yaml`

**Tracker Item IDs:** `<LABEL_CODE>-<NNN>` per GitHub labels: `ENH-001`, `BUG-002`, `DOC-003`

## Where to Add New Code

**New MCP tool:** `src/gate_mcp/server.py` — add `@mcp.tool()` function; register on `mcp` instance

**New workflow spec:** `specs/workflows/<workflow-name>.yaml` — mirror GAIN-Coding workflow structure

**New policy spec:** `specs/policies/<policy-name>.yaml` — declarative rules referenced by workflows

**Spec loader module:** `src/gate_mcp/spec_loader.py` — YAML loading, validation, caching (extend for new spec types)

**Tracker validator module:** `src/gate_mcp/tracker_validator.py` — Format, numbering, gate rule validation (extend for new rules)

**Shared utilities:** `src/gate_mcp/shared/` (create if needed) — Common helpers, constants, exceptions

**Tests:** `tests/test_<module>.py` — Pytest module per source module; co-located `src/gate_mcp/test_*.py` also accepted

**Documentation updates:** `docs/IMPROVEMENTS.md` — Add findings using the item template; `CHANGELOG.md` — Update on release