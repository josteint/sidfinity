#!/usr/bin/env python3
"""pattern_stream_verify.py — USF roundtrip verifier for pattern data.

Extracts USF from a SID via the engine's to_usf path, then re-emits
SID bytes via the composer. Compares the rebuilt pattern-stream region
byte-by-byte against HVSC's. Any mismatch means USF lost information
during extraction (lossy extract) or the composer mishandled the
re-emission (lossy compose).

For FC family this is trivially satisfied today because patterns
emit verbatim from HVSC mem — the rebuilt SID bytes in the pattern
region are bit-identical. But this tool catches regressions if:
  - A future change starts USF-encoding patterns as a structured
    field (with possible round-trip loss).
  - A composer modification accidentally writes through a derived
    pattern table instead of the verbatim source (e.g., the
    pointer-fixup in _fixup_verbatim_pointers — was bug-prone in
    Phase 2 of the symbolic data layout).

For Hubbard '85 / Companion engines where USF encodes patterns
structurally, this tool would catch real extraction bugs.

Usage:
    python3 pipelines/future_composer/pattern_stream_verify.py --engine ENGINE
    python3 pipelines/future_composer/pattern_stream_verify.py --all   # all canaries

Output:
    For each engine: number of pattern bytes verified, number of
    mismatches, and the FIRST mismatching offset (with neighboring
    bytes) if any.

Exit code: 0 if all verified, 1 if any mismatch.
"""
from __future__ import annotations

import argparse
import importlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# Known canaries with their pattern region ranges. The pattern region
# is the contiguous byte range in HVSC's load image that holds pattern
# data (and seq streams) — for FC, this is the "verbatim tail" after
# the USF-emitted sections.
_CANARIES = {
    'cybernoid_ii': {
        'config_module': 'pipelines.future_composer.cybernoid_ii.config',
        # Cyb II patterns live $AF01..$AFF3 (pattern_ptr_table + bodies),
        # extending into the seq area below. Verbatim region covers
        # ~$AF01..end of body.
        'pattern_range': (0xAF01, 0xB100),
    },
    'hawkeye': {
        'config_module': 'pipelines.future_composer.hawkeye.config',
        # Patterns at $8C00+, seq streams + SFX records up to ~$9D1A.
        # The verbatim tail covers this contiguously.
        'pattern_range': (0x8C00, 0x9D1A),
    },
}


