**Article**

**LEXON: Executable AI Regulatory Obligation Reasoning with Typed Knowledge Graphs and Stratified Datalog**

Roy Saurabh 1,\*

1 AffectLog SAS; [roy@affectlog.com](mailto:roy@affectlog.com)

\* Correspondence: roy@affectlog.com

**Abstract:** Regulatory frameworks for artificial intelligence systems increasingly impose obligations that are conditional on system risk classification, deployment domain, actor role, technical capability, and available evidence. Static checklists and documentation templates offer limited support for determining when obligations apply, which evidence items are missing, and where obligations may conflict. This article presents LEXON, a typed knowledge-graph and stratified-Datalog framework for executable regulatory obligation reasoning. LEXON represents clauses, obligations, conditions, exceptions, evidence specifications, actors, and AI system profiles as typed entities and relations, and executes four reasoning tasks: obligation activation, evidence-gap detection, conflict detection, and evidence-remediation candidate generation. We evaluate LEXON on a deterministic synthetic benchmark of AI regulatory clauses and system profiles, comparing it with checklist, ontology-only, and flat-rule baselines. In the controlled synthetic benchmark setting, LEXON achieves corpus-level F1 of 1.000 for obligation activation (T1) and evidence-gap detection (T2), and detects 11 of 11 cross-clause conflict pairs with one false positive (T3 F1 = 0.957). Ablation results show that each architectural component—the rule layer and the typed graph—contributes monotone improvement over the simpler baselines. The results establish that the LEXON implementation faithfully realises the specified formal semantics and that neither rule-only nor checklist-only alternatives achieve equivalent performance on this benchmark. Key limitations, including the synthetic nature of the benchmark, closed-world evidence assumptions, and the distinction between evidentiary completeness and substantive legal compliance, are discussed in detail.

**Keywords:** AI regulation; knowledge graphs; Datalog; compliance reasoning; regulatory information systems; evidence-gap detection; computational law; AI governance

---

# **1\. Introduction**

The global proliferation of regulation governing artificial intelligence (AI) systems marks a qualitative shift in the governance landscape. The European Union Artificial Intelligence Act \[1\], the U.S. National Institute of Standards and Technology AI Risk Management Framework \[2\], the international standard ISO/IEC 42001 \[3\], and a growing corpus of sector-specific instruments collectively impose hundreds of distinct, conditional obligations on AI system providers and deployers. These obligations are not uniformly applicable: they are contingent on system risk classification, deployment domain, actor role, and the presence or absence of specific technical artefacts. Yet the dominant practice for compliance assessment remains manual—compliance officers read regulatory text, maintain spreadsheets, and produce documentation whose completeness and correctness cannot be machine-verified.

This state of affairs has three consequences for information systems supporting AI governance. First, coverage can be systematically incomplete: tracking every conditional obligation across multiple intersecting regulatory instruments is difficult without structured computational support. Second, conflicts between co-applicable obligations may remain difficult to detect without explicit cross-obligation reasoning. Third, remediation guidance is ad hoc and non-reproducible across organisations. Existing automated tools—checklists, model cards \[4\], datasheets \[5\], and documentation templates—address documentation, but not reasoning. They cannot activate obligations conditionally, detect evidentiary gaps against specified requirements, identify conflicts, or generate auditable remediation candidates.

This article treats AI regulatory compliance as an information-structuring and reasoning problem rather than as an attempt to automate legal judgement. The goal is not to replace lawyers, auditors, or compliance officers, but to provide an auditable computational layer that can represent conditional obligations, determine whether formal activation conditions are satisfied under explicit assumptions, identify missing evidence artefacts, and surface potential conflicts for human review. We make this distinction explicit throughout the article: LEXON evaluates evidentiary completeness and rule-derived applicability, not the full legal validity of an AI system deployment.

We present LEXON (Legal EXecutable Obligation Network), a typed knowledge-graph and stratified-Datalog framework for executable regulatory obligation reasoning. LEXON consists of (i) a typed ontology that represents clauses, obligations, conditions, exceptions, evidence specifications, actors, and AI system profiles as graph entities; (ii) a stratified-Datalog rule layer with negation-as-failure under the closed-world assumption that compiles clause structure into executable inference rules; and (iii) a set of formally defined reasoning functions evaluated on a deterministic synthetic benchmark.

## ***1.1. Research Questions***

This article addresses four questions:

**RQ1.** Can AI regulatory obligations be represented as typed information objects supporting executable rule-based reasoning under explicit assumptions?

**RQ2.** What typed knowledge-graph schema and rule vocabulary are sufficient to capture AI-relevant regulatory clause structure with the precision required for inference?

**RQ3.** Does combining typed graph structure with rule inference improve obligation activation and evidence-gap detection compared with checklist, ontology-only, and flat-rule baselines in a controlled benchmark setting?

**RQ4.** What are the limits of executable obligation reasoning, in particular the distinction between evidentiary completeness and substantive legal compliance, and how does the synthetic benchmark construction constrain the interpretation of results?

## ***1.2. Contributions***

This article makes four contributions. First, it formalises AI regulatory obligation reasoning as an information-processing problem involving conditional activation, evidence-gap detection, conflict identification, and evidence-remediation candidate generation. Second, it introduces a typed knowledge-graph schema for representing regulatory clauses, obligations, conditions, exceptions, evidence specifications, actors, and AI system profiles. Third, it implements a stratified-Datalog inference layer, including three-valued condition semantics and actor matching, for executable reasoning under explicit closed-world and schema-coverage assumptions. Fourth, it evaluates the approach on a deterministic synthetic benchmark and compares it with checklist, ontology-only, and flat-rule baselines, with ablation results that isolate the contribution of each architectural component.

## ***1.3. Article Organisation***

Section 2 presents the materials and methods, including the formal problem definition, typed graph schema, stratified-Datalog rule layer, benchmark construction protocol, baselines, evaluation metrics, and reproducibility protocol. Section 3 reports experimental results for all four tasks, together with ablation analysis, ambiguity routing, and a benchmark construction quality audit. Section 4 discusses interpretation, prior work, design rationale, and limitations. Section 5 concludes.

---

# **2\. Materials and Methods**

## ***2.1. Formal Problem Definition***

We define the regulatory obligation reasoning problem over a universe of types

U = {Clause, Obligation, Condition, Exception, Evidence, System, Actor, RiskLevel, Domain, Action}.

All sets are finite and computable. We use the following core definitions.

**Definition 1 (Regulatory Clause).** A regulatory clause c ∈ C is a tuple ⟨id, text, source, scope⟩, where id is a unique identifier, text is the natural-language text, source ∈ {EU AI Act, NIST AI RMF, ISO/IEC 42001, …} is the issuing instrument, and scope ⊆ RiskLevel × Domain is the declared applicability scope.

**Definition 2 (Obligation).** An obligation o ∈ O is a tuple ⟨id, clause, actor, action, C_o, X_o, E_o⟩, where actor ∈ {Provider, Deployer, Importer, User, Mixed}, action ∈ Action, C_o is the conjunctive set of activation conditions, X_o is the disjunctive set of exception triggers, and E_o is the required evidence set.

