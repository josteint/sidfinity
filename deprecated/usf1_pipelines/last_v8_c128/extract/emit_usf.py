"""Emit ``codegen/LastV8C128/SongData.lean`` from the parsed engine model.

The Lean SongData here is *not* a USF song — it's a faithful dump of
what we know about the binary so the codegen has something concrete to
reference. The schema is defined in ``codegen/LastV8C128/SongData.lean``
(after this script runs) and matches the Lean ``EngineModel`` record.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .engine_model import extract
from .types import (
    EngineModel,
    Instrument,
    MusicSubtune,
    Orderlist,
    Pattern,
    PatternEvent,
    SampleRecord,
    SubtuneRoute,
)

logger = logging.getLogger(__name__)


PIPELINE_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PIPELINE_DIR / 'codegen' / 'LastV8C128' / 'SongData.lean'


def _lean_subtune_route(r: SubtuneRoute) -> str:
    return f'  {{ subtune := {r.subtune}, kind := "{r.kind}" }}'


def _lean_sample(s: SampleRecord) -> str:
    return (
        f'  {{ subtune := {s.subtune}'
        f', startAddr := 0x{s.start:04X}'
        f', endAddr := 0x{s.end:04X}'
        f', rateConstant := 0x{s.rate_constant:02X} }}'
    )


def _lean_freq_table(pairs: list[tuple[int, int]]) -> str:
    items = [f'  ({lo}, {hi})' for (lo, hi) in pairs]
    return '[\n' + ',\n'.join(items) + '\n]'


def _opt(v: int | None) -> str:
    return 'none' if v is None else f'some {v}'


def _lean_event(ev: PatternEvent) -> str:
    if ev.kind == 'tie':
        return (f'  PatternEvent.tie {ev.hold} '
                f'{"true" if ev.no_release else "false"}')
    return (
        f'  PatternEvent.note '
        f'⟨{ev.hold}, '
        f'{"true" if ev.no_release else "false"}, '
        f'{ev.pitch}, '
        f'{_opt(ev.instrument)}, '
        f'{_opt(ev.arp_mode)}⟩'
    )


def _lean_pattern(p: Pattern) -> str:
    body = ',\n'.join(_lean_event(ev) for ev in p.events) if p.events else ''
    events = f'[\n{body}\n  ]' if body else '[]'
    return (
        f'  {{ index := {p.index}, '
        f'addr := 0x{p.addr:04X}, '
        f'events := {events} }}'
    )


def _lean_orderlist(o: Orderlist) -> str:
    indices = ', '.join(str(i) for i in o.indices)
    return (
        f'    {{ voice := {o.voice}, addr := 0x{o.addr:04X}, '
        f'indices := [{indices}], terminator := "{o.terminator}" }}'
    )


def _lean_instrument(i: Instrument) -> str:
    return (
        f'  {{ id := {i.id}, '
        f'pulseWidth := 0x{i.pulse_width:04X}, '
        f'ctrl := 0x{i.ctrl:02X}, '
        f'ad := 0x{i.ad:02X}, '
        f'sr := 0x{i.sr:02X}, '
        f'vibShift := 0x{i.vib_shift:02X}, '
        f'pwm := 0x{i.pwm:02X}, '
        f'fxFlags := 0x{i.fx_flags:02X} }}'
    )


def _lean_music_subtune(s: MusicSubtune) -> str:
    voices = ',\n'.join(_lean_orderlist(v) for v in s.voices)
    return (
        f'  {{ subtune := {s.subtune},\n'
        f'    voices := [\n{voices}\n    ]\n  }}'
    )


def render(model: EngineModel) -> str:
    h = model.header
    out: list[str] = []
    out.append('-- Auto-generated from pipelines/last_v8_c128/extract/emit_usf.py')
    out.append('-- DO NOT EDIT — regenerate via:')
    out.append('--     python -m pipelines.last_v8_c128.extract')
    out.append('')
    out.append('namespace LastV8C128NS')
    out.append('')

    out.append('/-- RSID header fields, copied verbatim from the original binary. -/')
    out.append('structure Header where')
    out.append('  magic     : String')
    out.append('  loadAddr  : UInt16')
    out.append('  initAddr  : UInt16')
    out.append('  playAddr  : UInt16')
    out.append('  songs     : UInt8')
    out.append('  startSong : UInt8')
    out.append('  name      : String')
    out.append('  author    : String')
    out.append('  released  : String')
    out.append('  deriving Repr')
    out.append('')

    out.append('/-- One per subtune (0-indexed). `kind` ∈ {"music","sample","sfx"}. -/')
    out.append('structure SubtuneRoute where')
    out.append('  subtune : Nat')
    out.append('  kind    : String')
    out.append('  deriving Repr')
    out.append('')

    out.append('/-- One sample played by the relocated $C000 player. -/')
    out.append('structure SampleRecord where')
    out.append('  subtune       : Nat')
    out.append('  startAddr     : UInt16')
    out.append('  endAddr       : UInt16')
    out.append('  rateConstant  : UInt8')
    out.append('  deriving Repr')
    out.append('')

    out.append('/-- Where the static tables of the tracker driver live. -/')
    out.append('structure MusicTables where')
    out.append('  freqTable      : UInt16')
    out.append('  instrumentTable: UInt16')
    out.append('  sfxTable       : UInt16')
    out.append('  orderlistPtrs  : UInt16')
    out.append('  patternPtrLo   : UInt16')
    out.append('  patternPtrHi   : UInt16')
    out.append('  deriving Repr')
    out.append('')

    out.append('/-- The fields of a "note" pattern event. -/')
    out.append('structure NoteInfo where')
    out.append('  hold       : Nat')
    out.append('  noRelease  : Bool')
    out.append('  pitch      : Nat')
    out.append('  instrument : Option Nat')
    out.append('  arpMode    : Option Nat')
    out.append('  deriving Repr')
    out.append('')
    out.append('/-- A pattern event: a held note or a tie. -/')
    out.append('inductive PatternEvent where')
    out.append('  | note (info : NoteInfo)             : PatternEvent')
    out.append('  | tie  (hold : Nat) (noRel : Bool)   : PatternEvent')
    out.append('  deriving Repr')
    out.append('')

    out.append('structure Pattern where')
    out.append('  index   : Nat')
    out.append('  addr    : UInt16')
    out.append('  events  : List PatternEvent')
    out.append('  deriving Repr')
    out.append('')

    out.append('structure Orderlist where')
    out.append('  voice      : Nat')
    out.append('  addr       : UInt16')
    out.append('  indices    : List Nat')
    out.append('  terminator : String')
    out.append('  deriving Repr')
    out.append('')

    out.append('/-- 8-byte instrument record from $85A1. -/')
    out.append('structure Instrument where')
    out.append('  id          : Nat')
    out.append('  pulseWidth  : UInt16')
    out.append('  ctrl        : UInt8')
    out.append('  ad          : UInt8')
    out.append('  sr          : UInt8')
    out.append('  vibShift    : UInt8')
    out.append('  pwm         : UInt8')
    out.append('  fxFlags     : UInt8')
    out.append('  deriving Repr')
    out.append('')

    out.append('structure MusicSubtune where')
    out.append('  subtune : Nat')
    out.append('  voices  : List Orderlist')
    out.append('  deriving Repr')
    out.append('')

    out.append('structure EngineModel where')
    out.append('  header         : Header')
    out.append('  relocatorSrc   : UInt16')
    out.append('  relocatorLen   : UInt16')
    out.append('  relocatorDst   : UInt16')
    out.append('  routes         : List SubtuneRoute')
    out.append('  samples        : List SampleRecord')
    out.append('  music          : MusicTables')
    out.append('  freqTable      : List (UInt8 × UInt8)')
    out.append('  patterns       : List Pattern')
    out.append('  musicSubtunes  : List MusicSubtune')
    out.append('  instruments    : List Instrument')
    out.append('  deriving Repr')
    out.append('')

    out.append('def lastV8C128Model : EngineModel :=')
    out.append('  let h : Header := {')
    out.append(f'    magic     := "{h.magic}"')
    out.append(f'    loadAddr  := 0x{h.load_addr:04X}')
    out.append(f'    initAddr  := 0x{h.init_addr:04X}')
    out.append(f'    playAddr  := 0x{h.play_addr:04X}')
    out.append(f'    songs     := {h.songs}')
    out.append(f'    startSong := {h.start_song}')
    out.append(f'    name      := {_lean_str(h.name)}')
    out.append(f'    author    := {_lean_str(h.author)}')
    out.append(f'    released  := {_lean_str(h.released)}')
    out.append('  }')
    out.append('  let routes : List SubtuneRoute := [')
    out.append(',\n'.join(_lean_subtune_route(r) for r in model.routes))
    out.append('  ]')
    out.append('  let samples : List SampleRecord := [')
    out.append(',\n'.join(_lean_sample(s) for s in model.samples))
    out.append('  ]')
    out.append('  let m : MusicTables := {')
    out.append(f'    freqTable       := 0x{model.music.freq_table_addr:04X}')
    out.append(f'    instrumentTable := 0x{model.music.instrument_table_addr:04X}')
    out.append(f'    sfxTable        := 0x{model.music.sfx_table_addr:04X}')
    out.append(f'    orderlistPtrs   := 0x{model.music.orderlist_ptrs_addr:04X}')
    out.append(f'    patternPtrLo    := 0x{model.music.pattern_ptr_lo_addr:04X}')
    out.append(f'    patternPtrHi    := 0x{model.music.pattern_ptr_hi_addr:04X}')
    out.append('  }')
    out.append('  let patterns : List Pattern := [')
    out.append(',\n'.join(_lean_pattern(p) for p in model.patterns))
    out.append('  ]')
    out.append('  let musicSubtunes : List MusicSubtune := [')
    out.append(',\n'.join(_lean_music_subtune(s) for s in model.music_subtunes))
    out.append('  ]')
    out.append('  let instruments : List Instrument := [')
    out.append(',\n'.join(_lean_instrument(i) for i in model.instruments))
    out.append('  ]')
    out.append('  {')
    out.append('    header         := h')
    out.append(f'    relocatorSrc   := 0x{model.relocator_src:04X}')
    out.append(f'    relocatorLen   := 0x{model.relocator_len:04X}')
    out.append(f'    relocatorDst   := 0x{model.relocator_dst:04X}')
    out.append('    routes         := routes')
    out.append('    samples        := samples')
    out.append('    music          := m')
    out.append('    freqTable      := ' + _lean_freq_table(model.freq_table))
    out.append('    patterns       := patterns')
    out.append('    musicSubtunes  := musicSubtunes')
    out.append('    instruments    := instruments')
    out.append('  }')
    out.append('')
    out.append('end LastV8C128NS')
    out.append('')
    return '\n'.join(out)


def _lean_str(s: str) -> str:
    # Lean string literals: double-quote, escape backslash and quotes.
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog='python -m pipelines.last_v8_c128.extract',
        description=(
            'Parse the original Last V8 (C128) RSID, identify the dual-engine '
            'layout, and write SongData.lean for the Lean codegen.'
        ),
    )
    p.add_argument('subtunes', nargs='?', default=None,
                   help='accepted for parity with sibling pipelines; '
                        'ignored — this pipeline emits the whole model.')
    p.add_argument('-v', '--verbose', action='store_true')
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s',
    )

    model = extract()
    text = render(model)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text)
    logger.info('wrote %s', OUT_PATH.relative_to(PIPELINE_DIR.parent))
    logger.info('  routes:  %s',
                ', '.join(f'{r.subtune}={r.kind}' for r in model.routes))
    logger.info('  samples: %d (addrs %s)',
                len(model.samples),
                ', '.join(f'${s.start:04X}-${s.end:04X}' for s in model.samples))
    logger.info('  instruments: %d (referenced: %s)',
                len(model.instruments),
                sorted({ev.instrument for p in model.patterns for ev in p.events
                        if ev.instrument is not None}))
    logger.info('  patterns: %d', len(model.patterns))
    for s in model.music_subtunes:
        lens = ' '.join(f'V{v.voice}={len(v.indices)}({v.terminator})'
                        for v in s.voices)
        logger.info('  music subtune %d: %s', s.subtune, lens)
    return 0


if __name__ == '__main__':
    sys.exit(main())
