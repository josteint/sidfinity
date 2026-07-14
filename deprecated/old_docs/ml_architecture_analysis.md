# ML Architecture Analysis: Generating SID Music from USF

**Date:** 2026-04-29
**Status:** Proposal — not yet implemented

## Context and Constraints

The training corpus is ~5,000 Grade A USF songs derived from GT2, Hubbard, JCH, and DMC
pipelines. USF is already designed as a tokenization target (compact, event-based, ~300-token
vocabulary, ~2,000-4,000 tokens per song). Key structural facts from experiment 9 (information
theory):

- Per-token entropy: 5.67 bits (healthy for a ~300-token vocabulary at 7.2 bits max)
- Rest tokens: 42% of the stream (dominant, compressible)
- Voice mutual information: 31% (the three SID voices are correlated — a joint model can exploit this)
- USF gzip is 12% smaller than SID gzip — USF is structurally efficient

These numbers shape every architecture decision below.

---

## Architecture Candidates

### 1. Transformer (GPT-style decoder-only)

**How it works:** Linearize the full USF token stream, train a causal LM to predict the next
token. Generate by sampling autoregressively.

**Strengths for USF:**
- USF already has a grammar with ~300 tokens — maps cleanly to a fixed vocabulary
- Transformers handle long-range dependencies (instrument definition → later pattern usage)
- 5,000 songs x ~3,000 tokens = ~15M tokens: enough for a small model (125M–350M params)
- Simplest to implement; the most-validated architecture for symbolic music (e.g., Music Transformer)

**Weaknesses:**
- Flat sequence ignores the two-level hierarchy: instrument programs vs. score events
- Voice coherence emerges from the flat sequence order; three voices must be written
  in interleaved or concatenated form, both of which hide their relationship from attention
- No built-in validity guarantee: the model can emit malformed tokens (e.g., a note number
  outside 0-95, or a wave table step with an illegal waveform byte)
- Context length: a 4,000-token song at 4k context is at the edge; 8k safe

**Verdict:** Strong baseline. Likely the right first model because of training simplicity. Use
with a constrained vocabulary and grammar-aware decoding to reduce invalid output.

---

### 2. VAE (Variational Autoencoder)

**How it works:** Encoder maps USF → latent vector z; decoder maps z → USF. Sample z from
N(0,I) to generate new songs. The latent space enables interpolation ("blend these two styles").

**Strengths:**
- Continuous latent space enables style transfer and interpolation
- Encoder forces the model to compress the song into a semantically meaningful representation
- Lower inference cost once trained (decode in one pass)

**Weaknesses:**
- Sequential VAEs for music (MusicVAE style) require a hierarchical design; flat VAEs
  produce "average soup" because the KL term encourages posterior collapse
- 5,000 training examples is marginal for a VAE — the encoder needs enough songs to learn
  a smooth manifold; below ~10k examples the space becomes holey
- The SID constraint (≤64KB output, valid register sequences) is hard to enforce in a latent
  space; generated songs may be syntactically invalid more often than the GPT approach
- Reconstruction loss on token sequences requires careful weighting: a missed instrument
  program definition is catastrophically worse than a wrong note duration

**Verdict:** Useful as a second model for style control and interpolation, but not the first
model to train. Revisit once the GPT baseline proves the tokenization works.

---

### 3. Diffusion (discrete or continuous)

**How it works:** Either continuous diffusion over dense token embeddings (analog of audio
diffusion), or discrete diffusion (MDLM, D3PM) directly on token sequences.

**Strengths:**
- Iterative denoising can improve global coherence (unlike left-to-right generation)
- Conditioning on partial sequences is natural: denoise with a fixed prefix (style seed)

**Weaknesses:**
- Discrete diffusion on symbolic sequences is computationally expensive to train and slower
  at inference than autoregressive sampling
- The field is less mature for discrete symbolic music than for audio waveforms
- 5,000 training examples is insufficient for diffusion models, which typically need
  100k+ to learn a useful noise schedule
- The score at the USF level is sparse (42% rests) — diffusion noise corrupts rests and
  notes equally, but they have very different semantic weights

**Verdict:** Not recommended at this corpus size. Revisit at 50k+ training songs (after
extending pipeline to DMC 10k + JCH 3.6k + more engines).

---

### 4. Hierarchical Model

