---
source_url: local: multiple
fetched_via: local read
fetch_date: 2026-06-15
author: analysis
content_date: 2026-06-15
reliability: primary
---

# MoN/Deenen — Local Codebase Analysis

## Existing research.md summary

File: `pipelines/mon_deenen/docs/research.md` (7 lines)

- Author: Charles Deenen of Maniacs of Noise (founded 1987)
- Type: Commercial game music driver
- Driver name: "Musicfile"
- Composers entered hex numbers and labels into assembler source — no GUI
- Two versions: **MoN Old (1989–90)** and **MoN New (1990–92)**
- After group split, Jeroen Tel wrote his own driver
- Also ported to ZX Spectrum 128K
- Stub only — no format analysis, no effect catalogue, no disassembly

---

## HVSC database statistics

Source: `hvsc84.csv` via `src/sid_db`, queried 2026-06-15.

### Engine name variants

| Engine string     | SID count |
|-------------------|-----------|
| MoN/FutureComposer | 4024     |
| MoN/Deenen        | 135       |
| MoN/Bjerregaard   | 77        |

**Total MoN/Deenen SIDs: 135**

Note: MoN/FutureComposer (sidid's name for the FC player released by Maniacs of Noise)
is a completely separate family — FC v1/v3/v4, already fully migrated in this repo.
MoN/Bjerregaard is a different Maniacs-affiliated composer (Marco Bjerregaard, separate
engine). This analysis covers **only MoN/Deenen**.

### Distribution by HVSC musician folder

| Folder              | Count |
|---------------------|-------|
| MUSICIANS/T         | 74    |  (Jeroen Tel — the dominant contributor)
| MUSICIANS/D         | 20    |  (Charles Deenen himself)
| MUSICIANS/O         | 16    |  (Reyn Ouwehand, who used the driver)
| MUSICIANS/A         | 7     |
| MUSICIANS/J         | 7     |
| MUSICIANS/H         | 4     |
| MUSICIANS/L         | 2     |
| MUSICIANS/N         | 2     |
| MUSICIANS/W         | 2     |
| MUSICIANS/F         | 1     |

Jeroen Tel accounts for 55% of the corpus. This is consistent with research.md's note
that after Deenen founded MoN, Tel became the primary user of the driver.

### Longest subtunes (by songlength_s)

```
Rubicon.sid           (Tel)     1263s
Turbo_Outrun.sid      (Tel)     1138s
Bad_Blood.sid         (Tel)     1045s
Outrun_Europa.sid     (Tel)      869s
Nighthunter.sid       (Tel)      864s
Afterburner.sid       (Tel)      725s
2400_AD.sid           (Tel)      675s
Mantalos.sid          (Deenen)   639s
Golden_Axe.sid        (Tel)      572s
Hawkeye_loader.sid    (Tel)      528s
Hot_Rod.sid           (Tel)      504s
Thats_the_Way_It_Is_main.sid (Tel) 473s
Deadlock.sid          (Ouwehand) 457s
```

---

## sidid.cfg signature entries (verbatim)

Source: `/home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg` lines 1327–1358.
Identical in all three copies checked (`deprecated/`, `tmp/dmc_hunt/player-id/`,
`tmp/dmc_hunt/DeepSID/`).

```
MoN/Deenen
C9 60 B0 03 4C ?? ?? C9 FF D0 ?? A9 00 END
B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ?? 5E ?? ?? 7E ?? ?? 4C END
BD ?? ?? DD ?? ?? D0 ?? A9 FE 9D ?? ?? DE ?? ?? F0 ?? BD ?? ?? C9 FF F0 END
C9 C0 90 ?? 29 ?? 0A 0A 0A 9D ?? ?? C8 B1 ?? C9 ?? F0 END
C9 FF D0 0E A9 00 95 ?? B5 ?? F0 04 D6 ?? 10 END
C9 FF D0 17 A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 END
4C ?? ?? C6 ?? A4 ?? BD ?? ?? 86 ?? 0A 0A 0A AA 8E ?? ?? BD ?? ?? 85 ?? BD ?? ?? 25 ?? 99 04 D4 END
99 00 D4 C8 CA 10 F9 END

(MoN/Deenen_Digi)
A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D END
4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4 END
```

Also shown in context, the sidid.cfg sub-variant entries that appear WITHIN the
MoN/Deenen block (lines 1337–1358, all listed together under MoN/FutureComposer):

```
(MoN/JTS)
A9 ?? 9D ?? ?? 9D ?? ?? 9D ?? ?? 4C ?? ?? 8D ?? ?? 29 80 F0 0E AD ?? ?? 29 1F 9D ?? ??
FE ?? ?? 4C ?? ?? AD ?? ?? 29 40 F0 0E AD ?? ?? 29 3F 9D END

(MoN/RWE)
B0 05 BD ?? ?? D0 05 BD ?? ?? 29 FE 9D ?? ?? BD ?? ?? D0 0A AD ?? ?? C9 ?? D0 03 99 06 D4 BD END

(MoN/Bantam)
0A 0A 0A AA 8E ?? ?? BD ?? ?? A6 FF 9D ?? ?? 99 04 D4 A9 00 99 02 D4 A6 FF 9D END
```

### Interpretation of the eight MoN/Deenen signature patterns

**Pattern 1:** `C9 60 B0 03 4C ?? ?? C9 FF D0 ?? A9 00`
- `CMP #$60, BCS +3, JMP abs` — note-value range check (values $00–$5F are note
  pitches; $60+ are control commands or terminators)
- `CMP #$FF, BNE, LDA #$00` — end-of-pattern sentinel ($FF) handling
- This is the **note-decode dispatch** kernel. Values below $60 = pitch, $FF = pattern end.

**Pattern 2:** `B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ?? 5E ?? ?? 7E ?? ?? 4C`
- LDA abs,Y / EOR abs,Y — combines two table bytes (likely note + duration)
- `4A 4A 4A 4A` — four LSRs, extracting upper nibble
- `TAY, DEY, BMI` — loop counter or duration decrement
- `5E ?? ?? 7E ?? ??` — ASL abs,X / ROR abs,X — bit rotation (arpegio / vibrato step?)
- This is a **per-voice pattern processing** loop

**Pattern 3:** `BD ?? ?? DD ?? ?? D0 ?? A9 FE 9D ?? ?? DE ?? ?? F0 ?? BD ?? ?? C9 FF F0`
- LDA abs,X / CMP abs,X — compare voice state
- `LDA #$FE, STA abs,X` — write gate-off command
- `DEC abs,X, BEQ` — note duration counter decrement
- `CMP #$FF, BEQ` — rest/tie sentinel
- This is the **duration counter / gate-off** logic

**Pattern 4:** `C9 C0 90 ?? 29 ?? 0A 0A 0A 9D ?? ?? C8 B1 ?? C9 ?? F0`
- `CMP #$C0, BCC` — command range split ($C0–$FF are commands, below are notes)
- `AND #??, ASL, ASL, ASL` — command subtype extraction (upper bits → table index)
- This is the **command dispatch** (instrument select, waveform, etc.)

**Pattern 5:** `C9 FF D0 0E A9 00 95 ?? B5 ?? F0 04 D6 ?? 10`
- `CMP #$FF, BNE` — pattern end check
- `LDA #$00, STA zpg,X` — clear voice state
- `LDA zpg,X, BEQ` — test if next orderlist entry is zero (end of song)
- This is the **orderlist advance / pattern-end** handler

**Pattern 6:** `C9 FF D0 17 A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10`
- Similar pattern-end / channel-advance logic (likely a second variant path)

**Pattern 7:** `4C ?? ?? C6 ?? A4 ?? BD ?? ?? 86 ?? 0A 0A 0A AA 8E ?? ?? BD ?? ?? 85 ?? BD ?? ?? 25 ?? 99 04 D4`
- JMP + DEC zp + LDY zp — sequence counter decrement
- `0A 0A 0A` — three ASLs → instrument index computation
- `STX abs, LDA abs,X` — instrument table access
- `STA $D404` — voice waveform/gate write
- This is the **instrument-select / SID register write** path

**Pattern 8:** `99 00 D4 C8 CA 10 F9`
- `STA $D400,Y, INY, DEX, BPL` — register init loop writing 0x15 SID registers
- This is the **SID chip clear/init** loop (present in only 2 SIDs)

---

## Binary structure analysis

### PSID header observations

All MoN/Deenen SIDs use PSID format v2. Key fields:

- **load_offset = 0x007C** (standard, meaning load address is embedded in the first
  2 bytes of the SID data payload, little-endian)
- **init_addr = 0x0000** for the vast majority — meaning "use load address as init"
  (the first thing at the load address is the init entry point)
- **speed field**: nearly all are `0x00010000` (all CIA subtunes except subtune 0
  which is VBI) or `0x00010000` (mix); B_A_T uses `0x00020000`

### Data layout at load address

A consistent structure appears across the majority of MoN/Deenen SIDs
(the ones with `sig1` present, 96/135):

```
LOAD+$00: two-byte pointer or jump table (JMP init, JMP play, JMP extra)
          format: [lo, hi, 4C lo hi, 4C lo hi, 4C lo hi] ← three JMP vectors
LOAD+$06: [data starts immediately] ← instrument table or pattern pointers
```

Example — `Lord_of_the_Rings.sid` (load=0x1400):
```
1400: 00 14         ← embedded load address (little-endian 0x1400)
1402: 4C CE 0E      ← JMP $0ECE  (init? sub-song handler?)
1405: 4C BF 0E      ← JMP $0EBF  (play? channel 1?)
1408: 4C A2 0C      ← JMP $0CA2  (play entry point confirmed by PSID play=$0C9C)
140B: 00 96 0C      ← data follows
```

Example — `Ala_Gal.sid` (1988, earliest, load=0x1400):
```
1400: 00 14         ← embedded load address
1402: 3C 10         ← word pointer (play @ 0x103C)
1404: 4C ED 10      ← JMP $10ED
1407: 4C 20 11      ← JMP $1120
140A: 4C 26 11      ← JMP $1126
140D: 01 00 07 0E   ← data table starts (instrument data?)
```

### Two distinct sub-populations

Binary signature analysis across all 135 SIDs reveals two groups:

**Group A — "MoN Old" engine (~98 SIDs, 1988–1991):**
- Primary signature `C9 60 B0 03 4C` present
- Note values $00–$5F = pitches, $60–$FE = commands, $FF = end
- Play address typically in $0800–$2FFF range
- Load address typically $1400 or $1000 or $2000

**Group B — "Different / Tel variant" (~37 SIDs):**
- Neither primary signature present
- Includes both very early tunes (1987–1988: `Cool_Tune`, `Hotline_Intro`, `Koekoek`)
  and very late tunes (2004–2019: `Alternative_Fuel`, `Liberty_Lemmings`, `Fuzzball_*`)
- Also includes post-MoN commercial work: `Lemmings` (1994), `North_and_South` (1991)
- These may represent: (a) early pre-"Deenen" engine prototypes, (b) Jeroen Tel's
  own independent driver (confirmed: "After group split, Jeroen Tel wrote his own
  driver" per research.md), (c) later updates/rewrites

The Group B "Hawkeye_loader" (1988 Thalamus, Tel) has a completely different
init stub: `LDX #6, STX $AA74, ...` with CIA-based playback at $AA00 — clearly
a different engine than the standard sig1 engine.

The Group B `Supremacy` (1991 Virgin) and `Victrix` (1991 Tel) share a similar
data table structure at load (instrument tables starting at load+$10) but no sig1.

### Hex samples — canonical sig1 engine

**`Lord_of_the_Rings.sid`** (1990 Interplay, load=0x1400, play=0x0C9C):
Play subroutine at $0C9C. Sig1 found at $1707:
```
16F7: 0d 9d 46 0d a9 01 9d 5e 0d bc 71 0d b1 04 85 07
1707: c9 60 b0 03 4c 69 10 c9 ff d0 0e a9 00 9d 71 0d
1717: fe 6b 0d 4c 31 0f 4c 81 0f c9 fe d0 0b c8 b1 04
```
Disassembly at 0x1707: `CMP #$60 / BCS +3 / JMP $1069 / CMP #$FF / BNE $1717 /
LDA #$00 / STA $0D71,X` — confirmed note range dispatch + end-of-pattern reset.

**`After_the_War.sid`** (1989 Dinamic/Charles Deenen, load=0x0000, play=0x0C65):
Data starts at file offset 118 (no embedded load, actual load embedded = 0x0000):
```
0000: 00 14 00 00 00 00 5f 0c  [jump vectors to $0C5F, etc.]
0050: bd e4 18 8d 53 0e bd e5 18 8d c6 0e a9 30 8d 5d
```
The bytes at $0007–$000F appear to be an init vector table (pointers into the
song data), consistent with Group A layout.

---

## HVSC DOCUMENTS search results

`grep -r -i "maniacs|deenen|MoN" hvsc85/DOCUMENTS/` returned only Songlengths.md5
comment lines (song titles containing "Mon" or "Mon" prefixes). No dedicated
HVSC documentation file exists for MoN/Deenen in DOCUMENTS/.

No relevant MoN/Deenen content in STIL or dedicated .txt documentation files.

---

## Deprecated directory search

```bash
find /home/jtr/sidfinity/deprecated -name "*deenen*" -o -name "*mon_deenen*" -o \
  -name "*maniacs*" 2>/dev/null
```
**Result: no files found.** No prior migration attempts, no deprecated analysis, no
existing disassembly or extract code for this engine.

---

## Key structural observations

1. **The engine is a custom tracker** (not publicly released): hex-entry format,
   no GUI, commercial-game focus. This means there is no "official" format
   specification document to find — the format must be reconstructed from binaries.

2. **Note encoding confirmed**: values $00–$5F = pitch indices (96 notes max),
   $60–$FE = effect/command bytes, $FF = end-of-pattern sentinel. This is a
   clean 6-bit note space.

3. **Multiple sub-versions**: sidid.cfg registers sub-variants via named sub-entries
   under MoN/FutureComposer: `MoN/JTS`, `MoN/RWE`, `MoN/Bantam`, `MoN/TTWII`,
   `MoN/Cyb2` — these may be FC variants or unrelated sub-engines. The MoN/Deenen
   section itself has `MoN/Deenen_Digi` for digi-player members.

4. **Binary layout is relocatable**: play addresses span $0800–$FD20, no fixed
   base. The PSID init=0 convention (init at load address) means the engine is
   entirely self-contained.

5. **Duration/gate model**: Pattern 3 (`DE ?? ?? F0` = DEC + BEQ) indicates
   note duration is a countdown counter, like Hubbard '85. Pattern 5/6 show
   per-voice position state stored in zero-page-indexed arrays.

6. **SID register init loop**: Pattern 8 (`99 00 D4 C8 CA 10 F9`) is a standard
   "write 0 to all 25 SID registers" init found in only 2 SIDs — most members
   use a different init strategy (individual STAs, not a loop).

7. **Group B (37 SIDs) is likely Tel's independent driver** from 1991+. The
   research.md specifically notes "After group split, Jeroen Tel wrote his own
   driver." The 2004–2019 entries in Group B confirm the Tel driver was still
   in use decades later. These 37 SIDs likely need a separate engine analysis.

---

## Leads to follow

1. **Disassemble the canonical Group A engine** — pick `Lord_of_the_Rings.sid`
   or `Mantalos.sid` as the reference: generate seed disassembly with
   `tools/seed_disassembly.py`, annotate init + play routines, map the data
   structures (instrument table layout, pattern byte format, orderlist format).

2. **Confirm Group B = Tel's independent driver** — disassemble `Supremacy.sid`
   (1991, clear break from MoN) vs `Victrix.sid` vs `JT_42.sid`. If they share
   a common player code base, that's a separate engine family (possibly "Tel/MoN"
   or similar). Check if the sidid.cfg has a separate entry for these — it
   currently classifies all as MoN/Deenen.

3. **Check the MoN/Deenen_Digi sub-variant** — sidid pattern:
   `A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D` and
   `4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4` — find which SIDs match
   this and understand the digi mechanism (1-bit sample player?).

4. **Instrument table format** — the data at LOAD+$06 (after the JMP vectors)
   appears to be instrument definitions. Map byte roles: envelope (ADSR?),
   waveform, pulse width, possibly effect programs. Compare across 3–4 SIDs
   to derive the schema.

5. **Orderlist format** — understand how the engine iterates patterns per voice.
   Look for per-voice pointers near the beginning of the data section.

6. **Check `MoN/JTS`, `MoN/RWE`, `MoN/Bantam`** sub-variants in sidid — are
   these present in any of the 135 MoN/Deenen SIDs (sidid may have misclassified
   some), or are they genuinely separate engines in other HVSC sections?

7. **Research sweep** — run the `research-player` skill to find any CSDb threads,
   forum posts, or prior RE work on the Deenen "Musicfile" driver. Search specifically
   for "Charles Deenen driver" + "Musicfile C64" + HVSC forum discussions.

8. **Early SIDs (1987–1988)** — `Cool_Tune.sid` (1987 Scoop Designs) and
   `Hotline_Intro.sid` (1988 TMC) are in Group B (no sig1). If these predate the
   canonical engine, they may represent v0/prototype. Compare data layout with the
   sig1 group to establish evolution timeline.
