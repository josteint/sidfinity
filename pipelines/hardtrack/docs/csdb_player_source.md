# HardTrack Composer — Player Source (decoded)

> **Provenance**
> - source: `local: pipelines/hardtrack/docs/src/sdk/extracted/RELEASE_NOTES.bin`
>   (= assembled V1.0 player @ $1000 + demo tune), cross-referenced against
>   `PLAYER_V1.0.bin` / `PLAYER_V1.1.bin` (tokenised Elysium turbo-assembler SOURCE)
>   and against the canonical HVSC tune `hvsc84/MUSICIANS/W/Wodnik/HT_7_1.sid`.
> - fetched_via: local artifacts (Elysium SDK, already extracted) + py65 disassembly
>   (`tools/seed_disassembly.py` on `HT_7_1.sid`) + recovered symbol table from the
>   tokenised sources.
> - fetch_date: 2026-06-13
> - author: **Brush** (editor code) + **Longhair / Milosz Ignatowski** (player routine),
>   Elysium / Parados (Poland), 1992.
> - content_date: 1992 (V1.0 player), V1.1 player slightly later.
> - reliability: **primary** — disassembly of the released player binary; label names
>   recovered from the released assembler source.

---

## 0. What this file is

The **highest-value deliverable**: the actual HardTrack Composer player routine,
disassembled byte-exact from the released binary and annotated with the original
author's label names (recovered from the released `.SRC` symbol table). Everything
here is the live runtime that all ~1,170 HVSC HardTrack tunes execute.

The player code occupies **$1060–$1587** (~1,320 bytes) in the canonical $1000 build.
- `init` = `$1000: JMP $1060`
- `play` = `$1003: JMP $10D8`  (the source label is `IRQ`)

The sidid (cadaver) reloc-invariant fingerprint for this engine is:
```
0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB 1D ?? ?? 8D ?? ?? 8D 17 D4
```
which is exactly the filter-resonance emitter at **$1360–$137C** below (`ASL ASL …
ORA $1691,x … STA $D417`). Confirmed against `cadaver/sidid`.

---

## 1. Recovered symbol table (the Rosetta Stone)

The tokenised `PLAYER_V1.0.bin` carries a 323-entry symbol table (names are PETSCII
with the high bit set on the terminating char). Polish abbreviations, decoded:

| Label | Meaning (PL→EN) | Role |
|-------|-----------------|------|
| `INIT`, `IRQ` | init / play(=IRQ) | entry points |
| `NRTUNE`, `NRTUNEQ` | numer tune / tune-speed | subtune index / per-subtune speed |
| `TR` / `TRS` | track ptr lo / hi | live order-list (track) pointer |
| `PT` / `PTS` | pattern ptr lo / hi | live pattern pointer |
| `TRPOS` / `PTPOS` | track / pattern position | index into track / pattern stream |
| `SPEEED` | speed | frame speed counter |
| `PETLA1`/`PETLA2` | pętla = loop | loop counters |
| `PRZES` | przesunięcie = transpose | transpose accumulator |
| `STRONA` | strona = page | (hi byte of a pointer) |
| `ZMIEN` | zmień = change | "change instrument/voice" path |
| `DELAY` | delay | note-off / DEL handling |
| `KASAD` | kasuj ADSR = clear ADSR | gate-off / hard-restart |
| `NRDRUM`/`PRDRUM` | numer/przeszukaj drum | drum-macro index / scan |
| `WAV` / `NRWAV` / `POSWAV` | wave / nr / pos | waveform macro: table, index, position |
| `PULST`/`PLS`/`PL` / `NRPUL`/`POSPUL`/`CZASPUL` | pulse / czas=time | pulse macro: table, index, pos, timer |
| `FILST` / `NRFIL`/`POSFIL`/`CZASFIL` | filter / czas | filter macro: table, index, pos, timer |
| `ARP` | arpeggio | arp table |
| `WOLNE`/`WOLNE1`/`WOLNE2` | wolne = slow | half/quarter-speed (multispeed divider) |
| `D416`/`D417`/`D418`, `OD41x`/`AD41x`/`PD41x` | SID regs + OR/AND/POKE-into | filter/volume register handlers |
| `GORA` (`OPUSZ`) | góra/opuszczanie = up/down | glissando up / down |
| `START`, `KBYTE`, `SBYTE` | start / kolejny=next / czytaj=read byte | stream-decode helpers |

