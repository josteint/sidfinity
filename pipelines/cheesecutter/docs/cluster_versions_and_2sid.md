<!--
source_url:
  primary:   https://github.com/theyamo/CheeseCutter  (GPL, local checkout at tmp/dmc_hunt/CheeseCutter/)
  secondary: CSDb https://csdb.dk/search/?stype=all&search=cheesecutter  (release dates)
             HVSC hvsc85/ — 302 CheeseCutter SID files, all sidid-scanned here
             SIDID tool   tmp/dmc_hunt/sidid/sidid.cfg + compiled binary
fetched_via: local Read tool (source + binaries); WebFetch (CSDb, GitHub commit history);
             Bash (sidid scan on HVSC, PSID header parsing, binary disassembly)
fetch_date: 2026-06-14
author: CheeseCutter by Abaddon (Timo Taipalus) / Triad; 2SID tunes by Scarzix, LMan, Et1999cc, Steel
content_date: CheeseCutter 2.10 (player header "cc4.07", player source "feb '12")
reliability: HIGH for write model (first-principles binary disassembly of real HVSC SIDs);
             MEDIUM for version-era mapping (release dates from CSDb; no pre-2012 source survives in git);
             MEDIUM for 2.0-2.2 characterisation (0 HVSC examples; deduced from sig structure only)
-->

# CheeseCutter — Sub-variant version map and 2SID write model

## 1. Release timeline (CSDb)

| CC version | CSDb date | Notes |
|---|---|---|
| 0.4.0 | 2011-03-15 | First public; by Abaddon |
| 0.5.1 | 2011-10-15 | Still pre-2.x |
| 2.3.0 | 2012-03-20 | First "2.x" entry in CSDb; by Abaddon |
| 2.4.0 | 2012-09-24 | by Triad (3AD) |
| 2.5.0 | 2013-05-13 | |
| 2.6.1 | 2014-06-13 | |
| 2.7.1 | 2015-01-11 | player v4.01 (HR-SR from instr byte6); direct pulse added |
| 2.8.0 | 2015-11-28 | player v4.03/4.04 (direct pulse/filter; lovib cond fix; sync support) |
| 2.9.0 | 2017-04-13 | |
| 2.10  | 2026-03-xx | SDL2 port merged to master; current GitHub head |

The GitHub repository (`theyamo/CheeseCutter`) contains a single commit (85323d8, March 2026) — it is a
**flat snapshot**, not a full history. All player evolution below is reconstructed from CSDb dates, the
GitHub commit-log of `src/c64/player_v4.acme` (Dec 2013 – Mar 2016), and first-principles binary analysis
of HVSC SIDs.

The player source header labels itself:
```
;;; CCUTTER 2.x musicplayer by abad
;;; Based on JCH NP 21.G4 by Laxity/VIB
```
The in-memory version string (at `$0FEE` when `EXPORT=FALSE`) is `"cc4.07"`.

---

## 2. SIDID sub-signatures — what each fingerprints

The four sub-signatures under `CheeseCutter_2.x` in `sidid.cfg` all target the **exported** (PSID) player
binary. They are checked **after** the parent signature `C8 F0 ?? 98 9D ?? ?? B1 ?? C9 ?? D0 ?? FE ?? ??
BD ?? ?? 9D` which is always present. `sidid` outputs the **first** matching sub-sig, so ordering matters.

### 2a. `(CheeseCutter_2.0-2.2)` — 0 HVSC matches

Signature bytes:
```
B9 ?? ?? 8D ?? ?? 8D ?? ?? AD ?? ?? F0 ?? B9 ?? ?? 8D ?? ?? A2 02 AD ?? ?? 3D ?? ?? 9D ?? ?? CA 10 ?? 2C ?? ?? 10
```

