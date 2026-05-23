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

CHIMERA_DIGI_DISPATCHER = bytes.fromhex(
    "c902b0684878a99f8d1503a9a08d1403a2008e0edce88e1ad0682000c258ea60"
    "ee19d02006c24c31ea000000000000004878a9318d1403a9ea8d1503a2018e0e"
    "dcca8e1ad0ea6838e902aaa9358501bde29f8d0aa1bde49f8597a93785014c00"
    "c000b070020100000000000048a90085fda2009d00d4e8e019d0f8684cb09f00"
)
assert len(CHIMERA_DIGI_DISPATCHER) == 128

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

CHIMERA_DIGI = DigiCode(
    dispatcher_base=0x9F80,
    dispatcher=CHIMERA_DIGI_DISPATCHER,
    music_init_patch_off=0x9F9A - 0x9F80,    # `jsr $C200` -> patch to music init
    music_play_patch_off=0x9FA3 - 0x9F80,    # `jsr $C206` -> patch to music play
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
    is_rsid=True,
)


# ---------------------------------------------------------------------------
# Registry — pipelines/hubbard/build_from_usf.py looks up by engine name.
# ---------------------------------------------------------------------------

ENGINE_CONSTANTS: dict[str, EngineConstants] = {
    'chimera': CHIMERA,
    # Add other engines as they migrate onto the USF-only path.
}
