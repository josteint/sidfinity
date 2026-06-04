"""Hawkeye FCConfig — addresses verified by RE_NOTES.md + disassembly.s.

Run this module as a script to dump the decoded model:
    python3 pipelines/future_composer/hawkeye/config.py
"""
from pipelines.future_composer.config import FCConfig


HAWKEYE = FCConfig(
    name='hawkeye',
    sid_path='hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid',

    # Verified by `python3 pipelines/future_composer/hawkeye/data_dump.py`
    freq_lo_addr=0x8337,
    freq_hi_addr=0x8396,
    pattern_ptr_addr=0x8409,
    instr_records_addr=0x860C,
    per_subtune_speed_addr=0x83F5,

    subtune_layout='smc_template_with_sfx',
    per_subtune_smc_addr=0x83FC,
    per_subtune_mode_addr=0x7AFF,
    template_base_hi=0x7B,

    # Hawkeye: 6 music subtunes + 6 SFX; SFX records at pages
    # $92, $94, $96, $98, $9A, $9C (stride = 2 pages)
    music_subtune_count=6,
    sfx_page_base=0x92,
    sfx_page_stride=2,

    # Table sizes
    freq_table_entries=96,
    instr_count=16,
    max_patterns=64,
)


if __name__ == '__main__':
    from pipelines.future_composer.engine_model import extract, print_song
    print_song(extract(HAWKEYE))
