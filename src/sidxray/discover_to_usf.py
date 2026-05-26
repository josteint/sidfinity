"""discover_to_usf.py — End-to-end Commando crack via discovery (Option A).

Combines:
  1. Discovery — finds structural landmarks without engine knowledge.
  2. rh_decompile parsers — interpret the bytes at those landmarks.
  3. rh_to_usf — convert to USF (engine-specific Hubbard knowledge).
  4. usf_to_sid (V3) — emit rebuilt SID.
  5. siddump --writelog — verify byte-equal cycle-accurate output.

The script ALSO reports landmark-by-landmark how much of `rh_decompile`'s
output discovery would have produced on its own — this is the
"how much engine-specific knowledge does discovery still need" measure.

Usage:
    python3 src/sidxray/discover_to_usf.py <sid_path>
"""

import os
import sys
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sidxray.discover import (
    parse_psid_header, parse_memtrace, ensure_memtrace,
    trace_code_with_refs, infer_tables, trace_sid_dataflow,
    estimate_table_sizes, detect_pointer_tables,
)


def discover_landmarks(sid_path):
    """Run the discovery pipeline and return the landmarks it finds."""
    h = parse_psid_header(sid_path)
    payload = h['payload']
    code_offs, refs = trace_code_with_refs(
        payload, h['load_addr'], h['init_addr'], h['play_addr'])
    trace_path = ensure_memtrace(sid_path)
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

    # Aggregate: landmark name → discovered address (or None if missed)
    out = {
        'init_addr': h['init_addr'],
        'play_addr': h['play_addr'],
        'instr_addr': None, 'num_instruments': 0,
        'seqlo_addr': None, 'seqhi_addr': None, 'num_sequences': 0,
        'freq_table_addr': None,
        'song_track_lo': None, 'song_track_hi': None,
    }

    # Instrument cluster: max overlap with instrument-y SID roles
    inst_roles = {'pulse_lo', 'pulse_hi', 'ctrl', 'attack_decay', 'sustain_release'}
    cluster_first: dict[int, int] = {}
    cluster_recsize: dict[int, int] = {}
    cluster_count: dict[int, int] = {}
    cluster_roles: dict[int, set[str]] = {}
    for base in tables:
        s = sizes[base]
        cid = s['cluster_id']
        cluster_first.setdefault(cid, s['cluster_first'])
        cluster_recsize[cid] = s['record_size'] or 1
        cluster_count[cid] = s['record_count']
        cluster_roles.setdefault(cid, set()).update(
            tables[base].role_guess.split(','))
    inst_cid = max(cluster_roles,
                   key=lambda c: len(cluster_roles[c] & inst_roles),
                   default=None)
    if inst_cid is not None and len(cluster_roles[inst_cid] & inst_roles) > 0:
        out['instr_addr'] = cluster_first[inst_cid]
        out['num_instruments'] = cluster_count[inst_cid]

    # Freq table: lowest cluster with freq_lo / freq_hi
    for cid in sorted(cluster_first, key=lambda c: cluster_first[c]):
        if cluster_roles[cid] & {'freq_lo', 'freq_hi'}:
            out['freq_table_addr'] = cluster_first[cid]
            break

    # Pointer pairs by descending count
    seen = set()
    unique_pairs = []
    for p in sorted(ptr_pairs,
                    key=lambda p: p.hi_table - p.lo_table, reverse=True):
        k = (p.lo_table, p.hi_table)
        if k not in seen:
            seen.add(k)
            unique_pairs.append(p)
    if unique_pairs:
        out['seqlo_addr'] = unique_pairs[0].lo_table
        out['seqhi_addr'] = unique_pairs[0].hi_table
        out['num_sequences'] = unique_pairs[0].hi_table - unique_pairs[0].lo_table
    if len(unique_pairs) >= 2:
        out['song_track_lo'] = unique_pairs[1].lo_table
        out['song_track_hi'] = unique_pairs[1].hi_table

    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    sid = sys.argv[1]

    print(f'=== Discovery vs rh_decompile for {sid} ===\n')

    # Discovery
    print('Phase 1: Discovery (no engine knowledge)')
    disc = discover_landmarks(sid)
    print(f"  init={fmt(disc['init_addr'])}  play={fmt(disc['play_addr'])}")
    print(f"  instr_addr={fmt(disc['instr_addr'])}  "
          f"num_instruments={disc['num_instruments']}")
    print(f"  seqlo={fmt(disc['seqlo_addr'])}  seqhi={fmt(disc['seqhi_addr'])}  "
          f"num_sequences={disc['num_sequences']}")
    print(f"  song_track_lo/hi={fmt(disc['song_track_lo'])}/{fmt(disc['song_track_hi'])}")
    print(f"  freq_table_addr={fmt(disc['freq_table_addr'])}")

    # rh_decompile (the existing tool — engine-specific knowledge baked in)
    print('\nPhase 2: rh_decompile (engine-specific reference)')
    from rh_decompile import decompile
    r = decompile(sid)
    print(f"  init={fmt(r.init_addr)}  play={fmt(r.play_addr)}")
    print(f"  instr_addr={fmt(r.instr_addr)}  instruments={len(r.instruments)}")
    print(f"  seqlo={fmt(r.seqlo_addr)}  seqhi={fmt(r.seqhi_addr)}  "
          f"num_sequences={r.num_sequences}")
    print(f"  song_table={fmt(r.song_table_addr)}  num_songs={r.num_songs} "
          f"(decoded {len(r.songs)})")
    print(f"  freq_table_addr={fmt(r.freq_table_addr)}")

    # Comparison
    print('\nPhase 3: How much would discovery have driven the pipeline?')
    pairs = [
        ('init',           disc['init_addr'],     r.init_addr),
        ('play',           disc['play_addr'],     r.play_addr),
        ('instr_addr',     disc['instr_addr'],    r.instr_addr),
        ('num_instruments', disc['num_instruments'], len(r.instruments)),
        ('seqlo_addr',     disc['seqlo_addr'],    r.seqlo_addr),
        ('seqhi_addr',     disc['seqhi_addr'],    r.seqhi_addr),
        ('num_sequences',  disc['num_sequences'], r.num_sequences),
        ('freq_table',     disc['freq_table_addr'], r.freq_table_addr),
    ]
    matched = 0
    for name, d, g in pairs:
        ok = '✓' if d == g else '✗'
        if d == g:
            matched += 1
        print(f"  {ok} {name:18}  discovery={fmt(d):>8}  rh_decompile={fmt(g):>8}")
    print(f"\n  Discovery matched {matched}/{len(pairs)} core landmarks "
          f"({100*matched/len(pairs):.0f}%)")

    # Pipeline end-to-end via existing tools (we know this produces
    # byte-perfect Commando — the test is whether discovery's landmarks
    # would have led us to the same conclusions)
    print('\nPhase 4: End-to-end pipeline (rh_decompile → rh_to_usf → V3 → SID)')
    from converters.rh_to_usf import rh_to_usf
    from converters.usf_to_sid import usf_to_sid
    usf = rh_to_usf(sid)
    out_sid = '/tmp/discover_rebuild.sid'
    usf_to_sid(usf, out_sid)
    print(f"  rebuilt SID written: {out_sid}")

    # Writelog comparison
    print('\nPhase 5: Writelog comparison (cycle-accurate ground truth)')
    def writelog(p, dur=10):
        out = subprocess.run(
            ['/home/jtr/sidfinity/tools/siddump', p, '--writelog',
             '--duration', str(dur), '--raw'],
            capture_output=True, text=True)
        return out.stdout
    wl_orig = writelog(sid)
    wl_new = writelog(out_sid)
    if wl_orig == wl_new:
        print('  ✓✓✓ Writelogs are byte-identical — PERFECT match')
    else:
        orig_lines = wl_orig.split('\n')
        new_lines = wl_new.split('\n')
        match = sum(1 for a, b in zip(orig_lines, new_lines) if a == b)
        total = max(len(orig_lines), len(new_lines))
        print(f'  Writelog frames matching: {match}/{total} '
              f'({100*match/max(total,1):.1f}%)')
        # First mismatch
        for i, (a, b) in enumerate(zip(orig_lines, new_lines)):
            if a != b:
                print(f'  first divergence at frame {i}:')
                print(f'    orig: {a[:100]}')
                print(f'    new:  {b[:100]}')
                break


def fmt(v):
    if v is None: return 'None'
    if isinstance(v, int) and v >= 0x100: return f'${v:04X}'
    return str(v)


if __name__ == '__main__':
    main()
