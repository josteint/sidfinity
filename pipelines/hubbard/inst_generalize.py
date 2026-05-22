"""inst_generalize.py — Phase 3 step 3.2: decode each Commando instrument
into a behavioral model expressed in USF2 primitives.

Why not pure capture generalisation.  An earlier attempt tried to derive
each instrument purely from its py65 register-write captures. It cannot
work: Commando's modulations are not pure functions of (pitch, frame
offset). `_apply_vibrato` keys off the GLOBAL frame counter
(`frame_ctr & 7`); `_apply_arpeggio_freq` off `frame_ctr & 1`; PWM is a
free-running per-voice accumulator that is never reset between notes.
The same instrument at the same pitch therefore produces different
register streams depending on song position.

What does define an instrument, exactly and reliably, is its 8-byte
row in the instrument table at $5591 + inst*8:

    +0 pw_lo   +1 pw_hi   +2 ctrl   +3 ad   +4 sr
    +5 vib_depth   +6 pwm_speed   +7 fx_flags

    fx_flags bit 0  skydive / freqSlide   (decrement freq_hi)
             bit 1  INC-freq_hi-by-2 on odd frames
             bit 2  arpeggio             (base / base+12 by frame parity)
             bit 3  PWM mode: 1 = linear (uni), 0 = bidirectional

This module reads those bytes, interprets them via the engine semantics
(see src/hubbard_emu.py), and produces an `InstrumentModel` — the
parameter set 3.3 will serialise to a `USFInstrument2` literal. The
py65 captures from `inst_program.capture()` then VERIFY the decode:
the init block and HR block are checked byte-for-byte, and each
fx-driven feature is checked for presence/absence.

See docs/usf_instrument_program_plan.md (Phase 3).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.inst_program import (  # noqa: E402
    CaptureResult, NoteOccurrence, capture)

# Instrument table: 13 rows of 8 bytes at $5591 (Commando).
INSTR_TABLE_BASE = 0x5591
INSTR_SIZE = 8
N_INSTRUMENTS = 13

# Hard restart: the gate-off block fires 3 frames before note end.
HR_FRAMES = 3

# Register indices within a voice.
R_FREQ_LO, R_FREQ_HI, R_PW_LO, R_PW_HI, R_CTRL, R_AD, R_SR = range(7)


# ---------------------------------------------------------------------------
# USF2-shaped parameter pieces
# ---------------------------------------------------------------------------

@dataclass
class VibratoSpec:
    """Triangle LFO on freq, gated by note duration. `_apply_vibrato`."""
    depth: int                  # instrument byte +5; LFO delta >> (depth+1)
    period: int = 8             # frame_ctr & 7, folded triangle
    onset_dur: int = 6          # only applies when note's dur field >= 6


@dataclass
class ArpSpec:
    """Octave arpeggio: alternate pitch / pitch+12 by frame parity."""
    intervals: tuple = (0, 12)
    step_every: int = 1


@dataclass
class PwmSpec:
    """Pulse-width modulation. `_apply_pw`.

    Important: `_apply_pw` writes the stepped value back into the
    instrument table row (`_set_instr_pw_lo/hi`). The pw bytes are
    therefore a free-running accumulator that is never reset between
    notes — `seed_*` is only the song-start value. In USF2 this state
    lives per-voice in the codegen; the instrument data carries the
    seed + the step rule only."""
    mode: str                   # 'linear' | 'bidirectional'
    speed: int = 0              # linear: pw_lo += speed each frame
    period: int = 0             # bidirectional: reload for the step counter
    step: int = 0               # bidirectional: pw delta per step
    lo_bound: int = 0x08        # bidirectional: pw_hi lower turn-around
    hi_bound: int = 0x0E        # bidirectional: pw_hi upper turn-around
    seed_lo: int = 0            # song-start pw_lo (instrument table byte)
    seed_hi: int = 0            # song-start pw_hi (instrument table byte)


@dataclass
class InstrumentModel:
    """One Commando instrument as USF2-ready behavioral parameters."""
    inst: int
    # init block — const writes at note start (frame offset 0)
    init_ctrl: int
    init_pw_lo: int
    init_pw_hi: int
    init_ad: int
    init_sr: int
    # hard-restart block — const writes HR_FRAMES before note end
    hr_ctrl: int                # init_ctrl & 0xFE
    # how the init-block pw bytes behave: 'const' or 'accumulator'
    # (accumulator = owned by PWM, free-running across notes)
    pw_lo_kind: str
    pw_hi_kind: str
    # fx
    fx_flags: int
    freq_slide: bool            # bit 0 — skydive
    inc_by2: bool               # bit 1
    arpeggio: Optional[ArpSpec]  # bit 2
    vibrato: Optional[VibratoSpec]
    pwm: Optional[PwmSpec]
    # verification, filled by verify()
    verified: Optional[bool] = None
    verify_note: str = ''

    def summary(self) -> str:
        feats = []
        if self.vibrato:
            feats.append(f'vibrato(depth={self.vibrato.depth})')
        if self.freq_slide:
            feats.append('freqSlide')
        if self.inc_by2:
            feats.append('incBy2')
        if self.arpeggio:
            feats.append(f'arp{self.arpeggio.intervals}')
        if self.pwm:
            if self.pwm.mode == 'linear':
                feats.append(f'pwm:linear(speed=${self.pwm.speed:02X})')
            else:
                feats.append(f'pwm:bidir(period={self.pwm.period},'
                             f'step=${self.pwm.step:02X})')
        return ', '.join(feats) if feats else 'plain'


# ---------------------------------------------------------------------------
# Decode
# ---------------------------------------------------------------------------

def decode_instrument(inst: int, binary: bytes, load_addr: int,
                      base: int = INSTR_TABLE_BASE,
                      arp_interval: int = 12) -> InstrumentModel:
    """Decode instrument `inst` from its 8-byte table row at `base`.

    The 8-byte row layout (pw_lo, pw_hi, ctrl, ad, sr, vib_depth,
    pwm_speed, fx_flags) is shared across the whole Hubbard '85 engine
    family; the table address and the arpeggio interval differ per
    engine (Commando 12 semitones, Devils Galop 24)."""
    off = base + inst * INSTR_SIZE - load_addr
    pw_lo, pw_hi, ctrl, ad, sr, vib_depth, pwm_speed, fx = binary[off:off + 8]

    vibrato = VibratoSpec(depth=vib_depth) if vib_depth != 0 else None

    arpeggio = ArpSpec(intervals=(0, arp_interval)) if (fx & 0x04) else None

    pwm = None
    pw_lo_kind = pw_hi_kind = 'const'
    if pwm_speed != 0:
        if fx & 0x08:                                   # bit 3 -> linear
            pwm = PwmSpec(mode='linear', speed=pwm_speed,
                          seed_lo=pw_lo, seed_hi=pw_hi)
            pw_lo_kind = 'accumulator'
        else:                                           # bidirectional
            pwm = PwmSpec(mode='bidirectional',
                          period=pwm_speed & 0x1F,
                          step=pwm_speed & 0xE0,
                          seed_lo=pw_lo, seed_hi=pw_hi)
            pw_lo_kind = pw_hi_kind = 'accumulator'

    return InstrumentModel(
        inst=inst,
        init_ctrl=ctrl, init_pw_lo=pw_lo, init_pw_hi=pw_hi,
        init_ad=ad, init_sr=sr,
        hr_ctrl=ctrl & 0xFE,
        pw_lo_kind=pw_lo_kind, pw_hi_kind=pw_hi_kind,
        fx_flags=fx,
        freq_slide=bool(fx & 0x01),
        inc_by2=bool(fx & 0x02),
        arpeggio=arpeggio,
        vibrato=vibrato,
        pwm=pwm,
    )


def decode_all(sid_path: str, base: int = INSTR_TABLE_BASE,
               count: int = N_INSTRUMENTS,
               arp_interval: int = 12) -> list[InstrumentModel]:
    """Decode `count` instruments from the 8-byte table at `base`.
    Defaults are Commando's; other Hubbard '85 engines pass their own
    instrument-table address, count and arpeggio interval."""
    from src.hubbard_emu import load_sid
    _, binary, load_addr = load_sid(sid_path)
    return [decode_instrument(i, binary, load_addr, base, arp_interval)
            for i in range(count)]


# ---------------------------------------------------------------------------
# Verification against py65 captures
# ---------------------------------------------------------------------------

def _writes_dict(frame_writes: list[tuple[int, int]]) -> dict[int, list[int]]:
    """Group a frame's (reg, val) writes by register, preserving order."""
    out: dict[int, list[int]] = {}
    for reg, val in frame_writes:
        out.setdefault(reg, []).append(val)
    return out


