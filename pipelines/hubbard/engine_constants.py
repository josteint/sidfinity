"""Per-engine codegen constants.

These are engine-mechanism — properties of the engine code itself,
not of the tune. Same across all tunes of one engine. Captured here
so the USF-only codegen path can find them without reading the
original SID.

Right now this carries:
  - The 320-byte freq-table region (96 musical entries + scratch /
    arpeggio extension / per-voice init slots).
  - The address constants (instr_base, freq_table_base) that the
    codegen embeds as labels.
  - The voice_starts table (subtune -> voice loop start index).
  - SFX-related layout offsets (has_sfx, sfx_state_ofs,
    sfx_framectr_ofs).

The per-voice init slots inside `freq_bytes` (+205, +208, +214,
+229, +232, +239) are OVERWRITTEN at codegen time with the USF's
init values; what's stored here is just the rest of the region.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DigiCode:
    """Per-engine digi code: dispatcher (at the PSID init address) +
    digi player (called by the dispatcher). The dispatcher's two
    "jsr music_init / jsr music_play" addresses are patched at
    codegen time to point at our music engine.

    All addresses are engine-fixed; the codegen places these bytes
    verbatim at the recorded base addresses."""
    dispatcher_base: int        # where the dispatcher lives (PSID init)
    dispatcher: bytes
    music_init_patch_off: int   # offset in dispatcher of `jsr music_init`
    music_play_patch_off: int   # offset in dispatcher of `jsr music_play`
    player_base: int            # where the digi player lives
    player: bytes
    # Bank table base — the engine's `lda $A000,X` (where X = bank*4)
    # reads {src_lo, src_hi, end_lo, end_hi}. Same memory area carries
    # the validation table at +$10B and a few state bytes (keep_screen,
    # pace placeholder) at +$108 / +$10A.
    bank_table_base: int        # e.g. $A000
    # Where the *music* engine loads in the combined music+digi SID.
    # Default `None` keeps the codegen's global LOAD ($1000) and the
    # combined emitter zero-fills the gap between $1000+music_end and
    # the digi dispatcher (Chimera's $9F80) — that's ~36 KB of zeros
    # in the file. Setting this to a value close to (but not
    # overlapping) the dispatcher_base packs the file tight: e.g.
    # `music_load_addr=$9C00` puts music at $9C00..$9E62 (~610 bytes)
    # with a small gap to dispatcher at $9F80. The PSID still works
    # the same — `init`/`play` are the dispatcher's addresses, the
    # dispatcher's `jsr music_init`/`jsr music_play` are patched to
    # the new music load addr.
    music_load_addr: Optional[int] = None


@dataclass
class EngineConstants:
    instr_base: int
    instr_count: int
    freq_table_base: int
    freq_bytes: bytes                       # 320 bytes
    voice_starts: dict = field(default_factory=dict)  # subtune -> start idx
    has_sfx: bool = False
    sfx_state_ofs: Optional[int] = None
    sfx_framectr_ofs: int = 253
    # Digi support — None when the engine has no digi sub-engine.
    # Required when any subtune is `digi`.
    digi: Optional[DigiCode] = None
    # True if the rebuilt SID must be RSID (KERNAL-mapped, IRQ exit
    # via $EA31). Chimera is RSID; the standard Hubbard '85 music
    # engines are PSID. Determines the file's magic + flags.
    is_rsid: bool = False
    # Off-table arpeggio state-region layout. None = use the codegen's
    # default (Commando-shaped 3-voice layout, shared by Commando,
    # Monty, Devils Galop, Action Biker, Chimera). Human Race has its
    # own 2-voice layout with different offsets.
    state_layout: Optional[object] = None
    # Per-engine offsets within the freq-table region where the six
    # per-voice state variables live. None = Commando defaults
    # (v_ctrl=208, pwm_period=229, pwm_dir=232, v_instr=214,
    # v_durfield=205, v_slide=239). Hunter Patrol's v_slide is at
    # 238 instead of 239 — one byte earlier in the state region.
    seed_offsets: Optional[dict] = None
    # For engines whose off-table note-start reads pattern-position
    # state, the current voice's v_hubidx slot in statebuf must be
    # decremented by 1 to match the engine's v_patpos value at the
    # freq-read moment. Offset = where v_hubidx lives in state_layout
    # (Commando default = 7). Thing on a Spring sets this; others
    # leave it None.
    ns_offtab_decr_offset: Optional[int] = None
    # Whether the note codec resets v_hubidx at pattern end. True =
    # Commando family default; False = Thing on a Spring (v_patpos
    # only wraps on the NEXT note-load frame via the $C160 read).
    hubidx_wrap_at_patend: bool = True


# ---------------------------------------------------------------------------
# Chimera — first engine on the USF-only path
# ---------------------------------------------------------------------------

# Hubbard '85's 96-entry PAL musical freq table — the lookup that
# converts a note number (0..95) to a 16-bit SID freq register.
#
# This is empirical / hand-tuned, NOT strict equal-temperament:
# deriving from 440Hz * 2^(N/12) * 16777216 / 985248 reproduces the
# lower octaves but diverges progressively in higher ones, with entry
# 95 about 60 cents flat relative to standard tuning. Preserved
# verbatim because the original tunes were composed against this
# exact table.
#
# Verified byte-identical across all migrated Hubbard '85 engines
# (Commando, Devils Galop, Monty, Action Biker, Chimera). Each
# engine's full 320-byte region is `HUBBARD_85_PAL_FREQ_TABLE` plus
# 128 bytes of per-engine scratch + arpeggio extension + per-voice
# init slots.
HUBBARD_85_PAL_FREQ_TABLE = bytes.fromhex(
    "1601270138014b015f0173018a01a101ba01d401f0010e022d024e0271029602"
    "bd02e702130342037403a903e0031b045a049b04e2042c057b05ce0527068506"
    "e8065107c1073708b4083709c409570af50a9c0b4e0c090dd00da30e820f6e10"
    "68116e128813af14eb1539179c18131aa11b461d041fdc20d022dc2410275e29"
    "d62b722e3831263442378c3a083eb841a045b849204ebc52ac57e45c70624c68"
    "846e1875107c7083408b7093409c78a558afc8b9e0c498d008dd30ea20f82efd"
)
assert len(HUBBARD_85_PAL_FREQ_TABLE) == 192, len(HUBBARD_85_PAL_FREQ_TABLE)


# Per-engine state region (bytes 192..319 of the freq-table memory
# range). Engine scratch + arpeggio extension + per-voice init slots.
# The codegen overlays USF `init:` values onto +205, +208, +214, +229,
# +232, +239 (see `_freq_bytes_from_usf` in build_from_usf.py).
CHIMERA_FREQ_STATE = bytes.fromhex(
    "00070e00000101530000000707005757414141430000040e02ff002600410000"
    "010017010100000000000002027000340003268ca90000000500794207416986"
    "0204080008410c00000004c801410da00302080002810f0a000005e503410060"
    "00010d0008417989024100000841080a000001000511bf00000005000510bf05"
)
assert len(CHIMERA_FREQ_STATE) == 128

CHIMERA_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + CHIMERA_FREQ_STATE
assert len(CHIMERA_FREQ_BYTES) == 320


DEVILS_GALOP_FREQ_STATE = bytes.fromhex(
    "00070e0000000000000000000000000000000000000000000200000000000000"
    "0000000000000000000000000100c0000000000000ffff000000000000000000"
    "0000000000800241176502410000084108080000010008410939004100000281"
    "080a00000140014149870200000008410200000000000841030a000001800841"
)
assert len(DEVILS_GALOP_FREQ_STATE) == 128

DEVILS_GALOP_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + DEVILS_GALOP_FREQ_STATE
assert len(DEVILS_GALOP_FREQ_BYTES) == 320

# PSID dispatcher source — xa65 asm with equates for the three
# parameter addresses (music_init, music_play, digi_player). Assembled
# at codegen time by `chimera_psid_dispatcher()` below.
#
# Layout:
#   init at MUSIC_DISP_BASE — branch by subtune (cmp #$02).
#     music path  → ldx #$00, stx active_kind, jmp MUSIC_INIT (A preserved).
#     digi  path  → pha, silence loop, pla, lookup pace/bank tables,
#                   jmp DIGI_PLAYER (player rts returns to libsidplayfp).
#   play — switch on active_kind; music subtunes jmp MUSIC_PLAY,
#          digi subtunes rts (digi runs once in init).
#   pace_table / bank_table — 4 slots each, filled by the codegen with
#          per-subtune pace + bank-hi values.
#
# `active_kind` is zp $02 (a slot the engine doesn't use). Stored by
# init, read by play.
CHIMERA_PSID_DISPATCHER_ASM = r"""
MUSIC_INIT   = {music_init}
MUSIC_PLAY   = {music_play}
DIGI_PLAYER  = {digi_player}
active_kind  = $02

