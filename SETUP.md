# SETUP GUIDE — MUXBY-OS "NEON VOID" PROFILE

Everything in this repo is wired for the GitHub username **`muxby`** (this repo is
`muxby/muxby`, the special profile repository). If you fork or adapt it, this is the
complete find-and-replace map and activation checklist.

---

## 1. What's in the box

| File | Purpose |
|---|---|
| `README.md` | The profile itself — 16 sections, fully commented with `<!-- ══════ SECTION XX ══════ -->` markers |
| `assets/hero-banner.svg` | Animated nebula hero banner (SMIL) |
| `assets/sigil.svg` | The recurring hexagonal "M" monogram |
| `assets/divider-circuit.svg` | Circuit-board divider with traveling data pulses |
| `assets/divider-starfield.svg` | Constellation divider with comet |
| `assets/divider-wave.svg` | Triple sine-ribbon wave divider |
| `assets/divider-beam.svg` | Gradient beam divider with light sweep |
| `assets/constellation.svg` | Tech constellation map (Section 05) |
| `assets/radar-chart.svg` | Six-domain skill radar (Section 04) |
| `assets/odyssey.svg` | Metro-map learning roadmap (Section 12) |
| `assets/hologram.svg` | Hologram projector (Section 07) |
| `assets/glitch-restricted.svg` | Glitch "restricted area" banner (Section 09) |
| `assets/signature.svg` | Self-drawing signature (Section 16) |
| `assets/aurora-header.svg` | Aurora borealis header for The Observatory (Section 06½) |
| `assets/graph-gauges.svg` | Cockpit gauge cluster — animated needles & arcs (Section 06½) |
| `assets/graph-donut.svg` | "Code DNA" donut chart with staggered segment draw-in (Section 06½) |
| `assets/graph-bars.svg` | Skill equalizer — bars rise once, then breathe like an EQ (Section 06½) |
| `assets/graph-growth.svg` | Self-drawing XP line chart with milestone markers (Section 06½) |
| `assets/graph-heatmap.svg` | Commit-intensity heatmap with pulsing "supernova" cells (Section 06½) |
| `assets/graph-polar-clock.svg` | 24-hour circadian commit clock with rotating sweep (Section 06½) |
| `assets/graph-oscilloscope.svg` | Dev-vitals oscilloscope — scrolling EKG + flow wave (Section 13) |
| `.github/workflows/snake.yml` | Contribution snake generator → `output` branch |
| `.github/workflows/profile-3d.yml` | 3D contribution graph → `output-3d` branch |

## 2. Find-and-replace values

| Placeholder in files | Replace with |
|---|---|
| `muxby` (in all widget URLs & raw.githubusercontent links) | your GitHub username |
| `hello@example.com` | your real email (Sections 15) |
| `href="#"` in Section 15 | your real social profile URLs |
| `41.0082° N · 28.9784° E` | your (approximate!) coordinates |
| `since+2016` in the typing SVG | your actual start year |
| Project cards in Section 08 | your real repos, taglines, and links |
| `repo=muxby` pin card in Section 14 | your best repository |

Text inside the custom SVGs (name "MUXBY", radar values, roadmap stations) is plain
`<text>`/`<path>` markup — edit the SVG files directly.

## 3. Activation checklist

1. **Merge to the default branch** of `<username>/<username>` — GitHub only renders the
   profile README from the default branch.
2. **Enable Actions** (Actions tab → enable workflows) and check
   *Settings → Actions → General → Workflow permissions → Read and write permissions*.
3. **Run the snake**: Actions → *Generate Contribution Snake* → *Run workflow*.
   It publishes SVGs to the `output` branch that Section 06 embeds.
4. **Run the mountains**: Actions → *Generate 3D Contribution Graph* → *Run workflow*.
   It publishes to the `output-3d` branch that Section 07 embeds.
   (Until first run, those two images will 404 — everything else renders immediately.)
5. **Optional — WakaTime**: create a wakatime.com account, then uncomment the WakaTime
   card in Section 06.
6. **Optional — Spotify**: generate a widget at `spotify-github-profile.kittinanx.com`
   and drop it into the "NOW PLAYING" slot in Section 13.

## 4. External services used

`shields.io` · `readme-typing-svg.demolab.com` · `github-readme-stats.vercel.app` ·
`streak-stats.demolab.com` · `github-profile-trophy.vercel.app` ·
`github-readme-activity-graph.vercel.app` · `github-profile-summary-cards.vercel.app` ·
`komarev.com` · `capsule-render.vercel.app` · `skillicons.dev` ·
`quotes-github-readme.vercel.app` · `Platane/snk` · `yoshi389111/github-profile-3d-contrib`

All are free, no-auth image services; if one is temporarily down, only that card
degrades — the layout holds.

## 5. Color system ("Neon Void")

| Token | Hex | Reserved for |
|---|---|---|
| Void black | `#0D1117` | backgrounds (GitHub-dark native) |
| Electric cyan | `#00F5FF` | languages, primary accents |
| Neon magenta | `#FF00E5` | frameworks, alerts, glitch |
| Plasma purple | `#9D4EDD` | infrastructure, headings |
| Accent gold | `#FFD700` | **achievements & AI only** — keep it rare |
| Soft white | `#E6EDF3` | body text on dark |

---

<sub>Signed in the void. If a section breaks, check the HTML comment markers — every
section is independent and can be removed without collapsing its neighbors.</sub>
