"""GoatTracker V1 composer — UsfFile -> our own clean 6502 engine -> xa65 -> PSID.

CLEAN REIMPLEMENTATION of the V1.5 algorithm (RE_NOTES §10), NOT a
transliteration: RAM globals (no SMC), our own data layout (separate per-field
instrument arrays, branch-chain command dispatch), gatetimer/HR/tempo as plain
constants. We reproduce the WRITE STREAM (incl. $D404=$09 testbit on new-note),
not the original's byte tricks. All tables are regenerated from USF musical
content — no original bytes are emitted.

The wave-table layout is regenerated in GT's own (wctrl/wnote + $FF-marker)
shape so wave-exec is a faithful clean transcription of v153's mt_waveexec.
"""
from __future__ import annotations

from src.usf.types import UsfFile, Pitch
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header, FLAGS_PAL_6581

LOAD = 0x1000

# V1.5 freq table — a PLAYER CONSTANT (RE_NOTES §2), emitted verbatim.
FREQ_HI = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0a,0x0a,0x0b,0x0c,0x0d,0x0d,0x0e,0x0f,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1a,0x1b,0x1d,0x1f,0x20,
    0x22,0x24,0x27,0x29,0x2b,0x2e,0x31,0x34,0x37,0x3a,0x3e,0x41,
    0x45,0x49,0x4e,0x52,0x57,0x5c,0x62,0x68,0x6e,0x75,0x7c,0x83,
    0x8b,0x93,0x9c,0xa5,0xaf,0xb9,0xc4,0xd0,0xdd,0xea,0xf8,0xff,
]
FREQ_LO = [
    0x17,0x27,0x39,0x4b,0x5f,0x74,0x8a,0xa1,0xba,0xd4,0xf0,0x0e,
    0x2d,0x4e,0x71,0x96,0xbe,0xe8,0x14,0x43,0x74,0xa9,0xe1,0x1c,
    0x5a,0x9c,0xe2,0x2d,0x7c,0xcf,0x28,0x85,0xe8,0x52,0xc1,0x37,
    0xb4,0x39,0xc5,0x5a,0xf7,0x9e,0x4f,0x0a,0xd1,0xa3,0x82,0x6e,
    0x68,0x71,0x8a,0xb3,0xee,0x3c,0x9e,0x15,0xa2,0x46,0x04,0xdc,
    0xd0,0xe2,0x14,0x67,0xdd,0x79,0x3c,0x29,0x44,0x8d,0x08,0xb8,
    0xa1,0xc5,0x28,0xcd,0xba,0xf1,0x78,0x53,0x87,0x1a,0x10,0x71,
    0x42,0x89,0x4f,0x9b,0x74,0xe2,0xf0,0xa6,0x0e,0x33,0x20,0xff,
]

_NOTE_IDX = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def _note_num(p: Pitch) -> int:
    return p.octave * 12 + _NOTE_IDX[p.name]


def _byts(name, data, per=16) -> str:
    out = [f'{name}:']
    for i in range(0, len(data), per):
        out.append('        .byt ' + ', '.join(f'${b & 0xFF:02x}'
                                                for b in data[i:i + per]))
    if not data:
        out.append('        .byt $00')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Flatten the USF into engine tables
# ---------------------------------------------------------------------------

