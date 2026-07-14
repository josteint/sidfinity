<!--
provenance:
  source_url:
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/include/player.asm
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/exporter.asm
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/SWM-spec.src
  local:
    - hvsc84/MUSICIANS/C/Czyszy/ChipMotif.sid        (siddump --writelog ground truth, DRIVERTYPE=0/NORMAL v1.7)
    - hvsc84/MUSICIANS/H/Hermit/Magyar_Nepzenek.sid  (siddump --writelog, v1.4)
    - hvsc84/MUSICIANS/S/Slaxx/Bassloop.sid          (siddump --writelog, v1.8, clean 3-voice + hard-restart)
    - deprecated/gt2_pipeline/tools/sidid.cfg        (player byte-signatures, read-only)
    - tools/siddump.cpp                              (confirmed: writelog = raw bus writes, NO de-dup)
  fetched_via: WebFetch (raw.githubusercontent.com) + siddump --writelog (libsidplayfp ground truth) + Python decode
  fetch_date: 2026-06-13
  author: Mihály Horváth (Hermit) — player.asm $Id rev 390 (2014-07-22)
  content_date: source ~2012–2022; asm pinned to 2014 SVN rev on the anarkiwi master mirror
  reliability: HIGH for the observed per-frame write stream (siddump/libsidplayfp = project ground truth, cross-checked on 3 tunes) and for the verbatim COMMONREGS/SETADSR/HR asm. MEDIUM where flagged OPEN (the exact lean-1-SID emitter source, recovered only as a sidid pattern; the precise vibrato/PW/filter stepping asm).
-->

# SID-Wizard — Per-Frame `$D400-$D418` Write Model

**Scope:** the 1-SID case (`$D400..$D418`). Multi-SID adds `$D420+/$D440+/$D460+` (excluded).

**Verification mode (from `hvsc84.db` census — see `spec_extraction_plan.md` §0):**
- 992 / 1048 tunes have PSID `speed == 0x00000000` ⇒ **vblank 50 Hz** ⇒ **flat Mode-1**
  (`compare_instruction_stream`, per-50Hz-frame, init prefix dropped).
- 56 tunes have `speed == 0x00000001` ⇒ **CIA on subtune 1** (multispeed) ⇒ that subtune needs
  **`siddump --writelog-per-irq`** (per-play() bucketing). No tune sets any speed bit beyond bit 0.
- **All 739 primary-target tunes (`v2 AND init=$1000`) are `speed==0` ⇒ flat Mode-1.**

**Ground-truth tooling note (verified in `tools/siddump.cpp`):** `--writelog` emits
`engine.getWriteLog(0)` = the **raw libsidplayfp CPU write log**, every store to `$D4xx` with
`(cycle, reg, value)`, **with NO de-duplication**. So the per-frame `|W:` chunk is the *true bus
write order*. Within a frame the **order matters**; the **cycle timestamps do not** (Mode 1).

---

## 1. Voice dispatch order: V3 → V2 → V1 (descending), filter last

`play` ($10F1, verbatim, ChipMotif) processes channels in **descending** order:

```
$10F1: A5 FE / 48 / A5 FF / 48      ; push ZP $FE,$FF (PLAYERZP)
       A2 0E   LDX #$0E    ; =14 -> channel-3 base (2*7)
       20 73 11  JSR $1173          ; process channel 3
       A2 07   LDX #$07    ; =7  -> channel-2 base
       20 73 11  JSR $1173          ; process channel 2
       A2 00   LDX #$00    ; =0  -> channel-1 base
       20 73 11  JSR $1173          ; process channel 1
```

`X = 0 / 7 / 14` = the per-channel 7-byte stride (see ZP §5). **Every observed frame on all three
test tunes emits V3's registers, then V2's, then V1's, then the filter** ($17,$18,$16,$15). This
matches `COMMONREGS` iterating `X` from `2*7` down to `0` step `-7`.

Filter tail order (observed, every frame): **`$17` (RES/FILT) → `$18` (MODE/VOL) → `$16` (FC hi)
→ `$15` (FC lo)**.

---

## 2. Two register-flush implementations (driver-variant dependent)

### 2a. COMMONREGS — full ghost flush (multi-SID / `ALLGHOSTREGS_ON`)

Verbatim (`.if (feature.ALLGHOSTREGS_ON || SID_AMOUNT>1)` branch):

