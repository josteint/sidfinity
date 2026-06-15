"""Init-shape survey across the top 100 HVSC engines.

One-shot survey — output landed in `docs/sid_init_report.md` and
`docs/sid_init_research.md`. Kept here (rather than archived) so the
survey can be re-run when HVSC updates or new init bucket candidates
surface; not part of the regular regression.


For each engine in the top 100 (by SID count), sample up to 2 SIDs
with songlength > 30s (or any if no such), run `siddump --writelog`,
extract frame 0 (the init invocation), and characterise:

  - n_writes          : number of SID writes during init (including
                        the host stub's pre-init $D418=$0F)
  - regs_touched      : set of SID register offsets written
  - final state       : per-register value at end of init
  - transients        : registers written more than once
  - bucket            : classification against the trichotomy

The output is per-SID detail + per-engine aggregate + a stress-test
of the trichotomy categories.
"""

import sys
import os
from collections import Counter, defaultdict

sys.path.insert(0, '.')

from pipelines.hubbard.verify_cycle import writelog_capture


# Audit categories from the trichotomy + a few stress-test markers.

def classify_init(frame0):
    """Return a dict of init-shape features per the trichotomy.

    `frame0` is the list of (cycle, reg, val) writes during the init
    invocation (siddump's first VBI bucket).
    """
    out = {
        'n_writes': len(frame0),
        'regs_touched': set(),
        'final': {},
        'transients': {},
        'cyc_first_eng_write': None,    # first engine write after host pre-write
    }
    counts = Counter()
    seen_d418_at = []
    for cyc, reg, val in frame0:
        out['regs_touched'].add(reg)
        out['final'][reg] = val
        counts[reg] += 1
        # The host's pre-init $D418=$0F is the first write at ~cyc 40.
        # The engine's first write comes later.
        if reg == 0x18:
            seen_d418_at.append((cyc, val))
        if cyc > 100 and out['cyc_first_eng_write'] is None:
            out['cyc_first_eng_write'] = cyc

    out['transients'] = {r: n for r, n in counts.items() if n > 1}
    out['d418_history'] = seen_d418_at
    return out


def bucket_for(feat, n_eng_writes):
    """Heuristic classification against the trichotomy + extreme cases."""
    if n_eng_writes == 0:
        return 'deferred (no SID writes)'
    if n_eng_writes <= 3:
        return 'minimal touch (≤3 writes)'
    # Standard "silence-clear" loop writes $D400-$D417 (24 regs)
    # then $D418. That's exactly 25 writes minimum.
    if 24 <= n_eng_writes <= 30:
        return 'clean reset (silence-clear + $D418)'
    # FutureComposer-style noise-clear: writes V*.ctrl twice (once
    # to noise, once to off). Detect via voice-ctrl transients.
    voice_ctrl_transients = sum(
        1 for r in (0x04, 0x0B, 0x12) if r in feat['transients'])
    if voice_ctrl_transients >= 2:
        return 'noise-burst / test-bit reset'
    if n_eng_writes > 30:
        return 'thorough setup (>30 writes)'
    return 'partial setup (4-23 writes)'


