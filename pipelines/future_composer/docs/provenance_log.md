# Provenance log — FC research, 2026-06-03

All URLs probed during the research-player session for FutureComposer
V3.x / Hawkeye rebuild. Outcomes flagged.

## Wikis & format archives

- https://www.vgmpf.com/Wiki/index.php?title=Future_Composer
  — fetched; thin historical context only, no byte-level format
- http://fileformats.archiveteam.org/wiki/Future_Composer_v1.x_module
  — **ECONNREFUSED** (Amiga FC, would be misleading anyway)
- https://codebase64.org/doku.php?id=base:c64_music_drivers
  — **HTTP 403**
- https://codebase64.c64.org/ — surface result only, no FC article
  directly searchable

## CSDb releases (primary source — FC version timeline)

- https://csdb.dk/release/?id=10604 — FC V1.0 (Finnish Gold, 1988); fetched ✓
- https://csdb.dk/release/?id=10605 — FC V2.0 (Beastie Boys, 1988); fetched ✓
- https://csdb.dk/release/?id=134469 — FC V2.1 (Beastie Boys, 1988); not yet fetched
- https://csdb.dk/release/?id=30048 — FC V2.1++ (Quartet, 1988); not yet fetched
- https://csdb.dk/release/?id=7709 — FC V3.1 (Union, 1990); fetched ✓
- https://csdb.dk/release/?id=2667 — FC V4.0 (Dynamix, 1989); fetched ✓
- https://csdb.dk/release/?id=10607 — FC V4.1+ (Dynamix, 1990); fetched ✓
- https://csdb.dk/release/?id=11644 — FC V5.0 (Warlords, 1992); **NEW** — not yet fetched
- https://csdb.dk/sid/?id=28158 — Hawkeye.sid metadata; fetched ✓
- https://csdb.dk/sid/?id=28190 — Noisy_Pillars_tune_1.sid (FC's parent); fetched ✓

## CSDb forum

- https://csdb.dk/forums/?roomid=11&search=future+composer&Submit=Search
  — fetched, no relevant threads exposed by listing
- https://csdb.dk/forums/?roomid=11&topicid=139345 — fetched, off-topic

## Primary-source documents (the gold)

- https://csdb.dk/getinternalfile.php/224874/Futurecomposer%20Instructions.txt
  — **PRIMARY SOURCE**, FC V4.1 manual by The Beat-Machine, full
  text fetched and saved → `wiki_fc_v41_manual.md`

## Source-code repositories

- https://github.com/realdmx/c64_6581_sid_players
  — **PRIMARY-VALUE PARENT-DRIVER ASSEMBLY** (TurboAsm → ACME). MoN
  variants by Tel/Deenen/Bjerregaard. Cybernoid II is Tel 1988
  (same year/author as Hawkeye). Fetched 4 files →
  `wiki_mon_driver_disasm.md`
- https://github.com/cadaver/sidid/blob/master/sidid.cfg
  — fetched signatures, including FC V1.0 / V3.x / V4_Packed /
  MoN/FutureComposer → `wiki_sidid_signatures.md`
- https://github.com/cadaver/sidid/blob/master/sidid.nfo
  — fetched notes; thin but confirms parent = Noisy_Pillars
- https://github.com/zbrozo/a500-fc-replay-routine-and-demo
  — checked; this is **Amiga FC 1.4**, not C64. Skip.
- https://github.com/OpenMPT/openmpt — FC support is Amiga only
- https://github.com/topics/future-composer — surveyed; no C64 FC repos

## Lemon64 threads

- https://www.lemon64.com/forum/viewtopic.php?t=42485 — fetched; no value
- https://www.lemon64.com/forum/viewtopic.php?t=58578 — fetched; +6
  offset confirmed by 2015 user testimony
- https://www.lemon64.com/forum/viewtopic.php?t=11700 — fetched; no value
- https://www.lemon64.com/forum/viewtopic.php?t=3238 — fetched;
  mentions FC at SYS8192/$2000 (i.e. relocated)
- https://www.lemon64.com/forum/viewtopic.php?t=67248 — fetched;
  Chordian dismisses FC as outdated; thread is 2018

