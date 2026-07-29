"""DMC family composer - USF -> our own 6502 engine -> xa65 -> PSID.

Per the CORE TENET this is NOT a reproduction of the DMC player: the
runtime is our own implementation (own memory map, own pattern/track
encoding, own instrument layout - parallel arrays instead of 11-byte
records, pre-flattened pulse step schedules, explicit per-event
durations instead of sticky prefixes). It is judged solely by whether
the rebuilt SID emits the original's per-frame $D400-$D418 write
sequence.

Write-order contract (from pipelines/dmc/v4/disassembly.s):
  init        : $D418 = master vol, then $D400..$D417 = 0 ascending
  per frame   : per voice 0,1,2 (see below), then $D416, $D417
  fetch frame : hard note -> ctrl=$08, AD=$0F, SR=$0F only
                (soft/rest/switch/slide -> full effects writes)
  note init   : SR (sustain override applied), AD,
                [$D418 = filter mode | vol, on filter re-init],
                then cymbal ($D400=$FF,$D401=$FF,$D404=$81) or
                wave step + freq lo,hi, PW lo,hi, ctrl
  steady      : freq lo,hi, PW lo,hi, ctrl (gate logic may prepend
                AD=0, SR=0 on the holding gate-off tick)

The engine holds the family's fixed mechanism tables (freq tables +
the per-note vibrato-depth curve, pipelines/dmc/engine_constants.py);
all musical content comes from the USF.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import dataclasses

from src.usf.types import (UsfFile, Pitch, MusicSubtune, InitState,
                           DmcSfxSubtune, InstrumentRef, VoiceBlock,
                           Orderlist)
from src.usf.resolve import resolve_voice, resolve_wave_table
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header
from pipelines.dmc.engine_constants import FREQ_LO, FREQ_HI, VIBDEPTH

LOAD = 0x1000
NOTE_IDX = {n: i for i, n in enumerate(
    ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}


# ---------------------------------------------------------------------------
# Off-table read-redirect (CORE TENET technique; USF carries nothing extra)
# ---------------------------------------------------------------------------
# The wave step rebases a freq-table index as wftab[pos] + curnote. When the
# result exceeds the 96-entry table it overshoots freqlo/freqhi ($1647/$16A7)
# into the engine's live STATE region ($1707-$17A6), so the read SONIFIES a
# live variable (e.g. idx 244 = $173B = the per-voice duration counter). Our
# composer reproduces the write by reading its OWN byte-identical live variable
# instead of a static window byte.
#
# This is the Move-1-unifiable form (filter 3, feedback_three_filters): a
# SHARED generator (_gen_offtable_redirect) consumes a per-engine DATA map
# (idx -> composer state variable). The composer's state layout stays uniform;
# the per-engine difference is the map alone — NOT a layout-mirror that would
# couple the composer's memory map to each engine.
#
# To extend: add (orig_addr, composer_label, n_bytes) rows as members surface
# reads hitting other live state. The variable must track byte-identically
# (counters/ptrs/pos); DRIFTING accumulators (freq/PW) need the composer
# arithmetic made bit-exact first. Map derived from pipelines/dmc/v4/disassembly.s.
ORIG_FLO = 0x1647   # original freqlo table base (FIXED, code-addressed)
ORIG_FHI = 0x16A7   # original freqhi table base (FIXED)

# (orig_state_addr, composer_label, n_bytes). Each must track BYTE-IDENTICALLY
# with the orig (a non-identical row regresses FULLs that read it via the static
# capture). The set below is the EXACTLY-TRACKING per-voice musical state the
# composer maintains; encoding-specific state (wavepos/sectorpos/trkptr) and
# undocumented bytes are deliberately NOT mapped (they don't track identically).
DMC_OFFTABLE_STATE = [
    (0x172C, 'transp', 3),   # transpose (signed semitones)
    (0x172F, 'fbl', 3),      # base freq lo (note table lookup) — most-read
    (0x1732, 'fbh', 3),      # base freq hi
    (0x1735, 'accl', 3),     # freq offset accumulator lo (vibrato/glide)
    (0x1738, 'acch', 3),     # freq offset accumulator hi
    (0x173B, 'dur', 3),      # per-voice duration counter (DEC per tick)
    (0x173E, 'durrel', 3),   # duration reload — the orig's $173E only
                             # changes at a $80-$BF duration prefix, and
                             # every row reloads its counter from it, so
                             # each event's stored duration == the live
                             # reload; the composer shadows it at every
                             # `sta dur,x` event site (NOT the init seed —
                             # orig init writes $173B=1 but never $173E;
                             # the pre-first-event leftover is primed from
                             # the durrel_init params via idurl)
    (0x1741, 'glsp', 3),     # glide speed nibble
    (0x1744, 'gla', 3),      # glide start note
    (0x1747, 'glb', 3),      # glide target note
    # gla/glb/glsp are the SPARSE glide state — written ONLY in the glide
    # branches (ev_slide / the evflags&2 note branch), so a voice that never
    # glides leaves them at their INIT value. The orig keeps the file-image
    # LEFTOVER there (never cleared by init); the composer's init would zero
    # them, so an off-table read landing here (e.g. 98_Mix inst-0 wave freq=255
    # -> idx 255 -> gla[2]) read $00 where the orig reads the leftover $4C
    # (redirect shadowed the correct static capture — the C11 "redirect regresses
    # a FULL matched via the static byte" pattern, commit 1ab8c46's sample lacked
    # a static-leftover reader). FIX: the init now SEEDS gla/glb,x from the
    # captured off-table values (igla/iglb = the ovr-window bytes at these vars'
    # positions), so they track the orig from frame 0. glsp is NOT seeded (a
    # non-zero glsp would spuriously trigger fx_glide, gated `lda glsp,x / beq`);
    # it stays mapped for dynamic readers but a glsp static-leftover read remains
    # residue. A DYNAMIC reader (Alien_WOW/Hardcore) is unaffected — its glide
    # arm overwrites the seed before the read; a STATIC-leftover reader (98_Mix)
    # now reads the leftover.
    (0x174A, 'pend', 3),     # new-note pending flag
    (0x174D, 'ioff', 3),     # instrument record offset (orig inst# * 11, the
                             # exact 6502 carry-chain) — set at each voice's
                             # note-init from ioffval[cinst]; tracks $174D,x
                             # byte-identically (both derive from the current
                             # instrument number). Read off-table when a note
                             # index wraps to 166-168.
    (0x1750, 'pwl', 3),      # pulse width lo
    (0x1753, 'pwh', 3),      # pulse width hi
    (0x1762, 'pwphase', 3),  # PW phase index
    (0x1765, 'pwdir', 3),    # PW direction
    (0x175C, 'pwstep', 3),   # current PW step (phase nibble + base) — live
                             # shadow written in fx_pulse exactly where the
                             # orig's $1379 STA runs (guard + freewheel
                             # frames included); init-wiped on both sides
                             # (Brendas idx 182 = V2 $175D)
    (0x1768, 'vibdir', 3),   # vibrato direction
    (0x176B, 'vibctr', 3),   # vibrato step counter
    (0x176E, 'rampctr', 3),  # vibrato ramp counter
    (0x1771, 'vibdel', 3),   # vibrato delay counter
    (0x1774, 'vibwid', 3),   # vibrato width
    (0x1777, 'cvram', 3),    # vibrato ramp limit
    (0x177D, 'fxf', 3),      # FX flags cache (instr byte 10) — stored at
                             # note-init from iflag,y exactly where the orig
                             # stores $18FA,y ($12EB); init-cleared to 0 on
                             # both sides so no seed needed. iflags() is the
                             # lossless byte-10 reconstruction from the typed
                             # instrument fields (all 8 bits round-trip).
                             # Read off-table via fhi idx 214-216
                             # (Saturday_Dance V3 idx 216).
    (0x1780, 'wctrl', 3),    # current wave ctrl byte
    (0x1792, 'vstep', 3),    # vibrato step size lo
    (0x1795, 'vsteph', 3),   # vibrato step size hi
    (0x1798, 'slal', 3),     # dual-effect slide accumulator lo
    (0x179B, 'slah', 3),     # dual-effect slide accumulator hi
    # NB the composer's `cpwmin`/`cpwmax` VARIABLES hold bound A / bound B
    # respectively — the extract sets min_hi=pw_bound_a, max_hi=pw_bound_b, so
    # the var named cpwmin carries orig $1756 (bound A) and cpwmax carries orig
    # $1759 (bound B). Self-consistent for the PWM sweep (set + compare both use
    # the swapped names), but the off-table redirect must map each ORIG address
    # to the var HOLDING THAT ADDRESS'S VALUE: orig $1756 (bound A) -> cpwmin,
    # orig $1759 (bound B) -> cpwmax. (family-1 round 21: the pos~74-81 V2/V3
    # freqhi cluster read orig bound A but the redirect emitted cpwmax=bound B,
    # so mine=$0B where orig=$04 = A EOR $0F.)
    (0x1756, 'cpwmin', 3),   # orig PW bound A (byte2 hi nibble) = composer cpwmin
    (0x1759, 'cpwmax', 3),   # orig PW bound B (= A EOR $0F)    = composer cpwmax
    (0x175F, 'cpwbase', 3),  # PW step base (instr byte 6 hi nibble)
    # GLOBAL filter state machine ($1718-$1723). The composer already maintains
    # byte-identical copies (it reproduces the $D416/$D417 filter write stream),
    # so these track by construction — verified index-match + value-match on 5
    # reps (Senna/In_die_Dunkelheit/Slide_Me/High_Tech/1st_Intro). Mapped so an
    # off-table read lands on the live var instead of a stale freqhi-overrun byte.
    # (fcut $171C IS mapped below — the old "regressed Humppa" caution was
    # fcut+wavepos bundled; fcut alone tracks and is 0-regression,
    # exposure-censused this round.)
    (0x1718, 'spdctr', 1),   # speed counter (DEC per frame; reload = $1716)
    (0x1720, 'fclaim', 1),   # filter claim flag — 0 at play() entry ($1092
                             # `ldx #0 / stx fclaim`), then the FIRST filter-
                             # flagged voice in X order stores X+1 ($13D2).
                             # The composer's fclaim is op-for-op the same
                             # (same reset site, same `lda fclaim / bne / inx /
                             # stx fclaim / dex` claim in fx_filter, same voice
                             # order), and both sides start each play() at 0 —
                             # no seed needed. The 2026-06-29 rejection ("+0/−1
                             # Long_Night, fclaim timing ≠ orig") was measured
                             # against an f2 member and is superseded: on
                             # Industrial_Sci-Fi the two agree at ALL 12,784
                             # read moments (memwatch-on-write D40F, orig
                             # $9720 vs our fclaim — 0 mismatches). Sonified
                             # via hi idx 121 / lo idx 217.
    (0x171C, 'fcut', 1),     # filter current cutoff (-> $D416 every frame). The
                             # composer's fcut drives the identical $D416 stream,
                             # so it tracks $171C by construction (verified
                             # index+value on King_of_Earth $20==$20). The old
                             # "regressed Humppa" note (C11) was fcut BUNDLED with
                             # wavepos $177A (the positional-hard byte); fcut alone
                             # is clean — exposure-censused this round.
    (0x1719, 'fstep', 1),    # filter current step index 0-5
    (0x171A, 'fframe', 1),   # filter frames spent in current step
    (0x1721, 'fsz', 1),      # filter step size cache — the composer's fsz is
                             # stored from fdstep,y exactly where the orig
                             # stores $1a7b,y → $1721 ($13E9); init-cleared
                             # to 0 both sides (Saturday_Dance flo idx 218)
    (0x1722, 'fdu', 1),      # filter step duration cache (orig $13EF)
    (0x171B, 'fbase', 1),    # filter definition base index (def# << 4)
    (0x171D, 'frep', 1),     # filter repeat/loop step index (def byte2)
    (0x171E, 'fstop', 1),    # filter stop cutoff (def byte3) — verified tracks
    (0x171F, 'wjmp', 1),     # shared effect scratch — the LAST of: pulse-program
                             # raw speed byte ($1357/$135A, the two-nibble
                             # instr+3..5 byte, reconstructed as
                             # isteps[even] | isteps[odd]>>4 in irawsp), glide
                             # step<<4 ($1425), wave jump-back distance
                             # ($15A5/$15E2). Shadowed 1:1 at all three composer
                             # sites (fx_pulse / fx_glide / ws_rd0+ws_drum);
                             # init-cleared both sides ($1718-$179D wipe), and
                             # densely written (fx_pulse runs unconditionally
                             # per voice per frame) so it converges — no seed.
    (0x1723, 'fres', 1),     # filter resonance (def byte0 hi nibble) -> $D417 hi
    (0x1724, 'dtmpl', 1),    # dual-slide freq temp lo — GLOBAL scratch written
    (0x1725, 'dtmph', 1),    # only by the $40 slide path ($14CB/$14D3);
                             # shadowed 1:1 in fx_dual_run
    (0x1726, 'otrk', 3),     # track byte-offset (entry-table value + INC at
                             # sector end — mirrors $10FB/$182D/$10DF exactly)
    (0x1783, 'wnote', 3),    # arp note = wave-offset + curnote (derived in wavestep)
    (0x1786, 'guard', 3),    # post-note guard (2 at note-init, DEC 2->1->0;
                             # op-for-op the orig's $12FA/$1327). RE-VERIFIED
                             # (round 10): the orig's $1322 check runs for
                             # EVERY voice every frame — stopped voices
                             # included ($10B3 freewheels into $11F9, same as
                             # our run_effects) — and init CLEARS $1786-8, so
                             # both sides start 0 and track in lockstep. The
                             # earlier "leftover $FF" objection was a misread:
                             # $FF is not a possible guard value (BEQ guards
                             # the DEC); that member's read was wnote idx 221
                             # and its FULL status a stale palimpsest.
    # NOTE: wavepos ($177A) is NOT here — the composer's wavepos runs on its
    # own re-packed pool offsets (iwst), so an UNCONDITIONAL row was
    # net-negative (0 recoveries, 1 regression: Object_of_Art, 2026-06-28,
    # our wavepos = orig+5). It is served by the GATED DMC_WAVEPOS_ROW below
    # instead: members whose off-table reads sonify a live wave position
    # carry per-instrument `wave_table_pos` (editor arrangement, §8) and get
    # a LAYOUT-PRESERVING pool placed at those positions, making wavepos ==
    # orig $177A at every settled moment. See ledger C11 / project_dmc.
]

# sector-position shadow ($1729,x = INC per consumed sector byte, reset to 0
# at the $7F end check). NOT in DMC_OFFTABLE_STATE: the redirect row + the
# sectpos var + the extra per-event byte are emitted ONLY for members whose
# off-table freq reads land on $1729-$172B (params sectpos_shadow, extract-
# detected) — every other member stays byte-identical. Per-row visible values
# are DERIVED at compose time from row kind + the stated-command fx_flags
# (dur_cmd/instr_cmd/vol_cmd/soft_cmd — the editor's command placement, §8 arrangement);
# no byte offsets are carried in USF. The extract's event-driven capture
# excludes these idx unconditionally (_redirect_mapped_idx).
DMC_SECTPOS_ROW = (0x1729, 'sectpos', 3)

# live wave-position row ($177A,x — fhi window idx 211-213). NOT in
# DMC_OFFTABLE_STATE: the composer's wavepos runs on its OWN pool offsets, so
# the row is only correct under layout-preserving packing (every instrument
# carries wave_table_pos and the pool is placed at the orig editor positions —
# see Model.wavepos_layout). Emitted only for those members; everyone else
# keeps the static window byte (the old "mapping wavepos regressed a FULL"
# caution was exactly the un-gated form of this row).
DMC_WAVEPOS_ROW = (0x177A, 'wavepos', 3)


# Live-signal NAMES (live_signal_modulation_draft §3, phase 3): the USF
# vocabulary name for each live-served engine variable. One entry per
# DMC_OFFTABLE_STATE label (+ the sectpos/wavepos rows + the co-located
# tempo/master-volume slots). The composer maps names back to its OWN
# variables (mechanism); the USF never speaks in window indices again.
# Keep in sync with types.LIVE_SIGNAL_NAMES + the grammar's OFSIG terminal.
DMC_SIGNAL_NAMES = {
    'transp': 'transpose', 'fbl': 'freq_base_lo', 'fbh': 'freq_base_hi',
    'accl': 'freq_accum_lo', 'acch': 'freq_accum_hi',
    'dur': 'row_duration', 'durrel': 'row_duration_reload',
    'glsp': 'glide_speed', 'gla': 'glide_note', 'glb': 'glide_target',
    'pend': 'note_pending', 'ioff': 'instrument_offset',
    'pwl': 'pulse_lo', 'pwh': 'pulse_hi', 'pwphase': 'pulse_phase',
    'pwdir': 'pulse_dir', 'pwstep': 'pulse_step',
    'cpwmin': 'pulse_min', 'cpwmax': 'pulse_max', 'cpwbase': 'pulse_base',
    'vibdir': 'vibrato_dir', 'vibctr': 'vibrato_counter',
    'rampctr': 'vibrato_ramp_counter', 'vibdel': 'vibrato_onset',
    'vibwid': 'vibrato_width', 'cvram': 'vibrato_ramp_cache',
    'vstep': 'vibrato_step_lo', 'vsteph': 'vibrato_step_hi',
    'slal': 'slide_accum_lo', 'slah': 'slide_accum_hi',
    'fxf': 'instrument_flags', 'wctrl': 'wave_ctrl_cache',
    'wnote': 'note_offset', 'wjmp': 'wave_speed_cache',
    'guard': 'gate_guard', 'otrk': 'track_position',
    'spdctr': 'speed_counter', 'fclaim': 'filter_claim',
    'fcut': 'filter_cutoff', 'fstep': 'filter_step',
    'fframe': 'filter_frame', 'fbase': 'filter_base',
    'fsz': 'filter_size', 'fdu': 'filter_duration',
    'frep': 'filter_repeat', 'fstop': 'filter_stop', 'fres': 'filter_res',
    'dtmpl': 'slide_freq_lo', 'dtmph': 'slide_freq_hi',
    'sectpos': 'sector_position', 'wavepos': 'wave_position',
}


def signal_for_addr(addr: int):
    """(signal_name, voice|None) for a live-served canon-geometry address,
    or None (a static byte). Voice is 1-based for per-voice triples, None
    for globals. The single source of truth for extract's signal stamping;
    consistent with offtable_live_idx by construction (same rows)."""
    if addr == 0x1716:
        return ('tempo', None)
    if addr == 0x1717:
        return ('master_volume', None)
    for base, label, nb in DMC_OFFTABLE_STATE + [DMC_SECTPOS_ROW,
                                                 DMC_WAVEPOS_ROW]:
        if base <= addr < base + nb:
            return (DMC_SIGNAL_NAMES[label],
                    (addr - base + 1) if nb > 1 else None)
    return None


_OFFTABLE_LIVE_IDX = None


def offtable_live_idx() -> set:
    """The window indices a canon-geometry off-table read is served LIVE from:
    the redirect map (DMC_OFFTABLE_STATE + sectpos + wavepos rows) PLUS the
    co-located live speed/master-vol slots (window offset 15/16 => hi idx
    111/112, lo idx 207/208). A read at one of these idx (on a canon member)
    sonifies a live-varying value; a read elsewhere reads a fixed byte. The
    single source of truth for both extract (which stamps the per-read `live`
    flag) and the composer (which derives its member-global redirect boolean),
    so the two sides can't disagree on geometry."""
    global _OFFTABLE_LIVE_IDX
    if _OFFTABLE_LIVE_IDX is None:
        s = set()
        for addr, _lbl, nb in DMC_OFFTABLE_STATE + [DMC_SECTPOS_ROW,
                                                    DMC_WAVEPOS_ROW]:
            for k in range(nb):
                hi = (addr + k) - ORIG_FHI
                if 96 <= hi <= 255:
                    s.add(hi)
                lo = (addr + k) - ORIG_FLO
                if 192 <= lo <= 255:
                    s.add(lo)
        s |= {96 + 15, 96 + 16, 192 + 15, 192 + 16}  # co-located spd/mvol
        _OFFTABLE_LIVE_IDX = s
    return _OFFTABLE_LIVE_IDX


def _gen_offtable_redirect(state_map, orig_base, win_min, static_load,
                           store_label):
    """Emit the wave-step off-table redirect for one read (lo or hi).

    For each state variable whose table index (orig_addr - orig_base) lands in
    the off-table window [win_min, 255], emit a range check that reads our live
    variable; else fall through to ``static_load``. Y holds the rebased index.
    Returns asm text; the caller places the ``store_label:`` that the in-range
    branches jmp to. Engine-blind — reused per engine with its own map.

    The COMMON case (an in-table read, Y below every mapped offset) takes a
    single leading bounds check straight to ``static_load`` instead of walking
    the whole compare chain. The chain is on the per-voice per-frame wave-step
    path, so its cost scales with the map size for EVERY member — the row
    growth across rounds (wjmp/sectpos/wavepos/fxf/fsz) accumulated enough
    cycles to overrun tight high-multispeed CIA budgets (Revolution-Evolution,
    latch 2456: the play body must FIT the latch or play() entries slip and
    the rebuild runs measurably slow). The fast path serves exactly the Ys
    that fell through every row anyway — content-identical by construction."""
    rows = []
    for addr, label, nb in state_map:
        off = addr - orig_base
        if off < win_min or off + nb > 256:
            continue                     # not in this read's off-table window
        rows.append((off, label, nb))
    if not rows:
        return f'        {static_load}'
    min_off = min(off for off, _, _ in rows)
    parts = [
        f'        cpy #{min_off}\n'
        f'        bcs {store_label}_chain     ; mapped-window candidate\n'
        f'        {static_load}          ; common case: in-table\n'
        f'        jmp {store_label}\n'
        f'{store_label}_chain:']
    i = 0
    for off, label, nb in rows:
        nxt = f'{store_label}_n{i}'
        # upper-bound check is unnecessary when the range runs to idx 255
        # (off+nb == 256): idx is a byte, so `cpy #256` is both invalid and
        # always-in-range. Emit only the lower bound there.
        upper = ('' if off + nb >= 256 else
                 f'        cpy #{off + nb}\n        bcs {nxt}\n')
        parts.append(
            f'        cpy #{off}\n'
            f'        bcc {nxt}\n'
            + upper +
            f'        lda {label}-{off},y          ; live {label} (off-table)\n'
            f'        jmp {store_label}\n'
            f'{nxt}:')
        i += 1
    parts.append(f'        {static_load}')
    return '\n'.join(parts)


