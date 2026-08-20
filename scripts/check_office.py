#!/usr/bin/env python3
"""Check Office Open XML files (.docx, .pptx, .xlsx) for structural defects.

Opens each file as a zip package, parses the XML parts, and reports malformed
XML, missing core parts, broken media references, macro payloads, embedded OLE
objects, empty or hidden slides, placeholder markers, and author metadata. The
check certifies structure only; it cannot tell whether the document content is
correct, so every clean result still needs a rendered visual inspection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from posixpath import normpath as posix_normpath

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_research import PLACEHOLDERS  # noqa: E402

KIND_BY_EXTENSION = {".docx": "docx", ".pptx": "pptx", ".xlsx": "xlsx"}
MACRO_EXTENSIONS = {".docm", ".pptm", ".xlsm"}
MAX_PARSE_BYTES = 4 * 1024 * 1024

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DRAW_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PRES_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
SHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
DC_CREATOR = "{http://purl.org/dc/elements/1.1/}creator"
MARKERS = PLACEHOLDERS + ("lorem ipsum",)


class Finding:
    def __init__(self, severity: str, code: str, part: str, message: str) -> None:
        self.severity = severity
        self.code = code
        self.part = part
        self.message = message

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "part": self.part,
            "message": self.message,
        }

    def render(self) -> str:
        return f"{self.severity} [{self.code}] part={self.part}: {self.message}"


def collect_text(root: ET.Element) -> str:
    chunks = []
    for element in root.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        if tag.rsplit("}", 1)[-1] == "t" and element.text:
            chunks.append(element.text)
    return " ".join(chunks)


def scan_markers(text: str, part: str, findings: list[Finding]) -> None:
    lowered = text.lower()
    for marker in MARKERS:
        if marker.lower() in lowered:
            findings.append(Finding("warning", "placeholder-content", part, f"unresolved marker {marker}"))


def check_package(names: list[str], zf: zipfile.ZipFile, findings: list[Finding]) -> dict[str, ET.Element]:
    roots: dict[str, ET.Element] = {}
    for name in names:
        if not name.endswith((".xml", ".rels")):
            continue
        if zf.getinfo(name).file_size > MAX_PARSE_BYTES:
            continue
        try:
            roots[name] = ET.fromstring(zf.read(name))
        except ET.ParseError as exc:
            findings.append(Finding("error", "malformed-xml", name, f"XML could not be parsed: {exc}"))
    return roots


def owning_part(rels_name: str) -> str:
    directory, _, filename = rels_name.rpartition("/_rels/")
    return f"{directory}/{filename[:-len('.rels')]}"


def check_relationships(names: set[str], roots: dict[str, ET.Element], findings: list[Finding]) -> None:
    for rels_name, root in roots.items():
        if not rels_name.endswith(".rels"):
            continue
        base = owning_part(rels_name).rpartition("/")[0]
        for rel in root.iter(f"{REL_NS}Relationship"):
            rel_type = rel.get("Type") or ""
            if not rel_type.endswith("/image"):
                continue
            target = rel.get("Target") or ""
            if rel.get("TargetMode") == "External":
                findings.append(Finding("info", "external-image", owning_part(rels_name), f"references external image URL {target}"))
                continue
            resolved = posix_normpath(f"{base}/{target}").lstrip("/")
            if resolved not in names:
                findings.append(Finding("error", "missing-media", owning_part(rels_name), f"image target '{target}' is absent from the package"))


def check_core_props(roots: dict[str, ET.Element], findings: list[Finding]) -> None:
    core = roots.get("docProps/core.xml")
    if core is None:
        return
    creator = core.find(DC_CREATOR)
    if creator is not None and (creator.text or "").strip():
        findings.append(
            Finding(
                "info",
                "author-metadata",
                "docProps/core.xml",
                f"creator '{creator.text.strip()}' recorded; scrub metadata before anonymous release",
            )
        )


def check_docx(roots: dict[str, ET.Element], findings: list[Finding]) -> dict:
    document = roots.get("word/document.xml")
    if document is None:
        findings.append(Finding("error", "missing-part", "word/document.xml", "core document part is absent"))
        return {}
    scan_markers(collect_text(document), "word/document.xml", findings)
    if document.find(f".//{WORD_NS}ins") is not None or document.find(f".//{WORD_NS}del") is not None:
        findings.append(Finding("info", "tracked-changes", "word/document.xml", "tracked changes present; resolve before final delivery"))
    return {"paragraphs": len(document.findall(f".//{WORD_NS}p"))}


def check_pptx(names: list[str], roots: dict[str, ET.Element], findings: list[Finding]) -> dict:
    if "ppt/presentation.xml" not in roots:
        findings.append(Finding("error", "missing-part", "ppt/presentation.xml", "core presentation part is absent"))
        return {}
    slide_pattern = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
    slides = sorted(
        (name for name in names if slide_pattern.match(name)),
        key=lambda name: int(slide_pattern.match(name).group(1)),
    )
    hidden = 0
    for slide in slides:
        root = roots.get(slide)
        if root is None:
            continue
        if root.get("show") == "0":
            hidden += 1
            findings.append(Finding("info", "hidden-slide", slide, "slide is hidden from the show"))
        text = collect_text(root)
        if not text.strip():
            findings.append(Finding("warning", "empty-slide", slide, "slide carries no text content"))
        else:
            scan_markers(text, slide, findings)
    return {"slides": len(slides), "hidden": hidden}


def check_xlsx(roots: dict[str, ET.Element], names: list[str], findings: list[Finding]) -> dict:
    workbook = roots.get("xl/workbook.xml")
    if workbook is None:
        findings.append(Finding("error", "missing-part", "xl/workbook.xml", "core workbook part is absent"))
        return {}
    sheet_names = [sheet.get("name") or "?" for sheet in workbook.iter(f"{SHEET_NS}sheet")]
    worksheets = [name for name in names if re.match(r"^xl/worksheets/sheet\d+\.xml$", name)]
    if not sheet_names:
        findings.append(Finding("warning", "no-sheets", "xl/workbook.xml", "workbook declares no sheets"))
    for name in worksheets:
        root = roots.get(name)
        if root is not None:
            scan_markers(collect_text(root), name, findings)
    shared = roots.get("xl/sharedStrings.xml")
    if shared is not None:
        scan_markers(collect_text(shared), "xl/sharedStrings.xml", findings)
    return {"sheets": len(sheet_names), "worksheets": len(worksheets)}


def describe_counts(kind: str, counts: dict) -> str:
    if kind == "docx":
        return f"{counts.get('paragraphs', 0)} paragraph(s)"
    if kind == "pptx":
        return f"{counts.get('slides', 0)} slide(s), {counts.get('hidden', 0)} hidden"
    if kind == "xlsx":
        return f"{counts.get('sheets', 0)} sheet(s), {counts.get('worksheets', 0)} worksheet part(s)"
    return ""


def check_file(path: Path, findings: list[Finding]) -> tuple[str, dict]:
    extension = path.suffix.lower()
    if extension in MACRO_EXTENSIONS:
        findings.append(
            Finding(
                "error",
                "macro-enabled",
                path.name,
                "macro-enabled extension can carry executable VBA; request a macro-free copy before analysis",
            )
        )
        kind = extension[1:]
    else:
        kind = KIND_BY_EXTENSION.get(extension, "unknown")
    if kind == "unknown":
        findings.append(Finding("error", "unknown-type", path.name, "expected a .docx, .pptx, or .xlsx file"))
        return kind, {}

    try:
        zf = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        findings.append(Finding("error", "unreadable-file", path.name, f"package could not be opened: {exc}"))
        return kind, {}

    with zf:
        names = [info.filename for info in zf.infolist() if not info.is_dir()]
        name_set = set(names)
        for macro_part in (name for name in names if name.endswith("vbaProject.bin")):
            findings.append(
                Finding("error", "embedded-vba", macro_part, "package carries a VBA project; treat as untrusted executable content")
            )
        for embedded in (name for name in names if "/embeddings/" in name or name.startswith("embeddings/")):
            findings.append(Finding("warning", "embedded-object", embedded, "embedded OLE object; inspect before trusting or reusing"))

        roots = check_package(names, zf, findings)
        check_relationships(name_set, roots, findings)
        check_core_props(roots, findings)
        if kind == "docx":
            counts = check_docx(roots, findings)
        elif kind == "pptx":
            counts = check_pptx(names, roots, findings)
        elif kind == "xlsx":
            counts = check_xlsx(roots, names, findings)
        else:
            counts = {}
    return kind, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Office Open XML files for structural defects.")
    parser.add_argument("files", nargs="+", metavar="FILE", help=".docx, .pptx, or .xlsx files to check")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    reports = []
    exit_code = 0
    for raw_path in args.files:
        path = Path(raw_path)
        findings: list[Finding] = []
        kind, counts = check_file(path, findings)
        errors = [f for f in findings if f.severity == "error"]
        warnings = [f for f in findings if f.severity == "warning"]
        infos = [f for f in findings if f.severity == "info"]
        failed = bool(errors) or (args.strict and bool(warnings))
        status = "fail" if failed else ("pass-with-warnings" if warnings else "pass")
        if failed:
            exit_code = 1
        reports.append(
            {
                "file": str(path),
                "kind": kind,
                "counts": counts,
                "errors": [f.as_dict() for f in errors],
                "warnings": [f.as_dict() for f in warnings],
                "info": [f.as_dict() for f in infos],
                "status": status,
            }
        )
        if not args.as_json:
            description = describe_counts(kind, counts)
            header = f"{path}: {kind} package"
            if description:
                header = f"{header}, {description}"
            print(header)
            for finding in findings:
                print(f"  {finding.render()}")
            print(f"  status: {status}")

    if args.as_json:
        print(json.dumps({"reports": reports}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