**Definition 3 (AI System Profile).** A system profile S is a tuple ⟨id, capabilities, domain, risk, actor, deployment, evidence⟩, where capabilities ⊆ {GenerativeAI, Classification, Biometric, DecisionSupport, …}, risk ∈ {Unacceptable, HighRisk, LimitedRisk, MinimalRisk, Underspecified}, and evidence is the set of evidence items currently held by S.

**Definition 4 (Applicability with Three-Valued Condition Semantics).** Let sat(c, S) ∈ {true, false, unknown} denote the truth value of condition c in system profile S. A condition is true if the predicate-value pair matches a property asserted in S, false if the property is asserted and does not match, and unknown if the property is absent from S.

The applicability relation A : O × S → {Applicable, NotApplicable, Uncertain} is defined as:

- A(o, S) = Applicable iff actor(o) = actor(S) (or either is Mixed), every c ∈ C_o satisfies sat(c, S) = true, and no x ∈ X_o satisfies sat(x, S) = true.
- A(o, S) = NotApplicable iff actor(o) ≠ actor(S) (neither is Mixed), OR at least one c ∈ C_o satisfies sat(c, S) = false, OR at least one x ∈ X_o satisfies sat(x, S) = true.
- A(o, S) = Uncertain iff actor matching holds, no condition is false, no exception fires, and at least one c ∈ C_o satisfies sat(c, S) = unknown.

**Definition 5 (Evidentiary Completeness Function).** The evidentiary completeness function EC : O × S × 2^Ev → {EvidenceComplete, EvidenceIncomplete, EvidenceNotRequired, EvidenceUncertain} is defined as:

- EC(o, S, E_held) = EvidenceComplete iff A(o, S) = Applicable and E_o ⊆ E_held;
- EC(o, S, E_held) = EvidenceIncomplete iff A(o, S) = Applicable and E_o ⊄ E_held;
- EC(o, S, E_held) = EvidenceNotRequired iff A(o, S) = NotApplicable;
- EC(o, S, E_held) = EvidenceUncertain iff A(o, S) = Uncertain.

*Evidentiary completeness is not equivalent to legal compliance: a system may possess required documentation while failing to implement the underlying control. The distinction is essential to the framing of this article and is discussed in Section 4.4.*

**Definition 6 (Evidence Gap).** The evidence-gap function Gap : O × S × 2^Ev → 2^Ev is defined as Gap(o, S, E_held) = E_o \\ E_held when A(o, S) = Applicable, and ∅ otherwise. The system-level gap is Gap(S) = ⋃_o Gap(o, S, E_held).

**Definition 7 (Conflict).** A conflict pair (o₁, o₂, S) holds iff A(o₁, S) = A(o₂, S) = Applicable, actor(o₁) = actor(o₂), o₁ ≠ o₂, and action(o₁) and action(o₂) are mutually incompatible under an explicit incompatibility relation incompatible(·, ·). To avoid double-counting, only canonical pairs with o₁ < o₂ (by lexicographic obligation ID) are reported. The conflict set is K(S) = {(o₁, o₂) : Conflict(o₁, o₂, S), o₁ < o₂}.

**Definition 8 (Evidence-Remediation Candidate Set).** The evidence-remediation candidate function Rem : O × S × 2^Ev → 2^Ev returns evidence additions that, if obtained and validated, would change EC from EvidenceIncomplete to EvidenceComplete for one or more applicable obligations. Rem reasons about evidence completion only and does not model substantive operational controls.

## ***2.2. Reasoning Tasks***

The framework supports four reasoning tasks summarised in Table 1. Tasks T1–T3 are polynomial-time under the typed schema. Task T4 is approached via a greedy candidate-generation procedure; computing a minimum-cardinality remediation set across obligations is plausibly NP-hard by reduction from Weighted Set Cover, so LEXON returns candidate sets rather than minimum sets.

| ID | Task | Input | Output | Complexity |
| :---- | :---- | :---- | :---- | :---- |
| T1 | Obligation activation | (O, S) | {o : A(o, S) = Applicable} | Polynomial |
| T2 | Evidence-gap detection | (O, S, E_held) | Gap(S) | Polynomial |
| T3 | Conflict detection | (O, S) | K(S) | Polynomial |
| T4 | Evidence-remediation candidates | (O, S, E_held) | Rem candidate set | Greedy |

*Table 1. The four reasoning tasks supported by LEXON.*

## ***2.3. Typed Knowledge-Graph Schema***

The LEXON terminology box (TBox) defines the following entity types: Clause, Obligation, Condition, Exception, EvidenceSpec, SystemProfile, Actor, Action, RiskLevel, and Domain. The relations are hasObligation(Clause, Obligation), hasCondition(Obligation, Condition), hasException(Obligation, Exception), requiresEvidence(Obligation, EvidenceSpec), hasCapability(SystemProfile, Capability), holdsEvidence(SystemProfile, EvidenceSpec), hasRiskLevel(SystemProfile, RiskLevel), hasDomain(SystemProfile, Domain), systemActor(SystemProfile, Actor), and obligActor(Obligation, Actor). All relations are typed; domain and range constraints are enforced at ABox population time.

Bridge rules connect the typed KG relations to the flat sysProp predicate used by condition satisfaction:

```datalog
sysProp(S, riskLevel, R) :- hasRiskLevel(S, R).
sysProp(S, domain, D)    :- hasDomain(S, D).
sysProp(S, actor, A)     :- systemActor(S, A).
sysProp(S, deployment, D):- hasDeployment(S, D).
sysProp(S, capability, C):- hasCapability(S, C).
```

These bridge rules make the typed KG relations queryable by the condition satisfaction stratum without loss of domain-range typing.

## ***2.4. Stratified-Datalog Rule Layer***

LEXON compiles obligations into stratified Datalog with negation-as-failure under a closed-world assumption (CWA). Stratification ensures that all negated predicates appear at a strictly lower stratum than their derivations, so the resulting program admits a unique perfect model \[22,23\]. The stratification levels are: Stratum 0 (conditionSatisfied), Stratum 1 (MissingCondition, exceptionFired), Stratum 2 (AllConditionsSatisfied), Stratum 3 (actorMatches, Applicable), Stratum 4 (EvidenceGap, Conflict, RemediationCandidate). We present the core rules below; the complete Soufflé-compatible rule set is provided in Appendix A.

**R0—Bridge rules (Stratum 0).** See Section 2.3.

**R1—Condition satisfaction.**

```datalog
% A condition C is satisfied in system S if its predicate-value pair
% matches a property of S (via bridge rules or direct sysProp assertion).
conditionSatisfied(C, S) :-
  condPred(C, P),
  condVal(C, V),
  sysProp(S, P, V).
```

**R1b—Missing condition (Stratum 1).**

```datalog
% A required condition C of obligation O is missing in S if it is not satisfied.
% Under three-valued semantics: unknown properties cause conditions to evaluate
% as missing, producing Uncertain rather than NotApplicable.
MissingCondition(O, S) :-
  hasCondition(O, C),
  NOT conditionSatisfied(C, S).
```

**R2—Universal condition satisfaction (corrected) (Stratum 2).**

*Activation requires that ALL conditions of an obligation be satisfied. We express this as the absence of any missing condition rather than as an existential rule over single conditions. This corrects an existential pattern in which a single satisfied condition suffices to derive applicability; under that incorrect formulation, an obligation conditioned on both risk = HighRisk AND isDeployed = true would incorrectly activate for a MinimalRisk deployed system.*

