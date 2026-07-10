"""DMC v4 COMPILATION support (ledger C31).

A single SID file can pack N independent, fully-relocated copies of the SAME
DMC v4 engine, each with its own data pool (instruments / freq-wave-filter
tables / sectors / tracks / tune records). A small SMC dispatch wrapper at the
PSID init/play vectors maps each PSID subtune -> (player_base, that player's
song number):

    init/play vector -> JMP wrapper
    wrapper:  LDX subtune
              LDA base_hi_tab,X   -> STA <hi byte of the player JMP(s)>
              LDA song_tab,X      -> A (the song# handed to the selected player)
              JMP selected_player

`detect_compilation` finds the player bases (>=2 canonical DMC jump tables) and
statically decodes the two X-indexed wrapper tables into a per-subtune
(player_idx, song) map. `extract_compilation` extracts each player as a
standalone canonical DMC (factory `base_override`), then MERGES them into one
unified DmcModel emitting the correct per-subtune write stream: the freq/vibdepth
tuning is shared (verified identical across players), each player's instruments
are renumbered into one compact pool, and the songs are reordered by PSID
subtune. Scored by the CORE TENET — only the per-subtune write stream matters,
and each subtune runs exactly one player, so the streams are independent.

The result flows through the ordinary model_to_usf -> composer path unchanged
(one merged single-player DMC); the composer needs no compilation awareness.
"""

from __future__ import annotations

import copy
import os
from collections import defaultdict

from pipelines.dmc.v4.extract import engine_model as em


# ---------------------------------------------------------------------------
# Detection + subtune -> (player, song) map
# ---------------------------------------------------------------------------

def _canon_jt_bases(mem, load: int, img_hi: int) -> list:
    """Every base carrying a canonical DMC jump table `4C b+1D 4C b+85`."""
    out = []
    for b in range(load, img_hi - 6):
        if mem[b] == 0x4C and mem[b + 3] == 0x4C:
            e0 = mem[b + 1] | (mem[b + 2] << 8)
            e1 = mem[b + 4] | (mem[b + 5] << 8)
            if e0 == b + 0x1D and e1 == b + 0x85:
                out.append(b)
    return out


def _follow_jmps(mem, pc: int, hops: int = 8) -> int:
    """Chase a chain of `JMP abs` ($4C) up to `hops` deep; return the landing."""
    for _ in range(hops):
        if mem[pc] != 0x4C:
            break
        pc = mem[pc + 1] | (mem[pc + 2] << 8)
    return pc


def _is_player_base(mem, load: int, a: int) -> bool:
    """A page-aligned address carrying a DMC-family jump table: three `JMP abs`
    at +0/+3/+6. This is the RELOCATION- and REASSEMBLY-invariant player-base
    signature — canonical DMC (init +$1D / play +$85), the 2-entry / family-2
    layouts AND a re-assembled variant (Canyon's dmc_sfx player: init +$1B2 /
    play +$F0) all share the three-JMP head, where the rigid canonical-offset
    scan (`_canon_jt_bases`) misses the re-assembled ones."""
    return (load <= a and a + 6 < 0x10000
            and mem[a] == 0x4C and mem[a + 3] == 0x4C and mem[a + 6] == 0x4C)


