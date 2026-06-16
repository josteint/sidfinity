# MoN/Deenen Follow-up CSDb Research Findings

## Provenance

- source_urls: CSDb release IDs 10604, 10759, 10760, 10761; Monase_1.0.d64; Music Mania #1/#2.D64; Bjerregaard_J_James_Bond_3.asm; sidid.cfg
- fetched_via: WebFetch (CSDb pages) + binary download of D64 disk images (csdb.dk/getinternalfile.php) + local sidid.cfg file
- fetch_date: 2026-06-16
- reliability: HIGH for disk image and .asm file contents (direct binary); MEDIUM for CSDb page metadata (HTTP 503 on some pages)

---

## 1. CSDb Release 10604 — "FCS Future Composer V1.0" (NOT an FCS editor for MoN)

**Finding:** CSDb #10604 is not the "FCS editor for MoN player" as originally suspected. It is **Future Composer V1.0 by Finnish Gold / Charles Deenen (20 June 1988)**, released as "FCS's Future Composer no: 00.18 v1.0". It contains four SID music files (compositions). No technical documentation of the MoN player format is present. The CSDb description notes code by Charles Deenen (MoN/Scoop) and Finland Cracking Service. This is the early Deenen FC editor, not the SFX editor.

---

## 2. Monase Disk Image — CONFIRMED CONTENTS

CSDb releases 10759 / 10760 / 10761 all resolve to the same two download archives:

### Music Mania.zip (file ID 575, 37.4 KB compressed)
Contains two D64 disk images:
- `Music Mania #1.D64` (174848 bytes, 1998-10-29) — DEMONSTRATION DISK, contains 10 music entries (A–J) across two disks labelled "MUSIC MANIA/HYPE". Supplied by "MEGATRONIX PD, 21 Tiled House Lane, Pensnett, Brierley Hill, West Midlands DY5 4LG, Tel: (0384) 77172". **No tools.**
- `Music Mania #2.D64` (174848 bytes, 1998-10-29) — Side 2 of the same set, entries K–S. Same PD supplier.

### Monase_1.0.zip (file ID 93000, 29.9 KB compressed)
Contains one D64 disk image:
- `Monase_1.0.d64` (174848 bytes, 2010-11-03)

**D64 directory of Monase_1.0.d64:**
```
PRG(locked)  115 blocks  T17/S00  "MONASE V1.0 /MON"     ← main SFX editor (~28 KB)
PRG(locked)   10 blocks  T19/S00  "SFX RELOCAT./MON"     ← relocator (~2.5 KB)
PRG(locked)    7 blocks  T19/S05  "SFX CRASHSV./MON"     ← crash saver (~1.75 KB)
```

All three PRG files are locked (copy-protected). They all load at $0801 (standard BASIC address).

### Extracted PRG file details:

| File | Size | Load addr | Content |
|------|------|-----------|---------|
| MONASE V1.0 | 29,090 bytes | $0801 | Full SFX editor, $0801–$79A1 |
| SFX RELOCATOR | 2,529 bytes | $0801 | Relocator tool, $0801–$11E0 |
| SFX CRASHSAVER | 1,670 bytes | $0801 | Crash saver tool, $0801–$0E87 |

---

## 3. MONASE V1.0 Editor — Technical Findings

### Credits and version
- `"(C)1990 ROL...HERMANS-"` → Roland Hermans © 1990
- `"1.0  3/29/92"` → Version 1.0, dated 29 March 1992
- Player by Charles Deenen, editor by Roland Hermans (confirms CSDb credits)

### File format for SFX data
The editor stores data in files with `.SFX` extension:
- `"NCES .SFX"` = "SEQUENCES .SFX" (the data file extension)
- `"TEMPORARY.WRK0:PV"` = internal scratch/work file pattern

### SFX editor column labels (from string `"FWNIAOFX"` at $7498)
These 8 characters appear to be column headers in the SFX frame editor:
- **F** = Frequency
- **W** = Waveform (control register)
- **N** = Note
- **I** = ? (possibly PWM index or instrument index)
- **A** = ADSR envelope
- **O** = On/Off gate timing
- **F** = Filter
- **X** = eXtra parameter

### SFX sub-effect structure
- `"DATA SUBEFFECT8"` at $6D58 — confirms up to **8 sub-effects** per SFX entry
- The editor has explicit "DATA SUBEFFECT" menu item

