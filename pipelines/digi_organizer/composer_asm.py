"""Digi-Organizer composer — USF → 6502 → RSID.

Synthesizes the volume_4bit sample-channel player from the USF's
`digi {}` block + sample instruments + the digi voice's score. No
registry, no engine lookup (principle §8): every code byte is emitted
from these emitters, every data byte regenerated from USF + FLAC
sidecars.

CYCLE SKELETON: the verification mode for digi is CYCLE-STRICT (core
tenet Mode 2), and the host idles in psiddrv between interrupts on both
sides, so the whole write timing is determined by this generated code.
The emitters therefore mirror the canonical core's instruction SHAPES
(instruction sequence + addressing modes = the timing), while layout
and data are our own. Table low-byte placements are kept canonical
(the $92FC sample-table page cross is part of the timing).
"""
from __future__ import annotations

import os
import struct

from src.usf import parser as usf_parser
from src.usf.types import UsfFile
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header
from pipelines.hubbard.flac_io import read_sample

CORE = 0x9000
STATE_SPEEDCTR = 0x9081
STATE_ORDPOS = 0x9082
STATE_ROWPOS = 0x9083
STATE_PTRLO = 0x9084
STATE_PTRHI = 0x9085
STATE_REPEAT = 0x9086
ORDERLIST = 0x9200
SMPTAB = 0x92FC
PATTERNS = 0x9500
DRIVER = 0x9340
PCM_BASE = 0xA000

_LAYOUT_NAMES = ('CORE', 'STATE_SPEEDCTR', 'STATE_ORDPOS', 'STATE_ROWPOS',
                 'STATE_PTRLO', 'STATE_PTRHI', 'STATE_REPEAT', 'ORDERLIST',
                 'SMPTAB', 'PATTERNS', 'DRIVER')


def _layout(base: int) -> dict:
    """The canonical player layout shifted to `base` (page-aligned).

    Placement is pure layout under the core tenet, but under Mode 2 it
    must not change the CYCLE SKELETON — so the block only ever moves as
    a WHOLE, by a multiple of $100. That preserves every low byte, and
    every 6502 timing quantity that is not fixed depends only on low
    bytes: taken-branch page crossings, indexed-read page crossings (the
    $x2FC sample-table cross is deliberately canonical), and the SMC
    pointer walk. Absolute reads cost 4 cycles wherever they point.
    """
    if base & 0xFF:
        raise DigiComposeError(f'player base ${base:04X} is not page-aligned')
    sh = base - CORE
    return {n: globals()[n] + sh for n in _LAYOUT_NAMES}


class DigiComposeError(Exception):
    pass


def _byt(label, data, per_row=16):
    rows = [f'{label}:']
    for i in range(0, len(data), per_row):
        rows.append('\t.byt ' + ','.join(
            f'${b:02X}' for b in data[i:i + per_row]))
    return '\n'.join(rows) + '\n'


def _packed_blobs(usf: UsfFile, usf_dir: str):
    """The distinct PCM blobs, page-padded, largest first (a big blob
    must see the big region before smaller ones fragment it)."""
    sized = []
    for fname in sorted({si.sample for si in usf.sample_instruments}):
        smp = read_sample(os.path.join(usf_dir, fname))
        nib = [b >> 4 for b in smp.audio]
        if len(nib) % 2:
            nib.append(0)
        packed = bytes((nib[i] << 4) | nib[i + 1]
                       for i in range(0, len(nib), 2))
        if len(packed) % 256:
            packed += bytes(256 - len(packed) % 256)
        sized.append((len(packed), fname, packed))
    return sorted(sized, key=lambda t: -t[0])


def _aligned_find(data, packed):
    """Page offset (in pages) of `packed` inside `data`, or None."""
    off = data.find(packed)
    while off != -1 and off % 256:
        off = data.find(packed, off + 1)
    return None if off == -1 else off >> 8


def _tail_head(a, b):
    """Largest k such that a's last k PAGES equal b's first k pages."""
    for k in range(min(len(a), len(b)) >> 8, 0, -1):
        if a[-(k << 8):] == b[:k << 8]:
            return k
    return 0


def _cluster_blobs(blobs, join: bool):
    """Group the blobs into contiguous RUNS of memory.

    An original's sample table routinely carves SEVERAL windows out of
    ONE recording, and the .usf carries each window as its own sidecar,
    so the sharing has to be recovered CONTENT-ADDRESSEDLY. Containment
    (a blob sitting page-aligned inside another) always collapses. With
    `join`, blobs that merely OVERLAP also merge — in either direction,
    since which window was seen first is an artifact of sidecar naming,
    not of the audio. Digibeatz_2's 12 windows into one recording span
    429 pages placed separately and 216 merged; the machine has ~226.

    Byte-exactness is structural: a run only ever grows by bytes the
    overlap proved equal, so every member's window still reads back its
    own bytes. `_alloc_pcm` re-asserts that after placement.
    """
    runs = []                       # [[data, {fname: page offset}], ...]
    for _sz, fname, packed in blobs:
        for run in runs:
            off = _aligned_find(run[0], packed)
            if off is not None:
                run[1][fname] = off
                break
            if not join:
                continue
            k = _tail_head(run[0], packed)          # blob continues run
            if k:
                run[1][fname] = (len(run[0]) >> 8) - k
                run[0] = run[0] + packed[k << 8:]
                break
            k = _tail_head(packed, run[0])          # blob precedes run
            if k:
                shift = (len(packed) >> 8) - k
                run[0] = packed[:shift << 8] + run[0]
                run[1] = {f: o + shift for f, o in run[1].items()}
                run[1][fname] = 0
                break
        else:
            runs.append([packed, {fname: 0}])
    return runs


