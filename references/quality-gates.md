# Quality Gates

## Contents

1. Apply the gate protocol
2. Assign gate status
3. Calibrate mandatory checks
4. Gate the research contract and problem
5. Gate literature, gap, and idea selection
6. Gate a proposal
7. Gate feasibility, ethics, and policy
8. Gate experimental design
9. Gate implementation
10. Gate execution and evidence eligibility
11. Gate analysis and interpretation
12. Gate paper writing
13. Gate review and rebuttal
14. Gate submission or release
15. Report and reconcile gate outcomes

## 1. Apply the gate protocol

Use gates as decision controls, not ceremonial checklists. Select only the gates needed for the requested deliverable and every earlier gate on which that deliverable materially depends.

For each gate:

1. Name the decision the gate controls.
2. Identify mandatory criteria for the contribution type, methodology, risk, and current phase.
3. Inspect evidence directly rather than inferring completion from prose or filenames.
4. Record evidence IDs, run IDs, artifact paths, source locators, and policy sources.
5. Record uncertainty, deviations, waivers, blockers, and the decision owner.
6. Select one controlled status.
7. Specify the smallest decisive next action.

Return:

    Gate: <name>
    Status: PASS | CONDITIONAL | FAIL | BLOCKED | NOT_ASSESSED
    Decision controlled: <what may proceed>
    Evidence: <IDs, paths, and locators>
    Uncertainty: <what remains unknown>
    Deviations: <departures from the approved plan>
    Waivers: <risk, authority, rationale, and expiry or revisit condition>
    Next decisive action: <smallest informative step>

Do not merge gate status with research truth state. A manuscript may exist at IMPLEMENTED while its writing gate is FAIL. An experiment may be EXECUTED while its evidence-eligibility gate is CONDITIONAL.

## 2. Assign gate status

Use the statuses consistently:

| Status | Meaning |
|---|---|
| PASS | Inspect every mandatory criterion and support it with sufficient evidence; allow the controlled decision to proceed. |
| CONDITIONAL | Find no known disqualifying failure, but retain bounded deficiencies, explicit assumptions, or accepted risks with owners and resolution conditions. |
| FAIL | Establish that one or more mandatory criteria are not met; require redesign, correction, narrowing, or rejection before proceeding. |
| BLOCKED | Lack required access, authority, approval, artifact, policy interpretation, resource, or dependency needed for responsible assessment or action. |
| NOT_ASSESSED | Do not inspect this gate or lack enough scoped work even to characterize it; make no quality claim. |

Apply precedence carefully:

- Use FAIL rather than BLOCKED when available evidence establishes a defect.
- Use BLOCKED when a dependency prevents a responsible determination or action.
- Use CONDITIONAL only when proceeding is permitted and the residual risk is bounded.
- Use NOT_ASSESSED rather than PASS when the dimension was skipped.
- Use PASS only for the defined scope; never imply whole-project approval from a narrow check.

Do not convert FAIL to CONDITIONAL merely because a deadline is near. Do not convert BLOCKED to PASS by assuming an approval or artifact exists.

## 3. Calibrate mandatory checks

Identify the primary contribution and methodology from research-contract-and-state.md. Mark a criterion mandatory only when it bears on the stated contribution, inference, policy, or release.

Do not require:

- SOTA performance when the contribution is measurement, theory, replication, negative evidence, or insight.
- Experiments for a self-contained proof unless empirical claims are also made.
- Novelty from a replication whose stated value is reliability.
- Statistical significance for qualitative, formal, or deterministic claims.
- A positive outcome from a credible negative-results design.
- Public artifact release when law, consent, license, confidentiality, or safety forbids it.

Require an equivalent burden of proof rather than deleting an inapplicable criterion. For example, replace benchmark accuracy with proof completeness for theory or credibility and reflexivity checks for qualitative work.

Treat automated audits as structural evidence only. Do not let a passing script determine novelty, construct validity, ethics, policy compliance, or scientific soundness.

## 4. Gate the research contract and problem

Control whether substantive planning should proceed.

Require:

- A concrete deliverable and decision.
- A precise problem, affected setting, and reason it matters.
- An answerable research question or defensible conceptual objective.
- A primary contribution type and methodology.
- A stated unit of analysis and intended generalization.
- Known constraints, prohibitions, dependencies, and evidence cutoff.
- Success, failure, and kill criteria.
- A cheapest decisive falsifier or de-risking step.
- Clear user authority for the next proposed action.

Set:

- PASS when the question is stable enough to investigate and the next action is authorized.
- CONDITIONAL when safe assumptions permit bounded progress.
- FAIL when the question is incoherent, unfalsifiable despite claiming empirical proof, trivial under the stated objective, or mismatched to the proposed evidence.
- BLOCKED when a material decision owner, artifact, access permission, or noninferable requirement is absent.

## 5. Gate literature, gap, and idea selection

Control whether a novelty, gap, or idea claim may guide a proposal or paper.