def detect_compilation(sid_path: str, hvsc_root: str = 'hvsc84'):
    """Return a compilation spec or None.

    Spec: {'bases': [b0, b1, ...],           # distinct player bases (page-aligned)
           'map': [(player_idx, song), ...]}  # one entry per PSID subtune.
    None when the file is a single-player member (the common case): the dispatch
    wrapper doesn't decode into a base-hi table selecting >=2 distinct players.

    The player bases come from the wrapper's own base-hi `LDA abs,X` table (the
    authoritative list of what the dispatch selects), NOT from a memory scan for
    canonical jump tables — a heterogeneous compilation can pack a re-assembled
    or non-DMC player (Canyon_Tank_Duel's dmc_sfx sub-player at $3000, jump table
    at +$1B2/+$F0) whose base the canonical scan would miss. Each candidate base
    is validated by the three-JMP head (`_is_player_base`).
    """
    mem, s = em._load_image(os.path.join(hvsc_root, sid_path))
    load = s['load']
    songs = s.get('songs', 1)

    # follow the PSID init vector through the wrapper's JMP chain, then scan
    # the dispatch stub for its two `LDA abs,X` ($BD) tables.
    land = _follow_jmps(mem, s['init'])
    ldax = []
    p = land
    for _ in range(48):
        op = mem[p]
        if op == 0xBD:                       # LDA abs,X
            ldax.append(mem[p + 1] | (mem[p + 2] << 8))
            p += 3
        elif op in (0xAA, 0x8A, 0x98, 0xA8, 0xE8, 0xCA):   # TAX/TXA/.../INX/DEX
            p += 1
        elif op in (0x8D, 0x9D, 0x4C, 0xBC, 0xBE, 0xB9):   # abs stores/loads
            p += 3
        elif op in (0xA9, 0xA2, 0xA0):       # immediates
            p += 2
        elif op == 0x60:                     # RTS — stub ended
            break
        else:
            p += 1

    # classify the tables: the base-hi table's values all point (as a page
    # number, val<<8) at a player base; the song table's values are small
    # song numbers. Need at least the base-hi table.
    base_tab = song_tab = None
    for t in ldax:
        vals = [mem[(t + x) & 0xFFFF] for x in range(songs)]
        if all(_is_player_base(mem, load, v << 8) for v in vals):
            if base_tab is None:
                base_tab = vals
        elif all(v < 8 for v in vals):
            if song_tab is None:
                song_tab = vals
    if base_tab is None:
        return None
    if song_tab is None:
        # single-player-per-subtune dispatch with no song remap: every subtune
        # is song 0 of its selected player.
        song_tab = [0] * songs

    # ordered distinct bases in wrapper first-seen order
    ordered_bases = []
    for v in base_tab:
        b = v << 8
        if b not in ordered_bases:
            ordered_bases.append(b)
    base_idx = {b: i for i, b in enumerate(ordered_bases)}
    try:
        mp = [(base_idx[base_tab[x] << 8], song_tab[x]) for x in range(songs)]
    except (KeyError, IndexError):
        return None
    # Only a genuine compilation: the dispatch must actually select >=2
    # DISTINCT players. A single-player-with-wrapper (all subtunes -> one base)
    # is handled by the ordinary single-player path — never route it here.
    if len({pidx for pidx, _ in mp}) < 2:
        return None
    return {'bases': ordered_bases, 'map': mp}


# ---------------------------------------------------------------------------
# Merge N per-player models into one unified model
# ---------------------------------------------------------------------------

# instrument-select is a 5-bit id ($60+id, id 0-27 -> $60-$7B; $7C-$7F special),
# so the merged pool must stay within 28 instruments.
_MAX_INSTR = 28


def _inst_key(inst, drop=()):
    """Content key for instrument dedup (everything but the id and `drop`)."""
    import dataclasses
    skip = {'id'} | set(drop)
    d = {f.name: getattr(inst, f.name) for f in dataclasses.fields(inst)
         if f.name not in skip}
    return repr({k: (tuple(v) if isinstance(v, list) else v)
                 for k, v in d.items()})


def _merge_offtable(a, b):
    """Union two `offtable_freq` record lists `(off, note, lo, hi)`, or None if
    any (off, note) maps to a CONFLICTING (lo, hi). offtable_freq is a
    reachability artifact — which (wave-offset, note) an instrument was actually
    played at (ledger C6), NOT an intrinsic instrument property — so two
    instruments identical in every other field are the SAME instrument played at
    different notes, and the union is lossless: each record fires only for its
    own (off, note), and a record for notes one song never plays is inert there.
    A collision (the same (off, note) read a different byte in the two players'
    freq tables) means they are genuinely distinct -> refuse the merge."""
    by_key = {}
    for off, note, lo, hi in list(a) + list(b):
        k = (off, note)
        if k in by_key and by_key[k] != (lo, hi):
            return None
        by_key[k] = (lo, hi)
    return sorted((off, note, lo, hi)
                  for (off, note), (lo, hi) in by_key.items())


