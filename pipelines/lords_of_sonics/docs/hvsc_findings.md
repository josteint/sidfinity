---
source_url: local: /home/jtr/sidfinity/hvsc85/ + online (remix64.com, csdb.dk, vgmpf.com, github.com/cadaver/sidid)
fetched_via: local read + direct
fetch_date: 2026-06-16
author: Jostein Trondal (aggregated from multiple primary sources)
content_date: 2026-06-16
reliability: primary (local HVSC) + secondary (online)
---

# LordsOfSonics/MS — HVSC Research Findings

## 1. Group Bio (from HVSC STIL.txt, Musicians.txt, VGMPF, CSDb, Remix64)

**Lords of Sonics (LOS)** is a German C64 music group founded 1988 by **Markus Schneider** and **Jens Blidon**, both from Cologne. They met at the Hermann-Billung-Gymnasium. Blidon was composing with Soundmonitor; Schneider spent ~2 months in 1988 writing "a better player" for him. When classmates heard their music they scored their first commercial game (_Platou_, 1988, Kingsoft). Blidon left for military service in 1989, ending the Lords of Sonics collaboration; Schneider joined **X-Ample Architectures** (March 1989) and merged his driver with theirs over 7 weeks → became **Compotech**.

**Markus Schneider** handles: **Synth-Man** (1987–88), **Diflex** (1988–?), then own name. Also credited as "SMC" on Parsec Music Editor docs. CSDb: https://csdb.dk/scener/?id=6003

**Jens Blidon** — Musician, GERMANY. Ex-member Lords of Sonics (1988→). CSDb: https://csdb.dk/scener/?id=2205

STIL.txt (Schneider_Markus section bio):
> "Markus Schneider composed under the alias 'Diflex' in his early years and then later under his own name. In addition, he also composed under the name 'Lords of Sonics', which was a music team consisting of Schneider and Jens Blidon."

STIL.txt (Stoeten_Johann section):
> "Sadly, Johann H. Stoeten (Ultimax) passed away on December 1st, 2021."

SMC (Sanke Michael Choe) — separate person. STIL.txt for /MUSICIANS/S/SMC/:
> "SMC is short for Sanke Michael Choe."
(The SMC disambiguation in the player name "LordsOfSonics/MS" — "MS" = Markus Schneider, not Sanke Michael Choe.)

---

## 2. Editor / Player Lineage

Three related editors/players in chronological order:

| Name | Year | Authors | Notes |
|---|---|---|---|
| MS sound driver (unnamed) | 1988 | Markus Schneider | First driver; written for Jens Blidon as Soundmonitor replacement |
| **The Parsec Music Editor v5.1** | 1989 | Markus Schneider (MS/Diflex), Nic, ADT; bug-fix/docs: SMC (Pretzel Logic); music: Jeroen Tel | Released by Mnemonic Designs. CSDb #10744 + #169438. Version already at 5.1 at public release → prior versions existed. |
| **Compotech v2.1** | 1990 (v1), 1995 (v2.1) | Markus Schneider, Helge Kozielek (+ Chap Bizarre, Joachim Fräder in v2.1) | Released by X-Ample Architectures. "Compotech Editor from X-Ample & Lords of Sonic." CSDb #122614. |

The Remix64 interview quotes Schneider: "the last soundplayer based on my old player. Helge Kozielek and Mario van Zeist did some corrections to optimise the speed." — indicates Compotech/X-Ample is a further optimized descendant of the original LordsOfSonics MS player.

Sources:
- Remix64 interview: https://remix64.com/interviews/interview-markus-schneider.html
- VGMPF: https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider
- CSDb Parsec: https://csdb.dk/release/?id=10744
- CSDb Compotech: https://csdb.dk/release/?id=122614

---

## 3. sidid.cfg Identification Signature (from cadaver/sidid on GitHub)

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
Reliability: primary (tool used by HVSC classifier sidid to assign `engine` values).

```
LordsOfSonics/MS
79 ?? ?? 48 D0 06 A4 ?? C0 04 90 02 END
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4 END
(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06 END
```

