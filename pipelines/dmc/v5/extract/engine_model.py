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


def _load(path: str):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', '..', 'tools'))
    from seed_disassembly import parse_psid
    s = parse_psid(path)
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
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


def extract(cfg, hvsc_root: str = 'hvsc84') -> V5Model:
    from pipelines.dmc.v4.extract.engine_model import (_hdr_clock,
                                                       _hdr_sid_model)
    mem, s = _load(os.path.join(hvsc_root, cfg.sid_path))

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
    n_sub = max(1, s.get('songs', 1))
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
    for i in range(n_sectors):
        sp = mem[a_secp_lo + i] | (mem[a_secp_hi + i] << 8)
        ev, raw = _decode_sector(mem, sp)
        m.sectors.append(ev)
        m.sector_raw.append(raw)
    # Off-table arpeggio frequencies, per instrument (the off-table-read form;
    # see _assign_offtable_freq).
    _assign_offtable_freq(mem, a_flo, a_fhi, m)
    # family-4 (Jupiter41): capture the player-specific leftovers the composer
    # needs (Phase C). curnote $1012-$1014 is NOT cleared by init → the leadin
    # freq before the first note; $1018 = the filter MODE nibble → $D418.
    if getattr(cfg, 'family4', False):
        m.family4 = True
        d = cfg.base - 0x1000
        m.f4_idle_notes = [mem[0x1012 + d + v] for v in range(3)]
        m.f4_filtmode = mem[0x1018 + d]
        m.f4_fcinit = mem[0x1019 + d]
        # C-3: lo_spdctr was read from $1013 = V2 CURNOTE in family-4 (not a
        # speed counter) → a bogus 36-frame startup delay. Zero it; speed=1
        # already gives the 2-phase tick rate. lo_notes (idle) is overridden by
        # f4_idle_notes in the composer, so zero it too. (lo_fchi/lo_fclo/
        # lo_filtmode stay as-is — the filter is C-2's domain; zeroing them
        # makes to_usf emit an empty init.sid filter block.)
        m.lo_spdctr = m.lo_mvolfrac = 0
        m.lo_notes = [0, 0, 0]
    return m


def _slice_wave(wave: list, start: int):
    """Return (ctrl, freq, loop) for the wave program at `start`. `loop` is the
    relative index the $90 marker jumps back to. (Shared with to_usf — kept here
    so the extract's step indexing matches the USF's emitted wave_freq.)"""
    n = len(wave)
    ctrl, freq = [], []
    pos = start
    guard = 0
    while pos < n:
        guard += 1
        if guard > 256:
            raise RuntimeError(f'unsupported:wave_slice runaway @{start}')
        c, f = wave[pos]
        if c == 0x90:
            target = f                       # absolute loop-target index
            if target >= start:
                return ctrl, freq, target - start
            return (ctrl + [wave[k][0] for k in range(target, start)],
                    freq + [wave[k][1] for k in range(target, start)], 0)
        ctrl.append(c)
        freq.append(f)
        pos += 1
    raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')


def _assign_offtable_freq(mem, a_flo: int, a_fhi: int, m) -> None:
    """Set `offtable_freq` on each instrument: per (wave step, effective note)
    the explicit (lo,hi) frequency the step produces when its note-relative
    index `(wave_freq[step] + note) & $FF` runs past the 96-entry freq table.
    Ties each instrument's wave program to the notes it is actually played at
    (orderlist walk: snd-tracked instrument + transpose). The ML-musical
    replacement for the pooled freq_overrun window — frequencies attributed to
    the arpeggio, not bytes-at-offset. (The lead-in idle program at index 0 is
    NOT captured here; if a tune relies on an idle off-table read it shows up as
    a verify regression — handled separately.)"""
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
    if m.instruments and any(m.lo_notes):
        try:
            ic, ifr, _ = _slice_wave(m.wave, 0)
        except Exception:
            ic = ifr = []
        recs = set(m.instruments[0].offtable_freq)
        for c, off in zip(ic, ifr):
            if c & 0x08:
                continue
            for n in set(m.lo_notes):
                for t in transps:
                    cn = (n + t) & 0xFF
                    idx = (off + cn) & 0xFF
                    if idx > 95:
                        recs.add((off, cn, mem[(a_flo + idx) & 0xFFFF],
                                  mem[(a_fhi + idx) & 0xFFFF]))
        m.instruments[0].offtable_freq = sorted(recs)
