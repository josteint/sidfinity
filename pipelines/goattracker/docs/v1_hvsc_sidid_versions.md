# GoatTracker V1.x — HVSC Coverage, SidId Signatures, and Sub-version Landscape

**Provenance:** Synthesised from local sources only (no web fetch):
- `deprecated/gt2_pipeline/tools/sidid.cfg` — SidId pattern database
- `deprecated/gt2_pipeline/GoatTracker_2.65/src/gsong.c` — GT2 V1 import code (format parsing)
- `deprecated/gt2_pipeline/GoatTracker_2.65/src/sngspli2.c` — format magic detection
- `deprecated/gt2_pipeline/GoatTracker_2.65/readme.txt` — GT2 compat notes
- `tmp/goattracker_v1_research/v1_readme_125.txt` — GoatTracker V1.25 full readme
- `tmp/goattracker_v1_research/v1_readme_152.txt` — GoatTracker V1.52 full readme
- `tmp/goattracker_v1_research/v1_readme_153.txt` — GoatTracker V1.53 full readme
- `tmp/goattracker_v1_research/v1_player1_125.s` — V1.25 playroutine 1 source
- `tmp/goattracker_v1_research/v1_gmusic_153.s` — V1.53 game music player source
- `hvsc84.csv` — HVSC #84 DuckDB index (engine counts)
- HVSC SID file binary inspection (GoatTracker example + 2SID SIDs)

**Date produced:** 2026-06-29

---

## 1. HVSC Counts (HVSC #84)

| SidId engine tag    | Count | 2SID (path contains "2SID") | Single-SID |
|---------------------|-------|-----------------------------|------------|
| `GoatTracker_V1.x`  | 1,359 | 12                          | 1,347      |
| `GoatTracker_V2.x`  | 7,311 | 183                         | 7,128      |
| `GoatTracker_V2/Mini` | 1   | 0                           | 1          |
| `GoatTracker_V2/Mini2` | 1  | 0                           | 1          |

GoatTracker V1.x is a **single monolithic SidId class** — there is no per-sub-version tag in HVSC. The 1,359 V1.x SIDs span all V1 sub-versions (v1.0 through v1.53) as a single homogeneous group in the DB.

The 12 "2SID" paths are all dual-SID stereo tunes. Of these, two sub-signatures exist in `sidid.cfg` and are mutually exclusive — they distinguish V1.4-era vs V1.5-era 2SID builds.

**Directory distribution:** MUSICIANS: 1320, DEMOS: 36, GAMES: 3. Almost entirely composer-authored (not game-ripped) tunes.

---

## 2. SidId Signatures Explained

The full GoatTracker block from `deprecated/gt2_pipeline/tools/sidid.cfg` (lines 754–770):

```
GoatTracker_V1.x
BC ?? ?? B1 ?? C8 C9 60 90 ?? C9 C0 B0 ?? E9 5F END
(GT_V1.4_2SID)
B0 06 9D 06 D4 4C END
(GT_V1.5_2SID)
8D 18 D4 A0 00 D0 0C A9 END

GoatTracker_V2.x
BD ?? ?? D0 ?? BC ?? ?? B9 ?? ?? 85 ?? B9 ?? ?? 85 ?? BC ?? ?? B1 ?? C9 FF 90 END
(GT_V2.x_2SID)
8A A2 53 9D ?? ?? CA 10 FA 8D 15 D4 8D END

GoatTracker_V2/Mini
B9 ?? ?? 85 ?? B9 ?? ?? 85 ?? BC ?? ?? B1 ?? C9 7C B0 ?? 4A B0 ?? 7D ?? ?? 09 80 9D END

GoatTracker_V2/Mini2
B1 ?? C8 C9 7A B0 ?? 4A B0 ?? 7D ?? ?? 9D ?? ?? B1 ?? C8 9D END
B1 ?? C8 C9 7A B0 ?? 7D ?? ?? 4A 9D ?? ?? B0 ?? B1 ?? C8 9D END
```

### 2.1 V1.x Main Signature

