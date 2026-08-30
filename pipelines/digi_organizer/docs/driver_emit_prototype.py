"""Prototype: ONE universal driver emitter.

Takes the facts a driver actually contributes and emits code for them,
tracking a virtual A/X/Y so redundant loads are elided (originals hit short
cycle counts by reusing whatever is already in a register — the emitter must
be able to be at least as short as the shortest original) and padding to the
measured cycle count.
"""
CY_IMM, CY_ABS, CY_ZP = 2, 4, 3

def emit(pre, cycles_to_core, entry_off, post, tail, a_in=0x00, x_in=None, y_in=None):
    """pre/post: [(target, value)] where target is 'zp:$01' | '$d011' |
    'IRQ' | 'NMI' and value is an int or '<lbl'/'>lbl' pair marker."""
    out, cyc = [], 0
    regs = {'a': a_in, 'x': x_in, 'y': y_in}

    def put(target, val):
        nonlocal cyc
        # choose the cheapest register already holding `val`
        reg = next((r for r in 'axy' if regs[r] == val and val is not None), None)
        if reg is None:
            reg = 'a'
            out.append(f'\tlda #${val:02X}' if isinstance(val, int)
                       else f'\tlda #{val}')
            regs['a'] = val
            cyc += CY_IMM
        st = {'a': 'sta', 'x': 'stx', 'y': 'sty'}[reg]
        if target.startswith('zp:'):
            out.append(f'\t{st} {target[3:]}'); cyc += CY_ZP
        else:
            out.append(f'\t{st} {target}'); cyc += CY_ABS

    for t, v in pre:
        put(t, v)
    # pad to the measured pre-core cycle count (jsr itself is 6)
    need = cycles_to_core - cyc - 6
    if need < 0:
        return None, cyc + 6, f'OVERSHOOT by {-need} cycles'
    while need >= 2:
        if need == 3:
            out.append('\tbit $ea'); need -= 3          # 3-cycle filler
        else:
            out.append('\tnop'); need -= 2
    if need:
        return None, cyc + 6, f'UNREACHABLE residue {need}'
    out.append(f'\tjsr ${entry_off:04X}')
    cyc = cycles_to_core
    for t, v in post:
        put(t, v)
    out.append('\trts' if tail == 'rts' else 'drv_lock:\n\tjmp drv_lock')
    return '\n'.join(out) + '\n', cyc, None
