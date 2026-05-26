"""
Tests for evaluation metrics correctness.
"""

from lexon.evaluation.metrics import prf, compute_t1_instance, compute_t2_instance
from lexon.schemas import (
    ActivationTrace,
    ApplicabilityStatus,
    EvidenceGap,
    GoldLabels,
    ReasoningResult,
)


def _make_result(applicable_ids: list[str], gap_pairs: list[tuple[str, str]]) -> ReasoningResult:
    traces = [
        ActivationTrace(
            obligation_id=oid,
            status=ApplicabilityStatus.APPLICABLE if oid in applicable_ids
            else ApplicabilityStatus.NOT_APPLICABLE,
        )
        for oid in (applicable_ids + [f"O-NA-{i}" for i in range(2)])
    ]
    gaps = [
        EvidenceGap(obligation_id=oid, system_id="S", evidence_id=eid)
        for oid, eid in gap_pairs
    ]
    return ReasoningResult(
        instance_id="I-1",
        clause_id="C-1",
        system_id="S-1",
        activation_traces=traces,
        evidence_gaps=gaps,
    )


def _make_gold(applicable_ids: list[str], gap_pairs: list[tuple[str, str]]) -> GoldLabels:
    gaps_dict: dict[str, list[str]] = {}
    for oid, eid in gap_pairs:
        gaps_dict.setdefault(oid, []).append(eid)
    return GoldLabels(
        instance_id="I-1",
        clause_id="C-1",
        system_id="S-1",
        activation={oid: ApplicabilityStatus.APPLICABLE for oid in applicable_ids},
        evidence_gaps=gaps_dict,
    )


def test_perfect_precision_recall():
    """Perfect predictions → P=R=F1=1.0."""
    pred = _make_result(["O-1", "O-2"], [("O-1", "E-A")])
    gold = _make_gold(["O-1", "O-2"], [("O-1", "E-A")])
    tp, fp, fn = compute_t1_instance(pred, gold)
    assert tp == 2
    assert fp == 0
    assert fn == 0
    p, r, f = prf(tp, fp, fn)
    assert p == 1.0 and r == 1.0 and f == 1.0


def test_false_positive_reduces_precision():
    """Extra predicted positive → FP, precision < 1.0."""
    pred = _make_result(["O-1", "O-EXTRA"], [])
    gold = _make_gold(["O-1"], [])
    tp, fp, fn = compute_t1_instance(pred, gold)
    assert fp == 1
    p, r, f = prf(tp, fp, fn)
    assert p < 1.0
    assert r == 1.0


def test_false_negative_reduces_recall():
    """Missed gold positive → FN, recall < 1.0."""
    pred = _make_result([], [])
    gold = _make_gold(["O-1"], [])
    tp, fp, fn = compute_t1_instance(pred, gold)
    assert fn == 1
    p, r, f = prf(tp, fp, fn)
    assert r == 0.0


def test_t2_gap_metrics():
    """T2 gap detection metrics computed correctly."""
    pred = _make_result(["O-1"], [("O-1", "E-A"), ("O-1", "E-B")])
    gold = _make_gold(["O-1"], [("O-1", "E-A"), ("O-1", "E-C")])
    tp, fp, fn = compute_t2_instance(pred, gold)
    # ("O-1", "E-A") → TP; ("O-1", "E-B") → FP; ("O-1", "E-C") → FN
    assert tp == 1
    assert fp == 1
    assert fn == 1


def test_prf_zero_division():
    """prf handles zero denominator gracefully (returns 0.0)."""
    assert prf(0, 0, 0) == (0.0, 0.0, 0.0)
    assert prf(0, 1, 0)[0] == 0.0  # precision = 0/(0+1) = 0


def test_bootstrap_ci_deterministic():
    """Bootstrap CIs are identical for same seed."""
    from lexon.evaluation.bootstrap import bootstrap_ci
    vals = [0.8, 0.9, 0.85, 0.92, 0.88, 0.91, 0.87, 0.93, 0.89, 0.90]
    ci1 = bootstrap_ci(vals, seed=42)
    ci2 = bootstrap_ci(vals, seed=42)
    assert ci1 == ci2


def test_bootstrap_ci_different_seeds():
    """Different seeds may produce different CI bounds."""
    from lexon.evaluation.bootstrap import bootstrap_ci
    vals = [0.8, 0.9, 0.85, 0.92, 0.88, 0.91, 0.87, 0.93, 0.89, 0.90]
    ci42 = bootstrap_ci(vals, seed=42)
    ci99 = bootstrap_ci(vals, seed=99)
    # CIs may or may not differ (both valid), but both should be within [0, 1]
    assert all(0 <= v <= 1 for v in ci42)
    assert all(0 <= v <= 1 for v in ci99)
