# USF v3 — Richer Universal SID Format

## Goal

Express SID music in an engine-agnostic way that captures all behavioral details
needed for frame-accurate reproduction. Engine quirks (Hubbard's T[104], drum
mode, speed counter) are resolved by the decompiler into portable USF; the
universal player handles only the universal abstractions.

Scope: tracker music (PSID, single-speed). Cycle-precise digi/demo support is
a future extension that will need additional fields (sample streams, CIA timer
config) but should fit alongside what's defined here without breaking the spec.

## Design principles

1. **Frame-accurate granularity.** Note durations, effect timing, gate-off
   triggers all measured in frames. No ticks, no speed counters.

2. **Behavioral, not procedural.** USF says "instrument cI0 has bidirectional
   PW that bounces between $08 and $0E with step 22 every 4 frames." It does
   NOT say "do X on tick frames, Y on non-tick frames." The player implements
   the behavior.

3. **All engine state lives in USF or is computed by the universal player.**
   No reading "current voice ctrl byte" from arbitrary memory addresses
   (T[104] hack). Anything dynamic is an explicit field.

4. **Self-contained instruments.** An instrument fully describes how it sounds
   over time given a pitch and duration. No engine-global state needed.

## Schema

### NoteEvent (revised)

```lean
inductive NoteKind where
  | pitched : Nat → NoteKind             -- normal pitched note (pitch 0-95)
  | percussion : PercussionKind → NoteKind  -- drum/noise hits
  | rest : NoteKind                       -- silence (gate stays off)
  | tie : NoteKind                        -- continue previous note (no gate retrigger)

inductive PercussionKind where
  | noiseHit : Byte → Byte → PercussionKind  -- (freq_lo, freq_hi) for the hit
  | dynamicCtrl                              -- "use voice ctrl bytes as freq" (Hubbard quirk made explicit)

structure NoteEvent where
  kind         : NoteKind
  durationFrames : Nat                  -- TOTAL frames this note holds the voice (was: ticks)
  instrument   : Nat                    -- index into instrument table
```

Key change: `durationFrames` instead of `duration` ticks. The decompiler
multiplies `dur * tickLength + adjustments` to produce the frame count.

`tie` becomes a `NoteKind`, not a separate flag — clearer semantics.

`percussion` types replace pitch=104+ hacks. The decompiler resolves these.

### Instrument (revised)

```lean
structure ReleaseSpec where
  framesBeforeEnd : Nat   -- gate-off this many frames before note ends (≥2 for ADSR safety)
  zeroAdsr        : Bool  -- write AD=0, SR=0 on release (hard restart)
  noRelease       : Bool  -- if true: no gate-off at all (sustained until next note)

structure Instrument where
  -- Static parameters (set at note-load)
  initFreqMod   : Option InitFreqMod   -- e.g., V2's "load freq from ctrl bytes" trick
  initCtrl      : Byte                  -- ctrl byte at note-on (waveform[0] equivalent)
  initPwLo      : Byte
  initPwHi      : Byte
  ad            : Byte
  sr            : Byte

  -- Per-frame behaviors (running while note plays)
  waveformProgram : List Byte           -- ctrl bytes per frame; loops at waveLoop
  waveLoop        : Nat
  waveStepEvery  : Nat                  -- frames per waveform step (1 = every frame)

  pwMod         : Option PWMod          -- pulse width modulation
  vibrato       : Option Vibrato        -- frequency modulation (LFO)
  freqSlide     : Option FreqSlide      -- monotonic frequency change
  arpeggio      : Option Arpeggio       -- pitch alternation

  -- Effect chain order (the order behaviors run within each frame)
  effectOrder   : List EffectKind       -- e.g., [vibrato, freqSlide, ctrlWrite, arp]

  -- Gate-off behavior
  release       : ReleaseSpec
```

Key changes:
- `waveStepEvery` makes waveform stepping rate explicit (was implicit "every frame")
- `effectOrder` is a list, not a struct of options — explicit execution order
- `release` is its own struct with three behaviors (when, zero ADSR, no release)
- `initFreqMod` handles cases where freq isn't from the freq table

### PWMod (revised)

```lean
inductive PWMode where
  | linear : Byte → PWMode                -- add `speed` to pw_lo each step
  | bidirectional : Byte → Byte → Byte → PWMode  -- (speed, minHi, maxHi)
  | table : List (Byte × Byte) → PWMode   -- explicit (lo,hi) sequence

structure PWMod where
  mode       : PWMode
  stepEvery  : Nat   -- frames between updates (Hubbard's bidir sub-counter lives here)
  startDelay : Nat   -- frames after note-load before PW starts moving (onset)
```

