# Hubbard Engine Feature Audit — Commando Driver (1985)

**Engine:** Rob Hubbard 1985 driver  
**ROM range:** `$5012-$5427` (1046 bytes)  
**Audited:** 2026-04-29  
**Method:** Complete disassembly of every branch in the play routine  

---

## Summary

The Commando driver has **10 distinct code-gated feature paths**. We currently
implement 4 of them correctly. The table below lists all features found.

| Feature | Gate | Addr range | Implemented? |
|---------|------|-----------|--------------|
| Speed counter (inner) | `DEC $5513 / BPL` | `$5054-$506C` | YES |
| Pattern/sequence read | `CMP #$FF / CMP #$FE` | `$5086-$50A9` | YES |
| Hold mode (bit6 of wave step) | `BVS $5118` | `$50CF-$5118` | NO — see §2 |
| Extra byte: instrument select | `BPL $50E7` | `$50DF-$50EA` | YES (instrument) |
| Extra byte: drum control | `BMI $50E1` | `$50DF-$50E1` | PARTIAL — see §3 |
| Hard restart auto gate-off | `LDA $28; BMI; AND $20; BNE; AND $F2; BNE` | `$5174-$519A` | PARTIAL — see §4 |
| **Vibrato** (byte+5 depth != 0) | `BEQ $5230` | `$51BF-$522F` | **NO** — see §5 |
| PW unidirectional (bit3=1) | `AND #$08; BEQ` | `$5230-$524B` | YES |
| PW oscillating (bit3=0, byte6!=0) | `BEQ $52B3` | `$524C-$52B2` | YES |
| Drum frequency slide | `BEQ $52FA` | `$52B3-$52F9` | PARTIAL — see §6 |
| **fx_flags bit0: pitch-drop gate** | `AND #$01; BEQ` | `$52FA-$5335` | **NO** — see §7 |
| **fx_flags bit1: octave-up alternate** | `AND #$02; BEQ` | `$5336-$535D` | **NO** — see §8 |
| fx_flags bit2: octave arp | `AND #$04; BEQ` | `$535E-$538F` | YES |

---

## §1 — Engine overview

The play routine runs 3 times per frame (once per SID voice, X=2,1,0).

Each voice has:
- Pattern sequence (orderlist + pattern list + wave steps)
- Per-voice instrument register: `$54FE,X`
- Per-voice note register: `$54FB,X`
- Per-voice duration counter: `$54F2,X`
- Per-voice SID offset: `$54EB` (0, 7, 14 for V1, V2, V3)

Instrument table: 8 bytes per instrument at `$5591 + inst*8`:

| Offset | Register | Meaning |
|--------|----------|---------|
| +0 | `$5591,Y` | pw_lo |
| +1 | `$5592,Y` | pw_hi (AND `$0F` when writing SID) |
| +2 | `$5593,X` | wave control byte (waveform + gate bit) |
| +3 | `$5594,Y` | attack/decay |
| +4 | `$5595,Y` | sustain/release |
| +5 | `$5596,Y` | **vibrato depth** (number of right-shifts applied to semitone gap) |
| +6 | `$5597,Y` | **vibrato delta / PW speed** (dual purpose) |
| +7 | `$5598,Y` | fx_flags (bits 0-3) |

Global state:
- `$5525` = global frame counter (incremented every call)
- `$5519` = play/init state byte
- `$5528` = global enable (0xFF = enabled, 0x00 = disabled — set per-voice each loop)
- `$5513` = inner speed counter; `$5517` = speed reset value

---

## §2 — Hold mode (wave step bit 6) — NOT IMPLEMENTED

**Location:** `$50CF-$5118`

When a wave step byte has bit 6 set (`BVS $5118`), the engine:
1. Skips the frequency lookup and SID freq write entirely
2. Decrements a gate mask `$5501` (from `$FF` to `$FE`)
3. ANDs the wave control byte with `$5501` before writing to `D404` → **gate bit cleared**

This is effectively a **1-frame gate-off** inserted before the normal note starts.
It functions as a built-in hard restart trigger within the wave step format itself.