### Key assembly labels found in editor code
At $77C0–$77F0, the editor contains what appears to be assembled player code or assembler source fragments:
```
"AVEINIT"   → label SAVEINIT: (initialize/save chip state)
"ENDREP"    → label ENDREP: (end of repeat section)
"STA SD404,X" → actual SID write: STA $D404,X (voice control register)
"NOWA"      → label NOWAIT: or NOWAY:
```

### SFX Relocator menu structure
The relocator's dispatch table at $0A1D handles these keystrokes:
```
L = Load Player and Data    → $0A32
S = Save Player and Data    → $0AB7
A = Change Save-Address     → $0BEE
Z = Change Zeropage Bytes   → $0C15
$ = View Directory          → $0C36
@ = Disk Command            → $0CA5
Q = Quit Relocator          → $0CC5
```

Variables at $0D31/$0D32 = load address, $0D35/$0D36 = save address, $0D37 = ZP base.

The relocator reads the ZP base from address $2142 in the loaded player, implying the **default player load address is $2000** (ZP byte at offset $142 from base).

---

## 4. MoN/Deenen Player — Format from sidid.cfg fingerprints

The local `sidid.cfg` file (at `/home/jtr/sidfinity/tmp/mon_deenen_followup/sidid.cfg`) contains 8 byte-pattern fingerprints for `MoN/Deenen`. Decoding them as 6502 reveals:

### SID register write loop (patterns 7+8)
```asm
; Pattern 7 ends:
STA $D404,Y     ; write to SID voice control register

; Pattern 8 (the actual write loop):
STA $D400,Y     ; $99 00 D4 — STA abs,Y $D400
INY             ; $C8
DEX             ; $CA
BPL -7          ; $10 $F9 — loop back
```
The player writes SID registers using Y as base offset and X as a counter, writing both $D400+Y (freq lo) and $D404+Y (control) in sequence. Voice offsets: V1=0, V2=7, V3=14 (standard 7-byte stride).

### Sequence byte encoding (pattern 1)
```asm
CMP #$60        ; $C9 $60
BCS jump_ahead  ; $B0 $03 — if byte >= $60, it's a command
JMP player      ; $4C ?? ??
CMP #$FF        ; $C9 $FF — check for end marker
BNE skip        ; $D0 ??
LDA #$00        ; $A9 $00 — reset after $FF
```
- Bytes `$00–$5F`: note/data events (normal)
- Bytes `$60–$FE`: command bytes
- Byte `$FF`: end-of-sequence / loop sentinel → resets state to $00

### Duration countdown (patterns 5+6 — two variants: zeropage and absolute indexed)
```asm
CMP #$FF        ; end-of-sequence?
BNE continue    ; no → count down
LDA #$00        ; yes → reset
STA counter,X   ; clear per-voice counter
LDA timer,X     ; load duration timer
BEQ done        ; zero = exhausted
DEC timer,X     ; decrement
BPL loop        ; keep counting
```
Per-voice duration counters. `$FE` = "fire/repeat" trigger (restarts). `$FF` = terminal.

### Frequency slide / vibrato (pattern 2)
```asm
LDA freq_table,Y    ; load base frequency
SBC delta_table,Y   ; subtract delta → frequency slide
STA output_freq,X
LDA input,X
LSR A               ; extract high nibble: 4× LSR
LSR A
LSR A
LSR A
TAY
DEY
BMI underflow_check
LSR abs,X           ; shift output frequency bytes
ROR abs,X
JMP ...
```
Uses frequency lookup tables with per-frame delta subtraction for slides. High nibble extraction (4× LSR) used for vibrato rate/depth parameter encoding.

### Command dispatch >= $C0 (pattern 4)
```asm
CMP #$C0        ; byte >= $C0?
BCC not_cmd     ; no
AND #??         ; mask low bits
ASL A           ; shift × 3
ASL A
ASL A
STA table,X     ; store as 8× index
INY
LDA (ZP),Y      ; read next byte as parameter
CMP #??         ; compare parameter value
BEQ action
```
Bytes `$C0–$FE` are dispatched via a jump table using the low 5 bits × 8 as an index. Each command takes at least one parameter byte.

