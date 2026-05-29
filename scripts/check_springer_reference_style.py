#!/usr/bin/env python3
"""Heuristic check for Springer AI&L author-year reference style.

Checks:
- Fail if in-text numeric citations like [1], [2,3] appear in manuscript body
- Fail if References section uses numbered entries "1.", "2."
- Warn if reference list is not alphabetized by first token
- Warn if references lack https://doi.org/ links where DOI patterns appear
- Warn if "Proc." abbreviations are used inconsistently

Usage:
    python scripts/check_springer_reference_style.py
    python scripts/check_springer_reference_style.py --manuscript path/to/file.md
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANUSCRIPT = (
    REPO_ROOT
    / "submission"
    / "springer_ailaw"
    / "anonymized_manuscript"
    / "LEXON_AILaw_anonymized.md"
)

# Numeric in-text citation: [1], [1,2], [1-3], [12]
NUMERIC_CITATION_RE = re.compile(r"\[\d[\d,\s\-]*\]")
# Numbered reference entry: starts with "1.", "23.", etc.
NUMBERED_REF_ENTRY_RE = re.compile(r"^\s*\d+\.\s+\S")
# DOI pattern without https:// prefix
BARE_DOI_RE = re.compile(r"(?<!\w)10\.\d{4,}/\S+")
FULL_DOI_RE = re.compile(r"https://doi\.org/10\.\d{4,}/\S+")


def _find_references_section(lines: list[str]) -> int:
    """Return line index of the References heading, or -1."""
    for i, line in enumerate(lines):
        stripped = line.strip().rstrip("*_")
        if re.match(r"^#{1,3}\s+References?\s*$", stripped, re.IGNORECASE):
            return i
    return -1


def check(manuscript_path: Path) -> list[dict]:
    findings: list[dict] = []

    if not manuscript_path.exists():
        findings.append({
            "severity": "FAIL",
            "location": str(manuscript_path),
            "message": "Manuscript file not found.",
        })
        return findings

    text = manuscript_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    refs_idx = _find_references_section(lines)
    body_lines = lines[:refs_idx] if refs_idx >= 0 else lines
    ref_lines  = lines[refs_idx + 1:] if refs_idx >= 0 else []

    # 1. Numeric in-text citations in body
    for lineno, line in enumerate(body_lines, 1):
        for match in NUMERIC_CITATION_RE.finditer(line):
            findings.append({
                "severity": "FAIL",
                "location": f"line {lineno}",
                "message": f"Numeric citation found: {match.group()!r}  — convert to author-year style.",
            })

    # 2. Numbered reference entries
    if ref_lines:
        for i, line in enumerate(ref_lines, refs_idx + 2):
            if NUMBERED_REF_ENTRY_RE.match(line):
                findings.append({
                    "severity": "FAIL",
                    "location": f"line {i}",
                    "message": f"Numbered reference entry: {line.strip()[:80]!r}  — references must not be numbered.",
                })

    # 3. Alphabetisation check
    if ref_lines:
        ref_entries = [l.strip() for l in ref_lines if l.strip() and not l.startswith("#")]
        first_tokens = []
        for entry in ref_entries:
            # Extract first alphabetic token (ignore markdown bullets/asterisks)
            m = re.search(r"[A-Za-z]\S*", entry)
            if m:
                first_tokens.append(m.group().lower())
        if first_tokens != sorted(first_tokens):
            findings.append({
                "severity": "WARN",
                "location": "References section",
                "message": "Reference list may not be alphabetized by first author/institution.",
            })

    # 4. Bare DOI patterns
    for lineno, line in enumerate(lines, 1):
        for match in BARE_DOI_RE.finditer(line):
            if not FULL_DOI_RE.search(line):
                findings.append({
                    "severity": "WARN",
                    "location": f"line {lineno}",
                    "message": f"DOI without https://doi.org/ prefix: {match.group()!r}",
                })

    # 5. "Proc." inconsistency
    proc_abbrev = sum(1 for l in lines if "Proc." in l)
    proc_full   = sum(1 for l in lines if re.search(r"\bProceedings\b", l, re.IGNORECASE))
    if proc_abbrev > 0 and proc_full > 0:
        findings.append({
            "severity": "WARN",
            "location": "References section",
            "message": f"Mixed use of 'Proc.' ({proc_abbrev}) and 'Proceedings' ({proc_full}). Pick one.",
        })

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Springer reference-style checker")
    parser.add_argument(
        "--manuscript", type=Path, default=DEFAULT_MANUSCRIPT,
        help="Path to anonymized manuscript .md file",
    )
    args = parser.parse_args()

    findings = check(args.manuscript)
    fails = [f for f in findings if f["severity"] == "FAIL"]
    warns = [f for f in findings if f["severity"] == "WARN"]

    print(f"\nSpringer reference-style check: {len(fails)} FAIL(s), {len(warns)} WARN(s)\n")
    for f in findings:
        print(f"  [{f['severity']}] {f['location']}: {f['message']}")

    if fails:
        print(f"\nFAILED — {len(fails)} reference style error(s).")
        sys.exit(1)
    elif warns:
        print(f"\nPASSED (with {len(warns)} warning(s)).")
    else:
        print("\nPASSED — reference style OK.")


if __name__ == "__main__":
    main()
