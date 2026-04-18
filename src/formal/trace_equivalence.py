"""
trace_equivalence.py -- Formal specification of the SID register trace equivalence relation.

This module provides a mathematical framework for comparing original and rebuilt
SID file register traces. It formalizes the 8-layer jitter tolerance heuristics
from sid_compare.py into a composable set of equivalence rules with explicit
classification semantics.

Definitions
-----------
A RegisterFrame is a vector of 25 8-bit values representing the SID chip state
($D400-$D418) at one video frame boundary.

A RegisterTrace is a finite sequence of RegisterFrames: T = (f_0, f_1, ..., f_{n-1}).

Two traces T_orig and T_rebuilt are considered equivalent under grading function G
if G(classify(T_orig, T_rebuilt)) in {S, A}, where classification applies an
ordered sequence of tolerance rules to each (frame, voice) pair.

The equivalence relation is:
  - Reflexive: T ~ T for any trace (proven by construction -- all rules return IDENTICAL)
  - Symmetric for EarlyNoteStart (fixed 2026-04-18): both directions checked
  - NOT fully symmetric: FrameShiftRule still checks rebuilt→original only
  - NOT transitive in general: T1 ~ T2 and T2 ~ T3 does NOT imply T1 ~ T3

Remaining non-symmetry: FrameShiftRule checks if rebuilt's value appears in
original's neighborhood but not vice versa. EarlyNoteStart was fixed to check
both directions (see symmetry fix 2026-04-18).

Mathematical properties
-----------------------
Let R be the set of rules, and classify_R(i, v, T1, T2) be the classification
of voice v at frame i under rule set R.

1. Reflexivity: For all i, v: classify_R(i, v, T, T) = IDENTICAL
   Proof: When T1 = T2, all register values match, so no rule fires.

2. Grade monotonicity: For R' subset of R, grade(R', T1, T2) <= grade(R, T1, T2)
   (where S > A > B > C > F). Removing tolerance rules can only increase the
   count of AUDIBLE classifications, which can only worsen the grade.

3. Non-symmetry example: If rebuilt fires a note 5 frames early (gate=0 in original),
   EarlyNoteStartRule classifies this as INAUDIBLE. But swapping the traces, the
   original's value does NOT appear in the rebuilt's forward window -- classified AUDIBLE.
"""

from __future__ import annotations

import enum
from collections import namedtuple
from typing import List, Optional, Tuple, NamedTuple
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------

# 25 SID registers: 3 voices x 7 regs + 4 filter/volume regs
# Voice N (0-2): base = N*7
#   base+0: freq_lo, base+1: freq_hi, base+2: pw_lo, base+3: pw_hi,
#   base+4: waveform, base+5: ad, base+6: sr
# Global: 21: filt_lo, 22: filt_hi, 23: filt_ctrl, 24: filt_mode_vol

_REGISTER_NAMES = (
    'v1_freq_lo', 'v1_freq_hi', 'v1_pw_lo', 'v1_pw_hi', 'v1_waveform', 'v1_ad', 'v1_sr',
    'v2_freq_lo', 'v2_freq_hi', 'v2_pw_lo', 'v2_pw_hi', 'v2_waveform', 'v2_ad', 'v2_sr',
    'v3_freq_lo', 'v3_freq_hi', 'v3_pw_lo', 'v3_pw_hi', 'v3_waveform', 'v3_ad', 'v3_sr',
    'filt_lo', 'filt_hi', 'filt_ctrl', 'filt_mode_vol',
)

RegisterFrame = namedtuple('RegisterFrame', _REGISTER_NAMES)

# Per-voice register view (7 registers)
VoiceRegisters = namedtuple('VoiceRegisters',
    ['freq_lo', 'freq_hi', 'pw_lo', 'pw_hi', 'waveform', 'ad', 'sr'])


class RegisterTrace:
    """An ordered sequence of RegisterFrames representing a SID performance.

    Attributes:
        frames: List of RegisterFrame named tuples.
        length: Number of frames in the trace.
    """
    __slots__ = ('frames', 'length')

    def __init__(self, frames: List[RegisterFrame]):
        self.frames = list(frames)
        self.length = len(self.frames)

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> RegisterFrame:
        return self.frames[idx]

    def voice(self, frame_idx: int, voice: int) -> VoiceRegisters:
        """Extract the 7 voice registers for a given frame and voice (0-2)."""
        f = self.frames[frame_idx]
        base = voice * 7
        return VoiceRegisters(
            f[base], f[base + 1], f[base + 2], f[base + 3],
            f[base + 4], f[base + 5], f[base + 6],
        )

    @staticmethod
    def from_raw(raw_frames: List[List[int]]) -> 'RegisterTrace':
        """Construct from list-of-lists (siddump output format)."""
        return RegisterTrace([RegisterFrame(*f) for f in raw_frames])

    def freq_hi_events(self, voice: int) -> List[Tuple[int, int]]:
        """Extract note-change events: list of (frame_idx, freq_hi) where freq_hi changes."""
        base = voice * 7 + 1
        events = []
        prev = -1
        for i in range(self.length):
            fhi = self.frames[i][base]
            if fhi != prev:
                events.append((i, fhi))
                prev = fhi
        return events


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

class Classification(enum.IntEnum):
    """Audibility classification for a (frame, voice) difference.

    Ordered from least to most severe. The numeric values encode priority:
    lower values are less severe.
    """
    IDENTICAL = 0       # Registers match exactly
    INAUDIBLE = 1       # Difference exists but is imperceptible
    WEAKLY_AUDIBLE = 2  # Borderline -- tolerated in small quantities (e.g., envelope timing)
    AUDIBLE = 3         # Perceptually wrong -- affects the grade


