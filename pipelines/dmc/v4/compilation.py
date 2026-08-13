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


# A player's reachable code+data all sits within this window of its base; a
# valid init/play vector jumps somewhere inside it. Used as the reloc-invariant
# target-range validator that lets the head predicate drop to TWO JMPs (below)
# without admitting arbitrary `4C .. .. 4C .. ..` byte pairs in data.
# THE player-head predicate lives in engine_model (this module imports it, so
# the shared definition sits on the importable side — round 90's generalisation
# to the two-JMP head originally landed here and MISSED engine_model's stale
# three-JMP duplicate, breaking `_postinit_window(stop_at_player=True)` on
# re-assembled players). Re-exported under the old name for all callers here.
_PLAYER_WIN = em._PLAYER_WIN
_is_player_head = em._is_player_head


def _is_player_base(mem, load: int, a: int) -> bool:
    """`_is_player_head` with the file-image load-address floor (a base named in
    a static file-image table must sit at or above the load address)."""
    return load <= a and _is_player_head(mem, a)


def _is_canon_base_unaligned(mem, load: int, b: int) -> bool:
    """A canonical DMC jump table (`JMP b+$1D` init / `JMP b+$85` play) at `b`
    WITHOUT the page-alignment `_is_player_head` requires — for a base named by
    an EXPLICIT wrapper lo/hi table, where a non-page-aligned base is legitimate
    (Pievspie/Mission_Moon $5E24). The exact-offset canon signature is strict
    enough that a spurious lo/hi pairing cannot validate (both resulting bytes
    would have to form `4C b+1D .. 4C b+85`)."""
    return (load <= b and b + 6 < 0x10000
            and mem[b] == 0x4C and mem[b + 3] == 0x4C
            and (mem[b + 1] | (mem[b + 2] << 8)) == b + 0x1D
            and (mem[b + 4] | (mem[b + 5] << 8)) == b + 0x85)


def detect_compilation(sid_path: str, hvsc_root: str = 'hvsc85'):
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

    # classify the tables: a base table's values point at player bases; a song
    # table's values are small song numbers. The base table is normally a page
    # HI-byte table (base = val<<8). When the bases are NOT page-aligned, the
    # wrapper carries a SEPARATE lo + hi table (Pievspie/Mission_Moon: $5DE4 lo
    # / $5DE6 hi -> $5E24, $5000) — the observe path can't reach those (its
    # `--pc-watch` low-byte gate + page-aligned pre-gate are page-aligned by
    # construction), so PAIR the two `LDA abs,X` tables here and validate every
    # resulting base (a wrong lo/hi assignment fails `_is_player_base`).
    base_tab = song_tab = None
    for t in ldax:
        vals = [mem[(t + x) & 0xFFFF] for x in range(songs)]
        if all(_is_player_base(mem, load, v << 8) for v in vals):
            if base_tab is None:
                base_tab = vals
        elif all(v < 8 for v in vals):
            if song_tab is None:
                song_tab = vals
    full_bases = None
    if base_tab is not None:                       # page-aligned: base = hi<<8
        full_bases = [v << 8 for v in base_tab]
    elif len(ldax) >= 2:                            # non-page-aligned lo/hi pair
        for lo_t in ldax:
            for hi_t in ldax:
                if lo_t == hi_t:
                    continue
                lv = [mem[(lo_t + x) & 0xFFFF] for x in range(songs)]
                hv = [mem[(hi_t + x) & 0xFFFF] for x in range(songs)]
                cand = [lv[x] | (hv[x] << 8) for x in range(songs)]
                if all(_is_canon_base_unaligned(mem, load, b) for b in cand):
                    full_bases = cand
                    break
            if full_bases is not None:
                break
    if full_bases is None:
        return _observe_dispatch_2pass(sid_path, hvsc_root)
    if song_tab is None:
        # single-player-per-subtune dispatch with no song remap: every subtune
        # is song 0 of its selected player.
        song_tab = [0] * songs

    # ordered distinct bases in wrapper first-seen order
    ordered_bases = []
    for b in full_bases:
        if b not in ordered_bases:
            ordered_bases.append(b)
    base_idx = {b: i for i, b in enumerate(ordered_bases)}
    try:
        mp = [(base_idx[full_bases[x]], song_tab[x]) for x in range(songs)]
    except (KeyError, IndexError):
        return _observe_dispatch_2pass(sid_path, hvsc_root)
    # Only a genuine compilation: the dispatch must actually select >=2
    # DISTINCT players. A single-player-with-wrapper (all subtunes -> one base)
    # is handled by the ordinary single-player path — never route it here.
    if len({pidx for pidx, _ in mp}) < 2:
        return _observe_dispatch_2pass(sid_path, hvsc_root)
    return {'bases': ordered_bases, 'map': mp,
            # Which ENGINE each base is (mirrors the observe path's field).
            # A compilation can pack a DMC V5 player beside V4 ones
            # (Super_Tau-Zeta $B400) — its head is `JMP base+$40 (init) /
            # JMP base+$A1 (play)`, distinct from every V4 layout, so the
            # play vector is the discriminator. 'dmc' | 'dmcv5'.
            'kinds': [_base_kind(mem, b) for b in ordered_bases]}


# ---------------------------------------------------------------------------
# TIME-MEDLEY detection (ledger C31, medley variant — Praiser/Mega_Mix)
# ---------------------------------------------------------------------------
# A time-sequenced medley packs >=2 canonical DMC players and, unlike a C31
# compilation (per-subtune dispatch on the INIT vector), TIME-switches between
# them from the PLAY vector: the play vector points at a wrapper that runs a
# 2-byte frame countdown, double-plays the ACTIVE player, and on countdown
# expiry JSRs a per-segment re-init routine that inits the next player and
# reloads the counter. One PSID song; a full cycle loops. Reproduced by the
# composer's gated `playmedley` wrapper (params.fields['medley']).


