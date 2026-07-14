<!--
provenance:
  source_url:
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/exporter.asm
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/SWM-spec.src
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/include/player.asm
    - https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/editor.asm
  local:
    - hvsc84/MUSICIANS/C/Czyszy/ChipMotif.sid        (decoded — primary worked example, DRIVERTYPE=0/NORMAL, v1.7)
    - hvsc84/MUSICIANS/H/Hermit/Magyar_Nepzenek.sid  (decoded — Hermit, 5 subtunes, v1.4)
    - hvsc84/MUSICIANS/S/Slaxx/Bassloop.sid          (decoded — v1.8)
    - hvsc84/GAMES/G-L/Ill_Savior.sid                (decoded — v1.7 variant)
    - deprecated/gt2_pipeline/tools/sidid.cfg        (sidid signatures, read-only)
    - hvsc84.db                                      (census, read-only)
  fetched_via: WebFetch (raw.githubusercontent.com) + siddump --writelog + Python binary decode
  fetch_date: 2026-06-13
  author: Mihály Horváth (Hermit) — SID-Wizard player/exporter; SWM-spec.src $Id rev 382 (2014-06-23); player.asm $Id rev 390 (2014-07-22)
  content_date: source ~2012–2022 (V1.0–V1.92); SWM-spec/player asm pinned to 2014 SVN revs on the anarkiwi mirror's master branch
  reliability: HIGH for verbatim equates + PSID header + sidid sigs + decoded binary layout (cross-checked source vs 4 real HVSC binaries vs siddump ground truth). MEDIUM where flagged OPEN (exact per-driver data pointer-table offsets; lean-path source not fully recovered through the WebFetch summariser).
-->

# SID-Wizard — Binary → USF Extraction Plan

Target engine: **`Hermit/SidWizard_V1.x`** (HVSC engine label). Census from `hvsc84.db`
(`engine='Hermit/SidWizard_V1.x'`):

| Slice | Count |
|---|---|
| Total SID-Wizard tunes | **1048** |
| `psid_version=2` (1-SID) | 1010 |
| `psid_version=3` (2-SID) | 29 |
| `psid_version=4` (3-SID / 4-SID) | 9 |
| `load_addr=$0000` (PSID "original format") | **1048 (all)** |
| `init=$1000` / `play=$1003` | 775 |
| **In-scope primary target: `psid_version=2 AND init=$1000`** | **739** |
| PSID `speed` word `0x00000000` (vblank, all) | 992 |
| PSID `speed` word `0x00000001` (CIA on subtune 1) | 56 |

**Decisive verification-mode fact:** all 739 primary-target tunes have **`speed == 0`** →
vblank 50 Hz → **flat Mode-1 per-frame verdict** (`compare_instruction_stream`, no per-IRQ).
The 56 `speed=0x1` tunes use CIA on subtune 1 (multispeed exports) → those subtunes need the
`--writelog-per-irq` path. **No tune in the family sets any speed bit beyond bit 0.** This
*contradicts the BACKGROUND's "CIA-based multispeed" generalisation*: the exporter's
source default is `SIDtimerTyp .byte $FF,$FF,$FF,$FF` (CIA-all), but real HVSC exports are
overwhelmingly vblank. **Always read the actual speed word; never assume CIA.**

---

## 0. The exported binary is PSID "original format"

Verbatim PSID header emitted by `exporter.asm` (the `;+NN` are header byte offsets):

```asm
;SID v1 header - big endian (!!!) WORD (byte-pair) values most of the time
        .text "psid"                          ;+00 magicID
        .byte $00,(SID_AMOUNT==1)? $02:$03     ;+04 version  (1-SID => $0002, multi => $0003)
        .byte $00,$7C                          ;+06 dataOffset  ($007C, v2 header)
        .byte $00,$00                          ;+08 loadAddress (0 => data starts with a 2-byte LE load addr)
SIDinitadd .byte >CIAINIT,<CIAINIT             ;+0A initAddress
SIDplayadd .byte >CIAPLAY,<CIAPLAY             ;+0C playAddress
SIDstamount .byte $00,$01                       ;+0E songs
SIDdefasubt .byte $00,$01                       ;+10 startSong
SIDtimerTyp .byte $FF,$FF,$FF,$FF               ;+12 speed (32-bit BE; bit=1 => CIA)   <-- source default; HVSC mostly $00000000
SIDtitletx .fill $20,0                          ;+16 title (32B)
SIDauthrtx .fill $20,0                          ;+36 author
SIDreleatx .fill $20,0                          ;+56 released
SIDflags .byte %00000000                        ;+76 flags hi
           .byte (SID_AMOUNT==1)? %00100100 : %10100100  ;flags lo (mono=$24: PAL + 6581)
```

