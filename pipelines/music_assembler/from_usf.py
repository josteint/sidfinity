"""Music Assembler — UsfFile -> MasmModel, the build side of the round trip.

The USF is read as the COMPLETE specification of the music (the principle's
§8): nothing here consults the original image, and no branch asks which engine
produced the file. `MasmModel` is the composer's internal IR, not a library
keyed by USF content — `composer_asm` emits one player, always the same one,
parameterised only by what this module reads out of the USF.

Two reconstructions deserve a note, because both are places where a naive
inverse would lose information:

RE-POOLING THE ARPEGGIOS. `to_usf` inlines each instrument's arpeggio into its
wave program (de-fusing the engine's shared 16-entry pool, the C8 idiom). The
engine indexes that pool with a NIBBLE, so the inverse must fit the distinct
programs back into 15 slots. Identical programs dedup to one slot — which is
also what the original editor did, since several presets routinely share an
arpeggio.

THE IDLE STATE. USF carries only the leftovers that can reach a SID write
(see `to_usf`'s header). Everything else the engine's frame-0 fetch overwrites
before it is read, so the composer seeds those from ITS OWN note-init values
rather than from stored bytes: a voice primed `note_active` idles exactly as
if a note had just been initialised, which is what the state means. That is
mechanism choosing a consistent idle, not a guessed constant.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'src')]

from pipelines.music_assembler.extract.arps import Arp, ArpStep    # noqa: E402
from pipelines.music_assembler.extract.decode import (             # noqa: E402
    Event, OrderEntry, Track)
from pipelines.music_assembler.extract.model import MasmModel      # noqa: E402
from pipelines.music_assembler.extract.presets import Preset       # noqa: E402

ARP_SLOTS = 16                  # the Fx nibble: slots 1..15 are usable


def _u16(v: int) -> tuple:
    v &= 0xFFFF
    return v & 0xFF, v >> 8


def _arp_pool(instruments) -> tuple:
    """(arps, index_by_instrument_id) — the instruments' inlined wave programs
    re-pooled into the engine's 15 arpeggio slots, identical ones shared."""
    arps, idx_of, seen = {}, {}, {}
    for inst in instruments:
        wave = list(inst.waveform or [])
        if len(wave) < 2:                    # step 0 only = no arpeggio
            idx_of[inst.id] = 0
            continue
        wfreq = list(inst.wave_freq or [])
        wabs = list(inst.wave_abs or [])
        wfilt = list(inst.wave_filter or [])

        def at(lst, k, default=0):
            return lst[k] if k < len(lst) else default

        steps = []
        for k in range(1, len(wave)):
            absolute = bool(at(wabs, k))
            off = at(wfreq, k)
            note = (off | 0x80) if absolute else (off & 0x7F)
            steps.append(ArpStep(waveform=wave[k], note=note,
                                 filter_lp=at(wfilt, k)))
        loops = inst.loop == 1
        key = (tuple((s.waveform, s.note, s.filter_lp) for s in steps), loops)
        if key not in seen:
            slot = len(seen) + 1
            if slot >= ARP_SLOTS:
                raise ValueError(
                    'arpeggio pool overflow: %d distinct wave programs, the '
                    'engine index is a nibble (15 slots)' % (len(seen) + 1))
            seen[key] = slot
            arps[slot] = Arp(id=slot, addr=0, steps=steps, loops=loops)
        idx_of[inst.id] = seen[key]
    return arps, idx_of


def _preset(inst, arp_index: int) -> Preset:
    pwm = inst.pwm
    fx = arp_index & 0x0F
    if pwm.mode == 'linear':
        fx |= 0x40
    elif pwm.mode == 'bidirectional':
        fx |= 0x20
    vib = inst.vibrato
    if vib.amplitude:
        fx |= 0x10
    # delay occupies bits 3-7 and rate bits 0-3; they overlap at bit 3, which
    # the editor's own packing guarantees consistent.
    vib_byte = ((vib.onset & 0x1F) << 3) | (vib.speed & 0x07)
    ad, sr = inst.adsr
    return Preset(id=inst.id - 1, ad=ad, sr=sr,
                  waveform=(inst.waveform or [0])[0],
                  pulse_init=pwm.init, pulse_step=pwm.speed,
                  vib_byte=vib_byte, vib_depth=vib.amplitude, fx=fx)


def _flag(row, name: str):
    """The value of a `name=...` fx flag on `row`, or None."""
    pre = name + '='
    for f in row.fx_flags:
        if f.startswith(pre):
            return f[len(pre):]
    return None


