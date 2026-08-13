# CS and AI Evaluation

## Contents

1. Define the evaluation claim
2. Identify the evaluated system
3. Select and audit evaluation data
4. Specify the protocol
5. Choose fair comparators and ablations
6. Measure stochastic behavior
7. Validate metrics and judges
8. Evaluate agents and interactive systems
9. Control contamination and evaluation leakage
10. Test protocol sensitivity and robustness
11. Analyze failures, safety, and subgroup behavior
12. Report an auditable evaluation
13. Pass the AI evaluation gate

## 1. Define the evaluation claim

Read `experimental-design.md` first. Use this file for learned models, foundation models, API models, generative systems, retrieval-augmented systems, agents, automated judges, AI-assisted human workflows, and AI benchmarks.

Start with the intended use of the result, not with an available leaderboard:

1. State who will use the evaluation and what decision it informs.
2. Define the target construct, such as task success, factuality, calibration, robustness, usefulness, safety, efficiency, or user outcome.
3. State whether the evaluation measures the construct directly, measures a proxy, or predicts a downstream outcome.
4. Map the construct to observable outcomes, metrics, protocol settings, and a comparison or decision threshold.
5. Define the deployment or scientific conditions to which the claim applies.
6. Record what the evaluation cannot establish.

Use this alignment record:

```text
Claim ID:
Intended use of result:
Target construct:
Operational measure:
Evaluation population or task universe:
System boundary:
Protocol boundary:
Comparator or threshold:
Known proxy gap:
Result that would weaken the claim:
```

Do not infer broad intelligence, reasoning, safety, usefulness, or real-world impact from a narrow benchmark score without an explicit and supported bridge.

## 2. Identify the evaluated system

Define the system boundary before comparing results. Distinguish the base model from the complete system that includes prompting, retrieval, tools, memory, policies, and orchestration.

Record every field that can materially change behavior:

| Component | Record |
|---|---|
| Model | Developer or provider, exact name, version or checkpoint, weights digest when available, parameterization, quantization, adapters, tokenizer, and context limit |
| Access | Local or hosted access, endpoint and API version, region, access tier, evaluation dates and times, and provider-side features |
| Input construction | System, developer, user, few-shot, and tool prompts; templates; message ordering; truncation and packing rules |
| Generation | Temperature, top-p/top-k, maximum output, stop rules, penalties, number of samples, logit constraints, and seed support |
| Retrieval | Corpus version, index and embedding model, chunking, filters, top-k, reranker, update date, and access permissions |
| Agent scaffold | Planner, memory, reflection, retry, voting, routing, tool-selection, and termination logic |
| Tools and environment | Tool versions, schemas, permissions, network access, filesystem state, simulator or browser version, and initial state |
| Safety and policy | Moderation layer, refusal or content policy, guardrails, and any disabled or altered controls |
| Resources | Hardware, parallelism, latency budget, token or action budget, monetary cost, and rate limits |

Store prompt and configuration content as versioned artifacts, not only as prose. Preserve API responses and provider metadata permitted by policy. Do not describe a changing alias as a fixed model version.

When a provider cannot expose a version or implementation detail, record the uncertainty, evaluation date, and resulting limit on reproducibility.

## 3. Select and audit evaluation data

Evaluate each dataset, benchmark, workload, or environment against the claim:

- Document the exact version, source, license, access restrictions, provenance, creation date, and maintenance status.
- Explain what the benchmark was designed to measure and how that relates to the target construct.
- Inspect representative items and edge cases rather than relying only on a benchmark description.
- Assess coverage across task types, difficulty, languages, domains, demographics, environments, and failure modes relevant to the claim.
- Check floor and ceiling effects. Avoid a saturated or impossible benchmark when it cannot distinguish the systems or decision threshold of interest.
- Validate labels, graders, reference answers, environment dependencies, and task solvability.
- Define the population from which items are treated as sampled. Restrict inference when the benchmark is a fixed convenience set.
- Preserve item IDs and exclusions. Do not silently remove ambiguous, broken, or unfavorable items after seeing system results.
- Separate development items used for prompts, tool design, or scaffold tuning from final assessment items.
- Use group-, source-, or time-aware partitions when related items can leak solutions or styles.
- Record dataset transformations and verify that they do not alter the construct or advantage a system.

