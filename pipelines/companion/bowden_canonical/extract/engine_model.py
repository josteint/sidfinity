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


def _scan_voice_blocks(mem: bytearray, play_addr: int) -> tuple[list[dict], int]:
    """Scan the play loop for the 3 per-voice setup blocks. Each block
    matches the pattern:

        LDX abs   ($AE oplo ophi)   — V_pos counter read
        INC abs   ($EE oplo ophi)   — V_pos++
        LDY abs,X ($BC oplo ophi)   — orderlist[V_pos] read
        LDX #     ($A2 imm)          — set voice offset (0/7/14)
        JSR abs   ($20 oplo ophi)    — call proc_note

    Returns (voices, proc_note_addr). Each voice dict carries v_pos,
    v_ord (orderlist base), v_off (voice offset), jsr_op_addr (location
    of the JSR opcode byte, used for voice-enable detection).

    Engines vary in layout: bowden_canonical (Vic Berry et al) has these
    blocks at play+$7D after a `JMP main` from the tempo gate; Surfchamp
    has them inline at play+$10 with the tempo gate falling through;
    Hyper_Blast is the bowden layout relocated to $55C0. The scanner
    finds the blocks wherever they are.
    """
    voices = []
    proc_note = None
    pc = play_addr
    end = play_addr + 0x200  # don't scan forever
    while pc < end - 14 and len(voices) < 3:
        if (mem[pc] == 0xAE and mem[pc + 3] == 0xEE
                and mem[pc + 6] == 0xBC and mem[pc + 9] == 0xA2
                and mem[pc + 11] in (0x20, 0x2C)):    # JSR or BIT (voice disabled)
            v_pos = mem[pc + 1] | (mem[pc + 2] << 8)
            v_pos2 = mem[pc + 4] | (mem[pc + 5] << 8)
            v_ord = mem[pc + 7] | (mem[pc + 8] << 8)
            v_off = mem[pc + 10]
            pn = mem[pc + 12] | (mem[pc + 13] << 8)
            if v_pos == v_pos2 and v_off in (0, 7, 14):
                if proc_note is None:
                    proc_note = pn
                if pn == proc_note:
                    voices.append({
                        'v_pos': v_pos,
                        'v_ord': v_ord,
                        'v_off': v_off,
                        'jsr_op_addr': pc + 11,
                    })
                    pc += 14
                    continue
        pc += 1
    if len(voices) != 3:
        raise ValueError(f'expected 3 voice blocks in play loop, found {len(voices)}')
    return voices, proc_note


def _scan_proc_note(mem: bytearray, proc_addr: int) -> dict:
    """Scan proc_note for the freq-table / timbre-base / ctrl-byte
    addresses. The structure is:

        TYA / AND #$80 / BNE bit7_path
        LDA freq_hi_tab,Y   ; first LDA abs,Y after entry
        STA $D401,X
        LDA freq_lo_tab,Y   ; second LDA abs,Y
        STA $D400,X
        NOP / NOP (often)
        TXA / TAY
        ADC #$04
        STA end_y_storage
        LDA timbre_base,Y   ; PW loop's read
        STA $D402,Y
        INY / CPY end_y / BNE -
        LDY ctrl_base,X     ; gated ctrl read
        INY / TYA / STA $D404,X / RTS
    """
    pc = proc_addr
    end = proc_addr + 0x40
    lda_abs_y_addrs = []
    ldy_abs_x_addr = None
    while pc < end:
        op = mem[pc]
        if op == 0xB9:  # LDA abs,Y
            lda_abs_y_addrs.append(mem[pc + 1] | (mem[pc + 2] << 8))
            pc += 3
        elif op == 0xBC:  # LDY abs,X — gated ctrl read
            if ldy_abs_x_addr is None:
                ldy_abs_x_addr = mem[pc + 1] | (mem[pc + 2] << 8)
            pc += 3
        elif op == 0x60:  # RTS — end of normal-note path
            break
        else:
            # Use a simple length table for the rest
            pc += _opcode_length(op)
    if len(lda_abs_y_addrs) < 3:
        raise ValueError(
            f'proc_note at ${proc_addr:04X}: expected ≥3 LDA abs,Y, got {len(lda_abs_y_addrs)}')
    return dict(
        freq_hi_base=lda_abs_y_addrs[0],
        freq_lo_base=lda_abs_y_addrs[1],
        timbre_base=lda_abs_y_addrs[2],
        ctrl_base=ldy_abs_x_addr,
    )


