---
source_url: multiple — see per-section citations
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni ("Cadaver") / Covert Bitops; CSDb community
content_date: 2002–2021
reliability: primary
---

# NinjaTracker — CSDb / Covert Bitops / Pouet Research Findings

## 1. Author & Group

- **Author:** Lasse Öörni, handle "Cadaver" (CSDb scener ID **2908**)
- **Group:** Covert Bitops (CSDb group ID **1287**)
  - Homepage frame-redirects to: https://cadaver.github.io/
  - Cadaver is Finnish (country: Finland on CSDb).
  - Also member of Protovision since July 2020.
  - Tools page: https://cadaver.github.io/tools.html (HTML source at `tmp/ninjatracker_research/cadaver_tools.html`)

---

## 2. Complete NinjaTracker Release History (CSDb)

All releases are authored by Cadaver / Covert Bitops. CSDb IDs extracted from
scener page https://csdb.dk/scener/?id=2908.

### V1.x line (2002–2004)

| CSDb ID | Title | Date | Notes |
|---------|-------|------|-------|
| 7206 | NinjaTracker V1.0 | 2002-10-31 | First release. Download: `ninjatrk.zip` (CSDb internal 29747, 964 DLs). Also on Pokefinder. |
| 7310 | NinjaTracker V1.01 | 2002 | |
| 7258 | NinjaTracker V1.01 Gamemusic Version | 2002 | Separate gamemusic variant |
| 7261 | NinjaTracker V1.02 | 2002 | Added sound effect capability; octave 0 removed from playroutine |
| 7257 | NinjaTracker V1.03 | 2002 | |
| 8661 | NinjaTracker V1.04 | 2003 | |
| 39500 | NinjaTracker V1.05 | 2004 | Slide duration calculator; allow editing sector 0 |
| 39501 | NinjaTracker V1.1 | 2004 | Hardrestart solidified (AD,SR both $00); INS in pulse/filtertable inserts 00,00 instead of 90,00; pulse/filter pointers adjusted on INS/DEL in pulse/filter tables; pattern movement speed-optimized. Download: `ninjatrk.zip` (cadaver.github.io) |

### V2.x line (2006–2013)

| CSDb ID | Title | Date | Notes |
|---------|-------|------|-------|
| 39374 | NinjaTracker V2.0 | 2006 | Original V2. New features: commands (= instruments), 2-column tables, slide-to-target-pitch. |
| 39498 | NinjaTracker V2.01 | 2006 | Gamemusic SFX routine optimized; ins2nt2 updated; pattern view improvements |
| 39499 | NinjaTracker V2.02 | 2006 | Hardrestart 2 frames by default (init waveform gate-off); ZP use reduced to 2 bytes; arpeggio absolute note range limited |
| 39571 | NinjaTracker V2.03 | 2006 | Hardrestart = 2 frames + 1 silent frame ("hifi" style); duration range 3–65; transpose/loop duration restrictions removed; slide target-branch changed |
| **119721** | **NinjaTracker V2.04** | **2013-06-19** | Final official release. Bug fix: transpose reset when subtune played from beginning. Download: `ninjatr204.zip` (CSDb internal 118068, 1118 DLs) |

### Third-party editor mod

| CSDb ID | Title | Date | Notes |
|---------|-------|------|-------|
| 152640 | NinjaTracker MOD V2.04 | 2017-01-10 | By Spider Jerusalem (spider/myd!). Editor changes only (different F-key layout matching GoatTracker/SidWizard style, DMC keyboard removed, color changes). **Playroutine unchanged / fully compatible with official NT V2.04.** Download: `ninjatrMOD204.zip` + `ninjamod.d64` (CSDb internals 154170/154171, 631/291 DLs). |

### GT→NT converters

