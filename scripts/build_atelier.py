#!/usr/bin/env python3
"""Generate Obsidian Forge SVG assets for the muxby profile.

Graphite, iron, bone, brass, and one ember. No pastels, no neon, no HUD,
no charts.
"""

from __future__ import annotations

from pathlib import Path

import typeset as ts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

# Obsidian Forge. Graphite and iron, bone plaques, brass hardware, one ember
# accent, one cold patina. Sprite colors live here; scene colors live in the
# build_* functions below. "k" is the sprite outline and nothing else.
PALETTE = {
    ".": None,
    "k": "#14161A",  # outline
    "B": "#E4572E",  # body bright
    "b": "#C0431F",  # ember body
    "d": "#7E2A12",  # body shadow
    "C": "#E0B457",  # brass belly light
    "c": "#C9A227",  # brass belly
    "W": "#4A1B0C",  # wing strut
    "w": "#8E3218",  # wing membrane
    "L": "#D06A34",  # wing highlight
    "H": "#DCD6C8",  # horn
    "h": "#9C9484",  # horn shadow
    "e": "#F7F5F0",  # eye white
    "p": "#111214",  # pupil
    "s": "#EC8A62",  # blush
    "n": "#6E2311",  # nose
    "M": "#2A0E08",  # mouth
    "T": "#C0431F",
    "t": "#7E2A12",
    "G": "#4E7C72",  # patina
    "g": "#2F5A52",  # patina dark
    "Y": "#FFE3A3",  # fire light
    "O": "#F2A03C",  # fire
    "R": "#E4572E",  # ember
    "F": "#A33418",  # fire deep
    "S": "#6B7078",  # smoke
    "X": "#C9A227",  # brass
    "P": "#E9E6DF",  # bone
    "I": "#0F1013",  # obsidian
    "o": "#C9772F",  # fox coat
    "u": "#8A4418",  # fox dark
    "q": "#E9E6DF",  # fox bone
    "m": "#C0431F",  # ember mid
    "A": "#6E9C90",  # patina light
    "a": "#2A4A44",  # patina deep
    "N": "#3A342C",  # iron / charred wood
    "r": "#7E2A12",  # deep clay
    "z": "#C6C2B8",  # ash card
    "y": "#F7F5F0",  # chalk / lamp glass
    "1": "#3A342C",  # bark
    "2": "#2A3138",  # distant ridge
    "3": "#4A443A",  # path
    "4": "#1F222A",  # dusk high
    "5": "#262B33",  # dusk low
    "6": "#F2C14E",  # window glow
    "7": "#1B2A2A",  # dusk fir
    "8": "#241F1A",  # soil
    "9": "#FFE3A3",  # spark
}

def pad(rows: list[str]) -> list[str]:
    width = max(len(r) for r in rows)
    return [r.ljust(width, ".") for r in rows]


def rle_rects(rows: list[str], ox: float, oy: float, size: float, extra: str = "") -> str:
    rows = pad(rows)
    parts: list[str] = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            color = PALETTE.get(ch)
            if color is None:
                x += 1
                continue
            w = 1
            while x + w < len(row) and row[x + w] == ch:
                w += 1
            parts.append(
                f'<rect x="{ox + x * size}" y="{oy + y * size}" width="{w * size}" height="{size}" fill="{color}"{extra}/>'
            )
            x += w
    return "\n".join(parts)


def sprite_text(message: str, role: str, x: float, y: float, color_key: str, **kw) -> str:
    """Outlined lettering in a sprite color, for labels inside the pixel scenes.

    Lettering is typeset, never drawn on the pixel grid: see scripts/typeset.py.
    Taking the color from PALETTE keeps label ink and sprite ink the same thing.
    """
    return ts.outline(message, role, x, y, PALETTE[color_key], **kw)


# ---------------------------------------------------------------------------
# Sprites
# ---------------------------------------------------------------------------

def find_pixels(rows: list[str], chars: str) -> list[tuple[int, int]]:
    found = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in chars:
                found.append((x, y))
    return found


def stack(layers: list[tuple[list[str], int, int]], w: int, h: int) -> list[str]:
    """Flatten offset sprite layers into one table, later layers on top."""
    canvas = [["." for _ in range(w)] for _ in range(h)]
    for sprite, ox, oy in layers:
        for y, row in enumerate(pad(sprite)):
            for x, ch in enumerate(row):
                if ch == "." or not (0 <= oy + y < h and 0 <= ox + x < w):
                    continue
                canvas[oy + y][ox + x] = ch
    return ["".join(row) for row in canvas]


# The side-on dragon is three layers so the wing and tail can really move.
# Head and snout face right, with the horns swept back over the skull, one big
# eye (p pupil, e catchlight), a blush (s), and a mouth split into an upper
# muzzle and a lower jaw so it reads as open. The M run is where breath leaves.
DRAGON_BODY = pad(
    [
        ".................kkk..........",
        ".................kHkk.........",
        "..........kkkk...kHHk.........",
        "..........kHHkk..kHHkk........",
        "..........kHHHkk.kHHHk........",
        "..........kkHHHkkkhHHk........",
        "...........kHhHHBBHHHkk.......",
        "...........kkHHHbbbHbBkk......",
        "..........kkBbHbbbbbbbBkk.....",
        "..........kBbbbbbbeppbbBk.....",
        "..........kbbbbbbbpppbbbkkkkk.",
        ".........kkbbbbbbbpphbbbBBBBkk",
        ".........kBbbbbbbbbbbbbbbbbnnk",
        ".........kkbbbbbbbbbbbbbbbbbdk",
        "..........kbbbbbbbbbbbbbbbbdMk",
        "..........kHbbbsssbbbMMMMMMMMk",
        ".......kkkkbbbbbsbbbbbbbbbbkMk",
        "....kkkkBBHbbbbbbbbbbbbbbbbBkk",
        "...kkBBBbbbbbbbbbbbbdddddddkk.",
        "..kkBbbbbbbbbcccbbddkkkkkkkk..",
        ".kkBbbbbbbbCCCCCCCkkk.........",
        ".kBbbbbbbbCCCCCCCCCk..........",
        ".kbbbbbbbCCCCCCCCCCk..........",
        "kkbbbbbbbcccccccccckk.........",
        "kBbbbbbbCCCCCCCCCCCCk.........",
        "kkbbbbk.CCCCCCCCCCCkk.........",
        ".kbbbbk.CCCCCCCCCCCk..........",
        "kkbbbkk.kcccccccccck..........",
        "kbbbkk...kkkCCCCCCCk..........",
        "kdbbkk.kk..kbbbbbbbk..........",
        ".kbkk.kBbk.kbbbbbbbkk.........",
        "kdkk.kbkHk.kdbkbkbbBk.........",
        "kHkk.kHdHk.kHdkHkdHkk.........",
        "kkk..kkkkk.kkkkkkkkk..........",
    ]
)

# Wing and tail get three poses each, cycled by opacity. Rotating pixel art with
# animateTransform resamples it into mush, so each pose is redrawn on the grid
# and swapped in instead. All poses of a layer share one offset.
#
# The wing rides above the back rather than folded over the flank, so it
# silhouettes against the sky instead of reading as a hole in the body.
DRAGON_WING_POSES = [
    pad(
        [
            "............kkk...",
            ".........kkkkHk...",
            "......kkkkwLLkk...",
            "....kkkLLLLLLk....",
            "...kkLLwwLLLLkk...",
            "...kwwwwLwLwwLk...",
            "...kwwwLwwLwwLk...",
            "...kwwLwwwLwwLk...",
            "..kkLLwwwLwwwLk...",
            ".kkLwwwwLwwwwLkk..",
            ".kLkwwwwLwwwwwLk..",
            ".kkwwwwwLwwwwwLk..",
            "..kwwwwLwwwwwwLk..",
            "..kkwwLwwwwwwwLk..",
            "...kkwLwwwwwwwLkk.",
            "....kwLwwwwwwwLwk.",
            "....kLkkwwwwwwwLk.",
            "....kkkkkkkkwwwLk.",
            "...........kkkkLk.",
            "..............kkk.",
        ]
    ),
    pad(
        [
            "..................",
            "........kkk.......",
            ".......kkHk.......",
            ".....kkkLkk.......",
            "...kkkLLLLk.......",
            ".kkkwLwLLLkk......",
            ".kwLLwLwLwLk......",
            ".kLwwLwLwwLkk.....",
            "kkwwLwwLwwLwk.....",
            "kwwwLwwLwwwLkk....",
            "kkwLwwwLwwwLwk....",
            "kkLwwwLwwwwwLk....",
            "kLkwwwLwwwwwLkk...",
            "kLwwwwLwwwwwwLk...",
            "kkwwwwLwwwwwwLkk..",
            ".kwwwwLwwwwwwwLk..",
            ".kkkwLwwwwwwwwLkk.",
            "...kkLwwwwwwwwwLk.",
            "....kLkkkkkkkkkLk.",
            "....kkk.......kkk.",
        ]
    ),
    pad(
        [
            "...............kkk",
            ".......kkkkkkkkkHk",
            "......kkwLLLLLLLkk",
            ".....kkwLwwwLLLLk.",
            ".....kwwwwwLwLwLk.",
            ".....kwwwLLwLwwLk.",
            "....kkwLLwwwLwwLk.",
            "...kkLLwwwwLwwwLk.",
            "...kLkwwwwLwwwwLk.",
            "...kwwwwwwLwwwwLk.",
            "...kwwwwwLwwwwwLk.",
            "...kkwwwLwwwwwwLk.",
            "....kkwLwwwwwwwLk.",
            ".....kwLwwwwwwwLk.",
            ".....kLwwwwwwwwLk.",
            ".....kkkwwwwwwwLk.",
            ".......kkkkwwwwLk.",
            "..........kkkkwLk.",
            ".............kkLk.",
            "..............kkk.",
        ]
    ),
]
DRAGON_WING = DRAGON_WING_POSES[0]

