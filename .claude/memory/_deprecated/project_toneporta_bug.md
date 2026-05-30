---
name: Toneporta architecture and fix
description: How toneporta works in GT2 vs V2, the mt_chnnewfx overwrite bug, and the ce_tp_note fix
type: project
---

**FIXED** (commit 9724904). V2 toneporta now works correctly. Two fixes:

1. **ce_runfx param=0 bypass** (commit 368886d, +124 Grade A): The ce_runfx guard skipped ALL continuous effects when mt_chnparam=0. Toneporta with param=0 means "snap to target" (speed table reads $00 prefix). Fix: check mt_chnfx==3 before skipping.

2. **mt_chnnewfx overwrite fix** (commit 9724904): When a toneporta note (FX3+NOTE) was read, mt_chnnewnote was left pending. The next tick-0's pattern reader overwrites mt_chnnewfx before ce_newn checks it, causing full HR init instead of toneporta skip. Fix: ce_tp_note handler placed before ce_rest consumes the note inline (sets mt_chnnote, mt_chnfx=3, mt_chnparam, clears mt_chnnewnote).

**Why GT2 doesn't have this bug:** GT2 encodes toneporta as FXONLY ($53+param) on one row and bare note on the next. mt_chnnewfx=3 persists to the next tick-0 because no new FX byte is read with the bare note. V2 encodes FX+NOTE ($43+param+note) on the same row.

**Layout sensitivity:** The ce_tp_note handler adds ~24 bytes before ce_rest. This shifts addresses for songs with TONEPORTA flag. The sequence-level jitter detection (commit 5fcb5bf) absorbs most of the resulting timing artifacts.

**How to apply:** The toneporta fix is stable. Don't change the ce_tp_note placement without re-running the full 3,478-song batch test.
