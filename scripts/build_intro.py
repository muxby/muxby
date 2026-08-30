#!/usr/bin/env python3
"""Identity plate for the README intro.

Kept as its own builder so the hero rewrite in scripts/build_atelier.py can
land without a merge fight. One Cool Thing: molten wax drips from the struck
M and a droplet falls onto the brass nameplate. Glow, stretch, drop, and
splash share a single 5.6s SMIL loop.
"""

from __future__ import annotations

import math
from pathlib import Path

import typeset as ts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "atelier"


def _blob_path(
    cx: float,
    cy: float,
    r: float,
    lumps: list[tuple[float, float, float]],
    n: int = 80,
) -> str:
    """Closed polar blob. `lumps` are (angle_rad, amplitude, sigma_rad)."""
    pts: list[tuple[float, float]] = []
    for i in range(n):
        a = -math.pi / 2 + (2 * math.pi * i) / n
        bump = 0.0
        for ang, amp, sig in lumps:
            da = (a - ang + math.pi) % (2 * math.pi) - math.pi
            bump += amp * math.exp(-(da * da) / (2 * sig * sig))
        rr = r + bump
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    bits = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    bits.extend(f"L{x:.1f},{y:.1f}" for x, y in pts[1:])
    bits.append("Z")
    return "".join(bits)


def wax_defs(prefix: str) -> str:
    return f'''    <radialGradient id="{prefix}-wax" cx="46%" cy="32%" r="68%">
      <stop offset="0" stop-color="#E4572E"/>
      <stop offset=".38" stop-color="#C0431F"/>
      <stop offset=".72" stop-color="#A33418"/>
      <stop offset="1" stop-color="#5E1C0C"/>
    </radialGradient>
    <radialGradient id="{prefix}-halo" cx="50%" cy="42%" r="50%">
      <stop offset="0" stop-color="#F2C14E" stop-opacity=".55"/>
      <stop offset=".45" stop-color="#E4572E" stop-opacity=".22"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="{prefix}-brass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8A6E1F"/>
      <stop offset=".5" stop-color="#C9A227"/>
      <stop offset="1" stop-color="#F2C14E"/>
    </linearGradient>'''