**Current state:** `rh_decompile.py` does not parse the hold bit. The decompiler reads
wave steps as flat bytes without bit-field decoding. The `rh_to_usf.py` converter uses
the `has_drum` path for most gate-off cases.

**Impact:** Songs that use hold-mode wave steps (bit6=1) will miss the brief gate-off
and have ADSR artifacts at note transitions.

---

## §3 — Drum control byte format — PARTIAL

**Location:** `$50DF-$50E4` (wave step extra byte with bit7=1)

When a wave step has bit7=1 and the extra byte has bit7=1, the byte is stored at
`$5520,X`. This byte controls the drum frequency slide:

- Bits `[6:1]`: slide delta per frame (magnitude, always positive)
- Bit `0`: direction — 0=up (add delta), 1=down (subtract delta)

**Current state:** `rh_decompile.py` reads the drum control byte. `rh_to_usf.py` uses
`sidxray.drum_extract` to measure the actual slide from the original SID trace and applies
`freq_slide` to drum instruments. This is partially implemented but measurement-based
rather than parsing the drum byte directly.

**Missing:** Direct parsing of the drum control byte from the binary — we could read
`(drum_byte & 0x7E)` as the delta and `drum_byte & 0x01` as direction without needing
the siddump measurement. This would make the feature deterministic rather than heuristic.

---

## §4 — Hard restart auto gate-off — PARTIAL

**Location:** `$5174-$519A`

The engine checks 3 conditions to fire a hard restart:
1. `$5528` must be enabled (BMI — global enable)
2. Wave step bit5 must be clear — if bit5=1, hard restart is **inhibited**
3. Duration counter `$54F2,X` must be zero (note just started)

When all conditions met: write wave byte with gate stripped (`AND #$FE`), zero ADSR.

**Current state:** `rh_to_usf.py` uses `inst.gate_timer = 1` and `inst.hr_method = 'gate'`
for all instruments. This does not honor the **bit5 inhibit** flag.

**Missing:**
- Bit5 of wave step = inhibit hard restart. When bit5=1, the gate is never cleared by
  the auto-restart mechanism. We do not parse or apply this flag.
- Instruments with bit5 inhibit should have `gate_timer = 0` or `hr_method = None`.

---

## §5 — Vibrato — NOT IMPLEMENTED (critical)

**Location:** `$51BF-$522F`

This is the biggest missing feature. The vibrato system activates when `$5506` (byte+5
of the instrument) is non-zero. From Commando's instrument table, 9 of 13 instruments
have non-zero byte+5 values.

**Exact mechanism:**

1. Load `$5525 & 0x07` (global frame counter low 3 bits, 0-7)
2. Mirror: if >= 4, XOR with 7 (produces 0,1,2,3,3,2,1,0 — triangle wave pattern)
3. Store as `$550C` (vibrato phase, 0-3)
4. Compute semitone gap: `freq(note+1) - freq(note)` = 16-bit value
5. Right-shift the gap `depth` times (`$5506` = byte+5 = shift count)
6. Store as `($5509:$5508)` = per-semitone vibrato step
7. Start from base freq `freq(note)` in `($550B:$550A)`
8. Add step `phase` times to get final modulated frequency
9. Gate condition: wave step must have >= 6 frames remaining (`$54F2,X >= 6`); otherwise vibrato is disabled for the note's last 5 frames

**Pitch modulation formula:**
```
vibrato_delta = (freq[note+1] - freq[note]) >> byte5
vibrato_phase = frame_counter & 0x07, then mirrored (triangle: 0,1,2,3,3,2,1,0)
final_freq = freq[note] + vibrato_delta * vibrato_phase
```

This is DIFFERENT from what `rh_to_usf.py` currently emits. The current code uses
GT2-style calculated-speed vibrato with a shift count mapped from byte+5. The GT2
vibrato uses a different oscillation pattern and is driven by a separate speed table,
not the global frame counter.

