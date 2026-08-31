"""Ground-truth gate for the Rayden_Digi score model.

The composer for this family does not exist yet, so the extract needs a
verdict of its own — and it has one, because the score model PREDICTS the
whole `$D418` write stream.  This module checks that prediction against
`siddump --writelog` (libsidplayfp) write for write.

The model
---------
Every score event RE-TRIGGERS its sample from the pointer table, so the
measured stream is the concatenation of per-event prefixes of each sample's
nibble stream.  A sample runs from `start` to the in-stream terminator, then
the handler reloads the pointer from the table's second word — either DATA
(a sustain loop) or the terminator byte itself (a one-shot, after which the
voice is silent until the next trigger).

Two engine facts the stream shows and the model must carry:

  * **Re-trigger phase.**  A trigger does NOT reset the NMI vector.  With
    handler B pending, B writes one STALE nibble (the previous sample byte's
    high nibble, still in its `LDA` operand) and INCs the pointer past the
    new sample's first byte — so the event starts at sample offset 2.
  * **Idle insertions.**  Some members assert an idle level from the raster
    IRQ every frame (`lda or_mask / ora #$0A / sta $D418`), inserting a write
    without touching the digi pointer.

Two checks:

  CONTENT  the current event explains every write until the stream BREAKS,
           and each break is either an insertion or the next event's onset.
           Proves the sample start/loop pointers, the terminator, the nibble
           order, or_mask, and the score's sample sequence.
  TIMING   the NMI count each segment needed is proportional to
           sum(dur/(latch+1)) under ONE global cycles-per-tick constant.
           Proves the durations and the per-event playback latches.

⚠ They are not fully INDEPENDENT, and the reason is worth knowing.  A
re-trigger inside a long constant run of the outgoing sample is locally
invisible — the cursor sails past the boundary and only breaks where the run
ends, so every candidate near the break is wrong.  The alignment therefore
runs TWICE: pass 1 fits the tick rate from whatever aligns unambiguously,
pass 2 uses it to place those hidden onsets, and pass 2 is kept only if it
explains more of the stream.  So a member whose alignment leans heavily on
the prior has a CONTENT result that partly assumes TIMING.  `verify` reports
`run_resolved_onsets` for exactly that reason.

This only shows up over a LONG capture: at 60s all three clean members read
100%, and at full songlength the single-pass aligner lost them at 28-65%.
Measure a digi member over its full songlength — the project rule, and this
is what it catches.

The timing fit's ABSOLUTE scale is only meaningful when the NMI period is
comfortably longer than a VIC badline stall; at Spelling_Around's 67-cycle
period the engine loses ~9% of its NMIs to badlines and the fitted rate reads
low.  The residual SPREAD is the part that validates the score.
"""
from __future__ import annotations

import subprocess
import sys
from collections import Counter

from .extract import SIDDUMP, RaydenDigiUnsupported, extract_model

CONFIRM = 40      # writes a hypothesis must go on to explain
MINRUN = 6        # shortest acceptable confirmation (very short events)
BACK = 4          # how far before the observed break an onset may sit
FWD = 4           # how many writes may be unexplained at a break
PRIOR_W = 16      # base window around the predicted onset; widened
PRIOR_REL = 0.01  # proportionally, since the timing fit's own
                  # residual scales with the segment length
PRIOR_CAP = 512   # ...but bounded: the window is searched linearly,
                  # and a member with 100k-write segments otherwise
                  # spends minutes per break


def capture_d418(path, duration):
    r = subprocess.run(
        [SIDDUMP, path, '--duration', str(duration), '--writelog', '--raw',
         '--force-rsid'], capture_output=True, text=True)
    vals = []
    for line in r.stdout.splitlines():
        if '|W:' not in line:
            continue
        toks = line.split('|W:', 1)[1].strip().split(':')
        for i in range(0, len(toks) - 2, 3):
            try:
                reg, v = int(toks[i + 1], 16), int(toks[i + 2], 16)
            except ValueError:
                continue
            if reg == 0x18:
                vals.append(v)
    return vals


