---
source_url: local: hvsc84/ + github.com/cadaver/sidid + codebase64.org
fetched_via: local read + direct
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: primary
---

# Vibrants/JO — USF and Binary Analysis

## 1. Composer Identity

- **Real name:** Poul-Jesper Olsen
- **Handles:** JO, Rock (early Genesis Project era, 1988), Technic
- **Nationality:** Danish
- **Group history:** Genesis Project (–1991), Amok (–1991), Vibrants (1992–present)
- **Active SID period:** 1988–1992 (C64); later MS-DOS + SNES work
- **CSDb profile:** https://csdb.dk/scener/?id=1926
- **Demozoo profile:** https://demozoo.org/sceners/6764/

Key biographical note (from CSDb / Demozoo): JO "never really got around to finishing an
editor" — he composed C64 music directly in assembler. For AdLib (1993–94) he likewise
"wrote his very own AdLib player and composed tunes for it in an assembler listing."
This explains why the sidid.nfo entry (see §3) is a minimal stub: no named tool exists.

---

## 2. HVSC Corpus — 105 SID Files

Total: 105 .sid files under `hvsc84/MUSICIANS/J/JO/` (one Multi_Move.sidfinity.sid excluded).
One file already extracted to USF: `Multi_Move.usf` (1988, Genesis Project, "Rock" alias).

Binary sizes range from 635 bytes (Grid.sid — game tune, different engine entirely) to
6705 bytes (First_Digi.sid — has digi). The majority cluster in the 2400–3000-byte band,
consistent with a fixed-size player (~2300 bytes of code) plus per-tune music data.

### 2.1 sidid Recognition

sidid classifies this family as **Vibrants/JO** — a single engine family. Every sidid
match is attributed to Poul-Jesper Olsen. There is no named editor; just a player binary
fingerprint.

### 2.2 Player Variants — Fingerprint Clustering

Analysis of init-routine first 6 bytes across all 105 SIDs reveals 103 distinct patterns —
nearly every SID has a unique load address, making raw init-byte fingerprinting useless
without relocation-normalization. However, the STRUCTURAL pattern is consistent across the
majority:

```
Init address:   init JMP -> init-sub
Play address:   play JMP -> [optional subtune-dispatch] -> main-play
```

Five SIDs have play routine starting with `A9 1F 8D 18 D4` (LDA #$1F STA $D418 — set
master volume $1F at top of every play frame):
- `JO_01.sid`, `Old.sid`, `Intro_Music.sid`, `Bad_One.sid`, `Commando_Theme_Remix.sid`

The Multi_Move.sid is structurally different: it has a subtune-mode dispatcher at the
top of the play address ($1806), branching on a state variable ($2174) to handle:
- mode 2: RTS (song ended / silenced)
- mode 1: JMP $20e8 (main play engine)
- default: increment voice counters, set $D418=$1F, dispatch per voice

Several SIDs use a dispatch-table structure at init (two JMPs: one for full-init, one
for song-change). Multi_Move exemplifies this with:
```
$1800: JMP $2108   ; full init
$1803: JMP $2117   ; song-change (sets state byte $2174 = $02)
$1806: [play routine dispatcher]
```

Multi-subtune SIDs (e.g., `Destiny_v1.sid` songs=2, `Bad_Track.sid` songs=3,
`A_r_cade_Sprint.sid` songs=7) use the same init-JMP dispatch pattern.

---

## 3. sidid.nfo Entry

```
Vibrants/JO
   AUTHOR: Poul-Jesper Olsen (JO)
```

The entry has **no NAME field** (no editor name) and **no REFERENCE** (no CSDb link).
This confirms the player was never released as a standalone tool. Compare with the
adjacent Vibrants/Laxity entry which has both a named editor and a CSDb reference.

Full entry saved to: `tmp/vibrants_jo_research/sidid_nfo_vibrants_jo.txt`

---

## 4. Multi_Move.usf — Complete USF Analysis

