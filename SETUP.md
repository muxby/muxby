# SETUP GUIDE - MUXBY PROFILE

Everything here is wired for the GitHub username **`muxby`** (this repo is `muxby/muxby`,
the special profile repository). The visual system is **Obsidian Forge**: graphite and
iron, bone plaques, brass hardware, one ember accent, and a cold patina secondary. It is
deliberately not neon, not a cockpit, not a dashboard, and not a nursery.

---

## 1. What's in the box

| File | Purpose |
|---|---|
| `README.md` | The profile itself, centered end to end |
| `assets/atelier/hero.svg` | Studio window at night with the dragon on the sill |
| `assets/atelier/roadmap.svg` | **The roadmap** - brass rail, stations, legend, you-are-here |
| `assets/atelier/trail.svg` | The same route as a night walk |
| `assets/atelier/postcard.svg` | Short calling card |
| `assets/atelier/wax-seal.svg` | Ember and brass M seal |
| `assets/atelier/corkboard.svg` | Workbench cards (ink on bone, aligned grid) |
| `assets/atelier/kettle.svg` | Iron kettle and steam |
| `assets/atelier/lantern.svg` | Brass lantern and drifting embers |
| `assets/atelier/ember.svg` | Dish of banked embers |
| `assets/atelier/mail.svg` | Dragon post |
| `assets/atelier/desk.svg` | Polaroid on an iron desk |
| `assets/atelier/stickers.svg` | Forged medallion sheet |
| `assets/atelier/napping-banner.svg` | Break sign |
| `assets/atelier/quote.svg` | Quote card |
| `assets/atelier/signature.svg` | Brass signature |
| `assets/atelier/divider-rule.svg` | Brass hairline rule with a diamond |
| `assets/atelier/divider-ember.svg` | Ember spark rule |
| `assets/atelier/garden.svg` | Tool rack of etched brass tags (kept for old links) |
| `assets/dragon/pixel-dragon.svg` | Night ridge, fire-breathing pixel dragon |
| `assets/dragon/pixel-dragon-fire.svg` | Close-up fire breath |
| `assets/dragon/pixel-dragon-tiny.svg` | Sitting mascot |
| `scripts/build_atelier.py` | Regenerates the pixel scenes from sprite tables |
| `scripts/sprite_lab.py` | Rasterizes a sprite table to a big PNG in `/tmp` |
| `.github/workflows/snake.yml` | Contribution snake to the `output` branch |

Older filenames (`hero-banner.svg`, `constellation.svg`, `hologram.svg`, `graph-*.svg`,
`odyssey.svg`, `koi.svg`, the vine/firefly/paw dividers, and the circuit/glitch dividers)
are copies of current artwork so stale links cannot resurrect an old theme.

## 2. Color system ("Obsidian Forge")

Five families: neutrals go dark, text goes light, brass is the hardware, ember is the only
loud thing, patina is the one cold note.

| Token | Hex | Reserved for |
|---|---|---|
| Obsidian | `#0F1013` | outermost background, sprite-free deep field |
| Graphite | `#17181C` | scene backgrounds |
| Slate | `#1E2026` | raised panels on graphite |
| Iron | `#2A2D35` | panel fills, hardware bodies |
| Steel | `#3A3E48` | quiet strokes and rules on dark |
| Smoke | `#6B7078` | smoke, tertiary strokes |
| Mute | `#9AA0AC` | **secondary text on dark only** |
| Bone | `#E9E6DF` | plaques and cards, primary text on dark |
| Chalk | `#F7F5F0` | the highlighted plaque, brightest text |
| Ash | `#C6C2B8` | secondary cards |
| Ink | `#1B1D22` | **all body text on bone or ash** |
| Ink soft | `#4E535D` | captions on bone or ash |
| Brass | `#C9A227` | rails, frames, metal, signature, kickers |
| Brass dark | `#8A6E1F` | brass shadow, hardware, hairlines |
| Gold | `#F2C14E` | lamp and lantern light, current station |
| Ember | `#E4572E` | fire, seal, you-are-here, the one hot accent |
| Ember deep | `#A33418` | fire shadow, deep clay |
| Patina | `#3F6B62` | cold secondary, "later" markers |
| Patina light | `#6E9C90` | cold secondary light, "next" markers, foliage |

Contrast rule: light on deep, or dark on bone. Never mid-tone on mid-tone. Never
reintroduce `#00F5FF`, `#FF00E5`, `#9D4EDD`, or `#0D1117`. No pastels: no cream page, no
peach sky, no blush pink, no soft sage. Fire and the lantern are the only loud things.

Shape rule: hard edges. Corner radius stays at 0 to 3, drop shadows stay tight and near
black, and props stay tools rather than toys.

## 3. Regenerating pixel scenes

```bash
python3 scripts/build_atelier.py
```

Sprites live at the top of that file (`DRAGON_*`, `FOX_SIT`, fire frames) and colors come
from the `PALETTE` dict, so a theme change is a palette edit, not a sprite rewrite. Note
that `PALETTE["k"]` is the sprite outline only; body text fills are separate literals
inside each `build_*()` function, so recolor per scene rather than by global replace.

`scripts/sprite_lab.py` rasterizes a sprite to a large PNG in `/tmp` so pixel work can be
checked by eye.

Hand-drawn pieces (roadmap, trail, corkboard, desk, wax seal, signature) are plain SVG
files under `assets/atelier/` and are edited directly.

## 4. Find-and-replace values

| Placeholder | Replace with |
|---|---|
| `muxby` in widget URLs | your GitHub username |
| The Selected work table | your repositories |
| Station labels in `roadmap.svg` | your actual roadmap |
| QR images in `assets/` | your own codes |

## 5. Centering

GitHub strips `style="text-align:center"`. Use `align="center"` attributes instead:
`<div align="center">` for sections, `<h3 align="center">` for headings, and
`<table align="center">` for tables. HTML tables are used for the work list and the
Now strip so the table box itself centers, not only the cell text.

## 6. Activation checklist

1. Merge to the default branch of `<username>/<username>`.
2. Enable Actions with read and write permissions.
3. Run **Generate Contribution Snake**; it publishes to the `output` branch.

## 7. External services

`shields.io` / `readme-typing-svg.demolab.com` / `komarev.com` / `Platane/snk`

All are free image services. If one is down, only that piece degrades.

---

<sub>Keep text on bone. If you cannot read it, the plaque is in the wrong place.</sub>
