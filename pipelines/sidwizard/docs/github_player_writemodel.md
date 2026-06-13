# SID-Wizard — per-frame `$D400-$D418` write model (`player.asm`)

> **Provenance**
> - source_url: https://github.com/anarkiwi/sid-wizard (mirror of https://sourceforge.net/p/sid-wizard/code)
> - raw file: `https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/include/player.asm`
> - fetched_via: curl (raw.githubusercontent.com)
> - fetch_date: 2026-06-13
> - author: Hermit (Mihály Horváth)
> - content_date: SID-Wizard 1.x line, 64tass syntax (`player.asm` ~rev 382; freq tables annotated "values taken from player.asm of SID-Wizard 1.2")
> - reliability: **primary** (the player macro actually compiled into exported SID files)

This documents the player's frame model: register write **order**, ghost/shadow
buffering, hard-restart, table stepping, and multispeed (MULPLY). This is the
Mode-1 verification target (per-`play()` `(reg,val)` sequence).

The player is a 64tass **macro** (`player .macro`, ends `player_top`/
`playercode_end`, player.asm:2868) compiled into 5 driver variants
(bare/light/medium/normal/extra) via `feature.*` switches and into 1/2/3/4-SID
builds via `SID_AMOUNT`. Same logic; features gate code in/out.

---

## 1. Entry points (player.asm:65)

```asm
inisub  jmp INITER      ; INIT subtune (A = subtune number)
playsub jmp PLAYER      ; the "main" frame (advance pattern rows + tables, write SID)
mulpsub jmp MULPLY      ; multispeed intermediate tick (advance instrument tables only)
```

The PSID header's init vector points at `inisub` (1×) or `CIAINIT` (multispeed);
the play vector at `playsub` (1×) or `CIAPLAY` (multispeed). See
`github_exporter_layout.md` §3-4.

---

## 2. SID register equates (player.asm:23-58)

For each SID chip (`SIDBASE`/`SID2BASE`/`SID3BASE`, default `$D400`):
```
SID.FREQ = SIDBASE+0   ; $D400/01 frequency (16-bit, per voice +0)
SID.PLSW = SIDBASE+2   ; $D402/03 pulse width (12-bit)
SID.WAVE = SIDBASE+4   ; $D404 waveform/control
SID.AD   = SIDBASE+5   ; $D405 attack/decay
SID.SR   = SIDBASE+6   ; $D406 sustain/release
FCUT  = SIDBASE+21     ; $D415/16 filter cutoff (11-bit)
RESFC = SIDBASE+23     ; $D417 resonance + filter routing
FMVOL = SIDBASE+24     ; $D418 filter mode + main volume
```
Voice stride within a chip is **7** (`SID.x + voice*7`); the player indexes
everything by `X = (channel-1)*7`.

---

## 3. Ghost / shadow registers (player.asm:134-197)

Two register banks exist depending on the build:

- **Per-voice musical ghosts** at the head of the ZP variable block
  (always present), 7-byte bunches:
  ```
  FREQLO  (SID.0)  FREQHI (SID.1)  PWLOGHO (SID.2)  PWHIGHO (SID.3)  WFGHOST (SID.4)
  PTNGATE          PWEEPCNT
  ```
  These map 1:1 onto `$D400-$D404` and hold the value the player *computes*
  for the voice during the frame.

- **The flushable `SIDG` block** (player.asm:184): `FREQ .word / PLSW .word /
  WAVE / AD / SR`, 7-byte bunch per voice.
  - If `feature.ALLGHOSTREGS_ON` **or** `SID_AMOUNT>1`: `SIDG` is a separate RAM
    buffer; `COMMONREGS` copies it to the real SID at end of frame (§4).
  - If `ALLGHOSTREGS_ON==0` **and** `SID_AMOUNT==1`: **`SIDG = SID`**
    (player.asm:196) — writes go *directly* to `$D400+`; the buffered flush loop
    is omitted. This is a **driver-variant difference** in the emitted write
    stream: lighter drivers write registers as they compute them; heavier
    drivers (and all multi-SID) batch the flush. The per-frame *set* of writes is
    equivalent, but the within-frame interleaving differs.

Filter ghost bits live in self-modified operands (`FLTBAND+1`, `FLTBAN2+1`, …,
player.asm:349) rather than a RAM ghost.

---

## 4. The register write-out — `COMMONREGS` (player.asm:600) — VERBATIM ORDER

This is the canonical per-frame `$D4xx` write order. The flush loops over voices
with `X = 2*7, 1*7, 0*7` (i.e. **voice 3, then 2, then 1**), and per voice writes:

```asm
loop3   lda SIDG.SR,x       ; -> sta SID.SR,x        ($D406) Sustain/Release   FIRST
        lda SIDG.AD,x       ; -> sta SID.AD,x        ($D405) Attack/Decay
        lda SIDG.FREQ,x     ; -> sta SID.FREQ,x      ($D400) Freq lo
        lda SIDG.FREQ+1,x   ; -> sta SID.FREQ+1,x    ($D401) Freq hi
        lda SIDG.PLSW,x     ; -> sta SID.PLSW,x      ($D402) PW lo
        lda SIDG.PLSW+1,x   ; -> sta SID.PLSW+1,x    ($D403) PW hi
        lda SIDG.WAVE,x     ; -> sta SID.WAVE,x      ($D404) Waveform/control  LAST
        ; (SID2 block, then SID3 block, same 7-write order, for multi-SID)
        txa : sbc #7 : tax  ; next voice down
        bcs loop3
```

**Per-voice write order is fixed: SR, AD, FREQ-lo, FREQ-hi, PW-lo, PW-hi,
WAVEFORM.** The repeated source comments are load-bearing intent:
> "important to keep some distance between SR/AD and Waveform-setting for more
> reliable notestart" and "keep distance from ADSR setting … for more reliable
> notestart".

i.e. ADSR is written *before* the waveform (so the gate edge in WAVE lands after
the envelope rates are latched). Match this order in the rebuild.

### Then the global filter block (per chip), in this order:
```asm
FSWITCH lda #$00          ; filter-switch nibble (self-mod; ext.filter / BigFX-$1F)
RESONIB ora #...          ; resonance nibble (upper 4 bits)
        sta SID.RESFC     ; -> $D417   (resonance + routing)
MAINVOL lda #$0F          ; main volume nibble (self-mod; SEQ-FX MAINVOL delays this)
FLTBAND ora #...          ; filter-band bits (hi nibble)
        sta SID.FMVOL     ; -> $D418   (filter mode + main volume)
        ; ... optional filter keyboard-track / slowdown math ...
wrCtfHi sta SID.FCUT+1    ; -> $D416   (cutoff hi 8 bits)
CTFLGHO lda #...          ; -> sta SID.FCUT+0  ($D415 cutoff lo nibble; only if FINEFILTSWEEP_ON)
```

So the **global** write order each frame is: `$D417` (RESFC), `$D418` (FMVOL),
`$D416` (FCUT hi), then `$D415` (FCUT lo, only in drivers with fine filter
sweep). `$D415` lo is deliberately *not* keyboard-tracked ("for rastertime
reasons", player.asm:711).

**Overall per `play()` frame:** voices flushed 3→2→1 (7 writes each), then the
filter group `$D417,$D418,$D416[,$D415]`. (For multi-SID, voices of SID2/SID3
are interleaved inside the same `loop3` pass — voice3 of all chips, then voice2
of all chips, etc.)

---

## 5. INITER — subtune init (player.asm:256)

```
- SETSTUNE: select subtune (set seq pointers, subtune tempo) from A
- INIPVAR : zero the whole VARIABLES block (all counters/pointers/rowdata)
- SID clear: ldy #$17 ; sta SIDBASE,y down to 0   => writes $D400..$D417 = 0
             *** $D418 is deliberately LEFT OUT *** (player.asm:339:
             "$d418 is left out from init, so pop/clip might be less noticeable")
- reset self-mod filter operands: FLTBAND+1, FLSHIFT+1, CKBDTRK+1 (per chip)
```

**Extraction note (matches the project init-trichotomy principle):** the init
write set is a clean SID reset of `$D400-$D417` (no `$D418`) plus zeroed engine
state — i.e. universal reset + (per-subtune) priming via the subtune's first
play(), *not* a hand-tuned init write sequence. The first `playsub` then
establishes `$D418` (main volume `$0F` default via `MAINVOL`). Use trichotomy /
universal-reset comparison if rebuilding with a different init length.

---

## 6. PLAYER — the main frame (player.asm:540)

```
[optional SLOWDOWN frame-skip]
[optional ZP save]
for channel in 3,2,1  (multi-SID: 3,6,9, 2,5,8, 1,4,7):   ; voice-3-first
    jsr DOTRACK
jmp COMMONREGS                                            ; flush ghosts -> SID
```
Channel processing order is **3 → 2 → 1** (player.asm:555/579/589). `DOTRACK`
computes the ghost registers for one voice; the actual SID writes happen once,
at the end, in `COMMONREGS` (§4).

### DOTRACK per-voice flow (player.asm:855)
1. **Tempo**: compare `SPDCNT,x` to current tempo (`TEMPOTBL`, indexed via
   `TMPPOS`/tempo-program). On wrap → advance to next pattern row (TICK_0). Bit7
   of a tempo byte = "single tempo"; funktempo alternates two values row-by-row.
2. **TICK_0 — read a new pattern row** (player.asm:894):
   - Set ZP pointer to current pattern via `PPTRLO/PPTRHI[CURPTN]` (`p_ptnl1/h1`).
   - Reset one-shot fields `CURIFX`, `CURFX2`; reset `MAINVOL` self-mod to `$0F`
     (SEQ-FX main-volume is delayed to here).
   - **Decode the row columns** (this is the on-disk pattern encoding, §8):
     - read note byte; `$70..$77` = packed-NOP run (RLE rest), expands to N rests
       via `PACKCNT`; note `< $80` ⇒ **end of row**; note `>= $80` ⇒ instrument
       column follows (clear bit7 → `CURNOT`).
     - read instr/smallfx byte; `< $80` ⇒ end of row; `>= $80` ⇒ FX column
       follows (clear bit7 → `CURIFX`).
     - read FX byte → `CURFX2`; if `(fx & $E0) != 0` it's a **small-FX** (end of
       row); else it's a **big-FX** ($01..$1F) and one more **value byte** is
       read → `CURVAL`.
   - Store the new pattern position in `PTNPOS,x`.
