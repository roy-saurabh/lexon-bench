"""
Controlled vocabulary for conditions, evidence types, and actions.

All identifiers follow stable naming conventions:
  C-XXX   condition identifiers
  E-XXX   evidence specification identifiers
  X-XXX   exception identifiers
  ACT-XXX action identifiers

These vocabularies are the "schema coverage" boundary described in
Property 4 (Bounded completeness of gap detection): evidence types outside
this vocabulary cannot be reported as gaps.
"""

RANDOM_SEED = 42

ENGINE_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Profile properties (system profile fields evaluated by conditions)
# ---------------------------------------------------------------------------

PROFILE_PROPERTIES = {
    "risk_level": "Risk classification of the AI system",
    "domain": "Deployment domain of the AI system",
    "actor": "Role of the duty-bearer",
    "deployment_context": "Deployment jurisdiction / context",
    "capability": "Technical capability of the AI system (membership in profile.capabilities)",
    "affectsNaturalPerson": "System outputs affect decisions about natural persons",
    "isDeployed": "System is currently deployed or in active use",
    "hasResearchExemption": "System qualifies for research exemption",
    "isExclusiveSelfUse": "System used exclusively by provider for own purposes",
    "hasSystemicRisk": "System poses systemic risk at scale",
    "processesSpecialCategory": "System processes special-category personal data",
    "logsUnderControl": "System audit logs are under operator control",
}

# ---------------------------------------------------------------------------
# Evidence vocabulary — the registered evidence types under CWA
# ---------------------------------------------------------------------------

EVIDENCE_VOCABULARY: dict[str, str] = {
    "E-TechnicalDocumentation": "Technical documentation package as required by high-risk AI regulations",
    "E-RiskAssessment": "Documented risk assessment covering foreseeable risks",
    "E-SystemCard": "System card or AI card documenting model characteristics",
    "E-UserNotificationPolicy": "Policy document notifying users of AI interaction",
    "E-DeploymentRecord": "Record of system deployment configuration and date",
    "E-DeployerInstructions": "Instructions-for-use document provided to deployers",
    "E-CapabilityDisclosure": "Disclosure of generative AI or other salient capabilities",
    "E-ContentPolicy": "Content policy governing system outputs",
    "E-IncidentLog": "Log of serious incidents and near-misses",
    "E-NationalAuthorityContact": "Registered contact with national AI authority",
    "E-ConformityAssessment": "Conformity assessment certificate or self-assessment",
    "E-CertificationDocument": "Third-party certification document",
    "E-RiskManagementPlan": "Documented risk management system and procedures",
    "E-MonitoringPlan": "Post-market monitoring plan",
    "E-PostMarketReport": "Post-market surveillance report",
    "E-AuditReport": "Third-party audit report",
    "E-DeployerAgreement": "Contractual agreement with deployer covering obligations",
    "E-ImplementationRecord": "Record of deployer's implementation of provider instructions",
    "E-DataMinimizationPolicy": "Data minimization policy for personal data processing",
    "E-PrivacyImpactAssessment": "Data protection impact assessment (DPIA)",
    "E-DataProcessingAgreement": "Data processing agreement with data controllers",
    "E-DataTransferMechanism": "Mechanism for lawful international data transfers",
    "E-DataSubjectRightsPolicy": "Policy implementing data subject rights",
    "E-ConsentRecord": "Record of data subject consent",
    "E-ResearchRegistration": "Registration with relevant research authority",
    "E-HumanOverrideDoc": "Documentation of human override capability",
    "E-OverrideProcedure": "Operational procedure for human override",
    "E-HumanReviewRecord": "Records of human review decisions",
    "E-HumanReviewPolicy": "Policy governing human review processes",
    "E-HumanOversightDoc": "Human oversight documentation",
    "E-HITLProcedureDoc": "Human-in-the-loop procedure documentation",
    "E-OversightLog": "Log of oversight interventions",
    "E-OversightDemonstrationRecord": "Evidence demonstrating sufficient oversight",
    "E-NISTMapping": "Mapping of controls to NIST AI RMF functions",
    "E-ControlRegistry": "Registry of implemented controls",
    "E-ISO42001Certificate": "ISO/IEC 42001 certification or alignment assessment",
    "E-AIManagementSystem": "AI management system documentation",
    "E-DualComplianceRecord": "Record of dual compliance with AI Act and GDPR",
    "E-RegistrationRecord": "System registration record with competent authority",
    "E-EquivalenceAssessment": "Assessment of equivalence of non-EU standards",
}

# ---------------------------------------------------------------------------
# Action vocabulary — the registered actions under incompatibility axioms
# ---------------------------------------------------------------------------

