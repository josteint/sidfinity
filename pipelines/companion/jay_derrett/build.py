"""Clean xa65 composer for Jay_Derrett SIDs.

Phase 2 deliverable: emit clean asm + freshly-laid-out data for a
Jay_Derrett SID, producing byte-exact SID writes against the orig.

The engine logic is rewritten cleanly (not verbatim packed). Data
tables (freq lo/hi, sub-jump table, instrument sources + programs,
voice pattern bytes) are inlined from the orig SID body — these
ARE the SID's musical content, not the engine mechanism.

Iteration 1: Ninja_Hamster only (1 subtune, direct play, smallest
layout). Other Type A dispatch shapes added in subsequent iterations.

The emitted layout uses a configurable base load address (default
$1000). The composer is parametric over the EngineParams (defined
in emulator.py) — the parameters describe the orig binary's
addresses for extraction; the composer uses fresh chosen addresses
for its own layout.
"""

from __future__ import annotations

import json
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pipelines.companion.jay_derrett.emulator import (
    JayDerrettEmulator, NINJA_HAMSTER, EngineParams,
)

ROOT = Path(__file__).resolve().parents[3]
XA = str(ROOT / 'tools' / 'xa65' / 'xa' / 'xa')


# ---------------------------------------------------------------------------
# Extraction helpers — pull data from the orig SID's memory image
# ---------------------------------------------------------------------------

@dataclass
class ExtractedData:
    """Data extracted from orig SID (the musical content)."""
    freq_lo: bytes        # 256 bytes (covers note + $10 wraparound)
    freq_hi: bytes        # 256 bytes
    sub_jump_table: bytes # 20 bytes (10 entries × 2)
    voice_offsets: bytes  # 3 bytes (0, 7, 14)
    inst_src_table: bytes # 19 × 2 = 38 bytes (src addr lo/hi pairs)
    inst_programs: list[bytes]  # 19 × 24-byte programs
    voice_patterns: list[bytes]  # 3 byte-streams
    voice_initial_offsets: tuple[int, int, int]  # ptr offset into v's pattern
    initial_tempo: int
    initial_master_vol: int
    # PSID metadata
    title: str
    author: str
    released: str
    # Captured orig init state — emitted as init-time data in the reb.
    # 78 bytes (3 voices × 26-byte stride). None means "use zeros".
    init_voice_state: bytes | None = None


def _libsidplayfp_powerup_byte(addr: int) -> int:
    """Compute the libsidplayfp powerup pattern byte at `addr`.
    Mirrors SystemRAMBank::reset(). Used to determine engine-mechanism
    quirks where the engine reads an uninitialised cell."""
    # Determine bank's initial fill byte
    bank = addr >> 14   # 0, 1, 2, 3 for the four $4000-byte banks
    fill = 0xFF if bank in (1, 3) else 0x00
    overlay = fill ^ 0xFF
    # Within each 8-byte block: offset 0..1 = fill, 2..5 = overlay, 6..7 = fill
    off8 = addr & 7
    if off8 in (2, 3, 4, 5):
        return overlay
    return fill


def _run_init_for_extract(sid_path: str, params: EngineParams,
                          subtune: int = 0) -> bytearray:
    """Run orig init via py65 with libsidplayfp powerup RAM; return
    the full RAM image. Used by extract_data to read pattern data
    that init COPIES from body to per-voice RAM regions (Mandroid)."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = subtune
    mpu.x = 0; mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = params.init_addr
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    return bytearray(mpu.memory)


def detect_mod_base(sid_path: str, params: EngineParams) -> int:
    """Scan orig binary for the slide-update pattern
    `B9 LL HH 18 79 ?? ?? 99 LL HH` (LDA abs,Y / CLC / ADC abs,Y /
    STA abs,Y at the SAME address). The repeated address is the
    freq-lo-accumulator slot. mod_base = that addr - 1, since freq
    lo lives at offset +1 in all known Jay_Derrett slab variants.

    This is the address engine USES for voice_state slot reads,
    NOT the instrument-loader copy destination (which may differ
    in engines like Lifeforce/Mandroid where the copy lands at a
    stride offset from the modulation base).

    Universal across all slab variants because slide-update logic
    is structurally identical (always LDA-CLC-ADC-STA on the same
    accumulator)."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    body_end = load + len(body)
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    for addr in range(load, body_end - 10):
        if (mem[addr] == 0xB9 and mem[addr+3] == 0x18 and
            mem[addr+4] == 0x79 and mem[addr+7] == 0x99 and
            mem[addr+1] == mem[addr+8] and mem[addr+2] == mem[addr+9]):
            slot = mem[addr+1] | (mem[addr+2] << 8)
            return slot - 1
    raise RuntimeError(f'No slide-update pattern in {sid_path}')


def detect_voice_state_base(sid_path: str, params: EngineParams) -> int:
    """DEPRECATED: returned copy destination, which differs from
    modulation base in many engines. Use detect_mod_base instead.
    Kept for backwards compatibility."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    candidates = []
    for addr in range(load, load + len(body) - 9):
        if (mem[addr] == 0xB9 and mem[addr+3] == 0x99 and
            mem[addr+6] == 0x88 and mem[addr+7] == 0x10 and
            mem[addr+8] == 0xF7):
            dst = mem[addr+4] | (mem[addr+5] << 8)
            distance = abs(addr - params.proc_note_addr)
            candidates.append((distance, dst))
    if not candidates:
        raise RuntimeError(f'No voice_state base found in {sid_path}')
    candidates.sort()
    return candidates[0][1]


def detect_set_dur_clears_v3(sid_path: str) -> bool:
    """Detect engines whose SET DUR ($82 N) handler ALSO clears V3
    CTRL slots. Pattern: TWO `A9 00 8D LO HI 8D LO+3 HI 4C` blocks
    in proc_note (one for wrap, one for SET DUR). Engines with only
    ONE such block (NH) don't do the SET DUR clear."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    count = 0
    for addr in range(load, load + len(body) - 11):
        if (mem[addr] == 0xA9 and mem[addr+1] == 0x00 and mem[addr+2] == 0x8D
            and mem[addr+5] == 0x8D and mem[addr+8] == 0x4C
            and mem[addr+6] == mem[addr+3] + 3):
            count += 1
    return count >= 2


