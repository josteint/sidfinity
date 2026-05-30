---
name: project_hubbard_song_end_fade
description: "Hubbard '85 engines have a song-end $D418 fade we don't yet codegen — visible after verify_all started comparing $D418"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Several Hubbard '85 engines fade master VOL ($D418) from $0F down to
$00 over the final ~20 seconds of the song. The fade steps $D418 by 1
every ~85-100 frames (~1.7-2 sec). Confirmed in:

- **Confuzion**: frames 12727-13861 = 1134 frames at ~87 frames/step
- **Thing on a Spring** (subtune 0 music): frames 9601-10939 at
  ~90-100 frames/step

The fade is driven by an engine-state byte (Confuzion's is $0BC2) that
the disassembly seed doesn't reach because the init code NOPs out the
trigger via self-modifying code (e.g. Confuzion's `LDA #$EA; STA
$08B9` neuters the SEI at $08B9, which is the fade-arm address).
Finding what increments the counter requires deeper trace.

**Why we missed it for so long:** `inst_program.capture` was only
subscribing py65 to the 21 voice registers ($D400-$D414), and
`verify_all` was hashing the raw per-frame write list rather than the
end-of-frame register snapshot. $D418 writes were dropped at the
subscription layer; once expanded ([[reference_audit_tool]]'s analog
on the verify side), the fade became visible as ~600-1400 diff frames
per affected song.

**Likely scope:** every Hubbard '85 tune with a defined end-of-song
probably fades. The 11/85 verify_all run showed three engines failing
on $D418 alone — but most other engines just don't run long enough to
reach the fade phase in their `subtune_frames(passes=1.1)` window.
Suspect the fade is also present in Monty, Action Biker, Commando,
etc., just not exercised. After implementing the fade, re-test ALL
engines at extended duration to confirm.

**Implementation (commit 436b390):**

The fade isn't a separate "fade routine" — it's an implicit consequence
of Hubbard's volume formula. The engine writes
`$D418 = clamp(BASE - voice_orderpos, 0..$0F)` on every
instrument-change note, where `voice_orderpos` is an absolute counter
that increments at every pattern-end and **never wraps on song-loop**.
Once the counter passes `BASE - $0F` the formula drops below $0F and
the master VOL fades to $00 as the song approaches its end.

Two new EngineConfig fields (mirrored through USF params and the
codegen `_Inputs`):
- `master_vol_subtrahend_voice` — which voice (0/1/2) drives the
  counter. None disables the feature.
- `master_vol_base` — the BASE constant.

Confirmed values:
- Confuzion: V2 ($0BC2), BASE = $A0
- Thing on a Spring: V3 ($C46F), BASE = $47

Codegen adds a `vol_progress` zp counter ($B9), incremented at the
configured voice's pattern-end (same point `v_orderpos,x` increments
in note_codec.py). On every instrument-change note the codegen
emits `$D418 = clamp(BASE - vol_progress, $0F)`. Engines with the
fade enabled also init `$D418=$00` instead of `$0F` so the
pre-first-note frames match the engine's behavior.

**Resolved (commit 52f0e8a):** tick-level trace alignment found two
distinct root causes:

1. **Peek-ahead INC.** The engine INCs the V_orderpos counter on the
   SAME tick the pattern's LAST note loads (engine peeks one byte
   ahead at $C15A and finds $FF, INCs $C46D, jumps to $C310). Our
   codegen was INCing only on the next load attempt when v_notesleft
   hit 0 — exactly `(last_note_dur + 1) × tempo` frames late, which
   matched the observed per-pattern lag values:
   - pat 18 last dur=2 → 6 frames lag (3 ticks)
   - pat 5 last dur=5 → 12 frames lag
   - pat 6 last dur=23 → 48 frames lag
   Fix: move the INC into ln_decoded, gated on v_notesleft==0 (just
   DEC'd to zero by this load), so it fires on the load-tick of the
   last note — same tick as the engine's $C46D INC.

2. **Per-engine master_VOL trigger.** Confuzion fires master_VOL
   ONLY on instrument-change notes (engine's bit-7 path at $094C
   BPL skip). TOAS fires on EVERY note load including ties (engine's
   unconditional $C0C0 block after every dur read in the $C086+
   path). New EngineConfig field `master_vol_trigger`
   ('inst_change' default, 'every_note' for TOAS) selects which
   sentinel position in note_codec emits the clamp+write. For
   'every_note' the write lives in ln_decoded so it fires after
   both tie and non-tie paths converge.

Both engines now 100% byte-exact under the strict $D400-$D418
snapshot check (Confuzion 13998 frames, TOAS 12001 frames). Net
verify_all improvement: 81/85 → 83/85.

See [[project_confuzion]] and [[project_thing_on_a_spring]] for the
specific verify numbers.

## Related shared-core gap (different cause)

Action Biker's subtunes 1 and 2 fail at the END of the song (orig
writes $D415/$D416/$D417=$80 at the final frame, our codegen
doesn't). That's a separate end-of-song filter cleanup — inaudible
because no sound is being produced at that moment — and is **not** a
fade. See [[project_action_biker]].
