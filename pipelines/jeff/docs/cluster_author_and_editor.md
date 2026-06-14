# Jeff Player — Author, Editor, and Variant Cluster

<!-- provenance -->
primary_source: https://remix64.com/interviews/interview-soren-jeff-lund.html
secondary_sources:
  - http://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=86
  - https://csdb.dk/release/?id=122334  (Music Editor V2.0)
  - https://csdb.dk/release/?id=47985   (X-SID, 2007)
  - https://csdb.dk/release/?id=17292   (One Million Lightyears / FLT, 2005)
  - https://csdb.dk/scener/?id=8059     (Jeff scener profile)
  - sidid.cfg (local copy: deprecated/gt2_pipeline/tools/sidid.cfg, lines 983–1003)
  - hvsc84.db (engine column, queried 2026-06-14)
fetched_via: WebFetch + local grep (Claude agent)
fetch_date: 2026-06-14
reliability: HIGH for biographical facts and signature data; LOW for internal format details
  (no publicly available format spec, no released editor source code)

---

## 1. Author

**Søren Lund**, handle **Jeff**, born 1974, Denmark.

Group lineage (chronological):
- Daniax (–Aug 1991)
- X-Factor (Aug 1991–Dec 1992)
- Imagination Developments (1992–1993)
- **Cyberzound Productions / CZP** (1993–May 2003) — *founder* (co-founded 1994 with Duck LaRock/CML; Mitch and Dane joined later; also Mindflow, Vip, Jadawin)
- Camelot (Dec 1992–2013)
- Crest (1999–2013)
- Bonzai (1999–2013)
- Cosine (Nov 2006–2013)
- **Viruz** (June 2003–Nov 2013) — *founder*
- Maniacs of Noise (Apr 2013–2013)

