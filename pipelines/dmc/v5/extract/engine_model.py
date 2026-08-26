"""DMC V5 binary -> structured model.

Lifts a V5 packed module (family-3/5 player) into a V5Model: freq tables,
8-byte instruments, the three programmable 2-byte tables (wave/pulse/
filter), per-voice orderlists, and sector event streams. Table bases are
read by dataflow from the operand sites in DMCV5Config; region sizes are
derived from the address deltas (V4-style). See pipelines/dmc/v5/
disassembly.s for the byte maps this decoder follows.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class V5Instrument:
    id: int
    ad: int
    sr: int
    wave_ptr: int      # entry index into the wave table
    pulse_ptr: int     # entry index into the pulse table (0 = no restart)
    filter_ptr: int    # entry index into the filter table (0 = no restart)
    vib_delay: int
    vib_speed: int
    vib_width: int     # & $07
    # Off-table arpeggio frequencies (the ML-musical replacement for the
    # freq_overrun blob): per (wave step, effective note) the explicit
    # (freq_lo, freq_hi) the step produces when (offset+note) runs past the
    # 96-entry freq table into engine state. List of (step, note, lo, hi).
    offtable_freq: list = field(default_factory=list)


@dataclass
class V5Subtune:
    """One subtune's orderlist record: 3 per-voice orderlists + speed + vol.
    The data tables (sectors/instruments/freq/wave/pulse/filter) are shared
    across subtunes at the V5Model level."""
    orderlists: list = field(default_factory=list)     # 3 x list[event]
    orderlist_raw: list = field(default_factory=list)  # 3 x bytes (song data)
    speed: int = 2
    master_vol: int = 0x0F


@dataclass
class V5Model:
    freq_lo: list = field(default_factory=list)     # 96
    freq_hi: list = field(default_factory=list)      # 96
    # (off-table freq reads ride per-instrument `V5Instrument.offtable_freq`;
    # the old contiguous freq_overrun window was removed 2026-06-21.)
    instruments: list = field(default_factory=list)  # list[V5Instrument]
    # An off-table freq read SONIFIES the live pulse/filter position (the
    # engine's pulsepos/filterpos state block is reachable from the freq
    # tables). The captured static byte is only a snapshot of a moving value.
    # Before the paged-pool rebuild ships such a member, the read is MEASURED
    # at its actual read moments (ledger C11 event-driven doctrine,
    # `measure_live_window_reads`): never-fires -> inert, constant -> serve
    # the measured value, inconstant -> refuse (C8: don't approximate).
    offtable_live_pos: bool = False
    offtable_live_reads: set = field(default_factory=set)  # {(kind, idx)}
    wave: list = field(default_factory=list)         # list[(ctrl, freq)]
    pulse: list = field(default_factory=list)        # list[(lo, hi)]
    filter: list = field(default_factory=list)       # list[(lo, hi)]
    speed: int = 2                                   # subtune 0 (mirror)
    master_vol: int = 0x0F                            # subtune 0 (mirror)
    orderlists: list = field(default_factory=list)   # subtune 0: 3 x list[event]
    sectors: list = field(default_factory=list)      # list[list[event]] (SHARED)
    orderlist_raw: list = field(default_factory=list)  # subtune 0: 3 x bytes
    # per-subtune orderlist records (3 track ptrs + speed + master vol each).
    # The init indexes ordrec by song# (`ASL*3; TAY`); sectors/instruments/
    # freq/wave/pulse/filter tables are SHARED across subtunes. Single-subtune
    # members have one entry (song# always 0 -> Y=0).
    subtunes: list = field(default_factory=list)     # list[V5Subtune]
    sector_raw: list = field(default_factory=list)     # list[bytes]
    # file-image leftovers the player init does NOT clear (written to the
    # SID before the filter table overwrites them — V4 $1018-shadow analog)
    lo_filtmode: int = 0    # $1015 -> $D418 (mode nibble)
    lo_fchi: int = 0        # $1016 -> $D416 (cutoff hi)
    lo_fclo: int = 0        # $1017 -> $D415 (cutoff lo)
    # $1013 speed-counter: init sets $1012 (reload) but NEVER clears $1013,
    # so the speed counter starts at a file-image leftover. This sets the
    # song's startup PHASE — how many leftover-effects frames play before the
    # first note fetches (tick = speed==spdctr). Katusha's leftover is $00
    # (immediate first tick); others are non-zero (a 1+ frame lead-in).
    lo_spdctr: int = 0      # $1013 speed-counter startup phase
    # $100F,x per-voice current NOTE — also in the uncleared $1006-$103F gap.
    # Only OBSERVABLE when lo_spdctr delays the first tick: the lead-in
    # effects frame(s) run wave_step on this leftover note (freq-table lookup)
    # before the first fetch overwrites it. With lo_spdctr=0 it never matters.
    lo_notes: list = field(default_factory=lambda: [0, 0, 0])  # $100F-$1011
    # $101C fade fractional accumulator — also uncleared. Init clears the fade
    # SPEEDS ($1018/$1019) but not this sub-integer phase, so a tune whose
    # first FD+/FD- runs starts the master-vol ramp from this leftover phase
    # (off-by-one in $D418 vol otherwise). Unread until a fade is active.
    lo_mvolfrac: int = 0    # $101C fade fractional phase
    # CIA multispeed timer A latch (0 = VBI). A wrapper member with the PSID
    # speed bit runs play() off the CIA1 timer; the rate is measured from the
    # ground-truth writelog in the factory (py65 can't run the wrapper init).
    cia_period: int = 0
    # ledger C18 per-call phase schedule ('P_F123_...') for a WRAPPER member:
    # the play vector runs the full play only every Nth call and an
    # effects-only pass on the others. '' = no wrapper. Observed by the
    # factory, never parsed from the wrapper's code.
    play_phases: str = ''
    # ---- PLAYER-MECHANISM KNOBS (Principle §8) ----------------------
    # These eleven fields replace a single `family4` flag that named the
    # ORIGINATING PLAYER and gated ~190 lines of composer emitters. That is
    # §8's shape verbatim — "the composer identifies the originating engine
    # from USF content and dispatches to that engine's implementation" — and
    # it broke §8's own constraint that such a tag is read by the DISPATCHER,
    # never by an emitter. Each knob now names the MECHANISM it changes, so
    # the composer emits from named behaviour rather than from a player's
    # identity, and any future player exhibiting one of these can set it
    # alone. The Jupiter41 variant simply sets all eleven.
    play_skip_init: int = 2       # initial play() calls that do nothing
    noteon_skip_freq_clear: bool = False  # note-on writes SR/AD/CTRL only
    dur_ctr_init: int = 1         # per-voice duration-counter seed
    wave_speed_from_instr: bool = False   # wave-step period = instr byte6>>4
    volovr_ad_zero: bool = False  # vol-override note-on forces AD=$00
    pulse_ctr_8bit: bool = False  # 8-bit pulse step counter (not 16-bit)
    noteload_no_d418: bool = False        # note-load does not emit $D418
    filter_v3_only: bool = False  # filter init gated to voice 3
    filter_needs_cmd: bool = False        # filter sweep waits for the 1st cmd
    filter_d416_only: bool = False        # $D416 (+base) only, never $D415
    d418_skip_vib_reversal: bool = False  # skip $D418 on a vib-reversal frame
    wave_step_carry: bool = False # wave-step carry propagates into freq hi
    vib_from_instr_bytes: bool = False    # vib delay/period from instr b5/b6
    filter_prog_8bit: bool = False        # filter program is 8-bit (add,count)
    # the Jupiter41 V5 variant (play +$95): same data, different player. The
    # composer emits the family-4 mechanics (2-phase $1016 timing, $D416-only
    # 8-bit filter + $D418 mode, $1012 leadin-curnote leftover). Phase C.
    family4: bool = False
    f4_idle_notes: list = field(default_factory=lambda: [0, 0, 0])  # $1012-$1014
    f4_filtmode: int = 0    # $1018 (filter MODE nibble from $F9) -> $D418
    f4_fcinit: int = 0      # $1019 file-image (initial filter cutoff, swept by the
                            # default filter program from filterpos 0) -> $D416 base
    title: str = ''
    author: str = ''
    released: str = ''
    clock: str = 'PAL'      # PSID header clock flag (audio metadata)
    sid_model: int = 6581   # PSID header SID model (write-log-blind; audible)


def _load(path: str, post_init_sub: 'int | None' = None):
    """File image as a 64K map; `post_init_sub` swaps in the RAM left by that
    subtune's init (snapshot at the landing) for a RELOCATED compilation
    sub-player (ledger C31 + C26) — mirrors the V4 extract's view."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', '..', 'tools'))
    from seed_disassembly import parse_psid
    s = parse_psid(path)
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    if post_init_sub is not None:
        from pipelines.dmc.v4.extract.engine_model import _postinit_window
        post = _postinit_window(s, 0, 0x10000, sub=post_init_sub,
                                stop_at_player=True)
        if post is not None:
            mem = bytearray(post)
    return mem, s