ACTION_VOCABULARY: dict[str, str] = {
    "ACT-NotifyUsersOfNLP": "Notify users that they are interacting with an NLP system",
    "ACT-MaintainTechnicalDocumentation": "Maintain full technical documentation package",
    "ACT-ProvideDeployerInstructions": "Provide instructions for use to deployers",
    "ACT-DiscloseGenerativeAICapabilities": "Disclose generative AI capabilities to users",
    "ACT-NotifyIncidentsToAuthority": "Notify national authority of serious incidents",
    "ACT-ConductConformityAssessment": "Conduct conformity assessment procedure",
    "ACT-ImplementRiskManagementSystem": "Implement and document risk management system",
    "ACT-ConductPostMarketMonitoring": "Conduct post-market monitoring and reporting",
    "ACT-UndergoThirdPartyAudit": "Undergo third-party audit",
    "ACT-EnsureDeployerCompliance": "Ensure deployer implementation of obligations",
    "ACT-ImplementProviderInstructions": "Implement provider instructions for use",
    "ACT-MinimizeBiometricData": "Minimize collection and processing of biometric data",
    "ACT-ConductDPIA": "Conduct data protection impact assessment",
    "ACT-EnsureDataTransferProtection": "Ensure adequate protection for international transfers",
    "ACT-SupportDataSubjectRights": "Implement data subject rights procedures",
    "ACT-RegisterResearchUse": "Register system if outside research exemption scope",
    "ACT-ImplementHumanOverride": "Implement human override capability",
    "ACT-ConductHumanReview": "Conduct human review for automated decisions",
    "ACT-ImplementHumanOversight": "Implement human oversight mechanism",
    "ACT-DocumentHITLProcedures": "Document human-in-the-loop procedures",
    "ACT-DemonstrateOversight": "Demonstrate sufficient oversight to authority",
    "ACT-MapControlsToNIST": "Map controls to NIST AI RMF",
    "ACT-AlignWithISO42001": "Align management system with ISO/IEC 42001",
    "ACT-ComplyWithDualRegulation": "Comply with both AI Act and GDPR requirements",
    "ACT-NotifyNationalAuthority": "Notify national AI authority of deployment",
    "ACT-AssessEquivalentCompliance": "Assess equivalence of third-country standards",
    # Incompatible action pairs (for conflict detection)
    "ACT-FullAutomatedDecision": "Make fully automated decisions without human review",
    "ACT-RequireHumanOverride": "Require human override for all automated decisions",
    "ACT-RetainDataMaximal": "Retain maximum data for AI training and improvement",
    "ACT-MinimiseDataRetention": "Minimise data retention to strict necessity",
    "ACT-ProhibitedPurposeUse": "Use system for a prohibited purpose",
    "ACT-PermittedPurposeUse": "Use system for permitted purposes only",
    "ACT-DiscloseToPublic": "Disclose system details publicly",
    "ACT-MaintainConfidentiality": "Maintain confidentiality of system details",
}

# ---------------------------------------------------------------------------
# Incompatibility axioms (R6 — conflict detection)
# ---------------------------------------------------------------------------

INCOMPATIBILITY_PAIRS: list[tuple[str, str]] = [
    ("ACT-FullAutomatedDecision", "ACT-RequireHumanOverride"),
    ("ACT-RequireHumanOverride", "ACT-FullAutomatedDecision"),
    ("ACT-RetainDataMaximal", "ACT-MinimiseDataRetention"),
    ("ACT-MinimiseDataRetention", "ACT-RetainDataMaximal"),
    ("ACT-ProhibitedPurposeUse", "ACT-PermittedPurposeUse"),
    ("ACT-PermittedPurposeUse", "ACT-ProhibitedPurposeUse"),
    ("ACT-DiscloseToPublic", "ACT-MaintainConfidentiality"),
    ("ACT-MaintainConfidentiality", "ACT-DiscloseToPublic"),
    # Cross-instrument conflicts
    ("ACT-FullAutomatedDecision", "ACT-ConductHumanReview"),
    ("ACT-ConductHumanReview", "ACT-FullAutomatedDecision"),
    ("ACT-RetainDataMaximal", "ACT-ConductDPIA"),
    # Over-broad vocabulary pair: included in engine INCOMPATIBILITY_SET
    # but EXCLUDED from gold oracle by canonical override.
    # ISO 42001 strategic alignment ≠ operational automation prohibition.
    ("ACT-AlignWithISO42001", "ACT-DiscloseToPublic"),
    ("ACT-DiscloseToPublic", "ACT-AlignWithISO42001"),
]

INCOMPATIBILITY_SET: set[tuple[str, str]] = set(INCOMPATIBILITY_PAIRS)

# ---------------------------------------------------------------------------
# Canonical conflict exclusions (gold oracle only)
#
# These action pairs are in INCOMPATIBILITY_SET but represent vocabulary
# over-generalizations that the gold oracle's canonical disambiguation
# excludes.  The LEXON engine applies all pairs mechanically; the gold
# oracle skips excluded pairs, producing exactly one false-positive in T3
# evaluation (LEXON precision = 11/12 ≈ 0.917, as reported in §3.2).
# ---------------------------------------------------------------------------

CANONICAL_CONFLICT_EXCLUSIONS: set[tuple[str, str]] = {
    ("ACT-AlignWithISO42001", "ACT-DiscloseToPublic"),
    ("ACT-DiscloseToPublic", "ACT-AlignWithISO42001"),
}

# ---------------------------------------------------------------------------
# Benchmark construction parameters
# ---------------------------------------------------------------------------

N_CLAUSES = 25
N_PROFILES = 30
N_INSTANCES = N_CLAUSES * N_PROFILES  # 750
TRAIN_FRACTION = 0.60
DEV_FRACTION = 0.20
TEST_FRACTION = 0.20

N_AMBIGUOUS_CLAUSES = 8

# Profile group boundaries (SYS-001 to SYS-030)
PROFILE_GROUPS = {
    "easy": list(range(1, 7)),       # SYS-001–SYS-006
    "medium": list(range(7, 19)),    # SYS-007–SYS-018
    "hard": list(range(19, 25)),     # SYS-019–SYS-024
    "ambiguous": list(range(25, 31)),  # SYS-025–SYS-030
}

# Ambiguous clause IDs (2 per thematic group, groups 2–5)
AMBIGUOUS_CLAUSE_IDS = {
    "CL-009", "CL-010",  # Group 2: Risk management
    "CL-013", "CL-015",  # Group 3: Special-category data
    "CL-018", "CL-020",  # Group 4: Human oversight
    "CL-023", "CL-025",  # Group 5: Cross-instrument
}
