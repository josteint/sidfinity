"""Dragon's Lair Part II decompiler — pulls structured data out of the
1986 Hubbard engine binary.

This is the first pass of the structural conversion: a pure data
extractor that reads the SID payload and returns a tree of dataclasses
covering everything the engine needs at runtime. No Lean emit yet; no
USF mapping yet. Run as a script to dump everything as JSON for
hand-verification against the annotated disassembly at
`docs/hubbard_dragons_lair_part_ii_disassembly.s`.

Usage:
    python3 -m pipelines.dragons_lair_part_ii.extract.dl2_decompile
    python3 -m pipelines.dragons_lair_part_ii.extract.dl2_decompile --json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SID_PATH = REPO_ROOT / "hvsc84/MUSICIANS/H/Hubbard_Rob/Dragons_Lair_Part_II.sid"

# Anchor addresses from the annotated disassembly. These are hardcoded
# for DL2 specifically; making them auto-discovered comes later if we
# want to share this code with other 1986-engine Hubbards.
FREQ_TABLE_BASE   = 0xC400   # sentinel pair, then 96 (lo,hi) entries
FREQ_TABLE_NOTES  = 96       # 96 semitones indexed 0..95
INSTR1_BASE       = 0xC530   # 28 × 8 bytes (last = all-zero default)
INSTR2_BASE       = 0xC610   # 28 × 8 bytes
N_INSTRUMENTS     = 28
SPEED_TABLE       = 0xC4ED   # 10 bytes, indexed by internal subtune A
PHASE_TABLE       = 0xC4F7   # 10 bytes (also patched into $C06A operand)
SONG_HEAD_BASE    = 0xC6F6   # 10 × 6 bytes per subtune
N_SUBTUNES        = 10
PAT_PTR_LO        = 0xC732   # pattern LO byte at $C732+i
PAT_PTR_HI        = 0xC7B4   # pattern HI byte at $C7B4+i
# The pattern-pointer table has no explicit length; it's just bytes the
# play loop reads via `LDA $c732,y / LDA $c7b4,y` where Y is the
# orderlist value (excluding $FE/$FF). The actual count is one more
# than the highest pattern id any orderlist references.
VOICE_BASES       = 0xC4C4   # 3 bytes: D400 offsets for V1/V2/V3 = 0,7,14
DEFAULT_INSTR     = 0x1B     # 27 — the all-zero instrument used at first-frame

# Self-modifying init's two tables (PSID → internal A):
#   PSID#1 →9, #2→7, #3→1, #4→6, #5→4, #6→2, #7→3, #8→0, #9→5, #10→8.
# Derived in the init dispatcher ($AF00..$AF4A), table at $AF80/$AF88.
SUBTUNE_PERMUTATION_PSID_TO_INTERNAL = {
    1: 9, 2: 7, 3: 1, 4: 6, 5: 4,
    6: 2, 7: 3, 8: 0, 9: 5, 10: 8,
}


# ============================================================================
# Dataclasses (raw structural — engine bytes preserved verbatim)
# ============================================================================

@dataclass
class Instrument:
    """A single instrument as the 1986 engine sees it: two 8-byte records.

    Table 1 ($C530+8*i): pulse_lo, pulse_hi, ctrl_wave, ad, sr,
                          pulse_mod_cfg, arp_offset, fx_flags.
    Table 2 ($C610+8*i): alt_wave_A, vibrato_src, noise_wave, reserved,
                          release_wave, pulse_speed_packed, filter_res,
                          filter_delta.
    """
    id: int
    # Table 1
    pulse_lo: int
    pulse_hi: int
    ctrl_wave: int
    ad: int
    sr: int
    pulse_mod_cfg: int   # bits 6..3 = pulse_max, bits 2..0 = pulse shift
    arp_offset: int       # value added each frame to current note
    fx_flags: int         # bit-mask routing into the 8 fx blocks
    # Table 2
    alt_wave_A: int
    vibrato_src: int
    noise_wave: int
    reserved: int
    release_wave: int
    pulse_speed_packed: int   # lo nibble = pulse delta, hi nibble = pulse max
    filter_res: int
    filter_delta: int

    @property
    def pulse_width(self) -> int:
        return self.pulse_lo | (self.pulse_hi << 8)

    @property
    def is_default_silent(self) -> bool:
        """The default instrument ($1B = 27) is all zeros in both tables."""
        return (
            self.pulse_lo == 0 and self.pulse_hi == 0 and self.ctrl_wave == 0
            and self.ad == 0 and self.sr == 0 and self.pulse_mod_cfg == 0
            and self.arp_offset == 0 and self.fx_flags == 0
            and self.alt_wave_A == 0 and self.vibrato_src == 0
            and self.noise_wave == 0 and self.release_wave == 0
            and self.pulse_speed_packed == 0 and self.filter_res == 0
            and self.filter_delta == 0
        )


@dataclass
class PatternRow:
    """A single decoded row from a pattern.

    See `docs/hubbard_dragons_lair_part_ii_disassembly.s` for the bit
    semantics. Byte layout in source is 1..4 bytes; the decoded fields:

      duration    : frames the row holds (low 5 bits of raw byte).
      tie         : raw bit 6 — keep previous note, clear gate.
      has_secondary: raw bit 7 — secondary byte (instr/cmd) follows.
      instrument  : new instrument index, or None if not set.
      cmd_byte    : raw secondary byte for command rows (bit 7 set on
                    secondary). Engine consumes the value-after but
                    discards it.
      cmd_extra   : the discarded byte after a command secondary (4-byte
                    row only).
      note        : note byte (None on a pure tie row).
    """
    duration: int
    tie: bool
    has_secondary: bool
    instrument: int | None
    cmd_byte: int | None
    cmd_extra: int | None
    note: int | None
    raw_bytes: list[int]


@dataclass
class Pattern:
    """A pattern: byte range in source + decoded rows."""
    id: int
    addr: int                  # source address of first byte
    raw: list[int]             # raw bytes including the terminating $FF
    rows: list[PatternRow]
    end_byte_addr: int         # address of the $FF terminator


@dataclass
class Subtune:
    """A subtune's per-voice orderlists + tempo state."""
    psid_index: int            # 1..10
    internal_index: int        # 0..9 after the permutation
    speed_reload: int          # $C501 = $C4ED[A]
    phase_reload: int          # $C502 = $C4F7[A], also patched into $C06A
    voice_orderlist_addr: list[int]   # 3 addresses (V1/V2/V3)
    voice_orderlist: list[list[int]]  # 3 byte streams, terminated by $FE/$FF


