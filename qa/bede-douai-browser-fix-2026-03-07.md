# Fix Report — Douai Browser Issues
**Agent:** Bede (🌐)  
**Date:** 2026-03-07  
**Commit:** 5d6ef16  
**Based on:** Bellarmine QA report `qa/bellarmine-douai-browser-2026-03-07.md`

---

## Fix 1 — CRITICAL: NT pages now correctly attributed to Rheims 1582 ✅

**Problem:** Every NT book page (Matthew through Revelation) had meta description and inline note reading "1609 Douay Old Testament." The 1609 Douay was OT only. The NT was published at Rheims in 1582.

**Root cause:** `generate_douai.py` used a single hardcoded string "1609 Douay Old Testament" in all three generation functions (`build_index`, `build_book_index`, `build_chapter`) regardless of testament.

**Fix applied to `generate_douai.py`:**
- Added `source_short(abbrev)` → returns `'1582 Rheims New Testament'` or `'1609 Douay Old Testament'` based on OT/NT membership
- Added `source_long(abbrev)` → returns full inline note with correct college (Rheims vs Douai), year, and description
- Updated `build_book_index`: meta description now uses `source_short(abbrev)`
- Updated `build_chapter`: meta description and `<div class="lapide-synopsis">` paragraph now use `source_short` / `source_long`
- Updated `build_index` (douai/index.html): header now reads "Douay-Rheims — Annotations" with subtitle "Rheims New Testament (1582) · Douay Old Testament (1609)"; lead paragraph correctly describes both publications

**Sample — NT (1 Corinthians):**
```
<meta name="description" content="Annotations on 1 Corinthians from the 1582 Rheims New Testament. Browse by chapter.">
```
```
These annotations are from the original 1582 Rheims New Testament, produced by English scholars
in exile at the English College of Rheims. The archaic spelling is preserved.
```

**Sample — OT (Genesis):**
```
<meta name="description" content="Annotations on Genesis from the 1609 Douay Old Testament. Browse by chapter.">
```

---

## Fix 2 — MODERATE: "Song of Solomon" → "Canticle of Canticles" ✅

**Problem:** `generate_douai.py` BOOK_MAP had `'Sg': ('songofsolomon', 'Song of Solomon')`. "Song of Solomon" is the Protestant / Hebrew-derived title. The Douay-Rheims follows the Vulgate: *Canticum Canticorum* → Canticle of Canticles.

**Fix applied:**
- `generate_douai.py` BOOK_MAP: `'Sg': ('canticleofcanticles', 'Canticle of Canticles')`
- Directory renamed: `douai/songofsolomon/` → `douai/canticleofcanticles/`
- All generated pages (index, chapter pages) now use "Canticle of Canticles"
- `douai/index.html` OT book list entry updated accordingly

---

## Pages Regenerated

All 165 pages regenerated via `python3 generate_douai.py`:
- `douai/index.html` (main index)
- 35 book `index.html` files
- 130 chapter pages

---

## Commit

```
5d6ef16  fix: correct NT attribution to Rheims 1582, rename Canticle of Canticles [Bede]
149 files changed, 1309 insertions(+), 1622 deletions(-)
```

---

## Status

Both defects from Bellarmine's report resolved. Ready for:
1. **Bellarmine** — re-check
2. **Pius** — approval gate
3. **Leo** — deploy

*Ora pro nobis. — Bede*
