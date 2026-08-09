<!--
provenance:
  source_url: n/a (derived from local binaries)
  local:
    - pipelines/hardtrack/docs/src/sdk/extracted/PLAYER_V1.0.bin  (editor RELOCATABLE-OBJECT/source form + symbol table — NOT a runnable image; bogus load $A909; embeds "PLAYER V1.0 BY LONGHAIR" + the player symbol table)
    - pipelines/hardtrack/docs/src/sdk/extracted/PLAYER_V1.1.bin  (same, V1.1; bogus load $1309; embeds "PLAYER V1.1")
    - pipelines/hardtrack/docs/src/sdk/extracted/RELEASE_NOTES.bin  (despite the name, the COMPILED V1.0 PLAYER image: PRG load=$1000, JMP table 4C 60 10 / 4C D8 10, STA $D417 at file $37B/$39F = BASE+$379/$39D — independently confirms the HT_7_1 offsets below)
    - hvsc85/MUSICIANS/W/Wodnik/HT_7_1.sid   (canonical $1000 standalone build, disassembled byte-exact)
    - hvsc85/MUSICIANS/R/Randy/Scortia.sid   (relocated $3000 multi-copy build)
  fetched_via: local disassembly (tmp/hardtrack/work/dis.py, a hand-written 6502 disassembler) + siddump --writelog / --writelog-per-irq
  fetch_date: 2026-06-13
  author: HardTrack Composer player by Longhair / Milosz Ignatowski (Elysium/Parados); analysis SIDfinity
  content_date: player code 1992 (V1.0/V1.1); analysis 2026-06-13
  reliability: HIGH for the $1000 standalone layout (every offset below was read out of HT_7_1.sid's
               disassembly and cross-checked against the live siddump write stream); MEDIUM for the
               relocated/packed variant (Scortia) which bundles two player copies and bakes absolute
               freq addresses — flagged OPEN where unresolved.
-->

# HardTrack Composer — binary → USF extraction plan

This supersedes the byte offsets in `research.md`, which were a working model. Every
offset here was **read from the disassembly of `HT_7_1.sid`** (load $1000, init $1000,
play $1003) and confirmed against the live `siddump --writelog` stream. Where the model
in `research.md` was wrong it is called out as **[CORRECTION]**.

All offsets are **relative to the load address** (call it `BASE`). For the canonical
standalone build `BASE = $1000`. The engine is **relocation-invariant by fixed relative
offset** — confirmed on Scortia (`BASE=$3000`): the voice finaliser, $D417 build and
$D418 build all sit at the identical `BASE+offset` (see §9).

---

## 0. Census / why this layout

- 1170 HVSC tunes classified `HardTrack_Composer`; **1035 (88%) have `init=$1000`** —
  the standalone build this plan targets.
- PSID header `load_addr` field is **0** for all of them (load address is the first two
  bytes of the data block; real load = $1000).
- **Every** HVSC HardTrack tune has PSID `speed = 0` (vblank). There is **no** PSID
  CIA-multispeed bit set anywhere in the family. The "multispeed up to 6×" is an
  editor-authoring feature, not a PSID dispatch mode. `siddump --writelog-per-irq` shows
  ~1 play() entry per VBI for HT_7_1 / Intro_Zak_Remix / X-Style (2879–2882 entries over
  3000 frames). **[CORRECTION] Verdict uses the flat `--writelog` path, NOT the per-IRQ
  CIA path.** (See spec_write_model.md §7.)

---

## 1. Anchor the player (identity / version)

1.1 **Entry table at BASE+$00** (verbatim from HT_7_1):

```
$1000: 4C 60 10   JMP $1060      ; init  = BASE+$60
$1003: 4C D8 10   JMP $10D8      ; play  = BASE+$D8
```

So `init = BASE+$60`, `play = BASE+$D8`. **[CORRECTION] research.md said init "+$060 (~120B)"
and play "+$0D8" measured as flat file offsets — they are addresses BASE+$60 / BASE+$D8.**

