# The Principle

**Status: load-bearing. Read this document in full before designing or
changing how USF represents any instrument, effect, or behavior — and
before adding any composer code that branches on USF content. Do not
act on a summary of it. The reasoning chain below *is* the content — a
slogan drawn from it ("effects parametric, engine holds mechanism")
reproduces the shallow version and silently drops the discipline, which
is the part that does the work.**

This document settles one question: when a SID engine does something —
vibrato, PWM, an arpeggio, a portamento, a wave program — how should
USF represent it so the result is the best possible machine-learning
training data?

The question has a tempting wrong answer that looks right. The wrong
answer is a slow regression into the very thing the USF refactor was
built to eliminate. This document exists so that regression does not
happen by drift.

---

## 1. The decision every effect representation faces

Every effect representation sits somewhere on a spectrum between two
poles.

**Pole A — USF holds a thin reference; the engine holds the
implementation.** The USF instrument says, in effect, "vibrato number
7." The actual computation lives in the engine.

**Pole B — USF holds the full behavioral definition; the engine is a
generic interpreter.** The USF instrument carries the LFO table and the
update arithmetic as data; the engine just runs whatever it is handed.

At a glance both look defensible. Pole A keeps the USF schema small and
abstract — and "abstract" sounds like a virtue. Pole B keeps the USF
complete — nothing about the sound is hidden. So the instinct is that
the choice is a matter of taste, or a matter of how much you trust the
engine.

It is not. In their pure forms **both poles produce bad training
data**, for opposite reasons. The correct representation is a specific
structured middle — and it is not a compromise between the poles, it is
a different thing from either.

---

## 2. Failure mode A — engine variants behind references

Make Pole A concrete. Suppose, reverse-engineering Hubbard's catalogue,
you find twelve different vibrato implementations. You place all twelve
in the engine and give the USF instrument a field: `vibratoKind` with
values `0..11`.

To a learning model, `vibratoKind` is an **opaque categorical token**.
`kind 3` and `kind 7` are exactly as related as any two arbitrary
symbols in a vocabulary — which is to say, not at all, until the model
laboriously infers relationships from co-occurrence. The model cannot
see that both are "vibrato." It cannot transfer anything it learned
about one to the other. It cannot generate a vibrato that is "like
kind 3 but a little closer to kind 7," because the representation
offers no notion of *between*. Whatever structure related those twelve
implementations — and they are all vibrato, so there is a great deal of
structure — has been discarded at the moment of encoding.

This is not a minor inefficiency. **It is `engineQuirks` reborn.** The
USF refactor's founding purpose was to stop leaking engine internals
into the training data. Leaking an *engine address* and leaking an
*engine enum index* are the same disease: in both cases the USF carries
a number whose meaning is defined by the engine and is invisible to,
and unlearnable by, the model from the number alone.

Note the trap precisely: it does not matter that the engine is clean,
or that the `vibratoKind` field looks tidy and abstract in the schema.
**Abstractness of the schema is not the goal. Musical structure in the
data is the goal.** An index into an engine-defined library is an
engine artifact no matter how neat it looks.

---

## 3. Failure mode B — the raw behavioral program in USF

Now make Pole B concrete. The engine becomes a generic interpreter; the
USF instrument carries the actual vibrato program — the LFO contour,
the per-frame update arithmetic — as data.

This representation is *complete* and, in one sense, maximally
*structured*: two nearly identical vibratos have nearly identical
programs, so their similarity is visible.

But the model's action space now includes "write a synthesis
algorithm." The set of programs that actually sound like vibrato is a
vanishingly thin sub-manifold of the space of all programs; the
overwhelming majority of that space is silence, noise, or garbage. The
model must spend almost all of its capacity learning to *avoid* the
nonsense rather than learning music. And the representation is verbose —
every instrument carries a small program, and token counts explode.

Pole B is complete but, in practice, **unlearnable**. Completeness is
necessary; it is not sufficient.

---

## 4. The resolution — parametric over a musical basis

The correct representation is neither pole, and it is not a blend of
them. It is this:

> When you find N implementations of an effect, **do not enumerate
> them.** Ask instead: *what is the union of musical degrees of freedom
> across all N?* Then design **one parametric form** whose parameters
> span that union. Each of the N implementations becomes a *point* —
> or a small region — in that one parameter space.

For vibrato:

```
vibrato { shape, periodFrames, depthSemitones, onsetDelay,
          rampFrames, unipolar, ... }
```

