# SID `init` — what it is and what USF should capture

A research report for the USF design discussion.

Companion reading: [`docs/sid_init_research.md`](sid_init_research.md)
is the long-form research artifact — full PSID/RSID spec quotes, the
verbatim libsidplayfp `psiddrv.a65` stub, and source-by-source
analysis. This file is the shorter synthesis for the design call.

---

## TL;DR

1. **Init is not specified.** The PSID/RSID file format only constrains
   the address ranges of init/play and the parameter convention (A =
   subtune number, 0-indexed internally). It says nothing about what
   init must do. Every claim about "init does X" found in tutorials is
   composer convention, not protocol.

2. **Init writes that `play` never overwrites are part of the audio.**
   From the SID chip's view, a $D418 write at init time and a $D418
   write inside play are indistinguishable — both are bytes the
   hardware receives. The "purpose" distinction is composer-side
   ergonomics, not anything the chip or the spec cares about.

3. **Each engine family has a characteristic init signature.** Empirical
   sampling across the **top 100 HVSC engine families (89% of the
   catalogue, 53,905 SIDs covered)** plus a deep dive on the top 5
   plus Hülsbeck's Shades shows init write counts from 0 to 259 and
   qualitatively different patterns. **Init is not inferable from
   the music — it's a per-engine setup contract.** Six classification
   buckets (§2b) emerge, all of which fit the trichotomy.

4. **Init's apparently engine-specific bytes split into three
   universal categories** (§6 — the load-bearing finding of this
   report):

   - **Reset writes** — erase prior chip state. Universal
     infrastructure (silence-clear, baseline $D418, test-bit
     oscillator-phase clear). The composer always emits these,
     identical for every tune. **Invisible to USF.**

   - **Priming writes** — set specific SID state the play loop will
     rely on. Per-tune musical decisions. **Captured in USF as named
     typed parameters** (master_vol, filter, voice envelope_prime,
     pulse-width init). Default = absent.

   - **Environment** — CIA timer programming, IRQ install, playback
     rate. **Top-level USF parameter** (`playback_rate_hz`),
     orthogonal to init.

   Engine-internal RAM bookkeeping (Shades's `$033C=1` deferred-init
   flag, etc.) belongs to none of the above and doesn't go in USF.

5. **The composer's init becomes universal** — one routine,
   parameterised only by the USF priming fields. The original
   engine's specific init bytes are irrelevant; the composer uses
   ITS OWN play loop paired with ITS OWN reset infrastructure, and
   the priming fields are the only per-tune input.

6. **Verification shifts** — since the rebuild's init writes are
   structurally different from the original's (universal reset vs.
   the original's engine-specific style), byte-comparing init is
   no longer meaningful. The verification verdict becomes
   **"play-stream from first play() onward matches" + "SID state
   at end of init is musically equivalent."** See §6.4.

---

## 1. What the spec actually says

The HVSC `SID_file_format.txt` (Schwendt/White/Lem/Bos — the
authoritative spec) defines init only by its address and parameter
convention:

> `initAddress` — when the player wants to initialize a tune, the
> CPU registers are setup as follows: ... `A` accumulator = song
> number to be played. 0 means tune 1, 1 means tune 2, etc.

That's it. The spec lists what the host-side environment provides
(default IRQ vector, banking, CIA timer state) but does **not**
prescribe what init must accomplish.

For RSID (the "real" subset), init **must not** reprogram the CIA
timer, install IRQs, or rely on the KERNAL — it can only set up
data structures and let `play` handle the rest. For PSID, init is
free to do anything: install IRQs, clear the SID, pre-decode the
first note row, write filter state, etc.

**Crucial fact found in the reference player code (not in the prose
spec):** `libsidplayfp`'s PSID driver stub (`psiddrv.a65`) writes
`$D418 = $0F` *before* calling init. Nothing else is set on the
SID — voice registers are at whatever the emulator's reset produced
(zero on a clean reset). Hosts other than libsidplayfp may or may
not match this; in practice libsidplayfp is what everyone uses, so
its conventions are de facto standard.

**The gap between `init` returning and the first `play` call is a
host-defined wait loop** (libsidplayfp does `jmp idle`). The SID is
not actively driven during the gap. Whatever init wrote is the
chip's audible state until play starts overwriting.

See `sid_init_research.md §1–4` for the full quoted passages.

---

## 2. What init actually does in the wild

