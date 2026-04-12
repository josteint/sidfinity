---
source_url: https://csdb.dk/forums/index.php?roomid=14&topicid=97576&showallposts=1
fetched_via: direct
fetch_date: 2026-04-11
author: Hermit (primary contributor); also SIDWAVE, gegegege/gugugugu, NecroPolo (CSDb forum)
content_date: 2013-04-10 (thread start)
reliability: tertiary
---
# CSDb Sound Design Thread — DMC Technical Findings

Source: https://csdb.dk/forums/index.php?roomid=14&topicid=97576&showallposts=1
Thread title: "Sound Design hints & tips"
Started: 2013-04-10 by Hermit

---

## Primary DMC-Specific Technical Finding

### Sweep-Reset Disable Feature

From Hermit's post (2013-04-12):

> "Many trackers (like DMC, SW for example) support a setting to disable the 'sweep-reset' on sound start, so a new note won't start the sweep from the starting point but let it continue."

**What this means:**
- By default, when a new note triggers in a tracker, any ongoing pulse-width sweep or filter sweep is reset to its starting value.
- DMC has an instrument parameter (per-instrument flag) that disables this reset behavior.
- With sweep-reset disabled, the sweep continues from its current position when a new note is triggered.
- This allows continuous sweep progression across note retriggerings, enabling smoother timbral transitions in melodic passages.

**Usage context (from Hermit):**
- Used in "Pimp My Commodore" solo.
- Gives more variety to solo sounds.
- Also usable to simulate filter-cutoff automation in techno-like tunes when there are no pattern-effects available for that purpose.

**DMC tracker counterpart:**
- SID-Wizard (SW) implements the same feature — the two are mentioned together, confirming this is a known, named instrument parameter in both trackers.

---

## SID Sound Design Technical Context (general C64 tracker knowledge applicable to DMC)

These details were discussed in the thread and describe standard SID synthesis techniques that DMC instruments would implement.

### ADSR Guidelines

- **Decay = 0** is common practice for three reasons:
  1. The 1st frame waveform sounds shorter and more precise if Release > 3 (no time wasted traversing zero Attack + Decay phases).
  2. Sustain value controls per-note velocity (whereas Decay always reaches max volume peak first).
  3. Sounds start more precisely and align better in time.
- **Release > 3** is recommended for safe repetitive note triggering.
- For drums: Release values of 6..9 are typical.

### Waveform Values and Their Properties

Waveform register values (hexadecimal) as used in tracker waveform/gate programs:

| Value | Meaning |
|-------|---------|
| $81   | Noise + Gate — used for hard attack transient; "old hard-restart" style |
| $41   | Pulse + Gate |
| $40   | Pulse, Gate off |
| $11   | Triangle + Gate |
| $10   | Triangle, Gate off |
| $21   | Sawtooth + Gate |
| $31   | Sawtooth + Triangle (mixed) |
| $51   | Pulse + Triangle (mixed) |
| $61   | Pulse + Sawtooth (mixed) |
| $71   | Pulse + Triangle + Sawtooth (mixed) |
| $80   | Noise, Gate off |
| $09   | Test bit + Gate — "old type of hard-restart", stabilizes oscillator |
| $08   | Test bit only (pulse, no gate) — used for hardest punch in drums |

### Gate Bit Usage in Waveform Programs

- Gate bit can be cleared mid-program to produce percussive sounds with adjustable velocity.
- Example snare program (pulsewidth 50%): `81 41 41 80` — Gate cleared at 4th frame.
- Example kick program: `81 41 41 41 41 11 10`
- $09 (Test bit) in the 1st frame is the "old type of hard-restart" — considered less necessary in modern practice.

### Pulse-Width Sweep Parameters

- Pulsewidth is 12-bit, range $000–$FFF.
- $800 = 50% duty cycle (fattest/most symmetric sound).
- Towards $000 or $FFF: sharper, richer, more harmonics, less fat.
- No audible difference between very low ($100) and very high ($F00) — only polarity differs.
- Starting pulse values:
  - $100..$400 — thin solo sounds.
  - $500..$B00 — guitar-like "distorted sine" sounds.
  - Around $700 or $900 — typical solo start (more harmonics, less aggressive than $800).

**Sweep speed classification (SW values as reference):**
- Slow sweep: $08..$20 — "beautiful" solo sounds, majority of C64 tunes.
- Fast sweep: $20..$70 — choir-like effect, spectral variation, detuning feel; used in techno/trance.

### Keyboard Tracking

- Supported in SID-Wizard with 4-bit resolution.
- Effect: thinner pulsewidth for lower notes, fatter pulsewidth (near $800) for higher notes — mimics guitarist hand technique.
- Enhances variable feel on solo sounds.

### Vibrato Parameters

- Automatic delayed vibrato: delay of 8..20 frames before vibrato starts, so fast note-changes don't suffer intonation issues.
- Vibrato can be directional: upward only (like guitar without tremolo arm), downward only, or bidirectional.
- Increasing vibrato amplitude over time gives violin-like expression.

### Filter Sweep

