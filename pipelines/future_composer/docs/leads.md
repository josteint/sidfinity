# Leads to follow

Documents/sources identified but not (fully) fetched this session.
Priority ordered.

## Highest value

1. **Cybernoid II ASM (realdmx repo)** — full primary-source
   reference for Tel's 1988 MoN driver. Need full file fetch + grep
   for: actual voice-register stride; exact freq-table values;
   instrument byte semantics; effect-table sizes/layouts.
   - URL: `https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
   - Action: download whole file in next session, save as
     `docs/Tel_Jeroen_Cybernoid2.asm` for offline reference

2. **Deenen Test Tune 2 ASM (the one with symbolic constants)** —
   `Deenen_Charles_Test_Tune2.asm`. Already extracted the
   `end/arpend/drend/wfend/endsong/rep/dur/snd/vol/pause/stop/
   filter/glide/drum/arp/larp` constants but full source contains
   per-instrument data + the exact effect-table layout.
   - URL: `https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Deenen_Charles_MON/Deenen_Charles_Test_Tune2.asm`

3. **Bjerregaard MoN variants** — `James_Bond_3.asm` documents a
   *different* instrument byte layout from Deenen's. Need to know
   how many MoN/FC variants exist with mutually incompatible
   instrument formats — affects extract design.
   - URLs:
     - `https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Bjerregaard_Johannes_MON/Bjerregaard_J_James_Bond_3.asm`
     - `https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Bjerregaard_Johannes_MON/Bjerregaard_J_Myth.asm`

4. **FC V3.1 binary contents** — CSDb release 7709 has the actual
   editor PRG. Need to extract its embedded V3.1 driver and
   disassemble. The sidid signature shows V3.1 uses pattern-byte
   bands distinct from V1 (`CMP #$60 / AND #$0F` and
   `CMP #$40 / AND #$3F`), but the full opcode table isn't
   documented anywhere yet.
   - Direct download: `https://csdb.dk/release/?id=7709` → "futurecomposer + acid demo.zip"

## Medium value

5. **FC V5.0 (1992, Warlords)** — newest version. Per No-XS's
   comment, "minimal changes from V4.1", but might bundle updated
   docs. CSDb release 11644.

6. **DeepSID STIL annotations for Hawkeye.sid** — the SPA didn't
   surface STIL on a plain fetch. Better path: scrape
   `HVSC/DOCUMENTS/STIL.txt` directly (we have HVSC #84 locally at
   `hvsc84/`). Grep `STIL.txt` for `Tel_Jeroen/Hawkeye.sid`.

7. **Beastie Boys FC V2 variants** — releases 10605 (V2.0) and
   134469 (V2.1) and 30048 (V2.1++ Quartet). Comments and bundled
   docs not yet inspected. May contain version-specific format
   notes.

## Lower value

8. **Vandalism News magazine archive** — searches turned up no
   FC-specific articles, but a scene-mag with 80+ issues might have
   a Granberg or Deenen interview discussing FC internals. Best
   accessed via csdb.dk or scene.org archives.

9. **C=Hacking magazine** — issues 1-6, mid-90s. Issue #5 covers
   Hubbard's driver in depth; whether any issue covers MoN/FC
   directly is unknown. Index via `https://www.ffd2.com/fridge/chacking/`

10. **Recollection magazine interviews** — interview with Jonathan
    "Choroid" Dunn surfaced in search results; he was active in the
    MON era and might mention driver internals. URL:
    `https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=92`

11. **Hugi #38 Tel interview** —
    `https://hugi.scene.org/online/hugi38/hugi 38 - demoscene interviews magic jeroen tel.htm`
    — possible source for Tel's account of his own driver vs. FC.

## People to search for in future sessions

- **Juha Granberg (FCS, "Finland Cracking Service")** — FC editor
  author. May have published source/docs on Finnish BBSes
  preserved on disk archives.
- **Axiom** — coded FC V2 + V4. Major coder. Search "Axiom C64
  Beastie Boys" on csdb.
- **The Syndicate** — coded FC V4.1. Sometimes "Coococ Magazine
  Staff".