* = {base}

init
    cmp #$02
    bcs digi_init
; music — preserve A (the music engine reads it as the subtune number)
    ldx #$00
    stx active_kind
    jmp MUSIC_INIT

digi_init
    pha                     ; save subtune BEFORE clobbering A
    lda #$01
    sta active_kind
    lda #$00
    sta $FD                 ; vol bias = 0
    ldx #$00
silence_loop
    sta $D400,X
    inx
    cpx #$19
    bcc silence_loop
    pla                     ; restore subtune
    sec
    sbc #$02
    tax                     ; X = subtune - 2 (SFX index)
    lda #$35
    sta $01                 ; banking — RAM with I/O
    lda pace_table,X
    sta $A10A
    lda bank_table,X
    sta $97
    lda #$36
    sta $01                 ; banking $36 — no BASIC, so $A000-$BFFF is
                            ; RAM. (Was $37 = default banking, which leaves
                            ; BASIC mapped over $A000-$BFFF and turns the
                            ; JMP into ROM bytes if DIGI_PLAYER lives in
                            ; that range. The player itself ANDs $01 with
                            ; $3E so $36 & $3E = $36 — same target state.)
    jmp DIGI_PLAYER

play
    lda active_kind
    bne digi_play_done
    jmp MUSIC_PLAY
