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
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.usf.types import UsfFile, Pitch
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header, FLAGS_PAL_6581
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
    # NOT mapped: $1720 fclaim (voice/claim ordering differs — rejected f2) and
    # $1721/$1722 step-size/dur caches (the composer reads them inline from the
    # fdstep/fddur def views — no cache VAR to redirect to). (fcut $171C IS
    # mapped below — the old "regressed Humppa" caution was fcut+wavepos bundled;
    # fcut alone tracks and is 0-regression, exposure-censused this round.)
    (0x1718, 'spdctr', 1),   # speed counter (DEC per frame; reload = $1716)
    (0x171C, 'fcut', 1),     # filter current cutoff (-> $D416 every frame). The
                             # composer's fcut drives the identical $D416 stream,
                             # so it tracks $171C by construction (verified
                             # index+value on King_of_Earth $20==$20). The old
                             # "regressed Humppa" note (C11) was fcut BUNDLED with
                             # wavepos $177A (the positional-hard byte); fcut alone
                             # is clean — exposure-censused this round.
    (0x1719, 'fstep', 1),    # filter current step index 0-5
    (0x171A, 'fframe', 1),   # filter frames spent in current step
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
    # NOTE: wavepos ($177A) + fcut ($171C) are read off-table by Object_of_Art's
    # wave program (arp=213 -> hi=wavepos, lo=fcut). Mapping them was net-negative
    # (0 recoveries, 1 regression / 33 FULLs): the HI byte sonifies the ABSOLUTE
    # wave position, but our composer re-packs the wave pool with its own offsets
    # (iwst), so our wavepos diverges from the orig's (+5 for Object_of_Art's
    # V2/V3) — the off-table read can't match without reproducing the orig's
    # wave-pool LAYOUT byte-for-byte (the hard C11 encoding-specific class).
    # Mapping also regressed a FULL whose off-table read matched via the static
    # overrun byte. So: off-table-wavepos reads are BLOCKED on the wave-pool
    # layout, not addable as a redirect entry. See ledger C11 / project_dmc.
]


def _gen_offtable_redirect(state_map, orig_base, win_min, static_load,
                           store_label):
    """Emit the wave-step off-table redirect for one read (lo or hi).

    For each state variable whose table index (orig_addr - orig_base) lands in
    the off-table window [win_min, 255], emit a range check that reads our live
    variable; else fall through to ``static_load``. Y holds the rebased index.
    Returns asm text; the caller places the ``store_label:`` that the in-range
    branches jmp to. Engine-blind — reused per engine with its own map."""
    parts = []
    i = 0
    for addr, label, nb in state_map:
        off = addr - orig_base
        if off < win_min or off + nb > 256:
            continue                     # not in this read's off-table window
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
        if 'gate_toggle' in flags:
            return ('switch', row.duration)
        return ('rest', row.duration)
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
        return ('slide', gspd, note, row.duration)
    soft = 1 if 'noretrig' in flags else 0
    if 'glide_to' in flags:
        tgt = flags['glide_to']
        # NB the `len(tgt)==3` guard drops the '#' for a 2-digit-octave sharp
        # (F#10 -> parsed as F-10, one semitone low). This LOOKS like a bug, but
        # DO NOT "fix" it by `sep = tgt[1]`: glide_to octave-10+ targets are
        # off-table "notes" (raw noteB byte $7E etc.) whose arrival check reads
        # freqhi[126]=$1725=dtmph — a DYNAMIC scratch byte (C11 hard boundary).
        # The parsed-125 target terminates the sweep on freqhi[125]=$1724=dtmpl,
        # which is in a self-consistent balance with the composer's state; the
        # "correct" 126 breaks it. Verified: `sep=tgt[1]` REGRESSED 20/104 FULL
        # members (Calypso C-3->F#10 = a 90-semitone sweep, not a real glide),
        # recovered 0 (Plasmachaos, the degenerate gla==125 case, has an otrk
        # 2nd blocker). Round-22 investigation; left as-is.
        sep = tgt[1] if len(tgt) == 3 else '-'
        name = tgt[0] + ('#' if sep == '#' else '')
        target = int(tgt[2:]) * 12 + NOTE_IDX[name]
        if target == note and len(tgt) > 3 and tgt[1] == '#':
            target = int(tgt[2:]) * 12 + NOTE_IDX[tgt[0] + '#']
        return ('note', soft, note, row.duration, slot, vol, gspd, target)
    return ('note', soft, note, row.duration, slot, vol, 0, None)


