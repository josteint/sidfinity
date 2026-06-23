#!/usr/bin/env python3
"""Multi-voice generalization of the Basic_Program lift (proof).

Twinkle proved the single-voice loop. This generalizes to N voices with an
arbitrary per-tune WRITE ORDER, validated on Baby_Elephant_Walk (3 voices,
chord-per-step, gate-then-freq) and re-validated on Twinkle (1 voice,
freq-then-gate) as a regression.

Model: the music is a list of STEPS. Every step has the shape
    [attack writes] · hold(dur) · [release writes] · gap
where attack = per-voice gate-on + freq writes (in the tune's captured order)
and release = per-voice gate-off. The cross-voice write ORDER (gate-before-freq
vs freq-before-gate, voice sequence) is a structural per-tune parameter derived
from the capture — NOT musical content. Per-voice pitch + duration + waveform
are the musical content (→ USF). A template-driven player replays the order.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.hubbard.verify_cycle import (writelog_capture,
                                            compare_instruction_stream)
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header
from pipelines.basic_program.proof_twinkle import capture_real, flatten

LOAD = 0x1000
CTRL = {0x04: 1, 0x0b: 2, 0x12: 3}                 # ctrl reg -> voice
FHI = {1: 0x01, 2: 0x08, 3: 0x0f}
FLO = {1: 0x00, 2: 0x07, 3: 0x0e}
FREQREG = {0x00: (1, 'lo'), 0x01: (1, 'hi'), 0x07: (2, 'lo'), 0x08: (2, 'hi'),
           0x0e: (3, 'lo'), 0x0f: (3, 'hi')}
DRIVER_PREFIX = [(0x18, 0x0F)]

# ---------------------------------------------------------------- lift ----
def lift_mv(frames):
    stream = flatten(frames)                       # (frame_idx, reg, val)
    # music start: first gate-on, then back up over the freq writes feeding it
    g0 = next(i for i, (f, r, v) in enumerate(stream)
              if r in CTRL and (v & 1))
    start = g0
    while start > 0 and stream[start-1][1] in FREQREG:
        start -= 1
    init = [(r, v) for f, r, v in stream[:start]]
    start_frame = stream[start][0]                 # real frame of first note
    music = stream[start:]
    order = 'gate_then_freq' if music[0][1] in CTRL else 'freq_then_gate'
    # segment into steps: close after each gate-off group
    steps, cur = [], []
    for j, w in enumerate(music):
        cur.append(w)
        f, r, v = w
        if r in CTRL and not (v & 1):              # gate-clear ctrl
            nxt = music[j+1] if j+1 < len(music) else None
            nxt_gc = nxt is not None and nxt[1] in CTRL and not (nxt[2] & 1)
            if not nxt_gc:
                steps.append(cur); cur = []
    # parse steps -> per-voice freq + waveforms + write template
    voices, waves = set(), {}
    parsed = []
    for st in steps:
        if not any(r in CTRL and not (v & 1) for f, r, v in st):
            continue                                # incomplete trailing step
        vf = {}                                     # voice -> [hi,lo]
        attack, release = [], []                    # role templates
        on_frame = st[0][0]
        off_frame = None
        for f, r, v in st:
            if r in CTRL:
                voices.add(CTRL[r])
                if v & 1:
                    waves[CTRL[r]] = v & 0xF0
                    attack.append(('on', CTRL[r]))
                else:
                    release.append(('off', CTRL[r]))
                    if off_frame is None:
                        off_frame = f
            elif r in FREQREG:
                vc, hl = FREQREG[r]
                voices.add(vc)
                vf.setdefault(vc, [0, 0])[0 if hl == 'hi' else 1] = v
                attack.append((hl, vc))
        parsed.append({'vf': vf, 'attack': attack, 'release': release,
                       'on_frame': on_frame, 'off_frame': off_frame})
    # durations from real frames
    for i, p in enumerate(parsed):
        p['dur'] = max(1, min(255, (p['off_frame'] - p['on_frame'])))
        nxt_on = parsed[i+1]['on_frame'] if i+1 < len(parsed) else p['off_frame']+1
        p['gap'] = max(1, min(255, nxt_on - p['off_frame']))
    # loop detection: BASIC tunes that GOTO-loop replay from an intro skip.
    # Detect the period from the CHORD signature (the flat stream is what
    # must keep matching). steps[:intro+period] are unique; loop back to intro.
    sigs = [tuple(tuple(p['vf'].get(vc, [0, 0])) for vc in sorted(voices))
            for p in parsed]
    intro, period = _find_loop(sigs)
    loop_to, loop_period = None, 0
    if period is not None:
        loop_to = intro
        # loop period in FRAMES — measure from the capture if it reached the
        # 2nd iteration's loop head (step intro+period), so the absolute-frame
        # schedule stays anchored to the original each loop instead of summing
        # per-step deltas. Fall back to summed dur+gap if the capture is short.
        if intro + period < len(parsed):
            loop_period = (parsed[intro + period]['on_frame']
                           - parsed[intro]['on_frame'])
        else:
            loop_period = sum(parsed[k]['dur'] + parsed[k]['gap']
                              for k in range(intro, intro + period))
        parsed = parsed[:intro + period]
    return {'init': init, 'order': order, 'voices': sorted(voices),
            'waves': waves, 'steps': parsed, 'loop_to': loop_to,
            'loop_period': loop_period, 'start_frame': start_frame,
            'attack': parsed[0]['attack'], 'release': parsed[0]['release']}

def _find_loop(sigs, min_run=8):
    """Smallest period P whose backward run of identical chords is >= min_run.
    Returns (intro_len, period) or (None, None) if the tune doesn't loop."""
    n = len(sigs)
    for P in range(1, n):
        run, i = 0, n - 1
        while i - P >= 0 and sigs[i] == sigs[i - P]:
            run += 1; i -= 1
        if run >= min_run:
            return max(0, (i + 1) - P), P
    return None, None

