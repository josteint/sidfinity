# DMC time-medley — WIP (Praiser/Mega_Mix)

**Status (2026-07-31):** ✅ **sub 0 FULL** over the full songlength×1.1 window
(play_match=505746=len_a, state_match=True) AND byte-exact across TWO loop-backs
(500 s capture: 792634=len_a=len_b). The 1-write residual is RESOLVED by a
per-segment **shadow17 save/restore** in the `playmedley` wrapper (below). The
composer change is gated on `params.fields['medley']` → every non-medley member
is byte-identical (golden MD5 over 10 diverse members: single / family-2 /
page3-reloc / C29-oob / 2SID / hetero-compilation / two per-subtune-fact
compilations = all identical). Still builds only via the manual recipe below —
productionization (detection/probe/wiring) is the remaining step.

Ledger: this is a NEW structure adjacent to C31 — a **time-sequenced medley**
(one PSID subtune time-switches ≥2 packed players), distinct from C31 (per-
subtune dispatch) and C27 (parallel chips).

---

## What Mega_Mix is

`MUSICIANS/P/Praiser/Mega_Mix.sid` — 1 PSID song, VBLANK, load $1000, init
$2700, play $2703. No STIL/BUGlist entry. Songlength 290 s.

Two complete DMC players packed: **player 1 @ $1000**, **player 2 @ $2800**
(each a canonical DMC jump table). A wrapper at $2700 is the real init/play:

```
$2700 JMP $2706         ; init vector
$2703 JMP $272A         ; play vector
$2706 LDA #0 / JSR $1000 (player-1 init) / STA $03/$04/$02 = $40/$1F/$00
$272A (play wrapper):
      DEC $03                       ; 2-byte frame counter $03/$04
      LDA $03; CMP #$FF; BNE +; DEC $04   ; $04 DEC'd when $03 wraps ($FF)
    + LDA $02; BNE $274B            ; $02 = active segment flag
      JSR $1003 / JSR $275C(delay,no SID writes) / JSR $1003   ; DOUBLE-PLAY player 1
      LDA $04; BPL done; JSR $2718  ; when $04 < 0 → switch to player 2
      done: RTS
$274B ($02!=0): JSR $2803 / JSR $275C / JSR $2803  ; DOUBLE-PLAY player 2
      LDA $04; BPL +; JSR $2706     ; when $04<0 → switch back to player 1 (LOOP)
$2718 (→player 2): LDA #0/JSR $2800(player-2 init)/ $03=$64,$04=$19,$02=$01
```

So: **double-speed** (each player's play runs 2× per PSID play()) + a
**counter-timed switch** player1(seg0, cnt $40/$1F) → player2(seg1, cnt $64/$19)
→ player1 → … LOOPS. Measured: 1 switch within the songlength window; one full
cycle ≈ 315 s (player1 ≈174 s, player2 ≈141 s).

---

## Reproduction recipe (manual — no detection yet)

```python
from pipelines.dmc.v4.compilation import merge_models
from pipelines.dmc.v4.factory import dmc_v4_config
from pipelines.dmc.v4.extract import engine_model as em
from pipelines.dmc.v4.extract.to_usf import model_to_usf, write_file
from pipelines.dmc.composer_asm import build_dmc_sid
from src.usf.parser import parse_file
rel='MUSICIANS/P/Praiser/Mega_Mix.sid'; hv='hvsc85'
m0=em.extract(dmc_v4_config(rel,hvsc_root=hv,base_override=0x1000),hvsc_root=hv)
m1=em.extract(dmc_v4_config(rel,hvsc_root=hv,base_override=0x2800),hvsc_root=hv)
hdr={'title':m0.title,'author':m0.author,'released':m0.released,'clock':m0.clock,
     'sid_model':m0.sid_model,'start_song':1}
merged=merge_models([m0,m1],[(0,0),(1,0)],hdr)
merged.play_repeat=2                                   # double-speed
merged.extra_params['medley']='0:40:1F,1:64:19'        # seg = song:cnt_lo:cnt_hi (hex)
# → model_to_usf → build_dmc_sid → verify: sub 0 partial, play_match=500354/505746
```

## The composer wrapper (committed WIP, gated on `params.fields['medley']`)

`composer_asm.py`, in the play-wrapper chain (search `medley_spec`). Emits
`playmedley`: reproduces $272A's 2-byte counter (`medlo`/`medhi`, sentinel
`medseg=n_segments`), `jsr {playrepeat}` to double-play the active song, and on
segment expiry advances `medseg` (looping), reloads the counter from the
`medsong/medlo0/medhi0` tables, and `jsr init`s the next song. All gated — a
non-medley member emits nothing (byte-identical). Data tables + `medseg/medlo/
medhi` BSS are likewise gated.