- Two primary signatures (byte sequences) match the main LordsOfSonics/MS engine.
- A sub-variant labeled **(Parsec)** has its own additional signature — this corresponds to tunes built with The Parsec Music Editor (typically the Parsec-init stub).
- The `??` wildcards allow for relocation; the `END` terminates each pattern.
- The first signature (`79 ?? ?? 48 D0 06 ...`) is likely in the play routine (uses ADC/indexed addressing).
- The second signature (`AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ...`) looks like the voice-loop / channel-update section.
- The Parsec sub-variant (`9D ?? ?? 9D ?? ?? ... A2 18 A9 00 9D 00 D4 CA 10 FA 60 ...`) is a **clear-all-SID-regs** init stub: `LDX #$18` + `STA $D400,X` loop + `DEX / BPL` + `LDA #$0F / STA $D418` + `LDX #2 / STX ... CE ...` — a standard reset sequence.

---

## 4. PSID Header Survey — All 123 SIDs

All 123 entries have `load=0x0000` in the PSID header, meaning the actual load address is embedded as the first 2 bytes of the payload (little-endian). All are PSID v2.

### 4a. Composer distribution (by PSID `author` field)

| Author | SIDs |
|---|---|
| Jens Blidon | 32 |
| Kagan Demir (Babyface) | 17 |
| Markus Schneider | 13 |
| Steven Diemer (A-Man) | 8 |
| Jesper Spang | 7 |
| Stefan Toftevall (Ice) | 6 |
| Mc Olly | 6 |
| Markus Schneider & Jens Blidon | 5 |
| `<?>` | 5 |
| Sanke Michael Choe (SMC) | 4 |
| Markus Schneider (Diflex) | 4 |
| Others (12 individuals/combos) | 16 |

Active years: 1988–1994 (peak: 1989 with 48 SIDs, 1991 with 39 SIDs).

### 4b. Dispatch-table variant clusters

The 2-byte embedded load address is followed immediately by the dispatch table. Five major patterns identified:

| Variant | Count | Structure at payload+2 | PSID play | PSID init |
|---|---|---|---|---|
| **V_PLAY_INIT** (standard) | 87 | `4C jmp_play_lo jmp_play_hi 4C jmp_init_lo jmp_init_hi` | base+0 | base+3 |
| **V_NOP3_INIT_PLAY** | 9 | `EA EA EA 4C jmp_init 4C jmp_play` | base+6 | base+0 |
| **V_INIT_PLAY** | 11 | `4C jmp_init 4C jmp_play` (data starts at base+3 typically) | base+3 | base+0 or base+3 |
| **V_JMP_JMP_UNKNOWN** | 5 | Two JMPs but non-standard offsets | varies | varies |
| **Custom/game/special** | 11 | No consistent dispatch stub | varies | varies |

**V_PLAY_INIT** (87/123) is the canonical form: `[lo, hi, JMP $xxxx, JMP $yyyy, ...]` where the first JMP is the play entry and the second is the init entry. Init address = play address + 3 in the PSID header.

**V_NOP3_INIT_PLAY** (9 SIDs) — A-Man's tunes + 2 others: three NOPs at base, then JMP init, JMP play; PSID reports init=base (NOP path), play=base+6.

**V_INIT_PLAY** (11 SIDs) — Ice (Stefan Toftevall) and a few others: data starts at base+3 (embedded load = base+3), first JMP is init, second JMP is play; or reversed order of PSID fields.

### 4c. Header bytes 8–15 (after the two dispatch JMPs)

For the standard cluster, bytes at payload offset 8 onwards contain engine header fields:

```
Slot_Mashine (standard): 01 00 00 00 00 03 FF 27  (songs=1 at offset 8)
Blidon/Babylon (3-song): 01 00 00 00 05 0F FF 57
Platou (8-song):         01 00 00 00 0E 0F FF 37
A-Man variants skip this structure (payload offset 8 = 00 00 for most)
Babyface:                01 00 00 00 00 00 FF D7 ...
```

Byte at payload+8 consistently = `01` for single-song standard tunes, and seems to be a "max song index" or "song count" field. Bytes 9-10 appear to be `00 00`. Byte 11 may be a tempo/speed parameter (varies: `00`, `03`, `08`, `0E`, `0F`). Bytes 12-13 are often `FF xx` suggesting a countdown or default note length. **This header region is load-bearing for understanding the data format.**

### 4d. PSID `speed` field

