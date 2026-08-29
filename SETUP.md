# SETUP GUIDE — MUXBY ATELIER

Everything in this repo is wired for the GitHub username **`muxby`** (this repo is
`muxby/muxby`, the special profile repository). The visual system is **Ember Atelier**:
warm paper, terracotta, sage, and walnut ink. It is deliberately not neon, not a
cockpit, and not a constellation in the void.

---

## 1. What's in the box

| File | Purpose |
|---|---|
| `README.md` | The profile itself |
| `assets/atelier/hero.svg` | Dusk window with the dragon on the sill |
| `assets/atelier/postcard.svg` | Hello postcard and wax-seal story |
| `assets/atelier/wax-seal.svg` | Terracotta M seal |
| `assets/atelier/corkboard.svg` | Pinned notes for the stack (readable ink on cream) |
| `assets/atelier/garden.svg` | Skill garden — plants, not charts |
| `assets/atelier/trail.svg` | Storybook learning trail |
| `assets/atelier/kettle.svg` | Copper kettle, now brewing |
| `assets/atelier/lantern.svg` | Paper lantern and moths |
| `assets/atelier/koi.svg` | Slow koi pond |
| `assets/atelier/mail.svg` | Dragon post |
| `assets/atelier/desk.svg` | Polaroid on a walnut desk |
| `assets/atelier/stickers.svg` | Enamel pin sheet |
| `assets/atelier/napping-banner.svg` | Workshop / tea-break sign |
| `assets/atelier/quote.svg` | Pressed-leaf quote card |
| `assets/atelier/signature.svg` | Walnut-ink signature |
| `assets/atelier/divider-vine.svg` | Self-drawing sage vine |
| `assets/atelier/divider-fireflies.svg` | Fireflies |
| `assets/atelier/divider-paws.svg` | Pawprints |
| `assets/dragon/pixel-dragon.svg` | Hill scene, fire-breathing pixel dragon |
| `assets/dragon/pixel-dragon-fire.svg` | Close-up looping fire breath |
| `assets/dragon/pixel-dragon-tiny.svg` | Sitting mascot |
| `scripts/build_atelier.py` | Regenerates the pixel scenes from sprites |
| `.github/workflows/snake.yml` | Contribution snake → `output` branch |

Older filenames (`hero-banner.svg`, `constellation.svg`, `hologram.svg`, `graph-*.svg`,
and the circuit/glitch/odyssey files) now point at atelier artwork so leftover links
do not resurrect the neon palette.

## 2. Color system ("Ember Atelier")

| Token | Hex | Reserved for |
|---|---|---|
| Walnut | `#1C1510` | window frames, never body text on dark HUD |
| Leather | `#2A211A` | frames |
| Paper | `#F4EBD8` / `#F6EFE4` | cards, readable surfaces |
| Ink | `#3A2418` | all body text on paper |
| Terracotta | `#C45C32` | dragon, pins, languages |
| Ember | `#E07A3D` | fire, kettle |
| Sage | `#6F8F5E` | vines, hills, web/infra |
| Brass | `#B08D62` | quiet metal, not trophy gold |
| Blush | `#C4897A` | fox, koi, intelligence pins |

Do not reintroduce `#00F5FF`, `#FF00E5`, `#9D4EDD`, or `#0D1117` as a "premium" dark.
Those were the previous theme's problem. Text goes on cream. Fire is the only thing
that is allowed to be loud.

## 3. Regenerating pixel scenes

```bash
python3 scripts/build_atelier.py
```

Sprites live at the top of that file (`DRAGON_IDLE`, `DRAGON_SIT`, `FOX_SIT`, fire frames).
Editorial pieces (corkboard, trail, wax seal, signature, desk) are hand-drawn SVGs
under `assets/atelier/`.

## 4. Find-and-replace values

| Placeholder | Replace with |
|---|---|
| `muxby` in widget URLs | your GitHub username |
| Project table in the README | your real repositories |
| QR images in `assets/` | your own codes |

## 5. Activation checklist

1. Merge to the default branch of `<username>/<username>`.
2. Enable Actions with read and write permissions.
3. Run **Generate Contribution Snake**. It publishes to the `output` branch.
4. Optional: WakaTime or Spotify widgets can sit beside the kettle, in the same
   paper palette. Do not drop a dark-mode HUD into the atelier.

## 6. External services

`shields.io` · `readme-typing-svg.demolab.com` · `komarev.com` · `Platane/snk`

All are free image services. If one is down, only that piece degrades.

---

<sub>Signed in walnut ink. If a section breaks, remove it; neighbors do not collapse.</sub>
