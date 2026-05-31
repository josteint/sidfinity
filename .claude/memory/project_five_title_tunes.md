---
name: project_five_title_tunes
description: "5 Title Tunes — UNIFIED single-engine byte-exact (5/5 subtunes, 7950 bytes vs original 11849). One Hubbard '85 engine plays all 5 tunes via per-subtune runtime tables (params, ovseed, instrument-base, orderlist). Drove three codegen extensions: per-subtune engine params, per-subtune ovseed, USF v2 per-subtune params block. Replaces an earlier 5-engine compound (20836 bytes)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *5 Title Tunes* (1985, self-published). Unique in the
97-song Hubbard catalog — the parent PSID at $0B10/$0B40 is a
**dispatcher** that JSRs to 5 fully independent Hubbard '85 sub-engines
(each with its own init, play, freq table, instrument table, pattern
data). Disassembly: `pipelines/hubbard/five_title_tunes/disassembly.s`.

**Status (2026-05-25, evening): UNIFIED single-engine byte-exact.**

The shipped `demo/hubbard/5_Title_Tunes.sid` is now ONE Hubbard '85
engine playing all 5 subtunes (7950 bytes vs original 11849, and
38% the size of the earlier compound build at 20836 bytes).
Yesterday's compound was the stepping stone; today's unified build
replaces it.

```
unified sub_0: 3370/3370 (100.0%)
unified sub_1: 2247/2247 (100.0%)
unified sub_2: 2816/2816 (100.0%)
unified sub_3: 5921/5921 (100.0%)
unified sub_4: 6637/6637 (100.0%)
```

verify_all over the 9 other engines: 83/83 still byte-exact. Zero
regression.

## Pipeline shape — different from the other engines

Lives at `pipelines/five_title_tunes/v2/`. The directory's V1 path
(merge-into-single-engine, audibly correct but NOT byte-exact) is left
intact for reference.

```
data/.../5_Title_Tunes.sid                       (parent PSID, 11.7KB)
    │
    ▼ tools/split_multi_binary.py (existed already)
work_subs/sub_{0..4}.sid                         (5 standalone PSIDs)
    │
    ▼ v2/config.py — 5 EngineConfigs (TUNE0..TUNE4)
    │
    ▼ v2/extract/engine_model.py — forked Chimera
    │
    ▼ pipelines.hubbard.to_usf_v2.write_usf  ×5
    │
demo/hubbard/5_Title_Tunes_{0..4}.usf            (5 USFs, one per sub)
    │
    ▼ pipelines.hubbard.build_from_usf — standalone build at LOAD=$1000
    │  (each sub byte-exact against parent[subtune N])
    │
    ▼ v2/build_compound.py — codegen 5× at unique LOADs + dispatcher
    │
demo/hubbard/5_Title_Tunes.sid                   (compound PSID, 20.8KB)
```

## Per-sub parameter deltas (vs Commando defaults)

| sub | tempo | speed_ctr_init | arp_period | incby2          |
|-----|-------|----------------|------------|-----------------|
| 0   | 4     | 3              | 2          | (no late-gate)  |
| 1   | 2     | 1              | 2          | step=-1, onset=$10, late_gate=$18 |
| 2   | 3     | 0              | 2          | onset=$10, late_gate=$18 |
| 3   | 3     | 1              | 2          | (no late-gate)  |
| 4   | 2     | 1              | 2          | onset=$10, late_gate=$18 |

Per-sub addresses (from `decompile()` auto-discovery on each sub_N.sid):

| sub | instr_base | freq_table_base | instr_count |
|-----|------------|-----------------|-------------|
| 0   | $1065      | $0F6A           | 8           |
| 1   | $1D02      | $1C07           | 12          |
| 2   | $245B      | $2360           | 12          |
| 3   | $2C9B      | $2BA0           | 12          |
| 4   | $35BE      | $34C3           | 12          |

## Compound build — three things had to converge

1. **`pipelines/hubbard/codegen.py`** — `_emit_sid` now accepts an
   optional `load_addr`. Rewrites the ENGINE template's `* = $1000`
   before xa65 and threads the new address through the PSID header.
   Default $1000 keeps existing engines unchanged.

2. **`pipelines/hubbard/inst_generalize.py`** — linear-PW instruments
   with `pwm_speed=0` now correctly produce `mode='linear'` (was None).
   The Hubbard engine writes pw_lo each frame even when speed=0; the
   linear-PW path runs unconditionally. Without this, 5TT sub_0 inst 7
   lost its per-frame V2.pw_lo=00 writes. Existing engines unaffected.

