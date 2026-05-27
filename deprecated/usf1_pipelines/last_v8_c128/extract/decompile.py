"""Parse the Last V8 (C128) RSID and identify its engine structure.

The Last V8 (C128) SID is structurally different from the
Commando/Monty-era tracker SIDs — it's an RSID with an IRQ-driven play
routine, a dual engine (tracker + sample player), and a runtime
relocator that moves the sample player to $C000. This module decodes
just enough of the binary to populate an `EngineModel` (see types.py);
the heavier lift of recovering subtune-level note streams is left to
later work.

The constants below come from the hand-annotated disassembly at
docs/hubbard_last_v8_c128_disassembly.s — read that first if anything
here is surprising.
"""

from __future__ import annotations

from pathlib import Path

from .types import (
    EngineModel,
    Instrument,
    MusicSubtune,
    MusicTables,
    Orderlist,
    Pattern,
    PatternEvent,
    RSIDHeader,
    SampleRecord,
    SubtuneRoute,
)


# ----- well-known addresses inside the binary --------------------------

# Per-subtune dispatch ranges (from $7E80):
#   subtune < 3      → music
#   subtune in 3..5  → sample
#   subtune >= 6     → sfx (sound effect arming on V1+V2)
ROUTE_MUSIC_MAX_EXCLUSIVE = 3
ROUTE_SAMPLE_MAX_EXCLUSIVE = 6

# The sample-player records, read from $C200,X with X=$97*4 where
# $97 = subtune - 2. In the binary they live at $7D40 (= $C200 source).
SAMPLE_RECORD_BASE = 0x7D40
SAMPLE_RECORD_STRIDE = 4
# Search-table area (= $C300 source). Holds CIA threshold + valid IDs.
SAMPLE_PARAMS_BASE = 0x7E40   # $C300 in relocated space
SAMPLE_RATE_OFFSET = 0x0A     # $C30A holds the CIA Timer A threshold

# Music tables (fixed in this binary).
FREQ_TABLE_ADDR = 0x843B
INSTRUMENT_TABLE_ADDR = 0x85A1
SFX_TABLE_ADDR = 0x8699
ORDERLIST_PTRS_ADDR = 0x8791
PATTERN_PTR_LO_ADDR = 0x87A9
PATTERN_PTR_HI_ADDR = 0x87C6

# Relocator parameters (see $7E91 in the disassembly).
RELOCATOR_SRC = 0x7B40
RELOCATOR_LEN = 0x0400
RELOCATOR_DST = 0xC000


def _read_header(blob: bytes) -> RSIDHeader:
    magic = blob[:4].decode('ascii')
    if magic not in ('PSID', 'RSID'):
        raise ValueError(f'not a PSID/RSID: magic={magic!r}')
    version = int.from_bytes(blob[4:6], 'big')
    data_off = int.from_bytes(blob[6:8], 'big')
    load = int.from_bytes(blob[8:10], 'big')
    init_addr = int.from_bytes(blob[10:12], 'big')
    play_addr = int.from_bytes(blob[12:14], 'big')
    songs = int.from_bytes(blob[14:16], 'big')
    start_song = int.from_bytes(blob[16:18], 'big')
    name = blob[22:54].rstrip(b'\0').decode('latin-1')
    author = blob[54:86].rstrip(b'\0').decode('latin-1')
    released = blob[86:118].rstrip(b'\0').decode('latin-1')

    payload = blob[data_off:]
    if load == 0:
        load = payload[0] | (payload[1] << 8)

    return RSIDHeader(
        magic=magic, version=version, load_addr=load,
        init_addr=init_addr, play_addr=play_addr,
        songs=songs, start_song=start_song,
        name=name, author=author, released=released,
    )


def _read_payload(blob: bytes) -> tuple[int, bytes]:
    """Return (data_offset_in_file, raw payload after stripping load addr)."""
    data_off = int.from_bytes(blob[6:8], 'big')
    load = int.from_bytes(blob[8:10], 'big')
    raw = blob[data_off:]
    if load == 0:
        raw = raw[2:]
    return data_off, raw


