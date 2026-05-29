**LEXON: Executable Obligation Reasoning for AI Regulation with Typed Knowledge Graphs and Stratified Datalog**

Roy Saurabh

*AffectLog SAS, 75015 Paris, France · roy@affectlog.com*

*Submitted to Artificial Intelligence and Law (Springer)*

# **Abstract**

Regulatory frameworks for artificial intelligence increasingly impose conditional obligations that depend on actor role, system risk, deployment domain, capability, exceptions, and available evidence. This article presents LEXON, a symbolic AI-and-law framework for executable obligation reasoning over AI regulatory requirements. LEXON represents clauses, obligations, conditions, exceptions, evidence specifications, actors, and AI system profiles as typed information objects, and evaluates obligation activation, evidence-gap detection, direct conflict detection, and evidence-remediation candidates through stratified rule-based inference. The article formalises applicability using three-valued condition semantics, separates evidentiary completeness from substantive legal compliance, and provides derivation traces intended for human legal or compliance review. We evaluate the Python reference implementation on LEXON-Synth, a deterministic conformance suite of structured clauses and synthetic system profiles. LEXON achieves corpus-level F1 \= 1.000 for obligation activation and evidence-gap detection, confirming implementation conformance with the formal oracle, and detects 11 of 11 direct conflict pairs with one false positive (T3 F1 \= 0.957). We interpret these results as conformance evidence rather than legal-validity evidence. The article also provides an illustrative, non-authoritative mapping of selected EU AI Act provisions to LEXON tuple concepts and discusses the limits of executable obligation reasoning for AI governance.

**Keywords:** AI regulation; executable obligation reasoning; knowledge graphs; stratified Datalog; conformance suite; AI & Law; evidence-gap detection; conflict detection

# **1\. Introduction**

The global proliferation of regulation governing artificial intelligence (AI) systems marks a qualitative shift in the governance landscape. The European Union Artificial Intelligence Act \[1\], the U.S. National Institute of Standards and Technology AI Risk Management Framework \[2\], the international standard ISO/IEC 42001 \[3\], and a growing corpus of sector-specific instruments collectively impose many distinct, conditional obligations on AI system providers and deployers. These obligations are not uniformly applicable: they are contingent on system risk classification, deployment domain, actor role, and the presence or absence of specific technical artefacts. Yet the dominant practice for compliance assessment remains manual—compliance officers read regulatory text, maintain spreadsheets, and produce documentation whose completeness and correctness cannot be machine-verified.

This state of affairs has three consequences for the computational support of AI governance. First, coverage can be systematically incomplete: tracking every conditional obligation across multiple intersecting regulatory instruments is difficult without structured representation and inference. Second, conflicts between co-applicable obligations may remain difficult to detect without explicit cross-obligation reasoning. Third, remediation guidance can be ad hoc and difficult to reproduce across organisations. Existing instruments—checklists, model cards \[4\], datasheets \[5\], and documentation templates—address documentation, but not reasoning. They cannot activate obligations conditionally, detect evidentiary gaps against specified requirements, identify conflicts, or generate auditable remediation candidates.

LEXON belongs to the AI & Law tradition of executable legal knowledge representation and rule-based normative reasoning. Its aim is not to automate legal judgement but to make a restricted class of obligation-applicability and evidence-completeness inferences explicit, reproducible, and auditable. The contribution is therefore a formal representation and reasoning substrate for human-supervised AI regulatory review, rather than a compliance-certification system. We make this boundary explicit throughout the article: LEXON evaluates rule-derived applicability and evidentiary completeness, not the substantive legal validity of an AI system deployment.

The core technical problem is how to represent conditional, actor-specific, evidence-dependent regulatory obligations in a form that supports executable inference while preserving explicit boundaries between formal applicability, evidentiary completeness, and legal interpretation. We approach this not as an attempt to replace lawyers, auditors, or compliance officers, but as the construction of an auditable inference layer that can represent conditional obligations, determine whether formal activation conditions are satisfied under stated assumptions, identify missing evidence artefacts, and surface potential conflicts for human review.

We present LEXON (Legal EXecutable Obligation Network), a typed knowledge-graph and stratified-Datalog framework for executable regulatory obligation reasoning. LEXON consists of (i) a typed ontology that represents clauses, obligations, conditions, exceptions, evidence specifications, actors, and AI system profiles as graph entities; (ii) a stratified-Datalog rule layer with negation-as-failure under the closed-world assumption that compiles clause structure into executable inference rules; and (iii) a set of formally defined reasoning functions evaluated against a deterministic synthetic conformance suite.

## **1.1. Research Questions**

This article addresses four questions framed within legal informatics:

**RQ1.** How can AI regulatory obligations be represented as typed legal-information objects suitable for executable rule-based reasoning?

**RQ2.** What stratified rule semantics are sufficient to model obligation activation, exceptions, actor matching, evidence gaps, and direct conflicts under explicit closed-world assumptions?

**RQ3.** Does the reference implementation conform to the stated formal semantics on a deterministic synthetic conformance suite?

**RQ4.** What are the legal-informatics limits of executable obligation reasoning, particularly regarding evidentiary completeness, substantive compliance, ambiguity, and human review?

## **1.2. Contributions**

This article makes five contributions:

1. A typed legal-information schema for AI regulatory obligations, conditions, exceptions, evidence specifications, actors, and system profiles.

2. A stratified-Datalog-style rule layer for obligation activation, evidence-gap detection, direct conflict detection, and remediation-candidate generation.

3. A three-valued applicability semantics distinguishing true, false, and unknown condition states.

4. LEXON-Synth, a deterministic conformance suite for verifying implementation agreement with the formal oracle.

5. A reproducible software artifact including derivation traces, formal-property tests, baseline implementations, and an illustrative EU AI Act mapping. The EU AI Act mapping is illustrative, not legally adjudicated.

## **1.3. Article Organisation**

Section 2 presents the LEXON framework: the formal problem definition, typed knowledge-graph schema, stratified-Datalog rule layer, formal properties, and system architecture. Section 3 describes the LEXON-Synth conformance suite, its data splits, baselines, evaluation metrics, and reproducibility protocol. Section 4 provides an illustrative mapping of selected EU AI Act provisions to LEXON tuple concepts. Section 5 reports conformance-suite results for all four reasoning tasks together with ablation, ambiguity-routing, and construction-quality analyses. Section 6 discusses interpretation, prior work, design rationale, implications for AI & Law, the boundary against legal automation, and limitations. Section 7 concludes.

# **2\. The LEXON Framework**

## **2.1. Formal Problem Definition**

We define the regulatory obligation reasoning problem over a universe of types

U \= {Clause, Obligation, Condition, Exception, Evidence, System, Actor, RiskLevel, Domain, Action}.

All sets are finite and computable. We use the following core definitions.

**Definition 1 (Regulatory Clause).** A regulatory clause c ∈ C is a tuple ⟨id, text, source, scope⟩, where id is a unique identifier, text is the natural-language text, source ∈ {EU AI Act, NIST AI RMF, ISO/IEC 42001, …} is the issuing instrument, and scope ⊆ RiskLevel × Domain is the declared applicability scope.

**Definition 2 (Obligation).** An obligation o ∈ O is a tuple ⟨id, clause, actor, action, C\_o, X\_o, E\_o⟩, where actor ∈ {Provider, Deployer, Importer, User, Mixed}, action ∈ Action, C\_o is the conjunctive set of activation conditions, X\_o is the disjunctive set of exception triggers, and E\_o is the required evidence set.

