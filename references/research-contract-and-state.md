# Research Contract and Project State

## Contents

1. Preflight
2. Research contract
3. Contribution and methodology routing
4. Project dossier
5. Claim and evidence records
6. Truth states and transitions
7. Decision gates
8. Resuming stale projects

## 1. Preflight

Inspect before asking questions:

- Existing manuscripts, proposals, code, configs, data documentation, results, reviews, and venue templates.
- Repository instructions and current version-control state.
- `.research/state.json` and append-only ledgers when present.
- The user's requested role and authorization: advise, diagnose, write, implement, run, or review.
- Confidentiality, ownership, licensing, personal-data, human-subject, safety, and official-review constraints.

Ask only for missing facts that would change scope, validity, cost, policy compliance, or the requested artifact. Otherwise state a reasonable assumption and proceed.

## 2. Research contract

Capture the following in `assets/research-brief.md` or equivalent project state:

- Working title and project ID.
- Decision or deliverable required now.
- Audience, venue, funder, or degree context.
- Problem, population or operating environment, and why it matters.
- Primary research question and secondary questions.
- Intended contribution type and methodology.
- Candidate hypotheses or propositions, including a rival explanation.
- Unit of analysis and scope of generalization.
- Evidence cutoff date and search scope.
- Available and prohibited data, code, models, infrastructure, and tools.
- Compute, API, money, people, skills, and time budgets.
- Ethical, legal, privacy, security, dual-use, and licensing constraints.
- Success criteria, failure or kill criteria, and the cheapest decisive test.
- Required artifacts and definition of done.
- Known unknowns, dependencies, and next decision owner.

Do not let a working title silently harden into a claim. Keep the question stable enough to design a test, but allow a recorded pivot when evidence warrants it.

## 3. Contribution and methodology routing

Identify one primary contribution and any supporting contributions:

| Contribution | Central burden of proof |
|---|---|
| Algorithm or method | Mechanism is clear; evaluation isolates the claimed improvement against fair alternatives. |
| Theory | Assumptions and claims are precise; proofs are complete; examples or experiments appear only when informative. |
| Empirical finding | Sampling, measurement, analysis, uncertainty, and scope support the inference. |
| System | End-to-end utility, resource tradeoffs, component necessity, and realistic workload are demonstrated. |
| Dataset or benchmark | Need, collection, documentation, quality, representativeness, licensing, contamination, and maintenance are credible. |
| Measurement or evaluation | Construct validity, protocol sensitivity, reliability, and interpretation are established. |
| Application | The real use case, domain constraints, stakeholders, and value beyond a toy transfer are demonstrated. |
| Human-centered | Recruitment, consent, protocol, measurement, power or saturation, analysis, and validity threats are addressed. |
| Survey or taxonomy | Scope and method are transparent; synthesis yields structure or insight beyond a list of papers. |
| Replication | Fidelity to the target, deviations, reproducibility conditions, and interpretation of agreement or disagreement are explicit. |
| Negative result | The tested expectation is credible; the test has power and coverage; failure modes are explained. |
| Position or conceptual | Thesis, assumptions, argument, counterarguments, and implications are coherent and grounded. |

Then select the methodology-specific standard. Do not apply a controlled-experiment checklist to a proof, a systematic-review claim to ordinary related work, or a novelty rubric to a replication whose value is reliability.

## 4. Project dossier

Keep canonical state project-local:

```text
.research/
  state.json
  decisions.md
  evidence.jsonl
  claims.jsonl
  experiments.jsonl
  runs/<run-id>/manifest.json
```

Use `state.json` as an index, not a second copy of the paper or code. Include:

- `schema_version`, `project_id`, timestamps, title, and current stage.
- Research questions, contribution type, methodology, deliverables, and constraints.
- Artifact paths, open risks, blockers, a compact `decision_index`, and next actions.
- Stage status chosen from the controlled truth states.

Keep `decisions.md` append-only. For each material decision record date, decision, evidence, alternatives, rationale, consequences, owner, and revisit condition.

Keep evidence, claims, and experiment records append-only. Correct an error with a new unique record ID and a `supersedes` field pointing to the old ID rather than silently erasing history when traceability matters.

## 5. Claim and evidence records