# Thick at the hip, pinched below a spade fin so the tip reads as a blade.
DRAGON_TAIL_POSES = [
    pad(
        [
            "........................",
            "........................",
            "..kkk...................",
            ".kkbkk..................",
            ".kbbbk..................",
            "kkbBbkk.................",
            "kbBBBbkk................",
            "bBBBBBbk................",
            "bbBBBbbk................",
            "kbBBBbkk................",
            "kkbbbkk.................",
            ".kkbkk...........kkkkk..",
            ".kkBkk..........kkBBBkk.",
            ".kBbBkk........kkBbbbBkk",
            ".kkbbBkk......kkBbbbbbBk",
            "..kbbbBkk...kkkBbbbbbbbk",
            "..kdbbbBkkkkkBBbbbbbbbdk",
            "..kkdbbbBBBBBbbbbbbbbdkk",
            "...kkdbbbbbbbbbbbbbddkk.",
            "....kkdbbbbbbbbbbddkkk..",
            ".....kkdddbbbbdddkkk....",
            "......kkkkddddkkkk......",
            ".........kkkkkk.........",
            "........................",
        ]
    ),
    pad(
        [
            "........................",
            "........................",
            "........................",
            "........................",
            "kkkk....................",
            "kbbkk...................",
            "kbbbkk..................",
            "kbBbbk..................",
            "bBBBbkk.................",
            "bBBBBbk.................",
            "bBBBBbk.................",
            "bbBBbkk..........kkkkk..",
            "kbbbbk..........kkBBBkk.",
            "kkbbkk.........kkBbbbBkk",
            ".kkBkk........kkBbbbbbBk",
            ".kBbBkk......kkBbbbbbbbk",
            ".kkbbBkkk...kkBbbbbbbbdk",
            "..kdbbBBkkkkkBbbbbbbbdkk",
            "..kkdbbbBBBBBbbbbbbbdkk.",
            "...kkdbbbbbbbbbbbbddkk..",
            "....kkdbbbbbbbbbbdkkk...",
            ".....kkddddbbddddkk.....",
            "......kkkkkddkkkkk......",
            "..........kkkk..........",
        ]
    ),
    pad(
        [
            "...kkk..................",
            "...kbkk.................",
            "..kkbbk.................",
            ".kkbBbkk................",
            "kkbBBBbk................",
            "kbBBBBbkk...............",
            "kbBBBBBbk...............",
            "kkbBBBbkk...............",
            ".kbbbbkk................",
            ".kkbbkk.................",
            "..kkkk..................",
            "..kBBk...........kkkkk..",
            "..kbbkk.........kkBBBkk.",
            "..kbbBkk......kkkBbbbBkk",
            "..kdbbBkk....kkBBbbbbbBk",
            "..kkbbbBkkkkkkBbbbbbbbbk",
            "...kdbbbBBBBBBbbbbbbbbdk",
            "...kkdbbbbbbbbbbbbbbbdkk",
            "....kkddbbbbbbbbbbbddkk.",
            ".....kkkddbbbbbbdddkkk..",
            ".......kkkddddddkkkk....",
            ".........kkkkkkkk.......",
            "........................",
            "........................",
        ]
    ),
]
DRAGON_TAIL = DRAGON_TAIL_POSES[0]

DRAGON_W, DRAGON_H = 40, 36
BODY_AT = (10, 0)
WING_AT = (2, 3)
TAIL_AT = (0, 12)

# One flat table for the cameos that fly past and do not need to flap.
DRAGON_IDLE = stack(
    [(DRAGON_TAIL, *TAIL_AT), (DRAGON_BODY, *BODY_AT), (DRAGON_WING, *WING_AT)],
    DRAGON_W,
    DRAGON_H,
)

# Front-on hatchling: swept horns, two shiny eyes, a snout with nostrils and an
# open mouth, brass belly plates, and wings held out either side.
DRAGON_SIT = pad(
    [
        "......kkk...........kkk.......",
        "......kHkk.........kkHk.......",
        "......kHHk.........kHHk.......",
        "......kHHkkkkkkkkkkkHHk.......",
        "......kHHHkBBBBBBBkHHHk.......",
        "......kkhHHbbbbbbbHHhkk.......",
        "......kkHHHbbbbbbbHHHkk.......",
        "......kBbbbbbbbbbbbbbBk.......",
        ".....kkbbbbbbbbbbbbbbbkk......",
        ".....kBbbeppbbbbbeppbbBk......",
        ".....kbbbpppbbbbbpppbbbk......",
        ".kkk.kbbbpphbbbbbpphbbbk.kkk..",
        "kkwkkkbbbbbbbbbbbbbbbbbkkkwkk.",
        "kwLLkkdssbbbbbbbbbbbssdkkLLwk.",
        "kwLLkkkbbbbbbnbnbbbbbbkkkLLwk.",
        "kwLwLkkdbbbbbbbbbbbbbdkkLwLwkk",
        "wwLwLwkkbbbbMMMMMbbbbkkwLwLwwk",
        "wwLwLwkBbbbbbMbMbbbbbBkwLwLwwk",
        "kwLwLwwbbbbbcccccbbbbbwwLwLwkk",
        "kwLwLwwbbbbCCCCCCCbbbbwwLwLwk.",
        "kwLwwLwbbbCCCCCCCCCbbbwLwwLwk.",
        "kkLwwLbbbCCCCCCCCCCCbbbLwwLkk.",
        ".kkkbbbbbcccccccccccbbbbbkkk..",
        "...kbbbbbCCCCCCCCCCCbbbbbk....",
        "...kdbbbbCCCCCCCCCCCbbbbdk....",
        "...kkddbbCCCCCCCCCCCbbddkk....",
        "....kkkbbbcccccccccbbbkkk.....",
        ".....kBbbbbCCCCCCCbbbbBk......",
        ".....kbbbbbbCCCCCbbbbbbk......",
        ".....kdHbHbHdddddHbHbHdk......",
        ".....kkdddddkkkkkdddddkk......",
        "......kkkkkkk...kkkkkkk.......",
    ]
)

FOX_SIT = pad(
    [
        "......kkkk.......",
        ".....koookk......",
        "....kqoqoqok.....",
        "....kqppppqk.....",
        "....kqoqqqok.....",
        ".....kuqquk......",
        "....kooooouk.....",
        "...koooqqoouk....",
        "...kooqqqqook....",
        "....koooooookk...",
        ".....kuk..kuk....",
        ".....kkk..kkk.q..",
        "...............q.",
        "............qquk.",
        "...........kuuuk.",
        "............kkk..",
    ]
)