**Definition 3 (AI System Profile).** A system profile S is a tuple ⟨id, capabilities, domain, risk, actor, deployment, evidence⟩, where capabilities ⊆ {GenerativeAI, Classification, Biometric, DecisionSupport, …}, risk ∈ {Unacceptable, HighRisk, LimitedRisk, MinimalRisk, Underspecified}, and evidence is the set of evidence items currently held by S.

**Definition 4 (Applicability with Three-Valued Condition Semantics).** Let sat(c, S) ∈ {true, false, unknown} denote the truth value of condition c in system profile S. For single-valued predicates such as risk, domain, actor, and deployment, a condition is true if the predicate-value pair matches the property asserted in S, false if the property is asserted and does not match, and unknown if the property is absent from S. For multi-valued predicates such as capability, a condition is true if the expected value is a member of the asserted value set, false if the set is asserted and does not contain the expected value, and unknown if the predicate is absent. Negated conditions invert the true/false outcome but preserve the unknown outcome.

The applicability relation A : O × S → {Applicable, NotApplicable, Uncertain} is defined as:

* A(o, S) \= Applicable iff actor(o) \= actor(S) (or either is Mixed), every c ∈ C\_o satisfies sat(c, S) \= true, and no x ∈ X\_o satisfies sat(x, S) \= true.

* A(o, S) \= NotApplicable iff actor(o) ≠ actor(S) (neither is Mixed), OR at least one c ∈ C\_o satisfies sat(c, S) \= false, OR at least one x ∈ X\_o satisfies sat(x, S) \= true.

* A(o, S) \= Uncertain iff actor matching holds, no condition is false, no exception fires, and at least one c ∈ C\_o satisfies sat(c, S) \= unknown.

**Definition 5 (Evidentiary Completeness Function).** The evidentiary completeness function EC : O × S × 2^Ev → {EvidenceComplete, EvidenceIncomplete, EvidenceNotRequired, EvidenceUncertain} is defined as: EC \= EvidenceComplete iff A(o, S) \= Applicable and E\_o ⊆ E\_held; EvidenceIncomplete iff A(o, S) \= Applicable and E\_o ⊄ E\_held; EvidenceNotRequired iff A(o, S) \= NotApplicable; EvidenceUncertain iff A(o, S) \= Uncertain.

*Evidentiary completeness is not equivalent to legal compliance: a system may possess required documentation while failing to implement the underlying control. The distinction is essential to the framing of this article and is discussed in Section 6\.*

**Definition 6 (Evidence Gap).** The evidence-gap function Gap : O × S × 2^Ev → 2^Ev is defined as Gap(o, S, E\_held) \= E\_o \\ E\_held when A(o, S) \= Applicable, and ∅ otherwise. The system-level gap is Gap(S) \= ⋃\_o Gap(o, S, E\_held).

**Definition 7 (Conflict).** A conflict pair (o₁, o₂, S) holds iff A(o₁, S) \= A(o₂, S) \= Applicable, actor(o₁) \= actor(o₂), o₁ ≠ o₂, and action(o₁) and action(o₂) are mutually incompatible under an explicit incompatibility relation incompatible(·, ·). To avoid double-counting, only canonical pairs with o₁ \< o₂ (by lexicographic obligation ID) are reported. The conflict set is K(S) \= {(o₁, o₂) : Conflict(o₁, o₂, S), o₁ \< o₂}.

**Definition 8 (Evidence-Remediation Candidate Set).** The evidence-remediation candidate function Rem : O × S × 2^Ev → 2^Ev returns evidence additions that, if obtained and validated, would change EC from EvidenceIncomplete to EvidenceComplete for one or more applicable obligations. Rem reasons about evidence completion only and does not model substantive operational controls.

## **2.2. Reasoning Tasks**

The framework supports four reasoning tasks summarised in Table 1\. Tasks T1–T3 are polynomial-time under the typed schema. Task T4 is approached via a greedy candidate-generation procedure; computing a minimum-cardinality remediation set across obligations is plausibly NP-hard by reduction from Weighted Set Cover, so LEXON returns candidate sets rather than minimum sets.

| ID | Task | Input | Output | Complexity |
| :---- | :---- | :---- | :---- | :---- |
| T1 | Obligation activation | (O, S) | {o : A(o, S) \= Applicable} | Polynomial |
| T2 | Evidence-gap detection | (O, S, E\_held) | Gap(S) | Polynomial |
| T3 | Conflict detection | (O, S) | K(S) | Polynomial |
| T4 | Evidence-remediation candidates | (O, S, E\_held) | Rem candidate set | Greedy |

*Table 1\. The four reasoning tasks supported by LEXON.*

## **2.3. Typed Knowledge-Graph Schema**

The LEXON terminology box (TBox) defines the entity types Clause, Obligation, Condition, Exception, EvidenceSpec, SystemProfile, Actor, Action, RiskLevel, and Domain. The relations are hasObligation(Clause, Obligation), hasCondition(Obligation, Condition), hasException(Obligation, Exception), requiresEvidence(Obligation, EvidenceSpec), hasCapability(SystemProfile, Capability), holdsEvidence(SystemProfile, EvidenceSpec), hasRiskLevel(SystemProfile, RiskLevel), hasDomain(SystemProfile, Domain), systemActor(SystemProfile, Actor), and obligActor(Obligation, Actor). All relations are typed; domain and range constraints are enforced at ABox population time.

Bridge rules connect the typed KG relations to the flat sysProp predicate used by condition satisfaction:

sysProp(S, riskLevel, R) :- hasRiskLevel(S, R).  
sysProp(S, domain, D)    :- hasDomain(S, D).  
sysProp(S, actor, A)     :- systemActor(S, A).  
sysProp(S, deployment, D):- hasDeployment(S, D).  
sysProp(S, capability, C):- hasCapability(S, C).  
These bridge rules make the typed KG relations queryable by the condition-satisfaction stratum without loss of domain-range typing.

## **2.4. Stratified-Datalog Rule Layer**

LEXON compiles obligations into stratified Datalog with negation-as-failure under a closed-world assumption (CWA). Stratification ensures that all negated predicates appear at a strictly lower stratum than their derivations, so the resulting program admits a unique perfect model \[22,23\]. The stratification levels are: Stratum 0 (conditionSatisfied), Stratum 1 (MissingCondition, exceptionFired), Stratum 2 (AllConditionsSatisfied), Stratum 3 (actorMatches, Applicable), Stratum 4 (EvidenceGap, Conflict, RemediationCandidate). We present the core rules below; the complete rule set is provided in Appendix A. The rules are stated as Datalog-style pseudocode in Soufflé-inspired syntax: they correspond directly to the Python reference implementation, but the three-valued condition semantics (Definition 4\) is handled in the implementation rather than expressed inside the two-valued Datalog rules themselves. Distinguishing false from unknown conditions in a pure two-valued program would require additional predicates (knownProperty, conditionFalse, conditionUnknown); these are noted in Appendix A as a future-work extension.

% R1 Condition satisfaction (Stratum 0\)  
conditionSatisfied(C, S) :-  
  condPred(C, P), condVal(C, V), sysProp(S, P, V).

% R1b Missing condition (Stratum 1\)  
MissingCondition(O, S) :-  
  hasCondition(O, C), NOT conditionSatisfied(C, S).

% R2 Universal condition satisfaction (Stratum 2\)  
AllConditionsSatisfied(O, S) :-  
  hasObligation(\_, O), NOT MissingCondition(O, S).

% R3 Exception firing (Stratum 1\)  
exceptionFired(O, S) :-  
  hasException(O, X), excCondition(X, C), conditionSatisfied(C, S).

