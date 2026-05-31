---
name: project_usf2_refactor
description: Current plan — the USF instrument-as-program refactor. Supersedes the das_model_gen/Hubbard-discovery direction. GT2 work is deprecated.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

**Current plan (as of 2026-05-20): the USF instrument-as-program
refactor.** Roadmap is `docs/usf_instrument_program_plan.md` (Phases
0–7, with a tracking table). This SUPERSEDES the older
[[project_hubbard_strategy_2026_05]] (das_model_gen via discovery) and
[[project_pipeline_status]] directions.

Goal: replace USF's typed-field instruments + `engineQuirks` with
per-instrument behavioral programs (register-write events). Success =
the rebuild's `siddump --writelog` stream matches the original
frame-for-frame, register-for-register; .sid byte equality not required.
New schema: `pipelines/commando/codegen/Commando/USF2.lean`.

**GT2 work is deprecated.** User stated 2026-05-20: the previous GT2
pipeline work is no longer relevant. If the USF2 refactor succeeds, the
method will be applied to GT2 fresh. The GT2 regression registry is
empty on this machine — ignore it; don't run/rebuild it.

**Progress:** Phases 0–5 done (commits 5577782 .. 315f2ba). The USF
refactor is COMPLETE for all of Commando's music: the rebuilt SID
reproduces the original 100% over 25000 frames (>2 passes), every
register write, py65 play-call attributed — for ALL THREE music
subtunes (0, 1, 2), packed into one SID (commit d9a2308; `build()`
defaults to subtunes (0,1,2), `init` selects via A). song_interp and
the codegen each match the original 100% and each other 100%.

Commando's PSID header declares **19 subtunes**: 3 music (0/1/2) and
16 SFX (3–18). **ALL 19 are now done** — the codegen packs the whole
SID (commit cb0116a, 7059 bytes, PSID songs=19), every subtune
byte-exact vs the original. The SFX are the `$53A5` sub-engine (a
2-voice register snapshot + a freq-table pitch sweep); reverse-
engineered in `pipelines/commando/extract/sfx.py` (extractor +
`SfxInterp` reference interpreter, all 16 verified) and codegen'd as
`sfx_play`/`sfx_step` with 32-byte `sfxdata` records. `init` dispatches
A<3 -> music, A>=3 -> SFX index A-3. See [[project_commando_no_drum_engine]].
NOTE: `decomp.songs` (the music decompiler) is a COMPACTED list — its
index != PSID subtune number beyond the first 3; the SFX are not in
that table at all.

Subtune 2 needed two fixes (commit 669fee4): a tie note carries the
live pitch across pattern boundaries (decoder defaults it to 0); the
`$FE` orderlist marker is end-of-song (Voice.stop) — the song ends on
the held chord, one-shot gates all voices off, no loop.

**Commando is COMPLETE** — all 19 subtunes (music + SFX) reproduced
byte-exact through USF.

**Note-codec seam (commit 418b88e):** the codegen has a pluggable
`NoteCodec` — `pipelines/commando/codegen/note_codec.py`. A codec owns
only the pattern byte format + the 6502 `load_note` decoder; the
orderlist/effects/SFX/seq_idx stay generic. `build(codec=...)` picks
one; adding a packer = a new class. `BitPackCodec` (the streamable
bit-pack — per-note MSB-first bitstream) is the shipped codec. The
USF itself is NOT touched by the codec — compression is a codegen/SID
concern only; ML trains on the USF, not the SID. Result: the packed
19-subtune SID is **4833 bytes** (original Commando 4165; was 7059
before packing). Convention: pattern byte 0 = note count.

Remaining: phases 6–7 (migrate other Hubbard pipelines to USF2;
ML-readiness).