3. **Hard-restart** decision (§7), then note start / instrument table run
   (`CHKNOTE`, `CNTPLAY`).
4. On other (non-row) ticks: `MULCNTP`-style table stepping only.

---

## 7. Hard-restart (HR) (player.asm:998-1066)

HR runs on the tick *before* a new note (TICK2 / the frame before a row that has
a note), to silence the envelope cleanly. Driven by the instrument **control
byte** (offset 0): bits0-1 = HR timer length, bit2 = gate-off HR (staccato),
bit3 = test-bit HR.

```asm
HARDRST ldy CURNOT,x        ; only if a real note is coming (<$60) and not legato/portamento
...
; load upcoming instrument's control byte; AND with HR-timer mask
ISHARDR and (PLAYERZP),y    ; extract 2-frame HR switch-bit
        beq HRENDER         ; if not yet HR frame, skip (but also skip PW/filter)
HRGTOFF lda #$FE
        sta PTNGATE,x       ; gate-off (WF-arp muting)
        and WFGHOST,x : sta WFGHOST,x   ; clear gate bit in waveform ghost
        ; HARDRESTYPES_ON: write the instrument's HR-ADSR:
        ldy #2 : lda (PLAYERZP),y : sta SIDG.SR,x   ; HR-SR  (instrument byte 2)
        ldy #1 : lda (PLAYERZP),y : sta SIDG.AD,x   ; HR-AD  (instrument byte 1)
        ldy #0 : lda (PLAYERZP),y : and #4          ; gate-off HR (control bit2)?
        beq HRENDER
        lda #$18 : sta WFGHOST,x : sta SIDG.WAVE,x  ; TEST+mute waveform ($18), keep oscillator
        rts
; (else, default-HR build): SIDG.AD = >DEFAULTHRADSR, SIDG.SR = <DEFAULTHRADSR
```

So in an HR frame the player writes (via the §4 flush): the gate-cleared
waveform (and `$18` if staccato/gate-off HR), and the instrument's HR-AD / HR-SR
(instrument bytes 1,2) into AD/SR. `DEFAULTHRADSR` is the fallback when the
build only supports a single HR-ADSR (`feature.HARDRESTYPES_ON` off).

---

## 8. Pattern / instrument addressing during play

- `CURPTN,x` → pattern number; pattern base = `PPTRLO/PPTRHI[CURPTN]`
  (player code sites `p_ptnl1`,`p_ptnh1`). `PTNPOS,x` walks bytes within it.
- `CURINS,x` → instrument number; instrument base = `INSPTLO/INSPTHI[CURINS]`
  (sites `p_insl1/2/3/4/5`, `p_insh*`). The instrument's tables (wave/pulse/
  filter) are read relative to that base (offsets in instrument bytes $A,$B and
  the gate-off pointers $C,$D,$E; first wave-arp at +$10). See
  `github_swm_format.md` for the 16-byte instrument layout.
