---
name: project-refactor-1-phase-b
description: "Refactor 1 Phase B — lifted every Hubbard-skeleton emitter from `_emit_hubbard_*` into `FxNames`-parameterised skeleton-agnostic form, then dissolved the `_needs_hubbard85_path` discriminator. 26 commits, all byte-exact. Remaining work is folding the bitpack chain into `emit_asm`."
metadata: 
  node_type: memory
  type: project
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

Refactor 1 (composer engine-blindness) — the per-emitter lift phase.
Done 2026-06-03 across one session.

**Starting state:** `pipelines/composer.py` had a §8-violating
two-path structure: `_needs_hubbard85_path(usf, model)` sniffed USF
content for "Hubbard-shape" features (per-instrument modulation,
multi-pattern orderlists, SFX, state_layout) and dispatched to
`_emit_hubbard85_bytes`. The dispatch target was ~30 chunked
emitters with `_emit_hubbard_*` names that emitted Hubbard '85's
specific 6502 player skeleton. The universal `emit_asm` chain
handled simpler-shape USFs (companion, henrys, yes_tune, clever).

**What this phase landed:** every chunked emitter lifted to a
parametric form that reads/writes named storage via an `FxNames`
dataclass. The skeleton supplies a `FxNames` instance (today only
`HUBBARD_FX_NAMES` exists; future skeletons would supply their own).
Then the `_needs_hubbard85_path` discriminator was replaced with the
honest framing `if not can_handle(model): return _emit_bitpack_bytes(...)`.

**FxNames contract** (~70 named storage slots):
- Per-voice arrays (X-indexed): v_pitch, v_durfield, v_pwperiod,
  v_pwdir, v_dur, v_slide, v_tick, v_drumtrig, v_slidelo, v_instr,
  v_ctrlbyte, v_ended, v_frozen, v_patlo, v_pathi, v_orderpos,
  v_notesleft, v_bitcnt, v_hubidx, v_norel
- Per-voice scalars (zp): sidoff, instoff, pw_idx
- Global counters/state (zp): frame_ctr, vib_carry, vib_step,
  vdelta_lo, vdelta_hi, vdepthctr, vtarg_lo, vtarg_hi, vfreq,
  drum_prio, pv_abort, sub_tmp, end_phase, vol_progress, is_sfx,
  is_tick, first_frame, speed_ctr, cur_resetspd, voice_start,
  sfx_idx, sfx_rec, sfx_index, sfx_stepctr, sfx_done, sfx_started,
  sfx_v1gate, sfx_v2gate, sfx_y, sfx_flags, sfx_tmp, pwm_tmp,
  f_lo, f_hi, notep, orderp
- Note-start scratch: i_ctrl, i_ad, i_sr, i_pwlo, i_pwhi
- Instrument table (labeled, Y-indexed): it_fx, it_vibdepth,
  it_onset, it_pwmode, it_pwa, it_pwperiod, it_pwhi, it_pwlo,
  it_hrctrl, it_ctrl, it_ad, it_sr
- Lookup tables (labeled): freqtab, statebuf, pwacc, ovseed,
  pwseed, sidtab, sfxdata
- Orderlist (labeled): orderLo, orderHi, orderLoop
- Subtune-dispatch tables (labeled): subOrderLo, subOrderHi,
  subOrderLoop, subResetspd, subVoiceStart, subOvseedLo,
  subOvseedHi
- Subroutine: build_statebuf_subr

**Commits (this session):**
- `a7333c5` fx_vibrato — introduced FxNames + HUBBARD_FX_NAMES
- `209a28f` fx_pwm
- `975ee86` fx_skydive
- `1af319b` fx_arp (with arp_phase_invert arg)
- `638d896` fx_incby2 (with late_gate + per-subtune dispatch args)
- `b9a1ce9` fx_drumslide
- `7f29bf3` note_start (with ns_offtab_decr_offset arg)
- `c4b79f3` hr_writes
- `cd35cb0` set_patptr (with fade + loop_silences_song args)
- `27446df` next_orderidx
- `9841064` do_effects
- `cc0bce0` proc_voice
- `003038a` play (named `_emit_play_bp` — coexists with universal
            `_emit_play(model, active)`)
- `ee6065a` init (named `_emit_init_bp`)
- `05598a6` entry_stub
- `2d9345f` init_sfx (with sfx_state_ofs arg)
- `aadc9d2` sfx_play
- `da122a8` sfx_step (with sfx_state_ofs arg)
- `d3ce178` data-section emitters batch (14 functions; 2 needed
             `_bp` suffix for collision: _emit_orderlists_bp,
             _emit_per_subtune_tables_bp; wrapper renamed
             _emit_data_bp)
- `d6ebe84` top-level orchestrators (6 functions: _compose_engine_body_bp,
             _compose_engine_asm_bp, _emit_sid_bp,
             _emit_combined_sid_bp, _emit_bitpack_bytes,
             _needs_bitpack_path)