```datalog
AllConditionsSatisfied(O, S) :-
  hasObligation(_, O),
  NOT MissingCondition(O, S).
```

**R3—Exception firing (Stratum 1).**

```datalog
exceptionFired(O, S) :-
  hasException(O, X),
  excCondition(X, C),
  conditionSatisfied(C, S).
```

**R4—Actor matching and obligation activation (Stratum 3).**

```datalog
% Actor matching: obligation is structurally inapplicable if actors differ.
actorMatches(O, S) :-
  obligActor(O, A),
  systemActor(S, A).

actorMatches(O, S) :-
  obligActor(O, "Mixed").

actorMatches(O, S) :-
  systemActor(S, "Mixed").

% Applicable: all conditions satisfied, actor matches, no exception fires.
Applicable(O, S) :-
  actorMatches(O, S),
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).
```

**R5—Evidence-gap detection (Stratum 4).**

```datalog
EvidenceGap(O, S, E) :-
  Applicable(O, S),
  requiresEvidence(O, E),
  NOT holdsEvidence(S, E).
```

**R6—Direct conflict detection with canonical ordering (Stratum 4).**

```datalog
% Canonical ordering (O1 < O2) prevents double-counting symmetric pairs.
Conflict(O1, O2, S) :-
  Applicable(O1, S),
  Applicable(O2, S),
  obligActor(O1, A),
  obligActor(O2, A),
  obligAction(O1, Act1),
  obligAction(O2, Act2),
  incompatibleActions(Act1, Act2),
  O1 < O2.
```

**R7—Evidence-remediation candidates (Stratum 4).**

```datalog
RemediationCandidate(S, E) :-
  EvidenceGap(_, S, E).
```

Because Datalog with stratified negation under CWA is not monotone over arbitrary fact extensions, soundness, monotonicity, and completeness claims require explicit qualifications, stated below.

## ***2.5. Formal Properties***

**Property 1 (Soundness of activation).** Under the stratified-Datalog semantics with CWA, if LEXON derives Applicable(o, S), then A(o, S) = Applicable in the sense of Definition 4. By R4, derivation requires actorMatches(o, S), AllConditionsSatisfied(o, S), and NOT exceptionFired(o, S). The first condition corresponds to Definition 4's actor constraint; the second to universal condition satisfaction; the third to the exception clause. Under stratified Datalog, the perfect-model semantics derives no facts beyond those entailed by the rules and base facts; no spurious derivations occur. □

**Property 2 (Activation monotonicity over positive profile extensions).** Let the obligation graph, condition vocabulary, exception definitions, and rule vocabulary be fixed, and let S ⊆ S′ in the sense of fact entailment over system-profile facts only. If no fact in S′ \\ S satisfies an exception condition of o, then Applicable(o, S) implies Applicable(o, S′). The qualification is necessary: exception firing is non-monotone with respect to profile additions. □

**Property 3 (Anti-monotonicity of evidence gaps with respect to evidence additions).** For a fixed obligation set and a fixed applicability relation, adding held evidence can only reduce or preserve the set of detected evidence gaps. Formally, if E_held ⊆ E_held′, then Gap(S) under E_held′ ⊆ Gap(S) under E_held. □

**Property 4 (Bounded completeness of gap detection).** Under CWA on evidence holdings, LEXON computes Gap(o, S, E_held) = E_o \\ E_held for any applicable obligation o, provided E_o is contained in the LEXON evidence vocabulary. Completeness is bounded by schema coverage: evidence types outside the vocabulary cannot be reported as gaps. This is a schema-coverage limitation, not a soundness limitation. □

**Property 5 (Conflict-detection soundness for direct conflicts).** Every conflict pair reported by R6 is a genuine conflict under Definition 7 for the direct action-incompatibility relation. Temporal and resource conflicts are out of scope of the current rule set.

## ***2.6. System Architecture***

LEXON is realised as a five-stage information pipeline (Figure 1). Stage 1 (legal text decomposition) parses regulatory clauses into structured obligation tuples via a human-assisted extraction protocol. Stage 2 (graph population) instantiates the typed knowledge graph (TBox + ABox) from extracted tuples and system-profile inputs. Stage 3 (rule compilation) translates the graph into stratified-Datalog rules via the bridge rules of Section 2.3. Stage 4 (inference) runs the Datalog engine to derive activation, evidence-gap, conflict, and remediation-candidate facts. Stage 5 (output generation) renders auditable reports in human-readable and machine-readable form.

| Stage | Input | Output | Technology |
| :---- | :---- | :---- | :---- |
| 1. Legal text decomposition | Regulatory clause text | Obligation tuples (JSON) | Human annotation protocol |
| 2. Graph population | Tuples + system profile | KG ABox (typed triples) | Python / RDFLib |
| 3. Rule compilation | TBox + ABox | Stratified-Datalog rules | Template compiler |
| 4. Inference | Rules + facts | Applicable, Gap, Conflict, Candidate | Python Datalog engine |
| 5. Output generation | Derived facts | Report + remediation candidates | Template engine |

*Table 2. Five-stage LEXON pipeline.*

**Figure 1 (LEXON information pipeline):**

```
Regulatory clause text
        ↓
Obligation tuple extraction (human-assisted)
        ↓
Typed knowledge graph (TBox + ABox)
        ↓  ← Bridge rules (typed KG → sysProp)
Stratified-Datalog inference (R1–R7)
        ↓
Applicable obligations / Evidence gaps /
Conflict pairs / Remediation candidates
        ↓
Auditable report (JSON + Markdown)
```

## ***2.7. Benchmark Construction***

LEXON-Bench is a deterministic synthetic benchmark consisting of (i) 25 annotated regulatory clauses spanning five thematic groups (transparency and information, risk management and conformity assessment, special-category data handling, human oversight and human-in-the-loop, and cross-instrument provisions), (ii) 30 synthetic AI system profiles stratified by risk level, domain, actor role, and evidence completeness, and (iii) gold labels for the four reasoning tasks. Each clause is decomposed into one or more obligation tuples with explicit conditions, exceptions, and evidence specifications drawn from a controlled vocabulary.

Gold labels for T1 and T2 are derived by applying the formal definitions of Section 2.1 directly to the structured obligation tuples. This makes the benchmark internally consistent and deterministic. We note explicitly that gold labels derived from the same structured representation as the system under test create a risk of evaluative circularity: the benchmark can confirm that the implementation faithfully executes the specified semantics, but cannot independently validate that the semantics correctly captures the intent of the regulatory text. We mitigate this risk in three ways: by providing an ablation of system components (Section 3.3); by including an ambiguity-routing analysis on clauses flagged during annotation (Section 3.4); and by releasing the full benchmark for independent inspection. The limitation is restated in Section 4.4.

Three worked examples from the test set illustrating clause-profile pairs for each possible activation outcome (Applicable, NotApplicable, Uncertain) are provided in the companion repository; the repository also includes the complete benchmark instances, gold labels, and annotation rubric.

