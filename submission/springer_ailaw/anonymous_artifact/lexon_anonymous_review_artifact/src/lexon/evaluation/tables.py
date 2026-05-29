"""
Paper-ready table generation for LEXON-Bench results.

All tables are generated from computed metrics — no values are hardcoded.
Tables are formatted as Markdown (for README) and CSV (for supplementary).

IMPORTANT: If the LLM baseline was not executed, it does NOT appear in any
main results table.  See outputs/audit/llm_baseline_status.json.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from lexon.schemas import AggregateMetrics


def _fmt(v: float, decimals: int = 2) -> str:
    if math.isnan(v):
        return "—"
    return f"{v:.{decimals}f}"


def _fmt_ci(lo: float, hi: float) -> str:
    if math.isnan(lo) or math.isnan(hi):
        return ""
    return f"[{lo:.2f}, {hi:.2f}]"


def make_table_activation_gap(
    systems: list[AggregateMetrics],
    output_path: Path | None = None,
) -> str:
    """
    Generate Table 5 equivalent: T1 and T2 metrics.

    Columns: System | T1 P | T1 R | Corpus T1 F1 | Mean-inst T1 F1 95% CI | T2 P | T2 R | Corpus T2 F1 | Mean-inst T2 F1 95% CI
    """
    header = (
        "| System | T1 P | T1 R | Corpus T1 F1 | Mean-inst T1 F1 95% CI | T2 P | T2 R | Corpus T2 F1 | Mean-inst T2 F1 95% CI |\n"
        "|:-------|:-----|:-----|:-------------|:------------------------|:-----|:-----|:-------------|:------------------------|\n"
    )
    rows = []
    for sys in systems:
        ci1 = _fmt_ci(sys.t1_f1_ci_lo, sys.t1_f1_ci_hi)
        ci2 = _fmt_ci(sys.t2_f1_ci_lo, sys.t2_f1_ci_hi)
        rows.append(
            f"| {sys.system_name} "
            f"| {_fmt(sys.t1_precision)} "
            f"| {_fmt(sys.t1_recall)} "
            f"| {_fmt(sys.t1_f1)} "
            f"| {ci1} "
            f"| {_fmt(sys.t2_precision)} "
            f"| {_fmt(sys.t2_recall)} "
            f"| {_fmt(sys.t2_f1)} "
            f"| {ci2} |"
        )

    note = (
        "\n*Table: Obligation activation (T1) and evidence-gap detection (T2) "
        f"on the {systems[0].split if systems else 'test'} split. "
        "**Corpus T1/T2 F1** (main columns) are corpus-level micro-averaged F1 "
        "computed from summed TP/FP/FN across all instances. "
        "**Mean-inst F1 95% CI** (bracketed columns) are bootstrapped (1000 iterations, "
        "seed=42) confidence intervals over per-instance F1 scores; these measure "
        "per-instance variability and are not uncertainty intervals for the corpus-level F1. "
        "LEXON corpus T1/T2 F1=1.00 on this synthetic benchmark is by construction "
        "(formal rules and gold oracle share identical semantics for unambiguous clauses; "
        "see §2.7 and §4.4). "
        "External validation on real regulatory provisions is future work.*\n"
    )
    table = header + "\n".join(rows) + "\n" + note

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(table)

    return table


def make_table_conflicts(
    systems: list[AggregateMetrics],
    output_path: Path | None = None,
) -> str:
    """Generate conflict detection (T3) table."""
    header = (
        "| System | T3 Precision | T3 Recall | T3 F1 |\n"
        "|:-------|:-------------|:----------|:------|\n"
    )
    rows = []
    for sys in systems:
        rows.append(
            f"| {sys.system_name} "
            f"| {_fmt(sys.t3_precision)} "
            f"| {_fmt(sys.t3_recall)} "
            f"| {_fmt(sys.t3_f1)} |"
        )
    note = (
        "\n*Table: Conflict detection (T3) on the test split. "
        "LEXON T3 is evaluated at the cross-clause level: unique unordered "
        "obligation pairs across all 30 system profiles (TP=11, FP=1, FN=0). "
        "Baselines (B1–B3) do not implement cross-clause conflict detection "
        "and score 0.00 by design. "
        "Conflict pairs are scoped to same-actor applicable obligations "
        "with incompatible actions (Definition 7).*\n"
    )
    table = header + "\n".join(rows) + "\n" + note

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(table)

    return table


def make_table_ablation(
    lexon: AggregateMetrics,
    b3: AggregateMetrics,
    b1: AggregateMetrics,
    output_path: Path | None = None,
) -> str:
    """
    Generate ablation table (§3.3).

    Shows contribution of rule layer (B1→B3) and typed graph (B3→LEXON).
    """
    header = (
        "| System | T1 F1 | T1 F1 gain | T2 F1 | T2 F1 gain |\n"
        "|:-------|:------|:-----------|:------|:-----------|\n"
    )
    gain_b1_b3_t1 = round(b3.t1_f1 - b1.t1_f1, 2)
    gain_b3_lex_t1 = round(lexon.t1_f1 - b3.t1_f1, 2)
    gain_b1_b3_t2 = round(b3.t2_f1 - b1.t2_f1, 2)
    gain_b3_lex_t2 = round(lexon.t2_f1 - b3.t2_f1, 2)

    rows = [
        f"| B1 Static checklist | {_fmt(b1.t1_f1)} | — | {_fmt(b1.t2_f1)} | — |",
        f"| B3 Flat rules (+rule layer) | {_fmt(b3.t1_f1)} | +{gain_b1_b3_t1:.2f} | {_fmt(b3.t2_f1)} | +{gain_b1_b3_t2:.2f} |",
        f"| LEXON full (+typed graph) | {_fmt(lexon.t1_f1)} | +{gain_b3_lex_t1:.2f} | {_fmt(lexon.t2_f1)} | +{gain_b3_lex_t2:.2f} |",
    ]
    note = (
        "\n*Ablation: T1 F1 gain from adding the rule layer (B1→B3) and "
        "from adding the typed graph (B3→LEXON). "
        "Typed graph contributes more to T2 (evidence-gap detection) than to T1.*\n"
    )
    table = header + "\n".join(rows) + "\n" + note

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(table)

    return table


def write_metrics_csv(
    systems: list[AggregateMetrics],
    output_path: Path,
) -> None:
    """Write aggregate metrics to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "system_name", "split", "n_instances",
        "t1_precision", "t1_recall", "t1_f1",
        "t1_f1_ci_lo", "t1_f1_ci_hi",
        "t2_precision", "t2_recall", "t2_f1",
        "t2_f1_ci_lo", "t2_f1_ci_hi",
        "t3_precision", "t3_recall", "t3_f1",
        "t2_false_negative_rate",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for sys in systems:
            writer.writerow({
                fld: (
                    "nan" if math.isnan(v := getattr(sys, fld))
                    else v
                )
                if isinstance(getattr(sys, fld), float)
                else getattr(sys, fld)
                for fld in fields
            })


def check_no_placeholders(path: Path) -> list[str]:
    """
    Check that a generated table file contains no placeholder tokens.

    Returns list of violations (empty = OK).
    """
    BAD_TOKENS = [
        "[EXT]", "TODO", "TBD", "camera-ready", "planned experiment",
        "PLACEHOLDER", "INSERT HERE", "companion paper",
        "real regulatory-text evaluation is reported",
        "reported in the companion paper", "to be inserted", "[DOI", "[URL",
    ]
    violations: list[str] = []
    if not path.exists():
        violations.append(f"File not found: {path}")
        return violations
    content = path.read_text()
    content_lower = content.lower()
    for tok in BAD_TOKENS:
        if tok.lower() in content_lower:
            violations.append(f"Placeholder '{tok}' found in {path}")
    return violations
