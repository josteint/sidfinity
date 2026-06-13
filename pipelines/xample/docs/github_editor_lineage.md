# X-Ample / Compotech — Editor Lineage & Personnel

**Provenance:** Web fetches of CSDb release pages, Remix64 interviews,
VGMPF wiki, and sidid.nfo conducted 2026-06-13.
No siddump, py65, or disassembly was performed.

---

## 1. Editor / player lineage

### 1.1 Parsec Music Editor V5.1 (1989)

- **Release:** Mnemonic Designs, 1989. CSDb #10744.
- **Code:** Markus Schneider (handle: SMC), ADT, Nic.
- **Music demo:** Jeroen Tel (Maniacs of Noise) — "Tomcat".
- **Role:** First public release of the Schneider-family player.
  Established the foundational voice-loop architecture (3-voice bitmask
  dispatch, note/instrument table lookup). The base `X-Ample` sidid
  signature most likely identifies this player or its immediate derivative.
- **Source:** D64 disk image only (389 downloads as of 2026-06-13).
- **Note:** The VGMPF Markus Schneider wiki says the player was developed
  collaboratively with "Jens Blidon" (Lords of Sonics co-founder) in 1988,
  suggesting Parsec V5.1 was a refinement of an earlier in-house player.

### 1.2 Compotech V2.0 (1990) / V2.1 (1995)

- **Release:** X-Ample Architectures, 1990. CSDb #122614 (V2.1 uploaded 1995).
- **Code:** Markus Schneider + Helge Kozielek (optimisations) +
  Joachim Fräder (editor UI surface). Also credited: Chap Bizarre.
- **Description:** The "full tracker" evolution of Parsec. Adds a
  screen-based composition interface (patterns, sequences, instruments)
  wrapped around the same player core. sidid sub-variant `(Compotech_V2.x)`
  matches the dispatch loop of this player.
- **Source:** D64 disk image only (451 downloads). Not source code.
- **Key interview quote (Markus Schneider, Remix64):**
  "The last soundplayer [is] based on my old player. Helge Kozielek and
  Mario van Zeist did some corrections to optimise the speed [and]
  Joachim Fraeder [programmed] the surface."
- **Key interview quote (Thomas Detert, Remix64):**
  "Helge Kozieleck created together with Markus Schneider the X-ample
  Music Player. … On his first two games, he [Thomas] arranged using
  RoMuzak V6.3, and afterwards, in Compotech."

### 1.3 The Ultimate X-Tracker V3.1 (1996)

- **Release:** Smash Designs + The Art Project Studios, April 1996. CSDb #17708.
- **Code:** Tufan Uysal (SoNiC / The Art Project Studios / The Obsessed Maniacs).
- **Player relation:** CSDb user comment (Fred, 2013): "The player of this
  editor is 100% identical to Compotech V2.1." This means XTracker V3.1
  ships the Compotech V2.x player unmodified — it is only a new editor UI
  wrapping the same runtime.
- **Source:** D64 disk image only.

### 1.4 The Ultimate X-Tracker V4.13 (1996)

- **Release:** The Art Project Studios, 1996. CSDb #82320.
- **Code:** Tufan Uysal (SoNiC).
- **Player relation:** sidid variant `(XTracker_V4.1x)` — the player was
  revised to use an unrolled three-voice dispatch (three separate JSR calls
  instead of a bitmask loop). Nine demo SID tracks included in the release.
- **Source:** D64 disk image only (510 downloads).

### 1.5 Comptech-X (2019, private)

- **Source:** sidid.nfo entry from `WilfredC64/player-id` / `cadaver/sidid`:
  ```
  NAME: Comptech-X
  AUTHOR: Geir Tjelta
  RELEASED: 2019 <?>
  COMMENT: First used in 2019 by Geir Tjelta and Markus Schneider,
           probably private player for X-Ample members.
  ```
- **Implication:** A new variant of the player was created in 2019 as a
  collaboration between Geir Tjelta (Norwegian C64 composer, HVSC:
  `MUSICIANS/T/Tjelta_Geir/`) and Markus Schneider. Sidid has a signature
  for it but the player was not publicly released. Any post-2019 Tjelta or
  Schneider tunes in HVSC that use this engine would carry a distinct
  fingerprint.

---

## 2. Key personnel

