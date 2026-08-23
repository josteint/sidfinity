# Post-project research ideas — what the artifact enables

**Status: not work. A parking lot.** Nothing here is scheduled, and
nothing here should displace the grind (CLAUDE.md: engine by engine to
full family coverage; Move 1 waits for the owner). This file exists
because the ideas came up in conversation (2026-08-22) and are worth not
losing — they are the *byproduct* case for the project: what a completed
USF corpus makes possible beyond ML training data.

The framing that generated it: *"if/when we reach the project goal, we
would have produced an artifact we could use to make a lineage map of
players, and many other things of interest to historians."* That is
true, and some of it is already latent in the repo today.

---

## 1. Lineage is TWO maps, and we have machinery for both

This is the distinction to keep straight, because the two live on
opposite sides of the pipeline.

**Player-code lineage — the extraction side, not USF.** USF deliberately
abstracts the player's code away (that is the whole point of the Core
Tenet), so code phylogeny cannot come from the corpus. It comes from the
tooling we built to *read* the binaries:

- `pipelines/future_composer/engine_fingerprint.py` — reloc-invariant player-body skeleton
  fingerprinting. This is what established that 91% of HVSC's
  FutureComposer is one vanilla "standard" player.
- `pipelines/dmc/canon_diff.py` — linear-aligns every member's reachable
  player code against a canonical player binary, diffs opcodes and
  in-player operand repoints, clusters by site. That is a *collation
  tool*: it produces, per member, the set of deviations from the
  reference.
- The wedge knobs recorded per member in each family's config/params —
  effectively a coded transcription of those deviations.

Turning this into a tree is a small step from what exists. Precedent
in-repo: the Hubbard clustering (backlog item 15) showed the
unmigrated Hubbard mass is not a long tail but three distinct
*generations*, in one afternoon's measurement.

**Musical lineage — the USF side.** This is the half the binaries cannot
give you: cover versions, remixes, quotation, self-plagiarism, and an
author's style surviving a move from one editor to another. Comparable
across engines by construction, because that is exactly what the
Principle's parametric-over-a-musical-basis rule buys.

---

## 2. The wedge census is already scene ethnography

Per member we know which player patches it carries. The carrier-count
distribution separates two very different phenomena:

- **High counts = a circulated player variant.** 661 carriers of one
  gate-handling variant, 176 of a rest-effects variant, 140 of a
  play-phase wrapper. That is one modified player build passed around a
  group or a release chain and used for every tune its owner made.
  Family 2 itself is this phenomenon one level up: a whole variant build
  of the DMC player with remapped command bytes.
- **Low counts (1–3) = a one-off hack.** One musician, one evening, one
  tune — the singletons chased during the f2 grind.

Cross that with HVSC's author/group metadata and you have a map of who
modified their tools, how, and how those modifications propagated: a
social history of practice, evidenced at byte level rather than recalled
in interviews decades later.

**The making-of evidence is also readable from the bytes.** Almost all
wedges are in-place and *the same length* (opcode swaps, operand
repoints, patched immediates, stores NOPed or aimed at a void address) —
the signature of a freezer-cartridge machine-code monitor, not source
reassembly. New code is appended after the music data with a vector
re-pointed to it. A minority of members are genuinely re-assembled. In
archaeology's terms this is a *chaîne opératoire* reconstruction, and it
is already implicit in the ledger's C19 catalogue.

---

## 3. Other studies the corpus supports

- **Editor market share over time**, per scene group — engine
  classification joined to HVSC dates/authors.
- **Instrument-preset diffusion**: editors ship default instruments. Do
  authors modify them? Which presets propagate between groups? Our
  instrument records are typed and comparable, and dedup keys already
  exist.
- **Attribution for HVSC's unknowns** (stylometry): instrument
  fingerprints + wedge signatures + structural habits.
- **Cover/remix detection at the musical level** — e.g. the ten-plus
  members named `James_Bond` by different authors; with USF you can
  actually compare the notes.
- **Playback-practice history**: adoption curves for multispeed timing
  and for filter use (which is chip-model dependent, so it is a
  taste-versus-hardware story).
- **Preservation**: a verified round-trip means the corpus is
  re-renderable without the original binaries.

---

## 4. The preservation finding we stumbled into

Worth writing up on its own, because it is a claim stronger than the
usual hand-wave about hardware dependence:

**A nonzero number of these pieces are not self-contained works.**
Ledger C29 covers members that *sonify the machine's environment* —
notes read out of banked-in KERNAL ROM; a melody whose pitch is
psiddrv's patched reset vector; sectors that play the power-on RAM
stripe because the `$FF` fill they land in *is* the terminator the
player needs; a loop target read through a null pointer into live zero
page. For these, "the composition" and "the machine state" are not
separable, and we have a *measured list* of them rather than an
anecdote.

Related, and equally concrete: several members play bytes that are the
author's own credit text. ⚠ NOT the PSID header's `name`/`author`/
`released` fields — those are CONTAINER metadata added by rippers
decades later, and the emulator loads only the payload from
`dataOffset`, so the header never enters C64 RAM and the player cannot
read it. This is the author's handle stored INSIDE the C64 program
itself (standard scene practice — it shows up in a memory dump), sitting
in leftover space that the player's own code and state then overlap.
Two mechanisms:

- Over_and_Out stores "D BY ARTHUR/PRIDE'92**" at $1D60; the two
  trailing `*` land at $1D74/$1D75, which are exactly the song-chain
  countdown's two counter bytes. The init wrapper arms them only for
  subtune 2 (`CMP #$02`), so subtunes 0 and 1 count down from the
  ASCII leftover — 42*256+42 = 10,794 plays, 216 seconds — and then
  chain into the next song. The asterisks of a signature are the
  timer.
- A `$FF` track handler whose re-dispatch `JMP` is overwritten by
  author text: the text then EXECUTES (a `BVC` falls into the
  dispatch with A=$00) and injects a spurious note-0 row at every
  orderlist wrap (ledger C13, `loop_note_inject`).

---

## 5. What the Core Tenet COSTS — and creates — for historical work

Asked directly (2026-08-22): the Core Tenet abandons the original engine
and synthesises our own, judged only by write-stream equality. What does
that cost the research above, and what becomes hard *because of it*?

The costs are systematic, not incidental, and they all follow from one
fact: **our USF is a critical edition, not a facsimile.**

**The irony at the centre.** Our verdict can only see deviations that
change the write stream, so our record of engine variation is filtered to
the AUDIBLE subset — which is the phylogenetically LEAST informative one.
In stemmatics and in molecular phylogeny the valuable markers are the
variants under no functional pressure (a scribe's inert quirk, a
synonymous mutation): they propagate cleanly by copying, so they trace
descent. Ours are the opposite: every wedge we record was, by
construction, under selective pressure — and several we chased turned out
to be dead code, which we only learned by chasing them. The wedge census
of §2 is therefore a BIASED SAMPLE of deviations, and biased in the
direction that hurts lineage work most.

**Rule 1 erases the homology/homoplasy distinction by design.** "Three
byte-different 6502 routines that all produce the same triangle LFO are
ONE USF vibrato, not three." Correct for ML — you want the musical fact,
not the byte accident. Destructive for history: it removes exactly the
evidence that separates "these two authors' identical instruments are
identical because one copied the other" (homology) from "both landed on
the obvious setting" (homoplasy). USF normalises away the signal that
indicates copying.

**Structurally unanswerable from our outputs** (not fixable by trying
harder — it follows from what we chose to preserve):

- **Cycle-level timing within a frame.** Trap B makes intra-frame
  position observation, not signal (digi excepted). Raster-time sharing,
  hard-restart timing in cycles, 6581 write-timing tricks: not our layer.
- **CPU cost / raster budget.** Our play routine's cycle profile is
  nothing like the original's — proven the hard way in ledger C25, where
  our body overran a CIA latch the original fitted inside. "How expensive
  was this driver in a demo" is unanswerable from our artifacts.
- **Memory footprint and packing efficiency.** The 5 Title Tunes unified
  build is 38% the size of the compound one.
- **Code idiom as authorship signature** — SMC habits, routine ordering,
  register conventions. Destroyed by construction; we emit our own player.
- **The editor-level encoding** — command bytes, table layouts, what the
  musician actually saw and typed. C32's stated notation recovers
  authored STRUCTURE where the walk needs it, but USF is deliberately
  etic; it is not the editor's view.
- **Inert bugs.** A real bug in the original player that never reaches
  the chip is invisible to us.

