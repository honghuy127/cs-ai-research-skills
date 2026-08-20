# Methodology Sources and Design Provenance

Use this register to verify the principles and live rules behind the research skill. URLs were checked on 2026-08-14; the Markdown and GitHub rows were added on 2026-08-21. Re-open every source before relying on it, record the access date, and prefer the current official version over this snapshot.

## Contents

1. Apply the source hierarchy
2. Separate stable principles from volatile rules
3. Use official standards and policies
4. Use scholarly discovery services
5. Verify proposal rules at the source
6. Record public-skill design provenance
7. Reject unsafe defaults
8. Record and refresh a methodology source

## 1. Apply the source hierarchy

Use sources in this order:

1. exact current solicitation, venue instructions, law, policy, or standard governing the project;
2. current official agency, standards-body, society, or repository documentation;
3. primary research papers, registered protocols, datasets, and official code or artifacts;
4. high-quality public skills and workflow repositories for procedural inspiration only;
5. informal explanations only as discovery aids.

Never let a public skill override a governing policy or substitute for primary scientific evidence. Treat repository popularity as a discovery signal, not proof of methodological validity.

## 2. Separate stable principles from volatile rules

| Treat as relatively stable | Treat as volatile and re-fetch for every project |
|---|---|
| Trace claims to evidence and exact locators | Deadlines, time zones, eligibility, tracks, and award ranges |
| State hypotheses and proposed work as uncertain | Page limits, templates, fonts, attachments, and portal fields |
| Match the design and evaluation to the contribution type | Anonymity, authorship, AI-use, disclosure, and review policies |
| Map claims to experiments, rivals, and falsifiers | Budget, salary, indirect-cost, travel, and cost-share rules |
| Preserve raw inputs, versions, run manifests, and decisions | Models, APIs, datasets, benchmarks, leaderboards, and prices |
| Keep humans at authority, ethics, cost, and release gates | Licenses, terms of use, data-access, privacy, and security rules |
| Protect confidential submissions and participant data | Standards under revision, jurisdictional law, and institutional policy |
| Use a lean router with progressively loaded references | State of the art, novelty landscape, and current accepted work |

When a stable principle conflicts with a current governing rule, stop and resolve the conflict rather than silently choosing one.

## 3. Use official standards and policies

| Source | Current official URL | Use |
|---|---|---|
| Agent Skills specification | https://agentskills.io/specification | Keep metadata concise, load SKILL.md on trigger, and load focused references on demand |
| ACM SIGSOFT Empirical Standards | https://www2.sigsoft.org/EmpiricalStandards/ | Select method-specific quality criteria for empirical software-engineering work |
| SIGSOFT standards catalog | https://www2.sigsoft.org/EmpiricalStandards/docs/standards | Open the standard matching the actual study design; do not apply every checklist indiscriminately |
| PRISMA 2020 | https://www.prisma-statement.org/prisma-2020 | Report a qualifying systematic review transparently |
| PRISMA 2020 checklist | https://www.prisma-statement.org/prisma-2020-checklist | Verify the current checklist and extensions appropriate to the review type |
| NeurIPS paper checklist | https://neurips.cc/public/guides/PaperChecklist | Check claims, reproducibility, experiments, uncertainty, compute, ethics, assets, and impacts; re-open the target year's venue instructions |
| ACL Rolling Review form | https://aclrollingreview.org/reviewform | Understand current review dimensions for relevant NLP submissions; treat the form as venue-volatile |
| ACM artifact review and badging | https://www.acm.org/publications/policies/artifact-review-and-badging-current | Plan availability, functionality, reproducibility, and reuse claims for research artifacts |
| ACM research involving human participants | https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects | Check disclosure and ethical expectations for human-participant research |
| NIST AI Risk Management Framework | https://www.nist.gov/itl/ai-risk-management-framework | Structure voluntary AI-risk analysis where applicable; verify the current revision because NIST announced revision activity in 2026 |
| CRediT taxonomy | https://credit.niso.org/ | Describe contributor roles without treating the taxonomy as an authorship decision rule |
| CommonMark specification | https://spec.commonmark.org/ | Anchor the portable Markdown core and delimiter rules that all renderers share |
| GitHub Flavored Markdown specification | https://github.github.com/gfm/ | Verify extension behavior (tables, task lists, autolinks, strikethrough) beyond CommonMark |
| GitHub writing and formatting documentation | https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax | Check GitHub-only rendering rules such as alerts, math, heading anchors, relative links, and line breaks |
| GitHub CLI manual | https://cli.github.com/manual/ | Verify gh command syntax and flags against the current manual instead of memory |

