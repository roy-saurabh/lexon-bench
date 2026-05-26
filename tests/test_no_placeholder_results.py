"""
Tests that generated outputs contain no placeholder text.

Requirement N (quality bar): No generated result includes placeholder tokens
such as [EXT], TODO, TBD, camera-ready, planned experiment.
"""

import json
from pathlib import Path

import pytest

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


def _check_string(content: str, source: str) -> None:
    """Assert content contains no placeholder tokens."""
    for tok in PLACEHOLDER_TOKENS:
        assert tok not in content, (
            f"Placeholder token '{tok}' found in {source}"
        )


def test_benchmark_clauses_no_placeholders():
    """Generated clause objects contain no placeholder text."""
    from lexon.benchmark.generate_synthetic import generate
    clauses, _, _ = generate()
    for clause in clauses:
        for obl in clause.obligations:
            _check_string(obl.action, f"obligation {obl.obligation_id} action")
            _check_string(obl.notes, f"obligation {obl.obligation_id} notes")


def test_gold_labels_no_placeholders():
    """Generated gold labels contain no placeholder text."""
    from lexon.benchmark.generate_synthetic import generate
    from lexon.benchmark.gold import generate_all_gold_labels
    clauses, profiles, instances = generate()
    ci = {c.clause_id: c for c in clauses}
    pi = {p.system_id: p for p in profiles}
    gold = generate_all_gold_labels(instances, ci, pi)
    for g in gold:
        _check_string(g.canonical_notes, f"gold label {g.instance_id} canonical_notes")


def test_table_files_no_placeholders():
    """If table files exist in outputs/, they must not contain placeholder text."""
    tables_dir = Path("outputs/tables")
    if not tables_dir.exists():
        pytest.skip("outputs/tables not yet generated — run `make reproduce` first")

    md_files = list(tables_dir.glob("*.md"))
    if not md_files:
        pytest.skip("No table files found")

    for path in md_files:
        content = path.read_text()
        _check_string(content, str(path))


def test_reproducibility_report_no_placeholders():
    """If reproducibility report exists, it must not contain placeholder text."""
    report_path = Path("outputs/reports/reproducibility_report.md")
    if not report_path.exists():
        pytest.skip("Reproducibility report not yet generated")
    content = report_path.read_text()
    _check_string(content, str(report_path))


def test_llm_audit_file_no_main_results():
    """LLM baseline audit file must not be in main results CSV if not executed."""
    metrics_path = Path("outputs/results/metrics_synthetic.csv")
    if not metrics_path.exists():
        pytest.skip("metrics_synthetic.csv not yet generated")

    content = metrics_path.read_text()
    # LLM baseline should not appear in main results
    assert "llm" not in content.lower() or "not executed" in content.lower(), (
        "LLM baseline results should not appear in main metrics CSV unless executed"
    )


def test_no_ext_in_table_files():
    """Paper-ready tables must not contain '[EXT]' — the LLM-disabled sentinel."""
    tables_dir = Path("outputs/tables")
    if not tables_dir.exists():
        pytest.skip("outputs/tables not yet generated")

    for path in tables_dir.glob("*.md"):
        content = path.read_text()
        assert "[EXT]" not in content, (
            f"[EXT] sentinel found in paper-ready table {path}"
        )


def test_outputs_do_not_claim_companion_real_text_evaluation():
    """Generated artifacts must not contain phrases that contradict the manuscript.

    Manuscript v3 states external regulatory-provision validation is future work.
    The phrase 'real regulatory-text evaluation is reported in the companion paper'
    (or variants) must not appear in any committed output or the README.
    """
    paths = [
        Path("outputs/tables/table_activation_gap.md"),
        Path("outputs/reports/reproducibility_report.md"),
        Path("README.md"),
    ]
    banned = [
        "real regulatory-text evaluation is reported in the companion paper",
        "reported in the companion paper",
        "companion paper",
    ]
    for p in paths:
        if not p.exists():
            pytest.skip(f"{p} not yet generated")
        text = p.read_text().lower()
        for phrase in banned:
            assert phrase not in text, (
                f"Banned phrase '{phrase}' found in {p}. "
                "Manuscript v3 states external validation is future work — "
                "no 'companion paper' claim should appear in committed outputs."
            )
