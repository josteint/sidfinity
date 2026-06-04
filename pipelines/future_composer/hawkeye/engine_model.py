"""Engine model + extractor for Hawkeye (FutureComposer V3.x-lineage).

First-cut typed model of the FC engine, scoped to what `RE_NOTES.md`
has verified through trace + disassembly. Walks the binary, decodes
instruments / pattern-pointer table / sequence streams / per-subtune
setup, and returns a single `FCSong` dataclass.

This is the foundation for the USF representation + extract path,
not the byte-exact rebuild yet. The shapes here reflect ONLY
verified facts; everything still uncertain (fx1/fx2/fx3 semantics,
exact sequence-end criteria, glide parameter bytes) is preserved as
raw bytes for later interpretation.

Run as a script to inspect the decoded model:
    python3 pipelines/future_composer/hawkeye/engine_model.py
"""
from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass, field
from typing import Optional


# Verified addresses (RE_NOTES.md → "Data section addresses (Hawkeye)")
ADDR_FREQ_LO_TABLE = 0x8337   # 96 entries
ADDR_FREQ_HI_TABLE = 0x8396   # 96 entries
ADDR_PATTERN_PTR_TABLE = 0x8409  # (lo,hi) per pattern id
ADDR_INSTR_COL1 = 0x8580      # 16 entries
ADDR_INSTR_COL2 = 0x8589      # 16 entries
ADDR_INSTR_RECORDS = 0x860C   # 8 bytes per instrument
ADDR_PER_SUBTUNE_SPEED = 0x83F5  # X-indexed, 1 byte per subtune
ADDR_PER_SUBTUNE_SMC = 0x83FC    # X-indexed, 1 byte per subtune (template lo)
ADDR_PER_SUBTUNE_7BAE = 0x7AFF   # X-indexed, 1 byte per subtune (music=$02, sfx=$00)
ADDR_TEMPLATE_BASE_HI = 0x7B   # template addr = (TEMPLATE_BASE_HI << 8) | smc_lo

# Sequence command byte ranges (verified by L_7C0D/L_7C1F/L_7C31 dispatch)
SEQ_END = 0xFE
SEQ_WRAP = 0xFF
SEQ_TRANSPOSE_RANGE = (0x80, 0xBF)   # AND #$1F → toneadd
SEQ_VOICEINC_RANGE  = (0x60, 0x7F)   # AND #$0F → voiceinc
SEQ_REPEATS_RANGE   = (0x40, 0x5F)   # AND #$3F → repeatsto
SEQ_PATTERN_RANGE   = (0x00, 0x3F)   # ASL → index pattern-ptr table


@dataclass
class Instrument:
    """8-byte FC instrument record (verified at $860C+).

    The 8 raw bytes are preserved; the named fields are the
    interpretation per the research docs (FC V4.1 manual + Cybernoid II
    disassembly). Fx semantics still partly unverified.
    """
    id: int
    raw: bytes                  # 8 bytes
    pulse_hi: int               # +0
    waveform: int               # +1 (ctrl byte: waveform + gate/sync/ring/test)
    ad: int                     # +2 attack/decay
    sr: int                     # +3 sustain/release
    fil_count: int              # +4 filter-table pointer (TBD exact format)
    fx1: int                    # +5 — vibrato-related (TBD)
    fx2: int                    # +6 — arpeggio-related (TBD)
    fx3: int                    # +7 — drum/skydive flags (TBD)


@dataclass
class Sequence:
    """A per-voice sequence stream: bytes consumed left-to-right by
    the engine until $FE (end) or $FF (wrap to start).

    `bytes_raw` is the verbatim source. `parsed` is the decoded
    command-by-command structure (TBD — first pass only stores raw).
    `pattern_ids_used` is the unique pattern ids the sequence
    references (extracted from $00-$3F byte ranges).
    """
    start_addr: int
    bytes_raw: bytes
    pattern_ids_used: list[int]


