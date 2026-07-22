"""Music Assembler — compose a player + data from a MasmModel.

CORE TENET: the target is the `$D400-$D418` write stream, not the original's
bytes. Nothing is copied from the HVSC image — every table below is emitted
from the model and every address is resolved by the assembler, so the rebuild
is free to sit anywhere. What IS reproduced is the ALGORITHM, because the
write ORDER is an observable consequence of it:

  per play():
    DEC speedctr; on underflow reload it and, per voice, DEC the note-duration
    counter — a voice whose note expired FETCHES its next sequence event and
    emits NOTHING that frame; every other voice runs the update.
  per voice update:
    optional note-init (SR, AD, ctrl-with-gate-cleared) then always
    ctrl, PW hi, PW lo, freq lo, freq hi.
  the filter-owning voice writes $D416 FIRST, before its own voice writes.

Three tables are ENGINE CONSTANTS, verified byte-identical across 58 sampled
HVSC members, so they are mechanism and live here rather than in the model:
the voice register bases ($00/$07/$0E), the 4-phase vibrato direction pattern
($00,$01,$01,$00 — down/up/up/down), and the filter routing per owning voice
($F1/$F3/$F7 = "the triggering track and all lower tracks", exactly as the
manual describes).

The decode this is built on: docs/spec_player_RE_grounded.md CORRECTION block.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.composer_runtime import assemble, build_header      # noqa: E402

LOAD = 0x1000
VOICE_BASE = (0x00, 0x07, 0x0E)
VIB_DIR = (0x00, 0x01, 0x01, 0x00)
FILT_ROUTE = (0xF1, 0xF3, 0xF7)


def _tbl(name: str, vals) -> str:
    v = list(vals)
    if not v:
        return '%s\n        .byt 0' % name
    rows = ['        .byt ' + ','.join('$%02X' % b for b in v[i:i + 16])
            for i in range(0, len(v), 16)]
    return '%s\n%s' % (name, '\n'.join(rows))


def _seq_bytes(events) -> list:
    """Re-emit one sequence stream from decoded events (NOT copied bytes)."""
    by = []
    for e in events:
        if e.kind == 'preset':
            by.append(0x80 | (e.value & 0x1F))
        elif e.kind == 'rest':
            by.append(0x60 | (e.duration & 0x1F))
        elif e.kind == 'hold':
            by.append(0xA0 | (e.duration & 0x1F))
        else:
            by.append(e.value & 0x7F)
            by.append(e.raw_flags)
            if e.filt:
                by.extend(e.filt)
            elif e.slide:
                by.extend(e.slide)
    by.append(0xFF)
    return by


def _data(m) -> str:
    out = []
    # sequences + their pointer tables (indexed by seq number)
    top = max(m.sequences) + 1 if m.sequences else 1
    names = []
    for sn in range(top):
        if sn in m.sequences:
            names.append('seq_%d' % sn)
            out.append(_tbl('seq_%d' % sn, _seq_bytes(m.sequences[sn])))
        else:
            names.append('seq_none')
    out.append('seq_none\n        .byt $FF')
    out.append('seqlo\n        .byt ' + ','.join('<' + n for n in names))
    out.append('seqhi\n        .byt ' + ','.join('>' + n for n in names))
    # orderlists
    for i, t in enumerate(m.tracks):
        by = []
        for e in t.entries:
            by.append(e.seq)
            by.append(((e.transpose & 0x0F) << 4) | (e.repeat & 0x0F))
        by.append(0xFF if t.loops else 0xFE)
        by.append(0x00)
        out.append(_tbl('trk_%d' % i, by))
    out.append('trklo\n        .byt <trk_0,<trk_1,<trk_2')
    out.append('trkhi\n        .byt >trk_0,>trk_1,>trk_2')
    # presets (8 bytes each)
    pb = []
    for p in m.presets:
        pb.extend((p.ad, p.sr, p.waveform, p.pulse_init, p.pulse_step,
                   p.vib_byte, p.vib_depth, p.fx))
    out.append(_tbl('preset', pb or [0] * 8))
    # arpeggios
    anames = []
    for i in range(16):
        if i in m.arps:
            anames.append('arp_%d' % i)
            by = []
            for st in m.arps[i].steps:
                by.extend((st.waveform, st.note, st.filter_lp))
            by.append(0xFF if m.arps[i].loops else 0xFE)
            out.append(_tbl('arp_%d' % i, by))
        else:
            anames.append('arp_none')
    out.append('arp_none\n        .byt $FE')
    out.append('arplo\n        .byt ' + ','.join('<' + n for n in anames))
    out.append('arphi\n        .byt ' + ','.join('>' + n for n in anames))
    # freq tables + engine constants
    out.append(_tbl('freqlo', m.freq_lo))
    out.append(_tbl('freqhi', m.freq_hi))
    out.append(_tbl('vbase', VOICE_BASE))
    out.append(_tbl('vibdir', VIB_DIR))
    out.append(_tbl('froute', FILT_ROUTE))
    # Per-voice state. The work block (cleared by init) starts at 0; every
    # OTHER byte keeps the original's file-image leftover, which is audible
    # from frame 1 (see MasmModel.prime).
    for n in ('readpos', 'ctrlw', 'orderpos', 'durctr', 'seqnum', 'transrep',
              'repctr'):
        out.append('%s\n        .byt 0,0,0' % n)
    for n in ('curnote', 'nfrqlo', 'nfrqhi', 'sfrqlo', 'sfrqhi', 'noteflg',
              'arppos', 'sl1', 'sl2', 'vibdly', 'vibfr', 'vibph', 'pwfr',
              'pwdir', 'pwlo', 'pwhi', 'presetx', 'gmask', 'rattle'):
        out.append(_tbl(n, m.prime.get(n, [0, 0, 0])))
    out.append('speedctr\n        .byt 0')
    out.append('filtowner\n        .byt 0')
    return '\n'.join(out)


ENGINE = r"""
* = $1000
        jmp init
        jmp play

