# Paper Writing

## Contents

1. Establish the writing contract
2. Build a claim-led paper plan
3. Calibrate the paper to the contribution
4. Draft from verified evidence
5. Write each manuscript component
6. Handle citations and related work
7. Build tables, figures, and appendices
8. Check current venue requirements
9. Revise and audit the manuscript
10. Deliver the artifact

## 1. Establish the writing contract

Inspect the manuscript, proposal, experiment plan, code, result artifacts, claim ledger, and decisions before drafting. Determine whether the task is outlining, drafting, revising, shortening, formatting, or preparing a submission package.

Record:

- The primary contribution type and methodology.
- The intended audience and current target venue, if any.
- The allowed source and result horizon.
- The requested artifact and editable files.
- The authors' established terminology and style.
- The anonymity, confidentiality, authorship, disclosure, and submission constraints.
- The sections or claims that must remain unchanged.

Do not infer authorization to submit, upload, disclose, add authors, remove authors, accept licenses, or make public releases. Treat those as separate external actions requiring explicit authority.

## 2. Build a claim-led paper plan

Construct a claim map before polishing prose. Assign a stable claim ID to every central contribution, empirical conclusion, theoretical result, dataset property, and practical implication.

For each claim, record:

| Field | Required content |
|---|---|
| Claim ID | Stable identifier such as CLM-001 |
| Exact claim | One scoped, testable or defensible statement |
| Claim type | Contextual, novelty, theoretical, empirical, causal, descriptive, or normative |
| Evidence | Source, proof, run, analysis, table, or figure IDs |
| Lifecycle state | Proposed, analyzed, verified, reported, dropped, or another controlled truth state |
| Evidential status | Not assessed, insufficient, supported, mixed, or contradicted |
| Scope | Population, task, dataset, model, workload, setting, and time horizon |
| Caveat | Known limitation, assumption, uncertainty, or rival explanation |
| Destination | Abstract, introduction, results, discussion, or conclusion |

Require a direct path from each major claim to eligible evidence. Mark gaps with [CITATION NEEDED], [EVIDENCE NEEDED], or [RESULT PENDING]. Do not replace a marker with plausible text.

Draft the abstract and conclusion from the same claim map. Prevent either section from strengthening a claim beyond the evidence presented in the body.

## 3. Calibrate the paper to the contribution

Match the narrative and burden of proof to the primary contribution:

- For a method, explain the mechanism and isolate the claimed improvement with fair comparisons.
- For a theory paper, state assumptions, propositions, proof scope, and counterexamples precisely.
- For an empirical finding, foreground sampling, measurement, uncertainty, rival explanations, and generalization limits.
- For a system, demonstrate end-to-end utility, realistic workloads, resource tradeoffs, and component necessity.
- For a dataset or benchmark, establish need, collection process, quality, representativeness, licensing, contamination controls, and maintenance.
- For a measurement contribution, establish construct validity, reliability, protocol sensitivity, and interpretability.
- For a human-centered study, report recruitment, consent, protocol, analysis, researcher position where relevant, and validity threats.
- For a survey or taxonomy, explain scope and synthesis method and provide insight beyond an annotated list.
- For a replication, distinguish faithful reproduction, deviations, and conditions under which findings agree or differ.
- For a negative result, show that the tested expectation was credible and the study was informative enough to interpret the null or failure.
- For a position paper, make the thesis, assumptions, counterarguments, and implications explicit.

Do not manufacture an experimental section for self-contained theory, demand novelty from a replication, or frame a negative result as a failed positive-results paper.

## 4. Draft from verified evidence

Use the research truth states from the project dossier. Report a scientific result assertively only when its raw output, analysis path, configuration, and claim relation can be traced. Label preliminary, pilot, exploratory, or unverified evidence accurately.

Apply these rules:

1. Preserve the distinction between planned, implemented, executed, analyzed, verified, and reported.
2. Generate quantitative statements from traceable tables or analysis artifacts rather than manual recollection.
3. Include uncertainty and practical magnitude, not only direction or statistical significance.
4. Retain negative, mixed, and failed-run evidence when it changes interpretation.
5. State deviations from the frozen design and identify exploratory analyses.
6. Scope causal language to designs that support causal inference.
7. Separate an observed association from its proposed mechanism.
8. Avoid universal language when evaluation covers a limited dataset, workload, model family, language, population, or time period.

Never invent a result, interpolate a missing value, select a favorable run silently, or treat synthetic plumbing output as scientific evidence.

## 5. Write each manuscript component

### Title and abstract

State the object of study and primary contribution without promotional superlatives. Include the problem, approach, evaluation context, principal verified finding, and bounded implication when the format permits.

### Introduction

