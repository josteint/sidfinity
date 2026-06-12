"""FCConfig for the STANDARD ("vanilla") Future Composer player.

This is the dominant FC player: ~91% (3673/4024) of HVSC FutureComposer SIDs
share it (tools/engine_fingerprint.py). Migrating it covers the bulk of the FC
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
import hashlib
import struct
from pathlib import Path

from pipelines.future_composer.config import FCConfig


class FCStandardUnsupported(Exception):
    """The SID is not a clean standard-player family member.

    Raised by `fc_standard_config` with a machine-bucketable `reason` so
    batch runs flag oddballs cleanly instead of producing a garbage
    verdict (wrong-shape build → meaningless divergence noise).
    """

    def __init__(self, sid_path: str, reason: str):
        self.sid_path = sid_path
        self.reason = reason
        super().__init__(f'{sid_path}: {reason}')


# SHA1 of the canonical 96-entry freq LO table at load+$564 (the family
# membership probe — 2760/4024 HVSC FC SIDs carry it verbatim). LO only:
# the table is per-tune image DATA and a few members carry edited/zeroed
# HI bytes (Tyranny_for_You_part_6 hi[90]=$00) — content rides in the
# USF either way; the probe only establishes the layout.
_CANONICAL_FREQ_SHA1 = '0c341b7f47605a64e39a3bb7652580865c1444a9'

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
    # ---- family membership + variant hygiene -------------------------
    # Detect-and-flag (FCStandardUnsupported, bucketable reason) instead
    # of building a wrong-shape rebuild whose divergence is pure noise.
    if len(body) < 0x847:                # deepest probed offset ($2046)
        raise FCStandardUnsupported(str(sid_path), 'image too short')
    if hashlib.sha1(body[0x564:0x5C4]).hexdigest() != _CANONICAL_FREQ_SHA1:
        raise FCStandardUnsupported(
            str(sid_path), 'freq-table probe mismatch (not standard layout)')
    init_hdr = struct.unpack('>H', d[0x0A:0x0C])[0]
    play_hdr = struct.unpack('>H', d[0x0C:0x0E])[0]
    # Stock image: load+0 = JMP $2108 (init), load+6 = the inline play
    # routine. Some members' headers point init STRAIGHT at the stock
    # $2108-equivalent, bypassing the JMP — same engine, accepted.
    if (init_hdr not in (0, load, 0x2108 + delta)
            or play_hdr != load + 6):
        raise FCStandardUnsupported(
            str(sid_path), f'non-standard entry shape (init=${init_hdr:04X} '
            f'play=${play_hdr:04X} load=${load:04X})')
    if d[0x12:0x16] != b'\x00\x00\x00\x00':
        raise FCStandardUnsupported(
            str(sid_path), 'CIA-timed (PSID speed bits set)')
    # Static player-variant bytes:
    # $2046 (vibrato-skip JMP operand): $EB = skip writes nothing (Jarre_2);
    #   $DC = stale-tail write (Prato).
    # $1B3F (glide-up hi-write operand): $01 = freq hi (normal); $55 =
    #   mirror-write hack (Entrail). Stored as low 5 bits (mirror-equivalent).
    # Per-frame $D418 value — the $1833 LDA operand ($1F canonical;
    # builds exist with $0F = low-pass bit off, e.g. Colourbar_Designer).
    # The composer already parameterizes this as vol_every_frame.
    if body[0x1833 - _REF_LOAD] != 0xA9:
        raise FCStandardUnsupported(
            str(sid_path),
            f'oddball $1833 vol write (opcode ${body[0x1833 - _REF_LOAD]:02X})')
    vol_frame = body[0x1834 - _REF_LOAD]
    variant = body[0x2046 - _REF_LOAD]
    if variant not in (0xEB, 0xDC):
        raise FCStandardUnsupported(
            str(sid_path),
            f'oddball $2046 build (vibrato-skip operand ${variant:02X})')
    glide_hi = body[0x1B3F - _REF_LOAD]
    arp3 = tuple(body[0x1E86 - _REF_LOAD:0x1E89 - _REF_LOAD])
    # $D416-write variant (the opcode at orig $1C78): STA / NOPed-out /
    # a JSR hook that overrides the value with a constant.
    d416_mode, d416_const = 'normal', 0
    op_i = 0x1C78 - _REF_LOAD
    op = body[op_i]
    if op == 0xEA:
        d416_mode = 'none'
    elif op == 0x20:
        tgt = (body[op_i + 1] | (body[op_i + 2] << 8)) - load
        if (0 <= tgt < len(body) - 6 and body[tgt] == 0xA9
                and body[tgt + 2:tgt + 5] == bytes((0x8D, 0x16, 0xD4))
                and body[tgt + 5] == 0x60):
            d416_mode, d416_const = 'const', body[tgt + 1]
        else:
            raise FCStandardUnsupported(
                str(sid_path),
                f'unrecognized $1C78 hook (JSR ${tgt + load:04X})')
    elif op != 0x8D:
        raise FCStandardUnsupported(
            str(sid_path), f'oddball $1C78 opcode ${op:02X}')
    # Sequence-table provenance. The stock player reads the static 6-byte
    # record at $1EA1 and has NO subtune indexing. Wrapper inits (e.g.
    # Intense_Intro: copy a per-subtune record from a side table into the
    # slot, then JMP into the stock init) leave the STATIC slot stale —
    # in-image-looking but wrong. Ground truth: run the PSID init in py65
    # once and compare the post-init slot against the static record;
    # multi-song members need a wrapper by construction.
    songs = struct.unpack('>H', d[0x0E:0x10])[0]
    static_rec = bytes(body[0x1EA1 - _REF_LOAD:0x1EA1 - _REF_LOAD + 6])
    slot_stale = songs > 1
    if not slot_stale:
        # only bother with py65 when the init isn't the stock entry
        init_tgt = body[1] | (body[2] << 8)
        if init_tgt != 0x2108 + delta:
            from pipelines.future_composer.engine_model import (
                _run_init_in_py65)
            mem = _run_init_in_py65(str(p), subtune=0)
            slot = bytes(mem[0x1EA1 + delta:0x1EA1 + delta + 6])
            slot_stale = slot != static_rec
    layout = {}
    if slot_stale:
        layout = dict(subtune_layout='runtime_slot',
                      runtime_seq_ptrs_addr=0x1EA1 + delta,
                      runtime_speed_addr=0x211D + delta)
    return _dc.replace(
        FC_STANDARD,
        name=f'fc_standard:{p.stem}',
        sid_path=str(sid_path),
        std_vibrato_stale_tail=(variant == 0xDC),
        std_glide_hi_reg=glide_hi & 0x1F,
        std_arp3_init=arp3,
        std_d416_mode=d416_mode,
        std_d416_const=d416_const,
        vol_every_frame=vol_frame,
        **layout,
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
