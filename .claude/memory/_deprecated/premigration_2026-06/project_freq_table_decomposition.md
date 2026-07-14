---
name: project-freq-table-decomposition
description: "Phase 4 of the migration sequence — all 12 Hubbard '85 engines migrated from 320-byte opaque freq_table to typed USF carriers (192 musical + populated init.voice + per-SFX extended_freq). Engine code tail + dead state bytes dropped from USF."
metadata: 
  node_type: memory
  type: project
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

Phase 4 of the user's stated migration sequence (the freq_table
spillover decomposition refactor) — done 2026-06-03.

**What changed:** the old `freq_table { 320 bytes }` USF block carried
three unrelated things under one opaque carrier:
- 192 bytes of musical PAL freq table (read by every note + SFX sweep)
- ~18 bytes of per-voice init state at named offsets (+205/+208/+214/+229/+232/+239) — already had `init.voice N` schema, just emitted empty
- ~4-10 bytes of SFX-sweep "extended freq table" (bytes the sweep reads when sfx_y >= 192 or V2's sfx_y - v2_offset underflows — they ARE the audible pitches at extreme sweep positions)
- ~55 bytes of Hubbard's verbatim 6502 SFX-init code — INERT in the rebuild (composer regenerates SFX init cleanly via `_emit_hubbard_init_sfx`)
- ~110 zero/unread bookkeeping bytes

**Why:** Per [[feedback-composer-engine-blindness]] and §8 of
`docs/usf_representation_principle.md`. Bytes that aren't read by the
rebuild aren't music; they don't belong in USF. Carrying Hubbard's
6502 init code verbatim is shape-preservation that lets the composer
silently lean on engine-shaped USFs.

**New schema:**
- `freq_table { ...192 bytes... }` — musical PAL only (could later
  default-elide to `freq_table: hubbard85_pal` since all 12 engines
  share the same bytes)
- `init { voice N { ... } }` — populated explicitly from the named
  state-region offsets
- `SfxSubtune.extended_freq: dict[offset, byte]` — per-SFX overlay
  carrying ONLY the bytes the sweep actually reads at offset ≥ 192,
  computed by simulating the sweep state machine in extract. Drops
  entries equal to the implicit default (0 elsewhere, init.voice
  slot value at named offsets) so only the meaningful overlay bytes
  remain.

**Composer:** `_inputs_from_usf` accepts both 192-byte and 320-byte
`freq_table` (back-compat). For 192-byte, reconstructs a 320-byte
internal buffer = freq_table + 128 zeros + init.voice overlay +
per-SFX extended_freq overlays.

**Coverage:**
- All 12 Hubbard '85 engines migrated: commando, action_biker,
  battle_of_britain, chimera, confuzion, devils_galop, human_race,
  hunter_patrol, monty, one_man_and_his_droid, thing_on_a_spring,
  five_title_tunes.
- Hubbard 71/71 + Companion 44/44 + C64ME 15/15 + Jay_Derrett 17/17
  — zero regressions through `tools/regression.py`.

**5TT note:** uses its own bespoke write path
(`pipelines/hubbard/five_title_tunes/unified/write_unified_usf.py`)
rather than the shared `write_usf`. Patched to also emit 192-byte
freq_table; its per-subtune init.voice (via `per_subtune_ovseed`) was
already populated.

**Inventory experiment script:** the load-bearing-byte analysis was
done by zeroing groups of bytes in `COMMANDO_FREQ_STATE` and running
verify_all to see which broke. Findings recorded above; experiment
scripts removed from /tmp after the work landed. If a similar
inventory is needed for a new engine, the pattern is: monkeypatch the
ec.freq_bytes via the in-memory `EngineConstants` object, rebuild via
`build_from_usf`, run `verify_all`.

**Commits:**
- 04b242a — principle doc §8 (composer-blindness rule)
- 60e75a9 — Commando proof of concept (schema + extract + composer)
- 4ca3aa6 — 5TT migrated (just the freq_table trim on its bespoke
  write path)

**Next phase candidates (still on the user's list):**
- Composer engine-blindness refactor (Refactor 1 from the original
  plan — delete `_needs_hubbard85_path`, unify dispatch). Bigger
  scope; surfaces what Hubbard-specific knowledge is currently
  baked into the per-engine emitters.
- Phase 5: instrument representation refactor (the ML-target punch
  list — see [[project_usf_instrument_ml_target]]).