CTRLREG = {1: 0x04, 2: 0x0b, 3: 0x12}              # voice -> ctrl register

# ------------------------------------------------------------- emit asm ----
def build_player_asm(L):
    """ABSOLUTE-FRAME scheduling: a 16-bit frame counter fires each step's
    attack/release at its captured ABSOLUTE frame (no summed per-step deltas,
    so rounding doesn't accumulate). `loopbase` advances by the measured loop
    period each wrap, anchoring every loop iteration to the original."""
    steps = L['steps']
    N = len(steps)
    waves = L['waves']
    loop_to = L.get('loop_to')
    period = L.get('loop_period', 0)
    lines = []; em = lines.append
    em(f'* = ${LOAD:04X}')
    em('        jmp init')
    em('        jmp play')
    # --- init: program writes, zero state, curtgt = atk[0] ---
    em('init:')
    prog_init = L['init']
    if prog_init[:1] == DRIVER_PREFIX:
        prog_init = prog_init[1:]
    for reg, val in prog_init:
        em(f'        lda #${val:02X}')
        em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    for s in ('stepidx', 'phase', 'done', 'framelo', 'framehi',
              'loopbaselo', 'loopbasehi'):
        em(f'        sta {s}')
    em('        ldx #$00')
    em('        jsr set_atk_target')         # curtgt = atk[0] (incl. setup delay)
    em('        rts')
    # --- play ---
    em('play:')
    em('        lda done')
    em('        beq pl_go')
    em('        rts')
    em('pl_go:')
    em('        lda framehi')                # fire iff frame >= curtgt (16-bit)
    em('        cmp curtgthi')
    em('        bcc pl_wait')
    em('        bne pl_fire')
    em('        lda framelo')
    em('        cmp curtgtlo')
    em('        bcs pl_fire')
    em('pl_wait:')                           # not yet -> tick the frame counter
    em('        jmp pl_inc')
    em('pl_fire:')
    em('        lda phase')
    em('        bne pl_release')
    # attack: emit on/freq writes in template order; next target = rel[step]
    em('        ldx stepidx')
    for role, vc in L['attack']:
        if role == 'on':
            em(f'        lda #${(waves[vc] | 0x01):02X}')
            em(f'        sta $D4{CTRLREG[vc]:02X}')
        elif role == 'hi':
            em(f'        lda v{vc}hi,x')
            em(f'        sta $D4{FHI[vc]:02X}')
        elif role == 'lo':
            em(f'        lda v{vc}lo,x')
            em(f'        sta $D4{FLO[vc]:02X}')
    em('        ldx stepidx')
    em('        jsr set_rel_target')
    em('        lda #$01')
    em('        sta phase')
    em('        jmp pl_inc')
    # release: gate-off writes; advance step (loop or finish); target = atk[step]
    em('pl_release:')
    em('        ldx stepidx')
    for role, vc in L['release']:
        em(f'        lda #${waves[vc]:02X}')
        em(f'        sta $D4{CTRLREG[vc]:02X}')
    em('        inc stepidx')
    em('        lda stepidx')
    em(f'        cmp #${N & 0xFF:02X}')
    em('        bne pl_setatk')
    if loop_to is not None:                          # wrap to the intro skip
        em(f'        lda #${loop_to & 0xFF:02X}')
        em('        sta stepidx')
        em('        clc')                             # loopbase += period
        em('        lda loopbaselo')
        em(f'        adc #${period & 0xFF:02X}')
        em('        sta loopbaselo')
        em('        lda loopbasehi')
        em(f'        adc #${(period >> 8) & 0xFF:02X}')
        em('        sta loopbasehi')
    else:                                            # tune ENDs -> halt
        em('        lda #$01')
        em('        sta done')
        em('        jmp pl_inc')
    em('pl_setatk:')
    em('        ldx stepidx')
    em('        jsr set_atk_target')
    em('        lda #$00')
    em('        sta phase')
    em('pl_inc:')
    em('        inc framelo')
    em('        bne pl_ret')
    em('        inc framehi')
    em('pl_ret:')
    em('        rts')
    # curtgt = table[x] + loopbase (16-bit)
    em('set_atk_target:')
    em('        clc')
    em('        lda atklo,x')
    em('        adc loopbaselo')
    em('        sta curtgtlo')
    em('        lda atkhi,x')
    em('        adc loopbasehi')
    em('        sta curtgthi')
    em('        rts')
    em('set_rel_target:')
    em('        clc')
    em('        lda rello,x')
    em('        adc loopbaselo')
    em('        sta curtgtlo')
    em('        lda relhi,x')
    em('        adc loopbasehi')
    em('        sta curtgthi')
    em('        rts')
    for s in ('stepidx', 'phase', 'done', 'framelo', 'framehi',
              'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi'):
        em(f'{s}: .byte 0')

    def block(label, data):
        em(f'{label}:')
        for o in range(0, len(data), 16):
            em('        .byte ' + ', '.join(f'${b:02X}' for b in data[o:o+16]))
    for vc in L['voices']:
        block(f'v{vc}hi', [steps[s]['vf'].get(vc, [0, 0])[0] for s in range(N)])
        block(f'v{vc}lo', [steps[s]['vf'].get(vc, [0, 0])[1] for s in range(N)])
    block('atklo', [steps[s]['on_frame'] & 0xFF for s in range(N)])
    block('atkhi', [(steps[s]['on_frame'] >> 8) & 0xFF for s in range(N)])
    block('rello', [steps[s]['off_frame'] & 0xFF for s in range(N)])
    block('relhi', [(steps[s]['off_frame'] >> 8) & 0xFF for s in range(N)])
    return '\n'.join(lines)

