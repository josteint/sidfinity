"""Decode a jay_derrett orderlist byte stream into typed rows.

The engine's proc_note classifies each byte as:

  $00..$7F  → NOTE byte. Used as X index into freq_lo/hi tables. The
              freq table is laid out 16 entries per octave (12 notes
              + 4 padding); semantic pitch = (byte >> 4) octave with
              (byte & $0F) semitone (0..11; 12..15 are padding/rest).
  $80       → GATE OFF (write ctrl with gate bit clear).
  $81       → SKIP (no SID writes; pointer advances).
              [Empirically: also other bit-7 bytes that aren't $80 /
               $82..$EF / $FF treated as skip — the dispatch chain
               falls through.]
  $82 N     → SET DURATION. Reads next byte N; writes to per-voice
              duration counter.
  $Bx       → SET TEMPO. Low nibble = new tempo value.
  $Cx       → SET MASTER VOL. Low nibble = $D418 value.
  $Dx       → SET INSTRUMENT. Low nibble = instrument number
              (engine INCs after — index-by-+1 quirk).
  $E0..$E9  → PATTERN_JUMP. The engine's self-mod counter at $C4D3
              starts at $E0 and INCs after each match. The Nth
              `$E(0+N)` byte matches; smaller / larger $Ex are
              treated as skip. So the orderlist stream's $Ex bytes
              must appear in order $E0 → $E1 → ... → $E9, after
              which the counter resets and the song loops. Each $Ex
              maps to a sub-jump table entry indexed by (byte & $0F).
              We treat $E9 as song-end marker (counter reset point).

This is the canonical byte vocabulary for Type A engines. Type B
engines may use a subset / superset — TBD.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Note:
    """A pitched note row.

    `pitch_byte` is the raw byte value (0..127). Decoded octave +
    semitone are convenience fields. Bytes whose `semitone >= 12`
    fall in the freq table's per-octave padding region — engine
    treats them as silent (zero freq) but emits a CTRL gate-on, so
    we still encode them as Notes with a `is_padding` flag for
    downstream awareness.
    """
    pitch_byte: int
    octave: int
    semitone: int        # 0..11 normal, 12..15 padding-region
    is_padding: bool = False


@dataclass
class CmdGateOff:
    pass


@dataclass
class CmdSkip:
    pass


@dataclass
class CmdSetDuration:
    dur: int


@dataclass
class CmdSetTempo:
    tempo: int


@dataclass
class CmdSetVol:
    vol: int


@dataclass
class CmdSetInstrument:
    instrument: int


@dataclass
class CmdPatternJump:
    """A `$E(0+N)` byte. `n` is 0..9; the jump target lives in the
    sub-jump table at `sub_jump_table_addr + n*2` (lo) and `+n*2+1`
    (hi). After the 9th $E in the stream, the engine resets its
    counter and the song loops."""
    n: int


Row = Note | CmdGateOff | CmdSkip | CmdSetDuration | CmdSetTempo \
    | CmdSetVol | CmdSetInstrument | CmdPatternJump


@dataclass
class Pattern:
    """One pattern, identified by the cumulative pattern-jump index
    (0 = the data from initial_ptr to the first $E0; 1 = from the
    sub-jump table entry 1 to the next $E1; etc).

    `start_addr` is where this pattern's bytes begin in memory.
    `rows` is the decoded sequence (ends at the $Ex pattern jump).
    `end_byte_addr` is the address of the terminating $Ex byte.
    """
    n: int
    start_addr: int
    rows: list[Row]
    end_byte_addr: int


def _decode_byte(b: int, follow_byte: int) -> tuple[Row, int]:
    """Decode one byte into a Row. Returns (row, bytes_consumed) where
    `bytes_consumed` is 1 for most rows, 2 for $82 (which has an
    operand byte).

    `follow_byte` is the byte at ptr+1 (used by $82).
    """
    if b < 0x80:
        octave = b >> 4
        semi = b & 0x0F
        return Note(pitch_byte=b, octave=octave, semitone=semi,
                    is_padding=(semi >= 12)), 1
    if b == 0x80:
        return CmdGateOff(), 1
    if b == 0x81:
        return CmdSkip(), 1
    if b == 0x82:
        return CmdSetDuration(dur=follow_byte), 2
    hi = b & 0xF0
    lo = b & 0x0F
    if hi == 0xB0:
        return CmdSetTempo(tempo=lo), 1
    if hi == 0xC0:
        return CmdSetVol(vol=lo), 1
    if hi == 0xD0:
        return CmdSetInstrument(instrument=lo), 1
    if hi == 0xE0:
        return CmdPatternJump(n=lo), 1
    # $83..$AF, $F0..$FF — engine dispatch falls through to skip.
    return CmdSkip(), 1


def decode_voice_orderlist(
        mem: bytearray, initial_ptr: int,
        sub_jump_table_addr: int,
        max_patterns: int = 10,
        max_pattern_bytes: int = 512) -> list[Pattern]:
    """Walk one voice's orderlist starting at `initial_ptr`, follow
    `$Ex` pattern jumps through the sub-jump table, return one
    `Pattern` per $Ex segment.

    Stops when:
      - `max_patterns` reached (default 10 — engine resets the
        self-mod counter at the 10th $E byte and the song loops);
      - a $Ex byte's resolved target has already been visited
        (loop closure detected);
      - the byte counter for a single pattern exceeds
        `max_pattern_bytes` (safety; no $Ex found).
    """
    patterns: list[Pattern] = []
    visited_starts: set[int] = set()
    ptr = initial_ptr
    for n in range(max_patterns):
        if ptr in visited_starts:
            break
        visited_starts.add(ptr)
        rows: list[Row] = []
        pc = ptr
        end_pc = ptr
        for _ in range(max_pattern_bytes):
            if pc >= len(mem):
                break
            b = mem[pc]
            follow = mem[pc + 1] if pc + 1 < len(mem) else 0
            row, ln = _decode_byte(b, follow)
            rows.append(row)
            end_pc = pc
            pc += ln
            if isinstance(row, CmdPatternJump):
                break
        patterns.append(Pattern(n=n, start_addr=ptr, rows=rows,
                                end_byte_addr=end_pc))
        # Resolve next pattern via sub-jump table[n].
        if not rows or not isinstance(rows[-1], CmdPatternJump):
            break  # ran out of bytes before $Ex
        tbl_offset = rows[-1].n * 2
        ptr_lo = mem[sub_jump_table_addr + tbl_offset]
        ptr_hi = mem[sub_jump_table_addr + tbl_offset + 1]
        ptr = ptr_lo | (ptr_hi << 8)
    return patterns
