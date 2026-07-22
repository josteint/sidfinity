"""DMC + Music Assembler heterogeneous member (ledger C31).

One HVSC member packs players from DIFFERENT engines behind a per-subtune
dispatch wrapper. C31 already covers the DMC + `dmc_sfx` case; this is the
DMC + Music Assembler case, whose only carrier in DMC family-1 is
`Bayliss_Richard/Freespace_2075` (a scan of all 163 f1 partials found exactly
one). Its wrapper is also a RELOCATING one (round 85): the MA players are
COPIED into RAM per subtune and are absent from the file image at their run
addresses, so each is extracted from the post-copy memory.

    subtune 0 -> DMC v4 player at $1000
    subtune 1 -> MA player copied $2000 -> $4700
    subtune 2 -> MA player copied $2800 -> $3700

The rebuild composes all three engines into one image behind a dispatcher at
the PSID vectors, exactly the shape the dmc_sfx path uses: init records which
engine the subtune selected, play jumps to it.

Every engine here is built THROUGH ITS USF — the DMC half via `write_dmc_usf`
-> `parse_file` -> `compose_dmc_asm`, each MA sub-player via `model_to_usf` ->
`write_file` -> `parse_file` -> `usf_to_model`. Nothing is composed from an
in-memory model, so the regression canary guards the round trip and not merely
the audio. All three subtunes verify FULL against the original's write stream
(225,157 / 127,969 / 35,179 writes).

STATUS / SCOPE — read before extending. Still not wired into the DMC pipeline:
`detect_compilation` does not classify MA sub-players, so the DMC family batch
reports this member `error: track at $836F never settles` rather than full.
That is the remaining work.
"""

from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from seed_disassembly import parse_psid                       # noqa: E402
from src.composer_runtime import assemble, build_header       # noqa: E402
from src.usf.parser import parse_file                         # noqa: E402
from src.usf.writer import write_file                         # noqa: E402
from pipelines.dmc.composer_asm import (_sanitize_asm,        # noqa: E402
                                        compose_dmc_asm)
from pipelines.dmc.v4.extract.to_usf import write_dmc_usf     # noqa: E402
from pipelines.dmc.v4.factory import dmc_v4_config            # noqa: E402
from pipelines.music_assembler.composer_asm import compose_asm  # noqa: E402
from pipelines.music_assembler.extract.model import extract_mem  # noqa: E402
from pipelines.music_assembler.extract.to_usf import model_to_usf  # noqa: E402
from pipelines.music_assembler.from_usf import usf_to_model     # noqa: E402

LOAD = 0x1000
DMC_ORIGIN = 0x1100

_DISPATCH = """
* = $1000
        jmp dinit
        jmp dplay
dinit   cmp #$01
        beq i1
        cmp #$02
        beq i2
        lda #$00
        sta which
        jmp ${dmc:04X}
i1      lda #$01
        sta which
        lda #$00
        jmp ${ma1:04X}
i2      lda #$02
        sta which
        lda #$00
        jmp ${ma2:04X}
dplay   lda which
        beq p0
        cmp #$01
        beq p1
        jmp ${ma2play:04X}
p0      jmp ${dmcplay:04X}
p1      jmp ${ma1play:04X}
which   .byt 0
"""


def build(rel: str, copies: dict, hvsc_root: str = 'hvsc84') -> bytes:
    """Compose the member. `copies` maps subtune -> (src, dst, length), the
    relocation its wrapper performs (observe it, never assume it)."""
    s = parse_psid(os.path.join(hvsc_root, rel))
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            img[s['load'] + i] = b

    td = tempfile.mkdtemp()
    usf = parse_file(write_dmc_usf(dmc_v4_config(rel, hvsc_root=hvsc_root),
                                   td, hvsc_root=hvsc_root))
    dmc_blob = assemble(_sanitize_asm(compose_dmc_asm(usf, origin=DMC_ORIGIN)))
    o = (DMC_ORIGIN + len(dmc_blob) + 1) & ~1

    ma = {}
    for sub in sorted(copies):
        src, dst, n = copies[sub]
        mem = bytearray(img)
        mem[dst:dst + n] = mem[src:src + n]
        m = extract_mem(mem, hdr=s, lo=dst, hi=dst + n)
        # THROUGH THE USF, like the DMC half above: write each sub-player's
        # .usf and recover the model from the PARSED file. Building straight
        # from the extracted model would leave this member's MA halves the one
        # place in the pipeline that never exercises the USF round trip — the
        # exact blind spot that let GoatTracker V1's .usf go unreadable.
        mp = os.path.join(td, 'ma%d.usf' % sub)
        write_file(model_to_usf(m), mp)
        blob = assemble(compose_asm(usf_to_model(parse_file(mp)),
                                    origin=o, prefix='m%d_' % sub))
        ma[sub] = (o, blob)
        o = (o + len(blob) + 1) & ~1

    disp = assemble(_DISPATCH.format(
        dmc=DMC_ORIGIN, dmcplay=DMC_ORIGIN + 3,
        ma1=ma[1][0], ma1play=ma[1][0] + 3,
        ma2=ma[2][0], ma2play=ma[2][0] + 3))

    blobs = [(LOAD, disp), (DMC_ORIGIN, dmc_blob)] + list(ma.values())
    end = max(a + len(b) for a, b in blobs)
    image = bytearray(end - LOAD)
    for a, b in blobs:
        image[a - LOAD:a - LOAD + len(b)] = b
    hdr = build_header(load=0, init=LOAD, play=LOAD + 3,
                       songs=s.get('songs', 1),
                       start_song=s.get('start', 1), speed=0,
                       title=usf.psid.title, author=usf.psid.author,
                       released=usf.psid.released)
    return hdr + LOAD.to_bytes(2, 'little') + bytes(image)


FREESPACE = ('MUSICIANS/B/Bayliss_Richard/Freespace_2075.sid',
             {1: (0x2000, 0x4700, 0x800), 2: (0x2800, 0x3700, 0x700)})
