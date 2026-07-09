# USF v2 — file format specification

USF v2 is the on-disk format for the project's *Unified SID Format*
representation of SID music. One `.usf` file holds everything
except sample audio; samples live in sibling `.flac` files.

The format is the load-bearing input to the codegen. The codegen MUST
NOT peek at any other source — `usf + flacs → sid` is the whole input.

## Goals

- Single source of truth for one tune.
- Human-readable, human-editable in any text editor.
- Footgun-minimal: a small edit either keeps the song consistent or
  fails parse with a precise error.
- Round-trip stable: `parse → write` is byte-identical.
- Engine-agnostic structure; engine-specific fields live in
  `params:` and named effect tokens.

## Files

For tune `Chimera`:

```
Chimera.usf
Chimera.sample2.flac           ; only present if subtune 2 is digi
Chimera.sample3.flac           ; only present if subtune 3 is digi
```

- The `.usf` file is UTF-8.
- Sample files use the convention `<basename>.sample<N>.flac` where
  `N` is the PSID subtune index (0-indexed).
- Sample sidecars carry per-sample metadata in Vorbis comments
  (see `docs/usf_digi_plan.md`).

## Lexical conventions

- Comments start with `;` and run to end of line. They are lossy —
  the writer does not preserve them across a parse/serialize round
  trip.
- Whitespace and blank lines are not significant beyond separating
  tokens.
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`.
- Integers: bare decimal (`12`), or `$`-prefixed hex (`$40`). Never
  `0x40`.
- Strings: double-quoted, e.g. `"Rob Hubbard"`. Used only for PSID
  metadata fields where the content is free-form.
- Block delimiters: `{` and `}`.
- List delimiters: `[` and `]`, comma-separated.

## Top-level structure

```
version: 2
engine: chimera

psid {
  title:      "Chimera"
  author:     "Rob Hubbard"
  released:   "1985 Firebird"
  clock:      PAL
  sid:        6581
  start_song: 1
}

params {
  arp_interval:   12
  arp_period:     8
  linear_pw_or:   $40
  vib_onset:      8
  speed_ctr_init: 2
  incby2_step:    1
  incby2_onset:   $11
}

init {
  voice 1 { ctrl: $41  dur_field: $00  pwm_period: $80  pwm_dir: up  instr: i1 }
  voice 2 { ... }
  voice 3 { ... }
}

instrument 1 lead { ... }
instrument 2 bass { ... }
instrument 3       { ... }     ; unnamed, referenced as i3

