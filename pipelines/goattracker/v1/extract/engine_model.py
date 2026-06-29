"""GoatTracker V1 (original 1.x, V1.5 player) — binary → structured model.

Dataflow extraction (feedback_dataflow_over_heuristics): the V1.5 player body
is byte-identical across tunes modulo relocation + a few patched operands, so we
locate each data-table base and each song-global by its FIXED byte-pattern
anchor in the player code (the surrounding opcodes are constant; only the
operand relocates). See RE_NOTES.md §2,§6,§8.

This module READS the original only. It never emits original bytes — the USF
writer (to_usf.py) + the composer regenerate everything from musical content.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# PSID container
# ---------------------------------------------------------------------------

@dataclass
class Sid:
    path: str
    load: int
    init: int
    play: int
    songs: int
    start: int
    name: str
    author: str
    released: str
    mem: bytearray          # full 64K image with payload mapped at `load`
    end: int                # last mapped address + 1


def parse_sid(path: str) -> Sid:
    d = open(path, 'rb').read()
    assert d[:4] in (b'PSID', b'RSID'), f'not a PSID: {path}'
    data_off = struct.unpack('>H', d[6:8])[0]
    load = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    songs = struct.unpack('>H', d[14:16])[0]
    start = struct.unpack('>H', d[16:18])[0]
    name = d[22:54].rstrip(b'\0').decode('latin-1')
    author = d[54:86].rstrip(b'\0').decode('latin-1')
    released = d[86:118].rstrip(b'\0').decode('latin-1')
    payload = d[data_off:]
    if load == 0:
        load = payload[0] | (payload[1] << 8)
        payload = payload[2:]
    mem = bytearray(0x10000)
    mem[load:load + len(payload)] = payload
    return Sid(path=path, load=load, init=init, play=play, songs=songs,
               start=start, name=name, author=author, released=released,
               mem=mem, end=load + len(payload))


# ---------------------------------------------------------------------------
# Byte-pattern anchor search
# ---------------------------------------------------------------------------

def _find(mem: bytearray, lo: int, hi: int, pat: list) -> list[int]:
    """All addresses a in [lo,hi) where mem[a:a+len(pat)] matches pat
    (None = wildcard byte)."""
    out = []
    n = len(pat)
    for a in range(lo, hi - n + 1):
        ok = True
        for i, p in enumerate(pat):
            if p is not None and mem[a + i] != p:
                ok = False
                break
        if ok:
            out.append(a)
    return out


def _w(mem, a):
    return mem[a] | (mem[a + 1] << 8)


@dataclass
class Layout:
    """Relocated data-table bases + song globals read from the player."""
    instbase: int          # instrument records, 8 bytes/record
    wavetbl: int           # wave-program left column (waveform/delay)
    notetbl: int           # wave-program right column (note rel/abs)
    patttbllo: int
    patttblhi: int
    songtbllo: int
    songtblhi: int
    filttbl: int
    gatetimer: int         # ticks-before-next-note (hard-restart window)
    hr_ad: int             # hard-restart $D405 value
    hr_sr: int             # hard-restart $D406 value
    freqlo: int = 0        # freq table lo base (per-player; 96 entries)
    freqhi: int = 0        # freq table hi base


def detect_layout(sid: Sid) -> Layout:
    """Locate table bases + song globals via fixed code anchors."""
    mem, lo, hi = sid.mem, sid.load, sid.end

    def one(pat, opnd_off, what):
        hits = _find(mem, lo, hi, pat)
        if not hits:
            raise ValueError(f'V1 anchor not found: {what}')
        return hits

    # instbase: the instrument table is the ONLY table loaded (lda abs,Y = B9)
    # at many distinct offsets within an 8-byte window (fields 0,1,2,3,6,7);
    # every other table is loaded at 1-2 operands. Cluster B9 operands and pick
    # the 8-window with the most members. Variant-tolerant (some V1.x builds
    # insert a PHA/PLA around the pulse handler, breaking a single-opcode anchor).
    b9ops = set()
    for a in range(lo, hi - 2):
        if mem[a] == 0xB9:
            o = _w(mem, a + 1)
            if lo <= o < hi:
                b9ops.add(o)
    instbase, best = None, -1
    for base in b9ops:
        c = sum(1 for k in range(8) if base + k in b9ops)
        if c > best:
            best, instbase = c, base
    if instbase is None or best < 4:
        raise ValueError('V1 instrument-table cluster not found')

    # wavetbl: `lda mt_wavetbl,y; cmp #$08`  -> B9 <lo> <hi> C9 08
    h = one([0xB9, None, None, 0xC9, 0x08], 1, 'wavetbl')
    wavetbl = _w(mem, h[0] + 1)

    # notetbl: `lda mt_notetbl,y; bmi; clc; adc mt_chnnote,x`
    #   B9 <lo> <hi> 30 ?? 18 7D
    h = one([0xB9, None, None, 0x30, None, 0x18, 0x7D], 1, 'notetbl')
    notetbl = _w(mem, h[0] + 1)

    # filttbl: `mt_setfiltersub: tay; lda mt_filttbl,y; beq` -> A8 B9 <lo> <hi> F0
    h = one([0xA8, 0xB9, None, None, 0xF0], 2, 'filttbl')
    filttbl = _w(mem, h[0] + 2)

    # patttbl + songtbl: both `lda LO,y; sta $fc; lda HI,y; sta $fd`
    #   B9 <lo> <hi> 85 FC B9 <Lo> <Hi> 85 FD
    pairs = one([0xB9, None, None, 0x85, 0xFC, 0xB9, None, None, 0x85, 0xFD],
                1, 'songtbl/patttbl')
    pairs = sorted(pairs)
    if len(pairs) < 2:
        raise ValueError('expected 2 songtbl/patttbl pointer loads')
    # getnewnotes (pattern) precedes sequencer (song) in the player.
    patt_a, song_a = pairs[0], pairs[1]
    patttbllo, patttblhi = _w(mem, patt_a + 1), _w(mem, patt_a + 6)
    songtbllo, songtblhi = _w(mem, song_a + 1), _w(mem, song_a + 6)

    # gatetimer: initial-tick `lda #$05; sta chntempo,x; lda #gt+2; sta chntick,x; lda #$ff`
    #   A9 05 9D ?? ?? A9 ?? 9D ?? ?? A9 FF
    h = one([0xA9, 0x05, 0x9D, None, None, 0xA9, None, 0x9D, None, None,
             0xA9, 0xFF], 6, 'gatetimer')
    gatetimer = (mem[h[0] + 6] - 2) & 0xFF

    # hard-restart AD/SR: `lda #imm; sta $d405,x` / `sta $d406,x`
    ad_h = one([0xA9, None, 0x9D, 0x05, 0xD4], 1, 'hr_ad')
    sr_h = one([0xA9, None, 0x9D, 0x06, 0xD4], 1, 'hr_sr')
    hr_ad = mem[ad_h[0] + 1]
    hr_sr = mem[sr_h[0] + 1]

    # freq table — PER-PLAYER (V1.x sub-versions ship different tables!).
    # arpfreq: lda freqlo,y; sta x; lda freqhi,y; sta x → B9 ?? ?? 9D ?? ?? B9
    # ?? ?? 9D. The freqlo/freqhi pair are 96 ($60) bytes apart; other matches
    # (the new-note instwave/instad load) are not — disambiguate on that.
    freqlo = freqhi = 0
    for h in _find(mem, lo, hi, [0xB9, None, None, 0x9D, None, None,
                                 0xB9, None, None, 0x9D]):
        o1 = _w(mem, h + 1)
        o2 = _w(mem, h + 7)
        if abs(o1 - o2) == 96:
            freqhi, freqlo = (o1, o2) if o1 < o2 else (o2, o1)
            break
    return Layout(instbase=instbase, wavetbl=wavetbl, notetbl=notetbl,
                  patttbllo=patttbllo, patttblhi=patttblhi,
                  songtbllo=songtbllo, songtblhi=songtblhi, filttbl=filttbl,
                  gatetimer=gatetimer, hr_ad=hr_ad, hr_sr=hr_sr,
                  freqlo=freqlo, freqhi=freqhi)


# ---------------------------------------------------------------------------
# Table parsing — faithful structured model (binary semantics)
# ---------------------------------------------------------------------------

@dataclass
class Row:
    """One decoded pattern row. note: 0-$5D real note (C0..A7); $5E keyoff;
    $5F rest; or a packed-rest run (rest_rows>0)."""
    note: int                  # raw note value (see above); -1 if pure packed rest
    instr: int                 # current instrument number (1-based; carried)
    cmd: Optional[int] = None  # 0-7, or None (note-only row — INHERITS prev cmd)
    param: Optional[int] = None
    new_instr: bool = False    # True iff this row's cmd byte set inst field != 0
    rest_rows: int = 0         # >0 → packed rest of this many row-slots


@dataclass
class Pattern:
    num: int
    addr: int
    rows: list[Row] = field(default_factory=list)


@dataclass
class OrderList:
    addr: int
    entries: list[int] = field(default_factory=list)        # pattern numbers
    transposes: list[int] = field(default_factory=list)     # signed, per entry
    repeats: list[int] = field(default_factory=list)        # play-count per entry
    loop_to: Optional[int] = None                            # entry index


@dataclass
class WaveStep:
    left: int       # waveform ($08-$FF) or delay ($00-$07)
    right: int      # note: rel (bit7 clear, +note) / abs (bit7 set)


@dataclass
class Instr:
    num: int
    ad: int
    sr: int
    pulse: int
    pulsespd: int
    pulselow: int
    pulsehigh: int
    filter: int
    wave: int                 # wave-program start pointer
    wave_steps: list[WaveStep] = field(default_factory=list)
    wave_loop: Optional[int] = None    # step index the program loops to


@dataclass
class FilterEntry:
    ptr: int
    b0: int        # ctrl ($D417) / 0=mod-marker
    b1: int        # type|vol ($D418) / filttime
    b2: int        # cutoff ($D416) / cutoff-add
    b3: int        # next-step ptr


@dataclass
class V1Song:
    sid: Sid
    layout: Layout
    subtunes: list[list[OrderList]]          # [subtune][channel] -> OrderList
    patterns: dict[int, Pattern]
    instruments: dict[int, Instr]
    filters: dict[int, FilterEntry]
    # Init filter state from setfiltersub(0) at song init (RE_NOTES §1): the
    # engine reads filttbl[0..3] even on no-filter tunes, setting a constant
    # $D416/$D417/$D418-type the play loop writes every frame. (d416, d417,
    # d418type, filttime, filtstep) + funk(filttbl[2],[3]).
    init_filter: tuple = (0, 0, 0x0F, 0, 0)
    funk: tuple = (0, 0)
    freq_lo: list = field(default_factory=list)   # 96 bytes (per-player table)
    freq_hi: list = field(default_factory=list)


def _sim_setfilter0(mem, filttbl) -> tuple:
    """Simulate setfiltersub(ptr=0) → (d416, d417, d418type, filttime, filtstep)."""
    b0, b1, b2 = mem[filttbl], mem[filttbl + 1], mem[filttbl + 2]
    if b0 != 0:                                  # static
        d417 = b0
        d418type = b1
        d416 = b2 if b2 != 0 else 0
        return (d416, d417, d418type, 0, 0)
    # mod path: filtcutadd=b2, filttime=b1, filtstep=0 (ptr==0)
    return (0, 0, 0x0F, b1, 0)


def _ptr(mem, lo_base, hi_base, idx):
    return mem[lo_base + idx] | (mem[hi_base + idx] << 8)


def parse_orderlist(mem, addr) -> OrderList:
    """Walk a channel orderlist (RE_NOTES §3)."""
    ol = OrderList(addr=addr)
    byte_of_entry = []        # entry idx -> byte offset of its pattern byte
    cur_trans = 0
    pending_repeat = 1
    pos = addr
    loop_byteoff = None
    guard = 0
    while guard < 4096:
        guard += 1
        b = mem[pos]
        off = pos - addr
        pos += 1
        if b < 0xD0:                                  # pattern number
            byte_of_entry.append(off)
            ol.entries.append(b)
            ol.transposes.append(cur_trans)
            ol.repeats.append(pending_repeat)
            pending_repeat = 1
        elif b < 0xE0:                                # REPEAT $D0-$DF
            pending_repeat = (b - 0xD0) + 1
        elif b < 0xFF:                                # TRANS $E0-$FE
            cur_trans = b - 0xF0                       # signed: $E0=-16..$FE=+14
        else:                                          # $FF LOOPSONG
            loop_byteoff = mem[pos]
            break
    # resolve loop byte offset → entry index
    if loop_byteoff is not None:
        for i, bo in enumerate(byte_of_entry):
            if bo == loop_byteoff:
                ol.loop_to = i
                break
        else:
            ol.loop_to = 0
    if not any(ol.transposes):
        ol.transposes = []
    if all(r == 1 for r in ol.repeats):
        ol.repeats = []
    return ol


def parse_pattern(mem, num, addr) -> Pattern:
    """Walk a pattern's variable-length rows (RE_NOTES §4)."""
    pat = Pattern(num=num, addr=addr)
    cur_instr = 0
    pos = addr
    guard = 0
    while guard < 8192:
        guard += 1
        b = mem[pos]; pos += 1
        if b == 0xFF:                                  # ENDPATT
            break
        if b < 0x60:                                   # note WITH command (3-byte)
            note = b
            fx = mem[pos]; pos += 1
            param = mem[pos]; pos += 1
            inst = (fx & 0xF8) >> 3
            cmd = fx & 0x07
            new_instr = inst != 0
            if new_instr:
                cur_instr = inst
            pat.rows.append(Row(note=note, instr=cur_instr, cmd=cmd,
                                param=param, new_instr=new_instr))
        elif b < 0xC0:                                 # note WITHOUT command (1-byte)
            # sbc #$5F runs with carry CLEAR (after cmp #$c0, b<$c0) → b-$60.
            note = b - 0x60                            # $60→C0($00) .. $BD→A7, $BE=keyoff, $BF=rest
            pat.rows.append(Row(note=note, instr=cur_instr))
        else:                                          # $C0-$FE packed rest
            pat.rows.append(Row(note=-1, instr=cur_instr, rest_rows=256 - b))
    return pat


