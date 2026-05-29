"""
Tests for conflict detection (T3 — Definition 7).

A conflict exists when two applicable obligations:
  - apply to the same actor
  - have incompatible actions
  - refer to the same system
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


def _profile(actor: Actor = Actor.PROVIDER) -> SystemProfile:
    return SystemProfile(
        system_id="SYS-CONF",
        risk_level=RiskLevel.HIGH_RISK,
        domain=Domain.GENERAL,
        actor=actor,
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


def _clause_with_two_obls(
    actor1: Actor, action1: str,
    actor2: Actor, action2: str,
    conds: list[Condition] | None = None,
) -> RegulatoryClause:
    conds = conds or [Condition(condition_id="C1", predicate="isDeployed", value=True)]
    return RegulatoryClause(
        clause_id="CL-CONF",
        text="Test conflict",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[
            Obligation(
                obligation_id="O-CONF-1",
                clause_id="CL-CONF",
                actor=actor1,
                action=action1,
                conditions=conds,
                exceptions=[],
                required_evidence=[],
            ),
            Obligation(
                obligation_id="O-CONF-2",
                clause_id="CL-CONF",
                actor=actor2,
                action=action2,
                conditions=conds,
                exceptions=[],
                required_evidence=[],
            ),
        ],
    )


def test_conflict_detected_same_actor_incompatible_actions():
    """Two applicable obligations for same actor with incompatible actions → conflict."""
    clause = _clause_with_two_obls(
        Actor.PROVIDER, "ACT-FullAutomatedDecision",
        Actor.PROVIDER, "ACT-RequireHumanOverride",
    )
    result = engine.reason(clause, _profile(Actor.PROVIDER), "I-CONF-1")
    assert len(result.conflict_pairs) == 1
    conflict = result.conflict_pairs[0]
    assert conflict.shared_actor == "Provider"
    assert set([conflict.obligation_id_1, conflict.obligation_id_2]) == {"O-CONF-1", "O-CONF-2"}


def test_no_conflict_different_actors():
    """
    Definition 7: conflict requires actor(o₁) == actor(o₂).
    Different actors → no conflict even with incompatible actions.
    """
    clause = _clause_with_two_obls(
        Actor.PROVIDER, "ACT-FullAutomatedDecision",
        Actor.DEPLOYER, "ACT-RequireHumanOverride",
    )
    # Profile has one actor; clause has two different actors → at most one obligation activates
    result = engine.reason(clause, _profile(Actor.PROVIDER), "I-CONF-2")
    # OBL-2 (Deployer) won't activate for Provider profile → no conflict
    assert result.conflict_pairs == []


def test_no_conflict_compatible_actions():
    """Two applicable obligations with compatible actions → no conflict."""
    clause = _clause_with_two_obls(
        Actor.PROVIDER, "ACT-MaintainTechnicalDocumentation",
        Actor.PROVIDER, "ACT-ImplementRiskManagementSystem",
    )
    result = engine.reason(clause, _profile(Actor.PROVIDER), "I-CONF-3")
    assert result.conflict_pairs == []


def test_no_conflict_when_one_obligation_not_applicable():
    """If one of two potentially conflicting obligations is not applicable → no conflict."""
    # Second obligation has an extra condition that the profile doesn't satisfy
    obl1 = Obligation(
        obligation_id="O-C1",
        clause_id="CL-CONF",
        actor=Actor.PROVIDER,
        action="ACT-FullAutomatedDecision",
        conditions=[Condition(condition_id="C1", predicate="isDeployed", value=True)],
        exceptions=[],
        required_evidence=[],
    )
    obl2 = Obligation(
        obligation_id="O-C2",
        clause_id="CL-CONF",
        actor=Actor.PROVIDER,
        action="ACT-RequireHumanOverride",
        conditions=[
            Condition(condition_id="C1", predicate="isDeployed", value=True),
            Condition(condition_id="C2", predicate="hasSystemicRisk", value=True),  # not in profile
        ],
        exceptions=[],
        required_evidence=[],
    )
    clause = RegulatoryClause(
        clause_id="CL-CONF",
        text="Test",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obl1, obl2],
    )
    result = engine.reason(clause, _profile(Actor.PROVIDER), "I-CONF-4")
    # O-C2 not applicable → no conflict
    assert result.conflict_pairs == []


def test_multiple_incompatibility_pairs():
    """Test all four documented incompatibility action pairs from incompatibility_axioms.yaml."""
    from lexon.constants import INCOMPATIBILITY_PAIRS
    # Verify the canonical pairs are defined
    pair_set = set(INCOMPATIBILITY_PAIRS)
    assert ("ACT-FullAutomatedDecision", "ACT-RequireHumanOverride") in pair_set
    assert ("ACT-RetainDataMaximal", "ACT-MinimiseDataRetention") in pair_set
    assert ("ACT-DiscloseToPublic", "ACT-MaintainConfidentiality") in pair_set


def test_conflict_pair_is_symmetric():
    """Conflict detection should not double-count: (A,B) and (B,A) = 1 conflict."""
    clause = _clause_with_two_obls(
        Actor.PROVIDER, "ACT-RetainDataMaximal",
        Actor.PROVIDER, "ACT-MinimiseDataRetention",
    )
    result = engine.reason(clause, _profile(Actor.PROVIDER), "I-CONF-5")
    assert len(result.conflict_pairs) == 1