**A caveat for anyone reading our USF as a score.** Ledger C34: a
mis-decoded packed-stream byte can re-emit to a byte-identical write
stream, so a member verifies FULL forever while the USF carries WRONG
musical content (a `tie` where the music rests). The oracle is blind to
it by construction; those are found only by reading the engine's handler.
So the corpus is **audio-faithful by proof, and musically faithful by
diligence** — a real distinction for musicological use.

**The editorial acts a historian would need declared:**

- **Rule 1's collapse** — variant mechanisms merged into one musical form.
- **The C19 33rd-occurrence rule** — a hack that changes a musical value
  is deconstructed INTO content. The durrel-ramp driver became per-row
  durations: the fact that it was a hack disappears into the music.
- **The C29 environment capture** — when a piece sonifies KERNAL ROM or
  the power-on RAM stripe, we capture those bytes AS musical content,
  making the piece self-contained in our representation. A defensible
  emendation (it is what lets the work play outside its original machine)
  but it fixes an accident into the text.
- **Selection bias** — the corpus is the members we can do FULL: biased
  toward migrated engines and, within them, away from hard-residue
  members. No statistical claim about "SID music" survives without it.

**Where to look instead.** Nothing is lost to the world: HVSC keeps the
originals, and the mechanism half is retained on our EXTRACTION side —
fingerprints, canon-diff deviations, per-member configs and probed wedge
knobs, batch verdicts. The right research artifact is therefore not the
USF corpus alone but **the join**: member -> (USF, config/params, wedge
set, code fingerprint, verdict). Music questions go left, mechanism
questions go right. Curating that join is the single cheapest thing we
could do for future research, and it needs no change to the pipeline.

**What the Core Tenet CREATES, which is worth more than what it costs:**

- **A canonical reference write-stream per member** — integer-exact,
  model-independent, and a better MIR substrate than either the binary or
  rendered audio (the register stream is the last exactly reproducible
  point in the chain; every serious SID tool operates there). Nothing
  like it exists publicly. This is §7's first item and it is
  Core-Tenet-native.
- **The residue catalogue.** Our list of what we CANNOT reproduce, and
  why, is a systematic inventory of engine behaviours that are not
  expressible as music — an empirical map of exactly where mechanism and
  music come apart. That is a research finding, not a failure log.

**Verdict: do not change the Core Tenet for any of this.** Preserving
mechanism inside USF is precisely the Principle §7/§8 leak, and the ML
goal is the project's reason to exist. The mitigation is curatorial, not
architectural: keep the extraction-side record joinable, and declare the
editorial policy above alongside any historical claim.

---

## 6. Honest limits (state these before any claim)

- **Coverage is uneven.** DMC v4 is complete (8,369 members); the
  largest families have no pipeline at all (GoatTracker V2 ~7,800,
  Soundmonitor ~3,700, JCH ~3,700). Any scene-wide claim drawn today
  would be DMC-shaped and would mislead. This is the single reason most
  of this file has to wait.
- **USF abstracts code away by design.** Code-lineage work leans on the
  fingerprint/canon-diff side; do not claim USF gives it.
