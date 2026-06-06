"""FC family asm composer — session 1 foundations.

Multi-session deliverable. This session establishes:

  - The xa65 pipeline (USF → ACME source → xa65 → object → PSID wrapper)
  - The ACME source structure (PSID header, code layout, data emitters)
  - A complete DATA-section emitter (freq table, instruments, sequences,
    patterns, per-subtune setup) from USF.
  - A placeholder for the ENGINE-CODE region: session 1 carries it
    verbatim from the original SID as `!fill` bytes.

Sessions 2-3 will replace the verbatim engine bytes with feature-driven
asm emitters (init/songout/playirq dispatch loop, h2/h3 byte-range
dispatch, pattern byte chain, effect chain). Session 4-5 extends for
Hawkeye's SMC dispatcher + SFX page records.

Per-SID asm regions for Cybernoid II:

  $A600..        engine entry vectors (init/songout/play)
  ...            zero-page allocation, per-voice state arrays
  ...            ok2/song/songout/uitzet/playirq + dispatch chain
  ...            verhoogtest, effect chain (vibrato/glide/pulse/filter/
                 drum/pulse-run/wave-arp/etc.)
  $AE3F          lonote (87 bytes freq lo)        ┐
  $AE96          hinote (87 bytes freq hi)        │ DATA SECTIONS
  $AEED          snelheid (per-subtune speed)     │ — emitted from USF
  $AEEF          seqtabel (per-subtune seq ptrs)  │
  $AEFB          seqloclo/seqlochi runtime slots  │
  $AF01          sequence (pattern_ptr_table)     │
  ...            wavearp/pulsearp/drumtabel/etc.  │
  $AFF4          pulsetabel (4 × 8 bytes)         │
  $B014          instrument records (19 × 8)      │
  ...            vibtabwait/startlen/starttabel   │
  ...            seq0a..seq0c, seq1a..seq1c       │
  ...            patterns st00..st20              ┘

Public entry:
    build_via_asm(cfg) -> bytes      # returns SID file bytes
"""
from __future__ import annotations

import os
import struct
import subprocess
import tempfile
from pathlib import Path

from src.usf import UsfFile, parse
from src.usf.types import MusicSubtune
from pipelines.future_composer.config import FCConfig
from pipelines.future_composer.composer import _load_sid_psid


_ROOT = str(Path(__file__).resolve().parents[2])
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')


# ---------------------------------------------------------------------------
# Data emitters — produce ACME `.byt` directives from USF content
# ---------------------------------------------------------------------------

def _emit_byte_list(label: str, bytes_seq, per_row: int = 12) -> str:
    """Emit `label\\n        .byt $XX,$YY,...` with row wrapping."""
    rows = [f'{label}']
    for i in range(0, len(bytes_seq), per_row):
        row = bytes_seq[i:i + per_row]
        rows.append('        .byt ' + ','.join(f'${b:02X}' for b in row))
    return '\n'.join(rows)


