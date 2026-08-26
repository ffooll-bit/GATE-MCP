# GATE-MCP

GATE-MCP is an MCP (Model Context Protocol) server that enforces GAIN-Coding workflow gates as code — guiding the agent through reviewed, policy-compliant interactions and keeping it anchored in traditional engineering discipline. It is the active, machine-driven companion to GAIN-Coding: where GAIN-Coding is the canonical workflow specification written for the agent to read through progressive context loading, GATE-MCP holds its own machine-oriented spec (YAML per workflow) that mirrors the GAIN-Coding document structure, and does not parse that markdown at runtime.

## Name

`GATE` stands for **G**uided **A**gent **T**hrough **E**nforcement. The full expansion is *Guided Agent Through Enforcement MCP*. (When the expanded GATE is written out, `MCP` stays unexpanded — "Enforcement Model Context Protocol" is never used.)

## Features

- Enforces GAIN-Coding workflow gates as code, keeping agent interactions reviewed and policy-compliant.
- Holds machine-oriented YAML specs (one per workflow and per policy) that mirror the GAIN-Coding document structure.
- Runs as a stdio MCP server using the official `mcp` SDK, with a single runtime dependency.
- First implementation is a vertical slice covering the `findings-and-planning` workflow plus an integrated `docs/IMPROVEMENTS.md` tracker validator; the remaining workflows are added in later sessions (YAGNI).

## Installation

```bash
pip install .
```

## Usage

Register GATE-MCP with your MCP client, or run it directly over stdio:

```bash
python -m gate_mcp
```

## Documentation

- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community standards
- [SECURITY.md](SECURITY.md) — security policy

## License

MIT. See [LICENSE](LICENSE).