```asm
COMMONREGS              ;CALCULATING AND WRITING COMMON SID REGISTERS - ENTRY POINT FOR EDITOR
        .if (feature.ALLGHOSTREGS_ON || SID_AMOUNT>1)
        ldx #2*7
        sec
loop3   lda SIDG.SR,x
        sta SID.SR,x
        lda SIDG.AD,x
        sta SID.AD,x
        lda SIDG.FREQ,x
        sta SID.FREQ,x
        lda SIDG.FREQ+1,x
        sta SID.FREQ+1,x
        lda SIDG.PLSW,x
        sta SID.PLSW,x
        lda SIDG.PLSW+1,x
        sta SID.PLSW+1,x
        lda SIDG.WAVE,x
        sta SID.WAVE,x
        ...                ; (SID2/SID3 copies under .if SID_AMOUNT>=2 / >=3, then:)
        txa
        sbc #7
        tax
        bcs loop3          ; next channel down (X -= 7)
        .fi
```

⇒ Per channel this writes **SR, AD, FREQ-lo, FREQ-hi, PW-lo, PW-hi, WAVE** (the BACKGROUND's
"SR, AD, Freq, PW, Waveform" — confirmed for this path), unconditionally, every frame. This is the
path used by **2-SID/3-SID tunes** and any 1-SID build with `ALLGHOSTREGS_ON`. The multi-SID sidid
signature is exactly this loop: `A0 ?? 99 ?? ?? 88 10 ?? A0 ?? 99 00 D4 99 ?? ?? 88`.

Ghost-register block (verbatim):
```asm
SIDG .block             ; Ghost registers for buffering SID writes
FREQ .word ?            ;SID'S FREQUENCY GHOST-REGISTER
PLSW .word ?            ;SID'S PULSEWIDTH GHOST-REGISTER
WAVE .byte ?            ;SID'S WAVEFORM/CONTROL GHOST-REGISTER
AD   .byte ?            ;SID'S ATTACK/DECAY GHOST-REGISTER
SR   .byte ?            ;SID'S SUSTAIN/RELEASE GHOST-REGISTER
     .fill (CHN_AMOUNT-1)*7
     .bend
```

### 2b. Lean 1-SID emitter (DRIVERTYPE NORMAL/MID/LIGHT/BARE, `ALLGHOSTREGS_ON` off)

**This is the path the common HVSC tunes use, and its observed order is NOT the COMMONREGS order.**
The lean path does **not** rewrite all 7 registers every frame — it writes only what the per-voice
interpreter touches that frame:

- **Steady frame** (note held, no envelope change): per voice **Freq-lo, Freq-hi, CTRL** only
  (PW only if the pulse program stepped; no AD/SR).
- **Note-start frame:** per voice **AD, SR, Freq, CTRL** (ChipMotif/Magyar) — see §3.

Observed steady frame (Bassloop, verbatim decode):
```
V3.Flo=0D V3.Fhi=0E V3.CTRL=1A   V2.Flo=0D V2.Fhi=0E V2.CTRL=1A   V1.Flo=0D V1.Fhi=0E V1.CTRL=1A
RES/FILT=00 MODE/VOL=0F FC.hi=00 FC.lo=00
```
Observed steady frame (ChipMotif): `V3.Flo V3.Fhi V3.CTRL  V1.Flo V1.Fhi V1.CTRL  <filter>`
(a voice that emits nothing that frame is simply absent — e.g. V2 when idle).

The lean emitter's SID writes are absolute `9D xx D4` (`STA $D4xx,X` with X = chip-relative voice
offset), reading source bytes via `B1 ??` (`LDA (PLAYERZP),Y`). The sidid `(SidWizard_V1.?)`
signature is exactly this emitter (verbatim from `sidid.cfg`):
```
B1 ?? 9D 05 D4 C8 B1 ?? 9D 06 D4 A9 ?? 9D ?? ?? 3D ?? ?? 9D ?? ?? 9D 04 D4 60
;       ^$D405=AD      ^$D406=SR              ^(merge)        ^$D404=CTRL
```
⇒ AD→SR→…→CTRL, written directly to `$D4xx` (not via a ghost-flush loop).