def _inst_offset(iid: int) -> int:
    """The exact 6502 chain the DMC player uses to turn an instrument NUMBER
    into its record byte-offset ($1213-$1222 -> stored at $174D,x): ASL x3
    then ADC x3, carries propagating in the 8-bit accumulator — NOT a clean
    (iid*11) & 0xFF (an intermediate ADC carry feeds the next, and the final
    ASL carry feeds the first ADC for iid >= 32). Mirrors the extract's
    engine_model._decode_instrument so ioffval matches $174D byte-for-byte."""
    off, c = iid, 0
    for _ in range(3):
        c = (off >> 7) & 1
        off = (off << 1) & 0xFF
    for _ in range(3):
        off = off + iid + c
        c = 1 if off > 0xFF else 0
        off &= 0xFF
    return off


# ---------------------------------------------------------------------------
# USF -> internal song model
# ---------------------------------------------------------------------------

def _note_num(p: Pitch) -> int:
    return p.octave * 12 + NOTE_IDX[p.name]


def _row_event(row, inst_slot: dict) -> tuple:
    """Map a NoteRow to one engine event tuple."""
    flags = {f.split('=')[0]: (f.split('=')[1] if '=' in f else True)
             for f in row.fx_flags}
    vol = int(flags.get('vol', 0))
    gspd = int(flags.get('glide', 0))
    if row.pitch.is_rest:
        # legacy (materialized/effective) voices: notes re-state slot/vol, so
        # rest/switch carry no sticky update (None -> flags=0).
        if 'gate_toggle' in flags:
            return ('switch', row.duration, None, None)
        return ('rest', row.duration, None, None)
    note = _note_num(row.pitch)
    slot = inst_slot[row.instr.id]
    if 'noretrig' in flags and 'glide' in flags and 'glide_to' not in flags:
        # slide current note to target (DMC glide mode 1). Mode 1 renders as
        # `noretrig glide=N` with note=target and NO glide_to; a mode-0 glide
        # row under soft-start mode carries noretrig TOO but keeps glide_to —
        # it must take the note path below (full note load + rebase to note A,
        # glide up/down toward glide_to), not the slide path (Gangstallica
        # V2: slide held the OLD base and stepped down where the orig rebased
        # to A and stepped up — family-1 round 18).
        return ('slide', gspd, note, row.duration, None, None)
    soft = 1 if 'noretrig' in flags else 0
    if 'glide_to' in flags:
        target = _glide_target(flags['glide_to'], note)
        return ('note', soft, note, row.duration, slot, vol, gspd, target)
    return ('note', soft, note, row.duration, slot, vol, 0, None)


def _glide_target(tgt: str, note: int) -> int:
    """Parse a `glide_to=` flag into an absolute note number — EXACTLY.

    History: until round 97 a `len(tgt)==3` guard dropped the '#' for a
    2-digit-octave sharp (F#10 -> parsed as F-10 = 125, one semitone low),
    deliberately: off-table targets' arrival check reads freqhi[126] =
    $1725 = live dtmph, and with the arrival compare reading our STATIC
    window byte the parsed-125 target was in a self-consistent balance
    (the exact parse alone REGRESSED 20/104, round 22). Round 97 (Cleve_24)
    re-measured per C11: our dtmpl/dtmph shadow tracks the orig 1:1 (0
    mismatches over 2,843 events), so the arrival compare is now served
    through the SAME off-table redirect as the reload (gated `ga_cmp`) and
    the target parses exactly — the true mechanism, not the balance."""
    sep = tgt[1]
    name = tgt[0] + ('#' if sep == '#' else '')
    return int(tgt[2:]) * 12 + NOTE_IDX[name]


def _row_event_stated(rr, inst_slot: dict) -> tuple:
    """Statedness-driven event for a STATED voice (D6 piece 3, the sticky
    EMISSION change). Every event kind emits its instrument slot / vol override
    ONLY where the source row STATES it (`None` = inherited — the player keeps
    its sticky `curinst,x` / `volovr,x` register). The duration is always carried
    (resolved `rr.duration`) — DMC's dur carry is 2 slots corpus-wide, not worth
    a sticky seed.

    Emission is by STATEDNESS (C32 "presence = the byte fact"), never
    value-equality: statedness is pattern-intrinsic, so byte-keyed dedup still
    collapses the ~intro variants. The sonified sectpos ($1729) / otrk ($1726)
    counters are reproduced from the explicit per-event shadow (decoupled from
    what this emission carries), so the sticky change is safe for the
    off-table-sonified members."""
    row = rr.row
    flags = {f.split('=')[0]: (f.split('=')[1] if '=' in f else True)
             for f in row.fx_flags}
    # slot / vol are carried on EVERY event kind (note/rest/switch/slide),
    # emitted only where the SOURCE states them (None = inherit). A rest that
    # states an instrument updates the engine's sticky state (the resolver folds
    # it in) — carrying it lets the player's ev_rest update curinst,x so a
    # following inherited note reads the right instrument. Statedness is
    # pattern-intrinsic, so byte-keyed dedup still collapses the ~intro variants.
    slot = inst_slot[row.instr.id] if row.instr is not None else None
    vol = next((int(f[4:]) for f in row.fx_flags if f.startswith('vol=')), None)
    if row.pitch.is_rest:
        if 'gate_toggle' in flags:
            return ('switch', rr.duration, slot, vol)
        return ('rest', rr.duration, slot, vol)
    note = _note_num(row.pitch)
    gspd = int(flags.get('glide', 0))
    if 'noretrig' in flags and 'glide' in flags and 'glide_to' not in flags:
        return ('slide', gspd, note, rr.duration, slot, vol)
    soft = 1 if 'noretrig' in flags else 0
    if 'glide_to' in flags:
        return ('note', soft, note, rr.duration, slot, vol, gspd,
                _glide_target(flags['glide_to'], note))
    return ('note', soft, note, rr.duration, slot, vol, 0, None)


def _pattern_tempos(rows) -> 'list | None':
    """Per-row tempo events (fx `tempo=N`, ledger C14 — the Doxx
    v3_instr_tempo build): the composer emits a gated [$05, N] prefix at the
    row's fetch, setting the speed reload. None when the pattern has none
    (the corpus-dominant case — no encoding change)."""
    out = [next((int(f[6:]) for f in r.fx_flags if f.startswith('tempo=')),
                None) for r in rows]
    return out if any(t is not None for t in out) else None


def _encode_pattern(rows_events: list, secvals: list | None = None,
                    tempos: list | None = None) -> bytes:
    """Encode one pattern. With `secvals` (sectpos shadow on), each event
    carries the row's visible orig sector-position right after the opcode —
    every handler stores it to sectpos,x at fetch, mirroring the orig's
    per-byte INC + $7F reset settled value. With `tempos`, a row carrying a
    tempo event gets a [$05, N] prefix (speed reload = N) consumed before
    the row's own event."""
    out = bytearray()
    if tempos:
        pre = bytearray()
        for k, ev in enumerate(rows_events):
            if tempos[k] is not None:
                pre += bytes([0x05, tempos[k] & 0x0F])
            pre += _encode_pattern(rows_events[k:k + 1],
                                   None if secvals is None
                                   else secvals[k:k + 1])[:-1]
        pre.append(0x00)
        return bytes(pre)

    def _sv_tail(slot, vol):
        # STICKY slot/vol values (D6 piece 3), appended only when stated (None =
        # inherit -> the player keeps its sticky curinst,x / volovr,x).
        return ([slot] if slot is not None else []) + \
               ([vol] if vol is not None else [])

    def _dur_sv(dur, slot, vol):
        # rest/switch/slide have no flags byte, so slot/vol PRESENCE rides the
        # two free high bits of the always-present duration byte (dur <= $3F):
        # bit6 = slot, bit7 = vol. A plain rest is thus [op, dur] — no extra byte.
        return (dur & 0x3F) | (0x40 if slot is not None else 0) \
                            | (0x80 if vol is not None else 0)

    for k, ev in enumerate(rows_events):
        kind = ev[0]
        sp = [] if secvals is None else [secvals[k] & 0xFF]
        if kind == 'rest':
            _, dur, slot, vol = ev
            out += bytes([0x02] + sp + [_dur_sv(dur, slot, vol)]
                         + _sv_tail(slot, vol))
        elif kind == 'switch':
            _, dur, slot, vol = ev
            out += bytes([0x03] + sp + [_dur_sv(dur, slot, vol)]
                         + _sv_tail(slot, vol))
        elif kind == 'slide':
            _, gspd, note, dur, slot, vol = ev
            out += bytes([0x04] + sp + [gspd, note, _dur_sv(dur, slot, vol)]
                         + _sv_tail(slot, vol))
        else:
            _, soft, note, dur, slot, vol, gspd, target = ev
            # notes already carry a flags byte, so slot/vol presence rides
            # evflags bit3 (slot) / bit4 (vol) — no extra byte. glide tail keyed
            # on TARGET PRESENCE, not speed truthiness: a mode-0 glide with
            # speed 0 is the engine's glide-cancel (glsp STORED 0), which must
            # reach ev_note's glide path (C22).
            f = soft | (2 if target is not None else 0)
            f |= (0x08 if slot is not None else 0) \
                 | (0x10 if vol is not None else 0)
            out += bytes([0x01] + sp + [f, note, dur & 0x3F]
                         + _sv_tail(slot, vol))
            if target is not None:
                out += bytes([gspd, target])
    out.append(0x00)
    return bytes(out)


def _row_secwidth(row) -> int:
    """Orig byte width of one row's fetch: base bytes of the event kind
    (note/rest/switch 1, slide 2, glide 3 — each byte INCs $1729,x) plus the
    stated dur/instr/vol commands and $7C toggles consumed in the same fetch
    (the dur_cmd/instr_cmd/vol_cmd/soft_cmd fx_flags). Mirrors _row_event's kind logic."""
    flags = {f.split('=')[0]: (f.split('=')[1] if '=' in f else True)
             for f in row.fx_flags}
    extra = (('dur_cmd' in flags) + ('instr_cmd' in flags) + ('vol_cmd' in flags)
             + int(flags.get('soft_cmd', 0) or 0))
    if row.pitch.is_rest:
        return 1 + extra                     # $7E rest / $7D switch
    if 'noretrig' in flags and 'glide' in flags and 'glide_to' not in flags:
        return 2 + extra                     # mode-1 slide: $Dx + target
    if 'glide_to' in flags:
        return 3 + extra                     # mode-0 glide: $Cx + A + B
    return 1 + extra                         # plain note


def _pattern_secvals(rows, base: int = 0) -> list:
    """Per-row visible sectpos: cumulative width through the row's fetch;
    the LAST row reads 0 (the trailing $7F resets $1729,x in the same tick,
    sub_11E6 -> $11F2) — UNLESS it is a RUN-ON row ('runon' fx flag: the
    source stream hits the next fetch with no $7F, so $1729,x keeps its
    accumulated value into the next entry). `base` = the sectpos inherited
    from preceding run-on entries (0 for every $7F-terminated predecessor —
    the historical behaviour, byte-identical when no runon rows exist)."""
    vals, cum = [], base
    for r in rows:
        cum = (cum + _row_secwidth(r)) & 0xFF
        vals.append(cum)
    if vals and 'runon' not in rows[-1].fx_flags:
        vals[-1] = 0
    return vals


def _dmc_rows_stated(vb) -> bool:
    """True iff the voice's rows are in STATED-inherited form and need the
    resolution interpreter: any row omits its duration, or any NOTE row
    omits its instrument (DMC's effective form always carries both; vol
    can't discriminate — the extract guarantees a stated voice with no
    dur/instr inheritance has no ACTIVE vol inheritance either, falling
    back wholesale otherwise)."""
    return any(r.duration is None
               or (not r.pitch.is_rest and r.instr is None)
               for p in vb.patterns for r in p.rows)


class _Model:
    """Everything the asm emitter needs, distilled from the USF."""

    def __init__(self, usf: UsfFile):
        self.usf = usf
        self.instruments = list(usf.instruments)
        self.inst_slot = {i.id: k for k, i in enumerate(self.instruments)}
        # OFF-TABLE GLIDE TARGET present? (round 97, Cleve_24): a glide row
        # whose runtime glb = (target + transpose) & $FF passes the 96-entry
        # table makes the ARRIVAL check read the off-table window (canon:
        # freqhi[126] = live dtmph). Such members get the redirect-served
        # arrival compare (`ga_cmp`); everyone else keeps the plain
        # `cmp freqhi,y` — byte-identical. Conservative over-approx (any
        # target x any of the voice's transposes): a widely-gated member is
        # content-identical (in-table Y takes the chunk's fast path to the
        # same table byte).
        self.glide_offtable = False
        for _sub in usf.subtunes:
            for _vb in (getattr(_sub, 'voices', None) or []):
                _ol = _vb.orderlist
                _trs = {0}
                for _i in range(len(getattr(_ol, 'entries', None) or [])):
                    try:
                        _trs.add(_ol.transpose_at(_i))
                    except Exception:
                        pass
                for _p in _vb.patterns:
                    for _r in _p.rows:
                        for _f in _r.fx_flags:
                            if _f.startswith('glide_to='):
                                _t = _glide_target(_f[9:], 0)
                                if any(((_t + _tr) & 0xFF) > 95
                                       for _tr in _trs):
                                    self.glide_offtable = True
        # layout-preserving wave pool: every instrument carries its editor
        # wave-table position (only emitted for members whose off-table freq
        # reads sonify a live wave position $177A-$177C) — pack the pool at
        # those positions so the runtime wavepos EQUALS the orig's $177A,x
        # and the DMC_WAVEPOS_ROW redirect serves the read live.
        _wtp = [getattr(i, 'wave_table_pos', None) for i in self.instruments]
        self.wavepos_layout = bool(_wtp) and all(p is not None for p in _wtp)
        # Off-table serving booleans — DERIVED from the per-read `live` flags on
        # offtable_freq (5th tuple element), never from a params geometry bit
        # (which described HVSC memory layout — Core Tenet corollary). Each read
        # is (off, note, lo, hi[, live]); `live` marks reads the composer serves
        # from live state. The redirect/co-location only AFFECTS the write stream
        # for reads at a live-served idx; so the one member that must turn it OFF
        # is the NON-canon member, detectable as a STATIC read sitting at a
        # live-served idx (its geometry moved the state elsewhere, so that byte
        # is unrelated code/data — serve it from the static capture, not live).
        # Everyone else (canon, or reads only at fixed positions, or no reads)
        # keeps it ON — byte-identical to the old default. sectpos_on = a live
        # read hits the sector-position window.
        _all = [r for i in self.instruments
                for r in (getattr(i, 'offtable_freq', None) or [])]
        _live = offtable_live_idx()

        def _rec_live(r):
            # live = the legacy 5-tuple flag OR any named-signal slot
            # (phase 3, live-signal modulation §3 — both forms accepted
            # until the corpus sync retires the flag)
            return (len(r) > 4 and r[4]) or \
                any(hasattr(x, 'voice') for x in r[2:4])
        _static_at_live = any(not _rec_live(r)
                              and ((r[0] + r[1]) & 0xFF) in _live for r in _all)
        self.offtable_redirect = not _static_at_live
        _SECTPOS_IDX = {(0x1729 + k) - ORIG_FHI for k in range(3)} \
            | {(0x1729 + k) - ORIG_FLO for k in range(3)}
        self.sectpos = any(
            (any(getattr(x, 'name', None) == 'sector_position'
                 for x in r[2:4])
             or (len(r) > 4 and r[4]
                 and ((r[0] + r[1]) & 0xFF) in _SECTPOS_IDX))
            for r in _all)
        # POSITIONAL pool emission (live_signal_modulation phase 4): a
        # wave_position carrier whose USF carries the stated wave_table
        # gets its pool emitted AT the stated cell positions — the runtime
        # cursor then equals the original's labels natively (marker-hop
        # chains through co-located data and mod-256 wraps included), and
        # DMC_WAVEPOS_ROW serves the read live. Legacy wave_table_pos
        # members keep the place_prog path; everyone else the repack.
        _WP_IDX = {(0x177A + k) - 0x16A7 for k in range(3)}
        self.wavepos_positional = bool(
            usf.wave_table and not self.wavepos_layout
            and all(getattr(i, 'wave_start', None) is not None
                    for i in self.instruments)
            and any(
                any(getattr(x, 'name', None) == 'wave_position'
                    for x in r[2:4])
                or (len(r) > 4 and r[4]
                    and ((r[0] + r[1]) & 0xFF) in _WP_IDX)
                for r in _all))
        # filter defs: program key -> slot = orig def# (key-1). The def table
        # is emitted DENSE in orig order at the orig 16-byte record stride so
        # off-table walk reads (repeat > 5) hit the same bytes as the orig;
        # gaps (older sparse USF files) are zero records.
        self.filter_slots = {prog: prog - 1 for prog in usf.filter_programs}
        _zero_def = {'res': 0, 'mode': 0, 'init': 0, 'repeat': 0, 'stop': 0,
                     'steps': [(0, 0)] * 6}
        _maxd = max((p - 1 for p in usf.filter_programs), default=-1)
        self.filter_defs = [usf.filter_programs.get(d + 1, _zero_def)
                            for d in range(_maxd + 1)]
        # global pattern pool (content-deduped) + per subtune/voice tracks
        self.patterns: list[bytes] = []
        pat_ids: dict[bytes, int] = {}
        self.subtunes = []
        for sub in usf.subtunes:
            voices = []
            for v in sub.voices:
                track = bytearray()
                ol = v.orderlist
                pat_by_local = {p.id: p for p in v.patterns}
                # per-entry orig track byte-offset (of the entry's SECTOR
                # byte): the orig emits [transpose cmd byte]? [sector byte]
                # per entry, transpose byte present on CHANGE plus a per-voice
                # constant PAD of redundant editor-placed commands (the
                # otrk_pad phase scalar, extract-measured; the dual_phase
                # pattern). Off-table reads sonify this counter ($1726,x), so
                # the runtime keeps otrk,x as real state seeded per entry.
                def _intern(events, secvals, tempos=None):
                    enc = _encode_pattern(events, secvals, tempos)
                    gid = pat_ids.get(enc)
                    if gid is None:
                        gid = len(self.patterns)
                        self.patterns.append(enc)
                        pat_ids[enc] = gid
                    return gid

                def _gid_entry(pid, sbase=0):
                    return _intern(
                        [_row_event(r, self.inst_slot)
                         for r in pat_by_local[pid].rows],
                        _pattern_secvals(pat_by_local[pid].rows, sbase)
                        if self.sectpos else None,
                        _pattern_tempos(pat_by_local[pid].rows))

                def _sbase_next(pid, sbase):
                    # sectpos base threading: a pattern whose last row is
                    # RUN-ON ('runon') leaves $1729,x at its accumulated
                    # value — the next entry's visible sectpos starts there.
                    # A $7F-terminated pattern resets it to 0 (the common
                    # case: base stays 0 for every member with no runon
                    # rows — byte-identical).
                    if not self.sectpos:
                        return 0
                    rows = pat_by_local[pid].rows
                    if rows and 'runon' in rows[-1].fx_flags:
                        return (sbase + sum(_row_secwidth(r)
                                            for r in rows)) & 0xFF
                    return 0

                # D6 piece 3 STICKY slot/vol: a note emits its instrument slot /
                # vol only where the SOURCE row states it (None = inherit -> the
                # player keeps its sticky curinst,x / volovr,x); duration is
                # always carried; rest/switch/slide carry a stated slot/vol too,
                # so a rest's instrument command still updates the sticky state.
                # Byte-keyed dedup then collapses the former per-entry ~intro
                # variants that differed only by carried slot/vol.
                def _gid_resolved(pid, resolved, sbase=0):
                    return _intern(
                        [_row_event_stated(rr, self.inst_slot)
                         for rr in resolved],
                        _pattern_secvals(pat_by_local[pid].rows, sbase)
                        if self.sectpos else None,
                        _pattern_tempos(pat_by_local[pid].rows))

                # ORDERLIST: sticky-TRANSPOSE physical stream (D6 piece 3). A
                # $FD,(T+64) transpose command wherever the transpose changes —
                # the original's sticky transpose command, at the stated MARKS —
                # then a 2-byte [gid, otrk] pattern entry, and a $FF 16-bit-BYTE
                # loop back to the loop_to entry. The player THREADS the transpose
                # over the loop wrap at runtime, exactly like the original engine
                # (which is single-pass, never duplicated), so there is no 2-pass
                # unroll and non-mark entries drop their transpose byte. otrk (the
                # sonified $1726 counter) stays the DERIVED per-entry value,
                # decoupled from this byte layout.
                loop_target = None
                if getattr(ol, 'stated', False):
                    P = len(ol.entries)
                    marks = list(ol.stated_marks or [None] * P)
                    extras = list(ol.extra_cmds or [0] * P)
                    intros = list(ol.intro_entries or [None] * P)
                    steady = [None] * P
                    offs = []
                    cum = 0
                    for i in range(P):
                        if marks[i] is not None:
                            cum += 1 + (extras[i] or 0)
                        offs.append(cum + i)
                    if _dmc_rows_stated(v):
                        iv = next((x for x in
                                   (sub.init.voices if sub.init else [])
                                   if x.id == v.id and
                                   (x.dur_field or x.instr)), None)
                        passes = resolve_voice(v, iv, n_passes=1)
                        gids, _sb = [], 0
                        for i in range(P):
                            gids.append(_gid_resolved(ol.entries[i],
                                                      passes[0][i], _sb))
                            _sb = _sbase_next(ol.entries[i], _sb)
                    else:
                        gids, _sb = [], 0
                        for i in range(P):
                            _pid = (intros[i] if intros[i] is not None
                                    else ol.entries[i])
                            gids.append(_gid_entry(_pid, _sb))
                            _sb = _sbase_next(_pid, _sb)
                            # ENDLESS self-loop tail (C32 r128 admission):
                            # an intro variant that ENCODES differently
                            # from its steady entry exists only at the
                            # loop slot (the fold scopes it there) — the
                            # lead plays once, then the loop re-fetches
                            # the steady entry at the SAME otrk (the
                            # orig's frozen wrap position). Carried-only
                            # intro variants dedup to the same gid and
                            # emit nothing extra (byte identity).
                            if intros[i] is not None and i == ol.loop_to:
                                g2 = _gid_entry(ol.entries[i], _sb)
                                if g2 != gids[i]:
                                    steady[i] = g2
                                    _sb = _sbase_next(ol.entries[i], _sb)
                    for i in range(P):
                        if i == ol.loop_to and steady[i] is None:
                            loop_target = len(track)
                        if marks[i] is not None:      # sticky transpose command
                            track += bytes([0xFD, (marks[i] + 64) & 0xFF])
                        track += bytes([gids[i], offs[i] & 0xFF])
                        if steady[i] is not None:
                            loop_target = len(track)
                            track += bytes([steady[i], offs[i] & 0xFF])
                else:
                    pad = int(usf.params.fields.get(
                        f'otrk_pad_s{sub.id}_v{v.id}', 0) or 0)
                    period = int(usf.params.fields.get(
                        f'otrk_period_s{sub.id}_v{v.id}', 0) or 0) \
                        or len(ol.entries) or 1
                    legacy = bool(usf.params.fields.get(
                        f'otrk_legacy_s{sub.id}_v{v.id}', 0))
                    rcmd = int(usf.params.fields.get(
                        f'otrk_rcmd_s{sub.id}_v{v.id}', 0) or 0)
                    # cur = the transpose the leading command already set; pad
                    # covers its byte. off/red model the sonified $1726 counter.
                    cur0 = ol.transpose_at(0) if ol.entries else 0
                    off, cur, red = pad, cur0, 0
                    prev_t = None
                    _sb = 0
                    for i, e in enumerate(ol.entries):
                        p = i % period
                        if i and p == 0:
                            off, cur, red = pad, cur0, 0  # physical-track boundary
                        gid = _gid_entry(e, _sb)
                        _sb = _sbase_next(e, _sb)
                        t = ol.transpose_at(i)
                        if t != cur:
                            off, cur = off + 1, t
                        if rcmd & (1 << p):
                            red += 1
                        # legacy: unmodeled counter phase (piecewise redundancy)
                        # -> the historical entry+1 approximation, unchanged
                        val = (i + 1) if legacy else (off + red)
                        if i == ol.loop_to:
                            loop_target = len(track)
                        if t != prev_t:               # sticky transpose command
                            track += bytes([0xFD, (t + 64) & 0xFF])
                            prev_t = t
                        track += bytes([gid, val & 0xFF])
                        off += 1

                # loop tail emitted by the data section as a label-arithmetic
                # 16-bit BYTE target ($FF, <lbl+off, >lbl+off): a variable-width
                # track can exceed 255 bytes, so both the loop target and the
                # runtime track position are 16-bit.
                if ol.stop:
                    track.append(0xFE)
                    voices.append((bytes(track), None))
                else:
                    voices.append((bytes(track),
                                   loop_target if loop_target is not None else 0))
            sid = sub.init.sid if (sub.init and sub.init.sid) else None
            mvol = sid.master_vol if sid and sid.master_vol is not None else 0x0F
            routing = (sid.filter.res_routing
                       if sid and sid.filter else 0)
            self.subtunes.append({
                'tracks': voices, 'speed': sub.tempo,
                'mvol': mvol, 'routing': routing,
                # per-subtune composer-param overrides (MusicSubtune.params —
                # compilation players disagreeing on a wedge knob, ledger C31)
                'params': dict(sub.params.fields) if sub.params else {},
            })
        # gid rides byte 0 of a track pattern entry; $FD/$FE/$FF are the
        # transpose-command / stop / loop opcodes, so gid must stay <= $FC.
        assert len(self.patterns) <= 253, 'pattern pool overflow (>253)'
        # wave pool with the original's jump-back marker semantics:
        # program bytes followed by $90+(len-loop). The idle program
        # (wave_programs[0]) sits at pool index 0 — the engine's
        # cleared wave position walks it before a voice's first note.
        self.wctrl = bytearray()
        self.wfreq = bytearray()
        self.iwst = []
        # The wave position is a single byte, so the whole pool must fit in
        # 256 bytes (assert below). The original packer SHARES wave programs:
        # instruments with an identical (ctrl, freq, loop) program read from
        # one pooled copy. The composer emits per-instrument programs; without
        # dedup a member with many same-timbre instruments inflates the pool
        # past 255 (the "wave pool overflow" error). Sharing is byte-identical
        # for the write stream (each instrument re-inits wavepos to its start
        # per note and reads the same byte sequence), so dedup is pure packing.
        _wseen = {}

        def add_prog(ctrl, freq, loop):
            n = len(ctrl)
            if n == 0:                       # wave_start past the table:
                raise RuntimeError(          # off-table read (architectural
                    'unsupported:zero_wave_table')   # limit; refuse cleanly)
            assert 0 <= loop < n and n - loop <= 0x6F, \
                f'wave program shape n={n} loop={loop}'
            cb = bytes(b & 0xFF for b in ctrl)
            fb = bytes(b & 0xFF for b in freq)
            key = (cb, fb, loop)
            if key in _wseen:                # identical program already pooled
                return _wseen[key]
            s = len(self.wctrl)
            self.wctrl += cb
            self.wctrl.append(0x90 + n - loop)
            self.wfreq += fb + b'\x00'
            _wseen[key] = s
            return s

        # Layout-preserving packing (wavepos_layout): place every program at
        # its editor wave-table position so wavepos,x == orig $177A,x at all
        # times (marker hops included — the marker byte and hop distance are
        # identical for verbatim slices, which the extract gate guarantees).
        # Overlapping placements come from ONE original table, so they agree
        # byte-for-byte (asserted). Marker slots claim only the ctrl byte —
        # the parallel freq byte under a marker is never read, but another
        # program's step may legitimately own it.
        _ctrl_at, _freq_at = {}, {}

        def place_prog(ctrl, freq, loop, pos):
            n = len(ctrl)
            if n == 0:
                raise RuntimeError('unsupported:zero_wave_table')
            assert 0 <= loop < n and n - loop <= 0x6F, \
                f'wave program shape n={n} loop={loop}'
            assert pos + n <= 255, 'wave pool overflow'
            cb = [b & 0xFF for b in ctrl] + [0x90 + n - loop]
            fb = [b & 0xFF for b in freq]
            for k, v in enumerate(cb):
                assert _ctrl_at.setdefault(pos + k, v) == v, \
                    'wave layout overlap conflict'
            for k, v in enumerate(fb):
                assert _freq_at.setdefault(pos + k, v) == v, \
                    'wave layout overlap conflict'
            return pos

        # POSITIONAL emission (wavepos_positional, phase 4): the full
        # 256-cell stated table, verbatim at its positions (jump cells as
        # the orig's $90+dist marker bytes, unstated cells zero). Emitting
        # all 256 cells makes the runtime's read domain equal the
        # resolver's (mod-256, no "absent cell" edge), so the composer can
        # PROVE equivalence: every program resolved over the emitted table
        # must equal its materialized (ctrl, freq, loop) — the C32
        # re-derivation assert at the compose side. A program that walked
        # off the stated cells (a hold-terminated resolve) fails the proof
        # and drops the member back to the repacked pool (honest residue,
        # never a wrong pool).
        if self.wavepos_positional:
            wt = usf.wave_table
            dense = {p: c for p, c in wt.items()}
            full = {i: dense.get(i, ('step', 0, 0)) for i in range(256)}
            # The idle walk validates against the TABLE'S OWN resolve from
            # position 0 — in positional mode the emitted pool IS this
            # chip's stated table, and that is also what the original
            # player freewheels over. (A 2SID merge carries ONE shared
            # wave_programs[0], which can structurally differ from the
            # carrier chip's own idle while emitting the identical hold
            # stream — chip 1's 10x$41 vs chip 2's 9x$41, Kordiaukis.)
            _ir = resolve_wave_table(wt, 0)
            progs = [(0, (list(_ir[0]), [b & 0xFF for b in _ir[1]],
                          _ir[2]))] if _ir is not None else []
            progs += [(inst.wave_start,
                       (list(inst.waveform),
                        [b & 0xFF for b in (inst.wave_freq
                                            or [0] * len(inst.waveform))],
                        inst.loop))
                      for inst in self.instruments]
            ok = True
            for start, want in progs:
                r = resolve_wave_table(full, start)
                if r is None or (list(r[0]), [b & 0xFF for b in r[1]],
                                 r[2]) != (want[0], want[1], want[2]):
                    ok = False
                    break
            if ok:
                self.wctrl = bytearray(
                    (0x90 + full[i][1]) & 0xFF if full[i][0] == 'jump'
                    else full[i][1] & 0xFF for i in range(256))
                self.wfreq = bytearray(
                    0 if full[i][0] == 'jump' else full[i][2] & 0xFF
                    for i in range(256))
                self.iwst = [inst.wave_start for inst in self.instruments]
                return
            self.wavepos_positional = False    # fall back to the repack

        first = place_prog if self.wavepos_layout else \
            (lambda ctrl, freq, loop, _pos: add_prog(ctrl, freq, loop))

        ip = usf.wave_programs.get(0)
        if ip and ip['ctrl']:
            first(ip['ctrl'], ip['freq'], ip.get('loop', 0), 0)
        elif self.instruments:
            i0 = self.instruments[0]
            first(i0.waveform, i0.wave_freq or [0] * len(i0.waveform),
                  i0.loop, getattr(i0, 'wave_table_pos', None) or 0)
        for inst in self.instruments:
            self.iwst.append(first(
                inst.waveform, inst.wave_freq or [0] * len(inst.waveform),
                inst.loop, getattr(inst, 'wave_table_pos', None)))
        if self.wavepos_layout:
            size = max(_ctrl_at) + 1
            self.wctrl = bytearray(_ctrl_at.get(k, 0) for k in range(size))
            self.wfreq = bytearray(_freq_at.get(k, 0) for k in range(size))
        else:
            assert len(self.wctrl) <= 255, 'wave pool overflow'

    def iflags(self, inst) -> int:
        f = 0
        if 'drum' in inst.effects:
            f |= 0x01
        if inst.filter_prog.keep_running:
            f |= 0x02
        if inst.pwm.keep_running:
            f |= 0x04
        if inst.envelope.gate_mode == 'open' or inst.envelope.gate_open:
            f |= 0x08
        if inst.envelope.gate_mode == 'hold':
            f |= 0x10
        if inst.filter_prog.program:
            f |= 0x20
        if inst.freq_slide_config.mode == 'run':
            f |= 0x40
        if 'noise_attack' in inst.effects:
            f |= 0x80
        return f


