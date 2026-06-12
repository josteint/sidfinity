## Wave: DMC4 editor top-up 2026-06-12

- https://csdb.dk/release/?id=251057 — OK (DMC 4 Editor 1.1 release page)
- https://csdb.dk/search/?seinsel=releases&search=DMC+4+Editor — OK (found 1.0 = id 250645, 1.1 = id 251057)
- https://www.lemon64.com/forum/viewtopic.php?p=1055941 — FAIL (503, Lemon64 in maintenance mode)
- https://csdb.dk/release/?id=250645 — OK (DMC 4 Editor 1.0 release page + comments + external links)
- https://csdb.dk/getinternalfile.php/267129/dmc4editor11_win64.zip — OK (downloaded to tmp/dmc_research/; ReadMe.txt + config.ini + exe strings extracted)
- https://csdb.dk/getinternalfile.php/266649/dmc4editor10_win64.zip — OK (downloaded; 1.0 ReadMe extracted)
- https://csdb.dk/forums/?roomid=14&search=DMC+4+Editor — OK (no matching threads)
- https://csdb.dk/forums/?csdbentrytype=release&csdbentry=250645&entrytopic=1 — FAIL (redirects to CSDb homepage; no entry forum topic exists)
- https://csdb.dk/forums/?csdbentrytype=release&csdbentry=251057&entrytopic=1 — FAIL (same)
- https://csdb.dk/scener/?id=30449 — FAIL (wrong scener; not Logan)
- https://csdb.dk/search/?seinsel=scener&search=Logan — FAIL (no results; CSDb scener search did not surface Logan)
- https://csdb.dk/search/?seinsel=all&search=Logan+Slackers — FAIL (no results)
- https://www.lemon64.com/forum/viewtopic.php?t=80234 — FAIL (503 maintenance; "DMC 4 Instructions?" thread, unfetched)
- https://web.archive.org/web/20260210210501/https://www.lemon64.com/forum/viewtopic.php?p=1055943 — OK but wrong thread ("Bugged game list")
- https://web.archive.org/web/20250823134612/https://www.lemon64.com/forum/viewtopic.php?p=1056030&sid=b8ac7c7516f2a4fabd09787126839569 — OK (full "DMC V4 is back in 2025" thread, t=86611, 5 posts; saved tmp/dmc_research/lemon_thread2.html)
- Web searches (Anthropic WebSearch): "DMC 4 Editor Logan Slackers", "github dmcproxy/dmc4editor", "Demo Music Creator github", "DMC V4 is back lemon64" — no source repo found anywhere
- http://ftp.pokefinder.org/index.php?s=DMC%204%20Editor — NOT FETCHED (mirror link from CSDb 1.0 page; same zips)
- https://www.youtube.com/watch?v=uPdxCpUFnSc — NOT FETCHED (demo video, 1.0 release page)
- https://www.youtube.com/watch?v=a-BgREkkjcg — NOT FETCHED (demo video, Raf's comment)

## Wave: V5 + command bytes 2026-06-12

Target: HOLE 1 (V5 8-byte instrument format) + HOLE 2 ($C0-$DF / $E0-$FF sector command bytes).
Outputs: dmc_v5_format_notes.md, dmc_sector_commands.md, dmc_v5_docs_original.txt, tnd_dmc_tutorial.txt.

