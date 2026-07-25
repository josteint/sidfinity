#!/usr/bin/env python3
"""Golden byte-identity harness for DMC family-1 carrier refactors.

The DMC composer→extract relocation + representation tidy-ups (see
deprecated/old_docs/dmc_composer_to_extract_plan.md) are *carrier* refactors: they move where
information lives without changing what the composer emits. The proof that
"nothing broke" is therefore that the rebuilt .sid is MD5-identical to a
pre-change baseline (identical bytes => identical $D400-$D418 write-stream =>
identical verdict — stronger and cheaper than re-verifying).

Two modes:

    # before any change — record baseline .sid MD5 (+ carrier features) and
    # stash the baseline .sid bytes so a later diff can localize a mismatch:
    python3 tools/golden_sid_diff.py --capture [--members family1|FILE.json] \
        [--out tmp/golden_baseline.json] [--jobs 8]

    # after a change — rebuild + compare MD5 to baseline; classify each
    # mismatch as write-stream-identical (inert, e.g. the #1 window-byte
    # corner) vs a real regression:
    python3 tools/golden_sid_diff.py --diff [--members ...] \
        [--baseline tmp/golden_baseline.json] [--jobs 8]

Member list: `family1` (default) = the largest family in tmp/dmc_families.json;
or a JSON file containing a list of HVSC-relative paths. Build failures are
recorded (not fatal) — a member that failed to build at baseline AND still
fails is not a regression; a member that built at baseline and now fails IS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import traceback
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs  # noqa: E402

BASELINE_SID_DIR = os.path.join(ROOT, 'tmp', 'golden_baseline_sids')

# USF-text markers that flag a member as exercising a carrier feature this plan
# touches — reported so we can confirm the set covers #1's blast radius.
_FEATURE_MARKERS = {
    'offtable_freq': 'offtable_freq',
    'offtable_vibdepth': 'offtable_vibdepth',
    'offtable_redirect': 'offtable_redirect',   # #1
    'sectpos_shadow': 'sectpos_shadow',         # #1
    'wave_table_pos': 'wave_table_pos',         # #1 (wavepos exemplar)
    'otrk': 'otrk_',                             # #2
    'cia_period': 'cia_period',                 # #3
    'play_repeat': 'play_repeat',               # #3
    'slide_phase': 'slide_phase',               # #4
}


def _member_list(spec: str) -> list[str]:
    if spec in (None, 'family1'):
        fams = json.load(open(os.path.join(ROOT, 'tmp', 'dmc_families.json')))
        return sorted(fams.items(), key=lambda kv: -len(kv[1]))[0][1]
    return json.load(open(spec))


def _path_key(rel: str) -> str:
    return hashlib.sha1(rel.encode()).hexdigest()[:16]


def _build_one(rel: str):
    """Build one member; return dict(path, md5, chips, feats, err, sid_bytes)."""
    from dmc_build_one import build
    td = tempfile.mkdtemp()
    out_sid = os.path.join(td, 'o.sid')
    out_usf = os.path.join(td, 'o.usf')
    try:
        # build() returns (n_chips, usf_src_path, build_path_description) —
        # it grew the third element 2026-07 (corpus_sync build-path recording);
        # unpack by index so another addition can't silently break this again.
        nch = build(rel, out_sid, out_usf)[0]
        sid = open(out_sid, 'rb').read()
        usf_txt = open(out_usf).read()
        feats = sorted(k for k, m in _FEATURE_MARKERS.items() if m in usf_txt)
        return {'path': rel, 'md5': hashlib.md5(sid).hexdigest(),
                'chips': nch, 'feats': feats, 'err': None, 'sid': sid}
    except Exception as e:  # noqa: BLE001 — record, don't crash the pool
        return {'path': rel, 'md5': None, 'chips': 0, 'feats': [],
                'err': f'{type(e).__name__}: {e}', 'tb': traceback.format_exc(),
                'sid': None}
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)


def cmd_capture(members: list[str], out: str, jobs: int):
    os.makedirs(BASELINE_SID_DIR, exist_ok=True)
    base = {}
    feat_counts: dict[str, int] = {}
    n_err = 0
    with Pool(jobs) as p:
        for i, r in enumerate(p.imap_unordered(_build_one, members, chunksize=4)):
            if r['sid'] is not None:
                open(os.path.join(BASELINE_SID_DIR,
                                  _path_key(r['path']) + '.sid'), 'wb').write(r['sid'])
                for f in r['feats']:
                    feat_counts[f] = feat_counts.get(f, 0) + 1
            else:
                n_err += 1
            base[r['path']] = {k: r[k] for k in ('md5', 'chips', 'feats', 'err')}
            if (i + 1) % 200 == 0:
                print(f'  captured {i + 1}/{len(members)} ({n_err} build-err)',
                      flush=True)
    json.dump(base, open(out, 'w'), indent=0)
    print(f'\nBASELINE -> {out}  ({len(base)} members, {n_err} build-errors)')
    print('carrier-feature coverage:')
    for f in sorted(feat_counts, key=lambda k: -feat_counts[k]):
        print(f'  {f:20s} {feat_counts[f]}')


def _diff_one(args):
    rel, base_md5, base_err = args
    r = _build_one(rel)
    # classify
    if r['err'] and base_err:
        return (rel, 'both_err', None)
    if r['err'] and not base_err:
        return (rel, 'now_err', r['err'])          # REGRESSION (built before)
    if not r['err'] and base_err:
        return (rel, 'now_builds', None)            # improvement (was error)
    if r['md5'] == base_md5:
        return (rel, 'identical', None)
    # md5 differs — compare write-stream vs the stashed baseline .sid
    verdict = _writestream_class(rel, r['sid'])
    return (rel, verdict, None)


def _writestream_class(rel: str, new_sid: bytes) -> str:
    """Classify an MD5 mismatch: 'inert' (write-stream identical to baseline)
    vs 'REGRESSION' (write-stream diverges). Compares the new build against the
    stashed baseline .sid across all subtunes via the flat instruction stream."""
    base_sid_path = os.path.join(BASELINE_SID_DIR, _path_key(rel) + '.sid')
    if not os.path.exists(base_sid_path):
        return 'diff_no_baseline_sid'
    from pipelines.hubbard.verify_cycle import (writelog_capture,
                                                compare_instruction_stream)
    from seed_disassembly import parse_psid
    orig = os.path.join(ROOT, 'hvsc84', rel)
    td = tempfile.mkdtemp()
    try:
        new_path = os.path.join(td, 'n.sid')
        open(new_path, 'wb').write(new_sid)
        n = parse_psid(orig)['songs']
        for sub in range(n):
            a = writelog_capture(base_sid_path, subtune=sub, duration=12.0)
            b = writelog_capture(new_path, subtune=sub, duration=12.0)
            # both are OUR composer's output (identical init structure), so a
            # plain flat prefix compare is the right test; default mode='legacy'.
            # Identical iff no divergence in the matched prefix AND equal length
            # (NOT match==len: legacy `match` is max(with-init, post-init) and is
            # on a different basis than len_a/len_b — comparing them false-fires).
            r = compare_instruction_stream(a, b)
            if not (r['match_all'] == r['len_all_a'] == r['len_all_b']):
                return 'REGRESSION'
        return 'inert'
    except Exception as e:  # noqa: BLE001
        return f'classify_err:{type(e).__name__}'
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)


def cmd_diff(members: list[str], baseline: str, jobs: int):
    base = json.load(open(baseline))
    work = [(m, base[m]['md5'], base[m]['err']) for m in members if m in base]
    missing = [m for m in members if m not in base]
    if missing:
        print(f'WARNING: {len(missing)} members not in baseline (skipped)')
    buckets: dict[str, list[str]] = {}
    with Pool(jobs) as p:
        for i, (rel, verdict, detail) in enumerate(
                p.imap_unordered(_diff_one, work, chunksize=4)):
            buckets.setdefault(verdict, []).append(rel)
            if verdict not in ('identical', 'both_err'):
                print(f'  [{verdict}] {rel}' + (f'  {detail}' if detail else ''),
                      flush=True)
            if (i + 1) % 200 == 0:
                print(f'  ...{i + 1}/{len(work)}', flush=True)
    print('\n=== GOLDEN DIFF SUMMARY ===')
    for k in sorted(buckets):
        print(f'  {k:20s} {len(buckets[k])}')
    ok = not (buckets.get('now_err') or buckets.get('REGRESSION') or
              [v for v in buckets if v.startswith('classify_err')] or
              buckets.get('diff_no_baseline_sid'))
    print('\nGATE:', 'PASS (0 regressions)' if ok else 'FAIL — investigate above')
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--capture', action='store_true')
    ap.add_argument('--diff', action='store_true')
    ap.add_argument('--members', default='family1')
    ap.add_argument('--out', default=os.path.join(ROOT, 'tmp', 'golden_baseline.json'))
    ap.add_argument('--baseline', default=os.path.join(ROOT, 'tmp', 'golden_baseline.json'))
    ap.add_argument('--jobs', type=int, default=default_jobs())
    args = ap.parse_args()
    members = _member_list(args.members)
    print(f'{len(members)} members, jobs={args.jobs}')
    if args.capture:
        cmd_capture(members, args.out, args.jobs)
    elif args.diff:
        sys.exit(0 if cmd_diff(members, args.baseline, args.jobs) else 1)
    else:
        ap.error('need --capture or --diff')


if __name__ == '__main__':
    main()