### MoN/Deenen_Digi patterns
```asm
; Pattern 1 (sample lookup):
LDX #$00
BEQ next
TYA
ASL A           ; Y *= 2 (16-bit sample address table)
TAY
LDA table,Y     ; load lo byte of sample address
STA $D4xx       ; write to SID
LDA table+1,Y   ; load hi byte
STA $D4xx

; Pattern 2 (volume write):
LSR A           ; extract upper nibble in 3 steps
LSR A
LSR A
CLV             ; (branch trick: BVC = always-branch)
BVC skip
LSR A
LSR A
LSR A
CLC
ADC #??
STA $D418       ; write master volume register
```
Digi mode uses 16-bit sample address tables (Y as 2-byte index). Volume written to $D418 from nibble extraction.

---

## 5. MoN/Bjerregaard Player — Full Format from James Bond 3 Disassembly

The file `Bjerregaard_J_James_Bond_3.asm` in the scratch dir is a complete ACME-syntax disassembly/re-assembly of the Bjerregaard variant. This is the closest documented relative to the Deenen player.

### Memory layout (ZP = $FC/$FD)
```
ZP ($FC/$FD)    pointer for sequence/program reads
D4POINT         !by 0,7,14   ← 3 voice SID offsets ($D4xx+0/+7/+14)
```

### Per-voice state (3 bytes each, indexed by X=2,1,0):
```
TEMPOCNT        global tempo counter (1 byte, shared)
SETLEN          current note length setting
TRANSP          transpose value (signed byte)
SEQNO           sequence table index (orderlist position)
SEQPTR          pattern pointer within current sequence
GLIDE           glide amount
NLEN            next note length
ENVPTR          instrument program pointer (×8 index into SET1)
VIBCOUNTER      vibrato delay counter
FIPCOUNTER      filter program counter
WFPCOUNTER      waveform program counter
NOPCOUNTER      arpeggio program counter
PWPCOUNTER      pulse width program counter
VIBDIR          vibrato direction counter
WFM             current waveform byte
GATE            gate byte ($FF=on, $FE=resting, etc.)
LEN             frame counter (counts down, BPL=playing)
LOFQ            current frequency lo byte
HIFQ            current frequency hi byte
TEMPNOTE        current note number
VIBRATE         vibrato amount (lo)
VIBRATEHI       vibrato amount (hi)
NOTE            base note number
LOPW            pulse width lo
HIPW            pulse width hi (lo nibble only)
PWTIMES         pulse width step timer
PWVALUE         last pulse width value
FTMS            filter step timer
FDTA            filter delta value
ARPSELECT       current arpeggio table index
RELCTR          release counter
NEWRELOFF       ?
LAST            "last note" flag
RELEASE         sustain/release byte
```

Global state:
```
CTOF            current filter cutoff ($D416)
D418            current volume/filter-mode ($D418)
D417            current filter routing ($D417)
VOLUME          master volume (for fade)
FADERATE        fade speed (0 = off)
FADECOUNTER     fade frame counter
```

### Voice orderlist / sequence structure

**Orderlist** (per voice, 3 voices = 6 bytes in MUSSTART):
```
START table:  [tempo_byte, init_delay, <V0_lo, >V0_hi, <V1_lo, >V1_hi, <V2_lo, >V2_hi]
```
Each song entry = 8 bytes in START table. MUSSTART[] holds the 6 sequence-pointer bytes (3×2-byte addresses = which sequence array each voice uses).

**Sequence table**: LOSEQ/HISEQ split lo/hi tables (up to $3D = 61 sequences).

**Sequence byte encoding** (within pattern/sequence):
- `$00–$5F` : note number (0=lowest, `$5F`=highest note in freq table). Gets TRANSP added.
- `$60–$7F` : arpeggio select (bits 0–4 = arpeggio table index)
- `$80–$9F` : instrument select (bits 0–4 = instrument index × 8 = SET1 entry)
- `$A0–$BF` : glide to note (next byte = target note)
- `$C0–$DF` : note length override (bits 0–4 = new length)
- `$E0–$FE` : rest/pause (bits 0–4 = rest duration); gate goes off, env release triggered
- `$FE`     : end-of-sequence with loop (repeat from seqno+1 within orderlist)
- `$FF`     : end-of-orderlist loop (reset SEQNO to 0, restart from beginning)
- `$80–$FF` high bit set in sequence LIST byte: transpose command (`AND $7F, SEC, SBC $40` → signed transpose)

### Instrument program (SET1) — 8 bytes per instrument