subtune 0 music { ... }
subtune 1 music { ... }
subtune 2 digi  { sample: Chimera.sample2.flac }
subtune 3 digi  { sample: Chimera.sample3.flac }
```

Top-level entries appear in this order. The parser enforces it.

## `version`

```
version: 2
```

The first non-comment token of the file. The parser rejects any
version it does not implement, with a clear message.

## `engine`

```
engine: chimera
```

A bare identifier naming the engine pipeline (e.g. `chimera`,
`commando`, `monty`, `devils_galop`, `action_biker`). The codegen
uses this to pick its engine asm + EngineConfig defaults.

## `psid` block

PSID/RSID metadata reproduced in the rebuilt SID file. Fields:

| field        | type    | meaning                                  |
|--------------|---------|------------------------------------------|
| `title`      | string  | song title                               |
| `author`     | string  | composer                                 |
| `released`   | string  | release info (year + label)              |
| `clock`      | keyword | `PAL`, `NTSC`, `both`, or `unknown`      |
| `sid`        | keyword | `6581`, `8580`, `both`, or `unknown`     |
| `sid2`       | keyword | second chip's SID model (multi-SID only) |
| `sid3`       | keyword | third chip's SID model (3SID only)       |
| `start_song` | integer | 1-indexed default subtune                |

`sid2` / `sid3` appear ONLY when the original header states the extra
chip's model explicitly (PSID flags bits 6-7 / 8-9); the spec value
Unknown means "same as the first SID" and is elided. Chip COUNT is
never declared — it derives from the subtunes' voice-block count (see
Multi-SID below). Chip I/O ADDRESSES are pipeline constants (chip 2 =
`$D420`, chip 3 = `$D440`, stamped into the rebuilt header, which is
PSID v3/v4 for 2SID/3SID) — the original's addresses are environment
plumbing, normalized away at extract (the I/O-space analogue of "the
composer always emits the player at $1000").

## `params` block

Engine-specific configuration. Field set depends on the engine but
every field is a value, never a `*Kind` enum (see
`docs/usf_representation_principle.md`). Examples for Hubbard '85:

- `arp_interval`, `arp_period` — arpeggio offset + cycle length
- `vib_onset` — minimum note duration for vibrato to engage
- `linear_pw_or` — OR mask applied to pw_lo in linear-PW mode
- `incby2_step`, `incby2_onset`, `incby2_every_frame` — fx-bit-1 slide
- `speed_ctr_init` — initial tick counter (defers first note-load)
- `first_frame_gate_off` — boolean, frame-0 voice clear
- `freeze_on_stop` — boolean, `$FE` semantics
- `stop_fill` — byte to write on song end, or `none`

Boolean values: `true` / `false`.

## `init` block

Per-voice initial state. Each voice gets a brace-block of named
fields:

```
init {
  voice 1 {
    ctrl:       $41    ; SID V1 ctrl byte at engine init
    dur_field:  $00    ; vibrato carry path initial duration
    pwm_period: $80    ; PWM accumulator
    pwm_dir:    up     ; PWM direction: up / down
    instr:      i1     ; instrument id this voice starts with
    slide_v:    $00    ; cached freq-hi for skydive effect
  }
  voice 2 { ... }
  voice 3 { ... }
}
```

This replaces the original engine's freq-table-overlap-as-state-
storage trick. The codegen places the values wherever convenient in
the output binary.

## `arp_programs { ... }` (FC arpeggio library)

```
arp_programs {
  prog 0: [0, 3, 7]
  prog 1: [0, 4, 7]
  prog 6: [-23, -22, -21, ..., 0]
}
```

Optional. The Future Composer family's arpeggio library: each `prog N`
is the semitone-offset cycle for arp index `N`, which a pattern selects
with a `$7x` command (carried on a note as its instrument ref). Offsets
are signed semitone deltas (`[0,4,7]` = major triad; negatives run the
arp downward). The engine cycles the offsets each frame; the stored
"count" byte is `len(offsets) - 1`, so it is derived on emit, not stored.
The composer lays the programs out and computes the `arplo`/`arphi`
pointer tables itself — replacing the original's verbatim arp tables.

## `pulse_programs { ... }` (FC pulse-width-sweep library)

```
pulse_programs {
  prog 1: lo=4 hi=12 seg 2 48 seg 4 48 seg 6 48
  prog 2: lo=4 hi=12 wrap seg 4 128 seg 8 96 seg 12 64
}
```

Optional. Each `prog N` (selected by an instrument's `pulse_prog.program`)
is a pulse-width sweep shape: PW ramps between bound `lo` and `hi`, and the
step rate switches to `S` when a counter crosses threshold `T` (`seg T S`).
`flip` after a segment reverses sweep direction at that threshold; `wrap`
snaps at the bound instead of bouncing. Exactly three segments. The composer
emits the 8-byte-per-program `pulsetabel` from these fields.

## `filter_programs { ... }` (FC filter cutoff-envelope library)

```
filter_programs {
  prog 0: init=160 d418=31 final=128 end=98 seg 2 254 seg 34 2 seg 66 255
}
```

Optional. Each `prog N` (an instrument's `filter_prog.program`) is a filter
cutoff envelope: the `$D416` cutoff starts at `init`, gains each segment's add
value as a counter crosses that segment's threshold (`seg T A`), and snaps to
`final` once the counter passes `end`; `d418` is written to `$D418` (master
volume + filter routing). Exactly three segments. The composer lays the
10-byte programs out and computes the `filterbytes` pointer table itself.

## `drum_programs { ... }` (FC percussion library)

```
drum_programs {
  drum 0: wave=[129, 65, 64, 64, ...] tone=[52, 10, 8, 6, ...]
}
```

Optional. Each `drum N` (an instrument's `fx1 & $0F` when its drum flag is
set) is a short percussion program played one step per frame: `wave[k]` is
written to the `$D404` waveform control and `tone[k]` is the pitch offset.
The two lists are parallel (same length). The composer emits the engine's
`dwa` waveform program (a leading length byte = `len(wave)+1`, then the wave
bytes) and `dto` tone program, and computes the `drumtabel` pointer table
(4 bytes/drum) itself.

## FC flat aux tables (`attack_len` / `attack_wave` / `wave_arp` / `pulse_arp`)

```
attack_len  = [2, 2, 2, 2, 5, ...]
attack_wave = [129, 129, 129, 129, 65, ...]
wave_arp    = [64, 64, 64, 64]
pulse_arp   = [6, 7, 8, 9, 10, 9, 8, 7]
```

Optional flat per-index value lists. `attack_len[w]`/`attack_wave[w]` are the
note-attack frame count and `$D404` waveform for wave index `w` (the engine's
`startlen`/`starttabel`). `wave_arp` cycles the `$D404` waveform (indexed
`counter2 & 3`) and `pulse_arp` cycles `$D403` pulse-hi (`counter2 & 7`). The
composer emits each at its engine address.

## `default_filter { ... }` (DMC V5 idle V3 filter sweep)

```
default_filter { start=$B600 repeat=0 seg (2056, $3808) seg (-100, $0032) }
```

Optional. The **default (idle) filter-cutoff sweep** the engine applies to
voice 3 by default — from song start, before/between explicit per-instrument
filter notes (for a tune whose V3 never plays a filtered note, this is the
whole filter motion). Same `start=` / `repeat=` / `seg (rate, frames)` form as
an instrument's `filter_env` (one musical object, per the representation
principle): a cutoff sweep. This is **play-time content** — a sweep the play
loop performs — *not* init priming; the initial cutoff **state** stays in
`init.sid.filter` (the init trichotomy: priming = initial state, this =
behaviour). `start` records that initial cutoff for a complete SweepEnvelope;
the composer continues from the `init.sid.filter` priming and applies these
phases (the idle program has no start of its own). Absent ⇒ the cutoff holds
at the priming value.

## `default_pulse { ... }` (DMC V5 idle pulse-width sweep)

```
default_pulse { start=$0000 seg (49, $FFFF) }
```

Optional. The pulse twin of `default_filter`: the **default (idle) pulse-width
sweep** a voice runs from pulse position 0 (`pulse_run` is unconditional;
`pulsepos` clears to 0 at init) until an instrument with a pulse program restarts
it. Same `swenv_args` form (a PW `SweepEnvelope`, Rule 1), **play-time content**,
one shared program all voices index. Captured only when pulse position 0 is a
real ADD program; absent ⇒ the PW holds (the engine's null pos-0).

## `instrument N name { ... }`

```
instrument 1 lead {
  waveform: $41 $49
  loop:     1
  pwm:      mode=linear speed=0 init=$800 min_hi=0 max_hi=0
  adsr:     $09 $A9
  arp:      offsets=[0, 12] period=2
  vibrato:  scale=0
  envelope: gate_off_delta=0 adsr_zero_delta=0
}
```

- `N` is the instrument id (1-indexed, no zero-padding — `i1` not `i01`).
- `name` is optional; if present, the instrument is referenceable as
  `i:name` anywhere `i N` is expected. Names: `[A-Za-z_][A-Za-z0-9_]*`.
- Fields:
  - `waveform`: a sequence of ctrl bytes (the wave-table program).
  - `loop`: zero-based index into `waveform` where the program loops.
  - `pwm`: `mode=` is one of `linear`, `bidirectional`, `none`.
    `speed`, `init`, `min_hi`, `max_hi` parametric.
  - `adsr`: two bytes — attack/decay + sustain/release.
  - `arp`: `offsets=[...]` (list of semitone offsets including the
    base 0), `period=` (cycle length).
  - `vibrato`: `scale=` (depth).
  - `envelope`: `release_ctrl=` (CTRL byte written during release),
    `gate_mode=` one of `hold` (gate until note end, default),
    `release_early` (gate drops a few frames after attack), `open`
    (gate never drops), and `gate_open=1` (elidable; the never-release
    toggle is ALSO set alongside `gate_mode=hold` — the two are
    independent editor flags and hold takes articulation priority,
    but the co-set flag is still composer-typed content).
  - `pulse_env` / `filter_env`: per-instrument pulse-width / filter-cutoff
    sweep envelopes (DMC V5) — the parameterized form that dissolves the
    engine's shared, fused sweep tables (the editor's packer overlaps
    programs to save bytes; that fusion is mechanism, not content).
    `pulse_env: start=$0514 [repeat=N] seg (rate, frames) [seg (...)]*`.
    `start` is the initial 16-bit value; each `seg (rate, frames)` adds
    the signed `rate` to it every frame for `frames` frames before
    advancing; `repeat=N` loops from phase index N (omitted = the last
    phase holds). The reachable phases are captured per instrument
    (bleeding deconstructed away); `from_usf` synthesises a de-fused
    table the engine walks. Same musical family as Hubbard / DMC-V4 PWM
    (init + ramp). An instrument WITHOUT `pulse_env` keeps the running PW
    oscillator going across the note (`pwm: ... keep_running=true`).
  - `wave_freq`: `[...]` — parallel per-step pitch values for `waveform`
    (signed semitone offsets added to the note, or absolute freq-hi bytes
    for drum steps). Same length as `waveform`; `loop` applies to both.
  - `offtable_freq`: `at(offset, note, freq_lo, freq_hi) ...` (DMC V5). When a
    freq lookup index `(offset + note) & $FF` runs past the 96-entry freq table
    into per-voice engine state, the original engine plays that state byte as a
    frequency. This captures the EXPLICIT 16-bit frequency the read produces,
    keyed by `(offset, effective note)` — a musical pitch attributed to the
    instrument's arpeggio, NOT a raw memory window. `offset` is a wave-program
    step's semitone offset, or `0` for the base read (vib_setup's
    `base-note freq << width`, the note's own freq, glide arrival). Note-keyed
    because the produced freq depends on the played note. The composer builds
    its freq lookup in-bounds from these (`idx = offset + note`) and emits the
    value directly (no out-of-bounds read). This is the off-table-read
    representation (it superseded the removed `freq_overrun` verbatim
    post-table byte window); the model sees frequencies, never
    bytes-at-an-offset.
    An entry may instead be `live(offset, note, freq_lo, freq_hi)`: `live`
    marks a read that sonifies a live-VARYING engine value (a duration counter,
    freq accumulator, sector/wave position, speed/master-vol) which the composer
    reproduces from its own equivalent state rather than the captured
    `(freq_lo, freq_hi)`. `at(...)` = the read sonifies a fixed byte. This
    per-read behavioral flag replaced the DMC-v4 `offtable_redirect` /
    `sectpos_shadow` params, which serialized HVSC memory geometry (Core Tenet
    corollary: config never describes HVSC layout). Only DMC v4 emits `live`;
    all other engines emit `at(...)` only.
  - `wave_table_pos`: `N` — the instrument's position in the editor's SHARED
    wave table (DMC: a number the composer typed into instrument byte 9 —
    arrangement, like transpose-command placement). Audible only when an
    off-table freq read sonifies a voice's LIVE wave position, so it is
    emitted only for members where that happens (then EVERY instrument
    carries it). The composer packs its wave pool at these positions so its
    wave-position state equals the value the original sonifies, and serves
    the read live.

Field set is engine-determined. Fields not relevant to an engine
omit cleanly.

## `subtune N kind { ... }`

`kind` is `music`, `digi`, or `sfx`. The parser knows what shape to
expect downstream.

### `subtune N music`

```
subtune 0 music {
  tempo: 4

  voice 1 { ... }
  voice 2 { ... }
  voice 3 { ... }
}
```

- `tempo` is the frames-per-tick value.
- Three voices per chip. An ordinary tune has exactly `voice 1..3`; a
  2SID tune `voice 1..6`; a 3SID tune `voice 1..9` (any other count is
  a parse error).

### Multi-SID (2SID / 3SID)

The chip dimension is fully **elidable**: a single-chip USF never
mentions chips at all, and every chip-1 form is the bare form. A
multi-SID tune extends the same shapes:

- **Voices number through the chips**: voices 4-6 play on chip 2,
  7-9 on chip 3 (`chip = (voice-1)//3 + 1`). No `chip:` keyword
  exists anywhere.