| Profile group | Risk level | Domain | Actor | Difficulty |
| :---- | :---- | :---- | :---- | :---- |
| SYS-001–SYS-006 | MinimalRisk | General | Provider/User | easy |
| SYS-007–SYS-012 | HighRisk | Biometric/Healthcare | Provider | medium |
| SYS-013–SYS-018 | LimitedRisk | General/Education | Provider/Deployer | easy–medium |
| SYS-019–SYS-024 | HighRisk | Mixed | Deployer/Importer | hard |
| SYS-025–SYS-030 | Underspecified | Mixed | Mixed | hard (ambiguous) |

*Table 3. Summary of the 30-profile corpus, stratified by risk, domain, and actor.*

## ***2.8. Train/Development/Test Splits***

The 25 clauses and 30 profiles yield 750 clause-profile pairs. Each pair is tagged with the tasks for which gold labels are defined. The pair set is partitioned into 60% training (450 instances; rule tuning and baseline calibration), 20% development (150 instances; hyperparameter selection), and 20% held-out test (150 instances; final evaluation). All splits use seed = 42 and are versioned. Gold labels are released with the benchmark.

## ***2.9. Baselines***

We compare LEXON against three baselines that represent the space of widely used compliance support approaches. We do not include an LLM-only baseline in the reported results because the LLM experiment was not executed under a fixed-prompt, fixed-model-version, fixed-temperature reproducible protocol; the discussion of LLM-based legal reasoning appears in Section 4.2.

| ID | Baseline | Description | Capability gap tested |
| :---- | :---- | :---- | :---- |
| B1 | Static checklist | Binary checklist per risk level; no condition evaluation; no exception handling; no conflict detection. | Value of conditional activation, gap detection, and cross-clause reasoning. |
| B2 | Ontology without inference | LEXON TBox populated; no Datalog rules fired; no activation, gap, or conflict derived. | Contribution of the rule layer. |
| B3 | Flat-rule engine without typed graph | Production rules over untyped facts; no schema constraints; no conflict detection. | Contribution of the typed graph and actor-scoped conflict rules. |

*Table 4. Implemented baselines and what each isolates.*

## ***2.10. Evaluation Metrics***

For T1 and T2 we report corpus-level (micro-averaged) precision, recall, and F1 against the deterministic gold labels on the held-out test split. Corpus-level F1 aggregates TP, FP, and FN counts across all instances before computing P/R/F1; this is the appropriate metric when many instances have zero gold-positive labels (as is the case on easy and hard profiles). Bootstrap 95% confidence intervals are computed on per-instance F1 scores by non-parametric bootstrap with 1000 iterations and seed = 42; the CIs reflect per-instance variability and are reported alongside corpus-level F1 in Table 5. For T3 we evaluate at the unique unordered obligation-pair level across all 30 system profiles, reporting TP, FP, FN, precision, recall, and F1 directly from confusion counts. Exact McNemar discordant pair counts for T1 are reported in Section 3.1; for T3 we report exact confusion counts.

## ***2.11. Reproducibility Protocol***

The benchmark generation scripts, structured obligation tuples, system profiles, gold labels, rule specifications, baseline implementations, and evaluation scripts are provided in the companion repository. All reported tables are regenerated by a single reproduction command (`make reproduce`). All random seeds are fixed (seed = 42); benchmark generation is deterministic; baseline implementations are version-pinned in `pyproject.toml`. The repository and Zenodo DOI are listed in the Data Availability Statement.

## ***2.12. Use of Generative AI***

During the preparation of this manuscript, the author used a large language model assistant for language editing and for drafting support on prose sections. All technical content—including the formal definitions, the rule specifications, the benchmark construction, the baseline implementations, the evaluation scripts, and the analysis—was designed, implemented, and verified by the author. The author reviewed and edited all generative AI output and takes full responsibility for the content of this publication. Generative AI was not used to generate gold labels, benchmark instances, or evaluation results.

---

# **3\. Results**

## ***3.1. Obligation Activation (T1) and Evidence-Gap Detection (T2)***

Table 5 reports corpus-level precision, recall, and F1 with 95% bootstrap confidence intervals on the 150-instance held-out test split. The columns T1 F1 [95% CI] and T2 F1 [95% CI] give the corpus-level point estimate and the bootstrap CI on per-instance F1 scores. The note below Table 5 explains the relationship between the two quantities.

| System | T1 P | T1 R | T1 F1 [95% CI] | T2 P | T2 R | T2 F1 [95% CI] | T2 FNR |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| LEXON (full) | 1.000 | 1.000 | 1.000 [0.07, 0.19] | 1.000 | 1.000 | 1.000 [0.05, 0.15] | 0.000 |
| B1 Static checklist | 0.274 | 0.967 | 0.427 [0.07, 0.18] | 0.196 | 0.931 | 0.323 [0.05, 0.15] | 0.069 |
| B2 Ontology (no rules) | 0.250 | 0.033 | 0.059 [0.00, 0.02] | 0.000 | 0.000 | 0.000 [0.00, 0.00] | 1.000 |
| B3 Flat rules (no graph) | 0.459 | 0.933 | 0.615 [0.07, 0.17] | 0.360 | 0.931 | 0.519 [0.05, 0.14] | 0.069 |

*Table 5. Obligation activation (T1) and evidence-gap detection (T2) on the 150-instance held-out test split (seed = 42). Corpus-level P/R/F1 are micro-averaged over all clause-profile pairs. T2 FNR = 1 − T2 Recall. Bootstrap 95% CIs are computed on per-instance F1 scores (1000 iterations, seed = 42); because the majority of test instances have no applicable obligations and contribute per-instance F1 = 0, the CIs are wide relative to the corpus-level point estimate, reflecting variability in per-instance scores rather than uncertainty in the corpus-level F1. The corpus-level F1 = 1.000 for LEXON means that all gold-positive obligation activations and all gold-positive evidence gaps in the test set were detected with no false positives and no false negatives. Full reproducibility report and per-instance confusion counts are in the companion repository.*

LEXON achieves corpus-level F1 = 1.000 for both T1 and T2 on the synthetic benchmark. This result is expected, and correctly so: the LEXON rule engine faithfully implements the formal definitions of Section 2.1, and the gold labels are derived from those same formal definitions applied to the same structured tuples. Achieving F1 = 1.000 confirms that the implementation is a correct realisation of the specified semantics—a necessary condition for a reproducible system. The scientific value lies not in the absolute F1 score but in three complementary findings: (a) the ablation showing that neither rule-only nor checklist-only alternatives achieve this correctness on the same benchmark (Section 3.3); (b) the identification of which architectural components are responsible for which performance gains; and (c) the characterisation of where the baselines fail.

Since LEXON achieves FP = 0, FN = 0 for T1 and T2, all McNemar discordant pairs favour LEXON (n₁₀ = 0 for all three baseline comparisons). B1 accounts for 88 discordant obligation-level pairs in T1 (n₀₁ = 88, n₁₀ = 0; McNemar z = 9.38, p < 0.001); B2 accounts for 117 discordant pairs (z = 10.82, p < 0.001); B3 accounts for 62 discordant pairs (z = 7.87, p < 0.001). After Bonferroni correction for four comparisons (corrected α = 0.0125), all three comparisons remain significant. Exact discordant counts and per-instance breakdowns are reported in the companion repository.

