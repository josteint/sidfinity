---
source_url: synthesized from archive_jc64dis_disassembly.md + archive_sidid_fingerprints.md
fetched_via: derived 2026-06-15
fetch_date: 2026-06-15
author: derived from JC64dis 2.3 annotations by Stefano Tognon; sidid.cfg by Cadaver
content_date: driver (c) 1987/88
reliability: primary (from binary analysis)
---

# Ariston Format Summary — Music Data Structures

## Driver Architecture

The Ariston driver is a 3-voice C64 SID music driver using a hierarchical data model:
**Song → Track (orderlist) → Patterns → Notes + Effects**

3 voices play simultaneously, each with its own track pointer, pattern pointer,
and voice state. The engine processes one voice at a time in a loop (SID offsets 0, 7, $0E).

---

## Data Hierarchy

```
Song
 └── 3 Tracks (one per voice)
      └── Track: sequence of pattern-numbers / transpose commands / end marker
           └── Pattern: sequence of note/command bytes
                └── Note + Effects (instrument, length, vibrato, glissando, trill)
```

---

## Instrument Block (8 bytes)

```
Byte  Field
 0    Control        — SID waveform/gate control ($D404/$D40B/$D412)
 1    Attack/Decay   — packed nibbles: (attack << 4) | decay
 2    Sustain/Release — packed nibbles: (sustain << 4) | release
 3    Pulse Width    — 2-byte field (lo|hi) for $D402:$D403 / $D409:$D40A / $D410:$D411
 4    Vibrato        — packed nibbles: (step << 4) | size
 5    Pulse Sweep    — pulse width sweep rate (signed step)
 6    Trill Bits     — which entries in the trill buffer/table are active
 7    Effects        — bit-flags:
                        bit 0: drum effect BASS
                        bit 1: plunk effect
                        bit 2: echo effect
                        bit 3: drum effect SIDE
```

Up to 32 instruments (I00..I1F = $C0..$DF in pattern stream).

---

## Track / Orderlist Bytes

```
$00..$7F  — pattern number (0–127)
$80..$BF  — transpose DOWN by (byte & $3F) semitones
$C0..$FE  — transpose UP by (byte - $C0) semitones
$FF       — end of track (restart)
```

---

## Pattern Byte Commands

```
$00..$5F  — note (0=lowest, 95=highest; 8 octave range)
$7A dd nn — DVI: delay vibrato — dd=delay before vibrato, nn=note
$7B nn yy — GLI: glissando — nn=note, yy packed: (length<<4)|delay
$7C bb    — CTR: continue trill — bb=trill bits
$7D bb    — TRL: trill — bb=trill bits
$7E nn    — TIN: trill increment — nn=note offset
$7F nn    — TDE: trill decrement — nn=note offset
$80..$BF  — Lxx: note length (byte & $3F = 0..63)
$C0..$DF  — Ixx: instrument select (byte & $1F = 0..31)
$F0..$FB  — Sxx: set speed/tempo (byte & $0F = 0..11, 12 tempo levels)
$FC vv    — VOL: set volume/filter ($D418 write with value vv)
$FE       — STP: stop sound (gate off, silence)
$FF       — END: end of pattern (advance to next in track)
```

NOTE: $7A..$7F are the "special note commands" range. $60..$79 appears to be unused
(or part of the note table extension — the note range is 0..5F = 96 notes, so $60+
starts the command space).

---

## Frequency Table

- 96-note chromatic table
- PAL tuning: A4 = 459 Hz (per JC64dis annotation of Dark_Side.sid)
- NTSC tuning: A4 = 477 Hz
- VGMPF states "tuned at 424 Hz or 434 Hz" — this may refer to Ian_Crabtree_V1/V2 variants
- Ian Crabtree's own SIDs: "tuned at 433.5 Hz on PAL, 450 Hz on NTSC" (VGMPF)

The frequency table has 2-byte entries (lo/hi), addressed with SID stride offset.

---

## Voice State Variables (per-voice)

Each of the 3 voices maintains:
- Track pointer (lo/hi)
- Pattern pointer (lo/hi)
- Pattern index (current offset)
- Current note length counter
- Transpose value
- Trill bits / trill buffer / trill index / trill value
- Glissando state (length, delay)
- Pulse wave current value (lo/hi)
- Pulse wave direction (0=up)
- Vibrato frequency (lo/hi), step (lo/hi), counter, delay counter, size
- Instrument state (control, ADSR applied to SID)
- Effect flags (drum BASS/SIDE, plunk, echo)
- Allow sound flag
- Attack/Decay flag
- Release-not-max flag
- Inverse effect flag
- Pattern scan direction ($FE=inc forward, $DE=dec backward — bidirectional pattern play)

---

## Noteworthy Features

1. **Trill system:** 3-byte sequences in pattern encode note ornaments (TRL/TIN/TDE/CTR).
   A trill buffer per voice holds precomputed step values. CTR continues a trill without
   reloading.

2. **Glissando:** DVI and GLI commands encode smooth pitch slides. GLI packs length and
   delay in a single nibble-pair byte.

3. **Pulse sweep:** Instrument byte +5 controls pulse width sweep direction/rate; per-voice
   wave-direction flag tracks whether sweep is going up or down.

4. **Effects byte (inst +7):** Bitmask for BASS drum, SIDE drum, plunk, echo. The drum
   effects (BASS/SIDE) likely use SID noise waveform or ring-mod tricks for percussion.
   "Plunk" is a brief attack-decay with specific filter/waveform settings. "Echo" adds a
   delayed repeat of the note on the same voice.

5. **Phasing effect:** The distinctive Ariston "phasing" sound that Maniacs of Noise asked
   about. Likely implemented using the pulse sweep + vibrato + possibly ring modulation
   combination in the instrument settings. Not specifically labelled in the JC64dis
   annotations beyond the per-voice state variables.

6. **Bidirectional pattern scan:** The per-voice "instruction code FE inc / DE dec" implies
   patterns can be scanned in reverse. This is an unusual C64 music driver feature.

7. **12 tempo levels:** Speed commands $F0..$FB give 12 distinct tempo settings.

8. **Volume command:** $FC vv writes directly to $D418 (master volume + filter mode).
   This can change filter parameters mid-pattern.

---

## Known Driver Variants

1. **Ian_Crabtree_V1** — earliest, identified by specific $D400 write sequence
2. **Ian_Crabtree_V2** — second version, ADSR mask `AND #$0F` visible in fingerprint
3. **Wally_Beben** — improved drum variant (3 fingerprint sequences); used for Beben's own work
4. **Ariston Music Editor** (1988) — full editor binary by Philip Brabbin incorporating all above

The driver is relocatable (all table addresses are variable in fingerprints).
