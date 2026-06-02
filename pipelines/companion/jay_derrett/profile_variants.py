"""Profile the Jay_Derrett engine family — variant taxonomy.

For each SID (25 total across MUSICIANS/D/Derrett_Jay, MUSICIANS/C/Clever_Music,
MUSICIANS/R/Raeburn_Gavin), extract:

- Load/init/play addresses (dispatch shape)
- Instrument program size (LDY #imm immediately before the copy loop)
- Voice_state base (STA dst in the copy loop)
- Self-mod counter init value (from running orig init in py65)
- Modulation block structure: where each voice's freq_lo/hi/PW/CTRL
  is read from (slab vs interleaved layout)
- Sub-jump table entry count (sizeof table — heuristic: 20 bytes
  expected, may differ)

Output: a per-SID record. Cluster by signature to identify variant
families.

Run: python3 -m pipelines.companion.jay_derrett.profile_variants
"""

from __future__ import annotations

import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))


@dataclass
class SidProfile:
    name: str
    sid_path: str
    load: int
    init_addr: int
    play_addr: int
    dispatch_shape: str
    # Copy loop info — None if not found
    copy_loop_addr: int | None = None
    program_size: int | None = None
    copy_dst: int | None = None          # Initial operand (may be self-mod'd at runtime)
    # Modulation block info — these are the SOURCE OF TRUTH for slot layout
    sta_d400_addrs: list[int] = field(default_factory=list)
    # Slot addresses extracted from the modulation block
    slot_freq_lo: int | None = None      # LDA $XXXX,Y → STA $D400,X (first such)
    slot_freq_hi: int | None = None      # → STA $D401,X
    slot_pw_hi: int | None = None        # → STA $D403,X
    slot_pw_lo: int | None = None        # → STA $D402,X
    slot_ctrl: int | None = None         # → STA $D404,X (often via ORA)
    slot_off_freq_lo: int | None = None  # alt-path freq lo (the second STA $D400,X)
    # Computed modulation base = slot_freq_lo - 1 (freq lo is at +1 in all known variants)
    mod_base: int | None = None
    voice_strides: list[int] | None = None  # [0, $1A, $34] or [0, $18, $30] etc.
    layout: str = 'unknown'
    # Init state (from py65 capture)
    init_smc: int | None = None
    init_master_vol: int | None = None
    has_irq_play: bool = False
    notes: list[str] = field(default_factory=list)


def _read_sid(sid_path: str) -> tuple[int, int, int, bytes, bytearray]:
    """Returns (load, init, play, body, mem) for the SID."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load_in = struct.unpack('>H', raw[8:10])[0]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    init_addr = struct.unpack('>H', raw[10:12])[0]
    play_addr = struct.unpack('>H', raw[12:14])[0]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    return load, init_addr, play_addr, body, mem


def _libsidplayfp_powerup_ram() -> bytearray:
    ram = bytearray(0x10000)
    byte = 0x00
    for j in range(0, 0x10000, 0x4000):
        for k in range(0x4000):
            ram[j + k] = byte
        byte ^= 0xFF
        for i in range(0x02, 0x4000, 0x08):
            for k in range(4):
                ram[j + i + k] = byte
    return ram


def _classify_dispatch(mem: bytearray, play_addr: int, load: int,
                       body_end: int) -> str:
    """Classify play handler's dispatch shape."""
    if play_addr == 0:
        return 'irq'
    op = mem[play_addr]
    if op == 0x4C:  # JMP abs
        target = mem[play_addr + 1] | (mem[play_addr + 2] << 8)
        if target == 0:
            return 'trampoline (JMP $0000 — sets self up)'
        return f'trampoline (JMP ${target:04X})'
    if op == 0x6C:  # JMP indirect
        target = mem[play_addr + 1] | (mem[play_addr + 2] << 8)
        return f'trampoline_indirect (JMP (${target:04X}))'
    if op == 0xEE:  # INC abs
        return 'direct (INC...DEC...BEQ)'
    if op == 0xCE:  # DEC abs (some engines skip frame counter INC)
        return 'direct_no_inc (DEC first)'
    return f'unknown (opcode ${op:02X})'