Confirmed against real binaries (`ChipMotif`, `Magyar_Nepzenek`, `Bassloop`):
`magic=PSID, ver=$0002, dataOffset=$7C, loadAddress=$0000, init=$1000, play=$1003, flags=$0024`.

**Extraction consequence:** `load_addr` field is 0 → the **real C64 load address is the first
two bytes of the data area** (little-endian). For all 1048 tunes that is **`$1000`** when
not relocated; other inits seen ($0FB8, $0C00, $E000, …) are relocated exports of the same
player. Read it; do not hardcode.

`flags` lo-byte distribution (PAL everywhere; SID-model & SID2/SID3 bits vary):
`$24`×858, `$14`×110, `$A4`×26 (bit7 set ⇒ 2-SID), `$18`×21, `$34`×15, `$2A4`×8, `$28`×5.

---

## 1. Anchor the player (two anchors; prefer SWM-magic)

### 1a. Jump table at the load address (verbatim, ChipMotif @ $1000)

```
$1000: 4C 9C 10   JMP $109C   ; init  (PSID initAddress = load+0)
$1003: 4C F1 10   JMP $10F1   ; play  (PSID playAddress = load+3)
$1006: 4C 36 11   JMP $1136   ; 2nd play entry (single-speed / no-advance variant)
$1009: 4C 25 19   JMP $1925   ; 4th entry
$100C: 80 01 20   (flags / PLAYERID bytes)
$100F: "SID-WIZARD 1.7 " 00 00      ; version signature string
$1020: "SWM1" 01 04 01 01 FF FF FF 20 03 03 05 07 …   ; embedded SWM header (see §2)
```

So the player begins with **3–4 `JMP abs` vectors** at the load address. `init = load+0`,
`play = load+3`. (For relocated tunes the absolute targets shift but the relative shape holds.)

### 1b. Version-string signature (informational, NOT reliable as the sole anchor)

The player carries an ASCII string `"SID-WIZARD <ver>"`. **Offset and exact form vary by version**:

| Tune | string | string offset | SWM magic offset |
|---|---|---|---|
| `4_Emelet` / `Acting_Up` | `SID-WIZARD 1.4 ` | load+$0E | $1020 |
| `ChipMotif` | `SID-WIZARD 1.7 ` | load+$0F | $1020 |
| `Ill_Savior` | `SID-WIZARD 1.7SWM1` | load+$12 | $1020 |
| `Bassloop` | `SID-WIZARD 1.8 SWM` | load+$12 | $1021 |
| `1_Raster_Tracker_Demo`, 3SID demos | *(none)* | — | — |

⇒ Use the string to **read the version** when present, but it is **absent on some
(bare/custom/relocated) builds**.

### 1c. sidid byte-signatures (verbatim, `deprecated/gt2_pipeline/tools/sidid.cfg`)

These are the reloc-invariant code fingerprints (`??` = wildcard byte; matches the play loop /
ghost-flush). Use as the authoritative engine + variant classifier:

```
Hermit/SidWizard_V1.x
(SidWizard_V1.0) F0 04 C0 60 90 03 4C ?? ?? BC END
(SidWizard_V1.2) 0A 0A 0A 0A 8D ?? ?? C8 B1 ?? 8D ?? ?? A9 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? C8 98 8D END
(SidWizard_V1.4) 48 20 ?? ?? 68 4C ?? ?? 20 ?? ?? A0 ?? 71 ?? 9D ?? ?? 60 20 ?? ?? A0 ?? 71 ?? 8D ?? ?? 60 9D ?? ?? 60 END
(SidWizard_V1.5) 60 A0 ?? 20 ?? ?? 4C ?? ?? A0 ?? B1 ?? 29 30 9D ?? ?? 60 0A 9D ?? ?? 60 8D ?? ?? 8D ?? ?? 60 0A 0A 0A 0A END
(SidWizard_V1.?) A0 ?? B1 ?? 9D ?? ?? 2C ?? ?? 30 ?? A0 ?? B1 ?? A8 E0 ?? 90 ?? B1 ?? F0 ?? C9 FF F0 END
(SidWizard_2SID) B1 ?? 9D 05 D4 C8 B1 ?? 9D 06 D4 A9 ?? 9D ?? ?? 3D ?? ?? 9D ?? ?? 9D 04 D4 60 END
(SidWizard_3SID) A0 ?? 99 ?? ?? 88 10 ?? A0 ?? 99 00 D4 99 ?? ?? 88 END
            (and) A0 ?? 99 ?? ?? 88 10 ?? A0 ?? 99 00 D4 99 ?? ?? 99 END
```

