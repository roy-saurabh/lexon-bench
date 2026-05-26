"""
Script to check that all generated paper-ready files contain no placeholder text.

Exit code 0 = all clear.
Exit code 1 = placeholders found.

Run by CI after `make reproduce`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PLACEHOLDER_TOKENS = [
    "[EXT]",
    "TODO",
    "TBD",
    "camera-ready",
    "planned experiment",
    "PLACEHOLDER",
    "INSERT HERE",
    "NOT YET COMPUTED",
]

CHECK_PATHS = [
    Path("outputs/tables/table_activation_gap.md"),
    Path("outputs/tables/table_conflicts.md"),
    Path("outputs/tables/table_ablation.md"),
    Path("outputs/reports/reproducibility_report.md"),
    Path("outputs/results/metrics_synthetic.csv"),
]


def check() -> int:
    violations: list[str] = []
    missing: list[str] = []

    for path in CHECK_PATHS:
        if not path.exists():
            missing.append(str(path))
            continue
        content = path.read_text()
        for tok in PLACEHOLDER_TOKENS:
            if tok in content:
                violations.append(f"{path}: contains '{tok}'")

    if missing:
        print("Missing output files (run `make reproduce` first):")
        for m in missing:
            print(f"  - {m}")
        return 1

    if violations:
        print("PLACEHOLDER CHECK FAILED:")
        for v in violations:
            print(f"  ✗ {v}")
        return 1

    print("✓ No placeholder text found in any paper-ready output.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
