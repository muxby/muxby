#!/usr/bin/env python3
"""Generate Ember Atelier SVG assets for the muxby profile.

Warm paper, terracotta, sage, and walnut. No neon, no HUD, no charts.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

# Ink on paper. These are the only colors the atelier draws with.
PALETTE = {
    ".": None,
    "k": "#3A2418",  # outline
    "B": "#D4683C",  # body bright
    "b": "#C45C32",  # terracotta body
    "d": "#8B3A22",  # body shadow
    "C": "#F3D2B0",  # cream light
    "c": "#E8C49A",  # cream
    "W": "#6B3228",  # wing dark
    "w": "#A85A40",  # wing mid
    "L": "#E8A070",  # wing light
    "H": "#F0DDB8",  # horn
    "h": "#C4A574",  # horn shadow / brass
    "e": "#FFF8EE",  # eye white
    "p": "#2A1810",  # pupil / ink
    "s": "#E09080",  # blush
    "n": "#5A241C",  # nose
    "M": "#4A1C16",  # mouth
    "T": "#C45C32",
    "t": "#8B3A22",
    "G": "#6F8F5E",  # sage
    "g": "#4F6B45",  # moss
    "Y": "#FFF3A0",  # fire light
    "O": "#FFC14D",  # fire
    "R": "#E07A3D",  # ember
    "F": "#C45C32",
    "S": "#D4C8B8",  # smoke
    "X": "#B08D62",  # brass
    "P": "#F6EFE4",  # paper
    "I": "#1C1510",  # walnut
    "o": "#E07A3D",  # fox orange
    "u": "#A84A20",  # fox dark
    "q": "#F6EFE4",  # fox white
    "m": "#C4897A",  # dusty rose
    "A": "#7A9E6E",  # leaf bright
    "a": "#3F5A3A",  # leaf dark
    "N": "#8B6E58",  # wood
    "r": "#6B2E24",  # deep clay
    "z": "#EDE3D0",  # parchment
    "y": "#F4EBD8",  # warm paper
    "1": "#5C4A38",  # bark
    "2": "#8A9E78",  # distant hill
    "3": "#D9B48A",  # path
    "4": "#F7D9B0",  # dusk
    "5": "#E8B48A",  # dusk peach
    "6": "#F2C9A0",  # window glow
    "7": "#2C4A48",  # dusk fir
    "8": "#4A3A2C",  # soil
    "9": "#FFF8C8",  # spark
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


DRAGON_IDLE = pad(
    [
        ".........................H.H........",
        "........................HkHk........",
        ".......................kkbbkk......",
        "......................kBbbbbbk.....",
        ".....................kBbbeePPkk....",
        ".....................kBbsdPPPkk....",
        "....................kkCCCCCnkk.....",
        "....................kCCCCCCkk......",
        ".....................kCMMCkk.......",
        "..........LLL.....kbbbbbk..........",
        "........LLwLwL...kbbbbbbk..........",
        "..tttt.LLwwwwwL.kbbCCCCbk..........",
        ".tttttttLwwwwwLkbbbbbbbbk..........",
        "..ttttt..LLwL...kbbbbbbbk..........",
        "...ttt..........kkbbkbbk...........",
        ".................kbk..kdk..........",
        ".................kHk..kHk..........",
    ]
)

DRAGON_SIT = pad(
    [
        "......H...H.......",
        ".....HkkkkkH......",
        "....kkbbbbbkk.....",
        "...kBBePPeeBBk....",
        "...kBbsPPssPbk....",
        "...kkCCCCCCCkk....",
        "....kbbCnnCcbk....",
        "...WWkbbbbbbkWW...",
        "..WwLkbCCCCbkLwW..",
        "..WwLkbbbbbbkLwW..",
        "...WWkbk..kbkWW...",
        ".....kHk..kHk.....",
        ".....kHk..kHk.....",
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

FIRE_FRAMES = [
    pad(
        [
            "..Y9",
            ".YOY",
            ".ORY",
            ".O..",
        ]
    ),
    pad(
        [
            "...Y9Y.",
            "..YOYOY",
            ".YORORY",
            "..ORFR.",
            "...OR..",
        ]
    ),
    pad(
        [
            "....9Y.Y.9.",
            "...YYOYOYY.",
            "..YORORORY.",
            ".YORFFRROY.",
            "..ORFFRRO..",
            "...RFRR....",
            "....RR.....",
        ]
    ),
    pad(
        [
            "......9.Y.Y.9...",
            ".....YYOYOYOY...",
            "....YORORORORY..",
            "...YORFFFRROY...",
            "..YORFFFFRRO....",
            "...ORFFFRR......",
            "....RFRRS.......",
            ".....RRS........",
            "......S.........",
        ]
    ),
]

SMOKE = pad(
    [
        "S.S",
        ".S.",
        "S..",
    ]
)

HEART = pad(
    [
        ".mm.mm.",
        "mmmmmmm",
        "mmmmmmm",
        ".mmmmm.",
        "..mmm..",
        "...m...",
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

MUSHROOM = pad(
    [
        "..rrr..",
        ".rPrPrr",
        "rrrrrrr",
        "..CCC..",
        "..CCC..",
        "..CCC..",
    ]
)

SNAIL = pad(
    [
        "...mm.",
        "..mPPm",
        "k.mmmm",
        "kkkk..",
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

BUTTERFLY = pad(
    [
        "m.G.m",
        "mmGmm",
        ".kGk.",
        "A.k.A",
        "A...A",
    ]
)

LANTERN_CORE = pad(
    [
        "...NNN...",
        "..NyyyN..",
        ".NyyyyyN.",
        ".NyY9YyN.",
        ".NyyyyyN.",
        "..NyyyN..",
        "...NkN...",
        "....k....",
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

KOI = pad(
    [
        "..mmBBm..",
        ".mBBBBBm.",
        "mBBCeeBBm",
        ".mBBBBBm.",
        "..BmmB...",
        "...mm....",
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
        rows.append("".join("p" if ch == "#" else "." for ch in raw.replace(" ", ".")))
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
      <stop offset="0" stop-color="#E7C4A2"/>
      <stop offset=".42" stop-color="#F0D3B0"/>
      <stop offset="1" stop-color="#C9B48A"/>
    </linearGradient>
    <linearGradient id="paperSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F6EFE4"/>
      <stop offset="1" stop-color="#E4D3B4"/>
    </linearGradient>
    <linearGradient id="hillA" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#8AA078"/>
      <stop offset="1" stop-color="#5F734C"/>
    </linearGradient>
    <linearGradient id="hillB" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6F8F5E"/>
      <stop offset="1" stop-color="#4F6B45"/>
    </linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6B4A32"/>
      <stop offset="1" stop-color="#4A3224"/>
    </linearGradient>
    <radialGradient id="lamp" cx="50%" cy="40%" r="50%">
      <stop offset="0" stop-color="#FFF3A0" stop-opacity=".9"/>
      <stop offset=".45" stop-color="#E8A070" stop-opacity=".28"/>
      <stop offset="1" stop-color="#E07A3D" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="hearth" cx="50%" cy="60%" r="50%">
      <stop offset="0" stop-color="#FFF3A0" stop-opacity=".7"/>
      <stop offset="1" stop-color="#C45C32" stop-opacity="0"/>
    </radialGradient>
    <filter id="softPaper" x="-2%" y="-2%" width="104%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#3A2418" flood-opacity=".18"/>
    </filter>
    {extra_defs}
  </defs>
{body}
</svg>
'''


def dragon_group(ox: float, oy: float, size: float, fire: bool = True, bob: bool = True) -> str:
    body = rle_rects(DRAGON_IDLE, ox, oy, size)
    eyes = find_pixels(DRAGON_IDLE, "e")
    if eyes:
        bx, by = min(eyes)
        blink = rle_rects(["kkkk"], ox + bx * size, oy + by * size, size)
    else:
        blink = rle_rects(["kkk"], ox + 15 * size, oy + 5 * size, size)
    ms = find_pixels(DRAGON_IDLE, "M")
    if ms:
        mx, my = max(ms)
        mouth_x = ox + (mx + 1) * size
        mouth_y = oy + my * size
    else:
        mouth_x = ox + 24 * size
        mouth_y = oy + 8 * size
    fire_layers = []
    if fire:
        ember = rle_rects(FIRE_FRAMES[0], mouth_x + 1 * size, mouth_y - 1 * size, size)
        fire_layers.append(f"<g opacity=\".85\">\n{ember}\n</g>")
        timings = [
            ("0.2;0.9;0.2;0;0.2", "5.5s", "0s"),
            ("0;0.2;1;0.4;0", "5.5s", "0.15s"),
            ("0;0;0.3;1;0", "5.5s", "0.3s"),
            ("0;0;0;0.85;0", "5.5s", "0.45s"),
        ]
        offsets = [(2, -1), (3, -3), (4, -6), (5, -8)]
        for i, frame in enumerate(FIRE_FRAMES):
            dx, dy = offsets[i]
            values, dur, begin = timings[i]
            fire_layers.append(
                f'<g opacity="0">\n{rle_rects(frame, mouth_x + dx * size, mouth_y + dy * size, size)}\n'
                f'{animate_opacity(values, dur, begin)}\n</g>'
            )
        fire_layers.append(
            f'<g opacity="0">\n{rle_rects(SMOKE, mouth_x + 12 * size, mouth_y - 8 * size, size)}\n'
            f'{animate_opacity("0;0;0.8;0", "5.5s", "0.8s")}\n</g>'
        )
        fire_layers.append(
            f'<g opacity="0">\n{rle_rects(HEART, mouth_x + 9 * size, mouth_y - 12 * size, size)}\n'
            f'{animate_opacity("0;0;0;1;0", "5.5s", "1.6s")}\n</g>'
        )
    wing = f'''<g>
  <animateTransform attributeName="transform" type="rotate" values="0 {ox + 6*size} {oy + 12*size}; -9 {ox + 6*size} {oy + 12*size}; 0 {ox + 6*size} {oy + 12*size}" dur="2.2s" repeatCount="indefinite"/>
</g>'''
    tail_wag = ""
    bob_wrap_open = (
        f'<g>\n  <animateTransform attributeName="transform" type="translate" '
        f'values="0 0; 0 {-size/2}; 0 0" dur="2.6s" repeatCount="indefinite"/>'
        if bob
        else "<g>"
    )
    return f'''{bob_wrap_open}
{body}
<g opacity="0">
{blink}
{animate_opacity("0;0;1;1;0;0", "3.6s", "0s", "0;0.72;0.74;0.8;0.82;1")}
</g>
{"".join(fire_layers)}
{wing}
{tail_wag}
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
    return f'''  <rect width="{w}" height="{h}" fill="url(#duskSky)"/>
  <ellipse cx="{w*0.18}" cy="{h*0.22}" rx="{w*0.16}" ry="{h*0.08}" fill="#F4EBD8" opacity=".55">
    <animate attributeName="cx" values="{w*0.18};{w*0.22};{w*0.18}" dur="18s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="{w*0.78}" cy="{h*0.16}" rx="{w*0.14}" ry="{h*0.07}" fill="#F6EFE4" opacity=".4">
    <animate attributeName="cx" values="{w*0.78};{w*0.74};{w*0.78}" dur="22s" repeatCount="indefinite"/>
  </ellipse>
  <path d="M0 {h*0.62} C {w*0.18} {h*0.48}, {w*0.34} {h*0.52}, {w*0.5} {h*0.58} C {w*0.7} {h*0.66}, {w*0.86} {h*0.5}, {w} {h*0.56} L{w} {h} L0 {h} Z" fill="url(#hillA)"/>
  <path d="M0 {h*0.74} C {w*0.22} {h*0.66}, {w*0.4} {h*0.7}, {w*0.58} {h*0.7} C {w*0.76} {h*0.7}, {w*0.9} {h*0.64}, {w} {h*0.68} L{w} {h} L0 {h} Z" fill="url(#hillB)"/>
  <rect x="0" y="{h*0.82}" width="{w}" height="{h*0.18}" fill="#5C7348"/>
'''


def fireflies(positions: list[tuple[float, float, str]]) -> str:
    bits = []
    for i, (x, y, dur) in enumerate(positions):
        bits.append(
            f'<circle cx="{x}" cy="{y}" r="2.2" fill="#FFF3A0" opacity=".2">'
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
    dragon = dragon_group(210, 168, size, fire=True)
    fox = fox_group(80, 268, 5)
    plants = "\n".join(
        [
            rle_rects(GRASS, x, 340, 5)
            for x in (40, 70, 110, 150, 560, 600, 650, 700, 760, 820)
        ]
    )
    extras = "\n".join(
        [
            rle_rects(MUSHROOM, 48, 318, 5),
            rle_rects(SNAIL, 140, 348, 4),
            rle_rects(CAMPFIRE, 620, 292, 6),
            rle_rects(MARSHMALLOW, 598, 268, 5),
            rle_rects(TEACUP, 780, 328, 5),
            rle_rects(BUTTERFLY, 500, 150, 4),
            rle_rects(STAR, 80, 70, 4),
            rle_rects(STAR, 160, 40, 3),
            rle_rects(STAR, 840, 60, 4),
            rle_rects(STAR, 700, 36, 3),
        ]
    )
    butterfly = f'''<g>
  <animateTransform attributeName="transform" type="translate" values="0 0; 40 -16; 80 8; 40 -10; 0 0" dur="9s" repeatCount="indefinite"/>
{rle_rects(BUTTERFLY, 430, 120, 4)}
</g>'''
    camp_glow = '''<ellipse cx="644" cy="330" rx="54" ry="22" fill="url(#hearth)">
  <animate attributeName="opacity" values=".45;.85;.45" dur="1.4s" repeatCount="indefinite"/>
</ellipse>'''
    caption = f'''<g font-family="Georgia, 'Times New Roman', serif">
  <text x="460" y="48" text-anchor="middle" fill="#3A2418" font-size="22">a small dragon lives here</text>
  <text x="460" y="74" text-anchor="middle" fill="#6B4A32" font-size="13">he breathes fire when he is proud of a clean commit</text>
</g>'''
    rawr = f'''<g opacity="0">
{pixel_text("RAWR", 470, 188, 4, "r")}
{animate_opacity("0;0;1;1;0;0", "5.5s", "0s", "0;0.48;0.52;0.62;0.68;1")}
</g>'''
    body = f'''{meadow_background(w, h)}
  {camp_glow}
  {plants}
  {extras}
  {fox}
  {dragon}
  {butterfly}
  {rawr}
  {fireflies([(120, 90, "3.2s"), (260, 60, "4s"), (540, 80, "3.6s"), (800, 100, "4.4s"), (880, 140, "3s")])}
  {caption}
'''
    write(
        OUT / "dragon" / "pixel-dragon.svg",
        svg_wrap(
            w,
            h,
            "Pixel dragon breathing fire",
            "A cute pixel-art dragon on a warm evening hill, breathing looping fire beside a fox, campfire, and tea.",
            body,
        ),
    )


def build_tiny_dragon() -> None:
    w, h = 280, 160
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
{sitting_dragon(54, 36, 7, napping=False)}
{pixel_text("MUXBY", 86, 138, 4, "d")}
'''
    write(
        OUT / "dragon" / "pixel-dragon-tiny.svg",
        svg_wrap(w, h, "Tiny atelier dragon", "A sitting pixel dragon mascot on warm paper.", body),
    )


def build_napping() -> None:
    w, h = 900, 110
    body = f'''  <rect width="{w}" height="{h}" rx="18" fill="#F4EBD8"/>
  <rect x="3" y="3" width="{w-6}" height="{h-6}" rx="16" fill="none" stroke="#C4A574" stroke-width="2"/>
{sitting_dragon(28, 18, 4, napping=True)}
{fox_group(140, 48, 3)}
  <g font-family="Georgia, 'Times New Roman', serif" fill="#3A2418">
    <text x="250" y="48" font-size="20">workshop is open. dragon is on break.</text>
    <text x="250" y="76" font-size="13" fill="#6B4A32">Please leave a biscuit on the sill. Fire-breathing resumes after tea.</text>
  </g>
'''
    write(
        OUT / "atelier" / "napping-banner.svg",
        svg_wrap(w, h, "Dragon napping banner", "A paper workshop sign with a napping pixel dragon and fox.", body),
    )


def build_hero() -> None:
    w, h = 1200, 390
    size = 6
    body = f'''  <rect width="{w}" height="{h}" fill="#2A211A"/>
  <rect x="48" y="28" width="1104" height="334" fill="url(#duskSky)"/>
  <!-- window frame -->
  <rect x="48" y="28" width="1104" height="334" fill="none" stroke="#5C3A24" stroke-width="18"/>
  <rect x="590" y="28" width="18" height="334" fill="#5C3A24"/>
  <rect x="48" y="186" width="1104" height="14" fill="#5C3A24"/>
  <rect x="48" y="28" width="1104" height="22" fill="#6B4A32"/>
  <!-- sill -->
  <rect x="32" y="348" width="1136" height="22" fill="#8A5A38"/>
  <rect x="24" y="366" width="1152" height="18" fill="#4A3224"/>
  <!-- left pane: evening hills -->
  <path d="M66 186 C 160 150, 260 168, 360 170 C 460 172, 530 150, 590 168 L590 186 L66 186 Z" fill="#8AA078" opacity=".9"/>
  <path d="M66 186 C 180 176, 300 196, 590 186 L590 348 L66 186 Z" fill="#6F8F5E"/>
  <path d="M66 260 C 200 240, 340 268, 590 250 L590 348 L66 348 Z" fill="#4F6B45"/>
  <!-- right pane: lamp glow and desk -->
  <rect x="608" y="200" width="536" height="148" fill="#3A2A20"/>
  <ellipse cx="980" cy="248" rx="90" ry="70" fill="url(#lamp)">
    <animate attributeName="opacity" values=".55;.9;.55" dur="3.4s" repeatCount="indefinite"/>
  </ellipse>
  <rect x="860" y="268" width="18" height="80" fill="#C4A574"/>
  <path d="M848 268 Q869 248 890 268" fill="#F4EBD8" stroke="#C4A574" stroke-width="3"/>
  <rect x="640" y="300" width="200" height="48" fill="#5C3A24"/>
  <rect x="652" y="308" width="70" height="10" fill="#EDE3D0"/>
  <rect x="652" y="322" width="86" height="8" fill="#E8C49A"/>
  <rect x="652" y="334" width="54" height="6" fill="#C4A574"/>
{dragon_group(680, 214, size, fire=True, bob=True)}
{fox_group(96, 286, 4)}
{rle_rects(TEACUP, 1088, 312, 4)}
{rle_rects(STAR, 140, 70, 4)}
{rle_rects(STAR, 420, 88, 3)}
{rle_rects(STAR, 980, 70, 4)}
{rle_rects(STAR, 860, 96, 3)}
{fireflies([(220, 90, "3.5s"), (340, 60, "4.2s"), (760, 80, "3.8s"), (1040, 100, "4.6s")])}
  <g font-family="Georgia, 'Times New Roman', serif" text-anchor="middle">
    <text x="328" y="86" fill="#3A2418" font-size="42">Mubeen</text>
    <text x="328" y="118" fill="#6B4A32" font-size="16">software, systems, and a small fire-breathing dragon</text>
  </g>
  <g font-family="Georgia, 'Times New Roman', serif" fill="#F4EBD8">
    <text x="876" y="236" font-size="15">the atelier window</text>
  </g>
'''
    write(
        OUT / "atelier" / "hero.svg",
        svg_wrap(
            w,
            h,
            "Muxby atelier window",
            "A warm dusk window with a pixel dragon on the sill, a fox on the hill, and a paper lantern.",
            body,
        ),
    )


def build_garden() -> None:
    w, h = 920, 360
    plants = [
        ("PYTHON", 70, 0.86, "#6F8F5E"),
        ("TYPESCRIPT", 190, 0.8, "#4F6B45"),
        ("REACT", 320, 0.7, "#6F8F5E"),
        ("C++", 430, 0.62, "#8B3A22"),
        ("POSTGRES", 540, 0.74, "#4F6B45"),
        ("DOCKER", 660, 0.66, "#6B4A32"),
        ("PYTORCH", 780, 0.78, "#C45C32"),
    ]
    stems = []
    for i, (name, x, grow, color) in enumerate(plants):
        top = 80 + int((1 - grow) * 140)
        height = 280 - top
        delay = 0.2 * i
        stems.append(
            f'''<g>
  <rect x="{x+18}" y="{top}" width="8" height="{height}" fill="{color}">
    <animate attributeName="y" values="{top};{top-4};{top}" dur="3.4s" begin="{delay}s" repeatCount="indefinite"/>
  </rect>
  <ellipse cx="{x+22}" cy="{top+12}" rx="28" ry="18" fill="{color}">
    <animateTransform attributeName="transform" type="rotate" values="0 {x+22} {top+12}; 6 {x+22} {top+12}; -6 {x+22} {top+12}; 0 {x+22} {top+12}" dur="4s" begin="{1.8+delay}s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="{x+6}" cy="{top+22}" rx="16" ry="12" fill="#8AA078"/>
  <ellipse cx="{x+38}" cy="{top+24}" rx="16" ry="12" fill="#4F6B45"/>
  {pixel_text(name, x - 4, 304, 3, "p")}
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <rect x="24" y="22" width="{w-48}" height="{h-44}" rx="16" fill="#F6EFE4" filter="url(#softPaper)"/>
  <text x="460" y="54" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="20" fill="#3A2418">the skill garden</text>
  <text x="460" y="76" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12" fill="#6B4A32">things I tend, not a dashboard I perform</text>
  <rect x="48" y="286" width="824" height="14" rx="4" fill="#8B6E58"/>
  {"".join(stems)}
{sitting_dragon(20, 210, 4)}
{rle_rects(SNAIL, 860, 268, 4)}
{rle_rects(BUTTERFLY, 500, 96, 4)}
'''
    write(
        OUT / "atelier" / "garden.svg",
        svg_wrap(
            w,
            h,
            "Skill garden",
            "A paper garden of labeled plants representing languages and tools, with a sitting dragon gardener.",
            body,
        ),
    )


def build_kettle() -> None:
    w, h = 420, 280
    steam = []
    for i, x in enumerate((208, 230, 252)):
        steam.append(
            f'''<g fill="#D4C8B8" opacity="0">
  <ellipse cx="{x}" cy="70" rx="8" ry="12"/>
  {animate_opacity("0;0.7;0", f"{2.4 + i*0.2}s", f"{i*0.3}s")}
  <animateTransform attributeName="transform" type="translate" values="0 0; {(-8)+i*4} -40" dur="{2.4+i*0.2}s" begin="{i*0.3}s" repeatCount="indefinite"/>
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <text x="210" y="36" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="16" fill="#3A2418">now brewing</text>
  <ellipse cx="210" cy="210" rx="70" ry="14" fill="#C4A574" opacity=".35"/>
  <path d="M150 150 C150 110 270 110 270 150 L262 200 C262 226 158 226 158 200 Z" fill="#C45C32" stroke="#3A2418" stroke-width="3"/>
  <path d="M270 156 C318 156 318 198 268 198" fill="none" stroke="#3A2418" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="210" cy="128" rx="46" ry="10" fill="#8B3A22"/>
  <rect x="198" y="96" width="24" height="18" rx="3" fill="#8B3A22">
    <animateTransform attributeName="transform" type="rotate" values="0 210 114; -8 210 114; 6 210 114; 0 210 114" dur="1.2s" repeatCount="indefinite"/>
  </rect>
  {"".join(steam)}
  <text x="210" y="250" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="13" fill="#6B4A32">agentic systems, poured slowly</text>
{rle_rects(TEACUP, 320, 200, 5)}
'''
    write(
        OUT / "atelier" / "kettle.svg",
        svg_wrap(w, h, "Copper kettle brewing", "A copper kettle with bouncing lid and steam, labeled now brewing.", body),
    )


def build_lantern() -> None:
    w, h = 280, 300
    moths = []
    for i, (x, y) in enumerate(((70, 90), (200, 70), (160, 130))):
        moths.append(
            f'''<g fill="#E8C49A">
  <ellipse cx="{x}" cy="{y}" rx="6" ry="3">
    <animate attributeName="cx" values="{x};{x+16};{x-10};{x}" dur="{3.2+i}s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="{y};{y-12};{y+8};{y}" dur="{3.2+i}s" repeatCount="indefinite"/>
  </ellipse>
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <ellipse cx="140" cy="150" rx="70" ry="80" fill="url(#lamp)">
    <animate attributeName="opacity" values=".45;1;.45" dur="2.8s" repeatCount="indefinite"/>
  </ellipse>
{rle_rects(LANTERN_CORE, 92, 70, 8)}
  {"".join(moths)}
  <text x="140" y="270" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="14" fill="#3A2418">keep a light on</text>
'''
    write(
        OUT / "atelier" / "lantern.svg",
        svg_wrap(w, h, "Paper lantern", "A flickering paper lantern with moths on warm paper.", body),
    )


def build_mail() -> None:
    w, h = 520, 220
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <text x="260" y="34" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="16" fill="#3A2418">dragon post</text>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 20; 360 0; 0 20" dur="8s" repeatCount="indefinite"/>
{rle_rects(DRAGON_IDLE, 0, 70, 4)}
{rle_rects(ENVELOPE, 86, 92, 4)}
  </g>
  <text x="260" y="200" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12" fill="#6B4A32">letters travel at the speed of a polite dragon</text>
'''
    write(
        OUT / "atelier" / "mail.svg",
        svg_wrap(w, h, "Dragon delivering mail", "A pixel dragon flying a cream envelope across warm paper.", body),
    )


def build_koi_pond() -> None:
    w, h = 520, 220
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <ellipse cx="260" cy="120" rx="190" ry="70" fill="#C9D2B8"/>
  <ellipse cx="260" cy="120" rx="170" ry="56" fill="#9BB39A"/>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0; 40 8; 80 -6; 40 8; 0 0" dur="10s" repeatCount="indefinite"/>
{rle_rects(KOI, 160, 96, 5)}
  </g>
  <g>
    <animateTransform attributeName="transform" type="translate" values="80 16; 20 0; -10 10; 80 16" dur="12s" repeatCount="indefinite"/>
{rle_rects(KOI, 240, 110, 4)}
  </g>
  <circle cx="200" cy="100" r="4" fill="#F6EFE4" opacity=".5">
    <animate attributeName="r" values="3;9;3" dur="4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".5;0;.5" dur="4s" repeatCount="indefinite"/>
  </circle>
  <text x="260" y="204" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="13" fill="#3A2418">slow water, careful work</text>
'''
    write(
        OUT / "atelier" / "koi.svg",
        svg_wrap(w, h, "Koi pond", "Two pixel koi circling a sage pond on warm paper.", body),
    )


def build_dividers() -> None:
    vine_path = '''  <rect width="1200" height="64" fill="none"/>
  <path d="M20 40 C 140 8, 220 58, 340 32 C 460 6, 540 58, 660 30 C 780 4, 860 58, 980 28 C 1080 10, 1140 44, 1180 36" fill="none" stroke="#6F8F5E" stroke-width="3" stroke-linecap="round">
    <animate attributeName="stroke-dasharray" values="0 1200;1200 0" dur="3.2s" fill="freeze"/>
  </path>
'''
    leaves = []
    for i, x in enumerate(range(80, 1160, 90)):
        y = 28 + (8 if i % 2 else -8)
        leaves.append(
            f'''<ellipse cx="{x}" cy="{y}" rx="10" ry="6" fill="#6F8F5E">
  <animateTransform attributeName="transform" type="rotate" values="0 {x} {y}; 8 {x} {y}; -8 {x} {y}; 0 {x} {y}" dur="4s" begin="{1+i*0.1}s" repeatCount="indefinite"/>
</ellipse>'''
        )
    write(
        OUT / "atelier" / "divider-vine.svg",
        svg_wrap(1200, 64, "Vine divider", "A sage vine that draws itself across the page.", vine_path + "\n".join(leaves)),
    )

    flies = [fireflies([(x, 22, f"{3 + (i % 5) * 0.3}s") for i, x in enumerate(range(60, 1160, 70))])]
    write(
        OUT / "atelier" / "divider-fireflies.svg",
        svg_wrap(
            1200,
            48,
            "Firefly divider",
            "Warm fireflies drifting in a line.",
            f'  <rect width="1200" height="48" fill="none"/>\n{flies[0]}',
        ),
    )

    paw = pad([".kk.", "kkkk", ".kk."])
    prints = []
    for i, x in enumerate(range(40, 1160, 70)):
        y = 18 if i % 2 == 0 else 26
        prints.append(
            f'''<g opacity="0">
{rle_rects(paw, x, y, 4)}
{animate_opacity("0;1", "0.2s", f"{i*0.12}s")}
</g>'''
        )
        # freeze after appear: use fill freeze via values
        prints[-1] = (
            f'<g opacity="1">\n{rle_rects(paw, x, y, 4)}\n'
            f'<animate attributeName="opacity" values="0.35;1;0.35" dur="2.8s" begin="{i*0.18}s" repeatCount="indefinite"/>\n</g>'
        )
    write(
        OUT / "atelier" / "divider-paws.svg",
        svg_wrap(1200, 56, "Pawprint divider", "Fox and dragon pawprints walking across the page.", "  <rect width='1200' height='64' fill='none'/>\n" + "".join(prints)),
    )


def build_postcard() -> None:
    w, h = 640, 360
    body = f'''  <rect width="{w}" height="{h}" fill="#E8C49A"/>
  <rect x="18" y="18" width="604" height="324" fill="#F6EFE4" filter="url(#softPaper)"/>
  <path d="M330 18 L330 342" stroke="#C4A574" stroke-dasharray="4 8"/>
  <text x="174" y="58" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="22" fill="#3A2418">hello from the sill</text>
  <text x="40" y="96" font-family="Georgia, 'Times New Roman', serif" font-size="13" fill="#6B4A32">
    <tspan x="40" dy="0">I build software the way I keep a desk:</tspan>
    <tspan x="40" dy="22">warm light, sharp tools, and one</tspan>
    <tspan x="40" dy="22">creature who is allowed to scorch</tspan>
    <tspan x="40" dy="22">the drafts that do not deserve to live.</tspan>
    <tspan x="40" dy="28">Pakistan. Still learning. Still shipping.</tspan>
  </text>
{sitting_dragon(70, 230, 5)}
{rle_rects(WAX_STAMP, 400, 48, 8)}
  <text x="478" y="70" font-family="Georgia, 'Times New Roman', serif" font-size="18" fill="#F6EFE4">M</text>
  <rect x="380" y="160" width="210" height="8" fill="#C4A574" opacity=".5"/>
  <rect x="380" y="184" width="210" height="8" fill="#C4A574" opacity=".5"/>
  <rect x="380" y="208" width="160" height="8" fill="#C4A574" opacity=".5"/>
  <text x="486" y="250" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12" fill="#6B4A32">muxby · atelier</text>
  <text x="486" y="310" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="11" fill="#8B3A22">stamp of a finished thought</text>
'''
    write(
        OUT / "atelier" / "postcard.svg",
        svg_wrap(w, h, "Hello postcard", "A cream postcard with a wax M seal and a sitting dragon.", body),
    )


def build_quote() -> None:
    w, h = 720, 160
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <rect x="20" y="18" width="{w-40}" height="{h-36}" fill="#F6EFE4" filter="url(#softPaper)"/>
  <ellipse cx="86" cy="78" rx="18" ry="26" fill="#6F8F5E" opacity=".9"/>
  <ellipse cx="78" cy="70" rx="8" ry="14" fill="#4F6B45"/>
  <text x="360" y="78" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="16" fill="#3A2418">Build something this week that a future teammate</text>
  <text x="360" y="104" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="16" fill="#3A2418">will be glad still exists.</text>
'''
    write(
        OUT / "atelier" / "quote.svg",
        svg_wrap(w, h, "Pressed-flower quote", "A paper card with a pressed sage leaf and a working principle.", body),
    )


def build_fire_closeup() -> None:
    w, h = 640, 280
    size = 10
    body = f'''  <rect width="{w}" height="{h}" fill="#F4EBD8"/>
  <rect x="16" y="16" width="{w-32}" height="{h-32}" rx="18" fill="#F6EFE4" filter="url(#softPaper)"/>
  <text x="320" y="42" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="18" fill="#3A2418">ember, on purpose</text>
{dragon_group(48, 70, size, fire=True)}
{pixel_text("FIRE PLEASE", 430, 232, 4, "d")}
'''
    write(
        OUT / "dragon" / "pixel-dragon-fire.svg",
        svg_wrap(
            w,
            h,
            "Pixel dragon breathing fire, close",
            "A large cute pixel dragon with a constant ember and looping fire breath.",
            body,
        ),
    )


def build_stickers() -> None:
    w, h = 920, 300
    pins = [
        (70, 80, "#C45C32", "PY"),
        (200, 70, "#6F8F5E", "TS"),
        (330, 86, "#8B3A22", "C++"),
        (460, 68, "#6B4A32", "GO"),
        (590, 80, "#C45C32", "SQL"),
        (720, 74, "#6F8F5E", "REACT"),
        (120, 170, "#8B6E58", "NODE"),
        (260, 180, "#4F6B45", "PG"),
        (400, 166, "#C45C32", "K8S"),
        (540, 176, "#6B4A32", "AWS"),
        (680, 170, "#C4897A", "LLM"),
        (800, 160, "#4F6B45", "GIT"),
    ]
    badges = []
    for i, (x, y, color, label) in enumerate(pins):
        badges.append(
            f'''<g>
  <animateTransform attributeName="transform" type="translate" values="0 0; 0 {-3}; 0 0" dur="{3.2 + i*0.11}s" repeatCount="indefinite"/>
  <circle cx="{x+40}" cy="{y+28}" r="38" fill="{color}"/>
  <circle cx="{x+40}" cy="{y+28}" r="32" fill="#F6EFE4"/>
  <circle cx="{x+40}" cy="{y+28}" r="28" fill="{color}" opacity=".16"/>
  {pixel_text(label, x + 40 - len(label)*8, y + 20, 4, "p")}
</g>'''
        )
    body = f'''  <rect width="{w}" height="{h}" fill="#E8C49A"/>
  <rect x="20" y="16" width="{w-40}" height="{h-32}" fill="#EDE3D0" filter="url(#softPaper)"/>
  <text x="460" y="48" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="18" fill="#3A2418">enamel pins from the workbench</text>
  {"".join(badges)}
'''
    write(
        OUT / "atelier" / "stickers.svg",
        svg_wrap(w, h, "Enamel sticker sheet", "A kraft sheet of enamel-style technology pins on warm paper.", body),
    )


def main() -> None:
    build_dragon_camp()
    build_tiny_dragon()
    build_fire_closeup()
    build_napping()
    build_hero()
    build_garden()
    build_kettle()
    build_lantern()
    build_mail()
    build_koi_pond()
    build_dividers()
    build_postcard()
    build_quote()
    build_stickers()


if __name__ == "__main__":
    main()
