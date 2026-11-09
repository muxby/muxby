#!/usr/bin/env python3
"""Dragon Post: the companion walks the evening round with a letter.

GitHub README <img> SVGs run CSS keyframes, so every moving part here is CSS.
The walk is four redrawn leg poses swapped on hard cuts, so pixels stay sharp:
contact, passing, contact, passing. The body rises one cell on each passing
pose, which is what gives a walk its weight. The dragon stays centred and the
world scrolls past it: path stones at walking speed, fence posts at half speed
for depth, hills and sky fixed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402
import typeset as ts  # noqa: E402

# Head, neck, arms, haunch, and belly from the standing dragon, cut above the
# planted foot. The legs come from the walk poses below instead.
TORSO_ROWS = 31
DRAGON_TORSO = A.pad(A.DRAGON_BODY[:TORSO_ROWS])

# Each leg is a full shin so the body can rise a cell without opening a gap:
# the top rows hide behind the haunch until the torso lifts. The foot has a
# shaded heel and a bone claw at the toe.
_LEG_NEAR = A.pad(
    [
        ".kbbk....",
        ".kbbk....",
        ".kbbk....",
        ".kbBk....",
        ".kbbk....",
        ".kbbbk...",
        ".kbbbbkk.",
        "kdbbbbbHk",
        "kkkkkkkkk",
    ]
)
_LEG_FAR = A.pad(
    [
        ".kddk....",
        ".kddk....",
        ".kddk....",
        ".kddk....",
        ".kddk....",
        ".kdddk...",
        ".kddddkk.",
        "knddddnHk",
        "kkkkkkkkk",
    ]
)

LEG_TOP = TORSO_ROWS - 2  # planted legs start two rows up, under the haunch
FEET_W, FEET_H = 22, 11
FEET_AT = (A.BODY_AT[0], LEG_TOP - 2)  # two spare rows above for lifted poses


def _feet_pose(far: tuple[int, int], near: tuple[int, int]) -> list[str]:
    """Far leg behind, near leg in front. y is 2 for planted, 0 for lifted."""
    return A.stack([(_LEG_FAR, *far), (_LEG_NEAR, *near)], FEET_W, FEET_H)


# The planted foot slides back as the body moves forward; the lifted one swings
# through. Near: 8, 6, 3, lift. Far: 3, lift, 8, 6.
DRAGON_FEET_POSES = [
    _feet_pose((3, 2), (8, 2)),  # contact: near forward, far back
    _feet_pose((5, 0), (6, 2)),  # passing: far swings through
    _feet_pose((8, 2), (3, 2)),  # contact: far forward, near back
    _feet_pose((6, 2), (5, 0)),  # passing: near swings through
]
BOB = [0, 1, 0, 1]  # cells the body rises on each pose

# A sealed letter held in the foreclaws.
ENVELOPE = A.pad(
    [
        "kkkkkkkkk",
        "kzPPPPPzk",
        "kPzPPPzPk",
        "kPPzmzPPk",
        "kPPPPPPPk",
        "kkkkkkkkk",
    ]
)
_claws = A.find_pixels(DRAGON_TORSO, "H")
_hand = [(x, y) for x, y in _claws if y > 20]
ENVELOPE_AT = (A.BODY_AT[0] + min(x for x, _ in _hand) - 2, A.BODY_AT[1] + max(y for _, y in _hand) + 1)

PUFF_FRAMES = [
    A.pad([".e.", "ePe", ".e."]),
    A.pad(["..e..", ".eYOe", "..e.."]),
    A.pad(["....e..", "...ePe.", "..e..e.", "...e..."]),
    A.pad(["......e.", ".....e.e", "....e...", ".....e.."]),
]

_mouth = A.find_pixels(A.DRAGON_BODY, "M")
_mx = max(x for x, _ in _mouth)
_lips = [y for x, y in _mouth if x == _mx]
PUFF_AT = (A.BODY_AT[0] + _mx + 1, A.BODY_AT[1] + round(sum(_lips) / len(_lips)) - 1)

WALK_DUR = 0.96  # seconds for one full stride (four poses)
WALK_FEET_ORDER = [0, 1, 2, 3]
WALK_TAIL_ORDER = [1, 0, 2, 0]
WALK_WING_ORDER = [0, 1, 0, 2]
WALK_PUFF_ORDER = [0, 1, 2, 3]
STRIDE_CELLS = 10  # how far the world slides per stride, in cells


def css_swap(
    prefix: str,
    poses: list[list[str]],
    ox: float,
    oy: float,
    size: float,
    order: list[int],
    dur: float,
    cell: tuple[int, int] = (0, 0),
) -> tuple[str, str]:
    """Hard-cut pose swap: exactly one pose visible at any moment."""
    rules: list[str] = []
    groups: list[str] = []
    for index, pose in enumerate(poses):
        cls = f"{prefix}-{index}"
        rules.append(A.css_pose_cycle(cls, order, index, dur))
        groups.append(
            f'<g class="{cls}">\n'
            f"{A.rle_rects(pose, ox + cell[0] * size, oy + cell[1] * size, size)}\n"
            f"</g>"
        )
    return "\n".join(rules), "\n".join(groups)


def walking_dragon(ox: float, oy: float, size: float) -> tuple[str, str]:
    css_parts: list[str] = []
    svg_parts: dict[str, str] = {}
    for prefix, poses, order, dur, cell in (
        ("dp-tail", A.DRAGON_TAIL_POSES, WALK_TAIL_ORDER, WALK_DUR, A.TAIL_AT),
        ("dp-feet", DRAGON_FEET_POSES, WALK_FEET_ORDER, WALK_DUR, FEET_AT),
        ("dp-wing", A.DRAGON_WING_POSES, WALK_WING_ORDER, WALK_DUR * 2, A.WING_AT),
        ("dp-puff", PUFF_FRAMES, WALK_PUFF_ORDER, 1.4, PUFF_AT),
    ):
        css, groups = css_swap(prefix, poses, ox, oy, size, order, dur, cell)
        css_parts.append(css)
        svg_parts[prefix] = groups

    steps = len(BOB)
    frames = "".join(f"{100 * i / steps:.2f}%{{transform:translate(0,{-BOB[i] * size}px)}}" for i in range(steps))
    css_parts.append(
        f".dp-bob{{animation:dpBob {WALK_DUR}s step-end infinite}}"
        f"@keyframes dpBob{{{frames}100%{{transform:translate(0,0)}}}}"
    )
    torso = A.rle_rects(DRAGON_TORSO, ox + A.BODY_AT[0] * size, oy + A.BODY_AT[1] * size, size)
    letter = A.rle_rects(ENVELOPE, ox + ENVELOPE_AT[0] * size, oy + ENVELOPE_AT[1] * size, size)
    shadow_y = oy + (FEET_AT[1] + FEET_H) * size
    svg = f"""<ellipse cx="{ox + 20 * size}" cy="{shadow_y}" rx="{13 * size}" ry="{1.3 * size}" fill="url(#postShadow)"/>
