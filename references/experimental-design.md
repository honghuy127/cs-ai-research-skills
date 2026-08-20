# Experimental Design

## Contents

1. Start from the research contract
2. Route the methodology
3. Align claims, constructs, and decisions
4. Separate exploratory and confirmatory work
5. Define units, sampling, and data splits
6. Choose comparisons, controls, and ablations
7. Justify sample size and information
8. Plan randomness, trials, and compute
9. Freeze the design and record deviations
10. Apply method-specific checks
11. Pass the design gate

## 1. Start from the research contract

Read `research-contract-and-state.md` and inspect existing plans, data documentation, code, and `.research/` records before designing a study.

1. State the decision or knowledge claim the study must support.
2. Identify the primary contribution type and the methodology that supplies its evidence.
3. Record the target population, operating conditions, unit of analysis, and intended scope of generalization.
4. Record constraints on data, compute, time, people, access, privacy, licensing, and safety.
5. Define the smallest informative study and the cheapest result that would falsify or materially weaken the central idea.
6. Mark unavailable information as `NOT_ASSESSED`; do not fill design gaps with conventional defaults.

Design only to the resolution required by the claim. Do not require an empirical study for a self-contained proof, a controlled experiment for a descriptive question, or a systematic review for ordinary related work.

## 2. Route the methodology

Select one primary route and add secondary routes only when each answers a distinct research question.

| Study signal | Primary route | Central validity burden |
|---|---|---|
| Deliberately manipulate a treatment | Controlled or quasi-experiment | Allocation, controls, protocol fidelity, power, and causal identification |
| Observe existing behavior or records | Observational or repository-mining study | Sampling, measurement, confounding, dependence, and scope |
| Compare systems on a repeatable workload | Benchmark or systems-measurement study | Workload representativeness, fairness, stability, and reproducibility |
| Develop and assess an artifact | Engineering or design study | Need, mechanism, appropriate comparison, utility, and tradeoffs |
| Model a real process computationally | Simulation | Model verification, empirical validation, calibration, and sensitivity |
| Interact with people | Human-participant study | Consent, recruitment, allocation or sampling, measurement, and participant protection |
| Elicit perceptions with structured items | Survey | Target population, instrument validity, response bias, and missingness |
| Interpret interviews, observations, or text | Qualitative study | Sampling rationale, reflexivity, coding trace, credibility, and saturation or information power |
| Synthesize existing studies exhaustively | Systematic review or meta-analysis | Reproducible search, selection, extraction, study quality, and synthesis |
| Establish a formal claim | Theory or formal analysis | Explicit assumptions, definitions, proof correctness, and scope |
| Combine evidence forms | Mixed methods | Rationale for combination, method-level validity, and integration of findings |

Route AI models, learned systems, agents, or automated judges through `cs-ai-evaluation.md` in addition to this file. Route analysis choices through `analysis-and-statistics.md` after the design is fixed.

## 3. Align claims, constructs, and decisions

Create one row per central claim before selecting datasets or metrics:

| Field | Required content |
|---|---|
| Claim ID | Stable ID such as `CLM-001` |
| Claim text | Precise descriptive, predictive, causal, mechanistic, comparative, or utility claim |
| Population and conditions | Entities, settings, time horizon, interventions, and exclusions covered |
| Construct | Property that matters to the research question |
| Operational measure | Observable variable, instrument, metric, or coding rule |
| Contrast or estimand | Quantity to estimate or comparison that answers the claim |
| Evidence source | Experiment, observation, proof, benchmark, qualitative evidence, or synthesis |
| Rival explanation | Credible alternative account of the same observation |
| Failure criterion | Outcome that contradicts, bounds, or materially weakens the claim |

Then apply these checks:

- Define constructs independently of convenient metrics. Explain why each measure represents the intended construct and what it omits.
- Separate the unit of allocation, intervention, observation, and analysis. Prevent pseudoreplication by analyzing at the level that received independent variation.
- Match language to identification. Use causal wording only when the design and assumptions identify a causal effect.
- Define primary outcomes and their direction before inspecting confirmatory results.
- Define a practically meaningful effect or decision threshold where the use case supports one; do not substitute statistical detectability for importance.
- Bound generalization to sampled populations, workloads, languages, domains, model families, time periods, and deployment conditions.
- Include negative and null outcomes in the claim map. Do not design only for a favorable story.

## 4. Separate exploratory and confirmatory work

Label every analysis path before using its output as evidence:

- Use **exploratory** work to discover patterns, test plumbing, estimate variability, refine instruments, or generate hypotheses.
- Use **confirmatory** work to test frozen hypotheses or decision rules on data not used to create them.
- Use **descriptive** work to characterize a sample without implying population-level or causal conclusions beyond the design.

