#!/usr/bin/env python3
"""SID -> USF -> SID round-trip for Basic_Program (clean perstep=freq members).

The semantic model splits cleanly for the bulk of FULL members (85% are
perstep=freq only): pitch / rhythm / timbre / tuning are MUSICAL and map to real
USF v2 (instrument + freq_table + per-voice NoteRows, rests = silent voices); the
only non-musical part is the per-tune WRITE MODEL (which registers, in what order,
gate const values, init, loop), which USF v2's scalar-only `params {}` carries as
packed ints (one per template entry: reg<<16 | kind<<8 | val; kind 0=const,
1=perstep-freq-from-notes). build_through_usf reconstructs the model from the .usf
and reproduces the exact writelog.
"""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from src.usf import (UsfFile, PsidMeta, Params, InitState, InitSid, Instrument,
                     MusicSubtune, VoiceBlock, Pattern, NoteRow, Orderlist,
                     Pitch, InstrumentRef, write_file, parse_file)
from pipelines.basic_program.semantic_lift import build_model, build_psid, FREQ as _F
from pipelines.basic_program import semantic_lift as S

FREQ = {0x00, 0x01, 0x07, 0x08, 0x0e, 0x0f}
FHI = {1: 0x01, 2: 0x08, 3: 0x0f}; FLO = {1: 0x00, 2: 0x07, 3: 0x0e}
VOICE_OF = {0x00: 1, 0x01: 1, 0x07: 2, 0x08: 2, 0x0e: 3, 0x0f: 3}
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def is_clean(model):
    """True iff every perstep register is a freq register (pitch-only variation)."""
    for tmpl in (model['atk_template'], model['rel_template']):
        for ent in tmpl:
            if ent[1] == 'perstep' and ent[0] not in FREQ:
                return False
    return True

def _t4(ent):                                          # normalize 3/4-tuple template entry
    return ent if len(ent) == 4 else (ent[0], ent[1], ent[2], VOICE_OF.get(ent[0]))

