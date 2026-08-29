# SETUP GUIDE — MUXBY PROFILE

Everything here is wired for the GitHub username **`muxby`** (this repo is `muxby/muxby`,
the special profile repository). The visual system is **Twilight Garden**: deep indigo
night, ivory plaques, brass, sage, and an amber lantern glow. It is deliberately not
neon, not a cockpit, and not a dashboard.

---

## 1. What's in the box

| File | Purpose |
|---|---|
| `README.md` | The profile itself |
| `assets/atelier/hero.svg` | Window at dusk with the dragon on the sill |
| `assets/atelier/roadmap.svg` | **The roadmap** — lantern-lit stations, legend, you-are-here |
| `assets/atelier/trail.svg` | The same route as a night walk |
| `assets/atelier/postcard.svg` | Short intro card |
| `assets/atelier/wax-seal.svg` | Ember and brass M seal |
| `assets/atelier/corkboard.svg` | Pinned stack notes (ink on ivory, readable) |
| `assets/atelier/garden.svg` | Skill garden — plants, not charts |
| `assets/atelier/kettle.svg` | Kettle and steam |
| `assets/atelier/lantern.svg` | Lantern and moths |
| `assets/atelier/koi.svg` | Koi pond |
| `assets/atelier/mail.svg` | Dragon post |
| `assets/atelier/desk.svg` | Polaroid on a walnut desk |
| `assets/atelier/stickers.svg` | Enamel pin sheet |
| `assets/atelier/napping-banner.svg` | Tea-break sign |
| `assets/atelier/quote.svg` | Quote card |
| `assets/atelier/signature.svg` | Brass signature (readable in light and dark) |
| `assets/atelier/divider-*.svg` | Vine, fireflies, pawprints |
| `assets/dragon/pixel-dragon.svg` | Hill scene, fire-breathing pixel dragon |
| `assets/dragon/pixel-dragon-fire.svg` | Close-up fire breath |
| `assets/dragon/pixel-dragon-tiny.svg` | Sitting mascot |
| `scripts/build_atelier.py` | Regenerates the pixel scenes from sprite tables |
| `.github/workflows/snake.yml` | Contribution snake to the `output` branch |

Older filenames (`hero-banner.svg`, `constellation.svg`, `hologram.svg`, `graph-*.svg`,
`odyssey.svg`, and the circuit/glitch dividers) are copies of current artwork so stale
links cannot resurrect the old neon theme.

## 2. Color system ("Twilight Garden")

| Token | Hex | Reserved for |
|---|---|---|
| Night | `#141D2B` | scene backgrounds |
| Night panel | `#1B2738` / `#22303F` | raised panels, plaques on dark |
| Ivory | `#F0EADC` | note cards, anything with text |
| Moon | `#FBF6E9` | the highlighted plaque, moon |
| Parchment | `#DFD5C1` | secondary cards |
| Ink | `#22303F` | **all body text sits on ivory, never on night** |
| Ink soft | `#5C6B78` | captions on ivory |
| Brass | `#C8A868` / `#8C7442` | rails, frames, signature |
| Sage | `#7E9A72` / `#4C6650` | foliage, "next" and "later" markers |
| Amber | `#EDAE49` | lantern glow, current station |
| Ember | `#E2703A` / `#B4472A` | fire, wax seal, accents |
| Rose | `#C08E86` | quiet accent |

Never reintroduce `#00F5FF`, `#FF00E5`, `#9D4EDD`, or `#0D1117`. Fire and the lantern
are the only things allowed to be loud.

## 3. Regenerating pixel scenes

```bash
python3 scripts/build_atelier.py
```

Sprites live at the top of that file (`DRAGON_*`, `FOX_SIT`, fire frames) and colors come
from the `PALETTE` dict, so a theme change is a palette edit, not a sprite rewrite.
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

## 5. Activation checklist

1. Merge to the default branch of `<username>/<username>`.
2. Enable Actions with read and write permissions.
3. Run **Generate Contribution Snake**; it publishes to the `output` branch.

## 6. External services

`shields.io` · `readme-typing-svg.demolab.com` · `komarev.com` · `Platane/snk`

All are free image services. If one is down, only that piece degrades.

---

<sub>Keep text on ivory. If you cannot read it, the plaque is in the wrong place.</sub>