def _encode_pattern(rows_events: list) -> bytes:
    out = bytearray()
    for ev in rows_events:
        kind = ev[0]
        if kind == 'rest':
            out += bytes([0x02, ev[1] & 0x3F])
        elif kind == 'switch':
            out += bytes([0x03, ev[1] & 0x3F])
        elif kind == 'slide':
            _, gspd, note, dur = ev
            out += bytes([0x04, gspd, note, dur & 0x3F])
        else:
            _, soft, note, dur, slot, vol, gspd, target = ev
            # glide tail keyed on TARGET PRESENCE, not speed truthiness: a
            # mode-0 glide with speed 0 is the engine's glide-cancel (glsp
            # gets STORED 0), which must reach ev_note's glide path (C22).
            f = soft | (2 if target is not None else 0)
            out += bytes([0x01, f, note, dur & 0x3F, slot, vol])
            if target is not None:
                out += bytes([gspd, target])
    out.append(0x00)
    return bytes(out)


class _Model:
    """Everything the asm emitter needs, distilled from the USF."""

    def __init__(self, usf: UsfFile):
        self.usf = usf
        self.instruments = list(usf.instruments)
        self.inst_slot = {i.id: k for k, i in enumerate(self.instruments)}
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
                pad = int(usf.params.fields.get(
                    f'otrk_pad_s{sub.id}_v{v.id}', 0) or 0)
                period = int(usf.params.fields.get(
                    f'otrk_period_s{sub.id}_v{v.id}', 0) or 0) \
                    or len(ol.entries) or 1
                legacy = bool(usf.params.fields.get(
                    f'otrk_legacy_s{sub.id}_v{v.id}', 0))
                # rcmd = bitmask of physical entries the composer preceded with
                # a REDUNDANT transpose command (their arrangement); the byte
                # offset is DERIVED from it (each such command = +1 byte for
                # that entry onward, within the period). See _otrk_rcmd_model.
                rcmd = int(usf.params.fields.get(
                    f'otrk_rcmd_s{sub.id}_v{v.id}', 0) or 0)
                # cur = the transpose the leading command already set (matches
                # _otrk_model / _otrk_rcmd_model — avoids double-counting a
                # leading transpose command; pad covers its byte)
                cur0 = ol.transpose_at(0) if ol.entries else 0
                off, cur, red = pad, cur0, 0
                for i, e in enumerate(ol.entries):
                    p = i % period
                    if i and p == 0:
                        off, cur, red = pad, cur0, 0  # physical-track boundary
                    enc = _encode_pattern(
                        [_row_event(r, self.inst_slot)
                         for r in pat_by_local[e].rows])
                    gid = pat_ids.get(enc)
                    if gid is None:
                        gid = len(self.patterns)
                        self.patterns.append(enc)
                        pat_ids[enc] = gid
                    t = ol.transpose_at(i)
                    if t != cur:
                        off, cur = off + 1, t
                    if rcmd & (1 << p):
                        red += 1
                    # legacy: unmodeled counter phase (piecewise redundancy)
                    # -> the historical entry+1 approximation, unchanged
                    val = (i + 1) if legacy else (off + red)
                    track += bytes([(t + 64) & 0xFF, gid, val & 0xFF])
                    off += 1
                # loop tail emitted by the data section as a label-arithmetic
                # 16-bit target ($FF, <lbl+n*3, >lbl+n*3): a 3-byte-entry
                # track exceeds 255 bytes past 85 entries, so both the loop
                # target and the runtime track position must be 16-bit
                # (Happy_Hour V1: 198 entries / 594 bytes; the old 8-bit
                # `(loop_to*3) & 0xFF` + `ldy trkpos,x` silently wrapped).
                if ol.stop:
                    track.append(0xFE)
                    voices.append((bytes(track), None))
                else:
                    voices.append((bytes(track), (ol.loop_to or 0)))
            sid = sub.init.sid if (sub.init and sub.init.sid) else None
            mvol = sid.master_vol if sid and sid.master_vol is not None else 0x0F
            routing = (sid.filter.res_routing
                       if sid and sid.filter else 0)
            self.subtunes.append({
                'tracks': voices, 'speed': sub.tempo,
                'mvol': mvol, 'routing': routing,
            })
        assert len(self.patterns) <= 255, 'pattern pool overflow'
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

        ip = usf.wave_programs.get(0)
        if ip and ip['ctrl']:
            add_prog(ip['ctrl'], ip['freq'], ip.get('loop', 0))
        elif self.instruments:
            i0 = self.instruments[0]
            add_prog(i0.waveform, i0.wave_freq or [0] * len(i0.waveform),
                     i0.loop)
        for inst in self.instruments:
            self.iwst.append(add_prog(
                inst.waveform, inst.wave_freq or [0] * len(inst.waveform),
                inst.loop))
        assert len(self.wctrl) <= 255, 'wave pool overflow'

    def iflags(self, inst) -> int:
        f = 0
        if 'drum' in inst.effects:
            f |= 0x01
        if inst.filter_prog.keep_running:
            f |= 0x02
        if inst.pwm.keep_running:
            f |= 0x04
        if inst.envelope.gate_mode == 'open':
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


