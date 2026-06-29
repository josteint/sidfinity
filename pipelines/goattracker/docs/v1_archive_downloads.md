# GoatTracker V1.x — Archive Downloads and Format Reference

```
source_url:    https://archive.org/details/goattrk_zip  (v1.52 zip)
               https://cadaver.github.io/tools/goattrk.zip  (v1.53)
               https://cadaver.github.io/tools/goatold.zip  (v1.25)
fetched_via:   direct wget 2026-06-29 (both cadaver.github.io downloads live)
               archive.org item goattrk_zip (uploader Swizzley, Sep 2023)
fetch_date:    2026-06-29
author:        Lasse Oorni (Cadaver), Covert Bitops
content_date:  V1.25: 2002-06-18; V1.52: 2004-03-30; V1.53: 2006-05-16
reliability:   PRIMARY — verbatim readme.txt + player source from official zips
```

## Downloads Obtained

All zips saved to `tmp/goattracker_v1_research/` and key files
copied to `pipelines/goattracker/docs/src/` (v1_-prefixed):

| File | Source | Size | Contents |
|------|---------|------|----------|
| `v1_readme_153.txt` | cadaver.github.io/tools/goattrk.zip | 52 KB | Full V1.53 manual (1257 lines) |
| `v1_readme_125.txt` | cadaver.github.io/tools/goatold.zip | 44 KB | Full V1.25 manual (1132 lines) |
| `v1_gmusic_153.s`   | same as `v1_gmusic_v153.s` (pre-existing) | 29 KB | V1.53 game playroutine (DASM source, 868 lines) |
| `v1_player1_125.s`  | goatold.zip SRC/PLAYER1.S | 19 KB | V1.25 standard playroutine ("musicroutine 11.1", Sep 2001) |
| `v1_player2_125.s`  | goatold.zip SRC/PLAYER2.S | 22 KB | V1.25 game playroutine ("musicroutine 11.2", Sep 2001) |

Archived URL at Internet Archive: `https://archive.org/download/goattrk_zip/goattrk.zip`
(goattrk.zip = V1.52 zip, 461.9 KB, publication date 2004-03-30)

CSDb entry for V1.25: https://csdb.dk/release/?id=6072 (released 2002-07-18)
Cadaver's current tools page: https://cadaver.github.io/tools.html

V1.25 also has player sources PLAYER3.S–PLAYER6.S (scene/multispeed variants,
not extracted here; available in `tmp/goattracker_v1_research/goattrk_v125_cadaver.zip`).

---

## IMPORTANT CORRECTION to existing research.md

`research.md` states: "V1 IDs: GTS3, GTS4; V2: GTS5"

**This is wrong.** The actual V1.x format identifier is `GTS!` (verified
from both V1.25 and V1.53 readme.txt section 6.1.1):

> +0  4  Identification string GTS!

`GTS3` and `GTS4` are **early GoatTracker 2** format versions (GT2 pre-v2.59
used GTS3; v2.4 switched to GTS4 for the pulse-precision addition). GT1 uses
`GTS!` throughout all versions. The instrument file uses `GTI!`.

---

## V1 Song Format (.SNG) — Verbatim from readme.txt

### 6.1.1 Song header

```
Offset  Size    Description
+0      4       Identification string GTS!
+4      32      Song name, padded with zeros
+36     32      Author name, padded with zeros
+68     32      Copyright string, padded with zeros
+100    byte    Number of subtunes
```

### 6.1.2 Song order-lists (V1.53 / post-v1.3)

One orderlist per channel per subtune (3 × N_subtunes orderlists total),
stored in subtune-major order (all 3 channels of subtune 0, then subtune 1…):

```
Offset  Size    Description
+0      byte    Length of this channel's orderlist n - 1
+1      n       The orderlist data:
                Values 0-207   = pattern numbers
                Values 208-223 = repeat commands (repeat-count = value - 207, max 16)
                Values 224-254 = transpose commands (+/- halftones)
                Value 255      = RST endmark, followed by restart-position byte
```

**V1.25 orderlist (pre-v1.3) was simpler — no transpose or repeat:**

```
                Values 0-254 = pattern numbers
                Value 255    = RESTART endmark, followed by restart-position byte
```

Transpose was added in v1.3. The transpose range in V1.53: up 0-14 halftones,
down 1-15 halftones. Transpose is reset only on song start, not on RST endmark.