All examined tunes have `speed = 0x00000000` (VBlank timing, 50 Hz PAL) EXCEPT:
- `Magic_Events.sid`: speed = `0x00385468` (some CIA-timed subtunes)
- Arcade_Pilot, Mean_Car, etc. (game tunes): speed fields contain embedded text bytes (PSID ripped from original, speed not correctly set)

### 4e. Load address distribution (embedded, after de-referencing PSID load=0)

Most common embedded load addresses:
- `0x1000` / `0x1003` / `0x1006`: 46 SIDs (dominant — $1000 page)
- `0x3000` / `0x3003`: 27 SIDs ($3000 page — Mc Olly, Spang, Sphere_Success, Stoeten)
- `0xC000` / `0xC003`: 10 SIDs (Blidon A_Song_for_You series)
- `0x1800` / `0x1803`: 11 SIDs (Blidon Magic_Writer series + others)
- Others: many single-SID load addresses (game tunes, Blidon multi-song compilations)

The Babyface tunes almost exclusively load at `0x1000`; the Spang/SMC/Sphere_Success/Stoeten/Mc_Olly cluster loads at `0x3000`; Blidon's early LoS releases load at various higher addresses.

---

## 5. Notable Individual SIDs / Technical Observations

| SID | Notes |
|---|---|
| `Schneider_Markus/No_Mercy.sid` | 13 subtunes; play=`0x0000` (PSID player-defined play); init=`0x8C4A`; this is a complex multi-song engine, not the standard dispatch stub |
| `Schneider_Markus/Timezone.sid` | 13 subtunes; load=`0x3000`, but init=`0x3B97`, play=`0x3BF2` — NOT the standard +3/+0 pattern. Multi-voice complex arrangement. Speed=`0x00005469` (some CIA). |
| `Schneider_Markus/Magic_Events.sid` | 6 subtunes, speed=`0x00385468` indicating mixed CIA/VBlank |
| `Blidon_Jens/Tulsadom.sid` | 1987 East Agents; load=`0x9FF8`, play=`0x0000` — very early, pre-LoS, possibly Soundmonitor engine? (HVSC classified as LordsOfSonics/MS) |
| `SMC/Phaedra.sid` | 4 subtunes; init=`0x0FBD`, play=`0x0FBA` (play < init — inverted); load=`0x0FBA`; Parsec sub-variant per sidid.cfg |
| `Doussis_Stello/Blax.sid` | 14 subtunes (largest); init=`0x5C80`, play=`0x5C83`; non-standard |
| `Schneider_Markus/Rhenus_Demo.sid` | 1988; init=`0xE0AB`, play=`0xE0CF`; custom layout |
| `DEMOS/UNKNOWN/Slot_Mashine_tune_1.sid` | STIL: "Covers No_Mercy, Tune #13 (0:17-0:47)" — verbatim segment, useful for engine cross-referencing |

---

## 6. STIL Excerpts (Selected)

From `/MUSICIANS/S/Schneider_Markus/` section header:
> "Markus Schneider composed under the alias 'Diflex' in his early years and then later under his own name. In addition, he also composed under the name 'Lords of Sonics', which was a music team consisting of Schneider and Jens Blidon."

From `/MUSICIANS/S/Schneider_Markus/Crystal_Fever.sid`:
> "The drums, inspired from a jazz lp, used my new sound player for the first time." (MS)

From `/MUSICIANS/S/Schneider_Markus/Django.sid`:
> "These tunes are junk, but those people at CP Verlag loved them." (MS)

From `/MUSICIANS/S/Schneider_Markus/Declem.sid`:
> "I had only 5 hours time to complete this music — so it sounds!" (MS)

From `/MUSICIANS/B/Blidon_Jens/Birthday.sid`:
> "Also used as the intro tune for Magic Disk 64 between 08/89 and 05/91."

From `/MUSICIANS/B/Blidon_Jens/Counter_Force.sid`:
> "All tunes are almost like those in /MUSICIANS/B/Blidon_Jens/Metal_Force.sid"

SMC section header comment: "SMC is short for Sanke Michael Choe."

Stoeten section header: "Sadly, Johann H. Stoeten (Ultimax) passed away on December 1st, 2021."

---

## 7. Musicians.txt Entries