def detect_pwm_phase_base(sid_path: str, params: EngineParams) -> int:
    """Scan orig binary for the PWM phase check: `BD LL HH D0 ??`
    (LDA $XXXX,X / BNE phase1) where the LDA reads the per-voice
    phase cell. Returns the LDA's operand (PWM phase base address).

    The phase cell is indexed by X = voice idx (0/1/2), so values
    at base, base+1, base+2 give V0/V1/V2 phase states (0 = phase 0,
    non-zero = phase 1)."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    body_end = load + len(body)
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    # Scan for `BD LL HH D0 ??` near proc_note
    candidates = []
    for addr in range(load, body_end - 5):
        if mem[addr] == 0xBD and mem[addr + 3] == 0xD0:
            a = mem[addr + 1] | (mem[addr + 2] << 8)
            # Filter: state-cell-like address (not in inst src table etc.)
            distance = abs(addr - params.proc_note_addr)
            candidates.append((distance, a))
    if not candidates:
        raise RuntimeError(f'No PWM phase base found in {sid_path}')
    candidates.sort()
    return candidates[0][1]


def detect_pwm_lo_accum_base(sid_path: str, params: EngineParams) -> int:
    """Scan orig binary for the modulation block's PW-lo write:
    `AC ?? ?? B9 LL HH 9D 02 D4` (LDY $CB04 / LDA $CB01,Y / STA $D402,X)
    and return the LDA's operand — that's the PWM lo accum base."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    candidates = []
    for addr in range(load, load + len(body) - 9):
        if (mem[addr] == 0xAC and mem[addr+3] == 0xB9 and
            mem[addr+6] == 0x9D and mem[addr+7] == 0x02 and
            mem[addr+8] == 0xD4):
            base = mem[addr+4] | (mem[addr+5] << 8)
            distance = abs(addr - params.proc_note_addr)
            candidates.append((distance, base))
    if not candidates:
        raise RuntimeError(f'No PWM lo accum base found in {sid_path}')
    candidates.sort()
    return candidates[0][1]


def capture_cells_after_init(sid_path: str, params: EngineParams,
                             cell_addrs: list[int],
                             subtune: int = 0) -> bytes:
    """Run orig init in py65 with libsidplayfp powerup RAM; return
    the values at cell_addrs after init returns."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = subtune
    mpu.x = 0; mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = params.init_addr
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    return bytes(mpu.memory[a] for a in cell_addrs)


def capture_voice_state_slabs(sid_path: str, params: EngineParams,
                              voice_state_base: int,
                              stride: int = 0x1A,
                              subtune: int = 0) -> bytes:
    """Run orig init in py65 with libsidplayfp powerup RAM; dump the
    3 voice_state slabs (3 × stride = 78 bytes by default)."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = subtune
    mpu.x = 0; mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = params.init_addr
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    n_bytes = 3 * stride
    return bytes(mpu.memory[voice_state_base:voice_state_base + n_bytes])


def _libsidplayfp_powerup_ram() -> bytearray:
    """Mirror libsidplayfp's SystemRAMBank::reset() — needed because
    orig engines read uninitialised RAM cells whose powerup values
    influence audible behavior."""
    ram = bytearray(0x10000)
    byte = 0x00
    for j in range(0, 0x10000, 0x4000):
        for k in range(0x4000):
            ram[j + k] = byte
        byte ^= 0xFF
        for i in range(0x02, 0x4000, 0x08):
            for k in range(4):
                ram[j + i + k] = byte
    return ram


def capture_init_state(sid_path: str, params: EngineParams,
                       subtune: int = 0) -> dict:
    """Run orig init in py65 with libsidplayfp powerup RAM; return
    state-cell values the composer needs to reproduce.

    Returns a dict with keys:
      - tempo_counter, tempo_reload (the orig's value at the state cell
        Ninja_Hamster has at voice_ptrs - 9 / -8; same offset assumed
        for all Type A engines)
      - dur_counters (3 bytes at voice_ptrs - 12 / -11 / -10)
      - cur_inst (3 bytes at voice_ptrs - 7 / -6 / -5)
      - cur_ctrl (3 bytes at voice_ptrs - 4 / -3 / -2)
      - frame_counter (1 byte at voice_ptrs - 1)
      - self_mod_counter (from params)
      - initial_pwm_lo (3 bytes from voice_pwm_lo cells via heuristic
        or computed powerup pattern)
    """
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load = struct.unpack('>H', raw[8:10])[0]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = subtune
    mpu.x = 0; mpu.y = 0
    mpu.p = 0x20
    mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE
    mpu.memory[0x01FE] = 0xFE
    mpu.pc = params.init_addr
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    # Capture state assuming Ninja_Hamster layout offsets relative to voice_ptrs
    vp = params.voice_ptrs
    state = {
        'dur_counters': bytes(mpu.memory[vp - 12:vp - 9]),
        'tempo_counter': mpu.memory[vp - 9],
        'tempo_reload': mpu.memory[vp - 8],
        'cur_inst': bytes(mpu.memory[vp - 7:vp - 4]),
        'cur_ctrl': bytes(mpu.memory[vp - 4:vp - 1]),
        'frame_counter': mpu.memory[vp - 1],
        'self_mod_counter': mpu.memory[params.self_mod_counter],
        'voice_ptrs': bytes(mpu.memory[vp:vp + 6]),
        # Initial $D418 — read from SID register memory
        'master_vol': mpu.memory[0xD418] or 0x0F,
    }
    return state


def params_from_extracted_json(json_path: str | Path) -> EngineParams:
    """Build an EngineParams from the scanner's _extracted JSON.

    Some fields are not load-bearing for the rebuild (only for extraction
    and per-engine quirks) — set to 0 where unknown. emit_asm() doesn't
    consume these; only extract_data + composer init use them."""
    d = json.load(open(json_path))
    voices = [v['initial_ptr'] for v in d['voices']]
    while len(voices) < 3:
        voices.append(0)
    return EngineParams(
        play_addr=d['play_addr'],
        init_addr=d['init_addr'],
        proc_note_addr=d['proc_note_addr'],
        duration_counters=0,         # not used in extract
        tempo_counter=0,
        tempo_reload=0,
        current_inst=0,
        ctrl_byte=0,
        frame_counter=0,
        voice_ptrs=d['voices'][0]['ptr_addr'],
        self_mod_counter=d['counter_addr'],
        song_loop_clears=(),
        sub_jump_table=d['sub_jump_table']['addr'],
        inst_slide_lo_table=d['freq_table']['lo_addr'],
        inst_slide_hi_table=d['freq_table']['hi_addr'],
        voice_offsets=0,             # we synthesize [0, 7, 14]
        voice_pwm_phase=0,
        voice_pwm_lo_accum=0,        # configured per engine; defaults below
        modulation_voice_idx=0,
        voice_state_base=0,          # in orig binary; computed from proc_note
        voice_state_stride=0x1A,
        inst_src_table=d['instrument_base_table']['addr'],
        voice_dst_table=0,
        voice_initial_ptrs=tuple(voices[:3]),
        initial_tempo=0x0A,
        initial_master_vol=0x0F,
    )


