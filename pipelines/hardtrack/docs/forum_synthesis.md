<!--
source_url: (synthesis across the forum_*.md sources in this directory)
fetched_via: WebSearch + WebFetch (see per-source docs for URLs)
fetch_date: 2026-06-13
authors/handles: (aggregate — see per-source docs)
content_date: 1992-2013
reliability: secondary (community discussion synthesis; primary spec = the
             local SDK RELEASE_NOTES + PLAYER V1.0/V1.1 sources, decoded by the
             sibling asm agent — NOT by this doc)
-->

# HardTrack Composer — community-discussion synthesis (forums/wikis/Usenet)

Aggregates the forums-and-Usenet research cluster. The detailed sources are
`forum_c64power_v2.md`, `forum_csdb_releases.md`, `forum_polish_scene.md`.
This file resolves the two questions the engine brief most needs from the
community layer — **version differences** and **how multispeed (≤6×) is
configured** — and records where the community DOES NOT help (so it isn't
re-searched).

## 1. Version map (community-sourced)

| Build | Authority | Authors | What it is for the parser |
|---|---|---|---|
| **V1.0** | CSDb #74928 (Elysium, 1992) | Brush (editor) + Longhair (player) | Baseline data format + baseline player |
| **V1.0+ "[6 speed]" / `v1.6speed`** | CSDb #36647 (Beverly Hills Grp) | Brush + **Glover** + Longhair | Same data format; player gains ≤6× multispeed |
| **V1.1** | c64power V2.0 thread: "Player 1.1 = original 1.0 format" | Longhair | Same data format; player-code revision |
| **V2.0** (beta ~2002) | c64power topic 4120 | abby_/Brush + Longhair | NEW: data/player decoupled, players 2.0/3.0/4.0, pattern-bar compression, tempo-change + global-volume opcodes. **Not present in HVSC V1.x.** |

**Bottom line for parsing:** V1.0, V1.0+/[6 speed], and V1.1 all share **one
song-data encoding** (the V1.0 format). The community is explicit on this point
("Player 1.1 = original 1.0 format"). So a **single V1.x parser** covers the
entire HVSC HardTrack set (~1,170 tunes). The only runtime variable across V1.x
is the multispeed rate. The V2.0-era additions (tempo/volume opcodes,
compression) should NOT be expected in HVSC data — if they appear, the SID is a
rare V2 capture and an outlier.

> The authoritative V1.0-vs-V1.1 player-code diff is in the local SDK
> `RELEASE NOTES!!!` + `PLAYER V1.0` / `PLAYER V1.1` sources (in
> `_artifacts/sdk/`), being decoded by the sibling asm agent. The community
> sources only assert the *data format is identical*; the byte-level player
> differences come from those sources, not from forums.

## 2. Multispeed (≤6×) — how it is configured

Two independent community signals:

1. **CSDb #36647** packages multispeed as a distinct **"[6 speed]"** player
   build (`v1.6speed`), authored with **Glover** added. So in V1.x the
   multispeed capability is a *player-build property* (a 6-speed-capable player),
   not a per-song data-format change. A multispeed tune is identified at the PSID
   level by its **CIA timer rate** (the play vector is called N≤6 times per video
   frame).

2. **c64power V2.0 thread** states the V2-family players "support multispeed via
   **jump point $1006**." This is the strongest concrete lead: in the V2 player
   family the multispeed sub-frame entry is a **third JMP vector at load+$1006**
   (after init $1000 / play $1003). Reported caveat: "Multispeed jump ($1006)
   partially non-functional in certain players."

**Action for the binary-decode agent (PRIORITY):** check whether the V1.x HVSC
players expose a third vector at **$1006**. Two hypotheses, decide by disasm:
- (H1) V1.x has a single `$1003` play that, when running at a multispeed CIA
  rate, advances the correct number of sub-steps internally (the $1006 vector is
  a V2 formalisation of behaviour V1.x did implicitly via CIA rate). OR
