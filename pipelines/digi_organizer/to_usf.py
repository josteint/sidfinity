"""Digi-Organizer — typed model → .usf + FLAC sidecars.

Mapping (RE_NOTES.md §USF mapping, schema 532b3931):
  digi { technique: volume_4bit, or_mask }   (idle_level absent — the
    engine writes nothing at sample end)
  sample_instrument N { sample, rate_cycles=<per-sample TA latch lo> }
  subtune 0 music: no SID voices, digi_voice orderlist+patterns;
    tempo = speed_reload + 1 (frames per row);
    init.speed_ctr_init = the init-time counter seed;
    init.sid.master_vol = the core init's $D418 prime.
"""
from __future__ import annotations

import os

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitState, InitSid,
    DigiConfig, SampleInstrument, MusicSubtune, VoiceBlock,
    Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
)
from src.usf import writer as usf_writer
from pipelines.hubbard.sample import Sample
from pipelines.hubbard.flac_io import write_sample

from .extract import extract_model

PAL_CLOCK = 985248


def model_to_usf(m, usf_dir: str, basename: str) -> UsfFile:
    """Build the UsfFile and write the PCM sidecars into `usf_dir`."""
    # --- PCM sidecars: one FLAC per distinct page range; instruments
    # at different latches share the blob (a pitched sample).
    blob_file = {}
    for bi, (key, nibbles) in enumerate(sorted(m.pcm.items())):
        fname = f'{basename}.sample{bi}.flac'
        audio = bytes(n << 4 for n in nibbles)
        smp = Sample(
            audio=audio,
            sample_rate=PAL_CLOCK // max(1, m.base_latch),
            native_bits=4, method='d418_4bit_pcm', timer_source='cia2',
            engine='digi_organizer', extras={})
        write_sample(smp, os.path.join(usf_dir, fname))
        blob_file[key] = fname

    sample_instruments = [
        SampleInstrument(id=sid_, sample=blob_file[(s, e)],
                         rate_cycles=latch)
        for sid_, (s, e, latch) in sorted(m.samples.items())]

    # --- the digi voice score ---
    entries = [pat for pat, _rep in m.orderlist]
    repeats = [rep + 1 for _pat, rep in m.orderlist]
    ol = Orderlist(entries=entries, repeats=repeats)
    if m.order_term == 'loop':
        ol.loop_to = 0
    else:
        ol.stop = True
    patterns = []
    for pid, rows in sorted(m.patterns.items()):
        prows = []
        for b in rows:
            if b == 0:
                prows.append(NoteRow(pitch=Pitch.rest(), duration=1))
            else:
                prows.append(NoteRow(pitch=Pitch.rest(), duration=1,
                                     instr=InstrumentRef(b)))
        patterns.append(Pattern(id=pid, length=len(prows), rows=prows))

    # speed_init IS speed_reload physically: the "$908E init byte" is
    # the tick's own LDA #imm operand (code-as-data) — one engine byte,
    # carried once as `tempo`. Assert the identity so a variant that
    # breaks it is refused loudly instead of silently mis-carried.
    if m.speed_init != m.speed_reload:
        raise ValueError(
            f'speed_init ${m.speed_init:02X} != reload '
            f'${m.speed_reload:02X} — not the code-as-data shape')
    init = InitState(sid=InitSid(master_vol=m.d418_init))

    sub = MusicSubtune(
        id=0, tempo=m.speed_reload + 1, voices=[],
        digi_voice=VoiceBlock(
            id=0, orderlist=ol, patterns=patterns),
        init=None)

    meta = m.meta
    return UsfFile(
        psid=PsidMeta(title=meta['title'], author=meta['author'],
                      released=meta['released'],
                      start_song=meta['start_song'],
                      speed=meta['speed']),
        # Temporal dispatch of the sequencer tick: the driver CLASS
        # (cycle-shape the composer mirrors — the pre-core-init cycles
        # set the CIA2-NMI phase) + raster line + $D011 (badline
        # pattern = NMI-phase signal under Mode-2). Params keys
        # registered in tools/composer_params.json; the typed
        # `environment` block is the sibling family — flagged in the
        # digi proposal for the owner rather than grown silently here.
        # Defaults elided: sei=True, core_entry='core', nop=False.
        params=Params(fields={
            'digi_driver': m.driver,
            **({'digi_tick_raster': m.raster_line}
               if m.raster_line is not None else {}),
            **({'digi_tick_d011': m.d011} if m.d011 is not None else {}),
            **({'digi_driver_sei': False}
               if m.driver_params.get('sei') is False else {}),
            **({'digi_core_entry': 'core40'}
               if m.driver_params.get('core_entry') == 'core40' else {}),
            **({'digi_driver_nop': True}
               if m.driver_params.get('nop') else {}),
            **({'digi_base_latch': m.base_latch}
               if m.base_latch != 0x70 else {}),
            **({'digi_port_preinit': m.port_preinit}
               if m.port_preinit is not None else {}),
            **({'digi_core_tail': m.core_tail}
               if m.core_tail != 'rts' else {}),
            **({'digi_driver_bit': True}
               if m.driver_params.get('bit_pad') else {}),
        }),
        init=init,
        digi=DigiConfig(technique='volume_4bit', idle_level=None,
                        or_mask=m.or_mask),
        sample_instruments=sample_instruments,
        subtunes=[sub])


def write_usf(sid_path: str, out_dir: str | None = None) -> str:
    """SID → .usf (+ .sampleN.flac sidecars). Returns the .usf path."""
    m = extract_model(sid_path)
    if out_dir is None:
        out_dir = os.path.dirname(sid_path)
    basename = os.path.splitext(os.path.basename(sid_path))[0]
    usf = model_to_usf(m, out_dir, basename)
    out = os.path.join(out_dir, basename + '.usf')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(usf_writer.write(usf))
    return out
