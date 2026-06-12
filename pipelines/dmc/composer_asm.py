"""DMC family composer - USF -> our own 6502 engine -> xa65 -> PSID.

Per the CORE TENET this is NOT a reproduction of the DMC player: the
runtime is our own implementation (own memory map, own pattern/track
encoding, own instrument layout - parallel arrays instead of 11-byte
records, pre-flattened pulse step schedules, explicit per-event
durations instead of sticky prefixes). It is judged solely by whether
the rebuilt SID emits the original's per-frame $D400-$D418 write
sequence.

Write-order contract (from pipelines/dmc/v4/disassembly.s):
  init        : $D418 = master vol, then $D400..$D417 = 0 ascending
  per frame   : per voice 0,1,2 (see below), then $D416, $D417
  fetch frame : hard note -> ctrl=$08, AD=$0F, SR=$0F only
                (soft/rest/switch/slide -> full effects writes)
  note init   : SR (sustain override applied), AD,
                [$D418 = filter mode | vol, on filter re-init],
                then cymbal ($D400=$FF,$D401=$FF,$D404=$81) or
                wave step + freq lo,hi, PW lo,hi, ctrl
  steady      : freq lo,hi, PW lo,hi, ctrl (gate logic may prepend
                AD=0, SR=0 on the holding gate-off tick)

The engine holds the family's fixed mechanism tables (freq tables +
the per-note vibrato-depth curve, pipelines/dmc/engine_constants.py);
all musical content comes from the USF.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.usf.types import UsfFile, Pitch
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header, FLAGS_PAL_6581
from pipelines.dmc.engine_constants import FREQ_LO, FREQ_HI, VIBDEPTH

LOAD = 0x1000
NOTE_IDX = {n: i for i, n in enumerate(
    ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}


# ---------------------------------------------------------------------------
# USF -> internal song model
# ---------------------------------------------------------------------------

def _note_num(p: Pitch) -> int:
    return p.octave * 12 + NOTE_IDX[p.name]


def _row_event(row, inst_slot: dict) -> tuple:
    """Map a NoteRow to one engine event tuple."""
    flags = {f.split('=')[0]: (f.split('=')[1] if '=' in f else True)
             for f in row.fx_flags}
    vol = int(flags.get('vol', 0))
    gspd = int(flags.get('glide', 0))
    if row.pitch.is_rest:
        if 'gate_toggle' in flags:
            return ('switch', row.duration)
        return ('rest', row.duration)
    note = _note_num(row.pitch)
    slot = inst_slot[row.instr.id]
    if 'noretrig' in flags and gspd:
        # slide current note to target (DMC glide mode 1)
        return ('slide', gspd, note, row.duration)
    soft = 1 if 'noretrig' in flags else 0
    if 'glide_to' in flags:
        tgt = flags['glide_to']
        sep = tgt[1] if len(tgt) == 3 else '-'
        name = tgt[0] + ('#' if sep == '#' else '')
        target = int(tgt[2:]) * 12 + NOTE_IDX[name]
        return ('note', soft, note, row.duration, slot, vol, gspd, target)
    return ('note', soft, note, row.duration, slot, vol, 0, None)


def _encode_pattern(rows_events: list) -> bytes:
    out = bytearray()
    for ev in rows_events:
        kind = ev[0]
        if kind == 'rest':
            out += bytes([0x02, ev[1] & 0x3F])
        elif kind == 'switch':
            out += bytes([0x03, ev[1] & 0x3F])
        elif kind == 'slide':
            _, gspd, note, dur = ev
            out += bytes([0x04, gspd, note, dur & 0x3F])
        else:
            _, soft, note, dur, slot, vol, gspd, target = ev
            f = soft | (2 if gspd else 0)
            out += bytes([0x01, f, note, dur & 0x3F, slot, vol])
            if gspd:
                out += bytes([gspd, target])
    out.append(0x00)
    return bytes(out)


class _Model:
    """Everything the asm emitter needs, distilled from the USF."""

    def __init__(self, usf: UsfFile):
        self.usf = usf
        self.instruments = list(usf.instruments)
        self.inst_slot = {i.id: k for k, i in enumerate(self.instruments)}
        # filter defs: program key -> slot
        self.filter_slots = {prog: k for k, prog in
                             enumerate(sorted(usf.filter_programs))}
        self.filter_defs = [usf.filter_programs[p]
                            for p in sorted(usf.filter_programs)]
        # global pattern pool (content-deduped) + per subtune/voice tracks
        self.patterns: list[bytes] = []
        pat_ids: dict[bytes, int] = {}
        self.subtunes = []
        for sub in usf.subtunes:
            voices = []
            for v in sub.voices:
                track = bytearray()
                ol = v.orderlist
                pat_by_local = {p.id: p for p in v.patterns}
                for i, e in enumerate(ol.entries):
                    enc = _encode_pattern(
                        [_row_event(r, self.inst_slot)
                         for r in pat_by_local[e].rows])
                    gid = pat_ids.get(enc)
                    if gid is None:
                        gid = len(self.patterns)
                        self.patterns.append(enc)
                        pat_ids[enc] = gid
                    track += bytes([(ol.transpose_at(i) + 64) & 0xFF, gid])
                if ol.stop:
                    track.append(0xFE)
                else:
                    track += bytes([0xFF, ((ol.loop_to or 0) * 2) & 0xFF])
                voices.append(bytes(track))
            sid = sub.init.sid if (sub.init and sub.init.sid) else None
            mvol = sid.master_vol if sid and sid.master_vol is not None else 0x0F
            routing = (sid.filter.res_routing
                       if sid and sid.filter else 0)
            self.subtunes.append({
                'tracks': voices, 'speed': sub.tempo,
                'mvol': mvol, 'routing': routing,
            })
        assert len(self.patterns) <= 255, 'pattern pool overflow'
        # wave program concatenation
        self.wctrl = bytearray()
        self.wfreq = bytearray()
        self.iwave = []          # (start, end, loop) absolute indices
        for inst in self.instruments:
            s = len(self.wctrl)
            self.wctrl += bytes(b & 0xFF for b in inst.waveform)
            self.wfreq += bytes(b & 0xFF for b in (inst.wave_freq or
                                                   [0] * len(inst.waveform)))
            self.iwave.append((s, s + len(inst.waveform),
                               s + min(inst.loop, max(0, len(inst.waveform) - 1))))
        assert len(self.wctrl) <= 255, 'wave pool overflow'

    def iflags(self, inst) -> int:
        f = 0
        if 'drum' in inst.effects:
            f |= 0x01
        if inst.filter_prog.keep_running:
            f |= 0x02
        if inst.pwm.keep_running:
            f |= 0x04
        if inst.envelope.gate_mode == 'open':
            f |= 0x08
        if inst.envelope.gate_mode == 'hold':
            f |= 0x10
        if inst.filter_prog.program:
            f |= 0x20
        if inst.freq_slide_config.mode == 'run':
            f |= 0x40
        if 'noise_attack' in inst.effects:
            f |= 0x80
        return f


# ---------------------------------------------------------------------------
# asm emission
# ---------------------------------------------------------------------------

def _byt(data, per=16) -> str:
    lines = []
    for i in range(0, len(data), per):
        lines.append('        .byt ' + ', '.join(
            f'${b & 0xFF:02X}' for b in data[i:i + per]))
    return '\n'.join(lines) if lines else '        .byt $00'


def compose_dmc_asm(usf: UsfFile) -> str:
    m = _Model(usf)
    insts = m.instruments
    n = len(insts)

    # ---- per-instrument parallel data ----
    iad = [i.adsr[0] for i in insts]
    isr = [i.adsr[1] for i in insts]
    ipwinit = [(i.pwm.init >> 8) & 0x0F for i in insts]
    ipwmin = [i.pwm.min_hi for i in insts]
    ipwmax = [i.pwm.max_hi for i in insts]
    isteps = []
    ipwbase = []
    for i in insts:
        ss = list(i.pwm.speed_steps) or [i.pwm.speed] * 6
        ss = (ss + [ss[-1]] * 6)[:6]
        base = ss[0] & 0x0F
        assert all((s & 0x0F) == base for s in ss), \
            f'inst {i.id}: pulse steps do not share a base nibble'
        ipwbase.append(base)
        isteps += [s & 0xF0 for s in ss] + [0, 0]       # stride 8
    ifdef = [m.filter_slots.get(i.filter_prog.program, 0) for i in insts]
    ivdel = [i.vibrato.onset for i in insts]
    ivwid = [i.vibrato.amplitude for i in insts]
    ivram = []
    for i in insts:
        if i.freq_slide_config.mode == 'run':
            s = i.freq_slide_config
            ivram.append((s.step & 0x7F) | (0x80 if s.initial_dir == 'up' else 0))
        else:
            ivram.append(i.vibrato.ramp & 0xFF)
    iflag = [m.iflags(i) for i in insts]
    iwst = [w[0] for w in m.iwave]
    iwend = [w[1] for w in m.iwave]
    iwloop = [w[2] for w in m.iwave]

    fd = m.filter_defs
    fdres = [(d['res'] << 4) & 0xF0 for d in fd]
    fdmode = [(d['mode'] << 4) & 0xF0 for d in fd]
    fdinit = [d['init'] for d in fd]
    fdrep = [d['repeat'] for d in fd]
    fdstop = [d['stop'] for d in fd]
    fdstep = []
    fddur = []
    for d in fd:
        steps = (d['steps'] + [(0, 0)] * 6)[:6]
        fdstep += [s & 0xFF for s, _ in steps] + [0, 0]
        fddur += [f & 0xFF for _, f in steps] + [0, 0]

    # ---- tune records + tracks + patterns ----
    tune_lines = []
    track_blobs = []
    for si, sub in enumerate(m.subtunes):
        refs = []
        for vi in range(3):
            lbl = f'trk_{si}_{vi}'
            track_blobs.append((lbl, sub['tracks'][vi]))
            refs.append(lbl)
        tune_lines.append(
            f'        .byt <{refs[0]}, >{refs[0]}, <{refs[1]}, >{refs[1]}, '
            f'<{refs[2]}, >{refs[2]}, ${sub["speed"]:02X}, ${sub["mvol"]:02X}, '
            f'${sub["routing"]:02X}, $00, $00, $00, $00, $00, $00, $00')
    def _ptr_tab(pfx):
        lines = []
        for i in range(0, len(m.patterns), 12):
            lines.append('        .byt ' + ', '.join(
                f'{pfx}pat_{k}' for k in range(i, min(i + 12, len(m.patterns)))))
        return '\n'.join(lines)
    pat_lo = _ptr_tab('<')
    pat_hi = _ptr_tab('>')

    idle = [0, 0, 0]
    imask = [0, 0, 0]
    for v in usf.init.voices:
        if v.note is not None:
            idle[v.id - 1] = v.note
        if v.gate_mask is not None:
            imask[v.id - 1] = v.gate_mask
    data = []
    data.append('inote:\n' + _byt(idle))
    data.append('imask:\n' + _byt(imask))
    data.append('freqlo:\n' + _byt(FREQ_LO))
    data.append('freqhi:\n' + _byt(FREQ_HI))
    # off-table overrun window: the original reads past its freq tables
    # into the engine state block; reads the extract certifies as
    # reachable land on the stable prefix, mirrored here byte-for-byte
    # (the original's $1707+ adjacency: 6 track-ptr slots, the three
    # voice constant triplets, then speed + master volume — the last
    # two are the LIVE variables, placed here so the values track).
    data.append('ovrwin:   .dsb 6, 0\n'
                'sidoff:   .byt $00, $07, $0E\n'
                'fbit:     .byt $01, $02, $04\n'
                'fmask:    .byt $FE, $FD, $FB\n'
                'spd:      .dsb 1, 0\n'
                'mvol:     .dsb 1, 0\n'
                '          .dsb 143, 0')
    data.append('vibdepth:\n' + _byt(VIBDEPTH))
    for name, arr in [('iad', iad), ('isr', isr), ('ipwinit', ipwinit),
                      ('ipwmin', ipwmin), ('ipwmax', ipwmax),
                      ('ipwbase', ipwbase),
                      ('ifdef', ifdef), ('ivdel', ivdel), ('ivwid', ivwid),
                      ('ivram', ivram), ('iflag', iflag), ('iwst', iwst),
                      ('iwend', iwend), ('iwloop', iwloop)]:
        data.append(f'{name}:\n' + _byt(arr))
    data.append('isteps:\n' + _byt(isteps))
    for name, arr in [('fdres', fdres), ('fdmode', fdmode),
                      ('fdinit', fdinit), ('fdrep', fdrep),
                      ('fdstop', fdstop)]:
        data.append(f'{name}:\n' + _byt(arr or [0]))
    data.append('fdstep:\n' + _byt(fdstep or [0]))
    data.append('fddur:\n' + _byt(fddur or [0]))
    data.append('wctab:\n' + _byt(m.wctrl))
    data.append('wftab:\n' + _byt(m.wfreq))
    data.append('tunetab:\n' + '\n'.join(tune_lines))
    data.append('patlo:\n' + pat_lo)
    data.append('pathi:\n' + pat_hi)
    for lbl, blob in track_blobs:
        data.append(f'{lbl}:\n' + _byt(blob))
    for i, blob in enumerate(m.patterns):
        data.append(f'pat_{i}:\n' + _byt(blob))
    data_asm = '\n'.join(data)

    return f"""
        * = $1000
        jmp init
        jmp playframe