@dataclass
class Pattern:
    """A pattern stream: bytes consumed left-to-right by the per-voice
    pattern reader until $FF (end). Variable length.

    `bytes_raw` is the verbatim source. `len` is the length to the
    first $FF terminator (inclusive). `notes_count` is the rough
    note count (approx — the dispatch is multi-byte per "note").
    """
    id: int
    start_addr: int
    bytes_raw: bytes
    notes_count_approx: int


@dataclass
class Subtune:
    """Per-subtune setup: which sequence each voice plays + the
    tempo (speedbyte = frames per sequence step)."""
    id: int
    is_sfx: bool                # True if $7AFF+X == $00 (SFX kind)
    speedbyte: int              # frames per sequence step (-1? frames per step?)
    seq_v0_addr: int
    seq_v1_addr: int
    seq_v2_addr: int


@dataclass
class FCSong:
    """The full Hawkeye decoded model."""
    sid_path: str
    load_addr: int
    init_addr: int
    play_addr: int
    psid_songs: int             # raw PSID count (= 12 for Hawkeye)

    freq_table: list[int]       # 96 16-bit PAL freq values
    instruments: list[Instrument]
    pattern_ptr_table: list[int]  # addr per pattern id; truncated when out-of-range
    patterns: dict[int, Pattern]  # patterns referenced by any sequence
    sequences: list[Sequence]   # one per (subtune, voice) pair
    subtunes: list[Subtune]


# ---------------------------------------------------------------------------
# Binary loading helpers
# ---------------------------------------------------------------------------

def _load_psid(sid_path: str) -> tuple[int, int, int, int, bytes]:
    """Return (load_addr, init_addr, play_addr, songs, code_bytes)."""
    with open(sid_path, 'rb') as f:
        d = f.read()
    assert d[:4] == b'PSID', f'expected PSID magic, got {d[:4]!r}'
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    songs = struct.unpack('>H', d[14:16])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return la, init, play, songs, code


def _materialize_memory(load_addr: int, code: bytes) -> bytes:
    """Return a 64K memory image with the code mapped at load_addr."""
    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    return bytes(mem)


# ---------------------------------------------------------------------------
# Decoders
# ---------------------------------------------------------------------------

def _decode_freq_table(mem: bytes) -> list[int]:
    """96-entry PAL freq table at $8337 (lo) / $8396 (hi)."""
    return [
        mem[ADDR_FREQ_LO_TABLE + i] | (mem[ADDR_FREQ_HI_TABLE + i] << 8)
        for i in range(96)
    ]


def _decode_instruments(mem: bytes, count: int = 16) -> list[Instrument]:
    """Decode `count` per-instrument 8-byte records at $860C."""
    out: list[Instrument] = []
    for i in range(count):
        base = ADDR_INSTR_RECORDS + i * 8
        raw = bytes(mem[base:base + 8])
        out.append(Instrument(
            id=i, raw=raw,
            pulse_hi=raw[0], waveform=raw[1], ad=raw[2], sr=raw[3],
            fil_count=raw[4], fx1=raw[5], fx2=raw[6], fx3=raw[7],
        ))
    return out


def _decode_pattern_ptr_table(mem: bytes, load_addr: int, code_len: int,
                               max_patterns: int = 64) -> list[int]:
    """Walk $8409 pattern pointer table; stop at the first pointer that
    falls outside the loaded code region (signals end of table)."""
    out: list[int] = []
    lo_hi_end = load_addr + code_len
    for i in range(max_patterns):
        lo = mem[ADDR_PATTERN_PTR_TABLE + i * 2]
        hi = mem[ADDR_PATTERN_PTR_TABLE + i * 2 + 1]
        addr = lo | (hi << 8)
        if addr < load_addr or addr >= lo_hi_end:
            break
        out.append(addr)
    return out


def _decode_sequence(mem: bytes, start_addr: int,
                     max_bytes: int = 256) -> Sequence:
    """Walk a sequence stream from `start_addr` until $FE (end) or
    $FF (wrap) or `max_bytes` is hit. Collect pattern ids used."""
    raw_buf = bytearray()
    pat_ids: list[int] = []
    seen_pat = set()
    for k in range(max_bytes):
        b = mem[start_addr + k]
        raw_buf.append(b)
        if b == SEQ_END or b == SEQ_WRAP:
            break
        if SEQ_PATTERN_RANGE[0] <= b <= SEQ_PATTERN_RANGE[1]:
            if b not in seen_pat:
                seen_pat.add(b)
                pat_ids.append(b)
    return Sequence(start_addr=start_addr, bytes_raw=bytes(raw_buf),
                    pattern_ids_used=pat_ids)