File: `hvsc84/MUSICIANS/J/JO/Multi_Move.usf`
Title: "Multi Move", Author: "Jesper Olsen (Rock)", Released: "1988 Genesis Project"
Binary: PSID v2, PAL, 6581, load=$1800...$2289, init=$1800, play=$1806, songs=1

### 4.1 Top-Level Blocks

```
psid { title clock sid start_song }
params { }          -- empty (no engine-level params extracted)
init { }            -- empty (no priming extracted)
freq_table { ... }  -- 96 entries (8 octaves x 12 notes)
pulse_programs { }  -- 2 programs
filter_programs { } -- 1 program
wave_programs { }   -- 2 programs
wave_arp = [...]    -- 1 entry (4 values)
instrument 2..10 { } -- 9 instruments (1-based, starting at inst 2)
subtune 1 { }       -- 3 voices
```

### 4.2 Freq Table

96 entries (16-bit little-endian, 8 octaves × 12 semitones).
Stored in the binary as SPLIT tables:
- LO bytes: `$1d64`..`$1dc3` (96 bytes)
- HI bytes: `$1dc4`..`$1e23` (96 bytes)

First 12 values (C-0 through B-0):
```
$010C $011C $012D $013E $0151 $0166 $017B $0191 $01A9 $01C3 $01DD $01FA
```
These are standard C64 PAL tuning. The table covers C-0 (index 0) through B-7 (index 95).

USF note encoding: `C-2` appears for the bass voice, `C-4` for drums, range up to `E-5`
for melody. Note index in binary = octave*12 + semitone (0-based).

### 4.3 Instruments

9 instruments defined (IDs 2–10). No instruments 0 or 1 in the USF (possibly
reserved/unused). All have `loop: 0` and `arp: offsets=[] period=1`.

| Inst | Waveform (2 bytes) | ADSR (AD SR) | Effects |
|------|-------------------|--------------|---------|
| 2    | $02 $41           | $0A $EA      | filter_program, noise_tick |
| 3    | $08 $11           | $0F $E5      | drum |
| 4    | $08 $11           | $02 $A8      | drum; vibrato amplitude=1 speed=1 |
| 5    | $08 $11           | $0F $C8      | drum; vibrato amplitude=1 |
| 6    | $08 $17           | $00 $E8      | noise_tick |
| 7    | $01 $41           | $00 $6D      | (none); vibrato amplitude=3 speed=2; pulse_prog=2 |
| 8    | $09 $21           | $00 $8E      | wave_arp; vibrato amplitude=5 speed=2; pulse_prog=1 increment=3 |
| 9    | $04 $17           | $00 $F9      | filter_program, tone_arp, wave_arp |
| 10   | $02 $41           | $03 $8A      | filter_program, noise_tick; pulse_prog=1 increment=4 |

Waveform bytes in the binary: each instrument's data stream starts with a ctrl byte
(e.g., $C0, $C1, $C3, $C4, $C5, $C6, $C8) followed by wave step bytes. These are
the raw instrument program streams stored at addresses indexed by the ptr table at `$1EA7`.

The instrument pointer table is at `$1EA7`: 2-byte (lo,hi) pairs per instrument.
Example: inst 2 -> $21F9, inst 3 -> $2203, ..., inst 10 -> $226F.

Binary at `$21D0` (pre-instrument meta block): `02 41 03 8A 00 00 41 81 FF...`
This decodes as: waveform[0]=$02, waveform[1]=$41, ADSR-AD=$03, ADSR-SR=$8A —
matching instrument 10's USF parameters exactly. The meta block lives just before
the instrument stream at `$21D0`..`$21DF`.

### 4.4 Wave Programs

Two wave programs defined. Binary layout: ctrl bytes (16) followed by freq bytes (16)
interleaved in blocks starting at `$1E56`.

**prog 0** (at `$1E56` ctrl / `$1E46` freq):
```
ctrl: [129, 65, 64, 128, 128, 128, 128, 128, 16, 16, 16, 16, 16, 16, 16]
      = $81 $41 $40 $80 $80 $80 $80 $80 $10 $10 $10 $10 $10 $10 $10
freq: [19, 1, 255, 35, 8, 19, 3, 35, 0, 0, 0, 0, 0, 0, 0]
      = $13 $01 $FF $23 $08 $13 $03 $23 $00...
```

