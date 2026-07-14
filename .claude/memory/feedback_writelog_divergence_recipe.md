---
name: feedback_writelog_divergence_recipe
description: "CHECKLIST. For writelog-partial debugging (the rebuilt SID's writelog matches the HVSC original up to position N, then diverges) — the principled investigation protocol. Skip these steps and the session takes 5x longer (Cyb II sub 0 pulse_run lesson)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

When a rebuild has a partial writelog match (e.g. `verify_featuredriven`
reports `match=X` of `Y`, X < Y), follow this protocol. Do NOT start
from py65 state traces, prior task descriptions, or guesses about what
"feels wrong" — start from the writelog stream itself.

## Step 0 — Ask the three questions OUT LOUD before any tooling

In the order you'd encounter them when starting work on a family:

1. **Engine-family docs?** — `pipelines/<family>/docs/`. This is the
   FIRST thing acquired when work begins on a new player family (via
   the `research-player` skill). Format specs, player manual (e.g.
   `wiki_fc_v41_manual.md`), CSDB release notes, lineage,
   reverse-engineering reference material. ~47 family-doc dirs exist
   today. If a family-doc dir exists, read it BEFORE per-SID work.

2. **Full decompilation?** — `pipelines/<family>/<engine>/disassembly.s`.
   Hand-annotated full-engine disasm with structural labels (`L_7DCA`,
   `sub_7DBD`, etc.) — info py65 cannot reconstruct. READ before any
   py65 fragment-disasm work.

3. **Per-engine RE notes?** — `pipelines/<family>/<engine>/RE_NOTES.md`.
   State-byte assignments (`$90DA = wavecount`,
   `$90F6 = counter2`, etc.), per-frame flow narration, prior-session
   findings, known partial-cause analysis.

The Hawkeye sub 6 worked example (2026-06-06): a multi-hour session of
wrong hypotheses (+$20 shift, tonesweep, drum #3, $7E5D tone-arp) all
came from reading raw py65 disasm fragments WITHOUT consulting the
existing 1051-line `disassembly.s` + 608-line `RE_NOTES.md` (plus
~20 family docs in `pipelines/future_composer/docs/`). Once consulted,
the right answer (drum-path glide at `$7F42-$800E`) was identifiable
in 5 minutes. Full context in
[[feedback_check_existing_engine_docs]].

Do NOT skip Step 0. Confidence in wrong hypotheses came from "looks
plausible from this fragment" — fragments without structural context
yield confident guesses that are guesses nonetheless.

## Step 1 — Get the exact first divergence (one command)

```bash
python3 tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N
```

Output gives you:
- Position in the flat (reg, val) stream where orig and rebuild diverge
- Frame number + cycle within frame for both
- The exact register + voice + role (e.g. "V2 freq hi")
- Orig value vs rebuild value
- Context: ±N writes around the divergence

This collapses what used to be a 30-minute custom-script-writing
exercise into a single command. **The output names the bug location;
the rest of the session is just understanding and fixing it.**

## Step 1b — If the divergence likely traces to engine state, use state_diff (with a caveat)

If the bug looks like "rebuild's pattern position / counter / flag is
off, not just one effect's output" (Hawkeye sub 1 V2 pattern-dispatch
type bugs), reach for `tools/state_diff.py` instead of py65.

**Always auto-generate the state map** — hand-crafting addresses bites:

```bash
# 1. Generate map (joins per-engine annotation with composer xa65 labels)
python3 tools/state_map_gen.py --engine ENGINE --voice {1,2,3,all} \
    --output /tmp/map.py
# 2. Run state_diff
python3 tools/state_diff.py ORIG.sid REBUILD.sid \
    --map /tmp/map.py --subtune N --duration S
```