@dataclass
class DragonsLairPartII:
    title: str
    author: str
    released: str
    psid_init: int
    psid_play: int
    psid_load: int
    psid_songs: int
    psid_start_song: int
    psid_flags: int
    freq_table: list[tuple[int, int]]    # (lo,hi) — index 0 = sentinel, then 96 notes
    instruments: list[Instrument]
    pattern_pointers: list[int]          # 128 entries: pattern[i] address (or 0 if unused)
    patterns: list[Pattern]              # only those reached by ANY subtune
    subtunes: list[Subtune]              # 10 entries indexed by internal A


# ============================================================================
# PSID parse
# ============================================================================

def parse_psid(blob: bytes) -> dict:
    assert blob[:4] == b"PSID", "not a PSID file"
    data_off = int.from_bytes(blob[6:8], "big")
    load_hdr = int.from_bytes(blob[8:10], "big")
    init = int.from_bytes(blob[10:12], "big")
    play = int.from_bytes(blob[12:14], "big")
    songs = int.from_bytes(blob[14:16], "big")
    start = int.from_bytes(blob[16:18], "big")
    flags = int.from_bytes(blob[118:120], "big") if data_off >= 0x7C else 0
    title = blob[22:54].rstrip(b"\0").decode("latin-1")
    author = blob[54:86].rstrip(b"\0").decode("latin-1")
    released = blob[86:118].rstrip(b"\0").decode("latin-1")
    payload = blob[data_off:]
    if load_hdr == 0:
        load = payload[0] | (payload[1] << 8)
        binary = payload[2:]
    else:
        load = load_hdr
        binary = payload
    return dict(
        title=title, author=author, released=released,
        init=init, play=play, load=load, songs=songs, start=start, flags=flags,
        binary=binary,
    )


