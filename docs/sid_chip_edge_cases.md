# SID Chip Edge Cases and Undocumented Behaviors

**Status:** Research document for Das Model implementation validation.
**Sources:** libsidplayfp source (SIDLite backend, cRSID-derived), WavGen.cpp, ADSR.cpp, Filter.cpp
in this repository's tools/libsidplayfp tree, plus well-documented C64 community knowledge.

This document covers seven edge-case areas where the real 6581/8580 hardware departs from the
naive register-write model assumed by most software players, and maps each to its impact on the
SIDfinity pipeline.

---

## 1. ADSR Envelope Bug (6581 and 8580)

### What the bug is

The SID envelope generator uses a 15-bit linear feedback rate counter (LFSR) to divide time into
envelope "ticks." Each tick, the 8-bit envelope counter is incremented (attack) or decremented
(decay/release) according to an exponent lookup table.

The bug: the LFSR rate counter is NOT reset to zero when a new gate edge arrives. It is only
reset when a period match fires. This means the first tick of any new envelope phase can arrive
anywhere from 1 to the full period length after gate triggers. The delay is non-deterministic
from the player's perspective — it depends on the counter's state at the moment of the gate
write.

Consequence: On short attack rates (e.g., A=0, period=9 cycles), the first envelope step can
be delayed up to 9 cycles relative to the gate write. On long attack rates (A=F, period=31251
cycles) the first step can be delayed nearly one full VBI frame.

The best-known symptom: if a player zeros ADSR registers and then re-gates a voice (hard
restart), the new note's attack may start slightly late. This is exactly why the GT2 hard-restart
mechanism zeroes ADSR several frames before re-gating rather than on the same frame.

### Does sidplayfp (SIDLite) emulate it?

Yes. In ADSR.cpp line 92-94:
```c
*RateCounterPtr += cycles;
if (UNLIKELY(*RateCounterPtr >= 0x8000))
    // can wrap around (ADSR delay-bug: short 1st frame)
    *RateCounterPtr -= 0x8000;
```
The rate counter wraps on overflow (matching the real LFSR wrap behavior) rather than resetting.
The comment explicitly names the "ADSR delay-bug: short 1st frame." So our ground-truth
siddump traces already include this bug effect.

### Impact on Das Model

**Low for register-level comparison.** The ADSR bug affects the audio waveform (envelope
amplitude), not the SID register values that siddump captures. Our pipeline compares register
writes (freq, ctrl, PW, AD, SR), not the internal envelope counter state. The bug creates ±1
frame timing shifts in ADSR-register comparisons only when hard restart is involved, which is
already handled by the `env_wrong` 1% tolerance and the gate-off jitter rules.

**Conclusion:** No change to pipeline needed. The bug is absorbed by existing tolerances.

---

## 2. Combined Waveforms

### What happens on real hardware

When multiple waveform bits are set simultaneously in the control register (bits 4-7), the SID
does not simply mix them. The 12-bit R-2R DAC ladder receives inputs from all active waveform
circuits ANDed together at the analog comparator level. Because the comparators have non-zero
thresholds, the AND is not a clean digital AND — bits "pull toward zero" in a non-linear way
that depends on manufacturing process and die revision.

The result is a waveform that looks roughly like a digitally ANDed output but with smooth
transitions and amplitude that varies by chip sample. The waveform bit patterns commonly used
by tracker composers are:

| Ctrl byte | Waveforms | Common use |
|-----------|-----------|------------|
| $30       | SAW + TRI | Warm lead sound, slightly different from either alone |
| $50       | SAW + PULSE | Aggressive pulse-modulated saw |
| $60       | SAW + PULSE (wrong) | Actually pulse+saw = $60 |
| $70       | PULSE + SAW + TRI | Three combined |
| $41       | PULSE only + gate | Standard pulse; no combination |

