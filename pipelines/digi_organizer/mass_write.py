#!/usr/bin/env python3
"""Mass-write Digi-Organizer FULL members alongside the HVSC originals.

SYNCS the on-disk corpus to the batch results file via `src.corpus_sync`,
so that what is stored is exactly what was verified: only rows earned by
the CURRENT code are written, the recorded build path is REPLAYED rather
than re-derived, members that are not FULL have their stale artifacts
DELETED, and a stratified sample is re-verified FROM DISK afterwards.
The rationale for each of those layers lives in `src/corpus_sync` and
ledger C20; this tool is the family's binding of them.

One thing is specific to this family: a member's artifacts are the
`.usf` PLUS its PCM sidecars (`<name>.sampleN.flac`), which the .usf
names by relative path. `corpus_sync.ARTIFACT_SUFFIXES` knows about the
.usf and .sid only, so orphaned sidecars are swept here — a .usf deleted
without its FLACs leaves audio on disk that nothing references and no
gate can see.

Usage:
    python3 pipelines/digi_organizer/mass_write.py
    ... --results FILE     read a different batch results jsonl
    ... --audit N          re-verify N members from disk (0 = skip; default 8)
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src import corpus_sync  # noqa: E402
from src.batch_results import store_path  # noqa: E402
from src.jobs import default_jobs  # noqa: E402
from src.tslog import phase, ts  # noqa: E402

HVSC = os.path.join(ROOT, 'hvsc85')
RESULTS = store_path('digi_organizer')


def write_member(rel: str) -> tuple:
    """Extract + build one member beside its original. Returns (rel, ok, err)."""
    try:
        from pipelines.digi_organizer.to_usf import write_usf
        from pipelines.digi_organizer.composer_asm import build_sid
        src = os.path.join(HVSC, rel)
        out_dir = os.path.dirname(src)
        usf_path = write_usf(src, out_dir)
        build_sid(usf_path, os.path.splitext(src)[0] + '.sidfinity.sid')
        return (rel, True, '')
    except Exception as e:
        return (rel, False, f'{type(e).__name__}: {e}'[:140])


def _rebuild_from_usf(rel: str, usf_path: str) -> bytes:
    """corpus_sync.audit_rebuild builder: the STORED .usf -> .sid bytes.

    build_sid writes the file itself, so build to a scratch path and read
    it back; the point of the check is that the stored pair AGREES, not
    where the bytes are produced."""
    import tempfile
    from pipelines.digi_organizer.composer_asm import build_sid
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'a.sid')
        build_sid(usf_path, out)
        return open(out, 'rb').read()


def _orphan_sidecars(rels_kept: set) -> int:
    """Delete `.sampleN.flac` sidecars of members we no longer store.

    A sidecar is owned by the `.usf` of the same basename — so once that
    .usf is gone (orphan removal) or was never written, its FLACs are
    unreferenced. Nothing else removes them: they are not in
    ARTIFACT_SUFFIXES, they parse as nothing, and no census counts them.
    """
    n = 0
    for flac in glob.glob(os.path.join(HVSC, '**', '*.sample*.flac'),
                          recursive=True):
        usf = flac.split('.sample')[0] + '.usf'
        if not os.path.exists(usf):
            os.unlink(flac)
            n += 1
    return n


def _audit(written: list, n: int) -> int:
    """Re-verify n written members FROM THEIR STORED ARTIFACTS.

    Two checks per member, both against what is ON DISK: the stored .usf
    must rebuild the stored .sid byte for byte (corpus_sync.audit_rebuild,
    the C20 fifth layer), and the stored .sid must still verify
    CYCLE-STRICT against the original (the fourth layer). Sampled, so it
    costs a couple of minutes rather than a full batch.
    """
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_strict
    from src import songlengths as SL
    sample = corpus_sync.sample_by_build_path(
        [(rel, 'standalone') for rel in written], n)
    ts(f'AUDIT: {len(sample)} members re-verified from their STORED artifacts')
    bad = corpus_sync.audit_rebuild(sample, HVSC, _rebuild_from_usf)
    for b in bad:
        ts(f'  AUDIT FAIL (usf/sid disagree): {b}')
    db = SL.load_database(glob.glob(os.path.join(
        HVSC, 'DOCUMENTS', 'Songlengths.md5'))[0])
    for rel, _bp in sample:
        src = os.path.join(HVSC, rel)
        stored = os.path.splitext(src)[0] + '.sidfinity.sid'
        try:
            dur = SL.get_durations(src, db)[0] * 1.1
        except Exception:
            dur = 120.0
        a = writelog_capture(src, 0, dur, force_rsid=True)
        b = writelog_capture(stored, 0, dur, force_rsid=True)
        r = compare_strict(a, b)
        if r['first_diff'] is not None or sum(map(len, a)) != sum(map(len, b)):
            ts(f'  AUDIT FAIL (stored .sid not FULL): {rel}')
            bad.append(rel)
    return len(bad)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', default=RESULTS)
    ap.add_argument('--audit', type=int, default=8)
    args = ap.parse_args()

    with phase('digi_organizer mass-write'):
        plan = corpus_sync.plan(args.results, 'digi_organizer', HVSC)
        for line in plan.report('pipelines/digi_organizer/family_batch.py'):
            ts(line)
        if plan.orphans:
            ts(f'removing {corpus_sync.remove_orphans(plan)} orphaned artifacts')
        rels = [d['path'] for d in plan.write]
        ts(f'building {len(rels)} members ({default_jobs(len(rels))} workers)')
        with Pool(default_jobs(len(rels))) as pool:
            res = pool.map(write_member, rels)
        ok = [rel for rel, good, _e in res if good]
        for rel, good, err in res:
            if not good:
                ts(f'  FAILED {rel}: {err}')
        ts(f'wrote {len(ok)} of {len(rels)}')
        swept = _orphan_sidecars(set(ok))
        if swept:
            ts(f'swept {swept} unreferenced PCM sidecars')
        bad = _audit(ok, args.audit) if args.audit else 0
    if bad or len(ok) != len(rels):
        sys.exit(1)


if __name__ == '__main__':
    main()