def verify_instrument(model: InstrumentModel, occs: list[NoteOccurrence],
                      freq_table: list[int]) -> None:
    """Check the decoded model against captured note occurrences. Sets
    `model.verified` and `model.verify_note`.

    An occurrence whose note-start frame is empty/short was suppressed by
    the drum engine (the melodic write paths are gated on `drum_enable`);
    those are skipped, not counted as mismatches. PWM-owned pw registers
    are accumulator state, so they are excluded from the byte-exact init
    check and verified separately by their per-frame delta."""
    if not occs:
        model.verified = None
        model.verify_note = 'no captured occurrences'
        return

    # const init registers (accumulator pw bytes are excluded)
    const_regs = [R_FREQ_LO, R_FREQ_HI, R_CTRL, R_AD, R_SR]
    if model.pw_lo_kind == 'const':
        const_regs.append(R_PW_LO)
    if model.pw_hi_kind == 'const':
        const_regs.append(R_PW_HI)

    init_checked = init_ok = 0
    hr_checked = hr_ok = 0
    drum_suppressed = 0
    feature_fail: list[str] = []

    for o in occs:
        d0 = _writes_dict(o.writes[0] if o.writes else [])
        # A clean (drum-disabled) note-start writes all 7 registers.
        if all(r in d0 for r in range(7)):
            init_checked += 1
            f = freq_table[o.pitch]
            want = {
                R_FREQ_LO: f & 0xFF, R_FREQ_HI: (f >> 8) & 0xFF,
                R_CTRL: model.init_ctrl, R_AD: model.init_ad,
                R_SR: model.init_sr, R_PW_LO: model.init_pw_lo,
                R_PW_HI: model.init_pw_hi,
            }
            if all(d0[r][0] == want[r] for r in const_regs):
                init_ok += 1
        else:
            drum_suppressed += 1

        # HR block: the frame HR_FRAMES before note end.
        hr_k = o.n_frames - HR_FRAMES
        if 0 <= hr_k < o.n_frames:
            dhr = _writes_dict(o.writes[hr_k])
            if R_CTRL in dhr and R_AD in dhr and R_SR in dhr:
                hr_checked += 1
                if (dhr[R_CTRL][-1] == model.hr_ctrl
                        and dhr[R_AD][-1] == 0 and dhr[R_SR][-1] == 0):
                    hr_ok += 1

    # Whether this instrument's notes have a non-zero freq at all: when
    # freq_table[pitch] is 0 the engine's freq effects are inert by design.
    freq_inert = all(freq_table[o.pitch] == 0 for o in occs)

    # freqSlide: a real skydive is a long monotone freq_hi descent.
    # Vibrato also moves freq_hi, so the slide cross-check is only
    # reliable for non-vibrato, non-inert instruments.
    if not model.vibrato and not freq_inert:
        saw_slide = _saw_freq_slide(occs)
        if model.freq_slide and not saw_slide:
            feature_fail.append('fx bit0 set but no freq_hi slide observed')
        if not model.freq_slide and saw_slide:
            feature_fail.append('freq_hi slide observed but fx bit0 clear')

    if model.arpeggio and not freq_inert and not _saw_octave_arp(occs, freq_table):
        feature_fail.append('fx bit2 set but no octave arpeggio observed')

    saw_pw = _saw_pw_writes(occs)
    if model.pwm and not saw_pw:
        feature_fail.append('pwm set but no pw writes observed')
    if not model.pwm and saw_pw:
        feature_fail.append('pw writes observed but pwm_speed is 0')

    # linear-pwm step is an informational cross-check, not a gate
    # (the engine's uni-PWM add has a carry-in quirk — hubbard_emu:805).
    info = ''
    if model.pwm and model.pwm.mode == 'linear' and saw_pw:
        if not _linear_pwm_delta_ok(occs, model.pwm.speed):
            info = f'  note: linear pwm step not consistently ' \
                   f'${model.pwm.speed:02X}'

    init_pct = (100.0 * init_ok / init_checked) if init_checked else 0.0
    hr_pct = (100.0 * hr_ok / hr_checked) if hr_checked else 0.0
    model.verified = (not feature_fail and init_checked > 0
                      and init_ok == init_checked
                      and (hr_checked == 0 or hr_ok == hr_checked))
    model.verify_note = (
        f'init {init_ok}/{init_checked} ({init_pct:.0f}%)  '
        f'HR {hr_ok}/{hr_checked} ({hr_pct:.0f}%)  '
        f'drum-suppressed {drum_suppressed}'
        + ('  freq-inert(pitch->0)' if freq_inert else '')
        + (('  FEATURE: ' + '; '.join(feature_fail)) if feature_fail else '')
        + info)


