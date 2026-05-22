"""song_interp.py — Phase 3.3: whole-song USF2 reference interpreter.

The per-note interpreter (inst_interp.py) cannot reproduce instruments
whose state is shared with concurrently-playing voices — Commando's PWM
accumulators live in the instrument table and are shared by every voice
using that instrument; inst 7's arpeggio reads other voices' state.

This interpreter steps the WHOLE song: `init` once, then `play` once per
frame, stepping all three voices together with the shared instrument
state evolving. It is the reference operational semantics Phase 4's Lean
`Codegen2` will implement.

Inputs are the USF-level representation: the decoded `Score` (the music)
and the `InstrumentModel`s (the instruments). Output is the per-frame
SID register-write stream, verified against the py65 capture of the
real binary.

Build status: melodic instruments, all effects (skydive, arpeggio,
vibrato, linear + bidirectional PWM) with shared per-instrument PWM
accumulators. Not yet: the drum engine, and inst 7's off-table arp
(both deferred — they need cross-voice/Phase-5 handling).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.inst_generalize import (  # noqa: E402
    R_AD, R_CTRL, R_FREQ_HI, R_FREQ_LO, R_PW_HI, R_PW_LO, R_SR,
    InstrumentModel, decode_all)
from pipelines.hubbard.inst_interp import _vibrato  # noqa: E402


@dataclass
class VoiceRT:
    """Per-voice runtime state."""
    orderlist_pos: int = 0
    note_pos: int = 0                # index into the current pattern
    duration_ctr: int = 0            # ticks left for the current note ($54F2)
    dur_field: int = 0               # current note's raw duration field
    instr: int = 0                   # current instrument (0..12)
    pitch: int = 0
    tie: bool = False
    frame_in_note: int = -1          # frames since the note loaded (0 = load)
    tick_in_note: int = 0            # decrementing ticks since the note loaded
    slide_v: int = 0                 # skydive's running freq_hi ($551A)
    slide_lo: int = 0                # the running freq_lo ($551D) — the
                                     # drum-slide's low byte (paired w/ slide_v)
    drum_trig: int = 0               # the note's drum/porta trigger byte
                                     # ($5520,X) — bits 1-6 delta, bit0 dir
    slide_dead: bool = False
    started: bool = False            # a note has been loaded at least once
    hub_note_idx: int = 0            # Hubbard's byte offset into the pattern
                                     # ($54EF,X) — read by off-table arps
    seq_idx: int = 0                 # the engine's $54EC,X — orderlist
                                     # position, pre-incremented on the
                                     # last note of a pattern
    ctrl_byte: int = 0               # the instrument ctrl saved at note start
                                     # ($54F8,X) — read by off-table note-starts
    no_release: bool = False         # note_byte bit5 — suppresses the HR
    ended: bool = False              # the voice hit the $FE end marker —
                                     # it no longer reads notes or runs


class SongInterp:
    """Whole-song interpreter for one Commando subtune."""

    def __init__(self, sid_path: str, subtune: int = 0):
        from pipelines.commando.extract.engine_model import extract
        from pipelines.hubbard.inst_interp import subtune_resetspd
        from src.hubbard_emu import load_sid

        song = extract(subtune=subtune)
        self.freq_table = song.freq_table
        self.score = song.score
        self.models: list[InstrumentModel] = decode_all(sid_path)

        _, binary, load = load_sid(sid_path)
        self.resetspd = subtune_resetspd(subtune, binary, load)

        # per-instrument PWM accumulator (the shared instrument-table pw
        # bytes) — seeded from each instrument's table values.
        self.pw_acc: dict[int, list[int]] = {
            m.inst: [m.init_pw_lo, m.init_pw_hi] for m in self.models}
        # per-voice PWM direction / period counter (these ARE per-voice)
        self.pw_dir = [0, 0, 0]
        self.pw_period = [0, 0, 0]

        self.voices = [VoiceRT(), VoiceRT(), VoiceRT()]
        self.frame_ctr = -1              # INC'd to 0 on the first frame
        self.speed_ctr = 0
        self.frame_no = -1
        # end-of-song: 0 running, 1 = all voices ended (gate-off pending),
        # 2 = gated off, silent.
        self.end_phase = 0
        # when False, per-frame effects are skipped — leaves just the
        # note-start + HR backbone. The per-effect flags let a codegen
        # stage be verified against exactly the effects it implements.
        self.effects_on = True
        self.fx_vibrato = True
        self.fx_pwm = True
        self.fx_drum_slide = True
        self.fx_skydive = True
        self.fx_arp = True
        # the off-table (cross-voice) arpeggio — inst 7's reads past the
        # freq table — can be toggled off separately from the in-table arp.
        self.fx_arp_offtable = True

    # ------------------------------------------------------------------
    # note advancement
    # ------------------------------------------------------------------

    def _load_next_note(self, v: int) -> None:
        """Advance voice `v` to its next note in the Score."""
        rt = self.voices[v]
        voice = self.score.voices[v]
        if not voice.orderlist:
            return
        if rt.started:
            rt.note_pos += 1
        rt.started = True

        # walk past exhausted patterns / wrap at the loop point
        for _ in range(len(voice.orderlist) + 2):
            pat_idx = voice.orderlist[rt.orderlist_pos]
            notes = voice.patterns.get(pat_idx, [])
            if rt.note_pos < len(notes):
                break
            rt.note_pos = 0
            rt.orderlist_pos += 1
            if rt.orderlist_pos >= len(voice.orderlist):
                if voice.stop:
                    rt.ended = True       # $FE — end of song, no loop
                    return
                rt.orderlist_pos = voice.loop if voice.loop >= 0 else 0

        pat_idx = voice.orderlist[rt.orderlist_pos]
        notes = voice.patterns.get(pat_idx, [])
        note = notes[rt.note_pos]

        # Track Hubbard's note_idx — the byte offset into the pattern.
        # Each note consumes 1 byte (tie), 2 (no instrument byte) or 3
        # (with instrument byte); note_idx points past the current note,
        # and resets to 0 at the pattern's $FF end marker.
        # Hubbard's note is 1 byte (tie), 2 (no extra byte), or 3 (an
        # extra byte — present when the note changes instrument OR
        # carries a portamento). note_idx advances by this much.
        has_porta = (note.drum_trig & 0x7F) != 0
        has_b1 = (not (note.instrument & 0x80)) or has_porta
        nbytes = 1 if note.tie else (3 if has_b1 else 2)
        base = 0 if rt.note_pos == 0 else rt.hub_note_idx
        is_last = rt.note_pos == len(notes) - 1
        rt.hub_note_idx = 0 if is_last else base + nbytes
        # seq_idx mirrors the engine's $54EC,X. The engine pre-increments
        # it when the LAST note of a pattern loads (it peeks the $FF end
        # marker and bumps seq_idx + resets note_idx then). orderlist_pos
        # itself does not advance until the next load, so track seq_idx
        # separately — the off-table arp reads it.
        if is_last:
            nxt = rt.orderlist_pos + 1
            if nxt >= len(voice.orderlist):
                nxt = voice.loop if voice.loop >= 0 else 0
            rt.seq_idx = nxt
        else:
            rt.seq_idx = rt.orderlist_pos

        rt.dur_field = note.duration - 1          # Score stores ticks = field+1
        rt.duration_ctr = rt.dur_field
        # The instrument carries across notes AND patterns: a note with
        # no instrument byte (bit7 of the stored value) keeps the live
        # value. engine_model resets its per-pattern decode to 0, which
        # is wrong for a pattern whose first note omits the byte — so
        # carry it here at the orderlist level instead.
        if not (note.instrument & 0x80):
            rt.instr = note.instrument & 0x3F
        # a tie note carries the live pitch — it does NOT re-pitch. The
        # decoder defaults a tie's pitch to the previous note in the same
        # pattern (0 for a tie that is a pattern's first note), so only a
        # non-tie note may set rt.pitch — a tie keeps whatever is playing,
        # which carries the pitch correctly across pattern boundaries.
        if not note.tie:
            rt.pitch = note.pitch
        rt.tie = note.tie
        # no_release (note_byte bit5) suppresses the hard restart;
        # engine_model stores it in drum_trig bit7.
        rt.no_release = bool(note.drum_trig & 0x80)
        # the drum/porta trigger byte ($5520,X) — reset every note load,
        # set from the note. bit7 is no_release (handled above); the
        # drum slide keys off the payload (bits 0-6) only.
        rt.drum_trig = note.drum_trig
        rt.frame_in_note = 0
        rt.tick_in_note = 0
        # the running freq_hi/freq_lo ($551A/$551D) are only re-seeded on
        # a non-tie note (the engine skips the freq write entirely for a
        # tie, so the slide values carry over from the previous note).
        # They feed both the skydive and the drum slide.
        if not note.tie:
            if note.pitch >= 96:
                rt.slide_v = self._read_state(0x5429 + note.pitch * 2, v)
                rt.slide_lo = self._read_state(0x5428 + note.pitch * 2, v)
            else:
                f = self.freq_table[note.pitch]
                rt.slide_v = (f >> 8) & 0xFF
                rt.slide_lo = f & 0xFF
        rt.slide_dead = False

    # ------------------------------------------------------------------
    # per-frame stepping
    # ------------------------------------------------------------------

    def step(self) -> list[tuple[int, int]]:
        """Run one play() call. Returns this frame's (reg 0..20, val) writes."""
        self.frame_no += 1
        self.frame_ctr = 0 if self.frame_no == 0 else (self.frame_ctr + 1) & 0xFF

        # end-of-song: the frame after every voice hits $FE, the engine
        # gates all three voices off once (ctrl=0, in V1..V3 order); then
        # it produces nothing.
        if self.end_phase == 1:
            self.end_phase = 2
            return [(0 * 7 + R_CTRL, 0), (1 * 7 + R_CTRL, 0),
                    (2 * 7 + R_CTRL, 0)]
        if self.end_phase == 2:
            return []

        # speed counter: a tick fires when it reloads
        self.speed_ctr -= 1
        if self.speed_ctr < 0:
            self.speed_ctr = self.resetspd
        is_tick = (self.speed_ctr == self.resetspd)

        writes: list[tuple[int, int]] = []
        for v in (2, 1, 0):                       # engine processes V3,V2,V1
            writes += [(v * 7 + r, val)
                       for r, val in self._process_voice(v, is_tick)]
        if self.end_phase == 0 and all(rt.ended for rt in self.voices):
            self.end_phase = 1
        return writes

    def _process_voice(self, v: int, is_tick: bool) -> list[tuple[int, int]]:
        rt = self.voices[v]
        if rt.ended:
            return []
        if is_tick:
            rt.duration_ctr -= 1
            if rt.duration_ctr < 0:
                self._load_next_note(v)
                if rt.ended:
                    return []
                return self._note_start_writes(v)      # no effects on load
            rt.tick_in_note += 1
        rt.frame_in_note += 1

        w: list[tuple[int, int]] = []
        # hard restart: the gate-off block, on the tick `duration` hits 0
        # (suppressed by no_release, NOT by tie)
        if is_tick and rt.duration_ctr == 0 and not rt.no_release:
            m = self.models[rt.instr]
            w += [(R_CTRL, m.hr_ctrl), (R_AD, 0), (R_SR, 0)]
        if self.effects_on:
            w += self._effects(v)
        return w

    def _note_start_writes(self, v: int) -> list[tuple[int, int]]:
        rt = self.voices[v]
        m = self.models[rt.instr]
        if rt.tie:
            # tie: the engine skips only the freq write — it still does
            # the instrument write (ctrl gated off, pw, ad, sr).
            rt.ctrl_byte = m.init_ctrl
            pw = self.pw_acc[rt.instr]
            return [(R_CTRL, m.init_ctrl & 0xFE),
                    (R_PW_LO, pw[0]), (R_PW_HI, pw[1]),
                    (R_AD, m.init_ad), (R_SR, m.init_sr)]
        # freq: an off-table pitch (>=96, e.g. inst 4 at 104) reads
        # player state — the freq read happens BEFORE ctrl_byte is
        # updated below, matching the engine's ordering.
        if rt.pitch >= 96:
            flo = self._read_state(0x5428 + rt.pitch * 2, v)
            fhi = self._read_state(0x5429 + rt.pitch * 2, v)
        else:
            f = self.freq_table[rt.pitch]
            flo, fhi = f & 0xFF, (f >> 8) & 0xFF
        pw = self.pw_acc[rt.instr]
        w = [
            (R_FREQ_HI, fhi), (R_FREQ_LO, flo),
            (R_CTRL, m.init_ctrl),
            (R_PW_LO, pw[0]), (R_PW_HI, pw[1]),
            (R_AD, m.init_ad), (R_SR, m.init_sr),
        ]
        rt.ctrl_byte = m.init_ctrl
        return w

    # ------------------------------------------------------------------
    # effects — engine order: vibrato, PWM, drum-slide, skydive, arpeggio
    # ------------------------------------------------------------------

    def _effects(self, v: int) -> list[tuple[int, int]]:
        rt = self.voices[v]
        m = self.models[rt.instr]
        w: list[tuple[int, int]] = []

        vib_carry = 0
        if m.vibrato and self.fx_vibrato:
            vw, vib_carry = _vibrato(m.vibrato.depth,
                                     self._freq16(rt.pitch, v),
                                     self._freq16(rt.pitch + 1, v),
                                     self.frame_ctr, rt.dur_field)
            w += vw

        if m.pwm and self.fx_pwm:
            w += self._pwm(v, m, vib_carry)

        if self.fx_drum_slide:
            w += self._drum_slide(v)

        if m.freq_slide and self.fx_skydive:
            w += self._skydive(v, m)

        if m.inc_by2 and self.fx_skydive:
            w += self._inc_by2(v)

        if m.arpeggio and self.fx_arp:
            w += self._arp(v, m)

        return w

    def _inc_by2(self, v: int) -> list[tuple[int, int]]:
        """fx bit1 — on odd frames (dur field >= 3, slide value != 0)
        write the old slide value and bump it by 2 (disassembly
        $5336-$535D). Runs after the skydive, sharing slide_v."""
        rt = self.voices[v]
        if rt.dur_field < 3 or not (self.frame_ctr & 1) or rt.slide_v == 0:
            return []
        old = rt.slide_v
        rt.slide_v = (rt.slide_v + 2) & 0xFF
        return [(R_FREQ_HI, old)]

    def _pwm(self, v: int, m: InstrumentModel,
             vib_carry: int) -> list[tuple[int, int]]:
        pw = self.pw_acc[m.inst]
        if m.pwm.mode == 'linear':
            pw[0] = (pw[0] + m.pwm.speed + vib_carry) & 0xFF
            return [(R_PW_LO, pw[0])]
        # bidirectional: per-voice period counter; step on underflow
        self.pw_period[v] -= 1
        if self.pw_period[v] >= 0:
            return []
        self.pw_period[v] = m.pwm.period
        if self.pw_dir[v] == 0:                       # rising
            acc = pw[0] + m.pwm.step
            pw[0] = acc & 0xFF
            pw[1] = (pw[1] + (acc >> 8)) & 0x0F
            if pw[1] == m.pwm.hi_bound:
                self.pw_dir[v] = 1
        else:                                          # falling
            acc = pw[0] - m.pwm.step
            pw[0] = acc & 0xFF
            pw[1] = (pw[1] - (1 if acc < 0 else 0)) & 0x0F
            if pw[1] == m.pwm.lo_bound:
                self.pw_dir[v] = 0
        return [(R_PW_HI, pw[1]), (R_PW_LO, pw[0])]

    def _drum_slide(self, v: int) -> list[tuple[int, int]]:
        """Per-note portamento ($52B3-$52F9) — effect #3, after PWM and
        before the skydive. If the note carries a drum/porta trigger,
        slide the running freq ($551D/$551A) by `delta` each frame.

        The trigger byte's bit7 is no_release (engine_model packs it
        there); the real engine keys this effect off a marker byte whose
        bits 0-6 are the porta payload, so mask bit7 off before testing."""
        rt = self.voices[v]
        dt = rt.drum_trig & 0x7F
        if dt == 0:
            return []
        delta = dt & 0x7E                      # $52BB: AND #$7E
        if dt & 0x01:                          # $52C3: AND #$01 — slide down
            lo = rt.slide_lo - delta
            rt.slide_lo = lo & 0xFF
            rt.slide_v = (rt.slide_v - (1 if lo < 0 else 0)) & 0xFF
        else:                                  # slide up
            lo = rt.slide_lo + delta
            rt.slide_lo = lo & 0xFF
            rt.slide_v = (rt.slide_v + (1 if lo > 0xFF else 0)) & 0xFF
        return [(R_FREQ_LO, rt.slide_lo), (R_FREQ_HI, rt.slide_v)]

    def _skydive(self, v: int, m: InstrumentModel) -> list[tuple[int, int]]:
        rt = self.voices[v]
        if rt.slide_dead or rt.duration_ctr == 0:
            return []
        if rt.slide_v == 0:
            rt.slide_dead = True
            return []
        w = [(R_FREQ_HI, rt.slide_v)]
        if rt.tick_in_note == 0:
            w.append((R_CTRL, 0x80))
        else:
            masked = m.init_ctrl & 0xFE
            w.append((R_CTRL, masked if masked != 0 else 0x80))
            rt.slide_v = (rt.slide_v - 1) & 0xFF
        return w

    def _arp(self, v: int, m: InstrumentModel) -> list[tuple[int, int]]:
        rt = self.voices[v]
        parity = self.frame_ctr & 1
        idx = rt.pitch + m.arpeggio.intervals[parity]
        if idx < 96:
            af = self.freq_table[idx]
            return [(R_FREQ_HI, (af >> 8) & 0xFF), (R_FREQ_LO, af & 0xFF)]
        if not self.fx_arp_offtable:
            return []
        # Off the 96-entry freq table: the lookup reads player-state
        # bytes. Hubbard's space-saving trick — see the disassembly /
        # feedback_deconstruct_not_reproduce. Reproduced cleanly here by
        # reading the corresponding engine state directly.
        addr = 0x5428 + idx * 2
        return [(R_FREQ_HI, self._read_state(addr + 1, v)),
                (R_FREQ_LO, self._read_state(addr, v))]

    def _freq16(self, pitch: int, v: int) -> int:
        """The 16-bit freq for `pitch`. In-table pitches (<96) come from
        the freq table; an off-table pitch reads engine state (the same
        $5428-overflow the off-table arp/note-start use) — needed for
        the vibrato of an instrument played past the 96 musical notes."""
        if pitch < 96:
            return self.freq_table[pitch]
        addr = 0x5428 + pitch * 2
        return self._read_state(addr, v) | (self._read_state(addr + 1, v) << 8)

    def _read_state(self, addr: int, v: int) -> int:
        """The player-state byte at `addr` — what an off-table lookup
        (an arp with idx>=96, or a pitch-104 note-start) lands on past
        the 96-entry freq table. `v` is the voice whose effect is
        running — needed for the $54EB scratch, which holds the
        currently-processing voice's SID offset."""
        if 0x54E8 <= addr <= 0x54EA:            # v_sid_off[0..2]
            return (0, 7, 14)[addr - 0x54E8]
        if addr == 0x54EB:                      # scratch = current voice sid_off
            return (0, 7, 14)[v]
        if 0x54EC <= addr <= 0x54EE:            # seq_idx[0..2]
            return self.voices[addr - 0x54EC].seq_idx & 0xFF
        if 0x54EF <= addr <= 0x54F1:            # note_idx[0..2]
            return self.voices[addr - 0x54EF].hub_note_idx & 0xFF
        if 0x54F2 <= addr <= 0x54F4:            # duration[0..2]
            return self.voices[addr - 0x54F2].duration_ctr & 0xFF
        if 0x54F5 <= addr <= 0x54F7:            # note_byte[0..2]
            rv = self.voices[addr - 0x54F5]
            return (rv.dur_field | (0x40 if rv.tie else 0)) & 0xFF
        if 0x54F8 <= addr <= 0x54FA:            # ctrl_byte[0..2]
            return self.voices[addr - 0x54F8].ctrl_byte & 0xFF
        if 0x54FB <= addr <= 0x54FD:            # pitch[0..2]
            return self.voices[addr - 0x54FB].pitch & 0xFF
        if 0x54FE <= addr <= 0x5500:            # instr_num[0..2]
            return self.voices[addr - 0x54FE].instr & 0xFF
        if 0x5510 <= addr <= 0x5512:            # pw_dir[0..2]
            return self.pw_dir[addr - 0x5510] & 0xFF
        return 0


