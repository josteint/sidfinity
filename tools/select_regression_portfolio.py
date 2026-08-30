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
import random
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)

from src.jobs import default_jobs  # noqa: E402
from src.batch_results import store_path  # noqa: E402

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
    # --- THE FBDL SET (added 2026-08-22, `tools/fbdl_measure.py`) ---
    # Every full->non-full REGRESSION recoverable from f1's stored batch
    # generations. Measured: the 97-member tier-1 portfolio contained NONE of
    # them, i.e. 0/5 caught, 100% fault-detection loss on this family's real
    # history. Shi et al. (ISSTA'18, 1,478 real failed builds) found historical
    # detection is the ONLY predictor of a reduced suite's value — size
    # reduction scored R^2=0.00 and coverage loss was non-predictive — so these
    # five are worth more as portfolio members than any coverage dimension.
    # The first four are the ledger C20 sixth-layer incident: a net "+57 full"
    # closeout masked them, and they sat broken for a week.
    'MUSICIANS/F/Flash/Itinerant.sid',           # C29 play-time re-bank
    'MUSICIANS/F/Flash/Kan-Kan.sid',             # C29 play-time re-bank
    'MUSICIANS/F/Flash/Wind_of_Dead.sid',        # C29 play-time re-bank
    'MUSICIANS/T/Tomace/Other_Side.sid',         # C11 glide-leftover seed
    'MUSICIANS/B/Bakewell_Dwayne/Finale.sid',
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


# ⚠ WITNESSES ARE MEMBER PATHS, not dimension names — `exact_multicover` and
# `budget_cover` test `member in prefer/pinned`. (MASM_WITNESSES below holds
# dimension names, so MASM's tie-break is inert; left alone rather than
# silently re-deriving that family's portfolio here.)
DMC_V5_WITNESSES = {
    # Bug witnesses accumulate as the grind lands fixes: a member that WAS
    # broken and is now FULL gets pinned so it can never silently regress.
    # Pinned as HARD constraints per item 17(e) — historical detection was the
    # ONLY suite-reduction predictor that survived Shi et al.'s 1,478 real
    # failed builds (size reduction R^2=0.00), and we had been using it as a
    # tie-break only.
    'DEMOS/G-L/Katusha.sid',              # the family reference player
}

# Dimensions the portfolio must cover at DOUBLE the usual multiplicity: the
# v5 grind's measured lever classes (2026-08-22). Coverage here is what makes
# a regression in these classes visible to tier 1 at all.
DMC_V5_PIN_DIMS = {
    # The startup-leftover class — RE_NOTES FILTER ROUND 1 cause A. The v5
    # init's clear loop covers $17D5-$1845, so the $1006-$103F work-RAM gap
    # keeps file-image leftovers the first play frames sonify.
    'leftover:spdctr', 'leftover:notes', 'leftover:mvolfrac', 'leftover:filt',
    # The play-skip count ($1842): the canon init writes 2, but 77% of the
    # corpus writes 0. INVISIBLE to the flat write-stream verdict — which is
    # exactly why each value needs a carrier under some other gate.
    'knob:playskip_0', 'knob:playskip_1', 'knob:playskip_2',
    # The family-4 (Jupiter41) branch — a different play body entirely.
    'knob:family4',
    # C6 off-table freq reads: the ledger marks the class recurring for v5.
    'fx:offtable_freq',
}