class _Tables:
    def __init__(self, usf: UsfFile):
        self.usf = usf
        p = usf.params.fields
        self.gatetimer = int(p.get('gatetimer', 2))
        self.hr_ad = int(p.get('hr_ad', 0))
        self.hr_sr = int(p.get('hr_sr', 0))
        self.deftempo = int(p.get('default_tempo', 5))
        fi = p.get('filt_init', [0, 0, 0x0F, 0, 0])
        self.filt = list(fi) + [0, 0, 0x0F, 0, 0][len(fi):]
        self.funk = list(p.get('funk', [0, 0]))
        # full filter table (engine steps it); fall back to entry-0 placeholder.
        self.filttbl = list(p.get('filttbl_bytes', [self.filt[1], 0, 0, 0]))
        self.nowavedelay = bool(p.get('nowavedelay', False))
        self.player = p.get('player', 'tracker')   # 'tracker'|'gamemusic' (player2)
        self.p2_pulse_in_mod = bool(p.get('p2_pulse_in_mod', False))  # subA emission
        self.idle_priming = p.get('idle_priming', [])  # per-voice gate-off freewheel
        # optimized-layout variant: filter is EVENT-DRIVEN (written by setfilter,
        # not a per-frame exec), per-voice order is loadregs-before-pulse, init
        # chntick = tempo (not gatetimer+2).
        self.optimized = bool(p.get('inittick_is_tempo'))
        self.inittick = self.deftempo if self.optimized \
            else (self.gatetimer + 2) & 0xFF
        # freq table is PER-PLAYER (carried in USF); fall back to v153 constant.
        # Length is 2*N (lo then hi); N=128 captures the off-table window (C6).
        if usf.freq_table and len(usf.freq_table) >= 192:
            half = len(usf.freq_table) // 2
            self.freqlo = list(usf.freq_table[:half])
            self.freqhi = list(usf.freq_table[half:2 * half])
        else:
            self.freqlo = FREQ_LO
            self.freqhi = FREQ_HI

        insts = {i.id: i for i in usf.instruments}
        self.ninst = (max(insts) + 1) if insts else 1
        n = self.ninst
        self.instad = [0] * n; self.instsr = [0] * n
        self.instpulse = [0] * n; self.instpulsespd = [0] * n
        self.instpulselo = [0] * n; self.instpulsehi = [0] * n
        self.instfilter = [0] * n; self.instwave = [0] * n
        self.wctrl = [0]; self.wnote = [0]            # index 0 = no program
        for iid in range(1, n):
            inst = insts.get(iid)
            if inst is None:
                continue
            ad, sr = inst.adsr
            self.instad[iid] = ad; self.instsr[iid] = sr
            self.instpulse[iid] = inst.pwm.init
            self.instpulsespd[iid] = inst.pwm.speed & 0xFE  # bit0=HR flag (0=HR on)
            self.instpulselo[iid] = inst.pwm.min_hi
            self.instpulsehi[iid] = inst.pwm.max_hi
            self.instfilter[iid] = inst.filter_prog.program
            steps = list(zip(inst.waveform, inst.wave_freq))
            if steps:
                start = len(self.wctrl)
                self.instwave[iid] = start
                for left, right in steps:
                    self.wctrl.append(left & 0xFF)
                    self.wnote.append(right & 0xFF)
                # marker: wctrl=$FF, wnote = ABSOLUTE loop-target index (our own
                # clean scheme — engine loads it directly, no carry arithmetic).
                # lp == -1 → STOP (wnote=0 → engine sets waveptr=0, continuous
                # fx takes over — the toneporta slide etc.).
                lp = inst.loop if inst.loop is not None else (len(steps) - 1)
                self.wctrl.append(0xFF)
                self.wnote.append(0 if lp < 0 else (start + lp) & 0xFF)

        sub = usf.subtunes[0]
        # Global pattern slots: each voice's USF patterns (0-based contiguous)
        # map to a flat slot table; the orderlist stores the GLOBAL slot so the
        # engine indexes pattlo,chnpattnum directly. (Slots must stay < $D0 to
        # avoid colliding with orderlist REPEAT/TRANS/LOOP markers.)
        self.voices = []
        base = 0
        for v in sub.voices:
            self.voices.append(self._voice_tables(v, base))
            base += len(v.patterns)

    def _voice_tables(self, v, base):
        pat_bytes = [(pat.id, _encode_pattern(pat.rows, self.player))
                     for pat in sorted(v.patterns, key=lambda p: p.id)]
        ol = v.orderlist
        order = bytearray()
        entry_off = []
        cur_trans = 0
        for i, pn in enumerate(ol.entries):
            t = ol.transpose_at(i)
            if t != cur_trans:
                order.append((t + 0xF0) & 0xFF)
                cur_trans = t
            rep = ol.repeat_at(i)
            if rep > 1:
                order.append((0xD0 + (rep - 1)) & 0xFF)
            entry_off.append(len(order))
            order.append((base + pn) & 0xFF)            # GLOBAL slot
        loop_off = entry_off[ol.loop_to] if (ol.loop_to is not None
                                             and entry_off) else 0
        order.append(0xFF)
        order.append(loop_off)
        return {'order': bytes(order), 'patterns': pat_bytes}


def _encode_pattern(rows, player='tracker') -> bytes:
    out = bytearray()
    for r in rows:
        cmd, param = _fx_to_cmd(r.fx_flags, player)
        if r.pitch.is_rest and not r.fx_flags and r.duration > 1:
            out.append((256 - r.duration) & 0xFF)         # packed rest
            continue
        if r.pitch.is_rest:
            note = 0x5E if 'keyoff' in r.fx_flags else 0x5F
        else:
            note = _note_num(r.pitch)
        inst = r.instr.id if r.instr else 0
        if cmd is not None:
            out.append(note)                              # note WITH command
            out.append(((inst & 0x1F) << 3) | (cmd & 7))
            out.append(param & 0xFF)
        elif inst:
            out.append(note)                              # instr change needs cmd form
            out.append(((inst & 0x1F) << 3) | 0)
            out.append(0)
        else:
            out.append((note + 0x60) & 0xFF)              # note-only ($60-$BF)
    out.append(0xFF)
    return bytes(out)


def _fx_to_cmd(flags, player='tracker'):
    for f in flags:
        if f == 'keyoff':
            continue
        if f.startswith('arp='):                       # cmd 0 (both players)
            x, y, s = (int(t) for t in f[4:].split(','))
            return 0, (s << 7) | ((x & 7) << 4) | (y & 0xF)
        if f.startswith('porta='):                     # cmd 3 (both)
            return 3, int(f.split('=')[1])
        if f.startswith('vibrato='):                   # cmd 4 (both)
            a, w = (int(t) for t in f[8:].split(','))
            return 4, ((a & 0xF) << 4) | (w & 0xF)
        if f.startswith('srr='):                       # cmd 6 (both: SR/SETSUSTAIN)
            return 6, int(f.split('=')[1])
        if f.startswith('tempo='):                     # cmd 7 (both)
            return 7, int(f.split('=')[1])
        if player == 'gamemusic':                      # player2 command set
            if f.startswith('glide_up='):              # cmd 1, signed porta (up)
                return 1, int(f.split('=')[1]) & 0x7F
            if f.startswith('glide_down='):            # cmd 1, signed porta (down=bit7)
                return 1, (int(f.split('=')[1]) & 0x7F) | 0x80
            if f.startswith('fcutadd='):               # cmd 2, SETCUTOFFADD
                return 2, int(f.split('=')[1])
            if f.startswith('fctrl='):                 # cmd 5, SETFILTER ($D417)
                return 5, int(f.split('=')[1])
            continue
        if f.startswith('glide_up='):                  # player1: cmd 1 (porta up)
            return 1, int(f.split('=')[1])
        if f.startswith('glide_down='):                # player1: cmd 2 (porta down)
            return 2, int(f.split('=')[1])
        if f.startswith('filter='):                    # player1: cmd 5 (filter ptr)
            return 5, int(f.split('=')[1])
    return None, None


# ---------------------------------------------------------------------------
# Engine — clean transcription of v1_player1_v153.s mt_play
# ---------------------------------------------------------------------------

