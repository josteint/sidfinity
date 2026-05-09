"""Generic structure discovery for SID files.

Goal: given a SID, build a complete map of which bytes are code, which
are data tables, and what role each table plays — without using
engine-specific knowledge.

Inputs the discoverer is allowed to use:
  - The PSID header (load_addr, init_addr, play_addr) — standard format,
    not engine-specific.
  - The raw payload bytes.
  - A siddump --memtrace of the SID running for some duration.

It is NOT allowed to use:
  - Knowledge of the engine (Hubbard / GT2 / DMC / etc.)
  - rh_decompile / gt2_decompile output
  - Hand-coded layout assumptions

Three layers of evidence:
  1. Static: recursive-descent disassembly from (init, play) marks all
     reachable bytes as CODE; the addresses of operands of `LDA abs(,X)`,
     `STA abs(,X)`, etc. point at data tables.
  2. Dynamic: the memtrace gives access counts per address — confirms
     which data was actually used in this trace, and at what frequency.
  3. Roles: SID register writes ($D400-$D41C) tell us what the data
     adjacent to those writes represents (write to $D404,X with a value
     loaded from $XXXX,X → $XXXX is a per-voice ctrl table; etc).

Usage:
    python3 src/sidxray/discover.py <sid_file>
"""

import os
import re
import sys
import struct
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
from code_flow import trace_code, _INST_LEN, _BRANCHES


# --- 6502 addressing-mode tables for operand classification --------------

# Opcodes that take a 2-byte absolute or absolute,X / absolute,Y operand,
# and whose operand IS the address being loaded/stored from data memory
# (NOT the target of a JMP/JSR — those are control flow, handled elsewhere).
_DATA_ABS_OPCODES = {
    # LDA / LDX / LDY abs / abs,X / abs,Y
    0xAD, 0xBD, 0xB9,  # LDA abs / abs,X / abs,Y
    0xAE, 0xBE,        # LDX abs / abs,Y
    0xAC, 0xBC,        # LDY abs / abs,X
    # STA / STX / STY abs / abs,X / abs,Y
    0x8D, 0x9D, 0x99,  # STA
    0x8E,              # STX abs
    0x8C,              # STY abs
    # ADC / SBC / AND / ORA / EOR / CMP / CPX / CPY abs(,X)(,Y)
    0x6D, 0x7D, 0x79,  # ADC
    0xED, 0xFD, 0xF9,  # SBC
    0x2D, 0x3D, 0x39,  # AND
    0x0D, 0x1D, 0x19,  # ORA
    0x4D, 0x5D, 0x59,  # EOR
    0xCD, 0xDD, 0xD9,  # CMP
    0xEC,              # CPX abs
    0xCC,              # CPY abs
    # ASL / LSR / ROL / ROR / INC / DEC abs(,X)
    0x0E, 0x1E, 0x4E, 0x5E, 0x2E, 0x3E, 0x6E, 0x7E,
    0xEE, 0xFE, 0xCE, 0xDE,
}

# SID register addresses
SID_BASE = 0xD400
SID_END = 0xD41C  # inclusive, last writable register


def parse_psid_header(sid_path: str) -> dict:
    """Read PSID header. Returns dict with load_addr, init_addr,
    play_addr, payload, payload_offset_in_file."""
    with open(sid_path, 'rb') as f:
        data = f.read()
    magic = data[0:4]
    assert magic in (b'PSID', b'RSID'), f'Not a PSID/RSID: {magic!r}'
    data_offset = struct.unpack('>H', data[0x06:0x08])[0]
    load = struct.unpack('>H', data[0x08:0x0A])[0]
    init = struct.unpack('>H', data[0x0A:0x0C])[0]
    play = struct.unpack('>H', data[0x0C:0x0E])[0]
    if load == 0:
        # load is little-endian at start of data
        load = data[data_offset] | (data[data_offset + 1] << 8)
        payload = data[data_offset + 2:]
    else:
        payload = data[data_offset:]
    return {
        'load_addr': load, 'init_addr': init, 'play_addr': play,
        'payload': payload, 'load_end': load + len(payload) - 1,
    }


# --- Memtrace parsing ---------------------------------------------------

_MEMTRACE_PAT = re.compile(r'([0-9A-F]{4})=([0-9A-F]{2})')


def parse_memtrace(path: str) -> tuple[dict[int, int], int]:
    """Parse a memtrace file into per-address access counts. Also returns
    frame count (one frame per line)."""
    counts: dict[int, int] = defaultdict(int)
    frames = 0
    with open(path) as f:
        for line in f:
            frames += 1
            for m in _MEMTRACE_PAT.finditer(line):
                addr = int(m.group(1), 16)
                counts[addr] += 1
    return counts, frames


