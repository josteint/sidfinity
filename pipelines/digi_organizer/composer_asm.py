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


class DigiComposeError(Exception):
    pass


def _byt(label, data, per_row=16):
    rows = [f'{label}:']
    for i in range(0, len(data), per_row):
        rows.append('\t.byt ' + ','.join(
            f'${b:02X}' for b in data[i:i + per_row]))
    return '\n'.join(rows) + '\n'


def _score_tables(usf: UsfFile, usf_dir: str):
    """Rebuild orderlist / pattern / sample-table / PCM bytes from USF."""
    sub = usf.subtunes[0]
    dv = sub.digi_voice
    if dv is None:
        raise DigiComposeError('subtune has no digi_voice')

    # --- PCM blobs: FLAC sidecar → nibble stream → packed bytes.
    # Page-aligned first-fit over the FREE regions: below the player
    # ($1000-$8FFF), then $A000-$CFFF (NOT $D000+ — port=$35 maps I/O
    # there), then under the KERNAL ($E000-$FEFF; the NMI vector at
    # $FFFA bounds it). Absolute reads cost 4 cycles anywhere, so
    # placement is pure layout.
    regions = [[0x10, 0x90], [0xA0, 0xD0], [0xE0, 0xFF]]
    blob_pages = {}
    pcm_chunks = []
    # decreasing-size placement (an 80-page blob must see the big
    # region before smaller blobs fragment it)
    sized = []
    for fname in sorted({si.sample for si in usf.sample_instruments}):
        smp = read_sample(os.path.join(usf_dir, fname))
        sized.append((len(smp.audio), fname, smp))
    placed = []  # (page, packed) for overlap dedup
    for _sz, fname, smp in sorted(sized, key=lambda t: -t[0]):
        nib = [b >> 4 for b in smp.audio]
        if len(nib) % 2:
            nib.append(0)
        packed = bytes((nib[i] << 4) | nib[i + 1]
                       for i in range(0, len(nib), 2))
        if len(packed) % 256:
            packed += bytes(256 - len(packed) % 256)
        n_pages = len(packed) >> 8
        # content-addressed overlap dedup: the original's sample table
        # may carve overlapping ranges out of ONE recording — a blob
        # whose bytes sit page-aligned inside an already-placed blob
        # reuses that placement (byte-exact, no new memory).
        reused = None
        for bpage, bpacked in placed:
            off = bpacked.find(packed)
            while off != -1 and off % 256:
                off = bpacked.find(packed, off + 1)
            if off != -1:
                reused = bpage + (off >> 8)
                break
        if reused is not None:
            blob_pages[fname] = (reused, reused + n_pages)
            continue
        for reg in regions:
            if reg[1] - reg[0] >= n_pages:
                page = reg[0]
                reg[0] += n_pages
                break
        else:
            raise DigiComposeError(
                f'PCM allocator: no region fits {n_pages} pages')
        blob_pages[fname] = (page, page + n_pages)
        pcm_chunks.append((page << 8, packed))
        placed.append((page, packed))

    # --- sample table (id*4 entries: start, end, latch, pad) ---
    max_id = max(si.id for si in usf.sample_instruments)
    smptab = bytearray(b'\xff' * ((max_id + 1) * 4))
    for si in usf.sample_instruments:
        s, e = blob_pages[si.sample]
        if not (0 < si.rate_cycles <= 0xFF):
            raise DigiComposeError(
                f'sample_instrument {si.id}: rate_cycles '
                f'${si.rate_cycles:04X} exceeds the 8-bit TA-lo latch')
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

    return entries, patmem, smptab, pcm_chunks


_WRAP_ACK = ('irq_wrapper:\n'
             '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
             '\tasl $d019\n'
             f'\tjsr ${CORE + 3:04X}\n'
             '\tlda $dc0d\n'
             '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')

_WRAP_NOACK = ('irq_wrapper:\n'
               '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
               '\tasl $d019\n'
               f'\tjsr ${CORE + 3:04X}\n'
               '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')