Treat a benchmark as a dataset-plus-metric-plus-protocol, not as a self-explanatory property of a model.

## 4. Specify the protocol

Write an executable protocol before claim-eligible evaluation. Define:

- Unit of evaluation: item, dialogue, episode, user, repository, task, environment, or session.
- Initial state and reset procedure between units and systems.
- Exact input assembly, context selection, few-shot examples, and output parsing.
- Number of attempts and trials, feedback after failure, retry policy, and whether best-of-n, majority vote, or pass@k is used.
- Termination conditions, maximum steps, timeouts, token/action/tool/cost limits, and invalid-output handling.
- Tool availability, permissions, error behavior, network access, and external state.
- Caching, batching, concurrency, rate limiting, backoff, and service-error policy.
- Randomization and counterbalancing of system, answer, item, and judge order.
- Human intervention, escalation, or adjudication points.
- Logging fields and privacy or retention rules.
- Scoring code, aggregation, uncertainty estimation, and planned exclusions.

Keep the protocol comparable across systems when the claim is about the model or method. If system-specific tools or budgets represent realistic product configurations, treat the complete configuration as the unit of comparison and state that the evaluation does not isolate the base model.

Do not retry only failed systems, select the best run after inspection, or alter prompts per item unless the adaptive procedure is itself frozen and applied fairly.

## 5. Choose fair comparators and ablations

Choose comparators from the decision being studied:

- Compare against random or no-skill behavior when it validates the task and grader.
- Compare against a simple transparent method to establish incremental value.
- Compare against the incumbent workflow, non-AI alternative, human-only process, AI-assisted human process, or previous system when it represents the use case.
- Compare against strong available methods when necessary to locate the contribution; do not impose a SOTA requirement disconnected from the claim.
- Equalize data, information access, tools, tuning opportunity, prompt optimization, attempts, and resource budgets when isolating method quality.
- Report quality-cost, quality-latency, or capability-resource tradeoffs when equal budgets would hide the practical decision.
- Validate human baselines with an appropriate sample, instructions, tools, incentives, and expertise; do not reuse an incomparable number from another protocol as ground truth.

Tie each ablation to a mechanism claim. Remove or replace one component while holding the rest of the system and evaluation fixed. Test interactions when components are coupled. Distinguish:

- **Component ablation:** Does the component contribute under this scaffold?
- **Protocol ablation:** Does a protocol choice materially change the result?
- **Resource ablation:** Does improvement come from more tokens, tools, data, or attempts?
- **Information ablation:** Does access to retrieval, memory, feedback, or privileged context explain performance?

Do not interpret an ablation as a universal causal mechanism outside the evaluated configurations.

## 6. Measure stochastic behavior

Inventory variability from item sampling, model sampling, initialization, retrieval, tool responses, environment timing, annotators, and service drift.

1. Decide whether the claim concerns expected, median, tail, best-case, or worst-case behavior.
2. Choose independent items and repeated trials to measure different sources of variation.
3. Select trial counts from stability, precision, failure rarity, cost, and the planned analysis; do not use a universal seed count.
4. Freeze seeds or a seed-generation rule where the system supports them.
5. Record that hosted APIs may remain nondeterministic even when a seed parameter exists.
6. Preserve every output and technical failure under the frozen failure policy.
7. Report aggregation across trials separately from aggregation across items.

Define derived metrics exactly. For pass@k, success@k, majority-of-n, self-consistency, or best-of-n, specify whether samples are independent, how k and n are used, how duplicate outputs count, and what resource multiplier the metric entails.

Do not treat multiple completions of one item as additional independent benchmark items.

## 7. Validate metrics and judges

### Select metrics

