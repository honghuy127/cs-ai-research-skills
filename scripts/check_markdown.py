#!/usr/bin/env python3
"""Check Markdown files for structural defects before rendering or release.

Reports unclosed fenced code blocks, unresolved research markers, draft
placeholder words, broken relative link or image targets, root-relative
link paths that resolve only inside a repository, section anchors that
match no heading, skipped heading levels, duplicate top-level headings,
and images without alt text. Heading anchors approximate the documented
GitHub slug rules. The check is structural evidence about the source; it
cannot certify the rendered page, so the target platform still needs a
rendered inspection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

PLACEHOLDERS = ("[CITATION NEEDED]", "[EVIDENCE NEEDED]", "[RESULT PENDING]")
DRAFT_WORD_RE = re.compile(r"\b(TODO|FIXME|TBD|XXX)\b")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,}) *$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6}) +(.+?)(?: +#+)?$")
CUSTOM_ANCHOR_RE = re.compile(r'<a\s+(?:name|id)="([^"]+)"')
INLINE_CODE_RE = re.compile(r"(`+)([^`]*)\1")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LINK_TEXT_IN_HEADING_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkd"}


class Finding:
    def __init__(self, severity: str, code: str, line: int | None, message: str) -> None:
        self.severity = severity
        self.code = code
        self.line = line
        self.message = message

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "line": self.line,
            "message": self.message,
        }

    def render(self) -> str:
        line = "?" if self.line is None else str(self.line)
        return f"{self.severity} [{self.code}] line={line}: {self.message}"


def strip_inline_code(text: str) -> str:
    return INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), text)


def slugify_heading(text: str) -> str:
    """Approximate the documented GitHub heading anchor rules.

    Lowercase, drop inline markup and punctuation, and join whitespace with
    single hyphens. Unicode letters and digits are preserved.
    """
    text = LINK_TEXT_IN_HEADING_RE.sub(lambda match: match.group(1), text)
    text = HTML_TAG_RE.sub("", text)
    text = text.translate(str.maketrans("", "", "`*_~")).lower()
    words = []
    for chunk in text.split():
        word = "".join(ch for ch in chunk if ch.isalnum() or ch in "-_")
        if word:
            words.append(word)
    return "-".join(words)


def split_outside_fences(lines: list[str]) -> tuple[list[tuple[int, str]], tuple[str, int] | None]:
    """Split lines into those outside fenced code blocks.

    Follows the CommonMark fence rules: a closing fence is a bare run of the
    same character at least as long as the opener, and the info string of a
    backtick fence cannot contain backticks. Returns the outside lines with
    their 1-based numbers, and the still-open fence marker and line if any.
    """
    outside: list[tuple[int, str]] = []
    fence_marker: str | None = None
    fence_open_line: int | None = None

    for number, line in enumerate(lines, start=1):
        if fence_marker is not None:
            close = FENCE_CLOSE_RE.match(line)
            if close and close.group(1)[0] == fence_marker[0] and len(close.group(1)) >= len(fence_marker):
                fence_marker = None
                fence_open_line = None
            continue
        open_match = FENCE_OPEN_RE.match(line)
        if open_match and not (open_match.group(1)[0] == "`" and "`" in open_match.group(2)):
            fence_marker = open_match.group(1)
            fence_open_line = number
            continue
        outside.append((number, line))

    unclosed = (fence_marker, fence_open_line) if fence_marker is not None else None
    return outside, unclosed


def collect_anchors(text: str) -> tuple[set[str], set[str]]:
    """Return generated heading anchors and custom HTML anchors in one file."""
    heading_anchors: set[str] = set()
    custom_anchors: set[str] = set()
    counts: dict[str, int] = {}
    outside, _ = split_outside_fences(text.splitlines())

    for _, line in outside:
        heading = HEADING_RE.match(line)
        if heading:
            slug = slugify_heading(heading.group(2))
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            heading_anchors.add(slug if count == 0 else f"{slug}-{count}")
            continue
        custom_anchors.update(CUSTOM_ANCHOR_RE.findall(line))

    return heading_anchors, custom_anchors


def check_file(path: Path, anchor_cache: dict[Path, tuple[set[str], set[str]]]) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding("error", "unreadable-file", None, str(exc))], 0, 0

    lines = text.splitlines()
    outside, unclosed = split_outside_fences(lines)
    heading_count = 0
    link_count = 0
    h1_count = 0
    previous_level = 0
    links: list[tuple[int, bool, str, str]] = []

    if unclosed is not None:
        findings.append(
            Finding("error", "unclosed-fence", unclosed[1], "fenced code block is never closed")
        )

    for number, line in outside:
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            heading_count += 1
            if level == 1:
                h1_count += 1
                if h1_count > 1:
                    findings.append(Finding("warning", "multiple-h1", number, "document has more than one level-1 heading"))
            if previous_level and level > previous_level + 1:
                findings.append(
                    Finding("warning", "heading-level-skip", number, f"heading level jumps from {previous_level} to {level}")
                )
            previous_level = level
            continue

        stripped = strip_inline_code(line)
        for marker_text in PLACEHOLDERS:
            if marker_text in stripped:
                findings.append(
                    Finding("error", "unresolved-placeholder", number, f"unresolved marker {marker_text}")
                )
        draft = DRAFT_WORD_RE.search(stripped)
        if draft:
            findings.append(Finding("warning", "draft-marker", number, f"draft placeholder word {draft.group(1)}"))

        for match in LINK_RE.finditer(stripped):
            link_count += 1
            is_image = bool(match.group(1))
            links.append((number, is_image, match.group(2), match.group(3)))

    own_headings, own_custom = anchor_cache.setdefault(path, collect_anchors(text))

    for number, is_image, label, raw_target in links:
        target = urllib.parse.unquote(raw_target)
        file_part, _, fragment = target.partition("#")
        file_part = file_part.split("?", 1)[0]

        if is_image and not label.strip():
            findings.append(Finding("warning", "empty-alt-text", number, "image has no alt text"))

        if SCHEME_RE.match(target):
            continue

        if file_part.startswith("/"):
            findings.append(
                Finding("warning", "root-relative-link", number, f"target {raw_target} resolves only at a repository root")
            )
            continue

        if not file_part:
            if fragment and fragment not in own_headings and fragment not in own_custom:
                findings.append(Finding("warning", "missing-anchor", number, f"no heading generates anchor #{fragment}"))
            continue

        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            findings.append(
                Finding("error", "broken-link", number, f"target {raw_target} does not exist")
            )
            continue

        if fragment and resolved.suffix.lower() in MARKDOWN_SUFFIXES:
            try:
                other_text = resolved.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            other_headings, other_custom = anchor_cache.setdefault(resolved, collect_anchors(other_text))
            if fragment not in other_headings and fragment not in other_custom:
                findings.append(
                    Finding("warning", "missing-anchor", number, f"target file has no heading generating anchor #{fragment}")
                )

    return findings, heading_count, link_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Markdown files for structural defects.")
    parser.add_argument("files", metavar="FILE", nargs="+", help="Markdown files to check")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    anchor_cache: dict[Path, tuple[set[str], set[str]]] = {}
    reports = []
    any_error = False
    any_warning = False

    for name in args.files:
        path = Path(name)
        findings, heading_count, link_count = check_file(path, anchor_cache)
        errors = [f for f in findings if f.severity == "error"]
        warnings = [f for f in findings if f.severity == "warning"]
        any_error = any_error or bool(errors)
        any_warning = any_warning or bool(warnings)
        failed = bool(errors) or (args.strict and bool(warnings))
        status = "fail" if failed else ("pass-with-warnings" if warnings else "pass")
        reports.append(
            {
                "file": str(path),
                "headings": heading_count,
                "links": link_count,
                "errors": [f.as_dict() for f in errors],
                "warnings": [f.as_dict() for f in warnings],
                "status": status,
            }
        )
        if not args.as_json:
            print(f"{path}: {heading_count} heading(s), {link_count} link(s)")
            for finding in findings:
                print(f"  {finding.render()}")
            print(f"  status: {status}")

    overall = "fail" if any_error or (args.strict and any_warning) else ("pass-with-warnings" if any_warning else "pass")
    if args.as_json:
        print(json.dumps({"reports": reports, "status": overall}, indent=2))

    return 1 if overall == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
