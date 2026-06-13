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


def _row_to_usf(r: DmcRow) -> NoteRow:
    flags = []
    if r.vol:
        flags.append(f'vol={r.vol}')
    if r.gate_toggle:
        flags.append('gate_toggle')
    if r.soft or r.glide_slide:
        flags.append('noretrig')
    if r.glide_speed:
        flags.append(f'glide={r.glide_speed}')
    if r.glide_to is not None:
        flags.append(f'glide_to={_pitch(r.glide_to)}')
    if r.note is None:
        return NoteRow(pitch=Pitch.rest(), duration=r.duration,
                       fx_flags=tuple(flags))
    return NoteRow(pitch=_pitch(r.note), duration=r.duration,
                   instr=InstrumentRef(id=r.instr + 1),
                   fx_flags=tuple(flags))


def _instrument_to_usf(inst) -> Instrument:
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
        pwm=PwmConfig(mode='bidirectional',
                      init=inst.pw_init_hi << 8,
                      min_hi=inst.pw_bound_a, max_hi=inst.pw_bound_b,
                      speed_steps=list(inst.pw_steps),
                      keep_running=inst.pw_keep_running),
        arp=ArpConfig(offsets=[]),
        vibrato=vib,
        envelope=EnvelopeConfig(gate_mode=inst.gate_mode),
        freq_slide_config=slide,
        filter_prog=FilterProgConfig(
            program=(inst.filter_def + 1) if inst.filter_on else 0,
            keep_running=inst.filter_keep_running),
        effects=frozenset(effects),
    )


def model_to_usf(m: DmcModel) -> UsfFile:
    subtunes = []
    for song in m.songs:
        voices = []
        for vi, v in enumerate(song.voices):
            pats = [Pattern(id=i,
                            length=sum(r.duration for r in rows),
                            rows=[_row_to_usf(r) for r in rows])
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

    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      start_song=m.start_song),
        # slide_phase: initial phase bit of the global half-rate slide
        # clock (work-file leftover; shifts WHICH frames dual-effect
        # voices update on — audible interleave phase). cia_period: the
        # multispeed CIA1 timer A latch (0 = single-speed VBI).
        params=Params(fields={
            **({'slide_phase': m.dual_phase} if m.dual_phase else {}),
            **({'cia_period': m.cia_period} if m.cia_period else {}),
            **({'cymbal_onset': 1} if m.family2 else {})}),
        init=InitState(voices=[
            InitVoice(id=v + 1,
                      note=m.idle_notes[v] or None,
                      gate_mask=m.idle_masks[v] or None)
            for v in range(3) if m.idle_notes[v] or m.idle_masks[v]]),
        instruments=[_instrument_to_usf(m.instruments[k])
                     for k in sorted(m.instruments)],
        subtunes=subtunes,
        filter_programs={d + 1: dict(v) for d, v in m.filter_defs.items()},
        # tuning is per-tune musical content (members ship edited or
        # wholly different temperaments): 96 lo + 96 hi bytes.
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        # the idle wave program: what a voice's effects walk before its
        # first note (the engine's cleared cache starts the wave table
        # at index 0, independent of any instrument's start)
        wave_programs={0: {'ctrl': list(m.idle_wave[0]),
                           'freq': list(m.idle_wave[1]),
                           'loop': m.idle_wave[2]}},
        # family-2's per-note vibrato step (freq-hi >> 1); empty for canon
        vib_depth_curve=list(m.vib_depth_curve),
    )


def write_dmc_usf(cfg: DMCV4Config, out_dir: str,
                  hvsc_root: str = 'hvsc84') -> str:
    m = extract(cfg, hvsc_root=hvsc_root)
    usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(cfg.sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
