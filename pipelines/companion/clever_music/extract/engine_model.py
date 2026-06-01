"""Python emulator for the Clever Music Companion engine.

Used by Graham Jarvis & Rob Hartshorn — Fairlight, Gyroscope (and
likely other Clever Music titles). The engine is significantly more
sophisticated than Bowden-canonical: per-voice duration counters,
embedded commands ($Bx tempo / $Cx vol / $Dx instrument / $Ex pattern
jump), and a song-position synchronisation mechanism.

Engine layout (from disasm of Fairlight, init at $C367, play at $C03A):

  $C1C0   tempo (global, frames per tick)
  $C1C1   tempo_ctr (runtime)
  $C1C3   song_pos counter — starts at $E0, advances on each $Ex hit
  $C1C7   instrument table (16 × 5 bytes: pw_lo, pw_hi, ctrl, ad, sr)
  $C217+X V_pattern_pointer (16-bit; X = 0/7/14 voice offset)
  $C219+X V_timbre (5 bytes — copied from inst_table[idx*5..])
  $C21B+X V_ctrl (just timbre[+2])
  $C22C+v V_duration_counter (v = 0/1/2 voice index)
  $C22F   song dispatch table (16-bit pattern pointers, indexed by
          low nibble of the $Ex command)
  $C250   freq_hi table (128 bytes)
  $C2D0   freq_lo table (128 bytes)

Engine semantics:

  play() — every CIA fire:
    tempo_ctr++; if != tempo, return early
    reset tempo_ctr
    for each voice (V1, V2, V3):
      if duration_ctr == 1: JSR load_note   # consume pattern bytes
      else:                  duration_ctr--

  load_note(X = voice offset) — recursive:
    byte = pattern[pattern_ptr]; pattern_ptr++
    cases:
      $00..$7F: NORMAL_NOTE   — write freq, 5-byte timbre, gated ctrl
      $80     : REST           — write ctrl (gate off)
      $81     : SKIP           — RTS, no writes
      $82 D   : SET_DURATION   — write ctrl (gate off), duration_ctr=D,
                                 RTS (consumes 2 bytes, takes 1 tick)
      $B0-$BF : SET_TEMPO      — tempo = low nibble, recurse
      $C0-$CF : SET_MASTER_VOL — D418 = low nibble, recurse
      $D0-$DF : SET_INSTRUMENT — timbre = inst_table[(low&$0F)*5..]+5,
                                 recurse
      $Ex (when ==song_pos):     PATTERN_JUMP — pattern_ptr =
                                 song_table[low_nibble*2..+2],
                                 advance song_pos (wrap $E5→$E0),
                                 recurse
      Other bit-7-set         : SKIP_BYTE — recurse (no SID writes,
                                 no tick consumed)

  Only NORMAL_NOTE, REST, SKIP, and SET_DURATION consume a tick.
  Everything else recurses to read the next pattern byte.

  load_note's NORMAL_NOTE path emits 5-byte timbre + gated ctrl in
  the same junk-write-then-gated-write order as the Bowden engine,
  retriggering the envelope on every note.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


# Engine memory map (relative to load base $C000 for known Clever Music SIDs).
TEMPO_ADDR = 0xC1C0
TEMPO_CTR_ADDR = 0xC1C1
SONG_POS_ADDR = 0xC1C3
INST_TABLE_ADDR = 0xC1C7
SONG_TABLE_ADDR = 0xC22F
FREQ_HI_ADDR = 0xC250
FREQ_LO_ADDR = 0xC2D0
PER_VOICE_BASE = 0xC217        # +0/+7/+14 per voice
DUR_CTR_BASE = 0xC22C          # +0/+1/+2 per voice (note: stride 1!)

PSID_HEADER_SIZE = 124


@dataclass
class EngineState:
    """Mutable runtime state during emulation. Captures the engine's
    full per-voice + global state across a play() call."""
    tempo: int
    tempo_ctr: int
    song_pos: int                              # 0..15 (low nibble)
    pattern_ptr: list[int]                     # 3 × 16-bit
    timbre: list[bytearray]                    # 3 × 5 bytes
    duration_ctr: list[int]                    # 3 × 1 byte
    # Per-tune constants (not modified during play)
    memory: bytearray = field(repr=False)      # full 64KB image
    inst_table: bytes = b''                    # 16 × 5 = 80 bytes
    song_table: bytes = b''                    # N × 2 bytes
    freq_hi: bytes = b''                       # 128 bytes
    freq_lo: bytes = b''                       # 128 bytes


class _TrackingMem(bytearray):
    """bytearray subclass that records SID and CIA1 writes during init.

    Used so we can replay init's exact SID write sequence in the rebuild
    rather than hardcoding a Bowden-canonical-style assumption.
    """
    sid_writes: list  # type: ignore
    cia_writes: dict  # type: ignore

    def __new__(cls, size):
        obj = super().__new__(cls, size)
        obj.sid_writes = []
        obj.cia_writes = {}
        return obj

    def __setitem__(self, idx, val):
        if isinstance(idx, int):
            if 0xD400 <= idx <= 0xD418:
                self.sid_writes.append((idx - 0xD400, val))
            elif 0xDC00 <= idx <= 0xDDFF:
                self.cia_writes[idx] = val
        super().__setitem__(idx, val)


def _run_init(sid_path: str, subtune: int = 0
              ) -> tuple[bytearray, list[tuple[int, int]], dict]:
    """Load SID + run init in py65, return (post-init memory, sid_writes,
    cia_writes)."""
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    load_in = struct.unpack('>H', raw[8:10])[0]
    body = raw[PSID_HEADER_SIZE:]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    init_addr = struct.unpack('>H', raw[10:12])[0]
    mpu = MPU()
    mpu.memory = _TrackingMem(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.a = subtune
    mpu.x = 0
    mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    # Stop when init's RTS pops the sentinel return address $FEFE → PC=$FEFF.
    # We can't gate on `PC inside SID load range`: BTTF (and likely other
    # banking-trampoline variants) JMP into relocated init code OUTSIDE the
    # load range; that relocated code does the real per-voice state setup.
    for _ in range(200000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    return (bytearray(mpu.memory),
            list(mpu.memory.sid_writes),
            dict(mpu.memory.cia_writes))


def load_state_from_sid(sid_path: str, subtune: int = 0) -> EngineState:
    """Read engine state from a Clever Music SID."""
    mem, _, _ = _run_init(sid_path, subtune)

    pattern_ptr = []
    timbre = []
    duration_ctr = []
    for v, off in enumerate((0, 7, 14)):
        lo = mem[PER_VOICE_BASE + off]
        hi = mem[PER_VOICE_BASE + 1 + off]
        pattern_ptr.append((hi << 8) | lo)
        timbre.append(bytearray(mem[PER_VOICE_BASE + 2 + off:
                                     PER_VOICE_BASE + 2 + off + 5]))
        duration_ctr.append(mem[DUR_CTR_BASE + v])

    return EngineState(
        tempo=mem[TEMPO_ADDR],
        tempo_ctr=mem[TEMPO_CTR_ADDR],
        song_pos=mem[SONG_POS_ADDR],
        pattern_ptr=pattern_ptr,
        timbre=timbre,
        duration_ctr=duration_ctr,
        memory=mem,
        inst_table=bytes(mem[INST_TABLE_ADDR:INST_TABLE_ADDR + 80]),
        song_table=bytes(mem[SONG_TABLE_ADDR:SONG_TABLE_ADDR + 32]),
        freq_hi=bytes(mem[FREQ_HI_ADDR:FREQ_HI_ADDR + 128]),
        freq_lo=bytes(mem[FREQ_LO_ADDR:FREQ_LO_ADDR + 128]),
    )


def _read_pattern_byte(state: EngineState, voice: int) -> int:
    """Read byte at pattern_ptr[voice]; advance pattern_ptr by 1."""
    b = state.memory[state.pattern_ptr[voice]]
    state.pattern_ptr[voice] = (state.pattern_ptr[voice] + 1) & 0xFFFF
    return b


def _load_note(state: EngineState, voice: int,
               writes: list[tuple[int, int]]) -> None:
    """Run the engine's load-note routine for `voice` (0/1/2).

    Recurses on control commands. Tick-consuming actions (NORMAL_NOTE,
    REST, SKIP, SET_DURATION) RTS out without further recursion.
    """
    voice_off = voice * 7
    byte = _read_pattern_byte(state, voice)

    if byte < 0x80:
        # NORMAL NOTE — write freq + 5-byte timbre + gated ctrl
        writes.append((0x01 + voice_off, state.freq_hi[byte]))
        writes.append((0x00 + voice_off, state.freq_lo[byte]))
        tb = state.timbre[voice]
        writes.append((0x02 + voice_off, tb[0]))               # pw_lo
        writes.append((0x03 + voice_off, tb[1]))               # pw_hi
        writes.append((0x04 + voice_off, tb[2]))               # ctrl junk
        writes.append((0x05 + voice_off, tb[3]))               # ad
        writes.append((0x06 + voice_off, tb[4]))               # sr
        writes.append((0x04 + voice_off, (tb[2] + 1) & 0xFF))  # gated ctrl
        return

    if byte == 0x80:
        # REST — gate off (write ctrl byte without +1)
        writes.append((0x04 + voice_off, state.timbre[voice][2]))
        return

    if byte == 0x81:
        # SKIP — no writes this tick
        return

    if byte == 0x82:
        # SET_DURATION — gate off, then read next byte as new duration
        writes.append((0x04 + voice_off, state.timbre[voice][2]))
        new_dur = _read_pattern_byte(state, voice)
        state.duration_ctr[voice] = new_dur
        return

    # Bit-7-set commands. Engine tests $Ex (song-jump) match first
    # against the current song_pos; if mismatch, then $Dx/$Cx/$Bx; if
    # nothing matches, treat as skip-byte and recurse to next.
    if byte == state.song_pos:
        # PATTERN_JUMP — load new pattern pointer from song_table
        new_pos = state.song_pos + 1
        if new_pos == 0xE6:
            new_pos = 0xE0
        state.song_pos = new_pos
        idx = (byte & 0x0F) * 2
        lo = state.song_table[idx]
        hi = state.song_table[idx + 1]
        state.pattern_ptr[voice] = (hi << 8) | lo
        _load_note(state, voice, writes)
        return

    hi_nibble = byte & 0xF0
    if hi_nibble == 0xD0:
        # SET_INSTRUMENT — copy 5 bytes from inst_table into voice's timbre
        idx = (byte & 0x0F) * 5
        for i in range(5):
            state.timbre[voice][i] = state.inst_table[idx + i]
        _load_note(state, voice, writes)
        return

    if hi_nibble == 0xC0:
        # SET_MASTER_VOL — D418 = low nibble (preserving filter bits? engine just STAs)
        writes.append((0x18, byte & 0x0F))
        _load_note(state, voice, writes)
        return

    if hi_nibble == 0xB0:
        # SET_TEMPO
        state.tempo = byte & 0x0F
        _load_note(state, voice, writes)
        return

    # Anything else bit-7-set — treat as no-op marker (recurse)
    _load_note(state, voice, writes)


def play_one_frame(state: EngineState) -> list[tuple[int, int]]:
    """Run one VBI frame. Returns list of (reg, val) writes (cycle-
    less; just the order the engine emits them)."""
    state.tempo_ctr = (state.tempo_ctr + 1) & 0xFF
    if state.tempo_ctr != state.tempo:
        return []
    state.tempo_ctr = 0
    writes: list[tuple[int, int]] = []
    for v in range(3):
        if state.duration_ctr[v] == 1:
            _load_note(state, v, writes)
        else:
            state.duration_ctr[v] = (state.duration_ctr[v] - 1) & 0xFF
    return writes


def init_writes(sid_path: str, subtune: int = 0
                ) -> list[tuple[int, int]]:
    """SID writes performed by the engine's init routine, captured by
    intercepting $D400-$D418 writes during py65-simulated init."""
    _, sid_writes, _ = _run_init(sid_path, subtune)
    return sid_writes


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/C/Clever_Music/Fairlight.sid'
    state = load_state_from_sid(path)
    print(f'tempo={state.tempo} tempo_ctr={state.tempo_ctr} '
          f'song_pos=${state.song_pos:02X}')
    for v in range(3):
        print(f'V{v+1}: ptr=${state.pattern_ptr[v]:04X} '
              f'tb={" ".join(f"{b:02X}" for b in state.timbre[v])} '
              f'dur={state.duration_ctr[v]}')