Use stable IDs such as `SRC-001`, `CLM-001`, `RQ-001`, `HYP-001`, `RUN-001`, `TAB-001`, and `FIG-001`.

An evidence record should contain:

```json
{"id":"SRC-001","title":"...","url":"...","doi":null,"source_type":"primary-paper","publication_status":"published","peer_review_status":"peer-reviewed","accessed_at":"YYYY-MM-DD","locator":"Sec. 3.2","supports":["CLM-001"],"challenges":[],"contextualizes":[],"verification":"full-text-checked","notes":"..."}
```

An internal claim record should contain:

```json
{"id":"CLM-001","text":"...","claim_type":"empirical","lifecycle_state":"proposed","evidential_status":"not_assessed","evidence_ids":[],"run_ids":[],"verification_run_ids":[],"verification_artifact_paths":[],"artifact_paths":[],"scope":"...","caveats":[],"updated_at":"..."}
```

Keep two independent fields:

- `lifecycle_state` records workflow maturity using the truth states below.
- `evidential_status` records the current verdict: `not_assessed`, `insufficient`, `supported`, `mixed`, or `contradicted`.

Thus a claim may be `analyzed` and `mixed`, or `verified` and `contradicted`. A citation may contextualize a claim without supporting it; record the relation honestly in the evidence record.

Keep evidence links reciprocal: every claim `evidence_ids` entry must point to an evidence record that lists the claim under `supports`, `challenges`, or `contextualizes`, and every such evidence relation must point back from the claim. Do not link `metadata-only` records as claim evidence.

For an empirical claim whose `lifecycle_state` is `verified` or `reported`, link a distinct full measured rerun in `verification_run_ids` or a concrete independent-check report in `verification_artifact_paths`. Do not reuse the primary run as its own verification.

For source verification, distinguish:

- `metadata-only`: identity checked; no substantive attribution allowed.
- `abstract-checked`: useful for triage; qualify any attribution.
- `full-text-checked`: relevant passage inspected and locator recorded.
- `artifact-checked`: code, data, appendix, or repository inspected.

## 6. Truth states and transitions

Use these lifecycle states:

| State | Meaning |
|---|---|
| `NOT_ASSESSED` | No evaluation has been made. |
| `PROPOSED` | An idea or claim exists, without an approved plan. |
| `PLANNED` | Design and success criteria are explicit. |
| `IMPLEMENTED` | The artifact exists but may not execute correctly. |
| `SMOKE_TESTED` | Basic plumbing executes on a minimal case. |
| `PILOT_ONLY` | A small exploratory run informs feasibility or design. |
| `EXECUTED` | The planned run completed and raw outputs were preserved. |
| `ANALYZED` | Prespecified or clearly labeled exploratory analysis completed. |
| `VERIFIED` | Independent trace or rerun supports the result and its provenance. |
| `REPORTED` | The verified claim appears consistently in the deliverable. |
| `BLOCKED` | A named dependency prevents responsible progress. |
| `DROPPED` | A recorded decision removed the item from scope. |

Allow loops and backward transitions. Record why. A `PILOT_ONLY` artifact never becomes confirmatory merely through rewriting.

In prose and gate reports, use the uppercase lifecycle labels above. `state.json` serializes their lowercase equivalents such as `proposed`, `smoke_tested`, and `verified`.

## 7. Decision gates

For every gate return:

```text
Gate: <name>
Status: PASS | CONDITIONAL | FAIL | BLOCKED | NOT_ASSESSED
Evidence: <IDs and artifact paths>
Uncertainty: <what remains unknown>
Waivers: <who accepted which risk and why>
Next decisive action: <smallest informative step>
```

Require explicit human confirmation when the decision materially fixes scope, commits substantial resources, recruits or affects people, accesses sensitive data, expands dangerous capability, freezes claims, or submits externally.

## 8. Resuming stale projects

Treat files as more authoritative than a stale index. On resume:

1. Read state and last decisions.
2. Inspect version control, artifacts, configs, raw outputs, and manuscript timestamps.
3. Reconcile missing, moved, or modified paths.
4. Check whether cited sources, venue rules, APIs, datasets, and models have changed.
5. Downgrade any state whose evidence is no longer present or reproducible.
6. Append a reconciliation decision and set the next decisive action.

Do not silently recreate lost results or infer that an undocumented output came from the claimed run.