**Why the lean path differs from COMMONREGS (resolved):** in the
`ALLGHOSTREGS_ON==0 && SID_AMOUNT==1` build, **`SIDG = SID`** — i.e. the "ghost" registers are
*aliased directly onto the `$D4xx` chip addresses*, so every interpreter store to a ghost IS a bus
write (SETADSR writes `$D405/$D406` directly, the freq/wave writes hit `$D400/$D401/$D404`,
SETPWID hits `$D402/$D403`). There is no end-of-frame flush loop in this build; the per-frame `$D4xx`
stream is emitted incrementally by the per-channel routine as it runs. (This is documented at the
source level in the sibling doc `github_player_writemodel.md` §3, line "`SIDG = SID`"; it is the
source-side explanation of the empirical stream captured here.)

**OPEN (residual):** the exact instruction order *within* the lean per-voice writer (`$1173`) —
which determines the per-driver note-start order knob in §3 — should still be pinned by
disassembling `$1173` from `ChipMotif.sid` (`tools/seed_disassembly.py`); the emitter is the
`B1 ?? 9D 05 D4 … 9D 06 D4 … 9D 04 D4` sidid pattern.

---

## 3. Note-start order & Hard-Restart (HR)

### Note-start register order — **driver-variant dependent**

Observed per-voice note-start sequences (verbatim decode):

| Tune (driver/ver) | per-voice note-start order |
|---|---|
| ChipMotif (NORMAL, 1.7) | **AD, SR, Freq-lo, Freq-hi, CTRL** |
| Magyar_Nepzenek (1.4) | **AD, SR, Freq-lo, Freq-hi, CTRL** (`V1.AD=C2 V1.SR=C0 V1.Flo V1.Fhi V1.CTRL`) |
| Bassloop (1.8) | **Freq-hi, SR, AD, CTRL** (`V3.Fhi V3.SR V3.AD V3.CTRL`) |

⇒ **AD-vs-SR ordering and whether Freq precedes ADSR differs between builds.** The composer must
parametrise this (a per-driver write-order knob), exactly as the Hubbard/FC composers do for
`nextvoice_write_order`-style differences. Do **not** assume a single fixed order.

AD/SR are written **only at note-start / instrument change**, via SETADSR (verbatim):
```asm
SETADSR ldy #4          ;SR
        lda (PLAYERZP),y ;READ 'SUSTAIN & RELEASE'
        sta SIDG.SR,x
        dey             ;3 ;AD
        lda (PLAYERZP),y ;READ 'ATTACK & DECAY'
        sta SIDG.AD,x
```
(reads instrument bytes `SWI_SR_POS=4` then `SWI_AD_POS=3`).

First-frame waveform (verbatim):
```asm
SETWFR1 ldy #$0F        ;POSITION OF 1ST FRAME WAVEFORM
        lda (PLAYERZP),y
        sta WFGHOST,x   ;1ST FRAME WAVEFORM
```
(reads instrument byte `$0F` = first-frame waveform; written to the WF ghost.)

### Hard-Restart — gated by instrument control byte (byte 0)

Control-byte bit map (verbatim player comment):
```asm
lda (PLAYERZP),y ;(bit0-1:HRtimer, bit2:HRgateoff, bit3:TestbitHR, bit4-5:vib.type, bit6:pulseresetOFF, bit7:filtresetOff)
```

HR trigger (verbatim):
```asm
        lda #2          ;SIGN TICK2 TO HARDRESTART-ROUTINE
HARDRST ldy CURNOT,x    ;CHECK FOR HARD-RESTART
        beq NONEWNO     ;IF NO NEW NOTE STARTING, NO HR
        cpy #$60        ;IF NOTE-FX (>=$60), DON'T PERFORM HR
```
⇒ HR happens only when a **new note** is starting (CURNOT != 0) and it is a real note (< $60, i.e.
not a note-column FX).

The four HR/reset control bits:
- **bit0-1 HRtimer** — number of frames the HR pre-empts (1 vs 2 frame restart).
- **bit2 HRgateoff** — gate-off hard-restart switch.
- **bit3 TestbitHR** — "sexy" test-bit start (sets WAVE test bit `$08` to silence then restart).
- **bit6 pulseresetOFF / bit7 filterresetOFF** — suppress PW/filter reset on note-start (verbatim):
  ```asm
        bit INSCTRL+1   ;CHECK BIT6 - PW-RESET OFF FOR INSTRUMENT...
        bvs ENDPWRESET  ;BIT6 - PW RESET SWITCH
        ...
        bit INSCTRL+1   ;CHECK BIT7 - FILTER-RESET OFF...
        bmi ENDFILRESET
  ```

