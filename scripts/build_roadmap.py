#!/usr/bin/env python3
"""Forge-map roadmap and the night trail.

GitHub <img> SVGs cannot load webfonts, so every visible word is glyph outlines
from typeset. Titles are sentence-case italic (a chapter head, not a HUD).
Station names are the sturdy small Fraunces cut so they stay dense and readable on the
tickets. The path is a Catmull-Rom river, not a 90-degree flowchart. The trail
moon has a terminator; the house is a forge cottage with a smoking chimney.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402
import typeset as ts  # noqa: E402

# n, title, subtitle, kind, rail_x, rail_y, side
# side: which way the ticket hangs off the river.
# kind: walked, here (one station), next (the targets in reach), later.
STATIONS = [
    (1, "First programs", "CS50, print and loop", "walked", 128, 228, "up"),
    (2, "C and memory", "pointers, arrays", "walked", 318, 292, "down"),
    (3, "C++ and OOP", "classes, game systems", "walked", 520, 206, "up"),
    (4, "Systems in C++", "processes, scheduling", "walked", 742, 300, "down"),
    (5, "PHP dashboards", "the first real app", "walked", 960, 236, "up"),
    (6, "Databases", "schemas, SQL, joins", "walked", 1036, 430, "down"),
    (7, "TypeScript, React", "Haazir, asset tracker", "walked", 820, 512, "up"),
    (8, "Python for data", "pandas, notebooks", "walked", 600, 448, "down"),
    (9, "Data analysis", "networks, prices", "walked", 380, 528, "up"),
    (10, "Machine learning", "features and error", "walked", 168, 470, "up"),
    (11, "Applied AI", "CITY-MIND, smart city", "walked", 150, 718, "down"),
    (12, "Agentic systems", "review loops, tools, evals", "here", 400, 742, "up"),
    (13, "Cloud", "AWS, IAM, serverless", "next", 640, 668, "down"),
    (14, "DevOps", "CI/CD, K8s, Terraform", "next", 880, 742, "up"),
    (15, "Observability", "logs, metrics, traces", "later", 1060, 930, "up"),
    (16, "System design", "caches, queues, scale", "later", 880, 1010, "down"),
    (17, "Security", "auth, OWASP, secrets", "later", 690, 940, "up"),
    (18, "MLOps", "serving, evals in prod", "later", 500, 1010, "down"),
    (19, "Rust", "ship one CLI", "later", 310, 940, "up"),
    (20, "Distributed systems", "consensus, the papers", "later", 130, 1010, "down"),
]

PW, PH = 184, 62
HERE_W, HERE_H = 204, 84
STEM = 16


def _svg(w: int, h: int, title: str, desc: str, defs: str, css: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" shape-rendering="geometricPrecision">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <defs>
    <style>
{css}
    </style>
{defs}
  </defs>
{body}
</svg>
'''


def catmull_d(pts: list[tuple[float, float]]) -> str:
    """Open Catmull-Rom spline as SVG cubic commands."""
    if len(pts) < 2:
        return ""
    parts = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        parts.append(f"C{c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(parts)


def plaque_box(rx: float, ry: float, side: str, w: float, h: float) -> tuple[float, float]:
    if side == "up":
        return rx - w / 2, ry - h - STEM
    if side == "down":
        return rx - w / 2, ry + STEM
    if side == "left":
        return rx - w - STEM, ry - h / 2
    return rx + STEM, ry - h / 2


def stem_line(rx: float, ry: float, px: float, py: float, w: float, h: float, side: str, stroke: str) -> str:
    if side == "up":
        x2, y2 = px + w / 2, py + h
    elif side == "down":
        x2, y2 = px + w / 2, py
    elif side == "left":
        x2, y2 = px + w, py + h / 2
    else:
        x2, y2 = px, py + h / 2
    return f'<path d="M{rx:.1f} {ry:.1f} L{x2:.1f} {y2:.1f}" fill="none" stroke="{stroke}" stroke-width="1.4" opacity=".75"/>'


def _rivets(x: float, y: float, w: float, h: float, fill: str) -> str:
    bits = []
    for px, py in ((x + 7, y + 6), (x + w - 7, y + 6), (x + 7, y + h - 6), (x + w - 6, y + h - 6)):
        bits.append(f'<circle cx="{px}" cy="{py}" r="1.5" fill="{fill}"/>')
    return "\n".join(bits)


def ticket(x: float, y: float, w: float, h: float, fill: str, stroke: str) -> str:
    punch_y = y + h / 2
    return f'''  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="{h - 6}" rx="5" fill="none" stroke="{stroke}" stroke-width=".6" opacity=".45"/>
  <circle cx="{x}" cy="{punch_y}" r="6.5" fill="#121317"/>
  <circle cx="{x}" cy="{punch_y}" r="6.5" fill="none" stroke="{stroke}" stroke-width="1.2"/>
  <circle cx="{x}" cy="{punch_y}" r="2.2" fill="{stroke}" opacity=".55"/>
{_rivets(x, y, w, h, stroke)}'''


def chapter_title(cx: float, y: float, lead: str, rest: str, fill: str = "#E9E6DF", rest_size: float = 26) -> str:
    """Italic lead-in, bold rest, optically centred. Reads as a title page, not a HUD."""
    lead_w = ts.measure(lead + " ", "standfirst", size=18)
    rest_w = ts.measure(rest, "heading", size=rest_size, face="serif-bold", tracking=0.02, caps=False)
    x0 = cx - (lead_w + rest_w) / 2
    return (
        ts.outline(lead, "standfirst", x0, y, fill, size=18)
        + ts.outline(
            rest,
            "heading",
            x0 + lead_w,
            y,
            fill,
            size=rest_size,
            face="serif-bold",
            tracking=0.02,
            caps=False,
        )
    )


def ornament(cx: float, y: float, half: float = 90) -> str:
    return f'''<g opacity=".8">
  <path d="M{cx - half} {y} H{cx - 12}" stroke="#C9A227" stroke-width="1"/>
  <path d="M{cx + 12} {y} H{cx + half}" stroke="#C9A227" stroke-width="1"/>
  <path d="M{cx} {y - 5} L{cx + 5} {y} L{cx} {y + 5} L{cx - 5} {y} Z" fill="#C9A227"/>
</g>'''


def compass(cx: float, cy: float) -> str:
    n = ts.outline("N", "caption", cx, cy - 28, "#C9A227", "middle", size=9, face="display", tracking=0.04, caps=True)
    return f'''<g opacity=".85">
  <circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <circle cx="{cx}" cy="{cy}" r="4" fill="#C9A227"/>
  <path d="M{cx} {cy - 18} L{cx + 5} {cy} L{cx} {cy + 7} L{cx - 5} {cy} Z" fill="#C9A227"/>
  <path d="M{cx} {cy + 18} L{cx + 4} {cy} L{cx} {cy + 6} L{cx - 4} {cy} Z" fill="#3F6B62" opacity=".8"/>
  {n}
</g>'''


def plaque(st) -> str:
    n, title, sub, kind, rx, ry, side = st
    w, h = (HERE_W, HERE_H) if kind in ("here", "next") else (PW, PH)
    px, py = plaque_box(rx, ry, side, w, h)
    if kind == "walked":
        plate, inset, rail, ink, mute = "#1B1D22", "#E9E6DF", "#C9A227", "#1B1D22", "#5A564E"
    elif kind == "here":
        plate, inset, rail, ink, mute = "#2C1A12", "#F7F5F0", "#F2C14E", "#1B1D22", "#8A2E12"
    elif kind == "next":
        plate, inset, rail, ink, mute = "#1A1C22", "#E4E1D8", "#6E9C90", "#1B1D22", "#3F6B62"
    else:
        plate, inset, rail, ink, mute = "#14161A", "#B8B4AA", "#3F6B62", "#1B1D22", "#3F6B62"

    lantern = ""
    here_mark = ""
    glow = ""
    if kind == "here":
        lx, ly = px + w / 2, py - 22
        glow = f'<ellipse cx="{rx}" cy="{ry}" rx="88" ry="64" fill="url(#glow)"/>'
        lantern = f'''<g class="rm-lantern">
  <path d="M{lx} {py} V{ly + 10}" stroke="#8A6E1F" stroke-width="1.4"/>
  <ellipse cx="{lx}" cy="{ly + 10}" rx="20" ry="16" fill="url(#glow)"/>
  <rect x="{lx - 6}" y="{ly - 12}" width="12" height="4" fill="#C9A227"/>
  <path d="M{lx - 8} {ly - 8} L{lx + 8} {ly - 8} L{lx + 6} {ly + 8} L{lx - 6} {ly + 8} Z" fill="#2A2D35"/>
  <rect x="{lx - 5}" y="{ly - 4}" width="10" height="10" fill="#F2C14E"/>
</g>'''
        here_mark = ts.outline(
            "You are here",
            "standfirst",
            px + w / 2 + 6,
            py + h - 10,
            "#A33418",
            "middle",
            size=12.5,
        )
    elif kind == "next":
        here_mark = ts.outline(
            "Next target",
            "standfirst",
            px + w / 2 + 6,
            py + h - 10,
            "#2F5A52",
            "middle",
            size=12.5,
        )

    title_y = py + (27 if kind in ("here", "next") else 28)
    sub_y = py + 49
    tab_x, tab_y, tab_w = px + 14, py - 9, 28
    return f'''<g class="{"rm-here" if kind == "here" else ""}">
{glow}
{stem_line(rx, ry, px, py, w, h, side, rail)}
{lantern}
{ticket(px, py, w, h, inset, rail)}
  <rect x="{tab_x}" y="{tab_y}" width="{tab_w}" height="16" rx="2" fill="{plate}" stroke="{rail}" stroke-width="1.2"/>
  {ts.outline(f"{n:02d}", "tag", tab_x + tab_w / 2, tab_y + 12, rail, "middle", size=9, tracking=0.04)}
  {ts.outline(title, "heading", px + w / 2 + 6, title_y, ink, "middle", size=15, face="display", tracking=-0.01, caps=False, max_width=w - 28)}
  {ts.outline(sub, "standfirst", px + w / 2 + 6, sub_y, mute, "middle", size=13, max_width=w - 24)}
{here_mark}
</g>'''


def station_mark(st) -> str:
    n, _t, _s, kind, rx, ry, _side = st
    if kind == "walked":
        return (
            f'<circle cx="{rx}" cy="{ry}" r="8" fill="#C9A227" stroke="#0F1013" stroke-width="3"/>'
            f'<circle cx="{rx}" cy="{ry}" r="3" fill="#F2C14E"/>'
        )
    if kind == "here":
        return f'''<circle class="rm-pulse" cx="{rx}" cy="{ry}" r="12" fill="#F2C14E" stroke="#0F1013" stroke-width="3"/>
<circle class="rm-ring" cx="{rx}" cy="{ry}" r="12" fill="none" stroke="#F2C14E" stroke-width="1.5"/>'''
    stroke = "#6E9C90" if kind == "next" else "#3F6B62"
    return f'<circle cx="{rx}" cy="{ry}" r="7" fill="#17181C" stroke="{stroke}" stroke-width="2.6"/>'


def mini_house(x: float, y: float) -> str:
    return f'''<g transform="translate({x} {y})" opacity=".9">
  <rect x="0" y="8" width="22" height="16" fill="#2A2D35"/>
  <path d="M-3 10 L11 -4 L25 10" fill="none" stroke="#C9A227" stroke-width="1.4"/>
  <path d="M-3 10 L11 -4 L25 10 Z" fill="#1B1D22"/>
  <rect x="8" y="14" width="6" height="10" fill="#F2C14E" opacity=".85"/>
</g>'''


def mountains(x: float, y: float, peaks: list[tuple[float, float]], fill: str = "#20262B") -> str:
    """Map-style mountain range: flat-shaded peaks with a bone snow cap."""
    out = []
    for dx, hgt in peaks:
        px, half = x + dx, hgt * 0.75
        cap = hgt * 0.28
        out.append(
            f'<path d="M{px - half} {y} L{px} {y - hgt} L{px + half} {y} Z" fill="{fill}"/>'
            f'<path d="M{px} {y - hgt} L{px + half} {y} L{px + half * 0.25} {y} Z" fill="#14161A" opacity=".55"/>'
            f'<path d="M{px - cap * 0.75} {y - hgt + cap} L{px} {y - hgt} L{px + cap * 0.75} {y - hgt + cap} '
            f'L{px + cap * 0.3} {y - hgt + cap * 0.8} L{px} {y - hgt + cap * 1.05} L{px - cap * 0.35} {y - hgt + cap * 0.75} Z" '
            f'fill="#C6C2B8" opacity=".55"/>'
        )
    return "".join(out)


def map_pines(points: list[tuple[float, float, float]]) -> str:
    return "".join(
        f'<path d="M{x} {y - s} L{x + s * 0.42} {y} L{x - s * 0.42} {y} Z" fill="#243530"/>'
        f'<rect x="{x - 1}" y="{y}" width="2" height="{s * 0.2:.1f}" fill="#2A2620"/>'
        for x, y, s in points
    )


def lake(cx: float, cy: float, rx: float, ry: float) -> str:
    waves = "".join(
        f'<path d="M{cx - rx * 0.5 + i * rx * 0.34} {cy - ry * 0.15 + (i % 2) * ry * 0.4} q5 -3 10 0 t10 0" '
        f'fill="none" stroke="#6E9C90" stroke-width="1" opacity=".55"/>'
        for i in range(3)
    )
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#1B2A2A" stroke="#3F6B62" stroke-width="1.2" opacity=".9"/>'
        + waves
    )


def region_label(x: float, y: float, numeral: str, name: str, fill: str = "#8A8F99") -> str:
    """Cartographer's region name: roman numeral in brass, name in italic."""
    return (
        ts.outline(numeral, "label", x, y, "#C9A227", "middle", size=10, tracking=0.16)
        + ts.outline(name, "standfirst", x, y + 20, fill, "middle", size=17)
    )


