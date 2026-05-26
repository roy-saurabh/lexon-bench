"""
Deterministic synthetic benchmark generator for LEXON-Bench.

Generates:
  - 25 synthetic regulatory clauses (5 thematic groups, 8 ambiguous)
  - 30 synthetic AI system profiles (5 risk/domain groups)
  - 750 benchmark instances (all clause–profile pairs)

All generation is deterministic with seed=42 (RANDOM_SEED from constants).

IMPORTANT: Synthetic clauses are NOT official legal text and do NOT constitute
legal advice.  They are purpose-built for evaluating the LEXON reasoning engine.
"""

from __future__ import annotations

import random
from typing import Any

from lexon.constants import (
    AMBIGUOUS_CLAUSE_IDS,
    RANDOM_SEED,
)
from lexon.schemas import (
    Actor,
    BenchmarkInstance,
    Capability,
    Condition,
    DeploymentContext,
    DifficultyLevel,
    Domain,
    EvidenceSpec,
    ExceptionCondition,
    Obligation,
    RegulatoryClause,
    RiskLevel,
    SourceInstrument,
    SystemProfile,
)


# ---------------------------------------------------------------------------
# Clause definitions — 25 synthetic clauses across 5 thematic groups
# Each condition set is conjunctive (ALL must be satisfied).
# Each exception set is disjunctive (ANY fires to suppress).
# ---------------------------------------------------------------------------


