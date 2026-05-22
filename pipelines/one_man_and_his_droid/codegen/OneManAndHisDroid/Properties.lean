/-
  PropertiesV3.lean — invariants and theorems about the V3 codegen output.

  Goal: catch regressions at compile time. If any of these properties stop
  holding, `lake build` fails and we know something important changed shape.

  Layers:
  1. Boundary serialisation primitives (sizes, endianness, magic bytes).
  2. PSID file structure (header is always prepended).
  3. CodeBuilder invariants (fixups stay in-bounds across emit ops).
  4. Sub-block preservation through `emitInit` (the first real codegen
     helper threaded end-to-end).

  Layers 3 and 4 are the ones that catch real codegen regressions: if
  some new emit function fails to grow `bytes` enough to hold its fixup
  target, the invariant breaks at compile time rather than producing a
  corrupt SID at run time.

  What's still NOT here (left as future work, with honest reasons):
  - "After note-load, Y holds v_sidoff[X]" — register-state Hoare-logic
    invariants. Would have caught the porta-init Y-clobber bug. But
    formalising this requires a 6502 step semantics applied to specific
    emitted byte sequences — research-level effort, not 1-2 weeks.
  - "Every targetLabel referenced has a corresponding label declaration."
    Tractable but requires a separate "labelsDeclared" invariant that's
    threaded through every emit/label call site. The current codegen
    lets fixups reference *forward* labels (declared later in the same
    Id.run do block), so the property only holds *after* `cb.resolve`,
    and stating that cleanly needs an existential over label-decl order.
-/
import OneManAndHisDroid.Asm6502
import OneManAndHisDroid.PSIDFile
import OneManAndHisDroid.Codegen

open OneManAndHisDroidNS

namespace PropertiesV3

-- ==========================================================================
-- 1. Byte-serialisation primitives have the size you'd expect
-- ==========================================================================

/-- A big-endian `UInt16` always serialises to 2 bytes. -/
theorem writeBE16_size (v : UInt16) : (writeBE16 v).size = 2 := rfl

/-- A big-endian `UInt32` always serialises to 4 bytes. -/
theorem writeBE32_size (v : UInt32) : (writeBE32 v).size = 4 := rfl

/-- A raw little-endian word always serialises to 2 bytes. -/
theorem rawWord_size (v : UInt16) : (rawWord v).size = 2 := rfl

-- ==========================================================================
-- 2. Endianness
-- ==========================================================================

/-- The first byte of a big-endian write is the high byte. -/
theorem writeBE16_hi (v : UInt16) : (writeBE16 v)[0]! = (v >>> 8).toUInt8 := rfl

/-- The second byte of a big-endian write is the low byte. -/
theorem writeBE16_lo (v : UInt16) : (writeBE16 v)[1]! = v.toUInt8 := rfl

/-- The low byte of `rawWord` comes first (little-endian, matches 6502). -/
theorem rawWord_lo_first (v : UInt16) : (rawWord v)[0]! = v.toUInt8 := rfl

/-- The high byte of `rawWord` comes second. -/
theorem rawWord_hi_second (v : UInt16) : (rawWord v)[1]! = (v >>> 8).toUInt8 := rfl

/-- `writeBE32`'s bytes are highest-to-lowest. -/
theorem writeBE32_byte0 (v : UInt32) : (writeBE32 v)[0]! = (v >>> 24).toUInt8 := rfl
theorem writeBE32_byte1 (v : UInt32) : (writeBE32 v)[1]! = (v >>> 16).toUInt8 := rfl
theorem writeBE32_byte2 (v : UInt32) : (writeBE32 v)[2]! = (v >>>  8).toUInt8 := rfl
theorem writeBE32_byte3 (v : UInt32) : (writeBE32 v)[3]! =  v.toUInt8         := rfl

-- ==========================================================================
-- 3. PSID file structure: header is always prepended
-- ==========================================================================

/-- Both branches of `buildSID` prepend the serialised PSID header — the
    only difference is what comes after. So every produced `.sid` file
    starts with `serializeHeader h`. -/
theorem buildSID_starts_with_header (h : PSIDHeader) (payload : Bytes) :
    ∃ rest, buildSID h payload = serializeHeader h ++ rest := by
  unfold buildSID
  split
  · exact ⟨rawWord h.initAddr ++ payload, by simp [Array.append_assoc]⟩
  · exact ⟨payload, rfl⟩

/-- The hard-coded magic bytes match ASCII "PSID". A regression here would
    mean we changed the magic constants and broke the file format. -/
theorem psid_magic_is_ascii :
    [0x50, 0x53, 0x49, 0x44] = "PSID".toUTF8.toList := by native_decide

-- ==========================================================================
-- 4. CodeBuilder invariants: fixups stay in-bounds
-- ==========================================================================

/-- For every fixup recorded in the builder, the bytes it will eventually
    overwrite during `resolve` are already within `cb.bytes`.

    For non-relative branch fixups (JMP/JSR) and abs-fixups (LDA/STA abs,X
    etc), `resolve` writes two bytes at `byteIdx` and `byteIdx+1`, so we
    need `byteIdx + 1 < bytes.size`. For relative-branch fixups, only one
    byte at `byteIdx` is written.

    Once this holds, the `bytes.set!` calls inside `resolve` cannot
    silently extend the array or overwrite something unrelated to the
    instruction the fixup describes. -/
