# Stage 3 — Accessibility (Margaret)
**Date:** 2026-03-02  
**Files:** rome-indulgence-guide.html, holy-land-indulgence-guide.html

## Review

### lang attribute
- Both: `<html lang="en">` ✅

### Skip Navigation
- Both: `<a href="#main-content" class="skip-nav">Skip to content</a>` as first element in body ✅

### Main Landmark
- Both: `<main id="main-content">` ✅

### Nav aria-label
- Both: `<nav aria-label="Site navigation">` on site nav ✅
- Both: `<nav class="article-toc" aria-label="Table of contents">` on in-article TOC ✅
- Related articles section: `<section class="article-related" aria-label="Related articles">` ✅

### Single H1
- Rome: exactly one `<h1>` ✅
- Holy Land: exactly one `<h1>` ✅

### Heading Hierarchy
- Rome: H1 → H2 (conditions, four-major-basilicas, seven-churches, other-indulgences, practical-notes) → H3 within basilicas and other-indulgences ✅
- Holy Land: H1 → H2 (conditions, jerusalem, bethlehem, nazareth, galilee, franciscan-custody, practical-notes) → H3 within jerusalem, bethlehem, nazareth, galilee ✅
- No heading levels skipped ✅

### Alt Text
- No `<img>` elements in either file — no alt text required ✅

### Empty Links
- All anchor elements contain visible text content ✅
- TOC links point to section IDs with descriptive text ✅
- Nav links all have text ✅

### Inline Fixes Applied
None required.

## Result: PASS ✅