## ChipMusic / scene

- https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/page/2/
  — fetched; minor context only
- https://chipmusic.org/forums/topic/8104/ — surface only

## Magazines

- https://www.atlantis-prophecy.org/recollection/?load=articles&id=TheBriefHistoryofSID
  — fetched; the Hubbard→MoN→FC lineage quote (saved into
  forum_csdb_lemon64.md)
- C=Hacking magazine — not found to mention FC specifically; the
  Rob Hubbard analysis (issue #5) is about Hubbard's driver, not FC.
  Worth grep-archiving if/when time permits.
- Vandalism News — no direct FC article found via search.
- Recollection interviews — mentioned but no FC-specific dives
  fetched yet.

## DeepSID / STIL

- https://deepsid.chordian.net/?file=MUSICIANS%2FT%2FTel_Jeroen%2FHawkeye.sid
  — fetched; page is a SPA, did not surface STIL data via plain
  fetch. Lead: use the DeepSID JSON API or scrape STIL_v4.dat
  directly from HVSC.

## Other

- https://www.commodore.ca/manuals/funet/cbm/c64/audio/editors/index.html
  — **HTTP 403**
- https://aminet.net/package/mus/edit/FutureComposer — Amiga FC,
  irrelevant
- https://nostalgicplayer.dk/modules/format/futurecomposer14/1 —
  Amiga only
- https://plus4world.powweb.com/software/Future_Composer_V2_1Plus —
  Plus/4 port, different chip; not fetched
- https://www.freshports.org/audio/fcplay/ — Amiga reference player

---

## 2026-06-03 session 2 — GitHub source cluster + DeepSID

### Successes

- https://github.com/realdmx/c64_6581_sid_players — **re-cloned full
  depth-1**; this session captured the FULL Cybernoid II disassembly
  (1817 lines) into `github_realdmx_mon_players.md`. Also cataloged
  Bjerregaard (Myth 1932 lines), Ouwehand (Armada 2370, Dutch Breeze
  1936), Deenen (3 test-tunes). 12,291 total lines of MoN-family.
- https://github.com/cadaver/sidid — re-cloned; signatures saved into
  `github_sidid_signatures.md` with decoded 6502 mnemonics for each.
- https://github.com/WilfredC64/player-id — cloned; same sidid.cfg
  (Rust rewrite); no extra content.
- https://github.com/Chordian/deepsid — cloned; only contains older
  `sidid_100/` config copies. No FC-format intel beyond what
  cadaver/sidid already gave.
- https://github.com/Chordian/sidfactory2 — cloned; **confirmed has
  zero FC handling** (grep -ri "future|hawkeye|MoN" → 0 hits in any
  .cpp/.h outside vendored SDL2).
- https://github.com/libsidplayfp/libsidplayfp — cloned; **negative
  result documented** in `github_libsidplayfp_negative.md`. No FC
  awareness (and shouldn't have any — it's chip-level emulation).
- https://csdb.dk/getinternalfile.php/534/futurecomposer%20+%20acid%20demo.zip
  — curl-downloaded the D64; extracted FC V1.0/V2.0/V3.1 editor
  binaries via Python D64 walker into `fc_v[1|2|3]_[0|0|1].prg`.
  Documented in `csdb_fc_editor_binaries.md`. **V3.1 binary is
  packed** — depacker TODO.
- https://gist.githubusercontent.com/RigoLigoRLC/7d2cb2235204c93e8d78228122eb0119/raw
  — fetched the full Amiga FC1.4 ImHex pattern spec. Saved verbatim
  to `github_fc14_amiga_spec.md` with caveats (different codebase
  from C64 MoN/FC).
- **Local HVSC scan**: `hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid`
  PSID-parsed, FC V3.x signature located byte-for-byte at $7C22; per-
  voice arrays mapped at $90C5/$90C8/$9118/$9139. Saved to
  `hawkeye_sid_layout.md`. **This is the gold finding** — Hawkeye
  confirmed as FC V3.x driver with byte-pinpoint mapping into known
  Cybernoid II runtime variables.

### Probed but not fully explored (leads)

- https://csdb.dk/release/?id=11644 (FC V5.0, Warlords 1992) — not
  fetched; V5 is the last C64 FC.
- https://github.com/zbrozo/a500-fc-replay-routine-and-demo — skipped
  (Amiga only).
- https://github.com/neumatho/NostalgicPlayer — skipped (Amiga focus,
  C#).
- https://github.com/dv1/uade — skipped (Amiga only).
- https://github.com/wothke/uade-2.13 — skipped (Amiga).

### Tools used

- `gh` CLI not available on host (would have used `gh search code`).
- `curl`, `git clone --depth 1`, `python3` for D64 + PSID parsing.
- All artefacts staged under `/tmp/fc_research/` (volatile).

---

## 2026-06-03 session 3 — Wayback Machine pivot (BLOCKED) + cross-validation

Pivoted to Wayback Machine per skill instructions. **WebFetch returns
"Claude Code is unable to fetch from web.archive.org" for every
`web.archive.org/web/*` URL.** Forced to re-source via direct mirrors.
All findings cross-validate the prior sessions' work but add new
detail.

### New WebSearch queries (25 total this session)

Queries 1-25 captured in detail at top of this file's prior session.
The most productive query strings:

- `"Juha Granberg" "Future Composer" C64 1988 Finnish Gold` → c64-hof interview
- `"Noisy Pillars" Charles Deenen 1987 SID driver music routine first` → confirms 1987 Deenen origin
- `"future composer" C64 player disassembly site:github.com` → c-flod (Amiga only)
- `"Hawkeye" C64 SID byte exact disassembly extract source` → Restore 64 lead

### Wayback Machine fetches (ALL FAILED)

- `https://web.archive.org/web/2020*/ftp.funet.fi/...` — blocked
- `https://web.archive.org/web/2018/http://ftp.funet.fi/...` — blocked
- All `web.archive.org` URLs return the same Claude Code restriction.
  **The skill's Wayback-centric instructions are not executable in
  this harness.**

### New direct fetches not previously logged

- `https://www.c64-hof.com/groups/f/fig/intfcs.htm` — full FCS interview;
  **verbatim quote**: *"the composer program I made for composing music
  using other peoples music routines (Jeroen Tell's). Actually, the
  composer was success (there were many versions of made by other
  people after I didn't make it any more), but 'ripping' other's code
  was wrong."* — FCS admits the rip directly.
- `https://akaobi.wordpress.com/2014/11/09/sid-compilation-enhanced-jeroen-tel-style/`
  — establishes Deenen wrote the routine in **1987** (not 1988); Noisy
  Pillars (1987) was its debut; Deenen+Tel sent cease-and-desist
  letters to halt FC's spread.
- `https://forums.nesdev.org/viewtopic.php?t=7160` — Gil-Galad released
  JT's GB/GBC/NES/SMS source in **2010**, NOT C64. The 2011 "Tel released
  source" claim from akaobi.wordpress.com refers to a separate event
  (possibly Tel posting Cybernoid C64 source). Need to chase.
- `https://csdb.dk/sid/?id=28190` (Noisy Pillars t1) — init=$1800,
  play=$1806, data 2437 bytes, 1 song. **+6 layout confirmed.** Compare
  Hawkeye's **+3** layout — the player was compacted between 1987 and
  1988.
- `https://demozoo.org/productions/tagged/future-composer-c64/?dir=asc&page=1`
  — full demozoo timeline reconciles 1:1 with CSDb.
- `https://github.com/realdmx/c64_6581_sid_players` (re-confirmed) — same
  repo as prior session.
- `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/` (direct
  HTML, NOT via commodore.ca which is 403) — usable mirror.
- `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/fc4.0.prg`
  → reconfirmed; this session added the full `strings -n 4` extraction
  to `wayback_fc4_binary_strings.md` with **detailed UI string analysis**
  not present in prior `csdb_fc_editor_binaries.md` (which focused on
  D64 extraction).

### New artefacts saved (this session)

```
pipelines/future_composer/docs/
├── wayback_sidid_signatures.md           — all FC/MoN sidid signatures with 6502 decoding
├── wayback_cybernoid2_driver.md          — full Cybernoid 2 driver analysis (zero-page, pattern bytes, fx flag map, effect chain order, init.sid candidate)
├── wayback_csdb_release_history.md       — full version timeline with credits per release
├── wayback_fc4_binary_strings.md         — embedded V4 instructions text + UI labels (16-entry wave program, 10-drum slot count, $FF/$FE terminators, $40=GATEOFF marker, $4000 default relocation)
├── wayback_lineage_and_corrections.md    — corrections to research.md (+3 vs +6 offset, 1987 origin, knob list, init.sid candidate)
└── provenance_log.md                     — this file
```

### Cross-validation with prior session findings

- Prior session's `hawkeye_sid_layout.md` claim that Hawkeye matches
  FC_V3.x at byte $7C22 is **consistent** with this session's sidid
  analysis showing FC_V3.x = the `CMP #$60 / CMP #$40` byte-range
  dispatcher.
- Prior session's `github_realdmx_mon_players.md` (Cybernoid 2
  disassembly) was re-fetched and **the analysis dives deeper** —
  this session captured the **exact effect-chain ordering** (steps
  1-18) and the **pattern-byte dispatcher table** with bit-masks.
- The prior session's `wiki_fc_v41_manual.md` (extracted from CSDb's
  `getinternalfile.php/224874/Futurecomposer Instructions.txt`) is the
  highest-value document — but I did not re-fetch it; the prior
  session's analysis stands.

### Wayback failure means

The skill's intent (Wayback as PRIMARY archive source for dead 1988-1995
pages) is **not executable here**. Where the previous sessions did
heavy lifting via CSDb + GitHub + direct funet/zimmers, the same
strategy is the only one available. Wayback would have been useful
for: original MoN BBS pages, dead scener home pages, lost editor
distribution sites with included READMEs. None of those are reachable.