def _rd16(mem, a):
    return mem[a] | (mem[a + 1] << 8)


# ----- orderlist (track) decode: $FF loop / $FE end / $FD,$FC transpose --
# THE TRACK POSITION IS A BYTE. disassembly.s track_fetch ($10F2):
#   $10FC  LDY $17d5,x        ; per-voice track position -- ONE BYTE
#   $10FF  LDA ($f8),y
# and every advance is `INC $17d5,x`, so the position wraps $FF -> $00. A track
# is therefore at most a 256-byte window and CANNOT run on past it: one with no
# $FF/$FE in that window cycles forever rather than "never ending". The old
# 512-entry linear guard walked straight past the wrap and raised on data the
# player reads perfectly well (Goto80/Hairy's three tracks are exactly one page
# each). Revisiting a position IS the wrap, so it is recorded as a loop to that
# byte offset -- which is what the player does.
def _decode_orderlist(mem, ptr: int):
    out = []
    pos = 0
    seen = set()
    while pos not in seen:
        seen.add(pos)
        b = mem[(ptr + pos) & 0xFFFF]
        if b == 0xFF:
            out.append(('loop', mem[(ptr + pos + 1) & 0xFFFF]))
            return out, bytes(mem[ptr:ptr + pos + 2])
        if b == 0xFE:
            out.append(('end',))
            return out, bytes(mem[ptr:ptr + pos + 1])
        if b == 0xFD:
            out.append(('transpose', mem[(ptr + pos + 1) & 0xFFFF]))
            pos = (pos + 2) & 0xFF
            continue
        if b == 0xFC:
            out.append(('transpose', (-mem[(ptr + pos + 1) & 0xFFFF]) & 0xFF))
            pos = (pos + 2) & 0xFF
            continue
        out.append(('sector', b))       # ANY byte < $FC -- $10FF's BPL sends
        pos = (pos + 1) & 0xFF          # <$80 to sector_ptr, and $80-$FB falls
                                        # through the CMP chain to the same place
    # The position wrapped onto a byte already dispatched: an ENDLESS track.
    # Musically this is a loop to that byte offset, and `to_usf._orderlist`
    # treats it as one — but it is tagged distinctly because `extract` needs to
    # tell a track that STATES its loop from one that merely runs out of window:
    # the latter is what a garbage tune-table record looks like.
    out.append(('wrap', pos))
    return out, bytes(mem[(ptr + k) & 0xFFFF] for k in range(256))


# ----- sector decode: notes (<$80) + commands ($F1-$FE) + $FF end -------
# (byte counts per pipelines/dmc/v5/disassembly.s sector dispatch)
_CMD = {
    0xF1: ('srr', 2), 0xF2: ('adr', 2), 0xF3: ('vol', 2),
    0xF4: ('gate_tie', 1), 0xF5: ('gate_toggle', 1),
    0xF6: ('fade_out', 2), 0xF7: ('fade_in', 2),
    0xF8: ('frq', 2), 0xF9: ('flt', 2),
    0xFA: ('slide', 3), 0xFB: ('glide', 4),
    0xFC: ('snd', 2), 0xFD: ('dur', 2), 0xFE: ('gate', 1),
    # family-4-only commands (never present in family-3/V5 sector data, so
    # adding them to the shared map is inert for those families):
    #   $EF nn -> per-voice freq-lo BIAS ($1842,x), added in the wave-step.
    #   $F0 nn -> per-note vib width (nn&7) + wave/freq re-load (nn>>4 = count).
    0xEF: ('freq_bias', 2), 0xF0: ('f0', 2),
}