def dmc_v5_features(sid: str) -> tuple[str, set] | None:
    """DMC V5 feature set for one FULL member (factory + extract).

    Mirrors `dmc_features`: factory knobs, structural shape, the uncleared
    startup leftovers, per-instrument effects and the sector/orderlist command
    vocabulary. Same alarm discipline — the v5 factory measures the CIA latch
    from a siddump run, so the budget is generous.
    """
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(120)
    from pipelines.dmc.v5.factory import dmc_v5_config, DMCV5Unsupported
    from pipelines.dmc.v5.extract.engine_model import extract
    try:
        cfg = dmc_v5_config(sid)
        m = extract(cfg)
    except (DMCV5Unsupported, Exception):
        return None
    finally:
        signal.alarm(0)
    f: set[str] = set()
    # --- factory / player-variant knobs ---
    if cfg.base != 0x1000:
        f.add('knob:relocated')
    if cfg.base >= 0xA000:
        f.add('knob:high_load')
    if cfg.cia_period:
        f.add('knob:cia_multispeed')
    if getattr(cfg, 'family4', False):
        f.add('knob:family4')
    if getattr(cfg, 'n_songs', None) is not None:
        f.add('knob:subplayer')            # C31 packed sub-player
    if getattr(cfg, 'post_init_sub', None) is not None:
        f.add('knob:post_init')            # C26/C31 relocating wrapper
    for k in (getattr(cfg, 'extra_params', None) or {}):
        f.add(f'wedge:{k}')                # generic: every future probe knob
    ps = getattr(m, 'play_skip', None)
    if ps is not None:
        f.add(f'knob:playskip_{min(int(ps), 3)}')
    # --- the uncleared $1006-$103F startup leftovers ---
    if m.lo_spdctr:
        f.add('leftover:spdctr')
    if any(m.lo_notes):
        f.add('leftover:notes')
    if m.lo_mvolfrac:
        f.add('leftover:mvolfrac')
    if m.lo_filtmode or m.lo_fchi or m.lo_fclo:
        f.add('leftover:filt')
    if getattr(m, 'family4', False):
        if any(getattr(m, 'f4_idle_notes', ()) or ()):
            f.add('leftover:f4_idle')
        if getattr(m, 'f4_filtmode', 0) or getattr(m, 'f4_fcinit', 0):
            f.add('leftover:f4_filt')
    # --- structural shape ---
    if len(m.subtunes) > 1:
        f.add('struct:multi_subtune')
    if len(m.instruments) > 10:
        f.add('struct:inst_growth')
    if len(m.sectors) > 40:
        f.add('struct:sector_growth')
    if m.filter:
        f.add('struct:filter_table')
    if m.pulse:
        f.add('struct:pulse_table')
    speeds = {s.speed for s in m.subtunes} or {m.speed}
    if len(speeds) > 1:
        f.add('struct:per_subtune_speed')
    if any(s.master_vol != 0x0F for s in m.subtunes):
        f.add('struct:master_vol')
    # --- instrument effects ---
    for i in m.instruments:
        if i.vib_width:
            f.add('fx:vibrato')
            if i.vib_delay:
                f.add('fx:vib_delay')
        if i.pulse_ptr:
            f.add('fx:pulse')
        if i.filter_ptr:
            f.add('fx:filter')
        if getattr(i, 'offtable_freq', None):
            f.add('fx:offtable_freq')      # C6
    # --- sector / orderlist command vocabulary ---
    for sec in m.sectors:
        for ev in sec:
            if ev[0] != 'note':
                f.add(f'cmd:{ev[0]}')
    for st in m.subtunes:
        for ol in st.orderlists:
            for ev in ol:
                if ev[0] in ('loop', 'transpose', 'end'):
                    f.add(f'track:{ev[0]}')
    return (sid, f)


BASIC_PIN_DIMS = {
    # The trace-lift's own decision points. basic_program has no "engine" to
    # probe — the engine IS the BASIC+KERNAL ROM — so its feature dimensions
    # are the LIFTER's structural choices, which is exactly where its bugs
    # live. Double-cover the ones that select a different code path.
    'struct:legato', 'struct:gated', 'struct:multi_template',
    'struct:song_end', 'struct:start_offset', 'fx:perstep_timbre',
}


def _bp_dur(sid: str) -> float:
    """The batch's own window rule, so a portfolio member is verified over the
    same span the batch verified it over (songlength*1.1, floor 15 s, NO upper
    cap — the cap was ledger C20's eighth layer)."""
    from src.songlengths import load_database, get_durations
    root = os.path.join(ROOT, 'hvsc85')
    db = load_database(os.path.join(root, 'DOCUMENTS', 'Songlengths.md5'))
    try:
        d = get_durations(os.path.join(root, sid), db)
        sl = d[0] if d else 10
    except Exception:
        sl = 10
    return max((sl or 10) * 1.1, 15.0)