| CSDb ID | Title | Date | Notes |
|---------|-------|------|-------|
| 7833 | GoatTracker → NinjaTracker convertor | 2003 | GT V1.x → NT V1.03+ format. Download: `goatninj.zip`. V1.11 final. |
| 115448 | GoatTracker2 to NinjaTracker2 Converter V1.0 | 2013-02-03 | GT2 → NT2.03+ format. Download: `gt2nt2.zip` (CSDb 113477, 518 DLs). |
| 152424 | GoatTracker2 to NinjaTracker2 Converter V1.02 | 2015-10-03 | Adds `gt2nt2src` variant producing gamemusic source format. Download: (CSDb 153892, 344 DLs). |

The final `gt2nt2.zip` on cadaver.github.io is V1.03 (2021-09-11) with `gt2nt2src.c` dated 2021. No separate CSDb entry found for V1.03.

---

## 3. Covert Bitops Homepage Findings

Real URL: https://cadaver.github.io/tools.html (covertbitops.c64.org redirects via frameset).

**NinjaTracker V2.04 description (verbatim):**
> A C64 music editor with quite minimal featureset. Changes to previous versions include commands (also used as instruments), two-column tables and a slide function that stops at target pitch. As before, allows to save both normal executable musicdata and gamemusic data without the player.
>
> V2.04 fixes transpose not resetting when playback is started from the beginning.

**Download URLs on cadaver.github.io:**
- `tools/ninjatr204.zip` — NT V2.04 (editor + player source `nt2play.s`)
- `tools/gt2nt2.zip` — GT2→NT2 converter V1.03
- `tools/ninjatrk.zip` — NT V1.1 (the latest V1.x; editor disk + `ntplay.s`)
- `tools/ninja102.zip` — NT V1.02
- `tools/goatninj.zip` — GT V1.xx → NT V1.03+ converter

**Related tools also on the page:**
- **MiniPlayer** / **MiniPlayer 2** — feature-stripped playroutines targeting 9 rasterlines, with GT2→NT-style converter. Source only, GitHub repos `cadaver/miniplayer` + `cadaver/miniplayer2`.
- **GoatTracker V1.xx → NinjaTracker converter**: `tools/goatninj.zip`

---

## 4. GT2→NT2 Converter (GT2NT2) — Technical Details

Source: `gt2nt2.zip` / `gt2nt2src.c` (local: `tmp/ninjatracker_research/extracted/gt2nt2/`)

### GT2→NT2 V1.03 readme — unsupported GT2 features

- More than 127 patterns or 16 subtunes
- Combined 3-track orderlist > 256 bytes
- Pattern > 192 bytes after conversion
- Octave 0
- Wavetable commands
- "Leave frequency unchanged" in wavetable
- Changing filter mode without cutoff (or vice versa)
- Filter resonance control (passband+8 copied to resonance instead)
- Pattern commands 7, C, D, E
- Vibrato (cmd 4) with a new note
- Fine pulse modulations (NT only uses high 4 bits of GT pulse speed)
- Calculated (note-independent) slide / vibrato speed

Two commands: `gt2nt2` (binary output), `gt2nt2src` (DASM source output, gamemusic mode).
Max duration param: default 65 (NT max).

### Binary gamemusic module layout (from `saventsong()` in `gt2nt2src.c`)

The gamemusic module header is 6 bytes:
```
dc.b wavetbllen, pulsetbllen, filttbllen, cmdlen, legatocmdlen, highestpatt+1
```

Followed in order:
1. `wavetbl[wavetbllen]`
2. `notetbl[wavetbllen]` — arpeggio/note column
3. `pulsetimetbl[pulsetbllen]`
4. `pulsespdtbl[pulsetbllen]`
5. `filttimetbl[filttbllen]`
6. `filtspdtbl[filttbllen]`
7. `cmdad[cmdlen]`
8. `cmdsr[cmdlen]`
9. `cmdwavepos[legatocmdlen]`
10. `cmdpulsepos[legatocmdlen]`
11. `cmdfiltpos[legatocmdlen]`
12. Pattern table lo-bytes (one per pattern)
13. Pattern table hi-bytes (one per pattern)
14. Song/track table: for each subtune — `dc.w trackN, dc.b 0, songlen_ch1, songlen_ch1+ch2`
15. Pattern data (variable-length per pattern)
16. Track/orderlist data per subtune (three concatenated channel orderlists)

