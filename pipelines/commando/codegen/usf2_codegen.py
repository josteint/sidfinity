"""usf2_codegen.py — Phase 4: USF2 -> 6502 player -> .sid.

Builds a playable Commando SID from the clean USF2 representation (the
decoded Score + the InstrumentModels). The 6502 player is a clean
Commando engine — a faithful implementation of song_interp.py's
semantics — assembled by xa65; the USF2 data is serialised into memory
tables after the engine code.

No engineQuirks, no dynamicFreqEntries: the engine knowledge lives here
in the codegen (plumbing); the data stays abstract.

Built incrementally. Implemented so far: the note backbone (init,
frame/tick loop, note advancement, note-start + HR writes) and the
skydive (freqSlide) effect. Still to add: arpeggio, vibrato, PWM.

Usage:
    python3 pipelines/commando/codegen/usf2_codegen.py
    python3 pipelines/commando/codegen/usf2_codegen.py --verify
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.commando.extract.engine_model import extract  # noqa: E402
from pipelines.commando.extract.inst_generalize import decode_all  # noqa: E402
from pipelines.commando.extract.inst_interp import subtune_resetspd  # noqa: E402

SID_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_original.sid')
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')
OUT_SID = '/tmp/usf2_commando.sid'

LOAD = 0x1000

# Effects implemented by the 6502 engine so far (verification enables
# exactly this subset in song_interp).
ENGINE_FX = {'skydive', 'arp', 'vibrato', 'pwm', 'arp_offtable'}

# ---------------------------------------------------------------------------
# 6502 engine. A faithful implementation of song_interp.py's frame loop.
# Data labels (sidtab, nstreamLo/Hi, loopLo/Hi, insttab, freqtab, voice
# note streams) are appended by the codegen.
#
# instrument table row (16 bytes): init_ctrl, init_pw_lo, init_pw_hi,
# init_ad, init_sr, hr_ctrl, fx_flags, then 9 effect-param bytes.
# fx_flags bit0 = freqSlide (skydive).
# ---------------------------------------------------------------------------

ENGINE = r"""
frame_ctr = $40
speed_ctr = $41
is_tick   = $42
sidoff    = $43
v_dur     = $44
v_instr   = $47
v_pitch   = $4a
v_nptr_lo = $4d
v_nptr_hi = $50
v_loop_lo = $53
v_loop_hi = $56
notep     = $59
i_ctrl    = $5b
i_pwlo    = $5c
i_pwhi    = $5d
i_ad      = $5e
i_sr      = $5f
f_lo      = $60
f_hi      = $61
instoff   = $62
v_slide   = $63
v_tick    = $66
v_durfield = $69
vib_step  = $6c
vdelta_lo = $6d
vdelta_hi = $6e
vtarg_lo  = $6f
vtarg_hi  = $70
vdepthctr = $71
vib_carry = $72
pw_idx    = $73
v_pwdir   = $74
v_pwperiod = $77
pwm_tmp   = $7a
v_hubidx  = $7c

* = $1000
        jmp init
        jmp play

init:
        ldx #2
ini1:   lda #0
        sta v_dur,x
        sta v_pwdir,x
        sta v_pwperiod,x
        lda nstreamLo,x
        sta v_nptr_lo,x
        lda nstreamHi,x
        sta v_nptr_hi,x
        lda loopLo,x
        sta v_loop_lo,x
        lda loopHi,x
        sta v_loop_hi,x
        dex
        bpl ini1
        lda #0
        sta speed_ctr
        lda #$ff
        sta frame_ctr
        ldx #$18
ini2:   lda #0
        sta $d400,x
        dex
        bpl ini2
        lda #$0f
        sta $d418
        rts

play:
        inc frame_ctr
        dec speed_ctr
        bpl notick
        lda #RESETSPD
        sta speed_ctr
        lda #1
        sta is_tick
        jmp voices
notick: lda #0
        sta is_tick
voices:
        ldx #2