def ensure_memtrace(sid_path: str, duration: int = 30) -> str:
    """Capture (if missing) and return path to memtrace file."""
    base = os.path.basename(sid_path).replace('.sid', '')
    out = f'/tmp/{base}_memtrace.txt'
    if not os.path.exists(out):
        os.system(f'/home/jtr/sidfinity/tools/siddump "{sid_path}" '
                  f'--memtrace --duration {duration} --raw > "{out}" 2>/dev/null')
    return out


# --- Static analysis: data references inside code -----------------------

@dataclass
class DataRef:
    site_addr: int       # address of the instruction
    opcode: int
    target_addr: int     # absolute operand
    indexed: str         # '', 'X', or 'Y'
    is_write: bool       # STA/STX/STY/INC/DEC = write
    is_sid: bool         # target in $D400-$D41C


_INDEXED_X = {0xBD, 0xBC, 0x9D, 0x7D, 0xFD, 0x3D, 0x1D, 0x5D, 0xDD,
              0x1E, 0x5E, 0x3E, 0x7E, 0xFE, 0xDE}
_INDEXED_Y = {0xB9, 0xBE, 0x99, 0x79, 0xF9, 0x39, 0x19, 0x59, 0xD9}
_WRITE_OPS = {0x8D, 0x9D, 0x99, 0x8E, 0x8C, 0x0E, 0x1E, 0x4E, 0x5E,
              0x2E, 0x3E, 0x6E, 0x7E, 0xEE, 0xFE, 0xCE, 0xDE}


def trace_code_with_refs(payload: bytes, load_addr: int,
                         init_addr: int, play_addr: int) -> tuple[set[int], list[DataRef]]:
    """Like code_flow.trace_code but also collects every data-reference
    operand encountered in code."""
    code_bytes: set[int] = set()
    refs: list[DataRef] = []
    visited: set[int] = set()
    worklist: list[int] = []
    for addr in (init_addr, play_addr):
        off = addr - load_addr
        if 0 <= off < len(payload):
            worklist.append(off)
    n = len(payload)

    while worklist:
        pos = worklist.pop()
        if pos in visited or not (0 <= pos < n):
            continue
        visited.add(pos)
        op = payload[pos]
        ilen = _INST_LEN[op]
        if pos + ilen > n:
            continue
        for b in range(pos, pos + ilen):
            code_bytes.add(b)

        # Record data reference if this op takes an absolute operand
        if op in _DATA_ABS_OPCODES:
            target = payload[pos + 1] | (payload[pos + 2] << 8)
            indexed = 'X' if op in _INDEXED_X else ('Y' if op in _INDEXED_Y else '')
            refs.append(DataRef(
                site_addr=load_addr + pos,
                opcode=op,
                target_addr=target,
                indexed=indexed,
                is_write=op in _WRITE_OPS,
                is_sid=(SID_BASE <= target <= SID_END),
            ))

        # Control flow
        if op in (0x60, 0x40, 0x00):  # RTS / RTI / BRK
            continue
        if op == 0x4C:  # JMP abs
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            t_off = tgt - load_addr
            if 0 <= t_off < n:
                worklist.append(t_off)
            continue
        if op == 0x6C:  # JMP indirect — can't resolve
            continue
        if op == 0x20:  # JSR
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            t_off = tgt - load_addr
            if 0 <= t_off < n:
                worklist.append(t_off)
            worklist.append(pos + ilen)
            continue
        if op in _BRANCHES:
            offset = payload[pos + 1]
            if offset >= 0x80:
                offset -= 0x100
            t_off = pos + ilen + offset
            if 0 <= t_off < n:
                worklist.append(t_off)
            worklist.append(pos + ilen)
            continue
        worklist.append(pos + ilen)

    return code_bytes, refs


# --- Region inference ---------------------------------------------------

@dataclass
class TableHypothesis:
    base_addr: int               # where the table starts
    indexed_by: str              # 'X' or 'Y'
    sid_register_writes: set[int] = field(default_factory=set)  # which SID regs are written from this table's data
    read_sites: set[int] = field(default_factory=set)
    write_sites: set[int] = field(default_factory=set)
    runtime_count: int = 0       # accesses observed in trace
    role_guess: str = '?'


