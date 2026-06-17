---
source_url: https://csdb.dk/release/?id=66494
fetched_via: direct
fetch_date: 2026-06-17
author: various CSDb contributors
content_date: various
reliability: primary
---

# CSDb: SidWinder — Forum / community notes and technical findings

## Summary of CSDb coverage

No substantive technical forum discussion found on CSDb for either SIDwinder
release (ID 66494 = V01.22, ID 101758 = V01.23). The forum thread URL
`csdb.dk/forums/?csdbentrytype=release&csdbentry=66494&entrytopic=1`
redirected to the CSDb homepage; the forum thread does not appear to contain
any posts visible to unauthenticated visitors.

Production notes found:
- **V01.22 (ID 66494):** No production notes visible.
- **V01.23 (ID 101758):** One note: "Includes a packer and an ASCII file reader."
  Tested by: Luca of Fantastic Italian Research Enterprise.
  Music in V01.23 package: Classical, Draxish, Drummer, Glorious, Lost Love,
  Memories, Precisely, Radiation, Realbeat, Southern, Speed Up!, Status Quo,
  Sweet Lullaby, Uncertain (14 tracks).

## CSDb release metadata (both versions)

| Field | V01.22 | V01.23 |
|---|---|---|
| CSDb ID | 66494 | 101758 |
| Year | 1999 | 2000 (15 March) |
| Group | Natural Beat | Natural Beat |
| Code | Taki | Taki |
| Music | Taki | Luca (FIRE) |
| Testing | — | Luca (FIRE) |
| Downloads (CSDb) | 391 | 534 |

## Natural Beat group (CSDb ID 811)

Members at time of SidWinder releases:
- Taki — Musician/Coder, Hungary
- Chubrock — Musician
- Dec — Coder
- Peet — Musician

Former members: Decoy, Mercury, Silc (all Musicians).

Complete Natural Beat release history:
| Title | ID | Year | Type |
|---|---|---|---|
| SIDwinder V01.23 | 101758 | 2000 | Tool |
| SIDwinder V01.22 | 66494 | 1999 | Tool |
| Cubic Player | 8708 | 1998 | Tool |
| Revive | 97701 | 1996 | Music |
| Virtuality | 8707 | 1996 | Music Collection |
| Desert | 88768 | 1994 | Music |
| Harmony | 5075 | 1994 | Music |
| Let's Summer | 88776 | 1994 | Music |
| Relative | 88771 | 1994 | Music |
| Brainwash | 29836 | 1994 | Music |
| Fruitbat | 97536 | 1994 | Music |
| Gotic | 97533 | 1994 | Music |
| Smilygirl | 29840 | 1994 | Music |
| Speed Up | 97551 | 1994 | Music |
| 18 Years Mercury | 106532 | 1994 | One-File Demo |
| According | 97481 | 1993 | Music |
| Corruption | 97480 | 1993 | Music |
| Disno | 8899 | 1993 | Music |
| 18 Years Clarence | 36916 | 1993 | One-File Demo |
| Naturality | 8709 | 1993 | Music Collection |

Cubic Player (1998) is notable: it bundles 13 Taki SidWinder tunes as an
integrated player. User comment: "press H for help menu and to see all the
amazing options [of SID monitoring]."

## Taki (CSDb scener ID 2274)

