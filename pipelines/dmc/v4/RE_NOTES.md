# DMC V4 — RE notes / migration log

## ✅ ROUND 52 (2026-07-08): DOUBLE-SPEED base+3 JMP wrapper — Scan_Collection_end +9 → FULL (+10, 0 regr) [ledger C24/play_repeat note]

Random f1 partial `MUSICIANS/L/Lio/Scan_Collection_end.sid` (vblank). The
batch row looked odd: `play_match == play_overlap == 215063` (a PERFECT
prefix) yet `len_post_a=429373` vs `len_post_b=215063` — orig's play stream is
~2× mine's over the SAME duration. Not a content divergence: counting writes
per frame gave orig ≈34, mine ≈17 in steady state, and a steady-frame dump
showed orig = **two full music updates back-to-back** (the PW sweep
`$D402/$D403` advances `$2F/$0C → $B8/$0B` between the two halves). It is a
DOUBLE-SPEED tune.

Root cause: the play VECTOR is `$1003: JMP $2000` (the `$1000` page is just
title text), and `$2000: JSR $1050 : JMP $1050` = the engine at `$1050` runs
**twice per play()** — the classic `_detect_play_repeat` "`JSR T; JMP T` =
n+1" wrapper. But the probe never reached that analysis: line-680
`if play == base+3: return 1` short-circuited (play=$1003=base+3) BEFORE
following the JMP. Note the canonical player ALSO has `$1003: JMP $1085`, but
`$1085` is the plain play body (`DEC $1718` speed-counter) — the wrapper loop
already follows a leading JMP once and returns 1 for a plain body; the
short-circuit merely skipped that walk.

FIX (one line): short-circuit only when `mem[base+3] != 0x4C` (base+3 is NOT a
JMP); otherwise fall through to the existing loop, which follows the leading
JMP once and detects the JSR-chain / JMP-tail wrapper (returns 2 here).
REGRESSION-SAFE BY CONSTRUCTION: canon `base+3 = JMP → DEC play body` still
returns 1 (byte-identical build); only a genuine `JSR T; JMP T` double-play
wrapper returns ≥2 — and any such member, built single-speed, was ALWAYS a
length partial (½ the writes), never a FULL, so no FULL can regress.

Census over all 5401 f1 members: exactly **10** satisfy `play==base+3 AND new
play_repeat≥2` (the other 27 `play_repeat≥2` members have `play≠base+3` and
already went through the loop) — Lio Happy_Night / Msxs / Scan_Collection_end,
Logan Black_Music, PRI Do_the_Note / Dreamland, The_Syndrom Double_Power /
Other_One / Saturday_Night / Savage_Remix. **All 10 flip partial → FULL** on a
fresh full-songlength verify. Full `tools/regression.py` green (0 regressed all
7 families); artifacts mass-written.

METHOD LESSON: a perfect play-stream PREFIX plus a clean ~2× length tail on a
VBLANK tune is whole-play double-speed, not a missing effect — localize by
counting writes/frame, then disassemble the play VECTOR and FOLLOW its JMP;
don't stop at `base+3`.

## ✅ ROUND 51 (2026-07-08): WJMP-CHASE SHADOW — High_Tech partial → FULL (+1, 0 regr) [ledger C11 new note]

Random f1 partial High_Tech (Dr_Piotr, vblank, flat div 32811, V3 freq-hi
orig $01 vs mine $00). First-div chase (memwatch + pc-trace ground truth):
the V3 note's base freq = an OFF-TABLE melodic read at idx 120 → freqhi[120]
= $171F, the shared `wjmp` scratch (round-31 class). All other inputs (accum,
slide, parity) matched; only `wjmp` diverged (orig $01, mine $00). Root cause:
`$171F` at that read = V1's wave marker-HOP distance ($91→$01), and V1 plays
**instrument 7 whose wave_start=137 sits ON its own end-marker $91** (the
"start at the loop marker" editor idiom). The orig, starting on the marker,
chases back 1 EVERY note-init (writing $171F=1); the composer packs the
SETTLED program (skips the transient chase) so it misses the note-init hop —
every subsequent frame it hops naturally, so the ONLY missed write is the
note-init one, and it only shows when a wjmp read lands on that frame before
another voice overwrites $171F (V2 idle that frame). FIX (CORE TENET — layout-
independent, reproduce the WRITE): extract `wave_start_on_marker` (own-end
marker + loop 0, gated on a wjmp read + canon geom) → USF per-instrument flag
→ composer re-asserts `wjmp = n` at note-init (`iwchase` table + `ni_chase`,
emitted only when some instrument chases). REGRESSION-SAFE BY CONSTRUCTION:
re-asserts a write the orig ALWAYS makes; observable only where orig diverged
(6 random FULLs + all portfolio byte-identical; full tools/regression.py green,
0 regressed all 7 families). Census: 4 f1 partial carriers — High_Tech FULL
297/297s exact; Chwat + Solar_Energy first-div resolved → deeper blocker (Lens
3); King_of_Earth's wjmp read diverges for a non-chase reason (honest residue).
METHOD REMINDER: for a global cross-voice scratch, memwatch the read value +
diff orig-vs-reb INPUTS (base/accum/slide/parity) at the same event index to
isolate which term diverges; a chasing instrument's phase leaks into another
voice's $171F read even when its own output is a constant 1-step loop.

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
- **Ear test PASSED** (2026-06-12, user) on Geometrical_Zaks.

## ✅ ROUND 1 sub-build recovery (2026-06-14): 2945 -> 3135 FULL (+190)

