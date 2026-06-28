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
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.hubbard.verify_cycle import (writelog_capture,
                                            compare_instruction_stream)
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header
from pipelines.basic_program.proof_twinkle import capture_real, flatten

LOAD = 0x1000
CTRL = {0x04: 1, 0x0b: 2, 0x12: 3}                 # ctrl reg -> voice

# --- siddump frame / play-period unit conversion (rho) ----------------------
# The original is RSID (free-running, CPU-cycle paced); the rebuild is a PSID
# whose play() the C64 fires at the true VIC frame rate (PAL 19656 cyc = 50Hz).
# But siddump steps the emulator via engine.play(cyclesPerFrame) where
# cyclesPerFrame counts EVENT-SCHEDULER ticks, and one tick < 1 CPU cycle — so a
# siddump "frame" only advances ~18000 CPU cycles, NOT one play period. So an
# onset measured in siddump-frame units must be scaled by rho = (CPU cycles per
# siddump frame)/(play period) = plays-per-siddump-frame to express it in the
# player's play-period clock. rho ~0.919 (PAL); measured per-clock so it tracks
# NTSC too. With it, the rebuild's writes land at the original's exact cycles
# (gate-on absolute-cycle ratio -> 1.000), i.e. correct 50Hz, no tempo error.
_RHO_CACHE = {}
def measure_rho(clock='PAL', sid_model=6581):
    if clock in _RHO_CACHE:
        return _RHO_CACHE[clock]
    import subprocess, tempfile
    clk = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(clock, 1)
    flags = (clk << 2) | ({6581: 1, 8580: 2}.get(sid_model, 1) << 4)
    asm = "* = $1000\n  jmp i\n  jmp p\ni:\n rts\np:\n rts\n"
    sid = build_header(load=0x1000, init=0x1000, play=0x1003, songs=1,
                       start_song=1, speed=0, title='r', author='r',
                       released='r', flags=flags) + assemble(asm)
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(sid); path = f.name
    out = subprocess.run([os.path.join(ROOT, 'tools/siddump'), path,
                          '--memwatch', 'D404', '--duration', '20'],
                         capture_output=True, text=True).stdout
    plays = frames = 0
    for ln in out.splitlines():
        m = re.search(r'\|P:(\d+)', ln)
        if m:
            plays += int(m.group(1)); frames += 1
    os.unlink(path)
    rho = plays / frames if frames else 1.0
    _RHO_CACHE[clock] = rho
    return rho
FHI = {1: 0x01, 2: 0x08, 3: 0x0f}
FLO = {1: 0x00, 2: 0x07, 3: 0x0e}
FREQREG = {0x00: (1, 'lo'), 0x01: (1, 'hi'), 0x07: (2, 'lo'), 0x08: (2, 'hi'),
           0x0e: (3, 'lo'), 0x0f: (3, 'hi')}
DRIVER_PREFIX = [(0x18, 0x0F)]