# ----------------------------------------------------------------------
# verification
# ----------------------------------------------------------------------

def verify(sid_path: str, subtune: int, n_frames: int) -> dict:
    """Run the interpreter and the py65 capture; diff per frame.

    Also tallies, per failing frame, which voices carry the diff — so a
    failure confined to a voice playing the drum or inst 7's off-table
    arp (both deferred) can be told apart from a real interpreter bug."""
    from pipelines.hubbard.inst_program import capture

    cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
    si = SongInterp(sid_path, subtune)

    match = 0
    first_fail = None
    by_voices: dict[tuple, int] = {}
    for k in range(n_frames):
        got = si.step()
        want = cap.raw_frames[k]
        if got == want:
            match += 1
            continue
        if first_fail is None:
            first_fail = (k, want, got)
        diff = set(want) ^ set(got)
        vs = tuple(sorted({['V1', 'V2', 'V3'][o // 7] for o, _ in diff}))
        by_voices[vs] = by_voices.get(vs, 0) + 1
    return {'frames': n_frames, 'match': match,
            'pct': 100.0 * match / n_frames, 'first_fail': first_fail,
            'by_voices': by_voices}


def main(argv: list[str]) -> None:
    from pipelines.hubbard.inst_program import SID_PATH, REG_NAMES

    subtune = int(argv[0]) if argv else 0
    n_frames = int(argv[1]) if len(argv) > 1 else 1500
    res = verify(SID_PATH, subtune, n_frames)
    print(f'subtune {subtune}: {res["match"]}/{res["frames"]} frames '
          f'exact ({res["pct"]:.1f}%)')
    if res['by_voices']:
        print('  failing frames by voice(s) carrying the diff:')
        for vs, c in sorted(res['by_voices'].items(),
                            key=lambda x: -x[1]):
            print(f'    {",".join(vs)}: {c}')
    if res['first_fail']:
        k, want, got = res['first_fail']

        def fmt(fw):
            return ' '.join(
                f'{["V1","V2","V3"][o // 7]}.{REG_NAMES[o % 7]}={v:02X}'
                for o, v in fw) or '-'
        print(f'  first diff at frame {k}:')
        print(f'    capture: {fmt(want)}')
        print(f'    interp : {fmt(got)}')


if __name__ == '__main__':
    main(sys.argv[1:])
