<!--
source_url: (multiple — see per-section attribution)
  - http://chordian.net/c64editors.htm  (JCH's own editor-comparison table)
  - https://chipmusic.org/forums/topic/3753/  (CheeseCutter port thread; quoted via search)
  - https://theyamo.kapsi.fi/ccutter/about.html  (CheeseCutter About; quoted via search)
  - https://csdb.dk/release/?id=33785 , id=26563 , id=20112 , id=101622  (CSDb release pages)
  - https://blog.chordian.net/2015/07/01/im-back/...  (JCH editor history)
fetched_via: WebFetch + WebSearch (small-model summarization; some lines quoted from
             search-result snippets where the page itself 401/403'd the fetcher)
fetch_date: 2026-06-13
author/handle: JCH (Jens-Christian Huus / Chordian); Abaddon/theyamo (CheeseCutter); CSDb editors
content_date: table content 2018; CheeseCutter ~2011+; CSDb releases 2000-2006
reliability: secondary
-->

# JCH NewPlayer — version lineage, forks, and editor comparison

## 1. Lineage: who wrote what, and how the forks relate

The task asked specifically how Laxity_NewPlayer_V21, Dane_NewPlayer and
Glover_NewPlayer relate to JCH NewPlayer. Findings:

**JCH released his player source**, which is *the* reason there is a sprawling
"NewPlayer" family at all:
> "Many coders and composers took the step to write/improve their own 'New
> Players', since JCH was kind enough to release the source code for his
> players." — Codebase64 / chordian (via search)

So the relationship is overwhelmingly **same format lineage + different /
patched player code**, not independent engines:

- **NP17.G0, NP20.G4, NP20.Q0** — the classic JCH-authored players. Q = "quattro"
  = multispeed (see §3). These are the 2-byte-table era.
- **NP21.G4 / 21.G5 / 21.G6** — the 21-series. CSDb attributes these to **Laxity
  of Maniacs of Noise and Vibrants** (NP21.g5 released 2006-05-09; NP21.g4 final
  2006-01-16; 21.b4 beta 2005-08-27). So **"Laxity NewPlayer V21" IS the NP21
  line** — Laxity continued/forked JCH's player into the 21 series under the
  Vibrants/MoN banner. Not a separate engine; a continuation of the same format
  family with the wider (4-byte) tables.
- **CheeseCutter** (Abaddon / theyamo) is the cross-platform port:
  > "CheeseCutter has almost all the features of NP21.B6 (the B stands for
  > booty), which was based on Laxity's NP21.G5, and dozens more."
  > — CheeseCutter About (via search)
  i.e. lineage chain: **JCH NP → Laxity NP21.G5 → NP21.B6 → CheeseCutter**.
- **Dane_NewPlayer / Glover_NewPlayer** (as SIDId-named variants): these are
  per-musician patched copies of the same NewPlayer. CheeseCutter's About lists
  the editor's users as "Laxity, Drax, **Mitch & Dane** and of course JCH" — i.e.
  Dane composed on this player family; "Dane_NewPlayer" is his fingerprinted
  build of it. Treat Dane_/Glover_/Laxity_NewPlayer as **player-code dialects of
  one format family**, discriminated by SIDId signature, not as separate formats.
  (SIDId already enumerates ~21 NewPlayer signature variants incl. Dane_NewPlayer
  — see research.md.)

> **DMC ↔ JCH lineage:** they are *contemporaries and competitors*, NOT a fork
> chain. DMC (Demo Music Creator, Brian of Graffity, the engine of the separate
> `pipelines/dmc/` focus) is a distinct engine with a different memory map,
> ≥5 zero-page bytes, globally-set hard restart, and 3500+ byte player. JCH's
> NewPlayer has per-instrument hard restart and a ~1900-byte player. They share
> the broad "table-driven SID tracker" design idiom of the era but not code or
> byte format. See the comparison numbers in §2.

## 2. Editor / player comparison table (JCH's own c64editors.htm) — verbatim figures

These are the cleanest *quantitative discriminators*. Source: chordian.net
comparison table (authored by JCH himself).