_WRAP_INC = ('irq_wrapper:\n'
             '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
             '\tinc $d019\n'
             f'\tjsr ${CORE + 3:04X}\n'
             '\tlda $dc0d\n'
             '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')


def _emit_driver(p: dict, raster: int, d011: int, speed: int) -> str:
    """The standalone driver, mirrored per CLASS (extract's registry).
    Instruction shapes = the cycle skeleton; operands are ours."""
    cls = p.get('digi_driver', 'irq_vec')
    if cls == 'irq_vec':
        return ('driver_init:\n'
                '\tsei\n'
                '\tlda #$35\n\tsta $01\n'
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$81\n\tsta $dc0d\n\tlda $dc0d\n'
                f'\tlda #${raster:02X}\n\tsta $d012\n'
                f'\tlda #${d011:02X}\n\tsta $d011\n'
                '\tldx #$00\n\tstx $dc0e\n\tinx\n'
                '\tstx $d01a\n\tstx $d019\n'
                '\tlda #$00\n'
                f'\tjsr ${CORE:04X}\n'
                '\tcli\n\trts\n' + _WRAP_ACK)
    if cls == 'nmi_first':
        sei = '\tsei\n' if p.get('digi_driver_sei', True) else ''
        entry = (CORE + 0x40 if p.get('digi_core_entry') == 'core40'
                 else CORE)
        return ('driver_init:\n' + sei +
                '\tlda #$35\n\tsta $01\n'
                '\tlda #>idle_nmi\n\tsta $fffb\n'
                '\tlda #<idle_nmi\n\tsta $fffa\n'
                '\tlda #$00\n'
                f'\tjsr ${entry:04X}\n'
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$81\n\tsta $dc0d\n\tlda $dc0d\n'
                f'\tlda #${raster:02X}\n\tsta $d012\n'
                f'\tlda #${d011:02X}\n\tsta $d011\n'
                '\tldx #$00\n\tstx $dc0e\n\tinx\n'
                '\tstx $d01a\n\tstx $d019\n'
                '\tcli\n\trts\n' + _WRAP_NOACK)
    if cls == 'xreg':
        bit = '\tbit irq_wrapper\n' if p.get('digi_driver_bit') else ''
        wrap = _WRAP_INC
        if p.get('digi_driver_bit'):
            wrap = _WRAP_INC.replace(
                f'\tjsr ${CORE + 3:04X}\n',
                f'\tbit irq_wrapper\n\tjsr ${CORE + 3:04X}\n')
        entry = (CORE + 0x40 if p.get('digi_core_entry') == 'core40'
                 else CORE)
        return ('driver_init:\n'
                '\tsei\n'
                '\tldx #$35\n\tstx $01\n'
                f'\tldx #${raster:02X}\n\tstx $d012\n'
                '\tstx $dc0d\n\tstx $dd0d\n'
                '\tldx $dc0d\n\tldx $dd0d\n'
                '\tldx #$01\n\tstx $d019\n\tstx $d01a\n'
                '\tsta $dc0e\n'
                f'\tlda #${d011:02X}\n\tsta $d011\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                + bit +
                f'\tjsr ${entry:04X}\n'
                '\tcli\n\trts\n' + wrap)
    if cls == 'bare_stub':
        nop = '\tnop\n' if p.get('digi_driver_nop') else ''
        wrap = _WRAP_ACK
        if p.get('digi_driver_wrap_nops'):
            wrap = _WRAP_ACK.replace(
                f'\tjsr ${CORE + 3:04X}\n',
                f'\tjsr ${CORE + 3:04X}\n\tnop\n\tnop\n\tnop\n')
        return ('driver_init:\n'
                '\tlda #$00\n'
                f'\tjsr ${CORE:04X}\n'
                '\tjmp drv_l\n'
                'drv_l:\n' + nop +
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$7f\n\tsta $dc0d\n'
                '\tlda #$01\n\tsta $d01a\n'
                '\tlda $dc0d\n'
                '\tcli\n\trts\n' + wrap)
    if cls == 'jer_lock':
        # SEI, port, A/X vector pair, D01A=1 + $DC0D=$01, $D011
        # read-AND-$7F writeback (env-relative — cancels), raster,
        # JSR core+$40, 14 NOPs, CLI, JMP-self LOCK (never returns).
        return ('driver_init:\n'
                '\tsei\n'
                '\tlda #$35\n\tsta $01\n'
                '\tlda #<irq_wrapper\n\tldx #>irq_wrapper\n'
                '\tsta $fffe\n\tstx $ffff\n'
                '\tlda #$01\n\tsta $d01a\n\tsta $dc0d\n'
                '\tlda $d011\n\tand #$7f\n\tsta $d011\n'
                f'\tlda #${raster:02X}\n\tsta $d012\n'
                f'\tjsr ${CORE + 0x40:04X}\n'
                + '\tnop\n' * 14 +
                '\tcli\n'
                'drv_lock:\n'
                '\tjmp drv_lock\n'
                'irq_wrapper:\n'
                '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
                '\tinc $d019\n'
                f'\tjsr ${CORE + 3:04X}\n'
                '\tpla\n\ttay\n\tpla\n\ttax\n'
                '\tlda $dc0d\n'
                '\tpla\n\trti\n')
    if cls == 'sphere':
        # Wrapper re-writes $D011 + raster EVERY IRQ; push order
        # Y-then-X, restore X-then-Y; $D011 primed AFTER core init.
        d011_init = int(p.get('digi_d011_init', d011))
        return ('driver_init:\n'
                '\tsei\n'
                '\tlda #$35\n\tsta $01\n'
                '\tlda #$7f\n\tsta $dc0d\n'
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$01\n\tsta $d01a\n'
                '\tlda #$00\n\tldx #$00\n\tldy #$00\n'
                f'\tjsr ${CORE + 0x40:04X}\n'
                f'\tlda #${d011_init:02X}\n\tsta $d011\n'
                '\tcli\n\trts\n'
                'irq_wrapper:\n'
                '\tpha\n\ttya\n\tpha\n\ttxa\n\tpha\n'
                '\tinc $d019\n'
                f'\tlda #${d011:02X}\n\tsta $d011\n'
                f'\tlda #${raster:02X}\n\tsta $d012\n'
                f'\tjsr ${CORE + 3:04X}\n'
                '\tlda $dc0d\n'
                '\tpla\n\ttax\n\tpla\n\ttay\n\tpla\n\trti\n')
    if cls == 'earbleed':
        return ('driver_init:\n'
                '\tsei\n'
                '\tlda #$35\n\tsta $01\n'
                f'\tlda #${d011:02X}\n\tsta $d011\n'
                f'\tlda #${raster:02X}\n\tsta $d012\n'
                '\tlda #$01\n\tsta $d01a\n\tsta $d019\n'
                '\tlda #$7f\n\tsta $dc0d\n\tlda $dc0d\n'
                '\tlda #$00\n\tsta $dc0e\n'
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$00\n'
                f'\tjsr ${CORE:04X}\n'
                '\tcli\n\trts\n'
                'irq_wrapper:\n'
                '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
                '\tinc $d019\n'
                f'\tjsr ${CORE + 3:04X}\n'
                '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')
    if cls == 'poke_stub':
        # The delayed Morton shape: flag-gated wrapper + a ~2-frame
        # busy-wait after CLI before the sequencer unlocks; optional
        # runtime SPEED POKE into the tick immediate (the image byte
        # is only the first-row seed).
        dseed = int(p.get('digi_delay_seed', 0xD0))
        oseed = int(p.get('digi_delay_outer', 0x0B))
        lead = '\tsei\n' if p.get('digi_driver_tail_sei', True) else '\tnop\n'
        gate = p.get('digi_driver_gate', 'cmp1')
        has_poke = bool(p.get('digi_speed_poke_present'))
        poke = ('\tlda spdval\n\tsta st1+1\n' if has_poke else '')
        if gate == 'cmp1':
            wrap = ('irq_wrapper:\n'
                    '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
                    '\tlda dflag\n\tcmp #$01\n\tbne dwskip\n'
                    f'\tjsr ${CORE + 3:04X}\n'
                    'dwskip:\n'
                    '\tasl $d019\n'
                    '\tlda $dc0d\n'
                    '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')
        elif gate == 'ackfirst_beq':
            wrap = ('irq_wrapper:\n'
                    '\tpha\n\ttxa\n\tpha\n\ttya\n\tpha\n'
                    '\tasl $d019\n'
                    '\tlda dflag\n\tbeq dwskip\n'
                    f'\tjsr ${CORE + 3:04X}\n'
                    'dwskip:\n'
                    '\tlda $dc0d\n'
                    '\tpla\n\ttay\n\tpla\n\ttax\n\tpla\n\trti\n')
        else:
            raise DigiComposeError(f'unknown poke_stub gate {gate!r}')
        return ('driver_init:\n'
                '\tlda #$00\n\tsta dflag\n'
                f'\tjsr ${CORE:04X}\n'
                f'\tlda #${dseed:02X}\n\tsta dcnt1\n\tsta dcnt2\n'
                f'\tlda #${oseed:02X}\n\tsta docnt\n'
                + poke +
                '\tjmp ptail\n'
                'ptail:\n' + lead +
                '\tlda #<irq_wrapper\n\tsta $fffe\n'
                '\tlda #>irq_wrapper\n\tsta $ffff\n'
                '\tlda #$7f\n\tsta $dc0d\n'
                '\tlda #$01\n\tsta $d01a\n'
                '\tlda $dc0d\n'
                '\tcli\n'
                'dloop:\n'
                '\tdec docnt\n'
                '\tjsr dsub\n'
                '\tlda docnt\n'
                '\tbne dloop\n'
                '\tinc dflag\n'
                '\trts\n'
                'dsub:\n'
                '\tdec dcnt1\n'
                '\tlda dcnt1\n'
                '\tcmp #$00\n'
                '\tbne dsub\n'
                'dsub2:\n'
                '\tdec dcnt2\n'
                '\tlda dcnt2\n'
                '\tcmp #$00\n'
                '\tbne dsub2\n'
                '\trts\n'
                + wrap +
                'dflag:\t.byt $00\n'
                'docnt:\t.byt $00\n'
                'dcnt1:\t.byt $00\n'
                'dcnt2:\t.byt $00\n'
                + (f'spdval:\t.byt ${speed:02X}\n'
                   if has_poke else ''))
    raise DigiComposeError(f'unknown digi_driver class {cls!r}')


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

    entries, patmem, smptab, pcm_chunks = _score_tables(usf, usf_dir)

    port_preinit = p.get('digi_port_preinit')
    a = []
    if port_preinit is None:
        a.append('\tjmp core_init\n'
                 '\tjmp seq_tick\n')
    else:
        # Morton-variant port pre-init: the core entry routes through
        # `SEI / LDA #port / STA $01 / JMP core_init` (cycle-identical
        # to the original's stub at core+$26).
        a.append('\tjmp port_stub\n'
                 '\tjmp seq_tick\n'
                 f'\t.dsb ${CORE + 0x26:04X} - *, 0\n'
                 'port_stub:\n'
                 '\tsei\n'
                 f'\tlda #${port_preinit:02X}\n'
                 '\tsta $01\n'
                 '\tjmp core_init\n')
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
            (driver_addr, _emit_driver(p, raster, d011, speed))]
    for addr, packed in pcm_chunks:
        segs.append((addr, _byt(f'pcm_{addr:04X}', packed)))
    core_text = '\n'.join(a)
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
    load = int(asm.split('=', 1)[1].split('\n', 1)[0].strip().
               lstrip('$'), 16)
    h = bytearray(build_header(
        load=0, init=labels['driver_init'], play=0, songs=1,
        start_song=usf.psid.start_song, speed=0,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released))
    h[:4] = b'RSID'
    with open(out_path, 'wb') as f:
        f.write(h)
        f.write(struct.pack('<H', load))
        f.write(blob)
    return out_path