def basic_program_features(sid: str) -> tuple[str, set] | None:
    """basic_program feature set: the TRACE-LIFT's structural decisions.

    Unlike every other family there is no player to probe — the engine is the
    BASIC interpreter — so the dimensions that matter are the ones the lifter
    branches on: gated vs legato segmentation, single vs multi positional
    template (ledger C17), song-end detection, start-frame offset, per-step
    timbre, voice count and step count.
    """
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(300)          # a lift runs a real capture; be generous
    try:
        from pipelines.basic_program import semantic_lift as S
        from pipelines.basic_program import usf_roundtrip as RT
        # ⚠ build_model takes an ABSOLUTE path. Handed an HVSC-relative one it
        # captures nothing and returns `unsupported: too_few_steps` — the exact
        # symptom CLAUDE.md documents for a MISSING ROM, so it reads as a broken
        # environment rather than a wrong argument. Every member returned None
        # until this was fixed.
        m = S.build_model(os.path.join(ROOT, 'hvsc85', sid), _bp_dur(sid),
                          multi_template=True, detect_song_end=True)
        if not m or m.get('unsupported'):
            return None
    except Exception:
        return None
    finally:
        signal.alarm(0)

    f: set[str] = set()
    f.add('struct:legato' if m.get('legato') else 'struct:gated')
    multi = m.get('multi') or []
    if len(multi) > 1:
        f.add('struct:multi_template')
        f.add(f'tmpl:k={min(len(multi), 8)}')
    if m.get('song_end'):
        f.add('struct:song_end')
    if m.get('start_frame'):
        f.add('struct:start_offset')
    try:
        if RT._perstep_timbre(m):
            f.add('fx:perstep_timbre')
    except Exception:
        pass
    try:
        if RT.is_clean(m):
            f.add('struct:clean')
    except Exception:
        pass
    steps = m.get('steps') or []
    f.add(f'steps:{min(len(steps) // 100, 6)}00+')
    # voices + globals actually written across the lifted steps
    regs = {w[-2] for s in steps
            for w in (list(s.get('attack') or []) + list(s.get('release') or []))}
    voices = {1 for r in regs if 0x00 <= r <= 0x06} | \
             {2 for r in regs if 0x07 <= r <= 0x0D} | \
             {3 for r in regs if 0x0E <= r <= 0x14}
    f.add(f'voices:{len(voices)}')
    if any(0x15 <= r <= 0x17 for r in regs):
        f.add('fx:filter')
    if any(r == 0x18 for r in regs):
        f.add('fx:mastervol')
    if m.get('pw_program'):
        f.add('fx:pw_program')
    if m.get('mod_inc') or m.get('mod_start'):
        f.add('fx:modulation')
    if m.get('masked'):
        f.add('struct:masked_template')
    if m.get('loop_to') is not None:
        f.add('struct:loop')
    init = {w[-2] for w in (m.get('init') or [])}
    if any(0x15 <= r <= 0x17 for r in init):
        f.add('init:filter')
    return (sid, f)


