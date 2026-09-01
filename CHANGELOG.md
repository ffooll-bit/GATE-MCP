# Changelog

## [Unreleased]

### Added

- Machine-readable workflow spec `specs/workflows/findings-and-planning.yaml` mirroring GAIN-CODING findings-and-planning.md (#6)
- Findings-and-planning enforcement MCP tools (`record_finding`, `verify_finding`, `sync_tracker`, `archive_finding`, `deliver_finding`) with `docs/IMPROVEMENTS.md` tracker validator and spec loader (#5)
- Pytest suite for the spec loader and tracker validator (`tests/`) (#7)

### Changed

- Run the Python checks in CI (`ruff check`, `ruff format --check`, and `pytest`) on every push and pull request via a new `test` job (#13)
- Track `ARCHITECTURE.md` and `STRUCTURE.md` as project design documents and gitignore the machine-local `.cortexkit/` and `.playwright-mcp/` tooling artifacts (#14)

### Fixed

- _Bug fixes, one line each, referencing the issue if applicable._

[Unreleased]: https://github.com/ffooll-bit/GATE-MCP/compare/v0.1.0...HEAD
