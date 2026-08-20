#!/usr/bin/env python3
"""Lint .drawio diagram sources for structural defects.

Parses plain and compressed mxfile pages and reports malformed XML, duplicate
cell ids, dangling edge or parent references, missing geometry, empty labels,
embedded raster images, small font sizes, off-page content, and unresolved
placeholder markers. The lint certifies structure only; it cannot tell whether
the rendered figure communicates correctly, so every clean result still needs
a visual inspection of an actual export.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_research import PLACEHOLDERS

DEFAULT_PAGE_WIDTH = 850.0
DEFAULT_PAGE_HEIGHT = 1100.0


class Finding:
    def __init__(self, severity: str, code: str, page: str, message: str) -> None:
        self.severity = severity
        self.code = code
        self.page = page
        self.message = message

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "page": self.page,
            "message": self.message,
        }

    def render(self) -> str:
        return f"{self.severity} [{self.code}] page={self.page}: {self.message}"


def decode_compressed(payload: str) -> str:
    padded = payload + "=" * (-len(payload) % 4)
    inflated = zlib.decompress(base64.b64decode(padded), -zlib.MAX_WBITS)
    return urllib.parse.unquote(inflated.decode("utf-8"))


def extract_pages(root: ET.Element, findings: list[Finding]) -> list[dict]:
    pages: list[dict] = []
    if root.tag == "mxGraphModel":
        pages.append({"name": "model", "model": root})
        return pages
    if root.tag == "mxfile":
        diagrams = list(root.findall("diagram"))
    elif root.tag == "diagram":
        diagrams = [root]
    else:
        return pages
    for index, diagram in enumerate(diagrams, start=1):
        name = diagram.get("name") or f"page-{index}"
        model = diagram.find("mxGraphModel")
        if model is None and diagram.text and diagram.text.strip():
            try:
                fragment = ET.fromstring(decode_compressed(diagram.text.strip()))
            except (ValueError, ET.ParseError, zlib.error, UnicodeDecodeError) as exc:
                findings.append(Finding("error", "decode-error", name, f"compressed payload could not be decoded: {exc}"))
                continue
            model = fragment if fragment.tag == "mxGraphModel" else fragment.find("mxGraphModel")
        if model is None:
            findings.append(Finding("error", "empty-page", name, "page carries no mxGraphModel"))
            continue
        pages.append({"name": name, "model": model})
    return pages


def parse_style(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    parsed: dict[str, str] = {}
    for part in style.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
            parsed[key.strip()] = value.strip()
        else:
            parsed.setdefault(part, "")
    return parsed


def check_page(page: dict, min_font_size: float, findings: list[Finding]) -> tuple[int, int]:
    name = page["name"]
    model = page["model"]
    root = model.find("root")
    if root is None:
        findings.append(Finding("error", "missing-root", name, "mxGraphModel has no root element"))
        return 0, 0

    cells = list(root.iter("mxCell"))
    ids: set[str] = set()
    for cell in cells:
        cell_id = cell.get("id")
        if not cell_id:
            findings.append(Finding("error", "missing-id", name, "cell has no id attribute"))
            continue
        if cell_id in ids:
            findings.append(Finding("error", "duplicate-id", name, f"duplicate cell id '{cell_id}'"))
        ids.add(cell_id)

    vertex_count = 0
    edge_count = 0
    for cell in cells:
        cell_id = cell.get("id") or "?"
        parent = cell.get("parent")
        if parent and parent not in ids:
            findings.append(Finding("error", "dangling-parent", name, f"cell '{cell_id}' references unknown parent '{parent}'"))
        value = (cell.get("value") or "").strip()
        raw_style = cell.get("style") or ""
        style = parse_style(raw_style)

        for marker in PLACEHOLDERS:
            if marker in value:
                findings.append(Finding("warning", "placeholder-label", name, f"cell '{cell_id}' contains unresolved marker {marker}"))

        if "data:image/" in raw_style and "data:image/svg" not in raw_style:
            findings.append(Finding("warning", "embedded-raster", name, f"cell '{cell_id}' embeds a base64 raster image"))
        if style.get("shape") == "image" and style.get("image", "").startswith(("http://", "https://")):
            findings.append(Finding("warning", "external-image", name, f"cell '{cell_id}' references an external image URL"))

        if cell.get("vertex") == "1":
            vertex_count += 1
            if cell.find("mxGeometry") is None:
                findings.append(Finding("warning", "missing-geometry", name, f"vertex '{cell_id}' has no mxGeometry"))
            if not value and any(key not in style for key in ("image", "icon")) and style.get("shape") not in ("image",):
                findings.append(Finding("warning", "empty-label", name, f"vertex '{cell_id}' has no label"))
            font_size = style.get("fontSize")
            if font_size and value:
                try:
                    size = float(font_size)
                except ValueError:
                    findings.append(Finding("warning", "bad-font-size", name, f"vertex '{cell_id}' has unparsable fontSize '{font_size}'"))
                else:
                    if size < min_font_size:
                        findings.append(Finding("warning", "small-font", name, f"vertex '{cell_id}' uses font size {size:g}, below {min_font_size:g}"))
        elif cell.get("edge") == "1":
            edge_count += 1
            for endpoint in ("source", "target"):
                target_id = cell.get(endpoint)
                if not target_id:
                    findings.append(Finding("warning", "unconnected-edge", name, f"edge '{cell_id}' has no {endpoint}"))
                elif target_id not in ids:
                    findings.append(Finding("error", "dangling-edge", name, f"edge '{cell_id}' {endpoint} references unknown cell '{target_id}'"))

    check_off_page(model, root, ids, name, findings)
    return vertex_count, edge_count


def check_off_page(model: ET.Element, root: ET.Element, ids: set[str], name: str, findings: list[Finding]) -> None:
    if (model.get("page") or "1") != "1":
        return
    try:
        page_width = float(model.get("pageWidth") or DEFAULT_PAGE_WIDTH)
        page_height = float(model.get("pageHeight") or DEFAULT_PAGE_HEIGHT)
    except ValueError:
        return
    for cell in root.iter("mxCell"):
        if cell.get("vertex") != "1" or (cell.get("parent") or "1") != "1":
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            continue
        try:
            x = float(geometry.get("x") or 0)
            y = float(geometry.get("y") or 0)
            width = float(geometry.get("width") or 0)
            height = float(geometry.get("height") or 0)
        except ValueError:
            continue
        if x + width < 0 or y + height < 0 or x > page_width or y > page_height:
            findings.append(Finding("warning", "off-page", name, f"vertex '{cell.get('id') or '?'}' lies outside the page bounds"))


def validate_file(path: Path, min_font_size: float, findings: list[Finding]) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(Finding("error", "unreadable-file", path.name, str(exc)))
        return {"pages": []}
    try:
        tree_root = ET.fromstring(raw)
    except ET.ParseError as exc:
        findings.append(Finding("error", "parse-error", path.name, f"XML could not be parsed: {exc}"))
        return {"pages": []}

    pages = extract_pages(tree_root, findings)
    if not pages:
        findings.append(Finding("error", "no-pages", path.name, "file contains no diagram pages"))
        return {"pages": []}

    summary = []
    for page in pages:
        vertices, edges = check_page(page, min_font_size, findings)
        summary.append({"name": page["name"], "vertices": vertices, "edges": edges})
    return {"pages": summary}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint .drawio diagram sources for structural defects."
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".drawio files to lint")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    parser.add_argument(
        "--min-font-size",
        type=float,
        default=7.0,
        help="warn on labelled vertices below this font size (default: 7)",
    )
    args = parser.parse_args(argv)

    reports = []
    exit_code = 0
    for raw_path in args.files:
        path = Path(raw_path)
        findings: list[Finding] = []
        summary = validate_file(path, args.min_font_size, findings)
        errors = [f for f in findings if f.severity == "error"]
        warnings = [f for f in findings if f.severity == "warning"]
        failed = bool(errors) or (args.strict and bool(warnings))
        status = "fail" if failed else ("pass-with-warnings" if warnings else "pass")
        if failed:
            exit_code = 1
        reports.append(
            {
                "file": str(path),
                "pages": summary.get("pages", []),
                "errors": [f.as_dict() for f in errors],
                "warnings": [f.as_dict() for f in warnings],
                "status": status,
            }
        )
        if not args.as_json:
            totals = {page["name"]: (page["vertices"], page["edges"]) for page in summary.get("pages", [])}
            vertex_total = sum(v for v, _ in totals.values())
            edge_total = sum(e for _, e in totals.values())
            print(f"{path}: {len(totals)} page(s), {vertex_total} vertex(es), {edge_total} edge(s)")
            for finding in findings:
                print(f"  {finding.render()}")
            print(f"  status: {status}")

    if args.as_json:
        print(json.dumps({"reports": reports}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
