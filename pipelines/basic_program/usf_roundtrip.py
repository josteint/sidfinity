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
                     Pitch, InstrumentRef, PwmConfig, GlobalEvent, write_file, parse_file)
from pipelines.basic_program.semantic_lift import build_model, build_psid, FREQ as _F
from pipelines.basic_program import semantic_lift as S

FREQ = {0x00, 0x01, 0x07, 0x08, 0x0e, 0x0f}
FHI = {1: 0x01, 2: 0x08, 3: 0x0f}; FLO = {1: 0x00, 2: 0x07, 3: 0x0e}
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Per-voice register map. Per-note variation in a voice's TIMBRE regs
# (ctrl=waveform / ad / sr / pulse-width) = a per-note INSTRUMENT change (USF
# Instrument + NoteRow.instr) — schema-free, principle Rule 2. GLOBAL regs
# (filter $D415-17, master-vol $D418) are NOT per-voice instrument properties
# -> deferred to Phase 2.
REG_VOICE = {}; REG_FIELD = {}
for _v, _base in ((1, 0), (2, 7), (3, 14)):
    for _off, _f in enumerate(['flo', 'fhi', 'pwlo', 'pwhi', 'ctrl', 'ad', 'sr']):
        REG_VOICE[_base + _off] = _v; REG_FIELD[_base + _off] = _f
VOICE_OF = {r: REG_VOICE[r] for r in FREQ}
TIMBRE = {r for r, f in REG_FIELD.items() if f in ('ctrl', 'ad', 'sr', 'pwlo', 'pwhi')}
GLOBAL_REGS = {0x15, 0x16, 0x17, 0x18}     # filter + master vol — Phase 2


def _all_templates(model):
    """Every template list in the model (multi: all K templates' atk+rel)."""
    if model.get('multi'):
        return [t['atk'] for t in model['multi']] + [t['rel'] for t in model['multi']]
    return [model['atk_template'], model['rel_template']]


def _perstep_timbre(model):
    """{voice: sorted [perstep timbre regs]} — the per-note instrument fields."""
    pt = {}
    for tmpl in _all_templates(model):
        for reg, kind, *_ in tmpl:
            if kind == 'perstep' and reg in TIMBRE:
                pt.setdefault(REG_VOICE[reg], set()).add(reg)
    return {vc: sorted(rs) for vc, rs in pt.items()}


GLOBAL_TRACK = {0x16, 0x17, 0x18}                      # decomposable into the global automation track


def is_clean(model):
    """Round-trippable. Per-note PITCH -> NoteRow pitch; per-note per-voice TIMBRE
    (waveform/ad/sr/pw) -> NoteRow.instr; per-note chip-GLOBAL state ($D416 cutoff /
    $D417 res+route / $D418 vol+mode) -> the global automation track (Phase 2). Only
    a perstep $D415 (cutoff lo) is still unhandled -> deferred."""
    for tmpl in _all_templates(model):
        for ent in tmpl:
            if ent[1] == 'perstep' and ent[0] in GLOBAL_REGS and ent[0] not in GLOBAL_TRACK:
                return False
    return True