### 6.1.3 Instruments

31 instruments (instrument 0 = empty, not stored). Per instrument:

```
Offset  Size    Description
+0      byte    Attack/Decay
+1      byte    Sustain/Release
+2      byte    Initial pulse width (00-FE; low bit = hard-restart flag: 0=use HR, 1=skip)
+3      byte    Pulse speed (low bit always 0 = hard-restart flag; effective speed = value & $FE)
+4      byte    Pulse limit low  (low nybble always 0)
+5      byte    Pulse limit high (low nybble always 0)
+6      byte    Filter number to use (0 = no change; valid 1-63)
+7      byte    Size of wavetable in bytes n (always even)
+8      16      Instrument name (null-padded)
+24     n       Wavetable: interleaved waveform/note byte pairs
```

NOTE: In V1.25 the pulse bytes (+2,+3,+4,+5) had **nybbles reversed** compared to
the editor display. This was removed in a later version — V1.53 stores them
without reversal. (See V1.25 readme section 6.1.3: "* = nybbles reversed".)

The hard restart flag in bit 0 of the pulse speed byte (offset +3) controls
whether the instrument uses the testbit hard restart mechanism (0 = use it,
1 = skip). Added in v1.5.

### 6.1.4 Patterns header

```
+0      byte    Number of patterns n
```

### 6.1.5 Patterns

```
Repeat n times (pattern 0, 1, 2…):
+0      byte    Size of pattern in bytes m
+1      m       Groups of 3 bytes per row:
                  1st byte: Notenumber
                              0-93   = notes C-0 to A-7 (chromatic: 12/octave)
                              94     = keyoff (gate off)
                              95     = rest
                  2nd byte: Bits 7-3 = Instrument number (0-31)
                            Bits 2-0 = Command number (0-7)
                  3rd byte: Command databyte
```

### 6.1.6 Filter table (V1.53 only, added v1.4)

```
+0      256     64 filter steps × 4 bytes each:
                  1st byte: Resonance (high nybble) / channel bitmask (low nybble)
                            Nonzero = set new filter params; zero = cutoff modulation mode
                  2nd byte: Filter type (high nybble) / SID master volume (low nybble, default F)
                            If ctrl=0: duration of cutoff modulation in frames instead
                  3rd byte: New cutoff frequency (00 = no change)
                            If ctrl=0: cutoff modulation speed instead
                  4th byte: Next filter step to execute (0 = stop; loop by pointing back)
                            NOTE: filter 0 "Next Step" is disabled (funktempo hack)
```

The filter table is absent in V1.25 (which used a simpler per-instrument
freq/type byte + command-2 cutoff speed).

---

## V1 Instrument (.INS) Format

```
Offset  Size    Description
+0      4       Identification string GTI!
+4      byte    Attack/Decay
+5      byte    Sustain/Release
+6      byte    Initial pulse width
+7      byte    Pulse speed
+8      byte    Pulse limit low
+9      byte    Pulse limit high
+10     byte    Filter number (0 = no change; 1-63 active)
+11     byte    Wavetable size n (even)
+12     16      Instrument name
+28     n       Wavetable (waveform/note byte pairs)
+28+n   4       If filter number nonzero: filter settings of this instrument
```

---

## V1 Pattern Commands (V1.53)

```
Command 0XY: Arpeggio
             Cycles: root → root+X halftones → root+Y halftones, every tick.
             If X >= 8: half-speed arpeggio (X -= 8 for actual semitones).
             Executes every tick (tick 0 AND ticks 1-N).

Command 1XY: Portamento up
             Raises pitch by (XY)*4 each tick (ticks 1-N only).

Command 2XY: Portamento down
             Lowers pitch by (XY)*4 each tick (ticks 1-N only).

Command 3XY: Toneportamento
             Slides pitch toward target note at speed (XY)*4 per tick.
             Direction auto-detected (from v1.3). Speed 00 = tie note (no slide).
             Ticks 1-N only; tick 0 latches new note as target.

Command 4XY: Vibrato
             Pitch changes (Y*16+X) per tick; direction flips every X*2 ticks.
             Ticks 1-N only.

Command 5XY: Set filter
             Activates filter step XY (00-3F) from the filter table.
             Executes on tick 0 only.

Command 6XY: Set sustain/release
             Sets channel's SR register to XY. Tick 0 only.

Command 7XY: Set tempo / special
             XY < $80: set tempo on all 3 channels (minimum 3)
             XY >= $80: set tempo on current channel only (tempo = XY & $7F)
             XY = $00: activate funktempo (see below)
             XY = $EF: increment timing mark byte (playerbase+$445)
             XY = $F0-$FF: set master volume fader (F0=silence, FF=maximum)
             Tick 0 only.
```

