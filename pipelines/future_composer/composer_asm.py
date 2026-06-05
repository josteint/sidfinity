"""FC family asm composer — session 1 foundations.

Multi-session deliverable. This session establishes:

  - The xa65 pipeline (USF → ACME source → xa65 → object → PSID wrapper)
  - The ACME source structure (PSID header, code layout, data emitters)
  - A complete DATA-section emitter (freq table, instruments, sequences,
    patterns, per-subtune setup) from USF.
  - A placeholder for the ENGINE-CODE region: session 1 carries it
    verbatim from the original SID as `!fill` bytes.

Sessions 2-3 will replace the verbatim engine bytes with feature-driven
asm emitters (init/songout/playirq dispatch loop, h2/h3 byte-range
dispatch, pattern byte chain, effect chain). Session 4-5 extends for
Hawkeye's SMC dispatcher + SFX page records.

Per-SID asm regions for Cybernoid II:

  $A600..        engine entry vectors (init/songout/play)
  ...            zero-page allocation, per-voice state arrays
  ...            ok2/song/songout/uitzet/playirq + dispatch chain
  ...            verhoogtest, effect chain (vibrato/glide/pulse/filter/
                 drum/pulse-run/wave-arp/etc.)
  $AE3F          lonote (87 bytes freq lo)        ┐
  $AE96          hinote (87 bytes freq hi)        │ DATA SECTIONS
  $AEED          snelheid (per-subtune speed)     │ — emitted from USF
  $AEEF          seqtabel (per-subtune seq ptrs)  │
  $AEFB          seqloclo/seqlochi runtime slots  │
  $AF01          sequence (pattern_ptr_table)     │
  ...            wavearp/pulsearp/drumtabel/etc.  │
  $AFF4          pulsetabel (4 × 8 bytes)         │
  $B014          instrument records (19 × 8)      │
  ...            vibtabwait/startlen/starttabel   │
  ...            seq0a..seq0c, seq1a..seq1c       │
  ...            patterns st00..st20              ┘

Public entry:
    build_via_asm(cfg) -> bytes      # returns SID file bytes
"""
from __future__ import annotations

import os
import struct
import subprocess
import tempfile
from pathlib import Path

from src.usf import UsfFile, parse
from src.usf.types import MusicSubtune
from pipelines.future_composer.config import FCConfig
from pipelines.future_composer.composer import _load_sid_psid


_ROOT = str(Path(__file__).resolve().parents[2])
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')


# ---------------------------------------------------------------------------
# Data emitters — produce ACME `.byt` directives from USF content
# ---------------------------------------------------------------------------

def _emit_byte_list(label: str, bytes_seq, per_row: int = 12) -> str:
    """Emit `label\\n        .byt $XX,$YY,...` with row wrapping."""
    rows = [f'{label}']
    for i in range(0, len(bytes_seq), per_row):
        row = bytes_seq[i:i + per_row]
        rows.append('        .byt ' + ','.join(f'${b:02X}' for b in row))
    return '\n'.join(rows)


