# Conduct CS and AI Research

[![CI](https://github.com/honghuy127/cs-ai-research-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/honghuy127/cs-ai-research-skills/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10_%7C_3.13-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An agent skill for rigorous computer science and AI research. It guides an AI agent through idea construction, literature synthesis, novelty and feasibility checks, proposals, experimental design, implementation, evaluation, statistical analysis, reproducibility, paper writing, figure and diagram preparation, formatting checks, office document analysis and authoring, presentation slides, peer review, and rebuttals, with evidence discipline enforced at every step.

The skill follows the [Agent Skills specification](https://agentskills.io/specification): a lean `SKILL.md` router loads focused reference playbooks on demand, so an agent only reads the guidance relevant to the current task.

## Design principles

- **Truth states, not vibes.** Every claim moves through an explicit lifecycle (`NOT_ASSESSED → PROPOSED → PLANNED → IMPLEMENTED → SMOKE_TESTED → PILOT_ONLY → EXECUTED → ANALYZED → VERIFIED → REPORTED`), and workflow maturity is tracked separately from the evidential verdict. A pipeline that runs is not a result; a pilot is not confirmatory evidence.
- **Evidence eligibility.** Smoke tests and synthetic plumbing output are structurally barred from becoming scientific evidence. A completed full measured run is only a candidate until it is independently verified.
- **Decisive gates.** Each phase ends with a gate returning `PASS`, `CONDITIONAL`, `FAIL`, `BLOCKED`, or `NOT_ASSESSED`, with evidence and the next decisive action.
- **No fabrication.** Unverifiable content becomes `[CITATION NEEDED]`, `[EVIDENCE NEEDED]`, or `[RESULT PENDING]`, never plausible filler. The audit script fails on unresolved markers in reported deliverables.
- **Humans keep authority.** Submissions, releases, costly runs, participant work, and license or authorship decisions stay with the user.

## Repository layout

| Path | Contents |
|---|---|
| `SKILL.md` | Entry point and router; loads references per task intent |
| `references/` | Nineteen phase playbooks (literature, design, evaluation, analysis, writing, figures and diagrams, formatting, office documents, Markdown documents, presentation slides, GitHub collaboration, review, ethics, orchestration, and more) |
| `scripts/` | Dossier tooling: `research_state.py`, `capture_run.py`, `audit_research.py`, plus the `validate_drawio.py` figure lint, the `check_latex_log.py` build-log checker, the `check_office.py` Office package checker, and the `check_markdown.py` Markdown checker |
| `assets/` | Copy-and-adapt templates: research brief, experiment plan, paper and proposal outlines, figure plan, format checklist, slide deck plan, review template, rebuttal matrix |
| `agents/openai.yaml` | Interface metadata for runtimes that read the OpenAI agent format |
| `tests/` | End-to-end tests for the scripts |

## Installation

### Claude Code

The installed directory name must match the skill name `conduct-cs-ai-research` (the repository name differs), so clone directly into the skills directory:

```bash
# Personal skill (all projects)
git clone https://github.com/honghuy127/cs-ai-research-skills.git ~/.claude/skills/conduct-cs-ai-research

# Project skill (one repository)
git clone https://github.com/honghuy127/cs-ai-research-skills.git .claude/skills/conduct-cs-ai-research
```

Claude Code then triggers the skill automatically for research-shaped tasks; users can also invoke it explicitly via `/conduct-cs-ai-research`.

### Other runtimes

Any runtime implementing the Agent Skills specification can load `SKILL.md` directly. `agents/openai.yaml` supplies display metadata for runtimes that read that format.

## The project dossier

For substantial projects, the skill keeps canonical state in a `.research/` directory inside the research repository (never inside the installed skill):

```text
.research/
├── state.json          # index: stage, questions, deliverables, next actions
├── decisions.md        # append-only decision log
├── evidence.jsonl      # sources with verification depth and claim relations
├── claims.jsonl        # claims with lifecycle state and evidential status
├── experiments.jsonl   # run ledger
└── runs/<run-id>/manifest.json   # immutable per-run provenance
```

The scripts require only Python 3.10+ and the standard library:

```bash
# Initialize a dossier in the current project
python3 scripts/research_state.py init --title "My Study" --owner "me"

# Update index fields; repeated list options replace the stored list
python3 scripts/research_state.py update --next-action "freeze design"

# Record a justified stage transition
python3 scripts/research_state.py transition --stage design --status planned \
  --reason "design frozen" --evidence plan.md --alternative "stay in scoping" \
  --consequence "implementation may start" --owner me --revisit-condition "design change"

# Record provenance for a run that already happened (the script never executes commands)
python3 scripts/capture_run.py --run-id RUN-001 --experiment-id EXP-001 \
  --operator me --started-at 2026-08-14T01:00:00Z --ended-at 2026-08-14T01:30:00Z \
  --phase full --status completed --result-kind measured \
  --command "python train.py" --config cfg.yaml --output results/out.json

# Check structural traceability (exit 1 on any error)
python3 scripts/audit_research.py

# Lint draw.io figure sources (exit 1 on errors; --strict also fails on warnings;
# --min-font-size N sets the minimum label size; --json emits a machine report)
python3 scripts/validate_drawio.py figures/method.drawio

# Check a LaTeX build log for errors, overfull boxes, undefined refs
# (exit 1 on errors; --strict also fails on warnings; --json emits a
# machine report)
python3 scripts/check_latex_log.py build/main.log --max-pages 9

# Check Office packages (.docx, .pptx, .xlsx) for broken media, placeholder
# markers, and macro payloads (exit 1 on errors; --strict also fails on
# warnings; --json emits a machine report)
python3 scripts/check_office.py deck.pptx --strict

# Check Markdown files for unclosed fences, unresolved markers, broken
# relative links, and missing anchors (exit 1 on errors; --strict also
# fails on warnings; --json emits a machine report)
python3 scripts/check_markdown.py README.md docs/guide.md --strict
```

Notes on the audit:

- It certifies structure only, never novelty, statistics, ethics, or scientific validity.
- Records corrected via a `supersedes` field are excluded from auditing; only the head of each supersession chain is checked. A claim that still links superseded evidence gets a warning.
- Deliverables referenced by `reported` claims are automatically scanned for unresolved `[CITATION NEEDED]`, `[EVIDENCE NEEDED]`, and `[RESULT PENDING]` markers; pass additional files with `--scan`.
- Files over 64 MiB are not hashed and must carry an immutable external version (`--file-version PATH=ID` at capture time).
- The manifest's `capture_environment` records where it was written, not where the run executed; pass the run's own hardware and service facts via `--resource`.
- `research_state.py validate` and `status` inspect an existing dossier, `audit_research.py --json` emits a machine report, and every script documents its full flags under `--help`.

## Testing

```bash
python3 -m pip install pytest
python3 -m pytest tests/ -v
```

CI runs the tests on Python 3.10 and 3.13 and link-checks the documentation weekly.

## License

MIT. See [LICENSE](LICENSE).
