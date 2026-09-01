#!/usr/bin/env python3
"""render_pair.py — render an HVSC original and its rebuild to WAV, for a
LISTENING test.

    python3 tools/render_pair.py hvsc85/MUSICIANS/H/Hubbard_Rob/Commando.sid \\
        --subtune 0 --seconds 30 --out tmp/listen

writes  tmp/listen/Commando_sub0_orig.wav
        tmp/listen/Commando_sub0_rebuild.wav

Why this exists: `tools/write_timing_delta.py` measures the PHYSICAL quantity
the core tenet's Trap B is about (how far a write moves inside its play()
burst), and `write_timing_sweep.py` ranks the corpus by it. The last step is
the owner's ear on the WORST members — a targeted listening test rather than
a blind one. Backlog item 39 (c).

⚠ DO NOT reach for a sample-level null test or a hand-rolled spectral norm on
the results. Both were tried on 2026-09-01 and both had to be withdrawn: a
sub-millisecond time shift decorrelates a 3 kHz component completely, so a
residual reports "totally different" for audio that is identical to hear, and
a magnitude-spectrum difference is not calibrated to perception (a pure time
shift scores 3.7% while what Mode 1 actually permits — a waveform change on
harmonically dense square waves — scores 20% between two renders that sound
the same). Null testing IS the right instrument for DIGI, where the writes
are the waveform, and it is the wrong one for tracker music. If a metric is
ever needed here, it is a real perceptual one (PEAQ, bark-band loudness),
never a hand-rolled norm.

48 kHz mono 16-bit, which is what siddump's mixer produces.
"""
from __future__ import annotations

import argparse
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.tslog import ts, phase        # noqa: E402

SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')
RATE = 48000


def pcm(sid: str, subtune: int, seconds: float, force_rsid: bool) -> bytes:
    cmd = [SIDDUMP, sid, '--subtune', str(subtune + 1),
           '--duration', str(seconds), '--pcm']
    if force_rsid:
        cmd.append('--force-rsid')
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout


def write_wav(path: str, data: bytes) -> None:
    n = len(data)
    hdr = (b'RIFF' + struct.pack('<I', 36 + n) + b'WAVEfmt '
           + struct.pack('<IHHIIHH', 16, 1, 1, RATE, RATE * 2, 2, 16)
           + b'data' + struct.pack('<I', n))
    with open(path, 'wb') as f:
        f.write(hdr)
        f.write(data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('orig')
    ap.add_argument('rebuild', nargs='?',
                    help='default <orig>.sidfinity.sid')
    ap.add_argument('--subtune', type=int, default=0, help='0-indexed')
    ap.add_argument('--seconds', type=float, default=30.0)
    ap.add_argument('--out', default='tmp/listen')
    ap.add_argument('--force-rsid', action='store_true')
    a = ap.parse_args()

    reb = a.rebuild or (a.orig[:-4] + '.sidfinity.sid')
    for p in (a.orig, reb):
        if not os.path.exists(p):
            print(f'missing: {p}', file=sys.stderr)
            return 1
    outdir = os.path.join(ROOT, a.out)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.basename(a.orig)[:-4]

    with phase(f'render {base} sub {a.subtune}, {a.seconds}s x2'):
        for tag, src in (('orig', a.orig), ('rebuild', reb)):
            d = pcm(src, a.subtune, a.seconds, a.force_rsid)
            if not d:
                ts(f'  {tag}: siddump produced no PCM (RSID? try '
                   f'--force-rsid)')
                return 1
            out = os.path.join(outdir, f'{base}_sub{a.subtune}_{tag}.wav')
            write_wav(out, d)
            ts(f'  {tag}: {len(d) // 2} samples '
               f'({len(d) / 2 / RATE:.1f}s) -> {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
