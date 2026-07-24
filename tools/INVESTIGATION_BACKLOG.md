# Investigation tooling backlog

Durable list of diagnostic-tool ideas + ROI estimates. The premise: the
analysis pipeline is the long pole, not the code. A tool that saves 20
minutes per investigation pays back enormously across the migration
roadmap.

**Discipline:**
- After each non-trivial debugging session, ask "what tool would have
  collapsed this to <5 min?" Add it here (with rough estimate) or build
  it if it's <1 hour.
- If a tool starts producing misleading output, MODIFY or REMOVE it.
  Bad tools (silent failure, wrong-by-default, broken assumptions) cost
  more than no tool.
- When you build or modify a tool, update CLAUDE.md + the relevant
  memory so the next session knows it exists.

## Built (active)

| Tool | Use case | Memory pointer |
|---|---|---|
| `tools/find_first_divergence.py` | Locate first (reg, val) mismatch in writelog between orig + rebuild. Names voice/role. | [feedback_writelog_divergence_recipe](.claude/memory/feedback_writelog_divergence_recipe.md) |
| `tools/divergence_census.py` | RESIDUE TRIAGE for a wide family: census a batch jsonl by status+reason, then cluster detect-rejects (live first-divergence site) or verify partials (`--partials`, by first writelog reg/role) into ranked root-cause buckets w/ representatives. Automates stratify-by-first-diff. Wired: dmc_v5. Proved detection≠FULL. | [reference_divergence_census](.claude/memory/reference_divergence_census.md) |
| `siddump --memwatch HEX[,HEX...]` + `\|P:<count>` | Per-frame RAM snapshot at specific addresses + per-frame PSID play() invocation count (Trap C diagnostic). libsidplayfp-accurate (ground truth, not py65). | (in this file + CLAUDE.md) |
| `tools/state_diff.py` | Wrapper around `--memwatch`: takes orig+rebuild SIDs + an address-mapping file, finds first frame where any mapped pair diverges. Detects Trap C via IRQ-count delta. | (in this file + CLAUDE.md) |
| `tools/state_diff.py --on-write TRIG --align-value VV` | EVENT-ALIGNED state diff (Trap-C-free): snapshots at every write to TRIG, compares by global event index. For engines writing a fixed reg once per play() (standard FC: D418/1F). "writelog diverges + state matches" = a missing/extra effect EMISSION. Found Entrail's +$04 arp. | (in this file + CLAUDE.md) |
| `siddump --memwatch-on-write TRIG ADDR[,ADDR...]` | Event-driven RAM snapshot — on every CPU write to TRIG, snapshot the configured RAM addresses. For SMC / conditional-update traces. The address list is ONE comma-separated argument; siddump hard-errors on unrecognised args (2026-07-23 — the old legacy-positional catch-all turned a space-separated list into `--subtune 1708` and dumped a plausible wrong answer). `--subtune` is 1-BASED. | (in this file) |
| `tools/voice_writelog.py` | Filter writelog to one voice's writes + auto-attribute each write to the likely engine routine (nolengset / pulse_prog / glide / etc.) | (in this file) |
| `tools/pattern_stream_decode.py` | Decode FC pattern stream bytes as readable command list ($Cx wave/inst, $Fx markers, glide triples, etc.) Both pattern and seq streams. | (in this file) |
| `tools/state_map_gen.py` + per-engine `state_map.py` annotations | Auto-derive state_diff map files from xa65 labels joined with per-engine state-address annotations. `--engine ENGINE --voice {1,2,3,all}`. | (in this file) |
| `tools/disasm_diff.py` | Side-by-side compare orig disasm region vs composer emitter. Auto-extracts the asm string from `_emit_*` functions. Visual aid for spotting structural differences during recipe step 3. | (in this file + CLAUDE.md) |
| `siddump --writelog-per-irq` | Emits the writelog stream bucketed PER PSID `play()` invocation (one `\|I:` chunk per IRQ). Kills Trap C at the source. Implementation: c64cpubus hooks the play vector entry via cpuRead, records PHI1 cycle, siddump splits the writelog by these cycle markers. | (in this file + CLAUDE.md) |
| `tools/effect_chain_profiler.py` | Attribute each SID write to its CPU PC. Reads the store instruction's PC DIRECTLY off siddump --pc-trace (PC + A/X/Y + resolved `[d4xx]` effaddr on each line); groups by play() via cycle gaps. Outputs "$D408=$47 written by PC $831D" per write. (Rewritten 2026-06-28: the old cycle-reconstruction `frame*19688+rel` version was Trap-C-broken and mis-attributed every write to the PSID driver spin loop $04A5.) | (in this file + CLAUDE.md) |
| `tools/pattern_stream_verify.py` | USF roundtrip check for the pattern-stream region. Verifies orig vs rebuild bytes match, accounting for `featuredriven_addr_shift` and pointer fixup. Catches data-emission regressions early. | (in this file + CLAUDE.md) |
| `tools/usf_corpus_check.py` | Can the CURRENT grammar still read every stored `.usf`? Parses all 11,943 in ~9 s, groups failures by cause + DMC family, exits 1. Closes a blind spot regression cannot see: it builds from a ~116-member portfolio, so a schema change can orphan thousands of stored artifacts while staying green (1,182 = 9.9% did, 2026-07-21). RUN AFTER ANY grammar/parser/writer/types CHANGE. | ledger [C20](../docs/ledger/C20.md) third layer |
| `tools/seed_disassembly.py` | Generate a labelled disasm from a SID's binary as the starting point for hand-annotation. | (migrate-hubbard-engine skill) |
| `tools/taint_source.py <sid> <LO-HI> [--all]` | GREY-BOX CLASSIFY an OFF-TABLE read: is its source RAM region STATIC (never written during play → REPRESENTABLE, capture the value/program) or DYNAMIC (written → hard residue)? Uses `--memtrace` (per-ACCESS, within-frame-complete — a per-frame `--memwatch` snapshot misses a write-then-restore inside one play()), tracks distinct values per address (a read never changes a byte, a write does). Runs ALL subtunes by default. WHEN: an off-table read is the first flat-stream divergence and you must decide fix-the-capture (static) vs accept-residue (dynamic). Validated: Jupiter41 $23A3-24BB STATIC (→ first family-4 FULL); accumulator $182A-1832 correctly flagged DYNAMIC. LIMIT: an observation over played code paths (bounded 45s window by default), not a proof over unexercised branches. Ledger C2. | (ledger C2 + this file) |
| `tools/dmc_canon_diff.py [--status JSONL] [--csv]` | A-PRIORI WEDGE ENUMERATOR for a canon-player family: linear-align each member's reachable player code to the canonical player binary + diff OPCODES and in-player OPERAND-REPOINTS, Δ-mode-filter bulk state/table relocations, cluster by canon site, tag handled/NEW, and split each cluster into partial/full carriers (`--status`). The proactive complement to the reactive `_*_probe` detectors + a completeness audit of their true carrier counts. Proved DMC family-1's wedge space is ~fully handled: of 188 partials, 78% carry NO code wedge (off-table/CIA residue), 17% a handled wedge, only 9 (4%) a genuine unhandled patch — all singletons. LIMIT: misses immediate-value tweaks + re-assembled members (linear-align only). | [reference_dmc_canon_diff](.claude/memory/reference_dmc_canon_diff.md) + CLAUDE.md |