<g class="dp-bob">
{svg_parts["dp-tail"]}
</g>
<g>
{svg_parts["dp-feet"]}
</g>
<g class="dp-bob">
{torso}
{letter}
{svg_parts["dp-wing"]}
{svg_parts["dp-puff"]}
</g>"""
    return "\n".join(css_parts), svg


def walk_layers(index: int) -> list[tuple[list[str], int, int]]:
    """One frame of the walk as flat layers, for scripts/sprite_lab.py."""
    rise = BOB[index]
    return [
        (A.DRAGON_TAIL_POSES[WALK_TAIL_ORDER[index]], A.TAIL_AT[0], A.TAIL_AT[1] - rise),
        (DRAGON_FEET_POSES[index], *FEET_AT),
        (DRAGON_TORSO, A.BODY_AT[0], A.BODY_AT[1] - rise),
        (ENVELOPE, ENVELOPE_AT[0], ENVELOPE_AT[1] - rise),
        (A.DRAGON_WING_POSES[WALK_WING_ORDER[index]], A.WING_AT[0], A.WING_AT[1] - rise),
        (PUFF_FRAMES[WALK_PUFF_ORDER[index]], PUFF_AT[0], PUFF_AT[1] - rise),
    ]


def scrolling(cls: str, tile: float, dur: float, w: float, draw) -> tuple[str, str]:
    """Repeat `draw(x)` every `tile` px across the card and slide it left by
    one tile per loop, so the seam never shows."""
    count = int(w // tile) + 3
    css = (
        f".{cls}{{animation:{cls} {dur:.3f}s linear infinite}}"
        f"@keyframes {cls}{{from{{transform:translate(0,0)}}to{{transform:translate({-tile}px,0)}}}}"
    )
    svg = f'<g class="{cls}">' + "".join(draw(i * tile) for i in range(count)) + "</g>"
    return css, svg


def build() -> None:
    w, h = 640, 344
    size = 6
    ox = (w - A.DRAGON_W * size) / 2 - 10
    oy = 50
    ground_y = oy + (FEET_AT[1] + FEET_H) * size
    css, dragon = walking_dragon(ox, oy, size)

    stride_px = STRIDE_CELLS * size
    stones_css, stones = scrolling(
        "dp-stones",
        stride_px,
        WALK_DUR,
        w,
        lambda x: (
            f'<rect x="{x + 6}" y="{ground_y + 6}" width="12" height="4" fill="#3A342C"/>'
            f'<rect x="{x + 34}" y="{ground_y + 14}" width="8" height="3" fill="#2A2620"/>'
            f'<rect x="{x + 22}" y="{ground_y - 2}" width="3" height="3" fill="#4E7C72" opacity=".7"/>'
            f'<rect x="{x + 25}" y="{ground_y - 5}" width="3" height="6" fill="#2F5A52" opacity=".8"/>'
        ),
    )
    fence_css, fence = scrolling(
        "dp-fence",
        stride_px * 2,
        WALK_DUR * 4,
        w,
        lambda x: (
            f'<rect x="{x + 10}" y="{ground_y - 46}" width="6" height="46" fill="#30363E"/>'
            f'<rect x="{x - 40}" y="{ground_y - 36}" width="{stride_px * 2}" height="3" fill="#30363E"/>'
            f'<rect x="{x - 40}" y="{ground_y - 20}" width="{stride_px * 2}" height="3" fill="#30363E"/>'
        ),
    )
    star_css, stars = A.twinkle_stars(
        [(80, 60, 4, "3.1s"), (180, 30, 3, "2.7s"), (470, 44, 3, "3.6s"), (560, 82, 4, "2.9s"), (300, 92, 2.5, "4.0s")],
        "dps",
    )
    css_all = "\n".join(
        [
            css,
            stones_css,
            fence_css,
            star_css,
            ".dp-lamp{animation:dpLamp 2.4s ease-in-out infinite}",
            "@keyframes dpLamp{0%,100%{opacity:.55}50%{opacity:1}}",
        ]
    )
    defs = """
    <linearGradient id="duskBand" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#14161A"/>
      <stop offset=".55" stop-color="#1D1F26"/>
      <stop offset=".86" stop-color="#3A2420"/>
      <stop offset="1" stop-color="#5C2A18"/>
    </linearGradient>
    <radialGradient id="sunset" cx="50%" cy="100%" r="60%">
      <stop offset="0" stop-color="#F2A03C" stop-opacity=".55"/>
      <stop offset=".5" stop-color="#E4572E" stop-opacity=".18"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="postShadow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#000000" stop-opacity=".55"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>"""
    sky_bottom = ground_y
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="#17181C"/>
  <svg x="14" y="14" width="{w - 28}" height="{h - 28}" viewBox="14 14 {w - 28} {h - 28}" overflow="hidden">
  <rect x="14" y="14" width="{w - 28}" height="{sky_bottom - 14}" fill="url(#duskBand)"/>
  <ellipse cx="{w * 0.78}" cy="{sky_bottom}" rx="220" ry="90" fill="url(#sunset)"/>
  {stars}
  <circle cx="96" cy="78" r="15" fill="#E9E6DF" opacity=".9"/>
  <circle cx="103" cy="73" r="14" fill="#1A1C22"/>
  <path d="M14 {sky_bottom - 40} C 120 {sky_bottom - 78}, 220 {sky_bottom - 52}, 330 {sky_bottom - 64} C 440 {sky_bottom - 76}, 540 {sky_bottom - 50}, {w} {sky_bottom - 70} L{w} {sky_bottom} L14 {sky_bottom} Z" fill="#1E2629"/>
  <rect x="{w - 132}" y="{sky_bottom - 74}" width="30" height="22" fill="#14161A"/>
  <path d="M{w - 136} {sky_bottom - 74} L{w - 117} {sky_bottom - 88} L{w - 98} {sky_bottom - 74} Z" fill="#14161A"/>
  <rect x="{w - 121}" y="{sky_bottom - 66}" width="7" height="7" fill="#F2C14E" class="dp-lamp"/>
  {fence}
  <rect x="14" y="{ground_y}" width="{w - 28}" height="{h - ground_y}" fill="#1E2624"/>
  <rect x="14" y="{ground_y}" width="{w - 28}" height="3" fill="#8A6E1F" opacity=".75"/>
  {stones}
  </svg>
  <rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="none" stroke="#C9A227" stroke-width="1.5"/>
  <rect x="13" y="13" width="{w - 26}" height="{h - 26}" fill="none" stroke="#C9A227" stroke-width="1"/>
{dragon}
  {ts.outline("Night walk", "plate", w / 2, 42, "#E9E6DF", "middle", size=19)}
  {ts.outline("The post goes out at dusk", "eyebrow", w / 2, h - 30, "#C6C2B8", "middle", size=13)}
'''
    wrapped = A.svg_wrap(
        w,
        h,
        "Night walk",
        "A small dragon walks the evening path with a sealed letter in its claws. The post goes out at dusk.",
        body,
        extra_defs=defs,
        extra_css=css_all,
    )
    A.write(A.OUT / "atelier" / "dragon-post.svg", wrapped)
    A.write(A.OUT / "atelier" / "mail.svg", wrapped)


if __name__ == "__main__":
    build()