Hubbard's implementation 3 and implementation 7, if they are nearly the
same algorithm, now land as nearly the same point. Their similarity is
not discarded — it is the literal geometric fact of their proximity.

The distinction that makes this work is **parameter versus kind**. A
*parameter* — depth, rate, delay — is ordered and continuous-ish; the
model can interpolate along it, and "depth 3 is near depth 4" is true
by construction. An opaque *kind* is none of those things. Where a
difference between implementations is genuinely categorical and cannot
be made a parameter, it becomes a **small, musically meaningful enum** —
`shape: triangle | sine | square | table` — perhaps four values, each
with a meaning the model can actually learn and that generalizes across
instruments and engines. That is categorically different from
`kind: 0..40`, an enum of arbitrary engine-defined values.

This *is* "the definition lives in USF" — Pole B's virtue — but
realized as a parameter vector over a musical basis rather than as raw
code. It is also abstract and schema-small — Pole A's virtue — but the
abstraction is *musical*, not an engine pointer. The structured middle
keeps what was right about each pole and discards what was fatal.

---

## 5. Why this helps learning, specifically

The reason is concrete, not aesthetic.

A categorical token is handed to the model as an embedding it must
learn *entirely from co-occurrence statistics*. The model is given no
prior that two effects are similar; it must rediscover the whole
similarity structure of the effect vocabulary from the data.

A parametric feature hands the model a **metric space for free**. "Depth
3 is close to depth 4" is built into the representation before any
training happens. The similarity structure is *given*, not learned.

This matters because of the data regime we are actually in. C64 SID
music is *limited* data — on the order of a few thousand Grade-A songs,
not billions of tokens. Under limited data, the inductive bias of a
structured parameter space is not a refinement; it is frequently the
difference between a model that generalizes and a model that memorizes.
(With unbounded data, opaque categorical tokens would eventually be
fine — the model would learn the structure anyway. We do not have
unbounded data. The regime is the whole point.)

---

## 6. The two discipline rules

The resolution in §4 is only correct if it is applied with discipline.
Two rules.

### Rule 1 — cluster by behavior, not by code

Three byte-different 6502 routines that all produce the *same* triangle
LFO are **one** USF vibrato, not three. Hubbard hand-coded the same
musical idea differently across games to save bytes; that difference is
space-saving *mechanism*, and mechanism is exactly what you deconstruct
away (see the memory `feedback_deconstruct_not_reproduce`). A new
parameter — still less a new `shape` value — is justified **only** when
the resulting *SID writeset* (per-frame ordered `(reg, val)` writes)
differs, never when only the 6502 machine code differs.

**The concrete test is writelog comparison.** The SID is deterministic
from its register state: identical write stream, identical sound. For
non-digi music, two implementations are "the same musical concept" iff
their global cycle-ordered `(reg, val)` write streams match across the
song (`compare_instruction_stream` in
`pipelines/hubbard/verify_cycle.py` — concatenates writes across all
frames in cycle order, drops the init invocation; siddump's VBI-frame
bucketing of writes is reporting, not part of what the chip receives).
For digi, where cycle IS the signal, the test is cycle-strict
per-frame writelog comparison (`compare_strict`) — same write timing
matters there because the bit pattern timing is the sample.

When the test needs to attribute writes to a specific voice or 6502
routine (e.g. to isolate a single-voice effect from a multi-voice
frame), use `src/usf/audit.py` — it captures `(frame, PC, reg, val)`
per SID write, filters to one voice, and optionally cross-references
each PC against a disassembly file.

The failure this rule guards against is **over-splitting**: naively
minting one variant per byte-different routine you discover. That hands
you twelve "kinds" that are mostly the same triangle — opaque *and*
redundant, the worst of every world. Cluster by what the effect *does*,
not by how it was *typed*.

### Rule 2 — musical content to USF, interpreter to engine

If a vibrato uses a custom sixteen-byte LFO contour, that contour is
*musical content* — a shape the composer chose — and it belongs in USF,
as data: `shape: .table [...]`. The loop that reads a table and adds it
to the frequency is the *interpreter* of that content, and it belongs
in the engine.

The dividing line is sharp and it is the same line every time:
**content the composer chose is USF; the machinery that realizes
content is engine.** A wavetable is content. A triangle-LFO loop is
machinery. The depth knob is content. The 6502 that applies the depth
is machinery.

---

## 7. The forbidden shape

From the rules above, one concrete prohibition.

