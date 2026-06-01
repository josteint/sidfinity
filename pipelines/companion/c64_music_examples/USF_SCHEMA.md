# USF schema design for Commodore_64_Music_Examples

## Constraints

- **Principle**: USF carries *musical* data; engine *mechanism* lives in
  composer / engine_constants.
- **Composer must reproduce the SID instruction stream byte-exact** —
  not the original asm, but the same `(reg, val)` write sequence.
- 15 subtunes:
  - Subs 0, 2, 3, 4-14 use one of 2 engine families (V1-router, V2-router)
  - Sub 1 is Family B (separate engine — deferred)

## Engine variants we have to capture

Per `engine_model.py` + `RE_NOTES.md`, the working 14 subs split across:

| Bucket | Subs | Router | Dispatch else | PWM | PW bounds | Vibrato |
|---|---|---|---|---|---|---|
| V1.a | 0 | V1 | vibrato | sweep | 2..14 | yes |
| V1.b | 2 | V1 | no_vibrato | increment | 2..14 | no |
| V1.c | 3 | V1 | bne_loop | sweep | 3..13 | no |
| V2 | 4-14 | V2 | no_vibrato | increment | 2..14 | no |

These are **engine mechanism**, not musical data. Put in
`engine_constants.py`. The USF carries an engine variant identifier
per subtune.

## Pattern data decoding

Raw pattern bytes are engine-specific encoding. To be principled, USF
should carry decoded musical events:

**V1-router events:**
- `$00..$08` → SET_DURATION_NYBBLE n (event: timbre_nybble_set, value=n)
- `$09..$7F` → PLAY_NOTE n (event: note_on, pitch=note)
- `$80..$8B` → PLAY_NOTE_SUSTAINED n (event: note_on, pitch=n-0x80, tie=true)
- `$8C` → TIMBRE_WRITE (event: ctrl_refresh)
- `$8D` → TIMBRE_WRITE_LOOP (event: ctrl_refresh + loop ptr)
- `$8E` → END_OF_PATTERN_LOOP (event: pattern_loop)
- `$0C/$0D/$0E (bare)` → control variants
- `$0F` → END_OF_PATTERN (event: pattern_end)

**V2-router events:**
- `$00..$7F` → PLAY_NOTE n (with AD+SR+ctrl write; gate-checked)
- `$80..$FE` → mostly note_sustained (bit 7 → no_play if gated)
- `$8C/$8D/$8E` → control variants (timbre / song-end / pattern-loop)
- `$FF`? → end? (need to confirm — Family A used `$0F`)

The DECODED form for USF would be note rows:

```usf
subtune 0 music {
  engine_variant: v1.a
  tempo: 6
  alt_tempo: 10
  frame_ctr_init: 9

  voice 1 {
    init { pw_init: $0008 ad: $09 sr: $28 vibrato_note: $60 }
    orderlist: 1 loop @ 0
    pattern 1 length=N {
      ctrl_refresh   ; ($8C bytes)
      ctrl_refresh
      ...
      pattern_loop
    }
  }
  voice 2 { ... }
  voice 3 { ... }
}
```

## Per-subtune init state mapped to USF init.sid

State byte fields that prime the SID chip (init.sid block):
- AD, SR per voice → already supported in init.sid as `envelope_prime`
- PW init per voice → already supported as `pw_init`
- Ctrl byte → `pw_init` doesn't cover this; need extension

State byte fields that prime engine state (separate from SID):
- frame_ctr_init, tempo, alt_tempo — per-subtune music params
- vibrato_note (V1) — per-subtune (only meaningful for V1.a)
- per-voice PWM phase byte + phase_ctr_init — engine mechanism, in
  engine_constants

## Open design questions

1. **One engine identifier or four?** Options:
   - One: `engine='c64me'` + per-subtune `variant='v1.a'|'v1.b'|...`
   - Four: `engine='c64me_v1a'`, `engine='c64me_v1b'`, etc.
   - One is cleaner; mechanism dispatch happens in composer.
2. **How to capture freq tables?** Each variant has its own freq table
   bytes ($0B5F/$0BDF for V1, $32D8/$3358 for V2). Inline in USF or
   reference by name from engine_constants? The Hubbard '85 family
   inlines (USF v3 principle: self-contained). Probably inline.
3. **PWM ctr per voice (V1+V3) — musical or mechanism?** It's a per-subtune
   tunable but doesn't reflect any musical decision (just sets which
   frame the PWM starts sweeping). Mechanism → engine_constants per
   subtune, OR per-subtune init.sid extension.
4. **Sub 4-14 share an engine — how to express?** USF can have 11 subtunes
   all marked `variant='v2'`; composer emits one engine + 11 per-subtune
   data blocks.

## Next session pickup

- Decide answers to the 4 open questions above
- Define the grammar additions needed (likely none if we reuse existing
  init.sid + per-subtune-params shape + a new `engine: c64me` + per-subtune
  `variant: vX` param)
- Implement extract: `Sub0Emulator` state → USF write
- Verify roundtrip: USF → composer → byte-exact rebuild matching orig
