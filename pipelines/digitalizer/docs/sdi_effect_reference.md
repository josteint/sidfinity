---
source_url: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt (primary); http://chordian.net/c64editors.htm; https://www.lemon64.com/forum/viewtopic.php?t=24039; https://www.lemon64.com/forum/viewtopic.php?t=31585
fetched_via: direct (WebFetch, multiple redirects through SourceForge)
fetch_date: 2026-06-13
author: Geir Tjelta (GT) and Glenn Rune Gallefoss (6R6/GRG) of SHAPE; manual by Psylicium (2017)
content_date: SDI v2.1.6 docs (2013); v2.1.7 (2014)
reliability: primary (SDI 2.1.6 docs); secondary (forum posts)
---

# SID Duzz' It (SDI) v2.1 — Effect Reference

This document describes how each SDI effect maps to SID $D400–$D418 register writes
per tick/frame. All values hexadecimal. "OPEN" = needs RE of player source to confirm.

---

## SID Register Reference (3-voice layout)

| SID addr | Voice | Function |
|---------|-------|---------|
| $D400/$D401 | Voice 1 | Freq lo / hi |
| $D402/$D403 | Voice 1 | Pulse lo / hi |
| $D404 | Voice 1 | Voice ctrl (wave select + gate + sync + ring) |
| $D405 | Voice 1 | Attack/Decay |
| $D406 | Voice 1 | Sustain/Release |
| $D407/$D408 | Voice 2 | Freq lo / hi |
| $D409/$D40A | Voice 2 | Pulse lo / hi |
| $D40B | Voice 2 | Voice ctrl |
| $D40C | Voice 2 | Attack/Decay |
| $D40D | Voice 2 | Sustain/Release |
| $D40E/$D40F | Voice 3 | Freq lo / hi |
| $D410/$D411 | Voice 3 | Pulse lo / hi |
| $D412 | Voice 3 | Voice ctrl |
| $D413 | Voice 3 | Attack/Decay |
| $D414 | Voice 3 | Sustain/Release |
| $D415 | Filter | Cutoff lo (bits 0–2 used, bits 3–7 unused per SID spec) |
| $D416 | Filter | Cutoff hi (bits 0–7) |
| $D417 | Filter | Resonance (bits 4–7) + voice routing (bits 0–3) |
| $D418 | Master | Master volume (bits 0–3) + filter output select (bits 4–7) |

---

## 1. Note / Frequency

**Effect:** Setting note pitch for a voice.  
**Trigger:** Any non-tie note in the sequence NOTE column.  
**SID writes:**
- $D400/$D401 (or $D407/$D408 or $D40E/$D40F) — 16-bit frequency value from
  note frequency table at $EE00.
- For waveform program "soft" notes ($00–$5F or $60–$7F in note column): the
  SID frequency = base note frequency ± offset. OPEN: offset in semitones or
  raw frequency units?
- For "fixed" notes ($80–$DE): frequency overrides base note entirely.

**Gate:** Uppercase note → gate bit in voice ctrl set to 1 ($D404/$D40B/$D412 |= $01).
Tie note (lowercase) → no gate change.

---

## 2. Instrument Select

**Effect:** Switch to a different instrument.  
**Trigger:** FX column $00–$1F in channels 1–3.  
**SID writes per tick (instrument change):**
1. Attack/Decay: write to $D405/$D40C/$D413 (only on note-on or hard restart)
2. Sustain/Release: write to $D406/$D40D/$D414 (only on note-on or hard restart)
3. Waveform program restarted from beginning.
4. Pulse/filter/vibrato programs restarted.

---

## 3. Waveform Program — per tick writes

**Effect:** Sequence of voice-ctrl byte writes per tick; can include note offsets.  
**SID writes each tick:**
- $D404/$D40B/$D412 ← waveform byte from program ($10, $20, $40, $80, or combinations + gate bit $01)
- $D400/$D401 (etc.) ← note frequency, possibly adjusted by note byte

**Waveform program commands and their SID writes:**

### FF — Jump
No SID write. Redirects program counter to line $XX.

### FE — Delay
No SID write for $XX frames. Program suspended.

### FD — ADSR change
SID writes:
- $D405/$D40C/$D413 ← new Attack/Decay value (from next program line)
- $D406/$D40D/$D414 ← new Sustain/Release value
- Optionally: gate off ($D404 etc. &= ~$01) after $XX frames if XX=$01–$7F

### FB — Multipulse
SID write: switches between two pulse programs. Triggers pulse writes to
$D402/$D403/$D409/$D40A/$D410/$D411 at speed controlled by FB parameter.

### FA — Repeat
No SID write. Modifies jump counter for following FF.

### F0–F7 — Filter cutoff low bits
SID write:
- $D415 ← $F0–$F7 (sets lower 3 bits of filter cutoff frequency)
Note: $F0 writes $F0 to $D415 — the upper 5 bits of $D415 are not meaningful
on the SID (only bits 0–2 are used per MOS 6581 spec), so this effectively
sets the 3 low cutoff bits.

### EE — Pulse Init
SID writes:
- $D402/$D403 (or per-voice pulse registers) ← pulse lo|hi from parameter

