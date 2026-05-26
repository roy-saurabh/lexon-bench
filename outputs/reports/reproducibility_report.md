# LEXON-Bench Reproducibility Report

Generated: 2026-05-26 14:26 UTC
Seed: 42
Test instances: 150
Wall time: 1.1s

## T1 — Obligation Activation

| System | P | R | F1 | 95% CI |
|--------|---|---|----|--------|
| LEXON (full) | 1.000 | 1.000 | 1.000 | [0.073, 0.187] |
| B1 Static checklist | 0.274 | 0.967 | 0.426 | — |
| B2 Ontology (no rules) | 0.250 | 0.033 | 0.059 | — |
| B3 Flat rules (no graph) | 0.459 | 0.933 | 0.615 | — |

## T2 — Evidence-Gap Detection

| System | P | R | F1 | 95% CI | FNR |
|--------|---|---|----|--------|-----|
| LEXON (full) | 1.000 | 1.000 | 1.000 | [0.053, 0.153] | 0.000 |
| B1 Static checklist | 0.196 | 0.931 | 0.323 | — | 0.069 |
| B2 Ontology (no rules) | 0.000 | 0.000 | 0.000 | — | 1.000 |
| B3 Flat rules (no graph) | 0.360 | 0.931 | 0.519 | — | 0.069 |

## T3 — Cross-Clause Conflict Detection

Evaluated at the unique obligation-pair level across all 30 system profiles.
LEXON cross-clause T3: TP=11, FP=1, FN=0

| System | P | R | F1 |
|--------|---|---|----|
| LEXON (full) | 0.917 | 1.000 | 0.957 |
| B1 Static checklist | 0.000 | 0.000 | 0.000 |
| B2 Ontology (no rules) | 0.000 | 0.000 | 0.000 |
| B3 Flat rules (no graph) | 0.000 | 0.000 | 0.000 |

## LLM Baseline

The LLM baseline was NOT executed in this run.  See `outputs/audit/llm_baseline_status.json` for details.

## Integrity

All outputs generated from seed=42 with no external API calls.
Benchmark validated: 25 clauses, 30 profiles, 750 instances (with CF obligations).
No placeholder text in paper-ready tables.
