---
source_url: https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Whittaker_David/Whittaker_David_Panther.asm
fetched_via: direct
fetch_date: 2026-06-17
author: dmx87 (reverse-engineer) + synthesised from VGMPF / NostalgicPlayer C# source
content_date: 1986 (original player), disassembly 2020s
reliability: primary (C64 section from disassembly); secondary (Amiga section from C# re-implementation)
---

# David Whittaker C64 Format Specification

Synthesised from:
- `Whittaker_David_Panther.asm` (dmx87 disassembly, primary source)
- NostalgicPlayer `DavidWhittakerWorker.cs` (C# re-implementation of Amiga .dw format)
- `sidid.cfg` (Cadaver et al.)
- VGMPF David Whittaker + NES Driver pages
- c64.com interview; Wikipedia

---

## Overview

David Whittaker's C64 driver is NOT a standard module format: the player code
and music data are embedded together in a single binary.  There is no editor or
separate data file — Whittaker hand-assembled everything in a machine code
monitor (Supersoft tools) on the C64 itself.

Three driver generations exist:

| Period | Label | Key features |
|--------|-------|--------------|
| ≤1984 | Early (Lazy Jones) | Load $1480; 424 Hz tuning; uses SID filter; very minimalist |
| 1985–1986 | "Whittaker original" | Supersoft assembler; pattern/command set described below; no filter except SFX |
| 1986+ | "Jason Brooke rewrite" | More flexible chords, envelopes, combined pitch-bends; ported back to C64 from CPC June 1986 |

Brooke and Whittaker updated their respective variants independently after 1986
("drivers are distinguishable from each other").  Whittaker used the Brooke
back-port essentially unchanged until 1991.

---

## 1.  C64 Binary Layout (Panther / ~1986 variant)

Module loads at $9000 (Panther) — other games use other load addresses
(Red Max: $E000; Lazy Jones: $1480).  The offset from load address is
constant within a version.

```
$9000          init routine
$9000+$10      v1data  — 40-byte per-voice state block, voice 1
$9000+$38      v2data  — 40-byte per-voice state block, voice 2
$9000+$60      v3data  — 40-byte per-voice state block, voice 3
$9000+$88      PlayFlag
$9000+$117     L_9117  ) three global tempo/PWM temporaries
$9000+$118     L_9118  )
$9000+$119     L_9119  )
               play routine
               GetNote, NextPatValue, SoundUpdate routines
               CommandTable (18-entry jump table)
               Individual command handlers
               SIDreset, StopMusic
               TempoCnt, ModeVol
               NoteFreqsL/H  (84-semitone SID freq table)
               ArpTable       (13 arp patterns)
               Track1/2/3    (pointers to sequence tables)
               Track1Seq/2Seq/3Seq  (orderlist arrays, terminated by !wo 0)
               Pattern data  (L_9902 ... end)
```

---

## 2.  Per-Voice Data Block (40 bytes)

One 40-byte block per voice, zero-page indirect via $FA/$FB pointing to base.

| Offset | Label   | Meaning |
|--------|---------|---------|
| $00    | FLAGS   | Bit-field (see below) |
| $01    | PAT     | Current pattern pointer lo |
| $02    | PATH    | Current pattern pointer hi |
| $03    | TRACK   | Track (orderlist) pointer lo |
| $04    | TRACKH  | Track (orderlist) pointer hi |
| $05    | B05     | Track position byte-offset (initialised to 2) |
| $07    | B07     | Slide/vibrato accumulator lo |
| $08    | B08     | Slide/vibrato accumulator hi |
| $09    | ARP2L   | Arpeggio reset pointer lo |
| $0A    | ARP2H   | Arpeggio reset pointer hi |
| $0B    | ARP     | Arpeggio current pointer lo |
| $0C    | ARPH    | Arpeggio current pointer hi |
| $0E    | B0E     | Vibrato/slide step hi |
| $0F    | B0F     | Vibrato/slide countdown counter |
| $10    | NOTC    | Note duration counter (decrements each frame) |
| $11    | NOTD    | Note duration value (reloaded into NOTC) |
| $12    | NOTE    | Current note number (0–83) |
| $13    | AD      | ADSR Attack/Decay byte → $D405/$D40C/$D413 |
| $14    | SR      | ADSR Sustain/Release byte → $D406/$D40D/$D414 |
| $15    | FQL     | Frequency lo → $D400/$D407/$D40E |
| $16    | FQH     | Frequency hi → $D401/$D408/$D40F |
| $17    | PWL     | Pulse width lo → $D402/$D409/$D410 |
| $18    | PWH     | Pulse width hi → $D403/$D40A/$D411 |
| $19    | B19     | "new note" flag (1 = trigger gate-on next frame) |
| $1A    | B1A     | PWM half-range (half of max PWM sweep value) |
| $1B    | B1B     | PWM step delta |
| $1C    | B1C     | PWM current value |
| $1D    | B1D     | Bit-field: bit6=PWM direction, bit5=PWM active, others TBD |
| $1E    | B1E     | PWM lower bound |
| $1F    | B1F     | PWM upper bound |
| $20    | B20     | PWM increment per frame |
| $21    | B21     | PWM mode: 0=off, 1=sweep-up, $81=sweep-down |
| $22    | WAVE    | Waveform byte (without gate bit) |
| $23    | CTRL    | Control register value (with gate bit) |

### FLAGS byte ($00) bit assignments

| Bit | Meaning |
|-----|---------|
| 0   | Alternating toggle (flipped every frame via EOR #1) — used to gate-on/off cleanly |
| 1   | Companion to bit 0 in slide/vibrato path; combined with bit 6 ($24 mask) |
| 2   | Vibrato enable (set by $8E command) |
| 3   | (see bits 3+5) |
| 4   | ??? |
| 5   | Arp active (bit 5 = $10 mask); set when arp selected, checked in SoundUpdate |
| 6   | Slide UP active (set by $85) |
| 7   | Slide DOWN active (set by $87); $80 is "bit 8" comment in source |

---

## 3.  Pattern Stream Encoding

Pattern bytes are processed by `GetNote` / `NextPatValue`.

### 3a.  Note bytes ($00–$7F)

A byte in range $00–$7F is a note number.
- Set `NOTD` (duration) into `NOTC`
- Store note number in `NOTE`
- Set `B19` = 1 (trigger gate-on at next output stage)
- Advance pattern pointer

### 3b.  Command/effect bytes ($80–$FF)

The dispatch code at `pspecial` (`cmp #$b8` then cascade of `adc` +
branch) determines the byte's category:

| Range | Category | Details |
|-------|----------|---------|
| $80–$B7 | Pattern commands | Dispatched through CommandTable (18 entries, $80–$93 used) |
| $B8–$BF | Reserved / unused in Panther | — |
| $C0–$C7 | Note duration (4-bit) | `(byte - $BE)` → new NOTD (short values) |
| $C8–$CF | ADSR override | Next 2 bytes: new AD, new SR → stored in voice block |
| $D0–$D7 | Note duration (longer) | adc chain result → new NOTD |
| $D8–$DF | Tempo change | `(byte + $09 - $D0)` → new SongTempo |
| $E0–$FF | Arpeggio select | `(byte & ~$E0) * 2` → index ArpTable; arp pointers loaded into ARP/ARPH + ARP2L/ARP2H |

**Arpeggio pattern end byte:** `$88` (high-bit set, out of note range).
Each arpeggio byte is a semitone offset from the base note.  When the
advance pointer reaches a byte `>= $54`, the pointer resets to ARP2
(loop from beginning).  So $88 is both "arp end" AND the pattern end
sentinel.

**Pattern end sentinel:** $88 (same value as arp terminator).
When $88 is seen as a pattern byte, the track pointer advances to the
next entry in the track sequence table.  When the track table reaches
`!wo 0` the voice loops back from the beginning of the sequence table.

### 3c.  Duration encoding (empirical from Panther patterns)

Looking at L_99CD:
```
$D0 = duration load 8 (most common riff value)
$E0 = arp "off" or short duration
```
Exact decode:
- $C0–$C7: short durations 1–8 (direct: val - $BE)
- $D0–$D7: medium durations (val + $09 - see pcommand adc chain)
- $E0–$FF: arp select (top 3 bits = $E = 0b111, but arp select uses the LOW bits)

Note: the exact numeric mapping of each range must be derived from
the `pspecial` adc chain.  The adc-with-branch trick uses carry to
sequence the tests; see the source at ~$9744.

---

## 4.  Command Table ($80–$93)

Dispatched by `pcommand` via 2-byte jump table at `CommandTable`.

| Byte | Label | Effect |
|------|-------|--------|
| $80  | L_93FB | → jumps to L_9431 (re-enter note-trigger path without reading a new note) |
| $81  | L_93CF | Clear B1D ($00) — reset PWM/slide state |
| $82  | L_93D7 | Set B1D = $40 (bit7 = enable some PWM mode) |
| $83  | L_93DF | Set ModeVol = next pattern byte (global $D418 volume override) |
| $84  | L_9363 | Set FLAGS bit3 ($04): enable pitch-bend bit |
| $85  | L_935B | Set FLAGS bit6 ($20): slide UP enable |
| $86  | L_93C5 | Set FLAGS bit4 ($08) |
| $87  | L_93BD | Set FLAGS bit8 ($80): slide DOWN (& then also set bit4 via fallthrough) |
| $88  | L_9304 | Track advance: advance to next pattern via track pointer; if track end → restart |
| $89  | L_939A | Set up pitch-bend parameters: next 2 bytes = bend start (lo/hi), 3rd byte = B1C |
| $8A  | cmd_Noise    | Waveform = $80 (Noise) → WAVE |
| $8B  | cmd_Pulse    | Waveform = $40 (Pulse) → WAVE |
| $8C  | cmd_Saw      | Waveform = $20 (Sawtooth) → WAVE |
| $8D  | cmd_Tri      | Waveform = $10 (Triangle) → WAVE |
| $8E  | L_93EF       | Set FLAGS $02+$01 (enable vibrato, bits 1+2) |
| $8F  | cmd_PulseHi  | Set PWL=0, PWH=next pattern byte, B21=0 (fixed pulse width, no sweep) |
| $90  | L_9297       | Set PWM sweep: 3 bytes follow → B1E, B1F, B20 (lo-bound, hi-bound, step) |
| $91  | cmd_StopMusic| Pull return addresses off stack (JSR-chain), jump to StopMusic |
| $92  | cmd_RingTri  | Waveform = $14 (Triangle + Ring-Mod) → WAVE |
| $93  | cmd_SyncSquare| Waveform = $42 (Pulse + Sync) → WAVE |

**Waveform bytes written to $D404 (voice control register):**

| Waveform | SID bits | Hex |
|----------|----------|-----|
| Noise    | bit7     | $80 |
| Pulse    | bit6     | $40 |
| Sawtooth | bit5     | $20 |
| Triangle | bit4     | $10 |
| Ring+Tri | bit4+bit2| $14 |
| Sync+Pul | bit6+bit1| $42 |

Gate bit is OR'd in by the `play` output stage (INX then STX), not
stored in WAVE.

---

## 5.  Arpeggio Table

`ArpTable` at ~$9B37 in Panther (13 entries, 2-byte pointers):

| Index | Data bytes | Semitone intervals (arp sequence) |
|-------|------------|----------------------------------|
| 0  ($E0) | $00 $03 $07 $88 | root, minor 3rd, perfect 5th → minor triad |
| 1  ($E1) | $00 $04 $07 $88 | root, major 3rd, perfect 5th → major triad |
| 2  ($E2) | $00 $03 $07 $0C $88 | root, m3, p5, octave → minor 7th arp |
| 3  ($E3) | $00 $04 $07 $0C $88 | root, M3, p5, octave → major 7th arp |
| 4  ($E4) | $07 $0C $0F $88 | p5, octave, min 9th → power + ext |
| 5  ($E5) | $07 $0C $10 $88 | p5, octave, maj 9th |
| 6  ($E6) | $03 $07 $0C $88 | m3, p5, octave |
| 7  ($E7) | $04 $07 $0C $88 | M3, p5, octave |
| 8  ($E8) | $00 $0C $88 | root + octave (two-note octave) |
| 9  ($E9) | $00 $04 $88 | root + major 3rd |
| 10 ($EA) | $00 $03 $88 | root + minor 3rd |
| 11 ($EB) | $00 $05 $88 | root + perfect 4th |
| 12 ($EC) | $00 $07 $88 | root + perfect 5th |

Arp values are semitone offsets added to the base note number before
the freq-table lookup.  $88 terminates the sequence; the arp pointer
resets to ARP2 (start of pattern) for loop.

---

## 6.  Note Frequency Table

`NoteFreqsL` / `NoteFreqsH` at ~$9B7E in Panther (84 entries, PAL, ~424 Hz tuning).

Stored as interleaved word table: `NoteFreqsH = NoteFreqsL + 1`.
84 semitones (7 octaves) starting from ~C1.

First 12 values (one octave, C1–B1):
```
$0116 $0126 $0138 $014B $0160 $0172 $0189 $01A1 $01BB $01D6 $01F1 $020E
```

This corresponds to A4=424 Hz (slightly flat relative to A=440Hz standard).
These are SID register values, not Hz.  SID freq formula: `N = f * 2^24 / Fclock`
(PAL Fclock = 985248 Hz).  For $0116 (= 278): `278 * 985248 / 2^24 ≈ 16.3 Hz`.

The table spans 84 notes ($0116–$F880).

---

## 7.  Track / Sequence Structure

```
Track1    !wo Track1Seq    ; pointer to orderlist for voice 1
Track2    !wo Track2Seq    ; pointer to orderlist for voice 2
Track3    !wo Track3Seq    ; pointer to orderlist for voice 3

Track1Seq
    !wo L_9902             ; pattern 0 (intro)
    !wo L_9909             ; pattern 1 (repeated N times)
    ...
    !wo 0                  ; end of sequence → loop back to Track1Seq[0]
```

Each sequence entry is a 2-byte absolute address to a pattern.
Terminator: `!wo 0` (null pointer).
The init routine loads `Track#[0]` into VD_TRACK/TRACKH and then
pre-loads the first pattern into VD_PAT/PATH.

---

## 8.  SID Register Write Order (per frame)

From the `play` routine output stage:

```
V1: FREQLO, FREQHI, PWLO, PWHI, AD, SR, CTRL (gate-off first if B19 set)
V2: same
V3: same
$D418: ModeVol (master volume; fixed $0F unless overridden by $83 command)
```

Gate-on/off mechanism: `CTRL` (=WAVE | gate_bit) is written as gate-off
first (`STX` with the raw WAVE value), then gate-on (`INX; STX` to add 1).
The `B19` flag delays this by one frame: if `B19` > 0, it writes gate-off
and decrements B19; on the next frame `B19`=0 so only gate-on is written.

---

## 9.  SIDID Identification Signatures (C64)

From `cadaver/sidid` `sidid.cfg`:

```
[David_Whittaker]
CE ?? ?? 8E 04 D4 E8 8E 04 D4 END
8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4 END
AD ?? ?? 85 ?? AD ?? ?? 85 ?? A0 00 B1 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? 60 END
B1 ?? F0 AND C8 B1 AND A9 ?? 8D 04 D4 A9 ?? 8D 04 D4 AND 69 02 85 END
8D 08 D4 B9 ?? ?? 8D 0E D4 B9 ?? ?? 8D 0F D4 A9 ?? 8D 04 D4 END
```

Five signatures — all OR-matched.  `??` = wildcard byte.
They key on the SID register write patterns ($D404/$D406/$D408 etc.),
particularly the `STA $D406 / LDX #imm / STX $D404 / INX / STX $D404`
gate-on/off sequence that is characteristic of Whittaker's play routine.

No variant names are registered (e.g., no "David_Whittaker_v2") — all
variants match under one label.

---

## 10.  Amiga .dw Format (from NostalgicPlayer C# source)

The Amiga `.dw` format is a separate engine (68000 assembly, Devpac).
The C64 and Amiga formats share the MUSICAL CONCEPTS but are different binaries.
File extension: `.dw` or `dw.*`.

### 10a.  File identification

NostalgicPlayer identifies the format by scanning for 68000 machine code
patterns.  The file is rejected if it starts with "SC68".  Minimum size: 2048 bytes.

Identification markers:
- Init function: `$47FA` (LEA pc-relative) followed by `$F0+` nibble; `$6100` (BSR)
- Sample init patterns: `$4A2B`, `$41EB`, `$41FA`
- Play function: `$47FA $4A2B $67??`
- Delay counter: `$103A` pattern
- Square waveform: `$207A $303A` sequence
- Channel count: `$7E` instruction with immediate value

Pointer type (32 vs 16-bit): detected by `$2070` (32-bit MOVEA) vs `$3070` (16-bit).

### 10b.  Sub-song list

- Located at `subSongListOffset`
- Each entry:
  - Speed: 1–2 bytes (1 if `enableDelayCounter` = false, 2 if true)
  - DelayCounterSpeed: 1 byte (only if `enableDelayCounter` = true)
  - Channel position list pointers: 32-bit or 16-bit depending on `uses32BitPointers`
- Terminated when speed field value exceeds 255

### 10c.  Position lists

- Each channel has an independent position list (= orderlist)
- Entries: uint32 or uint16 offsets into track data
- Contains restart position for loop
- Terminated by zero/invalid offset

### 10d.  Track data format (Amiga)

Byte stream, same general structure as C64:
```
$00–$7F   Note value (pitch); decoded as: sample = note / 12; noteIndex = note % 12
           OR: direct note with sample set via command bytes >= newSampleCmd
$80–$DF   Commands (high bit set, < $E0)
$E0–$FF   Speed multiplier: (byte - $DF) * baseSpeed
```

`WaitUntilNextRow` ($03 effect) is the per-channel "stop processing this frame" marker.
`EndOfTrack` ($00 effect) → advance to next position; loop at end.

### 10e.  Sample info (new Amiga player), 12 bytes per sample

```
+0  4 bytes  pointer to sample data (not parsed, skipped)
+4  4 bytes  loop start (int32; -1 = no loop; capped at 64KB)
+8  2 bytes  length in words
+10 2 bytes  fine-tune period (multiply factor >> 10)
+12 2 bytes  volume (0–64)
+14 1 byte   transpose offset
+15 1 byte   padding
```

Sample data block:
```
+0  4 bytes  sample length
+4  2 bytes  frequency (converted to Amiga period via 3579545 / frequency)
+6  N bytes  signed 8-bit PCM data
```

Old player (QBall): only sample count + channel volume table; no per-sample metadata.

### 10f.  Amiga period tables

Three period tables (used by different driver versions):

**Periods1** (12 values, QBall old player, one octave):
`256 242 228 215 203 192 181 171 161 152 144 136`

**Periods2** (48 values, first player version):
`4096 3864 3648 3444 3252 3068 2896 2732 2580 2436 2300 2168`
`2048 1932 1824 1722 1626 1534 1448 1366 1290 1218 1150 1084`
`1024  966  912  861  813  767  724  683  645  609  575  542`
`512   483  456  430  406  383  362  341  322  304  287  271`
`256   241  228` (last 3 added beyond original player for arp/transpose range)

**Periods3** (63 values, newer Amiga player):
`8192 7728 7296 6888 6504 6136 5792 5464 5160 4872 4600 4336`
`4096 3864 3648 3444 3252 3068 2896 2732 2580 2436 2300 2168`
`2048 1932 1824 1722 1626 1534 1448 1366 1290 1218 1150 1084`
`1024  966  912  861  813  767  724  683  645  609  575  542`
`512   483  456  430  406  383  362  341  322  304  287  271`
`256   241  228  215  203  191  181  170  161  152  143  135`

### 10g.  Amiga effect codes

From NostalgicPlayer `Effect.cs` enum (Effect byte values 0–$0E):

| Code | Name | Arg bytes | Function |
|------|------|-----------|----------|
| $00 | EndOfTrack | 0 | Advance to next position; loop at end |
| $01 | Slide | 2 | Pitch slide: byte1=speed, byte2=counter |
| $02 | Mute | 0 | Silence channel immediately |
| $03 | WaitUntilNextRow | 0 | Stop processing this frame (frame boundary) |
| $04 | StopSong | 0 | End module playback |
| $05 | GlobalTranspose | 1 | Shift all notes by signed byte value |
| $06 | StartVibrato | 2 | byte1=speed, byte2=maxValue |
| $07 | StopVibrato | 0 | Disable pitch vibrato |
| $08 | Effect8 | 1 | Volume fade / channel transpose / half-volume (context-dependent) |
| $09 | Effect9 | 0 or 2 | Disable half-volume OR position restart |
| $0A | SetSpeed | 1 | Set playback speed (or delay speed if applicable) |
| $0B | GlobalVolumeFade | 1 | Master volume fade speed |
| $0C | SetGlobalVolume | 1 | Master volume level (0–64) |
| $0D | StartOrStopSoundFx | ? | Toggle sound effects channel |
| $0E | StopSoundFx | ? | Terminate sound effects |

### 10h.  Amiga arpeggio table

Located at `arpeggioListOffset`:
- Array of 16-bit offsets (one per arpeggio)
- Each arpeggio entry: variable-length byte sequence of semitone offsets
- Terminated by byte with high bit set ($80+)
- Default empty arpeggio: `[0x80]`

### 10i.  Amiga envelope table

Located at `envelopeListOffset`:
- Array of 16-bit offsets
- Each envelope entry:
  - 1st byte: speed (ticks per volume change)
  - Subsequent bytes: volume levels (0–127; byte with high bit = end marker)

### 10j.  Amiga vibrato (per-channel state)

- `VibratoDirection`: -1 (increasing), 0 (off), +1 (decreasing)
- `VibratoSpeed`: increment per frame
- `VibratoMaxValue`: peak deviation
- Current accumulated value added/subtracted from Amiga period

### 10k.  Global playing state (Amiga)

- `Transpose` (sbyte): global pitch shift
- `VolumeFadeSpeed`, `GlobalVolume`, `GlobalVolumeFadeSpeed`, `GlobalVolumeFadeCounter`
- `SquareChangePosition`, `SquareChangeDirection`: PWM / square wave animation
- `ExtraCounter`, `DelayCounterSpeed`, `DelayCounter`
- `Speed`

---

## 11.  Cross-Platform Compatibility

| Feature | C64 | ZX Spectrum | NES | Amiga |
|---------|-----|-------------|-----|-------|
| CPU | 6502 | Z80 | 6502 | 68000 |
| Song table | 7 bytes/subtune (3 voices) | compatible | 9 bytes/subtune (4 voices) | pointer-based |
| Pattern end byte | $88 | $87 | $FF | high-bit cmd |
| Tuning | 424 Hz | 390 Hz (2 semitones flat) | NES pitch tables | Amiga period tables |
| SID waveforms | $80/$40/$20/$10/$14/$42 | subset (fewer waveforms) | 2A03 equivalents | sample-based |
| Arpeggio table | present | present (identical structure) | present | present |
| Filter | early versions only | N/A | N/A | N/A |
| Brooke variant | 1986+ | 1986+ | NES port = C64 base | separate evolution |

---

## Leads to follow

1. **Bansai's Xenon ZX128→C64 conversion** (CSDb) — second C64 .asm disassembly; likely
   reveals Jason Brooke variant differences vs Panther driver.
   URL: search `csdb.dk` for scener 38332 or "Xenon ZX128 C64".

2. **realdmx/c64_6581_sid_players Whittaker_David/ full listing** — only Panther.asm
   confirmed; there may be more .asm files.
   Check: `https://api.github.com/repos/realdmx/c64_6581_sid_players/contents/Whittaker_David`

3. **David Whittaker Ripper.zip (CSDb 33379)** — ripper tool source code; decoding
   logic reveals how the format is identified in memory and how data is extracted.
   URL: `http://csdb.dk/getinternalfile.php/22425/David%20Whittaker%20Ripper.zip`

4. **Whittex rippers on Debyshire RAM disks** — later driver versions.

5. **NostalgicPlayer DavidWhittakerWorker.cs full source** — more detail on format
   recognition logic (esp. `subSongListOffset` derivation from player code offsets).
   URL: `https://raw.githubusercontent.com/neumatho/NostalgicPlayer/main/Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs`

6. **HVSC STIL.txt + BUGlist.txt** for Whittaker entries — per-SID ripper annotations
   may include driver version or load address notes.

7. **ExoticA EaglePlayers page** (TLS cert issue) — Amiga player source:
   `http://wt.exotica.org.uk/players.html` (EP_DWhittaker.lha, 6721 bytes)

8. **Jason Brooke VGMPF page** — gameography of Brooke-credited vs Whittaker-credited
   C64 games to identify which tunes use the post-June-1986 Brooke variant:
   `https://www.vgmpf.com/Wiki/index.php/Jason_Brooke`

9. **Tony Bybell's NES Menace disassembly** — referenced in VGMPF NES Driver page;
   original Menace .asm would show how the format translated to NES exactly.

10. **ZX Spectrum Whittaker player disassembly** — zxtunes.com (author 766) hosts 
    Spectrum tunes; World of Spectrum archives may have player source.
    `http://zxtunes.com/author.php?id=766&ln=eng`
