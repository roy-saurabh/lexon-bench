| System | T1 P | T1 R | Corpus T1 F1 | Mean-inst T1 F1 95% CI | T2 P | T2 R | Corpus T2 F1 | Mean-inst T2 F1 95% CI |
|:-------|:-----|:-----|:-------------|:------------------------|:-----|:-----|:-------------|:------------------------|
| LEXON (full) | 1.00 | 1.00 | 1.00 | [0.09, 0.21] | 1.00 | 1.00 | 1.00 | [0.06, 0.16] |
| B1 Static checklist | 0.29 | 0.94 | 0.45 | [0.08, 0.19] | 0.20 | 0.90 | 0.32 | [0.05, 0.15] |
| B2 Ontology (no rules) | 0.25 | 0.03 | 0.05 | [0.00, 0.02] | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| B3 Flat rules (no graph) | 0.51 | 0.94 | 0.66 | [0.09, 0.19] | 0.37 | 0.93 | 0.53 | [0.05, 0.15] |

*Table: Obligation activation (T1) and evidence-gap detection (T2) on the test split. **Corpus T1/T2 F1** (main columns) are corpus-level micro-averaged F1 computed from summed TP/FP/FN across all instances. **Mean-inst F1 95% CI** (bracketed columns) are bootstrapped (1000 iterations, seed=42) confidence intervals over per-instance F1 scores; these measure per-instance variability and are not uncertainty intervals for the corpus-level F1. LEXON corpus T1/T2 F1=1.00 on this synthetic benchmark is by construction (formal rules and gold oracle share identical semantics for unambiguous clauses; see §2.7 and §4.4). External validation on real regulatory provisions is future work.*
