#!/usr/bin/env python3
"""dmc_offtable_probe.py — one-command diagnosis of a DMC off-table freq
divergence (ledger C6/C11/C31).

The recurring DMC investigation, end to end: a member is partial, the first
divergence is a voice freq lo/hi, and the cause is an OFF-TABLE freq read
(a note/arp index past the 96-entry freq table, so the engine plays image /
state bytes as a pitch). Answering "which index, which address, static or
live, and (for a compilation) what value per player" took ~15 manual tool
calls (pc-trace + memwatch + writelog parsing + dmc_state_addr) the last time
it came up (Rogue_Ninja, round 91). This tool does the whole chain:

  1. Build the member (the SAME dispatch dmc_build_one uses) + trichotomy
     verdict -> the FAILING subtune(s).
  2. Localize the first divergence -> the diverging register + orig/our value
     (reusing the verify capture; no re-run).
  3. If the diverging register is a voice freq lo/hi, pc-trace the ORIGINAL and
     find the indexed load from THIS subtune's freq table whose result is the
     diverging value AND whose index is off-table (>=96) — reported by VALUE,
     never by a guessed frame (siddump frame != play() index — the Trap-C
     confusion this tool removes). Reports the index, the effective address,
     and which table byte it lands on.
  4. Classify the source address STATIC (constant across the song -> a
     representable window byte) vs LIVE (varies -> hard residue) via memwatch.
  5. For a COMPILATION, sample the SAME off-table index in EVERY packed player
     (each in the file subtune that selects it) — surfacing the per-player
     window fact directly (player 1 idx 97 = $B7 vs player 0 = $D6).

Usage:
    python3 tools/dmc_offtable_probe.py MUSICIANS/B/Bayliss_Richard/Rogue_Ninja.sid
    python3 tools/dmc_offtable_probe.py <path> --subtune 1      # a specific subtune

<path> is HVSC-relative (under hvsc84/).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')
# LDA/LDX/LDY with an effective address + loaded value, e.g.
#   25c9 t b7 01 61 ... b9 a7 26  LDAay 26a7,Y [2708]{b7}
_LD_LINE = re.compile(
    r'\bLD[AXY]\w*\s+([0-9a-fA-F]{2,4}),[XY]\s+\[([0-9a-fA-F]{4})\]\{([0-9a-fA-F]{2})\}')


def _freq_addrs_for_subtune(rel, hv, comp, sub):
    """(freq_lo_addr, freq_hi_addr, player_desc, all_player_cfgs) for `sub`.
    all_player_cfgs = [(pidx, base, flo, fhi, file_subtune)] so the caller can
    sample the same idx in every packed player (compilation per-player fact)."""
    from pipelines.dmc.v4.factory import dmc_v4_config
    if comp is None:
        cfg = dmc_v4_config(rel, hvsc_root=hv)
        return (cfg.freq_lo_addr, cfg.freq_hi_addr, f'single (base ${cfg.base:04X})',
                [(0, cfg.base, cfg.freq_lo_addr, cfg.freq_hi_addr, None)])
    import pipelines.dmc.v4.compilation as compmod
    reloc = comp.get('reloc') or {}
    players = []
    for pidx, base in enumerate(comp['bases']):
        c = compmod._player_cfg(rel, hv, comp, pidx, base, reloc.get(base))
        fsub = min(c.song_subtunes.values()) if getattr(c, 'song_subtunes', None) else None
        players.append((pidx, base, c.freq_lo_addr, c.freq_hi_addr, fsub))
    pidx = comp['map'][sub][0]
    _, _, flo, fhi, _ = players[pidx]
    return flo, fhi, f'compilation player {pidx} (base ${comp["bases"][pidx]:04X})', players


def _memwatch_series(sid_path, addr, subtune, dur=45):
    """Set of distinct values `addr` takes over `dur` s (per-frame memwatch on
    the given file subtune). One value -> STATIC; more -> LIVE."""
    st = [] if subtune is None else ['--subtune', str(subtune + 1)]
    try:
        out = subprocess.run(
            [SIDDUMP, sid_path, '--duration', str(dur), *st,
             '--memwatch', f'{addr:04X}'],
            capture_output=True, text=True, timeout=dur + 60).stdout
    except Exception:
        return set()
    vals = set()
    for line in out.splitlines():
        m = re.search(rf'{addr:04X}=([0-9A-F]{{2}})', line)
        if m:
            vals.add(m.group(1))
    return vals


def _pctrace_offtable_read(orig, subtune, flo, fhi, want_lo, orig_val, dur):
    """Scan the ORIGINAL's pc-trace for the indexed freq-table load whose result
    is `orig_val` and whose index is OFF-TABLE (>=96). Returns
    (idx, eff_addr, base) or None. Value-based, not frame-based."""
    base = flo if want_lo else fhi
    lo_reg, hi_reg = base + 96, base + 256          # off-table window of the table
    frames = min(6000, max(200, int(dur * 50)))
    with tempfile.NamedTemporaryFile(suffix='.pct', delete=False) as f:
        pct = f.name
    try:
        subprocess.run(
            [SIDDUMP, orig, '--subtune', str(subtune + 1),
             '--duration', str(frames / 50.0 + 1),
             '--pc-trace', pct, '1', str(frames)],
            capture_output=True, text=True, timeout=frames / 50 + 180)
        best = None
        with open(pct) as fh:
            for line in fh:
                m = _LD_LINE.search(line)
                if not m:
                    continue
                eff = int(m.group(2), 16)
                val = int(m.group(3), 16)
                if lo_reg <= eff < hi_reg and val == orig_val:
                    idx = eff - base
                    # earliest reachable off-table read of this value
                    if best is None or idx < best[0]:
                        best = (idx, eff, base)
        return best
    finally:
        os.unlink(pct)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', help='HVSC-relative path (under hvsc84/)')
    ap.add_argument('--subtune', type=int, default=None,
                    help='probe this subtune (default: every failing one)')
    args = ap.parse_args()

    from dmc_build_one import build, verify
    from find_first_divergence import _flatten, describe_reg
    from pipelines.dmc.v4.compilation import detect_compilation
    from pipelines.hubbard.verify_cycle import (writelog_capture,
                                                writelog_per_irq_capture)
    from src.songlengths import load_database, get_durations
    from seed_disassembly import parse_psid

    rel = args.path
    orig = os.path.join(ROOT, 'hvsc84', rel)
    if not os.path.exists(orig):
        sys.exit(f'not found: {orig}')
    hv = os.path.join(ROOT, 'hvsc84')
    name = os.path.splitext(os.path.basename(rel))[0]
    out_sid = os.path.join(ROOT, 'tmp', f'{name}.probe.sid')
    os.makedirs(os.path.dirname(out_sid), exist_ok=True)

    nch, _, path = build(rel, out_sid, None)
    comp = detect_compilation(rel, hvsc_root=hv) if 'compilation' in path else None
    print(f'member    : {rel}')
    print(f'build path: {path}')
    if nch > 1:
        print('note: multi-chip member — off-table probe assumes single-chip '
              'freq addressing; interpret with the build path in mind.')

    allok, fails = verify(orig, out_sid, nch)
    if allok:
        print('\nmember is FULL — nothing to probe.')
        return
    subs = [args.subtune] if args.subtune is not None else fails
    db = load_database(os.path.join(hv, 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    speed = int.from_bytes(open(orig, 'rb').read(0x16)[0x12:0x16], 'big')

    for sub in subs:
        print(f'\n===== subtune {sub} =====')
        cia = bool((speed >> min(sub, 31)) & 1)
        cap = writelog_per_irq_capture if cia else writelog_capture
        dur = max(5.0, min((durs[sub] if durs and sub < len(durs) else 110) * 1.1, 400.0))
        a = cap(orig, subtune=sub, duration=dur)
        b = cap(out_sid, subtune=sub, duration=dur)
        skip = not cia
        fo, fr = _flatten(a, skip), _flatten(b, skip)
        n = min(len(fo), len(fr))
        div = next((i for i in range(n) if fo[i][:2] != fr[i][:2]), None)
        if div is None:
            print('  no (reg,val) divergence in the overlap (a length_fail — '
                  'not an off-table read). See dmc_build_one --localize.')
            continue
        o_reg, o_val = fo[div][0], fo[div][1]
        r_val = fr[div][1]
        r = o_reg & 0x1F
        print(f'  first divergence @ flat {div}: $D4{o_reg:02X} '
              f'({describe_reg(o_reg)})  orig=${o_val:02X}  ours=${r_val:02X}')
        if r % 7 not in (0, 1) or r > 0x14:
            print('  diverging register is NOT a voice freq lo/hi — this probe '
                  'targets off-table FREQ reads; use dmc_build_one --localize + '
                  'effect_chain_profiler for other registers.')
            continue
        want_lo = (r % 7 == 0)
        flo, fhi, pdesc, players = _freq_addrs_for_subtune(rel, hv, comp, sub)
        print(f'  freq tables: lo ${flo:04X}  hi ${fhi:04X}  [{pdesc}]')
        hit = _pctrace_offtable_read(orig, sub, flo, fhi, want_lo, o_val, dur)
        if hit is None:
            print('  no off-table freq read of that value found in the pc-trace '
                  '— the divergence may be an on-table note, a slide, or a '
                  'non-freq effect. (Widen songlength or inspect manually.)')
            continue
        idx, eff, base = hit
        tbl = 'freq lo' if want_lo else 'freq hi'
        print(f'  >> OFF-TABLE {tbl} read: index {idx} (>=96) '
              f'-> ${eff:04X} = ${o_val:02X}')
        # static vs live (ledger C6): sample the source addr on THIS subtune's
        # selecting file subtune
        this_fsub = None
        if comp is not None:
            this_fsub = players[comp['map'][sub][0]][4]
        vals = _memwatch_series(orig, eff, this_fsub if comp else sub)
        if len(vals) == 1:
            print(f'     source ${eff:04X} is STATIC ({vals.pop()}) across the '
                  f'song -> REPRESENTABLE (capture the value).')
        elif vals:
            print(f'     source ${eff:04X} is LIVE ({len(vals)} distinct values) '
                  f'-> dynamic residue (C11: needs a live redirect/shadow).')
        # per-player window fact (ledger C31)
        if comp is not None and len(players) > 1:
            print('     per-player value at off-table idx '
                  f'{idx} (each in its selecting subtune):')
            for pidx, pbase, pflo, pfhi, pfsub in players:
                pa = (pflo if want_lo else pfhi) + idx
                pv = _memwatch_series(orig, pa, pfsub)
                tag = '  <- THIS subtune' if comp['map'][sub][0] == pidx else ''
                print(f'       player {pidx} (base ${pbase:04X}): '
                      f'${pa:04X} = {sorted(pv) or ["?"]}{tag}')
            print('     -> if these differ, it is the C31 per-player window fact '
                  '(the merge collapses one file-level idx-keyed array).')


if __name__ == '__main__':
    main()
