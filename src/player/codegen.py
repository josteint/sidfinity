"""
codegen.py — Per-song 6502 code generator for the SIDfinity player.

Instead of a monolithic .s file with #ifdef blocks, this generates only
the code blocks a specific song needs. Each block is a small unit of
xa65 assembly with declared interfaces (inputs, outputs, dependencies).

Architecture:
  USF Song → FeatureDetector → BlockSelector → BlockSorter → AssemblyEmitter → xa65

See docs/player_codegen_plan.md for the full plan.
"""

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# Block: the fundamental unit of player code
# =============================================================================

@dataclass
class Block:
    """A unit of 6502 assembly code with declared interfaces.

    A block is a contiguous piece of assembly that provides some labels
    and may require labels from other blocks. The code generator selects
    which blocks to include based on feature flags, then sorts them for
    maximum fall-through and emits them as a single assembly string.

    The `code` field contains xa65 assembly (with -XMASM). Labels
    defined in the code should match `provides`. Labels referenced but
    not defined should be in `requires`.

    Feature flags:
    - `needs`: set of flags that must ALL be active for this block to be included.
    - `excludes`: set of flags that must ALL be inactive (anti-flags).
    - A block with empty `needs` and empty `excludes` is always included.

    Layout hints:
    - `fall_through_to`: if set, this block should be placed immediately
      before the named block so execution can fall through without a JMP.
    - `order_group`: blocks in the same group are kept together. Lower
      group numbers are emitted earlier. Within a group, fall-through
      chains are maximized.
    """
    name: str
    code: str                              # xa65 assembly source
    provides: set = field(default_factory=set)   # labels this block defines
    requires: set = field(default_factory=set)   # labels this block references externally
    needs: set = field(default_factory=set)      # feature flags required (ALL must be active)
    excludes: set = field(default_factory=set)   # feature flags that prevent inclusion
    byte_estimate: int = 0                 # estimated assembled size
    cycle_estimate: int = 0                # estimated cycles (worst-case path)
    order_group: int = 50                  # emission order group (lower = earlier)
    fall_through_to: str = ''              # name of next block in fall-through chain

    # Register interface (for Phase 3 verification)
    input_regs: dict = field(default_factory=dict)   # {'X': 'channel_offset', ...}
    output_regs: dict = field(default_factory=dict)
    sid_writes: list = field(default_factory=list)    # SID register offsets written


# =============================================================================
# Feature flags — the full set (~30 flags)
# =============================================================================

# Always-present features (cannot be disabled)
# WAVE_TABLE, PATTERN_READER, SEQUENCER, REGISTER_WRITES

# Strippable features
FILTER = 'FILTER'
EFFECTS = 'EFFECTS'              # any continuous effect (fx 0-4)
VIBRATO = 'VIBRATO'              # fx 0 (inst vibrato) + fx 4 (pattern vibrato)
PORTAMENTO = 'PORTAMENTO'        # fx 1 (up) + fx 2 (down)
TONEPORTA = 'TONEPORTA'          # fx 3
CALCULATED_SPEED = 'CALCULATED_SPEED'  # speed table entries with bit 7 set
FUNKTEMPO = 'FUNKTEMPO'          # fx $0E
WAVE_DELAY = 'WAVE_DELAY'        # wave table entries $01-$0F
WAVE_CMD = 'WAVE_CMD'            # wave table entries >= $E0
PULSE_MOD = 'PULSE_MOD'          # any pulse table modulation
TICK0_FX = 'TICK0_FX'            # any tick-0 effect handler
ORDERLIST_TRANS = 'ORDERLIST_TRANS'  # orderlist transpose
ORDERLIST_REPEAT = 'ORDERLIST_REPEAT'  # orderlist repeat markers