def _categorise_subtunes(songs: int) -> list[SubtuneRoute]:
    routes: list[SubtuneRoute] = []
    for s in range(songs):
        if s < ROUTE_MUSIC_MAX_EXCLUSIVE:
            kind = 'music'
        elif s < ROUTE_SAMPLE_MAX_EXCLUSIVE:
            kind = 'sample'
        else:
            kind = 'sfx'
        routes.append(SubtuneRoute(subtune=s, kind=kind))
    return routes


def _extract_samples(payload: bytes, load: int,
                     routes: list[SubtuneRoute]) -> list[SampleRecord]:
    """Read the 4-byte (start_lo, start_hi, end_lo, end_hi) records.

    Indexed by $97 = subtune - 2, so subtune 3 → record at +$04, subtune
    4 → +$08, subtune 5 → +$0C (record 0 at +$00 is unused / sentinel).
    """
    rate = payload[SAMPLE_PARAMS_BASE + SAMPLE_RATE_OFFSET - load]
    samples: list[SampleRecord] = []
    for r in routes:
        if r.kind != 'sample':
            continue
        idx = r.subtune - 2  # $97 value
        off = SAMPLE_RECORD_BASE - load + idx * SAMPLE_RECORD_STRIDE
        start = payload[off] | (payload[off + 1] << 8)
        end = payload[off + 2] | (payload[off + 3] << 8)
        samples.append(SampleRecord(
            subtune=r.subtune,
            start=start, end=end,
            rate_constant=rate,
        ))
    return samples


# Pattern-byte semantics (see annotated disassembly $80CF..$816A).
HOLD_HAS_FX     = 0x80
HOLD_TIE        = 0x40
HOLD_NORELEASE  = 0x20
HOLD_COUNT_MASK = 0x1F
PATTERN_END     = 0xFF
ORDER_RESTART   = 0xFF
ORDER_END_SONG  = 0xFE
# Orderlist scan safety net: real V2 orderlist in subtune 0 is 88 bytes long.
MAX_ORDERLIST_BYTES = 256


def _read_pattern_addresses(payload: bytes, load: int) -> list[int]:
    """Return absolute pattern addresses from the $87A9/$87C6 ptr tables.

    The tables look like 29 entries each, but the last lo/hi pair points
    past the end of meaningful pattern data (into the dispatcher code at
    $8C53). We trim the list to the highest pattern index that the
    extracted orderlists actually reference (computed downstream).
    """
    n = PATTERN_PTR_HI_ADDR - PATTERN_PTR_LO_ADDR
    lo_off = PATTERN_PTR_LO_ADDR - load
    hi_off = PATTERN_PTR_HI_ADDR - load
    return [payload[lo_off + i] | (payload[hi_off + i] << 8) for i in range(n)]


def _decode_pattern(payload: bytes, load: int, index: int,
                    addr: int) -> Pattern:
    events: list[PatternEvent] = []
    off = addr - load
    while True:
        b = payload[off]
        if b == PATTERN_END:
            off += 1
            break
        has_fx = bool(b & HOLD_HAS_FX)
        tie = bool(b & HOLD_TIE)
        norel = bool(b & HOLD_NORELEASE)
        hold = b & HOLD_COUNT_MASK
        off += 1
        if tie:
            events.append(PatternEvent(
                kind='tie', hold_byte=b, hold=hold, no_release=norel,
                pitch=None,
            ))
            continue
        inst, arp = None, None
        if has_fx:
            fx = payload[off]
            off += 1
            if fx & 0x80:
                arp = fx
            else:
                inst = fx
        pitch = payload[off]
        off += 1
        events.append(PatternEvent(
            kind='note', hold_byte=b, hold=hold, no_release=norel,
            pitch=pitch, instrument=inst, arp_mode=arp,
        ))
    return Pattern(index=index, addr=addr, events=events, end_addr=load + off)


def _read_orderlist(payload: bytes, load: int, voice: int,
                    addr: int) -> Orderlist:
    off = addr - load
    indices: list[int] = []
    terminator = 'restart'
    for _ in range(MAX_ORDERLIST_BYTES):
        b = payload[off]
        off += 1
        if b == ORDER_END_SONG:
            terminator = 'end_song'
            break
        if b == ORDER_RESTART:
            terminator = 'restart'
            break
        indices.append(b)
    else:
        raise RuntimeError(
            f'orderlist at ${addr:04X} (voice {voice}) has no '
            f'$FE/$FF terminator within {MAX_ORDERLIST_BYTES} bytes'
        )
    return Orderlist(voice=voice, addr=addr,
                     indices=indices, terminator=terminator)


