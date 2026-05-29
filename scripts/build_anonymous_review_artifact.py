#!/usr/bin/env python3
"""Build clean anonymous ZIP for double-anonymous peer review."""

import json
import re
import shutil
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "submission" / "springer_ailaw" / "anonymous_artifact"
ARTIFACT_NAME = "lexon_anonymous_review_artifact"
ARTIFACT_DIR = OUT_DIR / ARTIFACT_NAME

# --- sanitisation rules (order matters: longer strings first) ---
SANITISE_RULES = [
    (r"Roy Saurabh", "[author withheld for review]"),
    (r"AffectLog SAS", "[institution withheld for review]"),
    (r"AffectLog", "[institution withheld for review]"),
    (r"roy@affectlog\.com", "[email withheld for review]"),
    (r"https://github\.com/roy-saurabh/lexon-bench", "[repository withheld for double-anonymous review]"),
    (r"github\.com/roy-saurabh/lexon-bench", "[repository withheld for double-anonymous review]"),
    (r"10\.5281/zenodo\.20399201", "[DOI withheld for double-anonymous review]"),
    (r"10\.5281/zenodo\.20397383", "[concept DOI withheld for double-anonymous review]"),
    # "Saurabh" standalone (not inside another word)
    (r"\bSaurabh\b", "[author withheld]"),
    # "Roy" only when used as author name: preceded/followed by word boundary,
    # but NOT when inside unrelated words (e.g. "royalty" is excluded by \b).
    # We apply this last so "Roy Saurabh" is already replaced above.
    (r"\bRoy\b", "[author withheld]"),
]

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".json", ".jsonl", ".csv",
    ".yaml", ".yml", ".toml", ".ttl", ".rego", ".rst",
}

# Files/dirs to exclude entirely from the artifact
EXCLUDE_PATTERNS = {
    ".git", ".github", "CITATION.cff", ".zenodo.json",
    "submission", "paper-txt", ".venv", ".pytest_cache",
    "__pycache__", "*.pyc", ".DS_Store", "*.pdf", "*.docx",
    "title_page", "cover_letter",
}

# Files to include explicitly (relative to REPO_ROOT)
INCLUDE_PATHS = [
    "src",
    "rules",
    "data/synthetic",
    "data/illustrative",
    "outputs/results",
    "outputs/tables",
    "outputs/reports/ailaw_results_block.md",
    "outputs/traces",
    "tests",
    "scripts/generate_trace_examples.py",
    "scripts/validate_illustrative_mapping.py",
    "pyproject.toml",
    "Makefile",
    "LICENSE",
    "LICENSE-DATA",
    "README_ANONYMOUS_REVIEW.md",
]


def _is_excluded(path: Path) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if path.name.endswith(pattern[1:]):
                return True
        elif path.name == pattern or any(part == pattern for part in path.parts):
            return True
    return False


def _sanitise_text(text: str) -> str:
    for pattern, replacement in SANITISE_RULES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _copy_path(src: Path, dest_base: Path) -> list[str]:
    """Copy src (file or dir) into dest_base, sanitising text files."""
    copied = []
    if src.is_file():
        dest = dest_base / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_EXTENSIONS:
            try:
                content = src.read_text(encoding="utf-8", errors="replace")
                dest.write_text(_sanitise_text(content), encoding="utf-8")
            except Exception:
                shutil.copy2(src, dest)
        else:
            shutil.copy2(src, dest)
        copied.append(str(dest.relative_to(ARTIFACT_DIR)))
    elif src.is_dir():
        for child in sorted(src.rglob("*")):
            if _is_excluded(child):
                continue
            if child.is_file():
                rel = child.relative_to(src)
                dest = dest_base / src.name / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if child.suffix.lower() in TEXT_EXTENSIONS:
                    try:
                        content = child.read_text(encoding="utf-8", errors="replace")
                        dest.write_text(_sanitise_text(content), encoding="utf-8")
                    except Exception:
                        shutil.copy2(child, dest)
                else:
                    shutil.copy2(child, dest)
                copied.append(str(dest.relative_to(ARTIFACT_DIR)))
    return copied