# Individual tick-0 FX handlers
SET_AD = 'SET_AD'                # fx 5
SET_SR = 'SET_SR'                # fx 6
SET_WAVE = 'SET_WAVE'            # fx 7
SET_WAVEPTR = 'SET_WAVEPTR'      # fx 8
SET_PULSEPTR = 'SET_PULSEPTR'    # fx 9
SET_FILTPTR = 'SET_FILTPTR'      # fx A
SET_FILTCTRL = 'SET_FILTCTRL'    # fx B
SET_FILTCUT = 'SET_FILTCUT'      # fx C
SET_MASTERVOL = 'SET_MASTERVOL'  # fx D
SET_TEMPO = 'SET_TEMPO'          # fx F

# Behavioral flags (from USF)
BUFFERED_WRITES = 'BUFFERED_WRITES'
UNBUFFERED_WRITES = 'UNBUFFERED_WRITES'
ADSR_AD_FIRST = 'ADSR_AD_FIRST'
LOADREGS_AD_FIRST = 'LOADREGS_AD_FIRST'
NEWNOTE_ALL_REGS = 'NEWNOTE_ALL_REGS'
VIBRATO_PARAM_FIX = 'VIBRATO_PARAM_FIX'
NOHR_INSTR = 'NOHR_INSTR'
LEGATO_INSTR = 'LEGATO_INSTR'


# =============================================================================
# Feature dependency lattice
# =============================================================================

# If feature A implies feature B, enabling A must also enable B.
FEATURE_IMPLIES = {
    VIBRATO: {EFFECTS},
    PORTAMENTO: {EFFECTS},
    TONEPORTA: {EFFECTS},
    CALCULATED_SPEED: {EFFECTS},
    FUNKTEMPO: {TICK0_FX},
    SET_AD: {TICK0_FX},
    SET_SR: {TICK0_FX},
    SET_WAVE: {TICK0_FX},
    SET_WAVEPTR: {TICK0_FX},
    SET_PULSEPTR: {TICK0_FX},
    SET_FILTPTR: {TICK0_FX, FILTER},
    SET_FILTCTRL: {TICK0_FX, FILTER},
    SET_FILTCUT: {TICK0_FX, FILTER},
    SET_MASTERVOL: {TICK0_FX},
    SET_TEMPO: {TICK0_FX},
    WAVE_CMD: {TICK0_FX},  # wave commands 5-F dispatch to tick0 handlers
}


def close_features(flags):
    """Compute transitive closure of feature implications.

    If VIBRATO is in flags, EFFECTS will be added (since VIBRATO implies EFFECTS).
    """
    result = set(flags)
    changed = True
    while changed:
        changed = False
        for flag in list(result):
            implied = FEATURE_IMPLIES.get(flag, set())
            if not implied.issubset(result):
                result.update(implied)
                changed = True
    return result


# =============================================================================
# Feature detector — analyzes USF Song to determine feature flags
# =============================================================================