# ---------------------------------------------------------------------------
# asm emission
# ---------------------------------------------------------------------------

def _byt(data, per=16) -> str:
    lines = []
    for i in range(0, len(data), per):
        lines.append('        .byt ' + ', '.join(
            f'${b & 0xFF:02X}' for b in data[i:i + per]))
    return '\n'.join(lines) if lines else '        .byt $00'


def _reloc_sid_regs(asm: str, reg_delta: int, keep_regs=()) -> str:
    """Relocate the SID register operands ($D400-$D418) by `reg_delta` — used
    to point a second/third player instance at chip 2 ($D420) / chip 3
    ($D440). Only 4-hex-digit `$d4NN` words with NN in $00-$18 are register
    writes (verified: no data literal takes that form — the freq table etc.
    emit single bytes `$D4`, never words), so a targeted rewrite is safe.

    `keep_regs`: stores this chip's player directs at CHIP 1 rather than its
    own, because the editor's relocation missed those operands (C19) — e.g.
    Surgeon/Nice_Dream's res/route `$D417`, so both players' res/route land
    on chip 1. Probed per member by `factory._multisid_keep_regs`; empty (a
    fully relocated player) is the default and the common case.

    Two granularities, because the miss is per-STORE while a register can
    have several stores across different routines:
      * `0x17`             — every store to that register stays on chip 1;
      * `(0x00, 'sidwrite')` — only the stores to that register inside the
        block that starts at the composer label `sidwrite`.
    The label is the ROLE: the composer re-architects the player, so a canon
    store site is named by what its block DOES, not by an address. Scoping
    to "after label L, before the next label" works because the composer
    emits one label per routine and never interleaves them."""
    if reg_delta == 0:
        return asm
    plain = frozenset(k for k in keep_regs if isinstance(k, int))
    scoped = {}                       # label -> {reg}
    for k in keep_regs:
        if not isinstance(k, int):
            scoped.setdefault(k[1], set()).add(k[0])
    # safety: no $d4NN word may hide in a data line
    for ln in asm.split('\n'):
        code = ln.split(';')[0]
        if re.search(r'\.(byt|word|dsb)\b', code, re.I) and \
                re.search(r'\$d4[0-9a-f]{2}\b', code, re.I):
            raise AssertionError(f'$d4xx word in data line: {ln!r}')
    if scoped:
        missing = scoped.keys() - set(re.findall(r'^(\w+):', asm, re.M))
        if missing:
            raise AssertionError(f'keep_regs names unknown labels: {missing}')

    label = None
    out = []
    for ln in asm.split('\n'):
        m = re.match(r'^(\w+):', ln)
        if m:
            label = m.group(1)
        here = plain | scoped.get(label, set())

        def _sub(mobj, here=here):
            nn = int(mobj.group(1), 16)
            if nn > 0x18 or nn in here:
                return mobj.group(0)
            return f'${(0xD400 + nn + reg_delta):04x}'
        out.append(re.sub(r'\$d4([0-9a-f]{2})\b', _sub, ln, flags=re.I))
    return '\n'.join(out)


def _materialize_wave_table(usf: UsfFile) -> None:
    """Wave-table normal form (live_signal_modulation_draft §4): expand the
    stated `wave_table` block into the legacy in-memory fields (instrument
    waveform/wave_freq/loop + the idle wave_programs[0]) through the ONE
    shared resolver, so every downstream consumer is unchanged. The melodic
    signed-offset convention mirrors the extract writer exactly. No-op for
    resolved-copy members."""
    wt = getattr(usf, 'wave_table', None)
    if not wt:
        return
    for inst in usf.instruments:
        ws = getattr(inst, 'wave_start', None)
        if ws is None:
            continue
        r = resolve_wave_table(wt, ws)
        if r is None:
            raise RuntimeError(
                f'unsupported:wave_table_resolve i{inst.id} @{ws}')
        c, f, loop = r
        inst.waveform = list(c)
        drum = 'drum' in (getattr(inst, 'effects', None) or frozenset())
        inst.wave_freq = (list(f) if drum else
                          [b - 256 if b >= 128 else b for b in f])
        inst.loop = loop
    if not usf.wave_programs.get(0):
        r = resolve_wave_table(wt, 0)
        if r is None:
            raise RuntimeError('unsupported:wave_table_resolve idle @0')
        usf.wave_programs[0] = {'ctrl': list(r[0]), 'freq': list(r[1]),
                                'loop': r[2]}


def denormalize_wave_table(usf: UsfFile) -> UsfFile:
    """Convert a wave-table NORMAL-FORM UsfFile back to the resolved-copy
    form in place (materialize through the shared resolver, then strip the
    block + pointers). For MERGE paths that consume a written single-player
    part and rebuild a combined UsfFile from pieces — the combined file has
    no wave_table, so pointer instruments must be expanded first (the
    zero_wave_table class the phase-2 regression caught). No-op for
    resolved-copy files."""
    _materialize_wave_table(usf)
    usf.wave_table = None
    for inst in usf.instruments:
        if getattr(inst, 'wave_start', None) is not None:
            inst.wave_start = None
    return usf