def fixupsInBounds (cb : CodeBuilder) : Prop :=
  (∀ f ∈ cb.fixups,
      if f.isRelative then f.byteIdx < cb.bytes.size
      else f.byteIdx + 1 < cb.bytes.size) ∧
  (∀ f ∈ cb.absFixups, f.byteIdx + 1 < cb.bytes.size)

/-- The default-constructed CodeBuilder (empty bytes, no fixups) trivially
    satisfies the invariant. This is the base case for every `generateSID`
    run. -/
theorem fixupsInBounds_empty : fixupsInBounds {} := by
  refine ⟨?_, ?_⟩ <;> intro _ h <;> simp at h

/-- `cb.emit bs` only adds bytes; it never adds fixups. So existing fixups,
    if they were in-bounds before, remain in-bounds after. -/
theorem emit_preserves_fixupsInBounds (cb : CodeBuilder) (bs : Bytes)
    (h : fixupsInBounds cb) : fixupsInBounds (cb.emit bs) := by
  obtain ⟨h1, h2⟩ := h
  refine ⟨?_, ?_⟩
  · intro f hf
    have := h1 f hf
    simp [CodeBuilder.emit] at *
    split
    · case _ hrel =>
        rw [if_pos hrel] at this
        exact Nat.lt_of_lt_of_le this (Nat.le_add_right _ _)
    · case _ hrel =>
        rw [if_neg hrel] at this
        exact Nat.lt_of_lt_of_le this (Nat.le_add_right _ _)
  · intro f hf
    have := h2 f hf
    simp [CodeBuilder.emit] at *
    exact Nat.lt_of_lt_of_le this (Nat.le_add_right _ _)

/-- `cb.label name` only adds a label entry; it doesn't touch bytes or
    fixups, so the invariant is trivially preserved. -/
theorem label_preserves_fixupsInBounds (cb : CodeBuilder) (name : String)
    (h : fixupsInBounds cb) : fixupsInBounds (cb.label name) := h

/-- `cb.emitInst` is just `emit` of an assembled instruction (or no-op if
    assembly fails), so the invariant is preserved. -/
theorem emitInst_preserves_fixupsInBounds (cb : CodeBuilder) (inst : Instruction)
    (h : fixupsInBounds cb) : fixupsInBounds (cb.emitInst inst) := by
  unfold CodeBuilder.emitInst
  split
  · exact emit_preserves_fixupsInBounds cb _ h
  · exact h

/-- `cb.emitByte v` is `emit #[v]` so the invariant is preserved. -/
theorem emitByte_preserves_fixupsInBounds (cb : CodeBuilder) (v : UInt8)
    (h : fixupsInBounds cb) : fixupsInBounds (cb.emitByte v) :=
  emit_preserves_fixupsInBounds cb _ h

/-- `cb.emitData ds` is `emit ds.toArray` so the invariant is preserved. -/
theorem emitData_preserves_fixupsInBounds (cb : CodeBuilder) (ds : List UInt8)
    (h : fixupsInBounds cb) : fixupsInBounds (cb.emitData ds) :=
  emit_preserves_fixupsInBounds cb _ h

/-- `cb.resolve` empties both fixup lists, so the invariant is vacuously
    true after resolve. (Stated as a sanity check: yes, after we've
    finished resolving forward references, no fixups remain to worry
    about.) -/
theorem resolve_fixupsInBounds (cb : CodeBuilder) :
    fixupsInBounds cb.resolve := by
  unfold CodeBuilder.resolve
  refine ⟨?_, ?_⟩ <;> (intro _ h; simp at h)

-- The interesting cases: emit ops that ADD a new fixup. Each must show
-- (a) the new fixup is in-bounds against the post-emit byte count, and
-- (b) all pre-existing fixups remain in-bounds.

/-- A 3-byte emit (opcode + 2-byte addr placeholder) at the end of a
    CodeBuilder has size `old.bytes.size + 3` after the append.
    Helper for the abs-fixup preservation proofs below. -/
