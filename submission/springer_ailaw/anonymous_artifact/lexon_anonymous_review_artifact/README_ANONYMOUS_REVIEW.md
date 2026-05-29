# LEXON Anonymous Review Artifact

This is the anonymized review artifact for a manuscript submitted to Artificial Intelligence and Law.

The public repository, author information, and persistent DOI are withheld during double-anonymous peer review. They will be supplied after review according to journal requirements.

## What this artifact contains

- Python reference implementation
- Synthetic conformance suite
- Structured obligation tuples
- Synthetic AI system profiles
- Conformance oracle labels
- Datalog-style rule specifications
- Baseline implementations
- Illustrative EU AI Act mapping
- Derivation-trace examples
- Reproduction scripts
- Formal-property tests

## What this artifact does not claim

This artifact does not provide legal advice, certify compliance, or constitute an expert-validated legal corpus. The EU AI Act mapping is illustrative only.

## Reproduction

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run:

```bash
make reproduce
make ailaw-artifact-check
```

## Expected conformance-suite results

| System | T1 F1 | T2 F1 | T3 F1 |
|---|---|---|---|
| LEXON full | 1.000 | 1.000 | 0.957 |
| B1 static checklist | 0.446 | 0.321 | 0.000 |
| B2 ontology only | 0.054 | 0.000 | 0.000 |
| B3 flat rules | 0.660 | 0.533 | 0.000 |

These are implementation-conformance results on synthetic data, not legal-validity results.