- These `p_*` operand sites are exactly the ones the exporter patches with the
  runtime data addresses (`DataPtr`/`PtrValu`, `github_exporter_layout.md` §7).

---

## 9. Vibrato / pulse / filter table stepping

The instrument runs three programmable tables each frame the note is held:

- **Wave-arp table** (`WFARPTB`, player.asm:1758) — per-frame waveform/arpeggio.
  Bytes: relative pitch `$00..$7E`, `$7F`=chord-call, `$80`=NOP/hold,
  `$81..$DF`=absolute notes, `$E0..$FF`=negative relative pitch, `$FE`=jump
  (next byte = table index), `$FF`=end/loop (from `swm.h` `SW1_ARP_*`).
- **Pulse table** (`SETPWID`, player.asm:1694) — steps pulse-width program;
  `PWTPOS,x` is the index, `PWEEPCNT` the sweep-length timer; writes `PWLOGHO/
  PWHIGHO` ghosts. PW-reset can be disabled per instrument (control bit6).
- **Filter table** (`FILTPRG`, player.asm:1676) — steps the filter program
  (cutoff/band/resonance) into the self-mod filter operands; filter-reset can be
  disabled per instrument (control bit7).

**Vibrato** (player.asm:165-169 state: `FREQMODL/H`, `VIDELCNT`, `VIBFREQU`,
`VIBRACNT`): a delayed, exponential pitch wobble. Instrument byte5 hi-nibble =
amplitude (indexes the exponential freq table), lo-nibble = frequency; byte6 =
vibrato delay (or amplitude-increase speed for "increasing" vibrato type, control
bits4-5). Vibrato amplitude uses the same exp-table as slides but the input value
is halved. The exp/frequency tables are reproduced in `swm.h`
(`SWexpTabH/SWexpTabL`, `SWvibFreq`) — see `github_swm_format.md` §6.

---

## 10. MULPLY — multispeed intermediate tick (player.asm:782)

On a multispeed tune, the CIA fires `framespeed` times per musical frame.
`framespeed-1` of those go through `mulpsub`→`MULPLY`; the wrap one goes through
`playsub`→`PLAYER` (see `github_exporter_layout.md` §3).

```
for channel in 3,2,1 (multi-SID 3,6,9,2,5,8,1,4,7):
    jsr MULCNTP        ; advance instrument tables only (no new pattern row)
jmp COMMONREGS         ; flush ghosts -> SID (incl. filter)
```

`MULCNTP` (player.asm:822): skips if `ARPSCNT,x` is still `$FF` (don't clobber
the 1st-frame waveform). Reads the instrument's **arp-speed byte (offset 7)**:
- bit7 set ⇒ step **filter table too** (`MULTIFI`→`FILTPRG`)
- bit6 set ⇒ step **pulse table too** (`MULTIPW`→`SETPWID`)
- else ⇒ step **wave-arp table only** (`WFARPTB`)

So multispeed re-emits the full SID register set each IRQ, but only the
table-driven voices change between the main frame and the intermediate ticks.

**Verification:** capture per-`play()` with `siddump --writelog-per-irq` (the
project's CIA-tune path) — one musical frame = `framespeed` IRQs; align the
flattened play stream after dropping the init prefix.

---

## 11. Driver-variant write-stream differences (summary)

| Variant | Ghost flush | Notable feature gates |
|---|---|---|
| bare | direct (`SIDG=SID`) if 1SID | minimal FX; smallest |
| light / medium | mix | progressively more `feature.*` on |
| normal | typically buffered | full standard FX chain |
| extra | `ALLGHOSTREGS_ON` | every reg ghosted; +3-4 rasterlines |

Key gates that change the emitted stream: `ALLGHOSTREGS_ON` (direct vs batched
writes), `FINEFILTSWEEP_ON` (`$D415` lo written or not), `FILTKBTRACK_ON`
(cutoff hi modulated by note), `HARDRESTYPES_ON` (per-instrument HR-ADSR vs a
single `DEFAULTHRADSR`), `TEMPOPRGSUPP_ON`, `MULTISPEEDSUPP_ON`,
`SEQ_FX_SUPPORT_ON`, `CHORDSUPPORT_ON`, `PACKEDNOPSUPP_ON`. The driver type is
recorded in the SWM header offset `$13` (`DRIVERTYPE_POS`) and selects the
`altplayers.inc` size/pointer tables at export. For extraction, the **resulting
`$D4xx` write set per frame is the invariant** to match (Mode 1), regardless of
which variant produced it.