class DifferenceKind(enum.Enum):
    """Fine-grained difference category matching sid_compare.py counters."""
    PERFECT = 'ok'
    NOTE_JITTER = 'note_jitter'
    NOTE_WRONG = 'note_wrong'
    WAVE_JITTER = 'wave_jitter'
    WAVE_WRONG = 'wave_wrong'
    GATE_DIFF = 'gate_diff'
    ENV_JITTER = 'env_jitter'
    ENV_WRONG = 'env_wrong'
    FREQ_FINE = 'freq_fine'
    PULSE_JITTER = 'pulse_jitter'
    PULSE_DIFF = 'pulse_diff'
    INIT_JITTER = 'init_jitter'

    @property
    def classification(self) -> Classification:
        _MAP = {
            'ok': Classification.IDENTICAL,
            'note_jitter': Classification.INAUDIBLE,
            'note_wrong': Classification.AUDIBLE,
            'wave_jitter': Classification.INAUDIBLE,
            'wave_wrong': Classification.AUDIBLE,
            'gate_diff': Classification.INAUDIBLE,
            'env_jitter': Classification.INAUDIBLE,
            'env_wrong': Classification.WEAKLY_AUDIBLE,
            'freq_fine': Classification.INAUDIBLE,
            'pulse_jitter': Classification.INAUDIBLE,
            'pulse_diff': Classification.INAUDIBLE,
            'init_jitter': Classification.INAUDIBLE,
        }
        return _MAP[self.value]


# ---------------------------------------------------------------------------
# Equivalence rules -- base class
# ---------------------------------------------------------------------------

class EquivalenceRule(ABC):
    """Base class for tolerance rules.

    Each rule is a predicate over a (frame, voice, orig_trace, rebuilt_trace) tuple.
    Rules are applied in priority order. The first rule that matches determines
    the classification. If no rule matches, the difference is AUDIBLE.

    Rules may inspect surrounding frames (windowed context) but must be
    deterministic and stateless across invocations.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable rule name."""
        ...

    @abstractmethod
    def classify(self, frame_idx: int, voice: int,
                 orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        """Attempt to classify the difference at (frame_idx, voice).

        Returns a DifferenceKind if this rule applies, or None to defer
        to the next rule in the chain.

        Precondition: the voice registers differ between orig and rebuilt
        at frame_idx (the caller checks for exact match before invoking rules).
        """
        ...


# ---------------------------------------------------------------------------
# Helper functions used by multiple rules
# ---------------------------------------------------------------------------

def _voice_base(voice: int) -> int:
    """Register index base for voice 0-2."""
    return voice * 7


def _fhi(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 1]


def _wav(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 4]


def _ad(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 5]


def _sr(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 6]


def _flo(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice)]


def _pwlo(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 2]


def _pwhi(trace: RegisterTrace, frame: int, voice: int) -> int:
    return trace[frame][_voice_base(voice) + 3]


# ---------------------------------------------------------------------------
# Concrete rules -- per-frame, per-voice classification
# ---------------------------------------------------------------------------

class SilentVoiceRule(EquivalenceRule):
    """Freq diffs when both waveform upper nibbles are 0 (oscillator off).

    When no waveform bits are set (bits 4-7 = 0), the SID oscillator produces
    no audible output regardless of frequency. Any freq_hi difference is inaudible.

    Symmetry: Yes -- checks both sides symmetrically.
    """

    @property
    def name(self) -> str:
        return 'silent_voice'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_fhi = _fhi(orig, i, v)
        n_fhi = _fhi(rebuilt, i, v)
        if o_fhi != n_fhi:
            o_wav = _wav(orig, i, v)
            n_wav = _wav(rebuilt, i, v)
            if (o_wav & 0xF0) == 0 and (n_wav & 0xF0) == 0:
                return DifferenceKind.NOTE_JITTER
        return None


class NoiseFreqRule(EquivalenceRule):
    """Freq_hi diffs when both sides play noise ($80).

    When both waveforms have noise set (bit 7) and no other wave bits,
    freq_hi controls the noise shift rate, not musical pitch. Different
    rates are perceptually similar. Classified as freq_fine (inaudible).

    Symmetry: Yes.
    """

    @property
    def name(self) -> str:
        return 'noise_freq'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_fhi = _fhi(orig, i, v)
        n_fhi = _fhi(rebuilt, i, v)
        if o_fhi != n_fhi:
            o_wav = _wav(orig, i, v)
            n_wav = _wav(rebuilt, i, v)
            if (o_wav & 0xF0) == 0x80 and (n_wav & 0xF0) == 0x80:
                return DifferenceKind.FREQ_FINE
        return None


class FrameShiftRule(EquivalenceRule):
    """Freq_hi matches original's nearby frame within +/-3 window.

    If the rebuilt's freq_hi value appears in the original trace within
    3 frames, this is a timing shift (IRQ jitter), not a wrong note.

    Symmetry: NO -- checks if rebuilt's value appears in original's window,
    not vice versa. This is intentional: original is ground truth.
    """

    WINDOW = 3

    @property
    def name(self) -> str:
        return 'frame_shift'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_fhi = _fhi(orig, i, v)
        n_fhi = _fhi(rebuilt, i, v)
        if o_fhi == n_fhi:
            return None
        total = min(orig.length, rebuilt.length)
        for d in [-3, -2, -1, 1, 2, 3]:
            j = i + d
            if 0 <= j < total:
                if n_fhi == _fhi(orig, j, v):
                    return DifferenceKind.NOTE_JITTER
        return None


class TransientRule(EquivalenceRule):
    """1-frame transient: both neighbors match.

    If the frame before and after both have matching freq_hi between orig
    and rebuilt, this isolated 1-frame difference is a transient glitch
    (e.g., out-of-bounds freq table reads producing different garbage).

    Symmetry: Yes -- neighbor matching is symmetric.
    """

    @property
    def name(self) -> str:
        return 'transient'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_fhi = _fhi(orig, i, v)
        n_fhi = _fhi(rebuilt, i, v)
        if o_fhi == n_fhi:
            return None
        total = min(orig.length, rebuilt.length)
        prev_ok = (i > 0 and _fhi(orig, i - 1, v) == _fhi(rebuilt, i - 1, v))
        next_ok = (i + 1 < total and _fhi(orig, i + 1, v) == _fhi(rebuilt, i + 1, v))
        if prev_ok and next_ok:
            return DifferenceKind.NOTE_JITTER
        return None