;; ===================== init (A = subtune) =====================
init:
        pha                          ; save subtune
        lda #$00
        tax
ini_st:
        sta state0,x
        inx
        cpx #(state_end - state0)
        bne ini_st
        pla
        asl
        asl
        asl
        asl                          ; subtune * 16
        tay
        ldx #$00
ini_ptr:
        lda tunetab,y
        sta trkpl,x
        lda tunetab+1,y
        sta trkph,x
        iny
        iny
        inx
        cpx #$03
        bne ini_ptr
        lda tunetab,y                ; +6 = speed
        sta spd
        lda tunetab+1,y              ; +7 = master vol
        sta mvol
        sta $d418                    ; priming (matches the family init)
        lda tunetab+2,y              ; +8 = $D417 routing-shadow priming
        sta shadow17
        ldx #$00
ini_v:
        lda #$01
        sta vactive,x
        sta dur,x                    ; expires on the first tick
        lda inote,x                  ; idle note-state priming
        sta curnote,x
        lda imask,x                  ; idle gate-mask priming
        sta gatemask,x
        inx
        cpx #$03
        bne ini_v
        ; ---- universal reset: silence-clear (ascending, as the family) ----
        ldx #$00
        txa
ini_sid:
        sta $d400,x
        inx
        cpx #$18
        bne ini_sid
        rts

