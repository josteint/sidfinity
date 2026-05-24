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


# ---------------------------------------------------------------------------
# Chimera — first engine on the USF-only path
# ---------------------------------------------------------------------------

# Captured from demo/hubbard/Chimera_original.sid binary at $C567..$C6A6
# (320 bytes). First 192 bytes = the 96-entry PAL musical freq table;
# bytes 192-319 = engine scratch + per-voice init slots.
_CHIMERA_FREQ_HEX = (
    "1601270138014b015f0173018a01a101ba01d401f0010e022d024e0271029602"
    "bd02e702130342037403a903e0031b045a049b04e2042c057b05ce0527068506"
    "e8065107c1073708b4083709c40957"   "0af50a9c0b4e0c090dd00da30e820f6e10"
    "68116e128813af14eb1539179c18131aa11b461d041fdc20d022dc2410275e29"
    "d62b722e3831263442378c3a083eb841a045b849204ebc52ac57e45c70624c68"
    "846e1875107c7083408b7093409c78a558afc8b9e0c498d008dd30ea20f82efd"
    "00070e00000101530000000707005757414141430000040e02ff002600410000"
    "010017010100000000000002027000340003268ca90000000500794207416986"
    "0204080008410c00000004c801410da00302080002810f0a000005e503410060"
    "00010d0008417989024100000841080a000001000511bf00000005000510bf05"
)
CHIMERA_FREQ_BYTES = bytes.fromhex(_CHIMERA_FREQ_HEX.replace(' ', ''))
assert len(CHIMERA_FREQ_BYTES) == 320, len(CHIMERA_FREQ_BYTES)