Use these as starting points, not a universal bundle. Select only the standards that match the jurisdiction, venue, study method, and deliverable.

## 4. Use scholarly discovery services

| Service | Official documentation | Proper role |
|---|---|---|
| Crossref REST API | https://www.crossref.org/documentation/retrieve-metadata/rest-api/ | Verify DOI metadata and discover linked records |
| OpenAlex | https://help.openalex.org/ | Discover works, authors, institutions, concepts, and citation relationships |
| Semantic Scholar API | https://api.semanticscholar.org/api-docs/ | Discover papers and citation links subject to documented coverage and rate limits |
| arXiv API | https://info.arxiv.org/help/api/ | Discover and track preprint records and versions |
| DBLP search API | https://dblp.org/faq/How+to+use+the+dblp+search+API.html | Discover computer-science bibliographic records |

Use discovery metadata to locate sources. Open the primary paper, proceedings record, dataset, or artifact before supporting a substantive claim. Record platform coverage, query, filters, date, cursor or pages, and deduplication decisions.

## 5. Verify proposal rules at the source

| Source | Current official URL | Use |
|---|---|---|
| NSF Proposal & Award Policies & Procedures Guide landing page | https://www.nsf.gov/policies/pappg | Locate the currently effective guide and supplements, then pair them with the exact solicitation and amendments |
| NIH application guide | https://grants.nih.gov/grants-process/write-application/how-to-apply-application-guide | Locate the current form and instruction set, then pair it with the notice of funding opportunity and policy notices |

Do not encode agency rules from these landing pages into a reusable skill. Parse the exact live call, incorporated documents, amendments, FAQs, and institutional policy for each proposal.

## 6. Record public-skill design provenance

The following public repositories informed workflow design. Reuse principles after independent verification; do not copy their numeric thresholds or domain assumptions.

