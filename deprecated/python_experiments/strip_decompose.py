"""
strip_decompose.py -- Iterative stripping effect decomposer.

CONCEPT: Strip each SID effect from the register stream one at a time,
most-constrained first.  Each strip makes the residual simpler for the
next detector.  The final residual MUST be zero -- if not, an unmodeled
effect remains.

STRIPPING ORDER (most constrained first):
  1. ADSR  (AD/SR registers)         -- direct read, zero ambiguity
  2. Gate  (ctrl bit 0)              -- edge detection, zero ambiguity
  3. Waveform (ctrl bits 4-7 + 1-3)  -- pattern match, zero ambiguity
  4. PW modulation (pw_lo/pw_hi)     -- differencing, zero ambiguity
  5. Arpeggio (freq)                 -- discrete value detection
  6. Portamento (freq residual)      -- linear trend after arpeggio
  7. Vibrato (freq residual)         -- DFT after arpeggio+portamento
  8. Drum slide (freq_hi residual)   -- constant delta on hi byte

Steps 1-4 are in distinct registers so order-independent.
Steps 5-8 are all in freq but have orthogonal signatures.

Usage:
    from strip_decompose import strip_to_sid
    strip_to_sid(
        '/path/to/song.sid', '/tmp/stripped.sid',
        subtune=1, max_frames=1000, progress=True
    )

or from the command line:
    python3 src/strip_decompose.py song.sid /tmp/out.sid [subtune]

Key paths used:
    src/ground_truth.py   -- SubtuneTrace capture
    src/effect_detect.py  -- DFT, constant_delta, freq_to_note helpers
    tools/xa65/xa/xa      -- assembler
    tools/py65_lib        -- py65 emulator for verification
"""

import math
import os
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get('SIDFINITY_ROOT', os.path.join(SCRIPT_DIR, '..')).strip()
XA65 = os.path.join(REPO_ROOT, 'tools', 'xa65', 'xa', 'xa')

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))

# ---------------------------------------------------------------------------
# Register layout constants
# ---------------------------------------------------------------------------

# Per voice: freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr  (7 bytes each)
VOICE_OFFSETS = [0, 7, 14]  # register 0 for each voice in the 25-byte frame
FILTER_OFFSET = 21           # fc_lo, fc_hi, res_route, vol_mode

# SID memory map
SID_BASE       = 0xD400
VOICE_SID = [SID_BASE + 0, SID_BASE + 7, SID_BASE + 14]

# Zero-page layout (8 ZP bytes per voice)
# np_lo, np_hi = note stream pointer
# fc           = frame counter within note (0-based, 0..nl-1)
# nl           = note length in frames
# ip_lo, ip_hi = instrument data pointer (points to first frame byte)
# rp_lo, rp_hi = read pointer (advances 6 bytes per frame)
ZP_VOICE = [
    (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77),
    (0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F),
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87),
]
# ZP filter pointer
ZP_FP_LO = 0x90
ZP_FP_HI = 0x91

# Player load address -- $0400 to maximise available RAM (avoids ZP/stack at $00-$FF)
PLAYER_BASE = 0x0400


# ---------------------------------------------------------------------------
# Per-frame register container
# ---------------------------------------------------------------------------

@dataclass
class Frame:
    """Mutable copy of one frame's 7 voice registers + residual tracking."""
    freq_lo: int
    freq_hi: int
    pw_lo: int
    pw_hi: int
    ctrl: int
    ad: int
    sr: int

    def freq16(self) -> int:
        return (self.freq_hi << 8) | self.freq_lo

    def pw12(self) -> int:
        return ((self.pw_hi & 0x0F) << 8) | self.pw_lo

    def clone(self) -> 'Frame':
        return Frame(self.freq_lo, self.freq_hi, self.pw_lo,
                     self.pw_hi, self.ctrl, self.ad, self.sr)


def frames_from_trace(trace, voice: int, start: int, end: int) -> List[Frame]:
    """Extract raw register frames for a voice/note span."""
    voff = voice * 7
    result = []
    for i in range(start, min(end, trace.n_frames)):
        r = trace.frames[i]
        result.append(Frame(
            freq_lo=r[voff + 0],
            freq_hi=r[voff + 1],
            pw_lo  =r[voff + 2],
            pw_hi  =r[voff + 3],
            ctrl   =r[voff + 4],
            ad     =r[voff + 5],
            sr     =r[voff + 6],
        ))
    return result


# ---------------------------------------------------------------------------
# Strip 1: ADSR
# ---------------------------------------------------------------------------

def strip_adsr(frames: List[Frame]) -> Dict[str, Any]:
    """Read ADSR from the gate-on frame; zero it out in residual."""
    ad = frames[0].ad
    sr = frames[0].sr
    for f in frames:
        f.ad = 0
        f.sr = 0
    return {'ad': ad, 'sr': sr}


# ---------------------------------------------------------------------------
# Strip 2: Gate
# ---------------------------------------------------------------------------

def strip_gate(frames: List[Frame]) -> Dict[str, Any]:
    """Detect gate-off edge; clear gate bit from residual."""
    release_frame = None
    for i, f in enumerate(frames):
        if i > 0 and not (f.ctrl & 1):
            release_frame = i
            break
    for f in frames:
        f.ctrl &= 0xFE
    return {'release_frame': release_frame, 'total_frames': len(frames)}


# ---------------------------------------------------------------------------
# Strip 3: Waveform sequence
# ---------------------------------------------------------------------------

