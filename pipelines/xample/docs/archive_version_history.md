# X-Ample / Compotech — Version & Editor-Family History

```
provenance:
  fetch_date: 2026-06-13
  sources:
    - url: https://remix64.com/interviews/interview-markus-schneider.html
      fetched_via: direct
      content_date: ~2005
      reliability: high (primary source)
    - url: http://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=173
      fetched_via: direct
      content_date: 2001
      reliability: high (primary source)
    - url: https://csdb.dk/release/?id=10744
      fetched_via: direct
      content_date: live
      reliability: high
    - url: https://csdb.dk/release/?id=122614
      fetched_via: direct
      content_date: live
      reliability: high
    - url: https://csdb.dk/release/?id=82320
      fetched_via: direct
      content_date: live
      reliability: high
    - url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
      fetched_via: direct (downloaded to tmp/xample_research/sidid.cfg)
      content_date: 2020s (maintained)
      reliability: high (authoritative SID engine fingerprints)
    - path: /home/jtr/sidfinity/tmp/xample_research/player_routine.txt
      fetched_via: disk image extraction
      content_date: 1992 (Compotech V1 D64)
      reliability: high (primary source — annotated player source with German comments)
    - path: /home/jtr/sidfinity/tmp/xample_research/comptech_2.1_docs.txt
      fetched_via: disk image extraction
      content_date: 1995 (Compotech V2.1 D64)
      reliability: high (primary source — editor commands visible)
    - path: /home/jtr/sidfinity/tmp/xample_research/compotech_1992_main.txt
      fetched_via: disk image extraction
      content_date: 1992 (Compotech V1 D64)
      reliability: high (primary source — binary content)
```

---

## Evolution Timeline

### Stage 0: Markus Schneider's Driver (1988)

Markus Schneider met Jens Blidon at school in 1987–1988. Blidon was composing on Chris Hülsbeck's SoundMonitor. Schneider spent approximately **2 months** writing Blidon "a better sound driver" — a custom 6502 player routine that formed the root of all future X-Ample music technology.

This early driver supported the core effects: glide (portamento), vibrato, drum tables, arpeggio. The driver was written and refined entirely natively on C64 (TurboAss assembler, as visible in the player_routine.txt source header).

### Stage 1: The Parsec Music Editor (1989)

**CSDb:** https://csdb.dk/release/?id=10744  
**Released by:** Mnemonic Designs  
**Version documented:** V5.1  
**Credits:** Code: Markus Schneider (Lords of Sonics / X-Ample Architectures), Nic, ADT; Bug-Fix & Documentation: SMC (Pretzel Logic); Music: Jeroen Tel (Maniacs of Noise, included demo tune "Tomcat"); Graphics: Kee  
**Distribution format:** D64 disk image and T64 tape image

The Parsec Music Editor was the first public release of Schneider's driver bundled with an editor UI. Key fact: Schneider took approximately **2 months** writing the original driver for Blidon, then the editor evolved through multiple versions (V5.1 implies at least 5 major iterations by 1989). Released through Mnemonic Designs (a separate group — not X-Ample).

The name "Parsec" derives from the X-Ample game *Parsec* (1993), but the editor predates the game by 4 years — the game was named after the editor, not the reverse.

**Relationship to Compotech:** Parsec Music Editor is the direct predecessor. Same Schneider driver; different editor surface/shell. SIDId classifies Parsec-engine SIDs under `LordsOfSonics/MS (Parsec)` — a separate fingerprint from the later Compotech family.

### Stage 2: X-Ample Sound Player Version 3.2 (1989–1992)

**Primary source:** `player_routine.txt` extracted from Compotech 1992 D64  
**Authors:** Markus Schneider + Helge Kozielek (as stated in the source header)  
**Assembler:** TurboAss (Turbo Assembler)

The player_routine.txt file (from the 1992 Compotech disk) preserves the fully documented player source with extensive German-language inline comments. This reveals the complete engine architecture:

#### Player Header Comment (translated from German)

```
X-AMPLE ARCHITECTURES SOUND PLAYER
VERSION 3.2
PROGRAMMED BY: MARKUS SCHNEIDER & HELGE KOZIELEK
ORIGINAL TURBOASS-FILE / DOCUMENTED
MUSIK-ROUTINE + SFX-ROUTINE
```