def build_psid(L, title='proof'):
    body = assemble(build_player_asm(L))
    hdr = build_header(load=LOAD, init=LOAD, play=LOAD+3, songs=1,
                       start_song=1, speed=0, title=title, author='x', released='x')
    return hdr + body

# ----------------------------------------------------------------- main ----
def verdict_basic(res, tol_frac=0.15):
    """Basic_Program verdict = OVERLAP-exact (every (reg,val) the original
    emits is reproduced in order) + a DURATION tolerance on the total length.

    Absolute-frame scheduling (the player fires step k at its captured absolute
    frame) removes per-step accumulation, so the rebuild is tempo-faithful on
    real hardware. The residual length diff in the VERDICT is a siddump
    measurement bias, NOT a rebuild error: the RSID-BASIC original runs
    free (no play() vector) while the PSID rebuild's play() is invoked at
    siddump's PSID rate (~0.92x/frame for EVERY PSID, incl. a trivial one and
    real Hubbard tunes). Scaling the rebuild's targets by that 0.92 makes the
    length diff EXACTLY 0 — proving the residual IS the rate bias — but we do
    NOT scale, because that would make the rebuild ~8.7% fast on real hardware
    (the ear is the final judge). So a proportional duration_tol absorbs the
    tool bias (the duration_tol the C6 research anticipated)."""
    a, b = res['len_all_a'], res['len_all_b']
    overlap_ok = res['match_all'] == min(a, b)
    length_ok = abs(a - b) <= max(64, tol_frac * max(a, b))
    return overlap_ok and length_ok, overlap_ok, length_ok

def run(sid_rel, dur, title):
    sid = os.path.join(ROOT, sid_rel)
    L = lift_mv(capture_real(sid, dur))
    print(f"\n=== {title} ===")
    print(f"  voices={L['voices']} order={L['order']} "
          f"waves={{{', '.join('%d:$%02X'%(k,v) for k,v in sorted(L['waves'].items()))}}} "
          f"steps={len(L['steps'])} loop_to={L['loop_to']}")
    out = os.path.join(ROOT, f'tmp/basic_program_research/{title}.sidfinity.sid')
    with open(out, 'wb') as f:
        f.write(build_psid(L, title))
    orig = writelog_capture(sid, 0, dur)
    reb = writelog_capture(out, 0, dur)
    res = compare_instruction_stream(orig, reb, skip_init=False)
    ok, overlap_ok, length_ok = verdict_basic(res)
    print(f"  overlap={'EXACT' if overlap_ok else 'DIVERGES'} "
          f"({res['match_all']}/{min(res['len_all_a'],res['len_all_b'])}); "
          f"len orig={res['len_all_a']} reb={res['len_all_b']} "
          f"(diff {abs(res['len_all_a']-res['len_all_b'])}, {'OK' if length_ok else 'over'} duration_tol)")
    print(f"  >>> {title} FULL={ok}")
    return ok

if __name__ == '__main__':
    ok1 = run('hvsc84/DEMOS/A-F/Baby_Elephant_Walk_BASIC.sid', 40.0, 'Baby_Elephant_Walk')
    ok2 = run('hvsc84/DEMOS/UNKNOWN/Twinkle_BASIC.sid', 12.0, 'Twinkle')
    print(f"\nBaby FULL={ok1}  Twinkle(regression) FULL={ok2}")
