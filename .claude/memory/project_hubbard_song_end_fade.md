---
name: project_hubbard_song_end_fade
description: "Hubbard '85 master-VOL fade is `clamp(BASE - voice_orderpos, 0..$0F)`. EngineConfig knobs: `master_vol_subtrahend_voice` + `master_vol_base` + `master_vol_trigger` (mandatory) + `master_vol_reset_on_loop` + `master_vol_underflow_clamp` + `loop_silences_song` (per-engine quirks). Confuzion + TOAS use it. `tools/audit_d418_fade.py` probes whether any other engine needs it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Several Hubbard '85 engines fade master VOL ($D418) from $0F to $00
over the song's final ~20s — driven by a per-engine counter that the
voice's pattern-end advances. The fade isn't a separate "fade routine"
— it's an implicit consequence of Hubbard's volume formula:
`$D418 = clamp(BASE - voice_orderpos, 0..$0F)`. Once the counter
passes `BASE - $0F` the formula drops below $0F and master VOL fades
to $00 as the song approaches its end.

## Implementation

Six EngineConfig fields (mirrored through USF params and the
composer's `_Inputs`):

- `master_vol_subtrahend_voice` — which voice (0/1/2) drives the
  counter. `None` disables the fade.
- `master_vol_base` — the BASE constant.
- `master_vol_trigger` — `'inst_change'` (Confuzion: fires only on
  instrument-change notes) or `'every_note'` (TOAS: fires on every
  note load including ties).
- `master_vol_reset_on_loop` — when True, set_patptr's $FF handler
  also resets vol_progress to orderLoop[V]. TOAS-style: the counter
  IS the orderlist position. Confuzion-style (default False): the
  counter is independent and never resets.
- `master_vol_underflow_clamp` — when True, the clamp asm handles
  SBC underflow correctly (vol_progress > BASE → write $00). When
  False (default), underflow falls through to the $0F upper-clamp
  branch. Confuzion enables this; TOAS leaves it off because the
  orig engine has the same SBC-underflow shape and verify_all was
  matching via that coincidence.
- `loop_silences_song` — when True, ANY voice hitting $FF in its
  orderlist immediately silences the song: $D418=0, end_phase=2,
  pv_abort=1, v_ended,x=$FF. Subsequent play() calls become no-ops.
  Matches Confuzion's `$0907→$091B→$08B9` path where the $FF handler
  JMPs to the song-silence routine. Default False: $FF is per-voice
  loop-back to orderLoop[V] as usual.

Composer adds a `vol_progress` zp counter ($B9), incremented at the
configured voice's pattern-end (same point `v_orderpos,x` increments
in `note_codec.py`). On every triggering note the composer emits
`$D418 = clamp(BASE - vol_progress, $0F)`. Engines with the fade
enabled also init `$D418=$00` instead of `$0F` so the pre-first-note
frames match the engine's behavior.

## Tick-alignment subtleties (commit 52f0e8a)

Two root causes of off-by-N-frames lag surfaced during the TOAS
work:

1. **Peek-ahead INC.** The engine INCs the voice's orderpos counter
   on the SAME tick the pattern's LAST note loads (engine peeks one
   byte ahead, finds the $FF pattern terminator, INCs, jumps to the
   next pattern). The composer was INCing only on the next load
   attempt when `v_notesleft` hit 0 — exactly `(last_note_dur + 1) ×
   tempo` frames late. Fix: move the INC into `ln_decoded`, gated on
   `v_notesleft==0` (just DEC'd to zero by this load), so it fires
   on the load-tick of the last note.

2. **Per-engine trigger.** Confuzion fires master_VOL only on
   instrument-change notes (engine's bit-7 path at $094C BPL skip).
   TOAS fires on every note load (engine's unconditional $C0C0 block
   after every dur read in the $C086+ path). The `master_vol_trigger`
   field selects which sentinel position in `note_codec` emits the
   clamp+write.

## Confirmed engines

- **Confuzion**: V2 ($0BC2), BASE = $A0, `underflow_clamp=True`,
  `loop_silences_song=True`
- **Thing on a Spring**: V3 ($C46F), BASE = $47, trigger `every_note`,
  `reset_on_loop=True`

## Open question — divergences past the verify window

`tools/audit_d418_fade.py` is the probe — captures both original
and rebuild at 2× songlength, compares $D418 traces, flags any
engine where divergence falls past the 1.5× verify boundary.

- **Confuzion**: RESOLVED across the full 2× window after
  `loop_silences_song=True` landed. The orig $FF handler silences
  the song entirely (any voice's $FF triggers $D418=0 + song-off
  flag), and we now mirror that — no more loop-back, no more
  vol_progress wrap, no more voice-reg divergence past frame ~15650.
  Audit `first_diff: None`.
- **TOAS**: RESOLVED across the full 2× window after
  `master_vol_reset_on_loop=True` landed. The earlier divergence at
  frame 21025 (orig starting its second fade $0F→$06; rebuild stuck
  at $0F) traced to vol_progress climbing monotonically past V3's
  first loop instead of resetting. Voice progression was already
  in lockstep at frame 21025 — only $D418 differed — so the fix
  was the single reset knob, no pattern-data investigation needed
  after all. Audit `first_diff: None`.
