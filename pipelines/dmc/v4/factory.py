"""DMC V4 config factory — `dmc_v4_config(sid_path)`.

Validates that a SID carries the canonical V4 player and derives its
DMCV4Config. Raises `DMCV4Unsupported(reason)` with a typed reason
bucket otherwise (FC factory-hygiene lesson: typed flags, never
silent misbuilds).

Identity probe = masked byte-compare of the player region against the
canonical carved binary (pipelines/dmc/docs/dmc4_player_embedded_1000.bin):
code + fixed tables must match EXACTLY except the packer-patched
operand positions, the per-song variables block, the copyright string
and the state leftovers. Multi-site operands (the packer patches the
same table address at several LDA abs,y sites) must agree with each
other — inconsistency = shifted/custom code (e.g. On_My_Way_to_X).

Leftover-state probes: the work-file image ships bytes the original
init never clears. The ones the play stream can read are either
captured ($1012-$1014 idle notes, $1018 routing shadow — both already
modeled) or flagged when non-default ($100F-$1011 gate masks, $1019
dual parity, record-0 wave_start with an idling voice).
"""
from __future__ import annotations

import os

from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.engine_constants import VIBDEPTH

_CANON_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                           'dmc4_player_embedded_1000.bin')
# Family-2 reference (carved from DEMOS/G-L/Kajun_Klog.sid, $1000-$17B0):
# the V4-derived build with the relocated instrument table ($17B0) and the
# $FF-terminator sector encoding. The play body + effect chain are
# canon-compatible, but the init / note-init tail / gate-off / hard-restart
# / rest dispatch / sector decoder differ — so family-2 members compare
# against THIS reference, not canon. See pipelines/dmc/family2/RE_NOTES.md.
_FAMILY2_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                             'dmc4_family2_player_1000.bin')
_F2_INSTR_BASE = 0x17B0      # code/data boundary (instr table base @ $1000)
# family-2 data regions masked out of the identity compare (per-tune /
# leftovers): vars + copyright, then freq tables + state up to the instr
# table. The code is one contiguous run $1037-$1644.
_F2_DATA_MASK = [(0x100C, 0x1037), (0x1647, _F2_INSTR_BASE)]

# packer-patched operand sites: name -> list of operand addresses
# (each site = 2 bytes lo/hi); per name all sites must agree
# (filter sites are filtdef + a fixed per-site offset).
_SITES = {
    'tunetab':  [0x1051, 0x180E],
    'secp_lo':  [0x1103],
    'secp_hi':  [0x1108],
    'instr':    [0x1227],
    'wavectrl': [0x159C, 0x15D9],
    'wavefreq': [0x15B9, 0x15FB],
    'filtdef':  [0x1296],
}
# filtdef satellite sites: operand = filtdef + offset
_FILT_SAT = [(0x12AC, 1), (0x12B2, 2), (0x12B8, 3), (0x13E7, 4), (0x13ED, 10)]
# tunetab satellite sites: operand = tunetab + 1 (the hi-byte reads)
_TUNE_SAT = [(0x1057, 1), (0x1814, 1)]

# 2ENTRY layout: the restructured-init regions that differ from canon
# (the play body matches, so masking these lets the canon identity
# compare pass). The 2-entry reads the tune table at $180E (tune setup,
# also a canon site) rather than canon's $1051 init-tail site.
_V2ENTRY_MASK = [(0x1000, 0x100C), (0x1050, 0x10B0), (0x162F, 0x1647),
                 (0x17EC, 0x17FB), (0x184B, 0x187E)]
_V2ENTRY_TUNETAB_SITE = 0x180E
_V2ENTRY_TUNE_SAT = [(0x1814, 1)]
# instrument satellite sites: operand = $18F0 + offset
_INST_SAT = [(0x122B, 1), (0x1242, 2), (0x1358, 3), (0x1258, 6),
             (0x1289, 6), (0x12CD, 7), (0x12DD, 8), (0x12E3, 9),
             (0x123B, 10), (0x126A, 10), (0x127A, 10), (0x12E9, 10)]

# track-loop hook site: canonical = STA $1726,x (loop to 0); the JSR
# hook variant reads the next track byte as the loop target. Both
# operands relocate with base. (hook signature: iny / lda ($f8),y /
# sta $1726,x / rts — validated inline, relocation-aware.)
_LOOP_SITE = 0x10DF

