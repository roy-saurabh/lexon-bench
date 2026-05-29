# LEXON Core Rules — Corrected Universal Activation Pattern

## Why this file exists

An earlier (informal) specification of the LEXON activation rules used an
*existential* pattern in which a single satisfied condition was sufficient to
derive `Applicable(O, S)`. The paper (§2.4, R2) corrects this to require
*universal* satisfaction of **all** activation conditions.

This file documents the correction and explains its implementation.

---

## The incorrect existential pattern (do not use)

```datalog
% WRONG — existential: one satisfied condition suffices
Applicable(O, S) :-
  hasCondition(O, C),
  conditionSatisfied(C, S),
  NOT exceptionFired(O, S).
```

This is **incorrect** because it activates an obligation as soon as *any one*
of its conditions is satisfied, regardless of the others. For example, an
obligation conditioned on both `risk_level = HighRisk` AND `isDeployed = True`
would incorrectly activate for a `MinimalRisk` deployed system, because
`isDeployed = True` alone satisfies one condition.

---

## The corrected universal pattern

```datalog
% R1b — A required condition C of obligation O is missing in S
%        if it is not satisfied.
MissingCondition(O, S) :-
  hasCondition(O, C),
  NOT conditionSatisfied(C, S).

% R2 — AllConditionsSatisfied: derived when NOT MissingCondition.
%      Universal quantification expressed via negation-as-failure.
AllConditionsSatisfied(O, S) :-
  hasObligation(_, O),
  NOT MissingCondition(O, S).

% R4 — Applicable only when all conditions satisfied and no exception.
Applicable(O, S) :-
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).
```

The key insight is that **universal quantification** `∀c ∈ Cₒ: satisfied(c, S)`
cannot be expressed as a single existential rule in Datalog. Instead, it is
expressed as the *absence of any unsatisfied condition* via negation-as-failure:

> `AllConditionsSatisfied(O, S)` holds iff there is **no** `C` such that
> `hasCondition(O, C)` and `NOT conditionSatisfied(C, S)`.

---

## Stratification

The corrected rules are stratifiable:

| Predicate | Stratum | Depends on |
|-----------|---------|------------|
| `conditionSatisfied` | 0 | base facts (R1) |
| `MissingCondition` | 1 | `NOT conditionSatisfied` (negates Stratum 0) |
| `exceptionFired` | 1 | `conditionSatisfied` (Stratum 0) |
| `AllConditionsSatisfied` | 2 | `NOT MissingCondition` (negates Stratum 1) |
| `Applicable` | 3 | `NOT exceptionFired` (negates Stratum 1) |
| `EvidenceGap`, `Conflict`, `RemediationCandidate` | 4 | `Applicable` (Stratum 3) |

Stratification ensures the program has a unique perfect model under the
closed-world assumption.  See Appendix B of the paper for soundness proofs.

---

## Closed-world assumption note

All inference is under the **closed-world assumption** (CWA):

- Any evidence item not listed in `evidence_held` is treated as **absent**.
- Any condition property not present in `properties` is treated as **unknown**,
  which triggers `Uncertain` status rather than `NotApplicable` or `Applicable`.
- This is a deliberate design choice for reproducible, auditable inference.
  Open-world extensions are identified as future work (§4.4).

---

## Python implementation reference

The corrected rules are implemented in
[`src/lexon/reasoning/engine.py`](../src/lexon/reasoning/engine.py):

- `_missing_conditions()` → R1b (`MissingCondition`)
- `_all_conditions_satisfied()` → R2 (`AllConditionsSatisfied`)
- `_exception_fired()` → R3 (`exceptionFired`)
- `_activate_obligation()` → R4 (`Applicable`)
- `_compute_evidence_gaps()` → R5 (`EvidenceGap`)
- `_detect_conflicts()` → R6 (`Conflict`)
- `_generate_remediation_candidates()` → R7 (`RemediationCandidate`)