- **`tempo N: T`** (N = 2/3), directly after `tempo:` — that chip's
  tempo when it differs from chip 1's; omitted = same.
- **`global N { ... }`** — chip N's master-volume/filter automation
  track (each chip has its own `$D415-$D418`); bare `global` = chip 1.
- **`init { sid N { ... } }`** — chip N's SID priming; bare `sid` =
  chip 1.
- **`psid.sid2` / `psid.sid3`** — the extra chips' SID models, only
  when explicitly flagged in the original header.

Verification is chip-tagged: the write-log encodes each write's chip
as `reg = chip*$20 + reg`, so single-chip streams are unchanged and
the flat `(reg, val)` comparators key multi-chip streams correctly
regardless of the original's chip addresses.

### Voice block

```
voice 1 {
  orderlist: 0 1 0*3+7 2 loop@2

  pattern 0 length=32 { ... }
  pattern 1 length=16 { ... }
}
```

- `orderlist`: a sequence of pattern ids. A `loop@N` token gives the
  position to jump to after the orderlist ends (0-indexed). A trailing
  `stop` (no `loop@`) indicates an end-of-song with no loop.
  `loop@N+T` — the loop **picks up** transpose `T`: the engine's
  transpose state carries over the wrap, so the head entries play
  passes 2+ under `T` (an audible pass-1-vs-2+ difference — standard
  FC tunes whose loop head has no explicit transpose). Plain `loop@N`
  means the head re-establishes its stated transpose on every pass.
  `loop@N len=L` — the loop **picks up** note length `L` (ticks): the
  engine's length state likewise carries over the wrap; the head
  pattern's first note states no length, so it plays pass 1 at the
  row's written duration (the start-of-song state) and passes 2+ at
  `L`. May combine with the transpose pickup: `loop@N+T len=L`.
