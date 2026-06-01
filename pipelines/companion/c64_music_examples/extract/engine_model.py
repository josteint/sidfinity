"""Python emulator for the C64 Music Examples Family A engine.

Family A is the engine used by 14 of 15 subtunes (all except sub 1).
Same engine logic instantiated at 4 different addresses with different
state regions:

  - sub 0  → handler $0903, state $0A6E, init template $10C7
  - sub 2  → handler $1D8B, state $1F00+, init template ?
  - sub 3  → handler $2A23, state $2B80+, init template ?
  - sub 4-14 → handler $33DB (shared), state $35C0+, per-subtune
              dataset selected via 5-byte stubs at $38A0..$4224

This module focuses on **sub 0** as the simplest isolated instance.
The engine model can be parameterized per-instance later.

Engine semantics (sub 0 reference):

  state $0A6E-$0A8D (32 bytes, init from $10C7):
    +0    V1 control/timbre byte (init: $01)
    +1    V1 freq lo (init: $00)
    +2    V1 freq hi (init: $00)
    +3    V2 phase (init: $08) — bit 7 = "voice silent"
    +4    V2 timbre (init: $10)
    +5    V2 freq lo (init: $5C)
    +6    V2 freq hi (init: $3A)
    +7    [unused] (init: $00)
    ...   (more per-voice state — to be mapped)
    +21   tempo                 (sub 0: $06)
    +22   alt-tempo             (sub 0: $0A)
    +23   frame_ctr             (sub 0: starts at $09)
    +24/25 V1 pattern_ptr       (sub 0: $0C5F)
    +26/27 V2 pattern_ptr       (sub 0: $0DA3)
    +28/29 V3 pattern_ptr       (sub 0: $0F84)
    +30   V1 running_ctr        (sub 0: $A2)
    +31   V2 running_ctr        (sub 0: $C7)

  Play loop ($0903) — VERIFIED by py65 trace:
    1. PWM tick for each voice if its phase byte ($0A7C for V1,
       $0A6E for V2) matches the per-voice running ctr ($0A8C/$0A8D).
       PWM tick = JSR $0AB6 (sweeps $0A71+X between 2 and 14, writes
       $D403+X).
    2. INC frame_ctr ($0A85)
    3. dispatch:
       - frame_ctr == tempo ($0A83, sub 0 = $06): JMP $09D6 → tick each
         voice via $09CD (writes only voices with bit 7 set in $0A6F+X),
         then JMP $0AF3 (vibrato)
       - frame_ctr == alt-tempo ($0A84, sub 0 = $0A): reset frame_ctr to
         0, advance all 3 voices via JSR $0A22 / $0A31 / $0A40 (voice
         event router $0954 processes one pattern byte per voice)
       - otherwise: JMP $0AF3 → vibrato only

  With sub 0 starting frame_ctr=$09: play #1 hits $0A (alt-tempo) →
  full voice advance + reset; plays #2..6 each increment to $01..$06;
  play #6 hits $06 (tempo) → loop reset path. So the actual cadence is
  6-frame loop: 1 full-tick + 4 vibrato + 1 loop-reset. Notes from
  patterns advance every 6 frames.

  Voice tick ($09D6 → $09CD per voice, X = 0/7/14):
    Reads byte at zp ptr ($1C/$1D for V1, $1E/$1F for V2, $20/$21 for V3),
    increments ptr, JMPs to $0954 (voice event router).

  Voice event router ($0954):
    - byte < $09:         duration ×16 → state, fall through to next byte
    - byte == $0F:        ??? (end-of-pattern marker?)
    - byte $0C/$0D/$0E:   control events
      - $0C: write timbre $0A72,X to $D404,X (control register)
      - $0D: JSR $09BE (= $0C subroutine)
      - $0E: ??? (per-voice)
    - byte ≥ $80:         "note with extended flag" — mask off bit 7,
                          play note via freq tables ($0B5F lo, $0BDF hi),
                          write to $D400+X / $D401+X, update timbre.
    - byte $09-$7F:       bare note — same play-note path, but ALSO
                          stores note number to $0B5A for V1 vibrato.

  Vibrato ($0AF3, runs every play frame for V1):
    - Read $A2 (frame ctr) & $07 → triangle wave pos (0..7, folded
      at 4 to be 0,1,2,3,3,2,1,0)
    - Take note from $0B5A (current V1 note, set by note-play path)
    - Compute interpolation step: (freq[note+1] - freq[note]) >> 4
    - Multiply step × triangle_pos, add to base freq → write $D400/$D401

  PWM sweep ($0AB6, X = 0/7/14):
    - State $0ADE+X: signed counter direction
    - $0A71+X: per-voice PW value
    - Ramps PW between 2 and 14, writes to $D403+X (PW hi)

  Init ($0A8E):
    - Copy 32 bytes from $10C7 → $0A6E (state)
    - JSR $09F8 (sets up zp ptrs $1C/$1E/$20 from state ptrs)
    - LDA #$0F; STA $D418 (master vol)
    - LDX #$14; copy $0A6E,X → $D400,X for X=$14 down to 0
      (dumps initial timbres to SID, in reverse register order)

Open work for next session:
  - Map remaining state bytes (+3..+20) by tracing each handler use.
    Tentative: $0A6F-$0A71 = per-voice "current pattern command" state,
    $0A72-$0A74 = per-voice timbre byte (control reg value).
  - Verify $09D6 (tempo-match loop reset) — does it actually loop the
    song, or is it dead code in sub 0?
  - Decode pattern bytes per voice (V2 starts $50 $D0 $08 $E0 $01 $D3
    $D2 $D3...). The byte semantics per $0954 event router:
      < $09 → duration*16 stored to $0A72+X (per-voice "rate"?), fall
              through to next byte (recursion)
      $0C   → STA $0A72+X to $D404+X (timbre write, no freq update)
      $0D   → JSR $09BE (same as $0C)
      $0E   → JSR $0A01 + JMP $0A22 (V1) / JSR $0A0C + JMP $0A40 (V3) /
              JSR $0A17 + JMP $0A31 (V2): reloads zp ptr from state
              (pattern loop?)
      $0F   → RTS (skip frame)
      bare note (≥$09, <$80): freq lookup + write, ALSO stores Y → $0B5A
              (sets V1 vibrato base note — only when X=0, i.e. V1)
      note with bit 7 set: AND #$7F, freq lookup + write WITHOUT storing
              $0B5A (so the note plays but vibrato continues on prior note)
  - Build event-by-event emulator that produces same writes as orig
  - Verify against writelog_capture(sid, 0)
  - Start the USF schema for sub 0 (per-voice pattern + tempo +
    init_timbre + init_current_note for V1 vibrato)

Reference: pipelines/companion/c64_music_examples/RE_NOTES.md
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


# Sub 0 Family A engine constants (verified by py65 trace + disassembly).
SUB0_HANDLER_ADDR = 0x0903
SUB0_STATE_ADDR = 0x0A6E
SUB0_STATE_SIZE = 32
SUB0_INIT_TEMPLATE_ADDR = 0x10C7

# Pattern data (sub 0 — initialized from state +24..+29)
SUB0_V1_PATTERN_ADDR = 0x0C5F
SUB0_V2_PATTERN_ADDR = 0x0DA3
SUB0_V3_PATTERN_ADDR = 0x0F84

# Freq tables — shared across all Family A instances (single copy in binary)
FAMILY_A_FREQ_LO_ADDR = 0x0B5F
FAMILY_A_FREQ_HI_ADDR = 0x0BDF
FAMILY_A_FREQ_TABLE_SIZE = 128

# Vibrato current-note byte (sub 0; physically at $0B5A)
SUB0_CURRENT_NOTE_ADDR = 0x0B5A

# Per-voice X offsets used by engine (V1, V2, V3)
VOICE_X_OFFSETS = (0, 7, 14)

PSID_HEADER_SIZE = 124


@dataclass
class Sub0State:
    """In-progress: sub 0's runtime state. Field names tentative until
    the engine model is verified against writelog_capture."""
    state_bytes: bytes  # 32 bytes from $0A6E
    v1_pattern_ptr: int
    v2_pattern_ptr: int
    v3_pattern_ptr: int
    tempo: int
    alt_tempo: int
    frame_ctr: int
    current_note: int  # $0B5A; initial value from binary
    memory: bytearray   # full 64KB image for now (py65 fallback)


def _run_init_via_py65(sid_path: str, subtune: int = 0
                       ) -> tuple[bytearray, list[tuple[int, int]]]:
    """Run init in py65, return (post-init memory, captured SID writes).

    Uses the same RTS-sentinel exit pattern as clever_music's _run_init."""
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU

    raw = Path(sid_path).read_bytes()
    load_in = struct.unpack('>H', raw[8:10])[0]
    init_addr = struct.unpack('>H', raw[10:12])[0]
    body = raw[PSID_HEADER_SIZE:]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in

    sid_writes: list[tuple[int, int]] = []

    class _TrackingMem(bytearray):
        def __setitem__(self, idx, val):
            if isinstance(idx, int) and 0xD400 <= idx <= 0xD418:
                sid_writes.append((idx - 0xD400, val))
            super().__setitem__(idx, val)

    mpu = MPU()
    mpu.memory = _TrackingMem(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.a = subtune
    mpu.x = 0; mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    for _ in range(200000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    return bytearray(mpu.memory), sid_writes


def load_sub0_state(sid_path: str) -> Sub0State:
    """Load sub 0's engine state from a freshly-init'd SID. Note: this
    is a snapshot reader, NOT an extractor — building the proper
    extractor (state → USF) is the next session's work."""
    mem, _ = _run_init_via_py65(sid_path, 0)
    state_bytes = bytes(mem[SUB0_STATE_ADDR:SUB0_STATE_ADDR + SUB0_STATE_SIZE])
    return Sub0State(
        state_bytes=state_bytes,
        v1_pattern_ptr=state_bytes[24] | (state_bytes[25] << 8),
        v2_pattern_ptr=state_bytes[26] | (state_bytes[27] << 8),
        v3_pattern_ptr=state_bytes[28] | (state_bytes[29] << 8),
        tempo=state_bytes[21],
        alt_tempo=state_bytes[22],
        frame_ctr=state_bytes[23],
        current_note=mem[SUB0_CURRENT_NOTE_ADDR],
        memory=mem,
    )


if __name__ == '__main__':
    sid = 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'
    s = load_sub0_state(sid)
    print(f"Sub 0 state:")
    print(f"  tempo={s.tempo} alt_tempo={s.alt_tempo} frame_ctr={s.frame_ctr}")
    print(f"  V1 ptr=${s.v1_pattern_ptr:04X} V2=${s.v2_pattern_ptr:04X} V3=${s.v3_pattern_ptr:04X}")
    print(f"  current_note=${s.current_note:02X} (initial vibrato note)")
    print(f"  state bytes: {' '.join(f'{b:02X}' for b in s.state_bytes)}")