MASM_PIN_DIMS = {
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


def digi_organizer_features(sid: str) -> tuple[str, set] | None:
    """Digi-Organizer feature set for one FULL member.

    This family is verified CYCLE-STRICT (core tenet Mode 2), so its
    dimensions are the things that move CYCLES, not just values: the
    driver CLASS (each one a distinct mirrored cycle shape), the
    core-entry and core-tail variants, the NMI vector target, the PSID
    clock, the speed-poke forms, and the data shapes whose handling is a
    BRANCH in the mirrored player (degenerate vs explicit one-page
    sample rows — ledger C40 3e). Also the composer-side layout paths
    (relocated player, PCM overlap join, past-EOF PCM), which no other
    member exercises.
    """
    import signal

    def _bail(_sig, _frm):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _bail)
    signal.alarm(20)
    from pipelines.digi_organizer.extract import extract_model
    try:
        m = extract_model(sid)
    except Exception:
        return None
    finally:
        signal.alarm(0)
    f = {f'driver:{m.driver}',
         f'tail:{m.core_tail}',
         f'nmivec:{m.nmi_vec}',
         f'clock:{m.meta["clock"]}'}
    if m.port_preinit is not None:
        f.add(f'preinit:{m.preinit_form}')
    if m.driver_params.get('core_entry') == 'core40':
        f.add('entry:core40')
    if m.base_latch != 0x70:
        f.add('latch:nondefault')
    if m.driver_params.get('speed_poke') is not None:
        f.add('speed:poke_post')          # poke AFTER core init
    if 'speed_preinit' in m.driver_params:
        f.add('speed:poke_pre')           # poke BEFORE core init
    if m.order_term == 'stop':
        f.add('order:stop')
    # BOTH one-page forms are dimensions, and a member can carry both
    # (Arnie-Rap has one degenerate row beside two explicit ones) — the
    # branch they take differs, so neither excludes the other. NB
    # `m.samples` is post-clamp, so an explicit row is one the extract
    # did NOT record as degenerate.
    if m.onepage_degenerate:
        f.add('smptab:onepage_degenerate')     # the C40 3e branch
    if any(e - s == 1 and i not in m.onepage_degenerate
           for i, (s, e, _l) in m.samples.items()):
        f.add('smptab:onepage_normal')
    # composer-side layout paths. Thresholds, not observed placements:
    # these are the sizes at which the composer's canonical map (largest
    # hole 128 pages) and then its relocated map (~183 + 31) stop
    # fitting, so they name the member property that forces each path.
    ranges = {(s, e) for s, e, _l in m.samples.values()}
    if len(ranges) != len(m.samples):
        f.add('pcm:shared_range')
    if max((e - s for s, e in ranges), default=0) > 128:
        f.add('pcm:blob_over_128p')       # forces the relocated player
    if sum(e - s for s, e in ranges) > 192:
        f.add('pcm:total_over_192p')      # forces the overlap join
    from pipelines.digi_organizer.extract import load_image
    _meta, load, img = load_image(sid)
    if any((e << 8) > load + len(img) for _s, e in ranges):
        f.add('pcm:past_eof')             # C29 CPU-eye capture
    return sid, f


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
    # basic_program — the one family with no PLAYER to probe (the engine IS the
    # BASIC+KERNAL ROM), so its dimensions are the TRACE-LIFT's own structural
    # choices, which is where its bugs live. Its portfolio format carries a
    # per-member verify WINDOW, so this entry supplies an `emit` hook; the
    # driver is otherwise unchanged.
    'basic_program': {
        'results': store_path('basic_program'),
        'out': os.path.join(ROOT, 'pipelines', 'basic_program',
                            'regression_portfolio.json'),
        'features': basic_program_features,
        'witnesses': set(),
        'pin_dims': BASIC_PIN_DIMS,
        'sid_key': 'path',
        'emit': lambda sid: {'sid': sid, 'dur': round(_bp_dur(sid), 1)},
    },
    'fc_standard': {
        'results': store_path('fc_standard'),
        'out': os.path.join(ROOT, 'pipelines', 'future_composer',
                            'regression_portfolio.json'),
        'features': member_features,
        'witnesses': FC_WITNESSES,
        'sid_key': 'sid',
    },
    'dmc_v4': {
        # family 1, #85 member set (5,445), fully re-verified 2026-08-22 at
        # the current code hash. NOT `dmc_wide_results.jsonl` — that is the
        # PRE-#85 working file (5,401 rows, missing 47 members) and pointing
        # a derivation at it silently derives from a stale member set.
        'results': store_path('dmc_v4'),
        'out': os.path.join(ROOT, 'pipelines', 'dmc', 'regression_portfolio.json'),
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
        'results': store_path('dmc_v4_family2'),
        'out': os.path.join(ROOT, 'pipelines', 'dmc',
                            'f2_regression_portfolio.json'),
        'features': dmc_features,
        'witnesses': DMC_F2_WITNESSES,
        'sid_key': 'path',
    },
    'music_assembler': {
        'results': store_path('music_assembler'),
        'out': os.path.join(ROOT, 'pipelines', 'music_assembler',
                            'regression_portfolio.json'),
        'features': masm_features,
        # ⚠ these were declared as `witnesses`, but witnesses are MEMBER PATHS
        # and these are DIMENSION names — so the tie-break had been inert since
        # the family was wired. They are semantically pin_dims; moved there,
        # where budget mode enforces them as double-cover constraints.
        'witnesses': set(),
        'pin_dims': MASM_PIN_DIMS,
        'sid_key': 'sid',
    },
    # DMC V5 — derived BEFORE the grind rather than at closeout (item 17(e));
    # v4's was derived at closeout, so the whole v4 grind ran guarded by ad-hoc
    # canaries. Built in BUDGET mode, see `budget_cover`.
    'dmc_v5': {
        # ⚠ THE POST-FIX BATCH, not `dmc_v5_85_results.jsonl` — that is the
        # PRE-#85-list baseline (1,495 rows, stale code hash). Deriving from it
        # silently produced a 1,120-member FULL pool containing ZERO family-4
        # members, so `knob:family4` never became a dimension and the portfolio
        # could not cover the branch the whole v5 grind is about. Same trap the
        # dmc_v4 entry above warns of; caught by checking the derived
        # dimensions against a member known to be FULL and family-4.
        'results': store_path('dmc_v5'),
        'out': os.path.join(ROOT, 'pipelines', 'dmc', 'v5',
                            'regression_portfolio.json'),
        'features': dmc_v5_features,
        'witnesses': DMC_V5_WITNESSES,
        'pin_dims': DMC_V5_PIN_DIMS,
        'sid_key': 'path',
    },
    # DIGI-ORGANIZER, derived at its standalone closeout (39/39). The
    # family is small but its dimensions are unusually SHARP: it is the
    # only Mode-2 cycle-strict family, so a covered dimension is covered
    # to the cycle, and 14 of its ~29 dimensions are driver classes with
    # ONE carrier each — an exact multicover therefore lands close to
    # the whole family, which is the honest answer for 39 members whose
    # every class is its own hand-written cycle skeleton.
    'digi_organizer': {
        'results': store_path('digi_organizer'),
        'out': os.path.join(ROOT, 'pipelines', 'digi_organizer',
                            'regression_portfolio.json'),
        'features': digi_organizer_features,
        'witnesses': set(),
        'sid_key': 'path',
    },
}


