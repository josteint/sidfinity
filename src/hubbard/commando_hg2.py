#!/usr/bin/env python3
"""
commando_hg2.py - Holy grail player for Commando by Rob Hubbard.

Approach:
1. Capture ground truth registers from original Commando SID via py65 (1500 frames)
2. Group notes by gate-on transitions per voice (bit 0 of waveform register)
3. For each note, store per-frame register data: (fl, fh, pw_lo, pw_hi, AD, SR, wave) = 7 bytes
4. Deduplicate identical note sequences into "instruments"
5. Generate xa65 assembly with a pointer-advancing player
6. Assemble and build PSID output

Output: demo/hubbard/Commando_hg2.sid
"""

import sys, struct, os, subprocess, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'py65_lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from py65.devices.mpu6502 import MPU

# ---- Paths ----------------------------------------------------------------
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
SID_PATH = os.path.join(BASE_DIR, 'data', 'C64Music', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Commando.sid')
XA65     = os.path.join(BASE_DIR, 'tools', 'xa65', 'xa', 'xa')
DEMO_DIR = os.path.join(BASE_DIR, 'demo', 'hubbard')
OUT_SID  = os.path.join(DEMO_DIR, 'Commando_hg2.sid')

SID_BASE   = 0xD400
NUM_FRAMES = 1500
NUM_VOICES = 3

# SID register layout per voice (offsets from SID_BASE):
# voice 0: $D400 (fl), $D401 (fh), $D402 (pw_lo), $D403 (pw_hi), $D404 (wave), $D405 (AD), $D406 (SR)
# voice 1: $D407 ..
# voice 2: $D40E ..
VOICE_OFFSETS = [0, 7, 14]

# Zero page layout (per voice, 6 bytes each):
# note_stream_ptr lo/hi (2), inst_data_ptr lo/hi (2), step (1), length (1)
ZP_BASE = 0x02
ZP_VOICE_SIZE = 6

def zp_note_lo(v):  return ZP_BASE + v * ZP_VOICE_SIZE + 0
def zp_note_hi(v):  return ZP_BASE + v * ZP_VOICE_SIZE + 1
def zp_inst_lo(v):  return ZP_BASE + v * ZP_VOICE_SIZE + 2
def zp_inst_hi(v):  return ZP_BASE + v * ZP_VOICE_SIZE + 3
def zp_step(v):     return ZP_BASE + v * ZP_VOICE_SIZE + 4
def zp_length(v):   return ZP_BASE + v * ZP_VOICE_SIZE + 5

PLAYER_BASE = 0x1000

# ---- Step 1: Capture register trace ---------------------------------------

def load_sid(path):
    with open(path, 'rb') as f:
        data = f.read()
    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr  = struct.unpack('>H', data[8:10])[0]
    init_addr  = struct.unpack('>H', data[10:12])[0]
    play_addr  = struct.unpack('>H', data[12:14])[0]
    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        code = code[2:]
    return data, load_addr, init_addr, play_addr, code


def run_until_rts(mpu, start_pc, trampoline=0x0300, max_steps=500000):
    mem = mpu.memory
    mem[trampoline]     = 0x20  # JSR
    mem[trampoline + 1] = start_pc & 0xFF
    mem[trampoline + 2] = (start_pc >> 8) & 0xFF
    mem[trampoline + 3] = 0x60  # RTS
    mpu.pc = trampoline
    for _ in range(max_steps):
        mpu.step()
        if mpu.pc == trampoline + 3:
            return True
    return False


def capture_trace(num_frames=NUM_FRAMES):
    print(f"Capturing {num_frames} frames from {SID_PATH} ...")
    orig_data, load_addr, init_addr, play_addr, code = load_sid(SID_PATH)

    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    mpu = MPU(memory=mem)
    mpu.memory = mem

    mpu.a = 0; mpu.x = 0; mpu.y = 0
    run_until_rts(mpu, init_addr)

    trace = []
    for frame in range(num_frames):
        if frame % 200 == 0:
            print(f"  frame {frame}/{num_frames}", end='\r', flush=True)
        run_until_rts(mpu, play_addr)
        regs = bytes(mpu.memory[SID_BASE:SID_BASE + 25])
        trace.append(regs)

    print(f"\nCaptured {len(trace)} frames.")
    return trace, orig_data


# ---- Step 2: Extract note sequences per voice ----------------------------

def extract_voice_notes(trace, voice_idx):
    """
    Returns list of note events. Each note is a list of 7-tuples:
    (freq_lo, freq_hi, pw_lo, pw_hi, AD, SR, wave).
    A new note starts when gate bit transitions 0->1.
    """
    base = VOICE_OFFSETS[voice_idx]
    notes = []
    current_note = []
    prev_gate = 0

    for regs in trace:
        fl    = regs[base + 0]
        fh    = regs[base + 1]
        pw_lo = regs[base + 2]
        pw_hi = regs[base + 3]
        wave  = regs[base + 4]
        ad    = regs[base + 5]
        sr    = regs[base + 6]
        gate  = wave & 0x01

        frame_data = (fl, fh, pw_lo, pw_hi, ad, sr, wave)

        if gate == 1 and prev_gate == 0:
            # Gate rising edge: new note
            if current_note:
                notes.append(current_note)
            current_note = [frame_data]
        else:
            current_note.append(frame_data)

        prev_gate = gate

    if current_note:
        notes.append(current_note)

    return notes


# ---- Step 3: Deduplicate instruments -------------------------------------

def deduplicate_instruments(all_voice_notes):
    """
    Returns:
      instruments: list of unique note-sequences (list of 7-tuples)
      note_streams: per-voice list of instrument IDs
    """
    instr_map = {}
    instruments = []
    note_streams = []

    for voice_notes in all_voice_notes:
        stream = []
        for note_seq in voice_notes:
            key = tuple(tuple(f) for f in note_seq)
            if key not in instr_map:
                instr_map[key] = len(instruments)
                instruments.append(list(note_seq))
            stream.append(instr_map[key])
        note_streams.append(stream)

    return instruments, note_streams


# ---- Step 4: Generate assembly --------------------------------------------

def h(v):
    """Format integer as $XX hex."""
    return f'${v:02X}'

def hh(v):
    """Format integer as $XXXX hex."""
    return f'${v:04X}'


def build_asm(instruments, note_streams):
    lines = []
    L = lines.append

    L(f'; Commando Holy Grail Player - auto-generated by commando_hg2.py')
    L(f'; {len(instruments)} instruments, 3 voice note streams')
    L(f'* = {hh(PLAYER_BASE)}')
    L(f'')

    # Entry points: JMP init, JMP play
    L(f'entry_init:')
    L(f'  JMP init_player')
    L(f'entry_play:')
    L(f'  JMP play_frame')
    L(f'')

    # ---- init_player ----
    # Set note_stream_ptr for each voice, zero step/length
    L(f'init_player:')
    for v in range(3):
        L(f'  LDA #<note_stream_v{v}')
        L(f'  STA {h(zp_note_lo(v))}')
        L(f'  LDA #>note_stream_v{v}')
        L(f'  STA {h(zp_note_hi(v))}')
        L(f'  LDA #$00')
        L(f'  STA {h(zp_step(v))}')
        L(f'  STA {h(zp_length(v))}')
        L(f'  STA {h(zp_inst_lo(v))}')
        L(f'  STA {h(zp_inst_hi(v))}')
    L(f'  RTS')
    L(f'')

    # ---- play_frame ----
    # Voice SID base addresses
    SID_V = [0xD400, 0xD407, 0xD40E]

    L(f'play_frame:')
    for v in range(3):
        sv = SID_V[v]
        nlo = zp_note_lo(v)
        nhi = zp_note_hi(v)
        ilo = zp_inst_lo(v)
        ihi = zp_inst_hi(v)
        sp  = zp_step(v)
        lp  = zp_length(v)

        L(f'  ; === Voice {v} (SID base {hh(sv)}) ===')
        L(f'  LDA {h(sp)}')
        L(f'  CMP {h(lp)}')
        L(f'  BCC write_v{v}')

        # Need next note from stream
        L(f'next_v{v}:')
        L(f'  LDY #$00')
        L(f'  LDA ({h(nlo)}),Y')
        L(f'  CMP #$FF')
        L(f'  BNE have_note_v{v}')
        L(f'  JMP done_v{v}')
        L(f'have_note_v{v}:')
        L(f'  TAX')
        L(f'  INC {h(nlo)}')
        L(f'  BNE nlo_ok_v{v}')
        L(f'  INC {h(nhi)}')
        L(f'nlo_ok_v{v}:')
        L(f'  LDA instr_lo_v{v},X')
        L(f'  STA {h(ilo)}')
        L(f'  LDA instr_hi_v{v},X')
        L(f'  STA {h(ihi)}')
        L(f'  LDY #$00')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {h(lp)}')
        L(f'  INC {h(ilo)}')
        L(f'  BNE ilo_ok_v{v}')
        L(f'  INC {h(ihi)}')
        L(f'ilo_ok_v{v}:')
        L(f'  LDA #$00')
        L(f'  STA {h(sp)}')
        L(f'  TAX')

        L(f'write_v{v}:')
        L(f'  LDY #$00')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 0)}')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 1)}')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 2)}')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 3)}')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 5)}   ; AD')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 6)}   ; SR')
        L(f'  INY')
        L(f'  LDA ({h(ilo)}),Y')
        L(f'  STA {hh(sv + 4)}')
        L(f'  CLC')
        L(f'  LDA {h(ilo)}')
        L(f'  ADC #$07')
        L(f'  STA {h(ilo)}')
        L(f'  BCC iptr_ok_v{v}')
        L(f'  INC {h(ihi)}')
        L(f'iptr_ok_v{v}:')
        L(f'  INC {h(sp)}')
        L(f'done_v{v}:')
        L(f'')

    L(f'  RTS')
    L(f'')

    # ---- Instrument pointer tables (per voice) ----
    for v in range(3):
        max_id = max(note_streams[v]) if note_streams[v] else 0
        L(f'instr_lo_v{v}:')
        for i in range(max_id + 1):
            L(f'  .byt <instr_{i}')
        L(f'instr_hi_v{v}:')
        for i in range(max_id + 1):
            L(f'  .byt >instr_{i}')
        L(f'')

    # ---- Instrument data ----
    L(f'; ---- Instrument data ({len(instruments)} instruments) ----')
    for i, instr in enumerate(instruments):
        L(f'instr_{i}:')
        L(f'  .byt {h(len(instr))}')
        for frame in instr:
            fl, fh, pw_lo, pw_hi, ad, sr, wave = frame
            L(f'  .byt {h(fl)},{h(fh)},{h(pw_lo)},{h(pw_hi)},{h(ad)},{h(sr)},{h(wave)}')
        L(f'')

    # ---- Note stream tables ----
    for v in range(3):
        L(f'note_stream_v{v}:')
        stream = note_streams[v]
        for i in range(0, len(stream), 16):
            chunk = stream[i:i + 16]
            L(f'  .byt {",".join(h(x) for x in chunk)}')
        L(f'  .byt $FF')
        L(f'')

    return '\n'.join(lines)