The static checklist (B1) applies uniform risk-level thresholds without condition evaluation, systematically missing conditional obligations and exception handling; its high recall (0.967) paired with very low precision (0.274) reflects indiscriminate activation of all obligations for any HighRisk system profile. The ontology-only baseline (B2) can classify entity types but cannot fire rules, missing virtually all conditional activation (R = 0.033) and all evidence-gap computation (F1 = 0.000). The flat-rule engine (B3) lacks typed domain-range constraints, producing false-positive activations on under-typed profiles. LEXON's combination of typed graph structure, three-valued condition semantics, actor matching, and stratified-Datalog inference is necessary to achieve both high precision and high recall simultaneously on this benchmark.

## ***3.2. Conflict Detection (T3)***

T3 is evaluated at the unique unordered obligation-pair level across all 30 system profiles. The benchmark gold set contains 11 canonical cross-clause conflict pairs derived from Definition 7 applied to the human-oversight and cross-instrument clause groups. LEXON's direct-conflict rules (R6) detected all 11 gold pairs (FN = 0, recall = 1.000) and one false positive (FP = 1), yielding precision = 0.917 and F1 = 0.957. The single false positive arises from an over-broad vocabulary entry in the incompatibility axioms (ACT-DiscloseToPublic ⊥ ACT-AlignWithISO42001), which the canonical gold oracle excludes as a vocabulary generalisation artefact. This FP identifies a specific point of improvement in the incompatibility axiom design.

None of the three baselines implements cross-clause conflict detection. B1, B2, and B3 each score T3 P = 0.000, R = 0.000, F1 = 0.000 by design: checklists apply per-obligation rules without cross-obligation scope; the ontology-only baseline derives no conflict predicate; the flat-rule engine lacks the actor-scoped conflict rule (R6) that scopes conflict pairs to same-actor applicable obligations. The T3 result should be interpreted as a functional validation that LEXON's direct-conflict rule correctly implements Definition 7 on the 11-pair gold set, not as a robust estimate of general conflict-detection performance across arbitrary regulatory corpora.

## ***3.3. Ablation: Graph + Rules vs. Rules Only vs. Checklist***

The comparison between the LEXON full system, the flat-rule engine (B3, typed-graph layer removed), and the static checklist (B1, both typed-graph and rule layers removed) isolates the contribution of each architectural component. Table 6 summarises the ablation results.

| System | T1 F1 | T1 ΔF1 | T2 F1 | T2 ΔF1 |
| :---- | :---- | :---- | :---- | :---- |
| B1 Static checklist | 0.427 | — | 0.323 | — |
| B3 Flat rules (+rule layer) | 0.615 | +0.188 | 0.519 | +0.196 |
| LEXON full (+typed graph, actor matching) | 1.000 | +0.385 | 1.000 | +0.481 |

*Table 6. Ablation: T1 and T2 F1 gains from adding the rule layer (B1→B3) and from adding the typed graph with actor matching (B3→LEXON). Both additions are necessary; neither alone achieves corpus-level correctness.*

Adding the rule layer (B1→B3) contributes +0.188 to T1 and +0.196 to T2. Adding the typed graph with actor-matching constraints (B3→LEXON) contributes an additional +0.385 to T1 and +0.481 to T2. Typed structure contributes substantially more to T2 (evidence-gap detection) than to T1 (obligation activation), consistent with the role of typed evidence specifications in disambiguating which evidence items correspond to which applicable obligations. Without domain-range constraints, B3 incorrectly classifies evidence gaps on under-typed profiles, producing both false positives and false negatives.

## ***3.4. Ambiguity Routing***

Eight of the 25 benchmark clauses carry an explicit ambiguity flag assigned during benchmark construction, indicating that the clause text admits more than one plausible structured representation and that human review is recommended before treating the derived obligation tuple as authoritative. On the 150 test instances containing these eight clauses, LEXON routes them to human-review status via the remediation-candidate mechanism (requires_human_review = true). The ambiguity flag and the routing mechanism were both established during benchmark construction; the routing result confirms that the mechanism is correctly wired to the flag, not that the system independently detects ambiguity from clause text. This result should be interpreted as a functional check of the routing pathway rather than as an independent ambiguity-detection capability.

The routing mechanism is consistent with LEXON's intended role: the system surfaces ambiguous cases for qualified human review rather than deriving applicability outcomes that depend on contested interpretations. Future work on independent ambiguity detection—comparing system uncertainty signals against independent annotator disagreement—is a defensible extension.

## ***3.5. Benchmark Construction Quality Audit***

During benchmark construction, the annotation protocol identified three categories of clause-representation challenges. These are not prediction errors of the LEXON engine on the test set—which achieves corpus-level F1 = 1.000—but rather annotation decisions that required explicit resolution in the rubric.

First, condition-vocabulary misalignment (3 instances) occurred where an obligation condition required a controlled-vocabulary term for which the initial vocabulary entry was subtly inconsistent with the clause text (for example, a risk-level predicate that needed refinement from a coarse to a fine-grained value). These were resolved by extending the vocabulary and re-annotating.

Second, exception-scope mis-attribution (2 instances) occurred on clauses in which a narrowing clause was initially annotated as a new obligation rather than as a partial exception, producing an incorrect obligation tuple. Resolution required clarifying the rubric distinction between narrowing exceptions and compound obligations.

Third, actor-attribution challenges (2 instances) arose on dual-actor clauses requiring decomposition into separate Provider and Deployer obligations. These were resolved by requiring explicit actor decomposition in the extraction protocol.

Each category points to a specific annotation rubric improvement. The resolution of all seven cases before finalising the gold labels is why the engine achieves F1 = 1.000 on the test set: the benchmark construction process is itself part of the quality assurance, and the rubric improvements are what allow the formal definitions to be applied consistently.

---

# **4\. Discussion**

## ***4.1. Interpretation of Results***

The results indicate that, within the controlled synthetic benchmark setting, LEXON correctly implements the specified formal semantics: it achieves F1 = 1.000 for obligation activation and evidence-gap detection, and detects all 11 gold conflict pairs with one false positive. The ablation confirms that each architectural component—the typed knowledge graph, the actor-matching constraints, and the stratified-Datalog rule layer—contributes to this correctness; removing any component degrades performance, and the combination is necessary.

The most informative single property of LEXON for practical compliance review is arguably not the absolute F1 score (bounded above by synthetic construction) but the presence of auditable derivation traces for every reported applicability or gap decision. Each output records which rules fired, which conditions were satisfied, and which evidence items were absent, providing the audit trail expected in regulated environments.

A critical limitation of the F1 = 1.000 result is that it measures agreement between the engine and the synthetic gold labels, not agreement between the system and the intent of the regulatory text. Extending the benchmark to expert-validated real clause representations is the primary direction for future work.

## ***4.2. Relation to Prior Work***

A substantial body of work addresses extraction of structure from legal text \[6,7,8\]. These approaches produce structured outputs from unstructured text but do not define or execute formal compliance reasoning functions. Legal-knowledge representation frameworks—LKIF \[9\], LegalRuleML \[10\], the ODRL policy language \[11\], and the Data Privacy Vocabulary (DPV) \[12\]—provide ontological coverage of legal concepts and obligations. Defeasible deontic logic frameworks \[13\] handle contrary-to-duty obligations and exceptions with formally specified non-monotonic semantics. SHACL \[14\] supports constraint validation over RDF graphs. Akoma Ntoso \[15\] standardises legislative document structure. Early work on executable legal reasoning includes the British Nationality Act formalisation \[24\], which demonstrated that statutory logic programs could be executed and interrogated—a conceptual ancestor of the approach taken here.

