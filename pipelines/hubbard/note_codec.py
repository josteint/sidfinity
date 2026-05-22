"""note_codec.py — pluggable note-data packers for the Commando codegen.

A NoteCodec is the swappable unit that decides how a voice's pattern
note-data is serialised into the SID and decoded by the 6502 engine.
It owns exactly the format-specific parts and nothing else:

  encode(patterns) -> (pattern_byte_lists, extra_data_asm)
      The Python encoder. `patterns` is a list of patterns, each a
      list of engine_model Note objects. Returns one byte-list per
      pattern — byte 0 is the note count — plus any extra data tables
      as xa65 `.byt` source.
  note_asm   the 6502 source defining `load_note` (+ its helpers).
  zp_asm     the codec's private zero-page equates.

Everything else — the orderlist, set_patptr / next_orderidx, the
effects, note_idx and seq_idx semantics — is engine-generic. Adding a
packer is a new class with these three members; nothing else changes.

Pattern convention (shared by every codec): byte 0 of a pattern is the
note count, so the generic set_patptr knows where a pattern ends
without a format-specific terminator.
"""

from __future__ import annotations


class _BitWriter:
    """MSB-first bit stream."""

    def __init__(self):
        self.bits: list[int] = []

    def write(self, value: int, n: int) -> None:
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def to_bytes(self) -> list[int]:
        out = []
        for i in range(0, len(self.bits), 8):
            b = 0
            for j in range(8):
                b = (b << 1) | (self.bits[i + j] if i + j < len(self.bits)
                                else 0)
            out.append(b)
        return out