### ED — Pulse Subtract
SID write:
- Current pulse value -= parameter → write result to pulse register

### EC — Pulse Add
SID write:
- Current pulse value += parameter → write result to pulse register

### EB — Pulse Write
SID write:
- $D402/$D403 (etc.) ← lo|hi pulse value (direct, bypasses pulse program)

### E2–E7 — Noise trick
SID write:
- $D404/$D40B/$D412 ← $E2–$E7 (non-standard waveform register values for
  metallic noise variants; SID interprets upper bits as wave select)

---

## 4. Gate Timeout / Hard Restart

**Effect:** Controls when gate goes off after note-on, and how the voice is reset
for the next note.  
**SID writes (on next note after gate timeout):**

**Hard restart (modes 1–4):**
OPEN: exact byte sequences not documented. Typical C64 hard restart = write $00 to
voice ctrl ($D404 etc.), then delay 1 frame, then write new ADSR + waveform + gate.
SDI has 4 "hard" and 4 "soft" variants — likely differ in the delay duration and/or
whether ADSR is reset before the new note.

**Soft restart (modes 1–4):**
OPEN: Soft restart likely writes the new waveform+gate byte without first clearing the
voice ctrl register. Mode 4 (E1–FF) ≈ tie note — no restart at all.

---

## 5. Vibrato Program

**Effect:** Frequency modulation oscillating around the base note frequency.  
**SID writes each tick:**
- $D400/$D401 (etc.) ← note frequency ± vibrato offset
- Offset oscillates based on width (c3) and speed (c4)

For detuning mode (c2=$00 or $FE): frequency adjusted by a fixed delta rather than
oscillating. Both ends of the delta come from c3 (lo) and c4 (hi).

OPEN: whether the vibrato/detune adds to the 16-bit SID frequency value directly or
adds semitone offsets looked up from the frequency table.

---

## 6. Pulse Width Modulation (Pulse Program)

**Effect:** Animate the pulse width register per tick.  
**SID writes each tick (while program active):**
- $D402/$D403, $D409/$D40A, or $D410/$D411 ← 16-bit pulse value (lo | hi)
- Sweep applied per tick: current_pulse += speed (or -= for reverse modes)

Sweep stops or loops per c5 mode byte. Direct pulse writes via $EB–$EE waveform
commands bypass the program entirely.

---

## 7. Filter Program

**Effect:** Animate the filter cutoff frequency per tick.  
**SID writes each tick (while program active):**
- $D416 ← filter cutoff hi byte (from sweep)
- $D415 ← filter cutoff lo 3 bits (from $F0–$F7 waveform commands, or left from last write)

**Special filter frame mode (c3=$00):**
- $D416 ← c2 value (direct write)
- $D417 ← c4 value (band/resonance)
- Delay c5 frames before next line

Filter enables (routing voices to filter) are written via:
- $D417 bits 0–2 = voice 1/2/3 filter enable
- $D418 bits 4–6 = filter output mix select (LP/BP/HP)
These come from the BAND/RESONANCE instrument field and channel 4 FX $70–$7F.

---

## 8. Arpeggio

**Effect:** Rapid note cycling to emulate chords; driven by waveform program.  
**SID writes per tick:**
- $D404/$D40B/$D412 ← arpeggio waveform byte ($91/$A1/$B1/$C1/$D1/$E1)
- $D400/$D401 (etc.) ← frequency of current arpeggio note (base + arpeggio offset)

Arpeggio speed determines how many ticks per note step. The arpeggio data at $E300
contains note offsets; the program counter advances at the rate given by the speed
nibble in the arpeggio program column 4 byte.

---

## 9. Glide / Portamento

**Effect:** Pitch slide from current note to target note.  
**Trigger:** FX column $21–$3F in channels 1–3, with a NOTE column target pitch.  
**SID writes each tick:**
- $D400/$D401 (etc.) ← current sliding frequency (± delta per tick toward target)

OPEN: which SID register the delta is applied to (frequency lo, frequency hi, or
both 16-bit). OPEN: whether glide adds to the 16-bit frequency value or uses a
separate note-number counter.

Two glide variants:
- **Hard glide** (uppercase NOTE): new note triggers gate restart + starts slide
- **Tie glide** (lowercase NOTE): slide continues without envelope restart

---

## 10. Sustain / Release / Attack change (FX $70–$7F)

**Effect:** Modify envelope parameters mid-sequence.  
**Trigger:** FX column $70–$7F.  
**SID writes:**
- One of $D405/$D40C/$D413 or $D406/$D40D/$D414 ← new value from NOTE column
OPEN: exact mapping of $70–$7F FX values to which envelope registers.

---

## 11. Channel 4 — Tempo

**Effect:** Change global playback speed.  
**Trigger:** FX column $01–$1F in channel 4.  
**No SID writes.** Changes the IRQ timing (frame rate for play routine invocation).

---

## 12. Channel 4 — Transpose

**Effect:** Global pitch shift for all 3 music channels.  
**Trigger:** NOTE column in channel 4 (combined with tempo FX).  
**No direct SID writes.** Shifts note frequency lookups: all 3 voices compute their
frequencies from (sequence_note + transpose) into the $EE00 frequency table.

