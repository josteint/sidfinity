"""FCConfig — per-SID configuration for the FC engine extractor.

The FC family (MoN/FutureComposer 1987-89) lacks a stable load
address: composers placed their SIDs at $0800, $1000, $1800, $2800,
$7AE0, $A600 and many other addresses, so every per-SID data table
(freq, patterns, instruments, per-subtune setup) lives at a different
CPU address even though the engine's structure is family-stable.

The shared `engine_model.extract(cfg)` walks the SID's memory image
using the addresses from `cfg`. Each canary SID gets its own
`pipelines/future_composer/<engine>/config.py` providing an `FCConfig`
instance.

Mirrors Hubbard's `EngineConfig` per-tune pattern.

What's per-SID vs what's family-stable:

- HERE (per-SID): data table addresses, table sizes, subtune layout
  discriminator
- IN engine_model: sequence/pattern command byte encodings (FE/FF
  terminators, $80-$BF length, $E0-$EF glide, etc.). These are
  FC-family-stable and never go in the config.

### Subtune layout variants

Different FC drivers store their per-subtune sequence pointers in
structurally different ways. Two layouts seen so far:

- `'flat_seqtabel'` (Cybernoid II): contiguous table; subtune N's
  6-byte sequence record lives at `seqtabel_addr + N * 6`. All
  subtunes are music — no SFX section.
- `'smc_template_with_sfx'` (Hawkeye): SMC-driven indirection — the
  table at `per_subtune_smc_addr` stores 1 lo-byte per subtune; combined
  with the fixed `template_base_hi`, this yields the per-subtune
  record's address. SFX subtunes are stored at fixed pages
  (`sfx_page_base + sfx_idx * sfx_page_stride`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SubtuneLayout = Literal['flat_seqtabel', 'smc_template_with_sfx']
VoiceLoopLayout = Literal['tight_nextvoice', 'interleaved']
NoiseTickStyle = Literal['cyb2_table', 'disabled']


@dataclass(frozen=True)
class FCConfig:
    """Per-SID configuration for the FC family extractor.

    Address fields are CPU addresses in the SID's memory image after
    loading. Table sizes and the subtune layout vary across the family.
    """
    name: str                       # canary identifier (e.g. 'hawkeye')
    sid_path: str                   # path under hvsc84/

    # Data table addresses (CPU addresses in the loaded memory image)
    freq_lo_addr: int               # freq-table lo bytes
    freq_hi_addr: int               # freq-table hi bytes
    pattern_ptr_addr: int           # pattern pointer table base
    instr_records_addr: int         # per-instrument 8-byte records
    per_subtune_speed_addr: int     # X-indexed speedbyte per subtune

    # Subtune layout discriminator (selects which variant fields apply)
    subtune_layout: SubtuneLayout

    # --- variant 'flat_seqtabel' fields ---
    seqtabel_addr: int = 0          # base of contiguous per-subtune
                                    # 6-byte (lo*3, hi*3) records

    # --- variant 'smc_template_with_sfx' fields ---
    per_subtune_smc_addr: int = 0   # X-indexed SMC template lo per subtune
    template_base_hi: int = 0       # high byte of template addr
                                    # (template = template_base_hi << 8 | smc_lo)
    per_subtune_mode_addr: int = 0  # X-indexed mode flag per subtune
                                    # (music=$02, sfx=$00)
    music_subtune_count: int = 0    # subtunes 0..N-1 are music; rest SFX
    sfx_page_base: int = 0          # SFX records at page (sfx_page_base
                                    # + sfx_idx * sfx_page_stride)
    sfx_page_stride: int = 0        # pages between SFX records

    # Table sizes (vary per SID even within the family)
    freq_table_entries: int = 96
    instr_count: int = 16
    max_patterns: int = 64

    # Aux-table addresses needed by the featuredriven asm composer.
    # These tables live in the verbatim aux region (not yet USF-derived);
    # the composer needs equates for them so the engine code can
    # reference them by name. Default 0 = "not yet located" (effect
    # that uses the table will error if invoked).
    drumtabel_addr: int = 0        # drum-program ptrs (4 bytes per drum)
    filterbytes_addr: int = 0      # filter-program ptrs (4 ptrs to 10-byte programs)
    startlen_addr: int = 0         # per-instrument noise-tick attack length
    starttabel_addr: int = 0       # per-instrument noise-tick attack waveform
    arplo_addr: int = 0            # arpeggio program ptrs (lo bytes, 8 entries)
    arphi_addr: int = 0            # arpeggio program ptrs (hi bytes, 8 entries)
    pulsetabel_addr: int = 0       # pulse-program data (4 programs × 8 bytes)
    vibtabwait_addr: int = 0       # per-instrument vibrato delay (20 bytes)
    wavearp_addr: int = 0          # 4-byte wave-arpeggio table {$80,$10,$80,$10}
    pulsearp_addr: int = 0         # 8-byte pulse-arpeggio table

    # Per-engine arpeggio start delays (counter2 thresholds at which
    # wave/pulse arpeggios activate). Cyb II: wavearpwait=2, pulsearpwait=1.
    # Hawkeye: wavearpwait=3, pulsearpwait=1.
    wavearpwait: int = 2
    pulsearpwait: int = 1

    # nextvoice's per-voice SID-register write order (offsets 0-6 within
    # the voice's $D400-$D406 block). Different FC-family engines use
    # different orders — and the order MATTERS audibly (gate-edge
    # timing, test-bit reset, ADSR delay-bug window, $D418 clicks).
    # See the SID-internal-state research for the principles.
    # Defaults to the Cybernoid II / Bowden / ACME-source convention:
    #   (4, 0, 1, 2, 3) = ctrl, freq lo, freq hi, pw lo, pw hi
    # Hawkeye overrides with (2, 3, 4, 0, 1).
    nextvoice_write_order: tuple = (4, 0, 1, 2, 3)

    # fm2 filter-cleanup parameters. fm2 runs when fx_filter_prog is NOT
    # active for the current voice. If this voice was the prior filter
    # owner, cleanup resets the filter.
    #   - Cyb II writes $D418=$10|VOL and $D416=$80, with a strange-filter
    #     early-out (don't reset if strange-filter is active).
    #   - Hawkeye writes only $D416=$E0, no $D418 write, no strange-filter
    #     check (cleanup runs unconditionally for the owner).
    fm2_cleanup_d416_value: int = 0x80           # Cyb II default
    fm2_cleanup_writes_d418: bool = True         # Cyb II default
    fm2_cleanup_checks_strange_filter: bool = True  # Cyb II default

    # Per-voice loop structural layout. Drives WHERE the SID register
    # writes happen inside the per-voice processing loop:
    #   - 'tight_nextvoice' (Cyb II default): all effects run first,
    #     writing only to shadows + maybe $D416/$D418 direct; then a
    #     tight nextvoice block writes all 5 voice regs in
    #     nextvoice_write_order.
    #   - 'interleaved' (Hawkeye): PW writes happen mid-chain (right
    #     after pulse_prog, before wave_arp / pulse_arp / filter_prog
    #     run); CTRL+FREQ writes happen at chain end. Effects that
    #     write $D416/$D418 (filter_prog, fm2, strange_filter) interleave
    #     between PW and CTRL+FREQ writes naturally.
    voice_loop_layout: VoiceLoopLayout = 'tight_nextvoice'

    # fx_noise_tick style. 'cyb2_table' (Cyb II default): per-instrument
    # startlen/starttabel lookup; writes noisehitone $FA to d401 when the
    # attack waveform byte has bit 7 set. 'disabled': fx_noise_tick is a
    # no-op (label exists but body falls through to chain end). Hawkeye
    # has its own noise-tick at $82D4 with hardcoded constants ($58, $81)
    # — using 'disabled' here prevents the Cyb II logic from reading
    # garbage from $0000 placeholder startlen/starttabel addresses;
    # a future 'hawkeye_constants' style will implement it properly.
    noise_tick_style: NoiseTickStyle = 'cyb2_table'

    # Constant offset added to the drum tone byte before storing to d401
    # (V3 freq hi shadow). Cyb II writes the raw tone byte; Hawkeye's
    # drum at $82C3 adds $0D first (`d401 = drum_table_B[counter2-1] + $0D`).
    # See hawkeye/RE_NOTES.md "Real root cause" section.
    fx_drum_d401_offset: int = 0

    # Whether the late $D404 (V_CTRL) write AND-masks `stod404` with the
    # per-voice `byteand` flag (Cyb II's drum-routine gate-off mechanism).
    # Cyb II does (default True). Hawkeye's late write at $830E/$8311 is
    # a direct `LDA $911B,X / STA $D404,Y` — no mask — because Hawkeye
    # clears the gate by modifying stod404 itself during the held-note
    # path at $7DCA, not via a separate mask. (See RE_NOTES.md.)
    late_ctrl_uses_byteand_mask: bool = True

    # Held-note gate-clear mechanism. Cyb II (False): h10 sets the
    # per-voice `byteand` mask to $FE based on a filcount-threshold
    # comparison; the late $D404 write ANDs stod404 with byteand.
    # Hawkeye (True): h10 instead does `stod404 = wavesto & $FE`
    # directly, with no byteand involvement. Mirrors disasm $7DCA-$7DF6.
    held_note_clears_stod404_gate: bool = False

    # TODO as effects come online:
    # wavearp_addr, pulsearp_addr (wave/pulse-arp tables)
