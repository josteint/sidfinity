"""FC family v0 composer — binary-patch from USF.

Pragmatic v0: read the HVSC original SID, overwrite the data sections
the USF can reconstruct (freq table, instruments, per-subtune speed)
in the SID's loaded memory image, re-wrap as PSID.

What this proves: the USF preserves those fields losslessly. If the
md5 of the rebuilt SID matches the HVSC original, the schema round-
trips those fields without loss.

What this does NOT do (deferred to a future composer iteration):
  - Compose 6502 asm from scratch
  - Re-emit variable-length sequence / pattern byte streams (they
    carry verbatim from the original — round-trip not tested for
    those bytes)
  - Reconstruct seqtabel (the per-subtune sequence pointers depend
    on the layout of the variable-length streams)
  - Re-emit voiceinc (lost in USF v0)

The FCConfig parameter supplies the address map — the binary-patch
composer needs to know WHERE to overwrite. A real asm composer
wouldn't need this; it'd generate addresses from scratch.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

from src.usf import UsfFile, parse
from pipelines.future_composer.config import FCConfig


def _load_sid_psid(sid_bytes: bytes) -> tuple[int, int, int, int, int, bytes,
                                                bool]:
    """Return (header_len, load_addr, init_addr, play_addr, n_songs,
    code_bytes, has_inline_load_addr).

    code_bytes is the data after the PSID header WITH the inline load
    address stripped (when present). `has_inline_load_addr` records
    whether the original used the inline form so we can rebuild it
    the same way.
    """
    assert sid_bytes[:4] == b'PSID', f'expected PSID magic'
    hl = struct.unpack('>H', sid_bytes[6:8])[0]
    la = struct.unpack('>H', sid_bytes[8:10])[0]
    init = struct.unpack('>H', sid_bytes[10:12])[0]
    play = struct.unpack('>H', sid_bytes[12:14])[0]
    n_songs = struct.unpack('>H', sid_bytes[14:16])[0]
    code = sid_bytes[hl:]
    has_inline = (la == 0)
    if has_inline:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return hl, la, init, play, n_songs, code, has_inline


def _apply_freq_table(mem: bytearray, cfg: FCConfig,
                      usf: UsfFile) -> None:
    """Overwrite freq table region with USF-decoded values.

    USF freq_table is 192 bytes lo,hi-interleaved (padded with zeros
    past the tune's actual entry count). FC stores them as separate
    lo and hi arrays at distinct addresses.
    """
    if not usf.freq_table:
        return
    for i in range(cfg.freq_table_entries):
        lo = usf.freq_table[i * 2] if i * 2 < len(usf.freq_table) else 0
        hi = usf.freq_table[i * 2 + 1] if i * 2 + 1 < len(usf.freq_table) else 0
        mem[cfg.freq_lo_addr + i] = lo
        mem[cfg.freq_hi_addr + i] = hi


def _apply_instruments(mem: bytearray, cfg: FCConfig,
                       usf: UsfFile) -> None:
    """Overwrite the 8-byte-per-instrument region with USF values.

    USF instruments are 1-based; engine_model.py emits id=raw_index+1.
    So USF inst id N corresponds to engine slot (N-1).

    USF skips all-zero instruments (typically inst 0). Slots not
    present in USF stay at whatever the original SID had (which is
    fine — the original engine code initializes them to zero).
    """
    from pipelines.future_composer.to_usf import fx_bytes_from_inst
    for inst in usf.instruments:
        slot = inst.id - 1
        if slot < 0 or slot >= cfg.instr_count:
            continue
        base = cfg.instr_records_addr + slot * 8
        pulse_hi = inst.waveform[0] if inst.waveform else 0
        ctrl     = inst.waveform[1] if len(inst.waveform) > 1 else 0
        fil_count, fx1, fx2, fx3 = fx_bytes_from_inst(inst)
        mem[base + 0] = pulse_hi
        mem[base + 1] = ctrl
        mem[base + 2] = inst.adsr[0]
        mem[base + 3] = inst.adsr[1]
        mem[base + 4] = fil_count
        mem[base + 5] = fx1
        mem[base + 6] = fx2
        mem[base + 7] = fx3


def _apply_per_subtune_speed(mem: bytearray, cfg: FCConfig,
                              usf: UsfFile) -> None:
    """Overwrite the per-subtune speed bytes from USF subtune.tempo.

    FC engine: speedbyte = tempo - 1 (engine counts down then reloads).
    USF subtune ids are 1-based; engine indices are 0-based.

    Layout-dependent slot count:
      `flat_seqtabel`: one byte per subtune; writes 0..n-1.
      `smc_template_with_sfx`: per_subtune_speed table is only
        music_subtune_count+1 bytes (one per music sub + one shared
        SFX-default at the slot the dispatcher forces via `LDX
        #music_subtune_count`). Writing past that overflows into the
        adjacent SMC template region. SFX subtunes all share the
        single SFX-default slot.
    """
    from src.usf.types import MusicSubtune
    if cfg.subtune_layout == 'flat_seqtabel':
        for sub in usf.subtunes:
            if not isinstance(sub, MusicSubtune):
                continue
            slot = sub.id - 1
            mem[cfg.per_subtune_speed_addr + slot] = (sub.tempo - 1) & 0xFF
    elif cfg.subtune_layout == 'smc_template_with_sfx':
        music_count = cfg.music_subtune_count
        for sub in usf.subtunes:
            if not isinstance(sub, MusicSubtune):
                continue
            slot = sub.id - 1
            if sub.is_sfx:
                # All SFX subtunes share the forced-X SFX-default slot
                mem[cfg.per_subtune_speed_addr + music_count] = (
                    sub.tempo - 1) & 0xFF
            elif slot < music_count:
                mem[cfg.per_subtune_speed_addr + slot] = (
                    sub.tempo - 1) & 0xFF


def _rewrap_psid(orig: bytes, hl: int, code: bytes,
                 has_inline_load: bool, load_addr: int) -> bytes:
    """Stitch new code back into a PSID file using the original header."""
    if has_inline_load:
        new_code = load_addr.to_bytes(2, 'little') + bytes(code)
    else:
        new_code = bytes(code)
    return orig[:hl] + new_code


def build_from_usf(usf: UsfFile, cfg: FCConfig,
                   root: str | None = None) -> bytes:
    """Build a SID from USF + FCConfig (which supplies the address map).

    Returns the new SID bytes. The data sections at the FCConfig
    addresses are overwritten with USF-decoded values; everything else
    (the engine code itself, the sequence/pattern byte streams, the
    seqtabel pointers) carries verbatim from the original.
    """
    if root is None:
        root = str(Path(__file__).resolve().parents[2])
    sid_path = str(Path(root) / cfg.sid_path)

    with open(sid_path, 'rb') as f:
        orig = f.read()

    hl, la, _init, _play, _n_songs, code, has_inline = _load_sid_psid(orig)
    mem = bytearray(65536)
    mem[la:la + len(code)] = code

    _apply_freq_table(mem, cfg, usf)
    _apply_instruments(mem, cfg, usf)
    _apply_per_subtune_speed(mem, cfg, usf)

    new_code = bytes(mem[la:la + len(code)])
    return _rewrap_psid(orig, hl, new_code, has_inline, la)


def build_canary(cfg: FCConfig, usf_path: str | None = None,
                 root: str | None = None) -> tuple[bytes, str]:
    """Build a canary SID from its USF. Returns (sid_bytes, usf_path)."""
    if root is None:
        root = str(Path(__file__).resolve().parents[2])
    if usf_path is None:
        usf_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(usf_path) as f:
        usf = parse(f.read())
    return build_from_usf(usf, cfg, root=root), usf_path


def verify_byte_exact(cfg: FCConfig, root: str | None = None) -> dict:
    """Build canary from USF and compare md5 to the HVSC original.

    Returns a dict with verdict + diagnostic info on mismatch (first
    differing offsets, byte counts in each FCConfig data region).
    """
    if root is None:
        root = str(Path(__file__).resolve().parents[2])
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()

    rebuilt, usf_path = build_canary(cfg, root=root)

    md5_orig = hashlib.md5(orig).hexdigest()
    md5_new = hashlib.md5(rebuilt).hexdigest()
    if md5_orig == md5_new:
        return {'ok': True, 'md5': md5_orig, 'size': len(orig)}

    # Diagnostic: where do they differ?
    diffs = []
    for i in range(min(len(orig), len(rebuilt))):
        if orig[i] != rebuilt[i]:
            diffs.append(i)
            if len(diffs) >= 16:
                break
    return {
        'ok': False,
        'md5_orig': md5_orig,
        'md5_new': md5_new,
        'size_orig': len(orig),
        'size_new': len(rebuilt),
        'first_diffs': diffs,
        'sample': [
            (i, orig[i], rebuilt[i]) for i in diffs[:8]
        ],
    }