# regions masked out of the identity compare (per-song / leftovers /
# dead-code gaps). The gap fragments are unreachable padding between
# routines that nonetheless carry relocated operands (e.g. a dead
# JMP $110C / STA $1975) the trace never reaches — never executed, so
# they don't affect the writelog; masking keeps the compare reloc-clean.
_MASKED_RANGES = [
    (0x100C, 0x1050),    # player vars + copyright string
    (0x110F, 0x1113),    # dead-code gap
    (0x119A, 0x11A2),    # dead-code gap (holds a dead JMP $110C)
    (0x131B, 0x1322),    # dead-code gap
    (0x162F, 0x1647),    # all-off (+$06) + sfx (+$09) routines — these are
                         # the PSID sub-entries, NEVER executed during play()
                         # (the verify only drives the play vector), so their
                         # per-build variation is irrelevant to the write
                         # stream. Sub-builds re-author them freely.
    (0x1647, 0x1707),    # freq tables (per-tune tuning, carried in USF)
    (0x1707, 0x170D),    # track ptr leftovers
    (0x1716, 0x17C0),    # state leftovers
    (0x17C3, 0x17C5),    # dead-code gap
    (0x187E, 0x1885),    # dead-code gap (holds a dead STA $1975)
    (0x18E8, 0x18F0),    # gap before instruments
]


class DMCV4Unsupported(Exception):
    def __init__(self, reason: str, detail: str = ''):
        self.reason = reason
        self.detail = detail
        super().__init__(f'{reason}: {detail}' if detail else reason)


# Canon's self-referencing operands: every 3-byte instruction whose
# 16-bit operand points into the fixed player region [$1000,$1900)
# (code, RAM state, freq/vibdepth tables) relocates with base. Computed
# once by tracing the canonical player; used to relocate the reference
# image so the identity compare is base-invariant.
_RELOC_INSTRS = None      # list[(pc, operand_value)]


def _canon_reloc_instrs():
    global _RELOC_INSTRS
    if _RELOC_INSTRS is not None:
        return _RELOC_INSTRS
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import trace, _INST_LEN
    canon = open(_CANON_PATH, 'rb').read()
    mem = bytearray(0x10000)
    mem[0x1000:0x1000 + len(canon)] = canon
    # trace both the loop-to-0 player AND the +$006 / +$009 entries
    # (all-off, sfx) so every reachable instruction is covered.
    _c, starts, _l, _j = trace(bytes(mem), 0, 0x1000, 0x1003, (0x1006, 0x1009))
    out = []
    for pc in sorted(starts):
        if pc < 0x1000 or pc + 2 >= 0x1000 + len(canon):
            continue
        if _INST_LEN[mem[pc]] == 3:
            val = mem[pc + 1] | (mem[pc + 2] << 8)
            if 0x1000 <= val < 0x1900:
                out.append((pc, val))
    _RELOC_INSTRS = out
    return out


_F2_REF = None      # (ref_bytes, masked[], reloc_instrs)


def _family2_ref():
    """Trace the carved family-2 reference once: return its byte image,
    the compare mask (1 = ignore: data regions + per-song operand bytes +
    non-reachable bytes), and the self-ref operand list (relocates with
    base). Mirrors _canon_reloc_instrs but reachable-instruction-precise."""
    global _F2_REF
    if _F2_REF is not None:
        return _F2_REF
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import trace, _INST_LEN
    ref = bytearray(open(_FAMILY2_PATH, 'rb').read())   # $1000-$17B0
    mem = bytearray(0x10000)
    mem[0x1000:0x1000 + len(ref)] = ref
    # entries: init $1037 / play $1085 / all-off $162F / sfx $163E
    _c, starts, _l, _j = trace(bytes(mem), 0, 0x1037, 0x1085, (0x162F, 0x163E))
    masked = bytearray([1]) * _F2_INSTR_BASE        # default: ignore
    reloc = []
    for pc in sorted(starts):
        if pc < 0x1000 or pc >= _F2_INSTR_BASE:
            continue
        L = _INST_LEN[mem[pc]]
        if pc + L > _F2_INSTR_BASE:
            continue
        for i in range(pc, pc + L):
            masked[i] = 0                           # compare this code byte
        if L == 3:
            op = mem[pc + 1] | (mem[pc + 2] << 8)
            if _F2_INSTR_BASE <= op < 0x1C00:
                masked[pc + 1] = masked[pc + 2] = 1  # per-song table operand
            elif 0x1000 <= op < _F2_INSTR_BASE:
                reloc.append((pc, op))               # self-ref (relocates)
    # data regions + the jump table (validated separately) are never code
    for a, b in _F2_DATA_MASK + [(0x1000, 0x100C)]:
        for i in range(a, b):
            masked[i] = 1
    _F2_REF = (ref, masked, reloc)
    return _F2_REF


