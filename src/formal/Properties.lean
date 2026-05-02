/-
  Properties.lean — Theorems about the Das Model compiler.

  These are the mathematical guarantees we want to prove about
  the compilation pipeline. Each theorem states a property that
  any correct Das Model implementation must satisfy.
-/

import SID
import State
import Effects
import Compile

/-
  Property 1: compileFrames is deterministic.
  The same Song always produces the same stream.
  (This is trivially true because all functions are pure.)
-/
theorem compileFrames_deterministic (s : Song) (n : Nat) :
    compileFrames s n = compileFrames s n := rfl

/-
  Property 2: Empty song produces empty stream.
-/
theorem compileFrames_zero (s : Song) :
    compileFrames s 0 = [] := by
  sorry  -- TODO: needs lemma about List.range 0 = [] and foldl on []

/-
  Property 3: compileFrames produces exactly nFrames frames.
-/
theorem compileFrames_length (s : Song) (n : Nat) :
    (compileFrames s n).length = n := by
  sorry  -- TODO: prove by induction on n

/-
  Property 4: Gate-before-ADSR invariant.
  In every note-load frame, the ctrl (gate) write appears before
  the AD/SR writes in the stream. This is critical: writing ADSR
  before gate causes the SID's ADSR to malfunction.

  We express this as: for any note-on writes produced by noteLoad,
  the ctrl write's position in the list is before the AD write's position.
-/
def findWriteIdx (stream : FrameStream) (reg : SIDReg) : Option Nat :=
  stream.findIdx? (fun w => w.reg == reg)

theorem gate_before_adsr (song : Song) (voice : Fin 3)
    (vs : VoiceState) (es : EngineState)
    (h : vs.tickCtr = 0) :
    let (writes, _) := noteLoad song voice vs es
    match findWriteIdx writes (.ctrl voice), findWriteIdx writes (.ad voice) with
    | some ci, some ai => ci < ai
    | _, _ => True  -- if either not present, vacuously true
    := by
  sorry  -- TODO: prove from noteLoad's write list construction

/-
  Property 5: Effect chain ordering.
  In eval frames, vibrato writes appear before arp writes in the stream.
  (Arp overwrites vibrato — this is the intended behavior.)
-/
theorem vibrato_before_arp (chain : EffectChain) (voice : Fin 3)
    (vs : VoiceState) (es : EngineState) (song : Song) (inst : Instrument)
    (_hv : chain.vibrato.isSome) (_ha : chain.arpeggio.isSome) :
    let (_writes, _) := evalEffectChain chain voice vs es song inst
    -- The vibrato writes come from the first segment, arp from the last
    -- This follows from evalEffectChain's concatenation order:
    -- vibWrites ++ slideWrites ++ arpWrites
    True  -- TODO: strengthen to positional claim
    := by trivial

/-
  Property 6: PW shared state consistency.
  After evalPW runs, if the instrument has linear PW mode,
  the new pwLo differs from the old by exactly pw.speed (mod 256).
-/
theorem pw_linear_step (spec : PWSpec) (voice : Fin 3) (vs : VoiceState)
    (hm : spec.mode = .linear) (hs : spec.speed.val ≠ 0) :
    let (_, vs') := evalPW spec voice vs
    vs'.pwLo.val = (vs.pwLo.val + spec.speed.val) % 256 := by
  sorry  -- TODO: unfold evalPW, case split on mode

/-
  Property 7: Bidirectional PW boundary flip uses exact equality.
  When pwHi reaches maxHi, direction flips. When it reaches minHi,
  direction flips back. This uses == (not >= or <), matching Hubbard's BNE.
-/
-- This is encoded in the implementation of evalPW itself.
-- The property is: evalPW produces the correct boundary behavior.
-- We verify this against the Python ground truth rather than proving in Lean.

/-
  Property 8: Triangle LFO produces the correct pattern.
  For period=8: 0,1,2,3,3,2,1,0.
-/
theorem triangle_lfo_period8 :
    (List.range 8).map (triangleLFO 8) = [0, 1, 2, 3, 3, 2, 1, 0] := by
  native_decide

/-
  Property 9: Note-load frames skip effects.
  When tickCtr == noteLen (just loaded), processVoice calls noteLoad
  (not evalFrame), so no effects run.
-/
-- This is structural in processVoice: `if vs.tickCtr == 0 then noteLoad ...`
-- Note-load happens when tickCtr reaches 0, not when tickCtr == noteLen.
-- The effects-skip for just-loaded notes is handled in evalFrame by checking
-- `isNoteStart := vs.tickCtr == vs.noteLen` for PW skip.
