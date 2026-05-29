"""
Pydantic data models for LEXON — typed knowledge-graph and Datalog reasoning framework.

All model validation uses Pydantic v2. The schema is faithful to the formal definitions
in the paper (Definitions 1–8, Appendix C).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Controlled vocabularies (enumerations)
# ---------------------------------------------------------------------------


class RiskLevel(str, Enum):
    UNACCEPTABLE = "Unacceptable"
    HIGH_RISK = "HighRisk"
    LIMITED_RISK = "LimitedRisk"
    MINIMAL_RISK = "MinimalRisk"
    UNDERSPECIFIED = "Underspecified"


class Domain(str, Enum):
    HEALTHCARE = "Healthcare"
    EMPLOYMENT = "Employment"
    EDUCATION = "Education"
    CRITICAL_INFRA = "CriticalInfra"
    BIOMETRIC = "Biometric"
    GENERAL = "General"
    PUBLIC_SERVICES = "PublicServices"
    RESEARCH = "Research"
    MIXED = "Mixed"
    FINANCIAL = "Financial"


class Actor(str, Enum):
    PROVIDER = "Provider"
    DEPLOYER = "Deployer"
    IMPORTER = "Importer"
    USER = "User"
    MIXED = "Mixed"


class Capability(str, Enum):
    GENERATIVE_AI = "GenerativeAI"
    CLASSIFICATION = "Classification"
    BIOMETRIC = "Biometric"
    DECISION_SUPPORT = "DecisionSupport"
    RECOMMENDATION = "Recommendation"
    CCTV = "CCTV"
    NLP = "NLP"
    COMPUTER_VISION = "ComputerVision"


class DeploymentContext(str, Enum):
    EU_MARKET = "EU_Market"
    NON_EU = "Non_EU"
    RESEARCH_EXEMPTION = "Research_Exemption"


class SourceInstrument(str, Enum):
    EU_AI_ACT = "EU_AI_Act"
    NIST_AI_RMF = "NIST_AI_RMF"
    ISO_42001 = "ISO_IEC_42001"
    GDPR = "GDPR"
    SYNTHETIC = "Synthetic"


class ApplicabilityStatus(str, Enum):
    APPLICABLE = "Applicable"
    NOT_APPLICABLE = "NotApplicable"
    UNCERTAIN = "Uncertain"


class EvidenceCompletenessStatus(str, Enum):
    COMPLETE = "EvidenceComplete"
    INCOMPLETE = "EvidenceIncomplete"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RemediationAction(str, Enum):
    ADD_EVIDENCE = "AddEvidence"
    UPDATE_STALE_EVIDENCE = "UpdateStaleEvidence"
    ESCALATE_FOR_HUMAN_REVIEW = "EscalateForHumanReview"
    CLARIFY_AMBIGUITY = "ClarifyAmbiguity"


# ---------------------------------------------------------------------------
# Core schema entities (Definition 1 – Definition 8)
# ---------------------------------------------------------------------------


class Condition(BaseModel):
    """A single activation condition on an obligation."""

    condition_id: str = Field(..., description="Unique condition identifier, e.g. C-001")
    predicate: str = Field(
        ...,
        description="Property name on the system profile (e.g. 'risk_level', 'capability')",
    )
    value: Any = Field(..., description="Required value or set of values")
    negated: bool = Field(
        False, description="If True, condition is satisfied when predicate!=value"
    )
    description: str = Field("", description="Human-readable description of this condition")


class ExceptionCondition(BaseModel):
    """An exception trigger that suppresses obligation applicability."""

    exception_id: str = Field(..., description="Unique exception identifier, e.g. X-001")
    predicate: str = Field(..., description="System property that triggers this exception")
    value: Any = Field(..., description="Value that triggers the exception")
    description: str = Field("", description="Human-readable description")


class EvidenceSpec(BaseModel):
    """A typed evidence artefact required by an obligation."""

    evidence_id: str = Field(
        ..., description="Controlled vocabulary ID, e.g. E-TechnicalDocumentation"
    )
    label: str = Field("", description="Human-readable label")
    description: str = Field("", description="What this artefact must contain")
    mandatory: bool = Field(True, description="False for recommended-only artefacts")


class Obligation(BaseModel):
    """
    Formal obligation tuple ⟨id, clause, actor, action, Cₒ, Xₒ, Eₒ⟩.

    Definition 2 from the paper.
    """

    obligation_id: str = Field(..., description="Unique obligation ID, e.g. OBL-001-1")
    clause_id: str = Field(..., description="Parent clause ID")
    actor: Actor = Field(..., description="Duty-bearer role")
    action: str = Field(..., description="Required action (vocabulary term)")
    conditions: list[Condition] = Field(
        default_factory=list,
        description="Conjunctive set of activation conditions Cₒ — ALL must be satisfied",
    )
    exceptions: list[ExceptionCondition] = Field(
        default_factory=list,
        description="Disjunctive set of exception triggers Xₒ — ANY fires to suppress",
    )
    required_evidence: list[EvidenceSpec] = Field(
        default_factory=list, description="Required evidence set Eₒ"
    )
    source_instrument: SourceInstrument = Field(SourceInstrument.SYNTHETIC)
    ambiguity_flag: bool = Field(
        False,
        description="True if clause text admits >1 plausible structured representation",
    )
    notes: str = Field("", description="Annotation notes, error categories, reviewer flags")


class RegulatoryClause(BaseModel):
    """
    A regulatory clause ⟨id, text, source, scope⟩.

    Definition 1 from the paper. Text field uses paraphrased synthetic language;
    does not reproduce official legal text verbatim.
    """

    clause_id: str = Field(..., description="Unique clause ID, e.g. CL-001")
    text: str = Field(
        ...,
        description=(
            "Paraphrased synthetic clause text. "
            "Not official legal text. Not legal advice."
        ),
    )
    source_instrument: SourceInstrument = Field(SourceInstrument.SYNTHETIC)
    thematic_group: str = Field("", description="Thematic group label")
    scope_risk_levels: list[RiskLevel] = Field(
        default_factory=list, description="Risk levels in declared applicability scope"
    )
    scope_domains: list[Domain] = Field(
        default_factory=list, description="Domains in declared applicability scope"
    )
    ambiguity_flag: bool = Field(False, description="Clause-level ambiguity indicator")
    obligations: list[Obligation] = Field(default_factory=list)
    notes: str = Field("")


class SystemProfile(BaseModel):
    """
    An AI system profile ⟨id, capabilities, domain, risk, actor, deployment, evidence⟩.

    Definition 3 from the paper and Appendix C schema.
    """

    system_id: str = Field(..., description="Unique system identifier, e.g. SYS-001")
    capabilities: list[Capability] = Field(default_factory=list)
    domain: Domain = Field(Domain.GENERAL)
    risk_level: RiskLevel = Field(RiskLevel.MINIMAL_RISK)
    actor: Actor = Field(Actor.PROVIDER)
    deployment_context: DeploymentContext = Field(DeploymentContext.EU_MARKET)
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Boolean profile properties: affectsNaturalPerson, isDeployed, "
            "hasResearchExemption, isExclusiveSelfUse, hasSystemicRisk, "
            "processesSpecialCategory, logsUnderControl"
        ),
    )
    evidence_held: list[str] = Field(
        default_factory=list,
        description=(
            "Set of evidence artefact IDs currently held by this system. "
            "Evaluated under closed-world assumption: any ID not listed is treated as absent."
        ),
    )
    profile_complete: bool = Field(
        True,
        description=(
            "True if all required profile fields are specified. "
            "Incomplete profiles yield Uncertain activation."
        ),
    )
    difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM)
    group_label: str = Field("")


class BenchmarkInstance(BaseModel):
    """A single clause–profile pair constituting one benchmark instance."""

    instance_id: str = Field(..., description="Unique instance ID, e.g. BENCH-0001")
    clause_id: str
    system_id: str
    split: str = Field(..., description="train | dev | test")
    difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM)
    ambiguous: bool = Field(False, description="True if clause carries ambiguity_flag")


class GoldLabels(BaseModel):
    """
    Gold-standard labels for a benchmark instance.

    Labels are derived from formal Definitions 4–7 applied to the structured tuples.
    For ambiguous clauses, canonical tie-breaking is documented in
    docs/data_dictionary.md.
    """

    instance_id: str
    clause_id: str
    system_id: str
    # T1 — activation status per obligation in this clause
    activation: dict[str, ApplicabilityStatus] = Field(
        default_factory=dict,
        description="Map obligation_id → ApplicabilityStatus",
    )
    # T2 — evidence gaps per obligation
    evidence_gaps: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map obligation_id → list[evidence_id] (gap set)",
    )
    # T3 — conflict pairs for this instance
    conflict_pairs: list[tuple[str, str]] = Field(
        default_factory=list,
        description="List of (obligation_id_1, obligation_id_2) conflict pairs",
    )
    # T4 — remediation candidates
    remediation_candidates: list[str] = Field(
        default_factory=list,
        description="Evidence IDs that, if obtained, would close one or more gaps",
    )
    canonical_notes: str = Field(
        "",
        description=(
            "For ambiguous instances, documents canonical tie-breaking rule applied. "
            "Blank for unambiguous instances."
        ),
    )


# ---------------------------------------------------------------------------
# Reasoning results
# ---------------------------------------------------------------------------


class ActivationTrace(BaseModel):
    """Derivation trace for a single obligation activation result."""

    obligation_id: str
    status: ApplicabilityStatus
    conditions_satisfied: list[str] = Field(default_factory=list)
    conditions_missing: list[str] = Field(default_factory=list)
    exceptions_fired: list[str] = Field(default_factory=list)
    derivation_rule: str = Field("", description="Rule that derived this result (R1–R4)")


class EvidenceGap(BaseModel):
    """A single evidence gap under the closed-world assumption."""

    obligation_id: str
    system_id: str
    evidence_id: str
    evidence_label: str = ""
    mandatory: bool = True


class ConflictPair(BaseModel):
    """A direct conflict between two applicable obligations (Definition 7)."""

    obligation_id_1: str
    obligation_id_2: str
    system_id: str
    action_1: str
    action_2: str
    shared_actor: str
    incompatibility_axiom: str = Field("", description="Axiom from incompatibility_axioms.yaml")


class RemediationCandidate(BaseModel):
    """
    An evidence-remediation candidate (Definition 8).

    Represents evidence additions that would close one or more gaps.
    Does NOT model substantive operational controls.
    """

    system_id: str
    evidence_id: str
    evidence_label: str = ""
    remediation_action: RemediationAction = RemediationAction.ADD_EVIDENCE
    closes_gaps_for: list[str] = Field(
        default_factory=list,
        description="obligation_ids for which this candidate closes a gap",
    )
    requires_human_review: bool = Field(
        False,
        description="True for ambiguous obligations requiring expert interpretation",
    )
    notes: str = ""


class ReasoningResult(BaseModel):
    """Complete reasoning output for a single clause–profile pair."""

    instance_id: str
    clause_id: str
    system_id: str
    # T1
    activation_traces: list[ActivationTrace] = Field(default_factory=list)
    # T2
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list)
    # T3
    conflict_pairs: list[ConflictPair] = Field(default_factory=list)
    # T4
    remediation_candidates: list[RemediationCandidate] = Field(default_factory=list)
    # Metadata
    engine_version: str = "1.0.0"
    closed_world_assumption: bool = Field(
        True,
        description=(
            "All reasoning uses CWA over evidence holdings. "
            "Evidence not listed in evidence_held is treated as absent."
        ),
    )

    @property
    def applicable_obligations(self) -> list[str]:
        return [
            t.obligation_id
            for t in self.activation_traces
            if t.status == ApplicabilityStatus.APPLICABLE
        ]

    @property
    def uncertain_obligations(self) -> list[str]:
        return [
            t.obligation_id
            for t in self.activation_traces
            if t.status == ApplicabilityStatus.UNCERTAIN
        ]


class CrossClauseConflict(BaseModel):
    """
    A cross-clause conflict between applicable obligations from different clauses.

    Definition 7 applied at the system (profile) level rather than the instance
    (clause–profile) level.  Cross-clause conflicts arise when two obligations from
    different regulatory instruments / clauses both activate for the same profile
    and their actions are incompatible under the LEXON incompatibility axioms.
    """

    system_id: str
    clause_id_1: str
    obligation_id_1: str
    action_1: str
    clause_id_2: str
    obligation_id_2: str
    action_2: str
    shared_actor: str
    incompatibility_axiom: str = Field("", description="Axiom that identifies the conflict")


class SystemConflictResult(BaseModel):
    """System-level (profile-level) cross-clause conflict detection result."""

    system_id: str
    cross_clause_conflicts: list[CrossClauseConflict] = Field(default_factory=list)

    @property
    def conflict_pair_keys(self) -> set[frozenset[str]]:
        return {
            frozenset([c.obligation_id_1, c.obligation_id_2])
            for c in self.cross_clause_conflicts
        }


class SystemConflictGold(BaseModel):
    """System-level gold labels for cross-clause conflict detection."""

    system_id: str
    # List of (obligation_id_1, obligation_id_2) gold conflict pairs
    conflict_pairs: list[tuple[str, str]] = Field(default_factory=list)

    @property
    def conflict_pair_keys(self) -> set[frozenset[str]]:
        return {frozenset([p[0], p[1]]) for p in self.conflict_pairs}


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


class InstanceMetrics(BaseModel):
    """Per-instance metrics for a single benchmark instance."""

    instance_id: str
    t1_precision: float | None = None
    t1_recall: float | None = None
    t1_f1: float | None = None
    t2_precision: float | None = None
    t2_recall: float | None = None
    t2_f1: float | None = None
    t3_conflict_precision: float | None = None
    t3_conflict_recall: float | None = None
    t3_conflict_f1: float | None = None
    ambiguous: bool = False
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class AggregateMetrics(BaseModel):
    """Aggregate metrics across the benchmark split."""

    system_name: str
    split: str
    n_instances: int
    # T1
    t1_precision: float
    t1_recall: float
    t1_f1: float
    t1_precision_ci_lo: float
    t1_precision_ci_hi: float
    t1_recall_ci_lo: float
    t1_recall_ci_hi: float
    t1_f1_ci_lo: float
    t1_f1_ci_hi: float
    # T2
    t2_precision: float
    t2_recall: float
    t2_f1: float
    t2_precision_ci_lo: float
    t2_precision_ci_hi: float
    t2_recall_ci_lo: float
    t2_recall_ci_hi: float
    t2_f1_ci_lo: float
    t2_f1_ci_hi: float
    # T3
    t3_precision: float
    t3_recall: float
    t3_f1: float
    # FN rate for evidence gaps
    t2_false_negative_rate: float