- `751b4bf` discriminator dissolved — replaced `_needs_bitpack_path`
             call with `not can_handle(model)`; function deleted
- `4a5fc97` unified non-digi asm-then-PSID-wrap pipeline. Extracted
             `_emit_asm_simple_shape` and `_emit_asm_bitpack`; both
             produce asm; shared `_assemble + _psid_header` post-
             pipeline. `_emit_bitpack_bytes` narrowed to digi-only.
- `dac43de` `emit_asm(model, usf)` — single asm entry, 5-way
             dispatch (4 simple-shape + bitpack); old `emit_asm`
             dispatch body renamed `_dispatch_simple_shape_asm`.

Every commit ran the full regression (Hubbard 71/71 + Companion
44/44 + C64ME 15/15 + Jay_Derrett 17/17) byte-exact green before
landing.

**Current state of `emit_sid_from_usf`:**
```python
digi_subs = [s for s in usf.subtunes if isinstance(s, DigiSubtune)]
if digi_subs:
    return _emit_bitpack_bytes(usf, usf_dir)   # digi orchestrator
asm = emit_asm(model, usf)                      # 5-way dispatch
body = _assemble(asm)
return _psid_header(model, n_subtunes=..., load=LOAD) + body
```

`emit_asm(model, usf)` is the single asm-emission entry with 5
branches: 4 simple-shape (every_tick × {two_phase, single_phase};
tick_counter; cmd-stream) + 1 bitpack (when `not can_handle(model)`).
The bitpack branch internally uses the lifted `_emit_*_bp` chunked
chain, but it's reached from the same `emit_asm` as everything else.

**The §8-honest framing:** the dispatch is feature-based throughout.
No engine identification anywhere. The remaining gap from full §8
satisfaction is that the bitpack branch is a sequestered
sub-implementation rather than feature-parametric pieces composed
into the simple-shape dispatch.

**Deeper diagnosis (2026-06-03, end of session):** even the 5-way
dispatch in `emit_asm` is engine-flavored — each of the 5 branches
maps to roughly one engine family (atomic = henrys/bowden; pair =
yes_tune; cmd-stream = clever_music; companion two-phase =
up_up_and_Away; bitpack = Hubbard '85). With one engine family per
branch, the §8 cover-story risk is still live, just spread across 5
branches instead of one. The mechanical-lift phase is genuinely
done; closing the remaining gap requires structural unification.

**Why further refactoring is DEFERRED, not abandoned:** designing a
unified player skeleton against the current narrow corpus (5
families, ~150 subtunes) would overfit. DMC (~10k SIDs), GT2 (~7k
SIDs), and other large engine families bring real structural
diversity. Migrating them FIRST either vindicates the existing
feature dimensions (multiple consumers per feature = genuine
parametricity) or surfaces what new dimensions the dispatch needs.

**Revisit criteria:** pick the unification work back up when at
least two of:
- DMC migration substantially started (50–100+ subtunes verified)
- GT2 migration substantially started (`deprecated/gt2_pipeline/`
  has prior work to reactivate)
- 2+ other large engine families migrated (Music_Assembler ~6k,
  Future_Composer ~4k, Soundmonitor ~3.6k SIDs)

**Substantive plan lives at:** `docs/refactor_1_remaining.md` —
includes Move 2 (digi fold — landable any time, doesn't depend on
corpus richness) and Move 1 sub-moves (D.1 unified note codec, D.2
unified per-voice state, D.3 unified player skeleton).

**Remaining work for the §8 endpoint:**

Two distinct pieces left, both architectural rather than mechanical:

1. **Collapse the bitpack-chain sub-emitters into peers of the
   simple-shape ones.** The bitpack player skeleton is structurally
   different from atomic/pair/cmd-stream — different runtime
   conventions, different orderlist layout, different note codec.
   To make them peers, the universal skeleton design has to
   accommodate all of them as variants of the same structural model.
   This is a redesign, not a lift.

2. **Fold digi orchestration into the unified pipeline.** Currently
   `_emit_combined_sid_bp`'s iterative auto-packing against the digi
   dispatcher base + inline-load PSID encoding + sample-blob
   composition makes digi a separate orchestrator. To fold it in,
   `emit_asm` would need to produce music asm for digi USFs and a
   post-asm step would handle the digi region.

The lifts done in this phase make either of these possible — the
mechanical work of removing engine names and parametrizing
emitters is done. What's left is architecture.

**Where `_bp` suffix lives** (collision-coexistence with universal
emit_asm names): `_emit_play_bp`, `_emit_init_bp`,
`_emit_orderlists_bp`, `_emit_per_subtune_tables_bp`, `_emit_data_bp`,
`_compose_engine_body_bp`, `_compose_engine_asm_bp`, `_emit_sid_bp`,
`_emit_combined_sid_bp`. Other lifted emitters (`_emit_fx_*`,
`_emit_note_start`, `_emit_hr_writes`, etc.) have no prefix because
they don't collide.
