# Quality Gates

## Contents

1. Apply the gate protocol
2. Assign gate status
3. Calibrate mandatory checks
4. Route phase-specific gates to their references
5. Gate the research contract and problem
6. Gate a proposal
7. Gate feasibility, ethics, and policy
8. Gate execution and evidence eligibility
9. Gate paper writing
10. Gate submission or release
11. Report and reconcile gate outcomes

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

## 4. Route phase-specific gates to their references

Each phase reference owns the detailed criteria for its gate. Load the reference and apply its gate section with the protocol above; do not maintain a second criteria list here.

| Gate | Canonical criteria |
|---|---|
| Literature, novelty, and feasibility | [literature-and-ideas.md](literature-and-ideas.md), section "Run novelty and feasibility gates" |
| Experimental design | [experimental-design.md](experimental-design.md), section "Pass the design gate" |
| AI and ML evaluation | [cs-ai-evaluation.md](cs-ai-evaluation.md), section "Pass the AI evaluation gate" |
| Implementation and reproducibility | [implementation-and-reproducibility.md](implementation-and-reproducibility.md), section "Pass the implementation gate" |
| Analysis and interpretation | [analysis-and-statistics.md](analysis-and-statistics.md), section "Preserve analysis provenance and pass the gate" |
| Figures and diagrams | [figures-and-diagrams.md](figures-and-diagrams.md), section "Record provenance and pass the figure gate" |
| Review and rebuttal | [paper-review-and-rebuttal.md](paper-review-and-rebuttal.md), section "Complete the review or rebuttal gate" |
| Submission formatting | [paper-formatting.md](paper-formatting.md), section "Iterate, record, and pass the formatting gate" |
| Ethics and policy response | [ethics-integrity-and-policy.md](ethics-integrity-and-policy.md), section "Respond to concerns and record the gate" |

The gates below have no phase reference of their own and remain canonical here.

## 5. Gate the research contract and problem

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

## 8. Gate execution and evidence eligibility

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

## 9. Gate paper writing

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
- A rendered-format inspection per paper-formatting.md when layout compliance matters: compile log, rendered page images, page count, and file metadata.
- No unresolved [CITATION NEEDED], [EVIDENCE NEEDED], or [RESULT PENDING] marker in submission text.

Set FAIL for fabricated or unsupported claims, material numerical inconsistency, hidden deviations, missing mandatory disclosure, or a methods section that misrepresents execution.

Use CONDITIONAL for bounded presentation work that does not affect validity or compliance and has an owner. Use BLOCKED for an unresolved venue policy, authorship decision, required approval, or missing central artifact.

## 10. Gate submission or release

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

## 11. Report and reconcile gate outcomes

Report the gate outcome with the requested artifact. Lead with the decision and the evidence supporting it.

Update project state only when authorized. Preserve:

- Gate name, scope, status, date, and assessor.
- Evidence and artifact versions.
- Deviations, waivers, blockers, and owners.
- Truth-state changes justified by the gate.
- The next decisive action.

When evidence changes, rerun affected downstream gates. Downgrade stale or unsupported statuses. Do not retain PASS after its supporting artifact, policy, design, or result has materially changed.

Never call a phase complete merely because a document, code path, or run exists.
