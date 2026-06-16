---
source_url: multiple — sidid.nfo (cadaver/sidid GitHub), sidid binary scan of HVSC, PSID headers
fetched_via: curl (sidid.nfo), built sidid from source, Python PSID scan
fetch_date: 2026-06-16
reliability: primary — byte-level verification against HVSC #84 SIDs
---

# MoN sub-signature identity + per-tune coverage

## 1. sidid.cfg sub-signature taxonomy

The cadaver/sidid.cfg file registers MoN-related players at two levels:

### Top-level player entries (what HVSC DB uses)
| sidid player name    | HVSC SID count | Description |
|----------------------|----------------|-------------|
| MoN/Deenen           | 135            | Deenen "Musicfile" tracker engine |
| MoN/Bjerregaard      | 77             | Bjerregaard variant of MoN player |
| MoN/FutureComposer   | 4024           | FC player (unrelated to Deenen tracker) |
| Music_Assembler      | 6351           | Dutch USA-Team, separate family |

### Sub-signatures (parenthesised in sidid.cfg — reported only with `-s"(name)"`)

All the following are sub-variants of the **MoN/FutureComposer** player:

| Sub-ID          | Abbrev expansion                         | HVSC count | Key representative tune |
|-----------------|------------------------------------------|------------|-------------------------|
| (FC_V3.x)       | Future Composer v3.x                     | 117        | Standard FC v3 player code |
| (FutureComposer_V1.0) | Future Composer v1.0                | 2919       | Dominant FC variant |
| (FC_V4_Packed)  | Future Composer v4 packed                | 519        | Packed variant |
| (MoN/Cyb2)      | **Cybernoid II** (1988 Hewson)           | 47         | Tel_Jeroen/Cybernoid_II.sid |
| (MoN/TTWII)     | **That's the Way It Is** (intro, Deenen) | 18         | Deenen_Charles/Thats_the_Way_It_Is_intro.sid |
| (MoN/JTS)       | **JT in Space** (1988 MoN)              | 11         | Tel_Jeroen/JT_in_Space.sid |
| (MoN/RWE)       | **RWE Intro** (1988 MoN/RWE group)       | 46         | Deenen_Charles/RWE_Intro.sid |
| (MoN/Bantam)    | **Bantam** (1988 MoN/Tel)               | 14         | Tel_Jeroen/Bantam.sid |

Sub-variant under MoN/Deenen:
| (MoN/Deenen_Digi) | Deenen digi player sub-variant          | 16         | Tel_Jeroen/Digi-Piece_for_Telecomsoft.sid |

**Note:** the sub-IDs are distinct NAME entries in sidid.cfg and ARE reported when using
`sidid -s"(MoN/Cyb2)"` etc. They do NOT appear in normal scanning output (the parent
MoN/FutureComposer or MoN/Deenen matches first). The HVSC DB uses only the parent names.

---

## 2. Sub-variant name expansions

### (MoN/Cyb2) — Cybernoid II
- Named after **Cybernoid II** (Hewson, 1988), music by Jeroen Tel
- File: `MUSICIANS/T/Tel_Jeroen/Cybernoid_II.sid`
- Defines pattern: `4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C`
- Slightly different voice-processor code than FC v3.x (different tail sequence)
- Author cluster: Deenen_Charles (Worktunes), Ouwehand_Reyn, Tel_Jeroen, Mad_Donne_Marcel, Siebold_Markus (11 tunes)
- Total 47 tunes across HVSC

### (MoN/TTWII) — That's the Way It Is (intro)
- Named after **"That's the Way It Is" intro** (Deenen_Charles, ©1988 MoN)
- File: `MUSICIANS/D/Deenen_Charles/Thats_the_Way_It_Is_intro.sid`
- Note: The *main* tune (`Tel_Jeroen/Thats_the_Way_It_Is_main.sid`) uses MoN/Deenen,
  NOT this FC sub-variant. The "intro" version uses FC with a specific voice-processor variant.
- Defines pattern: `BC ?? ?? BE ?? ?? 8E ?? ?? A5 ?? 29 0F 85 27 A5 ?? 29 70 4A 4A 4A 4A A6 ?? 95 ?? A0 BC A5 ?? 10 02 A0 7D 8C ?? ?? BC ?? ?? B9 ?? ?? 38 F9`
- Author cluster: Defbeat (12 tunes), Audial_Arts/Prijt_Francois (3), Captain_Rock (2), Commander (1)
- Total 18 tunes (none in Tel_Jeroen dir)

### (MoN/JTS) — JT in Space
- Named after **"JT in Space"** (1988 Maniacs of Noise), music by Jeroen Tel
- File: `MUSICIANS/T/Tel_Jeroen/JT_in_Space.sid`
- Defines pattern: `A9 ?? 9D ?? ?? 9D ?? ?? 9D ?? ?? 4C ?? ?? 8D ?? ?? 29 80 F0 0E AD ?? ?? 29 1F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? 29 40 F0 0E AD ?? ?? 29 3F 9D`
- Author cluster: TC/Timur Baysal (Paramount) = 9 tunes, Captain_Rock = 2, Audial_Arts/Peters_Patrick = 1
- Total 11 tunes