```
A-Man (Diemer, Steven) - GERMANY
Babyface (Demir, Kagan {Mr. Venus}) / Chaos / Clique - TURKEY
Blidon, Jens / Lords of Sonics - GERMANY
Ice (Toftevall, Stefan) / Exact - SWEDEN
```
(Markus Schneider not found in Musicians.txt — likely uses "Diflex" or "Schneider_Markus" as filing name and may not meet the 3+ SID threshold under the same handle, OR is listed under Schneider. The file only shows the fragment containing Blidon at line 236.)

---

## 8. Online Source Digest

### Remix64 Interview (https://remix64.com/interviews/interview-markus-schneider.html)
- Schneider wrote the original player in 1988 in ~2 months as a Soundmonitor replacement.
- "I promised him [Blidon] I'd write a better player." — Blidon taught Schneider about composing.
- Crystal_Fever was the FIRST tune to use his "new sound player."
- Helge Kozielek + Mario van Zeist later "did some corrections to optimise the speed" → Compotech.
- By 1989, Schneider had joined X-Ample Architectures.

### VGMPF (https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider)
- **Parsec Music Editor** (1989): described as "a better sound driver" for Blidon. Evolved into The Parsec Music Editor and then Compotech.
- Game credits 1988–1992 all C64 (see above); Amiga work started 1990.
- ROM's Fix used for sound effects in Timezone (C64).

### CSDb Lords of Sonics group (https://csdb.dk/group/?id=757)
- Founded 1988 by Markus Schneider.
- 7 releases listed: The Music of Platou (1988), Beyond the Zero (1988), Babylon Five (1988), No Mercy Title (1989), No Mercy Music (1989), Double Density (1989), Demo Musics (1989).
- Both Schneider and Blidon listed as "ex-member (1988→)".

