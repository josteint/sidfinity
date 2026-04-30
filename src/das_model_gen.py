"""
das_model_gen.py — Das Model codegen. Clean implementation from spec.

Implements docs/das_model.md:
    SID = (T, I, S)
    I = { W, F, P, E }   — programs, not interpreted by engine

The engine evaluates programs mechanically. All engine-specific knowledge
lives in the DECOMPILER (extract function), not the engine (generate_asm).
"""

import os
import sys
import struct
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

SID_PATH = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                         'Hubbard_Rob', 'Commando.sid')
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')
OUT_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_das_model.sid')


# ===================================================================
# DECOMPILER: Extract (T, I, S) from Hubbard binary
# ===================================================================
# This section is Hubbard-specific. It reads the binary and builds
# universal (W, F, P, E) programs from Hubbard's instrument format.

def extract():
    """Extract (T, I, S) from Commando. Hubbard-engine-specific."""
    from rh_decompile import decompile
    from effect_detect import FREQ_PAL
    from py65.devices.mpu6502 import MPU

    decomp = decompile(SID_PATH)

    # --- T: Frequency Table ---
    T = list(FREQ_PAL)  # T[0..95] = standard PAL

    # Extend with runtime values (Hubbard reads past the table)
    with open(SID_PATH, 'rb') as f:
        d = f.read()
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]; code = code[2:]
    mem = bytearray(65536); mem[la:la+len(code)] = code
    m = MPU(); m.memory = bytearray(mem); m.memory[0xFFF0] = 0x00
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[10:12])[0]; m.a = 0
    for _ in range(100000):
        if m.memory[m.pc] == 0x00: break
        m.step()
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[12:14])[0]
    for _ in range(50000):
        if m.memory[m.pc] == 0x00: break
        m.step()
    ft_base = 0x5428
    while len(T) < 120:
        i = len(T)
        addr = ft_base + i * 2
        T.append((m.memory[addr+1] << 8) | m.memory[addr])

    # --- I: Instruments ---
    # Build W and F PROGRAMS from Hubbard's fx_flags.
    # The engine doesn't know about drums/arpeggio — only the decompiler does.

    instruments = []
    speed = decomp.speed if decomp.speed is not None else 2
    hr_frames = 3  # Hubbard hard-restarts 3 frames before note end

    for rh in decomp.instruments:
        ctrl = rh.ctrl

        # W program: sequence of waveform bytes
        # Hubbard's pattern: drum instruments get noise burst ($80) on frames 1-2
        if rh.has_drum:
            w_steps = [ctrl | 0x01, 0x80, 0x80, ctrl & 0xFE]
            w_loop = 3  # sustain loops on last step
        else:
            w_steps = [ctrl | 0x01]  # gate on (engine handles gate-off via E)
            w_loop = 0

        # Arp: Hubbard uses global frame counter bit 0 to alternate +0/+12
        arp_offset = 12 if rh.has_arpeggio else 0

        # fx_flags
        flags = rh.fx_flags if rh.fx_flags is not None else 0

        # Vibrato: byte+5 of instrument table = vibrato depth scaler.
        # When nonzero, a triangle-wave LFO modulates frequency.
        # LFO: (frame_counter & 7) → 0,1,2,3,3,2,1,0 (period 8 frames)
        # Delta: freq[pitch+1] - freq[pitch], right-shifted byte5 times
        # Applied: base_freq + delta * depth, after 6 frames into note
        # rh_decompile.py stores this as vibrato_depth (data[5]).
        vibrato_scale = rh.vibrato_depth if hasattr(rh, 'vibrato_depth') else 0

        # P program: PW modulation
        # fx_flags bit 3 determines PW MODE (not table arp — that's post-1986)
        pw_speed = rh.pwm_speed
        pw_simple = (flags >> 3) & 1  # bit 3
        if pw_speed == 0:
            pw_mode = 'none'
            pw_min = 0xFF; pw_max = 0xFF
        elif pw_simple:
            # Simple increment: pw_lo += pw_speed each frame, 8-bit wrap
            pw_mode = 'linear'
            pw_min = 0xFF; pw_max = 0xFF
        else:
            # Oscillating: bounce pw between $08xx and $0Exx
            pw_mode = 'bidirectional'
            pw_min = 0x08; pw_max = 0x0E

        # E spec: ADSR + gate/adsr timing
        # Vibrato only effective for non-arp instruments (arp overwrites freq).
        eff_vibrato = vibrato_scale if not rh.has_arpeggio else 0
        instruments.append({
            'id': rh.index,
            'W': {'steps': w_steps, 'loop': w_loop},
            'arp_offset': arp_offset,
            'vibrato_scale': eff_vibrato,
            'P': {'speed': pw_speed, 'mode': pw_mode,
                   'min_hi': pw_min, 'max_hi': pw_max,
                   'init_pw': rh.pulse_width},
            'E': {'ad': rh.ad, 'sr': rh.sr,
                   'gate_off_delta': hr_frames,
                   'adsr_zero_delta': hr_frames},
        })

    # --- S: Score ---
    song = decomp.songs[0]
    tick_length = speed + 1
    pat_dict = {p.index: p for p in decomp.patterns}

    score = {'tempo': tick_length, 'voices': []}
    for v_track in song.tracks:
        voice = {'orderlist': [], 'patterns': {}, 'loop': -1}
        for entry in v_track:
            if entry[0] == 'pattern':
                pat_idx = entry[1]
                voice['orderlist'].append(pat_idx)
                if pat_idx not in voice['patterns']:
                    pat = pat_dict[pat_idx]
                    notes = []
                    cur_inst = 0
                    for note in pat.notes:
                        if note.instrument is not None:
                            cur_inst = note.instrument
                        dur = note.duration if note.duration is not None else 0
                        if note.pitch is None:
                            # TIE: use previous note's pitch (preserves hard restart timing)
                            pitch = notes[-1]['pitch'] if notes else 0
                        else:
                            pitch = note.pitch
                        notes.append({
                            'pitch': pitch,
                            'duration': dur + 1,  # Hubbard: counter loads D, decrements to -1
                            'instrument': cur_inst,
                        })
                    voice['patterns'][pat_idx] = notes
            elif entry[0] == 'loop':
                voice['loop'] = entry[1]
        score['voices'].append(voice)

    return T, instruments, score