class EarlyNoteStartRule(EquivalenceRule):
    """One side fires the next note while the other is still releasing (gate=0).

    If the early side's freq_hi appears in the late side's next 20 frames,
    this is a timing shift, not a wrong note.

    Checks BOTH directions for symmetry: compare(A,B) == compare(B,A).
    """

    FORWARD_WINDOW = 20

    @property
    def name(self) -> str:
        return 'early_note_start'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_fhi = _fhi(orig, i, v)
        n_fhi = _fhi(rebuilt, i, v)
        if o_fhi == n_fhi:
            return None
        total = min(orig.length, rebuilt.length)
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        # Direction 1: rebuilt early, original still releasing
        if not (o_wav & 0x01):
            for d in range(1, self.FORWARD_WINDOW + 1):
                j = i + d
                if 0 <= j < total:
                    if n_fhi == _fhi(orig, j, v):
                        return DifferenceKind.NOTE_JITTER
        # Direction 2: original early, rebuilt still releasing
        if not (n_wav & 0x01):
            for d in range(1, self.FORWARD_WINDOW + 1):
                j = i + d
                if 0 <= j < total:
                    if o_fhi == _fhi(rebuilt, j, v):
                        return DifferenceKind.NOTE_JITTER
        return None


class TestBitRule(EquivalenceRule):
    """$08/$09 (test bit waveform) near gate transitions is HR artifact.

    During hard restart, the player briefly sets the test bit to reset the
    oscillator. Different player implementations may set/clear this at
    slightly different times. If either side shows test bit ($08/$09)
    near a gate transition, the waveform difference is jitter.

    Symmetry: Yes -- checks both sides' neighborhoods.
    """

    @property
    def name(self) -> str:
        return 'test_bit'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        if (o_wav & 0xFE) == (n_wav & 0xFE):
            return None  # waveform bits match (only gate differs at most)
        # Only applies when one side has test bit
        if (n_wav & 0xFE) != 0x08 and (o_wav & 0xFE) != 0x08:
            return None
        total = min(orig.length, rebuilt.length)
        for d in [-3, -2, -1, 1, 2, 3]:
            j = i + d
            if 0 <= j < total:
                if (_wav(orig, j, v) & 0xFE) == 0x08:
                    return DifferenceKind.WAVE_JITTER
                if (_wav(rebuilt, j, v) & 0xFE) == 0x08:
                    return DifferenceKind.WAVE_JITTER
        return None


class GateOnlyRule(EquivalenceRule):
    """Only the gate bit (bit 0) of the waveform register differs.

    Gate-only differences are timing artifacts from different code paths
    setting gate on/off at slightly different times. The waveform shape
    (bits 4-7) and modulation flags (bits 1-3) are identical.

    Symmetry: Yes.
    """

    @property
    def name(self) -> str:
        return 'gate_only'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        base = _voice_base(v)
        o_fhi = orig[i][base + 1]
        n_fhi = rebuilt[i][base + 1]
        # This rule only fires when freq_hi matches and waveform bits match
        # but the full waveform byte differs (i.e., gate bit only)
        if o_fhi == n_fhi and (o_wav & 0xFE) == (n_wav & 0xFE) and o_wav != n_wav:
            return DifferenceKind.GATE_DIFF
        return None


class WaveShiftRule(EquivalenceRule):
    """Waveform matches original's nearby frame within +/-5 window.

    If the rebuilt's waveform (ignoring gate bit) appears in the original
    within 5 frames, this is timing jitter.

    Also handles: both gates off -> waveform bits inaudible.

    Symmetry: NO for the shift check (checks rebuilt in original's window).
    YES for the gate-off check.
    """

    WINDOW = 5

    @property
    def name(self) -> str:
        return 'wave_shift'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        base = _voice_base(v)
        o_fhi = orig[i][base + 1]
        n_fhi = rebuilt[i][base + 1]
        # Only applies when freq_hi matches but waveform differs (beyond gate)
        if o_fhi != n_fhi:
            return None
        if (o_wav & 0xFE) == (n_wav & 0xFE):
            return None  # waveform bits match

        # Both gates off: waveform bits are inaudible
        if not (o_wav & 1) and not (n_wav & 1):
            return DifferenceKind.WAVE_JITTER

        # Check window
        total = min(orig.length, rebuilt.length)
        for d in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
            j = i + d
            if 0 <= j < total:
                if (n_wav & 0xFE) == (_wav(orig, j, v) & 0xFE):
                    return DifferenceKind.WAVE_JITTER
        return None


class EnvelopeTimingRule(EquivalenceRule):
    """ADSR diffs during gate-off are inaudible (hard restart timing).

    When the gate is off on both sides, envelope register differences
    don't affect the audible output because the voice is in release phase
    and the ADSR values are being overwritten by the SID chip's own
    envelope generator.

    Symmetry: Yes.
    """

    @property
    def name(self) -> str:
        return 'envelope_timing'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        base = _voice_base(v)
        o_fhi = orig[i][base + 1]
        n_fhi = rebuilt[i][base + 1]
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        o_ad_v = _ad(orig, i, v)
        n_ad_v = _ad(rebuilt, i, v)
        o_sr_v = _sr(orig, i, v)
        n_sr_v = _sr(rebuilt, i, v)
        # Only fires when freq and wave match but AD/SR differ
        if o_fhi != n_fhi or (o_wav & 0xFE) != (n_wav & 0xFE):
            return None
        if o_wav != n_wav:
            return None  # gate differs -- handled by GateOnlyRule
        if o_ad_v == n_ad_v and o_sr_v == n_sr_v:
            return None
        gate_on = (o_wav & 1) or (n_wav & 1)
        if not gate_on:
            return DifferenceKind.ENV_JITTER
        return None


class EnvelopeShiftRule(EquivalenceRule):
    """ADSR matches +/-1 frame in the original (write-order timing).

    If the rebuilt's ADSR values match the original's previous or next
    frame, this is a 1-frame envelope timing shift.

    Symmetry: NO -- checks rebuilt's values in original's window.
    """

    @property
    def name(self) -> str:
        return 'envelope_shift'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        base = _voice_base(v)
        o_fhi = orig[i][base + 1]
        n_fhi = rebuilt[i][base + 1]
        o_wav = _wav(orig, i, v)
        n_wav = _wav(rebuilt, i, v)
        o_ad_v = _ad(orig, i, v)
        n_ad_v = _ad(rebuilt, i, v)
        o_sr_v = _sr(orig, i, v)
        n_sr_v = _sr(rebuilt, i, v)
        if o_fhi != n_fhi or (o_wav & 0xFE) != (n_wav & 0xFE):
            return None
        if o_wav != n_wav:
            return None
        if o_ad_v == n_ad_v and o_sr_v == n_sr_v:
            return None
        gate_on = (o_wav & 1) or (n_wav & 1)
        if not gate_on:
            return None  # handled by EnvelopeTimingRule
        total = min(orig.length, rebuilt.length)
        if i > 0:
            if n_ad_v == _ad(orig, i - 1, v) and n_sr_v == _sr(orig, i - 1, v):
                return DifferenceKind.ENV_JITTER
        if i + 1 < total:
            if n_ad_v == _ad(orig, i + 1, v) and n_sr_v == _sr(orig, i + 1, v):
                return DifferenceKind.ENV_JITTER
        return None


