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

- `'flat_seq_table'` (Cybernoid II): contiguous table; subtune N's
  6-byte sequence record lives at `seq_table_addr + N * 6`. All
  subtunes are music — no SFX section.
- `'smc_template_with_sfx'` (Hawkeye): SMC-driven indirection — the
  table at `per_subtune_smc_addr` stores 1 lo-byte per subtune; combined
  with the fixed `template_base_hi`, this yields the per-subtune
  record's address. SFX subtunes are stored at fixed pages
  (`sfx_page_base + sfx_idx * sfx_page_stride`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


SubtuneLayout = Literal['flat_seq_table', 'smc_template_with_sfx',
                        'runtime_slot']
VoiceLoopLayout = Literal['tight_nextvoice', 'interleaved', 'standard']
NoiseTickStyle = Literal['cyb2_table', 'hawkeye_constants', 'standard',
                         'disabled']


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
    seq_table_addr: int = 0
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

    # --- variant 'flat_seq_table' fields ---
    seq_table_addr: int = 0          # base of contiguous per-subtune
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
    # Minimum valid hi byte for an arp-program pointer in arphi; the extract
    # skips arphi slots below this as unused/garbage. Default $80 fits engines
    # whose arp programs live in high memory (Hawkeye $8xxx); engines with
    # low-memory arp programs (Adrenalin $19xx) lower it so valid pointers
    # aren't filtered out.
    arp_ptr_hi_min: int = 0x80
    # Auto-arpeggio from instrument fx3 bit 2 (engine A $7D9C): instruments with
    # fx3 bit 2 set run a fixed arp program every frame with NO pattern $7x
    # command. This is the arp-program INDEX they use (engine A hardcodes
    # program 1 @ $1973 = (0,+4,+7)). None = no fx3-bit-2 auto-arp (default;
    # Hawkeye/Cyb II drive arp only via the pattern $7x command).
    fx3_bit2_autoarp_index: Optional[int] = None
    # Whether fx3 bit 6 drives the wave-arp effect (cycles wavearp[] into the
    # ctrl/waveform). True for Hawkeye/Cyb II. Engine A (Adrenalin) does NOT
    # check fx3 bit 6 — that bit is dead in its instruments — so running the
    # wave-arp there spuriously clears the ctrl. Set False to disable it.
    fx3_bit6_wavearp: bool = True
    # Drum-kick (fx3 bit 7 noise_tick) release tail freq source. Hawkeye uses
    # the PRESERVED base shadow (lonotesto2/hinotesto2). Engine A (Adrenalin
    # $819F) reads the VIBRATO'D current shadow ($7a2b/$7a25, updated by the
    # vibrato at $7F65-$7F79), so its release tail keeps vibratoing. True =
    # use the current (vibrato'd) lonotesto/hinotesto.
    noise_tick_release_uses_vibrato: bool = False
    pulsetabel_addr: int = 0       # pulse-program data
    # Pulse-program byte format. 'tel' (default) = the Tel-variant 8-byte
    # program [lo,hi, 3×(thr,step)]. 'standard' = the vanilla FC player's
    # 4-byte program [thr_a, step1, thr_b, step2] (a ctr-keyed 2-threshold
    # step schedule; bounds $01/$0F hardcoded). See standard/RE_NOTES.md.
    pulse_prog_format: str = 'tel'
    # Filter-program byte format. 'tel' (default) = filterbytes_addr is a
    # 2-byte pointer table to 10-byte programs. 'standard' = the vanilla FC
    # player's ONE 12-byte program at filterbytes_addr: [6 cutoffs][6
    # thresholds] — a 6-band time-keyed cutoff envelope (band 0 absolute +
    # the $D417 res/routing write, bands 1-4 incremental, band 5 absolute
    # hold). See standard/RE_NOTES.md (filter $1E89 + the $2172 counter).
    filter_prog_format: str = 'tel'
    # Instrument-record byte layout. 'tel' (default) = waveform/fx1/fx2/fx3 at
    # +1/+5/+6/+7. 'standard' = vanilla FC: +5/+6/+7 are filter-sel/pulse-param/
    # effect-flags (NOT Tel fx); the standard decoder zeros fx1/2/3 so the
    # composer applies no Tel effects. See standard/RE_NOTES.md.
    instr_format: str = 'tel'
    # Pattern-stream byte dispatch. 'tel' (default) = the Tel-variant ranges
    # ($70-$7F instr, $C0-$DF wave-adjust, $F0 noglide, $F1 filter). 'standard'
    # = the vanilla FC player's parser ($18DD-$1957): $C0-$DF = instrument-select
    # (low 5 bits, 0-31), $F0-$FE = tie/no-retrigger prefix (next byte is the
    # note), $E0-$EF = 3-byte glide, $80-$BF = note-length, $00-$7F = note,
    # $FF = end. See standard/RE_NOTES.md (the foundational fix: the standard
    # player selects instruments via $Cx, which Tel decode misreads as a
    # wave-position nudge — leaving the wrong instrument's effects to corrupt
    # the freq stream).
    pattern_format: str = 'tel'
    # Standard-player VIBRATO-TAIL variant (one static byte at orig $2046):
    # variant $EB (Jarre_2) — vibrato-skipped instruments (fx1==0 / wave bit4 /
    # bit2) skip the freq write entirely; variant $DC (Prato) — they jump into
    # the vibrato's WRITE TAIL ($1ADC) and write the STALE global work regs
    # ($217C/$217D = the last vibrato computation, possibly another voice's)
    # to their freq lo,hi EVERY frame. True = the $DC behavior.
    std_vibrato_stale_tail: bool = False
    # Standard-player GLIDE-UP hi-write register (one static operand byte at
    # orig $1B3F): $01 (2739/2760 members) = the voice's freq hi, normal; $55
    # (20 members, e.g. Entrail_Ranx) = a hacked operand whose write lands on
    # SID-MIRRORED registers (($55+d4point) & $1F: V1→$15 cutoff-lo, V2→$1C,
    # V3→$03). Stored as the operand's low 5 bits; the composer emits
    # sta $D400+reg,y — mirror-equivalent to the orig's absolute target.
    std_glide_hi_reg: int = 0x01
    # Standard-player fx3-bit2 3-step ARPEGGIO (+$04 effect, orig $1D1E):
    # baked initial values of the 3-byte offset table at orig $1E86-$1E88.
    # Slots 1-2 are overwritten at runtime by every vibrato-skipped
    # instrument (the $2030 path: fx1 nibbles, or $0C/$18 when fx1==0);
    # slot 0 is static image data. Factory-probed.
    std_arp3_init: tuple = (0x00, 0x00, 0x01)
    # Standard-player $D416 write variant (the opcode at orig $1C78, the
    # filter chain's final SID write; the $2169,x shadow update before it is
    # never patched, so the band pipeline runs unchanged in all variants):
    #   'normal' ($8D, 2748/2760 members) — write the computed cutoff.
    #   'none'   ($EA, 8 members)         — the write is NOPed out.
    #   'const'  ($20 JSR to LDA #VV/STA/RTS, e.g. FBI_Crew_Intro_2 $10)
    #            — a hook overrides the value with std_d416_const.
    # Factory-probed; unrecognized hooks fall back to 'normal' with a warn.
    std_d416_mode: str = 'normal'
    std_d416_const: int = 0
    # If non-zero, write this value to $D418 at the TOP of every play frame
    # (before the voice loop), matching the vanilla FC player's $1833 vol write.
    # 0 = no top-of-frame vol write (Tel engines write vol elsewhere).
    vol_every_frame: int = 0
    # Standard wave-program pointer-table base ($1E3E in Jarre_2): 4 sub-tables
    # ctrl-lo(@base) / ctrl-hi(@base+?) / freq-lo / freq-hi, selected by an
    # instrument's wave nibble. 0 = no standard wave programs. See RE_NOTES.
    std_wave_ptr_addr: int = 0
    # Allocated (contiguous layout) addresses of the emitted wave-program
    # tables: ctrl[] and freq[] laid per selector at sel*16 stride. 0 until
    # the data-layout allocator assigns them.
    std_wave_ctrl_addr: int = 0
    std_wave_freq_addr: int = 0
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

    # Principled data tail. When True, the featuredriven composer emits the
    # patterns + pattern_ptr_table + sequences + seq_table from USF content
    # (into a fresh music-data block, pointers redirected there) instead of
    # carrying them verbatim from the orig binary. Aux tables (drumtabel,
    # filterbytes, ...) stay verbatim until their own phases. When False
    # (default), the whole data tail is verbatim.
    emit_data_from_usf: bool = False

    # SID load address. For the emit_data path the composer needs no orig file
    # at all, so the load address (also the init/play entry base) comes from
    # here instead of the PSID header. 0 = read it from orig (verbatim path).
    load_addr: int = 0

    # Song-init SID-write shape. The state setup (testbyte/speedbyte/seq-ptr
    # copy) is identical across styles; only the SID register-clear sequence
    # differs:
    #   'generic'        — Cyb II / Hawkeye: $D416=$FF, $D417=$00, $D418=$1F,
    #                      then ascending $00 silence of $D400-$D415.
    #   'fc_clear_sweep' — Adrenalin engine A ($7AE2): descending $D417..$D400
    #                      each written $01 then $00, then $D418=$0F, $D417=$00.
    #   'universal_reset' — pure trichotomy: OUR own clean silence-clear +
    #                      defensive test-bit phase clear + typed priming (the
    #                      init_master_vol / init_filter_* fields below). The
    #                      original engine's init write sequence is NOT
    #                      reproduced; only its end-of-init STATE is matched.
    init_style: str = 'generic'

    # Typed SID-chip PRIMING emitted by init_style='universal_reset' (the
    # trichotomy "priming" bucket — named musical params, not engine bytes).
    # Defaults reproduce the canonical reset state ($D418=$0F, no filter), so
    # an engine whose only priming is full volume needs nothing set. Engines
    # that prime the filter / a non-default master volume set these to their
    # original end-of-init register values (e.g. Cyb II: master_vol=$1F,
    # filter_cutoff_hi=$FF; Hawkeye: master_vol=$1F, filter_res_routing=$01).
    init_master_vol: int = 0x0F          # $D418 final value
    init_filter_cutoff_lo: int = 0x00    # $D415
    init_filter_cutoff_hi: int = 0x00    # $D416
    init_filter_res_routing: int = 0x00  # $D417

    # Repack the emit_data_from_usf data tables CONTIGUOUSLY from the first
    # data address instead of placing each at its original (extraction) address.
    # Needed when the original packs tables so tightly that emitting them at
    # their orig addresses overlaps (e.g. Adrenalin: pulsetabel/vibtabwait
    # collide with the instrument table) — overlapping CPU addresses can't map
    # to a flat load file, so xa65's backward `* =` desyncs file vs address and
    # the state region loads at the wrong place. Per the CORE TENET the rebuild's
    # data layout is free; only the writelog must match. Default False keeps the
    # proven fixed-address layout for Cyb II / Hawkeye (which don't overlap).
    contiguous_data_layout: bool = False

    # Per-path voice-loop mode constants (music_mode, sfx_mode) for the
    # emit_data song-init. Were read from mem[per_subtune_mode_addr] in the
    # verbatim path; for the de-verbatim path they come from here so the
    # composer needs no engine-mode bytes from orig. (2, 0) covers Hawkeye.
    song_init_modes: tuple = (2, 0)

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