### CSDb Parsec Music Editor V5.1 (https://csdb.dk/release/?id=10744)
- Released by Mnemonic Designs, 1989.
- Credits: Code by ADT, Markus Schneider (Lords of Sonics / X-Ample Architectures), Nic.
- Bug-fix + documentation: SMC (Pretzel Logic). Music: Jeroen Tel ("Tomcat").
- Note: "this represents the original release of the Parsec 5.1 editor with intro."
- A version without intro was distributed on the Ruthless Music Disk.
- Also a 1991 crack by Raiders of the Lost Empire (CSDb #169438); comment: "Differs from this" → multiple versions exist.
- Also CSDb #223413: "Parsec 10 V0.1 by PDB (1991)" — a separate unrelated tool with the same name.

### CSDb Compotech V2.1 (https://csdb.dk/release/?id=122614)
- Released August 1995 by X-Ample Architectures (also titled "Comptech V2.1").
- Code: Chap Bizarre, Joachim Fräder, **Markus Schneider** (Lords of Sonics).
- 451 downloads. .d64 format.

---

## 9. PSID Header Full Table (Selected Representatives)

| PATH | VER | LOAD | INIT | PLAY | SNG | SPD | AUTHOR |
|---|---|---|---|---|---|---|---|
| Blidon_Jens/Its_Magic_end | 2 | 0x3003→$3000 | 0x3003 | 0x3000 | 1 | 0 | Jens Blidon (1988 LoS) |
| Blidon_Jens/Babylon | 2 | 0x8003→$8000 | 0x8003 | 0x8000 | 3 | 0 | Blidon & Schneider (1988) |
| Blidon_Jens/American_Express | 2 | 0x3003→$3000 | 0x3003 | 0x3000 | 6 | 0 | Jens Blidon (1989) |
| Blidon_Jens/A_Song_for_You_* | 2 | 0xc003→$c000 | 0xc003 | 0xc000 | 1 | 0 | Jens Blidon (1989, 9 SIDs) |
| Blidon_Jens/Magic_Writer_* | 2 | 0x1803→$1800 | 0x1803 | 0x1800 | 1 | 0 | Jens Blidon (1989, 9 SIDs) |
| Schneider/Platou | 2 | 0xe003→$e000 | 0xe003 | 0xe000 | 8 | 0 | Schneider & Blidon (1988) |
| Schneider/No_Mercy | 2 | 0x8c4a | 0x8c4a | 0x0000 | 13 | 0 | Schneider (atypical) |
| Schneider/Timezone | 2 | 0x3b97 | 0x3b97 | 0x3bf2 | 13 | mixed | Schneider & Blidon (1989) |
| Babyface/Babes_Boogie | 2 | 0x1003→$1000 | 0x1003 | 0x1000 | 1 | 0 | Babyface (1991) |
| Ice/Music_No_1 | 2 | 0x1003→$1003 | 0x1003 | 0x1006 | 1 | 0 | Stefan Toftevall (1991) |
| A-Man/Harmonic_River | 2 | 0x1000→$1000 | 0x1000 | 0x1006 | 1 | 0 | Steven Diemer (1989) |
| Spang/Anuddah_One | 2 | 0x3003→$3000 | 0x3003 | 0x3000 | 1 | 0 | Jesper Spang (1991) |
| SMC/Phaedra | 2 | 0x0fbd→$0fba | 0x0fbd | 0x0fba | 4 | 0 | S.M.Choe (Parsec variant) |
| Mc_Olly/Look_preview | 2 | 0x3003→$3000 | 0x3003 | 0x3000 | 1 | 0 | Mc Olly (1991) |

---

## 10. Leads to Follow

1. **Disassemble the canonical player** — pick a simple 1-subtune Blidon tune from 1989 with standard V_PLAY_INIT layout (`It's_Magic_end.sid` or `Its_a_Sin.sid`, load=$3000/play=$3000/init=$3003). The play routine is at the JMP target from offset+2. Disassemble from `play_routine_addr` to understand: voice loop structure, envelope handling, pattern/orderlist layout, frequency tables. These 2 JMPs are pure engine entry points; the data block starts at ~payload+8.

2. **Header bytes 8–15** — these appear to be an engine header. Byte 8 = likely song-count or "max voice"; bytes 9–10 unknown; byte 11 = tempo-related (`0F` common = 15?); bytes 12–13 often `FF xx` — could be initial note-length/counter. Verify by correlating with player disassembly.

3. **Parsec-variant SIDs** — `SMC/Phaedra.sid` (4 subtunes) and others identified by sidid as `(Parsec)` sub-variant deserve separate treatment. The Parsec variant signature has a SID-clear init stub differing from the base player init. Check `SMC/Royal_Scam_intro.sid` and `SMC/Deuntje.sid` for comparison.

4. **A-Man variant** (V_NOP3_INIT_PLAY) — 9 SIDs, ~1989–1990. Three NOPs before the init entry instead of a direct JMP. Could indicate an older engine version or a wrapper. Check `Harmonic_River.sid` (1989, Tropic, Steven Diemer A-Man).

5. **Timezone / No_Mercy multi-subtune engine** — these are structurally different from the single-tune standard engine. Timezone has 13 subtunes and no standard dispatch stub (init=`$3B97`, play=`$3BF2`). Likely a different player mode with a subtune-selection mechanism embedded in the init. Worth treating as a separate sub-engine.

6. **Compotech vs Parsec compatibility** — Compotech is described as a speed-optimized descendant. Question: do Compotech-composed SIDs end up classified as `LordsOfSonics/MS` or under a different sidid entry? Check Schneider's 1990+ game SIDs (Dick_Tracy, Crown, Rolling_Ronny) against sidid output.

7. **CSDb Blidon releases 1988–1989** — search CSDb for specific 1988 Lords of Sonics releases to find any surviving .d64 disk images with the editor binary. The editor binary would be the ground truth for format spec. URL: https://csdb.dk/scener/?id=2205 → filter to 1988–1989 releases.

8. **Parsec Music Editor binary** — CSDb #10744 has a .d64 download (Mnemonic Designs, 1989). This contains the editor + player source/binary. Acquiring and disassembling the player routine from the editor binary is the highest-ROI path to a complete format spec without needing to RE production SIDs.

9. **Speed field anomalies** — `Magic_Events.sid` has speed=`0x00385468`; Timezone has `0x00005469`. These contain ASCII text bytes (`Ti`, `Sh`) suggesting the PSID rip had the speed field filled from nearby data. Verify whether these are actually CIA-timed or whether the speed field is corrupted.

10. **`No_Mercy.sid` play=`0x0000`** — PSID play address of zero means the SID uses a built-in IRQ rather than the PSID driver calling play. The STIL notes it has 13 subtunes. This is an outlier engine variant worth inspecting separately.