def main():
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..'))
    from src import sid_db
    db = sid_db.connect()

    # Top 100 engines
    engines = db.execute(
        "SELECT engine, COUNT(*) FROM sids WHERE engine IS NOT NULL "
        "GROUP BY engine ORDER BY COUNT(*) DESC LIMIT 100").fetchall()

    per_engine = {}

    for rank, (engine, n_sids) in enumerate(engines, 1):
        # Sample up to 2 SIDs with songlength > 30s; fall back to any
        rows = db.execute(
            "SELECT path, songlength_s FROM sids "
            "WHERE engine = ? AND songlength_s > 30 "
            "ORDER BY RANDOM() LIMIT 2", (engine,)).fetchall()
        if not rows:
            rows = db.execute(
                "SELECT path, songlength_s FROM sids WHERE engine = ? "
                "LIMIT 2", (engine,)).fetchall()

        per_engine[engine] = {
            'rank': rank, 'n_sids': n_sids,
            'samples': [],
        }

        for path, songlen in rows:
            full = f'/home/jtr/sidfinity/hvsc84/{path}'
            if not os.path.exists(full):
                continue
            try:
                frames = writelog_capture(full, 0, duration=1.0)
            except Exception as e:
                continue
            if not frames:
                continue
            f0 = frames[0]
            feat = classify_init(f0)

            # Count engine writes (exclude the host's pre-init $D418=$0F
            # write at cyc ≤ ~100).
            engine_writes = [
                w for w in f0
                if not (w[0] < 100 and w[1] == 0x18 and w[2] == 0x0F)]
            n_eng = len(engine_writes)
            feat['n_eng_writes'] = n_eng
            feat['bucket'] = bucket_for(feat, n_eng)

            per_engine[engine]['samples'].append({
                'path': path,
                'songlen': songlen,
                'feat': feat,
            })

    # ----- print summary -----

    # Per-engine compact line + a feature summary
    print(f'{"rank":>4}  {"engine":<35} {"n_sid":>5}  {"sample":>6} '
          f'{"writes":>6} {"regs":>4}  {"$D418":>5} {"trans":>5}  bucket')
    print('-' * 130)
    bucket_counts = Counter()
    for engine, info in per_engine.items():
        if not info['samples']:
            print(f'  {info["rank"]:>3}  {engine:<35} {info["n_sids"]:>5}  '
                  f'(no usable samples)')
            continue
        s = info['samples'][0]
        feat = s['feat']
        n_writes = feat['n_eng_writes']
        n_regs = len(feat['regs_touched'])
        d418 = feat['final'].get(0x18, '-')
        n_trans = len(feat['transients'])
        d418s = '-' if d418 == '-' else f'${d418:02X}'
        print(f'  {info["rank"]:>3}  {engine:<35} {info["n_sids"]:>5}  '
              f'{len(info["samples"]):>6} {n_writes:>6} {n_regs:>4}  '
              f'{d418s:>5} {n_trans:>5}  {feat["bucket"]}')
        bucket_counts[feat['bucket']] += 1

    print()
    print('Bucket distribution across top 100 engines (sample 1 per engine):')
    for bucket, n in bucket_counts.most_common():
        print(f'  {n:3d}  {bucket}')

    print()
    print('--- Stress-test: anything that doesn\'t fit the trichotomy ---')
    print()
    # Look for things the trichotomy might miss:
    # 1. Engines whose two samples differ wildly in init shape
    # 2. Engines that touch register slots beyond $D400-$D418
    # 3. Engines with weird transient patterns

    print('A. Per-engine intra-family variance (do tunes by the same engine '
          'have consistent init?):')
    for engine, info in per_engine.items():
        if len(info['samples']) < 2:
            continue
        s1, s2 = info['samples']
        n1 = s1['feat']['n_eng_writes']
        n2 = s2['feat']['n_eng_writes']
        regs1 = s1['feat']['regs_touched']
        regs2 = s2['feat']['regs_touched']
        if abs(n1 - n2) > 5 or regs1 != regs2:
            print(f'  {engine}: sample1 writes={n1} regs={len(regs1)}; '
                  f'sample2 writes={n2} regs={len(regs2)}')

    print()
    print('B. Engines touching registers outside $D400-$D418 (none should — '
          'siddump only reports SID writes):')
    # (siddump only captures SID, but defensive)

    print()
    print('C. Heavy-transient engines (many regs written >1 time during init):')
    for engine, info in per_engine.items():
        for s in info['samples'][:1]:
            n_trans = len(s['feat']['transients'])
            if n_trans >= 3:
                trans_summary = ', '.join(
                    f'${r:02X}×{n}' for r, n in
                    sorted(s['feat']['transients'].items())[:5])
                print(f'  {engine}: {n_trans} transients ({trans_summary})')
                break

    print()
    print('D. Engines with non-default $D418 (not $0F):')
    for engine, info in per_engine.items():
        for s in info['samples'][:1]:
            d418 = s['feat']['final'].get(0x18)
            if d418 is not None and d418 != 0x0F:
                print(f'  {engine}: final $D418=${d418:02X}')
                break

    print()
    print('E. Engines that DON\'T touch $D418 at all (relies on host):')
    for engine, info in per_engine.items():
        for s in info['samples'][:1]:
            # Did anything OTHER than the host's pre-init write hit $D418?
            d418_hist = s['feat']['d418_history']
            # Filter out the host's pre-init write (cyc ≤ 100, val $0F)
            engine_d418 = [
                (c, v) for c, v in d418_hist
                if not (c < 100 and v == 0x0F)]
            if not engine_d418 and d418_hist:
                print(f'  {engine}: only host wrote $D418 (engine left it alone)')
                break

    print()
    print('F. Engines that set the filter (cut_hi or res_filt non-zero):')
    for engine, info in per_engine.items():
        for s in info['samples'][:1]:
            cut_hi = s['feat']['final'].get(0x16, 0)
            res = s['feat']['final'].get(0x17, 0)
            if cut_hi or res:
                print(f'  {engine}: cut_hi=${cut_hi:02X} res_filt=${res:02X}')
                break


if __name__ == '__main__':
    main()
