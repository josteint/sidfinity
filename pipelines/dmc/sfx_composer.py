"""Composer for the dmc_sfx embedded sub-player.

Emits a clean 6502 interpreter of a typed `SfxEngine` (src/usf/types.py) that
reproduces the original sub-player's per-play() SID write stream. Per the CORE
TENET the runtime is ours to invent — this is a straight re-implementation of
the engine algorithm (RE_NOTES.md 'dmc_sfx'), driven entirely by the USF
musical content, not the original's bytes/SMC.

`compose_sfx_asm` yields a self-contained blob whose first two words are
`jmp sfxinit` / `jmp sfxplay` (init takes A = song index), so it drops into the
same (init_addr, play_addr) dispatch shape as a DMC player blob.
"""

from __future__ import annotations

from src.usf.types import SfxEngine
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header

_SIDOFF = (0, 7, 14)


def _byt(name, data):
    if not data:
        return f'{name}: .byt $00'
    rows = [', '.join(f'${b & 0xFF:02X}' for b in data[i:i + 16])
            for i in range(0, len(data), 16)]
    return f'{name}:\n' + '\n'.join('        .byt ' + r for r in rows)


def compose_sfx_asm(e: SfxEngine, *, origin: int = 0x1000) -> str:
    """Assembly for the dmc_sfx interpreter, entry jump table at `origin`."""
    # per-song / per-instrument parallel tables
    song_voice = [s.voice for s in e.songs]
    song_dur = [s.duration for s in e.songs]
    song_ws = [s.wavestep for s in e.songs]
    song_incr = [s.increment for s in e.songs]
    inst_ctrl = [b for ins in e.instruments for b in ins.ctrl]      # 4 per inst
    inst_fb = [b for ins in e.instruments for b in ins.freqbase]    # 4 per inst
    inst_ad = [ins.ad for ins in e.instruments]
    inst_sr = [ins.sr for ins in e.instruments]
    inst_pwlo = [ins.pw_lo for ins in e.instruments]
    inst_pwhi = [ins.pw_hi for ins in e.instruments]
    vi_dur = [v.duration for v in e.voice_init]
    vi_pitch = [v.pitch for v in e.voice_init]
    vi_incr = [v.increment for v in e.voice_init]
    vi_ws = [v.wavestep for v in e.voice_init]
    vi_inst = [v.instrument for v in e.voice_init]

    live = e.live_counter_fidx
    if live is not None and live >= 0:
        hi_read = (f'        lda cur_fidx\n'
                   f'        cmp #${live & 0xFF:02X}\n'
                   f'        bne sfx_hi_static\n'
                   f'        lda sfx_pc              ; off-table LIVE play counter\n'
                   f'        jmp sfx_hi_write\n'
                   f'sfx_hi_static:\n'
                   f'        lda freq_hi,y\n'
                   f'sfx_hi_write:')
    else:
        hi_read = '        lda freq_hi,y'

    asm = f"""        * = ${origin:04X}
        jmp sfxinit
        jmp sfxplay

;; init (A = song index)
sfxinit:
        pha                          ; save song number (the loop clobbers A)
        ldx #$02
sfxi_lp:
        lda vi_dur,x
        sta st_dur,x
        lda vi_pitch,x
        sta st_pitch,x
        lda vi_incr,x
        sta st_incr,x
        lda vi_ws,x
        sta st_ws,x
        lda vi_inst,x
        sta st_inst,x
        dex
        bpl sfxi_lp
        pla
        tax                          ; X = song
        lda song_voice,x
        tay                          ; Y = voice
        lda song_dur,x
        sta st_dur,y
        lda song_ws,x
        sta st_ws,y
        lda song_incr,x
        sta st_incr,y
        txa
        sta st_inst,y                ; instrument = song index
        lda #$00
        sta st_pitch,y
        lda #${e.init_counter & 0xFF:02X}
        sta sfx_pc
        ; match the orig init's SID-voice clear (canonical boundary)
        lda sidoff,y
        tax
        lda #$00
        sta $d400,x
        sta $d401,x
        sta $d402,x
        sta $d403,x
        sta $d404,x
        sta $d406,x
        lda #$0f
        sta $d405,x
        rts

;; play
sfxplay:
        lda sfx_pc
        tax
        lda filt_lfo,x
        sta $d416
        lda #$01
        sta $d415
        lda #$23
        sta $d417
        inx                          ; X = pc+1
        txa
        and #$07
        sta sfx_pc                   ; next pc = (pc+1)&7
        and #$03
        sta cur_r                    ; rotation = (pc+1)&3
        ldx #$02
sfx_vloop:
        stx cur_x                    ; save voice index for the whole iteration
        lda st_dur,x
        bne sfx_active
        jmp sfx_next
sfx_active:
        lda sidoff,x
        sta cur_off
        lda st_inst,x
        sta cur_ins
        lda #$1f
        sta $d418
        lda st_ws,x
        bmi sfx_glide
        ora st_incr,x
        tay
        lda wave_tab,y
        sta st_pitch,x
        iny
        tya
        and #$0f
        sta st_ws,x
        jmp sfx_regs
sfx_glide:
        lda st_pitch,x
        clc
        adc st_incr,x
        sta st_pitch,x
sfx_regs:
        lda cur_ins
        asl
        asl
        clc
        adc cur_r
        sta cur_rot                  ; ins*4 + r
        ldy cur_rot
        lda inst_ctrl,y
        ldx cur_off
        sta $d404,x
        ldy cur_ins
        lda inst_ad,y
        sta $d405,x
        lda inst_sr,y
        sta $d406,x
        lda inst_pwlo,y
        sta $d402,x
        lda inst_pwhi,y
        sta $d403,x
        ldy cur_rot
        lda inst_fb,y
        ldx cur_x
        clc
        adc st_pitch,x
        sta cur_fidx
        tay
        ldx cur_off
        lda freq_lo,y
        sta $d400,x
{hi_read}
        sta $d401,x
        ldx cur_x
        dec st_dur,x
        beq sfx_gateoff
        jmp sfx_next
sfx_gateoff:
        ldx cur_off
        lda #$08
        sta $d404,x
        lda #$00
        sta $d406,x
        sta $d405,x
sfx_next:
        ldx cur_x
        dex
        bmi sfx_done
        jmp sfx_vloop
sfx_done:
        rts

;; working state
st_dur:   .byt $00,$00,$00
st_pitch: .byt $00,$00,$00
st_incr:  .byt $00,$00,$00
st_ws:    .byt $00,$00,$00
st_inst:  .byt $00,$00,$00
sfx_pc:   .byt $00
cur_r:    .byt $00
cur_x:    .byt $00
cur_off:  .byt $00
cur_ins:  .byt $00
cur_rot:  .byt $00
cur_fidx: .byt $00
sidoff:   .byt {_SIDOFF[0]},{_SIDOFF[1]},{_SIDOFF[2]}

;; data tables
{_byt('filt_lfo', e.filter_lfo)}
{_byt('wave_tab', e.wave_table)}
{_byt('freq_lo', e.freq_lo)}
{_byt('freq_hi', e.freq_hi)}
{_byt('song_voice', song_voice)}
{_byt('song_dur', song_dur)}
{_byt('song_ws', song_ws)}
{_byt('song_incr', song_incr)}
{_byt('inst_ctrl', inst_ctrl)}
{_byt('inst_fb', inst_fb)}
{_byt('inst_ad', inst_ad)}
{_byt('inst_sr', inst_sr)}
{_byt('inst_pwlo', inst_pwlo)}
{_byt('inst_pwhi', inst_pwhi)}
{_byt('vi_dur', vi_dur)}
{_byt('vi_pitch', vi_pitch)}
{_byt('vi_incr', vi_incr)}
{_byt('vi_ws', vi_ws)}
{_byt('vi_inst', vi_inst)}
"""
    return asm


