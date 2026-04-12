---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg, https://github.com/cadaver/sidid/blob/master/sidid.c, https://github.com/cadaver/sidid/blob/master/sidid.nfo
fetched_via: direct
fetch_date: 2026-04-11
author: Lasse Oorni (Cadaver) — sidid tool; signatures contributed by Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos
content_date: unknown (sidid maintained through at least 2020s)
reliability: primary
notes: multiple sources — HVSC DOCUMENTS directory (local read), cadaver/sidid GitHub source code and config (primary), WilfredC64/player-id, libsidplayfp, and CSDb release pages. The sidid.cfg signature database and sidid.c matching algorithm are primary source material (actual tool source code). HVSC STIL and CSDb entries are secondary.
---

# DMC (Demo Music Creator) — External Research

Research collected from HVSC documentation, SIDId source code, and related sources.

## 1. HVSC Documentation

### HVSC DOCUMENTS Directory

The HVSC `DOCUMENTS/` directory (`data/C64Music/DOCUMENTS/`) contains no dedicated DMC format documentation. DMC is referenced only in:

- **STIL.txt** — User comments mentioning DMC as a composition tool (e.g. "composed using DMC V5.0+", "done with DMC V4.0")
- **Musicians.txt** — Lists "Danish Music Company (DMC)" as a music group (unrelated to the editor)
- **Update_Announcements/** — Various updates mentioning new DMC tunes added to HVSC

No byte-level format spec, no player disassembly, no technical documentation exists in HVSC's shipped docs.

### HVSC SIDId Output (sidid_full.txt)

The project's `data/sidid_full.txt` (61,634 lines) contains SIDId identification results for the entire HVSC collection:

| SIDId Label | Count | Notes |
|-------------|-------|-------|
| DMC         | 10,747 | Generic DMC (V4/V5 combined, not version-specific) |
| DMC_V6.x    | 16 | Separately identified by unique init signature |
| (unmatched) | ~12 | A handful tagged as Bjerregaard, GRG, Soundmonitor, MoN/FutureComposer |

**Key finding:** SIDId does NOT distinguish V4 from V5 — both match under the generic "DMC" label. The parenthesized `(DMC_V4.x)` and `(DMC_V5.x)` entries in sidid.cfg are sub-signatures of the main "DMC" entry (see Section 2 below), not separate player identifications. Only V6.x has its own top-level entry.

### STIL (SID Tune Information List)

STIL entries for DMC songs are purely editorial comments — composition notes, version history, artist credits. No technical format information. Example entries:

- Richard Bayliss compositions noting "composed using DMC V5.0+" and "DMC V4.0"
- Version mentions: V4.0, V5.0+, V7.0
- References to DMC's integrated packer and the Motiv 8 packer for V5

## 2. SIDId Source Code and Signature Database

### Source: [cadaver/sidid](https://github.com/cadaver/sidid) on GitHub

SIDId V1.09 by Cadaver (Lasse Oorni), with signatures by Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, and Prof. Chaos.

### Signature Matching Algorithm

From `sidid.c` — the `identifybytes()` function:

```c
int identifybytes(int *bytes, unsigned char *buffer, int length)
{
    int c = 0, d = 0, rc = 0, rd = 0;

    while (c < length) {
        if (d == rd) {
            // Searching for first byte match
            if (buffer[c] == bytes[d]) {
                rc = c+1;
                d++;
            }
            c++;
        }
        else {
            if (bytes[d] == END) return 1;  // Pattern complete
            if (bytes[d] == AND) {
                // Skip forward in buffer until next pattern byte found
                d++;
                while (c < length) {
                    if (buffer[c] == bytes[d]) {
                        rc = c+1;
                        rd = d;
                        break;
                    }
                    c++;
                }
                if (c >= length) return 0;
            }
            if ((bytes[d] != ANY) && (buffer[c] != bytes[d])) {
                // Mismatch: backtrack to recovery point
                c = rc;
                d = rd;
            }
            else {
                c++;
                d++;
            }
        }
    }
    if (bytes[d] == END) return 1;
    return 0;
}
```

**Special tokens:**
- `??` (ANY = -2): Matches any single byte (wildcard)
- `AND` (-3): Non-contiguous match — scans forward in buffer to find next pattern byte, then resumes contiguous matching from there
- `END` (-1): Pattern complete, return match

**Matching behavior:**
1. Scans buffer for first byte of pattern
2. Once found, attempts contiguous match (wildcards allowed)
3. On mismatch, backtracks to recovery point and resumes scanning
4. `AND` allows the pattern to skip arbitrary bytes between two parts of the signature

### Config File Structure

Signatures are organized hierarchically:
- A **top-level name** (no parentheses) creates a new player identity
- Lines starting with `(name)` are sub-signatures — version-specific refinements under the parent
- Each player can have multiple signature lines; any match identifies the player

### DMC Signature Entries (from sidid.cfg)

#### DMC (generic — matches V4.x and V5.x)

Top-level entry. This is what gets reported in sidid output.

```
DMC
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60 END
```

**6502 disassembly of signature:**
```
CLC
ADC $????,X    ; 18 7D ?? ??
STA $????,Y    ; 99 ?? ??
LDA $????,X    ; BD ?? ??
ADC $????,X    ; 7D ?? ??
...            ; ?? ?? ??
LDA $????,X    ; BD ?? ??
STA $????,Y    ; 99 ?? ??
LDA $????,X    ; BD ?? ??
STA $????,Y    ; 99 ?? ??
LDA $????,X    ; BD ?? ??
AND $????,X    ; 3D ?? ??
STA $????,Y    ; 99 ?? ??
RTS            ; 60
```

This matches the SID register write subroutine — a function that adds frequency values, stores results, and masks control bits. Present in both V4 and V5.

#### DMC_V4.x (sub-signature)

```
(DMC_V4.x)
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0 END
```

**6502 disassembly:**
```
INC $????,X    ; FE ?? ??
LDA $????,X    ; BD ?? ??
CLC            ; 18
ADC $????,X    ; 7D ?? ??
STA $????,X    ; 9D ?? ??
LDA $????,X    ; BD ?? ??
ADC #$00       ; 69 00
BIT $????      ; 2C ?? ??
LDA $????,X    ; BD ?? ??
AND #$01       ; 29 01
BNE ...        ; D0
```

This matches the V4 pulse width modulation routine — incrementing a counter, adding with carry, testing a flag, and branching on pulse direction.

#### DMC_V5.x (sub-signature)

```
(DMC_V5.x)
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60 END
```

**6502 disassembly:**
```
LDY $????,X    ; BC ?? ??
LDA $????,Y    ; B9 ?? ??
CMP #$90       ; C9 90
BNE ...        ; D0
[AND — skip to next part]
LDA $????,X    ; BD ?? ??
AND $????,X    ; 3D ?? ??
STA $????,Y    ; 99 ?? ??
RTS            ; 60
```

This matches the V5 wave table processing — loading the wave table pointer via Y, reading the wave table byte, comparing against $90 (the loop-back threshold), then later applying AND mask and storing result. The `AND` token in the signature allows non-contiguous matching between the two code sections.

#### DMC_V6.x (separate top-level entry)

```
DMC_V6.x
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20 END
```

**6502 disassembly:**
```
LDA #$02       ; A9 02
STA $????,X    ; 9D ?? ??
LDA #$00       ; A9 00
STA $????,X    ; 9D ?? ??
DEX            ; CA
BPL loop       ; 10 F3
STA $????      ; 8D ?? ??
LDA #$08       ; A9 08
STA $D404      ; 8D 04 D4  (voice 1 control reg)
STA $D40B      ; 8D 0B D4  (voice 2 control reg)
STA $D412      ; 8D 12 D4  (voice 3 control reg)
STA $D411      ; 8D 11 D4  (voice 3 freq hi — likely a bug or special init)
LDA #$1F       ; A9 1F
STA $D418      ; 8D 18 D4  (volume/filter mode = max volume, all filters)
LDA #$F2       ; A9 F2
STA $D417      ; 8D 17 D4  (filter resonance/route)
RTS            ; 60
DEC $????      ; CE ?? ??
BMI ...        ; 30 69
JSR $????      ; 20 ...
```

This is the V6 **init routine** — it initializes per-voice variables, writes $08 (test bit) to all three voice control registers, sets volume to max ($1F), sets filter routing ($F2), then continues into the play speed decrement. V6 is the only version with a distinct enough init to get its own top-level SIDId entry.

### How SIDId Distinguishes Versions

1. **Generic "DMC"** label: Matched by the SID register write subroutine (present in all versions)
2. **V4 vs V5**: Sub-signatures `(DMC_V4.x)` and `(DMC_V5.x)` refine the match but both report as "DMC" in output
3. **V6**: Has its own top-level entry because its init routine is uniquely identifiable
4. **V7**: Uses V4 player code, so matches as generic "DMC" (same as V4). No separate V7 signature exists.
5. **GMC** (predecessor): Has separate entries — `GMC/Superiors` and `GMC_V2.0/Superiors`

### SIDId NFO Metadata

From `sidid.nfo`:

| Entry | Full Name | Author | Year | CSDb |
|-------|-----------|--------|------|------|
| DMC | Demo Music Creator System | Balazs Farkas (Brian) | 1991 | [#2598](https://csdb.dk/release/?id=2598) |
| DMC_V4.x | Demo Music Creator System | Balazs Farkas (Brian) | 1991 | [#2596](https://csdb.dk/release/?id=2596) |
| DMC_V5.x | Demo Music Creator System | Balazs Farkas (Brian) | 1993 | [#2594](https://csdb.dk/release/?id=2594) |
| DMC_V6.x | Demo Music Creator System | Balazs Farkas (Brian) | — | — |
| GMC/Superiors | Game Music Creator System | Balazs Farkas (Brian) | 1990 | [#7268](https://csdb.dk/release/?id=7268) |
| GMC_V2.0/Superiors | Game Music Creator System | Balazs Farkas (Brian) | — | — |

### WilfredC64/player-id

[player-id](https://github.com/WilfredC64/player-id) is a modern alternative to SIDId, also by Wilfred/HVSC. It uses the same `sidid.cfg` format and signature database. Its `config/` directory contains:
- `sidid.cfg` — Same signatures as cadaver/sidid (identical DMC entries)
- `sidid.nfo` — Same metadata
- `tedid.cfg` — TED chip signatures (not relevant)

No additional DMC-specific signatures beyond what cadaver/sidid provides.

## 3. libsidplayfp

### Source: [libsidplayfp/libsidplayfp](https://github.com/libsidplayfp/libsidplayfp)

libsidplayfp is a cycle-accurate C64 emulation library for SID playback. It does NOT contain any DMC-specific handling:

- **No player-aware code**: libsidplayfp emulates the C64 CPU + SID chip. It runs the 6502 player code natively — it doesn't know or care what player engine is running.
- **No format parsing**: It reads PSID/RSID headers to set up load address, init address, and play address, then lets the 6502 code do everything.
- **Player identification**: Done externally via SIDId (uses `sidid.cfg` in the DOCUMENTS folder). libsidplayfp itself has no identification logic.
- **Song lengths**: Read from `Songlengths.md5` (HVSC database), not derived from player analysis.

The `psiddrv.cpp` module implements the PSID driver — a small 6502 stub that calls init and play at the correct addresses. This is generic for all players, not DMC-specific.

### Relevant for our pipeline

libsidplayfp's value for DMC work is as the emulation backend for `siddump` (our register dump tool). We use it to capture the ground-truth SID register writes from original DMC SIDs. No source changes needed for DMC support.

## 4. Cadaver's Music Player Technical Rant

Source: [cadaver.github.io/rants/music.html](https://cadaver.github.io/rants/music.html)

Lasse Oorni (Cadaver, author of GoatTracker and SIDId) describes C64 music player architecture in general. Key points relevant to DMC:

### Frame-Based Execution
- Music routines execute once per frame (50Hz PAL) during raster interrupt
- Standard flow: process voice 1, voice 2, voice 3, then non-voice-specific (filter)

### Ghost Registers
- SID registers are write-only, so players maintain shadow copies in RAM
- At end of frame processing, all shadow values are written to SID chip
- DMC follows this pattern: it builds register values in RAM, then writes to $D400-$D418

### Hard Restart — Testbit Method (used by DMC and JCH)
1. 2+ frames before note: set ADSR to preset ($0000, $0F00, or $F800), clear gate bit
2. First note frame: write AD and SR, then write $09 to waveform register (test bit + gate)
3. Second note frame: load actual waveform from wave table

**Critical register write order:** AD/SR always written BEFORE waveform. This is what makes hard restart work reliably.

### Pulse Width Modulation
- Parameters: initial value, modulation speed (per frame), high/low limits
- DMC uses 3 speed bytes per instrument (PW1-PW3) for complex pulse cycling
- Limit byte prevents wraparound artifacts

## 5. CSDb Release Information

### DMC 4.0 — [CSDb #2596](https://csdb.dk/release/?id=2596)
- Released: September 1991
- Author: Brian/Graffity
- Type: Music editor (C64 tool)
- Downloads: 1,544

### DMC V5.0 — [CSDb #2594](https://csdb.dk/release/?id=2594)
- Released: 1993
- Author: Brian/Graffity + The Imperium Arts
- Described as "the most popular music-editor on the C64"
- "Very powerful, but hard to use"
- "Requires good knowledge of the I/O between the SID and C64"

### DMC V5.0+ — [CSDb #22938](https://csdb.dk/release/?id=22938)
- Released: 26 December 2002
- Author: CreaMD/DMAgic (tweaked version of V5.0)
- Added: extended sector editing, track-play, audible editing, adjustable fast-forward
- Speed depends on tune 7 setting

### DMC V5.1+ Package — [CSDb #2600](https://csdb.dk/release/?id=2600)
- Released: 1994
- Authors: Graffity + Motiv 8

### DMC 7.0 — [CSDb #2629](https://csdb.dk/release/?id=2629)
- Released: 1995
- Author: Axl+Ray/Unreal
- Based on V4 code (NOT V5 lineage)
- Added ~50% more code than V4: multi-song (1-5), multi-channel, turbotape support
- Editor enhancements: playable from any position, sector length visibility
- Version numbering disputed — some consider it an unauthorized V4 mod

## 6. HVMEC (HVSC Music Editor Collection)

Source: [hvmec.altervista.org](https://hvmec.altervista.org/blog/)

HVMEC catalogs C64 music editors with downloads and keyboard documentation. DMC versions cataloged:

| Version | HVMEC Page | Key Info |
|---------|-----------|----------|
| V2.1+ [4x] | [p=504](https://hvmec.altervista.org/blog/?p=504) | 4x speed variant |
| V4.0 [2x] | [p=541](https://hvmec.altervista.org/blog/?p=541) | 2x speed by Moog/Keen Acid |
| V4.0 pro | [p=570](https://hvmec.altervista.org/blog/?p=570) | Enhanced by Onslaught |
| V4.3++ | [p=630](https://hvmec.altervista.org/blog/?p=630) | Enhanced by Stryyker/Tide |
| V5.0 | [p=700](https://hvmec.altervista.org/blog/?p=700) | Standard V5 by Brian/Graffity |
| V5.0+ | [p=757](https://hvmec.altervista.org/blog/?p=757) | CreaMD audible editing |
| V5.4 | [p=973](https://hvmec.altervista.org/blog/?p=973) | Glover/Samar, improved HR |

HVMEC pages contain keyboard controls and download links but NO byte-level format documentation.

Available downloads from HVMEC for V5.0:
- `DMC_V5.prg` (C64 program image)
- `dmc_5_docs.txt` (documentation)
- `DMC V5.0 Packer by Motiv 8` (external packer)
- `DMC_V5_Depacker.prg`

## 7. Key Technical Insights for Pipeline Development

### Version Detection Strategy

Since SIDId lumps V4/V5/V7 under generic "DMC", our parser needs its own detection:

1. **V5 detection** (already in dmc_parser.py): Look for `BC ?? ?? B9 ?? ?? C9 90` (LDY abs,X; LDA abs,Y; CMP #$90)
2. **V4/V7 detection**: Default when V5 signature not found
3. **V6 detection**: Look for `A9 08 8D 04 D4 8D 0B D4 8D 12 D4` (init writing $08 to all control regs)
4. **V4 vs V7**: V7 has multi-song support (1-5 songs) and larger binary size (~3000 bytes code). Could detect via binary size or presence of additional JMP entries.

### Instrument Size Difference

- V4/V7: 11 bytes per instrument (at freq_hi + $0248)
- V5: 8 bytes per instrument (location found dynamically)

This is the most critical format difference. The 3 missing bytes in V5 are likely the PW1-PW3 pulse width bytes being consolidated.

### Wave Table Difference

- V4/V7: 1 byte per wave table entry (waveform/control byte)
- V5: 2 bytes per wave table entry (waveform + note data in paired columns)

### Duration-Based Timing

DMC uses duration-based patterns (NOT tick-based like GoatTracker). Sectors can be any length with no forced sync between voices. This is a fundamental design difference that affects USF conversion — our USF patterns assume equal-length synchronized patterns.

### Packed vs Unpacked

DMC V4/V7 have built-in packers that relocate to $1000. Most HVSC DMC SIDs are packed. The init routine at $1000 unpacks, then the player runs. V5 uses an external packer (Motiv 8's `SYS $2E00`).

## Sources

### HVSC
- HVSC DOCUMENTS directory: `/data/C64Music/DOCUMENTS/`
- STIL.txt, Musicians.txt, Update_Announcements/

### SIDId
- [cadaver/sidid](https://github.com/cadaver/sidid) — Source code and signatures
- [cadaver/sidid/sidid.c](https://github.com/cadaver/sidid/blob/master/sidid.c) — Matching algorithm
- [cadaver/sidid/sidid.cfg](https://github.com/cadaver/sidid/blob/master/sidid.cfg) — Signature database
- [cadaver/sidid/sidid.nfo](https://github.com/cadaver/sidid/blob/master/sidid.nfo) — Player metadata

### player-id
- [WilfredC64/player-id](https://github.com/WilfredC64/player-id) — Modern SIDId alternative
- [config/sidid.cfg](https://github.com/WilfredC64/player-id/tree/master/config) — Same signature database

### libsidplayfp
- [libsidplayfp/libsidplayfp](https://github.com/libsidplayfp/libsidplayfp) — C64 emulation library
- [libsidplayfp/sidplayfp](https://github.com/libsidplayfp/sidplayfp) — Console player

### Technical References
- [Cadaver's music player rant](https://cadaver.github.io/rants/music.html) — Player architecture
- [Chordian C64 editors comparison](https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/)

### CSDb Releases
- [DMC 4.0 — CSDb #2596](https://csdb.dk/release/?id=2596)
- [DMC V5.0 — CSDb #2594](https://csdb.dk/release/?id=2594)
- [DMC V5.1+ — CSDb #2600](https://csdb.dk/release/?id=2600)
- [DMC V5.0+ — CSDb #22938](https://csdb.dk/release/?id=22938)
- [DMC 7.0 — CSDb #2629](https://csdb.dk/release/?id=2629)
- [DMC Relocator — CSDb #10758](https://csdb.dk/release/?id=10758)

### HVMEC
- [HVMEC DMC V5.0](https://hvmec.altervista.org/blog/?p=700)
- [HVMEC DMC V4.0 pro](https://hvmec.altervista.org/blog/?p=570)
- [HVMEC DMC V4.3++](https://hvmec.altervista.org/blog/?p=630)
- [HVMEC DMC V4.0 2x](https://hvmec.altervista.org/blog/?p=541)

### Zimmers.net Archive
- [C64 audio editors](https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html) — DMC binary downloads (no docs)

### Community
- [Lemon64 DMC V4 thread](https://www.lemon64.com/forum/viewtopic.php?p=1056030)
- [Lemon64 DMC 4 Instructions thread](https://www.lemon64.com/forum/viewtopic.php?t=80234)
- [TND64 Music Scene tutorial](http://www.tnd64.unikat.sk/music_scene.html)