The big `player_code_mismatch` buckets turned out to be EQUIVALENT-write
sub-builds or PSID-sub-entry variation — the family-1 sub-builds use the
SAME variant axes as DMC family 2. Fixed in `factory.py`:
- **$1181 (130): rest/switch/slide-tail JMP $1591 (skip effects)** vs
  canon JMP $1322 — the family-2 `rest_effects='skip'` behavior in
  family-1 members. Probe $1180 -> `cfg.extra_params['rest_effects']`.
- **$1631+$163E (136): all-off (+$06) / sfx (+$09) routines** vary per
  sub-build but are NEVER executed during play() (verify only drives the
  play vector). Masked $162F-$1647.
- **$12A8 (80): filter $D418 write via a JSR helper** (STA $D418 + a
  dead store) vs inline STA $D418 — identical write. Mask + validate.
- **IMAGE-WIDE jump-table scan** for relocated-within-file players (at
  neither play-3 nor load): +7 (most no_jumptable have NO jump table or
  a CIA-timer the py65 init probe can't read).
4 family-2 canaries + the v4 portfolio guard this in regress_dmc.
RESIDUE still open: remaining sub-build sites ($1231 = a real SR-compute
variant + different helper; $18B4; $1493; smaller), 364 no-jump-table
(no findable base), 35 cia_multispeed (timer unreadable), the off-table
architectural limit (~600, correctly refused).

## Wide-batch residue buckets (family 1 = 5401, ranked by size)

Each is its own next-round triage target. Sizes from the first full
sweep; the factory's typed reasons make these greppable in
`tmp/dmc_wide_results.jsonl`.

1. **Relocated 2-entry layout (~621, `player_code_mismatch` first
   diff at $1001).** A whole sub-build: 2-entry jump table
   (`$1000 JMP $1807` init / `$1003 JMP $1050` play) vs canonical's
   4-entry, with the body shifted (play body $1050 vs $1085, etc.) and
   vars starting $1006 not $100C. Same engine, different assembly —
   needs a second canonical reference binary + a layout-variant probe
   (FC reloc-factory analogue). HIGHEST-VALUE next target.
2. **Other code-mismatch sub-builds (~430): first diff at $1181 (101),
   $1631 (79), $12A8 (76), $163E (31), $1231 (24), $119B (22), ...**
   each a distinct patch/variant; triage by diffing the region against
   canonical.
3. **Second loop-hook variant (~162, `loop_site_unknown` site bytes
   `c8 20 4d` = INY/JSR $..4D).** Like the $1042 hook but a different
   helper address; generalize the loop probe to accept any JSR whose
   target matches the 7-byte hook signature, OR decode the hook to find
   the loop-target semantics. + smaller site variants (`8d 9d 17` 15,
   `7e 18 ea` 12, ...).
4. **nonstandard_vectors (~1184).** init/play not at $1000/$1003 —
   relocated members; needs the load-addr-relative operand probe
   (most are probably canonical code at a different base).
5. **dual_parity_leftover (486) — FIXED this session** (params.slide_phase).
6. **offtable_live (errors, ~200).** wave-freq offset or note>95 reads
   land on the LIVE state block ($1707+k for k≥17 or the track-ptr
   slots k≤5). Consistent sub-buckets k=[159] (18), k=[30] (18),
   k=[0] (14): worth checking whether $1707+k is a stable-zero byte
   that the composer window could extend to cover, vs genuinely live.
7. **wave n=0 (56) — FIXED this session** (marker-chain slice start).
8. **`sector at $0000 never ends` (9).** tune-pointer record reads a
   $0000 voice pointer — member declares more subtunes than it has
   data for, or the tunetab operand probe is off for these. Guard +
   investigate.
9. **partial (140).** factory-passing but writelog diverges — the true
   long tail; bucket by first_diff signature (carried in the jsonl).

## Documented residue — the dual-effect FREQ GENERATOR (Taurus_02, 2026-07-06)

**`dual_freq_generator` + `dual_gen_steps` params (renamed from
`dual_hack`/`dual_hack_steps`; ledger C19 4th occurrence, C7-(b)
document-and-minimize decision, user-ratified 2026-07-06).**

Taurus/Taurus_02.sid — the ONLY carrier in all 10,676 DMC members — byte-edits
the dual ($40) odd-parity path: the `LDA $172F,x` opcode is patched BD→A6
(`LDX $2F`; zp $2F=$A9 under the PSID environment), so every subsequent
per-voice `,x` read lands +$A9 past the state arrays onto fixed CODE bytes.
Net audible behaviour: ONE global free-running pseudo-random freq ramp on dual
frames (the "accumulator" self-modifies two tune-setup code bytes whose
file-image values seed it; the update ORs a BASIC ROM byte and rotates a
feedback byte via an illegal RRA) + fixed PW/ctrl from code bytes + a pwphase
clobber that drives the pulse-speed fetch off the instrument record.

Representation status (why this is residue, deliberately NOT schema):
- `factory._dual_freq_gen_probe` (static wedge-anchored regex) captures the 9
  write-determining constants → `dual_freq_generator` param; the composer
  emits the generator as CLEAN legal code (ror+adc = RRA; the BASIC-ROM bytes
  are environment constants, same category as zp $2F=$A9). Default
  byte-identical; verify FULL 86118/86118.
- `dual_gen_steps` = the static bytes the clobbered pulse fetch reads past the
  record (C2 class, same as offtable_freq but for pulse speeds). Derivability
  CHECKED and unavailable (inst-6 raws land past the table end in the wavectrl
  region, whose layout is not in USF for this member) → justified-minimal
  capture (2 entries).
- The "lift to a musical form" direction (e.g. a `law: random` enum) is a §8
  TRAP recorded in ledger C7: the enum value would not determine the write
  stream — the chaos generator would become hidden composer mechanism; putting
  its arithmetic in USF is Pole B. The param transcript is the maximally
  principled form for chaos content: all determining constants in USF, one
  fixed mechanism in the composer.
