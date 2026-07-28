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

    ⚠ DO NOT migrate this to siddump/libsidplayfp — it is a SIMULATION, not an
    observation (the exact class + reason as DMC `_postinit_window`, native-
    capture Phase 2c; see feedback_ground_truth.md). It deliberately reads an
    IDEALIZED machine (zero-fill + image, no PSID driver, stopped at the
    landing); the real machine cannot produce that counterfactual (psiddrv is
    always resident, and running past the landing overwrites the leftovers),
    so a libsidplayfp RAM snapshot injects driver/environment bytes and
    corrupts the priming. py65 reads image + init-copied bytes here, which is
    correct per the ground-truth rule.
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
    """Every instrument id a music subtune references.

    Covers both reference forms: `row.instr` (DMC V4 / MA) and the V5
    command-per-row `set_instr=<id>` fx flag (ledger C14 form; the V5
    engine's $FC command)."""
    out = set()
    for v in sub.voices:
        for pat in v.patterns:
            for row in pat.rows:
                if row.instr is not None and row.instr.id is not None:
                    out.add(row.instr.id)
                for fl in (row.fx_flags or ()):
                    if fl.startswith('set_instr='):
                        out.add(int(fl.split('=', 1)[1], 0))
    if sub.init is not None:
        for iv in sub.init.voices:
            if iv.instr is not None and iv.instr.id is not None:
                out.add(iv.instr.id)
    return out


