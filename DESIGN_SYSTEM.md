# Design System: Gemma AI Enterprise Workspace

## Principles
1. **Precision Over Ornament**
   - *This means:* Hierarchy comes from lightness steps, 1px structural borders, neutral shadows, and typographic scale.
   - *This does not mean:* Colored neon glow shadows (`dark-glow`), decorative repeating stripe backgrounds, or 8px micro-labels.
2. **Bilingual Thai/English Harmony**
   - *This means:* Generous line-height (`1.72–1.78`), zero letter-spacing on Thai text, no forced uppercase on mixed strings, and ≥11.5px minimum functional text size.
   - *This does not mean:* Clipping Thai tone marks (`วรรณยุกต์`) inside fixed-height pills or shrinking labels below 11px.
3. **Transparent AI Provenance & Control**
   - *This means:* Every streaming response provides a Stop control, elapsed time, model badge, inline numbered citations (`[1]`), and one-click copy/regenerate/export actions.
   - *This does not mean:* Black-box spinners without phase indicators or uninterruptible generation loops.
4. **Token-Driven Multi-Theme Architecture**
   - *This means:* Components consume semantic tokens (`--ds-color-*`, `--ds-space-*`, `--ds-radius-*`); switching between `dark` (Atelier Amber), `forest` (Botanical Sage), `nordic` (Nordic Cobalt), and `light` (Archival Parchment) updates only semantic mappings.
   - *This does not mean:* Hardcoding hex colors inside interactive components.

## Brand & Voice
See [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md).

## Tokens
- **Source of Truth:** [`tokens/design-tokens.json`](tokens/design-tokens.json) (W3C DTCG format: `$type`, `$value`, `$description`)
- **CSS Custom Properties:** `--ds-{category}-{concept}-{variant}-{state}` with backward-compatible aliases (`--bg`, `--surface`, `--text`, `--accent`, etc.)
- **Supported Themes:** `dark` (Atelier Amber), `forest` (Botanical Sage), `nordic` (Nordic Cobalt), `light` (Archival Parchment)

## Foundations
- **Font Stack:**
  - `--ds-font-sans`: `'DM Sans', 'Noto Sans Thai', system-ui, sans-serif`
  - `--ds-font-display`: `'DM Serif Display', 'Noto Sans Thai', Georgia, serif`
  - `--ds-font-mono`: `'DM Mono', ui-monospace, monospace`
- **Type Scale (Modular):**
  - `--ds-font-size-xs`: `11.5px` (minimum functional UI floor)
  - `--ds-font-size-sm`: `12.5px`
  - `--ds-font-size-md`: `14.5px`
  - `--ds-font-size-lg`: `17.5px`
  - `--ds-font-size-xl`: `22px`
  - `--ds-font-size-2xl`: `clamp(26px, 3.6vw, 36px)`
- **Spacing Scale (4px base):** `--ds-space-1` (4px) through `--ds-space-12` (48px)
- **Radius Default:** `--ds-radius-md` (`12px`), `--ds-radius-lg` (`16px`), `--ds-radius-xl` (`22px`)
- **Elevation:** Neutral offset shadows (`--ds-shadow-sm`, `--ds-shadow-md`, `--ds-shadow-lg`) without chromatic dark-glow halos.

## Component Inventory
| Component | Tier | Status | Owner | Notes |
|---|---|---|---|---|
| `Topbar & Theme Switcher` | Foundation | Stable | Core UI | Includes Model selector, Preset badge, Export MD, Command Palette trigger, 4-theme switcher |
| `Composer & Tool Dock` | Foundation | Stable | Core UI | Preset selector, Project selector, Library RAG toggle, Web Research toggle, File upload, Stop streaming |
| `Message Bubble & Action Bar` | Core | Stable | Core UI | Markdown renderer, Code copy/download, Sources drawer, Copy/Regenerate/Export actions |
| `Command Palette (Ctrl+K)` | Core | Stable | Core UI | Keyboard-first navigation, theme switching, preset switching, session search |
| `Admin Command Center` | Surface | Stable | Admin UI | KPIs, Daily throughput bars, Search analytics, User/Role table, Audit log, Safe Backup |

## Decision Log
| Date | Decision | Rationale | Alternatives Considered |
|---|---|---|---|
| 2026-10-28 | Replace colored box-shadow glows with neutral elevation shadows + 1px borders | Eliminates `dark-glow` anti-pattern and improves surface separation across 4 themes | Keeping orange/green blur halos |
| 2026-10-28 | Raise all functional UI text to ≥11.5px and boost muted text contrast to ≥4.8:1 | Passes WCAG 2.2 AA and eliminates `undersized-ui-text` and `low-contrast` defects | Keeping 7.5px–10px micro-labels |
| 2026-10-28 | Add 4 curated themes (`dark`, `forest`, `nordic`, `light`) via semantic tokens | Gives users distinct workspace moods while preserving strict contrast guarantees | Only dark/light binary toggle |