% R4 Actor matching and activation (Stratum 3\)  
actorMatches(O, S) :- obligActor(O, A), systemActor(S, A).  
actorMatches(O, S) :- obligActor(O, "Mixed"), systemActor(S, \_).  
actorMatches(O, S) :- obligActor(O, \_), systemActor(S, "Mixed").  
Applicable(O, S) :-  
  actorMatches(O, S), AllConditionsSatisfied(O, S),  
  NOT exceptionFired(O, S).

% R5 Evidence-gap detection (Stratum 4\)  
EvidenceGap(O, S, E) :-  
  Applicable(O, S), requiresEvidence(O, E), NOT holdsEvidence(S, E).

% R6 Direct conflict detection with canonical ordering (Stratum 4\)  
Conflict(O1, O2, S) :-  
  Applicable(O1, S), Applicable(O2, S),  
  obligActor(O1, A), obligActor(O2, A),  
  obligAction(O1, Act1), obligAction(O2, Act2),  
  incompatibleActions(Act1, Act2), O1 \< O2.

% R7 Evidence-remediation candidates (Stratum 4\)  
RemediationCandidate(S, E) :- EvidenceGap(\_, S, E).  
R2 expresses activation as the absence of any missing condition rather than as an existential rule over single conditions. This corrects an existential pattern in which a single satisfied condition would suffice to derive applicability; under that incorrect formulation, an obligation conditioned on both risk \= HighRisk and isDeployed \= true would incorrectly activate for a MinimalRisk deployed system. Because Datalog with stratified negation under CWA is not monotone over arbitrary fact extensions, the soundness, monotonicity, and completeness claims require explicit qualifications, stated next.

## **2.5. Formal Properties**

**Property 1 (Soundness of activation).** Under the stratified-Datalog semantics with CWA, if LEXON derives Applicable(o, S), then A(o, S) \= Applicable in the sense of Definition 4\. By R4, derivation requires actorMatches(o, S), AllConditionsSatisfied(o, S), and NOT exceptionFired(o, S), corresponding respectively to the actor constraint, universal condition satisfaction, and the exception clause of Definition 4\. Under perfect-model semantics no facts are derived beyond those entailed by the rules and base facts; no spurious derivations occur. □

**Property 2 (Activation monotonicity over positive profile extensions).** Let the obligation graph, condition vocabulary, exception definitions, and rule vocabulary be fixed, and let S ⊆ S′ in the sense of fact entailment over system-profile facts only. If no fact in S′ \\ S satisfies an exception condition of o, then Applicable(o, S) implies Applicable(o, S′). The qualification is necessary: exception firing is non-monotone with respect to profile additions. □

**Property 3 (Anti-monotonicity of evidence gaps with respect to evidence additions).** For a fixed obligation set and applicability relation, adding held evidence can only reduce or preserve the set of detected evidence gaps. Formally, if E\_held ⊆ E\_held′, then Gap(S) under E\_held′ ⊆ Gap(S) under E\_held. □

**Property 4 (Bounded completeness of gap detection).** Under CWA on evidence holdings, LEXON computes Gap(o, S, E\_held) \= E\_o \\ E\_held for any applicable obligation o, provided E\_o is contained in the LEXON evidence vocabulary. Completeness is bounded by schema coverage: evidence types outside the vocabulary cannot be reported as gaps. This is a schema-coverage limitation, not a soundness limitation. □

**Property 5 (Conflict-detection soundness for direct conflicts).** Every conflict pair reported by R6 is a genuine conflict under Definition 7 for the direct action-incompatibility relation. Temporal and resource conflicts are out of scope of the current rule set.

## **2.6. System Architecture**

LEXON is realised as a five-stage information pipeline (Figure 1). Stage 1 (legal text decomposition) parses regulatory clauses into structured obligation tuples via an author-curated structured annotation protocol; all annotations in this study were produced by the author following a written rubric, with no external annotators or human subjects. Stage 2 (graph population) instantiates the typed knowledge graph (TBox \+ ABox) from extracted tuples and system-profile inputs. Stage 3 (rule compilation) translates the graph into stratified-Datalog rules via the bridge rules of Section 2.3. Stage 4 (inference) runs the Datalog engine to derive activation, evidence-gap, conflict, and remediation-candidate facts. Stage 5 (output generation) renders auditable derivation traces in human-readable and machine-readable form.

| Stage | Input | Output | Technology |
| :---- | :---- | :---- | :---- |
| 1\. Legal text decomposition | Regulatory clause text | Obligation tuples (JSON) | Author-curated annotation |
| 2\. Graph population | Tuples \+ system profile | KG ABox (typed triples) | Python / RDFLib |
| 3\. Rule compilation | TBox \+ ABox | Stratified-Datalog rules | Template compiler |
| 4\. Inference | Rules \+ facts | Applicable, Gap, Conflict, Candidate | Python reference implementation |
| 5\. Output generation | Derived facts | Trace report \+ remediation candidates | Template engine |

*Table 2\. Five-stage LEXON pipeline.*

*Figure 1\. End-to-end LEXON information pipeline. Regulatory clause text is decomposed by the author into structured obligation tuples, populated into a typed graph, translated into rule facts through bridge predicates, and evaluated by the stratified-Datalog inference layer to produce auditable outputs. \[Figure image: outputs/figures/pipeline.png in the companion repository; regenerated by the reproduction pipeline.\]*

# **3\. The LEXON-Synth Conformance Suite**

## **3.1. Conformance-Suite Construction**

LEXON-Synth is a deterministic conformance suite, not an independent legal-validity benchmark. Its purpose is to test whether the Python reference implementation satisfies the formal obligation-applicability and evidence-gap semantics defined in this article, and whether ablation baselines that omit components of the semantics diverge from the formal oracle in predictable ways. The suite does not measure agreement between the system and the intent of any real regulatory provision; that question is addressed by extending the suite to expert-validated real clauses (future work).

LEXON-Synth consists of (i) 25 annotated regulatory clauses spanning five thematic groups (transparency and information; risk management and conformity assessment; special-category data handling; human oversight and human-in-the-loop; and cross-instrument provisions), (ii) 30 synthetic AI system profiles stratified by risk level, domain, actor role, and evidence completeness, and (iii) gold labels for the four reasoning tasks. Each clause is decomposed into one or more obligation tuples with explicit conditions, exceptions, and evidence specifications drawn from a controlled vocabulary.

Gold labels for T1 and T2 are derived by applying the formal definitions of Section 2.1 directly to the structured obligation tuples. This is the defining property of a conformance suite rather than a weakness of a benchmark: because the gold labels and the system under test share the same formal representation, the suite can confirm that the implementation faithfully executes the specified semantics, but cannot independently validate that the semantics correctly captures the intent of the regulatory text. We treat this property proactively. The suite is designed to (a) verify implementation conformance, (b) localise, through ablation (Section 5.3), which components are responsible for conformance, and (c) be released in full for independent inspection. The boundary between conformance and legal validity is restated in Section 6.6.

Table 3 presents three worked examples from the test set, one for each possible activation outcome. The full set of instances, gold labels, and the annotation rubric is provided in the companion repository.

| Example | Clause | Profile | Key conditions | Activation | Evidence gaps | Explanation |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| E1 Applicable | CL-002 | SYS-007 | risk \= HighRisk; isDeployed \= true; actor \= Provider | Applicable | — | All conditions true; no exception fires; required CL-002 evidence already held. |
| E2 NotApplicable | CL-002 | SYS-013 | risk \= LimitedRisk (false against required HighRisk) | NotApplicable | — | Risk-level condition is false; EC \= EvidenceNotRequired. |
| E3 Uncertain | CL-010 | SYS-027 | actor \= Mixed; deployment\_context unknown | Uncertain | — | Deployment condition is unknown; routed to human review. |

