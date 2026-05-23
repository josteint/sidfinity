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
class EngineConstants:
    instr_base: int
    instr_count: int
    freq_table_base: int
    freq_bytes: bytes                       # 320 bytes
    voice_starts: dict = field(default_factory=dict)  # subtune -> start idx
    has_sfx: bool = False
    sfx_state_ofs: Optional[int] = None
    sfx_framectr_ofs: int = 253


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

CHIMERA = EngineConstants(
    instr_base=0xC662,
    instr_count=19,
    freq_table_base=0xC567,
    freq_bytes=CHIMERA_FREQ_BYTES,
    voice_starts={},        # Chimera has no per-subtune voice-start override
    has_sfx=False,
)


# ---------------------------------------------------------------------------
# Registry — pipelines/hubbard/build_from_usf.py looks up by engine name.
# ---------------------------------------------------------------------------

ENGINE_CONSTANTS: dict[str, EngineConstants] = {
    'chimera': CHIMERA,
    # Add other engines as they migrate onto the USF-only path.
}
