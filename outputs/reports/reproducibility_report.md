# LEXON-Bench Reproducibility Report

Generated: 2026-05-26 15:41 UTC
Seed: 42
Test instances: 150
Wall time: 0.8s

## T1 — Obligation Activation

Corpus-level P/R/F1 are micro-averaged from summed TP/FP/FN across all instances.
Mean-inst F1 95% CI is a bootstrapped interval over per-instance F1 scores; it
measures per-instance variability and is NOT an uncertainty interval for corpus F1.

Corpus confusion counts:
  LEXON (full): TP=33, FP=0, FN=0
  B1 Static checklist: TP=31, FP=75, FN=2
  B2 Ontology (no rules): TP=1, FP=3, FN=32
  B3 Flat rules (no graph): TP=31, FP=30, FN=2

| System | Corpus P | Corpus R | Corpus F1 | Mean-inst F1 95% CI |
|--------|----------|----------|-----------|---------------------|
| LEXON (full) | 1.000 | 1.000 | 1.000 | [0.093, 0.207] |
| B1 Static checklist | 0.292 | 0.939 | 0.446 | — |
| B2 Ontology (no rules) | 0.250 | 0.030 | 0.054 | — |
| B3 Flat rules (no graph) | 0.508 | 0.939 | 0.660 | — |

## T2 — Evidence-Gap Detection

Corpus-level P/R/F1 are micro-averaged from summed TP/FP/FN across all instances.
Mean-inst F1 95% CI is a bootstrapped interval over per-instance F1 scores; it
measures per-instance variability and is NOT an uncertainty interval for corpus F1.

Corpus confusion counts:
  LEXON (full): TP=30, FP=0, FN=0
  B1 Static checklist: TP=27, FP=111, FN=3
  B2 Ontology (no rules): TP=0, FP=4, FN=30
  B3 Flat rules (no graph): TP=28, FP=47, FN=2

| System | Corpus P | Corpus R | Corpus F1 | Mean-inst F1 95% CI | FNR |
|--------|----------|----------|-----------|---------------------|-----|
| LEXON (full) | 1.000 | 1.000 | 1.000 | [0.060, 0.160] | 0.000 |
| B1 Static checklist | 0.196 | 0.900 | 0.321 | — | 0.100 |
| B2 Ontology (no rules) | 0.000 | 0.000 | 0.000 | — | 1.000 |
| B3 Flat rules (no graph) | 0.373 | 0.933 | 0.533 | — | 0.067 |

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
All paper-ready outputs verified clean (no stale template text).
External validation on real regulatory provisions is future work.