; ------------------------------------------------------------------ init
init    lda #$1f
        sta $d418
        lda #$f0
        sta $d417
        and #$0f
        sta filtowner
        ldx #2
iv      lda #0
        sta readpos,x
        sta ctrlw,x
        sta orderpos,x
        sta durctr,x
        sta seqnum,x
        dex
        bpl iv
        lda #0
        sta speedctr
        ldx #2
it      lda trklo,x
        sta $fa
        lda trkhi,x
        sta $fb
        ldy #0
        lda ($fa),y
        sta seqnum,x
        iny
        lda ($fa),y
        sta transrep,x
        and #$0f
        sta repctr,x
        dex
        bpl it
        rts

; ------------------------------------------------------------------ play
play    ldx #0
        dec speedctr
        bmi padv
        jsr voice
        jsr vnext
        jmp vnext
padv    lda #SPEED
        sta speedctr
        jsr dadv
        jsr dnext
dnext   inx
dadv    dec durctr,x
        bmi fetch
        jmp voice
vnext   inx
        jmp voice

; --------------------------------------------------------------- release
rel     lda ctrlw,x
        and #$fe
        sta ctrlw,x
        rts

; ----------------------------------------------------------- seq fetch
fetch   ldy seqnum,x
        cpy #$fe
        bne fok
        jmp rel
fok     lda seqlo,y
        sta $fa
        lda seqhi,y
        sta $fb
        ldy readpos,x
        lda ($fa),y
        bmi fcmd
        cmp #$60
        bcc fnote
frest   and #$1f
        sta durctr,x
        lda #$fe
        sta gmask,x
        jsr rel
        jmp fend
fcmd    cmp #$a0
        bcc fpre
        and #$1f
        sta durctr,x
        jmp fend
fpre    asl
        asl
        asl
        sta presetx,x
        iny
        lda ($fa),y
        cmp #$60
        bcs frest
fnote   sta $fc
        iny
        lda transrep,x
        lsr
        lsr
        lsr
        lsr
        clc
        adc $fc
        sta curnote,x
        sty $fc
        tay
        lda freqlo,y
        sta nfrqlo,x
        sta sfrqlo,x
        lda freqhi,y
        sta nfrqhi,x
        sta sfrqhi,x
        ldy $fc
        lda ($fa),y
        sta noteflg,x
        and #$1f
        sta durctr,x
        lda ($fa),y
        bmi ffilt
        and #$20
        beq fnend
        iny
        lda ($fa),y
        sta sl1,x
        iny
        lda ($fa),y
        sta sl2,x
        jmp fnend
ffilt   stx filtowner
        iny
        lda ($fa),y
        sta fcutr0+1
        and #$0f
        asl
        sec
        sbc #$10
        sta fvel0+1
        iny
        lda ($fa),y
        bne ffon
        lda #$f0
        sta $d417
        bne fnend
ffon    sta fdurr0+1
        lda froute,x
        sta $d417
fnend   lda #$ff
        sta gmask,x
        sta rattle,x
        lda #0
        sta vibfr,x
        sta vibph,x
fend    iny
        lda ($fa),y
        cmp #$ff
        bne fsave
        dec repctr,x
        bpl frst
        lda trklo,x
        sta $fa
        lda trkhi,x
        sta $fb
        ldy orderpos,x
        iny
        iny
        lda ($fa),y
        cmp #$ff
        bne fnw
        ldy #0
fnw     tya
        sta orderpos,x
        lda ($fa),y
        sta seqnum,x
        iny
        lda ($fa),y
        sta transrep,x
        and #$0f
        sta repctr,x
frst    ldy #0
fsave   tya
        sta readpos,x
        rts

; ----------------------------------------------------------------- voice
voice   ldy presetx,x
        sty $fc
        lda noteflg,x
        and #$40
        bne effects
        sta arppos,x
        ldy $fc
        lda preset+0,y
        sta $fa
        lda preset+1,y
        ldy vbase,x
        sta $d406,y
        lda $fa
        sta $d405,y
        lda ctrlw,x
        and #$fe
        sta $d404,y
        ldy $fc
        lda preset+2,y
        and gmask,x
        sta ctrlw,x
        lda preset+3,y
        sta pwlo,x
        sta pwhi,x
        cpx #0
        bne nf