I ran `writelog_capture(duration=1.0)` on three representative SIDs
from each of HVSC's top 5 engine families (chosen by volume —
together they account for ~31,000 SIDs, ~52% of the catalogue).
Frame 0 is the init invocation; here is what each family does:

### DMC (10,660 SIDs) — "thorough setup"

```
frame0 writes:    28–39
registers touched: every SID register ($00–$18)
final $D418:      $0F (master vol max, no filter routing)
final V*.ctrl:    $08 / $08 / $00..$40  (test bit set on V1+V2)
filter:           cutoff cleared, resonance per-tune
```

DMC writes essentially **every** SID register during init. Sets the
test bit (`$08`) on V1 and V2 — this resets the oscillator phase
counter, eliminating click artifacts on the first note. Per-tune
filter resonance/routing.

### GoatTracker V2.x (7,311 SIDs) — "minimal touch"

```
frame0 writes:    5 (typical) — 26 (occasional)
registers touched: usually just $D404 / $D40B / $D412 / $D415 / $D418
                  (voice ctrls, filter cutoff lo, master vol)
final $D418:      $0F (mostly) or $00
final V*.ctrl:    $00 / $00 / $00
```

Most GoatTracker tunes write 5 bytes during init: three voice
ctrls = $00 (envelope-released state), filter cutoff lo = $00,
$D418 = $0F. Some tunes (probably with a specific config setting)
do a full register clear instead.

### Music_Assembler (6,351 SIDs) — "barely anything"

```
frame0 writes:    3 (uniformly)
registers touched: $D417, $D418  — that's it
final $D418:      $1F (filter mode bit set — highpass/notch routing
                  on top of $0F volume)
final $D417:      $F0 (filter routing: voices unfiltered,
                  external in unfiltered)
```

Music_Assembler is striking — its init writes literally 3 bytes.
**Music_Assembler relies on the previous tune's state for everything
else.** A tune player switching from one Music_Assembler SID to
another inherits voice ctrl state, freq, pulse width, etc. from the
prior session.

### MoN/FutureComposer (4,024 SIDs) — "noise reset"

```
frame0 writes:    47 (uniformly)
registers touched: every SID register
final V*.ctrl:    $41 / $41 / $00..$41
final $D418:      $1F
```

FutureComposer writes V*.ctrl = `$41` = noise waveform + gate-on.
That's a deliberate "noise sweep" at init — the engine briefly
sounds noise on each voice to clear the SID's analog state, then
overwrites with the first note. Different philosophy from DMC's
test-bit approach.

### Soundmonitor (3,625 SIDs) — "clean clear + filter"

```
frame0 writes:    31–46
registers touched: every SID register
final $D418:      $0F
final V*.ctrl:    $00 / $00 / $00
filter cutoff:    cut_lo=$08 cut_hi=$10 (consistent across tunes)
```

Soundmonitor zeros everything cleanly then sets a tune-independent
filter cutoff. Master vol = $0F.

### Chris Hülsbeck (Shades, 1986) — "no-op on the SID"

```
frame0 SID writes: 0  (the single $D418=$0F is from the host stub,
                       not the engine's init routine)
init code:         SEI; NOP×10; LDA #$01; STA $033C; CLI; RTS
```

The init routine sets a single RAM flag at `$033C` and returns —
zero SID writes. The actual song-start setup is deferred to the
first play() call: play() reads `$033C`, finds it non-zero, jumps
to a setup routine at `$77B1` that loads pattern pointers and
clears the flag, then continues to normal play. Subsequent play()
calls find `$033C=0` and skip the bootstrap.

So Shades's init is a **"haven't bootstrapped yet" marker**, not a
SID setup at all. Adds a sixth pattern — "deferred init" — to the
five chip-touching styles above.

### What this tells us

- **Init write count varies from 0 to 47.** Hülsbeck's Shades does
  zero SID writes during init; FutureComposer writes 47.
- **The set of registers touched varies dramatically.** Music
  Assembler touches 2; FutureComposer touches all 25.
- **Four different "first-note prep" strategies** exist:
  - Test-bit reset (DMC)
  - Noise-sweep clear (FutureComposer)
  - Clean zero (Soundmonitor, GoatTracker partial)
  - Defer everything to first play() (Hülsbeck)
- **None of these are inferable from "the music."** They are
  engine-author choices that produce the same musical notes via
  different SID register histories.

---

## 2b. Survey: top 100 HVSC engines (89% catalogue coverage)

