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
    # off-table freq-hi window (DMC v5 analog of FC freq_overrun): the image
    # bytes after the 96-entry freq tables that the melodic wave path reads
    # when (wave_freq[step]+curnote)&$FF passes 95. Content-by-reference,
    # emitted right after freqhi so off-table indices resolve as in the orig.
    freq_overrun: list = field(default_factory=list)
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
    title: str = ''
    author: str = ''
    released: str = ''


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
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
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
    # Off-table arpeggio frequencies, per instrument (replaces the freq_overrun
    # blob). m.freq_overrun stays empty for v5; see _assign_offtable_freq.
    m.freq_overrun = []
    _assign_offtable_freq(mem, a_flo, a_fhi, m)
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


def _freq_overrun(mem, a_fhi: int, m) -> list:
    """Reachable off-table freq-hi window (DMC v5 analog of FC freq_overrun).

    The melodic wave path computes `(wave_freq[step] + curnote) & $FF` and
    reads freqlo/freqhi at that index; indices past 95 fall off the 96-entry
    tables into the following image bytes, which the orig plays as real freqs
    (e.g. Elysium inst8/9: wave_freq=64 + note 60 = index 124 → freq_hi 0).
    Capture only what the tune can REACH — every melodic wave value × every
    note (incl. glide/slide targets + idle notes) × every orderlist transpose,
    a conservative over-approximation. The window is contiguous from offset 96
    to the max reachable index so the composer can lay it right after freqhi.
    Empty when nothing reaches off-table. An under-capture can't pass silently:
    the next data section sits right after the window, so it diverges in verify.

    NB this STATIC over-approximation cannot de-verbatim much (contiguous-to-max
    + a note may be too short to advance the wave to the overshooting step). The
    runtime-accurate de-verbatim (drop the blob where the read is never actually
    reached — ~81% per the round-13 audibility census) is VERIFY-GATED in
    tools/dmc_v5_deverbatim.py: build with [] and keep empty iff it still
    verifies FULL, else fall back to this capture. So this stays the proven
    backstop; the batch decides empty-vs-blob per member by the writelog verdict.
    """
    melodic = {f for (c, f) in m.wave if not (c & 0x08)}
    if not melodic:
        return []
    notes = set(m.lo_notes)
    for sec in m.sectors:
        for e in sec:
            if e[0] == 'note':
                notes.add(e[1])
            elif e[0] == 'glide':            # (spd, cur, tgt)
                notes.add(e[2]); notes.add(e[3])
            elif e[0] == 'slide':            # (spd, tgt)
                notes.add(e[2])
    transps = {0}
    for st in m.subtunes:
        for ol in st.orderlists:
            for e in ol:
                if e[0] == 'transpose':
                    transps.add(e[1])
    curnotes = {(n + t) & 0xFF for n in notes for t in transps}
    oot = {(f + cn) & 0xFF for f in melodic for cn in curnotes}
    oot = {i for i in oot if 96 <= i <= 255}
    if not oot:
        return []
    return [mem[(a_fhi + i) & 0xFFFF] for i in range(96, max(oot) + 1)]