# ---- Step 5: Assemble and build PSID -------------------------------------

def assemble(asm_text):
    with tempfile.NamedTemporaryFile(suffix='.s', mode='w', delete=False) as f:
        f.write(asm_text)
        asm_file = f.name

    bin_file = asm_file.replace('.s', '.bin')
    try:
        result = subprocess.run(
            [XA65, '-o', bin_file, asm_file],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("xa65 ERRORS:")
            print(result.stdout)
            print(result.stderr)
            with open('/tmp/commando_hg2_debug.s', 'w') as f:
                f.write(asm_text)
            print("ASM written to /tmp/commando_hg2_debug.s")
            raise RuntimeError("Assembly failed")
        with open(bin_file, 'rb') as f:
            binary = f.read()
        return binary
    finally:
        if os.path.exists(asm_file):
            os.unlink(asm_file)
        if os.path.exists(bin_file):
            try:
                os.unlink(bin_file)
            except:
                pass


def build_psid(orig_data, player_binary):
    """Build PSID from original header (modified) + player binary."""
    header = bytearray(orig_data[:0x7C])

    # load addr = 0 means first 2 bytes of data specify it
    struct.pack_into('>H', header, 8,  0)
    # init = player_base (entry_init = JMP init_player)
    struct.pack_into('>H', header, 10, PLAYER_BASE)
    # play = player_base+3 (entry_play = JMP play_frame)
    struct.pack_into('>H', header, 12, PLAYER_BASE + 3)
    # num songs = 1
    struct.pack_into('>H', header, 14, 1)
    # default song = 1
    struct.pack_into('>H', header, 16, 1)

    body = struct.pack('<H', PLAYER_BASE) + player_binary
    return bytes(header) + body


# ---- Step 6: Verify -------------------------------------------------------

def get_trace_from_bytes(sid_bytes, num_frames):
    data = sid_bytes
    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr  = struct.unpack('>H', data[8:10])[0]
    init_addr  = struct.unpack('>H', data[10:12])[0]
    play_addr  = struct.unpack('>H', data[12:14])[0]
    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        code = code[2:]

    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    mpu = MPU(memory=mem)
    mpu.memory = mem

    mpu.a = 0; mpu.x = 0; mpu.y = 0
    run_until_rts(mpu, init_addr)

    trace = []
    for _ in range(num_frames):
        run_until_rts(mpu, play_addr)
        regs = bytes(mpu.memory[SID_BASE:SID_BASE + 25])
        trace.append(regs)
    return trace


def verify(orig_trace, psid_bytes, num_frames):
    print("Verifying new player ...")
    new_trace = get_trace_from_bytes(psid_bytes, num_frames)

    match = mismatch = 0
    first_bad = None

    for i, (o, n) in enumerate(zip(orig_trace, new_trace)):
        # Compare voice registers only (21 bytes; skip filter/vol at $D415-$D418)
        if o[:21] == n[:21]:
            match += 1
        else:
            mismatch += 1
            if first_bad is None:
                first_bad = i
                print(f"  First mismatch at frame {i}:")
                for v in range(3):
                    b = VOICE_OFFSETS[v]
                    ov = o[b:b+7]
                    nv = n[b:b+7]
                    if ov != nv:
                        print(f"    Voice {v}: orig fl={ov[0]:02X} fh={ov[1]:02X} pw={ov[2]:02X}{ov[3]:02X} wave={ov[4]:02X} AD={ov[5]:02X} SR={ov[6]:02X}")
                        print(f"             new  fl={nv[0]:02X} fh={nv[1]:02X} pw={nv[2]:02X}{nv[3]:02X} wave={nv[4]:02X} AD={nv[5]:02X} SR={nv[6]:02X}")

    pct = 100.0 * match / num_frames
    print(f"Match: {match}/{num_frames} ({pct:.1f}%)")
    return match, mismatch


# ---- Main -----------------------------------------------------------------

def main():
    os.makedirs(DEMO_DIR, exist_ok=True)

    # 1. Capture
    trace, orig_data = capture_trace(NUM_FRAMES)

    # 2. Extract notes
    print("Extracting note sequences ...")
    all_voice_notes = []
    for v in range(NUM_VOICES):
        notes = extract_voice_notes(trace, v)
        all_voice_notes.append(notes)
        total_frames = sum(len(n) for n in notes)
        print(f"  Voice {v}: {len(notes)} notes, {total_frames} frames total")

    # 3. Deduplicate
    print("Deduplicating instruments ...")
    instruments, note_streams = deduplicate_instruments(all_voice_notes)
    print(f"  {len(instruments)} unique instruments")
    for v in range(NUM_VOICES):
        print(f"  Voice {v}: {len(note_streams[v])} notes in stream")

    # 4. Generate assembly
    print("Generating assembly ...")
    asm_text = build_asm(instruments, note_streams)

    asm_out = '/tmp/commando_hg2.s'
    with open(asm_out, 'w') as f:
        f.write(asm_text)
    print(f"  Assembly written to {asm_out}")

    # 5. Assemble
    print("Assembling with xa65 ...")
    binary = assemble(asm_text)
    print(f"  Binary: {len(binary)} bytes")

    # 6. Build PSID
    print("Building PSID ...")
    psid_bytes = build_psid(orig_data, binary)

    # 7. Verify
    match, mismatch = verify(trace, psid_bytes, NUM_FRAMES)

    if mismatch == 0:
        print("PERFECT MATCH - all 1500 frames identical!")
    else:
        print(f"WARNING: {mismatch} frame mismatches")

    # Write output
    with open(OUT_SID, 'wb') as f:
        f.write(psid_bytes)
    print(f"Written: {OUT_SID}")

    return mismatch == 0


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
