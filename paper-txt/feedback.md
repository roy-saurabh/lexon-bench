## MDPI reviewer-style verdict

**Recommendation: Major Revision before submission.**
If I were assigned as an MDPI *Information* reviewer today, I would not recommend acceptance in its present form. I would probably select **Major Revision**, with a warning that the paper should be rejected if the companion repository, benchmark data, scripts, and reported result tables cannot be produced exactly as claimed.

The revised manuscript is **substantially improved** compared with the earlier FAccT-oriented version: it now uses the MDPI article structure, removes most placeholder language, correctly reframes “compliance” as **evidentiary completeness**, includes a GenAI disclosure, discloses the AffectLog conflict of interest, and no longer reports an unexecuted LLM baseline. Those are important improvements. 

But there are still several submission-blocking problems:

1. **The reported results are not yet auditable.**
2. **The companion repository is claimed but not identified.**
3. **The formal semantics still have gaps, especially actor matching and uncertainty.**
4. **The evaluation remains synthetic and partly circular.**
5. **The statistical claims are underreported.**
6. **The Datalog appendix is not publication-ready.**
7. **Funding and data availability still contain placeholders.**
8. **Several references are weak, missing, or mismatched.**

MDPI’s data policy expects the data/code needed to reproduce central findings to be available or clearly restricted; MDPI explicitly recommends depositing data and code in a trusted repository, and data availability statements are required for MDPI articles. ([MDPI][1]) The current manuscript promises a companion repository and DOI but still contains `[DOI/URL—to be inserted on submission]`, which must be fixed before upload. 

---

# 1. Editorial decision I would give

**Decision:** Major Revision
**Confidence:** High
**Potential after revision:** Publishable in *Information*
**Submit as-is?** No.

The paper has a viable MDPI *Information* profile because it is now framed as an information-processing, knowledge-graph, and rule-inference system for AI governance. That is much more appropriate than the previous FAccT framing. However, the manuscript must not be submitted until the repository, data, result-generation scripts, and exact statistical outputs exist.

A very direct reviewer summary would be:

> The manuscript proposes a typed knowledge-graph and stratified-Datalog framework for regulatory obligation reasoning in AI governance. The topic is timely and suitable for *Information*. The revised framing is careful in distinguishing evidentiary completeness from legal compliance. However, the paper currently relies on synthetic, internally generated benchmark labels, provides no visible repository DOI, reports statistical significance without p-values or confidence intervals in the manuscript, and leaves important details of the formal semantics underspecified. The article should undergo major revision before publication.

---

# 2. What is now strong

## 2.1 Scope is much better aligned with *Information*

The paper now treats AI regulatory compliance as an **information-structuring and reasoning problem**, not as an attempt to automate legal judgment. That is the correct move for *Information*. The introduction explicitly says LEXON evaluates evidentiary completeness and rule-derived applicability, not full legal validity. This significantly reduces legal overclaiming. 

## 2.2 The contribution statement is cleaner

The four contributions are now realistic:

1. formalizing obligation reasoning as an information-processing problem;
2. typed KG schema;
3. stratified-Datalog inference;
4. deterministic benchmark evaluation against implemented baselines.

This is much better than the earlier “first” and “placeholder discipline” language.

## 2.3 The LLM baseline issue has been handled correctly

The manuscript now says the LLM-only baseline is not reported because it was not executed under a reproducible protocol. That is the right decision. Keep this.

## 2.4 The GenAI and COI disclosures are appropriate

The disclosure that a large language model was used for prose drafting/editing, but not for gold labels or results, is good. MDPI requires transparency around materials and publication ethics, and this disclosure is safer than silence. MDPI also notes that its manuscripts undergo editorial pre-check and peer review, so visible disclosure and reproducibility issues can matter early. ([MDPI][2])

The COI statement disclosing AffectLog is also appropriate and should remain.

---

# 3. Submission-blocking problems

## 3.1 The repository claim is currently unsupported

The manuscript says:

> “The benchmark generation scripts, structured obligation tuples, system profiles, gold labels, rule specifications, baseline implementations, and evaluation scripts are provided in the companion repository.”

But the Data Availability Statement still says:

> `[DOI/URL—to be inserted on submission]`.

That is not acceptable for submission. It creates a direct contradiction: the manuscript reports numerical results, says all tables are reproducible, but gives no repository. MDPI can ask for raw data and code during review, and its policy recommends public deposition of data/code needed to support central findings. ([MDPI][1])

**Required fix before submission:**

Create a Zenodo archive or GitHub repository with:

* benchmark instances;
* structured clause tuples;
* system profiles;
* gold labels;
* rule files;
* baseline implementations;
* evaluation scripts;
* generated result tables;
* exact environment file;
* reproduction command.

Then replace:

> `[DOI/URL—to be inserted on submission]`

with the actual DOI or repository URL.

## 3.2 Funding statement still has a placeholder

The manuscript says:

> “The APC was funded by [AUTHOR/INSTITUTION].”

This is a visible placeholder. It must not be submitted.

Replace with one of:

> “This research received no external funding. The APC was funded by the author.”

or:

> “This research received no external funding. The APC was funded by AffectLog SAS.”

Given the COI disclosure, the second is acceptable if true, but it strengthens the need for the COI statement.

## 3.3 The results look too polished relative to the described evidence

The results are strong: T1 F1 = 0.92, T2 F1 = 0.95, all 11 conflicts detected, one false positive, significance after Bonferroni correction. But the manuscript does not show:

* test-set size per task;
* number of positives and negatives;
* confusion matrices;
* confidence intervals in the table;
* actual p-values;
* effect sizes;
* exact bootstrap procedure;
* exact train/dev/test composition;
* result-generation scripts.

This makes the results vulnerable to reviewer skepticism.

**Required fix:** Add a new table after Table 5:

| Task | Test instances | Positives | LEXON TP | FP | FN | Precision | Recall | F1 | 95% CI |
| ---- | -------------: | --------: | -------: | -: | -: | --------: | -----: | -: | -----: |

And a statistical comparison table:

| Comparison | Task | Test used | Statistic | p-value | Corrected α | Effect size |
| ---------- | ---- | --------- | --------: | ------: | ----------: | ----------: |

Do not simply say “statistically significant.” Report the values.

## 3.4 The synthetic benchmark remains the central weakness

The manuscript now acknowledges evaluative circularity, which is good. But the mitigation is not strong enough. Saying the benchmark is internally valid does not solve the problem that gold labels are derived from the same structured representation the system reasons over.

A critical reviewer would say:

> The benchmark evaluates whether the implementation reproduces the formal definitions, not whether the formal representation adequately captures real regulatory obligations.

This is not fatal for *Information*, but only if the paper is framed as a **reproducible systems benchmark**, not as a validated regulatory compliance method.

**Required fix:** Add at least one of the following before submission:

1. a small real-clause slice using EU AI Act Articles 9, 10, 11, 13, 14, 15, and Annex IV;
2. independent second annotation of 10–15 clauses;
3. an expert validation table;
4. manual error analysis with examples of actual clause/profile pairs;
5. release of the full benchmark so reviewers can inspect it.

At minimum, add **three worked benchmark examples** in the main paper, not only the appendix/repository.

---

# 4. Formal and technical issues

## 4.1 Actor matching is missing from the activation rule

This is the most serious remaining formal issue.

The introduction and definitions say applicability depends on actor role. Definition 2 includes `actor`, and the paper repeatedly states that obligations are actor-specific. But the core activation rule is:

```prolog
Applicable(O, S) :-
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).
```

There is no actor matching. The rule set includes actor comparison in conflict detection, but not in applicability. This means a Provider obligation could apply to a Deployer system if the other conditions are satisfied.

**Required fix:**

Add actor matching:

```prolog
actorMatches(O, S) :-
  obligActor(O, A),
  systemActor(S, A).

Applicable(O, S) :-
  actorMatches(O, S),
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).
```

