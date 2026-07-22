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

def _dispatch_asm(entries) -> str:
    """The per-subtune dispatcher, generated for N subtunes.

    `entries[k] = (init_addr, play_addr, song)` for PSID subtune k. init
    records which subtune was selected and jumps to that player's init with
    the song in A (Music Assembler ignores A — each packed MA player is one
    tune); play re-reads the record and jumps to the matching play.
    """
    out = ['* = $%04X' % LOAD, '        jmp dinit', '        jmp dplay',
           'dinit']
    for k in range(len(entries)):
        if k < len(entries) - 1:
            out += ['        cmp #$%02X' % k, '        beq i%d' % k]
    out.append('        jmp i%d' % (len(entries) - 1))
    for k, (ini, _play, song) in enumerate(entries):
        out += ['i%d      lda #$%02X' % (k, k),
                '        sta which',
                '        lda #$%02X' % song,
                '        jmp $%04X' % ini]
    out.append('dplay   lda which')
    for k in range(len(entries)):
        if k < len(entries) - 1:
            out += ['        cmp #$%02X' % k, '        beq p%d' % k]
    out.append('        jmp p%d' % (len(entries) - 1))
    for k, (_ini, play, _song) in enumerate(entries):
        out.append('p%d      jmp $%04X' % (k, play))
    out += ['which   .byt 0']
    return '\n'.join(out) + '\n'


def _landing_memory(s, img, sub: int, base: int, masm: bool,
                    max_steps: int = 400000):
    """RAM as it stands when subtune `sub`'s init reaches player `base`.

    A relocating wrapper copies its player into RAM, so the player is not in
    the file image and must be read from the post-copy memory. Snapshot AT THE
    LANDING, not after init completes — running init to the end overwrites the
    very work-file leftovers that are read as priming (ledger C31/C26).
    """
    import sys as _sys
    _sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    load = s['load']
    hi = min(0x10000, load + len(s['payload']))
    mem = ObservableMemory()
    for a in range(load, hi):
        mem[a] = img[a]
    mpu = MPU()
    mpu.memory = mem
    mpu.pc, mpu.a = s['init'], sub
    target = base + (0x48 if masm else 0)
    for _ in range(max_steps):
        if mpu.pc == target:
            return bytearray(mem[a] for a in range(0x10000))
        try:
            mpu.step()
        except Exception:
            break
    return None


def build(rel: str, spec: dict | None = None,
          hvsc_root: str = 'hvsc84') -> bytes:
    """Compose the member from its compilation SPEC.

    `spec` is what `detect_compilation` returns — bases, the per-subtune
    (player, song) map, which subtune materialises each relocated base, and
    each base's engine `kinds`. All of it is OBSERVED by running the member's
    own wrapper, so nothing here is hand-specified per member; pass None to
    detect it. Each sub-player is extracted from the RAM as it stands when the
    wrapper arrives at it, and every engine is built through its own USF.
    """
    from pipelines.dmc.v4.compilation import detect_compilation
    if spec is None:
        spec = detect_compilation(rel, hvsc_root=hvsc_root)
    if spec is None or 'masm' not in (spec.get('kinds') or []):
        raise ValueError('not a DMC+Music Assembler heterogeneous member')

    s = parse_psid(os.path.join(hvsc_root, rel))
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            img[s['load'] + i] = b

    bases, kinds = spec['bases'], spec['kinds']
    reloc = spec.get('reloc') or {}
    td = tempfile.mkdtemp()

    # Where each sub-player's engine lands in OUR image. The DMC engine keeps
    # the first slot; the rest follow it, each aligned to the next even byte.
    placed, o = {}, DMC_ORIGIN
    usf0 = None
    for pi, base in enumerate(bases):
        if kinds[pi] == 'dmc':
            u = parse_file(write_dmc_usf(
                dmc_v4_config(rel, hvsc_root=hvsc_root, base_override=base,
                              post_init_sub=reloc.get(base)),
                td, hvsc_root=hvsc_root))
            usf0 = usf0 or u
            blob = assemble(_sanitize_asm(compose_dmc_asm(u, origin=o)))
        else:
            # Bound the table search to THIS player's block: with more than one
            # MA player in the same 64K an unbounded search returns the first
            # player's tables for every one of them, and those addresses are
            # not materialised for the others (every preset field reads zero).
            nxt = min([b for b in bases if b > base] or [base + 0x1000])
            mem = _landing_memory(s, img, reloc.get(base, 0), base, masm=True)
            if mem is None:
                raise ValueError('could not reach MA player at $%04X' % base)
            m = extract_mem(mem, hdr=s, lo=base, hi=min(nxt, base + 0x1000))
            # THROUGH THE USF, like the DMC half: write each sub-player's .usf
            # and recover the model from the PARSED file. Building straight
            # from the extracted model would leave these the one place in the
            # pipeline that never exercises the USF round trip.
            mp = os.path.join(td, 'ma%d.usf' % pi)
            write_file(model_to_usf(m), mp)
            blob = assemble(compose_asm(usf_to_model(parse_file(mp)),
                                        origin=o, prefix='p%d_' % pi))
        placed[pi] = (o, blob)
        o = (o + len(blob) + 1) & ~1

    entries = [(placed[pi][0], placed[pi][0] + 3, song)
               for pi, song in spec['map']]
    disp = assemble(_dispatch_asm(entries))

    blobs = [(LOAD, disp)] + [placed[pi] for pi in sorted(placed)]
    end = max(a + len(b) for a, b in blobs)
    image = bytearray(end - LOAD)
    for a, b in blobs:
        image[a - LOAD:a - LOAD + len(b)] = b
    meta = usf0.psid if usf0 is not None else None
    hdr = build_header(load=0, init=LOAD, play=LOAD + 3,
                       songs=s.get('songs', 1),
                       start_song=s.get('start', 1), speed=0,
                       title=meta.title if meta else '',
                       author=meta.author if meta else '',
                       released=meta.released if meta else '')
    return hdr + LOAD.to_bytes(2, 'little') + bytes(image)


# The one known carrier in DMC family-1. Kept as the regression canary's
# subject; the relocation it performs is now OBSERVED from the spec, not
# hand-specified here.
FREESPACE = 'MUSICIANS/B/Bayliss_Richard/Freespace_2075.sid'