def scale_bar(x: float, y: float) -> str:
    seg = 28
    blocks = "".join(
        f'<rect x="{x + i * seg}" y="{y}" width="{seg}" height="5" fill="{"#C9A227" if i % 2 == 0 else "#1B1D22"}" '
        f'stroke="#8A6E1F" stroke-width=".8"/>'
        for i in range(4)
    )
    return blocks + ts.outline(
        "one station, one shipped thing", "standfirst", x + 2 * seg, y + 22, "#8A8F99", "middle", size=12.5
    )


def build_roadmap() -> None:
    w, h = 1200, 1250
    css = """
.rm-pulse{animation:rmPulse 2.4s ease-in-out infinite}
@keyframes rmPulse{0%,100%{r:11}50%{r:14}}
.rm-ring{animation:rmRing 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes rmRing{0%{opacity:.7;transform:scale(1)}100%{opacity:0;transform:scale(2.3)}}
.rm-lantern rect:last-child{animation:rmLamp 2.6s ease-in-out infinite}
@keyframes rmLamp{0%,100%{opacity:.7}50%{opacity:1}}
.rm-here{animation:rmHere 3.4s ease-in-out infinite}
@keyframes rmHere{0%,100%{opacity:1}50%{opacity:.92}}
.rm-dash{stroke-dasharray:11 9;animation:rmDash 1.8s linear infinite}
@keyframes rmDash{to{stroke-dashoffset:-40}}
.rm-next{stroke-dasharray:8 8;animation:rmDash 2.6s linear infinite}
.rm-beacon{animation:rmBeacon 2.8s ease-in-out infinite}
@keyframes rmBeacon{0%,100%{opacity:.35}50%{opacity:1}}
.rm-wyrm{animation:rmWyrm 5s ease-in-out infinite}
@keyframes rmWyrm{0%,100%{transform:translate(0,0)}50%{transform:translate(0,-4px)}}
"""
    defs = '''
    <linearGradient id="deck" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0F1013"/>
      <stop offset=".6" stop-color="#1B1D23"/>
      <stop offset="1" stop-color="#121317"/>
    </linearGradient>
    <linearGradient id="brass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8A6E1F"/>
      <stop offset=".5" stop-color="#C9A227"/>
      <stop offset="1" stop-color="#E0B94A"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#C9A227"/>
      <stop offset="1" stop-color="#F2C14E"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#F2C14E" stop-opacity=".42"/>
      <stop offset=".55" stop-color="#E4572E" stop-opacity=".14"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nextGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#6E9C90" stop-opacity=".35"/>
      <stop offset="1" stop-color="#6E9C90" stop-opacity="0"/>
    </radialGradient>
'''
    rails = [(s[4], s[5]) for s in STATIONS]
    kinds = [s[3] for s in STATIONS]
    here = kinds.index("here")
    last_next = max(i for i, k in enumerate(kinds) if k == "next")
    walked_d = catmull_d(rails[: here + 1])
    working_d = catmull_d(rails[here : here + 2])
    next_d = catmull_d(rails[here + 1 : last_next + 1])
    later_d = catmull_d(rails[last_next:])

    rail = f'''  <path d="{walked_d}" fill="none" stroke="#16181E" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="{walked_d}" fill="none" stroke="url(#brass)" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="{working_d}" fill="none" stroke="url(#gold)" stroke-width="4.5" stroke-linecap="round" class="rm-dash"/>
  <path d="{next_d}" fill="none" stroke="#6E9C90" stroke-width="4" stroke-linecap="round" class="rm-next"/>
  <path d="{later_d}" fill="none" stroke="#3F6B62" stroke-width="3.5" stroke-dasharray="3 10" stroke-linecap="round" opacity=".9"/>'''

    beacons = "\n".join(
        f'<ellipse class="rm-beacon" cx="{s[4]}" cy="{s[5]}" rx="46" ry="34" fill="url(#nextGlow)"/>'
        for s in STATIONS
        if s[3] == "next"
    )
    plaques = "\n".join(plaque(s) for s in STATIONS)
    marks = "\n".join(station_mark(s) for s in STATIONS)

    counts = {k: kinds.count(k) for k in ("walked", "here", "next", "later")}
    tally = (
        f'{counts["walked"]} walked  ·  {counts["here"]} in hand  ·  '
        f'{counts["next"]} next  ·  {counts["later"]} on the horizon'
    )

    # Terrain lives in the gaps between the rows of the river, never under a ticket.
    terrain = "\n".join(
        [
            mountains(36, 600, [(18, 40), (52, 58), (88, 36)]),
            mountains(1070, 600, [(10, 34), (44, 52), (80, 40)]),
            mountains(980, 1150, [(0, 30), (34, 46), (70, 32)]),
            map_pines(
                [
                    (250, 600, 18), (268, 606, 14), (232, 608, 13),
                    (700, 596, 16), (718, 602, 12),
                    (560, 1110, 16), (578, 1116, 12), (542, 1118, 11),
                    (760, 820, 14), (776, 826, 11),
                ]
            ),
            lake(1104, 800, 50, 18),
            lake(66, 878, 34, 13),
        ]
    )
    regions = "\n".join(
        [
            region_label(880, 384, "I", "Foundations"),
            region_label(470, 598, "II", "Data country"),
            region_label(160, 808, "III", "The workshop"),
            region_label(1060, 662, "IV", "Infrastructure", "#9DBDB4"),
            region_label(400, 1130, "V", "The frontier", "#6E9C90"),
        ]
    )
    # A tiny side-on dragon in the frontier corner, where old maps put them.
    wyrm = (
        f'<g class="rm-wyrm" opacity=".85">{A.rle_rects(A.DRAGON_IDLE, 1080, 1074, 1.8)}</g>'
        + ts.outline("here be dragons", "standfirst", 1116, 1160, "#A33418", "middle", size=11)
    )

    legend_y = 1190
    legend = f'''  <g>
  <circle cx="300" cy="{legend_y}" r="6" fill="#C9A227"/>
  {ts.outline("walked", "caption", 314, legend_y + 4, "#C6C2B8", size=14, face="display-italic", tracking=0, caps=False)}
  <circle cx="430" cy="{legend_y}" r="6" fill="#F2C14E"/>
  {ts.outline("working", "caption", 444, legend_y + 4, "#C6C2B8", size=14, face="display-italic", tracking=0, caps=False)}
  <circle cx="570" cy="{legend_y}" r="6" fill="#17181C" stroke="#6E9C90" stroke-width="2"/>
  {ts.outline("next target", "caption", 584, legend_y + 4, "#C6C2B8", size=14, face="display-italic", tracking=0, caps=False)}
  <circle cx="740" cy="{legend_y}" r="6" fill="#17181C" stroke="#3F6B62" stroke-width="2"/>
  {ts.outline("on the horizon", "caption", 754, legend_y + 4, "#C6C2B8", size=14, face="display-italic", tracking=0, caps=False)}
  </g>'''

    body = f'''  <rect width="{w}" height="{h}" fill="url(#deck)"/>
  <path d="M0 1120 C 200 1092, 380 1110, 580 1100 C 800 1090, 980 1076, 1200 1094 L1200 {h} L0 {h} Z" fill="#1E262A"/>
  <path d="M0 1164 C 240 1142, 460 1158, 680 1150 C 900 1140, 1060 1154, 1200 1140 L1200 {h} L0 {h} Z" fill="#243230"/>
  <rect x="18" y="18" width="1164" height="{h - 36}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".45"/>
  <rect x="24" y="24" width="1152" height="{h - 48}" fill="none" stroke="#8A6E1F" stroke-width=".6" opacity=".25"/>
  {chapter_title(600, 64, "The", "roadmap")}
  {ornament(600, 80, 118)}
  {ts.outline("A direction of travel, kept honest.", "standfirst", 600, 104, "#9AA0AC", "middle")}
  {terrain}
  {regions}
  {ts.outline("Start", "standfirst", 128, 206, "#C9A227", "middle", size=13)}
  {ts.outline("The long run", "standfirst", 130, 1098, "#6E9C90", "middle", size=13)}
{compass(1120, 196)}
{mini_house(232, 1046)}
{scale_bar(64, 1150)}
{wyrm}
{beacons}
{rail}
{plaques}
{marks}
{legend}
  {ts.outline(tally, "standfirst", 600, 1224, "#6E9C90", "middle", size=14)}
'''
    art = _svg(
        w,
        h,
        "The roadmap",
        "A winding map of twenty stations across five regions: foundations, data, the workshop, "
        "infrastructure, and the frontier. Agentic systems is in hand; Cloud and DevOps are the next "
        "targets; observability, system design, security, MLOps, Rust, and distributed systems lie beyond.",
        defs,
        css,
        body,
    )
    A.write(A.OUT / "atelier" / "roadmap-river.svg", art)
    A.write(A.OUT / "atelier" / "roadmap-ledger.svg", art)
    A.write(A.OUT / "atelier" / "roadmap.svg", art)