Then update:

* Section 2.4;
* Appendix A;
* Property 1 proof;
* benchmark schema;
* error analysis.

Alternatively, explicitly state that actor is encoded as a required condition in `Cₒ`. But that would be less clean. I strongly recommend adding `actorMatches`.

## 4.2 Domain, risk, deployment, and capability relations are defined but not connected to condition satisfaction

The TBox defines relations such as:

* `hasCapability`
* `hasRiskLevel`
* `hasDomain`

But the Datalog condition satisfaction rule only uses:

```prolog
sysProp(S, P, V)
```

This leaves ambiguity: are risk level, domain, actor, deployment, and capability all reified into `sysProp`, or are they separate typed relations?

A reviewer will ask:

> If the typed KG has domain/range constraints, how exactly do typed relations flow into condition satisfaction?

**Required fix:** Add bridge rules:

```prolog
sysProp(S, riskLevel, R) :-
  hasRiskLevel(S, R).

sysProp(S, domain, D) :-
  hasDomain(S, D).

sysProp(S, capability, C) :-
  hasCapability(S, C).

sysProp(S, deployment, D) :-
  hasDeployment(S, D).

sysProp(S, actor, A) :-
  systemActor(S, A).
```

Or remove `sysProp` and use typed predicates directly.

## 4.3 The NotApplicable / Uncertain semantics are still underdeveloped

Definition 4 says:

* Applicable iff all conditions satisfied and no exception fires;
* NotApplicable iff an exception fires;
* otherwise Uncertain.

This is too conservative and arguably wrong. Suppose an obligation requires `risk = HighRisk`, and the system is explicitly `MinimalRisk`. That should be **NotApplicable**, not Uncertain.

Current Definition 4 does not distinguish:

* false condition;
* unknown condition;
* missing value;
* exception firing.

You need a three-valued condition semantics:

```text
sat(c, S) ∈ {true, false, unknown}
```

Then define:

```text
Applicable iff all required conditions are true and no exception is true.
NotApplicable iff at least one required condition is false OR at least one exception is true.
Uncertain iff no required condition is false, no exception is true, and at least one required condition is unknown.
```

This would be much more rigorous.

## 4.4 The Datalog rule currently conflates false and unknown

The rule:

```prolog
MissingCondition(O, S) :-
  hasCondition(O, C),
  NOT conditionSatisfied(C, S).
```

treats any unproven condition as missing. Under CWA, this means unknown and false collapse. But the paper claims to propagate uncertainty. There is no Datalog rule for `Uncertain(O,S)` in the current main rule set.

**Required fix:** Either remove uncertainty claims from the formal system, or implement them.

A better rule pattern:

```prolog
conditionFalse(C, S) :-
  condPred(C, P),
  condVal(C, V),
  sysProp(S, P, V2),
  V2 != V.

conditionUnknown(C, S) :-
  condPred(C, P),
  NOT hasKnownProp(S, P).

HasFalseCondition(O, S) :-
  hasCondition(O, C),
  conditionFalse(C, S).

HasUnknownCondition(O, S) :-
  hasCondition(O, C),
  conditionUnknown(C, S).

Applicable(O, S) :-
  actorMatches(O, S),
  NOT HasFalseCondition(O, S),
  NOT HasUnknownCondition(O, S),
  NOT exceptionFired(O, S).

NotApplicable(O, S) :-
  HasFalseCondition(O, S).

NotApplicable(O, S) :-
  exceptionFired(O, S).

Uncertain(O, S) :-
  actorMatches(O, S),
  NOT HasFalseCondition(O, S),
  HasUnknownCondition(O, S),
  NOT exceptionFired(O, S).
```

This would align the implementation with the stated theory.

## 4.5 Conflict detection will double-count symmetric pairs

The rule:

```prolog
Conflict(O1, O2, S) :-
  ...
  O1 != O2.
```

