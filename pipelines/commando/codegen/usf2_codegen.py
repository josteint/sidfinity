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
ENGINE_FX = {'skydive', 'arp'}

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

* = $1000
        jmp init
        jmp play

init:
        ldx #2
ini1:   lda #0
        sta v_dur,x
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
        jsr hr_writes
pv_fx:
        jmp do_effects

calc_instoff:
        lda v_instr,x
        and #$3f
        asl
        asl
        asl
        asl
        sta instoff
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
        iny
        lda (notep),y
        sta v_instr,x
        lda #0
        sta v_tick,x
        lda v_nptr_lo,x
        clc
        adc #4
        sta v_nptr_lo,x
        bcc ln_done
        inc v_nptr_hi,x
ln_done:
        rts

; note_start - write the note-start register block for voice X.
note_start:
        ldy instoff
        lda insttab+0,y
        sta i_ctrl
        lda insttab+1,y
        sta i_pwlo
        lda insttab+2,y
        sta i_pwhi
        lda insttab+3,y
        sta i_ad
        lda insttab+4,y
        sta i_sr
        lda v_pitch,x
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        sta v_slide,x
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
        jsr fx_skydive
        jmp fx_arp

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
        bcs fxa_ret          ; off-table -> deferred
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
    (notes, loop_note_index)."""
    notes = []
    loop_idx = 0
    for oi, pat_idx in enumerate(voice.orderlist):
        if oi == voice.loop:
            loop_idx = len(notes)
        for n in voice.patterns.get(pat_idx, []):
            flags = 1 if n.tie else 0
            notes.append((n.pitch & 0xFF, (n.duration - 1) & 0xFF,
                          n.instrument & 0xFF, flags))
    return notes, loop_idx


def _fx_flags(m) -> int:
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _emit_data(score, models, freq_table) -> str:
    """Emit the xa65 data section."""
    lines = []

    lines.append('insttab:')
    for m in models:
        row = [m.init_ctrl, m.init_pw_lo, m.init_pw_hi, m.init_ad,
               m.init_sr, m.hr_ctrl, _fx_flags(m)] + [0] * 9
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in row))

    lines.append('freqtab:')
    for i in range(96):
        f = freq_table[i]
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