# ===================================================================
# ENGINE: Generate 6502 assembly
# ===================================================================
# This section is UNIVERSAL. It reads (T, I, S) and generates a player
# that evaluates W, F, P, E mechanically. No engine-specific knowledge.

def generate_asm(T, instruments, score):
    """Generate xa65 assembly. The engine is universal."""
    L = []
    a = L.append

    BASE = 0x1000
    tempo = score['tempo']

    # ZP layout per voice (16 bytes)
    # +0: tick_ctr
    # +1/+2: ol_ptr
    # +3/+4: pat_ptr
    # +5/+6: w_ptr (wave program, 1 byte/step)
    # +7: pw_lo
    # +8: base_note
    # +9: note_len
    # +10: pw_speed
    # +11: pw_hi
    # +12: pw_max    ($00=no mod, $FF=linear, else=bidir max)
    # +13: pw_dir    (0=up, 1=down)
    # +14: prev_inst (previous instrument ID, $FF=none)
    # +15: hub_off   (Hubbard pattern byte offset — tracks T[100] extended table)
    ZP = [0x80, 0x90, 0xA0]
    SOFF = [0, 7, 14]
    FRAME_CTR = 0xB0  # global frame counter (all voices share)
    VIB_TMP = 0xB1    # vibrato temp: delta (freq_hi difference, 1 byte)

    a(f'        * = ${BASE:04X}')
    a(f'        jmp init')
    a(f'        jmp play')
    a('')

    # --- INIT ---
    a('init')
    a('        lda #$0F')
    a('        sta $D418')
    a(f'        lda #$FF')
    a(f'        sta ${FRAME_CTR:02X}')   # global frame counter (INC on first play → 0)
    # T[104] = $4315 from py65 capture (V1/V2 ctrl). Correct after frame 0.
    # First 6 frames have $0000 in original (state not set yet) — accepted.
    for v in range(3):
        z = ZP[v]
        # Load first pattern address from orderlist into pat_ptr
        a(f'        lda v{v}ol')
        a(f'        sta ${z+3:02X}')        # pat_ptr lo
        a(f'        lda v{v}ol+1')
        a(f'        sta ${z+4:02X}')        # pat_ptr hi
        # ol_ptr starts at second entry (first already loaded)
        a(f'        lda #<(v{v}ol+2)')
        a(f'        sta ${z+1:02X}')        # ol_ptr lo
        a(f'        lda #>(v{v}ol+2)')
        a(f'        sta ${z+2:02X}')        # ol_ptr hi
        a(f'        lda #0')
        a(f'        sta ${z+7:02X}')        # pw_lo=0
        a(f'        sta ${z+9:02X}')        # note_len=0
        a(f'        sta ${z+10:02X}')       # pw_speed=0
        a(f'        sta ${z+11:02X}')       # pw_hi=0
        a(f'        sta ${z+12:02X}')       # pw_max=0
        a(f'        sta ${z+13:02X}')       # pw_dir=0 (up)
        a(f'        sta ${z+15:02X}')       # hub_off=0
        a(f'        lda #$FF')
        a(f'        sta ${z+14:02X}')       # prev_inst=$FF (force init on first note)
        a(f'        lda #1')
        a(f'        sta ${z:02X}')          # tick_ctr=1 → triggers first note
    a('        rts')
    a('')

    # --- PLAY ---
    a('play')
    a(f'        inc ${FRAME_CTR:02X}')   # global frame counter (like Hubbard's $5525)
    # Extended table: update T[96+] from live engine state each frame.
    # T[100]: accumulated pattern byte offset for V2 (lo) and V3 (hi)
    a(f'        lda ${ZP[1]+15:02X}')   # V2 hub_off
    a(f'        sta ftlo+100')
    a(f'        lda ${ZP[2]+15:02X}')   # V3 hub_off
    a(f'        sta fthi+100')
    # T[104]: V1/V2 ctrl values. Timing-sensitive (Hubbard reads CURRENT
    # frame V1 ctrl but PREVIOUS frame V2 ctrl). Not worth the complexity
    # since drum frequencies are inaudible under noise waveform.
    # Hubbard processes voices in REVERSE ORDER: V3 → V2 → V1.
    # This affects oscillator phase for ring modulation (V1 uses V3's phase).
    # V3 written first means V3's oscillator phase is set early in the frame,
    # then V1's ring mod reads it late — matching the original's timing.
    # Ω: cycle timing from Hubbard's engine (measured via py65 trace).
    # Eval-path and note-load-path have different cycle budgets.
    # Delays are inserted at the correct branch points.
    # Ω calibrated from actual CPU cycles (py65 processorCycles):
    # V3 eval: orig=133cy, ours=173cy without NOPs → already late, remove padding
    # V2 eval: orig=348cy avg, match with 35 NOPs (70cy)
    # V1 eval: orig=604cy avg, match with 57 NOPs (114cy)
    omega_eval_nops = {2: 0, 1: 35, 0: 57}   # NOPs in eval path per voice
    omega_note_nops = {2: 0, 1: 0, 0: 0}     # NOPs in note_load path per voice

    for v in [2, 1, 0]:
        z = ZP[v]
        so = SOFF[v]

        a(f'; --- Voice {v+1} ---')

        # Step 1: tick counter
        a(f'        dec ${z:02X}')
        a(f'        beq v{v}rd')
        # Ω eval-path delay: pad to match Hubbard's cycle budget
        for _ in range(omega_eval_nops[v]):
            a(f'        nop')
        a(f'        jmp v{v}eval')
        # tick_ctr hit 0 → load new note from pattern
        a(f'v{v}rd')
        a(f'        ldy #0')
        a(f'        lda (${z+3:02X}),y')       # read note from pat_ptr
        a(f'        cmp #$FE')                  # end of pattern marker
        a(f'        bne v{v}nt')
        # End of pattern → read next pattern address from orderlist
        a(f'        lda #0')
        a(f'        sta ${z+15:02X}')            # reset hub_off at pattern boundary
        a(f'        lda #$FF')
        a(f'        sta ${z+14:02X}')            # force inst reload (first note = 3 bytes)
        a(f'        ldy #0')
        a(f'        lda (${z+1:02X}),y')        # pattern addr lo from ol_ptr
        a(f'        sta ${z+3:02X}')
        a(f'        iny')
        a(f'        lda (${z+1:02X}),y')        # pattern addr hi
        a(f'        sta ${z+4:02X}')
        # Advance ol_ptr by 2
        a(f'        clc')
        a(f'        lda ${z+1:02X}')
        a(f'        adc #2')
        a(f'        sta ${z+1:02X}')
        a(f'        bcc v{v}rd')
        a(f'        inc ${z+2:02X}')
        a(f'        jmp v{v}rd')                # re-read from new pattern
        a(f'v{v}nt')
        a(f'        sta ${z+8:02X}')            # base_note
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # duration (in ticks)
        # Convert ticks to frames
        if tempo == 1:
            pass
        else:
            a(f'        tax')
            a(f'        lda #0')
            a(f'v{v}mul  clc')
            a(f'        adc #{tempo}')
            a(f'        dex')
            a(f'        bne v{v}mul')
        a(f'        sta ${z:02X}')              # tick_ctr
        a(f'        sta ${z+9:02X}')            # note_len
        # Read instrument ID
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')
        a(f'        tax')
        a(f'        lda i_ad,x')
        a(f'        sta $D4{so+5:02X}')
        a(f'        lda i_sr,x')
        a(f'        sta $D4{so+6:02X}')
        # PW: only init if instrument changed
        a(f'        cpx ${z+14:02X}')       # same instrument?
        a(f'        beq v{v}skpw')           # yes → keep PW running
        a(f'        stx ${z+14:02X}')       # save new inst id
        # hub_off += 3 (Hubbard: inst change = 3-byte note)
        a(f'        lda ${z+15:02X}')
        a(f'        clc')
        a(f'        adc #3')
        a(f'        sta ${z+15:02X}')
        a(f'        lda i_pwlo,x')
        a(f'        sta $D4{so+2:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        lda i_pwhi,x')
        a(f'        sta $D4{so+3:02X}')
        a(f'        sta ${z+11:02X}')
        a(f'        lda #0')
        a(f'        sta ${z+13:02X}')       # reset pw_dir to UP
        a(f'        jmp v{v}hbd')
        a(f'v{v}skpw')
        # hub_off += 2 (Hubbard: same inst = 2-byte note)
        a(f'        lda ${z+15:02X}')
        a(f'        clc')
        a(f'        adc #2')
        a(f'        sta ${z+15:02X}')
        a(f'v{v}hbd')
        # Always load PW speed/max (even if same inst — harmless)
        a(f'        lda i_pws,x')
        a(f'        sta ${z+10:02X}')
        a(f'        lda i_pwmax,x')
        a(f'        sta ${z+12:02X}')
        # Set W program pointer
        a(f'        lda i_wlo,x')
        a(f'        sta ${z+5:02X}')
        a(f'        lda i_whi,x')
        a(f'        sta ${z+6:02X}')
        # Write freq from note pitch (note-load always writes, even for non-arp)
        a(f'        ldx ${z+8:02X}')              # base_note
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')
        # Advance pat_ptr by 3
        a(f'        clc')
        a(f'        lda ${z+3:02X}')
        a(f'        adc #3')
        a(f'        sta ${z+3:02X}')
        a(f'        bcc v{v}eval')
        a(f'        inc ${z+4:02X}')
        a('')

        # Steps 2-5: evaluate F, W, P, E (Hubbard order: freq → ctrl → pw → adsr)
        a(f'v{v}eval')

        # F: freq — arp instruments alternate +0/+12 every frame.
        # Non-arp instruments: check for vibrato modulation.
        # Vibrato: triangle LFO (period 8), delta from freq table, applied after 6 frames.
        a(f'        ldy ${z+14:02X}')             # instrument ID (prev_inst)
        a(f'        lda i_arp,y')                 # arp_offset (0 or 12)
        a(f'        beq v{v}vib')                 # no arp → check vibrato
        # ARP path
        a(f'        ldx ${z+8:02X}')              # base_note
        a(f'        lda ${FRAME_CTR:02X}')        # global frame counter
        a(f'        and #$01')                    # bit 0
        a(f'        beq v{v}frok')                # even frame → base_note
        a(f'        txa')
        a(f'        clc')
        a(f'        adc i_arp,y')                 # base_note + arp_offset
        a(f'        tax')
        a(f'v{v}frok')
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')
        a(f'        jmp v{v}wrd')

        # VIBRATO path (non-arp instruments only)
        # Only fires when i_vib[inst] != 0 AND note has played >= 6 frames.
        # frames_elapsed = note_len - tick_ctr (both are 1-based counts)
        # LFO depth: (frame_ctr & 7) → triangle 0,1,2,3,3,2,1,0
        # delta = freq_hi[pitch+1] - freq_hi[pitch], right-shifted vibrato_scale times
        # base_freq + delta * depth → write to SID
        a(f'v{v}vib')
        a(f'        lda i_vib,y')                 # vibrato scale (0=none)
        a(f'        beq v{v}wrd')                 # no vibrato → skip freq write entirely
        # Check: note duration_field >= 6 (ticks, NOT frames).
        # Hubbard checks the raw duration from the pattern, not frames elapsed.
        # Short notes (< 6 ticks) never get vibrato.
        # note_len = duration * tempo. So duration = note_len / tempo.
        # Check: note_len >= 6 * tempo (= {6 * tempo} for this song).
        a(f'        lda ${z+9:02X}')              # note_len (frames)
        a(f'        cmp #{6 * tempo}')            # < 6 ticks worth of frames?
        a(f'        bcc v{v}wrd')                 # short note → no vibrato
        # Compute LFO depth: (frame_ctr & 7) → mirror if >= 4 → 0,1,2,3,3,2,1,0
        a(f'        lda ${FRAME_CTR:02X}')
        a(f'        and #$07')
        a(f'        cmp #4')
        a(f'        bcc v{v}vdok')                # < 4 → depth is the raw value
        a(f'        eor #$07')                    # mirror: 4→3, 5→2, 6→1, 7→0
        a(f'v{v}vdok')
        a(f'        pha')                         # push depth
        # Compute freq_hi delta = fthi[pitch+1] - fthi[pitch]
        a(f'        ldx ${z+8:02X}')              # base_note
        a(f'        lda fthi+1,x')
        a(f'        sec')
        a(f'        sbc fthi,x')
        a(f'        sta ${VIB_TMP:02X}')          # save delta
        # Right-shift delta by vibrato_scale+1 times (Hubbard's DEC/BPL loop
        # includes the zero iteration: depth=1 → 2 shifts, depth=2 → 3 shifts).
        a(f'        ldy ${z+14:02X}')             # instrument ID again
        a(f'        ldx i_vib,y')                 # X = vibrato_scale
        a(f'        inx')                         # +1 (DEC/BPL includes zero iteration)
        a(f'v{v}vsr')
        a(f'        lsr ${VIB_TMP:02X}')          # delta >>= 1
        a(f'        dex')
        a(f'        bne v{v}vsr')                 # repeat until scale==0
        # Multiply: acc = delta * depth (depth is on stack)
        # depth=0 means LFO at zero → write unmodulated freq (same as note-load)
        a(f'        pla')                          # pop depth
        a(f'        beq v{v}vwr')                 # depth=0 → write plain base freq
        a(f'        tax')                          # X = depth (loop counter)
        a(f'        lda #0')                       # acc = 0
        a(f'v{v}vmul')
        a(f'        clc')
        a(f'        adc ${VIB_TMP:02X}')           # acc += delta
        a(f'        dex')
        a(f'        bne v{v}vmul')
        # acc = delta * depth. Add to base freq_hi (reload base_note from ZP)
        a(f'        ldx ${z+8:02X}')              # base_note
        a(f'        clc')
        a(f'        adc fthi,x')
        a(f'        sta $D4{so+1:02X}')           # write modulated freq_hi
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')             # write base freq_lo (unmodified)
        a(f'        jmp v{v}wrd')
        # depth=0: write plain freq (no modulation this frame)
        a(f'v{v}vwr')
        a(f'        ldx ${z+8:02X}')              # base_note
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')

        # W: read waveform from w_ptr, write ctrl AFTER freq (gate on sees correct freq)
        a(f'v{v}wrd')
        a(f'        ldy #0')
        a(f'        lda (${z+5:02X}),y')        # waveform byte
        a(f'        cmp #$FF')
        a(f'        bne v{v}wok')
        a(f'        iny')
        a(f'        lda (${z+5:02X}),y')
        a(f'        tax')
        a(f'        iny')
        a(f'        lda (${z+5:02X}),y')
        a(f'        sta ${z+6:02X}')
        a(f'        stx ${z+5:02X}')
        a(f'        ldy #0')
        a(f'        lda (${z+5:02X}),y')

        a(f'v{v}wok')
        # Gate off check: gate off when tick_ctr <= 3 (Hubbard uses cmp #4)
        a(f'        pha')
        a(f'        lda ${z:02X}')
        a(f'        cmp #4')
        a(f'        bcs v{v}gon')
        a(f'        pla')
        a(f'        and #$FE')
        a(f'        jmp v{v}wrt')
        a(f'v{v}gon')
        a(f'        pla')
        a(f'v{v}wrt')
        a(f'        sta $D4{so+4:02X}')

        # Advance w_ptr by 1
        a(f'        inc ${z+5:02X}')
        a(f'        bne v{v}pw')
        a(f'        inc ${z+6:02X}')

        # P: PW modulation — write first, then accumulate
        # Skip PW entirely on note-start frame (Hubbard behavior: PW code
        # doesn't run on the tick that loads a new note). Except first note
        # (frame_ctr==0) where we need the first accumulation.
        # PW: accumulate-then-write (Hubbard order).
        # On note-start: skip accumulation, just write current value.
        a(f'v{v}pw')
        a(f'        lda ${z:02X}')            # tick_ctr
        a(f'        cmp ${z+9:02X}')          # == note_len? (just loaded)
        a(f'        beq v{v}pwwr')            # note-start → skip accum, just write
        # Hubbard order: ACCUMULATE first, then WRITE to SID.
        # The SID sees the POST-accumulation value (same value stored in inst table).
        # Check if modulation active
        a(f'        lda ${z+12:02X}')         # pw_max
        a(f'        beq v{v}pwwr')             # $00 = no modulation → just write
        a(f'        cmp #$FF')
        a(f'        beq v{v}lin')              # $FF = linear (8-bit only)
        # --- Bidirectional 16-bit: accumulate ---
        a(f'        lda ${z+13:02X}')         # pw_dir
        a(f'        bne v{v}dn')
        # UP: pw += speed (16-bit)
        a(f'        clc')
        a(f'        lda ${z+7:02X}')
        a(f'        adc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        bcc v{v}ncu')
        a(f'        inc ${z+11:02X}')
        a(f'v{v}ncu')
        # Check max: flip when pw_hi == pw_max EXACTLY (Hubbard uses BNE)
        a(f'        lda ${z+11:02X}')
        a(f'        cmp ${z+12:02X}')         # pw_hi == pw_max?
        a(f'        bne v{v}pwwr')            # not at boundary → write
        a(f'        lda #1')
        a(f'        sta ${z+13:02X}')         # flip to DOWN
        a(f'        jmp v{v}pwwr')
        # DOWN: pw -= speed (16-bit)
        a(f'v{v}dn')
        a(f'        sec')
        a(f'        lda ${z+7:02X}')
        a(f'        sbc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        bcs v{v}ncd')
        a(f'        dec ${z+11:02X}')
        a(f'v{v}ncd')
        # Check min: flip when pw_hi == $08 EXACTLY (Hubbard uses BNE)
        a(f'        lda ${z+11:02X}')
        a(f'        cmp #$08')                # pw_min
        a(f'        bne v{v}pwwr')            # not at boundary → write
        a(f'        lda #0')
        a(f'        sta ${z+13:02X}')         # flip to UP
        a(f'        jmp v{v}pwwr')
        # --- Linear 8-bit: accumulate ---
        a(f'v{v}lin')
        a(f'        clc')
        a(f'        lda ${z+7:02X}')
        a(f'        adc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')
        # --- WRITE pw to SID AFTER accumulation ---
        a(f'v{v}pwwr')
        a(f'        lda ${z+7:02X}')
        a(f'        sta $D4{so+2:02X}')       # write pw_lo to SID (post-accum)
        a(f'        lda ${z+11:02X}')
        a(f'        sta $D4{so+3:02X}')       # write pw_hi to SID (post-accum)

        # Write accumulated PW back to instrument table (Hubbard's shared mutable state)
        # When another voice (or this voice after instrument switch) loads the same
        # instrument, it reads the accumulated value, not the initial default.
        a(f'v{v}done')
        # PW writeback (shared mutable instrument table)
        a(f'        ldy ${z+14:02X}')         # prev_inst (current instrument ID)
        a(f'        lda ${z+7:02X}')           # pw_lo
        a(f'        sta i_pwlo,y')
        a(f'        lda ${z+11:02X}')          # pw_hi
        a(f'        sta i_pwhi,y')

        # E: ADSR zeroing at tick_ctr==3 (same frame as gate-off starts)
        a(f'        lda ${z:02X}')
        a(f'        cmp #3')
        a(f'        bne v{v}noz')
        a(f'        lda #0')
        a(f'        sta $D4{so+5:02X}')
        a(f'        sta $D4{so+6:02X}')
        a(f'v{v}noz')
        # T[104] is static ($4315) — correct in freq table from extract()
        a('')

    a('        rts')
    a('')

    # --- DATA: Frequency Table ---
    a('ftlo')
    for i in range(0, len(T), 16):
        a('        .byte ' + ','.join(f'${f & 0xFF:02X}' for f in T[i:i+16]))
    a('fthi')
    for i in range(0, len(T), 16):
        a('        .byte ' + ','.join(f'${(f >> 8) & 0xFF:02X}' for f in T[i:i+16]))
    a('')

    # --- DATA: Instrument columns ---
    a('i_ad')
    a('        .byte ' + ','.join(f'${i["E"]["ad"]:02X}' for i in instruments))
    a('i_sr')
    a('        .byte ' + ','.join(f'${i["E"]["sr"]:02X}' for i in instruments))
    a('i_pwlo')
    a('        .byte ' + ','.join(f'${i["P"]["init_pw"] & 0xFF:02X}' for i in instruments))
    a('i_pwhi')
    a('        .byte ' + ','.join(f'${(i["P"]["init_pw"] >> 8) & 0x0F:02X}' for i in instruments))
    a('i_pws')
    a('        .byte ' + ','.join(f'${i["P"]["speed"]:02X}' for i in instruments))
    a('i_pwmax')
    # $00=no modulation, $FF=linear 8-bit, else=bidirectional max boundary
    pwmax_vals = []
    for i in instruments:
        if i['P']['speed'] == 0:
            pwmax_vals.append(0x00)
        elif i['P']['mode'] == 'linear':
            pwmax_vals.append(0xFF)
        else:
            pwmax_vals.append(i['P']['max_hi'])
    a('        .byte ' + ','.join(f'${v:02X}' for v in pwmax_vals))
    a('i_arp')
    a('        .byte ' + ','.join(f'${i["arp_offset"]:02X}' for i in instruments))
    a('i_vib')
    a('        .byte ' + ','.join(f'${i["vibrato_scale"]:02X}' for i in instruments))
    a('i_wlo')
    a('        .byte ' + ','.join(f'<w{i["id"]}' for i in instruments))
    a('i_whi')
    a('        .byte ' + ','.join(f'>w{i["id"]}' for i in instruments))
    a('')

    # --- DATA: Wave programs per instrument (1 byte per step) ---
    for inst in instruments:
        iid = inst['id']
        w = inst['W']
        w_steps = w['steps']
        w_loop = w['loop']

        a(f'w{iid}')
        for step, ws in enumerate(w_steps):
            if step == w_loop:
                a(f'w{iid}lp')   # loop target label
            a(f'        .byte ${ws:02X}')
        # Loop back marker
        a(f'        .byte $FF,<w{iid}lp,>w{iid}lp')
        a('')

    # --- DATA: Patterns (shared, each stored once) ---
    all_pat_indices = set()
    for v in range(3):
        all_pat_indices.update(score['voices'][v]['orderlist'])

    for pat_idx in sorted(all_pat_indices):
        # Find which voice has this pattern
        for v in range(3):
            if pat_idx in score['voices'][v]['patterns']:
                notes = score['voices'][v]['patterns'][pat_idx]
                break
        a(f'pat{pat_idx}')
        for note in notes:
            a(f'        .byte ${note["pitch"] & 0xFF:02X},'
              f'${note["duration"] & 0xFF:02X},'
              f'${note["instrument"] & 0xFF:02X}')
        a(f'        .byte $FE')  # end of pattern marker
    a('')

    # --- DATA: Orderlists (sequence of pattern addresses per voice) ---
    for v in range(3):
        a(f'v{v}ol')
        voice = score['voices'][v]
        for pat_idx in voice['orderlist']:
            a(f'        .byte <pat{pat_idx},>pat{pat_idx}')
        # TODO: loop support
    a('')

    return '\n'.join(L)


