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

import subprocess, re
from pipelines.hubbard.verify_cycle import (writelog_capture,
                                            compare_instruction_stream, SIDDUMP)
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header
from src.usf import (UsfFile, PsidMeta, Params, InitState, InitSid, Instrument,
                     MusicSubtune, VoiceBlock, Pattern, NoteRow, Orderlist,
                     Pitch, InstrumentRef, write_file, parse_file)

SID = os.path.join(ROOT, 'hvsc84/DEMOS/UNKNOWN/Twinkle_BASIC.sid')
LOAD = 0x1000
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# ---------------------------------------------------------------- lift ----
def capture_real(sid_path, duration):
    """Capture writelog with REAL frame indices (every siddump frame is a
    line; writelog_capture drops empty frames, losing hold-duration). Returns
    list-of-frames where index = real frame number, each = [(cyc,reg,val),...].
    """
    r = subprocess.run([SIDDUMP, sid_path, '--writelog', '--duration',
                        str(duration)], capture_output=True, text=True)
    frames = []
    for line in r.stdout.splitlines():
        if ',' not in line.split('|')[0]:
            continue   # skip the 2 header lines (json + column names)
        writes = []
        if '|W:' in line:
            toks = line.split('|W:', 1)[1].strip().split(':')
            for i in range(0, len(toks) - 2, 3):
                try:
                    writes.append((int(toks[i]), int(toks[i+1], 16),
                                   int(toks[i+2], 16)))
                except ValueError:
                    pass
        frames.append(writes)
    return frames

def flatten(frames):
    """frames (list of [(cyc,reg,val),...]) -> list of (frame_idx, reg, val)."""
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

# ----------------------------------------------------- USF round-trip ----
def model_to_usf(L):
    """Lifted model -> USF v2 (shared schema). Musical content only:
    one triangle instrument, a per-tune freq_table, and a single voice whose
    pattern alternates note-row (hold) + rest-row (gap)."""
    rows = []
    for n in L['notes']:
        rows.append(NoteRow(pitch=Pitch(name=n['name'], octave=n['octave']),
                            duration=max(n['dur_frames'], 1),
                            instr=InstrumentRef(id=1)))
        rows.append(NoteRow(pitch=Pitch.rest(),
                            duration=max(n.get('gap_frames', 5), 1)))
    length = sum(r.duration for r in rows)
    voice1 = VoiceBlock(id=1, orderlist=Orderlist(entries=[1], stop=True),
                        patterns=[Pattern(id=1, length=length, rows=rows)])
    sub = MusicSubtune(id=0, tempo=1, voices=[
        voice1,
        VoiceBlock(id=2, orderlist=Orderlist(stop=True)),
        VoiceBlock(id=3, orderlist=Orderlist(stop=True))])
    return UsfFile(
        psid=PsidMeta(title='Twinkle', author='unknown', released='proof',
                      clock='PAL', sid=6581, start_song=1, speed=0),
        params=Params(fields={}),
        init=InitState(sid=InitSid(master_vol=dict(L['init']).get(0x18, 0x0F))),
        instruments=[Instrument(id=1, waveform=[L['wave']],
                                adsr=(L['ad'], L['sr']))],
        freq_table=list(L['ftab']),
        subtunes=[sub])

def playerdata_from_usf(usf):
    """Reconstruct the player inputs from a PARSED USF (proves the build
    consumes the .usf, not the in-memory lift)."""
    instr = usf.instruments[0]
    ad, sr = instr.adsr
    wave = instr.waveform[0]
    vol = usf.init.sid.master_vol
    ftab = bytes(usf.freq_table)
    sub = usf.subtunes[0]
    pat = sub.voices[0].patterns[0]
    notes = []
    rows = pat.rows
    for i in range(0, len(rows) - 1, 2):
        note, rest = rows[i], rows[i + 1]
        semi = NAMES.index(note.pitch.name)
        ni = (note.pitch.octave << 4) | semi
        notes.append({'note_index': ni, 'dur_frames': note.duration,
                      'gap_frames': rest.duration})
    # init = program writes only (driver supplies the leading $D418=$0F)
    return {'init': [(0x05, ad), (0x06, sr), (0x18, vol)], 'notes': notes,
            'ftab': ftab, 'wave': wave, 'ad': ad, 'sr': sr}

# ----------------------------------------------------------------- main ----
def note_onset_frames(frames):
    """Real frame index of each gate-on (reg 04 with gate bit) — for rhythm."""
    onsets = []
    for fi, fr in enumerate(frames):
        for cyc, reg, val in fr:
            if reg == 0x04 and (val & 0x01):
                onsets.append(fi)
    return onsets

def main():
    dur = 12.0
    # --- SID -> musical model (real durations from raw-frame capture) ---
    orig_real = capture_real(SID, dur)
    L = lift(orig_real)
    print(f"lifted: {len(L['notes'])} notes; "
          f"init(prog)={['%02X:%02X'%(r,v) for r,v in L['init'][1:]]}")
    print("  note seq:", " ".join(f"{n['name']}{n['octave']}" for n in L['notes']))
    print("  hold/gap frames:",
          " ".join(f"{n['dur_frames']}/{n.get('gap_frames','?')}" for n in L['notes'][:8]), "...")
    # --- model -> .usf (write) -> .usf (parse): SID -> USF -> SID ---
    usf_obj = model_to_usf(L)
    usf_path = os.path.join(ROOT, 'tmp/basic_program_research/Twinkle.usf')
    os.makedirs(os.path.dirname(usf_path), exist_ok=True)
    write_file(usf_obj, usf_path)
    usf_parsed = parse_file(usf_path)
    print(f"wrote + reparsed {usf_path}")
    # --- USF -> PSID (build consumes the PARSED usf) ---
    PD = playerdata_from_usf(usf_parsed)
    sid_bytes, asm = build_psid(PD)
    out = os.path.join(ROOT, 'tmp/basic_program_research/Twinkle.sidfinity.sid')
    with open(out, 'wb') as f:
        f.write(sid_bytes)
    print(f"built PSID -> {out} ({len(sid_bytes)} bytes)")
    # --- VERDICT: flat (reg,val) writelog match (project Mode-1) ---
    orig = writelog_capture(SID, subtune=0, duration=dur)
    rebuilt = writelog_capture(out, subtune=0, duration=dur)
    res = compare_instruction_stream(orig, rebuilt, skip_init=False)
    print(f"\nWRITELOG VERDICT (flat): is_full={res['is_full']} "
          f"match={res['match']}/{res['len_a']} (orig) vs {res['len_b']} (reb)")
    # --- RHYTHM: compare note onsets (frame gaps), tolerant ---
    reb_real = capture_real(out, dur)
    o_on, r_on = note_onset_frames(orig_real), note_onset_frames(reb_real)
    o_gaps = [o_on[i+1]-o_on[i] for i in range(len(o_on)-1)]
    r_gaps = [r_on[i+1]-r_on[i] for i in range(len(r_on)-1)]
    n = min(len(o_gaps), len(r_gaps))
    maxdiff = max((abs(o_gaps[i]-r_gaps[i]) for i in range(n)), default=0)
    # A 50Hz player can't align frame-exactly to BASIC's free-running FOR/NEXT
    # timing (+ siddump Trap-C bucket drift), so a few frames' slack is inherent
    # and within the duration_tol these tunes need.
    print(f"RHYTHM: {len(o_on)} onsets orig / {len(r_on)} reb; "
          f"max inter-onset frame-gap diff = {maxdiff} frames "
          f"({maxdiff/50.0:.2f}s; <=~5 = faithful within BASIC quantization)")

if __name__ == '__main__':
    main()