# Two facts read off disassembly.s sector_dispatch ($1158), both of which the
# first version of this walk got wrong -- it refused data the player consumes
# without complaint (14 members died in the batch as `error`, 2026-08-25):
#
#  * AN UNRECOGNISED >=$80 BYTE IS A 1-BYTE NO-OP. The CMP chain ends at
#      $12A2  CMP #$F6 / BNE $1289
#      $1289  INC $17d8,x / JMP $1158     <- advance ONE byte, re-dispatch
#    so a byte matching no command is skipped, emits no write and consumes no
#    duration. Dropping it from our event list is therefore lossless.
#  * THE SECTOR POSITION IS A BYTE ($1158 LDY $17d8,x; advances are
#    `INC $17d8,x`), so it wraps $FF -> $00. A sector is at most a 256-byte
#    window; one with no $FF inside that window CYCLES. Walking `pos` linearly
#    past 256 read bytes the player can never reach -- finding phantom
#    terminators beyond offset 255, and running off the end of memory
#    (IndexError) on the last sector of a file.
#
# ⚠ KNOWN LIMIT: a cycling sector is decoded to the events of one lap, and
# `from_usf._encode_sector` terminates every sector with $FF -- so the rebuild
# ENDS where the original would loop. The two agree until the lap runs out
# (256 steps; every carrier measured so far is a song-end "note then endless
# gate-offs" tail that no verify window reaches). Representing the lap itself
# is ledger C32's endless-tail question, deliberately not answered here.
# $FF ENDS A SECTOR ONLY AS A LOOKAHEAD, NEVER AS A DISPATCHED BYTE. The
# dispatch CMP chain ($1162..$12A2) has no $FF case at all; the single $FF test
# in the player is the peek `step_commit` takes immediately after committing a
# ROW ($118C, and note_on's own copy at $1314):
#
#     INC $17d8,x / LDY $17d8,x / LDA ($f8),y   ; peek row_start + row_width
#     CMP #$FF / BNE ...                        ; the only $FF test
#     LDA #$00 / STA $17d8,x                    ; sector pos = 0
#     STA $17e7,x / STA $17ea,x                 ; clear vol override + gate flag
#     INC $17d5,x                               ; ADVANCE THE TRACK
#
# So a sector ending `... note, $FD nn, $FF` does NOT end: the trailing command
# executes, the $FF falls through to $1289's 1-byte skip, and the voice RUNS ON
# into the bytes that follow. Reading $FF as end wherever it appeared made those
# sectors look like they terminated with orphan commands, which is what
# `trailing_sector_cmds` was refusing.
#
# Rows (the events that reach step_commit) are note, $FE gate, $F4 gate_tie,
# $FA slide and $FB glide; the widths in _CMD are exactly the peek offsets,
# because cmd_FA pre-advances $17d8 by 2 and note_on advances by 1 after the
# glide handler's 3.
#
# Exposure measured before landing: of 2,031 members exactly 3 have a
# REFERENCED run-on sector and all 3 are already `unsupported`; 1 partial has a
# referenced bare-$FF (empty) sector, which likewise runs on.
_ROW_EVENTS = {'note', 'gate', 'gate_tie', 'slide', 'glide'}


def _decode_sector(mem, ptr: int):
    out = []
    pos = 0
    seen = set()
    while pos not in seen:
        seen.add(pos)
        b = mem[(ptr + pos) & 0xFFFF]
        if b < 0x80:
            name, n = 'note', 1
            out.append(('note', b))
        elif b in _CMD:
            name, n = _CMD[b]
            args = tuple(mem[(ptr + pos + 1 + k) & 0xFFFF] for k in range(n - 1))
            out.append((name,) + args)
        else:
            # no command matched -> $1289's 1-byte no-op. An $FF read HERE is
            # just such a byte: it is not a terminator unless peeked after a row.
            pos = (pos + 1) & 0xFF
            continue
        pos = (pos + n) & 0xFF
        if name in _ROW_EVENTS and mem[(ptr + pos) & 0xFFFF] == 0xFF:
            out.append(('end',))            # the lookahead terminator
            return out, bytes(mem[(ptr + k) & 0xFFFF] for k in range(pos + 1))
    # the position wrapped onto a byte already dispatched: an endless sector
    return out, bytes(mem[(ptr + k) & 0xFFFF] for k in range(256))