def _parse_reinit(mem, load: int, r: int):
    """Parse a medley segment RE-INIT routine at `r`:

        LDA #song                    ; A9 song
        JSR player_base              ; 20 ll hh   (canonical DMC jump table)
        (LDA #imm / STA zp) x3        ; the two counter bytes + the segment flag
        RTS                          ; 60

    Returns {'song', 'base', 'stores': [(zp, imm), ...]} or None. Which store is
    counter-lo / counter-hi / seg-flag is decided by the WRAPPER (which byte it
    DECs first), so the raw ordered stores are returned here."""
    if mem[r] != 0xA9:                       # LDA #song
        return None
    song = mem[r + 1]
    if mem[r + 2] != 0x20:                    # JSR base
        return None
    base = mem[r + 3] | (mem[r + 4] << 8)
    if not _is_canon_base_unaligned(mem, load, base):
        return None
    p = r + 5
    stores = []
    for _ in range(6):                        # bounded: expect exactly 3
        if mem[p] == 0xA9 and mem[p + 2] == 0x85:   # LDA #imm / STA zp
            stores.append((mem[p + 3], mem[p + 1]))
            p += 4
        elif mem[p] == 0x60:                  # RTS
            break
        else:
            return None
    if mem[p] != 0x60 or len(stores) != 3:
        return None
    return {'song': song, 'base': base, 'stores': stores}


def _parse_medley_wrapper(mem, w: int):
    """Parse the play-vector wrapper at `w`. Returns
    {'lo': zp, 'hi': zp, 'seg': zp, 'play_repeat': N, 'reinits': [addr, ...]}
    or None. The wrapper DECs the counter-lo byte first, the counter-hi byte on
    lo-wrap, dispatches on a segment flag, double-plays the active player
    (`JSR base+3` x N), and JSRs a re-init on expiry."""
    decs = []          # zp addrs DEC'd, in order (lo then hi)
    lda_zp = []        # zp addrs LDA'd
    jsr_tgts = []      # JSR targets
    p = w
    for _ in range(96):
        op = mem[p]
        if op == 0xC6:                        # DEC zp
            decs.append(mem[p + 1]); p += 2
        elif op == 0xA5:                      # LDA zp
            lda_zp.append(mem[p + 1]); p += 2
        elif op == 0x20:                      # JSR abs
            jsr_tgts.append(mem[p + 1] | (mem[p + 2] << 8)); p += 3
        elif op == 0x60:                      # RTS — wrapper ended
            break
        elif op in (0xC9, 0xA9, 0xD0, 0xF0, 0x10, 0x30, 0x90, 0xB0, 0x85):
            p += 2                             # imm / branch / STA zp
        elif op in (0x4C, 0x8D, 0xAD, 0xBD, 0x9D):
            p += 3
        elif op in (0xAA, 0xA8, 0x8A, 0x98, 0xE8, 0xCA, 0xEA, 0x18, 0x38):
            p += 1
        else:
            p += 1
    if len(decs) < 2:
        return None
    lo_addr, hi_addr = decs[0], decs[1]
    seg_cands = [z for z in lda_zp if z not in (lo_addr, hi_addr)]
    if not seg_cands:
        return None
    seg_addr = seg_cands[0]
    return {'lo': lo_addr, 'hi': hi_addr, 'seg': seg_addr,
            'jsr_tgts': jsr_tgts}


def detect_medley(sid_path: str, hvsc_root: str = 'hvsc85'):
    """Return a time-medley spec or None.

    Spec: {'bases':     [b0, b1, ...],          # distinct player bases
           'segments':  [(base_idx, song, lo, hi), ...],  # schedule order
           'play_repeat': N,                     # inner plays per PSID play()
           'kinds':     ['dmc', ...]}

    None when the file is not a time-medley (the overwhelmingly common case).
    Detection is STATIC on the rigid wrapper/re-init shape, and validated end to
    end by build+verify (a false detection cannot false-FULL — the merged build
    diverges, ledger C13). Distinct from `detect_compilation` (INIT-vector
    per-subtune dispatch) and 2SID (parallel chips): a medley switches players
    on the PLAY vector over a frame countdown and exposes ONE PSID song."""
    mem, s = em._load_image(os.path.join(hvsc_root, sid_path))
    load = s['load']
    if s.get('songs', 1) != 1:                # a medley presents as one song
        return None

    wrap = _follow_jmps(mem, s['play'])
    info = _parse_medley_wrapper(mem, wrap)
    if info is None:
        return None

    # Re-init routines: the cold init (init vector) + every wrapper JSR target
    # that parses as a re-init. Each yields one segment.
    r0 = _follow_jmps(mem, s['init'])
    cand = [r0] + info['jsr_tgts']
    seen, reinits = set(), []
    for r in cand:
        if r in seen:
            continue
        seen.add(r)
        if _parse_reinit(mem, load, r) is not None:
            reinits.append(r)
    if len(reinits) < 2:
        return None

    # Which store is lo / hi / seg-flag: keyed by the wrapper's DEC'd addresses.
    lo_a, hi_a, seg_a = info['lo'], info['hi'], info['seg']
    segs = {}                                  # seg flag -> (base, song, lo, hi)
    for r in reinits:
        pr = _parse_reinit(mem, load, r)
        sd = dict(pr['stores'])
        if not (lo_a in sd and hi_a in sd and seg_a in sd):
            return None
        segs[sd[seg_a]] = (pr['base'], pr['song'], sd[lo_a], sd[hi_a])

    order = sorted(segs)
    if order != list(range(len(order))) or len(order) < 2:
        return None                            # seg flags must be a dense 0..n-1

    bases_seq = [segs[i][0] for i in order]
    distinct = []
    for b in bases_seq:
        if b not in distinct:
            distinct.append(b)
    if len(distinct) < 2:                       # must select >=2 DISTINCT players
        return None
    bidx = {b: i for i, b in enumerate(distinct)}

    # play_repeat = inner plays per PSID play() = JSR base+3 count for one player.
    play3 = [distinct[0] + 3]
    play_repeat = sum(1 for t in info['jsr_tgts'] if t in play3)
    if play_repeat < 1:
        return None

    segments = [(bidx[segs[i][0]], segs[i][1], segs[i][2], segs[i][3])
                for i in order]
    return {'bases': distinct, 'segments': segments,
            'play_repeat': play_repeat,
            'kinds': [_base_kind(mem, b) for b in distinct]}


