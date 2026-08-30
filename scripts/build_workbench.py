#!/usr/bin/env python3
"""The workbench as a smithy interior, not a card grid.

Languages hang on the pegboard. Web cools as ingots. Data sits in jars.
Infrastructure is a crate pile. Intelligence is the hearth. Current work
is a job ticket clipped to the anvil.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import typeset as ts
from build_atelier import (  # noqa: E402
    LANTERN_CORE,
    OUT,
    TEACUP,
    fireflies,
    rle_rects,
    sitting_dragon,
    svg_wrap,
    write,
)

OBS = "#0F1013"
GRAPHITE = "#17181C"
SLATE = "#1E2026"
IRON = "#2A2D35"
STEEL = "#3A3E48"
SMOKE = "#6B7078"
MUTE = "#9AA0AC"
BONE = "#E9E6DF"
CHALK = "#F7F5F0"
ASH = "#C6C2B8"
INK = "#1B1D22"
BRASS = "#C9A227"
BRASS_DK = "#8A6E1F"
GOLD = "#F2C14E"
EMBER = "#E4572E"
EMBER_DK = "#A33418"
PATINA = "#3F6B62"
PATINA_LT = "#6E9C90"
WOOD = "#3A342C"
WOOD_DK = "#241F1A"


def n(v: float) -> str:
    s = f"{v:.1f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def outline(text, role, x, y, fill, anchor="start", **over) -> str:
    return ts.outline(text, role, x, y, fill, anchor, **over)


def swinging(cx: float, cy: float, dur: str, begin: str, inner: str) -> str:
    return f'''<g>
  <animateTransform attributeName="transform" type="rotate" values="0 {n(cx)} {n(cy)}; 1.4 {n(cx)} {n(cy)}; -1.1 {n(cx)} {n(cy)}; 0 {n(cx)} {n(cy)}" dur="{dur}" begin="{begin}" repeatCount="indefinite"/>
{inner}
</g>'''


def hook(cx: float, cy: float) -> str:
    return (
        f'<circle cx="{n(cx)}" cy="{n(cy)}" r="3.2" fill="{STEEL}" stroke="{BRASS_DK}" stroke-width="1.2"/>'
        f'<path d="M{n(cx)} {n(cy + 3)} V{n(cy + 12)} Q{n(cx)} {n(cy + 18)} {n(cx + 7)} {n(cy + 18)}" '
        f'fill="none" stroke="{BRASS}" stroke-width="2" stroke-linecap="square"/>'
    )


def name_tag(cx: float, y: float, text: str) -> str:
    tw = ts.measure(text, "tag", size=9, tracking=0.05)
    w = max(tw + 14, 46)
    x = cx - w / 2
    return (
        f'<path d="M{n(cx)} {n(y - 7)} V{n(y)}" stroke="{BRASS_DK}" stroke-width="1"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="15" fill="{BONE}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="2" fill="{BRASS}"/>'
        f'{outline(text, "tag", cx, y + 12, INK, "middle", size=9, tracking=0.05, max_width=w - 8)}'
    )


def tool_hammer(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <rect x="{n(x - 3.5)}" y="{n(y)}" width="7" height="44" fill="{WOOD}"/>
  <rect x="{n(x - 5)}" y="{n(y + 42)}" width="10" height="5" fill="{BRASS}"/>
  <rect x="{n(x - 20)}" y="{n(y + 46)}" width="42" height="14" fill="{IRON}"/>
  <rect x="{n(x + 18)}" y="{n(y + 48)}" width="7" height="10" fill="{BRASS}"/>
  <rect x="{n(x - 24)}" y="{n(y + 49)}" width="6" height="8" fill="{STEEL}"/>
</g>'''


def tool_saw(hx: float, hy: float) -> str:
    x, y = hx, hy
    teeth = []
    px = x + 10
    while px < x + 58:
        teeth.append(f"L{n(px)} {n(y + 20)} L{n(px + 3)} {n(y + 14)}")
        px += 6
    return f'''<g>
  <path d="M{n(x - 6)} {n(y)} H{n(x + 12)} V{n(y + 18)} L{n(x + 2)} {n(y + 26)} L{n(x - 10)} {n(y + 18)} Z"
        fill="{WOOD}" stroke="{WOOD_DK}" stroke-width="1"/>
  <circle cx="{n(x + 3)}" cy="{n(y + 10)}" r="2.2" fill="{WOOD_DK}"/>
  <path d="M{n(x + 10)} {n(y + 6)} L{n(x + 62)} {n(y + 8)} L{n(x + 58)} {n(y + 20)} L{n(x + 10)} {n(y + 18)} Z" fill="{STEEL}"/>
  <path d="M{n(x + 10)} {n(y + 18)} {' '.join(teeth)}" fill="none" stroke="{IRON}" stroke-width="1.2"/>
</g>'''


def tool_file(hx: float, hy: float) -> str:
    """Mill file: long parallel body with teeth on both edges."""
    x, y = hx, hy
    teeth_l = "".join(
        f'<path d="M{n(x - 5)} {n(y + 24 + i * 4)} L{n(x - 8)} {n(y + 26 + i * 4)}" stroke="{STEEL}" stroke-width="1.2"/>'
        for i in range(8)
    )
    teeth_r = "".join(
        f'<path d="M{n(x + 5)} {n(y + 24 + i * 4)} L{n(x + 8)} {n(y + 26 + i * 4)}" stroke="{STEEL}" stroke-width="1.2"/>'
        for i in range(8)
    )
    return f'''<g>
  <rect x="{n(x - 6)}" y="{n(y)}" width="12" height="18" fill="{WOOD}"/>
  <rect x="{n(x - 7)}" y="{n(y + 16)}" width="14" height="5" fill="{BRASS_DK}"/>
  <rect x="{n(x - 5)}" y="{n(y + 21)}" width="10" height="38" fill="{ASH}"/>
  <rect x="{n(x - 5)}" y="{n(y + 21)}" width="10" height="38" fill="none" stroke="{STEEL}" stroke-width="1"/>
  {teeth_l}{teeth_r}
  <path d="M{n(x - 5)} {n(y + 59)} H{n(x + 5)} L{n(x)} {n(y + 64)} Z" fill="{STEEL}"/>
</g>'''


def tool_wrench(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <path d="M{n(x - 14)} {n(y)} H{n(x - 2)} V{n(y + 9)} H{n(x + 2)} V{n(y)} H{n(x + 14)}
           V{n(y + 8)} L{n(x + 6)} {n(y + 16)} V{n(y + 54)} H{n(x - 6)} V{n(y + 16)}
           L{n(x - 14)} {n(y + 8)} Z" fill="{STEEL}" stroke="{IRON}" stroke-width="1"/>
  <rect x="{n(x - 3.5)}" y="{n(y + 22)}" width="7" height="20" fill="{BRASS_DK}" opacity=".75"/>
</g>'''


def tool_square(hx: float, hy: float) -> str:
    x, y = hx, hy
    ticks = "".join(
        f'<path d="M{n(hx + 10 + i * 8)} {n(y + 48)} V{n(y + 53)}" stroke="{BRASS_DK}" stroke-width="1"/>'
        for i in range(5)
    )
    return f'''<g>
  <rect x="{n(x - 7)}" y="{n(y)}" width="14" height="50" fill="{WOOD}"/>
  <rect x="{n(x - 7)}" y="{n(y + 44)}" width="56" height="10" fill="{STEEL}"/>
  {ticks}
</g>'''


def tool_tongs(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <path d="M{n(x - 6)} {n(y)} L{n(x - 10)} {n(y + 34)} Q{n(x - 18)} {n(y + 48)} {n(x - 6)} {n(y + 58)}"
        fill="none" stroke="{STEEL}" stroke-width="3.4" stroke-linecap="square"/>
  <path d="M{n(x + 6)} {n(y)} L{n(x + 10)} {n(y + 34)} Q{n(x + 18)} {n(y + 48)} {n(x + 6)} {n(y + 58)}"
        fill="none" stroke="{STEEL}" stroke-width="3.4" stroke-linecap="square"/>
  <circle cx="{n(x)}" cy="{n(y + 32)}" r="3.6" fill="{BRASS}"/>
</g>'''


def tool_chisel(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <rect x="{n(x - 5)}" y="{n(y)}" width="10" height="22" fill="{WOOD}"/>
  <rect x="{n(x - 6)}" y="{n(y + 20)}" width="12" height="5" fill="{BRASS}"/>
  <path d="M{n(x - 4)} {n(y + 25)} H{n(x + 4)} L{n(x + 1.5)} {n(y + 54)} H{n(x - 1.5)} Z" fill="{STEEL}"/>
  <path d="M{n(x - 1.5)} {n(y + 54)} H{n(x + 1.5)} L{n(x)} {n(y + 62)} Z" fill="{BRASS}"/>
</g>'''


def tool_mallet(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <rect x="{n(x - 3.5)}" y="{n(y)}" width="7" height="38" fill="{WOOD}"/>
  <rect x="{n(x - 17)}" y="{n(y + 36)}" width="34" height="20" fill="{WOOD}"/>
  <rect x="{n(x - 17)}" y="{n(y + 36)}" width="34" height="20" fill="none" stroke="{WOOD_DK}" stroke-width="1.5"/>
  <rect x="{n(x - 15)}" y="{n(y + 38)}" width="30" height="4" fill="{BRASS_DK}" opacity=".55"/>
</g>'''


def tool_awl(hx: float, hy: float) -> str:
    x, y = hx, hy
    return f'''<g>
  <rect x="{n(x - 5)}" y="{n(y)}" width="10" height="16" fill="{WOOD}"/>
  <rect x="{n(x - 4)}" y="{n(y + 14)}" width="8" height="4" fill="{BRASS}"/>
  <path d="M{n(x - 1.6)} {n(y + 18)} H{n(x + 1.6)} L{n(x)} {n(y + 62)} Z" fill="{STEEL}"/>
</g>'''


def pegboard(x: float, y: float, w: float, h: float) -> str:
    holes = []
    py = y + 16
    row = 0
    while py < y + h - 12:
        px = x + 16 + (8 if row % 2 else 0)
        while px < x + w - 12:
            holes.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="2.05" fill="{OBS}"/>')
            px += 16
        py += 16
        row += 1
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="#1B1D22"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="5" fill="{BRASS_DK}"/>'
        f'<rect x="{n(x)}" y="{n(y + h - 5)}" width="{n(w)}" height="5" fill="{IRON}"/>'
        + "".join(holes)
    )


def rail_stamp(x: float, y: float, text: str, w: float) -> str:
    """Brass nameplate screwed to a rail, not a floating card."""
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="16" fill="{IRON}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="16" fill="none" stroke="{BRASS}" stroke-width="1"/>'
        f'<circle cx="{n(x + 5)}" cy="{n(y + 8)}" r="1.4" fill="{BRASS}"/>'
        f'<circle cx="{n(x + w - 5)}" cy="{n(y + 8)}" r="1.4" fill="{BRASS}"/>'
        f'{outline(text, "label", x + w / 2, y + 12, BRASS, "middle", size=8, tracking=0.16, max_width=w - 16)}'
    )


def ingot(x: float, y: float, w: float, label: str, top: str, front: str) -> str:
    """A cooling bar: top face, front bevel, brass stamped end."""
    fh = 7
    return f'''<g>
  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="15" fill="{top}"/>
  <rect x="{n(x)}" y="{n(y + 15)}" width="{n(w)}" height="{fh}" fill="{front}"/>
  <path d="M{n(x + w)} {n(y)} L{n(x + w + 8)} {n(y + 5)} L{n(x + w + 8)} {n(y + 15 + fh)} L{n(x + w)} {n(y + 15 + fh)}" fill="{ASH}"/>
  <rect x="{n(x)}" y="{n(y)}" width="6" height="{15 + fh}" fill="{BRASS}"/>
  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{15 + fh}" fill="none" stroke="{BRASS_DK}" stroke-width="0.8"/>
  {outline(label, "tag", x + 12, y + 12, INK, size=9.5, tracking=0.06, max_width=w - 18)}
</g>'''


def jar(cx: float, y: float, label: str) -> str:
    return f'''<g>
  <ellipse cx="{n(cx)}" cy="{n(y)}" rx="17" ry="5" fill="{BRASS}"/>
  <rect x="{n(cx - 15)}" y="{n(y)}" width="30" height="44" fill="{PATINA}"/>
  <rect x="{n(cx - 12)}" y="{n(y + 4)}" width="4" height="28" fill="{PATINA_LT}" opacity=".4"/>
  <ellipse cx="{n(cx)}" cy="{n(y + 44)}" rx="15" ry="5" fill="#2F5A52"/>
  <rect x="{n(cx - 17)}" y="{n(y + 16)}" width="34" height="13" fill="{BONE}"/>
  {outline(label, "tag", cx, y + 26, INK, "middle", size=7.5, tracking=0.04, max_width=32)}
</g>'''


def crate(x: float, y: float, w: float, h: float, label: str, rot: float = 0) -> str:
    g_open = f'<g transform="rotate({rot} {n(x + w / 2)} {n(y + h / 2)})">' if rot else "<g>"
    return f'''{g_open}
  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{WOOD}"/>
  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="none" stroke="{WOOD_DK}" stroke-width="2"/>
  <path d="M{n(x + 7)} {n(y + h * 0.38)} H{n(x + w - 7)}" stroke="{WOOD_DK}" stroke-width="1.2"/>
  <path d="M{n(x + 7)} {n(y + h * 0.62)} H{n(x + w - 7)}" stroke="{WOOD_DK}" stroke-width="1.2"/>
  <rect x="{n(x)}" y="{n(y)}" width="7" height="7" fill="{BRASS_DK}"/>
  <rect x="{n(x + w - 7)}" y="{n(y)}" width="7" height="7" fill="{BRASS_DK}"/>
  <rect x="{n(x)}" y="{n(y + h - 7)}" width="7" height="7" fill="{BRASS_DK}"/>
  <rect x="{n(x + w - 7)}" y="{n(y + h - 7)}" width="7" height="7" fill="{BRASS_DK}"/>
  {outline(label, "tag", x + w / 2, y + h / 2 + 4, BONE, "middle", size=9, tracking=0.05, max_width=w - 12)}
</g>'''


def kettle(cx: float, y: float) -> str:
    steam = []
    for i, dx in enumerate((-8, 0, 8)):
        steam.append(
            f'''<g fill="{SMOKE}" opacity="0">
  <ellipse cx="{n(cx + dx)}" cy="{n(y - 6)}" rx="5" ry="7"/>
  <animate attributeName="opacity" values="0;0.55;0" dur="{2.2 + i * 0.2}s" begin="{i * 0.25}s" repeatCount="indefinite"/>
  <animateTransform attributeName="transform" type="translate" values="0 0; {dx * 0.35} -26" dur="{2.2 + i * 0.2}s" begin="{i * 0.25}s" repeatCount="indefinite"/>
</g>'''
        )
    return f'''<g>
  {"".join(steam)}
  <path d="M{n(cx - 20)} {n(y + 16)} C{n(cx - 20)} {n(y - 4)} {n(cx + 20)} {n(y - 4)} {n(cx + 20)} {n(y + 16)}
           L{n(cx + 16)} {n(y + 34)} C{n(cx + 16)} {n(y + 44)} {n(cx - 16)} {n(y + 44)} {n(cx - 16)} {n(y + 34)} Z"
        fill="{IRON}" stroke="{STEEL}" stroke-width="1.5"/>
  <path d="M{n(cx + 20)} {n(y + 14)} C{n(cx + 36)} {n(y + 14)} {n(cx + 36)} {n(y + 32)} {n(cx + 18)} {n(y + 32)}"
        fill="none" stroke="{BRASS}" stroke-width="3.5"/>
  <ellipse cx="{n(cx)}" cy="{n(y + 2)}" rx="13" ry="3.5" fill="{STEEL}"/>
  <rect x="{n(cx - 3.5)}" y="{n(y - 8)}" width="7" height="7" fill="{BRASS}"/>
  <path d="M{n(cx - 16)} {n(y + 22)} H{n(cx + 16)}" stroke="{BRASS}" stroke-width="2"/>
</g>'''


def letter_stamp(x: float, y: float, label: str) -> str:
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="26" height="26" fill="{IRON}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="26" height="3" fill="{BRASS_DK}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="26" height="26" fill="none" stroke="{STEEL}" stroke-width="1"/>'
        f'{outline(label, "tag", x + 13, y + 18, BONE, "middle", size=9, tracking=0.04, max_width=20)}'
    )


def anvil(x: float, y: float) -> str:
    return f'''<g>
  <rect x="{n(x + 16)}" y="{n(y + 60)}" width="84" height="38" fill="{WOOD}"/>
  <rect x="{n(x + 16)}" y="{n(y + 60)}" width="84" height="4" fill="{WOOD_DK}"/>
  <path d="M{n(x + 28)} {n(y + 68)} V{n(y + 94)}" stroke="{WOOD_DK}" stroke-width="1"/>
  <path d="M{n(x + 58)} {n(y + 68)} V{n(y + 94)}" stroke="{WOOD_DK}" stroke-width="1"/>
  <rect x="{n(x + 8)}" y="{n(y + 50)}" width="100" height="12" fill="{STEEL}"/>
  <path d="M{n(x + 36)} {n(y + 26)} H{n(x + 80)} L{n(x + 90)} {n(y + 50)} H{n(x + 26)} Z" fill="{IRON}"/>
  <rect x="{n(x + 26)}" y="{n(y + 12)}" width="84" height="16" fill="{STEEL}"/>
  <rect x="{n(x + 26)}" y="{n(y + 12)}" width="84" height="3" fill="{BRASS}"/>
  <path d="M{n(x + 26)} {n(y + 14)} L{n(x - 4)} {n(y + 26)} L{n(x + 4)} {n(y + 32)} L{n(x + 26)} {n(y + 26)} Z" fill="{STEEL}"/>
  <rect x="{n(x + 96)}" y="{n(y + 16)}" width="6" height="6" fill="{OBS}"/>
  <rect x="{n(x + 38)}" y="{n(y + 6)}" width="48" height="7" fill="{EMBER}">
    <animate attributeName="opacity" values=".7;1;.7" dur="1.6s" repeatCount="indefinite"/>
  </rect>
  <rect x="{n(x + 42)}" y="{n(y + 7)}" width="18" height="5" fill="{GOLD}" opacity=".85"/>
</g>'''


def job_ticket(x: float, y: float) -> str:
    """Shop ticket clipped to the anvil horn. Live work, one object."""
    w, h = 196, 108
    return f'''<g transform="rotate(-4.5 {n(x + 16)} {n(y)})">
  <rect x="{n(x + 14)}" y="{n(y - 10)}" width="26" height="14" fill="{BRASS}"/>
  <path d="M{n(x + 16)} {n(y - 10)} H{n(x + 38)} V{n(y - 16)} H{n(x + 16)} Z" fill="{BRASS_DK}"/>
  <rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" fill="{CHALK}"/>
  <path d="M{n(x + w - 18)} {n(y)} L{n(x + w)} {n(y + 16)} V{n(y)} Z" fill="{ASH}"/>
  <rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" fill="none" stroke="{BRASS_DK}" stroke-width="1.6"/>
  <rect x="{n(x)}" y="{n(y)}" width="{w}" height="4" fill="{GOLD}"/>
  <circle cx="{n(x + w - 18)}" cy="{n(y + 20)}" r="4" fill="{EMBER}">
    <animate attributeName="opacity" values=".35;1;.35" dur="2.8s" repeatCount="indefinite"/>
  </circle>
  {outline("In hand", "label", x + 14, y + 24, EMBER_DK, size=9.5, tracking=0.16)}
  <path d="M{n(x + 14)} {n(y + 32)} H{n(x + w - 20)}" stroke="{BRASS}" stroke-width="1"/>
  <path d="M{n(x + 14)} {n(y + 50)} H{n(x + w - 18)}" stroke="{ASH}" stroke-width="1"/>
  <path d="M{n(x + 14)} {n(y + 70)} H{n(x + w - 18)}" stroke="{ASH}" stroke-width="1"/>
  <path d="M{n(x + 14)} {n(y + 90)} H{n(x + w - 18)}" stroke="{ASH}" stroke-width="1"/>
  {outline("agentic review loops", "body", x + 14, y + 48, INK, size=12.5)}
  {outline("local tools with manners", "body", x + 14, y + 68, INK, size=12.5)}
  {outline("systems people can keep", "body", x + 14, y + 88, INK, size=12.5)}
</g>'''


def hanging_tools() -> str:
    specs = [
        (156, "PYTHON", tool_hammer, "4.8s", "0s"),
        (266, "TS", tool_saw, "5.2s", "0.3s"),
        (376, "JS", tool_file, "5.6s", "0.1s"),
        (486, "GO", tool_wrench, "4.6s", "0.5s"),
        (596, "SQL", tool_square, "5.4s", "0.2s"),
        (706, "C++", tool_tongs, "5.0s", "0.4s"),
        (816, "C", tool_chisel, "5.8s", "0.15s"),
        (926, "PHP", tool_mallet, "4.9s", "0.35s"),
        (1036, "SHELL", tool_awl, "5.3s", "0.25s"),
    ]
    hook_y = 122
    parts = [rail_stamp(48, 104, "LANGUAGES", 102)]
    for hx, label, drawer, dur, begin in specs:
        hang = (hx, hook_y + 18)
        body = drawer(*hang)
        tag_y = hang[1] + 70
        parts.append(hook(hx, hook_y))
        parts.append(swinging(hang[0], hang[1], dur, begin, body + name_tag(hx, tag_y, label)))
    return "\n".join(parts)


def ingot_rack() -> str:
    bars = [
        (148, "REACT", BONE, ASH),
        (136, "NEXT.JS", ASH, "#9C9484"),
        (128, "VITE", BONE, ASH),
        (142, "TAILWIND", ASH, "#9C9484"),
        (122, "THREE.JS", BONE, ASH),
        (134, "NODE", ASH, "#9C9484"),
        (140, "FASTAPI", BONE, ASH),
        (130, "DJANGO", ASH, "#9C9484"),
    ]
    bits = [
        f'<rect x="52" y="318" width="8" height="292" fill="{IRON}"/>',
        f'<rect x="214" y="318" width="8" height="292" fill="{IRON}"/>',
        f'<rect x="48" y="606" width="180" height="8" fill="{STEEL}"/>',
        f'<rect x="70" y="332" width="120" height="3" fill="{BRASS_DK}"/>',
        rail_stamp(70, 312, "WEB", 56),
    ]
    for i, (width, label, top, front) in enumerate(bars):
        bits.append(ingot(64, 344 + i * 32, width, label, top, front))
    return "\n".join(bits)


def hearth_basin() -> str:
    """One forge pit. Labels are iron tags stuck in the ash, not a grid of pots."""
    tags = [
        (708, 598, "OPENAI", -12),
        (768, 628, "ANTHROPIC", 8),
        (838, 636, "LANGCHAIN", -6),
        (900, 618, "MCP", 14),
        (892, 568, "HF", -8),
        (746, 558, "TORCH", 10),
    ]
    bits = [
        '<ellipse cx="810" cy="600" rx="128" ry="52" fill="url(#hearth)">'
        '<animate attributeName="opacity" values=".4;.95;.4" dur="2.4s" repeatCount="indefinite"/>'
        "</ellipse>",
        f'<ellipse cx="810" cy="608" rx="118" ry="40" fill="{IRON}"/>',
        f'<ellipse cx="810" cy="600" rx="100" ry="30" fill="{WOOD_DK}"/>',
        f'<ellipse cx="810" cy="596" rx="70" ry="20" fill="{EMBER_DK}">'
        '<animate attributeName="opacity" values=".55;1;.55" dur="1.8s" repeatCount="indefinite"/>'
        "</ellipse>",
        f'<ellipse cx="800" cy="590" rx="22" ry="10" fill="{EMBER}"/>',
        f'<ellipse cx="828" cy="594" rx="18" ry="8" fill="{GOLD}" opacity=".8"/>',
        f'<ellipse cx="786" cy="598" rx="14" ry="7" fill="{EMBER}"/>',
        f'<ellipse cx="818" cy="586" rx="10" ry="5" fill="{GOLD}"/>',
        rail_stamp(748, 542, "AGENTS", 70),
    ]
    for x, y, label, rot in tags:
        tw = max(ts.measure(label, "tag", size=8, tracking=0.04) + 12, 36)
        bits.append(
            f'<g transform="rotate({rot} {n(x)} {n(y)})">'
            f'<rect x="{n(x - tw / 2)}" y="{n(y)}" width="{n(tw)}" height="13" fill="{IRON}"/>'
            f'<rect x="{n(x - tw / 2)}" y="{n(y)}" width="{n(tw)}" height="13" fill="none" stroke="{BRASS_DK}" stroke-width="1"/>'
            f'<rect x="{n(x - 1)}" y="{n(y - 8)}" width="2" height="8" fill="{STEEL}"/>'
            f'{outline(label, "tag", x, y + 10, BONE, "middle", size=8, tracking=0.04, max_width=tw - 6)}'
            f"</g>"
        )
    return "\n".join(bits)


def crate_pile() -> str:
    """A loading-dock pile, not a 2x3 card grid. Different sizes, stacked, one offset."""
    return "\n".join(
        [
            crate(980, 488, 148, 86, "AWS"),
            crate(1036, 434, 108, 58, "DOCKER"),
            crate(958, 572, 108, 70, "K8S"),
            crate(1074, 560, 92, 66, "BASH"),
            crate(990, 640, 126, 48, "TERRAFORM"),
            crate(1088, 624, 80, 64, "CLOUDFLARE", rot=-3),
        ]
    )


def bench() -> str:
    return f'''<g>
  <rect x="252" y="430" width="470" height="20" fill="{IRON}"/>
  <rect x="252" y="430" width="470" height="4" fill="{BRASS}"/>
  <rect x="252" y="446" width="470" height="8" fill="{WOOD_DK}"/>
  <rect x="272" y="454" width="16" height="154" fill="{IRON}"/>
  <rect x="686" y="454" width="16" height="154" fill="{IRON}"/>
  <rect x="268" y="604" width="24" height="8" fill="{STEEL}"/>
  <rect x="682" y="604" width="24" height="8" fill="{STEEL}"/>
  <rect x="296" y="528" width="382" height="9" fill="{STEEL}"/>
  <rect x="296" y="528" width="382" height="2" fill="{BRASS_DK}"/>
</g>'''


def build_workbench_scene() -> None:
    w, h = 1200, 780

    jars = "\n".join(
        jar(cx, 476, name)
        for cx, name in (
            (348, "POSTGRES"),
            (414, "REDIS"),
            (480, "MONGO"),
            (546, "SQLITE"),
            (612, "PGVECTOR"),
        )
    )

    lantern_x, lantern_y = 392, 300
    lantern = f'''<g>
  <path d="M{lantern_x} 288 V{lantern_y}" stroke="{BRASS_DK}" stroke-width="2"/>
  <ellipse cx="{lantern_x}" cy="{lantern_y + 34}" rx="44" ry="52" fill="url(#lamp)">
    <animate attributeName="opacity" values=".45;1;.45" dur="3.2s" repeatCount="indefinite"/>
  </ellipse>
{rle_rects(LANTERN_CORE, lantern_x - 28, lantern_y, 7)}
</g>'''

    body = f'''  <rect width="{w}" height="{h}" fill="{OBS}"/>
  <rect x="18" y="14" width="1164" height="752" fill="{GRAPHITE}"/>
  <rect x="18" y="14" width="1164" height="752" fill="none" stroke="{BRASS}" stroke-width="2"/>
  <rect x="24" y="20" width="1152" height="740" fill="none" stroke="{BRASS_DK}" stroke-width="1"/>
  <rect x="18" y="14" width="1164" height="5" fill="{BRASS}"/>

  {outline("The workbench", "plate", 600, 56, BONE, "middle")}
  <path d="M430 68 H770" stroke="{BRASS}" stroke-width="1" opacity=".7"/>
  {outline("What is actually on the bench", "eyebrow", 600, 90, MUTE, "middle")}

  {pegboard(40, 100, 1120, 186)}
  {hanging_tools()}

  <rect x="40" y="640" width="1120" height="88" fill="#141519"/>
  <path d="M40 640 H1160" stroke="{STEEL}" stroke-width="1" opacity=".5"/>

  {ingot_rack()}
  {bench()}
  {kettle(318, 384)}
{rle_rects(TEACUP, 372, 400, 4)}
  {letter_stamp(422, 402, "PY")}
  {letter_stamp(454, 402, "TS")}
  {letter_stamp(486, 402, "GO")}
{sitting_dragon(508, 330, 3)}
  {lantern}
  {anvil(640, 332)}
  {job_ticket(754, 348)}
  {hearth_basin()}
  {crate_pile()}
  {jars}
  {rail_stamp(300, 516, "STOCK", 64)}

  {fireflies([(650, 340, "3.1s"), (710, 318, "3.8s"), (800, 574, "2.9s"), (850, 556, "3.4s"), (318, 360, "4.2s")])}

  <path d="M48 688 H1152" stroke="{BRASS_DK}" stroke-width="1" opacity=".55"/>
  {outline("Steel, brass, bone", "label", 48, 716, BRASS, size=10, tracking=0.18)}
  {outline("Muxby", "label", 1152, 716, BRASS, "end", size=10, tracking=0.18)}
  <path d="M48 736 H1152" stroke="{STEEL}" stroke-width="2"/>
  <path d="M48 736 H220" stroke="{PATINA}" stroke-width="2"/>
  <path d="M220 736 H420" stroke="{EMBER}" stroke-width="2"/>
  <path d="M420 736 H700" stroke="{BRASS}" stroke-width="2"/>
  <path d="M48 732 L52 736 L48 740" fill="{BRASS}"/>
  <path d="M220 732 L224 736 L220 740" fill="{PATINA_LT}"/>
  <path d="M420 732 L424 736 L420 740" fill="{EMBER}"/>
  <path d="M700 732 L704 736 L700 740" fill="{GOLD}"/>
  <path d="M1152 732 L1148 736 L1152 740" fill="{BRASS}"/>
'''
    art = svg_wrap(
        w,
        h,
        "The workbench",
        "Languages hang as tools, web as labeled ingots, data in jars, infrastructure in crates, current work on a ticket.",
        body,
    )
    write(OUT / "atelier" / "corkboard.svg", art)
    write(OUT / "constellation.svg", art)


if __name__ == "__main__":
    build_workbench_scene()
