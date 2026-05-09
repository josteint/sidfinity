"""discover_hubbard_landmarks.py — find ALL the structural landmarks
das_model_gen needs, for any Hubbard-engine SID.

Replaces the Commando-hardcoded values in das_model_gen.extract with
discovery-derived values. Returns a dict suitable as input to a
generalized das_model_gen.extract(sid_path, landmarks=...).

Landmarks returned:
  load_addr, init_addr, play_addr        — PSID header (always present)
  num_songs, start_song                  — PSID header
  freq_table_addr                        — discovery (87.4% Hubbard coverage)
  instr_addr, instr_count                — discovery (cluster with multi-field
                                            SID-register roles)
  song_table_addr                        — discovery (per-voice ptr-table pair,
                                            X-indexed, count = 3 voices typically)
  seqlo_addr, seqhi_addr, num_sequences  — discovery (Y-indexed ptr pair)
  pattern_data_start, pattern_count      — derived from seqlo/seqhi pointers

If a landmark can't be found, it's None. Caller must handle missing
landmarks — typically by giving up on that SID or falling back to
rh_decompile for that one value.
"""
import os
import struct
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))


@dataclass
class HubbardLandmarks:
    """All structural landmarks needed by das_model_gen.extract."""
    sid_path: str
    load_addr: int = 0
    init_addr: int = 0
    play_addr: int = 0
    num_songs: int = 0
    start_song: int = 0
    freq_table_addr: int | None = None
    instr_addr: int | None = None
    instr_count: int = 0
    instr_record_size: int = 0
    song_table_addr: int | None = None
    seqlo_addr: int | None = None
    seqhi_addr: int | None = None
    num_sequences: int = 0
    pattern_addrs: list[int] = field(default_factory=list)
    # Discovery's confidence — which landmarks were found vs missing
    found: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def coverage_score(self) -> float:
        """Fraction of critical landmarks found (0..1)."""
        critical = ['freq_table_addr', 'instr_addr', 'song_table_addr',
                    'seqlo_addr', 'seqhi_addr']
        return sum(1 for k in critical if self.found.get(k, False)) / len(critical)

    def summary(self) -> str:
        lines = [f'Landmarks for {os.path.basename(self.sid_path)}:']
        lines.append(f'  load=${self.load_addr:04X}  init=${self.init_addr:04X}  '
                     f'play=${self.play_addr:04X}')
        lines.append(f'  num_songs={self.num_songs}  start_song={self.start_song}')
        for name in ['freq_table_addr', 'instr_addr', 'song_table_addr',
                     'seqlo_addr', 'seqhi_addr']:
            v = getattr(self, name)
            mark = '✓' if v is not None else '✗'
            v_str = f'${v:04X}' if v is not None else 'None'
            lines.append(f'  {mark} {name:20s} = {v_str}')
        lines.append(f'  instr_count={self.instr_count}  '
                     f'record_size={self.instr_record_size}')
        lines.append(f'  num_sequences={self.num_sequences}  '
                     f'pattern_addrs={len(self.pattern_addrs)}')
        lines.append(f'  coverage_score={self.coverage_score():.2f}')
        if self.notes:
            lines.append('  notes:')
            for n in self.notes:
                lines.append(f'    - {n}')
        return '\n'.join(lines)


