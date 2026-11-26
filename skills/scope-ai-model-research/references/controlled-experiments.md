# Controlled Adversarial Experiments

Use this route for AI safety, red-team, attack, poisoning, backdoor, jailbreak, monitor-evasion, and related experiments when their actual environment and authorization permit them. The discipline's name does not establish permission or prohibition. Evaluate the objective, target, data, method, effects, and distribution channel under the current governing rules in [scope-protocol.md](scope-protocol.md).

This protocol preserves legitimate controlled experiments. It does not authorize unsafe external action or obligate an assisting provider to process a particular artifact.

## Distinguish the study system from the host

An attack directed at a study model, test defender, or purpose-built target can be the legitimate subject of an experiment. An instruction that tries to take control of the assisting agent, override its provider, disable production monitoring, or expand permissions is a different event. Preserve this distinction even when both use the same attack text.

A research goal can intentionally vary a study system's safeguards to measure their contribution when the approved design covers that variation. This does not imply permission to disable safeguards in the host, on unrelated systems, or during deployment. Likewise, a low refusal rate is not inherently bad performance on a benign control, and a high refusal rate is not inherently good performance on an attack case. Score task success and protective behavior separately with an independent rubric.

Examples that may fit this route, subject to actual authority and controls, include:

- evaluating adversarial prompts against owned or explicitly permitted study models;
- injecting synthetic sabotage, data leakage, or evaluator failures into isolated research fixtures;
- measuring monitor coverage against controlled attempts inside a sandbox;
- studying poisoning or backdoor detection with owned models, documented data, and synthetic triggers;
- testing purpose-built cyber or agent targets with the operator's explicit scope and rules;
- analyzing previously collected adversarial artifacts under their license and handling terms.

## Bound the experiment, not its scientific validity

Record each of these decisions in [the experiment plan](../assets/controlled-experiment.md) before execution:

1. **Objective and estimand.** Name the attack behavior, defensive property, measured outcome, and scientific claim. State whether the goal is detection, measurement, mitigation, or another documented research purpose.
2. **Target and authority.** Identify the study model or system, operator authorization, provider and organizational constraints, and permitted experiment bounds. For a real or target-like environment, record the exact owner-approved target and action set rather than relying on a general red-team label.
3. **Experiment budget.** Freeze eligible cases, attack-generation method, trial count, model and tool budgets, seeds, and stopping conditions. Planned variations of the study target's attack input are experiment execution. Do not repurpose them as ad hoc attempts to make the assisting provider bypass its own constraints.
4. **Technical containment.** Use the strongest available host-enforced boundary for candidate code and study agents: an owned or purpose-built environment, disposable filesystem, approved credentials or synthetic canaries, restricted tools and network, bounded resources, and a safe stop mechanism. Use a controlled sink instead of a real exfiltration destination. Keep provider systems outside the attack target unless the governing authorization explicitly includes them. Instructions alone are not containment.
5. **Artifact handling.** Preserve the actual adversarial fixtures needed for the experiment when their storage and use are authorized. Do not silently replace an attack with an easier benign prompt, weaken a defender or baseline, omit unsuccessful trials, or relax the metric to obtain a preferred result. Use private authorized storage when an artifact is unsuitable for publication.
6. **Independent evaluation.** Freeze raw-result eligibility and scoring before outcomes. Include benign and attack controls, established baselines, counterexamples, and repeatability checks. Use executable tests or an independently controlled scorer where possible. Do not infer a missing attack or safety property from an assistant's self-report.
7. **Release controls.** Separate permission to perform an experiment from permission to publish its inputs, generated outputs, working exploit material, or capability improvements. Apply the actual disclosure, export, and access requirements without substituting an inadequate experiment for a restricted report.

No control guarantees that a dual-use experiment is safe or provider-compliant. Choose controls from the concrete effects and governing requirements, not this checklist alone.

## Assist without silently weakening the research

When a request is authorized, help preserve the complete intended task:

- draft the protocol, implement the controlled harness, inspect real and negative-control results, and diagnose failures at their actual technical cause;
- disclose any attack cases, source prompts, tools, or scoring dimensions that the assistant cannot process in the current environment;
- distinguish an unavailable provider capability from a scientifically justified change to the task;
- ask before reducing the experimental scope, and record the original and reduced claim when a reduction occurs;
- keep the raw target outputs, rejected cases, defensive failures, and excluded trials needed for an independent audit;
- use synthetic targets or non-operational analogs when they preserve the measured property and the claims are limited accordingly, not merely as a way to avoid accurate descriptions.

Do not transform every dual-use request into an abstract discussion when the authorized work needs implementation or execution. Conversely, do not turn a discussion of possible attacks into live exploitation, unauthorized target contact, destructive action, or release of restricted artifacts.

## When the assisting service cannot participate

Record which part of the authorized packet caused the disclosed limitation. Check whether a factual clarification about the existing target, authority, fixtures, and scientific goal resolves a misunderstanding without changing the activity. Never hide the adversarial purpose or replace a necessary attack fixture with a benign one just to make the packet pass.

If the service remains unavailable, options require independent authorization:

- ask for provider feedback, review, or an eligible verification program;
- obtain the decision owner's approved change to the method, environment, or approved service;
- perform an independently authorized local analysis of artifacts that are permitted for local use, with appropriate containment and no unauthorized external transmission;
- narrow the actual deliverable and its claims while preserving traceability of omitted requirements.

Choosing a local runtime or another provider requires its own permission, resource, confidentiality, and safety review. It is not a way to obtain a prohibited result. A successful clarification establishes neither a classifier bypass nor a valid experimental result.

## Report controls and results separately

Report the protocol, authority boundary readers may disclose, containment actually enforced, cases tested, raw scoring method, and failed trials. Compare benign and attack controls under matched budgets. Do not cherry-pick the passing trial, count a failed implementation as a successful defense, or claim real-world safety from synthetic fixtures alone. Explicitly record any assistant limitations or substitutions so they do not become hidden changes to the experiment.