Require:

- A dated and scoped search protocol proportionate to the claim.
- Current primary and authoritative sources.
- Verified identity and substantive inspection for nearest work.
- Search terms, databases or venues, backward and forward tracing where practical, and inclusion rationale.
- A comparison matrix using dimensions relevant to the contribution.
- Evidence that distinguishes an unsolved problem from an unsearched one.
- Rival interpretations and disconfirming prior work.
- A scoped novelty statement and explicit coverage limits.
- Feasibility, impact, evaluability, ethical risk, and kill criteria for shortlisted ideas.

Set FAIL when verified nearest work already establishes the same contribution under the claimed scope or when the proposed gap does not matter to the research question. Narrow or reframe rather than hide the conflict.

Never use “first,” “only,” “unprecedented,” or “no prior work” from an informal search. Use NOT_ASSESSED when novelty was not investigated.

## 6. Gate a proposal

Control whether the proposal is ready for internal approval or the next authorized submission step.

Require:

- Alignment among the problem, gap, objectives, questions, hypotheses, and contribution.
- A methodology capable of answering each research question.
- A claim-to-study or objective-to-work-package trace.
- Credible data, sampling, baselines, metrics, analysis, and validation as applicable.
- Timeline, dependencies, staffing, compute, infrastructure, budget, and deliverables.
- Risks, rival explanations, fallback designs, and stop conditions.
- Ethics, privacy, security, licensing, dual-use, and access plans.
- Current official solicitation or degree requirements when a target exists.
- Clear separation between expected outcomes and completed evidence.

Set FAIL when the method cannot answer the central question, resources cannot support a minimum informative study, or the proposal asserts completed results that do not exist.

Use CONDITIONAL for bounded issues such as pending noncritical metadata or a named feasibility check that is permitted before final commitment. Use BLOCKED for missing mandatory approval, access, eligibility, or solicitation interpretation.

## 7. Gate feasibility, ethics, and policy

Control resource commitment, participant or data access, risky implementation, and external release.

Require, as applicable:

- Evidence of data, model, API, hardware, skill, time, and financial feasibility.
- A minimum informative experiment within the authorized budget.
- Human-subject or institutional determination before recruitment or intervention.
- Consent, privacy, security, and data-governance controls.
- License, terms, intellectual-property, and sharing compatibility.
- Dual-use risk assessment and proportionate safeguards.
- Current official venue, funder, employer, and institutional rules.
- Explicit authority for expensive, sensitive, dangerous, or externally consequential actions.

Treat missing mandatory ethics approval, consent, legal authority, confidentiality permission, or safety control as FAIL or BLOCKED according to whether noncompliance is established or assessment is prevented.

Do not waive law, consent, confidentiality, or a nonwaivable safety control.

## 8. Gate experimental design

Control whether implementation or claim-eligible execution should begin.

Require:

- A mapping from research questions and claims to constructs, interventions or conditions, outcomes, and analyses.
- A defensible unit of analysis and sampling frame.
- Dataset, split, duplicate, leakage, and contamination controls.
- Fair baselines, comparators, tuning budgets, and compute accounting.
- Metrics aligned to constructs and deployment costs.
- Randomization, blocking, pairing, seeds, repeats, power or precision rationale as applicable.
- Ablations, robustness, sensitivity, error analysis, and rival explanations proportionate to the claims.
- Human-evaluation protocol, annotator plan, judge calibration, or qualitative rigor where applicable.
- Frozen primary outcomes, analysis choices, failure criteria, and deviation process.
- A pilot that informs feasibility without becoming silent confirmatory evidence.

Set FAIL when the design cannot distinguish the claimed effect from leakage, confounding, unfair comparison, measurement failure, or stochastic noise at the required level.

Use CONDITIONAL when a named pilot or calibration step is part of the approved design and cannot itself support the final claim.

## 9. Gate implementation

Control whether the pipeline may perform claim-eligible runs.

Require:

- Versioned code, configuration, dependencies, and environment.
- Validated data acquisition, checksums or fingerprints, preprocessing, and split reproduction.
- Deterministic or appropriately stochastic behavior with recorded seeds.
- Unit, integration, and smoke tests for central transformations and metrics.
- Baseline parity in preprocessing, tuning, resource budget, and evaluation.
- Logging of commands, errors, configuration, hardware, timing, cost, and raw outputs.
- Separation of immutable raw outputs from derived analysis artifacts.
- Safe handling of credentials, personal data, untrusted artifacts, and external services.
- A run manifest linked to the approved experiment plan.

Do not treat successful execution on a toy or synthetic case as scientific evidence. Set PASS only for readiness within the tested scope.

Set FAIL when a central metric, split, baseline, or data path is incorrect. Set BLOCKED when required data, infrastructure, credentials, or authorization is unavailable.

## 10. Gate execution and evidence eligibility

Control whether a run may support a scientific claim.

Require:

- Execution under the approved design or a documented deviation.
- Immutable raw outputs and a complete run manifest.
- Code revision, configuration, environment, hardware, data lineage, seeds, timing, and cost.
- Retention of failed, interrupted, and unfavorable runs.
- No silent test-set adaptation, cherry-picking, or repeated trials hidden from the search budget.
- Verification that outputs correspond to the recorded run.
- A clear label for pilot, exploratory, confirmatory, reproduction, or stress-test evidence.

Set FAIL for corrupted provenance, undisclosed selective reporting, invalid split use, or a deviation that destroys claim eligibility. Preserve the run as diagnostic evidence when useful.

Use CONDITIONAL when evidence remains eligible only for a narrowed claim or explicitly exploratory conclusion.

## 11. Gate analysis and interpretation

Control whether analyzed results may become verified claims.

Require:

- A trace from raw outputs through versioned analysis to every reported value.
- Correct unit of analysis and treatment of pairing, clustering, repeated measures, and dependence.
- Effect sizes and uncertainty appropriate to the design.
- Assumption checks, sensitivity analyses, and multiplicity handling where needed.
- Missingness, exclusions, outliers, and failed-run treatment.
- Comparison with prespecified outcomes and transparent labeling of exploratory analyses.
- Robustness, subgroup, error, or qualitative analysis needed to interpret the contribution.
- Rival explanations and limitations.
- Numerical consistency across tables, figures, text, abstract, and conclusion.

Set FAIL when the analysis cannot support the claim, uses an invalid denominator or unit, hides material outcomes, or overstates association as causation.

Do not equate lack of statistical significance with evidence of equivalence or no effect without an appropriate design.

## 12. Gate paper writing

Control whether the manuscript may be described as internally complete or ready for the next authorized submission step.

Require:

- A stable claim map linked to verified sources, proofs, runs, analyses, tables, and figures.
- Contribution-appropriate framing and scoped novelty language.
- Methods matching the executed work and disclosed deviations.
- Result wording matching evidence strength and generalization scope.
- Verified citations and consequential source locators.
- Consistent values, terminology, notation, and artifact references.
- Limitations, validity threats, ethics, data, licensing, safety, and disclosure statements.
- Current official venue or publisher requirements, with source and access date.
- No unresolved [CITATION NEEDED], [EVIDENCE NEEDED], or [RESULT PENDING] marker in submission text.

Set FAIL for fabricated or unsupported claims, material numerical inconsistency, hidden deviations, missing mandatory disclosure, or a methods section that misrepresents execution.

Use CONDITIONAL for bounded presentation work that does not affect validity or compliance and has an owner. Use BLOCKED for an unresolved venue policy, authorship decision, required approval, or missing central artifact.

## 13. Gate review and rebuttal

Control whether a review or response may be delivered to the authorized human.

For a review, require:

- Authorization, confidentiality, current AI-use policy, and conflict assessment.
- Calibration to contribution type and methodology.
- Independent reconstruction of claims and evidence.
- Location-specific findings with proportional severity.
- Clear impact, actionable remedy, and reviewer uncertainty.
- Separation of soundness, significance, novelty, clarity, venue fit, and recommendation.
- Current official rubric before assigning scores.

For a rebuttal, require:

- A disposition for every material reviewer comment.
- Direct, evidence-backed answers.
- Exact locations for completed changes.
- Honest labels for new, pilot, pending, or unavailable evidence.
- Respectful disagreement and bounded commitments.
- Current official response and disclosure rules.

Set BLOCKED when confidential-artifact processing is not authorized or current policy prohibits AI assistance. Do not replace artifact-specific review with inferred content.

## 14. Gate submission or release

Control any externally consequential submission, publication, artifact release, or communication.

Require:

- Explicit user authorization for the exact external action.
- Final consistency among manuscript, supplement, code, data, models, metadata, declarations, and claims.
- Current official formatting, anonymity, authorship, conflict, ethics, AI-use, artifact, and license rules.
- Removal of secrets, personal data, hidden metadata, internal comments, and disallowed identifying content.
- Valid permissions and licenses for every released artifact.
- Safety and dual-use review proportional to release capability.
- A reproducible archive or an honest access limitation.
- Human confirmation of author list, order, declarations, and final files.

Do not submit, upload, publish, accept terms, attest compliance, or contact third parties without explicit authority. Use BLOCKED when that authority is absent.

## 15. Report and reconcile gate outcomes

Report the gate outcome with the requested artifact. Lead with the decision and the evidence supporting it.

Update project state only when authorized. Preserve:

- Gate name, scope, status, date, and assessor.
- Evidence and artifact versions.
- Deviations, waivers, blockers, and owners.
- Truth-state changes justified by the gate.
- The next decisive action.

When evidence changes, rerun affected downstream gates. Downgrade stale or unsupported statuses. Do not retain PASS after its supporting artifact, policy, design, or result has materially changed.

Never call a phase complete merely because a document, code path, or run exists.
