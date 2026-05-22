"""inst_interp.py — Phase 3.3: a reference interpreter for the USF2
instrument model.

This is the operational semantics the USF2 schema lacked. It takes an
`InstrumentModel` (3.2's decode) plus a note (pitch, length) and renders
the exact per-frame SID register writes the instrument performs. Phase
4's Lean `Codegen2` will implement the same semantics in 6502.

The interpreter is verified by rendering every py65-captured note
occurrence and diffing against the real capture: `render == capture`.

Build status: const init block + HR block + freqSlide (skydive). Other
effects (arpeggio, vibrato, PWM) are added incrementally as each is
pinned down against the captures.

Skydive semantics (fitted from captures, engine `_apply_arpeggio_skydive`):
the effect runs every frame after note start. For the first
`skydive_hold` frames it writes freq_hi unchanged and ctrl = $80
(the "note-start sub-phase"); thereafter it writes the current freq_hi,
writes ctrl = init_ctrl & $FE, then decrements freq_hi. When freq_hi
reaches 0 the whole effect stops (no freq_hi AND no ctrl write) — the
freq slide and the ctrl pattern share one lifetime.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from pipelines.hubbard.inst_generalize import (  # noqa: E402
    HR_FRAMES, InstrumentModel, R_AD, R_CTRL, R_FREQ_HI, R_FREQ_LO,
    R_PW_HI, R_PW_LO, R_SR, decode_all)

# Per-subtune speed (resetspd) table. resetspd = $5514 + subtune; the
# tick period is resetspd+1 frames, and the skydive's note-start hold
# is exactly resetspd frames (the non-tick frames before the first
# post-note-load tick).
SPEED_TABLE = 0x5514


def subtune_resetspd(subtune: int, binary: bytes, load_addr: int) -> int:
    return binary[SPEED_TABLE + subtune - load_addr]


def _vibrato(depth: int, f_cur: int, f_next: int, frame_ctr: int,
             dur_field: int) -> tuple[list[tuple[int, int]], int]:
    """Vibrato — authoritative semantics from the disassembly $51C1-$522D.
    Returns (writes, carry_out).

    A triangle LFO over 8 frames (step 0,1,2,3,3,2,1,0) scales a delta of
    `(f_next - f_cur) >> (depth+1)`, added `step` times to the base freq
    (16-bit). `f_cur`/`f_next` are the 16-bit freq for the note's pitch
    and pitch+1 — the caller resolves these (an off-table pitch reads
    engine state, not the freq table). Gated off when the note's dur
    field < 6 (then it just rewrites the base freq). Writes freq_lo,
    freq_hi.

    carry_out is the 6502 carry the vibrato section leaves in the C flag
    for the linear-PWM `ADC` that immediately follows it — the engine
    omits a CLC there, so the PWM step inherits this carry. Determined
    by the disassembly: when the add loop is skipped the carry is the
    result of `CMP #$06` (0 if dur<6, 1 if dur>=6 with step 0); when the
    loop runs it is the carry-out of the last hi-byte ADC."""
    step = frame_ctr & 0x07
    if step >= 4:
        step ^= 0x07
    delta = ((f_next - f_cur) & 0xFFFF) >> (depth + 1)
    delta_lo = delta & 0xFF
    delta_hi = (delta >> 8) & 0xFF
    target_lo = f_cur & 0xFF
    target_hi = (f_cur >> 8) & 0xFF
    if dur_field < 6:
        carry = 0
    elif step == 0:
        carry = 1
    else:
        carry = 0
        for _ in range(step):
            lo = target_lo + delta_lo                  # CLC; ADC delta_lo
            target_lo = lo & 0xFF
            hi = target_hi + delta_hi + (lo >> 8)      # ADC delta_hi
            target_hi = hi & 0xFF
            carry = hi >> 8
    return [(R_FREQ_LO, target_lo), (R_FREQ_HI, target_hi)], carry


def render_note(model: InstrumentModel, pitch: int, n_frames: int,
                freq_table: list[int], frame_ctr0: int = 0,
                skydive_hold: int = 2,
                pw_seed: tuple[int, int] | None = None
                ) -> list[list[tuple[int, int]]]:
    """Render the per-frame (reg, val) writes for one note of `model`.

    Handles freqSlide (skydive), arpeggio, vibrato and linear PWM.
    Bidirectional PWM and inc_by2 raise NotImplementedError.

    `frame_ctr0` is the engine's global frame counter at note start
    (vibrato + arpeggio phase). `skydive_hold` is the subtune's resetspd.
    `pw_seed` is the (pw_lo, pw_hi) accumulator value at note start —
    PWM bytes are free-running engine state, so for a PWM instrument the
    note-start frame writes this seed rather than a constant."""
    if (model.pwm and model.pwm.mode == 'bidirectional') or model.inc_by2:
        raise NotImplementedError(
            f'inst {model.inst}: interp does not yet handle '
            f'{model.summary()}')

    base = freq_table[pitch]
    base_lo, base_hi = base & 0xFF, (base >> 8) & 0xFF

    # The HR (gate-off) block fires when `duration` hits 0, which is one
    # tick — resetspd+1 frames — before the note segment ends.
    tempo = skydive_hold + 1
    hr_frame = n_frames - tempo
    dur_field = n_frames // tempo - 1        # ticks the note lasts, minus 1

    # PWM bytes are accumulator state: a PWM instrument's note-start
    # frame writes the live accumulator, seeded here from pw_seed.
    if model.pwm and pw_seed is not None:
        pw_lo = pw_seed[0]
    else:
        pw_lo = model.init_pw_lo
    pw_hi = model.init_pw_hi

    frames: list[list[tuple[int, int]]] = []
    # frame 0 — note-start init block, in the engine's write order
    # (freq_hi, freq_lo, then ctrl, pw_lo, pw_hi, ad, sr).
    frames.append([
        (R_FREQ_HI, base_hi), (R_FREQ_LO, base_lo),
        (R_CTRL, model.init_ctrl),
        (R_PW_LO, pw_lo), (R_PW_HI, pw_hi),
        (R_AD, model.init_ad), (R_SR, model.init_sr),
    ])

    slide_v = base_hi
    slide_dead = False

    for k in range(1, n_frames):
        w: list[tuple[int, int]] = []

        # hard-restart block fires before the per-frame effects
        if k == hr_frame:
            w += [(R_CTRL, model.hr_ctrl), (R_AD, 0), (R_SR, 0)]

        # vibrato runs first in the engine's effect order
        vib_carry = 0
        if model.vibrato:
            vw, vib_carry = _vibrato(model.vibrato.depth,
                                     freq_table[pitch], freq_table[pitch + 1],
                                     frame_ctr0 + k, dur_field)
            w += vw

        # linear PWM — pw_lo accumulates by `speed` every effect frame.
        # The engine's `ADC` has no preceding CLC, so it also adds the
        # carry the vibrato section left behind.
        if model.pwm and model.pwm.mode == 'linear':
            pw_lo = (pw_lo + model.pwm.speed + vib_carry) & 0xFF
            w.append((R_PW_LO, pw_lo))

        # skydive effect — the engine guards it on `duration != 0`, and
        # `duration` reaches 0 exactly at the HR frame and stays there,
        # so the skydive never runs at or after the HR frame.
        if model.freq_slide and not slide_dead and k < hr_frame:
            if slide_v == 0:
                slide_dead = True
            else:
                w.append((R_FREQ_HI, slide_v))
                if k <= skydive_hold:
                    w.append((R_CTRL, 0x80))
                else:
                    masked = model.init_ctrl & 0xFE
                    w.append((R_CTRL, masked if masked != 0 else 0x80))
                    slide_v = (slide_v - 1) & 0xFF

        # arpeggio effect — runs after the skydive in the engine's effect
        # order, every frame (it has no `duration` guard, so unlike the
        # skydive it keeps running at and after the HR frame). It rewrites
        # freq from the table at pitch + interval[global frame parity].
        if model.arpeggio:
            parity = (frame_ctr0 + k) & 1
            arp_pitch = pitch + model.arpeggio.intervals[parity]
            af = freq_table[arp_pitch]
            w.append((R_FREQ_HI, (af >> 8) & 0xFF))
            w.append((R_FREQ_LO, af & 0xFF))

        frames.append(w)

    return frames


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _pw_seed(o) -> tuple[int, int]:
    """The (pw_lo, pw_hi) values the engine wrote on the note-start frame
    — the live PWM accumulator at note start."""
    d = {r: v for r, v in o.writes[0]}
    return (d.get(R_PW_LO, 0), d.get(R_PW_HI, 0))


def verify(model: InstrumentModel, occs, freq_table, resetspd) -> dict:
    """Render every captured occurrence and diff against the real capture.
    `resetspd` maps subtune -> resetspd (the skydive hold)."""
    exact = 0
    fails = []
    skipped = 0
    for o in occs:
        # drum-suppressed occurrences (incomplete note-start) are not the
        # instrument's own behaviour — skip them.
        if not o.writes or len(o.writes[0]) < 7:
            skipped += 1
            continue
        try:
            pred = render_note(model, o.pitch, o.n_frames, freq_table,
                               o.frame_ctr0, resetspd[o.subtune],
                               _pw_seed(o))
        except NotImplementedError:
            return {'status': 'unimplemented', 'summary': model.summary()}
        if all(pred[k] == o.writes[k] for k in range(o.n_frames)):
            exact += 1
        else:
            fails.append(o)
    return {'status': 'ok', 'exact': exact, 'fail': len(fails),
            'skipped': skipped, 'fails': fails}


def _first_diff(model, o, freq_table, resetspd) -> str:
    pred = render_note(model, o.pitch, o.n_frames, freq_table, o.frame_ctr0,
                       resetspd[o.subtune], _pw_seed(o))
    from pipelines.hubbard.inst_program import REG_NAMES
    for k in range(o.n_frames):
        if pred[k] != o.writes[k]:
            def fmt(fw):
                return ' '.join(f'{REG_NAMES[r]}={v:02X}' for r, v in fw) or '-'
            return (f'    +{k}: capture[{fmt(o.writes[k])}] '
                    f'!= render[{fmt(pred[k])}]')
    return '    (no diff)'


def main(argv: list[str]) -> None:
    from pipelines.commando.extract.engine_model import extract
    from pipelines.hubbard.inst_program import SID_PATH
    from pipelines.hubbard.inst_generalize import capture_all_subtunes
    from src.hubbard_emu import load_sid

    freq_table = extract().freq_table
    hdr, binary, load_addr = load_sid(SID_PATH)
    resetspd = [subtune_resetspd(s, binary, load_addr)
                for s in range(max(1, hdr['num_songs']))]

    models = decode_all(SID_PATH)
    pooled = capture_all_subtunes(SID_PATH, 4000)

    only = int(argv[0]) if argv else None
    print(f'{"inst":>4}  {"status":>13}  detail')
    for m in models:
        if only is not None and m.inst != only:
            continue
        occs = pooled.get(m.inst, [])
        if not occs:
            print(f'{m.inst:>4}  {"no captures":>13}')
            continue
        res = verify(m, occs, freq_table, resetspd)
        if res['status'] == 'unimplemented':
            print(f'{m.inst:>4}  {"unimplemented":>13}  {res["summary"]}')
            continue
        verdict = 'PASS' if res['fail'] == 0 else 'FAIL'
        print(f'{m.inst:>4}  {verdict:>13}  '
              f'exact={res["exact"]} fail={res["fail"]} '
              f'skipped={res["skipped"]}')
        if res['fail'] and only is not None:
            print(_first_diff(m, res['fails'][0], freq_table, resetspd))


if __name__ == '__main__':
    main(sys.argv[1:])
