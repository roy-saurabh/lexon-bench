"""
Tests for correct universal (all-conditions) activation semantics.

Property: Applicable(O, S) iff ALL conditions in Cₒ are satisfied AND
no exception fires.  A single satisfied condition is insufficient.
"""

import pytest
from lexon.reasoning.engine import LexonEngine
from lexon.schemas import (
    Actor,
    ApplicabilityStatus,
    Capability,
    Condition,
    DeploymentContext,
    Domain,
    EvidenceSpec,
    Obligation,
    RegulatoryClause,
    RiskLevel,
    SourceInstrument,
    SystemProfile,
)


def _make_clause(obligation: Obligation) -> RegulatoryClause:
    return RegulatoryClause(
        clause_id="CL-TEST",
        text="Test clause",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obligation],
    )


def _make_profile(**props) -> SystemProfile:
    defaults = dict(
        system_id="SYS-TEST",
        risk_level=RiskLevel.HIGH_RISK,
        domain=Domain.HEALTHCARE,
        actor=Actor.PROVIDER,
        deployment_context=DeploymentContext.EU_MARKET,
        properties={
            "isDeployed": True,
            "affectsNaturalPerson": True,
            "hasResearchExemption": False,
            "isExclusiveSelfUse": False,
            "hasSystemicRisk": False,
            "processesSpecialCategory": False,
            "logsUnderControl": False,
        },
        evidence_held=[],
        profile_complete=True,
    )
    defaults.update(props)
    return SystemProfile(**defaults)


engine = LexonEngine()


def test_all_conditions_satisfied_yields_applicable():
    """When ALL conditions hold, obligation is Applicable."""
    obl = Obligation(
        obligation_id="O-1",
        clause_id="CL-TEST",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[
            Condition(condition_id="C1", predicate="risk_level", value="HighRisk"),
            Condition(condition_id="C2", predicate="isDeployed", value=True),
        ],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile()
    result = engine.reason(_make_clause(obl), profile, "INST-001")
    assert result.activation_traces[0].status == ApplicabilityStatus.APPLICABLE


def test_one_condition_satisfied_insufficient():
    """Single satisfied condition out of two is NOT sufficient — must be ALL."""
    obl = Obligation(
        obligation_id="O-2",
        clause_id="CL-TEST",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[
            Condition(condition_id="C1", predicate="risk_level", value="HighRisk"),
            Condition(condition_id="C2", predicate="isDeployed", value=True),
            # Third condition: processesSpecialCategory — not satisfied
            Condition(condition_id="C3", predicate="processesSpecialCategory", value=True),
        ],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile(
        properties={
            "isDeployed": True,
            "affectsNaturalPerson": True,
            "hasResearchExemption": False,
            "isExclusiveSelfUse": False,
            "hasSystemicRisk": False,
            "processesSpecialCategory": False,  # NOT satisfied
            "logsUnderControl": False,
        }
    )
    result = engine.reason(_make_clause(obl), profile, "INST-002")
    trace = result.activation_traces[0]
    assert trace.status == ApplicabilityStatus.NOT_APPLICABLE
    assert "C3" in trace.conditions_missing


def test_no_conditions_yields_applicable():
    """Obligation with empty condition set is unconditionally applicable (for matching actor)."""
    obl = Obligation(
        obligation_id="O-3",
        clause_id="CL-TEST",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile()
    result = engine.reason(_make_clause(obl), profile, "INST-003")
    assert result.activation_traces[0].status == ApplicabilityStatus.APPLICABLE


def test_three_conditions_two_satisfied_not_applicable():
    """2-of-3 conditions satisfied → NotApplicable (universal semantics)."""
    obl = Obligation(
        obligation_id="O-4",
        clause_id="CL-TEST",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[
            Condition(condition_id="C1", predicate="risk_level", value="HighRisk"),
            Condition(condition_id="C2", predicate="isDeployed", value=True),
            Condition(condition_id="C3", predicate="hasSystemicRisk", value=True),  # False in profile
        ],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile()  # hasSystemicRisk=False
    result = engine.reason(_make_clause(obl), profile, "INST-004")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE


def test_negated_condition_satisfied_when_value_absent():
    """Negated condition C(NOT p=v) is satisfied when profile has p≠v."""
    obl = Obligation(
        obligation_id="O-5",
        clause_id="CL-TEST",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[
            Condition(condition_id="C1", predicate="risk_level", value="MinimalRisk",
                      negated=True),  # NOT MinimalRisk — HighRisk profile → satisfied
        ],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile()  # risk_level=HighRisk
    result = engine.reason(_make_clause(obl), profile, "INST-005")
    assert result.activation_traces[0].status == ApplicabilityStatus.APPLICABLE


def test_actor_mismatch_yields_not_applicable():
    """Obligation requires Deployer; Provider profile → NotApplicable."""
    obl = Obligation(
        obligation_id="O-6",
        clause_id="CL-TEST",
        actor=Actor.DEPLOYER,
        action="ACT-Test",
        conditions=[],
        exceptions=[],
        required_evidence=[],
    )
    profile = _make_profile()  # actor=Provider
    result = engine.reason(_make_clause(obl), profile, "INST-006")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE


def test_full_benchmark_clause_activation():
    """Integration test: CL-002 activates for HighRisk deployed provider profile."""
    from lexon.benchmark.generate_synthetic import generate
    clauses, profiles, _ = generate()
    clause = next(c for c in clauses if c.clause_id == "CL-002")
    profile = next(p for p in profiles if p.system_id == "SYS-007")  # HighRisk Provider
    result = engine.reason(clause, profile, "TEST-CL002-SYS007")
    applicable = [t for t in result.activation_traces if t.status == ApplicabilityStatus.APPLICABLE]
    assert len(applicable) >= 1, "CL-002 should activate for HighRisk deployed Provider"
