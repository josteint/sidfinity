# Rob Hubbard Player — Research Documentation

## Collection Summary

52 files, 27,217 lines, 789KB. Gathered via 3 research waves (18 agents total: 6 Opus broad-sweep + 4 Opus lead-following + 8 Sonnet lead-chasing) across CSDb, GitHub, Archive.org/Wayback, Lemon64, chipmusic.org, codebase64, C=Hacking archive, Remix64, HVSC docs, VGMPF, C64Audio, G|A|M|E Journal, and disassembly sources.

**Total Hubbard ecosystem in HVSC:** ~220+ SIDs across all variants (82 Rob_Hubbard + 65 Bjerregaard + 31 Laxity + 21 Paradroid/Lameplayer + 7 Zicchi + ~15 Tjelta + others).

**Online knowledge ceiling reached.** All publicly accessible sources have been exhausted. Remaining gaps require reverse engineering from our own SID files or purchasing the "Master of Magic" book.

## What We Have

### Disassemblies (the core references)
| File | What |
|------|------|
| `chacking_hubbard_disassembly.txt` (51KB) | **THE definitive reference.** McSweeney's fully commented Monty on the Run disassembly from C=Hacking #5. |
| `hubbard_monty_disassembly_acme.asm` (32KB) | Monty in ACME assembler by dmx87. Reassemblable. |
| `hubbard_commando_disassembly.asm` (19KB) | Commando player + data in ACME syntax. |
| `monty_on_the_run_disassembly.md` | Annotated summary of the Monty disassembly. |
| `hubbard_classic_driver_format.txt` | Consolidated byte-level format from the 1xn.org disassembly. |
| `chacking_hubbard_driver_disassembly.md` | Additional C=Hacking format details from chipmusic.org recovery. |
| `recollection_hubbard_driver_disassembly.txt` (19KB) | Recollection Issue 3 McSweeney article (recovered via Wayback). |
| `chacking_issue5_full.txt` (205KB) | Complete C=Hacking Issue #5 with all articles. |
| `codebase64_chacking5.md` (51KB) | C=Hacking #5 from codebase64 wiki (Wayback recovery). |
| `codebase64_chacking5_full.md` (188KB) | Full issue from codebase64 wiki. |

### Format Specifications
| File | What |
|------|------|
| `data_format_reference.md` | Byte-level format spec with concrete hex examples from Commando and Monty. Voice 3 skip bug, Action Biker drums, SFX architecture, PCM loop details. |
| `player_architecture.md` | Data hierarchy, per-frame processing flow, key variables, per-game variant differences, known SID addresses for 9+ games. |
| `cadaver_music_essay.txt` | Cadaver's analysis of logarithmic vibrato algorithm, vibrato centering, hard restart methods (old vs testbit). |
| `codebase64_music_routine.md` (19KB) | Cadaver's "Building a musicroutine" — ghost registers, hard restart, data format design, optimization. |
| `siddecompiler_conversion_code.md` | **Actual parsing logic** from SIDdecompiler's commented-out code: sequence byte encoding, instrument parsing, FX flags, speed divider. |
| `siddecompiler_full_source.cpp` (356 lines) | Complete STHubbardRipper.cpp including disabled convert/convertSequence/convertInstruments methods. |

### Player Evolution & Variants
| File | What |
|------|------|
| `driver_version_history.md` | 5 phases: Razzmatazz (1984) → Classic (1985-86) → Transitional (1986) → New (1986-87) → EA (1988). |
| `vgmpf_driver_evolution.md` | Timeline with sidid signatures, 8+ composers who used the driver. Other-platform drivers (Atari ST, NES, SNES). |
| `vgmpf_hubbard_driver.txt` | VGMPF wiki content: per-game feature additions. |
| `c64audio_master_of_magic.txt` | Driver boundary: classic ended at Hollywood or Bust, new driver April 1986. |
| `hubbard_new_driver_1986.txt` | Gap analysis of the 1986+ "new driver" — known vs unknown format details. |
| `csdb_robtracker_jason_page.md` | **RobTracker is NOT a Hubbard variant** — Jason Page's independent player. Digi cycle timing: 67/63/52 cycles, ~14,705 Hz max. |
| `chipmusic_driver_thread.md` | 31 posts recovered via Wayback. logikstate: instrfx bits 3-7 change per song version. IK adds transposition, ACE II adds arpeggio tables. |