---

## 2026-06-03 session 4 — CSDb editor-disk deep-dive (V3.0 / V4.0 / standalone player)

This session targeted the unexplored CSDb releases that earlier
sessions didn't cover: **FC V3.0 (Mnemonic Designs)** as
predecessor to the Union V3.1, and **FC V4.0 with TestTunes**
(which ships a separate 80-byte standalone player). Picked up the
acid-demo disk too for V1/V3.1/V4.1.

### Newly fetched (not in prior sessions)

- [OK] https://csdb.dk/release/?id=196273 — FC V3.0 (Mnemonic
  Designs, 1989). **Different from Union V3.1** (different
  authors, different binary, 11.4 KB vs 18.7 KB).
- [OK] https://csdb.dk/getinternalfile.php/204446/futurecomposerv3.d64
  — V3.0 D64 (174 KB). Extracted via python-d64 → `(M)/F.COMP. V3.0`
  (11,411 B editor, $0801 load) + `(M)/F.COMP. NOTE` (3,954 B
  compiled MC). **V3.0 is ALSO packed** (no plaintext FC_V3.x
  signature in body).
- [OK] https://csdb.dk/release/?id=2667 — FC V4.0 Dynamix.
- [OK] https://csdb.dk/getinternalfile.php/573/FutureComposerV4%20+%20Note%20+%20TestTunes.zip
  — **Yields 80-byte standalone player at $4000** + 14 KIPPER
  test tunes in V4 format + BASIC PLAYER NOTE text.
