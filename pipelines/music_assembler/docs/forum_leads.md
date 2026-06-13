# Music Assembler — forum/wiki/Usenet research: negatives + leads to follow

> **fetched_via:** WebSearch + WebFetch  ·  **fetch_date:** 2026-06-13
> **reliability:** secondary (research log / pointers, not primary format data).
> Scope of this cluster: Codebase64, Lemon64, forum64.de, CSDb forums, comp.sys.cbm.

## Confirmed NEGATIVE results (so future sessions don't re-walk them)

- **Codebase64 has NO Music Assembler / Dutch USA Team / VoiceTracker article.**
  Checked `base:sid_programming`, `base:sid_players` (page does not exist), and
  wiki search. There is no Codebase64 article on "how SID players pack their data"
  that names this engine. (Note: `codebase64.org` now redirects to spam; the live
  wiki is `codebase64.net` / `codebase64.com` — same content, still no MA page.)
- **comp.sys.cbm (Usenet, via narkive):** no substantive thread on the Music
  Assembler *format* found. The Dutch USA Team is referenced only historically
  (the group, the Amiga demos). No format/ripping discussion located.
- **forum64.de:** the German threads are real (#69740 "Sound-Musik-Programm für
  C64 gesucht", #56476 "PlayEm64") and mention MA favourably ("worked quite well,
  excellent music and instruments"), but forum64.de returns **HTTP 403 to WebFetch**
  and the search snippets carry no format/player-routine detail. Needs a browser /
  authenticated fetch to mine — low expected technical yield.
- **CSDb release #94388** (the canonical Music-Assembler V1.0 record) returned
  **HTTP 503 to WebFetch on every attempt** (bot-blocked). Re-try from a real
  browser; the release page + its comments/credits are still worth reading for
  contributor handles and links to the manual.

## The actually-useful artifacts (captured in sibling docs)

1. **SIDId signature DB** (`forum_sidid_signatures.md`) — six byte signatures that
   distinguish the player + variants, plus the Rosenfeldt name-collision. THIS is
   the version-distinction map. Upstream: github.com/cadaver/sidid (`sidid.cfg`).
2. **JITT64** (`forum_jitt64_importer.md`) — GPL Java tracker that ALREADY imports
   MA / VoiceTracker / Music Mixer from PSID. Its SVN source is a ready-made
   `binary → (presets,seqs,tracks,arps)` lifter. **Highest-leverage RE shortcut.**
3. **VoiceTracker == same compression as MA** (`forum_voicetracker_lemon64.md`) —
   one decoder covers VoiceTracker/Music Mixer/Double­Tracker/Ten Tracker too;
   JC64dis player family + example tunes; author primary-source contact.

## Leads to follow (ranked by expected technical payoff)

1. **★ JITT64 source — the MA/VoiceTracker importer.** GPLv2 Java, SourceForge SVN
   (NOT git): `https://svn.code.sf.net/p/jitt64/code/trunk/` (browse:
   `https://sourceforge.net/p/jitt64/code/HEAD/tree/trunk/`, rev ≥499). On a
   networked host: `svn checkout` it, then grep the source for `MusicAssembler` /
   `VoiceTracker` / `MusicMixer` / `ImportSid`. The per-format reader + the
   "import from PSID" path = the parser for the packed presets/sequences/tracks/
   arpeggios. (This sandbox has no `svn`, no `gh`, no Bash network egress — fetch
   elsewhere.)
2. **★ JC64dis / jc64 source.** `https://github.com/ice00/jc64` (GPL-2.0, Java).
   Recognition lives in `src/sw_emulator/software/SidId.java` + the
   `src/sw_emulator/software/sidid/` package (it uses the SIDId signature DB).
   JC64dis 2.8 added a "data relocation table reference (base+destination)" —
   read that code to see how it resolves an MA player's relocatable data pointers
   after relocation. The disassembler can also emit annotated asm for an MA SID.
3. **WilfredC64/player-id** `https://github.com/WilfredC64/player-id` — HVSC's
   actual classifier (BNDM matcher). Bundles the official `sidid.cfg`; its
   signature-format spec is at `doc/Signature_File_Format.txt`. Cross-check its
   Music Assembler / Voice Tracker / Music Mixer signatures against cadaver's
   (the raw config path needs resolving — `blob/main/sidid.cfg` 404'd; try
   `master`, or a `cfg/` subdir). Use to count/segment the HVSC slice per variant.
4. **CSDb #94388** (browser) — `https://csdb.dk/release/?id=94388`. Comments/credits
   + links to the manual PDF (already vendored: `docs/csdb_manual_*`) and possibly
   to crack/rip notes. Also CSDb releases for VoiceTracker (#2665 v4.2 by Image),
   Music Mixer, DoubleTracker, Ten Tracker — confirm which are "based on the MA
   player" and grab their players for signature/format diffing.
5. **Internet Archive disk image** — `archive.org/details/d64_Music_Assembler_1990_Markt_Technik`
   — the actual editor .d64. Running it (VICE) + saving an `s.` song then ripping
   gives a *known-content* packed file to validate any decoder against (ground
   truth you control, unlike HVSC PSIDs).
6. **Lemon64 threads** (rate-limited 503/403 on 2026-06-13, Retry-After 3600s):
   - t=2029 "Looking for a copy of Voicetracker" (the compression-equivalence quote)
   - t=26109 "JITT64: new Java C64 tracker in develop" (Ice Team dev thread — may
     discuss how the MA/VoiceTracker importer was reverse-engineered)
   - t=5712 / t=5725 "making music on c64" (editor comparisons)
   Fetch later when un-throttled; the JITT64 dev thread is the most promising.
7. **Author primary source** — Marco Swagerman posts as **MC-DusaT** on amiga.cafe
   (active Sep 2025); says he likely still has his Devpac source on diskettes.
   If the C64 packed format resists binary RE, he is reachable for the C64 player
   source / format notes. Also: **Reyn Ouwehand** wrote MA tunes (per JC64dis) —
   another reachable scene contact.

## Cross-references / handles worth chasing

- **Lasse Öörni (cadaver / Covert Bitops)** — SIDId author; the signature DB owner.
- **Wilfred Bos (WilfredC64)** + **iAN CooG**, **Professor Chaos**, **Ninja**,
  **Yodelking**, **Ice00** — the player-id / SIDId signature contributors; any of
  their notes on the MA signature derivation would document the player's entry code.
- **Ice Team (ice00)** — JITT64 + JC64dis; the only known party to have written a
  working MA/VoiceTracker *decoder*. Discord channel linked from the JC64dis page.
- Known representative HVSC members per variant (canary picks for verification):
  - Music Assembler: MC_01 (Swagerman, 1988); Reyn Ouwehand "Magazine Intro Tune".
  - Voice Tracker: "3LUX Intro" by The Bill.
  - Music Mixer: "Michael" by Arkadiusz Zych.
  - (plus the five reps already in `research.md` §canary).
