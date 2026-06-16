# MoN/Deenen Forums & Wiki Research
# Sweep date: 2026-06-15
# Researcher: Claude (automated sweep)
# Sources: lemon64, codebase64, c64-wiki, forum64.de, usenet, web

---

## Executive Summary

The MoN/Deenen player family was created by Charles Deenen (with variants by Jeroen Tel, Reyn
Ouwehand, and Johannes Bjerregaard) for commercial C64 game music circa 1988–1993. The driver was
written in TurboAssembler ("Turbo Ass") and distributed in binary form — no authoritative public
specification document exists. The primary technical source is the GitHub repo
`realdmx/c64_6581_sid_players`, which contains reverse-engineered / recovered ACME-format
assembly for four MoN variant composers. Key findings: all variants share a common 8-byte
instrument format and a common sequence byte encoding scheme, with per-composer divergences in
effect tables, waveform count, and sequence command extensions.

---

## URLs Visited

### 1. codebase64.org — MoN page
URL: https://codebase64.org/doku.php?id=base:maniacs_of_noise
Result: **Page does not exist / empty response.** No technical content.

### 2. site:codebase64.org search for "maniacs of noise" OR "mon/deenen"
Result: No codebase64.org results returned. Results redirected to C64-Wiki and other sources.

### 3. C64-Wiki — Maniacs of Noise
URL: https://www.c64-wiki.com/wiki/Maniacs_of_Noise
Result: Biographical/historical only. Only relevant technical fact: "When Deenen saw Tel arrange
a song in about 10 minutes, he created a music driver for Donné and Tel." No format specs.

### 4. C64-Wiki — Charles Deenen
URL: https://www.c64-wiki.com/wiki/Charles_Deenen
Result: HTTP 404.

### 5. VGMPF Wiki — Maniacs of Noise
URL: https://vgmpf.com/Wiki/index.php/Maniacs_of_Noise
Result: Limited technical content. Key facts extracted:
- Driver called "Musicfile", programmed in Turbo Ass
- Two format identifiers: JT (Jeroen Tel) and MON (also credited to Frederic Hahn in one source)
- Composers arranged by "typing hexadecimal numbers and labels into the driver's source code"
- Bjerregaard preferred his own driver; Petersen also used his own
- Deenen's C64 driver was officially converted to the 128K ZX Spectrum

### 6. VGMPF Wiki — Charles Deenen
URL: https://vgmpf.com/Wiki/index.php/Charles_Deenen
Result: Confirms "Around 1985 he wrote a C64 sound-driver." When working with MoN, he used
Jeroen Tel's version of the driver. Games using his drivers include: Hawkeye, Battle Valley,
Scorpion, Zyron, Stormlord, Golden Axe, Inve$t (pre-MoN). No format specs.

### 7. ExoticA — Jeroen Tel (format)
URL: https://www.exotica.org.uk/wiki/Jeroen_Tel_(format)
Result: Browser verification wall — no content retrieved.

### 8. ExoticA — Maniacs of Noise
URL: https://www.exotica.org.uk/wiki/Maniacs_of_Noise
Result: Browser verification wall — no content retrieved.

### 9. CSDb — Maniacs of Noise group page
URL: https://csdb.dk/group/?id=448
Result: Group profile page. Tools & utilities identified:
- **MON SFX Editor V1.00** (1990) — ID 10759, code by Charles Deenen + Roland Hermans (Dragon-Fly Soft)
- **MON SFX Relocator V1.0** — ID 10760, relocates SFX data
- **MON SFX Crash Saver V1.0** — ID 10761, code by Roland Hermans of Dragon-Fly Soft and Revive
- **JCH NewPlayer 21.g4 beta (21.b4)** — 2005, by Laxity, tool for music playback
- **JCH NewPlayer 21.g4 Final** — 2006
- **JCH NewPlayer 21.g5** — 2006

### 10. CSDb — MON SFX Editor V1.00
URL: https://csdb.dk/release/?id=10759
Result: Released 1990. Code credited to Charles Deenen (MoN, Scoop) + Roland Hermans (Dragon-Fly
Soft). Two downloads: "Music Mania.zip" and "Monase_1.0.zip". No format documentation on the
page, but the "Monase v1.0" package is described as containing all necessary files.