digi_play_done
    rts

pace_table
    .byte $00, $00, $00, $00
bank_table
    .byte $00, $00, $00, $00
"""


def chimera_psid_dispatcher(music_init: int, music_play: int,
                             digi_player: int, base: int) -> dict:
    """Assemble the Chimera PSID dispatcher via xa65.

    Same shape as `assemble_chimera_digi_player`: writes the asm to a
    temp file, runs xa65, reads the binary. The `play`, `pace_table`
    and `bank_table` offsets are derived from the known asm layout
    (the dispatcher's structure is fixed).

    Returns:
        bytes              — the assembled dispatcher bytes
        play_off           — offset of the `play` entry (codegen
                             converts to absolute address for PSID
                             header's `play` field)
        pace_table_off     — offset of the per-subtune pace bytes
        bank_table_off     — offset of the per-subtune bank-hi bytes
    """
    import os
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(here))
    xa = os.path.join(repo, 'tools', 'xa65', 'xa', 'xa')

    asm = CHIMERA_PSID_DISPATCHER_ASM.format(
        music_init=f'${music_init:04X}',
        music_play=f'${music_play:04X}',
        digi_player=f'${digi_player:04X}',
        base=f'${base:04X}',
    )
    src = '/tmp/chimera_psid_dispatcher.s'
    obj = '/tmp/chimera_psid_dispatcher.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([xa, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed on Chimera PSID dispatcher:\n'
                           f'{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        out = f.read()

    # Offsets from the known asm layout. Verified by structure:
    #   init                $00-$03  (cmp #$02, bcs digi_init)
    #   music_init path     $04-$0A  (ldx/stx/jmp = 7 bytes)
    #   digi_init           $0B-$38  (pha + setup + silence + lookup + jmp)
    #   play                $39-$40  (lda/bne/jmp/rts = 8 bytes)
    #   pace_table          $41-$44  (4 bytes)
    #   bank_table          $45-$48  (4 bytes)
    PLAY_OFF       = 0x39
    PACE_TABLE_OFF = 0x41
    BANK_TABLE_OFF = 0x45
    assert len(out) == BANK_TABLE_OFF + 4, len(out)

    return {
        'bytes': out,
        'play_off': PLAY_OFF,
        'pace_table_off': PACE_TABLE_OFF,
        'bank_table_off': BANK_TABLE_OFF,
    }

# Chimera digi player — hand-written xa65 asm equivalent to the
# original $C000-$C130 routine. CIA2-paced 1-bit waveform-toggle
# digi: each sample byte is shifted MSB-first into V1 ctrl
# ($D404 = $41 for bit 0, $49 for bit 1). After 16 audio bytes,
# a vol byte (capped at $0F, biased by $FD) writes $D418. Bank
# table at $A000+bank*4 = {src_lo, src_hi, end_lo, end_hi}.
#
# Cycle-paced via CIA2 timer A (one-shot, reloads from $DD04/$DD05
# which were set to $FFFF, exits the wait loop when the LOW byte
# of the counter drops below the pace threshold).
#
# `pace_cmp + 1` is self-modified at run-time with the per-tune
# pacing byte ($A10A, set by the dispatcher).
#
# Two cycles' difference between this and the original would shift
# the per-frame write distribution; verify_all's _checksum_digi
# already hashes the flat (reg, val) sequence so byte-identity isn't
# required — but in practice this assembles to exactly the original
# 305 bytes (verified via assemble_chimera_digi_player()).
CHIMERA_DIGI_PLAYER_ASM = r"""
* = $C000

; entry vector at $C000 plus 3 dead-data bytes at $C003-$C005
entry
    jmp digi_main
    .byte $4C, $32, $C1     ; dead bytes (jmp $C132 placeholder, never reached)

; main digi entry — save zp scratch, ban BASIC, find bank
digi_main
    lda $F7
    pha
    lda $F8
    pha
    lda $F9
    pha
    lda $FA
    pha
    sei
    lda #$3E
    and $01
    sta $01                 ; banking $36 — RAM plus I/O plus KERNAL, no BASIC
    lda $D011
    sta d011_cache          ; cache for restore at exit
    ldx #$00
    ldy $A103
    cpy #$00
    bne find_bank
    jsr ping
    jmp cleanup

find_bank
    lda $A10B,X
    cmp $97
    beq bank_found
    inx
    dey
    bne find_bank
    jsr ping
    jmp cleanup

; bank validated — set up sample pointers, CIA2 timer, V1
bank_found
    lda $A10A
    sta pace_cmp + 1        ; self-modify the cmp operand in the wait loop
    lda $97
    asl
    asl                     ; X = bank * 4
    tax
    lda $A000,X
    sta $FB                 ; sample src lo
    lda $A001,X
    sta $FC                 ; sample src hi
    lda $A002,X
    sta $F7                 ; sample end lo
    lda $A003,X
    sta $F8                 ; sample end hi
    lda #$FF
    sta $D402               ; V1 PW lo = $FF
    sta $D403               ; V1 PW hi = $FF
    sta $DD04               ; CIA2 timer A latch lo = $FF
    sta $DD05               ; CIA2 timer A latch hi = $FF
    ldy #$00
    lda #$F0
    sta $D406               ; V1 SR = $F0 (long release)
    lda $A108
    bne keep_vic            ; nonzero -> keep VIC running
    lda #$00
    sta $D011               ; else blank VIC (no badlines on sample writes)
keep_vic
    lda #$11
    sta $DD0E               ; start CIA2 timer one-shot
    nop                     ; six nops = ~12 cycles for CIA pickup
    nop
    nop
    nop
    nop
    nop
    jmp vol_read

; pointer advance plus bounds check
advance_check
    inc $FB
    bne check_done
    inc $FC
check_done
    ldx $FC
    cpx $F8
    bcc audio_byte          ; src_hi < end_hi -> continue
    ldx $FB
    cpx $F7
    bcc audio_byte          ; src < end -> continue
    jmp cleanup             ; src >= end -> exit

; 8-bit audio shift, MSB first, paced by CIA2
audio_byte
    lda #$08
    sta $96                 ; 8 bits per byte
    lda ($FB),Y
    sta $FE                 ; shift register

bit_loop
    lda $DD04               ; read CIA2 timer (low byte of counter)
pace_cmp
    cmp #$B0                ; self-modified with pace
    bcs bit_loop            ; wait while timer >= pace
    lda #$11
    sta $DD0E               ; restart timer one-shot
    asl $FE                 ; shift next bit into C
    bcc bit_zero
    lda #$49                ; bit = 1 -> tri + gate
    bne write_ctrl
bit_zero
    lda #$41                ; bit = 0 -> pulse + gate
write_ctrl
    sta $D404
    dec $96
    bne bit_loop            ; more bits in this byte
    dec $F9                 ; rate counter — 16 audio bytes per vol
    bne advance_check       ; not yet at vol — advance plus next audio
    inc $FB                 ; F9 hit 0 -> advance, fall through to vol_read
    bne vol_read
    inc $FC

; vol read — cap, bias, clamp, write $D418
vol_read
    lda ($FB),Y
    cmp #$10
    bcc vol_ok
    lda #$0F                ; cap at $0F
vol_ok
    sec
    sbc $FD                 ; subtract running bias
    bmi vol_clamp
    bne vol_write
vol_clamp
    lda #$01                ; clamp to $01 — never total mute mid-sample
vol_write
    sta $D418
    lda #$10
    sta $F9                 ; reload rate counter
    jmp advance_check

; cleanup — mute, restore VIC, pop scratch, re-enable IRQ, restore banking.
; Order matters. The banking restore (which maps BASIC ROM over
; the $A000-$BFFF range) must come AFTER the last instruction inside
; that range, otherwise the next opcode fetch reads BASIC ROM garbage
; instead of the bytes we just wrote. Restoring it LAST means RTS pops
; into the psiddrv driver page (always RAM) regardless of $01 state.
cleanup
    lda #$00
    sta $D418
    lda d011_cache
    sta $D011
    pla
    sta $FA
    pla
    sta $F9
    pla
    sta $F8
    pla
    sta $F7
    cli
    lda #$03
    ora $01
    sta $01                 ; restore default banking — MUST be last
    rts

; ping — SFX fallback when no valid bank found
ping
    lda #$2A
    sta $D408               ; V2 freq lo
    lda #$F0
    sta $D40D               ; V2 SR
    lda #$0F
    sta $D418               ; vol = $0F
    lda #$11
    sta $D40B               ; V2 ctrl = tri plus gate
    ldy #$FF
ping_outer
    ldx #$FF
ping_inner
    dex
    bne ping_inner
    dey
    bne ping_outer
    lda #$00
    sta $D40B
    sta $D418
    rts

; $D011 cache slot, written at digi_main, read at cleanup
d011_cache
    .byte $9B
"""


def assemble_chimera_digi_player(player_base: int = 0xC000) -> bytes:
    """Run xa65 on `CHIMERA_DIGI_PLAYER_ASM` at the given origin and
    return the 305-byte blob. Cached per player_base."""
    if player_base in _CHIMERA_DIGI_PLAYER_CACHE:
        return _CHIMERA_DIGI_PLAYER_CACHE[player_base]
    import os
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(here))
    xa = os.path.join(repo, 'tools', 'xa65', 'xa', 'xa')
    src = '/tmp/chimera_digi_player.s'
    obj = '/tmp/chimera_digi_player.bin'
    asm = CHIMERA_DIGI_PLAYER_ASM.replace('* = $C000',
                                          f'* = ${player_base:04X}')
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([xa, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed on Chimera digi player asm:\n'
                           f'{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        bs = f.read()
    if len(bs) != 305:
        raise RuntimeError(
            f'Chimera digi player assembled to {len(bs)} bytes, expected 305')
    _CHIMERA_DIGI_PLAYER_CACHE[player_base] = bs
    return bs


_CHIMERA_DIGI_PLAYER_CACHE: dict[int, bytes] = {}

# Chimera PSID DigiCode: the dispatcher is REGENERATED by the
# codegen via `chimera_psid_dispatcher`, not stored verbatim. The
# old RSID dispatcher is replaced with a clean PSID variant that has
# no KERNAL deps + a proper play() entry.
CHIMERA_DIGI = DigiCode(
    dispatcher_base=0x9F80,
    dispatcher=b'',                          # regenerated at codegen time
    music_init_patch_off=0,                  # unused for PSID
    music_play_patch_off=0,                  # unused for PSID
    player_base=0xC000,
    # The player bytes are assembled lazily from CHIMERA_DIGI_PLAYER_ASM;
    # `assemble_chimera_digi_player()` runs xa65 and caches the result.
    # Stored as a sentinel empty bytes here; the codegen calls the
    # assembler when it needs the bytes.
    player=b'',
    bank_table_base=0xA000,
    # Set to None — the combined builder auto-packs the music engine
    # against the dispatcher (two-pass measure + rebuild), so the gap
    # is exactly zero regardless of how the music engine size evolves.
    # Set to an explicit address if you need a fixed layout.
    music_load_addr=None,
)

CHIMERA = EngineConstants(
    instr_base=0xC662,
    instr_count=19,
    freq_table_base=0xC567,
    freq_bytes=CHIMERA_FREQ_BYTES,
    voice_starts={},        # Chimera has no per-subtune voice-start override
    has_sfx=False,
    digi=CHIMERA_DIGI,
    is_rsid=False,          # PSID — no KERNAL, no IRQ-driven playback
)


# ---------------------------------------------------------------------------
# Registry — pipelines/hubbard/build_from_usf.py looks up by engine name.
# ---------------------------------------------------------------------------

DEVILS_GALOP = EngineConstants(
    instr_base=0x183B,
    instr_count=13,
    freq_table_base=0x1694,
    freq_bytes=DEVILS_GALOP_FREQ_BYTES,
    voice_starts={},
    has_sfx=False,
    digi=None,
    is_rsid=False,
)


ACTION_BIKER_FREQ_STATE = bytes.fromhex(
    "00070e0002020b1d1d091000001f2f834121413e3c1f070802ff83850241ff00"
    "1200102700000000000000010238012722060040500002e4ecf4c4c4c4617ce2"
    "c4c4c4e4ecf4c4c4c4151719c5c5c51b65b6acaec2d6ea2a7ecbfe12263a3c50"
    "64788ca0b4c8dc4df05ffdc04683c2014049d12e8b80bf525558c5c5c5c8c8c8"
)
assert len(ACTION_BIKER_FREQ_STATE) == 128

ACTION_BIKER_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + ACTION_BIKER_FREQ_STATE
assert len(ACTION_BIKER_FREQ_BYTES) == 320

ACTION_BIKER = EngineConstants(
    instr_base=0xCB5B,
    instr_count=12,
    freq_table_base=0xC2FC,
    freq_bytes=ACTION_BIKER_FREQ_BYTES,
    # Action Biker subtune 0 starts at V2 (skipping V3); subtunes 1/2 at V3.
    voice_starts={0: 1, 1: 2, 2: 2},
    has_sfx=False,
    digi=None,
    is_rsid=False,
)


MONTY_FREQ_STATE = bytes.fromhex(
    "00070e00040204220a22011301251725414141462643100210ff25080041ff00"
    "7600083e0200011d010000000180003e093408c4260000000080fa00ffff3000"
    "301414811550a9008d04d48d0bd48dff84adfc84290f8dfc840a0a0a0aa8b954"
    "948d0585b955948dfe84b963948d0085b95c948d0285293f8d0185b959948d03"
)
assert len(MONTY_FREQ_STATE) == 128

MONTY_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + MONTY_FREQ_STATE
assert len(MONTY_FREQ_BYTES) == 320

MONTY = EngineConstants(
    instr_base=0x93B4,
    instr_count=20,
    freq_table_base=0x8400,
    freq_bytes=MONTY_FREQ_BYTES,
    voice_starts={},
    has_sfx=True,
    sfx_state_ofs=251,
    sfx_framectr_ofs=250,
    digi=None,
    is_rsid=False,
)


COMMANDO_FREQ_STATE = bytes.fromhex(
    "00070e0000000000000000000000000000000000000000090200000000000000"
    "0000000000000000000000000203020200c000000000000000000000000000ff"
    "000000000000000000a9008d04d48d0bd48d2a55ad2755290f8d27550a0a0a0a"
    "a8b9f9558d3055b9fa558d2955b908568d2b55b901568d2d55293f8d2c55b9fe"
)
assert len(COMMANDO_FREQ_STATE) == 128

COMMANDO_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + COMMANDO_FREQ_STATE
assert len(COMMANDO_FREQ_BYTES) == 320

COMMANDO = EngineConstants(
    instr_base=0x5591,
    instr_count=13,
    freq_table_base=0x5428,
    freq_bytes=COMMANDO_FREQ_BYTES,
    voice_starts={},
    has_sfx=True,
    sfx_state_ofs=None,
    sfx_framectr_ofs=253,
    digi=None,
    is_rsid=False,
)


# Human Race's off-table arp state layout. HR's state region at
# $0DA4 has interleaved per-voice arrays (2 voices, 1 scratch byte
# between each pair), so the offsets are spaced +3 per logical
# array. Mapping to our shared codegen zp:
#   $0DA4..$0DA5 -> sidoff constants [V1=0, V2=7]   (offset 0,1)
#   $0DAD..$0DAE -> v_dur                          (offset 9)
# Only mirror what the off-table arp at the observed pitches reads;
# unmapped offsets stay at the statebuf data-block init value (0).
from pipelines.hubbard.codegen import StatebufLayout, StatebufSlot

HUMAN_RACE_STATE_LAYOUT = StatebufLayout(
    n_voices=2,
    scalars=[
        StatebufSlot(offset=0, kind='const', value=0x00),
        StatebufSlot(offset=1, kind='const', value=0x07),
    ],
    per_voice=[
        StatebufSlot(offset=9, kind='var', var='v_dur'),
    ],
)


HUMAN_RACE_FREQ_STATE = bytes.fromhex(
    "0007000000000000000000000000000000000000000000020000000000000000"
    "000000000000000000000003030302030100c000000000000000000000000000"
    "08413c9f0381000008414c9f0281000001110e000000000009410a0900e10000"
    "02810a090000050008110a0f0000050008410609000001000841040a02000500"
)
assert len(HUMAN_RACE_FREQ_STATE) == 128

HUMAN_RACE_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + HUMAN_RACE_FREQ_STATE
assert len(HUMAN_RACE_FREQ_BYTES) == 320

HUMAN_RACE = EngineConstants(
    instr_base=0x0DE3,
    instr_count=23,
    freq_table_base=0x0CE4,
    freq_bytes=HUMAN_RACE_FREQ_BYTES,
    # HR uses V1+V2 for music; V3 is silent across all subtunes.
    voice_starts={0: 1, 1: 1, 2: 1, 3: 1, 4: 1},
    has_sfx=False,
    digi=None,
    is_rsid=False,
    state_layout=HUMAN_RACE_STATE_LAYOUT,
)


HUNTER_PATROL_FREQ_STATE = bytes.fromhex(
    "00070e0000000001010a03030151510111118100002f04040aff016e0281ff00"
    "02001801010000000000000102203620104cbc6e00000002001eaa0341294004"
    "40084004412840040000ba014119800007080002810a0a0000050000110aa002"
    "00020001411940021008000841050a0000010000810ab0000000000841043002"
)
assert len(HUNTER_PATROL_FREQ_STATE) == 128

HUNTER_PATROL_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + HUNTER_PATROL_FREQ_STATE
assert len(HUNTER_PATROL_FREQ_BYTES) == 320

HUNTER_PATROL = EngineConstants(
    instr_base=0xA427,
    instr_count=32,
    freq_table_base=0xA32D,
    freq_bytes=HUNTER_PATROL_FREQ_BYTES,
    voice_starts={},          # all 3 voices active; defaults to V3-start
    has_sfx=False,
    digi=None,
    is_rsid=False,
    # v_fhi is at $A41B = freq_table_base + 238 (one byte earlier
    # than Commando's +239). Other vars are at the Commando defaults.
    seed_offsets={
        'v_ctrl':     208,
        'pwm_period': 229,
        'pwm_dir':    232,
        'v_instr':    214,
        'v_durfield': 205,
        'v_slide':    238,
    },
)


THING_ON_A_SPRING_FREQ_STATE = bytes.fromhex(
    "00070e002a4c2c0007070701015705054141414558280e0506ff05300041ff41"
    "6f008c3a00010100000001010170003aaf030440e700ffff22003200008181a0"
    "a9008d04d48d0bd48da2c4ad9fc4290f8d9fc40a0a0a0aa8b9a2cd8da8c4b9a3"
    "cd8da1c4b9b1cd8da3c4b9aacd8da5c4293f8da4c4b9a7cd8da6c4b9aecd8da7"
)
assert len(THING_ON_A_SPRING_FREQ_STATE) == 128

THING_ON_A_SPRING_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + THING_ON_A_SPRING_FREQ_STATE
assert len(THING_ON_A_SPRING_FREQ_BYTES) == 320

THING_ON_A_SPRING = EngineConstants(
    instr_base=0xCD2A,
    instr_count=15,
    freq_table_base=0xC3A9,
    freq_bytes=THING_ON_A_SPRING_FREQ_BYTES,
    voice_starts={},          # all 3 voices active
    # 16 SFX overlays at $CDA2 — same 16-byte format as Commando.
    # PSID exposes them as subtunes 1..16 (subtune 0 is the music).
    has_sfx=True,
    digi=None,
    is_rsid=False,
    # Thing on a Spring uses pitch 100 in V2's pattern data; the
    # engine's $C100: LDA $C3A9,Y reads $C471 (= v_patpos[V2]) as
    # the off-table freq value. Our codec's v_hubidx lags v_patpos
    # by 1 at the freq-read moment (orig advances mid-load; ours
    # advances at end), so subtract 1 from the current voice's
    # v_hubidx slot before reading statebuf.
    ns_offtab_decr_offset=7,
    # The engine doesn't wrap v_patpos until $C160's $FF read, so
    # v_hubidx must stay at its post-cumulative value through the
    # sustain frames at end of pattern.
    hubidx_wrap_at_patend=False,
)


ONE_MAN_AND_HIS_DROID_FREQ_STATE = bytes.fromhex(
    "00070e0000000000000000000000000000000000000000000200000000000000"
    "0000000000000000000000000100c000000000000000000000000000ff000000"
    "000000000000a9008d04d48d0bd48d2115ad1e15290f8d1e150a0a0a0aa8b900"
    "168d2715b901168d2015b90f168d2215b908168d2415293f8d2315b905168d25"
)
assert len(ONE_MAN_AND_HIS_DROID_FREQ_STATE) == 128

ONE_MAN_AND_HIS_DROID_FREQ_BYTES = (HUBBARD_85_PAL_FREQ_TABLE
                                    + ONE_MAN_AND_HIS_DROID_FREQ_STATE)
assert len(ONE_MAN_AND_HIS_DROID_FREQ_BYTES) == 320

ONE_MAN_AND_HIS_DROID = EngineConstants(
    instr_base=0x1588,
    instr_count=32,
    freq_table_base=0x1422,
    freq_bytes=ONE_MAN_AND_HIS_DROID_FREQ_BYTES,
    voice_starts={},          # 3 voices active in subtune 0
    # 13 drum/SFX overlays at $1600. PSID exposes them as subtunes
    # 1..13 (subtune 0 is the music).
    has_sfx=True,
    digi=None,
    is_rsid=False,
    # The drum engine's V2 freq sweep wraps Y into the engine's
    # SFX-state block at $151D..$1522 (= freqtab+251..256). Use the
    # shared `_sfx_state_in_freqtab` mechanism (originally written
    # for Monty) to rewire init_sfx + sfxs_go so the SFX state
    # block sits at +251 and the per-step sweep index is mirrored
    # to +254 — matching the engine's exact byte layout.
    sfx_state_ofs=251,
    # The global frame counter lives at $151C = freqtab+$FA (= 250),
    # not Commando's $5525 (= +253).
    sfx_framectr_ofs=250,
)


def _five_title_tunes_freq_bytes(sub_idx: int) -> bytes:
    """Compute freq_bytes for a 5 Title Tunes sub-engine on demand.

    Each sub has its own freq table at its own address — but all are
    near-PAL, so the first 192 bytes match `HUBBARD_85_PAL_FREQ_TABLE`.
    The 128-byte state region is read from the sub's standalone PSID
    (written by `tools/split_multi_binary.py` into
    `pipelines/five_title_tunes/work_subs/`).
    """
    import os
    import sys
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from hubbard_emu import load_sid

    # Per-sub freq table base address (in sub_N.sid's address space).
    FT_BASE = {0: 0x0F6A, 1: 0x1C07, 2: 0x2360, 3: 0x2BA0, 4: 0x34C3}

    sub_path = os.path.join(ROOT, 'pipelines', 'five_title_tunes',
                            'work_subs', f'sub_{sub_idx}.sid')
    if not os.path.exists(sub_path):
        # Try to (re)generate via the splitter.
        import subprocess
        parent = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                              'Hubbard_Rob', '5_Title_Tunes.sid')
        os.makedirs(os.path.dirname(sub_path), exist_ok=True)
        subprocess.run(
            ['python3', os.path.join(ROOT, 'tools', 'split_multi_binary.py'),
             parent, os.path.dirname(sub_path)], check=True)

    _, binary, load = load_sid(sub_path)
    state_start = FT_BASE[sub_idx] - load + 192
    state = bytes(binary[state_start:state_start + 128])
    if len(state) < 128:
        state = state + bytes(128 - len(state))
    assert len(state) == 128, f"sub {sub_idx} state len={len(state)}"
    return HUBBARD_85_PAL_FREQ_TABLE + state


# 5 Title Tunes — five Hubbard '85 sub-engines. Each is its own
# EngineConstants; the v2 byte-exact compound build registers all 5
# via the names 'five_tt_sub0'..'five_tt_sub4'.
FIVE_TITLE_TUNES_SUBS = {}
for _i in range(5):
    _ib = {0: 0x1065, 1: 0x1D02, 2: 0x245B, 3: 0x2C9B, 4: 0x35BE}[_i]
    _ftb = {0: 0x0F6A, 1: 0x1C07, 2: 0x2360, 3: 0x2BA0, 4: 0x34C3}[_i]
    _ic = {0: 8, 1: 12, 2: 12, 3: 12, 4: 12}[_i]
    FIVE_TITLE_TUNES_SUBS[_i] = EngineConstants(
        instr_base=_ib,
        instr_count=_ic,
        freq_table_base=_ftb,
        freq_bytes=_five_title_tunes_freq_bytes(_i),
        voice_starts={},
        has_sfx=False,
        digi=None,
        is_rsid=False,
    )


BATTLE_OF_BRITAIN_FREQ_STATE = bytes.fromhex(
    "00070e00090a322f2f140606021f1f034141413c3921090a02ff03510041ff81"
    "4100932303000001010000000148221d07d046510000000080dc590341585203"
    "100848024158620410082203410a000011080002810c0a0000050000110ff002"
    "00020008415800000004800c415700008100800a415700008100a00a410fff02"
)
assert len(BATTLE_OF_BRITAIN_FREQ_STATE) == 128

BATTLE_OF_BRITAIN_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + BATTLE_OF_BRITAIN_FREQ_STATE
assert len(BATTLE_OF_BRITAIN_FREQ_BYTES) == 320

BATTLE_OF_BRITAIN = EngineConstants(
    instr_base=0x8420,
    instr_count=19,
    freq_table_base=0x8326,
    freq_bytes=BATTLE_OF_BRITAIN_FREQ_BYTES,
    voice_starts={},
    has_sfx=False,
    digi=None,
    is_rsid=False,
)


CONFUZION_FREQ_STATE = bytes.fromhex(
    "00070e00041b052b000002060603870f4181412a351f000302ff034e0041ff00"
    "05004e0c03000000000000020200ff0c170600003358fc0c0c0c241ac5fbac38"
    "d03167b588cc001bd559e7e8e9eaeb9c79d6026364edfc0b0d100f0d0d100f0e"
    "0e0e101011110d100f0f0f0f0f0d0d0e0f0f0f0f0f1000150307080904040e00"
)
assert len(CONFUZION_FREQ_STATE) == 128

CONFUZION_FREQ_BYTES = HUBBARD_85_PAL_FREQ_TABLE + CONFUZION_FREQ_STATE
assert len(CONFUZION_FREQ_BYTES) == 320

CONFUZION = EngineConstants(
    instr_base=0x1146,
    instr_count=12,
    freq_table_base=0x0AFD,
    freq_bytes=CONFUZION_FREQ_BYTES,
    voice_starts={},
    has_sfx=False,
    digi=None,
    is_rsid=False,
)


ENGINE_CONSTANTS: dict[str, EngineConstants] = {
    'chimera': CHIMERA,
    'devils_galop': DEVILS_GALOP,
    'action_biker': ACTION_BIKER,
    'monty': MONTY,
    'commando': COMMANDO,
    'human_race': HUMAN_RACE,
    'hunter_patrol': HUNTER_PATROL,
    'thing_on_a_spring': THING_ON_A_SPRING,
    'one_man_and_his_droid': ONE_MAN_AND_HIS_DROID,
    'battle_of_britain': BATTLE_OF_BRITAIN,
    'confuzion': CONFUZION,
    'five_tt_sub0': FIVE_TITLE_TUNES_SUBS[0],
    'five_tt_sub1': FIVE_TITLE_TUNES_SUBS[1],
    'five_tt_sub2': FIVE_TITLE_TUNES_SUBS[2],
    'five_tt_sub3': FIVE_TITLE_TUNES_SUBS[3],
    'five_tt_sub4': FIVE_TITLE_TUNES_SUBS[4],
    # Unified 5 Title Tunes — ONE engine playing all 5 subtunes. Uses
    # sub_1's freq_bytes (its state region is the only one whose
    # off-table arpeggio bytes are actually read at runtime; the other
    # subs never reach pitch >= 96). Per-subtune state seeding is
    # handled via per_subtune_ovseed at runtime.
    'five_title_tunes': EngineConstants(
        instr_base=0x1000,                          # bookkeeping only
        instr_count=56,                              # 8+12+12+12+12 absolute
        freq_table_base=0x1000,                      # bookkeeping only
        freq_bytes=FIVE_TITLE_TUNES_SUBS[1].freq_bytes,
        voice_starts={},                             # per-subtune via params
        has_sfx=False,
        digi=None,
        is_rsid=False,
    ),
}