def parse_wave_program(mem, layout: Layout, wave_ptr) -> tuple[list[WaveStep], Optional[int]]:
    """Follow an instrument's wave program from wave_ptr through wavetbl/notetbl
    until the loop/end marker (RE_NOTES §2). Returns (steps, loop_step_index)."""
    if wave_ptr == 0:
        return [], None
    steps: list[WaveStep] = []
    idx = wave_ptr
    guard = 0
    loop_to = None
    while guard < 256:
        guard += 1
        left = mem[layout.wavetbl + idx]
        right = mem[layout.notetbl + idx]
        steps.append(WaveStep(left=left, right=right))
        nxt_left = mem[layout.wavetbl + idx + 1]
        if nxt_left == 0xFF:                           # LOOPWAVE marker at idx+1
            tgt = mem[layout.notetbl + idx + 1]
            if tgt == 0:
                loop_to = len(steps) - 1               # stays (target 0)
            else:
                # new ptr = tgt + wave_ptr - 2 (loop target relative to inst start)
                new_idx = (tgt + wave_ptr - 2) & 0xFF
                loop_to = new_idx - wave_ptr           # step-relative
            break
        idx += 1
    return steps, loop_to


def parse_filter_entry(mem, layout: Layout, ptr) -> FilterEntry:
    base = layout.filttbl + ptr
    return FilterEntry(ptr=ptr, b0=mem[base], b1=mem[base + 1],
                       b2=mem[base + 2], b3=mem[base + 3])


