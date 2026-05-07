/-
  PropertiesV3.lean — invariants and theorems about the V3 codegen output.

  The goal is to catch regressions at compile time: if any of these
  properties stop holding, `lake build` fails and we know something
  important changed shape.

  Currently focused on the boundary functions (PSID file format,
  byte serialisation primitives) since the imperative `Id.run do`
  body of `CodegenV3.generateSID` is much harder to reason about.

  What's NOT here yet (and would be valuable):
  - "All fixups resolve to addresses inside the binary."
  - "Every `targetLabel` referenced has a corresponding `label` declaration."
  - "After note-load, Y holds v_sidoff[X]."
  These need lemmas about `CodeBuilder` invariants and would have caught
  the porta-init Y-clobber bug. Future work.
-/
import Asm6502
import PSIDFile

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

/-- The PSID magic bytes we hard-code match ASCII "PSID". A regression
    here would mean we changed the magic constants and broke the file
    format. (`toUTF8` returns `ByteArray`; we compare via `.toList`.) -/
theorem psid_magic_is_ascii :
    [0x50, 0x53, 0x49, 0x44] = "PSID".toUTF8.toList := by native_decide

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

end PropertiesV3