def _decode_pattern(mem: bytes, pat_id: int, start_addr: int,
                    max_bytes: int = 512) -> Pattern:
    """Walk a pattern stream until $FF terminator or max_bytes.

    notes_count_approx: rough count of "play-note" events (bytes in
    $00-$5F that aren't part of a multi-byte command). Exact decoding
    requires interpreting glide / instr-change / note-length prefixes
    — left for the USF design phase.
    """
    raw_buf = bytearray()
    notes_approx = 0
    skip_next = 0
    for k in range(max_bytes):
        b = mem[start_addr + k]
        raw_buf.append(b)
        if b == 0xFF:
            break
        if skip_next > 0:
            skip_next -= 1
            continue
        hi_nibble = b & 0xF0
        if hi_nibble == 0xE0:
            # glide: 3-byte command sequence (E0, delay, target)
            skip_next = 2
        elif (b & 0xE0) == 0xC0:
            pass  # freq-adjust: single byte
        elif hi_nibble == 0x70:
            pass  # instrument change: single byte
        elif (b & 0xC0) == 0x80:
            pass  # note-length: single byte; followed by a separate note
        elif b == 0xF1:
            skip_next = 1  # filter set: takes one parameter
        else:
            notes_approx += 1
    return Pattern(id=pat_id, start_addr=start_addr,
                   bytes_raw=bytes(raw_buf),
                   notes_count_approx=notes_approx)


def _decode_subtune(mem: bytes, sub_idx: int) -> Subtune:
    """Reconstruct per-subtune setup by replicating sub_7B5A's logic.

    `sub_7B5A` reads:
      A = $83FC,X    (template lo byte)  → SMC at $7B6B
      LDY #5; B9 2C 7B copies 6 bytes from $7B<lo>+0..5 to $8403+0..5
      A = $83F5,X    (speedbyte)         → $7AFE
      A = $7AFF,X    (mode byte)         → $7BAE

    NB: trace showed the raw subtune index isn't always X here —
    $918F apparently translates it. For now we read X = sub_idx
    directly; if disagreements appear vs the actual init trace,
    revisit.
    """
    template_lo = mem[ADDR_PER_SUBTUNE_SMC + sub_idx]
    template_addr = (ADDR_TEMPLATE_BASE_HI << 8) | template_lo
    seq_lo = mem[template_addr + 0:template_addr + 3]
    seq_hi = mem[template_addr + 3:template_addr + 6]
    v0_addr = seq_lo[0] | (seq_hi[0] << 8)
    v1_addr = seq_lo[1] | (seq_hi[1] << 8)
    v2_addr = seq_lo[2] | (seq_hi[2] << 8)
    speedbyte = mem[ADDR_PER_SUBTUNE_SPEED + sub_idx]
    mode = mem[ADDR_PER_SUBTUNE_7BAE + sub_idx]
    is_sfx = (mode == 0x00)
    return Subtune(
        id=sub_idx, is_sfx=is_sfx, speedbyte=speedbyte,
        seq_v0_addr=v0_addr, seq_v1_addr=v1_addr, seq_v2_addr=v2_addr,
    )


# ---------------------------------------------------------------------------
# Top-level extract
# ---------------------------------------------------------------------------