def strip_waveform(frames: List[Frame]) -> Dict[str, Any]:
    """Extract full ctrl byte sequence (gate already stripped); zero ctrl in residual."""
    # After gate strip, ctrl has bits 7-1 only (bit 0 cleared)
    wave_seq = [f.ctrl for f in frames]
    for f in frames:
        f.ctrl = 0
    return {'sequence': wave_seq}


# ---------------------------------------------------------------------------
# Strip 4: Pulse width modulation
# ---------------------------------------------------------------------------

def strip_pw(frames: List[Frame]) -> Dict[str, Any]:
    """Extract full PW sequence; zero pw in residual."""
    pw_seq = [(f.pw_hi & 0x0F, f.pw_lo) for f in frames]
    for f in frames:
        f.pw_lo = 0
        f.pw_hi = 0
    return {'sequence': pw_seq}


# ---------------------------------------------------------------------------
# Strip 5: Arpeggio (discrete freq values)
# ---------------------------------------------------------------------------

def strip_arpeggio(frames: List[Frame]) -> Optional[Dict[str, Any]]:
    """Detect and strip arpeggio from freq stream.

    Arpeggio: freq cycles through a small set of discrete values.
    Returns params dict if found, or None.  Modifies frames in place.
    """
    freqs = [f.freq16() for f in frames]
    unique = sorted(set(freqs))

    # Must have >=2 but <=6 unique values; more suggests vibrato/porta
    if len(unique) < 2 or len(unique) > 6:
        return None

    # Discreteness check: ratio of unique count to total must be low
    disc = len(unique) / len(freqs)
    if disc > 0.25:
        return None

    # All values must appear at least twice (not spurious)
    counts = Counter(freqs)
    if any(counts[v] < 2 for v in unique):
        return None

    # Detect the repeating pattern by finding the minimal period
    # Try period lengths 1..8
    best_period = None
    best_match = 0.0
    for period in range(1, min(9, len(freqs))):
        matches = sum(1 for i in range(len(freqs))
                      if freqs[i] == freqs[i % period])
        ratio = matches / len(freqs)
        if ratio > best_match:
            best_match = ratio
            best_period = period

    if best_match < 0.85 or best_period is None:
        return None

    # Extract the canonical pattern (first full period)
    pattern = freqs[:best_period]

    # Zero out freq residual
    for i, f in enumerate(frames):
        expected = pattern[i % best_period]
        actual = f.freq16()
        diff = actual - expected
        f.freq_lo = diff & 0xFF
        f.freq_hi = (diff >> 8) & 0xFF

    return {
        'pattern': pattern,
        'period': best_period,
        'unique_values': unique,
        'match_ratio': best_match,
    }


# ---------------------------------------------------------------------------
# Strip 6: Portamento (linear freq trend)
# ---------------------------------------------------------------------------

def strip_portamento(frames: List[Frame]) -> Optional[Dict[str, Any]]:
    """Detect and strip a linear freq slide from residual.

    After arpeggio strip, if any residual remains, check for a constant
    per-frame delta in freq.
    """
    freqs = [f.freq16() for f in frames]
    if all(v == 0 for v in freqs):
        return None

    deltas = [freqs[i + 1] - freqs[i] for i in range(len(freqs) - 1)]
    if not deltas:
        return None

    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return None

    counter = Counter(non_zero)
    best_delta, best_count = counter.most_common(1)[0]
    consistency = best_count / len(non_zero)

    if consistency < 0.7 or len(non_zero) < 3:
        return None

    # Subtract linear trend
    acc = 0
    for f in frames:
        actual = f.freq16()
        residual = actual - acc
        f.freq_lo = residual & 0xFF
        f.freq_hi = (residual >> 8) & 0xFF
        acc += best_delta

    return {
        'delta_per_frame': best_delta,
        'start_freq': freqs[0],
        'consistency': consistency,
    }


# ---------------------------------------------------------------------------
# Strip 7: Vibrato (sinusoidal freq residual)
# ---------------------------------------------------------------------------

