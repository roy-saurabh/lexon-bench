"""
LEXON Stratified-Datalog Reasoning Engine.

Implements Rules R1–R7 from the paper under the closed-world assumption (CWA)
with stratified negation-as-failure.  The engine faithfully reproduces the
formal definitions (Definitions 4–8) and proof sketches (Appendix B).

Stratification:
  Stratum 0: conditionSatisfied (base facts + R1)
  Stratum 1: MissingCondition (R1b), exceptionFired (R3)
  Stratum 2: AllConditionsSatisfied (R2 uses NOT MissingCondition)
  Stratum 3: Applicable (R4 uses NOT exceptionFired)
  Stratum 4: EvidenceGap (R5), Conflict (R6), RemediationCandidate (R7)

Closed-world assumption: any evidence ID not explicitly listed in
SystemProfile.evidence_held is treated as absent.  Any property not in
SystemProfile.properties is treated as unknown (yielding Uncertain activation).
"""

from __future__ import annotations

from lexon.constants import INCOMPATIBILITY_SET
from lexon.schemas import (
    ActivationTrace,
    ApplicabilityStatus,
    BenchmarkInstance,
    Condition,
    ConflictPair,
    CrossClauseConflict,
    EvidenceGap,
    GoldLabels,
    Obligation,
    RemediationCandidate,
    RemediationAction,
    ReasoningResult,
    RegulatoryClause,
    SystemConflictResult,
    SystemProfile,
)


