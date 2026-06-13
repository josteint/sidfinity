# Geir Tjelta Family — sidid Taxonomy & Signature Analysis

Provenance: mined from three local sidid.cfg copies (all identical in family content):
- `tmp/dmc_hunt/player-id/config/sidid.cfg` (player-id tool, Wilfred C64)
- `tmp/dmc_hunt/sidid/sidid.cfg` (cadaver/sidid)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg`
and from the `.nfo` companion files at those paths.
Date: 2026-06-13. No siddump/py65 used; all analysis is static.

---

## 1. Full Family Block from sidid.cfg

The `player-id` cfg (most authoritative) contains ten Geir Tjelta entries in this order:

```
Geir_Tjelta/Comptech-X      (line 699)
Geir_Tjelta/Echo            (line 702)
Geir_Tjelta/SIDSys_1.0      (line 705)
Geir_Tjelta/SIDSys18.4      (line 710)
Geir_Tjelta/SIDSys18.6      (line 713)
Geir_Tjelta/SIDDuzz'It      (line 716)   ← primary target
(GT_Editor)                 (line 720)   ← alt-sig, same block as SIDDuzz'It
Geir_Tjelta_Digi_1          (line 723)
Geir_Tjelta_Digi_2          (line 726)
Geir_Tjelta/MacroPlay1      (line 729)
Geir_Tjelta/MacroPlay2      (line 732)
```

In addition, Glenn Rune Gallefoss (GRG) runs a separate family of small custom players:
```
GRG            (line 799)
GRG_tiny_1     (line 804)
GRG_tiny_2     (line 808)
GRG_tiny_3     (line 811)
GRG_tiny_4     (line 814)
```
These are NOT SDI players; they are GRG's own hand-crafted mini-players. Not covered here.

---

## 2. Per-Entry Signatures and Static Interpretation

### 2.1 Geir_Tjelta/SIDDuzz'It  (PRIMARY TARGET)

```
9D ?? ?? B9 ?? ?? C9 80 29 7F 9D ?? ?? 6A 9D
B9 ?? ?? 48 4A 4A 4A 4A ?? ?? ?? ?? 68 29 0F CD ?? ?? 90 ?? 8D ?? ?? A9
29 0F 1D ?? ?? 85 ?? 29 F0 9D ?? ?? 09 0F 9D 06 D4 BD ?? ?? 09 01 9D 04 D4
(GT_Editor)
A9 ?? 1D ?? ?? 99 04 D4 BC ?? ?? B9 ?? ?? 29 ?? 0A 9D ?? ?? BD ?? ?? 30 ?? B9
```

Three signature lines required to match (all must hit); `(GT_Editor)` is a fourth
alternate-variant line for tunes assembled with the GT's Musiceditor wrapper (see §2.9).

**Static interpretation of line 1:**
- `9D ?? ??` — STA abs,X (store to indexed table, e.g. waveform register bank)
- `B9 ?? ??` — LDA abs,Y (load from indexed table — note/frequency source)
- `C9 80 29 7F` — CMP #$80 then AND #$7F: the NOTE-MASKING idiom.
  Top bit of note byte selects "fixed vs relative" pitch mode. If note >= $80, it is a fixed
  hardware note ($80..$DE); if < $80 it is a soft/relative note ($00..$5E) or soft-subtract
  ($60..$7F). The AND #$7F strips the mode bit before use.
- `9D ?? ??` — STA abs,X (store masked note to working register)
- `6A` — ROR A: right-shift A. After masking, this shifts the note value into carry or
  is part of the arpeggio-speed extraction (C4[7:4] = speed nibble).
- `9D ?? ??` — STA abs,X (store another indexed field)

**Static interpretation of line 2:**
- `B9 ?? ??` — LDA abs,Y (load from program table)
- `48` — PHA (push: saves current working byte to stack)
- `4A 4A 4A 4A` — four LSR A: right-shifts 4 bits to extract the high nibble
- `?? ?? ?? ??` — reloc-variable code (table lookup / branch)
- `68` — PLA (restore saved byte)
- `29 0F` — AND #$0F: extract low nibble
- `CD ?? ??` — CMP abs (compare against stored threshold, e.g. gate-timeout counter)
- `90 ?? 8D ?? ??` — BCC + STA abs (conditional store: instrument field write)
- `A9` — LDA # (load immediate: start of another field setup)

This is the **instrument-byte split / gate-timeout decrement loop** — splitting a packed byte
into high/low nibbles for separate register fields (AD or SR) and testing the gate timeout
counter.

**Static interpretation of line 3:**
- `29 0F` — AND #$0F: low nibble (waveform or control nibble)
- `1D ?? ??` — ORA abs,X: bitwise-OR with per-voice working byte (combine fields)
- `85 ??` — STA zp: store to zero-page working register ($FE or $FF)
- `29 F0` — AND #$F0: extract high nibble (after re-loading)
- `9D ?? ??` — STA abs,X: store to voice state
- `09 0F` — ORA #$0F: the hard-coded GATE+WAVEFORM mask — sets gate-on bit and
  ensures sustain/release are non-zero before writing
- `9D 06 D4` — STA $D406,X: write CONTROL REGISTER (waveform + gate) for voice
  (X = 0, 7, or 14 for voices 1/2/3)
- `BD ?? ??` — LDA abs,X: load per-voice field
- `09 01` — ORA #$01: force gate-on bit set
- `9D 04 D4` — STA $D404,X: write CONTROL REGISTER again (alternate path)

This is the **gate-on / waveform write** for all three SID voices: the outer loop (X=0/7/14)
iterates voices; the dual-write to $D406 and $D404 suggests two distinct code paths
for gate-on (one sets all four waveform bits + gate from the program byte; the other
only ORs gate-on into whatever the current control register holds).

**Summary:** The three lines together uniquely fingerprint:
1. The note-masking idiom (`C9 80 29 7F`) — hardcoded in SDI's waveform-program
   note-column handler
2. The high/low nibble-split with PHA/4×LSR/PLA sequence
3. The dual-write to $D404,X + $D406,X with the `09 0F` / `09 01` gate-force pattern

These all appear in the main PLAY routine of SDI V2.x. The signature is
**version-agnostic across all SDI releases** (V1.x through V2.1.7) — no version
disambiguation is embedded in the signature bytes.

---

### 2.2 (GT_Editor) — alternate variant signature

```
A9 ?? 1D ?? ?? 99 04 D4 BC ?? ?? B9 ?? ?? 29 ?? 0A 9D ?? ?? BD ?? ?? 30 ?? B9
```

- `A9 ??` — LDA # (load immediate waveform/control byte)
- `1D ?? ??` — ORA abs,X (bitwise-OR with per-voice working register)
- `99 04 D4` — STA $D404,Y: write CONTROL REGISTER using Y-indexed (vs X in main sig)
- `BC ?? ??` — LDY abs,X (load Y from voice state table)
- `B9 ?? ??` — LDA abs,Y (load from instrument/program data)
- `29 ?? 0A` — AND # then ASL A: nibble extract + shift
- `9D ?? ??` — STA abs,X
- `BD ?? ??` — LDA abs,X
- `30 ?? B9` — BMI + LDA abs,Y: signed branch + indirect load

This is the **GT's Musiceditor** wrapper variant. Per the `.nfo`: "GT's Musiceditor"
(CSDb #33645, 1992, Moz(Ic)art). It uses Y-indexed writes to $D404 instead of
X-indexed, reflecting a slightly different calling convention in this editor's output.
The `(GT_Editor)` label in parentheses marks it as a subordinate variant of the
`Geir_Tjelta/SIDDuzz'It` entry — sidid reports the primary label; the alt-sig is
matched as a fallback for the subset of HVSC tunes assembled through this wrapper.