**V1.25 command differences** (before v1.3 restructure):

```
Command 0XY: Arpeggio (same semantics, but executes ticks 1-N only — NOT tick 0)
Command 1XY: Portamento (combined: high bit=direction; 0=up, 1=down; speed=(XY & $7F)*2)
Command 2XY: Set filter cutoff speed (value added to cutoff every tick; >= $80 subtracts)
Command 3XY: Toneportamento (manual direction: high bit=direction; speed=(XY & $7F)*2)
Command 4XY: Vibrato (same formula Y*16+X, same direction flip)
Command 5XY: Set filter parameters (X=resonance, Y=channel bitmask — no filter table)
Command 6XY: Set sustain/release (same)
Command 7XY: Set tempo (same; no timing marks in playroutines 1 & 2; C0-FF = timing in 3 & 4)
```

---

## Wavetable Semantics (V1.x)

The wavetable is a sequence of (waveform, note) byte pairs executed starting
from note-on, one pair per tick. The waveform byte and note byte are
interleaved in the SNG instrument block (not separate tables as in GT2).

**Waveform byte:**

| Bits | Meaning |
|------|---------|
| $01  | Gate bit (must be set for audible sound) |
| $02  | Sync bit |
| $04  | Ring-mod bit |
| $08  | Test bit (silences channel; used for hard restart) |
| $10  | Triangle waveform |
| $20  | Sawtooth waveform |
| $40  | Pulse waveform |
| $80  | Noise waveform (do not combine with others) |
| $00  | Do not change waveform |
| $01-$08 | Delay execution 1-8 frames without changing waveform |
| $FF  | End/loop marker |

**Note byte:**

| Range | Meaning |
|-------|---------|
| $00-$5F | Relative note: add to current playing note |
| $80-$DF | Absolute note: C-0 ($80) through B-7 ($DF) |

When waveform = $FF:
- Note = $00: end wavetable (stay on last waveform/freq)
- Note = n > $00: loop to wavetable position n (1-indexed)

Until the wavetable ends (reaches $FF/00), portamento, vibrato, and arpeggio
commands do NOT execute. Pulse modulation executes during wavetable (from v0.94+).

**CRITICAL V1-vs-GT2 difference:** GT2 uses SEPARATE wave/pulse/filter/speed
tables (each independently stepped). V1 uses ONE interleaved (waveform, note)
table per instrument — there is no concept of a separate pulse or filter table
inside the instrument. Pulse modulation is controlled by the 4 instrument
parameters (initial PW, speed, low limit, high limit).

---

## Filter Semantics (V1.x, from v1.3/v1.4)

The filter is step-programmable with 64 steps (step 0 reserved for
funktempo). Each step is 4 bytes:

```
[ctrl] [type_vol] [freq_or_speed] [next_step]
```

- `ctrl` nonzero: set resonance (high nybble) + channel routing (low nybble,
  bitmask 1/2/4/8 for ch1/ch2/ch3/ext) and go to freq_or_speed as new cutoff.
- `ctrl` zero: sweep cutoff for `type_vol` frames at speed `freq_or_speed`
  (signed byte: positive = up, negative = down).
- `next_step`: 0 = stop; nonzero = advance to that step next frame.
  (Filter step 0 has Next Step disabled — used by funktempo hack.)

Filters can be activated by:
1. Pattern command 5xy (step xy activated once per row, tick-0)
2. Instrument parameter `Filter To Use` (activated on each new note trigger)

The V1.25 filter model was simpler:
- Command 5XY: set resonance (X) + channel bitmask (Y) once, with current cutoff
- Command 2XY: set cutoff speed (added each tick; >= $80 subtracts)
- Instrument byte 6: set cutoff freq + filter type on note trigger (combined byte)

---

## Arpeggio Semantics (V1.x) — Extracted from gmusic.s

The arpeggio (command 0) cycles through 3 notes using `mt_chnarpcount`:

```
mt_arpcount:  0 → play root note
mt_arpcount:  1 (or -1) → play root + X halftones
mt_arpcount:  2 → play root + Y halftones
then wraps back to 0
```