def _engine_v2(t: _Tables) -> str:
    """player2 (gamemusic-mode) engine — clean port of v1_player2_125.s (RE_NOTES
    §12/§12b). SMC immediates → RAM vars (filtcut/filtcutadd/filtctrl/filttype);
    chnnext linked list → X=0/7/14 jsr loop; SFX dropped (PSID never calls playsfx).
    Reads OUR data layout (songlo/songhi orderlists via the sequencer, pattlo/patthi
    +chnpattnum patterns, instXXX, wctrl/wnote, freqlo/hi). Global filter sweep at
    frame start, then per-voice; $D404 written DIRECTLY in wave-exec; immediate HR;
    instfilter→global cutoff+type on note-trigger. Idle-note reproduction (the
    C15 phase gate) is layered on after the audible stream converges."""
    DEF = t.deftempo
    # Emission sub-version (RE_NOTES §12d, ledger C16). subB (loadpulse-after-freq):
    # arpfreq falls to loadpulse which writes $D402/$D403 every voice every frame.
    # subA (majority): pulse is written IN the mod path (before freq, skipped on the
    # sequencer frame), and arpfreq/continuous-fx go straight to nextchn (loadpulse
    # is empty). Parametrized so both sub-versions compose from the one engine.
    pw = '        lda chnpulse,x\n        sta $d402,x\n        sta $d403,x\n'
    if t.p2_pulse_in_mod:
        loadpulse_body, pulsewrite_body = '', pw
    else:
        loadpulse_body, pulsewrite_body = pw, ''
    return f"""
ENDPATT = $ff
temp1 = $fc
temp2 = $fd
temp3 = $fe

; ===== init (deferred: first play does the setup = orig frame 0) =====
init:
        sta temp1                ; A = subtune
        asl
        clc
        adc temp1                ; subtune*3 (orderlist base)
        sta initpos
        rts

play:
        lda initpos
        bmi pm_music
        ; ----- deferred init -----
        ldx #0
pi_loop:
        lda initpos
        sta chnsongnum,x
        inc initpos
        lda #0
        sta chnsongptr,x
        sta chnwavetbl,x
        sta chnpulsedir,x
        sta chnrepeat,x
        sta chntrans,x
        sta $d404,x              ; idle ctrl = 0
        lda #{DEF}
        sta chntick,x
        sta chntempo,x
        sta chnnewnote,x         ; nonzero → no newnoteinit until a note loads
        lda #$ff
        sta chnpattptr,x
        txa
        clc
        adc #7
        tax
        cpx #21
        bcc pi_loop
        lda #0
        sta $d415
        sta filtcut
        sta filtcutadd
        sta filtctrl
        sta filttype
        lda #$ff
        sta initpos
        rts

; ===== per-frame music =====
pm_music:
        clc                      ; global filter sweep
        lda filtcut
        adc filtcutadd
        sta filtcut
        sta $d416
        lda filtctrl
        sta $d417
        lda filttype
        ora #$0f                 ; master volume nibble (default $0f)
        sta $d418
        ldx #0
        jsr chnexec
        ldx #7
        jsr chnexec
        ldx #14
        jsr chnexec
        rts

; ===== one channel =====
chnexec:
        ldy chntick,x
        beq cn_newnotes
        bpl cn_noreload
        ldy chntempo,x
cn_noreload:
        dey
        tya
        sta chntick,x
        lda chnpattptr,x
        cmp #ENDPATT
        bcs cn_seq               ; pattptr==ENDPATT → advance orderlist
        clc
        jmp effects
cn_seq:
        jmp sequencer            ; sets pattnum/pattptr, sec, jmp effects2

; ----- fetch a new row at tick 0 -----
cn_newnotes:
        lda #$ff
        sta chntick,x
        ldy chnpattnum,x
        lda pattlo,y
        sta temp1
        lda patthi,y
        sta temp2
        ldy chnpattptr,x
        lda (temp1),y
        iny
        cmp #$60
        bcc gn_cmd
        cmp #$c0
        bcs gn_packrest
        sbc #$5f
        sta temp3
        bcs gn_nocmd
gn_cmd:
        sta temp3
        lda (temp1),y
        and #$f8
        beq gn_skipinst
        lsr
        lsr
        lsr
        sta chninstnum,x
gn_skipinst:
        lda (temp1),y
        and #$07
        sta chncommand,x
        iny
        lda (temp1),y
        sta chncmddata,x
        iny
gn_nocmd:
        lda (temp1),y
        cmp #ENDPATT
        beq gn_endpatt
        tya
gn_endpatt:
        sta chnpattptr,x
        ldy chncommand,x
        lda temp3
        cmp #$5e                 ; keyoff or rest?
        beq gn_keyoff
        bcs gn_rest
gn_normalnote:
        clc
        adc chntrans,x
        sta chnnote,x
        cpy #3                   ; toneportamento? (no HR, no new-note)
        beq gn_rest
        lda #0
        sta chnnewnote,x         ; normal new note
        sta $d405,x              ; immediate hard restart
        sta $d406,x
gn_keyoff:
        lda chnwave,x            ; keyoff: clear gate bit
        and #$fe
        sta $d404,x
gn_rest:
        ; tick0 command dispatch (Y = chncommand)
        lda chncmddata,x
        cpy #2
        beq t0_setcutoffadd
        cpy #5
        beq t0_setfilter
        cpy #6
        beq t0_setsustain
        cpy #7
        beq t0_settempo
        cpy #3
        beq t0_starttp
        jmp effects2             ; arp/porta/vibrato are continuous (tickN)
gn_packrest:
        ldy chnpackrest,x
        bne gp_common
        sta chnpackrest,x
gp_common:
        inc chnpackrest,x
        bne gp_cont
        inc chnpattptr,x
gp_cont:
        jmp effects2

t0_starttp:
        lda #$fe
        sta chnvibcount,x
        jmp effects2
t0_setcutoffadd:
        sta filtcutadd
        jmp effects2
t0_setfilter:
        sta filtctrl
        jmp effects2
t0_setsustain:
        sta $d406,x
        jmp effects2
t0_settempo:
        bmi t0_tempo_one
        sta chntempo
        sta chntempo+7
        sta chntempo+14
        jmp effects2
t0_tempo_one:
        and #$7f
        sta chntempo,x
        jmp effects2

; ===== new-note init (chnnewnote==0) =====
newnoteinit:
        lda #1
        sta chnnewnote,x
        lda #$fe
        sta chnarpcount,x
        sta chnvibcount,x
        ldy chninstnum,x
        lda instfilter,y         ; instfilter → GLOBAL cutoff + type
        beq nn_nofilt
        sta filtcut
        asl
        asl
        asl
        asl
        sta filttype
nn_nofilt:
        lda instpulse,y
        beq nn_skippulse
        sta chnpulse,x
        sta $d402,x
        sta $d403,x
        lda #$80
        bne nn_skippulse2
nn_skippulse:
        lda chnpulsedir,x
        ora #$80
nn_skippulse2:
        sta chnpulsedir,x
        jmp nextchn

; ===== effects =====
effects:
        clc
effects2:
        ldy chninstnum,x
        lda chnnewnote,x
        beq newnoteinit
        bcs ef_pulseok2          ; carry set (from sequencer) → skip pulse mod
        lda chnpulsedir,x
        bpl ef_noadsrinit
        and #$7f
        sta chnpulsedir,x
        lda instwave,y
        sta chnwavetbl,x         ; start wave program (our wctrl/wnote index)
        lda wctrl,y
        sta chnwave,x
        sta $d404,x
        lda instad,y
        sta $d405,x
        lda instsr,y
        sta $d406,x
        lda instwave,y
        bne ef_skipwavetbl       ; wave program runs this frame
ef_noadsrinit:
        lsr
        lda chnpulse,x
        bcs ef_pulsesub
        adc instpulsespd,y
        adc #0
        sta chnpulse,x
        and #$0f
        cmp instpulsehi,y
        bcc ef_pulsewrite
        lda #1
        bne ef_pulsesetdir
ef_pulsesub:
        sbc instpulsespd,y
        sbc #0
        sta chnpulse,x
        and #$0f
        cmp instpulselo,y
        bcs ef_pulsewrite
        lda #0
ef_pulsesetdir:
        sta chnpulsedir,x
ef_pulsewrite:
        ; subA: pulse written here (after the mod ran; skipped on the sequencer
        ; frame, where line `bcs ef_pulseok2` jumps PAST this). subB: empty.
{pulsewrite_body}ef_pulseok2:
        ldy chnwavetbl,x
        bne ef_dowavetbl
        ldy chncommand,x
        beq ef_arpeggio
        lda chncmddata,x
        cpy #1
        bne ef_nt1
        jmp portamento
ef_nt1:
        cpy #3
        bne ef_nt3
        jmp toneportamento
ef_nt3:
        cpy #4
        bne ef_nt4
        jmp vibrato
ef_nt4:
        jmp loadpulse            ; cmds 2/5/6/7 = tick0-only
ef_skipwavetbl:
        jmp loadpulse

; ----- wave table exec (writes $D404 directly) -----
ef_dowavetbl:
        lda wctrl,y
        beq ew_skipwave
        sta chnwave,x
        sta $d404,x
ew_skipwave:
        lda wnote,y
        bmi ew_abs
        clc
        adc chnnote,x
ew_abs:
        and #$7f
        sta temp1
        lda wctrl+1,y
        cmp #$ff
        bne ew_noend
        lda wnote+1,y
        jmp ew_setptr
ew_noend:
        iny
        tya
ew_setptr:
        sta chnwavetbl,x
        ldy temp1
        jmp arpfreq

ef_arpeggio:
        ldy chncmddata,x
        beq loadpulse            ; no arp param
        bpl ea_fast
        lda chntick,x
        and #1
        bne loadpulse
ea_fast:
        ldy chnarpcount,x
        bmi ea_arp1
        bne ea_arp2
ea_arp0:
        ldy chnnote,x
        lda #$ff
        bne ea_setcount
ea_arp2:
        lda chncmddata,x
        and #$0f
        clc
        adc chnnote,x
        tay
        lda #0
        beq ea_setcount
ea_arp1:
        lda chncmddata,x
        and #$70
        lsr
        lsr
        lsr
        lsr
        clc
        adc chnnote,x
        tay
        lda #1
ea_setcount:
        sta chnarpcount,x
arpfreq:
        lda freqlo,y
        sta chnfreqlo,x
        sta $d400,x
        lda freqhi,y
        sta chnfreqhi,x
        sta $d401,x
loadpulse:
{loadpulse_body}nextchn:
        rts

; ----- continuous pitch effects -----
portamento:
        asl
        sta temp1
        bcc freqadd
        bcs freqsub
vibrato:
        sta temp1
        and #$0e
        sta temp2
        lda chnvibcount,x
        bmi vb_nodir2
        cmp temp2
        bcc vb_nodir
        eor #$ff
        jmp vb_done
vb_nodir2:
        clc
vb_nodir:
        adc #2
vb_done:
        sta chnvibcount,x
        lsr
        bcc freqadd
        bcs freqsub
toneportamento:
        ldy chnnote,x
        asl
        sta temp1
        bcs tp_down
tp_up:
        lda chnfreqhi,x
        cmp freqhi,y
        beq tp_upchklo
        bcc freqadd
        bcs tp_found
tp_upchklo:
        lda chnfreqlo,x
        cmp freqlo,y
        bcc freqadd
        bcs tp_found
tp_down:
        lda chnfreqhi,x
        cmp freqhi,y
        beq tp_dnchklo
        bcs freqsub
        bcc tp_found
tp_dnchklo:
        lda chnfreqlo,x
        cmp freqlo,y
        beq tp_found
        bcs freqsub
tp_found:
        jmp arpfreq
freqadd:
        lda chnfreqlo,x
        sta $d400,x
        adc temp1
        sta chnfreqlo,x
        lda chnfreqhi,x
        sta $d401,x
        adc #0
        sta chnfreqhi,x
        jmp loadpulse
freqsub:
        lda chnfreqlo,x
        sta $d400,x
        sbc temp1
        sta chnfreqlo,x
        lda chnfreqhi,x
        sta $d401,x
        sbc #0
        sta chnfreqhi,x
        jmp loadpulse

; ===== sequencer (orderlist advance, our format) → effects2 with carry SET =====
sequencer:
        ldy chnsongnum,x
        lda songlo,y
        sta temp1
        lda songhi,y
        sta temp2
        lda chnrepeat,x
        beq sq_norep
        dec chnrepeat,x
        jmp sq_done2
sq_norep:
        ldy chnsongptr,x
sq_loop:
        lda (temp1),y
        iny
        cmp #$d0
        bcc sq_pat
        cmp #$e0
        bcs sq_trans
        sbc #$cf
        sta chnrepeat,x
        bcs sq_loop
sq_trans:
        cmp #$ff
        bcc sq_notrans
        lda (temp1),y
        tay
        jmp sq_loop
sq_notrans:
        sbc #$ef
        sta chntrans,x
        jmp sq_loop
sq_pat:
        sta chnpattnum,x
        tya
        sta chnsongptr,x
sq_done2:
        lda #0
        sta chnpattptr,x         ; start of pattern
        sec
        jmp effects2
"""


