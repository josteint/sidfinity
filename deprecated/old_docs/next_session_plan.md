# Next Session Plan — Decompiler + Converter Fixes

**Goal:** Get from 61/103 Grade A to 90+/103, and unblock Group C (572 HVSC songs).

**All items below are independent and can run as parallel agents.**

---

## Track 1: Pattern Parser FX+$00 Bug (~10 songs)

**File:** `src/gt2_decompile.py` (pattern parsing section)

**Bug:** When a pattern ends with `FX_byte $00`, the `$00` is consumed as end-of-pattern instead of the FX parameter. This drops toneportamento setup (`$43 $00`) and effect resets (`$50 $00`).

**Fix:** In the pattern parser, when reading an FX byte ($40-$5F), always read the next byte as the parameter (even if $00), then check the byte AFTER that for end-of-pattern. The FX+param is a fixed 2-byte sequence that can't be split.

**Test:** Castlevania-Bloodlines.sid should improve significantly (813 note_wrong → near 0). Also check Nadia_The_Secret_of_Blue_Water.sid.

**Affects:** ~10 songs across Groups B and D that use toneportamento.

---

## Track 2: Speed Table $D9 Opcode (~16 songs)

**File:** `src/gt2_decompile.py`, function `_detect_speed_table_from_binary()`

**Bug:** The function only scans for `LDA abs,Y` (opcode $B9) to find speed table references. Songs compiled with `NOCALCULATEDSPEED=1` use `CMP abs,Y` (opcode $D9) instead for the vibrato speed check. The speed table is missed entirely.

**Fix:** Add $D9 (CMP abs,Y) to the opcode scan alongside $B9 (LDA abs,Y). Both have 3-byte format: opcode + addr_lo + addr_hi.

**Secondary fix:** Table boundary detection over-counts filter table size, consuming speed table bytes. After detecting speed table addresses, validate that the filter table doesn't extend past the speed table start.

**Test:** Pleasure_to_Paso.sid (7 note_wrong → 0), Quo_Vadis.sid (560 → near 0). All 17 Group D songs should improve.

**Affects:** ~16 songs, primarily Group D but also some Group B.

---

## Track 3: `nowavedelay` Misdetection (~5 songs)

**File:** `src/gt2_decompile.py` or `src/gt2_to_usf.py`, nowavedelay detection

**Bug:** Radar_Love.sid has wave table data WITHOUT +$10 bias (actual SID values), but `nowavedelay` is detected as False (claiming bias exists). The `gt2_to_usf` then subtracts $10 from already-unbiased values: $41 → $31 (pulse+gate becomes saw+tri+gate).

**Investigation needed:** Check how `nowavedelay` is detected. The function `detect_nowavedelay()` in `gt2_to_usf.py` examines the wave table bytes. It may fail when all waveform bytes happen to be >= $20 (looks biased but isn't). Cross-check against the original binary's player code — look for `CMP #$10` in the wave table handler to determine if the player has delay support.

**Fix:** Use the player code analysis (presence of `CMP #$10` / `BCS` before `SBC #$10`) as ground truth for `nowavedelay`, not just the data values.

**Test:** Radar_Love.sid (1449 wave_wrong → 0).

**Affects:** ~5 songs with false nowavedelay detection.

---

## Track 4: Group A Pulse Speed ASL (~14 songs)

**File:** `src/gt2_to_usf.py` (pulse table conversion)

**Bug:** Group A GT2 players (v2.65-2.67) use `ASL` to double the pulse speed byte before adding to the accumulator. Our converter doesn't account for this, so pulse modulates at half speed.

**Investigation needed:** The naive fix (double all speed bytes for Group A) regressed 12 songs. The ASL applies only during MODULATION (left column < $80), not during SET-PULSE (left column >= $80). But even with this condition, some songs regress.

**Deeper investigation:** Disassemble 2-3 Group A songs' pulse table handlers and compare the exact code path. Check if `fixedparams` or `simplepulse` flags affect which bytes get doubled. The agent found that Group A uses `ASL; BCC` (carry = sign) instead of `CLC; BPL` (N flag = sign). The sign detection is different — this may affect which speed values need doubling.

**Fix:** Condition the doubling on the exact code path: only double when the original uses `ASL` (not `CLC`). Detect from the binary whether ASL is present in the pulse handler.

**Test:** Enigmatic_Wave.sid (423 note_wrong), CARRIER_LOST.sid, Beloved.sid. No regression on existing Group A Grade A songs (Shapeshifter, Islamic_Snowmen, etc.).

**Affects:** ~14 Group A songs.

---

## Track 5: Group C Ghost Register Decompiler (572 blocked songs)

**File:** `src/gt2_parse_direct.py` and `src/gt2_decompile.py`

**Bug:** Group C players write to a RAM ghost buffer instead of SID $D400. The decompiler searches for `STA $D405,X` / `STA $D406,X` to find instrument columns — these don't exist in Group C code.

**Fix (3 steps):**

1. **Detect ghost buffer address:** The copy loop `LDX #$18; LDA buf,X; STA $D400,X; DEX; BPL` is already detected by `detect_gt2_player_group()`. Extract `buf` address from this pattern.

2. **In `parse_gt2_direct()`:** When searching for AD/SR column operands, also check `STA ghost+5,X` and `STA ghost+6,X` (where ghost = detected buffer address).

3. **In `detect_gt2_player_group()`:** Fix ADSR order detection and `newnote_regs` detection to also check ghost buffer addresses.

**Test:** Pick any Group C file (e.g., Airwolf_Remix.sid at ghost_buf=$139B). Should decompile successfully and produce reasonable output.

**Affects:** 572 songs (14% of all GT2 in HVSC). This is the highest-impact single fix.

---

## Track 6: Wave Table Note Read Alignment (investigation only)

**NOT a fix track — research to inform future ML data quality.**

The wave table extraction uses `+2` offset and the player reads notes before INY. These are a matched pair — both "off by one" in opposite directions, canceling out for correct playback. But the USF contains the shifted note values.

**Investigation:** Quantify how many songs have wave table entries where adjacent note values differ. For those songs, the USF note column is shifted by 1 entry. Determine if this matters for ML training (the model learns the shifted mapping, which is self-consistent).

**Output:** A document describing the tradeoff. No code changes unless the paired fix can be validated across all 103 songs.

---

## Execution Order

All 5 fix tracks (1-5) are fully independent — different files, different bugs.

**Quick wins** (< 30 minutes each): Track 2 (speed table $D9), Track 1 (pattern FX+$00)

**Medium** (1-2 hours): Track 3 (nowavedelay), Track 4 (Group A pulse)

**Large** (2-4 hours): Track 5 (Group C ghost registers)

**Expected outcome:** Tracks 1+2 fix ~26 songs. Track 3 fixes ~5. Track 4 fixes ~14. Track 5 unblocks 572 new songs. Total: ~90+ Grade A out of 103, plus Group C coverage.
