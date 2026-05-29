"""Engine model for Vic Berry's Companion variant (`c8282844` fingerprint).

Pure-Python simulation of the engine's per-frame SID write stream. Used
to validate our understanding before designing USF representation +
codegen — if the emulator's writes match py65's capture of the original
SID byte-for-byte, the model is correct.

Engine (from disassembly at pipelines/companion/bowden_canonical/disassembly.s):

  play (every VBI):
    INC tempo_ctr
    if tempo_ctr != tempo:    return    ; tempo gate
    tempo_ctr = 0
    for each voice (V1, V2, V3):
        pos = v_pos[i]
        v_pos[i] += 1
        note = orderlist[i][pos]
        proc_note(voice=i, note=note)

  proc_note(voice, note):
    if note & 0x80 == 0:                  # normal pitch
      write V_FREQ_HI ← freq_hi[note]
      write V_FREQ_LO ← freq_lo[note]
      write V_PW_LO, V_PW_HI, V_CTRL (junk), V_AD, V_SR from timbre[voice]
      write V_CTRL ← ctrl[voice] | 1      # gate on
    elif note == 0x80:                    # rest
      write V_CTRL ← ctrl[voice]          # gate off (no gate bit)
    elif note == 0xFF:                    # loop
      v_pos[voice] = 1
      note = orderlist[voice][0]
      proc_note(voice, note)              # tail-recursive

The 5-byte timbre block per voice is at $C019 + voice_offset (0/7/14):
  +0: pw_lo
  +1: pw_hi
  +2: ctrl    (used both as 'junk' write inside the loop and as the
              source for the gated V_CTRL write that follows)
  +3: ad
  +4: sr      ← reached via a 6502 carry-leak trick: at $C0C2 the engine
              does `ADC #4` without a CLC, and the upstream tempo gate's
              CPX leaves carry SET when control falls through, so the
              effective add is 5 — making the PW loop run 5 iterations
              instead of 4. Without this quirk, V_SR would never get
              written from the timbre block (the init sets V1/V2 SR to
              0 and V3 SR is undefined). With it, all three voices'
              V_SR comes from timbre[+4].

Initial positions:
  V1pos: zeroed by init     → starts at 0
  V2pos: load-time value    → starts wherever the binary stores it (Bach: 45)
  V3pos: load-time value    → starts wherever the binary stores it (Bach: 44)

When a voice hits $FF, pos becomes 1 (not 0), then orderlist[0] plays
once before normal advancement resumes at pos=2.

Tempo lives at $C07B in the binary (frames per tick).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


# Engine memory map (from the disassembly).
TEMPO_ADDR = 0xC07B
V1POS_ADDR = 0xC017
V2POS_ADDR = 0xC01E
V3POS_ADDR = 0xC025
TIMBRE_BASE = 0xC019            # per-voice timbre starts here; +0/+7/+14 per voice
TEMPO_CTR_ADDR = 0xC07C         # runtime tempo counter
FREQ_HI_BASE = 0xCA00
FREQ_LO_BASE = 0xCA80
ORDER_BASE = (0xCB00, 0xCC00, 0xCD00)  # V1, V2, V3 orderlists


@dataclass
class EngineState:
    """The dynamic state. Static data (orderlists, timbre, freq table)
    is read from the binary blob and held alongside."""
    tempo: int                  # frames per tick (engine constant per tune)
    v_pos: list[int]            # per-voice orderlist position (3)
    timbre: list[bytes]         # per-voice 5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr)
    orderlists: list[bytes]     # per-voice (3 × ~255 bytes, $FF-terminated)
    freq_hi: bytes              # 128 bytes
    freq_lo: bytes              # 128 bytes
    tempo_ctr: int = 0          # runtime counter


def _run_init(sid_path: str) -> tuple[bytearray, int]:
    """Load the SID, run its init routine in py65, return (memory, load).

    Used to capture the post-init memory state. Some Bowden-canonical
    SIDs (e.g. Keith Bowden's own `Roundabout`) ship with the freq table
    and orderlist addresses STORED in self-modifying-code form — init
    patches the high bytes of the play loop's `LDA $CA00,Y` etc. to
    point at a different memory layout. Reading the post-init bytes is
    the simple, layout-agnostic way to know where each table lives.
    """
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    load_in = struct.unpack('>H', raw[8:10])[0]
    body = raw[124:]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    init_addr = struct.unpack('>H', raw[10:12])[0]

    mpu = MPU()
    mpu.memory = bytearray(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.a = 0
    mpu.x = 0
    mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    for _ in range(50000):
        if not 0xC000 <= mpu.pc <= 0xCFFF:
            break
        mpu.step()
    return bytearray(mpu.memory), load


def _detect_layout(mem: bytearray) -> dict:
    """Read the freq-table and orderlist addresses encoded as operand
    bytes inside the post-init play loop. The high byte of each table
    is at a fixed offset within the play code:
      $C0B4 = freq_hi_tab high byte  (LDA $CA00,Y → patched)
      $C0BA = freq_lo_tab high byte  (LDA $CA80,Y → patched)
      $C088 = V1 orderlist high byte (LDY $CB00,X → patched)
      $C096 = V2 orderlist high byte (LDY $CC00,X → patched)
      $C0A4 = V3 orderlist high byte (LDY $CD00,X → patched)
    """
    return dict(
        freq_hi_base=(mem[0xC0B4] << 8) | 0x00,
        freq_lo_base=(mem[0xC0BA] << 8) | 0x80,
        v_order_bases=(
            (mem[0xC088] << 8) | 0x00,
            (mem[0xC096] << 8) | 0x00,
            (mem[0xC0A4] << 8) | 0x00,
        ),
    )


def load_state_from_sid(sid_path: str) -> EngineState:
    """Read engine state from a Bowden-canonical-family SID.

    Runs init via py65, then reads the post-init memory layout (which
    handles self-modifying-code variants like Roundabout that patch
    the freq table / orderlist addresses at runtime).
    """
    mem, _ = _run_init(sid_path)
    layout = _detect_layout(mem)

    def slice_(start: int, end: int) -> bytes:
        return bytes(mem[start:end])

    # Post-init v_pos values — V1 is zeroed by all known variant inits;
    # V2/V3 are either zeroed (Roundabout) or set to a per-tune offset
    # (Vic Berry tunes), preserved from load-time bytes.
    v_pos = [mem[V1POS_ADDR], mem[V2POS_ADDR], mem[V3POS_ADDR]]

    # 5-byte timbre per voice — same address layout in all known variants.
    timbre = [slice_(TIMBRE_BASE + off, TIMBRE_BASE + off + 5)
              for off in (0, 7, 14)]

    orderlists = []
    for base in layout['v_order_bases']:
        bs = slice_(base, base + 256)
        ff = bs.find(0xFF)
        if ff < 0:
            raise ValueError(f'no $FF terminator in orderlist at ${base:04X}')
        orderlists.append(bs[: ff + 1])

    return EngineState(
        tempo=mem[TEMPO_ADDR],
        v_pos=v_pos,
        timbre=timbre,
        orderlists=orderlists,
        freq_hi=slice_(layout['freq_hi_base'], layout['freq_hi_base'] + 128),
        freq_lo=slice_(layout['freq_lo_base'], layout['freq_lo_base'] + 128),
        tempo_ctr=mem[TEMPO_CTR_ADDR],
    )


def proc_note(state: EngineState, voice: int, note: int,
              writes: list[tuple[int, int]],
              skip_sr: bool = False) -> None:
    """Apply one note byte to a voice. Appends (reg_offset, val) for each
    SID write in the order the engine emits them.

    `voice` is 0/1/2 (we use 0/7/14 only at the SID register level).
    """
    voice_off = voice * 7  # 0, 7, 14 — used as register offset for the SID writes

    if note & 0x80 == 0:
        # Normal pitch: write freq+timbre+gate
        writes.append((0x01 + voice_off, state.freq_hi[note]))   # V_FREQ_HI
        writes.append((0x00 + voice_off, state.freq_lo[note]))   # V_FREQ_LO
        # 5-byte timbre dump — engine's PW loop runs 5 iterations (see
        # docstring re: the carry-leak ADC #4 trick) writing V_PW_LO,
        # V_PW_HI, V_CTRL (junk), V_AD, V_SR from timbre[voice][0..4]
        tb = state.timbre[voice]
        writes.append((0x02 + voice_off, tb[0]))                 # V_PW_LO
        writes.append((0x03 + voice_off, tb[1]))                 # V_PW_HI
        writes.append((0x04 + voice_off, tb[2]))                 # V_CTRL (junk — about to be overwritten)
        writes.append((0x05 + voice_off, tb[3]))                 # V_AD
        if not skip_sr:
            writes.append((0x06 + voice_off, tb[4]))             # V_SR (only if 5-byte timbre)
        # Gated CTRL: ctrl | $01 (engine does "INY" on ctrl, equivalent to +1
        # for the typical ctrl byte where bit 0 is off)
        writes.append((0x04 + voice_off, tb[2] + 1))             # V_CTRL with gate
        return

    if note == 0x80:
        # Rest — gate off (ctrl byte without the +1)
        writes.append((0x04 + voice_off, state.timbre[voice][2]))
        return

    if note == 0xFF:
        # Loop: pos := 1, then process orderlist[0] (engine's recursive call).
        # The engine's $FF dispatcher at $C0F0..$C105 does a sequence of
        # CPX checks (CPX #$00 / CPX #$07 / CPX #$0E) to select the right
        # voice's orderlist[0]. The LAST CPX executed determines the
        # carry flag entering the recursive proc_note:
        #   - For V1 (X=0): last CPX is #$0E, C=0 (X < $0E)
        #   - For V2 (X=7): last CPX is #$0E, C=0
        #   - For V3 (X=$E): CPX #$0E succeeds, BNE skipped, C=1
        # So V1 and V2's $FF recursive call enters proc_note with C=0,
        # which makes the PW timbre loop run only 4 iterations (no SR
        # write). V3's runs the normal 5 iterations.
        state.v_pos[voice] = 1
        if voice == 2:
            # V3: full 5-byte timbre
            proc_note(state, voice, state.orderlists[voice][0], writes)
        else:
            # V1 or V2: 4-byte timbre (skip SR write)
            proc_note(state, voice, state.orderlists[voice][0], writes,
                      skip_sr=True)
        return

    # bit-7-set + not $80/$FF: undefined in the engine (branches to $C108).
    # Should never occur in well-formed tunes.
    raise ValueError(f'undefined note byte ${note:02X} at voice {voice}')


def play_one_frame(state: EngineState) -> list[tuple[int, int]]:
    """Simulate one VBI frame. Returns the list of (reg_offset, val) SID writes
    in the order the engine emits them — or empty list if the tempo gate
    blocks the frame."""
    state.tempo_ctr += 1
    if state.tempo_ctr != state.tempo:
        return []
    state.tempo_ctr = 0

    writes: list[tuple[int, int]] = []
    for v in range(3):
        note = state.orderlists[v][state.v_pos[v]]
        state.v_pos[v] = (state.v_pos[v] + 1) & 0xFF
        proc_note(state, v, note, writes)
    return writes


def init_writes() -> list[tuple[int, int]]:
    """The fixed writes the engine's init routine emits (excluding the
    silence-loop sweep of $D400-$D418 → 0, which we model implicitly as
    'SID starts at zero state')."""
    # init at $C053 does:
    #   silence $D400-$D418 (we treat starting state as zero)
    #   D418 = $0F  (vol = max)
    #   D405 = $09  (V1 AD)
    #   D406 = $00  (V1 SR)
    #   D40C = $09  (V2 AD)
    #   D40D = $00  (V2 SR)
    return [
        (0x18, 0x0F),  # $D418
        (0x05, 0x09),  # V1_AD
        (0x06, 0x00),  # V1_SR
        (0x0C, 0x09),  # V2_AD
        (0x0D, 0x00),  # V2_SR
    ]


def simulate(sid_path: str, n_frames: int) -> list[list[tuple[int, int]]]:
    """Run `n_frames` of simulation. Returns per-frame write list.

    Frame 0 includes the init writes; subsequent frames are play() only.
    """
    state = load_state_from_sid(sid_path)
    out: list[list[tuple[int, int]]] = []
    out.append(init_writes() + play_one_frame(state))
    for _ in range(n_frames - 1):
        out.append(play_one_frame(state))
    return out


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.sid'
    state = load_state_from_sid(path)
    print(f'tempo: {state.tempo} frames/tick')
    print(f'v_pos initial: {state.v_pos}')
    print(f'timbres:')
    for i, tb in enumerate(state.timbre):
        print(f'  V{i+1}: pw=${tb[1]:02x}{tb[0]:02x} ctrl=${tb[2]:02x} '
              f'ad=${tb[3]:02x} sr=${tb[4]:02x}')
    print(f'orderlist lengths (incl $FF terminator): '
          f'{[len(ol) for ol in state.orderlists]}')

    # Simulate first 5 ticks of music (5 × tempo frames)
    print(f'\nFirst {3*state.tempo} frames of writes:')
    for f, writes in enumerate(simulate(path, 3 * state.tempo)):
        if writes:
            ws = ' '.join(f'D4{r:02X}=${v:02X}' for r, v in writes)
            print(f'  frame {f:3d}: {ws}')