`stepEvery` captures Hubbard's PW bidirectional sub-counter as data: e.g.,
`stepEvery = 4` means PW updates every 4th frame. No engine-specific code needed.

### Vibrato (revised)

```lean
structure Vibrato where
  shape       : LFOShape          -- triangle/sine/square
  periodFrames : Nat               -- one full LFO cycle in frames (8 for Hubbard)
  semitoneShift : Int              -- right-shift count on semitone interval (positive = smaller vibrato)
  onsetFrames : Nat                -- frames after note-load before vibrato active
  rampUpFrames : Nat               -- gradual depth increase (0 = sudden start)
  unipolar    : Bool               -- 0..depth vs -depth..+depth
```

Adds `rampUpFrames` for vibrato that fades in (some engines).
`semitoneShift` replaces ambiguous "depth" with explicit shift count.

### Arpeggio (revised)

```lean
structure Arpeggio where
  intervals    : List Int         -- semitone offsets from base pitch
  stepEvery    : Nat              -- frames per arp step
  phaseSource  : ArpPhase         -- global frame counter or per-voice
  startDelay   : Nat              -- frames before arp activates
```

### FreqSlide (revised)

```lean
inductive FreqSlideKind where
  | monotonic : Int → FreqSlideKind        -- per-step delta in freq_hi units
  | toTarget : Byte → Byte → Int → FreqSlideKind  -- (target_lo, target_hi, max_step)

structure FreqSlide where
  kind        : FreqSlideKind
  stepEvery   : Nat                  -- frames per slide step
  startDelay  : Nat                  -- frames before slide activates
  stopAtZero  : Bool                 -- stop sliding when freq_hi reaches 0
```

`startDelay` captures Hubbard's "skip slide on first frames of note" guard
without needing duration math in the player.

### Pattern + Voice + Song (mostly unchanged)

```lean
structure Pattern where
  notes : List NoteEvent  -- sequence of notes/rests/ties

structure Voice where
  orderlist  : List Nat
  loopPoint  : Option Nat

structure Song where
  freqTable    : List (Byte × Byte)  -- 96 entries (pitch 0-95), no extended hack
  instruments  : List Instrument
  voices       : List Voice          -- length = number of SID voices used (1-3)
  patterns     : List Pattern
  voiceOrder   : List (Fin 3)        -- processing order (e.g., [2,1,0])
  -- No tickLength: durations are in frames directly
```

Key changes:
- `freqTable` is exactly 96 entries (PAL standard). No "extended" engine-specific
  values. Drum/percussion notes use `NoteKind.percussion`.
- No `tickLength`: replaced by `NoteEvent.durationFrames`.

### EffectKind (new — explicit effect chain order)

```lean
inductive EffectKind where
  | vibrato
  | freqSlide
  | pwMod
  | arpeggio
  | waveformStep      -- write current waveform[wPtr] to ctrl
  | gateCheck         -- check if release should fire
```

`Instrument.effectOrder` is a list of these. The universal player runs them
in order each sustain frame. Different engines have different orders;
USF captures the order explicitly.

## What's gone

- `tickLength` — dur is now in frames
- "Extended" freq table entries — replaced by `NoteKind.percussion`
- Implicit effect ordering — now explicit `effectOrder`
- `WriteOrder.custom` — register write order is determined by the player
  (deterministic per effect), not configurable per instrument

## What's added

- `NoteKind` — pitched/percussion/rest/tie as data, not flags
- `Instrument.effectOrder` — explicit chain order
- `*.stepEvery` — sub-frame timing as data (no Hubbard sub-counters)
- `*.startDelay` — onset/skip-first-frames as data
- `Release.noRelease` — for sustained notes
- `Vibrato.rampUpFrames` — gradual onset

## Resolved design questions

### 1. Multispeed

**Resolution:** Frames-in-USF means **play() call counts**, not VBI frames.
Song carries an explicit play rate.

```lean
inductive PlayRate where
  | vbi                    -- one play per VBI (~50Hz PAL, ~60Hz NTSC)
  | cia : UInt16 → PlayRate  -- play every N CPU cycles via CIA timer

structure Song where
  ...
  playRate : PlayRate
```

A note with `durationFrames = 4` lasts 4 play() calls. At PlayRate.vbi this
is 4/50 sec; at `PlayRate.cia 9828` (half-VBI) this is 4/100 sec. The musical
interpretation is consistent; only the wall-clock rate changes.

