/-
  PropertiesV3.lean — invariants and theorems about the V3 codegen output.

  Goal: catch regressions at compile time. If any of these properties stop
  holding, `lake build` fails and we know something important changed shape.

  Three layers:
  1. Boundary serialisation primitives (sizes, endianness, magic bytes).
  2. PSID file structure (header is always prepended).
  3. CodeBuilder invariants (fixups stay in-bounds across emit ops).

  Layer 3 is the one that *would* catch a real codegen regression: if some
  new emit function fails to grow `bytes` enough to hold its fixup target,
  the invariant breaks at compile time rather than producing a corrupt SID
  at run time.

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
import Asm6502
import PSIDFile
import CodegenV3

open V3

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

end PropertiesV3