;; ===================== play (once per frame) =====================
playframe:
        dec spdctr
        bpl pf_notick
        lda spd
        sta spdctr
pf_notick:
        ldx #$00
        stx fclaim
        jsr voice
        inx
        jsr voice
        inx
        jsr voice
        lda fcut
        sta $d416
        lda shadow17
        ora fres
        sta $d417
        rts

;; ===================== per-voice tick/fetch =====================
voice:
        lda vactive,x
        beq vo_frame
        lda spd
        cmp spdctr                   ; tick iff counter just reloaded
        bne vo_frame
        dec dur,x
        lda dur,x
        beq fetch
vo_frame:
        jmp frame_entry

fetch:
        lda path,x                   ; pattern still in progress?
        beq f_newpat                 ; (pat_end clears the hi byte)
        jmp patrd
f_newpat:
        lda trkpl,x
        sta $f8
        lda trkph,x
        sta $f9
trkrd:
        ldy trkpos,x
        lda ($f8),y
        cmp #$FE
        bne trk1
        lda #$00                     ; stop: voice off (state freewheels)
        sta vactive,x
        rts
trk1:
        cmp #$FF
        bne trk2
        iny
        lda ($f8),y                  ; loop: byte offset of the loop entry
        sta trkpos,x
        jmp trkrd