def wax_seal_mark(
    cx: float,
    cy: float,
    r: float,
    prefix: str,
    m_size: float,
    land_y: float,
) -> str:
    """Struck M in molten wax. One beat: a drip forms, falls, kisses the plate."""
    lumps = [
        (math.pi / 2, 22.0, 0.30),
        (1.95, 12.0, 0.20),
        (1.18, 10.0, 0.18),
        (math.pi, 4.0, 0.32),
        (0.08, 3.5, 0.28),
        (-math.pi / 2, -2.0, 0.40),
        (2.55, 8.0, 0.22),
    ]
    wax = _blob_path(cx, cy, r, lumps)
    rim = _blob_path(cx, cy, r + 5.5, [(a, amp * 0.35, sig) for a, amp, sig in lumps])
    m_cap = ts.cap_height("wordmark", size=m_size, tracking=0)
    m_y = cy + m_cap / 2 - m_size * 0.04
    dur = "5.6s"
    hang = cy + r + 2
    left_x, right_x = cx - 22, cx + 26
    return f'''<g id="{prefix}-seal">
  <ellipse cx="{cx}" cy="{cy}" rx="{r + 22}" ry="{r + 18}" fill="url(#{prefix}-halo)">
    <animate attributeName="opacity" values=".42;.78;.42" dur="{dur}" repeatCount="indefinite"/>
  </ellipse>
  <circle cx="{cx}" cy="{cy}" r="{r + 16}" fill="#1B1D22"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 16}" fill="none" stroke="#8A6E1F" stroke-width="3"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 12}" fill="none" stroke="#C9A227" stroke-width="1.4"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="#F2C14E" stroke-width="1.1" stroke-dasharray="2.4 6.2" opacity=".9"/>
  <path d="{rim}" fill="#5E1C0C"/>
  <path d="{wax}" fill="url(#{prefix}-wax)"/>
  <circle cx="{cx}" cy="{cy - 8}" r="{r * 0.42}" fill="#F2C14E" opacity=".14">
    <animate attributeName="opacity" values=".10;.28;.10" dur="{dur}" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="{r - 18}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".55"/>
  {ts.outline("M", "wordmark", cx + 1.2, m_y + 1.4, "#5E1C0C", "middle", size=m_size, tracking=0, opacity=".55")}
  {ts.outline("M", "wordmark", cx, m_y, "#F7F5F0", "middle", size=m_size, tracking=0)}
  <path d="M{cx - 3:.1f},{cy + 10:.1f} L{cx:.1f},{cy + 16:.1f} L{cx + 3:.1f},{cy + 10:.1f} Z" fill="#F2C14E" opacity=".85"/>
  <g transform="translate({left_x:.1f} {hang:.1f})">
    <g>
      <animateTransform attributeName="transform" type="scale" values="1 0.72; 1 1.12; 1 0.72" keyTimes="0;0.4;1" dur="{dur}" calcMode="spline" keySplines="0.45 0 0.2 1; 0.4 0 0.2 1" repeatCount="indefinite"/>
      <path d="M0,0 C-5,10 -6,24 0,34 C6,24 5,10 0,0 Z" fill="#A33418"/>
      <path d="M0,4 C-2.4,12 -2.6,22 0,28 C2.6,22 2.4,12 0,4 Z" fill="#E4572E" opacity=".85"/>
    </g>
  </g>
  <g transform="translate({right_x:.1f} {hang - 4:.1f})">
    <g>
      <animateTransform attributeName="transform" type="scale" values="1 0.8; 1 1.18; 1 0.8" keyTimes="0;0.46;1" dur="{dur}" begin="0.35s" calcMode="spline" keySplines="0.45 0 0.2 1; 0.4 0 0.2 1" repeatCount="indefinite"/>
      <path d="M0,0 C-4.5,9 -5.5,20 0,28 C5.5,20 4.5,9 0,0 Z" fill="#A33418"/>
      <path d="M0,3 C-2,10 -2.2,18 0,23 C2.2,18 2,10 0,3 Z" fill="#E4572E" opacity=".8"/>
    </g>
  </g>
  <g transform="translate({cx:.1f} {hang + 4:.1f})">
    <g>
      <animateTransform attributeName="transform" type="scale" values="1 0.7; 1 1.28; 1 0.7" keyTimes="0;0.38;1" dur="{dur}" calcMode="spline" keySplines="0.4 0 0.15 1; 0.45 0 0.2 1" repeatCount="indefinite"/>
      <path d="M0,0 C-7,16 -9,40 0,58 C9,40 7,16 0,0 Z" fill="#A33418"/>
      <path d="M0,7 C-3.4,20 -3.6,38 0,48 C3.6,38 3.4,20 0,7 Z" fill="#E4572E"/>
      <path d="M0,12 C-1.7,22 -1.7,34 0,42 C1.7,34 1.7,22 0,12 Z" fill="#F2C14E" opacity=".55">
        <animate attributeName="opacity" values=".25;.7;.25" dur="{dur}" repeatCount="indefinite"/>
      </path>
    </g>
  </g>
  <g>
    <circle cx="{cx}" cy="{hang + 40}" r="5.4" fill="#E4572E" opacity="0">
      <animate attributeName="cy" values="{hang + 32:.1f};{hang + 32:.1f};{land_y:.1f};{land_y:.1f}" keyTimes="0;0.36;0.56;1" dur="{dur}" calcMode="spline" keySplines="0.4 0 0.2 1; 0.55 0 0.2 1; 0 0 1 1" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.34;0.38;0.54;0.6;1" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="r" values="4.2;5.6;5.2;4.6" keyTimes="0;0.38;0.52;1" dur="{dur}" repeatCount="indefinite"/>
    </circle>
    <ellipse cx="{cx}" cy="{land_y:.1f}" rx="6" ry="2.2" fill="#E4572E" opacity="0">
      <animate attributeName="opacity" values="0;0;.9;0" keyTimes="0;0.54;0.58;0.7" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="rx" values="5;5;20;24" keyTimes="0;0.54;0.62;1" dur="{dur}" repeatCount="indefinite"/>
    </ellipse>
  </g>
</g>'''


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def svg(w: int, h: int, title_id: str, title: str, desc_id: str, desc: str, defs: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{title_id} {desc_id}">
  <title id="{title_id}">{title}</title>
  <desc id="{desc_id}">{desc}</desc>
  <defs>
{defs}
  </defs>
{body}</svg>
'''


def build_wax_seal() -> None:
    w, h = 168, 236
    cx, cy, r = 84, 82, 56
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
{wax_seal_mark(cx, cy, r, "seal", 42, land_y=h - 16)}
'''
    write(
        OUT / "wax-seal.svg",
        svg(
            w,
            h,
            "sealTitle",
            "Molten monogram seal",
            "sealDesc",
            "A struck wax M with a slow molten drip.",
            wax_defs("seal"),
            body,
        ),
    )


def build_intro() -> None:
    w, h = 600, 372
    cx, cy, r = 300, 126, 70
    plate_w, plate_h = 256, 58
    plate_x = (w - plate_w) / 2
    plate_y = 292
    rivets = []
    for rx, ry in (
        (plate_x + 10, plate_y + 10),
        (plate_x + plate_w - 10, plate_y + 10),
        (plate_x + 10, plate_y + plate_h - 10),
        (plate_x + plate_w - 10, plate_y + plate_h - 10),
    ):
        rivets.append(
            f'<circle cx="{rx:.0f}" cy="{ry:.0f}" r="2.4" fill="#C9A227"/>'
            f'<circle cx="{rx:.0f}" cy="{ry:.0f}" r="1.1" fill="#8A6E1F"/>'
        )
    name = ts.outline(
        "Mubeen",
        "plate",
        w / 2,
        plate_y + 30,
        "#E9E6DF",
        "middle",
        size=22,
        tracking=0.18,
    )
    kicker = ts.outline(
        "Pakistan",
        "label",
        w / 2,
        plate_y + 46,
        "#C9A227",
        "middle",
        size=9,
        tracking=0.22,
    )
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="18" y="14" width="{w - 36}" height="{h - 28}" fill="#17181C"/>
  <rect x="18" y="14" width="{w - 36}" height="{h - 28}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <rect x="18" y="14" width="{w - 36}" height="3" fill="#C9A227"/>
{wax_seal_mark(cx, cy, r, "intro", 52, land_y=plate_y)}
  <rect x="{plate_x:.0f}" y="{plate_y:.0f}" width="{plate_w:.0f}" height="{plate_h:.0f}" fill="#2A2D35"/>
  <rect x="{plate_x:.0f}" y="{plate_y:.0f}" width="{plate_w:.0f}" height="{plate_h:.0f}" fill="none" stroke="url(#intro-brass)" stroke-width="2"/>
  <rect x="{plate_x + 5:.0f}" y="{plate_y + 5:.0f}" width="{plate_w - 10:.0f}" height="{plate_h - 10:.0f}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".8"/>
  {"".join(rivets)}
  {name}
  {kicker}
'''
    write(
        OUT / "intro.svg",
        svg(
            w,
            h,
            "introTitle",
            "Mubeen, struck in wax",
            "introDesc",
            "A molten wax M dripping onto a brass nameplate engraved Mubeen, Pakistan.",
            wax_defs("intro"),
            body,
        ),
    )


def main() -> None:
    build_wax_seal()
    build_intro()


if __name__ == "__main__":
    main()
