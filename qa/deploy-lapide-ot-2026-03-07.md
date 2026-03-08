# Deploy Log — Lapide OT Browser (Psalms + Minor Prophets)

**Date:** 2026-03-07 ~09:45 CST
**Deployed by:** Leo (📦)

## Commits Deployed

| SHA | Author | Message |
|-----|--------|---------|
| 089f253 | ecclesia-dev (Bede) | feat: add Psalms + 12 Minor Prophets to Lapide browser — full OT coverage |

**Note:** Original commits f0ca694 (Bede — new books) + 7795343 (Polycarp — path fix) were squashed into a single clean commit (089f253) to remove hardcoded system paths from `lapide/build.py` git history. The path fix by Polycarp (using `SCRIPT_DIR` relative paths instead of absolute `/Users/...` paths) is incorporated into the final commit.

Additionally, `douai/generate_douai.py` had the same hardcoded path issue — fixed to use `SCRIPT_DIR.parent.parent / "drb-ios"` relative resolution.

## Gate Clearance

- Bellarmine: APPROVED (theology) ✅
- Pius: CLEAR (PR gate, both rounds) ✅

## Pre-push Hook

- **Guard 4 (internal tooling):** Blocked initial push — `lapide/build.py` in commit history contained `.workspace` workspace paths. Resolved by soft-resetting to origin/main and recommitting with clean file content only.
- **Guard 3 (owner name):** Douai commit (Bede) contains OCR artifacts from the 1609 Douai-Rheims source text where "Tim." / "1 Tim" / "2 Tim" (abbreviations for the Epistles to Timothy) trigger the name guard. **Douai commit NOT pushed** — remains local, needs separate OCR cleanup pass before it can be pushed.

## Rsync Summary

- 2,398,709 bytes sent / 137,814 bytes received
- Total size: 19,028,719 bytes (speedup 7.50)
- New directories deployed: psalms/, hosea/, joel/, amos/, obadiah/, jonah/, micah/, nahum/, habakkuk/, zephaniah/, haggai/, zechariah/, malachi/
- Updated: lapide/index.html, lapide/build.py excluded from deploy

## HTTP Verification

```
psalms/22: HTTP 200 ✅
jonah/2:   HTTP 200 ✅
```

## Outstanding

- Douai-Rheims 1609 annotations browser commit (5815a83) remains unpushed — needs OCR cleanup of "Tim" → "Timothy" in 17 HTML files before the pre-push hook will pass. This is a separate task for Bede.