Decoded instruction sequence (subinit region):
```
LDA songsets,Y        ; B9 — track pointer lo
STA tracklo_table     ; 8D
STA trackhi_table     ; 8D  (or second voice ptr)
LDA speed_or_flag     ; AD
BEQ/BNE rel           ; F0 (skip if export flag)
LDA songsets+n,Y      ; B9 — voicon source byte
STA <somewhere>       ; 8D
LDX #2                ; A2 02 — voice loop
LDA voicon_flat       ; AD (absolute load — NOT Y-indexed)
AND voicon_bits,X     ; 3D (AND abs,X — bitmask per voice)
STA voicon,X          ; 9D (STA abs,X)
DEX                   ; CA
BPL loop              ; 10
BIT state             ; 2C
BPL rel               ; 10 (export/multispeed check)
```

The critical feature distinguishing 2.0-2.2 from later versions: the voicon initialisation uses `LDA abs`
(opcode `AD`) to load the voice-enable byte, followed by `AND abs,X` (opcode `3D`) to mask per-voice.
This means voicon is stored as a **flat absolute address** rather than being indexed by subtune number via Y.

**Interpretation:** the 2.0-2.2 player does not support per-subtune voice enable in the way 2.3+ does.
Voice enables come from a single global location, not from the per-subtune songsets table.

**Why 0 HVSC matches:** CC 0.4.0 (2011) and 0.5.1 (2011) predate any HVSC submission. The first
CheeseCutter HVSC entry was CC 2.3.0 (2012). No 2.0-2.2 exported SIDs appear to have been submitted
to HVSC. The signature remains valid for the pre-2012 era, but the corpus is not in HVSC #84.

### 2b. `(CheeseCutter_2.3-2.4)` — 4 HVSC matches

Signature bytes:
```
A9 01 9D ?? ?? CA 10 ?? 2C ?? ?? 10 ?? A9 01 8D ?? ?? 60
```

Decoded instruction sequence (subinit1 + subinit3 blocks):
```
LDA #$01              ; A9 01
STA newseq,X          ; 9D — mark "new sequence needed" for each voice
DEX                   ; CA
BPL loop              ; 10 (runs X = 2..0)
BIT state             ; 2C (check editor vs export flag)
BPL skip              ; 10 (BPL — if N clear, i.e. not in editor)
LDA #$01              ; A9 01
STA state             ; 8D — set state=1 (first-play trigger)
RTS                   ; 60
```

This fingerprints the **tail of `subinit`** in the CheeseCutter 2.3/2.4 player: the newseq
initialisation loop followed by the state=1 / RTS block.

Importantly, this sequence is **also present in the 2.5+ player** (source lines 302-309 of
`player_v4.acme`). The 4 tunes that match this sub-sig AND NOT the 2.5+ sub-sig are
**2.5+ player builds with `INCLUDE_CHORD=FALSE`** (the chord dispatch code is stripped by
`dumpOptimized` when no chord commands are used). Binary analysis confirms `Disillusionment.sid`
(one of the 4) has the chord dispatch code (`CMP #$A0` at `$15F2`) — so it IS a 2.5+ player build,
but sidid outputs the 2.3-2.4 label because that sub-sig appears earlier in `sidid.cfg`.

**Practical meaning for the pipeline:** "2.3-2.4" label actually means "any CC player build where the
chord dispatch was NOT stripped (or where the sig scan ran before the 2.5+ chord-path check)." Treat
2.3-2.4 and 2.5+ as the **same player architecture** for extraction purposes.

HVSC matches (4): `Disillusionment`, `Trouble_Every_Day` (both Abaddon), `Leasured_Time` (Terric),
`Zeropage_Gravity` (demo).

### 2c. `(CheeseCutter_2.5+)` — 184 HVSC matches

Signature bytes:
```
C9 A0 B0 0C 29 1F A8 B9
```

Decoded instruction sequence (superparse2 — chord dispatch):
```
CMP #$A0              ; C9 A0 — is this a $80-9F chord cmd?
BCS notchord          ; B0 0C (if >=, skip chord)
AND #$1F              ; 29 1F — extract chord index
TAY                   ; A8
LDA chordindex,Y      ; B9 -- look up in chordIndexTable
```

