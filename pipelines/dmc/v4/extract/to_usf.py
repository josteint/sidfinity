"""DMC V4 model → USF.

Maps the path-resolved DmcModel onto the engine-neutral USF schema:

- sectors → per-voice patterns (NoteRow: pitch/duration/instr +
  `vol=N` / `noretrig` / `gate_toggle` / `glide=N` / `glide_to=P` flags)
- tracks → orderlists with signed per-entry transposes + loop/stop
- instruments → adsr / pwm (bidirectional + speed_steps) / vibrato
  (onset + amplitude + ramp) / envelope.gate_mode / slide ('run',
  half_rate) / filter_prog / waveform + wave_freq + loop / effects
- filter definitions → the duration-based filter_programs shape
- per-subtune speed → tempo; master vol + the $D417 routing-shadow
  leftover → per-subtune init.sid priming (trichotomy: priming, not
  reset — the play loop's $D417 writes read this state)

The freq table IS carried (per-tune tuning content — members ship
edited or wholly different temperaments). The per-note vibrato-depth
curve stays a fixed engine constant (mechanism, identical family-wide).
"""
from __future__ import annotations

import os

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter, InitVoice,
    Instrument, PwmConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, FilterProgConfig, ArpConfig,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
    InstrumentRef,
)
from src.usf.writer import write_file
from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.v4.extract.engine_model import (
    extract, DmcModel, DmcRow, NOTE_NAMES,
)


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


# Sector-position window idx (per-voice $1729-$172B), for the row-command gate.
_SECTPOS_IDX = {(0x1729 + k) - 0x16A7 for k in range(3)} \
    | {(0x1729 + k) - 0x1647 for k in range(3)}


def _offtable_live_idx() -> set:
    """The window indices a canon-geometry off-table read is served LIVE from —
    the single source of truth lives in the composer (offtable_live_idx), shared
    so extract's per-read `live` stamp and the composer's redirect derivation
    can't disagree on geometry."""
    from pipelines.dmc.composer_asm import offtable_live_idx
    return offtable_live_idx()


def _stamp_live(recs, canon: bool) -> list:
    """Tag each off-table read `(off, note, lo, hi)` with a 5th element `live`
    (1 iff the read sonifies a live-varying value: canon geometry AND the read
    idx hits a live-served window slot). Static reads stay 4-tuples so they
    serialize as `at(...)` and non-off-table engines are byte-identical."""
    live_idx = _offtable_live_idx()
    out = []
    for rec in recs:
        off, note, lo, hi = rec[:4]
        idx = (off + note) & 0xFF
        if canon and idx in live_idx:
            out.append((off, note, lo, hi, 1))
        else:
            out.append((off, note, lo, hi))
    return out


def _row_to_usf(r: DmcRow, cmd_flags: bool = False) -> NoteRow:
    flags = []
    if r.vol:
        flags.append(f'vol={r.vol}')
    if cmd_flags:
        # stated-command placement (arrangement, §8): emitted only for members
        # whose off-table freq reads sonify the sector-position counter
        # ($1729-$172B) — the composer derives each row's orig byte width
        # (base + stated commands) to keep a live sectpos,x shadow.
        if r.dcmd:
            flags.append('dur_cmd')
        if r.icmd:
            flags.append('instr_cmd')
        if r.vcmd:
            flags.append('vol_cmd')
        if r.softcmd:
            flags.append(f'soft_cmd={r.softcmd}')
    if r.gate_toggle:
        flags.append('gate_toggle')
    if r.soft or r.glide_slide:
        flags.append('noretrig')
    if r.glide_speed or r.glide_slide or r.glide_to is not None:
        # glide/slide rows ALWAYS carry glide=N, including speed 0 (ledger
        # C22 — the encoding must be injective over engine ops). Mode 1: a
        # $Dx slide with a zero speed nibble is the engine's "set target,
        # no note load, hold" — suppressing glide=0 rendered it identically
        # to a plain soft note and the composer LOADED the note early
        # (Apocalypsa: octave drop 10 frames before the orig). Mode 0: a
        # $Cx glide with a zero speed nibble is the engine's GLIDE-CANCEL
        # ($1136 stores 0 to glsp) — suppressing it rendered a plain note,
        # so a previous row's armed glide kept ramping the freq accumulator
        # in the rebuild (Grave_Story_intro +$10/frame; the ×16-quantized
        # deep freq drift class, family-1 round 19).
        flags.append(f'glide={r.glide_speed}')
    if r.glide_to is not None:
        flags.append(f'glide_to={_pitch(r.glide_to)}')
    if r.note is None:
        return NoteRow(pitch=Pitch.rest(), duration=r.duration,
                       fx_flags=tuple(flags))
    return NoteRow(pitch=_pitch(r.note), duration=r.duration,
                   instr=InstrumentRef(id=r.instr + 1),
                   fx_flags=tuple(flags))