class _Stream:
    """head = start..terminator; cycle = loop..terminator ([] = one-shot)."""

    def __init__(self, head, cycle):
        self.head, self.cycle = head, cycle

    def at(self, k):
        """The k-th write, or None once the sample has fallen silent."""
        if k < len(self.head):
            return self.head[k]
        if not self.cycle:
            return None
        return self.cycle[(k - len(self.head)) % len(self.cycle)]

    def writes_for(self, start_off, nmis):
        """Writes emitted in `nmis` NMIs starting at sample offset
        `start_off` — the inverse of `nmis_for`, used to predict how long a
        segment should be when a constant run hides its boundary."""
        nmis = int(nmis)
        head_left = max(0, len(self.head) - start_off)
        if nmis <= head_left:
            return nmis
        w, n = head_left, nmis - head_left - 1     # -1 = the terminator NMI
        if not self.cycle or n <= 0:
            return w                                # one-shot: then silence
        full, part = divmod(n, len(self.cycle) + 1)
        return w + full * len(self.cycle) + min(part, len(self.cycle))

    def nmis_for(self, writes):
        """NMIs needed to emit `writes` writes, or None when the count
        carries no timing (a one-shot that ran to its end)."""
        if writes < len(self.head):
            return writes
        if not self.cycle:
            return None
        rest = writes - len(self.head)
        full, part = divmod(rest, len(self.cycle))
        return len(self.head) + 1 + full * (len(self.cycle) + 1) + part