- http://www.tnd64.unikat.sk/music_scene.html — FAIL (TLS cert invalid via WebFetch; direct curl returns 500; site moved)
- http://tnd64.unikat.sk/ — OK (redirect stub pointing to tnd64.dreamhosters.com)
- https://tnd64.dreamhosters.com/music_scene.html — OK (full DMC 4/7 + DMC 5 tutorial, 176KB; text saved as tnd_dmc_tutorial.txt)
- https://tnd64.dreamhosters.com/DMC%20Music%20Editors%5BTND%5D.zip — OK (D64 with DMC V2.1/V4.0/V5.0/V5.0+/V7.0 + V4 docs + V5 instrux noters; tmp/dmc_hunt/)
- https://csdb.dk/release/?id=2594 — OK (DMC V5.0 release page; download link + comments, no format info)
- https://csdb.dk/release/?id=2600 — OK (DMC V5.1+ package; credits show docs by The Syndrom)
- https://csdb.dk/getinternalfile.php/64792/DMC_V5.1+Packages.zip — OK (D64 downloaded; docs are inside a packed noter, not text-extractable — run in VICE if needed)
- https://csdb.dk/release/?id=36658 — OK (DMC V5.4 Samar; comments: better hard restart, raster savings, buggy packer; zip NOT fetched: csdb.dk/getinternalfile.php/26375/DMC_v5.4_SAMAR.zip)
- https://csdb.dk/release/?id=251057 — OK (DMC 4 Editor 1.1; ReadMe + exe strings confirm the complete V4 command set: SND/DUR/VOL/GLD/GATE/SWITCH/END)
- https://csdb.dk/getinternalfile.php/267129/dmc4editor11_win64.zip — OK (also in tmp/dmc_hunt/; exe format strings: "%.2X: VOL.%.2X" etc.)
- https://csdb.dk/release/?id=22938 — OK (DMC V5.0+ by CreaMD, Dec 2002: audible editing etc. — editor-side only, no format change documented; download: csdb.dk/getinternalfile.php/10752/dmcv5plus.zip, NOT fetched)
- https://csdb.dk/search/?seinsel=forum&search=DMC+format — OK (NO byte-level format threads exist on CSDb)
- https://hvmec.altervista.org/blog/?p=700 — OK (HVMEC DMC v5.0 page; lists PRG, docs, packer, depacker downloads)
- https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/dmc_5_docs.txt.gz — OK ★ (the ORIGINAL V5.0 docs by The Syndrom, ripped by FourthX 2002; file is plain text despite .gz; saved as dmc_v5_docs_original.txt)
- https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC_V5.prg_.gz — OK (DMC V5.0 editor binary, tmp/dmc_hunt/)
- https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC-V5.0-Packer-19xxMotiv-8.prg_.gz — OK (tmp/dmc_hunt/)
- https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC_V5_Depacker.prg_.gz — OK (tmp/dmc_hunt/)
- https://c64music.blogspot.com/2005/08/dmc-tutorials.html — OK (pointer to TND only)
- http://chordian.net/c64editors.htm — OK (DMC 5.0 row: 32 instruments, 8 subtunes, PAL-only; links arnold.c64.org DMC_V5_DOCS.txt = same doc)
- http://justsolve.archiveteam.org/wiki/DMC — FAIL (ECONNREFUSED)
- https://web.archive.org/web/2023/http://www.tnd64.unikat.sk/music_scene.html — FAIL (web.archive.org blocked for WebFetch)
- ftp://arnold.c64.org/pub/utils/music/dmc/ — FAIL (FTP not reachable from sandbox)
- https://www.lemon64.com/forum/viewtopic.php?t=24476 — FAIL (503 maintenance; "DMC 6" thread, unfetched)
- https://archive.org/details/d64_DMC_v5.0_Toolkit_2002_CreaMD-DMagic — NOT FETCHED (surfaced by search; CreaMD V5.0+ toolkit D64)
- Web searches: "DMC Demo Music Creator format sector commands $C0", ""DMC" C64 $7D $7E $A0 note duration", "DMC player disassembly github/codebase64", "csdb DMC V5.0+ CreaMD" — no byte-level documentation exists anywhere public

Artifacts kept in repo-local tmp (gitignored): tmp/dmc_hunt/ — DMC_V5.prg_,
V5 packer + depacker, TND editors D64 (+ extracted dmc_v40_docs.prg /
dmc_50_instrux.prg noters, both packed binaries), DMC V5.1+ D64,
dmc4editor11_win64.zip.

## Wave: disassembly hunt 2026-06-12

Goal: community disassemblies / source reconstructions of the DMC V4/V5 player.
Headline: **no public annotated disassembly exists**; carved Brian's V4 player
binary from DMC 4 Editor 1.1 instead (dmc4_player_embedded_1000.bin).

