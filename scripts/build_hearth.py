#!/usr/bin/env python3
"""Desk night scene and the three hearth cards.

GitHub <img> SVGs freeze SMIL and cannot load webfonts. These four plates use
CSS for lamp, steam, and coals, and outlined chapter type so the letterforms
match the forge map.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402
import typeset as ts  # noqa: E402


def chapter_title(cx: float, y: float, lead: str, rest: str, fill: str = "#E9E6DF", rest_size: float = 18) -> str:
    lead_w = ts.measure(lead + " ", "standfirst", size=13)
    rest_w = ts.measure(rest, "heading", size=rest_size, face="serif-bold", tracking=0.02, caps=False)
    x0 = cx - (lead_w + rest_w) / 2
    return (
        ts.outline(lead, "standfirst", x0, y, fill, size=13)
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


def ornament(cx: float, y: float, half: float = 48) -> str:
    return f'''<g opacity=".8">
  <path d="M{cx - half} {y} H{cx - 8}" stroke="#C9A227" stroke-width="1"/>
  <path d="M{cx + 8} {y} H{cx + half}" stroke="#C9A227" stroke-width="1"/>
  <path d="M{cx} {y - 4} L{cx + 4} {y} L{cx} {y + 4} L{cx - 4} {y} Z" fill="#C9A227"/>
</g>'''


def _rivets(x: float, y: float, w: float, h: float, fill: str = "#8A6E1F") -> str:
    bits = []
    for px, py in ((x + 6, y + 6), (x + w - 6, y + 6), (x + 6, y + h - 6), (x + w - 6, y + h - 6)):
        bits.append(f'<circle cx="{px}" cy="{py}" r="1.5" fill="{fill}"/>')
    return "\n".join(bits)


def css_sparks(prefix: str, pts: list[tuple[float, float]]) -> tuple[str, str]:
    rules, groups = [], []
    for i, (x, y) in enumerate(pts):
        cls = f"{prefix}-{i}"
        name = f"{prefix.replace('-', '_')}_{i}"
        dur = 2.4 + (i % 4) * 0.28
        delay = i * 0.32
        rules.append(
            f".{cls}{{opacity:.25;animation:{name} {dur:.2f}s ease-in-out infinite;animation-delay:{delay:.2f}s}}"
            f"@keyframes {name}{{0%,100%{{opacity:.2;transform:translate(0,0)}}"
            f"50%{{opacity:1;transform:translate(0,-9px)}}}}"
        )
        groups.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="1.7" fill="#F2C14E"/>')
    return "\n".join(rules), "\n".join(groups)


def css_steam(origin: tuple[float, float], count: int = 4) -> tuple[str, str]:
    ox, oy = origin
    rules, groups = [], []
    for i in range(count):
        cls = f"hob-steam-{i}"
        name = f"hobSteam{i}"
        delay = i * 0.45
        dx, dy = 4 + i * 5, -42 - i * 6
        rules.append(
            f".{cls}{{opacity:.2;animation:{name} 3.1s linear infinite;animation-delay:{delay:.2f}s}}"
            f"@keyframes {name}{{0%{{opacity:.15;transform:translate(0,0)}}"
            f"22%{{opacity:.55;transform:translate({dx * 0.3:.0f}px,{-abs(dy) * 0.28:.0f}px)}}"
            f"100%{{opacity:0;transform:translate({dx}px,{dy}px)}}}}"
        )
        groups.append(
            f'<ellipse class="{cls}" cx="{ox + i * 7}" cy="{oy}" rx="{6 + i}" ry="{9 + i}" fill="#8A9098"/>'
        )
    return "\n".join(rules), "\n".join(groups)


def plate_frame(w: int, h: int) -> str:
    return (
        f'<rect width="{w}" height="{h}" fill="#17181C"/>'
        f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".55"/>'
    )


def bankers_lamp(x: float, y: float) -> str:
    """Brass desk lamp. Shade is gold, stem is iron, glow is CSS."""
    return f'''<g class="desk-lamp">
  <ellipse class="desk-glow" cx="{x + 36}" cy="{y - 8}" rx="78" ry="70" fill="url(#lampGlow)"/>
  <rect x="{x + 28}" y="{y + 78}" width="16" height="8" fill="#2A2D35"/>
  <rect x="{x + 22}" y="{y + 84}" width="28" height="6" fill="#8A6E1F"/>
  <path d="M{x + 36} {y + 78} C{x + 36} {y + 48} {x + 18} {y + 36} {x + 18} {y + 18}" fill="none" stroke="#8A6E1F" stroke-width="4"/>
  <path d="M{x - 8} {y + 14} L{x + 62} {y + 8} L{x + 58} {y + 28} L{x - 4} {y + 32} Z" fill="#C9A227"/>
  <path d="M{x - 2} {y + 16} L{x + 54} {y + 11} L{x + 51} {y + 24} L{x + 1} {y + 28} Z" fill="#1B1D22"/>
  <ellipse class="desk-bulb" cx="{x + 26}" cy="{y + 22}" rx="16" ry="7" fill="#F2C14E"/>
</g>'''


def notebook(x: float, y: float) -> str:
    return f'''<g>
  <rect x="{x}" y="{y}" width="132" height="52" fill="#2A2D35"/>
  <rect x="{x}" y="{y}" width="132" height="5" fill="#C9A227"/>
  <rect x="{x + 10}" y="{y + 16}" width="78" height="3" fill="#4E535D"/>
  <rect x="{x + 10}" y="{y + 26}" width="96" height="3" fill="#4E535D"/>
  <rect x="{x + 10}" y="{y + 36}" width="62" height="3" fill="#4E535D"/>
  <rect x="{x + 108}" y="{y + 14}" width="14" height="22" fill="#1B1D22"/>
  <path d="M{x + 122} {y + 18} L{x + 148} {y + 6}" stroke="#8A6E1F" stroke-width="2"/>
  <rect x="{x + 146}" y="{y}" width="5" height="16" fill="#C9A227"/>
</g>'''


def build_desk() -> None:
    w, h = 640, 360
    spark_css, sparks = css_sparks("desk-spark", [(318, 92), (360, 78), (392, 108), (430, 86)])
    css = f"""
