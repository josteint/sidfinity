---
source_url: local: pipelines/ninjatracker/docs/ + tmp/ninjatracker_research/ + web searches
fetched_via: direct
fetch_date: 2026-06-17
author: synthesized from Cadaver (Lasse Öörni) primary sources + web
content_date: 2002–2013 (primary sources); 2026-06-17 (synthesis)
reliability: primary
---

# NinjaTracker — Research Findings

Primary sources in hand: full distribution archives for NT V1.02 and V2.04, GT2NT2 V1.03
converter source, the canonical player `nt2play.s`, the editor source tree, and the
Cadaver tools-page text. Everything below is derived from those sources unless explicitly
marked "web search" or "forum."

---

## Overview

NinjaTracker (NT) is a minimal native C64 SID tracker and gamemusic player by **Lasse Öörni
("Cadaver")** of **Covert Bitops**. Goal: produce usable in-game music with the smallest
possible rastertime and memory footprint — smaller and faster than GoatTracker at the cost
of a reduced feature set.

### Version history

| Version | CSDb ID | Date | Notes |
|---------|---------|------|-------|
| V1.0 | 7206 | 2002-10-31 | First release; gamemusic version (ntplay.s) |
| V1.02 | — | 2002-11 | Gamemusic sound-effect capability; ins2nt2 utility |
| V1.1 | — | — | Minor update; also on Covert Bitops tools page |
| V2.0 | 39374 | 2006-08-30 | Rewrite: commands as instruments, 2-column tables, smart slide |
| V2.01 | — | — | Gamemusic SFX optimized; ins2nt2 updated |
| V2.02 | — | — | Hardrestart 2 frames default; ZP use reduced to 2 bytes |
| V2.03 | — | — | "Hifi" hardrestart (2fr + 1 silent); duration range 3-65; slide goes to last waveform step |
| V2.04 | 119721 | 2013-06-19 | Reset transpose on subtune-start-from-beginning; current canonical |
| MOD V2.04 | 152640 | 2017-01-10 | Spider Jerusalem; editor UX tweaks only; **player unchanged/fully compatible** |

**Related tools:**
- **GT2NT2 V1.03** — GoatTracker 2 → NinjaTracker 2 converter (C source included)
- **ins2nt2** — GoatTracker 1.x/2.x instrument → NT2 sound-effect converter
- **MiniPlayer / MiniPlayer 2** — Cadaver's 9-rasterline derivative, NT1-inspired, GitHub:
  cadaver/miniplayer and cadaver/miniplayer2