def extract(sid_path: str) -> FCSong:
    """Read Hawkeye (or any FC-V3.x-lineage SID at the same layout)
    and return a fully-decoded `FCSong`."""
    load_addr, init_addr, play_addr, n_songs, code = _load_psid(sid_path)
    mem = _materialize_memory(load_addr, code)

    freq_table = _decode_freq_table(mem)
    instruments = _decode_instruments(mem)
    pattern_ptr_table = _decode_pattern_ptr_table(mem, load_addr, len(code))

    subtunes = [_decode_subtune(mem, s) for s in range(n_songs)]

    # Decode every distinct sequence referenced by the subtune table.
    sequences: list[Sequence] = []
    seq_seen: set[int] = set()
    pat_ids_total: set[int] = set()
    for st in subtunes:
        for addr in (st.seq_v0_addr, st.seq_v1_addr, st.seq_v2_addr):
            if addr in seq_seen:
                continue
            seq_seen.add(addr)
            seq = _decode_sequence(mem, addr)
            sequences.append(seq)
            pat_ids_total.update(seq.pattern_ids_used)

    # Decode patterns that are actually referenced.
    patterns: dict[int, Pattern] = {}
    for pat_id in sorted(pat_ids_total):
        if pat_id >= len(pattern_ptr_table):
            continue
        addr = pattern_ptr_table[pat_id]
        patterns[pat_id] = _decode_pattern(mem, pat_id, addr)

    return FCSong(
        sid_path=sid_path, load_addr=load_addr, init_addr=init_addr,
        play_addr=play_addr, psid_songs=n_songs,
        freq_table=freq_table, instruments=instruments,
        pattern_ptr_table=pattern_ptr_table,
        patterns=patterns, sequences=sequences, subtunes=subtunes,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    sid = os.path.join(root, 'hvsc84', 'MUSICIANS', 'T', 'Tel_Jeroen',
                       'Hawkeye.sid')
    song = extract(sid)

    print(f'Hawkeye: load=${song.load_addr:04X} '
          f'init=${song.init_addr:04X} play=${song.play_addr:04X}')
    print(f'PSID songs: {song.psid_songs}')

    print(f'\nFreq table: 96 entries, first 5 = '
          f'${song.freq_table[0]:04X} ${song.freq_table[1]:04X} '
          f'${song.freq_table[2]:04X} ${song.freq_table[3]:04X} '
          f'${song.freq_table[4]:04X}')
    print(f'  range: ${min(song.freq_table):04X} .. ${max(song.freq_table):04X}')

    print(f'\nInstruments: {len(song.instruments)}')
    for inst in song.instruments:
        if inst.raw == b'\x00' * 8:
            print(f'  inst {inst.id}: <all zero>')
        else:
            print(f'  inst {inst.id}: pulse=${inst.pulse_hi:02X} '
                  f'ctrl=${inst.waveform:02X} AD=${inst.ad:02X} '
                  f'SR=${inst.sr:02X} fil=${inst.fil_count:02X} '
                  f'fx1=${inst.fx1:02X} fx2=${inst.fx2:02X} '
                  f'fx3=${inst.fx3:02X}')

    print(f'\nPattern pointer table: {len(song.pattern_ptr_table)} valid entries')
    print(f'\nReferenced patterns: {len(song.patterns)}')
    for pat_id, pat in sorted(song.patterns.items()):
        print(f'  pat {pat_id:3d} @ ${pat.start_addr:04X}: '
              f'{len(pat.bytes_raw)} bytes, ~{pat.notes_count_approx} notes')

    print(f'\nSubtunes: {song.psid_songs}')
    print(f'{"sub":>3} {"kind":>5} {"speed":>5} {"V0_seq":>7} '
          f'{"V1_seq":>7} {"V2_seq":>7} pat_count')
    for st in song.subtunes:
        kind = 'sfx' if st.is_sfx else 'music'
        pat_count = sum(1 for s in song.sequences
                        if s.start_addr in (st.seq_v0_addr,
                                            st.seq_v1_addr,
                                            st.seq_v2_addr)
                        for p in s.pattern_ids_used)
        print(f'{st.id:>3} {kind:>5} ${st.speedbyte:02X}    '
              f'${st.seq_v0_addr:04X}  ${st.seq_v1_addr:04X}  '
              f'${st.seq_v2_addr:04X}  {pat_count}')

    print(f'\nDistinct sequences: {len(song.sequences)}')
    for s in song.sequences[:10]:
        print(f'  ${s.start_addr:04X}: {len(s.bytes_raw)} bytes, '
              f'{len(s.pattern_ids_used)} distinct patterns: '
              f'{s.pattern_ids_used[:8]}')


if __name__ == '__main__':
    _main()
