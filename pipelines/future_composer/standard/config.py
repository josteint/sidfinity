"""FCConfig for the STANDARD ("vanilla") Future Composer player.

This is the dominant FC player: ~91% (3673/4024) of HVSC FutureComposer SIDs
share it (tools/fc_fingerprint.py). Migrating it covers the bulk of the FC
catalogue. Address map from disassembly.s (representative Carter/Jarre_2 @
load $1800).

RELOCATION: the vanilla player's load image has a FIXED internal layout —
every engine table sits at a constant offset from the load address (verified
empirically: 2760/4024 HVSC FC SIDs carry the canonical 96-entry freq table
at exactly load+$564; 2639 of those share Jarre_2's full shape init=load,
play=load+6, vblank). `fc_standard_config(sid_path)` derives a per-SID config
by shifting every address field by (load - $1800).
"""
import dataclasses as _dc
import struct
from pathlib import Path

from pipelines.future_composer.config import FCConfig

# Address fields that live inside the original load image and shift with it.
_RELOC_FIELDS = (
    'freq_lo_addr', 'freq_hi_addr', 'pattern_ptr_addr', 'instr_records_addr',
    'per_subtune_speed_addr', 'seq_table_addr', 'pulsetabel_addr',
    'wavearp_addr', 'std_wave_ptr_addr', 'filterbytes_addr',
)
_REF_LOAD = 0x1800                  # Jarre_2's load address (the address map base)


def fc_standard_config(sid_path: str, root: str | None = None) -> FCConfig:
    """Relocation-aware FC_STANDARD for any standard-player family member.

    Reads the PSID load address and shifts every in-image address field by
    (load - $1800). Everything else (formats, write model, init style) is
    the player's behavior, identical across the family.
    """
    p = Path(root) / sid_path if root else Path(sid_path)
    d = p.read_bytes()
    hdr = struct.unpack('>H', d[6:8])[0]
    load = struct.unpack('<H', d[hdr:hdr + 2])[0]
    delta = load - _REF_LOAD
    shifted = {f: getattr(FC_STANDARD, f) + delta for f in _RELOC_FIELDS}
    body = d[hdr + 2:]
    # Static player-variant bytes:
    # $2046 (vibrato-skip JMP operand): $EB = skip writes nothing (Jarre_2);
    #   $DC = stale-tail write (Prato).
    # $1B3F (glide-up hi-write operand): $01 = freq hi (normal); $55 =
    #   mirror-write hack (Entrail). Stored as low 5 bits (mirror-equivalent).
    variant = body[0x2046 - _REF_LOAD]
    glide_hi = body[0x1B3F - _REF_LOAD]
    return _dc.replace(
        FC_STANDARD,
        name=f'fc_standard:{p.stem}',
        sid_path=str(sid_path),
        std_vibrato_stale_tail=(variant == 0xDC),
        std_glide_hi_reg=glide_hi & 0x1F,
        **shifted,
    )

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
    init_style='universal_reset',   # pure trichotomy: orig init is a clean
                                    # zeroing with NO priming (end state = all
                                    # 0 + host $D418=$0F = the defaults)
    load_addr=0x1000,               # our own engine below the $1D64 data

    pulsetabel_addr=0x1E95,
    wavearp_addr=0x1E32,            # $40 effect: 4-byte ctrl-cycle table ($1E32)
    wavearpwait=3,                  # onset delay (orig $1BEC CMP #$03)
    filterbytes_addr=0x1E89,        # filter: ONE 12-byte 6-band envelope
    filter_prog_format='standard',
    pulse_prog_format='standard',
    instr_format='standard',
    pattern_format='standard',
    noise_tick_style='standard',    # $80 effect: noise-click attack ($1CE3)
    std_wave_ptr_addr=0x1E3E,
    vol_every_frame=0x1F,
    fm2_cleanup_writes_d418=False,
    voice_loop_layout='standard',
    nextvoice_write_order=(2, 3, 1, 0, 4),  # PWlo,PWhi,freqhi,freqlo,ctrl (held-frame order)

    freq_table_entries=96,
    instr_count=10,
    max_patterns=64,
)
