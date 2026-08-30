# BACKLOG — the SIDfinity OPEN-WORK list (pruned 2026-08-21)
#
# TRACKED IN GIT since 2026-08-24. It previously lived in the gitignored
# scratch dir — one `rm -rf tmp` from gone, and it is the only record of a
# dozen measured-but-unfinished investigations. Moved to the repo root and
# tracked for exactly that reason.
#
# NEXT_ITEM: 36   <- autoincrement: a NEW item takes this number, then bump it.
#
# CONVENTIONS (owner-set 2026-08-28):
#  - A done item is REMOVED COMPLETELY — no tombstone, no summary line. The
#    record of what it was and how it resolved is `git log -p backlog.md`.
#  - Numbers are NEVER reused; gaps are normal (6, 19, 21, 24 are gone).
#    Other files may cite an item by number — a citation to a gap means
#    "resolved, see git history".
#
# Item 26 is a
# different kind again — PARKED HARD by the owner with a trigger (broad engine
# coverage, i.e. near the end of the project); it needs no decision, just time.

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
     and must not be reachable from USF even by name.
     (The "fix the registry note's false justification" sub-task is DONE:
     composer_params.json was corrected 2026-08-20, and 2026-08-28 the
     tripwire itself was written into `_digi_player_registry`'s docstring
     — the code site where row two would be added.)
     ✍ THE TRIPWIRE FIRED AND THE DESIGN IS WRITTEN (2026-08-29): two
     volume_4bit engines surfaced at once (Rayden_Digi ×17, Digi-Organizer
     ×131 — items 28/29 bucket A) and the parametrization is drafted at
     `docs/digi_parametrization_proposal.md`, awaiting owner approval.

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

14. BASIC_PROGRAM RESIDUE — the Bond_Alan loopers (PARTIALLY LANDED
    2026-08-28; originally "investigated 2026-08-20, diagnosis only").

    ✅ LANDED — **Cascading FULL at its honest 288s window + mass-written**
    (27,152/27,152 writes), recovering the lost pw-sweep portfolio carrier.
    The 2026-08-20 design (per-note instrument SweepEnvelope) turned out
    UNNECESSARY, and its premises measured false: the ramps are a ~19-shape
    LIBRARY (several non-constant-rate), and the song does NOT fold even
    with PW ignored (635/720 unique note-sigs — through-composed play-once).
    What was actually wrong, three stale caps in sequence (each masked the
    next):
      (1) `_capture_pw_program`'s `len(tab) <= 255` gate — OUR 8-bit
          offset+tick encoding, not the signal (ledger C8: whose cap is
          it?). V1/V3 at 288s need 392/284-byte tables. Fix = per-section
          16-BIT pointers (`pwsoflo/hi` -> `($FD),y`), sections still
          X-indexed <=255. Also fixed a latent rep>255 truncation (min(255)
          while advancing by the full run).
      (2) the best_attempt ladder never ran the modulation rung on an
          `image_too_big` base failure — but image_too_big IS the modulation
          symptom (unstripped staircase -> 7.6k unfoldable sub-steps).
      (3) both verify extenders capped the extended capture at a flat 240s
          (the 120s-batch-cap era, C20 eighth layer) — for reb_dur=280s the
          "extension" SHRANK the capture and could only fail. Ceiling is now
          `dur + 60`.
    USF: wide programs use the existing `bp_sweep{vc}_values/sections`
    string form (packed s{i} masks offsets to 8 bits — writer now falls back
    to strings when off>255, reader already prefers strings; narrow members
    byte-identical). No schema change.

    REMAINING (the actual residue now): Legion_of_One + Pepper_Spray moved
    from `image_too_big` to REAL divergences — the modulation model builds
    tiny (3.2KB/8.3KB, all four channels incl. $D416) but verifies
    `overlap_diverge` at m=1582/15999 (Legion). First lead: their V1
    programs start at non-zero bases (Legion v1: `3,4..0xA` repeating —
    ramps 3..10, not 0-based) and Legion's v1 capture collapses to 8B/3sec
    (suspiciously tiny vs 3,903 writes) — the free-running RLE may be
    folding a phase-shifting staircase wrongly. Localize with
    find_first_divergence at write 1582.

    ALSO OWED: the full bp re-batch (all 524 rows code_hash-stale after
    these edits) — queued behind the DMC overnight chain; and the portfolio
    re-derivation AFTER it (the pw-sweep dimension can then re-enter via
    Cascading; `_excluded` Medley_BASIC note says re-derive post-batch too).

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

23. DMC: THE ED-LINEAGE PLAYER ZOO among the unrouted (RESCOPED 2026-08-28 —
    the original premise was WRONG and is recorded here so it is not re-tried).
    This item used to claim ~30 members are "the CANON v5 body behind a
    lead-in wrapper", so only detection needed to see past the wrapper.
    MEASURED while landing item 22: FALSE. The cluster-B members (e.g.
    `Ed/Bouncy_Funk`, `Ed/A_Quoi_Ca_Sert`, head `4C 40 xx / 4C A5 xx`, play
    entry `A9 00 F0 04 CE <slot> 60 AA A5 F8 48 A5 F9 48 CE <spdctr> ...`)
    share We_Were_All_Kids' PLAY-HEAD IDIOM but their bodies are ~3%
    byte-identical to WWAK's player (and to canon v5) — each is another
    hand-built Ed-lineage player, like WWAK and Choices before it. That is a
    per-player site-map / reference job (a small migration each, or one
    generalized Ed-lineage detector), NOT a detector tweak.

    Post-item-22 residue census (tmp/f4_recovery.log, over the then-308
    unrouted): 47 claimed:family4 (item 22's recovery), 148
    player_code_mismatch, 113 no_jumptable. The Ed zoo is inside the 148;
    the 14 no-player-in-image members (C26, e.g. `Bakewell_Dwayne/
    Misfortune`) are inside the 113. Cluster reps + heads in
    tmp/unrouted_bigcluster.txt.

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
    standard entry) rather than an investigation.

    ✅ FIRST STEP DONE 2026-08-28: `dmc_v6` store registered
    (tmp/dmc_v6_results.jsonl) + `pipelines/dmc/v6/family_batch.py`, an
    ACCOUNTING batch recording each member `unsupported: no_composer` under the
    current dmc_v6 fingerprint. The family now reads **0/16** instead of being
    invisible, and `route.py --gaps` is fully clean for the first time. When the
    composer is built, replace `run_member` with the real chain (v5's batch is
    the template) — the store id and file name stay, and the accounting rows
    auto-invalidate (the composer lands inside the hashed closure).

    REMAINING: the migration itself — v6 extract/to_usf completion + a v6
    composer.