def extract(cfg, hvsc_root: str = 'hvsc85') -> V5Model:
    from pipelines.dmc.v4.extract.engine_model import (_hdr_clock,
                                                       _hdr_sid_model)
    mem, s = _load(os.path.join(hvsc_root, cfg.sid_path),
                   getattr(cfg, 'post_init_sub', None))

    a_order = _rd16(mem, cfg.op_orderlist)
    a_secp_lo = _rd16(mem, cfg.op_secp_lo)
    a_secp_hi = _rd16(mem, cfg.op_secp_hi)
    a_instr = _rd16(mem, cfg.op_instr)
    a_flo = _rd16(mem, cfg.op_freq_lo)
    a_fhi = _rd16(mem, cfg.op_freq_hi)
    a_wc = _rd16(mem, cfg.op_wave_ctrl)
    a_wf = _rd16(mem, cfg.op_wave_freq)
    a_pl = _rd16(mem, cfg.op_pulse_lo)
    a_ph = _rd16(mem, cfg.op_pulse_hi)
    a_fl = _rd16(mem, cfg.op_filter_lo)
    a_fh = _rd16(mem, cfg.op_filter_hi)
    end = s['load'] + len(s['payload'])

    # THE OPERANDS ARE NOT TABLE ADDRESSES AT ALL. On a couple of members the
    # detector's play-body signature matches but the data-table operands point
    # nowhere near the file image (Ed/We_Were_All_Kids and Piirainen_Antti/
    # Left_Ear_Bleedin_Ear_Left: 9 of 12 outside, all three track pointers read
    # $0000). Decoding proceeds from garbage and the member dies somewhere
    # arbitrary downstream — it reported as a crash rather than as "we can't
    # read this one", which is worse than useless in a residue census.
    #
    # This is ledger C26's shape (init unpacks the song into RAM, so the image
    # holds no tables) but only PARTLY: C26 requires EVERY operand outside the
    # image before it will read from post-init RAM, and mixed members stay
    # refused. So refuse — cleanly, and named — rather than guess. A member with
    # `post_init_sub` is already being read from post-init RAM (C26/C31), where
    # the file-image bounds do not apply, so it is exempt.
    if getattr(cfg, 'post_init_sub', None) is None:
        load = s['load']
        tables = (a_order, a_secp_lo, a_secp_hi, a_instr, a_flo, a_fhi,
                  a_wc, a_wf, a_pl, a_ph, a_fl, a_fh)
        outside = sum(1 for a in tables if not load <= a < end)
        if outside >= 6 and not load <= a_order < end:
            from pipelines.dmc.v5.factory import DMCV5Unsupported
            raise DMCV5Unsupported(
                f'data_tables_off_image: {outside}/12 table operands outside '
                f'${load:04X}-${end:04X} (orderlist ${a_order:04X})')

    # region sizes from address deltas (the packer lays tables contiguously:
    # instr | wave_ctrl | wave_freq | pulse_lo | pulse_hi | filter_lo |
    # filter_hi | <end>)
    # The wave table has the same off-table case as pulse/filter: wavepos is a
    # byte, so a program longer than the ctrl array runs past a_wf-a_wc into the
    # overlapping freq/pulse arrays, and its $90 loop marker can live off-table
    # (e.g. Compotune wave_ptr 68: no $90 within a_wf-a_wc=71, found at 256).
    # _slice_wave reads only up to len(wave) and bounds via the $90 + a 256 guard.
    n_wave = min(256, 0x10000 - a_wc, 0x10000 - a_wf)
    # Like the filter table below, the pulse program is NOT bounded by the
    # lo/hi-array delta: pulsepos is a byte, and an instrument whose program is
    # longer than the lo array runs pulse_run PAST it, reading the overlapping
    # hi/filter arrays + bytes after as further (step,count) phases (the ramp
    # lives off-table — e.g. Lectro_64 inst pulse_ptr 17 starts at $7777 then
    # ramps +8 from pos 18, which is past a_ph-a_pl=18). Read up to 256 entries;
    # _capture_env bounds the reachable program per ptr (loop/terminal/reach).
    n_pulse = min(256, 0x10000 - a_pl, 0x10000 - a_ph)
    # The filter table is the LAST data region, so its lo/hi-array delta does
    # NOT bound the program: tiny tables (e.g. 2 entries) whose instruments all
    # use ptr 1 run filter_run PAST the array boundary, reading the overlapping
    # lo/hi arrays + the bytes after them as further (step,count) phases (the
    # ramp lives off-table). filterpos is a byte, so read up to 256 entries
    # (capped at the memory top); reads past the payload are 0 (siddump
    # zero-fills RAM identically), and _capture_env bounds reachability per ptr.
    n_filter = min(256, 0x10000 - a_fl, 0x10000 - a_fh)
    n_instr = (a_wc - a_instr) // 8
    # The lo/hi ADDRESS DELTA IS NOT THE SECTOR COUNT. Both tables are reached
    # through operands the packer relocates independently (sector_ptr $114D:
    # `LDA $196e,y` / `LDA $1972,y` — four bytes apart in the reference player),
    # and the engine indexes both with an unchecked byte, so the delta says
    # nothing about how many sectors a song has. Used as a bound it both
    # OVERSTATES (tail entries decoded as sectors) and UNDERSTATES (an orderlist
    # referencing sector 32 with a delta of 26 — the KeyError the batch reported).
    # Bound by REACHABILITY instead, per ledger C2: keep the delta as the
    # baseline so every member whose songs stay inside it is byte-identical, and
    # extend to cover whatever the tracks actually reference. A byte index caps
    # the whole thing at 256. Absurd deltas (negative, or tens of thousands) come
    # from members whose table operands are not table addresses at all — those
    # are refused below, before this matters.
    n_sectors = min(256, max(0, a_secp_hi - a_secp_lo))

    m = V5Model(
        freq_lo=[mem[a_flo + i] for i in range(96)],
        freq_hi=[mem[a_fhi + i] for i in range(96)],
        speed=mem[a_order + 6], master_vol=mem[a_order + 7],
        lo_filtmode=mem[cfg.base + 0x15], lo_fchi=mem[cfg.base + 0x16],
        lo_fclo=mem[cfg.base + 0x17], lo_spdctr=mem[cfg.base + 0x13],
        lo_notes=[mem[cfg.base + 0x0F + i] for i in range(3)],
        lo_mvolfrac=mem[cfg.base + 0x1C],
        cia_period=int(getattr(cfg, 'cia_period', 0)) & 0xFFFF,
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
        clock=_hdr_clock(os.path.join(hvsc_root, cfg.sid_path)),
        sid_model=_hdr_sid_model(os.path.join(hvsc_root, cfg.sid_path)),
    )
    for i in range(n_instr):
        b = [mem[a_instr + i * 8 + k] for k in range(8)]
        m.instruments.append(V5Instrument(
            id=i, ad=b[0], sr=b[1], wave_ptr=b[2], pulse_ptr=b[3],
            filter_ptr=b[4], vib_delay=b[5], vib_speed=b[6],
            vib_width=b[7] & 0x07))
    m.wave = [(mem[a_wc + i], mem[a_wf + i]) for i in range(n_wave)]
    m.pulse = [(mem[a_pl + i], mem[a_ph + i]) for i in range(n_pulse)]
    m.filter = [(mem[a_fl + i], mem[a_fh + i]) for i in range(n_filter)]

    # per-subtune orderlist records: record N at a_order + N*8 (3 track
    # pointers + speed + master vol). The data tables above are shared.
    # A COMPILATION sub-player (ledger C31) owns fewer songs than the FILE
    # header declares — cfg.n_songs bounds the record read to what this
    # player actually carries (past-end records are another player's data).
    n_sub = max(1, getattr(cfg, 'n_songs', None) or s.get('songs', 1))
    for sub in range(n_sub):
        rec = a_order + sub * 8
        st = V5Subtune(speed=mem[rec + 6], master_vol=mem[rec + 7])
        try:
            for v in range(3):
                tp = _rd16(mem, rec + v * 2)
                ev, raw = _decode_orderlist(mem, tp)
                st.orderlists.append(ev)
                st.orderlist_raw.append(raw)
        except RuntimeError:
            # THE PSID HEADER OVERSTATES THE SONG COUNT. Past the last real
            # record the read runs into whatever follows the table — usually
            # orderlist bytes — and decodes as garbage pointers into low RAM
            # (Bayliss/Xmas_Crazy declares 6 songs, has 5: record 5 reads
            # `FC 08 FD 06 48 FE 43 FE` = track commands, giving track
            # pointers $08FC/$06FD/$FE48 whose "orderlist" never terminates).
            # The engine would play that record as noise, so it is not a song
            # and there is nothing musical to represent (C7).
            #
            # Stop at the first record that will not decode and keep the songs
            # that do. Only widening: a member whose records ALL decode is
            # untouched, so every currently-building member is byte-identical.
            # A failure at record 0 is a genuinely unreadable member and still
            # raises.
            if sub == 0:
                raise
            break
        # ⚠ THAT GUARD USED TO FIRE VIA THE RAISE ABOVE. `_decode_orderlist` no
        # longer raises on a track that never terminates — the player's position
        # is a byte, so such a track simply cycles — which silently disabled the
        # overstated-song-count protection: a garbage record's three cycling
        # "tracks" were accepted as a real song, and the sector numbers scraped
        # out of them dragged in junk patterns (Bayliss/Guns_n_Ghosts: 12 real
        # sectors became 67, referencing index 246 against a 43-entry table).
        # The condition the raise stood for is exactly "the track never states an
        # end", which is now the 'wrap' tag, so test for it directly. Record 0 is
        # exempt: a genuinely endless track there is the member's real music
        # (Goto80/Hairy's three tracks are each exactly one page).
        if sub and any(ev and ev[-1][0] == 'wrap' for ev in st.orderlists):
            break
        m.subtunes.append(st)
    # mirror subtune 0 onto the top-level fields (single-subtune readers)
    m.orderlists = m.subtunes[0].orderlists
    m.orderlist_raw = m.subtunes[0].orderlist_raw
    m.speed = m.subtunes[0].speed
    m.master_vol = m.subtunes[0].master_vol
    # A COMPILATION sub-player's sector-pointer tail can hold UN-RELOCATED
    # leftovers for sectors no track of its songs references (the re-linker
    # only patched the live entries — Super_Tau-Zeta's $B400 player: sectors
    # 14+ still point at canon $1Cxx, out of image). Tolerate a decode
    # failure ONLY for an unreferenced sector (empty placeholder keeps the
    # indices aligned); a referenced sector must still decode or the member
    # is refused. Members whose sectors all decode are byte-unchanged.
    referenced = {b for st in m.subtunes for ol in st.orderlists
                  for ev in ol if ev[0] == 'sector' for b in [ev[1]]}
    # extend past the delta to whatever the tracks reach (see n_sectors above)
    if referenced:
        n_sectors = min(256, max(n_sectors, max(referenced) + 1))
    for i in range(n_sectors):
        sp = (mem[(a_secp_lo + i) & 0xFFFF]
              | (mem[(a_secp_hi + i) & 0xFFFF] << 8))
        try:
            ev, raw = _decode_sector(mem, sp)
        except RuntimeError:
            if i in referenced:
                raise
            ev, raw = [], b''
        # KEEP THE PLACEHOLDER VALVE ALIVE. The tolerance above was written for
        # a decoder that RAISED on junk; now that nothing raises, an unplayed
        # tail entry silently becomes a real pattern instead — and a garbage one
        # ending in state commands trips `trailing_sector_cmds`, which took a
        # FULL member (Kordiaukis/Rotting_Christ, unreferenced sector 16) down
        # with it. The signal a sector is junk rather than music is that it never
        # reaches an $FF: the player would cycle its 256-byte window forever.
        # Combined with "no track plays it", that is the same set the old decoder
        # refused, so this restores its behaviour exactly. A REFERENCED sector is
        # kept however it decodes — that one is audible.
        if i not in referenced and not (ev and ev[-1][0] == 'end'):
            ev, raw = [], b''
        m.sectors.append(ev)
        m.sector_raw.append(raw)
    # family-4 (Jupiter41): capture the player-specific leftovers the composer
    # needs (Phase C). curnote $1012-$1014 is NOT cleared by init → the leadin
    # freq before the first note; $1018 = the filter MODE nibble → $D418.
    m.play_phases = str(getattr(cfg, 'play_phases', '') or '')
    if getattr(cfg, 'family4', False):
        m.family4 = True
        d = cfg.base - 0x1000
        # ---- the Jupiter41 variant, expressed as MECHANISM knobs (§8) ----
        # Detection stays here in the EXTRACT (the dispatcher's job); what
        # crosses into the USF and reaches the composer is the list of
        # behaviours, never the player's name.
        m.play_skip_init = 0            # its play has no $1842 skip counter
        m.noteon_skip_freq_clear = True
        m.dur_ctr_init = 2
        m.wave_speed_from_instr = True
        m.volovr_ad_zero = True
        m.pulse_ctr_8bit = True
        m.noteload_no_d418 = True
        m.filter_v3_only = True
        m.filter_needs_cmd = True
        m.filter_d416_only = True
        m.d418_skip_vib_reversal = True
        m.wave_step_carry = True
        m.vib_from_instr_bytes = True
        m.filter_prog_8bit = True
        # Its leftovers live at DIFFERENT addresses, but they mean the same
        # things — so read them into the CANONICAL fields and let the composer
        # have exactly one source for each. (This alone removed three
        # `if family4` branches from the composer.)
        m.f4_idle_notes = [mem[0x1012 + d + v] for v in range(3)]
        m.f4_filtmode = mem[0x1018 + d]
        m.f4_fcinit = mem[0x1019 + d]
        m.lo_notes = list(m.f4_idle_notes)
        m.lo_filtmode = m.f4_filtmode
        m.lo_fchi = m.f4_fcinit
        # STARTUP PHASE. family-4's play ($1095) does NOT use family-3's speed
        # counter at $1013 — it toggles `DEC $1016 / BMI` between MAIN (effects
        # only) and TICK (advance duration, fetch, then fall into MAIN). $1016
        # is a FILE-IMAGE LEFTOVER the init never clears, so it sets how many
        # idle plays precede the first note-on:
        #     $1016 = 0  ->  play1 is a TICK   (dec -> $FF, BMI taken)
        #     $1016 = 1  ->  play1 is MAIN     (dec -> $00), TICK from play2
        #
        # Reading $1013 here was wrong twice over: in family-4 that address is
        # V2's CURNOTE, so it produced a bogus multi-frame startup delay (fixed
        # in C-3 by zeroing it) — but zero is only right for the $1016=0 half of
        # the corpus. The 2026-07-01 round already found the mechanism and
        # recorded that seeding LEFT_SPDCTR from mem[base+$16] "did NOT fix it";
        # what it was missing is that the composer ALSO emits family-3's
        # `playskip = 2`, which family-4's play has no counterpart for.
        #
        # The composer's counter reproduces the toggle exactly at speed 1:
        #   seed 1 -> play1 `dec`->0, no reload, speed(1) != spdctr(0) -> MAIN
        #             play2 `dec`->$FF, reload to speed -> spdctr == speed -> TICK
        # which is the orig's MAIN/TICK alternation with the same phase.
        # (`lo_notes` / `lo_filtmode` / `lo_fchi` were canonicalised from the
        # family-4 addresses above — they used to be left zeroed here because
        # the COMPOSER picked the f4_* fields instead. That selection was one
        # of the §8 branches; one source per quantity replaces it.)
        m.lo_spdctr = mem[0x1016 + d]
        m.lo_mvolfrac = 0
    # Off-table arpeggio frequencies, per instrument (the off-table-read form;
    # see _assign_offtable_freq).
    #
    # ⚠ THIS MUST RUN AFTER the leftover block above. Its lead-in capture reads
    # `m.lo_notes`, and family-4 keeps those notes at $1012-$1014 rather than
    # the canonical $100F-$1011 — so while this call sat BEFORE the override it
    # saw the canon-offset bytes (for Pride: $01/$02/$04 instead of
    # $45/$30/$3C). Those decoy notes index INSIDE the 96-entry table, so the
    # `idx > 95` test never fired and every family-4 lead-in off-table read was
    # silently dropped: the composer then had no explicit frequency to place at
    # that index and the rebuild played $00 where the orig played the byte.
    # Canon members are unaffected (their `lo_notes` is identical either side of
    # the block), so moving the call is byte-identical for family-3/5.
    # Live-position window (backlog item 19 census): the per-voice pulsepos +
    # global filterpos of the member's own player — family-3/5 keeps them at
    # base+$7F6..$7F9, family-4 at base+$800..$803 ($1800,x / $1803 in the
    # $1000-based disassembly). Both are state-block addresses, fixed relative
    # to the player base regardless of how the data tables were packed.
    _d = cfg.base - 0x1000
    _live = ((0x1800 + _d, 0x1804 + _d)
             if getattr(cfg, 'family4', False)
             else (cfg.base + 0x7F6, cfg.base + 0x7FA))
    _assign_offtable_freq(mem, a_flo, a_fhi, m,
                          clear_range=(_init_clear_range(mem, cfg.base)
                                       if getattr(cfg, 'family4', False)
                                       else None),
                          live_range=_live)
    return m


