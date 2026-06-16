# MoN/Deenen Player — Web Research Findings

**Date:** 2026-06-15
**Researcher:** Claude (automated sweep)
**Scope:** Web searches + page fetches for Maniacs of Noise / Charles Deenen C64 SID player engine

---

## Summary

The MoN/Deenen player is a commercial C64 game music driver written by Charles Deenen in Turbo Assembler ("Turbo Ass"), called "Musicfile". It was used for game soundtracks from approximately 1988–1993. No public source code or official format documentation has been located. The primary technical artifact recovered is the **sidid fingerprint byte sequences** from the cadaver/sidid and WilfredC64/player-id repositories, which identify 8 distinct player variants. Secondary findings: historical/biographical context from VGMPF, Wikipedia, C64-Wiki.

---

## Search 1 — "maniacs of noise" disassembly 6502 c64 site:github.com OR site:gist.github.com

**Result:** No MoN-specific disassembly found on GitHub or Gist. General 6502 disassembly tools returned (Dis64, revenge, 6502-disassembly topic). No public MoN disassembly repo exists as of this sweep.

Top result URLs:
- https://github.com/topics/6502-disassembly?l=assembly
- https://github.com/smnjameson/Dis64
- https://github.com/christo/revenge

---

## Search 2 — "maniacs of noise" "musicfile" format c64 sid player

**Result:** Confirmed driver name "Musicfile" and that Deenen wrote it in Turbo Ass. No format specification found in search results.

Key snippet (from VGMPF page, confirmed by multiple sources):
> "Deenen programmed a music driver ('Musicfile') and a sound effects driver in Turbo Ass."

Top result URLs:
- https://vgmpf.com/Wiki/index.php/Maniacs_of_Noise
- https://www.lemon64.com/music/

---

## Search 3 — "charles deenen" c64 sid player driver source

**Result:** No public source code found. Historical context confirmed.

Key snippet (Wikipedia / VGMPF):
> "Around 1985 he wrote a C64 sound-driver... started a sound company with Jeroen Tel as Maniacs of Noise."
> "Charles Deenen made a player, and Juha Granberg (FCS) made an editor for [MoN/FutureComposer — see sidid.nfo]"

URLs:
- https://github.com/cadaver/sidid/blob/master/sidid.nfo
- https://en.wikipedia.org/wiki/Charles_Deenen
- https://www.mobygames.com/person/5435/charles-deenen/

---

## Search 4 — "mon/deenen" c64 sid player format specification

**Result:** No format specification found. General SID format docs returned (HVSC SID_file_format.txt, OverClocked ReMix).

---

## Search 5 — site:codebase64.org "maniacs of noise" OR "mon deenen"

**Result:** codebase64.org returned no results for this query. The page https://codebase64.org/doku.php?id=base:maniacs_of_noise returned empty content (page does not exist or is inaccessible).

---

## Search 6 — site:lemon64.com "maniacs of noise" player format

**Result:** No player format documentation on Lemon64. The Charles Deenen Q&A thread (viewtopic.php?t=16873) contained only interview questions about career/games, no technical content.

---

## Search 7 — "musicfile" c64 deenen instrument format pattern

**Result:** No hits with technical format details.

---

## Search 8 — "jeroen tel" c64 player driver source disassembly

**Key finding:** Reyn Ouwehand used "Jeroen Tel's version of the Maniacs of Noise sound driver." This implies Tel had his own variant of the driver after the group split, possibly distinct from Deenen's original. Source confirmed: driver came from Deenen originally.

Key snippet (VGMPF Reyn Ouwehand page):
> "Ouwehand used Jeroen Tel's version of the Maniacs of Noise sound driver."
> "The driver source came from Charles Deenen, who programmed a music driver ('Musicfile') and a sound effects driver in Turbo Ass."

URLs:
- https://www.vgmpf.com/Wiki/index.php?title=Reyn_Ouwehand
- https://vgmpf.com/Wiki/index.php/Jeroen_Tel

---

## Search 9 — "reyn ouwehand" "maniacs of noise" driver source

**Result:** Confirmed Tel's version used by Ouwehand. No source code located.

Additional snippet:
> "He got his first home computer, a Commodore 64 circa 1986, and soon became part of the system's demoscene. He began working for the group at the age of just 16, initially assisting with sound effects, with his first full job as a composer being providing the soundtrack to Last Ninja Remix."

---

## Search 10 — site:csdb.dk "maniacs of noise" player source

