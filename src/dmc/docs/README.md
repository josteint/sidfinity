# DMC Research — Summary and Gap Analysis

Collected 2026-04-11 across 3 research waves (6 broad + 12 lead-following + 6 third-order).
24 documents, ~8,000 lines of technical research.

## What We Now Know

### V4 Format (10,738 HVSC SIDs — our primary target)
- **Instruments**: 11 bytes x 32 max (AD, SR, wave_ptr, PW1, PW2, PW3, PW-L, Vib1, Vib2, Filter, FX)
- **FX byte flags** (all 8 bits confirmed, source: TND64 tutorial):
  - Bit 0: DRUM EFFECT (pitch ignored in sector, wave table pitch steps in higher range)
  - Bit 1: NO FILT RES (no filter reset on new notes)
  - Bit 2: NO PULS RES (no pulse reset on new notes / "sweep-reset disable")
  - Bit 3: NO GATE FX (hold note until explicit GATE)
  - Bit 4: HOLDING FX (note never released)
  - Bit 5: FILTER FX (activate filter)
  - Bit 6: DUAL EFFECT (wave table at half speed)
  - Bit 7: CYMBAL FX (short noise burst before sound)
- **Wave table**: 2 bytes/row (waveform + note offset). Confirmed 2-column by Cadaver. Loop via >= $90 byte.
- **Pulse table**: part of instrument (PW1/PW2/PW3 + PW-L limit)
- **Filter table**: 6-step envelope (S1-S6/X1-X6 parameters, R=resonance, T=type)
- **Sectors**: 64 max, up to 250 rows. Duration-based (not tick-synced). Channels maintain independent timing.
- **Sector encoding**: $00-$5F notes, $60-$7C duration, $7D continuation, $7E gate off, $7F end, $80-$9F instrument, $A0-$BF glide
- **Sector commands** (from TND64): DUR, SND, GLD, VOL, SWITCH, GATE, END
- **Track commands**: sector refs ($00-$3F), TR+/TR- transpose ($80-$8F/$A0-$AF), END ($FE), loop ($FF)
- **No per-pattern filter command** — filter changes require separate instruments
- **Freq table is user-replaceable** — "CGKOTY" tables play quarter-tone lower than standard "AEINRW" (confirmed by Brian)
- **Hard restart**: testbit method ($09 to waveform, PAL-only). 3-frame sequence: clear gate + ADSR preset, then $09, then actual waveform.
- **CIA1 Timer A: $4CF8 (19,704 cycles)** for standard 50Hz. Config at $0241 → zero-page $37/$38 → CIA1 $DC04/$DC05.
- **Loop code at $0FF9** (confirmed by HVSC update notes)
- **IRQ handler at $088C** in editor binary (entry via $080D BASIC stub)
- **8 sub-tunes per file**, 3 channels
- **Multispeed from DMC3 onward** (3x, 4x, 5x, 8x)
- **Player writes all 3 SID channels every frame**, even when idle

### V2/V3 Format
- **"Practically the same program" as V4** (Brian's own words). Our V4 parser should handle V2/V3 with minimal changes.

### V5 Format (separate branch from V4)
- **Instruments**: 8 bytes (ADSR + vibrato 3 bytes + wave/pulse/filter table pointers). Missing vs V4: PW1/PW2/PW3 moved to separate pulse table.
- **Wave table**: 2 bytes/row (waveform+gating, relative notes + hi-freq mode). Hi-freq mode bit replaces the test-bit. Loop only (no stop).
- **Pulse table**: 2 bytes/row (12-bit PW, 16-bit speed). Loop only.
- **Filter table**: 2 bytes/row (11-bit cutoff, 16-bit speed). **Channel 3 only.** Loop only. Type/resonance set via command, not in table.
- **96 sectors** (vs V4's 64). Sector end = $FF (vs V4's $7F).
- **Hard restart: hard-coded**, no per-instrument control
- **Two glide commands**: GLD (glide to destination) + portamento (glide from current)
- **No command table** (no pattern-level programmable commands)
- **$C0-$DF extended commands** (filter/ADSR/volume — details need disassembly)
- **V5.4 packer is unreliable** — HVSC SIDs may use mismatched editor/packer versions
- **Target: 18 raster lines** (~1134 cycles). Borrowed SID shutoff + datalogging from Sosperec.
- **Iceball's multi-speed variant** runs instruments faster than notes (DMC's CIA timer equivalent)

