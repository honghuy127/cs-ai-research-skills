# Presentation Slides

## Contents

1. Establish the talk contract
2. Storyboard the deck against the claims
3. Choose the slide technology
4. Author PowerPoint decks
5. Author LaTeX decks with Beamer
6. Verify rendered slides
7. Meet venue and accessibility standards
8. Record provenance and pass the talk gate

## 1. Establish the talk contract

Before drafting any slide, record:

- Audience, occasion, and time allotment, and whether the format is a live talk, recorded lecture, lightning pitch, or invited seminar.
- The source of truth: manuscript revision, claim map, or accepted paper, with version. Slides may simplify claims; they may not strengthen them.
- Technical constraints: aspect ratio, projector or platform, offline delivery, file size limits, and whether the audience receives the deck, a handout, or both.
- Confidentiality: whether the deck covers unpublished work, confidential review material, or personal data, and what may be shown or distributed.
- Reuse permissions for third-party figures and logos, following figures-and-diagrams.md.

Do not infer authorization to present unreleased results beyond what the source of truth supports, or to distribute the deck publicly.

## 2. Storyboard the deck against the claims

Use `assets/slide-deck-plan.md` as the planning template. Before authoring:

- Assign one message per slide, each tied to a claim ID from the claim map in [paper-writing.md](paper-writing.md), section "Build a claim-led paper plan".
- Budget slides against the time allotment; a deck that cannot be presented at pace fails its purpose even if every slide is good.
- Plan figure reuse from existing editable sources and exports per figures-and-diagrams.md rather than redrawing from screenshots.
- Record which numbers appear on which slide and which analysis artifact supplies them. A slide number without a trace fails the talk gate.

Keep the story arc: problem, gap, approach, evidence with its limits, and implication. Reserve backup slides for anticipated questions instead of crowding the main path.

## 3. Choose the slide technology

Pick the format the audience, co-authors, and venue workflow support. All three routes below are supported; a project may keep one canonical deck or derive the others from the same storyboard.

| Route | Authoring source | Use when |
|---|---|---|
| PowerPoint (`.pptx`) | python-pptx script or an institutional template | Co-authors or the venue work in Office; the deck needs native charts, speaker notes, or editable handoff |
| LaTeX (Beamer) | `.tex` sources compiled with the paper's TeX distribution | Math-heavy content, or typography and figures must match the manuscript; printable handouts from the same source |
| Markdown pipelines (Quarto, Marp, reveal.js) | Markdown plus a converter | Discussion drafts only, or the project already depends on that toolchain |

Routing rules:

- Load figures-and-diagrams.md for every figure that appears on a slide; this reference does not relax figure provenance rules.
- Load analysis-and-statistics.md before presenting any measured value; uncertainty and scope travel with the number.
- Create any .docx or .xlsx handout under office-documents.md; a handout is an office document artifact with its own provenance gate.
- Do not present a deck produced by a generator or web pipeline as a deliverable without render verification under section 6.

## 4. Author PowerPoint decks

Prefer reproducible authoring over one-off GUI edits:

- Generate or patch the deck with python-pptx from a recorded script, or start from the institutional template and keep the template file versioned. Verify API behavior against the installed python-pptx release.
- Use the template's layouts and masters instead of manually positioned boxes, so fonts, colors, and alignment stay consistent.
- Place figures as high-resolution exports from their editable sources; never screenshot a figure for a slide. Native tables and editable text are reusable; flattened images are not.
- Put elaboration and live-only content in speaker notes, not on the slide face.
- Use fonts that ship with the presentation environment or embed them through the tooling; record the font list because python-pptx cannot embed fonts by itself.
- Before structural checks or handoff, run the package lint:

```bash
python3 scripts/check_office.py deck.pptx --strict
```

Fix broken media references, macro payloads, placeholder markers, and empty slides; use `--json` when wiring the check into a pipeline.

## 5. Author LaTeX decks with Beamer

