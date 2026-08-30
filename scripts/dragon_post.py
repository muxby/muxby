#!/usr/bin/env python3
"""Dragon Post walk cycle.

GitHub README <img> SVGs run CSS keyframes (the contribution snake does).
SMIL <animate> opacity swaps freeze as a still, which is what the card was
doing. The walk is four redrawn poses swapped by CSS, discrete so pixels stay
sharp. Feet step, tail wags, wings bob. The whole dragon patrols left and
right so the stride actually travels.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402
import typeset as ts  # noqa: E402

# Last five rows are the planted feet. Thighs stay on the torso so a lifted
# foot never leaves a hole under the chest.
DRAGON_TORSO = A.pad(A.DRAGON_BODY[:-5])

_FOOT_HIND = A.pad(
    [
        "kdbbkk.kk.",
        ".kbkk.kBbk",
        "kdkk.kbkHk",
        "kHkk.kHdHk",
        "kkk..kkkkk",
    ]
)
# Matches body cols 11–19: a column out of the chest, not a 10-wide slab.
_FOOT_FORE = A.pad(
    [
        ".kbbbbbk.",
        "kbbbbbkk.",
        "kbkbbBk..",
        "kHdkHkk..",
        "kkkkkk...",
    ]
)

LIFT = 3
FEET_W, FEET_H = 24, 5 + LIFT
FEET_AT = (A.BODY_AT[0], A.BODY_AT[1] + len(DRAGON_TORSO) - LIFT)
FORE_X = 11


def _feet_pose(hind: tuple[int, int], fore: tuple[int, int]) -> list[str]:
    return A.stack([(_FOOT_HIND, *hind), (_FOOT_FORE, *fore)], FEET_W, FEET_H)


# Planted y=LIFT (flush with torso bottom). Lifted y=0 is three pixels up,
# still overlapping the thigh. Fore stays under the chest, never at x=16.
DRAGON_FEET_POSES = [
    _feet_pose((0, LIFT), (FORE_X, LIFT)),       # contact: hind back, fore planted
    _feet_pose((1, 0), (FORE_X - 1, LIFT)),       # hind passing, fore planted
    _feet_pose((3, LIFT), (FORE_X + 1, LIFT)),     # contact: hind forward
    _feet_pose((2, LIFT), (FORE_X + 2, 0)),       # fore reaching, still on the chest line
]

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

WALK_DUR = "0.9s"
WALK_FEET_ORDER = [0, 1, 2, 3]
WALK_TAIL_ORDER = [1, 0, 2, 0]
WALK_WING_ORDER = [0, 1, 0, 2]
WALK_PUFF_ORDER = [0, 1, 2, 3]


def _keyframe_block(name: str, order: list[int], pose_index: int) -> str:
    steps = len(order)
    on = [slot == pose_index for slot in order]
    lines = [f"@keyframes {name}{{"]
    for i, visible in enumerate(on):
        start = 100.0 * i / steps
        end = 100.0 * (i + 1) / steps - 0.05
        opacity = 1 if visible else 0
        lines.append(f"{start:.2f}%,{end:.2f}%{{opacity:{opacity}}}")
    lines.append(f"100%{{opacity:{1 if on[0] else 0}}}")
    lines.append("}")
    return "".join(lines)


def css_swap(
    prefix: str,
    poses: list[list[str]],
    ox: float,
    oy: float,
    size: float,
    order: list[int],
    dur: str,
    cell: tuple[int, int] = (0, 0),
) -> tuple[str, str]:
    """CSS pose-swap. Same mechanism GitHub already plays on the snake."""
    rules: list[str] = []
    groups: list[str] = []
    for index, pose in enumerate(poses):
        cls = f"{prefix}-{index}"
        rules.append(
            f".{cls}{{opacity:{1 if order[0] == index else 0};"
            f"animation:{name_safe(cls)} {dur} linear infinite}}"
        )
        rules.append(_keyframe_block(name_safe(cls), order, index))
        groups.append(
            f'<g class="{cls}">\n'
            f"{A.rle_rects(pose, ox + cell[0] * size, oy + cell[1] * size, size)}\n"
            f"</g>"
        )
    return "\n".join(rules), "\n".join(groups)


def name_safe(cls: str) -> str:
    return cls.replace("-", "_")


PATROL_PX = 90
PATROL_DUR = "7.2s"


def walking_dragon(ox: float, oy: float, size: float) -> tuple[str, str]:
    css_parts: list[str] = []
    svg_parts: list[str] = []
    for prefix, poses, order, dur, cell in (
        ("dp-tail", A.DRAGON_TAIL_POSES, WALK_TAIL_ORDER, WALK_DUR, A.TAIL_AT),
        ("dp-feet", DRAGON_FEET_POSES, WALK_FEET_ORDER, WALK_DUR, FEET_AT),
        ("dp-wing", A.DRAGON_WING_POSES, WALK_WING_ORDER, WALK_DUR, A.WING_AT),
        ("dp-puff", PUFF_FRAMES, WALK_PUFF_ORDER, "1.4s", PUFF_AT),
    ):
        css, groups = css_swap(prefix, poses, ox, oy, size, order, dur, cell)
        css_parts.append(css)
        svg_parts.append(groups)
    torso = A.rle_rects(
        DRAGON_TORSO, ox + A.BODY_AT[0] * size, oy + A.BODY_AT[1] * size, size
    )
    css_parts.append(
        ".dp-patrol{animation:dp-patrol "
        + PATROL_DUR
        + " linear infinite}"
        "@keyframes dp-patrol{"
        f"0%{{transform:translateX(-{PATROL_PX}px)}}"
        f"45%{{transform:translateX({PATROL_PX}px)}}"
        f"50%{{transform:translateX({PATROL_PX}px)}}"
        f"95%{{transform:translateX(-{PATROL_PX}px)}}"
        f"100%{{transform:translateX(-{PATROL_PX}px)}}"
        "}"
        ".dp-face{animation:dp-face "
        + PATROL_DUR
        + " linear infinite;transform-box:fill-box;transform-origin:50% 72%}"
        "@keyframes dp-face{"
        "0%,49.9%{transform:scaleX(1)}"
        "50%,99.9%{transform:scaleX(-1)}"
        "100%{transform:scaleX(1)}}"
    )
    svg = f"""<g class="dp-patrol">
