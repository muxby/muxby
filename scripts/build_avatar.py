#!/usr/bin/env python3
"""Blood-moon ink avatar for the muxby profile.

Organic liquid-ink crescent (not a geometric disc). GitHub README <img> SVGs
play CSS @keyframes; SMIL freezes, so every motion here is CSS. Rebuilds
assets/atelier/avatar-blood-moon.svg and supplies the same moon for the
forge-yard hero.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402

ROOT = A.ROOT
OUT = A.OUT

# Ink, not neon. Crimson is a shade richer than the ember body so the moon
# reads as stirred paint rather than pixel fire.
INK = "#050506"
INK_SOFT = "#0A0A0C"
INK_EDGE = "#14161A"
CRIMSON = "#C41E3A"
CRIMSON_HOT = "#E4572E"
CRIMSON_DEEP = "#8B1414"
FIRE_DEEP = "#A33418"
FIRE_SHADOW = "#7E2A12"
MIX = "#4A1014"
GRAPHITE = "#17181C"
OBSIDIAN = "#0F1013"
IRON = "#2A2D35"

SIZE = 512
CX = 256.0
CY = 236.0


def _fmt(n: float) -> str:
    v = f"{n:.2f}".rstrip("0").rstrip(".")
    return v if v and v != "-0" else "0"


def smooth_closed(pts: list[tuple[float, float]]) -> str:
    """Catmull-Rom through the points, closed, as cubic Beziers."""
    n = len(pts)
    if n < 3:
        return ""
    parts = [f"M{_fmt(pts[0][0])},{_fmt(pts[0][1])}"]
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        parts.append(
            f"C{_fmt(c1x)},{_fmt(c1y)} {_fmt(c2x)},{_fmt(c2y)} {_fmt(p2[0])},{_fmt(p2[1])}"
        )
    parts.append("Z")
    return " ".join(parts)


def blob(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    harmonics: list[tuple[float, float, float]],
    n: int = 72,
    rot: float = 0.0,
) -> str:
    """Irregular oval. harmonics are (k, amplitude, phase)."""
    pts: list[tuple[float, float]] = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1.0
        for k, amp, ph in harmonics:
            r += amp * math.cos(k * t + ph)
        x = rx * r * math.cos(t)
        y = ry * r * math.sin(t)
        ca, sa = math.cos(rot), math.sin(rot)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return smooth_closed(pts)


def circle_intersect(
    ox: float, oy: float, orad: float, ix: float, iy: float, irad: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    dx, dy = ix - ox, iy - oy
    d = math.hypot(dx, dy)
    a = (orad * orad - irad * irad + d * d) / (2 * d)
    h = math.sqrt(max(orad * orad - a * a, 0.0))
    mx, my = ox + a * dx / d, oy + a * dy / d
    px, py = -dy * h / d, dx * h / d
    return (mx + px, my + py), (mx - px, my - py)


def crescent_outline(
    ox: float,
    oy: float,
    orad: float,
    ix: float,
    iy: float,
    irad: float,
    outer_noise: float = 0.045,
    inner_noise: float = 0.07,
    n_outer: int = 96,
    n_inner: int = 80,
) -> str:
    """Two-circle crescent with noisy rims so it is never a clean moon disc.

    Opening faces the inner-circle centre (upper-left in the avatar layout).
    """
    p_a, p_b = circle_intersect(ox, oy, orad, ix, iy, irad)

    def ang(cx: float, cy: float, x: float, y: float) -> float:
        return math.atan2(y - cy, x - cx)

    a0 = ang(ox, oy, p_a[0], p_a[1])
    a1 = ang(ox, oy, p_b[0], p_b[1])
    # Walk the long outer arc (the body), not the short opening.
    span = (a1 - a0) % (2 * math.pi)
    if span < math.pi:
        a0, a1 = a1, a0
        span = (a1 - a0) % (2 * math.pi)

    def nse(t: float, seed: float, amp: float) -> float:
        return amp * (
            0.55 * math.sin(3 * t + seed)
            + 0.28 * math.sin(7 * t - seed * 1.3)
            + 0.17 * math.sin(13 * t + seed * 0.6)
            + 0.08 * math.sin(23 * t - seed)
        )

    outer: list[tuple[float, float]] = []
    for i in range(n_outer + 1):
        t = a0 + span * i / n_outer
        r = orad * (1.0 + nse(t, 0.4, outer_noise))
        # Weight the mass toward the bottom: swell the lower outer rim.
        swell = 0.045 * max(math.sin(t), 0)
        r *= 1.0 + swell
        outer.append((ox + r * math.cos(t), oy + r * math.sin(t)))

    b0 = ang(ix, iy, outer[-1][0], outer[-1][1])
    b1 = ang(ix, iy, outer[0][0], outer[0][1])
    span_ccw = (b1 - b0) % (2 * math.pi)
    span_cw = span_ccw - 2 * math.pi

    def inner_mid_inside(span: float) -> bool:
        t = b0 + span / 2.0
        x = ix + irad * math.cos(t)
        y = iy + irad * math.sin(t)
        return math.hypot(x - ox, y - oy) <= orad * 0.98

    inner_span = span_ccw if inner_mid_inside(span_ccw) else span_cw

    inner: list[tuple[float, float]] = []
    steps = n_inner
    for i in range(1, steps):
        t = b0 + inner_span * i / steps
        r = irad * (1.0 + nse(t, 1.7, inner_noise))
        # Jagged inner lip: extra high-frequency bite.
        r *= 1.0 + 0.035 * math.sin(19 * t + 0.8)
        inner.append((ix + r * math.cos(t), iy + r * math.sin(t)))

    pts = outer + inner
    return smooth_closed(pts)


def teardrop(cx: float, cy: float, w: float, h: float, lean: float = 0.0) -> str:
    """Drip hanging from (cx, cy). Tip at cy+h, width w at the shoulder."""
    tip_x = cx + lean
    tip_y = cy + h
    return (
        f"M{_fmt(cx)},{_fmt(cy)} "
        f"C{_fmt(cx - w)},{_fmt(cy + h * 0.22)} {_fmt(cx - w * 0.55)},{_fmt(cy + h * 0.62)} {_fmt(tip_x)},{_fmt(tip_y)} "
        f"C{_fmt(cx + w * 0.55 + lean)},{_fmt(cy + h * 0.62)} {_fmt(cx + w)},{_fmt(cy + h * 0.22)} {_fmt(cx)},{_fmt(cy)} Z"
    )


def spike(cx: float, cy: float, w: float, h: float) -> str:
    """Very thin central needle."""
    return (
        f"M{_fmt(cx - w)},{_fmt(cy)} "
        f"C{_fmt(cx - w * 0.4)},{_fmt(cy + h * 0.45)} {_fmt(cx - w * 0.15)},{_fmt(cy + h * 0.82)} {_fmt(cx)},{_fmt(cy + h)} "
        f"C{_fmt(cx + w * 0.15)},{_fmt(cy + h * 0.82)} {_fmt(cx + w * 0.4)},{_fmt(cy + h * 0.45)} {_fmt(cx + w)},{_fmt(cy)} Z"
    )


def taper_arc(
    x1: float, y1: float, cx: float, cy: float, x2: float, y2: float, w1: float, w2: float
) -> str:
    """Filled tapering quadratic stroke (start width w1, end width w2)."""
    # Approximate a normal to the chord for offset.
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    # Control-point offset.
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    cdx, cdy = cx - mx, cy - my
    return (
        f"M{_fmt(x1 + nx * w1)},{_fmt(y1 + ny * w1)} "
        f"Q{_fmt(cx + nx * (w1 + w2) / 2 + cdx * 0.02)},{_fmt(cy + ny * (w1 + w2) / 2 + cdy * 0.02)} "
        f"{_fmt(x2 + nx * w2)},{_fmt(y2 + ny * w2)} "
        f"L{_fmt(x2 - nx * w2)},{_fmt(y2 - ny * w2)} "
        f"Q{_fmt(cx - nx * (w1 + w2) / 2)},{_fmt(cy - ny * (w1 + w2) / 2)} "
        f"{_fmt(x1 - nx * w1)},{_fmt(y1 - ny * w1)} Z"
    )


def ribbon(
    cx: float,
    cy: float,
    length: float,
    width: float,
    waves: int,
    amp: float,
    rot: float,
    phase: float = 0.0,
) -> str:
    """Stirred-paint ribbon: a thick sine band, for the marble clip."""
    n = 40
    top: list[tuple[float, float]] = []
    bot: list[tuple[float, float]] = []
    ca, sa = math.cos(rot), math.sin(rot)
    for i in range(n):
        t = i / (n - 1)
        x = (t - 0.5) * length
        y = amp * math.sin(waves * math.pi * t + phase)
        # Taper the ends.
        w = width * math.sin(math.pi * t) ** 0.7
        px, py = cx + x * ca - y * sa, cy + x * sa + y * ca
        nx, ny = -sa, ca
        top.append((px + nx * w, py + ny * w))
        bot.append((px - nx * w, py - ny * w))
    pts = top + bot[::-1]
    return smooth_closed(pts)


# --- geometry for this piece -------------------------------------------------
# Outer disc sits a little above centre so the long drip has room inside the
# circular crop. Inner disc is shifted toward 10:30, opening the crescent
# upper-left.

OUTER = (286.0, 242.0, 168.0)
INNER = (196.0, 190.0, 120.0)


def main_crescent() -> str:
    return crescent_outline(*OUTER, *INNER, outer_noise=0.05, inner_noise=0.085)


def css_block() -> str:
    """Overlapping 8–12s loops so the frame never rests."""
    return """
