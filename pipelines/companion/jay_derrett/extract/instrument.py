"""Decode jay_derrett 24-byte instrument programs into typed USF
`Instrument` shape.

Each 24-byte program is COPIED at note-start from the per-instrument
table into the voice-state region `$C92D + voice_offset*24`. The
per-frame block at `$C6DD` reads the voice state every frame and
emits SID writes. The byte-by-byte semantics (traced from
`disassembly_ninja_hamster.s`):

| ofs | role |
|---|---|
| $00 | bit-flags: bit0=slide-dir, bit1=bidir-mode, bit2=bound-mode, bit7=high-oct-arp |
| $01 | freq cur lo (init) → SID $D400 |
| $02 | freq cur hi (init) → SID $D401 |
| $03 | freq bound 1 lo DELTA (added to freq_table[note] at note-start) |
| $04 | freq bound 1 hi delta |
| $05 | freq bound 2 lo delta |
| $06 | freq bound 2 hi delta |
| $07 | freq slide step lo |
| $08 | freq slide step hi |
| $09 | (unread / padding) |
| $0A | PW hi current → SID $D403 |
| $0B | PW first-phase bound |
| $0C | PW first-phase step |
| $0D | (unread / padding) |
| $0E | PW initial direction: 0=up/ADC, non-zero=down/SBC |
| $0F | PW oscillation state (init 0) |
| $10 | PW oscillation upper bound |
| $11 | PW oscillation lower bound |
| $12 | PW oscillation step |
| $13 | (unread / padding) |
| $14 | CTRL gate-on byte → SID $D404 |
| $15 | AD (attack/decay) → SID $D405 |
| $16 | SR (sustain/release) → SID $D406 |
| $17 | CTRL alt — OR'd onto $14 every frame. Mutated by $80 (gate off) handler to produce release CTRL. Init = $14. |

Per the principled-instrument refactor (see
`docs/refactor_plan_principled_instrument.md`), these bytes
decompose into musical primitives:

  - envelope: waveform CTRL + AD + SR + release_ctrl
  - PWM: two-phase (initial sweep → bidirectional oscillation)
  - freq_slide: 3 modes (one_shot_halt | one_shot_swap | bidirectional)
    + bounds + step + high-octave arp variant

Unread padding bytes ($09, $0D, $13) are dropped — they don't affect
the SID write stream.
"""

from __future__ import annotations

from src.usf import (
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, IncBy2Config,
)


def _signed16(lo: int, hi: int) -> int:
    """Build a signed 16-bit integer from lo/hi bytes (two's complement)."""
    v = (hi << 8) | lo
    if v & 0x8000:
        v -= 0x10000
    return v


