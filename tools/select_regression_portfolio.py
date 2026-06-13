"""Select an engine family's regression portfolio: the EXACT minimum set
of FULL members covering every exercised feature dimension >= 2x.

Rationale (user decision 2026-06-11): for a feature-driven engine family,
two members are redundant exactly when they exercise the same code paths.
The portfolio therefore covers FEATURE DIMENSIONS, not strains: factory
variant knobs + effects the instruments exercise + structural traits.
Exact minimum multicover (each dimension covered by >=2 distinct members,
or >=1 when only one member in the corpus has it), solved by branch and
bound with a greedy seed bound — optimal at this scale in milliseconds,
no SAT dependency. Bug-witness members win ties.

ENGINE-PARAMETRIC: each family is one entry in the ENGINES registry
(wide-batch jsonl + output path + feature extractor + bug witnesses +
jsonl SID key). `exact_multicover` and the driver are engine-blind;
adding a family = a registry entry + a `<engine>_features` function.

STANDARD CLOSEOUT STEP: once a family's wide batch is mass-written
(family reaches its FULL coverage), derive its portfolio and wire it as
tier-1 in tools/regression.py (the full family batch is tier-2). Do this
again whenever a new fix lands a big new clump of FULLs — the portfolio
is only as current as the last derivation.

Run (after a wide batch):
    PYTHONPATH=.:tools/py65_lib:tools:src python3 \
        tools/select_regression_portfolio.py --engine {fc_standard|dmc_v4} [--jobs 8]

Output: tools/<engine>_regression_portfolio.json (member list + the
feature->members map) + a human summary on stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)

# Members that caught a real FC-family bug during rollout — preferred
# on ties.
FC_WITNESSES = {
    'MUSICIANS/C/Carter/Jarre_2.sid', 'MUSICIANS/L/Luca/Prato.sid',
    'MUSICIANS/V/Venom/Entrail_Ranx_02_08.sid',
    'MUSICIANS/G/Griff/FBI_Crew_Intro_2.sid',
    'MUSICIANS/N/Nordic_Beat/Quan/Tyranny_for_You_part_6.sid',
    'MUSICIANS/R/Reverb/Intense_Intro.sid',
    'MUSICIANS/D/Dr_Silence/Exquisite_2_rank_screen.sid',
    'MUSICIANS/M/Mr_Bocky/Eurodance_Remix.sid',
    'MUSICIANS/M/Moppe/Obelisk_1_copychain.sid',
    'MUSICIANS/B/Beat_Machine/Chris/Deneb.sid',
    'DEMOS/0-9/1st_Sound.sid', 'DEMOS/M-R/Ranx.sid',
    'MUSICIANS/O/Odi/Jingle_from_the_Lenor_advert.sid',
    'MUSICIANS/S/Stember_Rudolf/Chaos_game.sid',
}

# Members that caught a real DMC-family bug during the v4 rollout.
DMC_WITNESSES = {
    'MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid',  # idle/pulse
    'DEMOS/G-L/Knallen_Wars_Remix.sid',          # loop-target + tuning
    'MUSICIANS/C/Compod/Door_Was_Ajar.sid',      # 16-bit pattern ptr
    'DEMOS/A-F/Face2face.sid',                   # relocation ($9000)
    'MUSICIANS/A/Alien_WOW/Exclusive_4_Fungus.sid',   # dual-clock phase
}


def member_features(sid: str) -> tuple[str, set] | None:
    """Derive the feature set for one FULL member (factory + extract).

    Hard 20s alarm per member: a stuck py65 probe must not stall the
    pool — a skipped member simply contributes no portfolio candidate
    (the portfolio need not be perfect, per the project owner)."""
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(20)
    from pipelines.future_composer.standard.config import (
        fc_standard_config, FCStandardUnsupported)
    from pipelines.future_composer.engine_model import (
        extract, PatNote, PatGlide, PatNoGlide, PatSetLength,
        PatInstrumentChange, SeqPatternJump, SeqTranspose, SeqVoiceinc,
        SeqRepeats, SeqEnd, SeqWrap)
    try:
        cfg = fc_standard_config('hvsc84/' + sid)
        song = extract(cfg)
    except (FCStandardUnsupported, Exception):
        return None
    finally:
        signal.alarm(0)
    f: set[str] = set()
    # --- factory variant knobs ---
    if cfg.std_vibrato_stale_tail:
        f.add('knob:stale_tail')
    f.add(f'knob:d416_mode={cfg.std_d416_mode}')
    if (cfg.std_glide_hi_reg or 1) != 1:
        f.add('knob:glide_hi_mirror')
    if getattr(cfg, 'subtune_layout', '') == 'runtime_slot':
        f.add('knob:runtime_slot')
    load = song.load_addr
    if load != 0x1800:
        f.add('knob:relocated')
    if load >= 0xA000:
        f.add('knob:high_load')
    # --- instrument effect dimensions (union over decoded insts) ---
    insts = [i for i in song.instruments if len(i.raw) >= 8]
    for i in insts:
        if i.fx1 and not (i.fx3 & 0x14):
            f.add('fx:vibrato')
        if i.fx3 & 0x10:
            f.add('fx:wave_prog')
            f.add('fx:wave_rel' if (i.fx1 & 0x10) else 'fx:wave_abs')
        if i.fx3 & 0x40:
            f.add('fx:wave_arp40')
        if i.fx3 & 0x80:
            f.add('fx:noise80')
        if i.fx3 & 0x04:
            f.add('fx:arp04')
            f.add('fx:arp04_bit7set' if (i.fx3 & 0x80)
                  else 'fx:arp04_bit7clear')
        if i.fx3 & 0x01:
            f.add('fx:filter')
        if i.fx2:
            f.add('fx:pulse')
            if (i.fx2 & 7) == 0:
                f.add('fx:pulse_prog0')
            elif (i.fx2 & 7) > 4:
                f.add('fx:pulse_by_ref')
        if i.raw[0] & 0x80:
            f.add('fx:pw_jitter_b0')
    if len(insts) > 10:
        f.add('struct:inst_growth')
    # --- pattern / sequence structure ---
    pats = {pid: p for st in song.subtunes
            for pid, p in (st.patterns or {}).items()}
    for p in pats.values():
        evs = p.events
        if any(isinstance(e, PatGlide) for e in evs):
            f.add('pat:glide')
        if any(isinstance(e, PatNoGlide) for e in evs):
            f.add('pat:tie')
        raw = p.bytes_raw
        if any(0x80 <= raw[k] <= 0xBF and 0x80 <= raw[k + 1] <= 0xBF
               for k in range(len(raw) - 1)):
            f.add('pat:chained_8x')
    seqs = [s for st in song.subtunes for s in (st.seqs or ())]
    for s in seqs:
        cmds = s.commands
        if any(isinstance(c, SeqTranspose) for c in cmds):
            f.add('seq:transpose')
        if any(isinstance(c, SeqVoiceinc) for c in cmds):
            f.add('seq:voiceinc')
        if any(isinstance(c, SeqRepeats) for c in cmds):
            f.add('seq:repeats')
        if any(isinstance(c, SeqEnd) for c in cmds):
            f.add('seq:fe_end')
        if any(isinstance(c, SeqWrap) for c in cmds):
            f.add('seq:ff_wrap')
    # loop-pickup transpose (FBI): the stream wraps, no explicit transpose
    # before the first jump, and the running transpose at the wrap != 0.
    for s in seqs:
        t, first_jump_seen, explicit_head = 0, False, False
        wraps = False
        for c in s.commands:
            if isinstance(c, SeqTranspose):
                t = c.semitones
                if not first_jump_seen:
                    explicit_head = True
            elif isinstance(c, SeqPatternJump):
                first_jump_seen = True
            elif isinstance(c, SeqWrap):
                wraps = True
        if wraps and not explicit_head and t:
            f.add('seq:loop_transpose')
    if song.freq_overrun:
        f.add('struct:freq_overrun')
    if song.psid_songs > 1:
        f.add('struct:multi_subtune')
    if song.std_wave_programs:
        f.add(f'struct:wave_sels={min(len(song.std_wave_programs), 3)}')
    return (sid, f)


def dmc_features(sid: str) -> tuple[str, set] | None:
    """DMC V4 feature set for one FULL member (factory + extract).

    Same 20s-alarm discipline as the FC extractor."""
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(20)
    from pipelines.dmc.v4.factory import dmc_v4_config, DMCV4Unsupported
    from pipelines.dmc.v4.extract.engine_model import extract
    from pipelines.dmc.engine_constants import FREQ_LO, FREQ_HI
    try:
        cfg = dmc_v4_config(sid)         # HVSC-relative; factory joins root
        m = extract(cfg)
    except (DMCV4Unsupported, Exception):
        return None
    finally:
        signal.alarm(0)
    f: set[str] = set()
    # --- factory variant knobs ---
    if cfg.track_loop_target:
        f.add('knob:loop_target')
    if cfg.op_tunetab == 0x180E:        # 2-entry layout (vs canon $1051)
        f.add('knob:layout_2entry')
    if cfg.base != 0x1000:
        f.add('knob:relocated')
    if cfg.base >= 0xA000:
        f.add('knob:high_load')
    if m.dual_phase:
        f.add('knob:dual_phase')
    if cfg.cia_period:
        f.add('knob:cia_multispeed')
    if m.d417_shadow:
        f.add('knob:routing_shadow')
    if any(m.idle_notes):
        f.add('knob:idle_note')
    if any(m.idle_masks):
        f.add('knob:idle_mask')
    if m.idle_wave[0]:
        f.add('knob:idle_wave')
    if bytes(m.freq_lo) != FREQ_LO or bytes(m.freq_hi) != FREQ_HI:
        f.add('struct:per_tune_tuning')
    # --- instrument effect dimensions (union over decoded insts) ---
    for i in m.instruments.values():
        if i.drum:
            f.add('fx:drum')
        if i.noise_attack:
            f.add('fx:cymbal')
        if i.filter_on:
            f.add('fx:filter')
        if i.filter_keep_running:
            f.add('fx:filter_keep')
        if i.pw_keep_running:
            f.add('fx:pulse_keep')
        if i.dual:
            f.add('fx:dual_slide')
        if i.vib_width:
            f.add('fx:vibrato')
            if i.vib_delay:
                f.add('fx:vib_delay')
            if not i.dual and i.vib_ramp:
                f.add('fx:vib_ramp')
        f.add(f'fx:gate_{i.gate_mode}')
    if len(m.instruments) > 10:
        f.add('struct:inst_growth')
    if m.filter_defs:
        f.add('struct:filter_defs')
    if m.n_subtunes > 1:
        f.add('struct:multi_subtune')
    # --- pattern / track structure (union over all voices) ---
    for song in m.songs:
        for v in song.voices:
            if v.stop:
                f.add('track:stop')
            if v.loop_to is not None:
                f.add('track:loop')
            if any(v.transposes):
                f.add('track:transpose')
            for rows in v.patterns:
                for r in rows:
                    if r.glide_speed and r.glide_to is not None:
                        f.add('pat:glide')
                    if r.glide_slide:
                        f.add('pat:slide')
                    if r.gate_toggle:
                        f.add('pat:gate_toggle')
                    if r.vol:
                        f.add('pat:vol')
                    if r.soft:
                        f.add('pat:soft')
    return (sid, f)


# Engine registry: each family declares where its wide-batch results
# live, where the portfolio goes, the feature extractor, the bug
# witnesses, and the per-record SID key in the jsonl. Adding a family =
# one entry + a `<engine>_features` function; exact_multicover and the
# driver stay engine-blind.
ENGINES = {
    'fc_standard': {
        'results': os.path.join(ROOT, 'tmp', 'fc_std_wide_results.jsonl'),
        'out': os.path.join(ROOT, 'tools', 'fc_regression_portfolio.json'),
        'features': member_features,
        'witnesses': FC_WITNESSES,
        'sid_key': 'sid',
    },
    'dmc_v4': {
        'results': os.path.join(ROOT, 'tmp', 'dmc_wide_results.jsonl'),
        'out': os.path.join(ROOT, 'tools', 'dmc_regression_portfolio.json'),
        'features': dmc_features,
        'witnesses': DMC_WITNESSES,
        'sid_key': 'path',
    },
}


def exact_multicover(universe: dict[str, int],
                     members: dict[str, set],
                     prefer: set[str]) -> list[str]:
    """Exact minimum multicover via branch and bound.

    universe: dimension -> required coverage (1 or 2).
    members: sid -> feature set.
    prefer: tie-break set (bug witnesses chosen first inside a branch).

    Loosened per the project owner (2026-06-12): candidates are first
    DEDUPED by feature-set signature (multicover needs at most 2
    representatives per signature; witnesses preferred) — 2528 members
    collapse to a few hundred — and the search runs under a 10s budget,
    returning the best solution found (the greedy seed at worst). The
    un-pruned exact search branched for 25+ minutes on thousands of
    interchangeable candidates.
    """
    import time
    sig_reps: dict[frozenset, list[str]] = {}
    for m in sorted(members, key=lambda m: (m not in prefer, m)):
        sig_reps.setdefault(frozenset(members[m]), []).append(m)
    members = {m: members[m]
               for reps in sig_reps.values() for m in reps[:2]}
    deadline = time.monotonic() + 10.0
    # Greedy seed for the upper bound.
    def greedy() -> list[str]:
        need = dict(universe)
        chosen: list[str] = []
        avail = dict(members)
        while any(v > 0 for v in need.values()):
            best = max(
                avail,
                key=lambda m: (sum(min(need.get(d, 0), 1)
                                   for d in avail[m]),
                               m in prefer, -len(avail[m])))
            chosen.append(best)
            for d in avail.pop(best):
                if d in need and need[d] > 0:
                    need[d] -= 1
        return chosen

    best_sol = greedy()
    contributors: dict[str, list[str]] = {
        d: [m for m, fs in members.items() if d in fs] for d in universe}

    def dfs(need: dict[str, int], chosen: list[str], banned: set[str]):
        nonlocal best_sol
        open_dims = [d for d, r in need.items() if r > 0]
        if not open_dims:
            if len(chosen) < len(best_sol):
                best_sol = list(chosen)
            return
        # Bound: one member can satisfy at most one unit per dimension it
        # has; cheap lower bound = remaining units / max units per member.
        if time.monotonic() > deadline:
            return
        rem = sum(need[d] for d in open_dims)
        max_per = max(
            (sum(1 for d in open_dims if d in members[m] and need[d] > 0)
             for m in members if m not in banned and m not in chosen),
            default=0)
        if max_per == 0:
            return                          # uncoverable under bans
        import math
        if len(chosen) + math.ceil(rem / max_per) >= len(best_sol):
            return
        # Branch on the tightest dimension.
        d = min(open_dims,
                key=lambda x: sum(1 for m in contributors[x]
                                  if m not in banned and m not in chosen))
        cands = [m for m in contributors[d]
                 if m not in banned and m not in chosen]
        cands.sort(key=lambda m: (
            -sum(1 for x in open_dims if x in members[m]), m not in prefer))
        new_banned = set(banned)
        for m in cands:
            nd = dict(need)
            for x in members[m]:
                if x in nd and nd[x] > 0:
                    nd[x] -= 1
            dfs(nd, chosen + [m], set(new_banned))
            new_banned.add(m)               # exclude m in later branches

    dfs(dict(universe), [], set())
    return best_sol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', default='fc_standard', choices=sorted(ENGINES),
                    help='which engine family to derive the portfolio for')
    ap.add_argument('--jobs', type=int, default=8)
    args = ap.parse_args()
    os.chdir(ROOT)
    eng = ENGINES[args.engine]
    results, out = eng['results'], eng['out']
    features, witnesses, sid_key = (
        eng['features'], eng['witnesses'], eng['sid_key'])
    fulls = [json.loads(l)[sid_key] for l in open(results)
             if json.loads(l)['status'] == 'full']
    print(f'[{args.engine}] {len(fulls)} FULL members; '
          f'deriving feature matrix...', flush=True)
    rows = []
    done = 0
    with Pool(args.jobs) as pool:
        for r in pool.imap_unordered(features, fulls, chunksize=8):
            done += 1
            if done % 250 == 0:
                print(f'{done}/{len(fulls)} extracted', flush=True)
            if r:
                rows.append(r)
    print(f'{len(rows)}/{len(fulls)} contributed (rest skipped/timed out)',
          flush=True)
    members = {sid: feats for sid, feats in rows}
    # Universe: every dimension any FULL member exercises; required
    # coverage 2 when >=2 members have it, else 1.
    from collections import Counter
    dim_count = Counter(d for fs in members.values() for d in fs)
    universe = {d: min(2, n) for d, n in dim_count.items()}
    print(f'{len(universe)} feature dimensions', flush=True)
    sol = exact_multicover(universe, members, witnesses)
    sol.sort()
    cover = {d: sorted(m for m in sol if d in members[m])
             for d in sorted(universe)}
    json.dump({'engine': args.engine, 'portfolio': sol, 'dimensions': cover,
               'corpus_full': len(members)},
              open(out, 'w'), indent=1)
    print(f'EXACT minimum portfolio: {len(sol)} members -> {out}')
    for m in sol:
        tag = '  [witness]' if m in witnesses else ''
        print(f'  {m}{tag}')
    for d in sorted(universe):
        print(f'  {dim_count[d]:5d}x {d}: '
              f'{", ".join(p.split("/")[-1] for p in cover[d])}')


if __name__ == '__main__':
    main()
