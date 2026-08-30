#!/usr/bin/env python3
"""Lay the contribution snake over the Ghibli sky as liquid green glass.

Platane/snk emits a bare grid. This script expands the canvas to the sky
photograph, frosts a glass plate behind the cells, and retints the cells
and snake to GitHub greens with enough opacity for the landscape to read
through. CSS keyframes from snk are left intact.

Usage:
    python3 scripts/glass_snake.py dist/github-contribution-grid-snake.svg
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKY = ROOT / "assets" / "atelier" / "snake-sky.jpg"

# Canvas matches the photograph (1025 x 280).
CANVAS_W = 1025
CANVAS_H = 280
PAD_X = 48
PAD_Y = 36

GREEN_ROOT = (
    ":root{"
    "--cb:rgba(255,255,255,0.45);"
    "--cs:#4ade80;"
    "--ce:rgba(255,255,255,0.16);"
    "--c0:rgba(255,255,255,0.20);"
    "--c1:#9be9a8;"
    "--c2:#40c463;"
    "--c3:#30a14e;"
    "--c4:#216e39"
    "}"
)

CELL_STYLE = (
    ".c{shape-rendering:geometricPrecision;"
    "fill:rgba(255,255,255,0.20);"
    "fill:var(--ce);"
    "fill-opacity:0.88;"
    "stroke-width:0.75px;"
    "stroke:rgba(255,255,255,0.55);"
    "animation:none 33300ms linear infinite;"
    "width:12px;height:12px}"
)

SNAKE_STYLE = (
    ".s{shape-rendering:geometricPrecision;"
    "fill:#4ade80;"
    "fill:var(--cs);"
    "filter:url(#snake-glow);"
    "animation:none linear 33300ms infinite}"
)


def encode_sky() -> str:
    if not SKY.is_file():
        raise FileNotFoundError(f"sky photograph missing: {SKY}")
    payload = base64.b64encode(SKY.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{payload}"


def parse_viewbox(svg: str) -> tuple[float, float, float, float]:
    match = re.search(r'viewBox="([^"]+)"', svg)
    if not match:
        raise ValueError("snake SVG has no viewBox")
    x, y, w, h = (float(p) for p in match.group(1).split())
    return x, y, w, h


def restyle(svg: str) -> str:
    svg = re.sub(r":root\{[^}]*\}", GREEN_ROOT, svg, count=1)
    svg = re.sub(r"\.c\{[^}]*\}", CELL_STYLE, svg, count=1)
    svg = re.sub(r"\.s\{[^}]*\}", SNAKE_STYLE, svg, count=1)
    svg = re.sub(
        r"\.u\{[^}]*\}",
        ".u{display:none;animation:none linear 33300ms infinite}",
        svg,
        count=1,
    )
    return svg


def scenery(min_x: float, min_y: float, width: float, height: float) -> str:
    uri = encode_sky()
    grid_w = width
    grid_h = height
    tx = (CANVAS_W - grid_w) / 2 - min_x
    ty = (CANVAS_H - grid_h) / 2 - min_y + 8
    plate_x = PAD_X
    plate_y = PAD_Y
    plate_w = CANVAS_W - PAD_X * 2
    plate_h = CANVAS_H - PAD_Y * 2
    return f'''<defs>
  <clipPath id="frame"><rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" rx="18" ry="18"/></clipPath>
  <clipPath id="glass-clip"><rect x="{plate_x}" y="{plate_y}" width="{plate_w}" height="{plate_h}" rx="16" ry="16"/></clipPath>
  <filter id="frost" x="-8%" y="-20%" width="116%" height="140%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="7"/>
  </filter>
  <filter id="snake-glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="1.4" result="bloom"/>
    <feColorMatrix in="bloom" type="matrix" values="0.2 0.8 0.2 0 0  0.1 1 0.2 0 0  0.1 0.7 0.2 0 0  0 0 0 0.55 0" result="tint"/>
    <feMerge>
      <feMergeNode in="tint"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <linearGradient id="glass-sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.20"/>
    <stop offset="45%" stop-color="#c8f4d4" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#16351f" stop-opacity="0.16"/>
  </linearGradient>
  <linearGradient id="sky-veil" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#7ec8ff" stop-opacity="0.06"/>
    <stop offset="100%" stop-color="#1a3a24" stop-opacity="0.18"/>
  </linearGradient>
</defs>
<g clip-path="url(#frame)">
  <image id="sky" href="{uri}" xlink:href="{uri}" x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" preserveAspectRatio="xMidYMid slice"/>
  <g clip-path="url(#glass-clip)" filter="url(#frost)">
    <use href="#sky" xlink:href="#sky"/>
  </g>
  <rect x="{plate_x}" y="{plate_y}" width="{plate_w}" height="{plate_h}" rx="16" ry="16" fill="url(#glass-sheen)" stroke="rgba(255,255,255,0.50)" stroke-width="1.15"/>
  <rect x="{plate_x + 1.2}" y="{plate_y + 1.2}" width="{plate_w - 2.4}" height="{plate_h - 2.4}" rx="15" ry="15" fill="none" stroke="rgba(74,222,128,0.28)" stroke-width="0.9"/>
  <rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="url(#sky-veil)"/>
  <g id="grid" transform="translate({tx:.2f} {ty:.2f})">
'''


def close_scenery() -> str:
    return (
        "</g>\n"
        '<rect x="0.6" y="0.6" width="1023.8" height="278.8" rx="17.4" ry="17.4" '
        'fill="none" stroke="rgba(18,28,22,0.55)" stroke-width="1.2"/>\n'
        "</g>\n"
    )


def glassify(svg: str) -> str:
    svg = restyle(svg)
    min_x, min_y, width, height = parse_viewbox(svg)
    open_tag = (
        f'<svg viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="{CANVAS_W}" '
        f'height="{CANVAS_H}" xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
    )
    svg = re.sub(r"<svg\b[^>]*>", open_tag, svg, count=1)
    # Insert scenery after <style>...</style> (or after <desc> if style is first).
    style_end = re.search(r"</style>", svg)
    if not style_end:
        raise ValueError("snake SVG has no style block")
    insert_at = style_end.end()
    svg = svg[:insert_at] + scenery(min_x, min_y, width, height) + svg[insert_at:]
    svg = re.sub(r"</svg>\s*$", close_scenery() + "</svg>\n", svg, count=1)
    return svg


def process(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    if "Generated with https://github.com/Platane/snk" not in original:
        raise ValueError(f"{path} does not look like a Platane/snk file")
    path.write_text(glassify(original), encoding="utf-8")
    print(f"glassified {path} ({path.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svgs", nargs="+", type=Path)
    args = parser.parse_args()
    for svg in args.svgs:
        process(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