def compose_dmc_asm(usf: UsfFile, *, origin: int = 0x1000,
                    reg_delta: int = 0, keep_regs=()) -> str:
    _materialize_wave_table(usf)
    m = _Model(usf)
    insts = m.instruments
    n = len(insts)

    # ---- per-instrument parallel data ----
    iad = [i.adsr[0] for i in insts]
    isr = [i.adsr[1] for i in insts]
    ipwinit = [(i.pwm.init >> 8) & 0x0F for i in insts]
    ipwmin = [i.pwm.min_hi for i in insts]
    ipwmax = [i.pwm.max_hi for i in insts]
    # instrument-record byte offset (orig inst# * 11, exact 6502 chain) — the
    # value the orig keeps in $174D,x; shadowed in ioff,x for off-table reads.
    ioffval = [_inst_offset(i.id - 1) for i in insts]
    # wjmp chase shadow (extract wave_start_on_marker): an instrument the editor
    # started ON its own loop marker chases back n on the first read every
    # note-init, storing $171F=n. The composer packs the settled program (no
    # transient chase), so it re-asserts wjmp=n at note-init for these (the hop
    # then repeats every settled frame, matching the orig). Distance = program
    # length n; 0 = no chase. Emitted + wired only when some instrument chases.
    # A POSITIONAL pool needs no chase re-assert: iwst points at the raw
    # marker cell and the first wave step performs the orig's chase (with
    # its wjmp write) natively.
    iwchase = [0] * len(insts) if m.wavepos_positional else \
        [len(i.waveform) & 0xFF if getattr(i, 'wave_start_on_marker', False)
               else 0 for i in insts]
    _any_chase = any(iwchase)
    # PULSE-STEP INDEX WIDTH (ledger C8 — widen the composer's own index).
    # fx_pulse reaches an instrument's step records with `id*8 + pwphase`, an
    # 8-bit index, so the stride-8 layout caps the pool at 32 instruments — a
    # merged compilation can carry more (Lane_Crazy: 39, its high ids wrapping
    # onto player 0's records and diverging on V1 PW lo at write 24). Above the
    # cap, pack the records at their true width (6) and give each instrument a
    # base BYTE, which keeps the index 8-bit (and costs one cycle LESS than the
    # three shifts). GATED on the count so every member that fits stride 8
    # emits byte-identical code.
    wide_pulse = len(insts) > 32
    istride = 6 if wide_pulse else 8
    istepbase = [k * istride for k in range(len(insts))]
    assert not wide_pulse or istepbase[-1] + 5 < 256, \
        f'{len(insts)} instruments overflow the pulse-step base byte'
    pulse_index = (
        '        ldy cinst,x\n'
        '        lda istepbase,y              ; compact stride-6 pool (>32\n'
        '        clc                          ; instruments — the id*8 shift\n'
        '        adc pwphase,x                ; would overflow the 8-bit index)\n'
        '        tay\n'
        if wide_pulse else
        '        lda cinst,x\n'
        '        asl\n'
        '        asl\n'
        '        asl\n'
        '        clc\n'
        '        adc pwphase,x\n'
        '        tay\n')
    isteps = []
    ipwbase = []
    irawsp = []
    for i in insts:
        ss = list(i.pwm.speed_steps) or [i.pwm.speed] * 6
        ss = (ss + [ss[-1]] * 6)[:6]
        base = ss[0] & 0x0F
        assert all((s & 0x0F) == base for s in ss), \
            f'inst {i.id}: pulse steps do not share a base nibble'
        ipwbase.append(base)
        isteps += ([s & 0xF0 for s in ss] + [0, 0])[:istride]
        # raw instr+3..5 speed bytes (hi nibble = even-phase step, lo nibble =
        # odd-phase step >> 4 — exact inverse of the extract's nibs decode),
        # duplicated per parity so fx_pulse reuses the isteps index. Feeds the
        # wjmp shadow of orig $171F ($1357: LDA raw / STA $171F).
        raw3 = [(ss[2 * k] & 0xF0) | ((ss[2 * k + 1] & 0xF0) >> 4)
                for k in range(3)]
        irawsp += [raw3[0], raw3[0], raw3[1], raw3[1],
                   raw3[2], raw3[2], 0, 0][:istride]
    # dual_freq_generator pulse-step extension (factory._dual_freq_gen_probe):
    # the wedge
    # forces pwphase to P0/P0+1 every dual frame (+<=2 flip INCs), so
    # fx_pulse indexes isteps/irawsp at cinst*8+P far past the canon 0-5
    # range. The orig reads the same positions off the END of the record
    # (static bytes, captured extract-side as dual_gen_steps =
    # 'usfid:rawA:rawB:rawC,...'); extend both tables with the equivalent
    # entries — everything in between stays 0.
    dhs = str(usf.params.fields.get('dual_generator_steps', '') or '')
    dh_param = str(usf.params.fields.get('dual_freq_generator', '') or '')
    if dhs and dh_param:
        if wide_pulse:
            # The wedge's off-the-end reads are positions in the STRIDE-8
            # layout; under the compact layout they would land inside a later
            # instrument's real records. No member carries both today (the
            # wedge is a single-player probe, the compact layout a merged
            # compilation) — refuse rather than emit a plausible wrong table.
            raise ValueError('dual_freq_generator + >32 instruments: the '
                             'pulse-step extension has no compact-layout form')
        p0 = (0x19 + int(dh_param.split(',')[1])) & 0xFF
        pos_by_id = {i.id: k for k, i in enumerate(insts)}
        ext = {}
        for ent in dhs.split(','):
            uid, *raws = (int(t) for t in ent.split(':'))
            k = pos_by_id.get(uid)
            if k is None:
                continue
            for p in range(p0, p0 + 4):
                raw = raws[(p >> 1) - (p0 >> 1)]
                idx = (k * 8 + p) & 0xFF
                if idx < len(insts) * 8:
                    continue                     # never clobber real entries
                ext[idx] = ((raw & 0x0F) << 4 if p & 1 else raw & 0xF0, raw)
        if ext:
            n = max(ext) + 1
            isteps += [0] * (n - len(isteps))
            irawsp += [0] * (n - len(irawsp))
            for idx, (sv, rv) in ext.items():
                isteps[idx] = sv
                irawsp[idx] = rv
    ifdef = [m.filter_slots.get(i.filter_prog.program, 0) for i in insts]
    ivdel = [i.vibrato.onset for i in insts]
    ivwid = [i.vibrato.amplitude for i in insts]
    ivram = []
    for i in insts:
        if i.freq_slide_config.mode == 'run':
            s = i.freq_slide_config
            ivram.append((s.step & 0x7F) | (0x80 if s.initial_dir == 'up' else 0))
        else:
            ivram.append(i.vibrato.ramp & 0xFF)
    iflag = [m.iflags(i) for i in insts]
    iwst = m.iwst

    fd = m.filter_defs
    fdres = [(d['res'] << 4) & 0xF0 for d in fd]
    fdmode = [(d['mode'] << 4) & 0xF0 for d in fd]
    fdinit = [d['init'] for d in fd]
    fdrep = [d['repeat'] for d in fd]
    fdstop = [d['stop'] for d in fd]
    # fdrec = the orig's 16-byte def RECORD layout, dense in orig def# order:
    # [res<<4|mode, init, repeat, stop, size*6, dur*6]. The walk arrays are
    # VIEWS into it (fdstep = fdrec+4, fddur = fdrec+10), so a step index that
    # overruns its def (repeat > 5: the INC/CMP #6 wrap never fires again and
    # the index walks upward forever) reads size/duration bytes from ADJACENT
    # records — byte-identical to the orig by construction (C2 extended
    # window; the extract ships 17 records = the full 266-byte window). The
    # old 12-byte stride matched only within-def overruns (index 6..11);
    # cross-def walks read the wrong bytes (Psycho_Tune's repeat=$1F).
    fdrec = []
    for d in fd:
        steps = (d['steps'] + [(0, 0)] * 6)[:6]
        fdrec += ([((d['res'] << 4) | (d['mode'] & 0x0F)) & 0xFF,
                   d['init'] & 0xFF, d['repeat'] & 0xFF, d['stop'] & 0xFF]
                  + [s & 0xFF for s, _ in steps]
                  + [f & 0xFF for _, f in steps])

    # rest / switch / slide fetch-frame effect behaviour (see the rest_effects
    # block below for semantics). Computed HERE because a COMPILATION's packed
    # players can DISAGREE on the knob (ledger C31 — Super_Seven: player 0
    # family-2 'skip', player 1 canon 'run'): each subtune's effective value =
    # its MusicSubtune.params override, else the file-level key. WIDENING IS
    # GATED like the per-subtune idle priming: unless subtunes actually
    # disagree, the static single-target form below is emitted byte-identically
    # (tune-record byte +9 stays $00, no resteff var, no dispatcher).
    _file_rest = str(usf.params.fields.get('rest_effects', 'run'))
    _rest_code = {'run': 0, 'skip': 1, 'vibflip': 2, 'none': 3}
    sub_rest = [str(s['params'].get('rest_effects', _file_rest))
                for s in m.subtunes] or [_file_rest]
    per_sub_rest = len(set(sub_rest)) > 1

    # ---- tune records + tracks + patterns ----
    tune_lines = []
    track_blobs = []
    for si, sub in enumerate(m.subtunes):
        refs = []
        for vi in range(3):
            lbl = f'trk_{si}_{vi}'
            track_blobs.append((lbl, sub['tracks'][vi]))
            refs.append(lbl)
        # +9 = per-subtune rest-effects code (only when subtunes disagree)
        rcode = _rest_code.get(sub_rest[si], 0) if per_sub_rest else 0
        tune_lines.append(
            f'        .byt <{refs[0]}, >{refs[0]}, <{refs[1]}, >{refs[1]}, '
            f'<{refs[2]}, >{refs[2]}, ${sub["speed"]:02X}, ${sub["mvol"]:02X}, '
            f'${sub["routing"]:02X}, ${rcode:02X}, $00, $00, $00, $00, $00, $00')
    def _ptr_tab(pfx):
        lines = []
        for i in range(0, len(m.patterns), 12):
            lines.append('        .byt ' + ', '.join(
                f'{pfx}pat_{k}' for k in range(i, min(i + 12, len(m.patterns)))))
        return '\n'.join(lines)
    pat_lo = _ptr_tab('<')
    pat_hi = _ptr_tab('>')

    slide_phase = int(getattr(usf.init, 'slide_phase', 0) or 0) & 1
    # Per-subtune half-rate slide-clock phase (compilation players with
    # DISAGREEING $1019 leftovers — Chwat). Gated: single-phase members emit
    # the constant-immediate form byte-identically.
    _ssp = [(getattr(sub.init, 'slide_phase', None) if sub.init else None)
            for sub in usf.subtunes]
    per_sub_sphase = any(v is not None and (v & 1) != slide_phase
                         for v in _ssp)
    sphase_vals = [slide_phase if v is None else v & 1 for v in _ssp]
    sphase_load = ('        tax                          ; per-subtune slide phase\n'
                   '        lda sphase,x\n'
                   '        sta dualpar\n'
                   '        txa\n') if per_sub_sphase else ''
    sphase_const = ('' if per_sub_sphase else
                    '        lda #SLIDE_PHASE             ; half-rate slide clock phase\n'
                    '        sta dualpar\n')
    # noise-attack (cymbal) onset: 0 = the burst fires at note-init
    # (canon — frame 1); 1 = one frame later (family 2 — frame 2, gated
    # by the post-note guard). A musical timing parameter of the effect.
    cymbal_onset = int(usf.params.fields.get('cymbal_onset', 0)) & 1
    # cymbal noise-burst freq value: the immediate written to $D400/$D401 for
    # the gated-noise attack. Canon is $FFFF (LDA #$FF), but the value is an
    # extracted per-member operand — a few demos patch it (e.g. Presentation's
    # $DF) for a different noise timbre. Read from the binary, default $FF.
    cymbal_burst = int(usf.params.fields.get('cymbal_burst', 0xFF)) & 0xFF
    # vibrato swell mechanism (two builds of the same engine ramp the
    # triangle differently): 'width' (canon) holds a fixed per-note step
    # (the $1888 VIBDEPTH table) and DOUBLES the half-cycle width as it
    # swells in; 'step' (family 2) holds a fixed width and RAMPS the step
    # by freq_hi(note)>>1 each half-cycle (16-bit). The per-note increment
    # is derived from the freq table the composer already carries.
    vib_ramp = str(usf.params.fields.get('vib_ramp', 'width'))
    # holding-instrument gate-off: 'adsr_clear' (canon) also zeroes AD+SR
    # (the original's sub_17EC); 'mask_only' (family 2) just drops the gate
    # bit via the mask. Family 2 relocated its instrument table over
    # sub_17EC and inlines a mask-only gate-off, so holding voices keep
    # their AD/SR at note-end (no $D405/$D406=$00 write).
    hold_gateoff = str(usf.params.fields.get('hold_gateoff', 'adsr_clear'))
    hold_adsr_clear = ('' if hold_gateoff == 'mask_only' else
                       '        ldy sidoff,x\n'
                       '        lda #$00\n'
                       '        sta $d405,y                  ; AD = 0\n'
                       '        sta $d406,y                  ; SR = 0\n')
    # hard-restart envelope preset: 'preset' (canon) writes AD=$0F SR=$0F
    # (the original's sub_17FB) on the note-fetch frame; 'none' (family 2)
    # writes only the $08 TEST bit (its relocated instrument table clobbers
    # sub_17FB, so the hard restart drops the AD/SR=$0F0F writes). A numeric
    # value (C19 wedge, Stryyker: the sub_17FB `LDA #$0F` immediate patched
    # to another byte) primes AD=SR=that value instead. 'skip' (C19 wedge,
    # SilverFox/Seaside_99: the note-load's `JSR sub_17FB` opcode patched
    # $20->$2C = BIT) neuters the ENTIRE prep call — the fetch frame writes
    # NOTHING (no TEST bit, no AD/SR); pending is still set so the note inits
    # normally next frame, and the old note rings through the fetch frame.
    # Distinct from 'none', which keeps the $08 TEST write (hr_test_write
    # forced '' below).
    hard_restart = str(usf.params.fields.get('hard_restart', 'preset'))
    if hard_restart in ('none', 'skip'):
        hard_restart_adsr = ''
    else:
        hr_val = 0x0F if hard_restart == 'preset' else int(hard_restart) & 0xFF
        hard_restart_adsr = (f'        lda #${hr_val:02X}\n'
                             f'        sta $d405,y                  ; AD = ${hr_val:02X}\n'
                             f'        sta $d406,y                  ; SR = ${hr_val:02X}\n')
    # rest / switch / slide (duration events that don't retrigger): canon
    # runs the full effect chain on the fetch frame ('run'); family 2 skips
    # straight to the wave step ('skip', the original's JMP $1591) — so the
    # vibrato + pulse program hold for that one frame (a one-frame modulator
    # stall at each tie boundary).
    # a third sub-build JMPs the mid-routine vibrato half-cycle entry (canon
    # $1567, 'vibflip'): rest frames flip the vibrato direction + wave-step.
    # `sub_rest`/`per_sub_rest` are computed above the tune-record loop. When
    # every subtune agrees, the single static target keeps the emitted image
    # byte-identical; a disagreement (compilation, C31) routes the fetch-frame
    # JMP through a 3-way dispatcher on `resteff` (loaded at init from the
    # tune record's +9 byte).
    if per_sub_rest:
        rest_jmp = 'rest_dispatch'
    else:
        rest_jmp = {'skip': 'wavestep', 'vibflip': 'vib_half',
                    'none': 'rest_none'}.get(sub_rest[0], 'run_effects')
    rest_load = ('        lda tunetab+3,y              ; +9 = per-subtune '
                 'rest-effects code\n'
                 '        sta resteff\n' if per_sub_rest else '')
    # 'none' (C19 RTS wedge, Bassy_Introtune: canon $1180 JMP $1322 -> RTS):
    # the fetch frame runs NO effects at all for the voice — not even the
    # wave-step SID refresh ('skip' still refreshes). Label + the extended
    # dispatcher arm are emitted ONLY when some subtune uses it, so every
    # existing member (incl. per-sub dispatch members) stays byte-identical.
    _has_none = 'none' in sub_rest
    rest_none = 'rest_none:\n        rts\n' if _has_none else ''
    rest_dispatch = (('''rest_dispatch:                       ; fetch-frame effect behaviour,
        lda resteff                  ; per-subtune (0=run 1=skip 2=vibflip
        bne rd_ns                    ;  3=none)
        jmp run_effects
rd_ns:
        cmp #$03
        beq rest_none
        lsr
        bne rd_vf
        jmp wavestep
rd_vf:
        jmp vib_half
''' if _has_none else '''rest_dispatch:                       ; fetch-frame effect behaviour,
        lda resteff                  ; per-subtune (0=run 1=skip 2=vibflip)
        bne rd_ns
        jmp run_effects
rd_ns:
        lsr
        bne rd_vf
        jmp wavestep
rd_vf:
        jmp vib_half
''') if per_sub_rest else '')
    rest_var = 'resteff:  .dsb 1, 0\n' if per_sub_rest else ''
    # tempo event (fx `tempo=N`, ledger C14 — the Doxx v3_instr_tempo build):
    # a gated [$05, N] pattern prefix consumed at the row fetch, setting the
    # speed RELOAD (the running counter is untouched, so the change takes
    # effect at the next reload — exactly the original's play-tail mailbox).
    # Emitted only when some pattern carries a tempo row; everyone else's
    # dispatcher is byte-identical.
    _has_tempo = any(f.startswith('tempo=')
                     for sub in usf.subtunes
                     for v in (getattr(sub, 'voices', None) or [])
                     for p in v.patterns for r in p.rows for f in r.fx_flags)
    tempo_evd = ('''        cmp #$05
        bne evd5
        ldy #$01
        lda ($f8),y                  ; tempo event: speed reload = N
        sta spd
        lda #$02
        jsr adv                      ; consume [$05, N], re-dispatch the row
        jmp patrd
evd5:
''' if _has_tempo else '')
    # SWITCH ($7D tie/legato) gate-mask toggle bits (C19 wedge,
    # Bax/Feed_a_Bird — 1 family-1 carrier): the switch handler EORs this
    # onto the voice's gate mask. Canon $01 toggles ONLY the gate bit
    # ($FF<->$FE = release the gate); the wedge $1F toggles
    # gate+test+ring+sync+triangle ($FF<->$E0), so a switch CUTS a
    # triangle/ring/sync note to silence ($17&$E0=$00) instead of merely
    # gating it off ($17&$FE=$16). Default $01 -> byte-identical.
    switch_toggle = int(usf.params.fields.get('switch_toggle_mask', 1)) & 0xFF
    switch_eor = f'#${switch_toggle:02X}'
    # PW-hi register source (C19 wedge, Olsen/Lame — 1 family-1 carrier):
    # the sidwrite tail's `LDA $1753,x / STA $D403,y` is re-pointed at
    # another per-voice byte ($1707,x = the track-ptr lo triple, constant
    # after init), pinning each voice's AUDIBLE PW hi at a per-voice
    # constant while the internal PWM state machine still runs on $1753
    # (note-init store + bound compares untouched). pw_hi_const = 'a,b,c'
    # carries the post-init constants; absent -> canon (byte-identical).
    pw_hi_const = str(usf.params.fields.get('pulsewidth_hi_const', '') or '')
    pw_hi_load = ('        lda pwhic,x                  ; patched PW-hi source'
                  if pw_hi_const else '        lda pwh,x')
    # Drum (absolute-freq) wave-step hi-store repoint (C19 wedge,
    # Heinmueck/Enforcer_2_Level_1_preview — sole family-1 carrier, see
    # factory._drum_fhi_probe): the canon $15FD `STA $1732,x` (fbh) is
    # re-pointed at $1754,x = pwh+1, so an absolute drum step zeroes fbl but
    # LEAVES the voice's freq hi at the note's base value, while the wave
    # table's freq byte pokes the NEXT voice's PW-hi running state. (X=2
    # would land on the orig's PW-min bound slot, but that carrier's V3
    # play unit is removed — unreachable.) Default -> byte-identical.
    drum_fhi_pw = str(usf.params.fields.get('drum_fhi_to_pw', '') or '')
    ws_drum_fhi = ('        sta pwh+1,x                  ; C19: -> next voice'
                   ' PW hi (fbh keeps note base)'
                   if drum_fhi_pw else '        sta fbh,x')
    # Deferred-wave note-init (OBSERVED build variant, C23 write-footprint —
    # factory._noteinit_defer_probe; carrier: the re-assembled Heinmueck
    # build, Redable_Rain): the note-INIT frame writes SR+AD and the state
    # setup only — its note-init routine RTSes instead of falling through
    # the wave step, so the note's first freq/PW/ctrl (gate-on) land on the
    # NEXT play(). Default = canon (init frame runs the wave step).
    ni_defer = str(usf.params.fields.get('noteinit_defer_wave', '0')) == '1'
    ni_wave_tail = ('        rts                          ; deferred-wave '
                    'build: first wave step next play'
                    if ni_defer else '        jmp wavestep')
    # Dual-effect freq-generator wedge (C19 4th occurrence, Taurus/Taurus_02,
    # the only family-1 carrier — see factory._dual_freq_gen_probe): the member's
    # odd-parity dual path is byte-edited (`LDX $2F` -> X=$A9) so every
    # per-voice read lands on fixed CODE bytes, turning the per-note slide
    # into ONE global free-running freq ramp; the "accumulator" self-modifies
    # two tune-setup code bytes (file-image values = the seed), the update
    # ORs in a BASIC ROM byte ($BD68,y) and rotates a feedback byte via an
    # illegal RRA. The composer reproduces the WRITE STREAM with clean code
    # (legal ror+adc, inlined constants); the pwphase store keeps the orig's
    # live-carry dependence (C chains from the pulse machine's last CMP).
    # dual_freq_generator = 'step,ph_add,base_hi,pw_lo,pw_hi,ctrl,seed_lo,seed_hi,slot'.
    dual_gen = str(usf.params.fields.get('dual_freq_generator', '') or '')
    if dual_gen:
        (dh_step, dh_ph, dh_bhi, dh_pwl, dh_pwh, dh_ctrl, dh_slo, dh_shi,
         dh_slot) = [int(t) & 0xFF for t in dual_gen.split(',')]
        if dh_step & 0x80:
            # wedge with slide bit7: the orig's UP branch is unpatched canon
            # (accum -= step&$7F, no ROM/RRA feedback)
            dh_upd = f"""        lda hacc
        sec
        sbc #${dh_step & 0x7F:02X}
        sta hacc
        lda hacch
        sbc #$00
        sta hacch"""
        else:
            dh_upd = f"""        lda hacc                     ; ramp update - exact orig carry chain
        clc
        adc #${dh_step:02X}
        sta hacc
        lda hacch
        adc #$00
        adc #${dh_step:02X}
        ora hromv,y                  ; BASIC ROM $BD68,y (env constant)
        ror hrra                     ; legal-op RRA (= ror mem + adc mem)
        adc hrra
        and #$7F
        sta tmp
        lda hacc
        sec
        sbc tmp
        sta hacc
        lda hacch
        sbc #$00
        sta hacch"""
        dual_run = f"""fx_dual_run:                         ; dual_freq_generator wedge (Taurus_02)
        ldy sidoff,x
        adc #$18                     ; A=parity(1), C live from pulse CMP
        adc #${dh_ph:02X}
        sta pwphase+{dh_slot}        ; the wedge's repointed dtmpl store
        lda #${dh_bhi:02X}
        sta dtmph                    ; orig $1725 (idx-222 off-table readers)
        lda dtmpl                    ; canon $1724 - wiped, never written here
        sec
        sbc hacc
        sta $d400,y
        lda #${dh_bhi:02X}
        sbc hacch
        sta $d401,y
{dh_upd}
        lda #${dh_pwl:02X}           ; sidwrite tail with X=$A9 - PW and ctrl
        sta $d402,y                  ; come from fixed code bytes
        lda #${dh_pwh:02X}
        sta $d403,y
        lda #${dh_ctrl:02X}
        sta $d404,y
        rts"""
        dual_vars = (f'hacc:     .byt ${dh_slo:02X}          '
                     '; dual_freq_generator ramp accum (file-image seed)\n'
                     f'hacch:    .byt ${dh_shi:02X}\n'
                     'hrra:     .byt $00              ; RRA feedback (orig zp $12)\n'
                     'hromv:    .byt $B4,$BF,$48,$24,$5F,$10,$02,$E6\n'
                     '          .byt $5D,$20,$E2,$BA,$68,$38,$E9 '
                     '; BASIC ROM $BD68-$BD76\n')
    else:
        dual_run = """fx_dual_run:
        ldy sidoff,x
        lda fbl,x
        clc
        adc accl,x
        sta tmp
        sta dtmpl                    ; orig $1724: the dual-slide freq temp is
        lda fbh,x                    ; a GLOBAL leftover ("last dual voice's
        adc #$00                     ; base+accum") that off-table reads
        sta tmp2                     ; sonify (idx 221) — shadow it 1:1
        lda tmp2
        sta dtmph                    ; orig $1725
        lda tmp
        sec
        sbc slal,x
        sta $d400,y
        lda tmp2
        sbc slah,x
        sta $d401,y
        lda cvram,x                  ; slide byte: bit7 = up
        bmi fx_dual_up
        lda slal,x
        clc
        adc cvram,x
        sta slal,x
        lda slah,x
        adc #$00
        sta slah,x
        jmp pwwrite
fx_dual_up:
        and #$7F
        sta tmp
        lda slal,x
        sec
        sbc tmp
        sta slal,x
        lda slah,x
        sbc #$00
        sta slah,x
        jmp pwwrite"""
        dual_vars = ''
    # sectpos shadow (params sectpos_shadow): each pattern event carries its
    # row's visible orig sector-position after the opcode; every handler
    # stores it to sectpos,x at fetch and all event field/advance offsets
    # shift by one. Default (no shadow) is byte-identical to the un-gated
    # composer. See DMC_SECTPOS_ROW.
    sectpos_on = m.sectpos
    g = 1 if sectpos_on else 0
    sp_fetch = ('        ldy #$01\n'
                '        lda ($f8),y                  ; per-row sectpos value\n'
                '        sta sectpos,x                ; live $1729 shadow\n'
                if sectpos_on else '')
    sectpos_bss = ('sectpos:  .dsb 3, 0                  '
                   '; orig sector-position shadow (= $1729)\n'
                   if sectpos_on else '')
    ev1 = f'#${1 + g:02X}'               # first event field (after opcode)
    ev3 = f'#${3 + g:02X}'               # note event: duration field
    ev6 = f'#${6 + g:02X}'               # note event: glide-speed field
    adv2 = f'#${2 + g:02X}'              # rest/switch event length
    adv4 = f'#${4 + g:02X}'              # slide event length
    adv6 = f'#${6 + g:02X}'              # note event length
    adv8 = f'#${8 + g:02X}'              # note+glide event length
    # hard-restart-patch variant (The_Syndrom / Tragic_Error / Gaston): a
    # canon player with two note-init wedges. $1230 JSRs $125A, which parks
    # the SR byte and passes #$99 to sub_184B, whose first STA now targets
    # $17FB — the OPCODE of the hard-restart primer's ctrl write (SMC).
    # $99 = STA $D404,y (TEST bit written); the pulse-reset path's $1262
    # wedge then rewrites it to $B9 = LDA $D404,y (TEST write skipped). Net
    # per note-init: the NEXT hard restart writes the $08 TEST bit iff the
    # instrument has the $04 no-pulse-reset flag. The $1257 JMP $1262 that
    # feeds the wedge also skips loading the PW step base ($175F stays 0
    # forever) and the PW phase/direction reset (both persist across
    # notes). hr_test_init = the file-image opcode at $17FB ($99 -> 1),
    # i.e. the toggle state before the first note-init.
    hr_patch = str(usf.params.fields.get('hardrestart_smc_variant', '0')) == '1'
    hr_test_init = int(usf.params.fields.get('hardrestart_test_init', 1)) & 1
    if hr_patch:
        hr_test_write = ('        lda hrtest\n'
                         '        beq hr_notest\n'
                         '        lda #$08\n'
                         '        sta $d404,y                  ; TEST (gated)\n'
                         'hr_notest:\n')
        hr_arm = ('        lda #$01\n'
                  '        sta hrtest                   ; $125A wedge ($99)\n')
        hr_disarm = ('        lda #$00\n'
                     '        sta hrtest                   ; $1262 wedge ($B9)\n')
        pw_base_reset = ''
        hr_test_var = f'hrtest:   .byt ${hr_test_init:02X}\n'
    else:
        # hr_prep_gate (OBSERVED build variant, with noteinit_defer_wave —
        # the re-assembled Heinmueck build): the hard-restart prep writes
        # ctrl $08 then $09 (TEST, then TEST|GATE) before the $0F0F.
        if str(usf.params.fields.get('hr_prep_gate', '0')) == '1':
            hr_test_write = ('        lda #$08\n'
                             '        sta $d404,y                  ; TEST bit\n'
                             '        lda #$09\n'
                             '        sta $d404,y                  ; TEST|GATE\n')
        else:
            hr_test_write = ('        lda #$08\n'
                             '        sta $d404,y                  ; TEST bit\n')
        hr_arm = hr_disarm = hr_test_var = ''
        # pw_dir_persist: C19 wedge — the canon `STA $1765,x` (direction=up)
        # is re-pointed at an unused state byte, so the PWM sweep DIRECTION
        # persists across note-inits while value/bounds/step/phase still reset.
        pw_base_reset = ('        lda ipwbase,y\n'
                         '        sta cpwbase,x\n'
                         '        lda #$00\n'
                         '        sta pwphase,x\n')
        if str(usf.params.fields.get('pulsewidth_dir_persist', '0')) != '1':
            pw_base_reset += '        sta pwdir,x\n'
    # 'skip' wedge: the whole `JSR sub_17FB` is neutered ($20->$2C BIT), so the
    # fetch frame emits NO prep at all — drop the TEST write too (the ADSR was
    # already dropped above). Overrides the hr_patch conditional TEST.
    if hard_restart == 'skip':
        hr_test_write = ''
    # CIA multispeed: when the original drives play() via a CIA1 timer
    # (PSID speed bit set), the rebuild programs the SAME timer A latch
    # so libsidplayfp calls OUR play() at the identical rate. 0 = VBI.
    cia_period = int(usf.environment.cia_period if usf.environment else 0) & 0xFFFF
    cia_init = ''
    if cia_period:
        cia_init = (
            '        lda #<CIA_PERIOD\n'
            '        sta $dc04                    ; CIA1 timer A lo (play rate)\n'
            '        lda #>CIA_PERIOD\n'
            '        sta $dc05                    ; CIA1 timer A hi\n'
            '        lda #$11\n'
            '        sta $dc0e                    ; start timer A, continuous\n')
    # internal multispeed (vblank, NO speed bit): the play vector runs the
    # engine N times per VBI. Emit the JT play entry as an N-fold JSR wrapper
    # (the original's `JSR play x N : RTS`), so each VBI logs N play()s worth of
    # writes — matching the orig's per-frame write count under flat capture.
    play_repeat = max(1, int(usf.environment.play_repeat if usf.environment else 1))
    # PLAY-PHASE wrapper (factory-observed, ledger C9): the original's play
    # vector cycles full-play / effects-only calls — the DMC slow-tempo /
    # smooth-effects editing trick (e.g. 'PFFF' = full play every 4th call;
    # the other calls run the per-voice frame entry $11F9 directly: pending
    # note-init / running effects, NO tick, NO $D416/$D417 tail). Reproduce
    # the mechanism: a phase counter dispatching full-play (P), fx-only (F)
    # or silence (S) per call. phasectr lives in code (not the cleared state
    # block), seeded so call #1 executes phases[0] = the observed sequence.
    play_phases = str(usf.params.fields.get('play_phases', '') or '')
    tokens = [t for t in play_phases.split('_') if t] if play_phases else []
    # notestart_arm: the F phase enters the wave step PAST the note-init check,
    # so a fetched note ARMS on the F call (wave-step only, envelope held at the
    # $0F0F hard-restart leftover) and note-init fires on the NEXT P call — the
    # DMC 2-frame note-start. Factory-observed per member (not schedule-derived:
    # Words and F.A.K.E are both P_F123 but differ). Default 0 = note-init on the
    # F call (orig $11F9 -> frame_entry), the immediate-note-start majority.
    notestart_arm = str(usf.params.fields.get('noteinit_deferred', '0')) == '1'
    # fx_entry='vibflip': the arm F phase enters at the vibrato half-cycle
    # boundary (canon $1567: vibctr=0, flip vibdir, swell, fall through the
    # wave step) instead of the plain wave step — the F call's own writes are
    # identical, but the flips reshape the vibrato (3 flips between full
    # plays => a +/-vstep square where wavestep entry free-runs the triangle).
    fx_entry = str(usf.params.fields.get('effect_entry_variant', '') or '')
    voice_fx_target = ('vib_half' if fx_entry == 'vibflip' else 'wavestep') \
        if notestart_arm else 'frame_entry'
    # rphase_variant='pulse_tail' (C18 entry variant, R-phase twin of
    # effect_entry_variant): the R (non-tick) play phase re-runs the pulse
    # program TAIL — a SECOND pulse advance per music tick — instead of a plain
    # register refresh (fx_glide). The orig's play-vector wrapper alternates
    # full-play / `$162F: JSR $135D x3`, where $135D is the pulse routine PAST
    # its `LDA $18f3,y / STA $171F` speed-nibble reload, so the tail computes
    # its step from the STALE $171F (wjmp) left by the prior full-play frame.
    rphase_pulse_tail = str(
        usf.params.fields.get('rphase_variant', '')) == 'pulse_tail'
    r_call = 'jsr pulse_tail' if rphase_pulse_tail else 'jsr fx_glide'
    pulse_tail_asm = ('pulse_tail:                          ; R-phase $135D: 2nd\n'
                      '        lda pwphase,x                ; pulse advance/tick,\n'
                      '        and #$01                     ; step nibble from the\n'
                      '        beq pt_even                  ; STALE wjmp ($171F) —\n'
                      '        lda wjmp                     ; $135D skips the fresh\n'
                      '        and #$0f                     ; speed-byte reload\n'
                      '        asl\n'
                      '        asl\n'
                      '        asl\n'
                      '        asl\n'
                      '        jmp pt_base\n'
                      'pt_even:\n'
                      '        lda wjmp\n'
                      '        and #$f0\n'
                      'pt_base:\n'
                      '        clc\n'
                      '        adc cpwbase,x                ; + cached step base\n'
                      '        sta tmp\n'
                      '        sta pwstep,x\n'
                      '        jmp pw_sweep                 ; sweep+filter+glide+wave+write\n\n'
                      ) if rphase_pulse_tail else ''
    if (tokens and 'P' in tokens and len(tokens) > 1
            and all(t == 'P' or t == 'S'
                    or (t[0] in 'FR' and t[1:]
                        and set(t[1:]) <= set('123')) for t in tokens)):
        n_ph = len(tokens)
        # one routine per DISTINCT token; phasetab holds the routine index
        kinds = []
        for t in tokens:
            if t not in kinds:
                kinds.append(t)
        tab = ','.join(str(kinds.index(t)) for t in tokens)
        disp, routines = '', ''
        for k, t in enumerate(kinds):
            disp += (f'        cmp #{k}\n'
                     f'        beq pp_r{k}\n')
            if t == 'P':
                body = '        jmp playframe                ; P = full play\n'
            elif t == 'S':
                body = '        rts                          ; S = silent call\n'
            elif t[0] == 'R':         # R<voices>: register refresh — the
                body = ''             # per-voice glide/write tail ($141C) only;
                for v in t[1:]:       # re-emits current freq/PW/ctrl. With
                    body += (f'        ldx #{int(v) - 1}\n'   # rphase_variant=
                             f'        {r_call}\n')           # pulse_tail it runs
                body += '        rts\n'                        # the $135D pulse tail
            else:                     # F<voices>: per-voice frame entry only
                body = ''
                for v in t[1:]:
                    body += (f'        ldx #{int(v) - 1}\n'
                             '        jsr voice_fx\n')
                body += '        rts\n'
            routines += f'pp_r{k}:\n{body}'
        play_entry = 'playphases'
        play_wrapper = (
            'playphases:\n'
            '        ldy phasectr\n'
            '        iny\n'
            f'        cpy #{n_ph}\n'
            '        bne pp_set\n'
            '        ldy #$00\n'
            'pp_set:\n'
            '        sty phasectr\n'
            '        lda phasetab,y\n'
            + disp
            + '        rts                          ; (unreachable)\n'
            + routines
            + f'phasetab: .byt {tab}\n'
            f'phasectr: .byt {n_ph - 1}\n'
            'voice_fx:                            ; F phase entry\n'
            f'        jmp {voice_fx_target}\n\n'    # frame_entry ($11F9: note-init
            # or effects) for the immediate note-start; wavestep ($1591: emit +
            # advance wave, PAST note-init/gate/pulse) when notestart_arm, so
            # pending survives to the next P call = the 2-frame arm
            + pulse_tail_asm)               # R-phase pulse tail (gated, C18)
    elif play_repeat > 1:
        play_entry = 'playrepeat'
        play_wrapper = ('playrepeat:\n'
                        + '        jsr playframe\n' * play_repeat
                        + '        rts\n\n')
    else:
        play_entry = 'playframe'
        play_wrapper = ''
    # $D418 play-vector wrapper (PVCF / Zyron / Signor, 6 members): the
    # original's PSID play vector points at `LDA #imm / STA $D418 / JMP
    # base+3` — a constant master-vol|filter-mode assertion on EVERY play()
    # call, before the play body (factory-probed at the PSID play address).
    d418_every_play = usf.params.fields.get('master_vol_every_play', None)
    if d418_every_play is not None:
        play_wrapper = (
            'playd418:\n'
            f'        lda #${int(d418_every_play) & 0xFF:02X}\n'
            '        sta $d418                    ; play-vector wrapper\n'
            f'        jmp {play_entry}\n\n') + play_wrapper
        play_entry = 'playd418'
    # Song-global filter-cutoff LFO (usf.filter_mod): a free-running looped
    # contour with two phase-offset taps feeding a filter program's init and
    # stop cutoff cells every play() call; the engine samples them at filter
    # note-init. Two sweep walkers (value / run index / frames-left) share
    # the contour's (rate, frames) run tables — clean parametric replacement
    # for the original's SMC roving-pointer table stream (Ed/Core_of_Acid;
    # multi-prog since Elechromania — one chunk per modulated prog, labels
    # suffixed by slot; a single-tap driver has init_phase == stop_phase).
    for _fm_prog, _fm in sorted(usf.filter_mod.items()):
        _slot = m.filter_slots.get(_fm_prog)
        if _slot is None:
            continue
        _runs = [(d & 0xFF, f) for d, f in _fm['steps']]

        def _fm_seed(phase):
            val, rem = _fm['start'] & 0xFF, phase
            for i, (d, f) in enumerate(_runs):
                if rem < f:
                    return (val + d * rem) & 0xFF, i, f - rem
                val = (val + d * f) & 0xFF
                rem -= f
            return val, 0, _runs[0][1]

        _sa = [_fm_seed(_fm['init_phase']), _fm_seed(_fm['stop_phase'])]
        _s = f'{_slot}'
        play_wrapper = (
            f'playfmod{_s}:                            ; global cutoff LFO\n'
            f'        lda fmv{_s}+0\n'
            f'        sta fdinit+{_slot}\n'
            f'        lda fmv{_s}+1\n'
            f'        sta fdstop+{_slot}\n'
            '        ldx #$00\n'
            f'        jsr fmadv{_s}\n'
            '        ldx #$01\n'
            f'        jsr fmadv{_s}\n'
            f'        jmp {play_entry}\n'
            f'fmadv{_s}:  ldy fmi{_s},x\n'
            f'        lda fmv{_s},x\n'
            '        clc\n'
            f'        adc fmrate{_s},y\n'
            f'        sta fmv{_s},x\n'
            f'        dec fmc{_s},x\n'
            f'        bne fmadv_rts{_s}\n'
            '        iny\n'
            f'        cpy #{len(_runs)}\n'
            f'        bne fmadv_set{_s}\n'
            '        ldy #$00\n'
            f'fmadv_set{_s}:\n'
            '        tya\n'
            f'        sta fmi{_s},x\n'
            f'        lda fmlen{_s},y\n'
            f'        sta fmc{_s},x\n'
            f'fmadv_rts{_s}:\n'
            '        rts\n'
            f'fmv{_s}:    .byt {_sa[0][0]},{_sa[1][0]}\n'
            f'fmi{_s}:    .byt {_sa[0][1]},{_sa[1][1]}\n'
            f'fmc{_s}:    .byt {_sa[0][2]},{_sa[1][2]}\n'
            f'fmrate{_s}: ' + _byt([d for d, _ in _runs]) + '\n'
            f'fmlen{_s}:  ' + _byt([f & 0xFF for _, f in _runs]) + '\n\n'
            ) + play_wrapper
        play_entry = f'playfmod{_s}'
    # Appended filter-def ANIMATOR (Ed/Wrath_Designs Cliche_Beat driver,
    # factory-probed C19): the original's play vector JSRs a self-retargeting
    # routine before the play body — phase 1 ramps defs 0-2's resonance cell
    # (+step every p1 plays until def0 hits the cap), then phase 2 walks a
    # generated 256-byte triangle into def0/def1's init-cutoff cells every p2
    # plays (def0 index decrements, def1's advances by 2; def2 is never
    # animated — the original stores def1 twice, an author bug whose first
    # store is dead). fres/fcut pick the animated cells up at filter
    # note-inits. The triangle is generated from its two ramp seeds, and the
    # phase flag replaces the original's SMC JSR operand.
    fda = usf.params.fields.get('filterdef_anim', None)
    if fda is not None:
        _step, _capf0, _c1, _p1, _c2, _p2, _ts, _td = (
            int(x, 16) for x in str(fda).split(','))
        _tri = [(_ts + i) & 0xFF for i in range(0x80)] \
            + [(_td - i) & 0xFF for i in range(0x80)]
        play_wrapper = (
            'playfda:                             ; filter-def animator\n'
            '        lda fdaph\n'
            '        bne fda_p2\n'
            '        dec fdac1\n'
            '        bne fda_done\n'
            f'        lda #${_p1:02X}\n'
            '        sta fdac1\n'
            '        lda fdres+0\n'
            f'        cmp #${_capf0:02X}\n'
            '        bne fda_add\n'
            '        inc fdaph                    ; ramp capped -> phase 2\n'
            '        jmp fda_done\n'
            'fda_add:\n'
            '        clc\n'
            f'        adc #${_step:02X}\n'
            '        sta fdres+0\n'
            '        lda fdres+1\n'
            '        clc\n'
            f'        adc #${_step:02X}\n'
            '        sta fdres+1\n'
            '        lda fdres+2\n'
            '        clc\n'
            f'        adc #${_step:02X}\n'
            '        sta fdres+2\n'
            '        jmp fda_done\n'
            'fda_p2:\n'
            '        dec fdac2\n'
            '        bne fda_done\n'
            f'        lda #${_p2:02X}\n'
            '        sta fdac2\n'
            '        ldx fdax0\n'
            '        lda fdatri,x\n'
            '        sta fdinit+0\n'
            '        dec fdax0\n'
            '        ldx fdax1\n'
            '        lda fdatri,x\n'
            '        sta fdinit+1\n'
            '        inc fdax1\n'
            '        inc fdax1\n'
            'fda_done:\n'
            f'        jmp {play_entry}\n'
            'fdaph:  .byt 0\n'
            f'fdac1:  .byt {_c1}\n'
            f'fdac2:  .byt {_c2}\n'
            'fdax0:  .byt 0\n'
            'fdax1:  .byt 0\n'
            'fdatri: ' + _byt(_tri) + '\n\n'
            ) + play_wrapper
        play_entry = 'playfda'
    # Filter-tail POWER-ON-PATTERN cutoff animator (Ed/Go_Funk, factory-
    # probed C19): the original re-points the filter tail's STA $D417 at a
    # stub that (after the store) every `reset` plays pokes one filter
    # def's INIT-cutoff cell from an address past the image end — i.e. the
    # emulator environment's power-on RAM pattern (C29). The table page is
    # generated here from that pattern (an environment constant, same for
    # every tune — mechanism, not member data). The original pokes at the
    # END of play N; this chunk runs at the START of play N+1 (counter
    # seeded +1), which is observably identical — the cell is only read by
    # note-inits inside a play body. The stub's two instrument-record
    # pokes are NOT reproduced: on the only carrier those instruments are
    # never played (unobservable); a carrier that plays them would simply
    # verify partial.
    gfa = usf.params.fields.get('d417_tail_anim', None)
    if gfa is not None:
        (_seed, _reset, _x1, _tabhi, _dslot,
         _x2, _tabhi2, _wf1, _wf2) = (
            int(x, 16) for x in str(gfa).split(','))

        def _poweron_page(hi):
            # one page of libsidplayfp's power-on RAM pattern (see the
            # extract's _poweron_fill): 16K blocks alternate base $00/$FF,
            # offsets 2-5 of every 8 hold the flipped byte. An environment
            # constant — mechanism, not member data (ledger C29).
            b = 0xFF if (hi >> 6) & 1 else 0x00
            page = bytearray([b] * 0x100)
            for i in range(0x02, 0x100, 0x08):
                page[i:i + 4] = bytes([b ^ 0xFF] * 4)
            return list(page)

        # wavefreq pokes only when the pool is layout-preserving AND the
        # offset exists in the emitted pool (an uncovered position is never
        # read by any program — unobservable either way).
        _wfpokes = ''
        if m.wavepos_layout:
            _tg = [o for o in (_wf1, _wf2) if o < len(m.wfreq)]
            if _tg:
                _wfpokes = (
                    '        inc gfax2\n'
                    '        inc gfax2\n'
                    '        ldx gfax2\n'
                    '        lda gfatab2,x\n'
                    + ''.join(f'        sta wftab+{o}\n' for o in _tg))
        play_wrapper = (
            'playgfa:                             ; filter-tail cutoff animator\n'
            '        dec gfac\n'
            '        bne gfa_done\n'
            f'        lda #${_reset:02X}\n'
            '        sta gfac\n'
            '        inc gfax\n'
            '        ldx gfax\n'
            '        lda gfatab,x\n'
            f'        sta fdinit+{_dslot}\n'
            + _wfpokes +
            'gfa_done:\n'
            f'        jmp {play_entry}\n'
            f'gfac:   .byt {(_seed + 1) & 0xFF}\n'
            f'gfax:   .byt {_x1}\n'
            f'gfax2:  .byt {_x2}\n'
            'gfatab: ' + _byt(_poweron_page(_tabhi)) + '\n'
            'gfatab2:' + _byt(_poweron_page(_tabhi2)) + '\n\n'
            ) + play_wrapper
        play_entry = 'playgfa'
    # Third Ed filter-def driver (Only_Ones, factory-probed C19): phase A
    # (every p1 plays) ramps def s2's init/stop toward cap2 while its res
    # nibble follows a 1..rescap counter, then walks def s1's init/stop
    # down to dncap, then flips to phase B (every play): def s2 init/stop =
    # tri[X1]/2 + add2, def s1 = tri[X2]/2 + add1; X1 += 1 per p8 plays,
    # X2 += 1 per p8*p2. The triangle is generated from its two seeds; a
    # phase flag replaces the original's SMC JSR retarget.
    ooa = usf.params.fields.get('filterdef_anim3', None)
    if ooa is not None:
        (_p1, _cap2, _rescap, _dncap, _x1, _x2, _p8, _p2,
         _add2, _add1, _step, _d0, _s2, _s1) = (
            int(x, 16) for x in str(ooa).split(','))
        _tri = [(_i + _step) & 0xFF for _i in range(0x80)] \
            + [(_d0 - _i) & 0xFF for _i in range(0x80)]
        play_wrapper = (
            'playooa:                             ; filter-def driver (2-phase)\n'
            '        lda ooaph\n'
            '        bne ooa_pb\n'
            '        dec ooac1\n'
            '        bne ooa_done\n'
            f'        lda #${_p1:02X}\n'
            '        sta ooac1\n'
            f'        lda fdinit+{_s2}\n'
            f'        cmp #${_cap2:02X}\n'
            '        beq ooa_res\n'
            f'        inc fdinit+{_s2}\n'
            f'        inc fdstop+{_s2}\n'
            'ooa_res:\n'
            '        lda ooacnt\n'
            '        asl\n        asl\n        asl\n        asl\n'
            f'        sta fdres+{_s2}\n'
            '        lda ooacnt\n'
            f'        cmp #${_rescap:02X}\n'
            '        beq ooa_dn\n'
            '        inc ooacnt\n'
            '        jmp ooa_done\n'
            'ooa_dn:\n'
            f'        lda fdinit+{_s1}\n'
            f'        cmp #${_dncap:02X}\n'
            '        beq ooa_sw\n'
            f'        dec fdinit+{_s1}\n'
            f'        dec fdstop+{_s1}\n'
            '        jmp ooa_done\n'
            'ooa_sw:\n'
            '        inc ooaph                    ; -> phase B\n'
            '        jmp ooa_done\n'
            'ooa_pb:\n'
            '        ldx ooax1\n'
            '        lda ooatab,x\n'
            '        lsr\n'
            '        clc\n'
            f'        adc #${_add2:02X}\n'
            f'        sta fdinit+{_s2}\n'
            f'        sta fdstop+{_s2}\n'
            '        ldx ooax2\n'
            '        lda ooatab,x\n'
            '        lsr\n'
            '        clc\n'
            f'        adc #${_add1:02X}\n'
            f'        sta fdinit+{_s1}\n'
            f'        sta fdstop+{_s1}\n'
            '        dec ooac8\n'
            '        bne ooa_done\n'
            f'        lda #${_p8:02X}\n'
            '        sta ooac8\n'
            '        inc ooax1\n'
            '        dec ooac2\n'
            '        bne ooa_done\n'
            f'        lda #${_p2:02X}\n'
            '        sta ooac2\n'
            '        inc ooax2\n'
            'ooa_done:\n'
            f'        jmp {play_entry}\n'
            'ooaph:  .byt 0\n'
            f'ooac1:  .byt {_p1}\n'
            f'ooacnt: .byt {(_x2 + 1) & 0xFF}\n'
            f'ooax1:  .byt {_x1}\n'
            f'ooax2:  .byt {_x2}\n'
            f'ooac8:  .byt {_p8}\n'
            f'ooac2:  .byt {_p2}\n'
            'ooatab: ' + _byt(_tri) + '\n\n'
            ) + play_wrapper
        play_entry = 'playooa'
    # Play-body unit repeat (default '1,1,1,1'): the play body executes four
    # units per frame — voice 0, voice 1, voice 2, then the global filter tail
    # ($D416/$D417) — and this 4-int list gives how many times each unit runs.
    # A value > 1 is the DMC editor hack where a play-body JSR is redirected to
    # a stub that calls a unit N times: a "double-speed voice" (that voice's
    # wave/pulse program advances N steps/frame and its full block is emitted N
    # times), or — via a stub that JMPs back into the filter tail rather than
    # RTS'ing — the filter tail re-runs ($D416/$D417 emitted twice). Factory-
    # detected; the '1,1,1,1' default emits the canonical single-pass body
    # byte-identically. (Distinct from play_repeat, which repeats the WHOLE
    # play() — all four units together.)
    # A 0 count SKIPS that voice's unit entirely (the two-voice player build:
    # Two_Channels inserts INX before the first JSR, so voice 0 never runs —
    # no writes, no state, ever). The `inx` chain below still steps X, so the
    # remaining voices keep their indices. The filter tail is clamped to >=1.
    pur_s = str(usf.params.fields.get('play_unit_repeat', '') or '1,1,1,1')
    try:
        play_unit_repeat = [max(0, int(x)) for x in pur_s.split(',')]
    except ValueError:
        play_unit_repeat = [1, 1, 1, 1]
    play_unit_repeat = (play_unit_repeat + [1, 1, 1, 1])[:4]
    play_unit_repeat[3] = max(1, play_unit_repeat[3])
    # fclaim_clear_dead wedge (C19, Jezuseczek): the orig's per-play fclaim
    # clear is re-pointed at a void — the claim persists forever after the
    # first filter voice sets it, freezing the filter program (cutoff then
    # moves only on $F1 filterset commands). Reproduce by dropping OUR
    # per-play clear; fclaim starts 0 (fresh var) exactly like the orig's
    # init-cleared state.
    _vc = ['        ldx #$00'] + (
        [] if usf.params.fields.get('fclaim_clear_dead')
        else ['        stx fclaim'])
    for _vi in range(3):
        if _vi:
            _vc.append('        inx')
        _vc += ['        jsr voice'] * play_unit_repeat[_vi]
    voice_calls = '\n'.join(_vc) + '\n'
    filter_tail = ('        lda fcut\n        sta $d416\n'
                   '        lda shadow17\n        ora fres\n'
                   '        sta $d417\n') * play_unit_repeat[3]
    # $D418 re-assert-every-frame wedge (Groove class; factory
    # _d418_filter_tail_probe -> ledger C19 detection / C10
    # master-vol-every-frame form). The member re-writes $D418 = filter-mode |
    # master-vol at the END of the filter tail on EVERY frame (never at filter
    # note-init, which its wedge neuters). The composer tracks the active
    # filter's mode in `d418mode` (set at note-init instead of writing $D418)
    # and re-asserts it here. Default None -> canonical (note-init writes
    # $D418), byte-identical.
    d418_filter_tail = usf.params.fields.get('master_vol_reassert_filter_tail', None)
    if d418_filter_tail is not None:
        d418_init_mode = int(d418_filter_tail) & 0xFF
        ni_d418 = ('        sta d418mode                 ; mode tracked; '
                   '$D418 re-asserted per-frame in filter tail\n')
        d418_prime = (f'        lda #${d418_init_mode:02X}\n'
                      '        sta d418mode\n')
        d418_var = 'd418mode: .dsb 1, 0\n'
        filter_tail = filter_tail + ('        lda d418mode\n'
                                     '        ora mvol\n'
                                     '        sta $d418\n')
    else:
        ni_d418 = ('        ora mvol\n'
                   '        sta $d418                    ; filter note-init- '
                   'mode | volume\n')
        d418_prime = ''
        d418_var = ''
    idle = [0, 0, 0]
    imask = [0, 0, 0]
    iguard = [0, 0, 0]
    idurl = [0, 0, 0]
    # sticky-instrument seed SLOTS (curinst,x priming): the engine's $1015,x
    # work-file leftover, carried as `init { voice N { instr: iK } }` — the
    # resolver seed a leading inherited note resolves to. Slot 0 (i1) is the
    # cleared/dead-seed common case and keeps the historical `lda #$00` init
    # form (byte identity); any nonzero slot switches to an icinst table.
    icinst = [0, 0, 0]
    for v in usf.init.voices:
        if v.note is not None:
            idle[v.id - 1] = v.note
        if v.gate_mask is not None:
            imask[v.id - 1] = v.gate_mask
        if v.guard is not None:
            iguard[v.id - 1] = v.guard
        if getattr(v, 'dur_reload', None) is not None:
            idurl[v.id - 1] = v.dur_reload
        if getattr(v, 'instr', None) is not None:
            icinst[v.id - 1] = m.inst_slot[v.instr.id]
    # PER-SUBTUNE idle priming (trichotomy §4.5 voice_state). The file-level
    # block above serves the ordinary case — one engine, one set of uncleared
    # work-file leftovers for the whole file. A COMPILATION packs several
    # players and each subtune runs exactly one of them, so its idle priming is
    # a per-subtune fact carried on `subtune { init { voice N { ... } } }`.
    # WIDENING IS GATED: unless some subtune actually states priming that
    # differs from the file-level block, the tables stay 3 bytes and the init
    # keeps its `lda inote,x` form — so every existing member's image is
    # byte-identical.
    sub_prime = []
    for sub in usf.subtunes:
        row = [list(idle), list(imask), list(iguard), list(idurl),
               list(icinst)]
        for v in ((sub.init.voices if sub.init else []) or []):
            if not 1 <= v.id <= 3:
                continue
            for k, val in ((0, v.note), (1, v.gate_mask), (2, v.guard),
                           (3, getattr(v, 'dur_reload', None))):
                if val is not None:
                    row[k][v.id - 1] = val
            if getattr(v, 'instr', None) is not None:
                row[4][v.id - 1] = m.inst_slot[v.instr.id]
        sub_prime.append(row)
    per_sub_prime = any(r != [idle, imask, iguard, idurl, icinst]
                        for r in sub_prime)
    if per_sub_prime:
        idle = [b for r in sub_prime for b in r[0]]
        imask = [b for r in sub_prime for b in r[1]]
        iguard = [b for r in sub_prime for b in r[2]]
        idurl = [b for r in sub_prime for b in r[3]]
        icinst = [b for r in sub_prime for b in r[4]]
    if usf.freq_table:
        assert len(usf.freq_table) == 192, len(usf.freq_table)
        flo, fhi = usf.freq_table[:96], usf.freq_table[96:]
    else:
        flo, fhi = FREQ_LO, FREQ_HI
    # off-table freq window (the v5 `offtable_freq` form): place the explicit
    # (lo, hi) each off-table read produces at its window position, so reads on
    # the track-ptr region (k<=5) / live state (k>=17) resolve to the original's
    # value instead of being rejected. freqlo/freqhi/window are contiguous, so a
    # read at idx hits window pos idx-96 (the HI read) and, for idx>=192, pos
    # idx-192 (the LO read lands deeper via table double-adjacency). Positions
    # 6..16 stay co-located (live spd/mvol + the sidoff/fbit/fmask constants) —
    # so members that only read there are byte-identical to before.
    # Positions 6..16 are CO-LOCATED live/constant structures (sidoff/fbit/
    # fmask + spd/mvol) for canon-geometry members — the orig's bytes there ARE
    # those live values, so records at those positions defer to the co-location.
    # For a non-canon member (offtable_redirect=0) the orig's window bytes are
    # unrelated static code/data: place every record verbatim and emit the live
    # structures OUTSIDE the window (see the ovrwin emission below).
    def _ovr_positions(inst):
        """(window position, value) each of `inst`'s off-table records fills.

        A NAMED-SIGNAL slot (phase 3) fills nothing: the read is served
        live by the redirect, and the slot no longer carries a captured
        byte (the sparse-glide seeds moved to init.voice_state)."""
        for rec in getattr(inst, 'offtable_freq', []) or []:
            off, note, lo, hi = rec[:4]     # rec may carry a 5th `live` flag
            idx = (off + note) & 0xFF
            if idx < 96:
                continue
            ph = idx - 96
            if isinstance(hi, int) and \
                    not (m.offtable_redirect and 6 <= ph <= 16):
                yield ph, hi
            if idx >= 192:
                pl = idx - 192
                if isinstance(lo, int) and \
                        not (m.offtable_redirect and 6 <= pl <= 16):
                    yield pl, lo

    ovr = [0] * 160
    for inst in insts:
        for pos, val in _ovr_positions(inst):
            ovr[pos] = val

    # PER-SUBTUNE off-table window (ledger C31 — a per-player fact the merge
    # collapses). The window is file-level and idx-keyed, but a COMPILATION's
    # packed players each overrun into their OWN state block, so two players'
    # records can name the SAME window position with different bytes and the
    # loop above silently keeps the last (Para_Lander_DX idx 96 = the running
    # player's V1 track-ptr lo: $C8 for the player subtune 0 selects, $D2 for
    # the one subtune 1 selects — one static window cannot serve both).
    # Attribute each record to the subtunes whose rows play its instrument;
    # where they disagree, init writes those positions for the subtune it was
    # called with. Every position is written on EVERY init (not just the
    # differing ones) so a subtune change can't inherit the previous one's.
    # GATED on an actual disagreement: with none, nothing below is emitted and
    # the member's image is byte-identical.
    ovr_sub = []
    for sub in usf.subtunes:
        used = set()
        for v in sub.voices:
            pat_by_id = {p.id: p for p in v.patterns}
            ol = v.orderlist
            for pid in (list(getattr(ol, 'intro_entries', None) or [])
                        + list(ol.entries or [])):
                for r in (pat_by_id[pid].rows if pid in pat_by_id else ()):
                    ins_ref = getattr(r, 'instr', None)
                    if ins_ref is not None:
                        used.add(getattr(ins_ref, 'id', ins_ref))
        d = {}
        for inst in insts:
            if inst.id in used:
                for pos, val in _ovr_positions(inst):
                    d[pos] = val
        ovr_sub.append(d)
    ovr_conflict = sorted({p for d in ovr_sub for p in d
                           if any(p in e and e[p] != d[p] for e in ovr_sub)})
    # Y walks the patch stream, so it must stay 8-bit; an over-long stream
    # keeps the static window (the pre-change behaviour) rather than truncating.
    if ovr_conflict and len(usf.subtunes) * (2 * len(ovr_conflict) + 1) > 256:
        ovr_conflict = []
    ovr_stream, ovr_rowbase = [], []
    for d in ovr_sub:
        ovr_rowbase.append(len(ovr_stream))
        for pos in ovr_conflict:
            ovr_stream += [pos, d.get(pos, ovr[pos])]
        ovr_stream.append(0xFF)         # end of this subtune's patch row

    # Seed the SPARSE glide vars gla/glb from their captured off-table values so
    # they track the orig from init (see DMC_OFFTABLE_STATE). A state var at
    # canonical addr A lands at window position A-ORIG_FLO-192 (LO and HI reads
    # coincide since ORIG_FHI=ORIG_FLO+96): gla[x]->pos 61+x, glb[x]->pos 64+x.
    # A DYNAMIC glide reader (Hardcore) overwrites the seed on its glide arm
    # before the read; a STATIC-leftover reader (98_Mix) now reads the leftover.
    # glsp is deliberately NOT seeded — a non-zero glsp would spuriously trigger
    # fx_glide (gated `lda glsp,x / beq`) at frame 0. Empty capture -> all-zero
    # seed == the old zero-init, so members that don't read here are unchanged.
    _glap = 0x1744 - ORIG_FLO - 192
    _glbp = 0x1747 - ORIG_FLO - 192
    # Seed source priority (phase 3a): the typed init.voice_state fields
    # (glide_note/glide_target — the seeds' §4.5 home) when present, else
    # the legacy window-fill bytes (old-form records still carry them).
    _ivs = {v.id: v for v in ((usf.init.voices if usf.init else None) or [])}

    def _gseed(x, attr, pos):
        v = _ivs.get(x + 1)
        val = getattr(v, attr, None) if v is not None else None
        return ovr[pos + x] if val is None else val
    igla = [_gseed(x, 'glide_note', _glap) for x in range(3)]
    iglb = [_gseed(x, 'glide_target', _glbp) for x in range(3)]

    data = []
    data.append('inote:\n' + _byt(idle))
    data.append('imask:\n' + _byt(imask))
    data.append('iguard:\n' + _byt(iguard))
    data.append('idurl:\n' + _byt(idurl))
    if any(icinst):
        # sticky-instrument seed slots — emitted only when some seed is
        # nonzero (the all-zero case keeps the constant init form, so every
        # existing member's image is byte-identical)
        data.append('icinst:\n' + _byt(icinst))
    data.append('igla:\n' + _byt(igla))
    data.append('iglb:\n' + _byt(iglb))
    data.append('freqlo:\n' + _byt(flo))
    data.append('freqhi:\n' + _byt(fhi))
    # off-table overrun window: the original reads past its freq tables
    # into the engine state block; reads the extract certifies as
    # reachable land on the stable prefix, mirrored here byte-for-byte
    # (the original's $1707+ adjacency: 6 track-ptr slots, the three
    # voice constant triplets, then speed + master volume — the last
    # two are the LIVE variables, placed here so the values track).
    if m.offtable_redirect:
        data.append('ovrwin:\n' + _byt(ovr[0:6]) + '\n'
                    'sidoff:   .byt $00, $07, $0E\n'
                    'fbit:     .byt $01, $02, $04\n'
                    'fmask:    .byt $FE, $FD, $FB\n'
                    'spd:      .dsb 1, 0\n'
                    'mvol:     .dsb 1, 0\n'
                    + _byt(ovr[17:160]))
    else:
        # non-canon geometry: the window is pure static capture; the live
        # structures live outside it (their canon co-location would shadow
        # the member's static bytes at pos 6..16 — Viiskyt lo idx 208 read
        # LIVE mvol $0F where the orig reads a static $07 code byte).
        data.append('ovrwin:\n' + _byt(ovr) + '\n'
                    'sidoff:   .byt $00, $07, $0E\n'
                    'fbit:     .byt $01, $02, $04\n'
                    'fmask:    .byt $FE, $FD, $FB\n'
                    'spd:      .dsb 1, 0\n'
                    'mvol:     .dsb 1, 0')
    if ovr_conflict:
        data.append('ovrbase:\n' + _byt(ovr_rowbase))
        data.append('ovrpat:\n' + _byt(ovr_stream))
    # vibdepth table (96-entry constant) + the off-table overrun window: a
    # note>95 reads `vibdepth[note]` past the table; place the captured depth at
    # pos note-96 so the read resolves to the original's value (it landed on
    # static instr-record bytes). Empty -> just the constant (byte-identical).
    _vibovr = getattr(usf, 'offtable_vibdepth', None) or []
    _vd = list(VIBDEPTH)
    if _vibovr:
        # head overrides (note < 96): the code-overlap head bytes 3,4 hold the
        # engine's state-store operand, which relocates for page-3 builds -> the
        # canonical VIBDEPTH head is wrong there. Override in place (empty for
        # canonical members -> byte-identical).
        for _note, _depth in _vibovr:
            if _note < 96:
                _vd[_note] = _depth
        _tail = [n for n, _ in _vibovr if n >= 96]
        if _tail:
            _top = max(_tail)
            _win = [0] * (_top - 95)
            for _note, _depth in _vibovr:
                if _note >= 96:
                    _win[_note - 96] = _depth
            _vd = _vd + _win
    data.append('vibdepth:\n' + _byt(_vd))
    for name, arr in [('iad', iad), ('isr', isr), ('ipwinit', ipwinit),
                      ('ipwmin', ipwmin), ('ipwmax', ipwmax), ('ioffval', ioffval),
                      ('ipwbase', ipwbase),
                      ('ifdef', ifdef), ('ivdel', ivdel), ('ivwid', ivwid),
                      ('ivram', ivram), ('iflag', iflag), ('iwst', iwst)]:
        data.append(f'{name}:\n' + _byt(arr))
    data.append('isteps:\n' + _byt(isteps))
    data.append('irawsp:\n' + _byt(irawsp))
    if wide_pulse:
        data.append('istepbase:\n' + _byt(istepbase))
    if _any_chase:
        data.append('iwchase:\n' + _byt(iwchase))
    if pw_hi_const:
        data.append('pwhic:\n' + _byt(
            [int(t) & 0xFF for t in pw_hi_const.split(',')]))
    for name, arr in [('fdres', fdres), ('fdmode', fdmode),
                      ('fdinit', fdinit), ('fdrep', fdrep),
                      ('fdstop', fdstop)]:
        data.append(f'{name}:\n' + _byt(arr or [0]))
    data.append('fdrec:\n' + _byt(fdrec or [0] * 16))
    data.append('fdstep = fdrec+4\nfddur = fdrec+10')
    data.append('wctab:\n' + _byt(m.wctrl))
    if per_sub_sphase:
        data.append('sphase:\n' + _byt(sphase_vals))
    data.append('wftab:\n' + _byt(m.wfreq))
    data.append('tunetab:\n' + '\n'.join(tune_lines))
    data.append('patlo:\n' + pat_lo)
    data.append('pathi:\n' + pat_hi)
    for lbl, (blob, loop_off) in track_blobs:
        s = f'{lbl}:' + (('\n' + _byt(blob)) if blob else '')
        if loop_off is not None:              # loop_off is a BYTE offset now
            s += f'\n        .byt $FF, <({lbl}+{loop_off}), >({lbl}+{loop_off})'
        data.append(s)
    for i, blob in enumerate(m.patterns):
        data.append(f'pat_{i}:\n' + _byt(blob))
    data_asm = '\n'.join(data)

    # note-init cymbal (canon onset 0) vs frame-2 cymbal (family-2 onset 1).
    # `cymburst:` is a ROLE label: a multi-SID keep_regs entry can name this
    # block to leave one of its stores on chip 1 (C19 per-store granularity —
    # Surgeon/Nice_Dream's chip-2 player relocates the burst's freq-lo but
    # not its freq-hi). Both call sites end at a label, so the scope is
    # exactly the burst.
    _cym_burst = (
        'cymburst:\n'
        '        ldy sidoff,x\n'
        f'        lda #${cymbal_burst:02X}\n'
        '        sta $d400,y\n'
        '        sta $d401,y\n'
        '        lda #$81\n'
        '        sta $d404,y                  ; gated noise burst\n')
    if cymbal_onset == 0:
        cym_ni = ('        lda fxf,x\n'
                  '        and #$80                     ; cymbal?\n'
                  '        beq ni_wave\n'
                  + _cym_burst + '        rts\n')
        cym_rf = ''
    else:
        cym_ni = ''                  # frame 1 = normal note
        cym_rf = ('        cmp #$02                     ; frame-2 cymbal?\n'
                  '        bne rf_nocym\n'
                  '        lda fxf,x\n'
                  '        and #$80\n'
                  '        beq rf_nocym\n'
                  + _cym_burst +
                  '        dec guard,x\n'
                  '        rts\n'
                  'rf_nocym:\n')

    # vibrato note-init step setup + half-cycle swell (canon vs family 2)
    if vib_ramp == 'step':
        # family 2: vstep/vsteph already 0 (note-init clear); the per-note
        # increment = freq_hi(note) >> 1 (the original's $16A7>>1 -> $178C).
        ni_vib_depth = (
            '        ldy curnote,x\n'
            '        lda freqhi,y                 ; family-2 vib increment\n'
            '        lsr                          ; = freq_hi(note) >> 1\n'
            '        sta vdep,x\n')
        vib_swell = (
            '        lda vstep,x                  ; swell: step += increment\n'
            '        clc\n'
            '        adc vdep,x\n'
            '        sta vstep,x\n'
            '        lda vsteph,x\n'
            '        adc #$00\n'
            '        sta vsteph,x')
    else:
        ni_vib_depth = (
            '        ldy curnote,x\n'
            '        lda vibdepth,y               ; per-note vibrato depth\n'
            '        sta vstep,x\n'
            '        lda vibwid,x\n'
            '        bne ni_vs\n'
            '        lda #$00\n'
            '        sta vstep,x                  ; width 0 -> no modulation\n'
            'ni_vs:\n')
        vib_swell = (
            '        lda vibwid,x                 ; swell: width doubles\n'
            '        asl\n'
            '        sta vibwid,x')

    # wjmp chase shadow (wave_start_on_marker): re-assert the shared $171F
    # scratch = the chase distance n at note-init, the one hop the settled-pool
    # packing skips (subsequent frames hop naturally). Empty (byte-identical)
    # unless some instrument chases; Y = cinst here.
    ni_chase = ('        lda iwchase,y\n'
                '        beq ni_nochase\n'
                '        sta wjmp                     ; chase hop: $171F = n\n'
                'ni_nochase:\n') if _any_chase else ''

    # Off-table read-redirect (per-engine map -> shared generator). lo reads
    # hit state for idx 192-255; hi reads for idx 96-255. The whole map is
    # void for non-canon state-geometry members (params offtable_redirect=0,
    # extract-probed): their window bytes are static code/data served by the
    # static capture.
    otmap = (DMC_OFFTABLE_STATE if m.offtable_redirect else []) \
        + ([DMC_SECTPOS_ROW] if sectpos_on else []) \
        + ([DMC_WAVEPOS_ROW] if (m.wavepos_layout or
                                 m.wavepos_positional) else [])
    ws_lo_redirect = _gen_offtable_redirect(
        otmap, ORIG_FLO, 192, 'lda freqlo,y', 'ws_rd_los')
    ws_hi_redirect = _gen_offtable_redirect(
        otmap, ORIG_FHI, 96, 'lda freqhi,y', 'ws_rd_his')
    # Base-freq RELOAD (note-fetch ev_note + glide-arrival fx_gl_chk) reads
    # freqlo/hi[Y] with Y a note index that can ALSO overshoot the 96-entry
    # table (a negative transpose wraps a low note to e.g. $F4 via the 8-bit
    # note-init ADC). The orig reads the live state block there exactly as the
    # wave step does — curnote $F4 -> $173B = V1's LIVE duration counter,
    # sonified as this voice's base freq (Secret_Loser V3). Route those reads
    # through the SAME redirect so a wrapped/off-table base read tracks the live
    # var instead of a stale static window byte; in-table + unmapped indices
    # fall through to the identical `lda freqlo,y`, so canonical members are
    # byte-identical. Shared by both sites via the reload_base subroutine.
    nf_lo_redirect = _gen_offtable_redirect(
        otmap, ORIG_FLO, 192, 'lda freqlo,y', 'nf_rd_los')
    nf_hi_redirect = _gen_offtable_redirect(
        otmap, ORIG_FHI, 96, 'lda freqhi,y', 'nf_rd_his')
    # Glide-ARRIVAL compare (round 97, Cleve_24): the orig's fx_gl_chk
    # `CMP freqhi,y` with an off-table glb reads the live state block
    # (canon glb=126 -> $1725 = dtmph, which the dual-slide keeps equal to
    # the current slid freq hi -> instant arrival). Serve the compare
    # through the SAME redirect map as the reload; gated on the member
    # actually carrying an off-table glide target so everyone else is
    # byte-identical (the plain `cmp freqhi,y`).
    if m.glide_offtable:
        ga_chunk = _gen_offtable_redirect(
            otmap, ORIG_FHI, 96, 'lda freqhi,y', 'ga_rd_his')
        ga_cmp = ('        jsr ga_cmp_sub               ; arrived when freq '
                  'HI matches (live-served) target\n')
        ga_cmp_sub = (f'ga_cmp_sub:\n'
                      f'        sta tmp2                     ; current freq hi\n'
                      f'{ga_chunk}\n'
                      f'ga_rd_his:\n'
                      f'        cmp tmp2                     ; Z survives rts\n'
                      f'        rts\n')
    else:
        ga_cmp = ('        cmp freqhi,y                 ; arrived when freq '
                  'HI matches target\n')
        ga_cmp_sub = ''

    # per-subtune idle-priming addressing (see `per_sub_prime` above). When the
    # tables are 3 bytes wide the voice index IS the table index and all three
    # inserts are empty, so the emitted init is byte-for-byte what it was.
    ps = 'y' if per_sub_prime else 'x'
    prime_save = ('        pha                          ; keep subtune for the '
                  'per-subtune priming\n' if per_sub_prime else '')
    prime_setup = ('        pla                          ; subtune -> idle-priming'
                   ' row (subtune * 3)\n'
                   '        sta tmp\n'
                   '        asl\n'
                   '        clc\n'
                   '        adc tmp\n'
                   '        tay\n' if per_sub_prime else '')
    prime_step = '        iny\n' if per_sub_prime else ''
    # sticky-instrument seed init (see `icinst` above): all-zero slots keep
    # the historical constant form byte-for-byte; a nonzero seed switches to
    # the icinst table (emitted below only in that case).
    if any(icinst):
        cinst_seed = (f'        lda icinst,{ps}               ; sticky-'
                      'emission seeds (C32): a leading\n'
                      '        sta curinst,x                ; inherited slot '
                      'resolves to the engine\n'
                      '        lda #$00                     ; sticky ($1015,x '
                      'leftover) / vol 0 -\n'
                      '        sta volovr,x                 ; matches the '
                      "resolver's StickyState seed\n")
    else:
        cinst_seed = (
            '        lda #$00                     ; sticky-emission seeds '
            '(D6 piece 3): a\n'
            '        sta curinst,x                ; leading inherited slot '
            'resolves to the\n'
            '        sta volovr,x                 ; engine sticky (i1 = slot '
            '0) / vol 0 -\n'
            '                                     ; matches the resolver\'s '
            'StickyState seed\n')
    # per-subtune off-table window patch (see `ovr_conflict` above). Runs on
    # entry, before the state clear, so `tmp` is free to hold the subtune.
    ovr_patch = ('''        sta tmp                      ; per-subtune off-table window
        tax
        ldy ovrbase,x
ovrp_l:
        ldx ovrpat,y                 ; window position ($FF = row end)
        cpx #$FF
        beq ovrp_d
        iny
        lda ovrpat,y
        sta ovrwin,x
        iny
        bne ovrp_l
ovrp_d:
        lda tmp
''' if ovr_conflict else '')

    # route_clear_dead (C19 wedge, 16th occ — Classic_Mix): the note-init's
    # NON-filter route-bit CLEAR (`STA shadow` at canon $12C6) is re-pointed
    # at a void byte, so the $D417 routing bits only ever ACCUMULATE — the
    # work-file leftover (init.sid res_routing) persists through non-filter
    # note-inits. The SET site is untouched. Emit no clear for such members;
    # everyone else keeps the canonical clear, byte-identical.
    # track_ff_reinit (C19 wedge, Greenhorn/Second): the orig's $FF track-loop
    # handler is re-pointed at the INIT routine — the FIRST track end restarts
    # the whole song from scratch, landing the init's $D418 + ascending SID
    # clear mid-stream, then playing from the top with init state. Reproduce
    # with the same mechanism: the $FF fetch TAIL-CALLS our init (its RTS pops
    # the voice call, so the play body's remaining units + filter tail run
    # with fresh state — exactly the orig's `JMP <init>` flow). `cursong`
    # keeps the subtune for the restart; it lives OUTSIDE state0..state_end
    # so the init's state clear cannot wipe it. Default: the canonical 16-bit
    # loop redirect, byte-identical.
    # track_ff_reinit_ghost (C19 wedge SHAPE B, Hallen/For_Party_V_95): the same
    # $FF-re-points-at-init restart, but the wrap voice is NOT the last unit, so
    # after init's RTS pops the wrap voice's call the play body's `inx : jsr
    # voice` chain runs the REMAINING voices as GHOST UNITS with X past the
    # 3-voice range ($19/$1A). On the ORIG memory map those aliased reads/writes
    # emit a member-constant SID burst on V1's registers AND poke the surviving
    # (idle) voice's state so it plays a real part in the restart instead of
    # idling like a cold start. We do NOT reproduce the aliasing (a different
    # memory map ⇒ different ghost writes — CORE TENET: reproduce the write
    # stream, not the mechanism): the $FF handler runs init, emits the captured
    # ghost burst verbatim, pokes the surviving voice's state to the captured
    # values, then DISCARDS the wrap voice's return and jmps the filter tail —
    # skipping our own (wrong) ghost voices. The burst + pokes are extract-
    # captured by a py65 ghost simulation (`_simulate_reinit_ghosts`); the wrap
    # falls once inside the verify window so one capture suffices.
    ghost_spec = usf.params.fields.get('track_ff_reinit_ghost')
    need_ptail = False
    reinit_ghost_routine = ''
    if ghost_spec:
        _burst_s, _pokes_s = (str(ghost_spec).split('|') + [''])[:2]
        gl = ['reinit_ghost:',
              '        jsr init                     ; re-prime + SID burst; '
              'returns here (X=$18)']
        for _w in _burst_s.split(';'):
            if not _w:
                continue
            _r, _v = _w.split('=')
            gl.append(f'        lda #${_v}')
            gl.append(f'        sta $d4{_r.lower()}              '
                      '; ghost unit V1-reg burst')
        for _pk in _pokes_s.split(';'):
            if not _pk:
                continue
            _lab, _vc, _val = _pk.split(',')
            gl.append(f'        lda #${_val}')
            gl.append(f'        sta {_lab}+{_vc}'.ljust(37)
                      + '; ghost state poke')
        gl += ['        pla',
               '        pla                          ; drop the wrap voice '
               'call return',
               '        jmp ptail                    ; skip our ghost voices '
               '-> filter tail']
        # emitted OUT OF LINE (a $FF handler inlining ~50 instructions blows a
        # nearby branch's ±128 range); trk_ff just tail-jumps into it.
        reinit_ghost_routine = '\n'.join(gl) + '\n'
        trk_ff = ('        lda cursong                  ; $FF SHAPE-B ghost '
                  'restart\n'
                  '        jmp reinit_ghost\n')
        cursong_save = ('        sta cursong                  ; subtune for '
                        'the $FF restart\n')
        cursong_var = 'cursong:  .dsb 1, 0\n'
        need_ptail = True
    elif usf.params.fields.get('track_ff_reinit'):
        trk_ff = ('        lda cursong                  ; $FF = restart the '
                  'song via init\n'
                  '        jmp init                     ; (track_ff_reinit '
                  'wedge - init RTS pops the voice call)\n')
        cursong_save = ('        sta cursong                  ; subtune for '
                        'the $FF restart\n')
        cursong_var = 'cursong:  .dsb 1, 0\n'
    else:
        trk_ff = ('        iny\n'
                  '        lda ($f8),y                  ; $FF loop: 16-bit '
                  'BYTE address of the entry\n'
                  '        sta trkpl,x\n'
                  '        iny\n'
                  '        lda ($f8),y\n'
                  '        sta trkph,x\n'
                  '        jmp f_newpat\n')
        cursong_save = ''
        cursong_var = ''
    route_clear = ('' if str(usf.params.fields.get('route_clear_dead', '')
                             or '') else
                   '        lda shadow17\n'
                   '        and fmask,x\n'
                   '        sta shadow17\n')
    # ptail: label marks the filter tail so the shape-B ghost handler can skip
    # our own (wrong) ghost voice calls and complete the frame. Label-only —
    # byte-neutral — and emitted ONLY for the ghost member so no other build
    # carries an unused label.
    ptail_label = 'ptail:\n' if need_ptail else ''

    asm = f"""
SLIDE_PHASE = ${slide_phase:02X}
CIA_PERIOD = ${cia_period:04X}
        * = ${origin:04X}
        jmp init
        jmp {play_entry}

;; ===================== init (A = subtune) =====================
init:
{cursong_save}{ovr_patch}        pha                          ; save subtune
        lda #$00
        tax
ini_st:
        sta state0,x
        inx
        cpx #(state_end - state0)
        bne ini_st
        pla
{prime_save}{sphase_load}        asl
        asl
        asl
        asl                          ; subtune * 16
        tay
        ldx #$00
ini_ptr:
        lda tunetab,y
        sta trkpl,x
        lda tunetab+1,y
        sta trkph,x
        iny
        iny
        inx
        cpx #$03
        bne ini_ptr
        lda tunetab,y                ; +6 = speed
        sta spd
        lda tunetab+1,y              ; +7 = master vol
        sta mvol
        sta $d418                    ; priming (matches the family init)
        lda tunetab+2,y              ; +8 = $D417 routing-shadow priming
        sta shadow17
{rest_load}{d418_prime}{sphase_const}{prime_setup}        ldx #$00
ini_v:
        lda #$01
        sta vactive,x
        sta dur,x                    ; expires on the first tick
        lda inote,{ps}                  ; idle note-state priming
        sta curnote,x
        lda imask,{ps}                  ; idle gate-mask priming
        sta gatemask,x
        lda iguard,{ps}                 ; post-note-guard leftover priming
        sta guard,x
        lda idurl,{ps}                  ; duration-reload leftover priming
        sta durrel,x                 ; (orig init never writes $173E)
        lda igla,x                   ; glide-start leftover priming (off-table
        sta gla,x                    ; read tracks orig from init; glsp=0 so
        lda iglb,x                   ; fx_glide stays gated off until an arm)
        sta glb,x
{cinst_seed}{prime_step}        inx
        cpx #$03
        bne ini_v
        ; ---- universal reset: silence-clear (ascending, as the family) ----
        ldx #$00
        txa
ini_sid:
        sta $d400,x
        inx
        cpx #$18
        bne ini_sid
{cia_init}        rts

;; ===================== play (once per frame) =====================
{play_wrapper}playframe:
        dec spdctr
        bpl pf_notick
        lda spd
        sta spdctr
pf_notick:
{voice_calls}{ptail_label}{filter_tail}        rts

{reinit_ghost_routine}
;; ===================== per-voice tick/fetch =====================
voice:
        lda vactive,x
        beq vo_frame
        lda spd
        cmp spdctr                   ; tick iff counter just reloaded
        bne vo_frame
        dec dur,x
        lda dur,x
        beq fetch
vo_frame:
        jmp frame_entry

fetch:
        lda path,x                   ; pattern still in progress?
        beq f_newpat                 ; (pat_end clears the hi byte)
        jmp patrd
f_newpat:
        lda trkpl,x
        sta $f8
        lda trkph,x
        sta $f9
trkrd:
        ldy #$00                     ; trkpl/trkph = 16-bit VARIABLE-width stream
        lda ($f8),y                  ; ptr: $FD,T transpose commands (sticky, at
        cmp #$FE                     ; marks) + 2-byte [gid,otrk] pattern entries
        bne trk1                     ; + $FF loop. gid <= $FC (pool <= 253).
        lda #$00                     ; $FE stop: voice off (state freewheels)
        sta vactive,x
        rts
trk1:
        cmp #$FF
        bne trk1b
{trk_ff}trk1b:
        cmp #$FD
        bne trk2
        iny                          ; $FD transpose command: STICKY like the orig
        lda ($f8),y                  ; — set transp, advance 2 bytes, read the
        sec                          ; next entry (transpose threads at runtime,
        sbc #64                      ; not baked per entry)
        sta transp,x
        lda $f8
        clc
        adc #$02
        sta $f8
        bcc trk1c
        inc $f9
trk1c:
        jmp trkrd
trk2:                                ; pattern entry: byte0 = gid, byte1 = otrk
        sta trkg
        iny
        lda ($f8),y                  ; $1726,x of this entry's sector byte
        sta otrk,x
        lda $f8                      ; advance the track ptr by 2 -> next entry
        clc                          ; and store it (pat_end no longer advances)
        adc #$02
        sta $f8
        sta trkpl,x
        lda $f9
        adc #$00
        sta $f9
        sta trkph,x
        ldy trkg
        lda patlo,y
        sta patl,x                   ; 16-bit running pattern pointer
        sta $f8                      ; (patterns may exceed 255 bytes)
        lda pathi,y
        sta path,x
        sta $f9
patrd:
        lda patl,x
        sta $f8
        lda path,x
        sta $f9
        ldy #$00
        lda ($f8),y
        cmp #$01                     ; dispatch via JMP trampolines - the
        bne evd1                     ; handler bodies exceed branch range
        jmp ev_note
evd1:
        cmp #$02
        bne evd2
        jmp ev_rest
evd2:
        cmp #$03
        bne evd3
        jmp ev_switch
evd3:
        cmp #$04
        bne evd4
        jmp ev_slide
evd4:
{tempo_evd}        ; defensive: stray end marker - advance track
        jsr pat_end
        jmp fetch

adv:                                 ; pattern ptr += A (16-bit)
        clc
        adc patl,x
        sta patl,x
        sta $f8
        lda path,x
        adc #$00
        sta path,x
        sta $f9
        rts

sc_slotvol:                          ; STICKY slot/vol suffix (D6 piece 3) for
        lda evflags                  ; rest/switch/slide: the raw duration byte
        and #$40                     ; is stashed in evflags — bit6 = slot, bit7
        beq scv_novol                ; = vol. y is at the duration byte; read the
        iny                          ; STATED slot/vol into the sticky
        lda ($f8),y                  ; curinst,x / volovr,x, then advance the
        sta curinst,x                ; pattern pointer by the bytes consumed.
scv_novol:
        lda evflags
        and #$80
        beq scv_adv
        iny
        lda ($f8),y
        sta volovr,x
scv_adv:
        iny
        tya
        jmp adv                      ; ptr += y+1, then rts back to the caller

ev_rest:
{sp_fetch}        ldy {ev1}
        lda ($f8),y                  ; dur byte (bit6=slot bit7=vol present)
        sta evflags
        and #$3F
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        jsr sc_slotvol
        jsr peekend
        jmp {rest_jmp}

ev_switch:
{sp_fetch}        ldy {ev1}
        lda ($f8),y                  ; dur byte (bit6=slot bit7=vol present)
        sta evflags
        and #$3F
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        lda gatemask,x
        eor {switch_eor}             ; canon $01 = gate bit; wedge = wider cut
        sta gatemask,x
        jsr sc_slotvol
        jsr peekend
        jmp {rest_jmp}

ev_slide:                            ; glide mode 1: current -> target
{sp_fetch}        ldy {ev1}
        lda ($f8),y                  ; speed
        sta glsp,x
        iny
        lda ($f8),y                  ; target (+ transpose)
        clc
        adc transp,x
        sta glb,x
        lda curnote,x
        sta gla,x
        iny
        lda ($f8),y                  ; dur byte (bit6=slot bit7=vol present)
        sta evflags
        and #$3F
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        jsr sc_slotvol
        jsr peekend
        jmp {rest_jmp}

ev_note:
{sp_fetch}        ldy {ev1}
        lda ($f8),y                  ; flags (1=soft 2=glide 8=slot 16=vol)
        sta evflags
        iny
        lda ($f8),y                  ; note
        clc
        adc transp,x
        sta curnote,x
        sty patix                    ; save the byte index across reload_base
        tay                          ; reload_base BEFORE the dur/slot/vol
        jsr reload_base              ; updates: its off-table redirect sonifies
        ldy patix                    ; live dur/durrel, so it must read their
                                     ; PRE-update values (was the original order)
        iny
        lda ($f8),y                  ; duration (always carried)
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        lda evflags
        and #$08                     ; instrument slot STATED? (else sticky)
        beq evn_noslot
        iny
        lda ($f8),y
        sta curinst,x
evn_noslot:
        lda evflags
        and #$10                     ; vol override STATED? (else sticky)
        beq evn_novol
        iny
        lda ($f8),y
        sta volovr,x
evn_novol:
        lda evflags
        and #$02                     ; glide?
        beq evn_ngl
        iny
        lda ($f8),y                  ; glide speed
        sta glsp,x
        iny
        lda ($f8),y                  ; glide target (+ transpose)
        clc
        adc transp,x
        sta glb,x
        lda curnote,x                ; glide start = this note
        sta gla,x
evn_ngl:
        iny                          ; advance = bytes consumed (y+1)
        tya
        jsr adv
ev_n_softq:
        lda evflags
        and #$01
        beq ev_n_hard
        jsr peekend                  ; soft (no retrigger) - orig funnels via
        jmp {rest_jmp}               ; the $117D tail, same JMP as rest/slide
ev_n_hard:
        lda #$00                     ; hard restart prep
        sta accl,x
        sta acch,x
        sta vibdir,x
        sta vibctr,x
        sta rampctr,x
        sta slal,x
        sta slah,x
        ldy sidoff,x
{hr_test_write}{hard_restart_adsr}        lda #$FF
        sta gatemask,x
        sta pend,x
        jsr peekend
        rts                          ; fetch frame writes nothing else

pat_end:
        inc otrk,x                   ; orig $182D: $1726 track position++ at
        lda #$00                     ; sector end. The track pointer was already
        sta path,x                   ; advanced past the entry at fetch (trk2),
        rts                          ; so path=0 just triggers the next fetch.

peekend:
        ldy #$00
        lda ($f8),y                  ; $f8/$f9 track the advanced position
        bne pk_done
        jsr pat_end
pk_done:
        rts

;; ===================== per-voice frame =====================
frame_entry:
        lda pend,x
        bne fe_ni
        jmp run_effects
fe_ni:
        ;; ----- note init (frame 2 of the note) -----
        lda #$00
        sta pend,x
        sta pwl,x                    ; PW accum lo cleared unconditionally
        sta vstep,x
        sta vsteph,x                 ; vib step hi (family-2 16-bit ramp; 0 canon)
        lda curinst,x
        sta cinst,x                  ; cache: soft notes don't re-init
        tay
        lda ioffval,y                ; orig inst# * 11 = $174D,x (off-table shadow)
        sta ioff,x
        lda isr,y
        sta tmp
        lda volovr,x
        beq ni_sr
        asl
        asl
        asl
        asl
        sta tmp2                     ; sustain override
        lda tmp
        and #$0F
        ora tmp2
        sta tmp
ni_sr:
        ldy sidoff,x
        lda tmp
        sta $d406,y                  ; SR
        ldy cinst,x
        lda iad,y
        ldy sidoff,x
        sta $d405,y                  ; AD
        ldy cinst,x
{hr_arm}        lda iflag,y
        and #$04                     ; keep-running pulse?
        bne ni_filter
{hr_disarm}        lda ipwinit,y
        sta pwh,x
        lda ipwmin,y
        sta cpwmin,x
        lda ipwmax,y
        sta cpwmax,x
{pw_base_reset}ni_filter:
        lda iflag,y
        and #$20                     ; filter instrument?
        bne ni_f_on
{route_clear}        jmp ni_vib
ni_f_on:
        lda shadow17
        ora fbit,x
        sta shadow17
        lda iflag,y
        and #$02                     ; keep-running filter?
        bne ni_vib
        lda #$00
        sta fstep
        sta fframe
        lda ifdef,y
        tay                          ; y = def slot = orig def#
        asl
        asl
        asl
        asl                          ; 16*def# (orig def-record stride)
        sta fbase
        lda fdres,y
        sta fres
        lda fdmode,y
{ni_d418}        lda fdinit,y
        sta fcut
        lda fdrep,y
        sta frep
        lda fdstop,y
        sta fstop
        ldy cinst,x
ni_vib:
        lda ivdel,y
        sta vibdel,x
        lda ivwid,y
        sta vibwid,x
        lda ivram,y
        sta cvram,x
        lda iwst,y
        sta wavepos,x
{ni_chase}        lda iflag,y
        sta fxf,x
{ni_vib_depth}        lda #$02
        sta guard,x                  ; gate logic off for 2 frames
{cym_ni}ni_wave:
{ni_wave_tail}

;; ----- running effects -----
{rest_dispatch}{rest_none}run_effects:
        lda guard,x
        beq fx_gate
{cym_rf}        dec guard,x
        jmp fx_pulse
fx_gate:
        lda fxf,x
        and #$10                     ; holding?
        beq fx_g2
        lda dur,x
        cmp #$01                     ; gate off one tick before note end
        bne fx_pulse
        lda #$FE
        sta gatemask,x
{hold_adsr_clear}        jmp fx_pulse
fx_g2:
        lda fxf,x
        and #$08                     ; open gate?
        bne fx_pulse
        lda #$FE                     ; default: release after 3 gate frames
        sta gatemask,x
fx_pulse:
{pulse_index}        lda irawsp,y                 ; raw speed byte -> wjmp (orig $135A
        sta wjmp                     ; STA $171F, before the nibble select)
        lda isteps,y                 ; per-phase step nibble
        clc
        adc cpwbase,x                ; + cached base (0 while idling)
        sta tmp
        sta pwstep,x                 ; live shadow of orig $175C (current PW
                                     ; step) — off-table hi reads sonify it
pw_sweep:                            ; shared by fx_pulse + pulse_tail (R phase)
        lda pwdir,x
        bne fx_pw_dn
        lda pwl,x
        clc
        adc tmp
        sta pwl,x
        lda pwh,x
        adc #$00
        sta pwh,x
        cmp cpwmax,x
        bne fx_filter
        lda #$01
        sta pwdir,x
        jmp fx_pw_ph
fx_pw_dn:
        lda pwl,x
        sec
        sbc tmp
        sta pwl,x
        lda pwh,x
        sbc #$00
        sta pwh,x
        cmp cpwmin,x
        bne fx_filter
        lda #$00
        sta pwdir,x
fx_pw_ph:
        lda pwphase,x
        cmp #$05
        beq fx_filter
        inc pwphase,x
fx_filter:
        lda fxf,x
        and #$20
        beq fx_glide
        lda fclaim
        bne fx_glide
        inx
        stx fclaim                   ; first filter voice claims
        dex
        lda fcut
        cmp fstop
        beq fx_glide
        lda fbase
        clc
        adc fstep
        tay
        lda fdstep,y
        sta fsz                      ; shadow orig $1721 STA (step size cache)
        lda fddur,y
        sta fdu                      ; shadow orig $1722 STA (step dur cache)
        lda fcut
        clc
        adc fsz
        sta fcut
        inc fframe
        lda fframe
        cmp fdu
        bne fx_glide
        lda #$00
        sta fframe
        inc fstep
        lda fstep
        cmp #$06
        bne fx_glide
        lda frep
        sta fstep
fx_glide:
        lda glsp,x
        beq fx_vibdel
        asl
        asl
        asl
        asl
        sta tmp                      ; step = speed << 4
        sta wjmp                     ; shadow orig $1425 STA $171F
        lda gla,x
        cmp glb,x
        bcs fx_gl_dn
        lda accl,x                   ; gliding up
        clc
        adc tmp
        sta accl,x
        lda acch,x
        adc #$00
        sta acch,x
        jmp fx_gl_chk
fx_gl_dn:
        lda accl,x                   ; gliding down
        sec
        sbc tmp
        sta accl,x
        lda acch,x
        sbc #$00
        sta acch,x
fx_gl_chk:
        ldy glb,x
        lda accl,x
        clc
        adc fbl,x
        lda acch,x
        adc fbh,x
{ga_cmp}        bne fx_gl_out
        tya
        sta curnote,x
        jsr reload_base              ; base freq freqlo/hi[target];
                                     ; off-table idx served live (redirect)
        lda #$00
        sta glsp,x
        sta accl,x
        sta acch,x
fx_gl_out:
        jmp wavestep                 ; glide active: no vibrato this frame
fx_vibdel:
        lda vibdel,x
        beq fx_dual
        dec vibdel,x
        jmp wavestep
fx_dual:
        lda fxf,x
        and #$40
        beq fx_vib
        inc dualpar                  ; global half-rate parity
        lda dualpar
        and #$01
        sta dualpar
        bne fx_dual_run
        jmp wavestep
{dual_run}
fx_vib:
        lda vibdir,x
        bne fx_vib_dn
        lda accl,x
        clc
        adc vstep,x
        sta accl,x
        lda acch,x
        adc vsteph,x                 ; 16-bit step (vsteph=0 for canon)
        sta acch,x
        jmp fx_vib_c
fx_vib_dn:
        lda accl,x
        sec
        sbc vstep,x
        sta accl,x
        lda acch,x
        sbc vsteph,x
        sta acch,x
fx_vib_c:
        inc vibctr,x
        lda vibctr,x
        cmp vibwid,x
        bne wavestep
vib_half:                            ; rest_effects='vibflip' entry (canon $1567)
        lda #$00                     ; half-cycle boundary
        sta vibctr,x
        lda vibdir,x
        eor #$01
        sta vibdir,x
        lda rampctr,x
        cmp cvram,x
        beq wavestep
        inc rampctr,x
{vib_swell}
;; ----- wave step + SID writes -----
;; pool bytes >= $90 are jump-back markers (the original's semantics:
;; position -= value - $90, then re-read)
wavestep:
        lda fxf,x
        and #$01                     ; drum mode?
        beq ws_notdrum               ; (jmp: ws_drum is past the off-table redirect)
        jmp ws_drum
ws_notdrum:
ws_rd0:
        ldy wavepos,x
        lda wctab,y
        cmp #$90
        bcc ws_rd
        sbc #$90                     ; (carry set)
        sta tmp
        sta wjmp                     ; shadow orig $15A5 STA $171F
        tya
        sec
        sbc tmp
        sta wavepos,x
        jmp ws_rd0
ws_rd:
        sta wctrl,x
        lda wftab,y
        clc
        adc curnote,x                ; semitone offset -> table rebase
        sta wnote,x                  ; orig $1783: arp note (wave offset+curnote),
                                     ; stored every melodic wave-step. Read
                                     ; off-table as a freq by the modulation idiom.
        tay
        ; OFF-TABLE READ-REDIRECT: off-table indices sonify live engine state
        ; ($1707-$17A6); reproduce by reading our own byte-identical variable.
        ; Generated from DMC_OFFTABLE_STATE (composer-side map; USF unchanged).
{ws_lo_redirect}
ws_rd_los:
        sta fbl,x
{ws_hi_redirect}
ws_rd_his:
        sta fbh,x
        inc wavepos,x
        jmp sidwrite
ws_drum:
        ldy wavepos,x
        lda wctab,y
        cmp #$90
        bcc ws_drd
        sbc #$90
        sta tmp
        sta wjmp                     ; shadow orig $15E2 STA $171F
        tya
        sec
        sbc tmp
        sta wavepos,x
        jmp ws_drum
ws_drd:
        sta wctrl,x
        lda #$00
        sta fbl,x
        lda wftab,y                  ; absolute freq hi
{ws_drum_fhi}
        inc wavepos,x
sidwrite:
        ldy sidoff,x
        lda fbl,x
        clc
        adc accl,x
        sta $d400,y
        lda fbh,x
        adc acch,x
        sta $d401,y
pwwrite:
        lda pwl,x
        sta $d402,y
{pw_hi_load}
        sta $d403,y
        lda wctrl,x
        and gatemask,x
        sta $d404,y
        rts

;; ===== base-freq reload (note-fetch + glide arrival), off-table-redirected =====
;; Y = note index (curnote / glide target); X = voice. Reads freqlo/hi[Y] but
;; serves an off-table (wrapped / high-transpose) index from the live state map,
;; mirroring the orig's `lda freqlo,y` which lands on the engine state block.
reload_base:
{nf_lo_redirect}
nf_rd_los:
        sta fbl,x
{nf_hi_redirect}
nf_rd_his:
        sta fbh,x
        rts

{ga_cmp_sub}
;; ===================== data (from USF) =====================
{data_asm}

;; ===================== state =====================
state0:
vactive:  .dsb 3, 0
gatemask: .dsb 3, 0
curnote:  .dsb 3, 0
curinst:  .dsb 3, 0
cinst:    .dsb 3, 0
volovr:   .dsb 3, 0
trkpl:    .dsb 3, 0
trkph:    .dsb 3, 0
patl:     .dsb 3, 0
path:     .dsb 3, 0
transp:   .dsb 3, 0
fbl:      .dsb 3, 0
fbh:      .dsb 3, 0
accl:     .dsb 3, 0
acch:     .dsb 3, 0
dur:      .dsb 3, 0
glsp:     .dsb 3, 0
gla:      .dsb 3, 0
glb:      .dsb 3, 0
pend:     .dsb 3, 0
pwl:      .dsb 3, 0
pwh:      .dsb 3, 0
cpwmin:   .dsb 3, 0
cpwmax:   .dsb 3, 0
cpwbase:  .dsb 3, 0
pwphase:  .dsb 3, 0
pwdir:    .dsb 3, 0
pwstep:   .dsb 3, 0
vibdir:   .dsb 3, 0
vibctr:   .dsb 3, 0
rampctr:  .dsb 3, 0
vibdel:   .dsb 3, 0
vibwid:   .dsb 3, 0
cvram:    .dsb 3, 0
vstep:    .dsb 3, 0
vsteph:   .dsb 3, 0
vdep:     .dsb 3, 0
wavepos:  .dsb 3, 0
fxf:      .dsb 3, 0
wctrl:    .dsb 3, 0
guard:    .dsb 3, 0
slal:     .dsb 3, 0
slah:     .dsb 3, 0
dtmpl:    .dsb 1, 0                  ; dual-slide freq temp (= orig $1724/25,
dtmph:    .dsb 1, 0                  ; global; sonified by off-table idx 221)
spdctr:   .dsb 1, 0
shadow17: .dsb 1, 0
dualpar:  .dsb 1, 0
fclaim:   .dsb 1, 0
fstep:    .dsb 1, 0
fframe:   .dsb 1, 0
fsz:      .dsb 1, 0                  ; filter step size cache (= orig $1721)
fdu:      .dsb 1, 0                  ; filter step duration cache (= orig $1722)
fbase:    .dsb 1, 0
fcut:     .dsb 1, 0
frep:     .dsb 1, 0
fstop:    .dsb 1, 0
fres:     .dsb 1, 0
tmp:      .dsb 1, 0
tmp2:     .dsb 1, 0
wjmp:     .dsb 1, 0                  ; orig $171F shared-scratch shadow (raw
                                     ; pulse speed byte / glide step / wave
                                     ; jump-back distance — last writer wins)
evflags:  .dsb 1, 0
patix:    .dsb 1, 0                  ; ev_note byte-index saved across reload_base
trkg:     .dsb 1, 0                  ; track pattern-gid held across the fetch advance
otrk:     .dsb 3, 0                  ; orig track byte-offset shadow (= $1726)
wnote:    .dsb 3, 0                  ; orig arp-note shadow (= $1783)
durrel:   .dsb 3, 0                  ; orig duration-reload shadow (= $173E)
ioff:     .dsb 3, 0                  ; orig instrument-offset shadow (= $174D)
{rest_var}{d418_var}{sectpos_bss}state_end:
{cursong_var}{hr_test_var}{dual_vars}        .byt $00
"""
    return _reloc_sid_regs(asm, reg_delta, keep_regs)