**prog 1** (at `$1E76` ctrl / `$1E86` freq):
```
ctrl: [129, 65, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64]
      = $81 $41 $40 $40 $40 $40 ... (sustained square wave)
freq: [36, 253, 251, 249, 248, 247, 246, 246, 245, 245, 244, 244, 245, 246, 245]
      = $24 $FD $FB $F9 $F8 $F7 $F6 $F6 $F5 $F5 $F4 $F4 $F5 $F6 $F5
```

ctrl byte `$81` = waveform control (triangle=0x10, sawtooth=0x20, pulse=0x40, noise=0x80,
gate=0x01; $81 = noise+gate; $41 = pulse+gate; $40 = pulse no gate; $10 = triangle no gate).

wave_arp = [64, 64, 64, 64] — a flat 4-slot arp pattern (all $40 = same value, no pitch change).

### 4.5 Pulse Programs

**prog 1:** lo=1 hi=15 seg 4 160 seg 8 96 seg 0 0
**prog 2:** lo=1 hi=15 seg 4 128 seg 12 16 seg 0 0

Format: lo/hi = pulse width bounds (hi nibble of PW), seg = (speed, target) pairs.
Binary storage not yet located precisely; the pulse program area is likely near `$1E30`..`$1E55`
based on nearby data patterns (the `40 40 40 40 06 06 07 07 08 08 07 07` sequence at `$1E32`
may encode segment data).

### 4.6 Filter Programs

**prog 0:** init=192 onset=1 d418=0 final=64 end=48 seg 2 240 seg 6 248 seg 12 244 seg 16 242

Filter program parameters: init = initial cutoff ($C0=192), onset = delay ticks before sweep,
d418 = filter routing/resonance value written to $D418, final = end cutoff ($40=64),
end = total program length (48 ticks). Four segments with (speed, cutoff_target) pairs.

Binary storage: not yet located (the filter prog bytes may be embedded in the instrument
stream or stored as a separate table not yet mapped).

### 4.7 Song Structure — Subtune 1

**tempo:** 2 (engine ticks per frame; play fires every VBI, advances state every 2 calls)

**Voice 1 (drums):**
- Orderlist: `0 1 1 1 1 1 1 ... loop@0` (39 entries of pattern 1, loop back)
- Binary orderlist at `$1F00`: `01 01 01 ... FF` (39 × $01, then $FF = end/loop)
- Pattern 0 & 1 (length=96): C-4 drum patterns using instruments 4 and 3, alternating

**Voice 2 (bass):**
- Orderlist: `0 1 2 2 3 3 4 5 1 1 2 2 ...` (repeated 8× then loop@0)
- Binary orderlist at `$1F80`: `02 02 03 03 04 04 06 07` repeated 8× then $FF
- Note: binary uses 1-based pattern indices; USF uses 0-based. Binary $02=USF pattern 1?
  (Further reconciliation needed — the mapping is not a simple offset.)
- Patterns cover C-2, F-2, D-2, G-2 basslines, instrument 2 (filter+pulse)

**Voice 3 (melody):**
- Orderlist: `0 1 1 1 ... 2 3 4 1 1 ... 5 6 4 ... 7 8 8 8...` (44 entries, loop@0)
- Binary orderlist at `$2050`: `05 05 ... 08 08 05 ... 09 09 05 ... 0A 0A 0A 0A FF`
- Wide variety of patterns: noise-tick arpeggios (inst 6/9), melody (inst 7/5), drum fills (inst 3/5)

**Pattern lengths** vary: 48, 96, 192, 384 ticks. Duration unit appears to be engine ticks
(with tempo=2, each tick = 2 VBI frames, so pattern of 96 ticks = 192 VBI frames ~= 3.84 sec at 50 Hz).

