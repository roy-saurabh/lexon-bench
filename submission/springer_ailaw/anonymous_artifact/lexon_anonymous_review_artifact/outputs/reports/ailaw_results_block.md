# Manuscript-ready results block: LEXON-Synth conformance suite

> **Instructions:** This block is the manuscript-ready text for the results section. Verify that numbers match `outputs/results/metrics_synthetic.csv` after running `make reproduce`.

---

The LEXON-Synth conformance suite was used to verify that the Python reference implementation satisfies the formal obligation-applicability and evidence-gap semantics defined in the paper. The suite contains 25 structured clauses and 30 synthetic AI system profiles, yielding 750 clause-profile pairs, with a 150-instance held-out test split generated using seed = 42.

On the held-out split, LEXON achieved corpus-level precision = 1.000, recall = 1.000, and F1 = 1.000 for obligation activation (T1), with 33 true positives, 0 false positives, and 0 false negatives. For evidence-gap detection (T2), LEXON also achieved corpus-level precision = 1.000, recall = 1.000, and F1 = 1.000, with 30 true positives, 0 false positives, and 0 false negatives. These values are interpreted as implementation-conformance results: they verify agreement between the reference implementation and the formal conformance oracle, not external legal validity.

The static-checklist baseline reached T1 F1 = 0.446 and T2 F1 = 0.321. The ontology-only baseline reached T1 F1 = 0.054 and T2 F1 = 0.000. The flat-rule baseline without typed graph constraints reached T1 F1 = 0.660 and T2 F1 = 0.533. These ablations indicate that the rule layer and typed-graph constraints are both necessary for full conformance on the synthetic suite.

For direct conflict detection (T3), LEXON detected 11 of 11 canonical gold conflict pairs with one false positive, yielding precision = 0.917, recall = 1.000, and F1 = 0.957. The false positive is attributable to an over-broad incompatibility axiom rather than to a failure of the activation semantics, illustrating that conflict-detection quality depends on the curation of the incompatibility vocabulary.

The repository also includes illustrative mappings from selected EU AI Act provisions to LEXON tuple concepts. These mappings are non-authoritative modelling examples only; they are not an expert-validated legal corpus and do not constitute legal advice.

---

## Summary table

| System | T1 Prec | T1 Rec | T1 F1 | T2 Prec | T2 Rec | T2 F1 | T3 Prec | T3 Rec | T3 F1 |
|--------|--------:|-------:|------:|--------:|-------:|------:|--------:|-------:|------:|
| LEXON full | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.917 | 1.000 | 0.957 |
| B1 Static checklist | — | — | 0.446 | — | — | 0.321 | — | — | 0.000 |
| B2 Ontology only | — | — | 0.054 | — | — | 0.000 | — | — | 0.000 |
| B3 Flat rules | — | — | 0.660 | — | — | 0.533 | — | — | 0.000 |

T3 confusion counts (LEXON full): TP = 11, FP = 1, FN = 0.

---

## Reproduction command

```bash
make reproduce
# then: cat outputs/results/metrics_synthetic.csv
```

Results are deterministic (seed=42). Run `make ailaw-artifact-check` to run the full artifact validation suite.