The moment an instrument or effect field is `somethingKind: int`, or
`variantPtr`, or anything else that indexes into an engine-defined
library, **the parameterization has failed and that field is the
leak.** It is the §2 failure mode wearing a schema-shaped disguise.

The test is not "is it an enum." A small enum whose values are
musically meaningful (`shape: triangle|sine|square|table`) is fine —
its values generalize, the model can learn what each *means*, and there
are a handful of them. The test is: **does the model have to learn what
each value means from scratch, with no structure given by the
representation?** If yes, it is the forbidden shape.

The master rule, stated once: **the engine may hold mechanism; it must
never hold a library that the USF indexes into.**

---

## 8. The same prohibition binds the composer

The schema-level prohibition in §7 has a structural twin on the
composer side. It is the more dangerous of the two, because it looks
reasonable and it does not appear in the serialized USF where a schema
review would find it.

A composer that **identifies the originating engine from USF content
and dispatches to that engine's 6502 implementation** is doing the
same thing as a `vibratoKind: int` field. The integer is replaced by
a tuple of "features only engine X uses"; the engine pointer is
replaced by `if discriminator: emit_engineX_bytes()`; the engine
library is the set of `_emit_engineX_*` routines reachable from those
branches. Moving the leak from the schema into Python does not unleak
it.

The cover story is "feature-parametric dispatch": the discriminator
claims to be reading *which features the music uses*, not *which
engine produced it*. The cover story collapses whenever there is only
one consumer of the feature combination — when "USF has vibrato +
multi-pattern orderlist + SFX" routes uniformly to "emit engine X's
bytes," the discriminator is engine identification and the routing
target is an engine-library lookup, regardless of what the
discriminator's docstring says.

The test is sharp: **does the composer's choice of which 6502 to
emit depend on USF content?** If yes, the composer has an engine
library indexed by content sniffing.

Why this is fatal in exactly the way §7's schema leak is:

The audible character of a tune is not only notes and instrument
parameters. It is also choices like the exact per-frame write order,
hard-restart timing, PWM-bound handling, arpeggio phase semantics.
When the composer recognises "this USF is engine-X-shape" and emits
engine X's exact 6502, those audible-character choices come from the
composer's hidden engine library, not from the USF. The USF was
incomplete; the composer silently completed it.

The ML consequence is the one the schema-level rule was meant to
prevent. **The musical knowledge the model needs to generate
audio-faithful music does not exist in the training data.** It exists
in the composer's engine-library Python. A model trained on this
corpus can only produce audio-faithful music by accidentally
producing USFs that match one of the composer's recognised engine
shapes; it has no path to learn the audible-character choices,
because those choices were never in USF for the model to see.

**The rule, stated to bind both sides:** there is one composer. It
is engine-blind. It reads USF as the complete specification of the
music and synthesises one 6502 implementation that produces the audio
that specification describes. If the composer needs information it
does not find in USF to produce correct audio, the missing
information goes into USF as named musical content — never into a
per-engine emitter selected by sniffing.

A new engine migration that ends in "we needed engine X's exact
bytes to match, so we added an engine-X emitter path" has the same
status as a schema PR that ends in "we needed to distinguish twelve
vibratos, so we added a `vibratoKind: int`." It is the failure mode
in a different disguise. The right outcome is either (a) USF grew a
musically-named field that carries the previously-missing content
and the universal composer uses that field, or (b) the universal
composer grew a parametric feature that USF uses — and no engine
identity entered the rebuild path.

### The one exception — `origin_engine`, a Move-1 scaffold

Stated here because a canon document that quietly contradicts practice
is worse than no document: today there is not yet ONE composer. There
are several per-family composers, and the dispatch between them lives
outside the USF, in whichever caller knows the member's family. A
handful of originals pack players from DIFFERENT families behind a
per-subtune dispatch wrapper, and no single composer can build them.

For those files only, each subtune may name its engine
(`MusicSubtune.origin_engine`). The boundary is mechanical:

> permitted EXACTLY when one file demonstrably requires more than one
> COMPOSER — never merely because it contains more than one engine.

5 Title Tunes is the bar. It packs five fully independent Hubbard '85
sub-engines, each with its own init, play, freq table, instruments and
patterns — and it carries no such field, because one composer serves
all five through per-subtune `params`. The unified build is 38% the
size of the compound one. Same-family plurality is a parameterization
problem and has a parametric answer; try it first.

Three constraints keep this from becoming the §8 leak it resembles:

1. **File or subtune level only.** Never inside an instrument or an
   effect. That distinction is not stylistic: this field is deleted BY
   Move 1 — with one engine-blind composer, "requires more than one
   composer" is false for every file, so the construct cannot outlive
   the unification even by neglect. A per-instrument engine `kind` is
   NOT deleted by Move 1, which unifies composers, not representations;
   it would survive as permanent damage to the effect space (§7).
2. **Read by the dispatcher, never by an emitter.** The moment a
   composer branches on it to decide what to EMIT, this is §8 again in
   full. It selects which composer runs; it never shapes that
   composer's output.
3. **Self-policing in the schema.** `src/usf/validate.py` refuses the
   field unless every music subtune names one AND at least two distinct
   values appear — a file whose subtunes all agree needs one composer
   and the tag states nothing.

It is a scaffold with a demolition date, not a softening of §8. The
prohibition above stands unchanged for every other use.

---

## 9. The four tests — the ML-readiness gate

So that "is this representation good?" is checkable rather than hoped,
four falsifiable tests. Together they are the ML-readiness gate for any
effect representation.

1. **Completeness.** Every real instance of the effect round-trips:
   `parameters → engine → the exact instruction stream`. `verify_all`
   running each engine's full subtune set is precisely this proof for
   the engines on the principled path — it demonstrates the parameter
   set is expressive *enough* for them.

2. **No escape hatch.** Two surfaces to check, both must be clean.
   *Schema:* no field in the serialized USF acts as an engine-library
   index. A grep for the obvious shapes (`*Kind: int`, `*Ptr`,
   `*_idx: int`) catches the most blatant slips; cross-engine
   cardinality analysis (group field values by engine, flag fields
   with disjoint value sets per engine) catches more; the final layer
   is human schema review, since a field can be named musically and
   still smuggle engine-defined values. *Composer (see §8):* no
   branch on USF content selects which 6502 implementation to emit.
   Discriminator functions named `_needs_<engine>_path` or
   `_emit_<engine>_*` routine families reachable only through
   engine-discriminating branches are the obvious shapes to grep for;
   the structural test is whether the composer is one universal
   engine or a library indexed by content sniffing.

3. **Interpolation sanity.** Take two real instances of the effect,
   average their parameters, and render or imagine. The result should
   be a plausible instance — interpolation along truly parametric
   fields produces sensible musical intermediates. The test is
   judgmental for purely integer parameters (averaging+rounding is
   meaningful but not unique) and undefined for genuine categoricals
   (averaging `triangle` and `square` doesn't give `quadrangle`). It
   bites hardest when you can't even *describe* what the interpolated
   point would mean musically — then the basis isn't parametric and
   must be refactored.

4. **Cross-engine reuse.** When another engine is migrated, its
   instances of the effect must land as points in the *same* parameter
   space. New *musical* parameters appearing is expected and healthy.
   New *opaque kinds* appearing means the basis was overfit to one
   engine and has failed.

---

## 10. The honest caveat

Any specific parameter set is provisional. Each parameter set is
reverse-engineered to be sufficient for the engines migrated so far
and proven so by the round-trip verification of those engines. New
engines will probably require these sets to grow.

The rule for growth is the whole of this document compressed to one
line: **a parameter set may grow along the musical axis — a new shape,
a new ramp control, a new modulation source that is genuinely a
different musical behavior — and it must never grow along the kind
axis.** Growth in musical parameters is the representation getting
richer. Growth in opaque kinds is the representation getting the
disease.

---

## Provenance

This principle was not decreed; it was stress-tested into existence. It
emerged when the project owner pushed back on a glib example —
`vibrato{depth:3}` — and asked directly whether many different vibrato
*implementations* would be better kept in the engine behind references
than written as definitions in USF. Examining that question honestly
produced this document. The provenance matters: the principle survived
a direct, well-aimed challenge, and that challenge is the reason it is
sharp. When in doubt about an effect representation, re-run that
challenge — it is the test that found the principle, and it will find
the next mistake too.

§8 was added later, after the composer-side analog of the schema leak
kept re-emerging across sessions. Each time it surfaced, the easy
escape was to read §7 narrowly as "the principle is about the
serialized USF, not the composer." That narrowing is the failure mode
§8 closes. The same challenge that produced §7 produces §8: if the
composer needs to recognise the originating engine to produce correct
audio, the USF was not the complete specification — close the gap on
the USF side, not by adding an engine-X emitter path.
