---
source_url: https://github.com/Chordian/sidfactory2 (driver notes + C++ source)
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity), Jens-Christian Huus (JCH), Michel de Bree
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver11.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/user_manual_20260314.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver12.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver13.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver14.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver15.txt (primary)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver16.txt (primary)
---

# SID Factory II — Per-Frame SID Register Effect Semantics

This document maps every driver 11 command and table effect to the SID register(s) it writes,
with exact per-frame update model. This is the primary reference for a register-accurate
re-emitter.

SID memory map:
  Voice 1: $D400=freq_lo, $D401=freq_hi, $D402=pw_lo, $D403=pw_hi, $D404=ctrl, $D405=AD, $D406=SR
  Voice 2: $D407=freq_lo, $D408=freq_hi, $D409=pw_lo, $D40A=pw_hi, $D40B=ctrl, $D40C=AD, $D40D=SR
  Voice 3: $D40E=freq_lo, $D40F=freq_hi, $D410=pw_lo, $D411=pw_hi, $D412=ctrl, $D413=AD, $D414=SR
  Global:  $D415=filter_lo(3-bit), $D416=filter_hi(8-bit), $D417=res_filt, $D418=mode_vol

Per-voice base offsets: voice 1 = +0, voice 2 = +7, voice 3 = +14.

---

## 1. Note Trigger (Gate On) — sequence note $01–$6F

**Registers written (in order — OPEN: exact write order needs disasm):**
- Voice+5 (AD): instrument byte 0
- Voice+6 (SR): instrument byte 1
- Voice+0/1 (freq lo/hi): note frequency from lookup table
- Voice+4 (ctrl): waveform from wave table row 0 with gate bit ($01) set

If oscillator reset flag ($10) is set in instrument byte 2, frame 0 of the new note writes:
- Voice+4 = $09 (test bit $08 + gate $01) first, then normal waveform on the same frame
  (or next — OPEN: exact timing of test-bit write vs waveform write needs disasm)

**OPEN:** The exact order of SID register writes within one frame is not documented in any
available text source. The driver likely writes freq first, then ctrl (waveform+gate), then
AD/SR. Confirm via `siddump --writelog` on any SF2 tune using driver 11.

---

## 2. Gate Off (`---`, sequence byte $00)

**Register written:**
- Voice+4 (ctrl): gate bit ($01) cleared; waveform bits preserved

Written on the frame where $00 appears in the sequence. ADSR enters release phase.

---

## 3. Gate On (`+++`, sequence byte $7E)

**Register written:**
- Voice+4 (ctrl): gate bit ($01) set; waveform bits preserved; no instrument reload

The wave table and pulse table continue from their current positions. ADSR is NOT
restarted — no new note trigger. Purely a gate-edge event.

---

## 4. Tie Note (`**`, duration range $90–$9F)

No SID register is written differently from a normal continuation. The gate bit is NOT
cycled. Instrument ADSR, wave table, and pulse table continue without interruption.
Used to suppress gate re-triggering during portamento or sustained notes.

---

## 5. Hard Restart (HR) — instrument byte 2 bit 7 ($80)

**Timing:** Fires exactly **2 frames before** the next note trigger.

**Frame N-2 (2 ticks before new note):**
- Voice+4 (ctrl): $09 written (test bit $08 + gate bit $01; freezes oscillator, seeds LFSR)
  — effectively gates off (the test bit trumps gate semantics for ADSR purposes)
- Voice+5 (AD): HR table byte 0 for selected HR index (typically $0F = attack 0, decay F)
- Voice+6 (SR): HR table byte 1 for selected HR index (typically $00 = sustain 0, release 0)

**Frame N-1:** HR state continues unchanged (ADSR hardware stabilizes).

**Frame N (new note):**
- Voice+4: new waveform (from wave table) + gate bit set
- Voice+5: instrument AD
- Voice+6: instrument SR
- Voice+0/1: note frequency

HR table index = bits 2-0 of instrument byte 2 (range 0–7 in driver 11.05; 0–15 in 11.00–11.04).

**Purpose:** Eliminates the "school band effect" — ADSR bug where rapid re-triggering with
certain ADSR values causes inconsistent envelope shapes.

---

## 6. Oscillator Reset — instrument byte 2 bit 4 ($10)

**Register written on first frame of a new note:**
- Voice+4: $09 (test bit $08 + gate $01) — holds oscillator in reset / seeds noise LFSR

