# The USF Representation Principle

**Status: load-bearing. Read this document in full before designing or
changing how USF represents any instrument, effect, or behavior. Do not
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
the resulting *modulation* differs audibly or structurally, never when
only the 6502 differs.

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

## 8. The four tests — the ML-readiness gate

So that "is this representation good?" is checkable rather than hoped,
four falsifiable tests. Together they are the ML-readiness gate for any
effect representation.

1. **Completeness.** Every real instance of the effect round-trips:
   `parameters → engine → the exact instruction stream`. (The 100%
   full-song Commando verification is precisely this proof for the
   current effect set — it demonstrates the parameter set is expressive
   *enough*.)

2. **No escape hatch.** A grep of the serialized USF finds no
   `*Kind: int`, no `*Ptr`, no engine-library index field. (This is the
   plan's Phase 7.1, sharpened to a hard gate.)

3. **Interpolation sanity.** Take two real instances of the effect,
   average their parameters, and render. The result must be a plausible
   instance of the effect — not garbage. If averaging two valid points
   produces nonsense, the basis is not musical or not smooth, and it
   must be refactored.

4. **Cross-engine reuse.** When another engine is migrated, its
   instances of the effect must land as points in the *same* parameter
   space. New *musical* parameters appearing is expected and healthy.
   New *opaque kinds* appearing means the basis was overfit to one
   engine and has failed.

---

## 9. The honest caveat

Any specific parameter set is provisional. The current `VibratoSpec`
(and `ArpSpec`, `PwmSpec`, and the rest) was reverse-engineered to be
sufficient *for Commando*, and proven so by the 100% round-trip — but
proven only for Commando. Other engines will probably require these
sets to grow.

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