# Breath, not a campfire: a jet that leaves the mouth sideways. Hottest at the
# lips (Y), cooling outward through O and R to the F fringe, with 9 for sparks.
# Frame 0 is a full jet so fire reads even when SMIL is off (cairosvg, first paint).
FIRE_FRAMES = [
    pad(
        [
            "......FF...F...9......",
            "...FFFFFFFF..F..9.....",
            ".YOOORRRRRRRFFF.......",
            "YYOOOORRRRRRRRRFFF....",
            "YYYOOOOORRRRRRRRRRFFF.",
            "YYOOOORRRRRRRRRFFF....",
            ".YOOORRRRRRRFFF.......",
            "...FFFFFFFF..F..9.....",
            "......FF...F...9......",
        ]
    ),
    pad(
        [
            "..F....",
            ".YOORF.",
            "YYOORRF",
            ".YOORF.",
            "..F....",
        ]
    ),
    pad(
        [
            "...FF...9..",
            ".YOORRRFF..",
            "YYOOORRRRFF",
            ".YOORRRFF..",
            "...FF......",
        ]
    ),
    pad(
        [
            ".....FFF...9....",
            "..FFFFFFF..F....",
            ".YOOORRRRRFF....",
            "YYOOOORRRRRRFF..",
            ".YOOORRRRRFF....",
            "..FFFFFFF..F....",
            ".....FFF........",
        ]
    ),
    pad(
        [
            "......FF...F...9......",
            "...FFFFFFFF..F..9.....",
            ".YOOORRRRRRRFFF.......",
            "YYOOOORRRRRRRRRFFF....",
            "YYYOOOOORRRRRRRRRRFFF.",
            "YYOOOORRRRRRRRRFFF....",
            ".YOOORRRRRRRFFF.......",
            "...FFFFFFFF..F..9.....",
            "......FF...F...9......",
        ]
    ),
]

SMOKE = pad(
    [
        ".S.S.",
        "S.S.S",
        ".S.S.",
        "S.S..",
    ]
)

# Fire that cools into a heart: two bumps and a point, ember/gold/red.
HEART = pad(
    [
        ".RO.OR.",
        "RYRRROR",
        "RRYORRR",
        ".RRORR.",
        "..RRR..",
        "...R...",
    ]
)

CLOSED_EYE = pad(
    [
        "kkk",
    ]
)

CAMPFIRE = pad(
    [
        "...9Y9...",
        "..YOYOY..",
        ".YOROROY.",
        ".ORFFRRO.",
        "..RFkFR..",
        "...kNk...",
        "..N.N.N..",
        ".N.....N.",
    ]
)

ANVIL = pad(
    [
        "..SSSSS..",
        ".NNNNNNN.",
        "NNNNNNNNN",
        "..NNNNN..",
        "...NNN...",
        "...NNN...",
        "..NNNNN..",
        ".NNNNNNN.",
    ]
)

GRASS = pad(
    [
        ".A.A.",
        "A.g.A",
        "g...g",
    ]
)

STAR = pad(
    [
        ".9.",
        "9X9",
        ".9.",
    ]
)

TEACUP = pad(
    [
        "..CCCCC.",
        ".CyyyyCkk",
        ".CyyyyCk.",
        "..CCCCC..",
        "...NNN...",
    ]
)

MARSHMALLOW = pad(
    [
        ".PP.",
        "PzzP",
        "PzzP",
        ".kk.",
        ".kk.",
        ".kk.",
        ".kk.",
    ]
)

LANTERN_CORE = pad(
    [
        "...XXX...",
        "..XyyyX..",
        ".XyyyyyX.",
        ".XyY9YyX.",
        ".XyyyyyX.",
        "..XyyyX..",
        "...XXX...",
        "....X....",
    ]
)

ENVELOPE = pad(
    [
        ".kkkkkkk.",
        "kPPkPPkk",
        "kPPPPkkP",
        "kPPPPPPk",
        ".kkkkkkk.",
    ]
)

WAX_STAMP = pad(
    [
        ".rrrrr.",
        "rrmmmrr",
        "rmmmm mr".replace(" ", "m"),
        "rmmmmmr",
        "rrmmmrr",
        ".rrrrr.",
    ]
)

def sleep_mark(ox: float, oy: float, size: float) -> str:
    """One drifting Z, set in the display serif rather than drawn as blocks."""
    return sprite_text("Z", "wordmark", ox, oy + size * 5, "P", size=size * 7, tracking=0)


def animate_opacity(values: str, dur: str, begin: str = "0s", key_times: str | None = None) -> str:
    kt = f' keyTimes="{key_times}"' if key_times else ""
    return (
        f'<animate attributeName="opacity" values="{values}"{kt} dur="{dur}" '
        f'begin="{begin}" repeatCount="indefinite"/>'
    )


