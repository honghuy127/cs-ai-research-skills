# Markdown Documents

## Contents

1. Establish the document contract
2. Author in portable Markdown
3. Write math that survives the renderer
4. Link to durable targets
5. Machine-check the source
6. Render and inspect before delivery
7. Convert to and from other formats
8. Verify and pass the markdown gate

Adjacent phase playbooks: office-documents.md for docx or xlsx deliverables, presentation-slides.md when deriving decks from documentation, figures-and-diagrams.md when the page embeds figures, github-collaboration.md when the render target or release channel is GitHub.

## 1. Establish the document contract

Before writing, record what the document is and where it will render:

- The class: README, project documentation page, research log or postmortem, report, dataset card supplement, manuscript supplement, or issue or pull request body.
- The render target, because rendering is not portable: a GitHub README, issue, pull request, or discussion differs from GitHub Pages or another static site generator, which differs from an editor preview or a pandoc conversion. Record the exact renderer and access date.
- The dialect the target supports: the CommonMark core plus which GitHub Flavored Markdown extensions (tables, task lists, strikethrough, autolinks, footnotes) and which platform extensions (alerts, math, color chips).
- Whether the document restates research results. If so, analysis-and-statistics.md governs every number and the document itself is a deliverable whose values must trace to analysis artifacts.

Do not infer authorization to push, publish, or externally share the document. Those stay under the authority rules in github-collaboration.md and quality-gates.md.

## 2. Author in portable Markdown

Write the CommonMark core first; add extensions only when the recorded target supports them.

Portable rules:

- One level-1 heading per document; no heading-level skips.
- Fenced code blocks with a language tag; prefer them over indented blocks.
- A blank line before and after headings, lists, tables, fences, and math blocks, since many renderers silently merge blocks that touch.
- Backslash-escape Markdown characters that must appear as text; escaping does not work inside inline code.
- Never ship a placeholder. Resolve or delete `[CITATION NEEDED]`, `[EVIDENCE NEEDED]`, `[RESULT PENDING]`, `TODO`, `FIXME`, `TBD`, and `XXX` before delivery.

GitHub-specific behavior where it differs from the core, verified against the official syntax reference rather than assumed:

- Line breaks: in issues, pull requests, and discussions a bare newline renders as a line break; in `.md` files a line break needs two trailing spaces, a trailing backslash, `<br/>`, or a blank line.
- Footnotes are not supported in wikis.
- Alerts (`> [!NOTE]` and its `TIP`, `IMPORTANT`, `WARNING`, and `CAUTION` siblings) are a GitHub extension. Other renderers show a plain blockquote. Alerts cannot be nested inside other elements; use them sparingly.
- Color chips (`#RRGGBB`, `rgb(...)`, `hsl(...)` in backticks) render only in issues, pull requests, and discussions, never in `.md` files.
- HTML comments hide content from the render but remain in the source. Never stash confidential notes in them for a public document.

## 3. Write math that survives the renderer

GitHub renders `$...$` and `$$...$$` with MathJax, but Markdown parsing competes with math parsing. Recorded failure modes:

- In inline math, one `_` on the line can pair with a later `_` as emphasis and eat the math expression. Expressions where every underscore directly follows a letter, like `$L_{total}$`, stay safe. Lines combining a `}_{...}` opening subscript with a later closing subscript elsewhere on the same line are the risk point. Fix by rephrasing the line or making the second token a code span; do not insert `\_`, which breaks the subscript.
- In display math, avoid spacing macros (`\,` `\;` `\!`), row spacing like `\\[2pt]` inside `cases`, and `\left(` paired with `\!`. Inside `cases`, use one source line per row.
- When a stubbed `$$...$$` block will not render, fall back to a fenced `math` code block rather than shipping broken markup.

Rules:

- Test-render any line containing math in the actual target before delivery as required by section 6. Never verify math rendering from the source alone.
- When the audience includes renderers without math support, keep equations small, or deliver them as figures per figures-and-diagrams.md.
- Re-verify the current GitHub math syntax page before asserting a rule, because renderer support and limitations change over time.

## 4. Link to durable targets

