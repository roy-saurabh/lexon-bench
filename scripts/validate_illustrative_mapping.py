"""
Validate the illustrative EU AI Act mapping CSV.

Checks:
- Required columns are present.
- At least 7 rows.
- Every validation_status == "Illustrative mapping only".
- No cell contains forbidden claim phrases.

Exit 0 = pass. Exit 1 = failure.
"""

import csv
import sys
from pathlib import Path

CSV_PATH = Path("data/illustrative/eu_ai_act_mapping.csv")

REQUIRED_COLUMNS = {
    "provision_id",
    "instrument",
    "actor",
    "obligation_action",
    "condition",
    "evidence_object",
    "exception_or_limitation",
    "lexon_construct",
    "validation_status",
}

FORBIDDEN_PHRASES = [
    "legal advice",
    "certified",
    "validated corpus",
    "compliance certification",
]

EXPECTED_STATUS = "Illustrative mapping only"
MIN_ROWS = 7


def main() -> int:
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        return 1

    rows = list(csv.DictReader(CSV_PATH.read_text().splitlines()))

    missing_cols = REQUIRED_COLUMNS - set(rows[0].keys()) if rows else REQUIRED_COLUMNS
    if missing_cols:
        print(f"ERROR: Missing columns: {missing_cols}")
        return 1

    if len(rows) < MIN_ROWS:
        print(f"ERROR: Expected at least {MIN_ROWS} rows, got {len(rows)}")
        return 1

    failures = []

    for i, row in enumerate(rows, start=2):
        status = row.get("validation_status", "")
        if status != EXPECTED_STATUS:
            failures.append(f"Row {i}: validation_status = {status!r} (expected {EXPECTED_STATUS!r})")

        for col, val in row.items():
            val_lower = val.lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in val_lower:
                    failures.append(f"Row {i}, col {col!r}: contains forbidden phrase {phrase!r}")

    if failures:
        print("VALIDATION FAILED:")
        for f in failures:
            print(f"  {f}")
        return 1

    print(
        f"PASS: {len(rows)} rows validated. "
        f"All validation_status == {EXPECTED_STATUS!r}. "
        "No forbidden phrases found."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