Noteworthy fixups in the converter: vibrato bytes $C0–$DF are bit-reversed ($xor $1F); pulse negative speed bytes are decremented by 1 and nybble-reversed (NT stores pulse speed with nybbles swapped).

---

## 5. NinjaTracker V2.04 Technical Reference

Sources: `readme.txt`, `nt2play.s`, `src/ninjatr2.s`, `src/nt2songdata.s`, `src/nt2var.s`
(local: `tmp/ninjatracker_research/extracted/nt204/`)

### 5.1 Editor limits (from `src/ninjatr2.s` constants)

```
MAX_SONGS    = 16       ; subtunes
MAX_PATT     = 127      ; patterns
MAX_CMD      = 127      ; commands (= instruments)
MAX_CMDNAMELEN = 9      ; command name max length
MAX_PATTLEN  = 192      ; max bytes per pattern (packed)
MAX_SONGLEN  = 256      ; max bytes per subtune orderlist (3 tracks combined)
MAX_TBLLEN   = 255      ; max table entries
MIN_OCTAVE   = 1
MAX_OCTAVE   = 7
```

Default hardrestart: `DEFAULT_HRPARAM = $00`, `DEFAULT_FIRSTWAVE = $09`.

### 5.2 Track / orderlist format

Per-channel track byte values:
```
$00       Loop marker (followed by loop destination byte)
$01–$7F   Pattern number to play
$80–$BF   Transpose downward  (V2: downward; V1 was opposite)
$C0–$FF   Transpose upward ($C0 = zero transpose)
```
Constraint: transpose cannot be immediately followed by loop. Combined 3-track total ≤ 256 bytes.

### 5.3 Pattern data format

4-column rows: `[note_byte] [cmd_byte] [dur_byte] [cmd_name — display only]`

**Note/keyon/keyoff byte:**
```
$00       End of pattern
$01       Execute command (no note)
$04*2=$08 Keyon (+++)
$08*2=$10 Keyoff (---)  — wait, see constants below
$0C*2=$18 = FIRSTNOTE (C-1)
$5F*2=$BE = LASTNOTE  (B-7)
$C0+      Duration flag (if high bit pair = $C0, this byte IS the duration)
```
Actual constants from source:
```
ENDPATT  = $00
CMD      = $01
KEYON    = $02*2 = $04
KEYOFF   = $04*2 = $08
FIRSTNOTE= $0C*2 = $18  (C-1)
LASTNOTE = $5F*2 = $BE  (B-7)
DUR      = $C0   (or-mask: indicates duration byte follows)
MAXDUR   = 65
```

**Command byte:** `$01–$7F` = normal command; `$81–$FF` = legato command (same command, ADSR/hardrestart/gate skipped; only table pointers set). `$00` = no change (continue prior command).

**Duration byte:** Only present when high two bits = $C0 (`dur & $C0 == $C0`). Range 3–65 decimal. If absent, last duration repeats. Pattern ends with $00 in note position.

### 5.4 Wavetable format (left/right column pairs)

Left column:
```
$00–$8F  Set waveform. Right = arpeggio ($00–$7F relative semitone; $8C–$DF absolute note)
$90–$BF  No waveform change; delay arpeggio by $00–$2F frames. Right = arpeggio.
$C0–$DF  Vibrato: speed $00–$1F encoded in low 5 bits. Right = depth.
$E0–$FE  Pitch slide: speed hi-byte $00–$1E. Right = speed lo-byte.
$FF      Jump. Right = destination (step index).
```
When slide reaches target pitch, execution jumps back to last waveform-set step. Vibrato continues indefinitely.

### 5.5 Pulse table format