def _engine(t: _Tables) -> str:
    # wave-exec prologue differs by variant: V1.5 has delayed-wave (0-7 = delay
    # via chnarpcount), the no-delay variant just skips on 0 / stores otherwise.
    if t.nowavedelay:
        wave_prologue = ("        lda wctrl,y\n"
                         "        beq we_skipwave          ; 0 = no waveform change\n"
                         "        sta chnwave,x")
    else:
        wave_prologue = ("        lda wctrl,y\n"
                         "        cmp #8                   ; 0-7 = delay\n"
                         "        bcs we_nodelay\n"
                         "        cmp chnarpcount,x\n"
                         "        beq we_skipwave\n"
                         "        inc chnarpcount,x\n"
                         "        jmp pulseexec\n"
                         "we_nodelay:\n"
                         "        sta chnwave,x")
    # Optimized variant: the filter is EVENT-DRIVEN (setfilter writes $D416/
    # $D417/$D418 directly; no per-frame filter exec), and the init writes the
    # filter once via setfilter(0). V1.5: per-frame filter exec writes the
    # shadows; setfilter only sets shadows.
    if t.optimized:
        filter_exec = ''
        init_filter = ('        lda #0\n'
                       '        jsr setfilter            ; write init filter once\n')
        # optimized setfiltersub writes $D418 = filttbl[1] DIRECTLY (no & volmask
        # — the master vol lives in the high nibble of the same byte).
        sf_d417, sf_d418, sf_d416 = ('        sta $d417\n',
                                     '        sta $d418\n',
                                     '        sta $d416\n')
    else:
        filter_exec = (
            '        lda filttime\n'
            '        bne pf_mod\n'
            '        lda filtstep\n'
            '        beq pf_skip\n'
            '        jsr setfilter\n'
            '        jmp pf_skip\n'
            'pf_mod: dec filttime\n'
            '        lda filtcut\n'
            '        clc\n'
            '        adc filtcutadd\n'
            '        sta filtcut\n'
            'pf_skip:\n'
            '        lda filtcut\n'
            '        sta $d416\n'
            '        lda filtctrl\n'
            '        sta $d417\n'
            '        lda filttype\n'
            '        and volmask\n'
            '        sta $d418')
        init_filter = ''
        sf_d417 = sf_d418 = sf_d416 = ''
    return f"""
GATETIMER = ${t.gatetimer:02x}
INITTICK  = ${t.inittick:02x}
HR_AD = ${t.hr_ad:02x}
HR_SR = ${t.hr_sr:02x}
DEFTEMPO = ${t.deftempo:02x}
temp1 = $fc
temp2 = $fd

; ===== init =====
init:
        sta temp1                ; A = subtune
        asl
        clc
        adc temp1                ; subtune*3
        sta initpos
        lda #${t.filt[0]:02x}
        sta filtcut
        lda #${t.filt[1]:02x}
        sta filtctrl
        lda #${t.filt[2]:02x}
        sta filttype
        lda #$ff
        sta volmask
        lda #${t.filt[3]:02x}
        sta filttime
        lda #${t.filt[4]:02x}
        sta filtstep
        rts

; ===== play =====
play:
{filter_exec}
        ldx #0
        jsr execchn
        ldx #7
        jsr execchn
        ldx #14
        jsr execchn
        lda #$ff
        sta initpos              ; mark init complete
        rts

; ===== one channel (X = 0/7/14) =====
execchn:
        lda initpos
        bmi ec_noinit
        sta chnsongnum,x
        inc initpos
        cpx #0
        bne ec_initnf
        lda #0
        sta $d415                ; first channel cutoff lo = 0
{init_filter}ec_initnf:
        lda #DEFTEMPO
        sta chntempo,x
        lda #INITTICK
        sta chntick,x
        lda #$ff
        sta chnpattptr,x
        sta chnnewnote,x
        lda #1
        sta chninstnum,x
        jmp loadregs

ec_noinit:
        dec chntick,x
        bne ec_chktickn
        jmp tick0
ec_chktickn:
        bpl ec_noreload
        lda chntempo,x
        cmp #2
        bcs ec_nofunk
        tay
        eor #1
        sta chntempo,x
        lda funktbl,y
ec_nofunk:
        sta chntick,x
ec_noreload:
        ldy chnwaveptr,x
        beq ec_fxrun
        jmp waveexec
ec_fxrun:
        lda #0
        sta temp2                ; speed hi = 0
        ldy chnfx,x
        lda chnfxparam,x
        cpy #1
        beq tn_portaup
        cpy #2
        beq tn_portadown
        cpy #3
        beq tn_toneport
        cpy #4
        beq tn_vibrato
        cpy #0
        beq tn_arp
        jmp pulseexec            ; fx 5/6/7 idle

; ----- continuous effects (tick N) -----
tn_arp:
        cmp #0
        beq tn_arpzero
        jmp arpeggio
tn_arpzero:
        jmp pulseexec            ; arp param 0 = no-op

tn_portaup:
        jsr makespeed
        clc                      ; freqadd's adc needs carry clear
        jmp freqadd
tn_portadown:
        jsr makespeed
        sec                      ; freqsub's sbc needs carry set
        jmp freqsub

tn_vibrato:
        tay
        and #$f0
        sta temp1                ; speed (delta hi bits)
        tya
        and #$0f
        sta vibcmp
        lda chnarpcount,x
        bmi vib_nodir
        cmp vibcmp
        bcc vib_nodir2
        beq vib_nodir
        eor #$ff
vib_nodir:
        clc
vib_nodir2:
        adc #2
        sta chnarpcount,x
        lsr
        bcc freqadd
        bcs freqsub

tn_toneport:
        ldy chnnote,x
        cmp #0
        beq tp_found2            ; speed 0 = tie
        jsr makespeed
        lda freqlo,y
        sec
        sbc chnfreqlo,x
        sta tplo
        lda freqhi,y
        sbc chnfreqhi,x
        sta tphi
        bmi tp_down
tp_up:  lda temp2
        cmp tphi
        bne tp_up_nl
        lda temp1
        cmp tplo
tp_up_nl:
        bcs tp_found
freqadd:
        lda chnfreqlo,x
        adc temp1
        sta chnfreqlo,x
        lda chnfreqhi,x
        adc temp2
        sta chnfreqhi,x
        jmp pulseexec
tp_down:
        lda tplo
        clc
        adc temp1
        sta tplo
        lda tphi
        adc temp2
        sta tphi
        bpl tp_found
        sec
freqsub:
        lda chnfreqlo,x
        sbc temp1
        sta chnfreqlo,x
        lda chnfreqhi,x
        sbc temp2
        sta chnfreqhi,x
        jmp pulseexec
tp_found:
        lda #0
tp_found2:
        sta chnfxparam,x
        jmp arpfreqreset

arpeggio:
        asl
        lda chnarpcount,x
        pha
        adc #1
        cmp #6
        bcc arp_nov
        lda #0
arp_nov:
        sta chnarpcount,x
        pla
        lsr
        cmp #1
        bcc arp1
        bne arp0
arp2:   lda chnfxparam,x
        and #$0f
        jmp arp_f2
arp0:   lda #0
        jmp arp_f2
arp1:   lda chnfxparam,x
        and #$70
        lsr
        lsr
        lsr
        lsr
arp_f2: clc
        adc chnnote,x
        tay
        jmp arpfreq

; ===== tick 0 =====
tick0:
        lda chnnewfx,x
        tay
        and #$f8
        beq t0_skipinst
        lsr
        lsr
        lsr
        sta chninstnum,x
t0_skipinst:
        tya
        and #$07
        sta chnfx,x
        tay
        lda chnnewfxparam,x
        sta chnfxparam,x
        ; tick0 dispatch on Y
        cpy #3
        beq t0_toneport
        cpy #5
        beq t0_filter
        cpy #6
        beq t0_sr
        cpy #7
        beq t0_tempo
        cpy #0
        beq t0_arp
t0_idle:
        jmp tick0done
t0_arp:
        cmp #0
        beq t0_idle              ; param 0
        lda chnnewnote,x
        bpl t0_idle              ; new note coming -> skip
        ldy chnwaveptr,x
        bne t0_idle              ; wave running -> skip
        jmp arpeggio
t0_toneport:
        lda chnnewnote,x
        bmi t0_idle
        sta chnnote,x
        lda #$ff
        sta chnnewnote,x
        jmp tick0done            ; legato: wave (if running) was NOT restarted;
                                 ; once it STOPs (tgt=0) the continuous toneporta
                                 ; slides chnfreq toward freqtbl[chnnote]
t0_filter:
        jsr setfilter
        jmp tick0done
t0_sr:
        sta $d406,x
        jmp tick0done
t0_tempo:
        bmi t0_tempo_one
        sta chntempo
        sta chntempo+7
        sta chntempo+14
        jmp tick0done
t0_tempo_one:
        cmp #$ef
        beq t0_timing
        bcs t0_fader
        and #$7f
        sta chntempo,x
        jmp tick0done
t0_timing:
        jmp tick0done
t0_fader:
        sta volmask
        jmp tick0done

tick0done:
        lda chnnewnote,x
        bmi tick0nonew
        ; --- new note init ---
        sta chnnote,x
        lda #$ff
        sta chnnewnote,x
        sta chngate,x
        ldy chninstnum,x
        lda instpulse,y
        beq nn_skippulse
        and #$f0
        sta chnpulsedir,x
        sta $d402,x
        lda instpulse,y
        and #$0f
        sta chnpulse,x
        sta $d403,x
nn_skippulse:
        lda instwave,y
        sta chnwaveptr,x
        lda instad,y
        sta $d405,x
        lda chnfx,x
        cmp #6
        beq nn_skipsr
        lda instsr,y
        sta $d406,x
nn_skipsr:
        lda #$09                 ; testbit first-frame ctrl
        sta chnwave,x
        sta $d404,x
        lda instfilter,y
        beq nn_nofilt
        jsr setfilter
nn_nofilt:
        jmp nextchn

tick0nonew:
        ldy chnwaveptr,x
        bne waveexec
        jmp pulseexec
        ; fall into waveexec

; ===== wave table exec =====
waveexec:
{wave_prologue}
we_skipwave:
        lda wnote,y
        bmi we_abs
        clc
        adc chnnote,x
we_abs: and #$7f
        sta temp1
        lda wctrl+1,y            ; peek next step's ctrl
        cmp #$ff
        bne we_noend             ; not the loop marker: advance
        lda wnote+1,y            ; marker: absolute loop-target index
        jmp we_setptr
we_noend:
        iny
        tya
we_setptr:
        sta chnwaveptr,x
        ldy temp1
arpfreqreset:
        lda #0
        sta chnarpcount,x
arpfreq:
        lda freqlo,y
        sta chnfreqlo,x
        lda freqhi,y
        sta chnfreqhi,x

; ===== pulse exec + gate timer =====
pulseexec:
        lda chntick,x
        cmp #GATETIMER
        beq getnewnotes
        lda chnpattptr,x
        cmp #$ff
        bne normalpulse
        jmp sequencer
normalpulse:
        ldy chninstnum,x
        lda instpulsespd,y
        and #$fe
        beq pulseok
        sta temp1
        lda chnpulsedir,x
        lsr
        bcs pulsesub
        asl
        adc temp1
        pha
        lda chnpulse,x
        adc #0
        sta chnpulse,x
        cmp instpulsehi,y
        jmp pulsedone
pulsesub:
        asl
        sec
        sbc temp1
        pha
        lda chnpulse,x
        sbc #0
        sta chnpulse,x
        cmp instpulselo,y
pulsedone:
        sta $d403,x
        pla
        adc #0
        sta chnpulsedir,x
        sta $d402,x
pulseok:
        jmp loadregs

packedrest:
        ldy chnpackrest,x
        bne pr_common
        sta chnpackrest,x
pr_common:
        inc chnpackrest,x
        bne pr_cont
        inc chnpattptr,x
pr_cont:
        jmp rest

; ===== fetch new note from pattern =====
getnewnotes:
        ldy chnpattnum,x
        lda pattlo,y
        sta temp1
        lda patthi,y
        sta temp2
        ldy chnpattptr,x
        lda (temp1),y
        iny
        cmp #$60
        bcc gn_cmd
        cmp #$c0
        bcs packedrest
        sbc #$5f
        sta notenum
        bcs gn_nocmd
gn_cmd: sta notenum
        lda (temp1),y
        sta chnnewfx,x
        iny
        lda (temp1),y
        sta chnnewfxparam,x
        iny
gn_nocmd:
        lda (temp1),y
        cmp #$ff
        beq gn_endpatt
        tya
gn_endpatt:
        sta chnpattptr,x
        lda notenum
        cmp #$5e
        beq gn_keyoff
        bcs rest                 ; > $5e (rest)
        clc
        adc chntrans,x
        sta chnnewnote,x
        lda chnnewfx,x
        and #$07
        cmp #3
        beq rest                 ; toneporta: no HR
        ldy chninstnum,x
        lda instpulsespd,y
        lsr
        bcs gn_nohr
        lda #HR_AD
        sta $d405,x
        lda #HR_SR
        sta $d406,x
gn_nohr:
gn_keyoff:
        lda #$fe
        sta chngate,x
rest:

; ===== register writes =====
loadregs:
        lda chnfreqlo,x
        sta $d400,x
        lda chnfreqhi,x
        sta $d401,x
        lda chnwave,x
        and chngate,x
        sta $d404,x
nextchn:
        rts

; ===== sequencer (orderlist advance) =====
sequencer:
        ldy chnsongnum,x
        lda songlo,y
        sta temp1
        lda songhi,y
        sta temp2
        lda chnrepeat,x
        beq seq_norep
        dec chnrepeat,x
        jmp seq_done2
seq_norep:
        ldy chnsongptr,x
seq_loop:
        lda (temp1),y
        iny
        cmp #$d0
        bcc seq_done
        cmp #$e0
        bcs seq_trans
        sbc #$cf
        sta chnrepeat,x
        bcs seq_loop
seq_trans:
        cmp #$ff
        bcc seq_notrans
        lda (temp1),y
        tay
        jmp seq_loop
seq_notrans:
        sbc #$ef
        sta chntrans,x
        jmp seq_loop
seq_done:
        sta chnpattnum,x
        tya
        sta chnsongptr,x
seq_done2:
        inc chnpattptr,x
        jmp loadregs

; ===== set filter (A = filter step ptr) =====
setfilter:
        tay
        lda filttbl,y
        beq sf_mod
        sta filtctrl
{sf_d417}        lda filttbl+1,y
        sta filttype
{sf_d418}        lda filttbl+2,y
        beq sf_cutskip
        sta filtcut
{sf_d416}sf_cutskip:
        lda #0
        beq sf_common
sf_mod: lda filttbl+2,y
        sta filtcutadd
        lda filttbl+1,y
sf_common:
        sta filttime
        tya
        beq sf_nonext
        lda filttbl+3,y
sf_nonext:
        sta filtstep
        rts

; ===== 16-bit speed from param (param<<2) =====
makespeed:
        asl
        rol temp2
        asl
        rol temp2
        sta temp1
        rts
"""


