/-
  Properties.lean — invariants of the tombstone codegen.

  Mirrors the role of Properties.lean in sibling pipelines but limited
  to what the tombstone actually guarantees today. Add real invariants
  here when the codegen grows beyond an RTS.
-/

import LastV8C128.Codegen
import LastV8C128.SongData

namespace LastV8C128NS

/-- The tombstone payload is exactly one byte. -/
theorem tombstone_payload_size : tombstonePayload.size = 1 := rfl

/-- The tombstone payload is `RTS` ($60). -/
theorem tombstone_payload_is_rts : tombstonePayload.get! 0 = 0x60 := rfl

end LastV8C128NS
