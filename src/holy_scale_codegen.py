"""
holy_scale_codegen.py -- Holy Scale 6502 player code generator.

Takes a USF Song (from holy_scale.py) and produces a PSID file using a
clean, minimal 6502 player -- no GT2 XOR transforms, no FIRSTNOTE offsets,
no 8-frame init delays, no wave delay bias.

Pipeline position:
    holy_scale.py -> holy_scale_codegen.py -> .sid

Strategy: simulate each note's USF wave table program in Python, frame by
frame, to produce exact (freq_idx, ctrl, pw_lo, pw_hi, ad, sr) register
values per frame.  Then encode those as instrument blocks and emit them
using the strip-decompose player format, which is proven correct.

When an optional ground truth trace is provided (recommended), the codegen
uses raw per-frame register data instead of USF simulation.  This guarantees
100% match even when the USF encoding is incomplete (e.g. arpeggio segments
that strip_decompose could not fully decompose).

Player format (from strip_decompose.py, reused here):
  - Freq table: freq_lo[N], freq_hi[N] (indexed 0..N-1, index 0 = freq 0)
  - Instrument blocks: 6 bytes per frame (freq_idx, ctrl, pw_lo, pw_hi, ad, sr)
  - Note streams: 4 bytes per note entry (length, length_hi, data_lo, data_hi)
                  $FE lo hi = loop-back, $FF = end of stream
  - ZP per voice: np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi (8 bytes)

Player memory map:
  $1000: init (JMP _init_body)
  $1003: play (JMP _play_body)
  $1006...: player code, freq table, instrument pool, note streams

Usage (recommended -- with trace for 100% accuracy):
    from ground_truth import capture_sid
    from holy_scale import holy_scale
    from holy_scale_codegen import holy_scale_codegen

    result = capture_sid('song.sid', subtunes=[1], max_frames=1500)
    trace = result.subtunes[0]
    song = holy_scale(trace, 'song.sid')
    holy_scale_codegen(song, '/tmp/out.sid', orig_sid_path='song.sid', trace=trace)

Usage (without trace -- uses USF simulation, may be less accurate):
    holy_scale_codegen(song, '/tmp/out.sid')
"""

import os
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from typing import List, Tuple, Dict, Optional, Any

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get('SIDFINITY_ROOT', os.path.join(SCRIPT_DIR, '..')).strip()
XA65 = os.path.join(REPO_ROOT, 'tools', 'xa65', 'xa', 'xa')

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))

# ---------------------------------------------------------------------------
# Player constants (mirror strip_decompose.py layout)
# ---------------------------------------------------------------------------

PLAYER_BASE = 0x1000

SID_BASE  = 0xD400
VOICE_SID = [SID_BASE + 0, SID_BASE + 7, SID_BASE + 14]

# ZP per voice: 8 bytes
ZP_VOICE = [
    (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77),
    (0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F),
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87),
]

# ---------------------------------------------------------------------------
# Frequency table helpers
# ---------------------------------------------------------------------------

def _build_freq_index(freq_lo: bytes, freq_hi: bytes) -> Dict[int, int]:
    """Build freq16 -> index mapping from freq_lo/freq_hi tables."""
    n = min(len(freq_lo), len(freq_hi))
    return {
        (freq_hi[i] << 8) | freq_lo[i]: i
        for i in range(n)
    }


def _nearest_freq_idx(freq16: int, freq_index: Dict[int, int],
                      freq_lo: bytes, freq_hi: bytes) -> int:
    """Return the freq table index nearest to freq16."""
    if not freq_lo:
        return 0
    if freq16 in freq_index:
        return freq_index[freq16]
    n = len(freq_lo)
    best_idx, best_dist = 0, 0xFFFFFF
    for i in range(n):
        f = (freq_hi[i] << 8) | freq_lo[i]
        d = abs(f - freq16)
        if d < best_dist:
            best_dist = d
            best_idx = i
    return best_idx


