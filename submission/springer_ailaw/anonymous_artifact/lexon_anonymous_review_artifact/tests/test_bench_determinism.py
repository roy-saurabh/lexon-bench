"""
Tests for deterministic benchmark generation.

Property: generating the benchmark twice with seed=42 produces
identical clauses, profiles, instances, and gold labels.
"""

import pytest
from lexon.benchmark.generate_synthetic import generate
from lexon.benchmark.gold import generate_all_gold_labels
from lexon.constants import RANDOM_SEED


def test_benchmark_generation_is_deterministic():
    """Two calls to generate() with same seed produce identical outputs."""
    clauses1, profiles1, instances1 = generate(seed=RANDOM_SEED)
    clauses2, profiles2, instances2 = generate(seed=RANDOM_SEED)

    assert len(clauses1) == len(clauses2)
    assert len(profiles1) == len(profiles2)
    assert len(instances1) == len(instances2)

    for c1, c2 in zip(clauses1, clauses2):
        assert c1.clause_id == c2.clause_id
        assert len(c1.obligations) == len(c2.obligations)

    for p1, p2 in zip(profiles1, profiles2):
        assert p1.system_id == p2.system_id
        assert p1.risk_level == p2.risk_level
        assert p1.evidence_held == p2.evidence_held

    for i1, i2 in zip(instances1, instances2):
        assert i1.instance_id == i2.instance_id
        assert i1.split == i2.split


def test_gold_labels_deterministic():
    """Gold labels are deterministic given the same benchmark."""
    clauses, profiles, instances = generate(seed=RANDOM_SEED)
    ci = {c.clause_id: c for c in clauses}
    pi = {p.system_id: p for p in profiles}

    gold1 = generate_all_gold_labels(instances, ci, pi)
    gold2 = generate_all_gold_labels(instances, ci, pi)

    assert len(gold1) == len(gold2)
    for g1, g2 in zip(gold1, gold2):
        assert g1.instance_id == g2.instance_id
        assert g1.activation == g2.activation
        assert g1.evidence_gaps == g2.evidence_gaps


def test_different_seeds_produce_different_splits():
    """Different seeds may produce different train/dev/test assignments."""
    _, _, instances42 = generate(seed=42)
    _, _, instances99 = generate(seed=99)
    splits42 = {i.instance_id: i.split for i in instances42}
    splits99 = {i.instance_id: i.split for i in instances99}
    # At least some instances should differ (shuffled differently)
    diffs = sum(1 for iid in splits42 if splits42[iid] != splits99.get(iid, ""))
    assert diffs > 0, "Different seeds should produce different shuffles"


def test_benchmark_counts():
    """Verify exact counts: 25 clauses, 30 profiles, 750 instances."""
    clauses, profiles, instances = generate()
    assert len(clauses) == 25
    assert len(profiles) == 30
    assert len(instances) == 750


def test_benchmark_split_counts():
    """Verify train/dev/test split counts are approximately 450/150/150."""
    _, _, instances = generate()
    train = sum(1 for i in instances if i.split == "train")
    dev = sum(1 for i in instances if i.split == "dev")
    test = sum(1 for i in instances if i.split == "test")
    assert train + dev + test == 750
    # Expect approximately 60/20/20 with small rounding
    assert 400 <= train <= 500
    assert 100 <= dev <= 200
    assert 100 <= test <= 200


def test_ambiguous_clause_count():
    """Exactly 8 clauses carry ambiguity_flag=True."""
    clauses, _, _ = generate()
    ambiguous = [c for c in clauses if c.ambiguity_flag]
    assert len(ambiguous) == 8


@pytest.mark.determinism
def test_lexon_predictions_deterministic():
    """Running LEXON on the same instances twice gives identical results."""
    from lexon.reasoning.engine import LexonEngine
    clauses, profiles, instances = generate()
    ci = {c.clause_id: c for c in clauses}
    pi = {p.system_id: p for p in profiles}
    engine = LexonEngine()

    test_insts = [i for i in instances if i.split == "test"][:20]
    results1 = [engine.reason(ci[i.clause_id], pi[i.system_id], i.instance_id)
                for i in test_insts]
    results2 = [engine.reason(ci[i.clause_id], pi[i.system_id], i.instance_id)
                for i in test_insts]

    for r1, r2 in zip(results1, results2):
        assert r1.instance_id == r2.instance_id
        assert len(r1.activation_traces) == len(r2.activation_traces)
        for t1, t2 in zip(r1.activation_traces, r2.activation_traces):
            assert t1.status == t2.status
        assert len(r1.evidence_gaps) == len(r2.evidence_gaps)
