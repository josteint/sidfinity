"""usf2_codegen_phase2.py — Phase 2 proof-of-concept codegen.

Implements the absolute minimum 6502 emit for the USF2 schema:
  - source `const`: LDA imm + STA $D4xx,Y
  - source `pitchFreqLo` / `pitchFreqHi` with empty USFFreqGenSpec:
        LDX #<pitch>; LDA freq_lo_table,X; STA $D4xx,Y
  - trigger `atFrame 0`: emit once in init/note-load path
  - trigger `atFrameBeforeNoteEnd N`: emit guarded by v_dur compare

Produces a self-contained PSID that plays ONE instrument at ONE
pitch for D frames, then loops. Used to validate the schema → 6502 →
SID → writelog round-trip end-to-end.

Phase 3+ will replace this with the real Codegen2.lean. For now Python
is faster to iterate.

Usage:
    python3 src/usf2_codegen_phase2.py > out.sid
    tools/siddump out.sid --writelog --duration 1 --raw | head
"""
from __future__ import annotations

import struct
import sys

# ----------------------------------------------------------------------------
# cv3I_test — mirror of pipelines/hubbard/commando/codegen/Commando/CommandoInsts2.lean
# ----------------------------------------------------------------------------
# Events: (trigger_kind, trigger_arg, register, source_kind, source_arg)
TEST_PITCH = 60               # play this pitch (semitone index)
TEST_DUR_FRAMES = 20          # frames per note
HR_THRESHOLD = 3              # frames-before-end where HR fires

# (kind, frame_or_dur, register_offset, source_kind, source_arg)
# Per-voice SID register offsets: freq_lo=0, freq_hi=1, pw_lo=2, pw_hi=3,
# ctrl=4, ad=5, sr=6.
CV3I_TEST_EVENTS = [
    ('atFrame',              0,  4, 'const',       0x41),   # ctrl  = $41
    ('atFrame',              0,  2, 'const',       0x00),   # pw_lo = $00
    ('atFrame',              0,  3, 'const',       0x09),   # pw_hi = $09
    ('atFrame',              0,  5, 'const',       0x29),   # AD    = $29
    ('atFrame',              0,  6, 'const',       0x5F),   # SR    = $5F
    ('atFrame',              0,  0, 'pitchFreqLo', None),   # freq_lo from pitch
    ('atFrame',              0,  1, 'pitchFreqHi', None),   # freq_hi from pitch
    ('atFrameBeforeNoteEnd', HR_THRESHOLD, 4, 'const', 0x40),   # ctrl gate off
    ('atFrameBeforeNoteEnd', HR_THRESHOLD, 5, 'const', 0x00),   # AD = 0
    ('atFrameBeforeNoteEnd', HR_THRESHOLD, 6, 'const', 0x00),   # SR = 0
]


# ----------------------------------------------------------------------------
# PAL freq table — 96 semitone entries, lo/hi pairs.
# Standard Hubbard PAL freq table (matches Commando's freq_table).
# ----------------------------------------------------------------------------
def gen_pal_freq_table():
    """Generate 96-entry PAL freq table."""
    # Approximation: scale up from a known base. Standard PAL formula:
    # freq = round(note_freq_hz * (16777216 / 985248))
    # where note_freq_hz = 440 * 2^((semitone - 57)/12)
    # Commando's freq table is well-known; just embed a standard sequence.
    import math
    table = []
    for n in range(96):
        # Hubbard's standard PAL: each semitone, ratio 2^(1/12)
        hz = 440.0 * (2 ** ((n - 57) / 12.0))
        sid_val = int(round(hz * 16777216.0 / 985248.0))
        sid_val = max(0, min(0xFFFF, sid_val))
        table.append(sid_val)
    return table