3. **`pipelines/five_title_tunes/v2/build_compound.py`** —
   - Build 5 sub-engines at $1000, $2000, $3000, $4000, $5000.
   - Assemble init dispatcher at $0B10 (CMP/BNE/LDA #0/JSR chain)
     and play dispatcher at $0B60 (LDA $0BA8 routed through same).
   - Save subtune index to $0BA8.
   - Compose memory image $0B10..(highest sub end), pack as PSID.

## CRITICAL discoveries (each cost ~30 min to find)

### xa65 ignores the second `* =` directive

xa65 emits a flat binary that ignores subsequent `* =` PC directives
when they're forward. `* = $0B10 ... init ... * = $0B40 ... play ...`
produces a contiguous binary where `play` ends up right after `init`,
NOT at $0B40. **Workaround**: assemble each chain separately and place
at the target offset in the region bytearray. The build_compound does
this via two `_assemble_chain` calls.

### Each sub-engine expects A=0 (its own subtune 0)

Each sub-engine is built with `N_MUSIC=1` — its `init` does
`cmp #N_MUSIC; bcs sfx_init`. If the dispatcher passes A=2 through to
the sub's init, A >= N_MUSIC → init routes into the SFX-init path,
which corrupts $9A (becomes a pointer to the end of sub data, where
bytes are $00) → play() writes $D400..$D40D from `(zp $9A),Y` reads
zero bytes → music silent.

**Fix**: dispatcher must `LDA #0` before each `JSR <sub_init>`. The
subtune routing happens BEFORE that LDA via CMP against the saved
$0BA8.

### Splitter has a load-offset bug (cosmetic, not blocking)

`tools/split_multi_binary.py` writes `sub_0.sid` with `load=$0C06` but
sub_0's $1850 init JSRs $0C00 (6 bytes earlier). The standalone
sub_0.sid as-written by the splitter doesn't play correctly through
py65 capture — the JSR to $0C00 hits unloaded ($00) memory.

This didn't block migration because the EXTRACT path doesn't need a
playable sub_0.sid (decompile reads bytes directly). But future code
that wants to play sub_N.sid standalone needs splitter changes
(probably: set load = lowest of init/play/JSR targets).

## Unification — the win

The compound's 5 codegen'd engines collapse to ONE engine code body
that handles all 5 subtunes. Architecture:

- ONE engine binary (~1.5KB compiled).
- ONE concatenated instrument table (56 absolute IDs: sub_0 → 0..7,
  sub_1 → 8..19, sub_2 → 20..31, sub_3 → 32..43, sub_4 → 44..55).
  Per-sub pattern note inst bytes get renumbered by `+offset`.
- ONE shared PAL freq table + sub_1's state region (sub_1 is the
  only sub whose arpeggio reads past pitch 95).
- 5 subtune-indexed runtime tables: existing `subOrderLo/Hi/Loop`,
  `subResetspd`, `subVoiceStart` PLUS three new ones — `subSpeedCtrInit`,
  `subIncBy2Step`, `subIncBy2LateGate` — PLUS per-subtune ovseed
  (`subOvseed_0..4` + `subOvseedLo/Hi`).
- Globally unique pattern-pool indices (each sub's patterns shifted
  by a per-sub offset; without renumbering the dedup pool collapses
  cross-sub).
- Codec auto-sizes `INST_BITS=6` to fit absolute IDs 0..55; smaller
  engines still use 4-5 bits.

The critical insight that closed the byte-exactness gap: the
per-voice `v_instr` ovseed bytes (load-time initial instrument
references) are sub-LOCAL in the raw freq-table overlap. When
extracting per-subtune ovseed for the unified build, the `v_instr`
bytes must be renumbered by the sub's global inst offset, or the
voices boot with the wrong initial instrument (sub_1 was reading
sub_0's first 3 insts → wrong PWM / freq / ctrl → silenced sub_1).

## Codegen extensions this engine drove

  1. `_emit_sid(load_addr=...)` for the compound stepping stone.
  2. Per-subtune engine params via runtime tables — gated on
     `inputs.per_subtune_*` lists. The `lda #SPEED_CTR_INIT;
     sta speed_ctr` becomes `ldy sub_tmp; lda subSpeedCtrInit,y;
     sta speed_ctr; ...` and the engine's fx_incby2 reads from new
     `cur_incby2_step` / `cur_incby2_late_gate` zp slots seeded at
     init. Existing 9 engines unchanged.
  3. Per-subtune ovseed via init-time copy — engine copies the
     selected sub's 18-byte ovseed into the `ovseed:` data block
     before the existing iniov loop runs.
  4. USF v2 schema extension: `params { ... }` block inside a
     music subtune. Optional; overrides engine-level params for
     that subtune.
  5. `inst_generalize` fix from yesterday (linear-PW with
     pwm_speed=0 emits mode='linear') still needed; preserved.

## Related

- [[project_usf2_refactor]] — overall USF v2 status (Phase 6.2 done +
  COMPOUND demonstrated + UNIFIED replaces compound).
- [[reference_engine_image_verbatim]] — alternative path when an engine
  can't be parametrized; not used here (5TT was fully parametrizable).
- [[feedback_audit_discriminator]] — useful when diagnosing the linear-PW
  zero-speed write issue.
