"""FCConfig for the STANDARD ("vanilla") Future Composer player.

This is the dominant FC player: ~91% (3673/4024) of HVSC FutureComposer SIDs
share it (tools/fc_fingerprint.py). Migrating it covers the bulk of the FC
catalogue. Address map from disassembly.s (representative Carter/Jarre_2 @
load $1800). Aux effect-program tables (arp/pulse/filter/drum/...) are left at
0 for the first pass and added as write-log divergence reveals them.
"""
from pipelines.future_composer.config import FCConfig

FC_STANDARD = FCConfig(
    name='fc_standard',
    sid_path='hvsc84/MUSICIANS/C/Carter/Jarre_2.sid',

    # core data tables (disasm address map, load $1800)
    freq_lo_addr=0x1D64,
    freq_hi_addr=0x1DC4,            # 96-entry canonical FC table
    pattern_ptr_addr=0x1EA7,        # 2-byte interleaved, indexed pattern*2
    instr_records_addr=0x2188,      # 8-byte records, id<<3
    per_subtune_speed_addr=0x211D,  # speed threshold ($211D)

    subtune_layout='flat_seq_table',
    seq_table_addr=0x1EA1,          # 6-byte record: lo*3 ($1EA1) + hi*3 ($1EA4)

    emit_data_from_usf=True,
    contiguous_data_layout=True,
    load_addr=0x1000,               # our own engine below the $1D64 data

    pulsetabel_addr=0x1E95,
    pulse_prog_format='standard',
    instr_format='standard',
    pattern_format='standard',
    std_wave_ptr_addr=0x1E3E,
    vol_every_frame=0x1F,
    fm2_cleanup_writes_d418=False,
    voice_loop_layout='standard',
    nextvoice_write_order=(2, 3, 1, 0, 4),  # PWlo,PWhi,freqhi,freqlo,ctrl (held-frame order)

    freq_table_entries=96,
    instr_count=10,
    max_patterns=64,
)