def _read_music_subtunes(payload: bytes, load: int,
                         routes: list[SubtuneRoute]) -> list[MusicSubtune]:
    """The 3 music subtunes (routes[0..2]) each get 6 bytes at
    $8797 + subtune*6: V0_lo, V1_lo, V2_lo, V0_hi, V1_hi, V2_hi."""
    subtunes: list[MusicSubtune] = []
    for r in routes:
        if r.kind != 'music':
            continue
        base = 0x8797 + r.subtune * 6
        rec = payload[base - load:base - load + 6]
        voices: list[Orderlist] = []
        for v in range(3):
            vaddr = rec[v] | (rec[v + 3] << 8)
            voices.append(_read_orderlist(payload, load, v, vaddr))
        subtunes.append(MusicSubtune(subtune=r.subtune, voices=voices))
    return subtunes


def _read_instruments(payload: bytes, load: int,
                      patterns: list[Pattern]) -> list[Instrument]:
    """Read 8-byte records from $85A1, trimming all-zero padding.

    We always keep entries up to (max referenced id), then keep any
    further non-empty records that follow (orphan instruments do exist
    in some Hubbard SIDs). Stop at the first all-zero record beyond
    that frontier.
    """
    referenced = {ev.instrument for p in patterns for ev in p.events
                  if ev.instrument is not None}
    keep_to = max(referenced) if referenced else -1
    instruments: list[Instrument] = []
    base_off = INSTRUMENT_TABLE_ADDR - load
    table_end = SFX_TABLE_ADDR - load
    i = 0
    while base_off + i * 8 + 8 <= table_end:
        off = base_off + i * 8
        rec = payload[off:off + 8]
        inst = Instrument(
            id=i,
            pulse_width=rec[0] | (rec[1] << 8),
            ctrl=rec[2], ad=rec[3], sr=rec[4],
            vib_shift=rec[5], pwm=rec[6], fx_flags=rec[7],
        )
        if i > keep_to and inst.is_empty:
            break
        instruments.append(inst)
        i += 1
    return instruments


def _decode_patterns(payload: bytes, load: int,
                     music_subtunes: list[MusicSubtune]) -> list[Pattern]:
    """Decode exactly the patterns the orderlists actually reference,
    plus any contiguous siblings that fit between referenced ones."""
    addrs = _read_pattern_addresses(payload, load)
    used = sorted({i for s in music_subtunes for v in s.voices for i in v.indices})
    if not used:
        return []
    max_idx = max(used)
    # Pattern index `max_idx + 1` and beyond may point past the end of
    # the pattern data region (the last entry in this binary aliases the
    # dispatcher at $8C53). Trim to the used range.
    return [_decode_pattern(payload, load, i, addrs[i])
            for i in range(max_idx + 1)]


def decompile(sid_path: str | Path) -> EngineModel:
    """Parse an SID file and return the static engine model."""
    blob = Path(sid_path).read_bytes()
    header = _read_header(blob)
    data_off, payload = _read_payload(blob)

    routes = _categorise_subtunes(header.songs)
    samples = _extract_samples(payload, header.load_addr, routes)
    music_subtunes = _read_music_subtunes(payload, header.load_addr, routes)
    patterns = _decode_patterns(payload, header.load_addr, music_subtunes)
    instruments = _read_instruments(payload, header.load_addr, patterns)

    music = MusicTables(
        freq_table_addr=FREQ_TABLE_ADDR,
        instrument_table_addr=INSTRUMENT_TABLE_ADDR,
        sfx_table_addr=SFX_TABLE_ADDR,
        orderlist_ptrs_addr=ORDERLIST_PTRS_ADDR,
        pattern_ptr_lo_addr=PATTERN_PTR_LO_ADDR,
        pattern_ptr_hi_addr=PATTERN_PTR_HI_ADDR,
    )

    return EngineModel(
        header=header,
        payload_start=data_off,
        payload_bytes=payload,
        relocator_src=RELOCATOR_SRC,
        relocator_len=RELOCATOR_LEN,
        relocator_dst=RELOCATOR_DST,
        routes=routes,
        samples=samples,
        music=music,
        patterns=patterns,
        music_subtunes=music_subtunes,
        instruments=instruments,
    )
