---
name: composer-dissolution
description: "Composer rewrite Phase 8 (2026-05-27 → 2026-05-30) — composer_hubbard.py dissolved into composer.py; entire Hubbard '85 family is now feature-driven asm composition with no template substitution."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

The 13-phase composer rewrite (Phases 8.9-8.21) lifted every Hubbard '85
asm artifact out of `composer_hubbard.py` and threaded every per-engine
knob through `_compose_hubbard_engine_asm` as typed arguments. **Phase
8.21 deleted `composer_hubbard.py` entirely.**

**Why:** Aligns Hubbard '85 with the same composer-native shape the
companion engines use; eliminates the template + sentinel-substitution
build path (which obscured what was actually engine-specific vs shared).

**How to apply:** From any USF, the build path is one call chain in
`pipelines/composer.py`:

```
build_from_usf(usf, out)
  → composer.emit_sid_from_usf(usf, usf_dir)
    → _needs_hubbard85_path(usf, model)
    → _emit_hubbard85_bytes(usf, usf_dir)
      → _inputs_from_usf(usf)                       # USF → _Inputs
      → _hubbard_emit_sid(inputs, ..., codec)       # music path
        → _pattern_pool(inputs.scores)
        → _compose_hubbard_engine_asm(inputs, codec, ...)
          → _emit_hubbard_asm_equates(inputs, codec)
          → codec.zp_asm
          → _compose_hubbard_engine_body(state_layout, load_addr,
              sfx_framectr_ofs, arp_phase_invert, ns_offtab_decr_offset,
              sfx_state_ofs, incby2_late_gate, has_per_subtune_ovseed,
              has_master_vol_fade, uses_per_subtune_dispatch)
            → 18 _emit_hubbard_<chunk>(...) calls
            → _emit_build_statebuf(state_layout)
          → _resolve_codec_note_asm(codec, inputs)
          → _emit_hubbard_data(...)
        → xa65
        → PSID header
   OR → _emit_combined_sid(...) when usf has DigiSubtunes
        → _build_digi_region(usf, digi_subs, digi_code, usf_dir, ...)
```

**No template substitution anywhere.** Every `; %%SENTINEL%%` placeholder
that existed during the transition has been resolved by parameterizing
its host chunk. The 18 routine chunks (init, play, proc_voice,
set_patptr, next_orderidx, note_start, hr_writes, do_effects,
fx_drumslide, fx_incby2, fx_pwm, fx_vibrato, fx_skydive, fx_arp,
build_statebuf, init_sfx, sfx_play, sfx_step) each have their own
`_HUBBARD_<NAME>_ASM` constant + `_emit_hubbard_<chunk>(...)` accessor
in `pipelines/composer.py`.

**Verification baseline as of 2026-05-30:**
- Hubbard '85: 71/71 byte-exact (md5 of `$D400-$D418` per-frame snapshots).
- Companion + 5_Title_Tunes: 32 ok + 3 known-partial + 0 regressions
  (cycle-strict via `compare_instruction_stream`).

Known-partial subtunes carried through the rewrite (NOT new regressions
— pre-existed since before the rewrite started):
- `Fairlight` sub 0
- `Melonmania` sub 1
- `5_Title_Tunes` sub 2

Run [`tools/regression.py`](../../../sidfinity/tools/regression.py) to
re-baseline; it explicitly lists the known-partials so they don't get
mistaken for regressions.

See also [[composer-architecture-files]] if I ever write down the
file-level map of composer.py's ~5,000 lines.