<g class="dp-face">
{svg_parts[0]}
{torso}
{svg_parts[1]}
{svg_parts[2]}
{svg_parts[3]}
</g>
</g>"""
    return "\n".join(css_parts), svg


def walk_layers(index: int) -> list[tuple[list[str], int, int]]:
    return [
        (A.DRAGON_TAIL_POSES[WALK_TAIL_ORDER[index]], *A.TAIL_AT),
        (DRAGON_TORSO, *A.BODY_AT),
        (DRAGON_FEET_POSES[index], *FEET_AT),
        (A.DRAGON_WING_POSES[WALK_WING_ORDER[index]], *A.WING_AT),
        (PUFF_FRAMES[WALK_PUFF_ORDER[index]], *PUFF_AT),
    ]


def build() -> None:
    w, h = 640, 280
    size = 6
    ox = (w - A.DRAGON_W * size) / 2
    oy = 48
    css, dragon = walking_dragon(ox, oy, size)
    ground_y = oy + (FEET_AT[1] + FEET_H) * size - 2
    body = f'''  <style>
{css}
.c{{shape-rendering:crispEdges}}
</style>
  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#C9A227" stroke-width="1.5"/>
  <rect x="13" y="13" width="{w-26}" height="{h-26}" fill="none" stroke="#C9A227" stroke-width="1"/>
  {ts.outline("Dragon post", "plate", 320, 40, "#E9E6DF", "middle", size=16)}
  <path d="M40 {ground_y} H{w - 40}" stroke="#8A6E1F" stroke-width="2" opacity=".7"/>
{dragon}
  {ts.outline("The post goes out at dusk", "eyebrow", 320, 258, "#9AA0AC", "middle")}
'''
    wrapped = A.svg_wrap(
        w,
        h,
        "Dragon post",
        "A pixel dragon walking left and right: front leg planted on the chest, feet stepping, facing the direction of travel.",
        body,
    )
    A.write(A.OUT / "atelier" / "dragon-post.svg", wrapped)
    A.write(A.OUT / "atelier" / "mail.svg", wrapped)


if __name__ == "__main__":
    build()
