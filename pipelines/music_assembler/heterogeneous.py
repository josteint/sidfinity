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

STATUS / SCOPE — read before extending. Wired into the DMC pipeline:
`detect_compilation` classifies each base's engine (`kinds`), and every path
that reconstructs a member — family batch, mass-write, `dmc_build_one` —
dispatches on it, so the member counts FULL in the family batch and its
stored `.usf` rebuilds its stored `.sid`.
"""

from __future__ import annotations

import copy
import dataclasses
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
    """Compose the member THROUGH its USF (extract -> one UsfFile -> compose).

    Everything the build needs now lives in that single file, so this is the
    same path a rebuild from the STORED artifact takes.
    """
    return build_from_usf(heterogeneous_to_usf(rel, spec, hvsc_root=hvsc_root))


def _refs(sub) -> set:
    """Every instrument id a music subtune references."""
    out = set()
    for v in sub.voices:
        for pat in v.patterns:
            for row in pat.rows:
                if row.instr is not None and row.instr.id is not None:
                    out.add(row.instr.id)
    if sub.init is not None:
        for iv in sub.init.voices:
            if iv.instr is not None and iv.instr.id is not None:
                out.add(iv.instr.id)
    return out


def _shift_refs(sub, d: int):
    """Offset every instrument reference in a subtune by `d`, in place."""
    from src.usf.types import InstrumentRef
    if not d:
        return
    for v in sub.voices:
        for pat in v.patterns:
            for k, row in enumerate(pat.rows):
                if row.instr is not None and row.instr.id is not None:
                    pat.rows[k] = dataclasses.replace(
                        row, instr=InstrumentRef(id=row.instr.id + d))
    if sub.init is not None:
        for iv in sub.init.voices:
            if iv.instr is not None and iv.instr.id is not None:
                iv.instr = InstrumentRef(id=iv.instr.id + d)


def heterogeneous_to_usf(rel: str, spec: dict | None = None,
                         hvsc_root: str = 'hvsc84'):
    """The whole member as ONE UsfFile.

    Each packed player is extracted through its own family's USF path, then
    merged: instruments go into one pool (the FIRST player keeps its ids, so
    its slice is identity; later players are offset past it), and everything
    that differs per player rides the per-subtune overrides that already
    exist for exactly this reason — `params`, `init`, plus `freq_table` and
    `default_filter`, which are per-subtune because a compilation's players
    tune differently and each carries its own idle filter sweep.

    Each subtune names its engine (`origin_engine`) — permitted here because
    this file demonstrably requires more than one COMPOSER (principle §8,
    ledger C35). `build_from_usf` reads it to pick the composer; nothing
    reads it to decide what to EMIT.
    """
    from pipelines.dmc.v4.compilation import detect_compilation
    from src.usf.types import MusicSubtune, Params, UsfFile
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

    per_player = {}
    for pi, base in enumerate(bases):
        if kinds[pi] == 'dmc':
            per_player[pi] = ('dmc_v4', parse_file(write_dmc_usf(
                dmc_v4_config(rel, hvsc_root=hvsc_root, base_override=base,
                              post_init_sub=reloc.get(base)),
                td, hvsc_root=hvsc_root)))
        else:
            nxt = min([b for b in bases if b > base] or [base + 0x1000])
            mem = _landing_memory(s, img, reloc.get(base, 0), base, masm=True)
            if mem is None:
                raise ValueError('could not reach MA player at $%04X' % base)
            per_player[pi] = ('music_assembler', model_to_usf(
                extract_mem(mem, hdr=s, lo=base, hi=min(nxt, base + 0x1000))))

    merged_insts, shift, subtunes = [], {}, []
    top = 0
    for pi in sorted(per_player):
        _eng, u = per_player[pi]
        ids = [i.id for i in u.instruments]
        # The projection recovers a player's slice as the id RANGE its
        # subtunes reference, so the lowest-id instrument must be referenced
        # or the slice would start too high and shift every id after it.
        # (DMC ids are SPARSE — 9 instruments spanning 1..22 — so a dense
        # renumber is not available.)
        used = set()
        for sub in u.subtunes:
            if isinstance(sub, MusicSubtune):
                used |= _refs(sub)
        if ids and used and min(used) != min(ids):
            raise ValueError(
                'player %d: lowest instrument i%d is unreferenced (lowest '
                'referenced is i%d) — the merged slice cannot be recovered'
                % (pi, min(ids), min(used)))
        shift[pi] = top
        for inst in u.instruments:
            merged_insts.append(dataclasses.replace(inst, id=inst.id + top))
        top += (max(ids) if ids else 0)

    first = per_player[min(per_player)][1]
    for k, (pi, song) in enumerate(spec['map']):
        eng, u = per_player[pi]
        music = [x for x in u.subtunes if isinstance(x, MusicSubtune)]
        src = music[song] if song < len(music) else music[0]
        sub = copy.deepcopy(src)
        _shift_refs(sub, shift[pi])
        sub.id = k
        sub.origin_engine = eng
        # Per-subtune overrides: whatever this player disagrees with the file
        # on. `params`/`init` already had the idiom; freq_table and
        # default_filter are the two this member needed.
        sub.params = sub.params or u.params
        sub.init = sub.init or u.init
        sub.freq_table = list(u.freq_table) if u.freq_table else None
        sub.default_filter = u.default_filter
        subtunes.append(sub)

    return UsfFile(
        psid=first.psid, params=Params(fields={}), init=first.init,
        instruments=merged_insts, subtunes=subtunes,
        freq_table=None,
        filter_programs=getattr(first, 'filter_programs', {}) or {},
        wave_programs=getattr(first, 'wave_programs', {}) or {},
        arp_programs=getattr(first, 'arp_programs', {}) or {},
        pulse_programs=getattr(first, 'pulse_programs', {}) or {},
        song_end=first.song_end, init_behavior=first.init_behavior,
        master_vol=first.master_vol)


def _blocks(music) -> list:
    """(lo, hi) instrument-id block per subtune, in subtune order.

    Blocks TILE the id space and are split at each subtune's lowest
    REFERENCED id — the first block starting at 1. They are emphatically NOT
    "the ids this subtune references": ledger C31's merge trap is that a
    player's RECORD 0 can be referenced by no row at all, because init clears
    the note-init cache to 0 and an idle voice runs record 0's pulse/wave
    mechanism. Dropping it is inaudible until a voice idles, then wrong
    (Freespace's DMC player: instrument i1 is unreferenced by its only
    dispatched song, and losing it diverges the stream at write 28).

    Tiling from the previous block's end instead of from min-referenced keeps
    those silent-but-live records with the player that owns them.
    """
    starts = []
    for k, sub in enumerate(music):
        used = _refs(sub)
        starts.append(1 if k == 0 else (min(used) if used else 1))
    out = []
    for k in range(len(starts)):
        hi = (starts[k + 1] - 1) if k + 1 < len(starts) else None
        out.append((starts[k], hi))
    return out


def _project(usf, subs, block=None):
    """A single-engine VIEW of `usf` holding only `subs` (one player's
    subtunes), with its instrument slice renumbered back into its own id
    space — so each composer sees exactly the file it would have seen alone
    (byte-identical output, hence the same verdict)."""
    from src.usf.types import MusicSubtune, UsfFile
    used = set()
    for sub in subs:
        used |= _refs(sub)
    if block is not None:
        lo, hi = block
        hi = hi if hi is not None else max(
            [i.id for i in usf.instruments] or [lo])
    else:
        lo, hi = min(used), max(used)
    d = lo - 1
    insts = [dataclasses.replace(i, id=i.id - d)
             for i in usf.instruments if lo <= i.id <= hi]
    out = []
    for n, sub in enumerate(subs, 1):
        c = copy.deepcopy(sub)
        _shift_refs(c, -d)
        c.id = n
        c.origin_engine = None            # the view is single-engine
        if c.freq_table is None:
            c.freq_table = usf.freq_table
        out.append(c)
    view = copy.deepcopy(usf)
    view.instruments = insts
    view.subtunes = out
    view.freq_table = out[0].freq_table
    view.default_filter = out[0].default_filter
    # The FIRST player keeps the merged file's own params/init (there is one
    # file-level slot and it is his); a LATER player's file-level params/init
    # were parked on its subtune at merge time, so lift them back out here.
    # Getting this wrong is silent: DMC's file-level init carries the per-voice
    # note/gate_mask priming, and overwriting it with the subtune's thinner
    # per-subtune init diverges the stream at write 26 with state_match still
    # true.
    if lo > 1:
        if out[0].params is not None:
            view.params = out[0].params
        if out[0].init is not None:
            view.init = out[0].init
        for c in out:
            c.params = None
            c.init = None
    for c in out:
        c.freq_table = None
        c.default_filter = None
    return view


def build_from_usf(usf) -> bytes:
    """Compose the member from ONE parsed UsfFile (the stored artifact).

    Groups the subtunes by `origin_engine`, projects each group to a
    single-engine view, composes it with that family's composer, and splices
    the results behind a generated dispatcher. The engine reference is read
    HERE, by the dispatcher, and nowhere else — no composer branches on it.
    """
    from src.usf.types import MusicSubtune
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]

    # ONE composer instance PER SUBTUNE. Grouping by `origin_engine` would be
    # wrong: two subtunes can name the same FAMILY yet be different PLAYERS
    # (Freespace packs two Music Assembler players, each with its own
    # instruments, tuning and idle filter sweep), and merging them into one
    # view silently builds one tune from another's data. A player serving
    # several subtunes is composed once per subtune — costs image size, never
    # correctness.
    blocks = _blocks(music)
    placed, o = [], DMC_ORIGIN
    for n, sub in enumerate(music):
        view = _project(usf, [sub], blocks[n])
        eng = sub.origin_engine or 'dmc_v4'
        if eng == 'music_assembler':
            blob = assemble(compose_asm(usf_to_model(view), origin=o,
                                        prefix='e%d_' % n))
        else:
            blob = assemble(_sanitize_asm(compose_dmc_asm(view, origin=o)))
        placed.append((o, blob))
        o = (o + len(blob) + 1) & ~1

    entries = [(a, a + 3, 0) for a, _b in placed]
    disp = assemble(_dispatch_asm(entries))

    blobs = [(LOAD, disp)] + placed
    end = max(a + len(b) for a, b in blobs)
    image = bytearray(end - LOAD)
    for a, b in blobs:
        image[a - LOAD:a - LOAD + len(b)] = b
    hdr = build_header(load=0, init=LOAD, play=LOAD + 3,
                       songs=len(music), start_song=usf.psid.start_song,
                       speed=0, title=usf.psid.title, author=usf.psid.author,
                       released=usf.psid.released)
    return hdr + LOAD.to_bytes(2, 'little') + bytes(image)


# The one known carrier in DMC family-1. Kept as the regression canary's
# subject; the relocation it performs is now OBSERVED from the spec, not
# hand-specified here.
FREESPACE = 'MUSICIANS/B/Bayliss_Richard/Freespace_2075.sid'
