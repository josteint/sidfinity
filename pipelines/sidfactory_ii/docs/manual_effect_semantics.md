---
source_url: https://github.com/Chordian/sidfactory2/releases/download/release-20260314/SIDFactoryII-linux.zip
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (documentation); Thomas Egeskov Petersen (driver code)
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - http://files.chordian.net/sf2/SIDFactoryII_20260314_User_Manual.pdf (primary PDF manual)
  - https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-4-instruments/
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/driver/driver_info.cpp
---

# SID Factory II — Effect Semantics Reference

This file maps every driver 11 effect/command to the SID register(s) it writes,
the per-frame update model, and the musical semantics.

SID register base addresses: Voice 1 = $D400, Voice 2 = $D407, Voice 3 = $D40E.
Per-voice offsets:  +0/$1 = freq lo/hi,  +2/$3 = PW lo/hi,  +4 = control,  +5/$6 = AD/SR.
Global: $D415/$D416 = filter cutoff lo/hi, $D417 = resonance+routing, $D418 = mode+main-vol.

---

## 1. Note Trigger (Gate On)

**SID registers written:**
- Voice+4 (control): set gate bit ($01) along with the waveform bits
- Voice+5 (AD): attack/decay from instrument byte 0
- Voice+6 (SR): sustain/release from instrument byte 1
- Voice+0/1 (freq lo/hi): frequency from note lookup table

**Per-frame:** Happens once on the row where a note value (0x01–0x6F) appears in the sequence.
The note number maps to a frequency via a lookup table in the driver (standard equal-temperament,
8 octaves, PAL clock = 985248 Hz; freq = round(clock * pitch_hz / 16777216)).

**Tie note (`**`):** When the tie flag is set (0x90–0x9F duration range), the gate bit is NOT
cycled — there is no gate-off/gate-on edge. Instrument ADSR and wave program are NOT restarted.
Useful for smooth portamento and sustained notes.

---

## 2. Gate Off (`---`)

**SID registers written:**
- Voice+4 (control): clear gate bit ($01); waveform bits unchanged

**Per-frame:** Written once on the `---` row. The ADSR envelope enters the release phase.

---

## 3. Hard Restart

**Mechanics:** Triggered when bit 7 ($80) is set in instrument byte 2.
The driver counts ticks and fires hard restart **exactly 2 frames** before the next note.

**Frame N-2:**
- Voice+4: oscillator reset waveform ($09 = test bit $08 + gate $01) written
- Voice+5: HR table AD written (typically $0F = attack 0, decay F)
- Voice+6: HR table SR written (typically $00 = sustain 0, release 0)
- Gate: cleared (gate bit in control = 0) — effectively $08 written (test bit, no gate)

**Frame N-1:** HR state continues (the ADSR hardware stabilizes).

**Frame N (new note):**
- Voice+4: new waveform (from wave table) with gate bit set
- Voice+5: instrument AD
- Voice+6: instrument SR
- Voice+0/1: note frequency

**Purpose:** Eliminates "school band effect" — the ADSR hardware quirk where rapid re-triggering
of notes with certain ADSR values causes inconsistent envelope shapes. HR forces a clean ADSR
reset 2 frames early, so the next note always starts from a known state.

---

## 4. Oscillator Reset (Test Bit)

**Trigger:** Instrument byte 2 bit 4 ($10).

**SID registers written (frame 0 of a new note):**
- Voice+4: $09 written (test bit $08 + gate bit $01; this resets/seeds the noise LFSR
  and holds the pulse/triangle oscillator at phase 0)

This is used to synchronize the oscillator phase for predictable noise + pulse starts.
Especially important when switching from another waveform to noise ($81), which requires
an oscillator reset to seed the noise register.

---

## 5. Wave Table Effect

**Per frame:** The wave table index advances by 1 each driver tick. The current row is applied.

**SID registers written per row:**
- Voice+4 (control): waveform byte (byte 0) written, including gate bit
- Voice+0/1 (freq lo/hi): computed from semitone offset or absolute semitone value