def _emit_freq_tables(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit lonote + hinote tables from USF freq_table (lo/hi interleaved
    192-byte form). Tunes with truncated tables emit only the populated
    entries — the original Cybernoid II has 87, not 96.
    """
    lo = []
    hi = []
    for i in range(cfg.freq_table_entries):
        lo.append(usf.freq_table[i * 2])
        hi.append(usf.freq_table[i * 2 + 1])
    out = [_emit_byte_list('lonote', lo)]
    out.append(_emit_byte_list('hinote', hi))
    return '\n\n'.join(out)


def _emit_snelheid(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit per-subtune speed bytes. Flat layout: 1 byte per USF
    subtune. SMC layout: music_subtune_count + 1 (shared SFX-default).
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if cfg.subtune_layout == 'flat_seqtabel':
        bytes_seq = [(s.tempo - 1) & 0xFF for s in music]
    elif cfg.subtune_layout == 'smc_template_with_sfx':
        bytes_seq = []
        sfx_speed = 0
        for s in music:
            if s.is_sfx:
                sfx_speed = (s.tempo - 1) & 0xFF
            elif s.id - 1 < cfg.music_subtune_count:
                bytes_seq.append((s.tempo - 1) & 0xFF)
        bytes_seq.append(sfx_speed)
    else:
        raise ValueError(f'unknown subtune_layout: {cfg.subtune_layout!r}')
    return _emit_byte_list('snelheid', bytes_seq)


def _emit_instruments(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit 8-byte per-instrument records starting at the `pulsehi`
    label (= instr_records_addr). Slots 0..instr_count-1; USF skips
    all-zero instruments so we fill missing slots with zeros.

    v1: the 4 effect bytes are recomposed from the USF Instrument's
    decomposed fields via `fx_bytes_from_inst`.
    """
    from pipelines.future_composer.to_usf import fx_bytes_from_inst
    slot_to_inst = {i.id - 1: i for i in usf.instruments}
    out = ['pulsehi = * + 0',
           'waveform = * + 1',
           'attdec = * + 2',
           'susrel = * + 3',
           'filcount = * + 4',
           'fx1 = * + 5',
           'fx2 = * + 6',
           'fx3 = * + 7']
    for slot in range(cfg.instr_count):
        inst = slot_to_inst.get(slot)
        if inst is None:
            row = [0] * 8
        else:
            pulse_hi = inst.waveform[0] if inst.waveform else 0
            ctrl     = inst.waveform[1] if len(inst.waveform) > 1 else 0
            fil_count, fx1, fx2, fx3 = fx_bytes_from_inst(inst)
            row = [pulse_hi, ctrl, inst.adsr[0], inst.adsr[1],
                   fil_count, fx1, fx2, fx3]
        out.append('        .byt ' + ','.join(f'${b:02X}' for b in row)
                   + f'  ; inst {slot}')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Engine code region — session 1 placeholder
# ---------------------------------------------------------------------------
#
# Session 1 carries the engine code verbatim from the original SID as
# `!fill N, $XX` (one byte at a time, since ACME's !fill is
# value-uniform). For Cybernoid II the engine region is roughly
# load_addr..freq_lo_addr-1 (everything before the data section). The
# verbatim region also includes the aux tables (wavearp, pulsearp,
# drumtabel, arp programs, filterbytes, pulsetabel) that sit between
# pattern_ptr_table and the instrument records — session 1 doesn't
# yet emit those as USF-derived either.
#
# Sessions 2-3 incrementally replace this with feature-driven asm
# emitters.

# ---------------------------------------------------------------------------
# Engine-code emitters — feature-driven (session 3+ asm composer)
# ---------------------------------------------------------------------------
#
# These emitters produce engine routines from USF features rather than
# carrying HVSC's verbatim bytes. The composer chooses its own layout;
# verification shifts from md5-exact to writelog frame-exact via
# `pipelines.future_composer.verify.verify_asm`.

# FC engine state — fixed RAM allocations the engine reads/writes during
# play. Addresses are the composer's choice; routines reference these
# labels and the assembler resolves them. Sessions 4+ will lay them out
# as a contiguous block at the end of the engine code region.

_FC_STATE_LABELS = """
; --- engine state ---
; testbyte: gates the play loop. 0 = playing, 1 = halted.
; song / songout / ok2 set it; playirq's first instruction tests it.
testbyte:       .dsb 1, 1            ; init to halted

; speedbyte: per-subtune tempo (frames per sequence step). song sets
; this from snelheid,X; playirq reloads speedsto from it.
speedbyte:      .dsb 1, 0
speedsto:       .dsb 1, 0

; st2: scratch — current sequence byte under dispatch in h3.
st2:            .dsb 1, 0

; st: scratch — used by the drum routine for the tone-byte read.
st:             .dsb 1, 0

; Vibrato shared scratch (NOT per-voice; reloaded each frame).
vibreallo:      .dsb 1, 0
vibrealhi:      .dsb 1, 0
templono:       .dsb 1, 0
temphino:       .dsb 1, 0

; Glide shared scratch (NOT per-voice; transient per-frame state).
glideslo:       .dsb 1, 0          ; 16-bit delta lo (then divisor)
glideshi:       .dsb 1, 0          ; 16-bit delta hi (then divisor)
glide_glen:     .dsb 1, 0          ; glidedelay hi nibble cached
glide_bran:     .dsb 1, 0          ; same — used as the long-div shift
glide_denom:    .dsb 1, 0          ; bran * (speedbyte+1)
glide_dir:      .dsb 1, 0          ; 0 = down (subtract), 1 = up (add)

; filwhat: shared scratch — last voice index that ran fx_filter_prog.
; Non-filter-prog voices check this to skip filter cleanup if they
; aren't the "owning" voice. Lives outside ok2's clear range so it
; persists across song init.
filwhat:        .dsb 1, 0

; d4point: per-voice SID register offset (V1=$00, V2=$07, V3=$14).
; Constant table, X-indexed.
d4point:        .byt $00, $07, $0E

; Per-voice 3-byte state arrays.
pulseruntest:   .dsb 3, 0            ; song sets to 1,1,1
tabcount:       .dsb 3, 0            ; sequence step (per voice)
begcount:       .dsb 3, 0            ; pattern offset (within current pat)
nootcount:      .dsb 3, 0            ; frames until next note
nootleng:       .dsb 3, 0            ; current note length
noho:           .dsb 3, 0            ; base pitch (before transpose)
noothoogt:      .dsb 3, 0            ; current pitch index
counter2:       .dsb 3, 0            ; global tick counter
toneadd:        .dsb 3, 0            ; per-voice transpose (from $80-$FF seq)
voiceinc:       .dsb 3, 0            ; per-voice wave-table inc (from $60-$7F)
repeatsto:      .dsb 3, 0            ; per-voice pattern-repeat ctr (from $40-$5F)
wavecount:      .dsb 3, 0            ; instrument index per voice (from $C0-$DF)
wavesto:        .dsb 3, 0            ; stored waveform byte
newnote:        .dsb 3, 0            ; new-note flag (set by $F0 noglide)
glidetest:      .dsb 3, 0            ; glide active flag
glidetest2:     .dsb 3, 0            ; glide secondary
vibcounter:     .dsb 3, 0            ; vibrato delay counter
vibstore1:      .dsb 3, 0            ; per-voice vibrato LFO step
vibstore2:      .dsb 3, 0            ; per-voice vibrato direction
vibstore3:      .dsb 3, 0            ; per-voice vibrato counter
tempglide:      .dsb 3, 0            ; glide target
glidedelay:     .dsb 3, 0            ; glide delay
tonearpcounter: .dsb 3, 0            ; tone-arp counter
arpieoklo:      .dsb 3, 0            ; arpeggio program ptr lo
arpieokhi:      .dsb 3, 0            ; arpeggio program ptr hi
lonotesto:      .dsb 3, 0            ; freq lo shadow (for vibrato later)
lonotesto2:     .dsb 3, 0            ; freq lo shadow 2 (preserved freq —
                                     ; used by Hawkeye noise-tick release
                                     ; to restore the note's original pitch
                                     ; after the drum-kick frames, parallel
                                     ; to hinotesto2 / orig $90E3)
hinotesto:      .dsb 3, 0            ; freq hi shadow
hinotesto2:     .dsb 3, 0            ; freq hi shadow 2
freq_rise_acc:  .dsb 3, 0            ; bit-2 sweep accumulator (orig $90E0)
                                     ; — INCs each odd counter2 frame when
                                     ; inst.filter_prog.freq_hi_rise is set;
                                     ; the PRE-INC value is written to
                                     ; hinotesto + d401 (slow upward freq
                                     ; creep). Init by nolengset to hinote.
pulsehitemp:    .dsb 3, 0
pulsestolo:     .dsb 3, 0
pulsehisto:     .dsb 3, 0
pulsetest:     .dsb 3, 0
pulsecountup:   .dsb 1, 0            ; shared scratch — pulse_prog step value
                                     ; (NOT per-voice; reloaded each frame)

; fx_pulse_run per-voice state (orig $a69f/$a6a2/$a6a5 in Cyb II).
; Kept SEPARATE from pulsestolo/pulsehisto: pulse_prog and pulse_run
; both touch the d402/d403 shadow each frame but each maintains its
; own state. On first-frame init, pulserun_hi seeds from pulsehisto
; (pulse_prog's hi state) — see fx_pulse_run.
pulserun_flag:   .dsb 3, 0
pulserun_acc:    .dsb 3, 0            ; pulse_run accumulator (orig $a6a2)
pulserun_hi:     .dsb 3, 0            ; pulse_run hi shadow (orig $a6a5)

filtercount:    .dsb 3, 0
filter:         .dsb 3, 0            ; per-voice filter cutoff shadow
                                     ; (written by fx_filter_prog / fm2 →
                                     ;  $D416)
stod404:        .dsb 3, 0            ; per-voice $D404 output byte
byteand:        .dsb 3, 0            ; per-voice $D404 AND mask
                                     ; (drum routine sets $FE; default $FF)

; Per-voice shadow SID registers (nextvoice writes these to $D400-$D403)
d400:           .dsb 3, 0            ; shadow $D400 (freq lo)
d401:           .dsb 3, 0            ; shadow $D401 (freq hi)
d402:           .dsb 3, 0            ; shadow $D402 (pw lo)
d403:           .dsb 3, 0            ; shadow $D403 (pw hi)

; End-of-state marker — ok2's clear loop runs from tabcount to here.
; ANYTHING THAT MUST SURVIVE ok2 GOES AFTER THIS MARKER (the song
; routine writes seqloclo/seqlochi BEFORE calling ok2; if those were
; inside the clear range, ok2 would wipe them — bug from session 3).
state_end:

; seqloclo / seqlochi: the current song's 3 voice sequence-stream
; pointers, copied from seqtabel by song init. Placed AFTER state_end
; so ok2's clear loop doesn't touch them (the song writes them before
; jsr ok2 returns).
seqloclo:       .dsb 3, 0
seqlochi:       .dsb 3, 0
"""


# Zero-page slot equates — these must live in $00-$FF for (zp),Y indirect
# addressing to work. ZP $40-$7F is the conventional FC range; pre-PSID
# environment is responsible for not stomping on these.
_FC_ZP_EQUATES = """
; --- zero-page equates ---
fx1sto     = $40           ; cached fx1 byte (vibrato params) for current voice
fx2sto     = $41           ; cached fx2 byte (pulse program + strange filter)
fx3sto     = $42           ; cached fx3 byte (8 effect-flag bits)
tabbytsto  = $43           ; current pattern byte under dispatch
seqptr_lo  = $44           ; sequence-stream indirect pointer lo
seqptr_hi  = $45           ; sequence-stream indirect pointer hi
zp3        = $46           ; pattern indirect pointer lo
zp4        = $47           ; pattern indirect pointer hi
wax        = $48           ; current voice index (0..2) during play
voicesto   = $49           ; current voice's $D400 offset (0/7/14)
denom      = $4B           ; scratch for arp setup

; Drum-routine ZP indirect ptrs (replaces ACME source's SMC dwalo/dtalo)
drum_dwa_lo = $4C          ; drum wave-program ptr lo
drum_dwa_hi = $4D           ; drum wave-program ptr hi
drum_dto_lo = $4E          ; drum tone-program ptr lo
drum_dto_hi = $4F           ; drum tone-program ptr hi
drum_dl     = $50          ; drum length scratch

; Filter-program ZP indirect (matches ACME source's zer0fillo/zer0filhi
; semantics). Used by fx_filter_prog to read fb<n> program bytes.
zer0fillo  = $51           ; filter program indirect ptr lo
zer0filhi  = $52           ; filter program indirect ptr hi

; Tone-arp ZP indirect (replaces ACME source's SMC arpieoklo1/2 slots).
; Loaded from arpieoklo,X/arpieokhi,X each frame.
ta_arp_lo  = $53           ; tone-arp program indirect ptr lo
ta_arp_hi  = $54           ; tone-arp program indirect ptr hi

; Pulse-program ZP scratch (replaces ACME source's SMC slots:
; pulsecountlo/pulsecounthi/purepbyte). Loaded fresh each frame
; when fx_pulse_prog runs.
pp_count_lo  = $55         ; lower bound for the bounce check
pp_count_hi  = $56         ; upper bound for the bounce check
pp_purepbyte = $57         ; wrap flag (1 = snap to lo, 0 = bounce)

; Vibrato ZP scratch
vibrasto    = $4A          ; amplitude/depth countdown (matches ACME)
vibwait_zp  = $58          ; cached vibtabwait[wavecount] (replaces
                            ; ACME's SMC vibwait slot)
"""


def _emit_song_init_routine(cfg: FCConfig) -> str:
    """Emit the song init routine + songout + ok2 + silence-all.

    Called via PSID init=$LOAD with X = song number. Initializes engine
    state for the selected subtune and silences the SID. Falls through
    from song into silence-all (the ACME `uitzet` label).

    Routine boundaries (each one a callable / branch target):
      song:        from PSID init; sets state, copies seq pointers,
                   primes $D416/$D417/$D418, calls ok2, falls into
                   silence-all.
      silence_all: writes 0 to $D400-$D415 (22 SID registers).
      songout:     marks engine halted; falls into silence-all.
      ok2:         zeros all per-voice state arrays (between tabcount
                   and the end of the state region).

    Frame-exact-visible SID writes during init (in order):
      $D416 ← $00, $D417 ← $01, $D418 ← $10|VOLUME, then 22× ($D4xx ← $00)
    plus whatever the first play() invocation writes (frame 0 in the
    writelog combines init+play).

    Uses straight code (not the ACME source's SMC trick) because
    frame-exact comparison only cares about $D4xx writes; CPU internals
    are free.
    """
    if cfg.subtune_layout == 'smc_template_with_sfx':
        return _emit_song_init_smc(cfg)
    if cfg.subtune_layout != 'flat_seqtabel':
        raise ValueError(f'unknown subtune_layout: {cfg.subtune_layout!r}')

    snelheid_addr = cfg.per_subtune_speed_addr
    seqtabel_addr = cfg.seqtabel_addr

    return f"""
; --- song init ($LOAD entry; A = subtune number) ---
; Initializes engine state for the selected subtune. Frame-exact SID
; writes: $D416/$D417 cleared, $D418 = $10|VOLUME, then $D400-$D415
; silenced via the fall-through into silence_all.
song:
        tax                          ; X = subtune number (PSID passes
                                     ; the subtune index in A; the
                                     ; whole song body uses X-indexed
                                     ; lookups so move it now)
        ; testbyte = 1 (halted), pulseruntest[0..2] = 1
        lda #1
        sta testbyte
        sta pulseruntest+0
        sta pulseruntest+1
        sta pulseruntest+2

        ; speedbyte = snelheid[X]
        lda ${snelheid_addr:04X},x
        sta speedbyte

        ; Compute Y-index into seqtabel for subtune X: idx = X*6 + 5
        ; (we copy 6 bytes downward into seqloclo[0..2]/seqlochi[0..2])
        ; Straight code, no SMC trick.
        stx song_tmp
        txa
        asl                          ; *2
        clc
        adc song_tmp                 ; *3
        asl                          ; *6
        adc #5                       ; *6 + 5
        tax

        ldy #5
song_seqcp:
        lda ${seqtabel_addr:04X},x
        sta seqloclo,y               ; seqloclo+0..2, seqlochi+0..2 are
                                     ; contiguous so Y=0..5 covers both
        dex
        dey
        bpl song_seqcp

        ; Filter setup + master volume. After the seqtabel loop, Y=$FF
        ; (the BPL exits when DEY underflows). HVSC writes Y to $D416
        ; ($FF = max cutoff lo), then INY (Y=$00), then writes Y to
        ; $D417 ($00 = filter off / no resonance). This matches what
        ; the frame-exact writelog captures from the original.
        sty $d416                    ; Y=$FF → $D416 ← $FF
        iny
        sty $d417                    ; Y=$00 → $D417 ← $00
        lda #$10 | VOLUME_INIT
        sta $d418                    ; $D418 ← $1F

        jsr ok2
        ; falls through into silence_all (init silences $D400-$D415)

silence_all:
        lda #0
        ldx #$15
silence_loop:
        sta $d400,x
        dex
        bpl silence_loop
        rts

songout:
        lda #1
        sta testbyte
        ; fall through into silence_all
        jmp silence_all

; ok2 — zero every byte from tabcount through the end of the engine
; state arrays, then reset the X-indexed counter2/tabcount/begcount/
; nootcount/noho per-voice arrays explicitly.
ok2:
        lda #0
        ldx #state_end - tabcount - 1
ok2_zero:
        sta tabcount,x
        dex
        bpl ok2_zero

        ; Per-voice arrays reset (overlaps the above for clarity)
        ldx #2
ok2_pv:
        sta tabcount,x
        sta begcount,x
        sta nootcount,x
        sta noho,x
        sta counter2,x
        dex
        bpl ok2_pv

        sta testbyte
        rts

song_tmp: .dsb 1, 0
"""


def _emit_song_init_smc(cfg: FCConfig) -> str:
    """Song init for SMC-template-with-SFX layout (Hawkeye).

    On entry, A holds the subtune number (PSID convention).
    Dispatches between two paths based on A vs music_subtune_count:

      MUSIC PATH (A < music_subtune_count):
        speedbyte = per_subtune_speed_addr[A]
        record at: (template_base_hi << 8) | per_subtune_smc_addr[A]
        Records are 6 bytes (lo*3, hi*3) for the 3 voice sequence ptrs.

      SFX PATH (A >= music_subtune_count):
        speedbyte = per_subtune_speed_addr[music_subtune_count]
                    (all SFX subtunes share one speed slot;
                     dispatcher forces X = music_count for SFX)
        record at: (sfx_page_base + (A - music_count) * sfx_page_stride)
                   * 256
        Same 6-byte record format at page boundary.

    Same shared code afterward as the flat_seqtabel path:
      $D416/$D417/$D418 setup → jsr ok2 → silence_all.
    """
    snelheid_addr = cfg.per_subtune_speed_addr
    smc_addr      = cfg.per_subtune_smc_addr
    mode_addr     = cfg.per_subtune_mode_addr
    music_count   = cfg.music_subtune_count
    template_hi   = cfg.template_base_hi
    sfx_pg_stride = cfg.sfx_page_stride
    # If data is shifted, SFX records also move. Bake shift's hi+lo into
    # the SFX-page-base lookup so seqptr_hi/seqptr_lo land on the
    # actually-emitted SFX record address.
    shift = cfg.featuredriven_addr_shift
    sfx_pg_base   = (cfg.sfx_page_base + (shift >> 8)) & 0xFF
    sfx_pg_offset = shift & 0xFF
    # Pre-emit the SFX stride multiplier as a sequence of ASLs (only
    # works for stride being a power of 2; Hawkeye stride=2 → 1 asl).
    if sfx_pg_stride == 1:
        stride_asm = ''
    elif sfx_pg_stride == 2:
        stride_asm = '        asl'
    elif sfx_pg_stride == 4:
        stride_asm = '        asl\n        asl'
    else:
        raise NotImplementedError(
            f'sfx_page_stride {sfx_pg_stride} not handled '
            f'(non-power-of-2 needs a multiply loop)')

    return f"""
; --- song init ($LOAD entry; A = subtune number) ---
; SMC-template-with-SFX layout (Hawkeye family). Dispatches between
; music subtunes (A < {music_count}) and SFX subtunes (A >= {music_count}).
; See _emit_song_init_smc docstring for the per-path semantics.
song:
        tax                          ; X = subtune number
        lda #1
        sta testbyte
        sta pulseruntest+0
        sta pulseruntest+1
        sta pulseruntest+2

        cpx #{music_count}              ; music_subtune_count
        bcs song_sfx_path

        ; --- MUSIC PATH ---
        lda ${snelheid_addr:04X},x
        sta speedbyte
        lda ${mode_addr:04X},x         ; per-subtune voice-loop mode byte
        sta voice_loop_start
        lda ${smc_addr:04X},x          ; SMC template lo for this subtune
        sta seqptr_lo                ; reuse seqptr ZP as the indirect ptr
        lda #${template_hi:02X}
        sta seqptr_hi
        jmp song_copy_seqs

song_sfx_path:
        ; X = music_count + sfx_idx. SFX uses the mode-byte at
        ; per_subtune_mode_addr[music_count] (same fixed slot for all SFX),
        ; matching orig's JSR $7B5A music init with forced X=music_count.
        ldy #{music_count}
        lda ${snelheid_addr:04X},y
        sta speedbyte
        lda ${mode_addr:04X},y         ; SFX shares the music_count slot's mode
        sta voice_loop_start
        txa
        sec
        sbc #{music_count}              ; A = sfx_idx
{stride_asm}                              ; A *= sfx_page_stride
        clc
        adc #${sfx_pg_base:02X}        ; A = SFX page (includes shift>>8)
        sta seqptr_hi
        lda #${sfx_pg_offset:02X}     ; SFX page low-byte offset (shift&$FF)
        sta seqptr_lo

        ; SFX 3-copy: SFX page contains 6+20+256 = 282 bytes of
        ; per-subtune data the engine reads at runtime. Orig populates
        ; runtime areas $7B2C..$7B31, $8475..$8488, $8FC5..$90C4 by
        ; copying from the SFX page. We do the same here so mine reads
        ; SFX-specific data when walking V1.
        ; Copy 2: 20 bytes ($SFX_page+6) → pattern_ptr_table+$6C (SFX
        ; pattern-pointer extension area). The +sfx_pg_offset accounts
        ; for the SFX page offset within a 256-byte page (= shift & $FF
        ; for shifted layouts; 0 otherwise).
        lda #(6 + ${sfx_pg_offset:02X})
        sta seqptr_lo
        ldy #$13
sfx_copy2:
        lda (seqptr_lo),y
        sta pattern_ptr_table+$6C,y
        dey
        bpl sfx_copy2
        ; Copy 3: 256 bytes ($SFX_page+$1A) → sfx_seq_stream destination.
        lda #($1A + ${sfx_pg_offset:02X})
        sta seqptr_lo
        ldy #0
sfx_copy3:
        lda (seqptr_lo),y
        sta sfx_seq_stream,y
        dey
        bne sfx_copy3
        ; Restore seqptr_lo = sfx_pg_offset for the 6-byte seq pointer
        ; copy below (song_copy_seqs reads (seqptr_lo, seqptr_hi) =
        ; SFX_page+0 in the shifted layout).
        lda #${sfx_pg_offset:02X}
        sta seqptr_lo

song_copy_seqs:
        ; Copy 6 bytes from (seqptr),Y to seqloclo+Y for Y=0..5.
        ; seqloclo / seqlochi are contiguous in state; Y=0..2 hits
        ; seqloclo[0..2], Y=3..5 hits seqlochi[0..2].
        ldy #5
song_seqcp:
        lda (seqptr_lo),y
        sta seqloclo,y
        dey
        bpl song_seqcp

        ; Hawkeye's init goes straight to silence then writes
        ; $D418=$FF and $D417=$00 AFTER the silence loop. NOT the
        ; Cybernoid II preamble; instead a post-silence cleanup.
        jsr ok2
        jsr silence_all              ; jsr (not fall-through) — we need
                                     ; to continue with more writes
        ; Hawkeye-specific: post-silence master vol + filter routing.
        lda #$FF
        sta $d418
        lda #$00
        sta $d417
        rts

songout:
        ; Hawkeye songout at orig $7BFC-$7C0C: silence only the three
        ; voice control regs ($D404/$D40B/$D412), set testbyte = $02.
        ; Note: orig writes #$02 (NOT #$01) to its testbyte equivalent
        ; ($7B99) — the play loop's `bne` test sees any non-zero as
        ; halted, but the chip-state writelog is what we match.
        lda #$02
        sta testbyte
        lda #$00
        sta $d404                    ; V1 ctrl = 0
        sta $d40b                    ; V2 ctrl = 0
        sta $d412                    ; V3 ctrl = 0
        rts

silence_all:
        ; Init-time SID reset (Hawkeye orig $7B82-$7B97): for each
        ; register $D400-$D417, write $01 then $00. Two-write strobe
        ; per register. This is the INIT pattern, NOT songout —
        ; songout has its own minimal silencing above.
        ldx #$17                     ; covers $D400 + $00..$17 = $D400-$D417
silence_loop:
        lda #$01
        sta $d400,x
        lda #$00
        sta $d400,x
        dex
        bpl silence_loop
        rts

ok2:
        lda #0
        ldx #state_end - tabcount - 1
ok2_zero:
        sta tabcount,x
        dex
        bpl ok2_zero

        ldx #2
ok2_pv:
        sta tabcount,x
        sta begcount,x
        sta nootcount,x
        sta noho,x
        sta counter2,x
        dex
        bpl ok2_pv

        sta testbyte
        rts

; SMC-layout per-voice loop initial X. Music subs set to mode_addr[X];
; SFX subs share mode_addr[music_count]. Single byte of state — only
; allocated for SMC layout (flat layout uses hardcoded `ldx #2`).
voice_loop_start: .dsb 1, 2
"""


def _emit_nextvoice_writes(write_order: tuple, use_byteand_mask: bool = True,
                            skip_pw: bool = False) -> str:
    """Emit the per-voice shadow→SID write block in the order given by
    `write_order` (tuple of register offsets 0-4 within the voice).

    Per the SID-internal-state research, within-frame write order IS
    musically significant (gate edges trigger envelope retriggers, test
    bit resets oscillator + noise LFSR, ADSR delay bug, $D418 clicks).
    Different FC-family engines use different orders — each cfg
    declares its convention.

    `skip_pw=True` (used by interleaved-layout's h10b shortcut) omits
    offsets 2 and 3 (PW lo, PW hi) — these were already written in the
    EARLY phase of the chain. Mirrors Hawkeye's $830C late-write trio
    of CTRL/FREQ LO/FREQ HI when the new-note path jumps via $7DBA.
    """
    chunks = []
    for offset in write_order:
        if skip_pw and offset in (2, 3):
            continue
        if offset == 0:
            chunks.append('        lda d400,x\n'
                          '        sta $d400,y                  ; freq lo')
        elif offset == 1:
            chunks.append('        lda d401,x\n'
                          '        sta $d401,y                  ; freq hi')
        elif offset == 2:
            chunks.append('        lda d402,x\n'
                          '        sta $d402,y                  ; pw lo')
        elif offset == 3:
            chunks.append('        lda d403,x\n'
                          '        sta $d403,y                  ; pw hi')
        elif offset == 4:
            if use_byteand_mask:
                chunks.append('        lda stod404,x\n'
                              '        and byteand,x                ; drum gate-off mask\n'
                              '        sta $d404,y                  ; ctrl (waveform + gate)')
            else:
                chunks.append('        lda stod404,x\n'
                              '        sta $d404,y                  ; ctrl (waveform + gate)')
        else:
            raise ValueError(
                f'invalid nextvoice_write_order offset {offset}; '
                f'expected 0..4')
    return '\n'.join(chunks)


def _emit_fx_pulse_run(cfg: FCConfig) -> str:
    """Emit fx_pulse_run body per cfg.pulse_run_style.

    'disabled' — no-op (just the fx3 bit check that falls through).
    'cyb2'     — Cyb II's $ACE4-$AD24 logic: per-voice accumulator +=
                 pulserunspeed each frame; written to pulsestolo. pwhi
                 shadow walks with overflow wrap (CMP upper / EOR wrap).
    """
    if cfg.pulse_run_style == 'disabled':
        return ('        ; STUB: fx_pulse_run disabled per cfg\n'
                '        lda fx3sto\n'
                '        and #$02\n'
                '        beq fx_double_voice\n'
                '        ; fall through (no-op)')
    if cfg.pulse_run_style == 'cyb2':
        return """        ; Cyb II fx_pulse_run: PW sweep at pulserunspeed.
        ; Mirrors orig $ACE4-$AD24. Maintains SEPARATE state from
        ; pulse_prog: pulserun_acc/pulserun_hi (vs pulsestolo/pulsehisto).
        ; Both routines write to the shared d402/d403 shadows; pulse_run
        ; runs AFTER pp_store so its shadow writes win for this frame.
        ;   bit clear → set per-voice flag (= "init next time bit goes on")
        ;   bit set + flag set   → first-frame init: clear flag + acc,
        ;                          seed pulserun_hi from pulsehisto
        ;   bit set + flag clear → step: acc+=spd; on carry, walk pulserun_hi
        lda fx3sto
        and #$02
        beq fx_pulse_run_set_flag
        ldx wax
        lda pulserun_flag,x
        beq fx_pulse_run_step
        lda pulsehisto,x             ; seed pulserun_hi from pulse_prog
        sta pulserun_hi,x
        lda #0
        sta pulserun_flag,x
        sta pulserun_acc,x
fx_pulse_run_step:
        lda pulserun_acc,x
        clc
        adc #pulserunspeed
        sta pulserun_acc,x
        sta d402,x                   ; shadow d402
        bcc fx_pulse_run_sync_pwhi   ; no carry → skip inc/wrap, still
                                     ; need to write d403 (orig $AD1F
                                     ; is unconditional)
        inc pulserun_hi,x
        lda pulserun_hi,x
        cmp #pulserun_pwhi_upper
        bne fx_pulse_run_sync_pwhi
        eor #pulserun_pwhi_wrap_xor
        sta pulserun_hi,x
fx_pulse_run_sync_pwhi:
        lda pulserun_hi,x            ; ALWAYS load pulserun_hi (orig $AD1C)
        sta d403,x                   ; ALWAYS write shadow (orig $AD1F)
        jmp fx_double_voice
fx_pulse_run_set_flag:
        ldx wax
        lda #1
        sta pulserun_flag,x"""
    raise ValueError(f'unknown pulse_run_style: {cfg.pulse_run_style!r}')


def _emit_fx_noise_tick(cfg: FCConfig) -> str:
    """Emit fx_noise_tick body per cfg.noise_tick_style.

    'cyb2_table'        — Cyb II's per-instrument startlen/starttabel
                          lookup, writing noisehitone $FA when attack
                          byte bit 7 set.
    'hawkeye_constants' — Hawkeye's drum-kick at orig $82D4-$82F0.
                          Triggered by fx3 bit 7. For counter2 in [0..1]:
                          ctrl=$81 (noise+gate), freq=$0058. For
                          counter2 in [2..3]: ctrl=wavesto&$FE (release,
                          gate cleared), freq restored from lonotesto/
                          hinotesto. Beyond counter2=3: done. Mode 1
                          equivalent of orig.
    'disabled'          — no-op (label only, falls through to
                          effect_chain_end).
    """
    if cfg.noise_tick_style == 'disabled':
        return (
            'fx_noise_tick:\n'
            "        ; disabled per cfg — falls through to effect_chain_end\n"
        )
    if cfg.noise_tick_style == 'hawkeye_constants':
        # Tight encoding to mirror orig $82D4-$82F0's 51-byte footprint.
        # `effect_chain_end` follows immediately — branches/exits use it
        # as the fall-through target to save the hk_nt_done label.
        return """fx_noise_tick:
        ; Hawkeye drum-kick (orig $82D4-$82F0). fx3 bit 7 triggers a
        ; 4-frame drum-kick + release effect:
        ;   counter2 in [0..1]: ctrl=$81 (noise+gate), freq=$0058
        ;   counter2 in [2..3]: ctrl=wavesto&$FE (release), freq from
        ;                       lonotesto/hinotesto
        ;   counter2 >= 4:      done (fall through)
        lda fx3sto
        bpl effect_chain_end          ; bit 7 clear → skip (orig $82D6)
        ; X is already wax (preserved through fx_double_voice + fx_drum's
        ; BEQ fall-through path; neither clobbers X). Save 2 bytes by not
        ; reloading. Verified in the chain order section.
        lda counter2,x
        cmp #$02
        bcs hk_nt_release             ; counter2 >= 2 → release path

        ; counter2 < 2: drum kick (orig $82DF-$82EE)
        lda #$58
        sta d401,x
        lda #$00
        sta d400,x
        lda #$81
        sta stod404,x
        bne effect_chain_end          ; always taken ($81 ≠ 0)

hk_nt_release:
        cmp #$04
        bcs effect_chain_end          ; counter2 >= 4 → done
        ; counter2 in [2..3]: release (orig $82F5-$8306). Uses the
        ; PRESERVED freq shadows (lonotesto2/hinotesto2) so the
        ; drum-kick "release tail" restores the original note pitch,
        ; not any vibrato/glide-modulated current value. Orig reads
        ; $90E3 (lonotesto2 equiv) and $90DD (hinotesto2 equiv).
        lda lonotesto2,x
        sta d400,x
        lda hinotesto2,x
        sta d401,x
        lda wavesto,x
        and #$FE
        sta stod404,x
        ; falls through to effect_chain_end"""
    if cfg.noise_tick_style == 'cyb2_table':
        return """fx_noise_tick:
        ; fx3 bit $80 — pre-attack waveform for the first N frames of
        ; a note, where N = startlen[wavecount]. Writes the attack
        ; waveform from starttabel[wavecount] into stod404. If the
        ; waveform's high bit is set (noise-y), also writes
        ; noisehitone ($FA) to d401 to fix the pitch.
        ;
        ; After startlen frames, has a 2-frame transition window
        ; (counter2 == startlen or startlen+1) where it restores
        ; lonotesto/hinotesto/wavesto into d400/d401/stod404 —
        ; i.e., the "real" note settings load. After startlen+1,
        ; noise_tick is done and the held-note steady state takes
        ; over.
        ;
        ; Last effect in the chain; falls through to effect_chain_end.
        lda fx3sto
        and #$80
        beq effect_chain_end

        ldy wavecount,x
        lda counter2,x
        cmp startlen,y
        bcs nt_nv3                   ; counter2 >= startlen → transition/done

        ; counter2 < startlen — attack phase
        lda starttabel,y
        cmp #$7F
        bcc nt_nve                   ; waveform < $7F → use directly

        ; waveform >= $7F (noise-y) — also force pitch to noisehitone
        lda #$FA                     ; noisehitone
        sta d401,x
        lda #$81                     ; use noise+gate as waveform
        jmp nt_nve

nt_nv3:
        ; counter2 >= startlen — check if we're in the 2-frame
        ; transition window (startlen or startlen+1).
        lda startlen,y
        clc
        adc #2
        sta st2                      ; scratch: startlen+2
        lda counter2,x
        cmp st2
        bcs effect_chain_end         ; counter2 >= startlen+2 → done

        ; transition frame — restore "real" note values into shadows
        lda lonotesto,x
        sta d400,x
        lda hinotesto,x
        sta d401,x
        lda wavesto,x
nt_nve:
        sta stod404,x
        ; falls through to effect_chain_end"""
    raise ValueError(f'unknown noise_tick_style: {cfg.noise_tick_style!r}')


def _emit_pw_writes_inline() -> str:
    """Emit V1 PW lo + PW hi writes (used by 'interleaved' voice loop layout).

    Mirrors Hawkeye disassembly $80F1-$80FA: PW shadows are written
    early in the per-voice loop, before wave_arp / pulse_arp / etc.
    can override them.
    """
    return (
        '        ; --- interleaved layout: PW writes (early) ---\n'
        '        ldx wax\n'
        '        ldy voicesto\n'
        '        lda d402,x\n'
        '        sta $d402,y                  ; PW lo (early)\n'
        '        lda d403,x\n'
        '        sta $d403,y                  ; PW hi (early)\n'
    )


def _emit_ctrl_freq_writes_inline(use_byteand_mask: bool = True) -> str:
    """Emit CTRL + FREQ lo + FREQ hi writes (used by 'interleaved' layout).

    Mirrors Hawkeye disassembly $830C-$831D: ctrl/freq shadows are
    written LATE in the per-voice loop, after all effects have settled.
    `use_byteand_mask` controls whether the drum gate-off mask
    `byteand,x` is ANDed in (Cyb II yes; Hawkeye no — Hawkeye clears
    the gate via stod404 itself in the held-note path at $7DCA).
    """
    ctrl_write = (
        '        lda stod404,x\n'
        '        and byteand,x                ; drum gate-off mask\n'
        '        sta $d404,y                  ; ctrl (waveform + gate)\n'
        if use_byteand_mask else
        '        lda stod404,x\n'
        '        sta $d404,y                  ; ctrl (waveform + gate)\n'
    )
    return (
        '        ; --- interleaved layout: CTRL + FREQ writes (late) ---\n'
        '        ldx wax\n'
        '        ldy voicesto\n'
        + ctrl_write +
        '        lda d400,x\n'
        '        sta $d400,y                  ; freq lo\n'
        '        lda d401,x\n'
        '        sta $d401,y                  ; freq hi\n'
    )


def _emit_playirq_dispatch(cfg: FCConfig) -> str:
    """Emit playirq + h2 + h3 sequence-byte dispatch.

    Called via PSID play=$LOAD+3 each VBI (50Hz PAL). Walks each
    voice's sequence stream, consuming transpose/voiceinc/repeat
    commands and advancing tabcount until it hits a pattern jump
    ($00-$3F). Pattern-jump processing (note-load + per-voice
    shadow→SID write loop) is the next session — for now h3f_pattern
    stubs out to nextvoice, and nextvoice just advances to the next
    voice without writing any SID registers.

    Frame-exact effect THIS session: zero net $D4xx writes per play()
    call. State updates only: tabcount, toneadd, voiceinc, repeatsto,
    counter2 advance per frame. The writelog `match` count therefore
    stays at 26 (init only). Next session lights up frame 1+ writes
    by emitting the note-load + shadow-write chain.

    Translation notes from the ACME reference (h2/h3/h3a/h3c/h3f):
      - SMC trick (yoa1/yoa2 patching the immediate operand of
        `lda $ffff,y`) replaced by ZP indirect load via seqptr_lo/hi.
        Frame-exact comparison only cares about SID writes; CPU
        internals are free.
      - Voice loop uses X=2,1,0 (V3→V2→V1) to match the original.
      - nextvoice's shadow→SID write order from cfg.nextvoice_write_order.
    """
    # nextvoice (used by h10b's skip path) writes regs in cfg order.
    # For interleaved layout, PW was already written either by
    # pp_store's inline SID writes (held-note path) or by nolengset's
    # inst-reload direct writes (new-note path). So nextvoice can
    # skip PW — matches Hawkeye's $830C 3-reg late write.
    nextvoice_writes = _emit_nextvoice_writes(
        cfg.nextvoice_write_order, cfg.late_ctrl_uses_byteand_mask,
        skip_pw=(cfg.voice_loop_layout == 'interleaved'))

    # fm2_cleanup parameters. Cyb II default: writes both $D418=$10|VOL
    # and $D416=$80, with a strange-filter early-out. Hawkeye writes
    # only $D416=$E0, no strange-filter check, no $D418.
    fm2_d416_value = f'{cfg.fm2_cleanup_d416_value:02x}'
    fm2_strange_check = (
        '        lda fx2sto\n'
        '        and #$08\n'
        '        bne fx_strange_filter        ; strange filter active → skip cleanup\n'
        if cfg.fm2_cleanup_checks_strange_filter else ''
    )
    fm2_d418_write = (
        '        lda #$10 | VOLUME_INIT\n'
        '        sta $d418\n'
        if cfg.fm2_cleanup_writes_d418 else ''
    )

    # Voice-loop layout. 'tight_nextvoice' (Cyb II): all effects run, then
    # nextvoice writes all 5 voice regs at chain end. 'interleaved'
    # (Hawkeye): PW writes happen INLINE in pp_store (right after each
    # PW shadow STA), then CTRL+FREQ writes happen at chain end before
    # falling through to the dex/loop. The nextvoice: block is still
    # emitted in both modes because h10b's skip path branches to it.
    pw_writes_mid_chain = ''  # legacy slot — empty now (moved into pp_store)
    # Voice-loop initial X. SMC layout: load from voice_loop_start (set
    # per-subtune in song init from mode_addr byte). Flat layout: hardcoded
    # ldx #$02 (Cyb II's tight engine budget can't afford the state byte).
    if cfg.subtune_layout == 'smc_template_with_sfx':
        playirq_run_ldx = (
            '        ldx voice_loop_start         ; loop initial X '
            '(set per-subtune)\n'
        )
    else:
        playirq_run_ldx = (
            '        ldx #2                       ; V3 → V1 (3 voices)\n'
        )

    # nolengset's tonearpcounter reset (Cyb II yes, Hawkeye no).
    nolengset_reset_tonearp = (
        '        lda #0\n'
        '        sta tonearpcounter,x\n'
        if cfg.nolengset_resets_tonearpcounter else ''
    )

    if cfg.voice_loop_layout == 'interleaved':
        pp_store_pw_setup = '        ldy voicesto\n'
        pp_store_sta_d402_sid = '        sta $d402,y                  ; SID PW lo (early)\n'
        pp_store_sta_d403_sid = '        sta $d403,y                  ; SID PW hi (early)\n'
        nolengset_sta_d402_sid = '        sta $d402,y                  ; SID PW lo (inst reload)\n'
        nolengset_sta_d403_sid = '        sta $d403,y                  ; SID PW hi (inst reload)\n'
        ctrl_freq_writes_late = _emit_ctrl_freq_writes_inline(
            cfg.late_ctrl_uses_byteand_mask) + '\n'
        chain_exit = (
            'dex\n'
            '        bmi playirq_done\n'
            '        jmp startplayer              ; interleaved: bypass nextvoice'
        )
    elif cfg.voice_loop_layout == 'tight_nextvoice':
        pp_store_pw_setup = ''
        pp_store_sta_d402_sid = ''
        pp_store_sta_d403_sid = ''
        nolengset_sta_d402_sid = ''
        nolengset_sta_d403_sid = ''
        ctrl_freq_writes_late = ''
        chain_exit = 'jmp nextvoice                ; per-voice shadow→SID write loop'
    else:
        raise ValueError(f'unknown voice_loop_layout: {cfg.voice_loop_layout!r}')

    fx_noise_tick_chunk = _emit_fx_noise_tick(cfg)
    fx_pulse_run_body = _emit_fx_pulse_run(cfg)

    # h10 body — per cfg.held_note_clears_stod404_gate.
    if cfg.held_note_clears_stod404_gate:
        h10_body = """        ; Held-note path (Hawkeye style): threshold-based gate
        ; clear in stod404. Threshold = (filcount byte & $F0) >> 3
        ; (high nibble / 8). Compared against ELAPSED frames
        ; (nootleng - nootcount), not remaining.
        ;   if elapsed >= threshold → stod404 = wavesto & $FE (kill gate)
        ;   else                    → stod404 = wavesto (keep gate)
        ; Mirrors disasm $7DCA-$7DF8 (self-modified CMP at $7DE8).
        ; No byteand involvement; late $D404 write is direct.
        lda nootcount,x
        beq h10_hk_kill              ; if 0 → kill gate
        lda wavecount,x
        asl
        asl
        asl
        tay
        lda filcount,y               ; instrument byte +4
        and #$F0
        lsr
        lsr
        lsr                          ; threshold = hi_nibble / 8 (>> 3)
        sta st2            ; scratch (reused from noise_tick)
        lda nootleng,x
        sec
        sbc nootcount,x              ; A = elapsed frames
        cmp st2
        bcs h10_hk_kill              ; elapsed >= threshold → kill gate
        ; elapsed < threshold — keep gate (use wavesto unchanged)
        lda wavesto,x
        bne h10_hk_store             ; if wavesto != 0, store directly
h10_hk_kill:
        lda wavesto,x
        and #$FE
h10_hk_store:
        sta stod404,x
"""
    else:
        h10_body = """        ; Held-note path (Cyb II style): compute byteand from
        ; filcount's high nibble. The late $D404 write ANDs stod404
        ; with byteand to apply the gate-off mask.
        lda nootcount,x
        beq h10_gwaitout
        lda wavecount,x
        asl
        asl
        asl
        tay
        lda filcount,y               ; instrument's filcount byte
        and #$F0
        lsr
        lsr
        cmp nootcount,x
        bcs h10_gwaitout             ; threshold >= nootcount → kill gate
        lda #$FF                     ; threshold < nootcount → keep gate
        bne h10_gwb                  ; always taken
h10_gwaitout:
        lda #$FE                     ; gate-off mask (preserves waveform bits)
h10_gwb:
        sta byteand,x
"""

    return ("""
; --- playirq dispatch + h2/h3 sequence walker ---
playirq:
        lda testbyte
        beq playirq_run
        rts                          ; halted, return immediately

playirq_run:
        lda speedbyte
{playirq_run_ldx}        dec speedsto
        bpl startplayer
        sta speedsto                 ; reload speed counter on underflow

startplayer:
        stx wax                      ; save current voice index
        inc counter2,x               ; per-voice frame counter
        ldy d4point,x                ; Y = SID register offset (0/7/14)
        sty voicesto
        lda speedsto
        cmp speedbyte
        beq do_h2                    ; speed counter just reloaded →
                                     ; eligible to take a new sequence step
        jmp h11                      ; intermediate frame → continuation

do_h2:
        ; Load current voice's sequence pointer into ZP indirect slot
        lda seqloclo,x
        sta seqptr_lo
        lda seqlochi,x
        sta seqptr_hi
        dec nootcount,x
        bmi h2_take_step             ; underflow → take next sequence step
        jmp h10                      ; note still playing → held-note path

h2_take_step:
        ldy tabcount,x
        lda (seqptr_lo),y            ; A = sequence byte
        cmp #$FE
        beq do_songout
        cmp #$FF
        bne h3_dispatch
        ; $FF — reset sequence cursor (loop to start)
        lda #0
        sta nootcount,x
        sta tabcount,x
        sta begcount,x
        jmp h2_take_step

do_songout:
        jmp songout

h3_dispatch:
        sta st2
        cmp #$40
        bcc h3f_pattern              ; $00-$3F → pattern jump
        cmp #$80
        bcc h3a_voiceinc_or_repeat   ; $40-$7F → voiceinc/repeat
        ; $80-$FF → set toneadd (transpose)
        and #$1F
        sta toneadd,x
        inc tabcount,x
        jmp h2_take_step

h3a_voiceinc_or_repeat:
        lda st2
        cmp #$60
        bcc h3c_repeat               ; $40-$5F → repeat
        ; $60-$7F → voiceinc
        and #$0F
        sta voiceinc,x
        inc tabcount,x
        jmp h2_take_step

h3c_repeat:
        ; $40-$5F → set repeatsto
        and #$3F
        sta repeatsto,x
        inc tabcount,x
        jmp h2_take_step

h3f_pattern:
        ; $00-$3F — pattern jump. Load pattern_ptr_table[A*2..A*2+1]
        ; into zp3/zp4 (the pattern indirect pointer), then walk the
        ; pattern byte chain to load the first note.
        ;
        ; A on entry: pattern id (0-63).
        asl                          ; A *= 2
        tay
        lda pattern_ptr_table,y
        sta zp3
        lda pattern_ptr_table+1,y
        sta zp4

        ; Reset per-note state for the new note
        lda #0
        sta glidetest,x
        sta glidetest2,x
        sta counter2,x
        sta vibcounter,x

        ; Fetch first pattern byte. If $F0/$F1, handle prefix; else
        ; jump to startnewnote (clear newnote flag) and dispatch.
        ldy begcount,x
        lda (zp3),y
        sta tabbytsto
        cmp #$F0
        bcc startnewnote

        ; >= $F0 — check bit 0 for $F1
        lda tabbytsto
        and #1
        bne dofilset                 ; $F1 = filter set
        ; $F0 — noglide marker. Set newnote, consume $F0, read next
        ; byte (the note) as tabbytsto, jump to skip (dispatch).
        lda #1
        sta newnote,x
        inc begcount,x
        iny
        lda (zp3),y
        sta tabbytsto
        bne skip                     ; (always nonzero — notes >$00)

dofilset:
        ; $F1 — filter set. Consume $F1, read value byte, write to
        ; $D417, then advance + fetch next byte into tabbytsto.
        inc begcount,x
        iny
        lda (zp3),y
        sta $d417                    ; filter resonance/routing
        jsr verhoogtest
        ; falls through to startnewnote

startnewnote:
        lda #0
        sta newnote,x

skip:
        ; --- Pattern byte dispatch chain ---
        ; Each handler dispatches `tabbytsto` and consumes byte(s).
        ;
        ; Range $F0/$F1 = special markers (noglide / filterset)
        ; Range $E0-$EF = glide (3-byte sequence)
        ; Range $C0-$DF = wave/inst adjust
        ; Range $80-$BF = setlength
        ; Range <$80   = note/arp
        ;
        ; $F0/$F1 must be checked FIRST because $F0 ≥ $E0 would
        ; otherwise be caught by the glide handler. Orig handles this
        ; via AND #$F0 / CMP #$F0 at $7C64 — re-dispatched on every
        ; chain step (setlen_loop, wave/inst chain) and on the
        ; initial pattern entry. Hawkeye sub 1 pattern $1B hits
        ; $82 $F0 $43 $FF — without this check, $F0 fires glide and
        ; consumes $FF as glide target, missing the pattern end.
        lda tabbytsto
        cmp #$F0
        bcs f0_or_f1_chained

        cmp #$E0
        bcc noglideset

        ; Glide handler: 3 bytes total ($Ex + delay + target).
        ; Consume delay, then target. The target is the actual note,
        ; saved into tempglide AND re-stored as tabbytsto for the
        ; nolengset chain to play it.
        lda #1
        sta glidetest,x
        inc begcount,x
        iny
        lda (zp3),y
        sta glidedelay,x
        inc begcount,x
        inc begcount,x
        iny
        iny
        lda (zp3),y
        clc
        adc toneadd,x
        sta tempglide,x
        dey                          ; back up Y to point at target
        lda (zp3),y
        sta tabbytsto
        bne nolengset                ; always taken (target > 0)

f0_or_f1_chained:
        ; Re-dispatched $F0 (noglide) or $F1 (filterset). Mirrors
        ; orig's $7C64-$7C8B flow: advance past the marker byte,
        ; read the next byte into tabbytsto, then re-dispatch via
        ; `skip` (or to nolengset for the noglide case, since the
        ; next byte IS the note).
        lda tabbytsto
        and #1
        bne f1_chained               ; $F1 → filterset
        ; $F0 — noglide marker. Set newnote, advance past $F0,
        ; read next byte (the note) as tabbytsto, dispatch.
        lda #1
        sta newnote,x
        inc begcount,x
        iny
        lda (zp3),y
        sta tabbytsto
        bne skip                     ; (always nonzero — notes >$00)

f1_chained:
        ; $F1 — filterset. Advance past $F1, read value byte, write
        ; to $D417, then advance + fetch next byte into tabbytsto,
        ; re-dispatch.
        inc begcount,x
        iny
        lda (zp3),y
        sta $d417
        jsr verhoogtest              ; INC begcount, fetch next byte
        jmp skip

noglideset:
        ; Range $C0-$DF = wave/inst adjust (sets wavecount)
        lda tabbytsto
        cmp #$C0
        bcc novoiceset

        and #$1F
        clc
        adc voiceinc,x
        sta wavecount,x
        jsr verhoogtest
        ; falls through to novoiceset

novoiceset:
        ; Range $80-$BF = setlength. First byte: nootleng = (lo 6 bits) - 1.
        ; Subsequent $80-$BF bytes extend: nootleng += (lo 6 bits).
        ; $C0+ next byte → re-dispatch (wave/inst, glide, $F0+).
        ; <$80 next byte → fall through to arpset (note/arp).
        lda tabbytsto
        cmp #$80
        bcc arpset

        and #$3F
        sec
        sbc #1
        sta nootleng,x

setlen_loop:
        jsr verhoogtest              ; reads next byte → tabbytsto, also in A
        cmp #$C0
        bcs skip                     ; >= $C0: re-dispatch fresh cmd
        cmp #$80
        bcc arpset                   ; < $80: note/arp

        ; extension byte ($80-$BF): nootleng += (byte & $3F)
        and #$3F
        clc
        adc nootleng,x
        sta nootleng,x
        jmp setlen_loop

arpset:
        ; Range $70-$7F = arpeggio program select. Loads arplo[N]/
        ; arphi[N] (where N = byte & $0F) into the per-voice
        ; arpieoklo/arpieokhi state arrays. fx_tone_arp consumes
        ; those each frame.
        cmp #$70
        bcc nolengset

        and #$0F
        sty denom                    ; save Y (begcount cursor)
        tay
        lda arplo,y
        ldx wax
        sta arpieoklo,x
        lda arphi,y
        sta arpieokhi,x
        ldy denom                    ; restore Y
        jsr verhoogtest
        ; falls through to nolengset

nolengset:
        ; Note play. tabbytsto holds the note pitch ($00-$6F).
        ; Apply toneadd, look up lonote/hinote, write to $D400/01,
        ; set ADSR + waveform from instrument, etc.
        lda nootleng,x
        sta nootcount,x
{nolengset_reset_tonearp}
        lda tabbytsto
        clc
        adc toneadd,x
        sta noho,x
        tay                          ; Y = freq table index

        ; Write lonote/hinote to per-voice shadow regs + SID
        lda lonote,y
        sta d400,x
        pha
        sta lonotesto,x
        sta lonotesto2,x             ; preserved (orig $90E3, Hawkeye release)
        lda hinote,y
        sta d401,x
        sta hinotesto,x
        sta hinotesto2,x             ; preserved (orig $90DD, Hawkeye release)
        sta freq_rise_acc,x          ; bit-2 sweep accumulator (orig $90E0)
        ldy voicesto
        sta $d401,y                  ; SID $D401 (freq hi)
        pla
        sta $d400,y                  ; SID $D400 (freq lo)

        ; If newnote flag set (came from $F0 noglide), skip ADSR
        ; reload — keep current envelope state.
        lda newnote,x
        bne snnn

        ; Reload ADSR + waveform + pulse from instrument table
        lda wavecount,x
        asl
        asl
        asl
        tax                          ; X = instrument byte offset (= wavecount*8)
        lda attdec,x
        sta $d405,y                  ; SID $D405 (AD)
        lda susrel,x
        sta $d406,y                  ; SID $D406 (SR)
        lda filcount,x
        pha
        lda pulsehi,x
        pha
        lda waveform,x
        ldx wax                      ; X = voice id again
        sta wavesto,x
        sta stod404,x                ; shadow $D404 (waveform+gate)
        lda #0
        sta d402,x                   ; shadow $D402 (pw lo)
        sta pulsestolo,x
{nolengset_sta_d402_sid}        pla
        sta pulsehitemp,x
        and #$0F
        sta d403,x                   ; shadow $D403 (pw hi nibble)
        sta pulsehisto,x
{nolengset_sta_d403_sid}
        lda #1
        sta pulsetest,x
        pla
        sta filtercount,x

snnn:
        ; Advance begcount, check if next byte is $FF (pattern end).
        inc begcount,x
        ldy begcount,x
        lda (zp3),y
        cmp #$FF
        bne h10b

nextjmp:
        ; Pattern ended ($FF). If repeats remain, decrement; else
        ; advance to next sequence step.
        lda #0
        sta begcount,x
        lda repeatsto,x
        beq nj1

        dec repeatsto,x
        bpl h10b

nj1:
        inc tabcount,x

h10b:
        ; Reset byteand (drum-routine gate mask) to $FF and exit.
        lda #$FF
        sta byteand,x
        jmp nextvoice

verhoogtest:
        ; Advance begcount, increment Y, fetch next byte into
        ; tabbytsto. If $FF (pattern end), jump to nextjmp.
        inc begcount,x
        iny
        lda (zp3),y
        cmp #$FF
        beq nextjmp
        sta tabbytsto
        rts

; --- Held-note path (h10) + intermediate-frame path (h11) ---
;
; h10 runs when do_h2 finds nootcount > 0 (note still has frames left).
; It sets byteand based on the drum-trigger threshold derived from
; filcount's high nibble, then falls into h11.
;
; h11 also runs directly when speedsto != speedbyte (intermediate
; frame — speed counter hasn't reloaded yet). It checks for a special
; ADSR-release condition (pulsehitemp bit 4 + nootcount=0 + speedsto=1),
; then falls into gwo2 (the effect-chain dispatcher).
;
; gwo2 loads the per-voice fx*sto cache from the current instrument
; and dispatches into the effect chain. For drum-flag instruments,
; it skips tone-arp + vibrato by jumping straight to fx_glide.
;
; Each effect chunk (fx_*) starts with its bit check and is currently
; a NO-OP stub that falls into the next effect. Drop in implementations
; one at a time by replacing the STUB block.

h10:
{h10_body}        ; fall into h11

h11:
        ; Intermediate-frame path entry + ADSR release check.
        ; If pulsehitemp bit 4 set AND note just ended AND speedsto=1,
        ; force ADSR release ($D406,y = h11_release_sr_value from cfg).
        ; Cyb II: $02. Hawkeye: $01 (orig reuses LDA $9116 result here).
        lda pulsehitemp,x
        and #$10
        beq gwo2
        lda nootcount,x
        bne gwo2
        lda speedsto
        cmp #1
        bne gwo2
        lda #h11_release_sr_value
        sta $d406,y                  ; ADSR sustain/release tweak

gwo2:
        ; Effect-chain dispatcher entry — load instrument fx bytes into
        ; ZP cache, then walk the effect chain.
        lda wavecount,x
        asl
        asl
        asl
        tay                          ; Y = wavecount * 8 (instrument offset)
        lda fx1,y
        sta fx1sto
        lda fx2,y
        sta fx2sto
        lda noho,x
        sta noothoogt,x
        lda fx3,y
        sta fx3sto
        and #$10
        beq fx_tone_arp              ; not drum — normal chain start
        jmp fx_glide                 ; drum — skip tone-arp + vibrato

; --- Effect chain (skeleton; drop in real impls one at a time) ---
;
; Order matches the original FC engine. Each effect's entry point is
; a labelled stub: the flag check is present so xa65 produces valid
; code, but the effect's actual logic is a TODO. Falls through to the
; next effect.
;
; What each effect should eventually modify (shadow regs that
; nextvoice writes to SID at end-of-frame):
;   stod404      ← waveform + gate ($D404,y)
;   d400         ← freq lo         ($D400,y)
;   d401         ← freq hi         ($D401,y)
;   d402         ← pulse-width lo  ($D402,y)
;   d403         ← pulse-width hi  ($D403,y)
;   byteand      ← AND mask for $D404 (drum routine clears gate)
; Some effects also write SID registers DIRECTLY (e.g., filter
; program writes $D416/$D418, noise-tick writes $D401,y).

fx_tone_arp:
        ; fx3 bit $04 — cycles a per-voice arp program. The program
        ; lives at arpieoklo,X/arpieokhi,X (set by arpset during
        ; pattern dispatch). Layout:
        ;   arp[0]    = reload counter value when the counter
        ;               underflows
        ;   arp[1..N] = semitone deltas added to noho per frame
        ;
        ; tonearpcounter,X counts down each frame. On underflow it
        ; reloads from arp[0]. Each frame reads arp[tonearpcounter+1]
        ; and adds it to noho to compute the new noothoogt (pitch),
        ; then reloads d400/d401 from lonote/hinote at that index.
        ;
        ; ZP indirect (ta_arp_lo/hi at $53/$54) replaces the ACME
        ; source's SMC trick (arpieoklo1/arpieoklo2/arpieokhi1/
        ; arpieokhi2 SMC slots patching `lda arp0`/`lda arp0,Y`).
        lda fx3sto
        and #$04
        beq fx_vibrato

        ldx wax
        lda arpieoklo,x
        sta ta_arp_lo
        lda arpieokhi,x
        sta ta_arp_hi
        dec tonearpcounter,x
        bpl ta_hallo

        ; counter underflowed — reload from arp[0]
        ldy #0
        lda (ta_arp_lo),y
        sta tonearpcounter,x

ta_hallo:
        ldx wax
        ldy tonearpcounter,x
        iny                          ; arp[counter+1] = current delta
        lda (ta_arp_lo),y
        clc
        adc noho,x
        sta noothoogt,x
        tay                          ; Y = new pitch index
        lda lonote,y
        sta d400,x                   ; freq lo shadow
        lda hinote,y
        sta d401,x                   ; freq hi shadow
        ; falls through to fx_vibrato

fx_vibrato:
        ; fx1 != 0 (vibrato amplitude lo nibble) AND !glidetest2,X
        ; (glide not yet 2nd-phase) → run vibrato. Otherwise skip.
        ;
        ; fx1 layout:
        ;   bits 0-3 (amplitude): vibrasto = depth shift count
        ;   bits 4-6 (speed):     vibstore1 = LFO step
        ;   bit  7   (direction): 0=positive (LDY path), 1=negative (ADC path)
        ;
        ; Algorithm:
        ;   1. Compute delta = freq[noothoogt+1] - freq[noothoogt]
        ;      (the inter-semitone distance — vibrato unit).
        ;   2. Shift delta right `vibrasto` times → smaller modulation
        ;      depth.
        ;   3. Update LFO state via vibstore1/2/3 (triangle wave).
        ;   4. Add/subtract scaled delta to vibreallo/vibrealhi based
        ;      on vibstore3 (number of subtractions) and (vibstore1>>1
        ;      - vibstore3) (number of additions).
        ;   5. Skip the add/sub when counter2,X < vibtabwait[wavecount]
        ;      (vibrato onset delay).
        ;   6. Write d400/d401 + lonotesto/hinotesto from
        ;      vibreallo/vibrealhi.
        ;
        ; Branch replaces ACME's SMC doitnot trick; ZP replaces SMC
        ; vibwait slot.
        lda fx1sto
        bne vib_check_glide
        jmp fx_glide                 ; fx1=0 → no vibrato
vib_check_glide:
        lda glidetest2,x
        beq vib_run
        jmp fx_glide                 ; glide phase 2 → skip vibrato

vib_run:
        ; Setup
        ldy wavecount,x
        lda vibtabwait,y
        sta vibwait_zp               ; cache vibtabwait[wavecount]

        lda fx1sto
        and #$0F                     ; amplitude nibble
        sta vibrasto

        lda fx1sto
        and #$70                     ; speed bits 4-6
        lsr
        lsr
        lsr
        lsr
        ldx wax
        sta vibstore1,x

        ; Increment vibcounter (capped at vibtotzover)
        lda vibcounter,x
        cmp #vibtotzover
        bcs vib_skip_inc
        inc vibcounter,x
vib_skip_inc:

        ; Compute delta = freq[noothoogt+1] - freq[noothoogt]
        ldy noothoogt,x
        lda lonote2,y                ; lonote2 = lonote + 1
        sec
        sbc lonote,y
        sta templono
        lda hinote2,y
        sbc hinote,y
        ; For NEGATIVE vibrato (fx1 bit 7 set), the original adds
        ; vibcounter[X] + carry to delta_hi here. Branch instead.
        bit fx1sto
        bpl vib_pos
        adc vibcounter,x             ; A = delta_hi + vibcounter[X] + carry
vib_pos:
        sta temphino

        ; Divide delta by 2^vibrasto (shift right vibrasto times)
vib_reducesize:
        dec vibrasto
        bmi vib_redout
        lsr temphino
        ror templono
        jmp vib_reducesize

vib_redout:
        ; Update LFO state via vibstore2 (direction) and vibstore3 (counter)
        lda vibstore2,x
        bpl vib_w1                   ; vibstore2 >= 0 → counting up
        ; vibstore2 < 0 → counting down
        dec vibstore3,x
        bne vib_nextsect
        inc vibstore2,x
        bpl vib_nextsect
vib_w1:
        inc vibstore3,x
        lda vibstore1,x
        cmp vibstore3,x
        bcs vib_nextsect             ; vibstore3 < vibstore1 → keep going up
        ; Reached peak — flip direction
        sta vibstore3,x
        dec vibstore2,x
        dec vibstore3,x

vib_nextsect:
        ; Load fresh base freq into vibreallo/vibrealhi
        ldy noothoogt,x
        lda lonote,y
        sta vibreallo
        lda hinote,y
        sta vibrealhi

        ; Subtract delta (vibstore1>>1) times, gated by vibtabwait
        lda vibstore1,x
        lsr
        tay                          ; Y = subtraction count

vib_subval:
        dey
        bmi vib_endsv
        lda counter2,x
        cmp vibwait_zp
        bcc vib_endav                ; counter2 < vibwait → onset delay
        lda vibreallo
        sec
        sbc templono
        sta vibreallo
        lda vibrealhi
        sbc temphino
        sta vibrealhi
        jmp vib_subval

vib_endsv:
        ; Then add delta vibstore3 times
        ldy vibstore3,x
vib_addval:
        dey
        bmi vib_endav
        clc
        lda vibreallo
        adc templono
        sta vibreallo
        lda vibrealhi
        adc temphino
        sta vibrealhi
        jmp vib_addval

vib_endav:
        ldx wax
        lda vibreallo
        sta d400,x
        sta lonotesto,x
        lda vibrealhi
        sta d401,x
        sta hinotesto,x
        ; falls through to fx_glide

fx_glide:
        ; glidetest set (PatGlide active) — linear pitch interpolation
        ; from current freq toward tempglide target. Step size derived
        ; from 16-bit (current-target) delta divided by
        ; (speedbyte+1) * glide_bran (where glide_bran is the hi
        ; nibble of glidedelay). Direction (subtract vs add) depends
        ; on delta sign.
        ;
        ; glidedelay byte layout:
        ;   hi nibble  →  glen (snap threshold) + bran (denom mult)
        ;   lo nibble  →  pre-onset delay (skip glide while nootcount
        ;                  + lo - 1 > nootleng)
        ;
        ; When close to note end (snap condition), pitch snaps to
        ; tempglide and glidetest/glidetest2 clear.
        ;
        ; Branches replace ACME source's SMC opcode-patching tricks
        ; (glisscarry / updown1 / updown2 / glen / bran / udlo / udhi).
        ldx wax
        lda glidetest,x
        bne glide_run
        jmp fx_freq_hi_rise            ; not glide → next effect

glide_run:
        ; Cache glen + bran (= glidedelay hi nibble)
        lda glidedelay,x
        and #$F0
        lsr
        lsr
        lsr
        lsr
        sta glide_glen
        sta glide_bran

        ; Pre-onset delay check
        lda glidedelay,x
        and #$0F
        sec
        sbc #1
        clc
        adc nootcount,x
        cmp nootleng,x
        bcc glide_phase2             ; A < nootleng → continue
        jmp fx_freq_hi_rise            ; still in delay phase

glide_phase2:
        pha
        lda #1
        sta glidetest2,x
        pla
        adc glide_glen
        cmp nootleng,x
        bcs glide_no_snap            ; A + glen >= nootleng → continue
        jmp glide_snap               ; otherwise snap (far branch via JMP)
glide_no_snap:

        ; Compute delta = freq[noho] - freq[tempglide]
        ldy noho,x
        lda tempglide,x
        tax                          ; X = target pitch (temporary)
        sec
        lda lonote,y
        sbc lonote,x
        sta glideslo
        lda hinote,y
        sbc hinote,x
        sta glideshi
        ldx wax                      ; restore X = current voice
        bcs glide_pos

        ; Delta negative — negate to abs value
        lda glideshi
        eor #$FF
        sta glideshi
        lda glideslo
        eor #$FF
        sta glideslo
        inc glideslo
        bne glide_neg_done
        inc glideshi
glide_neg_done:
        lda #1
        sta glide_dir                ; direction = UP
        jmp glide_div

glide_pos:
        lda #0
        sta glide_dir                ; direction = DOWN

glide_div:
        ; denom = bran * (speedbyte + 1) — repeated add
        ldy speedbyte
        lda #0
        clc
glide_denom_loop:
        adc glide_bran
        dey
        bpl glide_denom_loop
        sta glide_denom

        ; 16-bit / 8-bit long division: glideslo:glideshi /= denom
        ; Quotient back in glideslo:glideshi
        clc
        asl glideslo
        rol glideshi
        ldx #$0F                     ; 15 iterations
        lda #0
glide_div_loop:
        rol glideslo
        rol glideshi
        rol
        bcs glide_div_sub
        cmp glide_denom
        bcc glide_div_skip
glide_div_sub:
        sbc glide_denom
        sec
glide_div_skip:
        dex
        bne glide_div_loop
        rol glideslo
        rol glideshi
        ; Rounding step
        asl
        cmp glide_denom
        bcc glide_div_done
        inc glideslo
        bne glide_div_done
        inc glideshi
glide_div_done:

        ; Apply step to lonotesto/hinotesto + d400/d401 by direction
        ldx wax
        lda glide_dir
        bne glide_apply_up

        ; DOWN: lonotesto -= step
        sec
        lda lonotesto,x
        sbc glideslo
        sta lonotesto,x
        sta d400,x
        lda hinotesto,x
        sbc glideshi
        sta hinotesto,x
        sta d401,x
        jmp fx_freq_hi_rise

glide_apply_up:
        ; UP: lonotesto += step
        clc
        lda lonotesto,x
        adc glideslo
        sta lonotesto,x
        sta d400,x
        lda hinotesto,x
        adc glideshi
        sta hinotesto,x
        sta d401,x
        jmp fx_freq_hi_rise

glide_snap:
        ; Snap to target: load lonote/hinote[tempglide], clear glide flags
        ldx wax
        lda tempglide,x
        sta noho,x
        tay
        lda lonote,y
        sta lonotesto,x
        sta d400,x
        lda hinote,y
        sta hinotesto,x
        sta d401,x
        lda #0
        sta glidetest,x
        sta glidetest2,x
        jmp fx_freq_hi_rise

fx_freq_hi_rise:
        ; Per-instrument freq-hi creep (gated by inst.filter_prog.
        ; freq_hi_rise = fil_count bit 2). Each odd counter2 frame
        ; INC freq_rise_acc and write the PRE-INC value to hinotesto/
        ; d401. Mirrors orig $8243-$826B. Slot AFTER fx_glide so
        ; glide's writes (when active) aren't overwritten on drum-glide
        ; paths; AFTER vibrato so it can overwrite vibrato's hi output
        ; for non-drum tone_arp + bit-2 insts (Hawkeye step 25 worked
        ; example).
        lda counter2,x
        lsr                          ; carry = counter2 bit 0
        bcc fx_freq_hi_rise_skip     ; even → skip
        lda wavecount,x
        asl
        asl
        asl
        tay
        lda filcount,y
        and #$04
        beq fx_freq_hi_rise_skip     ; bit 2 clear → skip
        lda freq_rise_acc,x
        beq fx_freq_hi_rise_skip     ; acc=0 → would write 0
        inc freq_rise_acc,x
        sta d401,x                   ; PRE-INC value → d401 shadow
        sta hinotesto,x              ; mirror to inner shadow
fx_freq_hi_rise_skip:
        ; falls through to fx_pulse_prog

fx_pulse_prog:
        ; fx2 & $07 — pulse-width sweep program. 4 programs in
        ; pulsetabel, 8 bytes each. Program N starts at offset
        ; (N*8)-7 (so program 1 at offset 1, program 2 at offset 9,
        ; etc.) Bytes:
        ;   [0]    low nibble = lo bound; bit 7 = wrap flag (purepbyte)
        ;   [1]    hi bound
        ;   [2,4,6] threshold values (counter2 compared in order)
        ;          high bit toggles direction
        ;   [3,5,7] step values (active when corresponding threshold
        ;           is matched)
        ;
        ; pulsetest,X drives direction (1 = up, 0 = down). pulsestolo,X
        ; and pulsehisto,X are the 16-bit shadow PW. On reaching a
        ; bound, direction flips (or snap-wraps if purepbyte set).
        ;
        ; ZP scratch (pp_count_lo @ $55, pp_count_hi @ $56,
        ; pp_purepbyte @ $57) replaces ACME source's SMC slots.
        ;
        ; ALWAYS writes d402/d403 from shadows at end (the original
        ; engine's `pst:` entry is the unconditional shadow write).
        ; When fx2 & $07 == 0, just skip to the shadow write.
        lda fx2sto
        and #$07
        bne pp_active                ; program active → run program
        jmp pp_store                 ; inactive → just write shadows
                                     ; (using jmp because pp_store is
                                     ; out of branch range)
pp_active:
        ; Compute Y = program offset in pulsetabel: (N*8)-8 = (N-1)*8
        ; for program N (1..7). Comment used to say (N*8)-7 but the actual
        ; SBC #$07 with carry-clear (from asl chain) gives -8 not -7, and
        ; the resulting program-N at offset (N-1)*8 IS what matches HVSC's
        ; layout. Cyb II all subs ALL_FULL with this formula.
        asl
        asl
        asl
        sbc #$07
        tay

        ; Read pulsetabel[Y] — first byte
        lda pulsetabel,y
        pha                          ; save first byte
        and #$80                     ; bit 7 = wrap flag
        beq pp_noprep
        lda #1
pp_noprep:
        sta pp_purepbyte
        pla
        and #$0F                     ; low nibble = lo bound
        sta pp_count_lo

        iny
        lda pulsetabel,y             ; pulsetabel[Y+1] = hi bound
        sta pp_count_hi

        ; Walk thresholds at offsets 2, 4, 6 — find which segment
        ; counter2 falls into.
        iny
        lda pulsetabel,y             ; pulsetabel[Y+2]
        and #$7F
        cmp counter2,x
        bcc pp_go6
        jmp pp_go5

pp_go6:
        iny
        iny
        lda pulsetabel,y             ; pulsetabel[Y+4]
        and #$7F
        cmp counter2,x
        bcc pp_go2
        jmp pp_go5

pp_go2:
        iny
        iny
        lda pulsetabel,y             ; pulsetabel[Y+6]
        and #$7F
        cmp counter2,x
        bcc pp_go3
        ; fall through to pp_go5

pp_go5:
        ; Threshold matched — use this segment's step
        lda pulsetabel,y             ; the matched threshold byte
        and #$80                     ; high bit → flip direction
        beq pp_goo1
        lda #0
        sta pulsetest,x
pp_goo1:
        iny
        lda pulsetabel,y             ; pulsetabel[matched+1] = step
        sta pulsecountup
        jmp pp_go4

pp_go3:
        ; Past all thresholds — use fx2 hi nibble as step
        lda fx2sto
        and #$F0
        sta pulsecountup

pp_go4:
        lda pulsetest,x
        bne pp_pusw1                 ; pulsetest != 0 → direction UP

        ; Direction DOWN: pulsestolo -= pulsecountup (with hi borrow)
        lda pulsestolo,x
        sec
        sbc pulsecountup
        sta pulsestolo,x
        lda pulsehisto,x
        sbc #0
        sta pulsehisto,x
        cmp pp_count_lo              ; reached lower bound?
        bcs pp_store
        ; underflow — flip direction (go UP next frame)
        lda #1
        bne pp_pulseshit             ; always taken

pp_pusw1:
        ; Direction UP: pulsestolo += pulsecountup
        lda pulsestolo,x
        clc
        adc pulsecountup
        sta pulsestolo,x
        lda pulsehisto,x
        adc #0
        sta pulsehisto,x
        cmp pp_count_hi              ; reached upper bound?
        bcc pp_store
        ; hit upper bound — check wrap flag
        lda pp_purepbyte
        beq pp_ppt
        ; wrap: snap pulsehisto = pp_count_lo, pulsestolo = saved A
        ; Original: `sta pulsestolo,x / lda pulsecountlo / sta pulsehisto,x`
        ; A was the pp_purepbyte value (= 1 typically)
        sta pulsestolo,x
        lda pp_count_lo
        sta pulsehisto,x
        lda #1
        bne pp_pulseshit             ; always taken

pp_ppt:
        lda #0
pp_pulseshit:
        sta pulsetest,x              ; flip direction

pp_store:
        ldx wax
{pp_store_pw_setup}        lda pulsestolo,x
        sta d402,x                   ; PW lo shadow
{pp_store_sta_d402_sid}        lda pulsehisto,x
        sta d403,x                   ; PW hi shadow
{pp_store_sta_d403_sid}        ; falls through to fx_wave_arp

fx_wave_arp:
        ; fx3 bit $40 — cycles wavearp[$80,$10,$80,$10] (waveform
        ; toggle for test bit). Mirrors Hawkeye disasm $80FD-$8110:
        ;   skip if not active OR counter2 < wavearpwait;
        ;   else Y = counter2 & 3; stod404[X] = wavearp[Y].
        lda fx3sto
        and #$40
        beq fx_pulse_arp
        ldx wax
        lda counter2,x
        cmp #wavearpwait
        bcc fx_pulse_arp
        and #$03
        tay
        lda wavearp,y
        sta stod404,x

fx_pulse_arp:
        ; fx3 bit $08 — cycles pulsearp through $D403 (pw hi).
        ; Mirrors Hawkeye disasm $8113-$812B:
        ;   skip if not active OR counter2 < pulsearpwait;
        ;   else Y = counter2 & 7; $D403,voicesto = pulsearp[Y].
        ; Writes DIRECTLY to SID (bypassing the d403 shadow) — for
        ; 'interleaved' layout this is the latest write so the chip
        ; sees pulsearp's value. For 'tight_nextvoice' layout, the
        ; nextvoice tail overwrites $D403 from the shadow afterwards
        ; (matches the original engine's behaviour).
        lda fx3sto
        and #$08
        beq fx_tonesweep_up
        ldx wax
        lda counter2,x
        cmp #pulsearpwait
        bcc fx_tonesweep_up
        lda counter2,x
        and #$07
        tay
        lda pulsearp,y
        ldy voicesto
        sta $d403,y

fx_tonesweep_up:
        ; fx3 bit $20 — decrements hinotesto each frame (downward
        ; pitch sweep). Mirrors Hawkeye disasm $812E-$813A:
        ;   LDA fx3sto / AND #$20 / BEQ skip
        ;   DEC hinotesto,x
        ;   LDA hinotesto,x / STA d401,x
        lda fx3sto
        and #$20
        beq fx_filter_prog
        ldx wax
        dec hinotesto,x
        lda hinotesto,x
        sta d401,x

fx_filter_prog:
        ; fx3 bit $01 — walks the per-voice filter program (fb<n>)
        ; selected by filtercount,X & $07. Writes $D418 (master vol +
        ; filter routing) from fb[5], then $D416 (cutoff hi) computed
        ; by comparing counter2,X against the threshold list at
        ; fb[6..9] and either taking a fixed cutoff (fb[0]/fb[4]) or
        ; incrementing the current cutoff by fb[1..3].
        ;
        ; When the bit is CLEAR, falls into fm2 (filter cleanup):
        ; if this voice was the last to OWN the filter (filwhat == X)
        ; and strange filter isn't active (fx2 & $08 == 0), resets
        ; $D418 to $10|VOLUME and $D416 to $80. Otherwise no-op.
        ;
        ; ZP indirect (zer0fillo/zer0filhi at $51/$52) replaces the
        ; ACME source's SMC trick (trulo/truhi patching `lda #imm`
        ; into the operand of `lda zer0fillo`).
        lda fx3sto
        and #$01
        beq fm2_filter_cleanup

        ; --- filterklooi: filter_prog active ---
        ldx wax
        stx filwhat                  ; this voice now owns the filter
        lda filtercount,x
        and #{filter_prog_mask}      ; cfg-knob: $07 (Cyb II, 8 progs) or $03 (Hawkeye, 4 progs)
        asl
        tax                          ; X = (filtercount & mask) * 2
        lda filterbytes,x
        sta zer0fillo
        lda filterbytes+1,x
        sta zer0filhi

        ; $D418 ← fb[5] (master vol + filter routing for this program)
        ldy #5
        lda (zer0fillo),y
        sta $d418

        ; Compute cutoff by walking thresholds fb[9]..fb[6]
        ldx wax
        lda counter2,x
        ldy #9
        cmp (zer0fillo),y            ; counter2 < fb[9] ?
        bcc filfur3                  ; yes — look further

        ; counter2 >= fb[9] — use fb[4] as final cutoff
        ldy #4
        lda (zer0fillo),y
        jmp fme

filfur3:
        dey                          ; Y goes 8, 7, 6
        cmp (zer0fillo),y
        bcs filfur1                  ; counter2 >= fb[Y] → segment add
        cpy #6
        bne filfur3

        ; counter2 < fb[6] — use fb[0] (initial cutoff)
        ldy #0
        lda (zer0fillo),y
        jmp fme

filfur1:
        ; Within a segment — add fb[Y-5] to current cutoff
        ;   Y=8: add fb[3]
        ;   Y=7: add fb[2]
        ;   Y=6: add fb[1]
        dey
        dey
        dey
        dey
        dey
        lda filter,x                 ; current cutoff
        clc
        adc (zer0fillo),y
        jmp fme

fm2_filter_cleanup:
        ; --- fm2 cleanup: filter_prog NOT active for this voice ---
        ; Parametric per cfg:
        ;   - fm2_cleanup_d416_value: $D416 reset value (Cyb II $80, Hawkeye $E0)
        ;   - fm2_cleanup_writes_d418: write $D418=$10|VOL too (Cyb II yes, Hawkeye no)
        ;   - fm2_cleanup_checks_strange_filter: skip cleanup if strange-filter
        ;     bit is set (Cyb II yes, Hawkeye no)
        ldx wax
        cpx filwhat
        bne fx_strange_filter        ; this voice didn't own filter → skip
{fm2_strange_check}        ; This voice owned the filter — reset.
{fm2_d418_write}        lda #${fm2_d416_value}
        ; falls into fme

fme:
        sta filter,x                 ; cutoff shadow
        sta $d416                    ; SID cutoff hi
        ; falls through to fx_strange_filter

fx_strange_filter:
        ; fx2 bit $08 — bidirectional sweep of $D416 cutoff via
        ; strafilter state. Writes $D416. TODO.
        lda fx2sto
        and #$08
        beq fx_pulse_run
        ; STUB: strange-filter impl here.

fx_pulse_run:
{fx_pulse_run_body}

fx_double_voice:
        ; filcount bit $08 — adds dubvoice ($0C) to d400 lo freq
        ; for octave-detune effect. Modifies d400. TODO.
        lda wavecount,x
        asl
        asl
        asl
        tay
        lda filcount,y
        and #$08
        beq fx_drum
        ; STUB: double-voice impl here.

fx_drum:
        ; fx3 bit $10 — plays drumtabel-indexed waveform + pitch
        ; programs based on counter2,x. Modifies stod404 + d400/d401
        ; + byteand. Drum number from fx1 & $0F.
        ;
        ; drumtabel format (4 bytes per drum, X = drum_num * 4):
        ;   +0,+1: dwa_<n> pointer (waveform program: length byte +
        ;          N waveform bytes; counter2 indexes from 1..N)
        ;   +2,+3: dto_<n> pointer (tone program: N tone bytes;
        ;          counter2-1 indexes from 0..N-1)
        ;
        ; Per-frame:
        ;   - If counter2 >= dwa[0] (length), drum is finished; exit
        ;     to nextvoice without modifying shadows.
        ;   - Else write dwa[counter2] → stod404 (new waveform),
        ;     and dto[counter2-1] → either d401 directly (with d400=0)
        ;     or d400/d401 via lonote/hinote indexed by
        ;     (noothoogt + tone_byte) when fx1 bit 4 is set.
        ;
        ; Drum-routine ZP indirect ptrs (drum_dwa_lo/hi at $4C/$4D,
        ; drum_dto_lo/hi at $4E/$4F) replace the ACME source's SMC.
        ; Frame-exact comparison only cares about SID writes; the
        ; CPU-internal indirection method is free.
        lda fx3sto
        and #$10
        beq fx_noise_tick            ; not drum — fall to noise-tick

        ; Setup: load drumtabel[drum_num*4..+3] into ZP indirect ptrs
        lda fx1sto
        and #$0F
        asl
        asl                          ; X = drum_num * 4
        tax
        lda drumtabel,x
        sta drum_dwa_lo
        lda drumtabel+1,x
        sta drum_dwa_hi
        lda drumtabel+2,x
        sta drum_dto_lo
        lda drumtabel+3,x
        sta drum_dto_hi

        ; Read drum program length from dwa[0]
        ldy #0
        lda (drum_dwa_lo),y
        sta drum_dl

        ; Check if counter2 < length
        ldx wax
        lda counter2,x
        cmp drum_dl
        bcs drum_done                ; counter2 >= length → drum finished

        ; Read wave byte at dwa[counter2]
        tay                          ; Y = counter2
        lda (drum_dwa_lo),y
        sta stod404,x                ; new waveform shadow

        ; Set byteand based on wave's gate bit (preserved/cleared)
        and #1
        beq drum_nd1
        lda #$FF
        bmi drum_nd2                 ; always taken ($FF is negative)
drum_nd1:
        lda #$FE
drum_nd2:
        sta byteand,x

        ; Read tone byte at dto[counter2-1]
        dey                          ; Y = counter2 - 1
        lda (drum_dto_lo),y
        sta st                       ; tone scratch

        ; fx1 bit $10 = drum-uses-noothoogt path
        ldy voicesto
        lda fx1sto
        and #$10
        beq drum_drfu2

        ; fx1 bit 4 set — pitch = noothoogt + st; load lonote/hinote
        ldx wax
        lda noothoogt,x
        clc
        adc st
        tay                          ; Y = freq table index
        ldx wax
        lda lonote,y
        sta d400,x
        lda hinote,y
        sta d401,x
        jmp drum_done

drum_drfu2:
        ldx wax
        lda st
        clc
        adc #fx_drum_d401_offset     ; Cyb II 0; Hawkeye $0D
        sta d401,x                   ; freq hi shadow = tone byte (+ offset)
        lda #0
        sta d400,x                   ; freq lo shadow = 0

drum_done:
        ; Drum overrides downstream effects (specifically fx_noise_tick).
        ; Original engine: `drfu: jmp nextvoice` skipping noti.
        jmp effect_chain_end

{fx_noise_tick_chunk}

effect_chain_end:
{ctrl_freq_writes_late}        {chain_exit}

nextvoice:
        ; Per-voice tail: write the shadow regs to SID, then advance
        ; to next voice (or RTS if all 3 done). Write order from cfg
        ; — see SID-internal-state research for why order matters.
        ; For 'interleaved' layout, normal control flow bypasses this
        ; block (PW + CTRL/FREQ writes happen inline in the chain);
        ; this block is still emitted because h10b's skip path uses it.
        ldx wax
        ldy voicesto

{nextvoice_writes}
        dex
        bmi playirq_done
        jmp startplayer

playirq_done:
        rts
""").format(
        nextvoice_writes=nextvoice_writes,
        fm2_strange_check=fm2_strange_check,
        fm2_d418_write=fm2_d418_write,
        fm2_d416_value=fm2_d416_value,
        filter_prog_mask=f'${cfg.filter_prog_mask:02x}',
        pw_writes_mid_chain=pw_writes_mid_chain,
        ctrl_freq_writes_late=ctrl_freq_writes_late,
        chain_exit=chain_exit,
        fx_noise_tick_chunk=fx_noise_tick_chunk,
        h10_body=h10_body,
        pp_store_pw_setup=pp_store_pw_setup,
        pp_store_sta_d402_sid=pp_store_sta_d402_sid,
        pp_store_sta_d403_sid=pp_store_sta_d403_sid,
        nolengset_sta_d402_sid=nolengset_sta_d402_sid,
        nolengset_sta_d403_sid=nolengset_sta_d403_sid,
        nolengset_reset_tonearp=nolengset_reset_tonearp,
        playirq_run_ldx=playirq_run_ldx,
        fx_pulse_run_body=fx_pulse_run_body,
    )

#
# Cybernoid II's HVSC SID uses a multi-stage trampoline that doesn't
# match the ACME source's natural layout. The PSID-pointed init/play
# vectors at $A600/$A603 jump to a TAX/JMP at $A606 which jumps to a
# SECOND trampoline at $A620 which finally jumps to the real song
# body at $A6CA. The 22-byte zero gap at $A60A-$A61F is engine state
# storage that the engine zero-clears at runtime.
#
# Session 2: emit the trampolines as proper labelled asm. This is the
# simplest chunk to lift out of the verbatim placeholder.

def _emit_trampolines_cybernoid_ii() -> str:
    """Emit the two-stage trampoline at $A600-$A628 plus the
    state-region zero gap.

    HVSC's Cybernoid II uses a multi-stage trampoline. The PSID-pointed
    init/play vectors at $A600/$A603 jump to a TAX/JMP at $A606 which
    jumps to a second trampoline at $A620 which finally jumps to the
    real engine routines at $A6CA/$A70F/$A716. The 22-byte zero gap
    at $A60A-$A61F is engine state storage that the engine zero-clears
    at runtime.

    Targets are raw addresses ($A6CA etc.) so we don't need to define
    labels for them (they live in the verbatim engine region that
    follows). Session 3+ will replace those raw addresses with proper
    labels as more chunks lift out of verbatim.
    """
    return """; --- entry trampolines (session 2 asm) ---
; PSID init=$A600, play=$A603
init    jmp song_tramp           ; $A600 jmp $A606
        jmp play_tramp           ; $A603 jmp $A626
song_tramp                       ; $A606
        tax                      ; save song number from accumulator
        jmp song_body            ; $A607 jmp $A620

; $A60A-$A61F: 22 bytes of state storage (engine zero-clears at runtime)
        .dsb 22, 0

; --- second trampoline at $A620 (3-vector to real routines) ---
song_body                        ; $A620
        jmp $a6ca                ; song body (real routine)
        jmp $a70f                ; songout (real routine)
play_tramp                       ; $A626
        jmp $a716                ; playirq (real routine)
"""


def _emit_verbatim_region(orig_mem: bytes, start_addr: int,
                           end_addr_exclusive: int) -> str:
    """Emit a region of memory as `.byt` bytes. The label is the
    region's start address (for readability)."""
    out = [f'; verbatim bytes ${start_addr:04X}..${end_addr_exclusive-1:04X} '
           f'(session 1 placeholder — engine code to be replaced)']
    bytes_seq = orig_mem[start_addr:end_addr_exclusive]
    for i in range(0, len(bytes_seq), 16):
        row = bytes_seq[i:i + 16]
        out.append('        .byt ' + ','.join(f'${b:02X}' for b in row))
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Top-level asm assembly (Cybernoid II layout)
# ---------------------------------------------------------------------------

def _compose_fc_asm_cybernoid_ii(usf: UsfFile, cfg: FCConfig,
                                  orig_mem: bytes,
                                  orig_code_end: int) -> str:
    """Compose the full ACME asm for a Cybernoid-II-shaped FC SID.

    Session 1 strategy: emit data sections at their exact CPU addresses
    using `* = $XXXX` directives. Engine code + aux-table regions are
    placeholder-emitted as verbatim bytes from the original SID.

    The asm output, when assembled by xa65, produces a binary that
    matches the original SID byte-for-byte (provided the USF preserves
    the relevant fields losslessly).
    """
    load = cfg.freq_lo_addr   # not actually used; we use real load_addr
    # The actual load_addr comes from the original SID's PSID header.
    # Pass it in via a more robust route:
    raise NotImplementedError('use compose_fc_asm() instead')


def compose_fc_asm(usf: UsfFile, cfg: FCConfig,
                   root: str | None = None) -> tuple[str, int]:
    """Compose the full ACME asm + return (asm_text, load_addr).

    Layout strategy:
      - Read the original SID to get load_addr + verbatim engine bytes
      - Emit `* = $LOAD`
      - For each data section in cfg's address map, emit:
          * verbatim bytes from previous-end to section_addr (engine code)
          * `* = $section_addr` (defensive — ensures placement)
          * the section's data emitter from USF
      - Final tail: verbatim bytes after the last data section
    """
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    _hl, load_addr, _init, _play, _n_songs, code, _inline = _load_sid_psid(orig)
    code_end = load_addr + len(code)

    # Materialize the original memory for verbatim emission.
    mem = bytearray(65536)
    mem[load_addr:code_end] = code

    # Cybernoid II's data sections in order. For each, USF reconstructs
    # it; everything between sections is verbatim from the original.
    # The section_end addresses are computed from cfg + USF inputs.
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]

    # snelheid length depends on subtune_layout
    if cfg.subtune_layout == 'flat_seqtabel':
        snelheid_len = len(music_subs)
    else:
        snelheid_len = cfg.music_subtune_count + 1

    raw_sections = [
        ('freq_lo',  cfg.freq_lo_addr,
                     cfg.freq_lo_addr + cfg.freq_table_entries),
        ('freq_hi',  cfg.freq_hi_addr,
                     cfg.freq_hi_addr + cfg.freq_table_entries),
        ('snelheid', cfg.per_subtune_speed_addr,
                     cfg.per_subtune_speed_addr + snelheid_len),
        ('instruments', cfg.instr_records_addr,
                        cfg.instr_records_addr + cfg.instr_count * 8),
    ]

    # The USF-emitted content for each section. Closures take a `limit`
    # so we can truncate a section that's about to overlap its successor
    # (Hawkeye's freq_lo runs into freq_hi by 1 byte — lo[95] aliases
    # hi[0] in the original layout; we only emit the bytes that have a
    # unique address).
    def _emit_lo(limit):
        return _emit_byte_list('lonote',
            [usf.freq_table[i*2] for i in range(limit)])
    def _emit_hi(limit):
        return _emit_byte_list('hinote',
            [usf.freq_table[i*2+1] for i in range(limit)])
    section_emitters = {
        'freq_lo':  _emit_lo,
        'freq_hi':  _emit_hi,
        'snelheid': lambda _n: _emit_snelheid(usf, cfg),
        'instruments': lambda _n: _emit_instruments(usf, cfg),
    }

    # Sort by start; truncate any section that overlaps the next.
    raw_sections.sort(key=lambda s: s[1])
    sections = []
    for i, (name, start, end) in enumerate(raw_sections):
        if i + 1 < len(raw_sections):
            next_start = raw_sections[i + 1][1]
            if end > next_start:
                end = next_start    # truncate — the overlap byte is
                                    # owned by the next section
        sections.append((name, start, end))

    lines = [
        f'; FC asm composer — sessions 1+2 output for {cfg.name}',
        f'; load_addr = ${load_addr:04X}',
        f'; session 1: data sections from USF; session 2: '
        f'engine front-end as asm',
        '',
        f'* = ${load_addr:04X}',
        '',
    ]

    cursor = load_addr

    # Session 2 (cybernoid_ii only): emit the entry trampolines as asm.
    # The next-cursor advances past the second trampoline ($A628) so
    # the verbatim region kicks in from $A629 (speedbyte) onwards.
    if cfg.name == 'cybernoid_ii':
        lines.append(_emit_trampolines_cybernoid_ii())
        cursor = 0xA629    # one past second trampoline's last jmp

    for name, start, end in sections:
        if start > cursor:
            # Emit verbatim engine code from cursor..start-1
            lines.append(f'; --- engine/aux region ${cursor:04X}..${start-1:04X} '
                         f'(verbatim, session 1 placeholder) ---')
            lines.append(_emit_verbatim_region(mem, cursor, start))
            lines.append('')
        elif start < cursor:
            raise ValueError(
                f'section {name} at ${start:04X} overlaps prior section '
                f'(cursor at ${cursor:04X})')
        # Emit the section. Pass the truncated byte count to the
        # emitter so it produces only the bytes that fit before the
        # next section starts.
        n_bytes = end - start
        lines.append(f'; --- {name} ${start:04X}..${end-1:04X} '
                     f'(USF-derived, {n_bytes} bytes) ---')
        lines.append(f'* = ${start:04X}')
        lines.append(section_emitters[name](n_bytes))
        lines.append('')
        cursor = end

    # Final tail: verbatim bytes after the last section
    if cursor < code_end:
        lines.append(f'; --- tail ${cursor:04X}..${code_end-1:04X} '
                     f'(verbatim, session 1 placeholder) ---')
        lines.append(_emit_verbatim_region(mem, cursor, code_end))
        lines.append('')

    return '\n'.join(lines), load_addr


