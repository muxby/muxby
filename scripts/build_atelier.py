#!/usr/bin/env python3
"""Generate Obsidian Forge SVG assets for the muxby profile.

Graphite, iron, bone, brass, and one ember. No pastels, no neon, no HUD,
no charts.
"""

from __future__ import annotations

from pathlib import Path

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
    "s": "#A8391B",  # cheek shading
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

# 3x5 pixel caps for wooden signs. Kept tiny on purpose.
FONT_3X5 = {
    "A": [" # ", "# #", "###", "# #", "# #"],
    "B": ["## ", "# #", "## ", "# #", "## "],
    "C": [" ##", "#  ", "#  ", "#  ", " ##"],
    "D": ["## ", "# #", "# #", "# #", "## "],
    "E": ["###", "#  ", "## ", "#  ", "###"],
    "F": ["###", "#  ", "## ", "#  ", "#  "],
    "G": [" ##", "#  ", "# #", "# #", " ##"],
    "H": ["# #", "# #", "###", "# #", "# #"],
    "I": ["###", " # ", " # ", " # ", "###"],
    "J": ["###", "  #", "  #", "# #", " # "],
    "K": ["# #", "# #", "## ", "# #", "# #"],
    "L": ["#  ", "#  ", "#  ", "#  ", "###"],
    "M": ["# #", "###", "# #", "# #", "# #"],
    "N": ["# #", "## ", "# #", "# #", "# #"],
    "O": [" # ", "# #", "# #", "# #", " # "],
    "P": ["## ", "# #", "## ", "#  ", "#  "],
    "Q": [" # ", "# #", "# #", " ##", "  #"],
    "R": ["## ", "# #", "## ", "# #", "# #"],
    "S": [" ##", "#  ", " # ", "  #", "## "],
    "T": ["###", " # ", " # ", " # ", " # "],
    "U": ["# #", "# #", "# #", "# #", "###"],
    "V": ["# #", "# #", "# #", "# #", " # "],
    "W": ["# #", "# #", "# #", "###", "# #"],
    "X": ["# #", "# #", " # ", "# #", "# #"],
    "Y": ["# #", "# #", " # ", " # ", " # "],
    "Z": ["###", "  #", " # ", "#  ", "###"],
    "0": [" # ", "# #", "# #", "# #", " # "],
    "1": [" # ", "## ", " # ", " # ", "###"],
    "2": ["## ", "  #", " # ", "#  ", "###"],
    "3": ["## ", "  #", " # ", "  #", "## "],
    "4": ["# #", "# #", "###", "  #", "  #"],
    "5": ["###", "#  ", "## ", "  #", "## "],
    "6": [" ##", "#  ", "## ", "# #", " # "],
    "7": ["###", "  #", " # ", " # ", " # "],
    "8": [" # ", "# #", " # ", "# #", " # "],
    "9": [" # ", "# #", " ##", "  #", "## "],
    " ": ["   ", "   ", "   ", "   ", "   "],
    ".": ["   ", "   ", "   ", "   ", " # "],
    "!": [" # ", " # ", " # ", "   ", " # "],
    "'": ["#  ", "#  ", "   ", "   ", "   "],
    "-": ["   ", "   ", "###", "   ", "   "],
    "+": ["   ", " # ", "###", " # ", "   "],
    "/": ["  #", "  #", " # ", "#  ", "#  "],
    ":": ["   ", " # ", "   ", " # ", "   "],
    "?": ["## ", "  #", " # ", "   ", " # "],
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


def text_rows(message: str) -> list[str]:
    glyphs = [FONT_3X5.get(ch, FONT_3X5["?"]) for ch in message.upper()]
    rows = []
    for i in range(5):
        row = ""
        for gi, g in enumerate(glyphs):
            row += g[i].replace(" ", ".")
            if gi != len(glyphs) - 1:
                row += "."
        rows.append(row)
    return rows


def pixel_text(message: str, ox: float, oy: float, size: float, color_key: str = "p") -> str:
    rows = []
    for raw in text_rows(message):
        rows.append("".join(color_key if ch == "#" else "." for ch in raw))
    return rle_rects(rows, ox, oy, size)


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
# Head and snout face right; the mouth (M) is where the breath leaves.
DRAGON_BODY = pad(
    [
        "................kHk.kHk...........",
        ".................kHhkkHhk.........",
        "...............kkkkkkkkkk.........",
        ".............kkbbbbbbbbbbkk.......",
        "............kbbbbbbbbbbbbbk.......",
        "...........kbbbbbbbbbbbbbbbk......",
        "...........kbbbbbbbbbppebbbk......",
        "..........kbbbbbbbbbbpppbbbkkkkk..",
        "..........kbbbbbbbbbbpppbbbbbnbbk.",
        "..........kbbbbbbbbbbbbbbbkFFMMMk.",
        "..........kbbbbbbbbssbbbbbCFMMMk..",
        "..........kbbbbbbbbbbbbbbbCCkkkk..",
        "...........kbbbbbbbbbbbbbCCk......",
        "............kbbbbbbbbbbbCCk.......",
        ".............kkkkkkkkkkkkk........",
        "...............kbbbCCCCk..........",
        "..............kbbbbCCCCCk.........",
        ".............kbbbbbCCCCCCk........",
        "............kbbbbbbCCCCCCk........",
        "...........kbbbbbbbbCCCCCCk.......",
        "..........kbbbbbbbbbCCCCCCk.......",
        ".........kbbbbbbbbbbCCCCCCk.......",
        "........kbbbbbbbbbbbCCCCCCk.......",
        ".......kbbbbbbbbbbbbCCCCCCk.......",
        ".......kbbbbbbbbbbbCCCCCCCk.......",
        ".......kbbbbbbbbbbCCCCCCCCk.......",
        "........kbbbbbbbbCCCCCCCCk........",
        ".........kddddddCCCCCCCCk.........",
        ".........kbbbbkkkkbbbbk...........",
        ".........kbbbbkkkkbbbbk...........",
        "........kHHHHHHHkkHHHHHHHk........",
        "........kkkkkkkkkkkkkkkkkk........",
    ]
)

# Small folded wing. The membrane is lighter than the body so it reads as a wing
# and not a hole; the dark diagonal is the finger strut. The shoulder is the
# top-right corner, which is also the flap pivot.
DRAGON_WING = pad(
    [
        "......kkkk",
        "....kkLLwk",
        "..kkLLLLwk",
        ".kLLLLwLwk",
        "kLLLLwLLwk",
        "kkLLwLLLwk",
        ".kkwLLLLwk",
        "..kkkkkkkk",
    ]
)

# Tail: fat where it meets the hip on the right, spade fin at the raised tip.
DRAGON_TAIL = pad(
    [
        "..kBk.............",
        ".kBBBk............",
        "kBBBBBk...........",
        "kBBBBBk...........",
        ".kBBBk............",
        "..kbbk............",
        "..kbbk............",
        "..kbbdk...........",
        "..kbbbdk..........",
        "...kbbbdk.........",
        "...kbbbbdk........",
        "...kbbbbdkkkkkkk..",
        "...kbbbbbbbbbbbbb.",
        "...kbbbbbbbbbbbbb.",
        "....kbbbbbbbbbbbbb",
        ".....kkkkkkkkkkkkk",
    ]
)

# Where each layer sits inside the assembled dragon, in sprite cells.
DRAGON_W, DRAGON_H = 42, 32
BODY_AT = (8, 0)
WING_AT = (17, 17)
TAIL_AT = (0, 12)
WING_PIVOT = (26, 17)  # shoulder
TAIL_PIVOT = (15, 25)  # where the tail disappears behind the hip

DRAGON_IDLE = stack(
    [(DRAGON_TAIL, *TAIL_AT), (DRAGON_BODY, *BODY_AT), (DRAGON_WING, *WING_AT)],
    DRAGON_W,
    DRAGON_H,
)

# Front-on hatchling: swept horns, two shiny eyes, brass belly plate, small
# raised wings, and a spade tail curling out to one side.
DRAGON_SIT = pad(
    [
        ".......H..........H.......",
        "......HH..........HH......",
        ".....hHHkkkkkkkkkkHHh.....",
        "......kkbbbbbbbbbbkk......",
        ".....kbbbbbbbbbbbbbbk.....",
        ".....kbppebbbbbbppebk.....",
        ".....kbpppbbbbbbpppbk.....",
        ".....kbpppbbbbbbpppbk.....",
        ".....kssbbbbbbbbbssbk.....",
        ".....kbbbbbBBBBbbbbbk.....",
        ".....kbbbbbnBBnbbbbbk.....",
        "......kbbbbbMMbbbbbk......",
        ".......kkkkkkkkkkkk.......",
        "........kbCCCCCCbk........",
        "....kLLLbCCCCCCCCbLLLk....",
        "..kLLLLLbccccccccbLLLLLk..",
        ".kLwLLLLbCCCCCCCCbLLLLwLk.",
        ".kkLLLLLbccccccccbLLLLLkk.",
        "...kkLLLbCCCCCCCCbLLLkk...",
        ".......kbccccccccbkkBk....",
        ".......kbCCCCCCCCbkkBBk...",
        ".......kbbbkkkkbbbkkkk....",
        "......kCCCCCkkCCCCCk......",
        "......kkkkkkkkkkkkkk......",
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
# Frames go smallest to largest and are drawn centred on the mouth row.
FIRE_FRAMES = [
    pad(
        [
            ".9.",
            "YOR",
            ".R.",
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

# A rising glint of ember, not a cartoon heart. Kept under the old name so the
# dragon composers do not have to change.
HEART = pad(
    [
        "..9..",
        ".9O9.",
        "9ORO9",
        ".9O9.",
        "..9..",
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

SLEEP_Z = pad(
    [
        "###",
        "  #",
        " # ",
        "#  ",
        "###",
    ]
)


def zzz_pixels(ox: float, oy: float, size: float) -> str:
    rows = []
    for raw in SLEEP_Z:
        rows.append("".join("P" if ch == "#" else "." for ch in raw.replace(" ", ".")))
    return rle_rects(rows, ox, oy, size)


def animate_opacity(values: str, dur: str, begin: str = "0s", key_times: str | None = None) -> str:
    kt = f' keyTimes="{key_times}"' if key_times else ""
    return (
        f'<animate attributeName="opacity" values="{values}"{kt} dur="{dur}" '
        f'begin="{begin}" repeatCount="indefinite"/>'
    )


def svg_wrap(w: int, h: int, title: str, desc: str, body: str, extra_defs: str = "") -> str:
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
{body}
</svg>
'''


BREATH = 5.6  # seconds for one full ember-burst-smoke-spark loop


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

    def spin(cell: tuple[int, int], angles: list[float], dur: float) -> str:
        px, py = ox + cell[0] * size, oy + cell[1] * size
        frames = ";".join(f"{a} {px} {py}" for a in angles)
        return (
            f'  <animateTransform attributeName="transform" type="rotate" values="{frames}" '
            f'dur="{dur}s" repeatCount="indefinite"/>'
        )

    tail_layer = f'<g>\n{spin(TAIL_PIVOT, [0, 6, 0, -4, 0], 3.6)}\n{place(DRAGON_TAIL, TAIL_AT)}\n</g>'
    wing_layer = f'<g>\n{spin(WING_PIVOT, [0, -11, 1, 0], 2.4)}\n{place(DRAGON_WING, WING_AT)}\n</g>'

    # Blink: drop a lid the exact size of the eye over it.
    eye = find_pixels(DRAGON_BODY, "pe")
    ex0, ex1 = min(x for x, _ in eye), max(x for x, _ in eye)
    ey0, ey1 = min(y for _, y in eye), max(y for _, y in eye)
    span = ex1 - ex0 + 1
    lid = ["b" * span, "k" * span, "b" * span][: max(ey1 - ey0 + 1, 2)]
    blink = place(lid, (BODY_AT[0] + ex0, BODY_AT[1] + ey0))

    mx, my = max(find_pixels(DRAGON_BODY, "M"))
    lip_x = BODY_AT[0] + mx + 1
    lip_y = BODY_AT[1] + my

    layers: list[str] = []
    if fire:
        rest = FIRE_FRAMES[0]
        layers.append(
            f'<g>\n{gap_opacity(0.52, 2.72, 0.95)}\n<g>\n'
            f'{place(rest, (lip_x, lip_y - len(rest) // 2))}\n'
            f'{animate_opacity("0.55;1;0.7;1;0.55", "1.3s")}\n</g>\n</g>'
        )
        layers.append(
            f'<ellipse cx="{ox + (lip_x + 9) * size}" cy="{oy + (lip_y + 0.5) * size}" '
            f'rx="{13 * size}" ry="{7 * size}" fill="url(#hearth)" opacity="0">\n'
            f'{timed_opacity(0.62, 2.45, 0.9, 0.3)}\n</ellipse>'
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


def sitting_dragon(ox: float, oy: float, size: float, napping: bool = False) -> str:
    body = rle_rects(DRAGON_SIT, ox, oy, size)
    extras = ""
    if napping:
        extras = (
            f'<g>\n{zzz_pixels(ox + 14 * size, oy - 4 * size, size)}\n'
            f'{animate_opacity("0;1;0", "2.8s")}\n</g>'
            f'<g>\n{zzz_pixels(ox + 18 * size, oy - 8 * size, max(size - 1, 3))}\n'
            f'{animate_opacity("0;0;1;0", "2.8s", "0.6s")}\n</g>'
        )
    else:
        extras = (
            f'<g opacity="0">\n{rle_rects(HEART, ox + 16 * size, oy - 2 * size, max(size - 2, 3))}\n'
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
    dragon = dragon_group(210, 158, size, fire=True)
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
    caption = f'''<g font-family="Georgia, 'Times New Roman', serif">
  <text x="460" y="50" text-anchor="middle" fill="#E9E6DF" font-size="19" letter-spacing="7">A SMALL DRAGON LIVES HERE</text>
  <rect x="330" y="66" width="260" height="1" fill="#C9A227" opacity=".8"/>
  <text x="460" y="94" text-anchor="middle" fill="#C6C2B8" font-size="11" letter-spacing="2">FIRE IS THE LAST STAGE OF REVIEW</text>
</g>'''
    rawr = f'''<g opacity="0">
{pixel_text("RAWR", 470, 188, 4, "9")}
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
{sitting_dragon(68, 30, 6, napping=False)}
{pixel_text("MUXBY", 102, 184, 4, "X")}
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
{sitting_dragon(28, 18, 4, napping=True)}
{fox_group(140, 48, 3)}
  <g font-family="Georgia, 'Times New Roman', serif">
    <text x="248" y="56" font-size="16" fill="#E9E6DF" letter-spacing="3">THE FORGE IS OPEN. THE DRAGON IS ON BREAK.</text>
    <rect x="248" y="68" width="400" height="1" fill="#C9A227" opacity=".7"/>
    <text x="248" y="88" font-size="11" fill="#C6C2B8" letter-spacing="2">FIRE-BREATHING RESUMES SHORTLY</text>
  </g>
'''
    write(
        OUT / "atelier" / "napping-banner.svg",
        svg_wrap(w, h, "Dragon break banner", "A slate workshop sign with a napping pixel dragon and a fox.", body),
    )


def build_hero() -> None:
    w, h = 1200, 390
    size = 6
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="48" y="28" width="1104" height="334" fill="url(#duskSky)"/>
  <!-- window frame: iron with a brass hairline -->
  <rect x="48" y="28" width="1104" height="334" fill="none" stroke="#2A2D35" stroke-width="18"/>
  <rect x="57" y="37" width="1086" height="316" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <rect x="592" y="28" width="14" height="334" fill="#2A2D35"/>
  <rect x="48" y="188" width="1104" height="12" fill="#2A2D35"/>
  <rect x="48" y="28" width="1104" height="18" fill="#3A3E48"/>
  <!-- sill -->
  <rect x="32" y="348" width="1136" height="20" fill="#2A2D35"/>
  <rect x="32" y="348" width="1136" height="3" fill="#8A6E1F"/>
  <rect x="24" y="366" width="1152" height="16" fill="#1A1C22"/>
  <!-- left pane: cold ridges -->
  <path d="M66 188 C 160 152, 260 170, 360 172 C 460 174, 530 152, 590 170 L590 188 L66 188 Z" fill="#232B2E"/>
  <path d="M66 188 C 180 178, 300 198, 590 188 L590 348 L66 188 Z" fill="#1E2624"/>
  <path d="M66 262 C 200 242, 340 270, 590 252 L590 348 L66 348 Z" fill="#1A2421"/>
  <!-- right pane: lamp glow and desk -->
  <rect x="608" y="200" width="536" height="148" fill="#141519"/>
  <ellipse cx="1082" cy="252" rx="76" ry="64" fill="url(#lamp)">
    <animate attributeName="opacity" values=".55;.9;.55" dur="3.4s" repeatCount="indefinite"/>
  </ellipse>
  <rect x="1076" y="268" width="12" height="80" fill="#8A6E1F"/>
  <path d="M1056 268 L1068 242 L1096 242 L1108 268 Z" fill="#C9A227"/>
  <rect x="620" y="300" width="150" height="48" fill="#2A2D35"/>
  <rect x="620" y="300" width="150" height="3" fill="#8A6E1F"/>
  <rect x="632" y="312" width="64" height="8" fill="#E9E6DF"/>
  <rect x="632" y="326" width="78" height="6" fill="#C6C2B8"/>
  <rect x="632" y="338" width="48" height="4" fill="#C9A227"/>
{dragon_group(800, 188, 5, fire=True, bob=True)}
{fox_group(96, 286, 4)}
{rle_rects(TEACUP, 632, 280, 4)}
{rle_rects(STAR, 140, 70, 4)}
{rle_rects(STAR, 420, 88, 3)}
{rle_rects(STAR, 700, 64, 4)}
{rle_rects(STAR, 860, 108, 3)}
{fireflies([(220, 90, "3.5s"), (340, 60, "4.2s"), (760, 80, "3.8s"), (1040, 100, "4.6s")])}
  <g font-family="Georgia, 'Times New Roman', serif" text-anchor="middle">
    <text x="328" y="92" fill="#E9E6DF" font-size="44" letter-spacing="10">MUBEEN</text>
    <rect x="196" y="110" width="264" height="1" fill="#C9A227"/>
    <text x="328" y="136" fill="#C6C2B8" font-size="11" letter-spacing="1">SOFTWARE, SYSTEMS, AND A SMALL FIRE-BREATHING DRAGON</text>
  </g>
  <g font-family="Georgia, 'Times New Roman', serif" fill="#C9A227">
    <text x="1128" y="76" font-size="11" letter-spacing="4" text-anchor="end">THE FORGE WINDOW</text>
  </g>
'''
    write(
        OUT / "atelier" / "hero.svg",
        svg_wrap(
            w,
            h,
            "Muxby forge window",
            "An iron window at night with a pixel dragon on the sill, a fox on the ridge, and a brass lamp.",
            body,
        ),
    )


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
        text_w = (4 * len(label) - 1) * 3
        tags.append(
            f'''<g>
  <animateTransform attributeName="transform" type="rotate" values="0 {cx} 150; 1.1 {cx} 150; -1.1 {cx} 150; 0 {cx} 150" dur="{6 + i * 0.4}s" repeatCount="indefinite"/>
  <path d="M{cx} 150 V186" stroke="#8A6E1F" stroke-width="2"/>
  <rect x="{x}" y="186" width="{tag_w}" height="{tag_h}" fill="#E9E6DF"/>
  <rect x="{x}" y="186" width="{tag_w}" height="4" fill="#C9A227"/>
  <circle cx="{cx}" cy="200" r="3" fill="#2A2D35"/>
  {pixel_text(label, cx - text_w / 2, 226, 3, "p")}
  <path d="M{x + 18} 258 H{x + tag_w - 18}" stroke="#4E535D" stroke-width="1"/>
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="20" y="18" width="{w-40}" height="{h-36}" fill="#1E2026"/>
  <rect x="20" y="18" width="{w-40}" height="{h-36}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <text x="460" y="62" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="20" fill="#E9E6DF" letter-spacing="8">THE TOOL RACK</text>
  <path d="M340 78 H580" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  <text x="460" y="102" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12" fill="#9AA0AC" letter-spacing="3">HUNG WHERE I CAN REACH THEM</text>
  <rect x="48" y="146" width="824" height="5" fill="url(#brass)"/>
  <rect x="44" y="140" width="10" height="17" fill="#8A6E1F"/>
  <rect x="866" y="140" width="10" height="17" fill="#8A6E1F"/>
  {"".join(tags)}
  <rect x="20" y="356" width="{w-40}" height="66" fill="#2A2D35"/>
  <rect x="20" y="356" width="{w-40}" height="2" fill="#8A6E1F"/>
{sitting_dragon(48, 284, 3)}
{rle_rects(ANVIL, 816, 316, 5)}
  <text x="460" y="398" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#C9A227" letter-spacing="4">SAME SIZE TAGS. NO SCORES.</text>
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
    w, h = 420, 280
    steam = []
    for i, x in enumerate((208, 230, 252)):
        steam.append(
            f'''<g fill="#6B7078" opacity="0">
  <ellipse cx="{x}" cy="70" rx="8" ry="12"/>
  {animate_opacity("0;0.75;0", f"{2.4 + i*0.2}s", f"{i*0.3}s")}
  <animateTransform attributeName="transform" type="translate" values="0 0; {(-8)+i*4} -40" dur="{2.4+i*0.2}s" begin="{i*0.3}s" repeatCount="indefinite"/>
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".6"/>
  <text x="210" y="40" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="14" fill="#E9E6DF" letter-spacing="6">ON THE HOB</text>
  <ellipse cx="210" cy="212" rx="78" ry="20" fill="url(#hearth)">
    <animate attributeName="opacity" values=".5;.95;.5" dur="2.6s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="210" cy="216" rx="66" ry="10" fill="#0F1013"/>
  <path d="M154 152 L112 136 L106 150 L150 174 Z" fill="#2A2D35" stroke="#3A3E48" stroke-width="2"/>
  <path d="M150 150 C150 112 270 112 270 150 L262 200 C262 224 158 224 158 200 Z" fill="#2A2D35" stroke="#3A3E48" stroke-width="2"/>
  <path d="M160 176 H260" stroke="#C9A227" stroke-width="3" opacity=".9"/>
  <path d="M270 156 C316 156 316 198 268 198" fill="none" stroke="#C9A227" stroke-width="6"/>
  <ellipse cx="210" cy="128" rx="46" ry="9" fill="#3A3E48"/>
  <rect x="198" y="104" width="24" height="16" fill="#C9A227">
    <animateTransform attributeName="transform" type="rotate" values="0 210 114; -8 210 114; 6 210 114; 0 210 114" dur="1.2s" repeatCount="indefinite"/>
  </rect>
  {"".join(steam)}
  <text x="210" y="252" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#9AA0AC" letter-spacing="3">AGENTIC SYSTEMS, POURED SLOWLY</text>
{rle_rects(TEACUP, 324, 198, 5)}
'''
    write(
        OUT / "atelier" / "kettle.svg",
        svg_wrap(w, h, "Iron kettle on the hob", "An iron kettle with a brass band and handle, steaming over an ember glow.", body),
    )


def build_lantern() -> None:
    w, h = 280, 300
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".6"/>
  <ellipse cx="140" cy="150" rx="72" ry="84" fill="url(#lamp)">
    <animate attributeName="opacity" values=".45;1;.45" dur="2.8s" repeatCount="indefinite"/>
  </ellipse>
  <path d="M140 44 V62" stroke="#8A6E1F" stroke-width="3"/>
{rle_rects(LANTERN_CORE, 92, 70, 8)}
{fireflies([(84, 108, "3.4s"), (198, 92, "4.1s"), (172, 158, "3.7s"), (96, 176, "4.5s")])}
  <text x="140" y="266" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12" fill="#C9A227" letter-spacing="5">KEEP A LIGHT ON</text>
'''
    write(
        OUT / "atelier" / "lantern.svg",
        svg_wrap(w, h, "Brass lantern", "A brass lantern burning on graphite with embers drifting around it.", body),
    )


def build_mail() -> None:
    w, h = 520, 220
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".6"/>
  <text x="260" y="38" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="14" fill="#E9E6DF" letter-spacing="6">DRAGON POST</text>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 18; 330 0; 0 18" dur="8s" repeatCount="indefinite"/>
{rle_rects(DRAGON_IDLE, 0, 58, 4)}
{rle_rects(ENVELOPE, 176, 118, 4)}
  </g>
  <text x="260" y="208" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#9AA0AC" letter-spacing="3">THE POST GOES OUT AT DUSK</text>
'''
    write(
        OUT / "atelier" / "mail.svg",
        svg_wrap(w, h, "Dragon post", "A pixel dragon carrying a bone envelope across a graphite field.", body),
    )


def build_ember_dish() -> None:
    """Banked coals in an iron dish. Replaces the old koi pond."""
    w, h = 520, 220
    coals = []
    for i, (cx, cy, rx, ry, fill) in enumerate(
        [
            (200, 132, 26, 12, "#A33418"),
            (248, 126, 30, 13, "#E4572E"),
            (300, 134, 24, 11, "#A33418"),
            (224, 144, 22, 9, "#F2A03C"),
            (280, 146, 20, 9, "#E4572E"),
        ]
    ):
        coals.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}">'
            f'<animate attributeName="opacity" values=".55;1;.55" dur="{2.4 + i * 0.35}s" '
            f'begin="{i * 0.4}s" repeatCount="indefinite"/></ellipse>'
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#17181C"/>
  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".6"/>
  <text x="260" y="38" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="14" fill="#E9E6DF" letter-spacing="6">BANKED COALS</text>
  <ellipse cx="260" cy="118" rx="150" ry="58" fill="url(#hearth)">
    <animate attributeName="opacity" values=".5;.9;.5" dur="3.2s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="260" cy="140" rx="130" ry="42" fill="#2A2D35"/>
  <ellipse cx="260" cy="138" rx="118" ry="34" fill="#1A1C22"/>
  <path d="M142 140 A118 34 0 0 0 378 140" fill="none" stroke="#8A6E1F" stroke-width="2" opacity=".7"/>
  {"".join(coals)}
{fireflies([(214, 96, "3.1s"), (262, 84, "3.8s"), (312, 98, "3.4s")])}
  <text x="260" y="198" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#9AA0AC" letter-spacing="3">NEVER FULLY OUT</text>
'''
    art = svg_wrap(
        w,
        h,
        "Banked coals",
        "An iron dish of banked embers glowing on graphite, with sparks rising.",
        body,
    )
    write(OUT / "atelier" / "ember.svg", art)
    write(OUT / "atelier" / "koi.svg", art)


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
  <text x="174" y="70" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="18" fill="#E9E6DF" letter-spacing="6">FROM THE FORGE</text>
  <path d="M64 86 H284" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  <text x="44" y="122" font-family="Georgia, 'Times New Roman', serif" font-size="13" fill="#C6C2B8">
    <tspan x="44" dy="0">Sharp tools, one warm light, and one</tspan>
    <tspan x="44" dy="24">creature allowed to scorch the drafts.</tspan>
    <tspan x="44" dy="30">Pakistan. Still shipping.</tspan>
  </text>
{sitting_dragon(76, 244, 4)}
{rle_rects(WAX_STAMP, 400, 52, 8)}
  <text x="428" y="84" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="20" fill="#F7F5F0">M</text>
  <rect x="380" y="160" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="184" width="210" height="5" fill="#3A3E48"/>
  <rect x="380" y="208" width="160" height="5" fill="#3A3E48"/>
  <text x="486" y="252" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#C9A227" letter-spacing="4">MUXBY / THE FORGE</text>
  <text x="486" y="308" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="10" fill="#E4572E" letter-spacing="2">STAMP OF A FINISHED THOUGHT</text>
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
  <text x="52" y="86" font-family="Georgia, 'Times New Roman', serif" font-size="56" fill="#C9A227" opacity=".55">"</text>
  <text x="376" y="76" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="17" fill="#E9E6DF">Build something this week that a future teammate</text>
  <text x="376" y="104" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="17" fill="#E9E6DF">will be glad still exists.</text>
  <path d="M300 122 H452" stroke="#C9A227" stroke-width="1" opacity=".6"/>
'''
    write(
        OUT / "atelier" / "quote.svg",
        svg_wrap(w, h, "Working principle", "A slate card with a brass rule and a working principle in bone text.", body),
    )


def build_fire_closeup() -> None:
    w, h = 640, 380
    size = 8
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="14" y="14" width="{w-28}" height="{h-28}" fill="#17181C"/>
  <rect x="14" y="14" width="{w-28}" height="{h-28}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <text x="320" y="48" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="15" fill="#E9E6DF" letter-spacing="7">EMBER, ON PURPOSE</text>
  <path d="M240 62 H400" stroke="#C9A227" stroke-width="1" opacity=".6"/>
{dragon_group(44, 88, size, fire=True)}
{pixel_text("FIRE PLEASE", 424, 316, 4, "X")}
'''
    write(
        OUT / "dragon" / "pixel-dragon-fire.svg",
        svg_wrap(
            w,
            h,
            "Pixel dragon breathing fire, close",
            "A large pixel dragon on graphite with a constant ember and looping fire breath.",
            body,
        ),
    )


def build_stickers() -> None:
    """Struck medallions on a graphite sheet, on a strict grid. The old sheet
    was a scatter of pastel enamel pins."""
    w, h = 920, 300
    labels = ["PY", "TS", "JS", "C++", "GO", "SQL", "REACT", "NODE", "PG", "K8S", "AWS", "LLM"]
    rings = ["#C9A227", "#3F6B62", "#A33418", "#3A3E48"]
    badges = []
    for i, label in enumerate(labels):
        col, row = i % 6, i // 6
        cx = 96 + col * 146
        cy = 140 + row * 88
        cell = 3 if len(label) <= 4 else 2
        text_w = (4 * len(label) - 1) * cell
        badges.append(
            f'''<g>
  <animateTransform attributeName="transform" type="translate" values="0 0; 0 -2; 0 0" dur="{3.4 + i*0.13}s" repeatCount="indefinite"/>
  <circle cx="{cx}" cy="{cy}" r="34" fill="{rings[i % len(rings)]}"/>
  <circle cx="{cx}" cy="{cy}" r="29" fill="#1E2026"/>
  <circle cx="{cx}" cy="{cy}" r="29" fill="none" stroke="#14161A" stroke-width="2"/>
  {pixel_text(label, cx - text_w / 2, cy - cell * 2.5, cell, "P")}
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#0F1013"/>
  <rect x="18" y="14" width="{w-36}" height="{h-28}" fill="#17181C"/>
  <rect x="18" y="14" width="{w-36}" height="{h-28}" fill="none" stroke="#8A6E1F" stroke-width="1" opacity=".7"/>
  <text x="460" y="62" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="16" fill="#E9E6DF" letter-spacing="8">STRUCK AT THE BENCH</text>
  <path d="M340 78 H580" stroke="#C9A227" stroke-width="1" opacity=".7"/>
  {"".join(badges)}
'''
    write(
        OUT / "atelier" / "stickers.svg",
        svg_wrap(w, h, "Struck medallion sheet", "A graphite sheet of struck technology medallions ringed in brass, patina, and ember.", body),
    )


# Filenames from older versions of this profile. They are kept as copies of the
# current artwork so stale external links cannot resurrect a dead theme.
LEGACY_MIRRORS = {
    "constellation.svg": "atelier/corkboard.svg",
    "odyssey.svg": "atelier/trail.svg",
    "hologram.svg": "atelier/desk.svg",
    "radar-chart.svg": "atelier/desk.svg",
    "signature.svg": "atelier/signature.svg",
    "sigil.svg": "atelier/wax-seal.svg",
    "hero-banner.svg": "atelier/hero.svg",
    "hero-editorial.svg": "atelier/hero.svg",
    "aurora-header.svg": "atelier/quote.svg",
    "glitch-restricted.svg": "atelier/napping-banner.svg",
    "graph-bars.svg": "atelier/garden.svg",
    "graph-donut.svg": "atelier/ember.svg",
    "graph-gauges.svg": "atelier/mail.svg",
    "graph-growth.svg": "atelier/kettle.svg",
    "graph-heatmap.svg": "atelier/stickers.svg",
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
    build_dragon_camp()
    build_tiny_dragon()
    build_fire_closeup()
    build_napping()
    build_hero()
    build_tool_rack()
    build_kettle()
    build_lantern()
    build_mail()
    build_ember_dish()
    build_dividers()
    build_postcard()
    build_quote()
    build_stickers()
    mirror_legacy()


if __name__ == "__main__":
    main()