**Waveform → SID control byte mapping (common values):**
```
$11 — triangle:   $D404/$D40B/$D412 = $11 (tri waveform + gate)
$21 — sawtooth:   = $21
$41 — pulse:      = $41
$81 — noise:      = $81
$31 — tri+saw:    = $31 (ring mod sound in SID)
$51 — tri+pulse:  = $51
$61 — saw+pulse:  = $61
$71 — tri+saw+pulse = $71
$09 — test/reset: = $09 (used for HR and oscillator reset)
```

**Semitone note calculation (byte 1 = $00–$7F):**
- base_note = note from sequence + orderlist_transpose + byte_1_semitones
- freq = lookup_table[base_note]
- Written to Voice+0 (lo byte) and Voice+1 (hi byte)

**Absolute semitone (byte 1 = $80–$DF):**
- freq = lookup_table[byte_1 - $80]  (or similar encoding — exact table offset may vary)
- Sequence note value and order-list transpose are IGNORED
- Used for drums and fixed-pitch effects

**Arpeggio interaction:**
- When byte 1 = $00 AND a T3 arpeggio command is active, the arpeggio table value is ADDED
  to the base note before the lookup.
- When byte 1 ≠ $00, the arpeggio is bypassed for that row.

---

## 6. Pulse Program Effect

**Per frame:** Pulse table advances by 1 row after the hold counter (YY) reaches 0.

**SID registers written:**
- Voice+2 (PW lo byte): bits 3-0 of the 12-bit pulse width
- Voice+3 (PW hi byte): bits 11-4 of the 12-bit pulse width (4 bits used)

**Set pulse row ($8X XX YY):**
- Writes the new 12-bit value directly: PW_hi = XXX >> 4, PW_lo = XXX & $FF
- Holds for YY frames before advancing

**Add pulse row ($0X XX YY):**
- Adds signed XXX to the current 12-bit PW value (wraps at 12-bit boundaries)
- Applies the addition every frame, holds YY frames total before advancing

**Jump row ($7F -- XX):**
- Redirects execution to row XX in the pulse table
- Jump to self = sustain current pulse without further change

**Pulse reset on note-on:**
Normally, the pulse program restarts from the instrument's pulse table index when a new note
triggers. With bit 3 ($08, driver 11.05+) in instrument byte 2 set, the pulse program is NOT
reset unless the instrument is explicitly set (e.g., carrying a tie note through does not reset it).

---

## 7. Filter Program Effect (Command Ta / Instrument bit 6)

**Filter activation:** Either via command `Ta -- XX` (sets filter program index to XX) or via
instrument byte 2 bit 6 ($40) with filter table index in instrument byte 3.

**Per frame:** Filter table advances by 1 row after the hold counter (YY) reaches 0.

**SID registers written per Set-Filter row ($XY YY RB):**
```
$D415 — filter cutoff lo (bits 2-0 of 11-bit value)
$D416 — filter cutoff hi (bits 10-3 of 11-bit value)
$D417 — (R << 4) | B  where R=resonance nibble, B=voice bitmask (bits 2-0)
$D418 — (mode_bits) | main_volume  where mode_bits from X nibble ($9x–$Fx)
         bit 7 = HP, bit 6 = BP, bit 5 = LP
```

**Filter mode → $D418 bits 7-5:**
```
$9x — HP+BP:    $D418 bits 7,6 set  = %11000000
$Ax — HP only:  $D418 bit 7 set     = %10000000
$Bx — BP only:  $D418 bit 6 set     = %01000000
$Cx — HP+LP:    $D418 bits 7,5 set  = %10100000 (notch)
$Dx — BP+LP:    $D418 bits 6,5 set  = %01100000
$Ex — LP only:  $D418 bit 5 set     = %00100000
$Fx — all:      $D418 bits 7,6,5    = %11100000
```

