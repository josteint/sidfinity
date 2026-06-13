---
source_url: aggregate — see per-claim URLs inline; primary leads: github.com/WilfredC64/player-id, github.com/cadaver/sidid, github.com/c64cryptoboy/ChiptuneSAK, github.com/ice00/jc64, github.com/realdmx/c64_6581_sid_players, github.com/Chordian/deepsid
fetched_via: direct
fetch_date: 2026-06-13
author: SIDfinity research session (survey of the open-source SID-tooling ecosystem)
content_date: 2026-06-13 (repo states as of this date)
reliability: secondary=analysis (ecosystem survey + negative results), with primary signature data quoted from sidid configs
---

# Music Assembler — open-source ecosystem survey ("who already understands this format?")

## Bottom line

**No open-source tool parses the Music Assembler PACKED BINARY format.** The
only format-aware artifact in the entire open-source ecosystem is the **sidid
detection signature** (a ~20-byte fingerprint of one player routine — fully
decoded in `github_disasm_verified_runtime.md`). Every SID→note/MIDI converter
that "supports" MA does so by **emulating the C64 and capturing $D400 register
writes**, i.e. it never decodes MA's data tables — exactly the register-trace
approach SIDfinity rejects (CLAUDE.md: "NO writelog replay"). So for SIDfinity,
the binary format must be reverse-engineered from scratch; the open-source
contribution is (a) the signature → player-base locator, and (b) confirmation
of the entry-point layout and variant family.

## Tool-by-tool findings

