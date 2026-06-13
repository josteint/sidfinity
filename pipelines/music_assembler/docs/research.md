# Music Assembler

## Overview

- **HVSC count:** ~6,403 tunes
- **Authors:** Marco Swagerman (MC) and Oscar Giesen (OPM), Dutch USA-Team
- **Year:** 1989, published by Markt+Technik
- **Documentation:** Manual PDF at https://csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf
- **CSDb:** #94388

## Status & RE gaps (2026-06-13)

- **Migrated: 0 / 6,351.** No pipeline, no USF, no disassembly.s, no RE_NOTES.md yet.
- **This doc is manual/CSDb-derived, not RE-derived.** It describes the
  *editor's* data model. The **packed assembled-output format — the actual
  extraction target — is NOT reverse-engineered.** The "Assembled Output
  Format" section below is a placeholder: the player "disassembles intricate,
  unreadable data while playing," and that packed stream is what a migration
  must decode. This is the hard part and it is entirely open.
- **No player source exists** — MA was a closed commercial Markt+Technik
  product (cf. GoatTracker, where 13 versions of C source are bundled). The
  player must be RE'd from a binary. Likely multiple packer/version variants
  in HVSC (expect a version-group analysis akin to GT2's A/B/C/D).
- **Manual PDF is linked (csdb getinternalfile 137191), not vendored locally.**
  First acquisition step: pull it into this dir + run the `research-player`
  skill, then seed a disassembly of a representative member.
- **Representative members** (curated candidates, from `docs/canary_picker.md` §3):
  `MUSICIANS/R/Rage/Kalle_Kloakk_part_8.sid`,
  `MUSICIANS/K/Kleinert_Tim/Arcade_Intro.sid`,
  `MUSICIANS/0-9/4-Mat/Sub.sid`,
  `MUSICIANS/H/Harmony_Productions/War_at_33.sid`,
  `MUSICIANS/R/Remorhaz/Implosion.sid`.

## Key Concept

Not a tracker — it "assembles" complete standalone executables. Saving bundles the player routine + compressed music data into a relocatable binary. Base address user-selectable $0400-$FF00. Play via `SYS <base>`.

## Player Signature

- **Init address:** base + $0048
- **Play address:** base + $0021
- **IRQ setup:** base + $0000

## Data Structures

### Presets (Instruments) — 32 max, 8 bytes each

- ADSR envelope (2 bytes: AD, SR)
- Waveform byte (noise/pulse/saw/tri/disable/ring/sync/gate)
- Pulse rate (2 digits: LSB, MSB)
- Pulse effects (slide or vibrate mode with pulse byte/level/speed)
- Vibrato parameters (delay, speed, level)
- Arpeggio link (index into arpeggio table, or none)

### Arpeggios — 16 max

Each step has:
- Waveform byte
- Note offset (semitones, absolute with `<` or relative)
- Filter frequency value
- $FF = loop, $FE = stop

### Tracks — 3 separate (one per SID voice)

Each entry: sequence number ($00-$FD, $FE=stop, $FF=loop), transpose offset (0-15), repeat count.

### Sequences — Monophonic note lists

Each step:
- Note (C through B, across octaves)
- Duration ($00=16th, $01=8th, $03=quarter, $07=half, $0F=whole, $1F=double whole)
- Optional preset selection (PRE command)
- Optional modifiers: legato (Shift+note), hold, rest, portamento (2 extra columns), low-pass filter (3 params)

### Filter

Only low-pass supported. Shared across voices. Applied to triggering track and all lower-numbered tracks.

## Assembled Output Format

Player code + compressed data. The manual states data is "assembled into intricate, to many people unreadable data which is disassembled by the player routine while playing."

## File Types

- `s.filename` — complete song (player + data, relocatable)
- `p.filename` — presets only (shareable)
