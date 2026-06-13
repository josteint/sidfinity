---
source_url: local: pipelines/future_composer/docs/ (multiple files; see per-claim citations)
fetched_via: local read
fetch_date: 2026-06-14
author: jtr (synthesis from FC research corpus)
content_date: 2026-06-14
reliability: secondary (synthesis over primary FC sources)
---

# RoMuzak FC Inheritance — What FC V1.0 Carries and What RoMuzak Must Represent

## Scope and method

RoMuzak V6.2/V6.3 includes a built-in converter: "CVN Future Composer wandelt
Tracks und Sectoren zu 100%, Sounds zu 90%." (ROMUZAK.DOC, primary source).
The converter targets "FUTURE COMPOSER 0.18" per the EXTRAS/CONVERTER menu.
The "0.18" label appears to be an internal version designation for what the
scene calls FC V1.0 (Finnish Gold 1988) — RoMuzak was written in 1989,
contemporaneous with the FC V1.0/V2.x era only.

This note maps what FC V1.0 carries to what RoMuzak's internal data model
must therefore be able to represent, and flags which inferences are reliable
vs. open.

---

## FC V1.0 data model (RELIABLE — from FC research corpus)

Sources: `pipelines/future_composer/docs/research.md`,
`wiki_fc_v41_manual.md`, `csdb_format_inferences.md`,
`csdb_fc_editor_binaries.md`.

### Song/sequence hierarchy (3 voices)

FC V1.0 is a 3-voice tracker with a two-level hierarchy:

- **Track (sequence):** per-voice ordered list of pattern references +
  transposition commands. Terminated by $FF (restart). Entries are a
  variable-length byte stream, not fixed-stride structs.
  - `$00-$2B`: play pattern N
  - `$3F+`: repeat next pattern N times (`$43 $02` = play block 2 four times)
  - `$80+`: note transpose (semitone delta encoded in low bits)
  - `$FE`: stop
  - `$FF`: restart the track from the beginning

  Source: `wiki_fc_v41_manual.md` (FC V4.1 manual — confirms the same
  byte range semantics used since V1.0).

- **Pattern (block/sector):** variable-length byte stream of note events.
  - Plain note: pitch byte ($00-$5F, indexes 96-entry freq table: C-0..B-7)
  - Duration command (`DUR.xx`): sets duration for following notes (01-$20)
  - Instrument select (`SND.xx`): selects instrument 00-1F
  - Glide (`GLD.XYZ`): direction + delay + speed
  - Auto-portamento (`APM.xx`)
  - Continue (`CONT`): extends previous note
  - Pause (`PSE.xx`)
  - $FF: end of pattern

  Source: `wiki_fc_v41_manual.md` + `research.md`.

**NOTE:** The `wiki_fc_v41_manual.md` source is the FC V4.1 manual, which
documents V4. FC V1.0 was a subset. The subset that existed in FC "0.18"
(V1.0) is inferred to be: notes, DUR, SND, GLD, CONT, PSE — the core set
documented in ROMUZAK.DOC as matching RoMuzak's own sector command set.
The APM.xx command appears only in ROMUZAK.DOC (not FC V1.0) — it may be
a RoMuzak extension or a V2.x-era FC addition. OPEN.

### Instrument / sound definition (8 bytes in FC V4; V1.0 probably same)

FC V4.1 manual defines the instrument as exactly 8 bytes:

| Byte | Field |
|------|-------|
| 0 | Pulse level (lo-byte × 16 + hi-byte encoding) |
| 1 | Waveform register (= SID $D404 control byte) |
| 2 | Attack / Decay (= SID $D405) |
| 3 | Sustain / Release (= SID $D406) |
| 4 | Unused |
| 5 | Vibrato / Drumtype |
| 6 | Arpeggio CTRL |
| 7 | MCTRL: filter-enable (bit0), arp-enable (bit2), drum (bit4), gate-off ($40), gate-on ($80) |

Source: `wiki_fc_v41_manual.md` (FC V4.1 official manual).

ROMUZAK.DOC describes RoMuzak sounds as ALSO 8 bytes (B0..B7) with a
layout that maps almost perfectly to the FC layout. See the mapping below.

Up to 32 instruments (SND.00..SND.1F) in both FC and RoMuzak.

### Drum table (FC V1.0)

