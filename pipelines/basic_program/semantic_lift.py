#!/usr/bin/env python3
"""Semantic richer lift for Basic_Program (writelog -> per-step register model).

The freq+gate lift covers only ~10% — real BASIC note loops poke a richer, but
still MUSICAL, per-step set: freq (note), ctrl (waveform+gate), AD/SR (envelope),
$D418 (dynamics), PW/filter (timbre). This lift captures the FULL per-step write
template and classifies each register CONST (same value every step = instrument /
waveform — factored out) vs PERSTEP (varies = note / dynamics). That keeps it
principled (musical content, not a raw write dump): CONST regs are the instrument,
PERSTEP freq are the notes, PERSTEP $D418 is dynamics.

Ported from gt2_pipeline/regtrace_to_usf.py BUT on the --writelog ordered stream
(NOT the old per-frame snapshots, which lose within-frame write ORDER — and the
exact (reg,val) ORDER is what the flat verdict checks).

Segmentation: the writelog over real frames is bursts of writes ("active runs")
separated by silent holds (the FOR/NEXT busy-waits). A step = an attack run (note
start, has a gate-on or freq) + an optional release run (pure gate-off). Legato
steps have no release run (gate set once, freq-only changes).
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.basic_program.proof_twinkle import capture_real, flatten

CTRL = {0x04, 0x0b, 0x12}
FREQ = {0x00, 0x01, 0x07, 0x08, 0x0e, 0x0f}
DRIVER_PREFIX = [(0x18, 0x0F)]

def _music_start(stream):
    """Index of the first music write: first gate-on, backed up over its freq."""
    try:
        g0 = next(i for i, (f, r, v) in enumerate(stream) if r in CTRL and (v & 1))
    except StopIteration:
        return None
    s = g0
    while s > 0 and stream[s-1][1] in FREQ:
        s -= 1
    return s

def segment(frames):
    """-> (init, steps, start_frame, legato). Steps carry the FULL ordered writes.

    GATED tunes: a step ends after each gate-off GROUP (a maximal run of gate-clear
    ctrl writes); the step splits into attack (everything before that trailing
    group) + release (the group). LEGATO tunes (no per-note gate-off): a step
    boundary is each gate-on / freq-change to a new note; no release."""
    stream = flatten(frames)
    start = _music_start(stream)
    if start is None:
        return [(r, v) for f, r, v in stream], [], 0, False
    init = [(r, v) for f, r, v in stream[:start]]
    start_frame = stream[start][0]
    music = stream[start:]
    n_off = sum(1 for f, r, v in music if r in CTRL and not (v & 1))
    legato = n_off < max(3, len(music) // 200)        # ~no per-note gate-off
    raw = []                                          # list of step write-lists [(f,r,v)..]
    if not legato:
        cur = []
        for idx, (f, r, v) in enumerate(music):
            cur.append((f, r, v))
            if r in CTRL and not (v & 1):
                nxt = music[idx+1] if idx + 1 < len(music) else None
                nxt_gc = nxt is not None and nxt[1] in CTRL and not (nxt[2] & 1)
                if not nxt_gc:
                    raw.append(cur); cur = []
        # drop a trailing incomplete step (no gate-off group)
    else:
        # split at each gate-on (or freq-hi after a non-freq write) = new note
        cur = []
        for idx, (f, r, v) in enumerate(music):
            if cur and ((r in CTRL and (v & 1)) or
                        (r in FREQ and cur and cur[-1][1] not in FREQ)):
                raw.append(cur); cur = []
            cur.append((f, r, v))
        if cur:
            raw.append(cur)
    steps = []
    for st in raw:
        # release = trailing maximal gate-clear ctrl group (empty for legato)
        ri = len(st)
        while ri > 0 and st[ri-1][1] in CTRL and not (st[ri-1][2] & 1):
            ri -= 1
        atk, rel = st[:ri], st[ri:]
        if not atk:
            continue
        steps.append({'attack': [(r, v) for f, r, v in atk], 'on_frame': atk[0][0],
                      'release': [(r, v) for f, r, v in rel] if rel else None,
                      'off_frame': rel[0][0] if rel else None, 'next': None})
    for k in range(len(steps) - 1):
        steps[k]['next'] = steps[k+1]['on_frame']
    return init, steps, start_frame, legato

def derive_template(seqs):
    """seqs = list of per-step write lists (each [(reg,val)..], same length+regs).
    -> template [(reg, 'const', val) | (reg, 'perstep', None)] + per-step value
    arrays for the perstep slots. Returns None if the register sequences aren't
    consistent across steps (variable template — not handled in this pass)."""
    if not seqs:
        return None, []
    regseq = [r for r, v in seqs[0]]
    for s in seqs:
        if [r for r, v in s] != regseq:
            return None, []                            # inconsistent template
    template = []
    perstep_slots = []                                 # indices into the write list
    for idx, reg in enumerate(regseq):
        vals = [s[idx][1] for s in seqs]
        if len(set(vals)) == 1:
            template.append((reg, 'const', vals[0]))
        else:
            template.append((reg, 'perstep', None))
            perstep_slots.append(idx)
    return template, perstep_slots

def _modal(seqs):
    from collections import Counter
    return Counter(tuple(r for r, v in s) for s in seqs).most_common(1)[0][0]

def build_model(sid, dur):
    """Lift to a build-ready model, or {'unsupported': reason}. Handles the
    CONSISTENT-template case: every step writes the same registers in the same
    order (each reg const or perstep). Variable templates (rests / legato) are
    deferred."""
    from pipelines.basic_program.proof_multivoice import measure_rho, _find_loop
    import struct
    frames = capture_real(sid, dur)
    init, steps, start_frame, legato = segment(frames)
    if legato:
        return {'unsupported': 'legato'}
    if len(steps) < 2:
        return {'unsupported': 'too_few_steps'}
    # drop trailing steps that don't match the modal templates (capture cut-off)
    am, rm = _modal([s['attack'] for s in steps]), _modal([s['release'] for s in steps if s['release']])
    def ok(s):
        return (tuple(r for r, v in s['attack']) == am and s['release'] is not None
                and tuple(r for r, v in s['release']) == rm)
    while steps and not ok(steps[-1]):
        steps.pop()
    if len(steps) < 2:
        return {'unsupported': 'too_few_after_trim'}
    if not all(ok(s) for s in steps):
        return {'unsupported': 'variable_template'}    # mid-song variation (rests)
    atk_t, atk_ps = derive_template([s['attack'] for s in steps])
    rel_t, rel_ps = derive_template([s['release'] for s in steps])
    if atk_t is None or rel_t is None:
        return {'unsupported': 'template_derive'}
    # frames + durations + loop
    clk = {1: 'PAL', 2: 'NTSC', 3: 'PAL'}.get((struct.unpack('>H', open(sid,'rb').read()[118:120])[0] >> 2) & 3, 'PAL')
    sigs = [tuple(s['attack']) for s in steps]
    intro, period = _find_loop(sigs)
    loop_to, loop_period = None, 0
    if period is not None:
        loop_to = intro
        loop_period = (steps[intro+period]['on_frame'] - steps[intro]['on_frame']) \
            if intro + period < len(steps) else \
            (steps[-1]['next'] or steps[-1]['on_frame']) - steps[intro]['on_frame']
        steps = steps[:intro + period]
    rho = measure_rho(clk)
    for s in steps:
        s['on_frame'] = round(s['on_frame'] * rho)
        s['off_frame'] = round(s['off_frame'] * rho)
    loop_period = round(loop_period * rho)
    return {'init': init, 'steps': steps, 'atk_template': atk_t, 'atk_ps': atk_ps,
            'rel_template': rel_t, 'rel_ps': rel_ps, 'loop_to': loop_to,
            'loop_period': loop_period, 'clock': clk, 'rho': rho}

def analyze(sid, dur):  # debug view
    frames = capture_real(sid, dur)
    init, steps, start_frame, legato = segment(frames)
    atk_t, _ = derive_template([s['attack'] for s in steps]) if steps else (None, [])
    rel_seqs = [s['release'] for s in steps if s['release'] is not None]
    rel_t, _ = derive_template(rel_seqs) if rel_seqs else ([], [])
    return {'n_steps': len(steps), 'atk_template': atk_t, 'rel_template': rel_t, 'legato': legato}

def _fmt(t):
    if t is None: return "INCONSISTENT"
    return " ".join(f"{r:02X}={'PS' if k=='perstep' else f'{v:02X}'}" for r, k, v in t)

# ------------------------------------------------------------- emit asm ----
from pipelines.basic_program.proof_multivoice import SP, LOAD
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header

def build_player(model):
    """Template-driven player: per step emit the attack template (const values
    inline = instrument/waveform; perstep values from the packed record = notes/
    dynamics) at the step's absolute frame, hold, emit the release template.
    Reuses absolute-frame scheduling + rho + 16-bit step pointer + loop."""
    init, atk_t, rel_t = model['init'], model['atk_template'], model['rel_template']
    steps = model['steps']; N = len(steps)
    natk = len(model['atk_ps']); nrel = len(model['rel_ps'])
    stride = 4 + natk + nrel
    loop_to, period = model['loop_to'], model['loop_period']
    L = []; em = L.append
    em(f'* = ${LOAD:04X}'); em('        jmp init'); em('        jmp play')
    em('init:')
    pi = init[1:] if init[:1] == DRIVER_PREFIX else init
    for reg, val in pi:
        em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    for s in ('phase', 'done', 'framelo', 'framehi', 'loopbaselo', 'loopbasehi'):
        em(f'        sta {s}')
    em('        lda #<steprecs'); em('        sta splo'); em(f'        sta {SP}')
    em('        lda #>steprecs'); em('        sta sphi'); em(f'        sta {SP}+1')
    em('        jsr set_atk_target'); em('        rts')
    em('play:'); em('        lda done'); em('        beq pl_load'); em('        rts')
    em('pl_load:')
    em('        lda splo'); em(f'        sta {SP}'); em('        lda sphi'); em(f'        sta {SP}+1')
    em('        lda framehi'); em('        cmp curtgthi'); em('        bcc pl_wait'); em('        bne pl_fire')
    em('        lda framelo'); em('        cmp curtgtlo'); em('        bcs pl_fire')
    em('pl_wait:'); em('        jmp pl_inc')
    em('pl_fire:'); em('        lda phase'); em('        beq pl_attack'); em('        jmp pl_release')
    em('pl_attack:')
    slot = 0
    for reg, kind, val in atk_t:
        if kind == 'const':
            em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
        else:
            em(f'        ldy #${4+slot:02X}'); em(f'        lda ({SP}),y'); em(f'        sta $D4{reg:02X}'); slot += 1
    em('        jsr set_rel_target'); em('        lda #$01'); em('        sta phase'); em('        jmp pl_inc')
    em('pl_release:')
    slot = 0
    for reg, kind, val in rel_t:
        if kind == 'const':
            em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
        else:
            em(f'        ldy #${4+natk+slot:02X}'); em(f'        lda ({SP}),y'); em(f'        sta $D4{reg:02X}'); slot += 1
    em('        clc'); em(f'        lda {SP}'); em(f'        adc #${stride:02X}'); em(f'        sta {SP}')
    em(f'        lda {SP}+1'); em('        adc #$00'); em(f'        sta {SP}+1')
    eoff = N * stride
    em(f'        lda {SP}'); em(f'        cmp #<(steprecs+{eoff})'); em('        bne pl_setatk')
    em(f'        lda {SP}+1'); em(f'        cmp #>(steprecs+{eoff})'); em('        bne pl_setatk')
    if loop_to is not None:
        loff = loop_to * stride
        em(f'        lda #<(steprecs+{loff})'); em(f'        sta {SP}')
        em(f'        lda #>(steprecs+{loff})'); em(f'        sta {SP}+1')
        em('        clc'); em('        lda loopbaselo'); em(f'        adc #${period&0xFF:02X}'); em('        sta loopbaselo')
        em('        lda loopbasehi'); em(f'        adc #${(period>>8)&0xFF:02X}'); em('        sta loopbasehi')
    else:
        em('        lda #$01'); em('        sta done'); em('        jmp pl_inc')
    em('pl_setatk:'); em('        jsr set_atk_target'); em('        lda #$00'); em('        sta phase')
    em('pl_inc:')
    em(f'        lda {SP}'); em('        sta splo'); em(f'        lda {SP}+1'); em('        sta sphi')
    em('        inc framelo'); em('        bne pl_ret'); em('        inc framehi'); em('pl_ret:'); em('        rts')
    em('set_atk_target:'); em('        clc')
    em('        ldy #$00'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$01'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    em('set_rel_target:'); em('        clc')
    em('        ldy #$02'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$03'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    for s in ('splo', 'sphi', 'phase', 'done', 'framelo', 'framehi',
              'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi'):
        em(f'{s}: .byte 0')
    em('steprecs:')
    aps, rps = model['atk_ps'], model['rel_ps']
    for s in steps:
        rec = [s['on_frame'] & 0xFF, (s['on_frame'] >> 8) & 0xFF,
               s['off_frame'] & 0xFF, (s['off_frame'] >> 8) & 0xFF]
        rec += [s['attack'][i][1] & 0xFF for i in aps]
        rec += [s['release'][i][1] & 0xFF for i in rps]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(L)

def build_psid(model, title='probe'):
    body = assemble(build_player(model))
    return build_header(load=LOAD, init=LOAD, play=LOAD+3, songs=1, start_song=1,
                        speed=0, title=title, author='x', released='x') + body

def verify(sid_rel, dur=20.0, title='probe'):
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
    from pipelines.basic_program.proof_multivoice import verdict_basic
    sid = os.path.join(ROOT, 'hvsc84', sid_rel)
    m = build_model(sid, dur)
    if 'unsupported' in m:
        return {'status': 'unsupported:' + m['unsupported']}
    out = os.path.join(ROOT, 'tmp/basic_program_research/sem.sid')
    with open(out, 'wb') as f:
        f.write(build_psid(m, title))
    r = compare_instruction_stream(writelog_capture(sid, 0, dur),
                                   writelog_capture(out, 0, dur), skip_init=False)
    ok, ov, ln = verdict_basic(r)
    return {'status': 'FULL' if ok else ('overlap_diverge' if not ov else 'length_fail'),
            'match': r['match_all'], 'len_a': r['len_all_a'], 'len_b': r['len_all_b']}

if __name__ == '__main__':
    for rel in ['DEMOS/UNKNOWN/Twinkle_BASIC.sid',
                'DEMOS/A-F/Baby_Elephant_Walk_BASIC.sid',
                'DEMOS/A-F/Deutschlandlied_BASIC.sid',
                'DEMOS/A-F/American_Flag_BASIC.sid']:
        print(rel.split('/')[-1], '->', verify(rel))
