#!/usr/bin/env python3
"""Check a LaTeX compile log for evidence of layout and reference defects.

Reports hard errors, overfull boxes, undefined references and citations,
changed labels, missing files, rerun requests, and the output page count.
Page attribution for overfull boxes is approximate because TeX flushes pages
after the offending paragraph. The check is structural evidence about the
build; it does not replace rendering the PDF and inspecting the pages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ERROR_RE = re.compile(r"^!\s+(?P<message>.+)$")
SOURCE_LINE_RE = re.compile(r"^l\.(?P<line>\d+)")
PAGE_MARK_RE = re.compile(r"\[(\d+)")
FATAL_RE = re.compile(r"Emergency stop|Fatal error|no output PDF file produced")
MISSING_FILE_RE = re.compile(r"LaTeX Error: File `(?P<file>[^']+)' not found")
UNDEFINED_RE = re.compile(
    r"LaTeX Warning: (?P<kind>Reference|Citation) `(?P<key>[^']+)'"
    r"(?: on page (?P<page>\d+))? undefined on input line (?P<line>\d+)"
)
UNDEFINED_SUMMARY_RE = re.compile(r"There were undefined (references|citations)")
LABELS_RE = re.compile(r"LaTeX Warning: Label\(s\) may have changed")
RERUN_RE = re.compile(r"Please \(re\)run|rerun LaTeX|Rerun to get", re.IGNORECASE)
MISSING_CHAR_RE = re.compile(r"Missing character: There is no (?P<char>.+?) in font")
OVERFULL_RE = re.compile(
    r"Overfull \\(?P<box>[hv])box \((?P<amount>[0-9.]+)pt too (?P<dir>wide|high)\)"
    r"(?: in paragraph at lines (?P<start>\d+)--(?P<end>\d+)"
    r"| detected at line (?P<at>\d+))?"
)
UNDERFULL_RE = re.compile(
    r"Underfull \\(?P<box>[hv])box(?: in paragraph at lines (?P<start>\d+)--(?P<end>\d+))?"
)
OUTPUT_RE = re.compile(r"Output written on (?P<path>\S+) \((?P<pages>\d+) pages?, (?P<bytes>\d+) bytes?\)")


class Finding:
    def __init__(self, severity: str, code: str, message: str, page: int | None = None) -> None:
        self.severity = severity
        self.code = code
        self.message = message
        self.page = page

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "page": self.page,
        }

    def render(self) -> str:
        page = "?" if self.page is None else str(self.page)
        return f"{self.severity} [{self.code}] page={page}: {self.message}"


def find_source_line(lines: list[str], start: int) -> int | None:
    for index in range(start, min(start + 8, len(lines))):
        line = lines[index]
        if line.startswith("! "):
            break
        match = SOURCE_LINE_RE.match(line)
        if match:
            return int(match.group("line"))
    return None


def check_log(text: str, findings: list[Finding]) -> tuple[str | None, int | None]:
    lines = text.splitlines()
    output_pdf: str | None = None
    page_count: int | None = None
    current_page: int | None = None

    for index, line in enumerate(lines):
        marks = PAGE_MARK_RE.findall(line)
        current_page = max([current_page or 0] + [int(m) for m in marks]) or None

        output = OUTPUT_RE.search(line)
        if output:
            output_pdf = output.group("path")
            page_count = int(output.group("pages"))

        missing = MISSING_FILE_RE.search(line)
        if missing:
            findings.append(Finding("error", "missing-file", f"file `{missing.group('file')}' not found", current_page))
            continue
        if FATAL_RE.search(line):
            findings.append(Finding("error", "fatal", line.strip(), current_page))
            continue
        error = ERROR_RE.match(line)
        if error:
            source_line = find_source_line(lines, index + 1)
            suffix = f" (source line {source_line})" if source_line is not None else ""
            findings.append(Finding("error", "latex-error", f"{error.group('message').strip()}{suffix}", current_page))
            continue

        overfull = OVERFULL_RE.search(line)
        if overfull:
            box = f"{overfull.group('box')}box"
            where = ""
            if overfull.group("start"):
                where = f" (lines {overfull.group('start')}--{overfull.group('end')})"
            elif overfull.group("at"):
                where = f" (line {overfull.group('at')})"
            findings.append(
                Finding(
                    "warning",
                    "overfull-box",
                    f"Overfull \\{box}: {overfull.group('amount')}pt too {overfull.group('dir')}{where}",
                    current_page,
                )
            )
            continue
        underfull = UNDERFULL_RE.search(line)
        if underfull:
            where = f" (lines {underfull.group('start')}--{underfull.group('end')})" if underfull.group("start") else ""
            findings.append(
                Finding("info", "underfull-box", f"Underfull \\{underfull.group('box')}box{where}", current_page)
            )
            continue

        undefined = UNDEFINED_RE.search(line)
        if undefined:
            kind = undefined.group("kind").lower()
            findings.append(
                Finding(
                    "warning",
                    f"undefined-{kind}",
                    f"undefined {kind} `{undefined.group('key')}' (line {undefined.group('line')})",
                    int(undefined.group("page")) if undefined.group("page") else current_page,
                )
            )
            continue
        if UNDEFINED_SUMMARY_RE.search(line):
            findings.append(Finding("warning", "undefined-summary", line.strip(), current_page))
            continue
        if LABELS_RE.search(line):
            findings.append(Finding("warning", "labels-changed", "labels changed since the last run; recompile", current_page))
            continue
        if RERUN_RE.search(line):
            findings.append(Finding("warning", "rerun-requested", line.strip(), None))
            continue
        missing_char = MISSING_CHAR_RE.search(line)
        if missing_char:
            findings.append(Finding("warning", "missing-character", line.strip(), current_page))
            continue

    return output_pdf, page_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a LaTeX compile log for layout and reference defects.")
    parser.add_argument("logfile", metavar="LOG", help=".log file produced by the LaTeX build")
    parser.add_argument("--max-pages", type=int, help="fail when the output page count exceeds this limit")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    path = Path(args.logfile)
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        findings.append(Finding("error", "unreadable-log", str(exc)))
        text = None

    output_pdf = page_count = None
    if text is not None:
        output_pdf, page_count = check_log(text, findings)
        if args.max_pages is not None and page_count is not None and page_count > args.max_pages:
            findings.append(
                Finding("error", "page-limit-exceeded", f"output has {page_count} pages, above the limit of {args.max_pages}")
            )

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    infos = [f for f in findings if f.severity == "info"]
    failed = bool(errors) or (args.strict and bool(warnings))
    status = "fail" if failed else ("pass-with-warnings" if warnings else "pass")

    if args.as_json:
        report = {
            "file": str(path),
            "output_pdf": output_pdf,
            "pages": page_count,
            "max_pages": args.max_pages,
            "errors": [f.as_dict() for f in errors],
            "warnings": [f.as_dict() for f in warnings],
            "info": [f.as_dict() for f in infos],
            "status": status,
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"{path}: {page_count if page_count is not None else '?'} page(s), output {output_pdf or 'unknown'}")
        for finding in findings:
            if finding.severity != "info":
                print(f"  {finding.render()}")
        print(f"  status: {status}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