def _note_index(freq16):
    f = freq16 * 985248.0 / 16777216.0
    midi = round(12 * math.log2(f / 440.0)) + 69 if f > 0 else 0
    octv = min(7, max(0, midi // 12 - 1))              # clamp to the freq_table range (0-7)
    semi = midi % 12
    return ((octv << 4) | semi), NAMES[semi], octv

def _slot_pitch(slot):                                 # freq_table slot -> (name, octave)
    return NAMES[slot & 0xF], (slot >> 4) & 0x7

def _assign_slots(freqs):
    """Lossless freq16 -> freq_table-slot map. Each distinct freq lands at its
    nearest equal-tempered slot (so note names stay musically meaningful), and
    collisions linear-probe to the next free valid slot (semitone<12, octave<8).
    The freq_table is per-tune content (Rule 2) so a per-tune alphabet is exact.
    Returns None if the tune has > the 96 usable slots (glide/vibrato — deferred)."""
    if len(freqs) > 96:
        return None
    slot = {}; taken = set()
    for f in sorted(freqs):
        s = _note_index(f)[0]
        probes = 0
        while s in taken or (s & 0xF) >= 12:
            s += 1
            if s > 0x7B:
                s = 0
            probes += 1
            if probes > 128:
                return None
        slot[f] = s; taken.add(s)
    return slot

# --------------------------------------------------------- model -> usf ----
def model_to_usf(model, title='bp'):
    atk = [_t4(e) for e in model['atk_template']]
    rel = [_t4(e) for e in model['rel_template']]
    voices = sorted({v for e in atk + rel if (v := e[3])})
    steps = model['steps']
    # freq value per (voice, step) from the step's attack writes; None = rest
    def vfreq(s, vc):
        d = dict(s['attack']); hi, lo = FHI[vc], FLO[vc]
        if hi in d and lo in d:
            return (d[hi] << 8) | d[lo]
        return None
    # per-tune lossless freq alphabet (distinct freq -> unique freq_table slot)
    allfreqs = {fq for s in steps for vc in voices if (fq := vfreq(s, vc)) is not None}
    slotmap = _assign_slots(allfreqs)
    if slotmap is None:
        raise ValueError('too_many_pitches')
    # build per-tune freq table (slot -> exact bytes) + per-voice rows
    gated = len(rel) > 0
    ftab = bytearray(256)
    vrows = {vc: [] for vc in voices}
    # median delta as the last step's fallback (its real duration is the loop wrap)
    deltas = [steps[k+1]['on_frame'] - steps[k]['on_frame'] for k in range(len(steps)-1)]
    med = sorted(deltas)[len(deltas)//2] if deltas else 1
    for k, s in enumerate(steps):                      # gated: note(hold)+rest(gap); legato: note(step)
        on = s['on_frame']; off = s['off_frame']
        nxt = steps[k+1]['on_frame'] if k + 1 < len(steps) else on + med
        hold = max(1, (off - on)) if (gated and off is not None) else max(1, nxt - on)
        gap = max(1, nxt - off) if (gated and off is not None) else 1
        for vc in voices:
            f = vfreq(s, vc)
            if f is None:
                vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=hold))
            else:
                slot = slotmap[f]; nm, octv = _slot_pitch(slot)
                ftab[slot] = (f >> 8) & 0xFF; ftab[128 + slot] = f & 0xFF
                vrows[vc].append(NoteRow(pitch=Pitch(name=nm, octave=octv),
                                         duration=hold, instr=InstrumentRef(id=vc)))
            if gated:
                vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=gap))
    # instruments (musical view): waveform from a voice's gate-on const ctrl
    instrs = []
    for vc in voices:
        wave = next((e[2] for e in atk if e[0] == {1:4,2:0xb,3:0x12}[vc] and e[1]=='const'), 0x10)
        instrs.append(Instrument(id=vc, waveform=[wave & 0xF0], adsr=(0, 0)))
    vblocks = []
    for vc in (1, 2, 3):
        if vc in voices:
            vblocks.append(VoiceBlock(id=vc,
                orderlist=Orderlist(entries=[vc],
                    loop_to=(0 if model['loop_to'] is not None else None),
                    stop=(model['loop_to'] is None)),
                patterns=[Pattern(id=vc, length=sum(r.duration for r in vrows[vc]),
                                  rows=vrows[vc])]))
        else:
            vblocks.append(VoiceBlock(id=vc, orderlist=Orderlist(stop=True)))
    sub = MusicSubtune(id=0, tempo=1, voices=vblocks)
    # structural write-model -> packed scalar params
    fields = {'bp': 1, 'bp_legato': int(model['legato']),
              'bp_start_frame': steps[0]['on_frame'] if steps else 0,
              'bp_loop_to': model['loop_to'] if model['loop_to'] is not None else -1,
              'bp_loop_period': model['loop_period'],
              'bp_rho_milli': round(model['rho'] * 1000),
              'bp_atk_n': len(atk), 'bp_rel_n': len(rel),
              'bp_init_n': len(model['init'])}
    for i, (reg, val) in enumerate(model['init']):
        fields[f'bp_init{i}'] = (reg << 8) | (val & 0xFF)
    for i, e in enumerate(atk):
        k = 0 if e[1] == 'const' else 1
        fields[f'bp_atk{i}'] = (e[0] << 16) | (k << 8) | ((e[2] or 0) & 0xFF)
    for i, e in enumerate(rel):
        k = 0 if e[1] == 'const' else 1
        fields[f'bp_rel{i}'] = (e[0] << 16) | (k << 8) | ((e[2] or 0) & 0xFF)
    return UsfFile(
        psid=PsidMeta(title=title, author='basic_program', released='sidfinity',
                      clock=model['clock'], sid=6581, start_song=1, speed=0),
        params=Params(fields=fields),
        init=InitState(sid=InitSid(master_vol=dict(model['init']).get(0x18, 0x0F))),
        instruments=instrs, freq_table=list(ftab), subtunes=[sub])

# --------------------------------------------------------- usf -> model ----
def _pitch_freq(p, ftab):
    if p.is_rest:
        return None
    ni = (p.octave << 4) | NAMES.index(p.name)
    return (ftab[ni] << 8) | ftab[128 + ni]