### 11. CSDb — MON SFX Relocator V1.0
URL: https://csdb.dk/release/?id=10760
Result: Tool for relocating MoN SFX data. 631 downloads. Available as Monase_1.0.zip and via
Pokefinder.org. No format documentation.

### 12. CSDb — MON SFX Crash Saver V1.0
URL: https://csdb.dk/release/?id=10761
Result: Tool for crash/data recovery. Code by Roland Hermans. Available in Music Mania.zip.
No format documentation.

### 13. CSDb — Charles Deenen scener page
URL: https://csdb.dk/scener/?id=1040
Result: Key releases:
- MON SFX Editor V1.00 (1990), code
- Future Composer V3.1 (1990), code — NOTE: Deenen also worked on Future Composer!
- Sound Machine V1.1 (1989), code+music
- Music/SFX for: Outrun Europe, Formula 1 Simulator, Mr. Heli, Rubicon, B.A.T., Stock Car Racer

### 14. CSDb — Jeroen Tel scener page
URL: https://csdb.dk/scener/?id=8050
Result: Tel is primarily listed as musician/composer rather than tool developer. No standalone
driver tool releases attributed to him directly. Notable: "JCH NewPlayer" (Laxity's player)
can play Tel's music.

### 15. Hugi #38 — Jeroen Tel interview
URL: https://hugi.scene.org/online/hugi38/hugi%2038%20-%20demoscene%20interviews%20magic%20jeroen%20tel.htm
Result: Interview text. Only driver-relevant statement: Tel says he "hacked into Hubbard's
routine to compose music in machine-code, since I didn't have my own music driver yet." This
confirms Tel learned on existing drivers before the MoN driver was created. No format specs.

### 16. lemon64.com — Charles Deenen Q&A thread
URL: https://www.lemon64.com/forum/viewtopic.php?t=16873&start=15
Result: Biographical Q&A. Deenen states he no longer composes. No technical content.

### 17. lemon64.com — Sound coding in Assembler thread
URL: https://www.lemon64.com/forum/viewtopic.php?t=86473
Result: General SID programming discussion. No MoN-specific content.

### 18. Wikipedia — Charles Deenen
URL: https://en.wikipedia.org/wiki/Charles_Deenen
Result: Confirms 1987 MoN founding (with Tel and others). "Composed music for over 300 C64 and
Amiga games." No format specifications.

### 19. c64.com — Charles Deenen interview
URL: https://www.c64.com/gt_display_interview.php?interview=8
Result: SSL certificate error — not retrieved.

### 20. CSDb — JCH NewPlayer 21.g4 beta
URL: https://csdb.dk/release/?id=20112
Result: A playback utility by Laxity (2005), released under MoN + Vibrants. "JCH NP 21.g4".
This is a PLAYER for the JCH/Tel format, not the MoN/Deenen format per se. Download: 
NewPlayer v21.G4 Beta.zip.

### 21. GitHub — WilfredC64/player-id (sidid.cfg)
URL: https://github.com/WilfredC64/player-id
URL: https://github.com/WilfredC64/player-id/blob/main/config/sidid.cfg
Result: sidid.cfg is in config/ subdirectory. Raw URL returned 404. The web view was truncated
at ~line 1200 of 2375 total lines. The visible portion contained NO explicit "MoN", "Deenen",
or "Jeroen Tel" entries. The remaining ~1175 lines were not inspected — signatures may be there.

### 22. GitHub — realdmx/c64_6581_sid_players  *** PRIMARY TECHNICAL SOURCE ***
URL: https://github.com/realdmx/c64_6581_sid_players
Result: Repository of "original and reverse-engineered music players for the C64." Contains
FOUR MoN-family subdirectories:
- Bjerregaard_Johannes_MON/
- Deenen_Charles_MON/
- Ouwehand_Reyn_MON/
- Tel_Jeroen_MON/

README: "In the olden days, every budding musician wanting to make it in the business had no
other choice but to program their own music player. Sources have been recovered or
reverse-engineered by various people." Files are ACME assembler format, produce playable .sid
files.

### 23. Archive.org — Cybernoid Music (1988)(Maniacs Of Noise)
URL: https://archive.org/details/Cybernoid_Music_1988_Maniacs_Of_Noise
Result: .d64 disk image. Single file: "cybernoid 1 /mon" (PRG). Credits: Code=Charles Deenen,
Music=Jeroen Tel. Emulated via VICE-RESID. 45 screenshots. No player source.

### 24. Archive.org — Maniacs of Noise Music 1
URL: https://archive.org/details/Maniacs_of_Noise_Music_1_19xx_FCC
Result: .d64 disk image, 77 files (35 screenshots + disk). No player source documentation.

### 25. file-extensions.org — .mon extension
URL: https://www.file-extensions.org/mon-file-extension-maniacs-of-noise-audio-file
Result: HTTP 403. Not retrieved. (The other file-extensions.org page confirmed: .mon = Maniacs
of Noise Audio File, used with .jt format pair.)

### 26. CSDb forums — "maniacs of noise releases" thread
URL: https://csdb.dk/forums/?roomid=9&topicid=5112&firstpost=2
Result: Request thread for locating MoN releases. References "Charles' SFX screens" and a
collection URL. No technical format content.

### 27. HVSC SID_PLAYERS.txt
URL: https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/SID_PLAYERS.txt
Result: HTTP 404 — file not present at that URL.

### 28. DeepSID
URL: https://deepsid.chordian.net/
Result: No MoN/Deenen format documentation visible on landing page.

### 29. CSDb search — "maniacs of noise player"
URL: https://csdb.dk/search/?stype=release&search=maniacs+of+noise+player
Result: No results found. Search too specific.

### 30. Demozoo — Maniacs of Noise
URL: https://demozoo.org/groups/950/
Result: (Not fetched directly — seen in search results.) Group profile.

---

## PRIMARY TECHNICAL FINDINGS

### Source: realdmx/c64_6581_sid_players

The GitHub repo contains four MoN variant players, all converted from TurboAssembler to ACME
by "dmx87". Below is the technical extraction from each.

---

#### A. Deenen_Charles_MON — SFX Player (1989, Scoop)

**File:** Deenen_Charles_SFX_Player.asm  
**PSID header:**
- Load: $1000 (auto)
- Init: `restart`, Play: `plloop`
- Songs: 6, default song 1
- Title: "SFX Player", Author: "Charles Deenen", Copyright: "1989 Scoop"

**Sound settings table (`wfadsr`) — per instrument:**
```
byte 0: waveform index
byte 1: attack/decay
byte 2: sustain/release
byte 3: pulse setting
byte 4: frequency table reference
byte 5: vibrato setting
byte 6-7: reserved/flags
```

**Pulse table (`pudata`) — 5 bytes per entry:**
slide speed, pulse width ceiling, increment rate, offset

**Vibrato table (`vidata`) — 4 bytes per entry:**
delay start, length, amplitude, speed

**Waveform sequences (`wf0`-`wf4`):** chains terminated by `end` ($08)

**Sequence command encoding:**
| Code | Function |
|------|----------|
| $00  | End/Arpeggio end |
| $7a  | Duration control |
| $7b  | Repeat block |
| $7c  | Pause |
| $7d  | Filter off |
| $7e  | Filter |
| $7f  | Glide |
| $80+ | Duration byte |
| $e0  | Sound selection |

**Note table:** $00–$5F, chromatic C0–B7 (96 notes, 8 octaves), 16-bit freq in `lobyte`/`hibyte`.

**Filter:** resonance, length, cutoff parameters as sequence commands.

---

#### B. Deenen_Charles_MON — Test Tune (1988, Maniacs of Noise)

**File:** Deenen_Charles_Test_Tune.asm  
**PSID header:**
- Load: $1000, Init: $1000, Play: $1006
- Title: "Test Tune", Author: "Charles Deenen", Copyright: "1988 Maniacs of Noise"

**Zero page allocation ($61–$70):** effect parameters, vibrato data, temp values, note calculations.

**Instrument format (8 bytes per set):**
```
byte 0: waveform
byte 1: attack/decay
byte 2: sustain/release
byte 3: gate_on_length
byte 4: pulse_fx
byte 5: fx1 (vibrato)
byte 6: fx2 (pulse sweep)
byte 7: fx3 (arp/drum/flags)
```
6 instrument sets (sets 0–5) defined.

**Pulse table (`pudata`):** 8 variants, 5 bytes each
**Vibrato table (`vidata`):** 8 variants, 4 bytes each
**Sine wave lookup (`sinus`):** 128 entries for vibrato calculation
**Arpeggio patterns (`arp1`–`arp7`):** 7 pitch sequences
**Drum tables:**
- `drum1`–`drum4` (4 patterns), waveform envelopes `wft1`–`wft4`
- Drum triggers via waveform byte $e0+ or bit in waveform byte

**Filter banks (`fb0`–`fb5`):** 6 filter configs with cutoff and modulation curves

**Sequence format:**
- Three tracks (`seq0a`, `seq0b`, `seq0c`)
- Reference 48 music data blocks (`st00`–`st3f`)
- Special bytes:
  - $FF = repeat sequence
  - $FE = end sequence
  - $C0–$DF = instrument selection
  - $80–$BF = note length encoding
  - $00–$7F = pitch notes with modifiers

**Main routines:** `song` (init), `songout` (stop+SID clear), `playirq` (IRQ handler)

---

#### C. Deenen_Charles_MON — Test Tune 2 (1988, Maniacs of Noise)

**File:** Deenen_Charles_Test_Tune2.asm  
**PSID header:**
- Load: $1000 (auto), similar layout to Test_Tune
- Same 8-byte instrument format
- 13 instruments (0–12) — expanded from Test_Tune's 6

**Additional data structures:**
```
pudata: 8 pulse variants (same count as Test_Tune)
vidata: 8 vibrato variants
sinus: 128-entry sine lookup (same)
arp1–arp7: 7 arpeggio patterns
drum1–drum4 with wft1–wft4
fb0–fb5: 6 filter banks
```

**Drum system:** Drum triggers via high bit in waveform byte ($e0+). Separate drum frequency
envelope sequences.

**Command bytes (same as Test_Tune):**
- Duration prefix ($80+)
- Sound select ($e0+)
- Pause ($7c), Filter ($7e), Glide ($7f)

**Sequence structure:** block-based note sequencing, repeat/loop via `repc` counter.

---

#### D. Tel_Jeroen_MON — Cybernoid 2 (1988)

**File:** Tel_Jeroen_Cybernoid2.asm  
**PSID header:**
- Load: $1000, 2 songs (Cybernoid II title + Game Over)
- Title/Author/Copyright fields present, PAL timing, 6581 SID chip
- Code credited: "player designed by Charles Deenen" for Tel's compositions

**Zero page allocation ($40–$52):**
effect storage, vibrato state, glide parameters, note frequency data, filter settings

**Per-voice tracking arrays (3 entries each):**
`tabcount`, `begcount`, `nootcount` — sequencing position
`nootleng`, `wavesto`, `noothoogt` — note length and waveform
`hinotesto`, `lonotesto` — frequency registers
`pulsestolo`, `pulsehisto` — pulse width
`filter`, `filtercount` — resonance filter

**Instrument format (8 bytes each), 18 presets:**
```
offset +0: Pulse Width High byte
offset +1: Waveform (Triangle/Sawtooth/Pulse selection)
offset +2: Attack/Decay (ADSR)
offset +3: Sustain/Release (ADSR)
offset +4: Filter Count (resonance type/freq)
offset +5: FX1 (vibrato depth and modulation)
offset +6: FX2 (pulse sweep direction and speed)
offset +7: FX3 (bit flags: drum, arpeggio, sweep)
```

**Sequence byte encoding:**
```
$00–$3F: Note pitch value (index into frequency table)
$40–$7F: Tone offset accumulation
$80–$BF: Note duration with optional wave selection
$C0–$DF: Glide/portamento parameters
$E0–$EF: Filter/resonance setup
$FF:     Track end marker
$FE:     Song loop terminator
```

**Note lookup tables:** `lonote`/`hinote` (88 semitones, paired bytes); `lonote2`/`hinote2` for
vibrato modulation offsets.

**Effect pipeline:**
- Vibrato: amplitude+speed via `fx1sto`, counter-based phase through `vibcounter`
- Pulse sweep: `pulsetabel` defines ramp direction/duration/boundary, `pulsetest` tracks direction
- Glide/Portamento: `glidetest` flag, `glidedelay` timing, linear freq interpolation toward `tempglide`
- Arpeggiation: `arplo`/`arphi` (8 preset patterns), `tonearpcounter` cycles offsets
- Drum: conditional on `fx3sto` bit 4; waveform+freq envelopes from `drumtabel` time-indexed
- Filter: 8 preset banks (`fb0`–`fb3`), counter-based cutoff progression

**Timing:** `speedbyte` sets playback speed. `counter2` tracks elapsed frames; IRQ decrements
`speedsto`; voice processing gates on `speedsto == speedbyte`.

**Song data:** song 1 = 3 tracks (`seq0a`/`seq0b`/`seq0c`) with 17 reusable step sequences;
song 2 (Game Over) triggers `st08`, `st0a`, `st1e`. `snelheid` speed table (both songs = 2).

**Entry points:** `init`, `play`, `songout`

---

#### E. Ouwehand_Reyn_MON — Armada (1989, Scoop Designs)

**File:** Ouwehand_Reyn_Armada.asm  
**PSID header:**
- Credits: "player designed by Charles Deenen for Reyn Ouwehand, programmed by Scoop Designs 1989"

**Features (expanded from Deenen/Tel variants):**
- 25 instrument sets (set 0–18 labeled)
- 10 arpeggio patterns
- 6 pulse width tables
- 9 drum kits with custom envelopes
- 3 filter presets with envelope automation
- Wave arpeggio, pulse arpeggio, noise synthesis, double voice, spacing effects

**Instrument format:** Same 8-byte structure; adds pulse arpeggio and waveform bank in fx bytes.

**Effects:** vibrato, arpeggio, portamento/glide, pulse width modulation, drum synthesis, filter,
wave arpeggio, noise synthesis.

---

#### F. Ouwehand_Reyn_MON — Dutch Breeze (1990, MON)

**File:** Ouwehand_Reyn_Dutch_Breeze.asm  
**PSID header:**
- Title: "Dutch Breeze", Author: "Reyn Ouwehand", Copyright: "1990 MON"

**Expanded data tables:**
- 21 instrument entries
- 25 arpeggio patterns (arp0–arp24)
- 8 pulse tables (`pultablo`/`pultabhi`)
- 7 filter presets with timing (`filbyt`)
- 11 drum waveform sequences (`drmtab`)
- Waveform bank mapping (`starttabel`/`startlen`)
- 16 zero-page bytes used

**Extended sequence commands:**
```
$c0–$df: Instrument selection with optional transposition
$fd:     Glide setup with target note
$fc:     Fade envelope
$fb:     Connection byte toggle
$e0–$ff: Pause durations
$ff/$fe: Loop/jump markers
```

**Voice architecture:** shadowed SID register copies (`d400`–`d406` arrays); 3-frame subdivision;
independent speed/dubdec timing per voice.

**Note tables:** `lonote`/`hinote` 96-note frequency table; `attdec`/`susrel` envelope templates.

---

#### G. Bjerregaard_Johannes_MON — James Bond 3 Demo (1989)

**File:** Bjerregaard_J_James_Bond_3.asm  
**PSID header:**
- Title: "James Bond 3 Demo", Author: "Johannes Bjerregaard", 1989

**Entry points:** `SETMUS` (init, song selection via A), `PLAY` (IRQ handler), `MUSOFF` (silence)

**Voice control:** SID at $D400, $D407, $D40E (offset `D4POINT` = 0, 7, 14)

**Per-voice state:**
`SEQNO`, `SEQPTR`, `ENVPTR` (instrument pointer), `GATE`, `LEN`, `TEMPNOTE`, `LOFQ`/`HIFQ`,
`GLIDE`, `VIBRATE`/`VIBRATEHI`, `LOPW`/`HIPW`, `PWPCOUNTER`

**Instrument format (SET1, 8 bytes):**
```
byte 0: Attack/Decay
byte 1: Sustain/Release
byte 2: Vibrato depth/delay
byte 3: Pulse width sequence index / release delay
byte 4: Arpeggio selection
byte 5: Filter sequence index
byte 6: Waveform sequence index
byte 7: Vibrato rate/sustain level (bits 4-7 = secondary sustain level)
```
NOTE: DIFFERENT byte order from Deenen/Tel variant! AD/SR are bytes 0-1 here vs bytes 2-3 in
the other variants.

**Sequence encoding (DIFFERS from Deenen/Tel):**
```
$00–$3F: Rest with duration
$40–$7F: Transpose offset
$80–$9F: Envelope/instrument select
$A0–$BF: Glide with target note
$C0–$DF: Note with duration
$E0–$FF: Pause duration
$FE:     Tie next note
$FF:     Sequence end/loop
```

**Frequency tables:** `FQDATLO`/`FQDATHI`, ~5 octaves.
**Filter:** `FITABLO`/`FITABHI` lookup tables for cutoff progression.
**Timing:** single global `TEMPOCNT` (decremented per IRQ).

**Distinguishing features vs standard Deenen/Tel:**
1. "Second Sustain" — byte 7 bits 4-7 set secondary sustain level during release
2. `NEWRELOFF` counter for delayed release trigger
3. Chip always forced waveform gate clear before new notes
4. Auto sustain delay — byte 6 bits 5-7 specify release frame delay
5. Different sequence opcode ranges ($80–$9F for instrument, $C0–$DF for note)

NOTE: This matches what vgmpf.com says ("Bjerregaard preferred his own driver") — the
Bjerregaard variant is structurally different enough to be considered a fork.

---

## Format Versioning and Variant Summary

Based on assembled evidence:

### MoN family tree

```
~1985 Charles Deenen: original "Musicfile" driver (private, Turbo Ass)
   |
   +-- 1988: "Test Tune" era (Deenen) — initial MoN driver
   |     Instruments: 6–13 sets, 8-byte format (waveform first)
   |     Sequences: $C0-$DF=instrument, $80-$BF=length, $FF=loop
   |
   +-- 1988-1989: Jeroen Tel variant (Cybernoid, Cybernoid 2)
   |     Same 8-byte instrument format as Deenen
   |     Expanded: 18 instruments, 8 arpeggio patterns, 4 filter banks
   |     Adds: tone offset accumulation ($40-$7F)
   |
   +-- 1989-1990: Reyn Ouwehand variant (Armada, Dutch Breeze)
   |     Expanded: 21-25 instruments, 25 arp patterns, 11 drum kits
   |     Adds: $fd glide, $fc fade, $fb connection; waveform banks
   |     3-frame voice subdivision, shadowed SID registers
   |
   +-- 1989: Johannes Bjerregaard fork (James Bond 3)
         Different instrument byte order (AD/SR first, not waveform first)
         Different sequence encoding ($C0-$DF=note vs instrument)
         "Second sustain" enhancement
         Single global tempo counter
```

### Common Core (all non-Bjerregaard variants)
- Load address: $1000
- 8-byte instrument record
- 3-voice polyphony
- 96-note frequency table (C0–B7)
- Per-voice: vibrato, pulse sweep, glide, arpeggio, drum
- Sequence: $FF=loop, $FE=end

### File format names
- `.mon` — Maniacs of Noise audio file
- `.jt` — Jeroen Tel variant
- Both formats noted as used in the vgmpf.com article

### SFX Subsystem (separate from music player)
Three distinct tools shipped for the SFX data (not music):
- MON SFX Editor V1.00 (1990) — edit SFX entries
- MON SFX Relocator V1.0 — relocate SFX data in memory
- MON SFX Crash Saver V1.0 — rescue/recover SFX from crashed states
All three available from Monase_1.0.zip on CSDb.

---

## Notable Biographical/Context Facts

- MoN founded 1987 by Charles Deenen, Jeroen Tel, Marcel Donné (met at Venlo Meetings)
- Reyn Ouwehand joined age 16, first job = Last Ninja Remix
- Driver composed by typing hex numbers and labels directly into source
- Each game took 2–6 days, paid £100–£1000 per game
- Deenen also contributed code to Future Composer V3.1 (1990)
- Deenen left MoN ca. 1990 to join Scoop; Armada (1989) already credited "Scoop Designs"
- JCH NewPlayer (Laxity, 2005-2006) plays Jeroen Tel's music — this is the JCH format
  (related but distinct from MoN/Deenen HVSC classification)

---

## HVSC Classification

HVSC uses "MoN/Deenen" as the engine tag (as reported by sidid). This appears to cover the
main Deenen/Tel/Ouwehand variant family. The Bjerregaard fork may be classified separately or
under the same tag depending on how HVSC sidid signatures were set up.

---

## Leads to Follow

### Highest priority — actual source code and binaries

1. **Download Monase_1.0.zip from CSDb** (MON SFX Editor, Relocator, Crash Saver package):
   https://csdb.dk/release/?id=10759 — Download "Monase_1.0.zip". This likely contains the
   SFX player binary and possibly the music player binary. Disassembling these would give exact
   memory layout.

2. **Fetch remaining realdmx files not yet retrieved:**
   - https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Bjerregaard_Johannes_MON/Bjerregaard_J_Myth.asm
   - https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Ouwehand_Reyn_MON/ (check if more files exist)
   - Check for any README in the realdmx repo root or per-folder

3. **Read full sidid.cfg** (WilfredC64/player-id):
   The config/sidid.cfg was truncated at line 1200 of 2375. The MoN/Deenen signature bytes
   (the byte pattern HVSC uses to fingerprint SID files as MoN/Deenen) are likely in the
   second half. Full raw file:
   https://raw.githubusercontent.com/WilfredC64/player-id/refs/heads/main/config/sidid.cfg

4. **"Music Mania.zip" from CSDb** — appears in multiple MON tool downloads; may contain
   original player binaries or music data files for multiple MoN tunes.

### CSDb entries to check

5. **CSDb release ID 7936** (MON SFX Editor, alternate ID seen in scener page search):
   https://csdb.dk/release/?id=7936

6. **CSDb user comments on MON SFX Editor** — the page noted user comments including one from
   2010 mentioning "Monase v1.0 variant". May contain more technical info:
   https://csdb.dk/release/?id=10759

7. **Check other Bjerregaard CSDb entries** for any released music player source:
   https://csdb.dk/scener/?id=??? (Bjerregaard not yet found in CSDb)

### Format documentation

8. **Just Solve the File Format Problem — Maniacs of Noise page**:
   http://justsolve.archiveteam.org/wiki/Maniacs_of_Noise (ECONNREFUSED during this sweep;
   retry later)

