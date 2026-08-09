# SID-Wizard (Hermit) — SIDId variant taxonomy + multi-SID population split

**Provenance**
- Author of this doc: research agent, 2026-06-13 (SIDfinity SID-Wizard research cluster).
- Local sources (READ-ONLY): `tmp/dmc_hunt/sidid/sidid.cfg`,
  `tmp/dmc_hunt/player-id/config/sidid.cfg`,
  `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` — the **Hermit family block is
  byte-identical across all three** (the player-id copy merely omits the trailing
  `END` token on each line; same byte payloads). SIDId is cadaver's player
  identifier; `sidid.cfg` is its signature database.
- Population: `hvsc84.db` opened READ-ONLY (`file:hvsc84.db?mode=ro`, uri=True) +
  direct PSID-header reads of the actual `hvsc85/…` SID files.
- 6502 interpretation: opcode-level disassembly of each signature (operand
  wildcards `??` left as-is), cross-checked against three real Hermit binaries.
- Family format reference: `pipelines/sidwizard/docs/research.md` (SWM format,
  instrument layout, "SID write order: SR, AD, Freq, PW, Waveform", ghost/shadow
  registers, driver variants bare/light/medium/normal/extra).

---

## 0. TL;DR

| Question | Answer |
|---|---|
| HVSC #84 tunes labelled `Hermit/SidWizard_V1.x` | **1048** |
| 1SID (single $D400 chip) | **1010** (96.4%) |
| 2SID (adds $D420…) | **29** (2.8%) |
| 3SID (adds $D440…) | **9** (0.86%) |
| 4SID | **0** |
| Sibling Hermit engines in HVSC | `1RasterTracker` 27, `FlexSID` 14, `FlexSID-Bare` 3, base `Hermit` 6 |
| SID-count column in `hvsc84.db`? | **No** — must be derived from the PSID header (psid_version + 2nd/3rd-SID address bytes) or from the `_2SID`/`_3SID` filename suffix |
| Multi-SID in scope for the $D400–$D418 verdict? | **No** — 2SID/3SID write extra chips at $D420+/$D440+; out of scope. The in-scope target is **1010 single-SID** tunes. |

The clean rule that falls out of the data: **psid_version maps 1:1 to chip count**
for this engine in HVSC — `v2 ⇒ 1SID, v3 ⇒ 2SID, v4 ⇒ 3SID` (zero exceptions across
1048 files). The multi-SID tunes are additionally all named `*_2SID.sid` / `*_3SID.sid`,
which is the *only* signal DeepSID itself uses (see `deepsid_labelling.md`).

---

## 1. The Hermit family block in `sidid.cfg` (verbatim)

```
Hermit
0A 0A 0A 0A 85 02 B5 90 F0 19 C9 7E F0 END
(Hermit/3SID)
A0 03 BE ?? ?? B5 80 99 15 D4 B5 81 99 ?? ?? B5 82 99 ?? ?? 88 10 EB C8 BE D8 13 B5 40 99 00 D4 B5 43 99 ?? ?? B5 46 99 ?? ?? C8 C0 15 D0 E9 60 END

Hermit/SidWizard_V1.x
F0 04 C0 60 90 03 4C ?? ?? BC END
(SidWizard_V1.0)
0A 0A 0A 0A 8D ?? ?? C8 B1 ?? 8D ?? ?? A9 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? C8 98 8D END
(SidWizard_V1.2)
48 20 ?? ?? 68 4C ?? ?? 20 ?? ?? A0 ?? 71 ?? 9D ?? ?? 60 20 ?? ?? A0 ?? 71 ?? 8D ?? ?? 60 9D ?? ?? 60 END
(SidWizard_V1.4)
60 A0 ?? 20 ?? ?? 4C ?? ?? A0 ?? B1 ?? 29 30 9D ?? ?? 60 0A 9D ?? ?? 60 8D ?? ?? 8D ?? ?? 60 0A 0A 0A 0A END
(SidWizard_V1.5)
A0 ?? B1 ?? 9D ?? ?? 2C ?? ?? 30 ?? A0 ?? B1 ?? A8 E0 ?? 90 ?? B1 ?? F0 ?? C9 FF F0 END
(SidWizard_V1.?)
B1 ?? 9D 05 D4 C8 B1 ?? 9D 06 D4 A9 ?? 9D ?? ?? 3D ?? ?? 9D ?? ?? 9D 04 D4 60 END
(SidWizard_2SID)
A0 ?? 99 ?? ?? 88 10 ?? A0 ?? 99 00 D4 99 ?? ?? 88 END
(SidWizard_3SID)
A0 ?? 99 ?? ?? 88 10 ?? A0 ?? 99 00 D4 99 ?? ?? 99 END

Hermit/1RasterTracker
8D 0F D4 E6 FF 60 A4 FC B3 F5 F0 27 END

Hermit/FlexSID
AB 00 95 C1 9D 00 D4 E8 E0 3F D0 F6 8E 18 D4 60 A2 END
Hermit/FlexSID-Bare
A2 3F A9 00 95 C0 CA 10 FB 60 A2 0E 86 FF D6 D7 10 END
```