# ===================================================================
# BUILD + VERIFY (same as before)
# ===================================================================

def build_sid(asm_text, output_path):
    asm_path = output_path.replace('.sid', '.s')
    bin_path = output_path.replace('.sid', '.bin')
    with open(asm_path, 'w') as f:
        f.write(asm_text)
    result = subprocess.run([XA, '-o', bin_path, asm_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Assembly FAILED:\n{result.stderr}")
        return False
    with open(bin_path, 'rb') as f:
        binary = f.read()

    with open(SID_PATH, 'rb') as f:
        orig = f.read()
    header_len = struct.unpack('>H', orig[6:8])[0]
    header = bytearray(orig[:header_len])
    struct.pack_into('>H', header, 8, 0)
    struct.pack_into('>H', header, 10, 0x1000)
    struct.pack_into('>H', header, 12, 0x1003)
    struct.pack_into('>H', header, 14, 1)
    struct.pack_into('>H', header, 16, 1)

    sid_data = bytes(header) + struct.pack('<H', 0x1000) + binary
    with open(output_path, 'wb') as f:
        f.write(sid_data)

    end_addr = 0x1000 + len(binary)
    print(f"SID: {len(sid_data)} bytes ({len(sid_data)/1024:.1f} KB), end ${end_addr:04X}")
    return True


def verify(output_path, max_frames=500):
    from ground_truth import capture_sid as gt_capture
    from collections import Counter
    from py65.devices.mpu6502 import MPU

    gt_result = gt_capture(SID_PATH, subtunes=[1], max_frames=max_frames,
                           detect_loop=False)
    gt = gt_result.subtunes[0].frames
    N = len(gt)

    with open(output_path, 'rb') as f:
        sid = f.read()
    hl = struct.unpack('>H', sid[6:8])[0]
    la = struct.unpack('>H', sid[8:10])[0]
    code = sid[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]; code = code[2:]
    mem = bytearray(65536); mem[la:la+len(code)] = code
    m = MPU(); m.memory = bytearray(mem); m.memory[0xFFF0] = 0x00
    m.stPush(0xFF); m.stPush(0xEF); m.pc = la; m.a = 0
    for _ in range(50000):
        if m.memory[m.pc] == 0x00: break
        m.step()

    rn = ['flo', 'fhi', 'plo', 'phi', 'ctl', 'ad', 'sr']
    errors = Counter()
    perfect = 0
    for fr in range(N):
        m.stPush(0xFF); m.stPush(0xEF); m.pc = la + 3
        for _ in range(50000):
            if m.memory[m.pc] == 0x00: break
            m.step()
        ok = True
        for v, vo in enumerate([0, 7, 14]):
            for r in range(7):
                if m.memory[0xD400+vo+r] != gt[fr][vo+r]:
                    errors[(f'V{v+1}', rn[r])] += 1
                    ok = False
        if ok:
            perfect += 1

    print(f"\npy65 verification: {N} frames")
    print(f"Perfect: {perfect}/{N} ({100*perfect/N:.1f}%)")
    for (v, r), cnt in errors.most_common():
        print(f"  {cnt:4d}/{N} ({100*cnt/N:5.1f}%) {v} {r}")
    return perfect, N


if __name__ == '__main__':
    print("Das Model Gen — clean from spec")
    print("=" * 50)

    print("\n[1] Extracting (T, I, S)...")
    T, instruments, score = extract()
    print(f"    T: {len(T)} entries")
    print(f"    I: {len(instruments)} instruments")
    for i in instruments:
        w = i['W']
        print(f"      [{i['id']:2d}] W={len(w['steps'])} steps "
              f"arp={i['arp_offset']} "
              f"P={i['P']['mode']} E=AD${i['E']['ad']:02X}")

    print(f"\n    S: tempo={score['tempo']} frames/tick")
    for v in range(3):
        print(f"    V{v+1}: {len(score['voices'][v]['orderlist'])} patterns")

    print("\n[2] Generating assembly...")
    asm = generate_asm(T, instruments, score)

    print("\n[3] Building PSID...")
    ok = build_sid(asm, OUT_PATH)
    if not ok:
        sys.exit(1)

    print("\n[4] Verifying...")
    verify(OUT_PATH, max_frames=200)