The top-5 sample above was extended to the top 100 engines (covering
53,905 / 60,572 = **89.0% of HVSC**). Methodology: per engine, two
random SIDs with `songlength_s > 30`, frame-0 writelog captured at
`duration=1.0`. Six classification buckets emerge:

| Bucket | Count | Examples | Notes |
|---|---:|---|---|
| **Noise-burst / test-bit / multi-pass reset** | **44** | DMC, FutureComposer, JCH_NewPlayer, HardTrack, AMP, SoedeSoft | Transient writes (regs written 2-8× during init). Either test-bit phase clear, brief noise burst, or paranoid multi-pass silence-clear. Subdivides further (below). |
| **Clean reset (silence-clear + $D418)** | 19 | Soundmonitor, X-Ample, SidTracker64, TFX, PASS | 24-30 writes, every register touched once, single-pass. |
| **Partial setup (4-23 writes)** | 11 | GoatTracker V2, GoatTracker V1, Master_Composer, Rob_Hubbard, Vibrants/JO | Touches a subset of registers — voice ctrls only, or voices + filter. |
| **Deferred (no SID writes)** | 11 | Hülsbeck, Basic_Program, SidFactory_II, Laxity_NewPlayer, MusicShop, DefleMask_v2, GKGM | Pure RAM init; first play() does the SID setup. |
| **Thorough setup (>30 writes, single-pass)** | 7 | Hermit/SidWizard, Electrosound, David_Whittaker, Matt_Gray, Asterion, Adam_Gilmore | Lots of priming on top of reset. |
| **Minimal touch (≤3 writes)** | 4 | Music_Assembler, CheeseCutter_2.x, Ubik's_Musik, Arne/AFL | Relies on host-reset state. |

### The noise-burst bucket dissected

44 engines is a lot — and looking inside, this bucket actually
contains three different sub-patterns:

**(a) Test-bit oscillator-phase clear.** Voice ctrls written `$00 →
$08 → $00` (or similar transient). DMC, Soundmonitor (3 transients on
voice ctrls), Geir_Tjelta/SIDDuzz'It. ~10 engines.

**(b) Noise-burst sweep (audible tick).** Voice ctrls written `$00 →
$41 → $00` (noise + gate, then silence). FutureComposer, JCH_NewPlayer.
~5 engines.

**(c) Multi-pass silence-clear (paranoid).** Every register written
3-8 times with all values zero, then a final priming value at the end.
Griff (V1.freq_lo: `$00 $00 $00 $00 $00 $4B`), System6581 (writes 121
bytes during init), SkyLine_Editor (259 writes), Glover, Groovy_Bits.
~10 engines write 100+ bytes this way.

The remaining ~19 engines in the bucket are mixes of the above.

**Implication:** "transient writes during init" is *not* a unified
phenomenon — it's three different techniques (defensive phase clear,
intentional noise signature, redundant silence-clear). All three
arrive at the same final register state. Per Check A (strict, §5),
only the final state matters for verification, so all three collapse
to "what's the state at end of init."

### Master vol distribution (priming evidence)

`$D418` final values across the top 100 engines, ranked by frequency:

| Final $D418 | Engines | Reading |
|---|---:|---|
| **$0F** | 30 | Default — voices on, no filter mode bit |
| **$1F** | 27 | Filter mode bit (3-OFF) + voice volume 15 |
| (untouched by engine, host wrote $0F) | 22 | Music_Assembler-style: relies on host pre-init write |
| $00 | 5 | Fade-in or silent intro (DefleMask_v12, SkyLine_Editor, Power_Music, Adam_Gilmore, Griff) |
| $4F, $47, $7F, $2F, $39, $4F, $3F | various | High-bit / filter-mode combinations per-engine |
| Other ($01, $06, $10, $1C) | various | Tune-specific |

**This proves master_vol cannot be assumed $0F.** ~25% of engines
explicitly use $1F (filter mode bit set); 5% use $00 (fade-in intent);
plus a long tail of other values. A USF `init.sid.master_vol` field
is **necessary**, not nice-to-have.

### Filter init prevalence (priming evidence)

**37 / 100 engines set the filter at init** (either `$D416` cutoff_hi
or `$D417` res_routing non-zero). Values are diverse — `cut_hi`
ranges from $0A to $FF; `res_routing` from $00 to $F7.

**This proves filter is a real priming category.** Roughly 1 in 3
HVSC engines uses filter from frame zero. A USF
`init.sid.filter { cutoff_lo, cutoff_hi, res_routing }` block is
**necessary**.

### Trichotomy verdict at the 100-engine scale