### How SIDId names work (for reading the above)

- A bare name on its own line (`Hermit/SidWizard_V1.x`) is the **primary engine
  identifier** — what SIDId reports and what HVSC's `STIL`/`Documents/sidid`
  classification uses (and what `hvsc84.db.engine` carries).
- A name in **parentheses** `(SidWizard_V1.0)` is a **sub-signature**: it refines
  the match but is reported as a parenthetical addendum. In HVSC's DB these all
  collapse to the single primary `Hermit/SidWizard_V1.x` engine string — i.e.
  **`hvsc84.db` does NOT preserve which version/chip-count sub-signature fired.**
  (Confirmed: only `Hermit/SidWizard_V1.x` appears as a distinct `engine` value;
  no `_V1.0`/`_2SID` engine strings exist in the DB.)
- `??` matches any single byte (a relocation-variable operand). `END` terminates a
  signature. The signatures are searched against the whole loaded SID image.

---

## 2. Per-signature 6502 interpretation

Each block below: the raw bytes, the disassembly, and what it tells us. All address
operands are *relocatable* — the absolute `$D4xx` targets are the load-bearing part
(they're hard-wired register addresses, so SIDId leaves them un-wildcarded, which is
exactly why they reveal chip count).

### 2.1 `Hermit` (base / family root)
```
0A 0A 0A 0A   ASL A ×4          ; ×16 scale (note → table index, or nibble→hi)
85 02         STA $02           ; zp scratch
B5 90         LDA $90,X         ; per-channel state table at zp $90 (7-byte bunches)
F0 19         BEQ +$19
C9 7E         CMP #$7E          ; $7E = "gate off" pattern command (see research.md §Pattern)
F0 ..         BEQ ...
```
**Reading:** generic SID-Wizard *play-routine prologue* — the `LDA $90,X` confirms the
per-channel state lives in zero-page (research.md: "Zero-page: bunches of 7 bytes per
channel"); `CMP #$7E` is the pattern note/command decode ($7D/$7E = gate on/off). This
is the loosest, most general Hermit match; the 6 HVSC tunes that land here as bare
`Hermit` are SID-Wizard tunes whose more-specific sub-signature didn't fire (older/odd
relocations or hand-edited players). **No chip-count info** (single $D400 implied).

### 2.2 `Hermit/SidWizard_V1.x` (the primary engine signature — 1048 tunes)
```
F0 04         BEQ +$04
C0 60         CPY #$60          ; $60 = vibrato FX marker (research.md §Pattern: $60 vibrato)
90 03         BCC +$03
4C ?? ??      JMP <reloc>        ; dispatch to FX handler
BC ?? ??      LDY <reloc>,X
```
**Reading:** the *pattern-column dispatch* — `CPY #$60` separates notes ($00–$5F) from
the FX range ($60+) and branches into the effect jump. This is the stable fingerprint
of the SID-Wizard pattern interpreter and is what classifies all 1048 tunes. **Engine
identity, not version or chip count.**

### 2.3 Version sub-signatures (refine V-version of the player)

These fingerprint *specific routines* in successive player.asm revisions. They are NOT
a strict total order (a given tune matches whichever revision's routine bytes survive
relocation), but the mapping is:

| Sub-sig | Routine fingerprinted | Decoded gist | → version |
|---|---|---|---|
| `(SidWizard_V1.0)` | sequence/pattern pointer setup | `ASL A ×4` then a run of `STA abs` / `LDA (zp),Y` / `INY` copying 16-bit pointers into self-mod slots, ending `TYA / STA abs` | **V1.0** (2012 RC) |
| `(SidWizard_V1.2)` | PW/filter table write trampoline | `PHA / JSR / PLA / JMP` wrapper, then `LDY # / ADC (zp),Y / STA abs,X` and `… STA abs` — two near-identical table writers (one `,X`-indexed per-voice, one absolute) | **V1.2** |
| `(SidWizard_V1.4)` | gate-off waveform/PW pointer decode | `RTS / LDY # / JSR / JMP`, then `LDA (zp),Y / AND #$30 / STA abs,X` (mask test+ring bits) + `ASL A / STA abs,X` | **V1.4** |
| `(SidWizard_V1.5)` | table-step engine w/ end marker | `LDY # / LDA (zp),Y / STA abs,X / BIT abs / BMI` then a second `LDA (zp),Y / TAY / CPX # / BCC / LDA (zp),Y / BEQ / CMP #$FF / BEQ` ($FF = table terminator, research.md) | **V1.5** |
| `(SidWizard_V1.?)` | **single-SID** ADSR+ctrl flush | `LDA (zp),Y / STA $D405,X` (SR) ; `LDA (zp),Y / STA $D406,X` (AD) ; `LDA # / STA abs,X / AND abs,X / STA abs,X / STA $D404,X` (waveform/gate) | **unknown ≥V1.5** — version couldn't be pinned, but it's clearly the 1-chip register writer (only `$D404/$D405/$D406,X`, voice-strided base $D400) |

**Important:** none of these version sub-sigs distinguish chip count *except* by their
absence on multi-SID tunes — the chip count is carried by the `_2SID/_3SID` sub-sigs
below and by the PSID header, not by the V-version. There is **no `V1.8`/`V1.9`
sub-signature** in this `sidid.cfg`; tunes made with the modern 1.7–1.94 players match
via the version-agnostic primary `V1.x` signature (and/or `(SidWizard_V1.5)`/`(V1.?)`).
So "version" coverage here is effectively {1.0, 1.2, 1.4, 1.5, ≥1.5-unknown, generic}.

### 2.4 Chip-count sub-signatures — **the load-bearing multi-SID discriminator**

These two fingerprint the **ghost/shadow-register → SID flush loop** (research.md:
"Ghost/shadow registers buffered in RAM before SID writes"). The number of consecutive
`99 STA <chip-base>,Y` stores per loop body = the number of SID chips.

```
(SidWizard_2SID)
A0 ??         LDY #<n>           ; index over a register block
99 ?? ??      STA <filter?>,Y
88            DEY
10 ??         BPL -..            ; flush block #1 (filter / second sub-bank)
A0 ??         LDY #<n>
99 00 D4      STA $D400,Y        ; chip 1 voice regs
99 ?? ??      STA $D4xx,Y        ; chip 2  (e.g. $D420)   ← TWO stores
88            DEY                ; …loop
```
```
(SidWizard_3SID)
A0 ??         LDY #<n>
99 ?? ??      STA …,Y
88            DEY
10 ??         BPL -..
A0 ??         LDY #<n>
99 00 D4      STA $D400,Y        ; chip 1
99 ?? ??      STA $D4xx,Y        ; chip 2  ($D420)
99 ?? ??      STA $D4xx,Y        ; chip 3  ($D440)   ← THREE stores
```
The **only byte difference** between the two sub-sigs is the 16th token: `88` (DEY,
loop continues → 2SID) vs `99` (a third `STA …,Y` → 3SID). This is the cleanest
possible chip-count tell.

**Verified against real binaries** (pattern search over the loaded image):
- `MUSICIANS/H/Hermit/Tree_Angel_3SID.sid` → 3SID sig hits at file offset `$2AC`, 2SID sig absent.
- `MUSICIANS/H/Hermit/Phonky_2SID.sid` → 2SID sig hits at `$1D3`, 3SID sig absent.