def trail_moon(cx: float, cy: float, r: float = 48) -> str:
    """Blood moon with a terminator and cratered face. Not a flat sticker."""
    craters = []
    specs = (
        (0.22, -0.18, 0.22, 0.55),
        (-0.12, 0.28, 0.13, 0.7),
        (0.34, 0.16, 0.09, 0.6),
        (0.08, -0.38, 0.07, 0.65),
        (-0.28, -0.08, 0.1, 0.5),
        (0.18, 0.42, 0.06, 0.5),
    )
    for dx, dy, rr, op in specs:
        craters.append(
            f'<circle cx="{cx + dx * r}" cy="{cy + dy * r}" r="{rr * r}" fill="#7E2A12" opacity="{op}"/>'
        )
    highlight = (
        f'<path d="M{cx + r * 0.15} {cy - r * 0.82} '
        f'A{r * 0.9} {r * 0.9} 0 0 1 {cx + r * 0.82} {cy + r * 0.1}" '
        f'fill="none" stroke="#F2C14E" stroke-width="1.6" opacity=".45"/>'
    )
    return f'''<g class="moon">
  <circle cx="{cx}" cy="{cy}" r="{r + 28}" fill="url(#moonHalo)"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="#A33418" opacity=".28"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#5C1A10"/>
  <circle cx="{cx + r * 0.16}" cy="{cy - r * 0.08}" r="{r * 0.9}" fill="#A33418"/>
  <circle cx="{cx + r * 0.22}" cy="{cy - r * 0.1}" r="{r * 0.76}" fill="#E4572E"/>
  <ellipse cx="{cx - r * 0.38}" cy="{cy + r * 0.04}" rx="{r * 0.48}" ry="{r * 0.92}" fill="#3A120C" opacity=".72"/>
  {chr(10).join(craters)}
  <circle cx="{cx + r * 0.3}" cy="{cy - r * 0.22}" r="{r * 0.08}" fill="#F2A03C" opacity=".35"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#C9A227" stroke-width="1.5" opacity=".5"/>
  {highlight}
</g>'''


