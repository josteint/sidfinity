---
name: project_thing_on_a_spring
description: Thing on a Spring — FULLY MIGRATED. All 17 PSID subtunes byte-exact (music + 16 SFX overlays). Final commit fbc9fff.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *Thing on a Spring* (1985 Gremlin Graphics). Load
$C000, init $CECB, play $C012. 17 PSID subtunes: subtune 0 = the
song, subtunes 1..16 = SFX overlays (silence the main song and play
just an overlay). Disassembly: `pipelines/hubbard/thing_on_a_spring/disassembly.s`.

**Status (2026-05-25): music subtune 0 voice + filter byte-exact.**
12001/12001 frames match across $D400-$D417 via py65. Fixed in
commit 469966e by adding two shared-core knobs that compensate for
v_hubidx vs v_patpos timing differences.

**Status (2026-05-26, commit 667176a): under the stricter
$D400-$D418 snapshot check, music subtune 0 fails.** Two distinct
divergences:

1. **Frame 0 init quirk**: orig's init leaves $D418=$00; the first
   play() call doesn't write $D418 either, so frame-0 snapshot is
   $00. Frame 1 onward both are $0F. Our codegen sets $D418=$0F in
   init. Single-frame mismatch (= 20 ms), inaudible.
2. **Song-end fade**: from frame 9601 (= 192 s) the orig steps
   $D418 from $0F → $00 every ~95 frames, reaching $00 at frame
   10939, then back to $0F at frame 11041 (song loop). Same pattern
   as Confuzion — see [[project_hubbard_song_end_fade]].

All 16 SFX subtunes still pass under the stricter check. 16/17.

## Parameter deltas from defaults

```
arp_interval=24       # +24 semitone (2-octave) arpeggio
speed_ctr_init=1      # $C494=$01 binary load-time
incby2_step=1         # bit 1 = up-sweep (INC v_fhi_acc, write OLD)
incby2_every_frame=True
incby2_onset=0        # no long-note guard for up-sweep
```

Engine constants:
- `instr_base=$CD2A`, `instr_count=15`, `freq_table_base=$C3A9`.
- State offsets all match Commando defaults (no `seed_offsets`
  override needed).

## Effect audit verdicts

| effect | verdict | parameters |
|---|---|---|
| drum / down-sweep (bit 0) | ≡ `fx_skydive` | existing |
| up-sweep (bit 1) | ≡ `fx_incby2` | step=1, every_frame=True, onset=0 |
| +24 arpeggio (bit 2) | ≡ `fx_arp` | interval=24, period=2 |
| (no bit 3 PWmode) | n/a | n/a |

Zero new USF parameters. ToaS adds nothing new to the schema.

## Shared-core change driven by this migration

Generalized the note-load off-table path in `ns_full` (codegen.py):
the previous hardcoded `pitch==104 -> v_ctrlbyte` case (Commando-
specific) is replaced with a generic `pitch >= 96 -> statebuf`
lookup, mirroring the same approach `fx_arp` already uses for
off-table octave arpeggios. Commando's pitch-104 case still works
because Commando's `state_layout` puts `v_ctrlbyte` at the statebuf
offset (16) that pitch 104 reads.

## The off-table issue and its fix (commit 469966e)

V2 plays pitches 96 and 100 (off-table reads). Pitch 96 reads
statebuf+0/+1 = SID base constants — matches trivially. Pitch 100
reads statebuf+8/+9 = v_hubidx[V2/V3] (Commando layout) ≡
v_patpos[V2/V3] in Thing on a Spring's engine.

Our v_hubidx and Thing on a Spring's v_patpos track the same role
but at slightly different times within a frame:
- **Mid-load timing**: our codec updates v_hubidx at the end of
  load_note (post-cumulative byte count). The engine updates
  v_patpos byte-by-byte during note-load, leaving it at the pitch
  byte position when the freq read fires. Diff = +1.
- **Pattern-end wrap**: our codec wraps v_hubidx to 0 on the
  last note. The engine wraps v_patpos one frame later, when the
  next note-load reads the $FF marker.

Both fixed parametrically:
- `ns_offtab_decr_offset`: subtract 1 from the current voice's
  v_hubidx slot in statebuf after build_statebuf for off-table
  note-starts. Thing on a Spring sets this to 7 (v_hubidx
  position in Commando layout).
- `hubidx_wrap_at_patend`: when False, the codec doesn't reset
  v_hubidx on the last note; the next set_patptr resets it
  instead, matching the engine's timing.

Both defaults preserve existing engines (52/52 unchanged).

## SFX overlays (subtunes 1..16) — also byte-exact (commit fbc9fff)

The "different dispatch model" concern turned out to be wrong. ToaS
exposes 17 PSID subtunes: subtune 0 = music, subtunes 1..16 = SFX
overlays. When `init` is called with A>=1, ToaS's $CEBC path sets
$C497=$C0 (sub-only mode), which silences the main song and runs
only sub_C326 (the SFX engine). Functionally equivalent to
Commando's "subtunes >= 3 select SFX standalone".

Most importantly: ToaS's 16-byte SFX records at $CDA2 use the
**identical byte layout** to Commando's records at $55F9 —
including the flag bits (rate 0-3, direction 4-5, voice-skip 6-7)
and the V2-interval-from-V2.freq_lo aliasing. Hubbard must have
copied the SFX engine across his games.

Implementation: a 2-line `extract_sfx` wrapper + flipping
`has_sfx=True, extract_sfx=extract_sfx` in the config. The shared
codegen's init_sfx / sfx_play handle the rest. N_MUSIC=1 routes
A=1..16 to init_sfx. All 16 SFX subtunes verify byte-exact first
try.

Self-modifying INC/DEC at ToaS's $C35F vs Commando's runtime
branch produces the same per-frame writes, so byte-exact holds.

## Related

- [[feedback_audit_discriminator]] — fx_flags = $02 was unique to
  inst 13, helping disambiguate up-sweep.
- [[reference_audit_tool]] — used for the up-sweep audit.
- [[project_fingerprint_db]] — the off-table pitch-100 case is
  the kind of "engine-specific runtime state read" that the
  fingerprint DB would need to handle as a special case.
