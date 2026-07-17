# The Trichotomy — Evidence (SID `init` semantics — a research report)

> Companion to [`the_trichotomy.md`](the_trichotomy.md) (the canon doc, which
> is imported into every session; this file is loaded on demand). It is the
> EVIDENTIARY BASIS for the trichotomy's empirical claims: full PSID/RSID spec
> quotes, the verbatim libsidplayfp `psiddrv.a65` stub, and source-by-source
> analysis. Split out 2026-07-18 to keep the session import lean; content
> below is verbatim from the original appendix.

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