will derive both `(O1,O2)` and `(O2,O1)` unless canonical ordering is enforced. The manuscript claims 11 conflict pairs; it must state whether these are ordered or unordered.

**Required fix:**

Use canonical ordering:

```prolog
O1 < O2
```

or perform deduplication in post-processing and state it clearly.

## 4.6 Property 2 proof is still not precise enough

The proof says adding facts cannot introduce missing conditions. This is true only if the set of obligation-condition facts is fixed. If new `hasCondition` facts are added, missing conditions can be introduced.

Revise Property 2 to say:

> Let the obligation graph, condition vocabulary, exception definitions, and rule vocabulary be fixed. Let S ⊆ S′ only over system-profile facts.

This restriction is necessary.

## 4.7 The “unique perfect model” claim needs references

The paper states that stratification ensures a unique perfect model. This is a technical claim and needs foundational references. Add citations to:

* Apt, Blair, and Walker on stratified logic programs;
* Przymusinski on perfect model semantics;
* Ullman or Abiteboul/Hull/Vianu for Datalog foundations;
* Soufflé if the implementation uses Soufflé.

Right now, the paper lacks core Datalog references, which is a major weakness for a paper centered on Datalog.

---

# 5. Evaluation critique

## 5.1 Table 5 says CIs are in the repository, but they should be in the paper

Table 5 reports only point estimates. The caption says confidence intervals are in the companion repository. That is not enough.

For MDPI, the main paper should include the CIs if the text claims bootstrap inference. Add CIs directly:

| System | T1 P | T1 R | T1 F1 [95% CI] | T2 P | T2 R | T2 F1 [95% CI] |
| ------ | ---: | ---: | -------------: | ---: | ---: | -------------: |

## 5.2 Statistical tests are claimed but not reported

The text says differences were statistically significant at corrected α = 0.0125. But it gives no p-values or test statistics.

Add:

* McNemar χ² or exact binomial statistic;
* p-values;
* corrected threshold;
* effect sizes.

Also explain why paired t-tests are appropriate for per-instance F1. If gap-set F1 is bounded and non-normal, a Wilcoxon signed-rank test or bootstrap paired difference may be safer.

## 5.3 “7 of 100 T1 errors” is unclear

The Results say:

> “The 7 of 100 T1 errors observed by LEXON on the test split…”

But the benchmark has 750 clause-profile pairs, and the test split should be 20%, i.e. 150 pairs. Why 100? Is this the number of T1-labeled instances? Is it balanced? Was it sampled?

Clarify:

* number of T1 test instances;
* number of positive applicable obligations;
* number of negative/non-applicable obligations;
* whether “100” is the T1 subset;
* how multi-obligation clauses are counted.

## 5.4 Ambiguity sensitivity is tautological unless independently validated

The manuscript says:

> “The ambiguity flag correctly identifies all eight clauses on which human review is recommended.”

But the ambiguity flag appears to be assigned by the benchmark designers. If so, this is not a prediction; it is a label.

Rephrase:

> “All eight clauses marked as ambiguous by the benchmark construction protocol were routed to human-review status by design.”

Or add an independent test:

* annotator labels ambiguous clauses;
* system predicts uncertainty;
* compare system uncertainty to annotator ambiguity labels.

## 5.5 Conflict detection evaluation is too small

The benchmark has only 11 conflict pairs. That is very small. It is acceptable as a preliminary result, but the paper should be careful.

Add:

> “Because the conflict subset contains only 11 gold pairs, the T3 result should be interpreted as a functional validation of the direct-conflict rule rather than as a robust estimate of general conflict-detection performance.”

## 5.6 Baselines may be strawman baselines

The baselines are useful, but they are weak:

* Static checklist is intentionally simplistic.
* Ontology-only cannot infer by design.
* Flat rules are intentionally untyped.

This makes LEXON’s superiority predictable. Add a stronger baseline if possible:

1. SHACL validation baseline;
2. SPARQL query baseline over RDF graph;
3. Drools / production-rule baseline with typed facts;
4. LegalRuleML-style representation baseline;
5. RDFLib + hand-authored SPARQL rules.