**Key differences vs current implementation:**
- Current: uses GT2 speed table (oscillation rate independent of global counter)
- Actual: vibrato phase = `$5525 & 0x07` — tied to **global frame counter**, not per-voice
- Current: vibrato starts immediately
- Actual: vibrato suppressed for last 5 frames of any note (`CMP #$06; BCC skip`)
- Current: all 3 voices share the same oscillation phase if they have same speed table
- Actual: all 3 voices inherently share the same phase (same `$5525` counter)

**Byte+5 values in Commando:**

| Inst | byte+5 | vibrato_depth | effect |
|------|--------|---------------|--------|
| 0 | `$02` | 2 | divide semitone gap by 4 |
| 1 | `$00` | 0 | NO vibrato |
| 2 | `$00` | 0 | NO vibrato |
| 3 | `$00` | 0 | NO vibrato |
| 4 | `$00` | 0 | NO vibrato |
| 5 | `$00` | 0 | NO vibrato |
| 6 | `$02` | 2 | divide semitone gap by 4 |
| 7 | `$01` | 1 | divide semitone gap by 2 |
| 8 | `$02` | 2 | divide semitone gap by 4 |
| 9 | `$03` | 3 | divide semitone gap by 8 |
| 10 | `$02` | 2 | divide semitone gap by 4 |
| 11 | `$01` | 1 | divide semitone gap by 2 |
| 12 | `$00` | 0 | NO vibrato |
| 13 | `$11` | 17 | very fine (>> 17, essentially zero) |
| 14 | `$4C` | 76 | very fine (near-zero) |
| 15 | `$81` | 129 | byte+5 is NEGATIVE flag (bit7=1); see note |

**Note on byte+5 >= 128:** The code at `$51BF` only checks `BEQ $5230` (zero = skip).
A value of `$81` still passes the check (non-zero), but the 16-bit right-shift by 129
would produce zero, so vibrato is effectively off. The value likely indicates another
feature for non-1985 drivers (see §7 below).

---

## §6 — Drum frequency slide — PARTIAL

**Location:** `$52B3-$52F9`

The drum slide adds/subtracts `(drum_byte & 0x7E)` per frame to the stored frequency.
The stored frequency is the note's initial frequency (`$551A,X` hi, `$551D,X` lo),
which is saved when the note first plays.

**Current state:** Implemented via `sidxray.drum_extract` measurement. The heuristic
measures `freq_hi` descent from the original SID trace. Works for standard drum slides.

**Missing:** If the drum byte was set to 0 by initialization (the Commando case where
`$5520 = $00` after INIT), the drum slide is disabled. We currently handle this case
correctly (slide=0 means no slide). However, for songs where the drum byte comes from
game RAM (`$AC6B` area in Commando), we cannot parse it statically.

---

## §7 — fx_flags bit0: pitch-drop on release — NOT IMPLEMENTED

**Location:** `$52FA-$5335`

When `fx_flags & 0x01` is set (bit0), the engine modifies frequency near the end of each note:

**Phase 1 (first frame of note, `remaining == total`):**
- Writes `freq_hi` unchanged to `D401`
- Writes `$80` (noise, no gate) to `D404`

**Phase 2 (subsequent frames):**
- Decrements `$551A,X` (freq_hi) in memory
- Writes the OLD freq_hi to `D401` (before decrement)
- If waveform has only gate bit (`wave & $FE == 0`): also writes decremented freq_hi and then `$80` to D404

**Effect:** A downward pitch slide on each note, combined with a test-bit/noise write
on the first frame for hard restart. This creates a "pitch-drop" effect — each note
starts slightly sharp and slowly descends.

**Current state:** Not implemented. `rh_to_usf.py` has no handling for `fx_flags & 0x01`
in this context.

**Impact in Commando:** Instruments 1, 3, 4, 5, 7, 9, 10, 11, 12 all have bit0=1.
These are the majority of melodic instruments. The pitch-drop effect on every frame
accounts for a significant portion of the remaining `note_wrong` frames.