def _real_dft_peak(signal: List[float], sample_rate: float = 50.0,
                   min_hz: float = 2.0, max_hz: float = 15.0
                   ) -> Tuple[float, float, float]:
    """Return (peak_hz, peak_mag, total_energy)."""
    N = len(signal)
    if N < 8:
        return 0.0, 0.0, 0.0
    mean = sum(signal) / N
    x = [s - mean for s in signal]
    best_f, best_m, total = 0.0, 0.0, 0.0
    for k in range(1, N // 2 + 1):
        re = im = 0.0
        w = 2.0 * math.pi * k / N
        for n in range(N):
            re += x[n] * math.cos(w * n)
            im += x[n] * math.sin(w * n)
        mag = math.sqrt(re * re + im * im) / N
        freq_hz = k * sample_rate / N
        total += mag
        if min_hz <= freq_hz <= max_hz and mag > best_m:
            best_m = mag
            best_f = freq_hz
    return best_f, best_m, total


def strip_vibrato(frames: List[Frame]) -> Optional[Dict[str, Any]]:
    """Detect and strip sinusoidal freq modulation."""
    freqs = [f.freq16() for f in frames]
    if all(v == 0 for v in freqs):
        return None
    if len(set(freqs)) < 4:
        return None

    peak_hz, peak_mag, total = _real_dft_peak([float(v) for v in freqs])
    if total == 0 or peak_mag / total < 0.25:
        return None

    # Estimate amplitude and phase via the dominant frequency
    N = len(freqs)
    mean_freq = sum(freqs) / N
    w = 2.0 * math.pi * peak_hz / 50.0
    re = im = 0.0
    for n, v in enumerate(freqs):
        re += (v - mean_freq) * math.cos(w * n)
        im += (v - mean_freq) * math.sin(w * n)
    amp = 2.0 * math.sqrt(re * re + im * im) / N
    phase = math.atan2(-im, re)

    # Subtract modeled sinusoid from residual
    for i, f in enumerate(frames):
        modeled = int(round(mean_freq + amp * math.cos(w * i + phase)))
        actual = f.freq16()
        diff = actual - modeled
        f.freq_lo = diff & 0xFF
        f.freq_hi = (diff >> 8) & 0xFF

    return {
        'rate_hz': round(peak_hz, 2),
        'depth': round(amp, 1),
        'mean_freq': int(round(mean_freq)),
        'purity': round(peak_mag / total, 3),
    }


# ---------------------------------------------------------------------------
# Strip 8: Drum slide (constant delta on freq_hi only)
# ---------------------------------------------------------------------------

def strip_drum_slide(frames: List[Frame]) -> Optional[Dict[str, Any]]:
    """Detect and strip a constant per-frame freq_hi delta."""
    fhi = [f.freq_hi for f in frames]
    if all(v == 0 for v in fhi):
        return None

    deltas = [fhi[i + 1] - fhi[i] for i in range(len(fhi) - 1)]
    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return None

    counter = Counter(non_zero)
    best_delta, best_count = counter.most_common(1)[0]
    consistency = best_count / len(non_zero)
    if consistency < 0.6 or abs(best_delta) > 4:
        return None

    # Subtract linear trend on freq_hi
    acc_hi = fhi[0]
    for i, f in enumerate(frames):
        f.freq_hi = (f.freq_hi - acc_hi) & 0xFF
        if i < len(frames) - 1:
            acc_hi += best_delta

    return {
        'delta': best_delta,
        'start_freq_hi': fhi[0],
        'consistency': consistency,
    }


# ---------------------------------------------------------------------------
# Main decomposer
# ---------------------------------------------------------------------------

def strip_decompose(trace, voice: int, start_frame: int, end_frame: int
                    ) -> Tuple[Dict[str, Any], List[Frame], List[Frame]]:
    """Decompose one note's registers into effect parameters via iterative stripping.

    Returns:
        params:   dict of {effect_name: {parameters}}
        residual: per-frame Frame objects after all effects stripped (should be zero)
        original: unmodified copy of the frames for reconstruction checking
    """
    frames = frames_from_trace(trace, voice, start_frame, end_frame)
    original = [f.clone() for f in frames]

    if not frames:
        return {}, [], []

    params = {}

    # Strip 1: ADSR (independent register)
    params['adsr'] = strip_adsr(frames)

    # Strip 2: Gate (bit 0 of ctrl)
    params['gate'] = strip_gate(frames)

    # Strip 3: Waveform (remaining ctrl bits)
    params['waveform'] = strip_waveform(frames)

    # Strip 4: Pulse width (independent registers)
    params['pw'] = strip_pw(frames)

    # Strips 5-8: All operate on freq register residual
    # Try arpeggio first (most constrained -- discrete values)
    arp = strip_arpeggio(frames)
    if arp is not None:
        params['arpeggio'] = arp
    else:
        # Try portamento (linear trend)
        porta = strip_portamento(frames)
        if porta is not None:
            params['portamento'] = porta
        else:
            # Try vibrato (sinusoidal)
            vib = strip_vibrato(frames)
            if vib is not None:
                params['vibrato'] = vib

    # Drum slide on hi byte of whatever remains
    ds = strip_drum_slide(frames)
    if ds is not None:
        params['drum_slide'] = ds

    # Compute residual energy (sum of all remaining non-zero bytes)
    total_residual = sum(
        abs(f.freq_lo) + abs(f.freq_hi) + abs(f.pw_lo) + abs(f.pw_hi) +
        abs(f.ctrl) + abs(f.ad) + abs(f.sr)
        for f in frames
    )
    params['residual_energy'] = total_residual

    return params, frames, original


# ---------------------------------------------------------------------------
# Frequency table builder
# ---------------------------------------------------------------------------

class FreqTable:
    """Maps 16-bit freq value -> compact index, shared across all voices."""

    def __init__(self):
        self._vals: List[int] = []
        self._index: Dict[int, int] = {}

    def add(self, freq16: int) -> int:
        if freq16 not in self._index:
            self._index[freq16] = len(self._vals)
            self._vals.append(freq16)
        return self._index[freq16]

    def get(self, freq16: int) -> int:
        return self._index.get(freq16, 0)

    def lo_table(self) -> bytes:
        return bytes(v & 0xFF for v in self._vals)

    def hi_table(self) -> bytes:
        return bytes((v >> 8) & 0xFF for v in self._vals)

    def __len__(self) -> int:
        return len(self._vals)


# ---------------------------------------------------------------------------
# Player assembly generator
# ---------------------------------------------------------------------------

def _bytes_to_asm(data: bytes, indent: str = "        ") -> List[str]:
    """Convert bytes to xa65 .byte directives, 16 per line."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append(indent + ".byte " + ",".join(f"${b:02X}" for b in chunk))
    return lines


def generate_player_asm(freq_table: FreqTable,
                        voice_streams: List[bytes],
                        filter_frame: Tuple[int, int, int, int],
                        n_frames: int) -> str:
    """Generate xa65 assembly for the strip-decompose player.

    Player format per note stream entry (4 bytes):
        [length_lo, length_hi, data_lo, data_hi]
    where data_ptr points to the instrument block.

    Special note stream opcodes:
        length_lo=$FF -- end of stream (silence)
        length_lo=$FE -- loop-back: next 2 bytes are new np (lo, hi)

    Instrument block per note (6 bytes per frame):
        [freq_idx, ctrl, pw_lo, pw_hi, ad, sr]
    where freq_idx indexes into freq_lo_tbl / freq_hi_tbl.

    Filter: constant (4 bytes) -- fc_lo, fc_hi, res_route, vol_mode.

    ZP layout per voice (8 bytes):
        np_lo np_hi  -- note stream read pointer
        fc           -- frame counter (0..nl-1)
        nl           -- note length (frames)
        ip_lo ip_hi  -- instrument base pointer
        rp_lo rp_hi  -- read pointer (advances 6/frame)

    Memory map:
        $1000         init (3-byte JMP)
        $1003         play (main entry)
        ...           player code
        freq_lo_tbl   N bytes
        freq_hi_tbl   N bytes
        inst_data     instrument blocks
        ns1,ns2,ns3   note streams (4 bytes per note + terminator)
    """

    fc_lo = filter_frame[0]
    fc_hi = filter_frame[1]
    res   = filter_frame[2]
    vol   = filter_frame[3]

    # Note: xa65 with -XMASM syntax. No colons inside comments.
    asm = []

    # Org directive
    asm.append(f"; Strip-decompose player -- load at ${PLAYER_BASE:04X}")
    asm.append(f"* = ${PLAYER_BASE:04X}")
    asm.append("")

    # --- init ($1000) ---
    asm.append("; init -- called once with A=subtune-1")
    asm.append("init")
    asm.append("        jmp _init_body")
    asm.append("")

    # --- play ($1003) ---
    asm.append("; play -- called once per frame")
    asm.append("play")
    asm.append("        jmp _play_body")
    asm.append("")

    # --- init body ---
    asm.append("_init_body")
    # Set up note stream pointers and init frame counters
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        ns_label = f"ns{vi + 1}"
        asm.append(f"        lda #<{ns_label}")
        asm.append(f"        sta ${np_lo:02X}")
        asm.append(f"        lda #>{ns_label}")
        asm.append(f"        sta ${np_hi:02X}")
        # fc = 255 so the first play call immediately loads the first note
        asm.append(f"        lda #$FF")
        asm.append(f"        sta ${fc:02X}")
        asm.append(f"        lda #$00")
        asm.append(f"        sta ${nl:02X}")

    # Write constant filter registers
    asm.append(f"        lda #${fc_lo:02X}")
    asm.append(f"        sta $D415")
    asm.append(f"        lda #${fc_hi:02X}")
    asm.append(f"        sta $D416")
    asm.append(f"        lda #${res:02X}")
    asm.append(f"        sta $D417")
    asm.append(f"        lda #${vol:02X}")
    asm.append(f"        sta $D418")
    asm.append("        rts")
    asm.append("")

    # --- play body ---
    asm.append("_play_body")

    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        vsid = VOICE_SID[vi]
        vlabel = f"v{vi + 1}"

        asm.append(f"; Voice {vi + 1}")
        asm.append(f"{vlabel}_tick")

        # Increment frame counter; check against note length
        asm.append(f"        inc ${fc:02X}")
        asm.append(f"        lda ${fc:02X}")
        asm.append(f"        cmp ${nl:02X}")
        asm.append(f"        bcc {vlabel}_play_frame")

        # Note expired -- load next note from stream
        asm.append(f"{vlabel}_next_note")
        # Read length_lo from stream
        asm.append(f"        ldy #$00")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        cmp #$FF")
        asm.append(f"        beq {vlabel}_done")   # $FF = end of stream (silence)
        asm.append(f"        cmp #$FE")
        asm.append(f"        bne {vlabel}_normal_note")   # $FE = loop-back

        # $FE: load new note-stream pointer from next 2 bytes, then re-read
        asm.append(f"        iny")
        asm.append(f"        lda (${np_lo:02X}),y")   # new np_lo
        asm.append(f"        tax")
        asm.append(f"        iny")
        asm.append(f"        lda (${np_lo:02X}),y")   # new np_hi
        asm.append(f"        sta ${np_hi:02X}")
        asm.append(f"        stx ${np_lo:02X}")
        asm.append(f"        jmp {vlabel}_next_note")
        asm.append(f"{vlabel}_normal_note")

        # length_lo in A, save to nl (using 16-bit length split across 2 bytes)
        asm.append(f"        sta ${nl:02X}")
        # length_hi (we limit notes to 255 frames, so hi is always 0; but we read
        # it anyway to keep the stream pointer advancing by 4 bytes per note)
        asm.append(f"        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        # (discard length_hi -- all notes <= 255 frames in this player)

        # data_lo
        asm.append(f"        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        sta ${ip_lo:02X}")
        asm.append(f"        sta ${rp_lo:02X}")
        # data_hi
        asm.append(f"        iny")
        asm.append(f"        lda (${np_lo:02X}),y")
        asm.append(f"        sta ${ip_hi:02X}")
        asm.append(f"        sta ${rp_hi:02X}")

        # Advance note stream pointer by 4
        asm.append(f"        lda ${np_lo:02X}")
        asm.append(f"        clc")
        asm.append(f"        adc #$04")
        asm.append(f"        sta ${np_lo:02X}")
        asm.append(f"        bcc {vlabel}_np_ok")
        asm.append(f"        inc ${np_hi:02X}")
        asm.append(f"{vlabel}_np_ok")

        # Reset frame counter to 0
        asm.append(f"        lda #$00")
        asm.append(f"        sta ${fc:02X}")

        # Play current frame from instrument data
        asm.append(f"{vlabel}_play_frame")

        # Each instrument frame: [freq_idx, ctrl, pw_lo, pw_hi, ad, sr]
        # Use rp pointer (indirect indexed)
        asm.append(f"        ldy #$00")

        # freq_idx -> freq lookup -> write D400/D401
        asm.append(f"        lda (${rp_lo:02X}),y")       # freq_idx
        asm.append(f"        tax")
        asm.append(f"        lda freq_lo_tbl,x")
        asm.append(f"        sta ${vsid:04X}")
        asm.append(f"        lda freq_hi_tbl,x")
        asm.append(f"        sta ${vsid + 1:04X}")

        # ctrl
        asm.append(f"        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 4:04X}")

        # pw_lo
        asm.append(f"        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 2:04X}")

        # pw_hi
        asm.append(f"        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 3:04X}")

        # ad
        asm.append(f"        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 5:04X}")

        # sr
        asm.append(f"        iny")
        asm.append(f"        lda (${rp_lo:02X}),y")
        asm.append(f"        sta ${vsid + 6:04X}")

        # Advance read pointer by 6
        asm.append(f"        lda ${rp_lo:02X}")
        asm.append(f"        clc")
        asm.append(f"        adc #$06")
        asm.append(f"        sta ${rp_lo:02X}")
        asm.append(f"        bcc {vlabel}_done")
        asm.append(f"        inc ${rp_hi:02X}")
        asm.append(f"{vlabel}_done")
        asm.append("")

    asm.append("        rts")
    asm.append("")

    return "\n".join(asm)


# ---------------------------------------------------------------------------
# Instrument data encoder
# ---------------------------------------------------------------------------

class InstrumentPool:
    """Deduplicated pool of per-frame instrument data (6 bytes per frame).

    Each entry: (freq_idx, ctrl, pw_lo, pw_hi, ad, sr) per frame.
    Exact-match deduplication across all voices.
    """

    def __init__(self):
        self._entries: List[Tuple] = []
        self._index: Dict[Tuple, int] = {}

    def add(self, frames: List[Tuple[int, int, int, int, int, int]]) -> int:
        key = tuple(frames)
        if key in self._index:
            return self._index[key]
        idx = len(self._entries)
        self._entries.append(key)
        self._index[key] = idx
        return idx

    def encode(self) -> bytes:
        """Encode all instruments as flat byte stream."""
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

    def offset_of(self, idx: int, inst_base_addr: int) -> int:
        """Return the byte address of instrument[idx] within inst_base_addr."""
        addr = inst_base_addr
        for i in range(idx):
            addr += len(self._entries[i]) * 6
        return addr

    def __len__(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Full pipeline: trace -> asm -> SID
# ---------------------------------------------------------------------------

def strip_to_sid(sid_path: str, output_path: str,
                 subtune: int = 1,
                 max_frames: Optional[int] = None,
                 progress: bool = True,
                 detect_loop: bool = True) -> Dict[str, Any]:
    """Decompose a SID subtune via iterative stripping and produce a
    register-perfect, compact rebuilt SID.

    Args:
        sid_path:    original SID file path
        output_path: output .sid path
        subtune:     1-indexed subtune number
        max_frames:  override max frames (default: HVSC duration + 10%)
        progress:    print progress messages
        detect_loop: stop early when a loop is detected (default True).
                     Set False to capture the full max_frames duration.

    Returns:
        stats dict with size, match rate, and decomposition summary.
    """
    from ground_truth import capture_sid

    if progress:
        print(f"[SD] Strip-decompose: {sid_path} subtune {subtune}")

    # Step 1: Capture ground truth
    if progress:
        print("[SD] Capturing ground truth...")
    sid_trace = capture_sid(sid_path, subtunes=[subtune],
                            max_frames=max_frames,
                            detect_loop=detect_loop, progress=progress)
    if not sid_trace.subtunes:
        raise RuntimeError(f"No subtune {subtune} captured")
    trace = sid_trace.subtunes[0]
    if progress:
        print(f"[SD] {trace.n_frames} frames captured")

    # Step 2: Decompose all voices
    freq_table = FreqTable()
    inst_pool = InstrumentPool()

    # Add freq=0 as entry 0 (silence / gate-off frames)
    freq_table.add(0)

    decomp_stats = {v: {'notes': 0, 'effects': Counter()} for v in range(3)}

    # Note streams: list of (length, data_addr_placeholder) per voice
    # We'll fill data_addr after computing inst_pool layout
    # Each entry: (length, inst_idx)
    voice_note_seqs: List[List[Tuple[int, int]]] = [[], [], []]  # (length, inst_idx)
    # For loop support: note index in each voice's stream where loop_frame falls
    # (the note whose seg_start <= loop_frame, or the first note with seg_start == loop_frame)
    voice_loop_note_idx: List[Optional[int]] = [None, None, None]

    loop_frame = trace.loop_frame  # may be None (no loop)

    for voice in range(3):
        segs = trace.gate_segments(voice)
        if progress:
            print(f"[SD] Voice {voice + 1}: {len(segs)} notes")
        for seg_start, seg_end in segs:
            seg_end = min(seg_end, trace.n_frames)
            length = seg_end - seg_start
            if length == 0:
                continue

            note_idx = len(voice_note_seqs[voice])

            # Mark loop target: the note whose segment starts at or contains loop_frame
            if loop_frame is not None and voice_loop_note_idx[voice] is None:
                if seg_start >= loop_frame:
                    # This note starts at or after loop_frame -- use it as loop target
                    voice_loop_note_idx[voice] = note_idx
                elif seg_start < loop_frame < seg_end:
                    # loop_frame falls within this note; use the note as loop target
                    # (slight imprecision: we loop back a few frames early, but avoids splitting)
                    voice_loop_note_idx[voice] = note_idx

            # Decompose this note
            params, residual, original = strip_decompose(trace, voice, seg_start, seg_end)

            # Track effect stats
            decomp_stats[voice]['notes'] += 1
            for k in params:
                if k != 'residual_energy':
                    decomp_stats[voice]['effects'][k] += 1

            # Build instrument frames from original (not residual -- we store raw)
            # Each frame: (freq_idx, ctrl, pw_lo, pw_hi, ad, sr)
            inst_frames = []
            for f in original:
                fq = freq_table.add(f.freq16())
                inst_frames.append((fq, f.ctrl, f.pw_lo, f.pw_hi & 0x0F, f.ad, f.sr))

            # Clamp to 255 frames per note (player limit)
            n = min(len(inst_frames), 255)
            inst_frames = inst_frames[:n]

            inst_idx = inst_pool.add(inst_frames)
            voice_note_seqs[voice].append((n, inst_idx))

    if progress:
        print(f"[SD] Freq table: {len(freq_table)} unique frequencies")
        print(f"[SD] Instrument pool: {len(inst_pool)} unique instruments")
        if loop_frame is not None:
            for vi in range(3):
                lni = voice_loop_note_idx[vi]
                print(f"[SD] Voice {vi+1} loop note idx: {lni} "
                      f"(frame {loop_frame}, total notes {len(voice_note_seqs[vi])})")

    # Step 3: Compute layout
    # We need to know where inst_data and note streams go.
    # Layout:
    #   PLAYER_BASE + player_code_size: freq_lo_tbl, freq_hi_tbl
    #   + 2*N_freqs:                    inst_data (flat)
    #   + inst_data_size:               ns1, ns2, ns3

    # Generate player asm skeleton (without data labels) to measure code size
    filter_frame = tuple(trace.frames[0][FILTER_OFFSET:FILTER_OFFSET + 4])

    # Build note stream bytes (4 bytes per note: len_lo, len_hi, data_lo, data_hi)
    # We need inst_base_addr to compute data pointers.
    # We'll use a 2-pass approach: first measure player code size, then assemble.

    freq_lo_bytes = freq_table.lo_table()
    freq_hi_bytes = freq_table.hi_table()
    n_freqs = len(freq_table)

    inst_data = inst_pool.encode()

    # Measure player code size by assembling a stub
    player_asm_skeleton = generate_player_asm(
        freq_table,
        [b'', b'', b''],
        filter_frame,
        trace.n_frames,
    )
    # Add stub data labels at address 0 to measure code size
    stub = player_asm_skeleton
    stub += "\nfreq_lo_tbl\n        .byte $00\nfreq_hi_tbl\n        .byte $00\n"
    stub += "inst_data_start\n        .byte $00\n"
    stub += "ns1\n        .byte $FF\nns2\n        .byte $FF\nns3\n        .byte $FF\n"
    # Stub uses $FF terminators (1 byte each = 6 stub bytes total: freq_lo, freq_hi,
    # inst_data_start, ns1, ns2, ns3 -- each 1 byte)

    with tempfile.NamedTemporaryFile(suffix='.s', mode='w', delete=False) as tf:
        tf.write(stub)
        stub_path = tf.name
    stub_bin = stub_path.replace('.s', '.bin')
    try:
        r = subprocess.run([XA65, '-o', stub_bin, stub_path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Stub assembly failed:\n{r.stderr[:2000]}")
        # The player code ends before freq_lo_tbl
        # We need to read the binary and find where actual player bytes end
        player_code_size = os.path.getsize(stub_bin) - 1 - 1 - 1 - 1 - 1 - 1 - 1
        # This is imprecise; use a simpler approach: assemble stub, binary size minus stubs
        # Actually just use the full binary size -- it's minimal (1 byte per stub label)
        # Better: compute from labels. Use symbols.
        # Simplest: after assembly, player code is from PLAYER_BASE to PLAYER_BASE + code_size
        # Use binary file size minus 7 stub bytes:
        raw_size = os.path.getsize(stub_bin)
        # stubs added: freq_lo $00, freq_hi $00, inst $00, ns1 $FF, ns2 $FF, ns3 $FF = 6 bytes
        player_code_size = raw_size - 6
    finally:
        os.unlink(stub_path)
        if os.path.exists(stub_bin):
            os.unlink(stub_bin)

    if progress:
        print(f"[SD] Player code size: {player_code_size} bytes")

    # Compute addresses
    freq_tbl_base   = PLAYER_BASE + player_code_size
    inst_base_addr  = freq_tbl_base + n_freqs * 2   # lo + hi tables

    # Compute per-instrument addresses
    inst_addr_map: List[int] = []
    addr = inst_base_addr
    for idx in range(len(inst_pool)):
        inst_addr_map.append(addr)
        n_frames_in_inst = len(inst_pool._entries[idx])
        addr += n_frames_in_inst * 6

    ns_base = addr  # note streams start here

    # Build note stream bytes; compute where each voice stream starts
    # (needed to resolve loop-back addresses)
    ns_base_per_voice = [0, 0, 0]
    running_ns_base = ns_base
    for vi in range(3):
        ns_base_per_voice[vi] = running_ns_base
        n_notes = len(voice_note_seqs[vi])
        has_loop = (voice_loop_note_idx[vi] is not None and
                    voice_loop_note_idx[vi] < n_notes)
        term_size = 3 if has_loop else 1  # $FE lo hi or $FF
        running_ns_base += n_notes * 4 + term_size

    ns_bytes: List[bytearray] = [bytearray(), bytearray(), bytearray()]
    for vi in range(3):
        loop_note = voice_loop_note_idx[vi]
        loop_target_addr = None
        if loop_note is not None and loop_note < len(voice_note_seqs[vi]):
            # Address of the loop-target note = ns_base_per_voice[vi] + loop_note * 4
            loop_target_addr = ns_base_per_voice[vi] + loop_note * 4

        for note_i, (length, inst_idx) in enumerate(voice_note_seqs[vi]):
            iaddr = inst_addr_map[inst_idx]
            ns_bytes[vi].append(length & 0xFF)
            ns_bytes[vi].append(0)              # length_hi always 0 (<= 255 frames)
            ns_bytes[vi].append(iaddr & 0xFF)
            ns_bytes[vi].append((iaddr >> 8) & 0xFF)

        if loop_target_addr is not None:
            # $FE lo hi -- jump back to loop start
            ns_bytes[vi].append(0xFE)
            ns_bytes[vi].append(loop_target_addr & 0xFF)
            ns_bytes[vi].append((loop_target_addr >> 8) & 0xFF)
        else:
            ns_bytes[vi].append(0xFF)  # end-of-stream terminator

    # Step 4: Generate full assembly
    if progress:
        print("[SD] Generating assembly...")

    asm_lines = [generate_player_asm(freq_table, [bytes(b) for b in ns_bytes],
                                     filter_frame, trace.n_frames)]

    # Append data tables
    asm_lines.append(f"; Freq table ({n_freqs} entries)")
    asm_lines.append("freq_lo_tbl")
    asm_lines.extend(_bytes_to_asm(freq_lo_bytes))
    asm_lines.append("freq_hi_tbl")
    asm_lines.extend(_bytes_to_asm(freq_hi_bytes))
    asm_lines.append("")

    asm_lines.append(f"; Instrument pool ({len(inst_pool)} entries, {len(inst_data)} bytes)")
    asm_lines.append("inst_data_start")
    asm_lines.extend(_bytes_to_asm(inst_data))
    asm_lines.append("")

    for vi in range(3):
        asm_lines.append(f"; Note stream voice {vi + 1} ({len(ns_bytes[vi])} bytes)")
        asm_lines.append(f"ns{vi + 1}")
        asm_lines.extend(_bytes_to_asm(bytes(ns_bytes[vi])))
        asm_lines.append("")

    full_asm = "\n".join(asm_lines)

    # Step 5: Assemble
    asm_path = output_path.replace('.sid', '_strip.s')
    with open(asm_path, 'w') as f:
        f.write(full_asm)
    if progress:
        print(f"[SD] Assembly written to {asm_path}")

    bin_path = output_path.replace('.sid', '_strip.bin')
    r = subprocess.run([XA65, '-o', bin_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Assembly failed:\n{r.stderr[:3000]}")

    bin_data = open(bin_path, 'rb').read()
    bin_size = len(bin_data)
    if progress:
        print(f"[SD] Binary: {bin_size} bytes")

    # Step 6: Build PSID file
    load_addr_bytes = struct.pack('<H', PLAYER_BASE)
    payload = load_addr_bytes + bin_data

    psid_hdr = _build_psid_header(sid_path, PLAYER_BASE)
    with open(output_path, 'wb') as f:
        f.write(psid_hdr)
        f.write(payload)

    sid_size = os.path.getsize(output_path)
    if progress:
        print(f"[SD] PSID written: {output_path} ({sid_size} bytes)")

    # Step 7: Verify via py65
    if progress:
        print("[SD] Verifying against ground truth...")
    match_count, total_frames, mismatches = _verify(output_path, trace,
                                                     max_frames=min(trace.n_frames, 500),
                                                     progress=progress)
    match_pct = 100.0 * match_count / total_frames if total_frames else 0.0
    if progress:
        print(f"[SD] Match: {match_count}/{total_frames} frames ({match_pct:.1f}%)")
        if mismatches:
            print(f"[SD] First mismatch at frame {mismatches[0][0]}")
            frame_i, diffs = mismatches[0]
            reg_names = _reg_names()
            for ri, exp, got in diffs[:6]:
                print(f"      reg[{ri}] {reg_names[ri]}: expected ${exp:02X} got ${got:02X}")

    # Decomp summary
    total_notes = sum(s['notes'] for s in decomp_stats.values())
    all_effects: Counter = Counter()
    for s in decomp_stats.values():
        all_effects.update(s['effects'])

    stats = {
        'n_frames': trace.n_frames,
        'loop_frame': loop_frame,
        'loop_length': trace.loop_length,
        'n_freqs': n_freqs,
        'n_instruments': len(inst_pool),
        'total_notes': total_notes,
        'player_code_size': player_code_size,
        'freq_tbl_size': n_freqs * 2,
        'inst_data_size': len(inst_data),
        'ns_sizes': [len(b) for b in ns_bytes],
        'bin_size': bin_size,
        'sid_size': sid_size,
        'match_count': match_count,
        'total_frames': total_frames,
        'match_pct': match_pct,
        'effects_detected': dict(all_effects),
        'asm_path': asm_path,
        'bin_path': bin_path,
    }
    return stats


# ---------------------------------------------------------------------------
# PSID header builder
# ---------------------------------------------------------------------------

def _build_psid_header(orig_sid_path: str, load_addr: int) -> bytes:
    """Build a PSID v2 header copying metadata from original SID."""
    with open(orig_sid_path, 'rb') as f:
        orig = f.read()

    orig_header_len = struct.unpack('>H', orig[6:8])[0]
    title      = orig[22:54].rstrip(b'\x00')
    author     = orig[54:86].rstrip(b'\x00')
    copyright_ = orig[86:118].rstrip(b'\x00')
    flags      = struct.unpack('>H', orig[118:120])[0] if orig_header_len >= 120 else 0x0014

    init_addr = PLAYER_BASE          # $1000
    play_addr = PLAYER_BASE + 3      # $1003 (after 3-byte JMP)

    hdr = bytearray(124)
    hdr[0:4]   = b'PSID'
    struct.pack_into('>H', hdr, 4,  2)           # version 2
    struct.pack_into('>H', hdr, 6,  124)         # header length
    struct.pack_into('>H', hdr, 8,  0)           # load_addr=0 (in binary)
    struct.pack_into('>H', hdr, 10, init_addr)
    struct.pack_into('>H', hdr, 12, play_addr)
    struct.pack_into('>H', hdr, 14, 1)           # 1 song
    struct.pack_into('>H', hdr, 16, 1)           # start song = 1
    struct.pack_into('>I', hdr, 18, 0)           # speed flags
    hdr[22:54]  = (title     + b'\x00' * 32)[:32]
    hdr[54:86]  = (author    + b'\x00' * 32)[:32]
    hdr[86:118] = (copyright_ + b'\x00' * 32)[:32]
    struct.pack_into('>H', hdr, 118, flags)

    return bytes(hdr)


# ---------------------------------------------------------------------------
# Verification via py65
# ---------------------------------------------------------------------------

def _reg_names() -> List[str]:
    names = []
    for vi in range(3):
        for r in ('FL', 'FH', 'PL', 'PH', 'CT', 'AD', 'SR'):
            names.append(f'V{vi + 1}_{r}')
    for ri in range(4):
        names.append(f'FLT{ri}')
    return names


def _verify(output_sid_path: str, trace,
            max_frames: int = 300,
            progress: bool = False
            ) -> Tuple[int, int, List]:
    """Run rebuilt SID in py65 and compare against trace frame-by-frame."""
    from py65.devices.mpu6502 import MPU

    with open(output_sid_path, 'rb') as f:
        data = f.read()

    hdr_len    = struct.unpack('>H', data[6:8])[0]
    load_addr  = struct.unpack('>H', data[8:10])[0]
    init_addr  = struct.unpack('>H', data[10:12])[0]
    play_addr  = struct.unpack('>H', data[12:14])[0]

    code = data[hdr_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    end_addr = min(load_addr + len(binary), 65536)
    mem[load_addr:end_addr] = binary[:end_addr - load_addr]
    mem[0xFFF0] = 0x00  # BRK sentinel

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
    mismatches = []
    ret_addr = 0xFFF0 - 1
    reg_names = _reg_names()

    for frame in range(n):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(100000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        got = tuple(mpu.memory[0xD400 + i] for i in range(25))
        expected = trace.frames[frame]

        if got == expected:
            match_count += 1
        else:
            diffs = [(i, expected[i], got[i]) for i in range(25) if got[i] != expected[i]]
            mismatches.append((frame, diffs))
            if progress and len(mismatches) <= 3:
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
        print("Usage: python3 strip_decompose.py <input.sid> <output.sid> [subtune] [max_frames]")
        sys.exit(1)

    in_sid = sys.argv[1]
    out_sid = sys.argv[2]
    sub = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    mf = int(sys.argv[4]) if len(sys.argv) > 4 else None

    stats = strip_to_sid(in_sid, out_sid, subtune=sub, max_frames=mf, progress=True)

    print()
    print("=== Strip-Decompose Results ===")
    print(f"  Frames captured:   {stats['n_frames']}")
    print(f"  Freq table:        {stats['n_freqs']} entries ({stats['freq_tbl_size']} bytes)")
    print(f"  Instruments:       {stats['n_instruments']} unique ({stats['inst_data_size']} bytes)")
    print(f"  Notes:             {stats['total_notes']} total")
    print(f"  Player code:       {stats['player_code_size']} bytes")
    ns_total = sum(stats['ns_sizes'])
    print(f"  Note streams:      {ns_total} bytes ({stats['ns_sizes']})")
    print(f"  Binary total:      {stats['bin_size']} bytes")
    print(f"  PSID file:         {stats['sid_size']} bytes")
    print(f"  Register match:    {stats['match_count']}/{stats['total_frames']} "
          f"({stats['match_pct']:.1f}%)")
    print(f"  Effects detected:  {stats['effects_detected']}")
    if stats['match_pct'] == 100.0:
        print("  PERFECT MATCH")
    else:
        print(f"  Assembly: {stats['asm_path']}")
