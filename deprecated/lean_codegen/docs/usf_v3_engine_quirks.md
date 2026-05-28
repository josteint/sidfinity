# USF v3.x — Engine quirks as DATA

## Why this exists

The v3 design doc says engine quirks should be resolved by the decompiler into
"portable USF". In practice some quirks (Hubbard's hub_off counter, dynamic
T[100..107,116] aliasing) are too engine-specific to fully musicalize without
losing audio fidelity. We need a hard round-trip:

    SID → USF (JSON) → SID' such that audio(SID') == audio(SID)

That's a non-negotiable constraint (NN training pipeline depends on it).

So engine quirks become **data inside USF**, not hardcoded behavior in the
codegen. The codegen reads the data and emits 6502 mechanically. USF stays
JSON-serializable; one universal player handles all engines.

## Principles

1. **One codegen, many engines.** The Lean codegen has zero engine-specific
   branches. All differences come from data in the USFSong.

2. **Music vs quirks separation.** The "music" layer (notes, instruments,
   patterns, effects-at-intent-level) is the same shape for every engine —
   that's what the NN learns from.

3. **Quirks as a small DSL.** Per-voice scratch bytes, simple update programs
   on note-load and pattern-end, dynamic freq-table feeds with explicit timing
   phases. No turing-complete extension; just enough to cover Hubbard, GT2,
   JCH, DMC etc.

4. **Quirks travel with the song.** A Commando USFSong carries its own quirks.
   So does a Monty USFSong (similar quirks because same engine). So does a
   GT2-extracted USFSong (different quirks). The codegen doesn't need to know
   which engine the song came from.

## Schema additions to USFSong

```lean
structure USFSong where
  -- ... existing fields (freqTable, instruments, voices, patterns, ...) ...
  engineQuirks : USFEngineQuirks := {}        -- empty default = no quirks
```

```lean
structure USFEngineQuirks where
  -- Per-voice scratch bytes (in addition to the always-present v_pitch, v_inst,
  -- v_ctrl, etc.). Each entry adds a per-voice byte slot.
  voiceScratch : List USFVoiceScratch := []

  -- Operations on voice scratch bytes triggered at note-load
  noteLoadOps  : List USFNoteLoadOp := []

  -- Operations triggered at pattern-end ($00 marker reached in pattern data)
  patternEndOps : List USFPatternEndOp := []

  -- Dynamic freq-table feeds
  dynamicFreqEntries : List USFDynamicFreqEntry := []

  -- Should the pattern-data inst byte preserve its top 2 flag bits (used by
  -- noteLoadOps via flag-conditional increments)?
  preserveNoteFlags : Bool := false


structure USFVoiceScratch where
  name    : String           -- documentation only ("hub_off", "seq_idx", ...)
  initial : USFByte := 0     -- value at song-init


inductive USFNoteLoadOp where
  -- On every note_load, add `delta` to v_scratch[voice][slot].
  | addConst    : (slot : Nat) → (delta : USFByte) → USFNoteLoadOp
  -- On note_load, examine the note's raw inst-byte flag bits and add
  -- a flag-dependent delta. List of (flag_mask, flag_value, delta);
  -- first match wins.
  | addByFlag   : (slot : Nat) → List (USFByte × USFByte × USFByte) → USFNoteLoadOp
  -- On note_load, set v_scratch[voice][slot] to a constant.
  | setConst    : (slot : Nat) → (value : USFByte) → USFNoteLoadOp
  -- AFTER note_load (and pattern-pointer advance), peek the next pitch byte;
  -- if it's the end-of-pattern marker ($00), reset slot eagerly (das_model
  -- v2nd1 behavior). Distinct from patternEndOps because it fires DURING the
  -- last note's load, not at the next note_load that walks past the marker.
  | resetIfNextEnds  : (slot : Nat) → USFNoteLoadOp
  | incIfNextEnds    : (slot : Nat) → (delta : USFByte) → USFNoteLoadOp


inductive USFPatternEndOp where
  -- Triggered at advance_order time (when a note_load encounters the $00
  -- end-of-pattern marker as the pitch byte).
  | reset     : (slot : Nat) → USFPatternEndOp
  | increment : (slot : Nat) → (delta : USFByte) → USFPatternEndOp


structure USFDynamicFreqEntry where
  freqSlot   : Nat                  -- index into freq table to write
  loSource   : USFDynRef
  hiSource   : USFDynRef
  phase      : USFUpdatePhase

inductive USFDynRef where
  | constant   : USFByte → USFDynRef
  | scratch    : (voice : Fin 3) → (slot : Nat) → USFDynRef
  | voiceCtrl  : Fin 3 → USFDynRef
  | voicePitch : Fin 3 → USFDynRef
  | voiceInst  : Fin 3 → USFDynRef
                              -- v_inst[voice] at the time of this update phase.
                              -- Reads "current inst" if voice has loaded this
                              -- frame, else reads previous-frame inst (= what
                              -- das_model calls "prev_inst" at the right phase).

inductive USFUpdatePhase where
  | atFrameStart                     -- before any voice processes
  | beforeVoice : Fin 3 → USFUpdatePhase
                                     -- right before voice N's exec runs this frame
                                     -- (= das_model's "between V_prev and V_N")
```