def _find_copy_loop(mem: bytearray, load: int, body_end: int) -> tuple[int, int, int] | None:
    """Find the instrument-loader copy loop: A0 SS B9 ?? ?? 99 LL HH 88 10 F7
    where SS = copy size - 1 (LDY #imm). Returns (loop_addr, prog_size, dst_base)."""
    for addr in range(load, body_end - 11):
        if (mem[addr] == 0xA0 and
            mem[addr + 2] == 0xB9 and
            mem[addr + 5] == 0x99 and
            mem[addr + 8] == 0x88 and
            mem[addr + 9] == 0x10 and
            mem[addr + 10] == 0xF7):
            size = mem[addr + 1] + 1  # LDY #imm; +1 because copy includes 0
            dst = mem[addr + 6] | (mem[addr + 7] << 8)
            return (addr, size, dst)
    # Without LDY #imm immediately preceding
    for addr in range(load, body_end - 9):
        if (mem[addr] == 0xB9 and mem[addr + 3] == 0x99 and
            mem[addr + 6] == 0x88 and mem[addr + 7] == 0x10 and
            mem[addr + 8] == 0xF7):
            dst = mem[addr + 4] | (mem[addr + 5] << 8)
            # Look back for LDY #imm
            size = None
            for back in range(1, 8):
                if mem[addr - back] == 0xA0:
                    size = mem[addr - back + 1] + 1
                    break
            return (addr, size, dst)
    return None


def _scan_sta_d400(mem: bytearray, load: int, body_end: int) -> list[int]:
    """Find all `9D 00 D4` (STA $D400,X) instructions."""
    out = []
    for addr in range(load, body_end - 2):
        if mem[addr] == 0x9D and mem[addr + 1] == 0x00 and mem[addr + 2] == 0xD4:
            out.append(addr)
    return out


def _analyze_freq_lo_source(mem: bytearray, sta_addr: int
                             ) -> tuple[int | None, str | None]:
    """Look at the byte sequence preceding STA $D400,X.
    Expected pattern: LDA $YYYY,Y (or ,X) just before.
    Returns (source_addr, indexing_register_letter)."""
    if sta_addr < 3:
        return None, None
    op = mem[sta_addr - 3]
    operand = mem[sta_addr - 2] | (mem[sta_addr - 1] << 8)
    if op == 0xB9:    # LDA abs,Y
        return operand, 'Y'
    if op == 0xBD:    # LDA abs,X
        return operand, 'X'
    if op == 0xAD:    # LDA abs (no index)
        return operand, '-'
    return None, None


def _detect_voice_strides(mem: bytearray, copy_loop_addr: int,
                          body_end: int) -> list[int] | None:
    """Find the voice stride table. For Ninja_Hamster:
    voice_y_table $C86B = [$00, $1A, $34].

    Heuristic: after the copy loop, the engine accesses voice state
    via Y (stride). The Y values come from `LDA stride_tbl,X / TAY`.
    Scan ~200 bytes around proc_note for `B9 ?? ?? A8` pattern
    (LDA abs,Y / TAY) — the operand is the stride table."""
    # Search from copy_loop_addr backwards/forwards
    for addr in range(max(0, copy_loop_addr - 500),
                      min(body_end - 4, copy_loop_addr + 500)):
        # Pattern: B9 LL HH A8 (LDA abs,Y / TAY)
        if mem[addr] == 0xB9 and mem[addr + 3] == 0xA8:
            tbl_addr = mem[addr + 1] | (mem[addr + 2] << 8)
            # Read 3 bytes — possible strides
            tbl = list(mem[tbl_addr:tbl_addr + 3])
            # Sanity check: first byte should be $00 (V0 stride)
            if tbl[0] == 0 and tbl[1] != 0 and tbl[2] != 0:
                return tbl
    return None


def _capture_init_state(sid_path: str, init_addr: int, smc_addr: int
                        ) -> tuple[int | None, int | None]:
    """Run orig init in py65; return (smc_init, master_vol_init)."""
    from py65.devices.mpu6502 import MPU
    load, _, _, body, _ = _read_sid(sid_path)
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = 0
    mpu.x = 0
    mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    try:
        for _ in range(2_000_000):
            if mpu.pc == 0xFEFF:
                break
            mpu.step()
    except Exception:
        return (None, None)
    smc = mpu.memory[smc_addr] if smc_addr else None
    mvol = mpu.memory[0xD418]
    return (smc, mvol)