---

### 2.3 Geir_Tjelta/SIDSys_1.0

**Full name:** Sid Systems V1 — Geir Tjelta, 1990 (CSDb #108477)

```
38 E9 01 0A A8 B9 ?? ?? 85 ?? B9 ?? ?? 85 ?? B4 ?? B1
C9 C0 90 ?? 29 3F 9D ?? ?? C8 B1 ?? C9 ?? 90 ?? 29 3F 9D ?? ?? C8 98
D0 04 D6 32 30 03 4C
```

Three-line signature required.

**Static interpretation:**
- `38 E9 01` — SEC then SBC #$01: decrement-with-borrow (counter decrement)
- `0A` — ASL A: shift for table index computation
- `A8` — TAY: transfer to Y (index into song table)
- `B9 ?? ??` — LDA abs,Y: load from indexed table (song pointer low)
- `85 ??` — STA zp: store
- `B9 ?? ??` — LDA abs,Y: load from indexed table (song pointer high)
- `85 ??` — STA zp: store pointer pair
- `B4 ??` — LDY zp,X: load Y from zero-page indexed by X (voice state)
- `B1` → start of (B1 ??) = LDA (zp),Y: indirect indexed note read

Line 2: `C9 C0 90 ?? 29 3F` — the note-range check for SIDSys.
- `C9 C0` — CMP #$C0: is note >= $C0? (end-of-sequence marker range)
- `90 ??` — BCC: if less, continue
- `29 3F` — AND #$3F: strip high bits from note byte → extract sequence/control byte
- `9D ?? ??` — STA abs,X: store extracted byte
- `C8` — INY (advance pointer)
- `B1 ??` — LDA (zp),Y: read next byte from sequence
- `C9 ?? 90 ??` — CMP # then BCC: another range check (2-byte note encoding)
- `29 3F 9D ?? ??` — AND #$3F then STA abs,X: second field extraction
- `C8` — INY
- `98` — TYA (save Y back to A, probably for pointer preservation)

Line 3: `D0 04 D6 32 30 03 4C` —
- `D0 04` — BNE (skip 4 bytes): branch on non-zero
- `D6 32` — DEC zp,X ($32 = some voice counter, zero-page indexed)
- `30 03` — BMI +3: if counter went negative, jump forward
- `4C` → JMP to loop-restart

This is an early, simpler sequencer loop: 8-bit pointer arithmetic to advance through a
per-voice sequence table, note range comparison with $C0 as the "special" threshold
(rather than SDI's note-masking), and zero-page voice counters.

**Key difference from SDI:** SIDSys uses `C9 C0 / 29 3F` (range threshold) for note control
vs SDI's `C9 80 / 29 7F` (bit-masking). Confirms a different, simpler voice model.

---

### 2.4 Geir_Tjelta/SIDSys18.4

**Full name:** Sid Systems V4.1, player version 18.4 — Geir Tjelta, 1990 (CSDb #33644)

```
4A 4A 4A 4A A8 B9 ?? ?? 8D ?? ?? A5 ?? A4 ?? 10 ?? 4A 66 ?? 4A 66 ?? 4A 66 ?? 4A 66
```

Single-line signature.

**Static interpretation:**
- `4A 4A 4A 4A` — four LSR A: divide A by 16 (extract high nibble as index)
- `A8` — TAY: transfer to Y (program table index)
- `B9 ?? ??` — LDA abs,Y (load from program table)
- `8D ?? ??` — STA abs (store to absolute address — not indexed; one-voice or common state)
- `A5 ??` — LDA zp: load from ZP
- `A4 ??` — LDY zp: load Y from ZP
- `10 ??` — BPL: branch if positive (guard on counter/direction)
- `4A 66 ??` × 4 — LSR A + ROR zp × 4: **four-bit right-rotation into ZP chain**

The `4A 66 ?? 4A 66 ?? 4A 66 ?? 4A 66 ??` pattern is a 16-bit (or 32-bit) shift-right using
the carry chain — this is characteristic of SIDSys V18.4's **frequency accumulator** or
**pulse-width divider**. The four-stage ROR builds up a fractional pitch effect.

"Version 18.4" refers to an internal player-binary version number embedded in the
SIDSys V4.1 release, not a 4th major version. Two player binaries coexist: 18.4 and 18.6.

---

### 2.5 Geir_Tjelta/SIDSys18.6

**Full name:** Sid Systems V4.1, player version 18.6 — Geir Tjelta, 1990 (CSDb #33644)

```
A9 ?? 9D 06 D4 A9 FE 3D ?? ?? 9D 04 D4 4C ?? ?? BD ?? ?? 9D ?? ?? BD ?? ?? D0
```

Single-line signature.

**Static interpretation:**
- `A9 ?? 9D 06 D4` — LDA # imm, STA $D406,X: load immediate waveform control and
  store to VOICE 1 CONTROL REGISTER (waveform + gate). This is a **gate-off / hard-restart
  sequence**: write a specific waveform byte to $D406.
- `A9 FE` — LDA #$FE: load $FE (value has bit-0 clear = gate off, bit-7 set = noise or
  test-bit pattern)
- `3D ?? ??` — AND abs,X: AND $FE with current control register (clears gate bit)
- `9D 04 D4` — STA $D404,X: store to VOICE 1 CONTROL REGISTER — gate-off write
- `4C ?? ??` — JMP abs: unconditional jump (to next routine or loop head)
- `BD ?? ??` — LDA abs,X: load per-voice data (note/sequence byte)
- `9D ?? ??` — STA abs,X: store to voice state
- `BD ?? ??` — LDA abs,X: load another field
- `D0` — BNE start: branch-if-nonzero (loop tail)

The `A9 FE / 3D ?? ?? / 9D 04 D4` pattern is a **gate-clear idiom** (AND-not-gate-bit then
store), distinguishing 18.6 from 18.4 which uses a shift-chain instead. The direct
`9D 06 D4` write suggests 18.6 writes control registers in a different order or with
different timing than 18.4.

---

### 2.6 Geir_Tjelta/Comptech-X

**Full name:** Comptech-X — Geir Tjelta, first used 2019 (private, probably for X-Ample members)

```
29 0F C9 08 90 07 0A 0A 0A 0A 8D
```

Single-line signature (very short).

**Static interpretation:**
- `29 0F` — AND #$0F: extract low nibble
- `C9 08` — CMP #$08: compare with 8
- `90 07` — BCC: if less than 8, branch forward 7 bytes
- `0A 0A 0A 0A` — four ASL A: multiply low nibble by 16 (if >= 8)
- `8D` → STA abs: store result

This is a **nibble-range split**: if low nibble < 8 take one path; if >= 8, shift left ×4
(making it a high-nibble-sized value) and store. In a modern GT player, this pattern
typically distinguishes two instrument-field encoding ranges — e.g. waveform program
pointer vs. a direct waveform byte, or instrument index vs. effect-immediate.

Comptech-X is a **private player** (2019+) used by Geir Tjelta and Markus Schneider
(X-Ample). Only 6 HVSC tunes; not a widely-distributed editor like SDI.

---

### 2.7 Geir_Tjelta/Echo

```
AD ?? ?? 09 ?? 8D 18 D4 A9 70
```

Single-line signature. **No entry in sidid.nfo** (not documented there).

**Static interpretation:**
- `AD ?? ??` — LDA abs: load from an absolute address (sample/buffer read)
- `09 ??` — ORA #imm: OR with a fixed bitmask
- `8D 18 D4` — STA $D418: write VOLUME/FILTER register

The canonical digi-echo trick: read a delayed copy of earlier audio output (which was
previously written to $D418) and replay it via the volume register — producing an
echo/delay effect on top of another player's music.

- `A9 70` — LDA #$70: load #$70 ($70 = binary 0111 0000), which is likely the filter
  mode byte (LP+HP+BP = $70 in $D418 upper nibble) or a volume value used as a
  "pass-through" constant.

**Nature:** Echo is a **post-processing wrapper**, not a standalone music player. It:
1. Calls another player's PLAY routine (the underlying tune, often SDI or something else)
2. Samples the SID's volume register output into a ring buffer
3. Replays the delayed sample back to $D418

This explains why all Echo tunes have `play_addr = 0` — the echo code installs an NMI
or CIA-driven interrupt handler internally and never exposes a PSID play vector. The
underlying tune is either embedded or called from within the echo routine.

**HVSC population:** 8 tunes, 2009–2022, all RSID (is_psid=0). All authored by Geir Tjelta
himself or used with his permission (DRAX's Sub Hunter echoed by NecroPolo, etc.).

---

### 2.8 Geir_Tjelta_Digi_1

**Full name:** NMI Player v1.0 — Geir Tjelta & Glenn Rune Gallefoss (GRG). No CSDB link
in nfo; no nfo entry for Digi_2.

```
8D 18 D4 4C ?? ?? 24 ?? 30 ?? 4A 4A 4A 4A 4C
```

**Static interpretation:**
- `8D 18 D4` — STA $D418: volume/filter write — **digi sample write** to volume register
- `4C ?? ??` — JMP abs: jump (to main loop or sample-advance)
- `24 ??` — BIT zp: test zero-page flag bit (NMI trigger check)
- `30 ??` — BMI: branch if bit-7 set (NMI flag check)
- `4A 4A 4A 4A` — four LSR A: divide sample byte by 16 (extract 4-bit sample)
- `4C` → JMP: loop-back

This is a **4-bit digi player via $D418 volume writes** — the simplest C64 digi technique.
The four LSR operations extract the high nibble of each sample byte (4-bit DAC). An NMI
timer fires the sample output. The `BIT zp / BMI` sequence reads an NMI-set flag.

### 2.9 Geir_Tjelta_Digi_2

```
9D 00 D4 CA 10 FA A9 81 8D 0D DD AD 0D DD 60 AD ?? ?? CE ?? ?? 10 0B 8D ?? ?? D0
```

**Static interpretation:**
- `9D 00 D4` — STA $D400,X: store to SID (X=0..18, i.e. a full SID init loop)
- `CA 10 FA` — DEX + BPL loop: decrement X and loop → **SID register clear loop** (init)
- `A9 81 8D 0D DD` — LDA #$81, STA $DD0D: write $81 to CIA2 ICR → **enable NMI on timer A**
- `AD 0D DD` — LDA $DD0D (clear CIA2 interrupt flags)
- `60` — RTS
- `AD ?? ??` — LDA abs: load sample byte from buffer
- `CE ?? ??` — DEC abs: decrement sample counter
- `10 0B` — BPL: if not zero, continue
- `8D ?? ??` — STA abs: store sample output
- `D0` → BNE: loop branch

This is a **CIA2-NMI-driven digi player**: sets up NMI via CIA2 timer A ($DD0D write),
clears all SID registers on init, then fires the NMI handler which reads samples from a
buffer and writes to SID. More sophisticated than Digi_1 (uses full NMI, not just BIT-flag check).

---

### 2.10 Geir_Tjelta/MacroPlay1 and MacroPlay2

**Full name:** Macro Player — Geir Tjelta, 2009 (CSDb #76493). Two variants.

MacroPlay1:
```
A2 00 BD ?? ?? 8D ?? ?? CA 30 CB A0 00 B9
```
- `A2 00` — LDX #0 (init X=0)
- `BD ?? ??` — LDA abs,X: load from indexed table (register init sequence)
- `8D ?? ??` — STA abs: store (direct register write, abs = SID register)
- `CA 30 CB` — DEX + BMI -53: loop (decrement, branch negative to EARLIER address -53)
  Note: BMI $CB here is actually a signed offset of -53 making it loop back. Together:
  a **backward-counting init loop** (X=0 counting down, BMI on negative catches end)
  Actually: since X starts at 0, first DEX makes X=$FF (negative), so this fires immediately
  unless the loop condition differs. More likely X is set to a count > 0 before this point.
- `A0 00 B9` — LDY #0, LDA abs,Y: set Y=0 then load indexed (start of play loop)

MacroPlay2:
```
90 40 A5 ?? C9 FE D0 38 A9 ?? 8D 06 D4 10 30 AC
```
- `90 40` — BCC +$40: large branch on carry clear (jump over a big block)
- `A5 ??` — LDA zp: load from zero-page (sequence/track position)
- `C9 FE` — CMP #$FE: test for $FE end-marker (common in MacroPlay format)
- `D0 38` — BNE +56: if not end-marker, skip ahead
- `A9 ?? 8D 06 D4` — LDA # imm, STA $D406: write voice 1 waveform/control (gate-off?)
- `10 30` — BPL +48: branch if positive
- `AC` → LDY abs: load Y (pointer advance)

MacroPlay appears to be a **compact, macro-driven player** where sequences use $FE as
an end-marker. The 2009 date and the two variants (1 and 2) suggest two distinct
MacroPlay engines (possibly single-voice vs multi-voice). Only 1 HVSC tune each —
essentially one-off personal tools.

---

## 3. Disambiguation: SDI vs SIDSys vs Comptech-X vs Echo

| Label | Engine | Type | Years | Authors | HVSC n |
|---|---|---|---|---|---|
| `Geir_Tjelta/SIDSys_1.0` | Sid Systems V1 | Tracker player | 1989–1991 | GT | 45 |
| `Geir_Tjelta/SIDSys18.4` | Sid Systems V4.1 (player 18.4) | Tracker player | 1990–2018 | GT | 46 |
| `Geir_Tjelta/SIDSys18.6` | Sid Systems V4.1 (player 18.6) | Tracker player | 1991–2012 | GT | 48 |
| `Geir_Tjelta/SIDDuzz'It` | SID Duzz'It (SDI) V1.x–V2.1.7 | Tracker player+editor | 1992–2025 | GT+GRG | 934 |
| `Geir_Tjelta/Echo` | GT's Echo post-processor | Wrapper/digi echo | 2009–2022 | GT | 8 |
| `Geir_Tjelta/Comptech-X` | Comptech-X | Private player | 2019–2025 | GT+Schneider | 6 |
| `Geir_Tjelta/MacroPlay1` | Macro Player v1 | Micro player | 2009–2013 | GT | 1 |
| `Geir_Tjelta/MacroPlay2` | Macro Player v2 | Micro player | 2009–2020 | GT | 1 |
| `Geir_Tjelta_Digi_1` | NMI Player v1.0 | 4-bit digi | n/k | GT+GRG | 0 (in hvsc84) |
| `Geir_Tjelta_Digi_2` | CIA2-NMI digi | Full NMI digi | n/k | GT? | 0 (in hvsc84) |

**SIDSys is NOT SDI.** SIDSys (1989–1990) is a predecessor music system created by GT
before SDI existed. SDI (1992+) was built by GT and GRG on ideas from SIDSys plus
JCH/Vibrants editor and Panoramic "Digitalizer" (per SDI 2.1.7 manual). The note-encoding
idioms differ: SIDSys uses `C9 C0 / 29 3F` (range+strip); SDI uses `C9 80 / 29 7F` (bit-mask).

**Echo is a post-processor**, not a standalone player. It wraps existing SID tunes, adding
a realtime echo via $D418 sampling. All Echo tunes are RSID (no PSID play vector).

**Comptech-X is a private player** (2019+), distinct from SDI. Very small HVSC footprint.

**SDI has no internal version disambiguation** in the sidid signature — V1.x through V2.1.7
all match the same three-line pattern.

---

## 4. DeepSID Labeling Behaviour

DeepSID (local copy at `tmp/dmc_hunt/DeepSID/`) uses the same `sidid.cfg` for player
identification (`php/sid_id.php` reads `../sidid.cfg` at runtime). A `pretty_player_names.php`
file maps raw sidid labels to display names for 181 entries — but **no Geir_Tjelta/* entries
appear in that map**. Therefore:

- DeepSID shows the raw sidid label `Geir_Tjelta/SIDDuzz'It` as-is in the player field.
- No version tag is added (V1.x vs V2.x is indistinguishable from the sidid sig alone).
- The sidid label is the canonical display name on DeepSID for all SDI tunes.

---

## 5. SIDDuzz'It Signature: The `C9 80 29 7F` Note-Masking in Context

The full SDI waveform-program note-column byte encoding (from `sdi_217_manual.txt`):

```
Byte range   Meaning
$00–$5E      Soft note (relative pitch, added to transpose)
$60–$7F      Soft subtract (relative pitch, subtracted)
$80–$DE      Fixed note (hardware frequency, table-looked-up)
$FF          Special command (tie/rest/jump)
```

The `CMP #$80` test determines which half of the table applies. The `AND #$7F` strips
the mode bit, leaving a 7-bit index into either the relative-note table or the fixed-note
table. This is the ONLY place in the SDI play routine where this exact two-instruction
sequence (`C9 80 29 7F`) occurs, making it a unique fingerprint.

## Leads to follow

1. **SDI version discrimination inside the binary**: The sidid signature is version-agnostic.
   To distinguish V1.x (pre-2006), V2.0 Beta (2006–2009), and V2.1.x (2013–2014) in HVSC,
   look for version-string differences in the player binary (e.g. the `.TEXT "-PLAYER V2.1 "`
   at $1000+3 in V2.1 source), or differences in the zero-page layout / player flag
   positions. The `(GT_Editor)` alt-sig may correlate with older builds.

2. **SIDSys migration scope**: 139 tunes total (SIDSys_1.0 + 18.4 + 18.6). Years 1989–2018.
   The two V4.1 player variants (18.4 vs 18.6) share a CSDB release (#33644) — they may
   be the same editor but two player binaries the user could assemble against (analogous to
   SDI's N50/SPD50 split). Worth verifying with a static diff of the player bytes.

3. **Echo wrapper disassembly**: All 8 Echo tunes are RSID. The echo player's size can be
   inferred from load_addr (RSID data start) minus the position of the underlying tune.
   The chipflip.wordpress.com article (2009-09-23) has a technical writeup of the technique.

4. **Comptech-X format**: Only 6 tunes, 2019–2025. If Geir Tjelta can be contacted via CSDB,
   the source may be available. The nibble-range-split signature (`29 0F C9 08 90 07 0A 0A 0A 0A`)
   suggests a compact instrument format.

5. **SDI V1 vs V2 structural differences**: CSDb #7175 (V1.801, 2002) is the earliest known
   online release. The manual states SDI was built on SIDSys ideas (1992). Early V1
   tunes in HVSC (1992–2002) may use a slightly different data layout; worth flagging
   during extraction if instrument table offsets drift.

6. **MacroPlay CSDB #76493**: Single-tune footprint each. Investigate if these are embedded
   in demo/game PRGs with the player welded in (hence only 1 HVSC entry).

7. **`Geir_Tjelta_Digi_1/2` absent from hvsc84.db**: These appear in sidid.cfg but zero
   tunes match in the DB. Either the tunes they fingerprint are embedded within SDI or
   SIDSys tunes (detected by another label first), or they predate what's in hvsc84.
