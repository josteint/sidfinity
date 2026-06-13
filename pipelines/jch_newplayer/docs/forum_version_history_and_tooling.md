<!--
source_url: (multiple — per-section attribution)
  - https://csdb.dk/release/?id=14037  (JCH Editor V3.04 20G4 / NewPlayer 20.G4, Vibrants 1991)
  - https://csdb.dk/release/?id=33785 , id=26563 , id=20112 , id=101622  (NP21 releases)
  - https://csdb.dk/forums/index.php?roomid=10&topicid=5698  (CSDb "From jch newplayer file to SID")
  - https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/utils/  (Vibrants tool listing)
  - https://www.lemon64.com/forum/viewtopic.php?t=10351 , t=63546  (Lemon64; via search snippets — direct fetch was rate-limited 503)
  - https://blog.chordian.net/...  (JCH/Chordian editor history)
  - https://codebase64.pokefinder.org/...  (codebase64, via search)
fetched_via: WebFetch + WebSearch (small-model summarization; Lemon64 lines are from
             search-result snippets — Lemon64 + the CSDb forum thread both returned
             HTTP 503 Retry-After:3600 to the fetcher on 2026-06-13 and could not be
             read in full this session)
fetch_date: 2026-06-13
author/handle: JCH, Dane, SIDWAVE, Steppe, Yaemon, Yodelking, St0fF (scene handles); CSDb editors
content_date: editor 1991; CSDb comments 2003-2011; NP2011 mentioned 2011
reliability: secondary
-->

# JCH NewPlayer — version history, editor ecosystem, ripping & identification

Companion to `forum_version_lineage_and_comparison.md` (which covers the
JCH↔Laxity↔CheeseCutter fork chain and the quantitative comparison). This doc
covers the version timeline, the period tools, and how the format is
ripped/identified — the part the CSDb/forum cluster surfaced.

## 1. Version timeline (consolidated from CSDb + chordian + codebase64)

| Version | Era / notes | Source |
|---|---|---|
| NP10.G0 | "packer and relocator" (early) | chordian scanned notes |
| NP15.G7 | improvement notes for next version | chordian scanned notes |
| NP17.G0 / 17.G1 | classic; 17.G1 has the documented hard-restart impl; one of the 3 "most known" players | codebase64; chordian |
| NP20.G4 | **the standard JCH player**; shipped in JCH Editor V3.04 (Vibrants, 1991); "the last official version of this editor" | CSDb id=14037 (SIDWAVE) |
| NP20.Q0 | **multispeed** ("Q = quattro") sibling of 20.G4 | codebase64 |
| NP21.b4 (beta) | 2005-08-27, Maniacs of Noise + Vibrants | CSDb id=20112 |
| NP21.G4 (final) | 2006-01-16, MoN + Vibrants (Laxity) | CSDb id=26563 |
| NP21.G5 | 2006-05-09, "Laxity of Maniacs of Noise and Vibrants"; TLR: "use together with JCH Editor V3.04 20G4" | CSDb id=33785 |
| NP21.G6 | Samar Productions (2000 listing) | CSDb id=101622 |
| NP21.B6 | "B stands for booty"; based on Laxity's NP21.G5; the basis for CheeseCutter | CheeseCutter About |
| NP2011 | a newer player Dane was documenting for JCH Editor v3.05 (2011) | CSDb id=14037 (Dane) |

> Verbatim (CSDb id=14037):
> - SIDWAVE (2004): "This is the last official version of this editor. The
>   complete sourcecode and loads of worktunes by Vibrants, can be found at
>   http://www.vibrants.dk"
> - Dane (2011): "Version v3.05 should be ready soonish. I'll just need to write
>   some proper docs for the NP2011-player first"
> - JCH (2008): "The newest revision of this release can be found at
>   http://vibrants.dk/files.htm"
> - commenter (2011): "There exists at least up to v3.07 in HVMEC 1.0"

Credits line for the editor: **"Code .... JCH of Dominators, Ikari, Vibrants."**

> Practical takeaway: the two HVSC-relevant families are
> **(a) NP17/NP20.G4/NP20.Q0** (JCH, 2-byte tables, 32 insts) and
> **(b) NP21.x / NP2011 / CheeseCutter** (Laxity-line, 4-byte pulse/filter + 3-byte
> command table, up to 48 insts). research.md's "NP 22-25" likely fold into the
> 21/2011/CheeseCutter continuum — no distinct 22-25 release surfaced in the
> forum/CSDb cluster; treat those numbers as private/derivative builds until a
> primary source confirms.

