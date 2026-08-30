#!/usr/bin/env python3
"""Dragon Post walk cycle.

GitHub SVGs smear pixel art if you rotate or slide a single bitmap. The walk
is four redrawn poses swapped by discrete opacity: feet step, tail wags, wing
bobs, and a white breath puff drifts as its own layer. The torso stays put.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_atelier as A  # noqa: E402
import typeset as ts  # noqa: E402

# Torso is the side-on body without the last five foot rows, so the feet layer
# can lift and stride without the whole dragon sliding.
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
_FOOT_FORE = A.pad(
    [
        "kbbbbbbbk.",
        "kbbbbbbbkk",
        "kdbkbkbbBk",
        "kHdkHkdHkk",
        ".kkkkkkkkk",
    ]
)

FEET_W, FEET_H = 24, 8
# Canvas y=3 maps to body row 29, matching the original planted feet.
FEET_AT = (A.BODY_AT[0], A.BODY_AT[1] + len(DRAGON_TORSO) - 3)


def _feet_pose(hind: tuple[int, int], fore: tuple[int, int]) -> list[str]:
    return A.stack([(_FOOT_HIND, *hind), (_FOOT_FORE, *fore)], FEET_W, FEET_H)


# Four-frame walk. y=3 planted, y=0 lifted (three pixels up). x is the stride.
DRAGON_FEET_POSES = [
    _feet_pose((0, 3), (12, 3)),  # contact: hind back, fore reaching
    _feet_pose((0, 0), (11, 3)),  # hind passing in the air, fore planted
    _feet_pose((2, 3), (12, 3)),  # contact: hind stepped forward
    _feet_pose((1, 3), (13, 0)),  # fore passing in the air, hind planted
]

# Drift is baked into the pixels so the puff is never a translate.
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

WALK_DUR = 1.28
WALK_FEET_ORDER = [0, 1, 2, 3]
WALK_TAIL_ORDER = [1, 0, 2, 0]
WALK_WING_ORDER = [0, 1, 0, 2]
WALK_PUFF_ORDER = [0, 1, 2, 3]


def swap_poses(
    poses: list[list[str]],
    ox: float,
    oy: float,
    size: float,
    order: list[int],
    dur: float,
    cell: tuple[int, int] = (0, 0),
) -> str:
    """Flip between redrawn poses. Discrete keyTimes keep every frame crisp."""
    steps = len(order)
    keys = ";".join(f"{i / steps:.4f}" for i in range(steps + 1))
    parts: list[str] = []
    for index, pose in enumerate(poses):
        on = [1 if slot == index else 0 for slot in order]
        values = ";".join(str(v) for v in (*on, on[0]))
        parts.append(
            f'<g opacity="{on[0]}">\n'
            f"{A.rle_rects(pose, ox + cell[0] * size, oy + cell[1] * size, size)}\n"
            f'  <animate attributeName="opacity" values="{values}" keyTimes="{keys}" '
            f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>\n</g>'
        )
    return "\n".join(parts)


def walking_dragon(ox: float, oy: float, size: float) -> str:
    """Walk-in-place: feet step, tail wags, wing bobs, puff drifts. No slide."""
    tail = swap_poses(
        A.DRAGON_TAIL_POSES, ox, oy, size, WALK_TAIL_ORDER, WALK_DUR, A.TAIL_AT
    )
    feet = swap_poses(
        DRAGON_FEET_POSES, ox, oy, size, WALK_FEET_ORDER, WALK_DUR, FEET_AT
    )
    wing = swap_poses(
        A.DRAGON_WING_POSES, ox, oy, size, WALK_WING_ORDER, WALK_DUR, A.WING_AT
    )
    puff = swap_poses(PUFF_FRAMES, ox, oy, size, WALK_PUFF_ORDER, 1.6, PUFF_AT)
    torso = A.rle_rects(
        DRAGON_TORSO, ox + A.BODY_AT[0] * size, oy + A.BODY_AT[1] * size, size
    )
    return f"""<g>
{tail}
{torso}
{feet}
{wing}
{puff}
</g>"""


def walk_layers(index: int) -> list[tuple[list[str], int, int]]:
    """One flattened pose, for sprite_lab / cairosvg verification."""
    return [
        (A.DRAGON_TAIL_POSES[WALK_TAIL_ORDER[index]], *A.TAIL_AT),
        (DRAGON_TORSO, *A.BODY_AT),
        (DRAGON_FEET_POSES[index], *FEET_AT),
        (A.DRAGON_WING_POSES[WALK_WING_ORDER[index]], *A.WING_AT),
        (PUFF_FRAMES[WALK_PUFF_ORDER[index]], *PUFF_AT),
    ]


def build() -> None:
    w, h = 520, 220
    size = 4
    ox = (w - A.DRAGON_W * size) / 2
    oy = 44
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#C9A227" stroke-width="1.5"/>
  <rect x="13" y="13" width="{w-26}" height="{h-26}" fill="none" stroke="#C9A227" stroke-width="1"/>
  {ts.outline("Dragon post", "plate", 260, 36, "#E9E6DF", "middle", size=15)}
{walking_dragon(ox, oy, size)}
  {ts.outline("The post goes out at dusk", "eyebrow", 260, 206, "#9AA0AC", "middle")}
'''
    A.write(
        A.OUT / "atelier" / "mail.svg",
        A.svg_wrap(
            w,
            h,
            "Dragon post",
            "A pixel dragon walking in place: feet step, tail wags, and a white breath puff pulses.",
            body,
        ),
    )


if __name__ == "__main__":
    build()