class BitPackCodec:
    """Streamable bit-pack — a per-note bit stream, MSB-first:

        tie(1) no_release(1) dur(3 = index into the duration table)
        if not tie: pitch(7)
                    inst-changed(1) [+ instrument(4)]
                    porta(1)        [+ porta payload(7)]

    The engine reads it note-by-note with a per-voice bit buffer; the
    SID stays small with no decompression buffer. note_idx is computed
    as it decodes (cumulative 1/2/3 Hubbard-byte-lengths)."""

    name = 'bitpack'
    dur_bits = 3          # index width — set by encode() from the data
    inst_bits = 4         # instrument-field width — set by encode()

    def encode(self, patterns):
        # one global duration table — the index width adapts to the
        # engine: 3 bits (Commando, <=8 values) up to 5 (<=32). The raw
        # duration field is 5-bit, so 32 is the hard ceiling.
        durs = sorted({n.duration for p in patterns for n in p})
        self.dur_bits = max(3, (len(durs) - 1).bit_length()) if durs else 3
        if self.dur_bits > 5:
            raise ValueError(f'{len(durs)} distinct durations exceed the '
                             f'5-bit duration index')
        dur_index = {d: i for i, d in enumerate(durs)}
        # instrument field — width adapts to the engine's count
        insts = [n.instrument & 0x3F for p in patterns for n in p
                 if not (n.instrument & 0x80)]
        self.inst_bits = max(4, max(insts).bit_length()) if insts else 4

        pat_bytes = []
        for notes in patterns:
            bw = _BitWriter()
            for n in notes:
                no_release = (n.drum_trig >> 7) & 1
                bw.write(1 if n.tie else 0, 1)
                bw.write(no_release, 1)
                bw.write(dur_index[n.duration], self.dur_bits)
                if n.tie:
                    continue
                if n.pitch >= 128:
                    raise ValueError(f'pitch {n.pitch} exceeds the 7-bit field')
                bw.write(n.pitch, 7)
                # instrument — present only when the note changes it
                if not (n.instrument & 0x80):
                    inst = n.instrument & 0x3F
                    bw.write(1, 1)
                    bw.write(inst, self.inst_bits)
                else:
                    bw.write(0, 1)
                # portamento — present only when the note carries one
                porta = n.drum_trig & 0x7F
                if porta:
                    bw.write(1, 1)
                    bw.write(porta, 7)
                else:
                    bw.write(0, 1)
            data = bw.to_bytes()
            pat_bytes.append([len(notes) & 0xFF] + data)

        durtab = durs + [0] * ((1 << self.dur_bits) - len(durs))
        extra = ('durtab: .byt '
                 + ','.join(f'${d & 0xFF:02X}' for d in durtab))
        return pat_bytes, extra

    zp_asm = """
v_bitbuf  = $a8
v_bitcnt  = $ab
rb_acc    = $ae
rb_n      = $af
ln_tie    = $b0
ln_hasb1  = $b1
"""

    note_asm = """
; ===================== BitPackCodec note reader =====================
; load_note - advance voice X to its next note. The pattern is a bit
; stream; v_notesleft (set by set_patptr from the pattern's count
; header) says how many notes remain. note_idx (v_hubidx) is computed
; as the cumulative Hubbard byte-length (1 tie / 2 plain / 3 with an
; extra byte) so the off-table arpeggio reads the right value.
load_note:
ln_chk:
        lda v_notesleft,x
        bne ln_decode
        inc v_orderpos,x       ; pattern exhausted - next orderlist entry
        jsr set_patptr
        lda v_ended,x
        bne ln_ret
        lda v_frozen,x
        bne ln_ret
        jmp ln_chk
ln_ret:
        rts

ln_decode:
        dec v_notesleft,x
        lda #0
        sta v_drumtrig,x      ; defaults - no portamento
        sta ln_hasb1
        jsr getflag           ; tie
        sta ln_tie
        jsr getflag           ; no_release
        sta v_norel,x
        lda #DUR_BITS         ; dur - index into durtab
        sta rb_n
        jsr readbits
        tay
        lda durtab,y
        sec
        sbc #1
        sta v_dur,x
        sta v_durfield,x
        lda ln_tie
        bne ln_tienote
        lda #7                ; pitch
        sta rb_n
        jsr readbits
        sta v_pitch,x
        jsr getflag           ; instrument changed?
        beq ln_noinst
        lda #INST_BITS
        sta rb_n
        jsr readbits          ; new instrument (tie bit clear)
        sta v_instr,x
        inc ln_hasb1
        jmp ln_porta
ln_noinst:
        lda v_instr,x         ; keep the carried instrument, clear tie
        and #$3f
        sta v_instr,x
ln_porta:
        jsr getflag           ; portamento present?
        beq ln_decoded
        lda #7
        sta rb_n
        jsr readbits
        ora #$80              ; bit7 marks the drum trigger
        sta v_drumtrig,x
        inc ln_hasb1
        jmp ln_decoded
ln_tienote:
        lda v_instr,x         ; tie - keep pitch + instrument, set tie bit
        ora #$40
        sta v_instr,x
ln_decoded:
        lda #0
        sta v_tick,x
        ; note_idx += Hubbard byte length (1 tie / 3 extra byte / 2)
        lda ln_tie
        bne ln_nb1
        lda ln_hasb1
        bne ln_nb3
        lda #2
        jmp ln_addnb
ln_nb1: lda #1
        jmp ln_addnb
ln_nb3: lda #3
ln_addnb:
        clc
        adc v_hubidx,x
        sta v_hubidx,x
        ; seq_idx - pre-increment on the pattern's last note
        lda v_notesleft,x
        bne ln_seqcur
        lda #0
        sta v_hubidx,x        ; note_idx wraps to 0 at the pattern end
        jsr next_orderidx
        sta v_seqidx,x
        rts
ln_seqcur:
        lda v_orderpos,x
        sta v_seqidx,x
        rts

; getflag - read one bit for voice X, return it in A as 0 or 1.
getflag:
        jsr getbit
        lda #0
        rol
        rts

; readbits - read rb_n bits (MSB first) for voice X, return them in A.
; The counter is rb_n itself, not Y - getbit clobbers Y on a refill.
readbits:
        lda #0
        sta rb_acc
rb_lp:  jsr getbit
        rol rb_acc
        dec rb_n
        bne rb_lp
        lda rb_acc
        rts

; getbit - next stream bit for voice X into the carry. A per-voice bit
; buffer (v_bitbuf) is refilled a byte at a time from v_patptr.
getbit:
        lda v_bitcnt,x
        bne gb_have
        lda v_patlo,x
        sta notep
        lda v_pathi,x
        sta notep+1
        ldy #0
        lda (notep),y
        sta v_bitbuf,x
        inc v_patlo,x
        bne gb_nc
        inc v_pathi,x
gb_nc:  lda #8
        sta v_bitcnt,x
gb_have:
        dec v_bitcnt,x
        asl v_bitbuf,x
        rts
"""
