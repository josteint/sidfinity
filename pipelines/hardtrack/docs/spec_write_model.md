<!--
provenance:
  source_url: n/a (derived from local binaries)
  local:
    - hvsc85/MUSICIANS/W/Wodnik/HT_7_1.sid   (canonical $1000 build; play routine disassembled byte-exact, $10D8..$1587)
    - hvsc85/MUSICIANS/R/Randy/Scortia.sid    (relocation cross-check)
    - pipelines/hardtrack/docs/src/sdk/extracted/PLAYER_V1.0.bin / PLAYER_V1.1.bin (symbol tables)
  fetched_via: hand-written 6502 disassembler (tmp/hardtrack/work/dis.py) + siddump --writelog / --writelog-per-irq (libsidplayfp ground truth)
  fetch_date: 2026-06-13
  author: HardTrack Composer player by Longhair / Milosz Ignatowski (Elysium/Parados); analysis SIDfinity
  content_date: player code 1992; analysis 2026-06-13
  reliability: HIGH — the per-frame write order below was read out of the play disassembly
               AND independently confirmed against the live siddump --writelog stream of
               HT_7_1 (the W:cycle:reg:val triples match the disassembled emit order exactly).
-->

# HardTrack Composer — per-frame SID write model ($D400–$D418)

Companion to spec_extraction_plan.md. This is what the rebuild's write stream must match.
All addresses are for the canonical $1000 build (BASE=$1000); the engine is relocation-
invariant by fixed `BASE+offset` (see extraction plan §1.2, §9).

## 0. Dispatch / multispeed

- PSID `speed = 0` (vblank) for **every** HVSC HardTrack tune. The player installs **no**
  CIA/raster IRQ of its own (grep for `STA $DCxx`/`STA $D0xx` in the $1000 player region:
  zero hits). So the host calls `play()` once per VBI (50 Hz PAL).
- `--writelog-per-irq` shows ~1 play() entry per VBI (HT_7_1: 2879 entries / 3000 frames).
  **There is no internal multispeed in the PSID renders** — the editor's "multispeed up to
  6×" is an authoring-time setting that, when exported to PSID, is baked as plain
  50 Hz playback. **[CORRECTION to research.md / working model: do NOT use the per-IRQ
  CIA verdict path (CLAUDE.md Trap C). Use the flat `--writelog` instruction-stream
  comparator (Mode 1).]**
- A per-tune **tempo divider** runs inside `play()`: `$10DE DEC $10FB / BPL` reloads from a
  per-subtune speed value. This divides which frames advance the song; it does NOT call
  play() multiple times. (Still single-speed at the host level.)
- **V1.1 reportedly adds 4×/6× multispeed machinery** (per `sidid_signature_analysis.md` §5
  and the V1.1 symbol table), but it is **not triggered in PSID renders** — every HVSC SID
  is speed=0 and renders 1×/VBI regardless of version. So the multispeed code path is dead
  for our purposes; treat the family as single-speed. (If a future raw-disk capture exercises
  the multispeed, revisit — but no HVSC tune needs it.)

## 1. play() structure (BASE+$D8)

```
$10D8 LDA $FB / PHA / LDA $FC / PHA      ; save zp pointer
$10DE DEC $10FB / BPL +5 / reload         ; tempo divider
$10E8 LDX #$02                            ; voice loop V3,V2,V1 (X=2,1,0)
  ... per-voice processing (note read, instrument load, macros) ...
$151C voice finaliser: write 5 SID regs for this voice (see §3)
$1540 DEX / BPL -> next voice
$1546 global filter macro -> $D416 (see §5)
$157E $D418 = $10 | $1006                 ; master vol/filter mode (see §6)
$1581 PLA/PLA restore zp / RTS
```

Voices are processed **V3 → V2 → V1** (X counts down 2→1→0). Within each voice the SID
register block base `Y = $16A0,X ∈ {0, 7, 14}` selects V1/V2/V3's `$D400+Y` block.

## 2. Per-voice register block