#### Architecture (from source comments)

**Main entry point:**
- Must be called once per frame (VBI / raster interrupt)
- Controls all three SID voices (music + SFX)
- SFX and music voices independently managed

**Voice layout:**
- Voice state variables are stored in **7-byte blocks** (one block per SID voice: matches SID's $D400/$D407/$D40E register stride)
- "Variables / stored in 7-byte blocks like the SID's voices / initialised independently"
- Zero-page pointers for SID register access; three consecutive zero-page addresses required

**Data structure — named variables visible in symbol table:**

| Symbol | Description |
|--------|-------------|
| FRACSPED | Frame speed |
| CD41x, TD41x | SID register caches (D400–D418 region) |
| TRACKLO, TRACKHI, TRACKNO | Track/sequence pointers (lo/hi byte + number) |
| BLOCKNO, BLKREP | Block number, block repeat count |
| GLID* | Glide state (GLIDSTAG, GLIDEND, GLIDADC) |
| PLSTEST, OCTAV | Pulse test, octave |
| COUNTER, DURRA | Frame counter, duration |
| VIBCOUNT, VIBEORVIB | Vibrato counter |
| PULSELO, PULSEHI | Pulse width lo/hi |
| D401STA, D417ORA, WAVECNT | Wave/control state |
| BLOCKAD, STATI | Block address, status |
| ECHO, ECHOCNT | Echo state |
| D400STA, FEOR | D400 write state, filter EOR |
| FWCOUN, ARCNT, ARL | Filter/arp counters |
| D417STO, FILSEEK | Filter sweep |
| EXAND, RCONT, COUNTUP, COUNTDO | Extended control |
| FRAGSTAT | Fragment/block status |
| DRIV, VOICES | Voice count / driver state |
| FADESTAT, FADEWEGE | Fade state, fade direction |
| EFFEROUT | Effect routing |
| FADEEND, FRASPED | Fade end, frame speed |

**Routines (from comment labels):**

| Routine | Description |
|---------|-------------|
| VIBRATO | Vibrato effect |
| GLIDE/PORTAMENTO | Portamento (glide between notes) |
| ARPEGGIO | Arpeggio table lookup |
| PSEUDO ECHO (TREMOLO) | Pseudo-echo / tremolo |
| ECHTES ECHO | "True echo" (real echo FX) |
| DRUM-ROUTINE | Drum sound (wave-table driven) |
| PULSESWEEP | Pulse width sweep |
| FILTER ROUTINE | Filter cutoff / sweep |
| FILTERSWEEP | Filter sweep (FILSEEK) |
| NOTENVERWALTUNGS ROUTINE | Note management / main note handler |
| SFX-ROUTINE | Sound effects engine |
| FADE | Song-end master volume fade |

**Effects per voice (7-byte voice block, decoded from variable names + comments):**

Per-voice parameters include:
- Note lo + hi byte frequency
- Pulse value lo + hi byte
- Wave form variable
- Duration, duration comparison
- Vibrato onset counter, vibrato speed
- Glide mode, glide end note, glide add value
- Arpeggio table pointer
- Echo type (FX1 vs FX2, true echo vs pseudo-echo)
- Filter parameter (D416 write: `SETZEN IN $D416`)
- Filter seek / sweep
- ADSR (attack/decay/sustain/release)

**SFX block format (from German comments, translated):**

```
BYTE 0 = In which voice: 01 / 02 / 04 (voice bitmask)
BYTE 1 = Which block to play?
BYTE 2 = Which block to play?
BYTE 3 = Which block to play?
...
SFX blocks must end with $FE (null-sound), then $01, $00
```

**Block format:**
- Data is organised into "blocks" — sequences of notes
- Block repeat count at start
- Blocks can loop back; loop offset tracked by BLKREP / BLOCKNO
- More than $7F blocks possible (flag)
- More than 128 blocks option (WIEDERHOLUNG / repeat flag)
- Jump within pattern supported (SPRUNG)

**Frequency table:**
- "FREQUENZTABELLE LO" and "FREQUENZTABELLE HI" are separate lo/hi byte tables
- Multiple octave scales embedded (OCTAV parameter)

**Drum system:**
- `DRUM-TAB LESEN` — reads from a drum table
- Separate DRUM tabs (DRUM0_x labels in symbol table, 16 entries per drum: DRUM0$B0 ... DRUM0F)
- TOM and DRUM wave modes distinguished

**Arpeggio system:**
- `ARP0_x` labels (16 entries per arp table: ARP0$B0 ... ARP0F)
- Two arpeggio parameters (ARPEGGIO-PARAMETER 1, ARPEGGIO-PARAMETER 2)
- Arp table referenced via ARCNT, ARL

**Data track structure:**
- TRACK3/4/5 labels (three voice tracks + possible drum track)
- BLK0–BLK7 (8 main block groups, each with 16 sub-entries: BLK0$B0...BLK0F → BLK7$B0...BLK7F)
- BL1–BL5, BL8 (sub-block references)

**Filter:**
- Filter modus, filter wert stored separately
- $D416 (filter cutoff) and $D417 (filter mode + volume) both written
- Filter sweep: adds/subtracts to filter cutoff over time
- Filter seek (FILSEEK): seeks to a target filter value

**Echo effects:**
- True echo (ECHTES ECHO): reproduces note after a delay
- Pseudo-echo / tremolo (PSEUDO ECHO): amplitude modulation
- ECHOFX1, ECHOFX2 modes

**Volume / Fade:**
- LAUTSTAERKE (master volume) written to $D418
- AUSBLEND-SPEED (fade-out speed) — parametric fade
- FADESTATUS (fade active flag)
- Voice count: how many SID voices used by music vs SFX

**Raster/IRQ:**
- `RASTERZEIT AN` label — the player can be driven by raster IRQ
- Test IRQ entry point included (can be removed)
- SFX and music can be independently enabled/disabled per frame

### Stage 3: Compotech V1 (1992)

**CSDb:** (no separate entry; part of the group's tool releases)  
**Released by:** X-Ample Architectures  
**Type:** C64 music editor (full tracker interface over V3.2 player)  
**Download (D64):** Available from CSDb group page  
**Key disk files (from tmp/xample_research/):** Compotech_1992.d64, Compotech_force_full.d64, Docs2Compotech.d64

The 1992 Compotech is the first full "tracker" edition: the V3.2 player packaged with a complete editor front-end. The editor UI was programmed by **Joachim Fräder**; the player engine remained Schneider + Kozielek's work.

The `comptech_2.1_docs.txt` documentation string visible in the V2.1 disk at line 195 reveals the editor's command vocabulary (these are ASCII strings directly visible in the binary):

```
JUMP  LOOP  ADD  BOFF  BON  ...
CUR.TUN  FADE  SPEED  $0  VOICE  000
ARP  SND  DUR  GL  CNT  BNK  #  ERROR !!
```

Translation: The editor has commands for: JUMP (pattern jump), LOOP (loop back), ADD (add offset), BON/BOFF (block on/off), CUR.TUN (current tune), FADE, SPEED, VOICE selection, ARP (arpeggio), SND (sound), DUR (duration), GL (glide), CNT (counter), BNK (bank/block number).

### Stage 4: Compotech V2.1 (1995)

**CSDb:** https://csdb.dk/release/?id=122614  
**Alternative title:** Comptech V2.1  
**Released:** August 1995  
**By:** X-Ample Architectures  
**Credits:** Code: Chap Bizarre, Joachim Fräder, Markus Schneider (Lords of Sonics / X-Ample Architectures)  
**Download (D64):** http://csdb.dk/getinternalfile.php/121250/Comptech_2.1.d64 (451 downloads as of 2026)  
**External mirror:** Pokefinder.org

V2.1 is the last publicly released version of the Compotech editor. The player engine is an evolution of V3.2 — SIDId fingerprints distinguish the V2.x variant from the earlier variant.

**What changed V1 → V2.1:** The precise changes are not documented, but SIDId requires a separate fingerprint (`(Compotech_V2.x)`) meaning the inner player loop sequence changed enough to require re-fingerprinting. The V2.x SIDId fingerprint key sequence starts with `A9 ?? 8D ?? ?? CE ?? ?? 10 ?? ...` which differs structurally from the base `X-Ample` fingerprint.

### Stage 5: Thomas_Detert Variant

SIDId classifies some Thomas Detert SIDs under a separate `(Thomas_Detert)` sub-variant of the X-Ample family. The distinguishing fingerprint sequence: `8D ?? ?? CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 20 ?? ?? 8A 18 69 07 AA C9 15 90 F1 A9 ?? 09 0F 8D 18 D4 ...`

This suggests Thomas Detert had a personal build of the player with minor modifications — possibly a different voice-advance dispatch or a different master-volume treatment.

### Stage 6: Sonic/SDS Variant

SIDId signature: `BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 ...`

A separate variant used by an author/group called Sonic or SDS. Relationship to Tufan Uysal (SoNiC) is uncertain — the timing is consistent (SoNiC started using Compotech from 1996) but not confirmed.

### Stage 7: XTracker V4.1x / V4.2x (1996)

**CSDb:** https://csdb.dk/release/?id=82320  
**Author:** Tufan Uysal (SoNiC)  
**Released:** 1996  
**By:** The Art Project Studios / Smash Designs / The Obsessed Maniacs  
**Download (D64):** http://csdb.dk/getinternalfile.php/78891/0376a.d64 (510 downloads)

XTracker is a separate editor product by Tufan Uysal that uses an X-Ample-family player engine. Uysal started using Compotech in 1996 and built his own "own versions." XTracker is NOT a product of X-Ample Architectures; it is an independent editor that maintained compatibility with the X-Ample player family's data format or produced SIDs whose inner loops are recognizably X-Ample-derived.

SIDId has TWO separate XTracker fingerprints:

**XTracker_V4.1x:**
```
CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ?? A9 ?? 09 ?? 8D 18 D4 A9 ?? 8D 16 D4
```

**XTracker_V4.2x:**
```
A0 00 F0 01 60 A9 ?? 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 ?? 8D ?? ?? 4E ?? ?? B0 07 29 00 9D 04 D4 F0 03 20 ?? ?? 8A 18 69 07 AA C9 15 90 E8 A9 ?? 09 ?? 8D 18 D4
```

The XTracker variants differ in dispatch structure (explicit three-voice calls `A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ??` in V4.1x vs. bitmask loop in V4.2x).

### Stage 8: X-Ample_Digi Variant

SIDId fingerprint:
```
29 1F 8D ?? ?? C8 B1 ?? C9 80 90 ?? 29 3F 8D ?? ?? C8 B1 ?? AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD AE ?? ?? BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A9 ?? 8D 0E DD
```

This variant writes to `$DD04/$DD05/$DD0E` — CIA 2 timer registers — indicating a digi sample playback extension that uses CIA2 for timing. Writes `$D404` (waveform registers).

---

## SIDId Signature Summary

All signatures from `sidid.cfg` (cadaver/sidid, GitHub, downloaded 2026-06-13):

```
LordsOfSonics/MS
79 ?? ?? 0A A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? AC ?? ?? BD ?? ?? 99 ?? D4 END
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4 END
(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06 END

X-Ample
9D ?? ?? BD ?? ?? 29 7F 9D ?? ?? C8 98 9D ?? ?? BD ?? ?? 29 80 9D ?? ?? BC ?? ?? B9 ?? ?? 29 0F 9D ?? ?? 9D END
(Compotech_V2.x)
A9 ?? 8D ?? ?? CE ?? ?? 10 ?? A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 90 ?? 20 ?? ?? ?? ?? 69 07 AA ?? 15 90 ?? A9 ?? 09 ?? 8D END
(Sonic/SDS)
BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 A9 00 F0 12 CE ?? ?? 10 END
(Thomas_Detert)
8D ?? ?? CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 20 ?? ?? 8A 18 69 07 AA C9 15 90 F1 A9 ?? 09 0F 8D 18 D4 A9 ?? 8D 16 D4 A9 00 F0 03 20 ?? ?? 60 END
(XTracker_V4.1x)
CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ?? A9 ?? 09 ?? 8D 18 D4 A9 ?? 8D 16 D4 END
(XTracker_V4.2x)
A0 00 F0 01 60 A9 ?? 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 ?? 8D ?? ?? 4E ?? ?? B0 07 29 00 9D 04 D4 F0 03 20 ?? ?? 8A 18 69 07 AA C9 15 90 E8 A9 ?? 09 ?? 8D 18 D4 END
(X-Ample_Digi)
29 1F 8D ?? ?? C8 B1 ?? C9 80 90 ?? 29 3F 8D ?? ?? C8 B1 ?? AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD AE ?? ?? BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A9 ?? 8D 0E DD END
```

### Key structural observations from signatures

**Base X-Ample:**
- `29 7F` / `29 80` — ANDs with $7F and $80: separates lo-7-bits from hi-bit (likely frequency nibble split or waveform bits)
- `29 0F` — ANDs with $0F: extracts lower nibble (volume or instrument index)
- `BC ?? ??` — LDY abs,X — indexed load (voice table access)
- `B9 ?? ??` — LDA abs,Y — indirect indexed note data read
- Pattern: loads 3-register sets per voice (the SID's 7-byte block, stride by 7)

**Voice advance (base):** Bitmask loop: `8A 18 69 07 AA` — transfers A to X, adds 7, stores back in X. This advances the SID register base by 7 bytes per voice ($D400→$D407→$D40E).

**Compotech V2.x:** Uses `4E ?? ??` (LSR absolute) — a logical shift right in the voice dispatch; likely the bitmask test step. Also `69 07 AA` (ADC #7, TAX) — same stride advance.

**Thomas_Detert variant:** Nearly identical to V2.x but adds an explicit `20 ?? ?? 60` (JSR ... RTS) at end — perhaps an additional post-voice callback.

**XTracker V4.1x:** Drops the bitmask loop entirely: uses explicit `A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ??` — three explicit JSR calls with X=0, X=voice1_offset, X=voice2_offset. This is a significant structural change (loop unrolled to fixed calls).

**XTracker V4.2x:** Returns to bitmask-like approach (`4E ?? ?? B0 07 29 00 9D 04 D4`) but with branch on borrow after LSR, and an explicit note-gate clear (`29 00 9D 04 D4` — AND #0, STA D404,X = gate off).

**X-Ample_Digi:** Completely different loop — reads pairs of nibbles from data (`29 1F`, `29 3F`), then writes to CIA2 timer ($DD04/$DD05) and $D40E for digi sample. This is a 4-bit or 5-bit sample player routed through CIA2 timing.

---

## HVSC Distribution (from research.md baseline)

Total X-Ample family SIDs in HVSC #84: **~387**

Known major composers:
- Thomas Detert: 177 SIDs
- Stefan Hartwig: 134 SIDs
- Markus Schneider: 105 SIDs

Variants in HVSC:
- Compotech_V2.x
- Sonic/SDS
- Thomas_Detert
- XTracker_V4.1x
- XTracker_V4.2x
- X-Ample_Digi

---

## Player Architecture Summary (for USF migration planning)

Based on the annotated player_routine.txt (Version 3.2, 1992):

1. **Single entry point** called once per VBI frame
2. **Three SID voices** each with independent state (7-byte block layout matching SID stride)
3. **Data model:** tracks → blocks → notes (hierarchical)
4. **Effects per voice:** vibrato, glide/portamento, arpeggio (table-based), drum (wave-table), pulse sweep, filter sweep, echo (real + pseudo/tremolo), note hold, fade
5. **SFX system:** parallel SFX engine with voice-bitmask allocation ($01/$02/$04); SFX blocks with repeat count
6. **Filter:** $D416 (cutoff lo), $D417 (mode + resonance), $D418 (master vol) — all written by player
7. **Frequency table:** separate lo/hi byte tables, octave-scaled
8. **Voice advance:** `ADC #7 TAX` stride — confirms the research.md note "iterates 3 voices via bitmask, calls per-voice subroutine, advances SID register base by 7 per voice ($D400, $D407, $D40E)"

OPEN: The exact block/note byte encoding is not yet decoded from the binary. The block data format (pattern bytes) is the key missing piece for USF extraction.
