# Stage 4 — Code (Jerome)
**Date:** 2026-03-02  
**Files:** rome-indulgence-guide.html, holy-land-indulgence-guide.html

## Review

### Relative Paths
All asset paths are correct relative to the `articles/` directory:
- `../favicon.svg` ✅
- `../style.css` ✅
- `../scripts/liturgical.js` ✅
- `../index.html` (site nav links) ✅
- `index.html` (back to articles, TOC nav, article-back link) ✅
- Google Fonts via absolute CDN URL ✅

### Markdown Syntax in HTML
Checked for stray `**`, `*`, `##`, `---` (outside `<hr>` tags), `[text](url)`, and backtick patterns.
- No bare markdown syntax found in either file ✅
- All emphasis converted to `<em>`, all bold to `<strong>` ✅
- All list items converted to `<li>` elements ✅
- All links converted from `[text](url)` to `<a href="url">text</a>` ✅
- Source comment block (Follow-Up Articles) stripped from Rome article ✅
- Author byline (`*By Isidore — Ecclesia Dev*`) stripped from both ✅
- Footer publication line stripped from both ✅

### Viewport Meta
- Both: `<meta name="viewport" content="width=device-width, initial-scale=1.0">` ✅

### Clean Structure
- DOCTYPE, html, head, body structure correct ✅
- No unclosed tags or nesting errors apparent ✅
- Script tags at end of body ✅
- CSS in head ✅
- `<hr class="article-rule">` between header and TOC ✅

### Canonical / OG URL consistency
- Rome canonical and og:url both point to `rome-indulgence-guide.html` ✅
- Holy Land canonical and og:url both point to `holy-land-indulgence-guide.html` ✅

### Inline Fixes Applied
None required.

## Result: PASS ✅
