"""
B1 — Static Checklist Baseline.

Applies obligations based only on risk level and broad domain.
Does NOT evaluate fine-grained conditions or exceptions.

This baseline represents the simplest deployed compliance tool:
a spreadsheet mapping risk levels to applicable obligations.
Its systematic weaknesses:
  - Over-activates on HighRisk profiles regardless of actor or deployment status
  - Ignores all exception conditions
  - Cannot detect evidence gaps (uses a fixed generic evidence list)
  - Cannot detect conflicts (no rule layer)
"""

from __future__ import annotations

from lexon.schemas import (
    ActivationTrace,
    ApplicabilityStatus,
    BenchmarkInstance,
    EvidenceGap,
    ReasoningResult,
    RegulatoryClause,
    RiskLevel,
    SystemProfile,
)

# Static checklist: which risk levels trigger each thematic group
_RISK_TRIGGERS: dict[str, set[str]] = {
    "Transparency and information": {"HighRisk", "LimitedRisk"},
    "Risk management and conformity assessment": {"HighRisk"},
    "Special-category data handling": {"HighRisk", "LimitedRisk"},
    "Human oversight and human-in-the-loop": {"HighRisk"},
    "Cross-instrument provisions": {"HighRisk"},
}

# Generic evidence items assumed present if risk level is triggered
_GENERIC_EVIDENCE: set[str] = {
    "E-TechnicalDocumentation",
    "E-RiskAssessment",
    "E-SystemCard",
}


class ChecklistBaseline:
    """B1: Static risk-level checklist, no condition evaluation."""

    def reason(
        self,
        clause: RegulatoryClause,
        profile: SystemProfile,
        instance_id: str,
    ) -> ReasoningResult:
        result = ReasoningResult(
            instance_id=instance_id,
            clause_id=clause.clause_id,
            system_id=profile.system_id,
            engine_version="checklist-b1",
        )
        traces: list[ActivationTrace] = []

        triggered_risk_levels = _RISK_TRIGGERS.get(clause.thematic_group, set())
        risk_match = profile.risk_level.value in triggered_risk_levels

        for obl in clause.obligations:
            if risk_match:
                status = ApplicabilityStatus.APPLICABLE
                derivation = "B1-risk-level-match"
            else:
                status = ApplicabilityStatus.NOT_APPLICABLE
                derivation = "B1-risk-level-no-match"

            traces.append(
                ActivationTrace(
                    obligation_id=obl.obligation_id,
                    status=status,
                    derivation_rule=derivation,
                )
            )

        result.activation_traces = traces

        # Simplified evidence gap: just check generic items vs held
        held = set(profile.evidence_held)
        for trace in traces:
            if trace.status != ApplicabilityStatus.APPLICABLE:
                continue
            obl_by_id = {o.obligation_id: o for o in clause.obligations}
            obl = obl_by_id.get(trace.obligation_id)
            if obl is None:
                continue
            for ev_spec in obl.required_evidence:
                if ev_spec.evidence_id not in held:
                    result.evidence_gaps.append(
                        EvidenceGap(
                            obligation_id=obl.obligation_id,
                            system_id=profile.system_id,
                            evidence_id=ev_spec.evidence_id,
                            evidence_label=ev_spec.evidence_id,
                        )
                    )
        result.evidence_gaps.sort(key=lambda g: (g.obligation_id, g.evidence_id))
        return result
