<!--
source_url: http://noname.c64.org/download.php/ctmisc/ctfileformat-1_01.html
fetched_via: wayback 2025-10-01 (capture), retrieved 2026-06-14 (user-supplied HTML)
fetch_date: 2026-06-14
author: Bjarke Nørgaard Laustsen ("CyberBrain" / No Name)
content_date: 2001-11-13 (V1.01 fixed)
reliability: primary (author's own byte-level file-format spec)
-->

# CyberTracker — byte-level file format (V1.01, author's spec)

This closes the #1 migration gap. CyberBrain's own `.ct`/`.ci` file-format spec was
recovered (Wayback capture of `noname.c64.org/download.php/ctmisc/ctfileformat-1_01.html`)
and saved verbatim at [`src/ctfileformat-1_01.txt`](src/ctfileformat-1_01.txt). Key fact
from the author: **"there's absolutely no packing going on anywhere in the files"** — the
on-disk tables are the raw runtime tables. The only V1.00→V1.01 change: V1.01 saves only
the *used* pattern memory (not the whole pool).

⚠ This is the **editor `.ct`/`.ci` file** layout. HVSC ships the assembled `.sid`/exe
(see `cluster_write_model_and_variants.md` for the in-memory $10xx/$53A2 layouts). The two
share the same table SEMANTICS; the file spec below is the cleanest description of the data
model and is the reference for the extractor's table decode.

## Music file (`.ct`) layout

Header: `$0000` 10-byte ID `00 04 "nntrkmzx"` (`$00,$04` = PRG load addr; `4E4E54524B4D5A58`);
`$000A` `.word` version (`00 01` = V1.00; file is `0101`). `$000C` = `$11` table count.

Then a sequence of **length-prefixed tables** (each preceded by a 2-byte `.word` byte-length):

| Offset | Len | Table | Content |
|---|---|---|---|
| $000D | $20 | VIBDPT | vibrato depth × 32 instruments |
| $002F | $20 | VIBSPD | vibrato speed × 32 |
| $0051 | $20 | ARPEGGIO | arpeggio value × 32 |
| $0073 | $40 | ADSR | `[AD, 0R] × 32` (sustain nibble always 0) |
| $00B5 | $200 | INSNAM | 16-byte instrument names × 32 (C64 screen-codes, NOT ASCII) |
| $02B7 | $200 | MLTEFF | multi-effect table: first $100 = effect# (bit0-3 eff, bit4 = "E" flag), last $100 = effect param |
| $04B9 | $100 | SNGLEN | length (lines) of each of 256 songs ($00 = off) |
| $05BB | $100 | SNGREP | repeat position of each song |
| $06BD | $100 | LOOPSTART | envelope loop-start point ($FF = no loop) × 256 envelopes |
| $07BF | $300 | ENVXTABLO | x-coord lo of all 768 envelope points |
| $0AC1 | $300 | ENVXTABHI | x-coord hi |
| $0DC3 | $300 | ENVYTABLO | y-coord lo |
| $10C5 | $300 | ENVYTABHI | y-coord hi |
| $13C7 | PTNMEM | PATTERNS | pattern memory (raw, see below) |
| (next) | $100 | PTNLEN | length of each of 256 patterns |
| (next) | $100 | ENVLEN | length (points) of each of 256 envelopes |
| (next) | $200 | TRKMEM | track memory (all songs concatenated) |

All offsets after PATTERNS float with `PTNMEM`. Each `(len)` word = byte-length of the table
that follows (so the parser is self-describing — walk table-by-table).

## Pattern encoding (3 bytes per channel-line, 9 per line)

A single channel cell = **3 bytes**:
- **byte 1** `%nnnnoooi`: bit0 = instrument# bit4; bits1-3 = octave (0-7); bits4-7 = note
  (`0`="---", `1`="C-" … `12`="B-", `13`=gate, `14`=stop, `15`=???).
- **byte 2** `%iiiiEEEE`: bits0-3 = effect number; bits4-7 = instrument# bits0-3.
- **byte 3** `%eeeeeeee`: effect parameter.

(Example: `D#5 12345` → `%01001011 %00100011 %01000101`.) Instrument# is split across two
bytes (4 low bits in byte2 hi-nibble + 1 bit in byte1 bit0 → 5-bit instrument id, 0-31).
A full pattern line = the 3-byte cell ×3 channels = **9 bytes**, no separators. Patterns are
stored back-to-back with no end marker; **per-pattern length comes from `PTNLEN`**.

## Track / orderlist

`TRKMEM` = 1 byte/line, songs concatenated; per-song length from `SNGLEN`, repeat from
`SNGREP`. No end markers.

## Envelopes (the 8 per instrument)

Each point is a **16-bit (x,y)** pair, stored across the 4 split tables (ENVX/Y × LO/HI).
All points of all envelopes are concatenated; **per-envelope length from `ENVLEN`**, loop
from `LOOPSTART` ($FF = none). 32 instruments × 8 envelopes = 256 envelopes; the first 8
(instrument $00) are always length 0 (instrument 0 unused). The 8 envelope slots per
instrument, in order: **volume, waveform, pulse-width, filter-pass, cutoff, resonance,
pitch, pitch-control** (matches the manual's envelope list). Total envelope point pool = 768
(hence the $300-length ENVX/Y tables).

## Instrument file (`.ci`) layout

Header `$0000` 10-byte ID `00 04 "nntrkins"` (`…4E4954524B494E53`); `$000A` version;
`$000C` = `$0A` table count. Then length-prefixed: vibrato `[SPD,DPT]` (2B), arpeggio (1B),
ADSR `[AD,0R]` (2B), 16-byte name, 8 envelope loop-starts, 8 envelope lengths, then the 4
ENVX/Y LO/HI point tables (each `LEN` = sum of the 8 envelope lengths; min 4 — the
undeletable volume-envelope points). I.e. one instrument's slice of the music-file tables.

## Migration impact

- **The extractor's table decode is now fully specified** — patterns (3-byte cells), the
  768-point split-table envelopes, tracks, multi-effect table, and all per-instrument
  param tables. No RE needed for the DATA model; only the in-memory↔file offset mapping
  remains (the `.sid`/exe stores the same tables at $10xx/$53A2 — bind via one disassembly).
- Instrument id is **5-bit (0-31)**, split byte1.bit0 + byte2.hi-nibble — easy to misread.
- Names are **C64 screen-codes**, not ASCII.
- ADSR sustain nibble is **always 0** (sustain is driven by the volume envelope, not SID SR).

## Leads to follow

- The same `ctmisc/` Wayback directory may hold other CyberBrain notes (player internals,
  the Executable-Maker layout). Worth a listing fetch from a networked host.