# ---------------------------------------------------------------- lift ----
def lift_mv(frames, clock='PAL'):
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
    # convert absolute frame targets from siddump-frame units to the player's
    # play-period clock (see measure_rho) so the rebuild's writes land at the
    # original's exact emulated cycles (correct 50Hz, no tempo drift).
    rho = measure_rho(clock)
    for p in parsed:
        p['on_frame'] = round(p['on_frame'] * rho)
        p['off_frame'] = round(p['off_frame'] * rho)
    loop_period = round(loop_period * rho)
    return {'init': init, 'order': order, 'voices': sorted(voices),
            'waves': waves, 'steps': parsed, 'loop_to': loop_to,
            'loop_period': loop_period, 'start_frame': start_frame, 'rho': rho,
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
SP = '$FB'                                          # ZP step-record pointer (lo/hi)

def build_player_asm(L):
    """ABSOLUTE-FRAME scheduling: a 16-bit frame counter fires each step's
    attack/release at its captured ABSOLUTE frame (no summed per-step deltas);
    `loopbase` advances by the measured loop period each wrap.

    Per-step data is packed into fixed-stride records walked by a 16-bit step
    pointer (no 8-bit step limit). The pointer lives in persistent RAM (`splo`/
    `sphi`) and is copied to ZP $FB/$FC per play-call for `(zp),y` indexing — the
    KERNAL IRQ runs between play() calls, not during, so $FB/$FC are safe scratch.
    Record layout per step: [atk_lo, atk_hi, rel_lo, rel_hi, (v_hi, v_lo)*nvoices]."""
    steps = L['steps']
    N = len(steps)
    waves = L['waves']
    voices = L['voices']
    loop_to = L.get('loop_to')
    period = L.get('loop_period', 0)
    stride = 4 + 2 * len(voices)
    vidx = {vc: i for i, vc in enumerate(voices)}    # voice -> record slot
    lines = []; em = lines.append
    em(f'* = ${LOAD:04X}')
    em('        jmp init')
    em('        jmp play')
    # --- init: program writes, zero state, sp=steprecs, curtgt = atk[0] ---
    em('init:')
    prog_init = L['init']
    if prog_init[:1] == DRIVER_PREFIX:
        prog_init = prog_init[1:]
    for reg, val in prog_init:
        em(f'        lda #${val:02X}')
        em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    for s in ('phase', 'done', 'framelo', 'framehi', 'loopbaselo', 'loopbasehi'):
        em(f'        sta {s}')
    em('        lda #<steprecs')
    em(f'        sta splo')
    em(f'        sta {SP}')
    em('        lda #>steprecs')
    em(f'        sta sphi')
    em(f'        sta {SP}+1')
    em('        jsr set_atk_target')         # curtgt = atk[0] (incl. setup delay)
    em('        rts')
    # --- play ---
    em('play:')
    em('        lda done')
    em('        beq pl_load')
    em('        rts')
    em('pl_load:')                           # RAM step-pointer -> ZP scratch
    em(f'        lda splo')
    em(f'        sta {SP}')
    em(f'        lda sphi')
    em(f'        sta {SP}+1')
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
    em('        beq pl_attack')              # trampoline: attack code is long
    em('        jmp pl_release')
    # attack: emit on/freq writes in template order; next target = rel[step]
    em('pl_attack:')
    for role, vc in L['attack']:
        if role == 'on':
            em(f'        lda #${(waves[vc] | 0x01):02X}')
            em(f'        sta $D4{CTRLREG[vc]:02X}')
        elif role in ('hi', 'lo'):
            off = 4 + 2 * vidx[vc] + (0 if role == 'hi' else 1)
            reg = FHI[vc] if role == 'hi' else FLO[vc]
            em(f'        ldy #${off:02X}')
            em(f'        lda ({SP}),y')
            em(f'        sta $D4{reg:02X}')
    em('        jsr set_rel_target')
    em('        lda #$01')
    em('        sta phase')
    em('        jmp pl_inc')
    # release: gate-off writes; advance sp by stride (loop or finish)
    em('pl_release:')
    for role, vc in L['release']:
        em(f'        lda #${waves[vc]:02X}')
        em(f'        sta $D4{CTRLREG[vc]:02X}')
    em('        clc')                                 # sp += stride
    em(f'        lda {SP}')
    em(f'        adc #${stride:02X}')
    em(f'        sta {SP}')
    em(f'        lda {SP}+1')
    em('        adc #$00')
    em(f'        sta {SP}+1')
    end_off = N * stride                              # sp == steprecs+end_off -> wrapped
    em(f'        lda {SP}')
    em(f'        cmp #<(steprecs+{end_off})')
    em('        bne pl_setatk')
    em(f'        lda {SP}+1')
    em(f'        cmp #>(steprecs+{end_off})')
    em('        bne pl_setatk')
    if loop_to is not None:                           # wrap to the intro skip
        loop_off = loop_to * stride
        em(f'        lda #<(steprecs+{loop_off})')
        em(f'        sta {SP}')
        em(f'        lda #>(steprecs+{loop_off})')
        em(f'        sta {SP}+1')
        em('        clc')                             # loopbase += period
        em('        lda loopbaselo')
        em(f'        adc #${period & 0xFF:02X}')
        em('        sta loopbaselo')
        em('        lda loopbasehi')
        em(f'        adc #${(period >> 8) & 0xFF:02X}')
        em('        sta loopbasehi')
    else:                                             # tune ENDs -> halt
        em('        lda #$01')
        em('        sta done')
        em('        jmp pl_inc')
    em('pl_setatk:')
    em('        jsr set_atk_target')
    em('        lda #$00')
    em('        sta phase')
    em('pl_inc:')                                     # ZP step-pointer -> RAM, tick frame
    em(f'        lda {SP}')
    em(f'        sta splo')
    em(f'        lda {SP}+1')
    em(f'        sta sphi')
    em('        inc framelo')
    em('        bne pl_ret')
    em('        inc framehi')
    em('pl_ret:')
    em('        rts')
    # curtgt = (sp)[0,1] + loopbase  (attack target, 16-bit)
    em('set_atk_target:')
    em('        clc')
    em('        ldy #$00')
    em(f'        lda ({SP}),y')
    em('        adc loopbaselo')
    em('        sta curtgtlo')
    em('        ldy #$01')
    em(f'        lda ({SP}),y')
    em('        adc loopbasehi')
    em('        sta curtgthi')
    em('        rts')
    # curtgt = (sp)[2,3] + loopbase  (release target)
    em('set_rel_target:')
    em('        clc')
    em('        ldy #$02')
    em(f'        lda ({SP}),y')
    em('        adc loopbaselo')
    em('        sta curtgtlo')
    em('        ldy #$03')
    em(f'        lda ({SP}),y')
    em('        adc loopbasehi')
    em('        sta curtgthi')
    em('        rts')
    for s in ('splo', 'sphi', 'phase', 'done', 'framelo', 'framehi',
              'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi'):
        em(f'{s}: .byte 0')
    # --- packed per-step records ---
    em('steprecs:')
    for k in range(N):
        rec = [steps[k]['on_frame'] & 0xFF, (steps[k]['on_frame'] >> 8) & 0xFF,
               steps[k]['off_frame'] & 0xFF, (steps[k]['off_frame'] >> 8) & 0xFF]
        for vc in voices:
            hi, lo = steps[k]['vf'].get(vc, [0, 0])
            rec += [hi & 0xFF, lo & 0xFF]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(lines)

def build_psid(L, title='proof'):
    body = assemble(build_player_asm(L))
    hdr = build_header(load=LOAD, init=LOAD, play=LOAD+3, songs=1,
                       start_song=1, speed=0, title=title, author='x', released='x')
    return hdr + body

# ----------------------------------------------------------------- main ----
def verdict_basic(res, tol=64):
    """Basic_Program verdict = OVERLAP-exact (every (reg,val) the original emits
    is reproduced in order) + a tight length tolerance (Hubbard's |len|<=64).

    Absolute-frame scheduling (fire step k at its captured frame) + the rho unit
    conversion (siddump-frame -> play-period clock, see measure_rho) make the
    rebuild's writes land at the original's EXACT emulated cycles, so the length
    matches to ~0 (no rate drift). The rebuild plays at the true VIC frame rate
    (50Hz PAL); there is no emulation-vs-hardware difference — rho only corrects
    that siddump's engine.play(cyclesPerFrame) advances cyclesPerFrame
    event-scheduler ticks (~18000 CPU cycles), not one 19656-cycle play period.

    A LOOPING tune whose rebuild came up short in this fixed window (it would emit
    the rest given more frames) is handled by `_attempt_model`'s extend-and-verify
    pass, NOT by loosening this tolerance — see there."""
    a, b = res['len_all_a'], res['len_all_b']
    overlap_ok = res['match_all'] == min(a, b)
    length_ok = abs(a - b) <= tol
    return overlap_ok and length_ok, overlap_ok, length_ok

def run(sid_rel, dur, title):
    import json, subprocess
    sid = os.path.join(ROOT, sid_rel)
    hdr = json.loads(subprocess.run([os.path.join(ROOT, 'tools/siddump'), sid,
                     '--duration', '1'], capture_output=True, text=True
                     ).stdout.splitlines()[0])
    clock = hdr['clock']
    L = lift_mv(capture_real(sid, dur), clock=clock)
    print(f"\n=== {title} ===")
    print(f"  voices={L['voices']} order={L['order']} clock={clock} rho={L['rho']:.4f} "
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
