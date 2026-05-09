/-
  SidSemantics.lean — Per-tick DAC-output model of one SID voice.

  The point of this file is to give the tolerance rules in
  `src/sid_compare.py` a *proof* that they are sound. Today those
  rules are heuristic ("if both gates are off, freq diff is inaudible");
  this file lets us write them as theorems instead.

  We start with the simplest rule — "silent voice" — and prove that
  when a voice has no waveform select bit set, its DAC output is zero
  regardless of freq register values. This is what `sid_compare.py`
  asserts at line ~162:

      if (o_wav & 0xF0) == 0 and (n_wav & 0xF0) == 0:
          vr['note_jitter'] += 1   # classify as inaudible

  Modelling notes:
  - The four waveform-output functions (triangle / saw / pulse / noise)
    are declared `opaque` here. Their internal mechanics are not needed
    to prove the silent-voice claim — we only need the fact that when
    *no* waveform is selected, the DAC mux produces 0.
  - The "all waveforms AND together" behaviour matches the real SID
    chip and reSID emulation (multiple selected waveforms are bitwise
    AND'd; no waveform selected means the mux output goes to 0).
  - The model is per-tick (one phi2 cycle). A whole-frame claim
    follows by `List.foldl` over per-tick contributions; we add the
    aggregate lemma at the bottom.
-/

namespace SidSemantics

/-- 12-bit DAC sample. We use UInt16 with the convention that values
    above 0xFFF are not produced by the voice path. -/
abbrev DacSample := UInt16

/-- The four waveform generators are modelled abstractly. We don't need
    to know how they work — only that they each produce a 12-bit value
    when their corresponding control bit is set. -/
opaque triangleSample : (freqAccum : UInt32) → (ringMod : UInt32) → DacSample
opaque sawSample      : (freqAccum : UInt32) → DacSample
opaque pulseSample    : (freqAccum : UInt32) → (pulseWidth : UInt16) → DacSample
opaque noiseSample    : (lfsr : UInt32) → DacSample

/-- One voice's DAC output for one phi2 tick.

    `ctrl` is the voice control register. Bits 4-7 select waveforms
    (TRI / SAW / PULSE / NOISE). When all four are zero, the waveform
    mux outputs 0 — this is the property that makes the silent-voice
    tolerance rule sound.

    When one or more waveforms are selected, the SID hardware AND's
    them together (a documented quirk of the chip). -/
def voiceDacSample
    (ctrl : UInt8)
    (freqAccum : UInt32) (pulseWidth : UInt16)
    (ringSrc : UInt32) (lfsr : UInt32) : DacSample :=
  let wavMask := ctrl >>> 4   -- bits 4-7 of ctrl, shifted into 0-3
  if wavMask = 0 then
    -- No waveform selected → the mux output is 0.
    0
  else
    -- AND together the selected waveforms; default 0xFFF for unselected
    -- ones so the AND leaves them transparent.
    let tri := if wavMask &&& 1 ≠ 0 then triangleSample freqAccum ringSrc else 0xFFF
    let saw := if wavMask &&& 2 ≠ 0 then sawSample freqAccum else 0xFFF
    let pul := if wavMask &&& 4 ≠ 0 then pulseSample freqAccum pulseWidth else 0xFFF
    let nse := if wavMask &&& 8 ≠ 0 then noiseSample lfsr else 0xFFF
    tri &&& saw &&& pul &&& nse

/-! ## The silent-voice rule, proved sound. -/

/-- A voice with no waveform select bit set produces 0 DAC output. -/
theorem silent_voice_zero_dac
    (ctrl : UInt8)
    (freqAccum : UInt32) (pulseWidth : UInt16)
    (ringSrc : UInt32) (lfsr : UInt32)
    (h_silent : ctrl >>> 4 = 0) :
    voiceDacSample ctrl freqAccum pulseWidth ringSrc lfsr = 0 := by
  unfold voiceDacSample
  rw [if_pos h_silent]

/-- **Soundness of the silent-voice tolerance rule.**

    Two voice states differing in *any* of the inputs other than `ctrl`
    — including the freq accumulator (downstream of freq_lo / freq_hi
    register writes) — produce identical DAC output, provided neither
    has a waveform selected.

    This is exactly the claim `sid_compare.py:162` makes when it
    classifies freq diffs as inaudible during silent frames. -/
theorem silent_voice_freq_inaudible
    (ctrl : UInt8)
    (freqAccum1 freqAccum2 : UInt32)
    (pulseWidth1 pulseWidth2 : UInt16)
    (ringSrc1 ringSrc2 : UInt32) (lfsr1 lfsr2 : UInt32)
    (h_silent : ctrl >>> 4 = 0) :
    voiceDacSample ctrl freqAccum1 pulseWidth1 ringSrc1 lfsr1
      = voiceDacSample ctrl freqAccum2 pulseWidth2 ringSrc2 lfsr2 := by
  rw [silent_voice_zero_dac _ _ _ _ _ h_silent,
      silent_voice_zero_dac _ _ _ _ _ h_silent]

/-! ## Aggregate claim: across a whole frame, silent voice contributes 0. -/

/-- Per-tick state for one voice: (freqAccum, pulseWidth, ringSrc, lfsr). -/
abbrev TickState := UInt32 × UInt16 × UInt32 × UInt32

/-- Sum of voice DAC outputs across a list of phi2 ticks. -/
def voiceFrameSum (ctrl : UInt8) (ticks : List TickState) : Nat :=
  ticks.foldl (fun acc s =>
    acc + (voiceDacSample ctrl s.1 s.2.1 s.2.2.1 s.2.2.2).toNat) 0

/-- Generic lemma: a `foldl` whose per-step contribution is always 0
    leaves the accumulator unchanged. Used by `silent_voice_frame_zero`. -/
private theorem foldl_add_zero {α : Type}
    (xs : List α) (f : α → Nat) (start : Nat)
    (h : ∀ x ∈ xs, f x = 0) :
    xs.foldl (fun acc x => acc + f x) start = start := by
  induction xs generalizing start with
  | nil => rfl
  | cons x rest ih =>
    have h0 : f x = 0 := h x (List.mem_cons_self)
    have hrest : ∀ y ∈ rest, f y = 0 := fun y hy => h y (List.mem_cons_of_mem _ hy)
    show rest.foldl (fun acc y => acc + f y) (start + f x) = start
    rw [h0, Nat.add_zero]
    exact ih start hrest

/-- A silent voice contributes 0 to the audio mix across an entire frame,
    regardless of how many ticks the frame spans or what the per-tick
    accumulator / pulse / lfsr values are. -/
theorem silent_voice_frame_zero
    (ctrl : UInt8) (ticks : List TickState)
    (h_silent : ctrl >>> 4 = 0) :
    voiceFrameSum ctrl ticks = 0 := by
  unfold voiceFrameSum
  apply foldl_add_zero ticks _ 0
  intro s _
  rw [silent_voice_zero_dac _ _ _ _ _ h_silent]
  rfl

end SidSemantics