def _events(rows) -> list:
    """One pattern's note rows back into a sequence event stream."""
    out = []
    for r in rows:
        if r.instr is not None:
            out.append(Event('preset', value=r.instr.id - 1))
        dur = r.duration or 0
        if r.pitch.is_rest:
            kind = 'hold' if 'tie' in r.fx_flags else 'rest'
            out.append(Event(kind, duration=dur))
            continue
        note = r.pitch.octave * 12 + [
            'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
        ].index(r.pitch.name)
        ev = Event('note', value=note, duration=dur,
                   legato='noretrig' in r.fx_flags)
        flags = dur & 0x1F
        if ev.legato:
            flags |= 0x40
        up, down = _flag(r, 'glide_up'), _flag(r, 'glide_down')
        if up is not None or down is not None:
            rate = int((up or down).lstrip('$'), 16)
            if down is not None:
                rate = -rate
            ev.slide = _u16(rate)
            flags |= 0x20
        fs = _flag(r, 'filter_sweep')
        if fs is not None:
            cut, frames = fs.split(',')
            ev.filt = (int(cut.lstrip('$'), 16), int(frames))
            flags |= 0x80
        ev.raw_flags = flags
        out.append(ev)
    return out


def _prime(usf) -> dict:
    """The engine's idle state. Carried leftovers come from the USF; the rest
    are the composer's own post-note-init values (see the module header)."""
    p = {}
    voices = {v.id: v for v in usf.init.voices}
    for key, default in (('gmask', 0xFF), ('rattle', 0xFF), ('curnote', 0),
                         ('presetx', 0), ('arppos', 0), ('vibfr', 0),
                         ('vibph', 0), ('vibdly', 0), ('pwfr', 0),
                         ('pwdir', 0)):
        p[key] = [default] * 3
    for name in ('nfrqlo', 'nfrqhi', 'sfrqlo', 'sfrqhi', 'sl1', 'sl2',
                 'pwlo', 'pwhi', 'noteflg'):
        p[name] = [0, 0, 0]
    for i in range(3):
        v = voices.get(i + 1)
        if v is None:
            continue
        flg = (0x40 if v.note_active else 0) | (0x20 if v.sliding else 0)
        p['noteflg'][i] = flg
        p['nfrqlo'][i], p['nfrqhi'][i] = _u16(v.freq or 0)
        p['sfrqlo'][i], p['sfrqhi'][i] = _u16(v.slide_freq or 0)
        p['sl1'][i], p['sl2'][i] = _u16(v.slide_rate or 0)
        p['pwlo'][i], p['pwhi'][i] = _u16(v.pulse_width or 0)
    p['fcutr'] = usf.init.filter_arm_cutoff
    p['fdurr'] = usf.init.filter_arm_frames
    df = usf.default_filter
    if df is not None and df.phases:
        rate, frames = df.phases[0]
        p['fcut'], p['fvel'], p['fdur'] = df.start, rate & 0xFF, frames
    else:
        p['fcut'] = p['fvel'] = p['fdur'] = 0
    return p


FREQ_NOTES = 96
FREQ_READ = 128


def _freq_tables(usf) -> tuple:
    """The composer's freq tables: the musical 96 plus the off-table tail the
    instruments' `offtable_freq` records describe (ledger C6).

    Both tables are padded to a CONSTANT 128 entries for every member, never a
    per-tune size. A per-tune-varying array size shifts everything after it and
    can change page-crossing branch cycles — the GoatTracker V1 lesson in C6.
    Unreachable slots stay 0: nothing reads them, and if the reach model ever
    under-captures, the read lands on a 0 and diverges in verify rather than
    silently playing a plausible wrong byte.
    """
    ft = list(usf.freq_table or [])
    half = len(ft) // 2
    lo = ft[:half] + [0] * (FREQ_READ - half)
    hi = ft[half:] + [0] * (FREQ_READ - half)
    for inst in usf.instruments:
        for rec in getattr(inst, 'offtable_freq', ()) or ():
            offset, note, flo, fhi = rec[:4]
            idx = (offset + note) & 0xFF
            if FREQ_NOTES <= idx < FREQ_READ:
                lo[idx], hi[idx] = flo, fhi
    return lo, hi


def usf_to_model(usf) -> MasmModel:
    """A UsfFile as the composer's MasmModel."""
    sub = next(s for s in usf.subtunes if getattr(s, 'kind', 'music') == 'music')
    arps, arp_idx = _arp_pool(usf.instruments)
    presets = [_preset(i, arp_idx[i.id]) for i in usf.instruments]

    tracks, sequences = [], {}
    for vb in sorted(sub.voices, key=lambda v: v.id):
        ol = vb.orderlist
        tracks.append(Track(
            entries=[OrderEntry(seq=e, transpose=ol.transpose_at(k),
                                repeat=ol.repeat_at(k) - 1)
                     for k, e in enumerate(ol.entries)],
            loops=ol.loop_to is not None,
            loop_to=ol.loop_to or 0))
        for pat in vb.patterns:
            sequences.setdefault(pat.id, _events(pat.rows))

    lo, hi = _freq_tables(usf)
    return MasmModel(
        speed=sub.tempo, tracks=tracks, sequences=sequences,
        presets=presets, arps=arps,
        freq_lo=lo, freq_hi=hi,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
        start_song=usf.psid.start_song,
        prime=_prime(usf))


def build_masm_sid(usf) -> bytes:
    """UsfFile -> a complete PSID file."""
    from pipelines.music_assembler.composer_asm import build_sid
    return build_sid(usf_to_model(usf))
