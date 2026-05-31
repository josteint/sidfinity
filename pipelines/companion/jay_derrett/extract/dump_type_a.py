"""Type A engine-data dump.

For each of the 15 Type A SIDs, produce a structured JSON record
containing everything the downstream USF schema designer + composer
will need:

  - PSID header fields
  - Engine structural addresses (init/play/proc_note/play_loop_entry)
  - Per-voice ptr_addr + initial_ptr + byte sequence (the full
    captured stream from play-capture's min..max ptr range)
  - Freq table contents (256 bytes from freq_lo / freq_hi)
  - $E0 sub-jump table contents (up to 20 bytes — entries 0..9)
  - Instrument programs (24-byte each, indexed by inst num)
  - Self-mod counter address (proc_note + offset) + initial value

JSON output lands at `pipelines/companion/jay_derrett/_extracted/<NAME>.json`.

Usage:
    PYTHONPATH=. python3 pipelines/companion/jay_derrett/extract/dump_type_a.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))))

from pipelines.companion.jay_derrett.extract.engine_model import (
    load_state_from_sid, _run_play_capture,
    find_freq_tables, find_sub_jump_table, find_instrument_base_table,
)


TYPE_A = [
    'Counterforce', 'Destruct', 'Discovery', 'Jetboys', 'Lifeforce',
    'Mandroid', 'Ninja_Hamster', 'Osmium', 'Road_Warrior', 'Stratton',
    'Thundercross', 'Traxxion', 'Trigger_Happy', 'Vengeance', 'ZIP',
]


def _read_psid_meta(sid_path: str) -> dict:
    raw = open(sid_path, 'rb').read()
    return dict(
        title=raw[0x16:0x36].rstrip(b'\x00').decode('latin-1'),
        author=raw[0x36:0x56].rstrip(b'\x00').decode('latin-1'),
        released=raw[0x56:0x76].rstrip(b'\x00').decode('latin-1'),
        flags=int.from_bytes(raw[0x76:0x78], 'big'),
        start_song=int.from_bytes(raw[0x10:0x12], 'big'),
        speed=int.from_bytes(raw[0x12:0x16], 'big'),
        n_subtunes=int.from_bytes(raw[0x0E:0x10], 'big'),
    )


def _extract_one(name: str) -> dict | None:
    sid = f'hvsc84/MUSICIANS/D/Derrett_Jay/{name}.sid'
    if not os.path.exists(sid):
        return None
    try:
        s = load_state_from_sid(sid)
    except Exception as e:
        return dict(name=name, error=f'load_state_from_sid: {type(e).__name__}: {e}')
    mem = bytearray(s.post_init_mem)

    out = dict(
        name=name,
        sid_path=sid,
        psid=_read_psid_meta(sid),
        load=s.load,
        init_addr=s.init_addr,
        play_addr=s.play_addr,
        play_loop_entry=s.play_loop_entry,
        proc_note_addr=s.proc_note_addr,
    )

    # Voices: ptr_addr, initial_ptr, zp
    out['voices'] = [
        dict(idx=v.idx, ptr_addr=v.ptr_addr, initial_ptr=v.initial_ptr,
             zp=v.zp)
        for v in s.voices
    ]

    # Counter address (best-effort default — proc_note + $18).
    out['counter_addr'] = s.proc_note_addr + 0x18
    out['counter_init'] = mem[s.proc_note_addr + 0x18]

    # Freq tables.
    ft = find_freq_tables(mem, s.play_loop_entry)
    if ft is not None:
        ft_lo, ft_hi = ft
        out['freq_table'] = dict(
            lo_addr=ft_lo, hi_addr=ft_hi,
            lo=list(mem[ft_lo:ft_lo + 128]),
            hi=list(mem[ft_hi:ft_hi + 128]),
        )
    else:
        out['freq_table'] = None

    # $E0 sub-jump table (first 20 bytes — 10 entries × 2).
    e0 = find_sub_jump_table(mem, s.proc_note_addr, s.voices[0].zp)
    if e0 is not None:
        out['sub_jump_table'] = dict(addr=e0, bytes=list(mem[e0:e0 + 20]))
    else:
        out['sub_jump_table'] = None

    # Instrument programs.
    ib = find_instrument_base_table(mem, s.play_loop_entry)
    if ib is not None:
        # Determine instrument SIZE from the LDY #imm at the copy loop.
        # We don't have a helper for this — scan around the LDA $abs,Y
        # self-mod target for the preceding LDY #imm.
        # Approximation: scan a window in mem near play_loop_entry for
        # LDY #imm patterns where imm in 7..31. Pick the first.
        inst_size = 24  # default fallback
        for q in range(s.play_loop_entry,
                       min(s.play_loop_entry + 0x800, len(mem) - 1)):
            if mem[q] == 0xA0 and 0x07 <= mem[q + 1] <= 0x1F:
                inst_size = mem[q + 1] + 1
                break

        # Walk all 32 entries, recording valid ones (don't bail on a
        # single invalid — Ninja_Hamster has index 0 = garbage and
        # 1..16 valid; some other tunes use a sparse layout).
        instruments = []
        consecutive_invalid = 0
        for i in range(32):
            lo = mem[ib + i * 2]
            hi = mem[ib + i * 2 + 1]
            addr = lo | (hi << 8)
            if not (s.load <= addr < s.load + 0x4000):
                consecutive_invalid += 1
                if consecutive_invalid >= 3:
                    break  # Likely past the actual table.
                continue
            consecutive_invalid = 0
            instruments.append(dict(
                idx=i, addr=addr,
                bytes=list(mem[addr:addr + inst_size]),
            ))
        out['instrument_base_table'] = dict(
            addr=ib, size_per_instrument=inst_size,
            count=len(instruments),
            instruments=instruments,
        )
    else:
        out['instrument_base_table'] = None

    # Play-capture: per-voice byte sequence.
    try:
        trails, post_play_mem, ct = _run_play_capture(sid, n_frames=15000)
        out['play_capture'] = dict(
            n_frames=len(ct),
            counter_initial=ct[0],
            counter_max=max(ct),
            counter_final=ct[-1],
            loop_detected=(ct[-1] < max(ct)),
        )
        voice_bytes = []
        for i, t in enumerate(trails):
            uniq = sorted(set(t))
            lo, hi = min(uniq), max(uniq)
            voice_bytes.append(dict(
                idx=i,
                ptr_min=lo, ptr_max=hi,
                n_unique=len(uniq),
                bytes=list(post_play_mem[lo:hi + 2]),
            ))
        out['voice_bytes'] = voice_bytes
    except Exception as e:
        out['play_capture'] = dict(error=f'{type(e).__name__}: {e}')

    return out


def main() -> int:
    out_dir = 'pipelines/companion/jay_derrett/_extracted'
    os.makedirs(out_dir, exist_ok=True)
    ok = err = 0
    for name in TYPE_A:
        rec = _extract_one(name)
        if rec is None:
            print(f'  SKIP {name}: SID missing')
            continue
        if 'error' in rec:
            print(f'  ERR  {name}: {rec["error"]}')
            err += 1
            continue
        out_path = os.path.join(out_dir, f'{name}.json')
        with open(out_path, 'w') as f:
            json.dump(rec, f, indent=2)
        n_inst = (rec.get('instrument_base_table') or {}).get('count', 0)
        ranges = ' '.join(
            f'V{v["idx"]+1}:{v["n_unique"]}b'
            for v in rec.get('voice_bytes', [])
        )
        looped = rec.get('play_capture', {}).get('loop_detected', False)
        loop_marker = '✓loop' if looped else '15k'
        print(f'  OK   {name:18s}  insts={n_inst:2d}  {ranges:22s}  {loop_marker}')
        ok += 1
    print(f'\n{ok}/{len(TYPE_A)} ok, {err} errors')
    print(f'Output: {out_dir}/<NAME>.json')
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