def _instrument_to_usf(inst, wavepos_layout: bool = False,
                       canon: bool = True) -> Instrument:
    effects = set()
    if inst.drum:
        effects.add('drum')
    if inst.noise_attack:
        effects.add('noise_attack')
    wave_freq = inst.wave_freq
    if not inst.drum:
        # melodic: per-step semitone offsets, signed
        wave_freq = [b - 256 if b >= 128 else b for b in wave_freq]
    slide = FreqSlideConfig()
    vib = VibratoConfig(onset=inst.vib_delay, amplitude=inst.vib_width,
                        ramp=0 if inst.dual else inst.vib_ramp)
    if inst.dual:
        slide = FreqSlideConfig(mode='run', step=inst.slide_step,
                                initial_dir=inst.slide_dir, half_rate=True)
    return Instrument(
        id=inst.id + 1,
        waveform=list(inst.wave_ctrl),
        loop=inst.wave_loop,
        wave_freq=wave_freq,
        adsr=(inst.ad, inst.sr),
        offtable_freq=_stamp_live(inst.offtable_freq, canon),
        # editor wave-table position (arrangement) — only for members whose
        # off-table reads sonify a live wave position (see DmcModel)
        wave_table_pos=inst.wave_pool_pos if wavepos_layout else None,
        # editor "start at the loop marker" idiom — the first-read chase writes
        # $171F=n; carried only when an off-table read sonifies that scratch
        wave_start_on_marker=inst.wave_start_on_marker,
        pwm=PwmConfig(mode='bidirectional',
                      init=inst.pw_init_hi << 8,
                      min_hi=inst.pw_bound_a, max_hi=inst.pw_bound_b,
                      speed_steps=list(inst.pw_steps),
                      keep_running=inst.pw_keep_running),
        arp=ArpConfig(offsets=[]),
        vibrato=vib,
        envelope=EnvelopeConfig(gate_mode=inst.gate_mode,
                                gate_open=inst.gate_open),
        freq_slide_config=slide,
        filter_prog=FilterProgConfig(
            program=(inst.filter_def + 1) if inst.filter_on else 0,
            keep_running=inst.filter_keep_running),
        effects=frozenset(effects),
    )


def _otrk_model(v):
    """The otrk phase scalars (pad, period): the engine's track counter
    ($1726,x) counts BYTES of the orig encoding, where a transpose command
    byte is editor-placed — usually on change, but sometimes redundantly
    (measured: a leading constant, {+1: 146} of 540 tracks). The composer
    derives per-entry offsets as transpose-CHANGE count + PAD (the
    dual_phase-style phase scalar), resetting every PERIOD entries — the
    physical track length the loop-unrolling walk obscured (offsets are
    periodic because each pass re-reads the same bytes). Returns (pad,
    period) only when the model reproduces the walked ground-truth offsets
    EXACTLY; None = keep the plain derivation (piecewise mid-track
    redundancy — the documented residue tail)."""
    n = len(v.entries)
    if not v.entry_offsets or len(v.entry_offsets) != n:
        return None
    # physical period = first offset reset (loop-unrolled walks); else n
    period = n
    for i in range(1, n):
        if v.entry_offsets[i] <= v.entry_offsets[i - 1]:
            period = i
            break
    pad = v.entry_offsets[0]      # leading redundant-command count
    # cur = the transpose the LEADING command already set (pad accounts for its
    # byte); starting at 0 double-counts a leading transpose command when the
    # first entry is transposed (So_easy V1: entry 0 transpose 1 -> the model
    # re-added the byte pad already covers -> spurious legacy fallback).
    cur0 = v.transposes[0] if v.transposes else 0
    off, cur = pad, cur0
    for i in range(n):
        if i and i % period == 0:
            off, cur = pad, cur0  # pass boundary: orig re-reads from start
        t = v.transposes[i] if v.transposes else 0
        if t != cur:
            off, cur = off + 1, t
        if v.entry_offsets[i] != off:
            return None
        off += 1
    return pad, period