# ---------------------------------------------------------------------------
# BSS (channel state + globals) — loaded zeroed from the file
# ---------------------------------------------------------------------------

_BSS_VARS = [
    'chntick', 'chntempo', 'chnsongnum', 'chnsongptr', 'chnpattnum',
    'chnpattptr', 'chnrepeat', 'chntrans', 'chnpackrest', 'chnnewfx',
    'chnnewfxparam', 'chnfx', 'chnfxparam', 'chnnote', 'chnnewnote',
    'chninstnum', 'chngate', 'chnwave', 'chnwaveptr', 'chnarpcount',
    'chnfreqlo', 'chnfreqhi', 'chnpulse', 'chnpulsedir',
    # player2 (gamemusic) per-channel vars
    'chncommand', 'chncmddata', 'chnvibcount', 'chnwavetbl',
]


_IDLE_VARS = ['chnnote', 'chnfreqlo', 'chnfreqhi', 'chncommand', 'chncmddata',
              'chnwave', 'chnpulse', 'chnarpcount', 'chnvibcount', 'chninstnum']


def _bss(t=None) -> str:
    out = []
    # globals
    for g in ('initpos', 'filtstep', 'filttime', 'filtcut', 'filtctrl',
              'filttype', 'volmask', 'filtcutadd', 'vibcmp', 'notenum',
              'tplo', 'tphi'):
        out.append(f'{g}:  .dsb 1, 0')
    # player2 idle priming: pre-load the kept channel-state vars (the deferred init
    # does NOT zero these) so the gate-off idle freewheel reproduces the orig's
    # (C15 phase gate — RE_NOTES §12c). Per-voice values at X=0/7/14.
    idle = {}
    if t is not None and getattr(t, 'idle_priming', None):
        cols = list(zip(*t.idle_priming))      # 9 columns, each (v0,v1,v2)
        idle = {n: cols[i] for i, n in enumerate(_IDLE_VARS)}
    # per-channel arrays (X = 0/7/14 → 15 bytes each)
    for v in _BSS_VARS:
        if v in idle:
            bs = [0] * 15
            for vi in range(3):
                bs[vi * 7] = idle[v][vi]
            out.append(f'{v}:  .byt ' + ', '.join(str(b) for b in bs))
        else:
            out.append(f'{v}:  .dsb 15, 0')
    return '\n'.join(out)


