# Manuscript–Repository Alignment Table

This document maps each substantive claim in the manuscript to the
repository artifacts that support it.

| Manuscript Claim | Artifact(s) | Notes |
|:----------------|:-----------|:------|
| LEXON performs obligation activation (T1) | `src/lexon/reasoning/engine.py` (R4, `_activate_obligation`); `tests/test_activation_all_conditions.py`; `outputs/results/metrics_synthetic.csv` | Tested and benchmarked |
| LEXON detects evidence gaps (T2) | `src/lexon/reasoning/engine.py` (R5, `_compute_evidence_gaps`); `tests/test_evidence_gaps.py`; `outputs/results/metrics_synthetic.csv` | Gap = Eₒ \ E_held under CWA |
| LEXON detects conflicts (T3) | `src/lexon/reasoning/engine.py` (R6, `_detect_conflicts`); `tests/test_conflicts.py`; `outputs/results/conflict_results.csv` | Direct conflicts only (§4.4) |
| LEXON generates remediation candidates (T4) | `src/lexon/reasoning/engine.py` (R7, `_generate_remediation_candidates`); `src/lexon/schemas.py` (`RemediationCandidate`) | Candidate sets, not minimum sets |
| LEXON-Bench has 25 synthetic clauses | `data/processed/clauses.jsonl`; `src/lexon/benchmark/generate_synthetic.py` (`_build_clauses`); `tests/test_bench_determinism.py` | |
| LEXON-Bench has 30 system profiles | `data/processed/system_profiles.jsonl`; `src/lexon/benchmark/generate_synthetic.py` (`_build_profiles`); `tests/test_bench_determinism.py` | |
| LEXON-Bench has 750 benchmark instances | `data/processed/benchmark_instances.jsonl`; `scripts/reproduce_paper_results.py` | 25 × 30 pairs |
| Gold labels derived from formal definitions | `src/lexon/benchmark/gold.py` (`GoldOracle`); `data/processed/gold_labels.jsonl` | Canonical tie-breaking documented in `data_dictionary.md` |
| Train/dev/test split is 60/20/20, seed=42 | `src/lexon/benchmark/split.py`; `data/splits/`; `src/lexon/constants.py` (`RANDOM_SEED=42`) | Stratified by ambiguity flag |
| 8 ambiguous clauses identified | `src/lexon/benchmark/generate_synthetic.py` (8 clauses with `ambiguity_flag=True`); `src/lexon/constants.py` (`AMBIGUOUS_CLAUSE_IDS`) | Groups 2–5, 2 per group |
| Activation uses universal condition satisfaction (corrected) | `src/lexon/reasoning/engine.py` (R1b, R2); `rules/lexon_core_corrected.md`; `tests/test_activation_all_conditions.py::test_one_condition_satisfied_insufficient` | Paper §2.4 correction note |
| Stratified Datalog with negation-as-failure under CWA | `rules/lexon_core.dl`; `rules/lexon_core_corrected.md`; `docs/assumptions.md` | Python engine mirrors stratification |
| Baselines B1–B3 are implemented | `src/lexon/baselines/checklist.py` (B1); `src/lexon/baselines/ontology_only.py` (B2); `src/lexon/baselines/flat_rules.py` (B3) | |
| LLM baseline not reported unless executed | `src/lexon/baselines/llm_optional.py`; `outputs/audit/llm_baseline_status.json` | Disabled by default |
| Bootstrap CIs with 1000 iterations, seed=42 | `src/lexon/evaluation/bootstrap.py`; `outputs/results/metrics_synthetic.csv` | §2.10 |
| Evidentiary completeness ≠ legal compliance | `src/lexon/schemas.py` (docstring on `EvidenceSpec`); `docs/assumptions.md`; README disclaimer | §2.1, §4.4 |
| Evidence gap detection under CWA | `src/lexon/reasoning/engine.py` (R5); `docs/assumptions.md`; `tests/test_evidence_gaps.py::test_gap_detection_cwa_strict` | CWA documented throughout |
| Reproducibility: single command | `make reproduce`; `scripts/reproduce_paper_results.py`; `outputs/reports/reproducibility_report.md` | |
| Supplementary materials available | `lexon export-supplement`; `outputs/lexon_supplementary.zip` | Produced by `make supplement` |
| F1 scores reproduced from code | `outputs/tables/table_activation_gap.md`; `outputs/tables/table_ablation.md` | All tables generated from running code |

## What this repository does NOT claim

| Claim NOT made | Reason |
|:--------------|:-------|
| Legal compliance determination | LEXON evaluates evidentiary completeness only (§2.1) |
| External validity beyond the synthetic benchmark | Benchmark uses synthetic clauses; gold labels derived from same schema (§2.7) |
| Coverage of all EU AI Act obligations | Schema-coverage bound (Property 4); vocabulary is illustrative |
| Minimum-cardinality remediation sets | NP-hard conjecture; only candidates returned (§2.5) |
| LLM baseline results | Not executed; no API calls in default run (§2.9) |
| Temporal or resource conflict detection | Out of scope; future work (§4.4) |
