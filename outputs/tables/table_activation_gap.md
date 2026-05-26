| System | T1 P | T1 R | T1 F1 | T1 95% CI | T2 P | T2 R | T2 F1 | T2 95% CI |
|:-------|:-----|:-----|:------|:----------|:-----|:-----|:------|:----------|
| LEXON (full) | 1.00 | 1.00 | 1.00 | [0.07, 0.19] | 1.00 | 1.00 | 1.00 | [0.05, 0.15] |
| B1 Static checklist | 0.27 | 0.97 | 0.43 | [0.07, 0.18] | 0.20 | 0.93 | 0.32 | [0.05, 0.15] |
| B2 Ontology (no rules) | 0.25 | 0.03 | 0.06 | [0.00, 0.02] | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| B3 Flat rules (no graph) | 0.46 | 0.93 | 0.62 | [0.07, 0.17] | 0.36 | 0.93 | 0.52 | [0.05, 0.14] |

*Table: Obligation activation (T1) and evidence-gap detection (T2) on the test split. Corpus-level P/R/F1 (main columns) are micro-averaged TP/FP/FN across all instances. 95% CIs are bootstrapped (1000 iterations, seed=42) over per-instance F1 scores; most instances have no applicable obligations and contribute F1=0, so the CI reflects per-instance variability rather than uncertainty in the corpus-level F1. LEXON T1/T2 F1=1.00 on this synthetic benchmark is by construction (formal rules and gold oracle share identical semantics for unambiguous clauses); real regulatory-text evaluation is reported in the companion paper.*