private theorem size_after_3_byte_emit (cb : CodeBuilder) (b1 b2 b3 : UInt8) :
    (cb.bytes ++ #[b1, b2, b3]).size = cb.bytes.size + 3 := by
  simp

/-- `emitBranch` adds a relative fixup at `byteIdx = bytes.size + 1` and
    appends 2 bytes (opcode + offset placeholder). The new fixup's
    `byteIdx` is exactly 1 less than the post-emit `bytes.size`, so it
    sits inside the array (specifically: at the offset placeholder). -/
theorem emitBranch_preserves_fixupsInBounds
    (cb : CodeBuilder) (mn : Mnemonic) (target : String)
    (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitBranch mn target) := by
  obtain ⟨h1, h2⟩ := h
  unfold CodeBuilder.emitBranch
  refine ⟨?_, ?_⟩
  · intro f hf
    simp at hf
    rcases hf with hf | hf
    · -- new fixup: byteIdx = bytes.size + 1, isRelative = true.
      -- After emit, new bytes.size = old + 2, so byteIdx < new size.
      subst hf; simp
    · -- old fixup: bytes.size only grew, so still in-bounds.
      have := h1 f hf
      split
      · case _ hrel => rw [if_pos hrel] at this; simp; omega
      · case _ hrel => rw [if_neg hrel] at this; simp; omega
  · intro f hf
    have := h2 f hf
    simp; omega

/-- `emitJmpLabel` adds a non-relative fixup at `byteIdx = bytes.size + 1`
    and appends 3 bytes (opcode + 2-byte addr placeholder). The new fixup
    needs `byteIdx + 1 < bytes.size`, which holds since
    `(old + 1) + 1 = old + 2 < old + 3`. -/
theorem emitJmpLabel_preserves_fixupsInBounds
    (cb : CodeBuilder) (mn : Mnemonic) (target : String)
    (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitJmpLabel mn target) := by
  obtain ⟨h1, h2⟩ := h
  unfold CodeBuilder.emitJmpLabel
  refine ⟨?_, ?_⟩
  · intro f hf
    simp at hf
    rcases hf with hf | hf
    · subst hf; simp
    · have := h1 f hf
      split
      · case _ hrel => rw [if_pos hrel] at this; simp; omega
      · case _ hrel => rw [if_neg hrel] at this; simp; omega
  · intro f hf
    have := h2 f hf
    simp; omega

/-- Helper: the abs-fixup-emitting operations all share the same shape —
    add an `AbsFixup` at `byteIdx = bytes.size + 1`, append `#[op, 0, 0]`.
    Proving the invariant once for this shape covers `emitLdaAbsX`,
    `emitLdaAbsY`, `emitStaAbsX`, `emitStaAbsY`, `emitDecAbsX`,
    `emitIncAbsX`. -/
private theorem absFixup_emit_preserves
    (cb : CodeBuilder) (op : UInt8) (target : String)
    (h : fixupsInBounds cb) :
    fixupsInBounds
      { cb with bytes := cb.bytes ++ #[op, 0, 0],
                absFixups := { byteIdx := cb.bytes.size + 1,
                               targetLabel := target } :: cb.absFixups } := by
  obtain ⟨h1, h2⟩ := h
  refine ⟨?_, ?_⟩
  · intro f hf
    have := h1 f hf
    split
    · case _ hrel => rw [if_pos hrel] at this; simp; omega
    · case _ hrel => rw [if_neg hrel] at this; simp; omega
  · intro f hf
    simp at hf
    rcases hf with hf | hf
    · subst hf; simp
    · have := h2 f hf; simp; omega

/-- All six abs-fixup emit operations preserve the invariant via the
    shared shape above. -/
theorem emitLdaAbsX_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitLdaAbsX target) :=
  absFixup_emit_preserves cb 0xBD target h

theorem emitLdaAbsY_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitLdaAbsY target) :=
  absFixup_emit_preserves cb 0xB9 target h

theorem emitStaAbsX_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitStaAbsX target) :=
  absFixup_emit_preserves cb 0x9D target h

theorem emitStaAbsY_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitStaAbsY target) :=
  absFixup_emit_preserves cb 0x99 target h

theorem emitDecAbsX_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitDecAbsX target) :=
  absFixup_emit_preserves cb 0xDE target h

theorem emitIncAbsX_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitIncAbsX target) :=
  absFixup_emit_preserves cb 0xFE target h

theorem emitLdaAbs_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitLdaAbs target) :=
  absFixup_emit_preserves cb 0xAD target h

theorem emitStaAbs_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitStaAbs target) :=
  absFixup_emit_preserves cb 0x8D target h

theorem emitCmpAbsX_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitCmpAbsX target) :=
  absFixup_emit_preserves cb 0xDD target h

theorem emitCmpAbsY_preserves_fixupsInBounds
    (cb : CodeBuilder) (target : String) (h : fixupsInBounds cb) :
    fixupsInBounds (cb.emitCmpAbsY target) :=
  absFixup_emit_preserves cb 0xD9 target h

-- ==========================================================================
-- 5. Loop-fold preservation
-- ==========================================================================

/-- If a per-element step preserves `fixupsInBounds`, then folding over any
    list preserves it. This is the workhorse for reasoning about `for ... do`
    loops in the imperative `Id.run do` body — Lean desugars them to
    `forIn`/`foldlM`, which on `Id` reduces to `List.foldl`. -/
theorem List.foldl_preserves_fixupsInBounds
    {α : Type} (l : List α) (f : CodeBuilder → α → CodeBuilder)
    (hf : ∀ cb x, fixupsInBounds cb → fixupsInBounds (f cb x))
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (l.foldl f cb) := by
  induction l generalizing cb with
  | nil => simpa
  | cons x xs ih =>
    simp [_root_.List.foldl]
    exact ih (f cb x) (hf cb x h)

-- ==========================================================================
-- 6. Sanity check: a tiny imperative `Id.run do` block, threaded
-- ==========================================================================

/-- Toy function: do the same kind of imperative `cb := cb.X; cb := cb.Y`
    chain that real codegen helpers use, but with only a handful of ops.
    If we can thread the invariant through THIS, we can thread it through
    the bigger ones (modulo for-loops, which the foldl lemma covers). -/
private def testThread (cb : CodeBuilder) : CodeBuilder := Id.run do
  let mut cb := cb.label "test_label"
  cb := cb.emitByte 0x00
  cb := cb.emitInst I.rts
  cb := cb.emitJmpLabel .JMP "test_label"
  return cb