Chip revisions: The 6581 (old breadbox C64) and 8580 (C64C, flat case) produce measurably
different combined waveforms. The 6581 has the oscillator MSB inverted for combined
SAW+TRI, which the 8580 does not. SIDLite handles this:

```c
// In WavGen.cpp, combinedWF lambda:
if (UNLIKELY(!s->is8580() && WFarray!=PulseTriangle))
    oscval &= COMBINEDWF_OSC_MSB_OFF_MASK;  // 0x7FF — mask out MSB on 6581
```

The cw_tables.h contains pre-computed tables (PulseSawTriangle, PulseSawtooth,
PulseTriangle, SawTriangle) derived from oscilloscope measurements and the recursive
comparator model described in that file's comments.

### Impact on Das Model

The Das Model Wave Program (W) writes control register bytes directly as-is. When the instrument
binary specifies $30 (SAW+TRI), the wave table contains $30 and the player writes $30. SIDLite
then produces the combined waveform from its lookup tables.

**No pipeline change needed.** The Das Model is correct by construction — it writes the exact
byte the composer intended. The emulator handles the analog modeling. The register comparison
captures the control register value ($30), not the resulting audio sample, so there is no
combined-waveform comparison problem.

The only risk is if a converter (gt2_to_usf, rh_to_usf) incorrectly modifies a combined
waveform byte. Converters must preserve all 8 bits of the control byte without masking.

---

## 3. Ring Modulation Details

### How ring mod works on the 6581

Ring modulation on the SID is a hardware feature built into the triangle waveform generator.
It is NOT a separate multiplier or carrier/modulator pair. The behavior is:

When bit 2 of a voice's control register (RING_MOD bit, $04) is set AND the voice uses the
triangle waveform (bit 4, $10), the triangle oscillator's MSB is XOR'd with the MSB of voice 3's
oscillator before the waveform lookup:

```
if ring_mod_on:
    phase_input = voice_own_phase XOR (voice3_MSB_state)
else:
    phase_input = voice_own_phase
```

This creates an amplitude modulation effect (not true ring modulation in the signal-processing
sense). The rate and timbre depend on the frequency ratio between the voice and voice 3.

SIDLite implements this in WavGen.cpp:
```c
case TRI_BITVAL:
    int Tmp = *PhaseAccuPtr ^ (UNLIKELY(WF&RING_BITVAL) ? RingSourceMSB : 0);
    WavGenOut = (Tmp ^ (Tmp&PHASEACCU_MSB_BITVAL ? PHASEACCU_MAX : 0)) >> (CRSID_WAVE_SHIFTS-1);
```

And for PULSE+TRI combined:
```c
case PULTRI_VAL:
    int Tmp = *PhaseAccuPtr ^ ((WF&RING_BITVAL)? RingSourceMSB : 0);
```

The `RingSourceMSB` variable is updated each sample from voice 3's previous phase accumulator
MSB:
```c
RingSourceMSB = MSB;  // set after processing each channel, voice 3 is processed last
```

**Voice 3 gate-off behavior:** Ring modulation works regardless of whether voice 3's gate is on
or off. Voice 3's oscillator runs continuously as long as the test bit is not set. The gate only
controls the envelope (amplitude), not the oscillator. So even with voice 3 silenced (gate=0,
env=0), its phase accumulator keeps running and modulates any voices with ring mod enabled.

**Important quirk:** Ring mod only XORs the triangle waveform's internal phase, not pulse or
saw. The RING bit is silently ignored for non-triangle waveforms. Composers and drivers that set
RING together with SAW or PULSE get no ring effect.

### Impact on Das Model

The Das Model writes ctrl bytes that include the RING bit. Since the emulator handles the ring
modulation physics, the Das Model pipeline is correct as long as it:
1. Preserves the RING bit in the ctrl byte (W program step)
2. Preserves voice 3's frequency register values so voice 3's oscillator runs at the intended rate
3. Does NOT silence voice 3 when it is used as a ring modulator (voice3_as_modulator flag in USF)