def _alloc_pcm(usf: UsfFile, usf_dir: str, regions: list, join: bool = False):
    """Place the PCM runs page-aligned, first-fit over `regions`.

    Absolute reads cost 4 cycles anywhere, so placement is pure layout;
    `regions` is [[first_page, end_page_exclusive], ...] and is consumed
    (mutated) as runs are placed.
    """
    blobs = _packed_blobs(usf, usf_dir)
    runs = _cluster_blobs(blobs, join)
    if join:                        # merging changed the sizes
        runs.sort(key=lambda r: -len(r[0]))
    blob_pages = {}
    pcm_chunks = []
    for data, members in runs:
        n_pages = len(data) >> 8
        for reg in regions:
            if reg[1] - reg[0] >= n_pages:
                page = reg[0]
                reg[0] += n_pages
                break
        else:
            raise DigiComposeError(
                f'PCM allocator: no region fits {n_pages} pages')
        pcm_chunks.append((page << 8, data))
        for fname, off in members.items():
            blob_pages[fname] = (page + off, page + off + _blob_pages(
                blobs, fname))
    # every window must read back its own bytes from where it landed
    for _sz, fname, packed in blobs:
        s, _e = blob_pages[fname]
        for addr, data in pcm_chunks:
            o = (s << 8) - addr
            if 0 <= o and o + len(packed) <= len(data):
                if data[o:o + len(packed)] != packed:
                    raise DigiComposeError(
                        f'PCM allocator: {fname} misplaced at ${s:02X}00')
                break
        else:
            raise DigiComposeError(f'PCM allocator: {fname} placed nowhere')
    return blob_pages, pcm_chunks


def _blob_pages(blobs, fname):
    for sz, f, _p in blobs:
        if f == fname:
            return sz >> 8
    raise KeyError(fname)


def _driver_pages(p: dict, raster: int, d011: int, speed: int) -> int:
    """How many pages the emitted driver occupies. MEASURED, not
    guessed: its byte length is layout-independent (every operand is
    absolute), so the canonical emission answers for any base."""
    text = _emit_driver(p, raster, d011, speed, _layout(CORE))
    stubs = ''.join(f'{n} = ${CORE + off:04X}\n' for n, off in
                    (('st1', 0x8D), ('idle_nmi', 0x100)))
    return (len(assemble(f'* = $c000\n' + stubs + text)) + 0xFF) >> 8


def _place(usf: UsfFile, usf_dir: str, drv_pages: int):
    """Choose the player base + place the PCM. Returns (base, blob_pages,
    pcm_chunks).

    Three attempts, each from a clean slate, weakest first so that every
    member that fits the ordinary map keeps its ordinary layout:

    1. CANONICAL — player at $9000, PCM below it ($1000-$8FFF), then
       $A000-$CFFF (NOT $D000+ — port=$35 maps I/O there), then under
       the KERNAL ($E000-$FEFF; the NMI vector at $FFFA bounds it).
    2. RELOCATED — the player block parked as high as RAM allows, just
       under the $D000 I/O window, so the hole below it is the largest
       single run available. Jer's Digimix_2 plays 152 CONTIGUOUS pages
       (its table carves the whole $0800-$A000 memory) and no canonical
       hole is that big.
    3. RELOCATED + JOIN, over every page the machine can spare
       ($0800 up; page $04 stays free for psiddrv, which relocates into
       the first page outside the image). Digibeatz_2's 12 windows into
       one recording need the overlap join AND that extra room: 216
       pages against the 192+31 available.

    ⚠ Where the player may live is doubly constrained, and both
    constraints are why the relocated attempts park it just under
    $D000:
      - the mirrored core init seeds the repeat counter with `sty`
        reusing Y = >idle_nmi (the original's byte-saving trick), and
        the seed must be NEGATIVE for the first order fetch to latch
        its entry's repeat. Under Mode 2 we cannot add a separate load
        — the init's cycle count IS the interrupt-grid phase — so the
        handler page must be >= $80. build_sid asserts it.
      - RSID refuses an init address in $A000-$BFFF or $D000-$FFFF (and
        a load address below $07E8) outright: the tune does not play at
        all, with no diagnostic beyond silence.
    Together those leave $8000-$9FFF and $C000-$CFFF.
    """
    # The block spans CORE..PATTERNS+patmem plus the page-aligned
    # driver, whose size is MEASURED (below) rather than guessed.
    pats = usf.subtunes[0].digi_voice.patterns
    size = ((PATTERNS - CORE) +
            32 * (max((q.id for q in pats), default=0) + 1)
            + 0xFF & ~0xFF) + (drv_pages << 8)
    hi = 0xD000 - size
    if hi < 0xC000:
        raise DigiComposeError(
            f'player block is {size >> 8} pages — no RSID-legal window '
            f'holds it (init must avoid $A/$B/$D/$E/$F pages)')
    attempts = [
        (CORE, [[0x10, 0x90], [0xA0, 0xD0], [0xE0, 0xFF]], False),
        (hi, [[0x10, hi >> 8], [0xE0, 0xFF]], False),
        (hi, [[0x08, hi >> 8], [0xE0, 0xFF]], True),
    ]
    for i, (base, regions, join) in enumerate(attempts):
        try:
            blob_pages, pcm_chunks = _alloc_pcm(usf, usf_dir, regions, join)
            return base, blob_pages, pcm_chunks
        except DigiComposeError as exc:
            if 'no region fits' not in str(exc) or i == len(attempts) - 1:
                raise