Keep pilot data and confirmatory data separate unless the design explicitly allows reuse and the analysis accounts for it. If exploratory inspection changes the hypothesis, metric, exclusion rule, split, comparator, or stopping rule, record the change and obtain new claim-eligible data when possible.

Do not turn an exploratory result into confirmatory evidence by changing prose. Report mixed workflows as mixed: identify the prespecified part, the discovered part, and what independent confirmation remains necessary.

## 5. Define units, sampling, and data splits

### Sampling

1. Define the target population or task universe.
2. Describe the sampling frame and how it differs from the target.
3. State inclusion and exclusion criteria before selection when feasible.
4. Record the sampling mechanism, recruitment path, filters, attrition, missingness, and coverage gaps.
5. Sample at the level of the intended inference. Account for clusters such as users, repositories, documents, conversations, sites, or repeated measurements.
6. Justify convenience samples and narrow benchmarks; restrict claims rather than hiding the limitation.

### Splits and leakage

- Choose the split unit to prevent related entities from crossing partitions. Group by user, subject, source, repository, document family, time, geography, or other dependency when needed.
- Use chronological splits when the claim concerns future performance or when temporal leakage is plausible.
- Deduplicate before splitting, including near-duplicates and transformed copies when they can leak labels or solutions.
- Fit preprocessing, feature selection, imputation, normalization, representation learning, threshold choice, and other data-dependent transformations on training data only.
- Use development data or nested resampling for model and hyperparameter selection. Keep the final test set unavailable to the selection loop.
- Treat repeated cross-validation folds as dependent estimates, not as independent experimental units.
- Record split-generation code, source entity IDs, timestamps, filters, and randomization inputs.
- Audit label leakage, target proxies, post-outcome variables, benchmark answer exposure, and human annotation contamination.
- Replace or quarantine a compromised test set. Do not repair leakage only in the manuscript narrative.

If no train/development/test structure applies, define the analogous separation between design data and assessment data.

## 6. Choose comparisons, controls, and ablations

Choose each comparator to answer a named question:

- Include a simple or no-skill baseline to establish that the task and metric are meaningful.
- Include the current practice, incumbent system, non-AI alternative, human-only process, or prior method when it represents the real decision.
- Include a strong available method when needed to locate the contribution, but do not require a nominal SOTA system that is unavailable, inapplicable, irreproducible, or unfair to compare.
- Match information, data, preprocessing, tools, tuning opportunity, compute or interaction budget, and evaluation conditions across methods unless the difference is itself part of the claim.
- Report tuning and search budgets for every compared method. Do not lavish optimization on the proposed method while using untuned baselines.
- Use positive, negative, placebo, sham, or oracle controls only when their interpretation is explicit. Label an oracle or upper bound as unattainable rather than as a competitor.
- Add an ablation only when it isolates a component, mechanism, data source, or design choice named in a claim. Do not generate a combinatorial ablation table without a question.
- Test interactions when components are expected to depend on one another; a one-at-a-time ablation cannot establish all interactions.
- Preserve unfavorable comparisons and failed variants that belong to the frozen design.

Explain any omitted comparator by availability, relevance, rights, safety, or resource constraints and narrow the resulting claim.

## 7. Justify sample size and information

Base the rationale on the inferential unit, expected variability, smallest meaningful effect, desired precision, decision risk, and available resources.

- Use analytical power, simulation, historical variance, precision targets, sequential design, or another design-appropriate method.
- Simulate power for hierarchical, clustered, adaptive, nonstandard, or metric-heavy designs when closed-form assumptions are implausible.
- Account separately for the number of independent items, participants, or entities, and the number of repeated stochastic trials. More seeds do not compensate for too few test items, and more items do not measure run-to-run instability.
- For equivalence or non-inferiority claims, set and justify the margin before analysis.
- For qualitative work, justify sample sufficiency through information power, saturation, diversity, or case coverage rather than a quantitative power formula.
- For resource-limited studies, state what effects or failures the study can and cannot detect. Treat the constraint as a limitation, not as proof of adequacy.
- Avoid post-hoc observed power. Interpret estimates and uncertainty directly after data collection.

Do not impose a universal participant, dataset, seed, fold, or trial count.

## 8. Plan randomness, trials, and compute

Inventory every material source of variation, including sampling, split assignment, initialization, minibatch order, augmentation, stochastic decoding, simulator state, hardware nondeterminism, service changes, annotators, and environment timing.