def profile_sid(sid_path: str) -> SidProfile:
    name = Path(sid_path).stem
    try:
        load, init_addr, play_addr, body, mem = _read_sid(sid_path)
    except Exception as e:
        p = SidProfile(name=name, sid_path=sid_path, load=0, init_addr=0,
                       play_addr=0, dispatch_shape=f'READ-ERR {e}')
        return p
    body_end = load + len(body)
    dispatch = _classify_dispatch(mem, play_addr, load, body_end)
    p = SidProfile(name=name, sid_path=sid_path, load=load,
                   init_addr=init_addr, play_addr=play_addr,
                   dispatch_shape=dispatch,
                   has_irq_play=(play_addr == 0))

    # Copy loop / instrument size / copy dst
    cl = _find_copy_loop(mem, load, body_end)
    if cl:
        p.copy_loop_addr, p.program_size, p.copy_dst = cl

    # STA $D400,X locations
    p.sta_d400_addrs = _scan_sta_d400(mem, load, body_end)

    # Scan modulation block for every D40N write and the source it reads from.
    # Build slot_* by mapping STA's register to slot name.
    # The modulation block typically has:
    #   - 2x STA $D400 (normal + off-slide path)
    #   - 2x STA $D401 (matching freq hi)
    #   - 1x STA $D402 (PW lo from accum) and 1x STA $D403 (PW hi)
    #   - 1x STA $D404 (CTRL)
    slot_writes: dict[int, list[tuple[int, int]]] = {}  # reg → [(sta_addr, src)]
    for addr in range(load, body_end - 3):
        if mem[addr] == 0x9D and mem[addr + 2] == 0xD4:
            reg = mem[addr + 1]
            if addr >= 3 and mem[addr - 3] == 0xB9:  # LDA abs,Y
                src = mem[addr - 2] | (mem[addr - 1] << 8)
                slot_writes.setdefault(reg, []).append((addr, src))
    if 0x00 in slot_writes:
        # Two STA $D400,X — order by source addr (normal path < off-slide path
        # in NH; but in CF off-slide is at LOWER addr). Use the LATER STA addr
        # (= the second one encountered) as normal — heuristic.
        if len(slot_writes[0x00]) >= 2:
            srcs = sorted(slot_writes[0x00], key=lambda x: x[0])
            # Try smaller src — usually the off-slide is at LOWER source
            # offset relative to mod base. Take the larger src as normal:
            srcs_by_src = sorted(slot_writes[0x00], key=lambda x: x[1])
            p.slot_off_freq_lo = srcs_by_src[0][1]
            p.slot_freq_lo = srcs_by_src[1][1]
        else:
            p.slot_freq_lo = slot_writes[0x00][0][1]
    if 0x01 in slot_writes:
        srcs_by_src = sorted(slot_writes[0x01], key=lambda x: x[1])
        p.slot_freq_hi = srcs_by_src[-1][1]
    if 0x02 in slot_writes:
        p.slot_pw_lo = slot_writes[0x02][0][1]
    if 0x03 in slot_writes:
        p.slot_pw_hi = slot_writes[0x03][0][1]
    if 0x04 in slot_writes:
        p.slot_ctrl = slot_writes[0x04][0][1]
    # Modulation base = freq lo source - 1 (freq lo at +1 in all known variants)
    if p.slot_freq_lo:
        p.mod_base = p.slot_freq_lo - 1

    # Voice strides table
    if p.copy_loop_addr:
        p.voice_strides = _detect_voice_strides(mem, p.copy_loop_addr,
                                                body_end)

    # Layout classification (now simple: known engines are all slab)
    if p.voice_strides and p.voice_strides[1] >= 10:
        p.layout = 'slab'

    # Capture init state (smc + master_vol). Use scanner JSON for smc addr.
    jpath = ROOT / 'pipelines' / 'companion' / 'jay_derrett' / '_extracted' / f'{name}.json'
    smc_addr = None
    if jpath.exists():
        d = json.load(open(jpath))
        smc_addr = d.get('counter_addr')
    try:
        smc, mvol = _capture_init_state(sid_path, init_addr, smc_addr)
        p.init_smc = smc
        p.init_master_vol = mvol
    except Exception as e:
        p.notes.append(f'init-capture-err: {e}')

    return p