/-- Sanity check: a sequence of label / emitByte / emitInst / emitJmpLabel
    preserves `fixupsInBounds`. -/
theorem testThread_preserves (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (testThread cb) := by
  unfold testThread
  simp
  exact
    emitJmpLabel_preserves_fixupsInBounds _ .JMP _
      (emitInst_preserves_fixupsInBounds _ I.rts
        (emitByte_preserves_fixupsInBounds _ 0x00
          (label_preserves_fixupsInBounds _ _ h)))

-- ==========================================================================
-- 7. Threading through real codegen helpers
-- ==========================================================================

-- emitInit was refactored from a 38-mutation `Id.run do` monolith into
-- five named sub-blocks (CodegenV3.emitInitSubtuneClamp,
-- emitInitSubtuneCopy, emitInitSidSilence, emitInitVoiceState,
-- emitInitFrameCounter), each written as a plain `let` chain rather
-- than `Id.run do` + `let mut`. We then prove preservation per
-- sub-block and compose. This is path (a) from the previous attempt's
-- write-up; paths (b) custom meta tactic and (c) crank heartbeats are
-- still on the table for the other long helpers (emitPlay, emitNoteload).
--
-- Two design choices made the proofs fit in default heartbeats:
--
-- (1) The sub-blocks are plain `let` chains, not `Id.run do`. `Id.run`
--     reduction over mutable bindings is a major cost source for `simp`
--     and the unifier; plain `let` lets `unfold` expose the term
--     directly without the `Id` monad in the way.
--
-- (2) The proofs are written as explicit term-level chains, not tactic
--     scripts. A `repeat' (first | apply ... | apply ... | ...)` macro
--     looks tidy but forces Lean to retry up to 13 lemmas at every
--     step, multiplying the unifier's whnf cost. Spelling out the
--     nested `emitFoo_preserves_fixupsInBounds _ _ (emitBar_... _)`
--     chain is wordier but compiles in well under a second.

-- Per-sub-block proofs are written as explicit term-level chains rather
-- than going through the `preserve_fixups` macro. The macro uses
-- `repeat' (first | apply ...)` which forces Lean to retry up to 13
-- preservation lemmas per step; that dispatch cost compounds and hits
-- the whnf heartbeat budget. Explicit term-level proofs avoid the
-- search entirely — Lean just type-checks one nested application.

/-- Preservation through `emitInitSubtuneClamp` (9 ops). -/
theorem emitInitSubtuneClamp_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInitSubtuneClamp cb song) :=
  emitInst_preserves_fixupsInBounds _ I.tay
    (emitInst_preserves_fixupsInBounds _ (I.adc_zp 0xFB)
      (emitInst_preserves_fixupsInBounds _ I.clc
        (emitInst_preserves_fixupsInBounds _ I.asl_a
          (emitInst_preserves_fixupsInBounds _ (I.sta_zp 0xFB)
            (label_preserves_fixupsInBounds _ "subtune_in_range"
              (emitInst_preserves_fixupsInBounds _ (I.lda_imm 0)
                (emitBranch_preserves_fixupsInBounds _ .BCC "subtune_in_range"
                  (emitInst_preserves_fixupsInBounds _
                    (I.cmp_imm song.subtunes.length.toUInt8) h))))))))

/-- Preservation through `emitInitSubtuneCopy` (10 ops). The block
    contains a `BNE subtune_copy` referring to a label that's part of
    this same block — that's fine for the in-bounds invariant, which
    only cares about the fixup's `byteIdx` versus `bytes.size`. -/
theorem emitInitSubtuneCopy_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInitSubtuneCopy cb) :=
  emitBranch_preserves_fixupsInBounds _ .BNE "subtune_copy"
    (emitInst_preserves_fixupsInBounds _ ⟨.CPX, .imm 3⟩
      (emitInst_preserves_fixupsInBounds _ I.inx
        (emitInst_preserves_fixupsInBounds _ I.iny
          (emitStaAbsX_preserves_fixupsInBounds _ "ol_hi"
            (emitLdaAbsY_preserves_fixupsInBounds _ "ol_subtune_hi"
              (emitStaAbsX_preserves_fixupsInBounds _ "ol_lo"
                (emitLdaAbsY_preserves_fixupsInBounds _ "ol_subtune_lo"
                  (label_preserves_fixupsInBounds _ "subtune_copy"
                    (emitInst_preserves_fixupsInBounds _ (I.ldx_imm 0) h)))))))))

/-- Preservation through `emitInitSidSilence` (8 ops, all plain
    instructions — no fixups added by this block). -/
theorem emitInitSidSilence_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInitSidSilence cb) :=
  emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 0x18))
    (emitInst_preserves_fixupsInBounds _ (I.lda_imm 0x0F)
      (emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 18))
        (emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 11))
          (emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 4))
            (emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 11))
              (emitInst_preserves_fixupsInBounds _ (I.sta_abs (SID_BASE + 4))
                (emitInst_preserves_fixupsInBounds _ (I.lda_imm 0x00) h)))))))

/-- Preservation through `emitInitVoiceState` (10 ops: ldx, label, lda,
    five `sta abs,X`, dex, branch BPL). -/