class FreqFineRule(EquivalenceRule):
    """Only freq_lo differs (vibrato phase, sub-semitone tuning).

    When freq_hi, waveform, and envelope all match but freq_lo differs,
    the pitch difference is less than one semitone -- typically inaudible
    vibrato phase drift.

    Symmetry: Yes.
    """

    @property
    def name(self) -> str:
        return 'freq_fine'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        base = _voice_base(v)
        # All other regs must match for this to be a pure freq_lo diff
        for offset in [1, 2, 3, 4, 5, 6]:
            if orig[i][base + offset] != rebuilt[i][base + offset]:
                return None
        if orig[i][base] != rebuilt[i][base]:
            return DifferenceKind.FREQ_FINE
        return None


class PulseJitterRule(EquivalenceRule):
    """Pulse width difference < 5% of 12-bit range (200/4096).

    Small pulse width differences from IRQ timing jitter are inaudible.
    Larger differences (>= 5%) are classified as pulse_diff (still inaudible
    for grading, but tracked separately).

    Symmetry: Yes.
    """

    THRESHOLD = 200  # ~5% of 4096

    @property
    def name(self) -> str:
        return 'pulse_jitter'

    def classify(self, i: int, v: int, orig: RegisterTrace, rebuilt: RegisterTrace) -> Optional[DifferenceKind]:
        base = _voice_base(v)
        # Only applies when freq, wave, envelope all match but pulse differs
        for offset in [1, 4, 5, 6]:
            if orig[i][base + offset] != rebuilt[i][base + offset]:
                return None
        o_flo = orig[i][base]
        n_flo = rebuilt[i][base]
        o_pwlo = orig[i][base + 2]
        n_pwlo = rebuilt[i][base + 2]
        o_pwhi = orig[i][base + 3]
        n_pwhi = rebuilt[i][base + 3]
        if o_pwlo == n_pwlo and o_pwhi == n_pwhi:
            return None
        # freq_lo might also differ -- that's ok, pulse rule still applies
        o_pw = o_pwlo | ((o_pwhi & 0x0F) << 8)
        n_pw = n_pwlo | ((n_pwhi & 0x0F) << 8)
        if abs(o_pw - n_pw) < self.THRESHOLD:
            return DifferenceKind.PULSE_JITTER
        else:
            return DifferenceKind.PULSE_DIFF


# ---------------------------------------------------------------------------
# Post-processing (sequence-level) rules
# ---------------------------------------------------------------------------

class SequenceMatchRule:
    """Same note-change-event sequence in different order (95% LCS).

    This is a post-processing rule that operates on the full trace, not
    per-frame. If the rebuilt plays the same sequence of freq_hi change
    events as the original (exact match or >= 95% LCS), all note_wrong
    frames for that voice are reclassified as note_jitter.

    Applied after per-frame classification.

    Symmetry: YES for exact match, approximately symmetric for LCS
    (the 95% threshold uses max(len_a, len_b) as denominator).
    """

    LCS_THRESHOLD = 0.95

    @staticmethod
    def apply(voice: int, orig: RegisterTrace, rebuilt: RegisterTrace,
              classifications: List[DifferenceKind]) -> List[DifferenceKind]:
        """Reclassify note_wrong -> note_jitter if event sequences match.

        Args:
            voice: Voice index (0-2).
            orig: Original trace.
            rebuilt: Rebuilt trace.
            classifications: Per-frame classification list for this voice.
                Modified in place.

        Returns:
            The (possibly modified) classifications list.
        """
        if not any(c == DifferenceKind.NOTE_WRONG for c in classifications):
            return classifications

        total = min(orig.length, rebuilt.length)
        o_events = orig.freq_hi_events(voice)
        n_events = rebuilt.freq_hi_events(voice)
        # Filter to frames within range
        o_vals = [fhi for (fi, fhi) in o_events if fi < total]
        n_vals = [fhi for (fi, fhi) in n_events if fi < total]

        if o_vals == n_vals:
            # Exact sequence match -- all timing jitter
            for idx in range(len(classifications)):
                if classifications[idx] == DifferenceKind.NOTE_WRONG:
                    classifications[idx] = DifferenceKind.NOTE_JITTER
            return classifications

        if len(o_vals) > 5 and len(n_vals) > 5:
            # Greedy LCS approximation (matching sid_compare.py exactly)
            j = 0
            matched = 0
            for val in n_vals:
                while j < len(o_vals):
                    if o_vals[j] == val:
                        matched += 1
                        j += 1
                        break
                    j += 1
            match_ratio = matched / max(len(o_vals), len(n_vals))
            if match_ratio > SequenceMatchRule.LCS_THRESHOLD:
                for idx in range(len(classifications)):
                    if classifications[idx] == DifferenceKind.NOTE_WRONG:
                        classifications[idx] = DifferenceKind.NOTE_JITTER

        return classifications


class GlobalValueSetRule:
    """Both traces use identical set of freq_hi values (arpeggio phase drift).

    If the set of all freq_hi values played (when oscillator is active) is
    the same for both traces, the musical content is identical -- only the
    phase/timing differs.

    Applied after SequenceMatchRule.

    Symmetry: Yes -- set equality is symmetric.
    """

    @staticmethod
    def apply(voice: int, orig: RegisterTrace, rebuilt: RegisterTrace,
              classifications: List[DifferenceKind]) -> List[DifferenceKind]:
        if not any(c == DifferenceKind.NOTE_WRONG for c in classifications):
            return classifications

        total = min(orig.length, rebuilt.length)
        base = _voice_base(voice)

        # Collect freq_hi values where oscillator is active (waveform bits != 0)
        # Skip first 20 frames (init period)
        o_vals = set()
        n_vals = set()
        for i in range(20, total):
            if (orig[i][base + 4] & 0xF0) != 0:
                o_vals.add(orig[i][base + 1])
            if (rebuilt[i][base + 4] & 0xF0) != 0:
                n_vals.add(rebuilt[i][base + 1])

        if o_vals and n_vals and o_vals == n_vals:
            for idx in range(len(classifications)):
                if classifications[idx] == DifferenceKind.NOTE_WRONG:
                    classifications[idx] = DifferenceKind.NOTE_JITTER
        return classifications


