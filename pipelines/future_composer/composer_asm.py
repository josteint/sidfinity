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
tempglide:      .dsb 3, 0            ; glide target
glidedelay:     .dsb 3, 0            ; glide delay
tonearpcounter: .dsb 3, 0            ; tone-arp counter
arpieoklo:      .dsb 3, 0            ; arpeggio program ptr lo
arpieokhi:      .dsb 3, 0            ; arpeggio program ptr hi
lonotesto:      .dsb 3, 0            ; freq lo shadow (for vibrato later)
hinotesto:      .dsb 3, 0            ; freq hi shadow
hinotesto2:     .dsb 3, 0            ; freq hi shadow 2
pulsehitemp:    .dsb 3, 0
pulsestolo:     .dsb 3, 0
pulsehisto:     .dsb 3, 0
pulsetest:     .dsb 3, 0
pulsecountup:   .dsb 1, 0            ; shared scratch — pulse_prog step value
                                     ; (NOT per-voice; reloaded each frame)
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
    snelheid_addr = cfg.per_subtune_speed_addr
    seqtabel_addr = cfg.seqtabel_addr if cfg.subtune_layout == 'flat_seqtabel' else 0
    if seqtabel_addr == 0:
        raise NotImplementedError(
            f'song init emitter currently supports only flat_seqtabel layout '
            f'(cfg.subtune_layout = {cfg.subtune_layout!r}); SMC dispatcher '
            f'+ SFX page records for Hawkeye still pending')

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


def _emit_playirq_dispatch() -> str:
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
    """
    return """
; --- playirq dispatch + h2/h3 sequence walker ---
playirq:
        lda testbyte
        beq playirq_run
        rts                          ; halted, return immediately

playirq_run:
        lda speedbyte
        ldx #2                       ; X = voice 2 (V3) — count down to 0
        dec speedsto
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
        ; Range $E0-$EF = glide (3-byte sequence)
        lda tabbytsto
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
        ; Range $80-$BF (first) = setlength, with $80-$FF (second)
        ; as extension.
        lda tabbytsto
        cmp #$80
        bcc arpset

        and #$3F
        sec
        sbc #1
        sta nootleng,x
        jsr verhoogtest

        cmp #$E0
        beq skip                     ; glide can interrupt — re-dispatch
        cmp #$80
        bcc arpset

        ; second setlength byte (extension)
        and #$7F
        clc
        adc nootleng,x
        sta nootleng,x
        jsr verhoogtest

        cmp #$80
        bcc arpset

        jmp skip                     ; yet another $80+ byte — re-dispatch

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
        lda #0
        sta tonearpcounter,x
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
        lda hinote,y
        sta d401,x
        sta hinotesto,x
        sta hinotesto2,x
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
        pla
        sta pulsehitemp,x
        and #$0F
        sta d403,x                   ; shadow $D403 (pw hi nibble)
        sta pulsehisto,x
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
        ; Held-note path: nootcount > 0 (decremented by do_h2, didn't
        ; underflow). Compute byteand based on filcount's drum-trigger
        ; high nibble.
        lda nootcount,x
        beq gwaitout
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
        bcs gwaitout                 ; threshold >= nootcount → kill gate
        lda #$FF                     ; threshold < nootcount → keep gate
        bne gwb                      ; always taken
gwaitout:
        lda #$FE                     ; gate-off mask (preserves waveform bits)
gwb:
        sta byteand,x
        ; fall into h11

h11:
        ; Intermediate-frame path entry + ADSR release check.
        ; If pulsehitemp bit 4 set AND note just ended AND speedsto=1,
        ; force ADSR release (write $02 to $D406,y).
        lda pulsehitemp,x
        and #$10
        beq gwo2
        lda nootcount,x
        bne gwo2
        lda speedsto
        cmp #1
        bne gwo2
        lda #$02
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
        ; fx1 != 0 (and !glidetest2) — triangle-LFO vibrato modulating
        ; d400/d401 by depth derived from delta-freq, amplitude/speed
        ; from fx1 nibbles, polarity from fx1 bit 7. TODO.
        lda fx1sto
        beq fx_glide
        lda glidetest2,x
        bne fx_glide
        ; STUB: vibrato impl here.

fx_glide:
        ; glidetest set (PatGlide active) — linear pitch interpolation
        ; from current freq toward tempglide target, divided by
        ; (1<<bran)-1 per frame. TODO.
        lda glidetest,x
        beq fx_pulse_prog
        ; STUB: tone-glide impl here.

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
        ; Compute Y = program offset in pulsetabel: (N*8)-7
        asl
        asl
        asl
        sbc #$07                     ; carry already clear from asl chain
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
        lda pulsestolo,x
        sta d402,x                   ; PW lo shadow
        lda pulsehisto,x
        sta d403,x                   ; PW hi shadow
        ; falls through to fx_wave_arp