*Table 3\. Three worked examples illustrating the Applicable, NotApplicable, and Uncertain activation outcomes. Full instance traces, including rule derivations and typed-graph fragments, are in outputs/reports/ in the companion repository.*

| Profile group | Risk level | Domain | Actor | Difficulty |
| :---- | :---- | :---- | :---- | :---- |
| SYS-001–SYS-006 | MinimalRisk | General | Provider/User | easy |
| SYS-007–SYS-012 | HighRisk | Biometric/Healthcare | Provider | medium |
| SYS-013–SYS-018 | LimitedRisk | General/Education | Provider/Deployer | easy–medium |
| SYS-019–SYS-024 | HighRisk | Mixed | Deployer/Importer | hard |
| SYS-025–SYS-030 | Underspecified | Mixed | Mixed | hard (ambiguous) |

*Table 4\. Summary of the 30-profile corpus, stratified by risk, domain, and actor.*

## **3.2. Train/Development/Test Splits**

The 25 clauses and 30 profiles yield 750 clause-profile pairs. Each pair is tagged with the tasks for which gold labels are defined. The pair set is partitioned into 60% training (450 instances; rule tuning and baseline calibration), 20% development (150 instances; hyperparameter selection), and 20% held-out test (150 instances; final evaluation). All splits use seed \= 42 and are versioned. Gold labels are released with the suite.

## **3.3. Baselines**

We compare LEXON against three baselines representing the space of widely used compliance-support approaches. We do not include an LLM-only baseline in the reported results because the LLM experiment was not executed under a fixed-prompt, fixed-model-version, fixed-temperature reproducible protocol; the discussion of LLM-based legal reasoning appears in Section 6.2.

| ID | Baseline | Description | Capability gap tested |
| :---- | :---- | :---- | :---- |
| B1 | Static checklist | Binary checklist per risk level; no condition evaluation; no exception handling; no conflict detection. | Value of conditional activation, gap detection, and cross-clause reasoning. |
| B2 | Ontology without inference | LEXON TBox populated; no Datalog rules fired; no activation, gap, or conflict derived. | Contribution of the rule layer. |
| B3 | Flat-rule engine without typed graph | Production rules over untyped facts; no schema constraints; no conflict detection. | Contribution of the typed graph and actor-scoped conflict rules. |

*Table 5\. Implemented baselines and what each isolates.*

## **3.4. Evaluation Metrics**

For T1 and T2 we report corpus-level (micro-averaged) precision, recall, and F1 against the deterministic gold labels on the held-out test split, together with corpus-level TP, FP, and FN counts. Corpus F1 aggregates TP, FP, and FN counts across all clause-profile pairs before computing P/R/F1, and is the appropriate point estimate when most instances contain zero gold-positive labels. As a separate quantity we also report the mean per-instance F1 with a non-parametric bootstrap 95% confidence interval (1000 iterations, seed \= 42); because most per-instance F1 values are zero, the per-instance mean and its CI are not comparable to corpus F1 and are reported only for completeness. For T3 we evaluate at the unique unordered obligation-pair level across all 30 profiles. We do not report McNemar tests: because the suite is synthetic and gold labels are generated from the same formal semantics implemented by LEXON, we treat LEXON-versus-baseline comparisons as ablation diagnostics rather than as inferential evidence of population-level superiority. Computing properly paired McNemar tables on real regulatory provisions is identified as future work.

## **3.5. Reproducibility Protocol**

The conformance-suite generation scripts, structured obligation tuples, system profiles, gold labels, rule specifications, baseline implementations, and evaluation scripts are provided in the companion repository. All reported tables are regenerated by a single reproduction command (make reproduce). All random seeds are fixed (seed \= 42); suite generation is deterministic; baseline implementations are version-pinned in pyproject.toml. The repository and Zenodo DOI are listed in the Data Availability Statement.

# **4\. Illustrative Mapping to EU AI Act Provisions**

To demonstrate contact between the formal representation and real legal material, Table 6 maps selected EU AI Act provisions to LEXON tuple concepts: the responsible actor, the obligation action, the activating condition, the principal evidence object, and a limitation that marks where legal interpretation remains necessary.

*The mapping is illustrative only. It is not an expert-adjudicated legal corpus, does not reproduce official legal text verbatim, and does not constitute legal advice.*

| Provision | Actor | Obligation action | Condition | Evidence object | Limitation |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Article 9 | Provider | Maintain risk-management system | High-risk AI system | Risk-management plan | Scope depends on system classification |
| Article 10 | Provider | Apply data-governance measures | High-risk AI system using data | Data-governance record | Evidence sufficiency is context-dependent |
| Article 11 | Provider | Maintain technical documentation | High-risk AI system | Technical documentation | Annex IV decomposition required |
| Article 13 | Provider | Provide transparency / instructions | High-risk AI system | Instructions for use | Interpretive details remain legal |
| Article 14 | Provider/Deployer | Enable human oversight | High-risk AI system | Human-oversight protocol | Role allocation may require legal interpretation |
| Article 15 | Provider | Ensure accuracy, robustness, cybersecurity | High-risk AI system | Robustness/evaluation report | Thresholds are domain-specific |
| Annex IV | Provider | Prepare technical documentation | High-risk AI system | Annex IV documentation | Sub-items require structured decomposition |

*Table 6\. Illustrative, non-authoritative mapping of selected EU AI Act provisions to LEXON tuple concepts. The structured mapping is released as data/illustrative/eu\_ai\_act\_mapping.csv (and .jsonl) with every row marked validation\_status \= “Illustrative mapping only”.*

# **5\. Conformance-Suite Results**

## **5.1. Conformance-Suite Results for Obligation Activation (T1) and Evidence-Gap Detection (T2)**

The LEXON-Synth conformance suite was used to verify that the Python reference implementation satisfies the formal obligation-applicability and evidence-gap semantics defined in the paper. The suite contains 25 structured clauses and 30 synthetic AI system profiles, yielding 750 clause-profile pairs, with a 150-instance held-out test split generated using seed \= 42\.

On the held-out split, LEXON achieved corpus-level precision \= 1.000, recall \= 1.000, and F1 \= 1.000 for obligation activation (T1), with 33 true positives, 0 false positives, and 0 false negatives. For evidence-gap detection (T2), LEXON also achieved corpus-level precision \= 1.000, recall \= 1.000, and F1 \= 1.000, with 30 true positives, 0 false positives, and 0 false negatives. These values are interpreted as implementation-conformance results: they verify agreement between the reference implementation and the formal conformance oracle, not external legal validity.

The static-checklist baseline reached T1 F1 \= 0.446 and T2 F1 \= 0.321. The ontology-only baseline reached T1 F1 \= 0.054 and T2 F1 \= 0.000. The flat-rule baseline without typed-graph constraints reached T1 F1 \= 0.660 and T2 F1 \= 0.533. These ablations indicate that the rule layer and typed-graph constraints are both necessary for full conformance on the synthetic suite.

Table 7 reports corpus-level precision, recall, and F1 on the held-out split, together with the bootstrap mean per-instance F1 and its 95% confidence interval as a separate column; the two quantities are computed differently and should not be combined. Table 8 reports the underlying confusion counts.