def _otrk_rcmd_model(v):
    """When the plain (pad, period) model is off ONLY because the composer
    placed extra REDUNDANT transpose commands mid-track — a `transpose to X`
    where X is already the current value, an explicit reset the composer WROTE
    (their arrangement), which the on-change model doesn't predict — recover
    the exact offsets by carrying those command POSITIONS. Returns
    (pad, period, rcmd) where rcmd is a bitmask of the redundant-command
    positions WITHIN the period (bit p = a redundant transpose command
    precedes physical entry p). This is the composer's ARRANGEMENT (where they
    notated transpose commands) — named musical content per the representation
    principle §8 (the composer needs it to reproduce the off-table sonification
    of $1726); the byte-OFFSET is DERIVED from it, never stored. None = even
    this can't model it (a non-unit jump / decrease = genuine legacy residue)."""
    n = len(v.entries)
    if not v.entry_offsets or len(v.entry_offsets) != n:
        return None
    period = n
    for i in range(1, n):
        if v.entry_offsets[i] <= v.entry_offsets[i - 1]:
            period = i
            break
    pad = v.entry_offsets[0]
    cur0 = v.transposes[0] if v.transposes else 0
    rcmd = 0
    off, cur, red = pad, cur0, 0
    for i in range(n):
        p = i % period
        if p == 0:
            off, cur, red = pad, cur0, 0
        t = v.transposes[i] if v.transposes else 0
        if t != cur:
            off, cur = off + 1, t
        actual = v.entry_offsets[i]
        expected = off + red
        if actual == expected + 1:
            red += 1
            rcmd |= (1 << p)
        elif actual != expected:
            return None
        off += 1
    return pad, period, rcmd if rcmd else None


def _emit_otrk_fields(m) -> dict:
    fields = {}
    for song in m.songs:
        for vi, v in enumerate(song.voices):
            r = _otrk_model(v)
            if r is not None:
                pad, period = r
                if pad:
                    fields[f'otrk_pad_s{song.id}_v{vi + 1}'] = pad
                if period < len(v.entries):
                    fields[f'otrk_period_s{song.id}_v{vi + 1}'] = period
                continue
            # the composer's redundant transpose-command PLACEMENT (arrangement)
            r2 = _otrk_rcmd_model(v)
            if r2 is not None and r2[2] is not None:
                pad, period, rcmd = r2
                if pad:
                    fields[f'otrk_pad_s{song.id}_v{vi + 1}'] = pad
                if period < len(v.entries):
                    fields[f'otrk_period_s{song.id}_v{vi + 1}'] = period
                fields[f'otrk_rcmd_s{song.id}_v{vi + 1}'] = rcmd
                continue
            # non-unit jump / decrease: genuine residue -> entry+1 approximation
            fields[f'otrk_legacy_s{song.id}_v{vi + 1}'] = 1
    return fields