OPEN: Is this written BEFORE or AS PART OF the note-on frame? The manual states "waveform
$09 is used in the first frame of a note." This implies the oscillator-reset waveform is the
first thing written, and the actual waveform appears in the wave table execution on the same
or subsequent frame. Needs disasm to confirm.

---

## 7. Wave Table — per-tick update

**Update rate:** One row consumed per driver tick (each frame). The wave program pointer
advances every tick.

**Per tick, for a normal row (byte 0 ≠ $7F):**
- Voice+4 (ctrl): byte 0 written directly as the SID control register
  (contains waveform bits + gate bit; gate bit normally $01)
- Voice+0/1 (freq lo/hi): computed from byte 1 (see below)

**Frequency from byte 1:**
- $00–$7F: relative offset. base_note = (sequence note) + (orderlist transpose) + byte_1.
  freq = note_table[base_note]. Written to Voice+0/1.
- $80–$DF: absolute. freq = note_table[byte_1 - $80]. Sequence note and orderlist
  transpose are IGNORED. Used for drums and fixed-pitch effects.

**Arpeggio interaction (byte 1 = $00 only):**
When an active T3 arpeggio command is running AND byte 1 = $00, the current arp table
semitone value is ADDED to base_note before the lookup. If byte 1 ≠ $00, arpeggio is
bypassed for that wave table row.

**Jump row (byte 0 = $7F):**
- Wave table execution pointer jumps to byte 1 (absolute row index)
- Jump to own index = self-loop (infinite sustain of current state)
- NOT a SID write; internal pointer update only

**End of wave program:** No explicit end marker; the wave table must always be terminated
by a $7F self-loop (otherwise execution falls into adjacent data).

---

## 8. Pulse Table — per-frame update

**Update rate:** Duration counter (byte 2 = YY frames) counts down per frame. When YY
exhausted, advance to next row.

**Set Pulse row ($8X XX YY):**
- Pulse width = 12-bit value: upper nibble from byte 0 ($X), lower 8 bits from byte 1 (XX)
  → pw12 = ($X << 8) | XX
- Written to Voice+2 (pw lo byte) and Voice+3 (pw hi byte, 4 bits used)
- Held for YY frames

**Add Pulse row ($0X XX YY):**
- Signed 12-bit delta: ($X << 8) | XX, sign-extended if applicable
- Added to current pulse width every frame (one addition per frame) for YY frames
- Written to Voice+2/3 each frame

**Jump row ($7F -- XX):**
- Jump to row XX in pulse table. Jump to own index = end program (no further writes)

**Pulse reset on note-on:**
Normally, on a new note trigger (with a different instrument OR a new note that resets
the instrument), the pulse table pointer is reset to the instrument's pulse table index.
Driver 11.05 flag $08 in instrument byte 2: if set, the pulse program is NOT reset on
note-on unless the instrument is EXPLICITLY set in the sequence row.

---

## 9. Filter Table — per-frame update

**Update rate:** Duration counter (byte 2 = YY frames) counts down per frame.

**Set Filter row ($XY YY RB, where X > $8, i.e. $9–$F):**
- $D415 (filter cutoff lo, 3 bits): lower 3 bits of the 11-bit cutoff value
- $D416 (filter cutoff hi, 8 bits): upper 8 bits of the 11-bit cutoff value
- $D417 (resonance + routing): hi nibble = R (resonance 0–$F), lo nibble = B (voice bitmask)
  B bit 0 = voice 1 filtered, bit 1 = voice 2 filtered, bit 2 = voice 3 filtered
- $D418 (mode + main vol): bits 7-5 = filter mode (from X nibble), bits 3-0 = main volume
  (preserved from current $D418 unless overridden)

**Filter mode encoding (X nibble of first byte, for set-filter rows):**
```
$9x = High-pass + Band-pass   → $D418 bits: hp=1, bp=1, lp=0
$Ax = High-pass only          → $D418 bits: hp=1, bp=0, lp=0
$Bx = Band-pass only          → $D418 bits: hp=0, bp=1, lp=0
$Cx = High-pass + Low-pass    → $D418 bits: hp=1, bp=0, lp=1  (notch)
$Dx = Band-pass + Low-pass    → $D418 bits: hp=0, bp=1, lp=1
$Ex = Low-pass only           → $D418 bits: hp=0, bp=0, lp=1
$Fx = HP + BP + LP (all)      → $D418 bits: hp=1, bp=1, lp=1
```
($D418 bits: bit 7=HP, bit 6=BP, bit 5=LP)

