# Manuscript Revision for Readability, Explanation, and Consistency

## Contents

1. Establish the revision contract
2. Diagnose with measurements
3. Build the insight backbone and relocation ledger
4. Rewrite the main text for readers
5. Spend freed space on explanation
6. Run a consistency read
7. Revise the appendix
8. Maintain audits, artifacts, and records
9. Verify every pass
10. Deliver the revision

## 1. Establish the revision contract

Use this playbook when a drafted manuscript must become easier to read, especially for non-native readers, more argumentative in register, better explained, or internally consistent. It complements [paper-writing.md](paper-writing.md), which governs what may be claimed and how venue-grade prose reads, and [paper-formatting.md](paper-formatting.md), which governs the rendered layout. Load both during a revision.

Record before editing:

- Which goals are in scope: readability, register, explanation, consistency, or appendix structure.
- The frozen evidence. A revision changes presentation only; it creates no result, number, or claim beyond what the evidence supports.
- The page budget and which statements the venue exempts from it, taken from the current official rules.
- Author-attested or legally sensitive text, such as AI-use, ethics, or conflict statements, which stays untouched unless the authors ask.
- The relocation rule: nothing leaves the paper as a whole. Detail moves to the appendix. Scope limits and caveats stay in the main text.
- Every artifact bound to the manuscript, such as supplement manifests that hash the source, portal abstract copies, and prose-number audits.

Work on a branch. Treat commits, merges, pushes, and submissions as separate external actions that need explicit authority.

## 2. Diagnose with measurements

Measure before rewriting, so that "too dense" becomes a concrete target. Strip floats, math, citations, and commands. Split sentences on terminal punctuation followed by a capital letter, and treat paragraph breaks and run-in headings as boundaries so that they do not create false long sentences.

| Measurement | What it reveals | Starting target, calibrate to the venue |
|---|---|---|
| Mean words per sentence, per section | Reading load | About 14 to 20 |
| Sentences over 30 words | Likely re-reads | Near zero in main-text prose |
| Numbers per 100 words, per section | Report-style density | About 6 or fewer in results prose |
| Numbers in the abstract | Whether the abstract carries ideas | About 3 or fewer |
| Paragraphs over about 110 words | Walls of text, mostly in appendices | None |

Also scan for qualitative problems:

- **Audit voice.** Bookkeeping words such as "recorded", "retained", "pinned", and "configured" in nearly every sentence describe the process, not the science.
- **Stacked caveats.** A hedge, an appendix pointer, and an interval inside one sentence bury the claim.
- **Notation load.** Many symbols appear before the reader needs them.
- **Idioms and compressed phrasing.** Phrasal idioms and compressed constructions that non-native readers misparse.
- **Implicit insights.** The lessons appear only in the conclusion, while results sections list numbers without stating what they mean.

Record the measurements. Re-run them after each pass and report before-and-after values.

## 3. Build the insight backbone and relocation ledger

Write four to six one-sentence insight statements that the evidence supports, including any inconclusive or null result stated plainly. Tag every main-text paragraph with the insight it serves. A paragraph that serves none moves to the appendix. The insight tags are internal scaffolding and never appear in the manuscript.

Keep a relocation ledger with one row per number, caveat, pointer, or table that leaves the main text. Record where it now lives. Move numbers verbatim; do not round them on the way out. Before finishing, confirm that every scope limit and every caveat that changes interpretation still appears in the main text.

## 4. Rewrite the main text for readers

### Sentences

- Put one claim in each sentence. Place the subject and main verb early, and use the active voice where the actor is the authors.
- Avoid semicolon chains, nested clauses, and stacked negation. State what holds.
- Allow at most about one parenthetical per paragraph. Move section and appendix pointers to the end of a sentence or paragraph.
- Replace idioms with literal verbs.
- Shape each paragraph as claim, then evidence with one or two numbers, then meaning.
- Avoid over-correction. Uniformly short sentences read as staccato, so keep some two-clause sentences that link cause and consequence.

### Register

Apply [paper-writing.md](paper-writing.md), section "Write venue-grade prose". In addition:

- Title result subsections as claims, not as topics or questions.
- Open each result subsection with its insight as a declarative sentence, and close with what it implies.
- State the guiding research question once, early.
- State the design's main inferential limit, such as "observational", once and clearly in the main text instead of hedging every sentence.

### Numbers

- Keep the abstract to a few numbers. Qualitative ranges are acceptable when exact values appear in the body.
- Keep about two numbers per results paragraph. Round only when rounding cannot change a conclusion, and keep exact values in tables.
- Put intervals in tables. Use one in prose only when the interval is itself the finding, as with an inconclusive comparison.
- When prose rounds or restates a number, trace it to the exact source value and record the check.

### Terminology

Build a glossary with one prose term per concept and a separate display symbol for tables. Define each term once, at first use, and never swap in synonyms for variety. Check that the main text and the appendix use the same words, including the words in table captions.

### Structure