```
SET1+0: ADSR_ATK_DCY    Attack (hi nibble) / Decay (lo nibble) → $D405
SET1+1: SUS1_REL        Sustain1 (hi nibble) / Release (lo nibble) → $D406
SET1+2: VIB1            Vibrato: hi nibble = delay frames, lo nibble = direction range
SET1+3: PULSE_DLY       hi nibble = pulse width table index, lo nibble = ??? (release trigger timing)
SET1+4: NOTES           hi nibble = ??? lo nibble = arpeggio table index (initial)
SET1+5: FILTER          hi nibble = vibrato rate, lo nibble = filter program index (bits 0–2) + pulse index (bits 3–?)
SET1+6: WAVES           lo nibble = waveform program table index
SET1+7: VIB2_SUS2       hi nibble = vibrato depth / sustain 2 level, lo nibble = vibrato rate table index
```

Example instruments from James Bond 3:
```
; INTROSINGLECHORD: !by $00,$30,$19,$01, $04,$10,$03,$12
;   ATK=$0 DCY=$0 SUS1=$3 REL=$0 VIB1=$19 PULSE_idx=1 NOTES_idx=4 FILTER_idx=1 WAVE_idx=3 VIB2=$12
; DRUM: !by $06,$A9,$00,$00, $03,$00,$01,$00
;   ATK=$0 DCY=$6 SUS1=$A REL=$9 (no vib, no pulse, wave_idx=1)
```

### Waveform programs (W0..WC)

Variable-length byte sequences with:
- `$00–$FD`: waveform byte (written directly to $D404+voice_offset as SID control byte)
  - bit 0 = GATE (always 1 while playing, 0 when releasing)
  - bit 4 = TRI, bit 5 = SAW, bit 6 = PULSE, bit 7 = NOISE
- `$FE`: loop back to byte[0] (the first byte = loop-back index if non-$01)
- `$FF`: end / stop advancing waveform

Examples:
```
W0 BASSDRUM:  !by $01,$81,$41,$40,$FE   ; gate+noise→noise→pulse+gate→pulse,$FE loop
W1 LONGSNARE: !by $01,$81,$11,$40,$80,$40,$80,$FE
W5 GUITAR:    !by $01,$43,$43,$43,$40,$FE   ; pulse+tri on, fade to pulse only
```

### Arpeggio/note programs (N0..N12)

Variable-length with:
- Byte 0 = loop-restart position
- Bytes 1..n = note offsets (relative to base note, signed; `$80` = "use absolute freq" flag)
- `$FE` = loop to byte[loop_pos]
- `$FF` = stop

```
N0: !by $01,$04,$04,$00,$FF   ; +4 +4 +0 then stop (major triad arp)
N2: !by $81, $58,$08,$06,$04,$03,$02,$03,$04,$03,$FE   ; portamento slide down
```

### Pulse width programs (P0..P9)

Two-byte pairs: (value, timing):
- Byte 0 = loop-restart position
- Pairs: (PW_delta, count): if PW_delta < $80 → subtract (decrease), else → add (increase)
  - `delta * 2` is subtracted/added to 12-bit pulse width
- `$FE` = loop; `$FF` = stop

```
P0: !by $00,$08,$FE   ; +8 per frame, loop from pos 0
; Comments: "BYTE 0 = REPEAT POINT / BYTE 1 = LO/HI PULSE WIDTH"
```

### Filter programs (F0..F4)

Each filter sequence byte: two-byte pairs
- Byte 0 = loop position
- Pair: (cutoff_delta, timing_count)
  - Added to CTOF ($D416) each step
- `$7E` = no change (NOFILTCHANGE); `$7F` = loop back to byte[0]
- End-of-filter: byte 0 at F0 = $01,$00,$00 → immediately hits `$7E` (off)

```
; Comments: "BYTE 1=CUTOFF TRIGGER VALUE / BYTE 2=FILTER PASS (0=OFF)"
F0: !by $01,$00,$00,$7E   ; filter off
F1: !by $01,$80,$10,$F0,$06,$7E   ; cutoff from $80, add $10, hold 6, exit
```

### Frequency table

96-note chromatic table (FQDATLO/FQDATHI), covering ~8 octaves:
- C1 = $0117/$0127/$0139... up to C8 ≈ $F8xx
- Standard PAL C64 frequency table

---

## 6. Scener Pages (Reyn Ouwehand / Charles Deenen)