.desk-glow{{animation:deskGlow 3.4s ease-in-out infinite}}
@keyframes deskGlow{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.desk-bulb{{animation:deskBulb 2.8s ease-in-out infinite}}
@keyframes deskBulb{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.desk-polaroid{{transform-origin:150px 170px;animation:deskTilt 7s ease-in-out infinite}}
@keyframes deskTilt{{0%,100%{{transform:rotate(-3.2deg)}}50%{{transform:rotate(-2.2deg)}}}}
.desk-moon{{animation:deskMoon 8s ease-in-out infinite}}
@keyframes deskMoon{{0%,100%{{opacity:.88}}50%{{opacity:1}}}}
{spark_css}
"""
    extra_defs = '''
    <radialGradient id="lampGlow" cx="50%" cy="40%" r="60%">
      <stop offset="0" stop-color="#F2C14E" stop-opacity=".55"/>
      <stop offset=".5" stop-color="#E4572E" stop-opacity=".16"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="moonHalo" cx="50%" cy="45%" r="50%">
      <stop offset="0" stop-color="#E4572E" stop-opacity=".4"/>
      <stop offset=".6" stop-color="#A33418" stop-opacity=".12"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
'''
    px, py, pw, ph = 42, 36, 228, 268
    photo = f'''<g class="desk-polaroid">
  <rect x="{px + 6}" y="{py + 8}" width="{pw}" height="{ph}" fill="#1B1D22" opacity=".55"/>
  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#E9E6DF"/>
  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="#8A6E1F" stroke-width="1.6"/>
  {_rivets(px, py, pw, ph, "#C9A227")}
  <rect x="{px + 16}" y="{py + 16}" width="{pw - 32}" height="176" fill="#141519"/>
  <rect x="{px + 16}" y="{py + 16}" width="{pw - 32}" height="176" fill="none" stroke="#2A2D35" stroke-width="1"/>
{A.rle_rects(A.DRAGON_SIT, px + 28, py + 28, 2.6)}
  {ts.outline("First useful spark", "heading", px + pw / 2, py + 224, "#1B1D22", "middle", size=13, face="display", tracking=-0.01, caps=False, max_width=pw - 24)}
  {ts.outline("the night it compiled", "standfirst", px + pw / 2, py + 246, "#5A564E", "middle", size=11)}
</g>'''

    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="392" y="28" width="212" height="168" fill="#12141A"/>
  <rect x="392" y="28" width="212" height="168" fill="none" stroke="#8A6E1F" stroke-width="1.4"/>
  <rect x="400" y="36" width="196" height="152" fill="#0C0E12"/>
  <g class="desk-moon">{A.blood_moon(528, 92, 28)}</g>
  <path d="M400 168 C 448 148, 500 158, 596 150 L596 188 L400 188 Z" fill="#1A2220"/>
  <circle cx="430" cy="58" r="1.1" fill="#E9E6DF" opacity=".4"/>
  <circle cx="560" cy="50" r="0.9" fill="#E9E6DF" opacity=".3"/>
  <rect x="0" y="228" width="{w}" height="132" fill="#1E2026"/>
  <rect x="0" y="228" width="{w}" height="7" fill="#8A6E1F"/>
  <path d="M0 234 H640" stroke="#C9A227" stroke-width="1" opacity=".45"/>
{photo}
{bankers_lamp(318, 118)}
{notebook(430, 176)}
{sparks}
  {A.rle_rects(A.TEACUP, 574, 196, 5)}
  {chapter_title(430, 318, "The desk,", "not the cockpit", "#C9A227", rest_size=16)}
'''
    art = A.svg_wrap(
        w,
        h,
        "The desk, not the cockpit",
        "A night desk: a bone polaroid of a sitting dragon, a brass lamp, an open notebook, and a window with a blood moon.",
        body,
        extra_defs=extra_defs,
        extra_css=css,
    )
    A.write(A.OUT / "atelier" / "desk-night.svg", art)
    A.write(A.OUT / "atelier" / "desk.svg", art)


def build_kettle() -> None:
    w, h = 420, 300
    steam_css, steam = css_steam((208, 108), 4)
    spark_css, sparks = css_sparks("hob-spark", [(168, 196), (252, 188), (210, 176)])
    css = f"""
.hob-glow{{animation:hobGlow 2.8s ease-in-out infinite}}
@keyframes hobGlow{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
.hob-lid{{transform-box:fill-box;transform-origin:center;animation:hobLid 1.5s ease-in-out infinite}}
@keyframes hobLid{{0%,100%{{transform:rotate(0deg)}}35%{{transform:rotate(-8deg)}}70%{{transform:rotate(6deg)}}}}
{steam_css}
{spark_css}
"""
    body = f'''  {plate_frame(w, h)}
  {chapter_title(210, 42, "On the", "hob", rest_size=20)}
  {ornament(210, 56, 54)}
  <ellipse class="hob-glow" cx="210" cy="218" rx="86" ry="22" fill="url(#hearth)"/>
  <ellipse cx="210" cy="224" rx="70" ry="11" fill="#0F1013"/>
  <ellipse cx="210" cy="222" rx="54" ry="6" fill="#E4572E" opacity=".45"/>
  <path d="M152 158 L108 140 L100 156 L146 182 Z" fill="#2A2D35" stroke="#3A3E48" stroke-width="2"/>
  <path d="M148 156 C150 114 270 114 272 156 L264 208 C262 232 158 232 156 208 Z" fill="#2A2D35" stroke="#3A3E48" stroke-width="2"/>
  <path d="M162 180 H258" stroke="#C9A227" stroke-width="3.2"/>
  <path d="M272 160 C322 158 324 202 268 204" fill="none" stroke="#C9A227" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="210" cy="132" rx="48" ry="9" fill="#3A3E48"/>
  <rect class="hob-lid" x="196" y="104" width="28" height="18" fill="#C9A227"/>
  <rect x="204" y="98" width="12" height="8" fill="#8A6E1F"/>
{steam}
{sparks}
  {A.rle_rects(A.TEACUP, 318, 206, 5)}
  {ts.outline("Agentic systems, poured slowly.", "standfirst", 210, 270, "#9AA0AC", "middle", size=12)}
'''
    A.write(
        A.OUT / "atelier" / "kettle-hob.svg",
        A.svg_wrap(
            w,
            h,
            "On the hob",
            "An iron kettle with a brass band, steaming over a hob, a teacup waiting beside it.",
            body,
            extra_css=css,
        ),
    )
    A.write(A.OUT / "atelier" / "kettle.svg", (A.OUT / "atelier" / "kettle-hob.svg").read_text(encoding="utf-8"))


def hanging_lantern(cx: float, cy: float) -> str:
    return f'''<g>
  <path d="M{cx} 36 V{cy - 48}" stroke="#8A6E1F" stroke-width="2"/>
  <path d="M{cx - 10} {cy - 48} H{cx + 10}" stroke="#C9A227" stroke-width="3"/>
  <ellipse class="keep-halo" cx="{cx}" cy="{cy}" rx="58" ry="70" fill="url(#lamp)"/>
  <rect x="{cx - 22}" y="{cy - 46}" width="44" height="8" fill="#C9A227"/>
  <path d="M{cx - 24} {cy - 38} L{cx + 24} {cy - 38} L{cx + 20} {cy + 28} L{cx - 20} {cy + 28} Z" fill="#2A2D35"/>
  <path d="M{cx - 18} {cy - 32} L{cx + 18} {cy - 32} L{cx + 16} {cy + 22} L{cx - 16} {cy + 22} Z" fill="#141519"/>
  <rect class="keep-flame" x="{cx - 10}" y="{cy - 18}" width="20" height="32" fill="#F2C14E"/>
  <path d="M{cx} {cy - 32} V{cy + 22} M{cx - 18} {cy - 6} H{cx + 18}" stroke="#1B1D22" stroke-width="1.3"/>
  <rect x="{cx - 24}" y="{cy + 28}" width="48" height="7" fill="#C9A227"/>
  <rect x="{cx - 5}" y="{cy + 35}" width="10" height="12" fill="#8A6E1F"/>
</g>'''


def build_lantern() -> None:
    w, h = 300, 320
    spark_css, sparks = css_sparks(
        "keep-spark",
        [(88, 118), (196, 96), (210, 168), (78, 176), (154, 64)],
    )
    css = f"""
.keep-halo{{animation:keepHalo 3s ease-in-out infinite}}
@keyframes keepHalo{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
.keep-flame{{animation:keepFlame 1.8s ease-in-out infinite}}
@keyframes keepFlame{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
{spark_css}
"""
    body = f'''  {plate_frame(w, h)}
  {hanging_lantern(150, 148)}
{sparks}
  {chapter_title(150, 278, "Keep a", "light on", "#C9A227", rest_size=18)}
  {ts.outline("For the late review.", "standfirst", 150, 298, "#9AA0AC", "middle", size=12)}
'''
    art = A.svg_wrap(
        w,
        h,
        "Keep a light on",
        "A brass lantern hanging on graphite, flame pulsing, sparks drifting.",
        body,
        extra_css=css,
    )
    A.write(A.OUT / "atelier" / "lantern-keep.svg", art)
    A.write(A.OUT / "atelier" / "lantern.svg", art)


def build_coals() -> None:
    w, h = 520, 240
    coals = [
        (200, 128, 26, 12, "#A33418"),
        (248, 122, 30, 13, "#E4572E"),
        (300, 130, 24, 11, "#A33418"),
        (224, 140, 22, 9, "#F2A03C"),
        (280, 142, 20, 9, "#E4572E"),
        (262, 118, 14, 8, "#F2C14E"),
    ]
    coal_css = []
    coal_svg = []
    for i, (cx, cy, rx, ry, fill) in enumerate(coals):
        cls = f"coal-bit-{i}"
        coal_css.append(
            f".{cls}{{animation:coalBit{i} {2.2 + i * 0.25}s ease-in-out infinite;animation-delay:{i * 0.2}s}}"
            f"@keyframes coalBit{i}{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}"
        )
        coal_svg.append(
            f'<ellipse class="{cls}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"/>'
        )
    spark_css, sparks = css_sparks("coal-spark", [(214, 92), (262, 78), (312, 94), (238, 86)])
    css = f"""
.coal-halo{{animation:coalHalo 3.2s ease-in-out infinite}}
@keyframes coalHalo{{0%,100%{{opacity:.5}}50%{{opacity:.95}}}}
{"".join(coal_css)}
{spark_css}
"""
    body = f'''  {plate_frame(w, h)}
  {chapter_title(260, 40, "Banked", "coals", rest_size=20)}
  {ornament(260, 54, 58)}
  <ellipse class="coal-halo" cx="260" cy="118" rx="150" ry="56" fill="url(#hearth)"/>
  <ellipse cx="260" cy="148" rx="132" ry="40" fill="#2A2D35"/>
  <ellipse cx="260" cy="144" rx="118" ry="32" fill="#1A1C22"/>
  <path d="M142 144 A118 32 0 0 0 378 144" fill="none" stroke="#8A6E1F" stroke-width="2" opacity=".75"/>
  <rect x="148" y="168" width="8" height="22" fill="#2A2D35"/>
  <rect x="364" y="168" width="8" height="22" fill="#2A2D35"/>
  {chr(10).join(coal_svg)}
{sparks}
  {ts.outline("Never fully out.", "standfirst", 260, 212, "#9AA0AC", "middle", size=13)}
'''
    art = A.svg_wrap(
        w,
        h,
        "Banked coals",
        "An iron dish of banked embers, still glowing, with sparks lifting off.",
        body,
        extra_css=css,
    )
    A.write(A.OUT / "atelier" / "coals-dish.svg", art)
    A.write(A.OUT / "atelier" / "ember.svg", art)
    A.write(A.OUT / "atelier" / "koi.svg", art)


def build() -> None:
    build_desk()
    build_kettle()
    build_lantern()
    build_coals()


if __name__ == "__main__":
    build()