26. RIP THE HVSC DISK MAGS WITH OUR OWN PIPELINE — a CAPABILITY DEMO for near
    the end of the project. ⚠⚠ PARKED HARD, ON PURPOSE. This is not corpus
    growth and must not be resurrected as if it were (see REFUTED below). It is
    a capstone: take a packed C64 disk magazine, and produce a `.sid` for every
    tune in it, end to end, through this project's own machinery.

    WHY IT IS A GOOD DEMO. Every other member we have ever built arrived
    pre-ripped: someone else already found the player, set the init/play
    vectors and wrapped it in a PSID header. A disk mag gives none of that. The
    exercise is the whole pipeline against raw material — depack, find the
    player(s), identify each one, lift to USF, compose back, and verify against
    the original's write stream. If it works, the claim "this project can
    convert SID music generally" stops resting entirely on inputs someone else
    prepared. It is also the natural place to find out what the pipeline
    assumes about PSID that raw PRGs do not provide.

    THE TRIGGER: broad engine coverage, i.e. late. Measured reason — the 46
    anniversary-disk tunes span **17 distinct engines** (GoatTracker_V2.x 15,
    DMC 5, Geir_Tjelta/SIDDuzz'It 4, Laxity_NewPlayer_V21 3, then
    Roland_Hermans / OdinTracker / GoatTracker_V1 / John_Player / JCH_NewPlayer
    / Cyberlogic_SoundStudio 2 each, and TFMX / CheeseCutter_2.x / Asterion /
    Adam_Gilmore / TFX / SidFactory / Virtuoso once). Most are unmigrated
    today, so attempting this now would mostly produce "we cannot build this
    player" — which demonstrates nothing. The demo only means something when
    the answer is expected to be yes.

    WHAT IS THERE (inventoried 2026-08-28). Ten images at the collection root
    that `tools/build_sid_db.py` never sees, because it walks for `.sid`:

      10_Years_HVSC_2.d64    88 entries incl. **37 `musicN` PRGs** + articles
      10_Years_HVSC_1.d64    13 entries (intro, note, 1 bonus tune)
      10_Years_HVSC.d71/.d81 98 entries each — repackings of the same content
      20_Years_HVSC.d64      20 entries: main binary + **17 tunes**; the
                             directory art reads "m.17 exclusives!"
      HVSC_Intro_41..44.d64  1 program each
      10_Years_HVSC.dfi      NOT a disk image — header reads `DREAMLOAD FILE
                             ARCHIVE`; needs its own parser

    THE FIRST OBSTACLE, measured: it is ALL PACKED. sidid identifies 0 of the
    37 and 0 of the 17 as any player; the 20-Years main binary comes back
    `Crunched:Exomizer`; the tune files' load addresses are nonsense ($CD23,
    $3226, $551F). So step one is a depacker — an Exomizer decruncher (well
    documented; py65 can run the depack stub) or emulate-the-disk-and-rip.
    That is a capability the project does not have, and building it is a real
    part of this item, not a preliminary.

    ALREADY DONE, so it is not redone: `tools/cbm_diskimg.py` reads D64/D71/D81
    directories and extracts files by sector chain, validated against the BAM
    disk names. It stops exactly at the packed bytes.

    ⚠ REFUTED — DO NOT RE-OPEN THIS AS A CORPUS-GROWTH ITEM (answered
    2026-08-28). The "17 exclusives" are already in HVSC as `.sid`:
    `DOCUMENTS/Update_Announcements/20160712.txt` (Update #65, the same date
    the disk's own art carries) says HVSC produced an exclusive music disk for
    its 20th birthday, and the catalogue holds EXACTLY 17 SIDs credited
    `2016 ... HVSC` — the same convention is visible on the 2006 disk. Not
    proven per-tune (only a depacker would settle it), but an exact count match
    against an explicit claim of 17 is hard to explain otherwise. `Update65.hvs`
    is no help either way — it records only REPLACE/MOVE/DELETE, so new files
    never appear in it; STIL has no entries for these tunes. The engine
    diversity above is likewise already available as ordinary `.sid`.
    => nothing here grows the corpus. The value is the DEMONSTRATION.

    A HAPPY SIDE EFFECT, since the tunes are already ripped: **we have ground
    truth**. Our pipeline's output for each tune can be diffed against HVSC's
    own hand-made rip — a far stronger check than "it plays". Which is
    precisely what makes this a good capstone rather than a stunt.

    ONE GENUINE LOOSE END if anyone wants a smaller bite first: the 10-Years
    disk has 37 `musicN` files against only 29 tunes credited `2006 ... HVSC`.
    That disk never advertised a count, so it likely mixed exclusive with
    pre-existing material — but those 8 are the only place unexplained content
    could sit.

27. THE USF EDITOR — a realtime, USF-native music editor (owner's vision,
    2026-08-29). ⚠⚠ PARKED HARD: post-Move-1 by nature (one interpreter wants
    ONE set of semantics; today there are N family composers + params knobs).
    Recorded now because the DESIGN back-propagates a preference into today's
    work (see the last paragraph, which is live guidance, not parked).

    THE VISION: load a .usf, hit play, see everything in realtime; "slow
    play" at any rate including PAUSE-WITH-SUSTAIN (the moment keeps
    sounding); instrument / wavetable / freq-table editors — a professional
    sound editor contextualized to SID + USF.

    WHY THIS PROJECT MAKES IT TRACTABLE (the parked design notes):
    - No C64 needed: the whole project proves the music IS the $D400-$D418
      write stream, fully determined by USF. Play = a USF INTERPRETER
      emitting writes into a SID emulator (reSID->WASM; websid/jsSID prove
      browser-rate 6581). The score interpreted directly, at any clock.
    - Pause-with-sustain is PHYSICALLY REAL on a SID, and it is the
      trichotomy's schedule/chip split made audible: freeze the sequencer
      clock, keep clocking the chip — oscillators run, sustain holds, the
      filter sits where the sweep left it. Any-rate play = scale the
      player-tick : SID-cycle ratio (time-stretch with zero pitch change,
      native). A third freeze depth falls out of our layering: hold the ROW
      clock but keep the EFFECT clock (note holds, vibrato keeps wobbling).
      Envelope time is chip time — "true" stretch wants an optional
      envelope-rate scale; both are artistic tools, expose both.
    - Total provenance for free: an interpreter over USF knows which entity
      caused every write (orderlist entry -> row -> instrument -> table step
      -> register) — playheads on the C1 sweep curves, wavetable cursors, a
      raw register lane. A debugger for music; no SID tool has the abstract
      layer to do it.
    - Export is already solved AND verified: edit -> USF -> the real
      composer -> a genuine .sid for real hardware. Demo: load Commando,
      change a note, export a working C64 SID.
    - Correctness reuses the oracle: for any UNEDITED usf the interpreter's
      stream must equal the composer's rebuild (compare_instruction_stream)
      — the editor engine is just another consumer gated by the verdict.
      (After an edit there is no original; correctness becomes CONSUMER
      EQUIVALENCE — interpreter == composer — a Move-1-era addendum to the
      core tenet if the editor is ever built.)
    - The editor is the HUMAN-facing form of the ML claim: every schema
      field must surface as a comprehensible control; a field you cannot
      build a sane widget for is a section-7/8 leak announcing itself. It is
      also the natural curation surface for model-generated USFs.
    - Honest costs: the interpreter must honor the reproduction tail
      (off-table records, C29 environment serves, wedge knobs — shown as
      read-only "authenticity" flags, some tunes "layout-locked"); the real
      expense is UI, not audio (the schema IS the data model).

    ⚑ LIVE GUIDANCE THAT IS *NOT* PARKED — the one thing this vision
    back-propagates into current development (owner asked; analysis
    2026-08-29): NO canon changes are required, but one TIEBREAKER is worth
    honoring today: when a residue fix can carry either a FROZEN MEASURED
    VALUE or the GENERATING RELATIONSHIP and both verify byte-identical,
    prefer the relationship — a frozen snapshot of emergent state is
    reproduction-only (undefined after any edit, unlearnable by the model),
    while a relationship recomputes. The ledger has been drifting this way
    on its own (C11's named-signal doctrine `own cursor + delta`, C1
    deconstructions, C19's 33rd-occurrence rule); this names the drift.
    ✅ LANDED IN CANON 2026-08-29 (owner-approved): the tiebreaker now lives
    in the Principle, end of section 9.

    THE ISOMORPHISM REQUIREMENT (owner, 2026-08-29 — a MOVE-1 DESIGN
    CONSTRAINT recorded here so the unified composer is designed for it from
    day one; retrofitting later is expensive, designing for it is cheap):
    the editor should load OUR OWN exported .sid files too, which wants a
    STATIC, BYTE-LEVEL ISOMORPHISM between canonical USF and the sidfinity
    .sid. Analysis:
    - The FORWARD direction already exists and is enforced corpus-wide:
      compose is deterministic and `corpus_sync.audit_rebuild` asserts
      build(stored .usf) == stored .sid. The BACKWARD direction (recover the
      USF from the .sid alone) is new.
    - It can only be an isomorphism UP TO CANONICAL FORM — and the machinery
      exists: usf_spec_lint's round-trip + canonical-fixpoint invariants
      define exactly the equivalence class the bijection targets.
    - It is the DUAL of the Principle's section 8. Section 8: the .sid must
      not contain MORE than the USF (no engine library completing it). The
      isomorphism: the .sid must not contain LESS (the composer may not
      consume USF content irreversibly). Together: the .sid IS the canonical
      USF in another encoding — the composer becomes a CODEC, not an
      encoder. This bounds (mildly) the Core Tenet's "any runtime
      architecture" freedom: the RUNTIME stays free, but the DATA layout
      must stay decodable (no constant-folding musical content into
      unrecoverable code shapes without a decode map).
    - FREE LEAK DETECTOR: `decode(build(usf)) == canonical(usf)` as a corpus
      gate would mechanically catch every section-8 / C7-class-A3 leapfrog —
      information flowing orig -> .sid around the USF makes decode recover
      content the USF never had, an immediate loud failure. This is the
      strongest argument for the requirement beyond the editor itself.
    - ✅ DECIDED (owner, 2026-08-29): option (b) — recorded as a standing
      Move-1 design decision in docs/the_move-1_plan.md ("the unified
      composer is a CODEC"). The shapes, for the record: (a) EMBED the
      (compressed) canonical USF in the .sid with the self-check
      build(embedded) == surrounding bytes — trivially lossless,
      self-verifying (immunized against C20's fifth layer: artifact and
      source cannot disagree), but costs C64 RAM since a PSID payload loads
      wholesale (fails only near-64KB tunes; ~3-8KB compressed); or
      (b) make the unified composer's emitted DATA TABLES a self-describing
      binary serialization of USF with a versioned site map — no RAM waste,
      no duplication, and "sidfinitid for our own player" falls out of the
      decode map. (b) is the elegant end-state; (a) is a sound bridge.
    - Measured values / reproduction baggage survive either shape fine (they
      are bytes); what breaks isomorphism is DERIVED-AND-DISCARDED content —
      which the tiebreaker above already steers away from.

28. DMC f1 NEW RESIDUE — the 23 partials + 2 errors surfaced by de-invisibling
    (assessed 2026-08-29 from the fresh batch rows + two probes; ⚠ probes ran
    UNDER FULL MASS-WRITE CPU LOAD, and an empty writelog capture under load is
    a documented siddump-death artifact — re-verify bucket A quietly first).

    BUCKET A — ✅ CLASSIFIED 2026-08-29 (idle-box re-verify + header census +
    writelog histogram): the 14 Rayden members are the **RAYDEN_DIGI
    HETEROGENEOUS CLASS** — the exact f1 twin of item 29's f2 Digi-Organizer
    bucket, and sidid already names it (`engines` column:
    `DMC|(DMC_V4.x)|Rayden_Digi_V1` ×13 / `_V2` ×3).
      * ONE mechanism across all 14, confirmed at the header level: every
        member is **RSID with play=$0000** — init installs its own IRQ and
        never returns; the tune drives itself (the "self-IRQ" branch of the
        old classification question; NOT C24 unit-repeat, NOT C18 F-phase).
      * What the extra writes are, measured (Boot_Zak_v2, 5 s of orig
        writelog): **41,314 of ~45k writes are $D418** with 4-bit values at
        ~63-cycle spacing (~1 write/rasterline ≈ 8-15 kHz) = VOLUME-REGISTER
        DIGI sample playback, while the DMC voice registers get a normal
        ~450 writes each. So: ordinary DMC music + a Rayden digi player on
        the same chip under a fast self-installed IRQ.
      * The [0,0] batch rows were indeed the under-load capture artifact; a
        quiet rebuild gives the honest shape (Boot_Zak_v2: play_match=1,
        len_a=910,492 vs len_b=73,058 ≈ 12.5×). Content-wise unfixable
        without emitting the digi stream — the $D418 writes interleave from
        frame 1, so flat compare dies immediately regardless of the music.
      * CORPUS CLOSURE: Rayden_Digi carriers are EXACTLY 17, all
        MUSICIANS/R/Rayden — these 14 partials + Popel_Premiere_Intr0h_2SID
        (the C27 params-merge error, also tagged V1) + 2 with no verdict row
        anywhere (unrouted): Embarassed_Emotions (DMC|V2) and
        Spelling_Around (V2 beside ROB_HUBBARD — not even a DMC member).
      * WHAT IT NEEDS = the same as item 29 bucket A: heterogeneous
        music+digi handling, Mode-2 cycle-strict verification for the digi
        part (core tenet: digi = cycle-exact), FLAC-sidecar PCM (C7-C), and
        the item-5 tripwire FIRES: Rayden_Digi is a volume_4bit technique →
        the owner-gated `digi { technique, rate }` parametrization, NEVER
        registry row two. ⚠ EFFECTIVELY OWNER-GATED at the representation
        step; design it ONCE for Digi-Organizer + Rayden_Digi together
        (13 + 17 carriers = the two biggest digi families after Chimera).
      * ✍ DESIGN WRITTEN 2026-08-29 (owner lifted the design gate):
        `docs/digi_parametrization_proposal.md` — both players RE'd
        (Rayden V1: CIA2-NMI 4-bit $D418, (sample,rate,duration) event
        stream on the DMC tempo clock, music $D418 stores patched to the
        shadow so THE DIGI OWNS $D418; Digi-Organizer: NMI nibble-packed
        4-bit, full orderlist+32-row-pattern channel, per-sample pitch
        latch — and it is 131 carriers CORPUS-WIDE, 51 beside MA).
        Recommendation: digi channel = a VOICE with sample instruments +
        `digi { technique, idle_level, or_mask }` + `rate_cycles`;
        verify split by $D418 ownership (music Mode 1 / digi Mode 2).
        AWAITING OWNER APPROVAL of the schema; then Digi-Organizer
        first, Rayden second.

    BUCKET B — start-of-stream divergences (match=1 on failing subtunes):
    Dark_Destroyer_2117 (known UNMERGEABLE compilation -> single fallback;
    subs 1-2 wrong data = C31 shape), Space_Eggs, Zyron/Bouncy_Balls (subs
    1-6), Praiser/Upside_Down (all 6 subs; Praiser = the Mega_Mix medley
    author), PVCF/Centric + Daf/Alioth (most subs), Flubble subs 0/4.
    Signature = per-subtune dispatch/data selection, the C31/C37 family.
    Tanks_3000 error `base_override_not_player: $1000` is the same story one
    step earlier (the compilation scan proposes a bogus base).

    BUCKET C — small real content divergences: Ed/Solved_Track (m=370),
    Party_Party (m=34), Flubble subs 1-3 (m=32/37), Alioth sub 0 (m=26),
    Centric sub 1 (m=32) — ordinary first-divergence grind, localize with
    dmc_build_one --localize each.

    These 25 ARE the formerly-invisible set — never batched before Aug 28, so
    none of this is regression; it is virgin residue with named shapes.

29. DMC f2 NEW RESIDUE — 14 partials + 1 error, dominated by ONE new class:
    the DIGI-ORGANIZER HETEROGENEOUS members (assessed 2026-08-29).

    BUCKET A — 9 members recorded `match=0, overlap=0`, and unlike f1's
    bucket A this is NOT (mainly) capture death: `engines` (the sidid -m
    column, first real payoff) says 7 of them are **DMC|Digi-Organizer** — a
    digi sample player packed beside the DMC music player. Corpus-wide the
    class is exactly 13: these 7 + Sax/Digi_Music + Justincase_part_6 (bare
    `DMC` label but almost certainly the same, unsignatured) in f2, and 5
    MORE in the unrouted 261 (Bakewell/New_Wave, Bayliss/Egg_Catcher,
    Doxx/Love_Is_in_the_Air, PVCF/Centric_end_sequence, PVCF/Giana_2). The
    original's stream is dominated by sample volume writes our build never
    emits -> ~zero overlap. WHAT IT NEEDS: probe the Digi-Organizer player,
    C31-heterogeneous handling + the digi pipeline (Mode-2 cycle-exact for
    the sample part; Chimera/FLAC-sidecar machinery exists).
    ⚠⚠ ITEM-5 TRIPWIRE FIRES HERE BY DESIGN: Digi-Organizer would be the
    SECOND digi engine — the owner-reviewed rule says PARAMETRIZE (a real
    `digi { technique, rate }` enum, composer synthesizes the player), NEVER
    add registry row two. That is an owner-gated schema design, so this
    class is effectively OWNER-GATED at the representation step.
    ⚠ UPDATE 2026-08-29: item 28's f1 bucket A turned out to be the SAME
    architectural class with a DIFFERENT digi player (Rayden_Digi_V1/V2, 17
    carriers, all RSID play=$0000 self-IRQ volume digi) — so the `digi {
    technique, rate }` design has TWO engine families waiting on it, 13 + 17
    carriers; design once for both (see item 28 bucket A for measurements).
    ✍ DESIGN APPROVED + LANDED (2026-08-29): schema in 532b3931
    (`digi{}` + sample_instruments + digi_voice, all gates green), the
    Digi-Organizer pipeline exists (`pipelines/digi_organizer/`,
    [[project_digi_organizer]]), and **Heavy-Beat is FULL Mode-2
    CYCLE-STRICT** (4,249/4,249 frames, 535k writes @ 99 s) through the
    parametric composer — no registry row two. NB Digi-Organizer is 131
    carriers CORPUS-WIDE (51 beside Music_Assembler, 39 standalone) —
    far bigger than the f2-adjacent 13.
    ✅ STANDALONE BATCH LANDED (2026-08-29 evening, f4dd2120): **21/39
    FULL Mode-2 cycle-strict, 18 unsupported (unprobed driver shapes),
    0 partial** — driver-class registry (irq_vec/nmi_first/xreg/
    bare_stub) + 4 cycle levers (base latch = NMI grid origin, Morton
    port pre-init, core-init tail, BIT filler) + C29 past-EOF PCM +
    content-addressed overlap dedup. Store `digi_organizer` registered.
    ✅ ROUND 4 (2026-08-30): **36/39 FULL, 0 unsupported, 3 partial**
    (re-batch, batch_diff 0 regressions). Every claimed member now
    BUILDS. Landed: the NTSC clock flag as Mode-2 signal (the two
    Sphere members — a raster tick runs at the FRAME rate, so the
    PAL default ran 5/6 speed; the parked "first-tick phase" was a
    header field), a code-barrier stop for an unterminated orderlist,
    a page-granular RELOCATABLE player block + PCM overlap join
    (Digimix_2's 152-page sample, Digibeatz_2's 12 windows into one
    recording), and the `rwait_lock`/`rwait_rts`/`song_head` driver
    classes. C40 grew a 3d (layout invariants inside mirrored init +
    the RSID load/init address rules, which fail SILENTLY).
    ✅ STANDALONE FAMILY CLOSED, same day: **39/39 FULL**. The last
    three partials were ONE cause — the engine clamps a sample row whose
    end <= its start to end = start+1 THROUGH A BRANCH, so two rows
    describing the same single page by different arithmetic play
    identical audio 2 cycles apart, which Mode 2 sees (ledger C40 3e;
    not derivable — the corpus has 19 explicit and 5 degenerate one-page
    rows). Closeout done: tier-1 portfolio (22 members / 34 dimensions)
    derived + wired into regression.py (summary AND exit code), and
    pipelines/digi_organizer/mass_write.py. Item 30's params
    consolidation landed with it (18 keys -> 15 while the class registry
    grew 11 -> 14, all byte-identical).
    NEXT: (a) the 92 music-paired members (C31-hetero + the
    $D418-ownership split verdict); (b) Rayden_Digi (item 28) on the
    same schema.

    BUCKET B — per-subtune start divergences (the C31/C37 family, same as
    f1's bucket B): Andy/Jumping_Jack (6 subs m=1), Riot/Enzyme (subs 1-8
    m=1), Bayliss/Stealth_4 (sub 0 m=1; subs 1-5 m~27-32 with overlap ~3.9k
    = far short too), Grid_Zone_Remix sub 2 (m=6510, deep — this is the
    hetero_v5 + ambiguous-claim + sidid-disagreement member, every odd list
    this week). Last_Amazon error `base_override_not_player: $2000` = same
    family, one step earlier (also ambiguous v4/v5).

    All 15 are formerly-invisible members — virgin residue, no regressions.
    Cross-ref: f1 counterpart assessment = item 28.

31. CODE_FINGERPRINT'S TEST-SELECTION EXCLUSION IS INERT FOR 6 OF 7 FAMILIES

    ==== MEASURED 2026-08-30 22:30 (tools/fingerprint_policy_probe.py,
         tools/verdict_staleness_probe.py
         — read-only; the replica hasher self-checks against the real
         code_fingerprint() for all 8 engines before any number below) ====

    THE BLOCKING RATIONALE BELOW IS NO LONGER TRUE, AND THE WINDOW IS OPEN
    NOW. This item says the fix must wait for a planned batch because it
    moves six families' keys at once and a migration refusal means ~16 h of
    re-batching. Measured: **8 of the 9 verdict stores are ALREADY 100%
    stale**, and `migrate_verdict_rows` ALREADY refuses every one of them
    under EVERY policy including "change nothing" — because the digi
    parametrization schema landed on 2026-08-29 16:40 (532b3931 + 98484692,
    touching src/usf/{types,grammar,parser,writer}) AFTER those stores were
    stamped. So for those eight, landing this fix costs exactly nothing:
    they are already in the state the fix was feared to cause.

      dmc_v4   f1 5475 rows / f2 2944   stamped 08-29   100% stale
      dmc_v5      2078 rows             stamped 08-29   100% stale
      dmc_v6        16 rows             stamped 08-28   100% stale
      fc_standard 4140 rows             stamped 08-19   100% stale
      goattracker_v1 1387 rows          stamped 08-18   100% stale
      basic_program  524 rows           stamped 08-29   100% stale
      music_assembler 6489 rows         stamped 08-19   100% stale
      digi_organizer   39 rows          stamped 08-30   ALL CURRENT

    The one family with current rows is digi_organizer, and its migration
    CARRIES under every policy (0 closure files changed since its stamp).
    So the fix is free there too — 39 members, and no restamp even needed
    if it is re-batched instead.

    ⚠ MEMORY.md's "verdicts CURRENT" lines for DMC and basic_program are
    stale as of 2026-08-29 16:40 and should be re-marked.

    ==== AND THE STALENESS IS NOMINAL, NOT REAL ====
    A byte-identity spot check (rebuild the STORED .usf under current code,
    compare to the stored .sid — the CLAUDE.md carrier-refactor gate; same
    bytes => same write stream => same verdict) says the digi schema change
    moved NOTHING in the other families:

      dmc_v4       191/191 byte-identical, over ALL 7 build paths
                   (single/compilation/multisid/multiplex/medley/
                    hetero_masm/hetero_v5)
      dmc_v5        60/60
      fc_standard   60/60   (also spans the 2026-08-23 directory move)

    So the ~16 h re-batch is avoidable IF the owner accepts byte-identity
    as the proof. `migrate_verdict_rows` cannot express that today — it
    refuses on git CONTENT change and has no byte-identity mode. Adding one
    (`--prove-by-rebuild N`: sample N stored artifacts per family, restamp
    only on 100% identity, record the evidence in the row) is a smaller,
    safer piece of work than any re-batch and generalises to every future
    key change. NOT DONE HERE — it is a change to the restamp PROOF, which
    is owner territory.
    ⚠ It proves nothing about members with no stored artifact (non-FULL),
    which is exactly right: those get re-verified anyway.
    ⚠ music_assembler / goattracker_v1 have no stored .usf (no mass-write
    by design) so the check cannot cover them; basic_program has 489 but
    writes them from its batch with no corpus_sync, so it has no
    `audit_rebuild` binding to reuse.

    ==== TWO CORRECTIONS TO THE ANALYSIS BELOW ====

    (a) ⛔ EXCLUDING `docs/` IS UNSAFE — do not do it. Measured, a
        `/docs/` exclusion drops `pipelines/dmc/docs/*.bin`: the CANON
        PLAYER BINARIES the DMC factory dispatches and probes against.
        That is verbatim inclusiveness hole #1 in code_fingerprint's own
        docstring, closed on 2026-08-22 and re-opened by this. The docs
        instance must be fixed by DERIVING, never by a path exclusion.

    (b) DERIVING ALREADY FIXES THE MASS-WRITER INSTANCE, and that reframes
        the writer complaint as a symptom. Measured per family, adding
        `mass_write.py` to the exclusion changes the key ONLY for dmc_v6
        and digi_organizer — the two families with NO entry in
        engine_deps.json, which therefore fall back to the declared
        directory glob. For the six derived families the batch never
        imports its writer, so it is already outside the closure. Same for
        the digi docs prototypes. So:

          the portfolio instance  -> needs the suffix typo fixed; derivation
                                     does NOT fix it (portfolios enter via
                                     `_declared_data_files`, which globs the
                                     declared dir for non-.py files and
                                     applies the same suffix filter)
          the writer instance     -> derivation fixes it
          the docs instance       -> derivation fixes it

        COMPLETE FIX = the one-line suffix correction, PLUS a derived entry
        for digi_organizer and dmc_v6. Not "grow the exclusion list".

    ==== WHICH KEYS MOVE (policy B = suffix typo fixed) ====
      MOVES: dmc_v4 dmc_v5 dmc_v6 fc_standard basic_program
             music_assembler digi_organizer          (7, not 6 — dmc_v6 too)
      same:  goattracker_v1                          (no portfolio file)

    ==== NON-usf INPUTS THAT ALSO CHANGED (a real re-batch, not nominal) ====
      dmc_v4 / dmc_v5 / goattracker_v1 / basic_program: src/usf ONLY
      dmc_v6:          + route.py, v5/factory.py, v6/family_batch.py
      fc_standard:     + family_batch.py, standard/config.py  (both the
                         08-23 move's path fixups; byte-identity says the
                         builds are unchanged anyway)
      music_assembler: + family_batch.py, locate.py           (ditto)

    (original entry follows)

    (measured 2026-08-30). `_SELECTION_SUFFIXES` in src/code_fingerprint.py
    excludes portfolio files from the hash so that re-deriving a portfolio
    cannot invalidate a family's verdicts — its comment says "matched by
    suffix so a new family's portfolio is excluded automatically". It is
    matched as `rel.endswith('_regression_portfolio.json')`, with a literal
    LEADING UNDERSCORE, and only ONE portfolio in the repo has one:

      HASHED   pipelines/digi_organizer/regression_portfolio.json
      HASHED   pipelines/future_composer/regression_portfolio.json
      HASHED   pipelines/dmc/regression_portfolio.json
      EXCLUDED pipelines/dmc/f2_regression_portfolio.json
      HASHED   pipelines/dmc/v5/regression_portfolio.json
      HASHED   pipelines/basic_program/regression_portfolio.json
      HASHED   pipelines/music_assembler/regression_portfolio.json
      EXCLUDED pipelines/dmc/roster.json

    So the documented protection has never applied to dmc_v4, dmc_v5,
    fc_standard, basic_program, music_assembler or digi_organizer: for all
    six, re-deriving the portfolio moves the family key and marks every
    stored verdict stale — which is backwards, since choosing a different
    regression SAMPLE cannot change what the composer emits. CLAUDE.md tells
    you to re-derive "whenever a new fix lands a big new clump of FULLs", so
    this fires often.

    FIX is one line: `_SELECTION_SUFFIXES = ('regression_portfolio.json',
    'roster.json')`. NOT DONE HERE because it is a KEY-DEFINITION change:
    measured, it moves the key for all six families at once (goattracker_v1
    unaffected — no portfolio file), so it must land with
    `tools/migrate_verdict_rows.py` in the same step, and a refusal there
    means re-batching a family (~16 h for DMC on the X230). Sequence it with
    a planned batch, the way the #85 rename was. Until then the workaround is
    to derive a portfolio BEFORE the batch that stamps the rows the
    mass-write will read, not after.

    Found because digi_organizer's mass-write refused all 39 current rows
    right after its portfolio was derived.

    ⚠ THE PORTFOLIO IS NOT THE ONLY CONSUMER LIVING IN THE HASHED DIR, and
    the exclusion list names only artifacts, not tools. `mass_write.py` sits
    in `pipelines/<family>/` for every family that has one, so EDITING A
    MASS-WRITER invalidates that family's verdicts — measured the same day:
    a one-line fix to digi_organizer's writer stranded a 39/39 batch that
    had just finished, and the same shape holds for `pipelines/dmc/
    mass_write.py` against ~8,400 DMC rows. A writer cannot change a
    verdict by construction (it consumes rows and emits artifacts; the
    verifier never imports it), so it belongs outside the closure with the
    portfolio. That is an argument for DERIVING the set (tools/derive_deps.py
    measures the real per-(engine, consumer) closure and would simply never
    see a writer the batch does not import) rather than growing the
    exclusion list by hand — digi_organizer currently has no entry in
    tools/engine_deps.json and falls back to the declared directory glob.
    Whichever way it lands, it is the same KEY-DEFINITION change and wants
    the same migration step.

    ⚠⚠ THIRD INSTANCE, and the one that shows the real shape of the bug: it
    is not "tools that live in the hashed dir", it is EVERYTHING that lives
    there. Committing two RESEARCH PROTOTYPES into
    `pipelines/digi_organizer/docs/` — which CLAUDE.md names as the home for
    per-engine research material — invalidated all 39 freshly-earned
    verdicts. So the declared closure currently says a family's verdicts
    depend on its own documentation. Three instances in one day, each
    costing a re-batch: the portfolio, the mass-writer, and now the docs.
    The declared set is `['pipelines/<family>', ...shared]` — a whole
    directory — and the only files in it that can actually change a verdict
    are the extract, the composer and their shared imports, which is
    precisely what `tools/derive_deps.py` measures. That is the argument for
    deriving rather than for extending the exclusion list one suffix at a
    time.

32. OWNER DECISION — SAMPLE WINDOWS: the USF cannot say "these instruments
    are slices of ONE recording", so it stores the slices (measured
    2026-08-30, digi_organizer closeout). A sampler musician's ordinary
    move is to record once and carve several instruments out of it at
    different offsets; Morton/Digibeatz_2 does exactly that with TWELVE
    overlapping windows into one recording. `SampleInstrument` names a
    whole FLAC and nothing else, so to_usf emits twelve separate sidecars
    whose audio overlaps: **429 pages stored for 216 pages of sound**.

    The composer currently recovers the relationship CONTENT-ADDRESSEDLY at
    build time (`_cluster_blobs`, C40 3d): it byte-compares the blobs, finds
    the page-aligned overlaps in either direction and stacks them back. That
    works — the member is FULL, and without it the family could not have
    closed, since 429 pages exceed the machine's free RAM. But it is
    recovering by inference what the format threw away.

    WHY IT MATTERS BEYOND SIZE (Principle §9 tiebreaker, "the relationship
    over the frozen measurement"): twelve near-identical audio blobs are
    unlearnable — a model can only memorise them, and they are semantically
    undefined the moment anyone edits the music (edit the recording and the
    twelve copies silently disagree). The relationship "one recording,
    twelve windows" is the musical fact, and it is the fact a sampler user
    would recognise.

    SHAPE OF THE FIX (needs approval — a typed-field addition):
    `SampleInstrument { sample, offset, length, rate_cycles }`, with
    offset/length elided at their defaults so every existing member's .usf
    is unchanged and the corpus stays readable. The extract already knows
    the windows (it reads start/end pages from the engine's own table); the
    composer's clustering then becomes a placement detail rather than a
    reconstruction. NB it interacts with C40 3e's `digi_onepage_rows`: both
    are facts about how the sample TABLE was written, and a typed window
    might absorb the one-page-row distinction as `length == 1` vs an
    explicit end — worth checking before designing either further.

    EXPOSURE: 39 standalone digi_organizer members today (12 windows in
    Digibeatz_2, 24 of 39 members carry at least one shared range); the
    92 music-paired members are unmeasured; Rayden_Digi is the next family
    on the same schema and will have the same authoring idiom.

34. ⚠ DIGI_ORGANIZER'S 39 STORED .usf DO NOT REBUILD THEIR STORED .sid
    (measured 2026-08-30 22:37, found while measuring item 31; the family
    was declared CLOSED and mass-written this morning). Rebuilding each
    stored `.usf` under current code raises on ALL 39:

      DigiComposeError: driver overshoots its cycle budget by 6
      (pipelines/digi_organizer/composer_asm.py:575)

    CAUSE — tonight's universal-driver parametrization (c999ff81 20:23
    through c42e5e6c 21:39) replaced the driver's params surface. Diffed
    on 2NY/Heavy-Beat, stored vs a fresh extract:

      stored (09:38)          fresh (now)
        digi_driver: irq_vec    digi_drv_cyc / digi_drv_pcyc / digi_drv_post
        digi_tick_d011: 27      digi_drv_pre / digi_drv_tail / digi_drv_wrap
        digi_tick_raster: 129

    The mass-write ran at ~09:38, BEFORE the driver work. The batch re-ran
    at 21:44 and reports 39/39 FULL with a current code_hash — correctly,
    because a batch EXTRACTS FRESH and never reads the stored .usf.

    So: rows current, artifacts stale. Ledger C20 third layer, in its
    exact documented shape — and invisible to every other gate:
      * code_hash    — green (the rows really were earned by current code)
      * corpus_check — green (the old .usf still PARSES; the dead keys sit
                       in the wild `params` bag, which is why nothing
                       type-checks them)
      * regression   — green (portfolio members build from a fresh extract)
    The ONE gate that sees it is `corpus_sync.audit_rebuild`, which
    digi_organizer's mass_write.py already binds (--audit) — it simply has
    not been re-run since the driver landed.

    FIX (cheap, 39 members): re-run
      python3 pipelines/digi_organizer/mass_write.py --audit 12
    NOT DONE TONIGHT — it mutates the stored corpus, and the owner may
    want to look at the universal-driver work first. Deliberately left for
    a waking decision rather than done unattended.

    GENERAL LESSON, worth more than the incident: a family closeout has
    TWO write-side steps that can drift apart — the batch (verdicts) and
    the mass-write (artifacts) — and a composer change lands between them
    silently. The rule "re-run the mass-write after ANY composer change,
    not just after a batch" belongs in the closeout checklist. Note also
    that basic_program, music_assembler and goattracker_v1 do not use
    corpus_sync at all, so they have no audit_rebuild binding and this
    class is currently undetectable for them (basic_program has 489 stored
    .usf written inline by its batch).

35. REVIEW THE UNIVERSAL DIGI DRIVER (landed 2026-08-30 20:23-21:39, not yet
    reviewed). Five commits in ~3 h replaced the 14-entry driver CLASS
    REGISTRY with a generic instruction-walk decoder plus one parametric
    emitter: c999ff81 (design), 329dbdbc (12/14 shapes), 18be3c62 (delay-loop
    family, 14/14), d58ca2cb (no register assumptions after the core call),
    c42e5e6c (sub-JMP entry). Net −978/+829 across
    `pipelines/digi_organizer/{extract,composer_asm,to_usf}.py`, plus a
    rewrite of ledger C40's points 1-2 (6acb76fd). Verdict at the time:
    39/39 FULL, batch_diff 0 regressions.

    WHY IT WANTS A REVIEW: the motivation was correct and canonical — a
    registry of named code templates indexed from the USF is a Principle §8
    leak, and C40 now says so. But the replacement carries the driver as
    nine `digi_drv_*` params, and the question is whether those are MEASURED
    FACTS or the same library with a better story. What a member actually
    stores today (2NY/Heavy-Beat):

      digi_drv_pre: "SEI@0,01=35@4,IRQ@15,dc0d=81@21,R:dc0d@25,d012=81@31,
                     d011=1b@37,dc0e=00@43,d01a=01@49,d019=01@53"
      digi_drv_wrap: "save,ack=asl,tick,read=dc0d,restore,rti"
      digi_drv_post: "CLI@0"   digi_drv_tail: rts
      digi_drv_cyc: 65         digi_drv_pcyc: 2

    That is an ordered list of machine operations with cycle offsets. The
    owner REJECTED an earlier form of exactly this shape during the session
    ("an ordered write-list plus a cycles-to-core number — distilled
    machinery rather than anything the audio needs; that is the original's
    instruction sequence as data"), and three experiments then reshaped it.
    The review question is simply whether the landed form actually cleared
    that bar or converged back onto it. Principle §3 (Pole B: complete but
    unlearnable) and ledger C7 category B (opaque blob in USF) are the
    tests; `the_principle.md` §9's four tests are the gate.

    ⚖ THE HONEST COUNTER-ARGUMENT, to weigh rather than dismiss: digi is
    Mode 2, where cycle position IS the signal, so SOME temporal facts must
    reach the composer — a fully "musical" digi representation that drops
    them cannot verify by construction. So the question is not "should
    temporal facts be carried" (yes) but "is this the MINIMAL set of
    observable temporal facts, or a transcription of the original's
    instruction stream?" C40's own wording — "match the cycle SCHEDULE, own
    the code; producing the same schedule does not require producing it the
    same way" — is the standard to hold it to.

    SPECIFIC THINGS TO LOOK AT:
      a. All nine are registered `temporal-dispatch` in composer_params.json.
         Is that right for each? `digi_drv_wrap` ("save,ack=asl,tick,
         read=dc0d,restore,rti") reads as a CODE SHAPE, not a time.
      b. `digi_drv_subjmp` landed at 21:39 as a late fix. How many carriers?
         A single-carrier knob is the registry re-forming one row at a time
         — the speculative-generality tripwire already recorded in item 5.
      c. Does ledger C40's rewritten card match what SHIPPED, or what was
         intended at 19:38 when it was rewritten (before 3 of the 5 commits)?
      d. The two prototypes committed into `pipelines/digi_organizer/docs/`
         (c431fb6e) are item 31's third instance — do they still earn a place
         beside the family now the work has landed?
      e. 39/39 FULL was measured on FRESH extracts; item 34 shows the stored
         artifacts never rebuilt. Re-run the mass-write as part of accepting
         this work, not separately.

    NOT URGENT: the family verifies, nothing is blocked on it, and the
    coverage claim is honest. This is a design review of a fast, large,
    canon-adjacent change — exactly the kind that should not be self-
    certified by the session that wrote it.
