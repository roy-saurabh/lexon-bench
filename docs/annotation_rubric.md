# LEXON Obligation Annotation Rubric

## Purpose

This rubric defines how natural-language regulatory clauses are decomposed into LEXON obligation tuples.

The rubric supports reproducible modelling. It does not establish authoritative legal interpretation.

## Tuple fields

Each obligation tuple contains:

- `clause_id`
- `source_instrument`
- `actor`
- `action`
- `activation_conditions`
- `exceptions`
- `required_evidence`
- `ambiguity_flag`
- `human_review_reason`

## Decision rules

### Actor extraction

Identify the legal or operational actor to whom the obligation is addressed. If the clause distributes responsibility across multiple actors, decompose into actor-specific obligations where possible. Use `Mixed` only when the actor cannot be decomposed without interpretive judgement.

### Action extraction

Represent the deontic content as an action token. Prefer stable controlled-vocabulary actions over natural-language paraphrases.

### Condition extraction

Represent applicability requirements as predicate-value conditions. Conditions should be conjunctive unless the clause explicitly introduces alternatives.

### Exception extraction

Represent narrowing provisions, exemptions, or carve-outs as exceptions rather than as independent obligations when they defeat or suspend applicability.

### Evidence mapping

Map documentation, records, logs, assessments, reports, instructions, and policies to `EvidenceSpec` objects. Evidence completeness is not substantive compliance.

### Ambiguity flagging

Set `ambiguity_flag = true` when:

- actor attribution is contested;
- a condition has multiple plausible interpretations;
- a clause mixes obligations and exceptions;
- evidence sufficiency depends on domain-specific judgement;
- legal interpretation is required before executable encoding.

### Human review

Every ambiguity-flagged tuple must include a `human_review_reason`.

## Limitations

The rubric supports formal modelling and implementation conformance. It does not create an expert-validated legal corpus.