| URL | Status | Notes |
|---|---|---|
| http://www.tnd64.unikat.sk/music_scene.html | FAIL (HTTP 500, live site down) | |
| https://web.archive.org/web/2023/...tnd64...music_scene.html (WebFetch) | FAIL (web.archive.org blocked for WebFetch) | |
| http://archive.org/wayback/available?url=tnd64.unikat.sk/music_scene.html | OK | snapshot 20231217021836 found |
| http://web.archive.org/web/20231217021836id_/http://tnd64.unikat.sk/music_scene.html | OK (curl, gzip) | full tutorial text → tnd64_dmc_tutorial.md |
| https://csdb.dk/release/?id=10758 (DMC Relocator) | OK | 3 zips listed; no technical text |
| https://csdb.dk/release/?id=251057 (DMC 4 Editor 1.1) | OK | win64/win32 builds; Brian code credit |
| https://csdb.dk/release/?id=2629 (DMC V7.0) | OK | Ray + The Syndrom comments (V7 = hacked V4; official last = 5.1/6.0) |
| https://csdb.dk/release/?id=2627 (DMC Pro. Music Player V4.01+) | OK | zip downloaded |
| https://csdb.dk/release/?id=46815 (DMC 5.1 Player ONS) | OK | zip downloaded |
| https://csdb.dk/release/?id=236894 (DMC Relocator V2, Graffity) | FAIL (empty page content x1) | retry next wave |
| https://csdb.dk/release/?id=50611 (DMC V4.0b Relocator, Agemixer) | FAIL (empty page content x1) | retry next wave |
| https://csdb.dk/search/?seinsel=releases&search=DMC | OK | tool inventory → csdb_dmc_tools_survey.md |
| https://csdb.dk/search/?seinsel=all&search=DMC+player | OK | player releases; no forum hits |
| https://csdb.dk/getinternalfile.php/54268/dmc4.01+.zip | OK | d64 with "DMC PRO4" |
| https://csdb.dk/getinternalfile.php/37873/DMC_5.1_Player_ONS.zip | OK | PRG SYS2063 |
| https://codebase64.org/doku.php?id=base:playing_music_a000-_ffff | FAIL (empty; codebase64.org serving spam — domain looks compromised) | |
| https://codebase64.pokefinder.org/doku.php?id=base:playing_music_a000-_ffff | OK | only a JCH/DMC usage example ($A000 init/$A003 play under ROM banking); no internals |
| https://codebase64.pokefinder.org/doku.php?do=search&id=DMC | OK | no DMC internals anywhere on the wiki |
| https://hvmec.altervista.org/blog/?p=700 | OK | version inventory; 4 downloads |
| https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/dmc_5_docs.txt.gz | OK | → hvmec_dmc5_manual.md |
| https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC_V5.prg_.gz | OK | tmp/dmc_hunt/ |
| https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC-V5.0-Packer-19xxMotiv-8.prg_.gz | OK | tmp/dmc_hunt/ |
| https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/DMC_V5_Depacker.prg_.gz | OK | tmp/dmc_hunt/ (depacker = packed-format knowledge) |
| https://archive.org/details/d64_DMC_v5.0_Toolkit_2002_CreaMD-DMagic | OK | d64 fetched; no source on disk |
| https://archive.org/advancedsearch.php?q="demo music creator" | OK | only v5.1Y editor d64 item |
| https://www.lemon64.com/forum/viewtopic.php?t=86611 | FAIL (503 maintenance) | retry |
| https://www.lemon64.com/forum/viewtopic.php?t=72637 (Reverse-engineering music) | FAIL (503 maintenance) | retry — found via search, promising |
| https://www.pouet.net/prod.php?which=13452 (DMC 4.0) | OK | FUNET + HVMEC + TND links in comments |
| https://api.github.com/search/repositories?q=demo+music+creator[, +c64], dmc+sid+c64 | OK | no relevant repos |
| https://grep.app/api/search?q=... | FAIL (Vercel challenge) | |
| github clones: Chordian/sidfactory2, Chordian/DeepSID, WilfredC64/player-id, cadaver/sidid, libsidplayfp/libsidplayfp, theyamo/CheeseCutter, realdmx/c64_6581_sid_players | OK | all DMC-negative → github_parser_survey_negative.md |
| https://retroc64.github.io/docs/music/ | OK | generic SID relocation; no DMC |
| http://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/ (FUNET mirror) | OK | DMC v2.1db/qd, v4.0qu/sx, DMC-v4.0.prg, dmc4.0.prg — binaries only |
| dmc4editor11_win64.zip → dmc4editor.exe carve @0x7F300 | OK | → dmc4_player_embedded_1000.bin + dmc4editor_embedded_player_notes.md |

Local artifacts added this wave (tmp/dmc_hunt/): dmc4editor_x/ (exe + ReadMe),
dmc4_player_embedded_1000.bin (also copied to docs/), dmc4.01plus_x/dmc4.01+.d64,
DMC_5.1_Player_ONS_x/, dmc5_toolkit.d64, DMC_V4.0_DOCS.prg + decoded text,
DMC_5.0_INSTRUX.prg, DMC_5.0_SCANNER.prg, DMC_V5.0_PACKER.prg, DMC_V4.0.prg,
DMC_V7.0.prg, DMC_V5.0.prg (all extracted from the TND d64).