# Minimal 6502 opcode-length table used by _scan_proc_note.
_OP_LEN = [1] * 256
# 1-byte opcodes default; common 2-byte (imm/zp) and 3-byte (abs) overrides
_2BYTE = {0xA9, 0xA2, 0xA0, 0x29, 0x09, 0x49, 0x69, 0xE9, 0xC9, 0xC0, 0xE0,
          0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0,
          0xA5, 0xA6, 0xA4, 0x85, 0x86, 0x84, 0x65, 0x25, 0x05, 0xC5, 0xC6,
          0xE5, 0xE6, 0x45, 0x06, 0x46, 0x26, 0x66, 0x24}
_3BYTE = {0xAD, 0xAE, 0xAC, 0x8D, 0x8E, 0x8C, 0x6D, 0x2D, 0x0D, 0x4D, 0xCD,
          0xCE, 0xEE, 0xED, 0xEC, 0xCC, 0x4C, 0x6C, 0x20, 0xBD, 0xB9, 0xBE,
          0xBC, 0x9D, 0x99, 0x1D, 0x19, 0x3D, 0x39, 0x5D, 0x59, 0x7D, 0x79,
          0xDD, 0xD9, 0xFD, 0xF9, 0x0E, 0x1E, 0x2E, 0x3E, 0x4E, 0x5E, 0x6E,
          0x7E, 0x2C}
for op in _2BYTE:
    _OP_LEN[op] = 2
for op in _3BYTE:
    _OP_LEN[op] = 3


def _opcode_length(op: int) -> int:
    return _OP_LEN[op]


def _scan_tempo_gate(mem: bytearray, play_addr: int) -> tuple[int, int]:
    """Find the tempo_ctr and tempo addresses by scanning the tempo
    gate at the play entry. Two variants seen:

        bowden_canonical:   LDX tempo_ctr / INX / STX tempo_ctr / CPX tempo / BNE
        Surfchamp:          INC tempo_ctr / LDA tempo_ctr / CMP tempo / BNE
    """
    pc = play_addr
    end = play_addr + 0x20
    inc_target = None
    ldx_target = None
    cmp_target = None
    cpx_target = None
    while pc < end:
        op = mem[pc]
        if op == 0xEE:  # INC abs
            if inc_target is None:
                inc_target = mem[pc + 1] | (mem[pc + 2] << 8)
            pc += 3
        elif op == 0xAE:  # LDX abs
            if ldx_target is None:
                ldx_target = mem[pc + 1] | (mem[pc + 2] << 8)
            pc += 3
        elif op == 0xCD:  # CMP abs
            cmp_target = mem[pc + 1] | (mem[pc + 2] << 8)
            break
        elif op == 0xEC:  # CPX abs
            cpx_target = mem[pc + 1] | (mem[pc + 2] << 8)
            break
        else:
            pc += _opcode_length(op)
    if cpx_target is not None:
        return ldx_target, cpx_target          # bowden style
    if cmp_target is not None:
        return inc_target, cmp_target          # Surfchamp style
    raise ValueError(f'no tempo gate CMP/CPX found near play=${play_addr:04X}')


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
    cia1_timer_a: int = 0       # 16-bit CIA1 timer A value (0 = default)


class _TrackingMemory(bytearray):
    """bytearray subclass that records writes to specific address ranges.

    Used to capture init-time writes to CIA1 timer registers ($DC04/$DC05).
    Some engines (e.g. Surfchamp) program a non-default play() dispatch
    rate this way — the rebuild needs to replicate the programming or
    play at the wrong speed.
    """
    cia_writes: dict[int, int]  # type: ignore

    def __new__(cls, size):
        obj = super().__new__(cls, size)
        obj.cia_writes = {}
        return obj

    def __setitem__(self, idx, val):
        if isinstance(idx, int) and 0xDC00 <= idx <= 0xDDFF:
            self.cia_writes[idx] = val
        super().__setitem__(idx, val)