**How it works:** Two-stage generation. Stage 1 generates the song skeleton (instrument
definitions, pattern IDs in the orderlist, global tempo). Stage 2 fills in pattern contents
conditioned on the skeleton.

**Strengths:**
- Matches USF's actual structure: instruments + score are separately defined
- Stage 1 output is tiny (~50-100 tokens), Stage 2 is a separate conditional model per pattern
- Patterns repeat in the orderlist — generating one pattern and reusing it is musically correct
  and matches how human composers write

**Weaknesses:**
- Requires training two models with different input distributions
- Stage 1 quality is the bottleneck: if the skeleton is incoherent (e.g., pattern count does
  not match orderlist length), Stage 2 cannot recover
- Much more engineering complexity than a flat transformer

**Verdict:** The right long-term architecture once the flat transformer baseline establishes
what the data distribution looks like. Implement as Stage 1 = classify song structure,
Stage 2 = fill patterns.

---

### 5. Multi-track with Cross-Attention

**How it works:** Three parallel transformer streams (one per SID voice), with cross-attention
between streams so each voice can attend to the other two.

**Strengths:**
- Directly models the 31% voice mutual information measured in experiment 9
- Each voice has its own orderlist, so separate streams are structurally natural
- Bass line + melody + arp is the canonical C64 three-voice arrangement — models that
  "know" which stream is which can learn role-specific patterns

**Weaknesses:**
- Requires synchronizing the three streams at bar/pattern boundaries — non-trivial for
  variable-duration events
- USF orderlists already capture cross-voice structure: patterns are reused globally,
  not per-voice. A multi-stream model must handle shared patterns correctly
- 3x memory cost at training and inference

**Verdict:** Strong improvement over a flat transformer once corpus size justifies it.
Implement as a modification to the flat model: process orderlists as voice-tagged tokens,
add a cross-voice attention layer between pattern boundaries.

---

## Recommended Architecture: Staged Deployment

### Phase 1 (now — ~5,000 training songs): Flat GPT-style Transformer

**Model size:** 125M parameters. GPT-2 small as reference point.

**Tokenization:** USF text token stream after USF normalization (experiment 5 rewrite rules):
1. Duration merging: consecutive rests → one rest with summed duration
2. Instrument dedup: merge instruments with identical (AD, SR, waveform, wave_table)
3. Pattern dedup: merge identical event sequences
4. Transpose normalization: inline transposes into note values

This reduces tokens by ~22% and lowers per-token entropy. Apply before ALL tokenization.

**Token vocabulary:** The USF grammar defines ~300 tokens. Add:
- `<BOS>` / `<EOS>` — begin/end song
- `<VOICE_SEP>` — boundary between voice orderlists (helps attention find structure)
- `<PAT_SEP>` — boundary between patterns (the most important structural boundary)

Total vocabulary: ~310 tokens. At 5.67 bits entropy, the model needs to predict ~2.9 bits of
new information per token on average (entropy of a uniform 310-token distribution = 8.3 bits;
the real distribution is concentrated, so perplexity target is ~12-15).

**Context window:** 4,096 tokens. Covers a full song (max ~4,000 tokens post-normalization)
with room for a prompt prefix (conditioning).

**Ordering within the token stream:**

The USF grammar's natural ordering is also the recommended ML ordering:

```
<BOS> SONG header samples? modulation?
  instruments (all, in definition order)
  speed_table?
  patterns (all, in ID order, with PAT_SEP between each)
  orderlists (ORD V1 ... /V1 V2 ... /V2 V3 ... /V3 /ORD)
<EOS>
```

Rationale: instruments are defined before patterns that reference them, orderlists are last
(they are short and reference pattern IDs already seen). This ordering has no forward
references, making causal prediction valid everywhere.

**Training objective:** Standard cross-entropy on next token. No special loss.

**Validity enforcement:** At inference, use grammar-constrained decoding (top-k + grammar
mask). The USF grammar is regular/context-free at the token level — a lightweight finite
automaton over the grammar states can mask illegal next tokens. This eliminates the most
common failure mode (generating a pattern command with an out-of-range parameter).

---

### Phase 2 (50k+ songs): Hierarchical Two-Stage Model

Stage 1 — Structure model (small, ~30M params):
- Input: conditioning tokens (style, tempo, SID model, target length in patterns)
- Output: instrument definitions + orderlist skeleton (pattern IDs, transposes, restart points)
- This is a ~300-token sequence, trivially trainable