def build_sfx_sid(e: SfxEngine, *, songs_order=None, start_song: int = 1,
                  clock='PAL', sid=8580) -> bytes:
    """Standalone SID of just the dmc_sfx engine — subtune k plays
    `songs_order[k]`. For isolated validation of the interpreter."""
    order = songs_order if songs_order is not None else list(range(len(e.songs)))
    origin = 0x1100
    blob = assemble(compose_sfx_asm(e, origin=origin))
    # dispatcher at $1000: init(A=subtune) -> jsr sfxinit with A=song
    tab = ', '.join(f'${s & 0xFF:02X}' for s in order)
    disp = f"""        * = $1000
        jmp cinit
        jmp cplay
cinit:
        tax
        lda songtab,x
        jmp ${origin:04X}
cplay:
        jmp ${origin + 3:04X}
songtab: .byt {tab}
"""
    dblob = assemble(disp)
    end = max(0x1000 + len(dblob), origin + len(blob))
    image = bytearray(end - 0x1000)
    image[0:len(dblob)] = dblob
    image[origin - 0x1000:origin - 0x1000 + len(blob)] = blob
    clk = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(clock, 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(sid, 0)
    header = build_header(load=0, init=0x1000, play=0x1003,
                          songs=len(order), start_song=start_song,
                          title='dmc_sfx test', author='', released='',
                          flags=(clk << 2) | (sidm << 4))
    return header + bytes([0x00, 0x10]) + bytes(image)