def _t4(ent):                                          # normalize entry + authoritative voice
    return (ent[0], ent[1], ent[2], REG_VOICE.get(ent[0]))  # semantic_lift voice_of is freq-only

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
def model_to_usf(model, title='bp', gap_exact=False):
    pt = _perstep_timbre(model)                        # {vc: [perstep timbre regs]}
    inst_voices = set(pt)
    inst_slots = {(vc, r) for vc in inst_voices for r in pt[vc]}

    def _vfix(e):                                      # voice: inst -> voice-tied; else freq-voice / voiceless
        r = e[0]
        v = REG_VOICE[r] if (REG_VOICE.get(r), r) in inst_slots else VOICE_OF.get(r)
        return (r, e[1], e[2], v)
    multi = model.get('multi')
    if multi:                                          # K per-shape templates; atk/rel = the union view
        mt = [{'atk': [_vfix(e) for e in t['atk']],
               'rel': [_vfix(e) for e in t['rel']]} for t in multi]
        atk = [e for t in mt for e in t['atk']]
        rel = [e for t in mt for e in t['rel']]
    else:
        atk = [_vfix(e) for e in model['atk_template']]
        rel = [_vfix(e) for e in model['rel_template']]
    voices = sorted({v for e in atk + rel if (v := e[3])})
    if not voices:                                     # no pitched voice (e.g. a gate-only
        raise ValueError('no_note_voices')             # SFX/click w/ a fixed waveform, no freq)
    steps = model['steps']
    # Effective (running) freq per step/voice. A voice may write only the CHANGED
    # freq byte (stateful freq) — the note's pitch is (running hi, running lo).
    # Active = wrote a freq byte (None = no freq this step; timbre-only / re-trigger
    # steps are handled elsewhere). Full-freq tunes are unchanged (both bytes every note).
    eff = []
    run_hi = {vc: 0 for vc in voices}; run_lo = {vc: 0 for vc in voices}   # SID freq regs reset to 0
    for r, v in model['init']:
        for vc in voices:
            if r == FHI[vc]: run_hi[vc] = v
            elif r == FLO[vc]: run_lo[vc] = v
    for s in steps:
        d = dict(s['attack']); row = {}
        for vc in voices:
            wh, wl = FHI[vc] in d, FLO[vc] in d
            if wh: run_hi[vc] = d[FHI[vc]]
            if wl: run_lo[vc] = d[FLO[vc]]
            row[vc] = ((run_hi[vc] << 8) | run_lo[vc]) \
                if ((wh or wl) and vc in run_hi and vc in run_lo) else None
        eff.append(row)
    # glide members stay ORDINARY steps (own tid / frames / durations) but their
    # gliding-voice row is a REST — the reader re-derives their freq from the
    # armed glide (head + k*delta), so they never enter the freq alphabet.
    kept = list(range(len(steps)))
    # per-tune lossless freq alphabet (distinct freq -> unique freq_table slot)
    allfreqs = {fq for i in kept for vc2, fq in eff[i].items()
                if fq is not None and vc2 not in steps[i].get('glide_member', ())}
    slotmap = _assign_slots(allfreqs)
    if slotmap is None:
        raise ValueError('too_many_pitches')
    # per-note instruments: voices whose TIMBRE varies per note (is_clean verified
    # those regs present every active step). The note's instrument is the bundle of
    # its perstep-timbre attack values -> a distinct Instrument; the engine writes
    # them at note start. ctrl -> waveform, ad/sr -> adsr, pw -> pwm.init.
    instrs = []
    bundle_id = {}; _next = [100]
    run = {}                                           # running (effective) timbre state
    for _r, _v in model['init']:
        if _r in TIMBRE:
            run[_r] = _v
    def note_instr(vc, s):
        if vc not in inst_voices:
            return vc                                  # non-inst voice: one instrument id=vc
        d = dict(s['attack'])
        for r in pt[vc]:                               # update running timbre from this note's writes
            if r in d:
                run[r] = d[r]
        vals = tuple(run.get(r, 0) for r in pt[vc])    # effective timbre (carries stateful regs)
        # multi: a per-note RELEASE ctrl (the gate-off waveform, when it isn't the
        # attack ctrl with the gate bit cleared) is instrument content too — carried
        # as a second waveform entry [attack_ctrl, release_ctrl].
        rctrl = None
        if multi and s['release']:
            rd = dict(s['release'])
            for r in pt[vc]:
                if r in rd and REG_FIELD[r] == 'ctrl':
                    rctrl = rd[r]
        key = (vc, vals, rctrl)
        if key not in bundle_id:
            iid = _next[0]; _next[0] += 1; bundle_id[key] = iid
            fb = {REG_FIELD[r]: v for r, v in zip(pt[vc], vals)}
            wave = [fb['ctrl']] if 'ctrl' in fb else ([0] if rctrl is not None else [])
            if rctrl is not None:
                wave = wave + [rctrl]
            pw = ((fb.get('pwhi', 0) or 0) << 8) | (fb.get('pwlo', 0) or 0)
            pwm = PwmConfig(init=pw) if ('pwlo' in fb or 'pwhi' in fb) else PwmConfig()
            instrs.append(Instrument(id=iid, waveform=wave,
                                     adsr=(fb.get('ad', 0) or 0, fb.get('sr', 0) or 0), pwm=pwm))
        return bundle_id[key]
    # build per-tune freq table (slot -> exact bytes) + per-voice rows
    gated = (not model['legato']) if multi else len(rel) > 0
    ftab = bytearray(256)
    vrows = {vc: [] for vc in voices}
    # median delta as the last step's fallback (its real duration is the loop wrap)
    deltas = [steps[k+1]['on_frame'] - steps[k]['on_frame'] for k in range(len(steps)-1)]
    med = sorted(deltas)[len(deltas)//2] if deltas else 1
    for kk, ki in enumerate(kept):                     # gated: note(hold)+rest(gap); legato: note(step)
        s = steps[ki]; k = ki
        on = s['on_frame']; off = s['off_frame']
        nxt = steps[kept[kk+1]]['on_frame'] if kk + 1 < len(kept) else on + med
        # multi: hold stays EXACT (0 = gate-off in the gate-on frame, or a same-frame
        # split sub-step) — flooring it accumulates +1/step drift (ledger C12).
        hmin = 0 if multi else 1
        hold = max(hmin, (off - on)) if (gated and off is not None) else max(hmin, nxt - on)
        # gap may be 0 (back-to-back notes: the gate-off frame == the next gate-on frame).
        # Forcing max(1,...) inflates every such step by 1 frame -> a progressive timing
        # drift that accumulates past the |len|<=64 tolerance on LONG tunes (500+ steps).
        # gap_exact keeps it exact so on_frames reconstruct losslessly through USF; it's a
        # best_attempt verify-fallback (default max(1,...)) because a rho-rounding-collapsed
        # nxt-off=0 is sometimes SPURIOUS (two distinct frames merged) -> gap=0 would reorder
        # same-frame writes; the 3 tunes where that happens stay FULL via the default.
        gmin = 0 if gap_exact else 1
        # multi + releaseless step (empty-release template): hold spans to the next
        # step, gap exactly 0 -> on_frames reconstruct losslessly (ledger C12).
        gap = max(gmin, nxt - off) if (gated and off is not None) else \
              (max(0, nxt - on - hold) if (multi and gated) else 1)
        for vc in voices:
            f = eff[k][vc]
            if multi and vc in s.get('glide_member', ()):  # glide member: rest row, freq derived at read
                vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=hold))
                if gated:
                    vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=gap))
                continue
            if f is None:
                # timbre-only step: the voice writes a perstep-timbre reg but no note
                # (instrument setup for an upcoming note). Carry the instrument on the
                # rest row so the timbre write resolves; the stored mask emits only the
                # timbre regs (no freq). Voices that wrote a PARTIAL freq stay plain rests.
                # multi: a RELEASE-side timbre write (gate-off on a held voice) also
                # needs the instrument on the rest row.
                d_all = dict(s['attack'])
                if multi and s['release']:
                    d_all.update(dict(s['release']))
                if vc in inst_voices and any(r in d_all for r in pt[vc]) \
                        and FHI[vc] not in dict(s['attack']) and FLO[vc] not in dict(s['attack']):
                    vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=hold,
                                             instr=InstrumentRef(id=note_instr(vc, s))))
                else:
                    vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=hold))
            else:
                slot = slotmap[f]; nm, octv = _slot_pitch(slot)
                ftab[slot] = (f >> 8) & 0xFF; ftab[128 + slot] = f & 0xFF
                g = (s.get('glide') or {}).get(vc)
                fx = ()
                if g:                                  # linear glide from this note
                    d = g['delta']
                    fx = (f'glide_{"up" if d > 0 else "down"}=${abs(d):04X}',
                          f'glide_ticks={g["n"]}')
                    if g.get('hold', 1) > 1:           # staircase: level held R ticks
                        fx += (f'glide_hold={g["hold"]}',)
                vrows[vc].append(NoteRow(pitch=Pitch(name=nm, octave=octv),
                                         duration=hold, instr=InstrumentRef(id=note_instr(vc, s)),
                                         fx_flags=fx))
            if gated:
                vrows[vc].append(NoteRow(pitch=Pitch.rest(), duration=gap))
    # non-inst voices: one instrument (waveform from the gate-on const ctrl)
    for vc in voices:
        if vc not in inst_voices:
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
    # chip-global automation: decompose the perstep GLOBAL regs into musical fields
    # ($D418=mode<<4|dyn, $D417=res<<4|route, $D416=cutoff); sparse running-state
    # events keyed by step. The composer re-packs the bytes at the template position.
    gtrack = []; run_g = {}
    for kk, ki in enumerate(kept):
        s = steps[ki]; k = kk
        d = dict(s['attack']); d.update(dict(s['release']) if s['release'] else {})
        chg = {}
        for reg in (0x16, 0x17, 0x18):
            if reg not in d:
                continue
            fv = ({'cutoff': d[reg]} if reg == 0x16 else
                  {'res': d[reg] >> 4, 'route': d[reg] & 0xF} if reg == 0x17 else
                  {'mode': d[reg] >> 4, 'dyn': d[reg] & 0xF})
            for f, v in fv.items():
                if run_g.get(f) != v:
                    run_g[f] = v; chg[f] = v
        if chg:
            gtrack.append(GlobalEvent(step=k, **chg))
    sub = MusicSubtune(id=0, tempo=1, voices=vblocks, global_track=gtrack)
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
    song_end = model.get('song_end') or []             # song-end silence (bookend of init)
    fields['bp_songend_n'] = len(song_end)
    for i, (reg, val) in enumerate(song_end):
        fields[f'bp_songend{i}'] = (reg << 8) | (val & 0xFF)
    pw_program = model.get('pw_program') or {}          # per-voice PW sweep PROGRAM (C1 orderlist)
    fields['bp_pwprog_voices'] = sum(1 << (vc - 1) for vc in pw_program)   # bitmask of modulated voices
    fields['bp_mod_start'] = model.get('mod_start', 0)  # play-frame the sweep begins
    fields['bp_mod_inc'] = model.get('mod_inc', 0)      # fractional tick rate (per play, /256)
    for vc, (tab, secs) in pw_program.items():
        fields[f'bp_pwprog{vc}_ntab'] = len(tab)        # value table (4 bytes per int)
        for i in range((len(tab) + 3) // 4):
            ch = (tab[4 * i:4 * i + 4] + [0, 0, 0, 0])[:4]
            fields[f'bp_pwprog{vc}_t{i}'] = (ch[0] << 24) | (ch[1] << 16) | (ch[2] << 8) | ch[3]
        fields[f'bp_pwprog{vc}_nsec'] = len(secs)       # sections: (offset, period_len, repeats)
        for i, (off, ln, rep) in enumerate(secs):
            fields[f'bp_pwprog{vc}_s{i}'] = (off << 16) | (ln << 8) | rep
    def _kind(e):                                      # 2 = from instrument; 3 = from global track
        if e[1] == 'perstep' and e[0] in GLOBAL_TRACK:
            return 3
        if e[1] == 'perstep' and (e[3], e[0]) in inst_slots:
            return 2
        return 0 if e[1] == 'const' else 1             # a CONST timbre slot stays const
    if multi:
        # K per-shape templates + per-step template id (packed 4/int) — the write
        # model, same params{} precedent as bp_atk{i}/bp_mask{k}. Musical content
        # (pitch/duration/instrument/global track) is in the USF body as always.
        fields['bp_atk_n'] = 0; fields['bp_rel_n'] = 0
        fields['bp_multi'] = 1; fields['bp_ntmpl'] = len(mt)
        for t, tp in enumerate(mt):
            fields[f'bp_t{t}_atk_n'] = len(tp['atk'])
            for i, e in enumerate(tp['atk']):
                fields[f'bp_t{t}_atk{i}'] = (e[0] << 16) | (_kind(e) << 8) | ((e[2] or 0) & 0xFF)
            fields[f'bp_t{t}_rel_n'] = len(tp['rel'])
            for i, e in enumerate(tp['rel']):
                fields[f'bp_t{t}_rel{i}'] = (e[0] << 16) | (_kind(e) << 8) | ((e[2] or 0) & 0xFF)
        tids = [steps[i]['tid'] for i in kept]
        for j in range(0, len(tids), 4):
            ch = (tids[j:j + 4] + [0, 0, 0, 0])[:4]
            fields[f'bp_tid{j // 4}'] = (ch[0] << 24) | (ch[1] << 16) | (ch[2] << 8) | ch[3]
    else:
        for i, e in enumerate(atk):
            fields[f'bp_atk{i}'] = (e[0] << 16) | (_kind(e) << 8) | ((e[2] or 0) & 0xFF)
        for i, e in enumerate(rel):
            fields[f'bp_rel{i}'] = (e[0] << 16) | (_kind(e) << 8) | ((e[2] or 0) & 0xFF)
    # voice-rest derivation reproduces voice slots, but not voiceless-const
    # per-step activity (e.g. a per-note $D418 re-poke). Store explicit masks
    # only when that derivation would be wrong (Ahoy-class minority).
    need_masks = False
    if not multi:                                      # multi: the tid replaces the mask
        for k, s in enumerate(steps):
            act = {vc for vc in voices if eff[k][vc] is not None}
            da = sum(1 << i for i, e in enumerate(atk) if e[3] is None or e[3] in act)
            dr = sum(1 << i for i, e in enumerate(rel) if e[3] is None or e[3] in act)
            if da != s.get('atk_mask', da) or dr != s.get('rel_mask', dr):
                need_masks = True; break
    if need_masks:
        fields['bp_has_masks'] = 1
        for k, s in enumerate(steps):
            fields[f'bp_mask{k}'] = (s.get('atk_mask', 0) << 16) | s.get('rel_mask', 0)
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

_KINDS = {0: 'const', 1: 'perstep', 2: 'inst', 3: 'global'}


def usf_to_model(usf):
    f = usf.params.fields
    atk = []; rel = []
    def _pvoice(reg, kind):                            # inst slots voice-tied; else freq-voice / voiceless
        return REG_VOICE.get(reg) if kind == 'inst' else VOICE_OF.get(reg)
    for i in range(f['bp_atk_n']):
        x = f[f'bp_atk{i}']; reg = x >> 16; kind = _KINDS[(x >> 8) & 0xFF]
        atk.append((reg, kind, (x & 0xFF) if kind == 'const' else None, _pvoice(reg, kind)))
    for i in range(f['bp_rel_n']):
        x = f[f'bp_rel{i}']; reg = x >> 16; kind = _KINDS[(x >> 8) & 0xFF]
        rel.append((reg, kind, (x & 0xFF) if kind == 'const' else None, _pvoice(reg, kind)))
    multi_t = None
    if f.get('bp_multi'):
        def _dec(pref, n):
            out = []
            for i in range(n):
                x = f[f'{pref}{i}']; reg = x >> 16; kind = _KINDS[(x >> 8) & 0xFF]
                out.append((reg, kind, (x & 0xFF) if kind == 'const' else None, _pvoice(reg, kind)))
            return out
        multi_t = [{'atk': _dec(f'bp_t{t}_atk', f[f'bp_t{t}_atk_n']),
                    'rel': _dec(f'bp_t{t}_rel', f[f'bp_t{t}_rel_n'])}
                   for t in range(f['bp_ntmpl'])]
    init = [((f[f'bp_init{i}'] >> 8) & 0xFF, f[f'bp_init{i}'] & 0xFF) for i in range(f['bp_init_n'])]
    song_end = [((f[f'bp_songend{i}'] >> 8) & 0xFF, f[f'bp_songend{i}'] & 0xFF)
                for i in range(f.get('bp_songend_n', 0))]
    pw_program = {}                                     # modulation sweep program (ch 1-3 = PW, 4 = filter)
    for vc in (1, 2, 3, 4):
        if f.get('bp_pwprog_voices', 0) & (1 << (vc - 1)):
            ntab = f[f'bp_pwprog{vc}_ntab']; tab = []
            for i in range((ntab + 3) // 4):
                x = f[f'bp_pwprog{vc}_t{i}']
                tab += [(x >> 24) & 0xFF, (x >> 16) & 0xFF, (x >> 8) & 0xFF, x & 0xFF]
            secs = [((f[f'bp_pwprog{vc}_s{i}'] >> 16) & 0xFF, (f[f'bp_pwprog{vc}_s{i}'] >> 8) & 0xFF,
                     f[f'bp_pwprog{vc}_s{i}'] & 0xFF) for i in range(f[f'bp_pwprog{vc}_nsec'])]
            pw_program[vc] = (tab[:ntab], secs)
    mod_start = f.get('bp_mod_start', 0)
    mod_inc = f.get('bp_mod_inc', 0)
    ftab = list(usf.freq_table)
    sub = usf.subtunes[0]
    vrows = {vb.id: vb.patterns[0].rows for vb in sub.voices if vb.patterns}
    voices = sorted(vrows)
    # per-note instrument table: id -> (ctrl, ad, sr, pw16), for kind='inst' slots
    itab = {ins.id: (ins.waveform[0] if ins.waveform else 0, ins.adsr[0], ins.adsr[1],
                     ins.pwm.init if ins.pwm else 0,
                     ins.waveform[1] if len(ins.waveform) > 1 else None)  # release ctrl
            for ins in usf.instruments}

    def inst_val(vc, hi, reg, release=False):
        note = vrows[vc][hi]
        if note.instr is None:                         # timbre written on a rest step (no note) — defer
            raise ValueError('not_clean')
        ctrl, ad, sr, pw, rctrl = itab[note.instr.id]
        fld = REG_FIELD[reg]
        if fld == 'ctrl':
            if release:
                return rctrl if rctrl is not None else (ctrl & 0xFE)
            return ctrl
        return {'ad': ad, 'sr': sr, 'pwlo': pw & 0xFF, 'pwhi': (pw >> 8) & 0xFF}[fld]
    # chip-global automation: run the global track to pack the $D416/17/18 bytes
    gevents = {e.step: e for e in sub.global_track}; run_g = {}
    def gpack(reg):
        if reg == 0x18: return ((run_g.get('mode', 0) & 0xF) << 4) | (run_g.get('dyn', 0) & 0xF)
        if reg == 0x17: return ((run_g.get('res', 0) & 0xF) << 4) | (run_g.get('route', 0) & 0xF)
        return run_g.get('cutoff', 0) & 0xFF           # $D416
    gated = (not bool(f['bp_legato'])) if multi_t else len(rel) > 0
    per_step = 2 if gated else 1                       # gated row pair: note(hold)+rest(gap)
    aps = [e[0] for e in atk if e[1] == 'perstep']; rps = [e[0] for e in rel if e[1] == 'perstep']
    nsteps = min(len(r) for r in vrows.values()) // per_step
    has_masks = f.get('bp_has_masks', 0) == 1
    steps = []
    glides = {}                                        # vc -> [base_freq, delta, k, n] (armed glide)
    onf = f.get('bp_start_frame', 0)
    for k in range(nsteps):
        hi = k * per_step
        hold = (vrows[voices[0]][hi].duration if multi_t                # exact (C12)
                else max(1, vrows[voices[0]][hi].duration))
        gap = vrows[voices[0]][hi + 1].duration if gated else 0   # exact (0 = back-to-back notes)
        ge = gevents.get(k)                            # advance the global state this step
        if ge:
            for fld in ('dyn', 'cutoff', 'res', 'mode', 'route'):
                if getattr(ge, fld) is not None:
                    run_g[fld] = getattr(ge, fld)
        if multi_t:                                    # the step's own template, no masks
            tid = (f[f'bp_tid{k // 4}'] >> (8 * (3 - k % 4))) & 0xFF
            a_ent, r_ent = multi_t[tid]['atk'], multi_t[tid]['rel']
        else:
            a_ent, r_ent = atk, rel
        active = {vc for vc in voices if not vrows[vc][hi].pitch.is_rest}
        mask_a = (f[f'bp_mask{k}'] >> 16) & 0xFFFF if has_masks else None
        mask_r = f[f'bp_mask{k}'] & 0xFFFF if has_masks else None
        if multi_t:
            # arm a linear glide from this step's fx (per-voice; simultaneous OK)
            for vc in voices:
                fl = dict(x.split('=', 1) for x in vrows[vc][hi].fx_flags if '=' in x)
                if 'glide_ticks' in fl and ('glide_up' in fl or 'glide_down' in fl):
                    dlt = (int(fl['glide_up'].lstrip('$'), 16) if 'glide_up' in fl
                           else -int(fl['glide_down'].lstrip('$'), 16))
                    glides[vc] = [_pitch_freq(vrows[vc][hi].pitch, ftab) or 0,
                                  dlt, 0, int(fl['glide_ticks']),
                                  int(fl.get('glide_hold', 1))]
        attack = []; release = []; amask = 0; rmask = 0
        stepped = set()                                # glide tick: once per STEP (hi+lo pair)
        for i, (reg, kind, val, vc) in enumerate(a_ent):
            present = True if multi_t else (((mask_a >> i) & 1) if has_masks else (vc is None or vc in active))
            if not present:
                continue
            amask |= (1 << i)
            if kind == 'const':
                attack.append((reg, val))
            elif kind == 'inst':                       # per-note timbre from the note's instrument
                attack.append((reg, inst_val(vc, hi, reg)))
            elif kind == 'global':                     # chip-global dynamics/filter from the global track
                attack.append((reg, gpack(reg)))
            else:                                      # perstep freq from the note's pitch
                p = vrows[vc][hi].pitch
                if p.is_rest and vc in glides:         # glide member: derived freq
                    g = glides[vc]
                    if vc not in stepped:
                        g[2] += 1; stepped.add(vc)
                    fq = (g[0] + (g[2] // g[4]) * g[1]) & 0xFFFF
                elif p.is_rest:
                    fq = 0
                else:
                    fq = _pitch_freq(p, ftab) or 0
                attack.append((reg, (fq >> 8) & 0xFF if reg in FHI.values() else fq & 0xFF))
        for i, (reg, kind, val, vc) in enumerate(r_ent):
            present = True if multi_t else (((mask_r >> i) & 1) if has_masks else (vc is None or vc in active))
            if not present:
                continue
            rmask |= (1 << i)
            if kind == 'inst':
                release.append((reg, inst_val(vc, hi, reg, release=True)))
            elif kind == 'global':
                release.append((reg, gpack(reg)))
            else:
                release.append((reg, val if kind == 'const' else 0))
        steps.append({'attack': attack, 'release': release or None,
                      'on_frame': onf, 'off_frame': (onf + hold) if gated else None,
                      'next': None, 'atk_mask': amask, 'rel_mask': rmask,
                      'tid': (tid if multi_t else 0)})
        for vc in stepped:                             # disarm exhausted glides at step end
            if vc in glides and glides[vc][2] >= glides[vc][3]:
                del glides[vc]
        onf += hold + gap
    for k in range(len(steps) - 1):
        steps[k]['next'] = steps[k + 1]['on_frame']
    # the player only knows const/perstep; inst slots were resolved into each step's
    # writes above, so present them to the player as plain perstep (per-step value).
    def _to_ps(t):
        return [(reg, 'perstep' if kind in ('inst', 'global') else kind, val, vc) for reg, kind, val, vc in t]
    atk_o, rel_o = _to_ps(atk), _to_ps(rel)
    multi_o = ([{'atk': _to_ps(t['atk']), 'rel': _to_ps(t['rel'])} for t in multi_t]
               if multi_t else None)                   # the player only knows const/perstep
    return {'init': init, 'steps': steps, 'atk_template': atk_o, 'rel_template': rel_o,
            'atk_ps': [e[0] for e in atk_o if e[1] == 'perstep'],
            'rel_ps': [e[0] for e in rel_o if e[1] == 'perstep'],
            'loop_to': None if f['bp_loop_to'] < 0 else f['bp_loop_to'],
            'loop_period': f['bp_loop_period'], 'rho': f['bp_rho_milli'] / 1000.0,
            'clock': usf.psid.clock, 'masked': True, 'legato': bool(f['bp_legato']),
            'multi': multi_o,
            'song_end': song_end, 'pw_program': pw_program, 'mod_start': mod_start, 'mod_inc': mod_inc}

# ------------------------------------------------------------- verify -----
def _compare_with_extend(orig_wl, reb_sid, dur, loops):
    """Compare the orig writelog vs the rebuild SID captured at `dur`. If the
    rebuild is a correct but SHORT prefix AND the tune LOOPS, re-capture it for
    more frames and accept ONLY iff the orig's ENTIRE writelog is then reproduced
    exactly (orig is an exact prefix of the longer rebuild) — "the rebuild emits
    the same writelog as the original", no length tolerance. A looping rebuild
    runs ~1/rho slower than the orig's free-running BASIC, so the fixed window can
    cut it mid-loop; a play-once rebuild has HALTED (done=1) and never grows, so a
    genuine short tail (e.g. trailing-trim) is not rescued. A loop that truly
    DIVERGES from the orig when extended fails the exact-prefix check and stays
    length_fail. Returns (compare_result, extended_full)."""
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
    r = compare_instruction_stream(orig_wl, writelog_capture(reb_sid, 0, dur), skip_init=False)
    a0, b0 = r['len_all_a'], r['len_all_b']
    # Try the extension for play-once rebuilds too (not just loops): a rebuild that
    # merely runs slower than the free-running BASIC gets cut by the fixed window
    # even when it plays once (e.g. long glide-expanded step lists). A rebuild that
    # truly HALTED (done=1) never grows, so the exact-prefix acceptance can't
    # false-pass — the extra capture is the only cost.
    if r['match_all'] == min(a0, b0) and a0 - b0 > 64:             # only would-be length_fail

        ext = min(dur * (a0 / max(b0, 1)) * 1.2 + 2, 240.0)
        r2 = compare_instruction_stream(orig_wl, writelog_capture(reb_sid, 0, ext), skip_init=False)
        if r2['match_all'] == r2['len_all_a']:            # whole orig reproduced as prefix
            return r2, True
        # Play-once rebuild fully consumed with only a short orig tail left: the
        # same |len|<=64 tolerance the base verdict grants (the orig's final
        # capture-cut partial note, dropped at segmentation).
        if r2['match_all'] == r2['len_all_b'] and r2['len_all_a'] - r2['match_all'] <= 64:
            return r2, True
    return r, False


def _attempt_model(m, sid, dur, orig_wl, title='bp', gap_exact=False):
    """Build a rebuild from model m and verify against the (cached) orig writelog.
    Returns (status, match, len_a, len_b, usf_or_None, sid_bytes_or_None). Pool-safe."""
    import tempfile
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
    from pipelines.basic_program.proof_multivoice import verdict_basic
    if 'unsupported' in m:
        return ('unsupported:' + m['unsupported'], 0, 0, 0, None, None)
    if not is_clean(m):
        return ('not_clean', 0, 0, 0, None, None)
    try:
        usf = model_to_usf(m, title=title, gap_exact=gap_exact)
    except ValueError as e:                            # e.g. too_many_pitches (vibrato > 96 slots)
        return (str(e), 0, 0, 0, None, None)
    fd, up = tempfile.mkstemp(suffix='.usf'); os.close(fd)
    fd, sp = tempfile.mkstemp(suffix='.sid'); os.close(fd)
    extended_full = False
    try:
        try:
            write_file(usf, up)
            sid_bytes = build_psid(usf_to_model(parse_file(up)))
            with open(sp, 'wb') as fo:
                fo.write(sid_bytes)
            r, extended_full = _compare_with_extend(orig_wl, sp, dur, m.get('loop_to') is not None)
        except Exception:                              # degenerate model (e.g. empty voices)
            return ('build_fail', 0, 0, 0, None, None)
    finally:
        for p in (up, sp):
            if os.path.exists(p): os.unlink(p)
    if extended_full:
        ok, ov = True, True
    else:
        ok, ov, _ln = verdict_basic(r)
    status = 'FULL' if ok else ('overlap_diverge' if not ov else 'length_fail')
    return (status, r['match_all'], r['len_all_a'], r['len_all_b'], usf, sid_bytes)


def best_attempt(sid_rel, dur, title='bp'):
    """Verify the auto model; if it BUILT but verified diverge/length_fail, retry the
    force-split variant (the auto-fallback only fires on build-failure, so an unsplit
    model that builds-but-diverges where splitting would win is otherwise missed).
    Runs the whole fallback chain twice: first with the default gap encoding, then (only
    if still length_fail) with the drift-free gap_exact encoding — a length_fail-only
    fallback so the 3 tunes whose rho-rounding-collapsed gap=0 would REORDER same-frame
    writes stay FULL via the default. gap_exact must compose with every variant (e.g.
    Barn_Razing needs min_trim + gap_exact), hence the full second pass.
    Returns (status, match, len_a, len_b, usf_or_None, sid_bytes_or_None)."""
    from pipelines.hubbard.verify_cycle import writelog_capture
    sid = os.path.join(ROOT, 'hvsc84', sid_rel)
    orig_wl = writelog_capture(sid, 0, dur)

    def _try(gap_exact):
        res = _attempt_model(build_model(sid, dur), sid, dur, orig_wl, title, gap_exact=gap_exact)
        # too_few_after_trim = the AGGRESSIVE trailing-trim dropped a heterogeneous step
        # sequence below 2 steps. The model has real content (raw segment had 60-600+
        # steps); min_trim keeps it. Treat too_few like a built-but-wrong retry candidate.
        toofew = res[0].startswith('unsupported:too_few')
        if res[0] in ('overlap_diverge', 'length_fail') or toofew:  # built but wrong/over-trimmed
            res2 = _attempt_model(build_model(sid, dur, force_split=True), sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res2[0] == 'FULL':
                return res2
        if res[0] == 'length_fail' or toofew:              # short tail / over-trim -> keep final steps
            res3 = _attempt_model(build_model(sid, dur, min_trim=True), sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res3[0] == 'FULL':
                return res3
        if res[0] in ('overlap_diverge', 'length_fail'):   # trailing master-vol=0 fade -> song-end
            res4 = _attempt_model(build_model(sid, dur, detect_song_end=True), sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res4[0] == 'FULL':
                return res4
        if res[0] in ('overlap_diverge', 'length_fail'):   # free-running PW sweep modulation
            res5 = _attempt_model(build_model(sid, dur, detect_modulation=True), sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res5[0] == 'FULL':
                return res5
        if res[0] in ('overlap_diverge', 'length_fail') or res[0] in (
                'unsupported:variable_template', 'unsupported:legato_variable',
                'unsupported:too_few_after_trim', 'unsupported:too_few_steps',
                'unsupported:template_derive'):
            # heterogeneous step shapes -> K per-shape templates + per-step tid
            res6 = _attempt_model(build_model(sid, dur, multi_template=True), sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res6[0] == 'FULL':
                return res6
            # multi + split: an intra-step dup FREQ (arp within a step) round-trips
            # wrong through one NoteRow pitch per step — the unsplit multi MODEL
            # builds (positional dups) so the auto split-fallback never fires; force
            # the split so each freq gets its own sub-step (its own NoteRow).
            res7 = _attempt_model(build_model(sid, dur, multi_template=True, force_split=True),
                                  sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res7[0] == 'FULL':
                return res7
        if res[0] in ('overlap_diverge', 'length_fail', 'too_many_pitches') or \
                res[0].startswith('unsupported:'):
            # linear glides: constant-delta freq runs lift to glide_up/down +
            # glide_ticks row commands (the intermediates are engine mechanism,
            # not per-note content — they'd otherwise blow the 96-slot alphabet).
            res8 = _attempt_model(build_model(sid, dur, multi_template=True, force_split=True,
                                              detect_glide=True),
                                  sid, dur, orig_wl, title, gap_exact=gap_exact)
            if res8[0] == 'FULL':
                return res8
            if res8[0] != 'FULL':                      # e.g. the trim ate a trailing run, or the
                # trimmed tail's pitches pushed the alphabet over (min_trim keeps them liftable)
                res9 = _attempt_model(build_model(sid, dur, multi_template=True, force_split=True,
                                                  detect_glide=True, min_trim=True),
                                      sid, dur, orig_wl, title, gap_exact=gap_exact)
                if res9[0] == 'FULL':
                    return res9
        return res

    res = _try(False)
    if res[0] == 'length_fail' or res[0].startswith('unsupported:too_few'):  # drift / over-trim
        resg = _try(True)
        if resg[0] == 'FULL':
            return resg
    return res


def roundtrip(sid_rel, dur=20.0):
    """Full path SID -> model -> .usf -> model -> SID -> writelog vs orig (pool-safe)."""
    st, mt, la, lb, _u, _s = best_attempt(sid_rel, dur)
    return {'status': st, 'match': mt, 'len_a': la, 'len_b': lb}


def verify_usf(usf_rel, sid_rel, dur):
    """Production-path verdict: an EXISTING .usf -> model -> SID -> writelog vs the
    HVSC original. This is the regression check (the .usf is the persisted artifact;
    the model is reconstructed from it, not re-derived from the SID)."""
    import tempfile
    from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
    from pipelines.basic_program.proof_multivoice import verdict_basic
    sid = os.path.join(ROOT, 'hvsc84', sid_rel)
    m2 = usf_to_model(parse_file(os.path.join(ROOT, 'hvsc84', usf_rel)))
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as fo:
        fo.write(build_psid(m2)); out = fo.name
    try:
        orig_wl = writelog_capture(sid, 0, dur)
        r, extended_full = _compare_with_extend(orig_wl, out, dur, m2.get('loop_to') is not None)
    finally:
        os.unlink(out)
    ok = extended_full or verdict_basic(r)[0]
    return {'ok': ok, 'match': r['match_all'], 'len_a': r['len_all_a'], 'len_b': r['len_all_b']}


if __name__ == '__main__':
    for rel in ['DEMOS/UNKNOWN/Twinkle_BASIC.sid', 'DEMOS/A-F/Cancion_de_cuna_BASIC.sid',
                'DEMOS/A-F/Baby_Elephant_Walk_BASIC.sid', 'DEMOS/S-Z/Toonypoo_3_BASIC.sid']:
        print(rel.split('/')[-1], '->', roundtrip(rel))