**Add-to-cutoff row ($0X XX YY):**
- Signed 12-bit delta ($X << 8 | XX) added to current cutoff value each frame
- $D415/$D416 updated each frame for YY frames
- $D417 and $D418 NOT re-written on add-to-cutoff rows (preserved)

**Jump row ($7F -- XX):** Jump to filter table row XX (self = end program).

**Per-instrument filter enable [driver 11.03+]:**
When instrument byte 2 bit 5 ($20) is set, the voice's bit is combined (OR'd) into
the bitmask B in $D417, enabling filtering on that voice. This is applied in addition
to whatever B is set in the filter program row.

**Filter program activation:**
- Via instrument: bit 6 ($40) of instrument byte 2 = start filter program from byte 3 index
- Via command Ta: sets filter program pointer to the given index immediately

---

## 10. Arpeggio Table — per-tick update (driven by T3 command)

**Activation:** Command T3 XX YY sets arpeggio speed = XX, starting index = YY.

**Per tick (speed counter = XX):** After XX ticks at the current arp step, advance to next.

**Step value ($00–$6F):** Semitone offset added to the base note for freq computation.
Result fed into note_table[] → Voice+0/1. Only applied when wave table byte 1 = $00.

**Jump value ($70–$7F):** Jump to (starting_index + low_nibble). Example: $71 at step 4
with starting_index=0 → jumps to step 1. This allows different loop points based on
which starting index was specified in the T3 command.

**No SID writes besides freq:** The arp only modifies the frequency register computation;
it does not touch Voice+4 (ctrl) or ADSR.

---

## 11. Slide Up/Down (T0 XX YY — 16-bit speed)

**Per-frame SID write:**
- Voice+0 (freq lo) and Voice+1 (freq hi): raw 16-bit frequency register ± XXYY each frame