def _load(sid_path: str):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    import struct
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    raw = open(sid_path, 'rb').read()
    s['speed'] = struct.unpack('>I', raw[18:22])[0]   # PSID speed bitmask
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return mem, s


def _rd16(mem, a):
    return mem[a] | (mem[a + 1] << 8)


def _cia_period_from_init(sid_path: str, subtune: int,
                          max_cycles: int = 3_000_000) -> int:
    """Run the PSID init in py65 and read the CIA1 timer A latch
    ($DC04/$DC05) the wrapper programs — the multispeed play rate.
    Returns 0 if init never returns or programs no timer."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mpu = MPU()
    mem = ObservableMemory()
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem
    mpu.stPush(0x00)
    mpu.stPush(0x00)               # RTS sentinel -> PC = $0001
    mpu.pc = s['init']
    mpu.a = subtune
    mpu.x = mpu.y = 0
    for _ in range(max_cycles):
        if mpu.pc == 0x0001:
            break
        try:
            mpu.step()
        except Exception:
            return 0
    else:
        return 0
    return mem[0xDC04] | (mem[0xDC05] << 8)


# canon-path failures that signal a re-assembled / moved layout the
# dataflow extractor can recover (the player IS a DMC v4, just relocated
# internally). Verify-gated downstream — a mislocation yields a partial.
_DATAFLOW_RETRY = {'player_code_mismatch', 'loop_site_unknown',
                   'loop_hook_unknown', 'operand_inconsistent',
                   'layout_disorder', 'nonstandard_instr_base'}


def dmc_v4_config(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV4Config:
    """Primary canonical-layout build; on a moved-layout rejection, fall back
    to the layout-independent dataflow extractor (pipelines.dmc.v4.dataflow)."""
    try:
        return _build_via_canon(sid_path, hvsc_root)
    except DMCV4Unsupported as e:
        if e.reason not in _DATAFLOW_RETRY:
            raise
        cfg = _build_via_dataflow(sid_path, hvsc_root)
        if cfg is None:
            raise
        return cfg


def _build_via_dataflow(sid_path: str, hvsc_root: str):
    """Build a config by locating every table via opcode-skeleton signatures
    (handles re-assembled players whose routines + operand sites moved). Returns
    None if the base or any table can't be located; the verify gate is the net."""
    from pipelines.dmc.v4 import dataflow
    mem, s = _load(os.path.join(hvsc_root, sid_path))
    load = s['load']

    def _jt(b):
        return (0 < b and load <= b and b + 6 < 0x10000 and mem[b] == 0x4C
                and mem[b + 3] == 0x4C and (mem[b + 1] | (mem[b + 2] << 8)) == b + 0x1D)
    base = next((b for b in (s['play'] - 3, load) if _jt(b)), None)
    if base is None:
        hi = min(0x10000, load + len(s['payload']))
        base = next((b for b in range(load, hi - 6) if _jt(b)), None)
    if base is None:
        return None
    loc = dataflow.locate(mem, base)
    if loc is None:
        return None
    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base, cia_period=0, extra_params={}, **loc)


