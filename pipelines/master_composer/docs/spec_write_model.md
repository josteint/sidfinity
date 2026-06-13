<!--
provenance:
  source_url: local: tmp/jc64/doc/example/Master_Composer.dis (JC64dis, gzip'd cell format)
             upstream: https://github.com/ice00/jc64
             annotated tune: "Maniac" by Paul Kleimeyer, (c) 1983 Access Software Inc.
  fetched_via: local read of cloned ice00/jc64 at tmp/jc64/ (READ-ONLY); .dis decoded via Python
               re-impl of FileManager.readProjectFile. Write model derived from the annotated
               disasm (tmp/mc_work/maniac_listing.s) and CONFIRMED against libsidplayfp ground
               truth: tools/siddump --writelog / --writelog-per-irq / --memwatch on the real HVSC
               binaries (Maniac, Rondo_3, Mexico_86, Spell_Now, We_the_People, Valentino_intro,
               Allegro_Nr_19, Billboard_Maker).
  fetch_date: 2026-06-13
  author: disasm hand-annotated by Stefano Tognon / Ice Team (JC64dis). Player by Paul Kleimeyer.
  content_date: annotations contemporary; player 1983-1984.
  reliability: PRIMARY. Every write below is quoted from the disasm AND matched to a siddump
               writelog frame. Cycle TIMESTAMPS within a frame are observation (Trap B); the
               (reg,val) order is the verdict.
-->

# Master Composer — per-frame $D400-$D418 write model

Companion to `spec_extraction_plan.md`. The Mode-1 verification target is the
`$D400-$D418` write stream per `play()` invocation. **This engine is CIA-timed (PSID
`speed=1` for 984/1019 tunes), so the verdict path is per-IRQ (`siddump --writelog-per-irq`),
not flat-50 Hz.**

---

## 1. Dispatch (the dual clock)

```
playSound ($7587):  LDA #$00 : BNE doPlaySound : RTS
   ; "play+1" is patched non-zero by init; while running, BNE is taken.
doPlaySound ($75BC):  DEC speedCounter : BEQ generateSound : RTS
```
- **Outer clock = CIA-1 Timer A.** `play()` fires every Timer A underflow. The period is loaded
  per block from `timerALo/timerAHi[block]` in `setTimer` ($7699):
  `STA $DC04 / STA $DC05`, then `LDA $DC0E : ORA #$10 : STA $DC0E` (force-load + start). Maniac's
  per-block TimerA = `$4293`. MEASURED play() rate (libsidplayfp `--memwatch |P`): ~53 Hz for
  Maniac. (PSID `speed=1` ⇒ sidplayfp drives `play()` from the tune's CIA timer, NOT 50 Hz VBI.)
- **Inner clock = `speedCounter`/`blockSpeed`.** Each `play()` decrements `speedCounter`; only the
  `blockSpeed`-th call (Maniac `blockSpeed=6`) reaches `generateSound` and advances a note step.
  So note-steps fire at `CIA_rate / blockSpeed` (Maniac ≈ 53/6 ≈ 8.8 steps/s).

⇒ Two kinds of `play()` frame in the write stream:
1. **Step frame** (every `blockSpeed`-th): full note processing — see §3/§4.
2. **Idle frame** (the other `blockSpeed-1` calls): `DEC speedCounter : RTS` — **emits NO writes.**

> CONFIRMED in the per-IRQ capture: a `|I:`-with-writes bucket appears once per `blockSpeed`
> frames; the intervening frames emit an empty `|I` (no writes). The flat per-50 Hz capture
> mis-buckets these (Trap C) — hence the per-IRQ verdict.

---

## 2. Block-start register burst (the "switch instrument" snapshot)

On a **block change** (`setTimer` → `setBlockSpeed` → `outTimbre`), `outTimbre` ($762A, +$0AA)
writes the FULL per-block SID snapshot, indexed `,X = blockIndex`. **Exact write order** (the
verdict; from `maniac_listing.s`, byte-matched to the siddump burst at cycles 321..445):

| # | Register | Source table | Maniac burst (block 1) |
|---|----------|--------------|------------------------|
| 1 | `$D405` V1 AD | `AttackDecayV1` | `05:09` |
| 2 | `$D40C` V2 AD | `AttackDecayV2` | `0C:4A` |
| 3 | `$D413` V3 AD | `AttackDecayV3` | `13:4B` |
| 4 | `$D406` V1 SR | `SustainReleaseV1` | `06:00` |
| 5 | `$D40D` V2 SR | `SustainReleaseV2` | `0D:09` |
| 6 | `$D414` V3 SR | `SustainReleaseV3` | `14:09` |
| 7 | `$D402` V1 PW lo | `waveLoV1` | `02:99` |
| 8 | `$D409` V2 PW lo | `waveLoV2` | `09:FF` |
| 9 | `$D410` V3 PW lo | `waveLoV3` | `10:99` |
| 10 | `$D403` V1 PW hi | `waveHiV1` | `03:01` |
| 11 | `$D40A` V2 PW hi | `waveHiV2` | `0A:07` |
| 12 | `$D411` V3 PW hi | `waveHiV3` | `11:05` |
| 13 | `$D417` Res+routing | `filterRes` | `17:00` |
| 14 | `$D418` filter-mode+vol | `filterVol` | `18:4C` |
| 15 | `$D415` cutoff lo | `filterCutLo` | `15:03` |
| 16 | `$D416` cutoff hi | `filterCutHi` | `16:28` |

Notes:
- **`outTimbre` does NOT write `$D404/$D40B/$D412` (control/waveform/gate).** Waveform+gate come
  from `ctrlVn[block]` inside the note routines (§3/§4). So a block change updates ADSR / pulse /
  filter / volume only; the waveform is applied per-note.
- **`$D418` carries BOTH the master volume (low nibble) and the filter mode bits** (`filterVol`
  table). Maniac block 1 = `$4C` (vol $C + high-pass). Note a transient `$D418=$0F` is written by
  siddump/PSID at play-entry on the very first frame (cycle 40) BEFORE the burst — that is the
  player/host idle value, not `outTimbre`; `outTimbre`'s `18:4C` overwrites it.
- The burst occurs ONLY when the block index actually changes (a new block in the page run, or a
  measure rollover that lands on a new block). On step frames within the same block, no burst —
  just the per-note writes of §3.

---

## 3. Per-note writes (per step frame, all three voices)

`generateSound` advances `noteIndex`/`measureIndex`/`blockIndex`/`pageIndex`, then the V1/V2/V3
note routines read one byte per voice from the measure record and act. Per voice, **note byte
semantics** (verified against the data + writelog):

| Note byte | Action | Writes |
|-----------|--------|--------|
| `$00` | rest / skip | **none** (gate left as-is) |
| `1..$63` | pitched note (1-based freq index) | freq lo/hi + ctrl gate-retrigger (§4) |
| `$64` | release / note-off | `ctrlVn[block] AND #$FE → $D40{4,B,12}` (gate off, **1 write**, waveform kept) |

Pitched-note path (`outNoteV1` $7737 verbatim; V2/V3 analogous at +$20/+$30 data offset):
```
outNoteV1:  TAY
  LDA frequencyLo,Y : STA $D400     ; V1 freq lo
  LDA frequencyHi,Y : STA $D401     ; V1 freq hi
  JSR outCtrlV1                      ; gate retrigger (§4)
```
| Voice | freq lo | freq hi | ctrl | data offset within measure record |
|-------|---------|---------|------|-----------------------------------|
| V1 | `$D400` | `$D401` | `$D404` | `+$10..$1F` |
| V2 | `$D407` | `$D408` | `$D40B` | `+$20..$2F` |
| V3 | `$D40E` | `$D40F` | `$D412` | `+$30..$3F` |

VERIFIED freq link: note `$18` → `frequencyLo[$18]=$30`, `frequencyHi[$18]=$04` ⇒ writelog
`00:30 01:04`. Note `$37` → `$1E,$19` ⇒ `07:1E 08:19`. Byte-exact.

---

## 4. The gate retrigger (control-register writes) — verbatim

`outCtrlV1` ($7831): each pitched note writes `$D404` **twice** — gate-off then gate-on:
```
outCtrlV1:  LDX blockIndex
  LDA ctrlV1,X : AND #$FE : STA $D404   ; gate OFF (waveform from ctrlV1[block], bit0 cleared)
               : ORA #$01 : STA $D404   ; gate ON  (same waveform + gate)
```
- ⇒ writelog per pitched note: `04:40` then `04:41` (Maniac ctrlV1=$41 ⇒ pulse+gate; `$40`=pulse
  no-gate). The **double write is mandatory in the stream** (a hard retrigger / new ADSR attack
  every note — there is no legato/tie). Same for V2 (`$D40B`) and V3 (`$D412`).
- The **waveform nibble lives in `ctrlVn[block]`** (per block, not per note): bit4 triangle, bit5
  saw, bit6 pulse, bit7 noise + ring/sync bits 1-2. So all notes in a block share the waveform;
  pitch comes from the freq table; the gate is re-struck per note.
- A `$64` release writes `$D40{4,B,12}` ONCE with gate cleared (no `ORA #$01`).
- The release writelog frame is a "short bucket": e.g. `|I:13073:04:40:13132:0B:40:13191:12:40`
  (three gate-off writes, no freq) — these are the alternating release cells in the note stream.

**Frame write order (the verdict), per step frame:**
1. (block change only) `outTimbre` burst — 16 writes in the §2 order.
2. V1 note: `$D400,$D401` (if pitched) then `$D404,$D404` (gate off,on) — OR `$D404` once (release) — OR nothing (rest).
3. V2 note: `$D407,$D408` then `$D40B,$D40B` — etc.
4. V3 note: `$D40E,$D40F` then `$D412,$D412` — etc.
There is NO separate filter/vol writer per step (filter+vol are block-burst only). No
per-frame vibrato/PWM/arp — **the engine has zero runtime effects** (confirmed: idle frames emit
nothing; step frames emit only the above).

---

## 5. Sequencing + bar-duration timing

```
generateSound ($75C4):
  LDY blockIndex : LDA blockSpeed,Y : STA speedCounter   ; reload inner clock
  INC noteIndex
  ; measure-end test: if noteIndex > notesInMeasure[block]  -> nextMeasure
  ; (the disasm compares against the per-block 'notes' / notesInMeasure cache and
  ;  the measureTable/noteTable start markers)
nextMeasure ($77DA):  INC measureIndex : noteIndex = 1 : setAddr   ; advance one measure
nextBlock ($75F1):    INC blockIndex
  ; if blockIndex > toPage[pageIndex] -> nextPage ; else setTimer (new block burst)
nextPage ($7602):     INC pageIndex
  ; if pageIndex > lastPage -> stopSound ; else setPage
setPage ($7690):      blockIndex = fromPage[pageIndex]
```
- **Note resolution is fixed 16th-notes** (≤16 notes/measure at `noteIndex` 1..`notesInMeasure`).
  There is **no per-note duration**; the "bar duration" is encoded as *which note cells are rests
  ($00) vs releases ($64) vs pitched* — a held note = pitched cell followed by `$00` rests (gate
  stays on); a staccato note = pitched cell followed by `$64` release. The **tempo** (real time
  per 16th) = `CIA period (timerA) × blockSpeed`.
- **`notesInMeasure[block]`** sets how many of the 16 cells are used (Maniac block 1 = `$10` = all
  16; other blocks `$0C`/`$0A`). `measureTable[block]`/`noteTable[block]` give the block's entry
  measure + note. Indices are **1-based** (`pageIndex`/`blockIndex`/`measureIndex`/`noteIndex` all
  init to 1; tables read `table-1,X`).
- **Page run:** page `p` plays blocks `fromPage[p]..toPage[p]`; advancing past `toPage[p]` moves to
  page `p+1`; past `lastPage` → `stopSound`. CONFIRMED via `--memwatch`: `pageIndex`/`blockIndex`/
  `noteIndex` increment exactly as above (Maniac stays page 1 / block 1, `noteIndex` 1→2→… per
  step frame).

---

## 6. Verification mode (Mode 1, per-IRQ)

- PSID `speed=1` (984/1019) ⇒ **CIA-timed** ⇒ use `siddump --writelog-per-irq`
  (`writelog_per_irq_capture` per CLAUDE.md), dropping the init prefix, and flat-compare the
  flattened play stream. The flat per-50 Hz capture buckets the ~53 Hz CIA `play()` out of phase
  (Trap C) and will spuriously diverge.
- The 23 `speed=0` tunes are pure VBlank ⇒ the standard flat per-frame path applies to them.
- **OPEN / tooling caveat:** for Maniac the `--writelog-per-irq` splitter produced ~9 write-bearing
  buckets/s while `--memwatch |P` counts ~53 `play()`/s. This is consistent (only every
  `blockSpeed`=6th play() emits writes; idle frames are empty `|I`), BUT confirm the per-IRQ
  splitter aligns mine-vs-orig correctly when the rebuild uses a different init length / a
  cleaner dispatch (the empty-`|I` idle frames must line up). Validate the rebuild's per-IRQ
  stream against the orig with `find_first_divergence.py`/the per-IRQ comparator before declaring
  a tune FULL. If the splitter under-buckets, prefer the `--memwatch |P`-aware path or compare the
  flattened step-frame stream (idle frames carry no signal).
- WITHIN a frame: order matters (gate off→on retrigger, the §2 burst order, $D418 written after
  $D417); cycle timestamps do not (Trap B).

---

## 7. End-of-song behavior + the "decaying hum"

`stopSound` ($7610) fires when `pageIndex > lastPage`:
```
stopSound:  NOP                 ; (was SEI; NOPed — "PSID hack" comment)
  LDA #$1B : STA $DC04          ; reset CIA Timer A lo
  LDA #$41 : STA $DC05          ;            hi
  LDA #$00 : STA play+1         ; clear the run flag (playSound now returns early)
  NOP×6
  JMP gateOff                   ; clear gate bit0 on all 3 voices, then RTS
gateOff ($758D):  LDA $D404 : AND #$FE : STA $D404   ; (V1; then V2 $D40B, V3 — see bug below)
```
- After `stopSound`, `play+1` is 0 ⇒ every subsequent `play()` is `LDA #$00 : BNE … (not taken) :
  RTS` — **the engine emits no further writes**, but the CIA keeps firing play() (idle) and the
  SID is left with: gate cleared, **waveform + ADSR + volume unchanged**. With a non-zero release
  and the oscillator still selected, the voices ring down audibly = the documented **"decaying hum
  after the final page."** `stopSound` does NOT zero `$D418` and does NOT clear the waveform.
- **`gateOff` bug (verbatim, $75A2):** the third voice's gate-off mistakenly writes `STA $D404`
  again instead of `STA $D412` — i.e. V3's gate is never actually cleared by `gateOff`:
  ```
  LDA $D404 : AND #$FE : STA $D404   ; V1
  LDA $D40B : AND #$FE : STA $D40B   ; V2
  LDA $D412 : AND #$FE : STA $D404   ; <-- reads V3 ctrl but writes V1 ctrl (original-binary bug)
  ```
  This leaves V3 gated/sustaining at song end — a concrete contributor to the hum, and a
  per-stream artifact the rebuild must reproduce **iff verification extends past song end**
  (normally it does not — see below).
- **Practical impact on the verdict:** `verify_all` checks the rebuild over the overlap up to
  ~songlength×1.1. HVSC songlengths for this family are the natural LOOP/END point; most tunes
  observed (Rondo_3, Mexico_86, We_the_People, Spell_Now, Allegro, Billboard_Maker) keep playing
  through the window (long page lists / genuine loops) and never reach `stopSound` inside it. So
  the hum is **usually outside the verified window** and need not be modeled to pass. Flag it
  OPEN: confirm no verified tune terminates early, and if one does, reproduce the `stopSound` +
  buggy `gateOff` write tail exactly (it is a finite, deterministic sequence, fully in-spec — NOT
  an escape hatch).
- **No loop record in the data:** there is no explicit "loop to page N" marker; a song either runs
  out of pages (→ stopSound) or `lastPage` covers a page list whose tail repeats content. The
  editor's IRQ (`irqRoutine` $77F8) resets `pageIndex=1` on its own re-entry, but that path is the
  editor IRQ (patched out / not the PSID play path). OPEN: determine, per tune, whether the
  intended end is stop-with-hum or a content loop, and encode the USF song-end accordingly
  (finite page list + "stop" vs a loop point). For the wide batch, the safe default is: emit the
  page list verbatim; let the rebuild stop where the orig stops.

---

## 8. Summary write-stream shape (one block, one measure)

```
[block change]                                              <- step frame, blockIndex advanced
  $D405 $D40C $D413 $D406 $D40D $D414   (AD/SR ×3)           outTimbre burst (16 writes, §2 order)
  $D402 $D409 $D410 $D403 $D40A $D411   (PW lo/hi ×3)
  $D417 $D418 $D415 $D416               (res, mode+vol, cut lo/hi)
  V1: $D400 $D401 $D404 $D404 | $D404 | (none)              note | release | rest
  V2: $D407 $D408 $D40B $D40B | $D40B | (none)
  V3: $D40E $D40F $D412 $D412 | $D412 | (none)
[same block, next step]                                     <- step frame, no burst
  V1/V2/V3 note writes only (freq + gate retrigger, or release, or nothing)
[idle frames ×(blockSpeed-1)]                               <- NO writes
```

---

## Leads to follow
- **Confirm the player-variant taxonomy.** Maniac (sig +$1E4) vs Poole_Chris Star_Trek_II (sig
  +$1A3, only 1434/2752 leading bytes match) prove ≥2 code variants. Build a reloc-invariant
  fingerprint (à la `tools/engine_fingerprint.py`) over the 1019 tunes to enumerate variants +
  their table-base maps BEFORE a wide batch. Close with: per-tune sidid offset + `outTimbre`
  operand dataflow. (Binary: every Master_Composer `.sid`; tool: a new `mc_fingerprint`.)
- **Resolve the freq-table length + index range.** Tables are 95 (lo) / 96 (hi) bytes; note bytes
  are 1..$63 (=99). Determine whether indices >95 ever occur in real data and how the engine
  treats them (off-table read). (Binary: scan all note-data regions for max note byte; trace the
  freq read for n>95.)
- **Pin the measure-end comparison exactly.** §5 paraphrases the `notesInMeasure`/`measureTable`/
  `noteTable` test in `generateSound` ($75C4-$75E0); transcribe the exact branch conditions
  (`measureTable` vs `measureIndex`, `notesInMeasure` vs `noteIndex`, `notes` vs `noteIndex`) so
  the USF measure/block entry-point fields are unambiguous. (Source: maniac_listing.s $75C4..$75F0.)
- **Note-cell duration semantics across tunes.** Verify the "$00 rest holds gate / $64 releases /
  pitched retriggers" reading produces note durations matching the audible rhythm on a melodic
  tune (not just the Maniac note/release alternation). (Tool: decode + re-synthesize a slow tune,
  e.g. a hymn like Deck_the_Halls; ear-test.)
- **CIA period → effective Hz vs the computed value.** Maniac timerA byte = `$4293` ⇒ computed
  57.8 Hz but measured ~53 Hz play() rate. Reconcile (sidplayfp PAL frame model / which timer
  value is live at runtime / whether the editor IRQ re-programs it). Matters for tempo fidelity in
  the rebuild. (Tool: `--memwatch DC04,DC05` + `|P` count; `--pc-trace` over the first second.)
- **End-of-song decision per tune.** Detect, per tune, whether the verified window reaches
  `stopSound`; if so, reproduce the `stopSound` + buggy `gateOff` (V3-not-cleared) write tail.
  Decide the USF representation of song-end (finite "stop" vs content loop). (Tool: `--memwatch
  pageIndex,lastPage` to the end of songlength×1.1; `find_first_divergence` at the tail.)
- **Multi-subtune tunes (16/1019).** A few tunes have 2-7 (one =64) songs; the page/block/freq
  data layout per subtune is unconfirmed (separate page tables? a startsong offset?). (Binary: the
  16 multi-song tunes from the DB census.)
- **JC64dis decode is reproducible** from `tmp/mc_work/read_dis.py` (+ `merge_listing.py`); when
  starting the migration, seed `pipelines/master_composer/standard/disassembly.s` from the merged
  listing and hand-annotate the header per the `migrate` skill.