## Backlog (not built yet)

| Idea | Use case | Rough ROI | Build estimate |
|---|---|---|---|
| ~~**`dmc_offtable_probe` divergence-proximity gate**~~ **DONE (r116, 2026-07-24).** | The probe now pc-traces only a ±3-frame window around the divergence (per-irq play index converted for CIA tunes) and reports every proximate candidate; a value found only outside the window is reported as "NOT an off-table read at the divergence" with the far matches labeled by-value coincidences. Validated: Fantastic_Dreams (3 near candidates incl. the wavepos class), Long_Time (correct bow-out where the old scan would have blamed idx 140). Historical mis-fires: 6 (wavepos 3×, Real_Hardcore idx 150, r111 Rock_Tec_Tec idx 150, Psycho_One $172A). | — | done |
| **Ledger-discipline hook** (process, not diagnostic) | A `UserPromptSubmit`/`PostToolUse` hook that nudges the CONSULT/RECORD reflex structurally (e.g. remind to check the in-context ledger before a fix lands, or flag a commit that solved a non-trivial problem with no ledger delta). Today the whole ledger discipline is manual (CLAUDE.md + feedback_convergence_ledger). The full-import (2026-07-14) attacks the CONSULT side; RECORD-on-commit remains unenforced. | Medium — the discipline mostly holds; this closes the tail. | 1-2 hours hook scripting |
| **`siddump --memwatch` at IRQ boundaries** (the unbuilt half of play-aligned) | The writelog half is BUILT (`--writelog-per-irq`, see Built section). Remaining: let `--memwatch` snapshot at PSID `play()` entry instead of siddump frame boundaries, so `state_diff.py` sheds its Trap C caveat and becomes a verdict-grade tool (see Hurt list). `--memwatch-on-write TRIG` already covers engines with a once-per-play write — this closes the general case. | Medium-high — state_diff stays hint-only until then. | 1-2 hours libsidplayfp overlay |
| **Parameterize `dmc_canon_diff.py` by family descriptor** (for family-2) | The a-priori wedge enumerator is hardcoded to family-1 (canon binary `dmc4_player_embedded_1000.bin`, the `JMP base+$1D/+$85` JT signature, `_KNOWN_SITES`, fixed-table addrs). Add a family descriptor `{canon_binary, jt_signature, fixed_table_addrs, wedge_site_map, member_list}` (the `divergence_census` `ENGINES`-registry pattern) so family-2/3 = one entry, not a fork. Family-2's canon binary already exists (`pipelines/dmc/docs/dmc4_family2_player_1000.bin`). RUN IT EARLY on family-2 — it is LESS mature (~2507/2889) so likely has MORE unhandled wedges; the family-1 "wedges ~fully handled" finding does NOT carry over. | High — gives family-2's a-priori wedge accounting up front instead of grinding one-at-a-time blind. See [reference_dmc_canon_diff](.claude/memory/reference_dmc_canon_diff.md). | 1-2 hours when family-2 starts |
| **Composer-symbolic data layout** (PARTIAL — Phase 1 done) | Phase 1 (commit 4740472-followup): SFX-init hardcoded `$8475`/`$8FC5` → symbolic `pattern_ptr_table+$6C` / `sfx_seq_stream` (new cfg field). All currently-FULL subs preserved. Phase 2 (TODO): activate `featuredriven_addr_shift` with pointer-fixup for the verbatim tail's pointer tables (`pattern_ptr_table`, `drumtabel`, `filterbytes`, `arplo`/`arphi`, music subtune templates' seq pointers at `$7B0E+`). When done: flip Hawkeye to `noise_tick_style='hawkeye_constants'`, fix sub 10. | High — Phase 2 still blocks Hawkeye sub 10 noise-tick. | Phase 1 done in 30 min. Phase 2 still 1-2 hours of refactor. |
| `tools/voice_writelog.py` | Filter writelog to one voice; auto-attribute writes to likely effects (AD/SR write = nolengset; freq-only = glide; etc.) | Saves 10-15 min/session on "which effect produced this write?" | 30 min |
| `tools/pattern_stream_decode.py` | Given (SID, engine config, subtune, voice), decode pattern stream as human-readable command list | Saves 30-60 min/session on pattern-dispatch bugs | 1-2 hours, engine-specific |
| `tools/disasm_diff.py` | Side-by-side compare orig disasm region vs composer emitter, with state-name alias substitution | Saves 15-20 min/session on effect comparisons | 1-2 hours |
| State map generator | Auto-derive orig↔rebuild address map from xa65 labels + a per-engine annotation file (so state_diff.py becomes one-shot) | Saves 5-10 min/session and removes a footgun (wrong manual maps) | 1 hour, ongoing per-engine annotation |
| `siddump --memwatch-events` | Snapshot RAM addresses on a CPU event (PC enters range), not per-frame. For tracing when state changes mid-frame. | Very high for SMC and conditional updates | 1 hour C++ |
| `tools/effect_chain_profiler.py` | Attribute each `$D4xx` write to the routine that produced it (via PC-trace cross-reference). Output: "$D408 = $47 written by nolengset at PC $7CXX." | Definitive answer to "which routine produced this write." Saves ~20 min/session. | 2-3 hours |
| Pattern-stream USF-vs-binary verifier | Verify USF's extracted pattern stream byte-matches what the engine would have read from HVSC's binary | Catches USF extraction bugs at extract time, not rebuild time | 1 hour per engine family |