(Full 323-symbol dump is in `src/` decode logs; the table above is the subset
that maps onto live code.)

---

## 2. Memory map (canonical $1000 build, V1.0)

### 2.1 Vectors + config ($1000–$105F)
```
$1000  JMP init ($1060)
$1003  JMP play ($10D8)         ; source label IRQ
$1006  master volume nibble     ; OR'd with $10 → $D418 every frame (filter-mode|vol)
$1007..$1009  current note per voice (after transpose, &$7F)   [3-byte array]
$100A..$100C  TRACK base ptr lo per voice  (copied from subtune table)
$100D..$100F  TRACK base ptr hi per voice
$1010..$1012  PATTERN ptr lo per voice (live)   init=$F5
$1013..$1015  PATTERN ptr hi per voice (live)   init=$11
$1016..$1018  TRPOS  (track-stream position) per voice
$1019..$101B  PTPOS  (pattern-stream position) per voice
$101C..$101E  per-voice transpose base (note from pattern, &$7F)
$101F  filter resonance/routing shadow (mirrors $D417)
$10E4  (subtune-dependent constant copied from $16C4,x table)
$10FB  global multispeed/frame divider (init = NRTUNEQ+1)
```

### 2.2 Per-voice runtime state (3-byte arrays, indexed by X = voice 0/1/2)
All at $16xx. Byte `+0`=voice0, `+1`=voice1, `+2`=voice2.

| Addr | Symbol | Meaning |
|------|--------|---------|
| `$164E` | freq HI work | current frequency hi (→ $D401) |
| `$1651` | freq LO work | current frequency lo (→ $D400) |
| `$1654` | PW LO work | pulse-width lo (→ $D402) |
| `$1657` | PW HI work | pulse-width hi (→ $D403) |
| `$165A` | waveform/ctrl | base control byte (gate ORed in) (→ $D404) |
| `$165D` | (track-jump flag scratch) | set on $FE/$FD track commands |
| `$1660` | current pattern byte | the byte being decoded this step |
| `$1663` | glissando active flag | set by `$63`/`$64` pattern cmds |
| `$1666` | glissando direction | 0=up ($63), 1=down ($64) |
| `$1669` | glissando rate | yy operand of `$63`/`$64` |
| `$166C` | pulse one-shot flag | pulse-sweep one-direction latch |
| `$166F` | global SPEEED reload | per-step duration (note length) |
| `$1670` | vibrato/arp depth work | per-step pitch add (arp/vib) |
| `$1673` | arp step counter | counts down arp table steps |
| `$1676` | filter-enable mask | $80 if this instr drives the filter |
| `$1679` | pulse speed reload | `CZASPUL` |
| `$167C` | POSWAV | waveform-macro position pointer |
| `$167F` | pulse step add | per-tick PW delta |
| `$1682` | pulse limit | PW sweep bound |
| `$1685` | "$6F" tie/portamento flag | set on pattern byte $6F |
| `$1688` | prev waveform index latch | for waveform-macro `$176C` lookups |
| `$168B` | waveform index work | |
| `$168E` | KASAD / note-cut counter | gate-off / hard-restart frame counter |
| `$1691` / `$1694` | filter on / off masks | OR mask / AND mask into $D417 |
| `$1697` | "new note" (ZMIEN) flag | triggers instrument (re)load |
| `$169A` | gate AND-mask | $FE clears gate, $FF keeps; AND'd into ctrl |
| `$169D` | PRZES (transpose accumulator) | signed, applied from track stream |
| `$16A0` | **SID voice reg offset** | constant {0, 7, 14} — selects $D400/$D407/$D40E |
| `$16A3` | "song ended" flag (per voice) | set on track $FE → routes to $1540 (silence) |
| `$16A6` | pulse outer counter | |
| `$16A9` | arp/slide sign | from waveform-macro entry |
| `$16AC` | POSWAV-2 / arp-table position | per-voice arp position pointer |
| `$16B2` | note-delay counter | counts frames before note starts |
| `$16B5` | pulse speed base | |
| `$16B8` | pulse direction toggle | EOR $FF flip |
| `$16BB` | pulse current value work | |
| `$16BE` | current instrument index | `WF` (waveform/instrument number) |
| `$16C1` | previous instrument index | for change detection |
| `$16C4` | (NRTUNEQ copy) | per-subtune speed const |
```

### 2.3 Data tables (song-specific, addresses shift per build)
| Region (HT_7_1) | Symbol | Contents |
|-----------------|--------|----------|
| `$1588` (96 B) | freq LO | note→freq lo, 8 octaves × 12 |
| `$15E8` (96 B) | freq HI | note→freq hi |
| `$18A2`/`$18AA` | TR lo/hi table | per-subtune track (order-list) start ptr (≤8 subtunes; `AND #$07`) |
| `$18B2`/`$18BA` | PT lo/hi table | per-subtune pattern-base ptr |
| `$18C2`/`$18CA` | (aux hi tables) | per-subtune secondary base ptrs |
| `$16C4` | NRTUNEQ | per-subtune speed (e.g. 3,3,3,2,2,2,2,2) |
| `$194A`/`$195F` | pattern ptr lo/hi | per-pattern-number start pointers |
| `$16CC..$182C` | instrument macro tables | AD ($16CC), SR ($16EC), wave-ctrl ($170C/$172C/$174C), pulse params ($176C/$178C/$17AC/$17CC/$17EC/$180C/$182C), filter sel ($184C) — 32-entry instrument bank, indexed by `$16BE` |
| `$186C`/`$187C` | arp / wave-relative tables | walked via $16AC (`$FF`=loop-to / `$FE`=stop) |
| `$188C` | per-note pitch-control table | (vibrato/arp control words, `$FF`=loop) |
| `$189C` | global filter program | `$80 xx`=set position, terminated; drives $D416/$D417 |

