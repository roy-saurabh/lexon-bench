#!/usr/bin/env python3
"""Heuristic checks for Springer AI&L manuscript style requirements.

Checks:
- Keyword count (must be 4–6)
- Abstract word count (150–250)
- Figure naming: "Fig. N" not "Figure N"
- Figure file existence (Fig1.png / pipeline.png)
- Table numbering consecutive
- Source file existence (.docx, title page, artifact ZIP)

Usage:
    python scripts/check_springer_manuscript_style.py
    python scripts/check_springer_manuscript_style.py --manuscript path/to/file.md
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

KEYWORD_LINE_RE = re.compile(r"\*\*Keywords?:?\*\*\s*(.+)", re.IGNORECASE)
ABSTRACT_HEADING_RE = re.compile(r"^#{1,3}\s+\*{0,2}Abstract\*{0,2}\s*$", re.IGNORECASE)
FIGURE_FULL_RE = re.compile(r"\bFigure\s+\d+", re.IGNORECASE)
FIG_ABBREV_RE  = re.compile(r"\bFig\.\s*\d+", re.IGNORECASE)
TABLE_REF_RE   = re.compile(r"\bTable\s+(\d+)\b", re.IGNORECASE)
TABLE_DEFN_RE  = re.compile(r"^\*Table\s+(\d+)[.\s]", re.IGNORECASE)


def _extract_abstract(lines: list[str]) -> str:
    in_abstract = False
    para_lines: list[str] = []
    for line in lines:
        if ABSTRACT_HEADING_RE.match(line.strip()):
            in_abstract = True
            continue
        if in_abstract:
            if re.match(r"^#{1,3}\s+", line):  # next section heading
                break
            if line.strip().startswith("**Keywords"):
                break
            para_lines.append(line)
    return " ".join(para_lines)


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

    # --- 1. Keywords ---
    kw_count = 0
    for line in lines:
        m = KEYWORD_LINE_RE.search(line)
        if m:
            keywords = [k.strip() for k in m.group(1).split(";") if k.strip()]
            kw_count = len(keywords)
            break
    if kw_count == 0:
        findings.append({"severity": "WARN", "location": "Keywords",
                         "message": "No keywords line found."})
    elif kw_count < 4:
        findings.append({"severity": "FAIL", "location": "Keywords",
                         "message": f"Too few keywords ({kw_count}); Springer requires 4–6."})
    elif kw_count > 6:
        findings.append({"severity": "FAIL", "location": "Keywords",
                         "message": f"Too many keywords ({kw_count}); Springer requires 4–6. Current: {kw_count}."})
    else:
        findings.append({"severity": "OK", "location": "Keywords",
                         "message": f"Keyword count OK: {kw_count}."})

    # --- 2. Abstract word count ---
    abstract_text = _extract_abstract(lines)
    word_count = len(abstract_text.split())
    if word_count < 150:
        findings.append({"severity": "FAIL", "location": "Abstract",
                         "message": f"Abstract too short ({word_count} words); Springer requires 150–250."})
    elif word_count > 250:
        findings.append({"severity": "FAIL", "location": "Abstract",
                         "message": f"Abstract too long ({word_count} words); Springer requires 150–250."})
    else:
        findings.append({"severity": "OK", "location": "Abstract",
                         "message": f"Abstract word count OK: {word_count} words."})

    # --- 3. Figure naming ---
    for lineno, line in enumerate(lines, 1):
        if FIGURE_FULL_RE.search(line) and not FIG_ABBREV_RE.search(line):
            findings.append({"severity": "FAIL", "location": f"line {lineno}",
                             "message": f"Use 'Fig. N' not 'Figure N': {line.strip()[:80]!r}"})

    # --- 4. Figure file existence ---
    fig_candidates = [
        REPO_ROOT / "outputs" / "figures" / "pipeline.png",
        REPO_ROOT / "outputs" / "figures" / "Fig1.png",
        REPO_ROOT / "outputs" / "figures" / "Fig1.eps",
        REPO_ROOT / "outputs" / "figures" / "Fig1.tiff",
    ]
    found_fig = any(p.exists() for p in fig_candidates)
    if found_fig:
        found_path = next(p for p in fig_candidates if p.exists())
        findings.append({"severity": "OK", "location": "Figure file",
                         "message": f"Figure file found: {found_path.name}"})
    else:
        findings.append({"severity": "WARN", "location": "Figure file",
                         "message": "No Fig1.png/eps/tiff or pipeline.png found in outputs/figures/. "
                                    "Submit figure separately to Springer."})

    # --- 5. Table numbering consecutive ---
    table_numbers: list[int] = []
    for lineno, line in enumerate(lines, 1):
        m = TABLE_DEFN_RE.match(line)
        if m:
            table_numbers.append(int(m.group(1)))
    if table_numbers:
        expected = list(range(1, len(table_numbers) + 1))
        if table_numbers != expected:
            findings.append({"severity": "WARN", "location": "Tables",
                             "message": f"Table numbers not consecutive: {table_numbers} (expected {expected})"})
        else:
            findings.append({"severity": "OK", "location": "Tables",
                             "message": f"Table numbering consecutive: {table_numbers}"})

    # --- 6. Required submission files ---
    ms_docx = (
        REPO_ROOT / "submission" / "springer_ailaw" / "anonymized_manuscript" / "LEXON_AILaw_anonymized.docx"
    )
    title_docx = REPO_ROOT / "submission" / "springer_ailaw" / "title_page" / "title_page.docx"
    artifact_zip = (
        REPO_ROOT / "submission" / "springer_ailaw" / "anonymous_artifact" / "lexon_anonymous_review_artifact.zip"
    )

    for fpath, label in [
        (ms_docx, "Anonymized manuscript .docx"),
        (title_docx, "Title page .docx"),
        (artifact_zip, "Anonymous artifact .zip"),
    ]:
        if fpath.exists():
            findings.append({"severity": "OK", "location": label, "message": f"Found: {fpath.name}"})
        else:
            findings.append({"severity": "WARN", "location": label,
                             "message": f"Not found: {fpath}  (TODO: generate before submission)"})

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Springer manuscript style checker")
    parser.add_argument(
        "--manuscript", type=Path, default=DEFAULT_MANUSCRIPT,
        help="Path to anonymized manuscript .md file",
    )
    args = parser.parse_args()

    findings = check(args.manuscript)
    fails  = [f for f in findings if f["severity"] == "FAIL"]
    warns  = [f for f in findings if f["severity"] == "WARN"]
    oks    = [f for f in findings if f["severity"] == "OK"]

    print(f"\nSpringer manuscript style check: {len(fails)} FAIL(s), {len(warns)} WARN(s), {len(oks)} OK(s)\n")
    for f in findings:
        prefix = f"  [{f['severity']:<4}]"
        print(f"{prefix} {f['location']}: {f['message']}")

    if fails:
        print(f"\nFAILED — {len(fails)} style error(s).")
        sys.exit(1)
    elif warns:
        print(f"\nPASSED (with {len(warns)} warning(s)).")
    else:
        print("\nPASSED — manuscript style OK.")


if __name__ == "__main__":
    main()
