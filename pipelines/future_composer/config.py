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


SubtuneLayout = Literal['flat_seqtabel', 'smc_template_with_sfx',
                        'runtime_slot']
VoiceLoopLayout = Literal['tight_nextvoice', 'interleaved']
NoiseTickStyle = Literal['cyb2_table', 'hawkeye_constants', 'disabled']


@dataclass(frozen=True)
class EngineInstance:
    """One engine instance in a multi-engine FC SID.

    Most FC SIDs are single-engine: the engine code + data live at
    fixed addresses, and the PSID's init/play vectors point directly
    into the engine. For these, FCConfig.engines is None and the
    top-level address fields apply across all subtunes.

    Some FC SIDs (Adrenalin / HeatWave is the worked example) use a
    DIFFERENT engine per subtune — either the same FC family code
    relocated to a different base address, or a distinct entry shim.
    Each subtune's PSID init runs a memcpy of packed-source bytes into
    the runtime layout, then SMCs the play handler to the subtune's
    entry. EngineInstance captures one such engine layout.

    `subtune_indices` lists which 0-based subtune indices use this
    instance. `play_vector` is what gets SMC'd into PSID's play slot.
    The address fields override the top-level FCConfig defaults: 0
    means "fall back to the FCConfig top-level field of the same name."
    """
    name: str
    subtune_indices: tuple[int, ...]

    # Init copy params — engine init memcpy from raw binary's packed
    # source into the runtime data layout. 0 = no copy needed (engine
    # data already at runtime addresses in the raw binary, as
    # Hawkeye/Cyb II are).
    copy_src_addr: int = 0
    copy_dst_addr: int = 0
    copy_size: int = 0

    # PSID play handler address for subtunes in subtune_indices.
    # 0 = use PSID header's play field directly.
    play_vector: int = 0

    # Runtime address overrides. 0 = inherit the corresponding
    # top-level FCConfig field. The list is the same set as the
    # mandatory + aux fields on FCConfig.
    freq_lo_addr: int = 0
    freq_hi_addr: int = 0
    pattern_ptr_addr: int = 0
    instr_records_addr: int = 0
    per_subtune_speed_addr: int = 0
    seqtabel_addr: int = 0
    drumtabel_addr: int = 0
    filterbytes_addr: int = 0
    startlen_addr: int = 0
    starttabel_addr: int = 0
    arplo_addr: int = 0
    arphi_addr: int = 0
    pulsetabel_addr: int = 0
    vibtabwait_addr: int = 0
    wavearp_addr: int = 0
    pulsearp_addr: int = 0


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

    # --- variant 'runtime_slot' fields ---
    # For SIDs whose songinit copies subtune-specific data into a
    # fixed runtime "active slot" (the engine then reads from that
    # slot regardless of which subtune is active). Extract reads
    # directly from these addresses AFTER running init in py65 for
    # each subtune — `_run_init_in_py65` populates the slot with the
    # active subtune's pointers/speed. No per-subtune indexing.
    #
    # Used by Adrenalin: songinit at `$7AB4` SMC-copies 6 bytes from
    # `($18A5+X:$18A7+X)+0..5` to `$18B5..$18BA` (per-voice seq
    # pointers) and loads `$18A1+X` → `$7A09` (active speedbyte).
    runtime_seq_ptrs_addr: int = 0       # base of 6-byte slot
                                         # (3 lo bytes then 3 hi bytes)
    runtime_speed_addr: int = 0          # active speedbyte slot

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

    # Mask applied to filtercount (filter program selector) before
    # indexing filterbytes[]. Cyb II's fx_filter_prog at $AC76 uses
    # AND #$07 (8 programs). Hawkeye at $8149 uses AND #$03 (4
    # programs). Wrong mask reads beyond filterbytes table → garbage
    # filter routing/cutoff values written to $D418/$D416.
    filter_prog_mask: int = 0x07                 # Cyb II default

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

    # h11's force-release SR value, written to $D406,Y at end-of-note
    # when wave-byte bit $10 is set AND speedsto==1. Cyb II writes $02,
    # Hawkeye writes $01 (from `LDA $9116 / CMP #$01 / STA $D406,Y`,
    # reusing the freshly-loaded speed counter as the release value).
    h11_release_sr_value: int = 0x02

    # Whether nolengset (new-note load) resets tonearpcounter to 0.
    # Cyb II resets (default True); Hawkeye does NOT — its tonearpcounter
    # ($9107) is touched only inside fx_tone_arp itself, persisting
    # across notes. Resetting in mine produces wrong V3 freq evolution
    # in tunes that use tone_arp (sub 3 drops 1378→full match after
    # disabling).
    nolengset_resets_tonearpcounter: bool = True

    # fx_pulse_run (fx3 bit $02). 'disabled' (default): a STUB that just
    # falls through. 'cyb2': adds pulserunspeed to a per-voice accumulator
    # each frame, stores to pulsestolo, and walks a per-voice pwhi shadow
    # with overflow wrap. Mirrors Cyb II's $ACE4-$AD24 routine.
    pulse_run_style: Literal['disabled', 'cyb2'] = 'disabled'
    # Cyb II's pulse_run is `ADC #$63` (step = $63 hardcoded in the engine).
    pulserunspeed: int = 0x63
    # Cyb II's pwhi shadow CMP #$0F / EOR #$08 — when shadow hits upper,
    # wrap via XOR (= $07).
    pulserun_pwhi_upper: int = 0x0F
    pulserun_pwhi_wrap_xor: int = 0x08

    # When non-zero, shift every data-table address (freq_lo, freq_hi,
    # snelheid, instr_records, drumtabel, pulsetabel, ...) up by this
    # many bytes in the featuredriven rebuild ONLY. Engine code grows
    # past the HVSC table positions on some engines (e.g. Hawkeye's
    # $8337 is tight); a small upward shift creates margin. Extraction
    # still reads from the unshifted addresses (HVSC's actual layout).
    featuredriven_addr_shift: int = 0

    # SFX seq-stream destination address. For smc_template_with_sfx
    # engines, sub_song_init copy3 writes 256 bytes from $SFX_page+$1A
    # to this address. Orig location for Hawkeye is $8FC5; declared
    # symbolically in the asm so the composer can pick a different
    # value if the data layout shifts. 0 = use orig location $8FC5.
    sfx_seq_stream_addr: int = 0

    # Multi-engine support: if a SID uses a different engine instance
    # per subtune (different code, different runtime addresses, different
    # init-copy params), provide one EngineInstance per layout here.
    # None = single-engine SID; top-level fields apply to all subtunes
    # (the Hawkeye / Cybernoid II shape).
    #
    # Cover every subtune index with exactly one EngineInstance —
    # use `instance_for_subtune` to look up.
    engines: tuple | None = None

    # TODO as effects come online:
    # wavearp_addr, pulsearp_addr (wave/pulse-arp tables)