**Observed HR signature (Bassloop, verbatim decode)** — the audible-silent 1-frame restart:
```
frame~13:  V3.SR=00 V3.AD=00 V3.Flo V3.Fhi V3.CTRL=20   V2.SR=00 V2.AD=00 ... CTRL=50   V1.SR=00 V1.AD=00 ... CTRL=50  <filter>
           ; ADSR forced to $00 + gate bit clear (CTRL even: $20/$50 = waveform set, gate=0)
frame~15:  V3.Fhi V3.SR=F4 V3.AD=00 V3.CTRL=09   V2.Fhi V2.SR=F4 V2.AD=00 V2.CTRL=09   V1.Fhi V1.SR=F4 V1.AD=00 V1.CTRL=09  <filter>
           ; real SR loaded + gate ON (CTRL bit0=1: $09 = gate+test)
```
⇒ The composer must reproduce **the HR pre-frame(s)** (ADSR=$00 + gate-off, optionally test-bit
`$08`) followed by the note frame (real ADSR + gate-on), per the HRtimer/gateoff/testbit bits.
This is the same family of HR mechanics modelled in the Hubbard composer.

---

## 4. Per-frame table stepping (vibrato / PW / filter / arp-chord)

These run inside the per-channel routine and modify the voice's Freq / PW / CTRL / filter each
frame from the instrument's `$FF`-terminated tables (WF-ARP / PW / filter).

- **WF-ARP table** (instrument `$10+`): steps per `SWI_ARP_SPEED_POS` (byte 7) low bits; each entry
  sets the waveform/control and an arp note-offset (the `$Cx` wave-select style). The chord
  (`SWI_DEFCHORD_POS`) adds note-offsets from the chord table.
- **Pulse-width** (`SETPWID`, pointer `SWI_PULSETBPT_POS` byte $A): sweep counter increments to a
  target then advances a row; writes `$D402/$D403` (per-voice PW). **PW absent in a frame ⇒ the PW
  program is flat that frame** (confirmed: steady frames omit PW).
- **Filter** (`FilterProgram` macro, pointer byte $B): band/resonance/cutoff sweep → writes
  `$D415/$D416/$D417` (global). Observed every frame as the `$17/$18/$16/$15` tail.
- **Vibrato** (type from control bits 4-5; depth/speed from `SWI_INSVIBRATO_POS` byte 5, delay
  byte 6) — modulates Freq (verbatim fragment):
  ```asm
        lda VIBRACNT,x
        bne decVcnt
        lda VIBFREQU,x
  ```

**OPEN:** verbatim per-step asm for PW sweep direction-flip thresholds, vibrato triangle vs sine
type, and filter sub-program encoding — recover from the per-channel routine disasm of a real
binary (these affect the exact Freq/PW/cutoff byte stream and must match frame-for-frame).

---

## 5. Per-channel zero-page layout (7 bytes / channel)

Verbatim:
```asm
FREQLO   .byte ?        ;SID.0 LO
FREQHI   .byte ?        ;SID.1 HI
PWLOGHO  .byte ?        ;SID.2 LO
PWHIGHO  .byte ?        ;SID.3 HI
WFGHOST  .byte ?        ;SID.4 WAVEFORM
PTNGATE  .byte ?        ;GATE CONTROL
PWEEPCNT .byte ?        ;PW SWEEP COUNTER
```
Repeated per channel (up to 9 for 3 SIDs × 3 voices). The `X` index in §1/§2 is the channel base
`= voice_index * 7` (V1=0, V2=7, V3=14). `PLAYERZP` ($FE/$FF) is the indirect pattern/data pointer
the per-channel routine reads instrument/pattern bytes through (saved/restored around `play`).

---

## 6. MULPLY — multispeed dispatch (CIA tunes only)

`MULPLY` is invoked between main frames on multispeed (CIA) tunes to advance the per-instrument
tables faster than the note clock. Verbatim:
```asm
MULPLY
ldx #(3-1)*7    ;CHANNEL 3
jsr MULCNTP     ;PLAY INSTRUMENT-TABLE(S)
[... channels 6,9,2,5,8,1,4,7 ...]
jmp COMMONREGS  ;PLAY FILTER TOO
```
`MULCNTP` advances arp/WF (always), and PW / filter **iff** the instrument's multispeed flags are
set (control byte 7: bit6 ⇒ PW multispeed, bit7 ⇒ filter multispeed — §3/extraction §4). MULPLY
ends by falling into `COMMONREGS` so the filter is flushed.