pvloop: jsr proc_voice
        dex
        bpl pvloop
        rts

proc_voice:
        lda sidtab,x
        sta sidoff
        jsr calc_instoff
        lda is_tick
        beq pv_fx
        dec v_dur,x
        bpl pv_sus
        jsr load_note
        jsr calc_instoff
        jmp note_start
pv_sus:
        inc v_tick,x
        lda v_dur,x
        bne pv_fx
        lda v_instr,x
        and #$40
        bne pv_fx            ; tie note - skip the hard restart
        jsr hr_writes
pv_fx:
        jmp do_effects

calc_instoff:
        lda v_instr,x
        and #$3f
        asl
        sta pw_idx           ; inst*2  (index into pwacc)
        asl
        asl
        asl
        sta instoff          ; inst*16 (index into insttab)
        rts

; load_note - read next note at v_nptr,x then advance v_nptr by 4.
; a $FF pitch is the loop marker.
load_note:
        lda v_nptr_lo,x
        sta notep
        lda v_nptr_hi,x
        sta notep+1
        ldy #0
        lda (notep),y
        cmp #$ff
        bne ln_ok
        lda v_loop_lo,x
        sta v_nptr_lo,x
        sta notep
        lda v_loop_hi,x
        sta v_nptr_hi,x
        sta notep+1
        ldy #0
        lda (notep),y
ln_ok:  sta v_pitch,x
        iny
        lda (notep),y
        sta v_dur,x
        sta v_durfield,x
        iny
        lda (notep),y
        sta v_instr,x
        iny
        lda (notep),y
        sta v_hubidx,x       ; note byte 3 = Hubbard note_idx
        lda #0
        sta v_tick,x
        lda v_nptr_lo,x
        clc
        adc #4
        sta v_nptr_lo,x
        bcc ln_done
        inc v_nptr_hi,x
ln_done:
        lda v_pitch,x        ; seed the skydive slide value (all notes)
        asl
        tay
        lda freqtab+1,y
        sta v_slide,x
        rts

; note_start - write the note-start register block for voice X.
; a tie note writes only ctrl = init_ctrl & $FE (gate off, no retrigger).
note_start:
        lda v_instr,x
        and #$40
        beq ns_full
        ldy instoff
        lda insttab+5,y      ; hr_ctrl = init_ctrl & $FE
        ldy sidoff
        sta $d404,y
        rts
ns_full:
        ldy instoff
        lda insttab+0,y
        sta i_ctrl
        lda insttab+3,y
        sta i_ad
        lda insttab+4,y
        sta i_sr
        ldy pw_idx           ; pw_lo/pw_hi come from the live accumulator
        lda pwacc,y
        sta i_pwlo
        lda pwacc+1,y
        sta i_pwhi
        lda v_pitch,x
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
        lda i_ctrl
        sta $d404,y
        lda i_pwlo
        sta $d402,y
        lda i_pwhi
        sta $d403,y
        lda i_ad
        sta $d405,y
        lda i_sr
        sta $d406,y
        rts

; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        ldy instoff
        lda insttab+5,y
        ldy sidoff
        sta $d404,y
        lda #0
        sta $d405,y
        sta $d406,y
        rts

; do_effects - per-frame effects (engine order vibrato,pwm,skydive,arp).
do_effects:
        lda #0
        sta vib_carry
        jsr fx_vibrato
        jsr fx_pwm
        jsr fx_skydive
        jmp fx_arp

; fx_pwm - bit4. linear or bidirectional PWM. The pw accumulators
; (pwacc) are per-instrument shared state - see song_interp._pwm.
fx_pwm:
        ldy instoff
        lda insttab+8,y      ; pwm_mode  0=none 1=linear 2=bidir
        bne fxp_on
        rts
fxp_on:
        cmp #$01
        bne fxp_bidir
        ldy instoff
        lda insttab+9,y      ; linear - pw_lo += speed + vib_carry
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        clc
        adc vib_carry
        sta pwacc,y
        ldy sidoff
        sta $d402,y
        rts