## Worked example: Commando

```lean
engineQuirks := {
  preserveNoteFlags := true   -- hub_off increment depends on bits 6/7

  voiceScratch := [
    { name := "hub_off", initial := 0 },   -- slot 0
    { name := "seq_idx", initial := 0 }    -- slot 1
  ]

  noteLoadOps := [
    -- hub_off: bit 6 → +1, bit 7 → +2, neither → +3
    .addByFlag 0 [
      (0x40, 0x40, 1),
      (0x80, 0x80, 2),
      (0x00, 0x00, 3)
    ],
    -- Eager reset of hub_off when this is the last note in the pattern
    .resetIfNextEnds 0
  ]

  patternEndOps := [
    .reset 0,            -- hub_off = 0 on pattern end (also covered by resetIfNextEnds usually)
    .increment 1 1       -- seq_idx += 1 on pattern end (das_model `inc $C6`)
  ]

  dynamicFreqEntries := [
    -- T[100]: V2.hub_off (lo), V3.hub_off (hi). Updated twice — at frame
    -- start (so V3 sees previous values) and again before V1 runs (so V1
    -- sees post-V2 update).
    { freqSlot := 100,
      loSource := .scratch 1 0,
      hiSource := .scratch 2 0,
      phase    := .atFrameStart }
    { freqSlot := 100,
      loSource := .scratch 1 0,
      hiSource := .scratch 2 0,
      phase    := .beforeVoice 0 }

    -- T[104]: V1.ctrl (lo), V2.ctrl (hi). Hubbard's percussion noise feed.
    -- Replaces our pitch-104 special case.
    { freqSlot := 104,
      loSource := .voiceCtrl 0,
      hiSource := .voiceCtrl 1,
      phase    := .atFrameStart }
    { freqSlot := 104,
      loSource := .voiceCtrl 0,
      hiSource := .voiceCtrl 1,
      phase    := .beforeVoice 0 }

    -- T[98]: V1.seq_idx, V2.seq_idx. Updated between V3 and V2.
    { freqSlot := 98,
      loSource := .scratch 0 1,
      hiSource := .scratch 1 1,
      phase    := .beforeVoice 1 }

    -- T[99]: V3.seq_idx (lo), V1.huboff (hi).
    { freqSlot := 99,
      loSource := .scratch 2 1,
      hiSource := .scratch 0 0,
      phase    := .beforeVoice 1 }

    -- T[105]: V3.ctrl (lo), V1.pitch (hi).
    { freqSlot := 105,
      loSource := .voiceCtrl 2,
      hiSource := .voicePitch 0,
      phase    := .beforeVoice 1 }

    -- T[106]: V2.pitch (lo), V3.pitch (hi).
    { freqSlot := 106,
      loSource := .voicePitch 1,
      hiSource := .voicePitch 2,
      phase    := .beforeVoice 1 }

    -- T[107]: V1.inst (lo), V2.inst (hi). At the inter-voice phase, V1's
    -- v_inst is its previous frame's value (since V1 hasn't loaded yet);
    -- V2's v_inst is its current frame's value (since V2 just loaded if it
    -- did this frame). Matches das_model $8E/$A2 semantics.
    { freqSlot := 107,
      loSource := .voiceInst 0,
      hiSource := .voiceInst 1,
      phase    := .beforeVoice 1 }

    -- T[116]: V1.huboff (lo), V2.huboff (hi).
    --   (Note: das_model uses pw_dir bytes here, but for Commando these
    --   coincide with hub_off positions; keeping it as scratch references is
    --   cleaner.)
    { freqSlot := 116,
      loSource := .scratch 0 0,
      hiSource := .scratch 1 0,
      phase    := .atFrameStart }
  ]
}
```

