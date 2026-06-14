"""DMC V5 USF-layer round-trip tests.

1. The `pulse_sweep` schema field + the `set_instr` row marker survive
   write -> parse unchanged.
2. The representative member (Katusha) verifies instruction-sequence
   exact THROUGH USF: SID -> extract -> to_usf -> .usf -> parse ->
   from_usf -> V5Model -> composer -> SID reproduces the original
   $D400-$D418 write stream.

Run standalone (`python3 tests/test_dmc_v5_usf.py`) or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))


def test_sweep_env_schema_roundtrip():
    from src.usf.types import (UsfFile, PsidMeta, Params, InitState,
                               Instrument, SweepEnvelope, PwmConfig)
    from src.usf import writer, parser
    insts = [
        Instrument(id=0, adsr=(0x89, 0x9F),
                   pulse_env=SweepEnvelope(start=0x0514, phases=[(0, 0x9001)]),
                   filter_env=SweepEnvelope(start=0xBD12,
                                            phases=[(-252, 0x37)], loop=0)),
        Instrument(id=1, adsr=(8, 5), pwm=PwmConfig(keep_running=True)),
    ]
    u = UsfFile(psid=PsidMeta(title='T'), params=Params(), init=InitState(),
                instruments=insts)
    u2 = parser.parse(writer.write(u))
    assert u2.instruments[0].pulse_env == insts[0].pulse_env
    assert u2.instruments[0].filter_env == insts[0].filter_env
    assert u2.instruments[1].pulse_env is None
    assert u2.instruments[1].pwm.keep_running


def test_set_instr_flag_roundtrip():
    from src.usf.types import (Pattern, NoteRow, Pitch, Orderlist, VoiceBlock,
                               MusicSubtune, UsfFile, PsidMeta, Params,
                               InitState)
    from src.usf import writer, parser
    rows = [NoteRow(pitch=Pitch('C', 5), duration=2,
                    fx_flags=('set_dur=$02', 'set_instr=1')),
            NoteRow(pitch=Pitch.rest(), duration=2,
                    fx_flags=('set_instr=2', 'tie'))]
    vb = VoiceBlock(id=1, orderlist=Orderlist(entries=[0], loop_to=0),
                    patterns=[Pattern(id=0, length=4, rows=rows)])
    sub = MusicSubtune(id=1, tempo=2, voices=[
        vb, VoiceBlock(id=2, orderlist=Orderlist(entries=[0], loop_to=0),
                       patterns=[Pattern(id=0, length=4, rows=rows)]),
        VoiceBlock(id=3, orderlist=Orderlist(entries=[0], loop_to=0),
                   patterns=[Pattern(id=0, length=4, rows=rows)])])
    u = UsfFile(psid=PsidMeta(), params=Params(), init=InitState(),
                subtunes=[sub])
    u2 = parser.parse(writer.write(u))
    r = u2.subtunes[0].voices[0].patterns[0].rows
    assert r[0].fx_flags == ('set_dur=$02', 'set_instr=1')
    assert r[1].fx_flags == ('set_instr=2', 'tie')


def test_katusha_full_through_usf():
    from pipelines.dmc.v5.verify_v5 import verify_v5
    from pipelines.dmc.v5.config import KATUSHA
    r = verify_v5(KATUSHA)
    assert r['ok'], r
    assert r['subtunes'][0]['is_full']
    assert r['subtunes'][0]['play_match'] == r['subtunes'][0]['overlap']


if __name__ == '__main__':
    test_sweep_env_schema_roundtrip()
    print('OK pulse/filter sweep-envelope schema round-trip')
    test_set_instr_flag_roundtrip()
    print('OK set_instr/set_dur flag round-trip')
    test_katusha_full_through_usf()
    print('OK Katusha FULL through USF')