- (H2) V1.x already has the `$1006` sub-call vector and the 6-speed player just
  wires the CIA IRQ to call it. The `$1006` figure in the V2 thread strongly
  hints `$1003`/`$1006` were a stable convention even in V1.x.

Either way: **the per-SID multispeed factor is recoverable from the PSID/CIA
timer, capped at 6×** — it is NOT encoded as a song-data opcode in V1.x.

## 3. Where the community does NOT help (negative results — do not re-search)

- **comp.sys.cbm (Usenet):** no HardTrack/Elysium thread. HardTrack was a
  Polish-scene tool; English Usenet only discusses SID hardware generically.
- **Codebase64 wiki:** no HardTrack page; only generic SID-programming articles.
- **Lemon64 / forum64.de / ChipMusic.org:** HardTrack appears only in
  "list of C64 editors" mentions and beginner-recommendation context — no format
  or player detail. (Lemon64 was rate-limiting on 2026-06-13.)
- **DeepSID:** no HardTrack-specific player-ID or STIL technical notes.
- **CSDb forums (the discussion system, separate from release comments):** no
  HardTrack conversion/relocation thread.

The ONLY forum with substantive technical discussion is **c64power.com topic
4120** (the V2.0 dev thread) — and even there the deepest detail is the
player-family breakdown + the `$1006` multispeed note already captured.

## 4. Cross-checks for HVSC attribution / data

- Named HardTrack composers from the Polish forums: **wackee (Arise)**, **Klax**
  (also #197 in research.md's top-user list), plus the top-users Bzyk/Randy/
  Remarque/Shapie. Useful when reconciling HVSC author tags.
- HardTrack was **sold commercially on cassette in Poland by TIM-SOFT** — so
  some HVSC rips may carry TIM-SOFT/commercial intro framing; the player itself
  is unchanged.

## Leads to follow

- **Local SDK `RELEASE NOTES!!!` + `PLAYER V1.0`/`V1.1` sources** (already
  extracted to `_artifacts/sdk/extracted/`, decoded by the sibling agent) — the
  PRIMARY authority for the V1.0-vs-V1.1 player diff and the `$1006` question.
  Forums only confirm "same data format"; the byte diff lives there.
- **`$1006` third vector** — disassemble a V1.0 and a V1.0+/[6 speed] HVSC player
  and confirm whether the multispeed sub-call is a real $1006 JMP in V1.x or a
  V2-only formalisation (decides H1 vs H2 above). Highest-leverage open question.
- **Polish user manual** — "Hardtrack Composer — podręcznik użytkownika.rar"
  (~0.62 MB) on chomikuj.pl (smilingfish8 / "Instrukcje i dokumenty C64 [PL]").
  Gated behind a Polish download wall; no web preview. If obtainable, it is the
  primary feature-level doc (instrument editing, glissando $63/$64, drum
  instruments, multispeed setup from the user side). Worth a manual download.
- **TIM-SOFT cassette inlay** (Allegro archive listings
  archiwum.allegro.pl / archiwumalle.pl) — scans may include a Polish feature
  list / quick-reference; low priority.
- **filety.net literature archive** (`filety.net/index.php?strona=arty/...`) —
  had a TLS cert-name mismatch on 2026-06-13; retry with a tolerant client.
  Polish scene magazines (C&A) sometimes carried editor reviews/tutorials.
- **c64power.com V2.0 thread pages 2-4** — the forum returned only page 1
  reliably (posts by abby_/eXbee_/Zawoo_) plus an isolated post #15. Later pages
  (where Longhair may have posted player internals) were not fetchable on
  2026-06-13; retry the `;wap2` print view or fetch via an archive mirror.
- **`http://members.elysium.pl/brush/hardtrack/`** (dead in 2026) — the original
  source/binary dist (`hardtrack.bin`, `player11.obj`, source). Try a Wayback
  Machine snapshot via a non-WebFetch client (web.archive.org was blocked here).