def _saw_freq_slide(occs: list[NoteOccurrence], run: int = 6) -> bool:
    """True if any note shows a strictly-decreasing freq_hi run of length
    >= `run` — long enough to be a skydive, not a vibrato downswing.

    The skydive runs before the arpeggio in `_apply_effects`, so the
    slide is the FIRST freq_hi write of each frame; later freq_hi writes
    are the arpeggio and must not pollute the run detection."""
    for o in occs:
        seq = []
        for fw in o.writes:
            hi = [v for r, v in fw if r == R_FREQ_HI]
            if hi:
                seq.append(hi[0])
        streak = 1
        for a, b in zip(seq, seq[1:]):
            streak = streak + 1 if b == ((a - 1) & 0xFF) else 1
            if streak >= run:
                return True
    return False


def _linear_pwm_delta_ok(occs: list[NoteOccurrence], speed: int) -> bool:
    """True if consecutive pw_lo writes advance by `speed` (mod 256)."""
    for o in occs:
        seq = [v for fw in o.writes for r, v in fw if r == R_PW_LO]
        good = sum(1 for a, b in zip(seq, seq[1:])
                   if (b - a) & 0xFF == speed & 0xFF)
        if len(seq) >= 3 and good >= len(seq) - 2:
            return True
    return False


def _saw_octave_arp(occs: list[NoteOccurrence],
                    freq_table: list[int]) -> bool:
    for o in occs:
        if o.pitch + 12 >= len(freq_table):
            continue
        oct_hi = (freq_table[o.pitch + 12] >> 8) & 0xFF
        base_hi = (freq_table[o.pitch] >> 8) & 0xFF
        if oct_hi == base_hi:
            continue
        seen_oct = seen_base = False
        for fw in o.writes:
            for reg, val in fw:
                if reg == R_FREQ_HI and val == oct_hi:
                    seen_oct = True
                if reg == R_FREQ_HI and val == base_hi:
                    seen_base = True
        if seen_oct and seen_base:
            return True
    return False


