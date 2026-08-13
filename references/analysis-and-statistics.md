# Analysis and Statistics

## Contents

1. Reconstruct the analysis contract
2. Freeze and audit analysis inputs
3. Identify the estimand and dependence
4. Describe the data before inference
5. Choose effect sizes in meaningful units
6. Quantify uncertainty
7. Select tests or statistical models
8. Handle multiple analyses and adaptive decisions
9. Analyze ML, benchmark, and stochastic-system results
10. Perform robustness and sensitivity analysis
11. Conduct systematic error and qualitative analysis
12. Separate confirmatory, exploratory, and deviating analyses
13. Interpret null and negative results
14. Build honest tables and figures
15. Preserve analysis provenance and pass the gate

## 1. Reconstruct the analysis contract

Read the frozen experiment plan, `experimental-design.md`, and `cs-ai-evaluation.md` when applicable. Do not begin with whichever statistical test is familiar.

For each primary result, recover:

- Claim and research-question IDs.
- Confirmatory, exploratory, descriptive, or diagnostic status.
- Population, conditions, and scope of generalization.
- Unit of allocation, observation, repeated measurement, and analysis.
- Outcome, exposure or treatment, comparator, estimand, and practical threshold.
- Sampling, split, blocking, stratification, cluster, and pairing structure.
- Planned exclusions, missing-data rules, stopping rule, and analysis method.
- Variation sources to quantify and assumptions required for inference.

Stop and record a deviation if the plan is absent, ambiguous, contradicted by execution, or unable to answer the claim. Do not reconstruct an apparently prespecified analysis from observed results.

## 2. Freeze and audit analysis inputs

Analyze immutable raw outputs through versioned transformations.

1. Enumerate expected run, participant, item, group, and trial IDs from the frozen design.
2. Reconcile expected and observed records, including failures, attrition, retries, and duplicates.
3. Validate schemas, types, ranges, units, timestamps, uniqueness, joins, and referential integrity.
4. Re-run leakage, split-disjointness, label, and grader checks before promotion to `ANALYZED`.
5. Apply prespecified exclusions through a versioned table containing ID, rule, reason, decision time, and decision owner.
6. Preserve missingness indicators and distinguish missing, invalid, censored, failed, and not-applicable outcomes.
7. Verify that preprocessing, thresholds, prompt selection, and model selection did not use final outcomes improperly.
8. Hash or identify the input set and store it in the analysis manifest.

Do not silently drop failed runs, outliers, inconvenient subgroups, ambiguous items, or incomplete participants. Run any post-outcome exclusion as a labeled sensitivity analysis unless the frozen rule clearly applies.

Use synthetic values only to test analysis plumbing. Keep them marked ineligible as scientific evidence.

## 3. Identify the estimand and dependence

Write the target quantity in words and, when helpful, notation before estimating it. Examples include:

- Mean paired change in task success for the same items.
- Difference in population error rates under a defined sampling process.
- Median latency ratio under a fixed workload and hardware environment.
- Probability that a randomly sampled user prefers system A to system B.
- Conditional treatment effect for a prespecified subgroup.
- Expected success over both sampled benchmark items and stochastic trials.

Then identify dependence:

- Pair observations evaluated on the same item, user, task, fold, environment, or time point.
- Model repeated measurements within participants, repositories, documents, conversations, or sites.
- Treat cross-validation folds, multiple completions, checkpoints, and repeated seeds as dependent when they share data or training history.
- Account for stratification, blocking, matching, weighting, censoring, and adaptive sampling.
- Use the independent sampling or assignment unit as the basis for inference; do not inflate sample size with technical replicates.

Change the model, resampling scheme, or scope of inference when dependence cannot be estimated credibly.

## 4. Describe the data before inference

Report the flow from eligible units to analyzed units:

- Counts sampled, assigned, attempted, completed, failed, excluded, and missing by condition.
- Exposure, outcome, and covariate distributions in domain-relevant units.
- Cluster sizes, repeated-measure counts, class balance, task difficulty, and subgroup coverage.
- Runtime, token, action, compute, and cost distributions when they affect the claim.
- Floor, ceiling, censoring, truncation, heavy tails, multimodality, and outliers.
- Baseline balance for randomized or matched studies without using balance tests as proof that allocation succeeded.