Stage 2 — Pattern fill model (medium, ~125M params):
- Input: instrument definitions (already generated) + pattern ID + voice context
- Output: the event sequence for one pattern
- Run once per unique pattern, then the orderlist assembles them into the full song

Advantage: Stage 2 can share patterns across songs that use the same instruments and style,
which matches how real composers work.

---

### Phase 3 (optional, 200k+ songs): Voice-aware Multi-track Model

Extend Phase 1 with:
- Voice-ID embedding (0/1/2) added to each token's position embedding
- Cross-attention at pattern boundaries between the three voice streams
- Conditioning on "voice role" (bass / melody / arp) detected by a classifier trained on the
  corpus

At this scale (if DMC + JCH + Music Assembler + Future Composer pipelines are complete),
voice mutual information can be explicitly modeled.

---

## Training Data Pipeline

### Step 1: Export all Grade A USF songs

```python
# Pseudocode
from gt2_to_usf import gt2_to_usf
from usf_normalizer import normalize  # experiment 5 rewrite rules

songs = []
for sid_path in grade_a_songs:
    song = gt2_to_usf(sid_path)
    song = normalize(song)
    songs.append(song)
```

Current count: ~5,000 Grade A songs (GT2: 4,968, Hubbard: 77, JCH: 107).

### Step 2: Tokenize

Use `usf_tokens.py` tokenizer. Emit the full USF token stream per song with BOS/EOS.

Verify token length distribution: median, 90th percentile, max. If max >> 4096 tokens,
either raise context window or truncate at pattern boundaries (never mid-pattern).

### Step 3: Quality filter

Exclude songs where:
- Token count < 100 (trivial jingles, likely degenerate USF)
- More than 5 consecutive identical patterns in the orderlist (stuck-loop artifact)
- All three voices use the same instrument (copy-paste instrument definition bug)

### Step 4: Train/val/test split

80% / 10% / 10% split by song (not by token). No data augmentation at this stage —
the corpus is small enough that we need every real song in training.

Optional augmentation once baseline is established:
- Transpose entire song by ±1, ±2, ±3 semitones (modifies note values in patterns, not
  freq table or instruments — valid because USF notes are relative to the freq table)
- Tempo perturbation: multiply all durations by 2/3 or 3/2 (changes song tempo, valid)

These two augmentations can 7x the effective dataset size.

### Step 5: Train

Recommended hyperparameters for 125M GPT-2-like model on 5k songs:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Layers | 12 | Standard GPT-2 small |
| Heads | 12 | Standard |
| d_model | 768 | Standard |
| d_ff | 3072 | Standard |
| Context | 4096 | Covers one full song |
| Batch size | 32 songs | Limited by GPU VRAM |
| Learning rate | 3e-4 | With cosine decay |
| Warmup | 500 steps | |
| Epochs | 100 | Small corpus; overfit slightly then stop |
| Dropout | 0.1 | Regularization |
| Weight decay | 0.1 | AdamW |

With dual 3090s (24GB each), a 125M model at batch 32 x 4096 tokens fits comfortably.
Training time: ~2 hours per 100 epochs on the full 5k-song corpus.

### Step 6: Evaluate

Primary metric: **perplexity on the held-out test set.** Target < 15.

Secondary metrics:
- **Validity rate:** What fraction of generated songs can be compiled through usf_to_sid
  without error? Target > 80% with grammar-constrained decoding.
- **Playability rate:** Of valid compilations, what fraction produce a non-silent SID file?
  Target > 95% (silence means the model generated all-zero instruments or empty orderlists).
- **Audio quality:** Run the generated SIDs through `audio_compare.py` against the nearest
  training song (by token similarity). This is not a training signal — it is a sanity check
  that the output is in the right ballpark of C64 sound.
- **Grade A analog:** Run generated SIDs through the compare pipeline against the closest
  training song. A "Grade C" output (< 10% audible error) means the model is reproducing
  training data, which is actually bad here — we want generation, not memorization.

There is no clean "sounds good" loss function at the USF level. The field-standard approach
is to use a pretrained audio encoder (e.g., CLAP, EnCodec) to embed both generated and
reference audio, then measure cosine similarity in embedding space. For C64 audio this
requires a C64-specific fine-tuned audio encoder, which we do not have. Use listening tests
and playability rate as proxies for now.