def _score_tables(usf: UsfFile, blob_pages: dict, onepage_rows=()):
    """Rebuild orderlist / pattern / sample-table bytes from USF."""
    sub = usf.subtunes[0]
    dv = sub.digi_voice
    if dv is None:
        raise DigiComposeError('subtune has no digi_voice')

    # --- sample table (id*4 entries: start, end, latch, pad) ---
    max_id = max(si.id for si in usf.sample_instruments)
    smptab = bytearray(b'\xff' * ((max_id + 1) * 4))
    for si in usf.sample_instruments:
        s, e = blob_pages[si.sample]
        if not (0 < si.rate_cycles <= 0xFF):
            raise DigiComposeError(
                f'sample_instrument {si.id}: rate_cycles '
                f'${si.rate_cycles:04X} exceeds the 8-bit TA-lo latch')
        if si.id in onepage_rows:
            # DEGENERATE one-page row: the trigger clamps end to start+1
            # through a branch, so the sample is the same single page but
            # the trigger costs 2 cycles less — a Mode-2-visible fact the
            # original states in its table and we must state in ours.
            if e - s != 1:
                raise DigiComposeError(
                    f'sample_instrument {si.id}: degenerate one-page row '
                    f'but the blob is {e - s} pages')
            e = s
        smptab[si.id * 4:si.id * 4 + 4] = bytes(
            (s, e, si.rate_cycles, 0x00))

    # --- patterns (32-byte slots; short patterns end with $FF break) ---
    pats = {p.id: p for p in dv.patterns}
    max_pat = max(pats) if pats else 0
    patmem = bytearray(32 * (max_pat + 1))
    for pid, p in pats.items():
        rows = bytearray()
        for r in p.rows:
            rows.append(r.instr.id if r.instr is not None else 0)
        if len(rows) > 32:
            raise DigiComposeError(f'pattern {pid}: {len(rows)} rows > 32')
        if len(rows) < 32:
            rows.append(0xFF)
        patmem[pid * 32:pid * 32 + len(rows)] = rows

    # --- orderlist (2-byte entries + terminator) ---
    ol = dv.orderlist
    entries = bytearray()
    for i, pat in enumerate(ol.entries):
        rep = ol.repeat_at(i)
        if not (1 <= rep <= 0x80):
            raise DigiComposeError(f'orderlist entry {i}: repeat {rep}')
        entries += bytes((pat, rep - 1))
    entries += b'\xfe' if ol.stop else b'\xff'
    if len(entries) > 0x100:
        raise DigiComposeError('orderlist exceeds 128 entries')
    if ol.loop_to not in (None, 0):
        raise DigiComposeError('engine loops to position 0 only')

    return entries, patmem, smptab


# ---------------------------------------------------------------------------
# THE DRIVER — one universal emitter, no per-member templates
# ---------------------------------------------------------------------------
# A member's driver is the startup code that arms the interrupts. Every
# musician wrote their own, but MEASURED (2026-08-30, all 39 standalone
# members) the only things a driver contributes to the $D418 write stream
# are:
#
#   * the machine STATE it establishes (screen on/off — badlines steal
#     cycles, so this is audible; which interrupt sources are live; banking;
#     where the handler lives),
#   * the CYCLE COUNT before the sample timer starts, which is the phase of
#     the sample clock against the frame clock,
#   * what the CPU does BETWEEN interrupts, as an instruction-boundary
#     PERIOD — because an NMI is taken at the end of the current
#     instruction, so the code running when it arrives sets its latency.
#
# Everything else is free. Proven by experiment: reordering the init's
# writes, and re-emitting them with different registers and opcodes at
# equal cycles, both leave a member FULL (Heavy-Beat 4249/4249, separately
# and together). So the init is synthesised however we like — it runs under
# SEI, where no interrupt can observe its shape — and only its TOTAL cycles
# and final state are reproduced.
#
# The interrupt WRAPPER is the opposite case: NMIs are non-maskable, so they
# fire while it runs and its instruction lengths ARE observable. It is
# therefore built from ordered BEHAVIOUR tokens whose instruction sequences
# follow from the tokens — a product space, not a menu. The counter-example
# that proves this half is real: replacing a member's busy-wait with an
# armed raster (same schedule, cleaner mechanism) drops Digibeatz_1 from
# FULL to match=1, because the spin is a window in which the CPU runs a
# tight 7-cycle loop. See ledger C40 and backlog item 33.

_ACK = {'asl': '\tasl $d019\n', 'inc': '\tinc $d019\n',
        'dec': '\tdec $d019\n', 'lda': '\tlda #$01\n\tsta $d019\n'}