fcutr0  lda #PRIME_fcutr
        sta fcut0+1
fdurr0  lda #PRIME_fdurr
        sta fdur0+1
nf      lda #0
        sta pwfr,x
        sta pwdir,x
        lda preset+5,y
        lsr
        lsr
        lsr
        sta vibdly,x
        lda noteflg,x
        ora #$40
        sta noteflg,x
        lda preset+7,y
        sta $fd,x
        jmp out

; --------------------------------------------------------------- effects
effects cpx filtowner
        bne noflt
fdur0   lda #PRIME_fdur
        beq noflt
        dec fdur0+1
        clc
fcut0   lda #PRIME_fcut
fvel0   adc #PRIME_fvel
        sta fcut0+1
        sta $d416
noflt   lda $fd,x
        and #$0f
        beq novib
        jsr doarp
        jmp pulse
novib   lda noteflg,x
        and #$20
        bne pulse
        lda $fd,x
        and #$10
        beq pulse
        dec vibdly,x
        bpl pulse
        inc vibdly,x
        lda vibph,x
        and #3
        tay
        lda vibdir,y
        bne vadd
        ldy $fc
        sec
        lda nfrqlo,x
        sbc preset+6,y
        sta nfrqlo,x
        bcs vtail
        dec nfrqhi,x
        bne vtail
vadd    ldy $fc
        clc
        lda nfrqlo,x
        adc preset+6,y
        sta nfrqlo,x
        bcc vtail
        inc nfrqhi,x
vtail   inc vibfr,x
        lda preset+5,y
        and #$0f
        cmp vibfr,x
        bne pulse
        lda #0
        sta vibfr,x
        inc vibph,x

; ----------------------------------------------------------------- pulse
pulse   ldy $fc
        lda preset+4,y
        sta $fc
        lda $fd,x
        and #$40
        beq pvib
        clc
        lda $fc
        adc pwlo,x
        sta pwlo,x
        lda $fc
        adc pwhi,x
        sta pwhi,x
        jmp out
pvib    lda $fd,x
        and #$20
        beq out
        lda pwdir,x
        beq psub
        clc
        lda pwlo,x
        adc $fc
        sta pwlo,x
        bcc ptail
        inc pwhi,x
        bcs ptail
psub    sec
        lda pwlo,x
        sbc $fc
        sta pwlo,x
        bcs ptail
        dec pwhi,x
ptail   inc pwfr,x
        lda $fc
        and #$0f
        cmp pwfr,x
        bne out
        lda #0
        sta pwfr,x
        lda pwdir,x
        eor #$01
        sta pwdir,x

; ---------------------------------------------------------------- output
out     ldy vbase,x
        lda ctrlw,x
        sta $d404,y
        lda pwhi,x
        sta $d403,y
        lda pwlo,x
        sta $d402,y
        lda noteflg,x
        and #$20
        beq plain
        lda sl1,x
        and #$01
        beq dosl
        lda rattle,x
        eor #$ff
        sta rattle,x
        bne plain
dosl    clc
        lda sfrqlo,x
        adc sl1,x
        sta sfrqlo,x
        sta $d400,y
        lda sfrqhi,x
        adc sl2,x
        sta sfrqhi,x
        sta $d401,y
        rts
plain   lda nfrqlo,x
        sta $d400,y
        lda nfrqhi,x
        sta $d401,y
        rts

; -------------------------------------------------------------- arpeggio
doarp   tay
        lda arplo,y
        sta $fa
        lda arphi,y
        sta $fb
        ldy arppos,x
        lda ($fa),y
        and gmask,x
        sta ctrlw,x
        iny
        lda ($fa),y
        bmi aabs
        clc
        adc curnote,x
aabs    and #$7f
        sta anote0+1
        iny
        lda ($fa),y
        beq askip
        sta fcut0+1
askip   iny
        lda ($fa),y
        cmp #$fe
        bcc asave
        beq astop
        ldy #0
        beq asave
astop   lda $fd,x
        and #$f0
        sta $fd,x
asave   tya
        sta arppos,x
anote0  ldy #$1f
        lda freqlo,y
        sta nfrqlo,x
        lda freqhi,y
        sta nfrqhi,x
        rts
"""


def compose_asm(m) -> str:
    """Full engine + data for `m` as xa65 source."""
    body = ENGINE.replace('SPEED', '$%02X' % m.speed)
    for k in ('fcutr', 'fdurr', 'fdur', 'fcut', 'fvel'):
        body = body.replace('PRIME_' + k, '$%02X' % m.prime.get(k, 0))
    return body + chr(10) + _data(m)


def build_sid(m, title: str = '', author: str = '',
              released: str = '') -> bytes:
    """Assemble `m` into a complete PSID file."""
    blob = assemble(compose_asm(m))
    # inline-load encoding: header load=0, the body's first two bytes carry
    # the real load address (passing BOTH shifts the image by two bytes)
    hdr = build_header(load=0, init=LOAD, play=LOAD + 3,
                       songs=1, start_song=1, speed=0,
                       title=title or m.title, author=author or m.author,
                       released=released or m.released)
    return hdr + LOAD.to_bytes(2, 'little') + blob