def _signature(p: SidProfile) -> str:
    """A compact signature for clustering."""
    return (f"{p.layout}|prog={p.program_size}|"
            f"strides={p.voice_strides}|"
            f"smc={p.init_smc:02X}" if p.init_smc else "smc=?" +
            f"|{p.dispatch_shape.split()[0]}")


def main():
    sid_paths = sorted(
        list((ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay').glob('*.sid'))
        + list((ROOT / 'hvsc84' / 'MUSICIANS' / 'C' / 'Clever_Music').glob('*.sid'))
        + list((ROOT / 'hvsc84' / 'MUSICIANS' / 'R' / 'Raeburn_Gavin').glob('Gun_Runner.sid')),
        key=lambda p: p.stem)
    # Filter out .sidfinity.sid rebuilds
    sid_paths = [p for p in sid_paths if 'sidfinity' not in p.stem]
    # Also filter to known Jay_Derrett family — query DB.
    import sqlite3
    db = sqlite3.connect(str(ROOT / 'hvsc84.db'))
    valid = set()
    for r in db.execute(
        "SELECT path FROM sids WHERE engine='Companion/Jay_Derrett'"):
        valid.add(r[0])
    sid_paths = [p for p in sid_paths
                 if str(p.relative_to(ROOT / 'hvsc84')).replace('\\', '/') in
                 {v.split('hvsc84/')[-1] if 'hvsc84/' in v else v for v in valid}
                 or any(p.name in v for v in valid)]

    profiles = []
    for sp in sid_paths:
        p = profile_sid(str(sp))
        profiles.append(p)

    def fmtH(v, w=4):
        return f"${v:0{w}X}" if v is not None else '?'.rjust(w + 1)
    def fmtB(v):
        return f"${v:02X}" if v is not None else '?'

    def slot_off(slot, base):
        if slot is None or base is None:
            return '?'
        return f'+${slot - base:02X}' if slot >= base else f'-${base - slot:02X}'

    print(f"{'name':24} {'load':>5} {'play':>5} {'dispatch':24} "
          f"{'prog':>4} {'mod_base':>9} {'fl':>4} {'fh':>4} {'pwh':>4} {'pwl':>5} {'ctrl':>5} {'ofl':>5} "
          f"{'strides':>14} {'smc':>3} {'mvol':>4}")
    print('-' * 152)
    for p in profiles:
        b = p.mod_base
        print(f"{p.name:24} "
              f"{fmtH(p.load)} {fmtH(p.play_addr)} "
              f"{p.dispatch_shape[:24]:24} "
              f"{p.program_size if p.program_size else '?':>4} "
              f"{fmtH(p.mod_base):>9} "
              f"{slot_off(p.slot_freq_lo, b):>4} "
              f"{slot_off(p.slot_freq_hi, b):>4} "
              f"{slot_off(p.slot_pw_hi, b):>4} "
              f"{slot_off(p.slot_pw_lo, b):>5} "
              f"{slot_off(p.slot_ctrl, b):>5} "
              f"{slot_off(p.slot_off_freq_lo, b):>5} "
              f"{str(p.voice_strides) if p.voice_strides else '?':>14} "
              f"{fmtB(p.init_smc):>3} "
              f"{fmtB(p.init_master_vol):>4}")

    # Cluster by slot layout signature (the load-bearing dimension for emit_asm)
    print()
    print('=== Clusters (by slot layout) ===')
    from collections import defaultdict
    clusters = defaultdict(list)
    def slot_sig(p):
        b = p.mod_base
        if b is None:
            return ('unknown',)
        def off(s):
            return None if s is None else s - b
        return (off(p.slot_freq_lo), off(p.slot_freq_hi), off(p.slot_pw_hi),
                off(p.slot_ctrl), off(p.slot_off_freq_lo),
                p.program_size, tuple(p.voice_strides) if p.voice_strides else None,
                p.dispatch_shape.split('(')[0].strip())
    for p in profiles:
        clusters[slot_sig(p)].append(p.name)
    for sig, names in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        print(f"\n[{len(names)}] sig={sig}")
        for n in sorted(names):
            print(f"    {n}")


if __name__ == '__main__':
    main()