### 4.8 Effects Summary

Effects seen in Multi_Move instruments:
- **drum**: noise+triangle waveform sequence (ctrl bytes $08/$11/$17 etc.)
- **noise_tick**: single noise tick per note trigger
- **filter_program**: runs filter sweep program (prog 0)
- **wave_arp**: applies wave_arp table offsets to waveform control
- **tone_arp**: pitch arpeggio embedded in instrument stream
- **pulse_prog**: PWM sweep program (prog 1 or 2)
- **vibrato**: amplitude + speed parameters; onset=0 (immediate)

No glide/portamento visible in Multi_Move instruments or patterns.

---

## 5. Binary Engine Layout (Multi_Move.sid, $1800..$2289)

```
$1800..$1802   JMP $2108          ; init entry: full init
$1803..$1805   JMP $2117          ; song-change entry (sets mode=$02)
$1806..$182A   Play dispatcher    ; read mode byte, branch to main play or RTS
$182A..$1EFF   Main play engine   ; ~$681 bytes of player code
                                  ; routines: voice-loop, pattern-read, inst-load,
                                  ;   wave-prog, pulse-prog, filter, vibrato, drum
$1d60..$1d63   Code (tail of loop/jump)
$1d64..$1dc3   Freq table LO (96 bytes, 8 oct × 12 notes)
$1dc4..$1e23   Freq table HI (96 bytes)
$1e24..$1e55   [pulse prog / misc data area - $40-heavy]
$1e46..$1e55   Wave prog 0 freq bytes (10 bytes used, 16 allocated)
$1e56..$1e65   Wave prog 0 ctrl bytes (16 bytes)
$1e66..$1e75   Wave prog 1 freq bytes (same page, prog 0 and 1 interleaved?)
$1e76..$1e85   Wave prog 1 ctrl bytes
$1e86..$1e95   Wave prog 1 additional freq/data
$1ea1..$1ea3   Voice ptr table LO (3 voices: $00, $80, $50)
$1ea4..$1ea6   Voice ptr table HI (3 voices: $1F, $1F, $20)
               -> V1 orderlist @$1F00, V2 @$1F80, V3 @$2050
$1ea7..$1ed6   Instrument ptr table (16 × 2-byte lo/hi pairs)
               -> insts 0..10 at $21E0, $21E4, $21F9, $2203, ..., $226F
$1ed7..$1eFF   [misc data]
$1f00..$1f3F   Voice 1 orderlist (39 × $01, $FF = end)
$1f40..$1f7F   [unused / zeroed]
$1f80..$1fC1   Voice 2 orderlist (64 × instrument-pattern bytes, $FF)
$1fC2..$1fFF   [zeroed]
$2000..$204F   [code continuation — main play engine upper section]
$2050..$207F   Voice 3 orderlist (44 entries, $FF)
$2080..$20D8   [pattern data / code]
$20D9..$20E7   Init subroutine (zero $2121..., set mode=$00)
$20E8..$2107   Main play dispatch (LDX #2 loop, per-voice calls)
$2108..$2116   Full init entry (calls $20D9, clears $D400..$D417)
$2117..$211C   Song-change sub (set state $2174=$02)
$211D..$218F   Engine state variables (per-voice counters, ptrs, flags)
$21D0..$21DF   Instrument meta block (waveform + ADSR for inst 10)
$21E0..$2289   Instrument stream data (variable-length bytecode streams)
```

### 5.1 Engine State Variables at $211D..$2189

Key variables identified by tracing the play routine:
- `$211D`: speed counter reload value (= 1 for this tune)
- `$211E..$2120`: voice-X pattern indices (current playing pattern per voice, X=0,1,2)
- `$2121..$2123`: voice pattern position (offset into current pattern data)
- `$2124..$2126`: voice tick counter (remaining ticks for current note)
- `$2127..$2129`: voice segment counter (countdown to next orderlist advance)
- `$212A..$212C`: (other per-voice state)
- `$2142..$2144`: voice "instrument step" counters (incremented each play frame)
- `$214F..$2151`: transposition bytes (per voice)
- `$2167`: current instrument byte (scratch)
- `$2173`: main speed counter (decrements to 0, reloads from $211D)
- `$2174`: song mode ($00=playing, $01=end-loop, $02=silent/stopped)
- `$2176..$2178`: per-voice vibrato depth
- `$2180..$2182`: per-voice "noise tick" flags

