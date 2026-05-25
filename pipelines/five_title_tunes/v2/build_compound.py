"""Compound PSID build for 5 Title Tunes.

Packs all 5 sub-engines into ONE PSID with a 5-way dispatcher at the
parent's original init/play addresses ($0B10 / $0B40). Each subtune
selects one of the 5 sub-engines.

Memory layout:
  $0B10 - $0B6F : init dispatcher (CMP/BNE chain)
  $0B70         : saved subtune index (one byte)
  $0B40 - $0BAF : play dispatcher
  $1000 - $1FFF : sub 0 engine (init=$1000, play=$1003)
  $2000 - $2FFF : sub 1 engine
  $3000 - $3FFF : sub 2 engine
  $4000 - $4FFF : sub 3 engine
  $5000 - $5FFF : sub 4 engine

PSID header:  load=$0B10, init=$0B10, play=$0B40, songs=5, start=1.

Per-subtune byte-exactness inherits from the 5 standalone sub builds
(see project_five_title_tunes.md / v2/config.py): each sub at its
relocated LOAD produces the same per-frame SID register-write stream
as the original 5_Title_Tunes.sid at the corresponding subtune.
"""

from __future__ import annotations

import os
import struct
import subprocess

from pipelines.hubbard.codegen import _emit_sid, _inputs_from_config
from pipelines.hubbard.note_codec import BitPackCodec
from pipelines.five_title_tunes.v2.config import ALL_TUNES

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')

# Sub-engine load addresses — each 4KB apart, all above the dispatcher.
SUB_LOADS = [0x1000, 0x2000, 0x3000, 0x4000, 0x5000]

DISPATCHER_INIT = 0x0B10
# The parent's play is at $0B40 (8 bytes per branch × 5 + small body = ~48
# bytes). Our dispatcher needs to LDA #0 before each JSR so each sub
# sees its own subtune 0 — makes init ~66 bytes, so play sits past the
# parent's location. Capture reads play_addr from the PSID header.
DISPATCHER_PLAY = 0x0B60
SUBTUNE_SAVE_ADDR = 0x0BA8    # past both dispatchers, far from engines.


def _build_engine(cfg, load_addr: int, tmp_dir: str) -> bytes:
    """Build one sub-engine at `load_addr` and return raw code bytes
    (PSID header stripped)."""
    inputs = _inputs_from_config(cfg)
    out_path = os.path.join(tmp_dir, f'_{cfg.name}_{load_addr:04X}.sid')
    _emit_sid(inputs, out_path, BitPackCodec(), load_addr=load_addr)
    with open(out_path, 'rb') as f:
        d = f.read()
    # PSID header is 124 bytes (the standard v2 header _emit_sid emits).
    return d[124:]


def _emit_chain(name_prefix: str, start_addr: int, target_offset: int) -> str:
    """Emit a CMP/BNE/JSR/RTS chain JSRing to SUB_LOADS[i] + target_offset.

    Each sub-engine has N_MUSIC=1 (a single subtune) and expects A=0
    when called. The compound's caller passes A = parent subtune index
    (0..4); the dispatcher saves that to SUBTUNE_SAVE_ADDR for routing,
    then LDA #0 before each JSR so the sub sees its own subtune 0.
    """
    lines = [f'* = ${start_addr:04X}', f'{name_prefix}:']
    if name_prefix == 'init':
        lines.append(f'        sta ${SUBTUNE_SAVE_ADDR:04X}')
    else:
        lines.append(f'        lda ${SUBTUNE_SAVE_ADDR:04X}')
    for i, addr in enumerate(SUB_LOADS):
        lines.append(f'        cmp #{i}')
        if i == len(SUB_LOADS) - 1:
            lines.append(f'        bne {name_prefix}_done')
        else:
            lines.append(f'        bne {name_prefix}_n{i + 1}')
        # Pass A=0 to the sub-engine — each was built with N_MUSIC=1
        # and would mis-route subtune indices > 0 into the SFX path.
        lines.append(f'        lda #0')
        lines.append(f'        jsr ${addr + target_offset:04X}')
        if name_prefix == 'play':
            # play() returns to dispatcher RTS; subtune index must be
            # in A again on the next reload — but $0B70 holds it.
            pass
        lines.append(f'        rts')
        if i != len(SUB_LOADS) - 1:
            lines.append(f'{name_prefix}_n{i + 1}:')
            # Restore A from the saved subtune for the next CMP.
            lines.append(f'        lda ${SUBTUNE_SAVE_ADDR:04X}')
    lines.append(f'{name_prefix}_done: rts')
    return '\n'.join(lines) + '\n'


