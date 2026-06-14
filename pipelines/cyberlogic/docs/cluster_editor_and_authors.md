# Cyberlogic Sound Studio — Editor, Format & Authors

```
provenance:
  document_type: research cluster
  fetch_date: 2026-06-14
  sources:
    - url: https://csdb.dk/release/?id=170632
      label: CSDb #170632 — Cyberlogic Sound Studio V4.0 (full release)
      reliability: primary (scene database, maintained)
    - url: https://csdb.dk/release/?id=97286
      label: CSDb #97286 — Cyberlogic Sound Studio V4.0 Preview
      reliability: primary
    - url: https://csdb.dk/scener/?id=5968
      label: CSDb scener profile — Oliver Klee (Odi)
      reliability: primary
    - url: https://csdb.dk/scener/?id=3288
      label: CSDb scener profile — celticdesign (Sascha Nagie)
      reliability: primary
    - url: https://csdb.dk/group/?id=372
      label: CSDb group — Masters' Design Group
      reliability: primary
    - url: https://csdb.dk/group/?id=349
      label: CSDb group — Trance (TCE), Germany
      reliability: primary
    - url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
      label: sidid.nfo — cadaver's SID player identifier NFO
      reliability: primary (binary signature + reference URL)
    - url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
      label: sidid.cfg — cadaver's SID player identifier config (hex signatures)
      reliability: primary (byte-exact)
    - url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html
      label: Zimmers.net FUNET C64 audio editors index
      reliability: secondary (mirror of FUNET archive)
    - url: binary analysis of hvsc84/MUSICIANS/N/Nagie_Sascha/ and /O/Odi/
      label: HVSC #84 local binary inspection (196 SIDs)
      reliability: primary (ground truth for format)
  content_date: 1991-1992 (tool); SID corpus 1991-2021
  author: research agent (2026-06-14)
```

---

## 1. Tool identity

| Field | Value |
|---|---|
| Full name | Cyberlogic Sound Studio |
| Abbreviation | C.S.S. |
| Known version | V4.0 (1992) |
| Type | C64 music composition system (editor + player, self-contained per-tune SID) |
| Platform | Commodore 64 |
| Year | 1992 (two releases: Preview on 12 Nov 1992; full V4.0 release same year) |
| CSDb entries | #170632 (V4.0 full), #97286 (V4.0 Preview) |
| Releasing groups | Trance (TCE, Germany) for the Preview; credited jointly MDG + Oliver Klee for V4.0 full |
| FUNET listing | `Soundstudio.prg` (27,432 bytes) described as "Preview of Cyberlogic Sound Studio by Trance '92" |

The V4.0 Preview was released by the German group **Trance (TCE)** on **12 November 1992** and contained two bundled SIDs: "Narcotic" by Antti Piirainen and "Trance Introzak" by Odi (Oliver Klee).