def model_to_usf(m: DmcModel) -> UsfFile:
    pad_fields = _emit_otrk_fields(m)
    # row command flags (dur_cmd/instr_cmd/vol_cmd/soft_cmd) feed the composer's sectpos
    # shadow — emit them iff a canon-geometry off-table read sonifies the sector
    # position window (matches the composer's derived sectpos_on).
    cmd_flags = m.offtable_canon and any(
        (off + note) & 0xFF in _SECTPOS_IDX
        for ins in m.instruments.values()
        for off, note, *_ in ins.offtable_freq)
    subtunes = []
    for song in m.songs:
        voices = []
        for vi, v in enumerate(song.voices):
            pats = [Pattern(id=i,
                            length=sum(r.duration for r in rows),
                            rows=[_row_to_usf(r, cmd_flags) for r in rows])
                    for i, rows in enumerate(v.patterns)]
            ol = Orderlist(entries=list(v.entries),
                           transposes=(list(v.transposes)
                                       if any(v.transposes) else []),
                           loop_to=v.loop_to, stop=v.stop)
            voices.append(VoiceBlock(id=vi + 1, orderlist=ol, patterns=pats))
        sub_init = InitState(sid=InitSid(
            master_vol=song.master_vol,
            filter=InitFilter(res_routing=m.d417_shadow)
            if m.d417_shadow else None))
        subtunes.append(MusicSubtune(id=song.id, tempo=song.speed,
                                     voices=voices, init=sub_init))

    # duration-reload leftover priming ($173E-$1740): emitted ONLY when an
    # off-table freq read actually lands on the durreload rows (flo idx
    # 247-249 / fhi idx 151-153) — the composer's live `durrel` shadow then
    # needs the pre-first-event value for voices that haven't fetched yet
    # (stopped/never-inited voices keep it forever). Members that never read
    # the window carry no leftover (ML-cleanliness) and their USF is
    # unchanged.
    _DURREL_WIN = {151, 152, 153, 247, 248, 249}
    reads_durrel = any(((off + note) & 0xFF) in _DURREL_WIN
                       for inst in m.instruments.values()
                       for off, note, _lo, _hi in
                       (getattr(inst, 'offtable_freq', []) or []))
    durrel = (m.durrel_init if reads_durrel and any(m.durrel_init)
              else (0, 0, 0))

    # filter_mod: the factory probe encodes the song-global cutoff LFO as
    # 'prog|start|init_phase|stop_phase|d:f,...' — decode into the typed
    # block (musical content, not a params knob).
    filter_mod = {}
    fm = m.extra_params.pop('filter_mod', None)
    if fm:
        prog, start, ip, sp, steps = fm.split('|')
        filter_mod[int(prog)] = {
            'start': int(start), 'init_phase': int(ip),
            'stop_phase': int(sp),
            'steps': [(int(d), int(f)) for d, f in
                      (t.split(':') for t in steps.split(','))]}
    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      clock=m.clock, sid=m.sid_model,
                      start_song=m.start_song),
        # slide_phase: initial phase bit of the global half-rate slide
        # clock (work-file leftover; shifts WHICH frames dual-effect
        # voices update on — audible interleave phase). cia_period: the
        # multispeed CIA1 timer A latch (0 = single-speed VBI).
        params=Params(fields={
            **({'slide_phase': m.dual_phase} if m.dual_phase else {}),
            **({'cia_period': m.cia_period} if m.cia_period else {}),
            # internal-multispeed play-repeat count (>1 = play() loops Nx/VBI)
            **({'play_repeat': m.play_repeat} if m.play_repeat > 1 else {}),
            # otrk phase-offset scalars (see _otrk_pad)
            **pad_fields,
            # family-2 build knobs (factory-probed; empty for canon)
            **m.extra_params}),
        # NB idle_guards deliberately NOT emitted yet — the composer's guard
        # freewheel schedule for stopped voices is unverified vs the orig
        # (see composer_asm DMC_OFFTABLE_STATE note); priming would change
        # gate-logic behaviour for every member with $1786-8 leftovers.
        init=InitState(voices=[
            InitVoice(id=v + 1,
                      note=m.idle_notes[v] or None,
                      gate_mask=m.idle_masks[v] or None,
                      dur_reload=durrel[v] or None)
            for v in range(3)
            if m.idle_notes[v] or m.idle_masks[v] or durrel[v]]),
        instruments=[_instrument_to_usf(m.instruments[k], m.wavepos_layout,
                                        m.offtable_canon)
                     for k in sorted(m.instruments)],
        subtunes=subtunes,
        filter_programs={d + 1: dict(v) for d, v in m.filter_defs.items()},
        filter_mod=filter_mod,
        # tuning is per-tune musical content (members ship edited or
        # wholly different temperaments): 96 lo + 96 hi bytes.
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        # the idle wave program: what a voice's effects walk before its
        # first note (the engine's cleared cache starts the wave table
        # at index 0, independent of any instrument's start)
        wave_programs={0: {'ctrl': list(m.idle_wave[0]),
                           'freq': list(m.idle_wave[1]),
                           'loop': m.idle_wave[2]}},
        # off-table vibrato-depth reads (note>95) — the vibdepth analog of
        # offtable_freq; composer places these past the vibdepth table.
        offtable_vibdepth=sorted(m.offtable_vibdepth.items()),
    )


