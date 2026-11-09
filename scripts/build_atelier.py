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
        ".kBbbbbbbbCCCCCCCCCbk.........",
        ".kbbbbbbbCCCCCCCCCCbbk........",
        "kkbbbbbbbcccccccccckbbk.......",
        "kBbbbbBBkCCCCCCCCCCkbbbk......",
        "kbbbBBbbbkCCCCCCCCCkkbbbbk....",
        "kbbBbbdbbbkCCCCCCCCk.kHkHk....",
        "kbbBbbbbbbkcccccccck..k.k.....",
        "kbbbbdbbdbkCCCCCCCk...........",
        "kdbbbbbbbdkCCCCCCk............",
        ".kdbbbbbddkkcccckk............",
        ".kkddddddkkbbbbbbbbbBk........",
        "kHdbbbbbbbbbHkbbHkbbbHk.......",
        "kkkkkkkkkkkkkkkkkkkkkkk.......",
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

def mirror(half: list[str]) -> list[str]:
    """Symmetric sprite from its left half, so faces stay even."""
    return [row + row[::-1] for row in half]


# Front-on sitting fox: tall ears, bone cheeks and bib, a black nose, and a
# white-tipped brush curled up behind the right hip.
_FOX_FRONT = mirror(
    [
        "..kk....",
        "..kuk...",
        "..kuokkk",
        ".koooooo",
        ".koopeoo",
        "kqoooooo",
        "kqqqoooo",
        ".kqqqqqp",
        "..kqqqqq",
        "...kkqqq",
        "...kooqq",
        "..kooqqq",
        "..koooqq",
        ".kooooqq",
        ".koooukq",
        ".kqqqkqq",
        "..kkkkkk",
    ]
)
_FOX_BRUSH = [
    "......kk.",
    ".....kqqk",
    "....kqqqk",
    "...kooouk",
    "..kooouk.",
    ".kooouk..",
    "kooouk...",
    "kouuk....",
    "kkkk.....",
]
FOX_SIT = stack([(_FOX_BRUSH, 11, 8), (_FOX_FRONT, 0, 0)], 20, 17)

# A dragon's hoard: a heaped mound of brass coin, a patina gem, and a ruby.
HOARD = pad(
    [
        "........9.............",
        ".......CXC......A.....",
        ".....CCXCXC....AGa....",
        "....CXcXCXcXC..Gga.R..",
        "...CXCcXCXCXcXC.g.RRm.",
        "..CXcCXcXCXcXCXCXCXmm.",
        ".CXCXcXCXCcXCXcXCXCXC.",
        "cXcXcXcXcXcXcXcXcXcXcX",
    ]
)

# A blade left standing in a stone, brass hilt up. Forge yard, not a legend.
SWORD_STONE = pad(
    [
        ".....X.....",
        "....XCX....",
        ".....X.....",
        ".....N.....",
        ".....N.....",
        "..XXXCXXX..",
        "...kPzk....",
        "...kPzk....",
        "...kPzk....",
        "..khhShk...",
        ".kShSSSShk.",
        "kSSSShSSSSk",
        "kNSSSSSNSSk",
        "kkkkkkkkkkk",
    ]
)

# Iron-grey canvas tent with a brass ridge pole and a lamp lit inside.
TENT = pad(
    [
        "......k......",
        ".....kXk.....",
        "....kNXNk....",
        "...kNNXNNk...",
        "..kNNkXkNNk..",
        ".kNNk6X6kNNk.",
        "kNNk66X66kNNk",
        "kkkkkkkkkkkkk",
    ]
)

# Campfire flicker: same logs, the flame redrawn leaning the other way.
CAMPFIRE_FLICKER = pad(
    [
        "..9Y..9..",
        "..YOYOY..",
        ".YOROROY.",
        ".ORFFRRO.",
        "..RFkFR..",
        "...kNk...",
        "..N.N.N..",
        ".N.....N.",
    ]
)

# Toasted marshmallow, the same shape as MARSHMALLOW once the breath has had it.
MARSHMALLOW_GOLD = pad([".OO.", "OCCO", "OCCO"])
MARSHMALLOW_DONE = pad([".nn.", "nrrn", "nOrn"])