def extract(sid: Sid) -> V1Song:
    L = detect_layout(sid)
    mem = sid.mem

    # 1. Orderlists per subtune per channel (songnum = subtune*3 + channel).
    subtunes: list[list[OrderList]] = []
    pat_nums: set[int] = set()
    for s in range(sid.songs):
        chans = []
        for ch in range(3):
            songnum = s * 3 + ch
            addr = _ptr(mem, L.songtbllo, L.songtblhi, songnum)
            ol = parse_orderlist(mem, addr)
            chans.append(ol)
            pat_nums.update(ol.entries)
        subtunes.append(chans)

    # 2. Used patterns.
    patterns: dict[int, Pattern] = {}
    instr_nums: set[int] = set()
    for pn in sorted(pat_nums):
        addr = _ptr(mem, L.patttbllo, L.patttblhi, pn)
        pat = parse_pattern(mem, pn, addr)
        patterns[pn] = pat
        for r in pat.rows:
            if r.instr:
                instr_nums.add(r.instr)

    # 3. Used instruments + their wave programs.
    instruments: dict[int, Instr] = {}
    filt_ptrs: set[int] = set()
    for inum in sorted(instr_nums):
        base = L.instbase + inum * 8
        inst = Instr(num=inum, ad=mem[base], sr=mem[base + 1],
                     pulse=mem[base + 2], pulsespd=mem[base + 3],
                     pulselow=mem[base + 4], pulsehigh=mem[base + 5],
                     filter=mem[base + 6], wave=mem[base + 7])
        inst.wave_steps, inst.wave_loop = parse_wave_program(mem, L, inst.wave)
        instruments[inum] = inst
        if inst.filter:
            filt_ptrs.add(inst.filter)

    # 4. Filter entries (referenced by instruments + setfilter commands).
    for pat in patterns.values():
        for r in pat.rows:
            if r.cmd == 5 and r.param:
                filt_ptrs.add(r.param)
    filters: dict[int, FilterEntry] = {}
    for fp in sorted(filt_ptrs):
        filters[fp] = parse_filter_entry(mem, L, fp)

    init_filter = _sim_setfilter0(mem, L.filttbl)
    funk = (mem[L.filttbl + 2], mem[L.filttbl + 3])
    # Capture 128 entries (not 96): wave-program relative notes mask to &$7F
    # (0-127), so notes can run PAST the 96-entry table into the following image
    # bytes, which the engine plays as real freqs (C6 off-table read). Capturing
    # the reachable window reproduces those reads as per-tune content.
    freq_lo = [mem[L.freqlo + i] for i in range(128)] if L.freqlo else []
    freq_hi = [mem[L.freqhi + i] for i in range(128)] if L.freqhi else []
    return V1Song(sid=sid, layout=L, subtunes=subtunes, patterns=patterns,
                  instruments=instruments, filters=filters,
                  init_filter=init_filter, funk=funk,
                  freq_lo=freq_lo, freq_hi=freq_hi)


