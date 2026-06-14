"""USF v2 — parser.

Lark-based parser that produces typed AST classes from src.usf.types.
Grammar lives in src/usf/grammar.lark.
"""

from __future__ import annotations

import os

from lark import Lark, Transformer, Token, v_args
from lark.exceptions import LarkError

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitVoice, InitState,
    InitSid, InitSidVoice, InitFilter,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, IncBy2Config, SongEndConfig, InitBehaviorConfig,
    MasterVolConfig, SfxConfig,
    MusicSubtune, DigiSubtune, SfxSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
)


_GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), 'grammar.lark')


class UsfParseError(Exception):
    """Parse error with line/column information."""
    pass


def _load_parser() -> Lark:
    with open(_GRAMMAR_PATH) as f:
        return Lark(f.read(), start='start', parser='lalr', propagate_positions=True)


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
            setattr(v, k, val)
        return v

    def init_inner(self, items):
        # Either an InitVoice (engine-state priming) or InitSid
        # (SID-chip priming). Returned unchanged; init_block sorts.
        return items[0]

    def init_block(self, items):
        voices = [it for it in items if isinstance(it, InitVoice)]
        sids = [it for it in items if isinstance(it, InitSid)]
        if len(sids) > 1:
            raise UsfParseError('init { sid { ... } } can appear at most once')
        return InitState(voices=voices, sid=sids[0] if sids else None)

    # ----- init.sid -----
    def ifilt_lo(self, items):  return ('cutoff_lo', items[0])
    def ifilt_hi(self, items):  return ('cutoff_hi', items[0])
    def ifilt_res(self, items): return ('res_routing', items[0])

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

    def isid_voice(self, items):
        voice_id = int(items[0])
        v = InitSidVoice(id=voice_id)
        for k, val in items[1:]:
            setattr(v, k, val)
        return ('voice', v)

    def init_sid_block(self, items):
        sid = InitSid()
        for k, val in items:
            if k == 'voice':
                sid.voices.append(val)
            else:
                setattr(sid, k, val)
        return sid

    # ----- instruments -----
    def instrument_name(self, items):
        return str(items[0])

    def inst_waveform(self, items):
        return ('waveform', list(items[0]))

    def inst_loop(self, items):
        return ('loop', int(items[0]))

    def inst_wave_freq(self, items):
        return ('wave_freq', [int(x) for x in items])

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

    def subtune_kind(self, items):
        return items[0]

    def subtune_body(self, items):
        return items[0]

    def is_sfx_field(self, items):
        return ('is_sfx', bool(items[0]))

    def music_body(self, items):
        # 'tempo' ':' INT is_sfx_field? params_block? init_block? voice*3
        tempo = int(items[0])
        rest = list(items[1:])
        is_sfx = False
        if rest and isinstance(rest[0], tuple) and rest[0][0] == 'is_sfx':
            is_sfx = rest.pop(0)[1]
        params = None
        init = None
        if rest and isinstance(rest[0], Params):
            params = rest.pop(0)
        if rest and isinstance(rest[0], InitState):
            init = rest.pop(0)
        voices = rest
        return ('music', {'tempo': tempo, 'voices': voices,
                          'params': params, 'init': init,
                          'is_sfx': is_sfx})

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
                is_sfx=body_data.get('is_sfx', False))
        elif kind == 'digi':
            return DigiSubtune(id=sub_id, sample=body_data['sample'])
        else:
            # sfx — body_data is the decomposed SFX record
            return SfxSubtune(id=sub_id, **body_data)

    # ----- voice / orderlist / patterns -----
    def ol_loop(self, items):
        loop_tr = loop_len = None
        for it in items[1:]:
            if isinstance(it, tuple):
                if it[0] == 'tr':
                    loop_tr = it[1]        # ('tr', T) from ol_transpose
                elif it[0] == 'll':
                    loop_len = it[1]       # ('ll', L) from ol_looplen
        return ('loop', (int(items[0]), loop_tr, loop_len))

    def ol_stop(self, _):
        return ('stop', None)

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

    def ol_looplen(self, items):
        return ('ll', int(items[0]))

    def orderlist_entry(self, items):
        # a[*b][+c][^d] → ('entry', pattern_id, transpose, voiceinc, repeats)
        # The bare Token is the pattern id (operand, first); modifier
        # sub-rules arrive as tagged tuples.
        pid = None
        rep, tr, vi = 1, 0, 0
        for it in items:
            if isinstance(it, tuple):
                kind, val = it
                if kind == 'rep':
                    rep = val
                elif kind == 'tr':
                    tr = val
                elif kind == 'vi':
                    vi = val
            else:
                pid = int(it)
        return ('entry', pid, tr, vi, rep)

    def orderlist(self, items):
        # entries followed by optional terminator
        entries = []
        transposes = []
        voiceincs = []
        repeats = []
        loop_to = None
        loop_transpose = None
        loop_length = None
        stop = False
        for it in items:
            kind = it[0]
            if kind == 'entry':
                _, pid, tr, vi, rep = it
                entries.append(pid)
                transposes.append(tr)
                voiceincs.append(vi)
                repeats.append(rep)
            elif kind == 'loop':
                loop_to, loop_transpose, loop_length = it[1]
            elif kind == 'stop':
                stop = True
        # Omit each modifier list when it carries no information (clean
        # round-trip output + backward-compatible default).
        if not any(transposes):
            transposes = []
        if not any(voiceincs):
            voiceincs = []
        if all(r == 1 for r in repeats):
            repeats = []
        return Orderlist(entries=entries, loop_to=loop_to, stop=stop,
                         loop_transpose=loop_transpose,
                         loop_length=loop_length,
                         transposes=transposes, voiceincs=voiceincs,
                         repeats=repeats)

    def pattern_block(self, items):
        # INT INT note_row*
        pat_id = int(items[0])
        length = int(items[1])
        rows = list(items[2:])
        return Pattern(id=pat_id, length=length, rows=rows)

    def voice_block(self, items):
        voice_id = int(items[0])
        orderlist = items[1]
        patterns = list(items[2:])
        return VoiceBlock(id=voice_id, orderlist=orderlist, patterns=patterns)

    # ----- notes + pitches + instrument refs + fx -----
    def pitch_named(self, items):
        # NOTE_NAME like 'C-5' or 'D#3'; octave may be 2 digits (off-table
        # pitches 97..255 — freq_overrun reads, e.g. ghost-march ties).
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

    def fx_named(self, items):
        return f'fx:{items[0]}'

    def fx_glide(self, items):
        return f'glide={int(items[0])}'

    def fx_glide_up(self, items):
        return f'glide_up=${int(items[0]):04X}'

    def fx_glide_down(self, items):
        return f'glide_down=${int(items[0]):04X}'

    def fx_glide_onset(self, items):
        return f'glide_onset={int(items[0])}'

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

    def freq_table_block(self, items):
        # items[0] is a byte_list (= list[int])
        return ('freq_table', items[0])

    def freq_overrun_block(self, items):
        return ('freq_overrun', items[0])

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
        dur = int(items[1])
        idx = 2
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
        drum_programs = {}
        attack_len = []
        attack_wave = []
        wave_arp = []
        pulse_arp = []
        wave_programs = {}
        freq_overrun = []
        for it in items:
            if isinstance(it, tuple):
                k, v = it
                if k == 'freq_table':
                    freq_table = v
                elif k == 'freq_overrun':
                    freq_overrun = v
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
            elif isinstance(it, PsidMeta):
                psid = it
            elif isinstance(it, Params):
                params = it
            elif isinstance(it, InitState):
                init = it
            elif isinstance(it, Instrument):
                instruments.append(it)
            elif isinstance(it, (MusicSubtune, DigiSubtune, SfxSubtune)):
                subtunes.append(it)
        return UsfFile(
            psid=psid, params=params,
            init=init, instruments=instruments, subtunes=subtunes,
            freq_table=freq_table, state_layout=state_layout,
            song_end=song_end, init_behavior=init_behavior,
            master_vol=master_vol, sfx=sfx, arp_programs=arp_programs,
            pulse_programs=pulse_programs, filter_programs=filter_programs,
            drum_programs=drum_programs, attack_len=attack_len,
            attack_wave=attack_wave, wave_arp=wave_arp, pulse_arp=pulse_arp,
            wave_programs=wave_programs, freq_overrun=freq_overrun)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(text: str) -> UsfFile:
    """Parse a USF v2 source string into a typed `UsfFile`."""
    try:
        tree = _parser().parse(text)
    except LarkError as e:
        raise UsfParseError(str(e)) from None
    return _T().transform(tree)


def parse_file(path: str) -> UsfFile:
    """Parse a `.usf` file. Used by the codegen."""
    with open(path, encoding='utf-8') as f:
        return parse(f.read())