fxp_bidir:
        dec v_pwperiod,x
        bpl fxp_ret          ; period counter not expired
        ldy instoff
        lda insttab+10,y     ; reload period
        sta v_pwperiod,x
        lda v_pwdir,x
        bne fxp_fall
        ldy instoff          ; rising
        lda insttab+9,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        adc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp insttab+12,y     ; hi_bound
        bne fxp_wr
        lda #$01
        sta v_pwdir,x
        jmp fxp_wr
fxp_fall:
        ldy instoff
        lda insttab+9,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        sec
        sbc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        sbc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp insttab+11,y     ; lo_bound
        bne fxp_wr
        lda #$00
        sta v_pwdir,x
fxp_wr:
        ldy pw_idx
        lda pwacc+1,y
        sta pwm_tmp
        lda pwacc,y
        sta pwm_tmp+1
        ldy sidoff
        lda pwm_tmp
        sta $d403,y          ; pw_hi
        lda pwm_tmp+1
        sta $d402,y          ; pw_lo
fxp_ret:
        rts

; fx_vibrato - bit3. triangle LFO on freq, disassembly $51C1-$522D.
; leaves vib_carry = the 6502 carry the section hands to the PWM add.
fx_vibrato:
        ldy instoff
        lda insttab+6,y
        and #$08
        bne fxv_go
        rts
fxv_go:
        lda frame_ctr
        and #$07
        cmp #$04
        bcc fxv_s1
        eor #$07
fxv_s1: sta vib_step
        ldy instoff
        lda insttab+7,y      ; vib_depth
        sta vdepthctr
        lda v_pitch,x
        asl
        tay                  ; Y = pitch*2
        sec
        lda freqtab+2,y      ; freq16[pitch+1] - freq16[pitch]
        sbc freqtab+0,y
        sta vdelta_lo
        lda freqtab+3,y
        sbc freqtab+1,y      ; A = diff_hi
fxv_sh: lsr                  ; shift A,vdelta_lo right depth+1 times
        ror vdelta_lo
        dec vdepthctr
        bpl fxv_sh
        sta vdelta_hi
        lda freqtab+0,y      ; target = freq16[pitch]
        sta vtarg_lo
        lda freqtab+1,y
        sta vtarg_hi
        lda v_durfield,x
        cmp #$06
        bcc fxv_wr           ; dur < 6 -> no add (carry left = 0)
        ldy vib_step
        beq fxv_wr           ; step 0 -> no add (carry left = 1)
fxv_add:
        clc
        lda vtarg_lo
        adc vdelta_lo
        sta vtarg_lo
        lda vtarg_hi
        adc vdelta_hi
        sta vtarg_hi
        dey
        bne fxv_add
fxv_wr:
        lda #0               ; capture carry-out for the PWM ADC
        adc #0
        sta vib_carry
        ldy sidoff
        lda vtarg_lo
        sta $d400,y
        lda vtarg_hi
        sta $d401,y
        rts

; fx_skydive - bit0. freq_hi slide + ctrl, see song_interp._skydive.
fx_skydive:
        ldy instoff
        lda insttab+6,y
        and #$01
        beq fxs_ret
        lda v_dur,x
        beq fxs_ret          ; duration_ctr == 0
        lda v_slide,x
        beq fxs_ret          ; slide value dead
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; freq_hi = slide value
        lda v_tick,x
        beq fxs_ns
        ldy instoff
        lda insttab+5,y      ; not-start ctrl = hr_ctrl
        bne fxs_w
        lda #$80
fxs_w:  ldy sidoff
        sta $d404,y
        dec v_slide,x
        rts
fxs_ns: lda #$80             ; note-start subphase ctrl = $80
        ldy sidoff
        sta $d404,y
fxs_ret: rts

