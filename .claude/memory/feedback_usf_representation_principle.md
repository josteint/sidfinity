---
name: feedback_usf_representation_principle
description: "Before designing or changing any USF effect/instrument representation, read docs/usf_representation_principle.md IN FULL."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

There is a load-bearing design principle governing how USF must
represent instruments and effects so the result is good ML training
data. It lives in **`docs/usf_representation_principle.md`**.

**Before designing or changing any USF instrument/effect representation
— read that document IN FULL. Do not act on a summary of it, including
this one.**

This memory is deliberately a tripwire, not a container. The principle
is a multi-step argument (two failure modes, a structured resolution,
two discipline rules, four falsifiable tests); its persuasive force is
its *shape*, and a summary destroys the shape — it leaves a slogan that
can be nodded at without being understood. The depth is in the doc, on
purpose. Open the doc.

The one-line trigger to recognise the situation: any time you are about
to add a field like `somethingKind: int` or a `*Ptr`, or to "put the
variants in the engine and reference them" — stop, that is the exact
mistake the doc exists to prevent.

**Why:** the project owner identified that compressing this into a
sparse memory would let its depth fade. Correct. The doc carries the
depth; this memory only guarantees the doc gets opened.

**How to apply:** treat the doc as binding for every effect-representation
decision in [[project_usf_refactor]] Phases 6–7. Related: the engine
holds *mechanism*, never an indexed library — the sibling of
[[feedback_deconstruct_not_reproduce]] (reproduce the behaviour with
clean code; discard the space-saving mechanism).