9. **Codebase64 wiki SID programming section**:
   https://codebase64.net/doku.php?id=base:sid_programming — general SID programming; may
   link to MoN-specific documentation

10. **Pokefinder.org** — mentioned as mirror for Monase_1.0.zip; may have additional MoN
    content not on CSDb.

### People to contact / interviews to find

11. **Reyn Ouwehand** — still active in game audio; his CSDb page:
    https://csdb.dk/scener/?id=8051 — may have posted technical notes or links to source

12. **"dmx87" / realdmx** — the GitHub repo author who reverse-engineered the players. The
    GitHub profile may have blog posts or notes on the RE process and format variants.
    https://github.com/realdmx

13. **Jeroen Tel's website** (http://jeroen.tel/) — may have technical section or downloads of
    his player source code

### HVSC investigation

14. **Examine actual HVSC MoN/Deenen SID files** — the load address is consistently $1000;
    use `tools/seed_disassembly.py` on a representative SID (e.g. Cybernoid or Last Ninja Remix)
    to generate an annotated disassembly. Cross-reference against realdmx source.

15. **sidid tool / sidid.cfg** — run the HVSC sidid tool against known MoN/Deenen SIDs to
    extract the fingerprint byte sequence used for classification:
    https://github.com/WilfredC64/player-id (build and run against hvsc84/ MoN/Deenen files)

16. **HVSC DOCUMENTS/ directory** — SID_PLAYERS.txt was 404 at the tried URL; check the
    actual HVSC download tree at hvsc84/DOCUMENTS/ in the local HVSC copy for this file.

---

## Key Disambiguations

- "JCH NewPlayer" / "JCH format" — this is Laxity's PLAYER for Jeroen Tel's (JCH) SID music
  format. DIFFERENT from MoN/Deenen. Jeroen Tel composed in MoN format for C64 game music;
  his demoscene music used the JCH format. These are separate engines.

- "Musicfile" — Deenen's internal name for his driver. Not a public standard.

- "MON" suffix in realdmx repo (Bjerregaard_Johannes_MON, etc.) = "Maniacs of Noise" player
  family, not Frederic Hahn's "MON" format mentioned in one vgmpf source. The vgmpf attribution
  of "MON (Frederic Hahn)" appears to be an error or conflation.

- Charles Deenen also contributed to Future Composer V3.1 (1990 CSDb) — separate engine family.