def _run_init(sid_path: str, subtune: int = 0) -> tuple[bytearray, int]:
    """Load the SID, run its init routine in py65, return (memory, load).

    Used to capture the post-init memory state for the given subtune
    index. Some Bowden-canonical SIDs (e.g. Keith Bowden's own
    `Roundabout`) ship with the freq table and orderlist addresses
    STORED in self-modifying-code form — init patches the high bytes
    of the play loop's `LDA $CA00,Y` etc. to point at a different
    memory layout. Reading the post-init bytes is the simple, layout-
    agnostic way to know where each table lives.

    Multi-subtune engines (e.g. Karl Hörnell's Melonmania) use the A
    register passed to init to select which subtune's data tables get
    patched into the play loop. Different subtunes can have different
    orderlist addresses, different timbres, different tempo, and even
    voices disabled by patching `JSR $C0AD` to `BIT $C0AD`.
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
    mpu.memory = _TrackingMemory(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.a = subtune
    mpu.x = 0
    mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    # Run until PC leaves the loaded binary range.
    for _ in range(200000):
        if not load <= mpu.pc < load + len(body):
            break
        mpu.step()
    return bytearray(mpu.memory), load


def load_state_from_sid(sid_path: str, subtune: int = 0) -> EngineState:
    """Read engine state from a Bowden-canonical-family SID for the
    given subtune index.

    All addresses (V_pos, orderlist bases, freq tables, timbres, tempo,
    ctrl bytes) are discovered by scanning the post-init play loop and
    proc_note for the appropriate operand bytes. This handles every
    layout variant we've seen so far:
      - $C000-base: Vic Berry / Roundabout / Melonmania / Titanic
      - $55C0-base relocated: Hyper_Blast
      - Inline-tempo-gate layout: Surfchamp (no JMP to main play; voice
        blocks start at play+$10 instead of play+$7D)
    """
    raw = Path(sid_path).read_bytes()
    play_addr = struct.unpack('>H', raw[12:14])[0]

    mem, _ = _run_init(sid_path, subtune)
    voices, proc_addr = _scan_voice_blocks(mem, play_addr)
    proc_info = _scan_proc_note(mem, proc_addr)
    tempo_ctr_addr, tempo_addr = _scan_tempo_gate(mem, play_addr)

    def slice_(start: int, end: int) -> bytes:
        return bytes(mem[start:end])

    v_pos = [mem[v['v_pos']] for v in voices]

    # Timbre base is the address used inside the PW loop's `LDA $XX,Y`,
    # where Y starts at the voice offset (0/7/14). So timbre_base+0 is
    # V1.pw_lo, timbre_base+7 is V2.pw_lo, etc. We slice 5 bytes per voice.
    timbre = [slice_(proc_info['timbre_base'] + v['v_off'],
                     proc_info['timbre_base'] + v['v_off'] + 5)
              for v in voices]

    # Voice enables — JSR opcode is $20, BIT (absolute) is $2C.
    voice_enabled = tuple(mem[v['jsr_op_addr']] == 0x20 for v in voices)

    orderlists = []
    for v, voice in enumerate(voices):
        if not voice_enabled[v]:
            orderlists.append(bytes([0x81, 0xFF]))
            continue
        base = voice['v_ord']
        bs = slice_(base, base + 256)
        ff = bs.find(0xFF)
        if ff < 0:
            orderlists.append(bytes(bs) + bytes([0xFF]))
        else:
            orderlists.append(bs[: ff + 1])

    cia_writes = getattr(mem, 'cia_writes', {})
    cia1_timer_a = (cia_writes.get(0xDC04, 0)
                    | (cia_writes.get(0xDC05, 0) << 8))

    return EngineState(
        tempo=mem[tempo_addr],
        v_pos=v_pos,
        timbre=timbre,
        orderlists=orderlists,
        freq_hi=slice_(proc_info['freq_hi_base'],
                       proc_info['freq_hi_base'] + 128),
        freq_lo=slice_(proc_info['freq_lo_base'],
                       proc_info['freq_lo_base'] + 128),
        tempo_ctr=mem[tempo_ctr_addr],
        cia1_timer_a=cia1_timer_a,
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

    # bit-7-set + not $80/$FF: engine branches to $C108 which is just RTS.
    # The voice does nothing this tick — no SID writes. Karl Hörnell's
    # Melonmania uses these as silent skip markers (where a normal note
    # would re-trigger the envelope, an unrecognised bit-7 byte lets
    # the previous envelope keep ringing without retrigger).
    return


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
