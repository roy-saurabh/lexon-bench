"""Tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError

from lexon.schemas import (
    Actor,
    ApplicabilityStatus,
    BenchmarkInstance,
    Condition,
    DifficultyLevel,
    EvidenceSpec,
    ExceptionCondition,
    GoldLabels,
    Obligation,
    RegulatoryClause,
    RiskLevel,
    SourceInstrument,
    SystemProfile,
)


def test_obligation_roundtrip():
    """Obligation can be serialised and deserialised."""
    obl = Obligation(
        obligation_id="OBL-001-1",
        clause_id="CL-001",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[Condition(condition_id="C1", predicate="risk_level", value="HighRisk")],
        exceptions=[ExceptionCondition(exception_id="X1", predicate="hasResearchExemption", value=True)],
        required_evidence=[EvidenceSpec(evidence_id="E-TechnicalDocumentation")],
        source_instrument=SourceInstrument.SYNTHETIC,
    )
    data = obl.model_dump_json()
    obl2 = Obligation.model_validate_json(data)
    assert obl2.obligation_id == obl.obligation_id
    assert obl2.actor == obl.actor
    assert len(obl2.conditions) == 1


def test_system_profile_defaults():
    """SystemProfile has sensible defaults."""
    p = SystemProfile(system_id="SYS-001")
    assert p.risk_level == RiskLevel.MINIMAL_RISK
    assert p.profile_complete is True
    assert p.evidence_held == []


def test_gold_labels_roundtrip():
    """GoldLabels with nested types can roundtrip JSON."""
    gl = GoldLabels(
        instance_id="B-001",
        clause_id="CL-001",
        system_id="SYS-001",
        activation={"OBL-001": ApplicabilityStatus.APPLICABLE},
        evidence_gaps={"OBL-001": ["E-TechnicalDocumentation"]},
        conflict_pairs=[("OBL-001", "OBL-002")],
        remediation_candidates=["E-TechnicalDocumentation"],
    )
    data = gl.model_dump_json()
    gl2 = GoldLabels.model_validate_json(data)
    assert gl2.activation["OBL-001"] == ApplicabilityStatus.APPLICABLE
    assert "E-TechnicalDocumentation" in gl2.evidence_gaps["OBL-001"]


def test_benchmark_instance_fields():
    """BenchmarkInstance has required fields."""
    inst = BenchmarkInstance(
        instance_id="BENCH-CL-001-SYS-001",
        clause_id="CL-001",
        system_id="SYS-001",
        split="test",
        difficulty=DifficultyLevel.EASY,
    )
    assert inst.split == "test"
    assert inst.ambiguous is False


def test_full_benchmark_schema_valid():
    """All 750 generated instances pass schema validation."""
    from lexon.benchmark.generate_synthetic import generate
    clauses, profiles, instances = generate()
    # Pydantic validation happens at construction time; if we're here, it passed
    assert len(instances) == 750
    for inst in instances[:10]:
        assert inst.split in ("train", "dev", "test")