**Relevance:** only the 56 `speed=0x1` tunes drive MULPLY (CIA). For those subtunes, the
`$D4xx` write stream contains **multiple per-IRQ chunks per 50 Hz frame** ⇒ verify with
`--writelog-per-irq`. The 992 vblank tunes never run MULPLY at multispeed (single play() per VBI)
⇒ flat Mode-1.

---

## 7. Init / reset writes (the frame-0 prefix)

`init` ($109C, verbatim) clears the chip then primes first state:
```asm
$109C: 20 61 16     JSR $1661         ; (subtune setup)
       A9 00        LDA #$00
       A0 68        LDY #$68
       99 1E 10     STA $101E,Y       ; zero workspace
       88 / 10 FA   DEY / BPL
       A0 17        LDY #$17          ; =23
       99 00 D4     STA $D400,Y       ; <-- CLEAR $D400..$D417 (universal reset)
       88 / 10 FA   DEY / BPL
```

Observed frame-0 stream (Bassloop, verbatim) — the reset then the first play() in the same VBI:
```
$18=0F $17=00 $16=00 $15=00 $14=00 ... $00=00      ; reset: $18 master-vol=$0F first, then $17..$00 cleared (high->low)
$14=F0 $13=0F $0E=07 $0F=01 $12=1A ...             ; first play(): V3 ADSR+Freq+CTRL, then V2, V1, filter
```

⇒ **Init writes split cleanly per the project's init-trichotomy:** the `$D400..$D417` clear is the
**universal reset** (invisible to USF); `$18 = $0F` (master volume, no filter) is environment/master
priming → USF `init.sid { master_vol }`. There is no exotic per-voice priming beyond the first
play()'s note load. ⇒ **Use `compare_instruction_stream(mode='trichotomy')` if the composer emits
its own reset of a different length; otherwise the flat prefix matches** (the reset is a fixed
24-write descending clear). Re-read `docs/the_trichotomy.md` before finalising the `init.sid`
block.

---

## 8. Summary table — what fires each frame (1-SID lean path)

| Event | Registers written (per voice, in observed order) | Driver-variant note |
|---|---|---|
| Frame 0 init | `$D400..$D417`=0 (desc), `$18`=master-vol | universal reset; then first play() |
| Steady (note held) | Freq-lo, Freq-hi, CTRL (+ PW if program steps) | PW omitted when flat |
| Note-start | AD, SR, Freq, CTRL **or** Freq-hi, SR, AD, CTRL | **order is per-driver** (§3) |
| Hard-restart pre-frame | AD=0, SR=0, CTRL gate-off (± test-bit $08) | gated by ctrl bits 0-3 |
| Every frame, filter tail | `$17` RES/FILT, `$18` MODE/VOL, `$16` FC-hi, `$15` FC-lo | global |
| Multispeed (CIA only) | MULPLY advances tables N× per VBI before COMMONREGS | 56 tunes; per-IRQ verdict |

---

## Leads to follow

- **Disassemble the per-channel routine `$1173` (and `$114E`) from `ChipMotif.sid`** to recover the
  exact lean-path SID write sequence and the note-start order knob — closes the §2b/§3 OPENs. The
  emitter is the `B1 ?? 9D 05 D4 … 9D 06 D4 … 9D 04 D4` sidid pattern.
- **Verbatim PW-sweep / vibrato-type / filter-program asm** (`SETPWID`, `FilterProgram`,
  `VIBRACNT`) — fetch player.asm by byte-range or from the SourceForge SVN viewvc raw export (the
  GitHub raw + WebFetch summariser truncates the file). Needed to match Freq/PW/cutoff byte streams.
- **Confirm the note-start order across all 5 DRIVERTYPEs + each major version** by decoding one
  representative writelog per `(version, drivertype)`; tabulate the per-driver write-order knob.
- **Validate the init-prefix length** the composer must emit vs the original's 24-write descending
  clear; decide flat-prefix vs trichotomy per the dissolution composer's `init_style`.
- **CIA subtunes:** decode a `speed=0x1` tune (one of the 56) with `--writelog-per-irq` to confirm
  MULPLY produces N chunks/VBI and that the per-IRQ comparator aligns.
- **Ear-test reflex:** py65 misses CIA/dispatch bugs — any rebuild must be ear-tested in
  sidplayfp, especially the 56 multispeed tunes.