- Per-entry modifiers. An entry has the form `a[*b][+c][^d]` — the
  pattern id (operand) first, then a homogeneous list of
  `<operator><parameter>` modifiers:
  - `a` — the pattern id (required, the operand).
  - `*b` — **repeats**: play the pattern `b` times (e.g. `0*3` plays
    pattern 0 three times). Omitted means once. A lossless run-length
    form of an expanded orderlist (`0 0 0` == `0*3`).
  - `+c` — **transpose**: a semitone / freq-table-index offset added to
    the entry's notes (FC's `SeqTranspose`; non-negative). Omitted = 0.
  - `^d` — **voiceinc** ("sound transpose"): an offset added to the
    entry's wave/instrument-program index (FC's `SeqVoiceinc`).
    Omitted = 0; rare.

  These are sequence-level modifiers: the pattern body stores the pure
  untransposed motif and the orderlist shifts/repeats it, so one pattern
  is reused at several pitches/timbres. Each modifier is omitted at its
  identity value, so most engines (no transpose/voiceinc/repeat) emit
  plain pattern ids.
- `pattern N length=L`: pattern id `N`, total tick length `L`. The
  parser validates that the contained notes' durations sum to L.

### Pattern body — note rows

Each non-blank line inside a pattern body is a note row:

```
pattern 0 length=32 {
  C-5  4  i:lead
  D-5  2  i:lead  tie
  E-5  8  i:lead  fx:drum
  ---  18
}
```

