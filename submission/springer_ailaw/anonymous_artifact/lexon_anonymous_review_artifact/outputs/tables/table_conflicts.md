| System | T3 Precision | T3 Recall | T3 F1 |
|:-------|:-------------|:----------|:------|
| LEXON (full) | 0.92 | 1.00 | 0.96 |
| B1 Static checklist | 0.00 | 0.00 | 0.00 |
| B2 Ontology (no rules) | 0.00 | 0.00 | 0.00 |
| B3 Flat rules (no graph) | 0.00 | 0.00 | 0.00 |

*Table: Conflict detection (T3) on the test split. LEXON T3 is evaluated at the cross-clause level: unique unordered obligation pairs across all 30 system profiles (TP=11, FP=1, FN=0). Baselines (B1–B3) do not implement cross-clause conflict detection and score 0.00 by design. Conflict pairs are scoped to same-actor applicable obligations with incompatible actions (Definition 7).*
