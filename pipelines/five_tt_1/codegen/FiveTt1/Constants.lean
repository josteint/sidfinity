/-
Named constants used by FiveTt1.Codegen. Pulled out of Codegen.lean so the
magic numbers have a single source of truth and a short docstring.

Differences from the Commando equivalent are flagged inline.
-/

namespace FiveTt1NS

/-- Base address of the SID chip's write registers. -/
def SID_BASE      : UInt16 := 0xD400

/-- Volume + filter mode register. -/
def SID_VOL       : UInt16 := 0xD418

/-- Per-voice SID register offsets from the voice's base. -/
def SID_V_FREQ_LO : UInt16 := 0
def SID_V_FREQ_HI : UInt16 := 1
def SID_V_PW_LO   : UInt16 := 2
def SID_V_PW_HI   : UInt16 := 3
def SID_V_CTRL    : UInt16 := 4
def SID_V_AD      : UInt16 := 5
def SID_V_SR      : UInt16 := 6

/-- Frame counter, zero page. -/
def ZP_FRAME_CTR  : UInt8  := 0x50

/-- Hard-restart threshold. FiveTt1 uses 1 (vs Commando's 2) because FiveTt1
    fires HR exactly 2 frames before note-load, where Commando fires 3.
    The difference is engine-internal timing of when `v_dur` is decremented
    relative to the rest of the play loop. -/
def HR_THRESHOLD  : UInt8  := 1

/-- Hubbard's PW direction-flip bounds for bidirectional PWM. HARDCODED
    in the original `pulsework` routine (cmp #$08 / cmp #$0E), NOT
    per-instrument. -/
def PW_BIDIR_MIN  : UInt8  := 0x08
def PW_BIDIR_MAX  : UInt8  := 0x0E

end FiveTt1NS