def merge_models(models: list, subtune_map: list, hdr: dict) -> 'em.DmcModel':
    """Merge per-player DmcModels into one unified DmcModel.

    `models[i]` is player i (its `.songs` are that player's own songs).
    `subtune_map[k] = (player_idx, song_idx)` gives the (player, song) for PSID
    subtune k. `hdr` carries title/author/released/clock/sid_model/start_song.
    """
    start = max(0, hdr['start_song'] - 1)
    base_pidx = subtune_map[start][0] if start < len(subtune_map) else 0
    b = models[base_pidx]

    # shared tuning must coincide (freq is per-tune content but a compilation's
    # players are usually the standard DMC tuning; a mismatch is unmergeable).
    for m in models:
        if m.freq_lo != b.freq_lo or m.freq_hi != b.freq_hi:
            raise ValueError('compilation players disagree on the freq table')

    merged = em.DmcModel(
        freq_lo=list(b.freq_lo), freq_hi=list(b.freq_hi),
        vibdepth=list(b.vibdepth),
        offtable_vibdepth=dict(b.offtable_vibdepth),
        filter_defs=dict(b.filter_defs),
        d417_shadow=b.d417_shadow, dual_phase=b.dual_phase,
        cia_period=b.cia_period, play_repeat=b.play_repeat,
        idle_wave=b.idle_wave, idle_notes=b.idle_notes,
        idle_masks=b.idle_masks, idle_guards=b.idle_guards,
        durrel_init=b.durrel_init,
        offtable_canon=b.offtable_canon, wavepos_layout=b.wavepos_layout,
        title=hdr['title'], author=hdr['author'], released=hdr['released'],
        clock=hdr['clock'], sid_model=hdr['sid_model'],
        n_subtunes=len(subtune_map), start_song=hdr['start_song'],
        extra_params=dict(b.extra_params),
    )
    # union off-table vibdepth (freq-table-relative; identical across players)
    for m in models:
        for note, depth in m.offtable_vibdepth.items():
            merged.offtable_vibdepth.setdefault(note, depth)

    # instruments used by each player's MAPPED songs
    used = defaultdict(set)
    for (pidx, sidx) in subtune_map:
        for v in models[pidx].songs[sidx].voices:
            for rows in v.patterns:
                for r in rows:
                    used[pidx].add(r.instr)

    def _played_fdefs(pidx):
        out = set()
        for old in used[pidx]:
            inst = models[pidx].instruments.get(old)
            if inst is not None and inst.filter_on:
                out.add(inst.filter_def)
        return out

    # ---- filter-def window strategy ----
    # Strategy 1 (SHARED WINDOW): non-start players' played defs coincide with
    # the start player's window at the same index -> reuse it VERBATIM (the C2
    # 17-record overrun window is preserved; no instrument def-index remap).
    # Strategy 2 (COMPACT REMAP): on a conflict, dedup every PLAYED def across
    # players into one compact window and remap instrument def-indices. SAFE
    # only when NO played def OVERRUNS (repeat<=5, so the C2 step-index walk
    # stays inside its own record and adjacency is irrelevant) and the distinct
    # count fits the 4-bit def index (<=16). Otherwise unmergeable -> the caller
    # falls back to the single-player path (no regression).
    conflict = any(merged.filter_defs.get(d) != models[pidx].filter_defs.get(d)
                   for pidx in used if pidx != base_pidx
                   for d in _played_fdefs(pidx))
    fd_remap = {}                   # (player_idx, old_def) -> new_def
    if conflict:
        merged.filter_defs = {}
        fdpool = {}                 # def-content key -> new def index
        for pidx in sorted(used):
            for d in sorted(_played_fdefs(pidx)):
                dc = models[pidx].filter_defs.get(d)
                if dc is None:
                    raise ValueError(
                        f'player {pidx} references uncaptured filter def {d}')
                if dc.get('repeat', 0) > 5:
                    raise ValueError(
                        f'player {pidx} filter def {d} overruns (repeat>5) — '
                        f'compact-window adjacency not preservable')
                fk = repr(sorted(dc.items()))
                if fk not in fdpool:
                    fdpool[fk] = len(fdpool)
                    merged.filter_defs[fdpool[fk]] = dict(dc)
                fd_remap[(pidx, d)] = fdpool[fk]
        if len(merged.filter_defs) > 16:
            raise ValueError(
                f'merged filter window {len(merged.filter_defs)} > 16 slots')

    # ---- instruments: remap to one compact pool. Dedup identical instruments
    # (same drum kit shared across players) so many-player members stay under
    # the 5-bit id cap. The dedup key EXCLUDES offtable_freq (a reachability
    # artifact, not intrinsic content); instruments equal in every other field
    # share one merged id carrying the UNION of their offtable_freq records
    # (Principle Rule 1 — cluster by behavior). A record collision refuses the
    # union, so the two land as distinct ids in the same base bucket.
    pool = defaultdict(list)        # base key (no offtable) -> [new_iid, ...]
    remap = defaultdict(dict)       # player_idx -> {old_iid: new_iid}
    for pidx in sorted(used):
        m = models[pidx]
        for old in sorted(used[pidx]):
            inst = m.instruments.get(old)
            if inst is None:
                continue
            ni = copy.deepcopy(inst)
            if conflict and ni.filter_on and (pidx, ni.filter_def) in fd_remap:
                ni.filter_def = fd_remap[(pidx, ni.filter_def)]
            bk = _inst_key(ni, drop=('offtable_freq',))
            placed = None
            for nid in pool[bk]:
                u = _merge_offtable(merged.instruments[nid].offtable_freq,
                                    ni.offtable_freq)
                if u is not None:
                    merged.instruments[nid].offtable_freq = u
                    placed = nid
                    break
            if placed is not None:
                remap[pidx][old] = placed
                continue
            new = len(merged.instruments)
            pool[bk].append(new)
            remap[pidx][old] = new
            ni.id = new
            merged.instruments[new] = ni
    if len(merged.instruments) > _MAX_INSTR:
        raise ValueError(
            f'merged compilation needs {len(merged.instruments)} instruments '
            f'> {_MAX_INSTR} (5-bit id cap)')

    # songs in PSID-subtune order; rewrite each row's instrument to the merged id
    merged.songs = []
    for si, (pidx, sidx) in enumerate(subtune_map):
        song = copy.deepcopy(models[pidx].songs[sidx])
        song.id = si + 1
        rm = remap[pidx]
        for v in song.voices:
            for rows in v.patterns:
                for r in rows:
                    r.instr = rm.get(r.instr, r.instr)
        merged.songs.append(song)
    return merged


