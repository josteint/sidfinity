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
                                                     write_dmc_compilation_usf,
                                                     write_dmc_medley_usf)
        from pipelines.dmc.v4.compilation import (detect_compilation,
                                                  detect_medley)
        from pipelines.dmc.composer_asm import build_dmc_sid
        from src.usf.parser import parse_file
        hvsc = os.path.join(ROOT, 'hvsc85')
        out_dir = os.path.dirname(os.path.join(hvsc, rel))
        # REPLAY the build path the batch RECORDED, never re-derive it. The
        # writer re-deriving the dispatch is exactly how the stored artifact
        # came to disagree with the verified one (ledger C20, fourth layer),
        # and re-derivation is not even capable of matching: the batch's
        # compilation fallback fires on a VERIFY-time exception that no
        # writer can observe. A row without `build_path` is pre-2026-07-22
        # and is refused by main() rather than guessed at.
        # The batch's write-stream retry may have chosen mask_only (a member
        # whose original never clears AD+SR). Push it onto the CONFIG so the
        # writer emits it into the stored .usf natively. Injecting it into the
        # parsed USF instead left the stored pair inconsistent: the .usf
        # specified a build that verifies PARTIAL while the .sid beside it was
        # built from a param living solely in the batch jsonl
        # (Nice_Dream_2SID). That is the Principle §8 failure — a rebuild
        # needing information absent from the USF — and it defeats every gate,
        # since re-verifying the stored .sid PASSES while regenerating from
        # the stored .usf does not.
        def _prime(cfg):
            if hold_gateoff:
                cfg.extra_params['hold_gateoff'] = hold_gateoff
            return cfg
        if build_path == 'multisid':
            cfgs = dmc_v4_config_2sid(rel, hvsc_root=hvsc)
            usf_path = write_dmc_2sid_usf([_prime(c) for c in cfgs], out_dir,
                                          hvsc_root=hvsc)
        elif build_path == 'medley':
            usf_path = write_dmc_medley_usf(
                rel, detect_medley(rel, hvsc_root=hvsc), out_dir,
                hvsc_root=hvsc)
        elif build_path == 'compilation':
            usf_path = write_dmc_compilation_usf(
                rel, detect_compilation(rel, hvsc_root=hvsc), out_dir,
                hvsc_root=hvsc)
        elif build_path == 'multiplex':
            # TIME-MULTIPLEXED dual player (ledger C27): two independent
            # tunes on one chip, one per play() call. Replayed like every
            # other path (C20 fourth layer — never re-derive the dispatch).
            from pipelines.dmc.v4.compilation import detect_multiplex
            from pipelines.dmc.v4.extract.to_usf import write_dmc_multiplex_usf
            _mux = detect_multiplex(rel, hvsc_root=hvsc)
            usf_path = write_dmc_multiplex_usf(
                [_prime(dmc_v4_config(rel, hvsc_root=hvsc, base_override=b))
                 for b in _mux['bases']], out_dir, hvsc_root=hvsc)
        elif build_path in ('hetero_masm', 'hetero_v5'):
            # Heterogeneous (ledger C31/C35): one UsfFile carrying
            # every packed player — merged instrument pool, per-subtune
            # freq_table / default_filter / params / init, and `origin_engine`
            # naming which composer builds each subtune.
            from pipelines.music_assembler.heterogeneous import (
                heterogeneous_to_usf)
            from src.usf.writer import write_file
            usf_path = os.path.join(
                out_dir, os.path.basename(rel).replace('.sid', '.usf'))
            write_file(heterogeneous_to_usf(rel, hvsc_root=hvsc), usf_path)
        else:
            usf_path = write_dmc_usf(_prime(dmc_v4_config(rel, hvsc_root=hvsc)),
                                     out_dir, hvsc_root=hvsc)
        usf = parse_file(usf_path)
        if hold_gateoff and usf.params.fields.get('hold_gateoff') != hold_gateoff:
            # the writer dropped it (a build path whose params don't carry the
            # config's extra_params). Storing the pair anyway would recreate
            # the very inconsistency above — refuse instead.
            return (rel, False, f'hold_gateoff={hold_gateoff} did not reach '
                                f'the stored .usf ({build_path} path)')
        if build_path in ('hetero_masm', 'hetero_v5'):
            from pipelines.music_assembler.heterogeneous import build_from_usf
            sid = build_from_usf(usf)
        else:
            sid = build_dmc_sid(usf)
        base = os.path.splitext(os.path.join(hvsc, rel))[0]
        open(base + '.sidfinity.sid', 'wb').write(sid)
        return (rel, True, '')
    except Exception as e:
        return (rel, False, f'{type(e).__name__}: {e}'[:120])


def _rebuild_from_usf(rel: str, usf_path: str) -> bytes:
    """corpus_sync.audit_rebuild builder: stored .usf -> .sid bytes.

    Dispatches on `origin_engine` — a file whose subtunes name more than one
    engine needs the heterogeneous builder (ledger C35). This is the DISPATCH
    layer, the only place permitted to read that field."""
    from src.usf.parser import parse_file
    from pipelines.dmc.composer_asm import build_dmc_sid
    from src.usf.types import MusicSubtune
    usf = parse_file(usf_path)
    if any(getattr(s, 'origin_engine', None) for s in usf.subtunes
           if isinstance(s, MusicSubtune)):
        from pipelines.music_assembler.heterogeneous import build_from_usf
        return build_from_usf(usf)
    return build_dmc_sid(usf)


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
    from src import corpus_sync
    import io
    import contextlib
    sample = corpus_sync.sample_by_build_path(written, n)
    print(f'AUDIT: re-verifying {len(sample)} members from their STORED '
          f'artifacts ({", ".join(sorted({bp for _, bp in sample}))})',
          flush=True)
    bad = 0
    for rel, bp in sample:
        orig = os.path.join(ROOT, 'hvsc85', rel)
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
    # SELF-CONSISTENCY (corpus_sync item 4): the verify above cannot see a
    # stored PAIR that disagrees — it re-verifies the .sid, which passes while
    # the .usf beside it specifies a DIFFERENT build.
    for f in corpus_sync.audit_rebuild(sample, os.path.join(ROOT, 'hvsc85'),
                                       _rebuild_from_usf):
        bad += 1
        print(f'  AUDIT FAIL {f}', flush=True)
    return bad


def main():
    results = RESULTS
    if '--results' in sys.argv:
        results = sys.argv[sys.argv.index('--results') + 1]
    n_audit = 12
    if '--audit' in sys.argv:
        n_audit = int(sys.argv[sys.argv.index('--audit') + 1])
    from src import corpus_sync
    p = corpus_sync.plan(results, 'dmc_v4', os.path.join(ROOT, 'hvsc85'),
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
