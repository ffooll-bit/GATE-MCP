"""Policy enforcement for documents: writing-quality checks.

validate_doc() loads a writing-quality policy spec from specs/policies/ and checks
a target file against it. Deterministic checks (BOM, line ending, trailing
whitespace, non-Latin script) are returned as errors; heuristic checks (hardwrap,
Indonesian-language detection) are returned as warnings so they never block on a
false positive, only surface a high-signal concern for agent/human review.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from gate_mcp.spec_loader import SpecError, load_policy_spec

DEFAULT_POLICY = "writing-quality"


def _is_latin(c: str) -> bool:
    """True if ``c`` is an alphabetic Latin-script character."""
    return "LATIN" in (unicodedata.name(c, "") or "") and c.isalpha()


def _non_latin_letters(text: str) -> list[str]:
    """Return non-ASCII, non-Latin alphabetic characters present in ``text``."""
    return sorted(
        {c for c in text if c.isalpha() and ord(c) > 127 and not _is_latin(c)}
    )


def _indonesian_token_ratio(text: str, words: list[str]) -> float:
    """Ratio of tokens that are Indonesian function words."""
    allow = set(words)
    tokens = [t.lower() for t in re.findall(r"[^\W\d_]+(?:['\u2019][^\W\d_]+)*", text)]
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in allow)
    return hits / len(tokens)


class _Checker:
    """Stateful paragraph-aware line scanner for hardwrap detection."""

    def __init__(self, spec: dict) -> None:
        hw = spec.get("hardwrap") or {}
        self.skip_prefixes = tuple(hw.get("skip_prefixes") or [])
        self.sentence_end_chars = set(hw.get("sentence_end_chars") or ".?!:;")
        self.min_broken = int(hw.get("min_sentence_broken_lines") or 2)
        self.lines: list[str] = []

    def feed(self, lines: list[str]) -> None:
        self.lines = lines

    def broken_lines(self) -> list[int]:
        """One-based line numbers of lines that appear to hard-wrap a sentence."""
        broken: list[int] = []
        lines = self.lines
        in_fence = False
        for i in range(len(lines) - 1):
            line = lines[i]
            stripped = line.rstrip()
            if stripped.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if not stripped or stripped.lstrip().startswith(self.skip_prefixes):
                continue
            nxt = lines[i + 1].strip()
            if not nxt or nxt.startswith(self.skip_prefixes):
                # paragraph boundary — no proof of an artificial wrap
                continue
            if (
                nxt[0].islower()
                and stripped
                and stripped[-1] not in self.sentence_end_chars
            ):
                broken.append(i + 1)
        if len(broken) < self.min_broken:
            return []
        # dedupe to the first min_broken to keep the message concise
        return broken[: self.min_broken]


def validate_doc(path, policy_name: str = DEFAULT_POLICY) -> dict:
    """Validate a document at ``path`` against the writing-quality policy.

    Returns a dict with ``ok`` (True when no errors), ``path``, and ``findings``,
    each finding being {severity, code, message, line?}.
    """
    try:
        data = load_policy_spec(policy_name)
    except SpecError as exc:
        return {
            "ok": False,
            "path": str(path),
            "findings": [
                {
                    "severity": "error",
                    "code": "policy_spec",
                    "message": str(exc),
                }
            ],
        }
    spec = data
    findings: list[dict] = []

    raw = Path(path).read_bytes()
    bom_rule = spec.get("bom") or {}
    if bom_rule.get("allowed") == "none" and raw[:3] == b"\xef\xbb\xbf":
        findings.append(
            {
                "severity": bom_rule.get("severity", "error"),
                "code": "bom",
                "message": "file starts with a UTF-8 BOM; expected none",
            }
        )

    text = raw.decode("utf-8", errors="replace")
    le_rule = spec.get("line_ending") or {}
    if le_rule.get("allowed") == "lf" and "\r\n" in text:
        first_crlf = text.find("\r\n")
        findings.append(
            {
                "severity": le_rule.get("severity", "error"),
                "code": "crlf",
                "message": "file uses CRLF line endings; expected LF",
                "line": text.count("\n", 0, first_crlf) + 1,
            }
        )

    tw_rule = spec.get("trailing_whitespace") or {}
    if tw_rule.get("allowed") == "none":
        for i, line in enumerate(text.splitlines(), 1):
            if line.rstrip(" \t") != line:
                findings.append(
                    {
                        "severity": tw_rule.get("severity", "error"),
                        "code": "trailing_whitespace",
                        "message": "line ends with whitespace",
                        "line": i,
                    }
                )
                break

    lang = spec.get("language") or {}
    if lang.get("enforced"):
        nll = _non_latin_letters(text)
        if nll:
            findings.append(
                {
                    "severity": lang.get("non_ascii_severity", "error"),
                    "code": "non_latin_script",
                    "message": f"non-Latin script characters present: {', '.join(nll)}",
                }
            )

    hw = _Checker(spec)
    lines = text.splitlines()
    hw.feed(lines)
    for lineno in hw.broken_lines():
        findings.append(
            {
                "severity": spec.get("hardwrap", {}).get("severity", "warning"),
                "code": "hardwrap",
                "message": "line appears to force-wrap a sentence; write the paragraph as one line",
                "line": lineno,
            }
        )

    if lang.get("enforced"):
        ratio = _indonesian_token_ratio(
            text, lang.get("indonesian_function_words") or []
        )
        if ratio >= float(lang.get("indonesian_token_ratio_threshold") or 0.02):
            findings.append(
                {
                    "severity": lang.get("severity", "warning"),
                    "code": "language",
                    "message": (
                        f"text appears to contain Indonesian (function-word ratio {ratio:.3f}); "
                        "International English required"
                    ),
                }
            )

    errors = [f for f in findings if f["severity"] == "error"]
    result = {
        "ok": not errors,
        "path": str(path),
        "findings": findings,
    }
    return result