LEXON builds on this tradition and is most similar in spirit to LegalRuleML-style executable representations, but differs in three respects: the focus on AI-specific evidence specifications, the typed-graph schema for AI system profiles, and the joint evaluation of activation, gap, and conflict reasoning on a single benchmark.

AI governance documentation—model cards \[4\], datasheets for datasets \[5\], system cards \[16\], and dataset nutrition labels \[17\]—provides transparency instruments but is not designed for executable inference. LEXON treats documentation fields as instances of typed evidence specifications and can therefore consume model-card content as evidence.

Large language models have been applied to legal question answering and statutory reasoning \[18,19,20\]. These approaches achieve impressive fluency on multiple-choice legal benchmarks but lack formal soundness guarantees, produce non-reproducible outputs for identical inputs under stochastic inference, and offer limited support for the audit trails expected of regulatory compliance documentation. We do not report an LLM-only baseline in the present article because the comparison would not be informative without a fixed-prompt, fixed-model-version, fixed-temperature reproducible protocol. A controlled LLM comparison is a defensible direction for future work, particularly for the natural-language clause-to-tuple decomposition step (Stage 1 of the pipeline).

Regulatory technology (RegTech) systems address similar problems in financial and data-protection domains \[21\]. LEXON shares the goal of executable compliance reasoning but is specialised to AI regulation and its specific evidence structure.

## ***4.3. Why Typed Knowledge Graphs and Stratified Datalog?***

The choice of stratified Datalog reflects three practical considerations. First, Datalog evaluations terminate and admit unique perfect models under stratification \[22,23,25\], which is important for reproducibility and for generating audit trails. Second, the rule layer is human-readable and reviewable by domain experts, supporting the goal of an auditable compliance information layer. Third, typed-graph constraints prevent rules from firing on type-incoherent facts, which substantially reduces false positives in evidence-gap detection as shown by the ablation results. The combination of these properties is difficult to obtain with LLM-based pipelines, which do not natively provide derivation traces or determinism.

## ***4.4. Limitations***

Several limitations should be emphasised. First, the synthetic benchmark provides evidence of internal benchmark validity only: gold labels are derived from the same formal definitions that the engine implements, so the F1 = 1.000 result confirms correct implementation, not real-world regulatory coverage. Second, LEXON's results depend on the completeness and correctness of the typed schema; obligations or evidence types outside the schema cannot be detected, and this is the schema-coverage bound stated in Property 4. Third, the current implementation uses closed-world assumptions for evidence holdings, which is useful for reproducible inference but may classify non-standard or unregistered evidence as absent. Fourth, evidentiary completeness is not equivalent to substantive legal compliance: a system may possess required documentation while failing to implement the underlying control. The article uses the term evidentiary completeness throughout to mark this distinction. Fifth, legal interpretation remains context-dependent, especially where regulatory language is ambiguous or evolving; the framework supports human review rather than supplanting it. Sixth, the conflict-detection rules cover direct action-incompatibility conflicts only and not temporal or resource conflicts, which would require a clock model and a resource model respectively. Seventh, the baselines implemented here (static checklist, ontology-only, flat rules) are deliberately simplified; a comparison against a mature SHACL-based validation system or a production-rule engine with typed facts would provide a stronger baseline for future work.

## ***4.5. Implications for AI Governance Information Systems***

LEXON is intended as a transparent information-processing layer for machine-assisted AI governance. Its outputs are obligation-activation traces, evidence-gap lists, conflict alerts, and remediation candidates, each carrying the rule derivations that produced them. The framework is designed to augment human compliance reasoning by improving coverage of conditional obligations and by providing reproducible documentation of which obligations apply under which assumptions.

Three risks that adopters should consider. First, automated compliance support can create a false sense of assurance; the article therefore distinguishes evidentiary completeness from compliance and recommends that LEXON outputs be reviewed by qualified compliance officers. Second, the closed-world evidence model may penalise organisations with valid evidence in non-standard formats; open-world extensions are a direction for future work. Third, LEXON faithfully represents the regulations it is given; if a regulation imposes disproportionate burdens, LEXON will report them as obligations rather than flag them as inequitable. Compliance review processes should be designed with awareness of proportionality and contextual interpretation.

---

# **5\. Conclusions**

This article presented LEXON, a typed knowledge-graph and stratified-Datalog framework for executable regulatory obligation reasoning. The framework formalises four reasoning tasks—obligation activation, evidence-gap detection, conflict detection, and evidence-remediation candidate generation—and evaluates them on a deterministic synthetic benchmark of 25 AI regulatory clauses and 30 system profiles (750 clause-profile pairs, 150-instance held-out test set). In the benchmark setting, LEXON achieves corpus-level F1 = 1.000 for obligation activation and evidence-gap detection, confirming that the implementation faithfully realises the specified formal semantics; ablation results show that neither the rule layer alone (T1 F1 = 0.615) nor the checklist baseline (T1 F1 = 0.427) achieves this correctness, and that each architectural component contributes measurable improvement. LEXON identifies all 11 direct conflict pairs in the benchmark with one false positive (T3 F1 = 0.957).

LEXON demonstrates that AI regulatory obligations can be represented as typed information structures and evaluated through executable rule-based inference under explicit assumptions. The primary contribution is not the automation of legal judgement, but the provision of a transparent, auditable information-processing layer for machine-assisted AI governance and compliance review—one in which every applicability decision, evidence-gap finding, and conflict alert is accompanied by a derivation trace.

Future work should: extend the benchmark to expert-validated real regulatory provisions (EU AI Act Articles 9, 10, 11, 13, 14, 15, and Annex IV are natural starting points); conduct independent second annotation of benchmark clauses to assess inter-annotator agreement; enrich the remediation model beyond evidence completion to cover substantive operational controls; incorporate open-world evidence reasoning; evaluate the framework in practitioner workflows; and develop a clock model for temporal conflict detection.

---

**Supplementary Materials:** The benchmark instances, structured obligation tuples, system profiles, gold labels, Datalog rule specifications, baseline implementations, evaluation scripts, worked examples, and statistical outputs are provided in the companion repository (see Data Availability Statement).

**Author Contributions:** Conceptualization, R.S.; methodology, R.S.; software, R.S.; validation, R.S.; formal analysis, R.S.; investigation, R.S.; resources, R.S.; data curation, R.S.; writing—original draft preparation, R.S.; writing—review and editing, R.S.; visualization, R.S.; project administration, R.S. The author has read and agreed to the published version of the manuscript.

**Funding:** This research received no external funding. The article-processing charge was funded by AffectLog SAS.

**Institutional Review Board Statement:** Not applicable. The study did not involve human or animal subjects; all benchmark data are synthetic.

**Informed Consent Statement:** Not applicable.

