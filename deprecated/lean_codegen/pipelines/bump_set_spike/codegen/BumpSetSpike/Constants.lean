/-
Named constants used by BumpSetSpike.Codegen. Pulled out of Codegen.lean so the
magic numbers have a single source of truth and a short docstring.
-/

namespace V3

/-- Base address of the SID chip's write registers. -/
def SID_BASE      : UInt16 := 0xD400

/-- Volume + filter mode register: SID_BASE + $18 (= max volume / unfiltered). -/
def SID_VOL       : UInt16 := 0xD418

/-- Per-voice SID register offsets from the voice's base
    (V1 base = SID_BASE, V2 base = SID_BASE + 7, V3 base = SID_BASE + 14). -/
def SID_V_FREQ_LO : UInt16 := 0
def SID_V_FREQ_HI : UInt16 := 1
def SID_V_PW_LO   : UInt16 := 2
def SID_V_PW_HI   : UInt16 := 3
def SID_V_CTRL    : UInt16 := 4
def SID_V_AD      : UInt16 := 5
def SID_V_SR      : UInt16 := 6

/-- Frame counter, zero page. Incremented at the top of `play`.
    Read by vibrato (LFO phase) and arpeggio (octave alternation). -/
def ZP_FRAME_CTR  : UInt8  := 0x50

/-- Hard-restart threshold. The gate-off / AD=0 / SR=0 write fires when
    `v_dur == HR_THRESHOLD` for the current voice. -/
def HR_THRESHOLD  : UInt8  := 2  -- BumpSetSpike-tuned (= 3 frames before note-load)

end V3