| System | T1 P | T1 R | Corpus T1 F1 | Mean inst. T1 F1 \[95% CI\] | T2 P | T2 R | Corpus T2 F1 | Mean inst. T2 F1 \[95% CI\] |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| LEXON (full) | 1.000 | 1.000 | 1.000 | 0.15 \[0.09, 0.21\] | 1.000 | 1.000 | 1.000 | 0.11 \[0.06, 0.16\] |
| B1 Static checklist | 0.293 | 0.939 | 0.446 | 0.14 \[0.08, 0.19\] | 0.196 | 0.900 | 0.321 | 0.10 \[0.05, 0.15\] |
| B2 Ontology (no rules) | 0.250 | 0.030 | 0.054 | 0.01 \[0.00, 0.02\] | 0.000 | 0.000 | 0.000 | 0.00 \[0.00, 0.00\] |
| B3 Flat rules (no graph) | 0.508 | 0.939 | 0.660 | 0.14 \[0.09, 0.19\] | 0.373 | 0.933 | 0.533 | 0.10 \[0.05, 0.15\] |

*Table 7\. Obligation activation (T1) and evidence-gap detection (T2) on the 150-instance held-out test split (seed \= 42). Corpus F1 values are micro-averaged and are the primary point estimates. The per-instance means and CIs are low and wide because most instances have no applicable obligations; the two quantities are not directly comparable.*

| System | T1 TP | T1 FP | T1 FN | T1 P | T1 R | T2 TP | T2 FP | T2 FN | T2 P | T2 R |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| LEXON (full) | 33 | 0 | 0 | 1.000 | 1.000 | 30 | 0 | 0 | 1.000 | 1.000 |
| B1 Static checklist | 31 | 75 | 2 | 0.293 | 0.939 | 27 | 111 | 3 | 0.196 | 0.900 |
| B2 Ontology (no rules) | 1 | 3 | 32 | 0.250 | 0.030 | 0 | 4 | 30 | 0.000 | 0.000 |
| B3 Flat rules (no graph) | 31 | 30 | 2 | 0.508 | 0.939 | 28 | 47 | 2 | 0.373 | 0.933 |

*Table 8\. Corpus-level confusion counts on the held-out test split. Counts are summed over all clause-profile pairs; precision and recall are computed from the summed counts.*

The F1 \= 1.000 result is expected and correct: the rule engine faithfully implements the formal definitions of Section 2.1, and the gold labels are derived from the same definitions applied to the same structured tuples. Achieving F1 \= 1.000 confirms semantic conformance between the implementation and the gold-label oracle—a necessary condition for a reproducible system, not a measure of external regulatory accuracy. The static checklist (B1) applies uniform risk-level thresholds without condition evaluation, systematically missing conditional obligations; its high recall paired with low precision reflects indiscriminate activation for HighRisk profiles. The ontology-only baseline (B2) can classify entity types but cannot fire rules. The flat-rule engine (B3) lacks typed domain-range constraints and produces false-positive activations on under-typed profiles. LEXON's combination of typed graph structure, three-valued condition semantics, actor matching, and stratified-Datalog inference is the configuration that achieves zero false positives and zero false negatives simultaneously.

## **5.2. Conflict Detection (T3)**

For direct conflict detection (T3), LEXON detected 11 of 11 canonical gold conflict pairs with one false positive, yielding precision \= 0.917, recall \= 1.000, and F1 \= 0.957. The single false positive arises from an over-broad entry in the incompatibility axioms (ACT-DiscloseToPublic ⊥ ACT-AlignWithISO42001), which the canonical gold oracle excludes as a vocabulary-generalisation artefact. The false positive is attributable to the curated incompatibility vocabulary rather than to a failure of the activation semantics, illustrating that conflict-detection quality depends on the curation of the incompatibility vocabulary; rule soundness alone does not guarantee legally meaningful conflict detection.

Because none of the implemented ablation baselines (B1–B3) includes cross-obligation conflict reasoning, each scores T3 P \= R \= F1 \= 0.000 by design. The T3 comparison should therefore be read as a functional validation of LEXON's conflict rule against the 11-pair gold set, not as evidence of superiority over mature compliance systems with cross-clause reasoning. A comparison against a SHACL-based validator or a typed production-rule engine is identified as future work.

## **5.3. Ablation: Graph \+ Rules vs. Rules Only vs. Checklist**

The comparison between the LEXON full system, the flat-rule engine (B3, typed-graph layer removed), and the static checklist (B1, both layers removed) isolates the contribution of each architectural component.

| System | T1 F1 | T1 ΔF1 | T2 F1 | T2 ΔF1 |
| :---- | :---- | :---- | :---- | :---- |
| B1 Static checklist | 0.446 | — | 0.321 | — |
| B3 Flat rules (+rule layer) | 0.660 | \+0.214 | 0.533 | \+0.212 |
| LEXON full (+typed graph, actor matching) | 1.000 | \+0.340 | 1.000 | \+0.467 |

*Table 9\. Ablation: T1 and T2 F1 gains from adding the rule layer (B1→B3) and the typed graph with actor matching (B3→LEXON). Both additions are necessary; neither alone achieves corpus-level conformance.*

Adding the rule layer (B1→B3) contributes \+0.214 to T1 and \+0.212 to T2. Adding the typed graph with actor-matching constraints (B3→LEXON) contributes an additional \+0.340 to T1 and \+0.467 to T2. Typed structure contributes more to T2 than to T1, consistent with the role of typed evidence specifications in disambiguating which evidence items correspond to which applicable obligations. Without domain-range constraints, B3 incorrectly classifies evidence gaps on under-typed profiles.

## **5.4. Ambiguity Routing**

Eight of the 25 clauses carry an explicit ambiguity flag assigned during suite construction, indicating that the clause text admits more than one plausible structured representation and that human review is recommended before treating the derived tuple as authoritative. Within the held-out split, instances associated with these clauses are routed to human-review status via the remediation-candidate mechanism (requires\_human\_review \= true). The flag and the routing mechanism were both established during construction; the result confirms that the mechanism is correctly wired to the flag, not that the system independently detects ambiguity from clause text. This is a functional check of the routing pathway. The routing behaviour is consistent with LEXON's intended role: the system surfaces ambiguous cases for qualified human review rather than deriving outcomes that depend on contested interpretations.

## **5.5. Conformance-Suite Construction Quality Audit**

During construction, the annotation protocol identified three categories of clause-representation challenges. These are not engine prediction errors—the engine achieves corpus-level F1 \= 1.000—but annotation decisions that required explicit resolution in the rubric. First, condition-vocabulary misalignment (3 instances) occurred where a controlled-vocabulary term was subtly inconsistent with the clause text; resolved by extending the vocabulary and re-annotating. Second, exception-scope mis-attribution (2 instances) occurred where a narrowing clause was initially annotated as a new obligation rather than a partial exception; resolved by clarifying the rubric distinction between narrowing exceptions and compound obligations. Third, actor-attribution challenges (2 instances) arose on dual-actor clauses requiring decomposition into separate Provider and Deployer obligations; resolved by requiring explicit actor decomposition. The resolution of all seven cases before finalising the gold labels is why the engine attains F1 \= 1.000: the construction process is itself part of the quality assurance.

# **6\. Discussion**

## **6.1. Interpretation of Results**

On this synthetic conformance suite, LEXON correctly implements the specified formal semantics: it achieves F1 \= 1.000 for obligation activation and evidence-gap detection, and detects all 11 gold conflict pairs with one false positive. The ablation indicates that each architectural component—the typed knowledge graph, the actor-matching constraints, and the stratified-Datalog rule layer—contributes to this conformance; removing any component degrades agreement with the oracle. The most informative single property for practical review is arguably not the absolute F1 score (bounded above by synthetic construction) but the presence of auditable derivation traces for every reported applicability or gap decision: each output records which rules fired, which conditions were satisfied, and which evidence items were absent. A critical limitation is that F1 \= 1.000 measures agreement between the engine and the synthetic gold labels, not agreement between the system and the intent of the regulatory text.

## **6.2. Relation to Prior Work**