- Prefer relative links and image paths for files inside the same repository, so delivery works when the repository is cloned.
- On GitHub, links starting with `/` resolve at the repository root, not the filesystem root. They work in the hosted document but break in clones, so treat them as a portability warning and state the intent.
- Heading anchors are renderer-generated: lowercase, whitespace to hyphens, other punctuation dropped, formatting removed, with `-1`, `-2`, suffixes for duplicate headings. Renaming or reordering headings silently breaks every `#fragment` link to them. Do not construct anchors from memory; verify with `scripts/check_markdown.py` and the rendered target.
- Give every image meaningful alt text and a committed asset path; do not point at private URLs, local absolute paths, or login-gated locations.
- Cross-file links using the `path.md#section` form are real references: a missing fragment is a delivery defect, not a warning to wave through.

## 5. Machine-check the source

Run the structural lint before rendering or delivery:

```bash
python3 scripts/check_markdown.py README.md docs/CONTRIBUTING.md --strict
```

The checker reports with line numbers:

- Hard errors: an unclosed fenced code block, an unresolved `[CITATION NEEDED]`, `[EVIDENCE NEEDED]`, or `[RESULT PENDING]` marker, and a relative link or image target that does not exist.
- Warnings: a section anchor with no matching heading, a root-relative link path, draft placeholder words (`TODO`, `FIXME`, `TBD`, `XXX`), skipped heading levels, more than one level-1 heading, and an image without alt text.
- Use `--json` for a machine report and `--strict` in the delivery pass so warnings also fail.

Interpretation:

- Errors block the gate; fix them all.
- Warnings may pass a review pass with owners, but must clear before delivery.
- The lint cannot see renderer behavior such as alerts, math, task lists, and anchor quirks, so a clean lint is necessary but not sufficient; the delivery verdict comes from the rendered inspection in section 6.

## 6. Render and inspect before delivery

Text extraction is not a rendering check; the delivery verdict comes from the real target:

- GitHub READMEs, issues, pull requests, discussions, and wikis: preview in the GitHub UI at the exact revision being delivered, by pushing the branch or using the comment preview.
- GitHub Pages or another site generator: build locally with the recorded generator command and inspect the built pages in a browser.
- Editor or CLI previews are acceptable for drafts; still verify in the final renderer before delivery, because previews diverge.

On every rendered page verify at minimum: heading hierarchy and the auto-generated outline; tables, code, and math layout; images and their alt text; that every link lands on the intended section; and that no unrendered markup, raw command, or leaked placeholder appears in the output. Record the revision, target, and date, then re-render after fixes rather than trusting source edits.

## 7. Convert to and from other formats

Keep Markdown as the source whenever possible; treat conversions as derived artifacts produced under a recorded command:

| Task | Preferred command | Notes |
|---|---|---|
| Markdown to Word | `pandoc source.md -o out.docx --reference-doc template.docx` | The reference document carries styles; do not restyle by hand |
| Markdown to HTML or PDF for review | pandoc with a recorded template | Verify the output renders; never trust the source alone |
| Word or HTML into Markdown | pandoc in the reverse direction | Treat output as an extraction and verify per office-documents.md |

Verify generated Office outputs with `scripts/check_office.py` and rendered-inspect them before delivery. Capture converted deliverables with `scripts/capture_run.py` when the dossier applies, so regeneration stays traceable.

## 8. Verify and pass the markdown gate

Require all of the following for a markdown gate PASS:

- The document contract is recorded: class, render target, dialect, and whether results are restated.
- `scripts/check_markdown.py` reports no errors, and `--strict` reports no warnings before delivery.
- The final revision was inspected in the actual render target and all observed defects were resolved or explicitly waived.
- Every relative link, anchor, and image target exists, and alt text is present and meaningful.
- Every number or result statement traces to an analysis artifact or recorded source; no unresolved `[CITATION NEEDED]`, `[EVIDENCE NEEDED]`, or `[RESULT PENDING]` marker.
- Any converted outputs were machine-checked and rendered-inspected under their own phase check.

Return `CONDITIONAL` for bounded presentation waivers with an owner and expiry. Return `FAIL` for fabricated or untraceable content, shipped placeholders, or known-broken rendering. Return `BLOCKED` when the render target, dialect, or required approval cannot be determined.