The `voice3_as_modulator` USF field exists exactly for case 3 — when voice 3 is used as a
modulator, the converter should not suppress its register writes.

---

## 4. Test Bit Behavior ($08 in ctrl register)

### What the test bit does

The test bit (control register bit 3, $08) has three separate effects that happen simultaneously:

**Effect 1 — Oscillator reset.** The phase accumulator for the voice is forced to zero while
the test bit is set. In SIDLite:
```c
if (UNLIKELY(TestBit || ((WF & SYNC_BITVAL) && SyncSourceMSBrise)))
    *PhaseAccuPtr = 0;
```
The oscillator does not advance. The phase stays at 0 until the test bit is cleared.

**Effect 2 — Noise LFSR fill.** While the test bit is set, the noise LFSR for this voice has
all its bits forced to 1 (logically — in hardware, the bit shifting still occurs but feedback
is replaced with 1). On a real 6581 this takes approximately 8000 microseconds (~300 cycles) to
fully saturate. SIDLite approximates this instantly:
```c
// in noise case:
Tmp = ((Tmp << 1) | Feedback|TestBit) & 0x7FFFFF;
```
Forcing `|TestBit` means each clock cycle the shift-in bit is OR'd with 1, filling the LFSR
with 1s within 23 clock cycles (the LFSR is 23 bits).

**Effect 3 — Pulse waveform output.** While the test bit is set, pulse waveform output is forced
to $FFFF (maximum):
```c
if (UNLIKELY(TestBit))
    WavGenOut = CRSID_WAVE_MAX; // 0xFFFF;
```

**Hard restart use:** Many SID players use the test bit as part of hard restart: they set
test bit to reset the oscillator's phase, then clear it (and set gate) on the same or next frame
to start from a known phase. This avoids the click that occurs when a new note starts mid-cycle
with a non-zero phase. The GT2 hard restart sequence ($09 = test+gate → $11 = tri+gate) exploits
this.

**"Different sources say different things":** The confusion comes from:
- Some sources say "test bit resets oscillator" (correct)
- Some say "test bit freezes oscillator" (also correct — while set, accumulator stays at 0)
- Some say "test bit enables noise LFSR seeding" (correct, but it is a side effect)
- Some say "test bit affects pulse only" (wrong — pulse is one of three effects)

The test bit does ALL of the above simultaneously. They are not alternatives.

### Impact on Das Model

The Das Model V1 Wave Program includes test bit bytes ($08, $09) as regular wave table steps.
The emulator handles all three effects automatically. The pipeline is correct.

The `wave_jitter` classification in sid_compare.py ($08/$09 near gate transitions) correctly
identifies test-bit frames as measurement artifacts rather than errors. This is the right policy
— both player and original use test-bit writes at equivalent points in the note lifecycle.

---

## 5. Frequency Register Write Effects

### Do freq_lo/freq_hi writes cause oscillator glitches?

The SID frequency registers ($D400/$D401 for voice 1) feed directly into the phase accumulator
step size. The phase accumulator advances by `(freq_hi << 8) | freq_lo` every clock cycle.

When a player writes freq_hi and freq_lo separately (two consecutive writes, as all 6502 code
must do), there is a one-cycle window between the writes where only one byte has been updated.
During that single cycle the step size is:
- If freq_lo written first: `(old_freq_hi << 8) | new_freq_lo` (incorrect)
- If freq_hi written first: `(new_freq_hi << 8) | old_freq_lo` (incorrect)

At 1 MHz, one cycle is 1 microsecond. At typical SID frequencies (e.g., A4 = 17897 = $45E9),
the phase accumulator advances about 17897 units per 1MHz cycle. In one incorrect cycle, the
phase error is at most ~17897 units out of 16,777,216 total (24-bit accumulator) = 0.1% phase
error. This is inaudible.