(Note: the labels are slightly mis-assigned in the cfg — the `9D 05 D4 / 9D 06 D4 / 9D 04 D4`
pattern is the **lean 1-SID per-voice emitter**, and the `99 00 D4` descending-loop patterns are
the **multi-SID ghost-flush** = `COMMONREGS` `ALLGHOSTREGS_ON` path; see `spec_write_model.md`.)

---

## 2. Embedded SWM header (the metadata block) — verbatim offsets

The exporter **embeds an `"SWM1"`/`"SWMS"` 64-byte header** just after the jump table +
version string (≈ load+$20). Parse it per `SWM-spec.src` (verbatim equates):

```
00..03 : "SWM1" (mono) / "SWMS" (stereo)     ; ID
FSPEEDPOS        = 4    ;//frame-speed (1..8)
SWM_HILI_POS     = 5    ;//converter only
SWM_AUTO_POS     = 6    ;//obsolete in SWM1
SWM_CBIT_POS     = 7    ;//obsolete in SWM1
SWM_MUTE_POS     = 8    ;//(3 bytes 8,9,10) mute switches
SWM_DEFP_POS     = 11   ;//$B default pattern-length
SEQAMOPOS        = 12   ;//$C  amount of sequences (per channel)
PTAMOUPOS        = 13   ;//$D  amount of patterns
INSTAMPOS        = 14   ;//$E  amount of non-empty instruments
CHRDLEPOS        = 15   ;//$F  length of packed chordtable
TMPLENPOS        = 16   ;//$10 length of packed tempoprogram-table
COLORTHEMEPOS    = 17   ;//$11 obsolete
KEYBOARDTYPE_POS = 18   ;//$12 obsolete
DRIVERTYPE_POS   = 19   ;//$13 player/driver type (info only): light/medium/full/extra/bare/demo
TUNINGTYPE_POS   = 20   ;//$14 0:440Hz normal, 1:432Hz Verdi, 2:Just-intonation (key of C)
AUTHORPOS        = 24   ;//$18 author string (40 bytes, to header end $3F)
tuneheadersize   = 64   ;//$40 (don't modify)
```

Worked example — ChipMotif header at $1020 (verbatim bytes):
```
53 57 4D 31 01 04 01 01 FF FF FF 20 03 03 05 07 00 00 00 00 ...
"SWM1"      ^1 ^4 ^1 ^1 ^mute   ^32 ^3 ^3 ^5 ^7  ^tempo=0 ^theme/kb/drv/tuning all 0
```
⇒ FSPEED=1, default-patlen=$20, 3 sequences, 3 patterns, 5 instruments, chordtbl-len=7,
tempo-len=0, **DRIVERTYPE=0 (NORMAL)**, TUNING=0 (440 Hz). Confirmed by parser.

`DrvType` encoding (verbatim from `editor.asm`):
```asm
DrvType .byte 0 ; type of music player/driver (0=NORMAL, 1=MID, 2=LIGHT, 3=EXTRA, 4=BARE)
```
(`SWM-spec.src` lists the human set as light/medium/full/extra/bare/demo; the numeric map above is
what the exporter stores. **OPEN:** reconcile the "demo"/"full" names with the 0–4 codes — confirm
by exporting from the editor or by reading `startupmenu.inc`.)

### SWM static limits (verbatim, for sanity-checking parsed counts)

