"""
B3 — Flat-Rule Baseline (no typed graph).

Uses untyped if/then rules over profile properties.
Does NOT use typed graph constraints from the TBox.

Systematic weaknesses:
  - Does NOT enforce actor-type constraints (leads to false positives on
    under-typed profiles where actor is 'Mixed' or under-specified)
  - Evaluates conditions but WITHOUT domain/range type checking
  - May over-activate on profiles with partial type information
  - Cannot detect conflicts (no shared-actor constraint in the rule)
"""

from __future__ import annotations

from typing import Any

from lexon.schemas import (
    ActivationTrace,
    ApplicabilityStatus,
    Condition,
    EvidenceGap,
    ReasoningResult,
    RegulatoryClause,
    SystemProfile,
)


def _eval_condition_untyped(cond: Condition, profile: SystemProfile) -> bool:
    """
    Untyped condition evaluation: no range/domain checks.

    Treats unknown properties as TRUE (permissive / open-world) rather
    than raising Uncertain — this is the key failure mode of flat rules.
    """
    props = profile.properties
    pred = cond.predicate

    # Resolve value from profile (same as engine, but no unknown handling)
    if pred == "risk_level":
        val: Any = profile.risk_level.value
    elif pred == "domain":
        val = profile.domain.value
    elif pred == "actor":
        val = profile.actor.value
    elif pred == "deployment_context":
        val = profile.deployment_context.value
    elif pred in props:
        val = props[pred]
    else:
        # Flat-rule baseline: unknown property → assume satisfied (false positive source)
        return True

    expected = cond.value
    if isinstance(expected, list):
        satisfied = val in expected
    else:
        satisfied = val == expected

    return not satisfied if cond.negated else satisfied


class FlatRulesBaseline:
    """
    B3: Untyped rule engine without typed graph constraints.

    Activates obligations based on condition matching but without:
    - Actor type validation (leads to false positives)
    - Typed range/domain checks
    - Schema-enforced evidence vocabulary
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
            engine_version="flat-rules-b3",
        )
        traces: list[ActivationTrace] = []

        for obl in clause.obligations:
            # NO actor match enforcement (flat rules don't use type constraints)
            # This is the principal source of false positives in B3.

            # Check exceptions (same logic, but untyped)
            exception_fired = False
            for exc in obl.exceptions:
                exc_cond = Condition(
                    condition_id=exc.exception_id,
                    predicate=exc.predicate,
                    value=exc.value,
                )
                if _eval_condition_untyped(exc_cond, profile):
                    exception_fired = True
                    break

            if exception_fired:
                traces.append(
                    ActivationTrace(
                        obligation_id=obl.obligation_id,
                        status=ApplicabilityStatus.NOT_APPLICABLE,
                        exceptions_fired=[exc.exception_id for exc in obl.exceptions],
                        derivation_rule="B3-exception-fired",
                    )
                )
                continue

            # Check conditions (untyped, unknown → True)
            all_satisfied = all(
                _eval_condition_untyped(cond, profile) for cond in obl.conditions
            )

            if all_satisfied:
                traces.append(
                    ActivationTrace(
                        obligation_id=obl.obligation_id,
                        status=ApplicabilityStatus.APPLICABLE,
                        derivation_rule="B3-conditions-met",
                    )
                )
            else:
                traces.append(
                    ActivationTrace(
                        obligation_id=obl.obligation_id,
                        status=ApplicabilityStatus.NOT_APPLICABLE,
                        derivation_rule="B3-conditions-not-met",
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