For Commando: `playRate := .vbi`. For multispeed songs (~9.6% of GT2):
`playRate := .cia <value>`. Decompiler reads CIA setup from the original SID
binary if multispeed.

**Player implication:** Universal player needs CIA timer programming for
non-VBI rates. Defer implementation; the spec field is forward-compatible.

### 2. Filter modulation

**Resolution:** Filter is a song-level resource (one per SID). Model it as
a "filter program" similar to waveform programs.

```lean
inductive FilterMod where
  | static : UInt16 → FilterMod                    -- fixed cutoff
  | linearSweep : UInt16 → Int → Bool → FilterMod  -- (start, perFrameDelta, stopAtBound)
  | program : List UInt16 → Nat → FilterMod        -- (cutoff sequence, loopPoint)
  -- LFO modulation could be added later

structure FilterSpec where
  mode      : FilterMode      -- low/band/high pass
  resonance : Nybble
  cutoffMod : FilterMod

structure Song where
  ...
  filter : Option FilterSpec
```

Filter routing (which voices go through it) is per-instrument:

```lean
structure Instrument where
  ...
  filterEnabled : Bool        -- this instrument routes through the filter
```

The player tracks which voices currently have filterEnabled instruments
playing and writes the routing bits in $D417 accordingly.

For Commando: `filter = none` (no filter used). Most Hubbard songs don't
use the filter; later songs (Crazy Comets, etc.) do.

### 3. Drum patterns / percussion

**Resolution:** Drums are NOT a separate concept. They're regular notes with
`NoteKind.percussion` in regular voice patterns. Drum sounds become "drum
instruments" — special-purpose `Instrument` definitions with appropriate
ADSR, waveform programs, and effects.

Rationale: a drum hit IS just a note that takes over a voice for some frames.
The SID has 3 voices; if a drum plays on V2, V2 is doing the drum (not its
melodic line). This is naturally expressed as a percussion note in V2's pattern
that interrupts the melody.

For Commando: V2's pattern cP8 already has `pitch=104, dur=2, instrument=4`
notes. With USF v3, these become:
```lean
{ kind := .percussion .dynamicCtrl, durationFrames := 6, instrument := 4 }
```
(or `.percussion (.noiseHit lo hi)` for explicit drums)

Decompiler responsibility: detect Hubbard's drum patterns (which use the
T[104] alias trick) and convert them to `percussion` notes.

**For engines with overlay drums** (separate drum engine that uses voices
opportunistically): the decompiler resolves this by INTERLEAVING drum notes
into the voice pattern at the right frames. The drum note "wins" for its
duration, then the voice resumes its melodic pattern.

### 4. Drum mode flag suppression

**Resolution:** No special flag needed. The note kind itself determines behavior.

In Hubbard, the "drum mode" flag suppresses voice effects because the drum
sound IS overlaying the voice — running the voice's effects would clobber
the drum. In USF v3, when a voice is playing a `.percussion` note:
- The percussion's own behavior runs (drum-specific waveform/envelope)
- The voice's normal melodic effects (vibrato, freq slide, arpeggio) DO NOT run
  — they're tied to the percussion instrument, which doesn't have them

The "suppression" is naturally implicit because percussion notes use percussion
instruments which don't define melodic effects.

**No `frameMask`, no `silenceOtherVoices` flag needed.**

### Bonus: stream-style notes (deferred)

For digi/demo SIDs (out of scope for now), USF will need:
- `Sample` events: explicit (cycle, register, value) writes for $D418 streams
- Per-voice cycle-precise event lists for demo waveform tricks
- These would be additional `NoteKind` variants and a "raw stream" mode

The current schema is forward-compatible: adding `NoteKind.sampleStream` or
`NoteKind.cyclePrecise` doesn't break anything.

## Migration path

1. Define new types in `SID.lean` alongside old ones
2. Update `CommandoData.lean` to use new types (decompiler enhancement)
3. Update codegen to read new types
4. Verify F0-F4 still match
5. Verify drum/percussion now matches (the dynamic table issues should disappear)
6. Iterate on remaining diffs

## Verification

For any USF song, verification is:
```
sidplayfp(generateSID(song)) == sidplayfp(original_song.sid)
```
frame-by-frame state match (bisimulation at frame boundaries).

If verification fails, either:
- The decompiler missed a feature (USF doesn't capture everything)
- The codegen has a bug
- The USF spec needs another field

This loop tells us what's still needed.
