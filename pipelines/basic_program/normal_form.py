"""basic_program USF NORMAL FORM (stage 1): order declarations replace templates.

The write model dissolves per the representation principle §4: WHAT a step writes
is derivable from row-level musical facts (note onsets, changed freq bytes, glide
ticks, instrument changes, gate conventions); the only genuinely per-tune residue
is the register ORDER per event type — carried as a few NAMED string params
(`bp_order_<sig>: "v1_fhi v1_flo v1_gate / v1_gate"`, attack / release), the C16
knob shape. Values never appear: freq comes from pitch/glide, ctrl/AD/SR/PW from
the note's instrument, $D415-18 from the global track.

Signatures are computed from READER-VISIBLE inputs only, so the writer can run
the same derivation as a SELF-CHECK: it emits the normal form only when the
derived per-step (reg,val) sequences reproduce the model exactly, else it falls
back to the template form. Ordinary verification still gates everything.
"""

FHI = {1: 0x01, 2: 0x08, 3: 0x0f}; FLO = {1: 0x00, 2: 0x07, 3: 0x0e}
CTRLS = {1: 0x04, 2: 0x0b, 3: 0x12}
TIMBRE_OFF = {2: 'pwlo', 3: 'pwhi', 5: 'ad', 6: 'sr'}
REG_TOK = {}
for _vc, _b in ((1, 0), (2, 7), (3, 14)):
    for _o, _nm in ((0, 'flo'), (1, 'fhi'), (2, 'pwlo'), (3, 'pwhi'),
                    (4, 'ctrl'), (5, 'ad'), (6, 'sr')):
        REG_TOK[_b + _o] = f'v{_vc}_{_nm}'
REG_TOK[0x15] = 'flt_lo'; REG_TOK[0x16] = 'flt_hi'  # $D415 rides the global track (cutoff_lo)
REG_TOK[0x17] = 'flt_res'; REG_TOK[0x18] = 'vol'
TOK_REG = {v: k for k, v in REG_TOK.items()}


def regs_to_decl(atk_regs, rel_regs):
    a = ' '.join(REG_TOK[r] for r in atk_regs)
    r = ' '.join(REG_TOK[r] for r in rel_regs)
    return (a + ' / ' + r) if r else a


def decl_to_regs(decl):
    a, _, r = decl.partition(' / ')
    return ([TOK_REG[t] for t in a.split()] if a.strip() else [],
            [TOK_REG[t] for t in r.split()] if r.strip() else [])


# Signature refinement features, coarsest-first preference. The writer picks
# the FIRST subset whose sig->order map is conflict-free, so keys carry only
# the flags a tune actually needs (a tune that always pokes both freq bytes
# gets plain `v1_note`; one whose releases differ gets `v1_note_norel`; ...).
# Flag markers are unique strings, so a reader lookup that generates a key
# under any subset either misses or hits the exact stored declaration.
SIG_SUBSETS = [frozenset(), frozenset({'norel'}), frozenset({'tie'}),
               frozenset({'bytes'}), frozenset({'ins'}),
               frozenset({'tie', 'norel'}), frozenset({'norel', 'bytes'}),
               frozenset({'tie', 'bytes'}), frozenset({'norel', 'ins'}),
               frozenset({'tie', 'ins'}), frozenset({'bytes', 'ins'}),
               frozenset({'tie', 'norel', 'bytes'}),
               frozenset({'tie', 'norel', 'ins'}),
               frozenset({'norel', 'bytes', 'ins'}),
               frozenset({'tie', 'bytes', 'ins'}),
               frozenset({'tie', 'norel', 'bytes', 'ins'})]


def step_sig_at(ctx, subset):
    """Signature refined by an explicit FLAG SUBSET (see SIG_SUBSETS)."""
    parts = []
    for vc in (1, 2, 3):
        e = ctx.get(vc)
        if not e:
            continue
        if e['kind'] == 'glide':
            t = 'glide'
        elif e['kind'] == 'timbre':
            t = 'setup'
        else:
            t = 'note'
            if 'bytes' in subset:
                b = ('h' if e.get('hi_ch') else '') + ('l' if e.get('lo_ch') else '')
                t += '_' + (b or 'rp')                 # rp = same-pitch re-poke
            if 'tie' in subset and e.get('tie'):
                t += '_tie'
            if 'norel' in subset and e.get('no_rel'):
                t += '_norel'
            if 'ins' in subset and e.get('instr_ch'):
                t += '_ins'
        parts.append(f'v{vc}_{t}')
    g = ctx.get('globals') or ()
    for r in g:
        parts.append({0x15: 'fcutlo', 0x16: 'fcut', 0x17: 'fres', 0x18: 'vol'}.get(r, f'g{r:02x}'))
    return '__'.join(parts) or 'none'


def step_sig(ctx):
    """Event-type signature of one step, from reader-visible facts.

    ctx per voice vc (only voices with any event this step):
      kind: 'note' | 'glide' | 'timbre' (timbre-only setup row; such rest rows
            ALWAYS carry their instrument ref, so 'timbre' has no instr_ch flag)
      hi_ch/lo_ch: which freq bytes CHANGED vs the voice's running freq
                   (note only; a same-pitch re-poke has neither)
      tie: gateless note (fx 'tie')
      instr_ch: the row carries an instrument change
      no_rel: releaseless (fx 'no_release' / glide / legato)
    plus ctx['globals']: sorted tuple of global regs written this step
    (from the global track events).
    """
    parts = []
    for vc in (1, 2, 3):
        e = ctx.get(vc)
        if not e:
            continue
        if e['kind'] == 'glide':
            t = 'g'
        elif e['kind'] == 'timbre':
            t = 'x'
        else:
            t = 'n' + ('h' if e.get('hi_ch') else '') + ('l' if e.get('lo_ch') else '')
            if t == 'n':
                t = 'n0'                               # same-pitch re-poke
            if e.get('tie'):
                t += 't'
        if e.get('instr_ch'):
            t += 'i'
        if e.get('no_rel'):
            t += 'z'
        parts.append(f'v{vc}_{t}')
    g = ctx.get('globals') or ()
    if g:
        parts.append('G' + ''.join(f'{r:02x}' for r in g))
    return '__'.join(parts) or 'none'


def entry_kind(reg):
    """Template-entry kind for a derived register (values are all musical)."""
    if reg in TOK_REG.values() and reg >= 0x15:
        return 'global'
    o = reg % 7 if reg < 0x15 else -1
    if reg < 0x15 and o in (0, 1):
        return 'perstep'                               # freq from pitch / glide
    return 'inst'                                      # ctrl/ad/sr/pw from the instrument