1.2 **sidid / fingerprint signature.** Anchor on the entry table plus these relocation-
invariant code fragments (offsets from BASE; bytes verbatim from HT_7_1):

| BASE+ | bytes | meaning |
|---|---|---|
| `+$379` | `8D 17 D4` | `STA $D417` (filter routing build) |
| `+$39D` | `8D 17 D4` | `STA $D417` (filter-off build) |
| `+$522` | `99 02 D4` | `STA $D402,Y` head of voice finaliser |
| `+$57E` | `8D 18 D4` | `STA $D418` (master vol/filter mode) |

Confirmed on Scortia at `$3000+$379 = $3379`, `+$522 = $3522`, `+$57E = $357E`.

1.3 **Version string** lives at **BASE+$24** in fresh exports:
`"PLAYER V1.0 BY LONGHAIR/ELYSIUM! - COMPOSED BY DR.WODNIK -"` (HT_7_1, bytes $1024..).
Unreliable for version detection (present in only ~4/1170 SIDs; many overwrite the credit
text). **The reliable V1.0/V1.1 discriminator is the $D417 software-shadow address in the
sig region: V1.0 → `AD 1F 10` ($101F), V1.1 → `AD 1E 10` ($101E)** — see §10 and
`sidid_signature_analysis.md` §4. (The single sidid signature
`0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB 1D ?? ?? 8D ?? ?? 8D 17 D4` matches all
1170/1170 SIDs both versions, anchored on `STA $D417`.)

1.4 **Config / shadow region BASE+$06 .. BASE+$24** (the bytes between the JMP table and
the credit text). HT_7_1: `0F 28 1C 28 9C 9C 9C 1F 20 21 C8 90 00 36 37 36 04 02 03 0E 0E 0E 10 10 10`.
These are **runtime state, written by init** — do NOT extract them as song data. Key cells
(init writes them, §4): `+$06`=$D418 master-vol shadow; `+$07..+$09`=current note per voice;
`+$0A..+$0C`=track-ptr-lo per voice; `+$0D..+$0F`=track-ptr-hi per voice; `+$10..+$12`=
pattern-ptr-lo; `+$13..+$15`=pattern-ptr-hi; `+$16..+$18`=track index; `+$19..+$1B`=pattern
index; `+$1C..+$1E`=note value; `+$1F`=$D417 shadow.

---

## 2. init routine (BASE+$60) — what to read for subtune selection

init takes **A = subtune number**, `AND #$07` (max 8 subtunes), `TAX`, then copies
per-subtune pointers from tables indexed by X into the live config cells:

```
$1063 LDA $18A2,X  STA $100A   ; trk-ptr-lo V1  <- BASE+$8A2 table
$1069 LDA $18BA,X  STA $100D   ; trk-ptr-hi V1  <- BASE+$8BA table
$106F LDA $18AA,X  STA $100B   ; trk-ptr-lo V2  <- BASE+$8AA
$1075 LDA $18C2,X  STA $100E   ; trk-ptr-hi V2  <- BASE+$8C2
$107B LDA $18B2,X  STA $100C   ; trk-ptr-lo V3  <- BASE+$8B2
$1081 LDA $18CA,X  STA $100F   ; trk-ptr-hi V3  <- BASE+$8CA
$1087 LDA $16C4,X  STA $10E4   ; subtune speed/tempo divider <- BASE+$6C4
```

Then: `STA $D400..$D41C` cleared (`CPX #$1D`); `$1006 = $0F` (master vol); per-voice
state primed (X=0..2): track-index `$1016=0`, pattern-index `$1019=0`, note `$101C=0`,
pattern-ptr seeded `$1010=$F5 / $1013=$11` (placeholder), gate-mask `$169A=$FE`,
instrument `$16BE=0`, wave/pulse counters zeroed, `$16C1=1`, `$168E=1`; tempo counter
`$10FB = Y+1` (= 1 with Y=0). 