def _sanitize_asm(asm: str) -> str:
    """xa65 treats ':' as a statement separator even inside ';' comments —
    scrub colons (and non-ASCII) out of comment text."""
    out = []
    for line in asm.split('\n'):
        if ';' in line:
            code, _, comment = line.partition(';')
            line = code + '; ' + comment.replace(':', '-').strip()
        out.append(line)
    return '\n'.join(out).encode('ascii', 'replace').decode('ascii')


def _split_chip_usf(usf: UsfFile, ci: int) -> UsfFile:
    """Carve chip `ci`'s standalone 3-voice DMC USF out of a merged multi-SID
    USF — the exact inverse of merge_2sid_usf. Each chip's instruments +
    filter programs occupy a fixed-stride disjoint id block (chip c shifted
    by c*STRIDE); select that block and renumber it back to the chip's
    standalone form (so the sub-USF is byte-for-byte what a single-chip
    extraction of that player would produce), take its 3 voices (renumbered
    1-3, note refs un-shifted), and its own priming. freq_table / wave
    programs / params are shared. Every subtune is carved (the chips share
    one subtune list — subtune s of the merged USF holds chip ci's subtune s
    with its own tempo/priming)."""
    import dataclasses
    from pipelines.dmc.v4.extract.to_usf import (
        MULTISID_INSTR_STRIDE as ISTR, MULTISID_FILTER_STRIDE as FSTR,
        _offset_note_refs)
    ilo, ihi = ci * ISTR, (ci + 1) * ISTR       # id in (ilo, ihi]
    flo, fhi = ci * FSTR, (ci + 1) * FSTR
    instrs = []
    for i in usf.instruments:
        if ilo < i.id <= ihi:
            fp = i.filter_prog
            if fp and fp.program:
                fp = dataclasses.replace(fp, program=fp.program - flo)
            instrs.append(dataclasses.replace(i, id=i.id - ilo, filter_prog=fp))
    filters = {p - flo: d for p, d in usf.filter_programs.items()
               if flo < p <= fhi}
    ivs = [dataclasses.replace(iv, id=iv.id - ci * 3)
           for iv in usf.init.voices if ci * 3 < iv.id <= ci * 3 + 3]
    file_sid = [usf.init.sid, usf.init.sid2, usf.init.sid3][ci]
    # per-voice params (`..._v<N>`) renumber back to this chip's 1-3;
    # per-chip params take this chip's ';'-separated part; the rest are
    # player-wide and carry through (the inverse of merge_2sid_usf)
    from pipelines.dmc.v4.extract.to_usf import (_VOICE_KEY,
                                                 MULTISID_PER_CHIP_KEYS)
    pf = {}
    for k, v in usf.params.fields.items():
        mv = _VOICE_KEY.match(k)
        if k in MULTISID_PER_CHIP_KEYS:
            # merge_2sid_usf always emits one part PER CHIP, so a single-part
            # value is a .usf written before the key became per-chip — read it
            # with the old player-wide meaning rather than silently dropping
            # the schedule for every chip but the first.
            parts = str(v).split(';')
            part = parts[0] if len(parts) == 1 else (
                parts[ci] if ci < len(parts) else '')
            if part:
                pf[k] = part
        elif not mv:
            pf[k] = v
        elif ci * 3 < int(mv.group(2)) <= ci * 3 + 3:
            pf[f'{mv.group(1)}{int(mv.group(2)) - ci * 3}'] = v
    params = dataclasses.replace(usf.params, fields=pf)
    subts = []
    for sub in usf.subtunes:
        # select by voice ID, not position: a subtune whose dispatch wrapper
        # skips a chip carries no voices for it (see multisid_active_chips)
        mine = [v for v in sub.voices if ci * 3 < v.id <= ci * 3 + 3]
        vren = [dataclasses.replace(v, id=v.id - ci * 3,
                                    patterns=[dataclasses.replace(
                                        p, rows=_offset_note_refs(p.rows, -ilo))
                                        for p in v.patterns])
                for v in mine]
        if not vren:
            # this chip's player is never called for this subtune, but it
            # still needs a song-table slot so A=subtune stays aligned —
            # emit a stopped 3-voice placeholder (it produces no writes)
            vren = [VoiceBlock(id=k + 1,
                               orderlist=Orderlist(entries=[], stop=True),
                               patterns=[]) for k in range(3)]
        # per-subtune resolver seeds (stated rows) live on the SUBTUNE init —
        # a distinct level from the file-level idle voices above
        seed_ivs = [dataclasses.replace(iv, id=iv.id - ci * 3)
                    for iv in (sub.init.voices if sub.init else [])
                    if ci * 3 < iv.id <= ci * 3 + 3]
        # this subtune's own per-chip priming; falls back to the file-level
        # block for USFs written before per-subtune `sid 2/3` was emitted
        chip_sid = ([sub.init.sid, sub.init.sid2, sub.init.sid3][ci]
                    if sub.init else None) or file_sid
        tempo = [sub.tempo, sub.tempo2, sub.tempo3][ci]
        if tempo is None:
            tempo = sub.tempo
        subts.append(MusicSubtune(
            id=sub.id, tempo=tempo, voices=vren,
            init=InitState(voices=seed_ivs, sid=chip_sid)))
    init = InitState(voices=ivs, sid=file_sid)
    return dataclasses.replace(usf, instruments=instrs, params=params,
                               filter_programs=filters, subtunes=subts,
                               init=init)