- Choose a theme with a recorded rationale, and verify that the theme and any needed packages exist in the installed TeX distribution before writing slides. Never invent package names; check official documentation: https://ctan.org/pkg/beamer and https://github.com/josephwright/beamer.
- Structure with `\section` and `\subsection` so the outline and hyperlinked table of contents stay correct; use `\note` for speaker notes.
- Use overlays (`\pause`, `\only`, `\onslide`) deliberately; every overlay multiplies the render-verification surface. Compile with `handout` for printed or shared copies, and keep the on-screen and handout variants from diverging in content.
- Reuse manuscript figures via `\includegraphics` of the same recorded exports, or TikZ sources per figures-and-diagrams.md. Slides are not a place to re-type numbers.
- Put anticipated-question material in an `\appendix`, with frames after it excluded from the main frame count where the theme or venue numbering requires it.
- Compile under a recorded command with enough passes for references and links to settle, then machine-check the log:

```bash
python3 scripts/check_latex_log.py build/slides.log
```

Overfull `\hbox` warnings are common in Beamer and are real overflow defects, not style noise. Fix content or sizing; rerun does not remove them.

## 6. Verify rendered slides

A deck is judged by its rendered output, never by its source. For Beamer the artifact is already a PDF; for PowerPoint, export to PDF first:

```bash
# LibreOffice headless export; verify the binary name and flags per install
soffice --headless --convert-to pdf deck.pptx
```

Then rasterize and inspect with the same loop as paper-formatting.md:

```bash
pdftoppm -png -r 150 deck.pdf render/slide
```

Inspect every slide at presentation scale:

- Text is readable from the back of the intended room; figure text meets the legibility rules in figures-and-diagrams.md.
- No overflow, clipped figures, tables spilled off the slide, or invisible text from contrast failures.
- For overlay-heavy slides, check the first and final overlay states; for Beamer, also check the handout build.
- Numbers, labels, and terminology agree with the manuscript and the deck plan.
- Speaker notes render or export as intended when notes are part of the deliverable.

Record defects with slide numbers, patch the source, re-export or recompile, and re-render. Do not hand-edit an export.

## 7. Meet venue and accessibility standards

Venue and platform rules are volatile. Retrieve the current requirements of the conference, seminar series, or platform, and record the URL and access date. Check at minimum: aspect ratio and resolution, accepted formats and file size, whether sources or fonts must travel with the deck, and any branding or anonymity constraints.

Apply stable standards regardless of venue:

- Colorblind-safe palettes and redundant cues beyond color, matching figures-and-diagrams.md.
- Sufficient contrast between text and background; no text encoded inside raster screenshots.
- Alternative text for informative figures where the format supports it.
- Captions or transcripts for embedded audio and video.
- A deck that reads coherently without motion: animation may clarify sequence but must not be the only carrier of meaning.

## 8. Record provenance and pass the talk gate

Keep the deck ledger in `assets/slide-deck-plan.md`, mapping each slide to its claim ID, figure IDs, and the artifact supplying its numbers, plus the generation command and output paths. In a project dossier, capture deck generation runs with `scripts/capture_run.py` like any other produced artifact.

Require all of the following for a talk gate PASS:

- Every slide traces to the claim map, and every number traces to a recorded source, run, or analysis artifact.
- The editable source exists and is the unique origin of the delivered deck; structural check (`scripts/check_office.py` for pptx, `scripts/check_latex_log.py` for Beamer) reports no errors.
- Rendered slides were visually inspected at presentation scale with the checklist in section 6 completed and defects resolved.
- Labels, terminology, and claims agree with the manuscript and do not overstate it.
- Venue, aspect-ratio, font, and file constraints satisfied with the current source and access date recorded; confidentiality and figure reuse permissions honored.

Return `CONDITIONAL` for bounded polish with an owner. Return `FAIL` for untraceable numbers, figures without sources or permissions, or unpublished content shown beyond the authorized scope. Return `BLOCKED` when the renderer, the current venue rules, or approval for confidential content is missing.