def svg_wrap(
    w: int,
    h: int,
    title: str,
    desc: str,
    body: str,
    extra_defs: str = "",
    extra_css: str = "",
) -> str:
    style = f"  <style>\n{extra_css}\n  </style>\n" if extra_css else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <defs>
    <linearGradient id="duskSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0F1013"/>
      <stop offset=".42" stop-color="#1A1C22"/>
      <stop offset="1" stop-color="#20272A"/>
    </linearGradient>
    <linearGradient id="paperSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1E2026"/>
      <stop offset="1" stop-color="#141519"/>
    </linearGradient>
    <linearGradient id="hillA" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#232B2E"/>
      <stop offset="1" stop-color="#191F22"/>
    </linearGradient>
    <linearGradient id="hillB" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#26332F"/>
      <stop offset="1" stop-color="#1A2421"/>
    </linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2A2D35"/>
      <stop offset="1" stop-color="#1A1C22"/>
    </linearGradient>
    <linearGradient id="brass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8A6E1F"/>
      <stop offset=".55" stop-color="#C9A227"/>
      <stop offset="1" stop-color="#E0B94A"/>
    </linearGradient>
    <radialGradient id="lamp" cx="50%" cy="40%" r="50%">
      <stop offset="0" stop-color="#F2C14E" stop-opacity=".85"/>
      <stop offset=".45" stop-color="#E4572E" stop-opacity=".22"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="hearth" cx="50%" cy="60%" r="50%">
      <stop offset="0" stop-color="#FFE3A3" stop-opacity=".6"/>
      <stop offset=".5" stop-color="#E4572E" stop-opacity=".22"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <filter id="softPaper" x="-4%" y="-4%" width="108%" height="112%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity=".5"/>
    </filter>
    {extra_defs}
  </defs>
{style}{body}
</svg>
'''


def css_name(cls: str) -> str:
    return cls.replace("-", "_")


def css_opacity_windows(name: str, windows: list[tuple[float, float]], peak: float = 1.0) -> str:
    """Discrete opacity holds. GitHub README <img> SVGs play CSS, not SMIL."""
    windows = sorted(windows)
    lines = [f"@keyframes {name}{{"]
    cursor = 0.0
    for start, end in windows:
        if start > cursor:
            hold_end = max(start - 0.05, cursor)
            lines.append(f"{cursor:.2f}%,{hold_end:.2f}%{{opacity:0}}")
        lines.append(f"{start:.2f}%,{max(end - 0.05, start):.2f}%{{opacity:{peak}}}")
        cursor = end
    if cursor < 100.0:
        lines.append(f"{cursor:.2f}%,100%{{opacity:0}}")
    else:
        lines.append("100%{opacity:0}")
    lines.append("}")
    return "".join(lines)


def css_hold_rule(cls: str, dur: str, windows: list[tuple[float, float]], peak: float = 1.0) -> str:
    name = css_name(cls)
    on_at_start = any(a <= 0.0 < b for a, b in windows)
    return (
        f".{cls}{{opacity:{1 if on_at_start else 0};"
        f"animation:{name} {dur} linear infinite}}"
        f"{css_opacity_windows(name, windows, peak)}"
    )


def css_rise_rule(cls: str, dur: str, delay: str, dx: float, dy: float, peak: float = 0.7) -> str:
    name = css_name(cls)
    return (
        f".{cls}{{opacity:0;animation:{name} {dur} linear infinite;animation-delay:{delay}}}"
        f"@keyframes {name}{{"
        f"0%{{opacity:0;transform:translate(0,0)}}"
        f"18%{{opacity:{peak};transform:translate({dx * 0.25:.1f}px,{dy * 0.25:.1f}px)}}"
        f"100%{{opacity:0;transform:translate({dx:.1f}px,{dy:.1f}px)}}"
        f"}}"
    )


HERO_BREATH = 6.0  # seconds. CSS loop: inhale, blast, heart, rest. Overlaps so it never sits still.


BREATH = 5.6  # seconds for one full ember-burst-smoke-spark loop (SMIL cards only)


def timed_opacity(start: float, end: float, peak: float = 1.0, fade: float = 0.09) -> str:
    """Hold at 0, ramp to `peak` at `start`, hold, ramp back down after `end`."""
    stops = [0.0, max(start - fade, 0.0), start, end, min(end + fade, BREATH), BREATH]
    keys = ";".join(f"{s / BREATH:.4f}" for s in stops)
    return (
        f'<animate attributeName="opacity" values="0;0;{peak};{peak};0;0" keyTimes="{keys}" '
        f'dur="{BREATH}s" repeatCount="indefinite"/>'
    )


def gap_opacity(start: float, end: float, peak: float = 1.0, fade: float = 0.09) -> str:
    """The inverse of timed_opacity: visible except for a hole between the two."""
    stops = [0.0, max(start - fade, 0.0), start, end, min(end + fade, BREATH), BREATH]
    keys = ";".join(f"{s / BREATH:.4f}" for s in stops)
    return (
        f'<animate attributeName="opacity" values="{peak};{peak};0;0;{peak};{peak}" '
        f'keyTimes="{keys}" dur="{BREATH}s" repeatCount="indefinite"/>'
    )


# Frame index, on, off. Swells out and settles back so the loop reads as one breath.
BREATH_FRAMES = [
    (1, 0.60, 0.80),
    (2, 0.78, 1.00),
    (3, 0.98, 1.32),
    (4, 1.30, 2.10),
    (3, 2.08, 2.32),
    (2, 2.30, 2.48),
    (1, 2.46, 2.62),
]


def dragon_group(ox: float, oy: float, size: float, fire: bool = True, bob: bool = True) -> str:
    """Assemble the side-on dragon from its three layers so parts can move."""

    def place(sprite: list[str], cell: tuple[float, float]) -> str:
        return rle_rects(sprite, ox + cell[0] * size, oy + cell[1] * size, size)

    def cycle(poses: list[list[str]], cell: tuple[int, int], order: list[int], dur: float) -> str:
        """Flip between redrawn poses. Discrete keyTimes keep every frame crisp;
        rotating the pixels instead would resample them into mush."""
        steps = len(order)
        keys = ";".join(f"{i / steps:.4f}" for i in range(steps + 1))
        parts = []
        for index, pose in enumerate(poses):
            on = [1 if slot == index else 0 for slot in order]
            values = ";".join(str(v) for v in on + [on[0]])
            parts.append(
                f'<g opacity="{on[0]}">\n{place(pose, cell)}\n'
                f'  <animate attributeName="opacity" values="{values}" keyTimes="{keys}" '
                f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>\n</g>'
            )
        return "\n".join(parts)

    tail_layer = cycle(DRAGON_TAIL_POSES, TAIL_AT, [0, 1, 0, 2], 3.6)
    wing_layer = cycle(DRAGON_WING_POSES, WING_AT, [0, 1, 0, 2], 2.4)

    # Blink: drop a lid the exact size of the eye over it.
    eye = find_pixels(DRAGON_BODY, "pe")
    ex0, ex1 = min(x for x, _ in eye), max(x for x, _ in eye)
    ey0, ey1 = min(y for _, y in eye), max(y for _, y in eye)
    span = ex1 - ex0 + 1
    lid = ["b" * span, "k" * span, "b" * span][: max(ey1 - ey0 + 1, 2)]
    blink = place(lid, (BODY_AT[0] + ex0, BODY_AT[1] + ey0))

    # Breath leaves from the front of the mouth, centred on the lip opening.
    mouth = find_pixels(DRAGON_BODY, "M")
    mx = max(x for x, _ in mouth)
    lips = [y for x, y in mouth if x == mx]
    lip_x = BODY_AT[0] + mx + 1
    lip_y = BODY_AT[1] + round(sum(lips) / len(lips))

    layers: list[str] = []
    if fire:
        rest = FIRE_FRAMES[0]
        layers.append(
            f'<ellipse cx="{ox + (lip_x + 12) * size}" cy="{oy + (lip_y + 0.5) * size}" '
            f'rx="{22 * size}" ry="{5 * size}" fill="url(#hearth)" opacity=".4"/>'
        )
        layers.append(
            f'<g>\n'
            f'{place(rest, (lip_x, lip_y - len(rest) // 2))}\n'
            f'{animate_opacity("0.9;1;0.92;1;0.9", "1.1s")}\n</g>'
        )
        for index, on, off in BREATH_FRAMES:
            frame = FIRE_FRAMES[index]
            layers.append(
                f'<g opacity="0">\n{place(frame, (lip_x, lip_y - len(frame) // 2))}\n'
                f'{timed_opacity(on, off, 1.0, 0.05)}\n</g>'
            )
        drift = 6 * size
        layers.append(
            f'<g opacity="0">\n{place(SMOKE, (lip_x + 3, lip_y - 4))}\n'
            f'{timed_opacity(2.6, 3.9, 0.6, 0.35)}\n'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{drift} {-drift * 1.6}" dur="{BREATH}s" repeatCount="indefinite"/>\n</g>'
        )
        layers.append(
            f'<g opacity="0">\n{place(HEART, (lip_x + 6, lip_y - 7))}\n'
            f'{timed_opacity(3.9, 4.8, 1.0, 0.3)}\n'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{size} {-3 * size}" dur="{BREATH}s" repeatCount="indefinite"/>\n</g>'
        )

    bob_open = (
        f'<g>\n  <animateTransform attributeName="transform" type="translate" '
        f'values="0 0; 0 {-size / 2}; 0 0" dur="2.6s" repeatCount="indefinite"/>'
        if bob
        else "<g>"
    )
    return f'''{bob_open}
{tail_layer}
{place(DRAGON_BODY, BODY_AT)}
{wing_layer}
<g opacity="0">
{blink}
{animate_opacity("0;0;1;1;0;0", "4.4s", "0s", "0;0.76;0.78;0.83;0.85;1")}
</g>
{chr(10).join(layers)}
</g>'''


def shut_eyes(ox: float, oy: float, size: float) -> str:
    """Cover each open eye with a lid, so the napping dragon is actually asleep."""
    eyes = find_pixels(DRAGON_SIT, "pe")
    split = (min(x for x, _ in eyes) + max(x for x, _ in eyes)) / 2
    lids = []
    for half in (lambda x: x < split, lambda x: x > split):
        cells = [(x, y) for x, y in eyes if half(x)]
        x0, x1 = min(x for x, _ in cells), max(x for x, _ in cells)
        y0, y1 = min(y for _, y in cells), max(y for _, y in cells)
        rows = ["b" * (x1 - x0 + 1) for _ in range(y1 - y0 + 1)]
        rows[len(rows) // 2] = "k" * (x1 - x0 + 1)
        lids.append(rle_rects(rows, ox + x0 * size, oy + y0 * size, size))
    return "\n".join(lids)


def sitting_dragon(ox: float, oy: float, size: float, napping: bool = False) -> str:
    # Row 0 of DRAGON_SIT is the horn tips, so anything floating above the head
    # is offset from oy in whole cells and stays inside a tight banner.
    body = rle_rects(DRAGON_SIT, ox, oy, size)
    span = len(DRAGON_SIT[0])
    if napping:
        body += "\n" + shut_eyes(ox, oy, size)
        extras = (
            f'<g>\n{sleep_mark(ox + (span - 10) * size, oy - 3 * size, size)}\n'
            f'{animate_opacity("0;1;0", "2.8s")}\n</g>'
            f'<g>\n{sleep_mark(ox + (span - 6) * size, oy - 6 * size, max(size - 1, 2))}\n'
            f'{animate_opacity("0;0;1;0", "2.8s", "0.6s")}\n</g>'
        )
    else:
        extras = (
            f'<g opacity="0">\n{rle_rects(HEART, ox + (span - 6) * size, oy - 4 * size, max(size - 1, 3))}\n'
            f'{animate_opacity("0;1;0", "3.2s")}\n</g>'
        )
    return f'''<g>
  <animateTransform attributeName="transform" type="translate" values="0 0; 0 {-size/3}; 0 0" dur="3s" repeatCount="indefinite"/>
{body}
{extras}
</g>'''


def fox_group(ox: float, oy: float, size: float) -> str:
    return f'''<g>
  <animateTransform attributeName="transform" type="translate" values="0 0; 0 {-size/4}; 0 0" dur="2.8s" begin="0.4s" repeatCount="indefinite"/>
{rle_rects(FOX_SIT, ox, oy, size)}
</g>'''


def meadow_background(w: int, h: int) -> str:
    """Night ridge: graphite sky, cold ridges, a thin band of ground fog."""
    return f'''  <rect width="{w}" height="{h}" fill="url(#duskSky)"/>
  <ellipse cx="{w*0.18}" cy="{h*0.42}" rx="{w*0.18}" ry="{h*0.05}" fill="#2A3138" opacity=".5">
    <animate attributeName="cx" values="{w*0.18};{w*0.22};{w*0.18}" dur="18s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="{w*0.78}" cy="{h*0.36}" rx="{w*0.16}" ry="{h*0.045}" fill="#262B33" opacity=".5">
    <animate attributeName="cx" values="{w*0.78};{w*0.74};{w*0.78}" dur="22s" repeatCount="indefinite"/>
  </ellipse>
  <path d="M0 {h*0.62} C {w*0.18} {h*0.48}, {w*0.34} {h*0.52}, {w*0.5} {h*0.58} C {w*0.7} {h*0.66}, {w*0.86} {h*0.5}, {w} {h*0.56} L{w} {h} L0 {h} Z" fill="url(#hillA)"/>
  <path d="M0 {h*0.74} C {w*0.22} {h*0.66}, {w*0.4} {h*0.7}, {w*0.58} {h*0.7} C {w*0.76} {h*0.7}, {w*0.9} {h*0.64}, {w} {h*0.68} L{w} {h} L0 {h} Z" fill="url(#hillB)"/>
  <rect x="0" y="{h*0.82}" width="{w}" height="{h*0.18}" fill="#1E2624"/>
  <rect x="0" y="{h*0.82}" width="{w}" height="2" fill="#3A3E48" opacity=".6"/>