---

**BACKLOG STATUS (final sweep — all items resolved):**

| Item | Status |
|---|---|
| `siddump --play-aligned` / `--writelog-per-irq` | BUILT (commit ca1623f). Per-IRQ writelog bucketing eliminates Trap C at the source. |
| Composer-symbolic data layout | BUILT (commit 09742c7). Phase 1 + 2. Hawkeye 11/12 FULL. |
| `tools/voice_writelog.py` | BUILT (commit 7bb6abe). |
| `tools/pattern_stream_decode.py` | BUILT (commit 7bb6abe). |
| `tools/disasm_diff.py` | BUILT (commit 6db2726). |
| State map generator | BUILT as `tools/state_map_gen.py` (commit 0bdc98e). |
| `siddump --memwatch-events` | BUILT as `siddump --memwatch-on-write` (commit 8bc8d0f). |
| `tools/effect_chain_profiler.py` | BUILT (commit 9ec3509). PC-attributed write log. |
| Pattern-stream USF-vs-binary verifier | BUILT as `tools/pattern_stream_verify.py`. |

**Backlog cleared.** Add new entries above as future sessions surface
tools that would have saved time.

## Hurt list (built tools that didn't earn their keep — to be modified or removed)

| Tool | Why it hurt | Resolution |
|---|---|---|
| `tools/state_diff.py` (mitigated, not removed) | Misleads when siddump frame buckets are misaligned with PSID `play()` invocations (Trap C). Hawkeye sub 10 session: reported a `nootcount[V1]` "divergence" at f277 that turned out to be IRQ-count drift — orig had 0 IRQs in that siddump frame. Real bug was elsewhere. | KEPT — still useful for HINTS when cross-checked against writelog. Added explicit caveat in docstring + runtime warning in output. Permanent fix: build `siddump --play-aligned` (PRIORITY in Backlog above) so memwatch samples at IRQ boundaries. Until then: any state_diff "divergence" MUST be cross-checked against `find_first_divergence.py` before trusting. |

When entering: write what the tool was supposed to do, what it actually
did (silent failures, wrong defaults, etc.), what to do (delete? fix?
add a tripwire?).

## Process rules

- **Every entry in "Backlog" should have a session that wanted it.** No
  speculative additions. Examples: "If we'd had X, the Hawkeye sub 1
  V2 freq divergence would have taken N minutes instead of N hours."
- **Every entry in "Built" must point to its memory / CLAUDE.md home.**
  If a future session doesn't naturally find the tool, it might as well
  not exist.
- **Promotions and demotions happen here.** When a backlog idea gets
  built, move to Built. When a Built tool hurts more than helps, move
  to Hurt list with the reason.
