#!/usr/bin/env python3
"""The type system for the profile artwork.

One display serif, one grotesque, one mono, and a single scale that every asset
draws from. See SETUP.md for the scale table and the reasoning.

Why outlines. These SVGs are embedded in README.md with <img src="...">, and
GitHub renders them in an isolated context where external web fonts never load:
@font-face, @import and a <link> to Google Fonts all fail silently and fall back
to whatever the viewer happens to have. So display type and the small uppercase
labels are shaped here and emitted as glyph outlines, which render identically
for everyone and never depend on the reader's installed fonts.

Why not outlines everywhere. Outlined lowercase costs roughly 450 bytes a glyph,
so pushing running copy through it would add close to a megabyte across the
README. Body copy stays as real <text> in a curated stack led by the same
families, which also keeps it selectable, translatable, and searchable.

Fonts are Noto Serif Display, Inter, and JetBrains Mono, all under the SIL Open
Font License. Only the outlines of the glyphs actually used are embedded.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path("/usr/share/fonts/truetype")

FACES = {
    "serif": FONT_DIR / "noto/NotoSerifDisplay-Regular.ttf",
    "serif-bold": FONT_DIR / "noto/NotoSerifDisplay-Bold.ttf",
    "serif-italic": FONT_DIR / "noto/NotoSerifDisplay-Italic.ttf",
    "sans": FONT_DIR / "macos/Inter-Regular.ttf",
    "sans-medium": FONT_DIR / "macos/Inter-Medium.ttf",
    "sans-semibold": FONT_DIR / "macos/Inter-SemiBold.ttf",
    "sans-bold": FONT_DIR / "macos/Inter-Bold.ttf",
    "mono": FONT_DIR / "jetbrains-mono/JetBrainsMono-Medium.ttf",
    "mono-bold": FONT_DIR / "jetbrains-mono/JetBrainsMono-Bold.ttf",
}

# Fallbacks for the <text> elements that stay live. Ordered so the first hit on
# each platform is a face that belongs next to the outlined display type.
STACKS = {
    "serif": (
        "'Noto Serif Display','Iowan Old Style','Palatino Linotype',Palatino,"
        "'Book Antiqua',Georgia,'Times New Roman',serif"
    ),
    "sans": (
        "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',"
        "Helvetica,Arial,sans-serif"
    ),
    "mono": (
        "'JetBrains Mono','SF Mono',ui-monospace,Menlo,Consolas,"
        "'DejaVu Sans Mono',monospace"
    ),
}

WEIGHTS = {"": 400, "medium": 500, "semibold": 600, "bold": 700, "italic": 400}


@dataclass(frozen=True)
class Style:
    face: str           # key into FACES
    size: float         # user units
    tracking: float     # letter-spacing, in em
    caps: bool = False  # uppercase the string before shaping


# The scale. Sizes are for artwork at its natural viewBox size; the README scales
# the images down, so nothing here renders larger than it reads.
#
# Display type is set in caps with wide tracking, which is what carries the
# editorial feel; running copy is the grotesque at its natural spacing; technical
# labels are the mono so they read as identifiers rather than prose.
SCALE = {
    "hero": Style("serif", 44, 0.22, caps=True),        # the one name on the page
    "plate": Style("serif", 20, 0.30, caps=True),       # scene and card titles
    "heading": Style("serif", 18, 0.0),                 # sentence-case display
    "eyebrow": Style("sans-semibold", 11, 0.22, caps=True),   # standfirst under a plate
    "label": Style("sans-semibold", 11, 0.16, caps=True),     # small caps callouts
    "lede": Style("sans", 15, 0.0),                     # card body, one step up
    "body": Style("sans", 13, 0.0),                     # running copy
    "caption": Style("sans", 11.5, 0.005),              # smallest live text
    "tag": Style("mono-bold", 12, 0.08, caps=True),     # tags and medallions
    "micro": Style("mono-bold", 9.5, 0.12, caps=True),  # tightest technical label
    "wordmark": Style("serif-bold", 20, 0.22, caps=True),
}


def style(role: str, **over) -> Style:
    """A scale entry, optionally nudged for one call site."""
    base = SCALE[role]
    return Style(
        over.get("face", base.face),
        over.get("size", base.size),
        over.get("tracking", base.tracking),
        over.get("caps", base.caps),
    )


# ---------------------------------------------------------------------------
# Shaping
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _font(face: str):
    path = FACES[face]
    if not path.exists():
        raise FileNotFoundError(
            f"missing font for face {face!r}: {path}. Install the Noto Serif "
            "Display, Inter, and JetBrains Mono TrueType files before rebuilding."
        )
    tt = TTFont(str(path), fontNumber=0)
    hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    return tt, tt.getGlyphSet(), tt.getGlyphOrder(), tt["head"].unitsPerEm, hb_font


def _num(v: float) -> str:
    # A tenth of a user unit is far below one rendered pixel here, and rounding
    # there rather than at two decimals cuts the emitted path data by a sixth.
    s = f"{v:.1f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


@lru_cache(maxsize=None)
def _shape(text: str, face: str) -> tuple[tuple[str, float, float, float], ...]:
    """Shape one run into (glyph name, x offset, y offset, advance), font units."""
    _tt, _gs, order, _upm, hb_font = _font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    # JetBrains Mono ships coding ligatures that would fuse "++" into one arrow.
    ligatures = not face.startswith("mono")
    hb.shape(hb_font, buf, {"kern": True, "liga": ligatures, "clig": ligatures, "calt": ligatures})
    out = []
    pen = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append(
            (order[info.codepoint], pen + pos.x_offset, float(pos.y_offset), float(pos.x_advance))
        )
        pen += pos.x_advance
    return tuple(out)


def measure(text: str, role: str, **over) -> float:
    """Rendered advance width of `text` in user units."""
    st = style(role, **over)
    body = text.upper() if st.caps else text
    shaped = _shape(body, st.face)
    if not shaped:
        return 0.0
    _tt, _gs, _order, upm, _hb = _font(st.face)
    units = sum(g[3] for g in shaped)
    # Tracking sits between glyphs, so the last glyph adds no trailing space.
    return units * st.size / upm + st.tracking * st.size * (len(shaped) - 1)


def cap_height(role: str, **over) -> float:
    """Height of the capitals in user units, for fitting type into a fixed box."""
    st = style(role, **over)
    tt, _gs, _order, upm, _hb = _font(st.face)
    caps = getattr(tt["OS/2"], "sCapHeight", 0) or int(upm * 0.7)
    return caps * st.size / upm


def fit(text: str, role: str, max_width: float, **over) -> dict:
    """Overrides that shrink `role` until `text` fits `max_width`.

    Width is exactly proportional to size, tracking included, so one step lands
    it. Used wherever a label has to sit inside a tag, medallion, or card.
    """
    width = measure(text, role, **over)
    if width <= max_width or width == 0:
        return dict(over)
    out = dict(over)
    out["size"] = style(role, **over).size * max_width / width
    return out


# ---------------------------------------------------------------------------
# Outlined type
# ---------------------------------------------------------------------------

def _anchor_shift(width: float, anchor: str) -> float:
    if anchor == "middle":
        return -width / 2
    if anchor == "end":
        return -width
    return 0.0


def outline(
    text: str,
    role: str,
    x: float,
    y: float,
    fill: str,
    anchor: str = "start",
    opacity: str | None = None,
    max_width: float | None = None,
    **over,
) -> str:
    """One <path> holding the glyph outlines for `text`, baseline at `y`.

    Anchoring is resolved here from the shaped width rather than left to the
    renderer, which is also why tracked centred type comes out optically centred.
    """
    if max_width is not None:
        over = fit(text, role, max_width, **over)
    st = style(role, **over)
    body = text.upper() if st.caps else text
    shaped = _shape(body, st.face)
    if not shaped:
        return ""
    _tt, glyph_set, _order, upm, _hb = _font(st.face)
    scale = st.size / upm
    track = st.tracking * st.size
    x += _anchor_shift(measure(text, role, **over), anchor)

    parts: list[str] = []
    for i, (name, gx, gy, _adv) in enumerate(shaped):
        pen = SVGPathPen(glyph_set, ntos=_num)
        at = Transform(scale, 0, 0, -scale, x + gx * scale + i * track, y - gy * scale)
        glyph_set[name].draw(TransformPen(pen, at))
        d = pen.getCommands()
        if d:
            parts.append(d)
    if not parts:
        return ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    # The generated scenes set shape-rendering="crispEdges" for the pixel art, so
    # curves have to opt back out of it or the letterforms come out jagged.
    return (
        f'<path d="{"".join(parts)}" fill="{fill}"{op} '
        f'shape-rendering="geometricPrecision" role="img" aria-label="{_escape(text)}"/>'
    )


# ---------------------------------------------------------------------------
# Live <text>
# ---------------------------------------------------------------------------

def text_attrs(role: str, anchor: str = "start", **over) -> str:
    """Presentation attributes for a <text> element in the given role.

    SVG letter-spacing is a length in user units, not em, so tracking is resolved
    against the size here.
    """
    st = style(role, **over)
    family = STACKS[st.face.split("-")[0]]
    variant = st.face.partition("-")[2]
    bits = [f'font-family="{family}"', f'font-size="{st.size:g}"']
    weight = WEIGHTS.get(variant, 400)
    if weight != 400:
        bits.append(f'font-weight="{weight}"')
    if variant == "italic":
        bits.append('font-style="italic"')
    if st.tracking:
        bits.append(f'letter-spacing="{st.tracking * st.size:g}"')
    if anchor != "start":
        bits.append(f'text-anchor="{anchor}"')
    bits.append('text-rendering="geometricPrecision"')
    return " ".join(bits)


def optical_x(x: float, role: str, anchor: str = "start", **over) -> float:
    """Correct `x` for the trailing letter-space renderers add to a tracked run.

    A centred run tracked by t measures t wider than it looks and so lands half a
    step left of where it belongs. Outlined type resolves its own anchoring and
    never needs this.
    """
    st = style(role, **over)
    if not st.tracking or anchor == "start":
        return x
    track = st.tracking * st.size
    return x + (track / 2 if anchor == "middle" else track)


def text_el(
    text: str,
    role: str,
    x: float,
    y: float,
    fill: str,
    anchor: str = "start",
    **over,
) -> str:
    """A live <text> element carrying running copy in the given role."""
    st = style(role, **over)
    body = text.upper() if st.caps else text
    return (
        f'<text x="{_num(optical_x(x, role, anchor, **over))}" y="{_num(y)}" '
        f'{text_attrs(role, anchor, **over)} fill="{fill}">{_escape(body)}</text>'
    )