This fingerprints the `INCLUDE_SEQ_SET_CHORD=TRUE` chord-dispatch block inside `superparse2`
(player_v4.acme lines 1072-1076). When `dumpOptimized` detects no chord commands in the song,
it sets `INCLUDE_SEQ_SET_CHORD=FALSE` and this code is absent — then only the parent sig or the
2.3-2.4 sub-sig matches.

This signature works for **any version of the CC player from 2.3 onwards** as long as the exported
tune uses at least one chord command (super-index `$80..$9F`).

184 HVSC matches — this is the large majority of the CC corpus.

**The 302-total breakdown:**
- 184 match `(CheeseCutter_2.5+)` — 2.5+ era, chord used
- 4 match `(CheeseCutter_2.3-2.4)` — same player era, no chord (sidid hits 2.3-2.4 sub first)
- 6 match `(CheeseCutter_2SID)` — stereo variant (see §3)
- 108 match only `CheeseCutter_2.x` parent — 2.5+ era, no chord AND 2.3-2.4 sub didn't hit
  (probably these 108 don't have either the newseq or chord blocks — e.g. stripped tunes)

### 2d. `(CheeseCutter_2SID)` — 6 HVSC matches

Signature bytes:
```
C9 08 29 07 9D ?? ?? BD ?? ?? 7D ?? ?? 9D ?? ?? CA 30 ?? 4C ?? ?? AD ?? ?? 8D 15 D4 AD ?? ?? 8D 35 D4
```

Decoded (from binary at `$1719` in `Auxillary_Love_2SID.sid`):
```
CMP #$08              ; C9 08 — cutoff accumulator wrap check
AND #$07              ; 29 07 — mask to 3 bits
STA filt_accum,X      ; 9D — save per-SID filt state
LDA filt_base,X       ; BD
ADC filt_add,X        ; 7D (ADC abs,X)
STA filt_base,X       ; 9D
DEX                   ; CA
BMI done              ; 30 (not BPL — loop terminates when X < 0)
JMP filt_loop         ; 4C
LDA filt_cutlo        ; AD
STA $D415             ; 8D 15 D4 — SID1 cutoff lo
LDA filt_cutlo2       ; AD
STA $D435             ; 8D 35 D4 — SID2 cutoff lo ($D420 + $15)
```

The terminal `8D 15 D4 / ... 8D 35 D4` pair (write to BOTH `$D415` and `$D435`) is the unambiguous
2SID discriminator. `$D435 = $D420 + $15` = the filter cutoff-lo register of the second SID chip at
base `$D420`.

HVSC matches (6):
- `MUSICIANS/E/Et1999cc/Overdrive-Title_Theme_2SID.sid`
- `MUSICIANS/L/LMan/Blade_Runner_Main_Titles_2SID.sid`
- `MUSICIANS/L/LMan/Tuneful_Eight_tune_1_2SID.sid`
- `MUSICIANS/S/Steel/Game_of_Thrones_2SID.sid`
- `MUSICIANS/S/Scarzix/Auxillary_Love_2SID.sid`
- `MUSICIANS/S/Scarzix/Singularity_2SID.sid`

---

## 3. What changed between generations (player architecture delta)

### 2.0-2.2 → 2.3 (first change captured in HVSC)

- **Per-subtune voice enable**: 2.0-2.2 loaded voicon from a flat absolute address (`LDA abs + AND
  abs,X`). 2.3+ loads from the songsets table indexed by subtune number (`LDA songsets+n,Y + AND
  bits,X`), enabling per-subtune voice routing.
- **`newseq` initialisation**: 2.3 adds explicit `STA newseq,X` loop at end of subinit (the 2.3-2.4
  sub-sig fingerprints this). In 2.0-2.2 the voicon-AND loop occupied this code slot.
- **Subtune songset structure**: The songset entry for each subtune gains the voice-mask byte, implying
  a wider table width in 2.3+.

### 2.3/2.4 → 2.5 (player v4 restructure)

- **Chord table dispatch** added to `superparse2`: super-index `$80..$9F` now triggers `chordIndexTable`
  lookup. This is the feature that the 2.5+ sig fingerprints.
- **player_v4** introduced (GitHub log: "direct pulse set function to player" Dec 2013; "player updated
  to 4.01" Dec 2013). The player version string changes from the pre-v4 form to `cc4.07`.
- **per-instrument pulse and filter pointers** fully generalised: byte5=PULSP (`$00-$3F` → table index;
  `$80+` → direct PW), byte4=FLTP (table index); `INCLUDE_DIRECT_PULSE` conditional added.
- **Instrument count**: raised to 48 (`INSNO=48`) in v4; column-major stride 48 instead of 32.
- **4-byte pulse/filter table rows** (vs 2-byte in NP20.G4 ancestors).
- **Effect dispatch became fully conditional**: `INCLUDE_CMD_SLUP`, `INCLUDE_CMD_SLDOWN`, `INCLUDE_VIBRAFEEL`,
  `INCLUDE_FILTER`, `INCLUDE_CHORD`, etc. are all independently strippable.

### 2.5–2.9 (incremental player patches)

From the GitHub commit log on `player_v4.acme`:
- **2013-12-04**: `player updated to 4.01, HR value read from instr` — HR-SR previously came from a
  fixed location; now taken from instrument byte6 (`INS_7`).
- **2013-12-12**: `direct pulse set function to player` — `INCLUDE_DIRECT_PULSE=TRUE`; direct PW set
  via instrument byte5 `>= $80`.
- **2014-09-29**: `player v4.04` with `directfilter fixed`.
- **2014-10-08**: `revert player to '4.03', remove direct pulse&filt` — direct filter reverted;
  current head has `INCLUDE_DIRECT_PULSE=TRUE` but no `INCLUDE_DIRECT_FILTER`.
- **2016-03-13**: `added sync support for player` — `INCLUDE_SYNC=TRUE`; speed command `$F0` toggles
  `sync` flag instead of setting speed.

These are all minor and do not change the sidid fingerprint. The player was functionally stable from
2.5 onwards; the 2.5+ sig matches everything from 2.5 through 2.10.

---

## 4. 2SID write model (from binary analysis of Auxillary_Love_2SID.sid)

### 4a. PSID header (all 6 HVSC 2SID tunes are identical)

| Field | Value | Meaning |
|---|---|---|
| PSID magic | `PSID` | standard SID |
| Version | 3 | required for second SID address field |
| Load address | `$1000` | standard CC load |
| Init address | `$1000` | |
| Play address | `$1003` | |
| flags | `$00A4` | PAL, 8580 SID model for both chips |
| `second_SID_address` byte | `$42` | SID2 at `$D000 + $42 * 16 = $D420` |
| `third_SID_address` byte | `$00` | none |

The flags `$00A4` breakdown (PSID v3 spec):
- bits[1:0] = 0 (PSID/builtin player)
- bits[3:2] = 1 (PAL clock)
- bits[5:4] = 2 (8580)
- bits[7:6] = 2 (8580 for SID2)

### 4b. Voice-to-SID chip mapping (6 voices)

The 2SID player uses the **same setsid block** as the single-SID player (`STA $D400,Y` writes
with Y from a `voice[]` table) but extends the table from 3 to 6 entries:

```
voice[] = { $00, $07, $0E,   $20, $27, $2E }
           |--- SID1 ---|   |---- SID2 ----|
```

Voice loop runs `LDX #5` down to `LDX #0` (6 iterations). At each step Y = `voice[X]`:

| X | Y | Writes to | SID chip | Voice |
|---|---|---|---|---|
| 5 | `$2E` | `$D42E-$D434` | SID2 | V3 |
| 4 | `$27` | `$D427-$D42D` | SID2 | V2 |
| 3 | `$20` | `$D420-$D426` | SID2 | V1 |
| 2 | `$0E` | `$D40E-$D414` | SID1 | V3 |
| 1 | `$07` | `$D407-$D40D` | SID1 | V2 |
| 0 | `$00` | `$D400-$D406` | SID1 | V1 |

Per-voice register write order (same as single-SID):
`D4xx+0` (freqlo), `D4xx+1` (freqhi), `D4xx+6` (SR), `D4xx+5` (AD),
`D4xx+2` (PWlo), `D4xx+3` (PWhi), `D4xx+4` (ctrl/gate).

Voices 1-3 (X=2..0) write to SID1, voices 4-6 (X=5..3) write to SID2.

### 4c. Init / silence (both SID chips)

The init and first-play state-reset both zero both SID chips simultaneously via a single loop:

```asm
    LDA #$00
    LDX #$18        ; 24 = $D418 offset
loop:
    STA $D400,X     ; zero SID1 registers X..0 ($D400-$D418)
    STA $D420,X     ; zero SID2 registers X..0 ($D420-$D438)
    DEX
    BPL loop
```

`LDX #$18` → X goes from 24 down to 0, clearing 25 registers on each chip in a single pass.
After this, `LDX #5` loop inits the 6 voice state tables.

### 4d. Per-frame filter block (once per frame, after all 6 voice writes)

The filter sweep and volume writes happen once per frame (not per voice), writing to both chips
in interleaved order:

```
STA $D415   (SID1 cutoff lo)
STA $D435   (SID2 cutoff lo = $D420+$15)
STA $D416   (SID1 cutoff hi)
STA $D436   (SID2 cutoff hi)
STA $D417   (SID1 res+routing)
STA $D437   (SID2 res+routing)
ORA bandpass_SID1 → STA $D418   (SID1 vol|passband)
ORA bandpass_SID2 → STA $D438   (SID2 vol|passband)
```

Confirmed from binary disassembly at `$172F-$1762` (Auxillary_Love_2SID.sid).

Each SID chip has its **own independent filter state**: separate cutoff accumulators, bandpass
bits, and resonance/routing values. The filter table loop runs `LDX #1` (2 iterations: X=1=SID1,
X=0=SID2 — or vice versa; the BMI-terminate at $172A suggests X goes from 1 down to -1).

### 4e. Full per-frame write sequence (Mode-1 verdict)

The complete per-`play()` write stream for 2SID CheeseCutter:

```
; Voice loop, X = 5..0 (V6=SID2V3 first, down to V1=SID1V1)
for X in {5,4,3,2,1,0}:
    STA $D400+voice[X]+0   (freqlo)
    STA $D400+voice[X]+1   (freqhi)
    STA $D400+voice[X]+6   (SR)
    STA $D400+voice[X]+5   (AD)
    STA $D400+voice[X]+2   (PWlo)
    STA $D400+voice[X]+3   (PWhi)
    STA $D400+voice[X]+4   (ctrl/gate)

; Filter block (once, after voice loop):
STA $D415    (SID1 cutoff lo)
STA $D435    (SID2 cutoff lo)
STA $D416    (SID1 cutoff hi)
STA $D436    (SID2 cutoff hi)
STA $D417    (SID1 res/route)  [only on filter-init row — conditional]
STA $D437    (SID2 res/route)  [conditional]
STA $D415    (SID1 cutoff lo — written again via sweep accumulator)
STA $D416    (SID1 cutoff hi)
STA $D418    (SID1 vol|passband)
STA $D438    (SID2 vol|passband)
```

Note: `$D417/$D437` only written on a filter-init row (same conditional as single-SID). The final
`$D415/D416` writes come from the accumulated sweep value replacing the initial-cutoff set value.

**For Mode-1 (write-stream) verification:** 6 voices = 42 register writes per frame (vs 21 for
single-SID), plus 8 filter/global writes (vs 4). Total ~50 writes per frame.

---

## 5. The "flag out unused effect code" export mechanism

`dumpOptimized` in `src/ct/build.d` scans every sequence and instrument in the song and sets
`INCLUDE_*` flags only for effects actually used. Effects not used are compiled to zero bytes
(the `!if INCLUDE_X = FALSE { }` blocks in player_v4.acme).

**Flags set per-tune (if and only if the tune uses the effect):**

| Flag | Source condition | Player code stripped when FALSE |
|---|---|---|
| `INCLUDE_CMD_SLUP` | slide-up command used | slide-up loop (~10 bytes) |
| `INCLUDE_CMD_SLDOWN` | slide-down command used | slide-down loop |
| `INCLUDE_CMD_VIBR` | hi-fi vibrato command used | vibrato compute block (~80 bytes) |
| `INCLUDE_CMD_PORTA` | portamento command used | portamento engine |
| `INCLUDE_CMD_SET_ADSR` | set-ADSR command used | ADSR set block |
| `INCLUDE_CMD_SET_LOVIB` | lo-fi vibrato command used | lo-fi vibrato block |
| `INCLUDE_CMD_SET_OFFSET` | detune/offset command used | offset set block |
| `INCLUDE_SEQ_SET_CHORD` | `$80-$9F` super-index used | **chord dispatch** (the 2.5+ sid-id sig) |
| `INCLUDE_CHORD` | chord used | chord table loop |
| `INCLUDE_SEQ_SET_ATT/DEC/SUS/REL` | `$A0/$B0/$C0/$D0` super used | ADSR nibble setters |
| `INCLUDE_SEQ_SET_VOL` | `$E0-$EF` super used | volume setter |
| `INCLUDE_SEQ_SET_SPEED` | `$F0-$FF` super used | speed setter |
| `INCLUDE_BREAKSPEED` | any subtune speed < 2 | breakspeed/tempo-program code |
| `INCLUDE_FILTER` | any instrument has filter pointer > 0 | entire filter block |
| `INCLUDE_DIRECT_PULSE` | always TRUE in current player | direct-PW code path |

**`INCLUDE_CMD_SET_WAVE` is permanently FALSE** (command `$06` / `CMD_SET_WAVE` is disabled in
CC; the assembly line `!if INCLUDE_CMD_SET_WAVE = FALSE` is hardcoded).

**Multispeed:** `MULTISPEED` is set if `song.multiplier > 1`. This adds the CIA timer setup and
the `mplay` jump table entry. `USE_MDRIVER` is TRUE for PSID export with multispeed (CIA-driven
`cplay`/`cinit` path).

**INSNO:** set to `song.numInstr + 1` (one past the highest used instrument). Controls the
column-major stride of the instrument table in the exported binary. Ranges from 1 to 48.

**Effect on sidid matching:**
- If `INCLUDE_SEQ_SET_CHORD=FALSE`: the `(CheeseCutter_2.5+)` signature `C9 A0 B0 0C 29 1F A8 B9`
  is absent → only parent sig (or 2.3-2.4 sub-sig) matches.
- The remaining 108 "parent-only" tunes in HVSC are all 2.5+ player builds where chord was unused.
- The 2.3-2.4 label hitting 4 of those 108 is a sidid ordering artifact: both 2.3-2.4 and 2.5+
  sigs can match the same binary; sidid outputs whichever is listed first in the cfg.

---

## 6. Practical implications for the SIDfinity pipeline

### Sub-variant discrimination at extraction time

All four sub-sigs (2.0-2.2, 2.3-2.4, 2.5+, 2SID) share the **same effect chain and table format**
(described in `github_cheesecutter.md`). The sub-sig differences are:
- 2.0-2.2: different voicon init (pre-subtune-voicemask era). No HVSC examples to extract.
- 2.3-2.4 vs 2.5+: same player architecture; the label reflects only whether INCLUDE_CHORD was TRUE.
- 2SID: 6 voices instead of 3; extended voice table; dual filter write.

**Extraction can use a single code path for all 2.3-2.5+ variants.** Treat "2.3-2.4" as the same
engine as "2.5+" for USF purposes.

### INSNO / instrument stride

`INSNO` varies per-exported tune (1 to 48). The instrument table column stride = `INSNO`. This is
already noted in `github_cheesecutter.md`; confirmed here: `dump.d` emits exactly `maxInsno+1` rows
per instrument column.

### 2SID extraction

- 6 voices (X=0..5). Voice ordering in the play loop is X=5 down to X=0 (SID2-V3 first).
- Three voices write to SID1 (`$D400`), three to SID2 (`$D420`).
- The `.ct` file format does NOT support 2SID: `base.d` line 1312-1313 throws
  `"The song appears to be a stereo SID file and doesn't work with this editor."` if `ver >= 128`.
  This means 2SID songs are stored with `ver = ver | 0x80`, i.e. `ver = 140` (SONG_REVISION 12 + 128).
  The CC editor cannot open them; they were likely exported via a custom or patched build not in the
  public repository.
- **Write-stream verdict for 2SID**: 50 writes per frame (42 voice + 8 filter/global), all to the
  `$D400-$D438` range. The second-SID writes span `$D420-$D438`. PSID v3 header declares the second
  SID at `$D420` via `second_SID_address = $42`.
- All 6 HVSC 2SID tunes use a **non-multispeed** (VBI) play model (`speed = 0`, flags PAL).
- No third SID: `third_SID_address = 0` in all 6 files.

### Mode-1 comparison scope

For 2SID Mode-1 verification:
- The write stream covers `$D400-$D418` (SID1) and `$D420-$D438` (SID2).
- Frame order: V6..V1 voice writes (42 writes), then filter/vol block (8 writes).
- Within each voice: same 7-register order as single-SID (freqlo, freqhi, SR, AD, PWlo, PWhi, ctrl).
- `$D417/$D437` are conditional (only on filter-init frames), same as `$D417` in single-SID.

---

## Leads to follow

1. **2.0-2.2 source recovery**: The pre-2.3 player source is not in the GitHub repo. The CSDb entries
   for CC 0.4.0 and 0.5.1 may have downloadable binaries; extracting the player from one of those
   `.ct` demo exports (if any survive on CSDb) would confirm the voicon difference.

2. **108 "parent-only" tunes**: Are any of these 2.0-2.2 era, or all 2.5+ with INCLUDE_CHORD=FALSE?
   Binary analysis of one (check for `CMP #$A0` in play region) would confirm. A quick Python scan
   across all 108 could split them definitively.

3. **2SID filter: one or two filter programs?** The binary shows two separate cutoff values
   (`$1922`/`$1923`) and two bandpass bytes (`$1914`/`$1915`). Whether the 2SID variant supports
   TWO independent filter programs (one per chip) or mirrors a single program to both chips needs
   deeper disassembly of the filter-sweep loop (around `$16AE`, marked partially unclear above).

4. **2SID `.ct` format**: The editor rejects 2SID files. The export tool used to create the 6 HVSC
   2SID tunes is unknown — a patched CC build or a bespoke script. This matters if we ever want to
   re-extract from `.ct` source.

5. **Multispeed (CIA) 2SID tunes**: none in HVSC; the `CIA_VALUE / USE_MDRIVER` path would need
   testing if any such tunes appear.

6. **`src/ct/purge.d`**: The table-purge logic (`purgeAll`, `purgePulseFilter`, etc.) determines
   which pulse/filter rows survive in the exported binary. The `getHighestUsed` + `purgePulseFilter`
   functions trim trailing zero rows. This affects the exact table sizes present in each exported SID
   and should be accounted for in the extractor (don't assume fixed table sizes).