**The trichotomy holds.** Every one of the 100 engines' inits
decomposes cleanly into:
- Reset (universal, varies in technique but converges to "clean
  chip state going into priming")
- Priming (master_vol, filter, occasional envelope priming — all
  captured as named USF params)
- Environment (CIA timer / play rate — covered by `playback_rate_hz`)
- Bookkeeping (RAM-only writes, out of USF)

No engine surfaces a category the trichotomy can't handle.

**What this changes in the design call:**

- **Master_vol priming is mandatory** in the USF schema (already
  there as `master_vol.init_value`, just needs the broader value
  range support).
- **Filter priming is mandatory** in the USF schema (new fields).
- **Test-bit phase clear in the universal reset is well-supported** —
  ~10 engines do this defensively; including it makes our rebuild
  more reliable on first-note attacks across the catalogue.
- **Noise-burst transient signatures (FutureComposer family) are
  fidelity-loss the project accepts** — only ~5 engines exhibit
  this signature, and the cost of capturing it (a new
  `init.sid.startup_signature` field with multiple variants) outweighs
  the benefit.

### Sample data: `tools/init_survey.py`

The script that produced these numbers. Re-runnable; samples randomly,
so re-running may give slightly different intra-family-variance
findings. The bucket counts and key prevalence numbers are stable
across re-runs.

---

## 3. What USF currently captures vs misses

Current USF `init {}` block (per `docs/usf_format.md`):

```
init {
  voice 1 {
    ctrl:       $41    ; SID V1 ctrl byte at engine init
    dur_field:  $00    ; vibrato carry path initial duration
    pwm_period: $80    ; PWM accumulator
    pwm_dir:    up     ; PWM direction
    instr:      i1     ; instrument id voice starts with
    slide_v:    $00    ; cached freq-hi for skydive effect
  }
  voice 2 { ... }
  voice 3 { ... }
}
```

This is **Hubbard '85-shaped**. Five of those six fields
(`dur_field`, `pwm_period`, `pwm_dir`, `instr`, `slide_v`) only
have meaning for the Hubbard '85 family. They describe the
per-voice runtime state the Hubbard engine reads from the
freq-table overlap region.

**What USF init does NOT capture:**

| Category | Example engines | Why USF misses it |
|---|---|---|
| **Master vol init value** | FutureComposer ($1F), Music_Assembler ($1F), most others ($0F) | Only `$0F` is implied (today's master_vol.init_value field) |
| **Filter cutoff** | Soundmonitor (cut_lo=$08 hi=$10), many DMC | Not in USF |
| **Filter routing/resonance** | DMC (res_filt=$02/$04), Music_Assembler (res_filt=$F0) | Not in USF |
| **Test-bit oscillator reset** | DMC (V1.ctrl=$08, V2.ctrl=$08 at init, then $00 on first note) | Today's `init.voice.ctrl` is the *final* ctrl, can't express "set $08 then clear" |
| **Envelope priming** | Bowden ($D405=$09 etc.) | Not in USF — this is what the Melonmania investigation hit |
| **Noise-clear sweep** | FutureComposer (V*.ctrl=$41 briefly) | Not in USF |
| **CIA timer programming** | Any multispeed RSID, some PSIDs | Not in USF |

### The Melonmania-sub-1 lesson

The Bowden engine's hardcoded init writes (`$D405=$09, $D406=$00,
$D40C=$09, $D40D=$00`) couldn't be expressed in USF. I attempted
shape-detection ("if the carry-leak quirk is present, emit Bowden's
primes") — that's engine-name dispatch with extra steps. The user
correctly rejected it. **The right answer is to let USF carry
these init writes directly.**

---

## 4. The init trichotomy — reset / priming / environment

Every byte an engine's init routine writes (to SID, to RAM, to CIA,
anywhere) falls into one of four categories. The first three are
universal across engines; the fourth is engine-specific and stays
out of USF entirely.

### 4.1 Reset writes — erase the past

**What they are:** writes that ensure prior chip state (from a prior
tune, a prior emulator session, host residual) doesn't leak into the
current tune.

**Examples:**
- Silence-clear `$D400-$D417` to zero.
- Set `$D418` to a baseline ($0F is the universal default).
- Optional: test-bit oscillator-phase clear on all three voices.
  Briefly set `V*.ctrl = $08` then back to $00 — resets the
  oscillator's phase accumulator so first-note attacks are
  click-free and phase-aligned.

**Who emits them:** the **composer**, always, for every tune,
identical bytes. The original engine may or may not do them
(Music_Assembler doesn't; DMC and Soundmonitor do, in different
flavours). It doesn't matter — our composer's universal init does
them regardless.

**USF representation:** **none**. Reset is universal infrastructure
invisible to USF. The composer emits the same reset bytes for every
tune.

### 4.2 Priming writes — shape the future

**What they are:** writes that set specific SID state the play loop
will rely on but doesn't itself emit.

**Examples:**
- Master vol non-default (Music_Assembler uses `$D418=$1F` with the
  filter-mode bit; default would be `$0F`).
- Filter cutoff/resonance/routing (Soundmonitor sets a tune-wide
  filter; DMC tunes set per-tune resonance).
- Per-voice envelope priming (Bowden writes `$D405=$09, $D406=$00,
  $D40C=$09, $D40D=$00` so silent voices have consistent envelope
  state).
- Per-voice initial pulse-width.

**Who emits them:** the composer, parameterised by USF.

**USF representation:** typed musical-parameter fields. Default
value = "don't prime" = composer emits nothing for that slot.

```
init {
  sid {                            ; SID-chip priming
    master_vol: $0F                ; default $0F
    filter {
      cutoff_lo: $00
      cutoff_hi: $00
      res_routing: $00             ; Music_Assembler: $F0
    }
    voice 1 {
      envelope_prime: ($00, $00)   ; (ad, sr). Bowden: ($09, $00)
      pw_init: $0000               ; default zero
    }
    voice 2 { ... }
    voice 3 { ... }
  }
}
```

Most tunes will have all defaults and the `sid {}` block is
trivially empty (or omitted entirely). Bowden tunes set V1+V2's
`envelope_prime`. Music_Assembler tunes set master vol $1F + filter
res_routing. DMC tunes set filter resonance.

### 4.3 Environment — the per-tune playback rate

**What it is:** how the host invokes play(). CIA timer period sets
the play() rate (50Hz VBI, 100Hz CIA, custom multispeed). For
Hülsbeck's Shades, CIA programming determines that play() runs at
the rate the tune was authored for.

**Who handles it:** the composer's host-side setup, parameterised
by USF.

**USF representation:** a single top-level field, orthogonal to the
init block:

```
playback_rate_hz: 50              ; default VBI
;; OR
cia1_period: $4CC8                ; if exactness needed
```

Environment is neither reset nor priming — it's *temporal*, not
SID-state. Keeping it separate avoids conflating "what the chip
looks like" with "how often play() runs."

### 4.4 Engine bookkeeping — out of USF entirely

**What it is:** RAM writes the original engine made for its own
internal state machinery — flags, scratch pointers, deferred-init
markers, ordbits-and-bobs of any specific engine implementation.

**Examples:**
- Shades's `$033C=1` "haven't bootstrapped" flag.
- Hubbard's per-voice runtime state in the freq-table overlap.
  (Actually a borderline case — see §4.5.)
- DMC's pattern pointer table zeroing.
- Any engine's internal counter / position pointer initialization.

**Who handles it:** the composer's rebuild engine, however *it*
needs to. The composer's play loop is structurally different from
the original; its bookkeeping needs are its own.

**USF representation:** **none**. Engine bookkeeping is
implementation, not music.

### 4.5 The borderline — per-voice runtime state

The current USF v3 `init {}` block carries six Hubbard-shaped
per-voice fields (`ctrl/dur_field/pwm_period/pwm_dir/instr/slide_v`).
These aren't SID-chip state — they're **per-voice runtime state the
play loop reads on tick 1**. They tell the play loop "voice 1 starts
with instrument 4, pulse-width accumulator at $80 going up, no slide."

This is musical: it's saying "voice 1's first note plays through
instrument 4 with a fresh PWM ramp." Different per-voice starting
state means a different opening sound, even with the same first
note.

So this belongs in USF as **engine-state priming** — distinct from
**SID-state priming** (§4.2):

```
init {
  sid {            ; the §4.2 stuff — SID chip state
    master_vol: $0F
    filter { ... }
    voice 1 { envelope_prime: ($09, $00) ... }
    ...
  }
  voice_state {    ; per-voice runtime state for the play loop
    voice 1 { ctrl: $41, dur_field: $00, pwm_period: $80,
              pwm_dir: up, instr: i1, slide_v: $00 }
    voice 2 { ... }
    voice 3 { ... }
  }
}
```

Today's `init { voice N { ... } }` block is `voice_state` in the
new framing. Adding `init.sid { ... }` for SID-chip priming is the
schema growth this report recommends.

### Why this trichotomy matters

Three direct consequences:

1. **The composer's init becomes universal.** One routine,
   parameterised only by the §4.2 and §4.5 USF fields. The original
   engine's specific init bytes are no longer the composer's
   reference point. The composer pairs *its own play loop* with
   *its own reset infrastructure* and reads priming from USF.

2. **Migration becomes much simpler.** A new engine's init handling
   reduces to "what's the priming?" — extract reads the original's
   init writes, classifies as reset (drop) or priming (record to
   USF). No engine-specific init code in the composer ever.

3. **The "carry engine bytes" forbidden shape is impossible.**
   Every USF init field is a typed musical parameter with a clear
   meaning. The ML model sees structured state, not opaque bytes.

---

## 5. Verification under the new model

The user raised this consequence: **if the composer's init is
structurally different from the original's, we can no longer
byte-compare init writes.** The verification verdict has to shift.

### 5.1 What verification currently does

`tools/regression.py` calls `compare_instruction_stream(a, b)` which
flattens both write streams (orig + rebuild) and compares them
position-by-position. Today it reports `match_all` (with init) and
`match_post_init` (drops frame 0); `is_full` accepts either being
a perfect match.

For Music_Assembler today, `match_all=full` works only because our
rebuild happens to emit the same init bytes (we don't — we emit
the full Hubbard-style silence-clear, but Music_Assembler is on the
companion path which silences differently).

Under the new model, **all rebuilds emit the composer's universal
reset**, which structurally differs from every original engine's
init choices. `match_all` will be 0-or-tiny for every tune.

### 5.2 The new verdict — play stream + SID-state checkpoint

Two checks together replace the old "byte-exact stream comparison":

**Check A: SID state at end of init matches — strict, all 25
registers.** After init returns in both original and rebuild, the
SID's register state must be identical across all of $D400-$D418.
Compare register-by-register the LAST write of each register
during frame 0 (default 0 if unwritten):

```
For each register R in $D400..$D418:
  orig_state[R] = last value written to R during frame 0 (or 0 if unwritten)
  reb_state[R]  = last value written to R during frame 0 (or 0 if unwritten)
  assert orig_state[R] == reb_state[R]
```

**Why strict.** A lenient version would compare only registers
"play() won't immediately overwrite," but that requires inspecting
the rebuild's first play() output to know which slots are
exam-relevant — circular. The strict version is simpler and
guarantees identical chip state going into play(), which in turn
guarantees byte-identical play output from frame 1 onward. Any
false-positive (states differ but the difference is masked by
play()'s first writes) is something we'd want to see and decide
about explicitly, not silently accept.

This catches "we primed differently" without caring about HOW we
got there (reset+priming sequence vs. minimal-touch).

**Check B: play stream from frame 1 onward matches.** Concatenate
all writes from frame 1 onward in cycle order. Position-by-position
match. Equivalent to today's `match_post_init`.

If both checks pass, the audible output is identical from the first
play() onward. That's the verdict.

### 5.3 Edge cases

**Init writes that the original DID make but our universal reset
doesn't reproduce in the same order.** If both end up at the same
register state, fine — Check A passes. The stream during init
differs but the final state matches.

**Original engine relies on host-residual state** (Music_Assembler
in a chained-tune scenario). Our rebuild's universal reset
overrides this — actually MORE robust than the original. Check A
passes because libsidplayfp's host stub starts from a clean reset.

**Test-bit clear / noise-clear sequences.** These leave the same
register state as never touching them, but produce DIFFERENT
register *traces* during init (transient writes). Under the new
verdict, the trace difference is irrelevant — Check A only sees
final state. The audible effect on first-note attack is a separate
fidelity question (see §6 on test-bit defensive insertion).

**CIA-driven multispeed (e.g., Shades at speed=$1).** The play()
rate is different from VBI. siddump's writelog buckets by VBI
regardless. Check B still works — same play() output, same VBI
bucketing — as long as the composer's environment setup
(`playback_rate_hz`) matches.

### 5.4 Implementation impact

The `compare_instruction_stream` function gets a new mode:

```python
compare_instruction_stream(a, b, mode='play_plus_state')
```

Returns:
- `play_match`: longest matching prefix of frame-1-onward stream
- `play_len_a`, `play_len_b`: stream lengths
- `state_match`: True iff end-of-frame-0 register state matches
- `is_full`: play_match == play_len_a == play_len_b AND state_match

The old `match_all` / `match_post_init` fields stay for backward
compatibility but are no longer the verdict.

`tools/regression.py` switches to `is_full` under the new mode.

The Fairlight false-negative case (where init writes spilled into
frame 0 asymmetrically) is naturally cleaner under this model:
Check A handles asymmetric-bucket cases directly; Check B compares
from a clean frame-1 boundary.

---

## 6. Defensive infrastructure in the universal reset

The trichotomy raises a fidelity question: should the composer's
universal reset include *transient* defensive writes that aren't
strictly necessary for register state but ARE audible at first
play()?

Two candidates:

**(a) Test-bit oscillator-phase clear.** Set `V*.ctrl=$08` briefly
then `=$00` on all three voices. Resets oscillator phase
accumulators to zero. Without this, the first note's attack may
have a perceptible click whose exact shape depends on whatever
phase the SID happened to be at.

DMC does this; FutureComposer does its noise-clear sweep (different
approach to the same problem). Hülsbeck, Music_Assembler, and many
others skip it — relying on either clean host reset (phase=0
already) or accepting the click.

**Recommendation:** include test-bit clear in the universal reset.
Cost is ~6 SID writes (one $08, one $00 per voice). Benefit is
click-free attacks across the entire catalogue, regardless of host
or prior state. The rebuild becomes *more reliable than the
original* on this axis — same audible music, fewer click artifacts.

**(b) Noise-clear sweep.** The FutureComposer technique: briefly
emit noise on all voices then silence. Produces an audible "tick"
at song start that's part of the FutureComposer family signature.

**Recommendation:** do not include in universal reset. The
test-bit approach achieves the same SID-state-cleansing effect
silently. The FutureComposer noise tick is engine signature, not
music — accepting its loss is the trade-off for universality. (If
ever a strong user objection: add an opt-in
`init.sid.click_pattern: 'noise_burst'` priming field.)

---

## 7. The Hubbard init removal — re-examined

The commit `a29f01b` ("Hubbard '85: derive per-voice init from
freq_bytes — drop init block") removed init from the Hubbard '85
USFs. The reasoning at the time:

> The init block was 100% redundant with the engine constants.
> Phase 3 drops it from the 11 standard Hubbard '85 engines'
> USFs. The codegen reads from `engine_constants.freq_bytes`
> directly; an empty `usf.init.voices` means "use the engine
> constants verbatim."

This was correct for Hubbard '85 specifically: those six per-voice
init fields are bytes at fixed offsets in the engine's freq-table
region (which IS in the USF as `freq_table {}`). Reading them from
there is genuinely the same information as reading them from
`init {}` — and avoids redundancy.

**Crucially, this is also `voice_state` priming in the new
framing** (§4.5), not SID-state priming. Those six fields tell the
play loop "voice N starts with instrument 4, PWM accumulator at
$80, no slide" — engine-state runtime data. The fact that one
specific engine (Hubbard '85) happened to store this engine-state
in the freq-table memory region is *implementation*; the musical
meaning is "voice N's starting runtime state."

It was NOT a generalization that "init is always inferable from
the first pattern." Init is generally **NOT** inferable from
patterns — the empirical sampling in §2 proves this. What was
inferable was Hubbard-specific: per-voice runtime state stored in
a specific region of the freq table.

The takeaway: USF init *should* exist as a typed block, but its
contents should be **named musical parameters**, not raw bytes.
The new framing splits this block into `init.sid {}` (SID-chip
priming) and `init.voice_state {}` (engine-state priming). For
engines where init parameters are derivable from other USF data
(Hubbard '85: voice_state derivable from freq_table), the
corresponding block can be empty (or omitted entirely). For
engines where init parameters are independent (Bowden's envelope
primes), the block carries them.

---

## 8. Recommendations for the design call

1. **Adopt the reset / priming / environment trichotomy (§4) as
   the USF init model.** Reset is universal composer
   infrastructure invisible to USF; priming is per-tune typed
   musical parameters in USF; environment is a top-level USF
   field. Engine-internal bookkeeping doesn't enter USF.

2. **Split today's `init {}` block into `init.sid {}` and
   `init.voice_state {}`.** SID-chip priming and engine-state
   priming are conceptually different and have different
   provenance.

3. **Required `init.sid` schema fields, confirmed by the
   top-100-engine survey (§2b):**

   - **`master_vol` — mandatory.** ~50% of top-100 engines use a
     non-default value; $1F (filter mode bit + volume 15) alone
     accounts for 27 engines. Today's `master_vol.init_value` is
     the right shape; just needs the broader value range support
     and a rename/move into `init.sid` for consistency.

   - **`filter { cutoff_lo, cutoff_hi, res_routing } } — mandatory.**
     37 / 100 engines set the filter at init. Diverse values
     (cut_hi spans $00-$FF; res_routing spans $00-$F7). Not
     optional anymore.

   - **`voice N.envelope_prime: (ad, sr)` — when surfaced.** The
     Bowden case ($D405=$09, $D406=$00 etc.) is the only known
     example. Add as schema when migrating an engine that needs it.

   - **`voice N.pw_init: $XXXX` — when surfaced.** Engines that
     pre-set pulsewidth at init independent of any instrument.
     Currently covered by `instrument.pwm.init` for instrument-
     bound pw; this field is for raw-register priming.

4. **Other useful USF additions (orthogonal to init.sid):**
   - Hülsbeck's deferred-init flag → out of scope (engine
     bookkeeping, §4.4).
   - CIA-driven playback rate → top-level `playback_rate_hz`,
     not under init.