def instance_for_subtune(cfg: FCConfig, subtune: int) -> EngineInstance | None:
    """Return the EngineInstance handling `subtune`, or None for the
    single-engine case (caller should use cfg's top-level fields).

    Raises ValueError if `cfg.engines` is set but no instance covers
    `subtune` — that's a config bug, not a single-engine SID.
    """
    if cfg.engines is None:
        return None
    for engine in cfg.engines:
        if subtune in engine.subtune_indices:
            return engine
    raise ValueError(
        f'FCConfig {cfg.name!r}: no EngineInstance covers subtune {subtune}; '
        f'engines cover {[e.subtune_indices for e in cfg.engines]!r}'
    )


def resolve_address(cfg: FCConfig, engine: EngineInstance | None,
                    field: str) -> int:
    """Resolve a runtime address field, looking at the EngineInstance
    override first (if non-zero) then falling back to cfg's top-level
    field of the same name. Use this from extract/composer code that
    needs to handle both single- and multi-engine SIDs uniformly.

    Example:
      engine = instance_for_subtune(cfg, sub)
      freq_lo = resolve_address(cfg, engine, 'freq_lo_addr')
    """
    if engine is not None:
        v = getattr(engine, field, 0)
        if v != 0:
            return v
    return getattr(cfg, field)