FC has a built-in drum table (8 drums, 0-7) accessible via the MCTRL Drum
flag (byte 7 bit4 + drum type in byte 5). The V1.0 drum table is hardcoded
in the player. V3+ added the editable drum table.

Source: `wiki_fc_v41_manual.md` (drum referenced as "Drumsound" in MCTRL).

### Vibrato (FC V1.0)

Two vibrato modes documented in ROMUZAK.DOC's B5 field description:
- Mode A: "Wie FUTURE COMPOSER, d.h. die Bits 6-3 geben die Geschwindigkeit
  an und die Bits 2-0 die Einschnittstaerke" — i.e. FC's own vibrato
  encoding: speed in bits 6-3, depth in bits 2-0
- Mode B: first nibble = strength, second nibble = speed (RoMuzak native)

This directly confirms that RoMuzak's B5 field can hold either FC vibrato
format or its own format, selected by B7 bit3.

### Filter (FC V1.0)

FC V1.0 had a global filter (not per-instrument). The ROMUZAK.DOC confirms
a global filter (SET FILTER sets two values: base freq + add factor, applied
to one voice at a time per MCTRL bit5).

FC V3+ added a filter TABLE (command-driven per-frame filter sweep). FC V1.0
appears to have only the static filter setup. Consistent with RoMuzak's V6
static filter (SET FILTER menu).

### Frequency table

96 entries (C-0 to B-7), 16-bit SID frequencies. Both FC V1.0 and RoMuzak
use this identical range (c-0 to b-7 confirmed in both manuals). The actual
frequency values may differ slightly between FC's table and RoMuzak's — OPEN.
RE: compare the freq table in the V6.3 SID binary against the FC V1.0 player.

### What FC V1.0 does NOT have (and therefore RoMuzak need not import)

- Wave tables (per-frame waveform sequences): added in FC V3.x. V1.0 has
  only the static waveform byte (B1).
- Pulse tables: same, V3.x addition.
- Filter tables: same, V3.x addition.
- Relocatable format: FC V1.0 loads at fixed address ($1800 typically).
  RoMuzak also uses a fixed address with its MEMORY MOVER to relocate.

---

## RoMuzak format vs. FC V1.0 — the mapping (from ROMUZAK.DOC primary)

Source: `src/romuzak_doc_vacsid_bundle.txt` (ROMUZAK.DOC extracted from
vacsid.zip, dated 1996-03-31, covers RoMuzak V6.2 + V7.9x).

### Track byte semantics: near-identical to FC V4.1

| Byte range | FC V4.1 meaning | RoMuzak V6.2 meaning |
|------------|-----------------|----------------------|
| $00-$3F | Play pattern N | Play sector N |
| $40-$7F | Repeat: play next pattern (`$3F+1` times) | Repeat: next sector `$40-xx+1` times |
| $80-$BF | Note transpose (semitone delta in low bits) | Note transpose ($80-xx semitones) |
| $C0-$FB | (sound transpose, FC V4 only) | Sound transpose ($C0-xx instrument offset) |
| $FC | (not in V4.1 manual) | Jump to byte N in track (2-byte: $FC N) |
| $FD | (song-wide restart marker in V4.1) | Restart ALL tracks |
| $FE | Stop playing | Stop entire piece |
| $FF | Restart track | Restart this track from start |

The FC V4.1 manual's `$3F+` repeat syntax maps exactly to RoMuzak's `$40-$7F`
range. The sound-transpose range `$C0-$FB` appears to be a RoMuzak extension
not present in FC V1.0 (FC V4.1 has no sound-transpose in the track stream).

### Sector command set mapping (pattern-level)

RoMuzak V6.2 sector commands that directly map FC V1.0 pattern commands:

| RoMuzak command | FC V1.0 equivalent | Notes |
|-----------------|--------------------|-------|
| Note c-0..b-7 | Note $00-$5F (pitch byte) | Same 8-octave range |
| DUR.xx | Duration byte in FC | Both: 01-$20 range |
| SND.xx | SND.xx | Both: 00-$1F (32 instruments) |
| GLD.XYZ (direction + delay + speed) | GLD glide command | Slightly different encoding — see below |
| APM.xx | APM portamento (V2.x?) | Possibly a shared convention or RM extension |
| CONT | Tie / legato byte | Both use it for note extension |
| PSE.xx | Pause | Direct analog |

### Glide encoding difference (critical for conversion)

