# Contributing to GATE-MCP

Thank you for considering a contribution. This project works issue-first: every change starts as a GitHub issue and lands through a reviewed pull request. The agent that works on this repo follows the GAIN-Coding workflow gates, so changes are reviewed and policy-compliant by construction.

## Reporting Issues

Open an issue with the bug report or feature request template. Describe the problem with reproduction steps, expected behavior, and your environment.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
pytest
```

## Pull Request Process

1. Create a working branch from `main` named `feature/`, `fix/`, `chore/`, `docs/`, or `refactor/`.
2. Make atomic commits with Conventional Commit messages (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
3. Run linting, tests, and the build locally before pushing.
4. Open a pull request into `main` that references the issue with `Fixes #N`.
5. Wait for green CI and review approval before merging.

## Style

- Conventional Commits for all commit messages.
- Markdown is soft-wrapped: never break a line mid-paragraph (line breaks only in tables, bullets, code blocks).
- All text files use `LF` line endings and UTF-8 without BOM.
- Formal documentation is written in International English.
