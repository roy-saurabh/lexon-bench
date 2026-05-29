"""
Evaluation metrics for LEXON-Bench.

Computes precision, recall, F1 for:
  T1 — obligation activation
  T2 — evidence-gap detection
  T3 — conflict pair detection

Also computes:
  - False negative rate for evidence gaps
  - Per-instance metrics
  - Aggregate metrics across a split

All computation is deterministic; no randomness here (bootstrap in bootstrap.py).
"""

from __future__ import annotations

import math
from collections import defaultdict

from lexon.schemas import (
    AggregateMetrics,
    ApplicabilityStatus,
    GoldLabels,
    InstanceMetrics,
    DifficultyLevel,
    ReasoningResult,
    SystemConflictGold,
    SystemConflictResult,
)


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    """Compute precision, recall, F1 from TP/FP/FN counts."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return round(precision, 4), round(recall, 4), round(f1, 4)


def compute_t1_instance(
    pred: ReasoningResult,
    gold: GoldLabels,
) -> tuple[int, int, int]:
    """
    Compute T1 (activation) TP/FP/FN for a single instance.

    Gold and pred activation dicts map obligation_id → ApplicabilityStatus.
    We treat APPLICABLE as positive; NOT_APPLICABLE and UNCERTAIN as negative.
    """
    tp = fp = fn = 0
    pred_applicable = {
        t.obligation_id
        for t in pred.activation_traces
        if t.status == ApplicabilityStatus.APPLICABLE
    }
    gold_applicable = {
        oid
        for oid, status in gold.activation.items()
        if status == ApplicabilityStatus.APPLICABLE
    }

    for oid in gold_applicable | pred_applicable:
        gold_pos = oid in gold_applicable
        pred_pos = oid in pred_applicable
        if gold_pos and pred_pos:
            tp += 1
        elif pred_pos and not gold_pos:
            fp += 1
        elif gold_pos and not pred_pos:
            fn += 1

    return tp, fp, fn


def compute_t2_instance(
    pred: ReasoningResult,
    gold: GoldLabels,
) -> tuple[int, int, int]:
    """
    Compute T2 (evidence gap) TP/FP/FN for a single instance.

    A gap is a (obligation_id, evidence_id) pair.
    """
    tp = fp = fn = 0
    pred_gaps: set[tuple[str, str]] = {
        (g.obligation_id, g.evidence_id)
        for g in pred.evidence_gaps
    }
    gold_gaps: set[tuple[str, str]] = {
        (oid, eid)
        for oid, eids in gold.evidence_gaps.items()
        for eid in eids
    }

    for pair in gold_gaps | pred_gaps:
        g_pos = pair in gold_gaps
        p_pos = pair in pred_gaps
        if g_pos and p_pos:
            tp += 1
        elif p_pos and not g_pos:
            fp += 1
        elif g_pos and not p_pos:
            fn += 1

    return tp, fp, fn


def compute_t3_instance(
    pred: ReasoningResult,
    gold: GoldLabels,
) -> tuple[int, int, int]:
    """
    Compute T3 (conflict) TP/FP/FN for a single instance.

    A conflict pair is an unordered pair {oid1, oid2}.
    """
    tp = fp = fn = 0
    pred_conflicts = {
        frozenset([c.obligation_id_1, c.obligation_id_2])
        for c in pred.conflict_pairs
    }
    gold_conflicts = {
        frozenset([o1, o2])
        for o1, o2 in gold.conflict_pairs
    }

    for pair in gold_conflicts | pred_conflicts:
        g_pos = pair in gold_conflicts
        p_pos = pair in pred_conflicts
        if g_pos and p_pos:
            tp += 1
        elif p_pos and not g_pos:
            fp += 1
        elif g_pos and not p_pos:
            fn += 1

    return tp, fp, fn


def compute_instance_metrics(
    pred: ReasoningResult,
    gold: GoldLabels,
    ambiguous: bool = False,
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
) -> InstanceMetrics:
    """Compute all per-instance metrics."""
    t1 = compute_t1_instance(pred, gold)
    t2 = compute_t2_instance(pred, gold)
    t3 = compute_t3_instance(pred, gold)

    t1_p, t1_r, t1_f1 = prf(*t1)
    t2_p, t2_r, t2_f1 = prf(*t2)
    t3_p, t3_r, t3_f1 = prf(*t3)

    return InstanceMetrics(
        instance_id=pred.instance_id,
        t1_precision=t1_p, t1_recall=t1_r, t1_f1=t1_f1,
        t2_precision=t2_p, t2_recall=t2_r, t2_f1=t2_f1,
        t3_conflict_precision=t3_p, t3_conflict_recall=t3_r, t3_conflict_f1=t3_f1,
        ambiguous=ambiguous,
        difficulty=difficulty,
    )


def compute_corpus_metrics(
    preds: list[ReasoningResult],
    golds: list[GoldLabels],
) -> dict[str, tuple[int, int, int]]:
    """
    Compute corpus-level (micro-averaged) TP/FP/FN for T1, T2, T3.

    This is the correct way to compute P/R/F1 when many instances have
    zero positives: we sum TP/FP/FN across all instances and compute
    corpus-level P/R/F1 once.  This matches the paper's reporting of
    "precision, recall, and F1 against the deterministic gold labels."

    Returns {task: (tp, fp, fn)}.
    """
    gold_index = {g.instance_id: g for g in golds}
    t1_tp = t1_fp = t1_fn = 0
    t2_tp = t2_fp = t2_fn = 0
    t3_tp = t3_fp = t3_fn = 0

    for pred in preds:
        gold = gold_index.get(pred.instance_id)
        if gold is None:
            continue
        tp, fp, fn = compute_t1_instance(pred, gold)
        t1_tp += tp; t1_fp += fp; t1_fn += fn
        tp, fp, fn = compute_t2_instance(pred, gold)
        t2_tp += tp; t2_fp += fp; t2_fn += fn
        tp, fp, fn = compute_t3_instance(pred, gold)
        t3_tp += tp; t3_fp += fp; t3_fn += fn

    return {
        "t1": (t1_tp, t1_fp, t1_fn),
        "t2": (t2_tp, t2_fp, t2_fn),
        "t3": (t3_tp, t3_fp, t3_fn),
    }


def aggregate_metrics(
    instance_metrics: list[InstanceMetrics],
    system_name: str,
    split: str,
    corpus_counts: dict[str, tuple[int, int, int]] | None = None,
) -> AggregateMetrics:
    """
    Aggregate metrics into corpus-level P/R/F1.

    When corpus_counts is provided (preferred), uses corpus-level (micro-averaged)
    P/R/F1. Otherwise falls back to macro-averaging per-instance P/R/F1.

    Bootstrap CIs are computed per-instance (on individual F1 scores) and filled
    by bootstrap.py.
    """
    n = len(instance_metrics)
    if n == 0:
        raise ValueError("No instances to aggregate")

    if corpus_counts is not None:
        t1_tp, t1_fp, t1_fn = corpus_counts["t1"]
        t2_tp, t2_fp, t2_fn = corpus_counts["t2"]
        t3_tp, t3_fp, t3_fn = corpus_counts["t3"]
        t1_p, t1_r, t1_f1 = prf(t1_tp, t1_fp, t1_fn)
        t2_p, t2_r, t2_f1 = prf(t2_tp, t2_fp, t2_fn)
        t3_p, t3_r, t3_f1 = prf(t3_tp, t3_fp, t3_fn)
        t2_fnr = round(1.0 - t2_r, 4)
    else:
        def _mean(vals: list[float | None]) -> float:
            clean = [v for v in vals if v is not None and not math.isnan(v)]
            return round(sum(clean) / len(clean), 4) if clean else 0.0
        t1_p = _mean([m.t1_precision for m in instance_metrics])
        t1_r = _mean([m.t1_recall for m in instance_metrics])
        t1_f1 = _mean([m.t1_f1 for m in instance_metrics])
        t2_p = _mean([m.t2_precision for m in instance_metrics])
        t2_r = _mean([m.t2_recall for m in instance_metrics])
        t2_f1 = _mean([m.t2_f1 for m in instance_metrics])
        t3_p = _mean([m.t3_conflict_precision for m in instance_metrics])
        t3_r = _mean([m.t3_conflict_recall for m in instance_metrics])
        t3_f1 = _mean([m.t3_conflict_f1 for m in instance_metrics])
        t2_fnr = round(1.0 - t2_r, 4)

    return AggregateMetrics(
        system_name=system_name,
        split=split,
        n_instances=n,
        t1_precision=t1_p,
        t1_recall=t1_r,
        t1_f1=t1_f1,
        t1_precision_ci_lo=float("nan"),
        t1_precision_ci_hi=float("nan"),
        t1_recall_ci_lo=float("nan"),
        t1_recall_ci_hi=float("nan"),
        t1_f1_ci_lo=float("nan"),
        t1_f1_ci_hi=float("nan"),
        t2_precision=t2_p,
        t2_recall=t2_r,
        t2_f1=t2_f1,
        t2_precision_ci_lo=float("nan"),
        t2_precision_ci_hi=float("nan"),
        t2_recall_ci_lo=float("nan"),
        t2_recall_ci_hi=float("nan"),
        t2_f1_ci_lo=float("nan"),
        t2_f1_ci_hi=float("nan"),
        t3_precision=t3_p,
        t3_recall=t3_r,
        t3_f1=t3_f1,
        t2_false_negative_rate=t2_fnr,
    )


def compute_cross_clause_t3_metrics(
    system_results: list[SystemConflictResult],
    system_golds: list[SystemConflictGold],
) -> tuple[int, int, int]:
    """
    Compute cross-clause T3 metrics at the unique obligation-pair level.

    Counts TP/FP/FN over the set of unique unordered (obl_id_1, obl_id_2) pairs
    detected across all 30 system profiles, matching the paper's reporting of
    T3 precision=0.917 (11/12), recall=1.0 (11/11).

    Gold set: unique conflict pairs from the canonical gold oracle
              (excludes CANONICAL_CONFLICT_EXCLUSIONS vocabulary over-generalisation).
    Pred set: unique conflict pairs from LEXON's rule-based engine
              (includes the over-broad FP pair).

    Returns (tp, fp, fn).
    """
    gold_pairs: set[frozenset[str]] = set()
    for sg in system_golds:
        for p in sg.conflict_pairs:
            gold_pairs.add(frozenset([p[0], p[1]]))

    pred_pairs: set[frozenset[str]] = set()
    for sr in system_results:
        for c in sr.cross_clause_conflicts:
            pred_pairs.add(frozenset([c.obligation_id_1, c.obligation_id_2]))

    tp = len(gold_pairs & pred_pairs)
    fp = len(pred_pairs - gold_pairs)
    fn = len(gold_pairs - pred_pairs)
    return tp, fp, fn