A substantial body of work addresses extraction of structure from legal text \[6,7,8\]; these approaches produce structured outputs but do not define or execute formal compliance-reasoning functions. Legal-knowledge representation frameworks—LKIF \[9\], LegalRuleML \[10\], the ODRL policy language \[11\], and the Data Privacy Vocabulary \[12\]—provide ontological coverage of legal concepts and obligations. Defeasible deontic logic frameworks \[13\] handle contrary-to-duty obligations and exceptions with formally specified non-monotonic semantics. SHACL \[14\] supports constraint validation over RDF graphs, and Akoma Ntoso \[15\] standardises legislative document structure. Early work on executable legal reasoning includes the British Nationality Act formalisation \[24\], which showed that statutory logic programs could be executed and interrogated—a conceptual ancestor of the present approach. LEXON builds on this tradition and is most similar in spirit to LegalRuleML-style executable representations, but differs in three respects: the focus on AI-specific evidence specifications, the typed-graph schema for AI system profiles, and the joint evaluation of activation, gap, and conflict reasoning on a single conformance suite.

AI governance documentation—model cards \[4\], datasheets \[5\], system cards \[16\], and dataset nutrition labels \[17\]—provides transparency instruments but is not designed for executable inference; LEXON treats documentation fields as instances of typed evidence specifications. Large language models have been applied to legal question answering and statutory reasoning \[18,19,20\]; these achieve fluency on multiple-choice benchmarks but lack formal soundness guarantees, produce non-reproducible outputs under stochastic inference, and offer limited support for the audit trails expected of compliance documentation. A controlled LLM comparison, particularly for the clause-to-tuple decomposition step (Stage 1), is a defensible future direction. RegTech systems \[21\] address similar problems in financial and data-protection domains; LEXON shares the goal of executable compliance reasoning but is specialised to AI regulation and its evidence structure.

## **6.3. Why Typed Knowledge Graphs and Stratified Datalog?**

The choice of stratified Datalog reflects three practical considerations. First, Datalog evaluations terminate and admit unique perfect models under stratification \[22,23,25\], which is important for reproducibility and for generating audit trails. Second, the rule layer is human-readable and reviewable by domain experts, supporting the goal of an auditable inference layer. Third, typed-graph constraints prevent rules from firing on type-incoherent facts, substantially reducing false positives in evidence-gap detection, as shown by the ablation. The combination of these properties is difficult to obtain with LLM-based pipelines, which do not natively provide derivation traces or determinism.

## **6.4. Implications for AI & Law**

LEXON contributes to AI & Law by operationalising a restricted class of regulatory obligation reasoning as typed, executable, and inspectable inference. Unlike LLM-based legal reasoning systems, LEXON does not attempt to infer legal meaning from text end-to-end. Instead, it assumes an explicit structured representation and focuses on whether applicability, evidence-gap, and conflict conclusions follow from that representation under stated semantics. This design supports auditability and reproducibility while preserving the need for human legal interpretation. The framework is intended to augment human compliance reasoning by improving coverage of conditional obligations and by providing reproducible documentation of which obligations apply under which assumptions. Adopters should remain aware of three risks: automated support can create a false sense of assurance (hence the explicit separation of evidentiary completeness from compliance); the closed-world evidence model may penalise valid evidence in non-standard formats; and LEXON faithfully represents the regulations it is given, reporting disproportionate burdens as obligations rather than flagging them as inequitable.

## **6.5. Why This Is Not Legal Automation**

LEXON does not automate legal judgement. It automates only a bounded inference problem: given an encoded obligation tuple, system profile, evidence inventory, and incompatibility vocabulary, derive applicability, evidence gaps, and direct conflicts under explicit assumptions. The legally consequential steps—interpretation of source text, selection of evidence categories, assessment of evidence sufficiency, and judgement of substantive compliance—remain outside the system boundary and the responsibility of qualified human reviewers.

## **6.6. Limitations**

The following limitations are central to the interpretation of the contribution, not defensive caveats:

* No external legal-validity claim: the suite verifies implementation conformance, not regulatory correctness.

* Synthetic conformance suite only: all clauses and profiles are synthetic and deterministic.

* No expert-validated legal corpus: gold labels are derived from the formal definitions, not from independent legal adjudication.

* Illustrative EU AI Act mapping only: the mapping demonstrates contact with real provisions but is non-authoritative and not verbatim.

* Closed-world evidence assumptions: non-standard or unregistered evidence may be classified as absent.

* Conflict detection limited to direct action incompatibility: no temporal or resource conflict modelling.

* No temporal/resource conflict model: detecting these would require a clock model and a resource model respectively.

* Evidence completeness is not substantive compliance: a system may hold required documentation without implementing the underlying control.

* Legal interpretation remains a human responsibility: the framework supports review rather than supplanting it.

## **6.7. Implications for AI Governance**

LEXON is intended as a transparent inference layer for machine-assisted AI governance. Its outputs—obligation-activation traces, evidence-gap lists, conflict alerts, and remediation candidates—each carry the rule derivations that produced them, providing the audit trail expected in regulated environments. The framework augments, rather than replaces, the work of compliance officers, and its design deliberately routes contested or ambiguous cases to human review.

# **7\. Conclusion**

This article presented LEXON, a symbolic AI-and-law framework for executable obligation reasoning over AI regulatory requirements. The framework represents clauses, obligations, conditions, exceptions, evidence specifications, actors, and system profiles as typed information objects, and evaluates obligation activation, evidence-gap detection, direct conflict detection, and evidence-remediation candidates through stratified rule-based inference under three-valued applicability semantics. We evaluated the Python reference implementation on LEXON-Synth, a deterministic conformance suite of 25 clauses and 30 system profiles (750 clause-profile pairs, 150-instance held-out test set). LEXON achieves corpus-level F1 \= 1.000 for obligation activation and evidence-gap detection, confirming implementation conformance with the formal oracle; ablation shows that neither the rule layer alone (T1 F1 \= 0.660) nor the checklist baseline (T1 F1 \= 0.446) achieves this conformance. LEXON detects all 11 direct conflict pairs with one false positive (T3 F1 \= 0.957).

The primary contribution is not the automation of legal judgement but a reproducible, auditable inference substrate for human-supervised AI regulatory review, in which every applicability decision, evidence-gap finding, and conflict alert is accompanied by a derivation trace. We interpret the results as conformance evidence rather than legal-validity evidence, and we provide an illustrative mapping of selected EU AI Act provisions to show contact with real legal material under explicit non-authoritative assumptions.

Future work should extend the suite to expert-validated real regulatory provisions (EU AI Act Articles 9, 10, 11, 13, 14, 15, and Annex IV are natural starting points); conduct independent second annotation to assess inter-annotator agreement; compute properly paired McNemar tables on real provisions where independent classifiers diverge; compare LEXON against a stronger symbolic baseline such as a SHACL-based validator or a typed production-rule engine; enrich the remediation model beyond evidence completion; incorporate open-world evidence reasoning; evaluate the framework in practitioner workflows; and develop a clock model for temporal conflict detection.

# **Declarations**

**Funding.** This research received no external funding.

**Competing interests.** R.S. is the founder of AffectLog SAS, a company developing AI governance and compliance technologies. The research presented here is methodological and does not evaluate any AffectLog commercial product. The author declares that this interest did not influence the design, analysis, or reporting of the study.

**Ethics approval.** Not applicable. The study did not involve human or animal subjects; all conformance-suite data are synthetic.

**Author contributions.** R.S. conceived the framework, designed and implemented the software and conformance suite, conducted the formal analysis and evaluation, and wrote and revised the manuscript.