# Breath, not a campfire: a jet that leaves the mouth sideways and widens as it
# goes. White-hot at the lips (y, Y), cooling outward through O and R to the F
# fringe, with 9 for loose sparks. Tongues lean upward because heat rises.
# Index 0 is a full jet, kept so static renderers (no CSS) still show breath.
# 1-3 swell, 4/5 are two full-blast shapes swapped fast so the flame flickers
# instead of sitting still, and 6 is the jet tearing off into loose puffs.
FIRE_FULL_A = pad(
    [
        "...................F....9.....",
        "..............F..FRRF.F.......",
        "........FF..FRRFRRORRFRF..9...",
        ".....FFRRRFRROOOOOOORRRFF.....",
        "..RRROOOOOOOOYYYYOOOOORRRF.F..",
        "yyYYYYOYYYYYYYOYYYOOOOORRRFF..",
        "..RRROOOOOOOOYYYYOOOOORRRF....",
        ".....FFRRROOROOOOOORRRFF......",
        "........FF..FRRFRORRFF..F.....",
        "..............FF..FRF.........",
        "....................F...9.....",
    ]
)
FIRE_FULL_B = pad(
    [
        ".................F......9.....",
        "............F..FRF..FF........",
        ".......FF.FRRFRRORRRRF.F......",
        "....FFRRRRROOOOOOORRRRRF..9...",
        "..RROOOOOOOOYYYYYOOOOORRRFF...",
        "yyYYYYYOYYYYYYYOYYYOOOOORRRF.F",
        "..RROOOOOOOOYYYYYOOOOORRRFF...",
        "....FFRRRROOOROOOOORRRRF......",
        ".......FF.FRRFRRORRFF.F.......",
        "............F..FRF..F...9.....",
        "..................F...........",
    ]
)
FIRE_FRAMES = [
    FIRE_FULL_A,
    pad(
        [
            ".FF..",
            "YOORF",
            "yYORF",
            "YOORF",
            ".FF..",
        ]
    ),
    pad(
        [
            "....F..9.",
            "..FRRFF..",
            ".YOOORRF.",
            "yYYYOORRF",
            ".YOOORRF.",
            "..FRRFF..",
            "....F....",
        ]
    ),
    pad(
        [
            "..........F...9",
            "......FFRRF.F..",
            "...FRRROORRFF..",
            ".RROOOYYOOORRF.",
            "yYYYYYYYOOORRRF",
            ".RROOOYYOOORRF.",
            "...FRRROORRFF..",
            "......FFRRF....",
            "..........F....",
        ]
    ),
    FIRE_FULL_A,
    FIRE_FULL_B,
    pad(
        [
            "..............S..9...",
            "...........FRRF......",
            "........FRROORRF...S.",
            "..F.F..FRROOOORRF....",
            "........FRROORRF.....",
            "...........FRRF......",
            "..............S......",
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


HERO_BREATH = 6.0  # seconds. CSS loop: glow, swell, flicker, tear off, smoke, heart, rest.


def css_pose_cycle(cls: str, order: list[int], pose_index: int, dur: float) -> str:
    """Hard-cut pose swap. step-end holds each keyframe until the next one, so
    exactly one pose is ever showing and no frame is a half-faded blend."""
    steps = len(order)
    name = css_name(cls)
    first = 1 if order[0] == pose_index else 0
    frames = [f"{100 * i / steps:.2f}%{{opacity:{1 if slot == pose_index else 0}}}" for i, slot in enumerate(order)]
    frames.append(f"100%{{opacity:{first}}}")
    return (
        f".{cls}{{opacity:{first};animation:{name} {dur}s step-end infinite}}"
        f"@keyframes {name}{{{''.join(frames)}}}"
    )


def css_fly_rule(cls: str, dur: str, start: float, end: float, dx: float, dy: float, peak: float = 1.0) -> str:
    """Hidden until `start`%, then travels (dx, dy) and fades out by `end`%."""
    name = css_name(cls)
    mid = start + (end - start) * 0.3
    return (
        f".{cls}{{opacity:0;animation:{name} {dur} linear infinite}}"
        f"@keyframes {name}{{"
        f"0%,{max(start - 0.1, 0):.2f}%{{opacity:0;transform:translate(0,0)}}"
        f"{start:.2f}%{{opacity:{peak};transform:translate(0,0)}}"
        f"{mid:.2f}%{{opacity:{peak};transform:translate({dx * 0.35:.1f}px,{dy * 0.35:.1f}px)}}"
        f"{end:.2f}%,100%{{opacity:0;transform:translate({dx:.1f}px,{dy:.1f}px)}}"
        f"}}"
    )


def mouth_cell() -> tuple[int, int]:
    """Where breath leaves: just past the lip opening, in scene cells."""
    mouth = find_pixels(DRAGON_BODY, "M")
    mx = max(x for x, _ in mouth)
    lips = [y for x, y in mouth if x == mx]
    return BODY_AT[0] + mx + 1, BODY_AT[1] + round(sum(lips) / len(lips))


def dragon_group(ox: float, oy: float, size: float, prefix: str = "dg") -> tuple[str, str]:
    """Assemble the side-on dragon from its three layers so parts can move.

    Returns (css, svg). All motion is CSS, the one animation system every
    scene here uses. The dragon does not bob: it stands on its feet, so the
    feet stay planted and the life comes from the wing, tail, and blink.
    """

    def place(sprite: list[str], cell: tuple[float, float]) -> str:
        return rle_rects(sprite, ox + cell[0] * size, oy + cell[1] * size, size)

    rules: list[str] = []

    def cycle(part: str, poses: list[list[str]], cell: tuple[int, int], order: list[int], dur: float) -> str:
        out = []
        for index, pose in enumerate(poses):
            cls = f"{prefix}-{part}{index}"
            rules.append(css_pose_cycle(cls, order, index, dur))
            out.append(f'<g class="{cls}">\n{place(pose, cell)}\n</g>')
        return "\n".join(out)

    tail_layer = cycle("tail", DRAGON_TAIL_POSES, TAIL_AT, [0, 1, 0, 2], 3.6)
    wing_layer = cycle("wing", DRAGON_WING_POSES, WING_AT, [0, 1, 0, 2], 2.4)

    # Blink: drop a lid the exact size of the eye over it.
    eye = find_pixels(DRAGON_BODY, "pe")
    ex0, ex1 = min(x for x, _ in eye), max(x for x, _ in eye)
    ey0, ey1 = min(y for _, y in eye), max(y for _, y in eye)
    span = ex1 - ex0 + 1
    lid = ["b" * span, "k" * span, "b" * span][: max(ey1 - ey0 + 1, 2)]
    blink_cls = f"{prefix}-blink"
    rules.append(css_hold_rule(blink_cls, "4.4s", [(76.0, 83.0)]))
    blink = f'<g class="{blink_cls}">\n{place(lid, (BODY_AT[0] + ex0, BODY_AT[1] + ey0))}\n</g>'

    svg = f"""<g>
{tail_layer}
{place(DRAGON_BODY, BODY_AT)}
{wing_layer}
{blink}
</g>"""
    return "\n".join(rules), svg


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
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def twinkle_stars(specs: list[tuple[float, float, float, str]], prefix: str = "tw") -> tuple[str, str]:
    """Brass four-point stars that breathe in and out on their own clocks."""
    rules, marks = [], []
    for i, (x, y, r, dur) in enumerate(specs):
        cls = f"{prefix}{i}"
        rules.append(
            f".{cls}{{animation:{cls} {dur} ease-in-out infinite;animation-delay:{-i * 0.7:.1f}s}}"
            f"@keyframes {cls}{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}"
        )
        marks.append(f'<g class="{cls}">{four_star(x, y, r)}</g>')
    return "\n".join(rules), "\n".join(marks)


def shooting_star(x: float, y: float, dx: float, dy: float, dur: str = "9s", delay: str = "2s") -> tuple[str, str]:
    """A streak that crosses the sky once per loop and is gone most of the time."""
    import math

    angle = math.degrees(math.atan2(dy, dx))
    css = (
        f".shoot{{opacity:0;animation:shoot {dur} linear infinite;animation-delay:{delay}}}"
        f"@keyframes shoot{{0%{{opacity:0;transform:translate(0,0)}}"
        f"1%{{opacity:1;transform:translate(0,0)}}"
        f"7%{{opacity:0;transform:translate({dx}px,{dy}px)}}"
        f"100%{{opacity:0;transform:translate({dx}px,{dy}px)}}}}"
    )
    svg = (
        f'<g class="shoot"><g transform="translate({x} {y}) rotate({angle:.1f})">'
        f'<rect x="-46" y="-0.8" width="46" height="1.6" fill="url(#streak)"/>'
        f'<circle cx="0" cy="0" r="1.8" fill="#FFE3A3"/></g></g>'
    )
    return css, svg


def bat_flock(path: list[tuple[float, float]], dur: float, count: int = 3) -> tuple[str, str]:
    """Small bats crossing the sky. Each one flaps by squashing its own wings."""
    rules = [
        ".bat-flap{animation:batFlap .32s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}",
        "@keyframes batFlap{from{transform:scaleY(1)}to{transform:scaleY(-.45)}}",
    ]
    keys = "".join(
        f"{100 * i / (len(path) - 1):.1f}%{{transform:translate({x}px,{y}px)}}" for i, (x, y) in enumerate(path)
    )
    rules.append(f"@keyframes batPath{{{keys}}}")
    bats = []
    for i in range(count):
        scale = 1 - i * 0.18
        rules.append(
            f".bat-{i}{{animation:batPath {dur}s linear infinite;animation-delay:{-i * 0.9 - 3:.1f}s}}"
        )
        bats.append(
            f'<g class="bat-{i}"><g transform="translate({i * 16} {(-1) ** i * 7}) scale({scale:.2f})">'
            f'<g class="bat-flap"><path d="M0 0 Q-3 -5 -10 -4 Q-7 -1 -7 2 Q-4 0 -2 2 L0 1 L2 2 Q4 0 7 2 '
            f'Q7 -1 10 -4 Q3 -5 0 0 Z" fill="#0B0C0F"/></g>'
            f'<circle cx="0" cy="0.5" r="1.6" fill="#0B0C0F"/></g></g>'
        )
    return "\n".join(rules), "\n".join(bats)


def drifting_clouds(specs: list[tuple[float, float, float, float, float]], prefix: str = "cl") -> tuple[str, str]:
    """Thin night cloud bands that slide slowly sideways and back."""
    rules, shapes = [], []
    for i, (x, y, rx, ry, dur) in enumerate(specs):
        cls = f"{prefix}{i}"
        rules.append(
            f".{cls}{{animation:{cls} {dur}s ease-in-out infinite alternate}}"
            f"@keyframes {cls}{{from{{transform:translate(-30px,0)}}to{{transform:translate(30px,0)}}}}"
        )
        shapes.append(
            f'<g class="{cls}" opacity=".55"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#2A2D35"/>'
            f'<ellipse cx="{x + rx * 0.35}" cy="{y - ry * 0.6}" rx="{rx * 0.5}" ry="{ry * 0.8}" fill="#2A2D35"/></g>'
        )
    return "\n".join(rules), "\n".join(shapes)


def rising_embers(origins: list[tuple[float, float]], prefix: str = "emb") -> tuple[str, str]:
    """Hot flecks that lift off a fire, drift, and go out."""
    rules, flecks = [], []
    colors = ("#F2A03C", "#FFE3A3", "#E4572E")
    for i, (x, y) in enumerate(origins):
        cls = f"{prefix}{i}"
        dx = (-1) ** i * (6 + i % 3 * 5)
        rules.append(css_rise_rule(cls, f"{2.4 + (i % 4) * 0.5:.1f}s", f"{i * 0.37:.2f}s", dx, -58 - (i % 3) * 18, 0.95))
        flecks.append(f'<rect class="{cls}" x="{x}" y="{y}" width="3" height="3" fill="{colors[i % 3]}"/>')
    return "\n".join(rules), "\n".join(flecks)


def glints(points: list[tuple[float, float, float]], prefix: str = "gl") -> tuple[str, str]:
    """Quick brass sparkles on treasure, each on its own beat."""
    rules, marks = [], []
    for i, (x, y, r) in enumerate(points):
        cls = f"{prefix}{i}"
        rules.append(
            f".{cls}{{opacity:0;animation:{cls} {2.2 + i * 0.6:.1f}s ease-in-out infinite;animation-delay:{i * 0.5:.1f}s}}"
            f"@keyframes {cls}{{0%,70%,100%{{opacity:0}}82%{{opacity:1}}}}"
        )
        marks.append(f'<g class="{cls}">{four_star(x, y, r, "#FFE3A3", "1")}</g>')
    return "\n".join(rules), "\n".join(marks)


def pine_silhouette(x: float, y: float, hgt: float, fill: str = "#1B2A2A") -> str:
    half = hgt * 0.3
    return (
        f'<path d="M{x} {y - hgt} L{x + half * 0.55} {y - hgt * 0.62} L{x + half * 0.32} {y - hgt * 0.62} '
        f'L{x + half * 0.8} {y - hgt * 0.3} L{x + half * 0.48} {y - hgt * 0.3} L{x + half} {y} '
        f'L{x - half} {y} L{x - half * 0.48} {y - hgt * 0.3} L{x - half * 0.8} {y - hgt * 0.3} '
        f'L{x - half * 0.32} {y - hgt * 0.62} L{x - half * 0.55} {y - hgt * 0.62} Z" fill="{fill}"/>'
    )


STREAK_DEF = """
    <linearGradient id="streak" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFE3A3" stop-opacity="0"/>
      <stop offset="1" stop-color="#FFE3A3" stop-opacity=".9"/>
    </linearGradient>
    <radialGradient id="footShadow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#000000" stop-opacity=".55"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>"""


def marshmallow_roast(tip_x: float, tip_y: float, ground_y: float, size: float, prefix: str) -> tuple[str, str]:
    """A marshmallow on a stick, planted so it pokes into the breath and toasts.

    Fresh at the top of the loop, golden mid-blast, well done after. The stick
    is stepped pixels, so it stays on the grid like everything else.
    """
    dur = f"{HERO_BREATH}s"
    steps = int((ground_y - tip_y) / size)
    stick = "".join(
        f'<rect x="{tip_x + 1.2 * size + i * size * 0.45:.1f}" y="{tip_y + 3 * size + i * size:.1f}" '
        f'width="{size}" height="{size}" fill="#3A342C"/>'
        for i in range(max(steps - 3, 0))
    )
    rules = [
        css_hold_rule(f"{prefix}-gold", dur, [(36.0, 50.0)]),
        css_hold_rule(f"{prefix}-done", dur, [(50.0, 100.0)]),
    ]
    svg = (
        f"<g>{stick}\n{rle_rects(MARSHMALLOW[:3], tip_x, tip_y, size)}\n"
        f'<g class="{prefix}-gold">{rle_rects(MARSHMALLOW_GOLD, tip_x, tip_y, size)}</g>\n'
        f'<g class="{prefix}-done">{rle_rects(MARSHMALLOW_DONE, tip_x, tip_y, size)}</g></g>'
    )
    return "\n".join(rules), svg


def build_dragon_camp() -> None:
    """Night ridge camp. The dragon stands on the ground with its feet planted,
    breathes over the camp, and toasts a marshmallow on a stick in passing."""
    w, h = 920, 420
    size = 8
    dox, doy = 210, 110
    dragon_css, dragon = dragon_group(dox, doy, size, prefix="dg")
    breath_css, breath = dragon_breath(dox, doy, size, prefix="cf")
    lip_x, lip_y = mouth_cell()
    feet_y = doy + len(DRAGON_BODY) * size
    jet_y = doy + lip_y * size
    roast_css, roast = marshmallow_roast(dox + (lip_x + 23) * size, jet_y - size, 352, 6, "mm")
    star_css, stars = twinkle_stars(
        [(80, 70, 6, "3.4s"), (160, 40, 4, "2.8s"), (700, 36, 4, "3.9s"), (612, 112, 3, "2.6s"), (300, 32, 3, "3.1s"), (870, 160, 3, "4.2s")]
    )
    shoot_css, shoot = shooting_star(560, 34, -220, 70, "11s", "3s")
    ember_css, embers = rising_embers([(640, 300), (650, 296), (660, 302), (646, 292), (656, 298)], "ce")
    fire_css = "\n".join(
        [
            css_hold_rule("cfire-a", "0.7s", [(0.0, 50.0)]),
            css_hold_rule("cfire-b", "0.7s", [(50.0, 100.0)]),
            ".camp-glow{animation:campGlow 1.4s ease-in-out infinite}",
            "@keyframes campGlow{0%,100%{opacity:.45}50%{opacity:.9}}",
            ".ground-lit{opacity:0;animation:groundLit 6s linear infinite}",
            "@keyframes groundLit{0%,13%{opacity:0}18%,62%{opacity:.75}68%,100%{opacity:0}}",
        ]
    )
    fox = fox_group(64, 262, 5)
    plants = "\n".join(rle_rects(GRASS, x, 340, 5) for x in (34, 146, 520, 600, 700, 760, 880))
    moon = f"""<g>
  <circle cx="820" cy="70" r="40" fill="url(#moonHalo)"/>
  <circle cx="820" cy="70" r="22" fill="#E4572E"/>
  <circle cx="812" cy="64" r="20" fill="#14161A" opacity=".88"/>
  <circle cx="820" cy="70" r="22" fill="none" stroke="#C9A227" stroke-width="1" opacity=".45"/>
</g>"""
    extras = "\n".join(
        [
            rle_rects(ANVIL, 162, 322, 5),
            rle_rects(TENT, 796, 296, 6),
            f'<g class="cfire-a">{rle_rects(CAMPFIRE, 620, 292, 6)}</g>',
            f'<g class="cfire-b">{rle_rects(CAMPFIRE_FLICKER, 620, 292, 6)}</g>',
            rle_rects(TEACUP, 556, 330, 5),
            rle_rects(HOARD, 470, 352, 3),
        ]
    )
    foot_shadow = (
        f'<ellipse cx="{dox + 21 * size}" cy="{feet_y + 2}" rx="{15 * size}" ry="{1.6 * size}" fill="url(#footShadow)"/>'
    )
    ground_lit = (
        f'<ellipse class="ground-lit" cx="{dox + (lip_x + 14) * size}" cy="{feet_y}" rx="{18 * size}" ry="{3 * size}" '
        f'fill="url(#hearth)"/>'
    )
    camp_glow = '<ellipse class="camp-glow" cx="644" cy="330" rx="66" ry="28" fill="url(#hearth)"/>'
    frame = f'''<rect x="16" y="16" width="{w-32}" height="{h-32}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".5"/>'''
    caption = f'''<g>
  {ts.outline("Still here after dark", "plate", 460, 50, "#E9E6DF", "middle", max_width=760)}
  <rect x="330" y="66" width="260" height="1" fill="#C9A227" opacity=".8"/>
  {ts.outline("Review is the last stage that counts", "eyebrow", 460, 94, "#C6C2B8", "middle")}
</g>'''
    body = f'''{meadow_background(w, h)}
  {moon}
  {stars}
  {shoot}
  {camp_glow}
  {ground_lit}
  {plants}
  {extras}
  {embers}
  {fox}
  {foot_shadow}
  {dragon}
  {breath}
  {roast}
  {fireflies([(120, 90, "3.2s"), (260, 60, "4s"), (540, 80, "3.6s"), (800, 130, "4.4s"), (880, 200, "3s")])}
  {caption}
  {frame}
'''
    css = "\n".join([dragon_css, breath_css, roast_css, star_css, shoot_css, ember_css, fire_css])
    defs = STREAK_DEF + """
    <radialGradient id="moonHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#E4572E" stop-opacity=".3"/>
      <stop offset="1" stop-color="#E4572E" stop-opacity="0"/>
    </radialGradient>"""
    write(
        OUT / "dragon" / "pixel-dragon.svg",
        svg_wrap(
            w,
            h,
            "Night ridge",
            "A night ridge camp: a dragon breathes fire over the camp and toasts a marshmallow, "
            "with a fox, a tent, a small hoard, and a shooting star.",
            body,
            extra_defs=defs,
            extra_css=css,
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
        svg_wrap(w, h, "A small companion", "A sitting companion on graphite, framed in brass.", body),
    )


def build_napping() -> None:
    w, h = 900, 120
    body = f'''  <rect width="{w}" height="{h}" fill="#1E2026"/>
  <rect x="0" y="0" width="{w}" height="3" fill="#C9A227"/>
  <rect x="0" y="{h-3}" width="{w}" height="3" fill="#8A6E1F"/>
{sitting_dragon(26, 20, 3, napping=True)}
{fox_group(140, 48, 3)}
  <g>
    {ts.outline("The shop is open. Back shortly.", "plate", 248, 56, "#E9E6DF", size=15, max_width=560)}
    <rect x="248" y="68" width="400" height="1" fill="#C9A227" opacity=".7"/>
    {ts.outline("Shipping resumes shortly", "eyebrow", 248, 88, "#C6C2B8")}
  </g>
'''
    write(
        OUT / "atelier" / "napping-banner.svg",
        svg_wrap(w, h, "Break sign", "A slate workshop sign: the shop is open, back shortly.", body),
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


def dragon_breath(ox: float, oy: float, size: float, prefix: str = "hf") -> tuple[str, str]:
    """One CSS breath cycle, shared by every scene with the standing dragon.

    Timeline in % of HERO_BREATH: the throat lights first (7%), the jet swells
    through three frames (12-27%), flickers between two full-blast shapes
    (27-57%) while sparks spit off the end, shrinks back, tears off into loose
    puffs (66-71%), and leaves smoke and a heart drifting up. Nose smoke runs
    the whole time, so the dragon never sits completely still.
    """
    dur = f"{HERO_BREATH}s"

    def cell(c: tuple[float, float]) -> tuple[float, float]:
        return ox + c[0] * size, oy + c[1] * size

    lip_x, lip_y = mouth_cell()
    nose = find_pixels(DRAGON_BODY, "n")
    nx = BODY_AT[0] + sum(x for x, _ in nose) / len(nose)
    ny = BODY_AT[1] + min(y for _, y in nose) - 1

    rules: list[str] = []
    groups: list[str] = []

    # Glow behind the jet first, so the flame sits on top of its own light.
    glow_cls = f"{prefix}-glow"
    rules.append(css_hold_rule(glow_cls, dur, [(14.0, 66.0)], peak=0.95))
    gx, gy = cell((lip_x + 13, lip_y + 0.5))
    groups.append(
        f'<ellipse class="{glow_cls}" cx="{gx:.1f}" cy="{gy:.1f}" '
        f'rx="{17 * size}" ry="{8 * size}" fill="url(#hearth)"/>'
    )

    # Throat light: the mouth seam smoulders ember before and during the jet,
    # and only the lips themselves go gold where the flame leaves.
    seam = find_pixels(DRAGON_BODY, "M")
    lips_x = max(x for x, _ in seam) - 1
    for key, cells, windows in (
        ("R", seam, [(7.0, 70.0)]),
        ("O", [(x, y) for x, y in seam if x >= lips_x], [(14.0, 62.0)]),
    ):
        cls = f"{prefix}-throat{key}"
        rules.append(css_hold_rule(cls, dur, windows))
        rects = "".join(
            f'<rect x="{ox + (BODY_AT[0] + x) * size}" y="{oy + (BODY_AT[1] + y) * size}" '
            f'width="{size}" height="{size}" fill="{PALETTE[key]}"/>'
            for x, y in cells
        )
        groups.append(f'<g class="{cls}">{rects}</g>')

    blast = [(27.0 + 3 * i, 30.0 + 3 * i) for i in range(10)]
    fire_windows = {
        1: [(12.0, 16.0)],
        2: [(16.0, 21.0), (62.0, 66.0)],
        3: [(21.0, 27.0), (57.0, 62.0)],
        4: blast[0::2],
        5: blast[1::2],
        6: [(66.0, 71.0)],
    }
    for index, windows in fire_windows.items():
        cls = f"{prefix}-{index}"
        rules.append(css_hold_rule(cls, dur, windows))
        frame = FIRE_FRAMES[index]
        fx, fy = cell((lip_x, lip_y - len(frame) // 2))
        groups.append(f'<g class="{cls}">\n{rle_rects(frame, fx, fy, size)}\n</g>')

    # Sparks spit off the far end of the jet and arc up and away.
    reach = len(FIRE_FULL_A[0]) - 3
    sparks = [
        (30.0, 2, -3, 9, -7, "9"),
        (34.0, 0, 1, 11, 3, "O"),
        (38.0, 1, -1, 8, -10, "Y"),
        (43.0, 3, 0, 12, -4, "9"),
        (47.0, 0, -2, 10, -9, "O"),
        (51.0, 2, 2, 9, 5, "Y"),
        (55.0, 1, -1, 12, -6, "9"),
    ]
    for i, (start, cx_, cy_, dx, dy, key) in enumerate(sparks):
        cls = f"{prefix}-spark{i}"
        rules.append(css_fly_rule(cls, dur, start, start + 9.0, dx * size, dy * size))
        sx, sy = cell((lip_x + reach + cx_, lip_y + cy_))
        groups.append(
            f'<rect class="{cls}" x="{sx:.1f}" y="{sy:.1f}" width="{size}" height="{size}" fill="{PALETTE[key]}"/>'
        )

    # Spent breath curls up as smoke after the jet tears off.
    for i, (start, cx_, cy_) in enumerate(((68.0, 10, -3), (71.0, 15, -1), (74.0, 6, -2))):
        cls = f"{prefix}-smoke{i}"
        rules.append(css_fly_rule(cls, dur, start, start + 20.0, 3 * size, -9 * size, peak=0.6))
        sx, sy = cell((lip_x + cx_, lip_y + cy_))
        groups.append(f'<g class="{cls}">\n{rle_rects(SMOKE, sx, sy, size * 0.8)}\n</g>')

    heart_cls = f"{prefix}-heart"
    rules.append(css_fly_rule(heart_cls, dur, 70.0, 92.0, 5 * size, -7 * size))
    hx, hy = cell((lip_x + 16, lip_y - 5))
    groups.append(f'<g class="{heart_cls}">\n{rle_rects(HEART, hx, hy, size)}\n</g>')

    nose_sprite = pad([".S.", "S.S", ".S."])
    nx_px, ny_px = cell((nx, ny))
    nose_css, nose_svg = css_puff_stack(
        f"{prefix}nose", (nx_px, ny_px - 2 * size), 3, nose_sprite, max(size - 2, 3), "2.6s", 6, -28, 0.85, 0.6
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


def ruined_tower(x: float, y: float) -> str:
    """Broken watchtower on the far ridge, one window still lit."""
    return f'''<g>
  <path d="M{x} {y} V{y - 64} H{x + 6} V{y - 72} H{x + 12} V{y - 64} H{x + 18} V{y - 70} H{x + 24} V{y - 58} L{x + 30} {y - 52} V{y} Z" fill="#1E2629"/>
  <rect x="{x + 10}" y="{y - 44}" width="5" height="8" fill="#F2C14E" opacity=".8" class="tower-lamp"/>
  <rect x="{x + 6}" y="{y - 22}" width="3" height="6" fill="#141519"/>
  <path d="M{x + 30} {y - 30} H{x + 44} V{y}" fill="none" stroke="#1E2629" stroke-width="5"/>
</g>'''


def build_hero() -> None:
    """Night forge yard. Type sits in the sky, the dragon holds the middle,
    the floor is a hearth. Every moving part is CSS."""
    w, h = 1200, 480
    size = 7
    ox = 330
    oy = 150
    feet_y = oy + len(DRAGON_BODY) * size
    star_css, stars = twinkle_stars(
        [
            (300, 26, 7, "3.6s"),
            (900, 32, 5, "2.9s"),
            (220, 70, 4, "4.1s"),
            (980, 74, 4, "3.3s"),
            (600, 20, 3, "2.7s"),
            (1088, 50, 3, "3.8s"),
            (140, 48, 3, "3.1s"),
            (470, 96, 3, "4.4s"),
            (740, 88, 3, "3.5s"),
            (60, 120, 3, "2.6s"),
            (1150, 100, 3, "4.0s"),
        ]
    )
    shoot_css, shoot = shooting_star(1020, 24, -260, 80, "12s", "4s")
    bat_css, bats = bat_flock([(-40, 80), (120, 52), (260, 74), (420, 40), (620, 64), (1260, 30)], 16.0)
    cloud_css, clouds = drifting_clouds([(196, 82, 46, 5, 19.0), (120, 52, 34, 4, 23.0), (980, 120, 60, 5, 27.0)])
    dragon_css, dragon = dragon_group(ox, oy, size, prefix="dg")
    breath_css, breath_svg = dragon_breath(ox, oy, size, prefix="hf")
    ember_css, embers = rising_embers(
        [(430, 392), (452, 396), (470, 390), (492, 398), (512, 393), (536, 396), (458, 404), (500, 404)], "pit"
    )
    glint_css, glint_marks = glints([(642, 404, 5), (668, 420, 4), (700, 412, 4), (618, 424, 3)])
    chimney_css, chimney_svg = css_puff_stack("hchimney", (1074, 102), 4, SMOKE, 3.5, "3.2s", 8, -46, 0.72, 0.55)
    coal_css = "\n".join(
        (
            f".coal-{i}{{opacity:.7;animation:coal_{i} {2.4 + i * 0.3}s ease-in-out infinite}}"
            f"@keyframes coal_{i}{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}"
        )
        for i in range(7)
    )
    extra_css = "\n".join(
        [
            star_css,
            shoot_css,
            bat_css,
            cloud_css,
            dragon_css,
            breath_css,
            ember_css,
            glint_css,
            chimney_css,
            coal_css,
            ".moon{animation:moonPulse 7.5s ease-in-out infinite}",
            "@keyframes moonPulse{0%,100%{opacity:.88}50%{opacity:1}}",
            ".grate-glow{animation:gratePulse 2.6s ease-in-out infinite}",
            "@keyframes gratePulse{0%,100%{opacity:.4}50%{opacity:.75}}",
            ".tower-lamp{animation:towerLamp 3.7s ease-in-out infinite}",
            "@keyframes towerLamp{0%,100%{opacity:.35}50%{opacity:.95}}",
            ".floor-lit{opacity:0;animation:floorLit 6s linear infinite}",
            "@keyframes floorLit{0%,13%{opacity:0}18%,62%{opacity:.8}68%,100%{opacity:0}}",
        ]
    )
    extra_defs = STREAK_DEF + '''
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
    # The ring sits under the planted foot, so the dragon stands on the grate.
    hearth_cx, hearth_cy = 478.0, float(feet_y + 6)
    pines = "\n".join(
        pine_silhouette(x, y, hgt)
        for x, y, hgt in ((36, 262, 46), (70, 258, 58), (104, 262, 40), (796, 254, 44), (830, 250, 56), (868, 248, 38), (1150, 236, 50))
    )
    lit_floor = (
        f'<ellipse class="floor-lit" cx="{ox + 52 * size}" cy="{feet_y + 14}" rx="{24 * size}" ry="{4 * size}" '
        f'fill="url(#hearth)"/>'
    )
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect width="{w}" height="{h}" fill="url(#duskSky)"/>
  <rect x="0" y="0" width="{w}" height="10" fill="#2A2D35"/>
  <rect x="0" y="10" width="{w}" height="1" fill="#8A6E1F" opacity=".7"/>
  <rect x="0" y="0" width="2" height="{h}" fill="#C9A227"/>
  {stars}
  {shoot}
  {blood_moon(168, 64, 26)}
  {clouds}
  {bats}
  <!-- framing peaks so the name sits in a valley, not a void -->
  <path d="M0 168 C 70 78, 170 70, 270 128 C 330 162, 380 198, 430 210 C 500 128, 620 118, 760 150 C 880 90, 1020 70, 1200 128 L1200 {h} L0 {h} Z" fill="url(#ridgeFar)"/>
  <path d="M0 168 C 70 78, 170 70, 270 128 C 330 162, 380 198, 430 210 C 500 128, 620 118, 760 150 C 880 90, 1020 70, 1200 128" fill="none" stroke="#6E9C90" stroke-width="1.4" opacity=".55"/>
  {ruined_tower(880, 112)}
  <path d="M0 268 C 140 222, 280 248, 430 236 C 580 222, 740 258, 900 230 C 1040 212, 1140 228, 1200 224 L1200 {h} L0 {h} Z" fill="url(#ridgeMid)"/>
  {pines}
  <!-- forge shed on the right ridge -->
  <rect x="1008" y="156" width="92" height="52" fill="#1B1D22"/>
  <path d="M998 156 L1054 128 L1110 156 Z" fill="#2A2D35"/>
  <rect x="1072" y="114" width="16" height="46" fill="#1B1D22"/>
  <rect x="1068" y="110" width="24" height="6" fill="#3A3E48"/>
  <rect x="1022" y="174" width="14" height="12" fill="#F2C14E" opacity=".7" class="tower-lamp"/>
  <rect x="1076" y="118" width="8" height="6" fill="#E4572E">
    <animate attributeName="opacity" values=".4;1;.4" dur="1.8s" repeatCount="indefinite"/>
  </rect>
{chimney_svg}
  <!-- near bank into the hearth -->
  <path d="M0 348 C 200 322, 400 338, 600 328 C 820 316, 1020 340, 1200 330 L1200 {h} L0 {h} Z" fill="#1A2421"/>
  <rect x="0" y="392" width="{w}" height="88" fill="url(#forgeFloor)"/>
  {lit_floor}
  <ellipse class="grate-glow" cx="{hearth_cx}" cy="{hearth_cy}" rx="132" ry="48" fill="url(#grateGlow)"/>
  {coal_pit(hearth_cx, hearth_cy, 210, 58)}
  <rect x="0" y="{h - 3}" width="{w}" height="3" fill="#C9A227"/>
  {vector_lantern(1048, 300)}
{rle_rects(ANVIL, 56, 356, 7)}
{rle_rects(SWORD_STONE, 236, 352, 4)}
{rle_rects(HOARD, 610, 398, 4)}
{glint_marks}
{sitting_dragon(96, 368, 3, napping=False)}
{embers}
  <ellipse cx="{ox + 21 * size}" cy="{feet_y + 1}" rx="{14 * size}" ry="{1.4 * size}" fill="url(#footShadow)"/>
{dragon}
{breath_svg}
{fireflies([(280, 384, "3.1s"), (760, 372, "3.8s"), (880, 360, "3.3s"), (960, 378, "4.2s"), (360, 110, "4.6s"), (840, 92, "3.9s"), (180, 200, "5.1s")])}
  <g>
    {ts.outline("Mubeen", "hero", 600, 72, "#E9E6DF", "middle")}
    <rect x="454" y="88" width="292" height="1" fill="#C9A227"/>
    {ts.outline("Software, systems, and work that ships", "eyebrow", 600, 120, "#C6C2B8", "middle", size=15, tracking=0.12)}
  </g>
'''
    art = svg_wrap(
        w,
        h,
        "Muxby night yard",
        "A night forge yard under a blood moon: a dragon standing on a coal grate breathes fire past its hoard, "
        "bats cross the moon, a shooting star falls, and a lamp is still on in the shed.",
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
  {ts.outline("From the desk", "plate", 174, 70, "#E9E6DF", "middle", size=17)}
  <path d="M64 86 H284" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  {ts.outline("Sharp tools, one warm light, and one", "body", 44, 122, "#C6C2B8", size=14.5)}
  {ts.outline("creature allowed to scorch the drafts.", "body", 44, 146, "#C6C2B8", size=14.5)}
  {ts.outline("Pakistan. Still shipping.", "standfirst", 44, 178, "#C9A227", size=15)}
{sitting_dragon(64, 240, 3)}
{rle_rects(WAX_STAMP, 400, 52, 8)}
  {ts.outline("M", "wordmark", 428, 84, "#F7F5F0", "middle", size=22, tracking=0)}
  <rect x="380" y="160" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="184" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="208" width="160" height="5" fill="#3A3E48"/>
  {ts.outline("Muxby / Pakistan", "label", 486, 252, "#C9A227", "middle")}
  {ts.outline("Stamp of a finished thought", "label", 486, 308, "#E4572E", "middle", size=10, tracking=0.14)}
'''
    write(
        OUT / "atelier" / "postcard.svg",
        svg_wrap(w, h, "Calling card", "A slate calling card with a seal and a sitting companion.", body),
    )


# Workshop rules for the quote card. Two lines each, set by hand so the breaks
# fall on the phrase rather than wherever the measure runs out.
QUOTES = [
    ("Build something this week that a future", "teammate will be glad still exists.", "Rule of the bench"),
    ("Ship the small version first.", "Then make it honest.", "Rule of the forge"),
    ("Read the error. Then read it again,", "slower, before you touch the code.", "Rule of the lamp"),
    ("Leave every codebase a little warmer", "than the way you found it.", "Rule of the hearth"),
]
QUOTE_DUR = 28.0  # seconds for the full rotation, seven per quote


def build_quote() -> None:
    """Quote card: curly brass marks, a rotating set of workshop rules, an
    attribution line, and pips that show which rule is up. Fades are CSS; a
    renderer with no animation shows the first rule, fully set."""
    w, h = 760, 220
    cx = 380
    n = len(QUOTES)
    rules: list[str] = []
    slides: list[str] = []
    pips: list[str] = []
    pip_x0 = cx - (n - 1) * 9
    for i, (line1, line2, source) in enumerate(QUOTES):
        start, end = 100 * i / n, 100 * (i + 1) / n
        fade = 2.2
        name = f"quote{i}"
        if i == 0:
            frames = f"0%,{end - fade:.1f}%{{opacity:1}}{end:.1f}%,{100 - fade:.1f}%{{opacity:0}}100%{{opacity:1}}"
        else:
            frames = (
                f"0%,{start:.1f}%{{opacity:0}}{start + fade:.1f}%,{end - fade:.1f}%{{opacity:1}}"
                f"{end:.1f}%,100%{{opacity:0}}"
            )
        rules.append(
            f".{name}{{opacity:{1 if i == 0 else 0};animation:{name} {QUOTE_DUR}s linear infinite}}"
            f"@keyframes {name}{{{frames}}}"
        )
        slides.append(
            f'<g class="{name}">\n'
            f'  {ts.outline(line1, "heading", cx, 98, "#E9E6DF", "middle", size=21, max_width=540)}\n'
            f'  {ts.outline(line2, "heading", cx, 128, "#E9E6DF", "middle", size=21, max_width=540)}\n'
            f'  {ts.outline(source, "label", cx, 174, "#C9A227", "middle", size=11, tracking=0.14)}\n'
            f"</g>"
        )
        rules.append(css_hold_rule(f"pip{i}", f"{QUOTE_DUR}s", [(start, end)]))
        px = pip_x0 + i * 18
        pips.append(
            f'<circle cx="{px}" cy="196" r="3" fill="none" stroke="#8A6E1F" stroke-width="1"/>'
            f'<circle class="pip{i}" cx="{px}" cy="196" r="3" fill="#E4572E"/>'
        )

    ember_css, embers = rising_embers([(54, 182), (60, 186), (66, 183)], "qe")
    rules.append(ember_css)
    rules.append(".q-ember{animation:qEmber 2.6s ease-in-out infinite}@keyframes qEmber{0%,100%{opacity:.55}50%{opacity:1}}")
    open_mark = ts.outline("“", "heading", 66, 112, "#C9A227", "middle", size=96, face="serif-bold", opacity=".85")
    close_mark = ts.outline("”", "heading", w - 66, 172, "#C9A227", "middle", size=96, face="serif-bold", opacity=".85")
    rivets = "".join(
        f'<circle cx="{x}" cy="{y}" r="2" fill="#8A6E1F"/>' for x, y in ((30, 28), (w - 30, 28), (30, h - 28), (w - 30, h - 28))
    )
    body = "\n".join(
        [
            f'  <rect width="{w}" height="{h}" fill="#0F1013"/>',
            f'  <rect x="16" y="14" width="{w - 32}" height="{h - 28}" fill="#1E2026"/>',
            f'  <rect x="22" y="20" width="{w - 44}" height="{h - 40}" fill="none" stroke="#3A3E48" stroke-width="1"/>',
            f'  <rect x="16" y="14" width="{w - 32}" height="{h - 28}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>',
            f'  <rect x="16" y="14" width="5" height="{h - 28}" fill="#E4572E"/>',
            f"  {rivets}",
            f"  {open_mark}",
            f"  {close_mark}",
            f'  {ts.outline("Words from the workshop", "eyebrow", cx, 52, "#9AA0AC", "middle", size=11, tracking=0.16)}',
            f'  <path d="M{cx - 120} 64 H{cx - 10} M{cx + 10} 64 H{cx + 120}" stroke="#C9A227" stroke-width="1" opacity=".55"/>',
            f'  <path d="M{cx} 59 L{cx + 5} 64 L{cx} 69 L{cx - 5} 64 Z" fill="#C9A227"/>',
            "\n".join(slides),
            f'  <path d="M{cx - 76} 152 H{cx + 76}" stroke="#C9A227" stroke-width="1" opacity=".6"/>',
            "  " + "".join(pips),
            '  <ellipse class="q-ember" cx="60" cy="190" rx="16" ry="6" fill="url(#hearth)"/>',
            "  " + rle_rects(pad([".R.", "ROR", "mRm"]), 54, 184, 4),
            embers,
            "",
        ]
    )
    write(
        OUT / "atelier" / "quote.svg",
        svg_wrap(
            w,
            h,
            "Words from the workshop",
            "A slate card that rotates through four workshop rules in bone serif, framed by brass quote marks: "
            + " ".join(f"{a} {b}" for a, b, _ in QUOTES),
            body,
            extra_css="\n".join(rules),
        ),
    )


def build_signature() -> None:
    """Brass signature: the name in Fraunces italic, revealed left to right once
    by a CSS clip, with a rule and small caps under it. No background, so it
    sits on GitHub's light and dark themes alike."""
    w, h = 360, 140
    name = ts.outline("Muxby", "chapter", w / 2, 86, "url(#ink)", "middle", size=64, face="serif-italic", tracking=0.01)
    css = (
        ".sig-wipe{transform-box:fill-box;transform-origin:left center;"
        "animation:sigWipe 2.4s cubic-bezier(.6,.05,.3,1) .2s both}"
        "@keyframes sigWipe{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".sig-rule{transform-box:fill-box;transform-origin:center;animation:sigRule 1.4s ease-out 1.6s both}"
        "@keyframes sigRule{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    )
    art = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
  <title id="title">Muxby signature</title>
  <defs>
    <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="300" y2="0">
      <stop offset="0" stop-color="#8A6E1F"/>
      <stop offset=".5" stop-color="#C9A227"/>
      <stop offset="1" stop-color="#F2C14E"/>
    </linearGradient>
    <clipPath id="reveal"><rect class="sig-wipe" x="0" y="0" width="{w}" height="{h}"/></clipPath>
    <style>{css}</style>
  </defs>
  <g clip-path="url(#reveal)">{name}</g>
  <rect class="sig-rule" x="40" y="104" width="280" height="1.5" fill="url(#ink)"/>
  {ts.outline("Muxby", "label", w / 2, 128, "#C9A227", "middle", size=11, tracking=0.3)}
</svg>
'''
    write(OUT / "atelier" / "signature.svg", art)


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
    build_signature()
    mirror_legacy()


if __name__ == "__main__":
    main()