- **Reyn Ouwehand** (CSDb #8051): No tools, editors, or technical writeups. Composer only (Last Ninja 3, Flimbo's Quest, etc.). Left MoN for System 3.
- **Charles Deenen** (CSDb #1040): MON SFX Editor V1.00 (tool, 1990) and Future Composer V3.1 (1990) are his main tool releases. 700+ music compositions but no published format documentation.

---

## 7. Failed/Blocked Sources

| URL | Result |
|-----|--------|
| justsolve.archiveteam.org/wiki/Maniacs_of_Noise | ECONNREFUSED |
| exotica.org.uk/wiki/Maniacs_of_Noise | Bot-check (Cloudflare) |
| exotica.org.uk/wiki/Jeroen_Tel_(format) | Bot-check (Cloudflare) |
| web.archive.org (Wayback Machine) | Blocked by Claude Code fetch tool |
| GitHub code search | Requires login |
| CSDb group/search pages | HTTP 503 |

---

## 8. Key Technical Summary

### The MoN/Deenen SFX format (from MONASE + sidid fingerprints)

1. **File extension**: `.SFX` for sequence data files
2. **Memory layout**: Player + data block loaded as one relocatable unit. Default load address ≈ **$2000**. ZP base stored at offset $142 within player binary.
3. **ZP pointer**: Two-byte pointer at ZP/$FC/$FD used for sequence reads (standard (ZP),Y pattern)
4. **SID write model**: `STA $D400,Y` / `STA $D404,Y` loops with X as counter, Y as voice base (0, 7, 14)
5. **Sequence bytes**:
   - $00–$5F: notes
   - $60–$7F: arpeggio select
   - $80–$9F: instrument select (×8 index into SET1)
   - $A0–$BF: glide + target note
   - $C0–$DF: note-length override
   - $E0–$FE: rest/pause
   - $FF: sequence end/loop
6. **Instrument block (SET1)**: 8 bytes/instrument covering ADSR, vibrato (2 params), pulse-idx, note-prog-idx, filter-idx, wave-prog-idx, vibrato depth/rate
7. **Sub-programs**: Waveform (Wx), Arpeggio/note (Nx), Pulse width (Px), Filter (Fx) — all variable-length with $FE=loop/$FF=stop sentinels
8. **Counter system**: Per-voice frame counters (LEN/SETLEN), TEMPOCNT global counter (multi-speed)
9. **Filter state**: Global CTOF=$D416, D417=$D417 routing, D418=$D418 volume (with fade support)
10. **Digi variant**: Uses 16-bit sample lookup tables; writes nibble-packed volume to $D418

### Differences: Bjerregaard vs. Deenen variants

The Bjerregaard disassembly (`James Bond 3 Demo`, 1989) predates the MONASE tool (1990/1992). The Deenen engine (as fingerprinted in sidid) shares the same overall architecture but has a variant series (MoN/Deenen, MoN/Deenen_Digi, MoN/Bantam, MoN/RWE, MoN/JTS, MoN/TTWII, MoN/Cyb2) — likely evolved versions of the same core.

---

## Leads to Follow

1. **Exotica.org.uk** pages for "Maniacs of Noise" and "Jeroen Tel (format)" — blocked by Cloudflare. Try via a browser or Wayback Machine with a different user-agent. These may contain the most systematic format docs.
2. **MONASE editor binary** — the full 29 KB editor ($0801–$79A1) contains the complete SFX player code embedded. A proper 6502 disassembly of this binary (using `tools/seed_disassembly.py` or a proper disassembler) would reveal the exact data layout at the byte level. The binary is at `/home/jtr/sidfinity/tmp/mon_deenen_followup/MONASE_V1.0.prg`.
3. **Actual MoN SFX player binary** — the relocator expects a separate "player and data" file. HVSC SID files using the MoN engine contain this player inline. Disassembling one of those SIDs from `hvsc84/MUSICIANS/M/Maniacs_of_Noise/` would give the exact memory layout.
4. **ZX Spectrum 128K port** — the c64-wiki page mentions MoN "expanded to other popular computer formats." No Spectrum source was found. World of Spectrum forums (requires direct browser access) may have leads.
5. **MoN/FutureComposer** in sidid — this is a separate engine family (FutureComposer with MoN modifications), documented with different fingerprints. The existing `pipelines/future_composer/` research may overlap.
6. **CSDb group page** (ID 1135 = Maniacs of Noise) — currently returning 503. If it recovers, it lists all MoN releases including any additional tool releases.
7. **Pokefinder.org** alternative download — TLS error prevented access. Contains the same Monase archives but may have additional file listings.