'''


def fireflies(positions: list[tuple[float, float, str]]) -> str:
    """Drifting embers. Same signature as before, warmer and smaller."""
    bits = []
    for i, (x, y, dur) in enumerate(positions):
        bits.append(
            f'<circle cx="{x}" cy="{y}" r="1.8" fill="#F2C14E" opacity=".2">'
            f'<animate attributeName="opacity" values=".15;.95;.15" dur="{dur}" begin="{i * 0.4}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y};{y-10};{y}" dur="{float(str(dur).rstrip("s"))+1.5:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    return "\n".join(bits)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def build_dragon_camp() -> None:
    w, h = 920, 420
    size = 8
    dragon = dragon_group(210, 118, size, fire=True)
    fox = fox_group(80, 268, 5)
    plants = "\n".join(
        [
            rle_rects(GRASS, x, 340, 5)
            for x in (40, 70, 110, 150, 560, 600, 650, 700, 760, 820)
        ]
    )
    extras = "\n".join(
        [
            rle_rects(ANVIL, 44, 322, 5),
            rle_rects(CAMPFIRE, 620, 292, 6),
            rle_rects(MARSHMALLOW, 598, 268, 5),
            rle_rects(TEACUP, 780, 328, 5),
            rle_rects(STAR, 80, 70, 4),
            rle_rects(STAR, 160, 40, 3),
            rle_rects(STAR, 840, 60, 4),
            rle_rects(STAR, 700, 36, 3),
        ]
    )
    camp_glow = '''<ellipse cx="644" cy="330" rx="60" ry="26" fill="url(#hearth)">
  <animate attributeName="opacity" values=".45;.9;.45" dur="1.4s" repeatCount="indefinite"/>
</ellipse>'''
    frame = f'''<rect x="16" y="16" width="{w-32}" height="{h-32}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".5"/>'''
    caption = f'''<g>
  {ts.outline("A small dragon lives here", "plate", 460, 50, "#E9E6DF", "middle", max_width=760)}
  <rect x="330" y="66" width="260" height="1" fill="#C9A227" opacity=".8"/>
  {ts.outline("Fire is the last stage of review", "eyebrow", 460, 94, "#C6C2B8", "middle")}
</g>'''
    rawr = f'''<g opacity="0">
{sprite_text("Rawr", "label", 560, 146, "9", size=18, tracking=0.14)}
{animate_opacity("0;0;1;1;0;0", "5.5s", "0s", "0;0.48;0.52;0.62;0.68;1")}
</g>'''
    body = f'''{meadow_background(w, h)}
  {camp_glow}
  {plants}
  {extras}
  {fox}
  {dragon}
  {rawr}
  {fireflies([(120, 90, "3.2s"), (260, 60, "4s"), (540, 80, "3.6s"), (800, 100, "4.4s"), (880, 140, "3s")])}
  {caption}
  {frame}
'''
    write(
        OUT / "dragon" / "pixel-dragon.svg",
        svg_wrap(
            w,
            h,
            "Pixel dragon breathing fire",
            "A pixel dragon on a cold night ridge, breathing looping fire beside a fox, an anvil, and a campfire.",
            body,
        ),
    )


def build_tiny_dragon() -> None:
    w, h = 280, 220
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="6" y="6" width="{w-12}" height="{h-12}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".6"/>
{sitting_dragon(65, 28, 5, napping=False)}
{sprite_text("Muxby", "wordmark", 140, 202, "X", anchor="middle", size=17, max_width=190)}
'''
    write(
        OUT / "dragon" / "pixel-dragon-tiny.svg",
        svg_wrap(w, h, "Tiny forge dragon", "A sitting pixel dragon mascot on graphite, framed in brass.", body),
    )


def build_napping() -> None:
    w, h = 900, 120
    body = f'''  <rect width="{w}" height="{h}" fill="#1E2026"/>
  <rect x="0" y="0" width="{w}" height="3" fill="#C9A227"/>
  <rect x="0" y="{h-3}" width="{w}" height="3" fill="#8A6E1F"/>
{sitting_dragon(26, 20, 3, napping=True)}
{fox_group(140, 48, 3)}
  <g>
    {ts.outline("The forge is open. The dragon is on break.", "plate", 248, 56, "#E9E6DF", size=15, max_width=560)}
    <rect x="248" y="68" width="400" height="1" fill="#C9A227" opacity=".7"/>
    {ts.outline("Fire-breathing resumes shortly", "eyebrow", 248, 88, "#C6C2B8")}
  </g>
