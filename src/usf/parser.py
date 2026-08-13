"""USF — parser.

Lark-based parser that produces typed AST classes from src.usf.types.
Grammar lives in src/usf/grammar.lark.
"""

from __future__ import annotations

import os

from lark import Lark, Transformer, Token, v_args
from lark.exceptions import LarkError

from src.usf.types import (
    Environment,
    UsfFile, PsidMeta, Params, InitVoice, InitState,
    InitSid, InitSidVoice, InitFilter,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, IncBy2Config, SongEndConfig, InitBehaviorConfig,
    MasterVolConfig, SfxConfig, SweepEnvelope,
    MusicSubtune, DigiSubtune, SfxSubtune, DmcSfxSubtune,
    SfxEngine, SfxInstrument, SfxSong, SfxVoiceInit,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    GlobalEvent, LiveSignal,
)


_GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), 'grammar.lark')


class UsfParseError(Exception):
    """Parse error with line/column information."""
    pass


def _load_parser() -> Lark:
    # propagate_positions=False: it attaches line/column metadata to every tree
    # node, which costs ~30% of parse time, and nothing here reads it — the
    # transformer below never touches `.meta`/`.line`/`.column`, and parse
    # ERRORS carry their own position from the LarkError exception, so
    # UsfParseError messages are unaffected. Parsing is on every build path
    # (the composer re-reads the .usf it just wrote), so this is broad.
    with open(_GRAMMAR_PATH) as f:
        return Lark(f.read(), start='start', parser='lalr',
                    propagate_positions=False)


_PARSER = None


def _parser() -> Lark:
    global _PARSER
    if _PARSER is None:
        _PARSER = _load_parser()
    return _PARSER


# ---------------------------------------------------------------------------
# Transformer: Tree → typed AST
# ---------------------------------------------------------------------------