---

## What Loss Function Captures "Sounds Good"?

Short answer: there is no such loss function at the symbolic level.

Longer answer: at the USF level, the "sounds good" property is a function of:
1. Valid SID register sequences (hard constraint — enforced by grammar-constrained decoding)
2. Harmonic coherence between voices (soft constraint — emerges from training data statistics)
3. Idiomatic C64 timbre (hard restart timing, pulse modulation, filter sweeps — emerges from
   instrument programs in the training data)
4. Rhythmic feel (duty cycle of notes vs. rests — emerges from duration statistics)

The cross-entropy loss on the USF token stream implicitly optimizes all four: if the model
predicts the next token correctly, it must have learned what instruments look like, what note
sequences co-occur with them, and how voices interact. This is the standard symbolic music
argument for why language modeling is a valid proxy.

Do NOT add an audio reconstruction loss to the USF model. This requires:
1. Compiling every generated USF to a SID (xa65 assembly, ~100ms)
2. Rendering the SID to audio (libsidplayfp, ~2s)
3. Computing a differentiable audio similarity score

That loop is non-differentiable at the assembly step and prohibitively slow for a training
loop. It belongs in offline evaluation, not the training objective.

---

## Handling the ≤64KB SID Constraint

A SID file must fit in 64KB of Commodore 64 RAM. The current V2 codegen produces player
code + data that is well under this limit for the training corpus (the largest GT2 songs are
~8KB). The constraint is not a training-time concern.

At inference time, if the model generates an unusually long orderlist or many unique patterns,
the compiled SID may exceed 64KB. Mitigation:
1. Apply pattern dedup (experiment 5 rewrite rule 3) before compiling
2. If still over 64KB, truncate the orderlist at the restart point (the song already loops;
   truncation just makes it shorter)
3. Log a warning — this is a rare edge case in the training distribution

---

## Instruments: Learned or Specified?

The model should LEARN instrument definitions from the training data. Here is why:

- Instruments in the training corpus have rich structure (AD, SR, wave table programs, pulse
  modulation, filter programs). The model must learn what a "bass drum" instrument looks like
  vs. a "lead melody" instrument.
- The 31% voice mutual information (experiment 9) means instruments and patterns are
  correlated — a bass voice tends to use low-octave notes with specific ADSR profiles.
  Separating instrument learning from score learning discards this correlation.
- If a user wants to specify instruments ("use Rob Hubbard-style instruments"), this is a
  conditioning problem, not a model architecture problem. Condition on a few instrument
  tokens as a prefix, let the model generate the rest.

For style-conditioned generation ("make it sound like Hubbard"):
- Extract instrument fingerprints from Hubbard training songs: ADSR histogram, wave table
  program length distribution, freq_slide usage rate
- Encode these as conditioning tokens prepended to the generation context
- Fine-tune on Hubbard-only songs with a style token `<STYLE:HUBBARD>` prefix

---

## Summary and Priority Order

| Priority | Action | Expected outcome |
|----------|--------|-----------------|
| 1 | Apply USF normalization (experiment 5 rules) to all 5k Grade A songs | -22% tokens, cleaner training signal |
| 2 | Implement grammar-constrained decoding for USF | +30-40pp validity rate at inference |
| 3 | Train 125M GPT-2-style model on normalized USF | Baseline generation; target perplexity < 15 |
| 4 | Evaluate with playability rate + listening tests | Establish quality floor |
| 5 | Augment with transpose ±3 semitones + tempo scaling | 7x effective dataset size |
| 6 | Extend corpus: complete DMC/JCH pipelines (~14k more songs) | Better generalization |
| 7 | Add voice-role conditioning (bass/melody/arp classifier) | More musically structured output |
| 8 | Hierarchical two-stage model at 20k+ songs | Better long-range structure |

The single highest-leverage action before training is USF normalization. Without it, the model
must learn that `I2 C4 d2 . d1` and `I2 C4 . .` are the same event — an unnecessary
learning burden. After normalization they are identical tokens.

The single highest-leverage architectural choice is grammar-constrained decoding. A generated
USF that cannot compile is completely worthless. With a 310-token vocabulary and a well-defined
grammar, building the finite automaton is a one-day implementation task that will eliminate
the most common failure mode.