`Y = $16A0,X`: V1 → $00, V2 → $07, V3 → $0E. So voice V uses `$D400+7·(V-1) .. +6`:
freq-lo($00), freq-hi($01), PW-lo($02), PW-hi($03), ctrl($04), AD($05), SR($06).

## 3. Voice finaliser — the main per-frame writes (BASE+$522)

Disassembled order (and confirmed in the writelog), per voice, every frame the voice is
active:

```
$151C LDY $16A0,X            ; Y = 0 / 7 / 14
$151F LDA $1654,X  STA $D402,Y   ; (1) PW-LO
$1525 LDA $1657,X  STA $D403,Y   ; (2) PW-HI
$152B LDA $164E,X  STA $D401,Y   ; (3) FREQ-HI
$1531 LDA $1651,X  STA $D400,Y   ; (4) FREQ-LO
$1537 LDA $165A,X  AND $169A,X  STA $D404,Y  ; (5) CONTROL = waveform AND gate-mask
```

**Per-voice write order = PW-LO, PW-HI, FREQ-HI, FREQ-LO, CONTROL.** Verified against the
HT_7_1 writelog, e.g. one V3 frame: `…:10:20 …:11:01 …:0F:1D …:0E:46 …:12:60` = reg
$10(PW-lo)=$20, $11(PW-hi)=$01, $0F(freq-hi)=$1D, $0E(freq-lo)=$46, $12(ctrl)=$60. (Here
$0E..$14 is V3's block; the abs reg numbers are $D400+Y.)

- `$165A` = current **waveform/control nibble** (from the wave program, §4). The gate bit
  lives here too once a note is on.
- `$169A` = **gate-mask**: `$FF` normally (gate passes through), `$FE` after a DEL ($61) or
  when the wave program ends (`AND #$FE` clears bit0 = gate-off). So `ctrl = waveform &
  gate-mask` is how note-off is realised without a separate write.

### ADSR ($D405/$D406) — written on instrument-load / note events only
ADSR is **not** rewritten every frame. It is written when a new instrument/note loads:

```
$13A0 LDY $16A0,X
$13A3 LDA $164B,X  STA $D406,Y   ; SR  (from inst SR array)
$13A9 LDA $1648,X  STA $D405,Y   ; AD  (from inst AD array)
$13AF LDA #$09     STA $D404,Y   ; CONTROL = $09  (gate + TEST bit) — hard-restart kick
```

So on a fresh note the order is **SR, AD, then ctrl=$09**. The `$09` (= bit0 gate + bit3
TEST) is the classic **hard-restart**: TEST resets the oscillator phase and silences it for
one frame; the next frame the real waveform (§3 step 5) replaces it. Confirmed in the
writelog: note-on frames show `…:06:SR …:05:AD …:04:09` for the voice, then the following
frame the control becomes the instrument waveform (e.g. `…:04:60`).

### gate-off paths (control = waveform & $FE)
Two code paths write the gated-off control directly: `$11D7` and `$12C8`
(`LDA $165A,X / AND #$FE / STA $D404,Y`), used when a held note's wave program has ended
or a new note is being prepared while the previous still rings. CUT ($62) additionally
zeroes SR: `$1131 LDA #$00 / $1137 STA $D406,Y`.

## 4. Note / instrument / macro → register values

### Note → frequency (§8 of extraction plan)
`note_index = (pattern_note + track_transpose) AND $7F` → into the 96-entry freq tables:
`$D401 ← freqHI[idx]` ($15E8), `$D400 ← freqLO[idx]` ($1588). (Tables: freqLO=BASE+$588,
freqHI=BASE+$5E8.)

### Glissando ($63/$64) → frequency deltas
Gliss replaces the table lookup with an **incremental freq add/sub** (disasm $146E..$14A5):
each frame `freqLO ± gliss_speed` ($1669) with carry rippling into freqHI ($164E):
- up   ($63): `freqLO += speed; if carry: freqHI++`
- down ($64): `freqLO -= speed; if borrow: freqHI--`
USF should model this as a **per-step freq-slide effect** with rate = the `yy` operand.

### Drum / absolute-pitch (FX-byte bit7)
When the instrument FX byte ($176C) has **bit7 set** ($1676 flag), the wave-program **data**
byte ($187C) is written **directly as freq-HI** (absolute pitch), bypassing the note add:
```
$1440 LDA $1676,X (drum flag); if set ->
$1460 LDA $187C,Y  STA $164E,X   ; freq-HI = wave-data byte (absolute)
$1466 LDA #$00     STA $1651,X   ; freq-LO = 0
```
Otherwise ($1445) the wave-data byte is **note-relative**: `if bmi (byte&$80) treat as-is;
else freq-HI = freqHI[(byte + note)&$7F]`. USF: drum instruments carry an absolute-pitch
flag; their "notes" are the wave-program data bytes.

### Waveform program ($186C ctrl / $187C data)
Per active voice each frame, a running index ($16AC) walks the wave-ctrl stream:
- `$FF` → jump: next byte is the new index (loop point).
- `$FE` → end: `DEC $168E` (decrement the "wave running" flag) and hold.
- else → the byte becomes `$165A` (the control/waveform written in §3 step 5), AND its
  paired data byte ($187C) drives freq (above).
The step advances every `$1673` frames (a per-step duration loaded from the pulse program).

### Pulse-width program ($188C) → $D402/$D403
On note-on, pulse sweep is seeded from the instrument arrays: start ($17EC→$16BB), add
($180C→$167F), end/limit ($182C→$1682), plus the pulse-cfg nibbles ($170C) seed the initial
PW (`hi-nib → PW-lo seed $1654`, `lo-nib → PW-hi seed $1657`). Each frame the PW value
sweeps (`$14B8..$1519`): add/subtract `$16BB` toward the `$1682` limit, with a direction
toggle ($16B8 EOR $FF) at the bounds, producing a triangle PW LFO. The result is written as
PW-LO ($D402) / PW-HI ($D403) in §3 steps 1–2. The `$188C` pulse-program stream supplies
(step, dir, duration) triples; `$FF` = jump.

## 5. Filter — one shared filter, two write sites

### $D417 (resonance + routing) — built per-voice when a filtered instrument plays
At BASE+$379 / $39D (disasm $137C..$139D): the instrument's filter routing bits are OR'd
into the global $D417 shadow ($101F) and written:
```
$1373 ORA $1691,X       ; this voice's filter-enable bit
$1376 STA $101F         ; $D417 shadow
$1379 STA $D417         ; ENABLE this voice on the filter
…(when the filtered note ends)…
$1394 LDA $101F / AND $1694,X / STA $101F / STA $D417   ; DISABLE this voice's bit
```
`$1691,X = [$01,$02,$04]` (per-voice ENABLE bit: V1=bit0, V2=bit1, V3=bit2) and
`$1694,X = [$FE,$FD,$FB]` (per-voice CLEAR mask) are **constant tables in the player** (never
written at runtime — verified). So **$D417 is a shared, accumulated register**: each voice's
note-on ORs its enable bit + the instrument's filter byte into the shadow $101F; each note-
off ANDs the bit out via $1694. **Resonance** (high nibble, bits 7–4) comes from the
**instrument filter byte's LOW nibble**, promoted by 4× ASL (`AND #$0F; 0A 0A 0A 0A`) — this
is the exact sidid-signature anchor `0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB
1D ?? ?? 8D ?? ?? 8D 17 D4`. Resonance is whole-chip (set by whichever voice last triggered
a filtered instrument). See `sidid_signature_analysis.md` §2–3 for the full hand-disasm.
A USF rebuild must model $D417 as the running OR/AND of per-voice routing bits + last-set
resonance nibble, NOT as a per-voice snapshot.

### $D416 (filter cutoff hi) — global macro, written once per frame after all voices
At BASE+$546 (disasm $1546..$1576): a single global filter-cutoff macro stream ($189C,
`$80` = jump) advances each frame and writes `$D416`:
```
$156E LDA #$14 / CLC / ADC #$00 / STA $156F / STA $D416   ; cutoff hi
```
There is **one filter for all three voices** (standard 6581/8580); the per-voice $D417 bits
select which voices route through it. **$D415 (cutoff lo) is left at 0 / cleared at init**
— only $D416 (cutoff hi) is automated. In the writelog every frame ends with a `:16:<hi>`
write (reg $16 = $D416).

## 6. $D418 (master volume + filter mode) — written last, every frame

At BASE+$57E:
```
$1579 LDA #$10 / ORA $1006 / STA $D418
```
`$1006` = master-volume shadow (init sets it to `$0F`). `$10` sets the **low-pass filter
mode** bit (FILT bit4). So **$D418 = $1F** every frame in HT_7_1 (`$10 | $0F`). Confirmed in
the writelog: every frame ends `…:18:1F`. **This $D418=$1F-every-frame is the family's
master-vol signature** (cf. the Hubbard `master_vol_every_frame` knob). Fade-outs / volume
changes would alter the `$1006` shadow; the `$10` filter-mode bit is constant.

## 7. Verification recipe (rebuild vs original)

1. `tools/siddump ORIG.sid --writelog` and same for the rebuild.
2. Compare with `pipelines.hubbard.verify_cycle.compare_instruction_stream`
   (flat `(reg,val)` prefix, Mode 1). **Do NOT use the per-IRQ / CIA path** (§0).
3. Localise first divergence with `tools/find_first_divergence.py ORIG REBUILD --subtune N`.
4. Expected per-frame skeleton (active voice): for each of V3,V2,V1 in that order — PW-lo,
   PW-hi, freq-hi, freq-lo, ctrl; ADSR (SR,AD) + ctrl=$09 only on note-on frames; then one
   $D416 write; then $D418=$1F. $D417 writes appear only on filtered-instrument note edges.
5. Subtune frame count = songlength × 1.1 × 50 (per CLAUDE.md `subtune_frames`).
6. **Ear-test** in real sidplayfp (py65 misses dispatch nuances; the tempo divider and the
   hard-restart TEST-bit timing are audible).

## 8. Open / to-confirm

- **V1.0 vs V1.1 (discriminator RESOLVED, write-diff still OPEN):** version tag = $D417
  shadow address $101F (V1.0) vs $101E (V1.1) in the sig region; V1.1's code is shifted
  ~$25 later (extraction plan §10, `sidid_signature_analysis.md` §4). Still OPEN: does V1.1
  change the per-frame *emit order* (vs just shifting addresses + adding the dead multispeed
  block)? Disassemble `Shogoon/Tribute_to_Laxity.sid` (confirmed V1.1) play routine and diff
  the emit order against HT_7_1. Expectation: emit order identical, only addresses shifted.
- **OPEN ($D417 resonance source):** confirm the exact high-nibble (resonance) byte source
  for $D417 — is it from `$184C` (per-inst d416-build) or a global default? Trace a tune
  with audible resonance (e.g. one whose $184C array is nonzero) via
  `tools/effect_chain_profiler.py SID --register 17`.
- **OPEN (gliss carry exactness):** verify the gliss freq add/sub matches the 6502 carry
  behaviour byte-exactly on a tune with $63/$64 commands (find one via pattern decode).
- **CONFIRM (CUT vs DEL audible difference):** $61 (DEL) clears only the gate-mask; $62
  (CUT) also zeroes SR and waveform. Verify both round-trip in the writelog.

## Leads to follow

- Build a `pipelines/hardtrack/<engine>/disassembly.s` from this analysis (annotate the
  $10D8..$1587 play routine with the routine labels mined from the V1.0/V1.1 symbol tables:
  INIT, IRQ, TRTRS/PTPTS, OPSK=gliss, DRUM, PULST/PLSPL, NRWAV/POSWAV, NRPUL/POSPUL,
  D41.FILST/POSFIL, etc.).
- Pick `HT_7_1.sid` as the first migration canary (single subtune, V1.0, clean $1000).
- Confirm the standard write model on a filtered tune and a drum-heavy tune before
  declaring the family's effect dimensions complete.
- Resolve the V1.0/V1.1 fingerprint (extraction plan §10) so the DB can split the family.