### SIDId (cadaver/Lasse Öörni) + player-id (WilfredC64) — USEFUL (signature DB)
- https://github.com/cadaver/sidid , https://github.com/WilfredC64/player-id
- These are the canonical player-detection databases. The HVSC engine column
  (and SIDfinity's `hvsc84.db engine='Music_Assembler'`, n=6351) comes from
  here — SIDId scans the relocated player code for the byte fingerprint, using
  "playroutine info provided by the HVSC crew."
- The full Music_Assembler family signatures + the V2.0 signature-file grammar
  are quoted in `github_sidid_signatures.md`. player-id is the modern,
  multi-core, sidid.cfg-compatible re-implementation (Rust); its
  `config/sidid.cfg` is the most current signature set.
- VALUE: the primary signature `BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60
  B9 ?? ?? 85` is a verbatim slice of the player's sequence-command routine, so
  matching it gives the player base directly (sig_addr → base, see runtime doc).

### ChiptuneSAK (c64cryptoboy) — NOT format-aware (emulation only)
- https://github.com/c64cryptoboy/ChiptuneSAK ,
  https://chiptunesak.readthedocs.io/en/latest/sid.html
- "ChiptuneSAK imports SID files through C64 emulation, not binary parsing or
  player-specific handlers ... our python emulator_6502.py is very close to
  SIDDump's cpu.c ... The tool includes NO player-specific format handlers — it
  relies entirely on emulating the generic 6502 execution model." Imports PSID +
  some RSID, supports VBI + CIA + multispeed dispatch.
- VALUE for MA: none for parsing. Its only relevance is confirming that the
  general-purpose route is register-trace, which SIDfinity explicitly avoids.

### SID2MIDI (Wothke/remix64) + sidtool (olefriis) — NOT format-aware
- "SID2MIDI converts SID files into MIDI by emulating a C64 environment ... and
  analysing the SID output to determine the music data." Same register-trace
  philosophy. No MA data-format decoder.

### JC64dis (ice00/jc64) — POSSIBLY USEFUL (example disassembly), not in-repo source
- https://github.com/ice00/jc64 (Java) — an iterative interactive disassembler
  for MUS/SID/CRT/PRG. The author's release notes / sample outputs explicitly
  include **Music Assembler example disassemblies**: a tune "MC_01" by Marco
  Swagerman (c) 1988 Dutch USA Team, and a "Magazine Intro Tune" by Reyn
  Ouwehand (c) 1989 — i.e. JC64dis has been pointed at MA tunes and produced
  annotated 6502 listings. These sample listings are NOT committed to the GitHub
  source tree (code search for "Music Assembler"/"Swagerman"/"Ouwehand" returns
  nothing); they live in the itch.io build / forum posts (Lemon64 JC64dis
  threads). It's a generic disassembler, not an MA parser — but its MA sample
  output could be a useful cross-check / annotation seed if obtained.
- LEAD: pull the itch.io JC64dis distribution (iceteam.itch.io/jc64dis) and look
  for bundled example `.dis`/`.txt` of the Swagerman/Ouwehand MA tunes.

### realdmx/c64_6581_sid_players — NOT relevant
- https://github.com/realdmx/c64_6581_sid_players — reverse-engineered,
  ACME-buildable players, but organised by COMPOSER (Galway, Hubbard, Tel,
  Whittaker, Dunn, Gray, Bjerregaard, Bulka/FAME, Deenen, Kimmel, Ouwehand,
  Audial Arts). NO Music Assembler / Dutch-USA-Team / Swagerman / Giesen player.
  (Reyn Ouwehand appears as a composer here, but his entries are his own custom
  players, not the MA player — though some HVSC Ouwehand tunes ARE MA-detected.)

### DeepSID (Chordian) — NOT format-aware (metadata/STIL only)
- https://github.com/Chordian/deepsid — online player; gets engine/player names
  from HVSC metadata + sidid-style DBs + STIL, not from binary parsing. No MA
  decoder. (Chordian = SIDFactory II author; SF2 is a modern editor with its own
  format, unrelated to MA's packed output — no MA import path.)

### libsidplayfp / libsidtune — NOT format-aware
- The SID-tune loaders only parse the PSID/RSID HEADER (load/init/play/flags);
  the C64 payload is opaque machine code executed by the emulator. No
  per-player format knowledge. (This is what SIDfinity's own siddump uses.)

## Useful collateral facts harvested

- Alternate search term: **"DUSAT"** = Dutch USA Team — used in scene/tool
  references (e.g. "DUSAT Music Assembler"). Good for further CSDb/forum search.
- Original author credit cross-check: JC64 sample names the MC_01 tune
  "(c) 1988 Dutch USA Team, Marco Swagerman" — corroborates MC = Marco
  Swagerman; OPM = Oscar Giesen (the `MUSICIANS/O/OPM/` HVSC folder holds his
  tunes, all `Music_Assembler`-detected, ideal RE specimens).
- Tape Master Pro loader-music guide independently documents
  "Init $1048 play $1021 (Voice Tracker or Dutch USA Team's Music Assembler)" —
  third-party confirmation of the +$48/+$21 entry layout AND that VoiceTracker
  shares it.

## Where the open-source ecosystem leaves SIDfinity

Acquired (open-source, primary): the detection signature (→ player-base
locator) + entry-point layout + variant family list.
Missing everywhere (must RE from binaries): the packed sequence/track/preset
table encoding. Partially recovered THIS session by direct disassembly — see
`github_disasm_verified_runtime.md` (write model + sentinel bytes + table
strides + the two-layout-but-one-engine finding).

## Cross-references to sibling research docs (same directory)

These GitHub-cluster docs corroborate / complement docs produced by the
CSDb + forum + archive research clusters:
- `sidid_signature_analysis.md` (forum/local sidid copies) — same six
  signatures, cross-checked against HVSC binaries; agrees with
  `github_sidid_signatures.md`.
- `csdb_packed_format_disasm.md` / `spec_player_RE_grounded.md` — packed-format
  disassembly from the EDITOR's own assembled song output (CSDb #94388 disk
  PRGs). My `github_disasm_verified_runtime.md` independently disassembles
  HVSC-distributed binaries (OPM/Sid_Slam, Ozone/Power_Wars) and reaches the
  same player core + write model — a useful two-source confirmation that the
  HVSC tunes and the editor's V1.0 output are the SAME player.
- `forum_jitt64_importer.md` — note any JITT64 / JC64dis importer leads there
  alongside the JC64dis lead below.