---

## The 1-write residual — FULLY TRACED, then RESOLVED (2026-07-31)

Divergence: flat write 500293, siddump frame 15780, cyc $1293 →
`$D417 = $04` (orig) vs `$00` (ours). Res nibble matches ($0); routing nibble
differs (orig routes **voice 3** = $04, ours routes none). Streams re-converge
immediately (exactly ONE write in 505 685).

### The actual mechanism (measured, native siddump — the earlier guess refined)

Native measurement (`siddump --pc-watch 2708,270B --pc-watch-abs`, snapshotting
player-1's state region before/after the `JSR $1000` at the loop-back) settled
the reset/carry partition exactly: **`$101D` writes ONLY `$1719-$1794`** (zero
zp writes, nothing in `$0100-$1718`, nothing above `$1794`). So `$1018` =
shadow17 (the $D417 routing accumulator) is NOT reset — it CARRIES. And the
divergent `$04` is present at the loop-back **before AND after** init: it is
player-1's cycle-1-end routing accumulator, carried through player-2's segment
because in the orig `$1018` (player 1) and `$2818` (player 2) are **separate
addresses** — player 2 never touches player 1's `$1018`.

Our compilation merge collapses both players' `$1018` into ONE shared
`shadow17`, so at the loop-back OURS holds player-2's residual, not `$04`. That
is exactly why the doc's earlier "carry shadow17" experiment still left 1
mismatch — it carried the merged (player-2) value, the wrong one. The full
carry set (canon addr outside `$1719-$1794`) is {shadow17 `$1018`, spdctr
`$1718`, vsteph `$1795`, slal `$1798`, slah `$179B`}, but only shadow17 is
non-zero at the loop-back, and the baseline (reset-everything) has exactly ONE
divergence = shadow17 — so shadow17 is the sole functional carried var.

Mechanism (from `siddump --pc-trace`):
- Player 1's filter tail `$10A0-$10AC` recomputes **`$D417 = [$1018] | [$1723]`
  every frame**. Our composer mirrors this exactly: `lda shadow17 / ora fres /
  sta $d417` (so `shadow17`↔`$1018` routing, `fres`↔`$1723` res). This is why
  cycle 1 is byte-perfect.
- `$1018` is a **persistent routing accumulator**, written only at note-init
  (`$12C6`: `$1018 &= fmask[voice]` route-clear; `|= fbit` route-set). At the
  divergence it holds the V3 bit ($04), set earlier in cycle 2 by a **V3
  filter-on note-init** and persisted.
- The orig's **cycle 2 ≠ cycle 1**: a V3 note plays a *filter-on* instrument in
  cycle 2 where cycle 1 played non-filter — because the orig's player-1 init
  `$101D` is **MINIMAL** (resets the note/position machinery, **inherits player
  2's effect/filter/routing work-RAM**). Our universal `init` wipes everything,
  so our cycle 2 == cycle 1 (periodic) while the orig is aperiodic by this bit.

Confirmed: our player 2 matches the orig byte-for-byte, so **the exact state
that produces the `$04` already exists in our build at the switch** — the
loop-back just has to preserve it.

---

## The fix (DONE) — per-segment shadow17 save/restore in `playmedley`

Rather than a "soft re-init" that splits reset/carry inside one init, the clean
and self-consistent fix **reproduces the orig's separate per-player
accumulators**: give each segment its own carried `shadow17`. At every segment
switch the `playmedley` wrapper now:
- **SAVEs** the outgoing segment's `shadow17` to `medcarry[old_seg]` (before the
  `jsr init` that would wipe it),
- runs the clean `jsr init` (resets everything, re-primes `shadow17` from the
  song's tunetab routing byte),
- **RESTOREs** the incoming segment's `shadow17` from `medcarry[new_seg]`.

`medcarry[]` is **seeded** at the segment-0 cold start from `medrout[]` (each
song's routing prime), so a segment's FIRST entry restores == the init prime (a
no-op — critical because player 2's routing prime is `$02`, not 0, and a naive
BSS-0 restore would clobber it), and only a RE-entry re-asserts the player's own
carried value. At the loop-back the incoming (player-1) slot holds `$04` —
saved at the forward switch, where our stream matches the orig byte-for-byte, so
the value is correct **with no measured constant**.

Verdict: sub 0 FULL over songlength×1.1 AND byte-exact across two loop-backs
(500 s). Non-medley members byte-identical (all gated on `medley_segs`). Only
`shadow17` needs it; the mechanism generalizes to the full carry set
({spdctr, vsteph, slal, slah}) if a future medley exercises them (all 0 here).

**Bracket that motivated it (historical):** carry-nothing = 1 mismatch,
carry-everything = 5293 (position vars carry player-2's values). The save/restore
is the precise answer: reset all position/effect, carry only the per-player
routing accumulator — reproducing the orig's `$1018`/`$2818` address separation.

**Core tenet note:** tenet-legal — reproduces the mechanism (per-player
accumulator) to match the write stream, not an SMC/verbatim hack.

---

## Productionized (2026-07-31) — DONE

The pipeline now builds the medley automatically:
1. **Detect** — `compilation.detect_medley(sid_path)`: follow the PLAY vector to
   the countdown wrapper (`_parse_medley_wrapper`: two `DEC zp` = counter lo/hi,
   an `LDA zp` dispatch = the segment flag), collect the re-init routines (the
   cold init + the wrapper's `JSR` targets that parse via `_parse_reinit`:
   `LDA #song / JSR canon_base / 3×(LDA #imm/STA zp) / RTS`), require ≥2 distinct
   canonical bases, dense seg-flags. Returns `{bases, segments:[(base_idx, song,
   lo, hi)], play_repeat, kinds}`.
2. **Probe** — the segment schedule falls straight out of the re-init routines
   (counter lo/hi from the STAs keyed by the wrapper's DEC'd addrs; play_repeat
   = the `JSR base+3` count). `write_dmc_medley_usf` emits the `medley` param
   (`0:40:1F,1:64:19`) + `play_repeat` on the merged model.
3. **Wire** — `dmc_build_one.build`, `dmc_family_batch.run_member`, and
   `dmc_mass_write.write_member` all take a `medley` branch (checked after 2SID,
   before compilation/single; records `build_path='medley'`; falls back to
   single on a build exception). `build_dmc_sid` reports PSID `songs=1` for a
   medley (the N segment-subtunes are internal).

**Census** (run `detect_medley` over every `engine IN ('DMC','DMC_V6.x')` path):
it fires on EXACTLY 1 of 10,676 DMC members — Mega_Mix, the sole carrier. Zero
false-positives.
**Gates**: sub 0 FULL via `dmc_build_one --verify`; batch `run_member` = full,
`build_path=medley`; mass-write replay stores self-consistent artifacts (C20
4th-layer verify-from-stored FULL + 5th-layer rebuild-from-stored byte-identical);
smoke 6/6; golden MD5 (10 diverse members) byte-identical; full regression green.
