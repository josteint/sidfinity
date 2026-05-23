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

CHIMERA_DIGI_PLAYER = bytes.fromhex(
    "4c06c04c32c1a5f748a5f848a5f948a5fa4878a93e25018501ad11d08d30c1a2"
    "00ac03a1c000d0062009c14ceac0bd0ba1c597f00ae888d0f52009c14ceac0ad"
    "0aa18dacc0a5970a0aaabd00a085fbbd01a085fcbd02a085f7bd03a085f8a9ff"
    "8d02d48d03d48d04dd8d05dda000a9f08d06d4ad08a1d005a9008d11d0a9118d"
    "0eddeaeaeaeaeaea4ccfc0e6fbd002e6fca6fce4f89009a6fbe4f790034ceac0"
    "a9088596b1fb85fead04ddc9b0b0f9a9118d0edd06fe9004a949d002a9418d04"
    "d4c696d0e3c6f9d0c2e6fbd002e6fcb1fbc9109002a90f38e5fd3002d002a901"
    "8d18d4a91085f94c8bc0a9008d18d4ad30c18d11d0a903050185016885fa6885"
    "f96885f86885f75860a92a8d08d4a9f08d0dd4a90f8d18d4a9118d0bd4a0ffa2"
    "ffcad0fd88d0f8a9008d0bd48d18d4609b"
)
assert len(CHIMERA_DIGI_PLAYER) == 305

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
    player=CHIMERA_DIGI_PLAYER,
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
