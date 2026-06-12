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
# instrument satellite sites: operand = $18F0 + offset
_INST_SAT = [(0x122B, 1), (0x1242, 2), (0x1358, 3), (0x1258, 6),
             (0x1289, 6), (0x12CD, 7), (0x12DD, 8), (0x12E3, 9),
             (0x123B, 10), (0x126A, 10), (0x127A, 10), (0x12E9, 10)]

# track-loop hook site: canonical = 9D 26 17 (STA $1726,x = loop to 0);
# the JSR $1042 variant reads the next track byte as the loop target.
_LOOP_SITE = 0x10DF
_LOOP_HOOK = bytes.fromhex('c8b1f89d261760')   # iny / lda ($f8),y / sta / rts

# regions masked out of the identity compare (per-song / leftovers)
_MASKED_RANGES = [
    (0x100C, 0x1050),    # player vars + copyright string
    (0x1647, 0x1707),    # freq tables (per-tune tuning, carried in USF)
    (0x1707, 0x170D),    # track ptr leftovers
    (0x1716, 0x17C0),    # state leftovers
    (0x18E8, 0x18F0),    # gap before instruments
]


class DMCV4Unsupported(Exception):
    def __init__(self, reason: str, detail: str = ''):
        self.reason = reason
        self.detail = detail
        super().__init__(f'{reason}: {detail}' if detail else reason)


def _load(sid_path: str):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return mem, s


def _rd16(mem, a):
    return mem[a] | (mem[a + 1] << 8)


def dmc_v4_config(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV4Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))

    if (s['load'], s['init'], s['play']) != (0x1000, 0x1000, 0x1003):
        raise DMCV4Unsupported(
            'nonstandard_vectors',
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")

    # ---- masked identity compare against the canonical player ----
    canon = open(_CANON_PATH, 'rb').read()
    masked = bytearray(0x1000)           # 1 = ignore, covers $1000-$1FFF
    for a, b in _MASKED_RANGES:
        for i in range(a, b):
            masked[i - 0x1000] = 1
    for sites in _SITES.values():
        for a in sites:
            masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    for a, _off in _FILT_SAT + _INST_SAT + _TUNE_SAT:
        masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    # track-loop hook probe (before the identity compare; the site is
    # masked and validated here instead)
    loop_target = False
    site = bytes(mem[_LOOP_SITE:_LOOP_SITE + 3])
    if site == bytes.fromhex('9d2617'):
        pass                                     # canonical loop-to-0
    elif site[0] == 0x20:                        # JSR hook
        hook_at = site[1] | (site[2] << 8)
        if bytes(mem[hook_at:hook_at + 7]) != _LOOP_HOOK:
            raise DMCV4Unsupported(
                'loop_hook_unknown',
                bytes(mem[hook_at:hook_at + 14]).hex())
        loop_target = True
    else:
        raise DMCV4Unsupported('loop_site_unknown', site.hex())
    for i in range(_LOOP_SITE, _LOOP_SITE + 3):
        masked[i - 0x1000] = 1
    # compare the player region $1000-$18E7 (code + fixed tables +
    # vibdepth); $18F0+ is song data
    for i in range(0x1000, 0x18E8):
        if masked[i - 0x1000]:
            continue
        if mem[i] != canon[i - 0x1000]:
            raise DMCV4Unsupported(
                'player_code_mismatch', f'first diff at ${i:04X}')

    # ---- operand consistency ----
    vals = {}
    for name, sites in _SITES.items():
        vs = {_rd16(mem, a) for a in sites}
        if len(vs) != 1:
            raise DMCV4Unsupported('operand_inconsistent',
                                   f'{name}: {sorted(hex(v) for v in vs)}')
        vals[name] = vs.pop()
    if vals['instr'] != 0x18F0:
        raise DMCV4Unsupported('nonstandard_instr_base', hex(vals['instr']))
    for a, off in _FILT_SAT:
        if _rd16(mem, a) != vals['filtdef'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'filtdef+{off}')
    for a, off in _TUNE_SAT:
        if _rd16(mem, a) != vals['tunetab'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'tunetab+{off}')
    for a, off in _INST_SAT:
        if _rd16(mem, a) != 0x18F0 + off:
            raise DMCV4Unsupported('operand_inconsistent', f'instr+{off}')
    if not (0x18F0 < vals['wavectrl'] < vals['wavefreq'] < vals['filtdef']
            <= vals['tunetab'] < vals['secp_lo'] < vals['secp_hi']):
        raise DMCV4Unsupported(
            'layout_disorder',
            ' '.join(f'{k}=${v:04X}' for k, v in sorted(vals.items())))

    # ---- vibdepth stays a family constant (freq tables are per-tune
    # tuning content, carried in USF) ----
    if bytes(mem[0x1888:0x1888 + 96]) != VIBDEPTH:
        raise DMCV4Unsupported('custom_vibdepth')

    # ---- leftover-state probes ----
    # ($100F-$1011 gate-mask leftovers are CAPTURED by the extract as
    # init voice_state gate_mask priming — no flag needed.)
    if mem[0x1019]:
        raise DMCV4Unsupported('dual_parity_leftover', hex(mem[0x1019]))
    # (the idle wave walk from table index 0 is carried explicitly as
    # wave_programs[0] — record 0's wave_start no longer matters)

    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        op_instr=0x1227, op_wavectrl=0x159C, op_wavefreq=0x15B9,
        op_filtdef=0x1296, op_tunetab=0x1051,
        op_secp_lo=0x1103, op_secp_hi=0x1108,
        track_loop_target=loop_target,
    )