class VibratoPhaseRule:
    """Vibrato/arpeggio phase drift: +/-8 frame window, 50% threshold.

    For each note_wrong frame, check if both the original's and rebuilt's
    freq_hi values appear in each other's local windows. If >= 50% of
    wrong frames show this cross-window pattern, reclassify all as jitter.

    Symmetry: Yes -- the cross-window check is symmetric by construction.
    """

    WINDOW = 8
    THRESHOLD = 0.5

    @staticmethod
    def apply(voice: int, orig: RegisterTrace, rebuilt: RegisterTrace,
              classifications: List[DifferenceKind]) -> List[DifferenceKind]:
        if not any(c == DifferenceKind.NOTE_WRONG for c in classifications):
            return classifications

        total = min(orig.length, rebuilt.length)
        base = _voice_base(voice)
        W = VibratoPhaseRule.WINDOW

        reclassified = 0
        for i in range(W, total - W):
            if i >= len(classifications):
                break
            o_fhi = orig[i][base + 1]
            n_fhi = rebuilt[i][base + 1]
            if o_fhi == n_fhi:
                continue
            o_window = set(orig[j][base + 1] for j in range(i - W, i + W + 1) if 0 <= j < total)
            n_window = set(rebuilt[j][base + 1] for j in range(i - W, i + W + 1) if 0 <= j < total)
            if n_fhi in o_window and o_fhi in n_window:
                reclassified += 1

        note_wrong_count = sum(1 for c in classifications if c == DifferenceKind.NOTE_WRONG)
        if reclassified > 0 and reclassified >= note_wrong_count * VibratoPhaseRule.THRESHOLD:
            for idx in range(len(classifications)):
                if classifications[idx] == DifferenceKind.NOTE_WRONG:
                    classifications[idx] = DifferenceKind.NOTE_JITTER

        return classifications


# ---------------------------------------------------------------------------
# EquivalenceRelation -- composes rules
# ---------------------------------------------------------------------------

# The default per-frame rule chain, matching sid_compare.py's if/elif order.
# Rules are checked in this priority order for freq_hi diffs:
#   1. SilentVoiceRule
#   2. NoiseFreqRule
#   3. FrameShiftRule
#   4. TransientRule
#   5. EarlyNoteStartRule
# For waveform diffs (when freq_hi matches):
#   6. WaveShiftRule (includes gate-off check)
#   7. TestBitRule
#   8. GateOnlyRule
# For envelope diffs:
#   9. EnvelopeTimingRule
#  10. EnvelopeShiftRule
# For freq/pulse diffs:
#  11. FreqFineRule
#  12. PulseJitterRule

DEFAULT_PER_FRAME_RULES = [
    SilentVoiceRule(),
    NoiseFreqRule(),
    FrameShiftRule(),
    TransientRule(),
    EarlyNoteStartRule(),
    WaveShiftRule(),
    TestBitRule(),
    GateOnlyRule(),
    EnvelopeTimingRule(),
    EnvelopeShiftRule(),
    FreqFineRule(),
    PulseJitterRule(),
]