### (MoN/RWE) — RWE Intro
- Named after **"RWE Intro"** (1988 Maniacs of Noise/RWE), composed by Charles Deenen
- File: `MUSICIANS/D/Deenen_Charles/RWE_Intro.sid`
- Copyright: "1988 Maniacs of Noise/RWE" — RWE was a Dutch demo group/label
- Defines pattern: `B0 05 BD ?? ?? D0 05 BD ?? ?? 29 FE 9D ?? ?? BD ?? ?? D0 0A AD ?? ?? C9 ?? D0 03 99 06 D4 BD`
- Author cluster: Audial_Arts/Prijt_Francois, Deenen_Charles, FAME, TC/Timur Baysal
- Total 46 tunes

### (MoN/Bantam) — Bantam
- Named after **"Bantam"** (1988 Maniacs of Noise), music by Jeroen Tel
- File: `MUSICIANS/T/Tel_Jeroen/Bantam.sid`
- Defines pattern: `0A 0A 0A AA 8E ?? ?? BD ?? ?? A6 FF 9D ?? ?? 99 04 D4 A9 00 99 02 D4 A6 FF 9D`
- Author cluster: Tel_Jeroen (6 tunes incl. Chrome_Met1, DemoSong, Lost_in_China, Orion_Intro, Reggae_Example),
  Emotional_Mozes (6 tunes), Deenen_Charles/Ninja_Remix (1), Red_Duijckaerts_Roger (1)
- Total 14 tunes

---

## 3. Variant → author cluster mapping

### MoN/Deenen (135 SIDs)
- Primary author: **Jeroen Tel** (72 SIDs = 53%) — dominant user post-MoN
- **Charles Deenen** (19 SIDs = 14%) — driver author
- **Reyn Ouwehand** (16 SIDs = 12%)
- Minor: JVD (7), Audial_Arts (7), Holt_Hein (2), Leitch_Barry (2), No-XS (2), others (9)

### MoN/Bjerregaard (77 SIDs)
- **Tagged separately** from MoN/Deenen in sidid — not folded in
- Primary author: Johannes Bjerregaard (14 SIDs in his own folder + contributions elsewhere)
- Also used by: Blues_Muz/Gallefoss, Dokken, Drumbeat, others
- The Audiomaster_V1 editor (Scroll/Megastyle, 1989) is based on the Bjerregaard player
  (specifically the Stormlord.sid player — see nfo)
- Stormlord.sid: collaboration Bjerregaard + Tel, copyright "1989 Hewson/MoN"
  and also matches **(MoN/Deenen_Digi)** — Tel contributed the digi channel

### MoN/FutureComposer (4024 SIDs)
- FC is NOT the Deenen tracker — it is the Future Composer player by Tel + FCS (Juha Granberg editor)
- Already fully migrated in `pipelines/future_composer/`
- Sub-variants (Cyb2, TTWII, JTS, RWE, Bantam) are code micro-variants of the FC player
  used by different Dutch demo scene groups

---

## 4. MoN/Deenen_Digi — digi sub-variant

**Definition:** sidid sub-ID within MoN/Deenen for tunes that embed a digi
(sample playback) routine alongside the main 3-voice tracker engine.

**Byte patterns (two required, both present in digi tunes):**
```
Pattern 1: A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D
           LDX #$00 / BEQ rel / TYA / ASL / TAY / LDA abs,Y / STA abs / LDA abs,Y / STA abs
           → sets up self-modifying pointers to sample data tables

Pattern 2: 4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4
           LSR×3 / CLV / BVC rel / LSR×3 / CLC / ADC #imm / STA $D418
           → outputs 4-bit sample nibble via volume register ($D418 bits 3-0)
```

**Mechanism:** 4-bit sample playback via the $D418 master volume register. Each
sample byte is split into two 4-bit nibbles; the upper nibble is extracted with
3× LSR + BVC branch, the lower with 3× LSR + CLC ADC bias, then written to $D418.
This is the CIA-timed volume-register digi technique (same class as Chimera digi
but different code structure).

Note: Pattern 2 in the cfg matches tunes with FOUR LSRs before the BVC branch
(`4A 4A 4A 4A B8 50`) — the pattern bytes match at the 3rd LSR. The BVC is a
relative always-branch used to select upper vs lower nibble path.

**16 HVSC tunes with MoN/Deenen_Digi sub-signature:**
- `Tel_Jeroen/`: 2400_AD, Afterburner, Daring_Dots, Digi-Piece_for_Telecomsoft,
  Hot_Rod, KOUD_HE, Lemmings_end_screen, Navy_Moves, Nighthunter, Outrun_Europa,
  Savage, Turbo_Outrun (12 tunes)
- `Deenen_Charles/`: Eye_to_Eye_intro, F1_Simulator (2 tunes)
- `Bjerregaard_Johannes/`: Stormlord (1 tune — Bjerregaard+Tel collaboration)
- `Shavitt_Guy/`: Pompa_the_Jam (1 tune)