def decode_instrument(inst_id: int, prog: list[int]) -> Instrument:
    """Decode a 24-byte instrument program into a typed `Instrument`.

    `inst_id` is the 1-indexed USF instrument id (extract callers
    convert from the engine's 0-indexed byte+1 quirk).

    `prog` is the 24-byte program bytes as a list[int].

    The resulting `Instrument` is fully self-contained per the USF
    representation principle — no engine-name dispatch needed at
    rebuild time.
    """
    # Most Type A SIDs use 24-byte instrument programs (Ninja_Hamster
    # shape). Some (Counterforce = 31, others TBD) use longer layouts
    # whose extra bytes' semantics aren't yet RE'd. For first cut we
    # decode the first 24 bytes via the Ninja_Hamster mapping;
    # longer-layout extras are ignored. TODO: per-size decoders.
    if len(prog) < 24:
        # Pad short programs with zeros to allow decoding.
        prog = list(prog) + [0] * (24 - len(prog))
    else:
        prog = list(prog)[:24]

    flags    = prog[0x00]
    freq_lo  = prog[0x01]
    freq_hi  = prog[0x02]
    bnd1_lo, bnd1_hi = prog[0x03], prog[0x04]
    bnd2_lo, bnd2_hi = prog[0x05], prog[0x06]
    step_lo, step_hi = prog[0x07], prog[0x08]
    # $09 unread.
    pw_hi    = prog[0x0A]
    pw_bnd1  = prog[0x0B]
    pw_step1 = prog[0x0C]
    # $0D unread.
    pw_dir1  = prog[0x0E]
    # $0F = osc state init (always 0; not stored).
    pw_osc_upper = prog[0x10]
    pw_osc_lower = prog[0x11]
    pw_osc_step  = prog[0x12]
    # $13 unread.
    ctrl_on  = prog[0x14]
    ad       = prog[0x15]
    sr       = prog[0x16]
    ctrl_alt = prog[0x17]

    # --- Envelope ---
    # release CTRL = gate-on OR alt. The engine's $80 handler mutates
    # alt at runtime so the OR produces the desired release byte. At
    # init time, alt == gate-on, so OR is identity. The MUSICAL effect
    # at release is whatever bits ctrl_alt sets ON; we store the
    # resulting CTRL byte (ctrl_on | ctrl_alt) which is what the engine
    # writes during release for THIS instrument.
    envelope = EnvelopeConfig(release_ctrl=ctrl_on | ctrl_alt)

    # --- PWM ---
    # First-phase shape: PW hi starts at `pw_hi`, advances by
    # `pw_step1` per frame in `pw_dir1` direction, until crossing
    # `pw_bnd1`. If oscillation bounds (`$10`/`$11`) are set, the
    # second phase oscillates between them with `pw_osc_step`.
    pwm_active = (pw_bnd1 or pw_step1 or pw_osc_upper or pw_osc_lower
                  or pw_osc_step or pw_hi or pw_dir1)
    if not pwm_active:
        pwm = PwmConfig(mode='none', init=0)
    else:
        # Oscillation present → mode='bidirectional'; else 'linear'.
        if pw_osc_upper or pw_osc_lower or pw_osc_step:
            mode = 'bidirectional'
        else:
            mode = 'linear'
        pwm = PwmConfig(
            mode=mode,
            speed=pw_osc_step,
            init=pw_hi << 8,         # PW lo always zeroed by engine
            min_hi=pw_osc_lower,
            max_hi=pw_osc_upper,
            phase1_dir='down' if pw_dir1 else 'up',
            phase1_bound=pw_bnd1,
            phase1_step=pw_step1,
        )

    # --- Freq slide ---
    # Active iff slide step is non-zero (engine's per-frame block does
    # ADC/SBC `$c934,y` to the freq; if step=0, no change).
    slide_active = (step_lo or step_hi)
    if not slide_active:
        slide = FreqSlideConfig(mode='none')
    else:
        # Mode from bit-flags:
        #   bit 1 (bidir) set → bidirectional
        #   bit 1 clear, bit 2 (bound-mode) set → one_shot_swap
        #   bit 1 clear, bit 2 clear → one_shot_halt
        if flags & 0x02:
            mode = 'bidirectional'
        elif flags & 0x04:
            mode = 'one_shot_swap'
        else:
            mode = 'one_shot_halt'
        slide = FreqSlideConfig(
            mode=mode,
            initial_dir='down' if (flags & 0x01) else 'up',
            upper_delta=_signed16(bnd1_lo, bnd1_hi),
            lower_delta=_signed16(bnd2_lo, bnd2_hi),
            step=(step_hi << 8) | step_lo,
            high_oct_arp=bool(flags & 0x80),
        )

    return Instrument(
        id=inst_id,
        name=None,
        waveform=[ctrl_on],
        loop=0,
        pwm=pwm,
        adsr=(ad, sr),
        arp=ArpConfig(offsets=[0]),       # jay_derrett doesn't use classical arpeggio
        vibrato=VibratoConfig(scale=0),   # no vibrato (engine has no LFO)
        envelope=envelope,
        freq_slide_config=slide,
        inc_by2_config=IncBy2Config(),    # no inc_by2 in jay_derrett
    )