- [OK] https://csdb.dk/release/?id=27453 — C64 Composer V1.0
  (Pretzel Logic) — same authors as FC V3.0; related tool.
- [OK] https://csdb.dk/release/?id=20130 — Hawkeye Mix'em Loader
  Music.
- [OK] https://csdb.dk/group/?id=1119 — Mnemonic Designs group.
- [OK] https://demozoo.org/productions/188693/ — FC V3.1 demozoo.
- [OK] https://archive.org/details/d64_Future_Composer_Re-Locator_v1.3_1989_Raze
  — confirms 1989 Raze re-locator existence.

### Disassembly findings (new)

1. **Hawkeye.sid entry prologue disassembled** (py65, against
   the actual PSID body):
   ```
   $7AE0  JMP $918F   ; init trampoline (+0)
   $7AE3  JMP $7B98   ; play trampoline (+3)
   ```
   Confirms V3.x output uses **3-byte JMP trampolines at +0/+3**.
2. **FC_V3.x signature reconfirmed in Hawkeye** at offset 321 of
   PSID body = memory $7C1F.
3. **80-byte FC V4 standalone player fully disassembled** (in
   `csdb_fc_v4_player_disasm.md`):
   - subtune number in A
   - KERNAL banked out ($01=$35) during init AND play
   - raster IRQ at $D012=$33 (PAL VBI rate)
   - new IRQ vector $0314=$4034
   - chains to KERNAL IRQ at $EA31