| Name | Role | Connection |
|---|---|---|
| Markus Schneider | Coder + Musician | Founded Lords of Sonics 1988; joined X-Ample Architectures Mar 1989; authored the original Parsec player and co-authored Compotech. Handles: Diflex (1988), Synth-Man (1987-88), SMC. |
| Helge Kozielek | Coder | Optimised the player speed for Compotech (X-Ample). Later left X-Ample (listed as ex-member on CSDb). |
| Mario van Zeist | Coder | Also made speed corrections to the soundplayer (per Schneider interview). |
| Joachim Fräder (Multermann) | Coder | Programmed the editor UI ("surface") for Compotech. Still listed as core member of X-Ample on CSDb. |
| Thomas Detert | Musician | X-Ample Architectures founding member (1988). Used Compotech as primary tool. Produced 92 X-Ample SIDs in HVSC. His variant has a distinct sidid sub-signature `(Thomas_Detert)` — same Compotech player with minor idiom differences. |
| Tufan Uysal (SoNiC) | Coder + Musician | Created XTracker V3.1 / V4.1x / V4.2x. His `(Sonic/SDS)` variant has hardcoded $D404,X and $D418/$D416 writes. 123 X-Ample SIDs + 26 Reflextracker in HVSC. |
| Geir Tjelta | Musician + Coder | Norwegian composer. Collaborated with Schneider on `Comptech-X` in 2019 (private). |
| Michael Detert (Satzer) | Graphician | Thomas Detert's brother; co-founded X-Ample Architectures. |
| Jens Blidon | Coder | Lords of Sonics co-founder; collaborated with Schneider on early player (per VGMPF). |

---

## 3. Group context

**X-Ample Architectures (Germany)**
- Founded July 1988 by Stephen Taylor, Takashi, General X, Chap Bizarre.
- Became a commercial game development group (C64, Amiga, PC, PlayStation).
- Active 1988–2017 (primary 1988–1995).
- Motto: "Bit For Bit A Hit." CSDb group page: #245.
- The name "X-ample" explicitly stands for "Example."
- Notable game output: Bronx Medal, Genloc, Zillion, Darksword, Quadrant,
  Parsec (game), Dynamoid, Clystron, Starforce, B-Bobs, Gordian Tomb.

**Lords of Sonics**
- Founded by Markus Schneider, 1988. A music-focused group that predates
  his X-Ample membership.
- sidid.nfo groups the X-Ample base player under `LordsOfSonics/MS` —
  reflecting that the player was Schneider's personal work, brought into
  X-Ample, not a group-built artefact.

---

## 4. Confirmed negatives from this cluster

- **No source code** of Compotech, Parsec, or any XTracker version is
  publicly available (as of 2026-06-13).
- **No GitHub repository** contains a parser, converter, or decoder for
  the X-Ample / Compotech music format.
- **No annotated disassembly** of the player (`.s`, `.asm`, `.dis`)
  exists in any public repository checked (cadaver/sidid, ice00/jc64,
  realdmx/c64_6581_sid_players, WilfredC64/player-id).
- **Zimmers.net** `pub/cbm/c64/audio/editors/` does not contain
  Compotech, XTracker, or Parsec archives.
- **ChiptuneSAK / desidulate / sidtool** have no X-Ample support.

## Leads to follow

1. **Compotech V2.1 D64 (CSDb #122614, Pokefinder mirror)** — download the
   binary and extract the embedded player routine. This is the highest-ROI
   action: it covers the majority sub-variant and the XTracker V3.1
   player (which is confirmed identical).
2. **XTracker V4.13 D64 (CSDb #82320)** — covers the SoNiC `(Sonic/SDS)` /
   `(XTracker_V4.1x)` variants; 9 demo tracks included for canary SID
   selection.
3. **Parsec Music Editor V5.1 D64 (CSDb #10744)** — earliest extant version;
   useful to understand what the base `X-Ample` sidid signature matches (the
   pre-Compotech player).
4. **Geir Tjelta HVSC tunes** — check `MUSICIANS/T/Tjelta_Geir/` SIDs
   post-2019 for Comptech-X fingerprints using `sidid`.
5. **Markus Schneider contact** — active on CSDb and remix64.com (Symphonic
   Dreams). May provide format documentation or player source directly.
6. **HVSC STIL.txt** — grep for "Compotech" / "XTracker" / "X-Ample"
   per-SID notes; some composers annotate which editor version they used.