def _blind_check(artifact_dir: Path) -> list[dict]:
    """Return list of findings: {file, term, line, severity}."""
    findings = []
    hard_terms = [
        "Roy Saurabh", "Saurabh", "AffectLog", "roy@affectlog.com",
        "github.com/roy-saurabh", "20399201", "20397383",
        "0000-0003-3439-7731", "founder of AffectLog",
    ]
    soft_terms = ["Roy"]  # checked only as whole word

    for fpath in sorted(artifact_dir.rglob("*")):
        if not fpath.is_file():
            continue
        if fpath.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for lineno, line in enumerate(lines, 1):
            line_lower = line.lower()
            for term in hard_terms:
                if term.lower() in line_lower:
                    findings.append({
                        "file": str(fpath.relative_to(artifact_dir)),
                        "term": term,
                        "line": lineno,
                        "severity": "FAIL",
                    })
            for term in soft_terms:
                if re.search(r"\b" + re.escape(term) + r"\b", line, re.IGNORECASE):
                    findings.append({
                        "file": str(fpath.relative_to(artifact_dir)),
                        "term": term,
                        "line": lineno,
                        "severity": "WARN",
                    })
    return findings


def build() -> None:
    if ARTIFACT_DIR.exists():
        shutil.rmtree(ARTIFACT_DIR)
    ARTIFACT_DIR.mkdir(parents=True)

    all_files: list[str] = []

    for rel in INCLUDE_PATHS:
        src = REPO_ROOT / rel
        if not src.exists():
            print(f"  [skip] not found: {rel}")
            continue
        # Compute the dest_base so the path inside the artifact mirrors the source layout
        if src.is_file():
            dest_base = ARTIFACT_DIR / src.parent.relative_to(REPO_ROOT)
        else:
            dest_base = ARTIFACT_DIR / src.parent.relative_to(REPO_ROOT)
        dest_base.mkdir(parents=True, exist_ok=True)
        copied = _copy_path(src, dest_base)
        all_files.extend(copied)
        print(f"  [ok] {rel} ({len(copied)} file(s))")

    # Run blind check
    findings = _blind_check(ARTIFACT_DIR)
    hard_fails = [f for f in findings if f["severity"] == "FAIL"]
    blind_passed = len(hard_fails) == 0

    # Write manifest
    manifest = {
        "artifact_name": "LEXON anonymous review artifact",
        "journal": "Artificial Intelligence and Law",
        "review_mode": "double-anonymous",
        "contains_author_identifiers": not blind_passed,
        "public_repository_withheld": True,
        "public_doi_withheld": True,
        "reproduction_command": "make reproduce",
        "artifact_check_command": "make ailaw-artifact-check",
        "blind_check_passed": blind_passed,
        "blind_check_findings": findings,
        "contents": sorted(all_files),
    }
    manifest_path = ARTIFACT_DIR / "anonymous_artifact_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    all_files.append("anonymous_artifact_manifest.json")
    print(f"  [ok] manifest written ({len(all_files)} total files)")

    # Create ZIP
    zip_path = OUT_DIR / f"{ARTIFACT_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(ARTIFACT_DIR.rglob("*")):
            if fpath.is_file():
                zf.write(fpath, fpath.relative_to(OUT_DIR))

    print()
    print("=" * 60)
    print(f"ZIP path    : {zip_path}")
    print(f"Files       : {len(all_files)}")
    print(f"Blind check : {'PASSED' if blind_passed else 'FAILED'}")
    if not blind_passed:
        print(f"  {len(hard_fails)} hard fail(s):")
        for f in hard_fails[:10]:
            print(f"  FAIL  {f['file']}:{f['line']}  term={f['term']!r}")
    print("=" * 60)

    if not blind_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    build()