def _emit_freq_tables(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit lonote + hinote tables from USF freq_table (lo/hi interleaved
    192-byte form). Tunes with truncated tables emit only the populated
    entries — the original Cybernoid II has 87, not 96.
    """
    lo = []
    hi = []
    for i in range(cfg.freq_table_entries):
        lo.append(usf.freq_table[i * 2])
        hi.append(usf.freq_table[i * 2 + 1])
    out = [_emit_byte_list('lonote', lo)]
    out.append(_emit_byte_list('hinote', hi))
    return '\n\n'.join(out)


def _emit_snelheid(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit per-subtune speed bytes. Flat layout: 1 byte per USF
    subtune. SMC layout: music_subtune_count + 1 (shared SFX-default).
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if cfg.subtune_layout == 'flat_seqtabel':
        bytes_seq = [(s.tempo - 1) & 0xFF for s in music]
    elif cfg.subtune_layout == 'smc_template_with_sfx':
        bytes_seq = []
        sfx_speed = 0
        for s in music:
            if s.is_sfx:
                sfx_speed = (s.tempo - 1) & 0xFF
            elif s.id - 1 < cfg.music_subtune_count:
                bytes_seq.append((s.tempo - 1) & 0xFF)
        bytes_seq.append(sfx_speed)
    else:
        raise ValueError(f'unknown subtune_layout: {cfg.subtune_layout!r}')
    return _emit_byte_list('snelheid', bytes_seq)


def _emit_instruments(usf: UsfFile, cfg: FCConfig) -> str:
    """Emit 8-byte per-instrument records starting at the `pulsehi`
    label (= instr_records_addr). Slots 0..instr_count-1; USF skips
    all-zero instruments so we fill missing slots with zeros.

    v1: the 4 effect bytes are recomposed from the USF Instrument's
    decomposed fields via `fx_bytes_from_inst`.
    """
    from pipelines.future_composer.to_usf import fx_bytes_from_inst
    slot_to_inst = {i.id - 1: i for i in usf.instruments}
    out = ['pulsehi = * + 0',
           'waveform = * + 1',
           'attdec = * + 2',
           'susrel = * + 3',
           'filcount = * + 4',
           'fx1 = * + 5',
           'fx2 = * + 6',
           'fx3 = * + 7']
    for slot in range(cfg.instr_count):
        inst = slot_to_inst.get(slot)
        if inst is None:
            row = [0] * 8
        else:
            pulse_hi = inst.waveform[0] if inst.waveform else 0
            ctrl     = inst.waveform[1] if len(inst.waveform) > 1 else 0
            fil_count, fx1, fx2, fx3 = fx_bytes_from_inst(inst)
            row = [pulse_hi, ctrl, inst.adsr[0], inst.adsr[1],
                   fil_count, fx1, fx2, fx3]
        out.append('        .byt ' + ','.join(f'${b:02X}' for b in row)
                   + f'  ; inst {slot}')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Engine code region — session 1 placeholder
# ---------------------------------------------------------------------------
#
# Session 1 carries the engine code verbatim from the original SID as
# `!fill N, $XX` (one byte at a time, since ACME's !fill is
# value-uniform). For Cybernoid II the engine region is roughly
# load_addr..freq_lo_addr-1 (everything before the data section). The
# verbatim region also includes the aux tables (wavearp, pulsearp,
# drumtabel, arp programs, filterbytes, pulsetabel) that sit between
# pattern_ptr_table and the instrument records — session 1 doesn't
# yet emit those as USF-derived either.
#
# Sessions 2-3 incrementally replace this with feature-driven asm
# emitters.

# ---------------------------------------------------------------------------
# Engine-code emitters — feature-driven (session 3+ asm composer)
# ---------------------------------------------------------------------------
#
# These emitters produce engine routines from USF features rather than
# carrying HVSC's verbatim bytes. The composer chooses its own layout;
# verification shifts from md5-exact to writelog frame-exact via
# `pipelines.future_composer.verify.verify_asm`.

# FC engine state — fixed RAM allocations the engine reads/writes during
# play. Addresses are the composer's choice; routines reference these
# labels and the assembler resolves them. Sessions 4+ will lay them out
# as a contiguous block at the end of the engine code region.

_FC_STATE_LABELS = """
; --- engine state ---
; testbyte: gates the play loop. 0 = playing, 1 = halted.
; song / songout / ok2 set it; playirq's first instruction tests it.
testbyte:       .dsb 1, 1            ; init to halted

; speedbyte: per-subtune tempo (frames per sequence step). song sets
; this from snelheid,X; playirq reloads speedsto from it.
speedbyte:      .dsb 1, 0
speedsto:       .dsb 1, 0

; Per-voice 3-byte state arrays. Only the few used by song init are
; declared here; sessions 4+ add the rest.
pulseruntest:   .dsb 3, 0            ; song sets to 1,1,1
tabcount:       .dsb 3, 0            ; sequence step (per voice)
begcount:       .dsb 3, 0            ; pattern offset
nootcount:      .dsb 3, 0            ; frames until next note
noho:           .dsb 3, 0            ; base pitch
counter2:       .dsb 3, 0            ; global tick counter

; seqloclo / seqlochi: the current song's 3 voice sequence-stream
; pointers, copied from seqtabel by song init.
seqloclo:       .dsb 3, 0
seqlochi:       .dsb 3, 0

; End-of-state marker — ok2's clear loop runs from tabcount to here.
state_end:
"""


def _emit_song_init_routine(cfg: FCConfig) -> str:
    """Emit the song init routine + songout + ok2 + silence-all.

    Called via PSID init=$LOAD with X = song number. Initializes engine
    state for the selected subtune and silences the SID. Falls through
    from song into silence-all (the ACME `uitzet` label).

    Routine boundaries (each one a callable / branch target):
      song:        from PSID init; sets state, copies seq pointers,
                   primes $D416/$D417/$D418, calls ok2, falls into
                   silence-all.
      silence_all: writes 0 to $D400-$D415 (22 SID registers).
      songout:     marks engine halted; falls into silence-all.
      ok2:         zeros all per-voice state arrays (between tabcount
                   and the end of the state region).

    Frame-exact-visible SID writes during init (in order):
      $D416 ← $00, $D417 ← $01, $D418 ← $10|VOLUME, then 22× ($D4xx ← $00)
    plus whatever the first play() invocation writes (frame 0 in the
    writelog combines init+play).

    Uses straight code (not the ACME source's SMC trick) because
    frame-exact comparison only cares about $D4xx writes; CPU internals
    are free.
    """
    snelheid_addr = cfg.per_subtune_speed_addr
    seqtabel_addr = cfg.seqtabel_addr if cfg.subtune_layout == 'flat_seqtabel' else 0
    if seqtabel_addr == 0:
        raise NotImplementedError(
            f'song init emitter currently supports only flat_seqtabel layout '
            f'(cfg.subtune_layout = {cfg.subtune_layout!r}); SMC dispatcher '
            f'+ SFX page records for Hawkeye still pending')

    return f"""
; --- song init ($LOAD entry; X = song number) ---
; Initializes engine state for the selected subtune. Frame-exact SID
; writes: $D416/$D417 cleared, $D418 = $10|VOLUME, then $D400-$D415
; silenced via the fall-through into silence_all.
song:
        ; testbyte = 1 (halted), pulseruntest[0..2] = 1
        lda #1
        sta testbyte
        sta pulseruntest+0
        sta pulseruntest+1
        sta pulseruntest+2

        ; speedbyte = snelheid[X]
        lda ${snelheid_addr:04X},x
        sta speedbyte

        ; Compute Y-index into seqtabel for subtune X: idx = X*6 + 5
        ; (we copy 6 bytes downward into seqloclo[0..2]/seqlochi[0..2])
        ; Straight code, no SMC trick.
        stx song_tmp
        txa
        asl                          ; *2
        clc
        adc song_tmp                 ; *3
        asl                          ; *6
        adc #5                       ; *6 + 5
        tax

        ldy #5
song_seqcp:
        lda ${seqtabel_addr:04X},x
        sta seqloclo,y               ; seqloclo+0..2, seqlochi+0..2 are
                                     ; contiguous so Y=0..5 covers both
        dex
        dey
        bpl song_seqcp

        ; Filter setup + master volume. After the seqtabel loop, Y=$FF
        ; (the BPL exits when DEY underflows). HVSC writes Y to $D416
        ; ($FF = max cutoff lo), then INY (Y=$00), then writes Y to
        ; $D417 ($00 = filter off / no resonance). This matches what
        ; the frame-exact writelog captures from the original.
        sty $d416                    ; Y=$FF → $D416 ← $FF
        iny
        sty $d417                    ; Y=$00 → $D417 ← $00
        lda #$10 | VOLUME_INIT
        sta $d418                    ; $D418 ← $1F

        jsr ok2
        ; falls through into silence_all (init silences $D400-$D415)

silence_all:
        lda #0
        ldx #$15
silence_loop:
        sta $d400,x
        dex
        bpl silence_loop
        rts

songout:
        lda #1
        sta testbyte
        ; fall through into silence_all
        jmp silence_all

; ok2 — zero every byte from tabcount through the end of the engine
; state arrays, then reset the X-indexed counter2/tabcount/begcount/
; nootcount/noho per-voice arrays explicitly.
ok2:
        lda #0
        ldx #state_end - tabcount - 1
ok2_zero:
        sta tabcount,x
        dex
        bpl ok2_zero

        ; Per-voice arrays reset (overlaps the above for clarity)
        ldx #2
ok2_pv:
        sta tabcount,x
        sta begcount,x
        sta nootcount,x
        sta noho,x
        sta counter2,x
        dex
        bpl ok2_pv

        sta testbyte
        rts

song_tmp: .dsb 1, 0
"""

#
# Cybernoid II's HVSC SID uses a multi-stage trampoline that doesn't
# match the ACME source's natural layout. The PSID-pointed init/play
# vectors at $A600/$A603 jump to a TAX/JMP at $A606 which jumps to a
# SECOND trampoline at $A620 which finally jumps to the real song
# body at $A6CA. The 22-byte zero gap at $A60A-$A61F is engine state
# storage that the engine zero-clears at runtime.
#
# Session 2: emit the trampolines as proper labelled asm. This is the
# simplest chunk to lift out of the verbatim placeholder.

def _emit_trampolines_cybernoid_ii() -> str:
    """Emit the two-stage trampoline at $A600-$A628 plus the
    state-region zero gap.

    HVSC's Cybernoid II uses a multi-stage trampoline. The PSID-pointed
    init/play vectors at $A600/$A603 jump to a TAX/JMP at $A606 which
    jumps to a second trampoline at $A620 which finally jumps to the
    real engine routines at $A6CA/$A70F/$A716. The 22-byte zero gap
    at $A60A-$A61F is engine state storage that the engine zero-clears
    at runtime.

    Targets are raw addresses ($A6CA etc.) so we don't need to define
    labels for them (they live in the verbatim engine region that
    follows). Session 3+ will replace those raw addresses with proper
    labels as more chunks lift out of verbatim.
    """
    return """; --- entry trampolines (session 2 asm) ---
; PSID init=$A600, play=$A603
init    jmp song_tramp           ; $A600 jmp $A606
        jmp play_tramp           ; $A603 jmp $A626
song_tramp                       ; $A606
        tax                      ; save song number from accumulator
        jmp song_body            ; $A607 jmp $A620

; $A60A-$A61F: 22 bytes of state storage (engine zero-clears at runtime)
        .dsb 22, 0

; --- second trampoline at $A620 (3-vector to real routines) ---
song_body                        ; $A620
        jmp $a6ca                ; song body (real routine)
        jmp $a70f                ; songout (real routine)
play_tramp                       ; $A626
        jmp $a716                ; playirq (real routine)
"""


def _emit_verbatim_region(orig_mem: bytes, start_addr: int,
                           end_addr_exclusive: int) -> str:
    """Emit a region of memory as `.byt` bytes. The label is the
    region's start address (for readability)."""
    out = [f'; verbatim bytes ${start_addr:04X}..${end_addr_exclusive-1:04X} '
           f'(session 1 placeholder — engine code to be replaced)']
    bytes_seq = orig_mem[start_addr:end_addr_exclusive]
    for i in range(0, len(bytes_seq), 16):
        row = bytes_seq[i:i + 16]
        out.append('        .byt ' + ','.join(f'${b:02X}' for b in row))
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Top-level asm assembly (Cybernoid II layout)
# ---------------------------------------------------------------------------

def _compose_fc_asm_cybernoid_ii(usf: UsfFile, cfg: FCConfig,
                                  orig_mem: bytes,
                                  orig_code_end: int) -> str:
    """Compose the full ACME asm for a Cybernoid-II-shaped FC SID.

    Session 1 strategy: emit data sections at their exact CPU addresses
    using `* = $XXXX` directives. Engine code + aux-table regions are
    placeholder-emitted as verbatim bytes from the original SID.

    The asm output, when assembled by xa65, produces a binary that
    matches the original SID byte-for-byte (provided the USF preserves
    the relevant fields losslessly).
    """
    load = cfg.freq_lo_addr   # not actually used; we use real load_addr
    # The actual load_addr comes from the original SID's PSID header.
    # Pass it in via a more robust route:
    raise NotImplementedError('use compose_fc_asm() instead')


def compose_fc_asm(usf: UsfFile, cfg: FCConfig,
                   root: str | None = None) -> tuple[str, int]:
    """Compose the full ACME asm + return (asm_text, load_addr).

    Layout strategy:
      - Read the original SID to get load_addr + verbatim engine bytes
      - Emit `* = $LOAD`
      - For each data section in cfg's address map, emit:
          * verbatim bytes from previous-end to section_addr (engine code)
          * `* = $section_addr` (defensive — ensures placement)
          * the section's data emitter from USF
      - Final tail: verbatim bytes after the last data section
    """
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    _hl, load_addr, _init, _play, _n_songs, code, _inline = _load_sid_psid(orig)
    code_end = load_addr + len(code)

    # Materialize the original memory for verbatim emission.
    mem = bytearray(65536)
    mem[load_addr:code_end] = code

    # Cybernoid II's data sections in order. For each, USF reconstructs
    # it; everything between sections is verbatim from the original.
    # The section_end addresses are computed from cfg + USF inputs.
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]

    # snelheid length depends on subtune_layout
    if cfg.subtune_layout == 'flat_seqtabel':
        snelheid_len = len(music_subs)
    else:
        snelheid_len = cfg.music_subtune_count + 1

    raw_sections = [
        ('freq_lo',  cfg.freq_lo_addr,
                     cfg.freq_lo_addr + cfg.freq_table_entries),
        ('freq_hi',  cfg.freq_hi_addr,
                     cfg.freq_hi_addr + cfg.freq_table_entries),
        ('snelheid', cfg.per_subtune_speed_addr,
                     cfg.per_subtune_speed_addr + snelheid_len),
        ('instruments', cfg.instr_records_addr,
                        cfg.instr_records_addr + cfg.instr_count * 8),
    ]

    # The USF-emitted content for each section. Closures take a `limit`
    # so we can truncate a section that's about to overlap its successor
    # (Hawkeye's freq_lo runs into freq_hi by 1 byte — lo[95] aliases
    # hi[0] in the original layout; we only emit the bytes that have a
    # unique address).
    def _emit_lo(limit):
        return _emit_byte_list('lonote',
            [usf.freq_table[i*2] for i in range(limit)])
    def _emit_hi(limit):
        return _emit_byte_list('hinote',
            [usf.freq_table[i*2+1] for i in range(limit)])
    section_emitters = {
        'freq_lo':  _emit_lo,
        'freq_hi':  _emit_hi,
        'snelheid': lambda _n: _emit_snelheid(usf, cfg),
        'instruments': lambda _n: _emit_instruments(usf, cfg),
    }

    # Sort by start; truncate any section that overlaps the next.
    raw_sections.sort(key=lambda s: s[1])
    sections = []
    for i, (name, start, end) in enumerate(raw_sections):
        if i + 1 < len(raw_sections):
            next_start = raw_sections[i + 1][1]
            if end > next_start:
                end = next_start    # truncate — the overlap byte is
                                    # owned by the next section
        sections.append((name, start, end))

    lines = [
        f'; FC asm composer — sessions 1+2 output for {cfg.name}',
        f'; load_addr = ${load_addr:04X}',
        f'; session 1: data sections from USF; session 2: '
        f'engine front-end as asm',
        '',
        f'* = ${load_addr:04X}',
        '',
    ]

    cursor = load_addr

    # Session 2 (cybernoid_ii only): emit the entry trampolines as asm.
    # The next-cursor advances past the second trampoline ($A628) so
    # the verbatim region kicks in from $A629 (speedbyte) onwards.
    if cfg.name == 'cybernoid_ii':
        lines.append(_emit_trampolines_cybernoid_ii())
        cursor = 0xA629    # one past second trampoline's last jmp

    for name, start, end in sections:
        if start > cursor:
            # Emit verbatim engine code from cursor..start-1
            lines.append(f'; --- engine/aux region ${cursor:04X}..${start-1:04X} '
                         f'(verbatim, session 1 placeholder) ---')
            lines.append(_emit_verbatim_region(mem, cursor, start))
            lines.append('')
        elif start < cursor:
            raise ValueError(
                f'section {name} at ${start:04X} overlaps prior section '
                f'(cursor at ${cursor:04X})')
        # Emit the section. Pass the truncated byte count to the
        # emitter so it produces only the bytes that fit before the
        # next section starts.
        n_bytes = end - start
        lines.append(f'; --- {name} ${start:04X}..${end-1:04X} '
                     f'(USF-derived, {n_bytes} bytes) ---')
        lines.append(f'* = ${start:04X}')
        lines.append(section_emitters[name](n_bytes))
        lines.append('')
        cursor = end

    # Final tail: verbatim bytes after the last section
    if cursor < code_end:
        lines.append(f'; --- tail ${cursor:04X}..${code_end-1:04X} '
                     f'(verbatim, session 1 placeholder) ---')
        lines.append(_emit_verbatim_region(mem, cursor, code_end))
        lines.append('')

    return '\n'.join(lines), load_addr


# ---------------------------------------------------------------------------
# xa65 pipeline + PSID wrapping
# ---------------------------------------------------------------------------

def _xa65_assemble(asm_text: str, load_addr: int) -> bytes:
    """Run xa65 on asm_text, return the assembled raw bytes (no PSID
    header). The raw bytes start at the lowest emitted address; xa65
    pads any gaps with zeros."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'src.s')
        obj = os.path.join(td, 'out.bin')
        with open(src, 'w') as f:
            f.write(asm_text)
        # -M allows ':' to appear in comments (MASM-compat mode)
        r = subprocess.run([_XA, '-M', src, '-o', obj],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(
                f'xa65 failed (rc={r.returncode}):\n'
                f'stdout: {r.stdout}\nstderr: {r.stderr}')
        with open(obj, 'rb') as f:
            raw = f.read()
    # xa65 default output is raw bytes (no load-address prefix). The
    # asm's `* = $XXXX` sets the address symbol context only; the
    # output file starts at the lowest emitted byte.
    return raw


# ---------------------------------------------------------------------------
# Feature-driven composition path (incremental — engine emitters replace
# verbatim bytes one chunk at a time, verified via verify_asm writelog)
# ---------------------------------------------------------------------------

def compose_fc_asm_featuredriven(usf: UsfFile, cfg: FCConfig,
                                  root: str | None = None
                                  ) -> tuple[str, int]:
    """Featuredriven asm composition. Replaces HVSC's engine code with
    USF-feature-derived emitters. The composer chooses its own layout
    (engine routines + state) before the data tables; the data tables
    themselves stay at their original addresses (so the verbatim
    sequence/pattern/aux-table streams that follow them continue to
    work).

    Session 1 (this commit) emits:
      - PSID entry jumps at $LOAD
      - song / songout / ok2 / silence_all (the song init chunk)
      - playirq stub (returns immediately — music doesn't play yet)
      - engine state allocations (testbyte, speedbyte, per-voice arrays)

    Sessions 2+ will incrementally replace the playirq stub with real
    h2/h3 dispatch + effect chain emitters, verifying frame-by-frame
    via verify_asm at each step.
    """
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    _hl, load_addr, _i, _p, _n, code, _inline = _load_sid_psid(orig)
    code_end = load_addr + len(code)
    mem = bytearray(65536); mem[load_addr:code_end] = code

    # Data sections (same as compose_fc_asm)
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if cfg.subtune_layout == 'flat_seqtabel':
        snelheid_len = len(music_subs)
    else:
        snelheid_len = cfg.music_subtune_count + 1

    raw_sections = [
        ('freq_lo',  cfg.freq_lo_addr,
                     cfg.freq_lo_addr + cfg.freq_table_entries),
        ('freq_hi',  cfg.freq_hi_addr,
                     cfg.freq_hi_addr + cfg.freq_table_entries),
        ('snelheid', cfg.per_subtune_speed_addr,
                     cfg.per_subtune_speed_addr + snelheid_len),
        ('instruments', cfg.instr_records_addr,
                        cfg.instr_records_addr + cfg.instr_count * 8),
    ]
    def _emit_lo(limit):
        return _emit_byte_list('lonote',
            [usf.freq_table[i*2] for i in range(limit)])
    def _emit_hi(limit):
        return _emit_byte_list('hinote',
            [usf.freq_table[i*2+1] for i in range(limit)])
    section_emitters = {
        'freq_lo':  _emit_lo,
        'freq_hi':  _emit_hi,
        'snelheid': lambda _n: _emit_snelheid(usf, cfg),
        'instruments': lambda _n: _emit_instruments(usf, cfg),
    }
    raw_sections.sort(key=lambda s: s[1])
    sections = []
    for i, (name, start, end) in enumerate(raw_sections):
        if i + 1 < len(raw_sections):
            next_start = raw_sections[i + 1][1]
            if end > next_start:
                end = next_start
        sections.append((name, start, end))

    first_data_addr = sections[0][1]

    lines = [
        f'; FC featuredriven composer — {cfg.name}',
        f'; load_addr = ${load_addr:04X}',
        '',
        '; tune-shared equates',
        'VOLUME_INIT = $0F',
        '',
        f'* = ${load_addr:04X}',
        '',
        '; --- PSID entry trampolines ---',
        'init:   jmp song',
        'play:   jmp playirq',
        '',
        _emit_song_init_routine(cfg),
        '',
        '; --- playirq stub (session-1 placeholder) ---',
        ';',
        '; Returns immediately so music does NOT yet play; verify_asm',
        '; writelog will show frame 0 init writes match HVSC then',
        '; frame 1+ shows nothing from this rebuild (HVSC has play()',
        '; writes; we have none). Each session replaces more of this',
        '; stub with real h2/h3 + effect chain emitters.',
        'playirq:',
        '        lda testbyte',
        '        beq playirq_run',
        '        rts',
        'playirq_run:',
        '        rts',
        '',
        _FC_STATE_LABELS,
        '',
    ]

    # Explicit zero-fill from our engine code's end to the first data
    # table. xa65 does NOT auto-pad gaps between `* = $XXXX` directives
    # — the output file is byte-concatenated regardless of address.
    # So we emit `.dsb first_data_addr - *, 0` to materialize the gap.
    # The fill region is dead bytes — our entry jumps go directly to
    # our song/playirq routines, never executing through here.
    lines.append(f'; fill from end of engine code to first data table')
    lines.append(f'        .dsb ${first_data_addr:04X} - *, 0')
    lines.append('')

    cursor = first_data_addr
    for name, start, end in sections:
        if start > cursor:
            lines.append(f'; --- verbatim aux region ${cursor:04X}..'
                         f'${start-1:04X} ---')
            lines.append(f'* = ${cursor:04X}')
            lines.append(_emit_verbatim_region(mem, cursor, start))
            lines.append('')
        n_bytes = end - start
        lines.append(f'; --- {name} ${start:04X}..${end-1:04X} '
                     f'(USF-derived, {n_bytes} bytes) ---')
        lines.append(f'* = ${start:04X}')
        lines.append(section_emitters[name](n_bytes))
        lines.append('')
        cursor = end

    # Tail (sequences + patterns + remaining aux tables — still verbatim)
    if cursor < code_end:
        lines.append(f'; --- verbatim tail ${cursor:04X}..'
                     f'${code_end-1:04X} ---')
        lines.append(f'* = ${cursor:04X}')
        lines.append(_emit_verbatim_region(mem, cursor, code_end))
        lines.append('')

    return '\n'.join(lines), load_addr


def build_via_asm_featuredriven(cfg: FCConfig,
                                 usf_path: str | None = None,
                                 root: str | None = None) -> bytes:
    """Full featuredriven build path. Reuses the original SID's PSID
    header for now (the header carries title/author/init-vector/etc.,
    which the composer doesn't yet generate from scratch)."""
    if root is None:
        root = _ROOT
    if usf_path is None:
        usf_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(usf_path) as f:
        usf = parse(f.read())

    asm, load_addr = compose_fc_asm_featuredriven(usf, cfg, root=root)
    code_bytes = _xa65_assemble(asm, load_addr)

    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    hl, _la, _i, _p, _n, _c, has_inline = _load_sid_psid(orig)
    if has_inline:
        return orig[:hl] + load_addr.to_bytes(2, 'little') + code_bytes
    return orig[:hl] + code_bytes


def build_via_asm(cfg: FCConfig, usf_path: str | None = None,
                  root: str | None = None) -> bytes:
    """Full build path: USF → ACME asm → xa65 → PSID-wrapped SID bytes.

    Reuses the original SID's PSID header (since session 1 doesn't yet
    emit a from-scratch PSID header — that's a session-2+ concern).
    """
    if root is None:
        root = _ROOT
    if usf_path is None:
        usf_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(usf_path) as f:
        usf = parse(f.read())

    asm, load_addr = compose_fc_asm(usf, cfg, root=root)
    code_bytes = _xa65_assemble(asm, load_addr)

    # Wrap as PSID using the original's header
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    hl, _la, _i, _p, _n, _c, has_inline = _load_sid_psid(orig)

    if has_inline:
        return orig[:hl] + load_addr.to_bytes(2, 'little') + code_bytes
    return orig[:hl] + code_bytes


def verify_via_asm(cfg: FCConfig, root: str | None = None) -> dict:
    """Build via asm composer; compare md5 + report first diffs."""
    import hashlib
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)
    with open(sid_path, 'rb') as f:
        orig = f.read()
    rebuilt = build_via_asm(cfg, root=root)

    md5_orig = hashlib.md5(orig).hexdigest()
    md5_new = hashlib.md5(rebuilt).hexdigest()
    if md5_orig == md5_new:
        return {'ok': True, 'md5': md5_orig, 'size': len(orig)}

    diffs = []
    for i in range(min(len(orig), len(rebuilt))):
        if orig[i] != rebuilt[i]:
            diffs.append(i)
            if len(diffs) >= 32:
                break
    return {
        'ok': False,
        'md5_orig': md5_orig, 'md5_new': md5_new,
        'size_orig': len(orig), 'size_new': len(rebuilt),
        'first_diffs': diffs,
        'sample': [(i, orig[i], rebuilt[i]) for i in diffs[:8]],
    }