Visualize raw or lightly summarized distributions when practical. Use tables for exact values and plots for shape. Do not let a mean or median conceal instability, bimodality, subgroup reversal, or catastrophic failures.

## 5. Choose effect sizes in meaningful units

Lead with an effect that answers the decision in interpretable units. Add standardized measures only when they aid comparison across scales.

| Outcome or design | Prefer when appropriate | Guardrail |
|---|---|---|
| Continuous outcome | Mean or median difference, paired change, ratio, or percent change | Report scale, denominator, and distribution; ratios become unstable near zero |
| Binary outcome | Risk difference, risk ratio, paired discordance, or odds ratio | Do not present an odds ratio as a risk ratio; include base rates |
| Count or exposure-time outcome | Rate difference or rate ratio | Model exposure and overdispersion where relevant |
| Ordered or heavy-tailed outcome | Probability of superiority, rank-biserial effect, quantile difference, or robust location effect | Explain the population interpretation rather than reporting a test statistic alone |
| Correlation or association | Correlation, slope, mutual-information estimate, or model contrast | Do not imply causation; report range restriction and uncertainty |
| Prediction or benchmark metric | Paired metric difference, relative error reduction, calibration difference, or task-level win rate | Define aggregation and preserve item-level pairing |
| Efficiency | Latency, throughput, memory, energy, compute, or cost difference/ratio | Fix or model hardware, workload, concurrency, and quality level |
| Equivalence or non-inferiority | Effect estimate relative to a prespecified margin | Set and justify the margin before observing the result |

- Report absolute and relative effects when each answers a different practical question.
- Prefer raw-unit effects over standardized effects for stakeholder decisions.
- Define the sign so a positive value has one consistent meaning.
- Report subgroup effects only when supported by design and sample coverage.
- Avoid ranking methods solely by point estimate when uncertainty and cost make them practically indistinguishable.

## 6. Quantify uncertainty

State what each interval or error bar varies over. Distinguish variation from sampled items, participants, data splits, initialization, model sampling, annotators, judges, environments, services, and measurement error.

- Use confidence intervals, credible intervals, prediction intervals, standard errors, or distributional summaries according to the inferential goal.
- Label standard deviation, standard error, interval level, and calculation method explicitly.
- Preserve pairing and clusters in bootstrap, permutation, jackknife, or other resampling procedures.
- Use cluster or hierarchical resampling when observations within an entity are dependent.
- Model multiple variance components when the claim generalizes over both items and stochastic trials or over participants and tasks.
- Separate Monte Carlo error from uncertainty about the target population.
- Use asymmetric or transformed intervals for bounded, skewed, ratio, rare-event, and heavy-tailed quantities when appropriate.
- Check interval coverage by simulation when using a novel or complex estimator; keep simulation outputs methodological, not scientific evidence.
- Report uncertainty around differences or contrasts directly rather than inferring a difference from overlap of separate error bars.

Do not attach a narrow interval based only on technical repeats to a claim about a broad population of tasks or users.

## 7. Select tests or statistical models

Choose a method that matches the estimand, assignment or sampling design, outcome distribution, and dependence structure.

### Apply design-aware choices

- Use paired analyses for the same items, participants, seeds, or environments when pairing is valid.
- Use regression, mixed, generalized, survival, time-series, or other structured models when covariates, clusters, censoring, or repeated measures require them.
- Use randomization or permutation inference that mirrors the actual assignment or exchangeability structure when appropriate.
- Use robust or distribution-free procedures when their target and assumptions match the question; do not choose them merely because a normality test rejected.
- Use Bayesian models when priors, likelihood, and posterior quantities are justified and useful; inspect prior and posterior predictive behavior.
- Use equivalence, non-inferiority, or interval-based decision procedures for claims about similarity or acceptable degradation.
- Account for sequential looks or adaptive stopping with a valid sequential design.

### Check and disclose assumptions

- Examine residual structure, functional form, variance, dependence, exchangeability, censoring, overlap, positivity, and influential observations as applicable.
- Distinguish assumptions that can be diagnosed from assumptions that require domain justification.
- Report how violations change estimates through alternative models or sensitivity analysis.
- Avoid automatic test-selection pipelines driven by preliminary assumption-test p-values.

### Interpret evidence without p-value worship

