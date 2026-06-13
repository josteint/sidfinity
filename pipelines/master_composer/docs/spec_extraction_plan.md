<!--
provenance:
  source_url: local: tmp/jc64/doc/example/Master_Composer.dis (JC64dis project, gzip'd DataOutputStream cell format)
             upstream: https://github.com/ice00/jc64 (doc/example/Master_Composer.dis)
             annotated tune: "Maniac" by Paul Kleimeyer, (c) 1983 Access Software Inc.
                             (original at /home/ice/hvsids/MUSICIANS/K/Kleimeyer_Paul/Maniac.sid;
                              local HVSC copy hvsc84/MUSICIANS/K/Kleimeyer_Paul/Maniac.sid)
  fetched_via: local read of cloned ice00/jc64 at tmp/jc64/ (READ-ONLY). .dis decoded with a
               Python re-implementation of FileManager.readProjectFile (Java DataInputStream,
               big-endian, modified-UTF8 readUTF; project VERSION 7). Reader + extracted inB +
               cells.json + merged py65 listing live in the gitignored tmp/mc_work/.
               Binary facts cross-checked against the real bytes (tmp/mc_work/maniac_inB.bin)
               and against tools/siddump --writelog / --writelog-per-irq / --memwatch
               (libsidplayfp ground truth).
  fetch_date: 2026-06-13
  author: disassembly hand-annotated by Stefano Tognon / Ice Team (JC64dis). Player by Paul Kleimeyer.
  content_date: annotations contemporary with JC64dis; player 1983-1984.
  reliability: PRIMARY for the Maniac layout (hand-annotated disasm verified against the actual
               bytes + libsidplayfp writelog). The byte offsets below are byte-exact for Maniac
               (load $7580) and for the dominant fixed layout. CAVEAT: a second player variant
               exists with a slightly different code length / table base — see §6 (relocation).
-->

# Master Composer — binary → USF extraction plan

Paul Kleimeyer / Access Software, 1983-1984. **1,019 HVSC tunes, 0 migrated.** The DB
(`hvsc84.db`, `engine='Master_Composer'`) is the census authority.

> **Working-model corrections established this session** (verify before trusting the old `research.md`):
> 1. **NOT VBlank-timed — CIA-timed.** 984/1019 tunes have PSID `speed=$00000001` (CIA);
>    only 23 are `speed=0` (VBlank); the rest are per-subtune bitmasks. The player programs
>    **CIA-1 Timer A** (`$DC04/$DC05`) from per-block `timerALo/timerAHi` tables and the
>    editor's IRQ rewrites it every frame. ⇒ the Mode-1 verdict is the **per-IRQ** path
>    (`siddump --writelog-per-irq`), NOT the flat per-50Hz-frame path. See `spec_write_model.md` §6.
> 2. **`load_addr` is 0 in the PSID header for ALL 1019 tunes** → the true load address is the
>    embedded 2-byte little-endian prefix at the start of the data payload (`payload[0:2]`).
> 3. **init=$7580 is 74% (751/1019), not "dominant ~everything".** ~268 tunes are relocated
>    (init seen as low as $081A). play = init+7.
> 4. Note byte **`$64` = note-OFF / gate-release sentinel** (the working model's "$01–$63 = note"
>    is right for pitched notes; `$00` = rest; `$64` = release; values are 1-based freq indices).
> 5. Block-parameter tables are at **+$3D1.. with a $40 (64-byte) stride**, NOT the old "+$450,
>    64 entries each". The page tables are `fromPage` (+$A51) / `toPage` (+$A69). Note data is at
>    **+$AC0** (base pointer $7FFF), 64-byte measure records.

---

## 0. The fastest path: decode the JC64dis `.dis`

The single highest-value source is the local JC64dis project file
`tmp/jc64/doc/example/Master_Composer.dis`. It is gzip'd, then a Java `DataOutputStream`:

```
byte version(=7); UTF name/file/desc/fileType/targetType;
int len + len bytes  -> inB        (the real .sid file)
int len + len bytes  -> memoryFlags (64K)
int nCells(=65536);  per cell:
  int address; bool+UTF dasmComment; bool+UTF userComment; bool+UTF userBlockComment;
  bool+UTF dasmLocation; bool+UTF userLocation; bool isInside; bool isCode; bool isData;
  (v>0) bool isGarbage + UTF dataType; byte copy; int related; char(=u16) type;
  (v>2) byte index; (v>8) int relatedAddressBase + int relatedAddressDest;
  (v>9) UTF basicType;
int chip; ... (relocate/patch/freeze tail)
```
Full Java reader: `tmp/jc64/src/sw_emulator/swing/main/FileManager.java::readProjectFile`
(lines 1002-1100). A faithful Python reader is in `tmp/mc_work/read_dis.py`; it emits
`maniac_inB.bin` + `cells.json`. `tmp/mc_work/merge_listing.py` cross-renders the py65 disasm
with the JC64dis labels/comments → `maniac_listing.s` (the listing quoted throughout).

The `.dis` gives every routine + every table a **hand label** (`outTimbre`, `blockSpeed`,
`noteTable`, `frequencyLo`, …). This is the structural knowledge py65 cannot reconstruct.

---

## 1. Anchor the player

| Fact | Value (Maniac) | How |
|------|----------------|-----|
| PSID header `load` | `$0000` | always 0 across all 1019; **use the embedded prefix** |
| Embedded load (`payload[0:2]`, LE) | `$7580` | true base of the memory image |
| init | `$7580` (= base+$000) | header bytes [10:12] |
| play | `$7587` (= base+$007) | header bytes [12:14]; if header play=$0000, play = init+7 |
| PSID `speed` | `$00000001` (CIA) | header bytes [18:22] |
| Image span | `$7580–$943F` (7872 bytes) | base .. base+len(payload)-2 |

**sidid signature** `F0 ?? C9 64 D0 0E ?? ?? ?? ?? ?? ?? 29 FE 8D 0B D4 4C ?? ?? A8` is the
**`releaseV2` routine** (the V2 note-off path: `BEQ … ; CMP #$64 ; BNE +$0E ; … ; AND #$FE ;
STA $D40B ; JMP … ; TAY`). In Maniac it is at `$7764` (+$1E4 from load). In the Poole_Chris
variant it is at +$1A3 — **do NOT assume a fixed signature offset; scan for it** to locate the
player, then derive the table bases relative to the matched layout (§6).

---

## 2. Memory map (Maniac, load $7580) — byte-exact offsets

Two regions: (A) player code `$7580–$8013`, (B) data tables `$7881–$943F`. Offsets are
**relative to the embedded load address** — add `(realload − $7580)` for any other file.

### 2A. Player code (no musical content; the composer re-emits its own)
| Addr | +off | Label | Role |
|------|------|-------|------|
| `$7580` | +$000 | `initSongs` | `LDA #$01 : STA play+1 : BNE doInitSongs` (raises the run flag) |
| `$7587` | +$007 | `playSound` | play entry: `LDA #$00 : BNE doPlaySound : RTS` (`play+1` patched to non-0 by init) |
| `$758D` | +$00D | `gateOff` | gate-off all 3 voices (`LDA $D404 : AND #$FE : STA …` ×3) |
| `$75A8` | +$028 | `doInitSongs` | clear keyAction/isInEditor → `setIrq` |
| `$75B3` | +$033 | `setBlockSpeed` | `LDA blockSpeed-1,Y : STA speedCounter` |
| `$75BC` | +$03C | `doPlaySound` | `DEC speedCounter : BEQ generateSound : RTS` |
| `$75C4` | +$044 | `generateSound` | the per-step advance (measure/note/block/page logic) |
| `$762A` | **+$0AA** | **`outTimbre`** | **the block-register-write routine** (full SID snapshot; §4) |
| `$7690` | +$110 | `setPage` | `blockIndex = fromPage[pageIndex]` |
| `$7699` | +$119 | `setTimer` | program **CIA-1 Timer A** from `timerALo/Hi[blockIndex]`; start timer |
| `$76BF` | +$13F | `setAddr` | compute `dataAddr` = note-data pointer (§5) |
| `$76C4` | +$144 | `loopMulty` | `measureIndex × 64` via 6× `ASL/ROL` |
| `$7709` | +$189 | `testKey1` / V1 note read | read V1 note byte `(dataAddr+$10),noteIndex` |
| `$7729` | +$1A9 | `releaseV1` | note `$64`: `ctrlV1[blockIndex] AND #$FE → $D404` (gate off) |
| `$7737` | +$1B7 | `outNoteV1` | note 1..$63: `$D400=freqLo[n], $D401=freqHi[n]`, then `outCtrlV1` |
| `$7747`/`$7778` | | `testKey2`/`outNoteV2` | V2: data offset +$20 → `$D407/$D408` + `outCtrlV2` |
| `$778B`/`$77BC` | | `testKey3`/`outNoteV3` | V3: data offset +$30 → `$D40E/$D40F` + `outCtrlV3` |
| `$7831` | +$2B1 | `outCtrlV1` | `$D404 = ctrlV1[blk] AND #$FE` then `ORA #$01` (**gate retrigger, 2 writes**) |
| `$7842`/`$7853` | | `outCtrlV2/3` | same for `$D40B` / `$D412` |
| `$77DA` | +$25A | `nextMeasure` | `INC measureIndex : noteIndex=1 : setAddr` |
| `$77E5`/`$77F8` | | `setIrq`/`irqRoutine` | editor IRQ setup (`setIrq` NOPed for PSID; irqRoutine resets CIA + `pageIndex=1` + `setPage`) |
| `$7610` | +$090 | `stopSound` | end-of-song: reset CIA Timer A, clear run flag, `gateOff` (the SEI is NOPed; "PSID hack") |
| `$8014` | +$A94 | `RestoreIrq` | unused-in-PSID IRQ restore stub |

### 2B. Data tables (THE extraction target)
Offsets relative to load. **Block-parameter tables: 64-byte stride, indexed `,X = blockIndex`
(1-based; code reads them page-aligned as `$<page>50,X`).** Each holds one byte per block (≤64).

| Addr | +off | JC64dis label | Stride/size | Meaning |
|------|------|---------------|-------------|---------|
| `$7881` | **+$301** | `frequencyLo` | 95 entries | note→SID freq lo (note index 1..95; `frequencyLo-1+n` effectively, 1-based) |
| `$78E0` | **+$360** | `frequencyHi` | 96 entries | note→SID freq hi |
| `$7940` | +$3C0 | `pageIndex` | 1 | runtime: current page (1-based) |
| `$7941` | +$3C1 | `blockIndex` | 1 | runtime: current block (1-based) |
| `$7942` | +$3C2 | `measureIndex` | 1 | runtime: current measure |
| `$7943` | +$3C3 | `noteIndex` | 1 | runtime: intra-measure note step (1-based) |
| `$7944` | +$3C4 | `keyAction` | 1 | editor key state (0 in player; `$04`=stop) |
| `$7945` | +$3C5 | `speedCounter` | 1 | runtime: down-counter; reloaded from `blockSpeed[blk]` |
| `$7946` | +$3C6 | `isInEditor` | 1 | 0 in player |
| `$7947` | +$3C7 | `dataAddr` | 2 | runtime: 16-bit note-data pointer (lo at $7947, hi at $7948=`W7948`) |
| `$7949` | +$3C9 | `notes` | 1 | runtime: `notesInMeasure[blk]` cached |
| `$794A` | +$3CA | `lastPage` | 1 | **highest page index of the tune** (song-end test) |
| `$7951` | **+$3D1** | `blockSpeed` | **$40** | per-block speed (speedCounter reload; tempo divisor) |
| `$7991` | +$411 | `ctrlV1` | $40 | per-block V1 control/waveform (e.g. $41 = pulse+gate) |
| `$79D1` | +$451 | `ctrlV2` | $40 | per-block V2 control/waveform |
| `$7A11` | +$491 | `ctrlV3` | $40 | per-block V3 control/waveform |
| `$7A51` | +$4D1 | `AttackDecayV1` | $40 | per-block V1 AD (`$D405`) |
| `$7A91` | +$511 | `AttackDecayV2` | $40 | per-block V2 AD (`$D40C`) |
| `$7AD1` | +$551 | `AttackDecayV3` | $40 | per-block V3 AD (`$D413`) |
| `$7B11` | +$591 | `SustainReleaseV1` | $40 | per-block V1 SR (`$D406`) |
| `$7B51` | +$5D1 | `SustainReleaseV2` | $40 | per-block V2 SR (`$D40D`) |
| `$7B91` | +$611 | `SustainReleaseV3` | $40 | per-block V3 SR (`$D414`) |
| `$7BD1` | +$651 | `waveLoV1` | $40 | per-block V1 pulse-width lo (`$D402`) |
| `$7C11` | +$691 | `waveLoV2` | $40 | per-block V2 PW lo (`$D409`) |
| `$7C51` | +$6D1 | `waveLoV3` | $40 | per-block V3 PW lo (`$D410`) |
| `$7C91` | +$711 | `waveHiV1` | $40 | per-block V1 PW hi (`$D403`) |
| `$7CD1` | +$751 | `waveHiV2` | $40 | per-block V2 PW hi (`$D40A`) |
| `$7D11` | +$791 | `waveHiV3` | $40 | per-block V3 PW hi (`$D411`) |
| `$7D51` | +$7D1 | `filterRes` | $40 | per-block filter resonance + voice routing (`$D417`) |
| `$7D91` | +$811 | `filterVol` | $40 | per-block **filter mode + master volume** (`$D418`) |
| `$7DD1` | +$851 | `filterCutLo` | $40 | per-block filter cutoff lo (`$D415`, 3 bits) |
| `$7E11` | +$891 | `filterCutHi` | $40 | per-block filter cutoff hi (`$D416`) |
| `$7E51` | +$8D1 | `measureTable` | $40 | per-block **starting measure index** |
| `$7E91` | +$911 | `notused` | $40 | unused 64-byte slot (NOT in USF) |
| `$7ED1` | +$951 | `noteTable` | $40 | per-block **starting note index** (within the measure) |
| `$7F11` | +$991 | `notesInMeasure` | $40 | per-block note count per measure (≤16; `notes` cache) |
| `$7F51` | +$9D1 | `timerALo` | $40 | per-block **CIA-1 Timer A lo** (tempo) |
| `$7F91` | +$A11 | `timerAHi` | $40 | per-block **CIA-1 Timer A hi** (tempo) |
| `$7FD1` | +$A51 | `fromPage` | $18 (≤23) | **page table: first block of page** (`blockIndex=fromPage[page]`) |
| `$7FE9` | +$A69 | `toPage` | $29 (≤23) | **page table: last block of page** (`blockIndex>toPage[page]` ⇒ next page) |
| `$8012` | +$A92 | `irqRetVal` | 2 | engine word (not music) |
| `$8014` | +$A94 | `RestoreIrq` | code | IRQ restore stub (not music) |
| `$8040` | **+$AC0** | `data` | rest | **note/music data** (64-byte measure records; §5) |

> The page tables are split into `fromPage[page]` and `toPage[page]` (each ≤23 entries),
> NOT a single "+$A68 page table (23) start/end". The page-table semantics: page `p` plays
> blocks `fromPage[p] .. toPage[p]` inclusive (`generateSound`/`nextBlock`/`nextPage`).

---

## 3. Extraction order (binary → USF)

1. **Anchor.** Parse PSID header; `realload = payload[0:2]`. Confirm the sidid sig (`releaseV2`)
   is present (it is for the whole family). Set `delta = realload − $7580`.
2. **Locate table bases.** For the fixed layout, table base = `realload + off` (use the §2B
   `+off` column). For a variant layout (sig offset ≠ +$1E4), derive bases from the operands
   of `outTimbre`/`setTimer`/`setAddr` by dataflow (`LDA $xxxx,X → STA $D4nn` gives table↔reg
   binding directly). **Do not hardcode the absolute addresses** — see §6.
3. **Pages.** Read `lastPage` (+$3CA gives the highest page index; OPEN: confirm pages are
   1..`lastPage`). For page `p` in 1..lastPage: `(first_block, last_block) = (fromPage[p], toPage[p])`.
4. **Blocks.** For block `b` in 1..63 (only those reachable from the page table): read all 16
   per-block parameter bytes (the $40-stride tables) →
   `{ctrlV1/2/3, AD1/2/3, SR1/2/3, PWlo1/2/3, PWhi1/2/3, filterRes, filterVol, FClo, FChi}`
   plus the sequencer fields `{blockSpeed, measureTable(start measure), noteTable(start note),
   notesInMeasure, timerALo, timerAHi}`. These define the block's **full SID snapshot** + tempo
   + which measure/notes it plays.
5. **Measures + notes.** Note-data base pointer = `$7FFF + delta` (Maniac); measure `m`'s record
   = `base + m*64`. Within a record: V1 notes at `+$10..+$1F`, V2 at `+$20..+$2F`, V3 at
   `+$30..+$3F` (16 bytes = up to 16 notes each at 1-based `noteIndex`). `+$00..+$0F` = unused/meta
   (OPEN: confirm always ignored). Note byte: `$00`=rest, `1..$63`=freq index, `$64`=release.
6. **Freq tables.** `frequencyLo` (+$301, 95 bytes) + `frequencyHi` (+$360, 96 bytes). Index by
   the note byte (1-based). VERIFIED: note $18 → ($30,$04); note $37 → ($1E,$19) match the
   writelog exactly. Default tuning ≈ 450 Hz NTSC / 433.5 Hz PAL (header comment: "A4=424 PAL /
   440 NTSC"). USF stores the freq table by value (or by note→Hz if a clean mapping is derivable).
7. **Tempo.** `timerALo/Hi[block]` → CIA-1 Timer A period = the IRQ rate (and `blockSpeed` is a
   further integer divisor of note-steps). Maniac: TimerA = `$4293` ⇒ ~50.1 Hz; blockSpeed=6 ⇒
   a note step every 6 IRQs. See `spec_write_model.md` §6.

---

## 4. The block-register-write routine (`outTimbre`, +$0AA) — verbatim

When a new block starts (`setTimer` → `setBlockSpeed` → `outTimbre`), ALL these registers are
re-written from the per-block tables, indexed `,X = blockIndex`. Verbatim from `maniac_listing.s`
(order matters for the write-stream verdict; see `spec_write_model.md`):
```
outTimbre:  ($762A)
  LDX blockIndex
  LDA AttackDecayV1-1,X    : STA $D405   ; V1 AD
  LDA AttackDecayV2-1,X    : STA $D40C   ; V2 AD
  LDA AttackDecayV3-1,X    : STA $D413   ; V3 AD
  LDA SustainReleaseV1-1,X : STA $D406   ; V1 SR
  LDA SustainReleaseV2-1,X : STA $D40D   ; V2 SR
  LDA SustainReleaseV3-1,X : STA $D414   ; V3 SR
  LDA waveLoV1-1,X         : STA $D402   ; V1 PW lo
  LDA waveLoV2-1,X         : STA $D409   ; V2 PW lo
  LDA waveLoV3-1,X         : STA $D410   ; V3 PW lo
  LDA waveHiV1-1,X         : STA $D403   ; V1 PW hi
  LDA waveHiV2-1,X         : STA $D40A   ; V2 PW hi
  LDA waveHiV3-1,X         : STA $D411   ; V3 PW hi
  LDA filterRes-1,X        : STA $D417   ; resonance + routing
  LDA filterVol-1,X        : NOP : NOP : STA $D418   ; filter mode + master volume
  LDA filterCutLo-1,X      : STA $D415   ; cutoff lo
  LDA filterCutHi-1,X      : STA $D416   ; cutoff hi
  RTS
```
> NOTE: `outTimbre` does **not** write the control registers `$D404/$D40B/$D412` (waveform/gate).
> Those come from `ctrlV1/2/3[block]` inside `outCtrlVn` / `releaseVn` when each note triggers.
> The `-1,X` (1-based blockIndex) means table[0] is unused padding; index 1 = first block.

---

## 5. Note-data pointer math (`setAddr`/`loopMulty`/`get0MeasureIndex`) — verbatim

```
get0MeasureIndex: LDA #$00 : STA W7948 : LDA measureIndex : RTS   ; A = measureIndex, hi=0
setAddr:  JSR get0MeasureIndex : LDX #$06
loopMulty:  ASL A : ROL W7948 : DEX : BNE loopMulty   ; (W7948:A) = measureIndex << 6  (×64)
            CLC : ADC #$FF : STA dataAddr              ; lo = (measureIndex*64 low) + $FF
            LDA W7948 : ADC #$7F : STA W7948           ; hi += $7F (+carry)
```
⇒ **`dataAddr = (measureIndex << 6) + $7FFF`** (Maniac). Per-voice the note byte is read from
`(dataAddr + $10/$20/$30), Y` with `Y = noteIndex`. So:
- note-data base = `$7FFF + delta` (one less than the `data` label `$8040` minus the +$10 voice
  offset; measure 1 ⇒ ptr $803F ⇒ V1 first note at $804F = `data`+$0F).
- **measure record stride = 64 bytes**; V1 `+$10..$1F`, V2 `+$20..$2F`, V3 `+$30..$3F`.
- `noteIndex` is 1-based and runs 1..`notesInMeasure[block]` (≤16); `measureIndex` advances on
  measure end (`nextMeasure`).

VERIFIED note stream (Maniac measure 1, $803F): V1 = `00 18 64 18 64 18 …` (rest, note $18,
release, note $18, …), V2 = `64 37 64 30 64 36 …`, V3 = `64 34 64 2B …` — the classic
note/release 16th-note alternation. These indices resolve through the freq tables to the exact
writelog freq bytes.

---

## 6. Relocation handling (~268 tunes off $7580)

- ALL tunes carry **embedded load** (header `load=0`); read `payload[0:2]`.
- 751/1019 are load=$7580 (the canonical fixed layout in §2). The remainder relocate to other
  bases (seen as low as $081A); the player is **position-relocated** (absolute operands rewritten
  at build time by the editor's relocator).
- **OPEN / CAUTION:** the player is *not* 100% byte-identical across all files. Poole_Chris's
  `Star_Trek_II.sid` is also load=$7580 yet its sidid (`releaseV2`) sits at +$1A3 vs Maniac's
  +$1E4, and only 1434/2752 of the first $AC0 bytes match — i.e. there is **at least one second
  player variant** with a different code length and therefore different table bases. The
  immediate-operand core (`gateOff`, `AND #$FE`, freq lookups) is identical, but the table base
  offsets differ. ⇒ For robust extraction, **do not assume the §2B `+off` map for every file.**
  Two-tier strategy:
  1. Fixed-layout fast path: if the sidid is at the Maniac offset AND `outTimbre`/`setTimer`
     operands equal `realload + {$4D1.., $9D1..}`, use the §2B table.
  2. Otherwise dataflow-derive every table base from the player operands: `outTimbre`'s
     `LDA $xxxx,X : STA $D4nn` chain gives each block-param table base + its SID register; the
     `outNoteVn` `LDA $xxxx,Y : STA $D40{0,7,E}` gives `frequencyLo/Hi`; `setAddr`'s `ADC #$FF /
     ADC #$7F` immediates give the note-data base; `setTimer`'s `LDA $xxxx,Y : STA $DC04/05`
     gives `timerALo/Hi`; `setPage`/`nextBlock`/`nextPage` give `fromPage`/`toPage`/`lastPage`.
  This is the CORE-TENET-compliant approach (derive the layout from code dataflow; the composer
  re-emits its own layout). A reloc-invariant `engine_fingerprint`-style probe (cf.
  `tools/engine_fingerprint.py` for FC) should classify the variants before a wide batch.

---

## 7. What goes in USF vs. what is engine mechanism

**USF musical content:**
- Pages → ordered list of (first_block, last_block) over `fromPage/toPage` up to `lastPage`.
- Blocks → per-block instrument-ish snapshot: 3× {ctrl/waveform, AD, SR, PW lo/hi} + filter
  {res+routing, cutoff lo/hi, mode+volume} + tempo {timerA period, blockSpeed divisor} + the
  measure/note entry point {start measure, start note, notes-per-measure}.
- Measures → 3 voices × ≤16 note cells; cell ∈ {rest $00, freq-index 1..$63, release $64}.
- Freq table → note→(lo,hi) (by value, or note→Hz if invertible).

**Engine mechanism (NOT in USF; the composer re-emits its own):**
- The whole player code region $7580–$8013, the `notused`/`irqRetVal`/`RestoreIrq` slots, the
  `$01` banking, the editor key handler (`keyCheck`/`testKey*`/`editorRoutine` JSR $CB51), the
  CIA/IRQ self-rewrite, the double 1-based padding (`table-1,X`), the absolute table bases.
- The end-of-song **`stopSound`** behavior (CIA reset + clear-flag + gateOff) and the documented
  "decaying hum" — see `spec_write_model.md` §7 for whether it emits writes we must reproduce.

---

## Leads to follow
- **Variant taxonomy (highest priority).** Maniac's sidid sits at +$1E4; Poole_Chris's
  Star_Trek_II (also load=$7580) at +$1A3, with only 1434/2752 leading bytes matching ⇒ ≥2 player
  code variants with DIFFERENT table bases. Build a reloc-invariant fingerprint over all 1019
  tunes (à la `tools/engine_fingerprint.py`) to enumerate variants + per-variant table-base maps
  BEFORE coding the extractor. Until then, derive every table base by dataflow from the player
  operands (§6), never from the §2B absolute map. (Binary: all `engine='Master_Composer'` SIDs.)
- **Confirm `lastPage` / page count semantics + 1-based ranges.** `lastPage` (+$3CA) gates
  `nextPage`; confirm pages run 1..`lastPage` and that `fromPage[p]..toPage[p]` are inclusive
  block ranges for every page. (Source: `nextBlock`/`nextPage`/`setPage` $75F1-$7696; tool:
  `--memwatch 7940,7941,794A,7FD1,7FE9` over a multi-page tune to song end.)
- **Exact measure-end branch.** Transcribe the `generateSound` $75C4-$75F0 comparisons verbatim
  (`measureTable[blk]` vs `measureIndex`, `notesInMeasure[blk]`/`notes` vs `noteIndex`) so the USF
  block entry-point fields (start measure / start note / notes-per-measure) are unambiguous.
- **Freq-table length + index range.** Tables are 95 (lo) / 96 (hi) bytes; note bytes are 1..$63.
  Determine whether note indices >95 ever occur and how the engine reads off-table. Decide USF
  freq representation: by-value table vs note→Hz (default ≈ 450 Hz NTSC / 433.5 Hz PAL). (Binary:
  scan all note-data regions for max note byte.)
- **Multi-subtune tunes (16/1019).** A few carry 2-7 songs (one =64). Determine whether subtunes
  share the page/block/freq data or each has its own tables + a startsong offset. (Binary: the 16
  multi-song tunes from the DB census.)
- **Note-cell duration semantics on melodic tunes.** Verify "$00 rest holds gate / $64 releases /
  pitched retriggers" yields audibly-correct durations on a slow hymn (e.g. Deck_the_Halls), not
  just Maniac's note/release 16th alternation.
- **Reproducible decode.** `tmp/mc_work/read_dis.py` (+ `merge_listing.py`) regenerate the merged
  listing from the `.dis`; seed `pipelines/master_composer/<variant>/disassembly.s` from it at
  migration start.
- For the per-frame write-model leads (dispatch rate reconciliation, end-of-song hum modeling,
  verification-path validation), see `spec_write_model.md` "## Leads to follow".