NOTE: an earlier session claimed "100% complete" off a 1500-frame
check — that was an over-claim (one pass is 11808 frames). Phase 5c
(commits 60cee46..2e5d869) closed the full song: fixed the
instrument-carry-across-patterns desync, the general off-table
arpeggio (state mirror `statebuf`), the drum-slide (per-note
portamento, effect #3), the seq_idx pre-increment, and off-table
vibrato (reads live state, not the static freq table).
Phase 3 built four `pipelines/commando/extract/` modules:
- `inst_program.py` — runs the real Commando binary in py65, hooks
  $D4xx writes, segments into per-instrument NoteOccurrences.
- `inst_generalize.py` — decodes each instrument from its 8-byte table
  row at $5591+inst*8 into USF2 primitives (a pure capture-only
  generalisation cannot work — instruments aren't pure functions of
  pitch/frame). 11/13 decode clean.
- `song_interp.py` — the whole-song USF2 reference interpreter. init
  once, play per frame, all 3 voices, shared instrument state.
  Reproduces Commando subtune 0's ENTIRE melodic engine byte-exact
  (1270/1500 frames; the 230 misses are all inst 4, the drum).
- `emit_usf2.py` → `CommandoInsts2_gen.lean` — the 13 instruments as
  USF2 behavioral-parameter literals (parametric form; supersedes the
  Phase-1 events-list sketch in USF2.lean).

Phase 4: `pipelines/commando/codegen/usf2_codegen.py` — a clean 6502
Commando engine (xa65 assembly, a port of song_interp) + USF2 data
tables → a real `.sid`. Implements the full melodic engine (all four
effect families). Verified 1500/1500 frames vs song_interp; **78.97 %
siddump --writelog match vs the original Commando** — the entire
remaining gap is V2 (the drum) + V1 (inst 7's off-table arp). The
codegen is Python, not Lean (continuing Phase 2.3's Python-first
deviation; Lean Codegen2 deferred to the migration phases).

Phase 5 done (commits 3647892..315f2ba): inst 7's off-table arpeggio
and inst 4 (the "drum" — see [[project_commando_no_drum_engine]]; there
is no drum sub-engine, inst 4 is an off-table instrument). Phase 5c
verified the FULL song and closed every remaining divergence — see the
Progress note above. Key engine facts the full-song work nailed down:
- The instrument number carries across pattern boundaries (engine_model
  resets it per pattern — wrong; carry it at the orderlist level).
- `seq_idx`/`note_idx` are pre-incremented when a pattern's LAST note
  loads (the engine peeks the $FF end marker).
- An off-table lookup (arp idx>=96, note-start pitch>=96, or vibrato
  of an off-table-pitch instrument) overflows the 96-entry freq table
  into LIVE engine state at $54E8+ — the codegen mirrors that region
  into `statebuf` on demand. Static freq-table bytes are NOT a
  substitute (the state is dynamic).
- The drum-slide (per-note portamento, $52B3) is effect #3, between
  PWM and skydive; keyed off the note's drum/porta trigger byte.
Latent bugs surfaced earlier: tie notes write ctrl+pw+ad+sr (not just
ctrl); the hard restart is gated by no_release, not tie.

**Phase 6 — consolidation + per-engine migration (in progress).**
The Hubbard engines are near-clones, so Phase 6 first CONSOLIDATED:
`pipelines/hubbard/` is now a shared Hubbard '85 engine core (types,
inst_program, inst_generalize, inst_interp, note_codec, song_interp,
codegen, config). Each engine is a thin `EngineConfig` at
`pipelines/<engine>/config.py` — no clones. Commando is a config;
verified unchanged. Commits ae181ca, 5a90f28, 93e22b3.

**Phase 6.1 done — Devils Galop migrated, 100% byte-exact** (commit
84908ff). Devils Galop = `pipelines/devils_galop/config.py` + its
engine_model, on the shared core; codegen 20000/20000 byte-exact,
song_interp 100%, Commando still 19/19. Three per-engine deltas, all
config-driven: inc_by2 ramp, the $178B drum-priority gate, vibrato
onset 8 vs 6. The vibrato onset was handled per the representation
principle — `VibratoSpec.onset_dur`, a real per-instrument USF param,
NOT a vibratoKind. See [[project_devils_galop]].

**Phase 6.2 — ALL 7 ENGINES + COMPOUND PSID DONE.** Phase 6.2 was
seven Hubbard engines: Action Biker, Chimera, Monty, Human Race,
Hunter Patrol, Thing on a Spring, One Man and His Droid. ALL DONE.
Plus the COMPOUND PSID 5 Title Tunes (2026-05-25): 5 sub-engines
glued via dispatcher, byte-exact across all 5 subtunes. [[project_action_biker]] is engine #4;
[[project_chimera]] is engine #5 — music subtunes byte-exact, AND
digi subtunes 2, 3 cycle-strict via siddump --writelog (the digi
"boundary" is now solved for Chimera-style 1-bit wavetoggle; see
[[reference_digi_pipeline]]). Chimera drove the IRQ-driven capture
fix (PSID play 0 → follow the $0314/$0315 vector), the configurable
arp period, AND the digi pipeline (D0..D3c, 2026-05-23).

**USF v2 on-disk format (2026-05-24): LANDED — load-bearing.** A real
`.usf` file format now exists ([[reference_usf_v2_format]]). The
codegen reads only the USF + sidecar FLACs — no peek at the original
SID. **All five migrated Hubbard '85 engines are on the USF-only path:
Chimera, Devils Galop, Action Biker, Commando, Monty. 46/46 subtunes
verify (cleared cache).**

The SFX schema landed same day (commit 4867537): `SfxSubtune` carries
the 2-voice register snapshots (6 bytes per voice — freq_lo is
aliased with start_index for v1 and with the gate-flags/v2_offset
byte for v2, both rederived at codegen time), sweep params, and 4
flag booleans. Commando (3 music + 16 SFX) and Monty (3 music + 16
SFX, off-table sweep via sfx_state_ofs=251) both verify end-to-end.

**Why:** The pre-2026-05-24 pipeline read the original SID at codegen
time in five places (load_sid, decode_all, config.extract,
config.resetspd, raw freq_bytes). "Always through USF" was a half-
truth — the in-memory dataclasses flowed between extract and codegen,
but the codegen also peeked at the binary as a silent safety net.
With USF v2 on disk, gaps in the representation become parse errors
instead of silently working. User explicitly demanded this discipline
on 2026-05-23.

**Chimera ships as PSID now**, not RSID. The original Chimera is RSID
(its IRQ exit does `jmp $EA31` — KERNAL-dependent). The USF-only
rebuild has a hand-written PSID dispatcher (xa65, no KERNAL deps, no
IRQ install — proper PSID `play` entry; init returns cleanly).
General pipeline rule going forward: every USF-rebuilt SID is PSID,
regardless of the original's format. RSID is a property of originals,
never of our outputs.

- **Monty on the Run — DONE, codegen 100%** (commits up to 70b3e1b).
  `pipelines/monty/config.py` + its engine_model on the shared core;
  all 3 subtunes 25000/25000 byte-exact, Commando 19/19 + Devils
  Galop 12000/12000 unaffected. Engine #3, a config + traced deltas,
  no clone. Monty drove four shared-core improvements (all help every
  future engine): the adaptive note codec (DUR_BITS/INST_BITS size to
  the data — Commando was over-fit at 3/4 bits), column-major
  instrument tables (row-major inst*16 overflowed the 8-bit index
  past 15 instruments), the freq-table-overlap variable seeding
  (v_ctrl/pwm_period/pwm_dir seeded from the binary), and the `$FE`
  freeze model (`freeze_on_stop`). See [[project_monty]].
- **6 remaining:** Action Biker, Chimera, Human Race, Hunter Patrol,
  Thing on a Spring, One Man and His Droid — each a config +
  engine_model + a short per-engine-delta trace.

**Next:** finish Phase 6.2 — 4 engines remaining (Human Race, Hunter
Patrol, Thing on a Spring, One Man and His Droid). Each is now a
~30-line task: add an EngineConstants entry (capture the 128-byte
state region from the binary), write a 10-line `to_usf_v2.py`
wrapper, verify. Then Phase 6.3 (D/F pipelines) + Phase 7 (ML-
readiness — the tokenisable dataset).

**Why:** the current USF leaks Hubbard engine internals into the data,
which is bad ML training data. Behavioral programs keep music abstract.

**How to apply:** work the phases in `docs/usf_instrument_program_plan.md`
in order; append commit hashes to its tracking table. Verify with
`src/writelog_diff.py`. Engine semantics for Commando are fully mapped
in `src/hubbard_emu.py` — read it before touching the extractor.

**Key engine facts found in Phase 3** (Commando, see hubbard_emu.py):
- Instruments are NOT pure functions of (pitch, frame): vibrato keys
  off global `frame_ctr & 7`, arpeggio off `frame_ctr & 1`.
- PWM self-modifies the instrument table row — pw bytes are a
  free-running accumulator, not a per-note constant.
- The ctrl "wave program" is a side-effect of the bit-0 skydive
  writing ctrl, not an independent sequencer.
- `fx_flags` bits: 0=skydive/freqSlide, 1=INC-by-2, 2=arpeggio,
  3=PWM linear-vs-bidirectional.