---

## 3. The init routine ($1060)

```asm
init:                       ; $1060  (A = subtune number)
    AND #$07                ; ≤ 8 subtunes
    TAX
    LDA $18A2,X : STA $100A ; copy subtune's TR lo  → live ptr (v0)
    LDA $18BA,X : STA $100D ; … TR hi
    LDA $18AA,X : STA $100B
    LDA $18C2,X : STA $100E
    LDA $18B2,X : STA $100C
    LDA $18CA,X : STA $100F
    LDA $16C4,X : STA $10E4 ; per-subtune speed const (NRTUNEQ)
    LDA #$0F    : STA $1006 ; master volume nibble = $0F
    ; clear SID $D400..$D41C
    LDA #$00 : TAX
.clr_sid:                   ; $1095
    STA $D400,X : INX : CPX #$1D : BNE .clr_sid
    ; per-voice state init (X = 0..2)
    LDX #$00
.voice_init:                ; $109F
    LDA #$00
    STA $1019,X  ; PTPOS = 0
    STA $1016,X  ; TRPOS = 0
    STA $16AF,X  ; (effect flag)
    STA $16A3,X  ; song-end flag = 0
    STA $169D,X  ; PRZES = 0
    STA $1697,X  ; new-note flag = 0
    STA $16BE,X  ; instrument = 0
    LDA #$F5 : STA $1010,X  ; PT ptr lo seed
    LDA #$11 : STA $1013,X  ; PT ptr hi seed
    LDA #$FE : STA $169A,X  ; gate AND-mask = $FE
    LDA #$01 : STA $16C1,X  ; prev-instr = 1
              STA $168E,X  ; KASAD counter = 1
    INX : CPX #$03 : BNE .voice_init
    TAY : INY : STY $10FB   ; frame divider = subtune speed + 1 (here 4)
    RTS
```

Note `$16AF,x` is a per-voice effect-state byte (referenced at play but not in the
recovered name table prefix; treated as "glissando/effect pending" flag).

---

## 4. The play routine ($10D8 = source label `IRQ`)

Top-level shape: save zp $FB/$FC, decrement the global frame divider `$10FB`
(reload to 3 when it underflows — this is the **multispeed divider**), then run the
**per-voice loop** for X=2,1,0, then emit the global filter/volume.