def sfx_player_indices(sid_path: str, spec: dict,
                       hvsc_root: str = 'hvsc84') -> list:
    """Player indices in spec['bases'] that are dmc_sfx sub-players (not DMC)."""
    from pipelines.dmc.v4.sfx_engine import is_sfx_player
    mem, _ = em._load_image(os.path.join(hvsc_root, sid_path))
    return [i for i, b in enumerate(spec['bases']) if is_sfx_player(mem, b)]


def extract_compilation(sid_path: str, spec: dict,
                        hvsc_root: str = 'hvsc84') -> 'em.DmcModel':
    """Extract every referenced player and merge into one unified DmcModel."""
    from pipelines.dmc.v4.factory import dmc_v4_config
    from seed_disassembly import parse_psid
    models = [em.extract(dmc_v4_config(sid_path, hvsc_root=hvsc_root,
                                       base_override=base), hvsc_root=hvsc_root)
              for base in spec['bases']]
    s = parse_psid(os.path.join(hvsc_root, sid_path))
    b0 = models[0]
    hdr = {'title': b0.title, 'author': b0.author, 'released': b0.released,
           'clock': b0.clock, 'sid_model': b0.sid_model,
           'start_song': s.get('start', 1)}
    return merge_models(models, spec['map'], hdr)


def extract_heterogeneous(sid_path: str, spec: dict, hvsc_root: str = 'hvsc84'):
    """HETEROGENEOUS compilation (DMC players + a dmc_sfx sub-player, ledger
    C31): extract the DMC players and merge them (DMC subtunes only), extract
    the dmc_sfx player as a typed SfxEngine, and return
    `(dmc_model, sfx_engine, subtune_kinds)` where `subtune_kinds[k]` is
    `('dmc', dmc_subtune_index)` or `('sfx', sfx_song)` for PSID subtune k.
    The composer emits both engines behind a per-subtune dispatcher."""
    from pipelines.dmc.v4.factory import dmc_v4_config
    from pipelines.dmc.v4.sfx_engine import extract_sfx_engine
    from seed_disassembly import parse_psid
    mem, _ = em._load_image(os.path.join(hvsc_root, sid_path))
    bases, mp = spec['bases'], spec['map']
    sfx_idx = set(sfx_player_indices(sid_path, spec, hvsc_root))
    if len(sfx_idx) != 1:
        raise ValueError(f'expected exactly one dmc_sfx player, got {len(sfx_idx)}')
    sfx_base = bases[next(iter(sfx_idx))]
    dmc_idx = [i for i in range(len(bases)) if i not in sfx_idx]
    dmc_pos = {orig: new for new, orig in enumerate(dmc_idx)}

    # how many songs the sfx player exposes: cover every referenced song
    n_songs = max((song for pidx, song in mp if pidx in sfx_idx), default=-1) + 1
    sfx_engine = extract_sfx_engine(mem, sfx_base, max(n_songs, 1))
    # voice_init may reference an instrument slot past the referenced songs
    need = max((v.instrument for v in sfx_engine.voice_init), default=0) + 1
    if need > len(sfx_engine.songs):
        sfx_engine = extract_sfx_engine(mem, sfx_base, need)

    dmc_models = [em.extract(dmc_v4_config(sid_path, hvsc_root=hvsc_root,
                                           base_override=bases[i]),
                             hvsc_root=hvsc_root) for i in dmc_idx]
    dmc_map, subtune_kinds, dmc_ctr = [], [], 0
    for pidx, song in mp:
        if pidx in sfx_idx:
            subtune_kinds.append(('sfx', song))
        else:
            dmc_map.append((dmc_pos[pidx], song))
            subtune_kinds.append(('dmc', dmc_ctr))
            dmc_ctr += 1

    s = parse_psid(os.path.join(hvsc_root, sid_path))
    b0 = dmc_models[0]
    hdr = {'title': b0.title, 'author': b0.author, 'released': b0.released,
           'clock': b0.clock, 'sid_model': b0.sid_model, 'start_song': 1}
    dmc_model = merge_models(dmc_models, dmc_map, hdr)
    return dmc_model, sfx_engine, subtune_kinds, s.get('start', 1)