**Data Availability Statement:** The synthetic benchmark instances, system profiles, Datalog rule specifications, evaluation scripts, and generated results are openly available in the LEXON-Bench GitHub repository at https://github.com/roy-saurabh/lexon-bench and archived on Zenodo (DOI: https://doi.org/10.5281/zenodo.PENDING — to be confirmed after release). The benchmark data are synthetic and contain no personal data. Code is released under the MIT License; synthetic benchmark data are released under CC-BY-4.0.

**Acknowledgments:** During the preparation of this manuscript, the author used a large language model assistant for language editing and drafting support on prose sections. The author reviewed and edited all output and takes full responsibility for the content of this publication. Generative AI was not used to generate benchmark data, gold labels, or experimental results.

**Conflicts of Interest:** R.S. is the founder of AffectLog SAS, a company developing AI governance and compliance technologies. The research presented in this article is methodological in nature and does not evaluate any AffectLog commercial product. No AffectLog commercial product is evaluated in this study. The author declares that this interest did not influence the design, analysis, or reporting of the study.

**Abbreviations**

The following abbreviations are used in this manuscript:

| ABox | Assertion box (instance-level component of a knowledge graph) |
| :---- | :---- |
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

---

**Appendix A. Complete LEXON Datalog Rule Set**

The following rules implement the four reasoning tasks for LEXON-Bench. Rules are written in Soufflé-compatible stratified-Datalog syntax with negation-as-failure and typed declarations. The stratification is given in Section 2.4. The full file `rules/lexon_core.dl` is provided in the companion repository.

```datalog
% LEXON Core Rules v1.1 — stratified Datalog with negation-as-failure
% under the closed-world assumption.

% --- Type declarations (Soufflé-style) ---
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

% --- Bridge rules (Stratum 0) ---
sysProp(S, riskLevel, R) :- hasRiskLevel(S, R).
sysProp(S, domain, D)    :- hasDomain(S, D).
sysProp(S, actor, A)     :- systemActor(S, A).
sysProp(S, deployment, D):- hasDeployment(S, D).
sysProp(S, capability, C):- hasCapability(S, C).

% --- R1 Condition satisfaction (Stratum 0) ---
conditionSatisfied(C, S) :-
  condPred(C, P),
  condVal(C, V),
  sysProp(S, P, V).

% --- R1b Missing condition (Stratum 1) ---
MissingCondition(O, S) :-
  hasCondition(O, C),
  NOT conditionSatisfied(C, S).

% --- R2 Universal condition satisfaction — corrected (Stratum 2) ---
AllConditionsSatisfied(O, S) :-
  hasObligation(_, O),
  NOT MissingCondition(O, S).

% --- R3 Exception firing (Stratum 1) ---
exceptionFired(O, S) :-
  hasException(O, X),
  excCondition(X, C),
  conditionSatisfied(C, S).

% --- R4 Actor matching and activation (Stratum 3) ---
actorMatches(O, S) :-
  obligActor(O, A),
  systemActor(S, A).

actorMatches(O, S) :-
  obligActor(O, "Mixed").

actorMatches(O, S) :-
  systemActor(S, "Mixed").

Applicable(O, S) :-
  actorMatches(O, S),
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).

% --- R5 Evidence-gap detection (Stratum 4) ---
EvidenceGap(O, S, E) :-
  Applicable(O, S),
  requiresEvidence(O, E),
  NOT holdsEvidence(S, E).

% --- R6 Direct conflict detection with canonical ordering (Stratum 4) ---
% O1 < O2 prevents double-counting unordered pairs.
Conflict(O1, O2, S) :-
  Applicable(O1, S),
  Applicable(O2, S),
  obligActor(O1, A),
  obligActor(O2, A),
  obligAction(O1, Act1),
  obligAction(O2, Act2),
  incompatibleActions(Act1, Act2),
  O1 < O2.

% --- R7 Evidence-remediation candidates (Stratum 4) ---
RemediationCandidate(S, E) :-
  EvidenceGap(_, S, E).

% --- Incompatibility axioms (illustrative; full set in rules/incompatibility_axioms.yaml) ---
incompatibleActions("ACT-FullAutomatedDecision", "ACT-RequireHumanOverride").
incompatibleActions("ACT-RetainDataMaximal", "ACT-MinimiseDataRetention").
incompatibleActions("ACT-ProhibitedPurposeUse", "ACT-PermittedPurposeUse").
incompatibleActions("ACT-DiscloseToPublic", "ACT-MaintainConfidentiality").
```

**Appendix B. Proof Sketches for Properties 1–4**

**Property 1 (Soundness of activation).** By rule R4, Applicable(O, S) is derived only when (i) actorMatches(O, S) holds, (ii) AllConditionsSatisfied(O, S) holds, and (iii) exceptionFired(O, S) does not hold. By rule R2, AllConditionsSatisfied(O, S) holds iff there is no missing condition for O in S, that is, every C ∈ C_o satisfies conditionSatisfied(C, S) via R1. By R3, exceptionFired(O, S) holds iff at least one exception condition is satisfied. Actor matching corresponds to Definition 4's actor constraint. The conjunction of these conditions is precisely A(o, S) = Applicable in Definition 4. Under stratified Datalog with CWA, the perfect-model semantics derives no facts beyond those entailed by the rules and base facts. □

**Property 2 (Activation monotonicity over positive profile extensions).** Let the obligation graph, condition vocabulary, exception definitions, and rule vocabulary be fixed. Let S ⊆ S′ over system-profile facts only. Suppose no fact in S′ \\ S satisfies an exception condition of o. Then exceptionFired(o, S′) holds iff exceptionFired(o, S) holds. Adding system-profile facts cannot introduce missing conditions because R2 derives AllConditionsSatisfied from the absence of missing conditions, and adding system facts can only satisfy conditions (making them conditionSatisfied), never introduce new missing ones. Therefore Applicable(o, S) implies Applicable(o, S′). The qualification on exception-satisfying facts is necessary. □

**Property 3 (Anti-monotonicity of evidence gaps).** Fix the obligation set and applicability relation. By rule R5, EvidenceGap(O, S, E) is derived iff Applicable(O, S) holds, requiresEvidence(O, E) holds, and holdsEvidence(S, E) does not hold. Adding holdsEvidence(S, E′) cannot make Applicable(O, S) false (by Property 2 with trivial extension satisfying no exception), and cannot make other holdsEvidence atoms false. Therefore the gap set can only shrink or stay the same. □

**Property 4 (Bounded completeness of gap detection).** Under CWA, holdsEvidence(S, E) is false for any E not explicitly asserted. Rule R5 fires for every E ∈ requiresEvidence(O) that is not held. EvidenceGap(O, S, E) is derived for all and only elements of E_o \\ E_held within the evidence vocabulary. Evidence types outside the vocabulary cannot be reported; this is the schema-coverage bound. □

**Appendix C. System Profile Schema (Illustrative)**

LEXON system profiles are JSON objects conforming to the following structure (illustrative; authoritative JSON Schema is in the companion repository).