### JCH Editor 3.04 / NP 20.G4
- Player size: "Less than 1900 bytes"
- Zero page: "2 ($FB-$FC)"
- CPU @1x: "Approx 28-33 rasterlines"
- Instruments: 32
- Max sequences: "127 (up to 180 rows each)"
- Hard restart: "For each instrument"
- Multispeed: "1x (to 4x when loading patch)"

### CheeseCutter 2.9 (= NP21.B6 lineage)
- Player size: "Less than 2300 bytes"
- Zero page: "2; can be user defined"
- CPU @1x: "Approx 31-36 rasterlines"
- Instruments: 48
- Max sequences: "128 (up to 64 rows each)"  ← note SHORTER max rows (64) vs NP20's 180

### DMC 5.0 (separate engine — for contrast)
- Player size: "3500+ bytes (uncompressed)"
- Zero page: "At least 5 ($FB-$FF)"
- CPU @1x: "Most of the screen"
- Instruments: 32
- Max sequences: "96 sectors (up to 250 rows each)"
- Hard restart: "Set globally"  ← vs JCH "for each instrument"
- Multispeed: "1x"
- "from 1993 by Brian of Graffity"

> CORRECTION to research.md: research.md's "CPU: ~12-13 rasterlines (NP 20.G4)"
> conflicts with JCH's own table ("Approx 28-33 rasterlines"). The 28-33 figure
> is from the author and should be preferred. (12-13 may have been a single-voice
> or best-case number, or simply wrong.) Likewise research.md "Code size ~1000
> bytes" vs JCH "Less than 1900 bytes" — prefer <1900.

> Instrument-count discriminator: **32 insts ⇒ NP20.G4 / JCH-era**;
> **48 insts ⇒ CheeseCutter/NP21.B6-era**. Max-rows-per-sequence also flips
> (180 → 64). Useful alongside the 2-byte vs 4-byte table-width test.

## 3. The Q-series (multispeed / "quattro")

> "Multispeed works by accessing the soundchip more often to increase the
> resolution. The most known 'New Players' used are: 17.G0, 20.G4, 20.Q0. The
> Q-series stands for quattro and is used for multispeed songs."
> — Codebase64 (via search)

Implications for SIDfinity:
- **NP20.Q0 is the multispeed sibling of NP20.G4** — same format, player calls
  the SID-update inner loop multiple times per frame. The comparison table's
  "1x (to 4x when loading patch)" for the G-player means the *standard* G-player
  is single-speed but a multispeed patch raises it to up to 4x; the Q-player is
  the pre-patched multispeed build.
- A Q-series / multispeed tune will emit its `$D400` write block N times per
  PAL frame (N = framecall multiplier). Per the project's verification notes,
  multispeed tunes must NOT be verified with a per-50Hz-frame register snapshot
  (Trap A / Monty-class) — use the write-log `(reg,val)` stream and, for
  CIA-timed subtunes, `siddump --writelog-per-irq`.
- CheeseCutter exposes the multispeed framecall counter directly in its UI
  ("Decrease/increase multispeed framecall counter" — help.d), confirming it's a
  per-song integer multiplier on the play-routine call rate.

## 4. CheeseCutter format deltas vs the classic NP (from the port author) — verbatim

> "Many commands are accessible directly from a sequence so the Command table is
> not used nearly as much as it used to be."
> "The command table is 3 bytes wide instead of 2, with the 1st byte simply
> denoting the command to be used."
> "All filter settings can only be controlled from the filter table."
> "The downside of the extensive feature set is additional memory and rastertime
> use, though you can flag out unused effect code if willing to assemble the
> final tune from a source dump."
> — CheeseCutter About / docs (via search)

These pin down three codec-relevant facts:
1. **Command table widened 2→3 bytes at NP21/CheeseCutter** (byte 1 = command
   id). Confirms the 3-byte command-table layout in
   `forum_cheesecutter_np21_format.md`, and that NP20-era command table is 2-byte.
2. The **rich sequence command column** ($01-$FF map in the NP21 doc) exists
   precisely because commands moved inline into the sequence — so an NP21 rip
   carries most effects in the sequence stream, not the command table.
3. Filter is **table-only** in CheeseCutter (no inline filter command beyond the
   filter-pointer change).
