"""DMC family write-log verification.

Verdict = `compare_instruction_stream(mode='trichotomy')` per subtune
at full songlength × 1.1 (Check A end-of-init SID state + Check B play
stream), via siddump --writelog (libsidplayfp ground truth).
"""
from __future__ import annotations

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.jobs import default_jobs
from pipelines.hubbard.verify_cycle import (
    writelog_capture, compare_instruction_stream,
)
from src.songlengths import load_database, get_durations
from src.usf.parser import parse_file
from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.v4.extract.to_usf import write_dmc_usf
from pipelines.dmc.composer_asm import build_dmc_sid

_ROOT = str(Path(__file__).resolve().parents[2])


def build_from_cfg(cfg: DMCV4Config, hvsc_root: str | None = None) -> bytes:
    """SID → USF → SID (always through USF)."""
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    with tempfile.TemporaryDirectory() as td:
        usf_path = write_dmc_usf(cfg, td, hvsc_root=root)
        return build_dmc_sid(parse_file(usf_path))


def verify_dmc(cfg: DMCV4Config, hvsc_root: str | None = None) -> dict:
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    orig = os.path.join(root, cfg.sid_path)
    rebuilt = build_from_cfg(cfg, hvsc_root=root)
    return _verify_rebuilt(orig, rebuilt, bool(cfg.cia_period), root)