class Mem:
    """Read-only address-keyed view of the binary."""
    def __init__(self, binary: bytes, load: int):
        self.binary = binary
        self.load = load
        self.end = load + len(binary)

    def byte(self, addr: int) -> int:
        if addr < self.load or addr >= self.end:
            raise IndexError(f"address ${addr:04X} out of range")
        return self.binary[addr - self.load]

    def bytes(self, addr: int, n: int) -> list[int]:
        return [self.byte(addr + i) for i in range(n)]


# ============================================================================
# Decoders
# ============================================================================

def extract_freq_table(mem: Mem) -> list[tuple[int, int]]:
    """Sentinel pair + 96 notes."""
    out: list[tuple[int, int]] = []
    for i in range(FREQ_TABLE_NOTES + 1):
        lo = mem.byte(FREQ_TABLE_BASE + 2 * i)
        hi = mem.byte(FREQ_TABLE_BASE + 2 * i + 1)
        out.append((lo, hi))
    return out


def extract_instruments(mem: Mem) -> list[Instrument]:
    insts: list[Instrument] = []
    for i in range(N_INSTRUMENTS):
        t1 = mem.bytes(INSTR1_BASE + 8 * i, 8)
        t2 = mem.bytes(INSTR2_BASE + 8 * i, 8)
        insts.append(Instrument(
            id=i,
            pulse_lo=t1[0], pulse_hi=t1[1], ctrl_wave=t1[2],
            ad=t1[3], sr=t1[4], pulse_mod_cfg=t1[5],
            arp_offset=t1[6], fx_flags=t1[7],
            alt_wave_A=t2[0], vibrato_src=t2[1], noise_wave=t2[2],
            reserved=t2[3], release_wave=t2[4],
            pulse_speed_packed=t2[5], filter_res=t2[6], filter_delta=t2[7],
        ))
    return insts


def decode_pattern_rows(raw: list[int]) -> list[PatternRow]:
    """Decode a pattern's row stream (everything except the final $FF).

    The 1/2/3/4-byte row decoder follows the play loop at $C0E4..$C113
    in the annotated disassembly.
    """
    rows: list[PatternRow] = []
    i = 0
    n = len(raw)
    while i < n:
        d = raw[i]
        tie = bool(d & 0x40)
        has_sec = bool(d & 0x80)
        duration = d & 0x1F
        if tie:
            # 1-byte row: just duration + clear-gate flag, no new note.
            rows.append(PatternRow(
                duration=duration, tie=True, has_secondary=False,
                instrument=None, cmd_byte=None, cmd_extra=None, note=None,
                raw_bytes=[d],
            ))
            i += 1
            continue
        if not has_sec:
            # 2-byte row: duration + note.
            if i + 1 >= n:
                break
            note = raw[i + 1]
            rows.append(PatternRow(
                duration=duration, tie=False, has_secondary=False,
                instrument=None, cmd_byte=None, cmd_extra=None,
                note=note, raw_bytes=[d, note],
            ))
            i += 2
            continue
        # bit 7 set: secondary byte follows.
        if i + 1 >= n:
            break
        sec = raw[i + 1]
        if not (sec & 0x80):
            # 3-byte row: duration + instrument + note.
            if i + 2 >= n:
                break
            note = raw[i + 2]
            rows.append(PatternRow(
                duration=duration, tie=False, has_secondary=True,
                instrument=sec, cmd_byte=None, cmd_extra=None,
                note=note, raw_bytes=[d, sec, note],
            ))
            i += 3
        else:
            # 4-byte row: duration + cmd + extra + note (extra is consumed
            # but ignored by the play loop — preserved here for round-trip).
            if i + 3 >= n:
                break
            extra = raw[i + 2]
            note = raw[i + 3]
            rows.append(PatternRow(
                duration=duration, tie=False, has_secondary=True,
                instrument=None, cmd_byte=sec, cmd_extra=extra,
                note=note, raw_bytes=[d, sec, extra, note],
            ))
            i += 4
    return rows


