"""USF writer for Commodore_64_Music_Examples — DRAFT (session 10).

Produces a USF v3-style file from per-subtune extracted state +
pattern bytes. Currently a DRAFT format — the existing USF grammar
doesn't yet support C64ME's event-stream pattern rows, so this
writes a starter representation that captures the essential data.

Schema decisions taken this session (per USF_SCHEMA.md):
- One engine identifier `c64me`; per-subtune `variant: v1a|v1b|v1c|v2`.
- Engine variant determines mechanism (dispatch shape, PWM variant,
  PW bounds, freq tables).
- Freq tables inlined (per USF v3 self-contained principle): the V1
  variants share one table, V2 has its own.
- PWM ctr init lives in per-subtune init (it's per-subtune-tunable
  state, not engine constant).

Pattern bytes are currently emitted as a raw `pattern_bytes` field
because the existing grammar's `pattern N length=M { note_row* }`
shape requires pitch+duration semantics that C64ME's event-stream
format doesn't naturally fit. Properly decoding into row-events
needs grammar additions in a future iteration.
"""

from __future__ import annotations
import json
from pathlib import Path

from pipelines.companion.c64_music_examples.extract.engine_model import (
    FamilyAEmulator, V2Emulator, FAMILY_A_INSTANCES,
)


SID_PATH = 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'


def variant_for_subtune(subtune: int) -> str:
    """Engine variant identifier."""
    mapping = {0: 'v1a', 2: 'v1b', 3: 'v1c'}
    if subtune in mapping:
        return mapping[subtune]
    if subtune == 1:
        return 'b'  # Family B (deferred)
    return 'v2'  # subs 4-14


def extract_sub_usf_draft(subtune: int) -> str:
    """Produce a DRAFT USF representation for one Family A subtune."""
    if subtune == 1:
        return "; sub 1 (Family B) — emulator not yet implemented\n"

    variant = variant_for_subtune(subtune)
    if variant.startswith('v1'):
        em = FamilyAEmulator(SID_PATH, subtune)
        bindings = FAMILY_A_INSTANCES.get(subtune)
    else:
        em = V2Emulator(SID_PATH, subtune)
        bindings = FAMILY_A_INSTANCES['shared']

    lines = []
    lines.append(f"subtune {subtune} music {{")
    lines.append(f"  ; engine variant: {variant}")
    lines.append(f"  tempo: {em.tempo}")
    lines.append(f"  params {{")
    lines.append(f"    variant: {variant}")
    lines.append(f"    alt_tempo: {em.alt_tempo}")
    lines.append(f"    frame_ctr_init: {em.frame_ctr}")
    if hasattr(em, 'current_note'):
        lines.append(f"    current_note_init: ${em.current_note:02X}")
    lines.append(f"    v3_pwm_phase: ${em.pwm_phase_v3:02X}")
    lines.append(f"    v3_pwm_ctr_init: ${em.pwm_ctr_v3:02X}")
    lines.append(f"    v1_pwm_phase: ${em.pwm_phase_v1:02X}")
    lines.append(f"    v1_pwm_ctr_init: ${em.pwm_ctr_v1:02X}")
    lines.append(f"    v1_pw_init: ${em.pwm_pw[0]:02X}")
    lines.append(f"    v3_pw_init: ${em.pwm_pw[14]:02X}")
    if variant.startswith('v1'):
        lines.append(f"    v1_pwm_sign_init: ${em.pwm_sign[0]:02X}")
        lines.append(f"    v3_pwm_sign_init: ${em.pwm_sign[14]:02X}")
    lines.append(f"  }}")

    # Per-voice pattern bytes (raw — proper decoding TBD)
    for v_idx, x in enumerate((0, 7, 14)):
        lo, hi = em.zp_ptrs[x]
        start = lo | (hi << 8)
        # Walk pattern
        bytes_out = []
        addr = start
        for _ in range(4000):
            b = em.mem[addr]
            bytes_out.append(b)
            addr = (addr + 1) & 0xFFFF
            if b in (0x0F, 0x8E):
                break
        lines.append(f"  voice {v_idx + 1} {{")
        lines.append(f"    init {{")
        lines.append(f"      timbre: ${em.timbre[x]:02X}")
        lines.append(f"      last_cmd: ${em.last_cmd[x]:02X}")
        lines.append(f"    }}")
        lines.append(f"    pattern_bytes_raw: [")
        for i in range(0, len(bytes_out), 16):
            chunk = bytes_out[i:i + 16]
            lines.append(f"      " + " ".join(f"${b:02X}" for b in chunk))
        lines.append(f"    ]")
        lines.append(f"  }}")
    lines.append(f"}}")
    return "\n".join(lines)


def write_full_usf(out_path: str) -> None:
    """Write the full DRAFT USF covering all 15 subtunes."""
    import struct
    raw = Path(SID_PATH).read_bytes()
    title = raw[0x16:0x36].decode('latin-1').rstrip('\x00')
    author = raw[0x36:0x56].decode('latin-1').rstrip('\x00')
    released = raw[0x56:0x76].decode('latin-1').rstrip('\x00')

    out = []
    out.append(f"psid {{")
    out.append(f'  title:      "{title}"')
    out.append(f'  author:     "{author}"')
    out.append(f'  released:   "{released}"')
    out.append(f"  clock:      PAL")
    out.append(f"  sid:        6581")
    out.append(f"  start_song: 1")
    out.append(f"}}")
    out.append("")
    out.append(f"params {{")
    out.append(f"  engine: c64me")
    out.append(f"}}")
    out.append("")
    out.append(f"init {{ }}")
    out.append("")
    for st in range(15):
        out.append(extract_sub_usf_draft(st))
        out.append("")

    with open(out_path, 'w') as f:
        f.write("\n".join(out))


if __name__ == '__main__':
    out = 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.usf.draft'
    write_full_usf(out)
    import os
    print(f"Draft USF written: {out} ({os.path.getsize(out)} bytes)")