- Report effect estimates and uncertainty whether or not a threshold is crossed.
- Treat a p-value as a design-conditional compatibility measure, not the probability that a hypothesis is true or the probability the result occurred by chance.
- Do not equate `p > alpha` with no effect, equivalence, or evidence for the null.
- Do not equate `p < alpha` with practical importance, correct measurement, or a generalizable claim.
- Report exact values when useful and avoid decorative significance stars as the main result.

## 8. Handle multiple analyses and adaptive decisions

Define the inferential family from the scientific question, not from every number in the project.

1. Identify primary outcomes, contrasts, time points, subgroups, and model specifications.
2. Separate confirmatory families from exploratory screening.
3. Control family-wise error when any false positive in a small confirmatory family is costly.
4. Control false discovery rate for a justified discovery set when tolerating some false discoveries is acceptable.
5. Use hierarchical testing, gatekeeping, shrinkage, or multilevel modeling when hypotheses have structure.
6. Report all tested members of the family and the adjustment method.
7. Record unplanned looks, model searches, subgroup searches, prompt searches, and metric searches as researcher degrees of freedom.

Do not apply a blanket correction to unrelated descriptive outputs. Do not avoid adjustment by reporting only the favorable analysis. When selection was extensive or unrecorded, downgrade the result to exploratory and seek independent confirmation.

## 9. Analyze ML, benchmark, and stochastic-system results

- Keep the final test set outside feature, prompt, model, hyperparameter, threshold, and stopping-rule selection.
- Use nested resampling or a separate development process when estimating performance after model selection.
- Compare systems on matched items and conditions; analyze item-level or episode-level differences when available.
- Distinguish variability across test items from variability across training or generation trials.
- Do not treat folds from one cross-validation partition as independent replicates. Aggregate or model repeated resampling with its dependence intact.
- Include all frozen seeds and trials. Do not report the best seed or checkpoint unless best-of-n selection is part of the declared method and its budget is included.
- Report baseline and proposed-method tuning budgets and selection criteria.
- Estimate uncertainty for the actual aggregate metric, including pass@k, macro/micro averages, ranking metrics, and composite scores.
- Avoid arbitrary averaging across datasets with incompatible scales or importance. Report per-dataset results and justify any summary weighting.
- Account for benchmark reuse, leaderboard selection, and repeated test submissions when interpreting small improvements.
- Analyze failures, invalid outputs, timeouts, refusals, and missing scores under the frozen rule rather than only among successful cases.

For hosted or drifting systems, include time, endpoint, and model-version uncertainty in the scope. Do not pool incompatible service versions as if they were exchangeable repeats.

## 10. Perform robustness and sensitivity analysis

Choose checks that target assumptions capable of changing the conclusion:

- Alternative defensible outcome definitions, metrics, thresholds, or aggregation rules.
- Alternative missing-data, censoring, failure, outlier, and exclusion treatments.
- Alternative split, sampling, matching, weighting, or clustering choices.
- Alternative model specifications, priors, transformations, and dependence structures.
- Different seeds, trials, task subsets, time windows, environments, judges, prompts, or protocol settings.
- Negative controls, placebo outcomes, falsification tests, or benchmark sanity checks.
- Influence analysis for individual items, participants, datasets, sites, or runs.
- Distribution shifts and prespecified subgroups relevant to generalization.
- Bounds for unmeasured confounding, label error, contamination, or judge error when point identification is not credible.

Designate one primary analysis. Present sensitivity results as a structured comparison, not a search for the specification that preserves significance. Explain conclusion changes and identify the assumption responsible.

Do not claim robustness merely because many minor variants agree while the main construct or sampling threat remains untested.

## 11. Conduct systematic error and qualitative analysis

Use error analysis to explain behavior, not to decorate aggregate results.

1. Define the sampling rule for cases before selecting examples: random, stratified, high-loss, disagreement, success/failure pair, or another justified scheme.
2. Build a coding taxonomy from theory, pilot work, or an explicitly exploratory pass.
3. Blind coders to system or condition when feasible and relevant.
4. Record coder training, overlap, disagreements, adjudication, and revisions to the codebook.
5. Report category denominators and uncertainty when making quantitative prevalence claims.
6. Preserve co-occurring codes when failure modes are not mutually exclusive.
7. Distinguish system errors from ambiguous items, invalid references, grader defects, environment failures, and data problems.
8. Use quotations or examples as evidence for an interpretation only with context and privacy protection; do not treat cherry-picked examples as frequency evidence.