def forge_house(gx: float, gy: float) -> str:
    """Forge cottage at the end of the walk. gx, gy is the threshold."""
    bx, by, bw, bh = gx - 56, gy - 70, 118, 70
    peak_x, peak_y = gx + 4, gy - 118
    chx = gx + 34
    # Lean-to workshop on the left.
    lx, ly, lw, lh = bx - 36, gy - 38, 38, 38
    tiles = []
    for i in range(5):
        t = (i + 1) / 6
        y = by + 4 - t * (by + 4 - peak_y)
        inset = 10 + t * 36
        tiles.append(
            f'<path d="M{bx + inset} {y} L{bx + bw - inset} {y}" stroke="#8A6E1F" stroke-width=".7" opacity=".4"/>'
        )
    stones = []
    for i, (sx, sw) in enumerate(((-4, 22), (16, 26), (40, 20), (58, 28), (84, 24), (106, 18))):
        stones.append(
            f'<rect x="{bx + sx}" y="{gy + (i % 2)}" width="{sw}" height="{7 - i % 2}" fill="#2A2D35"/>'
        )
    return f'''<g class="tr-house">
  <ellipse cx="{gx}" cy="{gy + 10}" rx="108" ry="40" fill="url(#forgeGlow)"/>
  <path d="M{gx - 12} {gy + 2} L{gx - 34} {gy + 22} L{gx + 44} {gy + 22} L{gx + 16} {gy + 2} Z" fill="#F2C14E" opacity=".2"/>
  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#1A1C22"/>
  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="none" stroke="#3A3E48" stroke-width="1.2"/>
  <path d="M{lx - 4} {ly + 2} L{lx + lw / 2} {ly - 16} L{lx + lw + 4} {ly + 2}" fill="#252830"/>
  <path d="M{lx - 4} {ly + 2} L{lx + lw / 2} {ly - 16} L{lx + lw + 4} {ly + 2}" fill="none" stroke="#8A6E1F" stroke-width="1.3"/>
  <rect x="{lx + 10}" y="{ly + 14}" width="16" height="14" fill="#141519"/>
  <rect x="{lx + 12}" y="{ly + 16}" width="12" height="10" fill="#E4572E" class="tr-lamp" opacity=".55"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#1E2026"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#3A3E48" stroke-width="1.6"/>
  <path d="M{bx + 8} {by} V{gy} M{bx + bw - 8} {by} V{gy} M{bx} {by + 22} H{bx + bw} M{bx} {by + 46} H{bx + bw}" stroke="#141519" stroke-width="1.4"/>
  <path d="M{bx - 12} {by + 8} L{peak_x} {peak_y} L{bx + bw + 12} {by + 8} Z" fill="#252830"/>
  <path d="M{bx - 12} {by + 8} L{peak_x} {peak_y} L{bx + bw + 12} {by + 8}" fill="none" stroke="#C9A227" stroke-width="2"/>
  {chr(10).join(tiles)}
  <rect x="{chx}" y="{gy - 132}" width="18" height="50" fill="#1B1D22" stroke="#3A3E48" stroke-width="1"/>
  <path d="M{chx} {gy - 120} H{chx + 18} M{chx} {gy - 108} H{chx + 18} M{chx} {gy - 96} H{chx + 18}" stroke="#2A2D35" stroke-width="1"/>
  <rect x="{chx - 4}" y="{gy - 138}" width="26" height="7" fill="#2A2D35"/>
  <rect x="{chx + 5}" y="{gy - 132}" width="8" height="9" fill="#E4572E" class="tr-ember"/>
  <ellipse cx="{chx + 9}" cy="{gy - 142}" rx="5" ry="3.5" fill="#8A9098" opacity=".35"/>
  <ellipse cx="{chx + 14}" cy="{gy - 152}" rx="6" ry="4" fill="#8A9098" opacity=".28"/>
  <ellipse cx="{chx + 20}" cy="{gy - 164}" rx="7" ry="4.5" fill="#8A9098" opacity=".18"/>
  <rect x="{gx - 8}" y="{gy - 108}" width="12" height="10" fill="#141519"/>
  <rect x="{gx - 6}" y="{gy - 106}" width="8" height="6" fill="#F2C14E" class="tr-lamp" opacity=".7"/>
  <rect x="{gx - 42}" y="{gy - 52}" width="20" height="18" fill="#141519"/>
  <rect x="{gx - 40}" y="{gy - 50}" width="16" height="14" fill="#F2C14E" class="tr-lamp"/>
  <path d="M{gx - 32} {gy - 52} V{gy - 34} M{gx - 42} {gy - 43} H{gx - 22}" stroke="#1B1D22" stroke-width="1.3"/>
  <rect x="{gx + 24}" y="{gy - 52}" width="20" height="18" fill="#141519"/>
  <rect x="{gx + 26}" y="{gy - 50}" width="16" height="14" fill="#E4572E" class="tr-lamp" opacity=".85"/>
  <path d="M{gx + 34} {gy - 52} V{gy - 34} M{gx + 24} {gy - 43} H{gx + 44}" stroke="#1B1D22" stroke-width="1.3"/>
  <path d="M{gx - 11} {gy - 10} L{gx - 11} {gy + 1} Q{gx} {gy + 8} {gx + 11} {gy + 1} L{gx + 11} {gy - 10} Q{gx} {gy - 22} {gx - 11} {gy - 10} Z" fill="#141519"/>
  <path d="M{gx - 8} {gy - 8} L{gx - 8} {gy} Q{gx} {gy + 4} {gx + 8} {gy} L{gx + 8} {gy - 8} Q{gx} {gy - 18} {gx - 8} {gy - 8} Z" fill="#F2C14E" class="tr-lamp" opacity=".92"/>
  <circle cx="{gx + 6}" cy="{gy - 5}" r="1.4" fill="#C9A227"/>
  <rect x="{gx - 14}" y="{gy + 1}" width="8" height="4" fill="#2A2D35"/>
  <rect x="{gx + 6}" y="{gy + 1}" width="8" height="4" fill="#2A2D35"/>
  {chr(10).join(stones)}
  <rect x="{bx - 18}" y="{gy - 16}" width="5" height="22" fill="#2A2D35"/>
  <rect x="{bx + bw + 14}" y="{gy - 16}" width="5" height="22" fill="#2A2D35"/>
  <path d="M{bx - 18} {gy - 16} H{bx + bw + 19}" stroke="#8A6E1F" stroke-width="1.4"/>
  <circle cx="{gx - 86}" cy="{gy - 20}" r="5.5" fill="#F2C14E" class="tr-lamp" opacity=".8"/>
  <path d="M{gx - 86} {gy - 14} V{gy + 2}" stroke="#8A6E1F" stroke-width="1.5"/>
  <path d="M{gx - 86} {gy - 28} A7 6 0 0 1 {gx - 86} {gy - 14}" fill="none" stroke="#C9A227" stroke-width="1.3"/>
  <ellipse cx="{gx + 62}" cy="{gy + 6}" rx="7" ry="5" fill="#2A2D35"/>
  <rect x="{gx + 56}" y="{gy - 6}" width="12" height="12" rx="2" fill="#1B1D22" stroke="#8A6E1F" stroke-width=".8"/>
</g>'''