theorem emitInitVoiceState_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInitVoiceState cb) :=
  emitBranch_preserves_fixupsInBounds _ .BPL "init_loop"
    (emitInst_preserves_fixupsInBounds _ I.dex
      (emitStaAbsX_preserves_fixupsInBounds _ "v_patthi"
        (emitStaAbsX_preserves_fixupsInBounds _ "v_pattlo"
          (emitStaAbsX_preserves_fixupsInBounds _ "v_wptr"
            (emitStaAbsX_preserves_fixupsInBounds _ "v_olpos"
              (emitStaAbsX_preserves_fixupsInBounds _ "v_dur"
                (emitInst_preserves_fixupsInBounds _ (I.lda_imm 0x00)
                  (label_preserves_fixupsInBounds _ "init_loop"
                    (emitInst_preserves_fixupsInBounds _ (I.ldx_imm 0x02) h)))))))))

/-- Preservation through `emitInitFrameCounter` (3 ops: lda, sta_zp, rts). -/
theorem emitInitFrameCounter_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInitFrameCounter cb) :=
  emitInst_preserves_fixupsInBounds _ I.rts
    (emitInst_preserves_fixupsInBounds _ (I.sta_zp 0x50)
      (emitInst_preserves_fixupsInBounds _ (I.lda_imm 0xFF) h))

-- ==========================================================================
-- 8. Helper lemmas for dynamic-freq updates (used by emitPlay/emitNoteload)
-- ==========================================================================

/-- `emitDynRefLoad` either emits `LDA #imm` (for the `.constant` case) or
    `LDA abs` with a fixup (for the four address-resolved cases). All
    five cases preserve `fixupsInBounds`. -/
theorem emitDynRefLoad_preserves_fixupsInBounds
    (cb : CodeBuilder) (ref : USFDynRef) (h : fixupsInBounds cb) :
    fixupsInBounds (emitDynRefLoad cb ref) := by
  unfold emitDynRefLoad
  match ref with
  | .constant b   => exact emitInst_preserves_fixupsInBounds _ _ h
  | .scratch v slot => exact emitLdaAbs_preserves_fixupsInBounds _ _ h
  | .voiceCtrl v    => exact emitLdaAbs_preserves_fixupsInBounds _ _ h
  | .voicePitch v   => exact emitLdaAbs_preserves_fixupsInBounds _ _ h
  | .voiceInst v    => exact emitLdaAbs_preserves_fixupsInBounds _ _ h

/-- `emitFreqSlotStore` is just `emitStaAbs` with a label name picked
    from `whichLo`. -/
theorem emitFreqSlotStore_preserves_fixupsInBounds
    (cb : CodeBuilder) (whichLo : Bool) (slot : Nat) (h : fixupsInBounds cb) :
    fixupsInBounds (emitFreqSlotStore cb whichLo slot) :=
  emitStaAbs_preserves_fixupsInBounds _ _ h

/-- `emitDynamicFreqEntry` is a 4-step `let` chain: load lo, store lo,
    load hi, store hi. Composed from the helpers above. -/
theorem emitDynamicFreqEntry_preserves_fixupsInBounds
    (cb : CodeBuilder) (e : USFDynamicFreqEntry) (h : fixupsInBounds cb) :
    fixupsInBounds (emitDynamicFreqEntry cb e) :=
  emitFreqSlotStore_preserves_fixupsInBounds _ false e.freqSlot
    (emitDynRefLoad_preserves_fixupsInBounds _ e.hiSource
      (emitFreqSlotStore_preserves_fixupsInBounds _ true e.freqSlot
        (emitDynRefLoad_preserves_fixupsInBounds _ e.loSource h)))

/-- `emitDynamicEntryIfPhase` either emits the entry or no-ops. -/
theorem emitDynamicEntryIfPhase_preserves_fixupsInBounds
    (phase : USFUpdatePhase) (cb : CodeBuilder) (e : USFDynamicFreqEntry)
    (h : fixupsInBounds cb) :
    fixupsInBounds (emitDynamicEntryIfPhase phase cb e) := by
  unfold emitDynamicEntryIfPhase
  split
  · exact emitDynamicFreqEntry_preserves_fixupsInBounds _ _ h
  · exact h

/-- `emitDynamicUpdatesForPhase` is a `foldl` over the entries list with
    `emitDynamicEntryIfPhase` as the per-element step. -/
theorem emitDynamicUpdatesForPhase_preserves_fixupsInBounds
    (cb : CodeBuilder) (entries : List USFDynamicFreqEntry)
    (phase : USFUpdatePhase) (h : fixupsInBounds cb) :
    fixupsInBounds (emitDynamicUpdatesForPhase cb entries phase) := by
  unfold emitDynamicUpdatesForPhase
  exact List.foldl_preserves_fixupsInBounds entries _
    (fun cb e h => emitDynamicEntryIfPhase_preserves_fixupsInBounds phase cb e h) cb h

-- ==========================================================================
-- 9. emitPlay: header / per-voice loop step / loop / composed
-- ==========================================================================

/-- Header of `emitPlay` (label "play" + INC frame counter at $50). -/
theorem emitPlayHeader_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitPlayHeader cb) :=
  emitInst_preserves_fixupsInBounds _ (I.inc_zp 0x50)
    (label_preserves_fixupsInBounds _ "play" h)

/-- Per-iteration step of the voice loop. Branches on
    `song.voiceOrder[i]?` and on the `isLast` flag, but every reachable
    arm is a chain of preservation-friendly emit ops. -/