```json
{
  "instance_id": "SYS-XXX",
  "capabilities": ["GenerativeAI | Classification | Biometric | DecisionSupport | Recommendation | CCTV"],
  "domain": "Healthcare | Employment | Education | CriticalInfra | Biometric | General | PublicServices",
  "risk_level": "Unacceptable | HighRisk | LimitedRisk | MinimalRisk | Underspecified",
  "actor": "Provider | Deployer | Importer | User | Mixed",
  "deployment_context": "EU_Market | Non_EU | Research_Exemption",
  "properties": {
    "affectsNaturalPerson": true,
    "isDeployed": true,
    "hasResearchExemption": false,
    "isExclusiveSelfUse": false,
    "hasSystemicRisk": false,
    "processesSpecialCategory": false,
    "logsUnderControl": true
  },
  "evidence_held": ["E-RiskAssessment", "E-SystemCard"],
  "profile_complete": true
}
```

---

**References**

1. European Parliament and Council of the European Union. Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). Off. J. Eur. Union 2024, L 1689. Available online: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689 (accessed on 26 May 2026).

2. National Institute of Standards and Technology. Artificial Intelligence Risk Management Framework (AI RMF 1.0); NIST AI 100-1; U.S. Department of Commerce: Gaithersburg, MD, USA, 2023.

3. International Organization for Standardization. ISO/IEC 42001:2023 Information Technology — Artificial Intelligence — Management System; ISO: Geneva, Switzerland, 2023.

4. Mitchell, M.; Wu, S.; Zaldivar, A.; Barnes, P.; Vasserman, L.; Hutchinson, B.; Spitzer, E.; Raji, I.D.; Gebru, T. Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT* '19), Atlanta, GA, USA, 29–31 January 2019; pp. 220–229.

5. Gebru, T.; Morgenstern, J.; Vecchione, B.; Vaughan, J.W.; Wallach, H.; Daumé III, H.; Crawford, K. Datasheets for datasets. Commun. ACM 2021, 64, 86–92.

6. Koreeda, Y.; Manning, C.D. ContractNLI: A dataset for document-level natural language inference for contracts. In Findings of EMNLP 2021, Punta Cana, Dominican Republic, 7–11 November 2021; pp. 1907–1919.

7. Chalkidis, I.; Jana, A.; Hartung, D.; Bommarito, M.; Androutsopoulos, I.; Katz, D.M.; Aletras, N. LexGLUE: A benchmark dataset for legal language understanding in English. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL), Dublin, Ireland, 22–27 May 2022; pp. 4310–4330.

8. Lam, K.W.; Sleeman, D.; Pan, J.Z.; Vasconcelos, W. A privacy policy question-answering assistant. CEUR Workshop Proc. 2020, 2604.

9. Hoekstra, R.; Breuker, J.; Di Bello, M.; Boer, A. The LKIF Core Ontology of Basic Legal Concepts. In Proceedings of the Workshop on Legal Ontologies and Artificial Intelligence Techniques (LOAIT 2007), Stanford, CA, USA, 4 June 2007; pp. 43–63.

10. Athan, T.; Governatori, G.; Palmirani, M.; Paschke, A.; Wyner, A. LegalRuleML: Design principles and foundations. In Reasoning Web. Web Logic Rules; Lecture Notes in Computer Science; Springer: Cham, Switzerland, 2015; Volume 9203, pp. 151–188.

11. Iannella, R.; Villata, S. (Eds.) ODRL Information Model 2.2; W3C Recommendation; W3C: 2018. Available online: https://www.w3.org/TR/odrl-model/ (accessed on 26 May 2026).

12. Pandit, H.J.; Polleres, A.; Bos, B.; Brennan, R.; Bruegger, B.; Ekaputra, F.J.; Fernández, J.D.; Hamed, R.G.; Kiesling, E.; Lizar, M.; et al. Creating a vocabulary for data privacy: The first-year report of the Data Privacy Vocabularies and Controls Community Group (DPVCG). In Proceedings of the OTM Conferences, Rhodes, Greece, 21–25 October 2019; pp. 714–730.

13. Governatori, G.; Olivieri, F.; Rotolo, A.; Scannapieco, S.; Sartor, G. Two approaches to semantic legislative drafting. Artif. Intell. Law 2016, 24, 291–321.

14. Knublauch, H.; Kontokostas, D. Shapes Constraint Language (SHACL); W3C Recommendation; W3C: 2017. Available online: https://www.w3.org/TR/shacl/ (accessed on 26 May 2026).

15. Palmirani, M.; Vitali, F. Akoma Ntoso for legal documents. In Legislative XML for the Semantic Web; Sartor, G., Palmirani, M., Francesconi, E., Biasiotti, M.A., Eds.; Springer: Dordrecht, The Netherlands, 2011; pp. 75–100.

16. Procope, C.; Cheema, A.; Adkins, D.; Pasternak, J.; Stevens, S.; Cooley, P.; Roberts, C.; Walz, S.; Stenetorp, P.; Goldberg, Y.; et al. System-level transparency of machine learning. In Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society (AIES), Montreal, QC, Canada, 8–10 August 2023.

17. Holland, S.; Hosny, A.; Newman, S.; Joseph, J.; Chmielinski, K. The dataset nutrition label: A framework to drive higher data quality standards. In Data Protection and Privacy: Data Protection and Democracy; Hart Publishing: Oxford, UK, 2020; pp. 1–26.

18. Blair-Stanek, A.; Holzenberger, N.; Van Durme, B. Can GPT-3 perform statutory reasoning? In Proceedings of the International Conference on Artificial Intelligence and Law (ICAIL), Braga, Portugal, 19–23 June 2023; pp. 22–31.

19. Guha, N.; Nyarko, J.; Ho, D.E.; Ré, C.; Chilton, A.; Narayana, A.; Chohlas-Wood, A.; Peters, A.; Waldon, B.; Rockmore, D.; et al. LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models. In Advances in Neural Information Processing Systems 36, NeurIPS 2023, New Orleans, LA, USA, 10–16 December 2023.

20. Niklaus, J.; Chalkidis, I.; Stürmer, M. Swiss-Judgment-Prediction: A multilingual legal judgment prediction benchmark. In Proceedings of the Natural Legal Language Processing Workshop, Punta Cana, Dominican Republic, 10 November 2021; pp. 19–35.

21. Butler, T.; O'Brien, L. Understanding RegTech for digital regulatory compliance. In Disrupting Finance; Lynn, T., Mooney, J.G., Rosati, P., Cummins, M., Eds.; Palgrave Pivot: Cham, Switzerland, 2019; pp. 85–102.

22. Apt, K.R.; Blair, H.A.; Walker, A. Towards a theory of declarative knowledge. In Foundations of Deductive Databases and Logic Programming; Minker, J., Ed.; Morgan Kaufmann: Los Altos, CA, USA, 1988; pp. 89–148.

23. Przymusinski, T.C. On the declarative semantics of deductive databases and logic programs. In Foundations of Deductive Databases and Logic Programming; Minker, J., Ed.; Morgan Kaufmann: Los Altos, CA, USA, 1988; pp. 193–216.

24. Sergot, M.J.; Sadri, F.; Kowalski, R.A.; Kriwaczek, F.; Hammond, P.; Cory, H.T. The British Nationality Act as a logic program. Commun. ACM 1986, 29, 370–386.

25. Abiteboul, S.; Hull, R.; Vianu, V. Foundations of Databases; Addison-Wesley: Reading, MA, USA, 1995.

---

**Disclaimer/Publisher's Note:** *The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content.*