def build_dmc_2sid_sid(usf: UsfFile) -> bytes:
    """Multi-SID build: emit one independent DMC player per chip (each at its
    own origin, chip k>0 writing $D400+k*$20 via reg_delta), then a dispatch
    stub at $1000 whose init/play call each player in turn. The merged
    write-log = [chip1's stream][chip2's stream] (players run sequentially),
    which is exactly the original's per-frame ordering.

    A subtune need not sound every chip (Rayden's 2SID builds ship a
    both-chips subtune plus a chip-1-only and a chip-2-only rendition): a
    chip sounds in a subtune iff the subtune carries its voices, and the
    dispatcher gates that chip's init+play calls on a per-subtune activity
    byte. The original neuters its calls by SMC-patching JSR<->BIT; per the
    core tenet we emit clean gated calls that produce the same writes."""
    n_chips = max((max(v.id for v in s.voices) + 2) // 3
                  for s in usf.subtunes if s.voices)
    # chip ci sounds in subtune s iff s carries a voice in ci's id block
    act = [{(v.id - 1) // 3 for v in s.voices} for s in usf.subtunes]
    # per-chip un-relocated stores (C19, ';'-separated chip order) — empty
    # for the fully relocated players the editor normally produces. An entry
    # is either `NN` (every store to that register) or `NN@label` (only the
    # stores inside the composer routine `label` — the miss is per-STORE).
    def _keep_entry(r):
        reg, _, role = r.partition('@')
        return (int(reg, 16), role) if role else int(reg, 16)

    keep = [frozenset(_keep_entry(r) for r in part.split(',') if r)
            for part in
            usf.params.fields.get('multisid_keep_regs', '').split(';')]
    keep += [frozenset()] * (n_chips - len(keep))
    origin = 0x1100                       # players sit above the dispatcher
    blobs = []                            # (origin, bytes)
    entries = []                          # (init_addr, play_addr) per chip
    for ci in range(n_chips):
        sub_usf = _split_chip_usf(usf, ci)
        asm = _sanitize_asm(
            compose_dmc_asm(sub_usf, origin=origin, reg_delta=ci * 0x20,
                            keep_regs=keep[ci]))
        blob = assemble(asm)
        blobs.append((origin, blob))
        entries.append((origin, origin + 3))
        origin = (origin + len(blob) + 1) & ~1     # word-align next player

    # dispatcher at $1000: init (A=subtune) calls each active player's init;
    # play calls each active player's play. Players run in chip order so
    # their writes land chip1-then-chip2 within the frame (matches the
    # original wrapper). `actN` is latched at init from a per-subtune table
    # so the play path costs one load+branch per chip.
    gated = any(len(a) != n_chips for a in act)
    init_calls, play_calls, tables = [], [], []
    for ci, e in enumerate(entries):
        if not gated:
            init_calls.append(f'        jsr ${e[0]:04X}\n        lda subsav')
            play_calls.append(f'        jsr ${e[1]:04X}')
            continue
        init_calls.append(
            f'        ldx subsav\n'
            f'        lda actab{ci},x\n'
            f'        sta act{ci}\n'
            f'        beq skipi{ci}\n'
            f'        lda subsav\n'
            f'        jsr ${e[0]:04X}\n'
            f'skipi{ci}:')
        play_calls.append(
            f'        lda act{ci}\n'
            f'        beq skipp{ci}\n'
            f'        jsr ${e[1]:04X}\n'
            f'skipp{ci}:')
        tables.append(
            f'actab{ci}: .byt ' +
            ','.join('$%02X' % (1 if ci in a else 0) for a in act))
        tables.append(f'act{ci}: .byt $00')
    disp = """        * = $1000
        jmp cinit
        jmp cplay
cinit:
        sta subsav
{init_calls}
        rts
cplay:
{play_calls}
        rts
subsav: .byt $00
{tables}
""".format(init_calls='\n'.join(init_calls),
           play_calls='\n'.join(play_calls),
           tables='\n'.join(tables))
    dblob = assemble(disp)
    blobs.insert(0, (0x1000, dblob))
    end = max(o + len(b) for o, b in blobs)
    image = bytearray(end - LOAD)
    for o, b in blobs:
        image[o - LOAD:o - LOAD + len(b)] = b

    clock = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid, 0)
    m2 = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid2, 0)
    m3 = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid3, 0)
    # CIA multispeed: set the PSID speed bits so the host drives play() off
    # the timer each player programs (build_dmc_sid does the same for
    # single-chip). The USF's psid.speed carries the orig's PER-SUBTUNE mask
    # (a file can mix a CIA song with vblank ones — F_A_K_E-Intro); an absent
    # mask (older stored .usf) falls back to all-subtunes = the pre-r131
    # behaviour, byte-identical.
    _sm = usf.psid.speed & ((1 << len(usf.subtunes)) - 1)
    speed = ((_sm or ((1 << len(usf.subtunes)) - 1)) if (
        usf.environment and usf.environment.cia_period) else 0)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        speed=speed, title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
        flags=(clock << 2) | (sidm << 4) | (m2 << 6) | (m3 << 8),
        sid2_addr=0xD420 if n_chips >= 2 else 0,
        sid3_addr=0xD440 if n_chips >= 3 else 0)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + bytes(image)


