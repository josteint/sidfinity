# JCH NewPlayer — version lineage & changelog

> Provenance
> - source_url: https://blog.chordian.net/computer-timeline/ (primary, JCH's own dated log);
>   https://raw.githubusercontent.com/theyamo/CheeseCutter/master/src/c64/player_v4.acme (NP21.G4 lineage header + format);
>   http://web.archive.org/web/20190811215852/http://theyamo.kapsi.fi/ccutter/about.html (CheeseCutter ↔ NP21 lineage prose);
>   https://csdb.dk/release/?id=100406 (NP22-25 / Dane, 2011);
>   https://sidpreservation.6581.org/sid-trackers/ + DeepSID (G/Q meanings)
> - fetched_via: chordian/sidpreservation = direct (WebFetch) 2026-06-13; CheeseCutter raw = direct (curl); theyamo about + csdb = wayback 2026-06-13
> - fetch_date: 2026-06-13
> - author of underlying facts: Jens-Christian Huus (chordian); Abaddon/theyamo (CheeseCutter); Dane (NP22-25)
> - content_date: 1987–2011
> - reliability: HIGH for the chordian dated timeline and the CheeseCutter source header; MEDIUM where dates are inferred (NP21 series, exact 22-25 dates).

Goal of this file: **distinguish versions when parsing the binary** — which
suffix means what, where the table-width break happens, and which branch a given
HVSC tune belongs to.

---

## 0. The THREE branches (read this first)

The "NewPlayer" name spans **three authors**, not one. Getting this wrong is the
biggest version-parsing trap:

| Branch | Versions | Author | Notes |
|---|---|---|---|
| **JCH original** | v05 … **v20.G4 / 20.Q0** | Jens-Christian Huus | v20.G4 (May 1991) = JCH's *last* standard player by his own statement. |
| **Laxity continuation** | **NP21.G4 / G5 / G6**, NP21.B6 | Laxity (Vibrants/MoN) | The 21-series is Laxity's, not JCH's. CheeseCutter forked NP21.G4/G5. |
| **Dane resurrection** | **NP22, 23, 24, 25** | Dane (Booze Design), 2011 | Modern revival w/ JCH-Editor 3.1; comprehensive English manual. |

Derivatives commonly named in SIDId / HVSC: **Dane_NewPlayer**, **Glover_NewPlayer**,
**Laxity NewPlayer V21** — these are relocated/customised forks, not new branches.

---

## 1. Suffix grammar (G / Q / B + number)

> source: sidpreservation.6581.org/sid-trackers + DeepSID + CheeseCutter about (verbatim "the B stands for booty")

- **G = "standard"** single-speed player (e.g. 17.G0, 20.G4, 21.G4). Single
  50 Hz `play()` at $1003. ~12–13 rasterlines for 20.G4.
- **Q = "quattro" = multispeed** (e.g. 17.Q?, 20.Q0). CIA-timer-driven sub-frame
  dispatch (`$dc04/$dc05`, default $4cc7) with a software divider — see the
  `custplay.acme` wrapper captured in `archive_jch_vibrants.md` §2b. **PSID will
  carry speed!=0** for these → use the per-IRQ writelog capture path.
- **B = "booty"** — a CheeseCutter-era label (NP21.B6), based on Laxity's NP21.G5.
- Trailing digit = revision within the major (G4 = 4th rev of the v20 standard).

---

## 2. JCH original timeline (verbatim dates from chordian.net)

> source_url: https://blog.chordian.net/computer-timeline/ | reliability: HIGH (his own log)

| Version | Date (verbatim) | Notes (verbatim where quoted) |
|---|---|---|
| (proto) | **Jul 1987** | "Started coding the first versions of NewPlayer (no editor yet)" |
| NP v05.02 | **Jan 1989** | first numbered, for the music editor |
| NP v06.01 | **Apr 1989** | for the music editor |
| NP v12.G3 | **Jul 1990** | (note: chordian lists 12.G3 *after* 14/15 by date — log ordering, not version order) |
| NP v14.G0 | **May 1990** | for the music editor |
| NP v15.G0 | **May 1990** | for the music editor |
| NP v15.G6 | **Jul 1990** | for the music editor |
| NP v17.G1 | **Oct 16, 1990** | for the music editor |
| NP v17.Q? | **Jan 13, 1991** | "Quick"/quattro multispeed variant |
| NP v18.G0 | **Feb 1991** | for the music editor |
| NP v19.G1 | **Mar 1991** | for the music editor |
| **NP v20.G4** | **May 1991** | **"my last standard player on C64"** |