def write_dmc_usf(cfg: DMCV4Config, out_dir: str,
                  hvsc_root: str = 'hvsc84') -> str:
    m = extract(cfg, hvsc_root=hvsc_root)
    usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(cfg.sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out


def _offset_note_refs(rows, di: int):
    """Return rows with every instrument reference (note.instr + a
    `set_instr=N` fx flag) shifted by `di` — used to move a chip's
    instruments into a disjoint id range in the merged multi-SID USF."""
    import dataclasses
    out = []
    for r in rows:
        instr = r.instr
        if instr is not None and getattr(instr, 'id', None) is not None:
            instr = dataclasses.replace(instr, id=instr.id + di)
        flags = []
        for f in r.fx_flags:
            if f.startswith('set_instr='):
                flags.append(f'set_instr={int(f.split("=")[1]) + di}')
            else:
                flags.append(f)
        out.append(dataclasses.replace(r, instr=instr, fx_flags=flags))
    return out


# Per-chip id strides in the MERGED multi-SID USF: chip c's instruments +
# filter programs are shifted by c*STRIDE so a fixed-arithmetic split
# recovers each chip's standalone sub-USF exactly (ids well above any real
# DMC per-player count — instruments and 17-record filter windows). Only
# appear in multi-SID files; single-chip USFs are unchanged.
MULTISID_INSTR_STRIDE = 100
MULTISID_FILTER_STRIDE = 100


def merge_2sid_usf(models, sid2_model=None, sid3_model=None) -> UsfFile:
    """Merge per-chip DmcModels (one per SID chip) into ONE multi-SID USF:
    voices number through the chips (1-3 = chip 1, 4-6 = chip 2, ...), each
    chip's instruments + filter programs live in a disjoint id range (chip
    c shifted by c*STRIDE), and per-chip priming rides init.sid /
    init.sid2 / init.sid3. freq_table + idle wave are shared (verified
    identical across a member's chips). Chip I/O addresses are NOT carried —
    the composer standardises them (chip 2 = $D420, chip 3 = $D440).
    Single-subtune members only (the 2SID corpus)."""
    import dataclasses
    usfs = [model_to_usf(m) for m in models]
    assert all(len(u.subtunes) == 1 for u in usfs), \
        'multi-SID merge supports single-subtune members only'
    # shared musical content must coincide across chips (they're one tune)
    assert all(u.freq_table == usfs[0].freq_table for u in usfs), \
        'multi-SID chips disagree on the freq table'

    merged_instruments = []
    merged_filters = {}
    all_voices = []
    init_voices = []
    chip_sids = []          # per-chip InitSid priming
    tempos = []
    for ci, u in enumerate(usfs):
        ioff = ci * MULTISID_INSTR_STRIDE
        foff = ci * MULTISID_FILTER_STRIDE
        sub = u.subtunes[0]
        tempos.append(sub.tempo)
        for inst in u.instruments:
            fp = inst.filter_prog
            if fp and fp.program:
                fp = dataclasses.replace(fp, program=fp.program + foff)
            merged_instruments.append(
                dataclasses.replace(inst, id=inst.id + ioff, filter_prog=fp))
        for prog, dfn in u.filter_programs.items():
            merged_filters[prog + foff] = dfn
        # voices renumbered through the chips; note refs shifted
        for v in sub.voices:
            pats = [dataclasses.replace(p, rows=_offset_note_refs(p.rows, ioff))
                    for p in v.patterns]
            all_voices.append(dataclasses.replace(
                v, id=ci * 3 + v.id, patterns=pats))
        # per-voice idle priming (top-level init.voices), voices renumbered
        for iv in u.init.voices:
            init_voices.append(dataclasses.replace(iv, id=ci * 3 + iv.id))
        # per-chip SID priming (master vol + $D417 routing shadow) rides the
        # subtune init.sid in the per-chip USF
        chip_sids.append(sub.init.sid if sub.init else None)

    base = usfs[0]
    init = InitState(
        voices=init_voices,
        sid=chip_sids[0],
        sid2=chip_sids[1] if len(chip_sids) > 1 else None,
        sid3=chip_sids[2] if len(chip_sids) > 2 else None)
    subtune = MusicSubtune(
        id=1, tempo=tempos[0], voices=all_voices, init=init,
        tempo2=tempos[1] if len(tempos) > 1 and tempos[1] != tempos[0]
        else None,
        tempo3=tempos[2] if len(tempos) > 2 and tempos[2] != tempos[0]
        else None)
    psid = dataclasses.replace(base.psid, sid2=sid2_model, sid3=sid3_model)
    return dataclasses.replace(
        base, psid=psid, init=init,
        instruments=merged_instruments,
        filter_programs=merged_filters,
        subtunes=[subtune])


def write_dmc_2sid_usf(cfgs, out_dir: str, hvsc_root: str = 'hvsc84') -> str:
    from pipelines.dmc.v4.factory import _sid_header_multi
    models = [extract(c, hvsc_root=hvsc_root) for c in cfgs]
    _, _, _, m2, m3 = _sid_header_multi(
        os.path.join(hvsc_root, cfgs[0].sid_path))
    usf = merge_2sid_usf(models, sid2_model=m2, sid3_model=m3)
    base = os.path.splitext(os.path.basename(cfgs[0].sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out


def write_dmc_compilation_usf(sid_path: str, spec: dict, out_dir: str,
                              hvsc_root: str = 'hvsc84') -> str:
    """COMPILATION member (ledger C31): extract every packed player, merge into
    one unified single-player DmcModel (freq/vibdepth shared, instruments
    renumbered into one pool, songs reordered by PSID subtune), then serialize
    with the ordinary model_to_usf path — the composer needs no compilation
    awareness."""
    from pipelines.dmc.v4.compilation import extract_compilation
    m = extract_compilation(sid_path, spec, hvsc_root=hvsc_root)
    usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