- **Metadata quality is inherited.** Authorship and dates come from
  HVSC's credits, whose dominant edit between releases is precisely
  credit/title corrections (ledger C20's seventh layer). Claims inherit
  that uncertainty rather than resolving it.
- **Hacks have no provenance.** We can see *that* a wedge exists, not
  who made it. Musician versus demo coder is inference.
- **One ambiguous class we could not resolve**: the f2 `$FF` loop-to-N
  immediate ships non-zero in ten members, four by one author with
  *different* values each. Private player build with a loop-point
  option, or a habitual per-tune poke? Both fit the bytes.

---

## 7. Borrowed vocabulary — terms that fit, and what they name here

Useful for framing any future write-up, and for talking to historians
and musicologists in their own words. Three of the project's own
coinages are already borrowed terms of art: the **Convergence Ledger**
(evolutionary biology), `DMC_WITNESSES` in the portfolio code (textual
criticism's word for surviving copies of a text), and C20's
**palimpsest**.

**Textual scholarship** (the closest-fitting field):

- **Stemmatics** — reconstructing a manuscript family tree from shared
  copying *errors*, on the logic that idiosyncratic mistakes travel by
  descent while correctness does not discriminate. Exactly
  `dmc_canon_diff`: align to the canon, let the deviations group the
  members. Our wedges are scribal errors that happen to be deliberate.
- **Collation** — the systematic comparison of witnesses that produces
  the apparatus. The same tool, its other half.
- **Diplomatic vs critical edition** — a diplomatic edition transcribes
  one witness exactly, warts included; a critical edition reconstructs
  the work behind the witnesses. The project demands both at once: the
  Core Tenet requires diplomatic fidelity in *output* (the write
  stream), the Principle requires a critical edition in
  *representation*. Most hard calls live in that tension.
- **Urtext** — the work without editorial accretion. The C19
  33rd-occurrence rule is an urtext judgement made repeatedly: if a hack
  changes a musical value it is not accretion, it is the work, and it
  gets deconstructed into content rather than parked in a knob.
- **Conjectural emendation** — an editor's plausible guess at a corrupt
  passage. What the project systematically refuses (`dmc_state_addr`
  declining to name an address on non-canon geometry instead of
  returning a confident wrong one).
- **Lacuna** — a gap in a witness. Our residue.

**Evolutionary biology:**

- **Homology vs homoplasy** — same trait by descent vs independently
  arrived at. The Principle's Rule 1 in another language: three
  byte-different routines producing one triangle LFO are homoplasy and
  must collapse to one representation; f1/f2 sharing a player body is
  homology.
- **Vestigial structure** — persists, does nothing. Good_Beat's `$1512`
  wedge, proven dead by pc-watch. C30 is the sharper case: a flag bit
  the engine's priority renders mechanically dead, yet still *observable*
  through a state-as-data read — a vestige that leaves a fossil trace in
  the output.
- **Founder effect** — a small group's quirks dominating a population by
  descent rather than merit. The 661-carrier variant; family 2 itself.
- **Holotype** — the specimen that defines a name.
  `dmc4_player_embedded_1000.bin`.
- **Character matrix** — taxa × characters, the input to a phylogeny.
  `select_regression_portfolio.py` builds one (members × 93 feature
  dimensions). We use it to pick a test set; a historian would use the
  same object to draw a tree.
- **Cladistics vs phenetics** — informative shared characters vs overall
  similarity. Worth naming because we *proved* the phenetic version
  fails here: code-Jaccard clustering predicts nothing, since within a
  family the player is near-identical and behaviour varies by data.

**Archaeology and anthropology:**

- **Taphonomy** — what happens to remains between death and discovery,
  and how to subtract it. Everything between authorship and the HVSC
  entry: packers, rips, re-files, credit corrections, truncated copies.
  C20's seventh layer is a taphonomy problem, which is why identity had
  to be the payload hash rather than the file.
- **Chaîne opératoire** — the operational sequence reconstructed from
  manufacturing traces. See §2.
- **In situ vs ex situ** — every SID in HVSC is ex situ, ripped out of
  the demo it was written for. Medley and segment wrappers only make
  sense in situ, which is why they read as bizarre until you picture the
  demo around them.
- **Emic vs etic** — the insider's own categories vs the analyst's
  imposed frame. The Principle is a decision to be etic-but-musical:
  not the editor's categories (that leaks mechanism), not raw signal,
  but a frame comparable across engines. C32's "stated notation" is a
  deliberate step back toward emic.

**Historical linguistics and one philosophical:**

- **The comparative method** — reconstruct the proto-language from
  systematic correspondences among daughters. That is Move 1 exactly,
  with the ledger entries as cognate sets and the factor-candidates as
  its asterisked (hypothetical) forms.
- **Isogloss** — the map line where a feature stops. Wedge carrier
  distributions across authors and groups draw isoglosses.
- **Ship of Theseus** — identity through total material replacement. The
  composer keeps not one byte of the original player and the rebuild is
  nonetheless the same piece; the write stream is our answer to the
  puzzle, naming what must be preserved for identity to survive.

---

## 8. If this is ever picked up

Rough order, cheapest first:

1. **Publish the corpus as a community artifact.** A per-member,
   per-subtune reference write-stream corpus. Nothing like it exists;
   the emulator world's shared test suites (Lorenz, blargg,
   SingleStepTests) became infrastructure that third parties — including
   FPGA implementations — report against.
2. **The wedge census table** — carriers per wedge class joined to
   author/group/year. Already computable from the family batches and the
   stored configs.
3. **Player-code phylogeny** from `engine_fingerprint` +
   `dmc_canon_diff` distances, one family at a time.
4. **The C29 "not self-contained" list**, written up as a preservation
   note.
5. Musical-lineage work — only once coverage spans several families,
   for the reason in §6.