def compose_dmc_asm(usf: UsfFile) -> str:
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
        isteps += [s & 0xF0 for s in ss] + [0, 0]       # stride 8
        # raw instr+3..5 speed bytes (hi nibble = even-phase step, lo nibble =
        # odd-phase step >> 4 — exact inverse of the extract's nibs decode),
        # duplicated per parity so fx_pulse reuses the isteps index. Feeds the
        # wjmp shadow of orig $171F ($1357: LDA raw / STA $171F).
        raw3 = [(ss[2 * k] & 0xF0) | ((ss[2 * k + 1] & 0xF0) >> 4)
                for k in range(3)]
        irawsp += [raw3[0], raw3[0], raw3[1], raw3[1],
                   raw3[2], raw3[2], 0, 0]              # stride 8
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

    # ---- tune records + tracks + patterns ----
    tune_lines = []
    track_blobs = []
    for si, sub in enumerate(m.subtunes):
        refs = []
        for vi in range(3):
            lbl = f'trk_{si}_{vi}'
            track_blobs.append((lbl, sub['tracks'][vi]))
            refs.append(lbl)
        tune_lines.append(
            f'        .byt <{refs[0]}, >{refs[0]}, <{refs[1]}, >{refs[1]}, '
            f'<{refs[2]}, >{refs[2]}, ${sub["speed"]:02X}, ${sub["mvol"]:02X}, '
            f'${sub["routing"]:02X}, $00, $00, $00, $00, $00, $00, $00')
    def _ptr_tab(pfx):
        lines = []
        for i in range(0, len(m.patterns), 12):
            lines.append('        .byt ' + ', '.join(
                f'{pfx}pat_{k}' for k in range(i, min(i + 12, len(m.patterns)))))
        return '\n'.join(lines)
    pat_lo = _ptr_tab('<')
    pat_hi = _ptr_tab('>')

    slide_phase = int(usf.params.fields.get('slide_phase', 0)) & 1
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
    # sub_17FB, so the hard restart drops the AD/SR=$0F0F writes).
    hard_restart = str(usf.params.fields.get('hard_restart', 'preset'))
    hard_restart_adsr = ('' if hard_restart == 'none' else
                         '        lda #$0F\n'
                         '        sta $d405,y                  ; AD = $0F\n'
                         '        sta $d406,y                  ; SR = $0F\n')
    # rest / switch / slide (duration events that don't retrigger): canon
    # runs the full effect chain on the fetch frame ('run'); family 2 skips
    # straight to the wave step ('skip', the original's JMP $1591) — so the
    # vibrato + pulse program hold for that one frame (a one-frame modulator
    # stall at each tie boundary).
    rest_effects = str(usf.params.fields.get('rest_effects', 'run'))
    rest_jmp = 'wavestep' if rest_effects == 'skip' else 'run_effects'
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
    hr_patch = str(usf.params.fields.get('hr_patch', '0')) == '1'
    hr_test_init = int(usf.params.fields.get('hr_test_init', 1)) & 1
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
        hr_test_write = ('        lda #$08\n'
                         '        sta $d404,y                  ; TEST bit\n')
        hr_arm = hr_disarm = hr_test_var = ''
        pw_base_reset = ('        lda ipwbase,y\n'
                         '        sta cpwbase,x\n'
                         '        lda #$00\n'
                         '        sta pwphase,x\n'
                         '        sta pwdir,x\n')
    # CIA multispeed: when the original drives play() via a CIA1 timer
    # (PSID speed bit set), the rebuild programs the SAME timer A latch
    # so libsidplayfp calls OUR play() at the identical rate. 0 = VBI.
    cia_period = int(usf.params.fields.get('cia_period', 0)) & 0xFFFF
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
    play_repeat = max(1, int(usf.params.fields.get('play_repeat', 1)))
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
    notestart_arm = str(usf.params.fields.get('notestart_arm', '0')) == '1'
    voice_fx_target = 'wavestep' if notestart_arm else 'frame_entry'
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
                body = ''             # per-voice glide/write tail ($141C)
                for v in t[1:]:       # only; re-emits current freq/PW/ctrl
                    body += (f'        ldx #{int(v) - 1}\n'
                             '        jsr fx_glide\n')
                body += '        rts\n'
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
            f'        jmp {voice_fx_target}\n\n')   # frame_entry ($11F9: note-init
            # or effects) for the immediate note-start; wavestep ($1591: emit +
            # advance wave, PAST note-init/gate/pulse) when notestart_arm, so
            # pending survives to the next P call = the 2-frame arm
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
    d418_every_play = usf.params.fields.get('d418_every_play', None)
    if d418_every_play is not None:
        play_wrapper = (
            'playd418:\n'
            f'        lda #${int(d418_every_play) & 0xFF:02X}\n'
            '        sta $d418                    ; play-vector wrapper\n'
            f'        jmp {play_entry}\n\n') + play_wrapper
        play_entry = 'playd418'
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
    pur_s = str(usf.params.fields.get('play_unit_repeat', '') or '1,1,1,1')
    try:
        play_unit_repeat = [max(1, int(x)) for x in pur_s.split(',')]
    except ValueError:
        play_unit_repeat = [1, 1, 1, 1]
    play_unit_repeat = (play_unit_repeat + [1, 1, 1, 1])[:4]
    _vc = ['        ldx #$00', '        stx fclaim']
    for _vi in range(3):
        if _vi:
            _vc.append('        inx')
        _vc += ['        jsr voice'] * play_unit_repeat[_vi]
    voice_calls = '\n'.join(_vc) + '\n'
    filter_tail = ('        lda fcut\n        sta $d416\n'
                   '        lda shadow17\n        ora fres\n'
                   '        sta $d417\n') * play_unit_repeat[3]
    idle = [0, 0, 0]
    imask = [0, 0, 0]
    iguard = [0, 0, 0]
    idurl = [0, 0, 0]
    for v in usf.init.voices:
        if v.note is not None:
            idle[v.id - 1] = v.note
        if v.gate_mask is not None:
            imask[v.id - 1] = v.gate_mask
        if v.guard is not None:
            iguard[v.id - 1] = v.guard
        if getattr(v, 'dur_reload', None) is not None:
            idurl[v.id - 1] = v.dur_reload
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
    ovr = [0] * 160
    for inst in insts:
        for off, note, lo, hi in getattr(inst, 'offtable_freq', []) or []:
            idx = (off + note) & 0xFF
            if idx < 96:
                continue
            ph = idx - 96
            if not (6 <= ph <= 16):
                ovr[ph] = hi
            if idx >= 192:
                pl = idx - 192
                if not (6 <= pl <= 16):
                    ovr[pl] = lo

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
    igla = [ovr[_glap + x] for x in range(3)]
    iglb = [ovr[_glbp + x] for x in range(3)]

    data = []
    data.append('inote:\n' + _byt(idle))
    data.append('imask:\n' + _byt(imask))
    data.append('iguard:\n' + _byt(iguard))
    data.append('idurl:\n' + _byt(idurl))
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
    data.append('ovrwin:\n' + _byt(ovr[0:6]) + '\n'
                'sidoff:   .byt $00, $07, $0E\n'
                'fbit:     .byt $01, $02, $04\n'
                'fmask:    .byt $FE, $FD, $FB\n'
                'spd:      .dsb 1, 0\n'
                'mvol:     .dsb 1, 0\n'
                + _byt(ovr[17:160]))
    # vibdepth table (96-entry constant) + the off-table overrun window: a
    # note>95 reads `vibdepth[note]` past the table; place the captured depth at
    # pos note-96 so the read resolves to the original's value (it landed on
    # static instr-record bytes). Empty -> just the constant (byte-identical).
    _vibovr = getattr(usf, 'offtable_vibdepth', None) or []
    _vd = list(VIBDEPTH)
    if _vibovr:
        _top = max(n for n, _ in _vibovr)
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
    for name, arr in [('fdres', fdres), ('fdmode', fdmode),
                      ('fdinit', fdinit), ('fdrep', fdrep),
                      ('fdstop', fdstop)]:
        data.append(f'{name}:\n' + _byt(arr or [0]))
    data.append('fdrec:\n' + _byt(fdrec or [0] * 16))
    data.append('fdstep = fdrec+4\nfddur = fdrec+10')
    data.append('wctab:\n' + _byt(m.wctrl))
    data.append('wftab:\n' + _byt(m.wfreq))
    data.append('tunetab:\n' + '\n'.join(tune_lines))
    data.append('patlo:\n' + pat_lo)
    data.append('pathi:\n' + pat_hi)
    for lbl, (blob, loop_to) in track_blobs:
        s = f'{lbl}:' + (('\n' + _byt(blob)) if blob else '')
        if loop_to is not None:
            off = loop_to * 3
            s += f'\n        .byt $FF, <({lbl}+{off}), >({lbl}+{off})'
        data.append(s)
    for i, blob in enumerate(m.patterns):
        data.append(f'pat_{i}:\n' + _byt(blob))
    data_asm = '\n'.join(data)

    # note-init cymbal (canon onset 0) vs frame-2 cymbal (family-2 onset 1)
    _cym_burst = (
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

    # Off-table read-redirect (per-engine map -> shared generator). lo reads
    # hit state for idx 192-255; hi reads for idx 96-255.
    ws_lo_redirect = _gen_offtable_redirect(
        DMC_OFFTABLE_STATE, ORIG_FLO, 192, 'lda freqlo,y', 'ws_rd_los')
    ws_hi_redirect = _gen_offtable_redirect(
        DMC_OFFTABLE_STATE, ORIG_FHI, 96, 'lda freqhi,y', 'ws_rd_his')

    return f"""
SLIDE_PHASE = ${slide_phase:02X}
CIA_PERIOD = ${cia_period:04X}
        * = $1000
        jmp init
        jmp {play_entry}

;; ===================== init (A = subtune) =====================
init:
        pha                          ; save subtune
        lda #$00
        tax
ini_st:
        sta state0,x
        inx
        cpx #(state_end - state0)
        bne ini_st
        pla
        asl
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
        lda #SLIDE_PHASE             ; half-rate slide clock phase
        sta dualpar
        ldx #$00
ini_v:
        lda #$01
        sta vactive,x
        sta dur,x                    ; expires on the first tick
        lda inote,x                  ; idle note-state priming
        sta curnote,x
        lda imask,x                  ; idle gate-mask priming
        sta gatemask,x
        lda iguard,x                 ; post-note-guard leftover priming
        sta guard,x
        lda idurl,x                  ; duration-reload leftover priming
        sta durrel,x                 ; (orig init never writes $173E)
        lda igla,x                   ; glide-start leftover priming (off-table
        sta gla,x                    ; read tracks orig from init; glsp=0 so
        lda iglb,x                   ; fx_glide stays gated off until an arm)
        sta glb,x
        inx
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
{voice_calls}{filter_tail}        rts

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
        ldy #$00                     ; trkpl/trkph = 16-bit entry pointer
        lda ($f8),y                  ; (a 3-byte-entry track exceeds 255
        cmp #$FE                     ;  bytes past 85 entries)
        bne trk1
        lda #$00                     ; stop: voice off (state freewheels)
        sta vactive,x
        rts
trk1:
        cmp #$FF
        bne trk2
        iny
        lda ($f8),y                  ; loop: 16-bit address of the loop entry
        sta trkpl,x
        iny
        lda ($f8),y
        sta trkph,x
        jmp f_newpat
trk2:
        sec
        sbc #64                      ; entry byte 0 = transpose + 64
        sta transp,x
        iny
        iny
        lda ($f8),y                  ; entry byte 2 = orig track byte-offset
        sta otrk,x                   ; ($1726,x) of this entry's sector byte
        dey
        lda ($f8),y                  ; entry byte 1 = pattern id
        tay
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
        ; defensive: stray end marker - advance track
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

ev_rest:
        ldy #$01
        lda ($f8),y
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        lda #$02
        jsr adv
        jsr peekend
        jmp {rest_jmp}

ev_switch:
        ldy #$01
        lda ($f8),y
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        lda gatemask,x
        eor #$01
        sta gatemask,x
        lda #$02
        jsr adv
        jsr peekend
        jmp {rest_jmp}

ev_slide:                            ; glide mode 1: current -> target
        ldy #$01
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
        lda ($f8),y                  ; duration
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        lda #$04
        jsr adv
        jsr peekend
        jmp {rest_jmp}

ev_note:
        ldy #$01
        lda ($f8),y                  ; flags (1=soft 2=glide)
        sta evflags
        iny
        lda ($f8),y                  ; note
        clc
        adc transp,x
        sta curnote,x
        tay
        lda freqlo,y
        sta fbl,x
        lda freqhi,y
        sta fbh,x
        ldy #$03
        lda ($f8),y                  ; duration
        sta dur,x
        sta durrel,x                 ; live $173E shadow
        iny
        lda ($f8),y                  ; instrument slot
        sta curinst,x
        iny
        lda ($f8),y                  ; vol override
        sta volovr,x
        lda evflags
        and #$02
        beq ev_n_noglide
        ldy #$06
        lda ($f8),y                  ; glide speed
        sta glsp,x
        iny
        lda ($f8),y                  ; glide target (+ transpose)
        clc
        adc transp,x
        sta glb,x
        lda curnote,x                ; glide start = this note
        sta gla,x
        lda #$08
        jsr adv
        jmp ev_n_softq
ev_n_noglide:
        lda #$06
        jsr adv
ev_n_softq:
        lda evflags
        and #$01
        beq ev_n_hard
        jsr peekend                  ; soft (no retrigger) - effects run now
        jmp run_effects
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
        lda trkpl,x                  ; 16-bit entry pointer += 3
        clc
        adc #$03
        sta trkpl,x
        bcc pe_nc
        inc trkph,x
pe_nc:
        inc otrk,x                   ; orig $182D: track position++ at sector
        lda #$00                     ; end (points past the sector byte until
        sta path,x                   ; the next fetch re-seeds from the entry)
        rts

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
        lda shadow17
        and fmask,x
        sta shadow17
        jmp ni_vib
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
        ora mvol
        sta $d418                    ; filter note-init: mode | volume
        lda fdinit,y
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
        lda iflag,y
        sta fxf,x
{ni_vib_depth}        lda #$02
        sta guard,x                  ; gate logic off for 2 frames
{cym_ni}ni_wave:
        jmp wavestep

;; ----- running effects -----
run_effects:
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
        lda cinst,x
        asl
        asl
        asl
        clc
        adc pwphase,x
        tay
        lda irawsp,y                 ; raw speed byte -> wjmp (orig $135A
        sta wjmp                     ; STA $171F, before the nibble select)
        lda isteps,y                 ; per-phase step nibble
        clc
        adc cpwbase,x                ; + cached base (0 while idling)
        sta tmp
        sta pwstep,x                 ; live shadow of orig $175C (current PW
                                     ; step) — off-table hi reads sonify it
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
        sta tmp
        lda fddur,y
        sta tmp2
        lda fcut
        clc
        adc tmp
        sta fcut
        inc fframe
        lda fframe
        cmp tmp2
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
        cmp freqhi,y                 ; arrived when freq HI matches target
        bne fx_gl_out
        tya
        sta curnote,x
        lda freqlo,y
        sta fbl,x
        lda freqhi,y
        sta fbh,x
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
fx_dual_run:
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
        jmp pwwrite
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
        sta fbh,x
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
        lda pwh,x
        sta $d403,y
        lda wctrl,x
        and gatemask,x
        sta $d404,y
        rts

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
otrk:     .dsb 3, 0                  ; orig track byte-offset shadow (= $1726)
wnote:    .dsb 3, 0                  ; orig arp-note shadow (= $1783)
durrel:   .dsb 3, 0                  ; orig duration-reload shadow (= $173E)
ioff:     .dsb 3, 0                  ; orig instrument-offset shadow (= $174D)
state_end:
{hr_test_var}        .byt $00
"""


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


def build_dmc_sid(usf: UsfFile) -> bytes:
    asm = _sanitize_asm(compose_dmc_asm(usf))
    code = assemble(asm)
    # CIA multispeed: set the PSID speed bit for every subtune so
    # libsidplayfp drives play() via the CIA1 timer A our init programs.
    speed = ((1 << len(usf.subtunes)) - 1) if usf.params.fields.get(
        'cia_period') else 0
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        speed=speed, title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=FLAGS_PAL_6581)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code
