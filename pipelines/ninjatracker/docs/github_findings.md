---
source_url: multiple (see per-section notes)
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops)
content_date: 2009-2013 (V1), 2013 (V2.04), V1.03 GT2NT2
reliability: primary
---

# NinjaTracker — GitHub & Open-Source Research Findings

## 1. Source Repositories

### 1.1 Official distribution (canonical)

- **URL**: https://cadaver.github.io/tools.html
- Downloads:
  - `tools/ninjatr204.zip` — NT V2.04 full distribution (95 KB)
  - `tools/ninjatrk.zip` — NT V1.1 full distribution
  - `tools/ninja102.zip` — NT V1.02 full distribution
  - `tools/gt2nt2.zip` — GT2→NT2 converter V1.03 (81 KB)
- **Both zips downloaded** to `tmp/ninjatracker_research/`
- All key sources extracted to `docs/src/`

### 1.2 GitHub fork: localhost/NinjaTracker

- **URL**: https://github.com/localhost/NinjaTracker (branch: `custom`, 8 commits)
- Language: Assembly (95.9%), C (3.8%), Makefile (0.3%)
- Root files: `nt2play.s` (the gamemusic player, DASM format), `readme.txt`, `example.prg`, `ins2nt2.exe`, `ninjatr2.d64`
- `src/` directory: full editor source (18 `.s` files + C utilities)

### 1.3 Cadaver's GitHub profile

- **URL**: https://github.com/cadaver
- 13 total repos; visible popular ones: turso3d, hessian, c64gameframework, siddump, miniplayer, oldschoolengine2
- **NO NinjaTracker repo** under cadaver's own account — the canonical distrib is via `cadaver.github.io`

## 2. Player Source Files — SAVED

All files saved with provenance header prepended after copy:

| Local path | Source | Description |
|---|---|---|
| `docs/src/nt2play_v204.s` | `ninjatr204.zip/nt2play.s` | V2.04 gamemusic player (DASM, 702 lines) |
| `docs/src/nt2player_editor_v204.s` | `ninjatr204.zip/src/nt2player.s` | Editor-embedded player (different layout) |
| `docs/src/nt2play_gt2nt2.s` | `gt2nt2.zip/nt2play.s` | GT2NT2-bundled player (21 KB, slightly different) |
| `docs/src/ntplay_v1.s` | `ninjatrk_v1.zip/ntplay.s` | V1.1 player (18 KB, 5 zeropage bytes) |
| `docs/src/nt2songdata_v204.s` | `ninjatr204.zip/src/nt2songdata.s` | Song data layout definitions |
| `docs/src/nt2var_v204.s` | `ninjatr204.zip/src/nt2var.s` | Editor variable / memory map |
| `docs/src/gt2nt2.c` | `gt2nt2.zip/gt2nt2.c` | GT2→NT2 converter (1918 lines, C) |
| `docs/src/readme_v204.txt` | `ninjatr204.zip/readme.txt` | V2.04 format spec + full docs |
| `docs/src/readme_v1.txt` | `ninjatrk_v1.zip/readme.txt` | V1.1 docs |
| `docs/src/readgam_v1.txt` | `ninjatrk_v1.zip/readgam.txt` | V1 gamemusic mode docs |
| `docs/src/readme_gt2nt2.txt` | `gt2nt2.zip/readme.txt` | GT2NT2 limitations + usage |

**✅ CONFIRMED: nt2play.s saved to docs/src/ as `nt2play_v204.s`**

## 3. NT2 Binary File Format (from gt2nt2.c `saventsong`)

The `.sng` file format is a **run-length encoded** stream of blocks. The magic bytes `'N', '2'` appear first, then compressed sections in this order:

```
[N][2]
[ntwavetbl]       255 bytes  — wavetable left column
[ntnotetbl]       255 bytes  — wavetable right column (note/arpeggio)
[ntpulsetimetbl]  255 bytes  — pulse table timing column
[ntpulsespdtbl]   255 bytes  — pulse table speed column
[ntfilttimetbl]   255 bytes  — filter table timing column
[ntfiltspdtbl]    255 bytes  — filter table speed column
[ntpatterns]      127 × 192 bytes  — all patterns (padded to MAX_NTPATTLEN)
[nttracks]        16 × 256 bytes   — all song orderlists (16 songs)
[ntcmdad]         127 bytes  — command attack/decay
[ntcmdsr]         127 bytes  — command sustain/release
[ntcmdwavepos]    127 bytes  — command wave table pointer
[ntcmdpulsepos]   127 bytes  — command pulse table pointer
[ntcmdfiltpos]    127 bytes  — command filter table pointer
[ntcmdnames]      127 × 10 bytes   — command names (padded with spaces)
[ntsonglen]       16 × 3 bytes     — song track lengths (3 channels)
[nttbllen]        3 bytes    — table lengths [wave, pulse, filt]
[ntcmdlen]        1 byte     — number of commands used
[nthrparam]       1 byte     — hardrestart SR value (default $00)
[ntfirstwave]     1 byte     — init frame waveform (default $09)
```

**RLE encoding**: byte `$BF` is the escape. `$BF <val> <count>` means `<val>` repeated `<count>` times. `$BF $BF $01` encodes a literal `$BF`.

**Constants** (from `gt2nt2.c` + `nt2play.s`):
```c
MAX_NTSONGS    = 16
MAX_NTPATT     = 127
MAX_NTCMD      = 127
MAX_NTCMDNAMELEN = 9
MAX_NTPATTLEN  = 192
MAX_NTSONGLEN  = 256
MAX_NTTBLLEN   = 255
NT_ENDPATT     = 0x00
NT_CMD         = 0x01
NT_KEYON       = 0x04   (0x02 * 2)
NT_KEYOFF      = 0x08   (0x04 * 2)
NT_FIRSTNOTE   = 0x18   (0x0c * 2)
NT_LASTNOTE    = 0xBE   (0x5f * 2)
NT_DUR         = 0xC0
NT_MAXDUR      = 65
```

## 4. Pattern Data Layout (from readme + gt2nt2.c)

Each pattern row is **4 columns** (note, command, duration, name-display):

```
Col 0: Note/Keyoff/Keyon
  0x00         = end of pattern
  0x01         = only command (no note)
  0x04         = keyon (+++)
  0x08         = keyoff (---)
  0x18-0xBE    = note C-1 through B-7 (2 per semitone step)
  odd bit      = "command present" flag (LSB of the raw byte)

Col 1: Command number (01-7F = normal, 81-FF = legato)
Col 2: Duration ($C0-$FF range: top 2 bits set = duration, value+$C0 = raw byte)
Col 3: (display only, not in binary)
```

Pattern decode: `raw_byte >> 1` = note index; `raw_byte & 1` = has new command.
Duration byte ≥ $C0 means this row sets a new duration (stored as `$C0 | (dur-1)`?).

## 5. Track (Orderlist) Format

```
00 <pos>    = loop to position pos
01-7F       = pattern number (1-indexed)
80-BF       = transpose downwards (value - $C0 gives signed offset)
C0-FF       = transpose upwards (C0 = 0)
```

Max 16 songs × 3 channels × 256 bytes each.
Transpose cannot be followed by loop; combined per-subtune track length ≤ 256 bytes.

## 6. Table Formats

### Wavetable (left col = ntwavetbl, right col = ntnotetbl)

```
left 00-8F  = set waveform; right = arpeggio (00-7F relative, 8C-DF absolute)
left 90-BF  = no waveform, delay arpeggio by (left-0x90) frames
left C0-DF  = vibrato, speed = (left & 0x1F), right = depth
left E0-FE  = slide, speed hi = (left - 0xE0), right = speed lo
left FF     = jump; right = destination (00 = stop)
```

### Pulse table (left = ntpulsetimetbl, right = ntpulsespdtbl)

```
left 01-7F  = modulate pulse for N frames, right = signed speed
left 80-FE  = set pulse to right-side value
left FF     = jump; right = destination
```

### Filter table (left = ntfilttimetbl, right = ntfiltspdtbl)