If no stronger baseline is added, soften the claim:

> “LEXON outperforms deliberately simplified ablation baselines.”

Do not imply it outperforms mature compliance systems.

---

# 6. Presentation and formatting review

I rendered the DOCX and reviewed the layout. It produces **17 pages**, **no figures**, and **six tables**. The layout is much cleaner than the previous version, but still not publication-ready.

## 6.1 No figure or graphical architecture

The manuscript has no inline figures. For a systems paper in *Information*, this is a weakness.

Add at least one figure:

**Figure 1. LEXON information pipeline**

```text
Regulatory clause
   ↓
Obligation tuple extraction
   ↓
Typed knowledge graph
   ↓
Stratified-Datalog inference
   ↓
Applicability / evidence gaps / conflicts / remediation candidates
   ↓
Auditable report
```

Optionally add:

**Figure 2. Typed schema fragment**

Clause → Obligation → Condition / Exception / EvidenceSpec
SystemProfile → Actor / RiskLevel / Domain / EvidenceHeld

## 6.2 Appendix code formatting is weak

Appendix A is rendered as proportional text, not code. The Datalog rules are difficult to read. Use:

* monospace font;
* smaller size;
* shaded code block or table;
* no full justification;
* consistent indentation.

Better: move the full rule set to Supplementary Materials and keep only the core rules in the main paper.

## 6.3 Appendix C JSON schema is poorly formatted

The schema spans pages awkwardly and is not valid JSON because it uses pipe-style alternatives inside strings. It is more of a pseudo-schema.

Rename it:

> “Illustrative profile schema”

Or provide a real JSON Schema Draft 2020-12 object in supplementary material.

## 6.4 Tables need captions and explanatory notes

MDPI tables should be independently understandable. Table 5 especially needs:

* test-set size;
* CI note;
* definition of P/R/F1;
* whether micro or macro averaging;
* whether results are per clause-profile pair or per obligation.

## 6.5 Final template artifacts

The manuscript includes the MDPI Publisher’s Note at the end. This is usually present in MDPI templates, but confirm whether the submission portal expects authors to leave it in. It is not harmful, but do not manually modify it.

---

# 7. Section-by-section reviewer comments

## Title

Current:

> LEXON: Executable AI Regulatory Obligation Reasoning with Typed Knowledge Graphs and Stratified Datalog

Good. Keep it.

Possible improvement:

> LEXON: Executable Evidence-Gap Reasoning for AI Regulatory Obligations Using Typed Knowledge Graphs and Stratified Datalog

This would be more precise but less elegant. I would keep the current title.

## Abstract

The abstract is good and within normal MDPI length. However, it currently says:

> “The results show…”

This is acceptable only if the repository and results are reproducible. If not, soften:

> “In a controlled synthetic benchmark, the results indicate…”

Suggested revision:

> “In a controlled synthetic benchmark, combining typed graph structure with rule-based inference improved obligation activation and evidence-gap detection relative to implemented checklist, ontology-only, and flat-rule baselines.”

## Introduction

Strong, but two claims need softening:

Current:

> “no human reviewer reliably tracks every conditional obligation…”

This is rhetorically strong and unsupported. Replace with:

> “manual review can make it difficult to track conditional obligations consistently across intersecting instruments…”

Current:

> “conflicts … frequently go undetected until enforcement.”

This needs evidence. Replace with:

> “conflicts may remain difficult to detect without explicit cross-obligation reasoning.”

## Research Questions

RQ4 is not really an empirical research question. It is more of a conceptual framing question.

Revise RQ4:

> RQ4. What limitations arise from closed-world evidence assumptions, synthetic benchmark construction, and the distinction between evidentiary completeness and substantive legal compliance?

## Definitions

Definition 4 must be revised as discussed above.

Definition 5 is good, but it should perhaps return:

```text
EvidenceComplete, EvidenceIncomplete, EvidenceNotApplicable, EvidenceUncertain
```

