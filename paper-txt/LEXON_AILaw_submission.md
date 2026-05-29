> **Note:** Repository manuscript text is provided for traceability only; the submitted manuscript file may differ in formatting and content.

---

# LEXON: Executable Obligation Reasoning for AI Regulation with Typed Knowledge Graphs and Stratified Datalog

**Roy Saurabh**
AffectLog SAS
roy@affectlog.com

Submitted to *Artificial Intelligence and Law* (Springer)

---

## Abstract

We present LEXON (Legal EXecutable Obligation Network), a symbolic AI & Law framework for representing conditional regulatory obligations as typed information objects and evaluating their applicability, evidence requirements, and direct conflicts through stratified rule-based inference. LEXON encodes AI regulatory clauses as typed obligation tuples over a knowledge graph and applies seven stratified Datalog-style rules to compute: (T1) obligation activation under closed-world and three-valued semantics; (T2) evidence-gap detection under the closed-world assumption; (T3) direct conflict detection via an explicit incompatibility vocabulary; and (T4) evidence-remediation candidates. We evaluate LEXON using a deterministic synthetic conformance suite of 25 clauses and 30 AI system profiles (750 clause-profile pairs). On the held-out test split, LEXON achieves F1=1.000 for T1 and T2 (implementation-conformance results verifying agreement with the formal definitions) and F1=0.957 for T3. Three ablation baselines demonstrate that both the typed knowledge-graph layer and the stratified rule layer are necessary for full conformance. We provide derivation traces, formal-property tests, and an illustrative EU AI Act mapping. The full artifact is released under MIT/CC-BY-4.0.

**Keywords:** AI regulation; executable obligation reasoning; knowledge graphs; stratified Datalog; conformance suite; AI & Law; evidence-gap detection; conflict detection

---

## 1. Introduction

[Manuscript body — see submitted manuscript file]

---

## 2. LEXON Framework

### 2.1 Typed obligation schema

### 2.2 Knowledge-graph layer

### 2.3 Stratified rule layer (R1–R7)

### 2.4 Three-valued applicability semantics

### 2.5 Evidence-gap detection

### 2.6 Conflict detection

### 2.7 Relation to conformance testing

---

## 3. Conformance Suite and Evaluation

### 3.1 Conformance suite construction

The LEXON-Synth conformance suite contains 25 synthetic regulatory clauses, 30 AI system profiles, and 750 clause-profile pairs. A deterministic 150-instance held-out test split is generated using seed=42.

All gold labels are derived from the formal definitions implemented by the reference engine. This evaluative design is intentional for implementation verification and does not constitute external legal validation.

### 3.2 Conformance results

| System | T1 F1 | T2 F1 | T3 F1 |
|--------|------:|------:|------:|
| LEXON full | 1.000 | 1.000 | 0.957 |
| B1 Static checklist | 0.446 | 0.321 | 0.000 |
| B2 Ontology only | 0.054 | 0.000 | 0.000 |
| B3 Flat rules | 0.660 | 0.533 | 0.000 |

These results are conformance-suite results on synthetic data. They verify agreement between the reference implementation and the formal conformance oracle. They do not establish external legal validity.

### 3.3 Ablation analysis

[Manuscript body — see submitted manuscript file]

---

## 4. Illustrative EU AI Act Mapping

[Manuscript body — see submitted manuscript file]

---

## 5. Related Work

[Manuscript body — see submitted manuscript file]

---

## 6. Conclusion

[Manuscript body — see submitted manuscript file]

---

## Appendix A: Formal Definitions

[Manuscript body — see submitted manuscript file]

---

## Appendix B: Proof Sketches

[Manuscript body — see submitted manuscript file]

---

## Data Availability

The source code, synthetic conformance suite, structured obligation tuples, AI system profiles, conformance oracle labels, baseline implementations, rule specifications, illustrative EU AI Act mapping, derivation-trace examples, and reproduction scripts are available in the LEXON-Bench repository at https://github.com/roy-saurabh/lexon-bench and archived on Zenodo. The artifact version associated with this submission is v1.1.0, with version-specific DOI [INSERT DOI AFTER RELEASE]. The synthetic conformance suite contains no personal data. Code is released under MIT; synthetic data under CC-BY-4.0.
