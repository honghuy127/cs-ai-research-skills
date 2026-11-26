# Controlled Adversarial Experiment

Attach this plan to the factual [research scope](research-scope.md). Complete it from actual authorization and technical constraints. It does not create authorization by itself.

## Objective and claim

- Research question and threat model:
- Study system and its protective requirements:
- Attack or failure behavior under study:
- Detection, measurement, mitigation, or other documented purpose:
- Supported claim and explicit unsupported extrapolations:
- Decision owner and authority for this target and method:

## Target and containment

- Target models, applications, hosts, and environments:
- Owner-approved target and action set:
- Provider, organization, and legal constraints checked with dates and locators:
- Isolated filesystem, process, account, and network boundaries:
- Permitted credentials, synthetic secrets, and controlled sinks:
- Tools, resources, time, trial, and compute limits:
- Human monitor, stop mechanism, recovery image, and log location:

Do not rest containment solely on model instructions. Record the actual host-enforced boundaries or mark the corresponding control missing.

## Inputs and planned variations

- Adversarial fixtures and their provenance and handling permissions:
- Benign controls matched for task, tools, budget, and scoring:
- Baselines and reference defenses:
- Attack-generation or perturbation procedure:
- Eligible models, seeds, temperatures, retries, and budgets:
- Stop conditions and prohibited expansion:

Preserve necessary attack details in approved storage. Record any input the assistant cannot process instead of silently replacing it with a benign alternative.

## Measurements and integrity

| Requirement | Raw artifact | Independent check | Expected result |
|---|---|---|---|
| Benign-control behavior | | | |
| Attack behavior | | | |
| Baseline or defense comparison | | | |
| Monitor or evaluator coverage | | | |
| Negative and boundary cases | | | |

- Scorer, rubric version, and frozen eligibility rule:
- Denominator, exclusions, missing trials, and repeatability analysis:
- Separate measures of task completion, attack success, protective behavior, and false refusals:
- Injected faults and independently expected detector findings:
- Protected raw logs and immutable or separately retained summaries:

A blocked attack can establish effective protection only when the harness soundly executed the intended test and independently scored the outcome. A model refusal or an implementation failure is not enough by itself.

## Assistant and provider limitations

- Artifacts or methods the assistant cannot access or execute:
- Factual clarifications and unchanged authorized objectives:
- Actual approved changes to environment, provider, or method:
- Original and reduced claims after any scope change:
- Verification performed without the unavailable component:

## Review and release

- Raw results and all attempted trials retained:
- Independent reproduction or review and its result:
- Technical limits that failed or were not exercised:
- Artifacts approved for private storage, sharing, or publication:
- Required redaction, access control, coordinated disclosure, or release hold:
- Final supported claim and remaining uncertainty:
