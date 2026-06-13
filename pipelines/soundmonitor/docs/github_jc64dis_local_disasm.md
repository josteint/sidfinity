<!--
provenance:
  source_url: local file tmp/jc64/doc/example/SoundMonitor_shades.dis (JC64dis project, gzip'd cell format)
             upstream: https://github.com/ice00/jc64 (doc/example/SoundMonitor_shades.dis)
             tune: "Shades (filter corrected)" by Chris Hülsbeck (c) 1986 Markt & Technik
  fetched_via: local read of the cloned ice00/jc64 repo at tmp/jc64/ (READ-ONLY); .dis decoded
               with a Python re-implementation of FileManager.readProjectFile (Java DataInputStream,
               big-endian, modified-UTF8 readUTF; project format VERSION 7).
  fetch_date: 2026-06-13
  author: disassembly hand-annotated by Stefano Tognon / Ice Team (JC64dis author). Player by Chris Hülsbeck.
  content_date: annotations contemporary with JC64dis; player 1986.
  reliability: PRIMARY (hand-annotated disasm of the real binary, cross-checked against the actual bytes).
-->

# SoundMonitor / MusicMaster — annotated disassembly (JC64dis, Stefano Tognon)

This is the single highest-value SoundMonitor source we have: a complete, hand-labelled
reverse engineering of the **MusicMaster replayer** (the playback engine embedded in the
SoundMonitor editor). Every routine, every zero-page state variable, and every `$D4xx`
write is named. Mined locally from `tmp/jc64/doc/example/SoundMonitor_shades.dis`.

The annotated tune ("Shades, filter corrected") is a **relocated** copy:
- PSID v2, `load=$4E40`, `init=$7000`, `play=$742E`, songs=1, **speed=$00000001 (CIA-timed)**.
- Memory image spans **$4E40–$78FF** (10944 bytes).

The header block comment (verbatim) states the lineage:
```
 SOUNDMONITOR player  by Chris Hülsbeck  1986 Markt & Technik
 SOUNDMONITOR is the editor build onto MUSICMASTER player
```

So: **SoundMonitor = editor; MusicMaster = the replayer**. In this relocated artifact the
player sits at `$7000/$742E` rather than the canonical standalone `$C000/$C020`
(see `github_sidid_signatures.md` for the canonical MusicMaster layout). The engine logic
is identical; only base addresses differ.

> The JC64dis `.dis` is a custom binary (NOT Java `ObjectOutputStream`). It is gzip'd, then a
> `DataOutputStream` stream: `byte version; UTF name/file/desc/fileType/targetType; int len + len bytes (inB = the SID file); int len + len bytes (memoryFlags); int nCells; then per cell: int address, bool+UTF dasmComment, bool+UTF userComment, bool+UTF userBlockComment, bool+UTF dasmLocation, bool+UTF userLocation, bool isInside, bool isCode, bool isData, (v>0) bool isGarbage + UTF dataType, byte copy, int related, char type, (v>2) byte index, …`. Full reader: `tmp/jc64/src/sw_emulator/swing/main/FileManager.java::readProjectFile`. The Shades project has 302 user labels, 290 user block comments, 378 per-cell user comments.

---

## 1. Memory map (this relocated artifact; add the relocation delta for others)

| Range | Label / contents |
|-------|------------------|
| `$033C–$0379` | **Zero-page-style work variables** (engine state; see §2). JC64dis shows these as KERNAL "Tape I/O buffer" because they alias `$0334+`. |
| `$4E40` | `emptyFF` (a $40-byte $FF fill block) |
| `$4E80` | `empty00` ($40-byte $00 block) |
| `$4EC0–$57FF` | **Instrument records** `instr01..instr0E` (64-byte slots) + the index/transpose tables below interleaved |
| `$5000` | `voice1TableIndex` — V1 bar-pointer table (16-bit LE pairs) |
| `$5100` | `voice2TableIndex` — V2 bar-pointer table |
| `$5200` | `voice3TableIndex` — V3 bar-pointer table |
| `$5300` | `instrTableIndex` — instrument/sound-patch pointer table (16-bit LE pairs) |
| `$5400` | `voice1TranspTable` (per-step transpose, two's complement) |
| `$5480` | `voice2TranspTable` |
| `$5500` | `voice3TranspTable` |
| `$5580` | `progIndexTable` — **master step list** (the "track/step" sequencer; `$FF` = loop marker) |
| `$5800–$66FF` | `sound00..sound3C` — **24-parameter sound patches** + bar/note data (pointers from $5000 point here) |
| `$6700` | `instr0E` |
| `$6740–$6FFF` | `unuse00..unuse22` (unused 64-byte slots) |
| `$7000` | `initSongs` (init entry) |
| `$7012` | `makePortamentoEffect` |
| `$7132` | `makeVibratoEffect` |
| `$71C7` | `makeFilterCutEffect` |
| `$7234` | `readFilterParam` |
| `$72A0` | `makeWavePulseEffect` (pulse-width sweep) |
| `$733E` | `actualVoice1..3` — **per-voice 7-byte SID shadow blocks** (§2) |
| `$7357` | `freqV1/V2/V3` — per-voice target-freq blocks (7-byte stride, lo+hi interleaved) |
| `$7370` | `frequencyHi` — **95-entry note→freq high-byte table** (A4=440 Hz PAL / 457 NTSC) |
| `$73CF` | `frequencyLo` — 95-entry note→freq low-byte table |
| `$742E` | `playSound` (play entry) |
| `$748B` | `processNote` (V1) → `$754A` V2 → `$75E6` V3 |
| `$7693/$76E3/$773F` | `outVoice1/2/3` — write the voice shadow to `$D400+` |
| `$7792` | `outFilter` — write `$D415/$D416/$D417` |
| `$77AD` | `setFilterVol` — write `$D418` |
| `$77B1` | `playSoundOn` (start-of-song setup) |
| `$77D8` | `incProgrIndex` — **advance master step + load all per-voice pointers + sound patch** |
| `$787D` | `useTransposition` |
| `$78A7` | `swapNotePointer` — double-buffer the 8 ZP pointers ($A5..$AC ↔ $07E9..) |
| `$78BB` | `fadeOut` |

ZP pointers used at runtime (set up by `incProgrIndex`):
`$A5/$A6 = voice1 note ptr`, `$A7/$A8 = voice2`, `$A9/$AA = voice3`, `$AB/$AC = instrument/sound-patch ptr`.

---

## 2. Engine state layout

### 2a. Work variables `$033C–$0379` (user-labelled)
```
$033C soundOn              $0354 freqLevelV1          $0367 waveAmountV1
$033D effectFlag           $0355 freqLevelV2          $0368 waveAmountV2
$033E activateNextIndex    $0356 freqLevelV3          $0369 waveAmountV3
$033F nextIndexTable       $0357 relFreqV1            $036F tableSize
$0340 currentIndex         $0358 relFreqV2            $0370 allowFilterExtraTest
$0341 actualTwoCounter     $0359 relFreqV3            $0371 actualNoteV1
$0342 twoCounter           $035A counterV1            $0372 actualNoteV2
$0343 transpVoice1         $035B counterV2            $0373 actualNoteV3
$0344 transpVoice2         $035C counterV3            $0374 portEffectV1
$0345 transpVoice3         $035D filterCountUpTime    $0375 portEffectV2
$0346 portLevelLoV1        $035E filterCountDownTime  $0376 portEffectV3
$0347 portLevelHiV1        $035F filterCountLevelLo   $0377 fadeOutSpeed
$0348 portLevelLoV2        $0360 filterCountLevelHi   $0378 actualFadeSpeed
$0349 portLevelHiV2        $0361 waveUpCounterV1      $0379 actualVolume
$034A portLevelLoV3        $0362 waveUpCounterV2
$034B portLevelHiV3        $0363 waveUpCounterV3
$034C actualPortLevelLo    $0364 waveDownCounterV1
$034D actualPortLevelHi    $0365 waveDownCounterV2
$034E actualNoteLo         $0366 waveDownCounterV3
$034F actualNoteHi
$0350 specialCtrlVoice
$0351 delayV1
$0352 delayV2
$0353 delayV3
```

### 2b. Per-voice SID shadow `actualVoice1..3` at `$733E` (7-byte stride)
Indexed by the SID-voice offset X = 0/7/14 (the `,X` register-stepping the engine uses everywhere):
```
+0 actualFreqLo (label actualVoice1/2/3)   +4 actualCtrl
+1 actualFreqHi                            +5 actualAD
+2 actualWaveLo  (pulse width lo)          +6 actualSR
+3 actualWaveHi  (pulse width hi)
```
`freqV1` at `$7357` is the matching **target-freq** block (same 7-byte stride; `+0`=lo, `+1`=hi; JC64dis calls the hi-byte `W7358`). Portamento/vibrato drive `actualVoice*` toward `freqV*`.

---

## 3. The 24-parameter SOUND PATCH layout (THE extraction target)

The `$5600` block comment is the per-step **work-table layout** = the sound-patch field map
that the instrument pointer `($AB),Y` reads. This is the canonical SoundMonitor patch/record
field table (verbatim from the disasm, offsets are the `Y` index used in `processNote`/`incProgrIndex`):

```
$00 Voice 1: Control            $15 V1 relative freq up/down     $2A V2 wave up counter
$01 Voice 2: Control            $16 V2 relative freq up/down     $2B V3 wave up counter
$02 Voice 3: Control            $17 V3 relative freq up/down     $2C V1 wave down counter
$03 Voice 1: Attack/Decay       $18 V1 freq level               $2D V2 wave down counter
$04 Voice 1: Sustain/Release    $19 V2 freq level               $2E V3 wave down counter
$05 Voice 2: Attack/Decay       $1A V3 freq level               $2F V1 wave amount (up/down)
$06 Voice 2: Sustain/Release    $1B V1 counter                  $30 V2 wave amount (up/down)
$07 Voice 3: Attack/Decay       $1C V2 counter                  $31 V3 wave amount (up/down)
$08 Voice 3: Sustain/Release    $1D V3 counter                  $32 Table size
$09 Filter resonance            $1E Filter EG count up time      $33 Filter cut freq low
$0A Filter control/Volume       $1F Filter EG count down time    $34 Filter cut freq high
$0B Special control voice       $20 Filter effect for voice      $35 Filter EG count up time
$0C Filter cut frequency low    $21 Filter EG count level low    $36 Filter EG count down time
$0D Filter cut frequency high   $22 Filter EG count level high   $37 Filter EG count level low
$0E Timer A #1: Hi Byte (TEMPO) $23 V1 wave pulse low            $38 Filter EG count level high / EG mode
$0F V1 portamento level low     $24 V1 wave pulse high           $39 V1 relative(low) freq to add
$10 V1 portamento level high    $25 V2 wave pulse low            $3A V2 relative(low) freq to add
$11 V2 portamento level low     $26 V2 wave pulse high           $3B V3 relative(low) freq to add
$12 V2 portamento level high    $27 V3 wave pulse low            $3C V1 portamento effect
$13 V3 portamento level low     $28 V3 wave pulse high           $3D V2 portamento effect
$14 V3 portamento level high    $29 V1 wave up counter           $3E V3 portamento effect
                                                                 $3F Fade out speed
```

Critical reads inside `incProgrIndex` ($77D8) confirm the patch layout in code:
- `$03/$04`→`actualAD1/SR1`, `$05/$06`→AD2/SR2, `$07/$08`→AD3/SR3
- `$09`→`actualFilterRes`, `$0A`→`actualFilterCtrlVol`, `$0B`→`specialCtrlVoice`
- **`$0E`→`STA $DC05`** (CIA-1 Timer A hi) — this byte IS the song tempo / IRQ rate
- `$32`→`tableSize` (bar length in steps), `$3F`→`fadeOutSpeed` ($00 = no fade, $FF = special)

And inside `processNote` ($748B): per active note it reloads from the patch via `($AB),Y`:
`$00`→`$D404` (V1 ctrl), `$1B`→`delayV1`, `$23/$24`→pulse lo/hi, `$29`→waveUp, `$2C`→waveDown.

---

## 4. Master sequencer + bar/note model

### 4a. `progIndexTable` ($5580) — the "track/step" list
A flat list of step indices (`00 01 02 … 3F` in Shades = play steps 0..63 in order).
`incProgrIndex` ($77D8) logic:
```
incProgrIndex:
  LDX nextIndexTable
  LDA progIndexTable,X
  CMP #$FF              ; end marker?
  BNE readProgIndex
  LDA progIndexTable+1,X ; $FF → next byte is the LOOP target index
  STA nextIndexTable
  TAX
readProgIndex:
  LDA progIndexTable,X
  ASL : TAX             ; step index × 2 → 16-bit pointer-table offset
  LDA voice1TableIndex,X : STA $A5 / LDA voice1TableIndex+1,X : STA $A6
  LDA voice2TableIndex,X : STA $A7 / +1 → $A8
  LDA voice3TableIndex,X : STA $A9 / +1 → $AA
  LDA instrTableIndex,X  : STA $AB / +1 → $AC      ; sound-patch pointer
  ... then load AD/SR/filter/specialCtrl/tempo/tableSize/fadeOut from ($AB),Y ...
```
So a **step** = one entry pointing simultaneously at a V1 bar, V2 bar, V3 bar, and a sound
patch. `$FF` in `progIndexTable` is the song-end/loop marker; the byte after it is the step
to jump back to (`progIndexTable+1[X]`).

### 4b. Per-step transpose
`useTransposition` ($787D) reads `voice1TranspTable[nextIndex]` → `transpVoice1` (and V2/V3).
These are two's-complement semitone offsets (Shades values: `$01`=+1 default, `$FD`=-3,
`$FF`=-1, `$06`=+6). Applied in `processNote` via `ADC transpVoice1` unless the note's
transpose-disable option is set.

### 4c. Note stream (bar) format
`processNote` reads one byte per voice from `($A5),Y` indexed by `currentIndex`:
```
processNote:
  LDY currentIndex
  LDA ($A5),Y           ; note byte for voice 1
  STA actualNoteLo
  BNE notZeroV1
  JMP testGateOffV1     ; $00 = rest / gate-off slot
notZeroV1:
  CMP #$80              ; $80 = "+++" continue/tie marker (no new note)
  BNE limitNoteV1
  JMP processNoteV2
limitNoteV1:
  AND #$7F              ; bit7 stripped = note value (1..$7F)
  ... transpose, look up frequencyHi/Lo[note], set actualFreq, gate on ...
```
Note-byte semantics (decoded from the per-voice flow):
- `$00` = empty cell → handle gate-off (`testGateOffV1`)
- `$80` = tie/hold marker (`+++` in editor) → skip, keep current note
- bit7 set on a real note (`$80|note`) = "don't re-read frequency / no retrigger" path
- bits `0..6` = note index into the 95-entry `frequencyHi/Lo` tables (after transpose add)

The 4-bit per-note **option nibble** documented in the research lives in `specialCtrlVoice`
($0350, patch byte `$0B`) + the comparisons `CMP #$30 / BCS` gating in `processNoteV1` (the
`>= $30` test selects the "extra filter test / sound-transpose" path). The portamento-enable
bit is tested via `($AB),Y` at `Y=$0F` (portamento level low) being non-zero.

`currentIndex` ($0340) is the **intra-bar 32nd-note step counter**; it advances each
`twoCounter` tick (every 2 IRQs by default — `STX twoCounter` with X=2 in `playSoundOn`),
and when it reaches `tableSize` the engine calls `incProgrIndex` to advance to the next step.

---

## 5. Per-frame SID write model (play = `$742E`)

```
playSound ($742E):
  LDA soundOn ; BEQ → stop path (LDA #$00 : STA $D418 ; silence)
  → playSoundOn the first frame after init
makeEffects ($7446):
  JSR makePortamentoEffect    ; glides actualFreq → freqV target, writes $D400/$D401,X live
  JSR makeVibratoEffect       ; relFreq oscillation, writes $D400/$D401,X
  JSR makeFilterCutEffect     ; filter EG, writes $D415 (cut lo, 3-bit) + $D416 (cut hi)
  JSR makeWavePulseEffect     ; pulse-width sweep, writes $D402/$D403,X (wave pulse)
  DEC actualTwoCounter ; when 0 → reloadCounter → fadeOut + maybe incProgrIndex + processNote
processNote ($748B):
  per voice: set actualFreqLo/Hi, actualCtrl (gate), AD/SR, pulse, then JSR outVoiceN
outVoice1 ($7693): STA $D400 (freq lo), $D401 (freq hi), $D402/$D403 (pulse), $D405 (AD), $D406 (SR), $D404 (ctrl LAST = gate edge)
outVoice2 ($76E3): same → $D407..$D40D
outVoice3 ($773F): same → $D40E..$D414
outFilter ($7792): $D415 (cut lo), $D416 (cut hi), $D417 (res/routing)
setFilterVol ($77AD): $D418 (volume + filter mode)
```

Write-order within a frame (the verification target):
1. Effect routines update freq/pulse/filter shadows and write them **live** (portamento and
   vibrato `STA $D400,X / $D401,X`; pulse `STA $D402,X / $D403,X`; filter `STA $D415/$D416`).
2. On a step boundary, `processNote` + `outVoiceN` rewrite the full voice register set,
   **`$D404`/`$D40B`/`$D412` (control) written LAST per voice** so the gate edge lands after
   freq/pulse/ADSR are in place.
3. `outFilter` then `setFilterVol` ($D418) close the frame.

The `$01` bank byte is flipped to `$36` (BASIC+KERNAL off, I/O on) around the SID writes and
restored at exit (`setBankAndExit`/`exitPlaySound`) — this is C64-RAM-under-ROM banking, NOT a
music feature. For a PSID rebuild this is irrelevant (no ROM mapped).

---

## 6. Init (`$7000`) and double-buffering

`initSongs` ($7000) in this artifact is `NOP×11 : LDA #$01 : STA soundOn : NOP : RTS` — i.e.
the relocator stubbed the real init to just raise `soundOn`; the actual per-song setup happens
lazily in `playSoundOn` ($77B1) on the first `play()`:
```
playSoundOn: clear currentIndex/nextIndexTable/actualTwoCounter, soundOn=0,
             activateNextIndex=1, effectFlag=1, twoCounter=2,
             JSR swapNotePointer : JSR incProgrIndex
```
`swapNotePointer` ($78A7) swaps the 8 live ZP pointer bytes `$A5..$AC` with a save area at
`$07E9..` — SoundMonitor **double-buffers** the per-voice note pointers so the editor can edit
one bar set while the other plays. For a clean rebuild this is mechanism, not musical content.

---

## 7. What this means for the SIDfinity extractor

- **USF musical content** = `progIndexTable` (step order + loop point) → per step
  {V1 bar ptr, V2 bar ptr, V3 bar ptr, transpose×3, sound-patch index}, each bar = a stream
  of note bytes (note | `$00` rest | `$80` tie | bit7 no-retrigger), and the 24-param sound
  patches (decoded by the §3 field map into wave/ADSR/pulse-sweep/vibrato/portamento/filter-EG
  parameters).
- **Tempo** = patch byte `$0E` → CIA-1 Timer A hi (`$DC05`); PSID `speed=1` ⇒ CIA-timed ⇒ use
  the per-IRQ capture path (`siddump --writelog-per-irq`) for verification, per CLAUDE.md.
- **NOT in USF** (engine mechanism, per the CORE TENET): the ZP shadow blocks, the
  double-buffer swap, the `$01` banking, the `unuse*`/`empty*` padding, the absolute pointer
  tables ($5000/$5100/$5200/$5300) — those are positional artifacts; USF stores the bar
  content and the step→bar mapping, and the composer re-emits its own pointer layout.

Working files for this mining session live in the gitignored `tmp/sm_work/` (decoded cells
JSON, extracted `inB` binary, labelled listing). The decode recipe is reproducible from
`FileManager.readProjectFile` as documented in the header note above.
