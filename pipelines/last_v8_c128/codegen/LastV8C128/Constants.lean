/-
  Constants used by the Last V8 (C128) tombstone codegen.

  The original Last V8 engine fixes:
    * load address           $4800
    * init                   $7F40
    * play                   $0000  (RSID — play is IRQ-driven)
    * IRQ handler            $7F73  (installed at $0314/$0315)
    * relocator copies       $7B40..$7F3F  →  $C000..$C3FF

  See `docs/hubbard_last_v8_c128_disassembly.s` for the full layout.
-/

namespace LastV8C128NS

/-- SID chip base register. -/
def SID_BASE     : UInt16 := 0xD400

/-- SID master-volume register. -/
def SID_VOL      : UInt16 := 0xD418

/-- Original SID's PSID metadata (used by the tombstone). -/
def ORIG_LOAD    : UInt16 := 0x4800
def ORIG_INIT    : UInt16 := 0x7F40
def ORIG_PLAY    : UInt16 := 0x0000   -- RSID

end LastV8C128NS