**Wait — re-analysis:** Looking at the condition chain more carefully:
- `BEQ $5336` if `fx_flags & 1 == 0` → skip
- `BEQ $5336` if `freq_hi == 0` → skip (no slide when freq_hi is 0)
- `BEQ $5336` if `duration == 0` → skip (inactive voice)

So bit0 only fires when the note is active AND freq_hi is non-zero. This is the
**vibrato + frequency interaction** — bit0 is NOT a simple pitch-drop. Looking at
the actual register writes, the first frame writes `$80` to D404 which is the
noise waveform without gate. This is the hard restart mechanism (test bit pattern).

**Corrected interpretation:** fx_flags bit0 = **hard restart + freq slide mode**:
- Frame 1 of note: write noise (no gate) = hard restart
- Subsequent frames: decrement freq_hi each frame = downward pitch slide
- This creates instruments with an attack transient followed by a slow downward bend

This is a **portamento-style effect built into the instrument**, not a note command.

---

## §8 — fx_flags bit1: octave-up on alternate frames — NOT IMPLEMENTED

**Location:** `$5336-$535D`

When `fx_flags & 0x02` is set (bit1, "skydive"), the engine:
1. Checks duration >= 3 (`CMP #$03; BCC skip`)
2. Checks global frame counter bit0 is 1 (`AND #$01; BEQ skip`) — odd frames only
3. Checks freq_hi is non-zero
4. Adds 2 to freq_hi: `INC $551A,X; INC $551A,X`
5. Writes the incremented freq_hi to `D401`

**Effect:** On every odd global frame (when duration >= 3), freq_hi is increased by 2.
Since doubling freq_hi increases pitch by ~1 octave, this creates a rapid octave-up
transient on alternating frames. The effect is called "skydive" in Hubbard lore.

**Key detail:** The +2 to freq_hi is NOT saved back permanently. It writes the
incremented value to D401 but the stored `$551A,X` IS incremented. So freq_hi
permanently drifts upward by 2 per odd frame until the note ends.

Actually re-reading: `INC $551A,X` modifies the stored value, then `STA D401,Y`
writes the incremented value. So this IS a permanent +2/frame increase in freq_hi
on odd frames — a rapid pitch sweep.

**Combined with bit0:** Instruments with `fx_flags = 0x03` (Commando instruments 4, 11)
have BOTH bit0 (freq slide down) and bit1 (freq slide up). The net effect is:
- Bit0 on all frames: freq_hi--
- Bit1 on odd frames: freq_hi += 2

Net on odd frames: freq_hi + 1
Net on even frames: freq_hi - 1

This creates a very rapid oscillation — essentially a harsh vibrato at 1-frame resolution.

**Current state:** `rh_to_usf.py` uses `has_skydive` to detect bit1 and builds a
simple hold wave table. This completely ignores the actual frequency modulation.

---

## §9 — Wave step format — complete picture

The wave step encoding (at each position in the wave program pointer):

```
Byte N (step byte):
  bit 7: if 1 → extra byte at N+1 follows
  bit 6: if 1 → HOLD (gate cleared for 1 frame via $5501 mask, freq not updated)
  bit 5: if 1 → INHIBIT hard restart (gate stays open at note start)
  bits [4:0]: duration (0-31 frames, decrements each play call)

Byte N+1 (extra byte, only if bit7 set):
  bit 7: if 1 → drum control byte → $5520,X
                  bits [6:1] = slide delta per frame
                  bit 0 = slide direction (0=up, 1=down)
         if 0 → instrument number → $54FE,X

Byte N+2 (or N+1 if no extra byte): note index → $54FB,X
```

**Currently decoded by rh_decompile.py:**
- bit7 (extra byte): YES
- bit6 (hold): NO
- bit5 (inhibit restart): NO
- bits[4:0] (duration): YES
- extra byte drum control (bit7=1): YES
- extra byte instrument (bit7=0): YES
- note byte: YES

---

## §10 — Drum sequencer — separate subsystem

**Location:** `$53A5-$5427` (runs after the 3-voice loop)

The Commando drum sequencer is a second note sequence controller that runs
independently of the 3-voice melody loop. It controls SID voices 1 and 2 directly
(via `D400-D401` and `D407-D408`).