### V7 Format (V4 fork by Unreal, NOT V5-based)
- V7.0A and V7.0B are distinct sub-variants (DMC 4 Editor distinguishes them for import)
- V7.1 adds **filter commands** and **direct AD/SR set** in sector data — new command bytes
- Same core format as V4. Added multi-song, sector length display, turbotape.

### V6 Format (never publicly released by Brian, 16 HVSC SIDs)
- Max 8 raster lines (~504 cycles) via **per-song dead-code elimination** at pack/compile time
- Each packed V6 SID has a **different player binary** — can't assume single layout
- Editor written by **The Syndrom**, not Brian
- **Instrument fields**: AD, SR, WV (wave table pointer), P1/P2 (pulse), V1 (vibrato), F1/F2/F3 (filter)
- **Three dedicated tracks**: vibrato, filter, drum
- `dmc6-docs.txt` on CSDb is actually a packed D64, not extractable without VICE

### Version Lineage (confirmed by Brian)
```
GMC V1.0 (1990) → V1.6 → DMC V1.2 → V2.0 → V3.0 → V4.0 (1991, most popular)
    "Game Music Creator"    "Demo Music Creator"      ├→ V4 Pro variants (Morbid)
    Name changed at V3.0, continuous version numbering ├→ V4.G (Glover/Samar)
                                                       ├→ V4.1A (Lyon)
                                                       ├→ V4.2 (Sonic Screams)
                                                       ├→ V4.3 Double SID (Rayden, 2nd SID at $D500)
                                                       ├→ V4.3++ (Stryyker/Tide)
                                                       ├→ DMC 4 25Hz (MultiStyle Labs, frame-skip wrapper)
                                                       └→ V7.0 (Unreal, V4 fork)
                                                            ├→ V7.0A, V7.0B (sub-variants)
                                                            └→ V7.1 (filter/ADSR cmds)
                                                V3.0 → V5.0 (1993, major rethink)
                                                          ├→ V5.0+ (CreaMD, audible editing)
                                                          ├→ V5.01B (Zeux, bugfix)
                                                          ├→ V5.1x/y (Morbid+Iceball, multi-speed)
                                                          └→ V5.4 (Glover/Samar, better HR, buggy packer)
                                                V?.? → V6.0 (Syndrom editor, per-song compiled player)
```

### Key People
- **Brian (Balazs Farkas)** — original author of all official DMC versions. Tehernaplo interview confirms design philosophy and version relationships.
- **The Syndrom** — wrote V6 editor, V4 Relocator V2.0, V5.1y docs. Deepest internals knowledge after Brian.
- **Logan** — DMC 4 Editor 2025 (closed source, imports V4/V7.0A/V7.0B)
- **Morbid** — Pro variants of V4 and V5 (semi-official, Brian co-credited)
- **Glover/Samar** — V4.G and V5.4 modifications
- **Iceball** — multi-speed V5 variant (instruments faster than notes)

### JCH NP20 (DMC's direct successor) — Fully Documented
SIDFactory II converter provides complete format spec: pointer tables at fixed offsets ($0FBA-$0FD0),
2-byte orderlists (transpose + seq_index), 2-byte sequences (command/instrument + note), 
instrument/command tables (row-major), wave/pulse/filter tables (column-major), tempo handling
(speed >= 2 simple, speed < 2 = multispeed/CIA). Architecture maps closely to DMC.

### Sosperec's Datalogging Technique (adopted by DMC5)
Shut down SID → run music player for one frame → read all SID registers back → re-enable SID → 
write captured values. Same approach as modern `siddump --writelog`. Confirmed by Brian as the 
technique he borrowed for DMC5's efficiency improvements.

## Remaining Gaps

### Fillable from our own binaries (disassembly phase)
These require disassembling DMC player binaries we already have:
1. **Exact pulse width cycling algorithm** — PW1/PW2/PW3 byte interaction with PW-L limit
2. **Vibrato implementation** — Vib1/Vib2 byte meaning and per-frame register effect
3. **Filter 6-step envelope** — S1-S6/X1-X6 parameter interpretation and per-frame cutoff update
4. **Drum/cymbal synthesis** — exact waveform sequence and timing for DRUM EFFECT and CYMBAL FX
5. **$C0-$DF extended commands** (V5/V7.1) — what each byte does
6. **V5 8-byte instrument layout** — exact field mapping (we know ADSR + vib*3 + table ptrs, but not byte order)
7. **V6 per-song compiled player** — each SID has different player binary (dead-code eliminated)
8. **V7.0A vs V7.0B differences** — what changed between sub-variants
9. **Glide implementation** — per-frame frequency stepping algorithm
10. **Multi-speed mechanism** — CIA timer configuration details beyond the $4CF8 base value

