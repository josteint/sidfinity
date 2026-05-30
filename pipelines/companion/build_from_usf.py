"""USF v2 → SID for the Companion engine.

Inverse of `pipelines/companion/to_usf.py`. Reads
`<basename>.usf` and produces a byte-exact SID without touching the
original binary.

Reuses the engine asm template and data emission from `codegen.py`;
the work here is reconstructing the in-memory `SubtuneData` records
from the parsed USF.
"""

from __future__ import annotations

import os
import struct

from src.usf import UsfFile, MusicSubtune, parse_file
from pipelines.companion.extract import SubtuneData, VoiceState, VoicePadding
from pipelines.companion import codegen as cg


_SEMITONE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
             'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def _byte_from_row(row) -> int:
    """Inverse of `to_usf._row_from_byte`."""
    early = 'fx:early_release' in row.fx_flags
    if row.pitch.is_rest:
        # Rest + early_release = $8C; rest without flags shouldn't
        # happen in Companion's song-proper (the engine never reads
        # a row with V_FREQ=0 unless it's $0C/$0D garbage, which we
        # keep in `trailing`).
        if not early:
            raise ValueError(
                'rest row without fx:early_release is not representable '
                'in Companion; should be in trailing bytes')
        return 0x8C
    octave = row.pitch.octave
    semitone = _SEMITONE[row.pitch.name]
    b = (octave << 4) | semitone
    if early:
        b |= 0x80
    return b


def _voice_state_from_init(iv, instr) -> VoiceState:
    """Build a VoiceState from a USF InitVoice + its referenced Instrument.

    InitVoice carries ctrl/dur_field/pwm_period/pwm_dir/slide_v (most
    unused for Companion). The Instrument has the locked timbre
    (ctrl, pw, ad, sr).
    """
    init_pw = instr.pwm.init
    pw_lo = init_pw & 0xFF
    pw_hi = (init_pw >> 8) & 0xFF
    return VoiceState(
        pos=0,
        gate_off_flag=0,
        pw_lo=pw_lo,
        pw_hi=pw_hi,
        ctrl_noGate=iv.ctrl,
        ad=instr.adsr[0],
        sr=instr.adsr[1],
    )


def _orderlist_bytes_from_voice_block(vb) -> bytes:
    """Reconstruct the engine orderlist bytes for one voice.

    Layout: <pattern rows> + $8D (the `stop` terminator). Post-$8D
    ringoff bytes are NOT here — they come from the codegen laying
    out subsequent data adjacent in memory.
    """
    if not vb.patterns:
        raise ValueError(f'voice {vb.id} has no patterns')
    pat = vb.patterns[0]
    body = bytes(_byte_from_row(r) for r in pat.rows)
    return body + bytes([0x8D])


def _subtune_from_music(ms: MusicSubtune,
                        instruments_by_id: dict) -> SubtuneData:
    p = ms.params.fields
    iv1, iv2, iv3 = ms.init.voices
    return SubtuneData(
        index=ms.id,
        v1_state=_voice_state_from_init(iv1, instruments_by_id[iv1.instr.id]),
        v2_state=_voice_state_from_init(iv2, instruments_by_id[iv2.instr.id]),
        v3_state=_voice_state_from_init(iv3, instruments_by_id[iv3.instr.id]),
        gate_off_tick=p['gate_off_tick'],
        note_load_tick=p['note_load_tick'],
        init_tempo_counter=p['init_tempo_counter'],
        init_pwm_ctr=p['init_pwm_ctr'],
        init_pwm_ctr_2=p['init_pwm_ctr_2'],
        vol_filter=p['vol_filter'],
        filter_cutoff_hi=p['filter_cutoff_hi'],
        v1_padding=VoicePadding(p.get('v1_pad_count', 0), p.get('v1_pad_byte', 0)),
        v2_padding=VoicePadding(p.get('v2_pad_count', 0), p.get('v2_pad_byte', 0)),
        v3_padding=VoicePadding(p.get('v3_pad_count', 0), p.get('v3_pad_byte', 0)),
        orderlist_v1=_orderlist_bytes_from_voice_block(ms.voices[0]),
        orderlist_v2=_orderlist_bytes_from_voice_block(ms.voices[1]),
        orderlist_v3=_orderlist_bytes_from_voice_block(ms.voices[2]),
    )


def _companion_freq_tables() -> tuple[bytes, bytes]:
    """The Companion engine's freq tables are engine-level constants
    (same 256 bytes for every Companion tune) and live in
    `pipelines/companion/engine_constants.py`. The USF doesn't carry
    them — engine mechanism stays in the engine."""
    from pipelines.companion.engine_constants import (
        COMPANION_FREQ_HI, COMPANION_FREQ_LO)
    return COMPANION_FREQ_HI, COMPANION_FREQ_LO


def build_from_usf(usf_path: str, out_path: str) -> str:
    """Read a Companion USF, emit a byte-exact SID."""
    usf = parse_file(usf_path)
    if usf.engine != 'companion':
        raise ValueError(f"expected engine 'companion', got {usf.engine!r}")

    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)

    instruments_by_id = {inst.id: inst for inst in usf.instruments}
    subtunes = [_subtune_from_music(ms, instruments_by_id) for ms in music_subs]

    freq_hi, freq_lo = _companion_freq_tables()

    asm = cg.ENGINE + '\n' + cg._emit_data(subtunes, freq_hi, freq_lo) + '\n'

    import subprocess
    src = '/tmp/companion_build_from_usf.s'
    obj = '/tmp/companion_build_from_usf.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([cg.XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', cg.LOAD)
    h += struct.pack('>H', cg.LOAD)
    h += struct.pack('>H', cg.LOAD + 3)
    h += struct.pack('>H', len(music_subs))
    h += struct.pack('>H', usf.psid.start_song)
    h += struct.pack('>I', usf.psid.speed)
    def latin1(s: str, n: int) -> bytes:
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += latin1(usf.psid.title, 32)
    h += latin1(usf.psid.author, 32)
    h += latin1(usf.psid.released, 32)
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass    # db update is best-effort; never break the build
    return out_path


if __name__ == '__main__':
    import sys
    usf = sys.argv[1] if len(sys.argv) > 1 else 'demo/hubbard/Up_up_and_Away.usf'
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/uupa_from_usf.sid'
    p = build_from_usf(usf, out)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