5. **Each schema addition must pass the
   [schema-addition checklist](usf_representation_principle.md#7-the-forbidden-shape)**
   — exhaust derivation alternatives first.

6. **Stop inferring engines from quirk flags.** If a USF needs
   Bowden's envelope primes written, the USF carries them
   directly — not through a `carry_leak` marker that maps via
   shape-detection to a hidden constants table. The current
   `_init_sid_writes_for_shape` helper in composer.py is wrong
   and will be deleted.

7. **The composer's init becomes a single universal routine,
   parameterised by USF.** Reset (silence-clear + baseline $D418
   + test-bit phase clear) is identical for every tune. Priming
   (filter, master vol, envelope_prime, voice_state) is read from
   USF. No engine-specific init code anywhere.

8. **Verification verdict shifts to "play-stream + SID-state
   checkpoint" (§5).** Add a `mode='play_plus_state'` to
   `compare_instruction_stream`. The old `match_all` /
   `match_post_init` lose primacy.

9. **Document the trichotomy** in
   `docs/usf_representation_principle.md` if we adopt it as the
   USF contract.

---

## 9. What this means for the Melonmania investigation

The principled fix:

- The Bowden engine binary writes `$D405=$09, $D406=$00,
  $D40C=$09, $D40D=$00` during init. Per the trichotomy: these
  are **priming** writes (set V1/V2 envelope state going into
  play). They go in USF.

- USF schema addition: `init.sid.voice N.envelope_prime: (ad, sr)`.
  For Melonmania (and all Berry_Vic Bowden tunes), the extractor
  emits:

  ```
  init {
    sid {
      voice 1 { envelope_prime: ($09, $00) }
      voice 2 { envelope_prime: ($09, $00) }
      ;; voice 3 has no envelope_prime — engine doesn't prime V3
    }
    voice_state {
      voice 1 { ctrl: $00 dur_field: $00 pwm_period: $00 pwm_dir: up
                instr: i1 slide_v: $00 }
      voice 2 { ... }
      voice 3 { ... }
    }
  }
  ```

- The composer's universal init reads `init.sid.voice.envelope_prime`
  and emits the corresponding `$D405/$D406/$D40C/$D40D` writes —
  for any tune that has the field set, regardless of engine.

- The carry-leak shape detection (`_init_sid_writes_for_shape`),
  the Bowden-engine-constants `BOWDEN_INIT_SID_WRITES`, and the
  `_init_sid_writes_for_shape` helper all get **deleted**.

- The composer's `_emit_init` reads from the USF priming fields
  directly. No reach to engine_constants. No quirk-flag dispatch.

The investigation closes: Melonmania sub 1's divergence was the
right tune surfacing the wrong-fix instinct. The right fix is the
schema addition.

---

## Sources

- [HVSC SID file format spec (`SID_file_format.txt`)](https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/SID_file_format.txt)
  — Michael Schwendt, Simon White, LaLa, Wilfred Bos.
- [`libsidplayfp/src/psiddrv.a65`](https://github.com/libsidplayfp/libsidplayfp/blob/master/src/psiddrv.a65)
  — reference PSID driver stub.
- [Companion long-form report](sid_init_research.md) — full quoted
  spec passages and source analysis.
- Frame-0 captures: this report, §2. Generated via `siddump
  --writelog` on representative SIDs from each engine family
  (random sample of 3 per family, duration=1.0s, subtune 0).
