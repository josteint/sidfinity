"""inst_program.py — Phase 3 extractor: observe the original Commando SID
running in py65, segment it into per-note register-write captures, and
group them by instrument.

This is the OBSERVATION half of Phase 3 (step 3.1). It does not yet
generalise across occurrences (3.2) or emit a `USFInstrument2` literal
(3.3) — it produces raw `CaptureResult` data: for every note that plays,
the exact ordered SID register writes the original engine performed,
frame by frame.

Ground-truth note: py65 runs Hubbard's actual 6502 binary here, so this
is an OBSERVATION tool, not a verdict. Phase 3.5 verifies the emitted
instrument against `siddump --writelog`, which remains the authority
(see docs/usf_instrument_program_plan.md and feedback_ground_truth).

Usage:
    python3 -m pipelines.hubbard.inst_program            # summary table
    python3 -m pipelines.hubbard.inst_program 12         # dump inst 12
    python3 -m pipelines.hubbard.inst_program 12 600     # ... 600 frames
"""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass, field
from typing import Optional

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

# Default canary: the Commando SID Phase 0 captured its baseline from.
SID_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_original.sid')

# Commando voice-state arrays ($54xx,X, X = voice 0/1/2). Addresses from
# hubbard_emu.py / docs/hubbard_commando_disassembly.s.
VS_DUR     = 0x54F2   # duration countdown
VS_NOTEIDX = 0x54EF   # index of the current note within its pattern
VS_PITCH   = 0x54FB   # current pitch (semitone)
VS_INSTR   = 0x54FE   # current instrument number
G_FRAMECTR = 0x5525   # global frame counter (vibrato / arpeggio phase)

# Per-voice SID register block: V1 = $D400..$D406, V2 = $D407..$D40D,
# V3 = $D40E..$D414. Within a voice: freq_lo/hi, pw_lo/hi, ctrl, ad, sr.
SID_BASE = 0xD400
REG_NAMES = ['freq_lo', 'freq_hi', 'pw_lo', 'pw_hi', 'ctrl', 'ad', 'sr']


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------

@dataclass
class NoteOccurrence:
    """One note as the engine actually played it.

    `writes[k]` is the ordered list of `(reg, value)` pairs the engine
    wrote to THIS voice's registers on frame-offset `k` of the note
    (`reg` is 0..6 within the voice — see REG_NAMES). `k == 0` is the
    note-start frame.
    """
    voice: int
    instrument: int                       # VS_INSTR masked to 0x3F
    raw_instr: int                        # VS_INSTR including flag bits
    pitch: int
    start_frame: int                      # play() index the note loaded on
    frame_ctr0: int = 0                   # global frame counter at note start
    subtune: int = 0                      # subtune this occurrence is from
    writes: list[list[tuple[int, int]]] = field(default_factory=list)

    @property
    def n_frames(self) -> int:
        return len(self.writes)


@dataclass
class CaptureResult:
    sid_path: str
    n_frames: int
    occurrences: list[NoteOccurrence]
    # raw_frames[k] = the full ordered (reg_offset 0..20, value) write list
    # the engine produced on play() call k — every voice + drum, unsplit.
    raw_frames: list[list[tuple[int, int]]] = field(default_factory=list)

    def for_instrument(self, inst_idx: int) -> list[NoteOccurrence]:
        return [o for o in self.occurrences if o.instrument == inst_idx]

    def instruments(self) -> list[int]:
        return sorted({o.instrument for o in self.occurrences})


# ---------------------------------------------------------------------------
# SID loading
# ---------------------------------------------------------------------------

def _load_sid(path: str):
    """Return (load_addr, init_addr, play_addr, code_bytes, num_songs)."""
    with open(path, 'rb') as f:
        d = f.read()
    if d[:4] not in (b'PSID', b'RSID'):
        raise ValueError(f'not a SID file: {path}')
    data_offset = struct.unpack('>H', d[6:8])[0]
    load_addr = struct.unpack('>H', d[8:10])[0]
    init_addr = struct.unpack('>H', d[10:12])[0]
    play_addr = struct.unpack('>H', d[12:14])[0]
    num_songs = struct.unpack('>H', d[14:16])[0]
    code = d[data_offset:]
    if load_addr == 0:                       # load address prepended to data
        load_addr = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return load_addr, init_addr, play_addr, code, num_songs


# ---------------------------------------------------------------------------
# Capture
# ---------------------------------------------------------------------------

