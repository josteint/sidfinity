"""Split a multi-binary PSID (e.g. 5_Title_Tunes.sid) into N standalone PSID files.

A multi-binary SID has a dispatcher init/play that JSRs to N sub-binaries,
each with its own (init, play) addresses. This tool walks the dispatcher,
discovers the N (init, play) pairs, and writes one standalone PSID per
sub-binary.

For each sub-binary the load address is taken from the parent's binary
(the lowest play address corresponds to the first sub's load), and the
extracted payload is sliced from `min(load, play, init)` to the highest
relevant address.

Usage:
    python tools/split_multi_binary.py <parent_sid> <out_dir>

Example:
    python tools/split_multi_binary.py \\
        hvsc85/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid \\
        /tmp/5tt_subs

Writes /tmp/5tt_subs/sub_0.sid, sub_1.sid, ..., sub_N.sid plus a
manifest.json with each sub's load/init/play.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class SubBinary:
    index: int
    init: int
    play: int
    load: int       # = lowest of (init, play, used data)
    end: int        # = highest used address (exclusive)
    payload_offset_in_parent: int


def parse_psid(path: Path) -> tuple[int, bytes, dict]:
    b = path.read_bytes()
    hdr = b[:0x7C]
    hl = int.from_bytes(b[6:8], 'big')
    load = int.from_bytes(b[8:10], 'big')
    payload = b[hl:]
    if load == 0:
        load = int.from_bytes(payload[:2], 'little')
        payload = payload[2:]
    meta = {
        'init':      int.from_bytes(hdr[10:12], 'big'),
        'play':      int.from_bytes(hdr[12:14], 'big'),
        'num_songs': int.from_bytes(hdr[14:16], 'big'),
        'name':      hdr[0x16:0x36].split(b'\x00')[0].decode('latin1', 'replace'),
        'author':    hdr[0x36:0x56].split(b'\x00')[0].decode('latin1', 'replace'),
        'released':  hdr[0x56:0x76].split(b'\x00')[0].decode('latin1', 'replace'),
    }
    return load, payload, meta


def discover_subs(payload: bytes, load: int, init: int, play: int,
                   num_subs: int) -> list[SubBinary]:
    """Walk the init/play dispatchers and collect (init, play) pairs.

    Pattern per subtune is `C9 NN D0 04 20 lo hi 60` (CMP #N, BNE +4,
    JSR target, RTS) — exactly 8 bytes. The LAST entry's BNE offset
    differs but its JSR is still at the same relative position. We
    take exactly `num_subs` JSRs."""
    def jsr_targets(start: int, want: int) -> list[int]:
        """Walk a dispatcher block of CMP/BNE/JSR/RTS chains.
        Some slots have inserted NOPs (BNE offset > 4) so the JSR isn't
        always at a fixed offset — scan forward past CMP for the JSR opcode."""
        off = start - load
        targets: list[int] = []
        i = 0
        limit = want * 24
        while len(targets) < want and i < limit and off + i + 8 < len(payload):
            # CMP #imm at i, BNE at i+2, JSR somewhere in i+4..i+4+skip
            if payload[off + i] == 0xC9 and payload[off + i + 2] == 0xD0:
                skip = payload[off + i + 3]
                # Find JSR ($20) within the skip window
                window_end = i + 4 + skip
                j = i + 4
                while j < window_end and j + 2 < len(payload) - off:
                    if payload[off + j] == 0x20:
                        lo = payload[off + j + 1]
                        hi = payload[off + j + 2]
                        targets.append(lo | (hi << 8))
                        break
                    j += 1
                i = window_end  # next slot begins after the BNE-skipped region
                continue
            i += 1
        return targets

    init_targets = jsr_targets(init, want=num_subs)
    play_targets = jsr_targets(play, want=num_subs)
    if len(init_targets) != num_subs or len(play_targets) != num_subs:
        raise ValueError(
            f"expected {num_subs} subs, found init={len(init_targets)} "
            f"play={len(play_targets)} JSRs"
        )

    # Sub-binary boundaries: for sub N, its code+data lives in [play_N,
    # play_{N+1}) approximately (last sub goes to end of payload).
    sorted_subs = sorted(zip(init_targets, play_targets), key=lambda p: p[1])
    subs: list[SubBinary] = []
    end_of_payload = load + len(payload)
    for idx, (s_init, s_play) in enumerate(sorted_subs):
        # Next sub's play start defines THIS sub's end
        if idx + 1 < len(sorted_subs):
            s_end = sorted_subs[idx + 1][1]
        else:
            s_end = end_of_payload
        # Sub's load is min(play, init, …) since data may live below play
        s_load = min(s_play, s_init)
        subs.append(SubBinary(
            index=idx, init=s_init, play=s_play,
            load=s_load, end=s_end,
            payload_offset_in_parent=s_load - load,
        ))
    return subs


def write_psid(out_path: Path, parent_meta: dict, sub: SubBinary,
                parent_payload: bytes, parent_load: int) -> None:
    """Write a standalone PSID file containing only this sub-binary."""
    span = sub.end - sub.load
    code = parent_payload[sub.payload_offset_in_parent:sub.payload_offset_in_parent + span]

    # PSID v2 header, 124 bytes
    name = (parent_meta['name'] + f' (sub {sub.index})')[:32].ljust(32, '\x00').encode('latin1')
    author = parent_meta['author'][:32].ljust(32, '\x00').encode('latin1')
    released = parent_meta['released'][:32].ljust(32, '\x00').encode('latin1')

    hdr = bytearray(124)
    hdr[0:4] = b'PSID'
    hdr[4:6] = (2).to_bytes(2, 'big')           # version
    hdr[6:8] = (124).to_bytes(2, 'big')          # data offset
    hdr[8:10] = sub.load.to_bytes(2, 'big')      # load addr (non-zero, no inline)
    hdr[10:12] = sub.init.to_bytes(2, 'big')     # init
    hdr[12:14] = sub.play.to_bytes(2, 'big')     # play
    hdr[14:16] = (1).to_bytes(2, 'big')          # num_songs = 1
    hdr[16:18] = (1).to_bytes(2, 'big')          # start_song = 1
    hdr[18:22] = (0).to_bytes(4, 'big')          # speed (PAL=0)
    hdr[0x16:0x36] = name
    hdr[0x36:0x56] = author
    hdr[0x56:0x76] = released
    hdr[0x76:0x78] = (0).to_bytes(2, 'big')      # flags
    hdr[0x78:0x7C] = (0).to_bytes(4, 'big')      # startPage/pageLength/2nd SID

    out_path.write_bytes(bytes(hdr) + code)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('parent_sid', type=Path)
    ap.add_argument('out_dir', type=Path)
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    load, payload, meta = parse_psid(args.parent_sid)
    subs = discover_subs(payload, load, meta['init'], meta['play'],
                          meta['num_songs'])

    manifest = []
    for sub in subs:
        out = args.out_dir / f'sub_{sub.index}.sid'
        write_psid(out, meta, sub, payload, load)
        manifest.append({**asdict(sub),
                         'parent_load': load,
                         'load_hex': f'${sub.load:04X}',
                         'init_hex': f'${sub.init:04X}',
                         'play_hex': f'${sub.play:04X}',
                         'span_bytes': sub.end - sub.load,
                         'out_file': out.name})
        print(f"  sub {sub.index}: load=${sub.load:04X} init=${sub.init:04X} "
              f"play=${sub.play:04X} span={sub.end - sub.load:5d} bytes "
              f"→ {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}")

    (args.out_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {len(subs)} sub-binaries + manifest.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
