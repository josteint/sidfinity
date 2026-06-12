# DMC V4 — RE notes / migration log

## Status (2026-06-12)

**✅ Geometrical_Zaks FULL** — all 3 subtunes instruction-sequence exact
at full songlength ×1.1 (sub0 303565, sub1 266449, sub2 73661 play
writes; trichotomy Check A state ✓). First DMC member through the
SID → USF → SID pipeline. Wired into `tools/regression.py` (DMC
section). Verdict tool: `pipelines.dmc.verify.verify_dmc(cfg)`.

Pipeline: `pipelines/dmc/v4/extract/` (dataflow operand reader +
path-resolved pattern simulation) → USF → `pipelines/dmc/composer_asm.py`
(our own engine; own event encoding, parallel instrument arrays,
pre-split pulse nibble/base tables) → xa65 → PSID.

## The three write-log iterations that got Zaks FULL

1. **Idle-note voice_state priming.** A voice whose track opens with
   rests (Zaks V3) still runs the full effect chain; the original's
   wave-freq lookup reads the WORK-FILE LEFTOVER current-note bytes at
   $1012-$1014 (uncleared by init). Carried as
   `init { voice N { note: M } }` (engine-state priming, trichotomy
   §4.5). The leftover $1015-$1017 instrument bytes do NOT matter (the
   note-init CACHE is what the effects read, and init clears it to 0 —
   i.e. idle voices run instrument RECORD 0's pulse/wave mechanism).
   Extract therefore force-includes record 0 as USF slot 0.

2. **Idle pulse base separation.** The pulse step = table nibble +
   CACHED base ($175F). Idle voices have base 0 (cleared) but read
   record 0's nibbles — so the effective steps `(nib<<4)+base` cannot
   be pre-baked. USF carries effective `speed_steps`; the composer
   derives base = step & $0F (asserts all six share it) and the engine
   adds the cached base at runtime (0 while idling). Exact for both.

3. **xa65 gotchas** (composer-side): ':' acts as a statement separator
   even inside ';' comments (sanitizer strips them); branch-out-of-range
   at frame_entry; non-ASCII in comments is a syntax error.

## Family semantics the engine reproduces (see disassembly.s for all)

- 3-frame minimum gate ($1786 guard), then release_early instruments
  get the $FE gate mask; hold = gate-off + AD/SR=$00 at duration ctr 1;
  open = never.
- Hard-restart fetch frame writes ONLY ctrl=$08, AD=$0F, SR=$0F.
- Inactive ($FE'd) voices keep writing their 5 regs every frame.
- Dual effect: GLOBAL half-rate parity shared across voices; odd-frame
  freq = base+accum_lo (hi takes carry only, NOT accum_hi) − slide.
- Filter: single owner per frame (claim, X order); $D418 written only
  at init and at filter note-init (mode|vol).
- $D417 routing shadow primed from the file-image leftover ($1018,
  uncleared by the original init) = `init.sid.filter.res_routing`.

## Residue / uready accounting (open, not blocking Zaks)

- **Family rollout not started**: one member FULL. Factory
  (`dmc_v4_config(sid)` probing the 7 patched operands + wrapper-init
  members like On_My_Way_to_X / Retro_Tech) is the next phase, then
  the wide batch over family 1 (5401 SIDs).
- **Idle-state assumptions**: idle voices reproduce the original only
  when (a) USF slot 0 == original record 0 (extract enforces) and
  (b) record 0's wave_start == 0 (true for Zaks; factory must check —
  otherwise the idle wave walk starts elsewhere in the table).
- **Off-table reads not modeled**: wave-freq offset + note > 95 reads
  past the freq table (the original reads the adjacent table/state
  bytes — the FC freq_overrun analog); same for vibdepth with
  note+transpose > 95. Extract should assert; currently silent.
- **Gate-mask leftovers**: $100F-$1011 assumed 0 in the file image
  (true for Zaks; probe in the factory).
- **Aux entry points** (+$06 all-off, +$09 sfx-note, +$1D tune-select
  chaining semantics incl. the routing shadow surviving re-init) are
  not emitted — PSID playback never calls them.
- **V5/V6/V7 + family 2** (the 0.732 V4-derived variant, 2889 SIDs):
  separate work; V5 sector encoding still needs RE.
- **Ear test pending** (py65/writelog can't catch dispatch-rate bugs —
  CLAUDE.md convention: ear-test every new engine).