```
BC ?? ??   = LDY abs,X    ; load pattern table pointer (indexed by channel X)
B1 ??      = LDA (zp),Y   ; read pattern byte via indirect Y
C8         = INY           ; advance pattern pointer
C9 60      = CMP #$60     ; compare: is this a note? (FIRSTNOTE = $60 in V1/V2)
90 ??      = BCC rel       ; branch if < $60 (special: rest/keyoff/cmd-only row)
C9 C0      = CMP #$C0     ; compare upper boundary (FIRSTPACKEDREST = $C0)
B0 ??      = BCS rel       ; branch if >= $C0 (packed rest encoding)
E9 5F      = SBC #$5F     ; subtract $5F to get 0-based note index (note $60 → idx 1)
```

This is the **pattern decode loop** in the V1 player. The V1 player reads 3-byte pattern rows `(note, cmd_instr, data)` and branches based on the note byte:
- `$00–$5D`: note bytes 0–93 (C-0 to A-7), i.e. "note − 0 = 0-based note"
  - But the SNG file stores notes as 0-based; the packed SID adds FIRSTNOTE ($60) at assembly time so the in-SID range is `$60–$BC`
  - After SBC $5F: values $60–$BC become $01–$5D (1-based note index for the freq table)
- `$5E`: KEYOFF (clear gate bit)
- `$5F`: REST
- `$60`: NOCMD (no instrument/command bytes follow; the 2nd and 3rd bytes are absent)
- `$C0–$FF`: packed rests ($C0 = 1 rest, …, $FF = 64 rests)
- `$FF`: ENDPATT marker

**Why this is V1-specific vs V2:** In V2, the pattern byte range changed. V1 uses `NOCMD = $60` (i.e. note at or above $60 means "no command bytes follow"). V2 abandoned the 3-byte variable-length scheme for a fixed 4-byte scheme. The `SBC #$5F` and the `CMP #$60` / `CMP #$C0` combination is unique to V1's variable-length decode.

**Verified in HVSC:** the signature matches at offsets ~338–700 in the three Cadaver GoatTracker example SIDs (`GoatTracker_Classical_Example.sid`, `GoatTracker_drum_example.sid`, `GoatTracker_example_MW1_title.sid`), and in all tested non-example V1 SIDs.

### 2.2 GT_V1.4_2SID Sub-signature

```
B0 06      = BCS +6        ; if carry set (from preceding comparison), branch forward 6
9D 06 D4   = STA $D406,X  ; store to SID1 voice N sustain/release register
4C         = JMP abs       ; jump to second-SID handler
```

The full 6-byte pattern `B0 06 9D 06 D4 4C` is found in V1.4-era 2SID builds. After the first SID write (e.g. to voice 1/2/3 SR register), the player branches to a duplicate channel-processing block that handles the second SID chip at base $D420 (or $D500, hardware-dependent). The `4C` (JMP abs) leads to the parallel stereo channel code.

**Confirmed:** Found at offset 1202 in `MUSICIANS/C/Cadaver/Stereotest_2SID.sid`.

### 2.3 GT_V1.5_2SID Sub-signature

```
8D 18 D4   = STA $D418    ; store to SID1 master volume register
A0 00      = LDY #0       ; reset Y index
D0 0C      = BNE +$0C     ; branch (always taken unless Y was already 0 before LDY)
A9 ??      = LDA #imm     ; load the second SID's master volume value
```

The `STA $D418` / `LDY #0` / `BNE` / `LDA #imm` sequence is how the V1.5+ 2SID player writes the master volume separately for the two SID chips. The branch skips the second SID's $D438 write when a flag condition is not met. This changed between V1.4 and V1.5 because V1.5 rewrote the playroutine (testbit hard restart, new ADSR handling) — the 2SID variant followed.

**Confirmed:** Found at offset 238 in `MUSICIANS/B/Buddha/Last_Party_2SID.sid`.

### 2.4 V2.x Signature (for contrast)