trk2:
        sec
        sbc #64                      ; entry byte 0 = transpose + 64
        sta transp,x
        iny
        lda ($f8),y                  ; entry byte 1 = pattern id
        tay
        lda patlo,y
        sta patl,x                   ; 16-bit running pattern pointer
        sta $f8                      ; (patterns may exceed 255 bytes)
        lda pathi,y
        sta path,x
        sta $f9
patrd:
        lda patl,x
        sta $f8
        lda path,x
        sta $f9
        ldy #$00
        lda ($f8),y
        cmp #$01
        beq ev_note
        cmp #$02
        beq ev_rest
        cmp #$03
        beq ev_switch
        cmp #$04
        beq ev_slide
        ; defensive: stray end marker - advance track
        jsr pat_end
        jmp fetch

adv:                                 ; pattern ptr += A (16-bit)
        clc
        adc patl,x
        sta patl,x
        sta $f8
        lda path,x
        adc #$00
        sta path,x
        sta $f9
        rts

ev_rest:
        ldy #$01
        lda ($f8),y
        sta dur,x
        lda #$02
        jsr adv
        jsr peekend
        jmp run_effects

ev_switch:
        ldy #$01
        lda ($f8),y
        sta dur,x
        lda gatemask,x
        eor #$01
        sta gatemask,x
        lda #$02
        jsr adv
        jsr peekend
        jmp run_effects