Left column:
```
$01–$7F  Modulate pulse for $01–$7F frames. Right = signed mod speed (nybbles reversed in binary).
$80–$FE  Set pulse to right-side value.
$FF      Jump. Right = destination.
```
Pulse high byte stored only; written to both $D402 and $D403. Negative mod speed: in the native format, subtract 1 then nybble-reverse.

### 5.6 Filter table format

Left column:
```
$01–$7F  Modulate cutoff for $01–$7F frames. Right = signed mod speed.
$80–$FE  Set passband (left nybble–8), filter channel mask (right nybble of left), cutoff (right byte). Resonance = left nybble of left byte.
$FF      Jump. Right = destination.
```
Step 0 of the filter table is executed at song start.

### 5.7 Command (instrument) format

Per command (5 fields):
```
ADSR  (AD byte, SR byte)
Wv    (wavetable start pointer, 0 = leave unchanged)
Pu    (pulse table start pointer, 0 = leave unchanged)
Fl    (filter table start pointer, 0 = leave unchanged)
Name  (up to 9 chars, display only, not in gamemusic binary)
```
Legato mode (cmd $81–$FF): skips hardrestart, init frame waveform, auto-keyon, ADSR. Only table pointers are set.

Global settings (saved per song): hardrestart SR (`hrparam`, default $00), note init frame waveform (`firstwave`, default $09 = pulse+gate).

### 5.8 Packed binary (gamemusic) layout

The gamemusic module header (`NT_NUMFIXUPS = 21` fixup points):
```
Byte 0: wavetbl size
Byte 1: pulsetbl size
Byte 2: filttbl size
Byte 3: legatocmd size  (NT_ADDLEGATOCMD offset)
Byte 4: cmd size        (NT_ADDCMD offset — includes ADSR)
Byte 5: patt table size
```
Data sections in order (addresses filled in by `nt_newmusic` fixup engine):
1. Wave time table (`ntwavetbl`)
2. Wave note/arpeggio table (`ntnotetbl`)
3. Pulse time table (`ntpulsetimetbl`)
4. Pulse speed table (`ntpulsespdtbl`)
5. Filter time table (`ntfilttimetbl`)
6. Filter speed table (`ntfiltspdtbl`)
7. Cmd ADSR AD (`ntcmdad[cmdlen]`)
8. Cmd ADSR SR (`ntcmdsr[cmdlen]`)
9. Cmd wave pointer (`ntcmdwavepos[legatocmdlen]`)
10. Cmd pulse pointer (`ntcmdpulsepos[legatocmdlen]`)
11. Cmd filter pointer (`ntcmdfiltpos[legatocmdlen]`)
12. Pattern table lo (one per pattern)
13. Pattern table hi (one per pattern)
14. Song/subtune table (5 bytes per subtune: 2-byte track ptr, 0, ch1_end, ch2_end)
15. Pattern data (variable)
16. Orderlist/track data (variable)

The fixup engine (`nt_newmusic`) patches 21 absolute addresses inside the playroutine using this header + sequential section sizes. Called once per music data load. Uses only 2 ZP bytes (`nt_zpbase`, `nt_zpbase+1`).

### 5.9 Init / play entry points

```
nt_newmusic(A=lobyte, X=hibyte)  — call once after loading music data
nt_playsong(A=subtune_0–15)      — start a subtune
nt_playsfx(A=sfx_lo, X=sfx_hi, Y=chn_idx)  — SFX on channel (Y=0,7,14)
nt_music()                       — call each frame (VBI/raster interrupt)
```

**Rastertime claim:** "11 rasterlines max" for V1.x; V2.x readme doesn't give a hard figure but spider-j's CSDb comment says it is "great rastertime and RAM saver."

### 5.10 Playback optimisations (from readme)

- New note data read 3 frames before note starts; on that frame, slide/vibrato/pulse are skipped.
- Track data read 1 frame before note start (if necessary); pulse skipped in that frame.
- Executing a command without note: pulse + wavetable both skipped for 1 frame.

### 5.11 Sound effect (SFX) format

