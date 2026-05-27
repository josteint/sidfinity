"""Byte-region rebuilder for Sample Music from I. Karate.

Architectural pattern from pipelines/confuzion: emit the player engine
verbatim from the original binary, regenerate data tables from extracted
USF data. The PSID header is cloned (title/author/load/init/play) and
the body is reconstructed region-by-region.

Run:
    python3 pipelines/sample_music_i_karate/build_byte_perfect.py
    python3 src/writelog_grade.py \\
        hvsc84/MUSICIANS/H/Hubbard_Rob/Sample_Music_from_I_Karate.sid \\
        pipelines/sample_music_i_karate/build/sample_music_i_karate_bp.sid
"""
from __future__ import annotations

import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

SID_PATH = os.path.join(
    ROOT, 'hvsc84', 'MUSICIANS', 'H',
    'Hubbard_Rob', 'Sample_Music_from_I_Karate.sid',
)
OUT_PATH = os.path.join(
    ROOT, 'pipelines', 'sample_music_i_karate', 'build',
    'sample_music_i_karate_bp.sid',
)


def load_psid(path):
    with open(path, 'rb') as f:
        raw = f.read()
    data_off = struct.unpack('>H', raw[6:8])[0]
    load_addr = struct.unpack('>H', raw[8:10])[0]
    payload = raw[data_off:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        payload = payload[2:]
    return raw[:data_off], load_addr, payload


# --- Memory-map regions for Karate ($1000 = load) -------------------
# Derived from docs/hubbard_sample_music_karate_disassembly.s.
ENGINE_CODE_LO = 0x1000   # main player code (init trampoline + play body + utilities)
ENGINE_CODE_HI = 0x13FC   # exclusive — first byte of freq table
FREQ_TABLE_LO  = 0x13FC
FREQ_TABLE_HI  = 0x14BC   # exclusive — 192 bytes (96 entries × lo,hi interleaved)
SID_BASE_LO    = 0x14BC   # 3 bytes [0, 7, 14]
SID_BASE_HI    = 0x14BF
INSTR_TABLE_LO = 0x150B
INSTR_TABLE_RECORD = 8
INIT_ROUTINE_LO = 0x1DE3
INIT_ROUTINE_HI = 0x1E02   # exclusive (covers L_1DE3 .. L_1DFC bodies)


def build_freq_table_bytes(T):
    """Emit Karate's interleaved (lo, hi) freq table — 96 entries × 2 bytes."""
    out = bytearray()
    for i in range(96):
        v = T[i] if i < len(T) else 0
        out.append(v & 0xFF)
        out.append((v >> 8) & 0xFF)
    return out


def build_instrument_table_bytes(rh_instruments, total_records):
    """Emit Karate's 8-bytes-per-instrument table for $150B.

    `rh_instruments` is the list from `decompile().instruments`. Each
    record is laid out: pw_lo, pw_hi, ctrl, ad, sr, vibrato_depth,
    pwm_speed, fx_flags. Records past max(rh.index) are zeroed (the
    binary keeps a trailing all-zero "silence" record at index 19 used
    as the first-frame default instrument; see disassembly).
    """
    out = bytearray(total_records * 8)
    for rh in rh_instruments:
        idx = rh.index
        base = idx * 8
        out[base + 0] = rh.pw_lo
        out[base + 1] = rh.pw_hi
        out[base + 2] = rh.ctrl
        out[base + 3] = rh.ad
        out[base + 4] = rh.sr
        out[base + 5] = rh.vibrato_depth
        out[base + 6] = rh.pwm_speed
        out[base + 7] = rh.fx_flags
    return out


def build():
    header, load_addr, original_payload = load_psid(SID_PATH)
    payload = bytearray(original_payload)

    # Stage 2: substitute freq table from the extract pipeline.
    from pipelines.sample_music_i_karate.extract.engine_model import extract
    song = extract(subtune=0, ft_base=0x13FC)
    freq_bytes = build_freq_table_bytes(song.freq_table)
    assert len(freq_bytes) == FREQ_TABLE_HI - FREQ_TABLE_LO, (
        f"freq table size {len(freq_bytes)} != {FREQ_TABLE_HI - FREQ_TABLE_LO}")
    off = FREQ_TABLE_LO - load_addr
    payload[off:off + len(freq_bytes)] = freq_bytes

    # Stage 4 (decompile re-runs implicitly below): Stage 4 work happens after
    # we have `decomp` in scope — see below the instrument table.
    # Stage 3: substitute instrument table from raw decompile output.
    # We use raw rh_instruments rather than the structured Instrument
    # because the latter loses fx_flags upper nibble (used by Phase-4
    # arpeggio drivers).
    from pipelines.sample_music_i_karate.extract.decompile import (
        decompile, RHInstrument)
    decomp = decompile(SID_PATH)
    # decompile() only emits instruments referenced in patterns. Karate's
    # binary has 20 records (0..19); record 19 is unreferenced data that
    # the engine never reads but the binary keeps it in the table region.
    # Backfill any missing records by reading the original binary bytes.
    indices_present = {i.index for i in decomp.instruments}
    all_instrs = list(decomp.instruments)
    for idx in range(20):
        if idx not in indices_present:
            off_b = INSTR_TABLE_LO - load_addr + idx * 8
            data = original_payload[off_b:off_b + 8]
            all_instrs.append(RHInstrument(data, idx))
    instr_bytes = build_instrument_table_bytes(all_instrs, total_records=20)
    off = INSTR_TABLE_LO - load_addr
    payload[off:off + len(instr_bytes)] = instr_bytes

    # Stage 4: orderlists + patterns from decompile.
    # Each voice's orderlist starts at the address recorded in the binary's
    # song_table at $15B3/$15B6 (lo[3]+hi[3] split). Each pattern's bytes
    # start at the address recorded in the pattern_pointer table at
    # $15B9/$15E1 (lo[40]+hi[40]). We re-emit each ORDERLIST/PATTERN body
    # at its original address; the pointer tables themselves stay verbatim
    # (they hold addresses, not data, so they'd be identical anyway).
    n_pat_emitted, n_ol_emitted = 0, 0
    # Orderlists: emit pattern indices ONLY, leave binary's terminator
    # ($FF/$FE) and any transpose-marker bytes between in place. Karate's
    # V3 has $5F $5F transpose markers before the $FF terminator that
    # decompile.decode_track silently skips; preserving the binary tail
    # keeps those markers byte-perfect.
    song0 = decomp.songs[0]
    for v_idx, track in enumerate(song0.tracks):
        ol_lo = original_payload[decomp.song_table_addr - load_addr + v_idx]
        ol_hi = original_payload[decomp.song_table_addr - load_addr + 3 + v_idx]
        ol_addr = ol_lo | (ol_hi << 8)
        ol_bytes = bytearray()
        for kind, val in track:
            if kind == 'pattern':
                ol_bytes.append(val)
            else:
                break  # don't emit terminator — binary already has it
        off = ol_addr - load_addr
        payload[off:off + len(ol_bytes)] = ol_bytes
        n_ol_emitted += 1
    # Patterns (each terminated by $FF)
    for pat in decomp.patterns:
        pat_bytes = bytearray()
        for note in pat.notes:
            pat_bytes.extend(note.raw_bytes)
        pat_bytes.append(0xFF)
        off = pat.addr - load_addr
        payload[off:off + len(pat_bytes)] = pat_bytes
        n_pat_emitted += 1

    out = bytearray(header)
    if struct.unpack('>H', header[8:10])[0] == 0:
        out += struct.pack('<H', load_addr)
    out += payload
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'wb') as f:
        f.write(out)
    print(f"Wrote {OUT_PATH} ({len(out)} bytes, payload {len(payload)} @ ${load_addr:04X})")
    print(f"  freq table: {len(freq_bytes)} bytes from extract @ ${FREQ_TABLE_LO:04X}")
    print(f"  instr table: {len(instr_bytes)} bytes from decompile @ ${INSTR_TABLE_LO:04X}")
    print(f"  orderlists: {n_ol_emitted} voices from decompile.songs[0]")
    print(f"  patterns:   {n_pat_emitted} from decompile.patterns")


if __name__ == '__main__':
    build()