def detect_features(song):
    """Analyze a USF Song and return the set of active feature flags.

    Args:
        song: usf.Song dataclass

    Returns:
        frozenset of feature flag strings
    """
    flags = set()

    # Instruments
    for inst in song.instruments:
        if inst.filter_ptr > 0:
            flags.add(FILTER)
        if inst.pulse_ptr > 0:
            flags.add(PULSE_MOD)
        if inst.vib_speed_idx > 0:
            flags.add(VIBRATO)

    # Tables
    if song.shared_filter_table:
        flags.add(FILTER)

    # Wave table analysis
    if song.shared_wave_table:
        for left, right in song.shared_wave_table:
            if 0x01 <= left <= 0x0F:
                flags.add(WAVE_DELAY)
            if left >= 0xE0 and left != 0xFF:
                flags.add(WAVE_CMD)

    # Speed table analysis
    if song.speed_table:
        for entry in song.speed_table:
            if entry.left & 0x80:
                flags.add(CALCULATED_SPEED)

    # Pattern commands
    fx_used = set()
    for patt in song.patterns:
        for ev in patt.events:
            if ev.command is not None:
                fx_used.add(ev.command)

    # Map FX numbers to feature flags
    fx_to_flag = {
        0: VIBRATO,  # inst vibrato reload (only if inst has vibrato)
        1: PORTAMENTO, 2: PORTAMENTO,
        3: TONEPORTA,
        4: VIBRATO,
        5: SET_AD, 6: SET_SR, 7: SET_WAVE,
        8: SET_WAVEPTR, 9: SET_PULSEPTR,
        0xA: SET_FILTPTR, 0xB: SET_FILTCTRL, 0xC: SET_FILTCUT,
        0xD: SET_MASTERVOL,
        0xE: FUNKTEMPO,
        0xF: SET_TEMPO,
    }
    for fx in fx_used:
        if fx in fx_to_flag:
            # FX 0 only matters if an instrument actually has vibrato
            if fx == 0:
                if any(i.vib_speed_idx > 0 for i in song.instruments):
                    flags.add(VIBRATO)
            else:
                flags.add(fx_to_flag[fx])

    # Orderlists
    for ol in song.orderlists:
        for pat_id, transpose in ol:
            if transpose != 0:
                flags.add(ORDERLIST_TRANS)
    # Repeat detection: check for duplicate consecutive entries
    for ol in song.orderlists:
        for i in range(len(ol) - 1):
            if ol[i] == ol[i + 1]:
                flags.add(ORDERLIST_REPEAT)
                break

    # Behavioral flags from USF song fields
    if getattr(song, 'newnote_reg_scope', 'all_regs') == 'wave_only':
        flags.add(UNBUFFERED_WRITES)
    else:
        flags.add(BUFFERED_WRITES)
    if getattr(song, 'adsr_write_order', 'sr_first') == 'ad_first':
        flags.add(ADSR_AD_FIRST)
    if getattr(song, 'loadregs_adsr_order', 'sr_first') == 'ad_first':
        flags.add(LOADREGS_AD_FIRST)
    if getattr(song, 'newnote_reg_scope', 'all_regs') == 'all_regs' and \
       getattr(song, 'adsr_write_order', 'sr_first') == 'ad_first':
        flags.add(NEWNOTE_ALL_REGS)
    if getattr(song, 'vibrato_param_fix', False):
        flags.add(VIBRATO_PARAM_FIX)

    # Instrument classification
    for inst in song.instruments:
        raw_gt = getattr(inst, '_gate_timer_raw', inst.gate_timer & 0x3F)
        if raw_gt & 0x80:
            flags.add(NOHR_INSTR)
        if raw_gt & 0x40:
            flags.add(LEGATO_INSTR)

    # Close under implications
    flags = close_features(flags)

    # Tick0 FX: if any individual tick0 handler is active, enable TICK0_FX
    tick0_handlers = {SET_AD, SET_SR, SET_WAVE, SET_WAVEPTR, SET_PULSEPTR,
                      SET_FILTPTR, SET_FILTCTRL, SET_FILTCUT, SET_MASTERVOL,
                      SET_TEMPO, FUNKTEMPO}
    if flags & tick0_handlers:
        flags.add(TICK0_FX)

    return frozenset(flags)


# =============================================================================
# Block selector
# =============================================================================

def select_blocks(blocks, features):
    """Select blocks whose feature requirements are met.

    Args:
        blocks: list of Block
        features: frozenset of active feature flags

    Returns:
        list of selected Block instances
    """
    selected = []
    for block in blocks:
        # Block needs: all must be present in features
        if block.needs and not block.needs.issubset(features):
            continue
        # Block excludes: none may be present in features
        if block.excludes and block.excludes & features:
            continue
        selected.append(block)

    # Validate: every required label must be provided by some selected block
    all_provides = set()
    for block in selected:
        all_provides.update(block.provides)
    for block in selected:
        missing = block.requires - all_provides
        if missing:
            raise ValueError(
                f"Block '{block.name}' requires labels {missing} "
                f"not provided by any selected block")

    return selected


# =============================================================================
# Block sorter — topological sort for maximum fall-through
# =============================================================================