def _shift_refs(sub, d: int):
    """Offset every instrument reference in a subtune by `d`, in place —
    `row.instr` refs, `set_instr=` fx flags, and init-voice refs alike."""
    from src.usf.types import InstrumentRef
    if not d:
        return
    seen_pats = set()
    for v in sub.voices:
        for pat in v.patterns:
            # a deduped pattern OBJECT can be shared by several voices /
            # orderlist positions (V5 sector pool) — shift it exactly once
            if id(pat) in seen_pats:
                continue
            seen_pats.add(id(pat))
            for k, row in enumerate(pat.rows):
                rep = {}
                if row.instr is not None and row.instr.id is not None:
                    rep['instr'] = InstrumentRef(id=row.instr.id + d)
                if any(fl.startswith('set_instr=')
                       for fl in (row.fx_flags or ())):
                    rep['fx_flags'] = tuple(
                        'set_instr=%d' % (int(fl.split('=', 1)[1], 0) + d)
                        if fl.startswith('set_instr=') else fl
                        for fl in row.fx_flags)
                if rep:
                    pat.rows[k] = dataclasses.replace(row, **rep)
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
    kinds = (spec.get('kinds') or []) if spec else []
    if spec is None or not kinds or all(k == 'dmc' for k in kinds):
        raise ValueError('not a heterogeneous compilation member')

    s = parse_psid(os.path.join(hvsc_root, rel))
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            img[s['load'] + i] = b

    bases = spec['bases']
    reloc = spec.get('reloc') or {}
    td = tempfile.mkdtemp()

    # ---- per-player (per-UNIT) extraction. The DMC V4 players form ONE
    #      unit: with >=2 of them the proven homogeneous merge
    #      (write_dmc_compilation_usf) builds them into one model with all
    #      the C31 per-player machinery (idle priming, rest_effects,
    #      d417_shadow, song_subtunes); a lone V4 player keeps the original
    #      per-player path byte-for-byte (Freespace). V5 / MA players are
    #      one unit each. `unit_of[pi]` maps a spec player to its unit;
    #      'seq' units consume their subtunes in map order, 'song' units
    #      index by the map's song number. ----
    per_player = {}          # unit id -> (engine, UsfFile, 'seq'|'song')
    unit_of = {}
    dmc_idx = [i for i, k in enumerate(kinds) if k == 'dmc']
    if len(dmc_idx) >= 2:
        from pipelines.dmc.v4.extract.to_usf import write_dmc_compilation_usf
        sub_bases = [bases[i] for i in dmc_idx]
        pos = {p: n for n, p in enumerate(dmc_idx)}
        subspec = {'bases': sub_bases,
                   'map': [(pos[pi], song) for pi, song in spec['map']
                           if pi in dmc_idx],
                   'reloc': {b: sb for b, sb in reloc.items()
                             if b in sub_bases}}
        uid = dmc_idx[0]
        per_player[uid] = ('dmc_v4', parse_file(write_dmc_compilation_usf(
            rel, subspec, td, hvsc_root=hvsc_root)), 'seq')
        for pi in dmc_idx:
            unit_of[pi] = uid
    elif dmc_idx:
        pi = dmc_idx[0]
        cfg = dmc_v4_config(rel, hvsc_root=hvsc_root, base_override=bases[pi],
                            post_init_sub=reloc.get(bases[pi]))
        # C31: any runtime measurement inside the extract must run the file
        # subtune that SELECTS this player (song numbering is local).
        smap = {}
        for k, (pi2, song2) in enumerate(spec['map']):
            if pi2 == pi:
                smap.setdefault(song2, k)
        cfg.song_subtunes = smap
        # this merge rebuilds one UsfFile from parts (no file-level
        # wave_table survives) — expand a normal-form part's pointer
        # instruments back to resolved copies first
        from pipelines.dmc.composer_asm import denormalize_wave_table
        per_player[pi] = ('dmc_v4', denormalize_wave_table(parse_file(
            write_dmc_usf(cfg, td, hvsc_root=hvsc_root))), 'song')
        unit_of[pi] = pi
    for pi, base in enumerate(bases):
        if kinds[pi] == 'dmc':
            continue
        if kinds[pi] == 'dmcv5':
            from pipelines.dmc.v5.factory import dmc_v5_config
            from pipelines.dmc.v5.extract.engine_model import extract as v5x
            from pipelines.dmc.v5.extract.to_usf import (
                model_to_usf as v5_to_usf, _verify_window_frames)
            n_songs = max(song for p, song in spec['map'] if p == pi) + 1
            cfg5 = dmc_v5_config(rel, hvsc_root=hvsc_root, base_override=base,
                                 n_songs=n_songs,
                                 post_init_sub=reloc.get(base))
            per_player[pi] = ('dmc_v5', v5_to_usf(
                v5x(cfg5, hvsc_root=hvsc_root),
                reach=_verify_window_frames(cfg5, hvsc_root)), 'song')
        else:
            nxt = min([b for b in bases if b > base] or [base + 0x1000])
            mem = _landing_memory(s, img, reloc.get(base, 0), base, masm=True)
            if mem is None:
                raise ValueError('could not reach MA player at $%04X' % base)
            per_player[pi] = ('music_assembler', model_to_usf(
                extract_mem(mem, hdr=s, lo=base, hi=min(nxt, base + 0x1000))),
                'song')
        unit_of[pi] = pi

    merged_insts, shift, subtunes = [], {}, []
    top = 0
    # The V4 unit goes FIRST in the id space regardless of its player index:
    # the first (lowest-block) unit keeps the merged file's file-level slots,
    # and only V4 has file-level init the park/lift cannot carry (its
    # subtunes already hold their own per-subtune inits, so the file init
    # could never be parked — Black_It's V5 player is pi 0 but must not own
    # the file level). Members whose V4 unit is already lowest-pi (Freespace,
    # Super_Tau-Zeta) are byte-identical under this ordering.
    unit_order = sorted(per_player,
                        key=lambda uid: (per_player[uid][0] != 'dmc_v4', uid))
    for pi in unit_order:
        eng0, u, _mode = per_player[pi]
        ids = [i.id for i in u.instruments]
        # A V5 unit idles every voice on instrument-table position 0 (its
        # init clears instr_n) — record that as init-voice refs so the
        # lowest id is genuinely referenced and the slice check below (and
        # the block tiling) see the true usage. V5's own build reads only
        # `iv.note` from init voices, so this adds content without changing
        # its output.
        if eng0 == 'dmc_v5' and ids:
            from src.usf.types import InstrumentRef
            for sub in u.subtunes:
                if isinstance(sub, MusicSubtune) and sub.init is not None:
                    for iv in sub.init.voices:
                        if iv.instr is None:
                            iv.instr = InstrumentRef(id=min(ids))
        # The projection recovers a player's slice as the id RANGE its
        # subtunes reference, so the lowest-id instrument must be referenced
        # or the slice would start too high and shift every id after it.
        # (DMC ids are SPARSE — 9 instruments spanning 1..22 — so a dense
        # renumber is not available.)
        used = set()
        for sub in u.subtunes:
            if isinstance(sub, MusicSubtune):
                used |= _refs(sub)
        if eng0 == 'dmc_v4' and ids and used and min(used) != min(ids):
            # V4's record 0 (i1) is ALWAYS live — init clears the note-init
            # cache to 0, so an idle voice runs record 0's pulse/wave
            # mechanism (the C31 merge trap named in `_groups`). The old
            # resolver seeds (`instr: i1` hardcoded) referenced it by
            # accident; the true leftover seeds (C32 r113) need not. Record
            # the idle anchor as an init-voice ref so the slice check and
            # block tiling see the true usage — a slot-0 ref keeps the V4
            # composer's gated constant init form, so its output is
            # unchanged.
            from src.usf.types import InitState, InitVoice, InstrumentRef
            anchor = InstrumentRef(id=min(ids))
            injected = False
            for sub in u.subtunes:
                if not isinstance(sub, MusicSubtune):
                    continue
                if sub.init is not None:
                    for iv in sub.init.voices:
                        if iv.instr is None:
                            iv.instr = InstrumentRef(id=anchor.id)
                            injected = True
                    if injected:
                        break
            if not injected:
                for sub in u.subtunes:
                    if isinstance(sub, MusicSubtune):
                        if sub.init is None:
                            sub.init = InitState(voices=[])
                        sub.init.voices.append(
                            InitVoice(id=1, instr=InstrumentRef(id=anchor.id)))
                        break
            used = set()
            for sub in u.subtunes:
                if isinstance(sub, MusicSubtune):
                    used |= _refs(sub)
        if ids and used and min(used) != min(ids):
            raise ValueError(
                'player %d: lowest instrument i%d is unreferenced (lowest '
                'referenced is i%d) — the merged slice cannot be recovered'
                % (pi, min(ids), min(used)))
        # Shift this unit's ids to start right after the pool so far. A V4/MA
        # unit's ids are 1-based (shift == top, the original arithmetic); a
        # V5 unit's are 0-based, which unshifted would collide with the
        # previous unit's top id.
        shift[pi] = (top + 1 - min(ids)) if ids else 0
        for inst in u.instruments:
            merged_insts.append(dataclasses.replace(inst, id=inst.id + shift[pi]))
        top = (shift[pi] + max(ids)) if ids else top

    first_uid = unit_order[0]
    first = per_player[first_uid][1]
    seq_ctr = {uid: 0 for uid in per_player}
    for k, (pi, song) in enumerate(spec['map']):
        uid = unit_of[pi]
        eng, u, mode = per_player[uid]
        music = [x for x in u.subtunes if isinstance(x, MusicSubtune)]
        if mode == 'seq':
            src = music[seq_ctr[uid]]
            seq_ctr[uid] += 1
        else:
            src = music[song] if song < len(music) else music[0]
        sub = copy.deepcopy(src)
        _shift_refs(sub, shift[uid])
        sub.id = k
        sub.origin_engine = eng
        # Per-subtune overrides: whatever this player disagrees with the file
        # on. `params`/`init` already had the idiom; freq_table /
        # default_filter (Freespace) and wave_programs (Super_Tau-Zeta's V5
        # idle program) are the ones members needed so far.
        sub.params = sub.params or u.params
        sub.init = sub.init or u.init
        # or-preserving: a V4-merged unit's subtunes may already carry their
        # OWN per-subtune overrides (its packed players tune differently) —
        # never clobber those with the unit's file-level value.
        if sub.freq_table is None:
            sub.freq_table = list(u.freq_table) if u.freq_table else None
        if sub.default_filter is None:
            sub.default_filter = u.default_filter
        if uid != first_uid and getattr(u, 'wave_programs', None):
            sub.wave_programs = dict(u.wave_programs)
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