def verify(sid_path, duration=60.0, quiet=False, maxskip=64):
    """Returns (ok, report dict)."""
    m = extract_model(sid_path, duration=min(duration, 20.0))
    ev = m.events
    vals = capture_d418(sid_path, duration)
    if not vals:
        raise RaydenDigiUnsupported('no $D418 writes captured')
    hi = Counter(v & 0xF0 for v in vals).most_common(1)[0][0]
    if hi != m.or_mask & 0xF0:
        raise RaydenDigiUnsupported(
            f'the stream\'s dominant high nibble ${hi:02X} contradicts the '
            f'measured or_mask ${m.or_mask:02X}')
    nib = [v & 0x0F for v in vals if (v & 0xF0) == hi]
    off_mask = [v for v in vals if (v & 0xF0) != hi]
    S = {sid_: _Stream(*m.pcm[sid_]) for sid_ in m.pcm}

    def runlen(pos, s, off, cap=CONFIRM):
        n = 0
        while n < cap and pos + n < len(nib):
            x = s.at(off + n)
            if x is None or nib[pos + n] != x:
                break
            n += 1
        return n

    base = next((c for c in range(len(nib) - CONFIRM)
                 if runlen(c, S[ev[0]['sample']], 0) >= CONFIRM), None)
    if base is None:
        raise RaydenDigiUnsupported('the stream never locks onto event 0')

    def align(cpt_prior=None):
        """Walk the stream once.  `cpt_prior` (cycles per sequencer tick, from
        a first pass) resolves the one genuinely ambiguous case: a re-trigger
        INSIDE a constant run of the outgoing sample.  There the cursor sails
        past the true boundary and only breaks where the run ends, so no
        candidate near the break is right — the onset is somewhere back
        inside the run, and only the event's predicted LENGTH says where."""
        i, pos, off, segs = 0, base, 0, []
        ins, unexplained, fail, ended, guessed = Counter(), 0, None, False, 0
        while len(segs) < 4 * len(ev):
            e = ev[i % len(ev)]
            s = S[e['sample']]
            start_off, seg_start = off, pos
            while pos < len(nib):
                x = s.at(off)
                if x is None or nib[pos] != x:
                    break
                pos += 1
                off += 1
            if pos >= len(nib):
                segs.append((i, [i], off - start_off))
                ended = True
                break
            # An INSERTION is a write after which this same sample resumes at
            # the same offset.  An ONSET may sit a few writes BEFORE the
            # observed break (the new sample's leading nibbles coincided with
            # the outgoing stream) or after it (an insertion sat at the
            # break).  Score every candidate by how much it goes on to
            # explain.
            cont = max(((runlen(pos + k, s, off), k)
                        for k in range(1, FWD + 1)), default=(0, 0))
            best = None
            for n in range(1, maxskip):
                j = i + n
                e2 = ev[j % len(ev)]
                s2 = S[e2['sample']]
                # what the timing model expects this segment to be worth
                want = None
                if cpt_prior:
                    t = sum(ev[k % len(ev)]['dur']
                            / (ev[k % len(ev)]['latch'] + 1)
                            for k in range(i, j))
                    want = s.writes_for(start_off, cpt_prior * t)
                # candidates: near the observed break, plus — with a prior —
                # a small window around where the timing model says this
                # segment should END.  That second window is what resolves a
                # re-trigger buried in a constant run, where the cursor sails
                # past the boundary and every near-break candidate is wrong.
                # Placing the window from the prediction keeps this O(1); a
                # scan of the run itself is O(80,000) on Morbital's silence.
                cands = set(range(max(seg_start, pos - BACK), pos + FWD + 1))
                if want is not None:
                    wnd = min(PRIOR_CAP, max(PRIOR_W,
                                             int(want * PRIOR_REL)))
                    lo = max(seg_start, seg_start + want - wnd)
                    cands |= set(range(lo, min(pos + FWD + 1,
                                               seg_start + want + wnd + 1)))
                for q in sorted(cands):
                    for ph in (0, 2):
                        need = (pos - q) + MINRUN if q <= pos else MINRUN
                        r = runlen(q, s2, ph, cap=max(CONFIRM, need))
                        if r < min(need, len(nib) - q):
                            continue
                        # rank: explain the most, then (with a prior) land
                        # closest to the predicted segment length
                        key = ((r, q) if want is None
                               else (r, -abs((q - seg_start) - want)))
                        if best is None or key > best[0]:
                            best = (key, q, ph, j)
                if best or e2['sample'] != e['sample']:
                    break
            if cont[0] and (best is None or cont[0] > best[0][0]
                            or best[0][0] < MINRUN):
                for k in range(cont[1]):
                    ins[nib[pos + k]] += 1
                unexplained += cont[1]
                pos += cont[1]
                continue
            if best is None:
                fail = (i, pos, e, off)
                break
            _key, npos, nph, j = best
            if npos < pos - BACK:
                guessed += 1
            unexplained += max(0, npos - pos)
            segs.append((i, list(range(i, j)),
                         max(0, off - start_off - (pos - npos))))
            i, pos, off = j, npos, nph
        return segs, ins, unexplained, fail, ended, pos, guessed

    def fit(segs):
        rows, saturated = [], 0
        for _i0, idxs, w in segs[:-1]:
            s = S[ev[idxs[0] % len(ev)]['sample']]
            n = s.nmis_for(w)
            if n is None or w == 0:
                saturated += 1
                continue
            t = sum(ev[k % len(ev)]['dur'] / (ev[k % len(ev)]['latch'] + 1)
                    for k in idxs)
            if t > 0:
                rows.append((n, t))
        if not rows:
            return None, None, saturated
        c = sum(a * b for a, b in rows) / sum(b * b for _a, b in rows)
        return c, sorted(abs(a - c * b) / (c * b) for a, b in rows), saturated

    # pass 1 fixes the tick rate from whatever aligns unambiguously; pass 2
    # uses it to place the onsets a constant run hides.  Keep pass 2 only if
    # it explains more of the stream.
    segs, ins, unexplained, fail, ended, pos, guessed = align()
    cpt0, _res0, _sat0 = fit(segs)
    if cpt0:
        alt = align(cpt0)
        if alt[5] > pos:
            segs, ins, unexplained, fail, ended, pos, guessed = alt
    cpt, res, saturated = fit(segs)

    nev = sum(len(g[1]) for g in segs)
    rep = {'ok': fail is None, 'writes': len(vals), 'digi_writes': len(nib),
           'explained': pos - base, 'or_mask': m.or_mask,
           'off_mask_writes': len(off_mask),
           'off_mask_values': sorted(set(off_mask)),
           'score_events': len(ev), 'aligned_events': nev,
           'segments': len(segs), 'unexplained': unexplained,
           'insertions': sorted(ins.items()), 'saturated': saturated,
           'cycles_per_tick': cpt, 'ended_mid_event': ended,
           'residual_median': res[len(res) // 2] if res else None,
           'residual_p90': res[int(len(res) * 0.9)] if res else None,
           'residual_worst': res[-1] if res else None,
           'timing_segments': len(res) if res else 0,
           'run_resolved_onsets': guessed}
    # CONTENT alone is not a full verdict when much of the stream went
    # through the insertion path: a member whose dominant sample is a
    # constant (Embarassed_Emotions' 1-byte $88 at $7E70) can have its event
    # boundaries hidden inside a silent run, and then the write counts — and
    # so the durations and latches — are NOT corroborated.  Say so.
    rep['timing_ok'] = bool(res) and res[int(len(res) * 0.9)] < 0.05
    rep['ambiguous'] = unexplained > len(nib) // 200
    if fail:
        i, p, e, o = fail
        x = S[e['sample']].at(o)
        rep['failure'] = (
            f'event {i} (sample {e["sample"]} ptr=${e["ptr"]:04X} '
            f'loop=${e["loop"]:04X}) breaks at write {p}/{len(nib)}, sample '
            f'offset {o} (model {"silent" if x is None else f"${x:X}"}); '
            f'stream {"".join(f"{y:X}" for y in nib[p:p + 24])}')
    if not quiet:
        _report(sid_path, rep)
    return rep['ok'], rep


def _report(sid_path, r):
    print(f'{sid_path}: {r["writes"]} $D418 writes | or_mask='
          f'${r["or_mask"]:02X} | off-mask {r["off_mask_writes"]} '
          f'{[hex(v) for v in r["off_mask_values"]]} | {r["score_events"]} '
          f'score events')
    if r['ok']:
        print(f'  CONTENT: OK — all {r["explained"]}/{r["digi_writes"]} digi '
              f'writes explained, {r["aligned_events"]} events in '
              f'{r["segments"]} distinguishable segments'
              + (f'; {r["unexplained"]} unexplained '
                 f'({r["insertions"]} insertions)' if r['unexplained'] else '')
              + (' [capture ended mid-event]' if r['ended_mid_event'] else ''))
    else:
        print(f'  CONTENT MISMATCH: {r["failure"]}')
    if r['cycles_per_tick']:
        print(f'  TIMING : cycles/tick={r["cycles_per_tick"]:.1f} '
              f'({19656 / r["cycles_per_tick"]:.4f} ticks/frame) | residual '
              f'median {r["residual_median"]:.3%}, p90 {r["residual_p90"]:.3%},'
              f' worst {r["residual_worst"]:.3%} over '
              f'{r["timing_segments"]} segments'
              + (f' ({r["saturated"]} silent/one-shot segments carry no '
                 f'timing)' if r['saturated'] else ''))
    if r['ok'] and not r['timing_ok']:
        print('  ⚠ TIMING DOES NOT CORROBORATE — the content is explainable '
              'but the event boundaries are not pinned down, so the '
              'durations and latches are unverified here.')


if __name__ == '__main__':
    path = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    ok, rep = verify(path, dur)
    sys.exit(0 if ok and rep['timing_ok'] else 1)