def _emit_state(ops: str, ctx: dict) -> str:
    """Emit the code that establishes one phase of the machine state.

    The fact this reproduces is a SCHEDULE, not a total: each token carries
    the cycle at which the original performed its bus access (`token@N`),
    and the emitter pads so that ours lands on the same cycle. Matching
    only the total is not enough — Heavy-Beat's every offset agreed except
    the last, where the original reused a register (`inx`) to write $D019
    at cycle 53 while a reload put ours at 55, and that alone moved the
    whole NMI grid.

    Within that constraint the instructions are ours: X is the scratch
    register, reads go to Y, and a value already in a register is reused
    when doing so is what fits the schedule.

      AAAA=VV  write byte VV to $AAAA (a 2-digit address is zero page)
      IRQ / IRQK / NMI   install a vector pair ($FFFE, $0314, $FFFA)
      R:AAAA   read $AAAA (an interrupt acknowledge)
      AND:AAAA=MM  read-modify-write (its result depends on the
               environment, so the operation is reproduced, not a value)
      DEC:AAAA / SEI / CLI / SPD (the tick's speed immediate) / DEAD
    """
    out, t = [], 0
    regs = {'a': ctx.get('a_in', 0x00), 'x': None, 'y': None}

    def plan(tok):
        """(code, cycles before the bus access, total cycles)."""
        if tok == 'SEI':
            return '\tsei\n', 0, 2
        if tok == 'CLI':
            return '\tcli\n', 0, 2
        if tok in ('IRQ', 'IRQK', 'NMI'):
            lo, hi, lbl = {'IRQ': ('$fffe', '$ffff', 'irq_wrapper'),
                           'IRQK': ('$0314', '$0315', 'irq_wrapper'),
                           'NMI': ('$fffa', '$fffb', 'idle_nmi')}[tok]
            regs['x'] = None
            return (f'\tldx #<{lbl}\n\tstx {lo}\n'
                    f'\tldx #>{lbl}\n\tstx {hi}\n'), 8, 12
        if tok == 'SPD':
            regs['x'] = ctx['speed']
            return f"\tldx #${ctx['speed']:02X}\n\tstx st1+1\n", 2, 6
        if tok.startswith('R:'):
            regs['y'] = None
            return f'\tldy ${tok[2:]}\n', 0, 4
        if tok.startswith('AND:'):
            addr, _, mask = tok[4:].partition('=')
            regs['a'] = None
            return (f'\tlda ${addr}\n\tand #${int(mask, 16):02X}\n'
                    f'\tsta ${addr}\n'), 6, 10
        if tok.startswith('DEC:'):
            return f'\tdec ${tok[4:]}\n', 0, 6
        if tok == 'PAD2':
            return '\tnop\n', 0, 2
        if tok == 'DEAD':
            addr, v = 'drv_dead', '00'
        elif tok.startswith('S') and '=' in tok and tok[1:2].isdigit():
            addr, v = 'drv_s' + tok[1:tok.index('=')], tok.split('=')[1]
        else:
            addr, _, v = tok.partition('=')
        val = int(v, 16)
        w = 3 if len(addr) <= 2 and not addr.startswith('drv') else 4
        ref = addr if addr.startswith('drv') else '$' + addr   # label vs hex
        reg = next((r for r in 'axy' if regs[r] == val), None)
        if reg is not None:                      # already loaded: reuse it
            return ('\t%s %s\n' % ({'a': 'sta', 'x': 'stx',
                                     'y': 'sty'}[reg], ref)), 0, w
        regs['x'] = val
        return (f'\tldx #${val:02X}\n\tstx {ref}\n', 2, 2 + w, val, ref)

    # SCHEDULE the emission. Each token's bus access must land on its
    # measured cycle, and its load (if one is needed) has to fit somewhere
    # before it — which is not always the slot immediately before, because
    # originals issue several loads first and then several stores back to
    # back (Digibeatz_1 loads X and A, then stores both). So the stores are
    # pinned to their cycles first and the loads are then placed in the
    # gaps, latest-first, each in a register that is free until its store.
    toks = [x for x in ops.split(',') if x.strip()]
    plans = []
    for tok in toks:
        name, _, at = tok.partition('@')
        r = plan(name)
        code, before, cost = r[0], r[1], r[2]
        plans.append({'code': code, 'before': before, 'cost': cost,
                      'imm': r[3] if len(r) > 3 else None,
                      'ref': r[4] if len(r) > 4 else None,
                      'at': int(at) if at else None})
    slots = []                       # (start, end, code) laid out in order
    t = 0
    for pl in plans:
        target = pl['at'] if pl['at'] is not None else t + pl['before']
        start = target - pl['before']
        if start < t and pl['before'] and pl.get('imm') is not None:
            # No room for the load immediately before its store — the
            # original issued it earlier and kept it in a second register
            # (Digibeatz_1 loads X and A, then stores both). Hoist it into
            # the latest earlier gap and use A, which nothing else claims.
            for k in range(len(slots) - 1, -1, -1):
                g0, g1, gc = slots[k]
                if gc is None and g1 - g0 >= 2:
                    slots[k:k + 1] = [(g0, g1 - 2, None),
                                      (g1 - 2, g1, f"\tlda #${pl['imm']:02X}\n")]
                    pl['code'] = '\tsta %s\n' % pl['ref']
                    pl['cost'] -= 2
                    pl['before'] = 0
                    break
            else:
                raise DigiComposeError(
                    f'driver schedule: no gap to hoist the load for '
                    f'cycle {target}')
            start = target
        if start < t:
            raise DigiComposeError(
                f'driver schedule: cannot place a write at cycle {target} '
                f'(the previous one ends at {t})')
        if start > t:
            slots.append((t, start, None))          # a gap to fill
        slots.append((start, target + pl['cost'] - pl['before'], pl['code']))
        t = target + pl['cost'] - pl['before']
    for start, end, code in slots:
        out.append(code if code is not None else _pad(end - start))
    t = slots[-1][1] if slots else 0
    ctx['emitted'] = t
    return ''.join(out)


def _emit_wrapper(spec: str, ctx: dict) -> str:
    """Emit the per-interrupt wrapper from ordered BEHAVIOUR tokens.

    Unlike the init, this runs with NMIs live, so the token ORDER and the
    instruction lengths it implies are both observable:
      save / restore   push and pull A,X,Y
      ack=asl|inc|dec|lda      acknowledge the VIC interrupt
      set=AAAA:VV      re-assert a register every interrupt
      spin=NN          busy-wait until the raster reaches line $NN
      gate             run the tick only once the startup flag is set
      tick             call the sequencer
      read=AAAA        read a register (a CIA acknowledge)
      rti / jmp=AAAA   exit
    """
    out, gated = [], False
    for tok in [t for t in spec.split(',') if t.strip()]:
        if tok == 'save':
            out.append('\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n')
        elif tok == 'restore_cia':
            # the CIA acknowledge sits BETWEEN the pulls in some originals;
            # the instruction boundaries differ from doing it after, and
            # NMIs fire here, so reproduce the placement
            out.append('\tpla\n\ttay\n\tpla\n\ttax\n'
                       '\tlda $dc0d\n\tpla\n')
        elif tok == 'restore':
            out.append('\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n')
        elif tok.startswith('ack='):
            out.append(_ACK[tok[4:]])
        elif tok.startswith('set='):
            a, _, v = tok[4:].partition(':')
            out.append(f'\tlda #${int(v, 16):02X}\n\tsta ${a}\n')
        elif tok.startswith('spin='):
            out.append(f'\tlda #${int(tok[5:], 16):02X}\n'
                       'drv_spin:\n\tcmp $d012\n\tbne drv_spin\n')
        elif tok == 'gate':
            out.append('\tlda drv_s0\n\tcmp #$01\n\tbne drv_skip\n')
            gated = True
        elif tok == 'gate_beq':
            out.append('\tlda drv_s0\n\tbeq drv_skip\n')
            gated = True
        elif tok == 'tick':
            out.append(f"\tjsr ${ctx['CORE'] + 3:04X}\n")
            if gated:
                out.append('drv_skip:\n'); gated = False
        elif tok.startswith('read='):
            out.append(f'\tlda ${tok[5:]}\n')
        elif tok.startswith('pad='):
            # In the WRAPPER the instruction boundaries are observable (an
            # NMI is taken at the end of whatever is executing), so filler
            # must use the FEWEST, LONGEST instructions — two NOPs are not
            # the same as one 4-cycle BIT even though both cost 4.
            n = int(tok[4:])
            while n >= 4:
                out.append('\tbit drv_dead\n'); n -= 4
            if n == 3:
                out.append('\tbit $ea\n'); n = 0
            while n >= 2:
                out.append('\tnop\n'); n -= 2
        elif tok == 'rti':
            out.append('\trti\n')
        elif tok.startswith('jmp='):
            out.append(f'\tjmp ${tok[4:]}\n')
        else:
            raise DigiComposeError(f'unknown wrapper token {tok!r}')
    return 'irq_wrapper:\n' + ''.join(out)