ROMUZAK.DOC's GLD.XYZ: X=direction (+/-), Y=delay in DUR/2 (0-7),
Z=speed (0-f).

FC V4.1 manual's Glide: `gl:xx,y` where xx = rate (bit7 = up if set,
magnitude in 0-6 bits), y = delay.

These are structurally the same but the converter must swap the encoding.
ROMUZAK.DOC confirms: "CVN Future Composer wandelt Tracks und Sectoren zu
100%" — so the conversion is exact for these commands.

### Instrument (Sound) mapping

| Byte | RoMuzak V6.2 (ROMUZAK.DOC) | FC V1.0 (research + wiki_fc_v41) |
|------|-----------------------------|----------------------------------|
| B0 | PW lo-byte×16 + hi-byte; if SEEK: seek value $00-$FF | Pulse level (byte 0, same encoding) |
| B1 | Waveform register (= SID $D404) | Waveform register (byte 1 = SID $D404) |
| B2 | Attack/Decay (= SID $D405) | Attack/Decay (byte 2 = SID $D405) |
| B3 | Sustain/Release (= SID $D406) | Sustain/Release (byte 3 = SID $D406) |
| B4 | a) Drum type / b) Echo value / c) SoundChange param | Unused (byte 4) |
| B5 | Freq vibrato: FC-mode (bits 6-3 speed, 2-0 depth) OR normal-mode | Vibrato/Drumtype (byte 5) — same FC-mode encoding |
| B6 | PW vibrato (strength/speed) OR CH80 freq OR FreqDrum freq | Arpeggio CTRL (byte 6) |
| B7 | Effect control flags (8 bits, see below) | MCTRL (byte 7) — see below |

The first four bytes (B0-B3) are byte-identical between FC and RoMuzak.
B5's FC vibrato mode matches FC byte 5 encoding exactly.
B6 diverges: FC uses byte 6 for arpeggio; RoMuzak uses B6 for PW-vibrato.
B7 flag meanings overlap substantially but not entirely.

### B7 / MCTRL flag mapping

| Bit | RoMuzak B7 | FC MCTRL (byte 7) |
|-----|------------|-------------------|
| bit0 (01) | Drum: play drum (0-7 in B4) | Filter: enable filter for voice |
| bit1 (02) | Arpeggio: use arp bytes in next sound-table entries | (not present in FC MCTRL per V4.1 manual) |
| bit2 (04) | Echo: cycle between two notes | Arpeggio enable (bit2 per V4.1) |
| bit3 (08) | B5 mode switch: 0=FC-vibrato, 1=Normal-vibrato | — |
| bit4 (10) | SEEK: sweep PW from 0 upward | Drum enable (bit4) |
| bit5 (20) | Filter enable for this voice | — |
| bit6 (40) | After 2 DUR, switch waveform to $40 (rectangle) | Gate-off ($40) |
| bit7 (80) | First DUR in noise with high freq | Gate-on ($80) |
| bit6+7 (c0) | Alternate waveform every half DUR with CH80 noise | — |

**Key divergence:** FC MCTRL bit0 = Filter; RoMuzak B7 bit0 = Drum.
The converter "CVN Future Composer" must remap: FC drum→RoMuzak bit0,
FC filter→RoMuzak bit5. This is where the "90%" sound conversion score
originates — the bit flags don't map 1:1.

---

## What RoMuzak's data model must represent (inferred from FC converter)

Since the FC→RoMuzak converter achieves "Tracks und Sectoren zu 100%,
Sounds zu 90%", RoMuzak's format must be able to hold:

1. **8 independent melodies (tunes) sharing a global sector pool** — confirmed
   by ROMUZAK.DOC: "Insgesamt verarbeitet die Musikroutine 8 verschiedene
   Track-Anzeigen (Melodien)." FC V1.0 has only 3 subtunes (0-2); RoMuzak
   extends this to 8.

2. **3 tracks per melody, up to $40 (64) sectors shared globally** —
   ROMUZAK.DOC: "Es gibt insgesamt $40 (dez: 64) Sectoren."
   FC V1.0 has up to ~44 patterns addressable ($2B+1) inline.

3. **Variable-length sector streams** of notes + DUR + SND + GLD + CONT +
   PSE commands, terminated by $FF or $FE. Exact same semantic as FC patterns.

