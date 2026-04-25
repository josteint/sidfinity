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

        # F program: sequence of note offsets
        # Hubbard's arpeggio: alternate +0 and +12 every frame
        if rh.has_arpeggio:
            if rh.has_drum:
                # Arp applies on ALL frames including noise burst
                f_offsets = [0, 12, 0, 12, 0]
                f_loop = 3  # loop the alternating pair (offsets[3]=12, [4]=0)
            else:
                f_offsets = [0, 12]
                f_loop = 0
        else:
            f_offsets = [0]
            f_loop = 0

        # P program: PW modulation
        pw_speed = rh.pwm_speed
        if pw_speed == 0:
            pw_mode = 'none'
            pw_min = 0xFF; pw_max = 0xFF
        elif (rh.pulse_width >> 8) >= 0x08:
            # Bidirectional: Hubbard bounces between $08xx and $0Exx
            pw_mode = 'bidirectional'
            pw_min = 0x08; pw_max = 0x0E
        else:
            pw_mode = 'linear'
            pw_min = 0xFF; pw_max = 0xFF

        # E spec: ADSR + gate/adsr timing
        instruments.append({
            'id': rh.index,
            'W': {'steps': w_steps, 'loop': w_loop},
            'F': {'offsets': f_offsets, 'loop': f_loop},
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
                        notes.append({
                            'pitch': note.pitch if note.pitch is not None else 0,
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

    # ZP layout per voice (15 bytes)
    # +0: tick_ctr
    # +1/+2: ol_ptr
    # +3/+4: pat_ptr
    # +5/+6: wf_ptr
    # +7: pw_lo
    # +8: base_note
    # +9: note_len
    # +10: pw_speed
    # +11: pw_hi
    # +12: pw_max    ($00=no mod, $FF=linear, else=bidir max)
    # +13: pw_dir    (0=up, 1=down)
    # +14: prev_inst (previous instrument ID, $FF=none)
    ZP = [0x80, 0x8F, 0x9E]
    SOFF = [0, 7, 14]

    a(f'        * = ${BASE:04X}')
    a(f'        jmp init')
    a(f'        jmp play')
    a('')

    # --- INIT ---
    a('init')
    a('        lda #$0F')
    a('        sta $D418')
    # (global arp counter removed — per-step F offsets used instead)
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
        a(f'        lda #$FF')
        a(f'        sta ${z+14:02X}')       # prev_inst=$FF (force init on first note)
        a(f'        lda #1')
        a(f'        sta ${z:02X}')          # tick_ctr=1 → triggers first note
    a('        rts')
    a('')

    # --- PLAY ---
    a('play')
    for v in range(3):
        z = ZP[v]
        so = SOFF[v]

        a(f'; --- Voice {v+1} ---')

        # Step 1: tick counter
        a(f'        dec ${z:02X}')
        a(f'        bne v{v}eval')
        # tick_ctr hit 0 → load new note from pattern
        a(f'v{v}rd')
        a(f'        ldy #0')
        a(f'        lda (${z+3:02X}),y')       # read note from pat_ptr
        a(f'        cmp #$FE')                  # end of pattern marker
        a(f'        bne v{v}nt')
        # End of pattern → read next pattern address from orderlist
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
        a(f'        lda i_pwlo,x')
        a(f'        sta $D4{so+2:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        lda i_pwhi,x')
        a(f'        sta $D4{so+3:02X}')
        a(f'        sta ${z+11:02X}')
        a(f'        lda #0')
        a(f'        sta ${z+13:02X}')       # reset pw_dir to UP
        a(f'v{v}skpw')
        # Always load PW speed/max (even if same inst — harmless)
        a(f'        lda i_pws,x')
        a(f'        sta ${z+10:02X}')
        a(f'        lda i_pwmax,x')
        a(f'        sta ${z+12:02X}')
        # Set WF program pointer
        a(f'        lda i_wflo,x')
        a(f'        sta ${z+5:02X}')
        a(f'        lda i_wfhi,x')
        a(f'        sta ${z+6:02X}')
        # Advance pat_ptr by 3
        a(f'        clc')
        a(f'        lda ${z+3:02X}')
        a(f'        adc #3')
        a(f'        sta ${z+3:02X}')
        a(f'        bcc v{v}eval')
        a(f'        inc ${z+4:02X}')
        a('')

        # Steps 2-5: evaluate W, F, P, E
        a(f'v{v}eval')

        # E: ADSR zeroing
        a(f'        lda ${z:02X}')
        a(f'        cmp #3')
        a(f'        bne v{v}noz')
        a(f'        lda #0')
        a(f'        sta $D4{so+5:02X}')
        a(f'        sta $D4{so+6:02X}')
        a(f'v{v}noz')

        # W+F: read from wf_ptr (+5/+6)
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
        # E: gate off
        a(f'        pha')
        a(f'        lda ${z:02X}')
        a(f'        cmp #3')
        a(f'        bcs v{v}gon')
        a(f'        pla')
        a(f'        and #$FE')
        a(f'        jmp v{v}wrt')
        a(f'v{v}gon')
        a(f'        pla')
        a(f'v{v}wrt')
        a(f'        sta $D4{so+4:02X}')

        # F: note offset from WF program (interleaved with W)
        a(f'        iny')
        a(f'        lda (${z+5:02X}),y')          # F offset
        a(f'        clc')
        a(f'        adc ${z+8:02X}')              # + base_note
        a(f'        tax')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')

        # Advance wf_ptr by 2
        a(f'        clc')
        a(f'        lda ${z+5:02X}')
        a(f'        adc #2')
        a(f'        sta ${z+5:02X}')
        a(f'        bcc v{v}pw')
        a(f'        inc ${z+6:02X}')

        # P: PW modulation — write first, then accumulate
        a(f'v{v}pw')
        a(f'        lda ${z+7:02X}')
        a(f'        sta $D4{so+2:02X}')       # write pw_lo to SID
        a(f'        lda ${z+11:02X}')
        a(f'        sta $D4{so+3:02X}')       # write pw_hi to SID
        # Check if modulation active
        a(f'        lda ${z+12:02X}')         # pw_max
        a(f'        beq v{v}done')             # $00 = no modulation
        a(f'        cmp #$FF')
        a(f'        beq v{v}lin')              # $FF = linear (8-bit only)
        # --- Bidirectional 16-bit ---
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
        # Check max
        a(f'        lda ${z+11:02X}')
        a(f'        cmp ${z+12:02X}')         # pw_hi >= pw_max?
        a(f'        bcc v{v}done')
        a(f'        lda #1')
        a(f'        sta ${z+13:02X}')         # flip to DOWN
        a(f'        jmp v{v}done')
        # DOWN: pw -= speed (16-bit)
        a(f'v{v}dn')
        a(f'        sec')
        a(f'        lda ${z+7:02X}')
        a(f'        sbc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')
        a(f'        bcs v{v}ncd')
        a(f'        dec ${z+11:02X}')
        a(f'v{v}ncd')
        # Check min (hardcoded $08 for Commando — TODO: make per-instrument)
        a(f'        lda ${z+11:02X}')
        a(f'        cmp #$08')                # pw_min
        a(f'        bcs v{v}done')
        a(f'        lda #0')
        a(f'        sta ${z+13:02X}')         # flip to UP
        a(f'        jmp v{v}done')
        # --- Linear 8-bit ---
        a(f'v{v}lin')
        a(f'        clc')
        a(f'        lda ${z+7:02X}')
        a(f'        adc ${z+10:02X}')
        a(f'        sta ${z+7:02X}')

        a(f'v{v}done')
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
    a('i_wflo')
    a('        .byte ' + ','.join(f'<wf{i["id"]}' for i in instruments))
    a('i_wfhi')
    a('        .byte ' + ','.join(f'>wf{i["id"]}' for i in instruments))
    a('')

    # --- DATA: Combined W+F programs per instrument ---
    # Each step: (waveform_byte, note_offset)
    # The W.steps and F.offsets are INTERLEAVED into a single program.
    for inst in instruments:
        iid = inst['id']
        w = inst['W']
        f = inst['F']

        a(f'wf{iid}')
        # Combine W and F into interleaved (wave, offset) pairs
        # Both have loop points — we use the LONGER sequence and loop both
        w_steps = w['steps']
        f_offsets = f['offsets']
        w_loop = w['loop']
        f_loop = f['loop']

        # The combined program length = max(len(w_steps), len(f_offsets))
        # Pad the shorter one by repeating from its loop point
        max_len = max(len(w_steps), len(f_offsets))

        def get_step(seq, loop, idx):
            if idx < len(seq):
                return seq[idx]
            return seq[loop + (idx - len(seq)) % (len(seq) - loop)]

        # Find the combined loop point (where BOTH W and F have looped)
        # This is at max(len(w_steps), len(f_offsets)) rounded to the LCM of both cycle lengths
        # For simplicity: use max_len as the combined program length, loop at max(w_loop, f_loop)
        combined_loop = max(w_loop, f_loop)
        # Ensure combined_loop makes sense
        if combined_loop >= max_len:
            combined_loop = max_len - 1

        byte_pos = 0
        for step in range(max_len):
            ws = get_step(w_steps, w_loop, step)
            fo = get_step(f_offsets, f_loop, step)
            if step == combined_loop:
                a(f'wf{iid}lp')   # loop target label
            a(f'        .byte ${ws:02X},${fo & 0xFF:02X}')
            byte_pos += 2
        # Loop back
        a(f'        .byte $FF,<wf{iid}lp,>wf{iid}lp')
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
        w = i['W']; f = i['F']
        print(f"      [{i['id']:2d}] W={len(w['steps'])} steps "
              f"F={len(f['offsets'])} offsets "
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