def build_dmc_compilation_sid(usf: UsfFile) -> bytes:
    """HETEROGENEOUS compilation (ledger C31): the file's subtunes split across
    the DMC engine (MusicSubtune) and the embedded dmc_sfx sub-player
    (DmcSfxSubtune, content in usf.dmc_sfx). Emit BOTH engines into one image
    behind a per-subtune dispatch stub at $1000 that routes init/play to the
    engine owning the selected subtune (only one engine runs per subtune, so
    the per-subtune write streams are independent — matching the original)."""
    import dataclasses
    from pipelines.dmc.sfx_composer import compose_sfx_asm
    subs = sorted(usf.subtunes, key=lambda s: s.id)
    dmc_subs = [s for s in subs if isinstance(s, MusicSubtune)]

    # per PSID subtune: (engine 0=DMC/1=SFX, index within that engine)
    engtab, idxtab, dmc_i = [], [], 0
    for s in subs:
        if isinstance(s, MusicSubtune):
            engtab.append(0)
            idxtab.append(dmc_i)
            dmc_i += 1
        else:                                   # DmcSfxSubtune
            engtab.append(1)
            idxtab.append(s.song)

    dmc_origin = 0x1100
    dmc_usf = dataclasses.replace(
        usf, subtunes=dmc_subs, dmc_sfx=None,
        psid=dataclasses.replace(usf.psid, start_song=1))
    dmc_asm = _sanitize_asm(compose_dmc_asm(dmc_usf, origin=dmc_origin))
    dmc_blob = assemble(dmc_asm)
    sfx_origin = (dmc_origin + len(dmc_blob) + 1) & ~1
    sfx_blob = assemble(compose_sfx_asm(usf.dmc_sfx, origin=sfx_origin))

    di, dp = dmc_origin, dmc_origin + 3
    si, sp = sfx_origin, sfx_origin + 3
    engs = ', '.join(f'${e:02X}' for e in engtab)
    idxs = ', '.join(f'${i:02X}' for i in idxtab)
    disp = f"""        * = $1000
        jmp cinit
        jmp cplay
cinit:
        tax
        lda cengtab,x
        sta cactive
        lda cidxtab,x                ; A = index within the selected engine
        ldy cactive
        bne ci_sfx
        jmp ${di:04X}
ci_sfx:
        jmp ${si:04X}
cplay:
        lda cactive
        bne cp_sfx
        jmp ${dp:04X}
cp_sfx:
        jmp ${sp:04X}
cactive: .byt $00
cengtab: .byt {engs}
cidxtab: .byt {idxs}
"""
    dblob = assemble(disp)
    blobs = [(0x1000, dblob), (dmc_origin, dmc_blob), (sfx_origin, sfx_blob)]
    end = max(o + len(b) for o, b in blobs)
    image = bytearray(end - LOAD)
    for o, b in blobs:
        image[o - LOAD:o - LOAD + len(b)] = b
    clock = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid, 0)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(subs), start_song=usf.psid.start_song,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=(clock << 2) | (sidm << 4))
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + bytes(image)