class EquivalenceRelation:
    """Composes per-frame rules and post-processing rules to classify all
    (frame, voice) pairs between two traces.

    The classification proceeds in two phases:

    Phase 1 (per-frame): For each frame i and voice v where registers differ,
    apply per-frame rules in priority order. The first matching rule determines
    the DifferenceKind. If no rule matches, the difference is classified based
    on which register differs (note_wrong, wave_wrong, env_wrong).

    Phase 2 (post-processing): Apply sequence-level rules that can reclassify
    note_wrong -> note_jitter based on global trace analysis.

    The init/end grace period (first 10, last 2 frames) is handled before
    rule application -- all differences in those frames are INAUDIBLE.
    """

    INIT_GRACE = 10
    END_GRACE = 2

    def __init__(self, per_frame_rules: Optional[List[EquivalenceRule]] = None,
                 enable_sequence_match: bool = True,
                 enable_global_value_set: bool = True,
                 enable_vibrato_phase: bool = True):
        self.per_frame_rules = per_frame_rules if per_frame_rules is not None else list(DEFAULT_PER_FRAME_RULES)
        self.enable_sequence_match = enable_sequence_match
        self.enable_global_value_set = enable_global_value_set
        self.enable_vibrato_phase = enable_vibrato_phase

    def classify_trace(self, orig: RegisterTrace, rebuilt: RegisterTrace) -> 'TraceClassification':
        """Classify all (frame, voice) pairs between two traces.

        Returns a TraceClassification containing per-voice, per-frame results.
        """
        total = min(orig.length, rebuilt.length)
        if total == 0:
            return TraceClassification(total=0, voice_classifications=[[], [], []], filter_diffs=0, init_jitter=0, perfect=0)

        # Per-voice classification lists (one DifferenceKind per frame)
        voice_cls: List[List[DifferenceKind]] = [[], [], []]
        filter_diffs = 0
        init_jitter = 0
        perfect = 0

        for i in range(total):
            o = orig[i]
            n = rebuilt[i]

            if list(o) == list(n):
                perfect += 1
                for v in range(3):
                    voice_cls[v].append(DifferenceKind.PERFECT)
                continue

            # Grace period
            if i < self.INIT_GRACE or i >= total - self.END_GRACE:
                init_jitter += 1
                for v in range(3):
                    voice_cls[v].append(DifferenceKind.PERFECT)
                continue

            # Filter check
            if list(o[21:25]) != list(n[21:25]):
                filter_diffs += 1

            # Per-voice classification
            for v in range(3):
                base = v * 7
                o_voice = list(o[base:base + 7])
                n_voice = list(n[base:base + 7])

                if o_voice == n_voice:
                    voice_cls[v].append(DifferenceKind.PERFECT)
                    continue

                # Try per-frame rules in priority order
                classified = None
                for rule in self.per_frame_rules:
                    result = rule.classify(i, v, orig, rebuilt)
                    if result is not None:
                        classified = result
                        break

                if classified is not None:
                    voice_cls[v].append(classified)
                else:
                    # Fallback: determine category from which register differs
                    # This matches sid_compare.py's if/elif chain
                    o_fhi = o[base + 1]
                    n_fhi = n[base + 1]
                    o_wav = o[base + 4]
                    n_wav = n[base + 4]
                    o_ad_v = o[base + 5]
                    n_ad_v = n[base + 5]
                    o_sr_v = o[base + 6]
                    n_sr_v = n[base + 6]
                    o_flo = o[base]
                    n_flo = n[base]
                    o_pwlo = o[base + 2]
                    n_pwlo = n[base + 2]
                    o_pwhi = o[base + 3]
                    n_pwhi = n[base + 3]

                    if o_fhi != n_fhi:
                        voice_cls[v].append(DifferenceKind.NOTE_WRONG)
                    elif (o_wav & 0xFE) != (n_wav & 0xFE):
                        voice_cls[v].append(DifferenceKind.WAVE_WRONG)
                    elif o_wav != n_wav:
                        voice_cls[v].append(DifferenceKind.GATE_DIFF)
                    elif o_ad_v != n_ad_v or o_sr_v != n_sr_v:
                        voice_cls[v].append(DifferenceKind.ENV_WRONG)
                    elif o_flo != n_flo:
                        voice_cls[v].append(DifferenceKind.FREQ_FINE)
                    elif o_pwlo != n_pwlo or o_pwhi != n_pwhi:
                        # Pulse without jitter rule match -> pulse_diff
                        voice_cls[v].append(DifferenceKind.PULSE_DIFF)
                    else:
                        voice_cls[v].append(DifferenceKind.PERFECT)

        # Phase 2: post-processing rules
        for v in range(3):
            if self.enable_sequence_match:
                SequenceMatchRule.apply(v, orig, rebuilt, voice_cls[v])
            if self.enable_global_value_set:
                GlobalValueSetRule.apply(v, orig, rebuilt, voice_cls[v])
            if self.enable_vibrato_phase:
                VibratoPhaseRule.apply(v, orig, rebuilt, voice_cls[v])

        return TraceClassification(
            total=total,
            voice_classifications=voice_cls,
            filter_diffs=filter_diffs,
            init_jitter=init_jitter,
            perfect=perfect,
        )


# ---------------------------------------------------------------------------
# TraceClassification -- results container
# ---------------------------------------------------------------------------

class TraceClassification:
    """Result of classifying all (frame, voice) pairs between two traces.

    Provides aggregate counts matching sid_compare.py's results dict,
    plus the grading function.
    """

    def __init__(self, total: int, voice_classifications: List[List[DifferenceKind]],
                 filter_diffs: int, init_jitter: int, perfect: int):
        self.total = total
        self.voice_classifications = voice_classifications
        self.filter_diffs = filter_diffs
        self.init_jitter = init_jitter
        self.perfect = perfect

    def voice_counts(self, voice: int) -> dict:
        """Count occurrences of each DifferenceKind for a voice.

        Returns dict matching sid_compare.py's per-voice result dict.
        """
        counts = {
            'note_wrong': 0, 'note_jitter': 0,
            'wave_wrong': 0, 'wave_jitter': 0,
            'gate_diff': 0,
            'env_wrong': 0, 'env_jitter': 0,
            'freq_fine': 0,
            'pulse_diff': 0, 'pulse_jitter': 0,
            'ok': 0,
        }
        for kind in self.voice_classifications[voice]:
            if kind == DifferenceKind.PERFECT:
                counts['ok'] += 1
            elif kind == DifferenceKind.INIT_JITTER:
                counts['ok'] += 1
            else:
                counts[kind.value] += 1
        return counts

    def to_results_dict(self) -> dict:
        """Convert to sid_compare.py-compatible results dict."""
        return {
            'total': self.total,
            'perfect': self.perfect,
            'voices': [self.voice_counts(v) for v in range(3)],
            'filter_diff': self.filter_diffs,
            'init_jitter': self.init_jitter,
        }

    def grade(self) -> Tuple[float, str]:
        """Compute (score, grade) matching sid_compare.py's score_results exactly.

        Returns:
            (score, grade) where score is 0-100 and grade is S/A/B/C/F.
        """
        total = self.total
        if total == 0:
            return (0.0, 'F')

        strong_audible = 0
        env_audible = 0
        inaudible = 0

        for v in range(3):
            counts = self.voice_counts(v)
            strong_audible += counts['note_wrong'] + counts['wave_wrong']
            env_audible += counts['env_wrong']
            inaudible += (counts['freq_fine'] + counts['pulse_diff'] + counts['gate_diff']
                          + counts['pulse_jitter'] + counts['env_jitter'] + counts['wave_jitter']
                          + counts['note_jitter'])

        audible = strong_audible + env_audible
        audible_pct = audible / (total * 3)
        inaudible_pct = inaudible / (total * 3)
        strong_pct = strong_audible / (total * 3)
        env_pct = env_audible / (total * 3)

        score = max(0, 100 - audible_pct * 100 - inaudible_pct * 5)

        if strong_pct == 0 and env_pct == 0 and inaudible == 0:
            grade = 'S'
        elif strong_pct == 0 and env_pct < 0.01:
            grade = 'A'
        elif audible_pct < 0.02:
            grade = 'B'
        elif audible_pct < 0.10:
            grade = 'C'
        else:
            grade = 'F'

        return (score, grade)


# ---------------------------------------------------------------------------
# Convenience function matching sid_compare.compare_tolerant
# ---------------------------------------------------------------------------

def compare_tolerant(orig_frames: List[List[int]], new_frames: List[List[int]]) -> Optional[dict]:
    """Drop-in replacement for sid_compare.compare_tolerant.

    Takes raw frame lists (siddump format) and returns the same results dict.
    """
    total = min(len(orig_frames), len(new_frames))
    if total == 0:
        return None

    orig = RegisterTrace.from_raw(orig_frames[:total])
    rebuilt = RegisterTrace.from_raw(new_frames[:total])

    relation = EquivalenceRelation()
    tc = relation.classify_trace(orig, rebuilt)
    return tc.to_results_dict()