```asm
play:                       ; $10D8
    LDA $FB : PHA           ; preserve zp scratch
    LDA $FC : PHA
    DEC $10FB
    BPL .voices
    LDA #$03 : STA $10FB    ; reload divider (HT_7_1: const 3; build-dependent)
.voices:                    ; $10E8
    LDX #$02                ; process voice 2, then 1, then 0
.voice_loop:                ; $10EA
    LDA $16A3,X : BNE ->$1540   ; song ended for this voice → just emit SID, skip
    LDA $16AF,X : BNE ->$1272   ; effect pending → pulse/$D417 path ($1272)
    ; (dispatch over a 2/1/0 selector — here falls through to step-advance)
    ...
```

### 4.1 Pattern-byte decoder ($1108–$1177)
Reads the next pattern byte via `($FB),Y` where `$FB/$FC`=pattern ptr, `Y`=PTPOS.
Special bytes:

| Byte | Symbol | Action |
|------|--------|--------|
| `$60` | (rest/tie) | keep current note (jump to $117A "read fx") |
| `$61` | (note-off) | set gate AND-mask $169A=$FE (gate off), continue |
| `$62` | (hard cut) | zero SR ($D406,y=0), clear $165A, set KASAD `$168E`=1 |
| `$63 yy` | `GORA` | glissando **up**: flag $1663=1, dir $1666=0, rate $1669=yy |
| `$64 yy` | `OPUSZ` | glissando **down**: flag $1663=1, dir $1666=1, rate yy |
| `$6F` | tie/portamento | set $1685 (skip retrigger) |
| `$80–$FF` | set-instrument | `AND #$7F` → new note number → $101C,x + $16AF,x effect-pending |
| `$00` | end-of-pattern | falls through to track-advance ($11DD) |

After the note byte, a following byte with `$6F` selects portamento; otherwise the
low 5 bits choose the next instrument slot (`AND #$1F`, latched into $16BE/$16C1).

### 4.2 Track / order-list advance ($11DD–$1271)
When a pattern ends, read the **track stream** via `($FB),Y`, Y=TRPOS:

| Byte | Action |
|------|--------|
| `$00–$7F` | pattern number → look up `$194A,n`/`$195F,n` → load pattern ptr |
| `$80–$FC` | (signed) change transpose `PRZES` ($169D += (byte&$7F)) |
| `$FD nn` | jump to track position nn (set TRPOS) |
| `$FE` | end / stop → set $16A3,x=1 (this voice silent) → $1540 |
| `$FF` | loop track to start (TRPOS=0), set end-flag scratch $165D |

A new pattern number `LDA $194A,y / STA $1010,x` (lo) and `$195F,y / STA $1013,x`
(hi) installs the pattern start pointer; PTPOS resets implicitly via the next read.

### 4.3 Instrument / new-note load ($12CE "KBYTE")
When `$1697,x` (new-note flag) is set, load the instrument macro from the 32-entry
bank indexed by `$16BE,x`:
- AD ← `$16CC,instr`, SR ← `$16EC,instr` (→ $D405/$D406)
- waveform/ctrl program pointers ← `$170C/$172C/$174C` etc.
- pulse params (`$176C..$182C`), filter-select ← `$184C,instr`
- note → freq via `$15E8,note`/`$1588,note` (after transpose `+$1007,x`, `&$7F`)
- gate the voice: `LDA #$09 : STA $D404,y` (gate on + triangle/test as base ctrl).

The filter-resonance write (the sidid signature) lives in this path at $1360–$137C:
```asm
$1360: ASL A : ASL A         ; (left-shift instrument's filter nibble)
$1364: STA $157A             ; self-mod filter-program operand
$1367: PLA : AND #$F0 : STA $FB
$136C: LDA $101F : AND #$0F : ORA $FB
$1373: ORA $1691,X           ; per-voice filter-enable mask
$1376: STA $101F : STA $D417 ; resonance + filter routing
```