def budget_cover(universe: dict[str, int],
                 members: dict[str, set],
                 pinned: set[str],
                 budget: int,
                 n_random: int,
                 seed: int,
                 pin_dims: set[str] = frozenset()) -> tuple[list[str], dict]:
    """Best subset of size <= `budget`, instead of the exact minimum.

    WHY NOT EXACT MINIMUM (measured, not preference — item 17 DEFECT 2):

      * Zhang et al. put Greedy/HGS/GRE/ILP fault-detection loss at
        5.23/5.21/5.33/5.11 — statistically indistinguishable. The CRITERION
        dominates; the algorithm does not. So spending search effort on
        minimality buys nothing.
      * Every study finds detection tracks suite SIZE. Minimality is therefore
        a cost we pay voluntarily while sitting on wall-clock headroom (tier 1
        ~20 min vs tier 2's hours).
      * Our reduction ratio was 98.8% (64 of 5,401). Every study that found
        minimization survivable did so at 12-70% — one to two orders of
        magnitude inside the validated envelope from where we sat.

    Monotonically better than the exact form: the exact solution stays
    feasible, and unused budget converts into fault detection instead of
    being discarded.

    Three strata, in priority order:
      1. PINNED bug witnesses — HARD constraints, not tie-breaks. Historical
         detection was the ONLY predictor that worked in Shi et al.'s 1,478
         real failed builds (size reduction R^2=0.00; coverage loss also
         non-predictive).
      2. GREEDY MULTICOVER to satisfy the universe, then deepen it (each pass
         raises required coverage by one) while budget remains.
      3. A ROTATING RANDOM STRATUM. Random found 92% of 135 real config faults
         vs one-enabled's 79% (Medeiros et al. ICSE'16), and it is the only
         mitigation for the blind spot that our traits are extracted BY THE
         CODE UNDER TEST: if the extractor mis-detects a trait, a
         feature-derived portfolio is blind to that member class by
         construction. Bump `seed` per derivation to rotate it.
    """
    rnd = random.Random(seed)
    chosen: list[str] = sorted(m for m in pinned if m in members)
    covered: dict[str, int] = {}
    for m in chosen:
        for d in members[m]:
            covered[d] = covered.get(d, 0) + 1
    carriers = {d: sum(1 for fs in members.values() if d in fs)
                for d in universe}

    n_rand_slots = min(n_random, max(0, budget - len(chosen)))
    cover_budget = budget - n_rand_slots

    def marginal(m: str, need: dict[str, int]) -> int:
        return sum(1 for d in members[m] if need.get(d, 0) > 0)

    # Required coverage per dimension at a given deepening pass. Pass 1 is the
    # universe itself (1, or 2 where >=2 members carry the dimension); each
    # further pass asks for one more, capped by how many members actually have
    # it — so a dimension with a single carrier never blocks the loop.
    def required(d: str, dep: int) -> int:
        return min(universe[d] + (dep - 1) + (1 if d in pin_dims else 0),
                   carriers[d])

    depth = 1
    while len(chosen) < cover_budget and depth <= 4:
        need = {d: required(d, depth) - covered.get(d, 0) for d in universe}
        need = {d: v for d, v in need.items() if v > 0}
        avail = [m for m in members if m not in chosen]
        if not need or not avail:
            depth += 1
            continue
        best = max(avail, key=lambda m: (marginal(m, need), -len(members[m]), m))
        if marginal(best, need) == 0:
            depth += 1
            continue
        chosen.append(best)
        for d in members[best]:
            covered[d] = covered.get(d, 0) + 1

    # Rotating random stratum, drawn from members the cover pass did not pick.
    # If the cover pass stopped early (deepening capped, or the universe ran
    # out of uncovered dimensions), the leftover budget goes here rather than
    # being discarded — spending it on random members is the whole point of a
    # budget, and random sampling found 92% of 135 real config faults against
    # one-enabled's 79% (Medeiros et al. ICSE'16).
    slots = n_rand_slots + max(0, cover_budget - len(chosen))
    rest = sorted(set(members) - set(chosen))
    rand_pick = rnd.sample(rest, min(slots, len(rest))) if rest else []
    chosen += rand_pick

    unmet = sorted(d for d, r in universe.items() if covered.get(d, 0) < r)
    stats = {
        'pinned': sorted(m for m in pinned if m in members),
        'random_stratum': sorted(rand_pick),
        'random_seed': seed,
        'budget': budget,
        'max_depth_reached': depth,
        'uncovered_dimensions': unmet,
    }
    return sorted(set(chosen)), stats


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
    ap.add_argument('--budget', type=int, default=0,
                    help='BUDGET mode (item 17e): best subset of this size '
                         'instead of the exact minimum. 0 = exact (legacy).')
    ap.add_argument('--random', type=int, default=12,
                    help='budget mode: size of the rotating random stratum')
    ap.add_argument('--seed', type=int, default=20260822,
                    help='budget mode: bump to rotate the random stratum')
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
    # basic_program records 'FULL', the others 'full' — compare case-blind
    # or that family silently derives from an EMPTY candidate pool.
    fulls = [p for p, r in _latest.items()
             if str(r.get('status', '')).lower() == 'full']
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
    stats = {}
    if args.budget:
        sol, stats = budget_cover(universe, members, witnesses, args.budget,
                                  args.random, args.seed,
                                  eng.get('pin_dims', frozenset()))
    else:
        sol = exact_multicover(universe, members, witnesses)
    sol.sort()
    cover = {d: sorted(m for m in sol if d in members[m])
             for d in sorted(universe)}
    emit = eng.get('emit')
    out_portfolio = [emit(m) for m in sol] if emit else sol
    json.dump({'engine': args.engine, 'portfolio': out_portfolio,
               'dimensions': cover,
               'corpus_full': len(members),
               'mode': 'budget' if args.budget else 'exact', **stats},
              open(out, 'w'), indent=1)
    kind = (f'BUDGET portfolio (<= {args.budget})' if args.budget
            else 'EXACT minimum portfolio')
    print(f'{kind}: {len(sol)} members -> {out}')
    if stats:
        print(f'  pinned witnesses : {len(stats["pinned"])}')
        print(f'  random stratum   : {len(stats["random_stratum"])} '
              f'(seed {stats["random_seed"]})')
        print(f'  deepening reached: {stats["max_depth_reached"]}x')
        if stats['uncovered_dimensions']:
            print(f'  ⚠ UNCOVERED      : {stats["uncovered_dimensions"]}')
    for m in sol:
        tag = '  [witness]' if m in witnesses else ''
        print(f'  {m}{tag}')
    for d in sorted(universe):
        print(f'  {dim_count[d]:5d}x {d}: '
              f'{", ".join(p.split("/")[-1] for p in cover[d])}')


if __name__ == '__main__':
    main()