theorem emitPlayVoiceStep_preserves_fixupsInBounds
    (song : USFSong) (cb : CodeBuilder) (idxAndLast : Nat × Bool)
    (h : fixupsInBounds cb) :
    fixupsInBounds (emitPlayVoiceStep song cb idxAndLast) := by
  unfold emitPlayVoiceStep
  split
  · exact h
  · split
    · exact emitJmpLabel_preserves_fixupsInBounds _ .JMP _
        (emitInst_preserves_fixupsInBounds _ _
          (emitDynamicUpdatesForPhase_preserves_fixupsInBounds _ _ _ h))
    · exact emitJmpLabel_preserves_fixupsInBounds _ .JSR _
        (emitInst_preserves_fixupsInBounds _ _
          (emitDynamicUpdatesForPhase_preserves_fixupsInBounds _ _ _ h))

/-- Voice loop: foldl over `(List.range nVoices).map` of per-iteration
    steps, each preserving the invariant. -/
theorem emitPlayVoiceLoop_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitPlayVoiceLoop cb song) := by
  unfold emitPlayVoiceLoop
  exact List.foldl_preserves_fixupsInBounds _ _
    (fun cb x h => emitPlayVoiceStep_preserves_fixupsInBounds song cb x h) cb h

/-- The headline result for `emitPlay`: header + atFrameStart updates +
    voice loop. -/
theorem emitPlay_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitPlay cb song) :=
  emitPlayVoiceLoop_preserves_fixupsInBounds _ song
    (emitDynamicUpdatesForPhase_preserves_fixupsInBounds _ _ _
      (emitPlayHeader_preserves_fixupsInBounds _ h))

-- ==========================================================================
-- 10. emitNoteLoadPath helpers: emitFlagRule / emitNoteLoadOp(s) /
--     emitPatternEndOp(s)
-- ==========================================================================

/-- One iteration of the `.addByFlag` rule loop: 7 emit ops + 1 label. -/
theorem emitFlagRule_preserves_fixupsInBounds
    (opIdx : Nat) (doneLabel : String) (cb : CodeBuilder)
    (ruleAndIdx : (USFByte × USFByte × USFByte) × Nat) (h : fixupsInBounds cb) :
    fixupsInBounds (emitFlagRule opIdx doneLabel cb ruleAndIdx) :=
  label_preserves_fixupsInBounds _ _
    (emitJmpLabel_preserves_fixupsInBounds _ .JMP _
      (emitInst_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitBranch_preserves_fixupsInBounds _ .BNE _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _
                (emitInst_preserves_fixupsInBounds _ _ h)))))))

/-- All five `USFNoteLoadOp` constructors preserve the invariant. The
    `.addByFlag` case folds `emitFlagRule` over the indexed rule list. -/
theorem emitNoteLoadOp_preserves_fixupsInBounds
    (cb : CodeBuilder) (op : USFNoteLoadOp) (opIdx : Nat) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNoteLoadOp cb op opIdx) := by
  unfold emitNoteLoadOp
  match op with
  | .addConst slot delta =>
    exact emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitLdaAbsX_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _ h)))
  | .setConst slot value =>
    exact emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _ h)
  | .addByFlag slot rules =>
    exact emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitLdaAbsX_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (label_preserves_fixupsInBounds _ _
              (List.foldl_preserves_fixupsInBounds _ _
                (fun cb r h => emitFlagRule_preserves_fixupsInBounds opIdx _ cb r h)
                _
                (emitInst_preserves_fixupsInBounds _ _
                  (emitInst_preserves_fixupsInBounds _ _ h)))))))
  | .resetIfNextEnds slot =>
    exact label_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitBranch_preserves_fixupsInBounds _ .BNE _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _ h)))))
  | .incIfNextEnds slot delta =>
    exact label_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitLdaAbsX_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitBranch_preserves_fixupsInBounds _ .BNE _
                (emitInst_preserves_fixupsInBounds _ _
                  (emitInst_preserves_fixupsInBounds _ _ h)))))))

/-- `emitNoteLoadOps` is a foldl over the indexed op list. -/
theorem emitNoteLoadOps_preserves_fixupsInBounds
    (cb : CodeBuilder) (ops : List USFNoteLoadOp) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNoteLoadOps cb ops) := by
  unfold emitNoteLoadOps
  exact List.foldl_preserves_fixupsInBounds _ _
    (fun cb opAndIdx h => emitNoteLoadOp_preserves_fixupsInBounds cb opAndIdx.1 opAndIdx.2 h)
    cb h

/-- Both `USFPatternEndOp` constructors preserve the invariant. -/
theorem emitPatternEndOp_preserves_fixupsInBounds
    (cb : CodeBuilder) (op : USFPatternEndOp) (h : fixupsInBounds cb) :
    fixupsInBounds (emitPatternEndOp cb op) := by
  unfold emitPatternEndOp
  match op with
  | .reset slot =>
    exact emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _ h)
  | .increment slot delta =>
    exact emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitLdaAbsX_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _ h)))