Columns (whitespace-separated):

1. **Pitch**: a note name `C-5`, `D#5`, `F-3`, etc. Sharps use `#`.
   Octaves are 0-9 (engines may use off-table arpeggio extensions
   that index past the 96-entry musical freq table; those land in
   octave 8+). Rest is `---`.
2. **Duration**: positive integer (ticks).
3. **Instrument ref**: `iN` (numeric) or `i:name` (named). Optional —
   absent on rest rows.
4. **Effect flags** (zero or more): `tie`, `fx:drum`, `fx:arp`,
   `fx:vibrato`, `fx:pwm`, `fx:incby2`, etc. Engine-bit names. The
   parser interns them as string flags; the codegen translates to
   engine bits.

   Portamento family (one parameter space, two point shapes):
   `glide=N` — slide-to-target with an N-frame delay (Tel FC).
   `glide_up=$RRRR` / `glide_down=$RRRR` + `glide_onset=N` — a
   directional constant-rate portamento: 16-bit rate added/subtracted
   to the note freq each frame, starting after N elapsed ticks of the
   note (standard FC $Ex).

   Positioned sticky-state markers (DMC V5 sectors): `set_dur=$NN`
   (duration reload, $FD) and `set_instr=N` (instrument-select, $FC)
   are ORDERED prefix flags on the note/gate row that follows them in
   the event stream. They stay positioned rows rather than per-note
   tags because the engine's gate-off lookahead reads the raw next byte,
   so a command's stream position is itself write-stream-significant. A
   `tie` row (rest pitch + `tie`) is a hold/sustain of the current note
   ($FE) for one more duration with no retrigger.

   Stated-command placement (DMC V4 sectors): `dcmd` / `icmd` / `vcmd`
   mark that this editor row physically carries a duration ($80-$BF) /
   instrument ($60-$7B) / volume ($Fx) command, and `softcmd=N` that it
   carries N soft-start toggles ($7C) — including re-statements whose
   value did not change (a value-change derivation cannot see those).
   This is the composer's command PLACEMENT (arrangement, same §8 class
   as the redundant orderlist transpose commands), not byte offsets.
   Emitted only for members whose off-table freq reads sonify the
   engine's per-voice sector-position counter (DMC $1729-$172B): the
   composer derives each row's byte width (base bytes of the row kind +
   stated commands) to keep a live `sectpos` shadow that those reads
   are redirected to.