def _groups(music) -> list:
    """Group subtunes that share one composer instance, with their
    instrument-id block: returns [(indices, engine, (lo, hi))], in id order.

    Blocks TILE the id space and are split at each GROUP's lowest
    REFERENCED id — the first block starting at 1. They are emphatically NOT
    "the ids a subtune references": ledger C31's merge trap is that a
    player's RECORD 0 can be referenced by no row at all, because init clears
    the note-init cache to 0 and an idle voice runs record 0's pulse/wave
    mechanism. Dropping it is inaudible until a voice idles, then wrong
    (Freespace's DMC player: instrument i1 is unreferenced by its only
    dispatched song, and losing it diverges the stream at write 28).

    Grouping: ALL 'dmc_v4' subtunes form one group (the merge builds every
    packed V4 player into one model, so they reference one shared block —
    per-subtune tiling would split it and truncate each view's slice);
    any other consecutive same-engine subtunes group when their referenced
    id intervals OVERLAP (one packed player serving several subtunes);
    otherwise each subtune stands alone (Freespace's two MA players).
    """
    groups = []          # [{'eng', 'idx', 'lo', 'hi'}]  (lo/hi = referenced)
    v4g = None
    for i, sub in enumerate(music):
        eng = sub.origin_engine or 'dmc_v4'
        used = _refs(sub)
        lo, hi = (min(used), max(used)) if used else (None, None)
        if eng == 'dmc_v4' and v4g is not None:
            v4g['idx'].append(i)
            if lo is not None:
                v4g['lo'] = min(v4g['lo'], lo) if v4g['lo'] else lo
                v4g['hi'] = max(v4g['hi'], hi) if v4g['hi'] else hi
            continue
        g = groups[-1] if groups else None
        if (g is not None and eng != 'dmc_v4' and g['eng'] == eng
                and g['lo'] is not None and lo is not None
                and lo <= g['hi'] and g['lo'] <= hi):
            g['idx'].append(i)
            g['lo'], g['hi'] = min(g['lo'], lo), max(g['hi'], hi)
            continue
        groups.append({'eng': eng, 'idx': [i], 'lo': lo, 'hi': hi})
        if eng == 'dmc_v4':
            v4g = groups[-1]
    # tile blocks in referenced-id order
    order = sorted(range(len(groups)),
                   key=lambda n: groups[n]['lo'] if groups[n]['lo'] else 0)
    starts = []
    for rank, n in enumerate(order):
        starts.append(1 if rank == 0 else groups[n]['lo'])
    if any(b is not None and a >= b for a, b in zip(starts, starts[1:])):
        raise ValueError('heterogeneous instrument blocks are not '
                         'monotonic: %r' % (starts,))
    out = [None] * len(groups)
    for rank, n in enumerate(order):
        hi = (starts[rank + 1] - 1) if rank + 1 < len(order) else None
        out[n] = (groups[n]['idx'], groups[n]['eng'], (starts[rank], hi))
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
    # true. The subtune KEEPS its init: engines split on where they read it
    # (Music Assembler: file level; DMC V5: the subtune) — leaving both
    # populated serves each, since neither reads the other's slot.
    if lo > 1:
        if out[0].params is not None:
            view.params = out[0].params
        if out[0].init is not None:
            view.init = out[0].init
        for c in out:
            c.params = None
    # Parked file-level wave_programs (the V5 idle program) lift back the
    # same way freq_table does.
    if getattr(out[0], 'wave_programs', None):
        view.wave_programs = out[0].wave_programs
    for c in out:
        # Clear only what the view-level slot now carries; a multi-subtune
        # V4 group whose subtunes genuinely disagree (per-player tuning /
        # idle sweep) keeps those as the per-subtune overrides the V4
        # composer reads natively.
        if c.freq_table == view.freq_table:
            c.freq_table = None
        if c.default_filter == view.default_filter:
            c.default_filter = None
        c.wave_programs = None
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

    # ONE composer instance PER GROUP (see _groups). Grouping by
    # `origin_engine` alone would be wrong: two subtunes can name the same
    # FAMILY yet be different PLAYERS (Freespace packs two Music Assembler
    # players, each with its own instruments, tuning and idle filter sweep),
    # and merging them into one view silently builds one tune from another's
    # data — those stay one instance per subtune. The V4 subtunes are the
    # exception: the merge built every packed V4 player into ONE model, so
    # they compose as one instance whose PSID song index is the subtune's
    # position within the group (the dispatcher passes it in A).
    entries = [None] * len(music)
    placed, o = [], DMC_ORIGIN
    for idx, eng, block in _groups(music):
        subs = [music[i] for i in idx]
        view = _project(usf, subs, block)
        if eng == 'music_assembler':
            blob = assemble(compose_asm(usf_to_model(view), origin=o,
                                        prefix='e%d_' % idx[0]))
        elif eng == 'dmc_v5':
            from pipelines.dmc.v5.composer_v5 import emit_v5_asm
            from pipelines.dmc.v5.from_usf import usf_to_model as v5_model
            blob = assemble(_sanitize_asm(emit_v5_asm(v5_model(view),
                                                      origin=o)))
        else:
            blob = assemble(_sanitize_asm(compose_dmc_asm(view, origin=o)))
        placed.append((o, blob))
        for song, i in enumerate(idx):
            entries[i] = (o, o + 3, song)
        o = (o + len(blob) + 1) & ~1

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