def infer_tables(refs: list[DataRef], counts: dict[int, int],
                 load_lo: int, load_hi: int) -> dict[int, TableHypothesis]:
    """For every distinct (target_addr, indexed) combination found in
    code, build a TableHypothesis. Group by target_addr (the base of
    the table)."""
    tables: dict[int, TableHypothesis] = {}
    # Also track sequencing: when an LDA xxx,X is followed by STA $D4yy,Y
    # within the same basic block, we have evidence the table feeds a
    # specific SID register. We'll do a lightweight version: pair each
    # data-LOAD ref with the next data-WRITE ref to a SID register in
    # the same code-flow neighbourhood. For now just record indices.

    # Build by-target-address grouping for all loads-with-index
    for ref in refs:
        if not (load_lo <= ref.target_addr <= load_hi):
            continue  # external (zeropage, SID, OS) — skip for now
        if ref.indexed == '':
            continue  # plain abs reads — useful but harder to interpret
        t = tables.setdefault(ref.target_addr, TableHypothesis(
            base_addr=ref.target_addr, indexed_by=ref.indexed))
        if ref.is_write:
            t.write_sites.add(ref.site_addr)
        else:
            t.read_sites.add(ref.site_addr)

    # Annotate with runtime access counts (sum across all bytes in the
    # potential table region — we don't know its size yet; use a
    # window of 256 bytes as a rough upper bound).
    for base, t in tables.items():
        t.runtime_count = sum(counts.get(a, 0) for a in range(base, min(base + 256, load_hi + 1)))

    # Role guesses from neighboring SID register writes in code
    # (lightweight pairing — full version would do dataflow analysis)
    # For now we associate sid_register_writes per ref site that's
    # adjacent to a SID-write site. We emit a generic hint.
    return tables


# --- Pretty print -------------------------------------------------------

def role_from_sid_register(reg_low: int) -> str:
    """SID register offset → likely role of data being written to it."""
    voice_off = reg_low % 7
    if reg_low == 0x18: return 'volume'
    if reg_low in (0x15, 0x16): return 'filter_cutoff'
    if reg_low == 0x17: return 'filter_ctrl'
    if voice_off == 0: return 'freq_lo'
    if voice_off == 1: return 'freq_hi'
    if voice_off == 2: return 'pulse_lo'
    if voice_off == 3: return 'pulse_hi'
    if voice_off == 4: return 'ctrl'
    if voice_off == 5: return 'attack_decay'
    if voice_off == 6: return 'sustain_release'
    return f'sid_${reg_low:02X}'


def estimate_table_sizes(tables: dict[int, 'TableHypothesis'],
                          counts: dict[int, int],
                          code_offsets: set[int],
                          load_addr: int, load_end: int) -> dict[int, dict]:
    """For each table base, estimate its size using:
      - Upper bound: distance to the next non-overlapping data region or
        the next reachable code byte.
      - Lower bound: max offset at which the table was actually accessed
        in the runtime trace (gives us "at least this big").
      - Field-cluster detection: bases within 16 bytes of each other are
        grouped as a single struct. The struct's record size is the
        cluster's span; the record count is what `lower_bound / span`
        suggests.

    Returns dict keyed by base addr with:
      {'upper': int, 'lower': int, 'cluster_id': int, 'record_size': int|None,
       'record_count': int|None}
    """
    bases = sorted(tables.keys())
    out: dict[int, dict] = {}

    # Form clusters: consecutive bases ≤ 16 bytes apart are one cluster.
    CLUSTER_GAP = 16
    cluster_id = 0
    cluster_of: dict[int, int] = {}
    cluster_members: dict[int, list[int]] = defaultdict(list)
    if bases:
        cluster_of[bases[0]] = 0
        cluster_members[0].append(bases[0])
        for i in range(1, len(bases)):
            if bases[i] - bases[i-1] <= CLUSTER_GAP:
                cluster_of[bases[i]] = cluster_id
            else:
                cluster_id += 1
                cluster_of[bases[i]] = cluster_id
            cluster_members[cluster_of[bases[i]]].append(bases[i])

    # For each cluster, determine the cluster's span (last_base - first_base + 1
    # = field-record-size estimate) and the cluster's upper bound (until next
    # cluster's first base or next code byte).
    cluster_first: dict[int, int] = {}
    cluster_last: dict[int, int] = {}
    for cid, members in cluster_members.items():
        cluster_first[cid] = min(members)
        cluster_last[cid] = max(members)

    sorted_clusters = sorted(cluster_members.keys(),
                             key=lambda c: cluster_first[c])

    for ci, cid in enumerate(sorted_clusters):
        first = cluster_first[cid]
        last = cluster_last[cid]
        # Upper bound: next cluster's first OR next code byte after `last`
        next_cluster_first = (cluster_first[sorted_clusters[ci+1]]
                              if ci + 1 < len(sorted_clusters) else load_end + 1)
        # Find next code byte ≥ last+1
        next_code_addr = None
        for pos in range(last - load_addr + 1, len(code_offsets) + (load_end - load_addr) + 1):
            if pos in code_offsets and load_addr + pos > last:
                next_code_addr = load_addr + pos
                break
        # Both upper bounds, take the smaller (= more restrictive)
        ub_addr = next_cluster_first
        if next_code_addr is not None and next_code_addr < ub_addr:
            ub_addr = next_code_addr
        # Cluster's "table region" = first..ub_addr-1
        cluster_span = ub_addr - first

        # Record size estimate (only meaningful for multi-base clusters):
        #   = (last - first + 1)  → the byte distance covered by the field bases
        record_size = (last - first + 1) if len(cluster_members[cid]) > 1 else None

        # Record count from runtime accesses: max accessed offset within
        # the cluster region, divided by record_size (or just max offset+1
        # if single-base table).
        max_offset = -1
        for off in range(cluster_span):
            if counts.get(first + off, 0) > 0:
                max_offset = off
        runtime_extent = max_offset + 1 if max_offset >= 0 else 0

        if record_size and record_size > 0:
            record_count = runtime_extent // record_size + (1 if runtime_extent % record_size else 0)
        else:
            record_count = runtime_extent

        for base in cluster_members[cid]:
            out[base] = {
                'upper': cluster_span,
                'lower': max(0, runtime_extent - (base - first)),
                'cluster_id': cid,
                'cluster_first': first,
                'cluster_span': cluster_span,
                'record_size': record_size,
                'record_count': record_count,
            }

    return out


