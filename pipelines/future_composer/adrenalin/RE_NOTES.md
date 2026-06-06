# Adrenalin (HeatWave) — RE notes

**SID:** `hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid`
**Engine:** MoN/FutureComposer (per sidid)
**Authors:** Marvin Severijns & M. de Bree
**Songlength:** 9:25 (565s), 4 subtunes
**PSID:** load=$0000 (inline-encoded), init=$50E0, play=$50E3
**Purpose:** 3rd FC family canary — diversifies away from Tel-only
canaries (Hawkeye, Cybernoid_II). See `docs/canary_picker.md` row 3
of engine #4 (MoN/FutureComposer).

## Status (2026-06-06)

**Stalled at structural discovery.** The runtime layout differs
fundamentally from Hawkeye/Cyb II:

1. **Inline-load PSID.** Header load=$0000 means the first 2 bytes of
   code body hold the actual load address (=$50E0). Hawkeye/Cyb II
   are non-inline (header load=actual load).

2. **Self-decompressing engine.** PC trace at subtune 1, 0.5s shows
   execution flows from $50E0..$5100 area → $7A00-$8100 area. The
   binary occupies $50E0..$81D0 (~12.5kB), but the engine itself isn't
   visible at the load address — it gets *unpacked* into the
   $7Axx-$81xx range at init. Adrenalin's $50xx region is a
   decompressor + packed engine data.

3. **`tools/seed_disassembly.py` only traced 76 lines** because it
   follows reachable code from init+play+subtune-entries and the
   unpack stage SMC-installs further entry points it can't see ahead
   of time.

## To continue

The pre-decompression binary is opaque. To get a useful disassembly:

1. **Run init in py65 to completion** (the decompressor exits to RTS
   or the IRQ handler).
2. **Snapshot RAM after init**: `mem_post_init = py65.memory[$7A00:$8200]`
   (or wider — the actual range needs discovery).
3. **Write the snapshot as a synthetic PSID** with load=$7A00 and the
   actual play address from the IRQ vector.
4. **Re-run `tools/seed_disassembly.py`** on the synthetic PSID. Now
   the disasm sees the real engine code with proper entry points.
5. **Cross-reference with `pipelines/future_composer/docs/wiki_fc_v41_manual.md`**
   and `csdb_fc_v4_player_disasm.md` for FC instruction semantics.
6. **Hand-annotate** structural labels (per-frame routine, nolengset,
   tone_arp, vibrato, drum, etc.) following Hawkeye's
   `disassembly.s` as a model.

## Then the standard canary-extract path

Once a clean disassembly exists:

1. Find the ~12 address knobs (freq_lo/hi, pattern_ptr, instr_records,
   per_subtune_speed, drumtabel, filterbytes, arplo/hi, pulsetabel,
   vibtabwait, startlen, starttabel) via `lda <addr>,X` greps.
2. Choose FCConfig knobs (subtune_layout, pulse_run_style,
   noise_tick_style, voice_loop_layout, ...).
3. Address the inline-load PSID shape — may require a new FCConfig
   field or a small extension to `composer.py::_load_sid_psid` to
   handle inline at SID-write time.
4. Build canary: `pipelines/future_composer/adrenalin/config.py` →
   `ADRENALIN = FCConfig(...)`.
5. Extract: `from pipelines.future_composer.engine_model import
   extract; extract(ADRENALIN)`.
6. Verify byte-exact: `verify_featuredriven(ADRENALIN)`.
7. Add to `tools/regression.py::regress_future_composer` canaries
   list once 4/4 subtunes go FULL.

## Why we're adding Adrenalin

Hawkeye + Cybernoid_II are both Jeroen Tel tunes; their feature mix
overlaps heavily and doesn't exercise everything the FC engine can do.
HeatWave's Adrenalin is the only non-Tel candidate in `canary_picker`
row 3 of engine #4, and adds (at minimum):

- Different composer style → different per-instrument fx_bytes patterns
- Self-decompressing engine load shape
- Inline-encoded PSID header
- 4 subtunes (multi-sub regression coverage)
- Potentially: feature combinations no Tel tune uses (subtune SFX
  handling, different fil_count bits, different drum tables, etc.)

The composer's current feature coverage is honest only when at least
one canary structurally distinct from the existing two demonstrates
that the feature-driven composition path generalises beyond Tel's
subset.

## Tools to use (per [[feedback_writelog_divergence_recipe]])

- `tools/seed_disassembly.py` — generate skeleton (already done at
  76 lines; redo against post-init snapshot)
- `tools/find_first_divergence.py` — once a rebuild exists
- `siddump --memwatch-on-write` + `--memwatch` — state inspection
- The hand-annotated disassembly is the input to everything else.

## Related

- [[project_hawkeye]] — worked example of FC canary migration end-to-end
- [[feedback_check_existing_engine_docs]] — Step 0 protocol
- `pipelines/future_composer/docs/wiki_fc_v41_manual.md` — FC v4.1
  instruction format
- `pipelines/future_composer/docs/csdb_fc_v4_player_disasm.md` —
  player disasm reference