```asm
maxsubtuneamount=8-1   ;//max $1F
maxptnamount=100       ;//maximum number of patterns
maxinstamount=36+1     ;//37 instruments
seqlength=126          ;//$7e  max sequence length in orderlist
seqbound=128           ;//$80
maxptnlen=250-1        ;//$f9 (249) max pattern size in bytes
PTNBOUND=256           ;//$100
maxinstsize=128        ;//$80 per-instrument memory
instnamelength=8       ;//DON'T MODIFY
MAXCHORDAMOUNT=64      ;//$40
maxchordlength=32      ;//$20
ChordTableLen=256      ;//$100
MAXTEMPOPRAMOUNT=64    ;//$40
maxtempolength=32      ;//$20
TempoTableLen=128      ;//$80
SUBTUNE_MAX=31  PATT_MAX=127  INSTR_MAX=62
SWM_NOTE_MAX=95        ;//$5F
```

---

## 3. Locate the playable data sections

⚠ **KEY LAYOUT FACT (verified on the binary):** the bytes *immediately after* the embedded
64-byte SWM header are **NOT** a tight native-`.swm` concatenation. ChipMotif's header ends at
$1060; the first ~36 bytes there are `00`, and the real sequence stream (`01 FE 02 …`) starts
~$1084. The exporter (`exporter.asm::preparetunedata`) **re-lays-out the data into fixed-size /
pointer-indexed regions** and the player reads them through **self-modified pointer tables**, not
by walking the SWM header counts. So:

- The embedded `"SWM1"` header is **authoritative for COUNTS, DRIVERTYPE, TUNING, FSPEED** —
  read those from it.
- The **data bytes** (sequences / patterns / instruments / chord / tempo) must be located via the
  **player's pointer tables**, whose base addresses are fixed *per driver-variant + version* and
  computed at export time.

### What the player code tells us (verbatim, ChipMotif)

`init` ($109C) — clears chip + copies workspace:
```
$109C: 20 61 16     JSR $1661
       A9 00        LDA #$00
       A0 68        LDY #$68
       99 1E 10     STA $101E,Y     ; zero the workspace region near the header
       88 / 10 FA   DEY / BPL
       A0 17        LDY #$17        ; =23
       99 00 D4     STA $D400,Y     ; <-- CLEAR $D400..$D417 (the init reset, see write-model §init)
       88 / 10 FA   DEY / BPL
```

`play` ($10F1) — per-voice dispatch in **descending voice order**:
```
$10F1: A5 FE / 48 / A5 FF / 48     ; save ZP $FE,$FF
       A2 0E   LDX #$0E   ; =14  -> channel-3 base (2*7)
       20 73 11  JSR $1173        ; process channel 3
       A2 07   LDX #$07   ; =7   -> channel-2 base
       20 73 11  JSR $1173
       A2 00   LDX #$00   ; =0   -> channel-1 base
       20 73 11  JSR $1173
       ...
$1136: (2nd play entry) calls JSR $114E per channel (same X=$0E,7,0 order)
```

⇒ The per-channel routine is at a fixed offset (here `$1173`); it reads the channel's pattern /
sequence / instrument via ZP pointers `$FE/$FF` (`PLAYERZP`) that are set from the **pointer
tables**. The pointer-table symbols (from player.asm, names confirmed via exporter refs):
`ptnptloadd / ptnpthiadd` (pattern lo/hi), `insptloadd / inspthiadd` (instrument lo/hi),
plus sequence, `chordptadd`, `chordtbadd`, `tempoptadd`, `tempotbadd`, `subtuneadd`.

### Extraction recipe for the data (per binary, robust)

1. Parse the SWM header → counts (`SEQAMOUNT`, `PATAMOUNT`, `INSTAMOUNT`, `CHRDLEN`, `TMPLEN`),
   `DRIVERTYPE`, `TUNING`, `FSPEED`, `DEFPATLEN`.
2. Disassemble/scan the player to recover the **pointer-table base addresses** the player loads
   into `PLAYERZP` (look for the lo/hi table reads feeding `STA $FE / STA $FF` before the
   `JSR $1173`-style per-channel call; and the `LDA tbl,X / STA selfmod+1` self-mods).
   The tables are *contiguous lo-byte then hi-byte arrays* of length = the matching count.
3. From each pointer pair, read the data block until its terminator (sequences/patterns are
   `$FF`/`$FE` terminated; instrument WF/PW/filter tables are `$FF`-terminated — see §4–6).
