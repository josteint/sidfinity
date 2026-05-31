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

    `initial_ptr` is the orderlist pointer value present at `ptr_addr`
    after init runs (the starting position for this voice's stream).
    """
    idx: int
    ptr_addr: int
    zp: int
    setup_bytes: bytes
    initial_ptr: int = 0


@dataclass
class EngineState:
    """The static state extracted from a Jay_Derrett SID by the
    scanner. Mostly addresses + per-voice pointer slots; later phases
    will fill in tempo, instrument tables, freq tables, etc."""
    load: int
    init_addr: int
    play_addr: int
    proc_note_addr: int
    # The PC where the play loop's first per-voice setup block lives.
    # Equals `play_addr` for direct-play tunes; for trampoline /
    # IRQ-resolved tunes, it's the post-peel address. Downstream
    # extractors should use this (not `play_addr`) as the root for
    # reachability scans — both proc_note AND the per-frame block
    # are reachable from here.
    play_loop_entry: int = 0
    voices: list[VoiceBlock] = field(default_factory=list)
    # Post-init memory snapshot — populated when load_state_from_sid
    # ran init emulation, useful for downstream extractors that need
    # to follow self-modifying-code pointers or read table contents.
    post_init_mem: bytes | None = None


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


def _reachable_pcs(mem: bytearray, entry: int, budget: int = 2048
                   ) -> set[int]:
    """Walk 6502 control flow from `entry`, returning the set of all
    PCs reached. Follows JSR/JMP unconditionally and branches both
    ways; stops at RTI/RTS/budget. Used by the table-finding scanners
    so they only look at code actually called from proc_note (not
    random bytes elsewhere in the binary)."""
    seen: set[int] = set()
    stack = [entry]
    steps = 0
    while stack and steps < budget:
        pc = stack.pop()
        if pc in seen or pc >= len(mem):
            continue
        seen.add(pc)
        op = mem[pc]
        ln = _INST_LEN[op] or 1
        steps += 1
        if op in (0x60, 0x40):       # RTS / RTI
            continue
        if op == 0x4C:               # JMP abs
            stack.append(mem[pc + 1] | (mem[pc + 2] << 8))
            continue
        if op == 0x20:               # JSR abs
            stack.append(mem[pc + 1] | (mem[pc + 2] << 8))
            stack.append(pc + 3)     # fall through after the JSR
            continue
        if op == 0x6C:               # JMP (abs) — give up (target is
            continue                  # data-dependent on memory state)
        if 0x10 <= op <= 0xF0 and (op & 0x1F) == 0x10:
            # Branches (BPL/BMI/BVC/BVS/BCC/BCS/BNE/BEQ): try both paths.
            offset = mem[pc + 1]
            if offset >= 0x80:
                offset -= 0x100
            stack.append(pc + 2 + offset)
        stack.append(pc + ln)
    return seen


# 6502 opcodes that set A from a memory source (carry an addr operand).
# We only handle the addressing modes the jay_derrett engine actually
# uses for freq-table / voice-state loads.
_LDA_MODES: dict[int, str] = {
    0xA5: 'zp',       # LDA $zp
    0xAD: 'abs',      # LDA $abs
    0xB1: 'ind_y',    # LDA ($zp),Y
    0xB5: 'zp_x',     # LDA $zp,X
    0xB9: 'abs_y',    # LDA $abs,Y
    0xBD: 'abs_x',    # LDA $abs,X
}

# Opcodes that DON'T disturb A — predecessor walk can skip past them.
_A_NEUTRAL: set[int] = {
    0x18, 0x38,                                # CLC, SEC
    0x58, 0x78,                                # CLI, SEI
    0x88, 0xC8,                                # DEY, INY
    0xCA, 0xE8,                                # DEX, INX
    0x8A, 0xA8, 0x98, 0xAA, 0xBA, 0x9A,        # transfers not touching A
    0xD8, 0xF8,                                # CLD, SED
    0xEA,                                      # NOP
    0x85, 0x95, 0x8D, 0x9D, 0x99, 0x91,        # STA — stores A but
                                               # doesn't modify it
    0x84, 0x94, 0x8C,                          # STY
    0x86, 0x96, 0x8E,                          # STX
    0xA6, 0xB6, 0xAE, 0xBE, 0xA2,              # LDX
    0xA4, 0xB4, 0xAC, 0xBC, 0xA0,              # LDY
    0xE6, 0xF6, 0xEE, 0xFE,                    # INC mem
    0xC6, 0xD6, 0xCE, 0xDE,                    # DEC mem
    0xE0, 0xE4, 0xEC, 0xC0, 0xC4, 0xCC,        # CPX/CPY
}


def _walk_back_for_a_source(mem: bytearray, sorted_pcs: list[int],
                            sta_pc: int) -> tuple[str, int] | None:
    """Given the PC of a `STA …` instruction, walk backwards through
    the sorted reachable-PC list (linear predecessors) until we hit
    an LDA. Skip past A-neutral ops (CLC, INC mem, STA, LDX, LDY, ...).
    Returns (mode, abs_addr) for the LDA, or None if A's source is
    not a simple memory load (e.g. it came from a TXA / PLA / ASL).
    """
    i = sorted_pcs.index(sta_pc) if sta_pc in sorted_pcs else -1
    if i <= 0:
        return None
    while i > 0:
        i -= 1
        pc = sorted_pcs[i]
        op = mem[pc]
        if op in _LDA_MODES:
            mode = _LDA_MODES[op]
            if mode in ('zp', 'zp_x', 'ind_y'):
                return mode, mem[pc + 1]
            return mode, mem[pc + 1] | (mem[pc + 2] << 8)
        if op in _A_NEUTRAL:
            continue
        return None  # A was modified by something we don't track
    return None


def find_freq_tables(mem: bytearray, play_entry: int
                     ) -> tuple[int, int] | None:
    """Find the engine's freq_lo / freq_hi table addresses by tracing
    the data flow into V_FREQ_LO / V_FREQ_HI SID writes (no content
    heuristics).

    Approach:
      1. Trace all reachable code from `play_entry` (covers proc_note
         AND the per-frame block where SID writes happen).
      2. Find every `STA $D40N,X/Y` where N ∈ {0,7,$E} (V_FREQ_LO for
         V1/V2/V3) or N ∈ {1,8,$F} (V_FREQ_HI).
      3. Trace A backwards from the STA through predecessor instructions
         until we hit the originating LDA. The LDA's source is either:
           a) Directly an `LDA $abs,X` from the freq table — done.
           b) An intermediate voice-state load (`LDA $abs,Y`) — find
              the STA to that slot elsewhere in reachable code, then
              recurse: trace A backwards from that STA.
      4. Both lo and hi tables are found independently; they should
         turn out to be exactly 128 bytes apart in either order.

    Returns `(lo_base, hi_base)` or None if either trace fails.
    """
    pcs = sorted(_reachable_pcs(mem, play_entry))

    # Build the candidate STA-to-SID targets for V_FREQ_LO and V_FREQ_HI.
    LO_TARGETS = {0xD400, 0xD407, 0xD40E}
    HI_TARGETS = {0xD401, 0xD408, 0xD40F}

    def _find_freq_table(targets: set[int]) -> int | None:
        # Step 1: find a STA $D40N,X (opcode $9D) that writes to one of
        # the freq registers.
        for pc in pcs:
            if pc + 3 >= len(mem):
                continue
            if mem[pc] not in (0x9D, 0x99):    # STA abs,X / STA abs,Y
                continue
            tgt = mem[pc + 1] | (mem[pc + 2] << 8)
            if tgt not in targets:
                continue
            # Step 2: trace A backwards from this STA.
            src = _walk_back_for_a_source(mem, pcs, pc)
            if src is None:
                continue
            mode, addr = src
            if mode == 'abs_x':
                return addr  # direct lookup — found the table
            if mode in ('abs', 'abs_y'):
                # Indirect via a voice-state slot. Find the writer of
                # this slot somewhere in reachable code, then recurse.
                # We accept STA $abs (opcode $8D) or STA $abs,Y ($99)
                # writing to `addr`.
                for w_pc in pcs:
                    if w_pc + 3 >= len(mem):
                        continue
                    wop = mem[w_pc]
                    if wop not in (0x8D, 0x99):
                        continue
                    w_tgt = mem[w_pc + 1] | (mem[w_pc + 2] << 8)
                    if w_tgt != addr:
                        continue
                    src2 = _walk_back_for_a_source(mem, pcs, w_pc)
                    if src2 is None:
                        continue
                    mode2, addr2 = src2
                    if mode2 == 'abs_x':
                        return addr2
        return None

    lo = _find_freq_table(LO_TARGETS)
    hi = _find_freq_table(HI_TARGETS)
    if lo is None or hi is None:
        return None
    return lo, hi


def find_sub_jump_table(mem: bytearray, proc_note_addr: int,
                        zp_lo: int) -> int | None:
    """Find the address of the $E0..$EF orderlist sub-jump table.

    The $Ex handler in proc_note loads a new orderlist pointer from a
    lookup table indexed by (byte & $0F)*2. The pattern (Ninja_Hamster
    $C4D6-$C4E2):

        LDA ($F2),Y         ; reload the byte
        AND #$0F
        ASL A
        TAY
        LDA $tbl,Y          ; ← table lookup, lo
        STA $F2             ; ← writes ptr_lo zp
        LDA $tbl+1,Y        ; lookup, hi
        STA $F3             ; writes ptr_hi zp

    Dataflow approach: in proc_note's reachable code, find every
    `STA $zp_lo` (opcode $85 with operand = the per-voice scratch zp).
    Walk A's predecessor chain; if it traces to `LDA $abs,Y`, that
    abs is the table base.

    Tracing from `proc_note_addr` (not play_addr) excludes the play
    loop's per-voice setup blocks — those load the orderlist ptr from
    a per-voice abs slot (LDA abs, no index), not from an indexed
    table.
    """
    pcs = sorted(_reachable_pcs(mem, proc_note_addr))
    for pc in pcs:
        if pc + 1 >= len(mem): continue
        if mem[pc] != 0x85: continue       # STA $zp
        if mem[pc + 1] != zp_lo: continue
        src = _walk_back_for_a_source(mem, pcs, pc)
        if src is None: continue
        mode, addr = src
        if mode == 'abs_y':
            return addr
    return None


def find_instrument_base_table(mem: bytearray, entry: int
                               ) -> int | None:
    """Find the instrument-base lookup table.

    Each instrument is a 24-byte program. The engine doesn't store
    them in a regular array — note-start patches the source operand
    of an `LDA $abs,Y` instruction (the body of a 24-byte copy loop)
    before running it. The patching code reads the source address
    from an instrument-base table indexed by instrument byte:

        TAY                 ; Y = instrument byte
        LDA $base_lo,Y      ; instrument_base_lo[Y]
        STA $self_mod_pc+1  ; patch low byte of LDA source
        LDA $base_lo+1,Y    ; instrument_base_hi[Y] (interleaved)
        STA $self_mod_pc+2  ; patch high byte of LDA source
        ...                 ; (more setup)
        LDY #$17            ; 24-byte counter
   self_mod_pc:
        LDA $patched,Y      ; ← source addr is the self-modified value
        STA voice_state,Y
        DEY / BPL self_mod_pc

    Detect this pattern:
      1. Find the `LDY #$17` + `LDA $abs,Y / STA $abs2,Y / DEY / BPL`
         24-byte copy loop. The LDA's operand position is the
         self-mod target (PC+1, PC+2 from the LDA pc).
      2. Find the upstream `STA $self_mod_pc+1` / `STA $self_mod_pc+2`
         pair (opcode $8D with operand = the LDA's operand positions).
      3. Walk A's predecessor chain from each STA; should hit
         `LDA $base_tbl,Y` and `LDA $base_tbl+1,Y` respectively.
         The shared base (`$base_tbl`) is the instrument-base table.

    Returns the base address, or None if not found.
    """
    pcs = sorted(_reachable_pcs(mem, entry))

    # Step 1: find the per-instrument copy loop signature.
    # The instrument size varies per tune (Counterforce uses LDY #$0E
    # = 15 bytes, Ninja_Hamster uses LDY #$17 = 24 bytes). The shape
    # is LDY #imm followed within ~6 bytes by LDA $abs,Y (B9 lo hi).
    # imm is "size - 1", so an imm in roughly 7..31 matches plausible
    # instrument sizes (8..32 bytes).
    self_mod_lda_pc = None
    for pc in pcs:
        if pc + 5 >= len(mem): continue
        if mem[pc] != 0xA0: continue                     # LDY #imm
        if not (0x07 <= mem[pc + 1] <= 0x1F): continue
        for q in range(pc + 2, min(pc + 8, len(mem) - 3)):
            if mem[q] == 0xB9:                            # LDA $abs,Y
                self_mod_lda_pc = q
                break
        if self_mod_lda_pc is not None:
            inst_count_minus_1 = mem[pc + 1]
            break
    if self_mod_lda_pc is None:
        return None

    # Step 2: the LDA's operand bytes are at self_mod_lda_pc+1 (lo)
    # and self_mod_lda_pc+2 (hi). Find STAs that write to these
    # absolute addresses (opcode $8D = STA abs).
    sm_lo_addr = self_mod_lda_pc + 1
    sm_hi_addr = self_mod_lda_pc + 2
    sta_lo_pc = sta_hi_pc = None
    for pc in pcs:
        if pc + 2 >= len(mem): continue
        if mem[pc] != 0x8D: continue
        tgt = mem[pc + 1] | (mem[pc + 2] << 8)
        if tgt == sm_lo_addr:
            sta_lo_pc = pc
        elif tgt == sm_hi_addr:
            sta_hi_pc = pc
    if sta_lo_pc is None or sta_hi_pc is None:
        return None

    # Step 3: walk A back from each STA to its source LDA.
    src_lo = _walk_back_for_a_source(mem, pcs, sta_lo_pc)
    src_hi = _walk_back_for_a_source(mem, pcs, sta_hi_pc)
    if src_lo is None or src_hi is None:
        return None
    mode_lo, addr_lo = src_lo
    mode_hi, addr_hi = src_hi
    if mode_lo != 'abs_y' or mode_hi != 'abs_y':
        return None
    # Must be a paired lo/hi table — addresses 1 apart (interleaved).
    if addr_hi != addr_lo + 1:
        return None
    return addr_lo


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

    def _finalize(blocks: list[VoiceBlock], proc_note: int,
                  post_mem: bytes, loop_entry: int) -> EngineState:
        """Populate per-voice initial_ptr from post-init memory and
        return the final EngineState."""
        for vb in blocks:
            vb.initial_ptr = post_mem[vb.ptr_addr] | (
                post_mem[vb.ptr_addr + 1] << 8)
        return EngineState(
            load=load, init_addr=init_addr, play_addr=play_addr,
            proc_note_addr=proc_note, play_loop_entry=loop_entry,
            voices=blocks, post_init_mem=post_mem)

    # Always run init — we need post-init memory for table extraction
    # downstream anyway. 200k cycle budget; cheap relative to total
    # extract cost.
    post_mem, _, _, _ = _run_init_capture(sid_path, subtune)

    # Strategy 1+2: static scan against the raw binary, with up to 3
    # static trampoline peels.
    pc = play_addr
    static_err: Exception | None = None
    if play_addr != 0:
        for _ in range(4):
            try:
                blocks, proc_note = scan_voice_blocks(mem, pc)
                return _finalize(blocks, proc_note, post_mem, pc)
            except ValueError as e:
                static_err = e
                inner = _peel_trampoline(mem, pc)
                if inner is None or inner == pc:
                    break
                pc = inner

    # Strategy 3: resolve play via post-init memory, re-scan.
    resolved = _resolve_play_addr(post_mem, play_addr)
    if resolved == 0:
        raise ValueError(
            f'jay_derrett: init did not install a play vector '
            f'(play=$0000 still, $0314/$0315=$00)')
    pc = resolved
    for _ in range(4):
        try:
            blocks, proc_note = scan_voice_blocks(post_mem, pc)
            return _finalize(blocks, proc_note, post_mem, pc)
        except ValueError as e:
            inner = (_peel_trampoline(post_mem, pc)
                     or _peel_irq_handler(post_mem, pc))
            if inner is None or inner == pc:
                raise static_err or e
            pc = inner
    raise static_err or ValueError('jay_derrett: scan exhausted all strategies')


# ---------------------------------------------------------------------------
# Runtime simulation — capture which bytes each voice's orderlist ptr visits.
# ---------------------------------------------------------------------------

def _run_play_capture(sid_path: str, n_frames: int = 2000,
                      subtune: int = 0,
                      counter_addr: int | None = None,
                      stop_on_counter_wrap: bool = True
                      ) -> tuple[list[list[int]], bytearray, list[int]]:
    """Run init then call play() `n_frames` times in py65, recording
    each voice's orderlist pointer (`ptr_addr`/`ptr_addr+1`) after
    every play() call. Returns:

      - `trails`: list of length len(voices). `trails[i]` is the
        per-frame sequence of pointer values for voice i.
      - The final post-play memory.
      - `counter_trail`: per-frame value of the engine's self-mod
        $E counter (read from `counter_addr`, default = proc_note+$18
        which is the `CMP #imm` operand on jay_derrett). Used by the
        caller to detect song-loop closure (counter wrapping from
        ~$E9 back to $E0).

    If `stop_on_counter_wrap` is true and a counter value < the
    previous max is observed (the engine wrapped past $E9), the
    capture halts early to avoid re-capturing redundant loop
    iterations.

    Why static walk isn't enough: the engine's `$Ex` byte only fires
    when it equals a global self-mod counter that advances on each
    match. A voice's stream contains `$Ex` bytes that get skipped at
    runtime if the counter doesn't match yet — so the byte at which
    the songwriter "intended" pat 0 to end is not the first `$Ex`,
    but the first `$Ex` whose value equals the counter at the moment
    that voice processes it. Without simulation we don't know which
    `$Ex` is the active boundary.

    `n_frames=2000` covers ~40 seconds of music at 50 Hz, enough for
    most Type A songs to complete one full loop.
    """
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU

    # First: run init + scan to get the voice ptr addrs + the resolved
    # play address.
    state = load_state_from_sid(sid_path, subtune)
    post_mem = bytearray(state.post_init_mem)
    play_real = _resolve_play_addr(post_mem, state.play_addr)
    # DON'T peel the IRQ handler for runtime simulation. The peel
    # follows the FIRST JSR/JMP target from the IRQ entry, which is
    # typically the frame-skip branch (e.g. `JMP per_frame_block` on
    # the tempo-counter-non-zero path) — running only that branch
    # never advances the orderlist pointers. The full IRQ handler at
    # `play_real` runs both proc_note (which advances ptrs) and the
    # per-frame SID-write block, then RTSes back to our sentinel.

    ptr_addrs = [v.ptr_addr for v in state.voices]
    # Default counter_addr: the CMP #imm operand near the start of
    # proc_note. For Ninja_Hamster it's at proc_note+$18 ($C4D3).
    # The scanner doesn't pinpoint this slot; for now we hardcode the
    # offset and let the caller override per-tune if needed.
    if counter_addr is None:
        counter_addr = state.proc_note_addr + 0x18

    # Patch any `JMP $EA81` (KERNAL IRQ exit) in the play handler to
    # an RTS — KERNAL's exit sequence pulls A/X/Y + RTI from a 6-byte
    # IRQ stack frame our JSR doesn't provide. Patching to RTS lets
    # the handler return to our sentinel via the standard JSR stack.
    # Scan a 1KB window from play_real onward; replace any 4C 81 EA
    # sequence with 60 EA EA (RTS + 2 NOPs).
    for q in range(play_real, min(play_real + 1024, 0x10000 - 2)):
        if (post_mem[q] == 0x4C and post_mem[q + 1] == 0x81
                and post_mem[q + 2] == 0xEA):
            post_mem[q] = 0x60       # RTS
            post_mem[q + 1] = 0xEA   # NOP
            post_mem[q + 2] = 0xEA   # NOP

    mpu = MPU()
    mpu.memory = post_mem

    SENTINEL = 0x0200
    trails: list[list[int]] = [[] for _ in ptr_addrs]
    counter_trail: list[int] = []
    counter_max = mpu.memory[counter_addr]
    for _ in range(n_frames):
        # Plant sentinel return; call play() as a JSR-equivalent.
        mpu.sp = 0xFD
        mpu.memory[0x01FF] = (SENTINEL - 1) >> 8
        mpu.memory[0x01FE] = (SENTINEL - 1) & 0xFF
        mpu.pc = play_real
        # Run until RTS lands at sentinel. 50k cycle budget per frame
        # is generous (real PAL frame ~20k cycles).
        for _ in range(50000):
            if mpu.pc == SENTINEL:
                break
            mpu.step()
        for i, pa in enumerate(ptr_addrs):
            trails[i].append(mpu.memory[pa] | (mpu.memory[pa + 1] << 8))
        c = mpu.memory[counter_addr]
        counter_trail.append(c)
        if stop_on_counter_wrap and c < counter_max:
            # Counter wrapped past max — song-loop closure detected.
            break
        if c > counter_max:
            counter_max = c
    return trails, mpu.memory, counter_trail