def _base_kind(mem, b: int) -> str:
    """Engine kind of a detected player base (works on the file image OR a
    post-init RAM view): 'dmcv5' when the play vector (+3) targets base+$A1
    (the V5 family-3 play-body offset) or base+$95 with init at base+$40
    (the V5 family-4 / Jupiter41 layout — Black_It's relocated $1000
    player). V4 layouts use +$85 / +$50, so neither test can fire on one.
    Else 'dmc' (V4)."""
    it = mem[b + 1] | (mem[b + 2] << 8)
    pt = mem[b + 4] | (mem[b + 5] << 8)
    if pt == b + 0xA1:
        return 'dmcv5'
    if it == b + 0x40 and pt == b + 0x95:
        return 'dmcv5'
    return 'dmc'


def _is_player_base_ram(mem, a: int) -> bool:
    """`_is_player_base` without the load-address floor — for a base observed
    in RAM. A RELOCATING wrapper can copy a player BELOW the load address
    (Pour_le_merite loads at $8000 and copies its second player down to
    $1000), where the file-image floor is exactly the wrong test."""
    return _is_player_head(mem, a)


# Music Assembler's cold-start entry. Its base carries NO three-JMP head
# (`78 20 .. .. A9 18 ...` = SEI / JSR / IRQ install), so the DMC signature
# above can never see it; the reloc-invariant anchor is init's fixed prefix
# at base+$48 — `LDA #$1F / STA $D418 / LDA #$F0 / STA $D417`, measured at
# that offset on all 5,618 members that locate (see pipelines/music_assembler
# /locate.py).
_MASM_INIT_PREFIX = bytes((0xA9, 0x1F, 0x8D, 0x18, 0xD4,
                           0xA9, 0xF0, 0x8D, 0x17, 0xD4))
_MASM_INIT_OFS = 0x48


def _is_masm_base_ram(mem, a: int) -> bool:
    """Is `a` a Music Assembler player base, as observed in RAM?"""
    if not (0 < a and a + _MASM_INIT_OFS + len(_MASM_INIT_PREFIX) < 0x10000):
        return False
    return all(mem[a + _MASM_INIT_OFS + i] == b
               for i, b in enumerate(_MASM_INIT_PREFIX))


# --- ground-truth landing observation (siddump --pc-watch) -----------------
# Phase 2 of docs/siddump_native_capture_plan.md: the dispatch observation
# runs under libsidplayfp instead of py65 (feedback_ground_truth.md). The
# relative window [pc-$48, pc+$58] covers every predicate read: DMC head
# (pc..pc+5), MA prefix (b+$48..b+$51 = pc..pc+9 with b = pc-$48), _base_kind
# (b+1..b+5).

_PCW_BEFORE = 0x48
_PCW_AFTER = 0x58


class _WinView:
    """mem-like view over one --pc-watch event's pc-relative RAM window.
    Out-of-window reads return 0 — safe for the landing predicates, which
    all require specific nonzero bytes ($4C heads / the MA prefix)."""

    def __init__(self, pc: int, win: bytes):
        self.base = pc - _PCW_BEFORE
        self.win = win

    def __getitem__(self, a: int) -> int:
        i = a - self.base
        return self.win[i] if 0 <= i < len(self.win) else 0