### 5.2 Pattern Byte Encoding (Instrument Stream)

From disasm of play routine at `$18BE`..`$1957`:
- Byte `$FF` = end of instrument program (restart/loop)
- Byte `$FE` = end-of-song marker (set mode=$02, song done)
- Byte `$8X` = high bit set, low 7 bits: frequency adjustment / note data
- Byte `$CX` = instrument control command (set waveform/ctrl, X=sub-command)
- Byte `$EX` = effect command (X=effect type)
- Other bytes = note/duration data

Pattern stream bytes in the note data (orderlist→pattern):
- `$80` high bit set: some form of special marker
- `$40` bit set: vibrato/transpose control
- Plain bytes: note index into freq table

---

## 6. Cross-SID Binary Analysis

### 6.1 Header Parameters Across Selected SIDs

| File | Load | Init | Play | Binary size | Songs | Speed |
|------|------|------|------|-------------|-------|-------|
| Multi_Move | $1800 | $1800 | $1806 | $0A8A | 1 | 00000000 |
| JO_01 | $1000 | $1000 | $1006 | $0AC0 | 1 | 00000000 |
| Airwolf_Theme | $1000 | $1003 | $1009 | $0AD1 | 1 | 00000000 |
| Highlands | $3000 | $3000 | $3003 | $08D5 | 1 | 00000000 |
| Dreams | $C052 | $C052 | $C055 | $099B | 1 | 00000000 |
| Music_Demo | $6000 | $6000 | $6003 | $0B00 | 1 | 00000000 |
| Destiny_v1 | $43AB | $4F4F | $43AE | $0BE5 | 2 | 00000000 |
| A_r_cade_Sprint | $3000 | $3003 | $3000 | $12CA | 7 | 00000000 |
| Grid | $1000 | $1169 | $1000 | $027B | 1 | 00000000 |

All are VBI (speed=0 / PAL vblank), 6581, PAL. No CIA-timed tunes detected.

### 6.2 Grid.sid — Different Engine

Grid.sid (635 bytes, init=$1169, play=$1000) is a completely different, tiny player
— almost certainly the game's built-in player, NOT the JO composition engine. Size
alone (635 bytes) rules out the full JO engine (~2300 bytes of code).

### 6.3 First Digi.sid — Possibly Digi Content

First_Digi.sid (6705 bytes, play=$0000) is anomalous: play address = $0000 suggests
either no play routine (init-only?), or that the binary embeds digi sample data driving
the play via NMI/CIA. Needs separate investigation.

---

## 7. GitHub / External Disassembly Search Results

- **realdmx/c64_6581_sid_players**: Contains Audial_Arts, Bjerregaard, Deenen, Dunn, Galway,
  Gray (Fred+Matt), Hubbard, Kimmel, Ouwehand, Tel, Whittaker. **No Vibrants/JO entry.**
- **No dedicated GitHub repo** found for Vibrants/JO player disassembly.
- **jesper-olsen GitHub account** (github.com/jesper-olsen) exists with 37 repos but
  contains modern software projects, not C64 music tools.
- **codebase64.org music_players page**: page returned empty content (possible JS-dependent rendering).
- **Archive.org**: The JCH complete C64 collection (archive.org/details/jch_c64_zip) is by
  **Jens-Christian Huus (JCH)**, a different Vibrants member — NOT Poul-Jesper Olsen (JO).
  JCH released the editor + player source in that collection; JO never did.

---

## 8. Key Engine Characteristics (Summary)

1. **No published editor** — composed in assembler directly. Player code is bespoke per-tune
   with song data embedded in the same binary.

