# Proposal Writing and Compliance

Use this playbook for a funding proposal, thesis proposal, internal research plan, or concept note. Load literature-and-ideas.md first when the novelty or evidence basis is not already gated. Use the shared research contract and state records; do not invent applicant facts, institutional commitments, preliminary results, costs, or approvals.

## Table of contents

- [Identify the proposal regime](#identify-the-proposal-regime)
- [Parse the current official instructions](#parse-the-current-official-instructions)
- [Build a compliance matrix](#build-a-compliance-matrix)
- [Construct the proposal logic](#construct-the-proposal-logic)
- [Define objectives and work packages](#define-objectives-and-work-packages)
- [Design the evaluation plan](#design-the-evaluation-plan)
- [Build the schedule, team, and resources](#build-the-schedule-team-and-resources)
- [Manage risks, ethics, and impacts](#manage-risks-ethics-and-impacts)
- [Draft and substantiate the narrative](#draft-and-substantiate-the-narrative)
- [Run internal review](#run-internal-review)
- [Hand off the proposal](#hand-off-the-proposal)

## Identify the proposal regime

First classify the deliverable:

- For a funding solicitation, treat the exact call, amendments, and submission system as binding.
- For a thesis or degree proposal, follow the current department, graduate school, and committee requirements; emphasize research questions, contribution, method, feasibility, and milestones.
- For an internal concept note, confirm the decision being requested, audience, length, budget authority, and evaluation criteria.
- For an industry or collaborative plan, confirm confidentiality, IP, data rights, publication constraints, and acceptance authority.

Do not force grant headings onto a thesis proposal or assume a generic agency format. Record the proposal regime, official source set, deadline, time zone, evidence cutoff, and responsible owner in the research contract.

## Parse the current official instructions

Open the current official solicitation and every incorporated document. Do not rely on remembered rules, prior-year templates, blog summaries, or another applicant's proposal.

Capture:

- call title, identifier, track, version, amendment history, URL, and access date;
- deadline, local time interpretation, submission window, and portal;
- applicant, institution, team, geography, career-stage, and collaboration eligibility;
- program scope, priorities, exclusions, duration, award range, and number of submissions allowed;
- required sections, order, headings, page or character limits, fonts, margins, file types, and templates;
- budget categories, indirect-cost treatment, cost sharing, salary or effort rules, currency, quotes, and unallowable costs;
- required attachments, letters, biosketches, facilities statements, certifications, and institutional approvals;
- data-management, open-science, software, security, privacy, ethics, human-participant, animal, environmental, export-control, and dual-use requirements;
- AI-assistance, authorship, disclosure, confidentiality, and research-security rules;
- review criteria, scoring scale, weights, panel type, and tie-break or portfolio considerations;
- official FAQs, webinars, Q&A responses, and help-desk clarifications that alter interpretation.

Apply this precedence unless the official text says otherwise:

1. latest amendment or solicitation-specific correction;
2. solicitation and incorporated track instructions;
3. current agency, institution, or degree-program policy;
4. required official template or portal validation;
5. informal guidance, examples, or third-party summaries.

Record the exact locator for each rule. If official sources conflict, stop the affected drafting, preserve both sources, and obtain an authoritative clarification. If the source cannot be accessed, mark the rule BLOCKED and ask for the official document; do not fill gaps from memory.

## Build a compliance matrix

Create the matrix before drafting. Use one row per atomic requirement.

| Field | Record |
|---|---|
| ID | Stable requirement ID such as REQ-001 |
| Requirement | Verbatim-minimal paraphrase of the rule |
| Authority | Official URL, version, access date, and page or section locator |
| Applicability | Track, applicant, section, or condition that activates the rule |
| Mandatory | Yes, no, conditional, or unresolved |
| Deliverable | Section, attachment, portal field, or institutional action |
| Owner | Named role responsible for content and validation |
| Evidence | File, page, approval, quote, or record that proves compliance |
| Status | NOT_ASSESSED, in progress, satisfied, conflict, or BLOCKED |
| Due and validation | Internal deadline and final checker |

Separate scientific content from applicant-specific administrative facts. Use explicit placeholders for unknown registrations, budgets, personnel, facilities, and commitments. Never manufacture an institutional detail to make the matrix look complete.

## Construct the proposal logic

Build one traceable chain:

need or decision → evidence-backed gap → goal or hypothesis → objectives → methods and work packages → evaluation → outputs → outcomes → impact.

For every link, ask what evidence supports it and what would break it. Map each review criterion to a section and evidence item. Keep the central claim narrow enough to test within the proposed resources. Distinguish outputs under the team's control from outcomes that depend on adoption and long-term impacts that remain uncertain.

Write a one-page logic summary before expanding the narrative. If an objective does not contribute to the central claim or a mandatory program outcome, remove it or justify it as enabling work.

## Define objectives and work packages

Use a small coherent set of objectives. Make each objective specific enough to evaluate without pretending that an uncertain research outcome is guaranteed.

For each objective or work package, record:

- research question or hypothesis;
- input evidence and dependencies;
- activities, method, and responsible role;
- data, software, compute, equipment, participants, or partners required;
- deliverables and acceptance evidence;
- milestone and target date;
- success, failure, and minimum-informative criteria;
- decision point, contingency, and pivot;
- dependency on approvals or another work package.

Show how the packages integrate. Avoid a chain in which one early failure makes every later package worthless; add independent learning, staged validation, or a viable fallback where scientifically honest.

## Design the evaluation plan

Map each proposed claim and objective to:

- construct and unit of analysis;
- data source, sampling or split strategy, and leakage controls;
- naive, strong, ablation, and resource-matched comparators as relevant;
- primary and secondary metrics with direction and interpretation;
- analysis model, uncertainty, robustness checks, and multiplicity handling;
- formative checkpoints and summative evaluation;
- acceptance, falsification, and inconclusive criteria;
- reproducibility artifacts and independent verification.

Load experimental-design.md and any relevant CS/AI evaluation reference for detailed empirical planning. Separate verified preliminary evidence from proposed work. Label pilot-only evidence accurately, and explain how negative or null outcomes will still produce knowledge. Do not transform an aspiration into a guaranteed effect size.

## Build the schedule, team, and resources

Construct a dependency-aware schedule, not a list of dates. Show work packages, approval lead times, procurement, data access, integration, evaluation, dissemination, critical-path dependencies, decision gates, and realistic slack.

Assign roles and decision rights. Use CRediT roles when useful, but follow the sponsor's required personnel categories. Distinguish named and confirmed contributors from planned hires, collaborators awaiting letters, and advisory roles.

Build the resource and budget case from auditable assumptions:

- personnel effort and allowed salary basis;
- compute, storage, API, data, participant, travel, equipment, publication, and dissemination costs;
- quotes, rates, exchange dates, inflation or escalation treatment, indirect costs, and contingency rules;
- resources already available, requested, shared, or conditional;
- budget-to-work-package and budget-to-justification mapping.

Follow the live solicitation and institutional budget policy. Do not invent a rate, quote, facility, commitment, or in-kind contribution. Confirm that the work fits the duration and that the budget buys every critical resource.

## Manage risks, ethics, and impacts

Maintain a risk register with the risk, cause, likelihood, impact, early indicator, prevention, contingency, owner, trigger, and residual risk. Cover scientific, technical, operational, schedule, budget, access, partnership, security, and adoption risks.

Assess at least:

- human participants, consent, vulnerability, compensation, and required review;
- personal, sensitive, proprietary, licensed, or cross-border data;
- privacy, security, model abuse, dual use, export control, and responsible release;
- copyright, software and dataset licenses, IP, and publication rights;
- bias, accessibility, affected groups, labor effects, and distribution of benefits and harms;
- compute, energy, hardware, and environmental impacts;
- conflicts of interest and research-integrity risks.

Treat approvals and access agreements as preconditions, not narrative formalities. State positive, negative, uncertain, and indirect impacts. Pair credible harms with mitigation, monitoring, accountable owners, and release or stop conditions.

## Draft and substantiate the narrative

Use assets/proposal-outline.md as a starting scaffold, then conform it to the official required order. Obtain alignment on the one-page logic and compliance matrix before writing long sections.

Draft section by section:

1. state the reader's decision and the proposal's central claim;
2. support the need and gap with verified SRC-* evidence;
3. state objectives and hypotheses without overstating novelty;
4. explain methods at the resolution needed to judge validity and feasibility;
5. connect evaluation, work plan, resources, risks, and impact;
6. close every section against the relevant review criterion.

Use future tense for proposed work and the shared truth states for existing work. Use [CITATION NEEDED], [EVIDENCE NEEDED], and [RESULT PENDING] instead of plausible filler. Allocate the page budget by review importance and compliance, not equal section length. Cite official instructions by locator in working notes even if the final proposal does not show them.

## Run internal review

Run distinct passes so one reviewer is not asked to catch everything at once:

1. **Desk-rejection pass:** eligibility, mandatory attachments, anonymization, format, page limits, portal fields, signatures, and deadline.
2. **Scientific pass:** importance, scoped novelty, coherent claims, current literature, and contribution.
3. **Method and evaluation pass:** identifiability, controls, baselines, measurement, uncertainty, failure criteria, and reproducibility.
4. **Feasibility pass:** access, dependency graph, personnel, schedule, budget, and institutional commitments.
5. **Ethics and impact pass:** approvals, rights, harms, safeguards, responsible release, and required disclosures.
6. **Independent-reader pass:** use a reviewer who did not author the section; ask them to score against the actual criteria.
7. **Production pass:** terminology, references, cross-references, rendered pages, file names, templates, and upload validation.

Track findings in a response matrix with severity, source criterion, location, owner, resolution, and recheck status. Re-open the official solicitation and amendment page before final sign-off because rules and FAQs can change during drafting.

## Hand off the proposal

Deliver:

- the proposal in the required structure and format;
- the completed compliance matrix and official-source snapshot or access log;
- the logic model, objectives, work packages, and evaluation map;
- schedule, roles, resource assumptions, budget mapping, and dependency record;
- risk, ethics, impact, data-management, and responsible-release records;
- literature evidence and scoped novelty gate;
- internal-review findings and final validation record.

Mark unresolved applicant facts and institutional actions explicitly. Do not call the proposal submission-ready while any mandatory row is unresolved, conflicting, or BLOCKED.
