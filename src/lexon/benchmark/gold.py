"""
Gold label oracle for LEXON-Bench.

Gold labels are derived from the formal definitions (Definitions 4–8) applied
to the structured obligation tuples and system profiles.

For AMBIGUOUS clauses, a canonical tie-breaking rule is applied, as documented
in docs/data_dictionary.md and in each clause's `notes` field.  The canonical
rule is the "intended" interpretation for evaluation purposes; LEXON's strict
formal engine may diverge on these instances, which is expected behaviour.

Closed-world assumption: all evidence reasoning uses CWA over evidence_held.
"""

from __future__ import annotations

from lexon.constants import (
    AMBIGUOUS_CLAUSE_IDS,
    CANONICAL_CONFLICT_EXCLUSIONS,
    INCOMPATIBILITY_SET,
)
from lexon.schemas import (
    ApplicabilityStatus,
    BenchmarkInstance,
    GoldLabels,
    Obligation,
    RegulatoryClause,
    SystemConflictGold,
    SystemProfile,
)


class GoldOracle:
    """
    Reference oracle for generating gold labels.

    The oracle uses the same core logic as LexonEngine (R1–R7) but applies
    canonical tie-breaking for the 8 ambiguous clauses.  The tie-breaking
    rules are documented inline and in docs/data_dictionary.md.
    """

    def generate_gold(
        self,
        instance: BenchmarkInstance,
        clause: RegulatoryClause,
        profile: SystemProfile,
    ) -> GoldLabels:
        """Compute gold labels for a single clause–profile pair."""
        activation: dict[str, ApplicabilityStatus] = {}
        evidence_gaps: dict[str, list[str]] = {}
        conflict_pairs: list[tuple[str, str]] = []
        remediation_candidates: list[str] = []
        canonical_notes: str = ""

        if clause.clause_id in AMBIGUOUS_CLAUSE_IDS:
            canonical_notes = clause.notes

        for obl in clause.obligations:
            status, notes = self._gold_activation(obl, profile, clause)
            activation[obl.obligation_id] = status
            if notes:
                canonical_notes = (canonical_notes + " | " + notes).strip(" |")

            if status == ApplicabilityStatus.APPLICABLE:
                held = set(profile.evidence_held)
                gaps = [
                    ev.evidence_id
                    for ev in obl.required_evidence
                    if ev.evidence_id not in held
                ]
                evidence_gaps[obl.obligation_id] = sorted(gaps)
                remediation_candidates.extend(gaps)

        # Conflict detection: same actor, incompatible actions, both applicable
        applicable_obls = [
            obl for obl in clause.obligations
            if activation.get(obl.obligation_id) == ApplicabilityStatus.APPLICABLE
        ]
        seen: set[frozenset[str]] = set()
        for i, o1 in enumerate(applicable_obls):
            for o2 in applicable_obls[i + 1:]:
                if o1.actor != o2.actor:
                    continue
                pair_key = frozenset([o1.obligation_id, o2.obligation_id])
                if pair_key in seen:
                    continue
                act1, act2 = o1.action, o2.action
                if (act1, act2) in INCOMPATIBILITY_SET or (act2, act1) in INCOMPATIBILITY_SET:
                    conflict_pairs.append((o1.obligation_id, o2.obligation_id))
                    seen.add(pair_key)

        return GoldLabels(
            instance_id=instance.instance_id,
            clause_id=clause.clause_id,
            system_id=profile.system_id,
            activation=activation,
            evidence_gaps=evidence_gaps,
            conflict_pairs=sorted(conflict_pairs),
            remediation_candidates=sorted(set(remediation_candidates)),
            canonical_notes=canonical_notes,
        )

    # ------------------------------------------------------------------
    # Gold activation with canonical tie-breaking
    # ------------------------------------------------------------------

    def _gold_activation(
        self,
        obl: Obligation,
        profile: SystemProfile,
        clause: RegulatoryClause,
    ) -> tuple[ApplicabilityStatus, str]:
        """
        Compute gold activation status with canonical disambiguation.

        Returns (status, notes_for_ambiguous_cases).
        """
        # For ambiguous clauses, apply canonical tie-breaking
        if clause.clause_id in AMBIGUOUS_CLAUSE_IDS:
            return self._canonical_activation(obl, profile, clause)

        # For unambiguous clauses, apply pure formal semantics
        return self._formal_activation(obl, profile), ""

    def _formal_activation(
        self, obl: Obligation, profile: SystemProfile
    ) -> ApplicabilityStatus:
        """Pure formal activation (same as LexonEngine) for unambiguous clauses."""
        # Actor match
        if obl.actor.value not in ("Mixed",) and profile.actor.value not in ("Mixed",):
            if obl.actor.value != profile.actor.value:
                return ApplicabilityStatus.NOT_APPLICABLE

        # Exception check (disjunctive: ANY fires)
        for exc in obl.exceptions:
            props = profile.properties
            pred = exc.predicate
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
                continue
            if val == exc.value:
                return ApplicabilityStatus.NOT_APPLICABLE

        # Condition check (conjunctive: ALL must hold)
        has_unknown = False
        for cond in obl.conditions:
            props = profile.properties
            pred = cond.predicate
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
                has_unknown = True
                continue

            expected = cond.value
            if isinstance(expected, list):
                satisfied = val in expected
            else:
                satisfied = val == expected
            if cond.negated:
                satisfied = not satisfied

            if not satisfied:
                return ApplicabilityStatus.NOT_APPLICABLE

        if has_unknown:
            return ApplicabilityStatus.UNCERTAIN

        return ApplicabilityStatus.APPLICABLE

    def _canonical_activation(
        self, obl: Obligation, profile: SystemProfile, clause: RegulatoryClause
    ) -> tuple[ApplicabilityStatus, str]:
        """
        Canonical tie-breaking for ambiguous clauses.

        Canonical rules are documented per clause in generate_synthetic.py notes
        and in docs/data_dictionary.md.  These rules represent the "intended"
        interpretation against which LEXON is evaluated.
        """
        clause_id = clause.clause_id
        notes = f"Canonical tie-breaking applied for {clause_id}"

        # CL-009: 'where appropriate' → canonical: mandatory when hasSystemicRisk=True
        if clause_id == "CL-009":
            has_systemic = profile.properties.get("hasSystemicRisk", False)
            if not has_systemic:
                return ApplicabilityStatus.NOT_APPLICABLE, notes
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-010: Dual actor — resolve by exact actor match
        if clause_id == "CL-010":
            # OBL-010-1 applies to Provider; OBL-010-2 applies to Deployer
            # Mixed actor profiles: canonical = activate both obligations
            if profile.actor.value == "Mixed":
                # Check conditions except actor
                all_ok = True
                for cond in obl.conditions:
                    if cond.predicate == "actor":
                        continue  # skip actor check for Mixed profiles
                    if cond.predicate == "risk_level":
                        val = profile.risk_level.value
                    elif cond.predicate in profile.properties:
                        val = profile.properties[cond.predicate]
                    else:
                        all_ok = False
                        break
                    expected = cond.value
                    ok = (val == expected) if not isinstance(expected, list) else (val in expected)
                    if not ok:
                        all_ok = False
                        break
                if all_ok:
                    # Check exceptions
                    for exc in obl.exceptions:
                        if exc.predicate in profile.properties:
                            if profile.properties[exc.predicate] == exc.value:
                                return ApplicabilityStatus.NOT_APPLICABLE, notes
                    return ApplicabilityStatus.APPLICABLE, notes
                return ApplicabilityStatus.NOT_APPLICABLE, notes
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-013: 'adequate protection' → canonical: mandatory when processesSpecialCategory AND EU_Market
        if clause_id == "CL-013":
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-015: Research exemption scope → canonical: hasResearchExemption always suppresses
        if clause_id == "CL-015":
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-018: Override vs. monitoring → canonical: activate HighRisk deployed; GenAI exception
        if clause_id == "CL-018":
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-020: 'sufficient oversight' → canonical: Deployer + HighRisk + affectsNaturalPerson
        if clause_id == "CL-020":
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-023: AI Act + GDPR → canonical: strict tri-condition
        if clause_id == "CL-023":
            status = self._formal_activation(obl, profile)
            return status, notes

        # CL-025: Equivalence → canonical: Importer + HighRisk + EU_Market
        if clause_id == "CL-025":
            if profile.actor.value == "Mixed":
                # Canonical: Mixed actor profiles are NOT applicable for Importer-specific obligations
                return ApplicabilityStatus.NOT_APPLICABLE, notes
            status = self._formal_activation(obl, profile)
            return status, notes

        # Fallback: formal semantics
        return self._formal_activation(obl, profile), notes


