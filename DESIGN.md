# Visual Direction & Surface Authority — Gemma AI

## 1. Visual World: Tactile Editorial Intelligence
Gemma AI pairs the quiet precision of a technical instrument with the warmth of an archival research studio. Instead of neon sci-fi tropes or glowing chromatic halos, surfaces rely on physical lightness steps, crisp 1px structural hairlines, neutral elevation shadows, and editorial Thai/English typography.

## 2. Curated Multi-Theme System
All themes override the **Semantic Token Tier** (`--ds-color-*`) while maintaining WCAG 2.2 AA contrast (≥4.5:1 for body and secondary labels, ≥3:1 for large display titles and active boundaries):

1. **Atelier Amber (`data-theme="dark"` — Default Dark):**
   - Deep carbon-obsidian canvas (`#0d0e0c`), elevated warm slate panels (`#161814` / `#1f221c`), warm parchment foreground (`#f4f0e8`), secondary text (`#a5a89d`), and kiln-amber accent (`#ff852b`).
2. **Botanical Sage (`data-theme="forest"` — Deep Nature Dark):**
   - Deep moss canvas (`#0c110d`), forest-stone panels (`#141c16` / `#1c261f`), soft ivory foreground (`#edf2ec`), secondary text (`#9eb0a0`), and botanical sage accent (`#78c264`).
3. **Nordic Cobalt (`data-theme="nordic"` — Technical Slate Dark):**
   - Midnight mineral canvas (`#0b0f17`), slate-navy panels (`#131924` / `#1b2332`), crisp ice foreground (`#edf2f8`), secondary text (`#9ba8bc`), and precision azure accent (`#52a8ff`).
4. **Archival Parchment (`data-theme="light"` — Natural Paper Light):**
   - Warm archival paper (`#f4efe6`), cream card surfaces (`#fbf8f2` / `#e8e0d2`), espresso ink (`#1e1a15`), secondary ink (`#595248`), and terracotta-amber accent (`#b84a0e`).

## 3. Typography & Bilingual Thai/English Rules
- **Display Face:** `'DM Serif Display', 'Noto Sans Thai', serif` for primary identity headings.
- **UI & Body Face:** `'DM Sans', 'Noto Sans Thai', system-ui, sans-serif` with `line-height: 1.75` for Thai body copy so upper/lower vowel and tone marks (`วรรณยุกต์`) never clip.
- **Monospace Face:** `'DM Mono', monospace` with `font-variant-numeric: tabular-nums` for code, token counters, latencies, and timestamps.
- **Legibility Floor:** Functional UI text is strictly `>= 11.5px` (`0.72rem`). Zero letter-spacing on Thai strings; no `text-transform: uppercase` on bilingual strings.