Move from the important problem to the precise gap, research question, approach, contributions, and evidence. Present contributions as claims with scope, not as a list of activities.

### Background and related work

Define only concepts needed to understand the contribution. Organize prior work by the comparison dimensions that establish context and the gap. Preserve disagreement and boundary conditions.

### Methods

Describe the design at the resolution needed to evaluate validity and reproduce the work. Identify data, sampling, splits, preprocessing, models, prompts, baselines, metrics, hardware, software, randomization, stopping rules, and analysis choices as applicable.

### Results

Order results by research question or claim rather than by the sequence in which experiments happened. Pair every result with its setting, uncertainty, and evidence locator. Keep interpretation distinguishable from observation.

### Discussion

Explain what the evidence changes, which mechanisms remain uncertain, where results may generalize, and how rival explanations fare. Do not restate the results section as a stronger claim.

### Limitations, threats, and broader impacts

Describe limitations that could change interpretation, not ceremonial disclaimers. Address internal, construct, external, and statistical validity as applicable. Link ethical and societal risks to mitigations and residual uncertainty.

### Conclusion

Answer the research question at the supported level. Do not introduce new evidence, promises, or stronger generalizations.

## 6. Handle citations and related work

Verify citation identity and metadata against a DOI, publisher page, official proceedings entry, or authoritative repository. Open the primary source before making a substantive attribution.

Use metadata-only and abstract-only records for discovery, not for precise claims. Record a full-text locator for consequential comparisons. Distinguish whether a source supports, challenges, contextualizes, or merely mentions a claim.

Avoid:

- Creating citations from memory or completing metadata by guesswork.
- Citing a survey as the sole evidence for a claim made by an accessible primary source.
- Citing a paper for a claim it attributes to another work.
- Using citation count as a substitute for relevance or validity.
- Claiming exhaustive coverage without a systematic search protocol.
- Using “first,” “only,” or “unprecedented” without evidence sufficient for that scope.

Express novelty as a dated comparison with the nearest verified work. Record the search cutoff and limitations.

## 7. Build tables, figures, and appendices

Generate tables and figures from versioned analysis outputs when practical. Record the producing script, source data, configuration, and artifact ID.

Require every display to:

- Answer a named question or support a claim.
- Define metrics, units, directionality, aggregation, and uncertainty.
- Identify datasets, models, conditions, sample sizes, and excluded observations.
- Use readable labels, accessible colors, and captions that permit correct interpretation.
- Agree numerically with the text and supplementary material.

Do not hide unfavorable conditions in an appendix merely to simplify the main narrative. Use appendices and supplements for necessary detail, robustness checks, proofs, protocols, prompts, and expanded results subject to current venue rules.

## 8. Check current venue requirements

Retrieve requirements from current official venue, publisher, funder, or institutional sources. Record the URL, version or cycle, and access date.

Check, as applicable:

- Scope and contribution expectations.
- Official template and allowed modifications.
- Page, word, reference, appendix, and supplement treatment.
- Anonymity and self-citation rules.
- Author, conflict, and contribution declarations.
- Human-subject, ethics, data, artifact, and reproducibility statements.
- Generative-AI use, disclosure, and reviewer-assistance policies.
- Citation, accessibility, language, and file-format requirements.
- Artifact, code, data, model, and license obligations.

Do not encode remembered limits as current policy. If official sources conflict or remain ambiguous, report the conflict and request a human decision before irreversible submission work.

## 9. Revise and audit the manuscript

Revise in passes:

1. Audit the research question, contribution, and claim hierarchy.
2. Audit every claim against evidence and truth state.
3. Audit methods against the executed design and deviations.
4. Audit every number across text, tables, figures, appendix, and abstract.
5. Audit related-work comparisons and citation locators.
6. Audit limitations, ethics, privacy, licensing, and disclosures.
7. Audit terminology, notation, cross-references, and acronym consistency.
8. Audit current venue compliance.
9. Copyedit only after substantive consistency passes.

Preserve deliberate author choices and repository conventions. Do not flatten uncertainty or erase limitations for rhetorical force. Record material claim changes in the project dossier.

Run the writing gate in quality-gates.md before calling the manuscript complete. Return PASS, CONDITIONAL, FAIL, BLOCKED, or NOT_ASSESSED with evidence and the next decisive action.

## 10. Deliver the artifact

Lead with what was drafted or changed. Identify:

- The artifact paths.
- The central claims and evidence status.
- Any remaining citation, result, policy, or formatting markers.
- The venue-policy source and access date when venue adaptation was requested.
- The writing-gate status.
- The smallest next action needed for a submission-ready manuscript.

Distinguish completed edits from recommended future work. Never describe a manuscript as submission-ready when unresolved evidence, integrity, policy, or authorization blockers remain.
