# SoedeSoft / Soundmaster — Per-Frame $D400–$D418 Write Model

**Provenance:**
- Soundmaster V3.1 German manual (CSDb #90307, Walter Konrad, 1989) — primary source
- sidid.cfg byte signatures for V1.0 / V3.1 / V3.2 — secondary source
- PSID header statistics from hvsc84.db (929 SIDs) — tertiary source
- Known player structure from background task notes

Each claim is tagged: DOCUMENTED (directly from manual), INFERRED (deduced from
signatures or structural analysis), or OPEN (unknown; disassembly required).

---

## 1. Verification mode

SoedeSoft is a tracker-music engine with VBlank / 50 Hz IRQ firing. There is no
evidence of CIA timer use (manual gives no CIA programming instructions; no
digi-sample output). The write-log verification mode is therefore:

**Mode 1 — frame-by-frame instruction sequence** (same as Hubbard '85, FC standard).

The per-`play()` $D400–$D418 write sequence must match frame by frame. Within a frame
the order of writes matters; cycle timestamps within a frame do not.

OPEN: Confirm PSID `speed` bit is 0 (VBlank) for the canonical Cluster A SIDs before
committing to Mode 1. If any subtune has `speed != 0`, apply the `--writelog-per-irq`
capture path (CIA-tune branch in verify_all).

---

## 2. Voice stride

**DOCUMENTED (background task):** The player uses `STA $D4xx,X` with X = 0, 7, 14.

Voice-to-X mapping:
| Voice | X value | Voice register base |
|-------|---------|-------------------|
| 1     | $00     | $D400             |
| 2     | $07     | $D407             |
| 3     | $0E     | $D40E             |

This is standard C64 SID voice-stride addressing. All per-voice register writes
are X-indexed from the voice base.

INFERRED (from sidid V3.1/V3.2 signatures): The V3.1 player uses `STA $D400,Y` /
`STA $D401,Y` (Y-indexed), while V3.2 uses `STA $D400,X` / `STA $D401,X` (X-indexed).
Both use the same logical stride; the choice of index register differs between versions.

---

## 3. Per-voice write sequence per play() frame

The following is a PARTIAL model based on the manual's sound-parameter documentation.
Items are grouped by trigger: "note-on" (new note in the bar) vs. "sustain" (no new note)
vs. "release" (`--` row) vs. "always" (every frame).

### 3a. Note-on writes (new sound triggered on this bar row)

**DOCUMENTED:**

1. `STA $D404+X, waveform_byte1` — write voice control register (gate=1 set, waveform,
   sync, ring flags from Sound Part 1, byte 1). Manual: "Die 1. Zahl gibt die Waveform
   an ($D404). Dieses Register wird bei jedem Sound neu geschrieben."

2. `STA $D405+X, attack_decay` — write ADSR attack/decay (Sound Part 2).
   Manual: "Register $D405 des SID. Wird vom Waveformregister initialisiert."

3. `STA $D406+X, sustain_release` — write ADSR sustain/release (Sound Part 2).

4. Pulse-width init — write to $D402+X (PW lo) and $D403+X (PW hi) from the
   "Pulse start" field (DOCUMENTED: low nibble → PW lo high-nibble, high nibble → PW hi).
   OPEN: exact combined byte layout (the manual's "1 nibble = halbes bit" note is
   confusing; precise register values need disassembly confirmation).

5. Frequency write — OPEN: whether frequency is written from a lookup table indexed
   by note+octave+transpose on note-on, or only updated on subsequent frames.
   INFERRED from V3.1 sidid signature (`7D ?? ?? 99 00 D4 … 69 ?? 99 01 D4`): an
   arp/transpose delta is ADDED to the current frequency value via ADC, then the
   result is written to $D400+Y (freq lo) and $D401+Y (freq hi). So the frequency
   write occurs EVERY frame (not only on note-on), driven by the arp table.

6. Portamento init — OPEN: when the portamento flag ($80) is set in the bar row,
   the portamento accumulator is loaded with the portamento count (Sound Part 2
   "Portamento count high" / "Portamento count low" fields). Portamento mode then
   slides the frequency over subsequent frames.

### 3b. Sustain / held note writes (same note continues)

**DOCUMENTED:** The secondary waveform byte (Sound Part 1, byte 2) is written to
$D404+X at the start of a `++` "cycle trigger" event. This is INFERRED to re-trigger
the arp/wave cycle without re-loading the envelope.

For ordinary sustain (no `++`), the arp/wave table continues stepping, producing
ongoing writes to $D400+X (freq lo), $D401+X (freq hi), and $D404+X (waveform,
from wave table) every frame.

### 3c. Release writes (`--` row)

**DOCUMENTED:** "Release startet bei '--' in den bars" — when a `--` appears in the
bar, the sustain/release ADSR value's release phase is started. This means:
- Gate is cleared: write `waveform_byte & ~$01` to $D404+X (gate off).
- OPEN: whether the waveform byte written is byte 2 of Sound Part 1 (the "secondary
  waveform" used on `--` rows) or simply the current waveform with gate cleared.

### 3d. Always-writes (every play() invocation)

**DOCUMENTED:**

- Filter cutoff lo: `STA $D416, filter_start + (frame_count * filter_count)`
  or decremented by 2 if filter_count=$FE. The "Filter count time" controls
  how long this sweep runs (stop if time expires AND time < $80).

- INFERRED: $D417 (resonance + filter voice enable) and $D418 (volume + filter mode)
  are written from the global song parameters, likely only on song init or on block
  transitions, NOT every frame. OPEN: whether $D418 is written every frame or only
  on song events.

---

## 4. Global register writes

### $D418 — Filter mode / volume
**DOCUMENTED:** Set from the "Filter mode/volume" Spezial-Funktion parameter.
This is the $D418 SID register verbatim.
OPEN: write frequency (init-only? every-frame? on-block-change?).

### $D417 — Resonance / filter voice
**DOCUMENTED:** Set from the "Resonance/filtervoice" parameter. Low nibble selects
which voices are filtered: bit 0=voice1, bit 1=voice2, bit 2=voice3.
OPEN: write frequency.

### $D416 — Filter cutoff hi
**DOCUMENTED:** Set from "Filter start" in Sound Part 2. This is the initial cutoff-hi value.
"Filter count" modifies $D416 per frame: adds filter_count, or subtracts 2 if $FE.
The "Filter count time" limits how long the sweep runs (value > $80 = infinite).
INFERRED: $D416 is written every play() invocation for voices that have filter_count
active. OPEN: whether filter_count is global or per-sound.

### $D415 — Filter cutoff lo
OPEN: The manual references $D416 as the filter register modified by filter_count
and filter_start. Whether $D415 (cutoff lo) is also programmed is not mentioned.
INFERRED: likely written at note-on from a sound parameter.

---

## 5. Arp + wave table effect on writes

**DOCUMENTED:** Each sound step through an arp/wave table produces:
- An arp offset value added to the current note index (or subtracted if "revers" flag)
  → produces a modified frequency → writes to $D400+X, $D401+X.
- A wave value from the wave table → writes to $D404+X (voice control).
- The $08 bit in the wave byte ($D404 bit 3) enables vibrato or portamento to be
  applied within the arp step (i.e., arp and vibrato/portamento coexist when this bit set).
- $7F in the arp table = "constant effect value" — substitutes the actual note pitch
  rather than an offset. Used for a "tick" at sound start (the manual example shows
  waveform must be $81 = pulse + gate for this to click).

**INFERRED write sequence within arp step (per frame):**
```
STA $D404+X, wave_table[arp_idx]       ; waveform
STA $D400+X, freq_table[note + arp_delta] & $FF  ; freq lo
STA $D401+X, freq_table[note + arp_delta] >> 8   ; freq hi
```
The V3.1 sidid signature confirms this: `99 00 D4` / `99 01 D4` (Y-indexed freq writes)
immediately follow ADC-from-table operations.

---

## 6. Portamento write model

**DOCUMENTED:** Portamento is a per-note flag (bar row bit $80). The sound defines
"Portamento count high" (bits 0–2 of packed byte) and "Portamento count low" (separate).
The portamento count is a 16-bit rate accumulated per frame until the target frequency
is reached.

**INFERRED write model:** On each frame while portamento is active:
```
current_freq += portamento_rate   ; (or -=, depending on direction)
STA $D400+X, current_freq & $FF
STA $D401+X, current_freq >> 8
```
The "Delay/Portamento count high" packed byte also contains a vibrato delay field
(bits 3–7), so vibrato does not begin until this many frames have elapsed after
note-on.

OPEN: Direction of portamento slide (toward target note or away). Exact
accumulation algorithm.

---

## 7. Vibrato write model

**DOCUMENTED:**
- Vibrato amplitude: either fixed (< $80 = direct amplitude) or growing (≥ $80 → encodes
  addition rate; amplitude increases while sound plays, starting from "Levelinc. start").
- Global vibrato speed/rate: "Vibrato level" Spezial parameter (default=4).
- Vibrato delay: packed into "Delay/Portamento count high" bits 3–7.

**INFERRED write model:** Vibrato modulates the current frequency on every frame:
```
if vibrato_delay_counter == 0:
    vibrato_phase += vibrato_speed
    freq_delta = vibrato_lut[vibrato_phase] * vibrato_amplitude
    STA $D400+X, (base_freq + freq_delta) & $FF
    STA $D401+X, (base_freq + freq_delta) >> 8
```
OPEN: whether SoedeSoft uses a sine LUT for vibrato or a simple triangle wave.
OPEN: exact phase and amplitude encoding.

---

## 8. Pulse-width sweep write model

**DOCUMENTED:**
- "Pulse count level": delta added to PW lo register per frame when active.
- "Pulshigh max/min": clamp bounds for PW hi byte.
- Direction flip: implied by the max/min bounds (when PW hi hits max, reverse; when min, reverse).

**INFERRED write model:** On each frame while pulse count is active:
```
pw_lo += pulse_count_level        ; may wrap
if pw_hi >= pulshigh_max: direction = -1
if pw_hi <= pulshigh_min: direction = +1
pw_hi += direction
STA $D402+X, pw_lo
STA $D403+X, pw_hi
```
This is a bounded up/down sweep — analogous to Hubbard's PWM but with explicit max/min.
OPEN: exact wrap/carry behaviour for pw_lo overflow into pw_hi.

---

## 9. Init write sequence

**DOCUMENTED:** Init clears variables $0333–$039D (`LDA #0 / LDY #$69 / STA $0333,Y / DEY / BNE`).

**INFERRED init writes:**
- Clear all SID registers $D400–$D418 (standard C64 practice; OPEN — the player may
  or may not do an explicit SID reset).
- Load global parameters: write $D417, $D418 from song Spezial-Funktion values.
- Per-voice: set initial waveform (gate=0), set ADSR for voice 1/2/3.
- Position song pointer to block 0, step 0, bar 0, row 0 for each voice.

OPEN: Whether init takes a subtune number (A register convention) and how it
selects the correct block/step sequence for that subtune.

---

## 10. Register coverage summary

| Register | Voice | Source | Status |
|----------|-------|--------|--------|
| $D400+X  | 1/2/3 freq lo | freq table + arp delta | INFERRED |
| $D401+X  | 1/2/3 freq hi | freq table + arp delta | INFERRED |
| $D402+X  | 1/2/3 PW lo | pulse start + pulse count | DOCUMENTED |
| $D403+X  | 1/2/3 PW hi | pulse start (hi nibble) + clamp | DOCUMENTED |
| $D404+X  | 1/2/3 ctrl | waveform byte from sound + wave table | DOCUMENTED |
| $D405+X  | 1/2/3 AD | Sound Part 2 attack/decay | DOCUMENTED |
| $D406+X  | 1/2/3 SR | Sound Part 2 sustain/release | DOCUMENTED |
| $D415    | global | filter cutoff lo | OPEN |
| $D416    | global | filter start + filter count sweep | DOCUMENTED |
| $D417    | global | resonance/filtervoice | DOCUMENTED |
| $D418    | global | filter mode/volume (master vol) | DOCUMENTED |

Registers NOT covered by this engine: $D407–$D40D (voice 2 low regs), $D40E–$D414
(voice 3 low regs) — these are reached via the same +X stride, so they ARE written;
they are listed with the voice-1 registers above by stride.

---

## 11. Expected write ordering within a frame (INFERRED)

Based on typical C64 tracker practice and the manual's description of sequencing,
the most likely per-voice write order within a single play() call is:

```
; For each voice (v=1,2,3), X = 0/7/14:
  [if note-on:]
    STA $D404+X, waveform_1    ; set wave (gate=1, new waveform)
    STA $D405+X, attack_decay  ; ADSR init
    STA $D406+X, sus_release
    STA $D402+X, pw_lo         ; pulse start
    STA $D403+X, pw_hi

  [arp/wave step:]
    STA $D404+X, wave_byte     ; from wave table (may be same as above on first frame)
    STA $D400+X, freq_lo       ; note freq + arp delta
    STA $D401+X, freq_hi

  [vibrato/portamento modulation:]
    STA $D400+X, freq_lo       ; modified freq
    STA $D401+X, freq_hi

  [pulse sweep:]
    STA $D402+X, pw_lo_new
    STA $D403+X, pw_hi_new

  [if release row:]
    STA $D404+X, waveform_2    ; secondary waveform (gate=0 for release)

; Global (once per frame):
  STA $D416, filter_val        ; if filter sweep active
```

OPEN: The actual ordering (particularly whether freq or waveform is written first)
must be confirmed by `find_first_divergence.py` on a canary pair before
committing to this ordering in the composer.

---

## Leads to follow

1. **Confirm $D415 (filter cutoff lo) is or is not written.** The manual describes
   $D416 explicitly ("Filter start: Register $D416 des SID") but never mentions $D415.
   This is unusual — most players that modulate the filter write both $D415 and $D416.
   Run `tools/voice_writelog.py` on a filter-modulating canary and check for $D415 writes.

2. **V3.1 sidid signature fragment analysis.** The sequence
   `99 ?? ?? 99 00 D4 … 69 ?? 99 ?? ?? 99 01 D4` (Y-indexed ADC-then-STA to freq
   lo/hi) appears in V3.1. The `69 ??` = `ADC #imm` before storing freq hi suggests
   the freq-hi byte carries an extra signed offset (possibly an octave transpose baked
   in). This should be verified against the actual freq table format.

3. **V1.0 nibble-split pattern.** The `4A 4A 4A 4A` (four LSRs) / `0A 0A 0A 0A` (four
   ASLs) pattern in V1.0 is a textbook 4-bit field split. The most likely candidates are:
   (a) ADSR packing (attack+decay in one byte, split to $D405), or (b) pulse-width
   hi/lo packing. Given that V3.1 explicitly documents "Pulse start: low nibble = PW
   lo high nibble, high nibble = PW hi", this V1.0 pattern is likely the same PWM
   initialisation, just implemented differently. Verify by disassembling a V1.0 canary.

4. **Write ordering of waveform vs. freq.** Gate edge timing is critical for correct
   ADSR behaviour. If the waveform write (gate=0 first, then gate=1 on the same note)
   appears to be a two-step operation, that must be captured in the write model.
   Check with `find_first_divergence.py` using the REVERS note mechanism (a `!`-flagged
   note suggests some gate-off/gate-on sequencing).