---

## 13. Channel 4 — Filter Override

**Effect:** Force a specific filter program or filter routing globally.  
**Trigger:** FX $21–$3F (force filter program), $61–$67 (force filter band),
$70 (return to per-instrument filter), $71–$7F (force filter output).  
**SID writes:**
- $D415/$D416 ← filter cutoff (from forced filter program, if $21–$3F)
- $D417 ← resonance + channel routing (if $61–$67 or $71–$7F)
- $D418 ← filter output mix (if $71–$7F)

---

## 14. Initial Volume / Fade

**Effect:** Set master volume or fade in/out.  
**Trigger:** INVOL table (per-tune) or fade-out call ($1006).  
**SID writes:**
- $D418 bits 0–3 ← volume value ($0=silent, $F=full)
- Fade: each call to $1006 decrements volume toward target

---

## 15. Filter Channel Enable (Per-Instrument)

**Effect:** Route a specific voice through the SID filter.  
**Source:** BAND/RESONANCE instrument field (non-$00 value).  
**SID writes (on note-on or voice change):**
- $D417 ← resonance bits (high nibble) + voice routing (low nibble)
- $D418 ← filter output mix bits (LP/BP/HP select)

---

## Selectable Effects for Export

When dumping music for a demo/game, unused effects can be disabled in the player
source to reduce CPU time and code size. From the manual (identified labels):

```
rem_4ch    rem_det    rem_gout   rem_1wf    rem_wfd    rem_adsr
rem_mp     rem_wfr    rem_wf0    rem_puw    rem_pu     rem_we2
rem_arp    rek_fi     rem_fspd   rem_glid   rem_vib    rem_cc
rem_fad    rem_gat    rem_f20    rem_wfo    rem_voff   rem_trkl
rem_tp     rem_opt    spdchan
```

Likely meanings (OPEN — need player source to confirm):
- rem_4ch = remove channel 4 (control channel)
- rem_det = remove detune
- rem_gout = remove gate-out timer
- rem_1wf = remove 1-frame waveform
- rem_wfd = remove waveform delay
- rem_adsr = remove ADSR change in waveform program
- rem_mp = remove multipulse (FB command)
- rem_wfr = remove waveform repeat (FA command)
- rem_wf0 = remove waveform command $F0–$F7
- rem_puw = remove pulse program (write mode)
- rem_pu = remove pulse program (all)
- rem_we2 = remove $E2–$E7 noise trick
- rem_arp = remove arpeggio
- rek_fi = remove filter
- rem_fspd = remove filter speed
- rem_glid = remove glide
- rem_vib = remove vibrato
- rem_cc = remove ?
- rem_fad = remove fade
- rem_gat = remove gate timeout
- rem_f20 = remove FX $20 (filter on/off)
- rem_wfo = remove waveform offset
- rem_voff = remove voice off
- rem_trkl = remove track loop
- rem_tp = remove tempo program
- rem_opt = frame-player-only optimisation
- spdchan = speed channel control

---

## Drum Programming (from manual examples)

Three built-in drum presets demonstrating which parameters produce percussion:

**Snare drum:**
- WAVEFORM PRG: $00, AD: $08, SR: $88, GATE TIMEOUT: $22
- All other fields: $00
- Uses noise waveform ($80) in waveform program

**Bass drum:**
- WAVEFORM PRG: $07, AD: $08, SR: $86, GATE TIMEOUT: $22
- PULSE PRG: $88 (infinite pulse sweep)
- Uses pitch-decreasing waveform program

**Bass drum variant:**
- WAVEFORM PRG: $0D, SR: $86, GATE TIMEOUT: $20
- PULSE PRG: $01 (one-shot pulse sweep)

---

## Leads to follow

- OPEN: Hard restart 1–4 and soft restart 1–4 exact SID write sequences. Critical for
  understanding how envelope articulation differs between the 8 modes. Needs RE of
  player source (`s.sdi21-n49`).
- OPEN: Glide SID register write formula — is it a 16-bit frequency add or a note-number
  (semitone) step? Impacts whether Digitalizer → SDI mapping preserves glide granularity.
- OPEN: Arpeggio note offset semantics — raw 16-bit frequency delta vs semitone table
  lookup. If semitone: which octave is the base?
- OPEN: What FX values $70–$7F exactly do — which nibble selects release vs sustain
  vs attack, and what does the NOTE column carry?
- OPEN: Player source `rem_cc` label — "cc" likely = "clear" or "chord" or "cutoff";
  purpose unclear from name alone.
- SOURCE: Player source files in the SDI distribution ZIP (`Sid_Duzz_It_v2.1.7-shape.zip`)
  under the Turbo Assembler format. Files named `s.sdi21-n49` and `s.sdi21-spd49`.
  These directly show every SID register write for every effect.
- SOURCE: SDI 2.1.7 PDF manual (Psylicium, 2017, CSDb #153760) has a corrected
  arpeggio chapter. Fetch from psylicium.dk for the arpeggio semantics.