**Use of generative AI.** During preparation of this manuscript the author used a large language model assistant for language editing and drafting support on prose sections. All technical content—formal definitions, rule specifications, conformance-suite construction, baseline implementations, evaluation scripts, and analysis—was designed, implemented, and verified by the author, who takes full responsibility for the content. Generative AI was not used to generate gold labels, suite instances, or evaluation results.

**Data availability.** The source code, synthetic conformance suite, structured obligation tuples, AI system profiles, conformance oracle labels, baseline implementations, rule specifications, illustrative EU AI Act mapping, derivation-trace examples, and reproduction scripts are available in the LEXON-Bench repository at https://github.com/roy-saurabh/lexon-bench and archived on Zenodo. The artifact version associated with the Artificial Intelligence and Law submission is v1.1.0, with version-specific DOI \[INSERT DOI AFTER RELEASE\]. The earlier MDPI Information submission artifact is archived as v1.0.2 with DOI 10.5281/zenodo.20399201. The synthetic conformance suite contains no personal data. The EU AI Act mapping is illustrative and does not reproduce official legal text verbatim. Code is released under the MIT License; synthetic suite data are released under CC-BY-4.0.

# **Abbreviations**

| Abbreviation | Meaning |
| :---- | :---- |
| ABox | Assertion box (instance-level component of a knowledge graph) |
| AI | Artificial intelligence |
| CWA | Closed-world assumption |
| DPV | Data Privacy Vocabulary |
| F1 | Harmonic mean of precision and recall |
| FNR | False negative rate (1 − Recall) |
| KG | Knowledge graph |
| LKIF | Legal Knowledge Interchange Format |
| NIST | U.S. National Institute of Standards and Technology |
| ODRL | Open Digital Rights Language |
| RegTech | Regulatory technology |
| RMF | Risk Management Framework |
| SHACL | Shapes Constraint Language |
| TBox | Terminology box (schema-level component of a knowledge graph) |

# **Appendix A. Complete LEXON Datalog Rule Set**

The following rules implement the four reasoning tasks. They are written as Datalog-style pseudocode in Soufflé-inspired syntax, with typed declarations, negation-as-failure, and explicit stratification (Section 2.4). The Python reference implementation realises the same semantics; the three-valued Uncertain path (Definition 4\) is handled in the implementation rather than in the two-valued rule set. A fully executable rule set distinguishing false from unknown conditions would introduce additional predicates (knownProperty, conditionFalse, conditionUnknown, HasFalseCondition, HasUnknownCondition, NotApplicable, Uncertain) and is identified as a future-work extension.

% \--- Type declarations (Souffle-style) \---  
.decl condPred(condition:symbol, predicate:symbol)  
.decl condVal(condition:symbol, value:symbol)  
.decl sysProp(system:symbol, predicate:symbol, value:symbol)  
.decl hasCondition(obligation:symbol, condition:symbol)  
.decl hasException(obligation:symbol, exception:symbol)  
.decl excCondition(exception:symbol, condition:symbol)  
.decl hasObligation(clause:symbol, obligation:symbol)  
.decl requiresEvidence(obligation:symbol, evidence:symbol)  
.decl holdsEvidence(system:symbol, evidence:symbol)  
.decl obligActor(obligation:symbol, actor:symbol)  
.decl systemActor(system:symbol, actor:symbol)  
.decl obligAction(obligation:symbol, action:symbol)  
.decl incompatibleActions(action1:symbol, action2:symbol)  
.decl hasRiskLevel(system:symbol, level:symbol)  
.decl hasDomain(system:symbol, domain:symbol)  
.decl hasDeployment(system:symbol, deployment:symbol)  
.decl hasCapability(system:symbol, capability:symbol)

.decl conditionSatisfied(condition:symbol, system:symbol)  
.decl MissingCondition(obligation:symbol, system:symbol)  
.decl AllConditionsSatisfied(obligation:symbol, system:symbol)  
.decl exceptionFired(obligation:symbol, system:symbol)  
.decl actorMatches(obligation:symbol, system:symbol)  
.decl Applicable(obligation:symbol, system:symbol)  
.decl EvidenceGap(obligation:symbol, system:symbol, evidence:symbol)  
.decl Conflict(o1:symbol, o2:symbol, system:symbol)  
.decl RemediationCandidate(system:symbol, evidence:symbol)

% \--- Bridge rules (Stratum 0\) \---  
sysProp(S, riskLevel, R) :- hasRiskLevel(S, R).  
sysProp(S, domain, D)    :- hasDomain(S, D).  
sysProp(S, actor, A)     :- systemActor(S, A).  
sysProp(S, deployment, D):- hasDeployment(S, D).  
sysProp(S, capability, C):- hasCapability(S, C).

% \--- R1 Condition satisfaction (Stratum 0\) \---  
conditionSatisfied(C, S) :- condPred(C, P), condVal(C, V), sysProp(S, P, V).

% \--- R1b Missing condition (Stratum 1\) \---  
MissingCondition(O, S) :- hasCondition(O, C), NOT conditionSatisfied(C, S).

% \--- R2 Universal condition satisfaction \- corrected (Stratum 2\) \---  
AllConditionsSatisfied(O, S) :- hasObligation(\_, O), NOT MissingCondition(O, S).

% \--- R3 Exception firing (Stratum 1\) \---  
exceptionFired(O, S) :- hasException(O, X), excCondition(X, C), conditionSatisfied(C, S).

% \--- R4 Actor matching and activation (Stratum 3\) \---  
actorMatches(O, S) :- obligActor(O, A), systemActor(S, A).  
actorMatches(O, S) :- obligActor(O, "Mixed"), systemActor(S, \_).  
actorMatches(O, S) :- obligActor(O, \_), systemActor(S, "Mixed").  
Applicable(O, S) :- actorMatches(O, S), AllConditionsSatisfied(O, S), NOT exceptionFired(O, S).

% \--- R5 Evidence-gap detection (Stratum 4\) \---  
EvidenceGap(O, S, E) :- Applicable(O, S), requiresEvidence(O, E), NOT holdsEvidence(S, E).

% \--- R6 Direct conflict detection with canonical ordering (Stratum 4\) \---  
Conflict(O1, O2, S) :-  
  Applicable(O1, S), Applicable(O2, S),  
  obligActor(O1, A), obligActor(O2, A),  
  obligAction(O1, Act1), obligAction(O2, Act2),  
  incompatibleActions(Act1, Act2), O1 \< O2.

% \--- R7 Evidence-remediation candidates (Stratum 4\) \---  
RemediationCandidate(S, E) :- EvidenceGap(\_, S, E).

% \--- Incompatibility axioms (illustrative; full set in rules/incompatibility\_axioms.yaml) \---  
incompatibleActions("ACT-FullAutomatedDecision", "ACT-RequireHumanOverride").  
incompatibleActions("ACT-RetainDataMaximal", "ACT-MinimiseDataRetention").  
incompatibleActions("ACT-ProhibitedPurposeUse", "ACT-PermittedPurposeUse").  
incompatibleActions("ACT-DiscloseToPublic", "ACT-MaintainConfidentiality").

# **Appendix B. Proof Sketches for Properties 1–4**

**Property 1 (Soundness of activation).** By R4, Applicable(O, S) is derived only when (i) actorMatches(O, S), (ii) AllConditionsSatisfied(O, S), and (iii) NOT exceptionFired(O, S). By R2, AllConditionsSatisfied(O, S) holds iff there is no missing condition for O in S, i.e. every C ∈ C\_o satisfies conditionSatisfied(C, S) via R1. By R3, exceptionFired(O, S) holds iff at least one exception condition is satisfied. Actor matching corresponds to Definition 4's actor constraint. The conjunction is precisely A(o, S) \= Applicable. Under stratified Datalog with CWA, perfect-model semantics derives no facts beyond those entailed by rules and base facts. □

