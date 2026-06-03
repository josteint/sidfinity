---
source_url: https://csdb.dk/getinternalfile.php/224874/Futurecomposer%20Instructions.txt
fetched_via: direct
fetch_date: 2026-06-03
author: The Beat-Machine (Chris / Dynamix)
content_date: 1988-1989
reliability: primary (official manual bundled with FC V4.1)
---

# Future Composer V4.1 official manual (verbatim primary source)

This is the manual bundled with FC V4.1 (Dynamix 1990). The C
copyright is **The Beat-Machine 1988/89**. This is the **only known
authoritative format documentation** for FC; everything else
(disassemblies, sidid signatures) is derived from binaries.

## What's new in V4.1 (vs. earlier FC)

- "Main-Edit" much improved
- "Info-Page with discoptions" removed (merged into main UI)
- **Relocate-mode for music-routine**: FC tunes are not fixed at
  $1800 in V4 — they can be relocated. (This is highly relevant to
  Hawkeye which loads at $7AE0.)
- **Block / track / soundparameter / music-data saved separately**
  (so a single .SID may not contain everything; remixing is
  supported).
- **Subtune editing** (e.g. for title + game tune).

## CRITICAL: Entry points (from manual section at end)

```
to init Tune: LDA #$00-02       ; A = subtune number 0..2
              JSR $1800

to play Tune: JSR $1806
```

This confirms **+6 play offset** AND **subtune number in A** at init
(0, 1, or 2 — i.e. max 3 subtunes in V4.1, contradicting some
later-version statements about 12+ subtunes; Hawkeye's 12 subtunes
imply Hawkeye is NOT FC V4.1).

## Track format (Block sequence — track-edit)

The "track" is a per-voice sequence of bytes referencing blocks
(patterns). Each byte's value selects a behaviour:

| Range | Meaning |
|---|---|
| `$00-$2B` | Jump to block (44 blocks max addressable inline) |
| `$3F+` | (i.e. `$3F < x ≤ $7F`) **Repeat** next block (x − $3F) times. E.g. `$43 $02` = play block 2 four times. |
| `$80+` | (over `$7F`) Transpose all following tracks (semitones encoded in low bits — exact bias not stated, likely x − $80 signed). |
| `$FF` | Restart the track. |
| `$FE` | Stop playing. |

**End-of-song marker**: "End the last Tune with $FE/$FF followed by
$FD!" — i.e. the global tune terminator is `$FD`. This is a NEW
opcode not in any disassembly notes — likely the "song table
terminator" between subtunes.

## Soundparameter format (Instrument — 8 bytes, V4)

```
  byte 0   1   2   3   4   5   6   7
        |   |   |   |   |   |   |   |
Pulse-level  |   |   |   |   |   |   MCTRL register (filter ctl)
   Waveform  |   |   |   |   |   |   Pulse-cycle CTRL (2-bit)
       Att/Dec  |   |   |   |   |   Arpeggio CTRL
           Sust/Rel  |   |   |   |
              Unused (byte 4)|   |
                 Vibrato     |
                 /Drumtype   |
                       MPulse Cycle CTRL (2 bits: 00 01 10 11)
```

Wait — re-reading the ASCII art **carefully** (the original):

```
     xx xx xx xx xx xx xx xx
     .  .  .  .  .  .  .  .
Pulse.  .  .  .  .  .  .  MCTRL Register
level   .  .  .  .  .  .
        .  .  .  .  .  .
Waveform.  .  .  .  .  .
           .  .  .  .  .
Att/Dec.....  .  .  .  .
              .  .  .  .
Sust/Rel.......  .  .  .
                 .  .  .
Unused............  .  .
                    .  .
Vibrato/Drumtype.....  MPulse Cycle CTRL (00 01 10 11)
Arpeggio CTRL (00= 00 0c 18 otherwise : 00 0x 0y )
```

So the eight bytes are (left-to-right reading downward labels):