def trail_smoke(x: float, y: float) -> tuple[str, str]:
    rules = []
    groups = []
    for i in range(5):
        cls = f"tr-smoke-{i}"
        name = f"trSmoke{i}"
        delay = i * 0.55
        dx, dy = 6 + i * 5, -40 - i * 9
        rules.append(
            f".{cls}{{opacity:0;animation:{name} 3.4s linear infinite;animation-delay:{delay:.2f}s}}"
            f"@keyframes {name}{{0%{{opacity:0;transform:translate(0,0)}}"
            f"16%{{opacity:.55;transform:translate({dx * 0.28:.0f}px,{-abs(dy) * 0.22:.0f}px)}}"
            f"100%{{opacity:0;transform:translate({dx}px,{dy}px)}}}}"
        )
        groups.append(
            f'<circle class="{cls}" cx="{x + i * 2.4}" cy="{y}" r="{3.6 + i * 0.6}" fill="#8A9098"/>'
        )
    return "\n".join(rules), "\n".join(groups)


def tiny_walker() -> str:
    return """<g transform="translate(-16 -26)">
  <rect x="2" y="8" width="6" height="5" fill="#C0431F"/>
  <rect x="8" y="6" width="8" height="8" fill="#C0431F"/>
  <rect x="14" y="8" width="6" height="5" fill="#E0B457"/>
  <rect x="18" y="9" width="3" height="3" fill="#14161A"/>
  <rect x="6" y="14" width="3" height="4" fill="#7E2A12"/>
  <rect x="12" y="14" width="3" height="4" fill="#7E2A12"/>
  <rect x="0" y="10" width="4" height="2" fill="#C0431F"/>
  <rect x="21" y="9" width="3" height="2" fill="#F2C14E"/>
</g>"""


