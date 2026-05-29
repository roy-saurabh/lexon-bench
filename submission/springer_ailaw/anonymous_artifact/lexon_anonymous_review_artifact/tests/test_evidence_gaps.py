"""
Tests for evidence gap detection (T2).

Properties tested:
  - Gap(o,S) = Eₒ \\ E_held (CWA over evidence holdings)
  - Adding evidence never increases gaps (Property 3: anti-monotonicity)
  - Gap is empty for non-applicable obligations
  - Gap is exactly the missing evidence for applicable obligations
"""

from lexon.reasoning.engine import LexonEngine
from lexon.schemas import (
    Actor,
    ApplicabilityStatus,
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

engine = LexonEngine()


def _profile(evidence_held: list[str], **props) -> SystemProfile:
    p = {
        "isDeployed": True,
        "affectsNaturalPerson": True,
        "hasResearchExemption": False,
        "isExclusiveSelfUse": False,
        "hasSystemicRisk": False,
        "processesSpecialCategory": False,
        "logsUnderControl": False,
    }
    p.update(props)
    return SystemProfile(
        system_id="SYS-GAP",
        risk_level=RiskLevel.HIGH_RISK,
        domain=Domain.GENERAL,
        actor=Actor.PROVIDER,
        deployment_context=DeploymentContext.EU_MARKET,
        properties=p,
        evidence_held=evidence_held,
        profile_complete=True,
    )


def _clause(evidence_ids: list[str]) -> RegulatoryClause:
    obl = Obligation(
        obligation_id="O-GAP",
        clause_id="CL-GAP",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[Condition(condition_id="C1", predicate="risk_level", value="HighRisk")],
        exceptions=[],
        required_evidence=[EvidenceSpec(evidence_id=eid) for eid in evidence_ids],
    )
    return RegulatoryClause(
        clause_id="CL-GAP",
        text="Test",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obl],
    )


def test_gap_is_required_minus_held():
    """Gap = Eₒ \\ E_held: missing evidence correctly identified."""
    required = ["E-TechnicalDocumentation", "E-RiskAssessment", "E-SystemCard"]
    held = ["E-TechnicalDocumentation"]
    expected_gaps = {"E-RiskAssessment", "E-SystemCard"}

    result = engine.reason(_clause(required), _profile(held), "I-GAP-1")
    gap_ids = {g.evidence_id for g in result.evidence_gaps}
    assert gap_ids == expected_gaps


def test_no_gap_when_all_evidence_held():
    """When all required evidence is held, gap set is empty."""
    required = ["E-TechnicalDocumentation", "E-RiskAssessment"]
    held = ["E-TechnicalDocumentation", "E-RiskAssessment", "E-SystemCard"]
    result = engine.reason(_clause(required), _profile(held), "I-GAP-2")
    assert result.evidence_gaps == []


def test_full_gap_when_no_evidence_held():
    """When no evidence is held, gap = all required evidence."""
    required = ["E-TechnicalDocumentation", "E-RiskAssessment", "E-SystemCard"]
    result = engine.reason(_clause(required), _profile([]), "I-GAP-3")
    gap_ids = {g.evidence_id for g in result.evidence_gaps}
    assert gap_ids == set(required)


def test_adding_evidence_never_increases_gaps():
    """
    Property 3 (anti-monotonicity): adding held evidence reduces or preserves gaps.
    """
    required = ["E-TechnicalDocumentation", "E-RiskAssessment", "E-SystemCard"]

    prev_gaps = None
    for n_held in range(len(required) + 1):
        held = required[:n_held]
        result = engine.reason(_clause(required), _profile(held), f"I-MONO-{n_held}")
        curr_gaps = {g.evidence_id for g in result.evidence_gaps}
        if prev_gaps is not None:
            assert len(curr_gaps) <= len(prev_gaps), (
                f"Adding evidence increased gaps from {len(prev_gaps)} to {len(curr_gaps)}"
            )
        prev_gaps = curr_gaps


def test_gap_only_for_applicable_obligations():
    """Evidence gaps are computed only for Applicable obligations."""
    # Make obligation NotApplicable by failing a condition
    obl = Obligation(
        obligation_id="O-NA",
        clause_id="CL-NAGAP",
        actor=Actor.PROVIDER,
        action="ACT-Test",
        conditions=[
            Condition(condition_id="C1", predicate="risk_level", value="HighRisk"),
            Condition(condition_id="C2", predicate="processesSpecialCategory", value=True),
        ],
        exceptions=[],
        required_evidence=[EvidenceSpec(evidence_id="E-PrivacyImpactAssessment")],
    )
    clause = RegulatoryClause(
        clause_id="CL-NAGAP",
        text="Test",
        source_instrument=SourceInstrument.SYNTHETIC,
        obligations=[obl],
    )
    profile = _profile(
        evidence_held=[],
        processesSpecialCategory=False  # condition NOT satisfied
    )
    result = engine.reason(clause, profile, "I-NAGAP")
    assert result.activation_traces[0].status == ApplicabilityStatus.NOT_APPLICABLE
    assert result.evidence_gaps == [], "No gaps for non-applicable obligations"


def test_gap_detection_cwa_strict():
    """CWA: evidence not in evidence_held is treated as absent, even if it 'probably' exists."""
    required = ["E-TechnicalDocumentation"]
    # Even though system is a HighRisk Provider, if E-TechnicalDocumentation is not listed
    # in evidence_held, it must be reported as a gap.
    result = engine.reason(_clause(required), _profile([]), "I-CWA")
    assert len(result.evidence_gaps) == 1
    assert result.evidence_gaps[0].evidence_id == "E-TechnicalDocumentation"


def test_real_benchmark_gap_detection():
    """Integration: SYS-008 (HighRisk, Biometric+DecisionSupport) has evidence gaps for CL-007."""
    from lexon.benchmark.generate_synthetic import generate
    clauses, profiles, _ = generate()
    clause = next(c for c in clauses if c.clause_id == "CL-007")  # Risk management
    profile = next(p for p in profiles if p.system_id == "SYS-008")
    result = engine.reason(clause, profile, "INT-CL007-SYS008")
    # SYS-008 has limited evidence — should have some gaps
    applicable = [t for t in result.activation_traces if t.status == ApplicabilityStatus.APPLICABLE]
    if applicable:
        held = set(profile.evidence_held)
        obl_by_id = {o.obligation_id: o for o in clause.obligations}
        for t in applicable:
            obl = obl_by_id[t.obligation_id]
            expected_gaps = {e.evidence_id for e in obl.required_evidence} - held
            actual_gaps = {g.evidence_id for g in result.evidence_gaps
                         if g.obligation_id == t.obligation_id}
            assert actual_gaps == expected_gaps, (
                f"Gap mismatch for {t.obligation_id}: expected {expected_gaps}, got {actual_gaps}"
            )
