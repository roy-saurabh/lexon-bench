# LEXON-Bench: Explicit Assumptions and Limitations

## 1. Closed-World Assumption (CWA) over Evidence Holdings

**What it means:** Any evidence item not explicitly listed in
`SystemProfile.evidence_held` is treated as **absent** when evaluating evidence
gaps (R5). There is no inference of implicit evidence possession.

**Implication:** A system that holds a valid evidence artefact in a
non-standard format or under a different identifier will be reported as having
a gap. This is a conservative, auditable choice.

**Documentation:** `src/lexon/reasoning/engine.py` (R5 comment); Property 4 in
the paper.

**Future work:** Open-world extensions allowing partial evidence matching are
identified as future work (§4.4).

---

## 2. Evidentiary Completeness ≠ Legal Compliance

**Critical distinction:** LEXON evaluates whether a system profile holds the
evidence items required by structured obligation tuples. It does **not** verify
that the underlying operational controls are implemented, that evidence is
accurate, or that the system is legally compliant.

**What this means for interpreters:** An `EvidenceComplete` result means only
that the registered evidence vocabulary items are present in the profile. It
does not mean the system complies with the underlying regulation.

**Documentation:** Definition 5 in the paper; `schemas.py` (`EvidenceSpec`
docstring); all LEXON outputs.

---

## 3. Schema Coverage Bound (Property 4)

**What it means:** LEXON can only detect evidence gaps for evidence types
registered in `constants.py::EVIDENCE_VOCABULARY`. Evidence types outside this
vocabulary cannot be reported as gaps.

**Implication:** This is a schema-coverage limitation, not a soundness
limitation. Soundness holds within the vocabulary.

---

## 4. Synthetic Benchmark Limitations

- Clauses are synthetic, purpose-built for evaluating the reasoning engine.
  They are **not** official regulatory text and **do not** reproduce the full
  EU AI Act or any other official instrument.
- Gold labels are derived from the same structured schema as the system under
  test, creating a risk of evaluative circularity (§2.7, §4.4).
- Results reflect **internal benchmark validity**, not external legal-compliance
  validity.
- The 8 ambiguous clauses use a canonical tie-breaking rule that is documented
  but may not correspond to authoritative legal interpretations.

---

## 5. Actor Attribution Scope

- The current implementation enforces exact actor matching.
- "Mixed" actor profiles may yield unexpected results on obligations with a
  specific actor constraint.
- Canonical tie-breaking for dual-actor clauses (CL-010, CL-025) is documented
  in `src/lexon/benchmark/gold.py`.

---

## 6. Conflict Detection Scope

- LEXON detects **direct action-incompatibility conflicts** (Definition 7, R6).
- Temporal conflicts (overlapping time windows), resource conflicts, and
  priority conflicts are **out of scope** (§4.4).
- The incompatibility relation is defined in `rules/incompatibility_axioms.yaml`
  and `constants.py::INCOMPATIBILITY_PAIRS`.

---

## 7. Remediation Complexity

- Computing the minimum-cardinality remediation set is conjectured NP-hard
  (informal reduction from Weighted Set Cover, §2.5).
- LEXON returns greedy **candidate** sets, not optimal sets.
- Candidates are typed as `RemediationCandidate` with `remediation_action`
  field indicating whether human review is needed.

---

## 8. LLM Baseline

- The LLM baseline (`src/lexon/baselines/llm_optional.py`) is **disabled by
  default**.
- It requires both `LEXON_LLM_API_KEY` and `LEXON_RUN_LLM_BASELINE=1`.
- If not executed, results from this baseline do **not** appear in any
  main results table. See `outputs/audit/llm_baseline_status.json`.

---

## Disclaimer

LEXON is a research prototype for executable regulatory information reasoning.
It does not provide legal advice and does not determine legal compliance.
