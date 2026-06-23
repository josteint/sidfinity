#!/usr/bin/env python3
"""One-tune end-to-end PROOF for the Basic_Program family.

SID (RSID-BASIC) --capture--> musical model --emit--> PSID, whose $D400
write stream matches the original's (flat (reg,val), the project's Mode-1
verdict via compare_instruction_stream).

Proof tune: Twinkle (DEMOS/UNKNOWN/Twinkle_BASIC.sid) — the canonical
single-voice "POKE recipe": init vol/AD/SR, then per note
[freq_hi, freq_lo, ctrl=gate_on, hold, ctrl=gate_off, rest]. The musical
content is a (note, duration) list + one triangle instrument.

This first stage proves the WRITELOG MATCH with a minimal dedicated player
(the Hubbard composer would add per-frame writes Twinkle doesn't have).
The USF round-trip is layered on once the match holds.
"""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))

from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header

SID = os.path.join(ROOT, 'hvsc84/DEMOS/UNKNOWN/Twinkle_BASIC.sid')
LOAD = 0x1000

# ---------------------------------------------------------------- lift ----
def flatten(frames):
    """frames (list of [(reg,val),...]) -> list of (frame_idx, reg, val)."""
    out = []
    for fi, fr in enumerate(frames):
        for cyc, reg, val in fr:
            out.append((fi, reg, val))
    return out

def freq_to_note_index(freq16):
    """PAL freq value -> (note_index=(oct<<4)|semi, name, octave)."""
    f_hz = freq16 * 985248.0 / 16777216.0
    midi = round(12 * math.log2(f_hz / 440.0)) + 69
    octave = midi // 12 - 1
    semi = midi % 12
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return ((octave << 4) | semi, names[semi], octave)

def lift(frames):
    stream = flatten(frames)
    init = []           # (reg,val) before the first freq write
    i = 0
    while i < len(stream) and stream[i][1] not in (0x00, 0x01):
        init.append((stream[i][1], stream[i][2]))
        i += 1
    # walk notes: fhi(reg1), flo(reg0), ctrl-on(reg4 &1), ... ctrl-off(reg4 &~1)
    notes = []          # dict: freq, note_index, name, octave, dur_frames, gap_frames, wave
    cur = None
    last_gateoff_frame = None
    for fi, reg, val in stream[i:]:
        if reg == 0x01:          # freq hi -> new note begins
            if cur and cur.get('gate_off_frame') is not None and last_gateoff_frame is None:
                pass
            cur = {'fhi': val}
        elif reg == 0x00 and cur is not None:
            cur['flo'] = val
        elif reg == 0x04 and cur is not None:
            if val & 0x01:        # gate on
                cur['wave'] = val & 0xF0
                cur['gate_on_frame'] = fi
            else:                  # gate off -> note complete
                cur['gate_off_frame'] = fi
                cur['dur_frames'] = fi - cur['gate_on_frame']
                freq = (cur['fhi'] << 8) | cur.get('flo', 0)
                ni, name, octv = freq_to_note_index(freq)
                cur.update(freq=freq, note_index=ni, name=name, octave=octv)
                notes.append(cur)
                cur = None
    # gap_frames = next note's gate_on - this note's gate_off
    for n in range(len(notes) - 1):
        notes[n]['gap_frames'] = notes[n+1]['gate_on_frame'] - notes[n]['gate_off_frame']
    if notes:
        notes[-1]['gap_frames'] = notes[-1].get('gap_frames', 5)
    # build freq table (256 bytes: 128 hi + 128 lo)
    ftab = bytearray(256)
    for n in notes:
        ni = n['note_index']
        ftab[ni] = (n['freq'] >> 8) & 0xFF
        ftab[128 + ni] = n['freq'] & 0xFF
    # instrument: waveform from first note, AD/SR from init
    wave = notes[0]['wave'] if notes else 0x10
    ad = dict(init).get(0x05, 0)
    sr = dict(init).get(0x06, 0)
    return {'init': init, 'notes': notes, 'ftab': bytes(ftab),
            'wave': wave, 'ad': ad, 'sr': sr}

