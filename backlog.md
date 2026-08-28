# BACKLOG — the SIDfinity OPEN-WORK list (pruned 2026-08-21)
#
# TRACKED IN GIT since 2026-08-24. It previously lived in the gitignored
# scratch dir — one `rm -rf tmp` from gone, and it is the only record of a
# dozen measured-but-unfinished investigations. Moved to the repo root and
# tracked for exactly that reason.
#
# Done items get DELETED from here. Numbers stay stable across prunes
# (gaps are deliberate) only because other files cite them: project_dmc.md
# cites item 6 (DELETED 2026-08-21 — family-2 closed at 2,924/2,924, see
# project_dmc.md head + ledger C9 10th occ), cleanup_plan cites items 10 + 11.
#
# Items 19-21 need an OWNER DECISION (representation / schema); the rest are
# unfinished work that needs no permission. Items 22 + 24 also need an OWNER
# DECISION, but NOT on representation: 22 is a decision about COST (landing it
# re-invalidates every DMC verdict and forces a ~13 h re-batch), and 24 is a
# fork where the two possible causes need opposite actions.

5. REGISTRY REVIEW FLAGS (found by the first composer_param_lint runs):
   - digi_player (pipelines/composer.py): RE-ASSESSED 2026-08-16 — not
     "borderline §7", it meets §8's test exactly: the composer's choice
     of which 6502 to emit depends on USF content (params['digi_player']
     -> _digi_player_registry()[name] -> assemble_chimera_digi_player;
     the error message even says "register in _digi_player_registry").
     The registry note's C7-category-C justification is WRONG — C7-C
     covers the PCM sample data (FLAC sidecars, fine), not the player
     choice. LATENT, not active: a library of one (1 corpus carrier,
     4k-era Chimera; 1 registry entry). DECISION (owner-reviewed): do
     NOT design the parametric form from one example — speculative
     generality. TRIPWIRE instead: the SECOND digi engine migrated
     (e.g. Galway $D418 4-bit) must PARAMETRIZE (a real technique enum
     like `digi { technique: wavetoggle_1bit | volume_4bit, rate: N }`,
     composer synthesizes the player), NEVER add registry row two.
     DigiCode's addresses (dispatcher/player base) are composer layout
     and must not be reachable from USF even by name. Also: fix the
     registry note's false justification when next touching it.

# ============================================================
# (Items 9-14 were folded in on 2026-08-16 from an earlier handoff; the rest of
# that source was already done. Numbers kept as-is — see the no-renumber rule.)