- Move implementation settings and configuration tables to the appendix. Keep one sentence that states the effective difference between conditions.
- Fold thin subsections into the finding they support.
- Give an inconclusive result its own claim-titled subsection instead of burying it.
- Consider a discussion that contains a findings-to-implications table (finding, evidence, implication), why the result matters for the stakeholders or threat model, recommendations for practice, any decision rule the evidence cannot yet satisfy, and short boundary tests.
- Keep the conclusion to a few sentences that restate the insights at their supported scope.

### Accuracy review after rewriting

Compare every rewritten claim with the original text and its source tables. Rewrites introduce errors. Typical ones are a finding shown for one case restated for all cases, a wrong superlative, and a causal "because" linking two observations. Fix them before moving on.

## 5. Spend freed space on explanation

A readability pass usually frees space. Spend it on explanation, never on new results.

List the reader questions: places where a reader must reconstruct a step alone. Each addition must answer one question. Useful forms:

- **Worked examples built from reported numbers.** For example, a small numeric case showing why a net change hides churn, or a formula evaluated on the paper's own values. Reusing reported numbers keeps audits simple.
- **Definitions in plain words** for scoring variants, checks, intervals, and controls, stating what each one does and does not capture.
- **Rationale for a control.** Name the confound the control removes, and state what outcome would indicate a real effect.
- **Labeled interpretation.** Use hedged verbs such as "may" or "narrows the options", and end with an explicit open question when the design cannot decide.
- **Reading guides in captions.** Add one sentence that tells the reader what to compare.
- **Related-work context** for any method the study builds on but never describes.

Insert additions in tiers (core explanation, then interpretation, then reading aids) and build after each tier. Measure free space in rendered lines. Expect slack absorption: text added on early pages can disappear into flexible float and paragraph spacing without moving the last page, so check the rendered PDF rather than the source. When an addition pushes the main text past the limit, remove duplicated sentences, such as a conclusion that repeats the discussion, instead of shrinking fonts or spacing.

## 6. Run a consistency read

After any large rewrite, read the whole manuscript against its own tables, figures, and appendix. Check at least these defect types:

| Defect | Example check |
|---|---|
| Rounding mismatch | A prose difference computed before rounding disagrees with the difference of rounded table values; say so, or restate |
| Over-generalized scope | Every "both", "all", and "every" holds for each row it covers |
| Start versus end wording | Claims about starting conditions versus endpoints match the results |
| Imprecise metric description | A bound describes the quantity actually computed, not a nearby one |
| Unstated direction | Every difference names its order, and says which side is higher |
| Non-additive shares | Stage shares that do not sum to a cumulative share carry the reason |
| Unreconciled values | The same quantity reported by two suites or passes carries a pointer to the reconciliation |
| Conflicting framing | Earlier sections do not assert what a later control shows to be an artifact |
| Overbroad conclusion | A result shown for one case is not stated for all cases |
| Wrong superlative | "Largest" and "only" survive a check against the full table |
| Unsupported causal wording | "Because" links cause and effect only when the design supports it |
| Document structure | No subsection swallows unrelated material that follows it |
| Terminology drift | Main text, appendix, and captions use the same terms |

Fix defects with length-neutral edits when the page budget is full. Offset added words by removing duplication.

## 7. Revise the appendix

The appendix keeps its technical voice but must stay navigable, and it usually has no page limit.

- Split sentences over about 40 words and paragraphs over about 110 words at topic shifts.
- Add run-in headings where a split starts a new topic.
- Add explanations that restate recorded facts:
  - plain-language readings of formulas;
  - why an identity works;
  - one-line intuitions for aggregates;
  - definitions of terms used before they are defined, taken from the frozen protocol and never guessed;
  - worked readings of formal definitions with the paper's own numbers.
- Present the appendix guide as a grouped, non-floating table with a linked letter, a short topic, one line on what the reader will find, and a linked page number. Omit the caption so that table numbering does not shift. Keep each row to one line by shortening text, not by shrinking the font.

## 8. Maintain audits, artifacts, and records

- Anchor-based prose-number audits break when sentences move. Re-point each anchor to the new sentence instead of deleting the check, and add checks for new rounded restatements.
- Rebuild every artifact that hashes the manuscript, and re-run its own checks.
- Keep any external abstract copy word-for-word identical to the manuscript abstract.
- For each pass, add a notes entry recording what changed, the before-and-after measurements, and the gate results. Mark earlier certification records as superseded, with the new artifact hashes.

## 9. Verify every pass

After each pass, not only at the end:

- Build under the recorded command. Render the pages and inspect them, per [paper-formatting.md](paper-formatting.md).
- Confirm where the main text ends and where page-exempt statements begin.
- Run the project's style, reference-integrity, number-consistency, and compile-log checks.
- Confirm that the relocation ledger is complete and that no claim has become stronger than its evidence.
- Run the writing gate, and the formatting gate for layout changes, from [quality-gates.md](quality-gates.md).

## 10. Deliver the revision

Lead with what changed and whether the gates pass. Report:

- the before-and-after measurements;
- the structural changes;
- defects found and fixed, including those the revision itself introduced;
- the artifacts rebuilt;
- the remaining author-owned actions, such as portal entries, cross-builds, and uploads.

Distinguish completed edits from recommendations. Never call a revised manuscript submission-ready while a gate, a bound artifact, or an authorization remains open.