# ------------------------------------------------------------- emit asm ----
def build_player_asm(L):
    notes = L['notes']
    # detect the loop point: the melody repeats; find period by matching the
    # note_index sequence prefix against a later repeat. For the proof we play
    # the captured note list once then loop the whole list.
    nidx = [n['note_index'] for n in notes]
    dur = [min(n['dur_frames'], 255) for n in notes]
    gap = [min(n.get('gap_frames', 5), 255) for n in notes]
    N = len(notes)
    lines = []
    em = lines.append
    em(f'* = ${LOAD:04X}')
    em('        jmp init')
    em('        jmp play')
    # --- init: emit the PROGRAM's init writes, then prime player state ---
    # The PSID driver itself emits a leading $D418=$0F (an empty-init PSID
    # produces exactly that one write), and the capture of the RSID-BASIC
    # original begins with the same driver write. So strip that driver
    # prefix from the lifted init to avoid duplicating it.
    DRIVER_PREFIX = [(0x18, 0x0F)]
    prog_init = L['init']
    if prog_init[:len(DRIVER_PREFIX)] == DRIVER_PREFIX:
        prog_init = prog_init[len(DRIVER_PREFIX):]
    em('init:')
    for reg, val in prog_init:
        em(f'        lda #${val:02X}')
        em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    em('        sta noteidx')
    em('        sta phase')          # 0 = start next note
    em('        sta done')           # 0 = not finished
    em('        lda #$01')
    em('        sta countdown')      # fire on first play
    em('        rts')
    # --- play: per-frame note sequencer (plays the note list ONCE) ---
    em('play:')
    em('        lda done')
    em('        bne pl_ret')         # finished -> emit nothing
    em('        dec countdown')
    em('        beq advance')
    em('pl_ret:')
    em('        rts')
    em('advance:')
    em('        lda phase')
    em('        bne gateoff')
    # gate on: set freq from table, ctrl = wave|gate
    em('gateon:')
    em('        ldx noteidx')
    em('        lda notes_note,x')
    em('        tay')
    em('        lda freqtab,y')       # hi
    em('        sta $D401')
    em('        lda freqtab+128,y')   # lo
    em('        sta $D400')
    em(f'        lda #${(L["wave"] | 0x01):02X}')
    em('        sta $D404')
    em('        lda notes_dur,x')
    em('        sta countdown')
    em('        lda #$01')
    em('        sta phase')
    em('        rts')
    # gate off: ctrl = wave (gate clear), schedule gap, advance/loop
    em('gateoff:')
    em(f'        lda #${L["wave"]:02X}')
    em('        sta $D404')
    em('        ldx noteidx')
    em('        lda notes_gap,x')
    em('        sta countdown')
    em('        lda #$00')
    em('        sta phase')
    em('        inc noteidx')
    em('        lda noteidx')
    em(f'        cmp #${N:02X}')
    em('        bne pl_done')
    em('        lda #$01')           # past last note -> finished
    em('        sta done')
    em('pl_done:')
    em('        rts')
    # --- state ---
    em('noteidx:   .byte 0')
    em('phase:     .byte 0')
    em('countdown: .byte 0')
    em('done:      .byte 0')
    # --- data ---
    def bytes_block(label, data):
        em(f'{label}:')
        for o in range(0, len(data), 16):
            em('        .byte ' + ', '.join(f'${b:02X}' for b in data[o:o+16]))
    bytes_block('notes_note', nidx)
    bytes_block('notes_dur', dur)
    bytes_block('notes_gap', gap)
    bytes_block('freqtab', L['ftab'])
    return '\n'.join(lines)

def build_psid(L):
    asm = build_player_asm(L)
    body = assemble(asm)
    hdr = build_header(load=LOAD, init=LOAD, play=LOAD + 3, songs=1,
                       start_song=1, speed=0,
                       title='Twinkle', author='unknown', released='proof')
    return hdr + body, asm

# ----------------------------------------------------------------- main ----
def main():
    dur = 12.0
    orig = writelog_capture(SID, subtune=0, duration=dur)
    L = lift(orig)
    print(f"lifted: {len(L['notes'])} notes; init={['%02X:%02X'%(r,v) for r,v in L['init']]}")
    print("  note seq:", " ".join(f"{n['name']}{n['octave']}" for n in L['notes'][:20]))
    print("  durs    :", " ".join(str(min(n['dur_frames'],255)) for n in L['notes'][:20]))
    sid_bytes, asm = build_psid(L)
    out = os.path.join(ROOT, 'tmp/basic_program_research/Twinkle.sidfinity.sid')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'wb') as f:
        f.write(sid_bytes)
    print(f"built PSID -> {out} ({len(sid_bytes)} bytes)")
    rebuilt = writelog_capture(out, subtune=0, duration=dur)
    res = compare_instruction_stream(orig, rebuilt, skip_init=False)
    print("VERDICT (flat, skip_init=False):", res)
    res2 = compare_instruction_stream(orig, rebuilt, skip_init=True)
    print("VERDICT (flat, skip_init=True): ", res2)

if __name__ == '__main__':
    main()