# family-4 freq-table read sites (canon $1000-based PCs of the `LDA/CMP
# $1719,y` / `$1779,y` instructions — every consumer of the freq tables, per
# family4/disassembly.s; ledger C11's "ALL read sites" rule): wave-step,
# note-init first step, note-fetch base reload, vib-step setup, glide-arrival
# compares. Relocated by (base - $1000) at measurement time.
_F4_FREQ_READ_SITES = {'lo': (0x1685, 0x1452),
                       'hi': (0x168E, 0x1458, 0x13B8, 0x118E, 0x150E, 0x153B)}


def measure_live_window_reads(cfg, m, hvsc_root: str):
    """GROUND-TRUTH read-moment census of the off-table reads that land on the
    live pulsepos/filterpos block (`m.offtable_live_reads`).

    The reach model enumerates (instrument x played-note x transpose), which
    OVER-approximates: a live-window record may never actually be read, or be
    read only at moments when the live byte holds one constant value (ledger
    C11's event-driven doctrine — measure stability AT THE READ, not over a
    time window; the 2026-08-26 census: of 4 refused members, 1 never reads,
    1 reads a constant, only 2 are genuinely live).

    Watches every family-4 freq-table read site over each subtune's full
    verify window via `siddump --pc-watch ... --pc-watch-abs` (libsidplayfp
    ground truth; execution-discriminated per C36) and returns
    `(overrides, inconstant)`: `overrides` maps (kind, idx) -> the single
    value every read observed; `inconstant` holds (kind, idx) keys that
    observed >= 2 values (no static byte can serve them). A key in neither is
    never read — its captured value is inert. Returns None when the member's
    player has no site map (only family-4 carriers exist today)."""
    import re
    import subprocess
    if not getattr(cfg, 'family4', False) or not m.offtable_live_reads:
        return None
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    d = cfg.base - 0x1000
    sites = {}                                   # relocated pc-hex -> kind
    for kind, pcs in _F4_FREQ_READ_SITES.items():
        for pc in pcs:
            sites[f'{(pc + d) & 0xFFFF:04X}'] = kind
    live_idx = {kind: {i for k, i in m.offtable_live_reads if k == kind}
                for kind in ('lo', 'hi')}
    win_lo, win_hi = 0x1800 + d, 0x1804 + d      # pulsepos x3 + filterpos
    sid = os.path.join(hvsc_root, cfg.sid_path)
    try:
        from seed_disassembly import parse_psid
        n_songs = parse_psid(sid)['songs']
    except Exception:
        n_songs = 1
    try:
        from src.songlengths import load_database, get_durations
        db = load_database(os.path.join(hvsc_root, 'DOCUMENTS',
                                        'Songlengths.md5'))
        durs = get_durations(sid, db)
    except Exception:
        durs = None
    seen: dict = {}                              # (kind, idx) -> set(values)
    ev_re = re.compile(r'PW:([0-9A-F]+):[0-9A-F]+:[0-9A-F]+:([0-9A-F]+):'
                       r'\d+:[^:|]*:([0-9A-F]+)')
    for sub in range(n_songs):
        dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1 + 2
        out = subprocess.run(
            [os.path.join(root, 'tools', 'siddump'), sid,
             '--subtune', str(sub + 1),         # siddump subtunes are 1-BASED
             '--pc-watch', ','.join(sites), '0-0',
             '--pc-watch-abs', f'{win_lo:04X}-{win_hi:04X}',
             '--duration', str(int(dur))],
            capture_output=True, text=True, timeout=1800).stdout
        for pc, y, absw in ev_re.findall(out):
            kind = sites.get(pc)
            if kind is None:
                continue
            idx = int(y, 16)
            if idx not in live_idx[kind]:
                continue
            a = (0x1719 if kind == 'lo' else 0x1779) + d
            src = (a + idx) & 0xFFFF
            off = src - win_lo
            w = [absw[i:i + 2] for i in range(0, len(absw), 2)]
            if 0 <= off < len(w):
                seen.setdefault((kind, idx), set()).add(int(w[off], 16))
    overrides = {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}
    inconstant = {k for k, v in seen.items() if len(v) > 1}
    return overrides, inconstant


