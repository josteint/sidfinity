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
# register -> voice (1/2/3); regs not listed (filter $15-17, vol $18) are GLOBAL
VOICEREG = {b + o: v for v, b in ((1, 0x00), (2, 0x07), (3, 0x0e)) for o in range(7)}
def voice_of(reg):
    return VOICEREG.get(reg)              # None = global (always emitted)

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

def _split_attack(atk):
    """Split a frame-tagged write list [(f,r,v),...] into sub-steps, starting a NEW
    sub whenever a register repeats. A repeat = an arpeggio/vibrato per-tick freq
    update inside one held note; splitting turns it into a sequence of fast freq
    sub-steps (fired by the absolute-frame player's catch-up loop), so the per-step
    template has each register at most once. Non-arp steps (no repeat) pass through
    unchanged as a single sub."""
    subs = []; cur = []; seen = set()
    for f, r, v in atk:
        if r in seen:
            subs.append(cur); cur = []; seen = set()
        cur.append((f, r, v)); seen.add(r)
    if cur:
        subs.append(cur)
    return subs


def segment(frames, split_dups=False):
    """-> (init, steps, start_frame, legato). Steps carry the FULL ordered writes.

    split_dups: when True, a step's attack is split into sub-steps at each register
    repeat (arpeggio/vibrato per-tick freq updates). OFF by default because a
    CONSISTENT intra-step dup (same shape every step, e.g. ctrl re-poked every note)
    is handled positionally by derive_template — splitting it would fragment the
    shape. build_model retries with split_dups=True only when the unsplit path fails.

    GATED tunes: a step ends after each gate-off GROUP (a maximal run of gate-clear
    ctrl writes); the step splits into attack (everything before that trailing
    group) + release (the group). LEGATO tunes (no per-note gate-off): a step
    boundary is each gate-on / freq-change to a new note; no release."""
    stream = flatten(frames)
    start = _music_start(stream)
    if start is None:
        return [(r, v) for f, r, v in stream], [], 0, False
    g0 = next(i for i, (f, r, v) in enumerate(stream) if r in CTRL and (v & 1))
    n_off = sum(1 for f, r, v in stream[g0:] if r in CTRL and not (v & 1))
    legato = n_off < max(3, (len(stream) - g0) // 200)  # ~no per-note gate-off
    if legato:
        # one-time gate-on + setup are INIT; steps are pure freq active-runs.
        fa = next((i for i in range(g0, len(stream)) if stream[i][1] in FREQ), None)
        if fa is None:
            return [(r, v) for f, r, v in stream], [], 0, True
        init = [(r, v) for f, r, v in stream[:fa]]
        start_frame = stream[fa][0]
        music = stream[fa:]
        byframe = {}
        for f, r, v in music:
            byframe.setdefault(f, []).append((r, v))
        steps = []
        frs = sorted(byframe); i = 0
        while i < len(frs):
            f0 = frs[i]; w = [(f0, r, v) for r, v in byframe[f0]]; j = i + 1
            while j < len(frs) and frs[j] == frs[j-1] + 1:
                w += [(frs[j], r, v) for r, v in byframe[frs[j]]]; j += 1
            for sub in (_split_attack(w) if split_dups else [w]):  # arp/vibrato -> sub-steps
                steps.append({'attack': [(r, v) for f, r, v in sub], 'on_frame': sub[0][0],
                              'release': None, 'off_frame': None, 'next': None})
            i = j
        for k in range(len(steps) - 1):
            steps[k]['next'] = steps[k+1]['on_frame']
        return init, steps, start_frame, True
    # GATED: music starts at the first gate-on (backed over its freq);
    # a step ends after each gate-off GROUP, split into attack + release.
    init = [(r, v) for f, r, v in stream[:start]]
    start_frame = stream[start][0]
    music = stream[start:]
    raw = []; cur = []
    for idx, (f, r, v) in enumerate(music):
        cur.append((f, r, v))
        if r in CTRL and not (v & 1):
            nxt = music[idx+1] if idx + 1 < len(music) else None
            nxt_gc = nxt is not None and nxt[1] in CTRL and not (nxt[2] & 1)
            if not nxt_gc:
                raw.append(cur); cur = []
    if cur:
        # trailing capture-cut partial (its gate-off lies past the window) — the
        # orig PLAYED these writes. Kept only by the min_trim variants (every
        # other path's trailing-trim pops releaseless steps right back off).
        raw.append(cur)
    steps = []
    for st in raw:
        ri = len(st)
        while ri > 0 and st[ri-1][1] in CTRL and not (st[ri-1][2] & 1):
            ri -= 1
        atk, rel = st[:ri], st[ri:]
        if not atk:
            continue
        subs = _split_attack(atk) if split_dups else [atk]  # arp/vibrato -> sub-steps
        for si, sub in enumerate(subs):
            last = si == len(subs) - 1                 # gate-off rides the last sub only
            steps.append({'attack': [(r, v) for f, r, v in sub], 'on_frame': sub[0][0],
                          'release': [(r, v) for f, r, v in rel] if (rel and last) else None,
                          'off_frame': rel[0][0] if (rel and last) else None, 'next': None})
    for k in range(len(steps) - 1):
        steps[k]['next'] = steps[k+1]['on_frame']
    return init, steps, start_frame, False

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

def _union_order(seqs):
    """Ordered UNION of the step reg-sequences (off_superset): a single order such
    that every step is an order-preserving subsequence. Build a precedence DAG from
    adjacent regs, topo-sort (Kahn, reg-value tie-break for determinism), verify.
    Returns None on a within-step dup (arpeggio — deferred) or a precedence cycle."""
    import heapq, collections
    for sq in seqs:
        if len(set(sq)) != len(sq):
            return None                                # intra-step dup -> arpeggio
    nodes = set(); succ = collections.defaultdict(set); indeg = collections.defaultdict(int)
    for sq in seqs:
        nodes.update(sq)
        for a, b in zip(sq, sq[1:]):
            if a != b and b not in succ[a]:
                succ[a].add(b); indeg[b] += 1
    ready = [n for n in nodes if indeg[n] == 0]; heapq.heapify(ready)
    order = []
    while ready:
        n = heapq.heappop(ready); order.append(n)
        for m in sorted(succ[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(ready, m)
    if len(order) != len(nodes):
        return None                                    # precedence cycle
    pos = {r: i for i, r in enumerate(order)}
    for sq in seqs:
        idx = [pos[r] for r in sq]
        if idx != sorted(idx):
            return None
    return order

def _superset_templates(steps):
    """Variable-template handling via a PER-REGISTER mask. A step writes a SUBSET
    of a superset register order (rests = a voice's regs absent; a freq-inherited
    step = only gate regs). Derive the superset order (the max-register step),
    require every step's reg-seq == superset filtered to that step's present regs
    (order-preserving), classify each superset reg const/perstep (over steps where
    present), and set per-step attack/release masks (bit i = superset entry i
    present). Returns (atk_t4, atk_ps_regs, rel_t4, rel_ps_regs) or None."""
    def regseq(s, key):
        return [r for r, v in s[key]]
    def derive(key):
        seqs = [regseq(s, key) for s in steps if s[key]]
        if not seqs:
            return []
        order = _union_order(seqs)                     # ordered union of all steps
        if order is None:
            return None                                # arpeggio (intra-step dup) or cycle
        t = []
        for reg in order:
            vals = [dict(s[key])[reg] for s in steps if s[key] and reg in dict(s[key])]
            kind = 'const' if len(set(vals)) == 1 else 'perstep'
            t.append((reg, kind, vals[0] if kind == 'const' else None, voice_of(reg)))
        return t
    atk_t = derive('attack')
    if atk_t is None:
        return None
    rel_t = derive('release')
    if rel_t is None:
        return None
    atk_order = [t[0] for t in atk_t]; rel_order = [t[0] for t in rel_t]
    for s in steps:
        ap = set(r for r, v in s['attack'])
        s['atk_mask'] = sum(1 << i for i, r in enumerate(atk_order) if r in ap)
        rp = set(r for r, v in s['release']) if s['release'] else set()
        s['rel_mask'] = sum(1 << i for i, r in enumerate(rel_order) if r in rp)
    return (atk_t, [r for r, k, v, vo in atk_t if k == 'perstep'],
            rel_t, [r for r, k, v, vo in rel_t if k == 'perstep'])

def _multi_templates(steps, kmax=128):
    """MULTI-TEMPLATE derivation: cluster steps by their exact (attack reg-seq,
    release reg-seq) SHAPE; each cluster gets a POSITIONAL template (const/perstep
    per slot). The general form of the superset+mask: conflicting register orders
    (each shape keeps its own order), intra-step dups (a repeated reg is just two
    slots), and subset shapes (each its own template) are all handled. Steps gain
    s['tid']. Returns templates = [{'atk': t4-list, 'rel': t4-list}, ...] or None
    when the tune has more than kmax distinct shapes (not a small-section tune)."""
    keys = {}; order = []
    for s in steps:
        k = (tuple(r for r, v in s['attack']),
             tuple(r for r, v in (s['release'] or [])))
        if k not in keys:
            keys[k] = len(order); order.append(k)
        s['tid'] = keys[k]
    if len(order) > kmax:
        return None
    def classify(seqs):
        t = []
        for i in range(len(seqs[0])):
            reg = seqs[0][i][0]
            vals = [sq[i][1] for sq in seqs]
            if len(set(vals)) == 1:
                t.append((reg, 'const', vals[0], voice_of(reg)))
            else:
                t.append((reg, 'perstep', None, voice_of(reg)))
        return t
    templates = []
    for k in order:
        members = [s for s in steps if s['tid'] == keys[k]]
        atk_t = classify([s['attack'] for s in members])
        rels = [s['release'] or [] for s in members]
        rel_t = classify(rels) if rels[0] else []
        templates.append({'atk': atk_t, 'rel': rel_t})
    return templates


GLIDE_MIN = 4                                          # min run length worth compressing


def _mark_glide_runs(steps, init, loop_to):
    """LINEAR-GLIDE detection (multi+split path): PER VOICE, a maximal run of
    >= GLIDE_MIN freq-only same-shape releaseless steps of that voice with a
    CONSTANT nonzero 16-bit freq delta. Steps of OTHER voices may interleave the
    run (simultaneous glides); a same-voice non-run step ends it. The head stays
    a normal note (pitch row + glide fx); the n members gain
    s['glide_member'] = voice — they remain ORDINARY steps (own tid / frames /
    durations) but their gliding-voice row is a REST, and the reader re-derives
    their freq from the armed glide (head_pitch + k*delta). The intermediate
    freqs are engine-generated mechanism, so they never enter the freq alphabet.
    A run never spans the loop head."""
    hi = {1: 0, 2: 0, 3: 0}; lo = {1: 0, 2: 0, 3: 0}
    FHIr = {1: 0x01, 2: 0x08, 3: 0x0f}; FLOr = {1: 0x00, 2: 0x07, 3: 0x0e}
    def upd(d):
        for vc in (1, 2, 3):
            if FHIr[vc] in d: hi[vc] = d[FHIr[vc]]
            if FLOr[vc] in d: lo[vc] = d[FLOr[vc]]
    upd(dict(init))
    # Per-voice observation chains. For each step and voice: 'cand' = the step
    # writes ONLY freq regs of that voice (other voices' / global regs in the
    # same step are fine — a two-voice [V1hi,V2hi] tick contributes to BOTH
    # chains), no release; 'brk' = the step touches the voice some other way
    # (note ctrl / timbre / its release) and breaks its chain; else the step
    # doesn't involve the voice and is skipped.
    obs = []                                           # per step: {vc: ('cand', freq16) | ('brk',)}
    for s in steps:
        d = dict(s['attack'])
        rl = dict(s['release']) if s['release'] else {}
        upd(d)
        entry = {}
        for vc in (1, 2, 3):
            aregs = [r for r in d if voice_of(r) == vc]
            rregs = [r for r in rl if voice_of(r) == vc]
            if not aregs and not rregs:
                continue
            if rregs or any(r not in FREQ for r in aregs):
                entry[vc] = ('brk',)
            else:
                entry[vc] = ('cand', (hi[vc] << 8) | lo[vc])
        obs.append(entry)
    n = len(steps)
    for vc in (1, 2, 3):
        k = 0
        while k < n:
            e = obs[k].get(vc)
            if not e or e[0] != 'cand':
                k += 1; continue
            # collect the maximal candidate stretch, then fit the staircase form
            # u_t = u0 + (t // R) * delta (R = per-level hold, 1 = plain ramp)
            idxs = [k]; vals = [e[1]]
            j = k + 1
            while j < n:
                ej = obs[j].get(vc)
                if ej is None:
                    j += 1; continue                   # step doesn't involve this voice
                if ej[0] != 'cand':
                    break
                if loop_to is not None and j == loop_to:
                    break
                idxs.append(j); vals.append(ej[1]); j += 1
            R0 = next((t for t in range(1, len(vals)) if vals[t] != vals[0]), None)
            L = 0
            if R0 is not None and R0 <= 4:
                delta = vals[R0] - vals[0]
                while L < len(vals) and vals[L] == vals[0] + (L // R0) * delta:
                    L += 1
            if L - 1 >= GLIDE_MIN - 1:
                g = {'delta': delta, 'n': L - 1}
                if R0 > 1:
                    g['hold'] = R0
                steps[idxs[0]].setdefault('glide', {})[vc] = g
                for t in idxs[1:L]:
                    steps[t].setdefault('glide_member', set()).add(vc)
                k = idxs[L - 1] + 1
            else:
                k += 1


def _song_end_writes(frames, steps):
    """The trailing SILENCE the engine emits to stop the song. When the writelog
    ends with master-vol=$00 (the tune silences itself), capture every write AFTER
    the last note step's gate-off frame — the silence sequence (mvol=0, optionally
    voice/filter zeroing) that segment() leaves out of the note steps. The engine's
    stop-routine output, the symmetric bookend of `init`. [] if the tune doesn't
    silence itself this way."""
    flat = [(r, v) for fr in frames for (c, r, v) in fr]
    if not flat or flat[-1] != (0x18, 0x00) or not steps:
        return []
    last = steps[-1]
    bnd = last.get('off_frame') or last.get('on_frame') or 0
    tail = [(r, v) for i in range(bnd + 1, len(frames)) for (c, r, v) in frames[i]]
    return tail if (tail and tail[-1] == (0x18, 0x00)) else []


MODREG = {1: 0x03, 2: 0x0a, 3: 0x11, 4: 0x16}          # free-running modulation channels:
#   1-3 = per-voice pulse-width hi ($D403/$D40A/$D411); 4 = filter cutoff hi ($D416).
#   A swept $D416 is the `default_filter` analog of the per-voice PW sweep (ledger C1) —
#   same DOF (a swept byte to a fixed reg), so channel 4 reuses the whole sweep-program
#   path. $D416 is a global-track reg, so the build_model strip (modregs) also removes it
#   from the global-track decomposition (the ledger C10 sweep-detecting lift).


def _seq_reps(seq, i, P):
    n = len(seq); r = 0
    while i + (r + 1) * P <= n and seq[i + r * P:i + (r + 1) * P] == seq[i:i + P]:
        r += 1
    return r


def _dominant_period(seq, i, maxp=16):
    """period P at position i with MAX coverage (P*repeats); ties -> smallest P."""
    n = len(seq); best = (0, 1)
    for P in range(1, min(maxp, n - i) + 1):
        cov = P * _seq_reps(seq, i, P)
        if cov > best[0]:
            best = (cov, P)
    return best[1] if best[0] else (n - i)


def _first_note_frame(frames):
    """Frame index of the first note (first gate-on). Everything before is one-time
    INIT (kept verbatim, incl. any interleaved sweep priming); the modulation sweep
    program is captured from this frame onward (the loop body)."""
    for fi, fr in enumerate(frames):
        if any(r in CTRL and (v & 1) for (c, r, v) in fr):
            return fi
    return 0


def _capture_pw_program(frames):
    """Per-voice pulse-width MODULATION captured as a sweep PROGRAM (a PWM-automation
    orderlist, ledger C1/§7): the per-tick value sequence is run-length-encoded at the
    PERIOD level into (period, repeats) sections. Returns {voice: (value_table, sections)}
    where value_table = the concatenated distinct section periods and sections =
    [(offset_into_table, period_len, repeats), ...]. The player walks it (one parametric
    sweep per section), so the USF never carries the raw per-tick trace."""
    out = {}
    nf = len(frames)
    for vc, reg in MODREG.items():
        seq = [v for fr in frames for (c, r, v) in fr if r == reg]
        if len(seq) < nf * 0.10 or len(seq) < 16:               # not heavily modulated
            continue
        tab = []; secs = []; i = 0
        while i < len(seq):
            P = _dominant_period(seq, i)
            r = max(1, _seq_reps(seq, i, P))
            period = seq[i:i + P]
            off = _find_sub(tab, period)               # reuse identical period bytes if already present
            if off is None:
                off = len(tab); tab.extend(period)
            secs.append((off, P, min(255, r)))
            i += r * P
        if len(tab) <= 255 and all(rep <= 255 for _, _, rep in secs):  # byte offsets/reps
            out[vc] = (tab, secs)
    return out


def _find_sub(tab, sub):
    """offset of `sub` as a contiguous run already in `tab`, or None."""
    n = len(sub)
    for o in range(len(tab) - n + 1):
        if tab[o:o + n] == sub:
            return o
    return None


def _emit_pw_mod_asm(em, pw_program, mod_start, mod_inc):
    """Per-tick emit of the PW sweep PROGRAM: gated to start at mod_start, ticking at the
    fractional rate (mod_inc/256 per play()), each voice walking its (section,repeat,tick)
    program independently. Labels pwm_done / pwm_go / pwa{vc} are unique per player."""
    if not pw_program:
        return
    # gate (frame >= mod_start) + fractional rate; branch-over-jmp trampoline keeps every
    # conditional branch short (the per-voice walkers below exceed the +-127 branch range).
    em('        lda framehi'); em(f'        cmp #${(mod_start >> 8) & 0xFF:02X}')
    em('        bcc pwm_skip'); em('        bne pwm_go')
    em('        lda framelo'); em(f'        cmp #${mod_start & 0xFF:02X}'); em('        bcc pwm_skip')
    em('pwm_go:')
    em('        lda pwacc'); em('        clc'); em(f'        adc #${mod_inc:02X}'); em('        sta pwacc')
    em('        bcs pwm_emit')                          # fractional rate: tick only on overflow
    em('pwm_skip:'); em('        jmp pwm_done')
    em('pwm_emit:')
    em('        inc modticklo'); em('        bne pwm_tk'); em('        inc modtickhi')   # count ticks
    em('pwm_tk:')
    for vc in sorted(pw_program):
        nsec = len(pw_program[vc][1])
        em(f'        ldx pwsec_v{vc}')
        em(f'        cpx #${nsec:02X}'); em(f'        bcs pwa{vc}')     # program done -> hold
        em(f'        lda pwsoff_v{vc},x'); em('        clc'); em(f'        adc pwtk_v{vc}'); em('        tay')
        em(f'        lda pwtab_v{vc},y'); em(f'        sta $D4{MODREG[vc]:02X}')
        em(f'        inc pwtk_v{vc}'); em(f'        lda pwtk_v{vc}'); em(f'        cmp pwslen_v{vc},x'); em(f'        bne pwa{vc}')
        em(f'        lda #$00'); em(f'        sta pwtk_v{vc}')
        em(f'        inc pwrep_v{vc}'); em(f'        lda pwrep_v{vc}'); em(f'        cmp pwsrep_v{vc},x'); em(f'        bne pwa{vc}')
        em(f'        lda #$00'); em(f'        sta pwrep_v{vc}'); em(f'        inc pwsec_v{vc}')
        em(f'pwa{vc}:')
    em('pwm_done:')


def _pw_state_bytes(pw_program):
    sb = ['pwacc', 'modticklo', 'modtickhi', 'notesdone'] if pw_program else []
    for vc in sorted(pw_program):
        sb += [f'pwsec_v{vc}', f'pwrep_v{vc}', f'pwtk_v{vc}']
    return tuple(sb)


def _mod_total_ticks(pw_program):
    """Total ticks the longest modulation channel plays (= its $D4xx write count).
    The player ticks until modtick reaches this, so a sweep that runs PAST the last
    note (e.g. a filter cutoff still sweeping after the melody ends) finishes."""
    if not pw_program:
        return 0
    return max(sum(l * r for o, l, r in secs) for tab, secs in pw_program.values())


def _emit_mod_sweep_and_tail(em, emit_pw_mod, pw_program, mod_total, song_end):
    """At pl_load, BEFORE the note firing (orig per-frame order is [sweep][note]): tick
    the modulation sweep, then if the notes are already done (notesdone, set at the last
    step instead of `done`) skip firing and keep ticking until the program is fully
    played (modtick >= mod_total), THEN emit the song-end + halt. Falls through to pl_chk
    (fire the notes) while notes remain. No-op without a program (player unchanged).
    Labels pl_thalt / pl_tnext are unique per player (emitted once)."""
    emit_pw_mod()                                      # sweep BEFORE the notes
    if not pw_program:
        return
    em('        lda notesdone'); em('        beq pl_chk')   # notes remain -> fire them
    em('        lda modtickhi'); em(f'        cmp #${(mod_total >> 8) & 0xFF:02X}')
    em('        bcc pl_tnext'); em('        bne pl_thalt')
    em('        lda modticklo'); em(f'        cmp #${mod_total & 0xFF:02X}'); em('        bcc pl_tnext')
    em('pl_thalt:')
    for _sereg, _seval in song_end:                    # emit the song-end silence, then halt
        em(f'        lda #${_seval:02X}'); em(f'        sta $D4{_sereg:02X}')
    em('        lda #$01'); em('        sta done')
    em('pl_tnext:'); em('        jmp pl_inc')           # tail: skip firing, just advance the frame


def _emit_pw_data_asm(em, pw_program):
    for vc in sorted(pw_program):
        tab, secs = pw_program[vc]
        em(f'pwtab_v{vc}: .byte ' + ', '.join(f'${v:02X}' for v in tab))
        em(f'pwsoff_v{vc}: .byte ' + ', '.join(f'${o:02X}' for o, l, r in secs))
        em(f'pwslen_v{vc}: .byte ' + ', '.join(f'${l:02X}' for o, l, r in secs))
        em(f'pwsrep_v{vc}: .byte ' + ', '.join(f'${r:02X}' for o, l, r in secs))


def build_model(sid, dur, force_split=None, min_trim=False, detect_song_end=False, detect_modulation=False,
                multi_template=False, detect_glide=False):
    """Lift to a build-ready model, or {'unsupported': reason}. Tries the unsplit
    segmentation first (consistent templates incl. consistent intra-step dup, via
    derive_template); only if that fails on a template/dup reason does it retry with
    split_dups=True (arpeggio/vibrato per-tick freq sub-steps).

    force_split (True/False) bypasses the auto-fallback and segments that way only
    — used by the verifier to retry the split variant when the unsplit model BUILDS
    but verifies wrong (the catch-up loop case auto-fallback can't see).
    min_trim keeps complete differing final steps (drops only capture-cutoff tail) —
    a best_attempt verify-fallback for play-once tunes the aggressive trim cut short.
    detect_song_end captures a trailing master-vol=$00 silence as the song-end (forces
    play-once + emits the silence) — a best_attempt fallback for false-loop fade-outs.
    detect_modulation captures free-running per-voice pulse-width sweeps (SweepEnvelope,
    ledger C1) emitted per-tick during note holds — a best_attempt fallback.
    multi_template clusters steps by exact write shape (K positional templates +
    per-step template id) — the general form of the superset+mask, for tunes whose
    step shapes have conflicting register orders / dups — a best_attempt fallback."""
    frames = capture_real(sid, dur)
    window = len(frames)
    last_write = max((i for i, fr in enumerate(frames) if fr), default=0)  # song-end signal
    # The modulation sweep is captured from the LOOP region only (frames at/after the
    # first note). The INIT region (one-time setup, before the first note) is multi-frame
    # and may interleave the sweep's first value(s) with envelope setup — those stay
    # VERBATIM in init (kept, not stripped), so the program is the loop-body sweep and the
    # init flat-matches. boundary = first-note frame.
    boundary = _first_note_frame(frames) if detect_modulation else 0
    pw_program = _capture_pw_program(frames[boundary:]) if detect_modulation else {}
    # The modulated sweep writes are reproduced parametrically by the sweep PROGRAM at
    # runtime, so STRIP them (from the LOOP region only) before segmentation (else segment
    # splits them into raw per-tick sub-steps = the no-replay trap, redundant w/ the program).
    seg_frames = frames
    mod_start_raw = 0; pw_writes = 0
    if pw_program:
        modregs = {MODREG[vc] for vc in pw_program}
        seg_frames = [([w for w in fr if w[1] not in modregs] if fi >= boundary else list(fr))
                      for fi, fr in enumerate(frames)]
        mod_start_raw = next((i for i, fr in enumerate(frames)
                              if i >= boundary and any(w[1] in modregs for w in fr)), boundary)
        vc0 = min(pw_program)
        pw_writes = sum(1 for fr in frames[boundary:] for w in fr if w[1] == MODREG[vc0])  # loop ticks
    cum_pw = None
    if pw_program:                                     # cumulative sweep-ticks per original frame
        cum_pw = [0] * (window + 1); _c = 0
        for fi, fr in enumerate(frames):
            if fi >= mod_start_raw:
                _c += sum(1 for w in fr if w[1] == MODREG[vc0])
            cum_pw[fi + 1] = _c
    def _annot(steps):
        # Annotate each step (PRE rho-scaling, so on_frame is the original frame index)
        # with its sweep-tick count, so _inject can re-time it onto the sweep's clock.
        if cum_pw is not None:
            for s in steps:
                # +1: the note's own frame may contain the sweep tick it follows (the
                # write stream is interleaved); count it so the note lands after it.
                s['on_tick'] = cum_pw[min(s['on_frame'] + 1, window)] if s['on_frame'] >= mod_start_raw else None
                s['off_tick'] = (cum_pw[min(s['off_frame'] + 1, window)]
                                 if s.get('off_frame') is not None and s['off_frame'] >= mod_start_raw else None)
        return steps
    def _inject(m):
        if isinstance(m, dict) and 'unsupported' not in m:
            rho = m.get('rho', 1.0) or 1.0
            m['pw_program'] = pw_program
            m['mod_start'] = round(mod_start_raw * rho)                  # play-frame the sweep begins
            # Fractional emit rate: the sweep ticks at the BASIC-loop rate, not 50Hz.
            # mod_inc/256 ticks per play() -> over the active window emits exactly pw_writes.
            active = max(1, round((window - mod_start_raw) * rho))
            m['mod_inc'] = min(255, max(1, round(256 * pw_writes / active))) if pw_program else 0
            if pw_program and m['mod_inc']:
                # Re-time each note onto the play-frame where the sweep reaches its
                # captured tick count -> notes and sweep share ONE clock (no drift).
                inv = 256.0 / m['mod_inc']
                for s in m['steps']:
                    if s.get('on_tick') is not None:
                        s['on_frame'] = m['mod_start'] + round(s['on_tick'] * inv)
                    if s.get('off_tick') is not None:
                        s['off_frame'] = m['mod_start'] + round(s['off_tick'] * inv)
        return m
    if force_split is not None:
        init, steps, start_frame, legato = segment(seg_frames, split_dups=force_split)
        _annot(steps)
        se = _song_end_writes(seg_frames, steps) if detect_song_end else None
        return _inject(_build_model_from_steps(sid, init, steps, legato, window, last_write, min_trim, se,
                                               multi_template, detect_glide))
    result = None
    for split_dups in (False, True):
        init, steps, start_frame, legato = segment(seg_frames, split_dups=split_dups)
        _annot(steps)
        se = _song_end_writes(seg_frames, steps) if detect_song_end else None
        result = _build_model_from_steps(sid, init, steps, legato, window, last_write, min_trim, se,
                                         multi_template, detect_glide)
        if ('unsupported' not in result or result['unsupported'] not in (
                'variable_template', 'legato_variable', 'too_few_after_trim',
                'too_few_steps', 'template_derive', 'too_many_shapes')):
            return _inject(result)
    return _inject(result)


def _build_model_from_steps(sid, init, steps, legato, window=0, last_write=0, min_trim=False, song_end=None,
                            multi_template=False, detect_glide=False):
    from pipelines.basic_program.proof_multivoice import measure_rho, _find_loop
    import struct
    if len(steps) < 2:
        return {'unsupported': 'too_few_steps'}
    multi = None
    if multi_template:
        # Light trailing trim only: drop a trailing capture-cutoff step (gated: its
        # gate-off never captured). Complete differing final sections are KEPT — a
        # different shape is just another template. min_trim keeps even the
        # releaseless tail: with split, a final glide run's gate-off may simply lie
        # past the capture window — the orig PLAYED those writes.
        if not legato and not min_trim:
            while len(steps) > 2 and steps[-1]['release'] is None:
                steps.pop()
        if len(steps) < 2:
            return {'unsupported': 'too_few_after_trim'}
        multi = _multi_templates(steps)
        if multi is None:
            return {'unsupported': 'too_many_shapes'}
        # record stride + perstep slot offsets are single bytes in the player
        _hdr = 3 if legato else 5
        _nps = max(sum(1 for e in t['atk'] if e[1] == 'perstep') +
                   sum(1 for e in t['rel'] if e[1] == 'perstep') for t in multi)
        if _hdr + _nps > 250:
            return {'unsupported': 'too_many_shapes'}
        atk_t, atk_ps, rel_t, rel_ps = [], [], [], []
        masked = False
    elif legato:
        # attack-only steps (gate set once in init). Drop trailing partial-note
        # groups, then use the per-register mask (covers consistent + rests).
        am = set(_modal([s['attack'] for s in steps]))
        while len(steps) > 2 and set(r for r, v in steps[-1]['attack']) < am:
            steps.pop()
        sup = _superset_templates(steps)
        if sup is None:
            return {'unsupported': 'legato_variable'}
        atk_t, atk_ps, rel_t, rel_ps = sup
        masked = True
    else:
        am, rm = _modal([s['attack'] for s in steps]), _modal([s['release'] for s in steps if s['release']])
        def ok(s):
            return (tuple(r for r, v in s['attack']) == am and s['release'] is not None
                    and tuple(r for r, v in s['release']) == rm)
        # Trailing-trim. DEFAULT (aggressive): drop every trailing step that differs
        # from the modal template — removes capture-cutoff partials, but also
        # over-trims a complete final section with a thinner texture (Polimus lost 93
        # real-note steps -> short). MIN_TRIM variant (a best_attempt verify-fallback,
        # never the default -> 0 regression): drop ONLY genuine capture-cutoff tail
        # (no release = gate-off never captured), KEEP complete differing final steps
        # for the masked path. Some tunes NEED the aggressive trim (their tail breaks
        # the template), so min_trim is tried only when the aggressive build is short.
        if min_trim:
            while steps and steps[-1]['release'] is None:
                steps.pop()
        else:
            while steps and not ok(steps[-1]):
                steps.pop()
        if len(steps) < 2:
            return {'unsupported': 'too_few_after_trim'}
        masked = False
        if not all(ok(s) for s in steps):
            sup = _superset_templates(steps)        # mid-song variation (rests)
            if sup is None:
                return {'unsupported': 'variable_template'}
            atk_t, atk_ps, rel_t, rel_ps = sup
            masked = True
        else:
            atk_t, atk_ps = derive_template([s['attack'] for s in steps])
            rel_t, rel_ps = derive_template([s['release'] for s in steps])
    if not multi_template and (atk_t is None or rel_t is None):
        return {'unsupported': 'template_derive'}
    # frames + durations + loop
    clk = {1: 'PAL', 2: 'NTSC', 3: 'PAL'}.get((struct.unpack('>H', open(sid,'rb').read()[118:120])[0] >> 2) & 3, 'PAL')
    sigs = [tuple(s['attack']) for s in steps]
    # Song-end detection: if the WRITELOG goes silent well before the capture window
    # ends (the last write is early), the song plays ONCE then stops — a (possibly
    # spurious) internal-phrase loop must NOT be applied or the rebuild over-emits by
    # replaying. Uses the last WRITE frame (not the last step): a tune that loops with
    # a trailing gap still has writes filling the window.
    # A trailing master-vol=$00 (the engine silences itself) is an explicit SONG-END
    # marker: the song plays ONCE then stops, so a (false) internal-phrase loop must
    # not be applied. The captured silence writes are emitted once at the halt.
    ends = (window and last_write < window * 0.85) or bool(song_end)
    intro, period = (None, None) if ends else _find_loop(sigs)
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
        if s['off_frame'] is not None:                 # legato has no release frame
            s['off_frame'] = round(s['off_frame'] * rho)
    loop_period = round(loop_period * rho)
    if multi is not None and detect_glide:
        _mark_glide_runs(steps, init, loop_to)
    return {'init': init, 'steps': steps, 'atk_template': atk_t, 'atk_ps': atk_ps,
            'rel_template': rel_t, 'rel_ps': rel_ps, 'loop_to': loop_to,
            'loop_period': loop_period, 'clock': clk, 'rho': rho, 'masked': masked,
            'legato': legato, 'song_end': list(song_end or []), 'multi': multi}

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
    song_end = model.get('song_end') or []             # trailing silence emitted once at halt
    pw_program = model.get('pw_program') or {}          # {channel: (value_table, sections)}
    mod_start = model.get('mod_start', 0)               # play-frame the sweep begins
    mod_inc = model.get('mod_inc', 0)                   # fractional tick rate (per play, /256)
    mod_total = _mod_total_ticks(pw_program)            # ticks before the sweep tail halts
    L = []; em = L.append
    def emit_pw_mod():
        _emit_pw_mod_asm(em, pw_program, mod_start, mod_inc)
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
    _emit_mod_sweep_and_tail(em, emit_pw_mod, pw_program, mod_total, song_end)   # sweep BEFORE notes + tail
    em('pl_chk:')                                       # catch-up: fire every step due this frame
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
    em('        jsr set_rel_target'); em('        lda #$01'); em('        sta phase'); em('        jmp pl_chk')
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
        if pw_program:                                  # defer halt: let the sweep tail finish
            em('        lda #$01'); em('        sta notesdone'); em('        jmp pl_inc')
        else:
            for _sereg, _seval in song_end:            # emit the song-end silence, then halt
                em(f'        lda #${_seval:02X}'); em(f'        sta $D4{_sereg:02X}')
            em('        lda #$01'); em('        sta done'); em('        jmp pl_inc')
    em('pl_setatk:'); em('        jsr set_atk_target'); em('        lda #$00'); em('        sta phase'); em('        jmp pl_chk')
    em('pl_inc:')                                       # (sweep ticks at pl_load, before notes)
    em(f'        lda {SP}'); em('        sta splo'); em(f'        lda {SP}+1'); em('        sta sphi')
    em('        inc framelo'); em('        bne pl_ret'); em('        inc framehi'); em('pl_ret:'); em('        rts')
    em('set_atk_target:'); em('        clc')
    em('        ldy #$00'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$01'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    em('set_rel_target:'); em('        clc')
    em('        ldy #$02'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$03'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    for s in (('splo', 'sphi', 'phase', 'done', 'framelo', 'framehi',
               'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi')
              + _pw_state_bytes(pw_program)):
        em(f'{s}: .byte 0')
    _emit_pw_data_asm(em, pw_program)                   # modulation sweep program tables
    em('steprecs:')
    aps, rps = model['atk_ps'], model['rel_ps']
    for s in steps:
        rec = [s['on_frame'] & 0xFF, (s['on_frame'] >> 8) & 0xFF,
               s['off_frame'] & 0xFF, (s['off_frame'] >> 8) & 0xFF]
        rec += [s['attack'][i][1] & 0xFF for i in aps]
        rec += [s['release'][i][1] & 0xFF for i in rps]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(L)

def build_player_masked(model):
    """Like build_player but with a PER-REGISTER step mask (rests / freq-inherited
    steps): each superset entry is emitted iff its mask bit is set for this step.
    Record: [atk_lo,atk_hi,rel_lo,rel_hi, <atk mask bytes>, <rel mask bytes>,
    <atk perstep vals>, <rel perstep vals>]. Mask bit i (LSB-first, byte i//8)
    = superset entry i present. perstep slot layout is the superset (fixed
    offsets); absent entries carry a dummy and aren't read."""
    init, atk_t, rel_t = model['init'], model['atk_template'], model['rel_template']
    steps = model['steps']; N = len(steps)
    aps, rps = model['atk_ps'], model['rel_ps']
    nam = (len(atk_t) + 7) // 8                          # attack mask bytes
    nrm = (len(rel_t) + 7) // 8                          # release mask bytes
    aps_base = 4 + nam + nrm                             # attack perstep base offset
    rps_base = aps_base + len(aps)
    stride = 4 + nam + nrm + len(aps) + len(rps)
    loop_to, period = model['loop_to'], model['loop_period']
    song_end = model.get('song_end') or []             # trailing silence emitted once at halt
    pw_program = model.get('pw_program') or {}          # {channel: (value_table, sections)}
    mod_start = model.get('mod_start', 0)               # play-frame the sweep begins
    mod_inc = model.get('mod_inc', 0)                   # fractional tick rate (per play, /256)
    mod_total = _mod_total_ticks(pw_program)            # ticks before the sweep tail halts
    L = []; em = L.append; sk = [0]
    def emit_pw_mod():
        _emit_pw_mod_asm(em, pw_program, mod_start, mod_inc)
    def emit_template(tmpl, mask_off0, ps_base):
        slot = 0
        for i, (reg, kind, val, voice) in enumerate(tmpl):
            em(f'        ldy #${mask_off0 + i//8:02X}'); em(f'        lda ({SP}),y')
            em(f'        and #${1 << (i % 8):02X}'); em(f'        beq sk{sk[0]}')
            if kind == 'const':
                em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
            else:
                em(f'        ldy #${ps_base + slot:02X}'); em(f'        lda ({SP}),y'); em(f'        sta $D4{reg:02X}')
            em(f'sk{sk[0]}:'); sk[0] += 1
            if kind == 'perstep':
                slot += 1
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
    _emit_mod_sweep_and_tail(em, emit_pw_mod, pw_program, mod_total, song_end)   # sweep BEFORE notes + tail
    em('pl_chk:')                                       # catch-up: fire every step due this frame
    em('        lda framehi'); em('        cmp curtgthi'); em('        bcc pl_wait'); em('        bne pl_fire')
    em('        lda framelo'); em('        cmp curtgtlo'); em('        bcs pl_fire')
    em('pl_wait:'); em('        jmp pl_inc')
    em('pl_fire:'); em('        lda phase'); em('        beq pl_attack'); em('        jmp pl_release')
    em('pl_attack:')
    emit_template(atk_t, 4, aps_base)
    em('        jsr set_rel_target'); em('        lda #$01'); em('        sta phase'); em('        jmp pl_chk')
    em('pl_release:')
    emit_template(rel_t, 4 + nam, rps_base)
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
        if pw_program:                                  # defer halt: let the sweep tail finish
            em('        lda #$01'); em('        sta notesdone'); em('        jmp pl_inc')
        else:
            for _sereg, _seval in song_end:            # emit the song-end silence, then halt
                em(f'        lda #${_seval:02X}'); em(f'        sta $D4{_sereg:02X}')
            em('        lda #$01'); em('        sta done'); em('        jmp pl_inc')
    em('pl_setatk:'); em('        jsr set_atk_target'); em('        lda #$00'); em('        sta phase'); em('        jmp pl_chk')
    em('pl_inc:')                                       # (sweep ticks at pl_load, before notes)
    em(f'        lda {SP}'); em('        sta splo'); em(f'        lda {SP}+1'); em('        sta sphi')
    em('        inc framelo'); em('        bne pl_ret'); em('        inc framehi'); em('pl_ret:'); em('        rts')
    em('set_atk_target:'); em('        clc')
    em('        ldy #$00'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$01'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    em('set_rel_target:'); em('        clc')
    em('        ldy #$02'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$03'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    for s in (('splo', 'sphi', 'phase', 'done', 'framelo', 'framehi',
               'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi')
              + _pw_state_bytes(pw_program)):
        em(f'{s}: .byte 0')
    _emit_pw_data_asm(em, pw_program)                   # per-voice PW sweep program tables
    em('steprecs:')
    a_order = [t[0] for t in atk_t]; r_order = [t[0] for t in rel_t]
    for s in steps:
        amap = dict(s['attack']); rmap = dict(s['release']) if s['release'] else {}
        rec = [s['on_frame'] & 0xFF, (s['on_frame'] >> 8) & 0xFF,
               s['off_frame'] & 0xFF, (s['off_frame'] >> 8) & 0xFF]
        rec += [(s['atk_mask'] >> (8*b)) & 0xFF for b in range(nam)]
        rec += [(s['rel_mask'] >> (8*b)) & 0xFF for b in range(nrm)]
        rec += [amap.get(reg, 0) & 0xFF for reg in aps]
        rec += [rmap.get(reg, 0) & 0xFF for reg in rps]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(L)

def build_player_legato(model):
    """1-phase player for LEGATO tunes: gate is set once in init, then each step
    only writes freq (+ any per-note timbre) — NO per-note release. Each fire emits
    the step's attack at its absolute frame, advances, and targets the next step's
    frame. Record: [on_lo, on_hi, <atk mask bytes>, <atk perstep vals>]."""
    init, atk_t = model['init'], model['atk_template']
    steps = model['steps']; N = len(steps)
    aps = model['atk_ps']
    nam = (len(atk_t) + 7) // 8
    ps_base = 2 + nam
    stride = 2 + nam + len(aps)
    loop_to, period = model['loop_to'], model['loop_period']
    song_end = model.get('song_end') or []             # trailing silence emitted once at halt
    pw_program = model.get('pw_program') or {}          # {channel: (value_table, sections)}
    mod_start = model.get('mod_start', 0)
    mod_inc = model.get('mod_inc', 0)
    mod_total = _mod_total_ticks(pw_program)            # ticks before the sweep tail halts
    L = []; em = L.append; sk = [0]
    def emit_pw_mod():
        _emit_pw_mod_asm(em, pw_program, mod_start, mod_inc)
    em(f'* = ${LOAD:04X}'); em('        jmp init'); em('        jmp play')
    em('init:')
    pi = init[1:] if init[:1] == DRIVER_PREFIX else init
    for reg, val in pi:
        em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    for s in ('done', 'framelo', 'framehi', 'loopbaselo', 'loopbasehi'):
        em(f'        sta {s}')
    em('        lda #<steprecs'); em('        sta splo'); em(f'        sta {SP}')
    em('        lda #>steprecs'); em('        sta sphi'); em(f'        sta {SP}+1')
    em('        jsr set_atk_target'); em('        rts')
    em('play:'); em('        lda done'); em('        beq pl_load'); em('        rts')
    em('pl_load:')                                       # (sweep ticks below at pl_load, before notes)
    em('        lda splo'); em(f'        sta {SP}'); em('        lda sphi'); em(f'        sta {SP}+1')
    _emit_mod_sweep_and_tail(em, emit_pw_mod, pw_program, mod_total, song_end)   # sweep BEFORE notes + tail
    em('pl_chk:')                                       # catch-up: fire every step due this frame
    em('        lda framehi'); em('        cmp curtgthi'); em('        bcc pl_wait'); em('        bne pl_fire')
    em('        lda framelo'); em('        cmp curtgtlo'); em('        bcs pl_fire')
    em('pl_wait:'); em('        jmp pl_inc')
    em('pl_fire:')
    slot = 0
    for i, (reg, kind, val, voice) in enumerate(atk_t):
        em(f'        ldy #${2 + i//8:02X}'); em(f'        lda ({SP}),y')
        em(f'        and #${1 << (i % 8):02X}'); em(f'        beq sk{sk[0]}')
        if kind == 'const':
            em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
        else:
            em(f'        ldy #${ps_base + slot:02X}'); em(f'        lda ({SP}),y'); em(f'        sta $D4{reg:02X}')
        em(f'sk{sk[0]}:'); sk[0] += 1
        if kind == 'perstep':
            slot += 1
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
        if pw_program:                                  # defer halt: let the sweep tail finish
            em('        lda #$01'); em('        sta notesdone'); em('        jmp pl_inc')
        else:
            for _sereg, _seval in song_end:            # emit the song-end silence, then halt
                em(f'        lda #${_seval:02X}'); em(f'        sta $D4{_sereg:02X}')
            em('        lda #$01'); em('        sta done'); em('        jmp pl_inc')
    em('pl_setatk:'); em('        jsr set_atk_target'); em('        jmp pl_chk')
    em('pl_inc:')
    em(f'        lda {SP}'); em('        sta splo'); em(f'        lda {SP}+1'); em('        sta sphi')
    em('        inc framelo'); em('        bne pl_ret'); em('        inc framehi'); em('pl_ret:'); em('        rts')
    em('set_atk_target:'); em('        clc')
    em('        ldy #$00'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$01'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    for s in (('splo', 'sphi', 'done', 'framelo', 'framehi',
               'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi')
              + _pw_state_bytes(pw_program)):
        em(f'{s}: .byte 0')
    _emit_pw_data_asm(em, pw_program)                   # per-voice PW sweep program tables
    em('steprecs:')
    for s in steps:
        amap = dict(s['attack'])
        rec = [s['on_frame'] & 0xFF, (s['on_frame'] >> 8) & 0xFF]
        rec += [(s['atk_mask'] >> (8*b)) & 0xFF for b in range(nam)]
        rec += [amap.get(reg, 0) & 0xFF for reg in aps]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(L)

def build_player_multi(model):
    """K-TEMPLATE player: each step record carries its template id (tid); the play
    routine dispatches to that template's straight-line emit block (const values
    inline; perstep values from the record at the template's own slot offsets).
    Gated = 2-phase (attack at on_frame, release at off_frame — an empty-release
    template emits nothing); legato = 1-phase. Reuses absolute-frame scheduling +
    rho + 16-bit step pointer + loop + the catch-up loop. Record:
    gated  [on_lo,on_hi,off_lo,off_hi,tid, <atk ps vals><rel ps vals>]
    legato [on_lo,on_hi,tid, <atk ps vals>]
    PER-TEMPLATE stride (strtab, indexed by tid) — no pad; a glide-member-heavy
    tune would otherwise blow the record table past $D000 into the IO region
    (the player then reads SID registers as record bytes and silently stops)."""
    init, steps, templates = model['init'], model['steps'], model['multi']
    legato = model['legato']
    N = len(steps); K = len(templates)
    hdr = 3 if legato else 5
    naps = [sum(1 for e in t['atk'] if e[1] == 'perstep') for t in templates]
    nrps = [sum(1 for e in t['rel'] if e[1] == 'perstep') for t in templates]
    stride_t = [hdr + na + nr for na, nr in zip(naps, nrps)]
    loop_to, period = model['loop_to'], model['loop_period']
    song_end = model.get('song_end') or []
    L = []; em = L.append

    def dispatch(tag):                                 # tid -> template block (jmp trampolines)
        em(f'        ldy #${hdr-1:02X}'); em(f'        lda ({SP}),y')
        for t in range(K):
            em(f'        cmp #${t:02X}'); em(f'        bne d{tag}{t}'); em(f'        jmp t{tag}{t}'); em(f'd{tag}{t}:')
        em(f'        jmp t{tag}0')                     # unreachable fallback

    def emit_entries(entries, ps_base, done_lbl):
        slot = 0
        for reg, kind, val, _vo in entries:
            if kind == 'const':
                em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
            else:
                em(f'        ldy #${ps_base+slot:02X}'); em(f'        lda ({SP}),y'); em(f'        sta $D4{reg:02X}')
                slot += 1
        em(f'        jmp {done_lbl}')

    em(f'* = ${LOAD:04X}'); em('        jmp init'); em('        jmp play')
    em('init:')
    pi = init[1:] if init[:1] == DRIVER_PREFIX else init
    for reg, val in pi:
        em(f'        lda #${val:02X}'); em(f'        sta $D4{reg:02X}')
    em('        lda #$00')
    for s in (('done', 'framelo', 'framehi', 'loopbaselo', 'loopbasehi') if legato else
              ('phase', 'done', 'framelo', 'framehi', 'loopbaselo', 'loopbasehi')):
        em(f'        sta {s}')
    em('        lda #<steprecs'); em('        sta splo'); em(f'        sta {SP}')
    em('        lda #>steprecs'); em('        sta sphi'); em(f'        sta {SP}+1')
    em('        jsr set_atk_target'); em('        rts')
    em('play:'); em('        lda done'); em('        beq pl_load'); em('        rts')
    em('pl_load:')
    em('        lda splo'); em(f'        sta {SP}'); em('        lda sphi'); em(f'        sta {SP}+1')
    em('pl_chk:')                                       # catch-up: fire every step due this frame
    em('        lda framehi'); em('        cmp curtgthi'); em('        bcc pl_wait'); em('        bne pl_fire')
    em('        lda framelo'); em('        cmp curtgtlo'); em('        bcs pl_fire')
    em('pl_wait:'); em('        jmp pl_inc')
    if legato:
        em('pl_fire:')
        dispatch('a')
        for t in range(K):
            em(f'ta{t}:'); emit_entries(templates[t]['atk'], hdr, 'pl_adv')
    else:
        em('pl_fire:'); em('        lda phase'); em('        beq pl_attack'); em('        jmp pl_release')
        em('pl_attack:')
        dispatch('a')
        for t in range(K):
            em(f'ta{t}:'); emit_entries(templates[t]['atk'], hdr, 'atk_done')
        em('atk_done:'); em('        jsr set_rel_target'); em('        lda #$01'); em('        sta phase'); em('        jmp pl_chk')
        em('pl_release:')
        dispatch('r')
        for t in range(K):
            em(f'tr{t}:'); emit_entries(templates[t]['rel'], hdr + naps[t], 'pl_adv')
    em('pl_adv:')
    em(f'        ldy #${hdr-1:02X}'); em(f'        lda ({SP}),y'); em('        tay')   # tid -> stride
    em('        lda strtab,y')
    em('        clc'); em(f'        adc {SP}'); em(f'        sta {SP}')
    em(f'        lda {SP}+1'); em('        adc #$00'); em(f'        sta {SP}+1')
    eoff = sum(stride_t[s['tid']] for s in steps)
    em(f'        lda {SP}'); em(f'        cmp #<(steprecs+{eoff})'); em('        bne pl_setatk')
    em(f'        lda {SP}+1'); em(f'        cmp #>(steprecs+{eoff})'); em('        bne pl_setatk')
    if loop_to is not None:
        loff = sum(stride_t[s['tid']] for s in steps[:loop_to])
        em(f'        lda #<(steprecs+{loff})'); em(f'        sta {SP}')
        em(f'        lda #>(steprecs+{loff})'); em(f'        sta {SP}+1')
        em('        clc'); em('        lda loopbaselo'); em(f'        adc #${period&0xFF:02X}'); em('        sta loopbaselo')
        em('        lda loopbasehi'); em(f'        adc #${(period>>8)&0xFF:02X}'); em('        sta loopbasehi')
    else:
        for _sereg, _seval in song_end:                # emit the song-end silence, then halt
            em(f'        lda #${_seval:02X}'); em(f'        sta $D4{_sereg:02X}')
        em('        lda #$01'); em('        sta done'); em('        jmp pl_inc')
    em('pl_setatk:'); em('        jsr set_atk_target')
    if not legato:
        em('        lda #$00'); em('        sta phase')
    em('        jmp pl_chk')
    em('pl_inc:')
    em(f'        lda {SP}'); em('        sta splo'); em(f'        lda {SP}+1'); em('        sta sphi')
    em('        inc framelo'); em('        bne pl_ret'); em('        inc framehi'); em('pl_ret:'); em('        rts')
    em('set_atk_target:'); em('        clc')
    em('        ldy #$00'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
    em('        ldy #$01'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    if not legato:
        em('set_rel_target:'); em('        clc')
        em('        ldy #$02'); em(f'        lda ({SP}),y'); em('        adc loopbaselo'); em('        sta curtgtlo')
        em('        ldy #$03'); em(f'        lda ({SP}),y'); em('        adc loopbasehi'); em('        sta curtgthi'); em('        rts')
    for s in (('splo', 'sphi', 'done', 'framelo', 'framehi',
               'loopbaselo', 'loopbasehi', 'curtgtlo', 'curtgthi')
              + (() if legato else ('phase',))):
        em(f'{s}: .byte 0')
    em('strtab: .byte ' + ', '.join(f'${st:02X}' for st in stride_t))
    em('steprecs:')
    for s in steps:
        t = s['tid']
        onf = s['on_frame']
        off = s['off_frame'] if s.get('off_frame') is not None else onf
        rec = [onf & 0xFF, (onf >> 8) & 0xFF]
        if not legato:
            rec += [off & 0xFF, (off >> 8) & 0xFF]
        rec.append(t)
        aslots = [i for i, e in enumerate(templates[t]['atk']) if e[1] == 'perstep']
        rec += [s['attack'][i][1] & 0xFF for i in aslots]
        rslots = [i for i, e in enumerate(templates[t]['rel']) if e[1] == 'perstep']
        rel = s['release'] or []
        rec += [rel[i][1] & 0xFF for i in rslots]
        em('        .byte ' + ', '.join(f'${b:02X}' for b in rec))
    return '\n'.join(L)


START_CAP = 0                                          # NO leading silence (user policy 2026-07-02):
#   every tune's first event lands at frame 0, structurally identical to the
#   other engine families' USFs (first row fires on the first play() call) —
#   uniform structure across the corpus for ML training.


def cap_start_frames(model, cap=START_CAP):
    """PURE TIME TRANSLATION: when the original's BASIC setup delay (silence
    before the first event — a "PLEASE WAIT" DATA-decode phase, engine
    bookkeeping per the init trichotomy, NOT musical content) exceeds `cap`
    frames, shift every absolute frame target down so the first step lands at
    `cap`. All RELATIVE timing (rhythm, holds, loop period, sweep clock) is
    untouched, so the emitted (reg,val) write stream is identical — the music
    just starts at once. Applied at the MODEL level, so the USF itself carries
    no dead air (user decision: no delay in the USF). m['start_shift'] records
    the removed frames so verification can compare equal MUSIC-TIME windows."""
    steps = model.get('steps') or []
    if not steps:
        return model
    first = min(s['on_frame'] for s in steps)
    if first <= cap:
        return model
    d = first - cap
    m = dict(model)
    m['steps'] = [dict(s, on_frame=s['on_frame'] - d,
                       off_frame=(s['off_frame'] - d if s.get('off_frame') is not None else None))
                  for s in steps]
    if m.get('mod_start'):
        m['mod_start'] = max(0, m['mod_start'] - d)
    m['start_shift'] = d
    return m


def read_sid_meta(sid_path):
    """(title, author, released) from the original SID header (latin-1)."""
    raw = open(sid_path, 'rb').read()
    def s(off):
        return raw[off:off + 32].split(b'\0')[0].decode('latin-1', errors='replace')
    return s(0x16), s(0x36), s(0x56)


def build_psid(model, title=None, author=None, released=None):
    title = title if title is not None else (model.get('title') or 'sidfinity')
    author = author if author is not None else (model.get('author') or 'sidfinity')
    released = released if released is not None else (model.get('released') or 'sidfinity')
    if model.get('multi'):
        asm = build_player_multi(model)
    elif model.get('legato'):
        asm = build_player_legato(model)
    elif model.get('masked'):
        asm = build_player_masked(model)
    else:
        asm = build_player(model)
    # Clock flag MUST match the original: siddump drives play() at the header's
    # rate (PAL 50Hz / NTSC 60Hz), so a PAL rebuild of an NTSC tune gets through
    # less music per second -> overlap-exact but a short (truncated-prefix) stream.
    clock_bits = {'PAL': 1, 'NTSC': 2}.get(model.get('clock'), 1)
    flags = (clock_bits << 2) | (1 << 4)               # clock bits 2-3 + 6581 (bit 4)
    body = assemble(asm)
    if LOAD + len(body) > 0xCF00:                      # image must stay below IO at $D000:
        raise ValueError('image_too_big')              # records read from IO = silent garbage
    return build_header(load=LOAD, init=LOAD, play=LOAD+3, songs=1, start_song=1,
                        speed=0, title=title, author=author, released=released,
                        flags=flags) + body

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