- **Charles Deenen** — gave interviews (he later worked in
  commercial games); might be reachable for direct Q&A but mostly
  not interested in C64 era now.
- **Richard of TND** (active in 2004 Lemon64 thread, still active
  on TND-Sweetlight site).
- **Dan Gillgrass** — same thread, still active SID musician.

## Newly identified leads (session 3, 2026-06-03)

- **Restore 64** (`https://restore64.dev/`) — browser-based C64 PRG
  disassembler. Per its own marketing: "auto-depacks 370+ packers,
  detects SID music routines with **787 player signatures**, and
  generates **byte-exact reassemblable KickAssembler output**." If it
  can disassemble Hawkeye.sid and produce reassemblable source, that
  is a massive shortcut over manual disassembly. **Action**: feed
  Hawkeye.sid to it in next session, compare output to our manual
  trace at $7AE0+.

- **`Tel.sid sources released 2011`** — The akaobi.wordpress.com claim
  is that Tel released source code in 2011 (Cybernoid was RE'd in
  2014). The 2010 Gil-Galad release at gilgalad.arc-nova.org is for
  GB/GBC/NES/SMS, NOT C64. There is a **separate 2011 C64 release**
  to find. Possible URLs:
  - `https://csdb.dk/scener/?id=143` (Jeroen Tel scener page) — check
    for "Source" or "Code Release" entries
  - Tel's own site (if any current) — search "jeroentel.com" / "wave.nl"
  - **Action**: csdb scener-page sweep for Tel-released sources

- **`linusakesson.net/music/chipmusic.php`** — Linus Akesson is plausibly
  the author/contributor of `realdmx/c64_6581_sid_players` (the
  Cybernoid 2 reassembly). His personal page may have **un-published**
  disassemblies, including possibly Hawkeye. **Action**: fetch + grep.

- **2014 Cybernoid RE project** — akaobi.wordpress.com mentions a
  community RE of Cybernoid in 2014 that Tel engaged positively with.
  This would be the `c64_6581_sid_players/Tel_Jeroen_MON/Cybernoid2.asm`
  we already have, but the **commit log + community discussion** may
  contain format notes. **Action**: search "Cybernoid 2014 reverse
  engineering c64" + check the repo's GitHub Issues.

- **The Beat-Machine V4.1 manual section we still haven't fully mined**
  — prior session's `wiki_fc_v41_manual.md` only summarised. Reading
  the full text again with **byte-range / opcode-table eyes** could
  produce a complete state-table specification of FC V4.1's
  pattern-byte semantics.

- **FC V5.0 (Warlords TMB 1992)** — CSDb id=11644. Last C64 FC.
  Confirmed in our V3-session CSDb fetch as "minor cosmetic only", but
  may bundle a final-revision driver + last docs.

- **`csdb.dk/forums/?roomid=11`** — CSDb's general C64 forum. Searched
  but only a few hits. A **targeted search for "Cybernoid driver" or
  "MON 1987 player" or "Deenen driver"** by hot threads could surface
  developer comments.

- **Recollection issue 8 (Tel interview)** — Recollection magazine often
  digs deep on technical history. Per search hits it has interviews
  with multiple scene musicians including possibly Tel/Deenen
  discussing the 1987-1988 MoN driver. **Action**: scrape the
  Recollection back-issues index.

## Methodological leads

- **sidid against the local HVSC** — run `tools/build_sid_db.py`
  with sidid enabled and check the engine classification breakdown
  for Hawkeye.sid and other FC candidates. This is local work, not
  research, but informs migration target selection.
- **Compare Hawkeye.sid binary against Noisy_Pillars_tune_1.sid** —
  both Tel, both 1988, sizes 8768 vs 2437. Hawkeye is 3.5× bigger,
  meaning multiple subtunes + larger data — but the player code
  region should be near-identical.
- **Disassemble Hawkeye.sid with tools/seed_disassembly.py** —
  produce a seed disassembly, find $7AE3 entry, trace forward to
  understand its specific dispatcher. This is the standard
  `migrate-hubbard-engine` first step adapted to FC.