ev_slide:                            ; glide mode 1: current -> target
        ldy #$01
        lda ($f8),y                  ; speed
        sta glsp,x
        iny
        lda ($f8),y                  ; target (+ transpose)
        clc
        adc transp,x
        sta glb,x
        lda curnote,x
        sta gla,x
        iny
        lda ($f8),y                  ; duration
        sta dur,x
        lda #$04
        jsr adv
        jsr peekend
        jmp run_effects

ev_note:
        ldy #$01
        lda ($f8),y                  ; flags (1=soft 2=glide)
        sta evflags
        iny
        lda ($f8),y                  ; note
        clc
        adc transp,x
        sta curnote,x
        tay
        lda freqlo,y
        sta fbl,x
        lda freqhi,y
        sta fbh,x
        ldy #$03
        lda ($f8),y                  ; duration
        sta dur,x
        iny
        lda ($f8),y                  ; instrument slot
        sta curinst,x
        iny
        lda ($f8),y                  ; vol override
        sta volovr,x
        lda evflags
        and #$02
        beq ev_n_noglide
        ldy #$06
        lda ($f8),y                  ; glide speed
        sta glsp,x
        iny
        lda ($f8),y                  ; glide target (+ transpose)
        clc
        adc transp,x
        sta glb,x
        lda curnote,x                ; glide start = this note
        sta gla,x
        lda #$08
        jsr adv
        jmp ev_n_softq
ev_n_noglide:
        lda #$06
        jsr adv
ev_n_softq:
        lda evflags
        and #$01
        beq ev_n_hard
        jsr peekend                  ; soft (no retrigger) - effects run now
        jmp run_effects
ev_n_hard:
        lda #$00                     ; hard restart prep
        sta accl,x
        sta acch,x
        sta vibdir,x
        sta vibctr,x
        sta rampctr,x
        sta slal,x
        sta slah,x
        ldy sidoff,x
        lda #$08
        sta $d404,y                  ; TEST bit
        lda #$0F
        sta $d405,y                  ; AD = $0F
        sta $d406,y                  ; SR = $0F
        lda #$FF
        sta gatemask,x
        sta pend,x
        jsr peekend
        rts                          ; fetch frame writes nothing else

pat_end:
        lda trkpos,x
        clc
        adc #$02
        sta trkpos,x
        lda #$00
        sta path,x                   ; mark: next fetch reads the track
        rts

peekend:
        ldy #$00
        lda ($f8),y                  ; $f8/$f9 track the advanced position
        bne pk_done
        jsr pat_end
pk_done:
        rts

;; ===================== per-voice frame =====================
frame_entry:
        lda pend,x
        bne fe_ni
        jmp run_effects