## 2. Entry points & memory (forum-confirmed)

> Steppe (CSDb forum, 2003-07-28): "JCH uses standard init=$1000, play=$1003."

Zero page: `$FB-$FC` (2 bytes) per JCH's own comparison table; CheeseCutter's is
"2; can be user defined." So for a stock JCH rip, zero-page `$FB/$FC` are the
player's pointer scratch — relevant if relocating or if the rip's zp clashes.

## 3. Ripping & conversion to SID — the period workflow

From the CSDb thread "From jch newplayer file to SID .. how?" (roomid=10,
topicid=5698):

- **Yaemon:** extract the `.prg` from the `.d64`, then load it in a SID editor
  and save as SID with init=$1000 / play=$1003 set.
- **Yodelking (2003-07-29):** "a JCH-packer that can be found on the Vibrants
  page"; warned that "tunes sounding different after the packing" can happen —
  **verify after packing** (directly relevant: a packer that changes the
  write-log would break SIDfinity's verdict; rip the *unpacked* tune).
- **St0fF (2003-09-22):** the "AcidTrackMusicDevelopment System 3.2" can "produce
  .sid-files directly" with a working packer.

Period tools (zimmers.net Vibrants/utils listing):
- `VibRip50.00.prg` — "VibRip", the music ripper.
- `Relocate JCH.prg` **and** `Relocate Laxity.prg` — *separate* relocators for
  the JCH vs Laxity player code (evidence the two are distinct enough to need
  different relocation logic; see lineage doc).
- `Deluxe Driver-2.0..5.0.prg` — playing/relocating JCH tunes.
- `JCH Split v1.1.prg`, `JCH Coder v1.prg` (passwording), `JCH Editor v1.4G`.
- A "Syndrom JCH-depacker" is also referenced (Lemon64, via search) for unpacking
  old packed tunes.

> For SIDfinity: HVSC tunes are already SIDs at init=$1000/play=$1003, so the
> ripping step is moot — but the packer warning matters: some HVSC JCH SIDs may
> be *packed* (data relocated/compressed by the JCH packer). If a tune's table
> regions don't sit at the expected `$18CB+` offsets (NP20 layout in research.md),
> suspect a packed/relocated build and resolve addresses via the player's pointer
> setup rather than assuming the canonical map.

## 4. Identification

- Modern: **SIDId** signatures — research.md notes ~21 NewPlayer signature
  variants (V1-V20, V0x) plus a distinct **Dane_NewPlayer** signature. These
  fingerprint the *player code* dialect, not the format; all decode with the same
  family codec, parametrised by table width (2 vs 4 byte) + command-table width
  (2 vs 3 byte) + instrument count (32 vs 48).
- The cleanest *binary* discriminators (no SIDId needed), in priority order:
  1. pulse/filter table **row width** (2 byte ⇒ NP20-era; 4 byte ⇒ NP21+/CC);
  2. command table **row width** (2 byte ⇒ NP20; 3 byte, first byte = command id ⇒ NP21+/CC);
  3. **instrument count** cap (32 ⇒ NP20; 48 ⇒ CheeseCutter);
  4. max **rows/sequence** (180 ⇒ NP20; 64 ⇒ CheeseCutter).
- Multispeed (Q-series / NP21 multispeed): detect by the play routine emitting
  the `$D400` write block >1× per PAL frame; verify via `siddump --writelog`
  (and `--writelog-per-irq` for CIA-timed subtunes), never per-50Hz snapshot.

## 5. Documentation provenance (where the primary source lives)

- JCH released the **complete player source + worktunes + docs** at
  `vibrants.dk` (`vibrants.dk/files.htm`) — SIDWAVE & JCH, CSDb. This is THE
  primary source for the byte-exact format and should be the next acquisition
  (the GitHub/source-cluster sibling agent may already be pulling CheeseCutter +
  SF2; the *original JCH NP source* on vibrants.dk is the matching primary for
  the NP17/NP20 era).
- HVMEC 1.0 (High Voltage Music Engine Collection) reportedly contains JCH
  Editor up to v3.07 — another route to the source if vibrants.dk is down.
