# Master Composer — preservation-scene provenance, authorship & versions

Provenance
- source_url (catalog): https://preservation64.de/index.php?title=Master_Composer
  (raw wikitext: https://preservation64.de/index.php?title=Master_Composer&action=raw)
- source_url (catalog list): https://preservation64.de/index.php?title=List_of_archived_C64_applications
- source_url (CSDb crack): https://csdb.dk/release/?id=128699
- fetched_via: "direct" (preservation64.de page + raw wikitext via curl/WebFetch; CSDb release page via WebFetch)
- fetch_date: 2026-06-13
- author/handle: preservation64.de wiki, original-disk dump contributed by **sncboom2k** (a known C64 disk-preservation contributor), verified "by parser"; CSDb #128699 crack by group **MST**
- content_date: preservation64 record archived **14 Mar 2013**; describes a **1983** retail product; CSDb comment 2014-02-05
- reliability: HIGH — preservation64 is a curated original-media preservation project; the record is a verified dump of an ORIGINAL (uncracked) retail disk, and the canonical filename embeds the authorship/publisher/year exactly.

---

## 1. Authorship & publication (the strongest provenance string)

preservation64's archived **G64 image of the original retail disk** carries this canonical filename:

```
Master_Composer_(Paul Kleimeyer)_(Access Software)_(1983)_(original)_RAW1_k2_s0.g64
```

This is a primary-source attribution from a verified ORIGINAL (not cracked) disk dump and is the
authoritative confirmation of:
- **Author / programmer: Paul Kleimeyer**
- **Publisher: Access Software** (Inc.; Woods Cross, Utah — address per the Music Software Guide,
  see `archive_manual_and_disk.md`)
- **Year: 1983** (the program copyright; the broadly-cited "1983–1984" reflects 1983 authorship +
  1984 retail push/advertising)
- **`(original)`** = a clean uncracked dump exists (most other images are cracks).

The VGMPF wiki independently credits Paul Kleimeyer / Access Software, writing 1983 / released ~1984
(see `forum_vgmpf_wiki.md`). Two independent preservation sources agree on the authorship — treat it
as settled.

## 2. preservation64 catalog record (verbatim, original retail disk)

| Property | Data |
|---|---|
| Title | Master Composer |
| Publisher and/or Developer | Access Software |
| Year | 1983 |
| Disk(s) | 1 |
| Media Type | 5.25 DSDD |
| Retail / Budget / Compilation | **Retail** |
| Country of Release | US |
| Language(s) | English |
| Platform | C64 |
| NTSC or PAL | **NTSC (runs also on PAL)** |
| Protection | **Checks error 5 on track 18 sector 18** |
| Working? | Yes |
| Archived | 14 Mar 2013 — sncboom2k |
| Verified by | parser |

Preserved media on that page: a **streams ZIP** (`Streams_MasterComposer_Access_sncboom2k_ntsc.zip`,
raw flux/stream capture, NTSC) and the **G64** named above. **Disk side 1 is empty** (single-sided
content — consistent with the 174 848-byte = 35-track .d64 of the Playboy crack in
`archive_manual_and_disk.md`). Gallery images on the page: `…_title.png` (title screen),
`…_app.png`, `…_app2.png` (two application/editor screens).

### Why this matters for parsing the binary
- **`NTSC (runs also on PAL)`** is the structural reason the engine ships an **NTSC-tuned frequency
  table** (the project brief's "default tuning 450 Hz NTSC / 433.5 Hz PAL"): the table is computed
  for the NTSC SID clock (~1.0227 MHz) and is simply replayed on PAL hardware (~0.985 MHz), so PAL
  playback is slightly flat — there is no separate PAL table. Expect ONE freq table per file, NTSC
  values, regardless of the rip's PSID PAL/NTSC flag.
- **`Checks error 5 on track 18 sector 18`** = the original disk protection: a deliberate DOS
  error-5 (data-block-not-found / checksum) on the directory track (T18). Irrelevant to the SID
  music data, but it tells you the ORIGINAL load path included a protection probe that **cracks
  remove/patch** — so any disassembly of a cracked rip may show a stubbed/altered loader vs the
  original. The MUSIC player core (init/play) is downstream of and unaffected by this.

## 3. Versions — what is and isn't attested

There is **no evidence of multiple numbered engine versions** in the preservation record (one entry,
no v2.x). The "v1.0" seen in cracks (e.g. the Playboy disk titled `MASTERCOMPOSER V1.0`) is the
program's own version string; no later major version surfaced in this cluster. Attested variants are
about CRACKS and MODES, not engine rewrites:

| Variant | Source | Notes |
|---|---|---|
| Original retail (uncracked) | preservation64 G64 (sncboom2k, 2013) | `(Paul Kleimeyer)(Access Software)(1983)`; T18/S18 error-5 protection |
| Crack — group **Playboy** | archive.org `d64_Master_Composer_v1.0_19xx_Playboy` | titlebar "MASTERCOMPOSER V1.0"; 174 848-byte .d64; intro "BIER FRONT" |
| Crack — group **MST** | CSDb #128699 (`Master_Composer-MST.d64`) | the only crack with a **working "Dealer Demo"** mode per a CSDb comment |

> The "Dealer Demo" (a showroom/auto-play mode on the retail disk) is the only hint of a SECOND
> runtime mode beyond the editor's own playback. It is a packaging/mode difference, not a different
> music ENGINE — but if a Dealer-Demo rip ever appears in HVSC it may have a different init/play
> entry or auto-advance behaviour. Flag, don't assume.

CSDb download (route for the MST crack, recorded for completeness — CSDb blocks scripted fetches,
use a browser/Wayback): `https://csdb.dk/getinternalfile.php/127473/Master_Composer-MST.d64`.

## 4. HVSC placement (cross-reference, for DB/coverage queries)

Per the parallel HVSC-docs research (`forum_hvsc_docs.md`), Master Composer rips in HVSC #84 live
under `/DEMOS/UNKNOWN/Master_Composer/` (the engine is folded into the UNKNOWN demos tree; per-tune
composers mostly unidentified), NOT under a `MUSICIANS/` author folder. The eight tunes BUGlisted
there are flagged "File seems truncated, lacks lots of data at end" — DATA-truncation rips, not
engine bugs. And HVSC #80's **Prg2Sid 1.15 patched the Master Composer end-of-tune code** (the
"decaying hum" fix) — so post-#80 rips may carry a PATCHED player, not the pristine 1983 Access
Software end-of-tune routine. (Full detail in `forum_hvsc_docs.md`; noted here so the provenance of
the ~1,019 HVSC binaries is clear: many are cracked/patched/truncated, the clean reference is the
preservation64 original dump above.)

## 5. Net provenance summary

- **Settled:** author **Paul Kleimeyer**, publisher **Access Software** (Woods Cross, UT),
  **1983** program / 1984 retail, US, NTSC-native, **retail $39.95**, single 5.25" disk with T18/S18
  error-5 protection. A clean ORIGINAL dump survives (preservation64); two scene cracks survive
  (Playboy on archive.org, MST on CSDb).
- **Not found:** a scanned printed manual, a magazine ad PDF, any 4am write-up, any Paul Kleimeyer
  interview, or any second numbered engine version. The closest usage doc is the in-disk `H` help
  screen (see `archive_manual_and_disk.md`).