| Public source | URL | Adopt | Guard or reject |
|---|---|---|---|
| Anthropic skill creator | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md | Lean routing, imperative instructions, progressive disclosure, validation | Avoid copying templates without adapting them to this state model |
| K-Dense Scientific Agent Skills | https://github.com/K-Dense-AI/scientific-agent-skills | Evidence boundaries, hypothesis alternatives, experimental design checks, grant and review decomposition | Verify every cited rule; avoid treating a broad collection as one mandatory workflow |
| luwill research proposal skill | https://github.com/luwill/research-skills/blob/main/research-proposal/SKILL.md | Requirements-first drafting, verified literature, outline approval, section-level audit | Preserve its rejection of hard citation quotas and one-shot proposal drafting |
| Hermes research paper writing skill | https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/SKILL.md | Claim-to-experiment mapping, strong and compute-matched baselines, ablations, uncertainty, and experiment logs | Do not copy a monolithic workflow; load only the relevant phase |
| AutoResearchClaw | https://github.com/aiming-lab/AutoResearchClaw | Gated state transitions, rollback, cost guardrails, checksums, and versioned artifacts | Do not default to unattended end-to-end research or bypass human authority gates |
| AI4S Skills | https://github.com/ai4s-research/ai4s-skills | Resumable runs, provenance, explicit handoffs, and reusable scientific procedures | Reject fixed citation-volume requirements and simulated-results defaults |
| Academic Research Agent Skill | https://github.com/ngtiendong/Academic-Research-Agent-Skill/blob/main/SKILL.md | Lean lifecycle routing, categorical gates, cheapest falsifier, minimum informative artifact | Do not replace evidence-backed judgment with automatic numeric ranking |
| BESSER research paper review | https://github.com/BESSER-PEARL/research-agent-skills/blob/main/research-paper-review/SKILL.md | Paper-type calibration, structured review dimensions, and numeric consistency checks | Narrow the trigger, preserve confidentiality, and follow the current venue's verdict policy |
| draw.io diagram skill | https://github.com/Agents365-ai/drawio-skill | Direct `.drawio` XML authoring conventions, draw.io desktop CLI binary resolution and export flags, structural lint before rendering | Keep only what paper figures need; avoid the broad operations-diagramming script surface and its extra dependencies |
| Research draw.io diagram builder | https://github.com/Will-hxw/drawio-diagram-builder-skill | Editable-source-first policy, style extraction from reference figures, and render-then-inspect verification loops | Do not adopt mandatory defect-count quotas, network-dependent embedded previews, or hard browser-automation requirements |
| LaTeX document skill | https://github.com/ndpvt-web/latex-document-skill | Recorded compile commands, TeX log triage of overfull boxes and undefined references, and page-image rendering before verdicts | Do not copy its pip auto-install script behavior or broad non-research document scope |
| PDF proof | https://github.com/metedata/pdf-proof | Locate-then-crop evidence screenshots instead of text-only claims about visual material | Keep its render-as-evidence principle without the PyMuPDF dependency or the HTML proof-page deliverable |
| Anthropic pdf skill | https://github.com/anthropics/skills/tree/main/skills/pdf | Separation of structural PDF checks from visual review | Proprietary license: reuse concepts only, never copy code |
| Anthropic docx skill | https://github.com/anthropics/skills/tree/main/skills/docx | OOXML as inspectable zip/XML parts, template-first Word generation, and tracked-change-aware edits | Proprietary license: reuse concepts only, never copy code |
| Anthropic pptx skill | https://github.com/anthropics/skills/tree/main/skills/pptx | Structural validation plus rendered-thumbnail verification before delivery | Proprietary license: reuse concepts only, never copy code |
| Anthropic xlsx skill | https://github.com/anthropics/skills/tree/main/skills/xlsx | Formula-aware spreadsheet reading and clean tabular conventions | Proprietary license: reuse concepts only, never copy code |
| Anthropic doc-coauthoring skill | https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring | Structured co-authoring passes that separate content edits from commentary | Proprietary license: reuse concepts only, never copy code |
| Beamer LaTeX presentation class | https://ctan.org/pkg/beamer | Theme, overlay, handout, and appendix conventions for LaTeX slide decks | Verify themes and packages against the installed TeX distribution; never invent package names |
| python-pptx documentation | https://python-pptx.readthedocs.io/ | Reproducible `.pptx` generation and patching from recorded scripts | Third-party dependency, not bundled with this skill; verify API behavior per installed release |
| Pandoc | https://pandoc.org/ | Markdown or LaTeX to docx conversion with `--reference-doc` templates | Verify flags per installed version |
| LibreOffice | https://www.libreoffice.org/ | Headless Office-to-PDF export that enables rendered slide and document verification without Office | Verify binary names and flags per install |
| Public PPT generator skills, for example sunbigfly/ppt-agent-skills | https://github.com/sunbigfly/ppt-agent-skills | Outline-first storyboarding and rendered visual QA loops | Reject network, image-generation, and multi-tool pipeline dependencies; adopt no fixed design quotas |

## 7. Reject unsafe defaults

Never import these patterns into the skill:

- a minimum citation count, fixed recent-citation percentage, prestige filter, or paper-count stopping rule;
- simulated, plausible, illustrative, or synthetic scientific results presented as evidence;
- an automatic novelty score or a ranking that hides unresolved evidence;
- static venue, funder, API, model, dataset, benchmark, price, or legal rules;
- memory-only citations, invented identifiers, or substantive claims supported only by metadata;
- unattended costly runs, data collection, submission, disclosure, or release;
- a single universal checklist applied regardless of contribution and study design.

Synthetic data may test software plumbing when clearly labeled, isolated from scientific conclusions, and permitted by the research contract. It must never satisfy an empirical gate or become a reported result.

## 8. Record and refresh a methodology source

For every governing methodology source, record:

- title, authority, canonical URL, version or effective date, and access date;
- project, phase, method, venue, or jurisdiction to which it applies;
- exact section, page, checklist item, or locator used;
- whether the item is stable guidance or a volatile rule;
- the decision or artifact it changed;
- conflicts, superseding documents, and next refresh date.

Before a gate or deliverable:

1. re-open volatile sources and inspect amendments or revision notices;
2. compare the source's scope with the actual method and submission regime;
3. update the compliance or evidence record with an exact locator;
4. record any changed interpretation in decisions.md;
5. mark the affected gate BLOCKED when authority or current text cannot be verified.

This register documents provenance. It does not freeze the internet, replace professional ethics review, or confer compliance by itself.