def _assemble_chain(asm: str, tag: str, tmp_dir: str) -> bytes:
    src = os.path.join(tmp_dir, f'_{tag}.s')
    obj = os.path.join(tmp_dir, f'_{tag}.bin')
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 {tag} failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        return f.read()


def build_compound(out_path: str) -> str:
    """Build the compound 5 Title Tunes PSID.

    Writes a PSID file with load=$0B10, init=$0B10, play=$0B40, and 5
    music subtunes (one per sub-engine).
    """
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix='5tt_compound_')

    # Build each sub-engine at its target load address.
    sub_bodies: list[bytes] = []
    for cfg, addr in zip(ALL_TUNES, SUB_LOADS):
        body = _build_engine(cfg, addr, tmp_dir)
        sub_bodies.append(body)

    # Assemble init and play dispatchers separately and place them at
    # their proper addresses. xa65 emits a flat binary that ignores the
    # second `* =` directive — so we assemble each chain on its own.
    init_bytes = _assemble_chain(_emit_chain('init', DISPATCHER_INIT, 0),
                                 'init', tmp_dir)
    play_bytes = _assemble_chain(_emit_chain('play', DISPATCHER_PLAY, 3),
                                 'play', tmp_dir)
    if len(init_bytes) > DISPATCHER_PLAY - DISPATCHER_INIT:
        raise RuntimeError(
            f'init dispatcher ({len(init_bytes)}b) overflows play address '
            f'(${DISPATCHER_PLAY:04X})')

    # Compose the full memory image from DISPATCHER_INIT to the highest
    # used address. Fill gaps with $00.
    highest = max(addr + len(body)
                  for addr, body in zip(SUB_LOADS, sub_bodies))
    region = bytearray(highest - DISPATCHER_INIT)
    region[:len(init_bytes)] = init_bytes
    play_off = DISPATCHER_PLAY - DISPATCHER_INIT
    region[play_off:play_off + len(play_bytes)] = play_bytes
    for addr, body in zip(SUB_LOADS, sub_bodies):
        off = addr - DISPATCHER_INIT
        region[off:off + len(body)] = body

    # PSID header
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)               # version, hdr_len
    h += struct.pack('>H', DISPATCHER_INIT)        # load
    h += struct.pack('>H', DISPATCHER_INIT)        # init
    h += struct.pack('>H', DISPATCHER_PLAY)        # play
    h += struct.pack('>H', len(SUB_LOADS))         # songs
    h += struct.pack('>H', 1)                      # start_song
    h += struct.pack('>I', 0)                      # speed (PAL VBI for all)
    # Title / author / released — copy from parent.
    parent_sid = os.path.join(
        ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
        'Hubbard_Rob', '5_Title_Tunes.sid')
    with open(parent_sid, 'rb') as f:
        parent_hdr = f.read(124)
    h += parent_hdr[22:54]                         # title (32 bytes)
    h += parent_hdr[54:86]                         # author
    h += parent_hdr[86:118]                        # released
    h += struct.pack('>H', 0x0014)                 # PSID flags
    h += struct.pack('>BBH', 0, 0, 0)              # start_page/page_len/2nd_sid
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + bytes(region))
    return out_path


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/5tt_compound.sid'
    p = build_compound(out)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
