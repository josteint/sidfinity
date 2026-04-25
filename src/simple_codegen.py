"""
simple_codegen.py — Minimal USF → PSID codegen.

No GT2 encoding complexity. Reads notes, steps wave tables, looks up freq table.

Player is ~400 bytes of 6502. Data encoded in simplest possible format.

PW modulation supports two modes per instrument:
  Bidirectional 16-bit sweep (V1-style): pw_hi bounces between pw_min and pw_max,
    stepping by (pw_speed_lo | pw_speed_hi<<8) each frame, flipping direction at
    hi-byte boundaries. pw_lo is kept as computed (not clamped to 0).
  Linear 8-bit accumulation (V3-style): pw_lo wraps freely, pw_hi stays fixed.
    When pw_min == pw_max == $FF, no direction flip ever occurs.

Instrument PulseTable encoding:
  - First non-loop PulseTableStep: speed lo in .value, speed hi in .duration (high byte)
  - First is_set PulseTableStep: pw_min in .value, pw_max in .low_byte
    ($FF/$FF = linear wrap, no flip)

ZP layout per voice (16 bytes at $80/$90/$A0):
  +0  tick_ctr
  +1/+2  note_ptr
  +3/+4  wave_ptr
  +5  pw_lo
  +6  current_note
  +7  pw_speed_lo
  +8  pw_hi
  +9  pw_dir       (0=up, 1=down)
  +10 pw_speed_hi
  +11 pw_min       (min pw_hi boundary; $FF = no min flip)
  +12 pw_max       (max pw_hi boundary; $FF = no max flip)
  +13 saved_pw_lo
  +14 saved_pw_hi
  +15 prev_inst_id

Per-voice was_noise flags (1 byte each) at $B0, $B1, $B2:
  Set to 1 when the current instrument is noise, 0 otherwise.
  Used to detect noise→pulse transitions without reading SID PH register
  (which could falsely match pulse+sync instruments that happen to have pw_hi=$02).
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
    # ZP per voice: 16 bytes
    ZP = [0x80, 0x90, 0xA0]
    SOFF = [0, 7, 14]
    # was_noise flag per voice: 1 byte each at $B0, $B1, $B2
    WN = [0xB0, 0xB1, 0xB2]

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
        wn = WN[v]
        L(f'        lda #<v{v}pat')
        L(f'        sta ${z+1:02X}')
        L(f'        lda #>v{v}pat')
        L(f'        sta ${z+2:02X}')
        L(f'        lda #1')
        L(f'        sta ${z:02X}')           # tick_ctr=1 → triggers new note on first play
        L(f'        lda #0')
        L(f'        sta ${z+5:02X}')          # pw_lo=0
        L(f'        sta ${z+8:02X}')          # pw_hi=0
        L(f'        sta ${z+9:02X}')          # pw_dir=0 (up)
        L(f'        sta ${z+7:02X}')          # pw_speed_lo=0
        L(f'        sta ${z+10:02X}')         # pw_speed_hi=0
        L(f'        sta ${wn:02X}')           # was_noise=0
        L(f'        lda #$FF')
        L(f'        sta ${z+11:02X}')         # pw_min=$FF (no flip)
        L(f'        sta ${z+12:02X}')         # pw_max=$FF (no flip)
        L(f'        sta ${z+15:02X}')         # prev_inst_id=$FF (force PW init on first note)
    L('        rts')
    L('')

    # --- PLAY ---
    L('play')
    for v in range(3):
        z = ZP[v]
        wn = WN[v]
        so = SOFF[v]

        L(f'; --- Voice {v+1} ---')

        L(f'        dec ${z:02X}')
        L(f'        beq v{v}new')
        # Hard restart: zero ADSR when tick_ctr reaches 3 (after dec)
        L(f'        lda ${z:02X}')
        L(f'        cmp #3')
        L(f'        bne v{v}nohr')
        L(f'        lda #0')
        L(f'        sta $D4{so+5:02X}')
        L(f'        sta $D4{so+6:02X}')
        L(f'v{v}nohr')
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
        L(f'        sta ${z+6:02X}')           # current_note
        L(f'        iny')
        L(f'        lda (${z+1:02X}),y')        # duration
        if tempo == 1:
            pass
        else:
            L(f'        tax')
            L(f'        lda #0')
            L(f'v{v}m    clc')
            L(f'        adc #${tempo:02X}')
            L(f'        dex')
            L(f'        bne v{v}m')
        L(f'        sta ${z:02X}')              # tick_ctr

        # instrument ID
        L(f'        iny')
        L(f'        lda (${z+1:02X}),y')
        L(f'        tax')                       # X = instrument index
        L(f'        lda iad,x')
        L(f'        sta $D4{so+5:02X}')
        L(f'        lda isr,x')
        L(f'        sta $D4{so+6:02X}')

        # PW transition logic:
        # 1) same instrument → keep running
        # 2) first note (prev=$FF) → init from instrument
        # 3) pulse→pulse (diff inst, neither is noise) → keep PW running
        # 4) pulse→noise → save pw_lo+pw_hi, load noise PW
        # 5) noise→pulse → restore pw_lo+pw_hi
        #
        # Noise detection uses inoise[x] (1 if first waveform has bit 7 set),
        # NOT ipwh (which is $02 for both noise AND pulse+sync instruments).
        # was_noise flag ($B0/$B1/$B2) tracks whether previous instrument was noise.
        L(f'        cpx ${z+15:02X}')          # same instrument?
        L(f'        beq v{v}nopw')
        L(f'        lda ${z+15:02X}')
        L(f'        cmp #$FF')
        L(f'        beq v{v}pwini')             # first note → init
        # Check if new instrument is noise (inoise table: 1=noise, 0=pulse)
        L(f'        lda inoise,x')
        L(f'        bne v{v}tons')             # pulse→noise
        # New is pulse — check if previous was noise via was_noise flag
        L(f'        lda ${wn:02X}')
        L(f'        bne v{v}frns')              # was noise → restore
        # pulse→pulse: keep PW running ONLY if new instrument has PW modulation
        L(f'        lda ipwslo,x')
        L(f'        ora ipwshi,x')
        L(f'        bne v{v}nopw')              # has modulation → keep running
        L(f'        beq v{v}pwini')             # no modulation → reinit PW
        L(f'v{v}frns')
        # noise→pulse: restore saved pw_lo+pw_hi
        L(f'        lda ${z+13:02X}')
        L(f'        sta ${z+5:02X}')
        L(f'        sta $D4{so+2:02X}')
        L(f'        lda ${z+14:02X}')
        L(f'        sta ${z+8:02X}')
        L(f'        sta $D4{so+3:02X}')
        # Load new instrument's pw speed/min/max (direction preserved)
        L(f'        lda ipwslo,x')
        L(f'        sta ${z+7:02X}')
        L(f'        lda ipwshi,x')
        L(f'        sta ${z+10:02X}')
        L(f'        lda ipwmin,x')
        L(f'        sta ${z+11:02X}')
        L(f'        lda ipwmax,x')
        L(f'        sta ${z+12:02X}')
        L(f'        lda #0')
        L(f'        sta ${wn:02X}')            # was_noise=0 (now in pulse)
        L(f'        jmp v{v}pwdone')
        L(f'v{v}tons')
        # pulse→noise: save pw_lo+pw_hi
        L(f'        lda ${z+5:02X}')
        L(f'        sta ${z+13:02X}')
        L(f'        lda ${z+8:02X}')
        L(f'        sta ${z+14:02X}')
        L(f'v{v}pwini')
        # Init PW from instrument (first note or to-noise).
        # Always update was_noise based on current instrument — this handles
        # both the first-note-is-noise case (prev=$FF path) and pulse→noise.
        L(f'        lda inoise,x')
        L(f'        sta ${wn:02X}')            # was_noise = inoise[x]
        L(f'        lda ipwl,x')
        L(f'        sta ${z+5:02X}')
        L(f'        sta $D4{so+2:02X}')
        L(f'        lda ipwh,x')
        L(f'        sta ${z+8:02X}')
        L(f'        sta $D4{so+3:02X}')
        L(f'        lda #0')
        L(f'        sta ${z+9:02X}')           # pw_dir=0 (start going up)
        L(f'        lda ipwslo,x')
        L(f'        sta ${z+7:02X}')
        L(f'        lda ipwshi,x')
        L(f'        sta ${z+10:02X}')
        L(f'        lda ipwmin,x')
        L(f'        sta ${z+11:02X}')
        L(f'        lda ipwmax,x')
        L(f'        sta ${z+12:02X}')
        L(f'        jmp v{v}pwdone')
        L(f'v{v}nopw')
        # same instrument or pulse→pulse: update speed/min/max
        L(f'        lda ipwslo,x')
        L(f'        sta ${z+7:02X}')
        L(f'        lda ipwshi,x')
        L(f'        sta ${z+10:02X}')
        L(f'        lda ipwmin,x')
        L(f'        sta ${z+11:02X}')
        L(f'        lda ipwmax,x')
        L(f'        sta ${z+12:02X}')
        L(f'v{v}pwdone')
        L(f'        stx ${z+15:02X}')          # update prev_inst_id

        # Wave table ptr
        L(f'        lda iwl,x')
        L(f'        sta ${z+3:02X}')
        L(f'        lda iwh,x')
        L(f'        sta ${z+4:02X}')

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
        L(f'        sta $D4{so+4:02X}')        # waveform

        L(f'        iny')
        L(f'        lda (${z+3:02X}),y')        # note offset
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

        # --- PW modulation ---
        # Write current PW FIRST (init value plays on first frame),
        # then compute next value.
        #
        # Two modes:
        #   Linear 8-bit (pw_max==$FF): add speed_lo to pw_lo only, pw_hi stays fixed.
        #     Carry from pw_lo is NOT propagated to pw_hi (8-bit wrap).
        #     No direction flip ever. pw_min is also $FF (ignored).
        #
        #   Bidirectional 16-bit (pw_max != $FF): full 16-bit add or subtract based on dir.
        #     After add: if pw_hi >= pw_max → set pw_hi=pw_max, flip dir to DOWN.
        #     After sub: if pw_hi <= pw_min → set pw_hi=pw_min, flip dir to UP.
        #     pw_lo is kept as computed (not zeroed at boundary).
        L(f'v{v}pw')
        L(f'        lda ${z+5:02X}')
        L(f'        sta $D4{so+2:02X}')
        L(f'        lda ${z+8:02X}')
        L(f'        sta $D4{so+3:02X}')
        # Skip if speed is zero (both lo and hi)
        L(f'        lda ${z+7:02X}')
        L(f'        ora ${z+10:02X}')
        L(f'        beq v{v}done')

        # Check mode: pw_max==$FF → linear 8-bit, else bidirectional 16-bit
        L(f'        lda ${z+12:02X}')          # pw_max
        L(f'        cmp #$FF')
        L(f'        bne v{v}pwbidi')
        # Linear 8-bit: add speed_lo to pw_lo only, no carry to pw_hi
        L(f'        clc')
        L(f'        lda ${z+5:02X}')
        L(f'        adc ${z+7:02X}')
        L(f'        sta ${z+5:02X}')           # pw_lo wraps freely, pw_hi unchanged
        L(f'        jmp v{v}done')

        # Bidirectional 16-bit
        L(f'v{v}pwbidi')
        # Check direction
        L(f'        lda ${z+9:02X}')           # pw_dir: 0=up, 1=down
        L(f'        bne v{v}pwdn')

        # --- UP: pw += speed (16-bit) ---
        L(f'        clc')
        L(f'        lda ${z+5:02X}')
        L(f'        adc ${z+7:02X}')
        L(f'        sta ${z+5:02X}')           # new pw_lo
        L(f'        lda ${z+8:02X}')
        L(f'        adc ${z+10:02X}')
        L(f'        sta ${z+8:02X}')           # new pw_hi (A = pw_hi)
        # if pw_hi >= pw_max → clamp pw_hi=pw_max, flip to DOWN
        L(f'        cmp ${z+12:02X}')          # CMP pw_max; C=1 if pw_hi >= pw_max
        L(f'        bcc v{v}done')             # pw_hi < pw_max: no flip
        # pw_hi >= pw_max → clamp and flip
        L(f'        ldx ${z+12:02X}')
        L(f'        stx ${z+8:02X}')           # pw_hi = pw_max
        L(f'        lda #1')
        L(f'        sta ${z+9:02X}')           # pw_dir=1 (down)
        L(f'        jmp v{v}done')

        # --- DOWN: pw -= speed (16-bit) ---
        L(f'v{v}pwdn')
        L(f'        sec')
        L(f'        lda ${z+5:02X}')
        L(f'        sbc ${z+7:02X}')
        L(f'        sta ${z+5:02X}')           # new pw_lo
        L(f'        lda ${z+8:02X}')
        L(f'        sbc ${z+10:02X}')
        L(f'        sta ${z+8:02X}')           # new pw_hi (A = pw_hi)
        # if pw_hi <= pw_min → clamp pw_hi=pw_min, flip to UP
        # Test: pw_hi > pw_min → C=1, Z=0 → not flip
        L(f'        cmp ${z+11:02X}')          # CMP pw_min; C=1 if pw_hi >= pw_min
        L(f'        beq v{v}pflp')             # pw_hi == pw_min → flip
        L(f'        bcs v{v}done')             # pw_hi > pw_min: no flip
        L(f'v{v}pflp')
        # pw_hi <= pw_min → clamp and flip
        L(f'        ldx ${z+11:02X}')
        L(f'        stx ${z+8:02X}')           # pw_hi = pw_min
        L(f'        lda #0')
        L(f'        sta ${z+9:02X}')           # pw_dir=0 (up)

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

    # Noise-instrument flag: 1 if the instrument's first waveform has bit 7 set (noise), else 0.
    # Used to detect pulse→noise and noise→pulse transitions correctly.
    # Checking ipwh==$02 is WRONG: pulse+sync instruments (ctrl=$43) also have pw_hi=$02.
    noise_flags = []
    for inst in instruments:
        is_noise = 0
        if inst.wave_table:
            first_step = next((s for s in inst.wave_table if not s.is_loop), None)
            if first_step is not None and (first_step.waveform & 0x80):
                is_noise = 1
        noise_flags.append(is_noise)
    L('inoise')
    L('        .byte ' + ','.join(f'${n:02X}' for n in noise_flags))

    # PW speed (16-bit) and boundary parameters.
    # PulseTableStep encoding:
    #   Non-is_set, non-is_loop step: speed_lo = .value & 0xFF
    #                                  speed_hi = (.duration >> 8) & 0xFF
    #   is_set step:                   pw_min   = .value & 0xFF
    #                                  pw_max   = .low_byte & 0xFF
    #   $FF/$FF = linear 8-bit wrap (no direction flip)
    pw_speeds_lo = []
    pw_speeds_hi = []
    pw_mins = []
    pw_maxes = []
    for inst in instruments:
        spd_lo = 0
        spd_hi = 0
        pw_min = 0xFF   # default: no flip (linear 8-bit wrap)
        pw_max = 0xFF
        if inst.pulse_table:
            for ps in inst.pulse_table:
                if ps.is_loop:
                    continue
                if ps.is_set:
                    pw_min = ps.value & 0xFF
                    pw_max = ps.low_byte & 0xFF
                else:
                    spd_lo = ps.value & 0xFF
                    spd_hi = (ps.duration >> 8) & 0xFF
        pw_speeds_lo.append(spd_lo)
        pw_speeds_hi.append(spd_hi)
        pw_mins.append(pw_min)
        pw_maxes.append(pw_max)

    L('ipwslo')
    L('        .byte ' + ','.join(f'${s:02X}' for s in pw_speeds_lo))
    L('ipwshi')
    L('        .byte ' + ','.join(f'${s:02X}' for s in pw_speeds_hi))
    L('ipwmin')
    L('        .byte ' + ','.join(f'${m:02X}' for m in pw_mins))
    L('ipwmax')
    L('        .byte ' + ','.join(f'${m:02X}' for m in pw_maxes))

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
