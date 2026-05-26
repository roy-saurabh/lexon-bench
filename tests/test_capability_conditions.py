"""
Tests for capability-predicate condition and exception evaluation.

Reviewer C2: capability conditions in obligations and exceptions were previously
unevaluated because the engine only checked profile.properties, not
profile.capabilities.  These tests guard against regression.
"""

from lexon.benchmark.generate_synthetic import generate
from lexon.benchmark.gold import GoldOracle
from lexon.reasoning.engine import LexonEngine
from lexon.schemas import (
    Actor,
    ApplicabilityStatus,
    BenchmarkInstance,
    Capability,
    Condition,
    DeploymentContext,
    Domain,
    ExceptionCondition,
    Obligation,
    RegulatoryClause,
    RiskLevel,
    SourceInstrument,
    SystemProfile,
)

engine = LexonEngine()
oracle = GoldOracle()


def _profile(caps: list[Capability], **kwargs) -> SystemProfile:
    props = {
        "isDeployed": True,
        "affectsNaturalPerson": True,
        "hasResearchExemption": False,
        "isExclusiveSelfUse": False,
        "hasSystemicRisk": False,
        "processesSpecialCategory": False,
        "logsUnderControl": False,
    }
    return SystemProfile(
        system_id="SYS-CAP-TEST",
        risk_level=kwargs.get("risk_level", RiskLevel.HIGH_RISK),
        domain=kwargs.get("domain", Domain.GENERAL),
        actor=kwargs.get("actor", Actor.PROVIDER),
        deployment_context=kwargs.get("deployment_context", DeploymentContext.EU_MARKET),
        capabilities=caps,
        properties=props,
        evidence_held=[],
        profile_complete=True,
    )


def _clause(obl: Obligation) -> RegulatoryClause:
    return RegulatoryClause(
        clause_id="CL-CAP",
        text="Test capability clause",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obl],
    )


def _obl(cond_list=None, exc_list=None) -> Obligation:
    return Obligation(
        obligation_id="O-CAP",
        clause_id="CL-CAP",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=cond_list or [],
        exceptions=exc_list or [],
        required_evidence=[],
    )


def test_capability_condition_true_when_capability_present():
    """Engine: capability condition satisfied when profile holds that capability."""
    obl = _obl(cond_list=[
        Condition(condition_id="C-CAP-1", predicate="capability", value="NLP"),
    ])
    profile = _profile(caps=[Capability.NLP])
    result = engine.reason(_clause(obl), profile, "I-CAP-1")
    assert result.activation_traces[0].status == ApplicabilityStatus.APPLICABLE, (
        f"Expected APPLICABLE when capability=NLP is present, got "
        f"{result.activation_traces[0].status}"
    )


def test_capability_condition_false_when_capability_absent():
    """Engine: capability condition not satisfied when profile lacks the capability."""
    obl = _obl(cond_list=[
        Condition(condition_id="C-CAP-2", predicate="capability", value="NLP"),
    ])
    profile = _profile(caps=[Capability.CLASSIFICATION])
    result = engine.reason(_clause(obl), profile, "I-CAP-2")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE, (
        f"Expected NOT_APPLICABLE when capability=NLP is absent, got "
        f"{result.activation_traces[0].status}"
    )


def test_capability_exception_fires_when_capability_present():
    """Engine: exception with capability predicate fires when profile has the capability."""
    obl = _obl(
        cond_list=[Condition(condition_id="C-CAP-3", predicate="risk_level", value="HighRisk")],
        exc_list=[ExceptionCondition(
            exception_id="X-CAP-1", predicate="capability", value="GenerativeAI"
        )],
    )
    profile = _profile(caps=[Capability.GENERATIVE_AI])
    result = engine.reason(_clause(obl), profile, "I-CAP-3")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE, (
        f"Expected NOT_APPLICABLE when GenerativeAI exception fires, got "
        f"{result.activation_traces[0].status}"
    )
    assert "X-CAP-1" in result.activation_traces[0].exceptions_fired


def test_genai_exception_for_cl018_fires_for_generative_profile():
    """Integration: CL-018 GenAI exception suppresses activation for GenerativeAI profiles."""
    clauses, profiles, instances = generate()
    clause = next(c for c in clauses if c.clause_id == "CL-018")
    # SYS-004 is the GenerativeAI profile (group 1, hard-coded by generator seed=42)
    genai_profiles = [p for p in profiles if Capability.GENERATIVE_AI in p.capabilities]
    assert genai_profiles, "Expected at least one GenerativeAI profile in benchmark"

    for profile in genai_profiles:
        result = engine.reason(clause, profile, f"INT-CL018-{profile.system_id}")
        # The GenAI exception (X-018-1) must suppress OBL-018-1 for GenAI profiles
        for trace in result.activation_traces:
            if trace.obligation_id == "OBL-018-1":
                assert trace.status == ApplicabilityStatus.NOT_APPLICABLE, (
                    f"CL-018/OBL-018-1 must be NOT_APPLICABLE for GenerativeAI profile "
                    f"{profile.system_id}, got {trace.status}"
                )
