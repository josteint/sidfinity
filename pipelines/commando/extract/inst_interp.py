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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from pipelines.commando.extract.inst_generalize import (  # noqa: E402
    HR_FRAMES, InstrumentModel, R_AD, R_CTRL, R_FREQ_HI, R_FREQ_LO,
    R_PW_HI, R_PW_LO, R_SR, decode_all)

# Per-subtune speed (resetspd) table. resetspd = $5514 + subtune; the
# tick period is resetspd+1 frames, and the skydive's note-start hold
# is exactly resetspd frames (the non-tick frames before the first
# post-note-load tick).
SPEED_TABLE = 0x5514


def subtune_resetspd(subtune: int, binary: bytes, load_addr: int) -> int:
    return binary[SPEED_TABLE + subtune - load_addr]


def render_note(model: InstrumentModel, pitch: int, n_frames: int,
                freq_table: list[int], frame_ctr0: int = 0,
                skydive_hold: int = 2) -> list[list[tuple[int, int]]]:
    """Render the per-frame (reg, val) writes for one note of `model`.

    Handles freqSlide (skydive) and arpeggio. Vibrato / PWM raise
    NotImplementedError so a caller cannot silently get a wrong answer.

    `frame_ctr0` is the engine's global frame counter at note start —
    the arpeggio alternates pitch / pitch+interval on its parity.
    `skydive_hold` is the subtune's resetspd (see subtune_resetspd)."""
    if model.vibrato or model.pwm or model.inc_by2:
        raise NotImplementedError(
            f'inst {model.inst}: interp does not yet handle '
            f'{model.summary()}')

    base = freq_table[pitch]
    base_lo, base_hi = base & 0xFF, (base >> 8) & 0xFF

    frames: list[list[tuple[int, int]]] = []
    # frame 0 — note-start init block, in the engine's write order
    # (freq_hi, freq_lo, then ctrl, pw_lo, pw_hi, ad, sr).
    frames.append([
        (R_FREQ_HI, base_hi), (R_FREQ_LO, base_lo),
        (R_CTRL, model.init_ctrl),
        (R_PW_LO, model.init_pw_lo), (R_PW_HI, model.init_pw_hi),
        (R_AD, model.init_ad), (R_SR, model.init_sr),
    ])

    # The HR (gate-off) block fires when `duration` hits 0, which is one
    # tick — resetspd+1 frames — before the note segment ends.
    hr_frame = n_frames - (skydive_hold + 1)
    slide_v = base_hi
    slide_dead = False

    for k in range(1, n_frames):
        w: list[tuple[int, int]] = []

        # hard-restart block fires before the per-frame effects
        if k == hr_frame:
            w += [(R_CTRL, model.hr_ctrl), (R_AD, 0), (R_SR, 0)]

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
                               o.frame_ctr0, resetspd[o.subtune])
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
                       resetspd[o.subtune])
    from pipelines.commando.extract.inst_program import REG_NAMES
    for k in range(o.n_frames):
        if pred[k] != o.writes[k]:
            def fmt(fw):
                return ' '.join(f'{REG_NAMES[r]}={v:02X}' for r, v in fw) or '-'
            return (f'    +{k}: capture[{fmt(o.writes[k])}] '
                    f'!= render[{fmt(pred[k])}]')
    return '    (no diff)'


def main(argv: list[str]) -> None:
    from pipelines.commando.extract.engine_model import extract
    from pipelines.commando.extract.inst_program import SID_PATH
    from pipelines.commando.extract.inst_generalize import capture_all_subtunes
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
