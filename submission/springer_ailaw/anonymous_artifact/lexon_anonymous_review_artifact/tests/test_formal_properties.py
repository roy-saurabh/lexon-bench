"""
Formal-property tests for the LEXON AI & Law artifact.

Tests:
1. Trace files are generated.
2. Applicable trace has all-true conditions, actor_match, no evidence gaps.
3. NotApplicable trace has at least one false condition.
4. Uncertain trace has unknown condition and human_review_required.
5. Conflict trace is canonical pair with correct trace_type.
6. Illustrative mapping is not a validated corpus.
7. No legal-advice claims appear in docs or README.
8. Data availability statement mentions both v1.1.0 and v1.0.2.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_trace(filename: str) -> dict:
    return json.loads((REPO_ROOT / "outputs" / "traces" / filename).read_text())


# ---------------------------------------------------------------------------
# 1. Trace files are generated
# ---------------------------------------------------------------------------

def test_trace_files_are_generated(tmp_path):
    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from lexon.tracing.derivation_trace import write_trace_examples

    written = write_trace_examples(tmp_path)
    assert len(written) == 4
    names = {p.name for p in written}
    assert "trace_applicable_CL-002_SYS-007.json" in names
    assert "trace_not_applicable_CL-002_SYS-013.json" in names
    assert "trace_uncertain_CL-010_SYS-027.json" in names
    assert "trace_conflict_example.json" in names
    for p in written:
        assert p.exists()
        data = json.loads(p.read_text())
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# 2. Applicable trace
# ---------------------------------------------------------------------------

def test_applicable_trace_has_all_true_conditions(tmp_path):
    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from lexon.tracing.derivation_trace import write_trace_examples

    write_trace_examples(tmp_path)
    trace = json.loads((tmp_path / "trace_applicable_CL-002_SYS-007.json").read_text())

    assert trace["activation_status"] == "Applicable"
    assert trace["actor_match"] is True
    assert trace["evidence_gaps"] == []
    assert len(trace["conditions"]) > 0
    for cond in trace["conditions"]:
        assert cond["truth_value"] == "true", (
            f"Expected all truth_value='true', got {cond['truth_value']!r} for {cond}"
        )


# ---------------------------------------------------------------------------
# 3. NotApplicable trace
# ---------------------------------------------------------------------------

def test_not_applicable_trace_has_false_condition(tmp_path):
    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from lexon.tracing.derivation_trace import write_trace_examples

    write_trace_examples(tmp_path)
    trace = json.loads((tmp_path / "trace_not_applicable_CL-002_SYS-013.json").read_text())

    assert trace["activation_status"] == "NotApplicable"
    truth_values = [c["truth_value"] for c in trace["conditions"]]
    assert "false" in truth_values, f"Expected at least one 'false' condition, got {truth_values}"


# ---------------------------------------------------------------------------
# 4. Uncertain trace
# ---------------------------------------------------------------------------

def test_uncertain_trace_has_unknown_condition_and_human_review(tmp_path):
    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from lexon.tracing.derivation_trace import write_trace_examples

    write_trace_examples(tmp_path)
    trace = json.loads((tmp_path / "trace_uncertain_CL-010_SYS-027.json").read_text())

    assert trace["activation_status"] == "Uncertain"
    truth_values = [c["truth_value"] for c in trace["conditions"]]
    assert "unknown" in truth_values, f"Expected at least one 'unknown' condition, got {truth_values}"
    assert trace["human_review_required"] is True


# ---------------------------------------------------------------------------
# 5. Conflict trace
# ---------------------------------------------------------------------------

def test_conflict_trace_is_canonical_pair(tmp_path):
    import sys
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from lexon.tracing.derivation_trace import write_trace_examples

    write_trace_examples(tmp_path)
    trace = json.loads((tmp_path / "trace_conflict_example.json").read_text())

    assert trace["trace_type"] == "conflict"
    assert "obligation_id_1" in trace
    assert "obligation_id_2" in trace
    assert trace["obligation_id_1"] < trace["obligation_id_2"], (
        f"obligation_id_1 should be lexicographically less than obligation_id_2: "
        f"{trace['obligation_id_1']!r} vs {trace['obligation_id_2']!r}"
    )


# ---------------------------------------------------------------------------
# 6. Illustrative mapping is not a validated corpus
# ---------------------------------------------------------------------------

def test_illustrative_mapping_is_not_validated_corpus():
    csv_path = REPO_ROOT / "data" / "illustrative" / "eu_ai_act_mapping.csv"
    assert csv_path.exists(), f"{csv_path} not found"

    rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    assert len(rows) >= 7, f"Expected at least 7 rows, got {len(rows)}"

    for row in rows:
        assert row["validation_status"] == "Illustrative mapping only", (
            f"Row {row['provision_id']}: unexpected validation_status={row['validation_status']!r}"
        )


# ---------------------------------------------------------------------------
# 7. No legal-advice claims in docs/README
# ---------------------------------------------------------------------------

# Phrases that are claims rather than negations
_CLAIM_PATTERNS = [
    r"provides legal advice",
    r"certifies compliance",
    r"expert-validated legal corpus",
    r"determines legal compliance",
]

# These phrases are fine when preceded by negation words
_NEGATION_PREFIX = re.compile(
    r"(does not|do not|cannot|never|not a|not an|no claim|not provide|not determine|not certify)\b",
    re.IGNORECASE,
)


def _check_file_for_claims(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    violations = []
    for pattern in _CLAIM_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 80)
            context = text[start : m.end() + 40]
            before = text[start : m.start()]
            if not _NEGATION_PREFIX.search(before[-120:]):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}: positive claim found — "
                    f"'{m.group()}' in context: ...{context.strip()}..."
                )
    return violations


def test_no_legal_advice_claims_in_docs():
    check_paths = list((REPO_ROOT / "docs").glob("*.md")) + [REPO_ROOT / "README.md"]
    all_violations = []
    for path in check_paths:
        if path.exists():
            all_violations.extend(_check_file_for_claims(path))

    assert not all_violations, (
        "Found positive legal-advice claims (not preceded by negation):\n"
        + "\n".join(all_violations)
    )


# ---------------------------------------------------------------------------
# 8. Data availability statement mentions both versions
# ---------------------------------------------------------------------------

def test_data_availability_mentions_v1_1_and_v1_0_2():
    das_path = REPO_ROOT / "docs" / "data_availability_statement.md"
    assert das_path.exists(), f"{das_path} not found"

    text = das_path.read_text()
    assert "v1.1.0" in text, "data_availability_statement.md must mention v1.1.0"
    assert "v1.0.2" in text, "data_availability_statement.md must mention v1.0.2"