def usf_to_model(usf):
    f = usf.params.fields
    atk = []; rel = []
    for i in range(f['bp_atk_n']):
        x = f[f'bp_atk{i}']; reg = x >> 16; kind = 'const' if ((x >> 8) & 1) == 0 else 'perstep'
        atk.append((reg, kind, (x & 0xFF) if kind == 'const' else None, VOICE_OF.get(reg)))
    for i in range(f['bp_rel_n']):
        x = f[f'bp_rel{i}']; reg = x >> 16; kind = 'const' if ((x >> 8) & 1) == 0 else 'perstep'
        rel.append((reg, kind, (x & 0xFF) if kind == 'const' else None, VOICE_OF.get(reg)))
    init = [((f[f'bp_init{i}'] >> 8) & 0xFF, f[f'bp_init{i}'] & 0xFF) for i in range(f['bp_init_n'])]
    ftab = list(usf.freq_table)
    sub = usf.subtunes[0]
    vrows = {vb.id: vb.patterns[0].rows for vb in sub.voices if vb.patterns}
    voices = sorted(vrows)
    gated = len(rel) > 0
    per_step = 2 if gated else 1                       # gated row pair: note(hold)+rest(gap)
    aps = [e[0] for e in atk if e[1] == 'perstep']; rps = [e[0] for e in rel if e[1] == 'perstep']
    nsteps = min(len(r) for r in vrows.values()) // per_step
    steps = []
    onf = f.get('bp_start_frame', 0)
    for k in range(nsteps):
        hi = k * per_step
        hold = max(1, vrows[voices[0]][hi].duration)
        gap = max(1, vrows[voices[0]][hi + 1].duration) if gated else 0
        active = {vc for vc in voices if not vrows[vc][hi].pitch.is_rest}
        attack = []; release = []; amask = 0; rmask = 0
        for i, (reg, kind, val, vc) in enumerate(atk):
            if vc is not None and vc not in active:
                continue
            amask |= (1 << i)
            if kind == 'const':
                attack.append((reg, val))
            else:
                fq = _pitch_freq(vrows[vc][hi].pitch, ftab) or 0
                attack.append((reg, (fq >> 8) & 0xFF if reg in FHI.values() else fq & 0xFF))
        for i, (reg, kind, val, vc) in enumerate(rel):
            if vc is not None and vc not in active:
                continue
            rmask |= (1 << i)
            release.append((reg, val if kind == 'const' else 0))
        steps.append({'attack': attack, 'release': release or None,
                      'on_frame': onf, 'off_frame': (onf + hold) if gated else None,
                      'next': None, 'atk_mask': amask, 'rel_mask': rmask})
        onf += hold + gap
    for k in range(len(steps) - 1):
        steps[k]['next'] = steps[k + 1]['on_frame']
    return {'init': init, 'steps': steps, 'atk_template': atk, 'rel_template': rel,
            'atk_ps': aps, 'rel_ps': rps,
            'loop_to': None if f['bp_loop_to'] < 0 else f['bp_loop_to'],
            'loop_period': f['bp_loop_period'], 'rho': f['bp_rho_milli'] / 1000.0,
            'clock': usf.psid.clock, 'masked': True, 'legato': bool(f['bp_legato'])}

# ------------------------------------------------------------- verify -----
def roundtrip(sid_rel, dur=20.0):
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
    from pipelines.basic_program.proof_multivoice import verdict_basic
    sid = os.path.join(ROOT, 'hvsc84', sid_rel)
    m = build_model(sid, dur)
    if 'unsupported' in m:
        return {'status': 'unsupported:' + m['unsupported']}
    if not is_clean(m):
        return {'status': 'not_clean'}
    usf_path = os.path.join(ROOT, 'tmp/basic_program_research/rt.usf')
    write_file(model_to_usf(m), usf_path)
    m2 = usf_to_model(parse_file(usf_path))
    out = os.path.join(ROOT, 'tmp/basic_program_research/rt.sid')
    with open(out, 'wb') as fo:
        fo.write(build_psid(m2))
    r = compare_instruction_stream(writelog_capture(sid, 0, dur),
                                   writelog_capture(out, 0, dur), skip_init=False)
    ok, ov, ln = verdict_basic(r)
    return {'status': 'FULL' if ok else ('overlap_diverge' if not ov else 'length_fail'),
            'match': r['match_all'], 'len_a': r['len_all_a'], 'len_b': r['len_all_b']}

if __name__ == '__main__':
    for rel in ['DEMOS/UNKNOWN/Twinkle_BASIC.sid', 'DEMOS/A-F/Cancion_de_cuna_BASIC.sid',
                'DEMOS/A-F/Baby_Elephant_Walk_BASIC.sid', 'DEMOS/S-Z/Toonypoo_3_BASIC.sid']:
        print(rel.split('/')[-1], '->', roundtrip(rel))