def _build_via_canon(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV4Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))

    # ---- base detection. The canonical jump table is `JMP base+$1D /
    # JMP base+$85` (init / play handlers). Normally play = base+3, but a
    # multispeed / CIA wrapper member's play vector points to its own
    # dispatcher while the real player sits at the LOAD address. So try
    # play-3 first (clean relocations), then load. Relocation is
    # extract-only (the composer always emits at $1000; the writelog is
    # base-independent — the original's wrapper init/play are captured
    # as-is by the verify, handled by Check A + per-IRQ for CIA). ----
    # Two jump-table layouts share the same play body but wire init
    # differently. CANONICAL: `JMP base+$1D / JMP base+$85` (4-entry).
    # 2ENTRY: `JMP base+$807 / JMP base+$50` (2-entry table, restructured
    # init — ~621 members; the play body is byte-identical to canon, only
    # the init/dispatch/all-off regions differ, and we emit our own init).
    def _jt_layout(b):
        if not (0 < b and s['load'] <= b and b + 0x8E7 < 0x10000
                and mem[b] == 0x4C and mem[b + 3] == 0x4C):
            return None
        e0 = mem[b + 1] | (mem[b + 2] << 8)
        e1 = mem[b + 4] | (mem[b + 5] << 8)
        if e0 == b + 0x1D and e1 == b + 0x85:
            return 'canonical'
        if e0 == b + 0x807 and e1 == b + 0x50:
            return '2entry'
        # family 2: init $37 / play $85 (the distinctive signature). Some
        # builds wire all 4 entries (all-off $62F / sfx $63E), others only
        # init+play (the rest of $1006-$100B zeroed). The masked identity
        # compare validates the actual player either way, so init+play is
        # enough to dispatch.
        if e0 == b + 0x37 and e1 == b + 0x85:
            return 'family2'
        return None

    base = layout = None
    for b in (s['play'] - 3, s['load']):
        layout = _jt_layout(b)
        if layout:
            base = b
            break
    if base is None:
        # relocated-WITHIN-file: the player sits at neither play-3 nor
        # load — typically a CIA/multispeed wrapper whose dispatcher is at
        # play/load while the real player is elsewhere in the image. Scan
        # for the first valid jump-table signature; the masked identity
        # compare then validates it (a spurious 4C..4C match fails the
        # compare cleanly as player_code_mismatch).
        lo = s['load']
        hi = min(0x10000, lo + len(s['payload']))
        for b in range(lo, hi - 0x12):
            if mem[b] == 0x4C and mem[b + 3] == 0x4C:
                lay = _jt_layout(b)
                if lay:
                    base, layout = b, lay
                    break
    if base is None:
        b = s['play'] - 3
        reason = ('no_jumptable' if 0 < b and s['load'] <= b
                  else 'nonstandard_vectors')
        raise DMCV4Unsupported(
            reason,
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    # A wrapper member (play != base+3) drives the canonical player from a
    # separate dispatcher. When the PSID speed bit is set, that dispatcher
    # is a CIA-timer multispeed driver (~2-6x): the music plays faster, so
    # the rebuild must run at the same CIA rate. Recover the timer latch
    # the wrapper programs by running its init in py65 — the composer
    # emits the same latch + speed bit (see config.cia_period).
    cia_period = 0
    if s['play'] != base + 3 and (s.get('speed', 0) & 1):
        cia_period = _cia_period_from_init(
            os.path.join(hvsc_root, sid_path), s['start'] - 1)
        if not (0x0100 <= cia_period <= 0xFFFF):
            raise DMCV4Unsupported(
                'cia_multispeed',
                f"play=${s['play']:04X} CIA latch=${cia_period:04X} (unreadable)")
    delta = base - 0x1000

    def at(canon_addr):                 # canonical $1xxx addr -> mem index
        return canon_addr + delta

    def reloc(operand_val):             # canonical abs value -> relocated
        return operand_val + delta

    if layout == 'family2':
        return _family2_build(mem, s, sid_path, base, delta, at, cia_period)

    # ---- masked identity compare against the RELOCATED canonical
    # player. Build the reference image: canon with every self-ref
    # operand (code/RAM/table addresses) shifted by delta. ----
    canon = bytearray(open(_CANON_PATH, 'rb').read())
    if delta:
        for pc, val in _canon_reloc_instrs():
            nv = (val + delta) & 0xFFFF
            canon[pc - 0x1000 + 1] = nv & 0xFF
            canon[pc - 0x1000 + 2] = nv >> 8
    # layout-local site/satellite maps (the 2-entry play body uses the
    # canon sites; only the init-region tunetab access + the masked
    # init regions differ).
    sites_map = dict(_SITES)
    tune_sat = _TUNE_SAT
    mask_ranges = _MASKED_RANGES
    if layout == '2entry':
        sites_map = dict(_SITES, tunetab=[_V2ENTRY_TUNETAB_SITE])
        tune_sat = _V2ENTRY_TUNE_SAT
        mask_ranges = _MASKED_RANGES + _V2ENTRY_MASK
    masked = bytearray(0x1000)           # 1 = ignore, indexed by canon offset
    for a, b in mask_ranges:
        for i in range(a, b):
            masked[i - 0x1000] = 1
    for sites in sites_map.values():
        for a in sites:
            masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    for a, _off in _FILT_SAT + _INST_SAT + tune_sat:
        masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    # track-loop hook probe: the site holds STA (base+$726),x in the
    # canonical player; a JSR-hook variant reads the next track byte as
    # the loop target. Both operands relocate with base.
    loop_target = False
    op = mem[at(_LOOP_SITE)]
    if op == 0x9D and _rd16(mem, at(_LOOP_SITE) + 1) == reloc(0x1726):
        pass                                     # canonical loop-to-0
    elif op == 0x20:                             # JSR hook
        hook_at = _rd16(mem, at(_LOOP_SITE) + 1)
        ok = (bytes(mem[hook_at:hook_at + 4]) == bytes.fromhex('c8b1f89d')
              and _rd16(mem, hook_at + 4) == reloc(0x1726)
              and mem[hook_at + 6] == 0x60)
        if not ok:
            raise DMCV4Unsupported(
                'loop_hook_unknown', bytes(mem[hook_at:hook_at + 14]).hex())
        loop_target = True
    else:
        raise DMCV4Unsupported(
            'loop_site_unknown',
            bytes(mem[at(_LOOP_SITE):at(_LOOP_SITE) + 3]).hex())
    for i in range(_LOOP_SITE, _LOOP_SITE + 3):
        masked[i - 0x1000] = 1
    # ---- canon sub-build knob probes: variants that either map to an
    # existing composer knob or emit the same writes. Each masks its site
    # so the variant passes the compare; the verify is the safety net. ----
    extra = {}
    # rest/switch/slide-tail dispatch ($1180): canon JMP $1322 (run
    # effects); a sub-build JMP $1591 (wavestep) — the modulators hold one
    # frame at each tie (the family-2 rest_effects='skip' behavior).
    if mem[at(0x1180)] == 0x4C:
        tgt = _rd16(mem, at(0x1180) + 1)
        if tgt == reloc(0x1591):
            extra['rest_effects'] = 'skip'
        elif tgt != reloc(0x1322):
            raise DMCV4Unsupported('rest_dispatch_unknown', hex(tgt))
        for i in range(0x1180, 0x1183):
            masked[i - 0x1000] = 1
    # filter $D418 write ($12A8): canon inline STA $D418; a sub-build JSRs
    # a helper that does STA $D418 (+ a dead store) — identical write.
    if mem[at(0x12A8)] == 0x20:
        h = _rd16(mem, at(0x12A8) + 1)
        if not any(mem[h + k] == 0x8D
                   and (mem[h + k + 1] | (mem[h + k + 2] << 8)) == 0xD418
                   for k in range(9)):
            raise DMCV4Unsupported('filter_write_helper_unknown', hex(h))
        for i in range(0x12A8, 0x12AB):
            masked[i - 0x1000] = 1
    # compare the player region (code + fixed tables + vibdepth);
    # operand BYTES are masked (they relocate); the surrounding opcodes
    # are base-invariant and must match canonical exactly.
    for i in range(0x1000, 0x18E8):
        if masked[i - 0x1000]:
            continue
        if mem[at(i)] != canon[i - 0x1000]:
            raise DMCV4Unsupported(
                'player_code_mismatch', f'first diff at ${i:04X}')

    # ---- operand consistency (relocated absolute values) ----
    vals = {}
    for name, sites in sites_map.items():
        vs = {_rd16(mem, at(a)) for a in sites}
        if len(vs) != 1:
            raise DMCV4Unsupported('operand_inconsistent',
                                   f'{name}: {sorted(hex(v) for v in vs)}')
        vals[name] = vs.pop()
    if vals['instr'] != reloc(0x18F0):
        raise DMCV4Unsupported('nonstandard_instr_base', hex(vals['instr']))
    for a, off in _FILT_SAT:
        if _rd16(mem, at(a)) != vals['filtdef'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'filtdef+{off}')
    for a, off in tune_sat:
        if _rd16(mem, at(a)) != vals['tunetab'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'tunetab+{off}')
    for a, off in _INST_SAT:
        if _rd16(mem, at(a)) != reloc(0x18F0) + off:
            raise DMCV4Unsupported('operand_inconsistent', f'instr+{off}')
    if not (reloc(0x18F0) < vals['wavectrl'] < vals['wavefreq']
            < vals['filtdef'] <= vals['tunetab'] < vals['secp_lo']
            < vals['secp_hi']):
        raise DMCV4Unsupported(
            'layout_disorder',
            ' '.join(f'{k}=${v:04X}' for k, v in sorted(vals.items())))

    # ---- vibdepth stays a family constant (freq tables are per-tune
    # tuning content, carried in USF). Bytes 0-5 OVERLAP the player code
    # ($1888-$188D) so they relocate; only 6-95 are real vibrato data.
    # (the composer emits the canonical curve incl. 0-5; an octave-0
    # vibrato note on a relocated member is the rare exception the
    # verify gate would flag — not worth carrying.) ----
    if bytes(mem[at(0x1888) + 6:at(0x1888) + 96]) != VIBDEPTH[6:]:
        raise DMCV4Unsupported('custom_vibdepth')

    # ---- leftover-state probes ----
    # ($100F-$1011 gate masks and the $1019 dual-clock phase are
    # CAPTURED by the extract as priming — no flags needed.)
    # (the idle wave walk from table index 0 is carried explicitly as
    # wave_programs[0] — record 0's wave_start no longer matters)

    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(sites_map['tunetab'][0]),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1018),
        track_loop_target=loop_target, cia_period=cia_period,
        extra_params=extra,
    )