# ---------------------------------------------------------------------------
# Debug entry — validate detection against a canary
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/T/Topaz/Joker.sid'
    sid = parse_sid(path)
    print(f'{path}')
    print(f'  load=${sid.load:04x} init=${sid.init:04x} play=${sid.play:04x} '
          f'songs={sid.songs} name={sid.name!r}')
    L = detect_layout(sid)
    print(f'  instbase   ${L.instbase:04x}')
    print(f'  wavetbl    ${L.wavetbl:04x}   notetbl ${L.notetbl:04x}')
    print(f'  patttbl    lo ${L.patttbllo:04x} hi ${L.patttblhi:04x}')
    print(f'  songtbl    lo ${L.songtbllo:04x} hi ${L.songtblhi:04x}')
    print(f'  filttbl    ${L.filttbl:04x}')
    print(f'  gatetimer  {L.gatetimer}   hr_ad ${L.hr_ad:02x} hr_sr ${L.hr_sr:02x}')
    song = extract(sid)
    print(f'\n  subtunes={len(song.subtunes)} patterns={len(song.patterns)} '
          f'instruments={len(song.instruments)} filters={len(song.filters)}')
    for ch, ol in enumerate(song.subtunes[0]):
        print(f'  ch{ch}: {len(ol.entries)} entries={ol.entries[:12]}'
              f'{"..." if len(ol.entries) > 12 else ""} loop_to={ol.loop_to} '
              f'trans={ol.transposes[:6]} rep={ol.repeats[:6]}')
    for inum, inst in list(song.instruments.items())[:6]:
        print(f'  i{inum}: ad=${inst.ad:02x} sr=${inst.sr:02x} pulse=${inst.pulse:02x} '
              f'spd=${inst.pulsespd:02x} lo=${inst.pulselow:02x} hi=${inst.pulsehigh:02x} '
              f'filt={inst.filter} wave={inst.wave} ({len(inst.wave_steps)} steps, '
              f'loop={inst.wave_loop})')
    p0 = next(iter(song.patterns.values()))
    print(f'  pattern {p0.num}: {len(p0.rows)} rows; first 8:')
    for r in p0.rows[:8]:
        print(f'      note={r.note if r.note>=0 else "RST"} i{r.instr} '
              f'cmd={r.cmd} param={"$%02x"%r.param if r.param is not None else None} '
              f'rest_rows={r.rest_rows}')
