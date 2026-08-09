"""Per-SID engine-data dump for the Companion/Jay_Derrett family.

Reports everything the scanners currently find — play loop entry +
proc_note + per-voice orderlist pointer slots + freq tables + $E0
sub-jump table + instrument-base table — for each of the 25 SIDs
the scanner classifies. Writes a markdown table to stdout.

Run:
    PYTHONPATH=. python3 pipelines/companion/jay_derrett/dump_engine_data.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))))

from pipelines.companion.jay_derrett.extract.engine_model import (
    load_state_from_sid,
    find_freq_tables,
    find_sub_jump_table,
    find_instrument_base_table,
)
from pipelines.companion.jay_derrett.extract.orderlist import (
    decode_voice_orderlist, Note, CmdGateOff, CmdSkip, CmdSetDuration,
    CmdSetTempo, CmdSetVol, CmdSetInstrument, CmdPatternJump,
)


CANDIDATES = (
    [f'hvsc85/MUSICIANS/D/Derrett_Jay/{n}.sid' for n in [
        'Counterforce', 'Death_or_Glory', 'Destruct', 'Discovery',
        'Dracula', 'Equalizer', 'Jetboys', 'Lifeforce', 'Mandroid',
        'Ninja_Hamster', 'Osmium', 'Road_Warrior',
        'Spindizzy_USA_Version', 'Sqij', 'Stratton', 'Thundercross',
        'Traxxion', 'Trigger_Happy', 'Vengeance', 'ZIP',
    ]]
    + [f'hvsc85/MUSICIANS/C/Clever_Music/{n}.sid' for n in [
        'Blade_Runner', 'Shao-Lins_Road', 'Soundwave_Tubular_Bells',
        'Space_Doubt',
    ]]
    + ['hvsc85/MUSICIANS/R/Raeburn_Gavin/Gun_Runner.sid']
)


def _fmt(x: int | None) -> str:
    return f'${x:04X}' if x is not None else '----'


def main() -> int:
    print('| SID | init | play | loop | proc | freq_lo | freq_hi | $E0 | inst_base | zp | V1 ptr | V2 ptr | V3 ptr |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    n_freq = n_e0 = n_inst = 0
    n_total = 0
    for path in CANDIDATES:
        n_total += 1
        name = path.split('/')[-1].replace('.sid', '')
        try:
            s = load_state_from_sid(path)
        except Exception as e:
            print(f'| **{name}** | _scan failed: {type(e).__name__}_ | | | | | | | | | | | |')
            continue
        mem = bytearray(s.post_init_mem)
        ft = find_freq_tables(mem, s.play_loop_entry)
        e0 = find_sub_jump_table(mem, s.proc_note_addr, s.voices[0].zp)
        ib = find_instrument_base_table(mem, s.play_loop_entry)
        if ft is not None: n_freq += 1
        if e0 is not None: n_e0 += 1
        if ib is not None: n_inst += 1
        ft_lo, ft_hi = ft if ft else (None, None)
        zp = s.voices[0].zp
        print(
            f'| {name} | {_fmt(s.init_addr)} | {_fmt(s.play_addr)} '
            f'| {_fmt(s.play_loop_entry)} | {_fmt(s.proc_note_addr)} '
            f'| {_fmt(ft_lo)} | {_fmt(ft_hi)} | {_fmt(e0)} '
            f'| {_fmt(ib)} | ${zp:02X} '
            f'| {_fmt(s.voices[0].initial_ptr)} '
            f'| {_fmt(s.voices[1].initial_ptr)} '
            f'| {_fmt(s.voices[2].initial_ptr)} |'
        )
    print()
    print(f'Coverage:  freq_tables {n_freq}/{n_total}  '
          f'$E0 sub-jump {n_e0}/{n_total}  '
          f'inst-base {n_inst}/{n_total}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