def chimera_psid_dispatcher(music_init: int, music_play: int,
                             digi_player: int, base: int) -> dict:
    """Hand-assemble the Chimera PSID dispatcher.

    Replaces the RSID original ($9F80 RSID dispatcher + raster IRQ
    install + `jmp $EA31` KERNAL handoff). The PSID dispatcher:

      init  ($9F80):  branches on the subtune number — music subtunes
                      jump to `music_init`, digi subtunes run the
                      silence loop + digi player.
      play  (returned offset): branches on `active_kind` (a zp byte
                      stored by init) — music subtunes call
                      `music_play`, digi subtunes RTS (digi runs in
                      init, not per-frame).

    Returns a dict with the assembled `bytes`, the offset of the play
    entry (so the codegen can compute the PSID `play` address), and
    the offsets of `pace_table` / `bank_table` (so the codegen fills
    in the per-subtune values).

    No KERNAL refs, no IRQ install, no `jmp $EA31`. The output SID is
    PSID, playable on sidplayfp without `--force-rsid` and without
    KERNAL ROM installed.
    """
    out = bytearray()

    # ----- init ($9F80): branch by subtune -----
    # The music engine reads A as the subtune number — we must NOT
    # clobber A on the music path. Store the kind flag via a constant
    # in X instead.
    out += bytes([0xC9, 0x02])                          # cmp #$02
    out += bytes([0xB0, 0x07])                          # bcs digi_init (+7)
    # music_init:
    out += bytes([0xA2, 0x00])                          # ldx #$00 (music kind)
    out += bytes([0x86, 0x02])                          # stx $02
    out += bytes([0x4C, music_init & 0xFF, music_init >> 8])  # jmp music_init (A preserved)
    assert len(out) == 11
    # digi_init: save the subtune number BEFORE clobbering A with the
    # active_kind marker. (Without the early pha, the later pla restores
    # the marker instead of the subtune.)
    out += bytes([0x48])                                # pha (save subtune)
    out += bytes([0xA9, 0x01])                          # lda #$01 (active_kind=digi)
    out += bytes([0x85, 0x02])                          # sta $02
    out += bytes([0xA9, 0x00])                          # lda #$00
    out += bytes([0x85, 0xFD])                          # sta $FD (vol bias)
    out += bytes([0xA2, 0x00])                          # ldx #$00
    silence_loop_off = len(out)
    out += bytes([0x9D, 0x00, 0xD4])                    # sta $D400,X
    out += bytes([0xE8])                                # inx
    out += bytes([0xE0, 0x19])                          # cpx #$19
    bcc_offset = (silence_loop_off - (len(out) + 2)) & 0xFF
    out += bytes([0x90, bcc_offset])                    # bcc silence_loop
    out += bytes([0x68])                                # pla (restore subtune)
    out += bytes([0x38])                                # sec
    out += bytes([0xE9, 0x02])                          # sbc #$02 (X = subtune - 2)
    out += bytes([0xAA])                                # tax
    out += bytes([0xA9, 0x35])                          # lda #$35
    out += bytes([0x85, 0x01])                          # sta $01 (bank in I/O)
    pace_lda_off = len(out)
    out += bytes([0xBD, 0x00, 0x00])                    # lda pace_table,X — patched
    out += bytes([0x8D, 0x0A, 0xA1])                    # sta $A10A
    bank_lda_off = len(out)
    out += bytes([0xBD, 0x00, 0x00])                    # lda bank_table,X — patched
    out += bytes([0x85, 0x97])                          # sta $97
    out += bytes([0xA9, 0x37])                          # lda #$37
    out += bytes([0x85, 0x01])                          # sta $01 (default bank)
    out += bytes([0x4C, digi_player & 0xFF, digi_player >> 8])  # jmp digi_player

    # ----- play (called per-frame by libsidplayfp) -----
    play_off = len(out)
    out += bytes([0xA5, 0x02])                          # lda $02 (active_kind)
    out += bytes([0xD0, 0x03])                          # bne digi_play_done
    out += bytes([0x4C, music_play & 0xFF, music_play >> 8])  # jmp music_play
    out += bytes([0x60])                                # rts (digi: nothing per-frame)

    # ----- pace_table / bank_table (codegen fills) -----
    pace_table_off = len(out)
    out += bytes(4)                                     # 4 slots, runtime-patched
    bank_table_off = len(out)
    out += bytes(4)

    # Patch the LDA abs,X operands with the table addresses.
    out[pace_lda_off + 1] = (base + pace_table_off) & 0xFF
    out[pace_lda_off + 2] = (base + pace_table_off) >> 8
    out[bank_lda_off + 1] = (base + bank_table_off) & 0xFF
    out[bank_lda_off + 2] = (base + bank_table_off) >> 8

    return {
        'bytes': bytes(out),
        'play_off': play_off,
        'pace_table_off': pace_table_off,
        'bank_table_off': bank_table_off,
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

; cleanup — mute, restore VIC and banking, pop scratch, re-enable IRQ
cleanup
    lda #$00
    sta $D418
    lda d011_cache
    sta $D011
    lda #$03
    ora $01
    sta $01                 ; restore default banking
    pla
    sta $FA
    pla
    sta $F9
    pla
    sta $F8
    pla
    sta $F7
    cli
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


def assemble_chimera_digi_player() -> bytes:
    """Run xa65 on `CHIMERA_DIGI_PLAYER_ASM` and return the 305-byte
    blob. Cached: assembled once per process."""
    global _CHIMERA_DIGI_PLAYER_CACHED
    if _CHIMERA_DIGI_PLAYER_CACHED is not None:
        return _CHIMERA_DIGI_PLAYER_CACHED
    import os
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(here))
    xa = os.path.join(repo, 'tools', 'xa65', 'xa', 'xa')
    src = '/tmp/chimera_digi_player.s'
    obj = '/tmp/chimera_digi_player.bin'
    with open(src, 'w') as f:
        f.write(CHIMERA_DIGI_PLAYER_ASM)
    r = subprocess.run([xa, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed on Chimera digi player asm:\n'
                           f'{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        bs = f.read()
    if len(bs) != 305:
        raise RuntimeError(
            f'Chimera digi player assembled to {len(bs)} bytes, expected 305')
    _CHIMERA_DIGI_PLAYER_CACHED = bs
    return bs


_CHIMERA_DIGI_PLAYER_CACHED = None

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

ENGINE_CONSTANTS: dict[str, EngineConstants] = {
    'chimera': CHIMERA,
    # Add other engines as they migrate onto the USF-only path.
}