**HVSC coverage (HVSC #84):** 93 NinjaTracker_V2.x SIDs + 18 NinjaTracker_V1.x SIDs = **111 total**.
Key composers: Cadaver (Hessian, Fight_the_Machine), Sarah Jane Avory (Zeta_Wing,
Neutron, Briley_Witch_Chronicles, Soul_Force), Aomeba (AUX64, Hi_Five, Lucky).
Games: Hessian, Sam's Journey, Zeta Wing.

---

## Data Model

### V2.x — Complete Format Specification (from player source + packer + GT2NT2 source)

#### Global limits

| Constant | Value | Meaning |
|----------|-------|---------|
| MAX_SONGS | 16 | Subtunes per song file |
| MAX_PATT | 127 | Patterns (1–127) |
| MAX_CMD | 127 | Commands/instruments (1–127) |
| MAX_PATTLEN | 192 | Max bytes per pattern |
| MAX_SONGLEN | 256 | Max bytes per track per subtune |
| MAX_TBLLEN | 255 | Max entries per table |
| MAX_CMDNAMELEN | 9 | Command name string length |
| NT_FIRSTNOTE | $18 (=$0c*2) | Lowest note value in internal encoding |
| NT_DUR | $C0 | Duration flag in pattern |
| NT_MAXDUR | 65 | Maximum note duration in frames |
| MIN_DUR | 3 | Minimum note duration in frames |

#### .nt2 editor-save binary format (from GT2NT2 `saventsong`)

The disk-save format starts with a 2-byte magic `'N','2'` followed by full fixed-size tables.
All sizes are the *maximum* allocation, not the used portion (the editor tracks used lengths
separately in `nttbllen[3]` + `ntcmdlen`):

```
Offset    Size      Contents
0         2         Magic: 'N' 'Z'   (from GT2NT2; native editor uses 'N' '2')
2         256       ntwavetbl       (wave table LEFT column, 255 entries + terminator)
258       256       ntnotetbl       (wave table RIGHT column = arpeggio/note)
514       256       ntpulsetimetbl  (pulse table LEFT column)
770       256       ntpulsespdtbl   (pulse table RIGHT column = speed)
1026      256       ntfilttimetbl   (filter table LEFT column)
1282      256       ntfiltspdtbl    (filter table RIGHT column = speed)
1538      24384     ntpatterns      (127 patterns × 192 bytes)
25922     4096      nttracks        (16 subtunes × 256 bytes)
29018     127       ntcmdad         (command AD bytes)
29145     127       ntcmdsr         (command SR bytes)
29272     127       ntcmdwavepos    (command wave table pointer)
29399     127       ntcmdpulsepos   (command pulse table pointer)
29526     127       ntcmdfiltpos    (command filter table pointer)
29653     1270      ntcmdnames      (127 × 10-byte null-terminated names)
30923     48        ntsonglen       (16 × 3 bytes: track lengths V1,V2,V3)
30971     3         nttbllen        (used wave/pulse/filter table lengths)
30974     1         ntcmdlen        (number of commands used)
30975     1         nthrparam       (hardrestart S/R byte, default $00)
30976     1         ntfirstwave     (init-frame waveform, default $09)
```
Total: ~30977 bytes (fixed; packer output is much smaller).

#### Gamemusic binary module header (from `nt2var.s` `gamedatastart`)

When packed in Gamemusic mode the data blob starts with a **6-byte header**
(`NT_HEADERLENGTH = 6`), followed by compacted data sections. The 6-byte header:

```
Byte 0: gamewavetblsize   — number of used wave table entries
Byte 1: gamepulsetblsize  — number of used pulse table entries
Byte 2: gamefilttblsize   — number of used filter table entries
Byte 3: gamecmdsize       — number of full commands (with ADSR)
Byte 4: gamelegatocmdsize — number of legato commands (only table ptrs, no ADSR)
Byte 5: gamepatttblsize   — number of patterns (pattern table entry count)
```

After the header the `nt_newmusic` fixup routine (`NT_NUMFIXUPS = 21` fixup entries)
patches all absolute addresses inside the player code at load time, so the module can
sit at any address. The fixup table uses `NT_ADD*` offsets to navigate from the
blob base to each data section:

```
NT_ADDWAVE      = $00  → wave table (left) starts at blob+6
NT_ADDPULSE     = $04  → pulse table
NT_ADDFILT      = $08  → filter table
NT_ADDCMD       = $0c  → command ADSR table
NT_ADDLEGATOCMD = $10  → legato command table pointers
NT_ADDPATT      = $14  → pattern address table
NT_ADDZERO      = $80  → zero-offset (songdata, tracks)
```

The data sections in the packed blob after the 6-byte header follow the same order as
`prsavecommon` in the packer:

```
[wave_left × N] [wave_right × N]       — N = gamewavetblsize
[pulse_left × N] [pulse_right × N]     — N = gamepulsetblsize
[filt_left × N] [filt_right × N]       — N = gamefilttblsize
[cmd_AD × M]                           — M = gamecmdsize (attack/decay bytes)
[cmd_SR × M]                           — M = gamecmdsize (sustain/release bytes)
[cmd_wavepos × L]  [cmd_pulsepos × L]  — L = gamelegatocmdsize
[cmd_filtpos × L]
[patt_lo_tbl × P] [patt_hi_tbl × P]   — P = gamepatttblsize (pattern address table)
[song_lo × S] [song_hi × S] [song_len_V1,V2,V3 × S] — S = lastsong+1
[pattern data, packed end-to-end]
[track data for each subtune, each track]
```

#### Player API (V2.x `nt2play.s`)

```
nt_newmusic   A=lo, X=hi of musicdata blob → patches all internal addresses
nt_playsong   A=subtune number (0-15)       → queues init for next frame
nt_playsfx    A=lo, X=hi of sfx data, Y=channel_index (0,7,14) → plays SFX
nt_music      (no params)                   → call each frame from interrupt
```

ZP usage: **2 consecutive bytes** chosen at relocation time (`nt_zpbase` = default $FC/$FD).
The player also uses X as a channel index (0=$D400, 7=$D407, 14=$D40E).

#### Track / orderlist format (V2.x)

Each subtune has 3 tracks. Each track is a variable-length byte stream ending with a
loop entry. Combined length of all 3 tracks for a subtune ≤ 256 bytes.

| Byte value | Meaning |
|------------|---------|
| $00 | Loop marker (followed by 1 byte: loop-to position in this track) |
| $01–$7F | Pattern number to play |
| $80–$BF | Transpose downward (value $80 = –$40 semitones … $BF = –$01) |
| $C0–$FF | Transpose upward ($C0 = 0, $FF = +$3F semitones) |

Constraint: transpose cannot be immediately followed by a loop byte.
The current transpose is applied to all notes until the next explicit transpose.

#### Pattern format (V2.x)

Patterns are variable-length; each row encodes up to 3 bytes. Terminator = $00.

Each "row" consists of:

1. **Note/control byte** (always present):
   - $00 = end of pattern
   - $01 = command without note (cmd-exec-only; no SID gate / note)
   - $04 ($02×2) = key-on (gate bit set, no new note frequency)
   - $08 ($04×2) = key-off (gate bit cleared)
   - $18–$BE = note (NT_FIRSTNOTE=$18 through NT_LASTNOTE=$BE=$5F×2)
   - The low bit of the note byte indicates whether a **command byte follows**
   - Bit 7 of note: if set AND bit 0 set → this is a new command assignment

2. **Command byte** (present when bit 0 of note byte is set):
   - $01–$7F = command number (normal mode: triggers hardrestart + ADSR)
   - $81–$FF = command number in **legato mode** (cmd AND $7F; skips hardrestart, ADSR, auto-keyon)

3. **Duration byte** (present when ≥ $C0 in the raw stream):
   - $C0–$FF = duration value, actual duration = byte - (some base). Range 3–65 frames.
   - If absent, last-used duration carries forward.
   - If command-only row (no note), both pulse and wave table execution are skipped for 1 frame.

Note: "A note without a command number will use the last used command." The `nt_chncmd`
per-voice state carries the last command.

#### Command / instrument format (V2.x)

A command is both an instrument (when used with a note) and a pattern command (without note).
Each command stores:

| Field | Size | Notes |
|-------|------|-------|
| AD | 1 byte | Attack (high nybble) + Decay (low nybble) |
| SR | 1 byte | Sustain (high nybble) + Release (low nybble) |
| wave_table_ptr | 1 byte | Index into wave table (1-based; 0 = leave current running) |
| pulse_table_ptr | 1 byte | Index into pulse table (0 = leave current) |
| filt_table_ptr | 1 byte | Index into filter table (0 = leave current) |
| name | 9+1 bytes | Editor display name (editor only, not in packed module) |

**Legato mode** (command numbers $81–$FF in pattern): skips hardrestart, ADSR setup,
auto-keyon, and init-frame waveform. Only sets table pointers.

Optimization: the packer can omit the ADSR data of commands that are **only ever used in
legato mode**, if they are placed at the end of the command list. The split point is
tracked as `lastcmd` (full commands) vs `lastlegatocmd` (up to here for table-ptr-only
commands).

#### Wave table (V2.x) — two columns

Left column (function selector) + Right column (parameter). Entries are 1-indexed;
index 0 = stop execution. Jump destination 00 also stops execution.

| Left byte range | Function | Right byte |
|----------------|----------|------------|
| $00–$8F | **Set waveform** (SID $D404 register value) | Arpeggio: $00–$7F = relative semitone offset; $8C–$DF = absolute note |
| $90–$BF | **No waveform change; delay arpeggio** by (left - $90) = 0–47 frames | (ignored for arpeggio timing) |
| $C0–$DF | **Vibrato** with speed = (left - $C0) = 0–31 | Depth |
| $E0–$FE | **Slide** (toneportamento) speed hi = (left - $E0) = 0–30 | Speed lo byte |
| $FF | **Jump** (unconditional) | Destination index (1-based) |

The wave table is split in storage as two parallel arrays:
- `ntwavetbl` / `nt_wavetbl` — left column (function)
- `ntnotetbl` / `nt_notetbl` — right column (arpeggio/note/depth/speed-lo)

**Slide behaviour (V2.03+):** when the target pitch is reached, execution jumps to the
last "set waveform" step that was executed before the slide started (`nt_chnwaveold`).
Prior to V2.03, slide returned to a delayed-arpeggio step instead.

**Vibrato behaviour:** runs indefinitely once started. To delay vibrato, precede it with
a delayed-arpeggio step.

**New note read lookahead (V2.x):** pattern data is read 3 frames before the note starts.
On that lookahead frame, slide, vibrato, and pulse are skipped. Track data (if needed)
is read 1 frame before note start (pulse skipped that frame too).

#### Pulse table (V2.x) — two columns

`ntpulsetimetbl` (left) + `ntpulsespdtbl` (right).

| Left byte range | Function | Right byte |
|----------------|----------|------------|
| $01–$7F | **Modulate** pulse for 1–127 frames | Signed speed (added to current PW each frame) |
| $80–$FE | **Set pulse** to this value (pulse = right byte; both $D402 and $D403 are written) | Pulse value |
| $FF | **Jump** | Destination index |

Note: NinjaTracker stores pulse as a single 8-bit value written simultaneously to both
`$D402` (PW lo) and `$D403` (PW hi). This means pulse resolution is 1/256 of full range
(coarser than GoatTracker which uses 12-bit). This is the "reversed nybbles" convention:
pulse $400 is stored as $04 in the NT table, i.e., the byte is the PW high byte and it
goes to both lo and hi. GT2NT2 uses only the high 4 bits of GT's pulse speed values.

#### Filter table (V2.x) — two columns

`ntfilttimetbl` (left) + `ntfiltspdtbl` (right).

| Left byte range | Function | Right byte |
|----------------|----------|------------|
| $01–$7F | **Modulate cutoff** for 1–127 frames | Signed speed (added to current cutoff) |
| $80–$FE | **Set passband+routing+cutoff**: left nybble sets resonance ($D417 high nybble), low nybble of left is the passband ($70 bits) + channel routing (low 3 bits of left); right byte sets cutoff ($D416) | Cutoff value |
| $FF | **Jump** | Destination index |

Filter execution is **global** (one filter state, shared across all 3 voices), unlike
GoatTracker which has per-voice filter pointers. The filter table pointer (`nt_filtpos`)
is set by whichever command on any voice last assigned a non-zero filter pointer.

The global master volume write: `ORA #$0F; STA $D418`. The `#$0F` can be changed to
adjust volume. This write happens every frame regardless (fixed in the filter section).

#### Frequency table

The player has a **built-in frequency table** (`nt_freqtbl`): 84 entries covering C-1 to
B-7 (7 octaves × 12 semitones = 84 notes), stored as 16-bit little-endian words.
Note index 0 ($00) in the arpeggio right column means "use current pitch / slide-done."
Note range in internal encoding: `NT_FIRSTNOTE=$18` through `NT_LASTNOTE=$BE` (as doubled
values in the pattern stream).

Frequency table values (first octave, C-1 through B-1):
```
$022D, $024E, $0271, $0296, $02BE, $02E8,
$0314, $0343, $0374, $03A9, $03E1, $041C
```

#### Hardrestart (V2.x)

Configurable per-song:
- `hrparam` (default $00): the SR value written to `$D406` on hardrestart
- `firstwave` (default $09): waveform written on the "init frame" of a new note
  (`$09` = sawtooth | testbit | gate-off; `$01` = triangle | gate-off without testbit,
  for brighter noise attack)

Hardrestart sequence (V2.03+, "hifi" style, 3-frame):
1. Frame N–2: write `$FE` to gate (clears gate) and `hrparam` to `$D406`
2. Frame N–1: no new write (silent frame)
3. Frame N (note start): write `firstwave` ($09) to `$D404`, then AD/SR/waveform

In legato mode this entire sequence is skipped.

#### Sound effect format (V2.x)

SFX data format (from `nt_playsfx` docs in `nt2play.s`):

```
Byte 0: Sustain/Release
Byte 1: Attack/Decay
Byte 2: Pulsewidth (high byte, written to both $D402/$D403)
Byte 3+: Note,Wave pairs; note in $8C–$DF range; wave $01–$81
          If waveform unchanged, wave byte may be omitted (just note byte)
Terminator: $00
```

Priority system: a SFX at higher memory address can interrupt a lower-address SFX, but
not vice versa. The check is `CMP + SBC` on the address, so "higher address = higher
priority."

Channel index for SFX: Y = 0 (voice 1), 7 (voice 2), or 14 (voice 3).

#### ZP variables per channel (V2.x)

The player uses two arrays of 21 bytes each starting at `nt_chnpattpos` / `nt_chngate`
and a third array at `nt_chnfreqlo`. Each array is indexed as `array,x` where x = 0, 7,
or 14. Fields:

```
Offset from base:
0:  chnpattpos    — current position in current pattern
1:  chncounter    — frame countdown until next note
2:  chnnewnote    — buffered note (pending, loaded 3fr early)
3:  chnwavepos    — current wave table position
4:  chnpulsepos   — current pulse table position
5:  chnwave       — current SID waveform byte (shadow)
6:  chnpulse      — current pulse width (shadow)

(stride = 7; three channels packed at offsets 0, 7, 14)

Second array (nt_chngate base):
0:  chngate       — gate mask ($FF = note on, $FE = gate off)
1:  chntrans      — current transpose value ($FF = 0)
2:  chncmd        — last used command number
3:  chnsongpos    — position in track (orderlist) for this channel
4:  chnpattnum    — current pattern number
5:  chnduration   — current note duration
6:  chnnote       — current pitch (index into freq table ×2)

Third array (nt_chnfreqlo base):
0:  chnfreqlo     — current freq lo (shadow)
1:  chnfreqhi     — current freq hi (shadow)
2:  chnwavetime   — vibrato accumulator / wave delay counter
3:  chnpulsetime  — pulse modulation frame countdown
4:  chnsfx        — SFX state (0=no sfx, 1=init, 2=hr, ≥3=main)
5:  chnsfxlo      — SFX data pointer lo
6:  chnsfxhi / chnwaveold — SFX pointer hi / last-waveform-before-slide index
```

---

### V1.x — Format Overview (from `ninjagam.s` / `ntplay.s`)

V1.x has a different, simpler design. Key differences from V2.x:

1. **No commands** — instruments are defined separately as ADSR+wave+pulse+filter entries;
   there is no dual-role command/instrument object.
2. **Single-column tables** — wave, pulse, and filter tables use index-with-terminator
   sequences, not two-column left/right structure.
3. **No legato mode.**
4. **Note encoding** in V1 is a direct enum ($01=$C0, $02=$C#0 … $5F=REST, $60=SND).
   Octave 0 is present in V1; V1.02 gamemusic version removes octave 0.
5. **Track format** is the same concept: $00=LOOP, $80=TRANS; rest = pattern number.
6. **Player API (V1 gamemusic):**
   - Init song: `STA initsongnum+1` (value = song number + 1)
   - Play SFX (V1.02): direct memory write to channel SFX pointers at fixed offsets
   - Play frame: `JSR <baseadr>` (one call per frame)
7. **ZP usage:** V1 uses 5 ZP addresses (`musiczpbase` = $FB–$FF); V2 uses only 2.
8. **Binary header (V1 gamemusic):** 5-byte header:
   ```
   musicdata+0 = songtable len (lo/2 bytes)
   musicdata+1 = patttable len (lo/2 bytes)
   musicdata+2 = wavetable len
   musicdata+3 = pulsetable len
   musicdata+4 = filttable len
   ```
   Relocation uses `REL_*` constants ($00–$0B) in a fixup table (`reladdtbl`), not the
   NT2 fixup scheme.

**V1 SFX data format** (from `readgam_v1.txt`):
```
Byte 0: Pulsewidth (nybbles reversed)
Byte 1: Attack/Decay
Byte 2: Sustain/Release
Byte 3+: Note/Wave pairs: note in $8C–$DF, wave $01–$81
Terminator: $00
Warning: do not use maximum sustain or release ($F) — ADSR will bug.
```

Note/wave pair encoding in V1 is byte-level same as V2.

---

## CSDb Findings

| Version | CSDb ID | URL | Downloads |
|---------|---------|-----|-----------|
| V1.0 | 7206 | https://csdb.dk/release/?id=7206 | 964 |
| V2.0 | 39374 | https://csdb.dk/release/?id=39374 | — |
| V2.04 | 119721 | https://csdb.dk/release/?id=119721 | 1118 |
| MOD V2.04 | 152640 | https://csdb.dk/release/?id=152640 | — |

Download link for V2.04: `http://csdb.dk/getinternalfile.php/118068/ninjatr204.zip`
Download link for V1.0: `http://csdb.dk/getinternalfile.php/29747/ninjatrk.zip`

CSDb V2.04 user comments (paraphrased):
- "Great tool with very clever restrictions"
- "Awesome native tracker. Not the best for long tunes, but great rastertime and RAM saver."
- "Nice!" / "Thanks for the update!"

CSDb release type: **C64 Tool** for all versions. Code credit: Cadaver of Covert Bitops.

---

## Forum / Wiki Findings

### Lemon64 thread — NinjaTracker V2.0 (t=20873)
URL: https://www.lemon64.com/forum/viewtopic.php?t=20873
- V2.0 described as "totally rewritten" vs V1.x
- Cadaver: "the playroutine is slower than the previous versions" (for V2.0; later
  V2.02 had "slightly slower and bigger playroutine" vs V2.01)
- V2.03 hardrestart: "hides the fluctuation of the attack by using silent first frame
  of note" — 2fr+1silent "hifi" style
- No deep byte-level format discussion; social/announcement thread.

### Lemon64 thread — Minimal music player NT1-style (t=67012)
URL: https://www.lemon64.com/forum/viewtopic.php?t=67012
This thread is about Cadaver's **MiniPlayer** (not NT itself) but reveals design intent:
- Target: **max 9 rasterlines**
- Music+SFX on same channel: "you just need to read enough of the music data so you can
  keep the timing" — read music data but skip SID writes, execute SFX code instead
- SFX API: call once to trigger; `A`/`Y` = address lo/hi; `X` = channel (#14 etc.);
  playroutine takes care of the rest
- "No dedicated editor planned"

### Cadaver "Building a music routine" rant
URL: https://cadaver.github.io/rants/music.html
Comprehensive design essay by Cadaver covering the architecture that NT and GoatTracker
share. Key technical points:

- **Frame-based, 50Hz IRQ** execution; three voices processed sequentially via X-indexed
  reuse
- **Ghost registers:** SID registers are write-only → maintain shadow copies updated
  internally, written to HW at end of routine for sharpest timing
- **Hardrestart (testbit method):** set ADSR, clear gate, write $09 (testbit+gate-off) to
  waveform; next frame set actual waveform. Sharper attack than old method.
- **Frequency table:** all note values per octave; slides calculated as differences
  between adjacent freq-table entries, then bit-shifted for speed
- **PW modulation:** add/subtract speed each frame within limits to prevent wraparound
- **Vibrato:** needs delay, speed, width. Start with half-duration upward for tuning
  centered on target frequency
- **Arpeggio/wave table:** byte pairs = waveform register + note offset (relative or
  absolute); plus jump and termination entries
- **Tied notes:** change frequency only, no hardrestart, no PW reinit
- **Pattern read lookahead:** fetch next note data early to hide the rastertime cost
- **Data encoding:** sequences use $00–$7F patterns, $80–$BF transpose, $C0–$FF
  repeat/jump — same as NT2 orderlist
- Mentions GT, NT, and MiniPlayer as implementation examples in this design space

### Codebase64 wiki
Fetched: https://codebase64.org/doku.php?id=base:ninjatracker — no dedicated NT article
found in the search results or fetched HTML.

### GitHub — NinjaTracker
- github.com/localhost/NinjaTracker — "My custom modifications to NinjaTracker 2"
  (not Cadaver's official repo; fork with minor tweaks). Contents identical to V2.04
  distribution files.
- No official Cadaver GitHub repo for NinjaTracker (it predates his GitHub presence;
  his GitHub is cadaver.github.io with links to csdb/covertbitops.c64.org downloads).

---

## GT2NT2 Converter — What It Reveals About Format Compatibility

Source: `pipelines/ninjatracker/docs/src/gt2nt2.c` (GT2NT2 V1.03, Cadaver).

The converter explicitly documents NT2 limitations vs GoatTracker 2:

**Unsupported by NT2 (hard limits):**
- More than 127 patterns
- More than 16 subtunes
- Subtune orderlist > 256 bytes combined across all 3 tracks
- Patterns > 192 bytes
- Octave 0 (removed in V1.02 gamemusic, not present in NT2)
- Wavetable commands (GT pattern commands 7, C, D, E)
- "Leave frequency unchanged" in wavetable
- Changing filter mode without also changing cutoff, or vice versa
- Filter resonance control (NT copies passband+8 to resonance — fixed coupling)
- Pattern commands 7, C, D, E from GT
- Vibrato (GT command 4) combined with a new note on the same row
- Fine pulse modulation (GT uses full 8-bit speed; NT uses only high 4 bits)
- Calculated (note-independent) slide and vibrato speed

**Commands 1 & 2 (portamento up/down without destination)** are emulated using a very
high or low toneportamento target. Not exact in all cases.

**Converter output format (`saventsong`):**
Magic bytes: `'N'`, `'2'` followed by the same fixed-size table layout described above.

**Table construction notes from converter:**
- GT vibrato → NT wave table vibrato steps (`$C0 + speed`, right = depth)
- GT pulse set → NT pulse table `$80` entry; GT pulse mod → NT `$01-$7F` entry with
  high 4 bits of GT speed as NT speed value
- GT filter set → NT filter `$80` entry with passband, routing, cutoff packed in

---

## Technical Details

### Per-frame execution order (V2.x `nt_music`)

Each call to `nt_music`:
1. Check for new-song init flag; if set, initialize all channel state
2. **Filter execution** (global, once)
   - Look up filter table at `nt_filtpos`
   - $80–$FE: set resonance+passband to `$D417`, set cutoff to `$D416`, store passband
   - $01–$7F: modulate cutoff for N frames at signed speed
   - $FF: jump
3. Write `$D418` master volume (`ORA #$0F` — always $0F = max, but constant can change)
4. **Channel 1 execution** (X=0)
5. **Channel 2 execution** (X=7)
6. **Channel 3 execution** (X=14)

Per-channel execution order:
1. Increment frame counter; if not zero → jump to pulse (no new data yet)
2. If counter == 2 (3 frames before note): read pattern data into buffer (3-frame lookahead)
3. If counter reaches 0: reload duration counter; check for new note or new track entry
4. New note: apply transpose; set freq; trigger hardrestart if needed; set command ADSR+tables
5. **SFX check**: if SFX active on this channel → jump to SFX exec, skip wave/pulse
6. **Pulse table exec** (per-channel)
7. **Wave table exec** (per-channel): waveform set + arpeggio / vibrato / slide
8. Write `chnwave AND chngate` → `$D404,x` (SID control register)

### SID register write addresses (per channel)

Channel 1: $D400–$D406; Channel 2: $D407–$D40D; Channel 3: $D40E–$D414
Global: $D415 (cutoff lo, written once during init in V1), $D416 (cutoff hi), $D417
(resonance+filter routing), $D418 (volume+filter passband)

### Hardrestart state machine in the player

The gate manipulation uses `nt_chngate` as a mask applied to the waveform via AND:
- $FF = gate on (note playing)
- $FE = gate off (hardrestart or keyoff)
The AND with `nt_chnwave` then produces the effective waveform + gate written to `$D404,x`.

### Note encoding in internal representation

Notes are stored doubled: internal value = (note_index) × 2. The low bit signals
"command byte follows" in the pattern stream. So note C-1 = `$18` × 2 / 2 = note 12
in the freq table (0-indexed from C-1), and `NT_FIRSTNOTE = $18 = 12*2`.

The freq table is indexed as `nt_freqtbl - 24` (i.e., offset −12 words from the table
base) to align the 0-indexed doubled note value directly.

### Packer optimization: legato-only commands

The packer separately tracks `lastcmd` (highest command used in normal mode) and
`lastlegatocmd` (highest command used in any mode). Commands only used in legato mode
and placed at the end of the command list have their ADSR bytes elided in the packed
output, reducing module size. The player reads ADSR only for indices < `gamecmdsize`
and table pointers for indices < `gamelegatocmdsize`.

### Pulse width detail

NT2 uses a single 8-bit pulse value written simultaneously to `$D402,x` (lo) and
`$D403,x` (hi). Effective pulse width = (value × $0101) = approximately value/256 of
full 12-bit range. This is the source of GT2NT2's note: "NinjaTracker uses only the high
4 bits of the pulse speed values used by GoatTracker."

### MiniPlayer differences (cadaver/miniplayer, cadaver/miniplayer2)

MiniPlayer is an NT1-inspired derivative targeting 9 rasterlines:
- Wave, pulse, filter tables use "next column" (no jump commands inside the table)
- Pulse/filter use "destination value compare" rather than frame counters
- ZP variable footprint much larger (requires page-aligned music data in MiniPlayer 2)
- Same GT2 converter approach; supports effects 1,2,3,4,F (no funk tempo)
- Only 1 frame of gate-off before new note (no guaranteed hardrestart)
- MIT licensed; source only, no editor

---

## Leads to Follow

1. **CSDb search for NT-based productions:** https://csdb.dk/search/?seintype=release&query=NinjaTracker
   — the search page HTML was fetched but not deeply parsed; individual production pages
   may contain technical comments from Cadaver about specific design choices.

2. **Lemon64 thread p.3:** https://www.lemon64.com/forum/viewtopic.php?p=243231
   — not fetched; may contain deeper V2.0 technical discussion.

3. **Pouet.net NT2.0 NFO:** https://www.pouet.net/prod_nfo.php?which=26206&font=none
   — not fetched; may contain design notes in the release NFO text.

4. **Pouet.net NT1.1 NFO:** https://www.pouet.net/prod_nfo.php?which=13462&font=none
   — not fetched.

5. **cadaver/miniplayer2 on GitHub:** https://github.com/cadaver/miniplayer2
   — only partially fetched. The `gt2nt2`-style converter source and player.s there
   would reveal more about table format alternatives worth knowing before writing the
   NT USF converter (especially the "destination compare" vs "frame counter" pulse/filter
   approach).

6. **Sam's Journey and Hessian SID files** in HVSC84 — NT2 in production use.
   `MUSICIANS/C/Cadaver/Hessian.sid` and `MUSICIANS/C/Cadaver/Sam_s_Journey.sid`
   (if present) are Cadaver's own compositions; they are ground-truth for what the
   in-engine format looks like in practice.

7. **NinjaTracker V2.04 d64 disk image** (`ninjatr2.d64` inside `ninjatr204.zip`) —
   not yet extracted; contains example tunes that show real-world usage of commands and
   tables. "EfnCold" by Adam Morton is one bundled example.

8. **ins2nt2 C source** (`extracted/nt204/src/ins2nt2.c`) — not yet read; reveals the
   exact byte packing of GoatTracker instruments into NT2 SFX data, which is the
   definitive SFX format spec.

9. **HVSC NinjaTracker_V1.x SIDs:** 18 SIDs classified as V1.x — their binary layout
   will differ (5-byte header, single-column tables, different note encoding). The V1
   `ntplay.s` (already at `docs/src/ntplay_v1.s`) is the ground-truth player for those.

10. **GoatTracker 1.x → NinjaTracker 1.x converter** — on Covert Bitops tools page as
    a separate download. Not yet fetched; reveals V1 format from the conversion side.