# ----------------------------------------------------------------------------
# 6502 emit helpers
# ----------------------------------------------------------------------------
class Emit:
    def __init__(self, base=0x1000):
        self.bytes = bytearray()
        self.base = base
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str]] = []  # (offset_into_bytes, label_name)

    def addr(self) -> int:
        return self.base + len(self.bytes)

    def label(self, name: str):
        self.labels[name] = self.addr()

    def b(self, *bs: int):
        for x in bs:
            self.bytes.append(x & 0xFF)

    # LDA #imm
    def lda_imm(self, v): self.b(0xA9, v)
    # LDA abs
    def lda_abs(self, addr): self.b(0xAD, addr & 0xFF, (addr >> 8) & 0xFF)
    # LDA abs,X
    def lda_absX(self, addr): self.b(0xBD, addr & 0xFF, (addr >> 8) & 0xFF)
    # STA abs
    def sta_abs(self, addr): self.b(0x8D, addr & 0xFF, (addr >> 8) & 0xFF)
    # STA abs,X
    def sta_absX(self, addr): self.b(0x9D, addr & 0xFF, (addr >> 8) & 0xFF)
    # LDX #imm
    def ldx_imm(self, v): self.b(0xA2, v)
    # INC abs
    def inc_abs(self, addr): self.b(0xEE, addr & 0xFF, (addr >> 8) & 0xFF)
    # DEC abs
    def dec_abs(self, addr): self.b(0xCE, addr & 0xFF, (addr >> 8) & 0xFF)
    # CMP #imm
    def cmp_imm(self, v): self.b(0xC9, v)
    # BNE rel
    def bne_label(self, label_name: str):
        self.b(0xD0, 0)  # placeholder
        self.fixups.append((len(self.bytes) - 1, ('rel', label_name)))
    # JMP abs
    def jmp_abs(self, addr): self.b(0x4C, addr & 0xFF, (addr >> 8) & 0xFF)
    def jmp_label(self, label_name: str):
        self.b(0x4C, 0, 0)
        self.fixups.append((len(self.bytes) - 2, ('abs', label_name)))
    # RTS
    def rts(self): self.b(0x60)

    def resolve_fixups(self):
        for off, (kind, name) in self.fixups:
            if name not in self.labels:
                raise RuntimeError(f"unresolved label: {name}")
            target = self.labels[name]
            if kind == 'abs':
                self.bytes[off] = target & 0xFF
                self.bytes[off + 1] = (target >> 8) & 0xFF
            elif kind == 'rel':
                # PC at end of branch instruction = self.base + off + 1
                pc = self.base + off + 1
                delta = target - pc
                if not (-128 <= delta <= 127):
                    raise RuntimeError(f"branch out of range: {name} delta={delta}")
                self.bytes[off] = delta & 0xFF


# ----------------------------------------------------------------------------
# Codegen entry point
# ----------------------------------------------------------------------------
SID = 0xD400  # V1 base (ctrl=$D404, etc.)
FREQ_LO_TABLE = 0x4000   # placement of freq_lo table
FREQ_HI_TABLE = 0x4100   # placement of freq_hi table
V_FRAME = 0x50           # zero-page frame counter (since note start)
V_DUR   = 0x51           # zero-page frames-remaining (counts down)
PITCH   = 0x52           # zero-page pitch byte

PLAY_BASE = 0x1000
INIT_ADDR = 0x1000       # init entry
PLAY_ADDR = 0x1003       # play entry (= base + 3 to leave room for JMP)


def emit_instrument_event_at_frame_0(em: Emit, ev):
    """Emit code that executes one atFrame 0 event in init."""
    kind, _, reg, src_kind, src_arg = ev
    assert kind == 'atFrame'
    # Compute value into A, then STA SID+reg
    if src_kind == 'const':
        em.lda_imm(src_arg)
    elif src_kind == 'pitchFreqLo':
        em.lda_absX(FREQ_LO_TABLE)
    elif src_kind == 'pitchFreqHi':
        em.lda_absX(FREQ_HI_TABLE)
    else:
        raise RuntimeError(f"Phase 2 codegen doesn't support source: {src_kind}")
    em.sta_abs(SID + reg)


def emit_instrument_event_at_hr(em: Emit, ev):
    """Emit code that executes one atFrameBeforeNoteEnd event in play."""
    kind, threshold, reg, src_kind, src_arg = ev
    assert kind == 'atFrameBeforeNoteEnd'
    # Caller has already loaded current v_dur into A and compared.
    # We need only emit: LDA #imm; STA SID+reg.
    if src_kind == 'const':
        em.lda_imm(src_arg)
    else:
        raise RuntimeError(f"Phase 2 HR codegen doesn't support source: {src_kind}")
    em.sta_abs(SID + reg)


