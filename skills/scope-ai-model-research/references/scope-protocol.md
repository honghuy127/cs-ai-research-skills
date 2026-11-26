# Evidence and Scope Protocol

Use this reference to ground scope decisions in current documents. A research packet communicates facts and constraints. It is not a safety certificate, legal opinion, provider endorsement, or method for changing a classifier's decision.

## Scope dimensions

Answer each question with a source or mark it unknown:

| Dimension | Required distinction |
|---|---|
| Research objective | Capability, reliability, evaluation, data construction, training, deployment, or advice |
| Model roles | Study model, assistant, evaluator, fallback; their providers and deployments may differ |
| Scale claims | Parameter count or compute facts, if known; no assumed threshold for "small" or "frontier" |
| Data | Provenance, permissions, confidentiality, personal data, synthetic status, and intended downstream use |
| Provider outputs | Whether prompts or outputs become training examples, labels, rewards, rubrics, or benchmark items |
| Activity | Code, data collection, experiments, evaluations, external actions, or release |
| Capability change | Concrete measured improvement and any capability that could enable harm outside the test |
| Controls | Relevant safety objectives, access limits, isolation, monitoring, human authority, and recovery |
| Authority | Current provider policy, actual agreement or exception, institutional decision, and applicable law |
| Consequences | Intended users, affected people, possible misuse, unsupported generalization, and remaining uncertainty |

Model size can matter to computational design and deployment. It does not answer what data, tools, targets, or downstream capabilities are involved. The phrase "frontier" must come from a cited governing definition when a classification depends on it. Do not manufacture a numerical cutoff or assert a category from branding.

A capability or reliability goal does not cancel restrictions on how the work is performed. Distinguish evaluating a study system's safeguard from dismantling a host or production safeguard, an authorized sandbox from an external target, an aggregate statistic from personal profiling, and an independent open dataset from provider output reused for training. Authorized research can intentionally probe or defeat a study system's defense to measure it. Do not classify that experiment as prohibited solely because it contains an attack; examine the actual target, authority, effects, and output channel.

## Use current sources

Check these starting points at the time of use, then inspect the applicable product terms and organization-specific agreement. The linked texts and contextual summaries below were checked on 2026-11-26. They do not freeze policy or enumerate every restriction.

| Source | Relevant documented point | Workflow implication |
|---|---|---|
| [Anthropic Usage Policy](https://www.anthropic.com/legal/aup) | Policy applies to inputs and uses, including agent tools. It distinguishes prohibited activity, some authorized security research, high-risk requirements, and certain access programs. A real-time block alone does not establish a usage-policy violation. The policy also addresses guardrail circumvention and some training uses of outputs. | Verify the exact activity rather than inferring permission or violation from a refusal. Use an official program where eligible; never assume research affiliation grants it. |
| [Anthropic model-switching guidance](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-models) | Some disclosed model switches and blocks apply to particular categories, including frontier LLM development. Inputs reviewed include files, connectors, web results, and memory. Feedback channels exist for apparent mistakes. | Inspect the entire evidence packet and disclose actual fallback status. Do not hide context or infer undisclosed model degradation. |
| [OpenAI Usage Policies](https://openai.com/policies/usage-policies/) | Research, development, evaluation, and benchmarking are described as permitted within boundaries. Specific restrictions apply to training alternatives or substitutes from OpenAI outputs, including training data, rubrics, and feedback, unless an applicable exception permits them. Safeguard circumvention and some unsolicited testing are also restricted. | Determine the downstream use of every output before using it in model improvement. A small target model can still be a substitute. Check the exact agreement for exceptions. |
| [Research integrity playbook](https://github.com/honghuy127/cs-ai-research-skills/blob/main/references/research-integrity.md) | Observable integrity checks and independent review do not infer motive or certify scientific validity. | Preserve disclosure, traceability, and independent evidence during model research. |

### Decisions that need current authority

Ask the decision owner for the applicable written rule or approval whenever the work involves:

- model training or preparation of training signals from provider outputs;
- real systems, live targets, external action, or unsolicited testing;
- cyber, biological, chemical, or other dual-use subject matter;
- weapons, surveillance, deception, unauthorized access, or bypassing technical or monitoring controls;
- sensitive, licensed, confidential, or personal data;
- high-impact recommendations or autonomous physical actions;
- distribution of new capabilities or removal of existing safety measures.

This list is a routing aid, not a universal threat classifier. Apply the actual governing rule. Escalation requests a fuller assessment; it is not an automatic refusal. Authorized controlled adversarial work can proceed under [the experiment protocol](controlled-experiments.md), including faithful adversarial fixtures and planned study-target variations. A permitted analysis or synthetic execution may proceed separately from a restricted external action when the remaining method is genuinely authorized and every omitted activity is disclosed.

## A clarification is legitimate only when factual

Make a concise, evidence-based case for the legitimate work rather than a generic declaration of innocence. Show what the experiment measures, why its target and inputs are authorized, how its controls contain effects, and which bounded action the reviewer can take. Use accurate attack terminology when it describes the study, without accusatory language, urgency, demands that safeguards be ignored, or unsupported assertions that no relevant rule applies. A structured explanation can reduce misunderstanding; it cannot guarantee a classification outcome.

A neutral clarification can:

- identify the real study model, assisting service, and deployment context;
- provide exact artifacts, objective, benchmark, metric, and completion check;
- distinguish local fixtures from real targets and aggregate evaluation from personal decisions;
- state authorized data provenance and downstream use limitations;
- preserve safeguards and any meaningful dual-use category;
- identify an applicable written exception or approval without embellishment.

A clarification must not:

- invent small-model status, institutional review, permission, or an official exemption;
- assert that safety rules are irrelevant or request that they be ignored;
- replace precise descriptions with vague "research purposes" when those details materially change the task;
- turn a restricted deliverable into pieces, synonyms, or indirect instructions to achieve the same prohibited outcome;
- promise that a particular phrase, persona, or provider will produce the desired classification;
- transfer undisclosed material to a different reviewer under the assumption that its safeguards will be weaker.

## Triage provider events without inferring motive

Use observable labels separately from interpretations:

| Observable | What can be recorded | What remains unestablished |
|---|---|---|
| Disclosed refusal or block | Exact visible notice, allowed input scope, time, product, host, and disclosed policy link | Violation, undisclosed policy, intent, or whether clarification will help |
| Model fallback | Returned identity if exposed, visible notice, and effective task constraints | Hidden routing logic, common behavior across providers, or intentional degradation |
| Omitted task component | Requirement, delivered artifact, missing observable, and independent check result | Silent withholding, accidental error, or provider causation without further evidence |
| Successful clarification | Revised factual input and permitted output | Permission, classifier bypass, general reliability, or validity of the output |

Retain the original request and the full response record within authorized storage. Do not unnecessarily collect hidden reasoning or repeat prohibited prompts outside the authorized study-target protocol. Approved adversarial cases are experiment data, not permission to attack the assisting service. Use the official feedback or appeal route for apparent false positives. For performance questions, compare authorized benign and matched research tasks with the same tools, budget, and independent completion rubric as described in the [integrity playbook](https://github.com/honghuy127/cs-ai-research-skills/blob/main/references/research-integrity.md).

## Limitations of this skill

Prompt-level scoping cannot establish a legal category, compel an agent to answer, guarantee non-interference by a provider, or detect every relevant policy issue. A separate verifier may share training data, tools, assumptions, or operator errors with the executor. Policy sources change and current agreements may not be public. Human reviewers remain responsible for authorization, safety controls, sensitive data, external actions, and release decisions.
