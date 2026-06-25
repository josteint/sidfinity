---
name: project_commando_no_drum_engine
description: "Commando's drum sub-engine never runs in subtune 0. The \"noise drum\" is inst 4 played off the end of the freq table."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Commando's player HAS a drum sub-engine (`_drum_engine` / `_drum_init`,
$53A5-$5427 + $5531; modelled in src/hubbard_emu.py), but it is **never
triggered in subtune 0**. Verified by py65 trace: `drum_state` ($5527)
stays $FF for all 1500 frames — nothing in the play routine ever writes
it a runnable value (bit7 clear). The drum engine `BIT $5527 / BPL`
returns immediately while $5527 has bit7 set.

The audible "noise drum" is **inst 4** — an ordinary instrument played
at **pitch 104**. The freq table at $5428 has only 96 entries, so
inst 4's note-start freq lookup ($5428 + 104*2 = $54F8) runs off the
end into player-state memory (`ctrl_byte` of other voices). Same
off-table space-saving trick as inst 7's octave arpeggio — see
[[feedback_deconstruct_not_reproduce]]. The gritty percussive texture
is a consequence of the short freq table, not a percussion engine.

**Why this matters:** the [[project_usf_refactor]] plan's Phase 5
("the hard case") for SUBTUNE 0 is just "handle inst 4's off-table
cross-voice reads + its inc_by2 effect" — a bounded task. The drum
sub-engine genuinely never runs in the music subtunes (0/1/2).

**CORRECTION (later finding): the "drum sub-engine" IS the SFX engine,
and it DOES run — for subtunes 3-18.** Commando has 19 PSID subtunes:
0/1/2 music, 3-18 sound effects. `init` ($5FB2): A<3 -> music; A>=3 ->
SFX path, which does A-=3 then sets $5527 = (sfx_idx | $40), clearing
bit7 so the drum/SFX engine at $53A5 runs. The engine ($53A5) sweeps
an index down (or up) through the freq table ($5428), writing V1/V2
freq each frame. The trigger ($5531) loads a 16-byte SFX record from
the table at **$55F9** (16 SFX x 16 bytes): byte 0 = flags (rate $0F,
mode $30, skip $C0), bytes 1-7 = V1 SID register block, bytes 8-14 =
V2 block, byte 15 = sweep end index. byte 1 is aliased as both V1
freq_lo and the sweep start index; byte 8 as both V2 freq_lo and the
gate-flags/V2-offset. So a SFX = a 2-voice register snapshot + a
freq-table pitch sweep. See [[project_usf_refactor]] for the SFX
USF-representation plan.

**How to apply:** when an instrument plays at a pitch >= 96, its freq
lookup is an off-table read into engine state — handle it as a
cross-voice reference, not as a frequency. inst 4 reads `ctrl_byte` of
voices 0/1 at a mid-frame moment (before those voices update it), so
exact reproduction needs the cross-voice read timing modelled.
