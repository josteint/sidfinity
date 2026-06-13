# Provenance log — HardTrack Composer research sweep (2026-06-13)

Two-attempt sweep (the first was killed by a session limit after downloading the
SDK; the re-run continued from the extracted files). Per-file provenance headers
carry exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| elysium.filety.pl SDK (`hardtrack_sdk.zip` → `.d64`) | curl + D64 walk | player V1.0/V1.1 binaries + `EDYTOR/PACKER/DEPACKER.SRC` + `RELEASE_NOTES` |
| `RELEASE_NOTES.bin` (= compiled V1.0 player PRG) + `HT_7_1.sid` | local disasm (`seed_disassembly.py`) + `siddump --writelog` | byte-exact player + verified per-frame write model |
| `PLAYER_V1.0.bin` (tokenised) | local decode | 323-entry original Polish symbol table |
| Polish readme (`OUT_PRZECZYTAJ_MNIE.prg`, crunched) | one-off 6502 emulator (`_artifacts/decrunch_readme.py`) | first-party authorship + credits, translated |
| elysium.filety.pl mirror listing | local read (`tmp/hardtrack/elysium_filelist.txt`) | full HardTrack file inventory on the site |
| CSDb #74928 / #36647 (+ forum #65313 Asterion format note) | direct / snippets | versions, credits, a format spec |
| c64power.com topic 4120 (V2.0 dev thread, abby_=Dąbrowski) | direct (page 1) | V2.0 lineage + `$1006` multispeed vector |
| local `sidid.cfg` ×3 + `PLAYER_*.bin` | local read (read-only) | single signature decode + V1.0/V1.1 shadow split |
| `hvsc84.db` | read-only (`mode=ro`) | 1170 tunes; init/play + PSID-speed-bit census (only 5/1170 set) |
| GitHub (player-id, sidid, jc64, ChiptuneSAK, sid2midi, desidulate, libsidplayfp) | direct | NEGATIVE: no format-aware HardTrack parser anywhere |

## Attempted but blocked

| Source | Status |
|---|---|
| web.archive.org (some agents' env) | unreachable |
| c64power topic 4120 pages 2-4 | only page 1 reliably fetched |
| chomikuj.pl Polish user manual | gated |
| comp.sys.cbm, Codebase64, Lemon64, forum64.de, DeepSID | no HardTrack-specific technical content (negative) |

## Unfetched leads (see README "Top leads")

`groups/Elysium/misc/hardtrack_cracks.zip`; `C64_music_pl_v01.txt.zip`; the boxed
Tim-Soft printed manual (c64scene.pl t=584); `HARDTRACK V1.0+6` disasm; V1.1 build
stamp; the multi-copy `Scortia.sid` compilation variant.

## Note

This sweep's first attempt died on a session limit mid-download; the re-run picked
up from the on-disk SDK. All agents (both attempts) honored the hardened no-git /
write-scoped / read-only-DB constraints — no tracked file outside the docs dir was
touched. See `.claude/memory/feedback_subagents_no_git.md`.
