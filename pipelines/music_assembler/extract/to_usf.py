"""Music Assembler — MasmModel -> UsfFile.

Music Assembler gets NO per-engine USF block. Its musical content maps onto
the vocabulary the other families already established; where MA differs it is
in the composer's EMISSION, not in the schema. The mapping, and why each
choice is the honest one:

PRESETS -> INSTRUMENTS. The 8-byte preset is a instrument record and decomposes
field by field: (+0,+1) -> `adsr`, +2 -> the wave program's first step, +3/+4
-> `pwm.init`/`pwm.speed`, +5/+6 -> `vibrato` onset/speed/amplitude. The +7 Fx
byte is NOT carried: its three effect-enable bits are already implied by the
configs they gate (`pwm.mode` carries $40/$20; a zero vibrato `amplitude`
carries $10), and its low nibble selects an arpeggio that is inlined per
instrument. An enable bit that duplicates its own config would be a second
encoding of one fact.

ARPEGGIOS -> THE INSTRUMENT'S WAVE PROGRAM. An MA arpeggio step is
(waveform, pitch, filter cutoff) — that is a wave program, not a semitone
cycle, so it clusters with `waveform`/`wave_freq` rather than `ArpConfig`
(the principle's Rule 1: cluster by behaviour). The preset's own ctrl byte is
the program's step 0, because that is exactly how the engine plays it: the
note-init frame writes preset+2 and every frame after that writes the next
arpeggio step. So:

    waveform = [preset+2, step0.wave, step1.wave, ...]
    loop     = 1                       when the arpeggio loops ($FF)
             = len(waveform)           when it stops   ($FE)
             = 0                       when there is no arpeggio (1 step)

`loop == len` means "run once and hold the last step", which is what $FE does
— and it is also what re-enables vibrato, since the engine's stop clears the
arp nibble. The two extra parallel per-step lists (`wave_abs`, `wave_filter`)
carry the step's absolute/relative pitch mode and its filter cutoff.

SEQUENCES -> PATTERNS OF NOTE ROWS, per ledger C14 (command-per-row effects
become parametric `fx_flags` strings, never a schema field):

    note                -> pitch + duration
    rest                -> `---` + duration
    hold                -> `---` + duration + `tie`
    preset select       -> the FOLLOWING row's `instr` (stated notation, C32:
                           present = the stream states it, absent = inherit)
    flags bit 6 legato  -> `noretrig`   (play without retriggering)
    flags bit 5 slide   -> `glide_up=` / `glide_down=` (signed 16-bit rate)
    flags bit 7 filter  -> `filter_sweep=<cutoff>,<frames>`

ORDERLISTS -> `Orderlist`, which already has exactly MA's three per-entry
modifiers: pattern id, `transposes` (the entry byte's high nibble) and
`repeats` (its low nibble + 1, since the engine plays repeat+1 times).
`$FE` -> stop, `$FF` -> loop to 0, `$FD nn` -> loop to entry nn. The `$FD`
PLAYER VARIANT needs no USF flag: the composer emits its own orderlist
advance, so a non-zero `loop_to` is simply honoured.

INIT. Per the trichotomy: `$D418=$1F` / `$D417=$F0` are chip PRIMING
(`init.sid`); the per-voice work-file leftovers are engine-state priming
(§4.5) and ride `init.voice_state`. Only the leftovers that can actually
reach a SID write are carried — the engine's own init leaves `durctr` at 0,
so all three voices FETCH on frame 0, and that fetch overwrites
gmask/curnote/presetx/arppos before anything reads them. What survives is the
state a fetch does NOT write, i.e. what a voice idling mid-note plays: this is
`note_active`/`sliding`/`freq`/`slide_freq`/`slide_rate`/`pulse_width`.
(Measured, not assumed — see the knock-out test in project_music_assembler.)
The filter's live sweep state is `default_filter` (play-time contour), and the
pair a note-init re-arms it with is `init.filter_arm_*`.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'src')]

from src.usf.types import (                                    # noqa: E402
    Instrument, InitSid, InitFilter, InitState, InitVoice, InstrumentRef,
    MusicSubtune, NoteRow, Orderlist, Params, Pattern, Pitch, PsidMeta,
    PwmConfig, SweepEnvelope, UsfFile, VibratoConfig, VoiceBlock)

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# The engine's own init writes, and nothing else (trichotomy §2: MA is the
# "barely anything" bucket — exactly 3 bytes).
INIT_MASTER_VOL = 0x1F
INIT_RES_ROUTING = 0xF0


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


def _signed8(b: int) -> int:
    return b - 0x100 if b >= 0x80 else b


def _signed16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


def _wave_offset(b: int) -> int:
    """A RELATIVE arpeggio step's pitch offset, as a signed semitone delta.

    The engine adds the raw 0..127 byte to the note and masks the sum to 7
    bits, so 120 and -8 select the same freq-table slot. The signed reading is
    the musical one and reconstructs identically."""
    return b - 0x80 if b >= 0x40 else b


def _instrument(p, arp) -> Instrument:
    """One preset (+ the arpeggio its Fx nibble selects) as an Instrument."""
    wave = [p.waveform]
    wfreq = [0]                  # step 0 plays the row's own note
    wabs = [0]
    wfilt = [0]
    if arp is not None:
        for st in arp.steps:
            wave.append(st.waveform)
            wabs.append(1 if st.absolute else 0)
            wfreq.append(st.offset if st.absolute else _wave_offset(st.note))
            wfilt.append(st.filter_lp)
        loop = 1 if arp.loops else len(wave)
    else:
        loop = 0

    if p.fx & 0x40:
        mode = 'linear'
    elif p.fx & 0x20:
        mode = 'bidirectional'
    else:
        mode = 'none'

    # A zero depth makes the vibrato inaudible whether or not its enable bit
    # is set (the engine still runs its counters, but adds nothing), so
    # amplitude alone carries "is there vibrato" — the FC convention.
    amp = p.vib_depth if (p.fx & 0x10) else 0

    return Instrument(
        id=p.id + 1,
        waveform=wave,
        loop=loop,
        wave_freq=wfreq if len(wave) > 1 else [],
        wave_abs=wabs if any(wabs) else [],
        wave_filter=wfilt if any(wfilt) else [],
        adsr=(p.ad, p.sr),
        pwm=PwmConfig(mode=mode, speed=p.pulse_step, init=p.pulse_init),
        vibrato=VibratoConfig(shape='triangle', polarity='bipolar',
                              onset=p.vib_delay, speed=p.vib_rate,
                              amplitude=amp, period_frames=4),
    )


def _rows(events) -> list:
    """One sequence's events as note rows, folding preset selects onto the
    row that follows them (stated-instrument notation)."""
    rows, pending = [], None
    for e in events:
        if e.kind == 'preset':
            pending = InstrumentRef(id=e.value + 1)
            continue
        fx = []
        if e.kind == 'hold':
            fx.append('tie')
        pitch = _pitch(e.value) if e.kind == 'note' else Pitch.rest()
        if e.kind == 'note':
            if e.legato:
                fx.append('noretrig')
            if e.slide:
                rate = _signed16(e.slide[0] | (e.slide[1] << 8))
                fx.append('glide_up=$%04X' % rate if rate >= 0
                          else 'glide_down=$%04X' % -rate)
            if e.filt:
                fx.append('filter_sweep=$%02X,%d' % (e.filt[0], e.filt[1]))
        rows.append(NoteRow(pitch=pitch, duration=e.duration,
                            instr=pending, fx_flags=tuple(fx)))
        pending = None
    return rows


def _voice(vid: int, track, sequences) -> VoiceBlock:
    ol = Orderlist(
        entries=[e.seq for e in track.entries],
        transposes=[e.transpose for e in track.entries],
        # the engine DECs the low nibble and replays while it stays >= 0,
        # so the entry plays repeat+1 times
        repeats=[e.repeat + 1 for e in track.entries],
        loop_to=track.loop_to if track.loops else None,
        stop=not track.loops)
    pats = []
    for sn in sorted({e.seq for e in track.entries}):
        rows = _rows(sequences.get(sn, []))
        pats.append(Pattern(id=sn, length=sum(r.duration or 0 for r in rows),
                            rows=rows))
    return VoiceBlock(id=vid, orderlist=ol, patterns=pats)


def _init(m) -> InitState:
    """Per-voice engine-state priming + the filter arming pair."""
    voices = []
    for i in range(3):
        def b(key, idx=i):
            v = m.prime.get(key)
            return v[idx] if isinstance(v, list) else 0
        flg = b('noteflg')
        v = InitVoice(id=i + 1)
        # Only bits 5 and 6 of the leftover flags byte are ever read: the
        # duration bits are re-read from the stream at every fetch.
        v.note_active = bool(flg & 0x40)
        v.sliding = bool(flg & 0x20)
        v.freq = b('nfrqlo') | (b('nfrqhi') << 8)
        v.slide_freq = b('sfrqlo') | (b('sfrqhi') << 8)
        v.slide_rate = b('sl1') | (b('sl2') << 8)
        v.pulse_width = b('pwlo') | (b('pwhi') << 8)
        voices.append(v)
    return InitState(
        voices=voices,
        sid=InitSid(master_vol=INIT_MASTER_VOL,
                    filter=InitFilter(res_routing=INIT_RES_ROUTING)),
        filter_arm_cutoff=m.prime.get('fcutr', 0),
        filter_arm_frames=m.prime.get('fdurr', 0))


def model_to_usf(m) -> UsfFile:
    """A MasmModel as a UsfFile — the complete musical specification."""
    arp_for = {p.id: m.arps.get(p.arp_index) for p in m.presets}
    insts = [_instrument(p, arp_for[p.id]) for p in m.presets]
    voices = [_voice(i + 1, t, m.sequences) for i, t in enumerate(m.tracks)]

    # The filter's live sweep state at song start: cutoff `fcut` moving by
    # `fvel` for `fdur` frames. Play-time contour, not init priming — the
    # engine writes $D416 from the play loop, never from init.
    #
    # Carried whenever ANY of the three is set, not just when the sweep is
    # currently running: a note-init reloads the cutoff and the frame count,
    # but NOT the velocity, so the starting velocity survives until the song's
    # first stated filter command and is audible long after `frames` hits 0.
    # A zero-frame phase is the honest encoding of "armed at this velocity,
    # not presently sweeping".
    fdur = m.prime.get('fdur', 0)
    fcut = m.prime.get('fcut', 0)
    fvel = m.prime.get('fvel', 0)
    dflt = SweepEnvelope(start=fcut, phases=[(_signed8(fvel), fdur)],
                         loop=None) if (fcut or fvel or fdur) else None

    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      start_song=m.start_song),
        params=Params(fields={}),
        init=_init(m),
        instruments=insts,
        subtunes=[MusicSubtune(id=1, tempo=m.speed, voices=voices)],
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        default_filter=dflt,
    )


def write_masm_usf(sid_path: str, out_path: str,
                   hvsc_root: str = 'hvsc84') -> str:
    """Extract `sid_path` and write its .usf to `out_path`."""
    from pipelines.music_assembler.extract.model import extract
    from src.usf.writer import write_file
    usf = model_to_usf(extract(sid_path, hvsc_root=hvsc_root))
    write_file(usf, out_path)
    return out_path
