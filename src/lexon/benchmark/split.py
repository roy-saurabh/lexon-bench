"""Deterministic train/dev/test split for benchmark instances."""

from __future__ import annotations

import random

from lexon.constants import DEV_FRACTION, RANDOM_SEED, TEST_FRACTION, TRAIN_FRACTION
from lexon.schemas import BenchmarkInstance


def assign_splits(
    instances: list[BenchmarkInstance],
    rng: random.Random | None = None,
) -> list[BenchmarkInstance]:
    """
    Assign train/dev/test splits deterministically.

    Stratifies by ambiguous flag to ensure ambiguous instances appear in all splits.
    Split fractions: 60/20/20.  Seed is fixed via RANDOM_SEED.
    """
    if rng is None:
        rng = random.Random(RANDOM_SEED)

    ambiguous = [i for i in instances if i.ambiguous]
    unambiguous = [i for i in instances if not i.ambiguous]

    def _split(items: list[BenchmarkInstance]) -> list[BenchmarkInstance]:
        shuffled = list(items)
        rng.shuffle(shuffled)
        n = len(shuffled)
        n_train = int(n * TRAIN_FRACTION)
        n_dev = int(n * DEV_FRACTION)
        for inst in shuffled[:n_train]:
            inst.split = "train"
        for inst in shuffled[n_train: n_train + n_dev]:
            inst.split = "dev"
        for inst in shuffled[n_train + n_dev:]:
            inst.split = "test"
        return shuffled

    result = _split(unambiguous) + _split(ambiguous)
    result.sort(key=lambda i: i.instance_id)
    return result


def get_split_ids(
    instances: list[BenchmarkInstance], split: str
) -> list[str]:
    return sorted(i.instance_id for i in instances if i.split == split)