def capture(sid_path: str = SID_PATH, n_frames: int = 1500,
            subtune: int = 0) -> CaptureResult:
    """Run `sid_path` in py65 for `n_frames` play() calls, capturing every
    SID register write and segmenting the run into NoteOccurrences."""
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory

    load_addr, init_addr, play_addr, code, _ = _load_sid(sid_path)

    mem = ObservableMemory()
    mem.write(load_addr, list(code))

    # Ordered SID writes for the frame currently being executed.
    frame_writes: list[tuple[int, int]] = []

    def on_sid_write(address, value):
        frame_writes.append((address - SID_BASE, value))
        return None

    mem.subscribe_to_write(range(SID_BASE, SID_BASE + 21), on_sid_write)

    m = MPU()
    m.memory = mem

    def call(entry: int, acc: int = 0, budget: int = 200000):
        """Call a subroutine at `entry` with A=acc; run until it RTSes
        back to the $F000 BRK sentinel (memory there is zero-filled)."""
        m.a = acc
        m.stPush(0xFF)            # return address $EFFF -> RTS lands at $F000
        m.stPush(0xEF)
        m.pc = entry
        for _ in range(budget):
            if m.memory[m.pc] == 0x00:    # BRK sentinel
                break
            m.step()
        else:
            raise RuntimeError(f'routine at ${entry:04X} never returned')

    # init() — A = subtune number (0-indexed), per PSID convention.
    call(init_addr, acc=subtune)

    # Per-frame run. Snapshot voice state AFTER each play() so the
    # note-load that play() performed this frame is visible.
    frames: list[tuple[list[dict], list[list[tuple[int, int]]]]] = []
    raw_frames: list[list[tuple[int, int]]] = []
    for _ in range(n_frames):
        frame_writes.clear()
        call(play_addr, budget=100000)

        state = [{
            'dur':      m.memory[VS_DUR + v],
            'note_idx': m.memory[VS_NOTEIDX + v],
            'pitch':    m.memory[VS_PITCH + v],
            'instr':    m.memory[VS_INSTR + v],
        } for v in range(3)]
        frame_ctr = m.memory[G_FRAMECTR]

        raw_frames.append(list(frame_writes))
        # Split this frame's writes per voice (regs 0..6 within the voice).
        voice_writes: list[list[tuple[int, int]]] = [[], [], []]
        for off, val in frame_writes:
            v, r = divmod(off, 7)
            if v < 3:
                voice_writes[v].append((r, val))
        frames.append((state, voice_writes, frame_ctr))

    occurrences = _segment(frames)
    for o in occurrences:
        o.subtune = subtune
    return CaptureResult(sid_path=sid_path, n_frames=n_frames,
                         occurrences=occurrences, raw_frames=raw_frames)


def _segment(frames) -> list[NoteOccurrence]:
    """Cut the per-frame stream into NoteOccurrences. A new occurrence
    starts on a voice the frame its `note_idx` changes.

    `prev_note_idx` is seeded with frame 0's note_idx so no occurrence is
    opened for the song-start warmup — the frames before the first real
    note loads (still cold-start pitch 0 / stale instrument) belong to no
    note and are discarded."""
    occurrences: list[NoteOccurrence] = []
    open_occ: list[Optional[NoteOccurrence]] = [None, None, None]
    prev_note_idx = ([frames[0][0][v]['note_idx'] for v in range(3)]
                     if frames else [None, None, None])

    for fi, (state, voice_writes, frame_ctr) in enumerate(frames):
        for v in range(3):
            ni = state[v]['note_idx']
            if ni != prev_note_idx[v]:
                # note_idx advanced -> a new note loaded on this voice.
                if open_occ[v] is not None:
                    occurrences.append(open_occ[v])
                raw = state[v]['instr']
                open_occ[v] = NoteOccurrence(
                    voice=v,
                    instrument=raw & 0x3F,
                    raw_instr=raw,
                    pitch=state[v]['pitch'],
                    start_frame=fi,
                    frame_ctr0=frame_ctr,
                )
                prev_note_idx[v] = ni
            if open_occ[v] is not None:
                open_occ[v].writes.append(voice_writes[v])

    # The occurrences still open when the capture window ends are
    # truncated mid-note — drop them rather than emit a short fragment.
    return occurrences


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _fmt_writes(frame_writes: list[tuple[int, int]]) -> str:
    if not frame_writes:
        return '-'
    return ' '.join(f'{REG_NAMES[r]}={v:02X}' for r, v in frame_writes)


def _print_summary(cap: CaptureResult) -> None:
    print(f'{cap.sid_path}  ({cap.n_frames} frames, '
          f'{len(cap.occurrences)} note occurrences)')
    print(f'{"inst":>4}  {"#occ":>4}  {"voices":>8}  {"pitches":>14}  '
          f'{"frame-len min/med/max":>22}')
    for idx in cap.instruments():
        occ = cap.for_instrument(idx)
        voices = sorted({o.voice for o in occ})
        pitches = sorted({o.pitch for o in occ})
        lens = sorted(o.n_frames for o in occ)
        med = lens[len(lens) // 2]
        prange = (f'{pitches[0]}..{pitches[-1]}'
                  if len(pitches) > 1 else str(pitches[0]))
        print(f'{idx:>4}  {len(occ):>4}  {str(voices):>8}  {prange:>14}  '
              f'{lens[0]:>6}/{med}/{lens[-1]}')


def _dump_instrument(cap: CaptureResult, idx: int) -> None:
    occ = cap.for_instrument(idx)
    if not occ:
        print(f'instrument {idx}: no occurrences in {cap.n_frames} frames')
        return
    print(f'instrument {idx}: {len(occ)} occurrences')
    o = occ[0]
    print(f'  first occurrence: voice {o.voice}  pitch {o.pitch}  '
          f'start_frame {o.start_frame}  raw_instr ${o.raw_instr:02X}  '
          f'{o.n_frames} frames')
    for k, fw in enumerate(o.writes):
        print(f'    +{k:<3} {_fmt_writes(fw)}')


def main(argv: list[str]) -> None:
    inst_idx = int(argv[0]) if len(argv) > 0 else None
    n_frames = int(argv[1]) if len(argv) > 1 else 1500
    cap = capture(n_frames=n_frames)
    if inst_idx is None:
        _print_summary(cap)
    else:
        _dump_instrument(cap, inst_idx)


if __name__ == '__main__':
    main(sys.argv[1:])