9. #85 NEW/RECOVERED MEMBERS NOT YET SWEPT, per family (measured
   2026-08-09). "new" = absent from #84; "recovered" = present in #84 but
   only classified now (the sidid long-path truncation fix). Neither is a
   regression — they are members that were always there and are only now
   visible; each family's next batch picks them up naturally. The counts
   say how much tail to expect.

     SWEPT since:  DMC 116 (f1+f2 batches, Aug 11/15)
                   Basic_Program 38 (Aug 12 re-baseline)
                   NIGHT SWEEP 2026-08-18/19 (overnight chain, all three
                   full re-verifies under current code — today's schema
                   commits had invalidated every cached row; 0 REGRESSIONS
                   in all three, diffed vs tmp/*.pre85sweep.jsonl):
                     Music_Assembler   138 new -> 4,021 FULL (+106; 104 of
                       the new members FULL, 19 partial, 15 unsupported)
                     MoN/FC            114 new -> 2,604 FULL (+73; 72 new
                       FULL, 37 flagged/out-of-scope, 4 partial, 1 error:
                       DEMOS/UNKNOWN/New_Sound.sid — init never returns
                       under py65 (C9 class), residue lead)
                     GoatTracker_V1     28 new ->   168 FULL (+4)

     STILL NOT SWEEPABLE (no migration pipeline exists — counts are
     advance notice for when one is built):
       GoatTracker_V2.x     7,797         263 new +238 rec = 501
       Soundmonitor         3,682          44     + 38     =  82
       JCH_NewPlayer        3,687          13     + 67     =  80
       Rob_Hubbard            289 total — the 2 new/recovered need
         per-engine EngineConfigs (the Hubbard path is per-tune, not a
         wide batch). ✅ IDENTIFIED 2026-08-20 (both are truncation-fix
         RECOVERIES — the only Rob_Hubbard paths > 56 chars):
         - MUSICIANS/H/Hubbard_Rob/Geoff_Capes_Strongman_Challenge.sid
           (24 songs, load $1000): init head is EXACTLY the
           Thing_on_a_Spring compound idiom (`CMP #$08 / BCS / JMP
           $1000` + `SBC #$08 / JSR $100F`) = a TWO-sub-engine Hubbard
           '85 compound — ordinary migrate-hubbard-engine work, ToaS/
           5_Title_Tunes precedents apply.
         - MUSICIANS/H/Hubbard_Rob/Trans-Atlantic_Balloon_Challenge.sid
           (2 songs, load $0800, init $14F3, play $0809): init is a
           SMC-patching setup (LDA #$02 STA $0E20 / table copies into
           $0Dxx operands) — NOT the plain '85 head; needs a real
           disassembly pass before classifying.
         Migration itself deferred (full per-tune sessions).

10. E5 (Phase E) — ML-PROXY METRICS: token stats + engine-predictability of
    fields. "The eventual ground truth of the philosophy, not built now" —
    roadmap note only, never built. This is the LAST open box of Phase E
    (E1-E4 all landed: cardinality census, the escape-hatch mass ratchet,
    P3's interp probe, uready Phase 2 wiring).

11. G1 (Phase G) — FULL UREADY REVIEW: run `/uready-review all` (Phases
    1-3), which now includes the spec-lint check and, once E lands, the
    value matrix. Expected DMC-f1 outcome 6/6 PASS (criterion 4 was closed
    by Phase D). Its real output is the MOVE-1 DIVERGENCE DECISION LIST —
    known pending: DMC wave_table / SweepEnvelope vs FC threshold/segment
    programs.
    ⛔ DEFERRED INDEFINITELY by explicit user decision 2026-08-05 — DO NOT
    PROPOSE UNASKED. The plan's own Phase-G note says why: the cross-engine
    half's main output is the Move-1 decision list, which is not actionable
    until the grind saturates, while the mechanical layers (spec lint,
    censuses, interp probe) run standalone and carry the load between
    reviews. Opener if the owner lifts it:
    ▎ SIDfinity: I want to run the full uready review now, lifting my
    ▎ earlier indefinite deferral. Run /uready-review all and bring me the
    ▎ findings.

12. MOVE-1 PARKED QUESTIONS — parked until the grind saturates. The owner
    decides; NO automatic trigger (CLAUDE.md). Opener:
    ▎ SIDfinity: let's review the Move-1 parked items. Read
    ▎ docs/the_move-1_plan.md — walk me through the deferred decisions one
    ▎ at a time with recommendations.

13. AN IDEA raised 2026-08-07, never scheduled — vibrato's delay + ramp +
    width are three scalars describing ONE thing: how the wobble's depth
    changes over a note. Ledger C1 (a value swept over time) is that shape.
    Hypothesis, not a finding. Move-1 food. UPDATE 2026-08-16: now has a
    concrete home — the two-faced envelope candidate (generator face =
    shape/range/period/quantize/phase) noted in docs/the_move-1_plan.md
    under "D1/D2 candidate unified form"; vibrato depth is D4 there.

14. BASIC_PROGRAM RESIDUE LEADS — INVESTIGATED 2026-08-20 (diagnosis
    only, run during the DMC closeout; logs tmp/cascading_*.log). The
    two leads are ONE problem: the 3 image_too_big Bond_Alan loopers
    (Cascading 4:20 / Legion_of_One 2:43 / Pepper_Spray 1:59) include
    Cascading, the lost pw-sweep portfolio carrier.
    ROOT CAUSE (measured on Cascading at its honest 288s window): the
    lift explodes it to 7,665 sub-steps — each note's attack embeds an
    IDENTICAL per-note PW-HI staircase ($x0..$x7) on ALL THREE voices
    (the split materializes ~12 sub-steps/note), and because each
    note's ABSOLUTE sweep phase differs, the step signatures never
    repeat (579/627 unique even ignoring PW) -> _find_loop only closes
    at intro 7649 (no real fold) -> 7.6k records overflow $CF00.
    detect_modulation does NOT rescue it: _capture_pw_program is
    FREE-RUNNING-only and captured just voice 2; V1/V3's retriggered
    ramps stay materialized (verified: build_psid still image_too_big
    under the modulation rung). The old pre-honest-window FULL was
    brute materialization that happened to fit 120s.
    DESIGN (the principled fix, C1): represent the per-note PW ramp as
    an INSTRUMENT PWM program (SweepEnvelope, retriggered at note-on —
    the USF Instrument.pwm form the other families already use):
    (a) segmentation strips per-note PW writes that match a per-note-
        periodic ramp (detect: the PW subsequence of every attack is
        identical relative to note-on);
    (b) the note's instrument carries pwm SweepEnvelope(start, step,
        period) — likely ONE instrument for all notes here;
    (c) the player emits the ramp per note (a small per-voice pw tick
        in the play loop, like _emit_pw_mod_asm but note-retriggered);
    (d) with PW stripped, sigs collapse -> _find_loop folds a real lap
        -> image shrinks -> all 3 members + the pw-sweep portfolio
        dimension come back (as a BETTER typed carrier than before).
    Est. scope: a semantic_lift feature (strip + detect) + player emit
    + usf_roundtrip instrument wiring; roughly a Phase-1-per-note-
    instruments-sized change. Not landed (needed the DMC closeout to
    finish first only for CPU; basic_program's fingerprint is separate
    so it CAN land any time).
    Round detail in .claude/memory/project_basic_program.md.

# ------------------------------------------------------------
# tmp/cleanup_plan_2026-08-03.md is now CLOSED as a work list: its three
# open boxes are items 10 (E5) and 11 (G1) above; the third, H1, was
# ticked DONE 2026-08-16 with its evidence recorded in the plan file, and
# the boxes there point back here. Keep the plan file for its Phase A-I
# HISTORY (what was done, when, and why); do not re-open work from it.
# THIS FILE is the open-work list.

# ============================================================
15. HUBBARD x DMC-TECHNIQUES ANALYSIS (2026-08-20, requested during the
    f2+f1 closeout; measurements in tmp/hubbard_cluster*.log). Question:
    which of the levers industrialized during the DMC grind would change
    the Hubbard picture? Answer: nearly all of them — Hubbard is where
    DMC was pre-factory, and its population is bigger than assumed.

    THE POPULATION (measured): 289 Rob_Hubbard-classified members; only
    12 engines / ~72 subtunes migrated (the per-tune '85 path). A
    reloc-invariant play-body skeleton clustering (the FC/DMC
    fingerprint technique, run today) shows the unmigrated mass is NOT
    a long tail — it is THREE big generations:
      - "Sanxion generation" n=87, 0 migrated (Sanxion/Delta/Peppis_
        Quest + the remix ecosystem) — the mature '86-88 player. The
        single largest Hubbard lever, comparable to a small DMC family.
      - "'85 Monty/Commando generation" n=83, only 5 migrated — 78
        unmigrated members (demos/remixes on ripped '85 players) whose
        play body is >=50%-similar to engines OUR EXISTING '85 COMPOSER
        already serves. Cheapest yield: no new composer work, only
        extract/config industrialization.
      - "New_Tune_1 generation" n=16, 0 migrated (International_Karate,
        Kentilla, Proteus — the transitional player).
      - smaller: Action_Biker sub-gen (9, 5 migrated, 4 siblings free),
        After_8 late-'87 (6), Red_Hubbard (8), a JT-adjacent cluster
        (7 — check sidid misclassification: 'Tel_1.sid' is in it).
    At EXACT skeleton hash the same set fragments into 179 groups —
    Hubbard hand-tweaks his player PER GAME, i.e. the C19 wedge space
    is the NORM here, not the exception. That fragmentation is exactly
    what the DMC wedge machinery was built for.

    TECHNIQUE -> CHALLENGE MAP (ranked by expected yield):
    a. FACTORY + DATAFLOW LOCATE (dmc_v4_config/dataflow.locate): the
       Hubbard path's cost is the hand-written per-tune config.py +
       extract. Hubbard '85 data tables are per-tune addresses = the
       exact "packer-patched operand" problem dataflow.locate solves
       (project_dmc's KEY line). A hubbard factory for the '85
       generation (canon body = Monty/Commando) turns the 78 unmigrated
       '85-cluster members into a WIDE BATCH against the existing
       composer. This is the DMC f1 playbook verbatim.
    b. CANON-DIFF WEDGE ENUMERATOR (dmc_canon_diff pattern): with a
       canonical '85 body, enumerate every member's opcode/operand
       patches a-priori, cluster by canon site, and convert per-game
       tweaks into probed extra_params (C19 discipline) instead of
       today's per-engine hand-derived EngineConfig fields. The 179-way
       exact-hash fragmentation collapses into a knob census.
    c. BATCH HARNESS + code_hash rows + corpus_sync + divergence_census
       + batch_diff: Hubbard has NONE of the industrial residue
       machinery (no jsonl, no census, no sync/orphan discipline, no
       build_one). All of it is engine-parametric already; wiring costs
       days, pays on every generation.
    d. C6 OFFTABLE_FREQ TYPED RECORDS: Hubbard's signature quirks ARE
       the off-table class solved ad-hoc pre-ledger — Commando's "drum"
       = inst 4 played off the freq-table end
       (project_commando_no_drum_engine), and the notenum/freq overlap
       (cross-voice coupling via shared bytes) is state-as-data. The
       at()/live() record machinery + dmc_offtable_probe's method
       generalize; new '85-cluster members will hit these constantly.
    e. C18/C24/C9/C25 MULTISPEED MACHINERY: the Sanxion generation is
       HEAVILY multispeed (2x-4x CIA) — phase schedules, play_repeat,
       measured CIA latches, latch-fit costing. Monty's multispeed was
       done by hand pre-ledger; the '86 generation gets it as catalog.
    f. TRICHOTOMY INIT (C21): new generations need not reproduce their
       init verbatim — universal reset + typed priming + trichotomy
       compare kills a chunk of per-engine init RE (the '85 composer
       predates this; fine to leave '85 as-is, use for '86+).
    g. C31/C35 COMPILATION MACHINERY: 5_Title_Tunes predates C31 but is
       its precedent; Geoff_Capes (item 9, 24 songs, two sub-engines,
       ToaS idiom) rides the same unified-per-subtune-params path, now
       with the merge/per-player-fact catalog behind it.
    h. NATIVE-CAPTURE TOOLS (pc-watch/reinit-snapshot/memwatch lists/
       per-irq): engine-agnostic, usable today; the Hubbard-era
       sessions predate all of them.
    CAVEAT: sidid's 'Rob_Hubbard' bucket needs a hygiene pass first —
    the JT-adjacent cluster + fan/editor recreations (Red_Hubbard) are
    probably not Hubbard players; the fingerprint clusters themselves
    are the triage tool (engine-blind, C13: dispatch on the play body).
    SUGGESTED SEQUENCE if/when Hubbard resumes: (1) c's harness + a
    build_one, (2) a's '85 factory over the 83-cluster (existing
    composer!), (3) b's canon-diff census, (4) then the Sanxion
    generation as a NEW family via research-player + the full playbook.

# ============================================================
16. COMPANION x DMC-TECHNIQUES ANALYSIS (2026-08-20, follow-up to item
    15; measurements in tmp/companion_scan.log + this session's probes).
    Verdict: companion's situation is the OPPOSITE of Hubbard's — the
    population is CLOSED and essentially complete; what the DMC
    discipline exposes is VERIFICATION/CORPUS gaps, not migration mass.

    POPULATION (measured):
    - 'Companion' engine bucket = 26 members; 25 have stored .usf, the
      26th is C64_Music_Examples (migrated via its own c64me build path,
      15 subtunes ok in regression — artifacts stored under a different
      convention; check whether its .usf set exists for the ML corpus).
    - Sibling scan: a play-body 4-gram skeleton match (J>=0.5) of all 6
      companion strains against the 1,331 unclassified #85 members found
      ZERO hits — no hidden companion population anywhere in HVSC.
    - 'Companion/Jay_Derrett' label = 25 members, the ONLY open edge:
      17 wired in regression (10 psid + 4 typeb + 3 rsid; 15 ok + 2
      known-partial), 3 in-dir UNWIRED, 5 label-outsiders never touched.
      Kind-clustering of the un-covered 8 (measured today):
        - Traxxion: J=0.52 vs the psid kind (Ninja_Hamster) — closest to
          an existing pipeline kind; likely the cheapest wire-up.
        - Spindizzy_USA_Version + Space_Doubt (J=0.48 to Spindizzy) +
          Soundwave_Tubular_Bells (0.29): a probable FOURTH JD
          sub-variant cluster of their own.
        - Road_Warrior: matches no kind (unique variant).
        - Blade_Runner + Gun_Runner + Shao-Lins_Road: match NOTHING JD
          (J<=0.08) — the sidid label is suspect for them (or their
          RSID play=0 head defeats the skeleton; check init-side).
          C13/C20 rule: settle OWNERSHIP by play-body evidence before
          any artifact exists (the Polonaise NOT-MINE lesson).

    DISCIPLINE GAPS the DMC playbook closes (the real content here):
    a. JAY_DERRETT STORES NO CORPUS ARTIFACTS: its 15 verified members
       write only regression-side .sidfinity.sid; no .usf anywhere ->
       invisible to usf_corpus_check + the ML corpus. Worse, the build
       consumes pipelines/companion/jay_derrett/_extracted/*.json
       params (`params_from_extracted_json -> build_sid`) — on its face
       a SID->params->SID path that BYPASSES USF entirely
       (feedback_always_through_usf!). Either the USF leg exists
       somewhere I did not find (verify before acting) or this predates
       the law and is the corpus's largest silent representation hole
       relative to its size. NB the old "aperiodic by design" framing
       is NOT a mitigating factor: that conclusion was proven WRONG and
       reverted (commit 940a87af; the deprecated project_jay_derrett
       memory — the owner caught it via Soundwave_Tubular_Bells
       sounding like a normal orderlist engine; JD is an ordinary
       orderlist + SUBJUMP-command player). So the USF bypass is plain
       unfinished migration debt, and JD should be MORE tractable to
       bring through USF than its history suggests. Still owner-visible
       before acting (representation surface).
    b. VERIFY WINDOWS: the JD comparisons run at FIXED 6.0-second
       captures (regression.py _w_jd) — the exact C20 EIGHTH-LAYER
       weakness (ratified window = songlength x 1.1) that produced 44
       false FULLs in basic_program. The companion USF list should be
       audited for the same (its verify durations predate the
       ratification). A re-verify at honest windows is cheap (26 + 17
       members) and either confirms the verdicts or surfaces latent
       partials NOW rather than at Move 1.
    c. NO SYNC MACHINERY: companion/JD have no batch jsonl, no
       code_hash rows, no corpus_sync/orphan discipline, no fifth-layer
       audit. For a 46-member surface a full harness is overkill, but
       the corpus_sync PLAN/audit form (write+audit-from-disk) fits and
       would have caught (a) automatically.
    d. THE 2 KNOWN-PARTIALS ARE THE DIGI TRIPWIRE'S SECOND ENGINE:
       Trigger_Happy + Thundercross fail ONLY on the main-loop $D418
       volume digi — i.e. the volume_4bit technique. Item 5's
       owner-reviewed tripwire says the SECOND digi engine must
       PARAMETRIZE (`digi { technique: wavetoggle_1bit | volume_4bit,
       rate }`) instead of adding a registry row. Closing these two
       members IS that parametrization moment: Chimera's Mode-2
       cycle-strict machinery + C7-C PCM sidecars already exist; the
       missing piece is the typed technique enum (OWNER GATE — schema).
    e. Wiring the 8 un-covered JD-label members: the existing
       kind-dispatch (psid/typeb/rsid) is C13-shaped already; Traxxion
       probably rides psid as-is; the Spindizzy trio needs a fourth
       kind; Road_Warrior is a singleton dig; the 3 suspect-label
       members need ownership settled first (b/c above).
    SUGGESTED ORDER: (b) honest-window re-audit first (cheap, verdicts
    at stake), then (a) the JD-USF question to the owner, then (e)
    Traxxion + the Spindizzy trio, with (d) as the flagged owner
    decision it already is.

# ============================================================
17. ISOLATION vs SHARING / THE VERIFICATION APPARATUS — reviewed against
    the literature. Owner question 2026-08-22.

    ==== STATUS 2026-08-23: PILOT RUN, 7 OF 10 LANDED, AWAITING THE
         ADOPT/REJECT DECISION ====
    (owner decision 2026-08-22: run it on the DMC v5 grind. Owner
    direction 2026-08-22 night: "go all in — what would the pilot be if
    we didn't actually do the pilot?") The experiences are written back
    below; the six recording questions are answered where answerable.
    WHAT IS STILL OPEN IS THE DECISION: do these become general
    methodology? Nothing here has been declared project-wide.

      (a) toolchain + verdict inputs in the hash    ✅ 4f46e7af
      (b) cache epoch + per-row key components      ✅ 4f46e7af
      (c) DERIVED per-(engine,consumer) dep set     ✅ 4f46e7af
      (d) enforcement                               ◐ PARTIAL a0821f3d —
          the safe-fallback audit landed as a PRE-FLIGHT
          (`derive_deps --check`), because the in-batch form adds its own
          call site to the family's closure and so invalidates the very
          rows it protects. The other two properties (periodic
          unconditional full re-verify; shadow audit of cache HITS) are
          NOT done.
      (e) portfolio as a BUDGET + pinned witnesses
          + rotating random stratum                 ✅ e1c2995e, and
          wired for v5 as tier 1 (0e74141e) BEFORE the grind proper —
          which was the point of choosing v5.
      (f) pairwise / CCM extension                  ⬜ not started
      (g) FBDL measured                             ✅ 4ea7272e — and it
          is the most important number of the run (0/5, see below).
      (h) oracle strength by fault injection        ✅ 1da95402. It had
          been DEFERRED as "not a grind experiment"; it named a live
          defect on its first run, so that judgement was wrong.
      (i) exhaustive byte-identity manifest         ⬜ not started
      (j) corpus re-sync as its own commit          ✅ observed as commit
          policy all night; no corpus re-sync was needed.

    ⚠ ONE PILOT PREMISE WAS REFUTED, not confirmed: (c)'s stated
    re-measurement criterion ("a v5-only edit must leave v4 at
    8,369/8,369") is FALSE AS STATED — see recording question 1.

    WHAT TO RECORD (so the write-back is structured, not anecdotal):
      1. Did (c) actually decouple v4/v5? (Yes/no + the hash evidence.)
         ⇒ BASELINE MEASURED 2026-08-22, BEFORE any fix: editing ONE v5
           file (`pipelines/dmc/v5/verify_v5.py`, the C21 retry port)
           moved `code_fingerprint('dmc_v4')` and invalidated
           **8,369 v4 verdicts** — 5,445 f1 rows (re-established by a
           7-hour batch the same morning) + 2,924 f2 rows, to 0/8369
           current. The cost is now a number, not an argument. Re-measure
           after (c) lands: the same edit must leave v4 at 8,369/8,369.
         ⇒ SALVAGED the same day, and the salvage BUILT (c)'s prototype:
           ran the batch worker under a `sys.modules` snapshot to derive
           its REAL closure (55 repo modules), computed each family's
           delta from git since its rows were stamped, and asserted every
           delta file is ABSENT from that closure — then appended
           restamped rows carrying the old hash, the delta list and the
           evidence pointer (append-only, originals retained). 8,369/8,369
           current again, in seconds, licensed mechanically rather than by
           my judgement. Evidence: tmp/batch_closure.log +
           tmp/batch_used_set.txt.
         ⇒ ⚠ TWO REFINEMENTS (c) DID NOT ANTICIPATE, both measured:
           (i) THE CLOSURE IS PER-CONSUMER, not per-engine. The batch
               worker loads 55 modules; the regression harness's
               `verify_member` path loads 57 and INCLUDES
               `pipelines/dmc/verify.py`, which the batch never touches.
               A single per-family dependency set is the wrong shape —
               it must be per (engine, consumer).
           (ii) THE DECLARED SET IS BOTH TOO BROAD AND TOO NARROW. 18
               declared-but-unused files (all of v5 + all of v6 — the
               harmless part) and **42 USED-BUT-UNDECLARED**, including
               `src/composer_runtime/{xa65,psid}.py` (which EMIT THE
               BYTES), `src/songlengths.py` (the verify WINDOW — C20's
               eighth layer), `tools/seed_disassembly.py` (parse_psid),
               `tools/py65_lib/py65/*` (the 6502 interpreter that runs
               extraction probes) and `lark` (the USF parser, an
               unpinned third-party package). Today a change to the
               assembler, the header emitter, the verify window or the
               interpreter would move every family's output and
               invalidate NOTHING. That is the correctness bug, measured
               on our own code rather than argued from Bazel's docs.
      2. Did (a) ever fire — i.e. did a toolchain or window change
         invalidate rows that would otherwise have gone stale-silent?
      3. FBDL: N tier-2 regressions found, of which M would have been
         caught by tier 1. Report the fraction.
      4. Portfolio churn: how often did it need re-deriving, and did the
         budget form (e) ever pick a materially different set than the
         exact-minimum form would have?
      5. COST: wall-clock and human time the extra machinery added vs
         the re-verification it avoided. Be honest if it was a net loss.
      6. Anything the methodology MISSED — a regression that slipped
         through everything. That is the most valuable single datum.
    ⚠ WRITE THE EXPERIENCES BACK INTO THIS ITEM BEFORE GENERALISING.
    A recommendation that survived one real grind is evidence; one that
    only survived a literature review is a hypothesis.

    ==== ✍ WRITE-BACK #1 — 2026-08-22 night (a+b+c+d+h landed) ====
    Owner said "go all in on the pilot — what would the pilot be if we
    didn't actually do the pilot?" and went to bed. Landed: (a) toolchain
    + verdict inputs in the key, (b) epoch + per-row components, (c)
    derived per-(engine,consumer) sets, (d) partially (the closure
    self-check exists; batch wiring deferred), (h) fault injection, plus
    the migration tool the key change forced into existence. Commits
    4f46e7af, a9fe3f24, c98606bc, 27b4530f, 1da95402.

    ANSWERS TO THE SIX RECORDING QUESTIONS, so far:

    1. DID (c) DECOUPLE v4/v5? ⚠ THE QUESTION WAS WRONG. Measured, by
       touching one file at a time and re-reading every fingerprint:
         v5 VERIFY-only edit  -> dmc_v5 only        (was: 8,369 v4 rows)
         v5 COMPOSER edit     -> dmc_v4 AND dmc_v5
         v4 composer edit     -> dmc_v4 AND dmc_v5
         siddump rebuilt      -> all six families
       The criterion recorded above ("a v5-only edit must leave v4 at
       8,369/8,369") is FALSE AS STATED, and derivation is what proved it:
       DMC f1 has a `hetero_v5` build path (Super_Tau-Zeta) that runs a
       real v5 sub-player, and a `hetero_masm` path that runs the whole
       Music_Assembler pipeline. v4's closure legitimately contains 7 v5
       files and 11 MA files. v4 and v5 are NOT separable at family
       granularity — they share a build path. What derivation actually
       buys is getting that right FOR THE RIGHT REASON: verify_v5.py is
       not in v4's closure, so yesterday's edit correctly invalidates
       nothing, while a v5 COMPOSER edit correctly invalidates both.
       ⇒ REPLACEMENT CRITERION for any future re-measure: "a file used by
       only one consumer must move only that consumer's key", not
       "families must be independent".

    2. DID (a) EVER FIRE? Yes, immediately, and harder than expected. The
       migration tool (below) found FOUR FAMILIES whose verdicts have
       been stale since ~Aug 19 with nobody noticing, because nothing
       re-checks between batches: fc_standard (4,140), music_assembler
       (6,489), goattracker_v1 (1,387) all predate an Aug-19
       `src/usf/types.py` commit, and basic_program (524) predates
       grammar.lark + parser + types + writer changes since Aug 11. So
       MEMORY.md's coverage numbers for those four are stated at a stale
       key — not necessarily wrong, but unverified. They need a re-batch.

    3. FBDL — MEASURED, AND IT IS THE MOST IMPORTANT NUMBER OF THE NIGHT.
       `tools/fbdl_measure.py` over DMC f1's 11 stored generations:
       **tier 1 would have caught 0 of 5 real regressions = 100%
       fault-detection loss.** The five (all currently FULL, none in the
       97-member portfolio): Flash/Itinerant, Flash/Kan-Kan,
       Flash/Wind_of_Dead (C29 play-time re-bank), Tomace/Other_Side (C11
       glide-leftover seed), Bakewell/Finale — the first four being the
       C20 sixth-layer incident that a "+57 full" net count masked for a
       week. f2's generations contain no regressions, so its FBDL is
       UNDEFINED, not good.
       Caveats: n=5, and today's portfolio judged against July
       regressions (so it measures "would a portfolio of this SHAPE
       catch it"). Both still bear on the choice being made, which IS
       the shape.
       ⇒ ACTED ON: all five pinned in DMC_WITNESSES and wired into
       regression.py as their own group (verified FULL first).
       ⇒ This is the strongest evidence yet FOR (e): an exact-minimum
       feature-cover criterion did not intersect where this family's
       real regressions landed.

    4. PORTFOLIO CHURN: n/a yet; the v5 budget portfolio is built but
       waiting on the post-fix batch for its FULL list.

    5. COST, honestly: ~2.5 h of session time for (a)+(b)+(c)+the
       migration tool. Against it: 8,369 v4 rows carried instead of
       re-verified (~8.5 h of compute saved on this ONE key change), and
       four silently-stale families surfaced. Net positive already, and
       the machinery is reusable. The derivation itself costs ~4 min for
       all six engines.

    6. WHAT THE METHODOLOGY MISSED — three, all found by measurement:
       (i)  A CLOSURE MEASURED ON ONE MEMBER UNDER-APPROXIMATES, which is
            the unsafe direction. dmc_v4's `single` path loads 56 modules;
            `hetero_masm` 68, `hetero_v5` 76; the union over 7 build paths
            is 77. (c) as written said "a representative build+verify" —
            singular. It must be a build-path-STRATIFIED union.
       (ii) THE FIRST RUN OF THE DERIVATION TOOL PRODUCED A PLAUSIBLE,
            UNIFORM, SILENTLY TOO-NARROW ANSWER: 61 modules for every
            member, because `_worker_init()` had not run so `run_member`
            raised on its first use in ~0.3s. A derivation tool must
            report each member's VERDICT STATUS and refuse a sample where
            nothing reached one. "It ran and produced numbers" is not
            evidence that it measured the thing.
       (iii) MTIME IS USELESS AS A CHANGE DETECTOR. The migration's first
            cut refused all six families; every refusal was an artifact of
            this session's own probes (files modified and restored
            byte-identically still have a fresh mtime). Content comparison
            via `git diff <commit-at-stamp>` is the fix, and it turned six
            false refusals into two correct restamps and four correct
            refusals.

    ALSO MEASURED, AND NEW: the key was self-invalidating.
    `src/code_fingerprint.py` is imported by every batch (to compute the
    key), so the derived closure captured it — meaning every edit to the
    hashing logic invalidated every verdict everywhere, including edits
    that only WIDEN what the key covers. Excluded by name; it cannot
    affect a verdict.

    (h) ORACLE STRENGTH — FIRST NUMBER: 8/12 mutations caught (67%),
    stable across Katusha / Eco-Different / River_Racers / Commando.
    Caught: dropped write, dropped $D418, duplicated write, swap within a
    frame, value off by one, wrong register, reversed frame order, and a
    whole voice delayed one frame. Survived by design: cycle jitter (Trap
    B). SURVIVED UNINTENDED: (1) swapping a write across a frame boundary
    — the price of the flat concatenation that gives Trap-C robustness;
    (2) leading blank frames — NOT hypothetical, this is exactly the v5
    family-4 `playskip` defect fixed the same night; (3) losing up to 128
    trailing writes, inside the length tolerance. The verdict is exact on
    CONTENT and deliberately loose on FRAME BOUNDARY and TAIL. That was
    an axiom this morning and is a measurement tonight.
    ⇒ (h) should be promoted out of "deferred": it was listed as "not a
    grind experiment", but it named a live defect on its first run.

    STILL OPEN IN THE PILOT: (d)'s batch wiring (call
    `check_derived_closure` after the first member and fail loudly),
    (e)'s portfolio derivation (waiting on the batch), (f), (g), (i).

    (Provenance continued: the owner then challenged both the plan AND
    whether our whole regression apparatus is idiosyncratic
    invention or standard practice applied correctly. FIVE research
    sweeps were run against the academic + industry literature. This item
    is now the evidence-backed conclusion; the two earlier drafts —
    "narrow the fingerprints via an import graph", then "widen _SHARED
    and prefer byte-identity" — were BOTH mis-prioritised. Keep reading
    before touching anything.)

    ==== WHAT WE INVENTED vs WHAT IS STANDARD (the map) ====
    Almost every piece has a name in the literature. Ours is not a
    private methodology; it is a hand-rolled assembly of standard parts,
    two of which are assembled wrongly.

    OUR NAME                  STANDARD NAME / SOURCE                VERDICT
    write-log verdict         trace-level DIFFERENTIAL TESTING;     standard;
    (the Core Tenet)          the original is a PSEUDO-ORACLE       ours is
                              (Weyuker'82; McKeeman'98; Barr et     BETTER
                              al. TSE'15 taxonomy). ISO 26262-6     than the
                              calls it "back-to-back comparison     usual form
                              test" — the one standards-body hook.
      ⚠ It is NOT golden-master / approval / snapshot testing. Those
      store a HUMAN-APPROVED baseline; ours re-executes the original
      every run. The entire literature on golden-test pathology
      (rubber-stamping, brittle baselines, "the baseline captured a bug
      and now it's canon") does not apply to us BY CONSTRUCTION. Do not
      adopt that vocabulary — it would import a risk model we don't have.
    Trap B (cycles = observation) abstraction function applied before   standard
                              comparison; frame = transaction
                              boundary (UVM scoreboard practice)
    C28 per-chip split        out-of-order scoreboard                 standard
    trichotomy Check A +      prefix alignment w/ synchronization     standard
    aligned play stream       point + state checkpoint (RISC-V
                              lockstep vs Spike golden model)
    find_first_divergence     `first_diff.py` (sm64/oot decomp)      convergent
    regression portfolio      TEST-SUITE MINIMIZATION; criterion =    real, but
                              1-way covering array at index λ=2       WEAK end
                              (= Each Choice Coverage)
    code_hash gating          RTS AS MEMOIZATION (Ekstazi's own       right idea,
                              framing) / ACTION KEY (Bazel)          UNSAFE impl
    byte-identity gate        EARLY CUTOFF (Build Systems à la        sound, but
                              Carte; Ninja `restat`); bitwise =       we SAMPLE
                              Level-1 binary equivalence
    corpus_sync orphan rule   `insta --unreferenced=reject`           standardized
                                                                      elsewhere
    batch_diff at closeout    Crater-style two-run comparison         standard
    stratified subset         test selection by stratification        standard
    the convergence ledger    no counterpart found in any surveyed    OURS
                              community                              (and good)

    GENUINELY AHEAD OF THE FIELD (do not let anyone "simplify" these):
      * The re-executable reference (immune to the whole golden-rot
        family).
      * C15 — refusing to relax the verdict. Gulzar et al. (ICSE-SEIP'19)
        found over-relaxed output comparison is THE practitioner failure
        mode in differential testing. Keep treating relaxation proposals
        as adversarial.
      * Tier 2 exists. Most projects doing suite minimization have no
        full-suite backstop at all; ours is what caps the risk below.
      * The oracle is EXACT. NIST SP 800-142 names the oracle problem as
        the chief practical limit of combinatorial testing; we don't have
        it.
      * code_hash-gated incremental re-verification over a 12.6k corpus
        has no analogue in the emulator or decomp communities (they
        rebuild everything or run a fixed suite).

    ==== WHERE WE ARE SUB-STANDARD (the two real defects) ====

    DEFECT 1 — THE CACHE KEY IS UNSAFE (correctness, not performance).
    Rothermel & Harrold's axes split our four known problems in two, and
    the earlier drafts of this item attacked the harmless half:
      * shared dmc dir over-invalidates 8,369 rows  -> PRECISION failure.
        Costs compute. CANNOT produce a wrong answer.
      * missing modules + UNHASHED TOOL BINARIES + function-local imports
        -> INCLUSIVENESS (safety) failures. These produce SILENTLY WRONG
        VERDICTS: a cached FULL current code cannot reproduce. This is a
        NINTH LAYER of ledger C20, one level up from the eight we know —
        in the invalidation function itself.
      ⚠ WORST SINGLE GAP: `tools/siddump` is not hashed, and it sits on
        BOTH SIDES of the comparison — it produces the REFERENCE trace
        too. Rebuild it (or relink against a different libsidplayfp) and
        ground truth moves with nothing invalidated. Bazel documents this
        verbatim as a known issue ("two users with different compilers
        ... wrongly share cache hits"); ccache treats hashing the
        compiler as non-negotiable; REAPI requires tools to be inside the
        input root; SLSA L3 requires pin-by-digest.
      ⚠ "Hand-declared, unenforced" is the one combination nobody ships.
        Google DOES hand-declare deps in BUILD files — but an
        under-declaration is a sandbox failure or a strict-deps BUILD
        ERROR, never a silent cache hit. Empirical prior: humans doing
        manual RTS were unsafe in 27% of sessions (Gligoric et al.,
        ASE'14).
      ✓ In our favour: our verdict is DETERMINISTIC, which is exactly the
        precondition of the Christakis/Leino/Schulte (FM'14) machine-
        checked theorem that memoization is safe when the key covers ALL
        files. We meet the hard precondition and fail the easy one.

    DEFECT 2 — THE PORTFOLIO CRITERION IS AT THE WEAK END, AND THE
    OPTIMISATION IS ON THE WRONG AXIS.
      * 1-way coverage is blind in principle to 33-71% of failures
        (Kuhn/Wallace/Gallo TSE'04, Table 1: single-factor faults are
        28.6-67.5% of the total across four domains).
      * The directly comparable study — Medeiros et al. ICSE'16, 135 REAL
        configuration faults in configurable C systems — measures the
        upgrade: one-enabled (≈ our 1-way) found 107/135 = 79% at 1.7
        samples/file; PAIRWISE found 125/135 = 93% at 1.8. ~6% more tests
        bought 14 percentage points. RANDOM sampling found 124/135 = 92%.
      * λ=2 does NOT substitute for pairwise. Higher index λ is justified
        in the literature for fault LOCALIZATION (detecting arrays), not
        detection.
      * Our reduction ratio is 98.8% (64/5,401; 33/2,924). Every study
        that found minimization survivable did so at 12-70%. We are one
        to two orders of magnitude outside the validated envelope.
      * EXACT MINIMUM IS THE WRONG OBJECTIVE. Zhang et al. measured
        Greedy/HGS/GRE/ILP fault-detection loss at 5.23/5.21/5.33/5.11 —
        statistically indistinguishable. The CRITERION dominates, the
        algorithm doesn't. And every study finds detection tracks suite
        SIZE, so minimality is a cost we pay voluntarily while sitting on
        wall-clock headroom (20 min vs tier 2's hours).
      * Neither metric we can compute predicts our real risk: Shi et al.
        (ISSTA'18, 1,478 real failed builds) found size reduction R²=0.00
        and coverage loss also non-predictive against real faults. The
        ONLY predictor that worked was HISTORICAL detection — which we
        already collect and currently use only as a tie-break.
      * BLIND SPOT WITH NO LITERATURE ANSWER: our 93 traits are extracted
        BY RUNNING THE EXTRACTOR — the code under test. If the extractor
        mis-detects a trait, the portfolio is blind to that member class
        by construction. Code-coverage TSR doesn't have this because
        coverage is instrumented independently. Only a non-feature-derived
        stratum (random) mitigates it.

    ==== THE REVISED ACTION LIST (evidence-ranked) ====
    a. HASH THE TOOLCHAIN AND THE VERDICT INPUTS. [~1h, correctness]
       Fold into `code_fingerprint`: content hashes of `tools/siddump`
       and `tools/xa65/xa/xa`; `src/composer_runtime/`;
       `src/songlengths.py` + `tools/songlength_overrides.json` (the
       verify WINDOW — C20's eighth layer was exactly a window change
       silently invalidating verdicts); `tools/seed_disassembly.py`.
       Then extend the STAMP itself beyond code, Bazel-action-key style:
       md5 of the original PSID payload (kills C20 layer 7 — the HVSC
       update — structurally), the verify window params, and the build
       params fed to the builder (layers 4+5). Four C20 layers stop being
       detectable-by-bespoke-tool and become impossible.
       ⚠ TIMING: never land while a batch is in flight.
    b. CACHE EPOCH + RECORD THE KEY COMPONENTS PER ROW. [~30 min]
       A bumpable salt (REAPI `salt`, sccache's cache-buster) for "I know
       something moved that the hash can't see", and write the key's
       COMPONENTS into each results row (Debian `.buildinfo` idea) so a
       later-discovered under-approximation identifies WHICH rows are
       suspect instead of invalidating 5,401 at once.
    c. DERIVE THE DEPENDENCY SET, DON'T DECLARE IT. [~half day]
       Snapshot `sys.modules` after a representative build+verify, filter
       to repo files, hash exactly that set, and STORE the set. This is
       the depfile/Ekstazi pattern in ~30 lines; it captures
       FUNCTION-LOCAL imports by construction (a static walk cannot), and
       the v4/v5 separation falls out FOR FREE — no hand-narrowing, which
       is the one move that converts a performance bug into a correctness
       bug. Upgrade path if ever needed: `strace -f`-traced file access
       of the whole process tree (RTSLinux, ESEC/FSE'17 — they measured
       that a language-aware tracker sees only 17% of the files that
       matter once work escapes into subprocesses; our siddump subprocess
       IS that case).
    d. ENFORCE, DON'T JUST DECLARE — steal Azure TIA's three properties:
       SAFE FALLBACK (anything unmodelled ⇒ invalidate, never reuse),
       PERIODIC UNCONDITIONAL FULL RE-VERIFY, and a SHADOW AUDIT
       (re-verify a stratified sample of cache HITS from scratch; any
       disagreement is a dependency-set bug, reported loudly). Cheap, and
       it measures the exposure that (c) removes.
    e. PORTFOLIO: FLIP MINIMISATION TO A BUDGET. [~near zero, do first]
       Same solver, inverted objective: "best subset of size B" where B
       is the wall-clock budget, instead of "exact minimum satisfying the
       criterion". Monotonically better — the current 64 stays feasible —
       and it converts unused budget into fault detection instead of
       discarding it. Then: PIN bug-witness members as HARD CONSTRAINTS
       (Shi et al.'s only working predictor), and add a ROTATING RANDOM
       STRATUM of ~10-20 per family (random found 92% vs one-enabled's
       79% in Medeiros, and it is the ONLY mitigation for the
       self-referential trait blind spot).
    f. PORTFOLIO: MEASURE, THEN EXTEND TO PAIRWISE. [~moderate]
       First run NIST CCM over the CURRENT portfolio to measure what
       fraction of high-risk pairs 64 members already cover by accident
       (theoretical pairwise minimum for 93 binary factors is ~10 tests;
       we are at 64, so coverage may already be substantial). Only then
       add pair constraints, scoped to mechanistically coupled blocks
       (config knobs × instrument effects; each hand-patched wedge ×
       everything else; structural × config). 64→~150 would take tier 1
       from ~20 to ~45 min — still nothing against tier 2.
    g. MEASURE OUR OWN FBDL. [~low, highest evidential value]
       For every tier-2 run that surfaces a regression, record whether
       the tier-1 portfolio WOULD have caught it. Computable
       retrospectively from the batch jsonls + `batch_diff` full→partial
       events. A year of that number is worth more than any coverage
       argument, and it is the only metric the literature endorses.
    h. MEASURE THE ORACLE'S STRENGTH BY FAULT INJECTION. [~low]
       We have ZERO evidence about what the verdict would fail to catch,
       and one known blind spot (Trap B's boundary, found by ear).
       Mechanical mutants: shift one voice's writes a frame; swap two
       adjacent writes in a frame; drop one $D418; shorten a note by a
       tick; shift one of two interleaved tunes half a frame. Record the
       kill rate. This converts "cycles don't matter within a frame" from
       an AXIOM into a measured claim.
    i. MAKE THE BYTE-IDENTITY GATE EXHAUSTIVE. [~half day]
       Every reference system applies early cutoff per-artifact, never to
       a sample (GCC compares all stage2/stage3 objects; Debian rebuilds
       whole archives; Ninja checks every restat output). Our "portfolio
       + carriers" golden set is a hand-declared affected set — the same
       under-approximation as defect 1, one level up. Cure: a committed
       hash manifest (path → md5, all ~12.6k), so a carrier refactor's
       gate is "rebuild all, diff manifest, require zero changes". At
       ~100× cheaper than verification this is affordable, and it doubles
       as a permanent tripwire for defect 1.
    j. SPLIT THE CORPUS RE-SYNC COMMIT FROM THE CODE COMMIT. [~free]
       MongoDB's golden-data framework MANDATES this: changes affecting a
       non-trivial number of test outputs must be a separate PR, so the
       output diff is reviewable on its own. Ours currently bundles "one
       composer fix" with "12,600 artifacts changed".

    ==== EXPLICITLY REJECTED ====
      * Hand-narrowing the fingerprint dirs (both earlier drafts). It
        optimises the one axis that cannot produce a wrong answer, while
        the safety failures sit untouched. Do (c) instead — narrowing
        then falls out as a by-product, derived rather than asserted.
      * Adopting Bazel/Nix wholesale — disproportionate for a
        single-repo research pipeline. Steal the one idea (toolchain is
        an input) and move on.
      * ISO/IEC/IEEE 29119 — process/documentation framework, no
        substantive guidance on maintaining expected-results data. The
        only standards-body item worth citing is ISO 26262-6's
        "back-to-back comparison test", as vocabulary, plus its caveat:
        back-to-back equivalence demonstrates equivalence but NOT the
        absence of unintended functionality — which is exactly Trap B's
        boundary biting.
      * Renaming any of this to "golden master testing" (see the map).

    ==== THE ORIGINAL ISOLATION QUESTION, ANSWERED ====
    Unchanged by the research, and now better grounded: SHARE DECISIONS
    (ledger, techniques, verification machinery) — free at regression
    time; keep REPRESENTATION growth under the owner gate; ISOLATE
    composer/extract per family until Move 1 (§8 sequencing, not
    architecture); share a composer only when two families are the same
    engine modulo knobs (measured: f2 at Jaccard 0.732 shared, v5 at
    0.136 correctly did not). The regression COST question is answered by
    (c)+(i), not by weakening any gate.

    ==== GAPS THE SURVEYED COMMUNITIES HAVE THAT WE DON'T ====
    Recorded as leads, not tasks:
      * A SYNTHETIC hand-written test corpus (Lorenz / blargg / mooneye /
        SingleStepTests). Every emulator community's foundation is
        purpose-built minimal tests with known-correct answers; ALL of
        our tests are integration tests on real corpus members, which is
        why every failure is a multi-cause investigation. We have no
        "20-byte SID whose only job is to exercise pw_up_reverse".
        `resid-test`'s tiny `write/run/check` DSL is the model.
      * A SECOND ground-truth implementation. VICE's testbench tracks
        third-party emulators; resid-test compares against a
        transistor-level model. We have exactly one (libsidplayfp), and
        our own memory records py65 and libsidplayfp DISAGREEING on played
        notes. A second reference turns that hazard into a detector.
      * PERSISTED reference captures (Dolphin `.dff`, VICE `vicesnd.sid`).
        Ours are ephemeral; persisting them content-hashed is the only
        defence against C20 layer 7 that doesn't require re-deriving
        everything.
      * A LONGITUDINAL progress artifact (decomp.dev-style per-commit
        JSON reports + trend). C20's sixth layer — net counts masking 4
        regressions for a week — is structurally what this prevents.
      * EMI-style mutation for the C34 class (mis-decoded content that
        still round-trips): mutate a USF field the write stream SHOULD be
        sensitive to and assert the stream changes as predicted. A field
        whose mutation changes nothing is dead or mis-decoded. That is a
        mechanical detector for a class we currently find only by READING
        the handler.
      * Publishing the corpus as a community artifact (a SID player
        write-stream conformance corpus) — nothing like it exists.

    KEY SOURCES: Barr/Harman/McMinn/Shahbaz/Yoo TSE'15 (oracle taxonomy);
    McKeeman'98 (differential testing); Gulzar et al. ICSE-SEIP'19
    (practitioner failure modes); Gligoric et al. ISSTA'15 (Ekstazi);
    Celik et al. ESEC/FSE'17 (RTSLinux, cross-process); Christakis et al.
    FM'14 (memoization safety theorem); Bazel remote-caching known issues
    + REAPI; ccache `compiler_check`; reproducible-builds.org; Mokhov et
    al. (early cutoff); Kuhn/Wallace/Gallo TSE'04 + NIST SP 800-142
    (interaction rule); Medeiros et al. ICSE'16 (sampling comparison);
    Shi et al. ISSTA'18 (FBDL); Zhang et al. (JUnit reduction);
    Jeffrey & Gupta TSE'07 (selective redundancy); Dolphin FifoCI; VICE
    testbench; decomp.dev/objdiff/decomp-permuter; MongoDB golden data
    framework; insta `--unreferenced`.

# ============================================================
18. DMC V5 GRIND — plan + live status (opened 2026-08-22, right after
    the v4 closeout). The methodology pilot of item 17 rides on this
    grind; see item 17's PILOT charter for what is being trialled and
    what must be written back.

    ==== STATUS 2026-08-23: ROUND 1 DONE — 1,167/2,151 FULL (54.3%) ====
    The grind is OPEN and the target is now named precisely: the residue
    is ONE PLAYER VARIANT. `family4` (the Jupiter41 branch, play +$95) is
    642 members at 7.0% FULL of buildable and carries 466 of the 673
    partials (69%); canon f3/f5 is at 84.5%. So "the v5 grind" means
    "make family-4 work".
      DONE this round: the startup lever (27b4530f — the $1016 2-phase
      phase seed + dropping family-3's play-skip), the C21 diagnostic fix
      (c98606bc), the committed reference player, `dmc_v5_build_one`, and
      TIER 1 (50-member budget portfolio, wired both places, full
      regression GREEN).
      NOT DONE: the lever unblocked the class without closing it — 0
      regressions but only 8 new FULLs; the divergence moved deep instead.
      The next bucket is named under "NEXT, in order" below.
    ⚠ The LAYER-2 diagnosis in this item was SUPERSEDED — read the banner
    before the older text.

    ==== ⚠ SCOPE WAS WRONG BEFORE WE STARTED (fixed 2026-08-22) ====
    The v5 batch member list came from `tmp/dmc_families.json` — the
    PRE-#85 clustering — exactly the trap f1/f2 were fixed for when they
    got `dmc_f*_members_85.json`. Two consequences, both found by the
    baseline batch + `batch_diff` before any code was touched:
      * 2 "regressions" were INPUT DRIFT, not code: `I_Hate_Ascii.sid`
        was RENAMED to `I_Hate_ASCII.sid` in #85, and
        `Kochan_Maciej/Vitality_5_tune_10.sid` is GONE from the
        collection. (C20 seventh layer, in its crude form — the
        dangerous form is a file that still exists with a changed
        payload, which nothing in our key would catch. Pilot datum for
        item 17(a).)
      * The list MISSED 657 v5-family members. A sweep of the 911
        DMC-classified members that no family list claimed found 38 FULL
        + 478 partial + 141 recognised-but-unsupported that build through
        the v5 path; only 245 were genuinely not v5 (player_code_mismatch
        / no_jumptable). This reconciles a discrepancy that sat in plain
        sight: v5's own SCOPE.md censused 2,181 SIDs while the batch list
        had 1,495 — nobody had cross-checked the list against the doc.
      ⚠ LESSON (new, none of the five research sweeps surfaced it): THE
        MEMBER LIST IS AN INPUT TOO. Nothing versions it or checks it
        against the catalogue. Grinding the old list would have left 478
        partials permanently invisible to every residue census while the
        coverage number drifted toward a fake 100%.
      Corrected list: `tmp/dmc_v5_members_85.json` (2,151 members).

    ==== TRUE BASELINE (2026-08-22) / POST-FIX (2026-08-23) ====
      BASELINE 2,151 members: 1,158 FULL (53.8%) · 681 partial · 312
      unsupported + error. (The pre-grind "1,120/1,494 = 75%" was an
      artifact of the short list.)
      POST-FIX BATCH `tmp/dmc_v5_r2_results.jsonl` (2026-08-23, after the
      family-4 startup lever): **1,167 FULL / 2,151 (54.3%)** · 673
      partial · 311 unsupported+error. `batch_diff` vs the baseline:
      **0 REGRESSIONS**, 8 gains, 256 members only-in-old (all
      unsupported/error — no FULL lost), 1 only-in-new (the
      I_Hate_ASCII rename).
      SPLIT BY PLAYER BRANCH (whole-corpus census):
        family-4      642    35 FULL (5.5%)    7.0% of buildable
        canon f3/f5 1,382 1,132 FULL (81.9%)  84.5% of buildable
        unbuildable   127     0
      => family-4 carries 466 of the 673 partials (69%). THE GRIND IS
      family-4.
      TIER 1 NOW EXISTS: `tools/dmc_v5_regression_portfolio.json`, 50
      members, BUDGET mode, wired into regression.py (summary + exit
      code). Full regression GREEN with it, 0 regressed anywhere.
      Baseline files: `tmp/dmc_v5_85_results.jsonl` +
      `tmp/dmc_v5_discovery.jsonl`, merged in `tmp/dmc_v5_merged.jsonl`;
      July snapshot kept at `tmp/dmc_v5_results.pre_grind.jsonl`.

    ==== THE CENSUS SAYS WHERE TO START ====
    `divergence_census --engine dmc_v5 --partials` over the 681:
      * 280 (41%) diverge at POSITION 0 on $D400 V1 freq-lo
        (`orig=$00 mine=$1F` and friends) — position-0 across 280
        members is ONE systematic cause, not 280 bugs.
      * 26 more at position 0 on $D418 (`orig=$1F mine=$A9`).
      * the rest is a deep tail at `@>=4k` (40 $D400, 34 $D408, 28
        $D401, 26 $D407, 23 $D40E, ...) = genuine per-member effect work.

    ==== ORDER (per feedback_residue_triage_order: measure ->
         fix-verdict -> unblock-builds -> fix-effects -> accept-last) ====
    1. ✅ DIAGNOSED 2026-08-22 — see "THE LEAD-IN GAP" below. The
       position-0 cluster was TWO things stacked, and neither was what
       the census said.
       (original text) diagnose the 280-member position-0 cluster
       (+ the 26 $D418 siblings). Candidate: a verdict/alignment or
       init-priming artifact, i.e. a fix at zero composer cost in front
       of ~14% of the family. Representatives:
       Bayliss_Richard/River_Racers.sid sub 1 (pos=0 orig=$00 mine=$1F),
       Praiser/Emergency.sid sub 0, Astovel/Cyber_Brain.sid sub 0 ($D418).

    ==== ⚠⚠ THE LEAD-IN DIAGNOSIS BELOW IS SUPERSEDED (2026-08-22 night) ====
    Keep reading the LAYER-2 text as a record of what was believed; do not
    act on it. Three things were measured and two of them overturn it:

    (A) THE FLAT VERDICT CANNOT SEE A FOLDED-IN LEAD-IN AT ALL. An empty
        play() contributes nothing to the concatenated stream, so "our
        composer folds the lead-in into init, leaving ~352 partials two
        frames out of phase" cannot produce a divergence. Confirmed
        independently by fault injection (item 17 (h)): `leading_blank_
        frames` is one of exactly three mutations the oracle does not catch.
        The REAL first divergence is flat play position 1 — the orig writes
        V1 freq-lo where we write V1 SR.

    (B) THE CLUSTER IS A PLAYER VARIANT, NOT A FAMILY-WIDE PHASE BUG.
        80% of the pos<64 partials are `family4` (the Jupiter41 branch,
        play +$95). In a 40-member sample of currently-FULL members, ZERO
        are family-4. That branch is ~37% of buildable v5 members (~750 of
        2,151) and had NEVER produced a single FULL. It is the v5 residue,
        near enough — the canon family-3/5 player is already ~89% FULL of
        buildable members.
        ⇒ THE V5 GRIND IS "MAKE FAMILY-4 WORK", not "polish a mature family".

    (C) `pipelines/dmc/family4/RE_NOTES.md` ALREADY HAD THE MECHANISM,
        from 2026-07-01, including the exact prescription AND the record
        that its own attempt failed. Item 18 said to read the earlier
        round's notes first; the notes it pointed at were v5's, and the
        ones that mattered were family-4's. Reading both would have started
        this session where it ended.
        MECHANISM: family-4's play ($1095) has no speed counter — it
        toggles `DEC $1016 / BMI` between MAIN (effects) and TICK (advance
        + fetch, falling into MAIN). $1016 is an uncleared file-image
        leftover that sets the startup PHASE. The July attempt seeded it
        but left family-3's `playskip = 2` in place, so the rebuild still
        opened with two silent frames; both halves were needed.

    LANDED (27b4530f): phase seed from $1016 + playskip 0 for family-4.
    Measured on a 140-member stratified subset, family-4 depth buckets:
        1-63  58 -> 13   ·  64-999  3 -> 22  ·  1k-10k  4 -> 16
        10k+   7 -> 21   ·  deeper 49 · shallower 0 · REGRESSED 0
    HONEST: it UNBLOCKS the class, it does not close it — 0 of 140 reached
    FULL; the divergence just moves to the next family-4 bug. Counting only
    full/partial reports this as "0 gained" and hides the effect entirely;
    use the DEPTH HISTOGRAM as the metric for an unblocking lever
    (`tmp/v5_depth_measure.py`). Spot-check: Eco/Different partial -> FULL.

    NEXT, in order:
      1. The post-fix batch (`tmp/dmc_v5_85_results.jsonl`) gives the exact
         family-4 numbers + the portfolio's FULL list.
      2. Derive the v5 BUDGET portfolio + wire regression (both places).
      3. The next family-4 bucket. Two known first divergences to start
         from: Street_Fighter at flat position 4 ($D403 V1 PW hi, orig $08
         vs our $00 — another uncleared leftover on the idle frame), and
         Silicon_Dreams at 60,500/170,697.
      4. 13 family-4 members remain in the 1-63 bucket = a residual
         lead-in sub-class.

    ==== OPENER FOR A FRESH SESSION ====
    ⚠ SUPERSEDED 2026-08-24 — do not paste as-is. The open-work list is now
      `backlog.md`; `dmc_v5_r2_results.jsonl` is superseded by r3 (get the
      current file from src/batch_results.STORES, never a hardcoded name);
      and family-4 is 650 members WITH FULLs, not "~750, 0 FULL". Current
      status + the named next lever live in pipelines/dmc/v5/RE_NOTES.md.
    ▎ SIDfinity: continue the DMC v5 grind. Read backlog.md item 18 (plan
    ▎ + live status) and item 17 (the methodology pilot, now with a real
    ▎ write-back) first. The v5 residue is ONE PLAYER VARIANT — `family4`
    ▎ (~750 members, 0 FULL until last night) — not a family-wide bug; read
    ▎ pipelines/dmc/family4/RE_NOTES.md's 2026-08-22 section before anything.
    ▎ Step 1: read tmp/dmc_v5_r2_results.jsonl (the post-fix batch) and
    ▎ `tools/batch_diff.py tmp/dmc_v5_merged.jsonl tmp/dmc_v5_r2_results.jsonl
    ▎ --fail-on-regression` for the true numbers. Step 2: derive the v5 BUDGET
    ▎ portfolio (`select_regression_portfolio --engine dmc_v5 --budget 40`)
    ▎ and wire it into regression.py in BOTH places. Step 3: the next family-4
    ▎ bucket — Street_Fighter diverges at flat position 4 ($D403 V1 PW hi,
    ▎ orig $08 vs our $00, on the IDLE frame = another uncleared leftover).
    ▎ Use tools/dmc_v5_build_one.py --verify --localize.

    ⚠ LEFT UNDONE ON PURPOSE, needs the owner: FC / Music_Assembler /
    GoatTracker / basic_program all carry verdicts predating an Aug-19
    src/usf/types.py change (basic_program: Aug-11 grammar/parser/writer).
    `migrate_verdict_rows` refuses to carry them and MEMORY.md now flags all
    four. Re-batching them is hours of compute across four families — an
    owner call, not an autonomous one.

    ⚠ ALSO PENDING: pilot (d)'s batch wiring — call `check_derived_closure`
    after a batch's first member and fail loudly on a module outside the
    stored set. Deliberately NOT landed while the v5 batch was running,
    because editing a batch tool changes that family's fingerprint and
    contaminates the run in flight (learned the hard way tonight: an earlier
    baseline run had to be discarded for exactly that).

    ==== THE LEAD-IN GAP — step 1's real finding (2026-08-22) ====
    The census's "280 partials diverge at position 0" was a MEASURING
    artifact stacked on a real bug. Peeled apart:

    LAYER 1 (verdict, FIXED): `verify_v5` used the per-IRQ capture ONLY
    for `cfg.family4` members and never gained v4's C21 retry, so for
    every orig whose init SPILLS past the frame-0 bucket the flat
    trichotomy compare misaligned from write 0 — Check A compared a
    partial init against a complete one and the member reported
    "position 0" with a meaningless first_diff. River_Racers' init
    sweep starts at cycle 16,820 (our rebuild finishes init by ~2,400),
    so it spills. PORTED v4's retry into `verify_v5` (only runs when the
    primary compare already failed => zero-regression by construction),
    PLUS a second path: when neither compare passes, report the PER-IRQ
    numbers, so the census clusters on the honest divergence instead of
    alignment noise. Measured on 8 sampled cluster members: Check A
    flips False->True on 8/8.
    ⚠ It flips 0/8 to FULL. The verdict fix buys DIAGNOSIS, not
    coverage — but 352 partials were reporting a position that did not
    mean anything, so every residue census over them was blind.

    LAYER 2 (the real bug, OPEN — the top v5 lever): with Check A
    passing, the sampled members diverge in the FIRST PLAY FRAME
    (play_match 0-21 of ~110k). Two examined byte-by-byte
    (Eco/Different + MHD/Street_Fighter, different authors, identical
    `flat_div` signature [0,1,0,0,0]):
      * the ORIGINAL emits TWO full play frames (19 writes, then 22)
        that OUR REBUILD DOES NOT EMIT AT ALL (mine = 0 writes for
        play 1 and play 2). Our first writing frame is the orig's
        play 3.
      * those two orig frames are a per-voice LEAD-IN with the gate
        OFF (V1ctrl $80 = noise/no-gate on frame 1, then $10 =
        triangle/no-gate on frame 2) — the shape of a hard-restart /
        priming pass.
      * and our content is then OUT OF PHASE: at the orig's play 3 the
        orig writes V1fhi=$0A while we write $DF — and $DF is exactly
        what the ORIG wrote on its play 1. Street_Fighter identical:
        orig play3 V1fhi=$28, ours $A3 = the orig's play-1 value.
      READING: the original DEFERS part of its setup into its first two
      play() calls (the trichotomy's "deferred init" pattern), while our
      composer folds that work into init. Check A therefore PASSES (both
      reach the same end-of-init STATE) while the play STREAM differs by
      two whole frames — the orig's lead-in writes are play-stream
      writes and ours do not exist.
      ⚠ SO THE FIX IS A COMPOSER CHANGE, NOT A VERDICT ONE: emit the
      lead-in frames as play writes rather than folding them into init.
      NB v5 history already has `dmc_v5_results.preLeadin.jsonl` /
      `.afterLeadinFade.jsonl` — a lead-in feature was worked before;
      READ THAT ROUND'S NOTES BEFORE RE-DERIVING (RE_NOTES.md).
      Scope: 352 partials carry the pos<64 signature (52% of all
      partials, 16% of the family). 8/8 sampled share it; 2/2 examined
      in detail share the exact shape. Treat 352 as the upper bound
      until a re-batch measures the true carrier set.

    2. PORTFOLIO + REGRESSION WIRING, in PARALLEL — not a blocker.
       Needs a `dmc_v5_features` extractor + a `dmc_v5` ENGINES entry +
       wiring into regression.py (BOTH the per-family summary AND the
       hardcoded exit-code list). Per item 17(e) this is built as a
       BUDGET portfolio (max coverage under a wall-clock cap) with
       bug-witnesses PINNED and a rotating random stratum — the pilot's
       central experiment. NB v5 has NO regression presence at all today.
    3. UNBLOCK-BUILDS, as a HYPOTHESIS not a bucket: `pulse_table_
       overflow` (81) + `filter_table_overflow` (22) look like the C8
       capacity family we widened 4x in v4 — where the fix took members
       STRAIGHT TO FULL, not merely to partial. ~20 min of triage tells
       us. ⚠ C5 governs the rest: detection rejects
       (player_code_mismatch 202, no_jumptable 170) are NOT the FULL
       bottleneck; converting unsupported -> partial is not progress by
       itself.
    4. THE DEEP TAIL (`@>=4k` clusters) — per-member effect work, the
       long grind.

    ==== ✅ THE `error` BUCKET IS CLOSED (2026-08-25) ====
    All 14 v5 `error` rows were OUR DECODER disagreeing with the player, not
    corrupt data — ledger C34's 5th occurrence (the MIRROR IMAGE: refusing what
    the player accepts). Unlisted command byte = the dispatch chain's 1-byte
    no-op fall-through; both stream positions are 8-BIT and wrap (an
    unterminated stream cycles, it does not run on); and `n_sectors =
    secp_hi - secp_lo` is not a count (independently-relocated operands — bound
    by reachability, C2). 11 build (3 FULL), 1 joins item 19's overflow bucket,
    2 refuse cleanly under a new `data_tables_off_image` reason. 0 regressions
    (byte-identity gate over 181 members incl. the full portfolio).
    ⚠ STILL OPEN, small and self-contained: those 2 refusals. MEASURED
    2026-08-25 (post-init RAM vs file image, per operand) — and they are NOT the
    same problem, which the shared `data_tables_off_image` reason hides:
      * Piirainen_Antti/Left_Ear_Bleedin_Ear_Left IS a C26 unpacker. Its
        out-of-image operands are a clean page-aligned family ($4000 instr /
        $4100 wave_ctrl / $4200 wave_freq / $4300-$4400 pulse / $4500-$4600
        filter / $4700 orderlist) and ALL hold real data post-init. The two
        in-image operands are the PLAYER'S OWN freq tables at base+$119/$179 —
        song data proper is 9-of-10 out (the 10th, secp_lo $115A, is in-image
        but all zeros). So C26's "EVERY operand outside" gate should arguably
        read "every SONG-DATA table", not every operand.
        Setting `cfg.post_init_sub = 0` already makes it BUILD — but only to a
        weak partial (state_match True, play_match 0: diverges at the very first
        play write, orig $D400=$00 vs our $D418=$1F). Loosening a boundary the
        ledger states explicitly, for one member that then diverges at write 0,
        is not a call to make unattended. Worth 30 min when someone is awake:
        either the post-init snapshot is taken at the wrong moment or this is
        not really a v5 member.
      * Ed/We_Were_All_Kids is NOT this player. Its operands are incoherent
        ($D89D orderlist, $F985/$F8B1 secp, $0202/$0403 freq, $0F4B wave) — not
        a relocation, not an unpack target — and `_postinit_window` cannot even
        run its init. Treat as a detector false positive; the honest fix is a
        detection-side reject, not an extract accommodation.
    ⚠ Two guards written as `except` around the decode died silently when it
    stopped raising (one took a FULL member down) — discipline recorded in
    .claude/memory/feedback_relaxing_an_error_kills_its_guards.md.

    ==== TOOLING GAP vs v4 (build when the failure classes justify it,
         and PARAMETRISE rather than duplicate — a 4th copy of a
         dispatch is what produced the C20 harness bug) ====
      MISSING: build_one (--verify --localize), next_partial, smoke,
      state_addr (v5's state layout differs — v4's tool would give
      confidently WRONG addresses), offtable_probe (C6 is marked
      recurring for FC *and v5*, so the class exists here),
      canon_diff (needs a v5 canon player binary), and a
      divergence_triage ENGINE_DETECTORS entry.
      ALREADY THERE: own extract/composer/verify, family batch with
      code_hash gating, mass_write via corpus_sync (orphans + audit),
      divergence_census entry, and all three MANDATORY docs (SCOPE.md,
      52 KB RE_NOTES.md, annotated disassembly.s).

19. (DELETED 2026-08-26 — CLOSED. DMC v5 TABLE OVERFLOW, all 126 members.
    Option (c) landed (ledger C8 sixth widening: the paged composer cursor —
    from_usf pass-2 packer + per-voice page-select SMC, gated on
    `len(pool) > 256`, byte-gate 60/60 vs HEAD). The 4 position-sonifying
    members were then served by the LIVE-POSITION FORM (owner-approved:
    OFSIG `pulse_position`/`filter_position` + per-instrument
    `pulse_table_pos`/`filter_table_pos` + the composer delta-serve — ledger
    C11 2026-08-26 refinement), so the `offtable_live_pos` refusal class is
    EMPTY. Results: 10 FULL + 116 partial + 0 refused; techniques in
    C8/C11; numbers in project_dmc.md.)

20. DMC v5 PLAYER VARIANT behind ~106 `player_code_mismatch` rejects —
    ⚠ LARGELY SUPERSEDED 2026-08-28 by items 22 + 23, which identify the two
    biggest clusters concretely. Its conclusion ("a genuine player VARIANT with
    its own body layout, like family-4") was RIGHT about the shape and WRONG
    about the remedy for most carriers: the $10A1 cluster does not need a new
    reference binary at all — 43 of them ARE family-4 and just never reach that
    branch (item 22), and ~30 more are the CANON body behind a lead-in wrapper
    (item 23). What is left here after 22 + 23 is the $1385 x16 / $16C7 x16 /
    $10CD x6 clusters and the singletons. NB its counts were taken over the
    ~106 v5 rejects; items 22-23 measure all 309 UNROUTED (v4-and-v5 refused),
    so the cluster sizes differ legitimately.

    NOT blocked on you, just BIGGER than one overnight session. Parked with the
    measurement so it can be picked up cleanly.

    Clustered by first mismatch site (tmp/v5_mismatch_census.json):
      49  $10A1 opcode   16  $1385 opcode   16  $16C7 opcode
       6  $10CD abs       5  $10A1 imm      rest singletons
    The $10A1 cluster (the play-body ENTRY) is ~31 members carrying a 9-byte
    prologue `A9 imm / F0 04 / CE <ctr> / 60 / AA` = an inline play-skip
    counter, and ~7 more carrying `LDA $1119 / BEQ / LDA $111C` (a two-flag
    head). But it is NOT merely a prologue: retrying the canon compare at every
    shift 0..12 matches NONE of the 49, and at shift 9 the body then diverges at
    $10A7 where the member has `DEC $1013 / BPL / LDA $1012 / STA $1013` (an
    INLINE SPEED COUNTER) against the reference's `LDX #$00`.
    => a genuine player VARIANT with its own body layout, like family-4. It
    needs its own reference binary + site map (the extract reads data-table
    addresses from operand SITES, so a shifted body reads the wrong bytes).
    That is a migration-sized task, not a detector tweak — and C13's rule
    ("dispatch on the PLAY-body signature") is what makes it safe to attempt:
    a loosened dispatch cannot false-FULL, build+verify judges.

21. (DELETED 2026-08-26 — CLOSED. `trailing_sector_cmds` is 0 of 15: 14 FULL,
    1 (Player_One/Valtavirtaa) moved into item 19's overflow bucket. Its
    option (b) — "prove the trailing commands are DEAD and drop them" — was
    REFUTED at its premise: $FF ends a v5 sector only as the lookahead peeked
    after a ROW, so a sector ending in commands does not end at all and there
    is no next sector for the state to survive into. Technique recorded in
    ledger C34's 5th occurrence; numbers in project_dmc.md.)

22. DMC: 43 UNROUTED MEMBERS ARE FAMILY-4 PLAYERS COMPARED AGAINST THE WRONG
    REFERENCE (measured 2026-08-28; the biggest single lever in DMC right now).
    ⚠ OWNER DECISION — not on representation, on COST: landing it re-invalidates
    every DMC verdict and forces another full re-batch (~13 h wall on this box,
    the one just completed). The change itself is small and C13-licensed.

    MEASUREMENT. `v5_diagnose` over all 309 unrouted: 181 `player_code_mismatch`
    / 121 `no_base` / 7 `init_skeleton`. Of the 181, **128 diverge at site
    $10A1** (the play entry), so they were regrouped by the PLAY HEAD BYTES
    there — 44 distinct heads. The largest, **43 members**, carries the family-4
    play head VERBATIM (`A5 FA 48 A5 FB 48 CE 16 10 30 1E ...`) and 41 of them
    are **median 96.0% byte-identical** to the Jupiter41 family-4 player over
    its `$1095-$16FF` body — inside the genuine family-4 band (47-100%; the
    We_Were_All_Kids impostor was 2.0%). They are family-4 players.

    ROOT CAUSE (ledger C13, third occurrence — entry updated). `_detect_v5`
    reaches the family-4 branch only when the jump table reads init `base+$40`
    AND play `base+$95`. A family-4 player wearing any other head therefore has
    base derived as `play-$A1` and is compared against the family-3/5
    reference, which fails at the one site where the two players genuinely
    differ. The head chose the reference; the body was never consulted.

    FIX SHAPE: when the family-3/5 body compare fails, try the family-4
    reference at the same base before refusing — "the head selects a CANDIDATE,
    never THE reference". Safe by C13's rule: a loosened dispatch cannot
    false-FULL, build+verify judges. Note detection != FULL (ledger C5): expect
    these to land as partials first, and score by first-divergence DEPTH.

    REFUTED, do not re-chase: those 43 also use different zero-page pointers
    (`$FA`/`$FB` vs canon `$F8`/`$F9`), which reads exactly like a
    masked-compare bug since zp is runtime state the compare already ignores
    elsewhere. Re-running the whole body compare with EVERY zp operand treated
    as don't-care matched only **3 of 50** — the other 43 still differ at
    `$10A7` because they are a different player. The zp difference is a
    SYMPTOM, not the cause; fixing it would have changed nothing and hidden
    this finding.

    LOOSE END: 2 of the 43 (`Booker/Droop_Intoo`, `Booker/Droop_O_Funk`) share
    the head but score 5.7% — their `_detect_v5` base is non-page-aligned
    ($2D37 / $24D8), i.e. the BASE derivation is wrong for them. Separate look.

    Evidence: tmp/unrouted_{triage,diagnose,census,clusterA}.txt,
    tmp/unrouted_diagnose.json. Numbers in project_dmc.md head.

23. DMC: ~30 UNROUTED MEMBERS ARE THE CANON v5 BODY BEHIND A LEAD-IN WRAPPER
    (measured 2026-08-28; same census as item 22). Composer support ALREADY
    EXISTS — this is a detection-only gap.

    Their play head is `A9 00 / F0 04 / CE <slot> / 60 / AA` followed by the
    CANON v5 body (`A5 F8 48 A5 F9 48 ...`): an Ed-style lead-in skip counter
    (`LDA #imm / BEQ real / DEC slot / RTS`) prepended to an otherwise
    untouched player. That is exactly the mechanism landed 2026-08-27 for
    `Ed/We_Were_All_Kids` — `play_skip_init`, probed off the init immediate,
    with the composer emitting the count. So only `_detect_v5` has to see past
    the wrapper (follow it to the real body, as `_resolve_init` already does
    for a relocated init). Carriers e.g. `Ed/Bouncy_Funk`,
    `Ed/A_Quoi_Ca_Sert`. Same re-batch cost as item 22, so land them together.

    Two smaller clusters from the same grouping, for whoever picks this up:
    **14 members** read all-zero at `base+$A1` (the player is not in the file
    image at all — ledger C26 unpacker / relocating wrapper, e.g.
    `Bakewell_Dwayne/Misfortune`), and **5 members** carry a further distinct
    head (`AD 19 11 F0 19 AD 1C 11 38 ED 19 11 ...`, e.g.
    `CreaMD/Awesomeness`).

24. DMC: `Surgeon/Nice_Dream_2SID` — A VERDICT ROW NOTHING OWNS (found
    2026-08-28 by the new `route.py --gaps` mirror check; 1 carrier corpus-wide).
    ⚠ OWNER DECISION, because the two possible causes need OPPOSITE actions.

    It is recorded FULL as a `multisid` member under a now-dead `code_hash`,
    its `.usf` + `.sidfinity.sid` are on disk (Aug 22), and `dmc_v4_config`
    REFUSES it today: `player_code_mismatch: first diff at $1235`. It was
    already unrouted in the pre-overnight roster, so this predates the
    2026-08-27/28 work. Ledger C20's stale-FULL palimpsest, and it was
    invisible from every direction at once — the mass-write SKIPS it (stale
    hash; it prints `WARNING: skipped 1 FULL rows`), that writer's orphan
    removal only iterates members it knows about, the roster claims it for
    nobody, and no census counts it.

    THE QUESTION: did v4's detector TIGHTEN at some point (a regression worth
    finding — this is a 2SID / ledger-C27 member, and a detector that quietly
    stopped claiming a member it once built FULL would not be visible anywhere
    else either), or did the member legitimately leave the family, in which
    case its artifacts are orphans and should be DELETED?

    NEXT MEASUREMENT: `git log -S` / bisect `pipelines/dmc/v4/factory.py` over
    the window between its FULL row's `code_hash` and now, and dump the orig's
    bytes at `$1235` against the canon player to see WHAT the compare trips on.
    Cheap — one member, one site.

25. DMC v6 — 16 MEMBERS ROUTED TO A PIPELINE THAT CANNOT BUILD THEM.
    `route.py --gaps` reports them as `no_store`: they are claimed (sidid
    `DMC_V6.x`, and `pipelines/dmc/v6/extract/` exists), but there is no entry
    in `src/batch_results.STORES` for them because the v6 COMPOSER was never
    started. Zero verdicts, and they appear in no coverage line anywhere.

    Status per `pipelines/dmc/v6/RE_NOTES.md`: player RE first pass DONE
    (2026-06-21) — full state-block map, orderlist / pattern-pointer / pattern
    stream all documented from `DMC_V6_note`'s disassembly. Extract + composer
    NOT started. The notes' own judgement is that V6's musical degrees of
    freedom are the same DMC shape v5 already models, so the USF representation
    should largely REUSE the v5 dimensions; only the binary lifter and the
    emitted 6502 are new.

    So this is a small, well-prepared migration (16 members, all single-subtune,
    standard entry) rather than an investigation — and until it exists, those 16
    are the only DMC members with no possible verdict. First step: a v6 store in
    `batch_results.STORES` + `pipelines/dmc/v6/family_batch.py`, so they at
    least COUNT as unbuilt instead of being invisible.

26. THE HVSC DISK IMAGES — MUSIC THE CATALOGUE DOES NOT INDEX (inventoried
    2026-08-28). ⚠ PARKED BY THE OWNER, WITH A TRIGGER: do not start this until
    ENGINE COVERAGE IS BROADER. The expectation — and it is the whole reason to
    wait — is that the subsongs inside span MANY engines we have not looked at
    yet, so depacking them early just converts one unbuildable form (packed)
    into another (an unmigrated engine). The work only pays once there is a
    decent chance of building what comes out.

    WHAT IS THERE. HVSC ships ten disk images at the root of the collection
    which `tools/build_sid_db.py` never sees, because it walks for `.sid`:

      10_Years_HVSC_2.d64    88 entries incl. **37 `musicN` PRGs** + articles
      10_Years_HVSC_1.d64    13 entries (intro, note, 1 bonus tune)
      10_Years_HVSC.d71/.d81 98 entries each — repackings of the same content
      20_Years_HVSC.d64      20 entries: the main binary + **17 tunes**, and
                             the directory art itself reads "m.17 exclusives!"
      HVSC_Intro_41..44.d64  1 program each
      10_Years_HVSC.dfi      NOT a disk image — header reads `DREAMLOAD FILE
                             ARCHIVE`; needs its own parser

    So ~54 tunes, against 61,157 already-extracted `.sid`. Small, but the
    20-Years disk explicitly claims exclusives, and if those are genuinely not
    in HVSC then nothing else has them in usable form.

    THE BLOCKER, measured: it is ALL PACKED. sidid identifies **0 of the 37**
    and **0 of the 17** as any player; the 20-Years main binary comes back
    `Crunched:Exomizer`; the tune files' load addresses are nonsense ($CD23,
    $3226, $551F). There is no shortcut — extraction needs depacking, either an
    Exomizer decruncher (well documented; py65 could run the depacker) or
    emulate-the-disk-and-rip. That is a capability the project does not have.

    ALREADY DONE, so it is not redone: `tools/cbm_diskimg.py` reads D64/D71/D81
    directories and extracts files by sector chain, validated against the BAM
    disk names (`hvsc`, `>hvsc 20 years!<`, `hvsc-intro 42`, ...). It stops
    exactly at the packed bytes.

    WHEN PICKED UP, in order: (1) depack; (2) classify what falls out with
    `sidid -m` — the catalogue now carries EVERY match in `engines`, so a
    multi-engine or sub-version verdict is available immediately, which is
    precisely the information this item is waiting on; (3) only then decide
    what enters the corpus, and how — these are PRGs, not PSIDs, so they need
    wrapping (init/play vectors) before anything in this pipeline can touch
    them, and `build_sid_db`'s walk would need to learn about them.

    ⚠⚠ ANSWERED 2026-08-28, AND IT LARGELY CLOSES THE CASE FOR THE 20-YEARS
    DISK. The "17 exclusives" are almost certainly ALREADY IN HVSC as `.sid`:

      * `DOCUMENTS/Update_Announcements/20160712.txt` — Update #65, dated the
        same day the disk's own directory art carries ("q. 12/07/2016") —
        says "we felt also the need to produce a music disk with EXCLUSIVE
        content to celebrate 20 HVSC birthdays".
      * The catalogue holds **exactly 17** SIDs credited `2016 ... HVSC`
        (16 `2016 HVSC` + 1 `2016 Maniacs of Noise/HVSC`) — an exact match to
        the disk's own "m.17 exclusives!" claim.
      * The convention is visible on the 2006 disk too (`2006 ... HVSC`
        credits), so "YYYY HVSC" in `released` is how HVSC marks
        anniversary-disk material once it enters the collection.

    NOT proven per-tune — the disk files are packed, so no fingerprint is
    possible without depacking, and that is the ONLY thing that would settle
    it. But an exact count match against an explicit claim of 17 is hard to
    explain otherwise. (Checked and found unhelpful: `Update65.hvs` records
    only REPLACE/MOVE/DELETE — new files just ship in the update tree, so
    absence there proves nothing; and STIL has no entries for these tunes.)

    THE 10-YEARS DISK IS LESS CLEAR: 37 `musicN` files against **29** tunes
    credited `2006 ... HVSC`. That disk never advertised a count, so it most
    likely mixed exclusive with pre-existing material, and the 8-file gap may
    be differently-credited, non-exclusive, or not one-tune-per-file. That gap
    is the only part of this item with unexplained content behind it.

    ⚠ AND IT INVERTS THE ITEM'S OWN PREMISE. The parking rationale was that the
    subsongs span many engines we have not migrated — which is TRUE and
    measurable: the 46 anniversary-disk tunes across both years span **17
    distinct engines**, GoatTracker_V2.x 15, DMC 5, Geir_Tjelta/SIDDuzz'It 4,
    Laxity_NewPlayer_V21 3, then Roland_Hermans / OdinTracker / GoatTracker_V1
    / John_Player / JCH_NewPlayer / Cyberlogic_SoundStudio 2 each, and
    TFMX / CheeseCutter / Asterion / Adam_Gilmore / TFX / SidFactory / Virtuoso
    once. Most are unmigrated. But that diversity is ALREADY AVAILABLE TO US in
    usable `.sid` form — depacking the disks would not reach a single engine
    the catalogue does not already expose. So waiting for broader engine
    coverage no longer buys this item anything.

    NET: the strongest motivation (unique music nothing else has) is refuted
    for the 20-Years disk and weakened for the 10-Years one. What survives is
    the 8-file 2006 gap and completeness. RECOMMEND: keep parked, but as a
    curiosity rather than a corpus-growth item; if it is ever picked up, do the
    10-Years gap FIRST (identify which 8 of the 37 have no `2006 ... HVSC`
    counterpart) — that is the only part where new content might exist, and it
    needs the depacker just the same.