### Detection & Tooling
| File | What |
|------|------|
| `sidid_signatures.md` | All SIDID byte patterns with 6502 opcode decoding. |
| `sidid_signatures.txt` | Raw signature data. |
| `sidid_hubbard_signatures.txt` | Detailed analysis: confirms 8-byte instruments (ASL A x3), $FF/$FE terminators, 4-bit PCM. |
| `github_siddecompiler_hubbard_ripper.md` | Complete STHubbardRipper.cpp/h source + pattern summary table. |
| `tool_ecosystem.md` | All tools: SIDdecompiler, sidid, player-id, ChiptuneSAK, desidulate, Restore64.dev, realdmx ACME sources. |
| `csdb_editors_and_tools.md` | Scene editors: Moz(IC)art (ACE II), BHT editor (block format documented), Mirror, Paradroid V1.3. |
| `chiptunesak_sid_capture_analysis.md` | ChiptuneSAK note detection: 5 trigger conditions, vibrato margin snapping. Validation oracle. |
| `desidulate_ssf_analysis.md` | SSF (Sound Fragments) concept maps to Hubbard notes. Percussion detection logic. |
| `restore64_browser_disassembler.md` | Browser-based disassembler with 787 SIDID signatures. |

### SID Digi Reference (for Rob_Hubbard_Digi variant)
| File | What |
|------|------|
| `chacking20_c64_digi.txt` (90KB) | **Comprehensive C64 digi reference.** SID hardware internals, $D418 volume digis, 6581 vs 8580 differences, SID auto-detection, PWM digis, 7-bit/8-bit playback. |
| `chacking21_pwm_digi_followup.txt` (16KB) | Harsfalvi's 6-bit test-bit trick, Fourier analysis of PWM vs straight digis. |
| `chacking10_second_sid_chip.txt` | Second SID chip hardware installation. |
| `chacking11_dithering_sound.txt` | 5-bit digi dithering technique. |

### HVSC Census
| File | What |
|------|------|
| `hvsc_catalog.md` | 96 Hubbard SIDs: 82 Rob_Hubbard, 6 Jason_Page/RobTracker, 5 SidTracker64, 2 Companion. |
| `hvsc_variant_survey.md` | Full HVSC scan: Bjerregaard 65, Paradroid/Lameplayer 21, Laxity 31, Zicchi 7, Tjelta ~15. |
| `stil_notes.md` | Hubbard's own comments: Mr Meaner >50Hz, Delta custom driver, portamento for Monty. |

### Interviews & Historical Context
| File | What |
|------|------|
| `c64com_hubbard_interview.txt` | Multiplexing, VBlank, sample driver (2 samples + SID), optimization. Recovered via Wayback. |
| `sidmusicorg_hubbard_interview.txt` | "Thing on a Spring" was a driver test piece. All composition in assembler. Recovered via Wayback. |
| `gamejournal_driving_the_sid_chip.txt` (9.8KB) | Academic paper: verbatim Hubbard quotes, drum synthesis, why 8580 broke sample playback. |
| `remix64_jason_page_interview_full.txt` | Jason Page on MON drum technique (lookup tables), driver identity by sound. |
| `academic_analysis_and_interviews.md` | Index of all primary sources, interview quotes, HVSC stats. |
| `sid_history_and_techniques.txt` | Raw-value approach vs Galway's conversion, multiplexing, editor history. |

### Forum Threads & Community Knowledge
| File | What |
|------|------|
| `lemon64_freq_trick_thread.md` | tfg's explanation of the frequency table variable placement trick. |
| `lemon64_4mat_converter_thread.md` | 4mat (Matt Simmonds, NOT Jason Page) GT-to-Hubbard converter. No format details shared. |
| `lemon64_bz_utils_thread.md` | BZ Utils editor, Red/Judges Crazy Comets driver conversion. |
| `lemon64_additional_threads.md` | Aggregated from 5 threads + external references. |
| `sidin_magazine.md` | SIDin fanzine (15 issues, 2002-2015): no Hubbard disassembly, but Galway Arkanoid engine + architecture comparison table. |
| `research_sources.txt` | Index of all URLs fetched with status. |

## What We Know

