---
name: reference_tokenization
description: "When we get to ML training, the USF needs to be tokenized for transformer-family models. REMI-style is the proven starting point; we may need multiple tokenizers."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

USF is NOT itself a token sequence. USF is a structured representation;
tokenization is a downstream conversion. Different models will likely
need different tokenizers — REMI-style works for transformer-family
models; diffusion/VAE models may not need tokens at all.

## Why this is on the project's path

Limited training data (a few thousand HVSC SIDs) means the model
needs every inductive bias we can give it. A bad tokenizer can erase
the parametric structure we worked to build into USF. A good
tokenizer preserves it.

## REMI (REvamped MIDI-derived events) — the proven starting point

REMI is a tokenization scheme from the music ML literature for
generating polyphonic music with transformers. It was introduced in
"Pop Music Transformer" (Huang & Yang, 2020). Compared to earlier
schemes (MIDI-like, MuseNet), REMI:

- **Position-relative time tokens**: instead of "wait 240 ticks",
  REMI uses "this event is at beat 1 of bar 3 at subdivision 2".
  Gives the model a metric structure for free, like our parametric
  fields give it musical structure for free.

- **Structured event tokens**: `Note-On`, `Note-Duration`,
  `Velocity`, `Bar`, `Position-1/16`. Each event is a small set of
  tokens with clear semantics, not opaque indices.

- **Hierarchical positioning**: `Bar` → `Position` → `Note`. The
  model learns musical hierarchy directly from the token shape.

- **Compatible with conditioning**: you can prepend tokens like
  `Genre-Pop`, `Mood-Sad` if your corpus carries those labels.

REMI's relevance to USF: the same design philosophy. Don't tokenize
USF flatly as text characters; tokenize each USF field as a small,
musically-meaningful event vocabulary. `instrument 5` becomes
`<Instrument><5>`; `C-5 4 i:lead` becomes `<Note><C5><Dur4><InstLead>`
or similar. Parametric values stay parametric.

## Other tokenization families to consider

- **OctupleMIDI** — 8-tuple per note (pitch, dur, vel, instr, bar,
  pos, time-sig, tempo). Less flexible than REMI but lower token
  count.
- **CP-Word** (Compound Word) — REMI-style but groups related
  tokens into compound tokens. Better for transformer attention
  budget.
- **MMM-style** (Multi-track Music Machine) — per-track tokens for
  polyphonic. Probably overkill for SID's 3 voices.

## When this matters

Not yet. The tokenizer comes AFTER the USF corpus is built. The USF
schema needs to be tokenize-friendly NOW (which it mostly is —
discrete fields, low-cardinality categories, parametric integers),
but the actual tokenizer is built when we start training. Multiple
tokenizers in parallel is fine — each trained model gets the
tokenizer that suits it best.

## The non-negotiable

Whatever tokenizer we eventually use must preserve the parametric
structure. A tokenizer that turns `depth=3` into character tokens
`['d','e','p','t','h','=','3']` undoes the principle's work. The
tokenizer's vocabulary should make `depth=3` and `depth=4` adjacent
embeddings, not arbitrary symbols.

## How to apply

When the ML training workstream starts:
1. Pick a model architecture (transformer most likely first).
2. Write a USF → token converter tailored to that architecture.
3. Verify round-trip: parsed USF → tokens → reconstructed USF identical.
4. Train.
5. If another model architecture is tried later (diffusion, VAE),
   write a separate tokenizer/encoder; don't try to share.