**Extraction:** **subtune count = PSID `songs` field** (the `AND #$07` caps the index at 8;
unused subtune slots in the pointer table hold garbage/duplicate pointers, so you cannot
count them — verified: `songs=1` tunes Conqueror & Trigonomy have all 8 hi-slots nonzero,
`songs=8` Ashido uses all 8). Per subtune index `s` (0-based), read V1/V2/V3 track pointers
from `lo[s]`/`hi[s]` of the six subtune-track tables and the speed byte from the tempo
table. **The subtune-track-table base is OPERAND-DERIVED** (init reads it at code BASE+$063;
operand value = $18A2 in HT_7_1, $17D1 in Conqueror, $19C7 in Ashido — see §4). The six
tables (lo×3, hi×3) and the tempo table are consecutive; tempo table is at the fixed
BASE+$6C4. **Version-dependent:** subtune-table layout is the same in V1.0 and V1.1 for the
standalone build (OPEN — confirm against a known V1.1 SID).

---

## 3. Track tables (per voice, per subtune)

Track pointer comes from §2 (BASE+$8A2.. resolved per subtune). The track is a byte
stream, index in `$1016,X`. Decode (from disasm $11FE..$124F):

```
byte b = (track),index ; index++
if b & $80 == 0  ($00..$7F):  PATTERN NUMBER -> look up pattern pointer table (§5)
else:
  $FF : LOOP  (reset index=0; set "looped" flag $165D=$FF; continue)   ; bytes verbatim CMP #$FF
  $FE : END / stop voice (set $16A3,X = 1 "song stopped")              ; CMP #$FE
  $FD : JUMP  (next byte = new index value; index = that byte)         ; CMP #$FD
  else ($80..$FC) : SET TRANSPOSE  (AND #$7F -> $169D,X; add-then-mask)  ; AND #$7F
```

**[CONFIRMED]** matches research.md track model. Transpose range is **$80..$FC** (because
$FD/$FE/$FF are reserved). Transpose stored as `byte & $7F` (0..$7C), added to note at
trigger time then `AND #$7F` (§6) — so it wraps within the 0..$7F note index space (it is
NOT a two's-complement signed add; it's add-then-mask-7-bit). **[CORRECTION] research.md
said "signed transpose"; the player does `note + transpose & $7F`, an unsigned add into a
128-entry index, not a signed offset.**

Worked example (HT_7_1 track V1 @ $18D2):
`85 05 10 8C 05 05 05 05 05 05 05 FD 04 FF` = `transpose+$05`, pat5, pat$10,
`transpose+$0C`, pat5×7, `jump→4`, `loop`.

---

## 4. Pattern pointer tables — **OPERAND-DERIVED, not fixed**

**CRITICAL — the data tables are NOT at fixed offsets.** The player code is a fixed-size
block (BASE+$00..~$587) but the data that follows is **variable-length per tune**, so the
engine reads every table base from a **code operand at a fixed code address**. Extraction
MUST read these operands (dataflow), per CLAUDE.md "dataflow over heuristics". Measured
across HT_7_1 / Conqueror / Ashido:

| table | code addr (fixed) | operand value HT_7_1 | Conqueror | Ashido |
|---|---|---|---|---|
| pattern-ptr-lo | BASE+$251 (`B9 lo hi` at BASE+$250) | $194A | $1A9A | $1C53 |
| pattern-ptr-hi | BASE+$259 (`B9 lo hi` at BASE+$258) | $195F | $1AC2 | $1CD3 |
| subtune trk-ptr (init) | BASE+$064 (`LDA abs,X` at BASE+$063) | $18A2 | $17D1 | $19C7 |
| pulse-prog idx array | BASE+$337 | $172C | $16F3 | $1729 |
| wave-prog idx array | BASE+$331 | $174C | $1700 | $1748 |
| FX-byte array | BASE+$31A | $176C | $170D | $1767 |

