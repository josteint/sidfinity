"""Layout-independent operand location for re-assembled / relocated DMC v4
players (the `player_code_mismatch` + `no_jumptable` residue).

The factory's primary path extracts via FIXED offsets from the canonical layout
and gates on a byte-compare to canon. Re-assembled variants move the routines
(and their operand sites), so the byte-compare fails and the fixed offsets read
garbage. This locates each table-read by its canonical OPCODE-SKELETON signature
— the sequence of opcodes around the read is relocation-invariant (opcodes don't
change when a routine moves), so matching it in the variant's traced code finds
the read wherever it now sits; the operand there is the table address.

Proven end-to-end on the `$1231` variant family (e.g. For_Domination_04, the SR
helper relocated to +$25A with the wave/filter/sector tables moved): all 11
table addresses located correctly (validated against the on-disk track/sector
chain) and the member extracts + builds. The verify gate is the safety net — a
mislocated operand yields a partial, never a false FULL.

Used by the factory as a FALLBACK when the canonical byte-compare path raises
player_code_mismatch / can't find a jump table at the canonical offsets.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'tools', 'py65_lib'))
from seed_disassembly import trace, _INST_LEN          # noqa: E402

# canonical instruction ADDRESSES that read each table (site-1 of the operand
# sites in factory._SITES); tunetab has two candidate read sites (init / setup).
_CANON_READ = {
    'tunetab':  [0x1050, 0x180D],
    'secp_lo':  [0x1102],
    'secp_hi':  [0x1107],
    'instr':    [0x1226],
    'wavectrl': [0x159B],
    'wavefreq': [0x15B8],
    'filtdef':  [0x1295],
}
# data tables the canon code references by absolute operand (no fixed read site)
_CANON_DATA = {'freq_lo': 0x1647, 'freq_hi': 0x16A7,
               'vibdepth': 0x1888, 'd417': 0x1018}
# per-voice STATE blocks whose INITIAL (file-image) values are the idle note /
# idle gate-mask a resting (gate-off, freewheeling) voice uses. Canon: curnote
# at $1012, gatemask at $100F — but a re-assembled variant lays the state block
# out differently (Funky_Witch: curnote $1013, gatemask $1010, NOT a uniform
# shift), so the extract must LOCATE these, not assume base+0x12 / base+0x0F.
# Located by the operand of the first canon instruction that references each
# (curnote: $1168 LDA $1012,x; gatemask: $11E0 STA $100f,x).
_CANON_STATE = {'curnote': 0x1012, 'gatemask': 0x100F,
                # the $40 dual-effect GLOBAL half-rate parity (canon $1019,
                # INC/LDA/STA at $14B1-$14B9). Its file-image leftover seeds
                # slide_phase; a shifted body moves it (Staring_at_the_Ceiling:
                # $101A — reading base+0x19 there hits the member's $D417
                # shadow and mis-seeds the wave-step/slide interleave phase).
                'dual_parity': 0x1019}
# the track-loop hook ($10DF): canon STA $1726,x (loop-to-0, track_loop_target
# =False); a JSR-hook variant reads the next track byte (=True). Located by
# opcode signature so a moved hook is still classified (verify gate is the net).
_CANON_LOOP_SITE = 0x10DF        # _LOOP_SITE in the factory

_CANON_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                           'dmc4_player_embedded_1000.bin')


def _instrs(mem: bytearray, init: int, play: int, entries=()) -> list:
    """[(addr, opcode, operand16|None)] for reachable instructions, sorted."""
    _c, starts, _l, _j = trace(bytes(mem), 0, init, play, entries)
    out = []
    for pc in sorted(starts):
        op = mem[pc]
        operand = (mem[pc + 1] | (mem[pc + 2] << 8)) if _INST_LEN[op] == 3 else None
        out.append((pc, op, operand))
    return out


_CANON_I = None


def _canon_instrs() -> list:
    global _CANON_I
    if _CANON_I is None:
        canon = open(_CANON_PATH, 'rb').read()
        cm = bytearray(0x10000)
        cm[0x1000:0x1000 + len(canon)] = canon
        _CANON_I = _instrs(cm, 0x1000, 0x1003, (0x1006, 0x1009))
    return _CANON_I


def _sig_at(addr: int, w: int):
    """Opcode-skeleton signature of a window centred on the instruction at
    `addr` (a canon read site). Returns (opcode_tuple, target_index)."""
    cI = _canon_instrs()
    idx = next((i for i, (a, o, v) in enumerate(cI) if a == addr), None)
    if idx is None:
        return None
    lo, hi = max(0, idx - w), min(len(cI), idx + w + 1)
    return tuple(cI[i][1] for i in range(lo, hi)), idx - lo


def _sigs_op(addr: int, w: int) -> list:
    """Signatures of ALL canon instructions whose OPERAND is `addr` (data
    tables with no fixed read site). The first occurrence alone is fragile:
    a variant with a rewritten init/play-preamble breaks that one window
    while later reference sites (e.g. the d417 shadow's RMW at $1270/$12C0)
    still match — so the caller tries each in canon order."""
    cI = _canon_instrs()
    out = []
    for idx, (a, o, v) in enumerate(cI):
        if v == addr:
            lo, hi = max(0, idx - w), min(len(cI), idx + w + 1)
            out.append((tuple(cI[i][1] for i in range(lo, hi)), idx - lo))
    return out


def _locate_site(vI: list, vseq: list, sig):
    """The operand SITE (operand address) of the unique window in the variant's
    instruction stream matching `sig`. None if absent or ambiguous."""
    if not sig:
        return None
    opc, ti = sig
    n = len(opc)
    sites = set()
    for i in range(len(vseq) - n + 1):
        if tuple(vseq[i:i + n]) == opc:
            sites.add(vI[i + ti][0] + 1)
    return sites.pop() if len(sites) == 1 else None


def locate(mem: bytearray, base: int, play: int | None = None,
           region: 'tuple[int, int] | None' = None) -> dict | None:
    """Locate every DMC v4 table by opcode-skeleton signature in the player at
    `base`. Returns {op_instr, op_wavectrl, op_wavefreq, op_filtdef, op_tunetab,
    op_secp_lo, op_secp_hi, freq_lo_addr, freq_hi_addr, vibdepth_addr,
    d417_shadow_addr, track_loop_target} (operand SITES for the _SITES tables,
    absolute ADDRESSES for the data tables) or None if any required table can't
    be uniquely located. Verify-gated downstream.

    `play` overrides the base+3 play entry for the trace — a ripped member's
    jump-table play entry can point at zeroed RAM while the PSID header names
    the real play body (Silent_Memories: table JMP $3AF5 = zeros, header play
    $1085).

    `region` = (lo, hi) restricts the located instructions to the player's own
    code window. A COMPILATION player (ledger C31) can carry DEAD-CODE JMPs into
    a co-packed sibling player's canonical code (an un-relocated `JMP $1591`
    when the live path uses its own $3591) — the static trace follows them and
    every opcode-window signature then matches TWICE (once per player), so every
    site is ambiguous -> None. Bounding the trace to [lo, hi) drops the sibling's
    block (it sorts outside the range; the player's own $3xxx block stays
    contiguous, so signature windows are intact) and each site is unique again.
    Only the caller that FORCES a base (base_override) passes it; the general
    single-player path leaves it None (a re-assembled player may spread code
    past a fixed window)."""
    vI = _instrs(mem, base, base + 3 if play is None else play,
                 (base + 6, base + 9))
    if region is not None:
        lo, hi = region
        vI = [t for t in vI if lo <= t[0] < hi]
    vseq = [o for a, o, v in vI]

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    sites = {}
    for name, cands in _CANON_READ.items():
        site = None
        for w in (6, 9, 12):
            for ca in cands:
                site = _locate_site(vI, vseq, _sig_at(ca, w))
                if site is not None:
                    break
            if site is not None:
                break
        sites[name] = site
    dsites = {}
    for name, addr in _CANON_DATA.items():
        site = None
        for w in (6, 9, 12):
            for sig in _sigs_op(addr, w):
                site = _locate_site(vI, vseq, sig)
                if site is not None:
                    break
            if site is not None:
                break
        dsites[name] = site

    # ---- anchored fallbacks for the restructured-init family (the former
    # no_jumptable bucket): near-canon players whose init header is rewritten
    # around a read site, breaking every opcode WINDOW while the read's own
    # inner shape is intact. Each fallback keys on that inner shape + a
    # value-dedup (all matching sites must read the SAME table); ambiguity
    # returns None as before. Verify-gated downstream like everything here.

    # wavectrl: LDY wavepos,x / LDA wavectrl,y / CMP #$90 (the wave-step
    # marker test — the immediate $90 pins it; a variant may duplicate the
    # routine, both copies read the same table).
    if sites['wavectrl'] is None:
        vals = {}
        for i in range(len(vI) - 2):
            (a0, o0, v0), (a1, o1, v1), (a2, o2, v2) = vI[i], vI[i+1], vI[i+2]
            if o0 == 0xBC and o1 == 0xB9 and o2 == 0xC9 and mem[a2 + 1] == 0x90:
                vals.setdefault(v1, a1 + 1)
        if len(vals) == 1:
            sites['wavectrl'] = vals.popitem()[1]

    # secp lo/hi: LDA (zp),y / TAY / LDA lo,y / STA zp / LDA hi,y / STA zp —
    # the sector-pointer fetch; one anchor recovers both sites (a variant may
    # use a non-canon lo/hi spacing, e.g. Cotton_Eye_Joe $1E8F/$1E9A).
    if sites['secp_lo'] is None or sites['secp_hi'] is None:
        pairs = {}
        for i in range(len(vI) - 5):
            if [vI[i + k][1] for k in range(6)] == \
                    [0xB1, 0xA8, 0xB9, 0x85, 0xB9, 0x85]:
                pairs.setdefault((vI[i + 2][2], vI[i + 4][2]),
                                 (vI[i + 2][0] + 1, vI[i + 4][0] + 1))
        if len(pairs) == 1:
            lo_site, hi_site = pairs.popitem()[1]
            if sites['secp_lo'] is None:
                sites['secp_lo'] = lo_site
            if sites['secp_hi'] is None:
                sites['secp_hi'] = hi_site

    # tunetab: the paired lo/hi track-pointer load LDA t,y / STA / LDA t+1,y /
    # STA. filtdef's chained +1/+2 reads share the shape, so exclude any pair
    # whose base lands inside an already-located table's record window.
    if sites['tunetab'] is None:
        known = {rd16(s) for s in list(sites.values()) + list(dsites.values())
                 if s is not None}
        vals = {}
        for i in range(len(vI) - 3):
            (a0, o0, v0), (a1, o1, v1), (a2, o2, v2), (a3, o3, v3) = \
                vI[i], vI[i+1], vI[i+2], vI[i+3]
            if (o0 == 0xB9 and o1 in (0x8D, 0x9D) and o2 == 0xB9
                    and o3 in (0x8D, 0x9D) and v2 == v0 + 1
                    and not any(k <= v0 <= k + 0x20 for k in known)):
                vals.setdefault(v0, a0 + 1)
        if len(vals) == 1:
            sites['tunetab'] = vals.popitem()[1]

    # d417 shadow: LDA v / ORA (abs | abs,x | and-abs,x) / STA (D417 | v) —
    # the play-tail merge or the shadow's own RMW update.
    if dsites['d417'] is None:
        vals = {}
        for i in range(len(vI) - 2):
            (a0, o0, v0), (a1, o1, v1), (a2, o2, v2) = vI[i], vI[i+1], vI[i+2]
            if (o0 == 0xAD and o1 in (0x0D, 0x1D, 0x3D) and o2 == 0x8D
                    and (v2 == 0xD417 or v2 == v0)):
                vals.setdefault(v0, a0 + 1)
        if len(vals) == 1:
            dsites['d417'] = vals.popitem()[1]

    if any(s is None for s in sites.values()) or \
            any(s is None for s in dsites.values()):
        return None
    data = {name: rd16(site) for name, site in dsites.items()}

    # per-voice STATE blocks (curnote / gatemask): locate the variant's address
    # so the extract reads the right idle note / idle mask. Falls back to the
    # canon base-offset (None) if not locatable; the verify gate is the net.
    state = {}
    for name, addr in _CANON_STATE.items():
        # first canon occurrence ONLY (not _sigs_op): a None here falls back
        # to the canon base-offset, and widening the search could flip an
        # already-verified member's state addr — no gain, regression risk.
        site = None
        for w in (6, 9, 12):
            site = _locate_site(vI, vseq, next(iter(_sigs_op(addr, w)), None))
            if site is not None:
                break
        state[name] = rd16(site) if site is not None else None

    # track-loop hook. Base rule (historical): the canon STA $1726,x site is
    # located ⟹ loop-to-0 (False); absent ⟹ the JSR form (True = read-next
    # track byte). This is correct for canon-STA and read-next members and must
    # NOT be refined by a read-next signature scan — relocated members vary the
    # track-pointer zp ($58/$61/$68… not $f8) and the track-pos address, so any
    # fixed-shape read-next scan false-NEGATIVEs a genuine read-next hook and
    # regresses it to loop-to-0.
    #
    # The one form the base rule mislabels is the RESET-ALL-to-0 JSR hook
    # (LDA #0/STA $1726 / LDA #0/STA $1727 / LDA #0/STA $1728 — zero every
    # voice's track pos = a SYNCHRONIZED loop-to-start): its loop site is a JSR
    # so no canon STA sig is found ⟹ base rule says True, but it loops to 0.
    # These members fail the canon masked-compare (wedge bytes) and reach this
    # path. Flip to False ONLY on a POSITIVE match of that exact 3-pair idiom to
    # CONSECUTIVE track-pos addresses — an idiom absent from the canon player
    # and from every read-next member (census: 8 carriers in all of HVSC-DMC,
    # all reset-all), so it never touches a read-next hook regardless of zp.
    loop_site = None
    for w in (6, 9, 12):
        loop_site = _locate_site(vI, vseq, _sig_at(_CANON_LOOP_SITE, w))
        if loop_site is not None:
            break
    # Round-53 handled the reset-all-to-0 form (immediate #0). Round-62 the same
    # idiom with a non-zero immediate N (Action_G: LDA #5 ×3) = a synchronized
    # loop to track position N. The structural signature is 3× LDA #imm / STA to
    # CONSECUTIVE track-pos addrs (absent from canon + every read-next member).
    # ROUND-63 REFINEMENT (ledger C13): the three immediates need NOT be EQUAL —
    # a member can loop each voice to a DISTINCT position (Attacker: 3/30/3). The
    # SHAPE is the discriminator, the immediates are per-voice DATA (round-62's
    # own lesson). The equal-immediate case is left byte-identical (a scalar N,
    # None when 0); the per-voice case (unequal imms) captures the (n0,n1,n2)
    # tuple, but ONLY when the STA base is the actual track-position address —
    # so a non-reset-all init storing 3 consecutive immediates can't false-match.
    #
    # track-position base = operand of the orderlist-fetch read `LDY tpos,x`
    # (BC) immediately followed by `LDA (zp),y` (B1). Relocation-safe: the zp
    # track pointer varies but the fetch shape does not.
    track_pos_addr = None
    for j in range(len(vI) - 1):
        if vI[j][1] == 0xBC and vI[j + 1][1] == 0xB1:
            track_pos_addr = vI[j][2]
            break
    track_loop_target = loop_site is None
    loop_reset_pos = None
    if track_loop_target:
        for i in range(len(vI) - 5):
            s = vI[i:i + 6]
            if not (all(s[k][1] == 0xA9 for k in (0, 2, 4))
                    and all(s[k][1] == 0x8D for k in (1, 3, 5))
                    and s[3][2] == s[1][2] + 1 and s[5][2] == s[1][2] + 2):
                continue
            imms = (mem[s[0][0] + 1], mem[s[2][0] + 1], mem[s[4][0] + 1])
            if imms[0] == imms[1] == imms[2]:
                track_loop_target = False    # reset-all-to-N hook = loop-to-N
                if imms[0] != 0:
                    loop_reset_pos = imms[0]
                break
            # per-voice reset targets: require the STA triple to BE the track-pos
            # triple (anchored to the fetch-read address) → no false positive.
            if track_pos_addr is not None and s[1][2] == track_pos_addr:
                track_loop_target = False
                loop_reset_pos = imms
                break

    # C19 immediate wedge on the CANON $FF handler itself (round 95,
    # They_Are_the_Best_1): the in-player loop code `C9 FF D0 08 A9 00 9D
    # otrk,x` has its LDA immediate hand-patched (#$00 -> #$02), so every
    # voice's $FF loops to track position N instead of 0 — the same
    # semantics as the reset-all-to-N SYNC hook, expressed as a 1-byte
    # patch the canon-shaped `loop_site` detection sails past (the site
    # matches; only the immediate differs). Anchor: the STA operand must
    # be the fetch-anchored track-position address. Scalar per the wedge's
    # X-indexed store (one immediate serves all voices).
    if loop_reset_pos is None and track_pos_addr is not None:
        sig = bytes([0xC9, 0xFF, 0xD0, 0x08, 0xA9])
        buf = bytes(mem)
        j = buf.find(sig)
        while j >= 0:
            if buf[j + 6] == 0x9D and \
                    (buf[j + 7] | (buf[j + 8] << 8)) == track_pos_addr:
                if buf[j + 5] != 0:
                    track_loop_target = False
                    loop_reset_pos = buf[j + 5]
                break
            j = buf.find(sig, j + 1)

    # THIRD FORM of the $FF handler (a C13 corollary — the `loop_site is
    # None ⟹ JSR-hook` binary above hid it; Hudy/Cotton_Eye_Joe): the canon
    # loop-to-0 store IS present, but the re-dispatch `JMP $10D2` after it
    # was overwritten by author-credit TEXT that EXECUTES — its first byte
    # $50 'P' = BVC (always taken, V=0 from the duration arithmetic) into
    # the dispatch's glide-range `CMP #$C0` with A=$00, which cascades to
    # the plain-note path: every track wrap injects a spurious NOTE-0 row
    # (sticky dur/instr, current transpose, +1 sectpos INC) before the walk
    # resumes at position 0. Positive detection: the canon `C9 FF D0 08 A9
    # 00 9D tpos` shape followed by a BVC landing exactly on a `CMP #$C0`.
    loop_note_inject = False
    if track_pos_addr is not None:
        sig = bytes([0xC9, 0xFF, 0xD0, 0x08, 0xA9, 0x00, 0x9D,
                     track_pos_addr & 0xFF, track_pos_addr >> 8, 0x50])
        buf = bytes(mem)
        j = buf.find(sig)
        if j >= 0:
            op = buf[j + 10]
            tgt = j + 11 + (op - 256 if op >= 128 else op)
            if 0 <= tgt < len(buf) - 1 and buf[tgt] == 0xC9 \
                    and buf[tgt + 1] == 0xC0:
                loop_note_inject = True
                track_loop_target = False

    return {
        'op_instr': sites['instr'], 'op_wavectrl': sites['wavectrl'],
        'op_wavefreq': sites['wavefreq'], 'op_filtdef': sites['filtdef'],
        'op_tunetab': sites['tunetab'], 'op_secp_lo': sites['secp_lo'],
        'op_secp_hi': sites['secp_hi'],
        'freq_lo_addr': data['freq_lo'], 'freq_hi_addr': data['freq_hi'],
        'vibdepth_addr': data['vibdepth'], 'd417_shadow_addr': data['d417'],
        'curnote_addr': state['curnote'], 'gatemask_addr': state['gatemask'],
        'dual_parity_addr': state['dual_parity'],
        'track_loop_target': track_loop_target,
        'loop_reset_pos': loop_reset_pos,
        'loop_note_inject': loop_note_inject,
    }
