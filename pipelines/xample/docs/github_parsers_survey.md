# X-Ample / Compotech — GitHub Parser & Tool Survey

**Provenance:** Web searches + GitHub page fetches conducted 2026-06-13.
Scope: GitHub code search for X-Ample / Compotech / XTracker parsers,
converters, annotated disassemblies, and engine-neutral tools.
No siddump, py65, or disasm was run.

---

## 1. Summary verdict

**No parser, converter, decoder, or annotated disassembly of the X-Ample /
Compotech / XTracker music engine exists on GitHub or in any publicly indexed
source.** The source code of Compotech, XTracker, or the underlying player
routine has never been published. All public tool support is limited to
*identification* (sidid byte-pattern matching) and *generic SID playback*
(libsidplayfp). Zero structured data extraction tools exist.

---

## 2. Search queries run and results

### 2.1 Direct name searches

| Query | Result |
|---|---|
| `"X-Ample" C64 SID player parser site:github.com` | No relevant hits. sidid.nfo is the top result. |
| `"Compotech" C64 parser site:github.com` | No hits for a parser or decoder. |
| `"XTracker" C64 SID site:github.com` | No C64-specific XTracker repo. (Results polluted by financial ETF "Xtrackers" brand.) |
| `"Markus Schneider" C64 SID site:github.com` | No code repos. Only sidid.nfo attribution. |
| `"LordsOfSonics" OR "lords_of_sonics" C64 site:github.com` | No hits. |

### 2.2 Engine-neutral tools checked for X-Ample support

| Tool | Repo | X-Ample support? | Notes |
|---|---|---|---|
| **ChiptuneSAK** | `c64cryptoboy/ChiptuneSAK` | NO | Imports PSID/RSID via generic libsidplayfp; no player-specific decode. |
| **desidulate** | `anarkiwi/desidulate` | NO | Inputs are VICE SID register dump files only; player-agnostic. |
| **sidtool** | `olefriis/sidtool` | NO | Generic SID → MIDI; no player-specific decode. |
| **JC64dis** | `ice00/jc64` `doc/example/` | NO | Checked all `.dis` files in `doc/example/`; no X-Ample, Compotech, or XTracker entry. (Full list confirmed — 80+ .dis files covering Futurecomposer, Hubbard, Keith Bowden Companion, Clever Music, etc.) |
| **libsidplayfp / libsidtune** | `libsidplayfp/libsidplayfp` | GENERIC ONLY | Plays any PSID/RSID via emulation; no X-Ample-specific decode or note extraction. |
| **psid64** | `hermansr/psid64` | NO | PSID → C64-native; does not decode player format. |
| **player-id** (WilfredC64) | `WilfredC64/player-id` | IDENTIFY ONLY | X-Ample signatures present in `config/sidid.cfg` (identical to cadaver/sidid). No data extraction. |
| **c64_6581_sid_players** | `realdmx/c64_6581_sid_players` | NO | Covers Hubbard, Galway, Whittaker etc. (organised by composer name). X-Ample absent. |

### 2.3 JC64dis example directory — full negative confirmation

The `ice00/jc64` `doc/example/` directory contains 80+ annotated `.dis` files.
File list extracted 2026-06-13. Engines present include: FutureComposer,
Rob_Hubbard_CM, KeithBowden_Companion, Clever_Music_player, Kawasaki_Synthetizer,
TenTracker, DoubleTracker, SyntExecutor, Rockmonitor2/5, etc.

**Not present:** X-Ample, Compotech, XTracker, Parsec, LordsOfSonics, Markus_Schneider.

This is a hard negative: JC64dis is the most thorough public C64 disassembly
annotation collection, and X-Ample is absent.

---

## 3. Player-id / sidid identification

Both `cadaver/sidid` and `WilfredC64/player-id` carry identical X-Ample family
signatures in their `sidid.cfg` / `sidid.nfo`. The signatures and their
interpretation are documented in full in `sidid_variant_taxonomy.md` (sibling
file). The `.nfo` attribution for each variant:

| sidid sub-variant | sidid.nfo attribution |
|---|---|
| `X-Ample` (base) | Markus Schneider / LordsOfSonics |
| `(Compotech_V2.x)` | Markus Schneider & Helge Kozielek — 1990 X-Ample Architectures — CSDb #122614 |
| `(Sonic/SDS)` | (no separate .nfo entry; sub-entry under LordsOfSonics/MS) |
| `(Thomas_Detert)` | (no separate .nfo entry; sub-entry under LordsOfSonics/MS) |
| `(XTracker_V4.1x)` | Tufan Uysal (SoNiC) — 1996 The Art Project Studios — CSDb #82320 |
| `(XTracker_V4.2x)` | (no separate .nfo entry; sub-entry under LordsOfSonics/MS) |
| `(X-Ample_Digi)` | (no separate .nfo entry; sub-entry under LordsOfSonics/MS) |
| `Geir_Tjelta/Comptech-X` | Geir Tjelta + Markus Schneider, 2019 — probably a private player for X-Ample members |

The `Comptech-X` entry is notable: it is a 2019 private variant created
collaboratively by Geir Tjelta and Markus Schneider. It is unlikely to appear
in HVSC #84 (only tunes post-dating this entry would use it).

---

## 4. Source availability

- **Compotech V2.1:** Available as a D64 disk image at CSDb release #122614
  (Pokefinder.org mirror). Not source code — the editor binary only. 451 downloads
  as of the fetch date.
- **The Ultimate X-Tracker V3.1:** CSDb release #17708. D64. Fred (2013 comment):
  "The player of this editor is 100% identical to Compotech V2.1."
- **The Ultimate X-Tracker V4.13:** CSDb release #82320. D64. 510 downloads.
  Nine demo tracks by SoNiC included.
- **Parsec Music Editor V5.1:** CSDb release #10744. D64 + T64. 1989, Mnemonic
  Designs. Code: Markus Schneider, ADT, Nic. Music: Jeroen Tel (Tomcat).

No source code for any of these editors has been extracted or published.

---

## 5. Implications for SIDfinity migration

- The migration must start from binary SID files (HVSC #84 `engine='X-Ample'`
  population = 381 tunes excluding Reflextracker).
- No prior disassembly annotation exists to bootstrap from; a fresh
  `tools/seed_disassembly.py` run on a canary SID (e.g. Thomas Detert's
  Starforce or a Markus Schneider Compotech V2.x tune) is required.
- The D64 disk images of Compotech V2.1 and XTracker V4.13 are downloadable
  from CSDb and could yield the editor binary (and embedded player routine) for
  disassembly. The XTracker V3.1 player is confirmed identical to Compotech V2.1
  (CSDb user comment, 2013).
- ChiptuneSAK / desidulate / sidtool provide no head-start; all are player-agnostic.

## Leads to follow

1. **Download Compotech V2.1 D64 (CSDb #122614)** and extract the embedded
   player binary. This is the primary player for the majority of the 381-tune
   corpus. The XTracker V3.1 player (CSDb #17708) is confirmed identical.
2. **Download XTracker V4.13 D64 (CSDb #82320)** and extract the player. This
   covers the SoNiC / `(Sonic/SDS)` and `(XTracker_V4.1x)` variants.
3. **Geir Tjelta / Comptech-X (2019 private):** Geir Tjelta has released SIDs
   on HVSC under `MUSICIANS/T/Tjelta_Geir/`. Check whether any post-2019 tunes
   in that directory carry the `Comptech-X` sidid signature (would require
   re-running sidid on those files).
4. **The `realdmx/c64_6581_sid_players` repo** covers composer-organised
   reverse-engineered players but has no X-Ample entry. Watch this repo — an
   X-Ample RE submission could appear.
5. **HVSC STIL.txt** (`/DOCUMENTS/STIL.txt`) may carry per-SID comments
   identifying which Compotech version a tune used. Worth grepping for
   "Compotech", "XTracker", "X-Ample" once the HVSC tree is available.
6. **Contact / community:** Markus Schneider has been active post-2002 (remix
   scene). The sidid.nfo entry for `Comptech-X` suggests he collaborated with
   Geir Tjelta in 2019. He may be reachable via CSDb or remix64.com for
   format documentation.