def _pc_watch_landings(abs_path: str, sub: int):
    """Ordered executed-PC events for one subtune from `siddump --pc-watch`:
    [(pc, a, relwin bytes)] for every first-time PC with low byte $00 or $48
    (the two landing shapes), in execution order. Events are NOT filtered to
    init: the true landing is chronologically first, and filtering by
    play-index would mis-drop it on a member whose init copy-loop READS the
    play vector address as data (the play counter is a cpuRead proxy).
    Returns None when siddump fails."""
    import subprocess
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', '..', '..'))
    siddump = os.path.join(repo, 'tools', 'siddump')
    try:
        out = subprocess.run(
            [siddump, abs_path, '--pc-watch', '*00,*48',
             '%X-%X' % (_PCW_BEFORE, _PCW_AFTER), '--pc-watch-first',
             '--subtune', str(sub + 1), '--duration', '2'],
            capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    events = []
    for line in out.stdout.splitlines():
        pos = 0
        while True:
            pos = line.find('|PW:', pos)
            if pos < 0:
                break
            fields = line[pos + 4:].split(':', 6)
            if len(fields) < 7:
                break
            pc, a = int(fields[0], 16), int(fields[1], 16)
            rel = bytes.fromhex(fields[5].split('|', 1)[0])
            events.append((pc, a, rel))
            pos += 4
    return events


def _observe_dispatch(sid_path: str, hvsc_root: str = 'hvsc85',
                      allow_masm: bool = False):
    """Discover the per-subtune (player, song) map by RUNNING the wrapper —
    under libsidplayfp (`siddump --pc-watch`), the GROUND-TRUTH engine.

    The static decode above reads the wrapper's `LDA abs,X` tables assuming
    X *is* the subtune number and that the base table holds page HI-bytes
    only. Wrapper shapes vary (Defuzion_3 SCALES the index and patches full
    lo/hi VECTOR PAIRS), so per C18/C27 the cure is to OBSERVE rather than
    teach the parser one more shape: run the member's own init with
    A = subtune (one siddump invocation per subtune — the dispatch is SMC,
    and a fresh process is a fresh image) and replay the landing predicates
    over the executed-PC event stream, in execution order. The landing is
    the selected player base and the event's A is the song number that
    player is initialised with. Events are execution-discriminated (a data
    read of a page-aligned address cannot fire one — ledger C36) and carry
    the RAM window the predicates need, captured AT the landing — a
    relocated player exists only in RAM (Black_It materialises $1000).

    Runs only as a LATER pass (the static decode wins whenever it
    resolves), pre-gated so an ordinary single-player member never pays for
    the observation. Two gates, either of which admits a member:

      (a) the file image already carries >=2 page-aligned player bases —
          the co-packed compilation (Defuzion_3, Canyon);
      (b) it carries >=1, and the PSID init vector does NOT lead into any
          of them — the RELOCATING compilation, whose wrapper COPIES a
          player into RAM per subtune (Super_Seven, Pour_le_merite,
          Black_It, Freespace_2075).

    A base the file image does not carry is recorded in the returned spec's
    `reloc` map as {base: subtune}, naming the subtune whose init
    materialises it — every later memory read for that player must use that
    subtune's post-init RAM instead of the image (ledger C31 + C26).

    Migrated from py65 2026-07-25 (Phase 2 of
    docs/siddump_native_capture_plan.md); gate = spec-identity on the five
    observe-path members + dmc_smoke + regression.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    try:
        from seed_disassembly import parse_psid
    except ImportError:
        return None
    abs_path = os.path.join(hvsc_root, sid_path)
    try:
        s = parse_psid(abs_path)
    except Exception:
        return None

    # Never speak for a MULTI-SID member (C27) — observation alone cannot
    # tell a per-subtune chip gate from a compilation; the PSID header's
    # chip count is the authoritative discriminator.
    from pipelines.dmc.v4.factory import _sid_header_multi
    if _sid_header_multi(abs_path)[0] > 1:
        return None

    load, songs = s['load'], s.get('songs', 1)
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if load + i < 0x10000:
            img[load + i] = b

    # Pre-gate (see the docstring): >=2 packed players, or >=1 plus an init
    # vector that runs a wrapper first. Cheap page-aligned scan of the file
    # image; bail before observing when the member can't be either.
    hi = min(0x10000, load + len(s['payload']))
    in_image = [a for a in range((load + 0xFF) & ~0xFF, hi, 0x100)
                if _is_player_base(img, load, a)]
    if not in_image:
        return None
    if len(in_image) < 2:
        # 0x900 covers the canonical player extent ($1000-$18E8): an init
        # vector inside one of them is the player's own entry, not a wrapper.
        entry = _follow_jmps(img, s['init'])
        if any(b <= entry < b + 0x900 for b in in_image):
            return None

    obs, reloc, kinds = [], {}, {}
    for sub in range(songs):
        events = _pc_watch_landings(abs_path, sub)
        if not events:
            return None
        landed = None
        for pc, a, rel in events:
            # The wrapper's own entry can itself be page-aligned, so never
            # accept the address we started from as the landing.
            if pc == s['init']:
                continue
            view = _WinView(pc, rel)
            if not (pc & 0xFF) and _is_player_base_ram(view, pc):
                landed = (pc, a)
                # classify at the LANDING, on the RAM view captured there.
                kinds[pc] = _base_kind(view, pc)
                break
            # Music Assembler is entered at its INIT (base+$48), never at
            # the page-aligned base. It carries no song number in A (the
            # accumulator is leftover from the wrapper's copy loop): each
            # packed MA player is one tune, so the song is always 0.
            if allow_masm:
                b = pc - _MASM_INIT_OFS
                if b > 0 and not (b & 0xFF) and _is_masm_base_ram(view, b):
                    landed = (b, 0)
                    kinds[b] = 'masm'
                    break
        if landed is None:
            return None
        obs.append(landed)
        # A base absent from the file image was COPIED there by this
        # subtune's init; remember which subtune materialises it.
        if not _is_player_base(img, load, landed[0]):
            reloc.setdefault(landed[0], sub)

    ordered_bases = []
    for b, _ in obs:
        if b not in ordered_bases:
            ordered_bases.append(b)
    if len(ordered_bases) < 2:
        return None
    idx = {b: i for i, b in enumerate(ordered_bases)}
    return {'bases': ordered_bases,
            'map': [(idx[b], song) for b, song in obs],
            'reloc': reloc,
            # Which ENGINE each base is, recorded where it is actually known
            # (at the landing). 'dmc' | 'dmcv5' | 'masm'.
            'kinds': [kinds.get(b, 'dmc') for b in ordered_bases]}


def _observe_dispatch_2pass(sid_path: str, hvsc_root: str = 'hvsc85'):
    """Observe with DMC landings only, then RETRY admitting Music Assembler
    landings if that found nothing.

    A LATER PASS, exactly like the JSR-only/JMP-inclusive retry this module
    already does (ledger C31): a member that resolves on the first pass keeps
    its existing spec byte-for-byte, so broadening the landing predicate is
    zero-regression by construction. Only members that currently detect as
    NOTHING can change — which is what a heterogeneous DMC+MA compilation
    (Freespace_2075) does today, since its two MA sub-players carry no
    three-JMP head and the observation loop never accepts a landing on them.
    """
    return (_observe_dispatch(sid_path, hvsc_root)
            or _observe_dispatch(sid_path, hvsc_root, allow_masm=True))


# ---------------------------------------------------------------------------
# Merge N per-player models into one unified model
# ---------------------------------------------------------------------------

# Merged-pool cap — measured on OUR composer, not on the original editor.
#
# The ORIGINAL DMC stream selects an instrument with a 5-bit id ($60+id, id
# 0-27 -> $60-$7B; $7C-$7F special), and this cap was 28 because of it. But the
# composer emits its OWN pattern encoding (composer_asm: parallel arrays, the
# slot rides a full operand byte after the event flags), so the orig's 5-bit
# field binds nothing here — inheriting its limit refused members our engine
# can play (core tenet: the orig's format is a historical artifact).
#
# The composer's OWN binding index is fx_pulse's pulse-step lookup into
# isteps/irawsp, an 8-bit index. It has two regimes (composer_asm `wide_pulse`,
# gated so members that fit the first emit byte-identical code):
#   <= 32  `lda cinst,x / asl asl asl / adc pwphase,x` — id*8 + pwphase <= 255
#          with canon pwphase 0-5.
#   <= 42  a compact stride-6 pool with a per-instrument base byte
#          (`lda istepbase,y`) — 41*6 + 5 = 251.
# Audit that chain (and any other id-scaled table) before raising this again.
_MAX_INSTR = 42


def _fd_window(fd: dict) -> list:
    """The composer's 16-byte-per-record filter-def window, dense in def# order
    (`fdrec` in composer_asm): [res<<4|mode, init, repeat, stop, size*6, dur*6].
    The filter step-walk indexes into this (fdstep = +4, fddur = +10), so an
    overrunning def reads adjacent records' bytes from it (C2)."""
    out = []
    for d in range(max(fd) + 1 if fd else 0):
        dc = fd.get(d) or {'res': 0, 'mode': 0, 'init': 0, 'repeat': 0,
                           'stop': 0, 'steps': []}
        steps = (list(dc.get('steps', [])) + [(0, 0)] * 6)[:6]
        out += ([((dc['res'] << 4) | (dc['mode'] & 0x0F)) & 0xFF,
                 dc['init'] & 0xFF, dc['repeat'] & 0xFF, dc['stop'] & 0xFF]
                + [s & 0xFF for s, _ in steps] + [f & 0xFF for _, f in steps])
    return (out + [0] * 272)[:272]


def _walk_filter(fd: dict, deff: int, _cap: int = 400000):
    """Simulate the composer's `fx_filter` step-walk for def `deff` exactly
    (composer_asm.py:2481). Returns `(maxoff, overran, settled)`:
      maxoff  — furthest `fdrec` byte offset read (fddur = fdrec+10+y),
      overran — the step index advanced to >=6 with repeat>5, so the walk
                leaves its own 16-byte record into adjacent ones (C2),
      settled — the walk reached fstop (fcut==fstop) within `_cap` iterations.

    A def OVERRUNS iff `overran` — which is NOT `repeat > 5`: a def whose
    reached step has duration 0 stays pinned on that step (the
    `inc fframe / cmp fdu` advance never fires) and never leaves its record no
    matter how large `repeat` is (Quad_Core player 1 def 1: repeat=8, pinned on
    step 0, settles in-record). A looping def (repeat<=5) wraps within steps
    0..5 and never overruns even when it never settles."""
    rec = _fd_window(fd)
    s8 = lambda v: v - 256 if v >= 128 else v          # noqa: E731
    fbase = (16 * deff) & 0xFF
    fstep = 0
    frep = rec[16 * deff + 2]
    fcut = rec[16 * deff + 1]
    fstop = rec[16 * deff + 3]
    fframe = 0
    maxoff = 16 * deff + 15
    overran = False
    for _ in range(_cap):
        if fcut == fstop:
            return maxoff, overran, True
        y = (fbase + fstep) & 0xFF
        maxoff = max(maxoff, 10 + y)                   # fddur read = fdrec+10+y
        fsz = rec[4 + y]
        fdu = rec[10 + y]
        fcut = (fcut + s8(fsz)) & 0xFF
        fframe = (fframe + 1) & 0xFF
        if fframe == fdu:
            fframe = 0
            fstep += 1
            if fstep == 6:
                if frep > 5:
                    overran = True
                fstep = frep
    return maxoff, overran, False


def _def_overruns(fd: dict, deff: int) -> bool:
    """Does def `deff`'s filter walk actually read OUTSIDE its own 16-byte
    record? repeat<=5 always wraps in-record (fast path); otherwise the walk
    decides — a large `repeat` pinned by a dur-0 step does NOT overrun."""
    if (fd.get(deff) or {}).get('repeat', 0) <= 5:
        return False
    return _walk_filter(fd, deff)[1]


def _overrun_reach(fd: dict, deff: int) -> int:
    """The furthest `fdrec` byte offset def `deff`'s walk reads, or 272 (past
    the window -> caller refuses the merge) if a genuine overrun never settles
    and the reach can't be bounded."""
    maxoff, overran, settled = _walk_filter(fd, deff)
    return maxoff if (settled or not overran) else 272


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


def _overrun_anchored_window(merged, models, used, played_fn, genuine, fd_remap):
    """Strategy 3 — lay out a merged filter window that preserves a GENUINE
    cross-record overrun's byte adjacency.

    Exactly one player may hold genuinely-overrunning played defs (its window's
    trailing records ARE the overrun content, C2). Ship that player's records
    0..R VERBATIM at their native indices (R = the furthest record its played
    overruns reach), then place every OTHER player's played defs — all of which
    are compact-safe here (a second overrunning player would conflict for the
    low indices) — in the free slots R+1..15 the overrun never touches. The
    overrunning player's own played defs keep their native index.

    Refuses (ValueError -> caller falls back to single-player) when two players
    overrun, when R fills the walk space, or when the window exceeds 16 slots."""
    overp = {pidx for pidx, _ in genuine}
    if len(overp) != 1:
        raise ValueError(
            f'{len(overp)} players hold cross-record filter overruns — '
            f'only a single overrunning player is anchorable')
    op = next(iter(overp))
    opfd = models[op].filter_defs
    reach = max(_overrun_reach(opfd, d) for (p, d) in genuine)
    R = reach // 16
    if R >= 16:
        raise ValueError(f'overrun reaches record {R} — fills the 16-slot walk')

    merged.filter_defs = {}
    for idx in range(R + 1):        # op window verbatim (played + filler records)
        dc = opfd.get(idx)
        if dc is None:
            raise ValueError(f'overrun window record {idx} missing from player {op}')
        merged.filter_defs[idx] = dict(dc)
    for d in played_fn(op):
        fd_remap[(op, d)] = d       # op's own played defs stay at native index

    fdpool = {repr(sorted(merged.filter_defs[i].items())): i
              for i in merged.filter_defs}     # reuse an identical anchored rec
    nxt = R + 1
    for pidx in sorted(used):
        if pidx == op:
            continue
        for d in sorted(played_fn(pidx)):
            dc = models[pidx].filter_defs.get(d)
            if dc is None:
                raise ValueError(
                    f'player {pidx} references uncaptured filter def {d}')
            if _def_overruns(models[pidx].filter_defs, d):
                raise ValueError(
                    f'player {pidx} def {d} also overruns — unanchorable')
            fk = repr(sorted(dc.items()))
            if fk not in fdpool:
                if nxt > 15:
                    raise ValueError('merged filter window > 16 slots')
                fdpool[fk] = nxt
                merged.filter_defs[nxt] = dict(dc)
                nxt += 1
            fd_remap[(pidx, d)] = fdpool[fk]


def merge_models(models: list, subtune_map: list, hdr: dict) -> 'em.DmcModel':
    """Merge per-player DmcModels into one unified DmcModel.

    `models[i]` is player i (its `.songs` are that player's own songs).
    `subtune_map[k] = (player_idx, song_idx)` gives the (player, song) for PSID
    subtune k. `hdr` carries title/author/released/clock/sid_model/start_song.
    """
    from pipelines.dmc.composer_asm import _inst_offset   # ioff carry chain
    start = max(0, hdr['start_song'] - 1)
    base_pidx = subtune_map[start][0] if start < len(subtune_map) else 0
    b = models[base_pidx]

    # Tuning is PER-TUNE musical content (the principle's C7 category C), so
    # packed players may legitimately disagree — the merge used to refuse the
    # whole member here, which sent it to the single-player fallback and built
    # every non-start subtune from the WRONG player's data. It now carries the
    # disagreement per-subtune (below, beside idle_wave / d417_shadow /
    # dual_phase), and the start player's table stays the file-level one so
    # every agreeing member emits byte-identically.
    tuning_differs = any(m.freq_lo != b.freq_lo or m.freq_hi != b.freq_hi
                         for m in models)

    # The VIBDEPTH sibling (ledger C31): each player's captured
    # offtable_vibdepth ({note: depth} — reached in-table deviations +
    # off-table window reads) is measured against ITS OWN memory (the
    # code-overlap head operand relocates with the base; the off-table window
    # lands in the player's own state block), so two players can disagree on
    # a note. The union below keeps first-wins for the file-level table;
    # conflicting notes additionally ride per-subtune (each subtune gets its
    # own player's value, emitted only where it differs from the file-level
    # one). Census 2026-08-10: 22 compilations disagree on SOME vibdepth
    # byte, but only 4 on a REACHED note (Defuzion_3, Goldrake_plus_2,
    # Lane_Crazy, Quad_Core) — all currently unsonified (FULL), so this
    # closes the silent collapse rather than buying coverage.
    vib_conflict = sorted({
        n for i, m in enumerate(models)
        for n, d in m.offtable_vibdepth.items()
        for m2 in models[i + 1:]
        if n in m2.offtable_vibdepth and m2.offtable_vibdepth[n] != d})

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
    # players into one compact window and remap instrument def-indices. A def
    # can be freely relocated iff its step-walk stays INSIDE its own 16-byte
    # record (adjacency then irrelevant) — which is NOT the same as `repeat<=5`:
    # a large `repeat` pinned by a dur-0 first step also stays in-record
    # (`_def_overruns`, the exact `fx_filter` walk). Only a GENUINE cross-record
    # overrun blocks the compact path; that goes to strategy 3. The distinct
    # count must fit the composer's 8-bit `16*def#` step-walk index (<=16).
    conflict = any(merged.filter_defs.get(d) != models[pidx].filter_defs.get(d)
                   for pidx in used if pidx != base_pidx
                   for d in _played_fdefs(pidx))
    fd_remap = {}                   # (player_idx, old_def) -> new_def
    if conflict:
        genuine = {(pidx, d) for pidx in used for d in _played_fdefs(pidx)
                   if _def_overruns(models[pidx].filter_defs, d)}
        if genuine:
            _overrun_anchored_window(merged, models, used, _played_fdefs,
                                     genuine, fd_remap)
        else:
            merged.filter_defs = {}
            fdpool = {}             # def-content key -> new def index
            for pidx in sorted(used):
                for d in sorted(_played_fdefs(pidx)):
                    dc = models[pidx].filter_defs.get(d)
                    if dc is None:
                        raise ValueError(
                            f'player {pidx} references uncaptured filter def {d}')
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
    # the `_MAX_INSTR` cap. The dedup key EXCLUDES offtable_freq (a reachability
    # artifact, not intrinsic content); instruments equal in every other field
    # share one merged id carrying the UNION of their offtable_freq records
    # (Principle Rule 1 — cluster by behavior). A record collision refuses the
    # union, so the two land as distinct ids in the same base bucket.
    # RECORD 0 FIRST. The engine's note-init cache is init-cleared to 0, so a
    # voice idling before its first note runs instrument record 0's pulse/wave
    # mechanism (RE_NOTES "idle-note voice_state priming") — which is why the
    # single-player extract force-includes record 0 as USF slot 0. The merge
    # rebuilds the pool from ROW-referenced instruments only, so record 0 lost
    # that slot and every idling voice ran whichever instrument happened to
    # sort first (Defuzion_3 sub 3: V3's track is a bare $FE stop, so it idles
    # the whole song and wrote PW lo $00 where the orig writes $40). Seeding
    # the pool with the start player's record 0 restores the invariant; the
    # dedup collapses it into an identical row-referenced instrument, so a
    # member whose record 0 is already played keeps its exact pool size.
    placements = [(base_pidx, 0)] + [(pidx, old) for pidx in sorted(used)
                                     for old in sorted(used[pidx])]

    def _place(relax: set) -> 'tuple[dict, dict] | None':
        """One placement pass. `relax` = player indices whose instruments'
        POSITIONAL fields are DROPPED from the dedup key (and nulled):
        record_offset (sonified by ioff reads, idx 166-168), wave_start and
        wave_pool_pos (sonified by wavepos reads, fhi idx 211-213 — and
        wave_start is inert in compilation emission anyway: the merged model
        never carries wave_table_norm, so to_usf emits resolved-copy form).
        A relaxed player's subtunes carry NO position-sonifying read, so per
        the Principle Rule 1 the table position is NOT part of its
        instruments' behavior — identical resolved programs may share a slot
        regardless of where they sat in their players' tables (the
        Lane_Crazy r179 over-split: phase-4 positional identity kept
        near-identical kits distinct, 44 > the 42 cap).
        Returns (instruments, remap) or None when the cap overflows."""
        insts: dict = {}
        pool = defaultdict(list)    # base key (no offtable) -> [new_iid, ...]
        remap_ = defaultdict(dict)  # player_idx -> {old_iid: new_iid}
        for pidx, old in placements:
            inst = models[pidx].instruments.get(old)
            if inst is None:
                continue
            ni = copy.deepcopy(inst)
            if conflict and ni.filter_on and (pidx, ni.filter_def) in fd_remap:
                ni.filter_def = fd_remap[(pidx, ni.filter_def)]
            # The ioff a note sonifies (off-table read idx 166-168) is the
            # ORIG player-local record offset (inst# * 11), NOT the merged
            # slot's. Stamp it so it (a) rides the dedup KEY — two players'
            # identical instruments at different table positions sonify
            # different ioff and must NOT share — and (b) survives the
            # renumber (ledger C31/C11, the ioff analog of idle_wave).
            # A `relax`ed player's position is unobservable — no stamp,
            # and the wave-position fields are nulled out of the key too.
            ni.record_offset = (None if pidx in relax
                                else _inst_offset(old))
            if pidx in relax:
                ni.wave_start = None
                ni.wave_pool_pos = None
            bk = _inst_key(ni, drop=('offtable_freq',))
            placed = None
            for nid in pool[bk]:
                u = _merge_offtable(insts[nid].offtable_freq,
                                    ni.offtable_freq)
                if u is not None:
                    insts[nid].offtable_freq = u
                    placed = nid
                    break
            if placed is not None:
                remap_[pidx][old] = placed
                continue
            new = len(insts)
            pool[bk].append(new)
            remap_[pidx][old] = new
            ni.id = new
            # keep the orig offset ONLY when the renumber actually moved it —
            # a non-renumbered instrument derives the same value from its
            # position, so leaving it None keeps the emitted image
            # byte-identical to the pre-fix build.
            if ni.record_offset == _inst_offset(new):
                ni.record_offset = None
            insts[new] = ni
        # Capacity (mirrors composer_asm's pulse-step layouts, ledger C8):
        # <= 42 instruments fit the dense layouts; above that the composer
        # POOLS deduped 6-byte step blocks (2026-08-04, Lane_Crazy), so the
        # bound becomes DISTINCT step blocks <= 42 with the instrument count
        # free to 255 (cinst is a byte). Block key mirrors the composer's
        # padding exactly (speed_steps or [speed]*6, last entry repeated).
        if len(insts) <= _MAX_INSTR:
            return insts, remap_
        if len(insts) > 255:
            return None
        blocks = set()
        for i_ in insts.values():
            ss = list(i_.pw_steps) or [0] * 6
            blocks.add(tuple((ss + [ss[-1]] * 6)[:6]))
        return None if len(blocks) > _MAX_INSTR else (insts, remap_)

    # BEHAVIORAL IDENTITY IS THE DEFAULT KEY (2026-08-04, user decision after
    # the r180 canon re-assessment; Principle §6 Rule 1 — cluster by
    # behavior, not by storage layout). Positional fields (record_offset,
    # wave_start, wave_pool_pos) ride the dedup key ONLY for players whose
    # subtunes can actually sonify a table position: the ioff window
    # (166-168) or the wavepos window (fhi idx 211-213, $177A-$177C). A
    # player with no read into either window cannot observe where its
    # instruments sat — identical resolved programs share a slot regardless.
    # (History: r149 stamped record_offset unconditionally, phase-4 added
    # wave_start — the accumulated over-splitting pushed Lane_Crazy past the
    # instrument cap and silently degraded it to a single-player build; the
    # relax was first an overflow-only retry, promoted to the default with a
    # full re-verify of every merge_models member.)
    _POS_WIN = {166, 167, 168} | {(0x177A + k) - 0x16A7 for k in range(3)}
    flagged = {pidx for pidx in range(len(models))
               if any((rec[0] + rec[1]) & 0xFF in _POS_WIN
                      for i_ in models[pidx].instruments.values()
                      for rec in (i_.offtable_freq or []))}
    result = _place(set(range(len(models))) - flagged)
    if result is None:
        raise ValueError(
            f'merged compilation needs > {_MAX_INSTR} distinct pulse-step '
            f'blocks or > 255 instruments even under behavioral identity '
            f'(ledger C8 — the next widening is a 16-bit index)')
    merged.instruments, remap = result

    # songs in PSID-subtune order; rewrite each row's instrument to the merged id
    merged.songs = []
    for si, (pidx, sidx) in enumerate(subtune_map):
        song = copy.deepcopy(models[pidx].songs[sidx])
        song.id = si + 1
        # each subtune idles on ITS OWN player's work-file leftovers, not the
        # start player's (Defuzion_3's three players prime curnote 0/0/48)
        song.idle_notes = tuple(models[pidx].idle_notes)
        song.idle_masks = tuple(models[pidx].idle_masks)
        song.durrel_init = tuple(models[pidx].durrel_init)
        # ...and on its own player's idle wave program (wave-table pos 0). The
        # file-level `idle_wave` above is the START player's; a packed player
        # whose wave table differs at pos 0 makes its subtunes' idle voices
        # walk a different lead-in wave (Mission_Moon sub 1). model_to_usf
        # emits a per-subtune override only where it differs, so agreement
        # keeps the emitted image byte-identical.
        song.idle_wave = models[pidx].idle_wave
        # ...and on its own player's $D417 routing leftover (§4.2 priming).
        song.d417_shadow = models[pidx].d417_shadow
        # ...and its own player's half-rate slide-clock phase ($1019
        # leftover; None when it matches the merged file-level value so
        # single-phase members emit nothing).
        if (models[pidx].dual_phase or 0) != (models[0].dual_phase or 0):
            song.dual_phase = models[pidx].dual_phase or 0
        # ...and its own player's TUNING, when the packed players disagree.
        # Set only on the subtunes whose table actually differs from the
        # file-level (start player's) one, so an agreeing member carries
        # nothing and model_to_usf emits no override.
        if tuning_differs and (models[pidx].freq_lo != b.freq_lo
                               or models[pidx].freq_hi != b.freq_hi):
            song.freq_lo = list(models[pidx].freq_lo)
            song.freq_hi = list(models[pidx].freq_hi)
        # ...and its own player's value for every CONFLICTING vibdepth-read
        # note (see vib_conflict above). Only notes where this player's value
        # differs from the merged file-level one are carried — the composer's
        # patch writes every conflicting note on every init, falling back to
        # the file-level value for notes a subtune doesn't override, so a
        # subtune change can't inherit its predecessor's patch.
        vd = {n: models[pidx].offtable_vibdepth[n] for n in vib_conflict
              if n in models[pidx].offtable_vibdepth
              and models[pidx].offtable_vibdepth[n]
              != merged.offtable_vibdepth.get(n)}
        if vd:
            song.offtable_vibdepth = vd
        rm = remap[pidx]
        for v in song.voices:
            for rows in v.patterns:
                for r in rows:
                    r.instr = rm.get(r.instr, r.instr)
        merged.songs.append(song)

    # Per-subtune composer-param overrides (ledger C31 — per-player facts the
    # merge must not collapse to the start player). `rest_effects` is a
    # write-stream TIMING knob (one-frame modulator stall on event-fetch
    # frames): when the packed players disagree, each subtune carries its own
    # value on `MusicSubtune.params` (the composer dispatches at runtime);
    # agreement keeps the file-level key so the emitted image is byte-identical.
    eff = [str(mm.extra_params.get('rest_effects', 'run')) for mm in models]
    if len({eff[pidx] for pidx, _ in subtune_map}) > 1:
        for si, (pidx, _) in enumerate(subtune_map):
            merged.songs[si].params = {**(merged.songs[si].params or {}),
                                       'rest_effects': eff[pidx]}
        merged.extra_params.pop('rest_effects', None)
    # Same route, knob by knob (C31 — Rowdy, a relocating f2 compilation):
    # `vib_ramp` (the copied players are 'step_full' builds while the start
    # player is 'step') and `prep_ctrl` (the $F000 copy's $40 fetch-frame
    # prep-ctrl wedge). File-level stays the START player's value; only the
    # songs whose player disagrees carry a sparse MusicSubtune.params
    # override, so agreeing members emit byte-identically. `vib_ramp` is
    # skipped when a player carries no value (a canon-family player in a
    # mixed file — that disagreement is not runtime-gatable; today's
    # collapse behavior is kept there).
    for key, default in (('vib_ramp', None), ('prep_ctrl', 0x08)):
        vals = [mm.extra_params.get(key, default) for mm in models]
        for si, (pidx, _) in enumerate(subtune_map):
            if (vals[pidx] is None or vals[0] is None
                    or vals[pidx] == vals[0]):
                continue
            merged.songs[si].params = {**(merged.songs[si].params or {}),
                                       key: vals[pidx]}
    return merged


def sfx_player_indices(sid_path: str, spec: dict,
                       hvsc_root: str = 'hvsc85') -> list:
    """Player indices in spec['bases'] that are dmc_sfx sub-players (not DMC)."""
    from pipelines.dmc.v4.sfx_engine import is_sfx_player
    mem, _ = em._load_image(os.path.join(hvsc_root, sid_path))
    return [i for i, b in enumerate(spec['bases']) if is_sfx_player(mem, b)]


def _player_cfg(sid_path: str, hvsc_root: str, spec: dict, pidx: int,
                base: int, post_init_sub):
    """Config for one packed player, carrying its song -> PSID-subtune map.

    Every RUNTIME measurement inside the per-player extract (the off-table
    post-init capture) must run the file subtune that actually selects THIS
    player; its own song numbering is local (ledger C31 — the per-player facts
    the merge collapses). `song_subtunes` is that translation.
    """
    from pipelines.dmc.v4.factory import dmc_v4_config
    cfg = dmc_v4_config(sid_path, hvsc_root=hvsc_root, base_override=base,
                        post_init_sub=post_init_sub)
    smap = {}
    for k, (pi, song) in enumerate(spec['map']):
        if pi == pidx:
            smap.setdefault(song, k)
    cfg.song_subtunes = smap
    return cfg


def extract_compilation(sid_path: str, spec: dict,
                        hvsc_root: str = 'hvsc85') -> 'em.DmcModel':
    """Extract every referenced player and merge into one unified DmcModel."""
    from pipelines.dmc.v4.factory import dmc_v4_config
    from seed_disassembly import parse_psid
    reloc = spec.get('reloc') or {}
    models = [em.extract(_player_cfg(sid_path, hvsc_root, spec, pidx, base,
                                     reloc.get(base)),
                         hvsc_root=hvsc_root)
              for pidx, base in enumerate(spec['bases'])]
    s = parse_psid(os.path.join(hvsc_root, sid_path))
    b0 = models[0]
    hdr = {'title': b0.title, 'author': b0.author, 'released': b0.released,
           'clock': b0.clock, 'sid_model': b0.sid_model,
           'start_song': s.get('start', 1)}
    return merge_models(models, spec['map'], hdr)


def extract_heterogeneous(sid_path: str, spec: dict, hvsc_root: str = 'hvsc85'):
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

    reloc = spec.get('reloc') or {}
    dmc_models = [em.extract(_player_cfg(sid_path, hvsc_root, spec, i,
                                         bases[i], reloc.get(bases[i])),
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