```
Byte 0: Sustain/Release
Byte 1: Attack/Decay
Byte 2: Pulsewidth (nybbles reversed: pulse $400 → stored as $04)
Bytes 3..N: Note,Wave pairs. Note: $8C–$DF (C-1–B-7). Wave: $01–$81.
             If waveform unchanged, wave byte omitted.
$00: End of SFX.
```
Priority: higher memory address SFX interrupts lower; ongoing SFX not interrupted unless higher priority.

### 5.12 Frequency table (from `nt2play.s`)

84 entries (C-1 to B-7), little-endian 16-bit:
```
C-1: $022D  C#-1: $024E  D-1: $0271 ... B-7: $FFFF
```
Access: `nt_freqtbl-24,y` where y = note_number*2 + note_offset.

---

## 6. NinjaTracker V1.x Technical Reference

Sources: `readme.txt`, `ntplay.s`, `src/ninjagam.s` (local: `tmp/ninjatracker_research/extracted/nt1/`)

Key differences from V2.x:

### 6.1 Track format (V1.x)

```
$00       Loop (followed by loop position)
$01–$7F   Sector (pattern) to play
$80–$BF   Transpose UPWARD
$C0–$FF   Transpose DOWNWARD
```
(Note: V1 transpose direction encoding is **opposite** to V2.)

Sector 00 reserved for song init; cannot be used in track data.
Transpose is conceptually: `(note + trans) & $7F` — so trans $FF = one halfstep down, $81 = one halfstep up.

### 6.2 Sector (pattern) format (V1.x)

3 columns: `[note/command] [wavetable_ptr/param] [duration]`

Notes range C-0 to F-7. Commands: `===` (Rest), `Wav`, `AD`, `SR`, `Flt`.
Duration minimum 2, maximum 65 (V1 min is 2, not 3 like V2).

### 6.3 Wavetable format (V1.x — 3 columns)

```
$00    Hardrestart note init  (next col: pulse init; next-next: filter init)
$01    Legato note init
$02    Set ADSR (2nd frame: also executes wave/note step below it)
$03–$8F  Waveform + note change. Right = note/arp. Next = pointer to next step.
$90    Note without waveform change
$91–$FF  Pitch slide (duration as negative: $FF–$91 = 1–111 frames)
```

3-byte steps: `[left] [right] [next_step_ptr]`. Step 00 is reserved (pitch slide uses it). Jump to step 00 in next-ptr = continue previous slide.

### 6.4 V1.02 Gamemusic sound effect format

```
Byte 0: Pulsewidth (nybbles reversed)
Byte 1: Attack/Decay
Byte 2: Sustain/Release
Bytes 3+: Notes ($8C–$DF = C-1–B-7) and waves ($01–$81). $00 = end.
```

Init: set ptr first, then write $01 to trigger flag. SFX addresses for channels at fixed offsets within the player (V1.02 specific, not compatible with V2 SFX API).

---

## 7. CSDb User Comments

### NT V2.04 (ID 119721)

- **hedning** (2013-06-19): "Oh, Cadaver! <3"
- **NecroPolo** (2013-06-20): "Thanks for the update!"
- **Yogibear** (2013-06-20): "Nice!"
- **spider-j** (2014-11-14): "Awesome native tracker. Made an intro tune with it recently. Maybe not the best choice for composing long tunes, but it's a great rastertime and RAM saver."
- **Hein** (2018-10-22): "Great tool with very clever restrictions. Will definitely experiment more with it and borrow some ideas."

### GT2NT2 V1.0 (ID 115448)

- **Yogibear** (2013-02-04): "Good work!"
- **cadaver** (2013-02-04): [response, text truncated in HTML fetch]

### NT MOD V2.04 (ID 152640)

- **Xiny6581** (2017-01-10): "Not bad at all! Must take a look into this tracker."
- **Yogibear** (2017-01-11): [asks about tune]
- **Fred** (2017-01-13): credits ARTIST: Yasuaki Fujita (Bunbun)
- Note in release: "playroutine wasn't changed / is fully compatible to the 'official' NT V2.04 release by Cadaver"