| Byte | Field |
|---|---|
| 0 | Pulse level |
| 1 | Waveform |
| 2 | Att/Dec |
| 3 | Sust/Rel |
| 4 | Unused |
| 5 | Vibrato / Drumtype |
| 6 | Arpeggio CTRL |
| 7 | MCTRL register |

(8 fields × 8 bytes — the column alignment in the ASCII art makes
this the canonical reading.)

### MCTRL bit-field (byte 7)

The MCTRL register has **per-bit flags**:
```
01  Filter
04  Arpeggio                ; enables arp from byte 6
10  Drumsound               ; switches to drum lookup via byte 5
40  WF gateoff   → "will be $40"
80  WF gateon    → "will be $81"
```

This is the engine-state mode byte. Setting `$40` forces gate off
($40 = waveform-control byte for gate-off pulse — implied). Setting
`$80` forces gate on. Bits 0 (filter), 2 (arp), 4 (drum) are
independent flags.

### Arpeggio CTRL encoding (byte 6)

```
00 = "00 0c 18"     (default arpeggio sequence — major triad?)
                    0, 12, 24 semitones = major or unison + octave?
otherwise = "00 0x 0y"   (manual encoding — high nibble selects
                          arp index, two semitone deltas in 0x/0y)
```

So `$00` is a special-case default (3-note arpeggio with semitone
offsets 0/12/24), and any other value `$xy` encodes a 3-note arp
`[0, x, y]` semitones.

This is a **3-note hardcoded arpeggio** — important: FC arps are
length-3, not variable-length tables.

### Pulse-cycle CTRL (byte 7's high bits or byte 5?)

The ASCII art has `MPulse Cycle CTRL (00 01 10 11)` aligned under
column 5/6 — ambiguous. Two-bit field, 4 modes (constant, sweep up,
sweep down, ping-pong?).

## Block format (per-pattern note data)

Blocks contain a stream of these element types (manual gives only
the editor view):

| Element | Encoded as | Notes |
|---|---|---|
| Note | `c-3`, `d-6`, `g#3` (display) | 0-95 binary, indexes 96-entry freq table |
| Sound select | `snd.xx` | Selects instrument xx |
| Duration | `dur.xx` | Note length (50Hz frames? or beats?) |
| Glide | `gl:xx,y` | y = delay before glide (frames), xx = rate. If xx > $7F, glide UP at rate `xx − $80`; else glide DOWN. |

**Glide direction encoded in MSB of rate** — bit 7 set = up,
clear = down. Magnitude in low 7 bits.

## Frequency table

Manual doesn't quote it directly but notes use `c-3, d-6, g#3`
syntax (note + octave). 8 octaves × 12 = 96 entries (C0..B7 like the
MoN disassembly's `lonote`/`hinote` tables).

## Other UI commands (informational)

- F1 restart, F3 stop, F5 continue, F7 fast play, F8 main menu
- ctrl+1/2/3 = edit track 1/2/3
- ctrl+f = edit soundparameter (instrument)
- 'Left Arrow' → Sequence-Editor
- 'Upwards Arrow' → Filter-Editor (so V4.1 has the filter table from
  the existing research doc)

## Multi-subtune layout (CRITICAL)

> "When your first tune was finished you easily edit the second
> behind the end byte ($ff or $fe) of the first one. Do the same
> with the third tune."

This means subtunes are **concatenated in linear order** in the
track byte stream. The init routine (`LDA #subtune ; JSR $1800`)
walks through `subtune` track-ends ($FE/$FF) and stops at the start
of subtune N. The **final tune is terminated with `$FE/$FF` + `$FD`**
which signals "no more tunes" globally.

So the subtune-pointer table is implicit — the init routine scans
for `$FD` to know the song-count.

## Layout (manual is silent — derived from above)

Per binary layout, the FC V4.1 file likely contains:
1. Player routine at load address (e.g. $1800-$18xx)
2. Sequence/track data for 3 voices × N subtunes
3. Block (pattern) pool
4. Instrument table (8 bytes × N instruments)
5. Frequency table (96 × 2 bytes)
6. Wave/Pulse/Filter tables (V3+ additions, layout not in manual —
   need disassembly)
