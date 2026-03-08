# PR Gate Review — Lapide OT Browser (13 new books)
**Commit:** f0ca694  
**Date:** 2026-03-07  
**Reviewer:** Pius 🛡️  
**Theology pre-cleared by:** Bellarmine ✓  

---

## PR GATE: FLAGGED [Pius]

One blocker must be fixed before Leo pushes to production.

---

## ❌ BLOCKER — Hardcoded System Path in build.py

**File:** `lapide/build.py`  
**Lines:** 4 (docstring) and 23 (code)

```python
# Line 4 (docstring comment):
Output: /workspace/workspace/projects/website/lapide/

# Line 23 (active code):
DRB_DIR = Path("/workspace/workspace/projects/drb")
```

**Issue:** Username `master` and full internal directory structure `.agent-workspace/workspace/projects/` are hardcoded. This is a pre-existing issue that this commit touches but does not fix — and the task explicitly requires "No hardcoded internal paths in build.py or HTML." The repo is committed publicly (deployed to ecclesiadev.com). SOUL.md is unambiguous: *NEVER disclose personal information online.* A machine username + internal path structure counts.

**Fix required:**
```python
# Replace hardcoded path with relative resolution:
SCRIPT_DIR = Path(__file__).parent          # already defined
DRB_DIR = SCRIPT_DIR.parent.parent / "drb"  # resolve relative to script
```
Update the docstring comment to remove the absolute path as well.

Bede must fix this and resubmit.

---

## ✅ CLEARED ITEMS

### 1. PII in HTML
- No real names, emails, phone numbers, or system paths in any of the 196 new HTML files.
- The word "master" appears in three files (hosea/11.html, malachi/1.html, psalms/122.html) — checked; it is theological content ("a servant his master," "masters" as biblical metaphor). Not PII. ✓

### 2. Brand Voice
- Psalms intro: *"expounding the Psalter as simultaneously the prayer of David, the voice of Christ, and the prayer of the Church"* — patristic, traditional, orthodox. ✓
- Minor Prophet intros (Habakkuk, Malachi, Zephaniah et al.) are rich, Christologically grounded, and cite Council of Trent where appropriate (Malachi on the Mass). Excellent. ✓
- Footer: *"Ad maiorem Dei gloriam"* — appropriate. ✓
- No modernist framing detected anywhere. ✓

### 3. Mission Alignment
- Complete OT Lapide browser with 12 Minor Prophets + Psalms is excellent traditional Catholic scholarly content. Serves the mission directly. ✓

### 4. Links / Navigation
- All 13 new book directories confirmed present: hosea, joel, amos, obadiah, jonah, micah, nahum, habakkuk, zephaniah, haggai, zechariah, malachi, psalms. ✓
- All 13 correctly linked from lapide/index.html. ✓
- Spot-check lapide/psalms/index.html: navigation structure correct, canonical URLs correct (ecclesiadev.com/lapide/psalms/), breadcrumb correct, chapter grid renders properly. ✓

### 5. Agent Credits
- Commit message: `feat: add Psalms + 12 Minor Prophets to Lapide browser — full OT coverage [Bede]` ✓
- Author: `ecclesia-dev <noreply@ecclesiadev.com>` — no human names. ✓
- No human names in any HTML. ✓

### 6. Hardcoded Paths in HTML
- Generated HTML files use relative paths only (e.g., `href="../../style.css"`). ✓
- Canonical URLs are production URLs (`https://ecclesiadev.com/lapide/...`). ✓
- **build.py is the sole offender** (see blocker above). HTML itself is clean.

### 7. Psalms Page Spot-Check
- `lapide/psalms/index.html`: well-formed HTML5, correct meta tags, canonical link, site nav, breadcrumb, chapter grid. Intro text is substantive and patristically grounded. ✓

---

## ⚠️ NON-BLOCKING NOTE — OT Book Ordering

Psalms appears after Malachi in the index — after all the Minor Prophets — rather than in its canonical Vulgate position (Job → Psalms → Proverbs). This is intentional in build.py BOOK_META (grouped by Bede's completion order) and is a pre-existing architectural decision. It is not introduced by this commit.

**However:** the inconsistency is now more visible — some Sapiential books (Proverbs through Sirach) appear before the Major Prophets, while Job and Psalms appear after the Minor Prophets. This is worth a UX ticket. Not a blocker for this PR.

---

## Action Required

1. **Bede** — fix `lapide/build.py` lines 4 and 23: replace absolute path `/workspace/workspace/projects/drb` with a relative path resolved from `SCRIPT_DIR`. Remove the hardcoded path from the docstring as well.
2. Resubmit for Pius re-review (spot-check only; theology pre-cleared by Bellarmine, all other gates already CLEAR).
3. On re-review CLEAR → Leo deploys.

---

*Fac iustitiam et iudicium.* — Ezek. 45:9

🛡️ Pius | PR Gate | Ecclesia Dev

---
Re-check 2026-03-07 (commit 7795343): Path fix confirmed clean.
PR GATE: CLEAR [Pius] ✅
→ Leo: push and deploy to ecclesiadev.com