4. Cross-check parsed block bounds against the SWM limits (§2) and against the next pointer.

**OPEN (must close before coding the extractor):** exact byte offsets of each pointer table
relative to the load address, *per DRIVERTYPE (0..4) and per version (1.0/1.2/1.4/1.5/1.7/1.8/…)*.
Close by: (a) seeding `tools/seed_disassembly.py` on ChipMotif (DRIVERTYPE=0, v1.7) and
hand-annotating the pointer-load sites at `$1173`/`$114E`; (b) repeating for one tune of each
DRIVERTYPE; (c) recording the offsets as a per-(version,driver) table. The player source labels
to grep for are `ptnptloadd`, `inspthiadd`, `chordptadd`, `tempoptadd`, `subtuneadd`.

---

## 4. Decode INSTRUMENTS (16-byte base + variable tables)

Base record offsets (verbatim equates, relative to instrument base):

```asm
;byte 0  = control  (bit0-1:HRtimer, bit2:HRgateoff, bit3:TestbitHR,
;                    bit4-5:vib.type, bit6:pulseresetOFF, bit7:filtresetOff)   [from player comment]
;byte 1-2 = HR-ADSR (hard-restart ADSR word)
SWI_AD_POS         = 3   ;//Attack/Decay
SWI_SR_POS         = 4   ;//Sustain/Release
SWI_INSVIBRATO_POS = 5   ;//vibrato (hi nib amplitude, lo nib frequency)
SWI_VIBDELAY_POS   = 6   ;//vibrato delay / amplitude-increment speed
SWI_ARP_SPEED_POS  = 7   ;//arp/chord speed; bit6=>multispeed-PW, bit7=>multispeed-filter
SWI_DEFCHORD_POS   = 8   ;//default chord
SWI_OCTAVE_POS     = 9   ;//octave shift (2's-complement transpose)
SWI_PULSETBPT_POS  = 10  ;//$A pulse-width table pointer
;byte $B = filter table pointer
;byte $C = gate-off WF pointer ; byte $D = gate-off PW pointer ; byte $E = gate-off filter pointer
;byte $F = first-frame waveform
WFTABLEPOS         = 16  ;//$10 WF-ARP table base, relative to instrument base
```

After the 16-byte base: **WF-ARP table**, then **PW table**, then **filter table**, each
`$FF`-terminated. (Per `maxinstsize=128`, one instrument ≤ $80 bytes total.)

The multispeed bits on byte 7 (verbatim from player.asm):
```asm
        ldy #7          ;CHECK ARPSPEED DATA OF CURRENT INSTRUMENT (BIT 6 & 7)
        lda (PLAYERZP),y
        bmi MULTIFI     ;BIT7=1 => MULTISPEED FILTER TOO
        and #$40        ;BIT6=1 => PULSEWIDTH MULTISPEED TOO
```

→ USF mapping: control bits = the four hard-restart / reset flags (see write-model §HR);
AD/SR = ADSR; vibrato = (amplitude, frequency, delay) → standard USF vibrato; arp/chord-speed +
default chord + WF-ARP table → USF arp/wavetable; PW table → USF pulse program; filter table →
USF filter program; octave shift → USF transpose; first-frame waveform → USF note-on waveform.
**Apply the USF representation principle — these are parametric basis effects, not an indexed
library.** (Re-read `docs/the_principle.md` before designing the instrument USF.)

---

## 5. Decode PATTERNS (verbatim opcode map)

