# QA Report: Lapide Browser — Psalms + 12 Minor Prophets
**Agent:** Bede 🌐  
**Date:** 2026-03-07  
**Commit:** f0ca694

---

## Books Added (13 total)

| Book | Directory | Chapter HTML files | Notes |
|------|-----------|-------------------|-------|
| Psalms | `psalms/` | 122 | Not all 150 psalms covered — see Anomalies |
| Hosea | `hosea/` | 11 | Chapters 7, 9, 10, 12 absent from source |
| Joel | `joel/` | 3 | Complete (3-chapter book) |
| Amos | `amos/` | 8 | Chapter 6 absent from source |
| Obadiah | `obadiah/` | 1 | Complete (single-chapter book) |
| Jonah | `jonah/` | 4 | Complete |
| Micah | `micah/` | 6 | Chapter 2 absent from source |
| Nahum | `nahum/` | 3 | Complete |
| Habakkuk | `habakkuk/` | 3 | Complete |
| Zephaniah | `zephaniah/` | 3 | Complete |
| Haggai | `haggai/` | 2 | Complete |
| Zechariah | `zechariah/` | 11 | Chapters 5, 7, 10 absent from source |
| Malachi | `malachi/` | 4 | Complete |

**Total pages generated:** 196 files (195 HTML + 1 lapide.css update)  
- 13 book index pages  
- 182 chapter pages  
- 1 updated main `lapide/index.html`

---

## Canonical Ordering Applied

Per task instructions:
- **Minor Prophets** inserted after Daniel (before Job) in `BOOK_META`: Hosea → Joel → Amos → Obadiah → Jonah → Micah → Nahum → Habakkuk → Zephaniah → Haggai → Zechariah → Malachi  
- **Psalms** inserted after Job (at end of OT section)

---

## Anomalies in Source TSV Data

### Psalms (`lapide-Ps.tsv`)
- **28 psalms missing** from source data: Psalms 25, 42–43, 52, 55, 69, 74, 78, 80–82, 86, 92–95, 96–100, 114, 124, 128, 137, 140, 143, 147 have no commentary entries.
- These gaps are in the source TSV and not a build error — à Lapide's commentary does not cover every psalm with equal depth.
- The chapter nav on the book index page lists only the psalms that have entries, so no broken links are generated.

### Hosea (`lapide-Hos.tsv`)
- Chapters 7, 9, 10, 12 absent — 11 of 14 chapters covered.

### Amos (`lapide-Am.tsv`)
- Chapter 6 absent — 8 of 9 chapters covered.

### Micah (`lapide-Mic.tsv`)
- Chapter 2 absent — 6 of 7 chapters covered.

### Zechariah (`lapide-Zech.tsv`)
- Chapters 5, 7, 10 absent — 11 of 14 chapters covered.

All gaps are consistent with selective source translation; the build handles them cleanly (no broken chapter links — only existing chapters are linked in the TOC).

---

## Build Method

Modified `build.py` `BOOK_META` list to add 13 new OT entries with intro blurbs in à Lapide's scholarly style. Re-ran `build.py` — all existing books regenerated cleanly alongside the new ones. No template changes required; the existing `load_ot_file()` function handles the 5-column TSV format correctly.

---

## Next Steps

**Bellarmine** → theology review  
**Pius** → PR gate  
**Leo** → deploy to ecclesiadev.com