class _T(Transformer):
    # ----- numbers / literals -----
    def dec_number(self, items):
        return int(items[0])

    def hex_number(self, items):
        # token value starts with '$'
        return int(str(items[0])[1:], 16)

    def number(self, items):
        return items[0]

    def neg_number(self, items):
        return -items[0]

    def signed_int(self, items):
        return items[0]

    def byte(self, items):
        return items[0]

    def byte_list(self, items):
        return list(items)

    def bool_true(self, _):
        return True

    def bool_false(self, _):
        return False

    # ----- psid -----
    @staticmethod
    def _unquote(tok) -> str:
        # ESCAPED_STRING: strip the quotes, undo \" and \\ (single pass —
        # the writer's _quote escapes embedded quotes/backslashes).
        import re
        return re.sub(r'\\(.)', r'\1', str(tok)[1:-1])

    def psid_title(self, items):
        return ('title', self._unquote(items[0]))

    def psid_author(self, items):
        return ('author', self._unquote(items[0]))

    def psid_released(self, items):
        return ('released', self._unquote(items[0]))

    def psid_clock(self, items):
        return ('clock', str(items[0]))

    def psid_sid(self, items):
        return ('sid', int(items[0]))

    def psid_sid_name(self, items):
        return ('sid', str(items[0]))          # 'both' (PSID flag 3)

    def psid_sid2(self, items):
        return ('sid2', int(items[0]))

    def psid_sid2_name(self, items):
        return ('sid2', str(items[0]))

    def psid_sid3(self, items):
        return ('sid3', int(items[0]))

    def psid_sid3_name(self, items):
        return ('sid3', str(items[0]))

    def psid_start_song(self, items):
        return ('start_song', int(items[0]))

    def psid_speed(self, items):
        return ('speed', int(items[0]))

    def psid_field(self, items):
        return items[0]

    def psid_block(self, items):
        meta = PsidMeta()
        for k, v in items:
            setattr(meta, k, v)
        return meta

    # ----- params -----
    def param_number(self, items):
        return items[0]

    def param_keyword(self, items):
        return str(items[0])

    def param_bool(self, items):
        return items[0]

    def param_string(self, items):
        return str(items[0])[1:-1]                     # strip quotes

    def param_list(self, items):
        return list(items)

    def param_elem_int(self, items):
        return int(items[0])

    def param_elem_list(self, items):
        return items[0]

    def param_list_value(self, items):
        return items[0]

    def param_value(self, items):
        return items[0]

    def params_field(self, items):
        return (str(items[0]), items[1])

    def params_block(self, items):
        return Params(fields=dict(items))

    # ----- init -----
    def init_number(self, items):
        return items[0]

    def init_keyword(self, items):
        return str(items[0])

    def init_instr(self, items):
        return items[0]

    def init_value(self, items):
        return items[0]

    def init_field(self, items):
        return (str(items[0]), items[1])

    def init_voice(self, items):
        voice_id = int(items[0])
        fields = dict(items[1:])
        v = InitVoice(id=voice_id)
        for k, val in fields.items():
            if not hasattr(v, k):
                raise UsfParseError(f'init voice {voice_id}: unknown field {k!r}')
            # Flag-valued fields serialize as 0/1 (the grammar's init_value has
            # no boolean literal); restore the declared type.
            if isinstance(getattr(v, k), bool):
                val = bool(val)
            setattr(v, k, val)
        return v

    def init_inner(self, items):
        # Either an InitVoice (engine-state priming) or InitSid
        # (SID-chip priming). Returned unchanged; init_block sorts.
        return items[0]

    def init_slide_phase(self, items):
        return ('_init_slide_phase', int(items[0]))

    def init_speed_ctr(self, items):
        return ('_init_speed_ctr', int(items[0]))

    def init_fade_frac(self, items):
        return ('_init_fade_frac', int(items[0]))

    def init_filter_arm_cutoff(self, items):
        return ('_init_filter_arm_cutoff', int(items[0]))

    def init_filter_arm_frames(self, items):
        return ('_init_filter_arm_frames', int(items[0]))

    def init_block(self, items):
        voices = [it for it in items if isinstance(it, InitVoice)]
        slide_phase = None
        speed_ctr_init = 0
        fade_frac_init = 0
        filter_arm_cutoff = 0
        filter_arm_frames = 0
        for it in items:
            if isinstance(it, tuple) and it and it[0] == '_init_slide_phase':
                slide_phase = it[1]
            elif isinstance(it, tuple) and it and it[0] == '_init_speed_ctr':
                speed_ctr_init = it[1]
            elif isinstance(it, tuple) and it and it[0] == '_init_fade_frac':
                fade_frac_init = it[1]
            elif isinstance(it, tuple) and it and it[0] == '_init_filter_arm_cutoff':
                filter_arm_cutoff = it[1]
            elif isinstance(it, tuple) and it and it[0] == '_init_filter_arm_frames':
                filter_arm_frames = it[1]
        sids = {}
        for it in items:
            if isinstance(it, tuple) and it and it[0] == '_init_sid':
                _, chip, sid = it
                if chip not in (1, 2, 3):
                    raise UsfParseError(f'init sid chip must be 2 or 3, '
                                        f'got {chip}')
                if chip in sids:
                    raise UsfParseError(
                        f'init sid block for chip {chip} appears twice')
                sids[chip] = sid
        return InitState(voices=voices, sid=sids.get(1),
                         sid2=sids.get(2), sid3=sids.get(3),
                         slide_phase=slide_phase,
                         speed_ctr_init=speed_ctr_init,
                         fade_frac_init=fade_frac_init,
                         filter_arm_cutoff=filter_arm_cutoff,
                         filter_arm_frames=filter_arm_frames)

    # ----- init.sid -----
    def ifilt_lo(self, items):  return ('cutoff_lo', items[0])
    def ifilt_hi(self, items):  return ('cutoff_hi', items[0])
    def ifilt_res(self, items): return ('res_routing', items[0])

    def top_block(self, items):
        # Pass-through for the grouped top-level optional blocks (the
        # grammar groups them into one repeated rule for LALR size; each
        # inner handler returns a ('key', value) tuple).
        return items[0]

    def env_cia_period(self, items):
        return ('cia_period', int(items[0]))

    def env_play_repeat(self, items):
        return ('play_repeat', int(items[0]))

    def environment_block(self, items):
        e = Environment()
        for k, v in items:
            setattr(e, k, v)
        return ('environment', e)

    def isid_master_vol(self, items):
        return ('master_vol', items[0])

    def isid_filter(self, items):
        f = InitFilter()
        for k, v in items:
            setattr(f, k, v)
        return ('filter', f)

    def isidv_env(self, items):
        return ('envelope_prime', (items[0], items[1]))

    def isidv_pw(self, items):
        return ('pw_init', items[0])

    def isidv_ctrl(self, items):
        return ('ctrl_init', items[0])

    def isidv_freq(self, items):
        return ('freq_init', items[0])

    def isid_voice(self, items):
        voice_id = int(items[0])
        v = InitSidVoice(id=voice_id)
        for k, val in items[1:]:
            setattr(v, k, val)
        return ('voice', v)

    def init_sid_block(self, items):
        # optional leading INT = chip index (multi-SID); bare form = chip 1
        chip = 1
        if items and not isinstance(items[0], tuple):
            chip = int(items[0])
            items = items[1:]
        sid = InitSid()
        for k, val in items:
            if k == 'voice':
                sid.voices.append(val)
            else:
                setattr(sid, k, val)
        return ('_init_sid', chip, sid)

    # ----- instruments -----
    def instrument_name(self, items):
        return str(items[0])

    def inst_waveform(self, items):
        return ('waveform', list(items[0]))

    def inst_loop(self, items):
        return ('loop', int(items[0]))

    def inst_wave_freq(self, items):
        return ('wave_freq', [int(x) for x in items])

    def inst_wave_abs(self, items):
        return ('wave_abs', [int(x) for x in items])

    def inst_wave_filter(self, items):
        return ('wave_filter', list(items[0]))

    def ofreq_signal(self, items):
        # <name>(vN) / <name>() — a named live generator (live-signal
        # modulation §3); voice absent = a global signal
        v = int(str(items[1])[1:]) if len(items) > 1 else None
        return LiveSignal(str(items[0]), v)

    def ofreq_val(self, items):
        return items[0]

    def ofreq_static(self, items):
        # at(step, note, freq_lo, freq_hi) — a slot is a fixed byte or a
        # LiveSignal reference
        return tuple(x if isinstance(x, LiveSignal) else int(x)
                     for x in items)

    def ofreq_live(self, items):
        # live(step, note, freq_lo, freq_hi) — read sonifies a live value;
        # the trailing 1 marks it so the composer serves it from live state.
        return tuple(int(x) for x in items) + (1,)

    def inst_offtable_freq(self, items):
        return ('offtable_freq', [tuple(e) for e in items])

    def inst_wave_table_pos(self, items):
        return ('wave_table_pos', int(items[0]))

    def inst_record_offset(self, items):
        return ('record_offset', int(items[0]))

    def inst_wave_start_on_marker(self, items):
        return ('wave_start_on_marker', bool(int(items[0])))

    def inst_wave_start(self, items):
        return ('wave_start', int(items[0]))

    def wt_step(self, items):
        return (int(items[0]), ('step', items[1], items[2]))

    def wt_jump(self, items):
        return (int(items[0]), ('jump', int(items[1])))

    def wave_table_block(self, items):
        cells = {}
        for pos, cell in items:
            if pos in cells:
                raise UsfParseError(f'duplicate wave_table cell: {pos}')
            if not 0 <= pos <= 255:
                raise UsfParseError(f'wave_table position out of range: {pos}')
            cells[pos] = cell
        return ('wave_table', cells)

    def pwm_mode(self, items):
        return ('mode', str(items[0]))

    def pwm_speed(self, items):
        return ('speed', int(items[0]))

    def pwm_init(self, items):
        return ('init', items[0])

    def pwm_min_hi(self, items):
        return ('min_hi', int(items[0]))

    def pwm_max_hi(self, items):
        return ('max_hi', int(items[0]))

    def pwm_phase1_dir(self, items):
        return ('phase1_dir', str(items[0]))

    def pwm_phase1_bound(self, items):
        return ('phase1_bound', items[0])

    def pwm_phase1_step(self, items):
        return ('phase1_step', items[0])

    def pwm_lo_or_mask(self, items):
        return ('lo_or_mask', items[0])

    def pwm_speed_steps(self, items):
        return ('speed_steps', [int(x) for x in items])

    def pwm_step_base(self, items):
        return ('step_base', int(items[0]))

    def pwm_keep_running(self, items):
        return ('keep_running', items[0])

    def pwm_args(self, items):
        return PwmConfig(**dict(items))

    def inst_pwm(self, items):
        return ('pwm', items[0])

    def inst_adsr(self, items):
        return ('adsr', (items[0], items[1]))

    def arp_offsets(self, items):
        return ('offsets', list(items))

    def arp_period(self, items):
        return ('period', int(items[0]))

    def arp_interval(self, items):
        return ('interval', int(items[0]))

    def arp_phase_invert(self, items):
        return ('phase_invert', items[0])

    def arp_args(self, items):
        return ArpConfig(**dict(items))

    def inst_arp(self, items):
        return ('arp', items[0])

    def vib_scale(self, items):
        return ('scale', int(items[0]))

    def vib_onset(self, items):
        return ('onset', int(items[0]))

    def vib_shape(self, items):
        return ('shape', str(items[0]))

    def vib_period_frames(self, items):
        return ('period_frames', int(items[0]))

    def vib_polarity(self, items):
        return ('polarity', str(items[0]))

    def vib_depth_semitones(self, items):
        return ('depth_semitones', float(items[0]))

    def vib_amplitude(self, items):
        return ('amplitude', int(items[0]))

    def vib_speed(self, items):
        return ('speed', int(items[0]))

    def vib_direction(self, items):
        return ('direction', str(items[0]))

    def vib_ramp(self, items):
        return ('ramp', int(items[0]))

    def vib_args(self, items):
        return VibratoConfig(**dict(items))

    def inst_vibrato(self, items):
        return ('vibrato', items[0])

    def env_release_ctrl(self, items):
        return ('release_ctrl', items[0])

    def env_gate_mode(self, items):
        return ('gate_mode', str(items[0]))

    def env_gate_open(self, items):
        return ('gate_open', bool(items[0]))

    def env_args(self, items):
        return EnvelopeConfig(**dict(items))

    # ----- Phase 1 sub-configs: slide + incby2 -----
    def slide_mode(self, items):
        return ('mode', str(items[0]))

    def slide_initial_dir(self, items):
        return ('initial_dir', str(items[0]))

    def slide_upper_delta(self, items):
        return ('upper_delta', items[0])

    def slide_lower_delta(self, items):
        return ('lower_delta', items[0])

    def slide_step(self, items):
        return ('step', items[0])

    def slide_high_oct_arp(self, items):
        return ('high_oct_arp', items[0])

    def slide_half_rate(self, items):
        return ('half_rate', items[0])

    def slide_args(self, items):
        return FreqSlideConfig(**dict(items))

    def inst_slide(self, items):
        return ('freq_slide_config', items[0])

    def incby2_mode(self, items):
        return ('mode', str(items[0]))

    def incby2_step(self, items):
        return ('step', items[0])

    def incby2_onset(self, items):
        return ('onset', int(items[0]))

    def incby2_late_gate(self, items):
        return ('late_gate', int(items[0]))

    def incby2_every_frame(self, items):
        return ('every_frame', items[0])

    def incby2_args(self, items):
        return IncBy2Config(**dict(items))

    def inst_incby2(self, items):
        return ('inc_by2_config', items[0])

    def inst_envelope(self, items):
        return ('envelope', items[0])

    # FC v1 — decomposed effect blocks
    def pp_program(self, items):
        return ('program', int(items[0]))

    def pp_increment(self, items):
        return ('increment', int(items[0]))

    def pulse_prog_args(self, items):
        from src.usf.types import PulseProgConfig
        return PulseProgConfig(**dict(items))

    def inst_pulse_prog(self, items):
        return ('pulse_prog', items[0])

    def fp_program(self, items):
        return ('program', int(items[0]))

    def fp_strange(self, items):
        return ('strange', bool(items[0]))

    def fp_double_voice(self, items):
        return ('double_voice', bool(items[0]))

    def fp_aux_bits(self, items):
        return ('aux_bits', int(items[0]))

    def fpc_keep_running(self, items):
        return ('keep_running', bool(items[0]))

    def filter_prog_args(self, items):
        from src.usf.types import FilterProgConfig
        return FilterProgConfig(**dict(items))

    def inst_filter_prog(self, items):
        return ('filter_prog', items[0])

    def swenv_seg(self, items):
        return ('seg', (int(items[0]), int(items[1])))

    def swenv_args(self, items):
        start = int(items[0])
        segs = [it[1] for it in items[1:]
                if isinstance(it, tuple) and it[0] == 'seg']
        tail = [it for it in items[1:]
                if not (isinstance(it, tuple) and it[0] == 'seg')]
        loop = int(tail[0]) if tail else None
        return SweepEnvelope(start=start, phases=segs, loop=loop)

    def inst_pulse_env(self, items):
        return ('pulse_env', items[0])

    def inst_filter_env(self, items):
        return ('filter_env', items[0])

    def default_filter_block(self, items):
        # items[0] = the SweepEnvelope from swenv_args (the idle V3 sweep).
        return ('default_filter', items[0])

    def default_pulse_block(self, items):
        # items[0] = the SweepEnvelope from swenv_args (the idle PW sweep).
        return ('default_pulse', items[0])

    def efx_tone_arp(self, _):       return 'tone_arp'
    def efx_pulse_arp(self, _):      return 'pulse_arp'
    def efx_drum(self, _):           return 'drum'
    def efx_tonesweep_up(self, _):   return 'tonesweep_up'
    def efx_wave_arp(self, _):       return 'wave_arp'
    def efx_noise_tick(self, _):     return 'noise_tick'
    def efx_pulse_run(self, _):      return 'pulse_run'
    def efx_filter_program(self, _): return 'filter_program'
    def efx_noise_attack(self, _):   return 'noise_attack'

    def effect_name(self, items):
        return items[0]

    def effects_args(self, items):
        return frozenset(items)

    def inst_effects(self, items):
        return ('effects', items[0])

    def instrument_block(self, items):
        # items: INT [name] field*
        inst_id = int(items[0])
        idx = 1
        name = None
        if idx < len(items) and isinstance(items[idx], str):
            name = items[idx]
            idx += 1
        fields = dict(items[idx:])
        inst = Instrument(id=inst_id, name=name)
        for k, val in fields.items():
            if not hasattr(inst, k):
                raise UsfParseError(f'instrument {inst_id}: unknown field {k!r}')
            setattr(inst, k, val)
        return inst

    # ----- subtunes -----
    def kind_music(self, _):
        return 'music'

    def kind_digi(self, _):
        return 'digi'

    def kind_sfx(self, _):
        return 'sfx'

    def kind_dmcsfx(self, _):
        return 'dmcsfx'

    def dmcsfx_body(self, items):
        return ('dmcsfx', {'song': int(items[0])})

    # ----- dmc_sfx block -----
    def dmc_sfx_field(self, items):  return items[0]
    def dsfx_counter(self, items):   return ('init_counter', int(items[0]))
    def dsfx_live(self, items):      return ('live_counter_fidx', int(items[0]))
    def dsfx_filter(self, items):    return ('filter_lfo', tuple(items[0]))
    def dsfx_wave(self, items):      return ('wave_table', tuple(items[0]))
    def dsfx_freqlo(self, items):    return ('freq_lo', tuple(items[0]))
    def dsfx_freqhi(self, items):    return ('freq_hi', tuple(items[0]))

    def dsfx_instrument(self, items):
        # INT ctrl_list freqbase_list ad sr pw_lo pw_hi
        return ('_inst', int(items[0]), SfxInstrument(
            ctrl=tuple(items[1]), freqbase=tuple(items[2]),
            ad=int(items[3]), sr=int(items[4]),
            pw_lo=int(items[5]), pw_hi=int(items[6])))

    def dsfx_song(self, items):
        # INT voice duration wavestep increment instrument
        return ('_song', int(items[0]), SfxSong(
            voice=int(items[1]), duration=int(items[2]), wavestep=int(items[3]),
            increment=int(items[4]), instrument=int(items[5])))

    def dsfx_voice_init(self, items):
        # INT duration pitch increment wavestep instrument
        return ('_vinit', int(items[0]), SfxVoiceInit(
            duration=int(items[1]), pitch=int(items[2]), increment=int(items[3]),
            wavestep=int(items[4]), instrument=int(items[5])))

    def dmc_sfx_block(self, items):
        eng = SfxEngine()
        insts, songs, vinits = {}, {}, {}
        for it in items:
            tag = it[0]
            if tag == '_inst':
                insts[it[1]] = it[2]
            elif tag == '_song':
                songs[it[1]] = it[2]
            elif tag == '_vinit':
                vinits[it[1]] = it[2]
            else:
                setattr(eng, tag, it[1])
        eng.instruments = [insts[i] for i in sorted(insts)]
        eng.songs = [songs[i] for i in sorted(songs)]
        eng.voice_init = tuple(vinits[i] for i in sorted(vinits))
        return ('dmc_sfx', eng)

    def subtune_kind(self, items):
        return items[0]

    def subtune_body(self, items):
        return items[0]

    def is_sfx_field(self, items):
        return ('is_sfx', bool(items[0]))

    # ----- global automation track -----
    def g_dyn(self, items):    return ('dyn', int(items[0]))
    def g_cutoff(self, items): return ('cutoff', int(items[0]))
    def g_cutoff_lo(self, items): return ('cutoff_lo', int(items[0]))
    def g_res(self, items):    return ('res', int(items[0]))
    def g_mode(self, items):   return ('mode', int(items[0]))
    def g_route(self, items):  return ('route', int(items[0]))

    def global_event(self, items):
        return GlobalEvent(step=int(items[0]), **dict(items[1:]))

    def global_block(self, items):
        # optional leading INT = chip index (multi-SID); bare form = chip 1
        chip = 1
        if items and not isinstance(items[0], GlobalEvent):
            chip = int(items[0])
            items = items[1:]
        return ('_global', chip, list(items))

    def tempo_chip(self, items):
        return ('_tempo_chip', int(items[0]), int(items[1]))

    def sub_override(self, items):
        return ('_sub_override', items[0])

    def origin_engine_field(self, items):
        return ('_origin_engine', str(items[0]))

    def music_body(self, items):
        # 'tempo' ':' INT tempo_chip* is_sfx_field? params_block?
        #   init_block? voice_block+ global_block*
        tempo = int(items[0])
        rest = list(items[1:])
        tempos = {}
        while rest and isinstance(rest[0], tuple) \
                and rest[0][0] == '_tempo_chip':
            _, chip, t = rest.pop(0)
            if chip not in (2, 3):
                raise UsfParseError(f'tempo chip must be 2 or 3, got {chip}')
            if chip in tempos:
                raise UsfParseError(f'tempo {chip}: appears twice')
            tempos[chip] = t
        origin_engine = None
        if rest and isinstance(rest[0], tuple) \
                and rest[0][0] == '_origin_engine':
            origin_engine = rest.pop(0)[1]
        is_sfx = False
        if rest and isinstance(rest[0], tuple) and rest[0][0] == 'is_sfx':
            is_sfx = rest.pop(0)[1]
        params = None
        init = None
        if rest and isinstance(rest[0], Params):
            params = rest.pop(0)
        if rest and isinstance(rest[0], InitState):
            init = rest.pop(0)
        sub_freq, sub_dfilt, sub_wave, sub_vibovr = None, None, None, None
        while rest and isinstance(rest[0], tuple) \
                and rest[0][0] == '_sub_override':
            ov = rest.pop(0)[1]
            if isinstance(ov, tuple) and ov and ov[0] == 'freq_table':
                sub_freq = ov[1]
            elif isinstance(ov, tuple) and ov and ov[0] == 'default_filter':
                sub_dfilt = ov[1]
            elif isinstance(ov, tuple) and ov and ov[0] == 'wave_programs':
                sub_wave = ov[1]
            elif isinstance(ov, tuple) and ov \
                    and ov[0] == 'offtable_vibdepth':
                sub_vibovr = ov[1]
        globals_ = {}
        while rest and isinstance(rest[-1], tuple) \
                and rest[-1][0] == '_global':
            _, chip, evs = rest.pop()
            if chip not in (1, 2, 3):
                raise UsfParseError(f'global chip must be 2 or 3, got {chip}')
            if chip in globals_:
                raise UsfParseError(f'global block for chip {chip} '
                                    'appears twice')
            globals_[chip] = evs
        voices = rest
        # Multi-SID validation: voices come in whole 3-voice CHIP BLOCKS
        # (chip of voice v = (v-1)//3 + 1), ascending. A multi-SID subtune
        # need not sound every chip — a dispatch wrapper may gate a chip's
        # player off for some subtunes — so the blocks present may start
        # above 1 and skip (a chip-2-only subtune is voices 4..6).
        if not voices or len(voices) % 3:
            raise UsfParseError(
                f'music subtune has {len(voices)} voice blocks; '
                'expected a multiple of 3 (one block per sounding chip)')
        ids = [v.id for v in voices]
        blocks = sorted({(i - 1) // 3 for i in ids})
        if ids != sorted(ids) or len(blocks) != len(voices) // 3 or \
                ids != [3 * b + k for b in blocks for k in (1, 2, 3)]:
            raise UsfParseError(
                'voice blocks must be whole ascending 3-voice chip blocks '
                f'(1-3, 4-6, 7-9), got {ids}')
        n_chips = blocks[-1] + 1
        for chip in list(tempos) + list(globals_):
            if chip > n_chips:
                raise UsfParseError(
                    f'chip {chip} referenced but subtune has only '
                    f'{n_chips * 3} voices')
        return ('music', {'tempo': tempo, 'voices': voices,
                          'params': params, 'init': init,
                          'is_sfx': is_sfx, 'origin_engine': origin_engine,
                          'freq_table': sub_freq, 'default_filter': sub_dfilt,
                          'wave_programs': sub_wave,
                          'offtable_vibdepth': sub_vibovr,
                          'global_track': globals_.get(1, []),
                          'tempo2': tempos.get(2), 'tempo3': tempos.get(3),
                          'global_track2': globals_.get(2, []),
                          'global_track3': globals_.get(3, [])})

    def digi_body(self, items):
        return ('digi', {'sample': str(items[0])})

    # ----- sfx body -----
    def sfx_v1(self, items):
        return ('v1', tuple(int(x) for x in items))

    def sfx_v2(self, items):
        return ('v2', tuple(int(x) for x in items))

    def sfx_sweep_start(self, items):
        return ('start_index', int(items[0]))

    def sfx_sweep_end(self, items):
        return ('end_index', int(items[0]))

    def sfx_sweep_rate(self, items):
        return ('rate', int(items[0]))

    def sfx_sweep_direction(self, items):
        return ('direction', str(items[0]))

    def sfx_sweep_kv(self, items):
        return items[0]

    def sfx_sweep(self, items):
        return ('_sweep', dict(items))

    def sfx_v2_offset(self, items):
        return ('v2_offset', int(items[0]))

    def sfx_flag_toggle_v1(self, _):
        return 'toggle_v1'

    def sfx_flag_toggle_v2(self, _):
        return 'toggle_v2'

    def sfx_flag_skip_v1(self, _):
        return 'skip_v1'

    def sfx_flag_skip_both(self, _):
        return 'skip_both'

    def sfx_flag(self, items):
        return items[0]

    def sfx_flags(self, items):
        flags = {'toggle_v1': False, 'toggle_v2': False,
                 'skip_v1': False, 'skip_both': False}
        for name in items:
            flags[name] = True
        return ('_flags', flags)

    def ext_freq_pair(self, items):
        return (int(items[0]), int(items[1]))

    def sfx_extended_freq(self, items):
        return ('extended_freq', dict(items))

    def sfx_field(self, items):
        return items[0]

    def sfx_body(self, items):
        sweep_dict = {}
        flag_dict = {}
        out = {}
        for key, val in items:
            if key == '_sweep':
                sweep_dict = val
            elif key == '_flags':
                flag_dict = val
            else:
                out[key] = val
        out.update(sweep_dict)
        out.update(flag_dict)
        return ('sfx', out)

    def subtune_block(self, items):
        sub_id = int(items[0])
        kind = items[1]
        body_kind, body_data = items[2]
        if body_kind != kind:
            raise UsfParseError(
                f'subtune {sub_id}: declared {kind} but body looks like {body_kind}')
        if kind == 'music':
            return MusicSubtune(
                id=sub_id, tempo=body_data['tempo'],
                voices=body_data['voices'],
                params=body_data.get('params'),
                init=body_data.get('init'),
                is_sfx=body_data.get('is_sfx', False),
                origin_engine=body_data.get('origin_engine'),
                freq_table=body_data.get('freq_table'),
                default_filter=body_data.get('default_filter'),
                wave_programs=body_data.get('wave_programs'),
                offtable_vibdepth=body_data.get('offtable_vibdepth'),
                global_track=body_data.get('global_track', []),
                tempo2=body_data.get('tempo2'),
                tempo3=body_data.get('tempo3'),
                global_track2=body_data.get('global_track2', []),
                global_track3=body_data.get('global_track3', []))
        elif kind == 'digi':
            return DigiSubtune(id=sub_id, sample=body_data['sample'])
        elif kind == 'dmcsfx':
            return DmcSfxSubtune(id=sub_id, song=body_data['song'])
        else:
            # sfx — body_data is the decomposed SFX record
            return SfxSubtune(id=sub_id, **body_data)

    # ----- voice / orderlist / patterns -----
    def ol_loop(self, items):
        loop_tr, skip, kind = None, 0, None
        for it in items[1:]:
            if isinstance(it, tuple):
                if it[0] == 'tr':
                    loop_tr = it[1]        # ('tr', T) from ol_transpose
                elif it[0] == 'skip':      # byte-faithful landing skip
                    skip = it[1]
                elif it[0] == 'termkind':  # 'endless' | 'inject'
                    kind = it[1]
        return ('loop', (int(items[0]), loop_tr, skip, kind))

    def ol_stop(self, _):
        return ('stop', None)

    def ol_ring(self, _):
        # byte-faithful: no terminator byte — the 8-bit position wraps
        return ('ring', None)

    def ol_skip(self, items):
        return ('skip', int(items[0]))

    def tk_endless(self, _):
        return ('termkind', 'endless')

    def tk_inject(self, _):
        return ('termkind', 'inject')

    def ol_jump(self, items):
        return ('jump', int(items[0]))

    def ol_dual(self, _):
        return ('dual', True)

    def ol_faithful(self, _):
        return ('faithful_flag',)

    def orderlist_terminator(self, items):
        return items[0]

    def ol_repeat(self, items):
        return ('rep', int(items[0]))

    def ol_transpose(self, items):
        return ('tr', int(items[0]))

    def ol_transpose_neg(self, items):
        return ('tr', -int(items[0]))

    def ol_voiceinc(self, items):
        return ('vi', int(items[0]))

    def ol_intro(self, items):
        return ('intro', int(items[0]))

    def ol_extra(self, items):
        return ('extra', int(items[0]))

    def ol_stated(self, _):
        return ('stated_flag',)

    def orderlist_entry(self, items):
        # a[~i][*b][+c][!k][^d][@T][&] →
        # ('entry', pid, tr, vi, rep, intro, extra, jump, dual)
        # tr is None when the modifier is ABSENT (stated form: absent =
        # inherit; legacy form: absent = 0 — voice_block resolves).
        pid = None
        rep, tr, vi, intro, extra = 1, None, None, None, 0
        jump, dual = None, False
        for it in items:
            if isinstance(it, tuple):
                kind, val = it[0], it[1] if len(it) > 1 else None
                if kind == 'rep':
                    rep = val
                elif kind == 'tr':
                    tr = val
                elif kind == 'vi':
                    vi = val
                elif kind == 'intro':
                    intro = val
                elif kind == 'extra':
                    extra = val
                elif kind == 'jump':
                    jump = val
                elif kind == 'dual':
                    dual = True
            else:
                pid = int(it)
        return ('entry', pid, tr, vi, rep, intro, extra, jump, dual)

    def orderlist(self, items):
        # entries followed by optional terminator
        entries = []
        transposes = []
        voiceincs = []
        repeats = []
        loop_to = None
        loop_transpose = None

        stop = False
        intros = []
        extras = []
        jumps = []
        duals = []
        loop_skip = 0
        stated_term = None
        for it in items:
            kind = it[0]
            if kind == 'entry':
                _, pid, tr, vi, rep, intro, extra, jump, dual = it
                entries.append(pid)
                transposes.append(tr)
                voiceincs.append(vi)
                repeats.append(rep)
                intros.append(intro)
                extras.append(extra)
                jumps.append(jump)
                duals.append(dual)
            elif kind == 'loop':
                loop_to, loop_transpose, loop_skip, stated_term = it[1]
            elif kind == 'stop':
                stop = True
            elif kind == 'ring':
                stated_term = 'ring'
        # Raw transpose slots are None where the modifier was absent; the
        # stated-vs-legacy resolution happens in voice_block (which sees
        # the `stated` keyword). Stash the raw lists on the Orderlist.
        if all(r == 1 for r in repeats):
            repeats = []
        o = Orderlist(entries=entries, loop_to=loop_to, stop=stop,
                      loop_transpose=loop_transpose,
                      transposes=transposes, voiceincs=voiceincs,
                      repeats=repeats)
        o.intro_entries = intros if any(x is not None for x in intros) else []
        o.extra_cmds = extras if any(extras) else []
        # byte-faithful facts (I5) — elided to their defaults when absent
        o.jump_ins = jumps if any(x is not None for x in jumps) else []
        o.dual_flags = duals if any(duals) else []
        o.loop_skip = loop_skip or 0
        o.stated_term = stated_term
        return o

    def pattern_block(self, items):
        # INT ["length" = INT] note_row*  — length omitted for patterns
        # with stated-inherited rows (context-dependent total)
        pat_id = int(items[0])
        length = None
        idx = 1
        if idx < len(items) and isinstance(items[idx], Token):
            length = int(items[idx])
            idx += 1
        rows = list(items[idx:])
        return Pattern(id=pat_id, length=length, rows=rows)

    def voice_block(self, items):
        voice_id = int(items[0])
        stated = any(isinstance(it, tuple) and it and it[0] == 'stated_flag'
                     for it in items)
        faithful = any(isinstance(it, tuple) and it
                       and it[0] == 'faithful_flag' for it in items)
        rest = [it for it in items
                if not (isinstance(it, tuple) and it
                        and it[0] in ('stated_flag', 'faithful_flag'))]
        orderlist = rest[1]
        patterns = list(rest[2:])
        if faithful:
            orderlist.byte_faithful = True
        raw = orderlist.transposes            # None = modifier absent
        if stated:
            # STATED form: raw values are the stated command marks; the
            # effective (first-pass) values are derived by inheritance
            # (cur starts at 0 — the engine's init state). Voiceinc is a
            # sticky command too (FC) — same derivation.
            orderlist.stated = True
            orderlist.stated_marks = list(raw)
            eff, cur = [], 0
            for v in raw:
                if v is not None:
                    cur = v
                eff.append(cur)
            orderlist.transposes = eff if any(eff) else []
            vraw = orderlist.voiceincs        # None = modifier absent
            if any(x is not None for x in vraw):
                orderlist.stated_vmarks = list(vraw)
                veff, cur = [], 0
                for x in vraw:
                    if x is not None:
                        cur = x
                    veff.append(cur)
                orderlist.voiceincs = veff if any(veff) else []
            else:
                orderlist.voiceincs = []
            # Wrap PICKUP re-derivation (engines whose state persists over
            # the wrap consume it; others ignore). The carried value C is
            # the trailing stated command if present (a stated list's
            # `loop@N+T` annotation IS the trailing command), else the
            # end-of-list effective. The head inherits C only when
            # unmarked; a marked head re-establishes.
            if orderlist.loop_to is not None:
                trail = orderlist.loop_transpose      # terminator +T = trail
                orderlist.stated_trail = trail
                carried = trail if trail is not None else (
                    eff[-1] if eff else 0)
                if raw and raw[orderlist.loop_to] is None and carried:
                    orderlist.loop_transpose = carried
                else:
                    orderlist.loop_transpose = None
        else:
            orderlist.transposes = (
                [v or 0 for v in raw] if any(v for v in raw) else [])
            orderlist.voiceincs = (
                [x or 0 for x in orderlist.voiceincs]
                if any(x for x in orderlist.voiceincs) else [])
        return VoiceBlock(id=voice_id, orderlist=orderlist, patterns=patterns)

    # ----- notes + pitches + instrument refs + fx -----
    def pitch_named(self, items):
        # NOTE_NAME like 'C-5' or 'D#3'; octave may be 2 digits (off-table
        # pitches 97..255 — off-table reads, e.g. ghost-march ties).
        tok = str(items[0])
        letter = tok[0]
        sep = tok[1]
        octave = int(tok[2:])
        name = letter if sep == '-' else letter + '#'
        return Pitch(name=name, octave=octave)

    def pitch_rest(self, _):
        return Pitch.rest()

    def pitch(self, items):
        return items[0]

    def instr_id(self, items):
        # token text is like 'i12' — strip the 'i'
        return InstrumentRef(id=int(str(items[0])[1:]))

    def instr_name(self, items):
        # token text is like 'i:lead' — strip the 'i:'
        return InstrumentRef(name=str(items[0])[2:])

    def instr_ref(self, items):
        return items[0]

    def fx_tie(self, _):
        return 'tie'

    def fx_no_release(self, _):
        return 'no_release'

    def fx_porta(self, items):
        # encode as a string so it round-trips through tuple[str]
        return f'porta={int(items[0])}'

    def fx_tempo(self, items):
        return f'tempo={int(items[0])}'

    def fx_vol(self, items):
        return f'vol={int(items[0])}'

    def fx_song_pos(self, items):
        return f'song_pos={int(items[0])}'

    def fx_section_end(self, items):
        return f'section_end={int(items[0])}'

    def fx_set_dur(self, items):
        return f'set_dur=${items[0]:02X}'

    def fx_set_instr(self, items):
        return f'set_instr={int(items[0])}'

    def fx_frq(self, items):
        return f'frq=${int(items[0]):02X}'

    def fx_fade_in(self, items):
        return f'fade_in=${int(items[0]):02X}'

    def fx_fade_out(self, items):
        return f'fade_out=${int(items[0]):02X}'

    def fx_adr(self, items):
        return f'adr=${int(items[0]):02X}'

    def fx_srr(self, items):
        return f'srr=${int(items[0]):02X}'

    def fx_freq_bias(self, items):
        return f'freq_bias=${int(items[0]):02X}'

    def fx_f0_vib_width(self, items):
        return f'f0_vib_width={int(items[0])}'

    def fx_f0_wave_count(self, items):
        return f'f0_wave_count={int(items[0])}'

    def fx_gate_tie(self, _):
        return 'gate_tie'

    def fx_named(self, items):
        return f'fx:{items[0]}'

    def fx_glide(self, items):
        return f'glide={int(items[0])}'

    def fx_glide_up(self, items):
        return f'glide_up=${int(items[0]):04X}'

    def fx_glide_down(self, items):
        return f'glide_down=${int(items[0]):04X}'

    def fx_filter_sweep(self, items):
        return f'filter_sweep=${int(items[0]):02X},{int(items[1])}'

    def fx_arp3(self, items):
        return 'arp=%d,%d,%d' % tuple(int(x) for x in items)

    def fx_vibrato2(self, items):
        return 'vibrato=%d,%d' % (int(items[0]), int(items[1]))

    def fx_fcutadd(self, items):
        return f'fcutadd={int(items[0])}'

    def fx_fctrl(self, items):
        return f'fctrl={int(items[0])}'

    def fx_keyoff(self, _):
        return 'keyoff'

    def fx_glide_onset(self, items):
        return f'glide_onset={int(items[0])}'

    def fx_glide_ticks(self, items):
        return f'glide_ticks={int(items[0])}'

    def fx_glide_hold(self, items):
        return f'glide_hold={int(items[0])}'

    def fx_wave_adjust(self, items):
        return f'wave_adjust={int(items[0])}'

    def fx_filter(self, items):
        return f'filter=${int(items[0]):02X}'

    def fx_gate_toggle(self, _):
        return 'gate_toggle'

    def fx_glide_to(self, items):
        return f'glide_to={str(items[0])}'

    def fx_noretrig(self, _):
        return 'noretrig'

    def fx_dcmd(self, _):
        return 'dur_cmd'

    def fx_icmd(self, _):
        return 'instr_cmd'

    def fx_vcmd(self, _):
        return 'vol_cmd'

    def fx_runon(self, _):
        return 'runon'

    def fx_note_clock(self, _):
        return 'note_clock'

    def fx_softcmd(self, items):
        return f'soft_cmd={int(items[0])}'

    def fx_dcmd_n(self, items):
        return f'dur_cmd={int(items[0])}'

    def fx_icmd_n(self, items):
        return f'instr_cmd={int(items[0])}'

    def fx_vcmd_n(self, items):
        return f'vol_cmd={int(items[0])}'

    def freq_table_block(self, items):
        # items[0] is a byte_list (= list[int])
        return ('freq_table', items[0])

    def ovd_entry(self, items):
        return tuple(int(x) for x in items)        # (note, depth)

    def offtable_vibdepth_block(self, items):
        return ('offtable_vibdepth', [tuple(e) for e in items])

    def sl_n_voices(self, items):
        return ('n_voices', int(items[0]))

    def sl_scalar_const(self, items):
        return ('scalar', {'offset': int(items[0]),
                           'kind': 'const', 'value': int(items[1])})

    def sl_scalar_var(self, items):
        return ('scalar', {'offset': int(items[0]),
                           'kind': 'var', 'var': str(items[1])})

    def sl_pv_const(self, items):
        return ('per_voice', {'offset': int(items[0]),
                              'kind': 'const', 'value': int(items[1])})

    def sl_pv_var(self, items):
        return ('per_voice', {'offset': int(items[0]),
                              'kind': 'var', 'var': str(items[1])})

    def sl_field(self, items):
        return items[0]

    def se_stop_marker(self, items):
        return ('stop_marker', str(items[0]))

    def se_fill_value(self, items):
        return ('fill_value', int(items[0]))

    def se_loop_marker(self, items):
        return ('loop_marker', str(items[0]))

    def song_end_field(self, items):
        return items[0]

    def song_end_block(self, items):
        cfg = SongEndConfig()
        for k, v in items:
            setattr(cfg, k, v)
        return ('song_end', cfg)

    def ib_silence_all(self, items):
        return ('silence_all_voices_on_frame_0', items[0])

    def ib_no_first_attack(self, items):
        return ('no_first_attack_voice', int(items[0]))

    def ib_master_vol_every_frame(self, items):
        return ('master_vol_every_frame', int(items[0]))

    def ib_master_vol_every_note(self, items):
        return ('master_vol_every_note', int(items[0]))

    def ib_artic_int(self, items):
        return int(items[0])

    def ib_artic_name(self, items):
        return str(items[0])

    # articulation behaviors ride the GENERIC CNAME-key rule (see grammar
    # note — keyword terminals would shadow CNAME in old-corpus params{}).
    _IB_ARTIC = {'gate_off_hold': str, 'rest_effects': str,
                 'hard_restart': str,          # CNAME or INT, normalized str
                 'cymbal_onset': int, 'vibrato_ramp': str,
                 'vibrato_ramp_persist': int,
                 'vibrato_step_dead': int, 'vibrato_phase_persist': int}

    def ib_artic(self, items):
        key, val = str(items[0]), items[1]
        typ = self._IB_ARTIC.get(key)
        if typ is None:
            raise UsfParseError(f'init_behavior: unknown field {key!r}')
        return (key, typ(val))

    def init_behavior_field(self, items):
        return items[0]

    def init_behavior_block(self, items):
        cfg = InitBehaviorConfig()
        for k, v in items:
            setattr(cfg, k, v)
        return ('init_behavior', cfg)

    def mv_subtrahend_voice(self, items):
        return ('subtrahend_voice', int(items[0]))

    def mv_base(self, items):
        return ('base', items[0])

    def mv_trigger(self, items):
        return ('trigger', str(items[0]))

    def mv_reset_on_loop(self, items):
        return ('reset_on_loop', items[0])

    def mv_underflow_clamp(self, items):
        return ('underflow_clamp', items[0])

    def master_vol_field(self, items):
        return items[0]

    def master_vol_block(self, items):
        cfg = MasterVolConfig()
        for k, v in items:
            setattr(cfg, k, v)
        return ('master_vol', cfg)

    def sfx_framectr_ofs(self, items):
        return ('framectr_ofs', items[0])

    def sfx_state_ofs(self, items):
        return ('state_ofs', items[0])

    def sfx_kv(self, items):
        return items[0]

    def sfx_block(self, items):
        cfg = SfxConfig()
        for k, v in items:
            setattr(cfg, k, v)
        return ('sfx', cfg)

    def arp_program(self, items):
        # items[0] = INT index; rest = signed_int offsets
        return (int(items[0]), tuple(int(x) for x in items[1:]))

    def arp_programs_block(self, items):
        return ('arp_programs', {n: offs for n, offs in items})

    def pp_wrap(self, _):
        return ('wrap', True)

    def pp_flip(self, _):
        return ('flip', True)

    def pp_seg(self, items):
        thr = int(items[0]); step = int(items[1])
        flip = len(items) > 2 and items[2] == ('flip', True)
        return ('seg', (thr, step, flip))

    def pulse_program(self, items):
        n = int(items[0]); lo = int(items[1]); hi = int(items[2])
        wrap = False; segs = []
        for it in items[3:]:
            if it == ('wrap', True):
                wrap = True
            elif isinstance(it, tuple) and it[0] == 'seg':
                segs.append(it[1])
        return (n, {'lo': lo, 'hi': hi, 'wrap': wrap, 'segs': segs})

    def pulse_programs_block(self, items):
        return ('pulse_programs', {n: prog for n, prog in items})

    def fp_seg(self, items):
        return ('seg', (int(items[0]), int(items[1])))

    def fp_step(self, items):
        return ('step', (int(items[0]), int(items[1])))

    def filter_program_dur(self, items):
        n = int(items[0])
        head = [it for it in items[1:]
                if not (isinstance(it, tuple) and it[0] == 'step')]
        steps = [it[1] for it in items[1:] if isinstance(it, tuple)
                 and it[0] == 'step']
        res, mode, init, repeat, stop = (int(v) for v in head)
        return (n, {'res': res, 'mode': mode, 'init': init,
                    'repeat': repeat, 'stop': stop, 'steps': steps})

    def filter_program(self, items):
        n = int(items[0])
        head = [it for it in items[1:]
                if not (isinstance(it, tuple) and it[0] == 'seg')]
        segs = [it[1] for it in items[1:] if isinstance(it, tuple)
                and it[0] == 'seg']
        if len(head) == 5:           # init onset d418 final end
            init, onset, d418, final, end = (int(v) for v in head)
        else:                        # init d418 final end (Tel, onset 0)
            init, d418, final, end = (int(v) for v in head)
            onset = 0
        return (n, {'init': init, 'onset': onset, 'd418': d418,
                    'final': final, 'end': end, 'segs': segs})

    def filter_programs_block(self, items):
        return ('filter_programs', {n: prog for n, prog in items})

    def filter_mod_entry(self, items):
        n = int(items[0])
        start, ip = int(items[1]), int(items[2])
        # tail: optional stop_phase INT, optional `once` marker, then steps.
        # (LALR without placeholders: classify by shape — a step is a
        # ('step', v) tuple, `once` arrives as its FM_ONCE token, a bare
        # remaining scalar is the stop_phase.)
        sp, loop, direct, steps = None, True, False, []
        for it in items[3:]:
            if isinstance(it, tuple) and it and it[0] == 'step':
                steps.append(it[1])
            elif str(it) == 'once':
                loop = False
            elif str(it) == 'direct':
                direct = True
            elif it is not None:
                sp = int(it)
        e = {'start': start, 'init_phase': ip, 'stop_phase': sp,
             'steps': steps}
        if not loop:
            e['loop'] = False
        if direct:
            e['target'] = 'cutoff'
        return (n, e)

    def filter_mod_block(self, items):
        return ('filter_mod', {n: e for n, e in items})

    def dnum_list(self, items):
        return [int(x) for x in items]

    def drum_program(self, items):
        return (int(items[0]), {'wave': items[1], 'tone': items[2]})

    def fc_aux_block(self, items):
        return items[0]

    def drum_programs_block(self, items):
        return ('drum_programs', {n: prog for n, prog in items})

    def wave_program(self, items):
        d = {'ctrl': items[1], 'freq': items[2]}
        if len(items) > 3:
            d['loop'] = int(items[3])
        return (int(items[0]), d)

    def wave_programs_block(self, items):
        return ('wave_programs', {n: prog for n, prog in items})

    def attack_len_decl(self, items):
        return ('attack_len', items[0])

    def attack_wave_decl(self, items):
        return ('attack_wave', items[0])

    def wave_arp_decl(self, items):
        return ('wave_arp', items[0])

    def pulse_arp_decl(self, items):
        return ('pulse_arp', items[0])

    def state_layout_block(self, items):
        # items is a list of tuples ('n_voices', N) | ('scalar', dict)
        # | ('per_voice', dict). Reassemble into a StatebufLayout-shaped
        # dict; the build path constructs the actual StatebufLayout.
        d = {'n_voices': None, 'scalars': [], 'per_voice': []}
        for k, v in items:
            if k == 'n_voices':
                d['n_voices'] = v
            elif k == 'scalar':
                d['scalars'].append(v)
            elif k == 'per_voice':
                d['per_voice'].append(v)
        return ('state_layout', d)

    def fx_flag(self, items):
        return items[0]

    def note_row(self, items):
        pitch = items[0]
        idx = 1
        dur = None                    # absent = stated-inherited
        if idx < len(items) and isinstance(items[idx], Token):
            dur = int(items[idx])
            idx += 1
        instr = None
        if idx < len(items) and isinstance(items[idx], InstrumentRef):
            instr = items[idx]
            idx += 1
        fx = tuple(items[idx:])
        return NoteRow(pitch=pitch, duration=dur, instr=instr, fx_flags=fx)

    # ----- start -----
    def start(self, items):
        psid = None
        params = None
        init = None
        instruments = []
        subtunes = []
        freq_table = None
        state_layout = None
        song_end = None
        init_behavior = None
        master_vol = None
        sfx = None
        arp_programs = {}
        pulse_programs = {}
        filter_programs = {}
        filter_mod = {}
        drum_programs = {}
        attack_len = []
        attack_wave = []
        wave_arp = []
        pulse_arp = []
        wave_programs = {}
        default_filter = None
        default_pulse = None
        dmc_sfx = None
        environment = None
        offtable_vibdepth = []
        wave_table = None
        seen_blocks = set()
        for it in items:
            if isinstance(it, tuple):
                k, v = it
                if k in seen_blocks:
                    raise UsfParseError(f'duplicate top-level block: {k}')
                seen_blocks.add(k)
                if k == 'freq_table':
                    freq_table = v
                elif k == 'offtable_vibdepth':
                    offtable_vibdepth = v
                elif k == 'state_layout':
                    state_layout = v
                elif k == 'song_end':
                    song_end = v
                elif k == 'init_behavior':
                    init_behavior = v
                elif k == 'master_vol':
                    master_vol = v
                elif k == 'sfx':
                    sfx = v
                elif k == 'arp_programs':
                    arp_programs = v
                elif k == 'pulse_programs':
                    pulse_programs = v
                elif k == 'filter_programs':
                    filter_programs = v
                elif k == 'filter_mod':
                    filter_mod = v
                elif k == 'drum_programs':
                    drum_programs = v
                elif k == 'attack_len':
                    attack_len = v
                elif k == 'attack_wave':
                    attack_wave = v
                elif k == 'wave_arp':
                    wave_arp = v
                elif k == 'pulse_arp':
                    pulse_arp = v
                elif k == 'wave_programs':
                    wave_programs = v
                elif k == 'default_filter':
                    default_filter = v
                elif k == 'default_pulse':
                    default_pulse = v
                elif k == 'dmc_sfx':
                    dmc_sfx = v
                elif k == 'environment':
                    environment = v
                elif k == 'wave_table':
                    wave_table = v
            elif isinstance(it, PsidMeta):
                psid = it
            elif isinstance(it, Params):
                params = it
            elif isinstance(it, InitState):
                init = it
            elif isinstance(it, Instrument):
                instruments.append(it)
            elif isinstance(it, (MusicSubtune, DigiSubtune, SfxSubtune,
                                 DmcSfxSubtune)):
                subtunes.append(it)
        return UsfFile(
            psid=psid, params=params,
            init=init, environment=environment,
            instruments=instruments, subtunes=subtunes,
            freq_table=freq_table, state_layout=state_layout,
            song_end=song_end, init_behavior=init_behavior,
            master_vol=master_vol, sfx=sfx, arp_programs=arp_programs,
            pulse_programs=pulse_programs, filter_programs=filter_programs,
            filter_mod=filter_mod,
            drum_programs=drum_programs, attack_len=attack_len,
            attack_wave=attack_wave, wave_arp=wave_arp, pulse_arp=pulse_arp,
            wave_programs=wave_programs, offtable_vibdepth=offtable_vibdepth,
            wave_table=wave_table,
            default_filter=default_filter, default_pulse=default_pulse,
            dmc_sfx=dmc_sfx)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(text: str) -> UsfFile:
    """Parse a USF source string into a typed `UsfFile`."""
    try:
        tree = _parser().parse(text)
    except LarkError as e:
        raise UsfParseError(str(e)) from None
    return _T().transform(tree)


def parse_file(path: str) -> UsfFile:
    """Parse a `.usf` file. Used by the codegen."""
    with open(path, encoding='utf-8') as f:
        return parse(f.read())