fe_ni:
        ;; ----- note init (frame 2 of the note) -----
        lda #$00
        sta pend,x
        sta pwl,x                    ; PW accum lo cleared unconditionally
        sta vstep,x
        lda curinst,x
        sta cinst,x                  ; cache: soft notes don't re-init
        tay
        lda isr,y
        sta tmp
        lda volovr,x
        beq ni_sr
        asl
        asl
        asl
        asl
        sta tmp2                     ; sustain override
        lda tmp
        and #$0F
        ora tmp2
        sta tmp
ni_sr:
        ldy sidoff,x
        lda tmp
        sta $d406,y                  ; SR
        ldy cinst,x
        lda iad,y
        ldy sidoff,x
        sta $d405,y                  ; AD
        ldy cinst,x
        lda iflag,y
        and #$04                     ; keep-running pulse?
        bne ni_filter
        lda ipwinit,y
        sta pwh,x
        lda ipwmin,y
        sta cpwmin,x
        lda ipwmax,y
        sta cpwmax,x
        lda ipwbase,y
        sta cpwbase,x
        lda #$00
        sta pwphase,x
        sta pwdir,x
ni_filter:
        lda iflag,y
        and #$20                     ; filter instrument?
        bne ni_f_on
        lda shadow17
        and fmask,x
        sta shadow17
        jmp ni_vib
ni_f_on:
        lda shadow17
        ora fbit,x
        sta shadow17
        lda iflag,y
        and #$02                     ; keep-running filter?
        bne ni_vib
        lda #$00
        sta fstep
        sta fframe
        lda ifdef,y
        tay                          ; y = def slot (scalar tables)
        asl
        asl
        asl
        sta fbase                    ; slot*8 (step/duration tables)
        lda fdres,y
        sta fres
        lda fdmode,y
        ora mvol
        sta $d418                    ; filter note-init: mode | volume
        lda fdinit,y
        sta fcut
        lda fdrep,y
        sta frep
        lda fdstop,y
        sta fstop
        ldy cinst,x
ni_vib:
        lda ivdel,y
        sta vibdel,x
        lda ivwid,y
        sta vibwid,x
        lda ivram,y
        sta cvram,x
        lda iwst,y
        sta wavepos,x
        lda iflag,y
        sta fxf,x
        ldy curnote,x
        lda vibdepth,y               ; per-note vibrato depth
        sta vstep,x
        lda vibwid,x
        bne ni_vs
        lda #$00
        sta vstep,x                  ; width 0 -> no modulation
ni_vs:
        lda #$02
        sta guard,x                  ; gate logic off for 2 frames
        lda fxf,x
        and #$80                     ; cymbal?
        beq ni_wave
        ldy sidoff,x
        lda #$FF
        sta $d400,y
        sta $d401,y
        lda #$81
        sta $d404,y                  ; gated noise burst, nothing else
        rts
ni_wave:
        jmp wavestep

;; ----- running effects -----
run_effects:
        lda guard,x
        beq fx_gate
        dec guard,x
        jmp fx_pulse
fx_gate:
        lda fxf,x
        and #$10                     ; holding?
        beq fx_g2
        lda dur,x
        cmp #$01                     ; gate off one tick before note end
        bne fx_pulse
        lda #$FE
        sta gatemask,x
        ldy sidoff,x
        lda #$00
        sta $d405,y
        sta $d406,y
        jmp fx_pulse
fx_g2:
        lda fxf,x
        and #$08                     ; open gate?
        bne fx_pulse
        lda #$FE                     ; default: release after 3 gate frames
        sta gatemask,x
fx_pulse:
        lda cinst,x
        asl
        asl
        asl
        clc
        adc pwphase,x
        tay
        lda isteps,y                 ; per-phase step nibble
        clc
        adc cpwbase,x                ; + cached base (0 while idling)
        sta tmp
        lda pwdir,x
        bne fx_pw_dn
        lda pwl,x
        clc
        adc tmp
        sta pwl,x
        lda pwh,x
        adc #$00
        sta pwh,x
        cmp cpwmax,x
        bne fx_filter
        lda #$01
        sta pwdir,x
        jmp fx_pw_ph
fx_pw_dn:
        lda pwl,x
        sec
        sbc tmp
        sta pwl,x
        lda pwh,x
        sbc #$00
        sta pwh,x
        cmp cpwmin,x
        bne fx_filter
        lda #$00
        sta pwdir,x
