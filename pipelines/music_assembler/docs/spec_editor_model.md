<!--
provenance:
  source_url: https://csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf  (CSDb release #94388)
  fetched_via: csdb_manual_0_01b.pdf already vendored in this docs dir (txt extract: csdb_manual_0_01b.txt)
  fetch_date: 2026-06-13
  author: Marco Swagerman (MC), "Music Assembler 1.0 User Manual", version 0.01b, September 2010
  content_date: 2010-09 (manual); product 1989 (Dutch USA-Team / Markt+Technik)
  reliability: HIGH for the editor-side data model (author's own manual). Note: the manual
               describes what the COMPOSER edits, NOT the packed runtime encoding (which is
               in spec_player_RE_grounded.md). The author explicitly states the packed data
               is "intricate, to many people unreadable data which is disassembled by the
               player routine while playing."
-->

# Music Assembler — editor data model (from the author's manual)

Consolidated from MC's official 2010 manual (full text in
`csdb_manual_0_01b.txt`). This is the **musical basis** for the USF mapping;
the on-disk packed encoding of these structures is in
`spec_player_RE_grounded.md`.

## Top-level structure

- Not a tracker. "Assembles" a standalone relocatable executable = player
  routine + compressed data. Playable from BASIC via `SYS <base>`
  (e.g. `SYS 49152` for a $C000 build). Base selectable $0400-$FF00.
- Three independent tracks (one per SID voice). Each track is a list of
  (sequence#, transpose, repeat). Sequences are **monophonic** note lists.
- File types: `s.<name>` = full song (player + data, relocatable);
  `p.<name>` = presets only (shareable preset bank).

## Presets (instruments) — 32 max, 8 bytes each

The manual states each preset is exactly **8 bytes** and stores:
- **ADSR** envelope (AD byte, SR byte) — 2 bytes.
- **Waveform** byte (standard SID control bits): `$80` noise, `$40` pulse,
  `$20` saw, `$10` triangle, `$08` disable oscillator, `$04` ring mod,
  `$02` sync, `$01` gate. Example `$21` = saw + gate.
  - **Hard reset**: waveform `$09`/`$08` (both stored as `$08` by the player)
    switches the oscillator OFF at note end instead of releasing the gate;
    used with an arpeggio to pick the real waveform. ("$09/$08 → $08"
    conversion is done by the player — confirms a player-side normalisation.)
- **Pulse rate** — one byte, "left digit = LSB, right digit = MSB". Pure
  pulse = `$08`.
- **Pulse effects** (F3/F5 toggle): "Pulse Slide" (add *pulse byte* to pulse
  rate every frame — ramp); "Pulse Vibrate" (add/subtract *pulse level* for
  *pulse speed* frames, then reverse — triangle PWM).
- **Vibrato**: delay (frames before vibrato starts), speed (frames per
  direction flip), level (freq add/subtract amount).
- **Arpeggio link**: index into the 16-arpeggio table, or none. Using an
  arpeggio **cancels vibrato** for that preset. Arpeggios are **overruled by
  portamento** from the sequence.

## Arpeggios — 16 max

Each step = (waveform, note offset, low-pass filter freq). Terminators in the
waveform column: `$FF` = loop, `$FE` = stop. Note offset is either relative
(added to the triggered note) or **absolute** (denoted `<`, replaces the note).
`$0C` = one octave. One step plays for 1/50 s. Multiple presets may share one
arpeggio. Example arpeggios from the manual:
```
chord:           41 00 00 / 41 04 00 / 41 07 00 / FF
percussion tri:  81 5F< 00 / 11 00 00 / FE
```

## Tracks — 3, one per voice

Each entry: **sequence number** `$00..$FD` (`$FE` = stop, `$FF` = loop track),
**transpose** offset 0-15 semitones, **repeat** count (0 = play once, 1 =
twice...). Sequence numbers must be contiguous (no gaps). Song speed F1-F8.
(In the grounded player: the loop/stop sentinels and transpose are exactly the
`$C08D,X` seq# and `$C0E6,X` transpose state bytes; transpose is read from the
HIGH NIBBLE of `$C0E6,X` via `LSR×4` — see RE doc.)

## Sequences — monophonic note lists

Each step: note (C..B; standard or German H-notation) + **duration**, plus
optional modifiers. Durations count from 0:

| Entered | Actual length |
|---------|---------------|
| `$1F` | double-whole ("see you tomorrow") |
| `$0F` | whole |
| `$07` | half |
| `$03` | quarter |
| `$01` | 8th |
| `$00` | 16th |

(Player-side: the duration is the low 5 bits, `AND #$1F`, dropped into the
note-duration counter `$C08A,X` — RE doc confirms the `$1F` mask.)

Optional per-step modifiers:
- **PRE** — preset select (P key); preset index in a second column.
- **Legato / no-trigger** (Shift+note, shown `<`) — play note without
  re-triggering ADSR. Used at the end of a slide.
- **Hold** — sustain current note up to 2 whole notes; stackable; does NOT
  release.
- **Rest** — like hold but enters Release phase.
- **Portamento / slide** (Shift+S on the from-note): two extra columns =
  LSB (fine) + MSB (coarse). Downward slide = last column `$FF`/`$FE` (-1/-2).
  ODD fine value → "rattling" slide (effect applied only every other frame).
  Slide cancels arpeggio + vibrato for its duration.
- **Low-pass filter** (Shift+F on the note-length column): three params packed
  into two extra columns. First column split into two nibbles: nibble 1 =
  starting cutoff (0 lo .. F hi); nibble 2 = ramp direction+rate per the
  manual table below. Last column = number of frames to apply.

Filter ramp table (manual, verbatim):
```
7 down 2/frame   9 up 2/frame
6 down 4/frame   A up 4/frame
5 down 6/frame   B up 6/frame
4 down 8/frame   C up 8/frame
3 down 10/frame  D up 10/frame
2 down 12/frame  E up 12/frame
1 down 14/frame  F up 14/frame
0 down 16/frame  8 hold steady
```
(Grounded player: the filter cutoff ramp is the `$C296` down-counter +
`ADC #$F0 / STA $D416` ramp at `$C299`; only `$D416` (cutoff HIGH) is touched.)

## Filter / track interaction

Only low-pass. One shared filter for all three oscillators. Filtering is
applied to the **triggering track and all lower-numbered tracks** (track 3 →
also 2,1; track 2 → also 1). The owning track index is computed at init from
the low nibble of `$D417` and stored in `$C262` (RE doc).