def build_dmc_sid(usf: UsfFile) -> bytes:
    if getattr(usf, 'dmc_sfx', None) is not None:
        return build_dmc_compilation_sid(usf)
    if usf.subtunes and getattr(usf.subtunes[0], 'voices', None) \
            and len(usf.subtunes[0].voices) > 3:
        return build_dmc_2sid_sid(usf)
    asm = _sanitize_asm(compose_dmc_asm(usf))
    code = assemble(asm)
    # CIA multispeed: set the PSID speed bits so libsidplayfp drives play()
    # via the CIA1 timer A our init programs. psid.speed = the orig's
    # PER-SUBTUNE mask; absent mask -> all subtunes (pre-r131 behaviour).
    _sm = usf.psid.speed & ((1 << len(usf.subtunes)) - 1)
    speed = ((_sm or ((1 << len(usf.subtunes)) - 1)) if (
        usf.environment and usf.environment.cia_period) else 0)
    # Header clock/SID-model flags from the USF psid block (extracted from
    # the orig header): the write-log verdict is BLIND to these, but a 6581
    # build of an 8580 tune sounds wrong (filter curve, combined waves) —
    # 63% of the DMC corpus is flagged 8580.
    clock = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid, 0)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        speed=speed, title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=(clock << 2) | (sidm << 4))
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code