- Country: Hungary
- Function: Musician / Coder
- Groups: Natural Beat (current), formerly Craftmen Company, Stunts
- Events: Rage & Scenest 1998, Scenest 1996
- Won 1st place C64 Music at Chromance+Faces 1993 competition ("Surprise",
  CSDB #76106)
- Other tool: "Taki's Music Analyzer V1.0" (CSDB #99142, undated)

## Version history discovered in HVSC binaries

Surveying all 117 SidWinder SIDs in HVSC #84 by parsing the embedded PETSCII
version string at offset 0x1009 of the player binary:

| Version string | Count | Notes |
|---|---|---|
| V01.14 | 2 SIDs | Earliest: Victory.sid (Taki), Dankos_Remix.sid |
| V01.20 | 2 SIDs | Speed_Up.sid (Taki), Foolish.sid (Taki) |
| V01.22 | 62 SIDs | The dominant version; all Factor6, most Eclipse tunes |
| V01.23 | 8 SIDs | Eclipse and Zapac tunes from 2000-era |
| V01.36 | 3 SIDs | Taki only: Bastard_tune_2, Mr_Thomas, Reynbow |
| V01.37 | 1 SID | Taki only: Impulse.sid |

The version string is a PETSCII-encoded string (uppercase letters stored as
bytes 0x01-0x1A = A-Z; some variants use plain ASCII with bit-7 set for
reverse-video display). Eclipse's tunes use the string " -SIDWINDER V1.22-MUSIC
BY ECLIPSE/..." with plain-ASCII encoding (bit 7 set on some chars). Taki's
own tunes use "TAKI'S PLAYER V01.22-=> MUSIC BY TAKI/NATURAL BEAT <=".

## Technical findings from binary analysis (Radiation.sid as reference)

### Binary layout (Radiation.sid, V01.22, load=0x1000, 3150 bytes)

```
0x1000-0x1002  JMP stub to init routine (0x1593)
0x1003-0x1005  JMP stub to play/sequence routine (0x1100)
0x1006-0x1008  JMP stub to effects-only routine (0x13BD)
0x1009-0x103F  PETSCII version/author string (terminated by 0x01 padding)
0x1040-0x109F  Frequency table LO bytes (96 notes = 8 octaves x 12)
0x10A0-0x10FF  Frequency table HI bytes (96 notes = 8 octaves x 12)
0x1100-0x1592  Player code (note sequencer + effect chain)
0x1593-0x161F  Init routine
0x1620-0x168F  Per-voice runtime state (3 voices, 7-byte stride: X = 0, 7, 0xE)
0x1690-0x16AF  Global state variables (tempo counter, master vol, etc.)
0x16B0-0x173F  Instrument tables (parallel arrays, indexed by instrument#)
0x1734-...     Waveform program data (variable-length sequences)
...            Pulse program data
...            Arpeggio / other effect program data
0x1887+        Per-voice orderlists (one per subtune per voice)
0x1C00-0x1C4D  Subtune table (6 bytes per subtune: V1_lo, V2_lo, V3_lo, V1_hi, V2_hi, V3_hi)
```

### Three-vector architecture

The engine exports three callable entry points:
1. **0x1000 → init**: receives subtune number in A (0-based). Sets up voice
   state, loads orderlist pointers, clears SID chip (writes 0x00 to $D400-$D418).
2. **0x1003 → sequence play**: processes orderlists for all 3 voices, fetches
   new pattern bytes, triggers note events, handles ordering/looping.
3. **0x1006 → effects only**: runs the arpeggio/pulse/vibrato/glide chain
   without advancing the note sequence. Used in Drummer.sid's 2x CIA timing to
   call effects at double rate.

### Frequency table

Two separate 96-byte arrays (lo at 0x1040, hi at 0x10A0) covering 8 octaves
(96 notes total). Combined as `freq = lo[note] | (hi[note] << 8)`. Written to
$D400,X and $D401,X (per-voice, X = 0/7/14).

### Voice state layout (stride 7, X = 0, 7, 0xE for voices 1-3)

```
$1620,X  duration counter (frames remaining on current note)
$1621,X  gate flag: 0xFE = gate-off; used to suppress gate re-trigger
$1622,X  current note byte (0xC0 = tie/continue flag)
$1623,X  previous note byte (backup)
$1624,X  sequence step counter (frames left for sequence byte)
$1625,X  sequence step value (working copy)
$1626,X  modifier byte (from sequence; e.g. pitch offset or effect flag)
```

Per-voice sequence pointers (not stride-7, separate area):
```
$1636,X  orderlist ptr lo  (X used as voice index: 0, 7, 14)
$1637,X  orderlist ptr hi
$1638,X  orderlist position counter
$1639,X  pattern ptr lo (loaded from orderlist reference)
$163A,X  pattern ptr hi
$163B,X  position within current pattern
```

Per-voice instrument index:
```
$1675,X  current instrument number (0-63)
```

Per-voice effect state (some variables, collected from code refs):
```
$163C,X  vibrato phase counter
$164A,X  arpeggio program position
$164B,X  arpeggio step counter
$164C,X  arpeggio value lo
$164D,X  arpeggio value hi
$164E,X  note frequency accumulator lo (for pitch effects)
$164F,X  frequency delta lo (glide/vibrato)
$1650,X  frequency delta hi
$1663,X  waveform program position
$1675,X  instrument number
```

### Instrument table layout (18+ instruments, indexed by Y = inst#)

Parallel arrays in the range 0x16B0-0x17DF:

| Address | Field | SID register written |
|---|---|---|
| 0x16B6+Y | attack/decay byte | $D405,X (AD) |
| 0x16C8+Y | sustain/release byte | $D406,X (SR) |
| 0x16DA+Y | note duration (frames) | $1620,X (runtime) |
| 0x16EC+Y | waveform program index | $1663,X (runtime) |
| 0x1710+Y | vibrato speed | $163C or similar (runtime) |
| 0x1722+Y | vibrato depth | runtime |
| 0x16FE+Y | pulse program index | runtime |
| 0x17DF+Y  | arpeggio data index | runtime |

Number of instruments: up to 64 (instrument byte AND #$3F in sequence decoder).
In Radiation.sid approximately 18 instruments are used.

### Sequence / orderlist format

The engine reads bytes sequentially from an orderlist (one per voice).
Byte semantics in the sequence stream (read via `LDA ($FB),Y`):

| Range | Meaning |
|---|---|
| 0x00-0x5E | Note value (0-based; 0=C in lowest octave) |
| 0x5F | Rest (silence; writes 0x00 to $D405/$D406 and gate-off) |
| 0x60-0x6F | Jump/loop command (JMP $1387 path) |
| 0x70-0x7F | Possibly transpose or other sub-command |
| 0x80-0xBF | Modifier byte (e.g. pitch offset, transpose; AND #$3F) |
| 0xC0-0xFF | Instrument select (AND #$3F = instrument 0-63); must be followed by a note/rest byte |
| 0xF8-0xFF | Speed/tempo (sub 0xF7, shift left 3 → tempo frames): 0xF8=8, 0xFF=64 |
| 0xFF at start | End-of-sequence / loop marker; next byte = loop-back position |

**Pairs**: an instrument-select byte (0xC0+) is always followed by a second byte
(note or modifier). The step counter is advanced once per pair.

**Duration**: duration counts come from the instrument table ($16DA,Y), not from
the sequence directly. The sequence byte 0x41 (decimal 65) would be interpreted
as a note value 65 = 0x41 (within 0-0x5E range), NOT as a duration.

### Effect chain

Called on every play() frame (0x1003) for effects, and optionally separately
via 0x1006 (Drummer's 2x CIA mode):

1. **Waveform program** (0x1419 area): index into waveform sequence table at
   0x1734. Program bytes select SID waveform written to $D404,X. Advances
   automatically each frame. 0xFF = end/loop.
2. **Vibrato** (0x13C9 area): table-driven frequency modulation using speed +
   depth from instrument table. Uses sine-like table at 0x1693+.
3. **Glide / portamento**: frequency delta accumulation via $164F/$1650,X.
4. **Arpeggio**: index into arp table, cycles through note offsets per frame.
   Table at 0x17DF+. Uses $164A-$164D,X state.
5. **Pulse sweep**: reads pulse program table at 0x1827+, writes delta to
   $D402,X / $D403,X. Table contains signed deltas; 0xFF = end/loop.
6. **Filter / master vol**: $D415, $D416, $D417, $D418 written from global
   state variables at 0x168E+ area. Filter cutoff, resonance/routing,
   master volume.

### Subtune table format (at 0x1C00)

```
6 bytes per subtune entry:
  byte 0: voice 1 orderlist base lo
  byte 1: voice 2 orderlist base lo
  byte 2: voice 3 orderlist base lo
  byte 3: voice 1 orderlist base hi
  byte 4: voice 2 orderlist base hi
  byte 5: voice 3 orderlist base hi
```

Subtune 0 of Radiation.sid: `87 B8 E9 18 18 18`
→ V1 orderlist at 0x1887, V2 at 0x18B8, V3 at 0x18E9.

The init routine is called with A = subtune number; it reads Y = A (0-indexed)
then loads orderlist pointers from `$1C00+Y`, `$1C01+Y`, `$1C02+Y` (lo bytes)
and `$1C03+Y`, `$1C04+Y`, `$1C05+Y` (hi bytes). This means only one subtune is
supported per 6-byte stride at Y=0; multi-subtune tunes would need Y multiplied
by a stride, but from the init code seen the stride appears to be larger (the
init probes `$1693+Y` for additional data, suggesting Y is pre-scaled elsewhere).

### Drummer.sid: 2x CIA mode

Drummer.sid (MUSICIANS/T/Taki/Drummer.sid) declares init at 0x1C00 and play at
0x1C12 in the PSID header with speed=0x00000001 (CIA-timed). The code appended
at 0x1C00-0x1C22 is a thin wrapper:

```
init (0x1C00):
  LDX #$63, LDY #$26
  STX $DC04 ; CIA1 timer A lo = 0x63
  STY $DC05 ; CIA1 timer A hi = 0x26 → timer period = 0x2663 = 9827 cycles ≈ PAL/2
  LDX #$02
  STX $1C22 ; initialize frame counter (self-modified)
  JMP $1000  ; call SidWinder init

play IRQ (0x1C12):
  DEC $1C22
  BNE (branch to play)
  LDX #$02 ; reset counter to 2
  STX $1C22
  JMP $1003 ; call SidWinder full play (sequence + effects)
  ; (alternate: JMP $1006 - effects only, for odd frames)
```

Net effect: SidWinder play() is called at ~100 Hz (every 9827 cycles on PAL),
with the sequence advancing every other frame (50 Hz effective sequence rate)
and effects running at full 100 Hz.

### sidid.cfg fingerprint

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

Decoding: `LDA abs ; F0 = BEQ ; CE = DEC abs ; 88 = DEY ; 4C = JMP ; B9 = LDA abs,Y ;
C9 = CMP imm ; 90 = BCC ; ... ; A8 = TAY`

This matches the outer play loop pattern at ~0x1131-0x113C across all V01.xx versions.

### Multi-composer corpus (all 117 HVSC SIDs)

```
Composers using SidWinder:
  MUSICIANS/E/Eclipse/  — 19 SIDs (V01.22: 11, V01.23: 8)
  MUSICIANS/F/Factor6/  — 55 SIDs (all V01.22)
  MUSICIANS/T/Taki/     — 19 SIDs (V01.14: 1, V01.20: 2, V01.22: 13, V01.36: 2, V01.37: 1)
  MUSICIANS/Z/Zapac/    — 4 SIDs (V01.23)
```

Factor6 is the largest user of SidWinder (55 SIDs, all V01.22), suggesting
the format was widely distributed and used by other Hungarian/Central-European
composers in the demo scene circa 1999-2002.

---

## Leads to follow

- **V01.23 changelog**: Only production note is "includes a packer and an ASCII
  file reader." The actual binary differences between V01.22 and V01.23 are
  uncharted — worth a binary diff on representative SIDs.
- **V01.14 → V01.20 → V01.22 progression**: Victory.sid and Dankos_Remix.sid
  contain V01.14 binaries. Speed_Up and Foolish contain V01.20. A disassembly
  diff would reveal when the instrument table layout, effect chain, and subtune
  format were established.
- **V01.36 / V01.37**: Taki's Reynbow, Mr_Thomas, Bastard_tune_2, Impulse use
  these later versions. These are later than the publicly-released V01.23
  (CSDb) — may have been internal-only revisions.
- **No CSDb forum discussion found**: try Lemon64 (search requires login),
  Forum64.de (German-language C64 forum), or direct contact with Eclipse group
  members (Factor6, Zak) who used SidWinder extensively.
- **Taki's Music Analyzer V1.0** (CSDb #99142): may document the SidWinder
  internal format visually (it's a monitoring tool per description); worth
  downloading and examining the disk image.
- **FTP archives**: ftp.padua.org and c64.rulez.org carried Natural Beat
  releases (from Cubic Player notes). The SidWinder disk images on these FTPs
  may include documentation or README files not present in the HVSC SID files.
- **Useful CSDb usernames to check for SidWinder knowledge**:
  - Eclipse (composer group, 19 SIDs) — CSDb search for Eclipse group page
  - Factor6 (composer, 55 SIDs) — CSDb scener page
  - Luca/FIRE (tester of V01.23) — may have format notes
  - Zapac (4 SIDs, incl. Retrogathering 2012) — may have received format docs
- **Cross-reference**: `pipelines/sidwinder/docs/format_spec.md` and
  `format_from_source.md` for any format details already captured from source
  or binary analysis in prior research sweeps.
