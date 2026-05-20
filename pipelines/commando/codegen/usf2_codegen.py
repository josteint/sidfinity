"""usf2_codegen.py — Phase 4: USF2 -> 6502 player -> .sid.

Builds a playable Commando SID from the clean USF2 representation (the
decoded Score + the InstrumentModels). The 6502 player is a clean
Commando engine — a faithful implementation of song_interp.py's
semantics — assembled by xa65; the USF2 data is serialised into memory
tables after the engine code.

No engineQuirks, no dynamicFreqEntries: the engine knowledge lives here
in the codegen (plumbing); the data stays abstract.

Built incrementally. THIS STAGE: the note backbone — init, frame/tick
loop, note advancement, note-start + HR register writes. Per-frame
effects (vibrato, skydive, arpeggio, PWM) are added in following
stages; until then the rebuilt SID's note-start frames are correct but
the sustained frames are bare.

Usage:
    python3 pipelines/commando/codegen/usf2_codegen.py            # build /tmp/usf2_commando.sid
    python3 pipelines/commando/codegen/usf2_codegen.py --verify   # build + check note backbone
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

# ---------------------------------------------------------------------------
# 6502 engine — note backbone (no per-frame effects yet).
# A faithful implementation of song_interp.py's frame loop. Data labels
# (sidtab, nstreamLo/Hi, loopLo/Hi, insttab, freqtab, voice note streams)
# are appended by the codegen.
# ---------------------------------------------------------------------------

ENGINE = r"""
; ==== zero page ====
frame_ctr = $40
speed_ctr = $41
is_tick   = $42
sidoff    = $43
v_dur     = $44      ; ,x   3 bytes
v_instr   = $47      ; ,x
v_pitch   = $4a      ; ,x
v_nptr_lo = $4d      ; ,x
v_nptr_hi = $50      ; ,x
v_loop_lo = $53      ; ,x
v_loop_hi = $56      ; ,x
notep     = $59      ; 2-byte working pointer
i_ctrl    = $5b
i_pwlo    = $5c
i_pwhi    = $5d
i_ad      = $5e
i_sr      = $5f
f_lo      = $60
f_hi      = $61

* = $1000
        jmp init
        jmp play

; -------------------------------------------------------------------
init:
        ldx #2
ini1:   lda #0
        sta v_dur,x          ; dur 0 -> first tick loads note 0
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
        sta frame_ctr        ; play's INC makes frame 0 -> 0
        ldx #$18
ini2:   lda #0
        sta $d400,x
        dex
        bpl ini2
        lda #$0f
        sta $d418
        rts

; -------------------------------------------------------------------
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

; -------------------------------------------------------------------
proc_voice:
        lda sidtab,x
        sta sidoff
        lda is_tick
        beq pv_done          ; not a tick -> (effects later) nothing
        dec v_dur,x
        bpl pv_sustain
        jsr load_note
        jmp note_start
pv_sustain:
        lda v_dur,x
        bne pv_done          ; still sustaining
        jmp hr_writes        ; duration hit 0 -> hard restart
pv_done:
        rts

; -------------------------------------------------------------------
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
        lda v_loop_lo,x      ; loop
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
        lda v_nptr_lo,x      ; advance by 4
        clc
        adc #4
        sta v_nptr_lo,x
        bcc ln_done
        inc v_nptr_hi,x
ln_done:
        rts

; -------------------------------------------------------------------
; note_start - write the note-start register block for voice X.
note_start:
        lda v_instr,x
        and #$3f
        asl
        asl
        asl
        asl                  ; instr*16
        tay
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

; -------------------------------------------------------------------
; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        lda v_instr,x
        and #$3f
        asl
        asl
        asl
        asl
        tay
        lda insttab+5,y      ; hr_ctrl
        ldy sidoff
        sta $d404,y
        lda #0
        sta $d405,y
        sta $d406,y
        rts

sidtab: .byt 0, 7, 14
"""


# ---------------------------------------------------------------------------
# data serialisation
# ---------------------------------------------------------------------------

def _flatten_voice(voice):
    """Expand a Voice's orderlist into a flat note stream. Returns
    (notes, loop_note_index) — notes is a list of (pitch,durfield,instr,
    flags); loop_note_index is the flat index the $FF marker jumps to."""
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


def _emit_data(score, models, freq_table) -> str:
    """Emit the xa65 data section: pointer tables, instruments, freq
    table, and the three voices' note streams."""
    lines = []

    # instrument table — 16 bytes per instrument
    lines.append('insttab:')
    for m in models:
        row = [m.init_ctrl, m.init_pw_lo, m.init_pw_hi, m.init_ad,
               m.init_sr, m.hr_ctrl] + [0] * 10
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in row))

    # freq table — 96 entries, interleaved lo,hi
    lines.append('freqtab:')
    for i in range(96):
        f = freq_table[i]
        lines.append(f'        .byt ${f & 0xFF:02X},${(f >> 8) & 0xFF:02X}')

    # per-voice note streams + pointer tables
    streams = [_flatten_voice(v) for v in score.voices]
    for vi, (notes, loop_idx) in enumerate(streams):
        lines.append(f'nstream{vi}:')
        for (p, d, ins, fl) in notes:
            lines.append(f'        .byt ${p:02X},${d:02X},${ins:02X},${fl:02X}')
        lines.append(f'        .byt $FF,$00,$00,$00   ; loop marker')

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

    # PSID v2 header (124 bytes)
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)            # load addr
    h += struct.pack('>H', LOAD)            # init
    h += struct.pack('>H', LOAD + 3)        # play
    h += struct.pack('>H', 1)               # songs
    h += struct.pack('>H', 1)               # start song
    h += struct.pack('>I', 0)               # speed
    h += (b'USF2 Commando' + b'\0' * 32)[:32]
    h += (b'Rob Hubbard' + b'\0' * 32)[:32]
    h += (b'2026' + b'\0' * 32)[:32]
    h += struct.pack('>H', 0x0014)          # PAL + 6581
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path


def verify_backbone(sid_path: str, subtune: int = 0,
                    n_frames: int = 1500) -> None:
    """Check the rebuilt SID's note backbone against song_interp with
    effects disabled — same notes, same frames, same note-start/HR
    writes. (Per-frame effects are not emitted by this codegen stage.)"""
    from pipelines.commando.extract.inst_program import capture, REG_NAMES
    from pipelines.commando.extract.song_interp import SongInterp

    cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
    si = SongInterp(SID_PATH, subtune)
    si.effects_on = False

    match = 0
    first = None
    for k in range(n_frames):
        want = si.step()
        got = cap.raw_frames[k]
        if got == want:
            match += 1
        elif first is None:
            first = (k, want, got)
    print(f'note backbone: {match}/{n_frames} frames exact '
          f'({100.0 * match / n_frames:.1f}%)')
    if first:
        k, want, got = first

        def fmt(fw):
            return ' '.join(
                f'{["V1","V2","V3"][o // 7]}.{REG_NAMES[o % 7]}={v:02X}'
                for o, v in fw) or '-'
        print(f'  first diff at frame {k}:')
        print(f'    song_interp(no fx): {fmt(want)}')
        print(f'    rebuilt SID       : {fmt(got)}')


def main(argv: list[str]) -> None:
    path = build()
    size = os.path.getsize(path)
    print(f'built {path}  ({size} bytes)')
    if '--verify' in argv:
        verify_backbone(path)


if __name__ == '__main__':
    main(sys.argv[1:])
