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

from src.jobs import default_jobs  # noqa: E402

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

# Family-2 tie-break witnesses: the members whose LEVER would break
# silently if it lost portfolio cover — every mechanism landed during the
# f2 grind, each the sole (or first) carrier of its class.
DMC_F2_WITNESSES = {
    'MUSICIANS/A/Ass_It/Blast_n_Scream.sid',          # C31 dead-cargo split
    'MUSICIANS/C/Comer/Zwei_Bereten_Preview.sid',     # cross-inst declutter
    'MUSICIANS/T/Tichelmann_Kay/For_Nitro.sid',       # C11 vib-inc read site
    'MUSICIANS/A/Arthur/Over_and_Out.sid',            # C31 medley_switch
    'MUSICIANS/S/Spang_Jesper/Sams016.sid',           # subtune_songs fallthru
    'MUSICIANS/A/Alien_WOW/Knowledge_Posse_tune_3.sid',   # C18 pulse_tail_hi
    'MUSICIANS/M/Moon/Final_Game.sid',                # C29 past-EOF sector
    'MUSICIANS/C/Comer/Artris.sid',                   # C8 wave-pool split
    'MUSICIANS/S/Spang_Jesper/Ofyron_Gadaf.sid',      # C16 filter_before_voice
    'MUSICIANS/J/Jadawin/Conversion.sid',             # C9 $FF loop immediate
    'MUSICIANS/F/Freeze/Petshopmix.sid',              # C19 vib_swell_ror
    'MUSICIANS/O/Orcan/Inside.sid',                   # C19 filter_idx_eor
    'MUSICIANS/P/PFK/Childs_Play.sid',                # C19 filter_dur_dead
    'MUSICIANS/B/Brian/Delta_Zak.sid',                # C19 dur_fetch_underflow
    'MUSICIANS/R/Riot/Sub_Burner.sid',                # C31 three levers
    'GAMES/S-Z/Session.sid',                          # C8 4th widening
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
        cfg = fc_standard_config('hvsc85/' + sid)
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
    if getattr(song, 'offtable_freq', None):
        f.add('struct:offtable_freq')
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
    # 90s, not 20: an observe-confirm wedge probe (track_loop_dead's
    # full-song siddump) legitimately runs ~1 min on rare members, and the
    # alarm's TimeoutError lands inside the probe's own `except Exception`
    # — SILENTLY DROPPING the wedge key instead of failing the member
    # (Solar_Energy lost `wedge:track_loop_dead` this way). Only ~4 members
    # corpus-wide carry the heavy path, so the derivation cost is bounded.
    signal.alarm(90)
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
    # --- r74-r177 classes (2026-08-03 — the criterion-4 GAP closure).
    # GENERIC wedge dimensions: one per extra_params key, so every C19/C18/
    # C23/C24 probe knob — current AND FUTURE — is a portfolio dimension the
    # moment its probe lands. The 4-member regression of Jul 22-26 happened
    # exactly because these were absent: no portfolio member carried the
    # affected classes, so the per-round gate was blind to them.
    for k in (cfg.extra_params or {}):
        f.add(f'wedge:{k}')
    for k in (getattr(m, 'extra_params', None) or {}):
        f.add(f'wedge:{k}')
    if getattr(cfg, 'loop_reset_pos', None) is not None:
        f.add('knob:loop_reset')                      # C13 sync hook
    if getattr(cfg, 'loop_note_inject', False):
        f.add('knob:loop_note_inject')                # C13 third form
    if getattr(cfg, 'switch_retrig', False):
        f.add('knob:switch_retrig')                   # C19 $7D retrig
    if getattr(cfg, 'transpose_neg_bias', 1) != 1:
        f.add('knob:transpose_neg_bias')              # C19 28th occ
    if getattr(cfg, 'forced_subtune', None) is not None \
            or getattr(cfg, 'subtune_songs', None) is not None:
        f.add('knob:forced_record')                   # C19/C31 forced record
    if getattr(cfg, 'subtune_state_copy', None):
        f.add('knob:state_copy')                      # C37 resume wrapper
    if getattr(cfg, 'data_post_init', False):
        f.add('knob:post_init_data')                  # C26 unpacker (the
                                                      # C29-overlay members
                                                      # live in this class)
    if getattr(cfg, 'curnote_addr', None) is not None:
        f.add('knob:dataflow_path')                   # re-assembled build
    if getattr(m, 'play_repeat', 1) > 1:
        f.add('knob:play_repeat')                     # C24 whole-play repeat
    if getattr(m, 'wavepos_layout', False):
        f.add('knob:wavepos_layout')                  # C11 layout pool
    if getattr(m, 'wave_table_norm', None) is not None:
        f.add('struct:wave_table_norm')               # C32 stated wave table
    if getattr(m, 'offtable_vibdepth', None):
        f.add('fx:offtable_vibdepth')
    _recs = [r for i in m.instruments.values()
             for r in (i.offtable_freq or [])]
    if _recs:
        f.add('fx:offtable_freq')                     # C6 off-table reads
    if any(len(r) > 4 and r[4] for r in _recs):
        f.add('fx:offtable_live')                     # C11 live redirects
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


MASM_WITNESSES = {
    # The C6 off-table freq read — the family's dominant residue class, and
    # both of its read sites (the arp path masks to 7 bits, the note path
    # does not, so they overrun differently).
    'offtable:arp', 'offtable:note',
    # The orderlist targeted-loop target ($FD nn); the composer wrapped to
    # entry 0 regardless until 2026-07-22.
    'track:loop_target',
    # Idle-mid-note priming: a voice whose first event is a rest/hold plays
    # the work-file leftovers instead of a note-init.
    'init:note_active', 'init:sliding',
    # The post-preset dispatch position (ledger C34).
    'pat:preset_rest',
}


def masm_features(sid: str) -> tuple[str, set] | None:
    """Music Assembler feature set for one FULL member.

    Same 20s-alarm discipline as the FC/DMC extractors."""
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(20)
    from pipelines.music_assembler.extract.model import extract
    from pipelines.music_assembler.extract.to_usf import offtable_reach
    try:
        m = extract(sid)
    except Exception:
        return None
    finally:
        signal.alarm(0)
    f: set[str] = set()
    f.add('speed:%d' % min(m.speed, 8))
    if len(m.presets) > 12:
        f.add('struct:inst_growth')

    # --- off-table freq reads (ledger C6), split by read site ---
    reach = offtable_reach(m)
    if reach:
        f.add('offtable:any')
        arp_of = {p.id: m.arps.get(p.arp_index) for p in m.presets}
        for pid, idxs in reach.items():
            if arp_of.get(pid) is not None:
                f.add('offtable:arp')
        seq_tr = {}
        for t in m.tracks:
            for e in t.entries:
                seq_tr.setdefault(e.seq, set()).add(e.transpose)
        for sn, ev in m.sequences.items():
            for e in ev:
                if e.kind == 'note' and any(
                        (tr + e.value) & 0xFF >= 96
                        for tr in seq_tr.get(sn, {0})):
                    f.add('offtable:note')

    # --- instrument effect dimensions ---
    for p in m.presets:
        if p.fx & 0x40:
            f.add('fx:pulse_linear')
        elif p.fx & 0x20:
            f.add('fx:pulse_bidir')
        if p.fx & 0x10 and p.vib_depth:
            f.add('fx:vibrato')
            if p.vib_delay:
                f.add('fx:vib_delay')
        a = m.arps.get(p.arp_index)
        if a is not None:
            f.add('fx:arp_loop' if a.loops else 'fx:arp_stop')
            for st in a.steps:
                f.add('fx:arp_abs' if st.absolute else 'fx:arp_rel')
                if st.filter_lp:
                    f.add('fx:arp_filter')

    # --- init priming (trichotomy §4.5) ---
    def _pv(key, i):
        v = m.prime.get(key)
        return v[i] if isinstance(v, list) else 0
    for i in range(3):
        flg = _pv('noteflg', i)
        if flg & 0x40:
            f.add('init:note_active')
        if flg & 0x20:
            f.add('init:sliding')
        if _pv('pwlo', i) or _pv('pwhi', i):
            f.add('init:pulse_width')
    if m.prime.get('fdur') or m.prime.get('fvel'):
        f.add('init:filter_sweep')
    if m.prime.get('fcutr') or m.prime.get('fdurr'):
        f.add('init:filter_arm')

    # --- track / pattern structure ---
    for t in m.tracks:
        if not t.loops:
            f.add('track:stop')
        else:
            f.add('track:loop_target' if t.loop_to else 'track:loop')
        if any(e.transpose for e in t.entries):
            f.add('track:transpose')
        if any(e.repeat for e in t.entries):
            f.add('track:repeat')
    for ev in m.sequences.values():
        prev = None
        for e in ev:
            if e.kind == 'note':
                if e.legato:
                    f.add('pat:legato')
                if e.slide:
                    f.add('pat:slide')
                if e.filt:
                    f.add('pat:filter_sweep' if e.filt[1] else 'pat:filter_off')
            elif e.kind == 'hold':
                f.add('pat:hold')
            elif e.kind == 'rest':
                f.add('pat:rest')
                # the ledger-C34 position: a rest the PRESET handler decoded
                if prev is not None and prev.kind == 'preset':
                    f.add('pat:preset_rest')
            prev = e
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
        # family 1, #85 member set (5,445), fully re-verified 2026-08-22 at
        # the current code hash. NOT `dmc_wide_results.jsonl` — that is the
        # PRE-#85 working file (5,401 rows, missing 47 members) and pointing
        # a derivation at it silently derives from a stale member set.
        'results': os.path.join(ROOT, 'tmp', 'dmc_f1_85_results.jsonl'),
        'out': os.path.join(ROOT, 'tools', 'dmc_regression_portfolio.json'),
        'features': dmc_features,
        'witnesses': DMC_WITNESSES,
        'sid_key': 'path',
    },
    # FAMILY 2 (closed 2026-08-21 at 2,924/2,924). Its own entry, not a
    # merge into dmc_v4: the two families are separate wide batches with
    # separate results files, and f2 carries a mechanism set f1 never
    # exercises (the vib-swell/step wedges, pulse_tail_hi, the $FF loop
    # immediate, filter_before_voice, the C31 dispatch wrappers). Until
    # this landed, regression guarded all of f2 with FOUR hand-picked
    # canaries while every f2 lever of the Aug-21 grind was uncovered.
    # Same extractor (it is family-blind — generic over extra_params).
    'dmc_f2': {
        'results': os.path.join(ROOT, 'tmp', 'dmc_f2_85_results.jsonl'),
        'out': os.path.join(ROOT, 'tools',
                            'dmc_f2_regression_portfolio.json'),
        'features': dmc_features,
        'witnesses': DMC_F2_WITNESSES,
        'sid_key': 'path',
    },
    'music_assembler': {
        'results': os.path.join(ROOT, 'tmp', 'masm_wide_results.jsonl'),
        'out': os.path.join(ROOT, 'tools',
                            'masm_regression_portfolio.json'),
        'features': masm_features,
        'witnesses': MASM_WITNESSES,
        'sid_key': 'sid',
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
    ap.add_argument('--jobs', type=int, default=default_jobs())
    args = ap.parse_args()
    os.chdir(ROOT)
    eng = ENGINES[args.engine]
    results, out = eng['results'], eng['out']
    features, witnesses, sid_key = (
        eng['features'], eng['witnesses'], eng['sid_key'])
    # Append-only jsonl -> dedupe LAST-WINS (src/batch_results). Read naively, a
    # member that was `full` in an older generation and is now `partial` still
    # enters the FULL pool and can be SELECTED into the tier-1 portfolio, where
    # it would fail regression forever.
    from batch_results import load_latest
    _latest = load_latest(results, sid_key)
    fulls = [p for p, r in _latest.items() if r['status'] == 'full']
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