def score_results(results: dict) -> Tuple[float, str]:
    """Drop-in replacement for sid_compare.score_results."""
    total = results['total']
    if total == 0:
        return (0.0, 'F')

    strong_audible = 0
    env_audible = 0
    inaudible = 0

    for v in range(3):
        vr = results['voices'][v]
        strong_audible += vr['note_wrong'] + vr['wave_wrong']
        env_audible += vr['env_wrong']
        inaudible += (vr['freq_fine'] + vr['pulse_diff'] + vr['gate_diff']
                      + vr['pulse_jitter'] + vr['env_jitter'] + vr['wave_jitter']
                      + vr['note_jitter'])

    audible = strong_audible + env_audible
    audible_pct = audible / (total * 3)
    inaudible_pct = inaudible / (total * 3)
    strong_pct = strong_audible / (total * 3)
    env_pct = env_audible / (total * 3)

    score = max(0, 100 - audible_pct * 100 - inaudible_pct * 5)

    if strong_pct == 0 and env_pct == 0 and inaudible == 0:
        grade = 'S'
    elif strong_pct == 0 and env_pct < 0.01:
        grade = 'A'
    elif audible_pct < 0.02:
        grade = 'B'
    elif audible_pct < 0.10:
        grade = 'C'
    else:
        grade = 'F'

    return (score, grade)


# ---------------------------------------------------------------------------
# Property verification
# ---------------------------------------------------------------------------

def _make_frame(**kwargs) -> RegisterFrame:
    """Helper to create a RegisterFrame with defaults (all zeros)."""
    defaults = {name: 0 for name in _REGISTER_NAMES}
    defaults.update(kwargs)
    return RegisterFrame(**defaults)


def _make_note_frame(voice: int, freq_hi: int, waveform: int = 0x41,
                     ad: int = 0x09, sr: int = 0x00, freq_lo: int = 0,
                     pw_lo: int = 0, pw_hi: int = 0) -> RegisterFrame:
    """Create a frame with one voice active."""
    vals = [0] * 25
    base = voice * 7
    vals[base] = freq_lo
    vals[base + 1] = freq_hi
    vals[base + 2] = pw_lo
    vals[base + 3] = pw_hi
    vals[base + 4] = waveform
    vals[base + 5] = ad
    vals[base + 6] = sr
    return RegisterFrame(*vals)