.bm-swirl{transform-box:fill-box;transform-origin:50% 50%;animation:bm-swirl 11s ease-in-out infinite}
.bm-swirl-b{transform-box:fill-box;transform-origin:50% 50%;animation:bm-swirl-b 9.4s ease-in-out infinite}
.bm-pulse{transform-box:fill-box;transform-origin:50% 50%;animation:bm-pulse 10s ease-in-out infinite}
.bm-pulse-ink{transform-box:fill-box;transform-origin:50% 62%;animation:bm-pulse-ink 12s ease-in-out infinite}
.bm-drip{transform-box:fill-box;transform-origin:50% 0%;animation:bm-drip 9s ease-in-out infinite}
.bm-drip-b{transform-box:fill-box;transform-origin:50% 0%;animation:bm-drip 10.6s ease-in-out infinite;animation-delay:-3.2s}
.bm-drip-c{transform-box:fill-box;transform-origin:50% 0%;animation:bm-drip 8.4s ease-in-out infinite;animation-delay:-6.1s}
.bm-drip-long{transform-box:fill-box;transform-origin:50% 0%;animation:bm-drip-long 11.2s ease-in-out infinite}
.bm-fall{transform-box:fill-box;transform-origin:50% 0%;animation:bm-fall 8s cubic-bezier(.2,.7,.2,1) infinite}
.bm-fall-b{transform-box:fill-box;transform-origin:50% 0%;animation:bm-fall 9.6s cubic-bezier(.2,.7,.2,1) infinite;animation-delay:-2.8s}
.bm-fall-c{transform-box:fill-box;transform-origin:50% 0%;animation:bm-fall 7.4s cubic-bezier(.2,.7,.2,1) infinite;animation-delay:-5.1s}
.bm-arc{transform-box:fill-box;transform-origin:0% 100%;animation:bm-arc 10.5s ease-in-out infinite}
.bm-arc-b{transform-box:fill-box;transform-origin:80% 100%;animation:bm-arc 12s ease-in-out infinite;animation-delay:-4s}
.bm-speck{animation:bm-speck 8.8s ease-in-out infinite}
.bm-speck-b{animation:bm-speck 11.2s ease-in-out infinite;animation-delay:-3.4s}
@keyframes bm-swirl{0%{transform:rotate(0deg)}50%{transform:rotate(18deg)}100%{transform:rotate(0deg)}}
@keyframes bm-swirl-b{0%{transform:rotate(6deg)}50%{transform:rotate(-14deg)}100%{transform:rotate(6deg)}}
@keyframes bm-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.035)}}
@keyframes bm-pulse-ink{0%,100%{transform:scale(1)}50%{transform:scale(1.02)}}
@keyframes bm-drip{0%,100%{transform:translateY(0) scaleY(1)}38%{transform:translateY(7px) scaleY(1.14)}62%{transform:translateY(2px) scaleY(1.04)}}
@keyframes bm-drip-long{0%,100%{transform:translateY(0) scaleY(1)}42%{transform:translateY(11px) scaleY(1.1)}70%{transform:translateY(4px) scaleY(1.03)}}
@keyframes bm-fall{0%{transform:translateY(-2px);opacity:0}10%{opacity:1}72%{opacity:.85}100%{transform:translateY(46px);opacity:0}}
@keyframes bm-arc{0%,100%{transform:rotate(0deg) translate(0,0)}50%{transform:rotate(-7deg) translate(3px,-5px)}}
@keyframes bm-speck{0%,100%{transform:translate(0,0);opacity:.8}50%{transform:translate(5px,-9px);opacity:1}}
""".strip()


def _path(d: str, fill: str, cls: str = "", extra: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<path d="{d}" fill="{fill}"{c}{extra}/>'


def _circ(cx: float, cy: float, r: float, fill: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" fill="{fill}"{c}/>'


def moon_layers() -> str:
    """Layered ink: black mass, crimson, marble, drips, arcs, droplets."""
    body = main_crescent()

    # Extra organic lobes on the OUTER rim only — never in the opening.
    lobes = [
        blob(368, 158, 38, 26, [(2, 0.18, 0.4), (5, 0.08, 1.1), (9, 0.05, 0.2)], rot=-0.5),
        blob(392, 228, 34, 46, [(3, 0.16, 0.2), (6, 0.07, 2.0)], rot=0.3),
        blob(286, 392, 68, 30, [(2, 0.2, 1.2), (4, 0.1, 0.6), (8, 0.05, 2.4)]),
        blob(218, 348, 42, 34, [(3, 0.18, 0.8), (7, 0.07, 1.6)], rot=0.4),
        blob(344, 360, 42, 26, [(2, 0.14, 0.3), (5, 0.08, 2.1)]),
        blob(410, 286, 24, 32, [(2, 0.16, 0.9), (5, 0.08, 0.4)], rot=0.15),
        blob(320, 118, 28, 18, [(3, 0.14, 0.6), (6, 0.07, 1.8)], rot=-0.3),
    ]
    inner_bites = [
        blob(248, 188, 11, 8, [(3, 0.22, 0.5), (7, 0.1, 1.2)]),
        blob(228, 236, 10, 13, [(2, 0.2, 1.0), (6, 0.1, 0.4)]),
        blob(276, 152, 9, 8, [(4, 0.18, 0.7)]),
        blob(300, 138, 7, 9, [(3, 0.2, 2.0)]),
        blob(210, 286, 8, 11, [(5, 0.16, 0.9)]),
        blob(238, 160, 8, 7, [(3, 0.18, 0.4)]),
    ]

    crimson_core = blob(
        348,
        188,
        82,
        72,
        [(2, 0.12, 0.3), (3, 0.08, 1.4), (5, 0.05, 0.6), (9, 0.03, 2.1)],
        n=80,
        rot=-0.35,
    )
    crimson_hot = blob(
        372,
        158,
        50,
        38,
        [(2, 0.14, 0.8), (4, 0.07, 0.2), (8, 0.04, 1.7)],
        rot=-0.2,
    )
    crimson_tongue = blob(
        318,
        262,
        50,
        34,
        [(3, 0.16, 0.4), (6, 0.08, 1.9)],
        rot=0.5,
    )

    ink_base = blob(
        278,
        348,
        90,
        60,
        [(2, 0.14, 1.1), (3, 0.09, 0.4), (5, 0.05, 2.2), (8, 0.03, 0.7)],
        n=80,
    )
    ink_left = blob(
        222,
        318,
        54,
        60,
        [(2, 0.16, 0.6), (4, 0.08, 1.5), (7, 0.04, 0.3)],
        rot=0.25,
    )
    mix_tongue = blob(
        304,
        286,
        44,
        26,
        [(3, 0.2, 0.2), (6, 0.1, 1.4)],
        rot=-0.4,
    )
    mix_black = blob(
        330,
        252,
        34,
        22,
        [(2, 0.18, 1.2), (5, 0.1, 0.5)],
        rot=0.7,
    )

    swirls_a = [
        ribbon(348, 176, 120, 7.5, 2, 16, -0.55, 0.2),
        ribbon(328, 200, 90, 5.5, 3, 11, 0.8, 1.1),
        ribbon(368, 152, 70, 4.5, 2, 9, -1.1, 0.4),
        blob(356, 184, 18, 11, [(2, 0.3, 0.4), (5, 0.12, 1.6)], rot=0.6),
        blob(320, 164, 14, 9, [(3, 0.25, 0.8)], rot=-0.4),
    ]
    swirls_b = [
        ribbon(340, 194, 100, 6, 2, 13, 0.4, 2.2),
        ribbon(372, 178, 64, 4, 3, 8, -0.9, 0.7),
        blob(334, 210, 16, 10, [(2, 0.22, 1.3), (6, 0.1, 0.2)]),
        blob(380, 198, 12, 8, [(3, 0.2, 0.6)], rot=0.9),
    ]

    # Drips hang from the pooled bottom. One very long thin central spike.
    drip_root_y = 392.0
    drips = [
        ("bm-drip", teardrop(232, drip_root_y, 7.5, 42, lean=-2), INK),
        ("bm-drip-b", teardrop(258, drip_root_y + 4, 9, 54, lean=1), INK),
        ("bm-drip-c", teardrop(286, drip_root_y + 2, 11, 38, lean=0), CRIMSON_DEEP),
        ("bm-drip", teardrop(312, drip_root_y + 6, 8, 48, lean=2), INK),
        ("bm-drip-b", teardrop(338, drip_root_y + 4, 10, 36, lean=-1), MIX),
        ("bm-drip-c", teardrop(210, drip_root_y + 8, 6.5, 28, lean=-3), INK),
        ("bm-drip", teardrop(362, drip_root_y + 10, 7, 24, lean=2), FIRE_SHADOW),
        ("bm-drip-long", spike(286, drip_root_y + 6, 3.4, 104), INK),
    ]
    # Veined crimson on a couple of drips, sitting on top of the black.
    drip_veins = [
        ("bm-drip-c", teardrop(286, drip_root_y + 4, 4.2, 26, lean=0.4), CRIMSON),
        ("bm-drip-b", teardrop(338, drip_root_y + 6, 3.6, 20, lean=-0.6), CRIMSON_DEEP),
    ]

    detached = [
        ("bm-fall", 286, 504, 3.2, INK),
        ("bm-fall-b", 286, 492, 2.2, INK),
        ("bm-fall-c", 258, 454, 3.6, INK),
        ("bm-fall", 312, 450, 2.8, INK),
        ("bm-fall-b", 232, 440, 2.4, INK),
        ("bm-fall-c", 338, 434, 2.6, CRIMSON_DEEP),
        ("bm-fall", 210, 428, 2.0, INK),
        ("bm-fall-b", 286, 438, 2.2, CRIMSON),
    ]

    # Thin elegant arcs flying off the upper-right rim, plus specks.
    arcs = [
        ("bm-arc", taper_arc(352, 96, 378, 78, 404, 92, 1.7, 0.35), CRIMSON),
        ("bm-arc-b", taper_arc(368, 118, 402, 108, 428, 128, 1.4, 0.3), CRIMSON_HOT),
        ("bm-arc", taper_arc(340, 84, 356, 62, 372, 78, 1.2, 0.25), CRIMSON_DEEP),
        ("bm-arc-b", taper_arc(388, 140, 416, 148, 432, 170, 1.1, 0.25), INK),
        ("bm-arc", taper_arc(324, 108, 338, 92, 348, 104, 1.0, 0.2), INK),
        ("bm-arc-b", taper_arc(360, 88, 390, 70, 410, 86, 0.9, 0.2), CRIMSON),
    ]
    specks = [
        ("bm-speck", 396, 86, 2.6, CRIMSON),
        ("bm-speck-b", 418, 104, 2.0, CRIMSON_HOT),
        ("bm-speck", 408, 72, 1.6, CRIMSON_DEEP),
        ("bm-speck-b", 436, 118, 1.8, INK),
        ("bm-speck", 372, 70, 1.5, INK),
        ("bm-speck-b", 390, 128, 1.7, CRIMSON),
        ("bm-speck", 348, 64, 1.4, CRIMSON),
        ("bm-speck-b", 424, 156, 1.5, INK),
        ("bm-speck", 312, 78, 1.3, INK),
        ("bm-speck-b", 404, 178, 1.4, CRIMSON_DEEP),
        # Inner-opening specks
        ("bm-speck", 176, 168, 1.8, INK),
        ("bm-speck-b", 164, 210, 1.5, CRIMSON_DEEP),
        ("bm-speck", 192, 148, 1.4, CRIMSON),
        ("bm-speck-b", 158, 248, 1.6, INK),
        ("bm-speck", 210, 132, 1.3, INK),
        ("bm-speck-b", 148, 188, 1.2, CRIMSON),
    ]

    # Hair-thin inner-edge splatter lines.
    hairs = [
        taper_arc(236, 176, 228, 168, 222, 178, 0.7, 0.15),
        taper_arc(208, 220, 198, 212, 194, 226, 0.65, 0.15),
        taper_arc(252, 158, 246, 148, 240, 158, 0.6, 0.12),
        taper_arc(186, 258, 176, 252, 174, 266, 0.7, 0.14),
    ]

    parts: list[str] = []
    # Body clip keeps extra blobs from flooding the upper-left opening.
    parts.append("  <defs>")
    parts.append('    <clipPath id="bmBody" clipPathUnits="userSpaceOnUse">')
    parts.append(f"      {_path(body, INK)}")
    for d in lobes:
        parts.append(f"      {_path(d, INK)}")
    parts.append("    </clipPath>")
    parts.append('    <clipPath id="bmCrimson" clipPathUnits="userSpaceOnUse">')
    parts.append(f"      {_path(crimson_core, CRIMSON)}")
    parts.append(f"      {_path(crimson_hot, CRIMSON)}")
    parts.append(f"      {_path(lobes[0], CRIMSON)}")
    parts.append(f"      {_path(lobes[1], CRIMSON)}")
    parts.append("    </clipPath>")
    parts.append("  </defs>")

    parts.append('  <g clip-path="url(#bmBody)">')
    parts.append("  <!-- black mass: lower-left and base -->")
    parts.append('  <g class="bm-pulse-ink">')
    parts.append(f"    {_path(body, INK)}")
    for d in lobes:
        parts.append(f"    {_path(d, INK)}")
    parts.append(f"    {_path(ink_base, INK)}")
    parts.append(f"    {_path(ink_left, INK)}")
    parts.append("  </g>")

    parts.append("  <!-- crimson mass: upper-right, slow pulse -->")
    parts.append('  <g class="bm-pulse">')
    parts.append(f"    {_path(crimson_core, CRIMSON)}")
    parts.append(f"    {_path(crimson_hot, CRIMSON_HOT)}")
    parts.append(f"    {_path(crimson_tongue, CRIMSON_DEEP)}")
    parts.append(f"    {_path(lobes[0], CRIMSON)}")
    parts.append(f"    {_path(lobes[1], FIRE_DEEP)}")
    parts.append("  </g>")

    parts.append('  <g clip-path="url(#bmCrimson)">')
    parts.append('    <g class="bm-swirl">')
    for i, d in enumerate(swirls_a):
        fill = INK if i % 2 == 0 else FIRE_SHADOW
        parts.append(f"      {_path(d, fill)}")
    parts.append("    </g>")
    parts.append('    <g class="bm-swirl-b">')
    for i, d in enumerate(swirls_b):
        fill = INK_SOFT if i % 2 == 0 else MIX
        parts.append(f"      {_path(d, fill)}")
    parts.append("    </g>")
    parts.append("  </g>")

    parts.append("  <!-- red/black mixing at the boundary -->")
    parts.append(f"  {_path(mix_tongue, CRIMSON_DEEP)}")
    parts.append(f"  {_path(mix_black, INK)}")
    parts.append(
        f"  {_path(blob(280, 308, 26, 14, [(3, 0.22, 0.5), (6, 0.1, 1.8)], rot=-0.6), CRIMSON)}"
    )
    parts.append(
        f"  {_path(blob(300, 280, 20, 12, [(2, 0.2, 1.1), (5, 0.1, 0.3)], rot=0.4), INK)}"
    )
    parts.append(
        f"  {_path(blob(258, 298, 16, 11, [(4, 0.18, 0.7)], rot=0.8), FIRE_DEEP)}"
    )
    parts.append("  </g>")

    parts.append("  <!-- inner-edge spatters (sit on the lip, not in the hole) -->")
    for d in inner_bites:
        parts.append(f"  {_path(d, INK)}")
    parts.append(f"  {_path(blob(268, 172, 7, 6, [(3, 0.2, 0.4)]), CRIMSON_DEEP)}")
    parts.append(f"  {_path(blob(232, 220, 6, 8, [(2, 0.22, 1.2)]), CRIMSON)}")
    for d in hairs:
        parts.append(f"  {_path(d, INK)}")

    parts.append("  <!-- drips -->")
    for cls, d, fill in drips:
        parts.append(f"  {_path(d, fill, cls)}")
    for cls, d, fill in drip_veins:
        parts.append(f"  {_path(d, fill, cls)}")

    parts.append("  <!-- detached falling droplets -->")
    for cls, x, y, r, fill in detached:
        parts.append(f"  {_circ(x, y, r, fill, cls)}")

    parts.append("  <!-- upper-right arcs and flying specks -->")
    for cls, d, fill in arcs:
        parts.append(f"  {_path(d, fill, cls)}")
    for cls, x, y, r, fill in specks:
        parts.append(f"  {_circ(x, y, r, fill, cls)}")

    # A few more outer-rim beads so the lip is never smooth.
    beads = [
        (352, 142, 5.5, CRIMSON),
        (366, 188, 4.2, INK),
        (374, 248, 5.0, FIRE_DEEP),
        (348, 112, 3.6, CRIMSON_HOT),
        (184, 304, 4.8, INK),
        (170, 268, 3.4, INK),
        (330, 348, 6.0, INK),
        (300, 358, 4.4, MIX),
    ]
    for x, y, r, fill in beads:
        parts.append(f"  {_circ(x, y, r, fill)}")

    return "\n".join(parts)


def moon_fragment() -> tuple[str, str]:
    """CSS + markup in the 512-space, for the avatar and the hero embed."""
    return css_block(), moon_layers()


def avatar_svg() -> str:
    css, layers = moon_fragment()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" role="img" aria-labelledby="title desc" shape-rendering="geometricPrecision">
  <title id="title">Muxby blood-moon avatar</title>
  <desc id="desc">A thick liquid-ink crescent of deep black and vibrant crimson, opening toward the upper left, with marbled swirls, flying droplets, and dripping spikes. Animated with CSS.</desc>
  <defs>
    <style>
{css}
    </style>
    <clipPath id="bmCrop">
      <circle cx="{CX}" cy="{CX}" r="{CX}"/>
    </clipPath>
    <radialGradient id="bmDisc" cx="46%" cy="42%" r="62%">
      <stop offset="0" stop-color="{GRAPHITE}"/>
      <stop offset=".72" stop-color="{OBSIDIAN}"/>
      <stop offset="1" stop-color="#0B0C0E"/>
    </radialGradient>
  </defs>
  <g clip-path="url(#bmCrop)">
    <circle cx="{CX}" cy="{CX}" r="{CX}" fill="url(#bmDisc)"/>
    <circle cx="{CX}" cy="{CX}" r="248" fill="none" stroke="{IRON}" stroke-width="1.2" opacity=".55"/>
{layers}
  </g>
</svg>
'''


def hero_moon(cx: float, cy: float, scale: float, sink: float = 18) -> str:
    """Same ink moon, nested so CSS origins stay in the moon's own viewBox.

    Pixel dragon stays crispEdges on the parent; this nested svg is geometric
    (fluid ink, not a pixel grid).
    """
    css, layers = moon_fragment()
    side = SIZE * scale
    x = cx - side / 2
    y = cy - side / 2 + sink * scale
    return f'''<svg x="{_fmt(x)}" y="{_fmt(y)}" width="{_fmt(side)}" height="{_fmt(side)}" viewBox="0 0 {SIZE} {SIZE}" overflow="visible" shape-rendering="geometricPrecision">
  <defs>
    <style>
{css}
    </style>
  </defs>
{layers}
</svg>'''


def build() -> None:
    art = avatar_svg()
    A.write(OUT / "atelier" / "avatar-blood-moon.svg", art)


if __name__ == "__main__":
    build()
