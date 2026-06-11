#!/usr/bin/env python3
"""state_map_gen.py — generate a state_diff map file from per-engine
annotation + composer's xa65 label dump.

Each FC engine has a `state_map.py` annotation file with:
  - PER_VOICE_STATE: {label: orig_base_addr} for 3-byte voice arrays
  - SCALAR_STATE: {label: orig_addr} for shared scalars
  - COMPOSER_LABEL_MAP: {annotation_label: composer_label_in_xa65}

This tool builds the composer's asm, dumps xa65 labels, and writes a
state_diff map file (Python dict literal) that maps every orig state
address (per-voice expanded) to its rebuild counterpart with a label.

Usage:
    python3 tools/state_map_gen.py --engine ENGINE [--voice {1,2,3,all}] \
                                   [--output PATH]

ENGINE is the engine name (e.g. 'hawkeye', 'cybernoid_ii') — looks for
`pipelines/future_composer/<engine>/state_map.py` and that engine's
config.

Without --voice, emits all 3 voices' per-voice state + scalars.
With --voice N, emits only voice N's state + scalars.

Output is suitable for `python3 tools/state_diff.py ... --map MAP`.
"""
from __future__ import annotations

import argparse
import importlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_engine(engine: str):
    """Load (cfg, state_map module) for an engine."""
    cfg_mod = importlib.import_module(
        f'pipelines.future_composer.{engine}.config')
    state_mod = importlib.import_module(
        f'pipelines.future_composer.{engine}.state_map')
    # cfg singleton: assume the module has ONE FCConfig instance
    from pipelines.future_composer.config import FCConfig
    cfg_obj = next(v for v in vars(cfg_mod).values()
                    if isinstance(v, FCConfig))
    return cfg_obj, state_mod


def _build_and_get_xa65_labels(cfg) -> dict[str, int]:
    """Build the composer asm and parse xa65's label dump. Mirrors
    build_via_asm_featuredriven's contiguous base-float (measure pass +
    widen-on-'negative length' retries) so engines whose data layout needs
    the float (the standard family) resolve like the real build."""
    from pipelines.future_composer.to_usf import write_canary_usf
    from pipelines.future_composer.composer_asm import (
        compose_fc_asm_featuredriven, _xa65_assemble)
    from src.usf.parser import parse
    with tempfile.NamedTemporaryFile(suffix='.usf', delete=False) as f:
        p = f.name
    write_canary_usf(cfg, out_path=p)
    with open(p) as f:
        usf = parse(f.read())
    os.unlink(p)
    if cfg.emit_data_from_usf and cfg.contiguous_data_layout:
        orig_base = min(a for a in (cfg.freq_lo_addr, cfg.freq_hi_addr,
                                    cfg.per_subtune_speed_addr,
                                    cfg.instr_records_addr) if a)
        meas_base = orig_base + 0x800
        for _ in range(6):
            asm, _la = compose_fc_asm_featuredriven(
                usf, cfg, data_base_override=meas_base)
            try:
                _, labels = _xa65_assemble(asm, _la, return_labels=True)
            except RuntimeError as e:
                if 'negative length' in str(e):
                    meas_base += 0x800
                    continue
                raise
            engine_end = labels['__engine_end']
            break
        else:
            raise RuntimeError('state_map_gen: base-float failed')
        float_base = max(orig_base, engine_end)
        asm, _la = compose_fc_asm_featuredriven(
            usf, cfg, data_base_override=float_base)
        _, labels = _xa65_assemble(asm, _la, return_labels=True)
        return labels
    asm, _la = compose_fc_asm_featuredriven(usf, cfg)
    _, labels = _xa65_assemble(asm, _la, return_labels=True)
    return labels


def _build_state_map(cfg, state_mod, voices: list[int],
                     orig_shift: int = 0) -> dict:
    """Build the {orig_addr: (rebuild_addr, label)} dict. `orig_shift`
    relocates the annotation's orig addresses (standard-family members
    load at $1800/$4800/... with a fixed internal layout)."""
    labels = _build_and_get_xa65_labels(cfg)
    out: dict[int, tuple[int, str]] = {}

    # Per-voice arrays
    for ann_name, orig_base in state_mod.PER_VOICE_STATE.items():
        composer_name = state_mod.COMPOSER_LABEL_MAP.get(ann_name, ann_name)
        rebuild_base = labels.get(composer_name)
        if rebuild_base is None:
            print(f'WARN: composer label not found: {composer_name} '
                  f'(annotated as {ann_name})', file=sys.stderr)
            continue
        for v in voices:
            offset = v - 1  # V1=0, V2=1, V3=2
            label = f'{ann_name}[V{v}]'
            out[orig_base + orig_shift + offset] = (
                rebuild_base + offset, label)

    # Scalars (no voice expansion)
    for ann_name, orig_addr in state_mod.SCALAR_STATE.items():
        composer_name = state_mod.COMPOSER_LABEL_MAP.get(ann_name, ann_name)
        rebuild_addr = labels.get(composer_name)
        if rebuild_addr is None:
            print(f'WARN: composer label not found: {composer_name} '
                  f'(annotated as {ann_name})', file=sys.stderr)
            continue
        out[orig_addr + orig_shift] = (rebuild_addr, ann_name)

    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--engine', required=True,
                   help='Engine name (e.g. hawkeye, cybernoid_ii)')
    p.add_argument('--voice', default='all',
                   choices=['1', '2', '3', 'all'],
                   help='Which voice(s) to include (default all)')
    p.add_argument('--sid', default=None,
                   help='SID path for per-member configs (standard family: '
                        'derives the cfg via fc_standard_config — both the '
                        "rebuild's layout and the orig's reloc shift depend "
                        'on the member)')
    p.add_argument('--output', default=None,
                   help='Output map file path (default stdout)')
    args = p.parse_args()
    try:
        cfg, state_mod = _load_engine(args.engine)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f'error: could not load engine {args.engine!r}: {e}',
              file=sys.stderr)
        return 1
    orig_shift = 0
    if args.sid:
        if args.engine != 'standard':
            print('error: --sid is only supported for the standard engine',
                  file=sys.stderr)
            return 1
        from pipelines.future_composer.standard.config import (
            fc_standard_config, _REF_LOAD)
        import struct
        cfg = fc_standard_config(args.sid)
        d = open(args.sid, 'rb').read()
        hdr = struct.unpack('>H', d[6:8])[0]
        orig_shift = struct.unpack('<H', d[hdr:hdr + 2])[0] - _REF_LOAD
    voices = [1, 2, 3] if args.voice == 'all' else [int(args.voice)]
    m = _build_state_map(cfg, state_mod, voices, orig_shift=orig_shift)
    lines = [f'# Generated by state_map_gen.py from '
             f'pipelines/future_composer/{args.engine}/state_map.py']
    lines.append('# DO NOT EDIT — re-run state_map_gen.py to refresh.')
    lines.append('{')
    for orig, (reb, label) in sorted(m.items()):
        lines.append(f'    0x{orig:04X}: (0x{reb:04X}, {label!r}),')
    lines.append('}')
    out_text = '\n'.join(lines)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(out_text)
        print(f'wrote {args.output} '
              f'({len(m)} entries, voices={voices})', file=sys.stderr)
    else:
        print(out_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