Editor + tooling milestones (same log):
- Sequenced editor v1 line: **ED2.53 / D13 / 09.01** (May 1989).
- Editor **v3 series** started Dec 1990; **ED3.04 / D15 / 20.G4** (Aug 16, 1991,
  "my final music editor", built with Einstein's EASS Amiga util).
- Support tools: NP-PACKER V2.5 (May 1989) → V5.3 (Mar 1991, "for the v3-series
  editor"); RELOCATOR V1.1, SWAPPER V1.0 (both May 1989).
- CSDb also lists: J-Coder V1.0 (1989), JCH Relocator V1.1 & V2.0 (1989),
  NP-Pack V3.1 (1989); editor re-releases V1.11/V2.53/V2.55 and **JCH Editor
  V3.03 20G4 (1991)** / V3.04.

> The HVSC tune-file prefixes on funet encode the player version: `06*` = v06,
> `09*` = v09, `12jchNNj.prg` = v12, `15chordi.prg` = v15, etc. Useful for
> bucketing which player a given JCH tune used.

---

## 3. Laxity 21-series + CheeseCutter (the table-width break)

> source_url: theyamo CheeseCutter player_v4.acme header + about.html (wayback 20190811215852) | reliability: HIGH

CheeseCutter's own history prose (about.html, verbatim fragments):
- CC "0-series" aimed for **JCH-Editor compatibility** ("Most JCH Editor files
  are compatible").
- CC v2/v4 player "**Based on JCH NP 21.G4 by Laxity / Vibrants / MoN**" and
  "has almost all the features of **NP21.B6** … which was **based on Laxity's
  NP21.G5**."

So the chain is: **JCH NP20.G4 → Laxity NP21.G4 → NP21.G5 → NP21.B6 →
CheeseCutter (cc4.07 / player_v4)**.

### The format break — 2-byte (NP20.G4) → 4-byte (NP21+/CheeseCutter)
This is the single most important parsing distinction between branches:

| Table | NP20.G4 (JCH) | NP21+ / CheeseCutter (Laxity-derived) |
|---|---|---|
| **Pulse** | 2 bytes/row | **4 bytes/row** (dur+dir, add, init-PW[nibbles reversed], next-ptr/$7F-stop) |
| **Filter** | 2 bytes/row | **4 bytes/row** (dur/type, add/res+mask, init/$FF-skip, next-ptr/$7F-stop) |
| **Instruments** | 32 max, row-major-ish | **48 max (INSNO=48), COLUMN-MAJOR** (stride = INSNO per field) |
| **Multispeed** | only Q-series | compile-time `MULTISPEED=TRUE` (CIA $4cc7) |

(Field-level byte semantics for the 4-byte tables + the column-major instrument
layout are quoted verbatim from the released `player_v4.acme` in
`archive_jch_vibrants.md` §2a — the parser should read them from there.)

Wave table stayed **2 columns** across versions (transpose/loop + waveform/delay).
Effect/Super-Table command set stayed **$00–$08** (slide up/down, hi-fi vibrato,
detune, set ADSR, lo-fi vibrato, set wave, portamento, stop) across NP20/NP21/CC.

---

## 4. Dane NP22-25 (Booze Design, 2011)

> source_url: csdb.dk/release/?id=100406 (wayback 20250617141300) | reliability: HIGH (CSDb record), but per-version detail is in the unfetched manual

- **JCH-Editor 3.1 + NP22-25**, Booze Design, **6 Jun 2011**, all by **Dane of
  Booze Design**. Ships players NP22/23/24/25 ("several players" trading
  **raster-time vs flexibility**) + a comprehensive **English manual**.
- The per-version differences among 22/23/24/25 are documented in the manual
  **`NP22-25 docs.doc`** (csdb.dk/getinternalfile.php/97829) — NOT yet fetched
  (it's a binary .doc; needs a converter). **This is the #1 outstanding doc to
  pull** to complete the 22-25 column of this table.
- Working hypothesis (from the "raster-time vs flexibility" blurb, UNVERIFIED):
  the four players are feature-graded builds of one engine (cf. CheeseCutter's
  `INCLUDE_*` compile flags), differing by which effect commands / tables are
  compiled in — i.e. likely the **same data format** as NP21, with players
  picked by raster budget. Confirm against the manual before relying on it.

---

## 5. Quick decision tree for "which NP is this binary?"

1. init=$1000, play=$1003 → NewPlayer family (all branches).
2. PSID speed != 0 (CIA) OR a `[lo,hi,play,init]` 4-byte head with `$dc04/$dc05`
   writes → **Q-series / multispeed**; else G-series single-speed.
3. Pulse/Filter rows 2 bytes wide + ≤32 instruments → **NP20.G4 / JCH original**.
4. Pulse/Filter rows 4 bytes wide + up to 48 instruments (column-major inst
   table, stride=INSNO) → **NP21 (Laxity) / CheeseCutter / NP22-25 (Dane)**.
5. Distinguish 21 vs 22-25 vs CheeseCutter by code signature (SIDId variants —
   research.md notes 21 distinct signatures incl. Dane_NewPlayer) and/or the
   `version !pet "ccX.YZ"` string CheeseCutter embeds.

> Cross-check any version verdict against SIDId's signature buckets and DeepSID's
> player-ID string before committing — code reloc + custom forks blur the lines.
