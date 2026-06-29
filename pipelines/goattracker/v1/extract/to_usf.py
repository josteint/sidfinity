"""GoatTracker V1 — V1Song model → USF (UsfFile).

Maps the faithful extracted model to musical USF content (RE_NOTES §7). The
mapping is deliberately FAITHFUL (one NoteRow per GT row, rests explicit) to
minimise reduction risk during canary bring-up; an ML-legibility pass that
collapses rests into note durations is a later verify-gated refinement.

Per-row commands → NoteRow.fx_flags strings (convergence ledger C14, FC
precedent). The freq table is a player CONSTANT (not per-tune) so it is not
carried in USF — the composer emits it. Filter programs are carried only when
present (the canary has none).
"""
from __future__ import annotations

import os

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitState, Instrument, PwmConfig,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
    InstrumentRef, FilterProgConfig,
)
from src.usf.writer import write_file
from pipelines.goattracker.v1.extract.engine_model import (
    parse_sid, extract, V1Song, Instr,
)

_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
KEYOFF = 0x5E
REST = 0x5F


def _pitch(note: int) -> Pitch:
    """GT note number (0=C0 .. 93=A7) → USF Pitch."""
    return Pitch(name=_NOTE_NAMES[note % 12], octave=note // 12)


def _row_fx(cmd, param) -> tuple:
    """Per-row command → fx_flags tuple (ledger C14). Decomposed to musical
    parameters. Existing grammar tokens (porta/glide_up/glide_down/srr/filter/
    tempo) are reused; `arp` + `vibrato` are GT-specific carriers (grammar
    extension pending — composer reads these from the in-memory model)."""
    if cmd is None:
        return ()
    if cmd == 0:                               # arpeggio: cycle root,+X,+Y
        # Always emit (even param 0): a cmd-row SETS the active continuous
        # effect to arp, CLEARING any inherited effect (note-only rows inherit).
        x = (param >> 4) & 0x07                # 2nd-note offset (semitones)
        y = param & 0x0F                       # 3rd-note offset
        speed = (param >> 7) & 1               # bit7: 1 = fast (1 frame/step), 0 = slow (2)
        return (f'arp={x},{y},{speed}',)
    if cmd == 1:                               # portamento up (continuous)
        return (f'glide_up={param}',)
    if cmd == 2:                               # portamento down
        return (f'glide_down={param}',)
    if cmd == 3:                               # tone portamento (param 0 = tie)
        return (f'porta={param}',)
    if cmd == 4:                               # vibrato: amp(hi nibble), width(lo)
        return (f'vibrato={(param >> 4) & 0x0F},{param & 0x0F}',)
    if cmd == 5:                               # set filter pointer
        return (f'filter={param}',)
    if cmd == 6:                               # set SR ($D406)
        return (f'srr={param}',)
    if cmd == 7:                               # set tempo / fader / timing
        return (f'tempo={param}',)
    return ()


def _rows_to_usf(rows) -> list[NoteRow]:
    """Faithful row-stream: one NoteRow per GT row.

    note 0-$5D → pitched note; $5E → keyoff (rest pitch + 'keyoff'); $5F →
    rest (sustain). Packed rest (rest_rows>0) → one rest row of that many
    rows. duration is in ROWS (composer converts to frames via tempo)."""
    out: list[NoteRow] = []
    for r in rows:
        if r.rest_rows:                                # packed rest
            out.append(NoteRow(pitch=Pitch.rest(), duration=r.rest_rows))
            continue
        flags = _row_fx(r.cmd, r.param)
        # Set instr ONLY on a real instrument change (orig inst field != 0).
        # Note-only rows (no cmd) inherit BOTH the instrument and the active
        # effect via engine state — emitting neither keeps that inheritance.
        instr = InstrumentRef(id=r.instr) if r.new_instr else None
        if r.note == REST or r.note > REST:            # rest / sustain
            out.append(NoteRow(pitch=Pitch.rest(), duration=1, instr=instr,
                               fx_flags=flags))
        elif r.note == KEYOFF:
            out.append(NoteRow(pitch=Pitch.rest(), duration=1, instr=instr,
                               fx_flags=('keyoff',) + flags))
        else:                                          # pitched note
            out.append(NoteRow(pitch=_pitch(r.note), duration=1, instr=instr,
                               fx_flags=flags))
    return out


def _instr_to_usf(inst: Instr) -> Instrument:
    """GT instrument → USF Instrument. Wave program as waveform(ctrl)+
    wave_freq(note rel/abs raw) + loop; pulse as PwmConfig; hard-restart flag
    (pulsespd bit0 == 0) → effects {'hard_restart'}."""
    waveform = [s.left for s in inst.wave_steps]
    wave_freq = [s.right for s in inst.wave_steps]
    loop = inst.wave_loop if inst.wave_loop is not None else 0
    pmod = inst.pulsespd & 0xFE
    pwm = PwmConfig(
        mode='bidirectional' if pmod else 'none',
        speed=pmod, init=inst.pulse,
        min_hi=inst.pulselow, max_hi=inst.pulsehigh,
    )
    # Hard-restart flag (pulsespd bit0 == 0 → do HR) — the COMMON case.
    # Carried per-instrument once a tune needs the no-HR exception; the
    # composer defaults to HR-on. (TODO: principled carrier for no-HR insts.)
    fp = FilterProgConfig(program=inst.filter) if inst.filter else FilterProgConfig()
    return Instrument(
        id=inst.num, waveform=waveform, wave_freq=wave_freq, loop=loop,
        adsr=(inst.ad, inst.sr), pwm=pwm, filter_prog=fp,
    )


def model_to_usf(song: V1Song) -> UsfFile:
    sid = song.sid
    L = song.layout

    subtunes = []
    for s_idx, chans in enumerate(song.subtunes):
        voices = []
        for ch_idx, ol in enumerate(chans):
            # Per-voice pattern renumbering (USF pattern ids unique per voice).
            used = []
            for pn in ol.entries:
                if pn not in used:
                    used.append(pn)
            remap = {pn: i for i, pn in enumerate(used)}
            pats = []
            for pn in used:
                rows = _rows_to_usf(song.patterns[pn].rows)
                pats.append(Pattern(id=remap[pn],
                                    length=sum(r.duration for r in rows),
                                    rows=rows))
            usf_ol = Orderlist(
                entries=[remap[pn] for pn in ol.entries],
                transposes=list(ol.transposes) if ol.transposes else [],
                repeats=list(ol.repeats) if ol.repeats else [],
                loop_to=ol.loop_to,
            )
            voices.append(VoiceBlock(id=ch_idx + 1, orderlist=usf_ol,
                                     patterns=pats))
        subtunes.append(MusicSubtune(id=s_idx + 1, tempo=5, voices=voices))

    instruments = [_instr_to_usf(song.instruments[k])
                   for k in sorted(song.instruments)]

    params = Params(fields={
        'engine': 'goattracker_v1',
        'gatetimer': L.gatetimer,
        'hr_ad': L.hr_ad,
        'hr_sr': L.hr_sr,
        'default_tempo': 5,
        # init filter state (setfiltersub(0)): d416, d417, d418type, filttime, filtstep
        'filt_init': list(song.init_filter),
        'funk': list(song.funk),
    })
    # Full filter table — the engine steps through it (4-byte entries) when an
    # instrument's filter ptr or a setfilter cmd selects a program. (TODO: this
    # is a raw blob; the principled form is musical filter programs — C7/C10.)
    if any(b for b in song.filttbl_bytes[4:]):    # >entry0 has real data
        params.fields['filttbl_bytes'] = list(song.filttbl_bytes)

    return UsfFile(
        psid=PsidMeta(title=sid.name, author=sid.author, released=sid.released,
                      start_song=sid.start),
        params=params,
        init=InitState(),
        instruments=instruments,
        subtunes=subtunes,
        # freq table is PER-PLAYER (V1.x sub-versions differ) — carry it as
        # per-tune musical content (tuning), 96 lo + 96 hi.
        freq_table=(list(song.freq_lo) + list(song.freq_hi))
        if song.freq_lo else None,
    )


def write_v1_usf(sid_path: str, out_dir: str | None = None) -> str:
    song = extract(parse_sid(sid_path))
    usf = model_to_usf(song)
    out_dir = out_dir or os.path.dirname(sid_path)
    base = os.path.splitext(os.path.basename(sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/T/Topaz/Joker.sid'
    # In-memory model (the composer consumes this; text-grammar round-trip for
    # arp/vibrato fx is a pending grammar extension).
    song = extract(parse_sid(path))
    usf = model_to_usf(song)
    print(f'{path}')
    print(f'  {len(usf.instruments)} instruments, {len(usf.subtunes)} subtune(s)')
    for v in usf.subtunes[0].voices:
        print(f'  voice {v.id}: {len(v.patterns)} patterns, '
              f'orderlist {len(v.orderlist.entries)} entries '
              f'loop_to={v.orderlist.loop_to}')
    # show some fx_flags
    fx = set()
    for v in usf.subtunes[0].voices:
        for p in v.patterns:
            for r in p.rows:
                fx.update(r.fx_flags)
    print('  fx_flags seen:', sorted(fx)[:12])
    print('  params:', usf.params.fields)