def _load_sid_mem(sid_path: str) -> bytes:
    with open(sid_path, 'rb') as f:
        d = f.read()
    data_off = struct.unpack('>H', d[6:8])[0]
    psid_load = struct.unpack('>H', d[8:10])[0]
    if psid_load == 0:
        load = struct.unpack('<H', d[data_off:data_off+2])[0]
        body = d[data_off+2:]
    else:
        load = psid_load
        body = d[data_off:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    return bytes(mem)


def _build_rebuild(engine: str) -> tuple[bytes, bytes]:
    """Build a rebuild from USF and return (orig_mem, rebuild_mem)."""
    info = _CANARIES[engine]
    cfg_mod = importlib.import_module(info['config_module'])
    from pipelines.future_composer.config import FCConfig
    cfg = next(v for v in vars(cfg_mod).values()
                if isinstance(v, FCConfig))
    from pipelines.future_composer.composer_asm import build_via_asm_featuredriven
    rebuild_bytes = build_via_asm_featuredriven(cfg)
    orig_path = str(ROOT / cfg.sid_path)
    orig_mem = _load_sid_mem(orig_path)
    rebuild_mem = _load_sid_mem_from_bytes(rebuild_bytes)
    return orig_mem, rebuild_mem


def _load_sid_mem_from_bytes(reb_bytes: bytes) -> bytes:
    data_off = struct.unpack('>H', reb_bytes[6:8])[0]
    psid_load = struct.unpack('>H', reb_bytes[8:10])[0]
    if psid_load == 0:
        load = struct.unpack('<H', reb_bytes[data_off:data_off+2])[0]
        body = reb_bytes[data_off+2:]
    else:
        load = psid_load
        body = reb_bytes[data_off:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    return bytes(mem)


def verify_engine(engine: str) -> dict:
    """Verify one engine's pattern region. Returns dict with results.

    Accounts for cfg.featuredriven_addr_shift: rebuild's pattern bytes
    live at `orig_addr + shift`. We compare orig[A] vs rebuild[A+shift]
    and also re-apply the same pointer fixup the composer applies to
    the verbatim source (so pointer-containing tables verify as if the
    shift hadn't happened).
    """
    if engine not in _CANARIES:
        return {'engine': engine, 'error': f'unknown engine'}
    info = _CANARIES[engine]
    cfg_mod = importlib.import_module(info['config_module'])
    from pipelines.future_composer.config import FCConfig
    cfg = next(v for v in vars(cfg_mod).values()
                if isinstance(v, FCConfig))
    shift = cfg.featuredriven_addr_shift
    orig, reb = _build_rebuild(engine)
    # Apply the same pointer fixup to a copy of orig so the comparison
    # only flags TRUE byte-level data divergences (not legitimately
    # shifted pointers).
    if shift:
        from pipelines.future_composer.composer_asm import _fixup_verbatim_pointers
        import dataclasses as _dc
        # Build a shifted cfg matching what compose does internally
        def _s(a):
            return (a + shift) if a else 0
        sfx_default = (cfg.sfx_seq_stream_addr or 0x8FC5)
        shifted_cfg = _dc.replace(cfg,
            freq_lo_addr = _s(cfg.freq_lo_addr),
            freq_hi_addr = _s(cfg.freq_hi_addr),
            pattern_ptr_addr = _s(cfg.pattern_ptr_addr),
            instr_records_addr = _s(cfg.instr_records_addr),
            per_subtune_speed_addr = _s(cfg.per_subtune_speed_addr),
            drumtabel_addr = _s(cfg.drumtabel_addr),
            filterbytes_addr = _s(cfg.filterbytes_addr),
            startlen_addr = _s(cfg.startlen_addr),
            starttabel_addr = _s(cfg.starttabel_addr),
            arplo_addr = _s(cfg.arplo_addr),
            arphi_addr = _s(cfg.arphi_addr),
            pulsetabel_addr = _s(cfg.pulsetabel_addr),
            vibtabwait_addr = _s(cfg.vibtabwait_addr),
            wavearp_addr = _s(cfg.wavearp_addr),
            pulsearp_addr = _s(cfg.pulsearp_addr),
            sfx_seq_stream_addr = sfx_default + shift,
            per_subtune_smc_addr = _s(cfg.per_subtune_smc_addr),
        )
        orig_buf = bytearray(orig)
        _fixup_verbatim_pointers(orig_buf, shifted_cfg, shift, cfg.freq_lo_addr)
        orig = bytes(orig_buf)
    start, end = info['pattern_range']
    mismatches = []
    for orig_addr in range(start, end):
        reb_addr = orig_addr + shift
        if reb_addr >= 0x10000:
            break
        if orig[orig_addr] != reb[reb_addr]:
            mismatches.append((orig_addr, reb_addr,
                               orig[orig_addr], reb[reb_addr]))
            if len(mismatches) >= 16:
                break
    return {
        'engine': engine,
        'range': (start, end),
        'shift': shift,
        'total_bytes': end - start,
        'mismatches': mismatches,
    }


def _format_result(result: dict) -> str:
    if 'error' in result:
        return f'{result["engine"]:18s}  ERROR: {result["error"]}'
    start, end = result['range']
    n = result['total_bytes']
    miss = result['mismatches']
    shift = result.get('shift', 0)
    ok = '✓' if not miss else '✗'
    line = (f'{result["engine"]:18s}  {ok}  '
            f'${start:04X}..${end:04X} ({n} bytes, shift=${shift:04X})  '
            f'{len(miss)} mismatch{"" if len(miss)==1 else "es"}')
    if miss:
        for oa, ra, o, r in miss[:5]:
            line += f'\n    orig@${oa:04X}=${o:02X}  reb@${ra:04X}=${r:02X}'
        if len(miss) > 5:
            line += f'\n    ... ({len(miss) - 5} more)'
    return line


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--engine', choices=list(_CANARIES.keys()),
                      help='Verify one engine')
    grp.add_argument('--all', action='store_true',
                      help='Verify all canaries')
    args = p.parse_args()
    engines = list(_CANARIES.keys()) if args.all else [args.engine]
    any_fail = False
    for e in engines:
        result = verify_engine(e)
        print(_format_result(result))
        if result.get('mismatches') or 'error' in result:
            any_fail = True
    return 1 if any_fail else 0


if __name__ == '__main__':
    sys.exit(main())