; fx_arp - bit2. alternate pitch / pitch+12 by frame parity, write freq.
; idx >= 96 (off-table, inst 7) is deferred.
fx_arp:
        ldy instoff
        lda insttab+6,y
        and #$04
        beq fxa_ret
        lda frame_ctr
        and #$01
        beq fxa_even
        lda v_pitch,x
        clc
        adc #$0c
        jmp fxa_idx
fxa_even:
        lda v_pitch,x
fxa_idx:
        cmp #96
        bcc fxa_in
        ; off-table - the lookup runs into player state. idx 100
        ; (inst 7 at pitch 88) reads note_idx of voices 1 and 2.
        cmp #100
        bne fxa_ret
        ldy sidoff
        lda v_hubidx+2       ; note_idx[V3] -> freq_hi
        sta $d401,y
        lda v_hubidx+1       ; note_idx[V2] -> freq_lo
        sta $d400,y
        rts
fxa_in:
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
fxa_ret: rts

sidtab: .byt 0, 7, 14
"""


# ---------------------------------------------------------------------------
# data serialisation
# ---------------------------------------------------------------------------

def _flatten_voice(voice):
    """Expand a Voice's orderlist into a flat note stream. Returns
    (notes, loop_note_index). Each note record is 4 bytes: pitch,
    durfield, instrument, hub_note_idx — the last being Hubbard's
    byte offset into the pattern (read by inst 7's off-table arp)."""
    notes = []
    loop_idx = 0
    for oi, pat_idx in enumerate(voice.orderlist):
        if oi == voice.loop:
            loop_idx = len(notes)
        pat_notes = voice.patterns.get(pat_idx, [])
        hidx = 0
        for j, n in enumerate(pat_notes):
            nbytes = (1 if n.tie
                      else 2 if (n.instrument & 0x80) else 3)
            base = 0 if j == 0 else hidx
            hidx = 0 if j == len(pat_notes) - 1 else base + nbytes
            notes.append((n.pitch & 0xFF, (n.duration - 1) & 0xFF,
                          n.instrument & 0xFF, hidx & 0xFF))
    return notes, loop_idx


def _fx_flags(m) -> int:
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _emit_data(score, models, freq_table) -> str:
    """Emit the xa65 data section."""
    lines = []

    # instrument row (16 bytes): init_ctrl, init_pw_lo, init_pw_hi,
    # init_ad, init_sr, hr_ctrl, fx_flags, vib_depth, pwm_mode,
    # pwm_a (speed/step), pwm_period, pwm_lo, pwm_hi, then 3 spare.
    lines.append('insttab:')
    for m in models:
        vib_depth = m.vibrato.depth if m.vibrato else 0
        pwm_mode = pwm_a = pwm_period = pwm_lo = pwm_hi = 0
        if m.pwm:
            if m.pwm.mode == 'linear':
                pwm_mode, pwm_a = 1, m.pwm.speed
            else:
                pwm_mode, pwm_a = 2, m.pwm.step
                pwm_period, pwm_lo, pwm_hi = (m.pwm.period, m.pwm.lo_bound,
                                              m.pwm.hi_bound)
        row = [m.init_ctrl, m.init_pw_lo, m.init_pw_hi, m.init_ad,
               m.init_sr, m.hr_ctrl, _fx_flags(m), vib_depth,
               pwm_mode, pwm_a, pwm_period, pwm_lo, pwm_hi, 0, 0, 0]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in row))

    # pwacc - per-instrument pw_lo/pw_hi accumulators (shared by every
    # voice playing the instrument), seeded from the table pw values.
    lines.append('pwacc:')
    for m in models:
        lines.append(f'        .byt ${m.init_pw_lo:02X},${m.init_pw_hi:02X}')

    # full table (>=96 entries) — vibrato reads freqtab[pitch+1] which
    # can run one past the 96 musical notes.
    lines.append('freqtab:')
    for f in freq_table:
        lines.append(f'        .byt ${f & 0xFF:02X},${(f >> 8) & 0xFF:02X}')

    streams = [_flatten_voice(v) for v in score.voices]
    for vi, (notes, _loop) in enumerate(streams):
        lines.append(f'nstream{vi}:')
        for (p, d, ins, fl) in notes:
            lines.append(f'        .byt ${p:02X},${d:02X},${ins:02X},${fl:02X}')
        lines.append('        .byt $FF,$00,$00,$00   ; loop marker')

    lines.append('nstreamLo: .byt <nstream0,<nstream1,<nstream2')
    lines.append('nstreamHi: .byt >nstream0,>nstream1,>nstream2')
    loops = [loop for _, loop in streams]
    lines.append('loopLo: .byt '
                 + ','.join(f'<(nstream{i}+{loops[i] * 4})' for i in range(3)))
    lines.append('loopHi: .byt '
                 + ','.join(f'>(nstream{i}+{loops[i] * 4})' for i in range(3)))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(subtune: int = 0, out_path: str = OUT_SID) -> str:
    song = extract(subtune=subtune)
    models = decode_all(SID_PATH)
    from src.hubbard_emu import load_sid
    _, binary, load = load_sid(SID_PATH)
    resetspd = subtune_resetspd(subtune, binary, load)

    asm = (f'RESETSPD = {resetspd}\n'
           + ENGINE + '\n'
           + _emit_data(song.score, models, song.freq_table) + '\n')

    src = '/tmp/usf2_commando.s'
    obj = '/tmp/usf2_commando.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD + 3)
    h += struct.pack('>H', 1)
    h += struct.pack('>H', 1)
    h += struct.pack('>I', 0)
    h += (b'USF2 Commando' + b'\0' * 32)[:32]
    h += (b'Rob Hubbard' + b'\0' * 32)[:32]
    h += (b'2026' + b'\0' * 32)[:32]
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path


