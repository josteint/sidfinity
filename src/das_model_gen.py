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
        # Vibrato runs for ALL instruments (even arp) — intermediate write affects SID
        has_bit0 = bool(flags & 1)
        instruments.append({
            'id': rh.index,
            'W': {'steps': w_steps, 'loop': w_loop},
            'arp_offset': arp_offset,
            'vibrato_scale': vibrato_scale,
            'has_bit0': has_bit0,
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
                        is_tie = note.tie
                        if note.pitch is None or is_tie:
                            # TIE: use previous note's pitch; no freq write, no gate
                            pitch = notes[-1]['pitch'] if notes else 0
                        else:
                            pitch = note.pitch
                        # has_inst_byte: whether the original Hubbard note had an instrument byte
                        # This determines hub_off advance (3 bytes if yes, 2 if no)
                        # Encode: bit7 of stored inst = 0 means has_inst_byte, 1 means no_inst_byte
                        has_inst_byte = (note.instrument is not None)
                        # Bit7=1 → no inst byte (hub_off += 2)
                        # Bit6=1 → tie note (no freq write, ctrl without gate)
                        stored_inst = cur_inst | (0 if has_inst_byte else 0x80) | (0x40 if is_tie else 0)
                        notes.append({
                            'pitch': pitch,
                            'duration': dur + 1,  # Hubbard: counter loads D, decrements to -1
                            'instrument': stored_inst,
                            'tie': is_tie,
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

    # ZP layout per voice (17 bytes)
    # +0: tick_ctr      (frame countdown; 0 = load new note)
    # +1/+2: ol_ptr     (orderlist pointer lo/hi)
    # +3/+4: pat_ptr    (pattern pointer lo/hi)
    # +5: pw_period     (bidirectional PW sub-counter, signed; DEC each frame)
    # +6: dur_thresh    (dur_field * tempo; note-start when tick_ctr > dur_thresh)
    # +7: pw_lo         (current PW lo byte)
    # +8: base_note     (current pitch index)
    # +9: note_len      (tick_ctr value at note-load = (dur_field+1)*tempo)
    # +10: pw_speed     (PW add/step amount per tick)
    # +11: pw_hi        (current PW hi byte)
    # +12: pw_max       ($00=no mod, $FF=uni/linear, else=bidir max boundary)
    # +13: pw_dir       (0=rising, nonzero=falling)
    # +14: prev_inst    (current instrument ID)
    # +15: hub_off      (note_idx — tracks T[100] extended table lookup)
    # +16: fhi_state    (freq_hi state for bit0 skydive — written then DEC'd)
    ZP = [0x80, 0x91, 0xA2]
    SOFF = [0, 7, 14]
    FRAME_CTR = 0xB3  # global frame counter
    CTRL_V1   = 0xB4  # V1 ctrl byte (for T[104].lo update)
    CTRL_V2   = 0xB5  # V2 ctrl byte (for T[104].hi update)
    VIB_TMP   = 0xB6  # vibrato: delta accumulator

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
    a(f'        lda #0')
    a(f'        sta ${CTRL_V1:02X}')    # T[104].lo = V1 ctrl = 0 initially
    a(f'        sta ${CTRL_V2:02X}')    # T[104].hi = V2 ctrl = 0 initially
    for v in range(3):
        z = ZP[v]
        a(f'        lda v{v}ol')
        a(f'        sta ${z+3:02X}')        # pat_ptr lo
        a(f'        lda v{v}ol+1')
        a(f'        sta ${z+4:02X}')        # pat_ptr hi
        a(f'        lda #<(v{v}ol+2)')
        a(f'        sta ${z+1:02X}')        # ol_ptr lo
        a(f'        lda #>(v{v}ol+2)')
        a(f'        sta ${z+2:02X}')        # ol_ptr hi
        a(f'        lda #0')
        a(f'        sta ${z+5:02X}')        # pw_period=0
        a(f'        sta ${z+6:02X}')        # dur_thresh=0
        a(f'        sta ${z+7:02X}')        # pw_lo=0
        a(f'        sta ${z+9:02X}')        # note_len=0
        a(f'        sta ${z+10:02X}')       # pw_speed=0
        a(f'        sta ${z+11:02X}')       # pw_hi=0
        a(f'        sta ${z+12:02X}')       # pw_max=0
        a(f'        sta ${z+13:02X}')       # pw_dir=0 (up)
        a(f'        sta ${z+15:02X}')       # hub_off=0
        a(f'        sta ${z+16:02X}')       # fhi_state=0
        a(f'        lda #$FF')
        a(f'        sta ${z+14:02X}')       # prev_inst=$FF
        a(f'        lda #1')
        a(f'        sta ${z:02X}')          # tick_ctr=1 → triggers first note
    a('        rts')
    a('')

    # --- PLAY ---
    a('play')
    a(f'        inc ${FRAME_CTR:02X}')   # global frame counter
    # T[104]: lo=V1 ctrl_byte, hi=V2 ctrl_byte (Hubbard's contiguous memory layout).
    # These are ctrl values from the PREVIOUS frame's note-loads.
    a(f'        lda ${CTRL_V1:02X}')
    a(f'        sta ftlo+104')
    a(f'        lda ${CTRL_V2:02X}')
    a(f'        sta fthi+104')
    # T[100]: lo=V2 note_idx (hub_off), hi=V3 note_idx.
    # Updated at start of frame from previous frame's hub_off values.
    # V3 and V2 are processed before V1, so when V1 reads T[100], we need
    # the CURRENT frame's hub_off. We re-update T[100] between V2 and V1.
    a(f'        lda ${ZP[1]+15:02X}')   # V2 hub_off (from last frame)
    a(f'        sta ftlo+100')
    a(f'        lda ${ZP[2]+15:02X}')   # V3 hub_off
    a(f'        sta fthi+100')

    for v in [2, 1, 0]:
        z = ZP[v]
        so = SOFF[v]

        # After V2 processes (and before V1), update T[100] and T[104].
        # T[100]: V2/V3 hub_off (note_idx) — needed for V1 arpeggio freq lookup
        # T[104]: CTRL_V1/CTRL_V2 — updated after V2 note-load (ctrl_byte changes)
        # This ensures V1's arpeggio sees V2's CURRENT ctrl and note_idx values.
        if v == 0:
            a(f'; --- Update T[100] and T[104] before V1 ---')
            a(f'        lda ${ZP[1]+15:02X}')   # V2 hub_off (may have been updated this frame)
            a(f'        sta ftlo+100')
            a(f'        lda ${ZP[2]+15:02X}')   # V3 hub_off
            a(f'        sta fthi+100')
            a(f'        lda ${CTRL_V1:02X}')    # V1 ctrl (from V1's previous note-load)
            a(f'        sta ftlo+104')
            a(f'        lda ${CTRL_V2:02X}')    # V2 ctrl (from V2's note-load this frame)
            a(f'        sta fthi+104')

        a(f'; --- Voice {v+1} ---')

        # Tick counter decrement
        a(f'        dec ${z:02X}')
        a(f'        beq v{v}rd')
        a(f'        jmp v{v}eval')

        # ---- NOTE LOAD PATH ----
        a(f'v{v}rd')
        a(f'        ldy #0')
        a(f'        lda (${z+3:02X}),y')       # read pitch from pat_ptr
        a(f'        cmp #$FE')                  # end of pattern marker?
        a(f'        bne v{v}nt')
        # End of pattern: load next pattern from orderlist
        a(f'        lda #0')
        a(f'        sta ${z+15:02X}')            # reset hub_off at pattern boundary
        a(f'        lda #$FF')
        a(f'        sta ${z+14:02X}')            # force inst reload
        a(f'        ldy #0')
        a(f'        lda (${z+1:02X}),y')
        a(f'        sta ${z+3:02X}')
        a(f'        iny')
        a(f'        lda (${z+1:02X}),y')
        a(f'        sta ${z+4:02X}')
        a(f'        clc')
        a(f'        lda ${z+1:02X}')
        a(f'        adc #2')
        a(f'        sta ${z+1:02X}')
        a(f'        bcc v{v}rd')
        a(f'        inc ${z+2:02X}')
        a(f'        jmp v{v}rd')
        a(f'v{v}nt')
        # Got a note: pitch in A
        a(f'        sta ${z+8:02X}')            # base_note = pitch
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # duration field (= dur_field+1)
        # Convert to frames: tick_ctr = duration * tempo
        if tempo == 1:
            pass
        else:
            a(f'        tax')
            a(f'        lda #0')
            a(f'v{v}mul  clc')
            a(f'        adc #{tempo}')
            a(f'        dex')
            a(f'        bne v{v}mul')
        a(f'        sta ${z:02X}')              # tick_ctr = dur * tempo
        a(f'        sta ${z+9:02X}')            # note_len = same
        # dur_thresh = tick_ctr - tempo = dur_field * tempo (threshold for note-start check)
        a(f'        sec')
        a(f'        sbc #{tempo}')
        a(f'        sta ${z+6:02X}')            # dur_thresh
        # Read instrument byte
        # Bit7 = no_inst_byte flag (hub_off += 2 if set, else 3)
        # Bit6 = tie flag (hub_off += 1, no freq write, ctrl without gate)
        # Bits 0-5 = instrument ID (0-12)
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # instrument byte (may have bit7/bit6 flags)
        a(f'        sta ${VIB_TMP:02X}')        # save raw inst byte
        a(f'        and #$3F')                  # mask to 6 bits (clear bit7+bit6)
        a(f'        tax')                        # X = clean instrument ID (0-12)
        a(f'        stx ${z+14:02X}')           # save clean inst ID
        # Check bit6 (tie flag) first: tie → hub_off += 1 only
        a(f'        lda ${VIB_TMP:02X}')
        a(f'        and #$40')
        a(f'        bne v{v}hubt')              # tie → add 1
        # Not tie: check bit7 (no_inst_byte flag)
        a(f'        lda ${VIB_TMP:02X}')
        a(f'        bmi v{v}hub2')              # bit7 set → no inst byte → add 2
        # has inst byte: hub_off += 3
        a(f'        lda ${z+15:02X}')
        a(f'        clc')
        a(f'        adc #3')
        a(f'        sta ${z+15:02X}')
        a(f'        jmp v{v}hubx')
        a(f'v{v}hub2')
        # no inst byte: hub_off += 2
        a(f'        lda ${z+15:02X}')
        a(f'        clc')
        a(f'        adc #2')
        a(f'        sta ${z+15:02X}')
        a(f'        jmp v{v}hubx')
        a(f'v{v}hubt')
        # tie note: hub_off += 1
        a(f'        lda ${z+15:02X}')
        a(f'        clc')
        a(f'        adc #1')
        a(f'        sta ${z+15:02X}')
        a(f'v{v}hubx')
        # Check bit6 (tie flag) — tie: skip freq write, ctrl without gate
        a(f'        lda ${VIB_TMP:02X}')
        a(f'        and #$40')
        a(f'        bne v{v}tie')               # tie → jump to tie path
        # NORMAL NOTE: write freq_hi then freq_lo (Hubbard order)
        a(f'        lda ${z+8:02X}')            # base_note
        a(f'        tay')
        a(f'        lda fthi,y')
        a(f'        sta $D4{so+1:02X}')          # write freq_hi
        a(f'        sta ${z+16:02X}')            # fhi_state = fthi[base_note]
        a(f'        lda ftlo,y')
        a(f'        sta $D4{so:02X}')            # write freq_lo
        # CTRL: write instrument ctrl with gate on (normal path)
        a(f'        lda i_ctrl,x')              # instrument ctrl (gate already set)
        # Save UNGATED ctrl for T[104] tracking (Hubbard saves ctrl_byte BEFORE gate masking)
        if v == 0:   # V1 ctrl → CTRL_V1
            a(f'        sta ${CTRL_V1:02X}')
        elif v == 1: # V2 ctrl → CTRL_V2
            a(f'        sta ${CTRL_V2:02X}')
        a(f'        sta $D4{so+4:02X}')          # write ctrl to SID (gate on for normal)
        a(f'        jmp v{v}pw0')               # skip to PW (past tie path)
        a(f'v{v}tie')
        # TIE NOTE: no freq write; write ctrl WITHOUT gate
        a(f'        lda i_ctrl,x')
        # Save UNGATED ctrl for T[104] tracking (same: save before masking)
        if v == 0:
            a(f'        sta ${CTRL_V1:02X}')
        elif v == 1:
            a(f'        sta ${CTRL_V2:02X}')
        a(f'        and #$FE')                  # clear gate bit
        a(f'        sta $D4{so+4:02X}')          # write ctrl to SID (gate off for tie)
        a(f'v{v}pw0')
        # PW: always write pw_lo, pw_hi at note-load (Hubbard always writes PW)
        # pw_lo: read from pw_live[inst] — per-instrument mutable accumulator
        #         (Hubbard stores pw accumulator in-place in instrument table)
        a(f'        lda pw_live,x')
        a(f'        sta $D4{so+2:02X}')          # write pw_lo
        a(f'        sta ${z+7:02X}')             # sync ZP+7 with instrument's live pw_lo
        # Write pw_hi from i_pwhi[inst]
        a(f'        lda i_pwhi,x')
        a(f'        sta $D4{so+3:02X}')          # write pw_hi
        a(f'        sta ${z+11:02X}')
        # ADSR: write ad then sr (Hubbard order: ctrl→pw→adsr)
        a(f'        lda i_ad,x')
        a(f'        sta $D4{so+5:02X}')
        a(f'        lda i_sr,x')
        a(f'        sta $D4{so+6:02X}')
        # Load PW params for eval path
        a(f'        lda i_pws,x')
        a(f'        sta ${z+10:02X}')
        a(f'        lda i_pwmax,x')
        a(f'        sta ${z+12:02X}')
        # Advance pat_ptr by 3 (pitch+dur+inst)
        a(f'        clc')
        a(f'        lda ${z+3:02X}')
        a(f'        adc #3')
        a(f'        sta ${z+3:02X}')
        a(f'        bcc v{v}nd1')
        a(f'        inc ${z+4:02X}')
        a(f'v{v}nd1')
        a(f'        jmp v{v}done')              # skip eval entirely after note-load
        a('')

        # ---- EVAL PATH: effects only (vibrato, PW, skydive, arpeggio) ----
        a(f'v{v}eval')

        # GATE-OFF: fires exactly once per note, when tick_ctr == tempo
        # Corresponds to Hubbard's sustain_voice duration==0 path.
        a(f'        lda ${z:02X}')              # tick_ctr
        a(f'        cmp #{tempo}')             # == tempo? (gate-off tick)
        a(f'        bne v{v}efx')              # not gate-off frame
        # Gate-off: write ctrl&$FE, AD=0, SR=0
        a(f'        ldy ${z+14:02X}')          # current instrument
        a(f'        lda i_ctrl,y')
        a(f'        and #$FE')
        a(f'        sta $D4{so+4:02X}')         # ctrl with gate cleared
        a(f'        lda #0')
        a(f'        sta $D4{so+5:02X}')         # AD = 0
        a(f'        sta $D4{so+6:02X}')         # SR = 0
        a(f'v{v}efx')

        # VIBRATO: writes freq_lo and freq_hi if instrument has vibrato
        a(f'        ldy ${z+14:02X}')           # instrument ID
        a(f'        lda i_vib,y')              # vibrato scale (0=none)
        a(f'        beq v{v}bit0')             # no vibrato → skip to skydive
        # Check: note_len >= 6 ticks (6*tempo frames)
        # If short note: still write base freq (Hubbard always writes freq when vib active)
        a(f'        lda ${z+9:02X}')           # note_len
        a(f'        cmp #{6 * tempo}')
        a(f'        bcs v{v}vlong')            # long note → compute modulated vibrato
        # Short note: write SWAPPED freq bytes (Hubbard vibrato quirk)
        # Hubbard vibrato reads lo_cur = _rb($5429+y) = fthi[note] → D400
        #                and hi_cur = _rb($5428+y) = ftlo[note] → D401
        a(f'        ldx ${z+8:02X}')
        a(f'        lda fthi,x')
        a(f'        sta $D4{so:02X}')          # fthi → D400 (freq_lo reg) — SWAPPED!
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so+1:02X}')        # ftlo → D401 (freq_hi reg) — SWAPPED!
        a(f'        jmp v{v}bit0')
        a(f'v{v}vlong')
        # Compute LFO step: (frame_ctr & 7) → triangle 0,1,2,3,3,2,1,0
        a(f'        lda ${FRAME_CTR:02X}')
        a(f'        and #$07')
        a(f'        cmp #4')
        a(f'        bcc v{v}vdok')
        a(f'        eor #$07')                 # mirror: 4→3, 5→2, 6→1, 7→0
        a(f'v{v}vdok')
        a(f'        pha')                      # save depth (vib_step)
        # Compute semitone delta: fthi[pitch+1] - fthi[pitch]
        a(f'        ldx ${z+8:02X}')
        a(f'        lda fthi+1,x')
        a(f'        sec')
        a(f'        sbc fthi,x')
        a(f'        sta ${VIB_TMP:02X}')
        # Right-shift delta by (vib_scale+1)
        a(f'        ldy ${z+14:02X}')
        a(f'        ldx i_vib,y')
        a(f'        inx')
        a(f'v{v}vsr')
        a(f'        lsr ${VIB_TMP:02X}')
        a(f'        dex')
        a(f'        bne v{v}vsr')
        # Multiply delta * depth (vib_step times)
        a(f'        pla')                      # pop depth (vib_step)
        a(f'        beq v{v}vwr')             # vib_step=0 → write plain base freq
        a(f'        tax')
        a(f'        lda #0')
        a(f'v{v}vmul')
        a(f'        clc')
        a(f'        adc ${VIB_TMP:02X}')
        a(f'        dex')
        a(f'        bne v{v}vmul')
        # Add to base freq_hi — write flo first, fhi second (matches Hubbard vibrato order)
        a(f'        ldx ${z+8:02X}')
        a(f'        clc')
        a(f'        adc fthi,x')
        a(f'        sta ${VIB_TMP:02X}')       # stash modulated freq_hi
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')          # write base freq_lo first
        a(f'        lda ${VIB_TMP:02X}')
        a(f'        sta $D4{so+1:02X}')        # then write modulated freq_hi
        a(f'        jmp v{v}bit0')
        a(f'v{v}vwr')
        # vib_step=0: write plain base freq (flo first, fhi second)
        a(f'        ldx ${z+8:02X}')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')          # write freq_lo first
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')        # then freq_hi
        # fall through to bit0

        # BIT0 SKYDIVE: decrement freq_hi each sustain frame, write to SID
        # Note-start path (first tick period): write old fhi, write $80 to ctrl
        # NOT-start path (subsequent ticks): write old fhi, DEC, write ctrl&$FE or new fhi+$80
        a(f'v{v}bit0')
        a(f'        ldy ${z+14:02X}')
        a(f'        lda i_bit0,y')
        a(f'        beq v{v}arpc')             # no bit0 → skip to arp
        # Skip skydive when in last tick period (Hubbard: duration==0 → return)
        # This covers gate-off frame (tick_ctr==tempo) and frames after (tick_ctr<tempo)
        a(f'        lda ${z:02X}')             # tick_ctr
        a(f'        cmp #{tempo+1}')           # tick_ctr <= tempo?
        a(f'        bcc v{v}arpc')             # yes (tick_ctr < tempo+1) → skip skydive
        a(f'        lda ${z+16:02X}')          # fhi_state
        a(f'        beq v{v}arpc')             # fhi_state==0 → skip
        # Note-start vs NOT-start:
        # note-start: tick_ctr > dur_thresh (still in first tick period)
        a(f'        lda ${z+6:02X}')           # dur_thresh
        a(f'        cmp ${z:02X}')             # compare dur_thresh with tick_ctr
        a(f'        bcs v{v}bns')              # dur_thresh >= tick_ctr → NOT-start
        # NOTE-START PATH: write old fhi + $80 to ctrl
        a(f'        lda ${z+16:02X}')          # old freq_hi (unchanged)
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda #$80')
        a(f'        sta $D4{so+4:02X}')
        a(f'        jmp v{v}arpc')
        # NOT-START PATH: write old fhi, DEC, check ctrl
        a(f'v{v}bns')
        a(f'        lda ${z+16:02X}')          # old fhi
        a(f'        sta $D4{so+1:02X}')         # write old freq_hi
        a(f'        dec ${z+16:02X}')           # DEC fhi_state
        a(f'        lda i_ctrl,y')             # instrument ctrl
        a(f'        and #$FE')                 # clear gate
        a(f'        bne v{v}bcm')             # ctrl&$FE != 0 → write ctrl_masked
        # ctrl&$FE == 0: write new freq_hi + $80
        a(f'        lda ${z+16:02X}')          # new (decremented) fhi
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda #$80')
        a(f'v{v}bcm')
        a(f'        sta $D4{so+4:02X}')

        # FREQ TABLE ARPEGGIO (bit2): alternate base pitch and base+12 each frame
        a(f'v{v}arpc')
        a(f'        ldy ${z+14:02X}')
        a(f'        lda i_arp,y')              # arp_offset (0 or 12)
        a(f'        beq v{v}pw')               # no arp → skip to PW
        a(f'        ldx ${z+8:02X}')           # base_note
        a(f'        lda ${FRAME_CTR:02X}')
        a(f'        and #$01')
        a(f'        beq v{v}frok')             # even frame → base_note
        a(f'        txa')
        a(f'        clc')
        a(f'        adc i_arp,y')              # base_note + arp_offset
        a(f'        tax')
        a(f'v{v}frok')
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')

        # PW MODULATION: only write when modulation fires
        # PW_UNI (bit3 of fx → pw_max==$FF): add pw_speed to pw_lo each frame
        # BIDIR (pw_max != $00 and != $FF): fire when pw_period sub-counter expires
        # None (pw_max==$00): no write
        a(f'v{v}pw')
        a(f'        lda ${z+12:02X}')          # pw_max
        a(f'        beq v{v}done')             # $00 = no modulation
        a(f'        cmp #$FF')
        a(f'        beq v{v}lin')              # $FF = linear/uni
        # --- BIDIR: fire when pw_period expires ---
        a(f'        dec ${z+5:02X}')           # DEC pw_period
        a(f'        bpl v{v}done')             # still positive → no fire
        # Reload pw_period from pw_speed low 5 bits (= pwm & $1F)
        a(f'        lda ${z+10:02X}')          # pw_speed (= pwm byte)
        a(f'        and #$1F')
        a(f'        sta ${z+5:02X}')           # reload pw_period
        # Step size = pw_speed high 3 bits (= pwm & $E0)
        a(f'        lda ${z+10:02X}')
        a(f'        and #$E0')
        a(f'        sta ${VIB_TMP:02X}')       # step
        a(f'        lda ${z+13:02X}')          # pw_dir (0=up, nonzero=down)
        a(f'        bne v{v}dn')
        # RISING: pw += step
        a(f'        clc')
        a(f'        lda ${z+7:02X}')
        a(f'        adc ${VIB_TMP:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        bcc v{v}ncu')
        a(f'        inc ${z+11:02X}')
        a(f'        lda ${z+11:02X}')
        a(f'        and #$0F')                 # 12-bit PW
        a(f'        sta ${z+11:02X}')
        a(f'v{v}ncu')
        a(f'        lda ${z+11:02X}')
        a(f'        cmp ${z+12:02X}')          # == pw_max?
        a(f'        bne v{v}pwwr')
        a(f'        inc ${z+13:02X}')          # flip to falling
        a(f'        jmp v{v}pwwr')
        # FALLING: pw -= step
        a(f'v{v}dn')
        a(f'        sec')
        a(f'        lda ${z+7:02X}')
        a(f'        sbc ${VIB_TMP:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        bcs v{v}ncd')
        a(f'        dec ${z+11:02X}')
        a(f'v{v}ncd')
        a(f'        lda ${z+11:02X}')
        a(f'        cmp #$08')
        a(f'        bne v{v}pwwr')
        a(f'        dec ${z+13:02X}')          # flip to rising (any nonzero→one less)
        a(f'        jmp v{v}pwwr')
        # --- LINEAR/UNI: add pw_speed to pw_lo each frame ---
        a(f'v{v}lin')
        a(f'        clc')
        a(f'        lda ${z+7:02X}')
        a(f'        adc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')
        # Write pw_lo to SID (note: uni only writes pw_lo, not pw_hi)
        a(f'        sta $D4{so+2:02X}')
        # Also update pw_live[inst] so per-instrument accumulator is maintained
        a(f'        ldy ${z+14:02X}')         # inst ID
        a(f'        sta pw_live,y')
        a(f'        jmp v{v}done')
        # BIDIR: write both pw_lo and pw_hi to SID
        a(f'v{v}pwwr')
        a(f'        lda ${z+7:02X}')
        a(f'        sta $D4{so+2:02X}')
        a(f'        lda ${z+11:02X}')
        a(f'        sta $D4{so+3:02X}')
        # Write accumulated PW back to instrument table (shared mutable state)
        # (Hubbard's self-modifying code stores pw in instrument table)
        a(f'        ldy ${z+14:02X}')
        a(f'        lda ${z+7:02X}')
        a(f'        sta i_pwlo,y')
        a(f'        lda ${z+11:02X}')
        a(f'        sta i_pwhi,y')

        a(f'v{v}done')
        a('')

    a('        rts')
    a('')

    # --- DATA: Frequency Table ---
    # Override T[104] to start at 0 (dynamic, updated by CTRL_V1/V2)
    T_out = list(T)
    T_out[104] = 0   # will be updated at runtime from CTRL_V1/CTRL_V2
    a('ftlo')
    for i in range(0, len(T_out), 16):
        a('        .byte ' + ','.join(f'${f & 0xFF:02X}' for f in T_out[i:i+16]))
    a('fthi')
    for i in range(0, len(T_out), 16):
        a('        .byte ' + ','.join(f'${(f >> 8) & 0xFF:02X}' for f in T_out[i:i+16]))
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
    # pw_speed = raw pwm byte (contains both period and step)
    a('        .byte ' + ','.join(f'${i["P"]["speed"]:02X}' for i in instruments))
    a('i_pwmax')
    # $00=no modulation, $FF=linear/uni, else=bidir max (pw_hi boundary)
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
    a('i_bit0')
    a('        .byte ' + ','.join(f'${1 if i["has_bit0"] else 0:02X}' for i in instruments))
    a('i_ctrl')  # instrument ctrl WITH gate (written at note-load and gate-off)
    a('        .byte ' + ','.join(f'${i["W"]["steps"][0]:02X}' for i in instruments))
    # pw_live: mutable per-instrument pw_lo accumulator (starts as copy of i_pwlo)
    # Updated by linear PW eval path; read at note-load for same-instrument case
    a('pw_live')
    a('        .byte ' + ','.join(f'${i["P"]["init_pw"] & 0xFF:02X}' for i in instruments))
    a('')

    # --- DATA: Patterns (pitch, duration, instrument — 3 bytes each) ---
    all_pat_indices = set()
    for v in range(3):
        all_pat_indices.update(score['voices'][v]['orderlist'])

    for pat_idx in sorted(all_pat_indices):
        for v in range(3):
            if pat_idx in score['voices'][v]['patterns']:
                notes = score['voices'][v]['patterns'][pat_idx]
                break
        a(f'pat{pat_idx}')
        for note in notes:
            a(f'        .byte ${note["pitch"] & 0xFF:02X},'
              f'${note["duration"] & 0xFF:02X},'
              f'${note["instrument"] & 0xFF:02X}')
        a(f'        .byte $FE')
    a('')

    # --- DATA: Orderlists ---
    for v in range(3):
        a(f'v{v}ol')
        voice = score['voices'][v]
        for pat_idx in voice['orderlist']:
            a(f'        .byte <pat{pat_idx},>pat{pat_idx}')
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
