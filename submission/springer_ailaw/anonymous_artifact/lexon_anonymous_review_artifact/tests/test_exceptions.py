"""
Tests for exception handling semantics.

Property: exceptionFired(O, S) when ANY exception condition is satisfied
(disjunctive exception semantics).  Fired exception suppresses applicability.
"""

from lexon.reasoning.engine import LexonEngine
from lexon.schemas import (
    Actor,
    ApplicabilityStatus,
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


def _make_profile(**kwargs) -> SystemProfile:
    props = {
        "isDeployed": True,
        "affectsNaturalPerson": True,
        "hasResearchExemption": False,
        "isExclusiveSelfUse": False,
        "hasSystemicRisk": False,
        "processesSpecialCategory": False,
        "logsUnderControl": False,
    }
    props.update(kwargs.pop("properties", {}))
    return SystemProfile(
        system_id="SYS-TEST",
        risk_level=kwargs.get("risk_level", RiskLevel.HIGH_RISK),
        domain=kwargs.get("domain", Domain.GENERAL),
        actor=kwargs.get("actor", Actor.PROVIDER),
        deployment_context=kwargs.get("deployment_context", DeploymentContext.EU_MARKET),
        properties=props,
        evidence_held=[],
        profile_complete=True,
    )


def _clause(obl: Obligation) -> RegulatoryClause:
    return RegulatoryClause(
        clause_id="CL-EXC",
        text="Test",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obl],
    )


def _obl(exc_list, cond_list=None) -> Obligation:
    return Obligation(
        obligation_id="O-EXC",
        clause_id="CL-EXC",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=cond_list or [],
        exceptions=exc_list,
        required_evidence=[],
    )


def test_exception_fires_suppresses_applicability():
    """When research exemption applies, obligation is NotApplicable."""
    obl = _obl(
        cond_list=[Condition(condition_id="C1", predicate="risk_level", value="HighRisk")],
        exc_list=[ExceptionCondition(
            exception_id="X1", predicate="hasResearchExemption", value=True
        )],
    )
    profile = _make_profile(properties={"hasResearchExemption": True, "isDeployed": True,
                                        "affectsNaturalPerson": False, "isExclusiveSelfUse": False,
                                        "hasSystemicRisk": False, "processesSpecialCategory": False,
                                        "logsUnderControl": False})
    result = engine.reason(_clause(obl), profile, "I-EXC-1")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE
    assert "X1" in result.activation_traces[0].exceptions_fired


def test_exception_not_fired_when_condition_false():
    """When exception condition is False, obligation proceeds to condition check."""
    obl = _obl(
        cond_list=[Condition(condition_id="C1", predicate="risk_level", value="HighRisk")],
        exc_list=[ExceptionCondition(
            exception_id="X1", predicate="hasResearchExemption", value=True
        )],
    )
    profile = _make_profile()  # hasResearchExemption=False
    result = engine.reason(_clause(obl), profile, "I-EXC-2")
    assert result.activation_traces[0].status == ApplicabilityStatus.APPLICABLE


def test_disjunctive_exceptions_any_fires():
    """Two exceptions: if first fires, obligation is suppressed regardless of second."""
    obl = _obl(
        cond_list=[],
        exc_list=[
            ExceptionCondition(exception_id="X1", predicate="hasResearchExemption", value=True),
            ExceptionCondition(exception_id="X2", predicate="isExclusiveSelfUse", value=True),
        ],
    )
    profile = _make_profile(
        properties={"hasResearchExemption": True, "isExclusiveSelfUse": False,
                    "isDeployed": True, "affectsNaturalPerson": False,
                    "hasSystemicRisk": False, "processesSpecialCategory": False,
                    "logsUnderControl": False}
    )
    result = engine.reason(_clause(obl), profile, "I-EXC-3")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE


def test_adding_exception_facts_retracts_applicability():
    """
    Property 2 (non-monotone): adding exception-satisfying facts can retract Applicable.
    """
    obl = _obl(
        cond_list=[Condition(condition_id="C1", predicate="risk_level", value="HighRisk")],
        exc_list=[ExceptionCondition(exception_id="X1", predicate="isExclusiveSelfUse", value=True)],
    )
    base_profile = _make_profile()
    result_before = engine.reason(_clause(obl), base_profile, "I-EXC-4a")
    assert result_before.activation_traces[0].status == ApplicabilityStatus.APPLICABLE

    # Add exception-satisfying fact
    extended_props = dict(base_profile.properties)
    extended_props["isExclusiveSelfUse"] = True
    extended_profile = base_profile.model_copy(update={"properties": extended_props})
    result_after = engine.reason(_clause(obl), extended_profile, "I-EXC-4b")
    assert result_after.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE


def test_real_cl001_research_exemption():
    """Integration: CL-001 research-exempt profile (SYS-005) → NotApplicable."""
    from lexon.benchmark.generate_synthetic import generate
    clauses, profiles, _ = generate()
    clause = next(c for c in clauses if c.clause_id == "CL-001")
    profile = next(p for p in profiles if p.system_id == "SYS-005")  # research exempt
    result = engine.reason(clause, profile, "INT-CL001-SYS005")
    # SYS-005 has hasResearchExemption=True → exception fires
    for trace in result.activation_traces:
        assert trace.status == ApplicabilityStatus.NOT_APPLICABLE, (
            f"Expected NOT_APPLICABLE for research-exempt profile, got {trace.status}"
        )