### Best binaries to disassemble
- `dmc4.0.prg` from zimmers.net (12,357 bytes, unpacked, BASIC stub at $080D, IRQ at $088C)
- `MUSICIANS/T/The_Syndrom/DMC_V6_note.sid` from HVSC (V6)
- Any HVSC DMC V5 SID (pick via sidid detection)
- DMC Relocator binaries from CSDb (3 versions — reveal complete memory layout by showing which addresses get patched)

### Online knowledge is exhausted
All high-value online sources have been searched across 3 waves:
- No original source code exists for any DMC version (confirmed)
- No public annotated disassembly exists (confirmed)
- No other open-source DMC parser exists — our `dmc_parser.py` is the most complete (confirmed)
- D64 disk images contain demo scrollers, not text documentation (confirmed by extraction)
- `dmc6-docs.txt` on CSDb is a packed D64, not a text file (confirmed)

## Source Documents (24 files)

### Wave 1: Broad sweep
| File | Source | Key Content |
|------|--------|-------------|
| `csdb_research.md` | CSDb | 30+ releases, version history, variant catalog |
| `archive_research.md` | Archive.org | Authorship correction (Brian/Graffity), FX flags, wave table format |
| `forums_research.md` | Forums/Usenet | V5 format differences, hard restart, V6 details |
| `hvsc_sidid_research.md` | HVSC/SIDId | 4 signature patterns, V4/V5/V6 detection logic |
| `sidfactory_and_tools_source.md` | GitHub | JCH NP20 converter source (closest reference), no DMC parsers exist |
| `disassembly_research.md` | Various | No public disassembly exists, tool survey |

### Wave 2: Lead following
| File | Source | Key Content |
|------|--------|-------------|
| `lead_tutorials_and_docs.md` | TND64/Cadaver | **Complete FX byte flags (all 8 bits)**, wave table = 2-column confirmed, sector/track commands |
| `lead_chordian_comparison.md` | Chordian | **V5 format: 8-byte instruments, 2-byte tables, 96 sectors, channel 3 filter only** |
| `lead_v5_v6_docs.md` | CSDb/HVMEC | V6 docs exist (packed D64), V5 multi-speed (Iceball), V5.4 buggy packer |
| `lead_variants_and_people.md` | CSDb | **3 relocator binaries**, Brian interview found, CGKOTY freq tables, V7.1 filter/ADSR cmds |
| `lead_predecessors_and_jch.md` | CSDb/GitHub | GMC→DMC lineage confirmed, **JCH NP20 converter deep analysis** |
| `lead_tools_and_disassembly.md` | Various | Triad player pseudo-code (generic SID player algorithm), SIDdecompiler for cross-validation |
| `lead_hvsc_local_docs.md` | Local HVSC | Loop code $0FF9, no filter cmd in V4, multispeed from V3, **best SIDs to disassemble** |
| `lead_zimmers_binaries.md` | Zimmers.net | **Unpacked dmc4.0.prg** (12,357 bytes, clean entry point) |
| `lead_dmc4_editor_2025.md` | CSDb | **V7.0A vs V7.0B** distinction, V4 tables = 2 bytes/row, YouTube demo exists |
| `lead_pro_variants_batch.md` | CSDb | Two Pro lineages (Morbid semi-official, Xlcus independent), Double SID at $D500 |
| `lead_csdb_sound_design.md` | CSDb forum | Sweep-reset disable = NO PULS RES flag confirmed |
| `lead_academic_paper.md` | Academic | General SID architecture (no DMC-specific content) |

### Wave 3: Third-order leads
| File | Source | Key Content |
|------|--------|-------------|
| `lead_brian_interview.md` | Tehernaplo/Wayback | **Brian's own words**: V2/3/4 same program, V5 major rethink, V6 per-song compiled, CGKOTY tuning |
| `lead_dmc4_25hz.md` | CSDb | **CIA Timer A = $4CF8**, config path $0241→$37/$38→$DC04/$DC05, 25Hz = frame-skip wrapper |
| `lead_d64_extracted.md` | D64 extraction | All D64 "docs" are demo scrollers, not text. dmc6-docs.txt = packed D64. Dead end. |
| `lead_sid_preservation.md` | SID Preservation | Editor architecture overview, .SND/.DUR/.GLD commands (cross-validates TND64) |
| `lead_demozoo_productions.md` | Demozoo | 120+ productions, **V6 instrument fields** (AD,SR,WV,P1/P2,V1,F1/F2/F3), DMC 4 25Hz variant |
| `lead_youtube_demos.md` | YouTube/web | (pending) |