/-- `emitPatternEndOps` is already in `foldl` form. -/
theorem emitPatternEndOps_preserves_fixupsInBounds
    (cb : CodeBuilder) (ops : List USFPatternEndOp) (h : fixupsInBounds cb) :
    fixupsInBounds (emitPatternEndOps cb ops) := by
  unfold emitPatternEndOps
  exact List.foldl_preserves_fixupsInBounds _ _
    (fun cb op h => emitPatternEndOp_preserves_fixupsInBounds cb op h) cb h

-- ==========================================================================
-- 11. emitNoteLoadPath sub-blocks (26 of them)
-- ==========================================================================

theorem emitNL_Header_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_Header cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (emitLdaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitLdaAbsX_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (label_preserves_fixupsInBounds _ _ h)))))

theorem emitNL_PtrCheck_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PtrCheck cb) :=
  label_preserves_fixupsInBounds _ _
    (emitJmpLabel_preserves_fixupsInBounds _ .JMP _
      (emitBranch_preserves_fixupsInBounds _ .BNE _
        (emitInst_preserves_fixupsInBounds _ _ h)))

theorem emitNL_ReadPitch_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_ReadPitch cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (label_preserves_fixupsInBounds _ _
      (emitJmpLabel_preserves_fixupsInBounds _ .JMP _
        (emitBranch_preserves_fixupsInBounds _ .BNE _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _ h)))))

theorem emitNL_ReadDurInstPorta_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_ReadDurInstPorta cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _
                (emitInst_preserves_fixupsInBounds _ _
                  (emitInst_preserves_fixupsInBounds _ _
                    (emitInst_preserves_fixupsInBounds _ _ h)))))))))

theorem emitNL_PreAdvanceOps_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PreAdvanceOps cb song) := by
  unfold emitNL_PreAdvanceOps
  exact emitNoteLoadOps_preserves_fixupsInBounds _ _ h

theorem emitNL_ExtractFlags_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_ExtractFlags cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitStaAbsX_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _ h))))))

theorem emitNL_PreserveMask_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PreserveMask cb song) := by
  unfold emitNL_PreserveMask
  split
  · exact emitInst_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _ h))
  · exact h

theorem emitNL_AdvancePtr_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_AdvancePtr cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _
                (emitInst_preserves_fixupsInBounds _ _
                  (emitInst_preserves_fixupsInBounds _ _
                    (emitInst_preserves_fixupsInBounds _ _
                      (emitInst_preserves_fixupsInBounds _ _
                        (emitInst_preserves_fixupsInBounds _ _ h)))))))))))

theorem emitNL_PostAdvanceOps_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PostAdvanceOps cb song) := by
  unfold emitNL_PostAdvanceOps
  exact emitNoteLoadOps_preserves_fixupsInBounds _ _ h

theorem emitNL_DurField_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_DurField cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitStaAbsX_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _ h)))))

theorem emitNL_UpdateVInst_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_UpdateVInst cb) :=
  label_preserves_fixupsInBounds _ _
    (emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (emitBranch_preserves_fixupsInBounds _ .BNE _
          (emitLdaAbsX_preserves_fixupsInBounds _ _
            (emitBranch_preserves_fixupsInBounds _ .BEQ _
              (emitInst_preserves_fixupsInBounds _ _
                (emitInst_preserves_fixupsInBounds _ _ h)))))))

theorem emitNL_ResetAndSidoff_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_ResetAndSidoff cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (emitLdaAbsX_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _ h)))

theorem emitNL_TieCheck_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_TieCheck cb) :=
  emitBranch_preserves_fixupsInBounds _ .BEQ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _ h))

theorem emitNL_FreqWrite_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_FreqWrite cb) := by
  unfold emitNL_FreqWrite
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  exact h

theorem emitNL_PortaInit_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PortaInit cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitLdaAbsX_preserves_fixupsInBounds _ _
                (emitInst_preserves_fixupsInBounds _ _
                  (emitLdaAbsX_preserves_fixupsInBounds _ _ h))))))))

theorem emitNL_RestoreXY_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_RestoreXY cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitLdaAbsX_preserves_fixupsInBounds _ _ h))

theorem emitNL_SavePitchFhi_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_SavePitchFhi cb) :=
  emitStaAbsX_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitLdaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitStaAbsX_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _ h))))))

theorem emitNL_TieSkipLabel_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_TieSkipLabel cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (emitLdaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (label_preserves_fixupsInBounds _ _ h))))

theorem emitNL_CtrlWrite_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_CtrlWrite cb) := by
  unfold emitNL_CtrlWrite
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply label_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitBranch_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  exact h

theorem emitNL_PWADSRWrite_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_PWADSRWrite cb) := by
  unfold emitNL_PWADSRWrite
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  exact h

theorem emitNL_SaveCtrlAndReturn_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_SaveCtrlAndReturn cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (label_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _ h))))

theorem emitNL_AdvanceOrderHeader_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_AdvanceOrderHeader cb song) :=
  emitPatternEndOps_preserves_fixupsInBounds _ _
    (emitInst_preserves_fixupsInBounds _ _
      (label_preserves_fixupsInBounds _ _ h))

theorem emitNL_LookupOL_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_LookupOL cb) := by
  unfold emitNL_LookupOL
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  apply emitInst_preserves_fixupsInBounds
  apply emitLdaAbsX_preserves_fixupsInBounds
  exact h