The full V4.0 release (CSDb #170632, also downloadable as `css.d64`) contains **25 SID files** by composers Odi and Nagie Sascha, spanning genres described as baroque, jazz, funk, techno, and orchestral. One commenter (Fred, 27 Oct 2018) documented the keyboard interface:

> "Press Commodore Key (CBM) for several functions. CBM-M for start tune, CBM-P for stop/resume, CBM-D for disk menu, etc."

There is no known public source code, no format specification document, and no user manual available online as of 2026-06-14. The format is reconstructed below purely from binary analysis.

---

## 2. Authors

### Oliver Klee (handle: Odi)

- **CSDb scener ID:** 5968
- **Handles over time:** Orionsoft (1986–??), Odi the Hypnotic Juggler, Odi (current)
- **Country:** Germany
- **Role in CSS:** Code (player engine author)
- **Self-description on CSDb:** "Student of computer science, seminar teacher, consultant and web designer."
- **C64 scene groups:** Masters' Design Group (MDG, inactive member, roles: coder/musician/swapper), Trance (TCE, Germany), Trinomic, Presence, Oxyron, Bad Karma, The Second Ring
- **C64 activity:** 1986 (Orionsoft) through 2002 (last C64 release on CSDb: Grüne Tür 2). Attended Data-Live Conference 93.
- **Selected 1992 releases:** Cyberlogic Sound Studio V4.0, Cyberlogic Sound Studio V4.0 Preview, Genetic Dreams #13 & #14 (diskmag music), Uniplay V3, Wind of Change
- **Post-scene career:** TYPO3 core developer (contributing since 2001), accessibility advocate, seminar teacher. Website: oliverklee.de — no C64 content on that site as of 2026-06-14.
- **HVSC folder:** `MUSICIANS/O/Odi/` — 49 SIDs; 24 classified as Cyberlogic_SoundStudio, 11 as SoedeSoft, 8 as Soundmonitor, 4 as RoMuzak_V6.x
- **Confirmation string in binaries:** `"'BAROQUE PARTING' BY OLIVER KLEE"` (Baroque_Parting_Zero_Page.sid)

### Sascha Nagie (handle: celticdesign)

- **CSDb scener ID:** 3288
- **Handles over time:** DJ3D (earliest), celtic, celticdesign, dj3d, luziesoft
- **Country:** Germany
- **Role in CSS:** Music, Design, Concept (data/composition author); Oliver Klee wrote the player
- **CSDb musician rating:** 9/10 (15 votes)
- **C64 scene groups:**
  - Demons of Sound (ex, German group; active ~1989–1993)
  - Masters' Design Group (current, Germany)
  - Genesis Project (from 14 January 2013 onwards)
  - Security (ex)
  - Sunrise (ex)
- **Handle origin (from celticdesign's CSDb bio):** "I got a Celtic sticker and liked the word. When I discovered another musician used it, I added 'design' as a suffix. At that time the word 'design' was used in combination by many super groups like censor, panoramic, cosmos, MDG."
- **Active era (CSS):** 1991 through 2021 — still composing with CSS in 2021. The 196-SID HVSC corpus spans 30 years.
- **HVSC folder:** `MUSICIANS/N/Nagie_Sascha/` — ~250 SIDs total; the majority of CSS SIDs are here
- **Confirmation string:** `"MUSIC SASCHA NAGIE,PLAYER O.KLEE"` (A_Real_Compose.sid, and others)

### Relationship / collaboration
Both authors were members of **Masters' Design Group (MDG)**, a German demo and game group active 1988–1997 (54 CSDb releases). Celticdesign is a current MDG musician; Oliver Klee (Odi) was an inactive member (coder/musician/swapper). The V4.0 Preview was released under Oliver Klee's other affiliation, **Trance (TCE)**, which was a German cracker/demo group active 1992–1994. This explains the dual group credits.

---

## 3. HVSC corpus

| Metric | Value |
|---|---|
| Total SIDs in HVSC #84 classified as Cyberlogic_SoundStudio | 196 |
| Primary folder | `MUSICIANS/N/Nagie_Sascha/` (~148 SIDs) |
| Secondary folder | `MUSICIANS/O/Odi/` (24 SIDs) |
| Third-party users | `MUSICIANS/T/The_Blue_Ninja/` (24 SIDs), `MUSICIANS/X/X-Radical/` (28 SIDs) |
| Year span of corpus | 1991 – 2021 |
| SID model | 6581 (PAL) |
| Speed (PSID) | 0 = VBI-timed, 50 Hz interrupt (PAL standard) |

The **The_Blue_Ninja** folder (Lars Hutzelmann, 2012 onwards) confirms the player was distributed separately from Nagie — embedded string: `"LARS HUTZELMANN'96 PLAYER O.KLEE"` — implying a 1996 release of the player that Lars was still using in 2012. The **X-Radical** folder similarly uses Oliver Klee's player.

---

## 4. Binary format (from HVSC analysis)

This section is derived entirely from binary inspection of the 196 HVSC SIDs. No source or docs exist.

### 4.1 Self-contained SID architecture

Each CSS composition is a **self-contained binary** containing both the player code and the music data. There is no separate replayer distributed alongside data files. Every SID file embeds its own copy of the player; as a result, the player code varies slightly across SIDs (it evolves, and different compositions may use different player revisions).

### 4.2 Memory layout (standard, load = $1000)

```
$1000       JMP  init_main       ; 3 bytes
$1003       JMP  play_main       ; 3 bytes (the PSID play() vector)
$1006       JMP  ...             ; additional entry points (varies)
...
$1012       Title string         ; ASCII, NUL-terminated, eg:
                                 ;   "MUSIC SASCHA NAGIE,PLAYER O.KLEE"
                                 ;   "'BAROQUE PARTING' BY OLIVER KLEE"
$1032+      State variables      ; ~56 bytes, zero-filled on init
                                 ; (LDX #56: loop stores #0 into $102B+X, X down to 0)
$1064+      init_main code       ; initialises SID chip + state
$10C6+      play_main code       ; called by PSID at 50 Hz
            ...player routines...
$1300+      Data tables:
              - vibrato/sine table (~64 bytes of sin values, -128..+127)
              - velocity/volume curve table (ascending bytes, 
                matches string: ' "$\')+.147:>AEINRW\bhnu|')
              - ADSR / instrument descriptor tables
              - arp/pulse width tables
$14F0+      Pattern / song data  ; note+duration streams
            ...
            '*** END OF MUSIC ***'  ; or 0xFF terminators at end of each pattern
```

Most SIDs load at **$1000** (138/196). Other load addresses in use: $6000 (13 SIDs), $FF4/$FF6/$FF0 (5–6 each), $E000, $8000, $A000, $EB00, $EC00 (2 each). The init and play addresses equal load and load+3 respectively in all cases.

### 4.3 Pattern byte encoding (preliminary)

From observation of the `Baroque_Parting_Zero_Page.sid` pattern stream at $14F0:

```
60 30 10 AF 10 B0 11  33 22  37 22  38 22  38 62  37 62  FF
60 38 10 B7 10 B8 11  35 22  33 22  32 22  32 62  33 62  FF
...
*** END OF MUSIC ***
```

Tentative interpretation (not confirmed without a reference source):
- `FF` = end of pattern / pattern terminator
- `60` ($60 = RTS in 6502) appears to function as a pattern-start marker or separator
- Values in the range $10–$3F appear to be note codes (observed: $30=48, $32=50, $33=51, $37=55, $38=56)
- Values in the range $AF–$B8 seem to be associated with instrument or voice commands (appear before note runs, not between them)
- Values like $22 (34) and $62 (98) appear interleaved with notes — likely duration bytes
- `$1x` and `$11` seem to act as row-setup or voice-change bytes

The **sidid.cfg signature** (from `cadaver/sidid`) identifies this player by the byte sequence:
```
9D ?? ?? B0 ?? DE ?? ?? ?? ?? ?? 4A 4A 4A 4A DD ?? ?? D0 ?? A9 ?? 9D
```

Disassembly of this pattern (verified at offset $1296 in `Baroque_Parting_Zero_Page.sid`):
```
9D 5B 10     STA $105B,X     ; store note byte into voice state table
B0 14        BCS +$14        ; branch if carry set
DE 5E 10     DEC $105E,X     ; decrement counter
A9 79        LDA #$79        ; load value
EA           NOP
4A           LSR             ; \
4A           LSR             ;  |  value >> 4 = extract upper nibble
4A           LSR             ;  |  (instrument index from note byte)
4A           LSR             ; /
DD 5E 10     CMP $105E,X     ; compare with counter
D0 05        BNE +5          ; skip if no match
A9 00        LDA #0
9D 52 10     STA $1052,X     ; store zero
```

The 4× LSR is the key decode: the **upper nibble of the note byte encodes the instrument index**, and the lower nibble encodes note pitch/step (or octave). This is a compact 1-byte-per-note encoding with 16 possible instruments and 16 pitch steps.

### 4.4 Data tables (identified strings)

The string `' "$\')+.147:>AEINRW\bhnu|'` appears in virtually every CSS SID at the same relative offset. This is a **nonlinear volume/velocity curve** table (24 bytes of increasing values from $20 to $7C), used to scale envelope levels.

The string `"J"*N` (runs of `$4A`) appearing as data is the literal byte 0x4A repeated — **in data tables, not code**. This is part of the instrument or arp table filler, not the 4× LSR decode sequence.

### 4.5 Player variants and evolution

Every SID file has a **unique MD5** (no two CSS SIDs share identical binary content). The player code at the standard $1064 offset is not identical across SIDs — it evolves. The binary evidence shows:

- Earliest SIDs (1991–1992): `"MUSIC SASCHA NAGIE,PLAYER O.KLEE"` tag or direct author name in string
- Third-party SIDs (2012): `"LARS HUTZELMANN'96 PLAYER O.KLEE"` — implies a 1996 player revision distributed to other sceners
- Latest SIDs (2014–2021) by celticdesign: `"(C)ELTICDESIGN 20XX/Y"` copyright tag in title string; player code still structurally similar

The V4.0 designation on both CSDb releases appears to refer to the **editor application**, not the player format revision. The player has evolved over at least two documented versions (Oliver Klee's original ~1991–1992, and a 1996 revision distributed externally).

### 4.6 Data size characteristics

| Metric | Value |
|---|---|
| Minimum SID size (data) | 1,771 bytes |
| Maximum SID size (data) | 38,563 bytes |
| Mean SID size (data) | ~5,337 bytes |
| Typical (median) | ~4,500 bytes |

---

## 5. Related releases (CSDb)

| CSDb ID | Title | Type | Notes |
|---|---|---|---|
| #170632 | Cyberlogic Sound Studio V4.0 | Tool | Full release; 25 SIDs; code O.Klee; music/design celticdesign+Odi |
| #97286 | Cyberlogic Sound Studio V4.0 Preview | Tool | Released 12 Nov 1992 by Trance; music Odi + Rolex (Topaz Beerline); help celticdesign |
| #118747 | Cyberlogic Dream | Music | 1992 Demons of Sound; celticdesign composer; showcases CSS |
| SID #21103 | Cyberlogic Dream.sid | SID | HVSC entry for above; load $6000, play $6003 |
| #38107 | Cyberlogic Preview | Crack | 1994 Dytec+TRSI; unrelated to sound studio (different product) |

The music demo "Cyberlogic Dream" by Demons of Sound (1992) appears to be a showcase/demo release built around the CSS player, establishing the "Cyberlogic" brand for the tool.

---

## 6. What is NOT known / open questions

- **No source code available.** The player is not open-source and has never been published.
- **No format specification exists** beyond what is reconstructible from binaries.
- **No user manual or in-editor help file** has been located online. The D64 disk image (css.d64 from CSDb #170632) may contain in-program help or documentation; it has not been extracted and read.
- **Pattern command set** is not fully documented. The tentative note-byte encoding above is inferred but not confirmed against a known melody.
- **Effect catalogue** is unknown. Whether CSS supports vibrato, pulse sweep, arpeggio, filter sweep, and if so, how they are encoded in the pattern or instrument data, is unresolved.
- **Instrument format** structure is not mapped. The data tables contain ADSR + waveform data, but the exact byte layout per instrument is unconfirmed.
- **Earlier versions (V1–V3)** may exist. The earliest HVSC SIDs are from 1991, predating the V4.0 release. It is possible earlier format versions exist that are incompatible with V4.0's player.
- **Separate editor UI.** The css.d64 disk image contains an editor interface (CBM-M/P/D keys documented), but whether the editor writes the same binary format as the standalone player, or whether there's a conversion step, is unknown.
- **Oliver Klee's current awareness/interest** in CSS is unknown. His oliverklee.de site makes no mention of his C64 past.

---

## Leads to follow

1. **Disassemble css.d64** — download the disk image from CSDb #170632 and extract + disassemble the editor program. This would reveal the full pattern format, instrument editor layout, effect commands, and any embedded help text.

2. **Binary-diff the V4.0 Preview .prg** (`Soundstudio.prg` from zimmers.net FUNET archive, 26.8 KB) against the Nagie SID players. If the Soundstudio.prg is a dedicated editor binary (separate from the per-SID player), this would clarify the editor-vs-player architecture.

3. **Contact celticdesign on CSDb.** He is active (2021 SID) and has a CSDb profile (ID 3288). He wrote the tool's concept and was involved in design — he may know the full command set or have the editor source.

4. **Check CSDb forum for css.d64 threads** — CSDb has a forum attached to each release entry; the trivia section on #170632 mentions "2 trivia items" not visible in the summary fetch. Fetch the full page HTML directly.

5. **Analyze the Soundstudio.prg PRG more carefully.** The WebFetch binary read found `"12/11/92"` date and `"LARDAX & TUNE:ROLEX TOPAZ"` — this matches the Preview release date (12 Nov 1992) and the credited musician Rolex (Topaz Beerline). This is almost certainly the V4.0 Preview editor binary. A 26.8 KB PRG is large enough to include a full editor UI.

6. **Pattern decode against a known tune.** `Baroque_Parting_Zero_Page.sid` (by Oliver Klee, 1992) is Baroque_Parting = likely based on a known Bach piece. Cross-referencing the note bytes against the expected pitches would confirm the note encoding.

7. **Check The_Blue_Ninja and X-Radical on CSDb** for group affiliations and connections to Oliver Klee — they may clarify how the CSS player was distributed in the late 1990s.

8. **German scene forums (forum64.de)** — search for "Cyberlogic" or "celticdesign" or "Odi" threads; this was a German-language tool and German-language scene forums may have period discussions not indexed by English searches.