### Classic driver (Phase 2, ~30 songs) — FULLY DOCUMENTED
- 4-level hierarchy: Module > Song > Track > Pattern
- Note encoding: 1-3 bytes (5-bit duration + 3 flag bits, optional instrument/portamento, pitch)
- Instrument format: 8 bytes (PW lo, PW hi, control, AD, SR, vibrato depth, PWM speed, FX flags)
- Effects (flag-driven, NOT table-driven): drum (bit 0), skydive (bit 1), octave arpeggio (bit 2)
- **instrfx bits 3-7 change meaning per song version** (logikstate, chipmusic.org)
- Logarithmic vibrato: freq delta to neighbor semitone, divided by 2^depth, triangle-wave oscillation `0,1,2,3,3,2,1,0`. First half-cycle is half-length for centering.
- PWM sweep: oscillate between ~$0800 (50%) and ~$0E00 (88%)
- Hard restart: gate clear + ADSR zero 2 frames before note end. Write order: Waveform → AD → SR.
- Frequency table trick: out-of-range pitch indexes into player variables (Commando staccato)
- The player never reads a note AND processes effects on the same channel in the same frame
- Track terminators: $FF = loop, $FE = stop
- Voice 3 skip bug in first ~30 songs: "first time the driver runs, note on voice 3 is skipped"
- SIDdecompiler patterns locate: songs, instruments, sequences, freq table
- SIDdecompiler conversion code confirms: sequence byte encoding (duration/tie/rest/modifier/pitch), 8-byte instrument layout, speed divider scaling
- **Instrument byte +5**: McSweeney says vibrato depth; SIDdecompiler marks as unknown — needs verification

### New driver (Phase 4, 1987) — PARTIALLY DOCUMENTED
- Table-based drums (March 1987), table-based PWM (July 1987)
- Filter support (mid-1986, filter varies per machine — VICE: 6581 ReSID bias >= 540)
- Pattern transposition (IK adds this)
- Arpeggio tables (ACE II adds this)
- 4-bit PCM via $D418 volume register (CIA timer driven, can loop in middle)
- Digi cycle timing: 67 max / 63 low-nibble / 52 high-nibble cycles, ~14,705 Hz max sample rate
- Classic driver ended at Hollywood or Bust; new driver from April 1986; Sanxion impossible on old driver
- **Byte-level format of table extensions: UNKNOWN — requires reverse engineering**

## Remaining Gaps

### Fillable from our own binaries (sidxray / disassembly)
1. **Phase 4 "New" driver table format** — Disassemble Delta or ACE II, diff against Monty. Highest priority.
2. **Rob_Hubbard_Digi sample data format** — Disassemble `Sample_Music_from_I_Karate.sid`. CIA timer setup, sample tables, sample rates. C=Hacking #20 digi reference now available.
3. **Per-game variant mapping** — Cluster 82 SIDs by code similarity (diff player code regions).
4. **Paradroid/HubbardEd differences** — Paradroid V1.3 editor (CSDb #101594) uses fixed ZP $FC. Disassemble and diff.
5. **Bjerregaard variant** — 65 SIDs, largest derivative family. Disassemble one and diff against standard.
6. **Instrument byte +5 verification** — Is it vibrato depth (McSweeney) or something else (SIDdecompiler uncertain)?

### Fillable from offline sources
1. **"Master of Magic" book** by Chris Abbott (C64Audio.com) — contains actual 6502 driver source excerpts. Commercial book (~$30). The only known source for new driver internals.

### Exhausted online sources (no further leads)
- CSDb: all editor pages fetched, all comments captured
- GitHub: SIDdecompiler fully extracted (including commented-out code), all tool repos surveyed
- Archive.org/Wayback: chipmusic.org recovered, codebase64 recovered, interviews recovered
- Lemon64: all relevant threads fetched
- C=Hacking: all 21 issues surveyed, SID-relevant ones (#5, #10, #11, #20, #21) saved
- HVSC: full variant survey complete
- Interviews: all 4 previously-blocked sources recovered
- SIDin magazine: all 15 issues surveyed (no Hubbard content)

## Recommended Build Order

1. **Start with classic driver (Phase 2)** — fully documented, ~30 songs, well-understood format
2. **Use SIDdecompiler patterns** to locate data structures in binary
3. **Use SIDdecompiler conversion code** as reference for sequence/instrument parsing
4. **Validate against register dumps** (siddump comparison, ChiptuneSAK as oracle)
5. **Extend to Phase 4** via disassembly of Delta/ACE II (sidxray + Restore64.dev)
6. **Handle variants** (Bjerregaard, Paradroid, Zicchi) by diffing against standard player
7. **Digi last** — smallest count, most complex (CIA timer). Use C=Hacking #20 as reference.