### 4.4 Per-tick effect engine ($13B7 onward)
Run every play() call (every multispeed tick):
- **arp / pitch table** ($13B7): `DEC $1673,x` step counter; walk `$188C` pitch words
  (`$FF`=loop to next, low bit→direction, value→`$1670` per-tick add). Adds/subtracts
  into the working frequency hi/lo with carry into $164E.
- **waveform macro** ($141D `WAV`): walk `$186C`/`$187C` via `$16AC`; `$FF nn`=loop to
  nn, `$FE`=stop+`DEC $168E` (KASAD). Each entry sets `$165A` (waveform/ctrl). A
  signed entry (bit7) is an absolute note (drum), else `+$1007,x` (relative) → freq.
- **glissando** ($146E): if `$1663,x` set, add/sub `$1669,x` (rate) to/from freq with
  carry, direction in `$1666,x`.
- **pulse macro** ($14A8–$1519 `PULST`): note-delay `$16B2`; sweep `$16BB` by `$167F`
  step toward `$1682` limit; direction toggle via `$16B8` EOR $FF; reload `$1679`
  from `$16B5`; writes accumulate into PW work `$1654/$1657`.

### 4.5 SID emit ($151C) — per voice
```asm
.emit:                       ; $151C
    LDY $16A0,X              ; SID voice reg offset {0,7,14}
    LDA $1654,X : STA $D402,Y   ; PW lo
    LDA $1657,X : STA $D403,Y   ; PW hi
    LDA $164E,X : STA $D401,Y   ; freq hi
    LDA $1651,X : STA $D400,Y   ; freq lo
    LDA $165A,X : AND $169A,X : STA $D404,Y  ; ctrl (gate masked)
```
Then `$1540`: `DEX : BMI .global : JMP .voice_loop`.

### 4.6 Global filter + volume ($1546 onward)
Once all 3 voices done:
```asm
.global:                     ; $1546
    DEC $166F : BNE .vol     ; (filter-program step timer)
    ; walk filter program $189C via Y/$154C; $80 nn = jump, else set $1572 + reload
.vol:                        ; $156E
    LDA #$14 : CLC : ADC #$00 : STA $156F : STA $D416   ; FC hi (cutoff)
    LDA #$10 : ORA $1006 : STA $D418   ; $10|vol nibble → filter-mode|volume
    PLA : STA $FC : PLA : STA $FB
    RTS
```
The `$D416`/`$D418` order (filter cutoff then volume) matches the siddump writelog
tail (`…:16:xx … :18:1F`) observed on HT_7_1.

---

## 5. Verified write model (siddump ground truth, HT_7_1)

Per play() the player writes, in order: for each voice (loop order **V3, V2, V1**):
`PW_LO, PW_HI, FREQ_HI, FREQ_LO, CTRL` (and on new-note also `AD, SR`), then once
globally: `$D416` (filter cutoff hi) and `$D418` (= `$1F` = filter-mode bits 4 + vol
$0F). Multispeed is achieved by calling play() N× per VBI via CIA timer (PSID
`speed`-bit driven externally; the divider `$10FB` further subdivides note advance).

This per-frame ordered `(reg,val)` stream is the SIDfinity verification target
(Mode 1 — frame-by-frame instruction sequence; see docs/the_core_tenet.md).

---

## 6. Caveats for the extractor

- **Build-dependent addresses.** $16xx/$18xx/$19xx are song-data regions; their
  absolute addresses shift per packer/relocator. Extract them relative to the live
  pointers the init copies (`$100A–$100F`), not by hardcoded address.
- **≤8 subtunes** (`AND #$07`); the per-subtune speed lives in the `NRTUNEQ` table.
- **Two assembled layouts in HVSC** (see `csdb_release_notes_and_versions.md`):
  the V1.0 layout (init→$1060, play→$10D8, $18xx tables; RELEASE_NOTES.bin + HT_7_1)
  and a later Bzyk/Samar-relocated layout (init→$1080, play→$1061, $16xx tables;
  ~118 tunes). Same engine semantics, shifted bytes.
- The `$16AF,x` "effect pending" byte and the `$1697,x` "new note" byte are the two
  dispatch flags that branch the per-voice loop into the pulse/$D417 path ($1272)
  vs the instrument-load path ($12CE) vs the step-advance path.