def _pad(n: int) -> str:
    """Filler for exactly n cycles. NOP=2 and a 3-cycle read make every
    n >= 2 reachable, so any measured cycle count can be hit."""
    if n < 0:
        raise DigiComposeError(f'driver overshoots its cycle budget by {-n}')
    out = []
    if n % 2:
        out.append('\tbit $ea\n'); n -= 3
    while n > 0:
        out.append('\tnop\n'); n -= 2
    if n < 0:
        raise DigiComposeError('cycle budget unreachable')
    return ''.join(out)


def _cycles(asm: str) -> int:
    """Cycle cost of straight-line emitted code (no branches taken)."""
    import re as _re
    tot = 0
    for ln in asm.split('\n'):
        t = ln.strip()
        if not t or t.endswith(':') or t.startswith('.'):
            continue
        parts = t.split(None, 1)
        op, arg = parts[0], (parts[1] if len(parts) > 1 else '')
        if op in ('sei', 'cli', 'nop', 'tax', 'txa', 'tya', 'tay', 'inx', 'dex'):
            tot += 2
        elif op == 'pha':
            tot += 3
        elif op == 'pla':
            tot += 4
        elif op in ('rts', 'rti'):
            tot += 6
        elif op == 'jmp':
            tot += 3
        elif op == 'jsr':
            tot += 6
        elif op in ('lda', 'ldx', 'ldy', 'cmp', 'and', 'ora'):
            tot += 2 if arg.startswith('#') else (
                3 if _re.fullmatch(r'\$[0-9a-f]{2}', arg) else 4)
        elif op in ('sta', 'stx', 'sty'):
            tot += 3 if _re.fullmatch(r'\$[0-9a-f]{2}', arg) else 4
        elif op in ('inc', 'dec', 'asl'):
            tot += 6
        elif op == 'bit':
            tot += 3 if _re.fullmatch(r'\$[0-9a-f]{2}', arg) else 4
        elif op in ('bne', 'beq'):
            tot += 3
        else:
            raise DigiComposeError(f'cycle model: unknown op {op!r}')
    return tot


def _emit_driver(p: dict, raster: int, d011: int, speed: int,
                 L: dict) -> str:
    """THE driver — synthesised from the member's measured facts."""
    CORE = L['CORE']
    ctx = {'CORE': CORE, 'speed': speed}
    pre = _emit_state(p.get('digi_drv_pre', ''), ctx)
    pctx = dict(ctx)
    post = _emit_state(p.get('digi_drv_post', ''), pctx)
    pbudget = int(p.get('digi_drv_pcyc', 0))
    if pbudget and _cycles(post) > pbudget:
        pctx['elide'] = True
        post = _emit_state(p.get('digi_drv_post', ''), pctx)
    if pbudget:
        post += _pad(pbudget - _cycles(post))
    entry = CORE + 0x40 if p.get('digi_drv_entry') == 'core40' else CORE
    # Pad the init to the measured pre-timer cycle count. This is the whole
    # of what the init contributes: it runs under SEI, so nothing can
    # observe its shape — only when it hands over to the core.
    budget = int(p.get('digi_drv_cyc', 0))
    if budget and _cycles(pre) + 6 > budget:
        ctx['elide'] = True                # only then, buy cycles back
        pre = _emit_state(p.get('digi_drv_pre', ''), ctx)
    body = pre
    asm = ('driver_init:\n' + body + _pad(budget - _cycles(body) - 6)
           + f'\tjsr ${entry:04X}\n' + post)
    tail = p.get('digi_drv_tail', 'rts')
    # the CLI is placed by the decoded state, not by the tail
    if tail == 'lock':
        asm += 'drv_lock:\n\tjmp drv_lock\n'
    elif tail == 'rts':
        asm += '\trts\n'
    elif tail.startswith('delay='):
        # A counted startup delay that runs with interrupts LIVE, so its
        # loop PERIOD is what is observable — reproduce the structure over
        # our own counters, whose seeds the schedule already wrote.
        ids = tail[6:].split(':')
        o, c1, c2 = (f'drv_s{k}' for k in (ids + ['1', '2'])[:3])
        asm += (f'dloop:\n\tdec {o}\n\tjsr dsub\n'
                f'\tlda {o}\n\tbne dloop\n'
                '\tinc drv_s0\n\trts\n'
                f'dsub:\n\tdec {c1}\n\tlda {c1}\n\tcmp #$00\n\tbne dsub\n'
                f'dsub2:\n\tdec {c2}\n\tlda {c2}\n\tcmp #$00\n\tbne dsub2\n'
                '\trts\n')
    else:
        raise DigiComposeError(f'unknown driver tail {tail!r}')
    asm += _emit_wrapper(p.get('digi_drv_wrap', ''), ctx)
    asm += (''.join(f'drv_s{i}:\t.byt $00\n' for i in range(8))
            + 'drv_dead:\t.byt $03,$00\n'
            'drv_flag:\t.byt $00\n'
            'drv_c1:\t.byt $00\ndrv_c2:\t.byt $00\ndrv_c3:\t.byt $00\n')
    return asm