def compose_v1_asm(usf: UsfFile) -> str:
    t = _Tables(usf)
    order_blocks, patt_blocks = [], []
    song_lo, song_hi = [], []
    slot_lo, slot_hi, voice_base = [], [], []
    slot = 0
    for ch, vt in enumerate(t.voices):
        song_lo.append(f'<order_{ch}'); song_hi.append(f'>order_{ch}')
        order_blocks.append(_byts(f'order_{ch}', vt['order']))
        voice_base.append(slot)
        for pid, pb in sorted(vt['patterns']):
            slot_lo.append(f'<patt_{ch}_{pid}')
            slot_hi.append(f'>patt_{ch}_{pid}')
            patt_blocks.append(_byts(f'patt_{ch}_{pid}', pb))
            slot += 1

    A = []
    A.append(f'        * = ${LOAD:04x}')
    A.append('        jmp init')
    A.append('        jmp play')
    A.append(_engine_v2(t) if t.player == 'gamemusic' else _engine(t))
    A.append('')
    A.append(_byts('freqlo', t.freqlo))
    A.append(_byts('freqhi', t.freqhi))
    A.append(_byts('instad', t.instad))
    A.append(_byts('instsr', t.instsr))
    A.append(_byts('instpulse', t.instpulse))
    A.append(_byts('instpulsespd', t.instpulsespd))
    A.append(_byts('instpulselo', t.instpulselo))
    A.append(_byts('instpulsehi', t.instpulsehi))
    A.append(_byts('instfilter', t.instfilter))
    A.append(_byts('instwave', t.instwave))
    A.append(_byts('wctrl', t.wctrl))
    A.append(_byts('wnote', t.wnote))
    A.append(_byts('funktbl', t.funk))
    A.append(_byts('filttbl', t.filttbl))             # full filter table
    A.append('songlo:\n        .byt ' + ', '.join(song_lo))
    A.append('songhi:\n        .byt ' + ', '.join(song_hi))
    A.append('pattlo:\n        .byt ' + (', '.join(slot_lo) if slot_lo else '$00'))
    A.append('patthi:\n        .byt ' + (', '.join(slot_hi) if slot_hi else '$00'))
    A.append('voicebase:\n        .byt ' + ', '.join(str(b) for b in voice_base))
    for b in order_blocks:
        A.append(b)
    for b in patt_blocks:
        A.append(b)
    A.append(_bss(t))
    return '\n'.join(A)


def _sanitize(asm: str) -> str:
    out = []
    for line in asm.split('\n'):
        if ';' in line:
            code, _, comment = line.partition(';')
            line = code + '; ' + comment.replace(':', '-').strip()
        out.append(line)
    return '\n'.join(out)


def build_v1_sid(usf: UsfFile) -> bytes:
    asm = _sanitize(compose_v1_asm(usf))
    code = assemble(asm)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=FLAGS_PAL_6581)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code


if __name__ == '__main__':
    import sys
    from pipelines.goattracker.v1.extract.engine_model import parse_sid, extract
    from pipelines.goattracker.v1.extract.to_usf import model_to_usf
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/T/Topaz/Joker.sid'
    usf = model_to_usf(extract(parse_sid(path)))
    sid = build_v1_sid(usf)
    out = 'tmp/joker.sidfinity.sid'
    open(out, 'wb').write(sid)
    print(f'built {out}: {len(sid)} bytes')
