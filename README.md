# LEXON-Bench

[![CI](https://github.com/roy-saurabh/lexon-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/roy-saurabh/lexon-bench/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20399201.svg)](https://doi.org/10.5281/zenodo.20399201)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: CC-BY-4.0](https://img.shields.io/badge/Data-CC--BY--4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**Companion repository for:**
> Roy Saurabh. "LEXON: Executable AI Regulatory Obligation Reasoning with Typed Knowledge Graphs and Stratified Datalog." *MDPI Information*, 2026 (submitted).

---

> **LEXON is a research prototype for executable regulatory information reasoning.
> It does not provide legal advice and does not determine legal compliance.**

---

## What LEXON is

LEXON (Legal EXecutable Obligation Network) is a typed knowledge-graph and
stratified-Datalog framework for executable regulatory obligation reasoning. It
represents AI regulatory clauses, obligations, conditions, exceptions, evidence
specifications, and AI system profiles as typed entities, and executes four
reasoning tasks:

| Task | Description |
|------|-------------|
| T1 | Obligation activation — which obligations apply to a system? |
| T2 | Evidence-gap detection — which required evidence items are missing? |
| T3 | Conflict detection — which pairs of applicable obligations are incompatible? |
| T4 | Evidence-remediation candidates — which evidence additions close gaps? |

## Key results (seed=42, 150-instance held-out test set)

| System | T1 F1 | T2 F1 | T3 F1 |
|--------|-------|-------|-------|
| **LEXON (full)** | **1.000** | **1.000** | **0.957** |
| B1 Static checklist | 0.446 | 0.321 | 0.000 |
| B2 Ontology (no rules) | 0.054 | 0.000 | 0.000 |
| B3 Flat rules (no graph) | 0.660 | 0.533 | 0.000 |

T3 cross-clause conflict detection: TP=11, FP=1, FN=0 across 30 system profiles.
T1/T2 F1=1.000 is expected on this synthetic benchmark and confirms faithful implementation
of the formal semantics (see §2.7, §3.1 of the paper for full discussion).

> **LEXON-Bench is primarily an implementation-conformance benchmark, not an
> independent legal-validity benchmark.** Gold labels are derived from the same
> formal definitions as the LEXON engine; F1=1.000 on T1/T2 reflects faithful
> implementation of those definitions, not external legal-compliance validity.
> External validation on real regulatory provisions is future work.

Reproduce all results with one command: `make reproduce`

## What this repository reproduces

Running `make reproduce` from a clean clone will:

1. Generate LEXON-Bench: 25 synthetic clauses, 30 system profiles, 750 instances (seed=42)
2. Compute gold labels from formal definitions
3. Run LEXON full system and baselines B1–B3
4. Compute precision, recall, F1, and bootstrap 95% CIs for T1–T3
5. Generate paper-ready tables (`outputs/tables/`)
6. Generate figures (`outputs/figures/`)
7. Write a reproducibility report (`outputs/reports/reproducibility_report.md`)

## Installation

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/roy-saurabh/lexon-bench.git
cd lexon-bench
make setup          # installs uv + syncs dependencies
make test           # run test suite (~30s)
make reproduce      # full reproduction pipeline (~60s)
```

Or without uv:

```bash
pip install -e ".[dev]"
python scripts/reproduce_paper_results.py
```

## Docker (fully isolated)

```bash
docker-compose up lexon-bench
```

## Expected outputs

After `make reproduce`:

```
outputs/
  results/
    metrics_synthetic.csv          # Aggregate T1/T2/T3 metrics for all systems
    metrics_by_difficulty.csv      # Breakdown by profile difficulty (easy/medium/hard)
    lexon_predictions.jsonl        # LEXON full system predictions
    lexon_system_conflicts.jsonl   # Cross-clause conflict detection results
    checklist_predictions.jsonl    # B1 predictions
    ontology_predictions.jsonl     # B2 predictions
    flat_rules_predictions.jsonl   # B3 predictions
  tables/
    table_activation_gap.md        # Activation/gap metrics table (T1 + T2 with CIs)
    table_conflicts.md             # T3 conflict detection results
    table_ablation.md              # Ablation (§3.3)
  figures/
    pipeline.png                   # 5-stage LEXON pipeline diagram
    f1_by_task.png                 # F1 by task and system
    error_breakdown.png            # Benchmark construction quality audit
  reports/
    reproducibility_report.md      # Full report with metrics and confusion counts
  audit/
    llm_baseline_status.json       # LLM baseline execution record (not executed)
```

## Repository structure

```
lexon-bench/
├── src/lexon/
│   ├── schemas.py              # Pydantic models (Definitions 1–8)
│   ├── constants.py            # Evidence/action vocabulary, seeds
│   ├── io.py                   # JSONL serialisation helpers
│   ├── cli.py                  # CLI (typer)
│   ├── benchmark/
│   │   ├── generate_synthetic.py  # 25 clauses + 30 profiles
│   │   ├── split.py               # Deterministic train/dev/test split
│   │   ├── gold.py                # Gold oracle (formal definitions)
│   │   └── validators.py          # Benchmark integrity checks
│   ├── reasoning/
│   │   └── engine.py           # LexonEngine (Rules R1–R7)
│   ├── baselines/
│   │   ├── checklist.py        # B1: Static risk-level checklist
│   │   ├── ontology_only.py    # B2: Type-tag matching without inference
│   │   ├── flat_rules.py       # B3: Untyped rule engine
│   │   └── llm_optional.py     # LLM baseline (disabled by default)
│   └── evaluation/
│       ├── metrics.py          # Corpus-level P/R/F1 and confusion counts
│       ├── bootstrap.py        # Non-parametric bootstrap CIs (1000 iterations)
│       ├── compare.py          # Experimental statistical comparison utilities (unused in main paper)
│       ├── tables.py           # Paper-ready Markdown tables
│       └── figures.py          # Matplotlib figures
├── rules/
│   ├── lexon_core.dl           # Soufflé-compatible Datalog rules (R1–R7)
│   ├── lexon_core_corrected.md # Corrected universal activation explanation
│   └── incompatibility_axioms.yaml
├── data/
│   ├── raw/                    # Clause + profile specs, real-clause metadata
│   ├── processed/              # Generated JSONL files (benchmark instances, gold)
│   └── splits/                 # Train/dev/test instance IDs (seed=42)
├── tests/                      # pytest test suite (9 test modules)
├── scripts/
│   ├── reproduce_paper_results.py
│   └── check_no_placeholders.py
├── configs/
│   └── experiment_synthetic.yaml
├── docs/
│   ├── manuscript_alignment.md
│   ├── assumptions.md
│   └── mdpi_data_availability_statement.md
├── outputs/                    # Generated outputs (see above)
├── paper-txt/
│   └── LEXON_Information_MDPI.md  # Current manuscript draft
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── CITATION.cff
└── .zenodo.json                # Zenodo metadata for auto-archival
```

## Formal properties

| Property | Statement |
|----------|-----------|
| P1 Soundness | Every Applicable derivation matches Definition 4 |
| P2 Activation monotonicity | Positive profile additions cannot revoke applicability (except via new exception facts) |
| P3 Gap anti-monotonicity | Adding held evidence can only shrink or preserve the evidence-gap set |
| P4 Bounded completeness | Gap detection is complete within the evidence vocabulary (schema-coverage bound) |
| P5 Conflict soundness | Every reported conflict pair satisfies Definition 7 (direct action-incompatibility) |

## Closed-world assumptions

All evidence reasoning uses the **closed-world assumption (CWA)**:

- Any evidence item not listed in `evidence_held` is treated as **absent**.
- Any condition property absent from `profile.properties` is treated as **unknown**,
  yielding `Uncertain` activation status (three-valued semantics; Definition 4).
- This is a deliberate, auditable design choice. Open-world extensions are
  identified as future work.

See `docs/assumptions.md` for full documentation.

## Benchmark limitations

- All clauses are **synthetic** and do not reproduce official regulatory text verbatim.
- Gold labels are derived from the same structured schema as LEXON (evaluative circularity risk, §2.7, §4.4).
- Results reflect **internal benchmark validity**, not external legal-compliance validity.
- 8 of 25 clauses carry an ambiguity flag; canonical representation decisions are documented in `src/lexon/benchmark/gold.py`.
- Only direct action-incompatibility conflicts (T3) are implemented; temporal and resource conflicts are out of scope.

## Zenodo archival

This repository is configured for automatic Zenodo archival via `.zenodo.json`.

To set up Zenodo auto-archival for a fork or new deployment:

1. Go to [https://zenodo.org/account/settings/github/](https://zenodo.org/account/settings/github/) and authorise Zenodo.
2. Enable the `roy-saurabh/lexon-bench` repository in your Zenodo settings.
3. Creating a GitHub release will automatically trigger Zenodo archival and assign a DOI.
4. Update `CITATION.cff` and the Data Availability Statement in the manuscript with the resulting DOI.

## LLM baseline

The LLM baseline is **disabled by default**. To enable:

```bash
export LEXON_LLM_API_KEY=your-key
export LEXON_RUN_LLM_BASELINE=1
lexon run-baseline llm --run-llm-baseline
```

Results do NOT appear in any main results table unless the LLM baseline is executed
under a fixed-prompt, fixed-model-version, fixed-temperature reproducible protocol.
See `outputs/audit/llm_baseline_status.json` for the execution audit record.

## Citation

```bibtex
@article{saurabh2026lexon,
  title={{LEXON}: Executable {AI} Regulatory Obligation Reasoning with
         Typed Knowledge Graphs and Stratified {D}atalog},
  author={Saurabh, Roy},
  journal={Information},
  publisher={MDPI},
  year={2026},
  note={Submitted. DOI to be inserted upon acceptance.}
}
```

For the software repository:

```bibtex
@software{saurabh2026lexon_bench,
  title={{LEXON-Bench}: Executable {AI} Regulatory Obligation Reasoning
         --- Companion Benchmark Repository},
  author={Saurabh, Roy},
  year={2026},
  publisher={GitHub / Zenodo},
  url={https://github.com/roy-saurabh/lexon-bench},
  version={1.0.2}
}
```

## License

- Code: [MIT License](LICENSE)
- Synthetic benchmark data: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)

Synthetic clauses are NOT official legal text and do NOT constitute legal advice.

---

## Data Availability Statement (for manuscript)

> The synthetic benchmark instances, system profiles, Datalog rule specifications,
> baseline implementations, evaluation scripts, and generated results are openly
> available in the LEXON-Bench repository at
> https://github.com/roy-saurabh/lexon-bench and archived on Zenodo
> (DOI: https://doi.org/10.5281/zenodo.20399201). The benchmark data are synthetic
> and contain no personal data. Code is released under the MIT License; synthetic
> benchmark data are released under CC-BY-4.0.