def emit_init(em: Emit, events, pitch, dur_frames):
    """Emit init(): set up pitch, dur, frame counter, then emit all atFrame 0
    events (the "note start" writes)."""
    em.label('init')
    em.lda_imm(0)
    em.sta_abs(V_FRAME)
    em.lda_imm(dur_frames)
    em.sta_abs(V_DUR)
    em.lda_imm(pitch)
    em.sta_abs(PITCH)

    # Load X with pitch for any pitch-table lookups in atFrame events.
    em.ldx_imm(pitch)
    # Emit all atFrame 0 events
    for ev in events:
        if ev[0] == 'atFrame' and ev[1] == 0:
            emit_instrument_event_at_frame_0(em, ev)
    em.rts()


def emit_play(em: Emit, events, pitch, dur_frames, hr_threshold):
    """Emit play() — runs every frame.

    Bookkeeping:
      INC v_frame
      DEC v_dur — if reaches 0, retrigger the note (re-run init)
      If v_dur == hr_threshold, run all atFrameBeforeNoteEnd events.
    """
    em.label('play')
    em.inc_abs(V_FRAME)
    em.dec_abs(V_DUR)
    # If v_dur reached 0, retrigger via JMP init.
    em.lda_abs(V_DUR)
    em.cmp_imm(0)
    em.bne_label('not_zero')
    em.jmp_label('init')
    em.label('not_zero')
    # If v_dur == hr_threshold, run HR events
    em.cmp_imm(hr_threshold)
    em.bne_label('done_play')
    for ev in events:
        if ev[0] == 'atFrameBeforeNoteEnd':
            emit_instrument_event_at_hr(em, ev)
    em.label('done_play')
    em.rts()


def build_sid() -> bytes:
    em = Emit(base=PLAY_BASE)
    # Layout: at base, JMP init; at base+3, JMP play; then code.
    em.jmp_label('init')      # 0x1000: JMP init
    em.jmp_label('play')      # 0x1003: JMP play
    emit_init(em, CV3I_TEST_EVENTS, TEST_PITCH, TEST_DUR_FRAMES)
    emit_play(em, CV3I_TEST_EVENTS, TEST_PITCH, TEST_DUR_FRAMES, HR_THRESHOLD)
    em.resolve_fixups()

    code_bytes = bytes(em.bytes)

    # Build freq table (placed at FREQ_LO_TABLE / FREQ_HI_TABLE).
    table = gen_pal_freq_table()
    freq_lo = bytes(v & 0xFF for v in table) + b'\x00' * (256 - 96)
    freq_hi = bytes((v >> 8) & 0xFF for v in table) + b'\x00' * (256 - 96)

    # Memory layout the SID will be loaded into:
    #   $1000 .. $1000+len(code_bytes): code
    #   $4000 .. $40FF: freq_lo table (96 entries, rest zero)
    #   $4100 .. $41FF: freq_hi table
    # PSID stores a single contiguous payload starting at $1000.
    # We need to pad between code-end and $4000 with zeros.
    last_code = PLAY_BASE + len(code_bytes)
    pad_to_freq = FREQ_LO_TABLE - last_code
    assert pad_to_freq >= 0, f"code at ${last_code:04X} overlaps freq table at ${FREQ_LO_TABLE:04X}"

    payload = code_bytes + (b'\x00' * pad_to_freq) + freq_lo + freq_hi

    # PSID v2 header (124 bytes)
    header = bytearray(b'PSID')
    header += struct.pack('>HH', 2, 124)  # version=2, data_offset=124
    header += struct.pack('>H', PLAY_BASE)  # load_addr
    header += struct.pack('>H', INIT_ADDR)  # init_addr
    header += struct.pack('>H', PLAY_ADDR)  # play_addr
    header += struct.pack('>H', 1)  # num_songs
    header += struct.pack('>H', 1)  # start_song (1-indexed)
    header += struct.pack('>I', 0)  # speed
    def pad32(s: bytes) -> bytes:
        return (s + b'\x00' * 32)[:32]
    header += pad32(b'USF2 Phase 2 proof')
    header += pad32(b'(test)')
    header += pad32(b'2026')
    header += struct.pack('>H', 0x0014)  # flags: PAL + 6581
    header += struct.pack('>BB', 0, 0)   # startPage, pageLength (PSID v2 fields)
    header += struct.pack('>H', 0)       # reserved
    assert len(header) == 124, f"header length {len(header)} != 124"

    return bytes(header) + payload


def main():
    sid = build_sid()
    sys.stdout.buffer.write(sid)


if __name__ == '__main__':
    main()