Counter advances every tick. Wraps at 6 (stored 0,1,2,0,1,2,…). If X >= 8
(half-speed flag): only advances on even ticks (skips alternate ticks).

The arpeggio shares the `mt_chnarpcount` register with vibrato — mixing them
in the same note can produce unexpected results (per readme warning section 2,
item 6: "From version 1.3 onwards arpeggio & vibrato use the same internal
register for calculations").

In V1.25, arpeggio executes on ticks 1-N only (NOT tick 0). In V1.53 it executes
on every tick (the tick-0 handler still reads it — command 0 is in `mt_tick0tbl`
at index 0 pointing to `mt_tick0arp`, which checks if a new note is pending before
executing). The half-speed semantics are unchanged between V1.25 and V1.53.

---

## Vibrato Semantics (V1.53)

```
Command 4XY:
  Amount per tick = Y*16 + X
  Direction flips every X*2 ticks (X = half-period in ticks)
  Note: the formula Y*16+X is caused by player optimizations —
        the high nybble (Y*16) is the dominant term; the low nybble X
        adds a fine offset equal to the direction-flip speed.
```

From `mt_ticknvibrato` in `v1_gmusic_153.s`:
- `mt_zpbase` = (param & $F0) = Y*16 (pitch increment magnitude)
- `mt_vibratocmp+1` = (param & $0F) = X (half-period threshold)
- `mt_chnarpcount` incremented by 2 each tick; sign determines direction
- When `mt_chnarpcount >= X`: flip direction (EOR #$FF), restart at 0+2

The shared arpeggio/vibrato counter means you cannot run both simultaneously.

---

## Hard Restart Mechanism (V1.5+)

From `gmusic.s` and the readme (section 3.8 ADSR examples, warnings item 8):

1. On note trigger (tick 0, new note): if instrument has hard-restart enabled
   (pulse speed bit 0 = 0), the player writes the ADSR hard-restart parameter
   (configurable, default AD=$0F SR=$00) to `$D405`/`$D406` and sets waveform
   to `$09` (test bit + gate) for the `mt_gatetimer` frames (1 or 2).
2. After the gate-timer frames: the instrument's actual AD/SR and the first
   wavetable waveform are loaded, gate is set.

This produces sharp note attacks by resetting the ADSR envelope via the test
bit. The ADSR hard-restart parameter is set with the `/A` command-line option
(default `0F00`). Instruments can opt out (pulse speed bit 0 = 1).

In V1.25, hard restart was simpler: always write $00 to both AD and SR registers
on note start, no testbit involved.

---

## Player Loop Structure (V1.53 gmusic.s vs V1.25 player2.s)

### V1.53 `gmusic.s` (the "game playroutine" for relocatable music modules)

Entry: `music:` (play one frame) / `playtune:` (init, A=subtune) / `playsfx:`

Per-frame execution order:
1. **Filter execution** — one step of filter table if active; updates $D416/$D417/$D418
2. **Channel loop** (X = 0, 7, 14 for channels 1-3):
   a. Decrement tick counter; check tick 0
   b. **Tick N (not 0):** run wavetable if active, else dispatch to effect handler
      (portamento up/down, toneportamento, vibrato, arpeggio)
   c. **Tick 0:** read next pattern row; dispatch tick-0 command (filter/SR/tempo)
      then check for new note
   d. **New note:** load instrument params (PW, wavetable ptr, filter, AD/SR);
      write testbit ($09) waveform; set gate
   e. **Wavetable:** advance (waveform, note) pair; update freq from note table
   f. **Pulse modulation:** advance PW counter, check limits, flip direction
   g. **Register writes:** $D400/01 (freq), $D402/03 (PW), $D404 (wave+gate),
      $D405 (AD), $D406 (SR)

**Channel variable layout (stride-7 interleaving):**
Variables are stored in parallel arrays; X=0/7/14 selects channel 1/2/3.

```
mt_chnwave[x]       waveform currently written to $D404
mt_chnwaveptr[x]    index into wavetable (0 = no wavetable)
mt_chnpackrest[x]   packed-rest state
mt_chnrepeat[x]     repeat counter
mt_chntrans[x]      current transpose (halftones, signed)
mt_chnsongptr[x]    position in orderlist
mt_chnpattptr[x]    position within current pattern ($FF=ENDPATT sentinel)
mt_chnfreqlo[x]     current SID frequency lo byte
mt_chnfreqhi[x]     current SID frequency hi byte
mt_chnpulse[x]      current pulse width high byte
mt_chnpulsedir[x]   pulse direction (bit 0 = direction flag)
mt_chnad[x]         current AD value (for hard restart)
mt_chnsr[x]         current SR value
mt_chngate[x]       gate mask ($01 = gate on, $FE = gate pending off)
mt_chnnewfx[x]      queued effect command
mt_chnnewfxparam[x] queued effect parameter
mt_chnfx[x]         active effect command
mt_chnfxparam[x]    active effect parameter
mt_chnnote[x]       current playing note number (0-93)
mt_chnnewnote[x]    pending new note ($FF = none)
mt_chninstnum[x]    current instrument base address (offset from mt_musicdata)
mt_chnarpcount[x]   arpeggio/vibrato state counter
mt_chnsongnum[x]    which song orderlist (index into song table lo/hi)
mt_chnpattnum[x]    current pattern number
mt_chntick[x]       tick counter (tempo down to 0)
mt_chntempo[x]      tempo setting (speed 3-255)
mt_chnsfx[x]        sound effect playback state (0=none)
mt_chnsfxnum[x]     current sound effect number
```

### V1.25 `player2.s` (game playroutine, structurally different)

The V1.25 player is monolithic (not relocatable); wavetable and note table were
at SEPARATE addresses ($5000 and $5100). Key structural differences vs V1.53:

1. Wavetable ($5000) and note table ($5100) are separate memory regions;
   the SNG file stores them interleaved, the relocation splits them.
2. Filter model: no step table. Filter state = `mt_filtctrl` (resonance+channels,
   written to $D417) + `mt_filttype` (filter type, ORed with master vol → $D418)
   + `mt_filtcutoff` (written to $D416). Cutoff is updated every frame by adding
   `mt_filtcutoffadd` (set by command 2).
3. Hard restart: on note trigger, `$D405` and `$D406` both written to $00 (no testbit).
4. Pulse direction flag is in bit 7 of `mt_chnpulsedir` (not bit 0).
5. No tick-0 / tick-N dispatch table — inline condition checks.
6. Command 1 (portamento) is a single command with direction in high bit.
7. No transpose/repeat in orderlist (added v1.3).
8. Sound effects: address passed as raw pointer in AX (not a table number).

---

## V1-vs-GoatTracker-2 Player Differences (Summary)

This section answers "what is different about the V1 player loop vs GT2?"

| Aspect | GoatTracker V1.x | GoatTracker V2.x |
|--------|-----------------|-----------------|
| Song file ID | `GTS!` | `GTS3`(early)→`GTS4`→`GTS5` |
| Instruments per song | 31 | 63 |
| Max patterns per song | 208 (V1.53) | 256 |
| Max subtunes | 32 | 32 |
| Wavetable model | Single interleaved (waveform,note) table per instrument | Separate wave/pulse/filter/speed tables (global, shared) |
| Arpeggio | Pattern command 0XY (3-note: root,+X,+Y) | No arpeggio command; multi-note done in wave table |
| Pulse modulation | Per-instrument params (init PW, speed, low/high limits) | Separate pulse table with step-programmable sequence |
| Filter programming | V1.3+: 4-byte filter step table (64 steps); V1.25: direct cmd-2 cutoff | Separate filter table (255 steps) with time/speed semantics |
| Hard restart | V1.5+: testbit per instrument (configurable ADSR); V1.25: always AD=$00 SR=$00 | Testbit per instrument (configurable ADSR) |
| Portamento | V1.3+: separate up (cmd1) and down (cmd2); V1.25: combined cmd1 (dir in high bit) | Separate up/down (same as V1.3+) |
| Toneportamento | cmd3, speed*(4 in V1.3+) or *(2 in V1.25) | cmd3, configurable |
| Vibrato | cmd4, period=X*2 ticks, amount=Y*16+X | cmd4, separate vibrato delay parameter in instrument |
| Filter command | cmd5 step, cmd6 SR, cmd7 tempo/fader | cmd5 step, cmd6 SR, cmd7 tempo/fader (similar) |
| Orderlist | pattern#, transpose(V1.3+), repeat(V1.3+), RST+pos | pattern#, transpose, repeat, RST+pos |
| Channel register writes | freq, PW, wave+gate, AD, SR — every tick | freq, PW, wave+gate, AD, SR — gated by `mt_chngate` |
| Shared arp/vibrato register | Yes (cannot mix) | Not applicable (no arp command) |
| HVSC count | 1,359 SIDs | 7,311 SIDs |

**Key implication for USF:** The V1 instrument is self-contained (its own
wavetable with embedded pitch programs). In GT2 the tables are global and
referenced by index. A V1 USF representation could embed the wavetable
bytes directly per instrument (similar to Hubbard's wavetable model) since
there is no cross-instrument table sharing.

---

## Funktempo Hack

A special edge case in V1's filter table: filter step 0 is reserved for the
"funktempo" feature. Writing command `700` activates funktempo, which uses:
- Filter step 0 byte 3 (Freq/Spd) as tempo 1
- Filter step 0 byte 4 (Next Step) as tempo 2

The player alternates these two tempos every pattern row. This reuses the
filter slot 0 as a 2-entry tempo table. Filter step 0's "Next Step" field is
therefore always disabled (cannot point to next filter step).

---

## Version History Key Events (from readmes)

| Version | Date | Key format/player change |
|---------|------|--------------------------|
| 0.9 Beta | ~2001 | Original public release |
| 0.94 Beta | 2001 | Wavetable loops added ($FF end/loop byte). Pulse modulation during wavetable. |
| 1.1 | 2002 | Multiple playroutines (1-4). Song/instrument format documented. |
| 1.15 | 2002 | End song command replaced by RST+restart-pos. Max patterns 255. |
| 1.23 | 2002 | Pulse initial $00 no longer resets direction |
| 1.3 | 2003 | Hard restart toggle per instrument. Transpose + repeat in orderlist. Step-based filter table. Separate portamento down command (cmd2). Vibrato reworked. |
| 1.4 | 2003 | Filter step-programmable (64 steps). Funktempo hack. |
| 1.4d | 2004 | $D418 bug fix |
| 1.5 | 2004 | Playroutine rewritten: testbit hard restart. Master fader (7F0-7FF). Delayed wavetable. Proper gateoff. |
| 1.52 | 2004 | Frequency table tuning correction |
| 1.53 | 2006 | Packer fix for no-HR/no-pulseinit instruments |

---

## Leads to follow

1. **GTS3 / GTS4 format differences from GTS!** — The existing `research.md`
   mislabels GTS3/GTS4 as "V1 IDs". These are actually early GoatTracker 2
   format identifiers. The transition path GTS!→GTS3→GTS4→GTS5 is a GT2
   internal history, not a V1 thing. This should be corrected in `research.md`
   before any GT1 extraction work.

2. **V1.25 SRC/PLAYER3.S–PLAYER6.S** — Only PLAYER1/2 extracted here.
   PLAYER3 (scene, with author info), PLAYER4 (everything), PLAYER5 (multispeed),
   PLAYER6 (relocation stub) are in the tmp zip; extract if needed for V1 RE.

3. **HVSC GT1 SID detection** — The 1,359 V1 SIDs in HVSC are classified by
   sidid. Verify how sidid distinguishes GT1 from GT2 (likely by the `GTS!` vs
   `GTS3`/`GTS4`/`GTS5` magic embedded in the PRG data block of the SID file).

4. **V1 player relocation** — The V1.53 `gmusic.s` uses a relocation table
   (`reladrtbllo`/`reladrtblhi` + `reladdtbl`) of 15 entries, applied by
   `relocatemusic`. Understanding this is needed before extracting V1 SIDs —
   the player patches its own operand bytes to point into the loaded music data.

5. **GTS! stereo variant** — V1.53 stereo was also on the Cadaver page
   (`tools/gstereo.zip`). Not downloaded yet. May have different player layout.

6. **Wayback Machine snapshots** — The WebFetch tool cannot access
   `web.archive.org` directly (blocked). The CDX API also failed. To get
   historical snapshots of `covertbitops.cjb.net` (the original site, before
   the GitHub redirect), use a browser or `curl` directly from a machine that
   can reach Wayback. The original site had `tools/goattrk.zip` as early as
   2002.

7. **ChiptuneSAK GT1 docs** — ChiptuneSAK reportedly has GoatTracker (both V1
   and V2) support. Their docs at `chiptunesak.readthedocs.io/en/latest/goattracker.html`
   may have additional V1 format notes.