```
left 01-7F  = modulate cutoff for N frames, right = signed speed
left 80-FE  = set passband (left nybble - 8), channels (right nybble), cutoff = right
left FF     = jump; right = destination
```

When set filter: resonance = left nybble of left byte.

## 7. Command (Instrument) Format

Each command = 5 fields:
```
AD    1 byte  attack/decay
SR    1 byte  sustain/release
Wave  1 byte  wavetable start position (0 = unchanged)
Pulse 1 byte  pulse table start position (0 = unchanged)
Filt  1 byte  filter table start position (0 = unchanged)
```

Command used in legato mode (cmd# 81-FF): skips hard-restart, ADSR, gate-on init.
Only table pointers are updated in legato mode.

## 8. Playback Architecture (from nt2play.s V2.04)

### Memory / relocation model

The player uses a **fixup table** (`NT_NUMFIXUPS = 21`) — on `NT_NEWMUSIC`, 21 hardcoded
addresses inside the player code are rewritten to point into the loaded music data blob.
The music data blob starts at an arbitrary address (passed as A/X pair); its internal
structure is computed via the header's 6-byte size fields (`NT_HEADERLENGTH = 6`).

The `NT_ADDWAVE/$PULSE/$FILT/$CMD/$LEGATOCMD/$PATT/$ADDZERO` constants give the section
offsets within the blob.

### Zeropage

V2: 2 bytes (`nt_zpbase` default `$FC`, i.e. `$FC-$FD`)
V1: 5 bytes (`musiczpbase` = `$FB-$FF`)

### Channel state (X-indexed, stride 7)

For voices at X=0, 7, 14:

```
nt_chnpattpos,x    — current position within pattern
nt_chncounter,x    — duration countdown
nt_chnnewnote,x    — pending note
nt_chnwavepos,x    — current wavetable position
nt_chnpulsepos,x   — current pulse table position
nt_chnwave,x       — current waveform byte
nt_chnpulse,x      — current pulse value (hi byte)
nt_chngate,x       — gate mask ($FF = open, $FE = closed)
nt_chntrans,x      — current transpose offset
nt_chncmd,x        — current command index
nt_chnsongpos,x    — current orderlist position
nt_chnpattnum,x    — current pattern number
nt_chnduration,x   — current note duration
nt_chnnote,x       — current note (×2, freq table index)
nt_chnfreqlo,x     — current SID freq lo byte
nt_chnfreqhi,x     — current SID freq hi byte
nt_chnwavetime,x   — wavetable delay / vibrato state
nt_chnpulsetime,x  — pulse modulation timer
nt_chnsfx,x        — SFX active flag / frame counter
nt_chnsfxlo,x      — SFX data pointer lo
nt_chnsfxhi,x      — SFX data pointer hi / nt_chnwaveold
```

### Frequency table

96 entries (C-1 to B-7, same as shown in both V1 + V2):
```
$022D, $024E, $0271, ... $F820, $FFFF
```
Table is 1-indexed internally (accessed as `nt_freqtbl-24,y` for 2-byte words).

### Frame execution order

1. Init check (if initsongnum ≥ 0: reset state, load song table)
2. Filter execution (cutoff modulation, $D416/$D417/$D418)
3. Channel 0 exec (X=0)
4. Channel 1 exec (X=7)
5. Channel 2 exec (X=14)

Per-channel order within `nt_chnexec`:
- Increment duration counter; if 0: get new pattern row
- If counter == 2: reload from duration, check for new note
- Pulse execution (`nt_pulseexec`)
- Wave execution (`nt_waveexec`)
- Write `nt_chnwave & nt_chngate` to `$D404,x`

### Hard restart (V2)

2 frames: frame 1 sets gate=$FE, SR=`NT_HRPARAM` ($00 default), wave=`NT_FIRSTWAVE` ($09).
V2.03+: 2 frames + 1 silent frame ("hifi" style).

### SFX priority

SFX at higher memory address preempts lower. SFX data format:
```
SR, AD, PW, [note,wave pairs...], $00
```

### Key playback timing note

Pattern data is read **3 frames before note starts**. On that pre-read frame:
slide, vibrato, and pulse are all skipped.
Track data read happens **1 frame before note start** if needed (pulse skipped that frame).

## 9. V1 vs V2 Differences

| Feature | V1.x | V2.x |
|---|---|---|
| Zeropage | 5 bytes ($FB-$FF) | 2 bytes ($FC-$FD) |
| Commands/instruments | Separate concepts | Unified "commands" |
| Tables | Single-column (or differently structured) | Two-column (left/right) |
| Slide | Continuous portamento | Stops at target pitch; returns to last wave step |
| Hard restart | 1 frame | 2 frames + 1 silent (V2.03+) |
| Duration range | unknown | 3-65 |
| Songs | different limit | 16 |
| Relocation API | `RELOCATEMUSIC` + `PLAYTUNE` | `NT_NEWMUSIC` + `NT_PLAYSONG` |
| Fixups | Full relocation table, 5 ZP bytes | 21 fixups, 2 ZP bytes |

V1 player (`ntplay.s`) uses `musiczpbase` = `$FB`. Header = 5 bytes for table-length prefix.
V1 also reads from a `musicarea` structure with `REL_*` constants for each section.

## 10. GT2NT2 Converter (V1.03) — Format Insights

Source: `docs/src/gt2nt2.c` (1918 lines, Cadaver 2013)

Key conversions that reveal NT2 semantics:
- GT2 instruments → NT2 commands (AD+SR → ntcmdad/sr; wave/pulse/filt ptrs mapped)
- GT2 wavetable commands mapped: waveforms stay; speed commands → slide entries
  (`ntwavetbl[pos] = (speed >> 8) | 0xE0`, right = speed low byte)
- GT2 vibrato (cmd 4) → NT2 wavetable delay entries (`$90-$BF`) + vibrato step
- Toneportamento: uses fake high/low note targets when no explicit dest
- Unsupported: octave 0, filter resonance ctrl alone, wavetable commands, cmd 7/C/D/E

## 11. HVSC Coverage

From `hvsc84.csv`:
- NT V2: 93 SIDs in HVSC
- NT V1: 18 SIDs in HVSC

## 12. SID Identifier (sidid)

HVSC sidid uses a pattern-match database. NinjaTracker is identified by the
characteristic freq table signature (`$022D`, `$024E`, ..., `$FFFF`) at a fixed offset.

## 13. Other Tools

- **goatninj.c** (2003, `tmp/ninjatracker_research/goatninj.zip`): Earlier GoatTracker→NinjaTracker V1.x converter. Predates GT2NT2. 30 KB C source.
- **ins2nt2.exe**: GoatTracker instrument → NT2 SFX converter (C source in `ninjatr204.zip/src/ins2nt2.c`)
- **Ninjaforce convert tool**: http://www.ninjaforce.com/html/ninjatracker_convert.php (separate project, not inspected)

## Leads to Follow

1. **Gamemusic binary format** — the `gamemusic.bin` / `readgam.txt` in V1 describe the "gamemusic mode" headerless binary format (without player). Read `docs/src/readgam_v1.txt` for the V1 header layout. V2 gamemusic format is described inline in `nt2play.s` (the fixup mechanism IS the relocation format).
2. **nt2packer.s** — the editor's packer/relocator source (in `ninjatr204.zip/src/`) — reads the raw song data and writes the packed binary. Cross-reference with `saventsong` in gt2nt2.c to confirm the on-disk format.
3. **goatninj.c** — the earlier V1 converter; may reveal V1 data-format differences not obvious from the V1 player source alone.
4. **CSDb release #7206** — the NT V2.0 release NFO at https://www.pouet.net/prod_nfo.php?which=26206 — worth fetching for changelog + original release notes.
5. **SIDFactory II** — check if it has NinjaTracker import/export (github.com/SIDFactoryII); not yet inspected.
6. **DeepSID** — web-based SID player with engine annotations; may have NT-specific metadata.
7. **The nt2songdata.s defines** `savesongstart`/`savesongend` — the exact editor-internal save region. Cross this with `saventsong` order to confirm field offsets precisely.