def trace_sid_dataflow(payload: bytes, load_addr: int,
                       init_addr: int, play_addr: int) -> dict[int, set[str]]:
    """For each data-table base address referenced by code, identify
    which SID registers receive values loaded from that table.

    Method: re-walk control flow tracking the "current source" of A
    through linear code. When A is loaded from table T (LDA T,X / T,Y
    / T), record T as source. When A is stored to a SID register R via
    STA, attribute R to T. Resets on flow boundaries (branch / call /
    AND/ORA/EOR/ADC/SBC/etc. that mix in other sources are conservative
    "still T" — we accept that the data still came from T modulo
    arithmetic).

    Returns: {table_base_addr: {role_label, ...}} where each label is
    the SID register the data feeds.
    """
    sources: dict[int, set[str]] = defaultdict(set)
    visited: set[int] = set()
    # State per code position: address of last LDA-from-table source
    # (None if A's source is not a table).
    worklist: list[tuple[int, int | None]] = []
    for addr in (init_addr, play_addr):
        off = addr - load_addr
        if 0 <= off < len(payload):
            worklist.append((off, None))
    n = len(payload)
    sid_lo, sid_hi = SID_BASE, SID_END

    # Visited as (pos, a_source) — different sources may produce different
    # downstream attribution. To keep the walk bounded, collapse to just
    # `pos in visited` after first visit (loses some precision; acceptable).
    while worklist:
        pos, src = worklist.pop()
        if pos in visited or not (0 <= pos < n):
            continue
        visited.add(pos)
        op = payload[pos]
        ilen = _INST_LEN[op]
        if pos + ilen > n:
            continue

        # LDA / LDX / LDY abs / abs,X / abs,Y → A (or X/Y) source becomes target table
        if op in (0xAD, 0xBD, 0xB9):  # LDA abs / abs,X / abs,Y
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            new_src = tgt if (load_addr <= tgt <= load_addr + n - 1) else None
            src = new_src
        elif op == 0xA9:  # LDA #imm
            src = None
        elif op in (0xAA, 0xA8):  # TAX, TAY — A's source still drives downstream
            pass
        elif op in (0xAE, 0xBE, 0xAC, 0xBC):  # LDX/LDY abs(,Y)/(,X) — clobbers index, not A
            pass
        # STA abs / abs,X / abs,Y → if target is SID register, attribute
        elif op in (0x8D, 0x9D, 0x99) and src is not None:
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            if sid_lo <= tgt <= sid_hi:
                role = role_from_sid_register(tgt - sid_lo)
                sources[src].add(role)

        # Control flow (same as trace_code_with_refs)
        if op in (0x60, 0x40, 0x00):
            continue
        if op == 0x4C:
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            t_off = tgt - load_addr
            if 0 <= t_off < n:
                worklist.append((t_off, src))
            continue
        if op == 0x6C:
            continue
        if op == 0x20:
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            t_off = tgt - load_addr
            if 0 <= t_off < n:
                worklist.append((t_off, src))
            worklist.append((pos + ilen, src))
            continue
        if op in _BRANCHES:
            offset = payload[pos + 1]
            if offset >= 0x80:
                offset -= 0x100
            t_off = pos + ilen + offset
            if 0 <= t_off < n:
                worklist.append((t_off, src))
            worklist.append((pos + ilen, src))
            continue
        worklist.append((pos + ilen, src))

    return sources


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    sid = sys.argv[1]
    h = parse_psid_header(sid)
    payload = h['payload']
    print(f'SID: {sid}')
    print(f'Load: ${h["load_addr"]:04X}-${h["load_end"]:04X} ({len(payload)} bytes)')
    print(f'Init: ${h["init_addr"]:04X}  Play: ${h["play_addr"]:04X}')

    # Static: walk code from init/play
    code_offs, refs = trace_code_with_refs(
        payload, h['load_addr'], h['init_addr'], h['play_addr'])
    print(f'\nStatic disassembly:')
    print(f'  reachable code bytes: {len(code_offs)} ({100*len(code_offs)/len(payload):.1f}% of payload)')
    print(f'  data-reference operands found: {len(refs)}')

    # Dynamic: capture/parse memtrace
    trace_path = ensure_memtrace(sid)
    counts, n_frames = parse_memtrace(trace_path)
    print(f'\nDynamic trace: {n_frames} frames, '
          f'{sum(counts.values()):,} accesses, '
          f'{len(counts):,} unique addresses')

    # Cross-reference: which referenced data targets are in payload range?
    in_range_refs = [r for r in refs if h['load_addr'] <= r.target_addr <= h['load_end']]
    sid_refs = [r for r in refs if r.is_sid]
    external_refs = [r for r in refs if not r.is_sid and not (h['load_addr'] <= r.target_addr <= h['load_end'])]
    print(f'  refs to in-payload data: {len(in_range_refs)}')
    print(f'  refs to SID registers: {len(sid_refs)}')
    print(f'  refs to external (zeropage, OS, etc): {len(external_refs)}')

    # Tables hypothesised from indexed reads/writes in code
    tables = infer_tables(refs, counts, h['load_addr'], h['load_end'])

    # Role inference via SID-register dataflow
    sid_flow = trace_sid_dataflow(payload, h['load_addr'], h['init_addr'], h['play_addr'])
    for base, t in tables.items():
        if base in sid_flow:
            t.role_guess = ','.join(sorted(sid_flow[base]))

    sizes = estimate_table_sizes(tables, counts, code_offs,
                                 h['load_addr'], h['load_end'])

    print(f'\nDiscovered {len(tables)} candidate tables / fields '
          f'(grouped into {len(set(s["cluster_id"] for s in sizes.values()))} clusters):')
    print(f'{"base":>6} {"idx":>3} {"role":<22} {"upper":>5} {"lower":>5} '
          f'{"recsz":>5} {"count":>5} notes')
    print('-' * 105)
    last_cid = None
    for base in sorted(tables):
        t = tables[base]
        s = sizes[base]
        if s['cluster_id'] != last_cid:
            print(f'  --- cluster {s["cluster_id"]}: span ${s["cluster_first"]:04X}+{s["cluster_span"]} bytes '
                  f'({"struct of size " + str(s["record_size"]) + " × " + str(s["record_count"]) + " records" if s["record_size"] else "single table of " + str(s["record_count"]) + " bytes"}) ---')
            last_cid = s['cluster_id']
        notes = []
        if t.runtime_count == 0:
            notes.append('NEVER_ACCESSED')
        print(f'  ${base:04X}    {t.indexed_by:>1}  {t.role_guess:<22} '
              f'{s["upper"]:>5} {s["lower"]:>5} '
              f'{s["record_size"] if s["record_size"] else "":>5} '
              f'{s["record_count"]:>5} {" ".join(notes)}')

    # Coverage estimate
    code_bytes_in_payload = code_offs
    data_addrs_with_traffic = {a for a in counts if h['load_addr'] <= a <= h['load_end']
                               and a - h['load_addr'] not in code_offs}
    coverage = (len(code_bytes_in_payload) + len(data_addrs_with_traffic)) / len(payload)
    print(f'\nCoverage: code {len(code_bytes_in_payload)}, '
          f'data-with-traffic {len(data_addrs_with_traffic)} → '
          f'{100*coverage:.1f}% of payload accounted for')


if __name__ == '__main__':
    main()