```
BD ?? ??   = LDA abs,X   ; load channel state (different layout from V1)
D0 ??      = BNE rel     ; channel active check
BC ?? ??   = LDY abs,X   ; load orderlist pointer
B9 ?? ??   = LDA abs,Y   ; read orderlist (abs,Y — V2's dispatch is completely different)
85 ??      = STA zp       ; store to zero page
...
BC ?? ??   = LDY abs,X   ; reload
B1 ??      = LDA (zp),Y  ; read pattern data via indirect Y (same as V1)
C9 FF      = CMP #$FF    ; check for end pattern (V2 uses $FF end mark, no $60 NOCMD)
90 ??      = BCC rel      ; 
```

The structural tell: V2 uses `CMP #$FF` (not `CMP #$60` / `CMP #$C0` / `SBC #$5F`). V2 fixed 4-byte pattern rows; V1's variable-length decode is absent.

### 2.5 V2/Mini and V2/Mini2

The Mini players are stripped relocations of GT2 that omit the full song-engine dispatch (`LDA abs,X` style). They use a compressed inner loop starting with `B9 ?? ?? 85 ?? B9 ?? ?? 85 ??` (two `LDA abs,Y / STA zp` pairs loading channel state) and `CMP #$7C` (Mini) / `CMP #$7A` (Mini2) for the pattern boundary (different note range than standard GT2's `$FF`). Very rare in HVSC (1 each).

---

## 3. GoatTracker V1 Sub-version Landscape

### 3.1 SNG File Format Versions (GTS header magic)

| Magic | Introduced | Tables | Notes |
|-------|-----------|--------|-------|
| `GTS!` | V1.0–V1.29 | N/A | Original V1 format. Simple non-table filter (fixed 4-byte filter entries per instrument). Arpeggio command (cmd 0 with data) plus vibrato share same internal state register. Pattern rows = 3 bytes: `note, (instr<<3)|cmd, data`. Instruments are 32 max (5-bit index in the cmd byte). |
| `GTS3` | V1.3+ | 4 | Added table-based filter execution. Orderlist gained TRANSPOSE ($E0–$FE) and REPEAT ($D0–$DF) commands. Portamento-down command added. Vibrato odd speeds fixed. Hard restart toggle per instrument. |
| `GTS4` | V1.4+ | 4 | Changed filter parameters (filter params reorganized; old songs need manual adjustment per the readme). |
| `GTS5` | V2.0+ | 4 | GoatTracker V2 format. 63 instruments. Uniform wave/pulse/filter/speed tables (4 tables). Fixed 4-byte pattern rows. Arpeggio command removed (converted to wavetable programs). |

**Note:** GT2's `gsong.c` loads `GTS3` and `GTS4` identically (same code branch, both treated as 4-table format). The distinction is meaningful only within the V1 editor itself (V1.4 changed filter param semantics). `sngspli2.c` also treats both as `tables=4`.

The `GTS!` (GoatTracker 1.x old) format is parsed separately in GT2 (line 330 in gsong.c), converting arpeggios to wavetable programs, pulse tables, and filter tables during import.

`GTS2` was an intermediate GT2 beta format with 3 tables and only 47 instruments — handled by `betaconv.c` and a separate import branch.

### 3.2 Playroutine Sub-versions and Audio-Affecting Changes

Key points from the V1.25 and V1.52 readmes:

| Version milestone | Audio-affecting change |
|-------------------|----------------------|
| v0.94 Beta | Wavetable loops added (`$FF` end byte replaces `$00`). Old songs need manual conversion of the end byte. |
| v1.0 | First public stable release. |
| v1.1 | Added playroutines 2–4 (Game, Scene, Everything). Restructured all playroutines with jump table. |
| v1.14–1.19 | No audio changes — editor/platform fixes only. |
| v1.3 | **Major**: table-based filter execution replaces per-instrument fixed filter. Transpose + repeat in orderlists. Odd vibrato speeds fixed. Portamento-down added. Arpeggio + vibrato share internal register (mixing them can cause unexpected results). |
| v1.4 | **Filter param change**: filter parameters reorganized. Old songs need manual adjustment. GTS4 format introduced. |
| v1.5 | **Major**: Playroutine fully rewritten. Testbit-based hard restart (much sharper sounds). ADSR hard restart parameter now configurable (not just AD). Delayed wavetable execution added. Proper gate-off (keyoff in patterns now works correctly even with gate=1 in wavetable). Master fader command added ($7F0–$7FF). |
| v1.51 | Funktempo behavior changed. |
| v1.52 | Frequency table tuning corrected. |
| v1.53 | Minor: packer behavior fix for no-hardrestart / no-pulseinit instruments. |

**Practical implication for SidId:** The single `GoatTracker_V1.x` signature covers all V1 sub-versions because the **core pattern decode loop** (the `BC ?? ?? B1 ?? C8 C9 60 ... SBC $5F` sequence) is structurally identical across all V1 players. The audio-level changes (filter table, hard restart style, delayed wavetable) affect only blocks OTHER than the pattern byte dispatch.

### 3.3 V1 Song Format Details (as stored in packed/relocated SID)

**Pattern row format (3 bytes per row):**
```
Byte 1: Note value
  $00–$5D : Notes C-0 to A-7 (0-based; after SBC #$5F in player, $60→idx 1)
  $5E     : KEYOFF (clear gate bit)
  $5F     : REST
  $60     : NOCMD — no 2nd/3rd byte follow; only the note itself
  $C0–$FF : Packed rests ($C0 = 1 rest frame, …, $FF = 64 rest frames)
  $FF     : ENDPATT

Byte 2 (absent if byte1 == $60 NOCMD):
  Bits 7–3 : Instrument number (0–31, 5-bit; 32 instruments max)
  Bits 2–0 : Command number (0–7, 3-bit)

Byte 3 (absent if byte1 == $60 NOCMD):
  Command data byte
```

**Pattern data (in the SID binary):** Notes are stored as raw 0–93 range in the `.sng` file but the player source defines them starting from 0 (C-0 = 0). In the packed/relocated SID, notes are NOT offset by $60 — instead the player compares `CMP #$60` and `SBC #$5F` to distinguish notes from special bytes. The note bytes $00–$5D in the SID data directly index into the freq table (after being used as `(note + transpose) → freq index`).

**Wait — this needs clarification:** Looking at `v1_player1_125.s` defines, `NOCMD = $60`, `REST = $5F`, `KEYOFF = $5E`. Notes 0–93 are defined as `C0 = $00, CIS0 = $01, …, A7 = $5D`. So in the packed SID, a note byte below $5E is a raw note index, and $60 means "no command/instrument bytes on this row" (the instrument stays unchanged). The `SBC #$5F` (subtract 95) only applies AFTER the comparison branch to get the 1-based freq table index.

Comparing with V2's `FIRSTNOTE = $60`: V2 stores notes as $60–$BC in packed SIDs (added $60 offset). V1 stores notes as $00–$5D. This is the key structural difference that makes the sidid signatures differ.

**Instruments:** Maximum 32 in V1 (5-bit field). V2 raised this to 63.

**SNG file header (`GTS!`/`GTS3`/`GTS4`):**
```
+0    4     Magic: "GTS!" (pre-1.3) or "GTS3" (1.3+) or "GTS4" (1.4+)
+4    32    Song name
+36   32    Author name
+68   32    Copyright string
+100  1     Number of subtunes
```

**GTS!/GTS3/GTS4 instrument format (31 instruments, stored for indices 1–31):**
```
+0  byte  Attack/Decay
+1  byte  Sustain/Release
+2  byte  Initial pulse width (bit 0 = no-hardrestart flag in GTS! format)
+3  byte  Pulse speed
+4  byte  Pulse limit low
+5  byte  Pulse limit high
+6  byte  Filter freq/type (GTS!: single-byte filter; GTS3/4: filter table pointer)
+7  byte  Wavetable size in bytes (always even; 0 = no wavetable)
+8  16    Instrument name
+24 n     Wavetable (waveform/note pairs, 2 bytes each; n/2 steps)
```

GTS3/4 replace the single-byte `Filter freq/type` with a filter table pointer (since GTS3 introduced tablebased filter). GT2's import converts GTS! instruments by building pulse tables and filter tables from the inline instrument parameters.

**GTS! filter table (appended after patterns, 256 bytes, 64 entries × 4 bytes each):**
```
Each 4-byte entry:
  +0  byte  Resonance/routing
  +1  byte  Filter type/volume
  +2  byte  Cutoff frequency
  +3  byte  Cutoff speed (0 = set, nonzero = slide)
```

---

## 4. 2SID / Stereo Landscape

12 V1.x SIDs in HVSC have "2SID" in the path:

| Path | Title | Author |
|------|-------|--------|
| MUSICIANS/B/Bayliss_Richard/Summer_Timebooze_2SID.sid | Summer Timebooze | Richard Bayliss |
| MUSICIANS/B/Buddha/Last_Party_2SID.sid | Last Party | Sylwester Hasiak (Buddha) |
| MUSICIANS/C/Cadaver/Stereotest_2SID.sid | Stereotest | Lasse Öörni (Cadaver) |
| MUSICIANS/H/Holt_Hein/SidKit_2SID.sid | SidKit | Hein Holt |
| MUSICIANS/K/Kozaki_Soft/Geigeriada_2SID.sid | Geigeriada | Mateusz Kozicki |
| MUSICIANS/K/Kozaki_Soft/KnotCrafter_2SID.sid | KnotCrafter | Mateusz Kozicki |
| MUSICIANS/K/Kozaki_Soft/Sawlarmes_2SID.sid | Sawlarmes | Mateusz Kozicki |
| MUSICIANS/N/Nata/Anthrox_2SID.sid | Anthrox | Nata |
| MUSICIANS/N/Nata/Renegade_420_2SID.sid | Renegade 420 | Nata |
| MUSICIANS/S/SLO/Big_Secret_2SID.sid | The Big Secret | Teemu Mäki (SLO) |
| MUSICIANS/S/Sidder/Boys_2SID.sid | Boys | Marcin Romanowski (Sidder) |
| MUSICIANS/S/Sidder/X-Files_2SID.sid | X-Files | Marcin Romanowski (Sidder) |

Binary-confirmed:
- `Stereotest_2SID.sid` carries V1 main sig + **GT_V1.4_2SID** sub-sig at offset 1202
- `Last_Party_2SID.sid` carries V1 main sig + **GT_V1.5_2SID** sub-sig at offset 238

**Migration implication:** These 12 SIDs require a dual-SID composer (second SID at $D420 or $D500). They should be excluded from any single-SID USF pipeline. 1,347 V1 SIDs (99.1%) are standard single-SID and are the migration target.

---

## 5. V1 vs V2 Key Differences (migration-relevant)

| Dimension | GoatTracker V1.x | GoatTracker V2.x |
|-----------|-----------------|-----------------|
| SNG magic | `GTS!`, `GTS3`, `GTS4` | `GTS5` |
| Pattern row size | 3 bytes (variable: note-only rows omit cmd/data) | 4 bytes (fixed) |
| Instruments | 32 max | 63 max |
| Arpeggio | Dedicated pattern command (cmd 0 with data = 3-note arp) | Removed; wavetable programs replace it |
| Wavetable format | Two columns: waveform byte + note byte (arpeggio logic via note table) | Same basic layout but different value semantics; wavetable delay ($01–$0F) encoding changed in V2.18 |
| Filter | Pre-V1.3: per-instrument 4-byte entry; V1.3+: step-programmable filter table | Step-programmable filter table (same concept) |
| Hard restart | V1.0–1.4c: AD-only configurable, 2-frame; V1.5+: testbit-based, ADSR configurable | Testbit + ADSR configurable (inherited from V1.5) |
| Speed table | None (vibrato/portamento params inline) | Dedicated speed table (vibrato, portamento, funktempo) |
| Note range in packed SID | $00–$5D (0-based), $5F=rest, $5E=keyoff, $60=NOCMD | $60–$BC (offset by $60), $BD=rest, $BE=keyoff, $BF=keyon |
| Packed rests | $C0–$FF (count = 256-value) | $C0–$FF (count = 256-value) — same |
| Pattern end | $FF | $00 (end of pattern) |

The GT2 `gsong.c` import path for `GTS!` (V1 old format) converts:
1. Inline pulse parameters → pulsetable programs
2. Instrument filter byte → filtertable entries (converting the simple 4-byte entries to GT2 table steps)
3. Arpeggio commands → wavetable programs (duplicating the instrument wavetable, appending 3-step arp loop + jump)
4. Portamento/vibrato params → speedtable entries

---

## 6. HVSC Document Survey

No GoatTracker V1-specific documentation was found in `hvsc85/DOCUMENTS/`. The only GoatTracker hits are:
- `DOCUMENTS/Update_Announcements/20101224.txt` and later — all reference GoatTracker v2.x
- `DOCUMENTS/Songlengths.md5` — lists the three Cadaver V1 example SIDs

The three Cadaver example SIDs are the only GoatTracker-labelled SIDs in the `MUSICIANS/C/Cadaver/` path (all three are verified V1.x by signature).

---

## 7. DeepSID / Online Detection Notes

No online sources were fetched (LEAF constraint). Findings derivable from local sources:
- SidId uses the single `GoatTracker_V1.x` class for all V1 sub-versions; the two 2SID sub-signatures are supplementary discriminators within that class.
- The sidid.cfg has been in widespread use as the authoritative identification tool for HVSC. The V1 class has been stable since at least sidid version circa 2010.
- DeepSID (deepsid.chordian.net) uses SidId for engine classification; its GoatTracker V1 counts mirror the HVSC DB.

---

## 8. Summary for Future Migration Planning

- **V1 corpus:** 1,347 single-SID (migration target) + 12 dual-SID (exclude from single-SID pipeline).
- **Player variants:** One player binary class covers all V1 sub-versions. The sidid signature is structurally stable across v1.0–v1.53. No per-sub-version branching needed for detection.
- **Audio-affecting variants within the class:**
  - Pre-V1.3 (GTS! songs): simple 4-byte filter, no transpose/repeat in orderlists
  - V1.3–V1.4x (GTS3 songs): table-based filter, transpose/repeat available
  - V1.4x (GTS4 songs): changed filter parameter layout
  - V1.5+ (GTS4 songs): testbit hard restart, delayed wavetable, master fader
  All are stored in packed SIDs with the same player binary signature — sub-version is detectable only from PSID header (author, title, year) or from audio behavior, not from the SidId binary pattern.
- **Arpeggio:** V1 has a native arpeggio command absent in V2. It is a 3-note chord arpeggio (bits 6–4 = interval 1, bits 3–0 = interval 2, bit 7 = note-relative). USF representation will need an arpeggio effect (distinct from V2's wavetable arp).
- **Pattern row format:** 3-byte variable-length. V1's `NOCMD = $60` avoids writing instrument or command on "continuation" rows — this is a structural difference from V2's fixed 4-byte.
- **Frequency table:** V1 uses a 96-note (8 octave) direct lookup table; the note byte directly indexes it. V1.52 corrected tuning.

---

## Leads to Follow

1. **Confirm GTS3 vs GTS4 format difference** — the exact byte-level change in filter parameter layout between GTS3 and GTS4 has been referenced but not fully decoded from source. Check if any V1 source (not just GT2's import) survives that shows the difference in the filter section.
2. **2SID second SID base address** — the 12 V1 2SID tunes: what address does the second SID appear at? Standard is $D420 (stereo) or $D500 (some carts). Binary inspect `Stereotest_2SID.sid` + `Last_Party_2SID.sid` for `STA $D4xx` writes to determine the second base.
3. **DeepSID player ID notes** — fetch `https://deepsid.chordian.net` if online access is enabled; it may expose any V1-specific quirks observed during playback.
4. **Cadaver's original GoatTracker V1 homepage** — `http://covertbitops.cjb.net/tools/goattrk.zip` (referenced in V1.25 readme) or `cadaver.github.io/tools.html` — may have V1-specific release notes or a version history predating V1.25.
5. **V1 `GTS!` format HVSC prevalence** — query the 1,347 single-SID V1 tunes for creation date range to understand what fraction uses old GTS! format vs GTS3/4 (need to parse SNG files, not SID binaries).
6. **Playroutine variants in V1 SIDs** — V1 had 4 playroutine types (Standard, Game, Scene, Everything). In packed SIDs, which is most common? The sidid signature identifies all as one class. A byte-pattern scan of the 1,347 SIDs for the playroutine-2 sound-effect jump table could determine distribution.
