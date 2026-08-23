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
def _decode_orderlist(mem, ptr: int):
    out = []
    pos = 0
    guard = 0
    while guard < 512:
        guard += 1
        b = mem[ptr + pos]
        if b == 0xFF:
            out.append(('loop', mem[ptr + pos + 1]))
            return out, bytes(mem[ptr:ptr + pos + 2])
        if b == 0xFE:
            out.append(('end',))
            return out, bytes(mem[ptr:ptr + pos + 1])
        if b == 0xFD:
            out.append(('transpose', mem[ptr + pos + 1]))
            pos += 2
            continue
        if b == 0xFC:
            out.append(('transpose', (-mem[ptr + pos + 1]) & 0xFF))
            pos += 2
            continue
        out.append(('sector', b))
        pos += 1
    raise RuntimeError(f'orderlist at ${ptr:04X} never ends')


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


def _decode_sector(mem, ptr: int):
    out = []
    pos = 0
    guard = 0
    while guard < 4096:
        guard += 1
        b = mem[ptr + pos]
        if b == 0xFF:
            out.append(('end',))
            return out, bytes(mem[ptr:ptr + pos + 1])
        if b < 0x80:
            out.append(('note', b))
            pos += 1
            continue
        if b not in _CMD:
            raise RuntimeError(f'unknown sector cmd ${b:02X} @ ${ptr+pos:04X}')
        name, n = _CMD[b]
        args = tuple(mem[ptr + pos + 1 + k] for k in range(n - 1))
        out.append((name,) + args)
        pos += n
    raise RuntimeError(f'sector at ${ptr:04X} never ends')


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
    n_sectors = a_secp_hi - a_secp_lo

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
        for v in range(3):
            tp = _rd16(mem, rec + v * 2)
            ev, raw = _decode_orderlist(mem, tp)
            st.orderlists.append(ev)
            st.orderlist_raw.append(raw)
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
    for i in range(n_sectors):
        sp = mem[a_secp_lo + i] | (mem[a_secp_hi + i] << 8)
        try:
            ev, raw = _decode_sector(mem, sp)
        except RuntimeError:
            if i in referenced:
                raise
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
    _assign_offtable_freq(mem, a_flo, a_fhi, m,
                          clear_range=(_init_clear_range(mem, cfg.base)
                                       if getattr(cfg, 'family4', False)
                                       else None))
    return m


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
    pos = start
    first = True                             # wave_init: no marker check
    seen = {}
    guard = 0
    while True:
        guard += 1
        if guard > 512:
            raise RuntimeError(f'unsupported:wave_slice runaway @{start}')
        if pos >= n:
            raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')
        c, f = wave[pos]
        if not first and c == 0x90:
            pos = f                          # redirect; re-read, no recheck
            if pos >= n:
                raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')
            c, f = wave[pos]
        if pos in seen:
            return ctrl, freq, seen[pos]
        seen[pos] = len(ctrl)
        ctrl.append(c)
        freq.append(f)
        pos += 1
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
                          clear_range: 'tuple[int, int] | None' = None) -> None:
    """Set `offtable_freq` on each instrument: per (wave step, effective note)
    the explicit (lo,hi) frequency the step produces when its note-relative
    index `(wave_freq[step] + note) & $FF` runs past the 96-entry freq table.
    Ties each instrument's wave program to the notes it is actually played at
    (orderlist walk: snd-tracked instrument + transpose). The ML-musical
    replacement for the pooled freq_overrun window — frequencies attributed to
    the arpeggio, not bytes-at-offset. The lead-in idle program at index 0 IS
    captured, in the second pass below — which is why this must be called after
    `m.lo_notes` has been resolved to the member's real leftover addresses."""
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
                        recs.add((off, cn, _at(a_flo + idx), _at(a_fhi + idx)))
        m.instruments[0].offtable_freq = sorted(recs)
