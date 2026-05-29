"""Validation helpers for benchmark integrity checks."""

from __future__ import annotations

from lexon.schemas import BenchmarkInstance, GoldLabels, RegulatoryClause, SystemProfile


def validate_benchmark(
    clauses: list[RegulatoryClause],
    profiles: list[SystemProfile],
    instances: list[BenchmarkInstance],
    gold_labels: list[GoldLabels],
) -> list[str]:
    """
    Validate benchmark integrity.  Returns a list of error messages (empty = OK).
    """
    errors: list[str] = []

    if len(clauses) != 25:
        errors.append(f"Expected 25 clauses, found {len(clauses)}")
    if len(profiles) != 30:
        errors.append(f"Expected 30 profiles, found {len(profiles)}")
    if len(instances) != 750:
        errors.append(f"Expected 750 instances, found {len(instances)}")
    if len(gold_labels) != 750:
        errors.append(f"Expected 750 gold labels, found {len(gold_labels)}")

    # Verify split proportions are approximately correct
    train_n = sum(1 for i in instances if i.split == "train")
    dev_n = sum(1 for i in instances if i.split == "dev")
    test_n = sum(1 for i in instances if i.split == "test")
    if not (420 <= train_n <= 470):
        errors.append(f"Train split size {train_n} outside expected range [420, 470]")
    if not (125 <= dev_n <= 175):
        errors.append(f"Dev split size {dev_n} outside expected range [125, 175]")
    if not (125 <= test_n <= 175):
        errors.append(f"Test split size {test_n} outside expected range [125, 175]")

    # Verify ambiguous clause count
    ambiguous_clauses = [c for c in clauses if c.ambiguity_flag]
    if len(ambiguous_clauses) != 8:
        errors.append(f"Expected 8 ambiguous clauses, found {len(ambiguous_clauses)}")

    # Verify no placeholder text in gold labels
    for gl in gold_labels:
        if any(
            tok in gl.canonical_notes
            for tok in ["[EXT]", "TODO", "TBD", "camera-ready", "planned experiment"]
        ):
            errors.append(f"Placeholder text found in gold label {gl.instance_id}")

    return errors