XXYY is a 16-bit delta (XX=high byte, YY=low byte) added to (or subtracted from) the
current frequency register value each driver tick. The sign of the slide is determined by
whether XXYY is positive (up) or negative (two's complement, down).

**Duration:** Continues indefinitely until a new note triggers or command changes. No auto-stop.

---

## 12. Vibrato (T1 XX YY)

**Per-frame SID write:**
- Voice+0/1 (freq lo/hi): base frequency ± amplitude delta (oscillating)

**Parameters:**
- XX = frequency (period): larger = slower oscillation
- YY = amplitude: depth of frequency deviation. NOTE: SMALLER YY = STRONGER vibrato
  (counter-intuitive; this matches the driver documentation explicitly)

**Update model:** LFO advances XX steps per frame through an internal sine/triangle table.
The result, scaled by YY, is added to or subtracted from the base note frequency.
OPEN: exact LFO shape (sine vs triangle) and table size need disasm to confirm.

---

## 13. Portamento / Glide (T2 XX YY — 16-bit speed)

**Per-frame SID write:**
- Voice+0/1 (freq lo/hi): nudges current freq toward target freq by XXYY per frame

When a new note triggers with T2 active, instead of jumping to the new frequency
immediately, the frequency register slides by ±XXYY per frame until it reaches the target.

**Stop portamento:** Use `T2 02 80 00` (as per the manual). The `80 00` overflows quickly,
effectively snapping to the target. A speed of $0000 would stop all motion.

**Typical use:** Combine with tie-note (`**`) rows to prevent gate re-triggering while sliding.

---

## 14. ADSR Override — T8 (local) and T9 (instrument)

**SID registers written:**
- Voice+5 (AD): from XX byte of command
- Voice+6 (SR): from YY byte of command

**T8 — local:** Applies to the current note only. Reverts on next note trigger.
**T9 — instrument:** Persists until a different instrument is explicitly selected.

Both T8 and T9 override the instrument's byte 0/1 AD/SR for the current voice.

---

## 15. Filter Program Index — Ta (command)

**No SID write on the command row itself.**
Sets the filter program pointer to the given index. The filter table then runs per-frame
from that index. Equivalent to starting a filter program from a command rather than from
the instrument.

---

## 16. Wave Program Index — Tb (command)

**No SID write on the command row itself.**
Redirects the wave table execution pointer for the current voice to the given index.
Equivalent to mid-sequence wave program change without instrument change.

---

## 17. Pulse Program Index — Tc [driver 11.02+]

**No SID write on the command row itself.**
Sets the pulse program pointer for the current voice to the given index. Useful for
triggering a different pulse sweep without changing the instrument.

---

## 18. Tempo Program Index — Td [driver 11.02+]

**No SID write directly.**
Updates the tempo counter pointer to row XX of the tempo table. Immediate tempo change
(takes effect on the next sequence row). Affects all three voices simultaneously (tempo
is global).

---

## 19. Main Volume — Te [driver 11.02+]

**SID register written:**
- $D418 bits 3-0: main volume = X (0–$F)
- $D418 bits 7-4 (filter mode): preserved (not modified)

Written once on the frame where the command is active.

---

## 20. Note Delay — T-nibble [driver 11.04+]

**No SID write on the delay ticks themselves.**
The high nibble of the note byte in the sequence stream (when driver 11.04 is used)
specifies 0–15 ticks of delay. During those ticks, the previous voice state continues
unchanged. On tick T+1, the normal note-on occurs.

---

## 21. Fret Slide — T4 [driver 11.01–11.04 only, removed in 11.05]

**Per-frame SID write:**
- Voice+0/1 (freq lo/hi): slides by ±speed until YY semitones have been traversed

XX = $00–$7F: slide up. XX = $80–$FF: slide down.
YY = semitone distance to travel (auto-stops after YY semitones).
Different from T0 (runs forever) and T2 (slides to a specific target note).

---

## 22. Demo Sync — Tf

**No SID register written.** Internal counter incremented by XX. Used for timing external
demo effects/visual sync. Not relevant to audio reconstruction.

---

## 23. Init Table — multi-song setup

Each row = 2 bytes:
- Byte 0: tempo table index to start playback at
- Byte 1: main volume ($D418 bits 3-0); written to $D418 on song init (typically $0F)

One row per song in multi-song files. Selects which tempo program and initial master volume
the song starts with.

---

## Note Frequency Table

**Formula:** `freq_word = round(note_hz * 16777216 / cpu_clock)`
- PAL clock: 985248 Hz
- NTSC clock: 1022727 Hz
- 16777216 = $1000000 = 2^24 (SID frequency resolution)

**Note range in sequences:** $01–$6F = 111 note values across 8 octaves (0–7).
Octave numbering: C-0 = lowest, B-7 = highest. 12 notes per octave × ~9 octaves
(the exact start note and note-number-to-octave mapping is documented in the editor keyboard
layout but needs to be confirmed vs. the frequency table in the .prg binary).

**Known standard PAL SID frequency table (from matozoid/c64_freqtable.csv, cross-checked
with codebase64.org formula):**
Octave 0: C=268, C#=284, D=301, D#=318, E=337, F=358, F#=379, G=401, G#=425, A=451, A#=477, B=506
Each octave approximately doubles. Octave 7 C ≈ 34334.

**OPEN (needs disasm):** The exact 256-entry freq table embedded in `sf2driver11_05.prg`
must be extracted to confirm start note, number of octaves, and any fine-tuning offsets.
The wave table's absolute semitone encoding ($80–$DF = values 0–95, 8 octaves of 12) maps
to specific entries in this table; the exact offset ($80 = which absolute freq entry) needs
the binary. Run: `xxd sf2driver11_05.prg | grep -A2 <driver_code_top>` then locate the
two-byte-per-entry freq table.

---

## Leads to follow

- **OPEN: exact SID register write ORDER within a frame** — which register is written first
  each frame (freq lo, freq hi, ctrl, AD, SR, PW lo, PW hi). Critical for gate-edge timing
  and ADSR initialization. Requires disassembling `sf2driver11_05.prg` or capturing with
  `siddump --writelog` and reading the within-frame sequence.
- **OPEN: exact frequency table** — extract from prg binary at driver_code_top + N.
  The descriptor block chain gives driver_code_top; disasm from there to find the freq table.
- **OPEN: LFO shape for vibrato (T1)** — sine, triangle, or other? Table size?
- **OPEN: oscillator reset timing** — is $09 written in the SAME frame as the note-on, or is
  it pre-written one frame earlier (like HR)?
- **OPEN: filter mode encoding → exact $D418 bits** — particularly the $9x = HP+BP mapping.
  The SID $D418 bits 7-5 for HP/BP/LP are HP=bit7, BP=bit6, LP=bit5. Verify the X-nibble
  to $D418 bit mapping in the binary to be sure $9x → %11000000, $Ex → %00100000, etc.
- **OPEN: `$00` (keep waveform) in wave table byte 0** — is $00 explicitly handled as
  "don't write ctrl register" or is it written as-is (which would produce triangle-off/gate-on
  = $01 with waveform bits cleared)? Needs disasm.