def compose_asm(usf: UsfFile, usf_dir: str) -> str:
    d = usf.digi
    if d is None or d.technique != 'volume_4bit':
        raise DigiComposeError('digi.technique volume_4bit required')
    if d.idle_level is not None:
        raise DigiComposeError(
            'idle_level not emitted by this player (Digi-Organizer '
            'writes nothing at sample end) — parametrize before use')
    sub = usf.subtunes[0]
    speed = sub.tempo - 1
    if not (0 <= speed <= 0x7F):
        raise DigiComposeError(f'tempo {sub.tempo} out of range')
    # first-row SEED for the tick immediate: with a driver speed POKE
    # the image byte (carried as init.speed_ctr_init) seeds the first
    # row; the poke then installs the steady tempo.
    seed = (usf.init.speed_ctr_init
            if usf.init and usf.init.speed_ctr_init else speed)
    mvol = (usf.init.sid.master_vol
            if usf.init and usf.init.sid and
            usf.init.sid.master_vol is not None else 0x0F)
    p = usf.params.fields if usf.params else {}
    raster = int(p.get('digi_tick_raster', 0x81))
    d011 = int(p.get('digi_tick_d011', 0x1B))
    base_latch = int(p.get('digi_base_latch', 0x70))

    drv_pages = _driver_pages(p, raster, d011, speed)
    base, blob_pages, pcm_chunks = _place(usf, usf_dir, drv_pages)
    L = _layout(base)
    CORE = L['CORE']
    STATE_SPEEDCTR, STATE_ORDPOS = L['STATE_SPEEDCTR'], L['STATE_ORDPOS']
    STATE_ROWPOS, STATE_PTRLO = L['STATE_ROWPOS'], L['STATE_PTRLO']
    STATE_PTRHI, STATE_REPEAT = L['STATE_PTRHI'], L['STATE_REPEAT']
    ORDERLIST, SMPTAB, PATTERNS = L['ORDERLIST'], L['SMPTAB'], L['PATTERNS']

    onepage = {int(t) for t in str(p.get('digi_onepage_rows', '')).split(',')
               if t.strip()}
    entries, patmem, smptab = _score_tables(usf, blob_pages, onepage)

    port_preinit = p.get('digi_port_preinit')
    a = []
    if port_preinit is None:
        a.append('\tjmp core_init\n'
                 '\tjmp seq_tick\n')
    else:
        # Port pre-init stub at the core entry, mirrored per FORM:
        # 'jmp' (Morton), 'nopslide' (fall through NOPs into core
        # init), 'romcopy' (KERNAL $E000-$FFFF copied under itself +
        # DEC $01 — ~131k pre-timer cycles, part of the grid phase).
        form = p.get('digi_preinit_form', 'jmp')
        head = ('\tjmp port_stub\n'
                '\tjmp seq_tick\n'
                f'\t.dsb ${CORE + 0x26:04X} - *, 0\n'
                'port_stub:\n'
                '\tsei\n'
                f'\tlda #${port_preinit:02X}\n'
                '\tsta $01\n')
        if form == 'jmp':
            a.append(head + '\tjmp core_init\n')
        elif form == 'nopslide':
            a.append(head + f'\t.dsb ${CORE + 0x40:04X} - *, $EA\n')
        elif form == 'romcopy':
            a.append(head +
                     '\tlda #$e0\n\tsta $21\n'
                     '\tldy #$00\n\tsty $20\n'
                     'rcp1:\n'
                     '\tlda ($20),y\n\tsta ($20),y\n'
                     '\tiny\n\tbne rcp1\n'
                     '\tinc $21\n\tbne rcp1\n'
                     '\tdec $01\n')
        else:
            raise DigiComposeError(f'unknown preinit form {form!r}')
    # --- core init (canonical $9040) ---
    a.append(f'\t.dsb ${CORE + 0x40:04X} - *, 0\n'
             'core_init:\n'
             f'\tlda #${base_latch:02X}\n'
             '\tldy #$00\n'
             '\tsta $dd04\n'
             '\tsty $dd05\n'
             '\tsty $dd06\n'
             '\tsty $dd07\n'
             '\tlda #$11\n'
             '\tsta $dd0e\n'
             '\tlda #$51\n'
             '\tsta $dd0f\n'
             '\tlda $dd0d\n'
             '\tlda #$82\n'
             '\tsta $dd0d\n'
             f'\tlda #${mvol:02X}\n'
             '\tsta $d418\n'
             '\tldy #>idle_nmi\n'          # $91 — doubles as repeat seed
             '\tsty $fffb\n'
             '\tlda #<idle_nmi\n'
             '\tsta $fffa\n'
             '\tlda #$00\n'
             f'\tsty ${STATE_REPEAT:04X}\n'
             f'\tsta ${STATE_ORDPOS:04X}\n'
             f'\tsta ${STATE_ROWPOS:04X}\n'
             '\tjsr speed_init\n'
             + {'rts': '\trts\n',
                'nop_rts': '\tnop\n\t.byt $60\n',
                'cli_rts': '\tcli\n\t.byt $60\n'}[
                   p.get('digi_core_tail', 'rts')])
    # --- sequencer tick (canonical $9087; the LDA #speed operand is
    # the one engine speed byte, read back by speed_init) ---
    a.append(f'\t.dsb ${CORE + 0x87:04X} - *, 0\n'
             'seq_tick:\n'
             f'\tdec ${STATE_SPEEDCTR:04X}\n'
             '\tbmi st1\n'
             '\trts\n'
             'st1:\n'
             f'\tlda #${seed:02X}\n'
             f'\tsta ${STATE_SPEEDCTR:04X}\n'
             f'\tlda ${STATE_ROWPOS:04X}\n'
             '\tbne rowfetch\n'
             'orderfetch:\n'
             f'\tlda ${STATE_ORDPOS:04X}\n'
             '\tasl\n'
             '\ttax\n'
             'of2:\n'
             '\tlda orderlist,x\n'
             '\ttax\n'
             '\tcpx #$fe\n'
             '\tbne of3\n'
             '\tlda #<idle_nmi\n'
             '\tsta $fffa\n'
             '\trts\n'
             'of3:\n'
             '\tcpx #$ff\n'
             '\tbne of4\n'
             '\tinx\n'
             f'\tstx ${STATE_ORDPOS:04X}\n'
             '\tjmp loopentry\n'
             'of4:\n'
             f'\tlda ${STATE_ORDPOS:04X}\n'
             '\tasl\n'
             '\ttay\n'
             '\tlda orderlist+1,y\n'
             '\tand #$7f\n'
             '\tjsr rep_latch\n'
             '\tlda #$00\n'
             f'\tsta ${STATE_PTRHI:04X}\n'
             '\ttxa\n'
             '\tasl\n'
             f'\trol ${STATE_PTRHI:04X}\n'
             '\tasl\n'
             f'\trol ${STATE_PTRHI:04X}\n'
             '\tasl\n'
             f'\trol ${STATE_PTRHI:04X}\n'
             '\tasl\n'
             f'\trol ${STATE_PTRHI:04X}\n'
             '\tasl\n'
             f'\trol ${STATE_PTRHI:04X}\n'
             '\tnop\n\tnop\n\tnop\n\tnop\n'
             f'\tsta ${STATE_PTRLO:04X}\n'
             f'\tlda ${STATE_PTRHI:04X}\n'
             '\tclc\n'
             f'\tadc #${PATTERNS >> 8:02X}\n'
             f'\tsta ${STATE_PTRHI:04X}\n'
             '\tsta rf_op+2\n'
             f'\tlda ${STATE_PTRLO:04X}\n'
             '\tsta rf_op+1\n'
             f'\tlda ${STATE_ROWPOS:04X}\n'
             'rowfetch:\n'
             '\ttax\n'
             'rf_op:\n'
             '\tlda patterns,x\n'
             '\tbne trigger\n'
             'rowadv:\n'
             f'\tinc ${STATE_ROWPOS:04X}\n'
             f'\tlda ${STATE_ROWPOS:04X}\n'
             '\tcmp #$20\n'
             '\tbcs patdone\n'
             '\trts\n'
             'patdone:\n'
             '\tlda #$00\n'
             f'\tsta ${STATE_ROWPOS:04X}\n'
             f'\tdec ${STATE_REPEAT:04X}\n'
             '\tbpl pd1\n'
             f'\tlda ${STATE_ORDPOS:04X}\n'
             '\tclc\n'
             '\tadc #$01\n'
             '\tand #$7f\n'
             f'\tsta ${STATE_ORDPOS:04X}\n'
             'pd1:\n'
             '\trts\n'
             'trigger:\n'
             '\tldy #<idle_nmi\n'
             '\tjsr rowspecial\n'
             '\tasl\n'
             '\tasl\n'
             '\ttay\n'
             '\tlda smptab,y\n'
             '\tsta hi_op+2\n'
             '\tsta lo_op+2\n'
             '\tcmp smptab+1,y\n'
             '\tbcc tg1\n'
             '\tclc\n'
             '\tadc #$01\n'
             '\tjmp tg2\n'
             'tg1:\n'
             '\tlda smptab+1,y\n'
             'tg2:\n'
             '\tsta end_cmp+1\n'
             '\tlda smptab+2,y\n'
             '\tsta $dd04\n'
             '\tlda #$00\n'
             '\tsta hi_op+1\n'
             '\tsta lo_op+1\n'
             '\tlda #<hi_nmi\n'
             '\tsta $fffa\n'
             '\tjmp rowadv\n')
    # --- NMI handlers (canonical $9157/$9160/$9181) ---
    a.append(f'\t.dsb ${CORE + 0x157:04X} - *, 0\n'
             'idle_nmi:\n'
             '\tsta idle_scr\n'
             '\tlda $dd0d\n'
             '\tlda #$02\n'          # operand byte = idle_scr target
             '\trti\n')
    a.append(f'\t.dsb ${CORE + 0x160:04X} - *, 0\n'
             'hi_nmi:\n'
             '\tsta $f8\n'
             'hi_op:\n'
             f'\tlda ${PCM_BASE:04X}\n'
             '\tlsr\n\tlsr\n\tlsr\n\tlsr\n'
             f'\tora #${d.or_mask:02X}\n'
             '\tsta $d418\n'
             '\tlda #<lo_nmi\n'
             '\tinc hi_op+1\n'
             '\tbne hn1\n'
             '\tinc hi_op+2\n'
             'hn1:\n'
             '\tsta $fffa\n'
             '\tlda $dd0d\n'
             '\tlda $f8\n'
             '\trti\n')
    a.append(f'\t.dsb ${CORE + 0x181:04X} - *, 0\n'
             'lo_nmi:\n'
             '\tsta $f8\n'
             'lo_op:\n'
             f'\tlda ${PCM_BASE:04X}\n'
             '\tand #$0f\n'
             f'\tora #${d.or_mask:02X}\n'
             '\tsta $d418\n'
             '\tinc lo_op+1\n'
             '\tbeq ln1\n'
             '\tlda #<hi_nmi\n'
             '\tsta $fffa\n'
             '\tlda $dd0d\n'
             '\tlda $f8\n'
             '\trti\n'
             'ln1:\n'
             '\tinc lo_op+2\n'
             '\tlda lo_op+2\n'
             'end_cmp:\n'
             '\tcmp #$00\n'
             '\tbcs ln2\n'
             '\tlda #<hi_nmi\n'
             '\tsta $fffa\n'
             '\tlda $dd0d\n'
             '\tlda $f8\n'
             '\trti\n'
             'ln2:\n'
             '\tlda #<idle_nmi\n'
             '\tsta $fffa\n'
             '\tlda $dd0d\n'
             '\tlda $f8\n'
             '\trti\n'
             'speed_init:\n'
             f'\tbit ${STATE_REPEAT:04X}\n'
             '\tlda st1+1\n'         # the one speed byte (code-as-data)
             f'\tsta ${STATE_SPEEDCTR:04X}\n'
             'rl1:\n'
             '\trts\n'
             'rep_latch:\n'
             '\tsta rep_imm+1\n'
             f'\tlda ${STATE_REPEAT:04X}\n'
             '\tnop\n\tnop\n'
             '\tbpl rl1\n'
             'rep_imm:\n'
             '\tlda #$02\n'
             f'\tsta ${STATE_REPEAT:04X}\n'
             'rs1:\n'
             '\trts\n'
             'rowspecial:\n'
             '\tsty $fffa\n'
             '\tcmp #$ff\n'
             '\tbne rs1\n'
             '\tpla\n'
             '\tpla\n'
             '\tjsr patdone\n'
             '\tjmp orderfetch\n'
             'loopentry:\n'
             f'\tstx ${STATE_ROWPOS:04X}\n'
             '\tjmp of2\n')
    # idle_scr = the idle handler's LDA #imm operand (mirrors the
    # original's self-scribble; the value is never read).
    a.append(f'idle_scr = ${CORE + 0x15E:04X}\n')
    # --- data + driver as address-sorted SEGMENTS (PCM may sit below
    # the player; the driver floats after the patterns) ---
    if len(smptab) > PATTERNS - SMPTAB:
        raise DigiComposeError('sample table overruns the pattern area')
    # page-align the driver: a page-crossing taken branch inside the
    # delay/wait loops costs +1 cycle per iteration (measured: the
    # poke_stub outer loop crossing a page shifted the whole stream by
    # its 11 iterations) — the originals are page-local, so are we.
    driver_addr = (PATTERNS + len(patmem) + 0xFF) & 0xFF00
    segs = [(SMPTAB, _byt('smptab', smptab)),
            (ORDERLIST, _byt('orderlist', entries)),
            (PATTERNS, _byt('patterns', patmem)),
            (driver_addr, _emit_driver(p, raster, d011, speed, L))]
    blk_end = driver_addr + (drv_pages << 8)
    for addr, packed in pcm_chunks:
        segs.append((addr, _byt(f'pcm_{addr:04X}', packed)))
        # the PCM holes were reserved around a COMPUTED player extent —
        # re-assert it here, so a layout slip is a build error and never
        # a silently overwritten sample.
        if addr < blk_end and addr + len(packed) > CORE:
            raise DigiComposeError(
                f'PCM at ${addr:04X}+{len(packed)} overlaps the player '
                f'block ${CORE:04X}-${blk_end - 1:04X}')
    core_text = '\n'.join(a)
    # KERNAL-path core variant: every NMI vector-swap targets the
    # KERNAL RAM vector $0318/$0319 instead of the hardware $FFFA/$FFFB
    # (the member keeps the KERNAL banked in; probed, all-sites).
    if p.get('digi_nmi_vec') == '0318':
        core_text = core_text.replace('$fffa', '$0318') \
                             .replace('$fffb', '$0319')
    segs.append((CORE, core_text))
    segs.sort(key=lambda x: x[0])
    out = [f'* = ${segs[0][0]:04X}\n']
    for i, (addr, text) in enumerate(segs):
        if i > 0:
            out.append(f'\t.dsb ${addr:04X} - *, 0\n')
        out.append(text)
    return '\n'.join(out)


