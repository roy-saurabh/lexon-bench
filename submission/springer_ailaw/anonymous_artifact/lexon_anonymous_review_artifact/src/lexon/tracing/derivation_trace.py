"""
LEXON derivation trace writer.

Generates canonical derivation trace examples for the four trace types:
Applicable, NotApplicable, Uncertain, and Conflict.

These traces are illustrative conformance examples derived from known
conformance cases. They are not legal opinions.
"""

from __future__ import annotations

import json
from pathlib import Path


_NOTE = "Research trace generated from conformance suite. Not legal advice."


def build_applicable_trace() -> dict:
    return {
        "trace_id": "TRACE-001",
        "trace_type": "activation",
        "clause_id": "CL-002",
        "obligation_id": "OBL-002-01",
        "system_id": "SYS-007",
        "activation_status": "Applicable",
        "actor_match": True,
        "conditions": [
            {
                "predicate": "riskLevel",
                "expected": "HighRisk",
                "observed": "HighRisk",
                "truth_value": "true",
            },
            {
                "predicate": "deploymentSector",
                "expected": "Healthcare",
                "observed": "Healthcare",
                "truth_value": "true",
            },
        ],
        "exceptions_fired": [],
        "required_evidence": ["RiskManagementPlan", "TechnicalDocumentation"],
        "held_evidence": ["RiskManagementPlan", "TechnicalDocumentation"],
        "evidence_gaps": [],
        "rules_fired": ["R1", "R2", "R4"],
        "human_review_required": False,
        "notes": _NOTE,
    }


def build_not_applicable_trace() -> dict:
    return {
        "trace_id": "TRACE-002",
        "trace_type": "activation",
        "clause_id": "CL-002",
        "obligation_id": "OBL-002-01",
        "system_id": "SYS-013",
        "activation_status": "NotApplicable",
        "actor_match": True,
        "conditions": [
            {
                "predicate": "riskLevel",
                "expected": "HighRisk",
                "observed": "LimitedRisk",
                "truth_value": "false",
            },
            {
                "predicate": "deploymentSector",
                "expected": "Healthcare",
                "observed": "Retail",
                "truth_value": "false",
            },
        ],
        "exceptions_fired": [],
        "required_evidence": ["RiskManagementPlan", "TechnicalDocumentation"],
        "held_evidence": [],
        "evidence_gaps": [],
        "rules_fired": ["R1", "R1b"],
        "human_review_required": False,
        "notes": _NOTE,
    }


def build_uncertain_trace() -> dict:
    return {
        "trace_id": "TRACE-003",
        "trace_type": "activation",
        "clause_id": "CL-010",
        "obligation_id": "OBL-010-02",
        "system_id": "SYS-027",
        "activation_status": "Uncertain",
        "actor_match": True,
        "conditions": [
            {
                "predicate": "riskLevel",
                "expected": "HighRisk",
                "observed": None,
                "truth_value": "unknown",
            },
            {
                "predicate": "hasAutonomousDecision",
                "expected": "true",
                "observed": "true",
                "truth_value": "true",
            },
        ],
        "exceptions_fired": [],
        "required_evidence": ["RiskAssessmentReport", "HumanOversightProtocol"],
        "held_evidence": ["HumanOversightProtocol"],
        "evidence_gaps": ["RiskAssessmentReport"],
        "rules_fired": ["R1", "R2"],
        "human_review_required": True,
        "notes": (
            "Activation status is Uncertain because riskLevel property is absent "
            "from system profile (three-valued semantics, Definition 4). "
            + _NOTE
        ),
    }


def build_conflict_trace() -> dict:
    return {
        "trace_id": "TRACE-004",
        "trace_type": "conflict",
        "clause_id": None,
        "obligation_id_1": "OBL-005-01",
        "obligation_id_2": "OBL-017-01",
        "system_id": "SYS-004",
        "activation_status": None,
        "actor_match": True,
        "conditions": [],
        "exceptions_fired": [],
        "required_evidence": [],
        "held_evidence": [],
        "evidence_gaps": [],
        "rules_fired": ["R6"],
        "conflict_reason": (
            "OBL-005-01 requires action PROHIBIT_AUTOMATED_DECISION; "
            "OBL-017-01 requires action REQUIRE_AUTOMATED_DECISION. "
            "These actions are declared incompatible in the incompatibility vocabulary."
        ),
        "human_review_required": True,
        "notes": _NOTE,
    }


def write_trace_examples(output_dir: str | Path = "outputs/traces") -> list[Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    traces = {
        "trace_applicable_CL-002_SYS-007.json": build_applicable_trace(),
        "trace_not_applicable_CL-002_SYS-013.json": build_not_applicable_trace(),
        "trace_uncertain_CL-010_SYS-027.json": build_uncertain_trace(),
        "trace_conflict_example.json": build_conflict_trace(),
    }

    written = []
    for filename, trace in traces.items():
        path = out / filename
        path.write_text(json.dumps(trace, indent=2))
        written.append(path)

    return written