class LexonEngine:
    """
    Stateless reasoning engine implementing LEXON Rules R1–R7.

    All methods are pure functions over typed inputs; no mutable state is held.
    Reproducibility is guaranteed by deterministic iteration over sorted IDs.
    """

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def reason(
        self,
        clause: RegulatoryClause,
        profile: SystemProfile,
        instance_id: str,
    ) -> ReasoningResult:
        """
        Execute all four reasoning tasks for a clause–profile pair.

        Returns a ReasoningResult with full derivation traces.
        """
        result = ReasoningResult(
            instance_id=instance_id,
            clause_id=clause.clause_id,
            system_id=profile.system_id,
        )

        # Stage 1: Compute activation traces for all obligations (T1)
        traces = [
            self._activate_obligation(obl, profile)
            for obl in clause.obligations
        ]
        result.activation_traces = traces

        # Stage 2: Compute evidence gaps for applicable obligations (T2)
        result.evidence_gaps = self._compute_evidence_gaps(traces, clause, profile)

        # Stage 3: Detect conflicts among applicable obligations (T3)
        result.conflict_pairs = self._detect_conflicts(traces, clause, profile)

        # Stage 4: Generate evidence-remediation candidates (T4)
        result.remediation_candidates = self._generate_remediation_candidates(
            result.evidence_gaps, profile, clause
        )

        return result

    # ------------------------------------------------------------------
    # R1 + R1b: Condition satisfaction
    # ------------------------------------------------------------------

    def _evaluate_condition(self, cond: Condition, profile: SystemProfile) -> bool | None:
        """
        R1 — conditionSatisfied(C, S): check predicate–value match in profile.

        Returns True/False for known properties, None if property is unknown
        (triggering Uncertain under CWA in the caller).
        """
        props = profile.properties
        pred = cond.predicate

        # Handle top-level typed profile fields first
        if pred == "risk_level":
            val = profile.risk_level.value
        elif pred == "domain":
            val = profile.domain.value
        elif pred == "actor":
            val = profile.actor.value
        elif pred == "deployment_context":
            val = profile.deployment_context.value
        elif pred in props:
            val = props[pred]
        else:
            # Unknown property under CWA → signal Unknown
            return None

        # Handle multi-value conditions (condition value is a list)
        expected = cond.value
        if isinstance(expected, list):
            satisfied = val in expected
        else:
            satisfied = val == expected

        return not satisfied if cond.negated else satisfied

    def _missing_conditions(
        self, obligation: Obligation, profile: SystemProfile
    ) -> tuple[list[str], list[str], list[str]]:
        """
        R1b — MissingCondition(O, S): identify unsatisfied / unknown conditions.

        Returns (satisfied_ids, known_false_ids, unknown_ids).
        Separating known-false from unknown is required for correct stratified
        Datalog semantics: a known-false condition blocks activation definitively,
        while an unknown condition only produces Uncertain if no condition is
        known-false (Definition 4, Stratum 3 of the stratification).
        """
        satisfied: list[str] = []
        known_false: list[str] = []
        unknown: list[str] = []

        for cond in obligation.conditions:
            result = self._evaluate_condition(cond, profile)
            if result is None:
                unknown.append(cond.condition_id)
            elif result:
                satisfied.append(cond.condition_id)
            else:
                known_false.append(cond.condition_id)

        return satisfied, known_false, unknown

    # ------------------------------------------------------------------
    # R2: Universal condition satisfaction (corrected)
    # ------------------------------------------------------------------

    def _all_conditions_satisfied(
        self, obligation: Obligation, profile: SystemProfile
    ) -> tuple[bool, bool]:
        """
        R2 — AllConditionsSatisfied(O, S): derived when NOT MissingCondition(O, S).

        Returns (all_satisfied, has_unknown).
        """
        _, known_false, unknown = self._missing_conditions(obligation, profile)
        # Under the corrected universal semantics: ALL conditions must be
        # satisfied.  Existential satisfaction of a single condition is
        # insufficient (see Paper §2.4, R2 correction note).
        all_satisfied = len(known_false) == 0 and len(unknown) == 0
        return all_satisfied, len(unknown) > 0

    # ------------------------------------------------------------------
    # R3: Exception firing
    # ------------------------------------------------------------------

    def _exception_fired(self, obligation: Obligation, profile: SystemProfile) -> list[str]:
        """
        R3 — exceptionFired(O, S): ANY satisfied exception condition suppresses
        applicability (disjunctive exception semantics from Definition 2).

        Returns list of fired exception IDs (empty → no exception fires).
        """
        fired: list[str] = []
        for exc in obligation.exceptions:
            # Build a synthetic Condition for evaluation
            cond = Condition(
                condition_id=exc.exception_id,
                predicate=exc.predicate,
                value=exc.value,
            )
            result = self._evaluate_condition(cond, profile)
            if result is True:
                fired.append(exc.exception_id)
        return fired

    # ------------------------------------------------------------------
    # R4: Obligation activation (T1)
    # ------------------------------------------------------------------

    def _activate_obligation(
        self, obligation: Obligation, profile: SystemProfile
    ) -> ActivationTrace:
        """
        R4 — Applicable(O, S): activation with full derivation trace.

        Status follows Definition 4:
          Applicable   — all conditions satisfied, no exception fires
          NotApplicable — any exception fires, OR a blocking condition is false
          Uncertain    — at least one condition is unknown, no exception fires
        """
        # Profile completeness guard
        if not profile.profile_complete:
            return ActivationTrace(
                obligation_id=obligation.obligation_id,
                status=ApplicabilityStatus.UNCERTAIN,
                derivation_rule="profile-incomplete",
            )

        # Actor match (hard filter — if actor is specified and doesn't match,
        # the obligation is structurally NotApplicable for this profile)
        obl_actor = obligation.actor.value
        sys_actor = profile.actor.value
        if obl_actor not in ("Mixed",) and sys_actor not in ("Mixed",):
            if obl_actor != sys_actor:
                return ActivationTrace(
                    obligation_id=obligation.obligation_id,
                    status=ApplicabilityStatus.NOT_APPLICABLE,
                    derivation_rule="R4-actor-mismatch",
                )

        # R3: Check exceptions first (Xₒ is disjunctive — any exception fires)
        fired_exceptions = self._exception_fired(obligation, profile)
        if fired_exceptions:
            return ActivationTrace(
                obligation_id=obligation.obligation_id,
                status=ApplicabilityStatus.NOT_APPLICABLE,
                exceptions_fired=fired_exceptions,
                derivation_rule="R4-exception-fired",
            )

        # R1b + R2: Check universal condition satisfaction
        satisfied_ids, known_false_ids, unknown_ids = self._missing_conditions(
            obligation, profile
        )

        if known_false_ids:
            # At least one condition is definitively false → NotApplicable.
            # This takes priority over unknown conditions: a known-false condition
            # blocks activation even when other conditions are unevaluable
            # (stratified Datalog closed-world semantics, Definition 4).
            return ActivationTrace(
                obligation_id=obligation.obligation_id,
                status=ApplicabilityStatus.NOT_APPLICABLE,
                conditions_satisfied=satisfied_ids,
                conditions_missing=known_false_ids + unknown_ids,
                derivation_rule="R2-conditions-not-satisfied",
            )

        if unknown_ids:
            # All evaluable conditions are satisfied but some are unknown → Uncertain
            return ActivationTrace(
                obligation_id=obligation.obligation_id,
                status=ApplicabilityStatus.UNCERTAIN,
                conditions_satisfied=satisfied_ids,
                conditions_missing=unknown_ids,
                derivation_rule="R2-unknown-conditions",
            )

        # All conditions satisfied, no exception fired → Applicable (R4)
        return ActivationTrace(
            obligation_id=obligation.obligation_id,
            status=ApplicabilityStatus.APPLICABLE,
            conditions_satisfied=satisfied_ids,
            derivation_rule="R4-applicable",
        )

    # ------------------------------------------------------------------
    # R5: Evidence-gap detection (T2)
    # ------------------------------------------------------------------

    def _compute_evidence_gaps(
        self,
        traces: list[ActivationTrace],
        clause: RegulatoryClause,
        profile: SystemProfile,
    ) -> list[EvidenceGap]:
        """
        R5 — EvidenceGap(O, S, E): for each applicable obligation, compute
        Gap(o, S) = Eₒ \\ E_held under CWA.

        Property 3: adding held evidence can only reduce or preserve gaps.
        Property 4: completeness is bounded by the evidence vocabulary.
        """
        evidence_held = set(profile.evidence_held)
        gaps: list[EvidenceGap] = []

        # Build obligation lookup
        obl_by_id = {obl.obligation_id: obl for obl in clause.obligations}

        for trace in traces:
            if trace.status != ApplicabilityStatus.APPLICABLE:
                continue
            obligation = obl_by_id.get(trace.obligation_id)
            if obligation is None:
                continue
            for ev_spec in obligation.required_evidence:
                # CWA: not in evidence_held → treat as absent
                if ev_spec.evidence_id not in evidence_held:
                    gaps.append(
                        EvidenceGap(
                            obligation_id=obligation.obligation_id,
                            system_id=profile.system_id,
                            evidence_id=ev_spec.evidence_id,
                            evidence_label=ev_spec.label or ev_spec.evidence_id,
                            mandatory=ev_spec.mandatory,
                        )
                    )

        # Return in deterministic order
        return sorted(gaps, key=lambda g: (g.obligation_id, g.evidence_id))

    # ------------------------------------------------------------------
    # R6: Conflict detection (T3)
    # ------------------------------------------------------------------

    def _detect_conflicts(
        self,
        traces: list[ActivationTrace],
        clause: RegulatoryClause,
        profile: SystemProfile,
    ) -> list[ConflictPair]:
        """
        R6 — Conflict(O1, O2, S): direct action-incompatibility conflicts
        among applicable obligations sharing the same actor.

        Scope: direct conflicts only (Definition 7).
        Temporal and resource conflicts are out of scope (§4.4).
        """
        applicable_obls = [
            t.obligation_id
            for t in traces
            if t.status == ApplicabilityStatus.APPLICABLE
        ]
        obl_by_id = {obl.obligation_id: obl for obl in clause.obligations}

        conflicts: list[ConflictPair] = []
        seen: set[frozenset[str]] = set()

        for i, oid1 in enumerate(applicable_obls):
            for oid2 in applicable_obls[i + 1:]:
                pair_key = frozenset([oid1, oid2])
                if pair_key in seen:
                    continue

                o1 = obl_by_id.get(oid1)
                o2 = obl_by_id.get(oid2)
                if o1 is None or o2 is None:
                    continue

                # Same actor constraint (Definition 7)
                if o1.actor != o2.actor:
                    continue

                act1 = o1.action
                act2 = o2.action

                if (act1, act2) in INCOMPATIBILITY_SET or (act2, act1) in INCOMPATIBILITY_SET:
                    axiom = f"{act1} ⊥ {act2}"
                    conflicts.append(
                        ConflictPair(
                            obligation_id_1=oid1,
                            obligation_id_2=oid2,
                            system_id=profile.system_id,
                            action_1=act1,
                            action_2=act2,
                            shared_actor=o1.actor.value,
                            incompatibility_axiom=axiom,
                        )
                    )
                    seen.add(pair_key)

        return sorted(conflicts, key=lambda c: (c.obligation_id_1, c.obligation_id_2))

    # ------------------------------------------------------------------
    # System-level cross-clause conflict detection (T3 extended)
    # ------------------------------------------------------------------

    def detect_cross_clause_conflicts(
        self,
        profile: SystemProfile,
        clauses: list[RegulatoryClause],
    ) -> SystemConflictResult:
        """
        Detect cross-clause conflicts for a given system profile.

        Runs all clauses, collects applicable obligations, then finds
        cross-clause pairs with the same actor and incompatible actions.
        The engine applies the full INCOMPATIBILITY_SET mechanically,
        which may include over-broad vocabulary matches; the gold oracle
        excludes those via CANONICAL_CONFLICT_EXCLUSIONS.

        Returns a SystemConflictResult with all detected cross-clause conflicts.
        """
        # Build a flat list of (clause_id, obligation) for all applicable obligations
        applicable: list[tuple[str, Obligation]] = []
        for clause in sorted(clauses, key=lambda c: c.clause_id):
            for obl in clause.obligations:
                trace = self._activate_obligation(obl, profile)
                if trace.status == ApplicabilityStatus.APPLICABLE:
                    applicable.append((clause.clause_id, obl))

        conflicts: list[CrossClauseConflict] = []
        seen: set[frozenset[str]] = set()

        for i, (cid1, o1) in enumerate(applicable):
            for cid2, o2 in applicable[i + 1:]:
                if cid1 == cid2:
                    continue  # within-clause handled by per-instance _detect_conflicts

                pair_key = frozenset([o1.obligation_id, o2.obligation_id])
                if pair_key in seen:
                    continue

                if o1.actor != o2.actor:
                    continue

                a1, a2 = o1.action, o2.action
                if (a1, a2) in INCOMPATIBILITY_SET or (a2, a1) in INCOMPATIBILITY_SET:
                    conflicts.append(CrossClauseConflict(
                        system_id=profile.system_id,
                        clause_id_1=cid1,
                        obligation_id_1=o1.obligation_id,
                        action_1=a1,
                        clause_id_2=cid2,
                        obligation_id_2=o2.obligation_id,
                        action_2=a2,
                        shared_actor=o1.actor.value,
                        incompatibility_axiom=f"{a1} ⊥ {a2}",
                    ))
                    seen.add(pair_key)

        return SystemConflictResult(
            system_id=profile.system_id,
            cross_clause_conflicts=sorted(
                conflicts,
                key=lambda c: (c.obligation_id_1, c.obligation_id_2),
            ),
        )

    # ------------------------------------------------------------------
    # R7: Evidence-remediation candidates (T4)
    # ------------------------------------------------------------------

    def _generate_remediation_candidates(
        self,
        evidence_gaps: list[EvidenceGap],
        profile: SystemProfile,
        clause: RegulatoryClause,
    ) -> list[RemediationCandidate]:
        """
        R7 — RemediationCandidate(S, E): evidence additions that would close
        one or more gaps.

        Scope: evidence completion only (Definition 8 / §2.1 note).
        Does NOT model substantive operational controls.
        The minimum-cardinality set is NP-hard; we return candidate sets only.
        """
        if not evidence_gaps:
            return []

        # Group gaps by evidence_id (one candidate per unique evidence type)
        by_evidence: dict[str, list[str]] = {}
        for gap in evidence_gaps:
            if gap.evidence_id not in by_evidence:
                by_evidence[gap.evidence_id] = []
            by_evidence[gap.evidence_id].append(gap.obligation_id)

        # Flag whether any involved obligation is ambiguous
        ambiguous_obligations = {
            obl.obligation_id
            for obl in clause.obligations
            if obl.ambiguity_flag
        }

        candidates: list[RemediationCandidate] = []
        for ev_id in sorted(by_evidence.keys()):
            obl_ids = sorted(by_evidence[ev_id])
            needs_review = any(oid in ambiguous_obligations for oid in obl_ids)
            action = (
                RemediationAction.ESCALATE_FOR_HUMAN_REVIEW
                if needs_review
                else RemediationAction.ADD_EVIDENCE
            )
            candidates.append(
                RemediationCandidate(
                    system_id=profile.system_id,
                    evidence_id=ev_id,
                    evidence_label=ev_id,
                    remediation_action=action,
                    closes_gaps_for=obl_ids,
                    requires_human_review=needs_review,
                )
            )

        return candidates