def _slice_wave(wave: list, start: int):
    """Return (ctrl, freq, loop) for the wave program at `start`. `loop` is the
    relative index the $90 marker jumps back to. (Shared with to_usf — kept here
    so the extract's step indexing matches the USF's emitted wave_freq.)"""
    n = len(wave)
    ctrl, freq = [], []
    # EXACT WALK SIMULATION (ledger C2: simulate and emit the resolved
    # sequence). Two engine facts drive it, both from disassembly.s:
    #   * wave_init ($137F) reads ctrl[start] with NO $90 check — an
    #     instrument whose wave_ptr sits ON its own marker plays the raw
    #     ($90, freq) bytes as its first step, then walks FORWARD from
    #     start+1 (it never takes that marker's redirect: Super_Tau-Zeta's
    #     $B400 player, instrument 8).
    #   * wave_step ($165B) resolves a $90 marker by re-reading at the
    #     redirect target WITHOUT a second check — a marker pointing at
    #     another marker plays the second one's bytes raw.
    # The played position determines the future, so cycle-detect on it:
    # every previously-passing shape returns byte-identical (ctrl, freq,
    # loop) (in-program loop -> same loop index; back-jump before start ->
    # the same appended-tail rotation with loop 0).
    # THE WAVE POSITION IS A BYTE, so it WRAPS rather than running off the end:
    #   $165B  LDY $17f3,x        ; per-voice wave position -- one byte
    #   $165E  LDA $199e,y        ; ctrl[pos]
    #   $1698  INC $17f3,x        ; advance, $FF -> $00
    # A program with no $90 in the 256-cell table does not "run out" — it wraps
    # to cell 0 and keeps stepping, and the `seen` cycle check below then closes
    # it as the loop it really is. Walking `pos` unbounded instead raised
    # `wave_slice no $90` on 4 members whose programs the player reads happily.
    # Same 8-bit-position fact as the sector/track walks above (ledger C11/C2).
    # Exposure measured before relaxing (per
    # [[feedback_relaxing_an_error_kills_its_guards]] — `_assign_offtable_freq`
    # has two `except` guards around this call that would otherwise go dead):
    # exactly 5 of 2,031 members have a raising slice today and ALL 5 are
    # already `unsupported`, so no building member's off-table capture changes.
    pos = start & 0xFF
    first = True                             # wave_init: no marker check
    seen = {}
    while True:
        if pos >= n:
            # only reachable when the table itself is truncated (a_wc/a_wf sit
            # so high that fewer than 256 cells exist) — a genuine unreadable
            # member, not the wrap case above
            raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')
        c, f = wave[pos]
        if not first and c == 0x90:
            pos = f & 0xFF                   # redirect; re-read, no recheck
            if pos >= n:
                raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')
            c, f = wave[pos]
        if pos in seen:
            return ctrl, freq, seen[pos]
        seen[pos] = len(ctrl)
        ctrl.append(c)
        freq.append(f)
        pos = (pos + 1) & 0xFF
        first = False