def generate_all_gold_labels(
    instances: list[BenchmarkInstance],
    clause_index: dict[str, RegulatoryClause],
    profile_index: dict[str, SystemProfile],
) -> list[GoldLabels]:
    """Generate gold labels for all instances."""
    oracle = GoldOracle()
    gold_labels: list[GoldLabels] = []
    for inst in sorted(instances, key=lambda i: i.instance_id):
        clause = clause_index[inst.clause_id]
        profile = profile_index[inst.system_id]
        gold = oracle.generate_gold(inst, clause, profile)
        gold_labels.append(gold)
    return gold_labels


def generate_all_system_conflict_golds(
    profiles: list[SystemProfile],
    clauses: list[RegulatoryClause],
) -> list[SystemConflictGold]:
    """
    Generate system-level cross-clause conflict gold labels for all profiles.

    The gold oracle applies INCOMPATIBILITY_SET minus CANONICAL_CONFLICT_EXCLUSIONS,
    producing the ground truth for T3 evaluation at the unique obligation-pair level.
    The excluded pairs represent over-broad vocabulary generalisations that the
    canonical gold oracle rejects (see §2.4 and docs/data_dictionary.md).
    """
    oracle = GoldOracle()
    results: list[SystemConflictGold] = []

    for profile in sorted(profiles, key=lambda p: p.system_id):
        # Collect applicable obligations across all clauses via gold activation
        applicable: list[tuple[str, "Obligation"]] = []
        for clause in sorted(clauses, key=lambda c: c.clause_id):
            for obl in clause.obligations:
                status, _ = oracle._gold_activation(obl, profile, clause)
                if status == ApplicabilityStatus.APPLICABLE:
                    applicable.append((clause.clause_id, obl))

        # Find cross-clause conflicts using the canonical (exclusion-filtered) set
        conflict_pairs: list[tuple[str, str]] = []
        seen: set[frozenset[str]] = set()

        for i, (cid1, o1) in enumerate(applicable):
            for cid2, o2 in applicable[i + 1:]:
                if cid1 == cid2:
                    continue

                pair_key = frozenset([o1.obligation_id, o2.obligation_id])
                if pair_key in seen:
                    continue

                if o1.actor != o2.actor:
                    continue

                a1, a2 = o1.action, o2.action

                # Canonical override: exclude over-broad vocabulary pairs
                if (a1, a2) in CANONICAL_CONFLICT_EXCLUSIONS:
                    continue
                if (a2, a1) in CANONICAL_CONFLICT_EXCLUSIONS:
                    continue

                if (a1, a2) in INCOMPATIBILITY_SET or (a2, a1) in INCOMPATIBILITY_SET:
                    conflict_pairs.append((o1.obligation_id, o2.obligation_id))
                    seen.add(pair_key)

        results.append(SystemConflictGold(
            system_id=profile.system_id,
            conflict_pairs=sorted(conflict_pairs),
        ))

    return results