By contrast these ARE at fixed offsets (they immediately follow the fixed player code, so
their addresses don't move): **freq-LO = BASE+$588, freq-HI = BASE+$5E8, instrument-AD
array = BASE+$6CC, subtune-tempo table = BASE+$6C4** (identical in all three tunes — all
V1.0).

**VERSION CAVEAT:** the *code addresses* in the table above (BASE+$250, +$063, +$30E, …)
and the "fixed" data offsets (+$588, +$6CC, …) are **V1.0**. V1.1 shifts the whole player
~$25 bytes later (§10), so for V1.1 add the shift to every code/fixed-data offset. The
robust approach that survives both versions: **locate the operand by code pattern, not
absolute address** — e.g. find the `STA $D417` anchor (sig §1.3), then read the data-table
operands relative to a small set of recognisable opcode landmarks; or simply scan for the
`B9 lo hi` / `BD lo hi` instructions in the play routine and resolve their operands. Tag
the version first ($101F vs $101E, §10) and pick the matching offset constants.

- Pattern number 0..$7F indexes the (lo,hi) tables directly. There is **no in-band pattern
  count**: the gap between the lo and hi tables is the assembler's fixed max allocation
  ($15 = 21 slots), NOT the tune's pattern count. **The set of *used* patterns = the union
  of pattern numbers referenced by the three tracks.** [CORRECTION to earlier guess: the
  $15 gap is constant across tunes and is not a per-tune count.]

---

## 5. Pattern decode

Pattern is a stream of **2-byte steps `(note-byte, command-byte)`** (from disasm
$1115..$119B). **[CORRECTION] research.md described inline single bytes with `$80-$FF =
set-instrument` and `$FF = end-of-pattern`; the real format is interleaved (note, cmd)
pairs, fixed length, looped by the track — there is no in-pattern end sentinel.**

### note-byte (dispatched at $1115)
| value | meaning |
|---|---|
| `$00..$5F` | **NOTE** (index into 96-entry freq table after `+transpose &$7F`); sets retrigger flag $16AF=1 |
| `$60` | **TIE / hold** — keep current note, no retrigger |
| `$61` | **DEL** — gate off (set gate-mask $169A=$FE) |
| `$62` | **CUT** — hard cut: $D406(SR)=0, waveform $165A=0, flag $168E=1 |
| `$63 yy` | **GLISS UP** — set gliss flag $1663=1, dir $1666=0, *consumes next byte* yy = gliss speed → $1669 |
| `$64 yy` | **GLISS DOWN** — gliss flag $1663=1, dir $1666=1, *consumes next byte* yy = gliss speed → $1669 |

(`$63`/`$64` advance the read index by one extra byte for their `yy` operand.)

### command-byte (dispatched at $1180, read right after the note-byte)
| value | meaning |
|---|---|
| `$00` | no command |
| `$6F` | **legato / no-hard-restart flag** (set $1685; suppresses the hard-restart on this note) |
| else | **SET INSTRUMENT** = `byte AND $1F` (0..31). Saves previous inst → $16C1, new → $16BE |

**[CORRECTION]** instrument number is `cmd & $1F` (5 bits → max 32 instruments), NOT
`& $7F`. The instrument tables (§6) are exactly 32 entries each, confirming the $1F mask.

Worked example (HT_7_1 pattern 0 @ $1974): `10 83 60 00 60 00 60 00 10 00 ...` =
step0 (note $10, inst $03), step1 (tie, –), step2 (tie, –), step3 (tie, –),
step4 (note $10, –), ...

---

## 6. Instrument macro decode (32 instruments, parallel SoA arrays)

**[CORRECTION] research.md described "(waveform, transpose) pairs" (interleaved AoS).
The real layout is a set of parallel byte arrays (struct-of-arrays), one per parameter,
each `N` bytes where `N` = the tune's instrument count, indexed by the instrument number.**

**Instrument count is variable per tune and = the array stride.** The 13 instrument arrays
are packed consecutively starting at the **fixed** AD base (BASE+$6CC). The stride between
consecutive arrays equals the instrument count `N`:
- HT_7_1: AD@$6CC, SR@$6EC → stride $20 → **N = 32 instruments** (the editor max).
- Conqueror: AD@$6CC, SR@$6D9 → stride $0D → **N = 13 instruments**.

Each array's actual base is also readable directly from a code operand at its fixed code
address (the operands at BASE+$30E, $314, $31A, $322, $331, $337, … hold AD/SR/FX/…
bases). Either derive `N = SR_base − AD_base` then compute `array_k = AD_base + k·N`, or
read every base from its operand. Bases below are the **HT_7_1 (N=32)** values; the BASE+
offset shown is `AD_base + k·$20`.

| array | k·N (HT_7_1) | feeds | meaning |
|---|---|---|---|
| AD        | `+$6CC` | →$D405 | ADSR attack/decay |
| SR        | `+$6EC` | →$D406 | ADSR sustain/release |
| pulse-cfg | `+$70C` | seeds PW | lo-nib→PW-hi seed ($1657), hi-nib→PW-lo seed ($1654) |
| pulseprgI | `+$72C` | →$167C | start index into the **pulse program** ($188C, §7) |
| waveprgI  | `+$74C` | →$16AC | start index into the **wave program** ($186C, §7) |
| FX        | `+$76C` | flags  | **bit7 = drum / absolute-pitch flag** (→$1676); `&$03`=wave-step count; `&$10`=ring/test gate-special |
| filt-lo   | `+$78C` | →$154C | filter macro seed (cutoff stream low) |
| filt-hi   | `+$7AC` | →$156F | filter macro seed |
| FX2       | `+$7CC` | hard-restart | lo-nib → hard-restart frame count ($1679/$16B5); (hi-nib>>3) → note-on delay ($16B2) |
| pulse-st  | `+$7EC` | →$16BB | pulse-width sweep start |
| pulse-add | `+$80C` | →$167F | pulse-width sweep add |
| pulse-end | `+$82C` | →$1682 | pulse-width sweep end/limit |
| d416-build| `+$84C` | →$D416 | per-inst filter-cutoff value (lo-nib<<4 ⟶ hi composes with global, see write model §5) |

Stride between arrays is exactly $20 (e.g. `$16CC→$16EC→$170C…`). **Instrument count = 32.**

The FX byte's `bit7` = the **drum / absolute-pitch** flag (confirmed $131C `AND #$80 →
$1676`): when set, the wave-program data bytes ($187C) are written as the **frequency
HI directly** (absolute pitch, $1463) instead of being added to the note ($144B). This is
exactly research.md's "$80-$DF absolute/drum" intuition, but the flag lives in the FX byte,
not the transpose byte.

---

## 7. Program streams (wave / pulse / filter sequences)

Running-index sequence tables (offsets from BASE):

| stream | BASE+ | sentinels | meaning |
|---|---|---|---|
| wave-program ctrl | `+$86C` | `$FF`=jump (next byte = new index), `$FE`=end (hold) | per-frame waveform/control values ($165A) |
| wave-program data | `+$87C` | — | note-relative (+note) unless FX bit7 (then absolute freq-hi); `$80` bit selects |
| pulse-program     | `+$88C` | `$FF`=jump (next byte = new index) | triples driving PW sweep / direction ($1670 step, $16A9 dir, $1673 duration) |
| filter macro      | `+$89C` | `$80`=jump (next byte = new index) | global $D416 cutoff stream (one shared filter, §5 of write model) |

These are **content-by-reference** in the USF sense — extract the reachable window of each
stream (walk from each instrument's start index, following `$FF`/`$FE`/`$80` jumps until a
cycle/end), store the bytes as a typed macro program. Do NOT store the raw absolute jump
operands — re-derive jump targets as relative indices.

---

## 8. Frequency tables

- **freq-HI table = BASE+$5E8** (96 entries) — read at $12F6 `LDA $15E8,Y → $164E → $D401`.
- **freq-LO table = BASE+$588** (96 entries) — read at $12FC `LDA $1588,Y → $1651 → $D400`.

**[CORRECTION] research.md said freq-hi +$880 / freq-lo +$8E0. The real offsets are
freq-HI +$5E8 and freq-LO +$588, and the LO table comes *before* the HI table in memory.**
Note index range 0..$5F (96 = 8 octaves × 12). HT_7_1 freq-LO[0..]= `16 27 38 4B 5F 73…`,
freq-HI[0..]= `01 01 01 01 01 01…` → note 0 = $0116. These are a standard PAL note table.

The play routine ends at `RTS` at BASE+$587; the freq-LO table begins immediately at
BASE+$588. So **player code occupies BASE+$00 .. BASE+$587 (~1416 bytes)**; tables and song
data follow.

---

## 9. Memory map summary (canonical $1000 build, verified)

**FIXED** offsets (player code + the first data tables that abut it): everything up to and
including the instrument-AD array and the subtune-tempo table. **VARIABLE** (operand-
derived, §4): everything after — the rest of the instrument arrays, program streams,
subtune-track tables, pattern-ptr tables, track data, pattern data. The HT_7_1 values are
shown for the VARIABLE region for illustration only.

| BASE+ | content |
|---|---|
| `+$00` | JMP init / JMP play |
| `+$06..+$1F` | runtime config + voice shadows (init-written; not song data) |
| `+$20..+$5F` | credit text region (overwritable) |
| `+$60` | init routine |
| `+$D8` | play routine |
| `+$379,+$39D` | $D417 builds |
| `+$522` | voice finaliser ($D402/$D403/$D401/$D400/$D404,Y) |
| `+$57E` | $D418 build |
| `+$587` | end of player code (RTS) |
| `+$588` | freq-LO table (96) |
| `+$5E8` | freq-HI table (96) |
| `+$648..+$662` | per-voice work seeds ($164E etc. — runtime, not data) |
| `+$6C4` | per-subtune speed table |
| `+$6CC` | instrument AD array (32) |
| `+$6EC` | instrument SR array (32) |
| `+$70C..+$84C` | remaining 11 instrument arrays (32 each, §6) |
| `+$86C` | wave-program ctrl stream |
| `+$87C` | wave-program data stream |
| `+$88C` | pulse-program stream |
| `+$89C` | filter macro stream |
| `+$8A2..+$8CA` | per-subtune track-pointer tables (lo/hi × V1/V2/V3) + speed |
| `+$94A` | pattern-ptr-lo table |
| `+$95F` | pattern-ptr-hi table |
| `+$9xx..` | track data, then pattern data |

(Work-area addresses $1648..$16C3 etc. are RAM scratch the init clears; they are NOT
extracted. They are interleaved with the data tables in the $16xx page only because the
assembler placed the zero-initialised work vars between code and the instrument arrays.)

---

## 10. Version-dependent items (V1.0 vs V1.1)

The two SDK source files (`PLAYER_V1.0.bin`, `PLAYER_V1.1.bin`) are the editor's tokenised
source + symbol table. The symbol tables differ:

- **V1.0** symbol table ends `...PT1.PR1.PR1.KBYTER.AR.AR.AR.FL.PL.PL.PL...` (one block of
  pattern/instr symbols).
- **V1.1** symbol table has an **extra block**: `...KBYTE ATPS TR1.TR1.TR3.TR2.TR2.TR3.
  (×many) ADPDSD QWERTY... DACMP RUNSPEEES SDQW...`. The repeated `TRn.` symbols and the
  `RUNSPEEES` ("run speed") / `DACMP` symbols suggest V1.1 **expanded the per-voice track
  bookkeeping and/or the speed handling**. V1.1's source also exposes the entry label
  `IRQ  LDA $FB` plainly (the play routine starts by saving zp $FB/$FC — matches HT_7_1
  play at $10D8: `LDA $FB / PHA / LDA $FC / PHA`).

**RESOLVED discriminator** (from `sidid_signature_analysis.md` §4, real-SID cross-check on
`Bzyk/Good_World.sid` V1.0 vs `Shogoon/Tribute_to_Laxity.sid` V1.1):

| field | V1.0 (Good_World) | V1.1 (Tribute_to_Laxity) |
|---|---|---|
| $D417 shadow | **$101F** (`AD 1F 10`) | **$101E** (`AD 1E 10`) |
| sig routine addr | ~$1362 | ~$1387 (shifted ~$25 later) |
| resonance temp | $157A | $15A4 |
| per-voice set-mask table | `$1691,X` | `$16C4,X` |

So tag version per-SID by the byte at the sig-region `AD ?? 10` operand: $1F=V1.0, $1E=V1.1.
V1.1 inserts ~$25 bytes (the symbol table's extra `TRn`/`RUNSPEEES` block — likely the
4×/6× multispeed machinery, which is dead in PSID renders, write-model §0). **Remaining
OPEN:** confirm V1.1's *data-table* offsets relative to its (shifted) code are still
operand-derivable the same way (they should be — the dataflow §4 approach reads operands at
code-relative addresses, which the $25 shift moves uniformly).

---

## 11. Relocated / packed variant (Scortia and similar)

Scortia (`MUSICIANS/R/Randy/Scortia.sid`, load $3000, init $45B3, play $45F2, 4 subtunes)
bundles **two copies of the player** (voice finaliser found at both $3522 and ~$4979;
$D417 at $3379/$339D and $4979/$499D; $D418 at $357E and $4B7E). The second copy bakes
**absolute** freq addresses ($85E8) rather than relocated ones, i.e. the data was moved but
some code copies kept original assembly addresses. **OPEN:** the packed/multi-copy build is
out of scope for the first migration; target the 1035 clean `init=$1000` tunes first, then
revisit packed builds (likely the Adrenalin-style "multiple independent songs" pattern).

---

## 12. Extraction order (checklist)

1. Parse PSID; confirm real load = first 2 data bytes; require `init=$1000`, JMP table at
   `+$00 = 4C 60 10 / 4C D8 10`. Reject (defer) packed/relocated builds (§11).
2. Fingerprint/anchor (§1.2) → confirm engine + (eventually) version.
2b. **Resolve all table bases by reading code operands at their fixed code addresses** (§4):
   pattern-ptr-lo/hi (BASE+$251/$259), subtune-track base (BASE+$064), the instrument array
   bases (BASE+$30E,$314,$31A,$322,$331,$337,…) and derive instrument count N = SR−AD.
   freq-LO/HI, AD array and tempo table are at fixed BASE+$588/$5E8/$6CC/$6C4.
3. Read subtune table (§2): subtune count = PSID `songs`; per subtune get V1/V2/V3 track
   pointers + speed byte.
4. For each subtune/voice, walk track stream (§3) → ordered list of (transpose, pattern#,
   jump, loop, end).
5. Resolve pattern pointers (§4), decode each referenced pattern into (note, command)
   steps (§5).
6. Decode the 32 instruments (§6) + their referenced program streams (§7).
7. Read freq tables (§8) — store as the engine's note→frequency map (or recognise the
   standard PAL table and parametrise).
8. Emit USF: notes from pattern steps, transposes from track, instruments parametrised
   over the macro arrays, glissando as a freq-slide effect, drum/abs as the absolute-pitch
   instrument flag, pulse/filter as parametric automation. (Detailed write semantics for
   verification: spec_write_model.md.)

## Leads to follow

- **Confirm pattern-count discriminator** (§4 OPEN): is it `(BASE+$95F) − (BASE+$94A)`?
  Decode two more tunes (e.g. `MUSICIANS/A/Amadeus_Attic/Conqueror.sid`,
  `MUSICIANS/D/Data/Trigonomy.sid`) and check.
- **V1.0 vs V1.1 byte fingerprint** (§10 OPEN): disassemble a known-V1.1 $1000 SID and diff
  play+$06. Need to identify which HVSC tunes are V1.1 (the SDK ships V1.1; find a 1.1 export).
- **Packed/relocated builds** (§11 OPEN): map Scortia's two-copy / 4-subtune scheme; decide
  whether it's a single engine with two data pools or a true compilation.
- **Per-subtune count** (§2 OPEN): is it bounded by the $07 mask (max 8) and terminated by a
  zero pointer, or by PSID `songs`? Decode the 8-subtune `Touldie/Ashido.sid`.