'''
    write(
        OUT / "atelier" / "napping-banner.svg",
        svg_wrap(w, h, "Dragon break banner", "A slate workshop sign with a napping pixel dragon and a fox.", body),
    )


def four_star(cx: float, cy: float, r: float, fill: str = "#F2C14E", opacity: str = ".85") -> str:
    """A small four-pointed brass spark. Vector, not a pixel letter."""
    inner = r * 0.28
    return (
        f'<path d="M{cx} {cy - r} L{cx + inner} {cy - inner} L{cx + r} {cy} '
        f'L{cx + inner} {cy + inner} L{cx} {cy + r} L{cx - inner} {cy + inner} '
        f'L{cx - r} {cy} L{cx - inner} {cy - inner} Z" fill="{fill}" opacity="{opacity}"/>'
    )


def coal_pit(cx: float, cy: float, w: float, h: float) -> str:
    """Iron ring under the dragon's feet: connected grate, banked coals, contact shadow.

    `w`/`h` are the ring's full width and height (not a giant flattened oval).
    """
    rx, ry = w / 2, h / 2
    parts = [
        f'<ellipse cx="{cx:.1f}" cy="{cy + 8:.1f}" rx="{rx + 10:.1f}" ry="{ry * 0.42:.1f}" fill="#0F1013" opacity=".55"/>',
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#2A2D35"/>',
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#1A1C22" stroke-width="4"/>',
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx - 3:.1f}" ry="{ry - 2:.1f}" fill="none" stroke="#8A6E1F" stroke-width="2.2"/>',
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx - 9:.1f}" ry="{ry - 7:.1f}" fill="#141519"/>',
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx - 14:.1f}" ry="{ry - 11:.1f}" fill="#1A1C22"/>',
    ]
    coals = (
        (cx - rx * 0.38, cy + 2, 22, 9, "#A33418"),
        (cx - rx * 0.08, cy - 3, 26, 10, "#E4572E"),
        (cx + rx * 0.22, cy + 1, 20, 8, "#C0431F"),
        (cx - rx * 0.18, cy + 8, 16, 7, "#F2A03C"),
        (cx + rx * 0.08, cy + 9, 18, 7, "#E4572E"),
        (cx + rx * 0.36, cy + 6, 14, 6, "#A33418"),
        (cx, cy + 4, 20, 8, "#F2C14E"),
    )
    for i, (x, y, crx, cry, fill) in enumerate(coals):
        parts.append(
            f'<ellipse class="coal-{i}" cx="{x:.1f}" cy="{y:.1f}" rx="{crx}" ry="{cry}" fill="{fill}"/>'
        )
    # Horizontal grate bars whose ends meet the inner ring.
    inner_rx, inner_ry = rx - 10, ry - 8
    for yoff in (-9.0, -3.0, 3.0, 9.0):
        t = yoff / inner_ry
        if abs(t) >= 0.98:
            continue
        hw = inner_rx * (1 - t * t) ** 0.5
        parts.append(
            f'<rect x="{cx - hw:.1f}" y="{cy + yoff:.1f}" width="{2 * hw:.1f}" height="2.4" '
            f'fill="#8A6E1F" opacity=".82"/>'
        )
    # Short stone lip at the front of the ring so it reads as a platform, not a pancake.
    parts.append(
        f'<path d="M{cx - rx + 8:.1f} {cy + ry - 4:.1f} '
        f'Q{cx:.1f} {cy + ry + 6:.1f} {cx + rx - 8:.1f} {cy + ry - 4:.1f}" '
        f'fill="none" stroke="#3A3E48" stroke-width="3"/>'
    )
    return "".join(parts)


def blood_moon(cx: float, cy: float, r: float = 28) -> str:
    """Deep crimson disc with a gold rim and a few craters. Not neon."""
    return f'''<g class="moon">
  <circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="url(#moonHalo)"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#A33418"/>
  <circle cx="{cx}" cy="{cy}" r="{r - 1.5}" fill="#E4572E"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#C9A227" stroke-width="1.3" opacity=".5"/>
  <circle cx="{cx + 9}" cy="{cy - 5}" r="{r - 7}" fill="#7E2A12" opacity=".5"/>
  <circle cx="{cx - 9}" cy="{cy + 7}" r="4.2" fill="#7E2A12" opacity=".75"/>
  <circle cx="{cx + 5}" cy="{cy + 11}" r="3" fill="#A33418" opacity=".85"/>
  <circle cx="{cx - 3}" cy="{cy - 11}" r="2.4" fill="#7E2A12" opacity=".7"/>
  <circle cx="{cx + 11}" cy="{cy + 2}" r="2" fill="#F2A03C" opacity=".35"/>
</g>'''


def css_puff_stack(
    prefix: str,
    origin: tuple[float, float],
    count: int,
    sprite: list[str],
    size: float,
    dur: str,
    dx: float,
    dy: float,
    stagger: float,
    peak: float = 0.65,
) -> tuple[str, str]:
    """Looping pixel puffs that rise and fade. CSS transform, not SMIL."""
    rules: list[str] = []
    groups: list[str] = []
    ox, oy = origin
    for i in range(count):
        cls = f"{prefix}-{i}"
        delay = f"{i * stagger:.2f}s"
        rules.append(css_rise_rule(cls, dur, delay, dx + i * 3, dy - i * 4, peak))
        groups.append(
            f'<g class="{cls}">\n{rle_rects(sprite, ox - size + i * 5, oy, size)}\n</g>'
        )
    return "\n".join(rules), "\n".join(groups)


def hero_breath(ox: float, oy: float, size: float) -> tuple[str, str]:
    """CSS breath cycle for the forge-yard hero. GitHub will not play SMIL.

    ~6s loop, overlapping: nose smoke always, fire 15–66%, heart 40–70%.
    No always-on rest jet.
    """
    dur = f"{HERO_BREATH}s"

    def cell(c: tuple[float, float]) -> tuple[float, float]:
        return ox + c[0] * size, oy + c[1] * size

    mouth = find_pixels(DRAGON_BODY, "M")
    mx = max(x for x, _ in mouth)
    lips = [y for x, y in mouth if x == mx]
    lip_x = BODY_AT[0] + mx + 1
    lip_y = BODY_AT[1] + round(sum(lips) / len(lips))

    nose = find_pixels(DRAGON_BODY, "n")
    nx = BODY_AT[0] + sum(x for x, _ in nose) / len(nose)
    ny = BODY_AT[1] + min(y for _, y in nose) - 1

    rules: list[str] = []
    groups: list[str] = []

    # Frame 0 is the old always-on rest spark — skip it. Swell 1→4, then settle.
    fire_windows = {
        1: [(15.0, 24.0), (60.0, 66.0)],
        2: [(22.0, 32.0), (56.0, 62.0)],
        3: [(30.0, 42.0), (50.0, 58.0)],
        4: [(38.0, 52.0)],
    }
    for index, windows in fire_windows.items():
        cls = f"hf-{index}"
        rules.append(css_hold_rule(cls, dur, windows))
        frame = FIRE_FRAMES[index]
        fx, fy = cell((lip_x, lip_y - len(frame) // 2))
        groups.append(f'<g class="{cls}">\n{rle_rects(frame, fx, fy, size)}\n</g>')

    glow_cls = "hf-glow"
    rules.append(css_hold_rule(glow_cls, dur, [(18.0, 52.0)], peak=0.9))
    gx, gy = cell((lip_x + 8, lip_y + 0.4))
    groups.append(
        f'<ellipse class="{glow_cls}" cx="{gx:.1f}" cy="{gy:.1f}" '
        f'rx="{12 * size}" ry="{6.5 * size}" fill="url(#hearth)"/>'
    )

    heart_cls = "hf-heart"
    hdx, hdy = 36.0, -42.0
    rules.append(
        f".{heart_cls}{{opacity:0;animation:{css_name(heart_cls)} {dur} linear infinite}}"
        f"@keyframes {css_name(heart_cls)}{{"
        f"0%,39.5%{{opacity:0;transform:translate(0,0)}}"
        f"44%{{opacity:1;transform:translate({hdx * 0.12:.1f}px,{hdy * 0.12:.1f}px)}}"
        f"58%{{opacity:1;transform:translate({hdx * 0.62:.1f}px,{hdy * 0.62:.1f}px)}}"
        f"70%,100%{{opacity:0;transform:translate({hdx:.1f}px,{hdy:.1f}px)}}"
        f"}}"
    )
    biggest = FIRE_FRAMES[4]
    hx, hy = cell((lip_x + len(biggest[0]) - 4, lip_y - 6))
    groups.append(f'<g class="{heart_cls}">\n{rle_rects(HEART, hx, hy, size)}\n</g>')

    nose_sprite = pad([".S.", "S.S", ".S."])
    nx_px, ny_px = cell((nx, ny))
    nose_css, nose_svg = css_puff_stack(
        "hnose", (nx_px, ny_px - 2 * size), 3, nose_sprite, max(size - 2, 3), "2.6s", 6, -28, 0.85, 0.6
    )
    rules.append(nose_css)
    groups.append(nose_svg)

    return "\n".join(rules), "\n".join(groups)


def vector_lantern(cx: float, cy: float) -> str:
    """Brass lantern that still reads when the pixel core is small."""
    return f'''<g>
  <ellipse cx="{cx}" cy="{cy + 8}" rx="46" ry="54" fill="url(#lamp)">
    <animate attributeName="opacity" values=".4;.95;.4" dur="3.2s" repeatCount="indefinite"/>
  </ellipse>
  <path d="M{cx} {cy - 52} V{cy - 38}" stroke="#8A6E1F" stroke-width="3"/>
  <rect x="{cx - 16}" y="{cy - 38}" width="32" height="8" fill="#C9A227"/>
  <rect x="{cx - 18}" y="{cy - 30}" width="36" height="52" fill="#2A2D35"/>
  <rect x="{cx - 14}" y="{cy - 26}" width="28" height="44" fill="#1A1C22"/>
  <rect x="{cx - 10}" y="{cy - 18}" width="20" height="28" fill="#F2C14E" opacity=".85">
    <animate attributeName="opacity" values=".55;1;.55" dur="1.8s" repeatCount="indefinite"/>
  </rect>
  <rect x="{cx - 18}" y="{cy + 22}" width="36" height="6" fill="#C9A227"/>
  <rect x="{cx - 4}" y="{cy + 28}" width="8" height="10" fill="#8A6E1F"/>
