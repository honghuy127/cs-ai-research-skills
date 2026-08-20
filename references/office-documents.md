# Office Documents

## Contents

1. Establish the document contract
2. Treat Office files as untrusted structured input
3. Analyze documents
4. Create and edit documents
5. Preserve provenance for binary artifacts
6. Verify and pass the office document gate

## 1. Establish the document contract

Before reading or writing any Office document, record what the work is:

- The document class: solicitation or call, contract or terms, requirements or data sheet, report, dataset card, cover letter, response to a committee, or internal memo.
- Its role: input evidence for the project, or a project deliverable.
- The required editable format and template, confidentiality level, and who owns final approval.
- Whether the content includes unpublished results, personal data, or contractual obligations that constrain reuse and sharing.

Do not infer authorization to send, sign, share, or publicly upload any document. Treat those as separate external actions requiring explicit authority.

## 2. Treat Office files as untrusted structured input

Modern Office files (`.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`) are zip archives of XML parts. Legacy binary formats (`.doc`, `.xls`, `.ppt`) are opaque to structural checking; request an OOXML or PDF version where possible.

- Never enable or execute macros, OLE or ActiveX objects, spreadsheet scripts, or linked-content payloads found in a document. Record their presence as a security flag.
- Visible text is not the whole document. Comments, tracked changes, hidden sheets, rows, or columns, speaker notes, and file metadata can carry statements that change interpretation or reveal authorship. Decide which of these are in scope before citing the document.
- Run the structural check before deep analysis:

```bash
python3 scripts/check_office.py submission.docx --strict
```

The checker reports malformed XML, missing core parts, broken media references, macro payloads, embedded objects, placeholder markers, and author metadata. It certifies structure only, never that the content is correct.

## 3. Analyze documents

When a document is an evidence source, for example a solicitation, referee report, or data sheet:

- Convert controlled copies rather than quoting from memory: `pandoc input.docx -o extracted.md` for Word files, and read-only spreadsheet extraction to CSV or JSON with the project's analysis stack. Record the extraction command, the tool version, and a hash of the source file.
- Record findings in the dossier as evidence with locators: section, page, sheet, or cell range. Cite the document itself when asserting what it requires; do not paraphrase a rule and then enforce the paraphrase.
- Requirements in documents are volatile. Re-open the authoritative source rather than trusting a cached copy before acting on deadlines, limits, or eligibility rules.
- If a document's claims conflict with its provenance (unexpected author, edited date, mismatched filename), record the discrepancy in decisions.md before relying on it.

## 4. Create and edit documents

Choose the smallest tool that the deliverable needs, and record the template and command:

| Task | Preferred tool | Notes |
|---|---|---|
| Markdown or LaTeX source into Word | `pandoc source.md -o out.docx --reference-doc template.docx` | The reference document carries styles; do not restyle by hand |
| Programmatic `.docx` construction or patching | python-docx | Verify API behavior against the installed version |
| Spreadsheet generation from analysis | openpyxl or the project's analysis stack | Write values from traceable artifacts, never by manual transcription |
| Format conversion | pandoc or LibreOffice headless | Re-verify flags against the installed version |

Rules for content:

- Template first. Reuse the official or existing template's styles, headings, and numbering; record the template file and version in the dossier.
- Numbers, tables, and result statements in reports must be generated from traceable analysis artifacts, matching the rules in analysis-and-statistics.md. A document that restates results by hand fails the evidence link.
- When editing a document owned by others, keep changes reviewable: tracked changes in Word where available, or an explicit change log with locators when the tool cannot track edits. Never silently rewrite content, remove comments, or accept all changes without listing what changed.
- Spreadsheets intended for later analysis: keep raw data sheets separate from calculation sheets, avoid merged cells and multi-header rows in data regions, and state units and conventions in a header or companion note.

## 5. Preserve provenance for binary artifacts

Office formats do not diff. Treat the generated document as a derived artifact:

- Keep the authoritative source under version control when you own the document: Markdown, LaTeX, CSV, or the generation script.
- Record the generation command, template version, and a content hash of the output file. Capture deliverable documents with `scripts/capture_run.py` like any other produced artifact, so `audit_research.py` can trace them.
- State the regeneration path in the dossier: which script or command reproduces the exact file, and which inputs it reads.

## 6. Verify and pass the office document gate

Require all of the following for an office document gate PASS:

- `scripts/check_office.py` reports no errors, and `--strict` shows no placeholder markers or leftover warnings before delivery.
- A re-extraction or conversion of the final file shows the intended content: nothing truncated, no unresolved [CITATION NEEDED], [EVIDENCE NEEDED], or [RESULT PENDING] marker, and tracked changes resolved or intentionally preserved.
- Every number and result statement traces to a source, run, or analysis artifact recorded in the dossier.
- Metadata reviewed: author, editor, and hidden fields scrubbed or appropriate for the recipient, especially for anonymous or external delivery.
- The template, format, and approval constraints from the document contract are satisfied.

Return `CONDITIONAL` for bounded presentation work with an owner. Return `FAIL` for fabricated or untraceable values, macro payloads about to be shipped, or silent edits to documents owned by others. Return `BLOCKED` when the template, format, or approval owner cannot be determined.
