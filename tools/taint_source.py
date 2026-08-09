#!/usr/bin/env python3
"""taint_source.py — is a RAM region WRITTEN during SID playback? (grey-box classify)

GREY-BOX CLASSIFICATION for OFF-TABLE reads. When an engine indexes a table past its
end into adjacent memory (the recurring off-table-read phenomenon), the decisive
question is whether that source region is:

  * STATIC  (never written during play)  -> the off-table read is REPRESENTABLE:
            capture the value (offtable_freq) or the program (walk the static table).
  * DYNAMIC (written during play)         -> HARD RESIDUE: the read pulls in engine-
            positional/runtime state; there is no static value to capture.

Pure black-box observation of the $D4xx write-log CANNOT answer this — the source
bytes are internal RAM, not SID registers. You must look at the binary's RAM. This
tool is that probe.

METHOD: `siddump --memtrace` (per-ACCESS, within-frame-complete). A per-FRAME snapshot
(`--memwatch`) has a within-frame blind spot: a write-then-restore inside one play()
is invisible. The per-access memtrace sees every access, and since a READ never changes
a byte's value while a WRITE does, tracking the distinct values seen at each address
across the whole trace catches every write, including transient ones.

ROBUSTNESS: runs ALL subtunes by default and unions the results — a byte written only
in a code path that a DIFFERENT subtune exercises would falsely read "static" from a
single playthrough. Still an OBSERVATION over the played code paths (full songlength),
not a proof over all possible inputs; a branch never taken in any subtune is unseen.

USAGE:
    tools/taint_source.py <file.sid> <LO-HI> [--all | --subtune N] [--duration S]
    tools/taint_source.py hvsc85/DEMOS/G-L/Jupiter41.sid 23A3-24BB --all
    tools/taint_source.py Jupiter41.sid 23A3-24BB          # basename -> globbed in hvsc85

Exit 0 + "STATIC" if the whole region is unwritten; exit 1 + the written addresses
otherwise. See ledger C2 (off-table one-shot program) for how to act on the verdict.
"""
import os, sys, re, glob, struct, subprocess, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]
_SD = os.path.join(ROOT, 'tools', 'siddump')
_TOK = re.compile(r'([0-9A-Fa-f]{4})=([0-9A-Fa-f]{2})')


def resolve_sid(path):
    if os.path.exists(path):
        return path
    hits = glob.glob(os.path.join(ROOT, 'hvsc85', '**', os.path.basename(path)),
                     recursive=True)
    if not hits:
        sys.exit(f'SID not found: {path}')
    return hits[0]


def n_subtunes(sid):
    try:
        from seed_disassembly import parse_psid
        return parse_psid(sid)['songs']
    except Exception:
        # PSID header: song count at offset 0x0E (big-endian u16)
        return struct.unpack('>H', open(sid, 'rb').read()[0x0E:0x10])[0] or 1


def taint_subtune(sid, lo, hi, sub, duration):
    """Return {addr: sorted(distinct values seen)} for addrs in [lo,hi] over one subtune."""
    out = subprocess.run([_SD, sid, '--subtune', str(sub),
                          '--duration', str(duration), '--memtrace'],
                         capture_output=True, text=True).stdout
    seen = defaultdict(list)
    for m in _TOK.finditer(out):
        a = int(m.group(1), 16)
        if lo <= a <= hi:
            v = int(m.group(2), 16)
            if not seen[a] or seen[a][-1] != v:
                seen[a].append(v)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sid')
    ap.add_argument('range', help='hex address range, e.g. 23A3-24BB')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--all', action='store_true', help='taint over ALL subtunes (default)')
    g.add_argument('--subtune', type=int, help='only this subtune')
    ap.add_argument('--duration', type=float, default=45.0,
                    help='seconds of memtrace per subtune (default 45; a repeating '
                         'program runs ~2250x in 45s, so this exercises it thoroughly. '
                         'The full per-access memtrace is ~1MB/5s, so raise this only '
                         'when a write might occur ONLY late in the song)')
    a = ap.parse_args()

    sid = resolve_sid(a.sid)
    lo, hi = (int(x, 16) for x in a.range.split('-'))
    subs = [a.subtune] if a.subtune is not None else list(range(n_subtunes(sid)))

    union = defaultdict(set)          # addr -> set of values across all scanned subtunes
    for sub in subs:
        for addr, vals in taint_subtune(sid, lo, hi, sub, a.duration).items():
            union[addr].update(vals)
        print(f'  scanned subtune {sub} (~{a.duration:.0f}s)', file=sys.stderr)

    changing = {a_: sorted(v) for a_, v in union.items() if len(v) > 1}
    n_touched = len(union)
    print(f'{os.path.basename(sid)}  ${lo:04X}-${hi:04X}  subtunes={subs}  '
          f'addresses touched={n_touched}  WRITTEN={len(changing)}')
    if changing:
        print('*** DYNAMIC — off-table read pulls in written memory (hard residue) ***')
        for ad in sorted(changing):
            print('  $%04X: %d distinct %s' % (ad, len(changing[ad]),
                                               ['%02X' % v for v in changing[ad]][:8]))
        sys.exit(1)
    print('*** STATIC — no byte written during play (over the scanned subtunes) '
          '=> off-table read is REPRESENTABLE ***')


if __name__ == '__main__':
    main()