**Property 2 (Activation monotonicity over positive profile extensions).** Fix the obligation graph, condition vocabulary, exception definitions, and rule vocabulary; let S ⊆ S′ over system-profile facts only, with no fact in S′ \\ S satisfying an exception condition of o. Then exceptionFired(o, S′) holds iff exceptionFired(o, S) holds. Adding system-profile facts cannot introduce missing conditions because R2 derives AllConditionsSatisfied from the absence of missing conditions, and added facts can only satisfy conditions. Therefore Applicable(o, S) implies Applicable(o, S′). The qualification is necessary. □

**Property 3 (Anti-monotonicity of evidence gaps).** Fix the obligation set and applicability relation. By R5, EvidenceGap(O, S, E) is derived iff Applicable(O, S), requiresEvidence(O, E), and NOT holdsEvidence(S, E). Adding holdsEvidence(S, E′) cannot make Applicable(O, S) false (Property 2 with trivial extension) and cannot make other holdsEvidence atoms false. Therefore the gap set can only shrink or stay the same. □

**Property 4 (Bounded completeness of gap detection).** Under CWA, holdsEvidence(S, E) is false for any E not explicitly asserted. R5 fires for every E ∈ requiresEvidence(O) not held; EvidenceGap is derived for all and only elements of E\_o \\ E\_held within the evidence vocabulary. Evidence types outside the vocabulary cannot be reported; this is the schema-coverage bound. □

# **Appendix C. System Profile Schema (Illustrative)**

LEXON system profiles are JSON objects conforming to the following structure (illustrative; the authoritative JSON Schema is in the companion repository).

{  
  "instance\_id": "SYS-XXX",  
  "capabilities": \["GenerativeAI | Classification | Biometric | DecisionSupport | Recommendation | CCTV"\],  
  "domain": "Healthcare | Employment | Education | CriticalInfra | Biometric | General | PublicServices",  
  "risk\_level": "Unacceptable | HighRisk | LimitedRisk | MinimalRisk | Underspecified",  
  "actor": "Provider | Deployer | Importer | User | Mixed",  
  "deployment\_context": "EU\_Market | Non\_EU | Research\_Exemption",  
  "properties": {  
    "affectsNaturalPerson": true,  
    "isDeployed": true,  
    "hasResearchExemption": false,  
    "isExclusiveSelfUse": false,  
    "hasSystemicRisk": false,  
    "processesSpecialCategory": false,  
    "logsUnderControl": true  
  },  
  "evidence\_held": \["E-RiskAssessment", "E-SystemCard"\],  
  "profile\_complete": true  
}

# **References**

1\. European Parliament and Council of the European Union. Regulation (EU) 2024/1689 of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). Off. J. Eur. Union 2024, L 1689\.

2\. National Institute of Standards and Technology. Artificial Intelligence Risk Management Framework (AI RMF 1.0); NIST AI 100-1; U.S. Department of Commerce: Gaithersburg, MD, USA, 2023\.

3\. International Organization for Standardization. ISO/IEC 42001:2023 Information Technology — Artificial Intelligence — Management System; ISO: Geneva, Switzerland, 2023\.

4\. Mitchell, M.; Wu, S.; Zaldivar, A.; Barnes, P.; Vasserman, L.; Hutchinson, B.; Spitzer, E.; Raji, I.D.; Gebru, T. Model cards for model reporting. In Proc. FAT\* '19, Atlanta, GA, USA, 2019; pp. 220–229.

5\. Gebru, T.; Morgenstern, J.; Vecchione, B.; Vaughan, J.W.; Wallach, H.; Daumé III, H.; Crawford, K. Datasheets for datasets. Commun. ACM 2021, 64, 86–92.

6\. Koreeda, Y.; Manning, C.D. ContractNLI: A dataset for document-level natural language inference for contracts. In Findings of EMNLP 2021; pp. 1907–1919.

7\. Chalkidis, I.; Jana, A.; Hartung, D.; Bommarito, M.; Androutsopoulos, I.; Katz, D.M.; Aletras, N. LexGLUE: A benchmark dataset for legal language understanding in English. In Proc. ACL 2022; pp. 4310–4330.

8\. Lam, K.W.; Sleeman, D.; Pan, J.Z.; Vasconcelos, W. A privacy policy question-answering assistant. CEUR Workshop Proc. 2020, 2604\.

9\. Hoekstra, R.; Breuker, J.; Di Bello, M.; Boer, A. The LKIF Core Ontology of Basic Legal Concepts. In Proc. LOAIT 2007, Stanford, CA, USA; pp. 43–63.

10\. Athan, T.; Governatori, G.; Palmirani, M.; Paschke, A.; Wyner, A. LegalRuleML: Design principles and foundations. In Reasoning Web; LNCS 9203; Springer: Cham, 2015; pp. 151–188.

11\. Iannella, R.; Villata, S. (Eds.) ODRL Information Model 2.2; W3C Recommendation; W3C, 2018\.

12\. Pandit, H.J.; Polleres, A.; Bos, B.; Brennan, R.; et al. Creating a vocabulary for data privacy: First-year report of the DPVCG. In Proc. OTM Conferences 2019; pp. 714–730.

13\. Governatori, G.; Olivieri, F.; Rotolo, A.; Scannapieco, S.; Sartor, G. Two approaches to semantic legislative drafting. Artif. Intell. Law 2016, 24, 291–321.

14\. Knublauch, H.; Kontokostas, D. Shapes Constraint Language (SHACL); W3C Recommendation; W3C, 2017\.

15\. Palmirani, M.; Vitali, F. Akoma Ntoso for legal documents. In Legislative XML for the Semantic Web; Springer: Dordrecht, 2011; pp. 75–100.

16\. Procope, C.; Cheema, A.; Adkins, D.; et al. System-level transparency of machine learning. In Proc. AIES 2023, Montreal, QC, Canada.

17\. Holland, S.; Hosny, A.; Newman, S.; Joseph, J.; Chmielinski, K. The dataset nutrition label. In Data Protection and Privacy; Hart Publishing: Oxford, 2020; pp. 1–26.

18\. Blair-Stanek, A.; Holzenberger, N.; Van Durme, B. Can GPT-3 perform statutory reasoning? In Proc. ICAIL 2023, Braga, Portugal; pp. 22–31.

19\. Guha, N.; Nyarko, J.; Ho, D.E.; Ré, C.; et al. LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models. In NeurIPS 36, 2023\.

20\. Niklaus, J.; Chalkidis, I.; Stürmer, M. Swiss-Judgment-Prediction: A multilingual legal judgment prediction benchmark. In Proc. NLLP Workshop 2021; pp. 19–35.

21\. Butler, T.; O'Brien, L. Understanding RegTech for digital regulatory compliance. In Disrupting Finance; Palgrave Pivot: Cham, 2019; pp. 85–102.

22\. Apt, K.R.; Blair, H.A.; Walker, A. Towards a theory of declarative knowledge. In Foundations of Deductive Databases and Logic Programming; Morgan Kaufmann, 1988; pp. 89–148.

23\. Przymusinski, T.C. On the declarative semantics of deductive databases and logic programs. In Foundations of Deductive Databases and Logic Programming; Morgan Kaufmann, 1988; pp. 193–216.

24\. Sergot, M.J.; Sadri, F.; Kowalski, R.A.; Kriwaczek, F.; Hammond, P.; Cory, H.T. The British Nationality Act as a logic program. Commun. ACM 1986, 29, 370–386.

25\. Abiteboul, S.; Hull, R.; Vianu, V. Foundations of Databases; Addison-Wesley: Reading, MA, USA, 1995\.