4. **Note transpose and sound transpose as per-track-stream commands** —
   track bytes $80-$BF and $C0-$FB. FC V1.0 only has note-transpose;
   sound-transpose is a RoMuzak extension.

5. **Repeat count as inline track byte** ($40-$7F range). Matches FC exactly.

6. **Up to 32 instruments, 8 bytes each**, with the B0-B3 layout
   byte-compatible with FC's instrument bytes 0-3 (pulse, waveform, ADSR).

7. **Drum table: 8 drums (0-7)** built-in (V6.2); drums 8-$F editable in
   V7.94+ (XDSE). Each drum: 2 rows × 16 bytes (waveforms row + frequencies
   row), $FF = drum end.

8. **Global filter parameters** (base freq + add factor), not per-instrument.

9. **Zero-page state at $f8-$fb** (ZEROPAGE MOVER confirms these 4 bytes
   are the player's zero-page footprint in V6.2). Additional state likely
   at fixed absolute addresses (track pointers per voice, sector pointers
   per voice, current SND numbers, DUR counters, GLD state).

---

## What is UNKNOWN about how RoMuzak stores it (RE needed)

1. **Exact binary layout of the saved music file.** ROMUZAK.DOC describes
   the editor UI but not the on-disk byte layout. The "LOAD ALL" file
   format is undocumented. OPEN: mount the d64 disk image in VICE, save
   a test song, extract the .prg from the d64, and map the bytes.

2. **Track stream encoding: are track bytes preceded by a length or
   self-delimiting?** The doc shows a 21-row × 12-byte window (252 bytes
   per window); this is a UI parameter, not necessarily the stored size.
   Whether tracks are zero-padded to a fixed block or stored as variable
   streams is unknown.

3. **Sector format: exact byte encoding of sector commands.** The doc
   gives human-readable descriptions (DUR.xx, SND.xx, GLD.XYZ) but not
   the binary byte values. Key unknowns:
   - What byte value encodes DUR.xx (is it a fixed opcode prefix + parameter
     byte, or a range like FC's inline pitch bytes)?
   - What byte value encodes SND.xx vs. a note pitch?
   - How GLD.XYZ is packed into bytes (3-byte command or nibble-packed).
   OPEN: RE the player's sector-parsing loop to find the dispatch table.

4. **Arpeggio storage.** ROMUZAK.DOC says arpeggios are stored "in the next
   Sound-Table entries" when bit1 of B7 is set. This implies that arpeggio
   data is stored as additional pseudo-instrument bytes immediately following
   the base instrument record. The exact termination (how many arp bytes, how
   the FF wrap works) is not stated.

5. **Precise zero-page map beyond $f8-$fb.** The skull thread notes that
   splitting channels required "data-swapping for tracks/instruments/patterns",
   implying additional per-voice state outside the documented $f8-$fb range.
   OPEN: full zero-page map from disassembly.

6. **Memory map of a saved music file.** The BASIC POKE/SYS interface shows
   the default player at $8000 (init=$8000, play=$8003, data starts at
   $8006?). The MEMORY MOVER can relocate to $0400-$f000. The split between
   player code and data is unknown without the binary.

---

## Leads to follow

1. **Binary sector-command encoding** — highest priority for the extractor.
   OPEN RE: disassemble the sector-parsing inner loop of the V6.3 player.
   Look for the dispatch after a byte is read from the sector stream: CMP
   thresholds will reveal the command ranges.

2. **Saved file binary layout** — mount the d64 from archive.org, save a
   minimal test song, extract the PRG, map against the doc's description.
   This is gather (d64 tool, no emulator needed if we use c1541 or a Python
   d64 library).

3. **FC V1.0 arpeggio encoding** — the FC corpus (csdb_format_inferences.md)
   describes FC V3.x arpeggio but not V1.0 specifically. Check whether FC V1.0
   had arpeggio at all (the MCTRL bit2 per the V4.1 manual suggests yes).
   The ROMUZAK.DOC note that "Arpeggios werden als Echo-Effekte umgewandelt"
   when converting FROM FC suggests that FC's arpeggio model doesn't map
   directly to RoMuzak's arpeggio — RoMuzak converts them to the Echo effect
   instead.

4. **Drum table binary layout in V7.94+** — the XDSE description ("2 rows
   × 16 bytes: waveforms + frequencies, $FF = end") is explicit and RE-ready.
   Find the drum table at a fixed offset in the player binary.