**CSDb Group page (https://csdb.dk/group/?id=448) — fetched:**

No source code or technical format documentation listed. 181 releases catalogued, primarily music compositions and sound effect collections from commercial C64 games (1987–2026).

Tool releases found on the CSDb group page:
- **MON SFX Editor V1.00** (1990) — tool for sound effects editing
- **MON SFX Crash Saver V1.0** — tool
- **MON SFX Relocator V1.0** — tool
- **JCH NewPlayer 21.g5** (2006) — misc
- **JCH NewPlayer 21.g4 Final** (2006) — misc
- **JCH NewPlayer 21.g4 beta** (2005) — tool

Notable CSDb releases:
- https://csdb.dk/release/?id=52173 — "The Maniacs of Noise Collection by Alive (1990)" — 20 SID files, no source
- https://csdb.dk/release/?id=169676 — "Maniacs of Noise Music Collection by Legion (1989)" — D64 disk image, no source
- https://csdb.dk/release/?id=20117 — "Afterburner Music by Maniacs of Noise (1988)"

---

## Search 11 — "MoN" "Deenen" c64 "instrument" OR "pattern" OR "effect" format

**Result:** No technical format documentation returned. General biographical hits only.

---

## Page Fetch: sidid.nfo / sidid.cfg — CRITICAL TECHNICAL FIND

**Source 1:** https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
**Source 2:** https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg

These contain the player fingerprint signatures used to identify MoN variants in HVSC SID files. The sidid.nfo entry structure:

```
PLAYER_NAME
AUTHOR: <author>
REFERENCE: <url>
COMMENT: <notes>
```

### MoN/Deenen (sidid.nfo)
```
AUTHOR: Charles Deenen
```
(No REFERENCE or COMMENT in the nfo beyond the author line as seen in the GitHub view.)

### MoN/FutureComposer (sidid.nfo)
```
AUTHOR: Charles Deenen made the player & Juha Granberg (FCS) made the editor
REFERENCE: https://csdb.dk/release/?id=10604
COMMENT: Editor made for the player of /MUSICIANS/T/Tel_Jeroen/Noisy_Pillars_tune_1.sid
```

### MoN/Bjerregaard (sidid.nfo)
```
AUTHOR: Johannes Bjerregaard
```

---

## Player Fingerprint Signatures (from sidid.cfg / player-id)

These are the hex byte sequences used by sidid/player-id to detect MoN variants in SID binary data. `??` matches any byte.

### MoN/Bjerregaard
```
A9 00 ?? ?? ?? 8D ?? D4 8D ?? D4 8D ?? ?? 60 && 29 7F 38 E9 40
(Audiomaster_V1)
0A 18 75 ?? 95 ?? B5 ?? 69 ?? 95 ?? B4 ?? AD ?? ?? B4 ?? B9 ?? ?? 29 0F A8 B9 ?? ?? 85 ?? B9
(Roland_Hermans)
AC ?? ?? 30 ?? D0 && C9 80 29 7F B0
```

### MoN/Deenen
```
C9 60 B0 03 4C ?? ?? C9 FF D0 ?? A9 00
B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ?? 5E ?? ?? 7E ?? ?? 4C
BD ?? ?? DD ?? ?? D0 ?? A9 FE 9D ?? ?? DE ?? ?? F0 ?? BD ?? ?? C9 FF F0
C9 C0 90 ?? 29 ?? 0A 0A 0A 9D ?? ?? C8 B1 ?? C9 ?? F0
C9 FF D0 0E A9 00 95 ?? B5 ?? F0 04 D6 ?? 10
C9 FF D0 17 A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10
4C ?? ?? C6 ?? A4 ?? BD ?? ?? 86 ?? 0A 0A 0A AA 8E ?? ?? BD ?? ?? 85 ?? BD ?? ?? 25 ?? 99 04 D4
99 00 D4 C8 CA 10 F9
```

### MoN/FutureComposer (sub-variants)
```
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03
8D 17 D4 A0 06 88 88 88 88 88 88 B1 F9

(FutureComposer_V1.0)
EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60

(FC_V4_Packed)
EE 99 ?? EE 9A ?? EE 9B ?? A9

(FC_V3.x)
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90 0B 29 3F 9D

(MoN/Cyb2)
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C

(MoN/TTWII)
BC ?? ?? BE ?? ?? 8E ?? ?? A5 ?? 29 0F 85 27 A5 ?? 29 70 4A 4A 4A 4A A6 ?? 95 ?? A0 BC A5 ?? 10 02 A0 7D 8C ?? ?? BC ?? ?? B9 ?? ?? 38 F9

(MoN/JTS)
A9 ?? 9D ?? ?? 9D ?? ?? 9D ?? ?? 4C ?? ?? 8D ?? ?? 29 80 F0 0E AD ?? ?? 29 1F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? 29 40 F0 0E AD ?? ?? 29 3F 9D

(MoN/RWE)
B0 05 BD ?? ?? D0 05 BD ?? ?? 29 FE 9D ?? ?? BD ?? ?? D0 0A AD ?? ?? C9 ?? D0 03 99 06 D4 BD

(MoN/Bantam)
0A 0A 0A AA 8E ?? ?? BD ?? ?? A6 FF 9D ?? ?? 99 04 D4 A9 00 99 02 D4 A6 FF 9D
```

### MoN/Deenen_Digi
```
A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D
4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4
```

### Interpretation of key fingerprint bytes (6502 opcodes decoded)

**MoN/Deenen main fingerprint line 1:**
`C9 60` = CMP #$60 (compare accumulator with $60, i.e., note value 96?)
`B0 03` = BCS +3 (branch if carry set)
`4C ?? ??` = JMP abs (indirect dispatch)
`C9 FF` = CMP #$FF (compare with $FF — end-of-pattern marker?)
`D0 ??` = BNE rel (branch if not end)
`A9 00` = LDA #$00

**Line 2:**
`B9 ?? ??` = LDA abs,Y — table-indexed load
`F9 ?? ??` = SBC abs,Y — subtract (transpose/frequency delta?)
`9D ?? ??` = STA abs,X — store indexed
`BD ?? ??` = LDA abs,X — load indexed
`4A 4A 4A 4A` = LSR×4 (right-shift 4 bits = extract high nibble)
`A8` = TAY — transfer A to Y (use as index)
`88` = DEY — decrement Y
`30 ??` = BMI rel (branch if minus)
`5E ?? ??` = LSR abs,X — logical shift right memory,X
`7E ?? ??` = ROR abs,X — rotate right memory,X

This sequence strongly suggests an instrument waveform/effect step counter mechanism with nibble-packed data.

**Line 7 (instrument/voice dispatch):**
`4C ?? ??` = JMP (loop top or voice dispatcher)
`C6 ??` = DEC zpg (decrement zero-page tempo/counter)
`A4 ??` = LDY zpg
`BD ?? ??` = LDA abs,X
`86 ??` = STX zpg (save voice index)
`0A 0A 0A` = ASL×3 (multiply by 8 — instrument table stride of 8 bytes?)
`AA` = TAX
`8E ?? ??` = STX abs
`BD ?? ??` = LDA abs,X
`85 ??` = STA zpg
`BD ?? ??` = LDA abs,X
`25 ??` = AND zpg
`99 04 D4` = STA $D404,Y — write to SID voice control register (waveform/gate)
`99 00 D4` = STA $D400,Y — write to SID voice freq low
`C8` = INY
`CA` = DEX
`10 F9` = BPL -7 (loop — 3 voices × 2 SID writes each?)

**MoN/Deenen_Digi fingerprint decoded:**
`A2 00` = LDX #$00
`F0 ??` = BEQ rel (branch if zero — skip when no digi?)
`98` = TYA
`0A` = ASL (×2 table stride)
`A8` = TAY
`B9 ?? ??` = LDA abs,Y (load digi sample byte from table)
`8D ?? ??` = STA abs (store to ... likely $D418 master volume for digi)
`B9 ?? ??` = LDA abs,Y
`8D` = STA abs
then: `4A 4A 4A` = LSR×3 (extract bits 3..0 after shifting? or extract 4-bit digi sample)
`B8` = CLV
`50 ??` = BVC rel (always-branch, like BRA)
`4A 4A 4A` = LSR×3 again
`18` = CLC
`69 ??` = ADC #imm (add constant — period/timing calc)
`8D 18 D4` = STA $D418 — write master volume (4-bit digi output!)

This is a classic 4-bit digi output via $D418 (master volume register). Two nibbles per byte, 3 LSRs to extract upper nibble then 3 LSRs for lower nibble with ADC offset.

---

## Historical / Biographical Context

### From Wikipedia (Charles Deenen)
> "Around 1985 he wrote a C64 sound-driver... In 1987, Deenen, Jeroen Tel, and others started the sound and music group Maniacs of Noise."
> "Initially he was a programmer for the group, while Tel was the composer, but after their first few games he began working on music as well."

### From VGMPF (Maniacs of Noise)
> "Deenen programmed a music driver ('Musicfile') and a sound effects driver in Turbo Ass."
> "Deenen, Donné, Tel and Ouwehand arranged by typing hexadecimal numbers and labels into the driver's source code." (i.e., NO tracker GUI — pure hex entry)
> "Deenen's C64 music driver was officially converted to the 128K [ZX Spectrum]."

### From VGMPF (Reyn Ouwehand)
> "Ouwehand used Jeroen Tel's version of the Maniacs of Noise sound driver."
> "The driver source came from Charles Deenen, who programmed a music driver ('Musicfile') and a sound effects driver in Turbo Ass."

### From sidid.nfo (MoN/FutureComposer entry)
> "AUTHOR: Charles Deenen made the player & Juha Granberg (FCS) made the editor"
> "REFERENCE: https://csdb.dk/release/?id=10604"
> "COMMENT: Editor made for the player of /MUSICIANS/T/Tel_Jeroen/Noisy_Pillars_tune_1.sid"

This means a third-party editor (by FCS/Juha Granberg) was built for the MoN player, released on CSDb. The reference SID is Jeroen Tel's Noisy Pillars tune 1.

### From C64-Wiki (Maniacs of Noise)
> "Deenen 'created a music driver for Donné and Tel' after seeing Tel arrange music quickly using Soundmonitor."

This implies the driver was created as an improvement over/alternative to Soundmonitor (Rob Hubbard's / Martin Galway's tool).

### From CSDb group page tool releases
- **MON SFX Editor V1.00 (1990)** — a dedicated SFX editor for the MoN sound effects driver
- **MON SFX Relocator V1.0** — suggests the SFX driver could be relocated in memory
- **MON SFX Crash Saver V1.0** — recovery tool for the SFX editor

### Archive.org (Cybernoid_Music_1988_Maniacs_Of_Noise)
The D64 disk image contains: `"cybernoid 1 /mon" prg` — the `/mon` suffix in the PRG filename on the disk is the player's in-band identifier. Credits: Charles Deenen (code) and Jeroen Tel (music).

---

## Player Variant Naming Analysis

From sidid.cfg sub-variant names under MoN/FutureComposer:

| Variant | Likely meaning |
|---------|---------------|
| `MoN/Cyb2` | Cybernoid 2 (Jeroen Tel, 1988) |
| `MoN/TTWII` | That's The Way It Is (Jeroen Tel) |
| `MoN/JTS` | Jeroen Tel's variant/version |
| `MoN/RWE` | Reyn Ouwehand (RWE = Reyn Wijnand Edward Ouwehand?) |
| `MoN/Bantam` | Unknown — possibly a game or label name |

The FutureComposer-family entry in sidid encompasses both the original FC engine (which appears to share player code with MoN) AND game-specific MoN variants, suggesting Deenen's "Musicfile" had significant code overlap with or derivation from Future Composer.

---

## Key Technical Inferences from Fingerprints

1. **Pattern terminator:** `C9 FF` (CMP #$FF) used as end-of-pattern/sequence sentinel value $FF — very common C64 convention.

2. **Note range check:** `C9 60 B0 03` — CMP #$60, BCS = if note >= $60 handle specially (possibly $60-$BF = effect range, $FF = end, < $60 = note value). Or $60 could be a hard-restart threshold.

3. **Nibble-extracted instrument table index:** `4A 4A 4A 4A A8` — 4× LSR then TAY. This extracts the high nibble of a byte as an index. Instrument numbers 0–15 packed in high nibble.

4. **Voice iteration loop:** The `99 00 D4` / `99 04 D4` pattern with INY/CA/BPL suggests 3-voice iteration writing freq-lo ($D400,Y) and control ($D404,Y) to SID.

5. **8-byte instrument stride** (inferred): `0A 0A 0A` = ASL×3 = ×8. Instrument table likely has 8 bytes per instrument.

6. **Digi output via $D418:** `8D 18 D4` — classic 4-bit digi via master volume writes. Two nibbles per byte accessed via separate 3×LSR paths.

7. **Frequency calculation:** `B9 ?? ?? F9 ?? ??` = LDA table,Y then SBC table,Y — suggests frequency computed as difference between two table lookups (possibly base freq − transpose or note freq − detune).

8. **Counter/tempo mechanism:** `C6 ??` = DEC zpg — decrement zero-page counter for tempo. `4C ?? ??` (JMP) is the main play-loop top.

---

## Negative Findings

- **codebase64.org/doku.php?id=base:maniacs_of_noise** — page does not exist (empty response)
- **codebase64.org/doku.php?id=magazines:chacking** — not fetched (access returned no MoN content)
- **No public disassembly** of the MoN/Deenen player has been located on GitHub, CSDb, or any forum
- **No format specification document** exists in the public web
- **No source code** release by Deenen or Tel
- **CSDb release/?id=10604** (the FCS editor reference) returned HTTP 503 — could not fetch; this is the highest-priority manual follow-up
- **justsolve.archiveteam.org/wiki/Maniacs_of_Noise** — ECONNREFUSED; site appears down

---

## Leads to Follow

### High Priority
1. **CSDb release #10604** — the FCS/Juha Granberg editor for the MoN player (referenced in sidid.nfo). This is the most likely source of format documentation or even source code. URL: https://csdb.dk/release/?id=10604 — retry when CSDb is accessible.

2. **HVSC STIL.txt** — may have per-SID notes for MoN tunes mentioning technical quirks. Check: `grep -A5 -B2 "Deenen\|MoN\|Maniacs" hvsc84/DOCUMENTS/STIL.txt`

3. **sidid.nfo full text** — the GitHub viewer only shows excerpts. The raw file has 1791 lines; MoN entries (with full COMMENT fields) are beyond the visible portion. The sidid.cfg raw gives fingerprints but not the nfo COMMENT fields. Fetch: `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo` — re-fetch requesting specifically lines 800–1791.

4. **Noisy_Pillars_tune_1.sid** — the reference SID for the MoN/FutureComposer variant. Already in HVSC at `/MUSICIANS/T/Tel_Jeroen/Noisy_Pillars_tune_1.sid`. Disassemble it: `tools/seed_disassembly.py hvsc84/MUSICIANS/T/Tel_Jeroen/Noisy_Pillars_tune_1.sid` to get the engine code.

5. **Deenen MoN SIDs in HVSC** — disassemble one representative game SID (e.g., Cybernoid, Mr. Heli, Zamzara, Double Dragon) with `tools/seed_disassembly.py` to recover the actual player code. The fingerprint sequences above are the known entry points.

6. **Jeroen Tel's Q&A or forum posts** — Tel has been active in the scene and may have described the format. Search specifically on CSDb forums or the Lemon64 thread from Tel himself.

### Medium Priority
7. **MON SFX Editor V1.00 (CSDb)** — the SFX editor binary may reveal the SFX data format (offsets, effect byte meanings). Could extrapolate instrument format from SFX format.

8. **MoN ZX Spectrum 128K port** — if the driver was "officially converted to 128K," the Spectrum version's source may be more accessible. The Spectrum demoscene is smaller and more likely to have open-sourced such things.

9. **Frederic Hahn** — the sidid entry "MoN/FutureComposer" credits Juha Granberg (FCS) for the editor. The "MON format" on Amiga (mentioned in VGMPF) was created by "Frederic Hahn." These are distinct formats (Amiga vs C64) but Hahn may have documented the C64 driver.

10. **Modland** — `https://modland.ziphoid.com/pub/modules/Maniacs%20Of%20Noise/Reyn%20Ouwehand/` has Reyn Ouwehand's module files. If these include MON-format music (not Amiga MOD), the binary layout could be reverse-engineered.

11. **LMMS GitHub issue #1722** — "C64 SID music import" issue may contain discussion of MoN format internals.

### Low Priority
12. **Deli News 5 (ExoticA)** — mentioned in search results alongside MoN content; may have a technical interview or format note.
13. **"The Burrow" C64 page (theburrow.zzap64.co.uk)** — appeared in searches near MoN content.
14. **justsolve.archiveteam.org/wiki/Maniacs_of_Noise** — currently down (ECONNREFUSED); retry later for any file format registration.

---

## Source URLs

- https://vgmpf.com/Wiki/index.php/Maniacs_of_Noise
- https://vgmpf.com/Wiki/index.php/Charles_Deenen
- https://www.vgmpf.com/Wiki/index.php?title=Reyn_Ouwehand
- https://en.wikipedia.org/wiki/Charles_Deenen
- https://www.c64-wiki.com/wiki/Maniacs_of_Noise
- https://csdb.dk/group/?id=448
- https://csdb.dk/release/?id=52173
- https://csdb.dk/release/?id=169676
- https://csdb.dk/release/?id=10604 (CSDb — FCS editor for MoN player; currently 503)
- https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg
- https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
- https://github.com/cadaver/sidid
- https://github.com/WilfredC64/player-id
- https://archive.org/details/Cybernoid_Music_1988_Maniacs_Of_Noise
- https://deepsid.chordian.net/?file=%2FMUSICIANS%2FT%2FTel_Jeroen%2FNoisy_Pillars_tune_1.sid