**Filter routing (bitmask B in $D417):**
- bit 0 ($01) = voice 1 filtered
- bit 1 ($02) = voice 2 filtered
- bit 2 ($04) = voice 3 filtered
- Combined: $03 = voices 1+2; $07 = all voices; $04 = only voice 3

**[11.03] Per-instrument filter enable (bit $20):**
When set in the instrument, the channel's bit in $D417 is combined (OR'd) with the
bitmask B from the filter program row. This allows per-voice filter routing control
from the instrument definition rather than hardcoding it in the filter program.

**Add-to-cutoff row ($0X XX YY):**
- Signed XXX is added to the current 11-bit cutoff value each frame
- YY = frame count before advancing to next row

---

## 8. Slide Up/Down (Command T0)

**SID registers written per frame (while active):**
- Voice+0 (freq lo) and Voice+1 (freq hi): 16-bit frequency value updated by ±speed per frame

**Speed:** XXYY is a 16-bit signed delta added directly to the raw SID frequency register
each driver frame. Positive = pitch up; negative (two's complement) = pitch down.

**Duration:** Continues until a new note triggers or the command changes. There is no auto-stop.

---

## 9. Vibrato (Command T1)

**SID registers written per frame (while active):**
- Voice+0 / Voice+1 (freq lo/hi): frequency oscillates ±amplitude around the base pitch

**Parameters:**
- XX = frequency (period): how fast the vibrato oscillates (larger = slower)
- YY = amplitude: depth of the frequency deviation (SMALLER = STRONGER — counter-intuitive)

**Update model:** The driver uses a sine-like LFO. Every frame the LFO advances by XX steps
through a lookup table, then scales the amplitude by YY to produce a frequency delta that is
added to (or subtracted from) the base note frequency.

---

## 10. Portamento (Glide) (Command T2)

**SID registers written per frame:**
- Voice+0 / Voice+1 (freq lo/hi): slides toward target frequency by XXYY per frame

**Semantics:** When a new note triggers with portamento active, instead of jumping to the
new note's frequency immediately, the frequency register is nudged by ±XXYY per frame
until it reaches the target. The "tie note" (**) flag in the sequence is typically used
with portamento to prevent gate re-triggering during the glide.

**Stop portamento:** Use command `T2 80 00` (speed = $8000 = overflows quickly to target
or: use `T2 02 80 00` as noted in the documentation to disable a runaway portamento).

---

## 11. Arpeggio (Command T3)

**SID registers written per frame:**
- Voice+0 / Voice+1 (freq lo/hi): cycles through note frequencies from the arp table

**Parameters:**
- XX = arpeggio speed (how many frames per arp step)
- YY = arpeggio table index (which arp pattern to use)

**Update model:** The arp table is stepped through at rate XX. Each arp table entry specifies
a semitone offset. That offset is added to the base note to produce the arpeggio tone.
The arp table uses a relative $7X jump to create loops.

**Wave table interaction:** Arp is ONLY applied when the current wave table row has semitone
offset byte = $00. If the wave table specifies a non-zero semitone offset, the arp is ignored
for that frame.

---

## 12. ADSR Commands (T8, T9)

**SID registers written:**
- Voice+5 (AD): from XX byte of command
- Voice+6 (SR): from YY byte of command

**T8 — Local ADSR:** applies to the current note only; reverts on next note trigger.
**T9 — Instrument ADSR:** persists until a different instrument is explicitly selected in the sequence.

Both T8 and T9 override the instrument's byte 0/1 AD/SR for the current voice.

---

## 13. [11.02+] Main Volume Command (Te)

**SID register written:**
- $D418 (bits 3-0): main volume = X (0–F)

Bits 7-4 of $D418 (filter mode) are preserved. The X nibble is written to the low 4 bits.

---

## 14. [11.02+] Tempo Program Command (Td)

**No SID register written directly.** Updates the internal tempo counter pointer to row XX
of the tempo table. Causes an immediate tempo change (takes effect on the next row).

---

## 15. [11.02+] Pulse Program Index Command (Tc)

**SID registers written:** same as pulse table (see §6)

Sets the pulse program pointer for the current voice to row XX in the pulse table.
Equivalent to a "jump to a specific pulse program from a command" — useful for
triggering a different pulse sweep in the middle of a sequence without changing the instrument.

---

## 16. [11.04] Note Delay

**No SID write on the row itself.** Inserts T ticks of silence before the note triggers.

The note event is deferred by T ticks (0–15). During those ticks the previous note state
continues. Then on tick T+1 the normal note-on occurs (gate, ADSR, wave table, etc.).

---

## 17. [11.01-11.04] Fret Slide (Command T4)

**Removed in driver 11.05.**

**SID registers written per frame:**
- Voice+0/1 (freq lo/hi): slides by ±speed until YY semitones have been traversed

XX = 00–7F: slide up; XX = 80–FF: slide down.
YY = semitone distance to slide (stops automatically after YY semitones).
Different from T0 (which runs indefinitely) and T2 (which slides to a target note).

---

## 18. Tf — Demo Value / Sync

**No SID register written.** Internal counter incremented by XX. Used for demo sync / timing.

---

## Effect Priority and Interaction Notes

1. **Wave table vs arpeggio:** Wave table runs every tick. Arp only modifies the frequency
   computed from wave table rows where the semitone add byte = $00.

2. **Slide (T0) vs portamento (T2):** Both modify the frequency register. They are independent
   commands — using both simultaneously produces combined pitch changes.

3. **Filter program (Ta) vs instrument filter ($40):** The filter program runs the same table
   regardless of which voice triggered it. The instrument bit $40 only starts the program;
   the program itself applies globally to the SID's single filter.

4. **Hard restart timing:** Hard restart begins 2 frames before the next note. If the sequence
   row duration is 2, hard restart fires on the same frame as the note-on in practice — this is
   the minimum safe duration with hard restart enabled (as noted in the manual).

5. **Gate ON (`+++`) does NOT reset the wave table or ADSR.** It only sets the gate bit in
   Voice+4. The wave table and pulse table continue from their current positions.

6. **Tie note (**) combined with portamento:** The most common use is a slide between notes
   without re-triggering the instrument. Set T2 portamento, then use ** rows to prevent
   gate cycling while the pitch glides toward the new note.

---

## Leads to follow

- **Driver source assembly (the .prg files):** Disassembling `sf2driver11_05.prg` would give the
  exact 6502 instruction sequence: STA $D4XX addresses, the frame update order (which register
  is written first each frame), and the exact frequency table. This is needed for cycle-exact
  emulation. The .prg files are in `docs/src/` but need disassembly.
- **Exact frequency table:** Not yet captured. The SID chip uses:
  `freq_word = round(note_hz * 16777216 / cpu_clock)` where cpu_clock = 985248 Hz (PAL) or
  1022727 Hz (NTSC). The driver stores a 2-byte table per note.
- **Write ORDER within a frame:** Not yet determined. The driver likely writes freq first,
  then waveform (control), then ADSR. The exact sequence matters for gate-edge timing.
- **Driver 13 (Hubbard emulator):** Its dive effect, alternate arpeggio, and noise-on-attack
  behaviors are not fully mapped to SID registers here — need driver disassembly.
- **Multi-speed / multispeed:** Currently listed as a planned/missing feature in the FAQ.
  SF2 is single-speed (one update per VBI frame). No CIA-timer multispeed in current drivers.
- **Laxity's HVSC tunes:** These are the primary corpus. SIDID or similar fingerprinting should
  identify SF2 tunes by the characteristic `$0FFB` auxiliary data pointer / `0x1337` magic.
- **StrayBoom / Vincenzo tutorials:** YouTube tutorial series referenced in the Part 1 blog post.
  May contain additional effect explanation. Search: "SID Factory II tutorial Vincenzo StrayBoom".