1. Decide which sources to randomize, block, stratify, hold fixed, or model.
2. Choose trial counts using variance, stability, power or precision, cost, and failure risk.
3. Freeze the seed list or seed-generation rule before confirmatory execution.
4. Retain every planned run, including crashes and unfavorable outcomes; classify technical failures using a prespecified rule.
5. Define aggregation across trials and across test items separately.
6. Record per-run and total compute, hardware, memory, wall time, API usage, monetary cost, and material preliminary search when relevant.
7. Set resource and stopping limits before execution. Do not stop because a favorable threshold first appears unless a valid sequential rule was planned.

Treat a seed as provenance, not as a guarantee of identical results across software or hardware.

## 9. Freeze the design and record deviations

Create a timestamped, versioned experiment plan before claim-eligible execution, recording it in `assets/experiment-plan.md` or the dossier. Include:

- Research questions, hypotheses, claim IDs, and contribution type.
- Units, population, sampling, partitions, and exclusion rules.
- Treatments, comparators, controls, and ablations.
- Outcomes, metrics, estimands, practical thresholds, and analysis methods.
- Sample-size rationale, trials, seeds, stopping rules, and compute budget.
- Data and model versions, protocol, environment, and artifact paths.
- Planned tables, figures, robustness checks, and failure criteria.
- Ethics, privacy, licensing, safety, and release constraints.

Store a version identifier or content hash in the experiment record. Record every deviation with the time, reason, evidence available when decided, affected claims, and whether it occurred before or after outcome inspection. Never silently update the frozen plan.

Use a registered report or public preregistration when appropriate and permitted, but do not confuse public registration with good design. A versioned internal freeze still matters when public registration is infeasible.

## 10. Apply method-specific checks

### Controlled and human-participant experiments

- Randomize allocation or justify why it is impossible; describe concealment, blocking, crossover, washout, and order effects as applicable.
- Blind participants, operators, annotators, or analysts where feasible; otherwise explain likely bias.
- Validate instruments and manipulation; preserve instructions, recruitment, compensation, consent, attrition, and protocol deviations.
- Define treatment fidelity, interference risks, missing-data handling, and adverse-event procedures.

### Observational and repository-mining studies

- Draw a causal diagram or explicit rival-explanation map before making causal claims.
- Define time zero, exposure, outcome, censoring, and eligible population consistently.
- Avoid conditioning on consequences of treatment or selection without justification.
- Validate automated extraction and labels against a manually inspected sample; preserve acquisition and filtering code.

### Benchmark and systems studies

- Justify workload, scale, duration, warm-up, repetition, caching, isolation, and resource measurement.
- Randomize or counterbalance execution order when drift, throttling, thermal effects, or shared infrastructure can bias results.
- Validate benchmark stability and task solvability. Separate throughput, latency, quality, reliability, energy, and cost claims.
- Report the full distribution and failures rather than only peak performance.

### Simulation

- Verify implementation against invariants, limiting cases, and known solutions.
- Validate the model against independent real observations or explain why validation is unavailable.
- Separate calibration data from evaluation data. Vary structural assumptions and influential parameters.

### Survey and qualitative work

- Pilot instruments and prompts without erasing their revision history.
- Define recruitment, sampling, researcher positionality, coding, disagreement resolution, and stopping logic.
- Use multiple analysts when it improves credibility; do not use agreement coefficients mechanically where the epistemology does not support them.
- Preserve a defensible audit trail while protecting participant confidentiality.

### Theory and formal work

- Route primary validation to definitions, assumptions, proofs, mechanization, or counterexamples.
- Add experiments only when they illuminate scope, tightness, behavior, or practical relevance.
- Do not use empirical success to substitute for a missing proof of a formal claim.

### Mixed methods

- State what each method contributes and when integration occurs.
- Pass the validity checks for each component method.
- Explain convergence, complementarity, and disagreement rather than reporting parallel studies without synthesis.

## 11. Pass the design gate

Return `PASS`, `CONDITIONAL`, `FAIL`, `BLOCKED`, or `NOT_ASSESSED` with evidence and a next action.

Require all of the following for `PASS`:

- Map every central claim to an appropriate construct, measure, contrast, and failure criterion.
- Match methodology and analysis to the research question and dependence structure.
- Document sampling, leakage controls, comparators, sample rationale, variation, compute, and stopping logic.
- Separate exploratory, pilot, and confirmatory evidence.
- Freeze a versioned plan and define deviation handling.
- Address applicable ethics, rights, safety, and feasibility constraints.
- Identify a credible result that would weaken the proposed contribution.

Return `CONDITIONAL` only with an explicit waiver, affected claims, and owner. Return `FAIL` when the design cannot support the central claim. Return `BLOCKED` when a named dependency prevents a responsible decision.
