# DMC time-medley — WIP (Praiser/Mega_Mix)

**Status (2026-07-31):** composer `playmedley` wrapper written + gated (committed
WIP in `composer_asm.py`); reproduces the medley **byte-exact through the full
tune content** (0 mismatches at songlength 290 s AND at one full cycle 315 s).
**One** write differs at 315.6 s (0.6 s into the loop repeat, in the ×1.1
margin) → verdict `partial`. Root fully traced; fix is a "soft re-init" (below).
NOT productionized (no detection/probe/wiring yet — only builds via the manual
recipe below).

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
rel='MUSICIANS/P/Praiser/Mega_Mix.sid'; hv='hvsc84'
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

## The 1-write residual — FULLY TRACED

Divergence: flat write 500293, siddump frame 15780, cyc $1293 →
`$D417 = $04` (orig) vs `$00` (ours). Res nibble matches ($0); routing nibble
differs (orig routes **voice 3** = $04, ours routes none). Streams re-converge
immediately (exactly ONE write in 505 685).

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

## The fix (TODO) — a "soft re-init" for the medley loop-back

Reproduce the orig `$101D` init's exact carry/reset partition. **Bracket proven
empirically:**
- carry **nothing** (current clean `jsr init`) → **1** mismatch.
- carry the **whole** state block across the loop-back → **5293** mismatches
  (the position vars — trkpl/trkph/patl/path, otrk, patix, pend, curnote,
  vactive… — carry player 2's values, inconsistent with player 1's reloaded
  orderlist).

So the answer is the **precise middle**. At the loop-back (only — the *forward*
switch to player 2 uses a clean init and already matches):
- **RESET** (as the orig init does): `vactive, gatemask, curnote, trkpl, trkph,
  patl, path, transp, dur, pend, patix, trkg, otrk, sectpos` + reload orderlist
  pointers (song 0). Note: `gatemask`/`curnote` priming at the loop-back is the
  orig's *work-file leftover* = player 2's residual, NOT song 0's idle_notes —
  this is the per-cycle analog of the C31 idle_notes fact; may need measuring.
- **CARRY**: `shadow17`($1018), `fres`($1723), `fclaim` + filter sweep
  (`fstep/fframe/fsz/fdu/fbase/fcut/frep/fstop`), `curinst/cinst/volovr`, pulse
  (`pwl..pwstep`), vib (`vibdir..vdep`), wave (`wavepos/fxf/wctrl/guard`),
  `fbl/fbh/accl/acch`, `gla/glb/glsp`, `wnote/durrel/ioff`, `wjmp`,
  `slal/slah`, `dtmpl/dtmph`.

Individual-var carries (`shadow17`, `fres`, `curinst`, `cinst`, filter block) all
left 1 mismatch — the routing bit is produced by the *combination* (a V3 note
routes filter-on only when the whole effect-state carries) while the position
state must simultaneously reset. So implement the whole effect/position split,
not one var.

**Recommended way to nail the reset set precisely:** natively measure which
state addresses the orig `$101D` init actually writes (it clears those, carries
the rest) — e.g. `siddump --pc-watch 101d` capturing before/after, or a py65 run
of the init from a dirtied RAM. The static disasm undercounts (misses
subroutines): it found only `$100C, $1716-$1718, $173B, $D400, $D418` writes.

State-block layout is in `composer_asm.py` at label `state0:` (≤256 bytes, so a
single X-indexed copy loop works). The forward switch stays a clean `jsr init`.

**Core tenet note:** exact-through-songlength already satisfies the tenet ("the
whole song"). The soft re-init is tenet-legal (reproduce the mechanism to match
the write stream — not an SMC/verbatim hack). If it proves too costly, the
fallback is a verify-policy for looping tunes (a member exact through songlength
+ one full loop, diverging only in the ×1.1 tail on looped content, is FULL) —
but that touches the ratified ×1.1 rule and is a user decision.

---

## After green: productionize (also TODO)

Currently the wrapper only runs via the manual recipe. To make the pipeline
build it automatically:
1. **Detect**: play vector → a counter-dispatch wrapper that double-plays and
   time-switches over ≥2 canonical player bases. Route to a medley build path.
2. **Probe the schedule**: read the counter inits ($03/$04 per segment) and the
   segment→player+song map from the wrapper; emit `medley='0:40:1F,1:64:19'`.
3. **Wire**: hook into `dmc_build_one.py` build dispatch + the family batch +
   `dmc_mass_write` (record the build path). Golden byte-identity (non-medley
   unchanged), smoke, regression, commit.