fx_pw_ph:
        lda pwphase,x
        cmp #$05
        beq fx_filter
        inc pwphase,x
fx_filter:
        lda fxf,x
        and #$20
        beq fx_glide
        lda fclaim
        bne fx_glide
        inx
        stx fclaim                   ; first filter voice claims
        dex
        lda fcut
        cmp fstop
        beq fx_glide
        lda fbase
        clc
        adc fstep
        tay
        lda fdstep,y
        sta tmp
        lda fddur,y
        sta tmp2
        lda fcut
        clc
        adc tmp
        sta fcut
        inc fframe
        lda fframe
        cmp tmp2
        bne fx_glide
        lda #$00
        sta fframe
        inc fstep
        lda fstep
        cmp #$06
        bne fx_glide
        lda frep
        sta fstep
fx_glide:
        lda glsp,x
        beq fx_vibdel
        asl
        asl
        asl
        asl
        sta tmp                      ; step = speed << 4
        lda gla,x
        cmp glb,x
        bcs fx_gl_dn
        lda accl,x                   ; gliding up
        clc
        adc tmp
        sta accl,x
        lda acch,x
        adc #$00
        sta acch,x
        jmp fx_gl_chk
fx_gl_dn:
        lda accl,x                   ; gliding down
        sec
        sbc tmp
        sta accl,x
        lda acch,x
        sbc #$00
        sta acch,x
fx_gl_chk:
        ldy glb,x
        lda accl,x
        clc
        adc fbl,x
        lda acch,x
        adc fbh,x
        cmp freqhi,y                 ; arrived when freq HI matches target
        bne fx_gl_out
        tya
        sta curnote,x
        lda freqlo,y
        sta fbl,x
        lda freqhi,y
        sta fbh,x
        lda #$00
        sta glsp,x
        sta accl,x
        sta acch,x
fx_gl_out:
        jmp wavestep                 ; glide active: no vibrato this frame
fx_vibdel:
        lda vibdel,x
        beq fx_dual
        dec vibdel,x
        jmp wavestep
fx_dual:
        lda fxf,x
        and #$40
        beq fx_vib
        inc dualpar                  ; global half-rate parity
        lda dualpar
        and #$01
        sta dualpar
        bne fx_dual_run
        jmp wavestep
fx_dual_run:
        ldy sidoff,x
        lda fbl,x
        clc
        adc accl,x
        sta tmp
        lda fbh,x
        adc #$00                     ; hi: carry only (as the family does)
        sta tmp2
        lda tmp
        sec
        sbc slal,x
        sta $d400,y
        lda tmp2
        sbc slah,x
        sta $d401,y
        lda cvram,x                  ; slide byte: bit7 = up
        bmi fx_dual_up
        lda slal,x
        clc
        adc cvram,x
        sta slal,x
        lda slah,x
        adc #$00
        sta slah,x
        jmp pwwrite
fx_dual_up:
        and #$7F
        sta tmp
        lda slal,x
        sec
        sbc tmp
        sta slal,x
        lda slah,x
        sbc #$00
        sta slah,x
        jmp pwwrite
fx_vib:
        lda vibdir,x
        bne fx_vib_dn
        lda accl,x
        clc
        adc vstep,x
        sta accl,x
        lda acch,x
        adc #$00
        sta acch,x
        jmp fx_vib_c
fx_vib_dn:
        lda accl,x
        sec
        sbc vstep,x
        sta accl,x
        lda acch,x
        sbc #$00
        sta acch,x
fx_vib_c:
        inc vibctr,x
        lda vibctr,x
        cmp vibwid,x
        bne wavestep
        lda #$00                     ; half-cycle boundary
        sta vibctr,x
        lda vibdir,x
        eor #$01
        sta vibdir,x
        lda rampctr,x
        cmp cvram,x
        beq wavestep
        inc rampctr,x
        lda vibwid,x                 ; swell: width doubles
        asl
        sta vibwid,x