def extract_data(sid_path: str, params: EngineParams = NINJA_HAMSTER,
                 n_inst: int = 19,
                 voice_byte_ranges: list[tuple[int, int]] | None = None
                 ) -> ExtractedData:
    """Run the emulator-equivalent SID load + pull engine data tables.

    `voice_byte_ranges` overrides the contiguous-pattern heuristic for
    engines where the three voice pattern streams aren't contiguous in
    memory (Mandroid: V0/V1 at $04xx, V2 at $76xx). Pass a list of
    (min_addr, max_addr+1) per voice; we'll slice mem[min:max+1].
    Without it, we fall back to the Ninja_Hamster heuristic of
    "next sorted voice start" or play_addr."""
    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load_in = struct.unpack('>H', raw[8:10])[0]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body

    # Freq tables — 256 bytes each (engine uses note+$10 which can
    # overflow into the next 128 bytes; orig data layout has them
    # contiguous so the read still hits valid bytes)
    freq_lo = bytes(mem[params.inst_slide_lo_table:params.inst_slide_lo_table + 256])
    freq_hi = bytes(mem[params.inst_slide_hi_table:params.inst_slide_hi_table + 256])

    sub_jump = bytes(mem[params.sub_jump_table:params.sub_jump_table + 20])
    # Voice SID offsets are always [0, 7, 14] across all Jay_Derrett engines
    # (it's a SID register layout, not an engine choice).
    voice_offs = bytes([0, 7, 14])

    # Instrument source table — n_inst × 2 byte ptrs
    inst_src = bytes(mem[params.inst_src_table:params.inst_src_table + n_inst * 2])

    # Instrument programs — 24 bytes each, pointed to by inst_src
    inst_progs = []
    for i in range(n_inst):
        src_lo = inst_src[i * 2]
        src_hi = inst_src[i * 2 + 1]
        src_addr = src_lo | (src_hi << 8)
        prog = bytes(mem[src_addr:src_addr + 24])
        inst_progs.append(prog)

    # Voice patterns — bytes from each voice's initial ptr to "end".
    # The orig pattern data is laid out contiguously $C000-$C451.
    # We extract each voice's range from initial_ptr to next voice's
    # initial_ptr (or end of pattern region).
    voice_patterns = []
    if voice_byte_ranges is not None:
        # Explicit ranges from scanner; each voice's pattern stream
        # is whatever the play-capture observed at that voice's ptr.
        # For engines that COPY pattern data from body to RAM during
        # init (Mandroid), the body addresses at voice_ptrs are
        # uninitialised — we must run init via py65 to get the
        # populated pattern bytes.
        # Run init in py65 with libsidplayfp powerup RAM, then dump
        # the voice_byte_ranges from RAM. This handles both
        # "directly-loaded" engines (NH) and "copied" engines (Mandroid).
        post_init_mem = _run_init_for_extract(sid_path, params)
        for v in range(3):
            lo, hi = voice_byte_ranges[v]
            voice_patterns.append(bytes(post_init_mem[lo:hi]))
    else:
        pat_starts = [params.voice_initial_ptrs[v] for v in range(3)]
        pat_end = params.play_addr  # play starts right after data
        boundaries = list(pat_starts) + [pat_end]
        boundaries.sort()
        for v in range(3):
            start = params.voice_initial_ptrs[v]
            end = next(b for b in boundaries if b > start)
            voice_patterns.append(bytes(mem[start:end]))
    # Offsets of each voice's initial ptr within its pattern slice = 0
    voice_initial_offsets = (0, 0, 0)

    # PSID metadata
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')

    return ExtractedData(
        freq_lo=freq_lo,
        freq_hi=freq_hi,
        sub_jump_table=sub_jump,
        voice_offsets=voice_offs,
        inst_src_table=inst_src,
        inst_programs=inst_progs,
        voice_patterns=voice_patterns,
        voice_initial_offsets=voice_initial_offsets,
        initial_tempo=params.initial_tempo,
        initial_master_vol=params.initial_master_vol,
        title=title,
        author=author,
        released=released,
    )


# ---------------------------------------------------------------------------
# Composer — emit clean xa65 asm for the Jay_Derrett engine
# ---------------------------------------------------------------------------