CSDb scener page: https://csdb.dk/scener/?id=8059
HVSC directory: MUSICIANS/J/Jeff/ (181 SID files in HVSC #84)
Total HVSC SIDs using Jeff engines (incl. other musicians using his player): 205

Jeff died 1 December 2013.

---

## 2. The Music Editor / Player System

### Development history

Jeff began developing his own player system in **1991** and by ~1999 had built approximately **30 different players** and **2 editors**. Neither editor was fully released officially.

### Music Editor V2.0 (CZP, 1996)

- CSDb release: https://csdb.dk/release/?id=122334
- sidid NAME: "Music Editor"
- Type: C64 tool (unreleased; circulated informally)
- Disk image: `CZP_Music-Editor_V2_0_Preview_2_9.d64` (preview 2.9)
- Bundled SID examples: Martin Walker Tribute, MSI, Raabik, Zarathus
- Jeff's own retrospective comment (2013): "Well, never really was released, but eventually things do get out from time to time. Anyway, not an editor I would recommend using."
- The player from CZP Music Editor 2 is the basis for all subsequent players.

### The new editor (development ~2002, released as X-SID 2007)

From the 2002 Remix64 interview, Jeff described a work-in-progress editor (precursor to X-SID):

**Player specs at that time (vs JCH editor v20):**
- Rastertime: max $1C rasterlines (JCH v20 can exceed $26)
- More features than JCH v20

**Effect/instrument model features described:**
- **Wavetable / frequency tables** used for multispeed sounds (he calls them "wave freq tables")
- **Glide table** — dedicated table for portamento/glide per instrument
- **Detune table** — pitch detuning per instrument
- **Vibrato table** — vibrato per instrument
- **ADSR gate manipulation table** — flexible ADSR control for echo/reverb effects, tremolo; "manipulate ADSR and gate just as wicked as you like"
- **Pulse** — spent significant time on pulse programming
- **Filter** — extensively used; can combine filter types
- **Instrument table** — described as "quite big"; separate instrument editor "far more complex than the one in the JCH editor"
- **Track/sequence editing** — modelled similarly to JCH editors ("if you find that easy, then that's good")
- **Hard restart support** — mentioned as a player feature choice ("especially if you use a player with no hardrestart")
- **Multispeed** — supported; wave freq tables are the primary vehicle
- **Multiple voices for single sound** — compositional technique, not explicit engine feature

**Interface:** Separate instrument editor; "a lot of explanation in the editor"; text editor for screen design.

### X-SID (Viruz, 2007)

- CSDb release: https://csdb.dk/release/?id=47985
- Released: 6 April 2007, under his Viruz group
- Rating: 9.4/10 (18 votes)
- Download (original): http://www.6581.dk/xsid-viruz.rar
- Description: A released public music editor — the only editor Jeff formally published.
  Users called it "the perfect switch from other editors."
- sidid detection: listed as "(X-SID)" which is a sub-detection of the main Jeff signature
  (see sidid.cfg line 987: `(X-SID)` with signature `88 10 F7 A5 ?? 48 A5 ?? 48 A2`)
- X-SID uses the same underlying player architecture as CZP Music Editor 2, further optimised.

---

## 3. sidid Signature Variants — Full Data

Source: `deprecated/gt2_pipeline/tools/sidid.cfg`, lines 983–1003.

```
Jeff
A5 ?? 48 A5 ?? 48 AND A2 ?? 20 AND A2 07 20 AND A2 ?? 20 ?? ?? 68 85 ?? 68 85 ?? 60 END
9D ?? ?? BD ?? ?? 18 7D ?? ?? 7D ?? ?? A8 B9 END
BD ?? ?? 9D 00 D4 BD ?? ?? 18 7D ?? ?? 9D 01 D4 END

(X-SID)
88 10 F7 A5 ?? 48 A5 ?? 48 A2 END

Jeff/Airwalk
C9 FF B0 0E 8D 04 D4 C8 END

Jeff/BullSID
10 D7 A9 00 85 FC A9 00 85 FB 60 A9 END

Jeff/FLT
60 A9 00 8D 02 D4 A9 08 8D 03 D4 4C END

Jeff/XLarge
60 A9 D7 8D 06 D4 A9 ?? 8D 0D D4 A9 ?? 8D 14 D4 A9 00 8D 05 D4 8D 0C D4 END

Jeff/BullSID3
A0 16 A9 00 99 00 D4 88 10 FA 8D ?? ?? A0 ?? 99 END
```

**Interpretation notes:**

- The main **Jeff** signature has 3 detection lines (any/all may be used for positive match).
  Lines 2 and 3 point to the SID-write core: `9D ?? ?? BD ?? ?? ... A8 B9` is indexed table
  read + store pattern; `BD ?? ?? 9D 00 D4 BD ?? ?? 18 7D ?? ?? 9D 01 D4` is freq-low
  computation (load base freq, add offset, store to $D400=V1 freq lo, then freq hi at $D401).
- The **(X-SID)** sub-detection is an alternate init/play entry point byte sequence; it sits
  inside the Jeff block, meaning X-SID is detected as "Jeff" first, then X-SID if this
  secondary pattern matches.
- **Jeff/FLT**: `60 A9 00 8D 02 D4 A9 08 8D 03 D4 4C` = RTS; LDA #$00; STA $D402 (V1 PW lo);
  LDA #$08; STA $D403 (V1 PW hi = $0800); JMP — this is a player init sequence that sets
  fixed pulse width on voice 1, unique to the FLT variant.
- **Jeff/XLarge**: `60 A9 D7 8D 06 D4 ...` = sets $D406 (V1 ADSR) to $D7, plus further
  direct $D4xx writes — another init variant with hardcoded ADSR/control register values.
- **Jeff/BullSID**: `10 D7 A9 00 85 FC A9 00 85 FB 60 A9` — BPL + zero-page clear pattern;
  likely init cleanup or reset code unique to this variant.
- **Jeff/BullSID3**: `A0 16 A9 00 99 00 D4 88 10 FA` = LDY #$16; LDA #$00; STA $D400,Y;
  DEY; BPL loop — clears 23 SID registers ($D400–$D415) using a Y-decrementing loop. This
  is an init/reset routine; the $16 (22 decimal) count covers all voices + filter + vol.
- **Jeff/Airwalk**: `C9 FF B0 0E 8D 04 D4 C8` = CMP #$FF; BCS +$0E; STA $D404; INY — a
  note-gate write sequence with $FF sentinel check, slightly different gate-write path.

---

## 4. Variant Taxonomy — What Each Variant Is

These are **the same player engine with group/demo-specific customisation** in the init
sequence or player dispatch, not fundamentally different music formats. Evidence:

1. sidid.nfo comment for Jeff/FLT explicitly says: "Custom player made for One Million
   Lightyears from Earth/FairLight" — a single 2005 FLT demo.
2. The FLT SID files (Deep_Shit.sid, Martin_Walker_Tribute.sid) are exactly the two tracks
   used in "One Million Lightyears from Earth" (FLT, Floppy 2005, 2nd place).
3. The XLarge SIDs (X-Large.sid, X-Large_2.sid, X-Large_4.sid) are a titled series by Jeff
   — the variant name matches the release name, suggesting a dedicated player build for those
   productions.
4. Airwalk SIDs (Cool_Fool.sid, Music_001.sid, Old_Tune.sid) are early Jeff tunes; Airwalk
   (ACC) is a German C64 group — likely Jeff made a custom player build for Airwalk
   collaborations or their releases.
5. BullSID and BullSID3 — "BullSID" is NOT a group name; it is a CSDb music release (2006,
   by Triad/dalezy). The variant name likely refers to a "BullSID" music demo/competition
   entry that used Jeff's player, or a special build Jeff made for the Danish BullSID scene
   event. Crowley_Owen/BS_Test_Tune.sid also uses Jeff/BullSID — "BS" = BullSID.

**Summary:** All Jeff/X variants are the same CZP Music Editor 2 → X-SID player lineage,
with the variant discriminator capturing per-production or per-group init/reset tweaks in
a small init or note-gate code path. The musical data format (instrument tables, wavetable,
sequence/track structure) is expected to be identical or near-identical across variants.

---

## 5. HVSC Coverage (HVSC #84)

| Engine        | Count | Notes |
|---------------|-------|-------|
| Jeff          | 192   | Main engine — all MUSICIANS/J/Jeff/ plus other musicians using his player |
| Jeff/Airwalk  | 3     | Early Jeff tunes (Cool_Fool, Music_001, Old_Tune) |
| Jeff/XLarge   | 3     | X-Large series tunes |
| Jeff/BullSID  | 3     | 2 Jeff tunes + 1 Crowley_Owen tune |
| Jeff/BullSID3 | 2     | Drax_8580_Years_Old, Touching_Cloth |
| Jeff/FLT      | 2     | Deep_Shit, Martin_Walker_Tribute (FLT demo) |
| **Total**     | **205** | |

Additionally: 1 SID classified as Power_Music in MUSICIANS/J/Jeff/ (outlier).
Jeff Minter (2 SIDs) is a completely different person (Llamasoft game dev) — ignore.

Other musicians whose SIDs use Jeff's player (selected):
- Duck_LaRock (14 SIDs) — CZP co-founder, shared player
- A-Man, DRAX, Fanta, Hermit, NecroPolo, Nilsen_Ronny, Spang_Jesper, Vincenzo (1 each)
- These likely obtained Jeff's player binary directly for their own compositions.

---

## 6. Player Architecture — Inferred from Signatures + Interview

From the byte signatures and interview statements, the following can be inferred:

**Dispatch model:** 3-voice loop with indexed register writes (pattern `BD ?? ?? 9D 00 D4`
= load from table,X; store to $D400,X). Voice iteration is likely X=0,7,14 or similar
stride.

**Frequency computation:** `BD ?? ?? 18 7D ?? ?? 9D 01 D4` = load freq base + ADC freq
offset → store to $D401. Suggests a base-note table plus per-instrument or effect offset,
consistent with Jeff's description of "wave freq tables" driving multispeed sounds.

**No hard-restart:** Jeff explicitly mentioned "especially if you use a player with no
hardrestart" as a design choice. His Drax collaboration "Beyond" deliberately used no
hard restart for a "good old c64 sound." The CZP/Jeff player likely has no hard restart
(or makes it optional per instrument).

**Sequence/track model:** JCH-similar track/sequence model. JCH uses a pattern→sequence
(orderlist) two-level structure with in-pattern commands for instrument change, tempo,
transposition etc. Jeff adopted a similar paradigm.

**Instrument table:** Large; separate from the track data. Effects (glide, detune, vibrato,
ADSR gate manipulation) stored in per-instrument sub-tables.

**ADSR manipulation table:** Can set ADSR and gate arbitrarily per tick — enables tremolo,
echo, reverb-like effects.

**Rastertime budget:** Max $1C rasterlines in the player tested circa 2002 (CZP player 2 /
precursor to X-SID). Well within the ~$1E–$20 safety margin for a single raster interrupt.

---

## 7. Timeline

| Year | Event |
|------|-------|
| 1988 | Jeff starts making music on C64 |
| 1991 | Begins developing own player system |
| ~1993 | CZP co-founded (also described as 1994 in one interview) |
| 1996 | CZP Music Editor V2.0 (preview 2.9) circulated; never officially released |
| ~1996 | sidid identifies this era as the "1996 Cyberzound Productions" player release |
| 2002 | Remix64 interview: new player/editor in progress, player done, editor delayed |
| 2003 | Moves to Viruz (co-founded) |
| 2005 | Jeff/FLT variant: tunes for Fairlight demo "One Million Lightyears from Earth" |
| 2007 | X-SID released publicly (Viruz, 6 April 2007) |
| 2013 | Jeff dies (1 December 2013) |

---

## Leads to Follow

1. **Obtain X-SID disk image.** The download link `http://www.6581.dk/xsid-viruz.rar`
   (1,695 downloads at CSDb) may still be alive. The disk image will contain: the editor
   binary, bundled example SIDs, and possibly an embedded readme or disk directory with
   feature descriptions. This is the single highest-value asset for format RE.

2. **Obtain CZP Music Editor V2.0 disk image** from CSDb #122334. The D64 file
   `CZP_Music-Editor_V2_0_Preview_2_9.d64` is available (399 downloads). Contains 4 example
   SIDs. Useful for comparing the V2 player layout vs X-SID.

3. **Run sidid on HVSC Jeff SIDs** to confirm variant assignments and find any
   mis-classified SIDs (the 2 `None`-engine SIDs in MUSICIANS/J/Jeff/).

4. **Seed disassembly from a representative Jeff SID.** Recommend `Jeff/Rectumor_8580.sid`
   (Jeff/BullSID, single subtune) or `Jeff/Touching_Cloth.sid` (Jeff/BullSID3) as
   tractable starting points for the main-variant player.

5. **Check Wayback Machine for 6581.dk.** Jeff's site (`www.6581.dk`) hosted X-SID and
   may have had a player/format description page. Try:
   `https://web.archive.org/web/*/http://www.6581.dk/`

6. **Codebase64.org / Forum64.de / Lemon64 forum search** for Jeff / X-SID posts. Jeff
   was known to post about his editor development; forum threads may contain feature lists
   or format hints not in formal interviews.

7. **Viruz group page / Jeff's Cosine page** — Jeff joined Cosine (2006) around the time
   X-SID was released. Cosine may have hosted player documentation.

8. **BullSID event context.** Research what "BullSID" was (Triad music compo? Danish scene
   event?) to confirm why Jeff/BullSID and Jeff/BullSID3 got those names. CSDb query:
   search for "BullSID" releases in 2005–2008 range.

9. **X-SID internal format.** Once the disk image is obtained: examine the data area of
   example SIDs against the player to reverse-engineer the instrument table layout, the
   sequence command byte set, and the wavetable/arp structure. Jeff's JCH-like claim makes
   JCH v20 format a useful starting reference.