For interpretive qualitative analysis, apply the chosen methodology's standards for reflexivity, credibility, negative cases, saturation or information power, and audit trail. Do not force agreement coefficients onto a method whose aim is interpretive plurality.

## 12. Separate confirmatory, exploratory, and deviating analyses

Label every table, figure, and claim internally as:

- `CONFIRMATORY`: Prespecified hypothesis, outcome, population, and analysis followed without material post-outcome change.
- `EXPLORATORY`: Pattern or hypothesis discovered using the analyzed data.
- `DESCRIPTIVE`: Summary of the observed sample without a confirmatory population claim.
- `SENSITIVITY`: Alternative assumption or specification testing a primary conclusion.
- `DEVIATION`: Planned analysis changed or became infeasible.

For each deviation, record what changed, why, when, what outcomes were visible, and how claim eligibility changed. Present the planned result when computable alongside the revised analysis.

When exploratory work produces a promising claim, reserve new data, use an untouched holdout, or plan a future confirmatory study. Do not erase the discovery path.

## 13. Interpret null and negative results

- Report the effect estimate, interval, design sensitivity, data quality, and relevant failure modes.
- Distinguish evidence of negligible effect from absence of evidence. Use a justified equivalence margin or model comparison when supporting a null claim.
- State which effects remain compatible with the data and which the study rules out.
- Examine floor, ceiling, contamination, manipulation failure, low reliability, inadequate exposure, and undercoverage before interpreting a negative outcome scientifically.
- Separate technical failure from an informative failure of the method or hypothesis.
- Preserve and report negative outcomes when they answer a credible question, bound a method, reveal a failure regime, or correct a community expectation.
- Avoid retrospective claims that the study was “underpowered” solely because the result was not favorable.

## 14. Build honest tables and figures

- Generate publication values from analysis artifacts, not manual transcription.
- Show sample sizes, units, metric direction, aggregation, interval type, and variation source.
- Use consistent precision justified by measurement and uncertainty.
- Display distributions or paired changes when they reveal information hidden by summaries.
- Use common axes and scales for comparisons; disclose truncation, logarithmic transformation, smoothing, and omitted values.
- Avoid dual axes, area or volume encodings, and color choices that exaggerate small differences or impair accessibility.
- Show missing, failed, and censored observations where relevant.
- Keep exploratory plots from masquerading as confirmatory tests.
- Give every table and figure a stable ID linked to input run IDs, analysis code, configuration, and output path.

Make captions interpretable without overstating causality or generalization.

## 15. Preserve analysis provenance and pass the gate

Create an analysis manifest containing:

```text
Analysis ID and status:
Claim and research-question IDs:
Frozen plan version:
Input run IDs and hashes:
Inclusion, exclusion, and missing-data decisions:
Estimand and analysis population:
Code commit and dirty-state reference:
Environment and package lock:
Resolved analysis configuration:
Randomness or resampling seeds:
Generated data, table, and figure paths/hashes:
Deviations and exploratory additions:
Verifier and verification result:
```

Use `scripts/audit_research.py` for structural traceability when the dossier is enabled, but do not treat a clean structural audit as certification of statistical or scientific validity.

Require all of the following for `PASS`:

- Analyze the correct frozen run set with complete failure and exclusion accounting.
- Match the estimand, effect measure, model, test, and resampling to the design and dependence.
- Report interpretable effects and appropriate uncertainty, not thresholded p-values alone.
- Handle multiplicity and adaptive decisions transparently.
- Perform claim-relevant robustness checks and disclose conclusion reversals.
- Separate confirmatory, exploratory, descriptive, sensitivity, and deviating work.
- Trace every reported value, table, and figure to immutable inputs and versioned code.
- Bound conclusions to the supported population, conditions, versions, and time horizon.

Return `CONDITIONAL` when a bounded assumption or missing component narrows the claim. Return `FAIL` when dependence, leakage, selection, missingness, or analysis choices invalidate the central inference. Return `BLOCKED` when required raw outputs, design records, or authorization are unavailable.