### 2.5 `(Hermit/3SID)` (top-level, distinct from `(SidWizard_3SID)`)
```
A0 03         LDY #$03
BE ?? ??,Y    LDX <reloc>,Y      ; per-voice index from a 4-entry table
B5 80         LDA $80,X          ; zp shadow filter regs ($80..)
99 15 D4      STA $D415,Y        ; $D415 = filter cutoff lo  ← FILTER bank, Y over chips
B5 81 / 99 …  …$D416,Y           ; $D416 cutoff hi
B5 82 / 99 …  …$D417,Y           ; $D417 res/filt
88 / 10 EB    DEY / BPL          ; loop the 3-chip filter flush
C8            INY
BE D8 13,Y    LDX $13D8,Y        ; per-voice index, voice bank
B5 40 / 99 00 D4   LDA $40,X / STA $D400,Y   ; voice freq lo, chip-strided
B5 43 / 99 …  ; $D403 …
B5 46 / 99 …  ; $D406 …
C8 / C0 15 / D0 E9   INY / CPY #$15 / BNE     ; $15 = 21 = 3×7-register stride
60            RTS
```
**Reading:** this is the **3SID *register-flush engine* for the broader Hermit toolset**
(it appears separately from the SidWizard-specific `(SidWizard_3SID)` and is keyed off a
zp shadow bank at $40/$80 with a `$13D8` voice-index table). `CPY #$15` (21) = 3 chips ×
7 registers. It is the 3SID counterpart that matches some Hermit 3SID outputs whose flush
loop is X-indexed rather than the SidWizard `99,Y` triple-store form. **3 SID chips.**

### 2.6 `Hermit/1RasterTracker` (separate engine — 27 HVSC tunes)
```
8D 0F D4      STA $D40F          ; $D40F = SID3 freq-hi / (in 1-chip) FILTER-CUTOFF-HI write
E6 FF         INC $FF            ; bump frame/raster counter (self-mod step)
60            RTS
A4 FC         LDY $FC
B3 F5         LAX ($F5),Y        ; *illegal opcode* LAX — extreme size optimisation
F0 27         BEQ +$27
```
**Reading:** Hermit's **1 Raster-Tracker** (separate 2013 product, CSDb #117935) — a
player engineered to run in ~65 CPU cycles / one PAL rasterline. The illegal `LAX
($F5),Y` and the single direct `STA $D40F` are the tells of the hyper-minimal player.
**This is a DIFFERENT ENGINE from SID-Wizard** (different file format, different player,
single-chip). Single $D400 bank.

### 2.7 `Hermit/FlexSID` + `Hermit/FlexSID-Bare` (separate engine — 14 + 3 HVSC tunes)
```
FlexSID
AB 00         LAX #$00           ; *illegal* LAX immediate: A=X=0
95 C1         STA $C1,X          ; clear zp ghost-register block
9D 00 D4      STA $D400,X        ; mirror-blit ghost → SID, X = 0..$3E
E8            INX
E0 3F         CPX #$3F           ; $3F = 63 → fills the WHOLE $D400..$D43E bank
D0 F6         BNE -$0A
8E 18 D4      STX $D418          ; final volume/filter-mode write ($D418), X now $3F
60            RTS
```
```
FlexSID-Bare
A2 3F         LDX #$3F
A9 00         LDA #$00
95 C0         STA $C0,X          ; clear $C0..$FF zp ghost block (64 bytes)
CA / 10 FB    DEX / BPL -$05     ; clear-loop
60            RTS
A2 0E / 86 FF / D6 D7 / 10 …  LDX #$0E / STX $FF / DEC $D7,X / BPL   ; counter step
```
**Reading:** **FlexSID** is Hermit's later (2022, CSDb #220017 = FlexSID-1.2) compact
SID player. The `CPX #$3F` mirror-blit of a 63-byte ghost block straight into `$D400,X`
(then `STX $D418`) is a whole-bank flush — note it writes up to `$D43E`, so a 2SID FlexSID
tune naturally writes $D420+ via the *same* loop (the bank width, not extra code, carries
the chip count). `FlexSID-Bare` is the size-minimal "bare" driver variant (same family,
smaller init clearing $C0..$FF). **Separate engine from SID-Wizard**, though same author
and the same ghost-register philosophy.

---

## 3. Population — `hvsc84.db` (read-only) + PSID-header derivation

### 3.1 Engine-string counts (DB `engine` column)
| engine | count |
|---|---|
| `Hermit/SidWizard_V1.x` | **1048** |
| `Hermit/1RasterTracker` | 27 |
| `Hermit/FlexSID` | 14 |
| `Hermit` (base) | 6 |
| `Hermit/FlexSID-Bare` | 3 |
| `Reflextracker` *(NOT Hermit — different author; listed only to avoid confusion)* | 137 |