</g>'''


def build_hero() -> None:
    """Night forge yard. Type sits in the sky, the dragon holds the middle,
    the floor is a hearth. Motion on GitHub is CSS, never SMIL."""
    w, h = 1200, 480
    size = 7
    ox = 330
    oy = 150
    stars = "\n".join(
        [
            four_star(300, 26, 7),
            four_star(900, 32, 5, opacity=".7"),
            four_star(220, 70, 4, opacity=".55"),
            four_star(980, 74, 4, opacity=".5"),
            four_star(600, 20, 3, opacity=".45"),
            four_star(1088, 50, 3, "#C9A227", ".4"),
            four_star(140, 48, 3, "#C9A227", ".4"),
            four_star(470, 96, 3, opacity=".35"),
            four_star(740, 88, 3, opacity=".35"),
        ]
    )
    breath_css, breath_svg = hero_breath(ox, oy, size)
    chimney_css, chimney_svg = css_puff_stack(
        "hchimney",
        (1074, 102),
        4,
        SMOKE,
        3.5,
        "3.2s",
        8,
        -46,
        0.72,
        0.55,
    )
    coal_css = "\n".join(
        (
            f".coal-{i}{{opacity:.7;animation:coal_{i} {2.4 + i * 0.3}s ease-in-out infinite}}"
            f"@keyframes coal_{i}{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}"
        )
        for i in range(7)
    )
    extra_css = "\n".join(
        [
            breath_css,
            chimney_css,
            coal_css,
            ".moon{animation:moonPulse 7.5s ease-in-out infinite}",
            "@keyframes moonPulse{0%,100%{opacity:.88}50%{opacity:1}}",
            ".grate-glow{animation:gratePulse 2.6s ease-in-out infinite}",
            "@keyframes gratePulse{0%,100%{opacity:.4}50%{opacity:.75}}",
        ]
    )
    extra_defs = '''
    <linearGradient id="forgeFloor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2A2D35"/>
      <stop offset="1" stop-color="#141519"/>
    </linearGradient>
    <linearGradient id="ridgeFar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3A4A46"/>
      <stop offset="1" stop-color="#232B2E"/>
    </linearGradient>
    <linearGradient id="ridgeMid" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3F6B62"/>
      <stop offset="1" stop-color="#243832"/>
    </linearGradient>
    <radialGradient id="grateGlow" cx="50%" cy="40%" r="55%">
      <stop offset="0" stop-color="#E4572E" stop-opacity=".55"/>
      <stop offset=".5" stop-color="#A33418" stop-opacity=".18"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="moonHalo" cx="50%" cy="45%" r="50%">
      <stop offset="0" stop-color="#E4572E" stop-opacity=".28"/>
      <stop offset=".55" stop-color="#A33418" stop-opacity=".1"/>
      <stop offset="1" stop-color="#7E2A12" stop-opacity="0"/>
    </radialGradient>
'''
    # Feet land ~x 400–547, y ~381. Ring sits under that stance, not a yard-wide pancake.
    hearth_cx, hearth_cy = 478.0, 402.0
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect width="{w}" height="{h}" fill="url(#duskSky)"/>
  <rect x="0" y="0" width="{w}" height="10" fill="#2A2D35"/>
  <rect x="0" y="10" width="{w}" height="1" fill="#8A6E1F" opacity=".7"/>
  <rect x="0" y="0" width="2" height="{h}" fill="#C9A227"/>
  {blood_moon(168, 64, 26)}
  <!-- framing peaks so the name sits in a valley, not a void -->
  <path d="M0 168 C 70 78, 170 70, 270 128 C 330 162, 380 198, 430 210 C 500 128, 620 118, 760 150 C 880 90, 1020 70, 1200 128 L1200 {h} L0 {h} Z" fill="url(#ridgeFar)"/>
  <path d="M0 168 C 70 78, 170 70, 270 128 C 330 162, 380 198, 430 210 C 500 128, 620 118, 760 150 C 880 90, 1020 70, 1200 128" fill="none" stroke="#6E9C90" stroke-width="1.4" opacity=".55"/>
  <path d="M0 268 C 140 222, 280 248, 430 236 C 580 222, 740 258, 900 230 C 1040 212, 1140 228, 1200 224 L1200 {h} L0 {h} Z" fill="url(#ridgeMid)"/>
  <!-- forge shed on the right ridge -->
  <rect x="1008" y="156" width="92" height="52" fill="#1B1D22"/>
  <path d="M998 156 L1054 128 L1110 156 Z" fill="#2A2D35"/>
  <rect x="1072" y="114" width="16" height="46" fill="#1B1D22"/>
  <rect x="1068" y="110" width="24" height="6" fill="#3A3E48"/>
  <rect x="1076" y="118" width="8" height="6" fill="#E4572E">
    <animate attributeName="opacity" values=".4;1;.4" dur="1.8s" repeatCount="indefinite"/>
  </rect>
{chimney_svg}
  <!-- near bank into the hearth -->
  <path d="M0 348 C 200 322, 400 338, 600 328 C 820 316, 1020 340, 1200 330 L1200 {h} L0 {h} Z" fill="#1A2421"/>
  <rect x="0" y="392" width="{w}" height="88" fill="url(#forgeFloor)"/>
  <ellipse class="grate-glow" cx="{hearth_cx}" cy="{hearth_cy}" rx="132" ry="48" fill="url(#grateGlow)"/>
  {coal_pit(hearth_cx, hearth_cy, 210, 58)}
  <rect x="0" y="{h - 3}" width="{w}" height="3" fill="#C9A227"/>
  {vector_lantern(1048, 300)}
{rle_rects(ANVIL, 56, 356, 7)}
{sitting_dragon(96, 368, 3, napping=False)}
{dragon_group(ox, oy, size, fire=False, bob=True)}
{breath_svg}
{fireflies([(280, 384, "3.1s"), (500, 372, "3.8s"), (680, 360, "3.3s"), (860, 378, "4.2s"), (360, 110, "4.6s"), (840, 92, "3.9s"), (180, 200, "5.1s")])}
  {stars}
  <g>
    {ts.outline("Mubeen", "hero", 600, 72, "#E9E6DF", "middle")}
    <rect x="454" y="88" width="292" height="1" fill="#C9A227"/>
    {ts.outline("Software, systems, and a small fire-breathing dragon", "eyebrow", 600, 116, "#C6C2B8", "middle", size=11, tracking=0.16)}
  </g>
'''
    art = svg_wrap(
        w,
        h,
        "Muxby forge yard",
        "A night forge yard under a blood moon: a pixel dragon breathes fire that turns into a heart, smoke lifts from the chimney, and banked coals sit in an iron grate.",
        body,
        extra_defs=extra_defs,
        extra_css=extra_css,
    )
    write(OUT / "atelier" / "hero-blood-moon.svg", art)