def emit_asm(data: ExtractedData, load_addr: int = 0x1000,
             quirks: 'EngineQuirks' = None) -> str:
    """Generate xa65 source for a clean Jay_Derrett rebuild.

    Layout (one contiguous block from load_addr):
      load+0    init_entry: JMP init_code
      load+3    play_entry: JMP play_code
      load+6    engine code (init, play, proc_note, instrument_loader,
                modulation_block)
      ...       state region, tables, instruments, pattern data

    The engine logic mirrors the orig's semantics but is freshly
    written. Data tables are inlined from `data` (musical content)."""

    lines = [f'* = ${load_addr:04X}']
    lines += [
        '',
        '; ============================================================',
        '; Jay_Derrett engine — clean rebuild',
        '; ============================================================',
        '',
        '; ZP usage:',
        ';   $F2/$F3  pattern ptr (per voice; loaded/saved per call)',
        '',
        '; Entry points',
        'init_entry:',
        '    jmp init_code',
        'play_entry:',
        '    jmp play_code',
        '',
    ]

    # ----- State region forward decls -----
    # We label everything; xa65 resolves addresses.
    # State variables, all at the end of the file as .byte / .dsb.
    # Placed BEFORE data tables to keep them in a single dense block.

    # ----- init code -----
    lines += [
        'init_code:',
        '    ; Voice 0 ptr',
        '    lda #<voice0_pattern',
        '    sta voice_ptrs',
        '    lda #>voice0_pattern',
        '    sta voice_ptrs+1',
        '    ; Voice 1 ptr',
        '    lda #<voice1_pattern',
        '    sta voice_ptrs+2',
        '    lda #>voice1_pattern',
        '    sta voice_ptrs+3',
        '    ; Voice 2 ptr',
        '    lda #<voice2_pattern',
        '    sta voice_ptrs+4',
        '    lda #>voice2_pattern',
        '    sta voice_ptrs+5',
        '    ; Self-mod counter starts at $E0',
        '    lda #$e0',
        '    sta self_mod_counter',
        '    ; Tempo counter + reload',
        f'    lda #${data.initial_tempo:02X}',
        '    sta tempo_counter',
        '    sta tempo_reload',
        '    ; Master vol',
        f'    lda #${data.initial_master_vol:02X}',
        '    sta $d418',
        '    ; Duration counters = 1 (process first byte every tick)',
        '    lda #$01',
        '    sta dur_counters',
        '    sta dur_counters+1',
        '    sta dur_counters+2',
        '    ; Initial PWM lo accumulator values mirror orig reliance on',
        '    ; libsidplayfp powerup RAM at the engine PWM lo cell address.',
    ]
    pwm = quirks.initial_pwm_lo if quirks else (0xFF, 0x00, 0x00)
    for v, val in enumerate(pwm):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta voice_pwm_lo+{v}']
    phase = quirks.initial_pwm_phase if quirks else (0, 0, 0)
    for v, val in enumerate(phase):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta voice_pwm_phase+{v}']
    # cur_inst per voice (orig init may pre-set instrument IDs)
    cur_inst = quirks.initial_cur_inst if quirks else (0, 0, 0)
    for v, val in enumerate(cur_inst):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta cur_inst+{v}']
    # cur_ctrl per voice (CTRL byte cache; orig pre-sets via inst load)
    cur_ctrl = quirks.initial_cur_ctrl if quirks else (0, 0, 0)
    for v, val in enumerate(cur_ctrl):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta cur_ctrl+{v}']
    # frame_counter (ZIP pre-INCs during init → starts non-zero)
    fc = quirks.initial_frame_counter if quirks else 0
    if fc:
        lines += [f'    lda #${fc:02X}', '    sta frame_counter']
    # Copy captured orig init voice_state slabs into the reb's
    # voice_state region. This pre-populates per-voice runtime state
    # (freq slide setup, PW params, CTRL slot) — matches engines whose
    # init pre-loads instruments for one or more voices.
    if data.init_voice_state is not None and any(data.init_voice_state):
        n = len(data.init_voice_state)
        lines += [
            f'    ldx #${n-1:02X}',
            'init_copy_state_loop:',
            '    lda init_voice_state_data,x',
            '    sta voice_state,x',
            '    dex',
            '    bpl init_copy_state_loop',
        ]
    lines += [
        '    rts',
        '',
    ]
    if data.init_voice_state is not None and any(data.init_voice_state):
        lines.append('init_voice_state_data:')
        for i in range(0, len(data.init_voice_state), 16):
            chunk = data.init_voice_state[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
        lines.append('')

    # ----- play code -----
    lines += [
        'play_code:',
        '    inc frame_counter',
        '    dec tempo_counter',
        '    bne play_modulation     ; tempo not expired; skip voice processing',
        '    ; Process all 3 voices',
        '    ldx #$00',
        '    jsr process_voice',
        '    ldx #$01',
        '    jsr process_voice',
        '    ldx #$02',
        '    jsr process_voice',
        '    ; Reload tempo counter',
        '    lda tempo_reload',
        '    sta tempo_counter',
        'play_modulation:',
        '    ldx #$00',
        '    jsr modulate_voice',
        '    ldx #$01',
        '    jsr modulate_voice',
        '    ldx #$02',
        '    jsr modulate_voice',
        '    rts',
        '',
    ]

    # ----- process_voice: set up zp ptr, X stride, Y stride; JSR proc_note -----
    # X comes in as voice index (0/1/2).
    # We need: $F2/$F3 = voice's pattern ptr
    #         X stride for compact state (just X = voice idx)
    #         Y stride for runtime state slab (Y_table[X])
    lines += [
        'process_voice:',
        '    ; Save X (voice idx)',
        '    stx cur_voice',
        '    ; Load voice ptr into $F2/$F3',
        '    txa',
        '    asl',                  # X * 2 for ptr index
        '    tay',
        '    lda voice_ptrs,y',
        '    sta $f2',
        '    lda voice_ptrs+1,y',
        '    sta $f3',
        '    ; Y_state = voice_y_table[X]',
        '    ldx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    ; Call proc_note',
        '    jsr proc_note',
        '    ; Save ptr back',
        '    ldx cur_voice',
        '    txa',
        '    asl',
        '    tay',
        '    lda $f2',
        '    sta voice_ptrs,y',
        '    lda $f3',
        '    sta voice_ptrs+1,y',
        '    rts',
        '',
    ]

    # ----- proc_note -----
    lines += [
        'proc_note:',
        '    ; DEC duration counter; if non-zero, RTS',
        '    ldx cur_voice',
        '    dec dur_counters,x',
        '    beq pn_proceed',
        '    rts',
        'pn_proceed:',
        '    ; Reset duration to 1',
        '    inc dur_counters,x',
        'pn_read:',
        '    ldy #$00',
        '    lda ($f2),y         ; read pattern byte',
        '    pha                 ; save A',
        '    and #$f0            ; high nibble check',
        '    cmp #$e0            ; $Ex? (pattern-jump)',
        '    beq pn_ex',
        '    cmp #$d0            ; $Dx? (set instrument)',
        '    beq pn_dx',
        '    pla                 ; restore A',
        '    cmp #$80            ; gate-off?',
        '    beq pn_gate_off',
        '    cmp #$81            ; skip?',
        '    beq pn_skip',
        '    cmp #$82            ; set duration?',
        '    beq pn_set_dur',
        '    pha                 ; save A again',
        '    and #$f0',
        '    cmp #$b0            ; $Bx? (set tempo)',
        '    beq pn_bx',
        '    cmp #$c0            ; $Cx? (set master vol)',
        '    beq pn_cx',
        '    pla                 ; restore A — it\'s a NOTE',
        '    jmp pn_note',
        '',
        '; --- $Ex: pattern-jump dispatch (counter-matched) ---',
        'pn_ex:',
        '    pla                 ; restore byte',
        '    cmp self_mod_counter',
        '    beq pn_ex_match',
        '    ; No match — advance ptr + recurse',
        '    jmp pn_advance_recurse',
        'pn_ex_match:',
        '    and #$0f            ; low nibble',
        '    asl',
        '    tay',
        '    lda sub_jump_table,y',
        '    sta $f2',
        '    lda sub_jump_table+1,y',
        '    sta $f3',
        '    inc self_mod_counter',
        '    lda self_mod_counter',
        '    cmp #$e9',
        '    bne pn_read         ; not yet wrap, recurse with new ptr',
        '    ; Wrap: reset counter + silence voice 2 (orig clears',
        '    ; $C975 + $C978 which are voice 2 CTRL + gate-off CTRL slots).',
        '    lda #$e0',
        '    sta self_mod_counter',
        '    lda #$00',
        '    sta voice_state+$14+$34',
        '    sta voice_state+$17+$34',
        '    jmp pn_read',
        '',
        '; --- $Dx: set instrument ---',
        'pn_dx:',
        '    pla                 ; restore byte',
        '    and #$0f            ; low nibble',
        '    sta cur_inst,x      ; store at cur_inst[voice]',
        '    inc cur_inst,x      ; +1 quirk',
        '    jmp pn_advance_recurse',
        '',
        '; --- $80: gate off ---',
        'pn_gate_off:',
        '    ldy cur_voice_y',
        '    lda voice_state+$14,y       ; CTRL slot (gate-on)',
        '    sta voice_state+$17,y       ; copy to gate-off CTRL slot',
        '    jmp pn_advance_rts',
        '',
        '; --- $81: skip ---',
        'pn_skip:',
        '    jmp pn_advance_rts',
        '',
        '; --- $82 N: set duration ---',
        'pn_set_dur:',
        '    ; Advance past $82, read N, store, advance past N',
        '    inc $f2',
        '    bne pn_sd_no_inc_hi',
        '    inc $f3',
        'pn_sd_no_inc_hi:',
        '    ldy #$00',
        '    lda ($f2),y',
        '    sta dur_counters,x',
    ]
    if quirks and quirks.set_dur_clears_v3:
        lines += [
            '    ; Engine quirk: SET DUR also clears V3 CTRL slots',
            '    lda #$00',
            '    sta voice_state+$14+$34',
            '    sta voice_state+$17+$34',
        ]
    lines += [
        '    jmp pn_advance_rts',
        '',
        '; --- $Bx: set tempo ---',
        'pn_bx:',
        '    pla',
        '    and #$0f',
        '    sta tempo_reload',
        '    dec tempo_reload    ; (STA then DEC matches orig)',
        '    jmp pn_advance_recurse',
        '',
        '; --- $Cx: set master vol ---',
        'pn_cx:',
        '    pla',
        '    and #$0f',
        '    sta $d418',
        '    jmp pn_advance_recurse',
        '',
        '; --- NOTE handler ---',
        'pn_note:',
        '    ; A = note byte (preserved from earlier PLA)',
        '    pha                 ; save note',
        '    ; Write CTRL to $D404+sid_off',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
        '    lda cur_ctrl,x',
        '    sta $d404,y',
        '    ; Call instrument loader with A = note',
        '    pla                 ; restore note',
        '    jsr instrument_load',
        '    jmp pn_advance_rts',
        '',
        '; --- helpers ---',
        'pn_advance_recurse:',
        '    inc $f2',
        '    bne pn_ar_skip',
        '    inc $f3',
        'pn_ar_skip:',
        '    jmp pn_read',
        '',
        'pn_advance_rts:',
        '    inc $f2',
        '    bne pn_arts_skip',
        '    inc $f3',
        'pn_arts_skip:',
        '    rts',
        '',
    ]

    # ----- instrument_load (sub_C86E) -----
    lines += [
        'instrument_load:',
        '    ; Args: A = note byte; X = cur_voice; cur_voice_y = Y_stride',
        '    pha                 ; save note',
        '    ; Get inst from cur_inst[X]',
        '    lda cur_inst,x',
        '    asl                 ; inst * 2',
        '    tay',
        '    ; src_addr = inst_src_table[inst*2..+1]',
        '    lda inst_src_table,y',
        '    sta inst_copy_src+1',
        '    lda inst_src_table+1,y',
        '    sta inst_copy_src+2',
        '    ; Copy 24 bytes from src to voice_state[cur_voice_y]',
        '    ldy #$17            ; 23 → loop down to 0',
        '    ldx cur_voice_y',
        '    txa',
        '    clc',
        '    adc #<voice_state',
        '    sta inst_copy_dst+1',
        '    lda #>voice_state',
        '    adc #$00',
        '    sta inst_copy_dst+2',
        'inst_copy_loop:',
        'inst_copy_src:',
        '    lda $ffff,y         ; self-mod operand (src)',
        'inst_copy_dst:',
        '    sta $ffff,y         ; self-mod operand (dst)',
        '    dey',
        '    bpl inst_copy_loop',
        '    ; Apply note → freq lookup',
        '    pla                 ; restore note',
        '    pha                 ; save again',
        '    tax                 ; X = note',
        '    ldy cur_voice_y',
        '    lda freq_lo_table,x',
        '    sta voice_state+$01,y',
        '    clc',
        '    adc voice_state+$03,y',
        '    sta voice_state+$03,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$02,y',
        '    clc',
        '    adc voice_state+$04,y',
        '    sta voice_state+$04,y',
        '    lda voice_state+$01,y',
        '    sec',
        '    sbc voice_state+$05,y',
        '    sta voice_state+$05,y',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$06,y',
        '    sta voice_state+$06,y',
        '    ; note + $10 → freq off-slide override',
        '    pla',
        '    clc',
        '    adc #$10',
        '    tax',
        '    lda freq_lo_table,x',
        '    sta voice_state+$18,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$19,y',
        '    ; Set CTRL byte from voice_state+$14',
        '    lda voice_state+$14,y',
        '    ldx cur_voice',
        '    sta cur_ctrl,x',
        '    ; Clear PWM phase + lo accum for this voice',
        '    lda #$00',
        '    sta voice_pwm_phase,x',
        '    sta voice_pwm_lo,x',
        '    ; Write AD/SR',
        '    ldy voice_sid_off,x',
        '    ldx cur_voice_y',
        '    lda voice_state+$15,x',
        '    sta $d405,y',
        '    lda voice_state+$16,x',
        '    sta $d406,y',
        '    rts',
        '',
    ]

    # ----- modulate_voice (sub_C6EE) -----
    lines += [
        'modulate_voice:',
        '    ; X = voice idx (0/1/2)',
        '    stx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    ldy voice_sid_off,x',
        '    sty cur_sid_off',
        '    ; Output freq (with bit-7 LFO toggle)',
        '    ldy cur_voice_y',
        '    lda voice_state,y',
        '    bpl mod_freq_normal     ; bit 7 clear → normal freq',
        '    ; bit 7 set: check frame counter LSB',
        '    lda frame_counter',
        '    lsr',
        '    bcc mod_freq_offslide   ; carry clear → off-slide freq',
        'mod_freq_normal:',
        '    ldx cur_sid_off',
        '    lda voice_state+$01,y',
        '    sta $d400,x',
        '    lda voice_state+$02,y',
        '    sta $d401,x',
        '    jmp mod_pw_out',
        'mod_freq_offslide:',
        '    ldx cur_sid_off',
        '    lda voice_state+$18,y',
        '    sta $d400,x',
        '    lda voice_state+$19,y',
        '    sta $d401,x',
        'mod_pw_out:',
        '    ; PW out: $D403 = voice_state+$0A,y ; $D402 = voice_pwm_lo[v]',
        '    lda voice_state+$0A,y',
        '    sta $d403,x',
        '    ldx cur_voice',
        '    lda voice_pwm_lo,x',
        '    ldx cur_sid_off',
        '    sta $d402,x',
        '    ; CTRL out: $D404 = voice_state+$14,y | voice_state+$17,y',
        '    lda voice_state+$14,y',
        '    ora voice_state+$17,y',
        '    sta $d404,x',
        '    ; Slide update — flag bit 0 selects direction',
        '    lda voice_state,y',
        '    lsr',
        '    bcs mod_slide_down',
        '    jsr slide_up',
        '    jmp mod_pwm_update',
        'mod_slide_down:',
        '    jsr slide_down',
        'mod_pwm_update:',
        '    jsr pwm_update',
        '    rts',
        '',
    ]

    # ----- slide_up / slide_down -----
    lines += [
        '; slide_up: in cur_voice_y; modifies voice_state[$01,$02] and flag',
        'slide_up:',
        '    ldy cur_voice_y',
        '    lda voice_state+$01,y',
        '    clc',
        '    adc voice_state+$07,y       ; delta lo',
        '    sta voice_state+$01,y',
        '    lda voice_state+$02,y',
        '    adc voice_state+$08,y       ; delta hi',
        '    sta voice_state+$02,y',
        '    lda voice_state+$01,y',
        '    cmp voice_state+$03,y       ; max lo',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$04,y       ; max hi',
        '    bcc slu_continue            ; below max — keep sliding',
        '    ; Reached max',
        '    lda voice_state,y',
        '    and #$02',
        '    beq slu_check_continuous',
        '    ; Bit 1 set: swap direction (EOR #$01 on flag) + reset to max',
        '    lda voice_state,y',
        '    eor #$01',
        '    sta voice_state,y',
        '    lda voice_state+$03,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$04,y',
        '    sta voice_state+$02,y',
        '    rts',
        'slu_check_continuous:',
        '    lda voice_state,y',
        '    and #$04',
        '    bne slu_continuous',
        '    ; Bit 2 clear: one-shot — zero deltas',
        '    lda #$00',
        '    sta voice_state+$07,y',
        '    sta voice_state+$08,y',
        '    rts',
        'slu_continuous:',
        '    ; Bit 2 set: reset to min',
        '    lda voice_state+$05,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$06,y',
        '    sta voice_state+$02,y',
        'slu_continue:',
        '    rts',
        '',
        'slide_down:',
        '    ldy cur_voice_y',
        '    lda voice_state+$01,y',
        '    sec',
        '    sbc voice_state+$07,y       ; delta lo',
        '    sta voice_state+$01,y',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$08,y       ; delta hi',
        '    sta voice_state+$02,y',
        '    lda voice_state+$01,y',
        '    cmp voice_state+$05,y       ; min lo',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$06,y       ; min hi',
        '    bcs sld_continue            ; above min — keep sliding',
        '    ; Reached min',
        '    lda voice_state,y',
        '    and #$02',
        '    beq sld_check_continuous',
        '    ; Bit 1 set: swap direction + reset to min',
        '    lda voice_state,y',
        '    eor #$01',
        '    sta voice_state,y',
        '    lda voice_state+$05,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$06,y',
        '    sta voice_state+$02,y',
        '    rts',
        'sld_check_continuous:',
        '    lda voice_state,y',
        '    and #$04',
        '    bne sld_continuous',
        '    lda #$00',
        '    sta voice_state+$07,y',
        '    sta voice_state+$08,y',
        '    rts',
        'sld_continuous:',
        '    lda voice_state+$03,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$04,y',
        '    sta voice_state+$02,y',
        'sld_continue:',
        '    rts',
        '',
    ]

    # ----- pwm_update -----
    lines += [
        'pwm_update:',
        '    ldx cur_voice',
        '    lda voice_pwm_phase,x',
        '    bne pwm_phase1',
        '    ; --- Phase 0 ---',
        '    ldy cur_voice_y',
        '    lda voice_state+$0E,y       ; direction flag',
        '    bne pwm0_sub',
        '    ; Phase 0 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$0C,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    adc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$0B,y',
        '    bcs pwm0_advance',
        '    rts',
        'pwm0_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$0C,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    sbc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$0B,y',
        '    beq pwm0_advance',
        '    bcs pwm0_done',
        'pwm0_advance:',
        '    inc voice_pwm_phase,x',
        'pwm0_done:',
        '    rts',
        '',
        'pwm_phase1:',
        '    ldy cur_voice_y',
        '    lda voice_state+$0F,y       ; phase 1 direction flag',
        '    bne pwm1_sub',
        '    ; Phase 1 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$12,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    adc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$10,y',
        '    bcc pwm1_done',
        '    lda #$01',
        '    sta voice_state+$0F,y',
        '    rts',
        'pwm1_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$12,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    sbc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$11,y',
        '    beq pwm1_flip',
        '    bcs pwm1_done',
        'pwm1_flip:',
        '    lda #$00',
        '    sta voice_state+$0F,y',
        'pwm1_done:',
        '    rts',
        '',
    ]

    # ----- State region -----
    lines += [
        '; ============================================================',
        '; State region',
        '; ============================================================',
        '',
        'cur_voice:        .byte 0',
        'cur_voice_y:      .byte 0',
        'cur_sid_off:      .byte 0',
        'frame_counter:    .byte 0',
        'tempo_counter:    .byte 0',
        'tempo_reload:     .byte 0',
        'self_mod_counter: .byte 0',
        'dur_counters:     .byte 0, 0, 0',
        'cur_inst:         .byte 0, 0, 0',
        'cur_ctrl:         .byte 0, 0, 0',
        'voice_ptrs:       .byte 0, 0, 0, 0, 0, 0',
        'voice_pwm_phase:  .byte 0, 0, 0',
        'voice_pwm_lo:     .byte 0, 0, 0',
        '',
        '; Per-voice runtime state slabs (3 × $1A = 78 bytes)',
        '; Voice 0: $00, voice 1: $1A, voice 2: $34',
        'voice_state:      .dsb 26 * 3, 0',
        '',
        '; Voice Y-stride table',
        'voice_y_table:    .byte $00, $1A, $34',
        '',
        '; Voice SID register offsets',
        'voice_sid_off:    .byte ' + ', '.join(f'${b:02X}' for b in data.voice_offsets),
        '',
    ]

    # ----- Sub-jump table -----
    lines += [
        'sub_jump_table:',
        '    .byte ' + ', '.join(f'${b:02X}' for b in data.sub_jump_table),
        '',
    ]
    # NOTE: sub_jump_table entries point at absolute addresses in orig.
    # They reference pattern data inside the voice patterns. We MUST
    # remap them to point at our relocated pattern data. Compute the
    # mapping below — for now, emit raw and patch in the bytes table.
    # Actually we'll do this at runtime — see below.

    # ----- Freq tables (256 bytes each: 128 lo + 128 hi) -----
    # The engine indexes with X = note + $10 which can reach $8F, so we
    # need 256 bytes accessible from freq_lo_table base. Use the orig's
    # contiguous layout: freq_lo (128) then freq_hi (128) — engine reads
    # at offset $80+ into freq_lo land in freq_hi region (legitimately).
    lines += [
        'freq_lo_table:',
    ]
    for i in range(0, 128, 16):
        chunk = data.freq_lo[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines += [
        'freq_hi_table:',
    ]
    for i in range(0, 128, 16):
        chunk = data.freq_hi[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- Instrument source table -----
    # Orig has $C8FB pointing at instrument programs scattered through
    # the SID body. We re-emit a clean table pointing at our local
    # `inst_program_N` labels.
    lines += [
        'inst_src_table:',
    ]
    for i in range(len(data.inst_programs)):
        lines.append(f'    .byte <inst_prog_{i}, >inst_prog_{i}')
    lines.append('')

    # ----- Instrument programs (24 bytes each) -----
    for i, prog in enumerate(data.inst_programs):
        lines.append(f'inst_prog_{i}:')
        for j in range(0, 24, 8):
            chunk = prog[j:j + 8]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- Voice patterns -----
    for v, pat in enumerate(data.voice_patterns):
        lines.append(f'voice{v}_pattern:')
        for i in range(0, len(pat), 16):
            chunk = pat[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# Sub-jump-table relocation
# ---------------------------------------------------------------------------

def _remap_sub_jump_table(data: ExtractedData, params: EngineParams,
                           voice_pattern_bases: list[int],
                           voice_byte_ranges: list[tuple[int, int]] | None = None
                           ) -> bytes:
    """The orig sub_jump_table entries are absolute addresses into
    voice pattern data. Since we relocate the patterns to our own
    addresses, the table entries must be remapped.

    `voice_byte_ranges` (when provided) overrides voice_initial_ptrs
    as the source of truth for each voice's range — used when voices
    are non-contiguous in orig memory."""
    if voice_byte_ranges is not None:
        orig_voice_bases = [lo for lo, _ in voice_byte_ranges]
        voice_ends = [hi for _, hi in voice_byte_ranges]
    else:
        orig_voice_bases = list(params.voice_initial_ptrs)
        voice_ends = [orig_voice_bases[v] + len(data.voice_patterns[v])
                      for v in range(3)]
    remapped = bytearray()
    for i in range(0, len(data.sub_jump_table), 2):
        orig_lo = data.sub_jump_table[i]
        orig_hi = data.sub_jump_table[i + 1]
        orig_addr = orig_lo | (orig_hi << 8)
        # Find which voice owns this orig_addr
        owner = None
        for v in range(3):
            if orig_voice_bases[v] <= orig_addr < voice_ends[v]:
                owner = v
                break
        if owner is None:
            # Entry references something outside the pattern region —
            # leave as-is (might be padding). Emit zeros.
            remapped += b'\x00\x00'
            continue
        offset = orig_addr - orig_voice_bases[owner]
        new_addr = voice_pattern_bases[owner] + offset
        remapped += bytes([new_addr & 0xFF, (new_addr >> 8) & 0xFF])
    return bytes(remapped)


# ---------------------------------------------------------------------------
# Two-pass assembly to resolve addresses
# ---------------------------------------------------------------------------

def _sanitize_asm(s: str) -> str:
    """xa65 is picky about characters in comments. Strip non-ASCII and
    re-process comments to avoid `$NN:` syntax that confuses the parser."""
    import re
    s = (s.replace('—', '-')
          .replace('–', '-')
          .replace('→', '->')
          .replace('×', 'x')
          .replace('‘', "'").replace('’', "'")
          .encode('ascii', errors='replace').decode('ascii'))
    # Strip `$XX:` patterns from comments (xa65 sometimes mis-parses these).
    out_lines = []
    for line in s.split('\n'):
        comment_idx = line.find(';')
        if comment_idx >= 0:
            code = line[:comment_idx]
            comment = line[comment_idx:]
            # Replace `$XX:` with `XX_` in comments
            comment = re.sub(r'\$([0-9A-Fa-fXx]+):', r'\1_', comment)
            line = code + comment
        out_lines.append(line)
    return '\n'.join(out_lines)


def _assemble(asm_src: str, name: str = 'jd') -> tuple[bytes, dict[str, int]]:
    src = f'/tmp/{name}.s'
    obj = f'/tmp/{name}.bin'
    lbl = f'/tmp/{name}.labels'
    asm_src = _sanitize_asm(asm_src)
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, '-M', src, '-o', obj, '-l', lbl],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    labels = {}
    if Path(lbl).exists():
        for line in open(lbl):
            # xa65 labels file format: name, 0xaddr, 0, 0xext
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                try:
                    labels[parts[0]] = int(parts[1], 16)
                except ValueError:
                    pass
    return open(obj, 'rb').read(), labels


@dataclass
class EngineQuirks:
    """Per-engine quirks that have to be reproduced for byte-exact match.

    Most engines lift these into engine config; we keep them as a small
    typed bag here. Lift into USF (Phase later) once we understand the
    full quirk-space across the family.
    """
    # Initial value for the V1 PWM-lo accumulator (orig engines depend
    # on libsidplayfp's powerup RAM at the engine's PWM lo cell address).
    initial_pwm_lo: tuple[int, int, int] = (0xFF, 0x00, 0x00)
    # Initial PWM phase per voice (0 = phase 0, non-zero = phase 1).
    initial_pwm_phase: tuple[int, int, int] = (0x00, 0x00, 0x00)
    # Initial cur_inst per voice (orig init may pre-load instruments).
    initial_cur_inst: tuple[int, int, int] = (0x00, 0x00, 0x00)
    # Initial cur_ctrl per voice (CTRL byte cache; set by inst load).
    initial_cur_ctrl: tuple[int, int, int] = (0x00, 0x00, 0x00)
    # Initial tempo counter + reload values (most engines = $0A).
    initial_tempo: int = 0x0A
    initial_tempo_reload: int = 0x0A
    # Initial dur counters (most engines = [1, 1, 1]).
    initial_dur_counters: tuple[int, int, int] = (0x01, 0x01, 0x01)
    # Initial self-mod counter ($E0 for most; $D0 for Jetboys; $FB for Traxxion).
    initial_smc: int = 0xE0
    # Initial master vol (most $0F; Destruct $05).
    initial_master_vol: int = 0x0F
    # Initial frame_counter (most $00; ZIP=$53 — engine pre-INCs during init).
    initial_frame_counter: int = 0x00
    # Some engines (Jetboys/Lifeforce/Vengeance/ZIP) clear V3 CTRL slots
    # inside the SET DUR ($82 N) handler. NH/Mandroid/Counterforce/
    # Destruct/Discovery don't. Detected by scanning for the
    # `A9 00 8D LO HI 8D LO+3 HI 4C` pattern preceded by SET DUR setup.
    set_dur_clears_v3: bool = False
    # Number of instruments in the inst src table (typically 19).
    n_inst: int = 19


# Per-SID config: SID basename -> EngineQuirks
# Defaults work for most "direct-play" Ninja_Hamster-shape engines.
_PER_SID_QUIRKS: dict[str, EngineQuirks] = {
    'Ninja_Hamster': EngineQuirks(),  # defaults
}


def _quirks_for(sid_stem: str, params: EngineParams) -> EngineQuirks:
    """Look up per-SID quirks; fall back to libsidplayfp powerup defaults."""
    if sid_stem in _PER_SID_QUIRKS:
        return _PER_SID_QUIRKS[sid_stem]
    # Default: compute PWM lo initial values from orig engine address.
    # If we don't know the orig PWM lo cell, fall back to Ninja_Hamster
    # pattern (V1=$FF, V2/V3=$00). This is wrong for non-default SIDs
    # — they need explicit quirks entries when byte-exact verification fails.
    return EngineQuirks()


def build_sid(sid_path: str, params: EngineParams,
              load_addr: int = 0x1000,
              quirks: EngineQuirks = None,
              voice_byte_ranges: list[tuple[int, int]] | None = None
              ) -> bytes:
    """Generic PSID builder for any Type A direct-play Jay_Derrett engine.

    `params` carries the orig binary's data-table addresses (for
    extraction). `quirks` carries per-engine init-quirks; defaults
    sufficient for many SIDs. `voice_byte_ranges` overrides the
    pattern slicing heuristic when voices are non-contiguous in
    memory (typical for relocated/IRQ-driven variants).
    """
    sid_stem = Path(sid_path).stem
    if quirks is None:
        quirks = _quirks_for(sid_stem, params)
    data = extract_data(sid_path, params, n_inst=quirks.n_inst,
                        voice_byte_ranges=voice_byte_ranges)
    # Capture orig init voice_state slabs so the reb starts with the
    # same per-voice runtime state (some engines pre-load instruments
    # during init; their voice_state has non-zero contents at frame 0).
    try:
        vs_base = detect_mod_base(sid_path, params)
        data.init_voice_state = capture_voice_state_slabs(
            sid_path, params, vs_base, stride=0x1A)
    except RuntimeError:
        data.init_voice_state = None
    # Capture orig PWM lo accumulator initial values (engines depend
    # on libsidplayfp powerup RAM at the PWM lo cell address; for
    # engines whose body extends past the cell, on the body bytes).
    pwm_lo_init = quirks.initial_pwm_lo
    pwm_phase_init = quirks.initial_pwm_phase
    if pwm_lo_init == (0xFF, 0x00, 0x00):
        try:
            pwm_base = detect_pwm_lo_accum_base(sid_path, params)
            pwm_vals = capture_cells_after_init(
                sid_path, params, [pwm_base + v for v in range(3)])
            pwm_lo_init = (pwm_vals[0], pwm_vals[1], pwm_vals[2])
        except RuntimeError:
            pass
    if pwm_phase_init == (0x00, 0x00, 0x00):
        try:
            phase_base = detect_pwm_phase_base(sid_path, params)
            phase_vals = capture_cells_after_init(
                sid_path, params, [phase_base + v for v in range(3)])
            pwm_phase_init = (phase_vals[0], phase_vals[1], phase_vals[2])
        except RuntimeError:
            pass
    # Capture engine state cells near voice_ptrs (NH layout assumed):
    # voice_ptrs - 12 = dur_counters[0]
    # voice_ptrs - 9 = tempo_counter
    # voice_ptrs - 8 = tempo_reload
    # voice_ptrs - 7 = cur_inst[0]
    # voice_ptrs - 4 = cur_ctrl[0]
    vp = params.voice_ptrs
    try:
        state_cells = capture_cells_after_init(
            sid_path, params,
            [vp - 12, vp - 11, vp - 10,    # dur
             vp - 9, vp - 8,                # tempo, tempo_reload
             vp - 7, vp - 6, vp - 5,        # cur_inst
             vp - 4, vp - 3, vp - 2,        # cur_ctrl
             vp - 1,                        # frame_counter
             params.self_mod_counter,       # smc
             0xD418])                       # master vol
        dur = (state_cells[0], state_cells[1], state_cells[2])
        tempo = state_cells[3]
        tempo_reload = state_cells[4]
        cur_inst = (state_cells[5], state_cells[6], state_cells[7])
        cur_ctrl = (state_cells[8], state_cells[9], state_cells[10])
        frame_cnt = state_cells[11]
        smc = state_cells[12]
        mvol = state_cells[13] if state_cells[13] else 0x0F
    except Exception:
        dur = quirks.initial_dur_counters
        tempo = quirks.initial_tempo
        tempo_reload = quirks.initial_tempo_reload
        cur_inst = quirks.initial_cur_inst
        cur_ctrl = quirks.initial_cur_ctrl
        frame_cnt = quirks.initial_frame_counter
        smc = quirks.initial_smc
        mvol = quirks.initial_master_vol
    quirks = EngineQuirks(
        initial_pwm_lo=pwm_lo_init,
        initial_pwm_phase=pwm_phase_init,
        initial_cur_inst=cur_inst,
        initial_cur_ctrl=cur_ctrl,
        initial_tempo=tempo,
        initial_tempo_reload=tempo_reload,
        initial_dur_counters=dur,
        initial_smc=smc,
        initial_master_vol=mvol,
        initial_frame_counter=frame_cnt,
        set_dur_clears_v3=detect_set_dur_clears_v3(sid_path),
        n_inst=quirks.n_inst)
    # Apply tempo + master vol overrides into data so emit_asm uses them
    data.initial_tempo = tempo
    data.initial_master_vol = mvol

    asm1 = emit_asm(data, load_addr, quirks=quirks)
    bin1, labels1 = _assemble(asm1, f'jd_{sid_stem}_pass1')
    voice_pattern_bases = [
        labels1.get(f'voice{v}_pattern', 0) for v in range(3)
    ]
    remapped_sjt = _remap_sub_jump_table(
        data, params, voice_pattern_bases,
        voice_byte_ranges=voice_byte_ranges)
    data.sub_jump_table = remapped_sjt
    asm2 = emit_asm(data, load_addr, quirks=quirks)
    bin2, _ = _assemble(asm2, f'jd_{sid_stem}_pass2')

    title = data.title
    author = data.author
    released = data.released
    init_addr = load_addr
    play_addr = load_addr + 3
    return _wrap_psid(title, author, released, init_addr, play_addr,
                      load_addr, bin2, n_subtunes=1)


def _wrap_psid(title: str, author: str, released: str,
               init_addr: int, play_addr: int, load_addr: int,
               body: bytes, n_subtunes: int = 1) -> bytes:
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', init_addr)
    h += struct.pack('>H', play_addr)
    h += struct.pack('>H', n_subtunes)
    h += struct.pack('>H', 1)
    h += struct.pack('>I', 0)
    def _latin1(s, n):
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += _latin1(title, 32)
    h += _latin1(author, 32)
    h += _latin1(released, 32)
    h += struct.pack('>H', (1 << 2) | (1 << 4))
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h) + body


def build_ninja_hamster_sid(load_addr: int = 0x1000) -> bytes:
    """Build a clean Ninja_Hamster PSID."""
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   'Ninja_Hamster.sid')
    return build_sid(sid_path, NINJA_HAMSTER, load_addr=load_addr)


_TYPE_A_SIDS = [
    'Counterforce', 'Destruct', 'Discovery', 'Jetboys', 'Lifeforce',
    'Mandroid', 'Ninja_Hamster', 'Osmium', 'Road_Warrior', 'Stratton',
    'Thundercross', 'Traxxion', 'Trigger_Happy', 'Vengeance', 'ZIP',
]


def try_all_type_a(duration: float = 6.0) -> dict[str, str]:
    """Attempt to build + verify every Type A SID with current composer.
    Returns dict of sid_name -> status string. Useful for tracking
    Phase 3 progress across engine variants."""
    from pipelines.hubbard.verify_cycle import (
        writelog_capture, compare_instruction_stream,
    )
    results: dict[str, str] = {}
    base = ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay'
    extracted = ROOT / 'pipelines' / 'companion' / 'jay_derrett' / '_extracted'
    for name in _TYPE_A_SIDS:
        sid_path = str(base / f'{name}.sid')
        reb_path = str(base / f'{name}.sidfinity.sid')
        json_path = str(extracted / f'{name}.json')
        if not Path(json_path).exists():
            results[name] = 'NO-JSON'
            continue
        try:
            params = params_from_extracted_json(json_path)
            jd = json.load(open(json_path))
            voice_byte_ranges = [
                (vb['ptr_min'], vb['ptr_min'] + len(vb['bytes']))
                for vb in jd['voice_bytes']
            ]
            sid_bytes = build_sid(sid_path, params,
                                  voice_byte_ranges=voice_byte_ranges)
            Path(reb_path).write_bytes(sid_bytes)
            a = writelog_capture(sid_path, 0, duration=duration)
            b = writelog_capture(reb_path, 0, duration=duration)
            r = compare_instruction_stream(a, b)
            if r['is_full']:
                results[name] = 'PASS'
            else:
                results[name] = (f"FAIL match_all={r['match_all']}/"
                                 f"{r['len_all_a']}")
        except Exception as e:
            results[name] = f"BUILD-ERR {type(e).__name__}: {str(e)[:60]}"
    return results


if __name__ == '__main__':
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == 'all':
        results = try_all_type_a()
        for name, status in results.items():
            print(f'{name:18} {status}')
    else:
        sid = build_ninja_hamster_sid()
        out = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                  'Ninja_Hamster.sidfinity.sid')
        Path(out).write_bytes(sid)
        print(f'Wrote {out} ({len(sid)} bytes)')
