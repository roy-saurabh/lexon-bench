# LEXON-Synth Conformance Suite

LEXON-Synth is a deterministic conformance suite for testing whether an implementation satisfies the formal semantics defined in the manuscript.

It is not an independent legal-validity benchmark. Conformance oracle labels are generated from the formal definitions implemented by the reference engine.

## What the suite tests

- universal condition satisfaction;
- exception firing;
- actor matching;
- mixed actor handling;
- capability bridge facts;
- three-valued unknown routing;
- evidence-gap anti-monotonicity;
- canonical conflict-pair generation;
- remediation-candidate generation;
- deterministic reproduction.

## Purpose

The purpose is implementation verification, not external legal validation.

## Suite composition

- 25 synthetic regulatory clauses
- 30 synthetic AI system profiles
- 750 clause-profile pairs
- 150-instance held-out test split (seed=42)

## Conformance results summary

| System | T1 F1 | T2 F1 | T3 F1 |
|--------|------:|------:|------:|
| LEXON full | 1.000 | 1.000 | 0.957 |
| B1 Static checklist | 0.446 | 0.321 | 0.000 |
| B2 Ontology only | 0.054 | 0.000 | 0.000 |
| B3 Flat rules | 0.660 | 0.533 | 0.000 |

These results verify agreement between the reference implementation and the formal conformance oracle. They do not establish external legal validity.

## Limitations

- All clauses are synthetic; no official regulatory text is reproduced verbatim.
- Gold labels are derived from the same formal definitions as the engine (evaluative circularity is intentional for conformance testing).
- 8 of 25 clauses carry an ambiguity flag; canonical decisions are documented in `src/lexon/benchmark/gold.py`.
- T3 conflict detection tests only direct action-incompatibility; temporal and resource conflicts are out of scope.
