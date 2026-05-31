"""Jay_Derrett engine scanner.

The engine — sibling to bowden_canonical in HVSC's sidid
classification but otherwise unrelated — uses pointer-walking
orderlists. The play loop carries three "voice setup blocks", each
shaped:

    LDA abs_lo            ; copy current ptr-lo from voice-state to zp scratch
    STA zp_lo
    LDA abs_hi            ; copy ptr-hi
    STA zp_hi
    ...                   ; voice-index + offset setup (LDX/INC/ASL/LDA/STA)
    JSR proc_note         ; advance the pointer through the byte-stream
    LDA zp_lo             ; write the advanced ptr back to voice-state
    STA abs_lo
    LDA zp_hi
    STA abs_hi

`abs_lo`/`abs_hi` are consecutive (the per-voice ptr lives at
abs_lo:abs_hi). `zp_lo`/`zp_hi` are consecutive engine scratch slots
(`$F2`/`$F3` on Ninja_Hamster). The inner setup varies per voice
(LDX #imm vs INC + LDA #imm vs INC + ASL) and we don't need to
parse it yet — the surrounding LDA/STA bookends are the load-bearing
signal.

See `pipelines/companion/jay_derrett/README.md` for the full engine
RE based on Ninja_Hamster (load $C000, init $C57A, play $C452).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field


# Opcodes
_OP_LDA_ABS = 0xAD
_OP_LDA_ZP  = 0xA5
_OP_STA_ABS = 0x8D
_OP_STA_ZP  = 0x85
_OP_JSR_ABS = 0x20


# 6502 instruction lengths by opcode. Same shape as src/code_flow.py
# but with the JSR-is-3-bytes patch applied (the base table has $20
# at 2 because it shares the low-nibble pattern of other 2-byte ops).
_INST_LEN = [0] * 256
for _op in (0x00, 0x08, 0x0A, 0x18, 0x28, 0x2A, 0x38, 0x40, 0x48, 0x4A,
            0x58, 0x60, 0x68, 0x6A, 0x78, 0x88, 0x8A, 0x98, 0x9A, 0xA8,
            0xAA, 0xB8, 0xBA, 0xC8, 0xCA, 0xD8, 0xE8, 0xEA, 0xF8):
    _INST_LEN[_op] = 1
for _op in range(256):
    if _INST_LEN[_op] > 0:
        continue
    _mode = _op & 0x1F
    if _mode in (0x00, 0x01, 0x02, 0x04, 0x05, 0x06, 0x09, 0x0A,
                 0x10, 0x11, 0x12, 0x14, 0x15, 0x16):
        _INST_LEN[_op] = 2
for _i in range(256):
    if _INST_LEN[_i] == 0:
        _INST_LEN[_i] = 3
_INST_LEN[0x20] = 3  # JSR abs (the base table classifies it as 2 by
                     # mistake — see tools/seed_disassembly.py for the
                     # same patch).


@dataclass
class VoiceBlock:
    """One per-voice setup block found in the play loop.

    `idx` is 0/1/2 (the order the block appears at). `ptr_addr` is the
    16-bit address holding the voice's orderlist pointer (lo at
    ptr_addr, hi at ptr_addr+1). `zp` is the scratch zp slot the
    engine uses while proc_note is running. `setup_bytes` is the raw
    inner-block bytes between the ptr-load and the JSR — kept verbatim
    so a later pass can decode the voice-index/offset assignment scheme.
    """
    idx: int
    ptr_addr: int
    zp: int
    setup_bytes: bytes


@dataclass
class EngineState:
    """The static state extracted from a Jay_Derrett SID by the
    scanner. Mostly addresses + per-voice pointer slots; later phases
    will fill in tempo, instrument tables, freq tables, etc."""
    load: int
    init_addr: int
    play_addr: int
    proc_note_addr: int
    voices: list[VoiceBlock] = field(default_factory=list)


def _read_psid_header(data: bytes) -> tuple[int, int, int, int, int]:
    """Return (hdr_size, load, init, play, n_sub) from a PSID file."""
    hdr_size = struct.unpack('>H', data[6:8])[0]
    load = struct.unpack('>H', data[8:10])[0]
    init = struct.unpack('>H', data[10:12])[0]
    play = struct.unpack('>H', data[12:14])[0]
    n_sub = struct.unpack('>H', data[14:16])[0]
    return hdr_size, load, init, play, n_sub


def _load_sid_binary(sid_path: str) -> tuple[bytearray, int, int, int, int]:
    """Read a PSID file and return (mem, load, init, play, n_sub)
    where `mem` is a 64K bytearray with the binary copied in at its
    load address."""
    with open(sid_path, 'rb') as f:
        data = f.read()
    hdr_size, load, init, play, n_sub = _read_psid_header(data)
    body = data[hdr_size:]
    if load == 0:
        # Embedded load address (PSID convention when header says 0)
        load = body[0] | (body[1] << 8)
        body = body[2:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    return mem, load, init, play, n_sub


def _scan_voice_block(mem: bytearray, pc: int) -> tuple[VoiceBlock, int] | None:
    """Try to match one voice setup block starting at `pc`. Returns
    (block, end_pc) on a match, or None if no block matches here.

    The bookends are LDA abs / STA zp / LDA abs / STA zp (ptr load)
    and after the JSR, LDA zp / STA abs / LDA zp / STA abs (ptr write
    back). Both halves must reference the same `(abs, abs+1)` source
    address and the same `(zp, zp+1)` scratch slots.
    """
    # --- Front bookend: LDA abs_lo / STA zp_lo / LDA abs_hi / STA zp_hi ---
    if pc + 10 >= len(mem): return None
    if mem[pc] != _OP_LDA_ABS or mem[pc + 3] != _OP_STA_ZP: return None
    if mem[pc + 5] != _OP_LDA_ABS or mem[pc + 8] != _OP_STA_ZP: return None
    abs_lo = mem[pc + 1] | (mem[pc + 2] << 8)
    zp_lo  = mem[pc + 4]
    abs_hi = mem[pc + 6] | (mem[pc + 7] << 8)
    zp_hi  = mem[pc + 9]
    if abs_hi != abs_lo + 1 or zp_hi != zp_lo + 1:
        return None

    # --- Walk forward instruction-by-instruction looking for a JSR ---
    # Some tunes (Equalizer) interleave extra LDA-then-STA pairs of
    # unrelated state before the proc_note call. Must walk by 6502
    # instruction length so a STX/LDA operand byte (e.g. `86 20`)
    # isn't mistaken for the $20 JSR opcode.
    setup_start = pc + 10
    setup_end = None
    proc_note = None
    q = setup_start
    limit = min(setup_start + 48, len(mem) - 13)
    while q < limit:
        op = mem[q]
        if op == _OP_JSR_ABS:
            proc_note = mem[q + 1] | (mem[q + 2] << 8)
            setup_end = q
            break
        ln = _INST_LEN[op] or 1
        q += ln
    if proc_note is None:
        return None

    # --- Back bookend: LDA zp_lo / STA abs_lo / LDA zp_hi / STA abs_hi ---
    # Usually immediately after the JSR, but some tunes insert a guard
    # check (`LDA flag / BNE skip`) between the JSR and the writeback.
    # Search a small window.
    bk_start = setup_end + 3  # past the JSR opcode + 2-byte abs target
    bk = None
    for cand in range(bk_start, min(bk_start + 36, len(mem) - 11)):
        if (mem[cand] == _OP_LDA_ZP and mem[cand + 1] == zp_lo
                and mem[cand + 2] == _OP_STA_ABS
                and (mem[cand + 3] | (mem[cand + 4] << 8)) == abs_lo
                and mem[cand + 5] == _OP_LDA_ZP and mem[cand + 6] == zp_hi
                and mem[cand + 7] == _OP_STA_ABS
                and (mem[cand + 8] | (mem[cand + 9] << 8)) == abs_hi):
            bk = cand
            break
    if bk is None:
        return None

    block = VoiceBlock(
        idx=-1,  # caller will assign once it knows the block ordering
        ptr_addr=abs_lo,
        zp=zp_lo,
        setup_bytes=bytes(mem[setup_start:setup_end]),
    )
    return block, bk + 10


def scan_voice_blocks(mem: bytearray, play_addr: int
                      ) -> tuple[list[VoiceBlock], int]:
    """Scan from `play_addr` for 3 consecutive voice setup blocks.

    Returns (blocks, proc_note_addr). All 3 blocks must JSR the same
    proc_note address (the engine's single per-voice dispatcher).
    Raises ValueError if fewer than 3 blocks are found within ~256
    bytes of play_addr.
    """
    blocks: list[VoiceBlock] = []
    proc_note: int | None = None
    pc = play_addr
    end = play_addr + 0x100
    while pc < end and len(blocks) < 3:
        m = _scan_voice_block(mem, pc)
        if m is None:
            pc += 1
            continue
        block, pc_next = m
        # Re-derive the JSR target so we can enforce shared proc_note.
        # Walk by instruction (not by byte) — STX/LDA operands can
        # contain $20 and would be misread as JSR opcodes if we walked
        # by byte.
        pn = None
        q = pc + 10
        while q < pc_next - 10:
            op = mem[q]
            if op == _OP_JSR_ABS:
                pn = mem[q + 1] | (mem[q + 2] << 8)
                break
            ln = _INST_LEN[op] or 1
            q += ln
        if pn is None:
            pc += 1
            continue
        if proc_note is None:
            proc_note = pn
        if pn != proc_note:
            # Different proc_note — not part of the same engine
            # play loop. Skip and keep scanning.
            pc += 1
            continue
        block.idx = len(blocks)
        blocks.append(block)
        pc = pc_next
    if len(blocks) < 3:
        raise ValueError(
            f'jay_derrett: only {len(blocks)}/3 voice blocks found in '
            f'play loop at ${play_addr:04X}')
    assert proc_note is not None
    return blocks, proc_note


def _peel_trampoline(mem: bytearray, pc: int) -> int | None:
    """If `pc` points at a known static dispatch shell, return the
    inner play address. Otherwise None. Static = readable from the
    SID binary bytes alone (no init emulation needed).

    Patterns handled:
      - bare `JMP abs` (Dracula-shape via JSR is handled separately)
      - bank-switch + JSR: `LDA #imm / STA $01 / JSR abs / LDA #imm /
        STA $01 / RTS` (Dracula)
      - conditional dispatch (`LDA / CMP / BNE / JMP a / JMP b`) —
        Sqij; tries the first JMP target.
    """
    op = mem[pc]
    # Bare JMP abs
    if op == 0x4C:
        return mem[pc + 1] | (mem[pc + 2] << 8)
    # Bank-switch + JSR: A9 imm 85 01 20 lo hi A9 imm 85 01 60
    if (op == 0xA9 and mem[pc + 2] == 0x85 and mem[pc + 3] == 0x01
            and mem[pc + 4] == 0x20):
        return mem[pc + 5] | (mem[pc + 6] << 8)
    # Conditional JMP: LDA abs / CMP #imm / Bxx +3 / JMP a / JMP b
    if (op == 0xAD and mem[pc + 3] == 0xC9 and mem[pc + 5] in (0xD0, 0xF0)
            and mem[pc + 6] == 0x03 and mem[pc + 7] == 0x4C):
        return mem[pc + 8] | (mem[pc + 9] << 8)
    return None


def _run_init_capture(sid_path: str, subtune: int = 0
                      ) -> tuple[bytearray, int, int, int]:
    """Run the SID's init() in py65 and return the post-init memory
    plus (load, init_addr, play_addr).

    Used to recover the dispatch state for SIDs whose play vector is
    installed at runtime: KERNAL-IRQ engines (`play_addr=$0000` — init
    sets the IRQ vector at $0314/$0315) and engines whose play_addr
    points at a `JMP ($zp)` or `JMP $abs` whose target gets patched
    by init.
    """
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU

    with open(sid_path, 'rb') as f:
        raw = f.read()
    hdr_size, load_hdr, init_addr, play_addr, _ = _read_psid_header(raw)
    body = raw[hdr_size:]
    if load_hdr == 0:
        load = body[0] | (body[1] << 8)
        body = body[2:]
    else:
        load = load_hdr

    mpu = MPU()
    mpu.memory = bytearray(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.a = subtune
    mpu.x = 0
    mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    # Plant a sentinel return address so the RTS at end of init lands
    # somewhere we can detect. We pick $0200 (out of typical engine
    # range); init's RTS will fetch $0200-1 then jump there.
    SENTINEL = 0x0200
    mpu.memory[0x01FF] = (SENTINEL - 1) >> 8
    mpu.memory[0x01FE] = (SENTINEL - 1) & 0xFF
    mpu.pc = init_addr
    # Run until PC leaves the engine area (to the sentinel or out of
    # the loaded binary).
    for _ in range(200000):
        if mpu.pc == SENTINEL:
            break
        if not load <= mpu.pc < load + len(body):
            break
        mpu.step()
    return bytearray(mpu.memory), load, init_addr, play_addr


def _resolve_play_addr(mem: bytearray, play_addr: int) -> int:
    """Resolve `play_addr` to a concrete code address using `mem`
    (which must already have been touched by init).

    Handles:
      - play_addr == 0: read IRQ vector at $0314/$0315 (KERNAL).
      - first instruction at play_addr is `JMP ($zp)` ($6C): read the
        16-bit pointer at the indirect target.
      - first instruction is `JMP $abs` ($4C): follow it (same as
        the static peel but works regardless of memory state).
    """
    if play_addr == 0:
        return mem[0x0314] | (mem[0x0315] << 8)
    op = mem[play_addr]
    if op == 0x4C:  # JMP abs
        return mem[play_addr + 1] | (mem[play_addr + 2] << 8)
    if op == 0x6C:  # JMP (abs)
        ind = mem[play_addr + 1] | (mem[play_addr + 2] << 8)
        return mem[ind] | (mem[(ind + 1) & 0xFFFF] << 8)
    return play_addr


def _peel_irq_handler(mem: bytearray, pc: int) -> int | None:
    """If `pc` points at a KERNAL IRQ handler (or a subtune dispatcher),
    find the inner JSR or selected JMP and return its target.

    Typical raster-IRQ handler:
        INC $D019           ; ack raster
        (optional) LDA $01 / PHA / LDA #imm / STA $01   ; bank-switch save
        (optional) LDA $F6 / BEQ skip                   ; conditional skip
        JSR <inner_play>
        (optional) PLA / STA $01                        ; bank-switch restore
        JMP $EA81                                       ; KERNAL IRQ exit

    Subtune dispatcher (Gun_Runner):
        LDA #imm            ; load constant
        BEQ +N              ; always taken since imm=0 sets Z
        ...
        JMP <selected play>

    Walks forward by 6502 instruction length. Tracks one piece of CPU
    state — `a_known`, the last-known A value from `LDA #imm` — so a
    following `BEQ +N` can be evaluated. Returns the first JSR or JMP
    target reached. Stops at RTI/RTS.
    """
    q = pc
    end = pc + 80
    a_known: int | None = None
    while q < end and q < len(mem):
        op = mem[q]
        if op == 0x20:  # JSR abs
            return mem[q + 1] | (mem[q + 2] << 8)
        if op == 0x4C:  # JMP abs
            return mem[q + 1] | (mem[q + 2] << 8)
        if op == 0x40 or op == 0x60:  # RTI / RTS
            return None
        if op == 0xA9:  # LDA #imm — record A
            a_known = mem[q + 1]
        elif op == 0xF0 and a_known == 0:  # BEQ taken (A==0 sets Z)
            offset = mem[q + 1]
            if offset >= 0x80:
                offset -= 0x100
            q += 2 + offset
            continue
        elif op == 0xD0 and a_known is not None and a_known != 0:
            # BNE taken (A!=0 clears Z)
            offset = mem[q + 1]
            if offset >= 0x80:
                offset -= 0x100
            q += 2 + offset
            continue
        ln = _INST_LEN[op] or 1
        q += ln
    return None


def load_state_from_sid(sid_path: str, subtune: int = 0) -> EngineState:
    """Top-level entry: load the SID, scan its play loop, return an
    `EngineState` with the engine's structural addresses filled in.

    Tries three strategies in order:
      1. Direct static scan at the PSID `play_addr`.
      2. Peel up to 3 layers of static trampoline (`_peel_trampoline`)
         and re-scan.
      3. Run init in py65 (`_run_init_capture`), resolve the play
         vector from post-init memory (IRQ vector at $0314/$0315 or
         `JMP ($abs)` indirect target), re-scan with that memory.
    """
    mem, load, init_addr, play_addr, _n_sub = _load_sid_binary(sid_path)

    # Strategy 1+2: static scan, with up to 3 static trampoline peels.
    pc = play_addr
    static_err: Exception | None = None
    if play_addr != 0:
        for _ in range(4):
            try:
                blocks, proc_note = scan_voice_blocks(mem, pc)
                return EngineState(
                    load=load, init_addr=init_addr, play_addr=play_addr,
                    proc_note_addr=proc_note, voices=blocks)
            except ValueError as e:
                static_err = e
                inner = _peel_trampoline(mem, pc)
                if inner is None or inner == pc:
                    break
                pc = inner

    # Strategy 3: run init, resolve play via post-init memory, re-scan.
    post_mem, _, _, _ = _run_init_capture(sid_path, subtune)
    resolved = _resolve_play_addr(post_mem, play_addr)
    if resolved == 0:
        raise ValueError(
            f'jay_derrett: init did not install a play vector '
            f'(play=$0000 still, $0314/$0315=$00)')
    # Same peel chain on the resolved address. Try both the static
    # trampoline peel AND the IRQ-handler peel — the IRQ case
    # (`play_addr=$0000`) resolves to a raster-IRQ wrapper whose
    # real-play target sits behind an INC $D019 + optional bank-switch
    # + JSR inner_play sequence.
    pc = resolved
    for _ in range(4):
        try:
            blocks, proc_note = scan_voice_blocks(post_mem, pc)
            return EngineState(
                load=load, init_addr=init_addr, play_addr=play_addr,
                proc_note_addr=proc_note, voices=blocks)
        except ValueError as e:
            inner = (_peel_trampoline(post_mem, pc)
                     or _peel_irq_handler(post_mem, pc))
            if inner is None or inner == pc:
                raise static_err or e
            pc = inner
    raise static_err or ValueError('jay_derrett: scan exhausted all strategies')
