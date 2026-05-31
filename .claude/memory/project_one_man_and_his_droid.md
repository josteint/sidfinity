---
name: project_one_man_and_his_droid
description: "One Man and his Droid — FULLY byte-exact. All 14 subtunes verify md5-exact (music + 13 SFX). The two failing SFX (7 and 11) were fixed in commit 5432dc3 via existing sfx_state_ofs/sfx_framectr_ofs knobs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *One Man and his Droid* (1985 Mastertronic). Load
$1000, init $1000 (trampoline to $1F70), play $1012. 14 PSID
subtunes: subtune 0 = main 3-voice song, subtunes 1..13 =
drum/SFX patterns played through the secondary "drum engine" at
$139F (commandeers V1+V2 for sampled percussion, configured by
sub_1528 from $1600 16-byte recipes). Disassembly:
`pipelines/hubbard/one_man_and_his_droid/disassembly.s`.

**Status (2026-05-25): FULLY byte-exact (14/14 subtunes).**
Music subtune 0 byte-exact (19101 frames). All 13 SFX subtunes
byte-exact. The two previously-failing SFX (7 and 11) were fixed
in commit 5432dc3 by recognizing that One Man and his Droid's SFX
state layout maps to the existing `_sfx_state_in_freqtab`
mechanism (originally written for Monty) — see "SFX off-table"
section below.

## Parameter deltas from defaults

```
arp_interval=12
vib_onset=8                # raw_dur & $1F >= $08 ($11F7 CMP)
arp_period=5               # ARP_MASK=$04, tests bit 2 of frame ctr
arp_phase_invert=True      # NEW: opposite branch sense in fx_arp
incby2_step=-1             # bit 1 "alt slide" DECs v_fhi
incby2_onset=16            # $1338 CMP #$10
incby2_late_gate=24        # $133F CMP #$18 - past-midpoint gate
has_sfx=True
extract_sfx                # 13 SFX records at $1600 (16 bytes each)
```

State offsets match Commando defaults (no `seed_offsets` override).

## New shared-core extension: arp_phase_invert

One Man and his Droid's table arpeggio at $1358 tests `frame_ctr &
$04` with the OPPOSITE polarity from every other Hubbard '85
engine: "non-zero → base pitch, zero → +12 octave". To match
without rewriting `fx_arp`, we added a per-engine `arp_phase_invert`
flag that does an asm-text `.replace('beq fxa_even', 'bne
fxa_even')` at codegen time, flipping the branch sense.

Default False keeps every other engine unchanged.

## SFX off-table: fixed via existing `sfx_state_ofs` mechanism

Some SFX records (notably 6 and 10) produce V2 freq sweeps where
`V2_Y = start*2 - v2_offset` is negative, wrapping Y to $F5..$FF
and reading the engine's runtime scratch at $1517..$1522 as freq
values. These bytes change per-SFX and per-frame.

Initially I thought this would need a per-engine SFX runtime. It
didn't — the shared codegen already has `_sfx_state_in_freqtab`
(originally written for Monty) which:

1. Rewrites init_sfx to mirror the SFX-state block at
   `freqtab+ofs..ofs+5` (disable / index / static / sweep /
   rate / end).
2. Rewrites `sfxs_go` to mirror the POST-advance sweep index to
   `freqtab+ofs+3` each step — so the engine's per-frame
   sample-addr increment is captured.

For One Man and his Droid:
- `sfx_state_ofs=251` → block at +251..256 = $151D..$1522
  (engine's exact SFX-state region).
- `sfx_framectr_ofs=250` → global frame counter at +250 = $151C
  (not Commando's +253).

With these two engine_constants settings, all SFX subtunes including
the off-table-reading ones verify byte-exact. No new shared-core
code was needed.

**Lesson:** when a new engine's SFX off-table reads diverge, check
the existing `sfx_state_ofs` / `sfx_framectr_ofs` knobs first.
The `_sfx_state_in_freqtab` machinery is exactly designed for
"engine's V2 sweep wraps Y into its own scratch region" patterns.

## Songs formula change

While migrating One Man and his Droid (which has 13 SFX, not 16),
the shared codegen's `songs = len(subtunes) + (16 if has_sfx else
0)` formula was generalized to `songs = len(subtunes) +
len(sfx_list)`. Reads actual SFX count from the extractor.

## Related

- [[feedback_audit_discriminator]] — used to disambiguate which
  inst is firing fx_incby2 mid-frame.
- [[reference_audit_tool]] — used to trace v_fhi DEC behavior.
- [[project_thing_on_a_spring]] — has_sfx on both EngineConfig AND
  EngineConstants pattern; same lesson applied here.
