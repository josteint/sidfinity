"""
simple_codegen.py — Minimal USF → PSID codegen.

No GT2 encoding complexity. Reads notes, steps wave tables, looks up freq table.

Player is ~300 bytes of 6502. Data encoded in simplest possible format.
"""

import os
import sys
import struct
import subprocess


def simple_codegen(song, output_path, orig_sid_path=None):
    """Generate a PSID from a USF Song using a minimal 6502 player."""

    freq_lo = list(song.freq_lo) if song.freq_lo else [0] * 96
    freq_hi = list(song.freq_hi) if song.freq_hi else [0] * 96
    n_freq = len(freq_lo)
    tempo = max(1, song.tempo)
    instruments = song.instruments
    n_inst = len(instruments)

    BASE = 0x1000
    # ZP per voice: 9 bytes
    # +0 tick_ctr, +1/+2 note_ptr, +3/+4 wave_ptr, +5 pw_lo, +6 current_note,
    # +7 pw_speed, +8 release_ctr (counts down to ADSR zero)
    ZP = [0x80, 0x89, 0x92]
    SOFF = [0, 7, 14]

    lines = []
    L = lines.append

    L(f'        * = ${BASE:04X}')
    L(f'        jmp init')
    L(f'        jmp play')
    L('')

    # --- INIT ---
    L('init')
    L('        lda #$0F')
    L('        sta $D418')
    for v in range(3):
        z = ZP[v]
        L(f'        lda #<v{v}pat')
        L(f'        sta ${z+1:02X}')
        L(f'        lda #>v{v}pat')
        L(f'        sta ${z+2:02X}')
        L(f'        lda #1')
        L(f'        sta ${z:02X}')
        L(f'        lda #0')
        L(f'        sta ${z+5:02X}')
        L(f'        sta ${z+7:02X}')
        L(f'        lda #$FF')
        L(f'        sta ${z+8:02X}')  # release_ctr = $FF (no release pending)
    L('        rts')
    L('')

    # --- PLAY ---
    L('play')
    for v in range(3):
        z = ZP[v]
        so = SOFF[v]

        L(f'; --- Voice {v+1} ---')

        # Hard restart: zero ADSR 3 frames before note ends
        L(f'        lda ${z:02X}')           # tick_ctr
        L(f'        cmp #3')
        L(f'        bne v{v}nohr')
        L(f'        lda #0')
        L(f'        sta $D4{so+5:02X}')
        L(f'        sta $D4{so+6:02X}')
        L(f'v{v}nohr')

        L(f'        dec ${z:02X}')
        L(f'        beq v{v}new')
        L(f'        jmp v{v}wave')
        L('')

        # New note
        L(f'v{v}new')
        L(f'        ldy #0')
        L(f'        lda (${z+1:02X}),y')
        L(f'        cmp #$FF')
        L(f'        bne v{v}note')
        L(f'        jmp v{v}done')

        L(f'v{v}note')
        L(f'        sta ${z+6:02X}')       # current_note
        L(f'        iny')
        L(f'        lda (${z+1:02X}),y')    # duration
        if tempo == 1:
            pass
        else:
            L(f'        tax')
            L(f'        lda #0')
            L(f'v{v}m    clc')
            L(f'        adc #${tempo:02X}')
            L(f'        dex')
            L(f'        bne v{v}m')
        L(f'        sta ${z:02X}')          # tick_ctr

        # instrument ID
        L(f'        iny')
        L(f'        lda (${z+1:02X}),y')
        L(f'        tax')
        L(f'        lda iad,x')
        L(f'        sta $D4{so+5:02X}')
        L(f'        lda isr,x')
        L(f'        sta $D4{so+6:02X}')
        # PW init
        L(f'        lda ipwl,x')
        L(f'        sta $D4{so+2:02X}')
        L(f'        sta ${z+5:02X}')        # pw_lo accumulator
        L(f'        lda ipwh,x')
        L(f'        sta $D4{so+3:02X}')
        # PW speed
        L(f'        lda ipws,x')
        L(f'        sta ${z+7:02X}')
        # Wave table ptr
        L(f'        lda iwl,x')
        L(f'        sta ${z+3:02X}')
        L(f'        lda iwh,x')
        L(f'        sta ${z+4:02X}')
        # Release counter from instrument
        L(f'        lda irel,x')
        L(f'        sta ${z+8:02X}')

        # advance note_ptr by 3
        L(f'        clc')
        L(f'        lda ${z+1:02X}')
        L(f'        adc #3')
        L(f'        sta ${z+1:02X}')
        L(f'        bcc v{v}wave')
        L(f'        inc ${z+2:02X}')
        L('')

        # Wave table processing
        L(f'v{v}wave')
        L(f'        ldy #0')
        L(f'        lda (${z+3:02X}),y')
        L(f'        cmp #$FF')
        L(f'        bne v{v}wok')

        # Loop: read 2-byte target address
        L(f'        iny')
        L(f'        lda (${z+3:02X}),y')
        L(f'        tax')
        L(f'        iny')
        L(f'        lda (${z+3:02X}),y')
        L(f'        sta ${z+4:02X}')
        L(f'        stx ${z+3:02X}')
        L(f'        ldy #0')
        L(f'        lda (${z+3:02X}),y')

        L(f'v{v}wok')
        L(f'        sta $D4{so+4:02X}')     # waveform

        L(f'        iny')
        L(f'        lda (${z+3:02X}),y')     # note offset
        L(f'        clc')
        L(f'        adc ${z+6:02X}')
        L(f'        tax')
        L(f'        lda ftlo,x')
        L(f'        sta $D4{so:02X}')
        L(f'        lda fthi,x')
        L(f'        sta $D4{so+1:02X}')

        # Advance wave_ptr by 2
        L(f'        clc')
        L(f'        lda ${z+3:02X}')
        L(f'        adc #2')
        L(f'        sta ${z+3:02X}')
        L(f'        bcc v{v}pw')
        L(f'        inc ${z+4:02X}')

        # PW modulation
        L(f'v{v}pw')
        L(f'        lda ${z+5:02X}')
        L(f'        clc')
        L(f'        adc ${z+7:02X}')
        L(f'        sta ${z+5:02X}')
        L(f'        sta $D4{so+2:02X}')

        L(f'v{v}done')
        L('')

    L('        rts')
    L('')

    # --- DATA ---

    # Freq table
    L('ftlo')
    for i in range(0, n_freq, 16):
        L('        .byte ' + ','.join(f'${b:02X}' for b in freq_lo[i:i+16]))
    L('fthi')
    for i in range(0, n_freq, 16):
        L('        .byte ' + ','.join(f'${b:02X}' for b in freq_hi[i:i+16]))
    L('')

    # Instrument columns
    L('iad')
    L('        .byte ' + ','.join(f'${inst.ad:02X}' for inst in instruments))
    L('isr')
    L('        .byte ' + ','.join(f'${inst.sr:02X}' for inst in instruments))
    L('ipwl')
    L('        .byte ' + ','.join(f'${inst.pulse_width & 0xFF:02X}' for inst in instruments))
    L('ipwh')
    L('        .byte ' + ','.join(f'${(inst.pulse_width >> 8) & 0x0F:02X}' for inst in instruments))
    # PW speed
    pw_speeds = []
    for inst in instruments:
        spd = 0
        if inst.pulse_table:
            for ps in inst.pulse_table:
                if not ps.is_set and not ps.is_loop:
                    spd = ps.value & 0xFF
                    break
        pw_speeds.append(spd)
    L('ipws')
    L('        .byte ' + ','.join(f'${s:02X}' for s in pw_speeds))
    # Release frame (frames until ADSR zeroed, $FF = no release)
    release_frames = []
    for inst in instruments:
        # Check wave table for the release point
        # Simple heuristic: count non-loop steps. Release = total_frames - 2 (gate-off 2 frames before end)
        n_steps = sum(1 for s in inst.wave_table if not s.is_loop)
        # But we don't know the note duration here. Use $FF (no auto-release).
        # The ADSR release will be handled by the SID chip's own envelope.
        release_frames.append(0xFF)
    L('irel')
    L('        .byte ' + ','.join(f'${r:02X}' for r in release_frames))
    L('iwl')
    L('        .byte ' + ','.join(f'<wt{i}' for i in range(n_inst)))
    L('iwh')
    L('        .byte ' + ','.join(f'>wt{i}' for i in range(n_inst)))
    L('')

    # Wave tables
    for i, inst in enumerate(instruments):
        L(f'wt{i}')
        wt = inst.wave_table
        if not wt:
            wt = [type('S', (), {'is_loop': False, 'waveform': 0x41, 'note_offset': 0, 'absolute_note': -1})(),
                  type('S', (), {'is_loop': True, 'loop_target': 0, 'waveform': 0, 'note_offset': 0, 'absolute_note': -1})()]

        byte_pos = 0
        for si, step in enumerate(wt):
            if step.is_loop:
                target_label = f'wt{i}b{step.loop_target * 2}'
                L(f'        .byte $FF,<{target_label},>{target_label}')
            else:
                L(f'wt{i}b{byte_pos}')
                offset = step.absolute_note if step.absolute_note >= 0 else step.note_offset
                L(f'        .byte ${step.waveform:02X},${offset & 0xFF:02X}')
                byte_pos += 2
    L('')

    # Pattern data per voice
    for v in range(3):
        L(f'v{v}pat')
        if v < len(song.orderlists):
            for pat_id, transpose in song.orderlists[v]:
                if pat_id < len(song.patterns):
                    for ev in song.patterns[pat_id].events:
                        if ev.type == 'note':
                            note = (ev.note + transpose) & 0xFF
                            dur = max(1, ev.duration) & 0xFF
                            inst_id = ev.instrument & 0xFF
                            L(f'        .byte ${note:02X},${dur:02X},${inst_id:02X}')
        L(f'        .byte $FF')
    L('')

    asm_text = '\n'.join(lines)

    # --- Assemble ---
    asm_path = output_path.replace('.sid', '.s')
    with open(asm_path, 'w') as f:
        f.write(asm_text)

    bin_path = output_path.replace('.sid', '.bin')
    xa = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'xa65', 'xa', 'xa')
    if not os.path.exists(xa):
        xa = 'xa'

    result = subprocess.run([xa, '-o', bin_path, asm_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Assembly failed: {result.stderr}")
        return None

    with open(bin_path, 'rb') as f:
        binary = f.read()

    # --- Build PSID ---
    if orig_sid_path and os.path.exists(orig_sid_path):
        with open(orig_sid_path, 'rb') as f:
            orig = f.read()
        header_len = struct.unpack('>H', orig[6:8])[0]
        header = bytearray(orig[:header_len])
    else:
        header = bytearray(124)
        header[0:4] = b'PSID'
        struct.pack_into('>H', header, 4, 2)
        struct.pack_into('>H', header, 6, 124)

    struct.pack_into('>H', header, 8, 0)
    struct.pack_into('>H', header, 10, BASE)
    struct.pack_into('>H', header, 12, BASE + 3)
    struct.pack_into('>H', header, 14, 1)
    struct.pack_into('>H', header, 16, 1)

    sid_data = bytes(header) + struct.pack('<H', BASE) + binary
    with open(output_path, 'wb') as f:
        f.write(sid_data)

    print(f"SID: {len(sid_data)} bytes ({len(sid_data)/1024:.1f} KB)")
    return output_path
