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


# =====================================================================
# Event-by-event emulator — produces the same (reg, val) SID writes as
# the original engine for sub 0. Used to validate our understanding
# before designing the USF schema.
# =====================================================================


class Sub0Emulator:
    """Frame-by-frame pure-Python emulator for sub 0's Family A engine.

    Holds state read from py65-init'd memory (engine state + pattern
    bytes + freq tables) and steps one play frame at a time, returning
    the SID writes that play frame would emit.

    Implementation tracks per-voice state mirroring the engine's
    in-memory layout: $0A6E (V2 phase), $0A6F+X (per-voice last-cmd
    flag, bit 7 = sustained), $0A71+X (PW value), $0A72+X (timbre nybble),
    $0A8C/$0A8D (per-voice running ctr), $0A85 (frame ctr), and the
    three zp pattern pointers ($1C/$1E/$20).
    """

    # Per-voice X offsets used by the engine (V1=0, V2=7, V3=14).
    X_V1, X_V2, X_V3 = 0, 7, 14

    def __init__(self, sid_path: str):
        mem, _ = _run_init_via_py65(sid_path, 0)
        self.mem = mem  # 64KB after init — used for freq tables + pattern data reads
        self.frame_ctr = mem[0x0A85]
        self.tempo = mem[0x0A83]
        self.alt_tempo = mem[0x0A84]
        self.current_note = mem[0x0B5A]  # V1 vibrato base
        self.frame_index = 0             # play call counter ($086E)
        # ZP pattern pointers (initialized by $09F8 during engine init)
        self.zp_ptrs = {
            self.X_V1: (mem[0x1C], mem[0x1D]),
            self.X_V2: (mem[0x1E], mem[0x1F]),
            self.X_V3: (mem[0x20], mem[0x21]),
        }
        # Per-voice state. Index by X (0/7/14).
        self.last_cmd = {x: 0 for x in (0, 7, 14)}      # $0A6F+X
        self.timbre = {x: 0 for x in (0, 7, 14)}        # $0A72+X (nybble << 4)
        for x in (0, 7, 14):
            self.last_cmd[x] = mem[0x0A6F + x]
            self.timbre[x] = mem[0x0A72 + x]
        # PWM state. Sweep only V1 (X=0) and V3 (X=$0E). Each tracks
        # phase target ($0A6E/$0A7C), running ctr ($0A8D/$0A8C),
        # current PW ($0A71+X), and sign byte ($0ADE+X — starts $00).
        self.pwm_phase_v1 = mem[0x0A6E]
        self.pwm_phase_v3 = mem[0x0A7C]
        self.pwm_ctr_v1 = mem[0x0A8D]
        self.pwm_ctr_v3 = mem[0x0A8C]
        self.pwm_pw = {self.X_V1: mem[0x0A71], self.X_V3: mem[0x0A7F]}
        self.pwm_sign = {self.X_V1: mem[0x0ADE], self.X_V3: mem[0x0AEC]}

    def _read_pattern_byte(self, x: int) -> int:
        """Read byte at the voice's zp pattern ptr; advance ptr by 1."""
        lo, hi = self.zp_ptrs[x]
        addr = lo | (hi << 8)
        b = self.mem[addr]
        addr = (addr + 1) & 0xFFFF
        self.zp_ptrs[x] = (addr & 0xFF, (addr >> 8) & 0xFF)
        return b

    def _voice_event(self, x: int, byte: int,
                     writes: list[tuple[int, int]]) -> bool:
        """Process one pattern byte for voice X. Returns True if a
        new byte should be read (recursion case for < $09)."""
        self.last_cmd[x] = byte
        if byte < 0x09:
            # Duration-set: store (byte * 16) as timbre, recurse.
            self.timbre[x] = (byte << 4) & 0xFF
            return True
        if byte == 0x0F:
            # End-of-pattern marker — no writes, no recurse.
            return False

        if byte >= 0x80:
            y = byte & 0x7F
            # Hit the $099C path — check $0E/$0C/$0D specially.
            if y == 0x0E:
                # Pattern loop: reload zp ptr from state ($0A86/87 for V1,
                # $0A88/89 V2, $0A8A/8B V3) and recurse.
                if x == self.X_V1:
                    self.zp_ptrs[x] = (self.mem[0x0A86], self.mem[0x0A87])
                elif x == self.X_V2:
                    self.zp_ptrs[x] = (self.mem[0x0A88], self.mem[0x0A89])
                else:
                    self.zp_ptrs[x] = (self.mem[0x0A8A], self.mem[0x0A8B])
                return True
            if y == 0x0C:
                # Just write timbre to $D404+X — no freq update.
                writes.append((0x04 + x, self.timbre[x]))
                return False
            if y == 0x0D:
                # Same as $0C — timbre write + return.
                writes.append((0x04 + x, self.timbre[x]))
                return False
            # Note play (with bit 7 → still stored as note; bit 7 controls
            # the "sustained" flag in last_cmd which the loop-reset path
            # reads later).
            note = y
        else:
            note = byte

        # Bare-note path: store note as V1 vibrato base (V1 only), play note.
        if x == self.X_V1:
            self.current_note = note
        freq_lo = self.mem[FAMILY_A_FREQ_LO_ADDR + note]
        freq_hi = self.mem[FAMILY_A_FREQ_HI_ADDR + note]
        # NB: engine writes go to $D401,X (= reg 0x01+x) THEN $D400,X.
        # The values stored: A=$0B5F[Y]=freq_lo → STA $D401,X.
        # That looks BACKWARDS — actually $0B5F is the freq HIGH table
        # per the engine layout, despite the symbol name. The voice
        # event router writes freq HIGH to reg+1 then freq LOW to reg+0
        # (which matches SID's reg+0=lo / reg+1=hi convention if the
        # table at $0B5F is freq lo and $0BDF is freq hi after all).
        # Verify empirically below.
        writes.append((0x01 + x, freq_lo))
        writes.append((0x00 + x, freq_hi))
        # Control reg: timbre + 1 (the engine does `LDY $0A72,X; INY; TYA`)
        writes.append((0x04 + x, (self.timbre[x] + 1) & 0xFF))
        return False

    def _advance_voice(self, x: int, writes: list[tuple[int, int]]) -> None:
        """Read pattern bytes for voice X until a non-recurse case."""
        while True:
            b = self._read_pattern_byte(x)
            if not self._voice_event(x, b, writes):
                return

    def _vibrato(self, writes: list[tuple[int, int]]) -> None:
        """Reproduce $0AF3: V1 freq sweep based on (frame_index & 7)
        folded as a triangle, multiplied by (freq[note+1]-freq[note])/16."""
        # $0AF3-$0AFD: triangle position
        a = self.frame_index & 0x07
        if a >= 4:
            a = a ^ 7  # EOR #$07: 4→3, 5→2, 6→1, 7→0
        tri_pos = a
        note = self.current_note
        # Step = (freq[note+1] - freq[note]) >> 4, signed-extending across
        # both bytes (see ASM: SBC + LSR/ROR sequence). Build as 16-bit
        # signed delta of the freq, then shift right 4.
        f0_lo = self.mem[FAMILY_A_FREQ_HI_ADDR + note]
        f0_hi = self.mem[FAMILY_A_FREQ_LO_ADDR + note]
        f1_lo = self.mem[FAMILY_A_FREQ_HI_ADDR + note + 1]
        f1_hi = self.mem[FAMILY_A_FREQ_LO_ADDR + note + 1]
        # NB: the engine's freq tables map confusingly — $0B5F seems to
        # be freq HIGH and $0BDF freq LOW (need to confirm with writes).
        # For the sweep math we use the 16-bit freq value as
        # (hi<<8)|lo with the engine's labeling.
        f0 = (f0_hi << 8) | f0_lo
        f1 = (f1_hi << 8) | f1_lo
        if f1 == 0:
            # Engine's BEQ $0B56 escape — exit without writing.
            return
        step = ((f1 - f0) & 0xFFFF) >> 4  # logical shift right 4
        # base = f0; sweep value = base + step * tri_pos
        sweep = (f0 + step * tri_pos) & 0xFFFF
        writes.append((0x00, sweep & 0xFF))         # $D400 = V1 freq lo
        writes.append((0x01, (sweep >> 8) & 0xFF))  # $D401 = V1 freq hi

    def _pwm_tick(self, x: int, writes: list[tuple[int, int]]) -> None:
        """Per-voice PWM sweep ($0AB6). Ramps PW between 2 and 14,
        flipping direction via sign-byte tracking, writes $D403+X."""
        sign = self.pwm_sign[x]
        if sign & 0x80:
            # Ascending phase: PW++.
            pw = (self.pwm_pw[x] + 1) & 0xFF
            self.pwm_pw[x] = pw
            if pw == 0x0E:
                self.pwm_sign[x] = (sign + 1) & 0xFF
            a = pw
        else:
            # Descending phase: PW--.
            pw = (self.pwm_pw[x] - 1) & 0xFF
            self.pwm_pw[x] = pw
            if pw == 0x02:
                self.pwm_sign[x] = (sign - 1) & 0xFF
            a = pw
        writes.append((0x03 + x, a))   # STA $D403,X

    def play_frame(self) -> list[tuple[int, int]]:
        """Run one engine play-call. Returns list of (reg, val) SID writes
        in the order the engine emits them."""
        writes: list[tuple[int, int]] = []

        # PWM ticks: V3 first (LDX #$0E), then V1 (LDX #$00) per $0903 order.
        # Each only fires if (phase-byte BPL-not-set) AND (++ctr == phase).
        # V3 path checks $0A7C; V1 path checks $0A6E.
        if not (self.pwm_phase_v3 & 0x80):
            self.pwm_ctr_v3 = (self.pwm_ctr_v3 + 1) & 0xFF
            if self.pwm_ctr_v3 == self.pwm_phase_v3:
                self._pwm_tick(self.X_V3, writes)
                self.pwm_ctr_v3 = 0
        if not (self.pwm_phase_v1 & 0x80):
            self.pwm_ctr_v1 = (self.pwm_ctr_v1 + 1) & 0xFF
            if self.pwm_ctr_v1 == self.pwm_phase_v1:
                self._pwm_tick(self.X_V1, writes)
                self.pwm_ctr_v1 = 0

        self.frame_ctr = (self.frame_ctr + 1) & 0xFF
        if self.frame_ctr == self.tempo:
            # Loop-reset path: per-voice, if last_cmd bit 7 set → timbre write
            for x in (self.X_V1, self.X_V2, self.X_V3):
                if self.last_cmd[x] & 0x80:
                    writes.append((0x04 + x, self.timbre[x]))
            self._vibrato(writes)
        elif self.frame_ctr == self.alt_tempo:
            # Full voice tick: reset frame_ctr, advance each voice.
            self.frame_ctr = 0
            for x in (self.X_V1, self.X_V2, self.X_V3):
                self._advance_voice(x, writes)
            # Note: $09D6's tempo-match path JMPs to vibrato AFTER tick.
            # But the alt-tempo (full advance) path DOES NOT — it just
            # does the voice advances and exits. Verify with writelog.
        else:
            # Vibrato only.
            self._vibrato(writes)

        self.frame_index = (self.frame_index + 1) & 0xFF
        return writes


if __name__ == '__main__':
    sid = 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'
    s = load_sub0_state(sid)
    print(f"Sub 0 state:")
    print(f"  tempo={s.tempo} alt_tempo={s.alt_tempo} frame_ctr={s.frame_ctr}")
    print(f"  V1 ptr=${s.v1_pattern_ptr:04X} V2=${s.v2_pattern_ptr:04X} V3=${s.v3_pattern_ptr:04X}")
    print(f"  current_note=${s.current_note:02X} (initial vibrato note)")
    print(f"  state bytes: {' '.join(f'{b:02X}' for b in s.state_bytes)}")

    # Verify emulator against orig writelog
    print(f"\nEmulator verification (sub 0, first 10 play frames):")
    em = Sub0Emulator(sid)
    for f in range(10):
        writes = em.play_frame()
        print(f"  play #{f+1:2d}: {len(writes)} writes: " +
              ' '.join(f'${r:02X}=${v:02X}' for r, v in writes[:8]))
