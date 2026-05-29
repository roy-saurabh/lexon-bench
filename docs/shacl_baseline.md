# SHACL Baseline

The SHACL baseline validates graph-shape constraints and evidence-presence shapes. It is included as a semantic-web comparator.

**Status: optional stub.** RDFLib/pySHACL are listed under `[project.optional-dependencies] rdf` in `pyproject.toml`. The baseline script is provided but not required for the main reproduction pipeline.

## What the SHACL baseline does

Validates SHACL shapes against a knowledge-graph serialisation of each AI system profile. Checks:

- required evidence fields are present in the graph;
- actor type constraints are satisfied;
- system-profile structure matches declared shapes.

## What the SHACL baseline does not implement

- stratified activation semantics;
- exception firing;
- three-valued applicability;
- canonical conflict-pair generation;
- LEXON derivation traces.

Therefore the SHACL baseline is not expected to match LEXON on T1/T2/T3 conformance results. Its role is a semantic-web representation comparator only.

## Files

- `rules/shacl/evidence_shapes.ttl` — SHACL shape definitions (stub)
- `src/lexon/baselines/shacl_validator.py` — validation script (stub, requires `rdflib` extra)

## Installation

```bash
pip install -e ".[rdf]"
```