def sort_blocks(blocks):
    """Sort blocks for maximum fall-through, respecting order_group.

    Blocks are first grouped by order_group (lower = earlier).
    Within each group, fall-through chains are built: if block A has
    fall_through_to = B.name, A is placed immediately before B.

    Returns:
        list of Block in emission order
    """
    # Build fall-through chains
    by_name = {b.name: b for b in blocks}
    # Who falls through to whom
    ft_target = {}  # name -> target name
    ft_source = {}  # target name -> source name
    for b in blocks:
        if b.fall_through_to and b.fall_through_to in by_name:
            ft_target[b.name] = b.fall_through_to
            ft_source[b.fall_through_to] = b.name

    # Build chains: find chain heads (blocks that are NOT a fall-through target)
    chain_heads = [b for b in blocks if b.name not in ft_source]

    # Build chains from heads
    chains = []
    used = set()
    for head in sorted(chain_heads, key=lambda b: (b.order_group, b.name)):
        chain = [head]
        used.add(head.name)
        current = head
        while current.name in ft_target:
            next_name = ft_target[current.name]
            if next_name in used:
                break
            next_block = by_name[next_name]
            chain.append(next_block)
            used.add(next_name)
            current = next_block
        chains.append(chain)

    # Emit chains sorted by the head's order_group
    result = []
    for chain in sorted(chains, key=lambda c: (c[0].order_group, c[0].name)):
        result.extend(chain)

    # Add any orphans (shouldn't happen if fall_through_to is consistent)
    for b in blocks:
        if b.name not in used:
            result.append(b)

    return result


# =============================================================================
# Assembly emitter
# =============================================================================

def emit_assembly(blocks, defines=None):
    """Emit the final assembly source from sorted blocks.

    Args:
        blocks: list of Block in emission order (from sort_blocks)
        defines: dict of assembler defines (name -> value), e.g. {'base': '$1000'}

    Returns:
        str: complete xa65 assembly source
    """
    lines = []

    # Header
    lines.append('; =============================================================================')
    lines.append('; SIDfinity Compact Player (generated by codegen.py)')
    lines.append('; =============================================================================')
    lines.append('')

    # Defines
    if defines:
        for name, value in defines.items():
            lines.append(f'{name:<16s} = {value}')
        lines.append('')

    # Origin
    lines.append('                * = base')
    lines.append('')

    # Emit blocks
    for block in blocks:
        lines.append(f'; ---- block: {block.name} ({block.byte_estimate} bytes est) ----')
        lines.append(block.code)
        lines.append('')

    return '\n'.join(lines)


# =============================================================================
# Test: feature detection on Covfefe
# =============================================================================

if __name__ == '__main__':
    import sys
    import os
    import json
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from gt2_to_usf import gt2_to_usf

    with open('src/player/regression_registry.json') as f:
        reg = json.load(f)

    # Test on Covfefe
    path = [e['path'] for e in reg if 'Covfefe' in e['path']][0]
    song = gt2_to_usf(path)
    features = detect_features(song)

    print(f'Covfefe features ({len(features)}):')
    for f in sorted(features):
        print(f'  {f}')
    print()

    # Show what's NOT active (potential stripping)
    all_flags = {FILTER, EFFECTS, VIBRATO, PORTAMENTO, TONEPORTA,
                 CALCULATED_SPEED, FUNKTEMPO, WAVE_DELAY, WAVE_CMD,
                 PULSE_MOD, TICK0_FX, ORDERLIST_TRANS, ORDERLIST_REPEAT,
                 SET_AD, SET_SR, SET_WAVE, SET_WAVEPTR, SET_PULSEPTR,
                 SET_FILTPTR, SET_FILTCTRL, SET_FILTCUT, SET_MASTERVOL,
                 SET_TEMPO}
    stripped = all_flags - features
    print(f'Stripped features ({len(stripped)}):')
    for f in sorted(stripped):
        print(f'  {f}')