fx_wave_arp:
        ; fx3 bit $40 — cycles wavearp[$80,$10,$80,$10] (waveform
        ; toggle for test bit). Modifies stod404. TODO.
        lda fx3sto
        and #$40
        beq fx_pulse_arp
        ; STUB: wave-arp impl here.

fx_pulse_arp:
        ; fx3 bit $08 — cycles pulsearp through d403 (pw hi).
        ; TODO.
        lda fx3sto
        and #$08
        beq fx_tonesweep_up
        ; STUB: pulse-arp impl here.

fx_tonesweep_up:
        ; fx3 bit $20 — decrements hinotesto each frame (downward
        ; pitch sweep). Modifies d401. TODO.
        lda fx3sto
        and #$20
        beq fx_filter_prog
        ; STUB: tonesweep-up impl here.

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
        and #$07
        asl
        tax                          ; X = (filtercount & 7) * 2
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
        ldx wax
        cpx filwhat
        bne fx_strange_filter        ; this voice didn't own filter → skip
        lda fx2sto
        and #$08
        bne fx_strange_filter        ; strange filter active → skip cleanup
        ; This voice owned the filter, no strange filter — reset.
        lda #$10 | VOLUME_INIT
        sta $d418
        lda #$80
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
        ; fx3 bit $02 — autonomous PWM sweep via pulserunlo/hi at
        ; pulserunspeed rate. Modifies d402/d403. TODO.
        lda fx3sto
        and #$02
        beq fx_double_voice
        ; STUB: pulse-run impl here.

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
        sta d401,x                   ; freq hi shadow = tone byte
        lda #0
        sta d400,x                   ; freq lo shadow = 0

drum_done:
        ; Drum overrides downstream effects (specifically fx_noise_tick).
        ; Original engine: `drfu: jmp nextvoice` skipping noti.
        jmp effect_chain_end

fx_noise_tick:
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
        ; falls through to effect_chain_end

effect_chain_end:
        jmp nextvoice                ; per-voice shadow→SID write loop

nextvoice:
        ; Per-voice tail: write the shadow regs to SID, then advance
        ; to next voice (or RTS if all 3 done).
        ldx wax
        ldy voicesto

        lda stod404,x
        and byteand,x
        sta $d404,y                  ; SID $D404 (waveform+gate)
        lda d400,x
        sta $d400,y                  ; SID $D400 (freq lo — redundant with inline)
        lda d401,x
        sta $d401,y                  ; SID $D401 (freq hi — redundant with inline)
        lda d402,x
        sta $d402,y                  ; SID $D402 (pw lo)
        lda d403,x
        sta $d403,y                  ; SID $D403 (pw hi)
        dex
        bmi playirq_done
        jmp startplayer

playirq_done:
        rts
"""

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
        f'drumtabel = ${cfg.drumtabel_addr:04X}'
        if cfg.drumtabel_addr else '; drumtabel: not yet located',
        f'filterbytes = ${cfg.filterbytes_addr:04X}'
        if cfg.filterbytes_addr else '; filterbytes: not yet located',
        f'startlen = ${cfg.startlen_addr:04X}'
        if cfg.startlen_addr else '; startlen: not yet located',
        f'starttabel = ${cfg.starttabel_addr:04X}'
        if cfg.starttabel_addr else '; starttabel: not yet located',
        f'arplo = ${cfg.arplo_addr:04X}'
        if cfg.arplo_addr else '; arplo: not yet located',
        f'arphi = ${cfg.arphi_addr:04X}'
        if cfg.arphi_addr else '; arphi: not yet located',
        f'pulsetabel = ${cfg.pulsetabel_addr:04X}'
        if cfg.pulsetabel_addr else '; pulsetabel: not yet located',
        _FC_ZP_EQUATES,
        '',
        f'* = ${load_addr:04X}',
        '',
        '; --- PSID entry trampolines ---',
        'init:   jmp song',
        'play:   jmp playirq',
        '',
        _emit_song_init_routine(cfg),
        '',
        _emit_playirq_dispatch(),
        '',
        _FC_STATE_LABELS,
        '',
    ]

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
            lines.append(f'; --- verbatim aux region ${cursor:04X}..'
                         f'${start-1:04X} ---')
            lines.append(f'* = ${cursor:04X}')
            lines.append(_emit_verbatim_region(mem, cursor, start))
            lines.append('')
        n_bytes = end - start
        lines.append(f'; --- {name} ${start:04X}..${end-1:04X} '
                     f'(USF-derived, {n_bytes} bytes) ---')
        lines.append(f'* = ${start:04X}')
        lines.append(section_emitters[name](n_bytes))
        lines.append('')
        cursor = end

    # Tail (sequences + patterns + remaining aux tables — still verbatim)
    if cursor < code_end:
        lines.append(f'; --- verbatim tail ${cursor:04X}..'
                     f'${code_end-1:04X} ---')
        lines.append(f'* = ${cursor:04X}')
        lines.append(_emit_verbatim_region(mem, cursor, code_end))
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