- Filter cutoff resolution: 11-bit.
- On 6581: fast filter changes (cutoff/type/resonance) produce audible popping — wild filter programs should be avoided. Increasing frame speed reduces audibility.
- On 8580: clicks are much less audible.
- Sweeps should generally be bidirectional to avoid overflow at $00 or $FF.
- Solo filter usage options:
  1. Solo channel only filtered.
  2. Solo channel as primary filter controller (others follow).
  3. Another channel (e.g., bass) controls filter and solo channel uses same filter.

### Drum Sound Design (waveform program technique)

**Kick drum:**
- Structure: `81 CE` (noise at high pitch) → `41 C7 41 A7 41 A0` (pulse sliding down)
- The transition from noise hit to first pulse value is the key decision point for hardness.
- Pitch sequence should descend faster in early frames, slower in later frames.
- SIDWAVE's soft trance kick ending: `$11 07 11 04 11 02 11 00` — soft slide on the tail (WET).
- Hard kick: use high freq values ($B0+) at end.
- `$08` (Test/pulse) gives hardest smash.
- Combining with noise on another voice adds extra punch.

**Snare:**
- Example program: `81 41 41 80`
- Noise at high pitch ($D0..$EF range in SW/GT) for crack.
- Pulse at mid pitch ($98..$A8 range) for membrane resonance.
- Noise tail ($C0..$D0 range) for snare-wire simulation.
- Additional high-frequency layer on another channel: `51-81-81` style.

### Channel Combination (saving channels)

From gegegege/gugugugu (2013-04-12):

**Kick+bass mixing:**
- Kick needs only half a tick row (3 ticks at tempo 6).
- Follow `81-41-41` or `81-41-40` waveform with bass sound.
- Works best filtered, with different filter types for kick vs bass.
- ADSR like `6A` (Decay=6, Sustain=A) useful — kick needs high sustain, bass shouldn't be too loud.

**Snare+bass mixing:**
- Follow thump sequence with noise sequence on another channel.
- `51-81-81` style noise layer as HF component.

**Legato speed trick:**
- Fast tempos: create short distinct sound by direct legato to a higher note and back.
- Works best with low-pass filter.

### Delay Echo Technique (one-channel)

- Don't gate-off the note; instead decrease Sustain via pattern FX.
- Notes can change together with decreasing sustain (to notes 1–2 rows prior, or base key note).
- Backwards (increasing sustain) doesn't work without note retriggering.
- Two-channel echo: phase-delay second channel; echo channel more silent (different instrument or Sustain pattern effect).
- Drax's "Winterbird" technique: echo channel uses long Attack + legato.

### 1st-Frame Transient Tricks

- Octave up/down shift on frame 1 cheats ear into hearing doubled sound.
- Non-octave intervals (third, fourth) on frame 1 modify mood of solo.
- $81 (noise) + specific pitch on frame 1 simulates key-press click of real Hammond organ.

### Mixed Waveforms

- $51 (pulse+triangle) at $400..$700 pulsewidth — hammond-like sounds (idea from Shogoon's "Fun Factory" solo).
- Mixed waveforms + low-pass or mixed filter — brass-like sounds.
- Pulse-sweep is weakly audible with mixed waveforms; sound goes silent past a certain pulsewidth.
- After a certain pulsewidth value, sound becomes silent.
- On 6581: some mixed waveforms don't work as well as on 8580.

---

## Relevant Waveform Value Reference (from SIDWAVE post)

Drum construction formula:
```
81 ce   <- noise at high pitch (initial hit)
41 c7   <- pulse sliding down from here
41 a7
41 a0
```

Soft trance kick tail:
```
11 07
11 04
11 02
11 00
```

---

## Thread Participants and Context

- **Hermit** — Main contributor for technical sound design. Author of the DMC sweep-reset mention. Makes tunes in SID-Wizard. References "Pimp My Commodore", "Rakoczi Indulo", "Deep Though", "Arok 2013 invitro", "Lenore", "Garden Party cover", "The Loner cover".
- **SIDWAVE** — Drum construction expertise. Mentions using `$08` (pulse test-bit) for hardest drum smash.
- **gegegege/gugugugu** — Channel-combination techniques.
- **NecroPolo** — Known for ringmod/sync usage (mentioned by Hermit as "Cadmium" example).
- **chatGPZ, wacek, Soren, Yogibear, Flavioweb, Steppe, Linus** — General discussion, no additional DMC-specific technical content.

---

## Summary of DMC-Specific Parameters Identified

1. **Sweep-reset disable flag** — per-instrument setting; when enabled, pulse-width or filter sweep is NOT reset to start value on new note trigger. Sweep continues from current position.

This is the only explicitly DMC-named parameter in the thread. All other information describes general SID synthesis techniques that apply to DMC instruments as the underlying SID hardware behavior.

---

## Cross-References

- SID-Wizard (SW) implements the same sweep-reset disable feature.
- Goattracker (GT) is referenced as another tracker, but does not explicitly support sweep-reset disable in this discussion.
- DMC and SW are presented as the examples of trackers with this feature, implying it may NOT be universal.
