"""Type B engine emit (Equalizer-shape).

Type B SIDs (10 in Jay_Derrett family):
- B1: Equalizer, Death_or_Glory, Dracula — canonical shape (this file)
- B2: Gun_Runner, Shao-Lins_Road — extended (multi-subtune?)
- B3: Blade_Runner, Space_Doubt, Spindizzy_USA_Version — minimal (no PWM unrolled subs)
- B4: Sqij (2x dur counter), Soundwave_Tubular_Bells (no *5 inst index)

This file implements B1 (canonical Equalizer-shape).

## Equalizer engine architecture (RE'd 2026-06-02)

Different from Type A:
- 5-byte instrument programs (vs Type A's 24/15-byte)
- Per-voice unrolled PWM modulation subroutines (not Y-indexed slab)
- State cells per-voice individual addresses (no slab+stride)
- $Ex wraps at $E3 (3 sub-jump entries, vs NH's 9)
- PWM logic: simple ADD-until-limit + signed-delta oscillation

Same as Type A:
- proc_note byte vocabulary IDENTICAL ($Ex/$Dx/$80/$81/$82/$Bx/$Cx + NOTE)
- Per-voice dur counter at proc_note entry

Equalizer state layout (orig binary):
- $C8AA: tempo counter
- $C8AB: tempo reload
- $C8AC..$C8B1: voice ptrs (V0/V1/V2 lo+hi)
- $C8B2..$C8B4: dur counters per voice
- $C8B5..$C8B7: cur_ctrl per voice
- $C8BF..: instrument programs (5 bytes each)
- $C8E1..$C960: freq lo table (128 bytes)
- $C961..$C9E0: freq hi table (128 bytes)
- $CA03/$CA04: V1 PW lo/hi accumulators
- $CA05/$CA06: V2 PW lo/hi
- $CA07/$CA08: V3 PW lo/hi
- $CA0A/$CA0B: V1 current/saved phase-1 PWM delta
- $CA0D/$CA0E: V2/V3 saved phase-1 PWM delta

Engine multiplexes per-voice state through V1's slots during proc_note
(play_code swaps V2/V3 cells into V1 positions around the proc_note JSR).
This avoids needing per-voice proc_note copies.

NOTE handler:
- Resets V1 PW lo accumulator to 0
- Copies V1's saved phase-1 delta to current (restart oscillation)
- Looks up freq lo/hi from tables, writes to $D400/$D401
- Writes cur_ctrl to $D404 (without gate)
- ORA #$01 + writes again (with gate set — gate retrigger)

$Dx handler:
- byte = inst_id. Index = inst * 5 (via ASL ASL ADC)
- byte 0 → cur_phase1_delta (saved + current)
- byte 1 → cur_ctrl (at $C8B5,X)
- byte 2 → AD (direct STA $D405,X)
- byte 3 → SR (direct STA $D406,X)
- byte 4 → unused

PWM modulation per voice:
- Phase 0: ADD #$40 to PW lo each frame; carry → INC PW hi
- When PW hi >= $08, switch to phase 1
- Phase 1: ADD signed delta to PW lo; if result == 0, flip sign of delta

NOT YET IMPLEMENTED — this is a skeleton. See project_jay_derrett.md
for full plan.
"""
from __future__ import annotations
from pathlib import Path


def emit_asm_type_b(data, load_addr: int, quirks) -> str:
    """Emit clean xa65 asm for a Type B (Equalizer-shape) Jay_Derrett SID.

    NOT YET IMPLEMENTED — placeholder. Need:
    1. Per-voice unrolled PWM subroutines (3 — one per voice)
    2. proc_note dispatch (byte vocab same as Type A — can adapt)
    3. NOTE handler with PWM reset + freq lookup + 2x CTRL writes
    4. $Dx handler with 5-byte program copy to specific cells
    5. Init that sets voice ptrs + cur_ctrl + PWM state cells
    6. Data tables (freq, sub-jump, 5-byte instruments, voice patterns)
    """
    raise NotImplementedError(
        "emit_asm_type_b is a skeleton. See project_jay_derrett.md "
        "for the implementation plan.")