theorem emitNL_ReadAndDispatch_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_ReadAndDispatch cb) :=
  emitJmpLabel_preserves_fixupsInBounds _ .JMP _
    (emitIncAbsX_preserves_fixupsInBounds _ _
      (emitStaAbsX_preserves_fixupsInBounds _ _
        (emitLdaAbsY_preserves_fixupsInBounds _ _
          (emitStaAbsX_preserves_fixupsInBounds _ _
            (emitLdaAbsY_preserves_fixupsInBounds _ _
              (emitInst_preserves_fixupsInBounds _ _
                (emitBranch_preserves_fixupsInBounds _ .BEQ _
                  (emitInst_preserves_fixupsInBounds _ _
                    (emitInst_preserves_fixupsInBounds _ _ h)))))))))

theorem emitNL_OLEndOrLoop_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_OLEndOrLoop cb) :=
  emitJmpLabel_preserves_fixupsInBounds _ .JMP _
    (emitStaAbsX_preserves_fixupsInBounds _ _
      (emitBranch_preserves_fixupsInBounds _ .BEQ _
        (emitInst_preserves_fixupsInBounds _ _
          (emitInst_preserves_fixupsInBounds _ _
            (emitInst_preserves_fixupsInBounds _ _
              (label_preserves_fixupsInBounds _ _ h))))))

theorem emitNL_SongEnd_preserves_fixupsInBounds
    (cb : CodeBuilder) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNL_SongEnd cb) :=
  emitInst_preserves_fixupsInBounds _ _
    (emitStaAbsX_preserves_fixupsInBounds _ _
      (emitInst_preserves_fixupsInBounds _ _
        (label_preserves_fixupsInBounds _ _ h)))

-- ==========================================================================
-- 12. emitNoteLoadPath: composition of all 26 sub-blocks
-- ==========================================================================

/-- The headline result for `emitNoteLoadPath`. Each `let cb := ...`
    in the body corresponds to one application of a sub-block
    preservation lemma. If any sub-block ever stops preserving
    `fixupsInBounds` — say, because someone adds an emit op that
    doesn't track its fixup correctly — this theorem stops compiling
    and the regression is blocked at `lake build` time. -/
theorem emitNoteLoadPath_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitNoteLoadPath cb song) :=
  emitNL_SongEnd_preserves_fixupsInBounds _
    (emitNL_OLEndOrLoop_preserves_fixupsInBounds _
      (emitNL_ReadAndDispatch_preserves_fixupsInBounds _
        (emitNL_LookupOL_preserves_fixupsInBounds _
          (emitNL_AdvanceOrderHeader_preserves_fixupsInBounds _ song
            (emitNL_SaveCtrlAndReturn_preserves_fixupsInBounds _
              (emitNL_PWADSRWrite_preserves_fixupsInBounds _
                (emitNL_CtrlWrite_preserves_fixupsInBounds _
                  (emitNL_TieSkipLabel_preserves_fixupsInBounds _
                    (emitNL_SavePitchFhi_preserves_fixupsInBounds _
                      (emitNL_RestoreXY_preserves_fixupsInBounds _
                        (emitNL_PortaInit_preserves_fixupsInBounds _
                          (emitNL_FreqWrite_preserves_fixupsInBounds _
                            (emitNL_TieCheck_preserves_fixupsInBounds _
                              (emitNL_ResetAndSidoff_preserves_fixupsInBounds _
                                (emitNL_UpdateVInst_preserves_fixupsInBounds _
                                  (emitNL_DurField_preserves_fixupsInBounds _
                                    (emitNL_PostAdvanceOps_preserves_fixupsInBounds _ song
                                      (emitNL_AdvancePtr_preserves_fixupsInBounds _
                                        (emitNL_PreserveMask_preserves_fixupsInBounds _ song
                                          (emitNL_ExtractFlags_preserves_fixupsInBounds _
                                            (emitNL_PreAdvanceOps_preserves_fixupsInBounds _ song
                                              (emitNL_ReadDurInstPorta_preserves_fixupsInBounds _
                                                (emitNL_ReadPitch_preserves_fixupsInBounds _
                                                  (emitNL_PtrCheck_preserves_fixupsInBounds _
                                                    (emitNL_Header_preserves_fixupsInBounds _ h)))))))))))))))))))))))))

/-- The headline result: `emitInit` preserves `fixupsInBounds`. Composed
    from the five sub-block lemmas above. The proof itself is a
    five-step chain — each `let cb := ...` in `emitInit` corresponds to
    one application of a sub-block preservation lemma.

    What this catches: if a future edit to any `emitInit*` sub-block
    introduces an emit op that records a fixup at a `byteIdx` past the
    end of `bytes`, this theorem stops compiling and the regression is
    blocked at `lake build` time. -/
theorem emitInit_preserves_fixupsInBounds
    (cb : CodeBuilder) (song : USFSong) (h : fixupsInBounds cb) :
    fixupsInBounds (emitInit cb song) := by
  unfold emitInit
  exact
    emitInitFrameCounter_preserves_fixupsInBounds _
      (emitInitVoiceState_preserves_fixupsInBounds _
        (emitInitSidSilence_preserves_fixupsInBounds _
          (emitInitSubtuneCopy_preserves_fixupsInBounds _
            (emitInitSubtuneClamp_preserves_fixupsInBounds _ song
              (label_preserves_fixupsInBounds _ _ h)))))

end PropertiesV3