---

## 8. Pouet.net Findings

URL searched: https://www.pouet.net/search.php?what=ninjatracker&type=prods

Two entries found:

| Title | Group | Date | Type | Rating |
|-------|-------|------|------|--------|
| NinjaTracker V1.1 | Covert Bitops | 2004-01 | Demotool | 0.67 |
| Ninjatracker V2.0 | Covert Bitops | 2006-08 | Demotool | 1.00 |

No other NinjaTracker-specific entries found (productions using it are not separately indexed).

---

## 9. HVSC Coverage

The existing `research.md` in this directory notes: **97 tunes** in HVSC use NinjaTracker V2.x.

---

## 10. Local Files Downloaded

All in `/home/jtr/sidfinity/tmp/ninjatracker_research/`:

| File | Contents |
|------|---------|
| `ninjatr204.zip` | NT V2.04 full distribution (editor D64 + `nt2play.s` + full editor source) |
| `gt2nt2.zip` | GT2→NT2 converter V1.03 (source + binary + `nt2play.s` copy) |
| `ninjatrk_v1.zip` | NT V1.1 distribution (`ntplay.s` + editor D64 + source) |
| `ninja102.zip` | NT V1.02 (with gamemusic SFX support) |
| `goatninj.zip` | GT V1.x → NT V1.x converter V1.11 |
| `ninjatrMOD204.zip` | NT MOD V2.04 by spider-j (editor-only changes) |
| `extracted/nt204/` | Extracted NT V2.04 |
| `extracted/gt2nt2/` | Extracted GT2NT2 |
| `extracted/nt1/` | Extracted NT V1.1 |
| `extracted/nt102/` | Extracted NT V1.02 |
| `extracted/goatninj/` | Extracted GT1→NT converter |

Key source files of interest for decompiler work:
- `extracted/nt204/nt2play.s` — complete V2 playroutine (702 lines DASM)
- `extracted/nt204/src/nt2songdata.s` — all data section labels and sizes
- `extracted/nt204/src/ninjatr2.s` — all editor constants (MAX_SONGS etc.)
- `extracted/nt204/src/nt2var.s` — all variable names + relocation table structure
- `extracted/nt1/ntplay.s` — V1 playroutine (588 lines)
- `extracted/gt2nt2/gt2nt2src.c` — full binary module layout in `saventsong()`

---

## 11. Leads to Follow

1. **GitHub repos for MiniPlayer:** https://github.com/cadaver/miniplayer and https://github.com/cadaver/miniplayer2 — feature-stripped relatives, may clarify minimum required engine features.
2. **NT V2.03 CSDb page (ID 39571):** comments may contain technical discussion about "hifi" hardrestart style.
3. **Forum discussion on NT V2.04 (ID 119721):** https://csdb.dk/forums/?csdbentrytype=release&csdbentry=119721&entrytopic=1 — not fetched; may contain bug reports or format clarifications.
4. **HVSC SIDId config:** Cadaver's SIDId tool (`https://github.com/cadaver/sidid`) contains NinjaTracker signatures — cross-reference to confirm HVSC fingerprinting coverage.
5. **Covert Bitops tools page music section:** `https://cadaver.github.io/music.html` — may list tunes composed with NinjaTracker for eartest reference.
6. **Pokefinder archives:** `http://ftp.pokefinder.org/index.php?s=NinjaTracker` — mirrors of all CSDb releases, useful if CSDb download links die.
7. **NT V1.03 specifically (ID 7257):** first version with filter support in gamemusic mode (per goatninj readme: "effect 5 set filter — in editors that don't support it, such as NinjaTracker V1.03, shown as 'End'"). Fetch for clarification.
8. **GT2NT2 V1.03 CSDb entry:** not found on CSDb (the homepage zip is dated 2021 but no separate CSDb entry was located). Check cadaver.github.io changelog if any.