### 3.2 SID-count split — there is **no `sid_count`/`flags` column in `hvsc84.db`**
The DB schema (`sids` table) has `is_psid, psid_version, load_addr, init_addr,
play_addr, n_subtunes, …` but **no SID-chip-count or PSID-flags field**. Derived
instead by reading the PSID v2NG+ header of each file:
- `secondSIDAddress` at header offset **0x7A**, `thirdSIDAddress` at **0x7B**
  (a page nibble: chip addr = `$D000 | (byte << 4)`); only meaningful for
  `version ≥ 3`.

Result over all 1048 `Hermit/SidWizard_V1.x` files (all read OK, 0 missing):

| chips | count | % | psid_version | how flagged |
|---|---|---|---|---|
| **1SID** | **1010** | 96.4% | all **v2** | header 2nd/3rd-SID bytes = 0 |
| **2SID** | **29** | 2.8% | all **v3** | 2nd-SID byte set |
| **3SID** | **9** | 0.86% | all **v4** | 2nd + 3rd-SID bytes set |
| 4SID | 0 | — | — | — |

`psid_version ↔ chip-count is a perfect bijection here` (v2=1, v3=2, v4=3, no exceptions).
Magic: 1041 `PSID`, 7 `RSID`.

2nd-SID address distribution among the 38 multi-SID tunes: `$D420` ×26 (standard),
`$DE00` ×9 (all Televicious — an I/O-area placement), `$D500` ×3. 3rd-SID (3SID only)
is `$D440` in all 9.

### 3.3 The 38 multi-SID members (out of scope for the $D400–$D418 verdict)
```
3SID  $D420/$D440  DEMOS/A-F/Devils_ReSIDence_3SID.sid
2SID  $D420        DEMOS/S-Z/TES_IV_Oblivion_2SID.sid
2SID  $D420        MUSICIANS/B/Batsman/Piraten_2SID.sid
2SID  $D500        MUSICIANS/C/C0zmo/Space_Oddity_2SID.sid
2SID  $D420        MUSICIANS/C/Chabee/Stickman_2SID.sid
2SID  $D420        MUSICIANS/C/Chiummo_Gaetano/A_Childhood_Dream_2SID.sid
2SID  $D420        MUSICIANS/C/Chiummo_Gaetano/Calming_Stream_2SID.sid
3SID  $D420/$D440  MUSICIANS/C/Chiummo_Gaetano/Edelin_Tales_Theme_3SID.sid
3SID  $D420/$D440  MUSICIANS/C/Chiummo_Gaetano/Enchanted_Forest_3SID.sid
3SID  $D420/$D440  MUSICIANS/C/Chiummo_Gaetano/Happy_New_Wave_3SID.sid
3SID  $D420/$D440  MUSICIANS/C/Chiummo_Gaetano/Hope_3SID.sid
3SID  $D420/$D440  MUSICIANS/C/Chiummo_Gaetano/Ramos_2016_3SID.sid
2SID  $D420        MUSICIANS/D/DAM/New_Air_2SID.sid
3SID  $D420/$D440  MUSICIANS/E/Et1999cc/Resonance_3SID.sid
2SID  $D420        MUSICIANS/H/Hermit/E_G_Blues_2SID.sid
2SID  $D420        MUSICIANS/H/Hermit/Phonky_2SID.sid
3SID  $D420/$D440  MUSICIANS/H/Hermit/Thiz_Iz_Da_Gizda_3SID.sid
3SID  $D420/$D440  MUSICIANS/H/Hermit/Tree_Angel_3SID.sid
2SID  $D420        MUSICIANS/M/M_O_T/Take_em_Out_stereo_2SID.sid
2SID  $D420        MUSICIANS/N/Nobody/Hardtek_Jam_2SID.sid
2SID  $D420        MUSICIANS/N/Nobody/Turn_it_Louder_2SID.sid
2SID  $D420        MUSICIANS/S/Spider_Jerusalem/Canon_457_Study_2_2SID.sid
2SID  $D420        MUSICIANS/S/Stone_James/A_Final_Hyperbase_2SID.sid
2SID  $D420        MUSICIANS/S/Stone_James/Dawn_of_the_Oval_Hordes_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Aliens_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Cybo_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Eviltwin_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Fidelity_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Finity_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Giovanni_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Ring-a-sync_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Sauceage_2SID.sid
2SID  $DE00        MUSICIANS/T/Televicious/Symphonic_2SID.sid
2SID  $D420        MUSICIANS/T/Toggle/Beacon_2SID.sid
2SID  $D500        MUSICIANS/V/Vincenzo/Quad_Core_bottom_part_2SID.sid
2SID  $D500        MUSICIANS/V/Vincenzo/Quad_Core_top_part_2SID.sid
2SID  $D420        MUSICIANS/W/Wemyss_Chris/Grange_Hill_2SID.sid
2SID  $D420        MUSICIANS/Y/Yaruni/Lethal_Xcess_Menu_2SID.sid
```
**Scope note:** these 38 emit writes to $D420+/$D440+ in addition to $D400–$D418, so
the standard single-chip instruction-stream verdict cannot judge them as-is. Either
exclude them (the cleanest first cut → leaves **1010 in-scope tunes**) or extend the
verdict's write-window to all three chip banks. They are also trivially identifiable two
ways (`_2SID`/`_3SID` filename suffix; `psid_version ≥ 3`) so an exclusion filter is
cheap to write.