Pattern rows have up to 4 columns (Note/FX, Instrument/SmallFX, BigFX, FX-value). The hardwired
note-column effect values (verbatim from `SWM-spec.src`, "PATTERN-EFFECT values …
NOT TO MODIFY THESE, HARDWIRED VALUES"):

```asm
SWM_NOTE_MAX = 95   ;//$5F  maximum note-value      (so $00..$5F = notes; $00 commonly "no note")
VIBRATOFX    = 96   ;//$60  base of vibrato-effect
PACKEDMIN    = 112  ;//$70  min value = 2 packed NOPs
PACKEDMAX    = 119  ;//$77  max value = 9 packed NOPs   (so $70..$77 => 2..9 empty rows)
PORTAMFX     = 120  ;//$78  auto-portamento note-effect
DEFAULTPORTA = 110  ;//      auto-portamento default speed
SYNCONFX     = 121  ;//$79  sync ON
SYNCOFFX     = 122  ;//$7A  sync OFF
RINGONFX     = 123  ;//$7B  ring ON
RINGOFFX     = 124  ;//$7C  ring OFF
GATEONFX     = 125  ;//$7D  gate ON (note-start)
GATEOFFX     = 126  ;//$7E  gate OFF (note-mute)
```

Instrument column: `$01..$3E` select instrument; `$3F` = **legato** (BACKGROUND; `INSTR_MAX=$3E`
confirms the range). Pattern terminator: `$FF`. (BigFX / FX-value column semantics: **OPEN** —
the `$60` vibrato + `$78` porta take a parameter from the value column; confirm the per-effect
value encoding from the per-channel routine `$1173` or the editor's pattern editor. Mark
version/driver-dependent: BigFX support is a feature flag, absent in bare/light drivers.)

---

## 6. Decode SEQUENCES (orderlist) — opcode map

Per-channel orderlist. Opcode ranges (BACKGROUND; **note: these are NOT in `SWM-spec.src`** —
they live in player/editor code, marked OPEN to verbatim-confirm):

```
$01..$7F : pattern number to play       (PATT_MAX=$7F theoretical)
$80..$9F : transpose ($90 = no transpose; $80..$8F down, $91..$9F up)
$A0..$AF : track volume
$B0..$EF : track tempo
$FE      : end (loop)
$FF      : jump  (followed by a 2-byte target — the loop point)
```

In the export, each stored sequence is **size-prefixed** by `depkptseq` ("all expanded with its
1-byte size-info" — verbatim paraphrase from `SWM-spec.src`'s sequence note), then the player
walks it with the pointer table. The loop target ($FF) is an absolute address in the export.

→ USF mapping: per-channel orderlist with `Orderlist.transposes` (transpose), volume, and tempo
as sequence commands; `$FF` jump = the loop point. Multi-channel orderlists realign at their
loop points (standard tracker semantics).

**OPEN:** verbatim-confirm the $80/$90/$A0/$B0 boundaries and whether `$FF` target is absolute or
SWM-relative in the *export* — close by decoding ChipMotif's sequence region after recovering the
sequence pointer table (§3).

---

## 7. Driver-variant & version dependence (affects BOTH layout and write stream)

- **DRIVERTYPE (byte $13 of header; 0=NORMAL,1=MID,2=LIGHT,3=EXTRA,4=BARE):** selects which
  `feature.*_ON` flags are compiled → changes (a) which instrument features exist (vibrato types,
  chord support, tempo programs, filter-reset switch, frame-1 waveform switch, hard-restart types)
  and (b) **the per-frame SID write order / which registers are emitted** (see write-model §3).
  → The extractor must read DRIVERTYPE and the version, then select the matching pointer-table
  offset map and write-model variant.
- **Version (1.0/1.2/1.4/1.5/1.7/1.8/1.9x):** different sidid signatures (§1c); different version
  string offset (§1b); different player size ⇒ different data base addresses. Treat
  `(version, drivertype)` as the key for the offset table.
- **ALLGHOSTREGS_ON / multi-SID:** uses the full `COMMONREGS` ghost-flush loop (write-model §2) —
  a *different write order* than the lean 1-SID path.

---

## 8. Multi-SID exclusion (out of scope for the first pass)

2-SID / 3-SID / 4-SID tunes (`psid_version` 3/4; flags bit7/bit9 set; sidid `2SID`/`3SID`) write
extra chips at **$D420+/$D440+/$D460+**. The in-scope target is the **1-SID case
($D400..$D418)** only. The 38 multi-SID tunes (29 v3 + 9 v4) should be **deferred / excluded**
until 1-SID is solid. (If excluded, add to `tools/excluded_sids.json` with reason
"SID-Wizard multi-SID — extra-chip writes $D420+/$D440+/$D460+, out of 1-SID USF scope".)

---

## 9. Ordered extraction checklist (binary → USF)

1. **Header:** parse PSID header; confirm `magic=PSID`, read `version`, `init`, `play`,
   `songs`, `startSong`, **`speed` word** (→ vblank vs per-IRQ verdict), `flags` (PAL/SID model).
   `load_addr` field = 0 ⇒ real load = first 2 data bytes (LE). Reject multi-SID (version≥3 /
   flags bit7) → exclude.
2. **Anchor:** confirm jump table at load (`JMP init / JMP play` = load+0 / load+3). Classify
   `(version, drivertype)` via sidid signature (§1c) + version string (§1b).
3. **SWM header:** locate `"SWM1"/"SWMS"` (≈ load+$20); read counts, DRIVERTYPE, TUNING, FSPEED,
   DEFPATLEN, mute, author. Sanity-check counts against §2 limits.
4. **Pointer tables:** using the `(version,drivertype)` offset map (OPEN — build per §3), read the
   sequence / pattern / instrument / chord / tempo pointer tables.
5. **Instruments:** for each of `INSTAMOUNT`, decode the 16-byte base (§4) + `$FF`-terminated
   WF-ARP / PW / filter tables → USF instrument (parametric).
6. **Patterns:** for each of `PATAMOUNT`, decode rows with the §5 opcode map (notes $00-$5F, FX
   $60/$70-$77/$78/$79-$7E, instrument $01-$3E/$3F, end $FF).
7. **Sequences:** for each channel, decode the §6 orderlist (pattern#, transpose, volume, tempo,
   end $FE, jump $FF) → USF per-channel orderlist + loop point.
8. **Chord table & tempo table:** decode `CHRDLEN` / `TMPLEN` bytes (chord = note-offset lists;
   tempo = per-step speed program) → USF chord/tempo (parametric).
9. **Tuning:** map TUNINGTYPE (0=440, 1=432 Verdi, 2=Just) → the USF freq-table choice / pitch
   reference. (The player ships 3 freq tables; tuning selects which — see write-model.)
10. **init.sid priming:** the init clears $D400-$D417 (universal reset) then primes nothing
    special beyond first-frame state → USF `init.sid` likely just master-vol; confirm against the
    init trace (write-model §init).
11. **Verify:** build → `siddump --writelog` orig vs rebuild → `compare_instruction_stream`
    (flat, for the 992 vblank tunes) / per-IRQ (for the 56 `speed=0x1` subtunes). Ear-test
    (py65 misses dispatch/CIA bugs).

---

## Leads to follow

- **CLOSE the pointer-table offset map (highest priority):** `tools/seed_disassembly.py` on
  `ChipMotif.sid` (v1.7, DRIVERTYPE=0), hand-annotate the pointer loads at `$1173`/`$114E` and the
  lo/hi tables; repeat for one tune per DRIVERTYPE (0..4) and per major version. Record offsets as
  a `(version,drivertype) → {seq,pat,inst,chord,tempo,subtune base}` table. This is the single
  blocking unknown for the extractor.
- **Recover the lean 1-SID emitter source** (the `COMMONREGS .else` branch + `SETPWID` +
  per-voice writer at `$1173`). The WebFetch summariser truncates player.asm; fetch by byte-range
  or via the SourceForge SVN `viewvc` raw export instead. The sidid `(SidWizard_V1.?)` line
  `B1 ?? 9D 05 D4 … 9D 06 D4 … 9D 04 D4` is that emitter — disassemble it from a real binary.
- **Verbatim-confirm sequence opcodes** ($80/$90/$A0/$B0 boundaries) and **pattern BigFX/value
  column** semantics from `editor.asm` (pattern/orderlist editor) or the per-channel routine.
- **Reconcile DrvType names**: 0=NORMAL,1=MID,2=LIGHT,3=EXTRA,4=BARE (editor.asm) vs the
  light/medium/full/extra/bare/demo set (SWM-spec.src). Read `include/startupmenu.inc`.
- **Tuning tables:** locate the 3 freq tables (440/432/Just) in the player and confirm
  TUNINGTYPE selects among them (relevant to the write-model freq bytes).
- **Census refinement:** of the 56 `speed=0x1` tunes, confirm which subtunes are CIA (multispeed)
  vs vblank, and whether any are also multi-SID. Run `siddump --writelog-per-irq` on a sample.
- **Relocated 1-SID variants** (init $0FB8/$0C00/$E000/…, 775→1010 gap): same player, different
  base — confirm the anchor + offset map still apply after the reloc shift before counting them in
  scope.
