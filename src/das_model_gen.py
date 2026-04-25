"""
das_model_gen.py — Clean Das Model codegen. No baggage.

Implements docs/das_model.md from scratch:
    SID = (T, I, S)
    I = { W(delta,L), F(delta), P(delta,state), E(delta,L) }

Reads instrument definitions from the binary via rh_decompile.
Generates 6502 assembly via xa65.
Verifies against ground truth frame by frame.

No dependency on simple_codegen, holy_scale, or any previous codegen.
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
OUT_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_holyscale.sid')


# ===================================================================
# Step 1: Extract (T, I, S) from binary
# ===================================================================

def extract():
    """Extract freq table T, instruments I, and score S from Commando."""
    from rh_decompile import decompile
    decomp = decompile(SID_PATH)

    # T: freq table (PAL + extended entries from py65)
    from effect_detect import FREQ_PAL
    T = list(FREQ_PAL)  # T[0..95]

    # Extend T with runtime values at indices 96+
    from py65.devices.mpu6502 import MPU
    with open(SID_PATH, 'rb') as f:
        d = f.read()
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    mem = bytearray(65536)
    mem[la:la + len(code)] = code
    m = MPU()
    m.memory = bytearray(mem)
    m.memory[0xFFF0] = 0x00
    # Run init
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[10:12])[0]
    m.a = 0
    for _ in range(100000):
        if m.memory[m.pc] == 0x00:
            break
        m.step()
    # Run one play call to populate runtime state
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[12:14])[0]
    for _ in range(50000):
        if m.memory[m.pc] == 0x00:
            break
        m.step()
    # Read extended entries
    ft_base = 0x5428  # Hubbard interleaved freq table address
    while len(T) < 120:
        i = len(T)
        addr = ft_base + i * 2
        T.append((m.memory[addr + 1] << 8) | m.memory[addr])

    # I: instruments
    instruments = []
    for inst in decomp.instruments:
        instruments.append({
            'id': inst.index,
            'ad': inst.ad,
            'sr': inst.sr,
            'ctrl': inst.ctrl,
            'pw': inst.pulse_width,
            'pw_speed': inst.pwm_speed,
            'has_drum': inst.has_drum,
            'has_arp': inst.has_arpeggio,
            'has_skydive': inst.has_skydive,
            'vibrato': getattr(inst, 'vibrato_depth', 0),
        })

    # S: score (patterns + orderlists for song 0)
    song = decomp.songs[0]
    speed = decomp.speed if decomp.speed is not None else 2
    tick_length = speed + 1  # frames per tick

    pat_dict = {p.index: p for p in decomp.patterns}

    score = {
        'tick_length': tick_length,
        'voices': [],
    }
    for v_track in song.tracks:
        voice = {'orderlist': [], 'patterns': {}}
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
                        notes.append({
                            'pitch': note.pitch if note.pitch is not None else 0,
                            'duration': note.duration if note.duration is not None else 0,
                            'instrument': cur_inst,
                        })
                    voice['patterns'][pat_idx] = notes
            elif entry[0] == 'loop':
                voice['loop_target'] = entry[1]
        score['voices'].append(voice)

    return T, instruments, score


# ===================================================================
# Step 2: Generate 6502 assembly from (T, I, S)
# ===================================================================

def generate_asm(T, instruments, score):
    """Generate xa65 assembly implementing Das Model.

    The player evaluates per frame, per voice:
        ctrl = W(delta, L)
        freq = T[base_note + F(delta)]
        pw   = P(delta, state)
        (ad, sr) = E(delta, L)
    """
    L = []  # assembly lines
    a = L.append

    BASE = 0x1000
    HR = 3  # hard restart frames before note end
    tick_length = score['tick_length']

    # ZP layout per voice (8 bytes each)
    # +0: tick_ctr (frames until next note)
    # +1: note_ptr_lo
    # +2: note_ptr_hi
    # +3: wave_ptr_lo
    # +4: wave_ptr_hi
    # +5: pw_lo (PW accumulator low byte)
    # +6: current_note (base freq table index)
    # +7: delta (frames since note-on, for wave table stepping)
    ZP = [0x80, 0x88, 0x90]
    SOFF = [0, 7, 14]  # SID register offsets per voice

    a(f'        * = ${BASE:04X}')
    a(f'        jmp init')
    a(f'        jmp play')
    a('')

    # --- INIT ---
    a('init')
    a('        lda #$0F')
    a('        sta $D418')  # volume
    for v in range(3):
        z = ZP[v]
        a(f'        lda #<v{v}notes')
        a(f'        sta ${z+1:02X}')
        a(f'        lda #>v{v}notes')
        a(f'        sta ${z+2:02X}')
        a(f'        lda #1')          # tick_ctr=1 triggers first note immediately
        a(f'        sta ${z:02X}')
        a(f'        lda #0')
        a(f'        sta ${z+5:02X}')  # pw_lo=0
        a(f'        sta ${z+7:02X}')  # delta=0
    a('        rts')
    a('')

    # --- PLAY ---
    a('play')
    for v in range(3):
        z = ZP[v]
        so = SOFF[v]

        a(f'; --- Voice {v+1} ---')

        # E(delta, L): hard restart check BEFORE decrementing tick_ctr
        # When tick_ctr == HR+1 (before dec), we have HR frames left after this one
        # After dec, tick_ctr == HR, and we zero ADSR
        a(f'        dec ${z:02X}')           # tick_ctr--
        a(f'        beq v{v}new')             # if 0 -> new note
        a(f'        lda ${z:02X}')
        a(f'        cmp #{HR}')
        a(f'        bne v{v}nhr')
        a(f'        lda #0')
        a(f'        sta $D4{so+5:02X}')       # AD = 0
        a(f'        sta $D4{so+6:02X}')       # SR = 0
        a(f'v{v}nhr')
        a(f'        jmp v{v}wt')              # process wave table
        a('')

        # --- NEW NOTE ---
        a(f'v{v}new')
        a(f'        ldy #0')
        a(f'        lda (${z+1:02X}),y')      # read note byte
        a(f'        cmp #$FF')                 # end marker
        a(f'        bne v{v}nt')
        a(f'        jmp v{v}done')
        a(f'v{v}nt')
        a(f'        sta ${z+6:02X}')           # current_note = pitch

        # Read duration, multiply by tick_length
        a(f'        iny')
        a(f'        lda (${z+1:02X}),y')       # duration byte (D)
        a(f'        clc')
        a(f'        adc #1')                    # D+1 ticks
        if tick_length == 1:
            pass  # frames = ticks
        else:
            a(f'        tax')
            a(f'        lda #0')
            a(f'v{v}mul  clc')
            a(f'        adc #{tick_length}')
            a(f'        dex')
            a(f'        bne v{v}mul')
        a(f'        sta ${z:02X}')              # tick_ctr = (D+1) * tick_length

        # Read instrument ID
        a(f'        iny')
        a(f'        lda (${z+1:02X}),y')
        a(f'        tax')

        # E: set ADSR from instrument
        a(f'        lda i_ad,x')
        a(f'        sta $D4{so+5:02X}')
        a(f'        lda i_sr,x')
        a(f'        sta $D4{so+6:02X}')

        # P: set initial PW from instrument
        a(f'        lda i_pwlo,x')
        a(f'        sta $D4{so+2:02X}')
        a(f'        sta ${z+5:02X}')            # pw_lo accumulator
        a(f'        lda i_pwhi,x')
        a(f'        sta $D4{so+3:02X}')

        # Set wave table pointer
        a(f'        lda i_wlo,x')
        a(f'        sta ${z+3:02X}')
        a(f'        lda i_whi,x')
        a(f'        sta ${z+4:02X}')

        # Reset delta
        a(f'        lda #0')
        a(f'        sta ${z+7:02X}')

        # PW speed to ZP... actually, we read it each frame from the instrument
        # But we need to know WHICH instrument. Store inst ID somewhere.
        # For simplicity: the wave table already encodes the waveform+offset per frame.
        # PW speed: we read it from the table each frame using the instrument.
        # BUT we don't store inst_id. Let's store pw_speed in a ZP byte.
        # Hmm, running out of ZP bytes. Let me use the wave table for everything
        # and handle PW separately.
        #
        # Actually: PW speed is per-instrument, constant during a note.
        # I'll store it in an extra ZP byte. Extend ZP to 9 bytes.

        # Advance note pointer by 3
        a(f'        clc')
        a(f'        lda ${z+1:02X}')
        a(f'        adc #3')
        a(f'        sta ${z+1:02X}')
        a(f'        bcc v{v}wt')
        a(f'        inc ${z+2:02X}')
        a('')

        # --- W(delta) + F(delta): wave table processing ---
        a(f'v{v}wt')
        # Wave table: pairs of (waveform, note_offset)
        # $FF + lo + hi = loop to absolute address
        a(f'        ldy #0')
        a(f'        lda (${z+3:02X}),y')       # read waveform byte
        a(f'        cmp #$FF')
        a(f'        bne v{v}wok')
        # Loop: read 2-byte target address
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # target lo
        a(f'        tax')
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # target hi
        a(f'        sta ${z+4:02X}')
        a(f'        stx ${z+3:02X}')
        a(f'        ldy #0')
        a(f'        lda (${z+3:02X}),y')        # re-read waveform from loop target

        a(f'v{v}wok')
        # W: write waveform to SID ctrl register
        a(f'        sta $D4{so+4:02X}')

        # F: read note offset, add to base note, look up freq table
        a(f'        iny')
        a(f'        lda (${z+3:02X}),y')        # note_offset
        a(f'        clc')
        a(f'        adc ${z+6:02X}')             # + current_note
        a(f'        tax')
        a(f'        lda ftlo,x')
        a(f'        sta $D4{so:02X}')             # freq_lo
        a(f'        lda fthi,x')
        a(f'        sta $D4{so+1:02X}')           # freq_hi

        # Advance wave pointer by 2
        a(f'        clc')
        a(f'        lda ${z+3:02X}')
        a(f'        adc #2')
        a(f'        sta ${z+3:02X}')
        a(f'        bcc v{v}pw')
        a(f'        inc ${z+4:02X}')

        # P: PW modulation (simple linear for now)
        a(f'v{v}pw')
        # Write current PW, then accumulate
        a(f'        lda ${z+5:02X}')
        a(f'        sta $D4{so+2:02X}')
        # TODO: add pw_speed accumulation

        a(f'v{v}done')
        a('')

    a('        rts')
    a('')

    # --- DATA: Frequency Table ---
    a('ftlo')
    for i in range(0, len(T), 16):
        chunk = T[i:i+16]
        a('        .byte ' + ','.join(f'${f & 0xFF:02X}' for f in chunk))
    a('fthi')
    for i in range(0, len(T), 16):
        chunk = T[i:i+16]
        a('        .byte ' + ','.join(f'${(f >> 8) & 0xFF:02X}' for f in chunk))
    a('')

    # --- DATA: Instrument columns ---
    a('i_ad')
    a('        .byte ' + ','.join(f'${i["ad"]:02X}' for i in instruments))
    a('i_sr')
    a('        .byte ' + ','.join(f'${i["sr"]:02X}' for i in instruments))
    a('i_pwlo')
    a('        .byte ' + ','.join(f'${i["pw"] & 0xFF:02X}' for i in instruments))
    a('i_pwhi')
    a('        .byte ' + ','.join(f'${(i["pw"] >> 8) & 0x0F:02X}' for i in instruments))
    a('i_wlo')
    a('        .byte ' + ','.join(f'<wt{i["id"]}' for i in instruments))
    a('i_whi')
    a('        .byte ' + ','.join(f'>wt{i["id"]}' for i in instruments))
    a('')

    # --- DATA: Wave tables per instrument ---
    for inst in instruments:
        iid = inst['id']
        ctrl = inst['ctrl']
        has_drum = inst['has_drum']
        has_arp = inst['has_arp']

        a(f'wt{iid}')

        if has_drum:
            # W: gate on, noise burst frames 1-2, sustain after
            # F: if has_arp, alternate offset 0/12
            a(f'wt{iid}b0')
            a(f'        .byte ${ctrl | 0x01:02X},$00')      # frame 0: gate on, base note
            if has_arp:
                a(f'        .byte $80,$0C')                    # frame 1: noise, note+12
                a(f'        .byte $80,$00')                    # frame 2: noise, base note
                a(f'wt{iid}b6')
                a(f'        .byte ${ctrl & 0xFE:02X},$0C')    # frame 3: sustain, note+12
                a(f'        .byte ${ctrl & 0xFE:02X},$00')    # frame 4: sustain, base note
                a(f'        .byte $FF,<wt{iid}b6,>wt{iid}b6')  # loop to frame 3
            else:
                a(f'        .byte $80,$00')                    # frame 1: noise, base note
                a(f'        .byte $80,$00')                    # frame 2: noise, base note
                a(f'wt{iid}b6')
                a(f'        .byte ${ctrl & 0xFE:02X},$00')    # frame 3: sustain
                a(f'        .byte $FF,<wt{iid}b6,>wt{iid}b6')  # loop to frame 3
        else:
            # W: gate on (player handles gate-off via HR)
            # F: no offset changes
            a(f'wt{iid}b0')
            a(f'        .byte ${ctrl | 0x01:02X},$00')        # gate on, base note
            a(f'        .byte $FF,<wt{iid}b0,>wt{iid}b0')    # loop to self (gate stays on)
        a('')

    # --- DATA: Note streams per voice ---
    for v in range(3):
        a(f'v{v}notes')
        voice = score['voices'][v]
        for pat_idx in voice['orderlist']:
            notes = voice['patterns'][pat_idx]
            for note in notes:
                pitch = note['pitch'] & 0xFF
                dur = note['duration'] & 0xFF
                inst_id = note['instrument'] & 0xFF
                a(f'        .byte ${pitch:02X},${dur:02X},${inst_id:02X}')
        a(f'        .byte $FF')  # end marker
    a('')

    return '\n'.join(L)


# ===================================================================
# Step 3: Assemble and build PSID
# ===================================================================

def build_sid(asm_text, output_path):
    """Assemble xa65 source and wrap in PSID."""
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

    # PSID header from original
    with open(SID_PATH, 'rb') as f:
        orig = f.read()
    header_len = struct.unpack('>H', orig[6:8])[0]
    header = bytearray(orig[:header_len])
    struct.pack_into('>H', header, 8, 0)      # load from data
    struct.pack_into('>H', header, 10, 0x1000) # init
    struct.pack_into('>H', header, 12, 0x1003) # play
    struct.pack_into('>H', header, 14, 1)      # songs
    struct.pack_into('>H', header, 16, 1)      # default

    sid_data = bytes(header) + struct.pack('<H', 0x1000) + binary

    with open(output_path, 'wb') as f:
        f.write(sid_data)

    end_addr = 0x1000 + len(binary)
    print(f"SID: {len(sid_data)} bytes ({len(sid_data)/1024:.1f} KB), "
          f"end ${end_addr:04X}")
    return True


# ===================================================================
# Step 4: Verify against ground truth
# ===================================================================

def verify(output_path, max_frames=500):
    """Compare register output frame by frame against py65 ground truth."""
    from ground_truth import capture_sid as gt_capture
    from collections import Counter
    from py65.devices.mpu6502 import MPU

    # Ground truth
    gt_result = gt_capture(SID_PATH, subtunes=[1], max_frames=max_frames,
                           detect_loop=False)
    gt = gt_result.subtunes[0].frames
    N = len(gt)

    # Our SID
    with open(output_path, 'rb') as f:
        sid = f.read()
    hl = struct.unpack('>H', sid[6:8])[0]
    la = struct.unpack('>H', sid[8:10])[0]
    code = sid[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    mem = bytearray(65536)
    mem[la:la + len(code)] = code
    m = MPU()
    m.memory = bytearray(mem)
    m.memory[0xFFF0] = 0x00
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = la; m.a = 0
    for _ in range(50000):
        if m.memory[m.pc] == 0x00:
            break
        m.step()

    rn = ['flo', 'fhi', 'plo', 'phi', 'ctl', 'ad', 'sr']
    errors = Counter()
    perfect = 0

    for fr in range(N):
        m.stPush(0xFF); m.stPush(0xEF)
        m.pc = la + 3
        for _ in range(50000):
            if m.memory[m.pc] == 0x00:
                break
            m.step()

        ok = True
        for v, vo in enumerate([0, 7, 14]):
            for r in range(7):
                us = m.memory[0xD400 + vo + r]
                g = gt[fr][vo + r]
                if us != g:
                    errors[(f'V{v+1}', rn[r])] += 1
                    ok = False
        if ok:
            perfect += 1

    print(f"\npy65 verification: {N} frames")
    print(f"Perfect: {perfect}/{N} ({100*perfect/N:.1f}%)")
    for (v, r), cnt in errors.most_common():
        print(f"  {cnt:4d}/{N} ({100*cnt/N:5.1f}%) {v} {r}")
    return perfect, N


# ===================================================================
# Main
# ===================================================================

if __name__ == '__main__':
    print("Das Model Gen — clean implementation from spec")
    print("=" * 50)

    print("\n[1] Extracting (T, I, S) from binary...")
    T, instruments, score = extract()
    print(f"    T: {len(T)} entries")
    print(f"    I: {len(instruments)} instruments")
    print(f"    S: {len(score['voices'])} voices, "
          f"tick_length={score['tick_length']}")
    for v in range(3):
        n_pats = len(score['voices'][v]['orderlist'])
        print(f"    V{v+1}: {n_pats} patterns in orderlist")

    print("\n[2] Generating 6502 assembly...")
    asm = generate_asm(T, instruments, score)

    print("\n[3] Assembling and building PSID...")
    ok = build_sid(asm, OUT_PATH)
    if not ok:
        sys.exit(1)

    print("\n[4] Verifying against ground truth...")
    perfect, total = verify(OUT_PATH, max_frames=200)