**Conclusion:** The write order glitch is real but inaudible. No pipeline change needed.

The SIDLite emulator runs the wave generator at the audio sample rate (not 1 MHz), so it reads
both frequency registers as a 16-bit value each sample — the one-cycle partial-write window
does not exist in emulation. This means our ground-truth traces (from siddump) are actually
cleaner than real hardware in this regard.

### Write order conventions in the pipeline

The Hubbard player writes frequency registers in the order: freq_lo then freq_hi. Das Model
code generator (`das_model_gen.py` line 517) matches this order. The GT2 V2 player writes
freq_lo then freq_hi in codegen_v2.py. This is consistent and matches what siddump expects.

---

## 6. Pulse Width (PW) Register Update Timing

### Does PW update immediately or at next cycle?

On the real SID, the pulse width comparator checks the current PW register value against the
current phase accumulator value on every clock cycle. When a player writes to the PW registers
($D402/$D403), the comparator reads the new value on the very next clock cycle.

There is no "latch" or buffering for PW. The update is effectively immediate at the cycle
boundary after the write.

The one-cycle partial-write issue applies here too (PW_LO written, then PW_HI), but the
audible effect is negligible for the same reason as frequency writes: one incorrect cycle out of
~17,000 cycles per period.

SIDLite reads PW from registers each sample:
```c
static inline unsigned short getPW(unsigned char* channelptr)
{
    // PW=0000..FFF0 from SID-register (000..FFF)
    return getCombinedPW(channelptr) << 4;
}
```
No buffering — direct register read each sample tick. This matches the real chip behavior.

### Impact on Das Model

PW modulation in Das Model (the P program) writes PW registers every frame. Since the SID
updates PW immediately, frame-rate PW writes produce the expected pulse-width modulation
effect without any synchronization concerns.

The Das Model's pulse program is intentionally frame-granular (not cycle-precise). This matches
the GT2 player's PW update rate and is correct.

---

## 7. Filter Behavior: Does It Affect Unrouted Voices?

### Does the 6581 filter affect voices even when filter routing is off?

Register $D417 controls filter routing: bits 0-2 enable filtering for voices 1-3 respectively.
Voice 3's output can additionally be disconnected from the master output entirely using bit 7 of
$D418 (the "OFF3" bit).

**For voices not routed to the filter:** Their signal bypasses the filter circuit and goes
directly to the output summer. The filter circuit does not process them.

**HOWEVER**, the 6581 filter has a well-documented "bleed-through" artifact. Due to the
analog design of the VCF (voltage-controlled filter using MOSFET variable resistors), unfiltered
voices can partially bleed into the filter's signal path at high resonance settings. This is a
physical coupling artifact from the chip layout, not a design feature.

Additionally, the 6581's filter cutoff curve is non-linear and the input impedance of the
filter circuit draws some current from unfiltered voices. At extreme resonance, this creates
subtle tonal coloring of nominally unfiltered voices.

**The 8580 does not have this bleed-through.** Its filter uses a cleaner circuit design.

SIDLite implements the 6581 cutoff non-linearity and a simplified version of the input-signal
feedback:
```c
// In Filter.cpp, 6581 branch:
Cutoff += (FilterInput*105)>>16;  // input-signal modulates cutoff (distortion emulation)
```
This is the "MOSFET-VCR control-voltage calculation" comment. It does NOT implement the
bleed-through of unfiltered voices into the filter — but the cutoff modulation by the filtered
signal itself is present.

**Voice 3 special case:** When bit 7 of $D418 is set (the OFF3 bit), voice 3 is disconnected
from both the filtered AND unfiltered output paths. SIDLite:
```c
else if (LIKELY(Channel!=3 || !(VolumeBand & OFF3_BITVAL)))
{
    NonFiltered += (swave * Envelope) / ENVELOPE_MAGNITUDE_DIV;
}
```
When `Channel==3` (0-indexed, so voice 3) and `OFF3_BITVAL` is set, voice 3 contributes zero
to NonFiltered. However voice 3's oscillator still runs (for ring mod and sync).

