"""Layout-independent operand location for re-assembled / relocated DMC v4
players (the `player_code_mismatch` + `no_jumptable` residue).

The factory's primary path extracts via FIXED offsets from the canonical layout
and gates on a byte-compare to canon. Re-assembled variants move the routines
(and their operand sites), so the byte-compare fails and the fixed offsets read
garbage. This locates each table-read by its canonical OPCODE-SKELETON signature
— the sequence of opcodes around the read is relocation-invariant (opcodes don't
change when a routine moves), so matching it in the variant's traced code finds
the read wherever it now sits; the operand there is the table address.

Proven end-to-end on the `$1231` variant family (e.g. For_Domination_04, the SR
helper relocated to +$25A with the wave/filter/sector tables moved): all 11
table addresses located correctly (validated against the on-disk track/sector
chain) and the member extracts + builds. The verify gate is the safety net — a
mislocated operand yields a partial, never a false FULL.

Used by the factory as a FALLBACK when the canonical byte-compare path raises
player_code_mismatch / can't find a jump table at the canonical offsets.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'tools', 'py65_lib'))
from seed_disassembly import trace, _INST_LEN          # noqa: E402

# canonical instruction ADDRESSES that read each table (site-1 of the operand
# sites in factory._SITES); tunetab has two candidate read sites (init / setup).
_CANON_READ = {
    'tunetab':  [0x1050, 0x180D],
    'secp_lo':  [0x1102],
    'secp_hi':  [0x1107],
    'instr':    [0x1226],
    'wavectrl': [0x159B],
    'wavefreq': [0x15B8],
    'filtdef':  [0x1295],
}
# data tables the canon code references by absolute operand (no fixed read site)
_CANON_DATA = {'freq_lo': 0x1647, 'freq_hi': 0x16A7,
               'vibdepth': 0x1888, 'd417': 0x1018}
# the track-loop hook ($10DF): canon STA $1726,x (loop-to-0, track_loop_target
# =False); a JSR-hook variant reads the next track byte (=True). Located by
# opcode signature so a moved hook is still classified (verify gate is the net).
_CANON_LOOP_SITE = 0x10DF        # _LOOP_SITE in the factory

_CANON_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                           'dmc4_player_embedded_1000.bin')


def _instrs(mem: bytearray, init: int, play: int, entries=()) -> list:
    """[(addr, opcode, operand16|None)] for reachable instructions, sorted."""
    _c, starts, _l, _j = trace(bytes(mem), 0, init, play, entries)
    out = []
    for pc in sorted(starts):
        op = mem[pc]
        operand = (mem[pc + 1] | (mem[pc + 2] << 8)) if _INST_LEN[op] == 3 else None
        out.append((pc, op, operand))
    return out


_CANON_I = None


def _canon_instrs() -> list:
    global _CANON_I
    if _CANON_I is None:
        canon = open(_CANON_PATH, 'rb').read()
        cm = bytearray(0x10000)
        cm[0x1000:0x1000 + len(canon)] = canon
        _CANON_I = _instrs(cm, 0x1000, 0x1003, (0x1006, 0x1009))
    return _CANON_I


def _sig_at(addr: int, w: int):
    """Opcode-skeleton signature of a window centred on the instruction at
    `addr` (a canon read site). Returns (opcode_tuple, target_index)."""
    cI = _canon_instrs()
    idx = next((i for i, (a, o, v) in enumerate(cI) if a == addr), None)
    if idx is None:
        return None
    lo, hi = max(0, idx - w), min(len(cI), idx + w + 1)
    return tuple(cI[i][1] for i in range(lo, hi)), idx - lo


def _sig_op(addr: int, w: int):
    """Signature of the canon instruction whose OPERAND is `addr` (data tables
    with no fixed read site)."""
    cI = _canon_instrs()
    idx = next((i for i, (a, o, v) in enumerate(cI) if v == addr), None)
    if idx is None:
        return None
    lo, hi = max(0, idx - w), min(len(cI), idx + w + 1)
    return tuple(cI[i][1] for i in range(lo, hi)), idx - lo


def _locate_site(vI: list, vseq: list, sig):
    """The operand SITE (operand address) of the unique window in the variant's
    instruction stream matching `sig`. None if absent or ambiguous."""
    if not sig:
        return None
    opc, ti = sig
    n = len(opc)
    sites = set()
    for i in range(len(vseq) - n + 1):
        if tuple(vseq[i:i + n]) == opc:
            sites.add(vI[i + ti][0] + 1)
    return sites.pop() if len(sites) == 1 else None


def locate(mem: bytearray, base: int) -> dict | None:
    """Locate every DMC v4 table by opcode-skeleton signature in the player at
    `base`. Returns {op_instr, op_wavectrl, op_wavefreq, op_filtdef, op_tunetab,
    op_secp_lo, op_secp_hi, freq_lo_addr, freq_hi_addr, vibdepth_addr,
    d417_shadow_addr, track_loop_target} (operand SITES for the _SITES tables,
    absolute ADDRESSES for the data tables) or None if any required table can't
    be uniquely located. Verify-gated downstream."""
    vI = _instrs(mem, base, base + 3, (base + 6, base + 9))
    vseq = [o for a, o, v in vI]

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    sites = {}
    for name, cands in _CANON_READ.items():
        site = None
        for w in (6, 9, 12):
            for ca in cands:
                site = _locate_site(vI, vseq, _sig_at(ca, w))
                if site is not None:
                    break
            if site is not None:
                break
        if site is None:
            return None
        sites[name] = site
    data = {}
    for name, addr in _CANON_DATA.items():
        site = None
        for w in (6, 9, 12):
            site = _locate_site(vI, vseq, _sig_op(addr, w))
            if site is not None:
                break
        if site is None:
            return None
        data[name] = rd16(site)

    # track-loop hook: locate the canon STA $1726,x site; if found, the loop
    # uses the loop-to-0 form (track_loop_target=False), else the JSR form.
    loop_site = None
    for w in (6, 9, 12):
        loop_site = _locate_site(vI, vseq, _sig_at(_CANON_LOOP_SITE, w))
        if loop_site is not None:
            break
    track_loop_target = loop_site is None

    return {
        'op_instr': sites['instr'], 'op_wavectrl': sites['wavectrl'],
        'op_wavefreq': sites['wavefreq'], 'op_filtdef': sites['filtdef'],
        'op_tunetab': sites['tunetab'], 'op_secp_lo': sites['secp_lo'],
        'op_secp_hi': sites['secp_hi'],
        'freq_lo_addr': data['freq_lo'], 'freq_hi_addr': data['freq_hi'],
        'vibdepth_addr': data['vibdepth'], 'd417_shadow_addr': data['d417'],
        'track_loop_target': track_loop_target,
    }