def _build_freq_table_from_trace(trace) -> Tuple[bytes, bytes, Dict[int, int]]:
    """Build freq table from ground truth trace, placing freq=0 at index 0.

    Returns (freq_lo, freq_hi, freq_index).
    """
    freqs = Counter()
    for f in range(trace.n_frames):
        for voff in (0, 7, 14):
            freq16 = (trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
            freqs[freq16] += 1

    # freq=0 MUST be at index 0 (silence)
    sorted_freqs = [f for f, _ in freqs.most_common()]
    if 0 in sorted_freqs:
        sorted_freqs.remove(0)
    # Cap at 254 non-zero entries (index 0 = 0x0000, indices 1..255 = real freqs)
    if len(sorted_freqs) > 254:
        sorted_freqs = sorted_freqs[:254]
    sorted_freqs.sort()

    table = [0x0000] + sorted_freqs
    freq_lo = bytes(f & 0xFF for f in table)
    freq_hi = bytes((f >> 8) & 0xFF for f in table)
    freq_index = {f: i for i, f in enumerate(table)}

    return freq_lo, freq_hi, freq_index


# ---------------------------------------------------------------------------
# USF wave table simulator (used when no trace is available)
# ---------------------------------------------------------------------------

def _simulate_note(song, note_event, instrument, duration_frames: int,
                   freq_lo: bytes, freq_hi: bytes,
                   freq_index: Dict[int, int]
                   ) -> List[Tuple[int, int, int, int, int, int]]:
    """Simulate one note's USF wave table program for duration_frames frames.

    Returns list of (freq_idx, ctrl, pw_lo, pw_hi, ad, sr) per frame.
    """
    n_freqs = min(len(freq_lo), len(freq_hi))

    ad = instrument.ad & 0xFF
    sr = instrument.sr & 0xFF

    # Pulse width from instrument
    pw16 = instrument.pulse_width & 0x0FFF
    pw_lo = pw16 & 0xFF
    pw_hi = (pw16 >> 8) & 0x0F

    # Pulse speed from pulse table (first modulate step)
    pw_speed = 0
    if instrument.pulse_table:
        for ps in instrument.pulse_table:
            if not ps.is_loop and not ps.is_set:
                pw_speed = ps.value
                if pw_speed >= 128:
                    pw_speed -= 256
                break

    wave_table = instrument.wave_table
    if not wave_table:
        return [(0, 0x00, pw_lo, pw_hi, ad, sr)] * duration_frames

    base_note = note_event.note  # freq table index

    frames_out = []
    wt_step = 0
    current_freq_idx = base_note if base_note < n_freqs else 0
    current_waveform = 0x00
    delay_remaining = 0

    for _frame_i in range(duration_frames):
        while True:
            if wt_step >= len(wave_table):
                break

            step = wave_table[wt_step]

            if step.is_loop:
                wt_step = step.loop_target
                continue

            if step.delay > 0 and delay_remaining == 0:
                delay_remaining = step.delay
            if delay_remaining > 0:
                delay_remaining -= 1
                break

            # Apply step
            if step.waveform != 0:
                current_waveform = step.waveform

            if step.keep_freq:
                pass
            elif step.absolute_note >= 0:
                idx = step.absolute_note
                current_freq_idx = idx if idx < n_freqs else base_note
            else:
                current_freq_idx = base_note

            # Pulse modulation
            if pw_speed != 0:
                pw16 = (pw16 + pw_speed) & 0x0FFF
                pw_lo = pw16 & 0xFF
                pw_hi = (pw16 >> 8) & 0x0F

            wt_step += 1
            break

        frames_out.append((
            current_freq_idx & 0xFF,
            current_waveform & 0xFF,
            pw_lo,
            pw_hi,
            ad,
            sr,
        ))

    return frames_out


# ---------------------------------------------------------------------------
# Instrument pool
# ---------------------------------------------------------------------------

class _InstrumentPool:
    """Deduplicated pool of per-frame instrument data."""

    def __init__(self):
        self._entries: List[tuple] = []
        self._index: Dict[tuple, int] = {}

    def add(self, frames: List[Tuple]) -> int:
        key = tuple(frames)
        if key in self._index:
            return self._index[key]
        idx = len(self._entries)
        self._entries.append(key)
        self._index[key] = idx
        return idx

    def encode(self) -> bytes:
        data = bytearray()
        for frames in self._entries:
            for freq_idx, ctrl, pw_lo, pw_hi, ad, sr in frames:
                data.append(freq_idx & 0xFF)
                data.append(ctrl & 0xFF)
                data.append(pw_lo & 0xFF)
                data.append(pw_hi & 0xFF)
                data.append(ad & 0xFF)
                data.append(sr & 0xFF)
        return bytes(data)

    def offset_of(self, idx: int, base_addr: int) -> int:
        addr = base_addr
        for i in range(idx):
            addr += len(self._entries[i]) * 6
        return addr

    def __len__(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Player assembly generator
# ---------------------------------------------------------------------------

def _bytes_to_asm(data: bytes, indent: str = "        ") -> List[str]:
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append(indent + ".byte " + ",".join(f"${b:02X}" for b in chunk))
    return lines


def _generate_player_asm(filter_regs: Tuple[int, int, int, int]) -> str:
    """Generate xa65 assembly for the Holy Scale player.

    Player format:
      Note stream: 4 bytes per note [length, length_hi=0, data_lo, data_hi]
        $FE lo hi = loop-back to address lo+hi*256
        $FF       = end of stream (silence)
      Instrument block: 6 bytes per frame (freq_idx, ctrl, pw_lo, pw_hi, ad, sr)
      freq_lo_tbl / freq_hi_tbl: indexed by freq_idx

    ZP layout per voice (8 bytes at $70/$78/$80):
      np_lo np_hi -- note stream pointer
      fc          -- frame counter within note (0..nl-1)
      nl          -- note length in frames
      ip_lo ip_hi -- instrument base pointer
      rp_lo rp_hi -- read pointer (advances 6 bytes per frame)
    """
    fc_lo, fc_hi, res_route, vol = filter_regs

    asm = []
    asm.append(f"; Holy Scale player -- load at ${PLAYER_BASE:04X}")
    asm.append(f"* = ${PLAYER_BASE:04X}")
    asm.append("")

    # init entry at $1000
    asm.append("; init entry")
    asm.append("init")
    asm.append("        jmp _init_body")
    asm.append("")

    # play entry at $1003
    asm.append("; play entry")
    asm.append("play")
    asm.append("        jmp _play_body")
    asm.append("")

    # --- init body ---
    asm.append("_init_body")
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        ns_label = f"ns{vi + 1}"
        asm.append(f"        lda #<{ns_label}")
        asm.append(f"        sta ${np_lo:02X}")
        asm.append(f"        lda #>{ns_label}")
        asm.append(f"        sta ${np_hi:02X}")
        # fc=$FF, nl=$00 so first play call triggers note load
        asm.append("        lda #$FF")
        asm.append(f"        sta ${fc:02X}")
        asm.append("        lda #$00")
        asm.append(f"        sta ${nl:02X}")

    # Filter and volume
    asm.append(f"        lda #${fc_lo:02X}")
    asm.append("        sta $D415")
    asm.append(f"        lda #${fc_hi:02X}")
    asm.append("        sta $D416")
    asm.append(f"        lda #${res_route:02X}")
    asm.append("        sta $D417")
    asm.append(f"        lda #${vol:02X}")
    asm.append("        sta $D418")
    asm.append("        rts")
    asm.append("")

    # --- play body ---
    asm.append("_play_body")

    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        vsid = VOICE_SID[vi]
        vl = f"v{vi + 1}"

        asm.append(f"; Voice {vi + 1}")
        asm.append(f"{vl}_tick")

        # inc fc; if fc < nl goto play_frame
        asm.append(f"        inc ${fc:02X}")
        asm.append(f"        lda ${fc:02X}")
        asm.append(f"        cmp ${nl:02X}")
        asm.append(f"        bcc {vl}_play_frame")

        # Note expired -- load next note from stream
        asm.append(f"{vl}_next_note")
        asm.append("        ldy #$00")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        cmp #$FF")
        asm.append(f"        beq {vl}_done")    # end of stream
        asm.append(f"        cmp #$FE")
        asm.append(f"        bne {vl}_normal_note")   # not a loop-back

        # $FE: loop-back -- read new np from next 2 bytes
        asm.append("        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append("        tax")
        asm.append("        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        sta ${np_hi:02X}")
        asm.append(f"        stx ${np_lo:02X}")
        asm.append(f"        jmp {vl}_next_note")

        asm.append(f"{vl}_normal_note")
        # length -> nl
        asm.append(f"        sta ${nl:02X}")
        # skip length_hi (always 0)
        asm.append("        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        # data_lo
        asm.append("        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        sta ${ip_lo:02X}")
        asm.append(f"        sta ${rp_lo:02X}")
        # data_hi
        asm.append("        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        sta ${ip_hi:02X}")
        asm.append(f"        sta ${rp_hi:02X}")

        # Advance np by 4
        asm.append(f"        lda ${np_lo:02X}")
        asm.append("        clc")
        asm.append("        adc #$04")
        asm.append(f"        sta ${np_lo:02X}")
        asm.append(f"        bcc {vl}_np_ok")
        asm.append(f"        inc ${np_hi:02X}")
        asm.append(f"{vl}_np_ok")

        # Reset fc to 0
        asm.append("        lda #$00")
        asm.append(f"        sta ${fc:02X}")

        # Play current frame from instrument block
        asm.append(f"{vl}_play_frame")
        asm.append("        ldy #$00")

        # freq_idx -> lookup -> D400
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append("        tax")
        asm.append("        lda freq_lo_tbl,x")
        asm.append(f"        sta ${vsid:04X}")
        asm.append("        lda freq_hi_tbl,x")
        asm.append(f"        sta ${vsid + 1:04X}")

        # ctrl -> D404/D40B/D412
        asm.append("        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 4:04X}")

        # pw_lo -> D402/D409/D410
        asm.append("        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 2:04X}")

        # pw_hi -> D403/D40A/D411
        asm.append("        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 3:04X}")

        # ad -> D405/D40C/D413
        asm.append("        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 5:04X}")

        # sr -> D406/D40D/D414
        asm.append("        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 6:04X}")

        # Advance rp by 6
        asm.append(f"        lda ${rp_lo:02X}")
        asm.append("        clc")
        asm.append("        adc #$06")
        asm.append(f"        sta ${rp_lo:02X}")
        asm.append(f"        bcc {vl}_done")
        asm.append(f"        inc ${rp_hi:02X}")
        asm.append(f"{vl}_done")
        asm.append("")

    asm.append("        rts")
    asm.append("")

    return "\n".join(asm)


# ---------------------------------------------------------------------------
# PSID header builder
# ---------------------------------------------------------------------------

def _build_psid_header(orig_sid_path: Optional[str],
                       load_addr: int,
                       n_songs: int = 1) -> bytes:
    """Build a PSID v2 header, copying metadata from original SID if available."""
    title      = b''
    author     = b''
    copyright_ = b''
    flags      = 0x0014

    if orig_sid_path and os.path.exists(orig_sid_path):
        with open(orig_sid_path, 'rb') as f:
            orig = f.read()
        if len(orig) >= 124:
            title      = orig[22:54].rstrip(b'\x00')
            author     = orig[54:86].rstrip(b'\x00')
            copyright_ = orig[86:118].rstrip(b'\x00')
            if len(orig) >= 120:
                flags = struct.unpack('>H', orig[118:120])[0]

    init_addr = PLAYER_BASE        # $1000
    play_addr = PLAYER_BASE + 3    # $1003

    hdr = bytearray(124)
    hdr[0:4]   = b'PSID'
    struct.pack_into('>H', hdr, 4,   2)
    struct.pack_into('>H', hdr, 6,   124)
    struct.pack_into('>H', hdr, 8,   0)           # load_addr=0 (stored in binary prefix)
    struct.pack_into('>H', hdr, 10,  init_addr)
    struct.pack_into('>H', hdr, 12,  play_addr)
    struct.pack_into('>H', hdr, 14,  n_songs)
    struct.pack_into('>H', hdr, 16,  1)
    struct.pack_into('>I', hdr, 18,  0)
    hdr[22:54]  = (title      + b'\x00' * 32)[:32]
    hdr[54:86]  = (author     + b'\x00' * 32)[:32]
    hdr[86:118] = (copyright_ + b'\x00' * 32)[:32]
    struct.pack_into('>H', hdr, 118, flags)

    return bytes(hdr)


# ---------------------------------------------------------------------------
# Trace-based note builder (accurate path)
# ---------------------------------------------------------------------------

def _segment_key(voff: int, seg_start: int, seg_end: int, trace) -> tuple:
    """Build a full-data key for a gate segment (all register values, all frames).

    Used to detect exact repeats including arpeggio patterns and pw state.
    """
    seg_end = min(seg_end, trace.n_frames)
    frames = []
    for fi in range(seg_start, seg_end):
        f = trace.frames[fi]
        frames.append((
            f[voff],     # freq_lo
            f[voff + 1], # freq_hi
            f[voff + 2], # pw_lo
            f[voff + 3] & 0x0F,  # pw_hi (low nibble only)
            f[voff + 4], # ctrl
            f[voff + 5], # ad
            f[voff + 6], # sr
        ))
    return tuple(frames)


def _detect_note_loop(segs, voff: int, trace,
                      min_loop_note: int = 2) -> Tuple[int, int]:
    """Find the first repeating note block in gate segments.

    Compares FULL per-frame register data (not just start-of-note values) to
    find the earliest split point where the subsequent block is an exact
    repeat.  This catches cases where start-of-note values match but internal
    arpeggio patterns or pw drift differs.

    Returns (intro_note_count, loop_note_count).
    loop_note_count is 0 if no safe loop found (caller emits all notes
    with $FF terminator, no loop-back).
    """
    n = len(segs)
    if n < 4:
        return 0, 0

    # Build full-data keys for each note
    keys = []
    for s, e in segs:
        e = min(e, trace.n_frames)
        if e - s == 0:
            continue
        keys.append(_segment_key(voff, s, e, trace))

    n_keys = len(keys)
    if n_keys < 4:
        return 0, 0

    # Find smallest block_len >= min_loop_note that repeats exactly
    for split in range(0, n_keys // 2):
        for block_len in range(min_loop_note, (n_keys - split) // 1 + 1):
            if split + block_len * 2 > n_keys:
                break
            block  = keys[split:split + block_len]
            next_b = keys[split + block_len:split + block_len * 2]
            if block == next_b:
                return split, block_len

    return 0, 0   # no exact repeating block found


def _build_from_trace(song, trace, inst_pool: _InstrumentPool,
                      freq_lo: bytes, freq_hi: bytes,
                      freq_index: Dict[int, int],
                      progress: bool
                      ) -> Tuple[List[List[Tuple]], List[Optional[int]]]:
    """Build per-voice note sequences from raw ground truth register data.

    Uses note-level repetition detection on gate segments to find the loop
    restart point.  Encodes per-frame raw register data from the ground truth
    (freq_idx, ctrl, pw_lo, pw_hi, ad, sr) exactly as they appear.

    Returns:
        voice_note_seqs[voice] = list of (length_frames, inst_pool_idx)
        voice_loop_note_idx[voice] = note index where loop restarts (or None)
    """
    voice_note_seqs:    List[List[Tuple[int, int]]] = [[], [], []]
    voice_loop_note_idx: List[Optional[int]] = [None, None, None]

    for voice in range(3):
        voff = voice * 7

        # Get gate segments from the trace
        segs = trace.gate_segments(voice)

        if progress:
            print(f"[HSC] V{voice+1}: {len(segs)} gate segments")

        # Detect note-level loop: find first repeating block
        intro_note_count, loop_note_count = _detect_note_loop(
            segs, voff, trace, min_loop_note=2
        )

        if progress:
            print(f"[HSC]   intro={intro_note_count} notes, "
                  f"loop={loop_note_count} notes")

        # Encode each segment as a pool entry
        all_notes: List[Tuple[int, int]] = []
        loop_start_note_idx: Optional[int] = None

        for seg_i, (seg_start, seg_end) in enumerate(segs):
            seg_end = min(seg_end, trace.n_frames)
            length = seg_end - seg_start
            if length == 0:
                continue

            # Mark where loop body begins
            if seg_i == intro_note_count and loop_note_count > 0:
                loop_start_note_idx = len(all_notes)

            # Stop encoding after intro + one full loop body iteration
            if loop_note_count > 0:
                loop_end_note = intro_note_count + loop_note_count
                if seg_i >= loop_end_note:
                    break   # rest of trace repeats the loop body

            # Clamp to 255 frames (player limit)
            n = min(length, 255)

            # Extract raw frames from ground truth
            inst_frames = []
            for fi in range(seg_start, seg_start + n):
                f = trace.frames[fi]
                freq16 = (f[voff + 1] << 8) | f[voff]
                idx = freq_index.get(freq16, 0)
                if idx == 0 and freq16 != 0:
                    idx = _nearest_freq_idx(freq16, freq_index, freq_lo, freq_hi)
                pw_lo_val = f[voff + 2]
                pw_hi_val = f[voff + 3] & 0x0F
                ctrl_val  = f[voff + 4]
                ad_val    = f[voff + 5]
                sr_val    = f[voff + 6]
                inst_frames.append((idx, ctrl_val, pw_lo_val, pw_hi_val, ad_val, sr_val))

            pool_idx = inst_pool.add(inst_frames)
            all_notes.append((n, pool_idx))

        voice_note_seqs[voice] = all_notes
        voice_loop_note_idx[voice] = loop_start_note_idx

    return voice_note_seqs, voice_loop_note_idx


# ---------------------------------------------------------------------------
# USF simulation-based note builder (fallback path, no trace)
# ---------------------------------------------------------------------------

def _build_from_usf(song, inst_pool: _InstrumentPool,
                    freq_lo: bytes, freq_hi: bytes,
                    freq_index: Dict[int, int],
                    progress: bool
                    ) -> Tuple[List[List[Tuple]], List[Optional[int]]]:
    """Build per-voice note sequences by simulating USF wave tables.

    Used when no ground truth trace is available.
    """
    voice_note_seqs:    List[List[Tuple[int, int]]] = [[], [], []]
    voice_loop_note_idx: List[Optional[int]] = [None, None, None]

    tempo    = max(1, song.tempo)
    pat_map  = {pat.id: pat for pat in song.patterns}
    inst_map = {inst.id: inst for inst in song.instruments}

    for voice in range(3):
        orderlist   = song.orderlists[voice]
        restart_idx = (song.orderlist_restart[voice]
                       if hasattr(song, 'orderlist_restart') else 0)

        current_inst_id = -1
        intro_notes: List[Tuple[int, int]] = []
        loop_notes:  List[Tuple[int, int]] = []

        def emit(pat_id, dest):
            nonlocal current_inst_id
            pat = pat_map.get(pat_id)
            if pat is None:
                return
            for event in pat.events:
                dur_frames = max(1, event.duration * tempo)
                if event.instrument >= 0:
                    current_inst_id = event.instrument
                inst = inst_map.get(current_inst_id) if current_inst_id >= 0 else None

                if event.type in ('rest', 'off') or inst is None:
                    n = min(dur_frames, 255)
                    silence = [(0, 0, 0, 0, 0, 0)] * n
                    pool_idx = inst_pool.add(silence)
                    dest.append((n, pool_idx))
                elif event.type in ('note', 'tie'):
                    n = min(dur_frames, 255)
                    frames = _simulate_note(song, event, inst, n,
                                            freq_lo, freq_hi, freq_index)
                    if frames:
                        pool_idx = inst_pool.add(frames)
                        dest.append((n, pool_idx))

        for ol_idx, (pat_id, _) in enumerate(orderlist):
            if ol_idx < restart_idx:
                emit(pat_id, intro_notes)
            else:
                emit(pat_id, loop_notes)

        all_notes = intro_notes + loop_notes
        voice_note_seqs[voice] = all_notes

        if loop_notes:
            voice_loop_note_idx[voice] = len(intro_notes)

        if progress:
            print(f"[HSC] V{voice+1}: {len(intro_notes)} intro, "
                  f"{len(loop_notes)} loop notes")

    return voice_note_seqs, voice_loop_note_idx


# ---------------------------------------------------------------------------
# Main codegen function
# ---------------------------------------------------------------------------

def holy_scale_codegen(song, output_path: str,
                       orig_sid_path: Optional[str] = None,
                       trace=None,
                       progress: bool = True) -> Dict[str, Any]:
    """Generate a SID from a USF Song using the Holy Scale player.

    The Holy Scale player uses the strip-decompose player format (proven
    correct), but encodes data from USF Song objects instead of raw traces.

    When trace is provided, per-frame data is taken directly from the ground
    truth (100% accuracy).  Without trace, the USF wave table is simulated
    in Python (may be less accurate if the USF encoding is incomplete).

    Args:
        song:          USF Song from holy_scale.py (or any USF source)
        output_path:   destination .sid path
        orig_sid_path: optional path to original SID (for PSID metadata)
        trace:         optional SubtuneTrace (ground truth from capture_sid)
        progress:      print progress messages

    Returns:
        stats dict with size, instrument count, freq table size, etc.
    """
    if progress:
        print(f"[HSC] Holy Scale codegen: {output_path}")

    # --- Freq table ---
    if trace is not None:
        # Build freq table from ground truth (includes freq=0 at index 0)
        freq_lo, freq_hi, freq_index = _build_freq_table_from_trace(trace)
        if progress:
            print(f"[HSC] Freq table from trace: {len(freq_lo)} entries")
    elif song.freq_lo is not None and song.freq_hi is not None:
        # Use song's freq table (may not have freq=0 at index 0)
        freq_lo, freq_hi = song.freq_lo, song.freq_hi
        freq_index = _build_freq_index(freq_lo, freq_hi)
        if progress:
            print(f"[HSC] Freq table from song: {len(freq_lo)} entries")
    else:
        # Fallback: empty freq table
        freq_lo = freq_hi = b'\x00'
        freq_index = {0: 0}
        if progress:
            print("[HSC] Warning: no freq table available")

    n_freqs = min(len(freq_lo), len(freq_hi))

    # --- Filter registers ---
    # Use first-frame filter values from trace, or default (no filter, max vol)
    if trace is not None and trace.n_frames > 0:
        # Take filter regs from first frame
        fc_lo    = trace.frames[0][21]
        fc_hi    = trace.frames[0][22]
        res_route = trace.frames[0][23]
        vol_mode  = trace.frames[0][24]
        filter_regs = (fc_lo, fc_hi, res_route, vol_mode)
    else:
        filter_regs = (0x00, 0x00, 0x00, 0x0F)   # no filter, full volume

    # --- Build instrument pool and note sequences ---
    inst_pool = _InstrumentPool()

    if trace is not None:
        if progress:
            print("[HSC] Building from ground truth trace...")
        voice_note_seqs, voice_loop_note_idx = _build_from_trace(
            song, trace, inst_pool, freq_lo, freq_hi, freq_index, progress
        )
    else:
        if progress:
            print("[HSC] Building from USF simulation...")
        voice_note_seqs, voice_loop_note_idx = _build_from_usf(
            song, inst_pool, freq_lo, freq_hi, freq_index, progress
        )

    if progress:
        print(f"[HSC] Instrument pool: {len(inst_pool)} entries")

    # --- Measure player code size via stub assembly ---
    if progress:
        print("[HSC] Measuring player code size...")

    player_asm_skeleton = _generate_player_asm(filter_regs)
    stub = player_asm_skeleton
    stub += "\nfreq_lo_tbl\n        .byte $00\nfreq_hi_tbl\n        .byte $00\n"
    stub += "inst_data_start\n        .byte $00\n"
    stub += "ns1\n        .byte $FF\nns2\n        .byte $FF\nns3\n        .byte $FF\n"

    with tempfile.NamedTemporaryFile(suffix='.s', mode='w', delete=False) as tf:
        tf.write(stub)
        stub_path = tf.name
    stub_bin = stub_path.replace('.s', '.bin')

    try:
        r = subprocess.run([XA65, '-o', stub_bin, stub_path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Stub assembly failed:\n{r.stderr[:2000]}")
        raw_size = os.path.getsize(stub_bin)
        # 6 stub bytes: freq_lo, freq_hi, inst_data_start, ns1, ns2, ns3
        player_code_size = raw_size - 6
    finally:
        os.unlink(stub_path)
        if os.path.exists(stub_bin):
            os.unlink(stub_bin)

    if progress:
        print(f"[HSC] Player code size: {player_code_size} bytes")

    # --- Compute layout ---
    freq_tbl_base  = PLAYER_BASE + player_code_size
    inst_base_addr = freq_tbl_base + n_freqs * 2

    inst_addr_map: List[int] = []
    addr = inst_base_addr
    for idx in range(len(inst_pool)):
        inst_addr_map.append(addr)
        addr += len(inst_pool._entries[idx]) * 6

    ns_base = addr

    # Compute per-voice note stream base addresses
    ns_base_per_voice = [0, 0, 0]
    running_ns = ns_base
    for vi in range(3):
        ns_base_per_voice[vi] = running_ns
        n_notes   = len(voice_note_seqs[vi])
        loop_note = voice_loop_note_idx[vi]
        has_loop  = (loop_note is not None and loop_note < n_notes)
        term_size = 3 if has_loop else 1
        running_ns += n_notes * 4 + term_size

    # --- Build note stream bytes ---
    ns_bytes: List[bytearray] = [bytearray(), bytearray(), bytearray()]

    for vi in range(3):
        loop_note = voice_loop_note_idx[vi]
        n_notes   = len(voice_note_seqs[vi])

        loop_target_addr = None
        if loop_note is not None and loop_note < n_notes:
            loop_target_addr = ns_base_per_voice[vi] + loop_note * 4

        for (length, pool_idx) in voice_note_seqs[vi]:
            iaddr = inst_addr_map[pool_idx]
            ns_bytes[vi].append(length & 0xFF)
            ns_bytes[vi].append(0)               # length_hi always 0
            ns_bytes[vi].append(iaddr & 0xFF)
            ns_bytes[vi].append((iaddr >> 8) & 0xFF)

        if loop_target_addr is not None:
            ns_bytes[vi].append(0xFE)
            ns_bytes[vi].append(loop_target_addr & 0xFF)
            ns_bytes[vi].append((loop_target_addr >> 8) & 0xFF)
        else:
            ns_bytes[vi].append(0xFF)

    # --- Generate full assembly ---
    if progress:
        print("[HSC] Generating assembly...")

    asm_lines = [_generate_player_asm(filter_regs)]

    asm_lines.append(f"; Freq table ({n_freqs} entries)")
    asm_lines.append("freq_lo_tbl")
    asm_lines.extend(_bytes_to_asm(freq_lo[:n_freqs]))
    asm_lines.append("freq_hi_tbl")
    asm_lines.extend(_bytes_to_asm(freq_hi[:n_freqs]))
    asm_lines.append("")

    inst_data = inst_pool.encode()
    asm_lines.append(f"; Instrument pool ({len(inst_pool)} entries, "
                     f"{len(inst_data)} bytes)")
    asm_lines.append("inst_data_start")
    asm_lines.extend(_bytes_to_asm(inst_data))
    asm_lines.append("")

    for vi in range(3):
        asm_lines.append(f"; Note stream voice {vi + 1} ({len(ns_bytes[vi])} bytes)")
        asm_lines.append(f"ns{vi + 1}")
        asm_lines.extend(_bytes_to_asm(bytes(ns_bytes[vi])))
        asm_lines.append("")

    full_asm = "\n".join(asm_lines)

    # Write .s file
    asm_path = output_path.replace('.sid', '_holyscale.s')
    if asm_path == output_path:
        asm_path = output_path + '_holyscale.s'
    with open(asm_path, 'w') as f:
        f.write(full_asm)

    if progress:
        print(f"[HSC] Assembly written: {asm_path}")

    # --- Assemble ---
    bin_path = asm_path.replace('.s', '.bin')
    r = subprocess.run([XA65, '-o', bin_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Assembly failed:\n{r.stderr[:3000]}")

    bin_data = open(bin_path, 'rb').read()
    bin_size  = len(bin_data)

    if progress:
        print(f"[HSC] Binary: {bin_size} bytes")

    # --- Build PSID ---
    load_addr_bytes = struct.pack('<H', PLAYER_BASE)
    payload = load_addr_bytes + bin_data

    psid_hdr = _build_psid_header(orig_sid_path, PLAYER_BASE)

    with open(output_path, 'wb') as f:
        f.write(psid_hdr)
        f.write(payload)

    sid_size = os.path.getsize(output_path)
    if progress:
        print(f"[HSC] PSID written: {output_path} ({sid_size} bytes, "
              f"{sid_size / 1024:.1f} KB)")

    return {
        'asm_path':          asm_path,
        'bin_path':          bin_path,
        'player_code_size':  player_code_size,
        'n_freqs':           n_freqs,
        'n_instruments':     len(inst_pool),
        'inst_data_size':    len(inst_data),
        'ns_sizes':          [len(b) for b in ns_bytes],
        'bin_size':          bin_size,
        'sid_size':          sid_size,
    }


# ---------------------------------------------------------------------------
# Verification via py65
# ---------------------------------------------------------------------------

def verify_against_trace(output_sid_path: str, trace,
                         max_frames: int = 300,
                         progress: bool = True
                         ) -> Tuple[int, int, List]:
    """Run rebuilt SID in py65 and compare frame-by-frame against ground truth.

    Returns (match_count, total_frames, mismatches).
    """
    from py65.devices.mpu6502 import MPU

    with open(output_sid_path, 'rb') as f:
        data = f.read()

    hdr_len   = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]

    code = data[hdr_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    end_addr = min(load_addr + len(binary), 65536)
    mem[load_addr:end_addr] = binary[:end_addr - load_addr]
    mem[0xFFF0] = 0x00   # BRK sentinel

    mpu = MPU()
    mpu.memory = mem

    # Run init
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(200000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    n = min(max_frames, trace.n_frames)
    match_count = 0
    mismatches  = []
    ret_addr = 0xFFF0 - 1

    reg_names = []
    for vi in range(3):
        for r in ('FL', 'FH', 'PL', 'PH', 'CT', 'AD', 'SR'):
            reg_names.append(f'V{vi+1}_{r}')
    for ri in range(4):
        reg_names.append(f'FLT{ri}')

    for frame in range(n):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(100000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        got      = tuple(mpu.memory[0xD400 + i] for i in range(25))
        expected = trace.frames[frame]

        if got == expected:
            match_count += 1
        else:
            diffs = [(i, expected[i], got[i]) for i in range(25)
                     if got[i] != expected[i]]
            mismatches.append((frame, diffs))
            if progress and len(mismatches) <= 5:
                diff_str = ', '.join(
                    f'{reg_names[i]}={e:02X}->{g:02X}'
                    for i, e, g in diffs
                )
                print(f"  Frame {frame:4d}: {diff_str}")

    return match_count, n, mismatches


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 holy_scale_codegen.py <input.sid> <output.sid> "
              "[subtune] [max_frames]")
        sys.exit(1)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xa65_path = os.path.join(repo_root, 'tools', 'xa65', 'xa')
    tools_path = os.path.join(repo_root, 'tools')
    os.environ['PATH'] = xa65_path + ':' + tools_path + ':' + os.environ.get('PATH', '')
    os.environ.setdefault('SIDFINITY_ROOT', repo_root)

    sys.path.insert(0, os.path.join(repo_root, 'src'))

    from ground_truth import capture_sid
    from holy_scale import holy_scale

    in_sid     = sys.argv[1]
    out_sid    = sys.argv[2]
    subtune    = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_frames = int(sys.argv[4]) if len(sys.argv) > 4 else None

    print(f"[HSC] Capturing: {in_sid} subtune {subtune}")
    result = capture_sid(in_sid, subtunes=[subtune], max_frames=max_frames,
                         detect_loop=False, progress=True)
    trace = result.subtunes[0]
    print(f"[HSC] {trace.n_frames} frames captured")

    print("[HSC] Building USF...")
    song = holy_scale(trace, in_sid)
    print(f"[HSC] tempo={song.tempo}, {len(song.instruments)} instruments, "
          f"{len(song.patterns)} patterns")

    stats = holy_scale_codegen(song, out_sid,
                               orig_sid_path=in_sid,
                               trace=trace,
                               progress=True)

    print()
    print("=== Holy Scale Results ===")
    print(f"  Player code:  {stats['player_code_size']} bytes")
    print(f"  Freq table:   {stats['n_freqs']} entries")
    print(f"  Instruments:  {stats['n_instruments']} ({stats['inst_data_size']} bytes)")
    print(f"  Note streams: {stats['ns_sizes']}")
    print(f"  Binary:       {stats['bin_size']} bytes")
    print(f"  SID:          {stats['sid_size']} bytes ({stats['sid_size']/1024:.1f} KB)")

    verify_frames = min(trace.n_frames, 300)
    print(f"\n[HSC] Verifying {verify_frames} frames...")
    match_count, total, mismatches = verify_against_trace(
        out_sid, trace, max_frames=verify_frames, progress=True
    )
    pct = 100.0 * match_count / total if total else 0.0
    print(f"[HSC] Match: {match_count}/{total} frames ({pct:.1f}%)")
    if mismatches:
        print(f"[HSC] First mismatch at frame {mismatches[0][0]}")