- Prefer measures that correspond directly to the decision and target construct.
- Report multiple dimensions separately when a single composite would hide tradeoffs.
- Justify weights and normalization in a composite score; test whether conclusions depend on them.
- Report calibration, selective behavior, cost, latency, reliability, or harm alongside task quality when the claim includes them.
- Use distributional and item-level results, not only a leaderboard average.
- Check whether the metric rewards shortcuts, verbosity, formatting, abstention, gaming, or leakage.

### Use programmatic graders

- Version and test grading code against known correct, incorrect, malformed, and adversarial cases.
- Define numerical tolerances, canonicalization, partial credit, and ambiguous-answer handling.
- Keep grader bugs and item bugs distinct from model failures.
- Run scoring invariants and preserve grader outputs with the system outputs.

### Use human evaluation

- Define the evaluator population, expertise, recruitment, compensation, consent, training, and exclusion rules.
- Use a task-specific rubric with examples and an abstain or uncertain option.
- Blind or randomize system identity and presentation order when feasible.
- Separate absolute ratings, pairwise preferences, ranking, and error annotation; analyze the design actually used.
- Plan overlap among evaluators and disagreement resolution. Report agreement or reliability only when meaningful for the construct and design.
- Preserve instructions, assignments, raw ratings, timestamps, and adjudication while protecting identities.

### Use an LLM or model-based judge

Treat the judge as a measurement instrument, not as ground truth.

1. Record the exact judge model, version, access date, prompt, rubric, examples, decoding, order, and parsing.
2. Validate the judge on a blinded human-rated sample that covers relevant score ranges and failure types.
3. Test position, length, style, self-family, reference-answer, and refusal biases when they could affect the conclusion.
4. Randomize or counterbalance candidate order and report ties, abstentions, invalid judgments, and disagreement.
5. Measure judge stability across repeated calls or relevant judge variants when nondeterminism matters.
6. Keep the judge independent of development when possible. Do not optimize the evaluated system directly against the final judge and then present the judge score as untouched evidence.
7. Use expert or human adjudication for cases where judge validity is weak or stakes are high.
8. Propagate judge uncertainty into result uncertainty rather than reporting only deterministic-looking scores.

Do not delegate scientific judgment about construct validity to the judge model.

## 8. Evaluate agents and interactive systems

Define an agent as the model plus scaffold, tools, permissions, memory, and environment. Evaluate both end-to-end performance and claimed components when the contribution requires attribution.

- Validate that each task is solvable in the supplied environment and that reference solutions still work.
- Version environment images, files, services, tool schemas, and initial state. Reset state between episodes unless persistence is part of the task.
- Specify action, token, time, tool, retry, and monetary budgets.
- Record every observation, action, tool call, tool result, state transition, intervention, and termination reason allowed by privacy policy.
- Distinguish reasoning or planning failures from tool, parser, environment, permission, network, and grader failures.
- Define task success, partial progress, invalid actions, side effects, and unsafe actions before execution.
- Test whether success depends on unintended environment shortcuts, leaked solution files, external search, or grader exploitation.
- Report completion quality with cost, latency, reliability, and harmful side effects.
- Control concurrent-agent interference and shared external state.
- Sandbox untrusted actions and use least privilege. Do not expand tool access merely to improve a benchmark score without changing the stated system boundary.

For human-agent systems, evaluate the joint workflow. Record allocation of tasks, user expertise, learning effects, reliance, override behavior, and whether assistance improves the downstream outcome rather than only model output quality.

## 9. Control contamination and evaluation leakage

Audit distinct channels:

- **Training contamination:** Benchmark items, solutions, paraphrases, or source material may appear in pretraining or fine-tuning data.
- **Development leakage:** Prompts, retrieval, tools, thresholds, or scaffolds may be tuned on final evaluation items.
- **Search-time contamination:** An agent or retrieval system may access benchmark solutions during evaluation.
- **Cross-split leakage:** Related entities, duplicates, templates, or labels cross training, development, and test partitions.
- **Judge leakage:** The judge sees system identity, reference provenance, hidden metadata, or information unavailable in the intended use.
- **Human leakage:** Annotators or operators know the condition or expected result and change behavior.

