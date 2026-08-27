#!/usr/bin/env python3
"""Render .drawio diagram sources to PNG and SVG without the draw.io desktop CLI.

Uses the diagrams.net static viewer in a headless browser driven by Playwright:
the drawio XML is embedded in a local page, the viewer renders it, and the
script captures a PNG screenshot and reconstructs an SVG export from the
rendered graph (shapes come from the viewer's SVG; HTML labels are folded back
in as foreignObject elements positioned over the same coordinates).

This is the documented local-render fallback from
references/figures-and-diagrams.md when the draw.io desktop CLI is unavailable.
Unlike the other helper scripts it needs optional dependencies that the
standard library cannot provide:

    python3 -m pip install playwright
    python3 -m playwright install chromium

The viewer script itself is fetched from viewer.diagrams.net at render time, so
network access is required, but figure content stays inside the local page.
Do not use this path for confidential diagrams if uploading content to a web
editor would violate confidentiality; the page never submits data anywhere,
but review the embed page if your policy requires it.

PNG output scales with --scale (device pixel ratio). SVG output is vector but
reconstructed; always inspect the exported SVG by rendering it once more
(this script does that automatically and writes <name>.svg.check.png).
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys
import tempfile

EMBED_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  body {{ margin: 0; background: #ffffff; }}
  .mxgraph {{ max-width: none; border: 1px solid transparent; }}
</style>
<script src="https://viewer.diagrams.net/js/viewer-static.min.js"></script>
</head>
<body>
<div class="mxgraph" data-mxgraph='{payload}'></div>
</body>
</html>
"""

SVG_EXTRACT_JS = """() => {
  const container = document.querySelector('.mxgraph');
  if (!container) { return {error: 'no .mxgraph container'}; }
  const svg = container.querySelector('svg');
  if (!svg) { return {error: 'viewer produced no svg'}; }
  const bbox = container.getBoundingClientRect();
  const clone = svg.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('xmlns:xhtml', 'http://www.w3.org/1999/xhtml');
  clone.setAttribute('width', bbox.width);
  clone.setAttribute('height', bbox.height);
  clone.setAttribute('viewBox', '0 0 ' + bbox.width + ' ' + bbox.height);

  // Fold HTML label overlays back in as foreignObject elements.
  const svgRect = svg.getBoundingClientRect();
  const labels = Array.from(container.querySelectorAll('div')).filter(el => {
    if (el === container || el.contains(svg)) { return false; }
    const style = getComputedStyle(el);
    if (style.position !== 'absolute') { return false; }
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) { return false; }
    return !el.classList.contains('geToolbarContainer');
  });
  const serializer = new XMLSerializer();
  for (const lab of labels) {
    const r = lab.getBoundingClientRect();
    const wrap = document.createElement('div');
    wrap.setAttribute('xmlns', 'http://www.w3.org/1999/xhtml');
    const inner = lab.cloneNode(true);
    inner.style.position = 'static';
    inner.style.left = '';
    inner.style.top = '';
    inner.style.boxSizing = 'border-box';
    wrap.appendChild(inner);
    const fo = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
    fo.setAttribute('x', r.left - svgRect.left);
    fo.setAttribute('y', r.top - svgRect.top);
    fo.setAttribute('width', Math.ceil(r.width) + 4);
    fo.setAttribute('height', Math.ceil(r.height) + 4);
    fo.innerHTML = serializer.serializeToString(wrap);
    clone.appendChild(fo);
  }
  return {svg: serializer.serializeToString(clone)};
}
"""


def build_embed_page(xml_source: str) -> str:
    """Wrap drawio XML in the diagrams.net viewer embed page."""
    payload = html.escape(
        json.dumps(
            {
                "highlight": "#0000ff",
                "nav": False,
                "resize": True,
                "toolbar": "",
                "xml": xml_source,
            }
        ),
        quote=True,
    )
    return EMBED_TEMPLATE.replace("{payload}", payload)


def render(source: pathlib.Path, out_dir: pathlib.Path, formats: list[str], scale: float, timeout_ms: int) -> int:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "error: playwright is not installed. Install the optional renderer deps:\n"
            "  python3 -m pip install playwright\n"
            "  python3 -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    xml_source = source.resolve().read_text(encoding="utf-8")
    page_html = build_embed_page(xml_source)
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[pathlib.Path] = []

    with tempfile.TemporaryDirectory() as tmp:
        page_path = pathlib.Path(tmp) / "preview.html"
        page_path.write_text(page_html, encoding="utf-8")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(device_scale_factor=scale)
            page = context.new_page()
            try:
                page.goto(page_path.as_uri(), wait_until="networkidle", timeout=timeout_ms)
                # On file:// pages the viewer's automatic on-load processing may
                # not fire; invoke it explicitly (idempotent if it already ran).
                page.evaluate("() => { if (window.GraphViewer) { GraphViewer.processElements(); } }")
                page.wait_for_selector(".mxgraph svg", timeout=timeout_ms)
                page.wait_for_timeout(500)
                container = page.locator(".mxgraph")

                if "png" in formats:
                    png_path = out_dir / (source.stem + ".png")
                    container.screenshot(path=str(png_path))
                    outputs.append(png_path)

                if "svg" in formats:
                    result = page.evaluate(SVG_EXTRACT_JS)
                    if "error" in result:
                        print(f"error: svg extraction failed: {result['error']}", file=sys.stderr)
                        browser.close()
                        return 1
                    svg_path = out_dir / (source.stem + ".svg")
                    svg_path.write_text(result["svg"], encoding="utf-8")
                    outputs.append(svg_path)

                    # Verification pass: render the exported SVG once more.
                    check_png = out_dir / (source.stem + ".svg.check.png")
                    page2 = context.new_page()
                    try:
                        page2.goto(svg_path.as_uri(), timeout=timeout_ms)
                        size = page2.evaluate(
                            "() => ({w: Math.ceil(document.documentElement.scrollWidth),"
                            " h: Math.ceil(document.documentElement.scrollHeight)})"
                        )
                        page2.set_viewport_size({"width": max(size["w"], 100), "height": max(size["h"], 100)})
                        page2.screenshot(path=str(check_png), timeout=timeout_ms)
                        outputs.append(check_png)
                    except PlaywrightError as exc:  # screenshot of an SVG document can stall; keep SVG, flag check
                        print(f"warning: svg check render failed ({exc}); inspect the svg manually", file=sys.stderr)
                    page2.close()
            finally:
                browser.close()

    for produced in outputs:
        print(f"wrote {produced}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a .drawio source to PNG/SVG via the diagrams.net static viewer and Playwright."
    )
    parser.add_argument("source", metavar="FILE.drawio", help="drawio source to render")
    parser.add_argument(
        "-o",
        "--out-dir",
        default=None,
        help="output directory (default: directory of the source file)",
    )
    parser.add_argument(
        "--format",
        action="append",
        choices=["png", "svg"],
        dest="formats",
        help="output format; repeatable (default: png and svg)",
    )
    parser.add_argument("--scale", type=float, default=2.0, help="device scale factor for PNG (default: 2)")
    parser.add_argument("--timeout", type=int, default=30000, help="page load timeout in ms (default: 30000)")
    args = parser.parse_args(argv)

    source = pathlib.Path(args.source)
    if not source.is_file():
        print(f"error: source not found: {source}", file=sys.stderr)
        return 2
    out_dir = pathlib.Path(args.out_dir) if args.out_dir else source.parent
    formats = args.formats or ["png", "svg"]
    return render(source, out_dir, formats, args.scale, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