## How the codegen consumes this

1. **Voice state allocation.** For each `voiceScratch` entry, allocate 3 bytes
   in voice-state RAM (one per voice). Init to `initial`.

2. **Note-load patch.** After reading the inst byte (raw, with flag bits
   preserved if `preserveNoteFlags`), iterate `noteLoadOps` and emit the
   corresponding 6502 sequence (compare-mask-and-add or set).

3. **Pattern-end patch.** In the orderlist-advance routine, zero each scratch
   slot listed in `patternEndResets`.

4. **Dynamic freq updates.** In the play() routine, group `dynamicFreqEntries`
   by `phase` and emit copy-from-source-to-freq-table-slot at each phase point
   (frame start, between voice N-1 and voice N).

5. **Pitch-104 special case** is REMOVED from the codegen. The decompiler will
   instead emit a `USFDynamicFreqEntry { freqSlot := 104, loSource := voiceCtrl
   N, hiSource := voiceCtrl M, phase := atFrameStart }` (Hubbard's T[104] is
   actually fed from V1.ctrl and V2.ctrl per das_model). Then `.percussion
   .dynamicCtrl` notes simply reference `pitch=104` and the freq table
   provides the dynamic value.

## How the NN consumes this

The music layer (notes, instruments, patterns) is consistent across all songs
of all engines — the NN's primary input.

The `engineQuirks` field carries the engine-level quirks. Two strategies:

- **Per-engine quirks fixed.** During training, group songs by source engine.
  The quirks are then a property of the engine class, not the song; the NN
  generates only the music layer for songs of class C, and the quirks of
  class C are looked up at synthesis time. Simple.

- **Quirks part of the generative target.** The NN generates the
  `engineQuirks` field too, perhaps constrained to a learned vocabulary of
  quirk-sets. Lets the NN learn cross-engine patterns.

Either strategy keeps USF as a single self-describing format.

## Constraints / non-goals

- This DSL is intentionally **not turing-complete**. If a song needs more
  complex per-frame computation (digi, demo SIDs), it doesn't fit here and
  needs a different USF extension (sample stream, raw write log).
- This DSL handles **frame-granular tracker engines**. Cycle-precise tricks
  are out of scope.
- The DSL is "engine-agnostic in structure, engine-specific in content". A
  single USF can express any engine's quirks, but no single song will use
  every quirk.

## Migration plan

1. Define the new types in `USFv3.lean`.
2. Add `engineQuirks` field to `USFSong` with empty default (preserves
   existing songs that don't need quirks).
3. Update `gen_commando_v3.py` to populate `engineQuirks` for Commando
   (currently-hardcoded hub_off + T[100] behavior moves into data).
4. Refactor `CodegenV3.lean` to be data-driven for the quirks. Existing
   hardcoded T[100] and hub_off code is replaced by a dispatcher that reads
   `engineQuirks` and emits.
5. Verify Commando audio match is the SAME as before the refactor
   (~64% per-frame, same WAV).
6. Add the next dynamic freq entry (T[104] or T[116]) by editing data only —
   no codegen changes needed. This is the test that the DSL is well-formed.
7. Iterate.