;; ----- wave step + SID writes -----
wavestep:
        ldy cinst,x
        lda fxf,x
        and #$01                     ; drum mode?
        bne ws_drum
        lda wavepos,x
        cmp iwend,y
        bne ws_rd
        lda iwloop,y
        sta wavepos,x
ws_rd:
        tay
        lda wctab,y
        sta wctrl,x
        lda wftab,y
        clc
        adc curnote,x                ; semitone offset -> table rebase
        tay
        lda freqlo,y
        sta fbl,x
        lda freqhi,y
        sta fbh,x
        inc wavepos,x
        jmp sidwrite
ws_drum:
        lda wavepos,x
        cmp iwend,y
        bne ws_drd
        lda iwloop,y
        sta wavepos,x
ws_drd:
        tay
        lda wctab,y
        sta wctrl,x
        lda #$00
        sta fbl,x
        lda wftab,y                  ; absolute freq hi
        sta fbh,x
        inc wavepos,x
sidwrite:
        ldy sidoff,x
        lda fbl,x
        clc
        adc accl,x
        sta $d400,y
        lda fbh,x
        adc acch,x
        sta $d401,y
pwwrite:
        lda pwl,x
        sta $d402,y
        lda pwh,x
        sta $d403,y
        lda wctrl,x
        and gatemask,x
        sta $d404,y
        rts

;; ===================== data (from USF) =====================
{data_asm}

;; ===================== state =====================
state0:
vactive:  .dsb 3, 0
gatemask: .dsb 3, 0
curnote:  .dsb 3, 0
curinst:  .dsb 3, 0
cinst:    .dsb 3, 0
volovr:   .dsb 3, 0
trkpl:    .dsb 3, 0
trkph:    .dsb 3, 0
trkpos:   .dsb 3, 0
patl:     .dsb 3, 0
path:     .dsb 3, 0
transp:   .dsb 3, 0
fbl:      .dsb 3, 0
fbh:      .dsb 3, 0
accl:     .dsb 3, 0
acch:     .dsb 3, 0
dur:      .dsb 3, 0
glsp:     .dsb 3, 0
gla:      .dsb 3, 0
glb:      .dsb 3, 0
pend:     .dsb 3, 0
pwl:      .dsb 3, 0
pwh:      .dsb 3, 0
cpwmin:   .dsb 3, 0
cpwmax:   .dsb 3, 0
cpwbase:  .dsb 3, 0
pwphase:  .dsb 3, 0
pwdir:    .dsb 3, 0
vibdir:   .dsb 3, 0
vibctr:   .dsb 3, 0
rampctr:  .dsb 3, 0
vibdel:   .dsb 3, 0
vibwid:   .dsb 3, 0
cvram:    .dsb 3, 0
vstep:    .dsb 3, 0
wavepos:  .dsb 3, 0
fxf:      .dsb 3, 0
wctrl:    .dsb 3, 0
guard:    .dsb 3, 0
slal:     .dsb 3, 0
slah:     .dsb 3, 0
spdctr:   .dsb 1, 0
shadow17: .dsb 1, 0
dualpar:  .dsb 1, 0
fclaim:   .dsb 1, 0
fstep:    .dsb 1, 0
fframe:   .dsb 1, 0
fbase:    .dsb 1, 0
fcut:     .dsb 1, 0
frep:     .dsb 1, 0
fstop:    .dsb 1, 0
fres:     .dsb 1, 0
tmp:      .dsb 1, 0
tmp2:     .dsb 1, 0
evflags:  .dsb 1, 0
state_end:
        .byt $00
"""


def _sanitize_asm(asm: str) -> str:
    """xa65 treats ':' as a statement separator even inside ';' comments —
    scrub colons (and non-ASCII) out of comment text."""
    out = []
    for line in asm.split('\n'):
        if ';' in line:
            code, _, comment = line.partition(';')
            line = code + '; ' + comment.replace(':', '-').strip()
        out.append(line)
    return '\n'.join(out).encode('ascii', 'replace').decode('ascii')


def build_dmc_sid(usf: UsfFile) -> bytes:
    asm = _sanitize_asm(compose_dmc_asm(usf))
    code = assemble(asm)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        speed=0, title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=FLAGS_PAL_6581)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code
