---
name: Hubbard fx_flags bit 3 — PW mode (1985) vs table arp (post-1986)
description: CORRECTED — bit 3 meaning differs by driver generation. 1985 (Commando) = PW mode select. Post-1986 (Chain_Reaction) = table arpeggio.
type: project
---

**CORRECTED 2026-04-26:** Prior claim that bit 3 = table arp in Commando was WRONG.

## 1985 drivers (Commando, etc.)

fx_flags bit 3 = **PW mode selector**:
- bit3=1: Simple unidirectional PW increment (add pw_delta to pw_lo each frame)
- bit3=0: Oscillating bidirectional sweep (bounce between $08xx and $0Exx)

The oscillating mode uses a period counter at $550D,X and direction flag at $5510,X.

Commando PW code at $5230-$52B3:
- $5233: AND #$08 checks bit 3
- bit3=1 path ($5237): simple increment, modifies inst table pw_lo in-place
- bit3=0 path ($524C): oscillating sweep with period counter, boundary checks at $08/$0E (exact equality via BNE)

## Post-1986 drivers (Chain_Reaction, etc.)

fx_flags bit 3 = **table arpeggio** (when combined with bit 1 = skydive):
- `fx & $0A == $0A` → table arp active
- Per-voice frame counter AND #$01 toggles between base note and arp table note
- Arp table at $0E71 (Chain_Reaction), indexed by inst*8
- Each instrument has one arp note (absolute note number)

**Key difference from octave arp:** table arp uses a PER-VOICE counter, not the global $5525.

## Detection

Must identify which driver generation before interpreting bit 3. The 1985 driver has the PW code at AND #$08; BEQ; LDY inst_offset; LDA inst_table,Y. The post-1986 driver has AND #$08; BEQ; LDA per_voice_counter,X.