def build_tool_rack() -> None:
    """Tags hanging from a brass rail. Every tag is the same size on purpose:
    this is a rack of tools, not a chart of scores."""
    w, h = 920, 440
    labels = ["PYTHON", "TS", "REACT", "C++", "POSTGRES", "DOCKER", "TORCH"]
    tag_w, tag_h, step, first_x = 96, 92, 117, 62
    tags = []
    for i, label in enumerate(labels):
        x = first_x + i * step
        cx = x + tag_w / 2
        tags.append(
            f'''<g>
  <animateTransform attributeName="transform" type="rotate" values="0 {cx} 150; 1.1 {cx} 150; -1.1 {cx} 150; 0 {cx} 150" dur="{6 + i * 0.4}s" repeatCount="indefinite"/>
  <path d="M{cx} 150 V186" stroke="#8A6E1F" stroke-width="2"/>
  <rect x="{x}" y="186" width="{tag_w}" height="{tag_h}" fill="#E9E6DF"/>
  <rect x="{x}" y="186" width="{tag_w}" height="4" fill="#C9A227"/>
  <circle cx="{cx}" cy="200" r="3" fill="#2A2D35"/>
  {sprite_text(label, "tag", cx, 240, "p", anchor="middle", max_width=tag_w - 26)}
  <path d="M{x + 18} 258 H{x + tag_w - 18}" stroke="#4E535D" stroke-width="1"/>
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="20" y="18" width="{w-40}" height="{h-36}" fill="#1E2026"/>
  <rect x="20" y="18" width="{w-40}" height="{h-36}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  {ts.outline("The tool rack", "plate", 460, 62, "#E9E6DF", "middle")}
  <path d="M340 78 H580" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  {ts.outline("Hung where I can reach them", "eyebrow", 460, 102, "#9AA0AC", "middle")}
  <rect x="48" y="146" width="824" height="5" fill="url(#brass)"/>
  <rect x="44" y="140" width="10" height="17" fill="#8A6E1F"/>
  <rect x="866" y="140" width="10" height="17" fill="#8A6E1F"/>
  {"".join(tags)}
  <rect x="20" y="356" width="{w-40}" height="66" fill="#2A2D35"/>
  <rect x="20" y="356" width="{w-40}" height="2" fill="#8A6E1F"/>
{sitting_dragon(48, 280, 3)}
{rle_rects(ANVIL, 816, 316, 5)}
  {ts.outline("Same size tags. No scores.", "label", 460, 398, "#C9A227", "middle")}
'''
    write(
        OUT / "atelier" / "garden.svg",
        svg_wrap(
            w,
            h,
            "Tool rack",
            "Equal-sized bone tags for languages and tools hanging from a brass rail, with a sitting dragon and an anvil on the bench.",
            body,
        ),
    )


def build_kettle() -> None:
    import build_hearth

    build_hearth.build_kettle()


def build_lantern() -> None:
    import build_hearth

    build_hearth.build_lantern()


def build_mail() -> None:
    # Walk cycle lives in dragon_post.py so the pose tables stay next to the card.
    import dragon_post

    dragon_post.build()


def build_ember_dish() -> None:
    import build_hearth

    build_hearth.build_coals()


def build_dividers() -> None:
    """Two rules only: a brass hairline and an ember line. No vines, no paws."""
    rule = '''  <rect width="1200" height="40" fill="none"/>
  <path d="M40 20 H560" stroke="#8A6E1F" stroke-width="1">
    <animate attributeName="stroke-dasharray" values="0 520;520 0" dur="1.6s" fill="freeze"/>
  </path>
  <path d="M640 20 H1160" stroke="#8A6E1F" stroke-width="1">
    <animate attributeName="stroke-dasharray" values="0 520;520 0" dur="1.6s" fill="freeze"/>
  </path>
  <path d="M600 10 L610 20 L600 30 L590 20 Z" fill="#C9A227"/>
  <path d="M566 20 H580" stroke="#C9A227" stroke-width="2"/>
  <path d="M620 20 H634" stroke="#C9A227" stroke-width="2"/>
  <circle cx="40" cy="20" r="2" fill="#8A6E1F"/>
  <circle cx="1160" cy="20" r="2" fill="#8A6E1F"/>
'''
    art_rule = svg_wrap(
        1200,
        40,
        "Brass rule",
        "A thin brass rule with a diamond at the centre.",
        rule,
    )
    write(OUT / "atelier" / "divider-rule.svg", art_rule)
    write(OUT / "atelier" / "divider-vine.svg", art_rule)

    sparks = fireflies([(x, 20, f"{3 + (i % 5) * 0.3}s") for i, x in enumerate(range(70, 1150, 72))])
    ember = f'''  <rect width="1200" height="40" fill="none"/>
  <path d="M40 20 H1160" stroke="#3A3E48" stroke-width="1" opacity=".9"/>
  <path d="M520 20 H680" stroke="#E4572E" stroke-width="2">
    <animate attributeName="opacity" values=".5;1;.5" dur="2.6s" repeatCount="indefinite"/>
  </path>
{sparks}
'''
    art_ember = svg_wrap(
        1200,
        40,
        "Ember rule",
        "A steel rule with an ember centre and sparks lifting off it.",
        ember,
    )
    write(OUT / "atelier" / "divider-ember.svg", art_ember)
    write(OUT / "atelier" / "divider-fireflies.svg", art_ember)
    write(OUT / "atelier" / "divider-paws.svg", art_rule)


def build_postcard() -> None:
    w, h = 640, 360
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="16" y="16" width="608" height="328" fill="#1E2026"/>
  <rect x="16" y="16" width="608" height="328" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <rect x="16" y="16" width="608" height="4" fill="#C9A227"/>
  <path d="M330 40 V320" stroke="#3A3E48" stroke-width="1" stroke-dasharray="3 7"/>
  {ts.outline("From the forge", "plate", 174, 70, "#E9E6DF", "middle", size=17)}
  <path d="M64 86 H284" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  <text x="44" y="122" {ts.text_attrs("body")} fill="#C6C2B8">
    <tspan x="44" dy="0">Sharp tools, one warm light, and one</tspan>
    <tspan x="44" dy="24">creature allowed to scorch the drafts.</tspan>
    <tspan x="44" dy="30">Pakistan. Still shipping.</tspan>
  </text>
{sitting_dragon(64, 240, 3)}
{rle_rects(WAX_STAMP, 400, 52, 8)}
  {ts.outline("M", "wordmark", 428, 84, "#F7F5F0", "middle", size=22, tracking=0)}
  <rect x="380" y="160" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="184" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="208" width="160" height="5" fill="#3A3E48"/>
  {ts.outline("Muxby / The forge", "label", 486, 252, "#C9A227", "middle")}
  {ts.outline("Stamp of a finished thought", "label", 486, 308, "#E4572E", "middle", size=10, tracking=0.14)}
'''
    write(
        OUT / "atelier" / "postcard.svg",
        svg_wrap(w, h, "Calling card from the forge", "A slate calling card with an ember seal and a sitting dragon.", body),
    )


def build_quote() -> None:
    w, h = 720, 160
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="16" y="14" width="{w-32}" height="{h-28}" fill="#1E2026"/>
  <rect x="16" y="14" width="{w-32}" height="{h-28}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <rect x="16" y="14" width="5" height="{h-28}" fill="#E4572E"/>
  {ts.outline('"', "heading", 46, 126, "#C9A227", size=88, opacity=".5")}
  {ts.outline("Build something this week that a future teammate", "heading", 376, 76, "#E9E6DF", "middle", max_width=540)}
  {ts.outline("will be glad still exists.", "heading", 376, 104, "#E9E6DF", "middle", max_width=540)}
  <path d="M300 122 H452" stroke="#C9A227" stroke-width="1" opacity=".6"/>
'''
    write(
        OUT / "atelier" / "quote.svg",
        svg_wrap(w, h, "Working principle", "A slate card with a brass rule and a working principle in bone text.", body),
    )


# Filenames from older versions of this profile. They are kept as copies of the
# current artwork so stale external links cannot resurrect a dead theme.
LEGACY_MIRRORS = {
    "constellation.svg": "atelier/corkboard.svg",
    "odyssey.svg": "atelier/trail-cottage.svg",
    "hologram.svg": "atelier/desk.svg",
    "radar-chart.svg": "atelier/desk.svg",
    "signature.svg": "atelier/signature.svg",
    "sigil.svg": "atelier/wax-seal.svg",
    "hero-banner.svg": "atelier/hero-blood-moon.svg",
    "hero-editorial.svg": "atelier/hero-blood-moon.svg",
    "atelier/hero.svg": "atelier/hero-blood-moon.svg",
    "atelier/hero-hearth.svg": "atelier/hero-blood-moon.svg",
    "aurora-header.svg": "atelier/quote.svg",
    "glitch-restricted.svg": "atelier/napping-banner.svg",
    "graph-bars.svg": "atelier/garden.svg",
    "graph-donut.svg": "atelier/ember.svg",
    "graph-gauges.svg": "atelier/mail.svg",
    "graph-growth.svg": "atelier/kettle.svg",
    "graph-oscilloscope.svg": "atelier/lantern.svg",
    "graph-polar-clock.svg": "atelier/postcard.svg",
    "divider-beam.svg": "atelier/divider-rule.svg",
    "divider-circuit.svg": "atelier/divider-rule.svg",
    "divider-starfield.svg": "atelier/divider-ember.svg",
    "divider-wave.svg": "atelier/divider-ember.svg",
    "dragon/divider-ember.svg": "atelier/divider-ember.svg",
}


def mirror_legacy() -> None:
    for legacy, current in LEGACY_MIRRORS.items():
        source = OUT / current
        if not source.exists():
            print(f"skipped {legacy}: {current} missing")
            continue
        write(OUT / legacy, source.read_text(encoding="utf-8"))


def main() -> None:
    import build_avatar

    build_dragon_camp()
    build_tiny_dragon()
    build_napping()
    build_hero()
    build_avatar.build()
    import build_roadmap

    build_roadmap.build()
    build_tool_rack()
    import build_hearth

    build_hearth.build()
    build_mail()
    build_dividers()
    build_postcard()
    build_quote()
    mirror_legacy()


if __name__ == "__main__":
    main()