`pipelines/future_composer/<engine>/state_map.py` declares the orig→
composer label mapping for each engine. If a state label you need isn't
there yet, add it (it's a small Python file). DO NOT manually build
state map files — wrong addresses are easy to introduce and the tool
won't catch them.

Internally uses `siddump --memwatch HEX,HEX,...` which snapshots RAM at
chosen addresses per-frame (libsidplayfp-accurate — NOT py65). Output
is "first frame where any mapped pair diverged + which pairs + Trap C
check via |P:<count> play() invocation count."

Why this matters: py65 silently disagrees with libsidplayfp for some
engines (Hawkeye especially) because it doesn't model CIA timing the
same way. `siddump --memwatch` uses libsidplayfp ground truth.

### CAVEAT — match memwatch duration to verify duration

`siddump --memwatch ADDR --duration T` captures state up to time T. If
T < the writelog_capture duration, the state shown is at a DIFFERENT
engine-state moment than the divergent frame `find_first_divergence.py`
reports — *the song hasn't yet progressed to the divergent state*.

`verify_featuredriven` uses `per-subtune-songlength × 1.1 + 1s` margin.
ALWAYS pass that same value as `--duration` to siddump for memwatch.
A 15s capture for a 110s divergent frame shows STALE state from a
completely different point of the song — and the analysis built on it
is fiction (Hawkeye sub 6 worked example: a 15s capture put V1 on
wave-program step 21 / drum, while the 110s capture put V1 on step 25
/ tone_arp+vibrato — these are completely different effect paths).

### CAVEAT — state_diff produces HINTS, not verdicts (Trap C)

`siddump --memwatch` captures RAM at the end of each `engine.play(19688)`
call. PAL VBI is 19656 cycles. The +32 margin (in `siddump.cpp`) means
each siddump "frame" processes usually 1, sometimes 0, sometimes 2 PSID
`play()` invocations. State sampled at siddump-frame N is NOT
necessarily what the engine had after IRQ N.

Hawkeye sub 10 burned a chunk of one session on a `nootcount[V1]`
"divergence" at f277 that turned out to be IRQ-count drift: orig's
`$90F6` per-frame counter was frozen at f278 (0 IRQs in that siddump
frame). The engines were equivalent under Mode 1; only the siddump
sampling was misaligned.

**Always cross-check state_diff's localization against
`find_first_divergence.py` (writelog ground truth).** If writelog
matches at the state_diff "divergence" frame, you're in Trap C —
ignore the state hint. See [[feedback_verification_modes]] for the
full framing.

## Step 1c — Specialised tools for narrower questions

When the divergence has a specific shape, reach for the targeted tool
instead of the general writelog. Each is in
[`tools/INVESTIGATION_BACKLOG.md`](../../tools/INVESTIGATION_BACKLOG.md)
under "Built (active)" with use cases.

- **`tools/voice_writelog.py SID --voice {1,2,3}`** — filter writelog to
  a single voice + auto-attribute each write to the likely engine
  routine (nolengset/pulse_prog/glide/etc). Use when "which effect
  produced this write?" is the question. Supports `--diff-against
  OTHER.sid` for side-by-side.
- **`tools/pattern_stream_decode.py SID --addr HEX`** — decode FC
  pattern stream bytes ($Cx wave/inst, $Fx markers, glide triples, etc.)
  as readable command list. `--seq` for seq stream mode. Use when "what
  byte does the pattern stream actually contain at this offset?" is the
  question. Sub 1 V2 F0/F1 chain bug was confirmed in one glance with
  this tool.
- **`siddump --memwatch-on-write TRIG ADDRS`** — event-driven RAM
  snapshot. Captures the listed RAM addresses every time the CPU writes
  to TRIG. Use for SMC behavior + "show me the engine state at every
  $D404 write." Hawkeye sub 10 drum-kick localisation went from an hour
  of py65 trace to ~5 minutes with this.
- **`siddump --writelog-per-irq`** — IRQ-aligned writelog. Each `|I:`
  chunk is exactly the writes that occurred during ONE PSID `play()`
  invocation. Kills Trap C from observation. Use when comparing
  writelogs from engines that drift IRQ-count across siddump frames
  (Hawkeye sub 10 was the worked example). Implies `--writelog`.
- **`tools/effect_chain_profiler.py SID --subtune N --frames F1-F2
  [--register HEX]`** — attribute each SID write to its CPU PC.
  Cross-references writelog + pc-trace. Answers "which routine wrote
  this $D408 = $47?" in one command. The Hawkeye sub 1 V2 freq hi
  divergence would have been 5 minutes instead of 30.
- **`tools/pattern_stream_verify.py --engine ENGINE` (or `--all`)** —
  sanity check, not an investigation tool. Run BEFORE diving into a
  writelog divergence to confirm the extract/compose pipeline isn't
  the culprit: verifies orig and rebuild pattern bytes match (with
  `featuredriven_addr_shift` accounted for via the pointer fixup).
  If this fails, the bug is in the data emission path, not the engine
  code emission path — different investigation entirely.

## Step 2 — Read the orig's effect code for that register

Disassemble the orig SID's code that writes the diverged register
near the diverged frame. Use:

```python
PYTHONPATH=tools/py65_lib python3 ... # disassemble orig $XXXX-$YYYY
```

Or for the FC family, search the HVSC asm source if available; or
seed a fresh disassembly with `tools/seed_disassembly.py`.

The effect is usually identifiable from the register class:
- `V_ freq lo/hi` writes → glide, vibrato, fx_drum, fx_pulse_run
  (sometimes, via shadow), nextvoice freq shadow
- `V_ PW lo/hi` writes → fx_pulse_prog, fx_pulse_run, nolengset
- `V_ ctrl` writes → nolengset (gate-on), h10/h11 (gate-off),
  fx_strange_filter (test bit), nextvoice late
- `V_ AD/SR` writes → nolengset (note attack), h11 (release tweak)
- `vol/filter mode` ($D418) → master vol fade, fx_filter_prog, fm2
- `filter cutoff` ($D415/$D416) → fx_filter_prog, fm2 cleanup,
  fx_strange_filter

## Step 3 — Diff orig's effect code against the composer emitter

Find the matching `_emit_fx_*` function in
`pipelines/future_composer/composer_asm.py` (or
`pipelines/composer.py` for Hubbard '85).

**For mechanical side-by-side**, use
`tools/disasm_diff.py --orig SID --orig-range HEX-HEX --composer FILE
--composer-label LABEL`. It auto-extracts the asm string from `_emit_*`
functions and pairs lines by mnemonic. It's a visual aid — read both
columns yourself, don't trust the pairing for semantic equivalence.

**Look for these specific bug patterns** (the Cyb II pulse_run fix
hit both at once):

| Pattern | Symptom | Example fix |
|---|---|---|
| State alias | Composer reuses one state byte for two effects; orig keeps them separate | Cyb II pulse_run: added `pulserun_acc`/`pulserun_hi` separate from `pulsestolo`/`pulsehisto` |
| Conditional write | Composer skips a shadow write under a branch; orig writes unconditionally | Cyb II pulse_run: orig `$AD1F` writes `d403` always, rebuild only wrote on carry |
| Off-by-one | Counter compared with `==` instead of `>=` or wraps one cycle early | Various |
| Missing wrap | Composer's `cmp #$0F` / `eor #$08` wrap missed because of branch flow | Hawkeye `novoiceset` $C0+ re-dispatch |
| Shared-scratch order | ZP scratch reloaded per voice; if order differs from orig, side effects diverge | Various per-voice loops |

## What NOT to do (lessons from the Cyb II session)

- **Don't start from the prior task description.** Task descriptions
  go stale: "V3 PW drift" in task #76 turned out to be V1 PW
  (writelog regs 2/3 = $D402/$D403 = V1, not V3). Verify the voice
  from the writelog itself.
- **Don't reach for py65 traces first.** [[feedback_py65_misses_dispatch_bugs]]
  applies here too: py65 showed "V1 PW values match every frame,"
  hiding the fact that the *sequence* of writes diverged. Only
  `siddump --writelog` is the verdict.
- **Don't rederive state addresses by reading the asm source.** The
  xa65 `-l` label dump gives a definitive map in one command:
  ```bash
  tools/xa65/xa/xa -M -l labels.txt -o out.bin source.s
  ```
  Then `grep '^pulserun_hi,' labels.txt`.

## Reg → voice cheat sheet

This bites every session. Pin it.

```
$D400-$D406   regs 0-6     V1 (lo,hi,PWlo,PWhi,ctrl,AD,SR)
$D407-$D40D   regs 7-13    V2
$D40E-$D414   regs 14-20   V3
$D415         reg 21       filter cutoff lo
$D416         reg 22       filter cutoff hi
$D417         reg 23       filter res / voice route
$D418         reg 24       vol / filter mode
```

`siddump --writelog` and `compare_instruction_stream` both use
`reg = $D4xx - $D400`. Reg 2/3 = V1 PW, not V3. Reg 14-20 = V3.

## Related

- [[feedback_ground_truth]] — sidplayfp/writelog is ground truth
- [[feedback_observation_drift]] — siddump's per-VBI bucketing is
  observation, not what the chip sees
- [[feedback_sid_hidden_state_write_order]] — within-frame order is
  audible; comparator cannot be relaxed to multiset
- [[feedback_deconstruct_not_reproduce]] — CORE TENET: target is
  the writelog stream, not orig's code structure
