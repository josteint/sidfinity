#!/usr/bin/env python3
"""Mass-write DMC FULL members alongside the HVSC originals.

SYNCS the on-disk corpus to a batch results file, so that what is stored is
exactly what was verified — three separate guarantees, each closing one
layer of the C20 palimpsest:

  1. code_hash — only rows whose verdict was earned by the CURRENT code are
     written. Stale rows are skipped with a warning; re-run the batch.
  2. build_path REPLAY — each member is rebuilt through the path the batch
     RECORDED, never a re-derived dispatch. Re-deriving is how multi-SID
     members came to be stored as single-chip extractions, and it cannot in
     principle match the batch's compilation fallback, which fires on a
     verify-time exception no writer can observe. A row with no recorded
     build_path is refused, not guessed at.
  3. ORPHAN REMOVAL — a member that is NOT full must have no stored
     artifact. Without this, the .usf/.sid written when older code judged it
     FULL persists forever: no mass-write revisits a non-FULL member, and
     usf_corpus_check cannot see it because the file parses fine.

Then it AUDITS a stratified sample by re-verifying them FROM THE STORED
ARTIFACTS (one per distinct build_path) — the only check that exercises
writer and verifier against each other — and exits 1 if any fails.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/dmc_mass_write.py
    ... --results FILE     read a different batch results jsonl
    ... --audit N          audit N members from disk (0 = skip; default 12)
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs  # noqa: E402

RESULTS = os.path.join(ROOT, 'tmp', 'dmc_wide_results.jsonl')


def write_member(item) -> tuple:
    rel, hold_gateoff, build_path = item
    try:
        from pipelines.dmc.v4.factory import dmc_v4_config, dmc_v4_config_2sid
        from pipelines.dmc.v4.extract.to_usf import (write_dmc_usf,
                                                     write_dmc_2sid_usf,
                                                     write_dmc_compilation_usf)
        from pipelines.dmc.v4.compilation import detect_compilation
        from pipelines.dmc.composer_asm import build_dmc_sid
        from src.usf.parser import parse_file
        hvsc = os.path.join(ROOT, 'hvsc84')
        out_dir = os.path.dirname(os.path.join(hvsc, rel))
        # REPLAY the build path the batch RECORDED, never re-derive it. The
        # writer re-deriving the dispatch is exactly how the stored artifact
        # came to disagree with the verified one (ledger C20, fourth layer),
        # and re-derivation is not even capable of matching: the batch's
        # compilation fallback fires on a VERIFY-time exception that no
        # writer can observe. A row without `build_path` is pre-2026-07-22
        # and is refused by main() rather than guessed at.
        if build_path == 'multisid':
            usf_path = write_dmc_2sid_usf(
                dmc_v4_config_2sid(rel, hvsc_root=hvsc), out_dir,
                hvsc_root=hvsc)
        elif build_path == 'compilation':
            usf_path = write_dmc_compilation_usf(
                rel, detect_compilation(rel, hvsc_root=hvsc), out_dir,
                hvsc_root=hvsc)
        else:
            usf_path = write_dmc_usf(dmc_v4_config(rel, hvsc_root=hvsc),
                                     out_dir, hvsc_root=hvsc)
        usf = parse_file(usf_path)
        # the batch's write-stream retry may have chosen mask_only (a member
        # whose original never clears AD+SR) — apply it so the written SID
        # matches the verified verdict.
        if hold_gateoff:
            usf.params.fields['hold_gateoff'] = hold_gateoff
        sid = build_dmc_sid(usf)
        base = os.path.splitext(os.path.join(hvsc, rel))[0]
        open(base + '.sidfinity.sid', 'wb').write(sid)
        return (rel, True, '')
    except Exception as e:
        return (rel, False, f'{type(e).__name__}: {e}'[:120])


def _audit(written, n: int) -> int:
    """Re-verify n written members FROM THE STORED ARTIFACTS.

    The C20 fourth-layer detector: a writer that takes a different build path
    than the verifier produces a well-formed, code_hash-blessed, WRONG file
    that no other gate can see. Only re-verifying what is ON DISK exercises
    writer and verifier against each other. Sampled (one member per distinct
    build_path first, then spread over the rest) so it costs seconds, and the
    build_path stratification is precisely what would have caught the
    multi-SID case.
    """
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from dmc_build_one import verify
    import io
    import contextlib
    by_path = {}
    for rel, bp in written:
        by_path.setdefault(bp, []).append(rel)
    sample = []
    for bp, rels in sorted(by_path.items()):
        step = max(1, len(rels) // max(1, n // max(1, len(by_path))))
        sample += [(r, bp) for r in rels[::step][:max(1, n // len(by_path))]]
    print(f'AUDIT: re-verifying {len(sample)} members from their STORED '
          f'artifacts ({", ".join(sorted(by_path))})', flush=True)
    bad = 0
    for rel, bp in sample:
        orig = os.path.join(ROOT, 'hvsc84', rel)
        reb = os.path.splitext(orig)[0] + '.sidfinity.sid'
        nch = 1
        if bp == 'multisid':
            from pipelines.dmc.v4.factory import _sid_header_multi
            nch = _sid_header_multi(orig)[0]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                ok = verify(orig, reb, nch)
        except Exception as e:
            ok, bp = False, f'{bp} ({type(e).__name__})'
        if not ok:
            bad += 1
            print(f'  AUDIT FAIL [{bp}] {rel} — the STORED artifact does not '
                  f'reproduce its verdict', flush=True)
    print(f'AUDIT: {len(sample) - bad}/{len(sample)} stored artifacts '
          f're-verify', flush=True)
    return bad


def main():
    results = RESULTS
    if '--results' in sys.argv:
        results = sys.argv[sys.argv.index('--results') + 1]
    n_audit = 12
    if '--audit' in sys.argv:
        n_audit = int(sys.argv[sys.argv.index('--audit') + 1])
    from src import corpus_sync
    p = corpus_sync.plan(results, 'dmc_v4', os.path.join(ROOT, 'hvsc84'),
                         require_build_path=True)
    for line in p.report('tools/dmc_family_batch.py'):
        print(line, flush=True)
    full = [(d['path'], d.get('hold_gateoff'), d['build_path'])
            for d in p.write]
    orphan = p.orphans
    corpus_sync.remove_orphans(p)
    ok = err = 0
    errs = []
    with Pool(default_jobs(cap=len(full))) as pool:
        for i, (rel, good, msg) in enumerate(
                pool.imap_unordered(write_member, full, chunksize=8)):
            if good:
                ok += 1
            else:
                err += 1
                errs.append((rel, msg))
            if (i + 1) % 250 == 0:
                print(f'  {i+1}/{len(full)}  ok={ok} err={err}', flush=True)
    print(f'DONE  ok={ok}  err={err}  orphans_removed={len(orphan)}', flush=True)
    for rel, msg in errs[:20]:
        print(f'  ERR {rel}: {msg}')
    if n_audit and ok:
        written = [(rel, bp) for rel, _, bp in full
                   if rel not in {e[0] for e in errs}]
        if _audit(written, n_audit):
            sys.exit(1)


if __name__ == '__main__':
    main()
