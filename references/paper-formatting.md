# Paper Formatting and Visual Checks

## Contents

1. Establish the formatting contract
2. Compile under a recorded command
3. Machine-check the compile log
4. Render pages for visual inspection
5. Run the visual checklist
6. Verify files and metadata
7. Iterate, record, and pass the formatting gate

## 1. Establish the formatting contract

Venue formatting rules are volatile. Before checking anything, retrieve the current official requirements from the venue, publisher, or template maintainer and record the URL and access date. Do not rely on remembered limits.

Record in `assets/format-checklist.md` or the dossier:

- Exact template or document class, version or release date, and allowed modifications.
- Page or word limits and what counts against them: main text, references, appendices, ethics statements, checklists, and reproducibility checklists are treated differently across venues.
- Required engine or DVI/PS/PDF constraints, font rules, and file formats for submission.
- Anonymity requirements that affect content, metadata, acknowledgments, and embedded file properties.
- Figure rules that interact with layout (width limits, caption placement, subfigure labels), deferring content decisions to `figures-and-diagrams.md`.

If official sources conflict or remain ambiguous on a rule that would change the layout work, stop and ask for a human decision rather than guessing.

## 2. Compile under a recorded command

A format check starts from a clean, reproducible build of the exact submission sources.

- Use the engine the template requires; `latexmk -pdf`, `latexmk -xelatex`, or `latexmk -lualatex` with sufficient passes so references and citations stabilize.
- Compile with `-interaction=nonstopmode` so the run completes and the full log survives; never silence the log or discard it.
- Build in an isolated output directory from a pristine copy of the submission tree, so the check reflects what will be uploaded, not a locally patched variant.
- Record the command, engine version, template version, and source revision. Treat the resulting PDF and log as the format-check artifacts.

If the template does not compile at all under the required engine, that is a FAIL, not a formatting nuance to negotiate.

## 3. Machine-check the compile log

Extracted text and memory of the source are not the layout state; the compile log is the first machine-readable record of it. Run:

```bash
python3 scripts/check_latex_log.py build/main.log --max-pages 9
```

The checker reports, with locations:

- Hard errors: lines starting with `!`, emergency stops, and fatal-error markers.
- Overfull `\hbox` and `\vbox` warnings, the amount of spill, and an approximate page.
- Underfull boxes as informational noise.
- Undefined references and citations, labels that changed since the last pass, missing files and figures, and rerun requests.
- The output file and page count, checked against `--max-pages` when given.

Treat the results as:

- Hard errors block every further claim about formatting.
- Undefined references, undefined citations, and changed labels block a submission-ready verdict; rerun or fix first.
- Overfull boxes are visible layout defects. Fix them before camera-ready, prioritizing large spills and anything near margins, table rules, or column breaks. A venue that silently ships overflowing text has already failed its format check.
- Use `--strict` in a camera-ready pass so any warning fails.

The log check is structural evidence about the build. It does not certify that the rendered pages look right.

## 4. Render pages for visual inspection

Text extraction is not a formatting check. Extraction loses order, overlap, margins, figure legibility, and float placement, so a converted-to-text review cannot pass or fail formatting. Render the compiled PDF to page images and inspect them visually.

Rasterize every page at roughly 150 DPI:

```bash
# Preferred, poppler (Linux, or macOS via package manager)
pdftoppm -png -r 150 main.pdf render/page

# macOS alternative without poppler: Quick Look thumbnails cover only page 1,
# so for multi-page inspection prefer installing poppler or using MuPDF
mutool draw -o render/page-%d.png -r 150 main.pdf
```

Fallbacks when neither tool exists: a small PyMuPDF loop if the environment already provides it, a headless-browser PDF viewer screenshot, or asking the user to supply page images. If no renderer is available, mark the visual part `BLOCKED`; never pass the formatting gate on text alone.

Inspection discipline:

- Open every page image, not a sample, when the paper is short enough; for long documents, inspect first and last pages, every page with figures or tables, and every page the log flagged, then scan the remainder at a reduced but readable size.
- Judge at final print size or equivalent zoom; a page that looks fine at 25% zoom can still carry 5pt text or margin spills.
- Record each observed defect as page number plus description before starting fixes, and re-render after fixes rather than trusting source edits.

## 5. Run the visual checklist

On each rendered page, verify at minimum:

- Margins and text block match the template; nothing prints in the margin or beyond the page, including equation numbers, long URLs, code listings, and tables.
- Figures and tables appear as floats near their first reference, are not clipped or split awkwardly, keep caption adjacency, and respect single- versus double-column spans.
- Captions, subfigure labels, and axis text are readable at print size, per `figures-and-diagrams.md`.
- No orphaned headings at page bottoms, no single-line paragraphs stranded across pages, no badly unbalanced final columns.
- Footnotes stay inside the text block; wide footnotes do not spill columns.
- Page headers, footers, page numbers, and running titles match template policy and any anonymity state.
- Cross-references, citations, and hyperlinks point where the text says they do, and link colors follow venue policy.
- Anonymity holds visually: no author names, affiliations, acknowledgments, funding IDs, or repository links that reveal identity where prohibited.

Text conversion may accompany this pass to cross-check content, but the verdict for layout comes from the rendered pages.

## 6. Verify files and metadata

Before calling a submission package complete, check the artifacts themselves:

- Page count against the recorded limit, counting exactly the sections the limit covers; verify with the log's output line or `pdfinfo`, not source estimates.
- Font embedding with `pdffonts`: every embedded font subset should report `yes`, since unembedded fonts break publisher pipelines and change rendering.
- PDF metadata: title is present, and author or subject metadata is empty or anonymized when anonymity applies; remove editor names and absolute local paths from metadata and embedded properties.
- File size within portal limits.
- Source package completeness when the venue requires sources: `.bbl`, style files, figures at sufficient resolution, and no files the venue forbids.
- Absence of hidden content the venue forbids, including comments with reviewer responses, tracked changes, or JavaScript in the PDF.

Record what was checked, the tool used, and the observed value.

## 7. Iterate, record, and pass the formatting gate

Work the defect list from sections 3 to 6 to zero, patching sources, recompiling, and re-rendering on every cycle. Keep the log, the rendered page images, and the defect list together as the format-check evidence.

In a project dossier, capture the format-check build with `scripts/capture_run.py` like any other reproducible step, and index the rendered evidence as artifacts.

Require all of the following for a formatting gate PASS:

- A recorded, reproducible compile command against the exact submission sources, with the log preserved.
- `check_latex_log.py` reports no hard errors, no undefined references or citations, and no overfull boxes when `--strict` applies.
- Every required page was rendered and visually inspected at a readable size, with the checklist completed and defects resolved.
- Page count, font embedding, metadata, anonymity, and package contents verified against the current venue contract, with source and access date.
- The rendered PDF, not extracted text, carries the layout verdict.

Return `CONDITIONAL` for bounded cosmetic waivers a venue explicitly permits, with an owner and expiry. Return `FAIL` for template violations, overflowing layout shipped knowingly, or anonymity leaks. Return `BLOCKED` when the renderer, the current venue rules, or a human decision is missing.
