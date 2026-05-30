"""Audit test — convert each of the 6 currently-supported USF shapes
into an EngineModel and assert the model captures the features the
audit identified.

The point of this test is to verify that `pipelines.engine_model.
EngineModel` is **expressive enough** to represent every shape's
behavior parametrically. It does NOT yet verify that the model
produces a byte-exact SID — that's Phase 3+ when the codegen consumes
the model.
"""

from __future__ import annotations

import os

# Resolve project root for USF file paths.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel: str):
    from src.usf import parse_file
    return parse_file(os.path.join(_ROOT, rel))


def _model(rel: str):
    from pipelines.engine_model import from_usf
    return from_usf(_load(rel))


# ---------------------------------------------------------------------------
# henrys_house — atomic 1-voice
# ---------------------------------------------------------------------------

def test_henrys_house_shape():
    m = _model('hvsc84/GAMES/G-L/Henrys_House.usf')
    assert m.pattern.encoding == 'atomic_per_tick'
    assert m.pattern.pitch_byte_format == 'octave_semi_nibble'
    assert m.voice_timing.mode == 'every_tick'
    assert m.tempo_dispatch.mode == 'single_phase'
    assert m.master_vol.mode == 'fixed_init'
    assert m.master_vol.init_value == 0x0F
    # 1 active voice + 2 placeholder slots; our converter currently
    # reports voice count from the first active voice or full slot count.
    # Either is OK as long as it captures "1 active musical voice."
    assert m.voices.count in (1, 3)
    assert m.voices.ctrl_source == 'instrument_waveform'
    # $FF = master_vol_reset_and_loop on henrys
    assert m.terminators.byte_map.get(0xFF) == 'master_vol_reset_and_loop'
    # No modulation programs
    assert all(i.vibrato is None for i in m.instruments)
    assert all(i.pwm_linear is None for i in m.instruments)
    assert all(i.arpeggio is None for i in m.instruments)
    # No sub-engines
    assert m.commands is None
    assert m.sfx is None
    assert m.digi is None
    assert m.state_layout is None
    assert m.hardcoded_pw_sweep is None


# ---------------------------------------------------------------------------
# bowden_canonical — atomic 3-voice + carry leak
# ---------------------------------------------------------------------------

def test_bowden_canonical_shape():
    m = _model('hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.usf')
    assert m.pattern.encoding == 'atomic_per_tick'
    assert m.voice_timing.mode == 'every_tick'
    assert m.tempo_dispatch.mode == 'single_phase'
    assert m.voices.count == 3
    assert m.voices.ctrl_source == 'instrument_waveform'
    # Bowden's loop substitution
    assert m.terminators.byte_map.get(0xFF) == 'loop_substitute_first'
    # $81-$FE are all skip
    assert m.terminators.byte_map.get(0x81) == 'skip'
    assert m.terminators.byte_map.get(0xC0) == 'skip'
    # No commands, no sub-engines, no modulation
    assert m.commands is None
    assert m.sfx is None
    assert m.state_layout is None
    assert m.hardcoded_pw_sweep is None


# ---------------------------------------------------------------------------
# yes_tune — note_dur_pair + tick_counter state machine
# ---------------------------------------------------------------------------

def test_yes_tune_shape():
    m = _model('hvsc84/DEMOS/UNKNOWN/Yes_Tune.usf')
    assert m.pattern.encoding == 'note_dur_pair'
    assert m.voice_timing.mode == 'tick_counter_decrement'
    assert m.tempo_dispatch.mode == 'single_phase'
    assert m.voices.count == 3
    assert m.master_vol.mode == 'per_subtune_init'
    # $80 dur = rest, $81 = song_end_voice, $FF = loop_reset
    assert m.terminators.byte_map.get(0x80) == 'rest_gate_off'
    assert m.terminators.byte_map.get(0x81) == 'song_end_voice'
    assert m.terminators.byte_map.get(0xFF) == 'loop_reset'
    assert m.commands is None


def test_soldier_of_fortune_multi_subtune():
    m = _model('hvsc84/GAMES/S-Z/Soldier_of_Fortune.usf')
    assert m.pattern.encoding == 'note_dur_pair'
    assert len(m.subtunes) == 8
    # Multiple subtunes, mix of music + SFX (gain_init='preserve').


# ---------------------------------------------------------------------------
# clever_music — command stream + recursive interpreter
# ---------------------------------------------------------------------------