### 3.4 Init / load / play address spread (all 1048)
- `load_addr` is **$0000 for all 1048** in the DB — i.e. the PSID `loadAddress` header
  field is 0, meaning the *effective* load address is the first two bytes of the C64
  data block (HVSC's normal embedded-load convention). Do not read the $0000 as a real
  address; the real placement tracks `init_addr`.
- `init_addr` (top of the long tail):
  | init | count | | init | count |
  |---|---|---|---|---|
  | **$1000** | **775** | | $E600 | 14 |
  | $0FB8 | 51 | | $8000 | 11 |
  | $0C00 | 25 | | $0900 | 11 |
  | $E000 | 23 | | $34F0 | 8 |
  | $A000 | 18 | | …79 distinct values total | tail of 1s/2s |
- `play_addr` = `init_addr + 3` in every common bucket (e.g. $1003 ×775, $0FCF ×46 for
  the $0FB8 relocation — note $0FB8→play $0FCF is +$17 because that build's play vector
  sits past a header, see research.md "Init = base (subtune in A)"). Confirms the
  SID-Wizard export convention: **init = player base, play = base + 3**.
- The dominant target is **init=$1000 (775, 74%)**; principal relocations are
  $0FB8 (51), $0C00 (25), $E000 (23), $A000 (18), $E600 (14). This is the natural
  "highest-leverage first" ordering for a migration (mirrors the FC `init=$1000`
  strategy in `project_fc_fingerprint_and_standard`).

### 3.5 Subtune distribution (all 1048)
`991` single-subtune (94.6%); `22`×2, `9`×3, `9`×4, `5`×5, `2`×6, then a long thin tail
(`7, 8, 9, 9, 10, 10, 12, 17, 24` subtunes — one or a few files each). Max = 24 subtunes
(SWM spec allows up to 31). PSID-version split: v2 1010, v3 29, v4 9.

### 3.6 Build/migration status
All 1048 are **un-migrated**: `pipeline IS NULL`, `usf_path` empty, `verify_status` NULL.
SID-Wizard is a greenfield family in SIDfinity.

---

## 4. How the siblings relate to SID-Wizard (engine map)

| SIDId name | What it is | Same engine as SID-Wizard? | Chips |
|---|---|---|---|
| `Hermit/SidWizard_V1.x` | **SID-Wizard** tracker player (2012–2026, V1.0–1.94). SWM format. | — (this is it) | 1 (v2) / 2 (v3) / 3 (v4) |
| `(SidWizard_V1.0…V1.5/V1.?)` | version sub-sigs of the same player | yes (refinements) | 1 unless paired with a chip sub-sig |
| `(SidWizard_2SID)/(3SID)` | chip-count sub-sigs (count the `99 STA,Y` stores) | yes | 2 / 3 |
| `(Hermit/3SID)` | broader-Hermit 3-chip flush engine (X-indexed shadow bank, `CPY #$15`) | related family, distinct flush form | 3 |
| `Hermit/1RasterTracker` | **1 Raster-Tracker** — separate 2013 hyper-minimal (~1 rasterline / 65cyc) tracker+player; uses illegal `LAX`. | **No — different engine + format** | 1 |
| `Hermit/FlexSID` | **FlexSID** — separate 2022 compact player; 63-byte ghost-block mirror-blit to `$D400,X` + `STX $D418`. | **No — different engine** (same author, same ghost-reg idea) | 1 (bank-wide blit naturally extends to 2SID) |
| `Hermit/FlexSID-Bare` | FlexSID's "bare" size-minimal driver variant | FlexSID family | 1 |
| `Reflextracker` | **NOT a Hermit engine** (different author); only adjacent in name | No | n/a |

**Driver variants vs version:** research.md §Player Architecture lists SID-Wizard's
player *driver* variants — **bare / light / medium / normal / extra** (a feature↔size
tradeoff selected at export; SWM header offset 0x13 "Driver type"). These are
*orthogonal* to the V-version and to chip count, and SIDId does **not** fingerprint them
separately for SID-Wizard (it only forks `FlexSID` vs `FlexSID-Bare`). A migration must
treat "driver variant" as a parameter discovered from the player image / SWM header, not
from the SIDId label.

---

## 5. Practical takeaways for the SIDfinity migration

1. **In-scope target = 1010 single-SID SID-Wizard tunes** (psid_version==2). The 38
   multi-SID (29×2SID + 9×3SID) write $D420+/$D440+ and are out of scope for the
   standard $D400–$D418 verdict — exclude via `_2SID`/`_3SID` suffix or `psid_version≥3`,
   or extend the write-window if multi-chip support is later wanted.
2. **Highest-leverage relocation = init=$1000** (775 tunes, 74%) — start there, exactly
   like the FC standard-player rollout. Then $0FB8/$0C00/$E000/$A000/$E600.
3. **94.6% are single-subtune** → subtune handling is a minor concern initially.
4. **`hvsc84.db` cannot tell you the SID-Wizard sub-version or chip count** — the sub-sig
   names collapse to one `engine` string and there's no chip-count column. Use the PSID
   header (this doc's method) if version/chip granularity is needed.
5. **Don't conflate the siblings.** 1RasterTracker and FlexSID/FlexSID-Bare are *separate
   Hermit engines* with their own formats — a SID-Wizard pipeline will not handle them.
6. The signatures confirm research.md's **ghost/shadow-register write model**: the chip
   count is literally the number of `STA <chipbase>,Y` stores in the flush loop, and
   the SID write order (SR, AD, freq, PW, waveform) is visible in `(SidWizard_V1.?)`
   ($D405 SR → $D406 AD → … → $D404 ctrl/gate last).

## Leads to follow
- **Pin the version sub-sigs to player.asm revisions empirically.** Disassemble the
  $1000-init majority and confirm which `(SidWizard_V1.x)` sub-sig each modern (1.7–1.94)
  player matches — the cfg only names up to "V1.5/V1.?", so verify whether 1.7+ all fall
  through to the generic primary signature (then SIDId version granularity caps at ~1.5).
- **Resolve the $0FB8→play $0FCF (+$17) offset** vs the usual init+3: read one $0FB8 tune
  to see whether $0FB8 is a packed/auto-relocating wrapper (49 of 51 use $0FCF, 2 don't).
- **Decode one canonical 1SID init=$1000 tune end-to-end** (siddump --writelog) and map
  its frame write stream onto the SWM format in research.md — the natural first migration
  candidate. (A sibling agent already has tasks #34–36 staged for this; coordinate.)
- **Confirm 4SID truly absent.** SID-Wizard advertises up to 4SID but HVSC #84 has none
  labelled here (max is 3SID). Worth a quick CSDb check before assuming the engine path
  never needs a 4th bank.
- **`(Hermit/3SID)` vs `(SidWizard_3SID)` overlap:** determine whether any HVSC 3SID tune
  matches the X-indexed `(Hermit/3SID)` flush instead of the SidWizard `99,Y`-triple
  form (would indicate a different/older 3SID export path).
- **Cross-check the 9 `DE00` (Televicious) 2SID tunes** — the 2nd chip at $DE00 (I/O
  expansion area, not the usual $D420) may need special address handling if multi-SID is
  ever brought in scope.
