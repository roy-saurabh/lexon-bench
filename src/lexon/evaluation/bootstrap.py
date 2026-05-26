"""
Non-parametric bootstrap confidence intervals for LEXON-Bench metrics.

Implements 1000-iteration bootstrap as specified in §2.10 of the paper.
All bootstrap operations use seed=42 for reproducibility.
"""

from __future__ import annotations

import math
import random
from typing import Callable

from lexon.constants import RANDOM_SEED
from lexon.schemas import AggregateMetrics, InstanceMetrics

N_BOOTSTRAP = 1000
CI_ALPHA = 0.05  # 95% confidence interval


def bootstrap_ci(
    values: list[float],
    stat_fn: Callable[[list[float]], float] = lambda x: sum(x) / len(x),
    n_iter: int = N_BOOTSTRAP,
    alpha: float = CI_ALPHA,
    seed: int = RANDOM_SEED,
) -> tuple[float, float]:
    """
    Non-parametric bootstrap CI for a scalar statistic.

    Returns (lower_bound, upper_bound) at (1-alpha) confidence level.
    """
    if not values:
        return (float("nan"), float("nan"))

    rng = random.Random(seed)
    n = len(values)
    boot_stats: list[float] = []

    for _ in range(n_iter):
        sample = [values[rng.randint(0, n - 1)] for _ in range(n)]
        boot_stats.append(stat_fn(sample))

    boot_stats.sort()
    lo_idx = int(math.floor((alpha / 2) * n_iter))
    hi_idx = int(math.ceil((1 - alpha / 2) * n_iter)) - 1
    lo_idx = max(0, lo_idx)
    hi_idx = min(n_iter - 1, hi_idx)

    return (round(boot_stats[lo_idx], 4), round(boot_stats[hi_idx], 4))


def fill_bootstrap_cis(
    metrics: AggregateMetrics,
    instance_metrics: list[InstanceMetrics],
    seed: int = RANDOM_SEED,
) -> AggregateMetrics:
    """
    Fill bootstrap CIs in an AggregateMetrics object.

    Modifies in-place and returns the updated object.
    """

    def mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    def get_vals(attr: str) -> list[float]:
        return [
            v for m in instance_metrics
            if (v := getattr(m, attr)) is not None and not math.isnan(v)
        ]

    # T1 CIs
    for field, attr in [
        ("t1_precision", "t1_precision"),
        ("t1_recall", "t1_recall"),
        ("t1_f1", "t1_f1"),
    ]:
        vals = get_vals(attr)
        lo, hi = bootstrap_ci(vals, mean, seed=seed)
        setattr(metrics, f"{field}_ci_lo", lo)
        setattr(metrics, f"{field}_ci_hi", hi)

    # T2 CIs
    for field, attr in [
        ("t2_precision", "t2_precision"),
        ("t2_recall", "t2_recall"),
        ("t2_f1", "t2_f1"),
    ]:
        vals = get_vals(attr)
        lo, hi = bootstrap_ci(vals, mean, seed=seed)
        setattr(metrics, f"{field}_ci_lo", lo)
        setattr(metrics, f"{field}_ci_hi", hi)

    return metrics


def mcnemar_p_value(
    n01: int, n10: int, two_tailed: bool = True
) -> float:
    """
    McNemar test p-value from discordant pair counts.

    n01: gold=1, pred=0 (false negatives)
    n10: gold=0, pred=1 (false positives)
    Uses normal approximation for large samples.
    """
    n = n01 + n10
    if n == 0:
        return 1.0
    import math

    z = abs(n01 - n10) / math.sqrt(n)
    # Two-tailed p-value via normal CDF approximation
    from math import erfc, sqrt

    p = erfc(z / sqrt(2))
    return round(p, 6)