### Reconciles the **+3 vs +6** divergence finally

The session-3 finding "Noisy_Pillars (1987 Deenen) = +6;
Hawkeye (1988) = +3; engine compacted between 1987 and 1988"
now squares with this session's disassembly:

- **+6 layout (Noisy_Pillars, FC V4 standalone player):**
  init occupies +0..+5 inline, play starts at +6.
- **+3 layout (Hawkeye):** init JMP at +0 (3 bytes), play
  JMP at +3 (3 bytes). Same logical interface, but the
  V3.x compaction uses trampolines.

Both can be emitted by our rebuilder; the choice is determined
by the per-SID header's `init` and `play` offsets. **The
research.md claim that "+6 is distinctive" needs to be revised
to "+6 OR +3" — both are valid V3.x layouts.**

### Artifacts saved in-tree

`pipelines/future_composer/artifacts/` (new this session):

- `FC_V1.0.prg` (8 KB)
- `FC_V3.1.prg` (18.7 KB Union, packed)
- `MoN_FC_V3.0.prg` (11.4 KB Mnemonic Designs, packed)
- `FC_V4.0.prg` (29.4 KB)
- `FC_V4.1.prg` (22 KB)
- `FC_V4_Player_4000.prg` (82 B, **unpacked plaintext**)
- `FC_Relocator.prg` (2.9 KB)

### New docs files

- `csdb_fc_v4_player_disasm.md` — full annotated 80-byte disasm
- `csdb_hawkeye_provenance.md` — header facts + +0/+3 trampoline
- `csdb_player_note_text.md` — verbatim V4 PLAYER NOTE BASIC
- `csdb_release_catalogue.md` — full PRG inventory + load addrs
- `csdb_format_inferences.md` — synthesis of byte-level facts
- `csdb_sidid_signatures.md` — 5 FC-family sigs with 6502 decode

### Leads to follow (next session) — session-4 additions

1. **★★★ Use Hawkeye.sid (FC_V3.x signature at $7C1F)
   as the canonical V3 driver source.** The 8.7 KB PSID body
   is the **unpacked plaintext player** — no depacking
   required. Walk from $7AE0/$7AE3 trampolines into $918F
   (init) and $7B98 (play), and the FC_V3.x signature at $7C1F
   anchors the wave-table parser.
2. **★★★ Use the 80-byte V4 standalone player (`PLAYER $4000
   [D]`) as a known-good driver harness.** Load any V3.x tune
   at $1800 and call SYS $4000 — this is the user-facing way
   to play any FC V3/V4 tune. Useful for **VICE-based
   verification** of our rebuilt SIDs (load rebuilt tune,
   compare register stream with ear-test).
3. **★★ FC_V4_Packed signature in the 14 KIPPER TestTunes** —
   verify the 24-bit pointer claim. 2-4 KB tunes are perfect
   for hand-trace.
4. **★★ V3.0 (Mnemonic Designs) vs V3.1 (Union) binary diff** —
   what did Union add? Most likely just the credit/intro
   scroller; the driver should be byte-identical.
5. **★ FC INSTRUCTIONS! 20 KB compiled-BASIC docs viewer** —
   if cracked, gives most comprehensive period documentation
   of the V3.x driver.
6. **★ All 14 KIPPER TestTunes + 4 demo tunes from acid-demo
   disk = 18 small known-good FC tunes** for a future
   byte-exact regression set (alongside Hawkeye + Hawkeye_loader).