### Impact on Das Model

The Das Model correctly handles this by:
1. Writing $D417 (filter routing) and $D418 (filter mode/volume) from the filter table
2. The `voice3_as_modulator` USF flag prevents voice 3's audio from being included in the
   output when it is used only as a ring mod source

The 6581 bleed-through is an analog artifact that the SIDLite emulator only approximates. Since
we compare against SIDLite output (not real hardware), our pipeline is internally consistent.
Any bleed-through in the original SID playback is equally present in both the original and
rebuilt SID traces through siddump, so comparison grades are unaffected.

---

## Summary Table: Das Model Impact Assessment

| Edge Case | Real Chip Behavior | SIDLite Emulates? | Das Model Impact |
|-----------|-------------------|-------------------|-----------------|
| ADSR delay bug | Rate counter not reset on gate | Yes (wrap-on-overflow) | None — absorbed by env_wrong tolerance |
| Combined waveforms | Analog AND via comparator threshold | Yes (lookup tables) | None — ctrl byte written as-is |
| Ring mod mechanics | Triangle XOR with voice 3 MSB | Yes (exact) | None — ctrl byte preserved |
| Ring mod with gate-off V3 | V3 oscillator runs regardless | Yes | None — V3 freq must be written |
| Test bit — osc reset | Phase accumulator frozen at 0 | Yes | None — wave table byte written as-is |
| Test bit — noise fill | LFSR fills with 1s (~8000us) | Approximated (instant) | None — timing difference is sub-cycle |
| Test bit — pulse max | Pulse output forced to max | Yes | None |
| Freq write glitch | 1-cycle partial-value step size | Not emulated (sample-rate) | None — inaudible, not in ground truth |
| PW immediate update | No latch, updates next cycle | Yes (sample-rate direct read) | None |
| Filter routing off | Signal bypasses filter | Yes | None |
| 6581 filter bleed-through | Unfiltered signal couples into VCF | Partial (input modulates cutoff) | None — consistent in both streams |
| OFF3 bit | Voice 3 removed from audio output | Yes | None — `voice3_as_modulator` flag |

**Bottom line:** None of the seven edge cases require changes to the Das Model, USF format, or
pipeline code. The SIDLite emulator correctly handles all behaviors that affect register-level
playback. The edge cases that SIDLite approximates (noise fill timing, 6581 bleed-through) are
consistent between the original and rebuilt SID traces, so they cancel out in comparison grading.

---

## Notes on Chip Revision Differences (6581 vs 8580)

The SIDLite emulator defaults to MOS6581 in our siddump configuration (siddump.cpp line 194:
`cfg.defaultSidModel = SidConfig::MOS6581`). PSID files specify their target model in the
header; siddump reports this in the JSON metadata. The comparison pipeline uses the model
reported by siddump for the original SID.

Key differences that affect audio output but not register values:

1. **ADSR DAC non-linearity:** The 6581 has a non-linear mapping from envelope counter (0-255)
   to DAC output due to a mismatch in the R-2R ladder. SIDLite corrects for this with
   `ADSR_DAC_6581[]` (256-entry table in WavGen.cpp). The 8580 has a linear mapping.

2. **Filter cutoff curve:** 6581 has a non-linear VCR-based curve with a 220Hz minimum cutoff.
   8580 has a linear resistor-ladder curve with near-zero minimum. Dramatically different sound.

3. **Combined waveforms:** 6581 masks out oscillator MSB for SAW+TRI and similar combinations.
   8580 does not. Different waveform shapes result.

4. **DC offset:** 6581 outputs are asymmetric (DC offset ~5V on audio out). 8580 is centered.
   This affects distortion characteristics when overdriving the chip.

None of these affect the register comparison used for grading.
