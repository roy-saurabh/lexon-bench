# Illustrative EU AI Act Mapping

This document provides a small illustrative mapping from selected EU AI Act provisions to LEXON tuple concepts.

**This mapping is not an adjudicated legal corpus. It does not reproduce official legal text verbatim. It does not provide legal advice. It demonstrates how selected provisions can be represented using the LEXON vocabulary.**

The authoritative legal text remains the official EU AI Act.

## Illustrative provision table

| Provision | Actor | Obligation action | Condition | Evidence object | Exception / limitation | LEXON construct | Validation status |
|-----------|-------|------------------|-----------|-----------------|----------------------|-----------------|-------------------|
| EUAI-ART-09 | Provider | Maintain risk-management system | High-risk AI system | RiskManagementPlan | Scope depends on system classification | Obligation+Condition+EvidenceSpec | Illustrative only |
| EUAI-ART-10 | Provider | Apply data governance measures | High-risk AI system using data | DataGovernanceRecord | Evidence sufficiency is context-dependent | Obligation+Condition+EvidenceSpec | Illustrative only |
| EUAI-ART-11 | Provider | Maintain technical documentation | High-risk AI system | TechnicalDocumentation | Annex IV details require decomposition | Obligation+EvidenceSpec | Illustrative only |
| EUAI-ART-13 | Provider | Provide transparency / instructions for use | High-risk AI system | InstructionsForUse | Interpretive detail remains legal | Obligation+EvidenceSpec | Illustrative only |
| EUAI-ART-14 | Provider/Deployer | Enable human oversight | High-risk AI system | HumanOversightProtocol | Role allocation may require legal interpretation | Obligation+Actor+Condition | Illustrative only |
| EUAI-ART-15 | Provider | Ensure accuracy, robustness, cybersecurity | High-risk AI system | RobustnessEvaluationReport | Thresholds are domain-specific | Obligation+EvidenceSpec | Illustrative only |
| EUAI-ANNEX-IV | Provider | Prepare technical documentation | High-risk AI system | AnnexIVDocumentation | Sub-items require structured decomposition | EvidenceSpec hierarchy | Illustrative only |

## Machine-readable files

- `data/illustrative/eu_ai_act_mapping.csv` — CSV format
- `data/illustrative/eu_ai_act_mapping.jsonl` — JSONL format

Validation script: `scripts/validate_illustrative_mapping.py`

## Validation status

Every row carries `validation_status = "Illustrative mapping only"`. None of these rows have been reviewed by legal experts. None constitute legal advice. None constitute authoritative interpretation of the EU AI Act.