# ---------------------------------------------------------------------------
# xa65 pipeline + PSID wrapping
# ---------------------------------------------------------------------------

def _xa65_assemble(asm_text: str, load_addr: int) -> bytes:
    """Run xa65 on asm_text, return the assembled raw bytes (no PSID
    header). The raw bytes start at the lowest emitted address; xa65
    pads any gaps with zeros."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'src.s')
        obj = os.path.join(td, 'out.bin')
        with open(src, 'w') as f:
            f.write(asm_text)
        # -M allows ':' to appear in comments (MASM-compat mode)
        r = subprocess.run([_XA, '-M', src, '-o', obj],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(
                f'xa65 failed (rc={r.returncode}):\n'
                f'stdout: {r.stdout}\nstderr: {r.stderr}')
        with open(obj, 'rb') as f:
            raw = f.read()
    # xa65 default output is raw bytes (no load-address prefix). The
    # asm's `* = $XXXX` sets the address symbol context only; the
    # output file starts at the lowest emitted byte.
    return raw


# ---------------------------------------------------------------------------
# Feature-driven composition path (incremental — engine emitters replace
# verbatim bytes one chunk at a time, verified via verify_asm writelog)
# ---------------------------------------------------------------------------

def _fixup_verbatim_pointers(mem: bytearray, cfg, shift: int,
                              orig_first_data_addr: int) -> None:
    """Rewrite 16-bit pointers in HVSC's verbatim source bytes so they
    point to the shifted data positions. Mutates `mem` in place.

    Without this, the composer emits pattern_ptr_table (and similar)
    bytes verbatim from HVSC; the entries still contain unshifted
    addresses that don't match the shifted data layout. The engine
    reads those entries at runtime, follows them, gets garbage.

    Tables fixed up (all in HVSC's verbatim aux/tail regions):
      - pattern_ptr_table  (cfg.pattern_ptr_addr, max_patterns entries)
      - drumtabel          (4 drums × 4 bytes = 2 ptrs each)
      - filterbytes        (4 filter progs × 2-byte pointer)
      - arplo + arphi      (split-byte pointers, 8 entries)
      - SFX records        (first 6 bytes = V1/V2/V3 seq ptrs;
                            next 20 bytes = SFX pattern ptr extension)

    Conservative shift rule: only shift pointers whose VALUE is in the
    data region [orig_first_data_addr .. $FFFF]. Engine-code addresses
    (below orig_first_data_addr) are left alone — they typically refer
    to engine subroutines that stay at their original location.
    """
    if shift == 0:
        return
    cutoff = orig_first_data_addr

    def shift_at(lo_addr: int, hi_addr: int) -> None:
        ptr = mem[lo_addr] | (mem[hi_addr] << 8)
        if ptr >= cutoff:
            new = (ptr + shift) & 0xFFFF
            mem[lo_addr] = new & 0xFF
            mem[hi_addr] = new >> 8

    # cfg passed in is ALREADY shifted; convert back to unshifted for
    # source reads.
    def _u(a):
        return a - shift if a else 0

    # pattern_ptr_table: max_patterns entries, 2 bytes each.
    base = _u(cfg.pattern_ptr_addr)
    if base:
        for n in range(cfg.max_patterns):
            shift_at(base + n*2, base + n*2 + 1)

    # drumtabel: each entry = 4 bytes = 2 ptrs (dwa, dto). Engine masks
    # drum_num with $0F (= 16 possible drums). Iterate all 16 and skip
    # entries whose hi bytes look like garbage (< orig_first_data_addr's
    # hi byte). Hawkeye uses drum 5 (inst 21), so the conservative-4
    # used to miss it.
    base = _u(cfg.drumtabel_addr)
    if base:
        for drum in range(16):
            # Sanity: check the dwa hi byte looks like a code/data
            # address (>= $80). If not, this drum slot is unused; skip.
            dwa_hi = mem[base + drum*4 + 1]
            dto_hi = mem[base + drum*4 + 3]
            if dwa_hi < 0x80 or dto_hi < 0x80:
                continue
            shift_at(base + drum*4 + 0, base + drum*4 + 1)
            shift_at(base + drum*4 + 2, base + drum*4 + 3)

    # filterbytes: filter programs × 2 bytes per pointer. Iterate up to
    # 8 (fits the engine's max mask); skip entries with garbage hi byte.
    base = _u(cfg.filterbytes_addr)
    if base:
        for prog in range(8):
            if mem[base + prog*2 + 1] < 0x80:
                continue
            shift_at(base + prog*2, base + prog*2 + 1)

    # arplo + arphi: SEPARATE arrays. arp[N] = (arplo[N], arphi[N]).
    # Iterate up to 16 (engine masks with $0F); skip entries with
    # garbage hi byte.
    base_lo = _u(cfg.arplo_addr)
    base_hi = _u(cfg.arphi_addr)
    if base_lo and base_hi:
        for n in range(16):
            if mem[base_hi + n] < 0x80:
                continue
            shift_at(base_lo + n, base_hi + n)

    # Music subtune templates (smc_template_with_sfx layout). Each music
    # subtune has a 6-byte template at (template_base_hi << 8) |
    # SMC_byte. Format: 3 lo + 3 hi seq pointers (V1, V2, V3). These
    # pointers reference seq streams which have moved with the shift.
    if cfg.subtune_layout == 'smc_template_with_sfx':
        already_fixed = set()
        # per_subtune_smc_addr is now shifted; read SMC bytes from
        # the unshifted source location in mem.
        smc_src_base = _u(cfg.per_subtune_smc_addr)
        for sub_idx in range(cfg.music_subtune_count):
            smc_byte = mem[smc_src_base + sub_idx]
            template_addr = (cfg.template_base_hi << 8) | smc_byte
            if template_addr in already_fixed:
                continue  # multiple subs may share a template
            already_fixed.add(template_addr)
            for v in range(3):
                shift_at(template_addr + v, template_addr + 3 + v)

    # SFX records (smc_template_with_sfx layout). Each SFX page record:
    #   bytes 0..5: V1/V2/V3 seq pointers (lo3, hi3) — pointing to
    #               sfx_seq_stream destination (= $8FC5 default).
    #   bytes 6..$19: 20 bytes of pattern_ptr_table extension (10
    #               2-byte pointers).
    #   bytes $1A..$119: 256 bytes pattern data (not pointers).
    if cfg.subtune_layout == 'smc_template_with_sfx' and cfg.sfx_page_base:
        # Use the actual number of SFX subtunes from the PSID songs count
        # minus music subs. Defaults to 6 if unclear. The cfg doesn't
        # carry this directly; conservatively iterate up to 8 SFX records
        # and skip rows whose mem bytes look empty.
        for sfx_idx in range(8):
            rec_base = (cfg.sfx_page_base
                        + sfx_idx * cfg.sfx_page_stride) << 8
            if rec_base + 0x1A > 0x10000:
                break
            # Probe: if all 6 leading bytes are 0, treat as empty/unused.
            if all(mem[rec_base + i] == 0 for i in range(6)):
                continue
            # First 6 bytes: V1/V2/V3 seq pointers (lo3, hi3)
            for v in range(3):
                shift_at(rec_base + v, rec_base + 3 + v)
            # Bytes 6..$19: pattern_ptr extension (10 × 2-byte ptrs)
            for n in range(10):
                shift_at(rec_base + 6 + n*2, rec_base + 6 + n*2 + 1)


def compose_fc_asm_featuredriven(usf: UsfFile, cfg: FCConfig,
                                  root: str | None = None
                                  ) -> tuple[str, int]:
    """Featuredriven asm composition. Replaces HVSC's engine code with
    USF-feature-derived emitters. The composer chooses its own layout
    (engine routines + state) before the data tables; the data tables
    themselves stay at their original addresses (so the verbatim
    sequence/pattern/aux-table streams that follow them continue to
    work).

    Session 1 (this commit) emits:
      - PSID entry jumps at $LOAD
      - song / songout / ok2 / silence_all (the song init chunk)
      - playirq stub (returns immediately — music doesn't play yet)
      - engine state allocations (testbyte, speedbyte, per-voice arrays)

    Sessions 2+ will incrementally replace the playirq stub with real
    h2/h3 dispatch + effect chain emitters, verifying frame-by-frame
    via verify_asm at each step.
    """
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    _hl, load_addr, _i, _p, _n, code, _inline = _load_sid_psid(orig)
    code_end = load_addr + len(code)
    mem = bytearray(65536); mem[load_addr:code_end] = code

    # Apply featuredriven_addr_shift: rebuild's data tables can be
    # placed higher than HVSC's actual layout (which the unshifted
    # cfg.X_addr fields point at — used by extract). Build a shifted
    # cfg so the rest of this function emits everything at the
    # rebuild's chosen positions and the engine code's equates match.
    import dataclasses as _dc
    shift = cfg.featuredriven_addr_shift
    orig_first_data_addr = cfg.freq_lo_addr  # capture BEFORE shifting
    if shift:
        def _s(a): return (a + shift) if a else 0
        sfx_seq_default = (cfg.sfx_seq_stream_addr or 0x8FC5)
        cfg = _dc.replace(cfg,
            freq_lo_addr = _s(cfg.freq_lo_addr),
            freq_hi_addr = _s(cfg.freq_hi_addr),
            pattern_ptr_addr = _s(cfg.pattern_ptr_addr),
            instr_records_addr = _s(cfg.instr_records_addr),
            per_subtune_speed_addr = _s(cfg.per_subtune_speed_addr),
            drumtabel_addr = _s(cfg.drumtabel_addr),
            filterbytes_addr = _s(cfg.filterbytes_addr),
            startlen_addr = _s(cfg.startlen_addr),
            starttabel_addr = _s(cfg.starttabel_addr),
            arplo_addr = _s(cfg.arplo_addr),
            arphi_addr = _s(cfg.arphi_addr),
            pulsetabel_addr = _s(cfg.pulsetabel_addr),
            vibtabwait_addr = _s(cfg.vibtabwait_addr),
            wavearp_addr = _s(cfg.wavearp_addr),
            pulsearp_addr = _s(cfg.pulsearp_addr),
            sfx_seq_stream_addr = sfx_seq_default + shift,
            # per_subtune_smc_addr SHIFTED — the SMC byte table at $83FC
            # is in the verbatim aux region (between snelheid + instr),
            # not the preserved-SMC region $7AE6..$7B5F. Earlier comment
            # was wrong.
            per_subtune_smc_addr = _s(cfg.per_subtune_smc_addr),
            # per_subtune_mode_addr ($7AFF) IS in the preserved region —
            # not shifted. template_base_hi is a high byte, not an
            # address — not shifted.
        )
        # Fix up pointers in verbatim regions so they target the shifted
        # data positions. Without this, pattern_ptr_table entries (and
        # similar) emitted verbatim from HVSC still point to unshifted
        # addresses where mine no longer has the data.
        _fixup_verbatim_pointers(mem, cfg, shift, orig_first_data_addr)

    # Data sections (same as compose_fc_asm)
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if cfg.subtune_layout == 'flat_seqtabel':
        snelheid_len = len(music_subs)
    else:
        snelheid_len = cfg.music_subtune_count + 1

    raw_sections = [
        ('freq_lo',  cfg.freq_lo_addr,
                     cfg.freq_lo_addr + cfg.freq_table_entries),
        ('freq_hi',  cfg.freq_hi_addr,
                     cfg.freq_hi_addr + cfg.freq_table_entries),
        ('snelheid', cfg.per_subtune_speed_addr,
                     cfg.per_subtune_speed_addr + snelheid_len),
        ('instruments', cfg.instr_records_addr,
                        cfg.instr_records_addr + cfg.instr_count * 8),
    ]
    def _emit_lo(limit):
        return _emit_byte_list('lonote',
            [usf.freq_table[i*2] for i in range(limit)])
    def _emit_hi(limit):
        return _emit_byte_list('hinote',
            [usf.freq_table[i*2+1] for i in range(limit)])
    section_emitters = {
        'freq_lo':  _emit_lo,
        'freq_hi':  _emit_hi,
        'snelheid': lambda _n: _emit_snelheid(usf, cfg),
        'instruments': lambda _n: _emit_instruments(usf, cfg),
    }
    raw_sections.sort(key=lambda s: s[1])
    sections = []
    for i, (name, start, end) in enumerate(raw_sections):
        if i + 1 < len(raw_sections):
            next_start = raw_sections[i + 1][1]
            if end > next_start:
                end = next_start
        sections.append((name, start, end))

    first_data_addr = sections[0][1]

    # For SMC layout: compute preservation range for HVSC's SMC
    # template region. My engine reads `mem[(template_base_hi<<8) |
    # per_subtune_smc_addr,X]` to get music-subtune sequence records.
    # That region overlaps where my engine code would live if I emit
    # right after the entry jumps. Preserve HVSC's bytes in that range
    # via verbatim emission, place engine code AFTER it.
    preserve_end = 0     # 0 = no preservation (flat layout default)
    if cfg.subtune_layout == 'smc_template_with_sfx':
        # Find max SMC template lo byte to compute the upper preservation
        # bound. Each music subtune's template is 6 bytes at
        # (template_base_hi << 8) | smc_lo[N], so the last byte of the
        # highest-addressed template is max_smc_lo + 5.
        # IMPORTANT: read SMC bytes from the UNSHIFTED location in mem
        # (cfg.per_subtune_smc_addr is now shifted but mem still holds
        # HVSC's bytes at the original address).
        smc_src_addr = cfg.per_subtune_smc_addr - shift
        smc_los = [mem[smc_src_addr + n]
                   for n in range(cfg.music_subtune_count)]
        preserve_end = (cfg.template_base_hi << 8) | (max(smc_los) + 5)

    lines = [
        f'; FC featuredriven composer — {cfg.name}',
        f'; load_addr = ${load_addr:04X}',
        '',
        '; tune-shared equates',
        'VOLUME_INIT = $0F',
        '',
        '; --- data-table address equates ---',
        '; Engine code references these; the tables themselves live',
        '; in the data section (USF-derived) or verbatim aux region.',
        f'pattern_ptr_table = ${cfg.pattern_ptr_addr:04X}',
        # SFX seq-stream destination (used by sfx_copy3 in sub_song_init).
        # Defaults to orig Hawkeye's $8FC5 when cfg.sfx_seq_stream_addr is 0.
        f'sfx_seq_stream = ${(cfg.sfx_seq_stream_addr or 0x8FC5):04X}',
        # Aux-table addresses. Default $0000 placeholders when an
        # address isn't located yet — the engine code still compiles,
        # but any effect that reads from $0000 will return junk. As
        # long as the effect's flag bit isn't set for any instrument,
        # the dead-code path doesn't execute and behaviour is correct.
        f'drumtabel = ${cfg.drumtabel_addr or 0:04X}',
        f'filterbytes = ${cfg.filterbytes_addr or 0:04X}',
        f'startlen = ${cfg.startlen_addr or 0:04X}',
        f'starttabel = ${cfg.starttabel_addr or 0:04X}',
        f'arplo = ${cfg.arplo_addr or 0:04X}',
        f'arphi = ${cfg.arphi_addr or 0:04X}',
        f'pulsetabel = ${cfg.pulsetabel_addr or 0:04X}',
        f'vibtabwait = ${cfg.vibtabwait_addr or 0:04X}',
        f'wavearp = ${cfg.wavearp_addr or 0:04X}',
        f'pulsearp = ${cfg.pulsearp_addr or 0:04X}',
        f'wavearpwait = {cfg.wavearpwait}',
        f'pulsearpwait = {cfg.pulsearpwait}',
        f'fx_drum_d401_offset = ${cfg.fx_drum_d401_offset:02X}',
        f'h11_release_sr_value = ${cfg.h11_release_sr_value:02X}',
        f'pulserunspeed = ${cfg.pulserunspeed:02X}',
        f'pulserun_pwhi_upper = ${cfg.pulserun_pwhi_upper:02X}',
        f'pulserun_pwhi_wrap_xor = ${cfg.pulserun_pwhi_wrap_xor:02X}',
        # vibrato uses lonote2/hinote2 = lonote+1/hinote+1 (one byte
        # past the freq-table base) to read the next note's freq for
        # delta computation.
        'lonote2 = lonote + 1',
        'hinote2 = hinote + 1',
        '; --- engine constants ---',
        'vibtotzover = $30          ; vibrato counter max',
        _FC_ZP_EQUATES,
        '',
        f'* = ${load_addr:04X}',
        '',
        '; --- PSID entry trampolines ---',
        'init:   jmp song',
        'play:   jmp playirq',
        '',
    ]

    # For SMC layout, preserve HVSC's bytes from after the entry jumps
    # to the end of the SMC template region. My engine code starts
    # after that.
    if preserve_end:
        engine_code_start = preserve_end + 1
        lines.append(f'; --- preserve HVSC SMC template region '
                     f'${load_addr+6:04X}..${preserve_end:04X} ---')
        lines.append(f'; The per-subtune music-record templates at '
                     f'$(template_base_hi << 8) | smc_lo are read by ')
        lines.append(f'; song init. My engine reads them at HVSC\'s '
                     f'original addresses, so they must be preserved.')
        lines.append(_emit_verbatim_region(mem, load_addr + 6,
                                            preserve_end + 1))
        lines.append('')
        lines.append(f'* = ${engine_code_start:04X}')
        lines.append('')

    lines += [
        _emit_song_init_routine(cfg),
        '',
        _emit_playirq_dispatch(cfg),
        '',
    ]

    # State allocation: ALWAYS park past the data region (matches Hawkeye's
    # long-standing approach). This frees the engine code area from the
    # engine+state budget — engine code can grow up to first_data_addr,
    # state lives past the SID body end.
    # (Previous flat_seqtabel-style "state between code and data" was
    # blocking Cyb II's engine from adding fx_pulse_run.)

    # Explicit zero-fill from our engine code's end to the first data
    # table. xa65 does NOT auto-pad gaps between `* = $XXXX` directives
    # — the output file is byte-concatenated regardless of address.
    # So we emit `.dsb first_data_addr - *, 0` to materialize the gap.
    # The fill region is dead bytes — our entry jumps go directly to
    # our song/playirq routines, never executing through here.
    lines.append(f'; fill from end of engine code to first data table')
    lines.append(f'        .dsb ${first_data_addr:04X} - *, 0')
    lines.append('')

    cursor = first_data_addr
    for name, start, end in sections:
        if start > cursor:
            # Verbatim aux fill between sections. Source bytes from HVSC
            # at the UNSHIFTED address (mem[addr - shift]); destination
            # is the shifted address (set by `* = $cursor`).
            lines.append(f'; --- verbatim aux region ${cursor:04X}..'
                         f'${start-1:04X} ---')
            lines.append(f'* = ${cursor:04X}')
            lines.append(_emit_verbatim_region(
                mem, cursor - shift, start - shift))
            lines.append('')
        n_bytes = end - start
        lines.append(f'; --- {name} ${start:04X}..${end-1:04X} '
                     f'(USF-derived, {n_bytes} bytes) ---')
        lines.append(f'* = ${start:04X}')
        lines.append(section_emitters[name](n_bytes))
        lines.append('')
        cursor = end

    # Tail (sequences + patterns + remaining aux tables — still verbatim)
    # When shift != 0, the tail's source address is also unshifted.
    if cursor < (code_end + shift):
        tail_end_dest = code_end + shift
        lines.append(f'; --- verbatim tail ${cursor:04X}..'
                     f'${tail_end_dest-1:04X} ---')
        lines.append(f'* = ${cursor:04X}')
        lines.append(_emit_verbatim_region(
            mem, cursor - shift, tail_end_dest - shift))
        lines.append('')
        cursor = tail_end_dest

    # For SMC layout, state arrays are parked AFTER the verbatim tail
    # (engine code + state would overflow into data tables otherwise).
    # IMPORTANT: xa65 doesn't auto-pad gaps between `* = $XXXX`
    # directives — the output file is byte-concatenated regardless
    # of address. So we explicit `.dsb` to materialize the gap;
    # otherwise the state bytes would land at the wrong CPU address
    # and d4point/per-voice arrays would read garbage at runtime.
    # Park state past the end of the verbatim tail (= original SID body
    # end). For both flat and SMC layouts. shift accounts for any
    # featuredriven_addr_shift in effect.
    state_addr = (((code_end + shift) + 0xFF) & ~0xFF)
    lines.append(f'; --- state arrays parked at ${state_addr:04X} '
                 f'(past HVSC SID end) ---')
    lines.append(f'        .dsb ${state_addr:04X} - *, 0  ; pad gap '
                 f'so state lands at ${state_addr:04X} in CPU memory')
    lines.append(_FC_STATE_LABELS)
    lines.append('')

    return '\n'.join(lines), load_addr


def build_via_asm_featuredriven(cfg: FCConfig,
                                 usf_path: str | None = None,
                                 root: str | None = None) -> bytes:
    """Full featuredriven build path. Reuses the original SID's PSID
    header for now (the header carries title/author/init-vector/etc.,
    which the composer doesn't yet generate from scratch)."""
    if root is None:
        root = _ROOT
    if usf_path is None:
        usf_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(usf_path) as f:
        usf = parse(f.read())

    asm, load_addr = compose_fc_asm_featuredriven(usf, cfg, root=root)
    code_bytes = _xa65_assemble(asm, load_addr)

    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    hl, _la, _i, _p, _n, _c, has_inline = _load_sid_psid(orig)
    if has_inline:
        return orig[:hl] + load_addr.to_bytes(2, 'little') + code_bytes
    return orig[:hl] + code_bytes


def build_via_asm(cfg: FCConfig, usf_path: str | None = None,
                  root: str | None = None) -> bytes:
    """Full build path: USF → ACME asm → xa65 → PSID-wrapped SID bytes.

    Reuses the original SID's PSID header (since session 1 doesn't yet
    emit a from-scratch PSID header — that's a session-2+ concern).
    """
    if root is None:
        root = _ROOT
    if usf_path is None:
        usf_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(usf_path) as f:
        usf = parse(f.read())

    asm, load_addr = compose_fc_asm(usf, cfg, root=root)
    code_bytes = _xa65_assemble(asm, load_addr)

    # Wrap as PSID using the original's header
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    hl, _la, _i, _p, _n, _c, has_inline = _load_sid_psid(orig)

    if has_inline:
        return orig[:hl] + load_addr.to_bytes(2, 'little') + code_bytes
    return orig[:hl] + code_bytes


def verify_via_asm(cfg: FCConfig, root: str | None = None) -> dict:
    """Build via asm composer; compare md5 + report first diffs."""
    import hashlib
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    rebuilt = build_via_asm(cfg, root=root)

    md5_orig = hashlib.md5(orig).hexdigest()
    md5_new = hashlib.md5(rebuilt).hexdigest()
    if md5_orig == md5_new:
        return {'ok': True, 'md5': md5_orig, 'size': len(orig)}

    diffs = []
    for i in range(min(len(orig), len(rebuilt))):
        if orig[i] != rebuilt[i]:
            diffs.append(i)
            if len(diffs) >= 32:
                break
    return {
        'ok': False,
        'md5_orig': md5_orig, 'md5_new': md5_new,
        'size_orig': len(orig), 'size_new': len(rebuilt),
        'first_diffs': diffs,
        'sample': [(i, orig[i], rebuilt[i]) for i in diffs[:8]],
    }
