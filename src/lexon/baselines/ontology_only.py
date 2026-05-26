"""
B2 — Ontology-Only Baseline.

Loads typed entities and relations from the TBox/ABox.
Performs NO inference — no Datalog rules are fired.
Can only surface obligations directly linked to matching type tags.

Systematic weaknesses:
  - Can match actor, domain, risk level from profile type tags
  - Cannot evaluate conditional activation (no rule layer)
  - Cannot fire exception rules
  - Evidence gap detection is incomplete (no activation dependency)
  - Cannot detect conflicts (no rule layer)
"""

from __future__ import annotations

from lexon.schemas import (
    ActivationTrace,
    ApplicabilityStatus,
    EvidenceGap,
    ReasoningResult,
    RegulatoryClause,
    SystemProfile,
)


class OntologyOnlyBaseline:
    """
    B2: Typed ontology lookup without inference.

    Activates an obligation if and only if:
    1. The profile's risk_level is in the clause's scope_risk_levels, AND
    2. The profile's domain is in the clause's scope_domains (or scope is empty), AND
    3. The profile's actor matches the obligation's actor.

    No condition evaluation, no exception handling.
    """

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
            engine_version="ontology-b2",
        )
        traces: list[ActivationTrace] = []

        risk_in_scope = (
            not clause.scope_risk_levels
            or profile.risk_level in clause.scope_risk_levels
        )
        domain_in_scope = (
            not clause.scope_domains
            or profile.domain in clause.scope_domains
        )

        for obl in clause.obligations:
            # Actor type match
            actor_match = (
                obl.actor.value == "Mixed"
                or profile.actor.value == "Mixed"
                or obl.actor.value == profile.actor.value
            )

            if risk_in_scope and domain_in_scope and actor_match:
                status = ApplicabilityStatus.APPLICABLE
                derivation = "B2-type-tag-match"
            else:
                status = ApplicabilityStatus.NOT_APPLICABLE
                derivation = "B2-type-tag-no-match"

            traces.append(
                ActivationTrace(
                    obligation_id=obl.obligation_id,
                    status=status,
                    derivation_rule=derivation,
                )
            )

        result.activation_traces = traces

        held = set(profile.evidence_held)
        obl_by_id = {o.obligation_id: o for o in clause.obligations}
        for trace in traces:
            if trace.status != ApplicabilityStatus.APPLICABLE:
                continue
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
