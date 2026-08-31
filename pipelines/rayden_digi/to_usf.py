"""Rayden_Digi — typed model → USF objects (digi channel only, for now).

Mapping:

    digi { technique: volume_4bit, or_mask, idle_level }
    sample_instrument N { sample, rate_cycles }     one per engine sample id
    subtune 0 music { digi_voice { orderlist, patterns } }

Each score event is one row: `instr` is STATED only where the score states a
sample command (a rate-only command re-triggers the current sample), and
`rate=$XXXX` is stated only where the event's playback latch differs from the
instrument's default — the elidable-default discipline `usf_spec_lint`
enforces.  Two-level members map their block orderlist straight onto
`Orderlist` + `Pattern`; single-level members are a one-entry looping
orderlist.

⛔ **This does not yet write a member's `.usf`.**  Two things are missing and
both are deliberate rather than forgotten:

  * The sample LOOP POINT has no home in `SampleInstrument`, so any member
    with a sustaining sample is REFUSED here — backlog item 38, parked for
    the owner rather than smuggled through `params`.
  * These files carry MUSIC (DMC, or Rob Hubbard on Spelling_Around) beside
    the digi channel.  A `.usf` holding only the digi voice would be an
    incomplete description of the tune, and every corpus tool would then
    treat it as the member's artifact.  So the writer builds objects for
    round-tripping; storing them waits for the music side.
"""
from __future__ import annotations

from collections import Counter

from src.usf.types import (
    DigiConfig, InitState, MusicSubtune, Orderlist, Pattern, NoteRow,
    Pitch, InstrumentRef, PsidMeta, Params, SampleInstrument, UsfFile,
    VoiceBlock,
)

from .extract import RaydenDigiUnsupported, extract_model


def _blocks(m):
    """Segment the score into orderlist entries.

    A two-level member changes its ORDERLIST pointer between blocks; a
    single-level one has just the looping score stream.  Returns
    (entries, {block id: [event index]}).
    """
    if not m.seq['two_level']:
        return [0], {0: list(range(len(m.events)))}
    entries, blocks, cur = [], {}, None
    for n, e in enumerate(m.events):
        if cur is None or e['order'] != cur:
            cur = e['order']
            entries.append(cur)
            blocks[cur] = []
        blocks[cur].append(n)
    # the orderlist is a sequence of BLOCK indices; the same block may recur.
    # Key patterns by the score-stream address they start at, so a repeated
    # block is one pattern played twice rather than two identical patterns.
    by_stream, ids, seq = {}, {}, []
    for pos, o in enumerate(entries):
        start = m.events[blocks[o][0]]['stream']
        if start not in by_stream:
            by_stream[start] = len(by_stream)
            ids[by_stream[start]] = blocks[o]
        seq.append(by_stream[start])
    return seq, ids


def model_to_usf(m, sample_files: dict) -> UsfFile:
    """Build the UsfFile.  `sample_files` maps engine sample id -> sidecar
    filename; the caller writes the FLACs (this module never touches disk)."""
    sustaining = [s for s, (start, loop) in m.samples.items()
                  if m.pcm[s][1]]
    if sustaining:
        raise RaydenDigiUnsupported(
            f'samples {sorted(sustaining)} SUSTAIN by looping and '
            f'SampleInstrument has no loop point — backlog item 38 '
            f'(owner decision), not to be worked around via params')
    # per-instrument default rate = the latch it is most often triggered at
    latches = {}
    for e in m.events:
        latches.setdefault(e['sample'], Counter())[e['latch']] += 1
    instruments = [
        SampleInstrument(id=s, sample=sample_files[s],
                         rate_cycles=latches[s].most_common(1)[0][0])
        for s in sorted(m.samples)]
    default_rate = {s: latches[s].most_common(1)[0][0] for s in latches}

    seq, blocks = _blocks(m)
    patterns, prev_sample = [], None
    for pid in sorted(blocks):
        rows = []
        for n in blocks[pid]:
            e = m.events[n]
            flags = ()
            if e['latch'] != default_rate[e['sample']]:
                flags = (f'rate=${e["latch"]:04X}',)
            rows.append(NoteRow(
                pitch=Pitch.rest(), duration=e['dur'],
                instr=(InstrumentRef(e['sample'])
                       if e['sample'] != prev_sample else None),
                fx_flags=flags))
            prev_sample = e['sample']
        patterns.append(Pattern(id=pid, length=sum(r.duration for r in rows),
                                rows=rows))
    ol = Orderlist(entries=seq, loop_to=m.loop_at if m.loop_at is not None
                   else 0)
    sub = MusicSubtune(id=0, tempo=1, voices=[],
                       digi_voice=VoiceBlock(id=0, orderlist=ol,
                                             patterns=patterns))
    meta = m.meta
    return UsfFile(
        psid=PsidMeta(title=meta['title'], author=meta['author'],
                      released=meta['released'], clock=meta['clock'],
                      sid=meta['sid_model'], start_song=meta['start_song'],
                      speed=meta['speed']),
        params=Params(fields={}),
        # no SID priming is known from the digi side alone; the
        # music extract will own init when it lands
        init=InitState(),
        digi=DigiConfig(technique='volume_4bit', or_mask=m.or_mask,
                        idle_level=m.idle_level),
        sample_instruments=instruments,
        subtunes=[sub])


def roundtrip(sid_path, duration=20.0):
    """Build the objects and prove `parse(write(x)) == x` — the writer
    guarantee that makes any later change to this path .sid-byte-safe.
    Rayden is the FIRST producer of the per-row `rate=` override, so this
    exercises grammar territory nothing else has."""
    from src.usf import parser as usf_parser, writer as usf_writer
    m = extract_model(sid_path, duration=duration)
    files = {s: f'x.sample{s}.flac' for s in m.samples}
    usf = model_to_usf(m, files)
    text = usf_writer.write(usf)
    back = usf_parser.parse(text)
    return usf, text, back
