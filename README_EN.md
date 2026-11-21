# bisheng — HTML Web PPT Skill

> Movable type, one page per block. Generate a single-file HTML web deck: fullscreen paging, fluid responsive layout, traditional slide navigation, a self-built motion engine, thumbnail overview, speaker notes, dual-screen mirroring, and PDF export.

[![version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)](SKILL.md) [![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE) [![python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)](scripts/)
[![deck](https://img.shields.io/badge/deck-single--file-orange?style=flat-square)](assets/deck.html) [![checks](https://img.shields.io/badge/checks-4--in--1-brightgreen?style=flat-square)](scripts/check_all.py)

[中文](README.md) | English

## ✨ Features

- **Fluid fullscreen layout**: each slide is 100vw × 100vh; `html font-size = min(100vw/80, 100vh/45)` and rem-based typography scale with the window. Switches to a single-column layout at ≤760px. No black bars on any screen, projector, or TV
- **Traditional slide navigation**: click / Shift+click, arrow keys, Space, PageUp/Down, Home/End, number-key jumps, mouse wheel, and touch swipe
- **Advanced interaction**: Esc thumbnail grid (left-aligned, final-state numbers) with click-to-jump, F fullscreen, P notes drawer, B low-power static mode, A auto-advance, dual-window mirroring
- **Self-built motion engine**: `data-anim` leaf markers + four recipes (quote / directional / pipeline / bars) + `data-count` number roll; transform/opacity only; `prefers-reduced-motion` fallback; content stays visible if the engine is unavailable. Extra effects: spring easing, text reveal, SVG path drawing, smooth page transitions
- **Theme system**: four presets (Ink & Paper / Indigo / Forest / Kraft) with light/dark/accent states; pages use CSS variables only; brand-color script applies WCAG-constrained lightness adjustment
- **Multi-image layouts**: two-image symmetric / 7:5, three-image equal / hero+two, four-image 2×2 / hero+three; uniform ratios and heights within a group
- **One-command defect check**: `check_all.py` runs static structure + per-page rendering + keyboard interaction + PDF export in one shot, with `[FAIL]/[WARN]` findings and an exit code; contrast failures include the element id
- **Design review gate**: a mandatory critique before delivery (Nielsen heuristics + persona walkthrough); passing mechanical checks does not mean good design

## 📦 Installation

```bash
# Option 1: sync from a multi-skill workspace (run at the root containing bisheng/ and scripts/)
python3 scripts/sync_install.py

# Option 2: copy manually into the agent skill directory
cp -r bisheng/ ~/.zcode/skills/bisheng/
```

Requirements: Python 3.8+. Rendering checks need Playwright (falls back to the system Edge/Chrome browser).

## 🚀 Quick Start

Trigger with natural language in a skill-aware agent session:

```text
Create a 10-slide AI product launch deck       # → generate an HTML deck
Change this deck to a Swiss style              # → switch theme / layout
Add a three-layer architecture diagram to page 4  # → generate SVG and embed
```

Generation workflow (7 steps, see [SKILL.md](SKILL.md)):

```text
1. Structure first   → align page plan / layout plan / theme rhythm tables
2. Create folder     → index.html + bs-motion.js + images/
3. Fill content      → L1-L10 skeletons + data-anim markers + SPEAKER_NOTES
4. One-command check → python3 scripts/check_all.py <deck>/index.html
5. Browser QA        → per-page screenshots, paging, scaling, motion, PDF
6. Design review     → critique gate
7. Iterate & deliver → fix → re-run → delivery notes
```

## ✅ Testing & Verification

```bash
python3 -m unittest discover -s tests -v       # 7 golden samples: validator positives/negatives + render smoke/overflow
python3 scripts/check_all.py <deck>/index.html  # one-command gate: exit 0 pass / 1 defects / 2 cannot check
```

Negative verification is proven: removing the white override on an accent-card subtitle makes `check_all` report `.t-sub contrast 3.57:1 (<4.5) @card card-accent` with exit code 1.

Checker coverage: placeholders, slide count, unique ids, motion-marker density, theme rhythm, hero line breaks, recipe pairing, note fields, image references, screen-reader hooks, hardcoded hex, bottom-stick risks, overflow, safe area, title gap, rendered font size, contrast, JS errors, keyboard matrix, and PDF page count.

## 📁 Directory Structure

```text
bisheng/
├── SKILL.md                  # Entry: 7-step workflow + gates + prohibitions
├── assets/
│   ├── deck.html             # Engine template (single source of class names and keys)
│   └── bs-motion.js          # Self-built motion engine (spring/text reveal/SVG draw/smooth switch)
├── references/
│   ├── narrative.md          # Narrative arc + three-table alignment + theme rhythm + notes/image rules
│   ├── layouts.md            # L1-L10 paste-ready layout skeletons
│   ├── themes.md             # Theme presets + color variable contract + brand color generation
│   ├── image-layouts.md      # Multi-image layouts (six skeletons for 2/3/4 images)
│   ├── checklist.md          # P0/P1/P2 quality checklist
│   └── maliang-gate.md       # Design review gate workflow and fallbacks
├── scripts/
│   ├── check_all.py          # Unified one-command check
│   ├── validate_deck.py      # Static structure validation
│   ├── check_render.py       # Rendering/contrast/keyboard/PDF verification
│   ├── brand_theme.py        # Brand color → constrained theme
│   ├── sync_install.py       # Dev copy → installed copy sync (--check reports drift)
│   ├── watch_deck.py         # Automatic validation on file change (optional)
│   └── gate-hook.py          # PostToolUse validation trigger (optional)
├── tests/                    # unittest golden samples
└── examples/demo/            # Example deck (8 pages, includes a multi-image page)
```

## 🔮 Boundaries

- **Not a collaboration tool**: use other tools for Feishu decks, PPT-to-Markdown conversion, and real-time collaborative documents
- **No data charts**: dense tables and data plots belong in traditional tools; this skill builds presentation pages
- **No hardcoded sizes**: typography uses rem; the only breakpoint is the built-in ≤760px single-column downgrade
- **Mechanical checks are not design approval**: delivery must pass the design review gate

## 📄 License

MIT License (© 2026 Kirky-X).