def build_sid(usf_path: str, out_path: str) -> str:
    usf = usf_parser.parse_file(usf_path)
    usf_dir = os.path.dirname(usf_path) or '.'
    asm = compose_asm(usf, usf_dir)
    blob, labels = assemble(asm, return_labels=True)
    # Layout invariants the mirrored core encodes (see _place):
    #  - the repeat-counter seed is Y = >idle_nmi and must be NEGATIVE;
    #  - the NMI vector swap writes only the LOW byte, so all three
    #    handlers must share one page.
    if not labels['idle_nmi'] >> 8 & 0x80:
        raise DigiComposeError(
            f'player layout: idle_nmi at ${labels["idle_nmi"]:04X} gives a '
            f'POSITIVE repeat seed — the first order fetch would not latch')
    if len({labels[n] >> 8 for n in ('idle_nmi', 'hi_nmi', 'lo_nmi')}) != 1:
        raise DigiComposeError('player layout: NMI handlers span pages')
    load = int(asm.split('=', 1)[1].split('\n', 1)[0].strip().
               lstrip('$'), 16)
    # Clock is SIGNAL under Mode 2: the raster-IRQ tick runs at the
    # frame rate, so an NTSC member's stream is 60 Hz — a PAL default
    # rebuilds at 5/6 speed (perfect content prefix, wrong wall time).
    clock = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(usf.psid.sid, 0)
    h = bytearray(build_header(
        load=0, init=labels['driver_init'], play=0, songs=1,
        start_song=usf.psid.start_song, speed=0,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
        flags=(clock << 2) | (sidm << 4)))
    h[:4] = b'RSID'
    with open(out_path, 'wb') as f:
        f.write(h)
        f.write(struct.pack('<H', load))
        f.write(blob)
    return out_path