def _build_clauses() -> list[RegulatoryClause]:
    """Return the complete list of 25 synthetic regulatory clauses."""

    def cond(cid: str, pred: str, val: Any, desc: str = "", neg: bool = False) -> Condition:
        return Condition(
            condition_id=cid, predicate=pred, value=val, negated=neg, description=desc
        )

    def exc(eid: str, pred: str, val: Any, desc: str = "") -> ExceptionCondition:
        return ExceptionCondition(exception_id=eid, predicate=pred, value=val, description=desc)

    def ev(eid: str, label: str = "", mandatory: bool = True) -> EvidenceSpec:
        return EvidenceSpec(evidence_id=eid, label=label or eid, mandatory=mandatory)

    def obl(
        oid: str,
        cid: str,
        actor: Actor,
        action: str,
        conditions: list[Condition],
        exceptions: list[ExceptionCondition],
        evidence: list[EvidenceSpec],
        source: SourceInstrument = SourceInstrument.SYNTHETIC,
        ambiguous: bool = False,
        notes: str = "",
    ) -> Obligation:
        return Obligation(
            obligation_id=oid,
            clause_id=cid,
            actor=actor,
            action=action,
            conditions=conditions,
            exceptions=exceptions,
            required_evidence=evidence,
            source_instrument=source,
            ambiguity_flag=ambiguous,
            notes=notes,
        )

    clauses: list[RegulatoryClause] = []

    # ---- Group 1: Transparency and information obligations (CL-001–CL-005) ----

    clauses.append(RegulatoryClause(
        clause_id="CL-001",
        text=(
            "Synthetic clause (not official legal text): Providers of AI systems that "
            "interact with natural persons through natural-language interfaces must notify "
            "users that they are interacting with an AI system, unless such disclosure is "
            "apparent from context. Research-exempt systems are excluded."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Transparency and information",
        scope_risk_levels=[RiskLevel.HIGH_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-001-1", "CL-001", Actor.PROVIDER,
                "ACT-NotifyUsersOfNLP",
                conditions=[
                    cond("C-001-1", "capability", "NLP", "System uses NLP capability"),
                    cond("C-001-2", "isDeployed", True, "System is deployed"),
                    cond("C-001-3", "affectsNaturalPerson", True, "System interacts with persons"),
                ],
                exceptions=[exc("X-001-1", "hasResearchExemption", True, "Research exemption applies")],
                evidence=[ev("E-UserNotificationPolicy"), ev("E-DeploymentRecord")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-002",
        text=(
            "Synthetic clause: Providers of high-risk AI systems must maintain "
            "comprehensive technical documentation throughout the system lifecycle. "
            "This obligation applies regardless of deployment status once the system "
            "has been placed on the market."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Transparency and information",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-002-1", "CL-002", Actor.PROVIDER,
                "ACT-MaintainTechnicalDocumentation",
                conditions=[
                    cond("C-002-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-002-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-TechnicalDocumentation"), ev("E-RiskAssessment")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-003",
        text=(
            "Synthetic clause: Providers of high-risk AI systems must provide deployers "
            "with instructions for use that enable safe and intended deployment. "
            "This obligation does not apply where the provider is the exclusive user "
            "of the system."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Transparency and information",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-003-1", "CL-003", Actor.PROVIDER,
                "ACT-ProvideDeployerInstructions",
                conditions=[
                    cond("C-003-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-003-2", "actor", "Provider", "Role is provider"),
                ],
                exceptions=[exc("X-003-1", "isExclusiveSelfUse", True, "Provider is sole user")],
                evidence=[ev("E-DeployerInstructions"), ev("E-SystemCard")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-004",
        text=(
            "Synthetic clause: Providers deploying systems with generative AI capabilities "
            "must disclose to end users, at the point of interaction, that content is "
            "AI-generated, and must maintain a content policy governing generated outputs."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Transparency and information",
        scope_risk_levels=[RiskLevel.LIMITED_RISK, RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-004-1", "CL-004", Actor.PROVIDER,
                "ACT-DiscloseGenerativeAICapabilities",
                conditions=[
                    cond("C-004-1", "capability", "GenerativeAI", "System is generative AI"),
                    cond("C-004-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-CapabilityDisclosure"), ev("E-ContentPolicy")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-005",
        text=(
            "Synthetic clause: Providers of high-risk AI systems exhibiting systemic "
            "risk must notify the relevant national authority of any serious incident "
            "or malfunction within prescribed timeframes after the system is deployed."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Transparency and information",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-005-1", "CL-005", Actor.PROVIDER,
                "ACT-NotifyIncidentsToAuthority",
                conditions=[
                    cond("C-005-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-005-2", "hasSystemicRisk", True, "System has systemic risk"),
                    cond("C-005-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-IncidentLog"), ev("E-NationalAuthorityContact")],
            )
        ],
    ))

    # ---- Group 2: Risk management and conformity assessment (CL-006–CL-010) ----

    clauses.append(RegulatoryClause(
        clause_id="CL-006",
        text=(
            "Synthetic clause: Providers of high-risk AI systems incorporating biometric "
            "capabilities must conduct a conformity assessment procedure before placing "
            "the system on the market. Research-exempt systems are excluded."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Risk management and conformity assessment",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.BIOMETRIC],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-006-1", "CL-006", Actor.PROVIDER,
                "ACT-ConductConformityAssessment",
                conditions=[
                    cond("C-006-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-006-2", "capability", "Biometric", "System uses biometrics"),
                    cond("C-006-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-006-1", "hasResearchExemption", True, "Research exemption")],
                evidence=[ev("E-ConformityAssessment"), ev("E-CertificationDocument")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-007",
        text=(
            "Synthetic clause: Providers of high-risk AI systems must implement, document, "
            "and maintain a risk management system throughout the system lifecycle, "
            "covering foreseeable risks to health, safety, and fundamental rights."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Risk management and conformity assessment",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-007-1", "CL-007", Actor.PROVIDER,
                "ACT-ImplementRiskManagementSystem",
                conditions=[
                    cond("C-007-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-007-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-RiskManagementPlan"), ev("E-RiskAssessment")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-008",
        text=(
            "Synthetic clause: Providers of high-risk AI systems deployed in healthcare "
            "contexts must conduct post-market monitoring to detect adverse events and "
            "update the risk management documentation accordingly."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Risk management and conformity assessment",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.HEALTHCARE],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-008-1", "CL-008", Actor.PROVIDER,
                "ACT-ConductPostMarketMonitoring",
                conditions=[
                    cond("C-008-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-008-2", "isDeployed", True, "System is deployed"),
                    cond("C-008-3", "domain", "Healthcare", "Domain is healthcare"),
                ],
                exceptions=[],
                evidence=[ev("E-MonitoringPlan"), ev("E-PostMarketReport")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-009",
        text=(
            "Synthetic clause [AMBIGUOUS — 'where appropriate']: Providers of high-risk "
            "AI systems with systemic risk characteristics should, where appropriate, "
            "undergo third-party audits by accredited conformity assessment bodies. "
            "The phrase 'where appropriate' introduces activation ambiguity: it may "
            "require case-by-case determination by the competent authority."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Risk management and conformity assessment",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: 'where appropriate' is interpretive. "
            "Canonical tie-breaking (gold oracle): treat as mandatory when hasSystemicRisk=True. "
            "LEXON strict logic: activates on conditions without canonical disambiguation, "
            "may yield false negatives on profiles where systemic risk is borderline."
        ),
        obligations=[
            obl(
                "OBL-009-1", "CL-009", Actor.PROVIDER,
                "ACT-UndergoThirdPartyAudit",
                conditions=[
                    cond("C-009-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-009-2", "hasSystemicRisk", True, "System has systemic risk"),
                ],
                exceptions=[exc("X-009-1", "hasResearchExemption", True, "Research exemption")],
                evidence=[ev("E-AuditReport")],
                ambiguous=True,
                notes="Ambiguous activation: 'where appropriate' requires authority determination",
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-010",
        text=(
            "Synthetic clause [AMBIGUOUS — dual actor]: High-risk AI system providers "
            "must ensure deployer compliance with obligations, and deployers must implement "
            "provider instructions. The scope boundary between provider and deployer "
            "obligations is not fully specified in all deployment configurations."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Risk management and conformity assessment",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: Dual-actor clause. "
            "Canonical tie-breaking: provider obligation always activates; "
            "deployer obligation activates unless isExclusiveSelfUse=True. "
            "LEXON actor-attribution errors occur on profiles with Mixed actor."
        ),
        obligations=[
            obl(
                "OBL-010-1", "CL-010", Actor.PROVIDER,
                "ACT-EnsureDeployerCompliance",
                conditions=[
                    cond("C-010-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-010-2", "actor", "Provider", "Role is provider"),
                ],
                exceptions=[],
                evidence=[ev("E-DeployerAgreement")],
                ambiguous=True,
                notes="Actor-attribution ambiguity: dual-actor clause",
            ),
            obl(
                "OBL-010-2", "CL-010", Actor.DEPLOYER,
                "ACT-ImplementProviderInstructions",
                conditions=[
                    cond("C-010-3", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-010-4", "actor", "Deployer", "Role is deployer"),
                ],
                exceptions=[exc("X-010-1", "isExclusiveSelfUse", True, "Provider is sole user")],
                evidence=[ev("E-ImplementationRecord")],
                ambiguous=True,
                notes="Actor-attribution ambiguity: may conflict with OBL-010-1 scope",
            ),
        ],
    ))

    # ---- Group 3: Special-category data handling (CL-011–CL-015) ----

    clauses.append(RegulatoryClause(
        clause_id="CL-011",
        text=(
            "Synthetic clause: Providers of AI systems that incorporate biometric "
            "processing capabilities must implement data minimization measures "
            "limiting biometric data collection to what is strictly necessary "
            "for the declared purpose."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Special-category data handling",
        scope_risk_levels=[RiskLevel.HIGH_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.BIOMETRIC],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-011-1", "CL-011", Actor.PROVIDER,
                "ACT-MinimizeBiometricData",
                conditions=[
                    cond("C-011-1", "capability", "Biometric", "System uses biometrics"),
                    cond("C-011-2", "processesSpecialCategory", True, "Processes special data"),
                ],
                exceptions=[],
                evidence=[ev("E-DataMinimizationPolicy"), ev("E-PrivacyImpactAssessment")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-012",
        text=(
            "Synthetic clause: Providers deploying AI systems that process special-category "
            "personal data must conduct a data protection impact assessment prior to "
            "deployment, unless a research exemption applies."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Special-category data handling",
        scope_risk_levels=[RiskLevel.HIGH_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-012-1", "CL-012", Actor.PROVIDER,
                "ACT-ConductDPIA",
                conditions=[
                    cond("C-012-1", "processesSpecialCategory", True, "Processes special data"),
                    cond("C-012-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-012-1", "hasResearchExemption", True, "Research exemption")],
                evidence=[ev("E-PrivacyImpactAssessment"), ev("E-DataProcessingAgreement")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-013",
        text=(
            "Synthetic clause [AMBIGUOUS — 'adequate protection']: Providers of AI systems "
            "deployed in the EU market that involve international transfer of special-category "
            "data must ensure adequate protection for such transfers. The scope of 'adequate "
            "protection' requires case-by-case legal assessment."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Special-category data handling",
        scope_risk_levels=[RiskLevel.HIGH_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: 'adequate protection' is interpretive. "
            "Canonical tie-breaking: mandatory when processesSpecialCategory=True AND deployment=EU_Market. "
            "LEXON errors: vocabulary mismatch on non-standard transfer mechanisms."
        ),
        obligations=[
            obl(
                "OBL-013-1", "CL-013", Actor.PROVIDER,
                "ACT-EnsureDataTransferProtection",
                conditions=[
                    cond("C-013-1", "processesSpecialCategory", True, "Processes special data"),
                    cond("C-013-2", "deployment_context", "EU_Market", "Deployed in EU market"),
                ],
                exceptions=[],
                evidence=[ev("E-DataTransferMechanism")],
                ambiguous=True,
                notes="Vocabulary mismatch: 'adequate protection' scope ambiguity",
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-014",
        text=(
            "Synthetic clause: Providers of AI systems that affect natural persons through "
            "processing of special-category data must implement procedures enabling data "
            "subjects to exercise their rights of access, rectification, and erasure."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Special-category data handling",
        scope_risk_levels=[RiskLevel.HIGH_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-014-1", "CL-014", Actor.PROVIDER,
                "ACT-SupportDataSubjectRights",
                conditions=[
                    cond("C-014-1", "processesSpecialCategory", True, "Processes special data"),
                    cond("C-014-2", "affectsNaturalPerson", True, "Affects natural persons"),
                ],
                exceptions=[],
                evidence=[ev("E-DataSubjectRightsPolicy"), ev("E-ConsentRecord")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-015",
        text=(
            "Synthetic clause [AMBIGUOUS — research exemption boundary]: Providers of AI "
            "systems in research domains must register the system with the relevant authority "
            "unless the system qualifies for a research exemption. The boundary of the "
            "research exemption for commercial research activities is not fully specified."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Special-category data handling",
        scope_risk_levels=[RiskLevel.MINIMAL_RISK, RiskLevel.LIMITED_RISK],
        scope_domains=[Domain.RESEARCH],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: Research exemption scope for commercial research is unclear. "
            "Canonical tie-breaking: hasResearchExemption=True suppresses obligation. "
            "LEXON errors: exception-scope mis-attribution on commercial research profiles."
        ),
        obligations=[
            obl(
                "OBL-015-1", "CL-015", Actor.PROVIDER,
                "ACT-RegisterResearchUse",
                conditions=[
                    cond("C-015-1", "domain", "Research", "Domain is research"),
                    cond("C-015-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-015-1", "hasResearchExemption", True, "Research exemption")],
                evidence=[ev("E-ResearchRegistration")],
                ambiguous=True,
                notes="Exception-scope mis-attribution risk for commercial research",
            )
        ],
    ))

    # ---- Group 4: Human oversight and HITL (CL-016–CL-020) ----

    clauses.append(RegulatoryClause(
        clause_id="CL-016",
        text=(
            "Synthetic clause: Providers of high-risk AI systems with decision-support "
            "capabilities must implement a human override capability enabling authorised "
            "operators to interrupt, override, or shut down the system."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Human oversight and human-in-the-loop",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-016-1", "CL-016", Actor.PROVIDER,
                "ACT-ImplementHumanOverride",
                conditions=[
                    cond("C-016-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-016-2", "capability", "DecisionSupport", "System supports decisions"),
                    cond("C-016-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-HumanOverrideDoc"), ev("E-OverrideProcedure")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-017",
        text=(
            "Synthetic clause: Deployers of high-risk AI systems with decision-support "
            "capabilities affecting natural persons must ensure that a qualified human "
            "reviews automated decisions before they are implemented."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Human oversight and human-in-the-loop",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-017-1", "CL-017", Actor.DEPLOYER,
                "ACT-ConductHumanReview",
                conditions=[
                    cond("C-017-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-017-2", "capability", "DecisionSupport", "System supports decisions"),
                    cond("C-017-3", "affectsNaturalPerson", True, "Affects natural persons"),
                ],
                exceptions=[],
                evidence=[ev("E-HumanReviewRecord"), ev("E-HumanReviewPolicy")],
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-018",
        text=(
            "Synthetic clause [AMBIGUOUS — override vs. monitoring threshold]: High-risk AI "
            "system providers must implement either full human override capability or a "
            "real-time monitoring mechanism, depending on operational context. The threshold "
            "between requiring override versus monitoring is not precisely specified."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Human oversight and human-in-the-loop",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: Override vs. monitoring threshold is interpretive. "
            "Canonical tie-breaking: activate for all HighRisk deployed systems. "
            "Exception: GenerativeAI systems may use monitoring instead of override. "
            "LEXON errors: vocabulary ambiguity on combined override-monitoring obligation."
        ),
        obligations=[
            obl(
                "OBL-018-1", "CL-018", Actor.PROVIDER,
                "ACT-ImplementHumanOversight",
                conditions=[
                    cond("C-018-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-018-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-018-1", "capability", "GenerativeAI",
                                "GenAI may use monitoring instead of full override")],
                evidence=[ev("E-HumanOversightDoc")],
                ambiguous=True,
                notes="Ambiguous: override vs. monitoring threshold unclear",
            )
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-019",
        text=(
            "Synthetic clause: Providers of high-risk AI systems with audit logging under "
            "operator control must document human-in-the-loop procedures and maintain "
            "records of oversight interventions."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Human oversight and human-in-the-loop",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-019-1", "CL-019", Actor.PROVIDER,
                "ACT-DocumentHITLProcedures",
                conditions=[
                    cond("C-019-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-019-2", "logsUnderControl", True, "Logs under operator control"),
                ],
                exceptions=[],
                evidence=[ev("E-HITLProcedureDoc"), ev("E-OversightLog")],
            ),
            obl(
                "OBL-019-CF1", "CL-019", Actor.PROVIDER,
                "ACT-RequireHumanOverride",
                conditions=[
                    cond("C-019-CF1-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-019-CF1-2", "logsUnderControl", True, "Logs under operator control"),
                ],
                exceptions=[],
                evidence=[ev("E-OverrideProcedure")],
                notes=(
                    "Conflict-forming obligation: HITL compliance requires human override "
                    "enforcement for all automated outputs where logs are under control. "
                    "Creates cross-clause conflicts with ACT-FullAutomatedDecision obligations."
                ),
            ),
            obl(
                "OBL-019-CF2", "CL-019", Actor.PROVIDER,
                "ACT-MinimiseDataRetention",
                conditions=[
                    cond("C-019-CF2-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-019-CF2-2", "logsUnderControl", True, "Logs under operator control"),
                ],
                exceptions=[],
                evidence=[ev("E-DataMinimizationPolicy")],
                notes=(
                    "Conflict-forming obligation: HITL log-control obligations require "
                    "strict data minimisation. Creates cross-clause conflicts with "
                    "ACT-RetainDataMaximal obligations."
                ),
            ),
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-020",
        text=(
            "Synthetic clause [AMBIGUOUS — 'sufficient oversight']: Deployers of high-risk "
            "AI systems affecting natural persons must demonstrate sufficient oversight of "
            "AI-assisted decisions. The standard for 'sufficiency' is not quantitatively "
            "defined and requires contextual assessment."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Human oversight and human-in-the-loop",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: 'Sufficient oversight' is interpretive. "
            "Canonical tie-breaking: activate when Deployer + HighRisk + affectsNaturalPerson. "
            "LEXON errors: actor-attribution errors on dual-role profiles."
        ),
        obligations=[
            obl(
                "OBL-020-1", "CL-020", Actor.DEPLOYER,
                "ACT-DemonstrateOversight",
                conditions=[
                    cond("C-020-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-020-2", "actor", "Deployer", "Role is deployer"),
                    cond("C-020-3", "affectsNaturalPerson", True, "Affects natural persons"),
                ],
                exceptions=[],
                evidence=[ev("E-OversightDemonstrationRecord")],
                ambiguous=True,
                notes="Actor-attribution ambiguity: deployer vs. provider split",
            )
        ],
    ))

    # ---- Group 5: Cross-instrument provisions (CL-021–CL-025) ----

    clauses.append(RegulatoryClause(
        clause_id="CL-021",
        text=(
            "Synthetic clause: Providers of high-risk AI systems deployed in the EU market "
            "must map their technical and organisational controls to the NIST AI Risk "
            "Management Framework governance functions and maintain a current control registry."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Cross-instrument provisions",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-021-1", "CL-021", Actor.PROVIDER,
                "ACT-MapControlsToNIST",
                conditions=[
                    cond("C-021-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-021-2", "deployment_context", "EU_Market", "EU market deployment"),
                ],
                exceptions=[],
                evidence=[ev("E-NISTMapping"), ev("E-ControlRegistry")],
            ),
            obl(
                "OBL-021-CF1", "CL-021", Actor.PROVIDER,
                "ACT-FullAutomatedDecision",
                conditions=[
                    cond("C-021-CF1-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-021-CF1-2", "deployment_context", "EU_Market", "EU market deployment"),
                ],
                exceptions=[],
                evidence=[],
                notes=(
                    "Conflict-forming obligation: NIST AI RMF governance permits automated "
                    "decision pathways when documented controls are in place. Creates "
                    "cross-clause conflicts with ACT-RequireHumanOverride obligations."
                ),
            ),
            obl(
                "OBL-021-CF2", "CL-021", Actor.PROVIDER,
                "ACT-RetainDataMaximal",
                conditions=[
                    cond("C-021-CF2-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-021-CF2-2", "deployment_context", "EU_Market", "EU market deployment"),
                    cond("C-021-CF2-3", "processesSpecialCategory", True,
                         "Processes special-category data"),
                ],
                exceptions=[],
                evidence=[ev("E-ControlRegistry")],
                notes=(
                    "Conflict-forming obligation: NIST AI RMF governance requires retaining "
                    "comprehensive data for accountability analysis when special-category data "
                    "is involved. Creates cross-clause conflicts with ACT-MinimiseDataRetention "
                    "and ACT-ConductDPIA obligations."
                ),
            ),
            obl(
                "OBL-021-CF3", "CL-021", Actor.PROVIDER,
                "ACT-DiscloseToPublic",
                conditions=[
                    cond("C-021-CF3-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-021-CF3-2", "deployment_context", "EU_Market", "EU market deployment"),
                    cond("C-021-CF3-3", "hasSystemicRisk", True,
                         "System poses systemic risk"),
                ],
                exceptions=[],
                evidence=[ev("E-NISTMapping")],
                notes=(
                    "Conflict-forming obligation: NIST AI RMF accountability requires public "
                    "disclosure for systemic-risk systems. Creates cross-clause conflicts with "
                    "ACT-MaintainConfidentiality obligations."
                ),
            ),
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-022",
        text=(
            "Synthetic clause: Providers of high-risk AI systems that are deployed must "
            "align their AI management systems with the requirements of ISO/IEC 42001 "
            "and document the alignment."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Cross-instrument provisions",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-022-1", "CL-022", Actor.PROVIDER,
                "ACT-AlignWithISO42001",
                conditions=[
                    cond("C-022-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-022-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[ev("E-ISO42001Certificate"), ev("E-AIManagementSystem")],
            ),
            obl(
                "OBL-022-CF1", "CL-022", Actor.PROVIDER,
                "ACT-FullAutomatedDecision",
                conditions=[
                    cond("C-022-CF1-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-022-CF1-2", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[],
                evidence=[],
                notes=(
                    "Conflict-forming obligation: ISO 42001 management system controls may "
                    "permit automated decision channels when management system evidence is "
                    "documented. Creates cross-clause conflicts with ACT-RequireHumanOverride."
                ),
            ),
            obl(
                "OBL-022-CF2", "CL-022", Actor.PROVIDER,
                "ACT-RetainDataMaximal",
                conditions=[
                    cond("C-022-CF2-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-022-CF2-2", "isDeployed", True, "System is deployed"),
                    cond("C-022-CF2-3", "processesSpecialCategory", True,
                         "Processes special-category data"),
                    cond("C-022-CF2-4", "hasSystemicRisk", True, "System poses systemic risk"),
                ],
                exceptions=[],
                evidence=[ev("E-AIManagementSystem")],
                notes=(
                    "Conflict-forming obligation: ISO 42001 AI management system requires "
                    "comprehensive data retention for systemic-risk systems processing special "
                    "data. Creates cross-clause conflicts with ACT-MinimiseDataRetention and "
                    "ACT-ConductDPIA obligations."
                ),
            ),
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-023",
        text=(
            "Synthetic clause [AMBIGUOUS — AI Act + GDPR interaction]: High-risk AI system "
            "providers deployed in the EU market that process special-category data must "
            "comply with obligations arising from both AI Act and GDPR requirements. "
            "The interaction between the two instruments is ambiguous in certain scenarios."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Cross-instrument provisions",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: AI Act + GDPR interaction is not fully specified. "
            "Canonical tie-breaking: activate when all three conditions satisfied. "
            "LEXON errors: vocabulary mismatch on dual-compliance evidence specification."
        ),
        obligations=[
            obl(
                "OBL-023-1", "CL-023", Actor.PROVIDER,
                "ACT-ComplyWithDualRegulation",
                conditions=[
                    cond("C-023-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-023-2", "processesSpecialCategory", True, "Processes special data"),
                    cond("C-023-3", "deployment_context", "EU_Market", "EU market deployment"),
                ],
                exceptions=[],
                evidence=[ev("E-DualComplianceRecord"), ev("E-PrivacyImpactAssessment")],
                ambiguous=True,
                notes="Vocabulary mismatch: dual-compliance evidence types ambiguous",
            ),
            obl(
                "OBL-023-CF1", "CL-023", Actor.PROVIDER,
                "ACT-FullAutomatedDecision",
                conditions=[
                    cond("C-023-CF1-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-023-CF1-2", "processesSpecialCategory", True,
                         "Processes special-category data"),
                    cond("C-023-CF1-3", "deployment_context", "EU_Market",
                         "EU market deployment"),
                ],
                exceptions=[],
                evidence=[],
                notes=(
                    "Conflict-forming obligation (in ambiguous clause): AI Act + GDPR dual "
                    "compliance may permit automated processing when adequate safeguards are "
                    "documented under both instruments. Creates cross-clause conflicts with "
                    "ACT-RequireHumanOverride obligations."
                ),
            ),
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-024",
        text=(
            "Synthetic clause: Providers of high-risk AI systems deployed in the EU market "
            "must register the system with the relevant national AI authority, unless the "
            "system qualifies for a research exemption."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Cross-instrument provisions",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=False,
        obligations=[
            obl(
                "OBL-024-1", "CL-024", Actor.PROVIDER,
                "ACT-NotifyNationalAuthority",
                conditions=[
                    cond("C-024-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-024-2", "deployment_context", "EU_Market", "EU market deployment"),
                    cond("C-024-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-024-1", "hasResearchExemption", True, "Research exemption")],
                evidence=[ev("E-NationalAuthorityContact"), ev("E-RegistrationRecord")],
            ),
            obl(
                "OBL-024-CF1", "CL-024", Actor.PROVIDER,
                "ACT-MaintainConfidentiality",
                conditions=[
                    cond("C-024-CF1-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-024-CF1-2", "deployment_context", "EU_Market",
                         "EU market deployment"),
                    cond("C-024-CF1-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-024-CF1-1", "hasResearchExemption", True,
                                 "Research exemption")],
                evidence=[ev("E-RegistrationRecord")],
                notes=(
                    "Conflict-forming obligation: EU-registered providers may claim "
                    "confidentiality of proprietary system details included in registration. "
                    "Creates cross-clause conflicts with ACT-DiscloseToPublic obligations."
                ),
            ),
            obl(
                "OBL-024-CF2", "CL-024", Actor.PROVIDER,
                "ACT-RequireHumanOverride",
                conditions=[
                    cond("C-024-CF2-1", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-024-CF2-2", "deployment_context", "EU_Market",
                         "EU market deployment"),
                    cond("C-024-CF2-3", "isDeployed", True, "System is deployed"),
                ],
                exceptions=[exc("X-024-CF2-1", "hasResearchExemption", True,
                                 "Research exemption")],
                evidence=[ev("E-OverrideProcedure")],
                notes=(
                    "Conflict-forming obligation: EU national authority registration includes "
                    "attestation that human override is required for all automated decisions "
                    "affecting registered activities. Creates cross-clause conflicts with "
                    "ACT-FullAutomatedDecision obligations."
                ),
            ),
        ],
    ))

    clauses.append(RegulatoryClause(
        clause_id="CL-025",
        text=(
            "Synthetic clause [AMBIGUOUS — equivalence]: Importers of high-risk AI systems "
            "from non-EU jurisdictions and deploying in the EU market must assess whether "
            "the system meets standards equivalent to EU requirements. The standard of "
            "equivalence is not defined for all third-country regulatory frameworks."
        ),
        source_instrument=SourceInstrument.SYNTHETIC,
        thematic_group="Cross-instrument provisions",
        scope_risk_levels=[RiskLevel.HIGH_RISK],
        scope_domains=[Domain.GENERAL],
        ambiguity_flag=True,
        notes=(
            "AMBIGUITY: Equivalence standard undefined for many third-country frameworks. "
            "Canonical tie-breaking: activate when actor=Importer, HighRisk, EU_Market. "
            "LEXON errors: actor-attribution errors on Importer profiles with Mixed deployment."
        ),
        obligations=[
            obl(
                "OBL-025-1", "CL-025", Actor.IMPORTER,
                "ACT-AssessEquivalentCompliance",
                conditions=[
                    cond("C-025-1", "actor", "Importer", "Role is importer"),
                    cond("C-025-2", "risk_level", "HighRisk", "System is high-risk"),
                    cond("C-025-3", "deployment_context", "EU_Market", "EU market deployment"),
                ],
                exceptions=[],
                evidence=[ev("E-EquivalenceAssessment")],
                ambiguous=True,
                notes="Actor-attribution ambiguity: Importer role not always specified",
            )
        ],
    ))

    assert len(clauses) == 25, f"Expected 25 clauses, got {len(clauses)}"
    return clauses


# ---------------------------------------------------------------------------
# System profile definitions — 30 synthetic profiles
# ---------------------------------------------------------------------------


def _build_profiles(rng: random.Random) -> list[SystemProfile]:
    """Return the complete list of 30 synthetic AI system profiles."""

    profiles: list[SystemProfile] = []

    # Group 1: Easy — MinimalRisk, General, Provider/User (SYS-001–SYS-006)
    group1_defs = [
        ("SYS-001", [Capability.NLP], Domain.GENERAL, RiskLevel.MINIMAL_RISK, Actor.PROVIDER,
         DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-UserNotificationPolicy", "E-DeploymentRecord", "E-CapabilityDisclosure"]),
        ("SYS-002", [Capability.RECOMMENDATION], Domain.GENERAL, RiskLevel.MINIMAL_RISK, Actor.USER,
         DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": False, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": True, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard"]),
        ("SYS-003", [Capability.NLP, Capability.GENERATIVE_AI], Domain.GENERAL,
         RiskLevel.MINIMAL_RISK, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-UserNotificationPolicy", "E-DeploymentRecord", "E-CapabilityDisclosure",
          "E-ContentPolicy"]),
        ("SYS-004", [Capability.CLASSIFICATION], Domain.GENERAL, RiskLevel.MINIMAL_RISK,
         Actor.PROVIDER, DeploymentContext.NON_EU,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard", "E-DeploymentRecord"]),
        ("SYS-005", [Capability.NLP], Domain.GENERAL, RiskLevel.MINIMAL_RISK, Actor.PROVIDER,
         DeploymentContext.RESEARCH_EXEMPTION,
         {"affectsNaturalPerson": False, "isDeployed": True, "hasResearchExemption": True,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-ResearchRegistration"]),
        ("SYS-006", [Capability.GENERATIVE_AI], Domain.GENERAL, RiskLevel.LIMITED_RISK,
         Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-CapabilityDisclosure", "E-ContentPolicy", "E-UserNotificationPolicy"]),
    ]
    for sid, caps, dom, risk, actor, depl, props, ev_held in group1_defs:
        profiles.append(SystemProfile(
            system_id=sid, capabilities=caps, domain=dom, risk_level=risk,
            actor=actor, deployment_context=depl, properties=props,
            evidence_held=ev_held, profile_complete=True,
            difficulty=DifficultyLevel.EASY, group_label="Group1-MinimalRisk",
        ))

    # Group 2: Medium — HighRisk, Biometric/Healthcare, Provider (SYS-007–SYS-012)
    group2_defs = [
        ("SYS-007", [Capability.BIOMETRIC], Domain.HEALTHCARE, RiskLevel.HIGH_RISK, Actor.PROVIDER,
         DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": True, "logsUnderControl": True},
         ["E-TechnicalDocumentation", "E-RiskAssessment", "E-ConformityAssessment",
          "E-CertificationDocument", "E-RiskManagementPlan", "E-MonitoringPlan",
          "E-PostMarketReport", "E-DataMinimizationPolicy", "E-PrivacyImpactAssessment",
          "E-DataProcessingAgreement", "E-AuditReport", "E-IncidentLog",
          "E-NationalAuthorityContact", "E-DeployerInstructions", "E-SystemCard"]),
        ("SYS-008", [Capability.BIOMETRIC, Capability.DECISION_SUPPORT], Domain.HEALTHCARE,
         RiskLevel.HIGH_RISK, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": True, "logsUnderControl": True},
         ["E-TechnicalDocumentation", "E-RiskAssessment", "E-ConformityAssessment",
          "E-RiskManagementPlan", "E-PrivacyImpactAssessment", "E-HumanOverrideDoc"]),
        ("SYS-009", [Capability.DECISION_SUPPORT], Domain.HEALTHCARE, RiskLevel.HIGH_RISK,
         Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": True},
         ["E-TechnicalDocumentation", "E-RiskAssessment", "E-RiskManagementPlan",
          "E-MonitoringPlan", "E-HumanOverrideDoc", "E-OverrideProcedure",
          "E-HITLProcedureDoc", "E-OversightLog", "E-DeployerInstructions", "E-SystemCard"]),
        ("SYS-010", [Capability.BIOMETRIC], Domain.BIOMETRIC, RiskLevel.HIGH_RISK, Actor.PROVIDER,
         DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": True, "logsUnderControl": False},
         ["E-ConformityAssessment", "E-DataMinimizationPolicy", "E-PrivacyImpactAssessment"]),
        ("SYS-011", [Capability.CLASSIFICATION, Capability.BIOMETRIC], Domain.HEALTHCARE,
         RiskLevel.HIGH_RISK, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": True, "logsUnderControl": True},
         ["E-TechnicalDocumentation", "E-RiskManagementPlan", "E-ConformityAssessment",
          "E-AuditReport", "E-PrivacyImpactAssessment"]),
        ("SYS-012", [Capability.NLP, Capability.DECISION_SUPPORT], Domain.HEALTHCARE,
         RiskLevel.HIGH_RISK, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": True},
         ["E-TechnicalDocumentation", "E-RiskAssessment", "E-UserNotificationPolicy",
          "E-DeploymentRecord", "E-RiskManagementPlan"]),
    ]
    for sid, caps, dom, risk, actor, depl, props, ev_held in group2_defs:
        profiles.append(SystemProfile(
            system_id=sid, capabilities=caps, domain=dom, risk_level=risk,
            actor=actor, deployment_context=depl, properties=props,
            evidence_held=ev_held, profile_complete=True,
            difficulty=DifficultyLevel.MEDIUM, group_label="Group2-HighRisk-Healthcare",
        ))

    # Group 3: Easy-Medium — LimitedRisk, General/Education (SYS-013–SYS-018)
    group3_defs = [
        ("SYS-013", [Capability.NLP], Domain.EDUCATION, RiskLevel.LIMITED_RISK, Actor.PROVIDER,
         DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-UserNotificationPolicy", "E-DeploymentRecord", "E-SystemCard"]),
        ("SYS-014", [Capability.RECOMMENDATION], Domain.EDUCATION, RiskLevel.LIMITED_RISK,
         Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard", "E-DeploymentRecord"]),
        ("SYS-015", [Capability.GENERATIVE_AI, Capability.NLP], Domain.GENERAL,
         RiskLevel.LIMITED_RISK, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-CapabilityDisclosure", "E-ContentPolicy", "E-UserNotificationPolicy",
          "E-DeploymentRecord"]),
        ("SYS-016", [Capability.CLASSIFICATION], Domain.GENERAL, RiskLevel.LIMITED_RISK,
         Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": False, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard"]),
        ("SYS-017", [Capability.COMPUTER_VISION], Domain.EDUCATION, RiskLevel.LIMITED_RISK,
         Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard", "E-DeploymentRecord"]),
        ("SYS-018", [Capability.DECISION_SUPPORT], Domain.GENERAL, RiskLevel.LIMITED_RISK,
         Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard", "E-DeploymentRecord", "E-HumanReviewPolicy"]),
    ]
    for sid, caps, dom, risk, actor, depl, props, ev_held in group3_defs:
        profiles.append(SystemProfile(
            system_id=sid, capabilities=caps, domain=dom, risk_level=risk,
            actor=actor, deployment_context=depl, properties=props,
            evidence_held=ev_held, profile_complete=True,
            difficulty=DifficultyLevel.EASY, group_label="Group3-LimitedRisk",
        ))

    # Group 4: Hard — HighRisk, Mixed domains, Deployer/Importer (SYS-019–SYS-024)
    group4_defs = [
        ("SYS-019", [Capability.DECISION_SUPPORT, Capability.CLASSIFICATION], Domain.EMPLOYMENT,
         RiskLevel.HIGH_RISK, Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": False, "logsUnderControl": True},
         ["E-ImplementationRecord", "E-HumanReviewRecord", "E-HumanReviewPolicy"]),
        ("SYS-020", [Capability.BIOMETRIC, Capability.CCTV], Domain.PUBLIC_SERVICES,
         RiskLevel.HIGH_RISK, Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": True, "logsUnderControl": True},
         ["E-DataMinimizationPolicy", "E-PrivacyImpactAssessment", "E-HumanReviewRecord"]),
        ("SYS-021", [Capability.DECISION_SUPPORT], Domain.FINANCIAL, RiskLevel.HIGH_RISK,
         Actor.IMPORTER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-EquivalenceAssessment", "E-TechnicalDocumentation"]),
        ("SYS-022", [Capability.NLP, Capability.GENERATIVE_AI], Domain.PUBLIC_SERVICES,
         RiskLevel.HIGH_RISK, Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": False, "logsUnderControl": True},
         ["E-UserNotificationPolicy", "E-ContentPolicy", "E-IncidentLog",
          "E-NationalAuthorityContact", "E-RegistrationRecord"]),
        ("SYS-023", [Capability.BIOMETRIC, Capability.DECISION_SUPPORT], Domain.CRITICAL_INFRA,
         RiskLevel.HIGH_RISK, Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": True,
          "processesSpecialCategory": True, "logsUnderControl": True},
         ["E-ConformityAssessment", "E-PrivacyImpactAssessment", "E-AuditReport",
          "E-HumanReviewRecord"]),
        ("SYS-024", [Capability.CLASSIFICATION, Capability.DECISION_SUPPORT], Domain.EMPLOYMENT,
         RiskLevel.HIGH_RISK, Actor.IMPORTER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-EquivalenceAssessment"]),
    ]
    for sid, caps, dom, risk, actor, depl, props, ev_held in group4_defs:
        profiles.append(SystemProfile(
            system_id=sid, capabilities=caps, domain=dom, risk_level=risk,
            actor=actor, deployment_context=depl, properties=props,
            evidence_held=ev_held, profile_complete=True,
            difficulty=DifficultyLevel.HARD, group_label="Group4-HighRisk-Mixed",
        ))

    # Group 5: Ambiguous — Underspecified, Mixed roles (SYS-025–SYS-030)
    group5_defs = [
        ("SYS-025", [Capability.DECISION_SUPPORT], Domain.MIXED, RiskLevel.UNDERSPECIFIED,
         Actor.MIXED, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard"]),
        ("SYS-026", [Capability.NLP, Capability.CLASSIFICATION], Domain.MIXED,
         RiskLevel.UNDERSPECIFIED, Actor.PROVIDER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-UserNotificationPolicy", "E-SystemCard"]),
        ("SYS-027", [Capability.GENERATIVE_AI], Domain.GENERAL, RiskLevel.UNDERSPECIFIED,
         Actor.PROVIDER, DeploymentContext.NON_EU,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-ContentPolicy"]),
        ("SYS-028", [Capability.BIOMETRIC], Domain.MIXED, RiskLevel.UNDERSPECIFIED,
         Actor.MIXED, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": False, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": True, "logsUnderControl": False},
         ["E-PrivacyImpactAssessment"]),
        ("SYS-029", [Capability.DECISION_SUPPORT, Capability.NLP], Domain.MIXED,
         RiskLevel.UNDERSPECIFIED, Actor.DEPLOYER, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": True, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         ["E-SystemCard", "E-UserNotificationPolicy"]),
        ("SYS-030", [Capability.CLASSIFICATION], Domain.MIXED, RiskLevel.UNDERSPECIFIED,
         Actor.MIXED, DeploymentContext.EU_MARKET,
         {"affectsNaturalPerson": False, "isDeployed": True, "hasResearchExemption": False,
          "isExclusiveSelfUse": False, "hasSystemicRisk": False,
          "processesSpecialCategory": False, "logsUnderControl": False},
         []),
    ]
    for sid, caps, dom, risk, actor, depl, props, ev_held in group5_defs:
        profiles.append(SystemProfile(
            system_id=sid, capabilities=caps, domain=dom, risk_level=risk,
            actor=actor, deployment_context=depl, properties=props,
            evidence_held=ev_held, profile_complete=True,
            difficulty=DifficultyLevel.HARD, group_label="Group5-Underspecified",
        ))

    assert len(profiles) == 30, f"Expected 30 profiles, got {len(profiles)}"
    return profiles


# ---------------------------------------------------------------------------
# Benchmark instance construction
# ---------------------------------------------------------------------------


def build_benchmark_instances(
    clauses: list[RegulatoryClause],
    profiles: list[SystemProfile],
    rng: random.Random,
) -> list[BenchmarkInstance]:
    """
    Generate all 750 clause–profile pairs and assign train/dev/test splits.

    Split is seeded with RANDOM_SEED for determinism (60/20/20).
    """
    from lexon.benchmark.split import assign_splits

    instances: list[BenchmarkInstance] = []
    for clause in sorted(clauses, key=lambda c: c.clause_id):
        for profile in sorted(profiles, key=lambda p: p.system_id):
            iid = f"BENCH-{clause.clause_id}-{profile.system_id}"
            instances.append(
                BenchmarkInstance(
                    instance_id=iid,
                    clause_id=clause.clause_id,
                    system_id=profile.system_id,
                    split="train",  # placeholder, updated below
                    difficulty=profile.difficulty,
                    ambiguous=clause.ambiguity_flag,
                )
            )

    instances = assign_splits(instances, rng)
    return instances


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(seed: int = RANDOM_SEED) -> tuple[
    list[RegulatoryClause], list[SystemProfile], list[BenchmarkInstance]
]:
    """
    Generate the complete LEXON-Bench benchmark deterministically.

    Returns (clauses, profiles, instances).
    All generation is seeded with `seed` (default: RANDOM_SEED = 42).
    """
    rng = random.Random(seed)
    clauses = _build_clauses()
    profiles = _build_profiles(rng)
    instances = build_benchmark_instances(clauses, profiles, rng)
    return clauses, profiles, instances