Reduce risk with post-cutoff or private items, source-aware deduplication, held-out task generators, access controls, isolated environments, hidden solutions, and independent final evaluation where appropriate. Test suspiciously high or anomalous performance for shortcuts.

Do not claim that contamination is absent when training data or service internals are unknown. State the audit performed, residual risk, and how contamination would change interpretation. Balance transcript release with privacy, security, and future-test integrity.

## 10. Test protocol sensitivity and robustness

Select sensitivity tests from plausible threats to the claim:

- Prompt wording, formatting, demonstrations, ordering, and context truncation.
- Decoding, attempt count, stopping, retry, voting, and budget.
- Retrieval corpus, chunking, top-k, reranking, and unavailable documents.
- Tool availability, latency, errors, permissions, and scaffold choices.
- Environment version, task order, time, region, and service drift.
- Judge model, rubric, order, reference access, and aggregation.
- Dataset source, language, domain, difficulty, demographic group, temporal shift, and adversarial perturbation.
- Model version, quantization, adapter, and safety policy.

Freeze the sensitivity grid before using it for confirmatory robustness claims. Use development data to select a protocol, then assess the selected protocol on held-out data. Report when rankings or conclusions reverse under plausible settings.

Do not perform an unbounded prompt search on the test set. Report optimization budgets and treat protocol tuning as part of the evaluated method.

## 11. Analyze failures, safety, and subgroup behavior

- Define an error taxonomy from the research question, a pilot, or an independent sample before coding the final results.
- Sample failures and successes systematically; do not showcase only vivid examples.
- Separate item ambiguity, grader error, environment failure, and system error.
- Use blinded multiple coders when subjective classification materially supports a claim; preserve disagreement and adjudication.
- Quantify subgroup results only when group definitions, sample sizes, privacy, and uncertainty support interpretation.
- Search for disparate failure rates, unsafe actions, privacy leakage, security failures, deception, overreliance, or other harms relevant to intended and foreseeable use.
- Preserve redacted evidence for high-risk failures and follow responsible-disclosure constraints.
- Treat red teaming and adversarial tests as scoped searches, not proof that a system is safe when no failure is found.

Keep exploratory error findings separate from prespecified outcome tests. Use discovered patterns to motivate future confirmation.

## 12. Report an auditable evaluation

Release or preserve, subject to rights and safety constraints:

- A machine-readable system and protocol manifest.
- Exact prompts, templates, configs, tools, environment, and model/API identification.
- Dataset or benchmark versions, item IDs, exclusions, contamination audit, and licenses.
- Comparator configurations and tuning or prompt-search budgets.
- Trial-level raw outputs, traces, failures, judge records, and cost or compute records.
- Scoring and analysis code, uncertainty methods, and scripts for tables and figures.
- A README with exact commands, expected outputs, runtime, resources, and known nondeterminism.
- A limitations statement covering construct gaps, coverage, contamination, service drift, and external validity.

When artifacts cannot be shared, state why and provide the strongest safe verification path: gated access, hashes, synthetic fixtures, redacted traces, executable service, or independent audit.

Use `implementation-and-reproducibility.md` to package and clean-room test the evaluation. Use `analysis-and-statistics.md` to estimate effects and uncertainty.

## 13. Pass the AI evaluation gate

Require all of the following for `PASS`:

- Align intended use, construct, benchmark, metric, protocol, and claim.
- Identify the evaluated model and complete system precisely enough to interpret the result.
- Validate data quality, task solvability, grader behavior, and relevant contamination risks.
- Apply fair comparator conditions or explicitly evaluate full-system tradeoffs.
- Measure relevant item, trial, judge, and service variability without pseudoreplication.
- Validate human or model-based judges for the target use.
- Test claim-relevant protocol sensitivity and report reversals.
- Preserve raw outputs, failures, configs, prompts, and analysis provenance.
- Bound claims to the evaluated versions, dates, tasks, populations, and conditions.

Return `CONDITIONAL` when a known weakness narrows but does not invalidate the claim. Return `FAIL` when the benchmark, judge, contamination, or protocol cannot support the central inference. Return `BLOCKED` when access, policy, solvability, or system identity prevents a responsible evaluation.
