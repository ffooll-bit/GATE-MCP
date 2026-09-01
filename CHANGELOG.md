# Changelog

## [Unreleased]

### Added

- Machine-readable workflow spec `specs/workflows/findings-and-planning.yaml` mirroring GAIN-CODING findings-and-planning.md (#6)
- Findings-and-planning enforcement MCP tools (`record_finding`, `verify_finding`, `sync_tracker`, `archive_finding`, `deliver_finding`) with `docs/IMPROVEMENTS.md` tracker validator and spec loader (#5)
- Pytest suite for the spec loader and tracker validator (`tests/`) (#7)
- Protocol-level pytest suite for the MCP tools (`tests/test_server.py`), exercising the five tools over the real MCP protocol against an isolated temp tracker (#19)

### Changed

- Run the Python checks in CI (`ruff check`, `ruff format --check`, and `pytest`) on every push and pull request via a new `test` job (#13)
- Install the package with dev extras in the CI test job (`pip install -e .[dev]`) so the async tool tests pick up `pytest-asyncio` (#19)
- Track `ARCHITECTURE.md` and `STRUCTURE.md` as project design documents and gitignore the machine-local `.cortexkit/` and `.playwright-mcp/` tooling artifacts (#14)
- Gitignore the `build/` and `dist/` directories produced by packaging (#20)
- Support a `GATE_MCP_REPO` environment variable to override the tracker and spec locations off the package-relative default (#27)
- Document in the README that standalone operation requires a repo checkout or `GATE_MCP_REPO` pointing at one, since the wheel intentionally does not bundle the `specs/` or `docs/IMPROVEMENTS.md` (#25)

### Fixed

- `python -m gate_mcp` now starts the server correctly via a new `src/gate_mcp/__main__.py`; README documents both the `gate-mcp` console script and `python -m gate_mcp` (#18)

[Unreleased]: https://github.com/ffooll-bit/GATE-MCP/compare/v0.1.0...HEAD
