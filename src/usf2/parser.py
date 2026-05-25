"""USF v2 — parser.

Lark-based parser that produces typed AST classes from src.usf2.types.
Grammar lives in src/usf2/grammar.lark.
"""

from __future__ import annotations

import os

from lark import Lark, Transformer, Token, v_args
from lark.exceptions import LarkError

from src.usf2.types import (
    UsfFile, PsidMeta, Params, InitVoice, InitState,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
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

    # ----- version + engine -----
    def version_decl(self, items):
        return ('version', int(items[0]))

    def engine_decl(self, items):
        return ('engine', str(items[0]))

    # ----- psid -----
    def psid_title(self, items):
        return ('title', str(items[0])[1:-1])

    def psid_author(self, items):
        return ('author', str(items[0])[1:-1])

    def psid_released(self, items):
        return ('released', str(items[0])[1:-1])

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

    def init_block(self, items):
        return InitState(voices=list(items))

    # ----- instruments -----
    def instrument_name(self, items):
        return str(items[0])

    def inst_waveform(self, items):
        return ('waveform', list(items[0]))

    def inst_loop(self, items):
        return ('loop', int(items[0]))

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

    def arp_args(self, items):
        return ArpConfig(**dict(items))

    def inst_arp(self, items):
        return ('arp', items[0])

    def vib_scale(self, items):
        return ('scale', int(items[0]))

    def vib_args(self, items):
        return VibratoConfig(**dict(items))

    def inst_vibrato(self, items):
        return ('vibrato', items[0])

    def env_gate_off_delta(self, items):
        return ('gate_off_delta', int(items[0]))

    def env_adsr_zero_delta(self, items):
        return ('adsr_zero_delta', int(items[0]))

    def env_args(self, items):
        return EnvelopeConfig(**dict(items))

    def inst_envelope(self, items):
        return ('envelope', items[0])

    def inst_fx_freq_slide(self, _):
        return 'freq_slide'

    def inst_fx_inc_by2(self, _):
        return 'inc_by2'

    def inst_fx(self, items):
        # items is a list of flag-name strings
        flags = {'freq_slide': False, 'inc_by2': False}
        for name in items:
            flags[name] = True
        return ('_fx_flags', flags)

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
        # Pull fx flags out of the synthetic '_fx_flags' key before the
        # generic setattr loop, since the dataclass has individual bools.
        fx_flags = fields.pop('_fx_flags', None)
        if fx_flags is not None:
            for fname, fval in fx_flags.items():
                setattr(inst, fname, fval)
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

    def music_body(self, items):
        # 'tempo' ':' INT params_block? voice voice voice
        tempo = int(items[0])
        rest = list(items[1:])
        params = None
        if rest and isinstance(rest[0], Params):
            params = rest.pop(0)
        voices = rest
        return ('music', {'tempo': tempo, 'voices': voices, 'params': params})

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
                params=body_data.get('params'))
        elif kind == 'digi':
            return DigiSubtune(id=sub_id, sample=body_data['sample'])
        else:
            # sfx — body_data is the decomposed SFX record
            return SfxSubtune(id=sub_id, **body_data)

    # ----- voice / orderlist / patterns -----
    def ol_loop(self, items):
        return ('loop', int(items[0]))

    def ol_stop(self, _):
        return ('stop', None)

    def orderlist_terminator(self, items):
        return items[0]

    def orderlist_entry(self, items):
        return int(items[0])

    def orderlist(self, items):
        # entries followed by optional terminator
        entries = []
        loop_to = None
        stop = False
        for it in items:
            if isinstance(it, int):
                entries.append(it)
            elif isinstance(it, tuple):
                kind, val = it
                if kind == 'loop':
                    loop_to = val
                elif kind == 'stop':
                    stop = True
        return Orderlist(entries=entries, loop_to=loop_to, stop=stop)

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
        # NOTE_NAME like 'C-5' or 'D#3'
        tok = str(items[0])
        letter = tok[0]
        sep = tok[1]
        octave = int(tok[2])
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

    def fx_named(self, items):
        return f'fx:{items[0]}'

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
        version = None
        engine = None
        psid = None
        params = None
        init = None
        instruments = []
        subtunes = []
        for it in items:
            if isinstance(it, tuple):
                k, v = it
                if k == 'version':
                    version = v
                elif k == 'engine':
                    engine = v
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
            version=version, engine=engine, psid=psid, params=params,
            init=init, instruments=instruments, subtunes=subtunes)


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