Currently, if an obligation is not applicable, EC returns EvidenceIncomplete. That is conceptually wrong. A non-applicable obligation should not be evidence-incomplete.

Revise:

```text
EC(o,S,Eheld) =
  EvidenceComplete if A(o,S)=Applicable and Eo⊆Eheld
  EvidenceIncomplete if A(o,S)=Applicable and Eo⊄Eheld
  EvidenceNotRequired if A(o,S)=NotApplicable
  EvidenceUncertain if A(o,S)=Uncertain
```

This is a major conceptual fix.

## Rule Layer

Needs actor matching, three-valued condition handling, and typed relation bridge rules.

## Formal Properties

Good improvement, but still under-cited. Add Datalog/logic-programming references.

## Benchmark Construction

Good honesty about circularity. But the mitigation is insufficient. Add worked examples and/or a real-clause slice.

## Baselines

The exclusion of LLM baseline is appropriate. But the baselines are weak. Add one stronger symbolic baseline if possible.

## Results

Too compressed. Add CIs, p-values, confusion matrices, denominators, and exact test sizes.

## Discussion

This is now one of the stronger sections. The limitations are credible and should remain.

## Conclusion

Good, but remove repeated language. The first and second paragraphs partially duplicate each other. Condense by 20–25%.

## Back Matter

Fix funding and data availability placeholders. Keep GenAI and COI disclosures.

---

# 8. Reference review

## 8.1 Missing essential references

Add Datalog / logic-programming foundations:

* Apt, Blair, and Walker, “Towards a Theory of Declarative Knowledge”
* Przymusinski, “On the declarative semantics of deductive databases and logic programs”
* Ullman, *Principles of Database and Knowledge-Base Systems*
* Abiteboul, Hull, and Vianu, *Foundations of Databases*
* Soufflé system paper if Soufflé is mentioned

Add executable law / computational legal reasoning:

* Sergot et al., British Nationality Act as a logic program
* Bench-Capon on legal knowledge representation
* Prakken and Sartor on legal argumentation
* Ashley, *Artificial Intelligence and Legal Analytics*
* Gordon / Carneades if argumentation is discussed

Add legal-rule representation:

* LegalRuleML core paper already present, good.
* LKIF already present, good.
* Add RuleML / legal compliance checking if possible.
* Add SHACL validation in relation to KG constraints, already present, good.

## 8.2 Mismatched citation

The text says:

> “system cards [16], and AI cards [17]…”

But reference [17] is the Dataset Nutrition Label, not AI cards. That is a mismatch.

Fix by either:

* changing the sentence to “system cards and dataset nutrition labels”; or
* replacing [17] with a genuine AI cards reference.

## 8.3 EU AI Act citation needs URL/access date

Add official URL and access date. The current entry is too sparse for MDPI.

## 8.4 Reference [8] is incomplete

Lam et al. CEUR entry needs:

* volume number;
* workshop/conference title;
* page/article number if available;
* URL if available.

## 8.5 Reference [16] needs verification

“System-level transparency of machine learning” should be verified. Ensure the title, authors, proceedings, and page numbers are real and exact.

---

# 9. Ethical, legal, and conflict-of-interest review

The COI statement is appropriate but could be stronger:

Current:

> “R.S. is the founder of AffectLog SAS, a company developing AI governance and compliance technologies.”

Good. Add:

> “No AffectLog commercial product is evaluated in this study.”

You already say something similar. Keep it.

The GenAI statement is good but creates an obligation: if LLMs were used for drafting, ensure the manuscript does not contain fabricated references or unsupported claims. Reviewers are increasingly sensitive to this.

The IRB statement is fine only if no human annotators outside the author were involved. But the Methods mention “human-assisted extraction protocol.” If this involved only the author, fine. If it involved any other annotators, experts, or contributors, reconsider whether an ethics/consent statement is needed.

---

# 10. Specific text changes to make before submission

## Replace Definition 4

Use:

> Definition 4 (Applicability). Let sat(c,S) ∈ {true, false, unknown}. A(o,S)=Applicable iff every c ∈ Cₒ satisfies sat(c,S)=true and no exception x ∈ Xₒ satisfies sat(x,S)=true. A(o,S)=NotApplicable iff at least one required condition c ∈ Cₒ satisfies sat(c,S)=false or at least one exception x ∈ Xₒ satisfies sat(x,S)=true. A(o,S)=Uncertain iff no required condition is false, no exception is true, and at least one required condition is unknown.

## Replace Definition 5

Use:

> EC(o,S,Eheld)=EvidenceComplete iff A(o,S)=Applicable and Eₒ⊆Eheld; EvidenceIncomplete iff A(o,S)=Applicable and Eₒ⊄Eheld; EvidenceNotRequired iff A(o,S)=NotApplicable; EvidenceUncertain iff A(o,S)=Uncertain.

## Replace activation rule

Use:

```prolog
actorMatches(O, S) :-
  obligActor(O, A),
  systemActor(S, A).

Applicable(O, S) :-
  actorMatches(O, S),
  AllConditionsSatisfied(O, S),
  NOT exceptionFired(O, S).
```

## Add canonical conflict ordering

Use:

```prolog
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

## Replace ambiguity claim

Current:

> “The ambiguity flag correctly identifies all eight clauses…”

Replace with:

> “All eight clauses marked as ambiguous by the benchmark construction protocol were routed to human-review status. Because ambiguity labels are assigned during benchmark construction, this result should be interpreted as a functional check of the routing mechanism rather than as independent ambiguity-detection performance.”

## Replace statistical claim

Current:

> “The pairwise McNemar tests… indicated…”

Replace with exact values or write:

> “The statistical comparison scripts are provided in the repository. We report p-values, effect sizes, and bootstrap confidence intervals in Table X.”

Then add Table X.

---

# 11. Must-fix checklist before upload

Do not submit until every item below is complete:

* [ ] Replace `[AUTHOR/INSTITUTION]`.
* [ ] Replace `[DOI/URL—to be inserted on submission]`.
* [ ] Create and test the companion repository.
* [ ] Add actual CIs to Table 5.
* [ ] Add p-values and effect sizes.
* [ ] Add test-set denominators and confusion counts.
* [ ] Add actor matching to Datalog rules.
* [ ] Add three-valued condition semantics or remove uncertainty claims.
* [ ] Fix EC so non-applicable obligations are not labelled evidence-incomplete.
* [ ] Add bridge rules between typed KG relations and condition satisfaction.
* [ ] Deduplicate conflict pairs.
* [ ] Add at least one figure.
* [ ] Reformat Appendix A as code or move to supplement.
* [ ] Fix JSON schema formatting.
* [ ] Verify references [8], [16], [17].
* [ ] Add Datalog/logic-programming references.
* [ ] Add executable law references.
* [ ] Clarify whether any human annotation occurred.
* [ ] Remove or soften unsupported claims about manual review failure and conflict frequency.
* [ ] Add three worked benchmark examples.
* [ ] Ensure all manuscript claims are reproduced by the repository.

---

# 12. Final recommendation

The revised LEXON manuscript is now **directionally suitable for MDPI *Information***, but it should not yet be submitted. It is one strong revision away from being credible.

The highest-impact fixes are:

1. **publish the companion repo and DOI;**
2. **fix actor matching and uncertainty semantics;**
3. **add full statistical reporting;**
4. **add at least a small real-clause or worked-example validation;**
5. **remove all remaining placeholders;**
6. **strengthen Datalog and AI & Law references.**

With those corrections, I would expect a fair MDPI reviewer to treat it as a serious, publishable information-systems contribution rather than as a synthetic compliance demo.

[1]: https://www.mdpi.com/ethics?utm_source=chatgpt.com "Research and Publication Ethics"
[2]: https://www.mdpi.com/authors?utm_source=chatgpt.com "Information for Authors"
