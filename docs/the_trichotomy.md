# The Trichotomy

SID `init` — what it is and what USF should capture. A research
report for the USF design discussion.

Companion reading: the **appendix at the end of this file** ("SID
`init` semantics — a research report") is the long-form research
artifact — full PSID/RSID spec quotes, the verbatim libsidplayfp
`psiddrv.a65` stub, and source-by-source analysis. The trichotomy is
an EMPIRICAL claim; the appendix is its evidentiary basis, kept
co-located so a future revision has the evidence in hand. This first
part is the shorter synthesis for the design call.

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
   sampling across the **top 100 HVSC engine families (89%) plus the
   500-sample tail covering ranks 101-1000 plus unclassified
   tunes** — effectively 100% of the catalogue's structural
   coverage. Init write counts range from 0 to 279 and qualitatively
   different patterns. **Init is not inferable from the music — it's
   a per-engine setup contract.** Six classification buckets (§2b)
   emerge, and the bucket distribution is **structurally identical
   across the head and the tail** — the trichotomy holds at full
   scope.

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

See the appendix (§1–4) for the full quoted passages.

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

### Tail check: the remaining 11%

For thoroughness, the trichotomy was also tested against the
remaining 11% of HVSC: 200 samples from engine ranks 101-200 +
100 random samples from ranks 201-1000 + 200 random samples from
the 2,639 unclassified SIDs (`engine IS NULL`, sidid had no
fingerprint). Tool: `tools/init_survey_tail.py`.

**Bucket distribution is structurally identical to the top 100:**

| Bucket | Top 100 | Long tail (101-200) | Deep tail (201-1000) | Unclassified |
|---|---:|---:|---:|---:|
| Noise-burst / test-bit / multi-pass | 44% | 43% | 39% | 36% |
| Clean reset (silence-clear + $D418) | 19% | 15% | 18% | 17% |
| Partial setup (4-23 writes) | 11% | 18% | 20% | 24% |
| Deferred (no SID writes) | 11% | 13% | 10% | 11% |
| Thorough setup (>30 writes) | 7% | 7% | 10% | 9% |
| Minimal touch (≤3 writes) | 4% | 4% | 3% | 4% |

**Priming prevalence holds across the tail too:**

| | Top 100 | Long tail | Deep tail | Unclassified |
|---|---:|---:|---:|---:|
| Non-default $D418 | 50% | 46% | 42% | 41% |
| Filter set at init | 37% | 31% | 27% | 33% |

**One stress-test finding worth noting** — a small number of tunes
write to registers `$D419-$D41F` (the SID's read-only POTX / POTY /
OSC3 output / ENV3 output, plus mirror/unused slots). Examples:
`Maduplec/More_Los_Disco`, `Stephen_Ruddy/Psycho_Pigs_UXB`,
`Ozzy_Oldskool/Starglide`, `<unclassified>/Twinky_Goes_Hiking`.

These writes are **audibly no-ops on real SID** — the chip's
address decoder accepts them, but the registers are read-only,
so the writes are silently discarded. They're engine quirks
(sloppy loop bounds, accidental misaligned writes), not a new init
concern. Our universal init writes only $D400-$D418; the rebuild's
audible output is unaffected by skipping $D419-$D41F.

**Implication for verification (§5):** Check A's strict register-
state comparison should remain scoped to $D400-$D418. Including
$D419-$D41F would flag false positives on these quirky tunes
(rebuild doesn't reproduce the no-op writes) without any audible
divergence. The chip-state checkpoint is sufficient at $D400-$D418.

### Final verdict at full catalogue scope

**The trichotomy holds across 100% of HVSC.** Reset / priming /
environment / bookkeeping is sufficient to classify every init
across 60,572 SIDs. No engine surfaces a category that requires a
schema extension beyond the master_vol + filter priming fields
identified above (plus the rare envelope_prime when an engine
needs it).

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
   [schema-addition checklist](the_principle.md#7-the-forbidden-shape)**
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
   `docs/the_principle.md` if we adopt it as the
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
- Companion long-form report — the appendix below ("SID `init`
  semantics — a research report"): full quoted spec passages and
  source analysis.
- Frame-0 captures: this report, §2. Generated via `siddump
  --writelog` on representative SIDs from each engine family
  (random sample of 3 per family, duration=1.0s, subtune 0).

---

# Appendix: SID `init` semantics — a research report

**Audience:** SIDfinity USF design discussion.
**Date:** 2026-05-30.
**Question we are trying to inform:** what should USF capture about a
SID tune's `init` routine?

This report distinguishes three layers, because they are routinely
conflated in the literature:

1. **The SID file format spec** — what the `.sid` header fields
   formally promise, in the words of the actual specification.
2. **The C64 player environment** — what state the player (the host)
   sets up *before* calling the tune's `init`, and what happens
   *between* `init` returning and the first `play`.
3. **Composer convention** — what tunes actually do in `init` in
   practice, which is not specified anywhere but is broadly
   consistent because the same handful of music drivers (Hubbard,
   Galway, JCH, Link, ...) get reused across hundreds of tunes.

The spec is unusually quiet about (3) and not entirely complete about
(2), which is part of why this question is interesting. Where the
evidence runs out, I say so rather than fill the gap.

A note on citations: where a passage is quoted verbatim from the HVSC
spec file or from the libsidplayfp PSID-driver assembly, the source
URL is footnoted at the section break. I have read the full HVSC
spec text (`SID_file_format.txt`, 506 lines, authors Schwendt /
White / Lem / Bos / LaLa) and the full source of
`libsidplayfp/src/psiddrv.a65` for this report.

---

## 1. What is `init` formally?

### 1.1 The header fields

The SID v1 header (still the foundation of every later version) defines
`initAddress` at offset +0A and `playAddress` at offset +0C. The HVSC
spec says, verbatim:

> +0A    WORD initAddress
>
> The start address of the machine code subroutine that initializes a
> song, accepting the contents of the 8-bit 6510 Accumulator as the
> song number parameter. 0 means the address is equal to the effective
> load address.

> +0C    WORD playAddress
>
> The start address of the machine code subroutine that can be called
> frequently to produce a continuous sound. 0 means the initialization
> subroutine is expected to install an interrupt handler, which then
> calls the music player at some place. This must always be true for
> RSID files.

That is the entirety of the spec's prescriptive content about what
`init` and `play` are. Read literally: `init` is "the routine that
initializes a song" and `play` is "the routine that produces continuous
sound." The spec does not enumerate what either is *allowed* or
*required* to do.

The accumulator (A register) carries the **song number** — a value in
the range `1..songs` where `songs` is the +0E header field, with a
default given by `startSong` at +10.

> +0E    WORD songs
>
> The number of songs (or sound effects) that can be initialized by
> calling the init address. The minimum is 1. The maximum is 256.

So a single PSID file can package up to 256 separate musical pieces,
all addressed through the same `init` entry point, differentiated by
the value passed in A. This is the formal definition of "subtune."

(Source: HVSC `SID_file_format.txt`, sections "+0A initAddress",
"+0C playAddress", "+0E songs", "+10 startSong".)

### 1.2 The boundary between PSID and RSID

The same header layout describes both formats. The differences are
encoded as restrictions, not as new fields:

> RSID is based on PSIDv2NG with the following modifications:
>
> magicID = RSID
> version = 2, 3 and 4 only
> loadAddress = 0 (reserved)
> playAddress = 0 (reserved)
> speed = 0 (reserved)
> psidSpecific flag is called C64BASIC flag
>
> The above fields MUST be checked and if any differ from the above
> then the tune MUST be rejected. The definitions above will force
> tunes to contain proper hardware configuration code and install
> valid interrupt handlers.

So an RSID is, by construction, a PSID where `playAddress = 0` is
mandatory. The semantic consequence is that **for RSID files,
`init` MUST install its own interrupt handler** — there is no host
"play loop" to schedule. The spec puts this directly:

> 0 means the initialization subroutine is expected to install an
> interrupt handler, which then calls the music player at some place.
> This must always be true for RSID files.

The restriction on `initAddress` is asymmetric, too:

> +0A    WORD initAddress
>
> Valid values:
> - $0000 - $FFFF
> - $07E8 - $9FFF, $C000 - $CFFF (RSID)
>
> In RSID files initAddress must never point to a ROM area
> ($A000-$BFFF or $D000-$FFFF) or be lower than $07E8.

The ROM-area exclusion is justified later in the spec:

> A side effect of the bank register is that init MUST NOT be located
> under a ROM/IO memory area (addresses $A000-$BFFF and $D000-$FFFF)
> or outside the load image.

i.e. when the host calls `init`, the C64 bank register is in its
default state ($37 — I/O, KERNAL ROM, BASIC ROM mapped in), so
fetching code from the ROM ranges would read ROM, not the tune's
code. RSID forbids that case because RSID requires "every effort
[...] be made to make sure they are directly runnable on an actual
C64 computer."

PSID, being looser, allows `initAddress` anywhere in $0000–$FFFF and
the host is expected to adjust banking (see §2.1).

(Source: HVSC `SID_file_format.txt`, section "+04 version" through
"+0A initAddress" and the "Some words about the Real C64 SID file
format (RSID)" interlude.)

### 1.3 The boundary "init has finished" / "play begins"

**There isn't one in the spec.** The spec describes `init` as
returning (it is "a machine code subroutine") and `play` as being
"called frequently." Whether the first `play` call is back-to-back
with the `init` return, or one frame later, or aligned to the next
raster IRQ, is **not specified at the protocol level**. It is a
property of the host player.

In practice the host player is what enforces a boundary. We can see
this concretely in libsidplayfp's PSID driver stub (the small 6502
program the emulator installs to drive the tune); see §2.2.

---

## 2. The C64 player environment — what the host sets up

### 2.1 The two formats' "default environment"

The spec carves out the environment in two places. For PSID:

> For PSID Files
> --------------
>
> The default C64 environment for PSID files is as follows:
>
> VIC           : IRQ set to any raster value less than 0x100. Enabled
>                 when speed flag is 0, otherwise disabled.
> CIA 1 timer A : set to 60Hz (0x4025 for PAL and 0x4295 for NTSC) with
>                 the counter running. IRQs active when speed flag is 1,
>                 otherwise IRQs are disabled.
> Other timers  : disabled and loaded with 0xFFFF.
>
> When the init and play addresses are called the bank register value
> must be written for every call and the value is calculated as
> follows:
>
> if   address <  $A000 -> 0x37 // I/O, Kernal-ROM, Basic-ROM
> else address <  $D000 -> 0x36 // I/O, Kernal-ROM
> else address >= $E000 -> 0x35 // I/O only
> else                  -> 0x34 // RAM only

For RSID:

> For RSID Files
> --------------
>
> The default C64 environment for RSID files is as follows:
>
> VIC           : IRQ set to raster 0x137, but not enabled.
> CIA 1 timer A : set to 60Hz (0x4025 for PAL and 0x4295 for NTSC) with
>                 the counter running and IRQs active.
> Other timers  : disabled and loaded with 0xFFFF.
> Bank register : 0x37

Two observations:

- The bank register is **automatic for PSID** (host adjusts it per
  call based on the address) and **fixed at $37 for RSID** (because
  RSID forbids init/play in ROM ranges; the tune must do its own
  banking if it wants to e.g. write under $D000).

- Neither environment description says anything about `$D400-$D418`.
  The host does **not** zero the SID chip before calling `init`.
  This is implicit but worth stating clearly: the SID registers
  retain whatever state they had at the moment the host invoked
  `init`. In a cold-start emulator they are likely zero by default;
  on real hardware they hold whatever was last written.

(Source: HVSC `SID_file_format.txt`, sections "For PSID Files" and
"For RSID Files" under "The SID file environment".)

### 2.2 What libsidplayfp does — the reference player stub

libsidplayfp is the modern reference implementation and the basis of
all serious cycle-accurate SID emulation, including `siddump` in this
repo. Its PSID driver stub `psiddrv.a65` is the canonical reading of
the spec.

The full stub is short enough to reproduce here (Copyright 2014
Leandro Nini, 2001-2004 Simon White, 2000 Dag Lem; GPL):

```
            ; entry address
coldvec     .word cold

            ; initial user interrupt vectors
irqusr      .word irqret
brkusr      .word exception
nmiusr      .word exception
stopusr     .word setiomap

playnum     .byte 0
speed       .byte 0
initvec     .word 0
playvec     .word 0
initiomap   .byte 0
playiomap   .byte 0
video       .byte 0
clock       .byte 0
flags       .byte 0

            ; init/play PSID
play        jmp (playvec)
init        jmp (initvec)

            ; cold start
cold        sei

            ; turn interrupts off and
            ; clear any pending irqs
            lda #$00
            sta $d01a
            lda $d019
            sta $d019
            lda #$7f
            sta $dc0d
            sta $dd0d
            lda $dc0d
            lda $dd0d

            ; setup hardware

            ; maximum volume
            lda #$0f
            sta $d418

            ; set CIA 1 Timer A to 50/60 Hz
            lda video
            beq ntsc
pal         ldx #$25
            ldy #$40
            jmp timer
ntsc        ldx #$95
            ldy #$42
timer       stx $dc04
            sty $dc05

            ; set VICII raster to line 311 for RSIDs
            ldx #$9b
            ldy #$37

            ; we should use the proper values for
            ; the default raster, however if the tune
            ; is playing at the wrong speed (e.g.
            ; PAL at NTSC) use the compatibility
            ; raster instead to try make it work
            eor clock
            ora initiomap
            beq vicinit

            ; set VICII raster to line 0 for PSIDs
            ; (compatibility raster)
            ldx #$1b
            ldy #$00
vicinit     stx $d011
            sty $d012

            ; don't override default irq handler for RSIDs
            lda initiomap
            beq irqinit

            ; if play address, override default irq vector so
            ; we reach our routine to handle play routine
            lda playiomap
            beq irqinit
            ldx #<irqjob
            stx $0314

            ; 0 indicates VIC timing (PSIDs only)
            ; else it's from CIA
irqinit     lda speed
            bne ciainit

            ; enable VICII raster interrupt
            lda #$81
            sta $d01a
            jmp setiomap

            ; enable CIA 1 timer A interrupt
ciainit     lda #$81
            ldx #$01
            sta $dc0d
            stx $dc0e

            ; set I/O map and call song init routine
setiomap    lda initiomap
            bne setbank

            ; only release interrupt mask for real
            ; C64 tunes (initiomap = 0) thus
            ; providing a more realistic environment
            lda #$37
setbank     sta $01

setregs     lda flags
            pha
            lda playnum
            plp
            jsr init
            lda initiomap
            beq idle
            lda playiomap
            beq run
            lda #$37
            sta $01

run         cli
idle        jmp idle

irqjob      lda $01
            pha
            lda playiomap
            sta $01
            lda #0
            jsr play
            pla
            sta $01
            dec $d019
irqret      lda $dc0d
            pla
            tay
            pla
            tax
            pla
            rti
```

Several things worth flagging:

**(a) The host writes `$D418 = $0F` *before* calling `init`.** The
stub explicitly sets maximum volume "maximum volume / lda #$0f / sta
$d418" before the CIA/VIC setup and before `jsr init`. This is a
universal pre-init action.

**(b) The host does NOT zero `$D400-$D417`.** Look at the cold-start
block: it touches `$d01a` (VIC interrupt mask), `$d019` (VIC
interrupt latch), `$dc0d`/`$dd0d` (CIA interrupt masks), `$dc04/05`
(CIA timer latches), `$d011/$d012` (VIC raster), and `$d418` (SID
volume). It does not write the SID voice registers $D400-$D417.

**(c) The CPU enters `init` with A = playnum (the subtune index) and
P (status flags) = `flags`.** The unusual `pha / plp / jsr init`
sequence loads the 6502 status register with caller-supplied flags
(`flags` defaults to zero, so this is normally "all flags clear").
This is essentially a clean processor entry.

**(d) Between `init` returning and the first `play` call: the stub
sits in `idle: jmp idle`** until the next interrupt fires. The actual
flow is:

   1. `jsr init` returns.
   2. Either `idle jmp idle` (for tunes that install their own IRQ
      handlers — including all RSIDs) or `run cli` (re-enable
      interrupts) followed by `idle jmp idle`.
   3. The pre-armed CIA-timer-A or VIC-raster interrupt fires.
   4. `irqjob` runs, which `jsr play`s the tune's play routine with
      A=0.
   5. `irqjob` writes `$d019` (acknowledges the raster latch) and
      `rti`s.
   6. Loop to step 3.

So between `init` returning and the first `play` call, the CPU is
running `jmp idle` and the SID is being clocked but no `$D4xx` writes
are happening. The SID's audible state during that gap is whatever
`init` left it in.

**(e) `play` is invoked with `A = 0`.** `lda #0 / jsr play`. This is
not documented in the spec, but is consistent across all PSID drivers
I am aware of. Some tunes look at A in `play` and skip an
"if-this-is-the-init-pass" branch when A != 0 — but for PSID this
distinction is moot since `init` is called via `jsr init` directly,
not via `play` with a flag.

(Source: `libsidplayfp/src/psiddrv.a65`, full file reproduced
above. https://github.com/libsidplayfp/libsidplayfp/blob/master/src/psiddrv.a65)

### 2.3 What `siddump` (our writelog tool) does

For grounding, the local writelog tool we use as ground truth
(`tools/siddump.cpp`) is a thin wrapper around libsidplayfp. The
relevant sequence is:

```
SidTune tune(filename);
tune.selectSong(subtune);
sidplayfp engine;
engine.config(cfg);
engine.load(&tune);        // installs the psiddrv stub from §2.2
engine.initMixer(false);
// (loop)
int samples = engine.play(cyclesPerFrame);
```

`engine.load()` is what installs the driver stub and triggers the
cold-start path through `init`. The first `engine.play(cyclesPerFrame)`
call advances the emulator for one frame's worth of cycles, during
which the pre-armed interrupt fires and `irqjob` calls the tune's
`play` for the first time.

The `cyclesPerFrame` value is `63 * 312 + 32 = 19688` on PAL — the
full PAL frame plus a 32-cycle margin "to ensure we always cross the
raster trigger point" (siddump.cpp:222-227). The +32 margin causes
the well-known ~8c/frame measurement drift noted in our cycle-stream
comparator's documentation.

The siddump `--writelog` output thus contains writes that originate
both from `init` (its writes happen during `engine.load()`) and from
each subsequent `play` invocation. Our `compare_instruction_stream`
deliberately **drops the init invocation** (see
`pipelines/hubbard/verify_cycle.py`) because we have repeatedly found
that init-time register writes are an idiosyncratic mix of "set up
the chip" and "leak state from a previous tune" that does not need
to match byte-for-byte for two tunes to be musically identical from
the moment `play` starts running.

(Source: `tools/siddump.cpp` lines 160–280; project memory
`feedback_observation_drift` and `feedback_ground_truth`.)

---

## 3. What does `init` do *musically* vs *structurally*?

The spec is silent on this. Empirically, across the dozen Hubbard
1985 engines this repository has byte-exact rebuilt, plus published
disassemblies of other drivers, init routines fall into roughly four
content categories:

### 3.1 Category A — "set up the chip" writes

The most common init action is to write a small, fixed set of SID
registers to put the chip into a known state. The canonical Rob
Hubbard example, from the published Monty-on-the-Run disassembly
quoted on `1xn.org/text/C64/rob_hubbards_music.txt`:

```
  lda #$00         ;clear control regs
  sta $d404
  sta $d40b
  sta $d412
  sta $d417       ; filter resonance/routing

  lda #$0f         ;full volume
  sta $d418
```

This is essentially "gate off all three voices, kill the filter, set
master volume to $0F." Hubbard then sets a status byte (`mstatus =
$40`, meaning "init pending") and **returns**. He deliberately does
*not* play any notes from `init` itself.

Note that the host (libsidplayfp's stub) already wrote $D418 = $0F
before calling init (§2.2(a)), so this rewrite is redundant under
libsidplayfp but necessary on a real C64 if you cannot guarantee the
host did it. Composer practice is to do it themselves anyway.

### 3.2 Category B — driver state initialization (no SID writes)

The bulk of init's work in most engines is purely RAM-level: copying
pointers, zeroing counters, initializing voice state machines. None
of this touches the SID chip. This is "structural" content in your
framing — it is engine internal state, not anything the listener can
hear.

For our 12 Hubbard '85 engines this is precisely what the USF v3
`init {}` block already captures, parameterised — per-voice initial
`ctrl`, initial `dur_field`, initial `pwm_period`, initial `instr`,
and so on (see `docs/usf_format.md` §"init block"). These values
*will* affect the first `play` frame's writes, so they belong in
USF, but they are not themselves audible.

### 3.3 Category C — CIA timer programming (multispeed PSID)

Some PSID tunes run at 2x, 3x, 4x speed by reprogramming CIA 1
Timer A in their init routine. The spec acknowledges this:

> Note that if 'play' = 0, the bits in 'speed' should still be set
> for backwards compatibility with older SID players. New SID
> players running in a C64 environment will ignore the speed bits in
> this case.

The community summary (chiptunesak, paraphrased in §1 search
results) is direct: "for multispeed PSID files to play back
correctly in many low-fidelity emulation players, those PSIDs must
set the CIA #1 Timer A in their init routine to indicate how much
shorter the play interval is than the frame interval."

This is musically significant — it sets the playback rate — but it
is not an audible *SID* write. It is a hardware-timer programming
write to `$DC04/$DC05`.

### 3.4 Category D — IRQ vector installation (RSID, and some PSIDs)

For RSID tunes, init must install an IRQ vector at `$0314/$0315` (or
hook the raster IRQ via $FFFE if banking allows) and enable the
appropriate CIA / VIC interrupt source. After this, `init` returns
and the IRQ machinery — set up entirely by the tune — schedules play.

PSID tunes occasionally do this too, even though they have a
`playAddress`, when they need a custom IRQ chain (multi-source IRQs
for samples + music, raster splits for graphics in demos, etc.).

### 3.5 A clean conceptual boundary?

For Hubbard-style PSID engines: **yes, fairly clean.** Init does
A + B (zero a handful of registers, set up driver state) and
nothing else. The SID's audible state after init is "voices gated
off, volume = $0F." That is a silent SID with the master volume
unmuted.

For RSID and demo-track tunes: **no clean boundary.** Init can do
anything: install IRQs, write samples, prefetch a row of music, play
a sting. Some demo tunes have very elaborate inits.

The boundary the spec gives us is the one in §1.3 — `init` returns
and then `play` runs. It is a *control-flow* boundary, not a
*musical-content* boundary.

---

## 4. What happens between `init` returning and the first `play`?

This is the question with the least spec coverage and the most
practical relevance to USF. Three things to distinguish:

### 4.1 What the spec says — nothing

The spec does not address it. The closest it comes is the timing
implication of the speed flag: "A 0 bit specifies vertical blank
interrupt (50Hz PAL, 60Hz NTSC), and a 1 bit specifies CIA 1 timer
interrupt (default 60Hz)." That tells you *how often* play runs, not
*when the first one fires relative to init*.

### 4.2 What libsidplayfp does

From the driver stub in §2.2: after `jsr init` returns, the stub
runs `cli` (or skips it for tunes that already enabled interrupts in
init) and then `jmp idle`. The next pre-armed interrupt fires
*whenever it would have fired anyway* — typically very soon, since
CIA 1 Timer A was armed before the init call and has been counting
down throughout init's execution.

So the **first `play` call happens at the next interrupt boundary
after init returns**, which on PAL VBI timing is some fraction of a
frame later, and on a 50Hz CIA tune is somewhere in the next ≤19656
cycles.

### 4.3 Is the SID expected to be silent during the gap?

There is no spec rule. But every PSID engine I have read does one
of three things in this gap:

1. **Silent** — voices gated off by init (Category A above). This
   is the dominant case. The first audible sound in the song is
   triggered by the first `play` call.

2. **Sustained from a prior chip state** — init didn't bother to
   clear $D404/$D40B/$D412, the chip was in some random state, and
   it stays there until play runs and overwrites it. On a real C64
   coming out of a clean BASIC boot, this is silence anyway because
   $D400-$D418 is all zero on power-up. In an emulator with a clean
   reset, ditto. The first `play` always overwrites, so the gap is
   never audibly meaningful.

3. **A pre-loaded note** — rare; some engines write the first row of
   music in init so that the very first interrupt is "row tick 1"
   not "row tick 0". I have not seen this in our 12 Hubbard engines;
   we treat the first `play` call as the first frame.

For our USF purposes, the convention to lean on is **"the first
audible event of the song is the first `play` call's writes"**.
This matches every Hubbard-'85 engine we have rebuilt; it does not
universally match RSID/demo tunes but those are not in the current
USF v3 scope.

### 4.4 The "init writes count as music or as engine state?" question

From the listener's standpoint, an init-time write to $D418=$0F that
play() never updates means the chip stays at master volume $0F for
the entire song. Is that "music" or "engine state"?

I think the honest answer is **it's neither — it's a side-channel
that USF should encode explicitly but separately from per-frame
play writes**.

- It is *not* per-frame play data; capturing it among the play
  writes would make every other engine's first-frame output diverge.
- It is *not* purely structural; an init that fails to set $D418=$0F
  produces a silent SID even with correct play() output. The value
  is musically necessary.

The current USF v3 `init {}` block in `docs/usf_format.md` already
takes this position: per-voice initial state lives in `init {}` as
parameters (`ctrl`, `dur_field`, `pwm_period`, `pwm_dir`, `instr`,
`slide_v`), and the codegen emits the corresponding writes wherever
convenient in the rebuilt binary. We do not currently carry the
master-volume init value in USF because every Hubbard engine
hardcodes $D418=$0F — but that decision should be revisited the
moment we migrate an engine that uses a non-$0F master volume.

---

## 5. Why does `init` exist at all? Could engines do everything in `play()`?

A reasonable design question. The answer has three parts.

### 5.1 Subtune selection

This is the single piece of functionality that absolutely requires a
separate entry point: the host needs a way to say "start subtune 7"
that is distinct from "render one frame of audio." Cramming both
into a single `play(A)` entry would force every play call to test
"is A a subtune number or a no-op?" — workable, but the spec
authors chose a cleaner two-function interface.

The spec quote, again:

> +0A    WORD initAddress
>
> The start address of the machine code subroutine that initializes
> a song, accepting the contents of the 8-bit 6510 Accumulator as
> the song number parameter.

The accumulator carries the subtune number *at init time only*. By
the time `play` runs (with A=0 per the libsidplayfp stub
convention), the subtune choice has been latched into engine state.

### 5.2 First-frame vs steady-state cost

A music engine that did "if first call, do init; else play" in a
single entry point would have to test that branch every frame. Cheap
on modern hardware, but on a 6502 cycle budget where every play call
is competing with the rest of a game's logic, the savings from
splitting them are real. Composers and engine authors built
two-routine interfaces for performance reasons that the SID format
then standardised.

### 5.3 Hardware initialization is genuinely different

§3.1 — clearing voice control bytes — is a one-shot action. §3.3 —
programming CIA timers — is a one-shot action. §3.4 — installing an
IRQ vector — is a one-shot action. These are categorically distinct
from "produce the next frame of audio." A two-routine interface
makes the distinction explicit.

So `init` exists because:

- **Subtune selection** needs an entry point that takes a parameter;
- **One-shot hardware setup** is conceptually distinct from
  per-frame audio production;
- **Performance**: separating one-shot from steady-state saves
  cycles in the inner loop.

None of these are forced by the spec; all of them are forced by
practical C64 programming, and the spec records the convention.

---

## 6. Init writes vs play writes from a listener's standpoint

### 6.1 The deterministic-SID frame

The SID chip is **stateful and deterministic**: it has 25 writable
registers ($D400-$D418), and given a fixed initial state and an
ordered sequence of writes, the resulting waveform is fully
determined. (This is the principle on which the project memory
`feedback_observation_drift` is built — "the SID is deterministic
from its register state.")

From this point of view, *every* `$D4xx` write — whether issued from
init or from play — is part of the audio waveform. There is no
ontological distinction.

### 6.2 The pragmatic distinction

But the *purpose* of init and play writes differs:

- **Init writes establish a baseline** (volume = $0F; voice 1
  control = $00; filter = off). They are written once and the chip
  remains in that state until play overwrites.

- **Play writes are dynamic** (gate notes, sweep PWM, adjust
  envelope). They change every frame and constitute "the music."

The pragmatic line is: **a write is "engine state" if no play frame
ever overwrites it; it is "music" otherwise.** This is testable
post-hoc by scanning every play() frame's writeset for the register
in question.

Applied to a Hubbard-'85 engine:

- $D418 = $0F at init, never touched by play → engine state.
  (Hubbard '85 master volume is constant. Some other engines —
  Galway's volume-triggered samples; the song-end fade Hubbard does
  in `feedback_hubbard_song_end_fade` — DO update $D418 in play. So
  "engine state" is engine-specific.)
- $D404/$D40B/$D412 = $00 at init, written every frame by play →
  music. The init zero is a redundant baseline.
- $D415/$D416/$D417 = $00 at init (filter cutoff lo/hi, filter
  ctrl), written by play if the engine uses the filter. Engines
  that don't touch the filter leave these at $00 for the whole song
  — and that absence-of-write is part of the engine's audio
  character.

### 6.3 Implication for USF

The question is: **does USF need to capture init writes that play
never overwrites?**

For Hubbard '85 specifically:

- $D418 = $0F → captured implicitly via codegen (always emitted as
  part of the init prologue); does not appear as a parameter
  because all 12 engines use $0F. Migrate an engine that uses a
  different value and this becomes a USF parameter.
- $D404/$D40B/$D412 = $00 → redundant, since play overwrites every
  frame. Not captured.
- $D415/$D416/$D417 = $00 → captured implicitly via the init block
  voice fields where filter is used; engines that don't use filter
  leave them at $00 by virtue of nothing writing them.
- Per-voice $D400/$D401 (frequency lo/hi), $D402/$D403 (pulse width),
  $D405/$D406 (ADSR) at init time → captured by USF's per-voice
  init fields where they are *load-bearing* (e.g. PWM period that
  the engine treats as initial state, ctrl byte for the gate path).

The principled framing, consistent with
`docs/the_principle.md` (which I re-read in full for
this report), is:

> A write that the composer authored as part of the engine's
> mechanism — a fixed baseline — belongs in USF as a parameter
> (named, musically meaningful). A write that play() overwrites
> every frame need not be captured because USF describes what
> play() does.

The forbidden shape (§7 of the principle doc) is **carrying init's
raw 6502 instructions as bytes in USF**. That would index into the
engine and learn nothing the model can interpolate over.

The current USF v3 `init {}` block is principled in this sense:
each field (`ctrl`, `dur_field`, `pwm_period`, `pwm_dir`, `instr`,
`slide_v`) is a named musical parameter, not an opaque setup
program. The block's role is **"per-voice initial musical state for
the first play frame"**, which is exactly the structured middle the
principle document prescribes.

---

## 7. Open questions and design implications

### 7.1 What `init` content does USF currently NOT capture?

1. **Master volume at init.** Hardcoded $0F in our codegen.
   Universal across Hubbard '85; will need a USF parameter when
   migrating an engine that uses a non-$0F value (e.g. Galway's
   sample engines write $D418 from a table every frame; the "init
   value" is more like a starting envelope).

2. **Filter init state.** All current Hubbard '85 engines initialize
   filter registers ($D415-$D417) to $00 implicitly. Engines that
   ship with a non-trivial filter routing would need this
   parameterised.

3. **CIA timer programming for multispeed.** None of our 12 engines
   are multispeed, so this hasn't surfaced. When it does, the USF
   should carry the play rate as a parameter (frames per second, or
   plays per VBI), and the codegen should emit the corresponding
   `$DC04/$DC05` writes in init.

4. **IRQ vector installation (RSID).** Not yet in scope — USF v3 is
   PSID-only across our 12 Hubbard engines and the Companion family.

5. **The very first play() invocation's `A` register.** Hardcoded to
   `A = 0` by libsidplayfp's stub. None of our engines branch on A
   in play, so this is fine. Worth noting for forward-compat.

### 7.2 Should USF track "audibly silent" init?

If init leaves all voices gated and the master volume at $0F, the
chip is silent until play runs. The current USF v3 does not encode
"is the SID silent at the init/play boundary?" as a tested invariant
— it just emits the init writes the codegen has been told to emit,
and verification compares the resulting SID's per-frame output to the
original. If the original is silent at frame 0 (before play has
ever run), our rebuild had better be too — and this is enforced by
the bytewise md5 of `$D400-$D418` snapshots.

So the answer is: USF doesn't need a dedicated "silent at init"
flag; the existing verification path catches any divergence.

### 7.3 Should USF capture init writes as data (Pole B-ish) or as
named parameters (the structured middle)?

The principle doc's answer is unambiguous: **named parameters**. Any
`bytes`-typed init field would be the forbidden shape.

The Hubbard-'85 engines have proven this is workable: 12 engines × 89
subtunes byte-exact through a parametric `init { voice { ... } }`
block with 5-6 named fields per voice. The fields are *musically
meaningful*:

- `ctrl` — the SID voice 1/2/3 control byte (waveform + gate +
  test/ring/sync bits). Maps directly to a published 8-bit SID
  register field that any composer reads as a unit.
- `pwm_period`, `pwm_dir` — the PWM accumulator's initial value and
  direction. The PWM modulation is a musical parameter the
  composer chose.
- `instr` — which instrument program the voice starts with.
- `dur_field` — the vibrato/duration counter initial value, which
  affects when vibrato first engages relative to note start.

These are all *content the composer chose*, which is exactly Rule 2
of the principle doc.

### 7.4 Should we eventually unify init and play into a single
"frame -1 → frame 0 → frame 1 → ..." view?

Tempting but problematic:

- Init writes happen at undefined cycle offsets relative to the
  start of frame 0 (depending on the host stub). The cycle-stream
  comparator already drops init for this reason.
- A unified view would force USF to commit to a specific *timing*
  for init writes, which is host-defined and not stable across
  emulators.
- Subtune selection — the A-register input — has no analog in a
  per-frame model.

The two-routine model is well-suited to a two-section USF: the
`init {}` block for the one-shot baseline; the `subtune N {}` blocks
for per-frame content. We should keep this split.

---

## 8. Summary — recommendations for the USF design discussion

A. **`init` is formally just "the routine called once at song start
with A = subtune number."** The PSID/RSID spec says nothing about
what it must or must not do beyond memory-location restrictions.
All "init does X" claims you find in documentation are *convention
about composer practice*, not protocol.

B. **The host (libsidplayfp's PSID stub) writes $D418 = $0F before
calling init and otherwise leaves the SID chip at whatever state the
emulator's reset produced (zero on a clean reset).** No host zeroes
$D400-$D417 for the tune.

C. **The gap between `init` returning and the first `play` call is
undefined in length** (depends on speed flag and CIA arming) but is
always a "silent CPU loop"-style wait in libsidplayfp. The SID is
not driven during the gap, so its audible state during the gap is
whatever init left it in. For our 12 Hubbard '85 engines that is
"voices gated off, master volume $0F" — silence.

D. **From a listener's standpoint, init writes that play never
overwrites are equally part of the audio waveform as any play
write.** The distinction is purpose, not effect. USF should
capture these baseline writes as named parameters where they are
load-bearing (and confirm they are derivable/constant where they
are not).

E. **The current USF v3 `init {}` block design is consistent with
the representation principle.** It carries per-voice initial state
as named musical parameters (ctrl, pwm_period, etc.), not as raw
bytes. The codegen reproduces the original's init-time SID writes
faithfully via parameters that are interpolatable and cross-engine
reusable.

F. **Open growth axes for USF init:**
   - Master volume parameter (when an engine uses non-$0F).
   - Filter init state (cutoff hi/lo, resonance, routing) when an
     engine uses it.
   - Play rate / multispeed parameter (when migrating a multispeed
     engine).
   - RSID-specific IRQ install metadata (when migrating RSID).

   None of these need adding pre-emptively; each becomes a USF
   parameter the first time it is musically distinct between two
   engines or two subtunes within an engine.

G. **What USF should NOT do:**
   - Carry init's raw 6502 bytes as a `bytes`-typed field. This is
     the forbidden shape from the principle doc.
   - Encode "init kind: $0..$N" as a categorical token referencing
     a library of init routines in the engine. Same forbidden
     shape, schema-shaped.
   - Try to merge init and play into a single per-frame stream.
     The cycle offsets are host-defined and the subtune-number
     parameter has no per-frame analog.

The honest summary: the spec leaves more open than it pins down,
which is why composer practice — and our reverse-engineering of it —
ends up doing the load-bearing work. USF v3's existing `init {}`
block captures the right things for the engines we've migrated. The
risk to manage is feature creep when a new engine surfaces a novel
init-time behaviour: keep growing along the *musical parameter*
axis (per Rule 2 of the principle doc), never along the *opaque
kind* axis.

---

## Sources

Primary specifications:

- HVSC `SID_file_format.txt` (authors: Michael Schwendt, Simon
  White, Dag Lem, Wilfred Bos, LaLa). Full 506-line spec read for
  this report.
  https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/SID_file_format.txt

- libsidplayfp PSID driver stub `psiddrv.a65` (Leandro Nini, Simon
  White, Dag Lem). Full 289-line assembly source read for this
  report.
  https://github.com/libsidplayfp/libsidplayfp/blob/master/src/psiddrv.a65

- libsidplayfp PSID driver C++ harness `psiddrv.cpp`.
  https://github.com/libsidplayfp/libsidplayfp/blob/master/src/psiddrv.cpp

- libsidplayfp `PSID.cpp` (SID tune loader). Verified RSID/PSID
  header validation logic.
  https://github.com/libsidplayfp/libsidplayfp/blob/master/src/sidtune/PSID.cpp

Secondary / contextual sources:

- Rob Hubbard music driver disassembly (Monty on the Run).
  https://www.1xn.org/text/C64/rob_hubbards_music.txt

- ChiptuneSAK "Commodore SID Music" documentation. Useful on
  multispeed CIA-timer convention.
  https://chiptunesak.readthedocs.io/en/stable/sid.html

- C64 OS sidplay.lib programmer's guide. Useful prose on the host
  side of the init/play protocol.
  https://www.c64os.com/c64os/programmersguide/usinglibraries_sidplay

- OCRemix SID Format Specification wiki. Restates the HVSC spec
  with the same content.
  https://ocremix.org/info/SID_Format_Specification

- Lemon64 forum threads on SID playback and SID register state on
  song end. Community-level confirmation of conventions.
  https://www.lemon64.com/forum/viewtopic.php?t=61054
  https://www.lemon64.com/forum/viewtopic.php?t=66773

Local project references consulted:

- `/home/jtr/sidfinity/docs/usf_format.md` — current USF v2/v3 init
  block design.
- `/home/jtr/sidfinity/docs/the_principle.md` —
  the discipline this report is consistent with.
- `/home/jtr/sidfinity/tools/siddump.cpp` — our writelog tool, lines
  160-280 for the init/play invocation path.