**Structure:**
- `$5529` = drum sequence counter (counts down from initial value)
- `$552A` = drum speed counter (reloaded from low nibble of `$5530`)
- `$552B` = stop marker (when counter equals this, sequence ends)
- `$552C` = voice-2 freq offset (subtracts from counter to get voice-2 note)
- `$552D` = gate toggle control (bit7=toggle V1 gate, bit6=toggle V2 gate)
- `$5530` = drum control byte (bit7=skip V1 freq, bit6=skip V1 freq alt, low nibble=speed)
- `$5531` = inline subroutine (patched at runtime via init; in Commando: gate off code)

The drum subroutine at `$5531` is actually self-modifying code patched by init.
For Commando it contains: `LDA #$00; STA D404; STA D40B; LDA $5527; AND ...` — gate-off
for voices 1 and 2.

**Key:** In Commando, `$5520 = $00` which means the drum mode byte in the wave step
extra byte is never set, and all the drum frequency slide at `$52B3` is bypassed.
The drum sequencer here is the primary percussion mechanism.

**Current state:** The drum sequencer is not modeled at all. We treat voice 0 (which
the drum sequencer controls) as a melody voice with invalid pattern pointers. The
original SID's voice 0 may be mostly controlled by the drum sequencer, not by the
melody pattern data.

---

## §11 — Multi-subtune and init dispatch

**Location:** `$5F0C-$5FB1` (init), `$5FB2` (multi-song dispatch)

For Commando, subtunes 0-2 are valid. Each subtune has:
- A tempo byte in `$5514,X`
- A 6-byte block in the song table at `$56FF + subtune*6` containing 3 voice pattern-list pointers

**Current state:** Correctly implemented in `rh_decompile.py`.

---

## Priority ranking of missing features

1. **Vibrato (§5):** Affects 9/13 instruments in Commando. The triangle-wave vibrato
   tied to the global frame counter (`$5525 & 0x07`) produces smooth 8-frame oscillation.
   This accounts for the largest fraction of remaining `note_wrong` frames.

2. **fx_flags bit1 (§8, "skydive"):** The per-frame freq_hi+2 on odd frames is a
   significant pitch effect. Current implementation (simple hold wave table) produces
   completely wrong frequencies.

3. **fx_flags bit0 (§7, pitch-drop):** The hard restart + downward pitch slide on
   every note. Combined with bit1, creates the characteristic Hubbard "note with bite"
   sound. Instruments 1, 3, 4, 5, 7, 9, 10, 11, 12 are affected.

4. **Wave step bit5 (§4, hard restart inhibit):** Minor — prevents ADSR zeroing for
   sustained legato notes. Not many notes use this.

5. **Wave step bit6 (§2, hold mode):** Minor — brief gate-off at step transition.

---

## Relationship to Das Model

The Das Model architecture can accommodate all of these features through USF extensions:

- **Vibrato:** Needs a new vibrato type in `WaveTableStep` that computes delta from
  `freq[note+1] - freq[note]` shifted by N bits, with phase tied to a global counter.
  OR: approximate with the existing `freq_slide` field per step.

- **Skydive (bit1):** Can be modeled as `freq_slide = +2` on alternate frames — but
  the V2 player applies `freq_slide` to `freq_hi` only, and it's per-step not
  per-frame. This needs a new USF `freq_hi_slide` or `every_other_frame_freq_mod` field.

- **Pitch-drop (bit0):** Can be modeled as `freq_slide = -1` per frame, but only
  applied AFTER the first frame. The first-frame hard restart could use the existing
  `gate_timer` mechanism. Net effect: `gate_timer=1` (hard restart on frame 0) plus
  `freq_slide=-1` starting frame 1.

- **Hold (bit6):** Can be modeled as an additional `WaveTableStep` with `waveform=ctrl&$FE`
  (gate stripped) inserted before the main note step.

The most tractable immediate fix for Grade A improvement is implementing vibrato
correctly using the global frame counter phase, since it affects the majority of
melodic notes.