# ---------------------------------------------------------------------------
# verification — rebuilt SID vs song_interp with a matching effect subset
# ---------------------------------------------------------------------------

def verify(sid_path: str, enabled: set, subtune: int = 0,
           n_frames: int = 1500) -> None:
    from pipelines.commando.extract.inst_program import capture, REG_NAMES
    from pipelines.commando.extract.song_interp import SongInterp

    cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
    si = SongInterp(SID_PATH, subtune)
    si.fx_vibrato = 'vibrato' in enabled
    si.fx_pwm = 'pwm' in enabled
    si.fx_skydive = 'skydive' in enabled
    si.fx_arp = 'arp' in enabled
    # the engine does not yet do the off-table (inst 7) arpeggio
    si.fx_arp_offtable = 'arp_offtable' in enabled

    match = 0
    first = None
    by_voice: dict[tuple, int] = {}
    for k in range(n_frames):
        want = si.step()
        got = cap.raw_frames[k]
        if got == want:
            match += 1
            continue
        if first is None:
            first = (k, want, got)
        diff = set(want) ^ set(got)
        vs = tuple(sorted({['V1', 'V2', 'V3'][o // 7] for o, _ in diff}))
        by_voice[vs] = by_voice.get(vs, 0) + 1

    feats = '+'.join(sorted(enabled)) or 'backbone'
    print(f'vs song_interp [{feats}]: {match}/{n_frames} frames exact '
          f'({100.0 * match / n_frames:.1f}%)')
    for vs, c in sorted(by_voice.items(), key=lambda x: -x[1]):
        print(f'  {",".join(vs)}: {c}')
    if first:
        k, want, got = first

        def fmt(fw):
            return ' '.join(
                f'{["V1","V2","V3"][o // 7]}.{REG_NAMES[o % 7]}={v:02X}'
                for o, v in fw) or '-'
        print(f'  first diff at frame {k}:')
        print(f'    song_interp: {fmt(want)}')
        print(f'    rebuilt SID: {fmt(got)}')


def main(argv: list[str]) -> None:
    path = build()
    print(f'built {path}  ({os.path.getsize(path)} bytes)')
    if '--verify' in argv:
        verify(path, ENGINE_FX)


if __name__ == '__main__':
    main(sys.argv[1:])