**Notable:** Stormlord (Bjerregaard+Tel) uses both MoN/Bjerregaard AND MoN/Deenen_Digi
patterns — the Bjerregaard player base with Tel's digi extension.

---

## 5. DeepSID detection strings

DeepSID uses the same cadaver/sidid.cfg (confirmed: PHP `sid_id.php` reads `../sidid.cfg`).
Detection is first-match in cfg order, so:
- MoN/Deenen tunes → reported as `"MoN/Deenen"` by DeepSID
- MoN/FutureComposer tunes → reported as `"MoN/FutureComposer"` (sub-IDs never surface)
- MoN/Bjerregaard → reported as `"MoN/Bjerregaard"`

The only MoN-adjacent pretty name in DeepSID's `pretty_player_names.php`:
```php
'MoN/FutureComposer/Deenen_Digi' => 'MoN/FC/Deenen_Digi',
```
This key (`MoN/FutureComposer/Deenen_Digi`) does NOT match the sidid.cfg name
`(MoN/Deenen_Digi)` — it appears to be a DeepSID-internal alternate key from an
older version of the cfg or a manual DB override. In practice, DeepSID's DB
stores the parent player name (`MoN/Deenen` or `MoN/FutureComposer`) for all tunes;
the sub-IDs are not stored per-tune.

In `music.php`, DeepSID reclassifies MoN/Bjerregaard → displayed as "Bjerregaard"
(the condition `$player == 'MoN/Bjerregaard'` → `$player = 'Bjerregaard'`).

---

## 6. Music_Assembler family

The Music_Assembler + its sub-editors (VoiceTracker, Music_Mixer, DoubleTracker,
Ten_Tracker) are an **entirely separate, unrelated engine family** from MoN/Deenen.

- Author: Marco Swagerman (MC) + Oscar Giesen (OPM), Dutch USA-Team, 1989
- Sub-editors (all based on the Music_Assembler player):
  - VoiceTracker (Polonus/Science 451, 1991) — CSDB #77308
  - Music_Mixer (Polonus/Padua, 1991) — CSDB #82618
  - DoubleTracker (Polonus/Padua, 1993, multispeed) — CSDB #8430
  - Ten_Tracker (Moog/Keen Acid, 1991, 10× speed) — CSDB #63135
- HVSC count: 6351 SIDs total (all under engine label "Music_Assembler")
- No code relationship to Deenen's tracker; different player architecture

---

## 7. Leads to follow

1. **Cyb2 vs FC_V3.x byte diff** — the two patterns diverge at byte offset ~18:
   FC_V3.x has `AD ?? ?? C9 40 90 0B 29 3F 9D` (LDA abs / CMP #$40 / BCC / AND / STA);
   Cyb2 has `29 3F 9D ?? ?? FE ?? ?? 4C` (AND then short path). Both are wave/pulse
   processing variants of the same basic structure. Worth a side-by-side disasm to
   understand which specific feature differs (pulse handling? waveform cutoff?).

2. **TTWII variant distinctive feature** — the TTWII pattern is entirely different
   from Cyb2/FC_V3x: `BC ?? ?? BE ?? ?? 8E ?? ?? A5 ?? 29 0F 85 27 A5 ?? 29 70 ...`
   suggests a different voice tick structure (indexed LDY/LDX pair, different register
   access). Used exclusively by Defbeat + Audial_Arts demo-scene composers, NOT Tel.
   This might be a "licensed/leaked" version of the FC player with different voice
   channel structure.

3. **RWE identity** — "RWE Intro" copyright says "Maniacs of Noise/RWE"; 46 tunes use
   this variant (more than Bantam's 14). RWE was a Dutch demo group. The RWE variant
   has 46 matches including Audial_Arts, FAME, and TC composers. Worth checking CSDb
   for "RWE" group to understand the connection.

4. **MoN/Deenen_Digi digi clock source** — the $D418 nibble trick needs a CIA timer
   to clock the sample output. Check whether the digi SIDs use CIA1 timer A (standard
   for C64 digi routines) or abuse the VBI. The PSID `speed` field of affected SIDs
   should indicate CIA (speed bit set) for the digi subtunes.

5. **Bjerregaard+Tel Stormlord cross-classification** — Stormlord matches BOTH
   MoN/Bjerregaard AND MoN/Deenen_Digi. sidid stops at first match, so it reports
   MoN/Bjerregaard. The digi extension was likely added by Tel after Bjerregaard's
   base music. When migrating, this SID will need both the Bjerregaard voice engine
   AND the Tel digi channel.

6. **Music_Assembler sub-variants** — the 6351 Music_Assembler SIDs all carry the
   same engine label in HVSC. If targeting this family, need to distinguish the
   4 sub-editors (VoiceTracker/Music_Mixer/DoubleTracker/Ten_Tracker) using sidid
   sub-scan. VoiceTracker and DoubleTracker are likely the largest sub-groups.
