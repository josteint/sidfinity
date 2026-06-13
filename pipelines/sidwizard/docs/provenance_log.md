# Provenance log — SID-Wizard research sweep (2026-06-13)

Roll-up across the six-cluster sweep. Per-file provenance headers carry exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| github.com/anarkiwi/sid-wizard (SVN mirror) | curl raw (NOT git clone) | `player.asm`, `exporter.asm`, `SWM-spec.src`, `swm.h`, `SWMconvert.c`, driver includes |
| in-repo `manuals/ChangeLog.txt` (Hermit's own, 31 KB) | curl raw | per-version C64 player/format/exporter deltas V1.0-V1.8 |
| SourceForge sid-wizard SVN tags/dates | direct | exact rev+date per version (1.0-rc r3 … 1.8 r394) |
| SID-Wizard 1.0 manual PDF (`csdb.dk/getinternalfile.php/108351/`) + 1.4 (c64.cz/retrotime.hu) + 1.5 fragment | curl + pdftotext | prose format spec: instrument params, FX catalogue, multispeed thresholds, ABI |
| plaintext 1.8 manual (M64GitHub fork raw) | curl | 1.8 deltas, multi-SID limits |
| 4 HVSC binaries (Magyar_Nepzenek, ChipMotif, Bassloop, Phonky_2SID, Tree_Angel_3SID) | local disasm + `siddump --writelog` | verified write model + decoded layout |
| local `sidid.cfg` ×3 | local read (read-only) | full Hermit signature block (V1.0-1.5, 2SID/3SID, FlexSID, 1RasterTracker) |
| `hvsc84.db` | read-only (`mode=ro`) | census: 1048 (1010 v2 / 29 v3 / 9 v4); init/play + speed-bit distribution |
| CSDb V1.92 release + comments | WebFetch AI-path (curl/raw 503'd) | 4SID/WebSID routing thread |
| DeepSID source (`php/sid_id.php`, controls.js) | direct | labelling = SIDId primary key + `_2SID`/`_3SID` filename suffix |

## Attempted but blocked

| Source | Status |
|---|---|
| csdb.dk release HTML pages | Cloudflare JS challenge / 503 to curl+WebFetch (V1.92 worked via AI-path) |
| hermit.sidrip.com | HTTP 522 (origin down) — reconstructed from manual + SourceForge |
| chipmusic.org (Hermit's hands-on threads) | 403 to fetcher UA |
| lemon64.com threads | 503, Retry-After 3600 |
| comp.sys.cbm | sparse (2012+ tool, post-Usenet) |
| large `player.asm` lean-emitter body | truncated by GitHub-raw + WebFetch summarizer (use SVN viewvc) |

## Unfetched leads (see README "Top leads")

SourceForge viewvc full `player.asm` + pre-V1.4 layout; full 1.5/1.7/1.8 manuals;
the `$B0..$FD` vs `$F0..$FD` orderlist dispatch question; cRSID reference replayer;
"Creating Chip Tunes with SID-Wizard" e-book; chipmusic.org topics 7702/14204/18490;
WebSID 4SID header spec.

## Note

All six agents honored the hardened no-git / write-scoped / read-only-DB
constraints — source was fetched via curl to gitignored `tmp/sw/` (no `git clone`),
and the pre-existing `M hvsc84.db` / `M pipelines/dmc/v4/factory.py` (the concurrent
DMC session) were left untouched.