def _family2_build(mem, s, sid_path, base, delta, at, cia_period):
    """Family-2 config: masked identity compare vs the carved family-2
    reference (relocation-aware), then derive the packer-patched table
    addresses from the canon-compatible operand sites. The 5 family-2
    write-stream params (cymbal_onset / vib_ramp / hold_gateoff /
    hard_restart / rest_effects) are emitted by the extract whenever
    sector_format=='family2' — see pipelines/dmc/v4/extract/to_usf.py."""
    ref, masked, reloc = _family2_ref()
    canon = bytearray(ref)
    if delta:
        for pc, val in reloc:
            nv = (val + delta) & 0xFFFF
            canon[pc - 0x1000 + 1] = nv & 0xFF
            canon[pc - 0x1000 + 2] = nv >> 8
    # the holding gate-off ($133D) varies across family-2 sub-builds: some
    # builds inline STA $100f,x (mask only), others JSR a helper that also
    # clears AD/SR=$00 (the relocated sub_17EC). Probe it; mask its 3 bytes
    # out of the code compare. (Other knobs stay validated by the compare;
    # a sub-build that varies them is rejected with a typed reason.)
    probe = set(range(0x133D, 0x1340))    # hold_gateoff variant
    probe |= set(range(0x129F, 0x12A1))   # filter-mode-extract variant
    for i in range(0x1000, _F2_INSTR_BASE):
        if masked[i] or i in probe:
            continue
        if mem[at(i)] != canon[i - 0x1000]:
            raise DMCV4Unsupported('player_code_mismatch_f2',
                                   f'first diff at ${i:04X}')
    # $129F filter-mode extraction: Kajun masks `AND #$0F`; a re-assembly
    # variant uses `STA $9E` (a dead store — the following ASL x4 discards
    # the hi nibble either way, so $D418 is identical). Both equivalent.
    fmop = mem[at(0x129F)]
    if not ((fmop == 0x29 and mem[at(0x129F) + 1] == 0x0F) or fmop == 0x85):
        raise DMCV4Unsupported('filter_mode_variant', hex(fmop))
    gop = mem[at(0x133D)]
    if gop == 0x9D:                       # STA $100f,x — mask only
        hold_gateoff = 'mask_only'
    elif gop == 0x20:                     # JSR helper — clears AD/SR=$00
        hold_gateoff = 'adsr_clear'
    else:
        raise DMCV4Unsupported('hold_gateoff_unknown', hex(gop))
    # packer-patched table addresses (canon-compatible sites; tunetab via
    # $1051 since family 2 leaves the $180E site empty; instr base $17B0).
    instr = _rd16(mem, at(0x1227))
    wavectrl = _rd16(mem, at(0x159C))
    wavefreq = _rd16(mem, at(0x15B9))
    filtdef = _rd16(mem, at(0x1296))
    tunetab = _rd16(mem, at(0x1051))
    secp_lo = _rd16(mem, at(0x1103))
    secp_hi = _rd16(mem, at(0x1108))
    if not (base + 0x600 <= instr < base + 0x1000):
        raise DMCV4Unsupported('nonstandard_instr_base_f2', hex(instr))
    if not (instr < wavectrl < wavefreq < filtdef < tunetab
            < secp_lo < secp_hi):
        raise DMCV4Unsupported(
            'layout_disorder_f2',
            f'instr=${instr:04X} wc=${wavectrl:04X} wf=${wavefreq:04X} '
            f'fd=${filtdef:04X} tt=${tunetab:04X} '
            f'sl=${secp_lo:04X} sh=${secp_hi:04X}')
    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(0x1051),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1034),
        track_loop_target=False, cia_period=cia_period,
        sector_format='family2',
        extra_params={'cymbal_onset': 1, 'vib_ramp': 'step',
                      'hold_gateoff': hold_gateoff, 'hard_restart': 'none',
                      'rest_effects': 'skip'},
    )