class PropertyTests:
    """Verification of mathematical properties of the equivalence relation."""

    @staticmethod
    def test_reflexivity() -> bool:
        """T ~ T for any trace.

        Constructs several synthetic traces and verifies that comparing
        any trace against itself always yields grade S (perfect).
        """
        traces = [
            # Trace 1: silence
            RegisterTrace([_make_frame() for _ in range(50)]),
            # Trace 2: steady note on voice 1
            RegisterTrace([_make_note_frame(0, 0x40, 0x41) for _ in range(50)]),
            # Trace 3: arpeggio on voice 2
            RegisterTrace([
                _make_note_frame(1, [0x20, 0x28, 0x30][i % 3], 0x41)
                for i in range(50)
            ]),
            # Trace 4: mixed voices
            RegisterTrace([
                RegisterFrame(
                    *([0, 0x40 + (i % 3), 0, 8, 0x41, 9, 0] +  # v1
                      [0, 0x30, 0, 4, 0x21, 0x0A, 0x0B] +       # v2
                      [0, 0, 0, 0, 0, 0, 0] +                    # v3
                      [0, 0, 0, 0x0F])                            # filter
                ) for i in range(50)
            ]),
        ]

        relation = EquivalenceRelation()
        for idx, trace in enumerate(traces):
            tc = relation.classify_trace(trace, trace)
            score, grade = tc.grade()
            if grade != 'S':
                print(f"  FAIL: Reflexivity violated on trace {idx}: grade={grade}, score={score}")
                return False
        print("  PASS: Reflexivity holds for all test traces")
        return True

    @staticmethod
    def test_symmetry() -> Tuple[bool, List[str]]:
        """Check if T1 ~ T2 implies T2 ~ T1.

        EXPECTED: This property does NOT hold in general. This test
        documents the specific asymmetries.

        Returns (is_symmetric, list_of_violations).
        """
        violations = []
        relation = EquivalenceRelation()

        # Case 1: Early note start (EarlyNoteStartRule is asymmetric)
        # Rebuilt fires note while original is still releasing (gate=0).
        # The rebuilt's freq_hi appears in the original's forward window,
        # so A->B classifies as jitter. But B->A has gate=1 in B, so the
        # rule doesn't fire, and A's freq_hi does NOT appear in B's window.
        # Need enough frames and multiple asymmetric regions to avoid
        # post-processing rules masking the effect.
        frames_a = []
        frames_b = []
        for i in range(200):
            if i < 12:
                frames_a.append(_make_note_frame(0, 0x40, 0x41))
                frames_b.append(_make_note_frame(0, 0x40, 0x41))
            elif 50 <= i < 55:
                # A: releasing (gate off), B: already playing new note
                frames_a.append(_make_note_frame(0, 0x40, 0x00))
                frames_b.append(_make_note_frame(0, 0x60, 0x41))
            elif 55 <= i < 60:
                frames_a.append(_make_note_frame(0, 0x60, 0x41))
                frames_b.append(_make_note_frame(0, 0x60, 0x41))
            elif 100 <= i < 105:
                frames_a.append(_make_note_frame(0, 0x30, 0x00))
                frames_b.append(_make_note_frame(0, 0x70, 0x41))
            elif 105 <= i < 115:
                frames_a.append(_make_note_frame(0, 0x70, 0x41))
                frames_b.append(_make_note_frame(0, 0x70, 0x41))
            else:
                frames_a.append(_make_note_frame(0, 0x40, 0x41))
                frames_b.append(_make_note_frame(0, 0x40, 0x41))

        trace_a = RegisterTrace(frames_a)
        trace_b = RegisterTrace(frames_b)

        # Use relation without post-processing to isolate per-frame asymmetry
        relation_no_pp = EquivalenceRelation(
            enable_sequence_match=False,
            enable_global_value_set=False,
            enable_vibrato_phase=False,
        )

        tc_ab = relation_no_pp.classify_trace(trace_a, trace_b)
        tc_ba = relation_no_pp.classify_trace(trace_b, trace_a)
        grade_ab = tc_ab.grade()[1]
        grade_ba = tc_ba.grade()[1]

        if grade_ab != grade_ba:
            violations.append(
                f"EarlyNoteStart asymmetry: A->B grade={grade_ab}, B->A grade={grade_ba}"
            )

        is_symmetric = len(violations) == 0
        if is_symmetric:
            print("  PASS: Symmetry holds for all test cases (surprising!)")
        else:
            print(f"  EXPECTED: Symmetry violations found ({len(violations)}):")
            for v in violations:
                print(f"    - {v}")
        return is_symmetric, violations

    @staticmethod
    def test_grade_monotonicity() -> bool:
        """Removing a tolerance rule never improves the grade.

        Tests that grade(fewer_rules) <= grade(all_rules) where
        S > A > B > C > F.
        """
        grade_order = {'S': 4, 'A': 3, 'B': 2, 'C': 1, 'F': 0}

        # Create a trace pair with timing jitter (needs FrameShiftRule)
        frames_orig = []
        frames_rebuilt = []
        for i in range(100):
            if 20 <= i < 80:
                # Original plays alternating notes
                fhi = 0x40 if (i % 10 < 5) else 0x50
                frames_orig.append(_make_note_frame(0, fhi, 0x41))
                # Rebuilt is 1 frame late
                fhi_r = 0x40 if ((i - 1) % 10 < 5) else 0x50
                frames_rebuilt.append(_make_note_frame(0, fhi_r, 0x41))
            else:
                frames_orig.append(_make_note_frame(0, 0x40, 0x41))
                frames_rebuilt.append(_make_note_frame(0, 0x40, 0x41))

        orig = RegisterTrace(frames_orig)
        rebuilt = RegisterTrace(frames_rebuilt)

        # Full rule set
        full_relation = EquivalenceRelation()
        full_tc = full_relation.classify_trace(orig, rebuilt)
        full_grade = full_tc.grade()[1]

        # Test removing each rule individually
        all_pass = True
        for rule_idx, rule in enumerate(DEFAULT_PER_FRAME_RULES):
            reduced_rules = [r for j, r in enumerate(DEFAULT_PER_FRAME_RULES) if j != rule_idx]
            reduced_relation = EquivalenceRelation(per_frame_rules=reduced_rules)
            reduced_tc = reduced_relation.classify_trace(orig, rebuilt)
            reduced_grade = reduced_tc.grade()[1]

            if grade_order[reduced_grade] > grade_order[full_grade]:
                print(f"  FAIL: Removing {rule.name} improved grade from {full_grade} to {reduced_grade}")
                all_pass = False

        # Test removing post-processing rules
        for pp_name, kwargs in [
            ('sequence_match', {'enable_sequence_match': False}),
            ('global_value_set', {'enable_global_value_set': False}),
            ('vibrato_phase', {'enable_vibrato_phase': False}),
        ]:
            reduced_relation = EquivalenceRelation(**kwargs)
            reduced_tc = reduced_relation.classify_trace(orig, rebuilt)
            reduced_grade = reduced_tc.grade()[1]
            if grade_order[reduced_grade] > grade_order[full_grade]:
                print(f"  FAIL: Disabling {pp_name} improved grade from {full_grade} to {reduced_grade}")
                all_pass = False

        if all_pass:
            print("  PASS: Grade monotonicity holds -- removing rules never improves grade")
        return all_pass

    @staticmethod
    def test_identical_traces_grade_s() -> bool:
        """Identical traces always get grade S."""
        frames = [
            RegisterFrame(
                *([0, 0x40, 0x08, 0x08, 0x41, 0x09, 0x00] * 3 + [0, 0, 0, 0x0F])
            ) for _ in range(100)
        ]
        trace = RegisterTrace(frames)
        relation = EquivalenceRelation()
        tc = relation.classify_trace(trace, trace)
        score, grade = tc.grade()
        if grade == 'S' and score == 100.0:
            print("  PASS: Identical traces yield grade S, score 100.0")
            return True
        else:
            print(f"  FAIL: Identical traces yield grade={grade}, score={score}")
            return False

    @staticmethod
    def test_completely_different_traces_grade_f() -> bool:
        """Completely different traces get grade F."""
        frames_a = [_make_note_frame(0, 0x20, 0x41) for _ in range(100)]
        frames_b = [_make_note_frame(0, 0x60, 0x21) for _ in range(100)]
        orig = RegisterTrace(frames_a)
        rebuilt = RegisterTrace(frames_b)
        relation = EquivalenceRelation()
        tc = relation.classify_trace(orig, rebuilt)
        _, grade = tc.grade()
        if grade == 'F':
            print("  PASS: Completely different traces yield grade F")
            return True
        else:
            print(f"  FAIL: Completely different traces yield grade={grade}")
            return False

    @staticmethod
    def run_all() -> bool:
        """Run all property tests. Returns True if all pass (or expected failures)."""
        print("=== Trace Equivalence Property Tests ===\n")

        results = []

        print("1. Reflexivity (T ~ T):")
        results.append(PropertyTests.test_reflexivity())

        print("\n2. Identical traces -> Grade S:")
        results.append(PropertyTests.test_identical_traces_grade_s())

        print("\n3. Completely different traces -> Grade F:")
        results.append(PropertyTests.test_completely_different_traces_grade_f())

        print("\n4. Symmetry (T1 ~ T2 => T2 ~ T1):")
        is_sym, violations = PropertyTests.test_symmetry()
        # Symmetry violations are EXPECTED, not failures
        results.append(True)

        print("\n5. Grade monotonicity (fewer rules => same or worse grade):")
        results.append(PropertyTests.test_grade_monotonicity())

        print("\n" + "=" * 50)
        all_pass = all(results)
        if all_pass:
            print("All property tests passed.")
        else:
            print("Some property tests FAILED.")
        return all_pass


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    success = PropertyTests.run_all()
    sys.exit(0 if success else 1)
