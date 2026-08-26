## Summary

<!-- What does this PR do? Keep it short and clear. -->

## Related issues

<!-- Link the issue(s) this PR closes - use one "Fixes #N" line per issue. -->

Fixes #

## Checklist

- [ ] `ruff check .` passes on all modified files
- [ ] `pytest` succeeds (verification and tests are green)
- [ ] No HTTP routes apply — this is a stdio MCP server (route check not needed)
- [ ] `ruff format .` passes (no style violations)
- [ ] `pytest` is green (if tests exist)
- [ ] No debug code left in the change
- [ ] All user inputs validated (server-side / tool-input schema)
- [ ] No web forms or HTML output — CSRF and output-escaping checks are N/A
- [ ] No unrelated files changed
- [ ] CHANGELOG updated if this is a user-facing change
- [ ] Behaviour verified with the MCP client if tool behaviour changed

## Screenshot (if applicable)

<!-- Paste screenshots here -->

## Notes for reviewers

<!-- Optional: anything the reviewer needs to know -->