def discover_hubbard_landmarks(sid_path: str, duration: int = 5) -> HubbardLandmarks:
    """Run discovery + PSID parsing to populate all Hubbard landmarks."""
    from sidxray.discover import (
        parse_psid_header, parse_memtrace, ensure_memtrace,
        trace_code_with_refs, infer_tables, trace_sid_dataflow,
        estimate_table_sizes, detect_pointer_tables,
        materialize_pointers, find_pattern_regions,
    )
    out = HubbardLandmarks(sid_path=sid_path)

    # PSID header — always available
    h = parse_psid_header(sid_path)
    out.load_addr = h['load_addr']
    out.init_addr = h['init_addr']
    out.play_addr = h['play_addr']

    with open(sid_path, 'rb') as f:
        raw = f.read()
    out.num_songs = struct.unpack('>H', raw[0x0E:0x10])[0]
    out.start_song = struct.unpack('>H', raw[0x10:0x12])[0]

    payload = h['payload']

    # Discovery pass
    code_offs, refs = trace_code_with_refs(
        payload, h['load_addr'], h['init_addr'], h['play_addr'])
    trace_path = ensure_memtrace(sid_path, duration=duration)
    counts, _ = parse_memtrace(trace_path)
    tables = infer_tables(refs, counts, h['load_addr'], h['load_end'])
    sid_flow = trace_sid_dataflow(payload, h['load_addr'],
                                  h['init_addr'], h['play_addr'])
    for base, t in tables.items():
        if base in sid_flow:
            t.role_guess = ','.join(sorted(sid_flow[base]))
    sizes = estimate_table_sizes(tables, counts, code_offs,
                                  h['load_addr'], h['load_end'])
    ptr_pairs = detect_pointer_tables(payload, h['load_addr'],
                                       h['init_addr'], h['play_addr'])

    # 1. freq_table_addr — lowest cluster with freq_lo or freq_hi role.
    # Discovery often finds freq_hi; for das_model_gen we need freq_lo
    # base (where actual freq values start). Heuristic: if discovered
    # base has freq_hi role and there's a sister cluster ~95-96 bytes
    # earlier, use the earlier one (= freq_lo base).
    freq_bases = []
    for base, t in tables.items():
        roles = sid_flow.get(base, set())
        if 'freq_lo' in roles or 'freq_hi' in roles:
            freq_bases.append((base, roles))
    if freq_bases:
        freq_bases.sort()
        # Prefer the lowest base (typically freq_lo); if it only has
        # freq_hi role, look for a sister ~95 bytes earlier.
        chosen = freq_bases[0][0]
        chosen_roles = freq_bases[0][1]
        if 'freq_lo' not in chosen_roles and 'freq_hi' in chosen_roles:
            # Look for a freq_lo base ~95 bytes earlier in any cluster
            for offset in (95, 96, 94, 93):
                candidate = chosen - offset
                if h['load_addr'] <= candidate <= h['load_end']:
                    out.notes.append(
                        f'freq_hi at ${chosen:04X}; freq_lo likely at '
                        f'${candidate:04X} (-{offset})')
                    chosen = candidate
                    break
        out.freq_table_addr = chosen
        out.found['freq_table_addr'] = True
    else:
        out.found['freq_table_addr'] = False

    # 2. instr_addr — cluster with multiple instrument-y SID roles.
    # Hubbard instruments have fields that flow to ctrl, attack_decay,
    # sustain_release, pulse_lo, pulse_hi.
    inst_role_set = {'pulse_lo', 'pulse_hi', 'ctrl',
                     'attack_decay', 'sustain_release'}
    cluster_roles: dict[int, set[str]] = {}
    cluster_first_addr: dict[int, int] = {}
    cluster_recsize: dict[int, int] = {}
    cluster_count: dict[int, int] = {}
    for base in tables:
        if base not in sizes:
            continue
        s = sizes[base]
        cid = s['cluster_id']
        cluster_first_addr.setdefault(cid, s['cluster_first'])
        cluster_recsize[cid] = s['record_size'] or 1
        cluster_count[cid] = s['record_count']
        cluster_roles.setdefault(cid, set()).update(
            tables[base].role_guess.split(','))
    inst_cid = None
    inst_score = 0
    for cid, roles in cluster_roles.items():
        sc = len(roles & inst_role_set)
        if sc >= 2 and sc > inst_score:
            inst_score = sc
            inst_cid = cid
    if inst_cid is not None:
        out.instr_addr = cluster_first_addr[inst_cid]
        out.instr_count = cluster_count[inst_cid] or 0
        out.instr_record_size = cluster_recsize[inst_cid]
        out.found['instr_addr'] = True
    else:
        out.found['instr_addr'] = False

    # 3. Pointer-table pairs → song table + sequence pointer table.
    # Per-voice tracks (X-indexed, small count) = song dispatch.
    # Sequence pointers (Y-indexed, larger count) = pattern dispatch.
    seen_pairs = set()
    unique_pairs = []
    for p in sorted(ptr_pairs,
                    key=lambda p: p.hi_table - p.lo_table, reverse=True):
        k = (p.lo_table, p.hi_table)
        if k not in seen_pairs:
            seen_pairs.add(k)
            unique_pairs.append(p)

    # Sequence pointer table: largest count_hint (often 30-100)
    if unique_pairs:
        seq_pair = unique_pairs[0]
        out.seqlo_addr = seq_pair.lo_table
        out.seqhi_addr = seq_pair.hi_table
        out.num_sequences = seq_pair.hi_table - seq_pair.lo_table
        out.found['seqlo_addr'] = True
        out.found['seqhi_addr'] = True

        # Materialize pointers → pattern start addresses
        pat_regions = find_pattern_regions(
            payload, h['load_addr'], h['load_end'],
            seq_pair, out.num_sequences, counts)
        out.pattern_addrs = sorted({r.start for r in pat_regions})
    else:
        out.found['seqlo_addr'] = False
        out.found['seqhi_addr'] = False

    # Song table: smaller pointer pair (X-indexed, count ≈ 3 voices)
    # Heuristic: in Hubbard's layout, song table holds 6 bytes per song
    # (3 lo + 3 hi pointers), starting just before the active per-voice
    # working pointers found by discovery.
    if len(unique_pairs) >= 2:
        # Second-largest pair is likely the per-voice working pointers
        # (lo at X for current song's V0/V1/V2 tracks)
        voice_pair = unique_pairs[1]
        # Song table starts wherever rh_decompile would find it; for now
        # use the discovered base directly (caller may need adjustment).
        out.song_table_addr = voice_pair.lo_table
        out.found['song_table_addr'] = True
    else:
        out.found['song_table_addr'] = False

    return out


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('sid')
    p.add_argument('--duration', type=int, default=5)
    args = p.parse_args()
    lm = discover_hubbard_landmarks(args.sid, duration=args.duration)
    print(lm.summary())


if __name__ == '__main__':
    main()