A line with no pitch (`---`) and no instrument is a rest of the given
duration.

### Global automation track (`global { ... }`)

```
subtune 0 music {
  tempo: 1
  voice 1 { ... }
  voice 2 { ... }
  voice 3 { ... }

  global {
    at 0   dyn=$0F res=$0F mode=$07 route=$04
    at 1   cutoff=$58
    at 32  mode=$06 route=$03
  }
}
```

Optional, at most one per music subtune; omitted when empty. The global
track carries **chip-global** musical automation — state that belongs to
the whole subtune, not to any one voice, so it cannot ride a voice's
`NoteRow`. On the SID the only such controls are the master-volume and
filter registers (`$D415`-`$D418`), so the track decomposes them into
**named musical fields** rather than raw register bytes:

- `dyn` — master volume / dynamics (`$D418` low nibble, 0-15).
- `mode` — filter mode bits (`$D418` high nibble: LP/BP/HP/voice-3-off).
- `res` — filter resonance (`$D417` high nibble).
- `route` — filter routing, which voices pass through the filter
  (`$D417` low nibble).
- `cutoff` — filter cutoff, high 8 bits (`$D416`).

Each `at N` event names the step index `N` (same step axis as the voice
patterns) and lists only the fields that **change** at that step; a field
holds its last value until the next event that names it (running state).
The composer re-packs the named fields into the exact `$D415`-`$D418`
register writes; the per-tune write template fixes their ORDER relative to
the voice writes, so the global track says *what* the global state is at
each step, never *when within the frame* it is written.

This is a single shared track (not separate volume / filter streams): the
SID's global controls are few and the engine writes them interleaved in
one fixed order, so splitting them would lose nothing and gain nothing. A
`GlobalEvent` is structurally just like a `NoteRow` — several named fields
on one row — which is what keeps it principled; the forbidden shape is an
opaque register dump or a library index, not multiple-named-fields-per-row.

### `subtune N digi`

```
subtune 2 digi {
  sample: Chimera.sample2.flac
}
```

The sample reference is a relative filename. The parser checks the
file exists in the same directory and that its Vorbis-comment engine
field matches the parent USF's `engine:`.

### `subtune N sfx`

(Reserved for Commando-style 16-byte SFX records — covered in a
follow-up spec when SFX is migrated to USF. For now, an `sfx`
subtune block contains engine-specific fields TBD.)

## Validation layers

Layer 1 — parse: grammar check, produces a typed AST or precise
syntax error (line, column, expected vs got).

Layer 2 — references: every `iN` / `i:name` in a pattern resolves to
a defined `instrument`. Every orderlist entry resolves to a defined
`pattern` in the same voice. Every `sample:` resolves to an
existing FLAC sidecar.

Layer 3 — lengths: per-pattern, durations sum to declared `length=`.

Layer 4 — sidecar fingerprint: each `.flac`'s Vorbis comments are
internally consistent (native_bits, method, engine all populated)
and `engine` matches the USF's `engine:`.

Layer 5 (`usf lint`) — soft warnings: instrument defined but never
used; orderlist position 0 referenced only once (might be a typo);
durations way out of distribution; etc. Opt-in.

Layers 1-4 must pass before codegen runs. Layer 5 is informational.

## Round-trip invariant

For any well-formed `Chimera.usf`, `write(parse(text)) == text` as
bytes. The writer:

- Emits fields in a fixed order within each block.
- Uses a canonical layout (one space after `:`, aligned columns in
  pattern bodies where feasible).
- Always emits `length=` on every pattern.
- Always emits `loop@N` even when N == 0.
- Never invents fields the parser would not produce.

## Things the format deliberately does NOT have

- Count fields. The parser derives `n_voices`, `n_patterns`,
  `n_subtunes`, `n_instruments` from the data.
- Implicit defaults that mask typos. Unknown tokens are errors.
- A `kind:` field on instruments. Instrument behavior is fully
  parametric.
- `0x` hex (only `$`), `0` octal, scientific notation.
- Per-tick `@offset` markers (creates redundancy footgun).
- A cross-voice alignment check (free by default; lockstep would
  reject most polyrhythmic SID music).
- Comment preservation across round-trips.