def extract_pattern(mem: Mem, pat_id: int, addr: int) -> Pattern:
    """Read pattern bytes from `addr` up to and including the first $FF."""
    raw: list[int] = []
    cur = addr
    max_len = 4096   # sanity bound
    while cur - addr < max_len:
        b = mem.byte(cur)
        raw.append(b)
        cur += 1
        if b == 0xFF:
            break
    else:
        raise RuntimeError(f"pattern {pat_id} @ ${addr:04X} ran past sanity bound")
    body = raw[:-1]   # strip $FF
    rows = decode_pattern_rows(body)
    # Round-trip self-check: re-serialize the decoded rows + $FF and
    # confirm it matches the original byte stream. Catches any decoder
    # off-by-one before the data leaves this layer.
    rt = [b for row in rows for b in row.raw_bytes] + [0xFF]
    if rt != raw:
        raise RuntimeError(
            f"pattern {pat_id} @ ${addr:04X} round-trip mismatch:\n"
            f"  original: {raw}\n"
            f"  rebuilt : {rt}"
        )
    return Pattern(id=pat_id, addr=addr, raw=raw, rows=rows, end_byte_addr=cur - 1)


def extract_orderlist(mem: Mem, start_addr: int) -> list[int]:
    """Read the orderlist byte stream starting at `start_addr`.

    Stops on (and includes) the first $FF (wrap) or $FE (end-of-song),
    or after 256 bytes as a sanity bound.
    """
    out: list[int] = []
    addr = start_addr
    for _ in range(256):
        b = mem.byte(addr)
        out.append(b)
        addr += 1
        if b in (0xFE, 0xFF):
            return out
    return out


def extract_subtunes(mem: Mem) -> list[Subtune]:
    subs: list[Subtune] = []
    for psid_idx in range(1, N_SUBTUNES + 1):
        A = SUBTUNE_PERMUTATION_PSID_TO_INTERNAL[psid_idx]
        head = mem.bytes(SONG_HEAD_BASE + A * 6, 6)
        v_addr = [head[0] | (head[3] << 8),
                  head[1] | (head[4] << 8),
                  head[2] | (head[5] << 8)]
        v_orderlist = [extract_orderlist(mem, a) for a in v_addr]
        subs.append(Subtune(
            psid_index=psid_idx,
            internal_index=A,
            speed_reload=mem.byte(SPEED_TABLE + A),
            phase_reload=mem.byte(PHASE_TABLE + A),
            voice_orderlist_addr=v_addr,
            voice_orderlist=v_orderlist,
        ))
    return subs


def collect_referenced_pattern_ids(subtunes: list[Subtune]) -> set[int]:
    """Set of pattern indices reachable from any subtune × any voice."""
    seen: set[int] = set()
    for s in subtunes:
        for stream in s.voice_orderlist:
            for b in stream:
                if b in (0xFE, 0xFF):
                    continue
                seen.add(b)
    return seen


def decompile(blob: bytes) -> DragonsLairPartII:
    info = parse_psid(blob)
    mem = Mem(info["binary"], info["load"])

    freq = extract_freq_table(mem)
    insts = extract_instruments(mem)
    subtunes = extract_subtunes(mem)
    used_ids = collect_referenced_pattern_ids(subtunes)
    n_pattern_slots = max(used_ids) + 1 if used_ids else 0

    # Pattern pointer table (LO at $C732, HI at $C7B4). Size is implicit.
    pattern_pointers: list[int] = []
    for i in range(n_pattern_slots):
        lo = mem.byte(PAT_PTR_LO + i)
        hi = mem.byte(PAT_PTR_HI + i)
        addr = lo | (hi << 8)
        # Sanity-check: HI in the binary range, else table likely shorter.
        if not (mem.load <= addr < mem.end):
            raise RuntimeError(
                f"pattern[{i}] ptr ${addr:04X} outside binary range "
                f"${mem.load:04X}..${mem.end-1:04X} — table size guess wrong"
            )
        pattern_pointers.append(addr)

    patterns: list[Pattern] = []
    for i in sorted(used_ids):
        addr = pattern_pointers[i]
        patterns.append(extract_pattern(mem, i, addr))

    return DragonsLairPartII(
        title=info["title"], author=info["author"], released=info["released"],
        psid_init=info["init"], psid_play=info["play"], psid_load=info["load"],
        psid_songs=info["songs"], psid_start_song=info["start"], psid_flags=info["flags"],
        freq_table=freq,
        instruments=insts,
        pattern_pointers=pattern_pointers,
        patterns=patterns,
        subtunes=subtunes,
    )