def _verify_rebuilt(orig: str, rebuilt: bytes, cia: bool, root: str) -> dict:
    """Capture + compare ONE (original, rebuilt-bytes) pair, per subtune.

    Factored out of `verify_dmc` unchanged so `verify_member` below can
    reuse the identical verdict for members whose real build path is not
    the single-player config one."""
    db = load_database(os.path.join(root, 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(rebuilt)
        tmp = f.name
    out = {'subtunes': {}, 'ok': True}
    try:
        from seed_disassembly import parse_psid
        from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
        n = parse_psid(orig)['songs']
        _cap = writelog_per_irq_capture if cia else writelog_capture
        # An RSID original is SKIPPED by siddump unless forced, and a skipped
        # capture is EMPTY — which reads as a partial with nothing to
        # localize rather than as a failure to capture. Force it for the
        # orig; the rebuild is always PSID, so the flag is a no-op there.
        rsid = open(orig, 'rb').read(4) == b'RSID'

        def _capture(path, **kw):
            return _cap(path, force_rsid=rsid and path == orig, **kw)

        # Subtunes are independent, and within one subtune the orig and
        # rebuild captures are independent siddump runs over different files.
        # Both were serialized. THREADS, not a Pool: the work is subprocess-
        # bound, and this is called from inside a regression Pool worker where
        # a nested Pool is illegal (daemonic) — see src/jobs.py.
        def _one(sub: int):
            dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
            with ThreadPoolExecutor(max_workers=2) as ex2:
                fa = ex2.submit(_capture, orig, subtune=sub, duration=dur)
                fb = ex2.submit(_capture, tmp, subtune=sub, duration=dur)
                a, b = fa.result(), fb.result()
            if cia:
                # CIA multispeed: the original is driven by a CIA timer at
                # 2-6x. Capture BOTH per play() invocation (the rebuild
                # programs the same latch, so both run at the same rate)
                # and flat-compare the play streams over their overlap +
                # a one-frame length tolerance (Trap C / CIA bucketing).
                r = compare_instruction_stream(a, b)
                la, lb = r['len_all_a'], r['len_all_b']
                # match_all == min(len) already proves the shorter stream
                # is a full prefix of the longer; the length tolerance only
                # guards against a rebuild that HALTS early. At a multispeed
                # rate the capture boundary lands a couple frames off, so
                # the tolerance is relative (0.5%, min 128 writes).
                full = (r['match_all'] == min(la, lb)
                        and abs(la - lb) <= max(128, max(la, lb) // 200))
                return sub, {
                    'is_full': full, 'match': r['match_all'],
                    'overlap': min(la, lb), 'len_a': la, 'len_b': lb,
                }, full
            else:
                r = compare_instruction_stream(a, b, mode='trichotomy')
                if not r['is_full']:
                    # C21: an orig whose INIT SPILLS past the frame-0 bucket
                    # (Rowdy's relocating wrapper banks + copies ~10 pages +
                    # runs the copied player's init = 2-3 frames, so its init
                    # writes land in the flat capture's "play" frames and the
                    # trichotomy compare misaligns from write 0). RETRY with
                    # the per-play() capture — there the init prefix is
                    # everything before the first play ENTRY, immune to
                    # bucket spill — and apply the ratified CIA-branch
                    # play-stream verdict. FULL members never reach this
                    # (zero-regression); a flip to full carries the same
                    # strict flat play-stream evidence as every CIA member.
                    a2 = writelog_per_irq_capture(
                        orig, subtune=sub, duration=dur,
                        force_rsid=rsid, keep_init=True)
                    b2 = writelog_per_irq_capture(
                        tmp, subtune=sub, duration=dur, keep_init=True)
                    # Check A stays (C15: never relax the verdict): end-of-
                    # init chip state = last write per register over the
                    # init chunk (|N, both sides symmetric — the Kordiaukis
                    # keep_init machinery), then the play chunks flat.
                    def _st(ch):
                        st = {}
                        for (_c, reg, val) in (ch[0] if ch else []):
                            st[reg] = val
                        return st
                    state2 = _st(a2) == _st(b2)
                    r2 = compare_instruction_stream(a2[1:], b2[1:])
                    la, lb = r2['len_all_a'], r2['len_all_b']
                    full2 = (state2 and r2['match_all'] == min(la, lb)
                             and abs(la - lb) <= max(128, max(la, lb) // 200))
                    if full2:
                        return sub, {
                            'is_full': True, 'state_match': True,
                            'play_match': r2['match_all'],
                            'overlap': min(la, lb),
                            'via': 'per_irq_retry',
                        }, True
                return sub, {
                    'is_full': r['is_full'], 'state_match': r['state_match'],
                    'play_match': r['play_match'], 'overlap': r['play_overlap'],
                    'first_play_diff': r.get('first_play_diff'),
                }, r['is_full']

        if n > 1:
            with ThreadPoolExecutor(max_workers=default_jobs(cap=n)) as ex:
                rows = list(ex.map(_one, range(n)))
        else:
            rows = [_one(s) for s in range(n)]
        for sub, entry, full in rows:          # re-assembled in subtune order
            out['subtunes'][sub] = entry
            out['ok'] &= bool(full)
    finally:
        os.unlink(tmp)
    return out


def detect_v4_build_path(rel: str, hvsc_root: str | None = None) -> dict:
    """Which v4 BUILD PATH a member takes, as the detector objects plus a
    `kind` name. THE one place that ordering lives.

    The order is load-bearing and is not alphabetical: 2SID first, then
    medley, then compilation, then multiplex, each guarded on the previous
    having declined — a compilation probe run against a 2SID member answers a
    different question. Factored out of `verify_member` (2026-08-23) so the
    router can ask "what path is this?" without becoming yet another copy;
    `project_dmc` records that this dispatch already lives in four places and
    that each copy is where ledger C20's fourth layer recurs.

    Detection only — it builds nothing and raises nothing about support."""
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    from pipelines.dmc.v4.factory import dmc_v4_config_2sid
    from pipelines.dmc.v4.compilation import (detect_compilation,
                                              detect_medley, detect_multiplex)
    cfgs2 = dmc_v4_config_2sid(rel, hvsc_root=root)
    med = detect_medley(rel, hvsc_root=root) if cfgs2 is None else None
    comp = (None if (cfgs2 is not None or med is not None)
            else detect_compilation(rel, hvsc_root=root))
    mux = (detect_multiplex(rel, hvsc_root=root)
           if (cfgs2 is None and med is None and comp is None) else None)
    if cfgs2 is not None:
        kind = 'multisid'
    elif med is not None:
        kind = 'medley'
    elif comp is not None:
        kind = ('compilation'
                if all(k == 'dmc' for k in (comp.get('kinds') or []))
                else 'heterogeneous')
    elif mux is not None:
        kind = 'multiplex'
    else:
        kind = 'single'
    return {'kind': kind, 'cfgs2': cfgs2, 'medley': med,
            'compilation': comp, 'multiplex': mux}


def verify_member(rel: str, hvsc_root: str | None = None) -> dict:
    """Verify one member through the CANONICAL DISPATCH — the build path the
    family batch takes — instead of assuming the single-player config path.

    Why this exists (found 2026-08-22 by the portfolio re-derivation): the
    regression harness built every DMC portfolio member with
    `dmc_v4_config(sid)`, so a member whose real path is a COMPILATION
    (ledger C31: N packed players + a per-subtune dispatch wrapper) was
    built as a single player and read as REGRESSED — sub 0 FULL, the rest
    garbage, the textbook C31 signature. Both members the new portfolios
    pulled in (Defuzion_3, Nyaaaah_9) are exactly that. This is ledger
    C20's fourth layer one tool over: a consumer re-deriving the dispatch
    instead of taking the one the verdict was earned on.

    An unsupported path RAISES rather than silently falling back to the
    single-player build — a wrong-path FULL is the failure mode C20 is
    about; a loud failure in regression is the correct outcome.
    """
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    orig = os.path.join(root, rel)
    from pipelines.dmc.v4.factory import dmc_v4_config
    d = detect_v4_build_path(rel, hvsc_root=root)
    cfgs2, med, comp, mux = d['cfgs2'], d['medley'], d['compilation'], d['multiplex']
    if cfgs2 is None and med is None and comp is None and mux is None:
        # single player: unchanged path, so every member that passed before
        # takes exactly the same code as before.
        return verify_dmc(dmc_v4_config(rel, hvsc_root=root), hvsc_root=root)
    if comp is not None and all(k == 'dmc' for k in (comp.get('kinds') or [])):
        from pipelines.dmc.v4.extract.to_usf import write_dmc_compilation_usf
        with tempfile.TemporaryDirectory() as td:
            usf = write_dmc_compilation_usf(rel, comp, td, hvsc_root=root)
            rebuilt = build_dmc_sid(parse_file(usf))
        with open(orig, 'rb') as f:
            hdr = f.read(0x16)
        cia = len(hdr) >= 0x16 and int.from_bytes(hdr[0x12:0x16], 'big') != 0
        return _verify_rebuilt(orig, rebuilt, cia, root)
    raise RuntimeError(
        f'verify_member: {rel} builds through the {d["kind"]} path, which this '
        f'entry does not implement — add it here rather than letting the '
        f'caller fall back to a single-player build (ledger C20).')