def trail_walk_css() -> str:
    pts = [
        (52, 318),
        (150, 308),
        (250, 322),
        (360, 310),
        (480, 298),
        (590, 316),
        (700, 308),
        (790, 300),
        (858, 300),
        (890, 292),
    ]
    keys = []
    n = len(pts) - 1
    for i, (x, y) in enumerate(pts):
        pct = 100.0 * i / n
        keys.append(f"{pct:.1f}%{{transform:translate({x}px,{y}px)}}")
    return (
        ".tr-walk{animation:trWalk 16s linear infinite}"
        "@keyframes trWalk{" + "".join(keys) + "}"
    )


def pine(x: float, y: float, hgt: float) -> str:
    half = 14 + hgt * 0.08
    return (
        f'<polygon points="{x - half},{y} {x},{y - hgt} {x + half},{y}" fill="#1F2C2A"/>'
        f'<polygon points="{x - half * 0.7},{y - hgt * 0.28} {x},{y - hgt * 0.72} {x + half * 0.7},{y - hgt * 0.28}" fill="#243530"/>'
    )


def build_trail() -> None:
    w, h = 1000, 420
    house_x, house_y = 905, 286
    smoke_css, smoke = trail_smoke(944, 148)
    css = f"""
.moon{{animation:moonPulse 7.5s ease-in-out infinite}}
@keyframes moonPulse{{0%,100%{{opacity:.9}}50%{{opacity:1}}}}
.tr-lamp{{animation:trLamp 2.6s ease-in-out infinite}}
@keyframes trLamp{{0%,100%{{opacity:.62}}50%{{opacity:1}}}}
.tr-ember{{animation:trEmber 1.8s ease-in-out infinite}}
@keyframes trEmber{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}
{smoke_css}
{trail_walk_css()}
"""
    defs = '''
    <linearGradient id="trailSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0C0D10"/>
      <stop offset=".5" stop-color="#16181E"/>
      <stop offset="1" stop-color="#20282A"/>
    </linearGradient>
    <radialGradient id="forgeGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#F2C14E" stop-opacity=".55"/>
      <stop offset=".5" stop-color="#E4572E" stop-opacity=".2"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="moonHalo" cx="50%" cy="45%" r="50%">
      <stop offset="0" stop-color="#E4572E" stop-opacity=".5"/>
      <stop offset=".55" stop-color="#A33418" stop-opacity=".16"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
'''
    # x, y, sign width, label, state, lean. state: walked, here, next.
    posts = [
        (64, 268, 98, "Fundamentals", "walked", -2.2),
        (176, 260, 84, "Web craft", "walked", 1.8),
        (290, 250, 86, "Backends", "walked", -1.4),
        (404, 254, 92, "Data and AI", "walked", 1.2),
        (540, 246, 128, "Agentic systems", "here", 0.0),
        (668, 252, 66, "Cloud", "next", -1.6),
        (770, 256, 74, "DevOps", "next", 1.4),
    ]
    signs = []
    for x, y, bw, label, state, rot in posts:
        here = state == "here"
        fill = {"here": "#F7F5F0", "next": "#D4D0C6"}.get(state, "#E9E6DF")
        stroke = {"here": "#F2C14E", "next": "#6E9C90"}.get(state, "#8A6E1F")
        extra = ""
        hgt = 36 if here else 28
        sy = y - (hgt + 8)
        if here:
            extra = ts.outline(
                "You are here",
                "standfirst",
                x + 4,
                sy + hgt - 7,
                "#A33418",
                "middle",
                size=10,
            )
        signs.append(
            f'''<g transform="rotate({rot} {x + 4} {y})">
  <rect x="{x}" y="{y}" width="8" height="{340 - y}" fill="#2A2620"/>
  <rect x="{x + 4 - bw / 2}" y="{sy}" width="{bw}" height="{hgt}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="{2.2 if here else 1.3}"/>
  {_rivets(x + 4 - bw / 2, sy, bw, hgt, stroke)}
  {ts.outline(label, "heading", x + 4, sy + (18 if not here else 16), "#1B1D22", "middle", size=12.5, face="display", tracking=-0.015, caps=False, max_width=bw - 10)}
{extra}
</g>'''
        )

    trees = "\n".join(
        [
            pine(30, 270, 56),
            pine(232, 258, 74),
            pine(350, 250, 64),
            pine(470, 246, 58),
            pine(616, 242, 52),
            pine(722, 250, 44),
        ]
    )

    body = f'''  <rect width="{w}" height="{h}" fill="url(#trailSky)"/>
  {trail_moon(882, 68, 52)}
  <circle cx="140" cy="42" r="1.2" fill="#E9E6DF" opacity=".4"/>
  <circle cx="280" cy="58" r="1.0" fill="#E9E6DF" opacity=".32"/>
  <circle cx="430" cy="34" r="1.3" fill="#E9E6DF" opacity=".38"/>
  <circle cx="580" cy="50" r="1.1" fill="#E9E6DF" opacity=".3"/>
  <circle cx="640" cy="28" r="0.9" fill="#E9E6DF" opacity=".28"/>
  <path d="M0 228 C 160 188, 300 208, 460 196 C 640 182, 780 168, 1000 188 L1000 420 L0 420 Z" fill="#1C2226"/>
  <path d="M0 286 C 180 258, 340 278, 520 266 C 700 254, 850 238, 1000 268 L1000 420 L0 420 Z" fill="#212B2C"/>
  <path d="M0 348 C 170 322, 320 340, 520 328 C 700 318, 850 334, 1000 318 L1000 420 L0 420 Z" fill="#26332F"/>
  <g>{trees}</g>
  <path d="M36 318 C 150 306, 250 328, 360 314 C 490 298, 600 322, 710 308 C 800 296, 860 306, 960 288" fill="none" stroke="#2A2620" stroke-width="20" stroke-linecap="round"/>
  <path d="M36 318 C 150 306, 250 328, 360 314 C 490 298, 600 322, 710 308 C 800 296, 860 306, 960 288" fill="none" stroke="#8A6E1F" stroke-width="6.5" stroke-linecap="round"/>
{chr(10).join(signs)}
{forge_house(house_x, house_y)}
{smoke}
  {chapter_title(430, 50, "The", "long walk", rest_size=24)}
  {ornament(430, 66, 92)}
  {ts.outline("Same route, on foot, after dark.", "standfirst", 430, 88, "#9AA0AC", "middle")}
  <g class="tr-walk">
{tiny_walker()}
  </g>
  {ts.outline("Then: observability, system design, security, MLOps, Rust, distributed systems.", "standfirst", 500, 400, "#6E9C90", "middle", size=12)}
'''
    art = _svg(
        w,
        h,
        "The long walk",
        "The same route on foot after dark: signposts across the ridges toward a lit cottage, with a small companion on the path.",
        defs,
        css,
        body,
    )
    A.write(A.OUT / "atelier" / "trail-cottage.svg", art)
    A.write(A.OUT / "atelier" / "trail-night.svg", art)
    A.write(A.OUT / "atelier" / "trail.svg", art)
    A.write(A.OUT / "odyssey.svg", art)


def build() -> None:
    build_roadmap()
    build_trail()


if __name__ == "__main__":
    build()