# ============================================================================
# CLI / debug dump
# ============================================================================

def _summary(song: DragonsLairPartII) -> str:
    lines = [
        f"Dragon's Lair Part II — structural decompile",
        f"  title:     {song.title!r}",
        f"  author:    {song.author!r}",
        f"  released:  {song.released!r}",
        f"  load=${song.psid_load:04X}  init=${song.psid_init:04X}  play=${song.psid_play:04X}",
        f"  songs={song.psid_songs}  start={song.psid_start_song}  flags=${song.psid_flags:04X}",
        f"  freq table: 1 sentinel + {FREQ_TABLE_NOTES} notes "
        f"(sentinel={song.freq_table[0]}, note0={song.freq_table[1]}, "
        f"note95={song.freq_table[FREQ_TABLE_NOTES]})",
        f"  instruments: {N_INSTRUMENTS} entries "
        f"({sum(1 for i in song.instruments if i.is_default_silent)} silent/default)",
        f"  pattern slots: {len(song.pattern_pointers)} (0..{len(song.pattern_pointers)-1});"
        f" {len(song.patterns)} referenced by orderlists",
        f"  pattern bytes total: "
        f"{sum(len(p.raw) for p in song.patterns)} "
        f"(including each pattern's terminating $FF)",
    ]
    lines.append("  per-subtune:")
    for s in song.subtunes:
        ol_lens = [len(s.voice_orderlist[v]) for v in range(3)]
        lines.append(
            f"    PSID#{s.psid_index:>2} (internal A={s.internal_index}): "
            f"speed=${s.speed_reload:02X} phase=${s.phase_reload:02X} "
            f"V1@${s.voice_orderlist_addr[0]:04X}({ol_lens[0]}b) "
            f"V2@${s.voice_orderlist_addr[1]:04X}({ol_lens[1]}b) "
            f"V3@${s.voice_orderlist_addr[2]:04X}({ol_lens[2]}b)"
        )
    # Used instrument ids per subtune (scanned from pattern rows).
    inst_use = {s.psid_index: set() for s in song.subtunes}
    pat_lookup = {p.id: p for p in song.patterns}
    for s in song.subtunes:
        for stream in s.voice_orderlist:
            for b in stream:
                if b in (0xFE, 0xFF):
                    continue
                for row in pat_lookup[b].rows:
                    if row.instrument is not None:
                        inst_use[s.psid_index].add(row.instrument)
    lines.append("  instruments referenced per PSID# (excluding default $1B):")
    for psid_idx, ids in inst_use.items():
        ids = sorted(i for i in ids if i != DEFAULT_INSTR)
        lines.append(f"    PSID#{psid_idx:>2}: {ids}")
    return "\n".join(lines)


def _to_json(song: DragonsLairPartII) -> dict:
    """Strip raw_bytes from rows (already implied by raw)."""
    d = asdict(song)
    return d


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true",
                        help="dump everything as JSON to stdout")
    parser.add_argument("--pattern", type=int, metavar="ID",
                        help="dump rows of a single pattern ID")
    args = parser.parse_args()
    blob = SID_PATH.read_bytes()
    song = decompile(blob)
    if args.pattern is not None:
        pat = next((p for p in song.patterns if p.id == args.pattern), None)
        if pat is None:
            print(f"pattern {args.pattern} not referenced by any subtune")
            return 1
        print(f"Pattern ${args.pattern:02X} @ ${pat.addr:04X} ({len(pat.raw)} bytes)")
        for ri, r in enumerate(pat.rows):
            print(f"  row {ri:>3}: {r}")
        return 0
    if args.json:
        print(json.dumps(_to_json(song), indent=2, default=str))
        return 0
    print(_summary(song))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