2. **Relocatable player** — load addresses vary wildly ($0800..$F000). The player code is
   fully position-independent (all addresses are absolute but the whole binary shifts).

3. **Split freq table** — LO and HI bytes in separate 96-byte blocks (not interleaved pairs).
   Standard PAL C64 tuning.

4. **Instrument stream format** — variable-length bytecode: ctrl bytes ($CX), freq data ($8X),
   effect commands ($EX), $FF=end. Wave programs and filter programs are separate indexed tables.

5. **Voice orderlist** — per-voice pointer-indexed list of pattern indices, terminated by $FF.
   Pointers stored in a 3-entry table (lo-bytes then hi-bytes at `$1EA1`/`$1EA4`).

6. **Tempo** — a global speed counter at `$2173` (reloads from `$211D`). Multi_Move uses
   tempo=2 (every-other-play-call advances). Other tunes may differ.

7. **Master volume** — $D418=$1F written at top of every play call (most tunes). Multi_Move's
   dispatcher pattern writes `A9 1F 8D 18 D4` as part of the main play path.

8. **Multi-subtune support** — init has two JMP entries (full-init and song-change). Song-change
   sets a mode byte; songs are addressed by subtune index.

9. **Effects used in Multi_Move**: drum, noise_tick, filter_program, wave_arp, tone_arp,
   pulse_prog, vibrato. No glide/portamento in this tune.

10. **Song mode state machine** — 3 states: $00=playing, $01=loop-at-end, $02=silent.
    $FE in pattern stream triggers mode=$02 (song-end).

---

## 9. Leads to Follow

1. **Fingerprint normalization** — build a relocation-normalized player fingerprint (strip
   load address, normalize absolute references). This will reveal how many of the 103
   apparent player "variants" are actually the same engine at different addresses. Expected
   result: likely 1–3 actual player revisions across the 105 SIDs.

2. **Wave program layout** — the interleaving of ctrl/freq bytes and the exact binary layout
   of wave_prog 0 freq bytes (found at `$1E46`, not adjacent to ctrl at `$1E56`) needs a
   second pass. The indexing scheme used by the play routine to locate wave program data
   should be traced from `$1D30`..`$1D5F` (the wave-prog dispatcher).

3. **Filter program binary location** — not yet found. Trace the filter-write code path
   (the routine that writes to `$D415`/`$D416`/`$D418` for filter) to locate the filter
   table start address.

4. **Pulse program binary location** — the area `$1E24`..`$1E55` has candidate data
   (`40 40 40 40 06 06 07 07 08 08 07 07`) matching segment-like patterns. Trace the
   pulse-prog dispatcher routine.

5. **Orderlist binary encoding** — the discrepancy between USF 0-based pattern indices and
   binary 1-based (or otherwise offset) indices needs reconciliation. Trace the code at
   `$185C`..`$186D` (the pattern-ptr lookup) to confirm the index mapping.

6. **Multi-subtune extraction** — `Destiny_v1.sid` (2 songs), `Bad_Track.sid` (3 songs),
   `A_r_cade_Sprint.sid` (7 songs), `Rautaudaw.sid` (5 songs) need song-change mechanism
   traced. The second JMP in the init dispatch likely loads a song-number-indexed offset
   into the voice orderlists.

7. **Grid.sid** — separate investigation; tiny binary (635 bytes) suggests a completely
   different game engine, not the JO composition player. May be worth excluding or treating
   as a different family.

8. **First_Digi.sid** — play address $0000 is anomalous. Investigate whether it's a digi
   tune (NMI/CIA driven) or has a corrupted header. If digi: document separately.

9. **sidid fingerprint** — run `sidid` against a representative set of JO SIDs to confirm
   which ones match the Vibrants/JO signature vs other engines (since Grid.sid is a known
   outlier, there may be others).

10. **Compare with Amok-era player evolution** — `01_1989.sid` (1989) vs `Multi_Move.sid`
    (1988) vs later tunes: trace whether the engine's instrument-stream command set evolved
    between 1988 and 1992.