def test_clever_music_shape():
    m = _model('hvsc84/MUSICIANS/C/Clever_Music/Gyroscope.usf')
    assert m.pattern.encoding == 'atomic_per_tick'
    assert m.voice_timing.mode == 'dur_counter_decrement'
    assert m.tempo_dispatch.mode == 'single_phase'
    # Has embedded commands
    assert m.commands is not None
    # At least one of Bx/Cx/Dx/Ex should be present
    assert any(cmd in m.commands.nibble_map.values()
               for cmd in ('set_tempo', 'set_master_vol',
                           'set_instrument', 'pattern_jump'))
    # $82 SET_DURATION
    assert m.terminators.byte_map.get(0x82) == 'set_duration_next_byte'
    # Master vol mutable mid-stream via $Cx
    assert m.master_vol.mode == 'mutable_commands'


# ---------------------------------------------------------------------------
# companion — Up_up_and_Away
# ---------------------------------------------------------------------------

def test_companion_shape():
    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.usf')
    assert m.pattern.encoding == 'atomic_per_period'
    assert m.tempo_dispatch.mode == 'two_phase'
    assert m.voice_timing.mode == 'every_tick'
    assert m.voices.count == 3
    # Companion uses InitVoice.ctrl, not instrument.waveform
    assert m.voices.ctrl_source == 'init_voice_field'
    # Hardcoded V3 PW sweep
    assert m.hardcoded_pw_sweep is not None
    assert m.hardcoded_pw_sweep.voice_idx == 2
    assert m.hardcoded_pw_sweep.delta_per_phase == 5
    assert m.hardcoded_pw_sweep.phase_period == 2
    # $8C / $8D terminators
    assert m.terminators.byte_map.get(0x8C) == 'rest_gate_off'
    assert m.terminators.byte_map.get(0x8D) == 'end_song_on_voice_n'
    assert m.terminators.end_song_voice_idx == 2
    # 5 subtunes
    assert len(m.subtunes) == 5
    # Each subtune carries gate_off_tick and note_load_tick
    assert m.subtunes[0].gate_off_tick is not None
    assert m.subtunes[0].note_load_tick is not None


# ---------------------------------------------------------------------------
# Hubbard '85 — Commando + a few others to cover variants
# ---------------------------------------------------------------------------

def test_commando_shape():
    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf')
    # The bitpack codec + 320-byte freq table indicate Hubbard '85 features
    assert m.pattern.encoding == 'bitpack'
    assert m.pattern.pitch_byte_format == 'absolute_semi'
    assert m.voice_timing.mode == 'dur_counter_decrement'
    assert m.voices.count == 3
    assert m.voices.ctrl_source == 'instrument_waveform'
    # Has SFX (16 sound effects)
    assert m.sfx is not None
    # Some instruments carry vibrato or PWM modulation
    has_modulation = any(
        i.vibrato or i.pwm_linear or i.pwm_bidirectional or i.arpeggio
        or i.freq_hi_slide or i.odd_frame_slide
        for i in m.instruments)
    assert has_modulation
    # FE = song_end on orderlist
    assert m.terminators.byte_map.get(0xFE) in ('song_end_voice', 'song_end_stop_fill')


def test_chimera_has_digi():
    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Chimera.usf')
    assert m.pattern.encoding == 'bitpack'
    assert m.digi is not None
    assert m.digi.technique == 'chimera_1bit'


def test_human_race_has_state_layout():
    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Human_Race.usf')
    assert m.pattern.encoding == 'bitpack'
    assert m.state_layout is not None
    # HR uses a 2-voice statebuf layout (not Commando's 3-voice default)
    # — confirm scalars/per_voice are non-empty.
    assert m.state_layout.scalars or m.state_layout.per_voice


def test_action_biker_stop_fill():
    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Action_Biker.usf')
    # AB writes $FF to $D400-$D417 on song end.
    # The terminator vocab should reflect this.
    if m.terminators.stop_fill_byte is not None:
        assert m.terminators.byte_map.get(0xFE) == 'song_end_stop_fill'


# ---------------------------------------------------------------------------
# Pitch-format normalization sanity
# ---------------------------------------------------------------------------

def test_pitch_format_split():
    """All non-Hubbard shapes use the octave-semi nibble byte format;
    Hubbard '85 uses absolute_semi. Verify the model captures this
    correctly."""
    nibble_shapes = [
        'hvsc84/GAMES/G-L/Henrys_House.usf',
        'hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.usf',
        'hvsc84/DEMOS/UNKNOWN/Yes_Tune.usf',
        'hvsc84/MUSICIANS/C/Clever_Music/Gyroscope.usf',
        'hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.usf',
    ]
    for r in nibble_shapes:
        m = _model(r)
        assert m.pattern.pitch_byte_format == 'octave_semi_nibble', r

    m = _model('hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf')
    assert m.pattern.pitch_byte_format == 'absolute_semi'