def _init_clear_range(mem, base: int) -> 'tuple[int, int] | None':
    """The RAM window the player's init zeroes, probed from the member's own
    bytes (static, relocation-aware — ledger C19's method).

    family-4's init ends with a plain clear loop:

        base+$65: A2 00      LDX #$00
        base+$67: 8A         TXA
        base+$68: 9D DF 17   STA <clr>,x
        base+$6B: E8         INX
        base+$6C: E0 79      CPX #$79
        base+$6E: D0 F8      BNE

    It matters to the off-table capture because the freq-HI table ends only 6
    bytes below `clr` (uniform across all 642 family-4 members), so an
    off-table read of any depth lands in memory the init has already zeroed —
    the FILE-IMAGE byte there is stale and is not what the engine reads.
    Returns None (caller keeps the file image) if the shape does not match."""
    if mem[base + 0x68] != 0x9D or mem[base + 0x6C] != 0xE0:
        return None
    start = mem[base + 0x69] | (mem[base + 0x6A] << 8)
    return start, start + mem[base + 0x6D]


def _assign_offtable_freq(mem, a_flo: int, a_fhi: int, m,
                          clear_range: 'tuple[int, int] | None' = None,
                          live_range: 'tuple[int, int] | None' = None) -> None:
    """Set `offtable_freq` on each instrument: per (wave step, effective note)
    the explicit (lo,hi) frequency the step produces when its note-relative
    index `(wave_freq[step] + note) & $FF` runs past the 96-entry freq table.
    Ties each instrument's wave program to the notes it is actually played at
    (orderlist walk: snd-tracked instrument + transpose). The ML-musical
    replacement for the pooled freq_overrun window — frequencies attributed to
    the arpeggio, not bytes-at-offset. The lead-in idle program at index 0 IS
    captured, in the second pass below — which is why this must be called after
    `m.lo_notes` has been resolved to the member's real leftover addresses."""
    def _mark_live(idx: int) -> None:
        # The read's source lands on the engine's LIVE pulsepos/filterpos
        # block: the captured byte is a snapshot of a moving value. Stamp the
        # model (bool + the (kind, idx) set — the read-moment measurement in
        # `measure_live_window_reads` consumes the set); the static capture
        # itself is unchanged here.
        if live_range:
            for kind, a in (('lo', a_flo), ('hi', a_fhi)):
                if live_range[0] <= (a + idx) & 0xFFFF < live_range[1]:
                    m.offtable_live_pos = True
                    m.offtable_live_reads.add((kind, idx))

    # per-instrument melodic steps: list of (step_index, freq_offset)
    inst_steps = {}
    for ins in m.instruments:
        try:
            ctrl, freq, _ = _slice_wave(m.wave, ins.wave_ptr)
        except Exception:
            inst_steps[ins.id] = None        # unresolvable slice -> skip
            continue
        inst_steps[ins.id] = [(s, f) for s, (c, f) in enumerate(zip(ctrl, freq))
                              if not (c & 0x08)]
    # orderlist walk: per instrument, the effective notes it is played at
    osets = ([st.orderlists for st in m.subtunes] if m.subtunes
             else ([m.orderlists] if m.orderlists else []))
    transps = {0}
    for ols in osets:
        for ol in ols:
            for e in ol:
                if e[0] == 'transpose':
                    transps.add(e[1])
    inst_notes = {}
    for ols in osets:
        for ol in ols:
            cur = None
            for e in ol:
                if e[0] != 'sector':
                    continue
                if e[1] >= len(m.sectors):
                    continue
                for se in m.sectors[e[1]]:
                    if se[0] == 'snd':
                        cur = se[1]
                    elif se[0] in ('note', 'glide', 'slide'):
                        ns = ([se[1]] if se[0] == 'note'
                              else [se[2], se[3]] if se[0] == 'glide' else [se[2]])
                        inst_notes.setdefault(cur, set()).update(ns)
    # build the records: per (OFFSET, effective note) the explicit (lo,hi) the
    # off-table read produces. `offset` is a wave-program step's semitone offset
    # OR 0 for the BASE read — `freqtable[effective_note]`, used by vib_setup
    # (vib step = base-note freq << width), the note's own freq, and glide
    # arrival. That offset-0 read off-tables when a note wraps past 95 via
    # transpose (e.g. Redemption_6_4 V1 -> effective note 252), a site the
    # wave-step walk alone misses. idx = (offset + note) & $FF.
    for ins in m.instruments:
        notes = inst_notes.get(ins.id, set())
        if not notes:
            continue
        offsets = {off for _, off in (inst_steps.get(ins.id) or [])}
        offsets.add(0)                       # base / vib / glide-arrival read
        recs = set()
        for off in offsets:
            for n in notes:
                for t in transps:
                    cn = (n + t) & 0xFF
                    idx = (off + cn) & 0xFF
                    if idx > 95:
                        _mark_live(idx)
                        recs.add((off, cn, mem[(a_flo + idx) & 0xFFFF],
                                  mem[(a_fhi + idx) & 0xFFFF]))
        ins.offtable_freq = sorted(recs)

    # The lead-in IDLE program (wave index 0) plays at lo_notes before a voice's
    # first note (cleared wavepos). Its off-table reads are NOT covered by the
    # per-instrument walk above (the idle is not in m.instruments) — e.g.
    # Planet_Love's idle step 6 (offset $E0) x lo_note 26 -> idx 250. Capture them
    # too, attributed to instrument 0 (the composer builds ext[idx] from the union
    # of all records, so attribution is functional; the idle is the lead-in, not
    # instrument 0's arpeggio).
    #
    # ⚠ NOT gated on `any(m.lo_notes)`. A leftover note of $00 is an ORDINARY
    # note, and the idle program's own step OFFSETS are what push the index
    # off-table: Chronic_Music_3 idles at note $00 with idle steps at offsets
    # 251/254, so it reads idx 251-254 and the orig plays those bytes. The
    # all-zero-notes gate skipped exactly those members. (It was invisible
    # while the family-4 notes were read from the canonical address, because
    # the decoy bytes there were usually non-zero — the gate passed for the
    # wrong reason and the block then enumerated the wrong notes.)
    if m.instruments:
        try:
            ic, ifr, _ = _slice_wave(m.wave, 0)
        except Exception:
            ic = ifr = []
        # The lead-in read happens on the FIRST play(), i.e. immediately after
        # init — so the byte the engine sees is the POST-INIT one, and for any
        # address inside the init's clear window that is $00, not the stale
        # file-image byte. (Measured over the family: 253 members make a
        # lead-in off-table read and 86 of them read into the cleared window.)
        # Deeper per-instrument reads deliberately keep the file image: by then
        # that memory holds LIVE engine state, which is ledger C11 territory,
        # not a value this capture can state.
        #
        # ⚠ CONVERGENCE NOTE (ledger C6). DMC **v4** already solves the general
        # form of this — `_correct_offtable_postinit` / `_postinit_values` in
        # `pipelines/dmc/v4/extract/engine_model.py` — by MEASURING the source
        # bytes post-init with `siddump --memwatch` (libsidplayfp ground truth,
        # per-subtune) and keeping only those constant across the sample. That
        # is strictly more general than the clear-window probe here: it also
        # serves bytes init WRITES rather than zeroes (v5 family-4's freq-HI
        # table ends 6 bytes below the clear window, and those 6 are the tune
        # record's track pointers — an off-table read at idx 96-101 still gets
        # the stale file byte from this code). It is deliberately NOT adopted
        # wholesale here yet: it would change captured values for the 1,132
        # canon v5 members that are already FULL, which is a far larger blast
        # radius than this lead-in fix. Converge on the v4 mechanism when that
        # is measured; do not grow a second variant in its place.
        def _at(addr: int) -> int:
            addr &= 0xFFFF
            if clear_range and clear_range[0] <= addr < clear_range[1]:
                return 0
            return mem[addr]

        recs = set(m.instruments[0].offtable_freq)
        for c, off in zip(ic, ifr):
            if c & 0x08:
                continue
            for n in set(m.lo_notes):
                for t in transps:
                    cn = (n + t) & 0xFF
                    idx = (off + cn) & 0xFF
                    if idx > 95:
                        _mark_live(idx)
                        recs.add((off, cn, _at(a_flo + idx), _at(a_fhi + idx)))
        m.instruments[0].offtable_freq = sorted(recs)
