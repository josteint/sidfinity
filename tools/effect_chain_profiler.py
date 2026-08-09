#!/usr/bin/env python3
"""effect_chain_profiler.py — attribute each SID write to its CPU PC.

For each write to a target SID register (or all $D4xx), report the CPU
PC that performed it. Lets you answer "which routine wrote this
$D408 = $47?" in one command, without manually tracing the engine.

Internally runs `siddump --writelog --pc-trace` over a chosen frame
range. The PC of each write is read DIRECTLY off the store instruction
in the pc-trace — every pc-trace line carries the PC, the A/X/Y
registers, and the RESOLVED effective address, e.g.

    160d t 47 00 00 ...  99 00 d4  STAay d400,Y [d400]

means PC $160D wrote A=$47 to $D400. So attribution is EXACT — there is
no cycle reconstruction. The pc-trace `[d4xx]` stores are zipped
ordinally with the writelog (the Nth store in the trace IS the Nth
write in the writelog); the writelog supplies frame numbers and a
desync sanity-check.

(Earlier versions rebuilt each write's absolute cycle as
`frame * 19688 + rel_cycle` and binary-searched the PC trace for the
nearest sample. That `19688` is the Trap-C pitfall — a siddump frame
advances ~18,000 CPU cycles, not 19688 — so the reconstructed cycle
drifted and the lookup landed in the PSID driver's idle spin loop
($04A5) instead of the real writer. The ordinal-zip avoids cycles.)

Usage:
    python3 tools/effect_chain_profiler.py SID --subtune N \\
        --frames START-END [--register HEX[,HEX,...]]

    # Examples:
    # Tag every $D408 write in Hawkeye sub 1 frames 145-152:
    python3 tools/effect_chain_profiler.py \\
        hvsc85/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid \\
        --subtune 1 --frames 145-152 --register D408

    # Tag ALL writes in a frame range (omit --register):
    python3 tools/effect_chain_profiler.py SID --subtune 0 --frames 1-3

Output format:
    f<frame>  $D4XX <role>  $VV   PC=$YYYY
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDDUMP = ROOT / 'tools' / 'siddump'

# A pc-trace data line, e.g.:
#   160d t 47 00 00 01f4 2f 37 00110100  99 00 d4  STAay d400,Y [d400]
#   PC   _ A  X  Y  ...                              mnem        [effaddr]
_PC_LINE = re.compile(
    r'^\s*([0-9a-fA-F]{4})\s+\S\s+'        # PC, the f/t flag
    r'([0-9a-fA-F]{2})\s+'                 # A
    r'([0-9a-fA-F]{2})\s+'                 # X
    r'([0-9a-fA-F]{2})\b')                 # Y
_STORE = re.compile(r'\b(ST[AXY])\w*', re.I)        # STA / STX / STY (+addr mode)
_EFFADDR = re.compile(r'\[d4([0-9a-fA-F]{2})\]', re.I)
# The pc-trace resolves an [effaddr] bracket only for INDEXED stores; an
# absolute store prints bare (`8d 16 d4  STAa  d416`, no bracket). Missing
# these made --find-write report 0 for players that write SID registers
# with absolute stores (Calf_Love, 2026-07-28) — match the disasm operand.
_ABS_STORE = re.compile(r'\bST[AXY]a\s+d4([0-9a-fA-F]{2})\s*$', re.I)
_CYCLE = re.compile(r'\((\d+)\)')


def _capture(sid_path: str, subtune: int, start_frame: int, end_frame: int):
    """Run siddump and return the ordered $D4xx store stream.

    Returns [(pc, reg, val, cycle)] for every `ST[AXY]` instruction whose
    RESOLVED effective address is $D400..$D418, read DIRECTLY off the
    pc-trace line (PC, A/X/Y, effective address, and cycle are all on the
    same line). No cycle reconstruction, no writelog zip — the pc-trace IS
    ground truth for what the CPU executed, so every store is real and its
    PC is exact. Frame/play() grouping is recovered downstream from the
    cycle gaps (the ~19k-cycle idle between play() invocations).
    """
    duration = (end_frame + 2) / 50.0
    with tempfile.NamedTemporaryFile(suffix='.pc', delete=False) as f:
        pc_path = f.name
    try:
        r = subprocess.run(
            [str(SIDDUMP), sid_path,
             '--subtune', str(subtune + 1),
             '--duration', str(duration),
             '--pc-trace', pc_path,
             str(start_frame), str(end_frame)],
            capture_output=True, text=True)
        if r.returncode not in (0, 2):
            print(f'siddump error (rc={r.returncode}):\n{r.stderr}',
                  file=sys.stderr)
            return []

        pcw: list[tuple[int, int, int, int | None]] = []
        cur_cycle: int | None = None
        with open(pc_path) as f:
            for line in f:
                mc = _CYCLE.search(line)
                if mc and 'Instruction' in line:
                    cur_cycle = int(mc.group(1))
                    continue
                me = _EFFADDR.search(line) or _ABS_STORE.search(line)
                if not me:
                    continue
                reg = int(me.group(1), 16)
                if reg > 0x18:                 # $D419+ are read regs / paddle
                    continue
                mst = _STORE.search(line)
                if not mst:                    # a LOAD from $D4xx — not a write
                    continue
                ml = _PC_LINE.match(line)
                if not ml:
                    continue
                pc = int(ml.group(1), 16)
                a, x, y = (int(ml.group(2), 16), int(ml.group(3), 16),
                           int(ml.group(4), 16))
                mn = mst.group(1).upper()
                val = x if mn == 'STX' else y if mn == 'STY' else a
                pcw.append((pc, reg, val, cur_cycle))
        return pcw
    finally:
        os.unlink(pc_path)


def _song_frames(sid_path: str, subtune: int, cap: int = 6000) -> int:
    """Frame count (50 Hz) for `subtune` from HVSC's Songlengths.md5, capped so
    a full-song pc-trace stays bounded. Falls back to `cap` if unavailable."""
    try:
        from src.songlengths import load_database, get_durations
        db = load_database(str(ROOT / 'hvsc85' / 'DOCUMENTS' / 'Songlengths.md5'))
        durs = get_durations(sid_path, db)
        if durs and subtune < len(durs):
            return min(cap, max(50, int(durs[subtune] * 50 * 1.1)))
    except Exception:
        pass
    return cap


def _voice_role(reg: int) -> str:
    if 0x00 <= reg <= 0x14:
        v = reg // 7 + 1
        roles = ['freq lo', 'freq hi', 'PW lo', 'PW hi', 'ctrl', 'AD', 'SR']
        return f'V{v} {roles[reg % 7]}'
    return {
        0x15: 'filter cutoff lo',
        0x16: 'filter cutoff hi',
        0x17: 'filter res/route',
        0x18: 'vol/filter mode',
    }.get(reg, f'reg ${reg:02X}')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('sid')
    p.add_argument('--subtune', type=int, default=0,
                   help='0-indexed (default 0)')
    p.add_argument('--frames', default=None,
                   help='Frame range START-END (e.g. 145-152). Optional with '
                        '--find-write (defaults to a full-song scan).')
    p.add_argument('--register', default=None,
                   help='Filter to specific $D4xx register(s), '
                        'comma-separated hex (e.g. D408 or 02,03)')
    p.add_argument('--find-write', default=None, metavar='REG=VAL',
                   help='Find every write of REG=VAL (e.g. D408=B7) and report '
                        'its PC + play index — no frame guess needed. This is '
                        'the answer to "find_first_divergence gave me a VALUE '
                        'but not the frame" (siddump frame != play() index).')
    args = p.parse_args()
    if not os.path.exists(args.sid):
        print(f'sid not found: {args.sid}', file=sys.stderr); return 1

    find_reg = find_val = None
    if args.find_write:
        if '=' not in args.find_write:
            print('--find-write must be REG=VAL (e.g. D408=B7)',
                  file=sys.stderr); return 1
        rs, vs = args.find_write.split('=')
        find_reg = int(rs, 16)
        if find_reg >= 0xD400:
            find_reg -= 0xD400
        find_val = int(vs, 16)

    if args.frames is None:
        if not args.find_write:
            print('--frames START-END is required (or use --find-write)',
                  file=sys.stderr); return 1
        # Full-song scan: derive the frame count from the songlength (capped so
        # the pc-trace stays bounded). --find-write's whole point is not knowing
        # the frame, so scan the song.
        sf, ef = 1, _song_frames(args.sid, args.subtune)
    else:
        if '-' not in args.frames:
            print('--frames must be START-END', file=sys.stderr); return 1
        sf_s, ef_s = args.frames.split('-')
        sf, ef = int(sf_s), int(ef_s)

    reg_filter: set[int] | None = None
    if args.register:
        reg_filter = set()
        for tok in args.register.split(','):
            v = int(tok.strip(), 16)
            if v >= 0xD400:
                v -= 0xD400
            reg_filter.add(v)

    pcw = _capture(args.sid, args.subtune, sf, ef)
    if not pcw:
        print('No $D4xx stores captured. siddump stderr above may explain.',
              file=sys.stderr)
        return 1

    # Group stores into play() invocations by cycle gap. Within one play()
    # the $D4xx stores cluster within ~a few hundred cycles; consecutive
    # play()s are ~19656 cycles (one PAL frame) apart. A gap over PLAY_GAP
    # therefore marks a new play(). This is the honest unit (siddump's frame
    # buckets are NOT play() invocations — Trap C — so we don't pretend to
    # label by siddump frame). Play 0 = the first play() in the range; for a
    # capture that starts at frame F it corresponds to ~frame F.
    PLAY_GAP = 4000

    if find_reg is not None:
        # --find-write: report every occurrence of REG=VAL with its play index
        # + exact PC. No frame guessing — the play index is recovered from the
        # cycle gaps, and the PC pins the writer. Answers "where is this value
        # written?" given only the value.
        play_idx = 0
        hits = []
        prev_cyc: int | None = None
        for pc, reg, val, cyc in pcw:
            if prev_cyc is not None and cyc is not None and cyc - prev_cyc > PLAY_GAP:
                play_idx += 1
            prev_cyc = cyc
            if reg == find_reg and val == find_val:
                hits.append((sf + play_idx, pc, cyc))
        print(f'# {args.sid} subtune {args.subtune}: '
              f'$D4{find_reg:02X} ({_voice_role(find_reg)}) = ${find_val:02X}')
        print(f'# {len(hits)} occurrence(s) over frames {sf}-{ef} '
              f'(play index by cycle gap; PC = the exact store)')
        if not hits:
            print('  (none — widen --frames, or the value is written to a '
                  'different register)')
        pcs = sorted({pc for _, pc, _ in hits})
        print(f'  writer PC(s): ' + ', '.join(f'${p:04X}' for p in pcs))
        for play, pc, cyc in hits[:40]:
            print(f'  p{play:<5}  PC=${pc:04X}   c{cyc}')
        if len(hits) > 40:
            print(f'  ... (+{len(hits) - 40} more)')
        return 0

    play_idx = 0
    print(f'# {args.sid} subtune {args.subtune} frames {sf}-{ef}')
    print(f'# {len(pcw)} $D4xx store(s); play() boundaries by cycle gap '
          f'(>{PLAY_GAP} cyc). PC = the exact store instruction.')
    print()
    print('  play  register             val   PC      cycle')
    prev_cyc = None
    for pc, reg, val, cyc in pcw:
        if prev_cyc is not None and cyc is not None and cyc - prev_cyc > PLAY_GAP:
            play_idx += 1
            print()
        prev_cyc = cyc
        if reg_filter is not None and reg not in reg_filter:
            continue
        cyc_s = f'c{cyc}' if cyc is not None else ''
        print(f'  p{sf + play_idx:<4}  $D4{reg:02X} {_voice_role(reg):<18}  '
              f'${val:02X}    ${pc:04X}   {cyc_s}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