def _saw_pw_writes(occs: list[NoteOccurrence]) -> bool:
    for o in occs:
        for fw in o.writes[1:]:                 # after the init block
            for reg, _ in fw:
                if reg in (R_PW_LO, R_PW_HI):
                    return True
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def capture_all_subtunes(sid_path: str, n_frames: int
                         ) -> dict[int, list[NoteOccurrence]]:
    """Capture every subtune and pool note occurrences by instrument."""
    from src.hubbard_emu import load_sid
    hdr, _, _ = load_sid(sid_path)
    pooled: dict[int, list[NoteOccurrence]] = {}
    for subtune in range(max(1, hdr['num_songs'])):
        cap: CaptureResult = capture(sid_path, n_frames=n_frames,
                                     subtune=subtune)
        for o in cap.occurrences:
            pooled.setdefault(o.instrument, []).append(o)
    return pooled


def main(argv: list[str]) -> None:
    from pipelines.commando.extract.engine_model import extract
    from pipelines.hubbard.inst_program import SID_PATH

    freq_table = extract().freq_table
    n_frames = int(argv[1]) if len(argv) > 1 else 4000

    models = decode_all(SID_PATH)
    pooled = capture_all_subtunes(SID_PATH, n_frames)
    for m in models:
        verify_instrument(m, pooled.get(m.inst, []), freq_table)

    if argv and argv[0] != 'all':
        idx = int(argv[0])
        m = models[idx]
        print(f'instrument {idx}')
        print(f'  init : ctrl=${m.init_ctrl:02X} pw=${m.init_pw_hi:02X}'
              f'{m.init_pw_lo:02X} ad=${m.init_ad:02X} sr=${m.init_sr:02X}')
        print(f'  HR   : ctrl=${m.hr_ctrl:02X} ad=$00 sr=$00 '
              f'({HR_FRAMES} frames before note end)')
        print(f'  fx   : ${m.fx_flags:02X}  {m.summary()}')
        print(f'  verify: {m.verified}  {m.verify_note}')
        return

    print(f'{"inst":>4}  {"ctrl":>4}  {"fx":>3}  {"verified":>8}  '
          f'features / verify detail')
    for m in models:
        v = {True: 'PASS', False: 'FAIL', None: '-'}[m.verified]
        print(f'{m.inst:>4}  ${m.init_ctrl:02X}  ${m.fx_flags:02X}  '
              f'{v:>8}  {m.summary()}')
        print(f'{"":>26}{m.verify_note}')


if __name__ == '__main__':
    main(sys.argv[1:])
