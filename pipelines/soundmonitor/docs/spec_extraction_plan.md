# Soundmonitor / MusicMaster — Binary Extraction Plan (binary → USF)

> **Provenance**
> - **primary source:** `local: tmp/jc64/doc/example/SoundMonitor_shades.dis` (gzip JC64dis project file; decoded with `gunzip -c`). JC64dis-authored disassembly of the "Shades (filter corrected)" SID by Chris Hülsbeck, (c) 1986 Markt & Technik. Hand/auto-annotated with routine + state-variable labels.
> - **secondary (variant):** `local: tmp/jc64/doc/example/Rockmonitor2.dis`, `Rockmonitor5.dis` (same JC64dis cell format).
> - **address census:** `local: hvsc84.db` (READ-ONLY), `engine='Soundmonitor'`, 3625 rows.
> - **blog (REQUESTED, UNAVAILABLE):** `https://namelessalgorithm.com/computer_music/blog/soundmonitor/` — returned **HTTP 404** on the bare path and **403** on the index over WebFetch; `web.archive.org` is blocked from this environment. The page is confirmed to exist (it is the top WebSearch hit) but could not be fetched. All format facts below are grounded in the JC64dis disassembly instead, which is a primary artifact and strictly higher-reliability than a blog. See `## Leads to follow`.
> - **fetched_via:** Bash `gunzip -c` + `tr` cleanup; WebSearch; sqlite3 via python.
> - **fetch_date:** 2026-06-13
> - **reliability:** HIGH for everything cross-checked in the disassembly (routine flow, register writes, the 64-byte instrument map which is reproduced *verbatim as a comment block in the .dis*); MEDIUM for the editor-facing "SP TRKx TR ST" row model in the briefing (the **replayer does not use that layout** — see §0); OPEN items explicitly flagged.

---

## §0 — CRITICAL REFRAME vs. the briefing's working model

The briefing's "master track/step table rows `SP TRKx TR ST 00`" and "24-parameter sound patches" describe the **editor's on-screen data model**. The **MusicMaster replayer** — the thing 3,625 HVSC SIDs actually run, and the thing whose `$D400-$D418` write stream is our verification target (CORE TENET) — reads a **different, compiled layout**:

- The master sequence is **four parallel 16-bit pointer arrays** (`voice1TableIndex`, `voice2TableIndex`, `voice3TableIndex`, `instrTableIndex`), indexed by an order counter, **plus** three parallel transpose byte-arrays and a `progIndexTable` order list. There is no `SP TRK TR ST` row in the replayer.
- The "sound patch" the replayer dereferences (`($AB)`) is a **64-byte ($40) record**, not 24 bytes. 24 is the editor's *user-editable parameter count*; the compiled record is $40 wide and bundles **all three voices' ADSR + a global filter EG + per-voice portamento/vibrato/PWM state + tempo + fade** in one row.

**Extraction therefore targets the replayer's compiled tables, not the editor format.** This is the SIDfinity-correct framing: USF carries musical content derived from what the replayer reads/emits, never the editor's positional artifacts.

---

## §1 — Anchor the replayer (signature, NOT a fixed address)

`hvsc84.db` shows the engine is **not** at one fixed base. Init/play address census (top rows, 3625 total):

| init | play | count | notes |
|------|------|-------|-------|
| `$C000` | `$C020` | 1182 | canonical (briefing). play = init + `$20` |
| `$C000` | `$0000` | 507 | play vector installed via IRQ; effectively init+`$20` |
| `$C000` | `$C475` | 349 | **second replayer layout**: play = init + `$475` |
| `$9FD0` | `$0000` | 236 | relocated |
| `$CBD4` | `$C020` | 207 | relocated init, fixed play |
| `$BFF0` | `$C020` | 141 | |
| `$80F8`, `$9E00`, `$CE30/31`, `$7FF8`, `$6000/$6475`, ... | | | many relocations |

`load_addr` is `$0000` for **all 3625** (the real load address is the first 2 bytes of the PSID data payload — CBM format). The `SoundMonitor_shades.dis` example is itself relocated to **init=$7000, play=$742E** (delta `$42E`).

**Two play-deltas dominate: `+$20` and `+$475`.** These are two replayer builds (likely "v1.0" vs. a later/patched MusicMaster). Treat the delta as a variant discriminator.

**Extraction step 1 — anchor by code signature, then derive base from PSID `init_addr`:**

1. Read PSID header → `init_addr`, `play_addr`, payload. Load payload to `load_addr` = first 2 bytes of payload.
2. The replayer's `play()` entry is `playSound` (label in disasm). Confirm engine identity with a **relocation-invariant fingerprint** of the `playSound`/`processNote`/`makeEffects` code (reuse `pipelines/future_composer/engine_fingerprint.py` methodology — it already does reloc-invariant FC fingerprinting). Anchor candidates: the `makeEffects` JSR chain
   ```
   jsr makePortamentoEffect / jsr makeVibratoEffect / jsr makeFilterCutEffect / jsr makeWavePulseEffect
   ```
   (four consecutive JSRs) is a strong, data-free signature.
3. From `init_addr` + the matched build's known internal offsets (below, expressed relative to the build base), compute every table address. **Do not assume $C000.**

**OPEN-1:** The exact play-delta → internal-layout mapping for the `+$475` build. *Closes by:* fingerprinting + disassembling one `play=$C475` SID (e.g. pick from DB) and diffing its table offsets against the `+$20`/Shades build. (No `+$475` .dis is in the local JC64dis set.)

---

## §2 — Internal layout of the canonical build (offsets from the Shades disasm)

JC64dis annotated each label with its absolute PC in Shades (`W7xxx` markers). Subtract the Shades base `$7000` to get **build-relative offsets** (these should hold across relocations of the *same* build; verify per §1).

### Code (relative to base $7000 in Shades)

| label | Shades PC | rel. off | role |
|-------|-----------|----------|------|
| (init entry) `initSongs` | — | — | init; in Shades it is stubbed `nop×11; lda #$01; sta soundOn; rts` |
| `makePortamentoEffect` | `$7012` | `+$012` | portamento (per-frame) |
| `makeVibratoEffect` | `$7132` | `+$132` | vibrato (per-frame) |
| `makeFilterCutEffect` | `$71C7` | `+$1C7` | filter EG (per-frame) |
| `outFilter` | `$71FB` | `+$1FB` | writes `$D415/$D416/$D417` (+`$D418`) |
| `makeWavePulseEffect` | `$72A0` | `+$2A0` | PWM (per-frame) |
| `freqV1/V2/V3` (data) | `$7357/$735E/$7365` | `+$357..` | 7-byte target-freq staging per voice |
| `frequencyHi` (data) | `$7370` | `+$370` | freq table hi, 95 bytes |
| `frequencyLo` (data) | `$73CF` | `+$3CF` | freq table lo, 95 bytes |
| `makeEffects` | `$7446` | `+$446` | the 4-JSR effect chain |
| `processNote` | `$748B` | `+$48B` | reads new note column for V1/V2/V3 |
| `setFilterVol` | `$77AD` | `+$7AD` | `stx $D418` |
| `playSoundOn` | `$77B1` | `+$7B1` | per-note (re)load of order entry |
| `swapNotePointer` | `$78A7` | `+$8A7` | swaps `$A5..$AC` ↔ `$07E9..` |
| `fadeOut` | `$78BB` | `+$8BB` | volume fade-out |

`playSound` = the play() entry (`W748B processNote` is reached from it). `freqV1` staging buffer is 7 bytes; live SID-mirror buffers `actualVoice1/2/3` are 7 bytes each (freqLo, freqHi, PWlo, PWhi, control, AD, SR).

### Zero-page pointers (set by `incProgrIndex`/`readProgIndex`)

| ZP | content |
|----|---------|
| `$A5/$A6` | pointer → **voice-1 bar/note stream** (current order pos) |
| `$A7/$A8` | pointer → **voice-2 bar/note stream** |
| `$A9/$AA` | pointer → **voice-3 bar/note stream** |
| `$AB/$AC` | pointer → **current 64-byte instrument record** (`($AB),y` everywhere) |
| `$07E9..$07F0` | shadow copy of `$A5..$AC` (double-buffer swapped each frame by `swapNotePointer`) |

### State variables ($033C–$0379, page 3) — verbatim equates from disasm

```
soundOn            = $033C   ; 1 = song active
effectFlag         = $033D   ; 1 = effects/playback active
activateNextIndex  = $033E
nextIndexTable     = $033F   ; ORDER-LIST cursor (index into progIndexTable / transp tables)
currentIndex       = $0340   ; COLUMN cursor within the current bar
actualTwoCounter   = $0341   ; tempo down-counter (frames until next column)
twoCounter         = $0342   ; tempo reload (frames-per-column)
transpVoice1/2/3   = $0343/$0344/$0345
portLevelLoV1/HiV1 = $0346/$0347   ; per-voice portamento step
portLevelLoV2/HiV2 = $0348/$0349
portLevelLoV3/HiV3 = $034A/$034B
actualPortLevelLo/Hi = $034C/$034D
actualNoteLo/Hi    = $034E/$034F   ; scratch (target freq during note proc)
specialCtrlVoice   = $0350   ; split/sound-transpose control (see §5)
delayV1/V2/V3      = $0351/$0352/$0353   ; vibrato onset delay countdown
freqLevelV1/V2/V3  = $0354/$0355/$0356   ; vibrato depth/half-period
relFreqV1/V2/V3    = $0357/$0358/$0359   ; vibrato per-tick freq delta
counterV1/V2/V3    = $035A/$035B/$035C   ; vibrato LFO phase counter
filterCountUpTime    = $035D
filterCountDownTime  = $035E
filterCountLevelLo/Hi= $035F/$0360
waveUpCounterV1/2/3  = $0361/$0362/$0363   ; PWM up ramp count
waveDownCounterV1/2/3= $0364/$0365/$0366   ; PWM down ramp count
waveAmountV1/2/3     = $0367/$0368/$0369   ; PWM step size
tableSize          = $036F   ; columns in current bar (compare vs currentIndex)
allowFilterExtraTest = $0370
actualNoteV1/V2/V3 = $0371/$0372/$0373   ; last note byte read (tie detection)
portEffectV1/V2/V3 = $0374/$0375/$0376   ; per-voice portamento mode (0/1/2)
fadeOutSpeed       = $0377
actualFadeSpeed    = $0378
actualVolume       = $0379
```
Also written: `$DC05` (CIA1 Timer A hi) loaded from instrument offset `$0E` — see §3 / OPEN-3.

---

## §3 — The 64-byte instrument / "sound patch" record (`($AB),y`)  ✅ stride confirmed = $40

The disasm reproduces the full byte map **verbatim as a comment block** (header "Index of AR/S table of editor"). Measured stride `instr01→instr02` = **8 rows × 8 = 64 bytes**. Reproduced exactly:

```
$00  Voice 1: Control   (waveform+gate base; OR #$01 for gate-on)
$01  Voice 2: Control
$02  Voice 3: Control
$03  Voice 1: Attack/Decay        -> $D405
$04  Voice 1: Sustain/Release     -> $D406
$05  Voice 2: Attack/Decay        -> $D40C
$06  Voice 2: Sustain/Release     -> $D40D
$07  Voice 3: Attack/Decay        -> $D413
$08  Voice 3: Sustain/Release     -> $D414
$09  Filter resonance             -> $D417 (via actualFilterRes)
$0A  Filter control/Volume        -> $D418 (via actualFilterCtrlVol)
$0B  Special control voice        -> specialCtrlVoice (split/sound-transpose)
$0C  Filter cut frequency low     -> $D415 (3 bits)
$0D  Filter cut frequency high    -> $D416
$0E  Timer A #1: Hi Byte          -> $DC05   (tempo? see OPEN-3)
$0F  Voice 1: portamento level low      (read in outVoice1 @ y=$0F; gates portamento)
$10  Voice 1: portamento level high
$11  Voice 2: portamento level low
$12  Voice 2: portamento level high
$13  Voice 3: portamento level low
$14  Voice 3: portamento level high
$15  Voice 1: relative freq up/down   (vibrato delta -> relFreqV1)
$16  Voice 2: relative freq up/down
$17  Voice 3: relative freq up/down
$18  Voice 1: freq level              (vibrato depth -> freqLevelV1)
$19  Voice 2: freq level
$1A  Voice 3: freq level
$1B  Voice 1: counter                 (vibrato delay -> delayV1)
$1C  Voice 2: counter
$1D  Voice 3: counter
$1E  Filter EG count up time
$1F  Filter EG count down time
$20  Filter effect for voice  (bitmask; AND with voice bit {1,2,4} to enable filter)
$21  Filter EG count level low (up/down)
$22  Filter EG count level high
$23  Voice 1: wave pulse low          (initial PW -> actualVoice1+2)
$24  Voice 1: wave pulse high  [comment says "Voice 2" but code reads V1 +2/+3 from $23/$24]
$25  Voice 2: wave pulse low
$26  Voice 2: wave pulse high
$27  Voice 3: wave pulse low
$28  Voice 3: wave pulse high
$29  Voice 1: wave up counter         (PWM -> waveUpCounterV1)
$2A  Voice 2: wave up counter
$2B  Voice 3: wave up counter
$2C  Voice 1: wave down counter       (PWM -> waveDownCounterV1)
$2D  Voice 2: wave down counter
$2E  Voice 3: wave down counter
$2F  Voice 1: wave amount (up/down)   (PWM step -> waveAmountV1)
$30  Voice 2: wave amount (up/down)
$31  Voice 3: wave amount (up/down)
$32  Table size               -> tableSize (columns per bar)
$33  Filter cut freq low  (EXTRA/secondary filter set; used when split active)
$34  Filter cut freq high
$35  Filter EG count up time   (extra)
$36  Filter EG count down time (extra)
$37  Filter EG count level low (extra)
$38  Filter EG count level high / EG mode voice (extra)
$39  Voice 1: relative (low) freq to add
$3A  Voice 2: relative (low) freq to add
$3B  Voice 3: relative (low) freq to add
$3C  Voice 1: portamento effect   -> portEffectV1   (0=glide-to-target, 1=down, 2=up)
$3D  Voice 2: portamento effect
$3E  Voice 3: portamento effect
$3F  Fade out speed   ($00 keep / $FF = "no fade" sentinel / else start fade)
```

**Extraction:** for each distinct `instr0N` pointer referenced by `instrTableIndex`, copy its 64 bytes. These ARE the USF instrument set (after de-positionalising — map each field to a USF musical parameter; do NOT store the raw 64-byte blob, per USF representation principle). Note one record packs **3 voices' worth of ADSR + a shared filter EG + tempo** — a USF "instrument" here is really a *per-order-position voice/filter/tempo preset*, so the natural USF decomposition is per-voice instrument + a filter-EG object + a tempo field, all keyed to the order position.

---

## §4 — Master sequence: pointer tables + order list

`incProgrIndex` / `readProgIndex` drive sequencing (verbatim flow):

```
incProgrIndex:
  ldx nextIndexTable
  lda progIndexTable,x
  cmp #$FF            ; END MARK
  bne readProgIndex
  lda progIndexTable+1,x   ; $FF -> next byte = LOOP/restart order index
  sta nextIndexTable
  tax
readProgIndex:
  lda progIndexTable,x
  asl                ; index*2 (16-bit table)
  tax
  lda voice1TableIndex,x  / +1  -> $A5/$A6
  lda voice2TableIndex,x  / +1  -> $A7/$A8
  lda voice3TableIndex,x  / +1  -> $A9/$AA
  lda instrTableIndex,x   / +1  -> $AB/$AC
  ... reads instrument $03..$0E (ADSR×3, filt res/vol, specialCtrl, Timer A) ...
  ... offset $32 -> tableSize ; offset $3F -> fade handling ...
useTransposition:
  ldx nextIndexTable
  lda voice1TranspTable,x -> transpVoice1
  lda voice2TranspTable,x -> transpVoice2
  lda voice3TranspTable,x -> transpVoice3
  inc nextIndexTable ; AND #$7F  (wrap at 128)
```

**Tables (Shades sizes; counts confirmed):**

| table | element | entries | bytes | indexed by |
|-------|---------|---------|-------|-----------|
| `progIndexTable` | byte (order value, `$FF`+loopidx terminates) | up to 128 (+term) | ~128 | `nextIndexTable` |
| `voice1TableIndex` | `.word` → bar stream | **128** | 256 | order value × 2 |
| `voice2TableIndex` | `.word` → bar stream | 128 | 256 | " |
| `voice3TableIndex` | `.word` → bar stream | 128 | 256 | " |
| `instrTableIndex` | `.word` → 64-byte instr record | 128 | 256 | " |
| `voice1TranspTable` | byte (2's-comp; `$01`=base) | **128** | 128 | `nextIndexTable` |
| `voice2TranspTable` | byte | 128 | 128 | " |
| `voice3TranspTable` | byte | 128 | 128 | " |

NB transpose base is **`$01`** (not `$00`): in `addTranspV1` the value is `clc; adc transpVoice1`, and the freq table is indexed by `note+transp`. A stored `$01` = +1 semitone offset baseline; values like `$FD/$FE/$FA` = negative (down), `$06/$08` = up. **OPEN-2:** confirm whether the editor's "TR (two's-complement)" maps to `transp-1` or the raw stored byte (a one-semitone bias is visible). *Closes by:* picking a known-pitch tune and matching emitted `$D400/01` against the freq table index.

**Bar/note streams (`sound0N`):** measured stride `sound00→sound01` = **64 bytes**. A bar is a fixed 64-byte buffer; only the first `tableSize` columns are played (`currentIndex` compared to `tableSize`). The three voices read **the same `currentIndex`** (column-synchronous) and `currentIndex` is `inc`'d once per column at the end of `processNoteV3`.

**Extraction order for the master sequence:**
1. From base, locate `progIndexTable`; walk it until `$FF`; the byte after `$FF` is the **loop point** (order index to jump back to) → USF `loop@N`.
2. For each order value `v` in `progIndexTable`, read `voice{1,2,3}TableIndex[v]` (bar pointers) and `instrTableIndex[v]` (instrument), and `voice{1,2,3}TranspTable[order-pos]` (transpose). NB transposes are indexed by the **order position** (`nextIndexTable`), pointers by the **order value** (`v`) — a subtle but verbatim distinction. *(See OPEN-4.)*
3. For each bar pointer, read its 64-byte stream; play only `tableSize` (from the instr record `$32`) columns.

---

## §5 — Bar/note stream decode + sentinels

The note byte for a voice is `lda ($A5),y` with `y=currentIndex` (verbatim `processNote`):

```
lda ($A5),y         ; note byte for voice 1 this column
sta actualNoteLo
beq testGateOffV1   ; $00 => REST / note-off branch
cmp #$80
beq processNoteV2   ; $80 => "+++" TIE/HOLD: skip this voice entirely
and #$7F            ; else: low 7 bits = NOTE INDEX into freq table
... (transpose add, freq lookup, gate handling) ...
```

**Note-byte grammar (replayer view):**

| byte | meaning |
|------|---------|
| `$00` | **rest / sustain-off**: if a note was playing (`actualNoteV1 != 0`) → gate OFF (`actualVoice+4 AND #$FE`, re-emit control); else nothing |
| `$80` | **`+++` tie/hold**: leave the currently-sounding note untouched (no re-gate, no freq reload) |
| `$01..$7F` | **note-on**, value = freq-table index (after `+transp`); triggers gate-on (`control OR #$01`) and full param reload |
| `$81..$FF` | high-bit-set notes other than `$80`: the `and #$80` test routes them to the gate-off/tie path while `and #$7F` would still extract a note — used by portamento ("don't re-trigger gate but slide to this note"). The portamento-active branch reads target freq into `freqV1` (not `actualVoice1`) so the per-frame `makePortamentoEffect` glides toward it. |

**The bar grid (briefing's "leftmost col = 8th, +3 successive 32nds"):** confirmed structurally — a 64-byte stream at one column-per-tempo-tick gives the 32nd-note resolution; the editor groups columns 4-per-8th visually. The replayer is agnostic — it just walks `tableSize` columns. Example `sound01` bytes: `$2D` (note), then `$B9 $BC $C0` (all ≥$80 ⇒ tie/portamento continuations of the held note across the next 3 sub-columns). So a sustained 8th note = one note byte + three `$8x` ties.

**Instrument digit + options nibble (briefing):** in the **replayer** the per-note byte is ONLY note(+tie/rest). The **instrument is per-order-position** (`instrTableIndex`), NOT per-note. The "options nibble (portamento / transpose-disable / arpeggio / sound-transpose)" is realised by **instrument-record fields + `specialCtrlVoice`**, not bits in the note byte:
- portamento ← instr `$0F/$10` (level) + `$3C..$3E` (mode);
- transpose-disable / sound-transpose / split ← `specialCtrlVoice` (instr `$0B`) with the `#$30` note threshold (`cmp #$30 / bcs skipAddTransp` and the "extra filter test" split at `cpx #$30`);
- arpeggio ← see §6.

This is a **second divergence** from the editor model and must be respected in extraction: do not look for an options nibble inside note bytes.

**Sentinels summary:** bar end = `currentIndex == tableSize` (length-counted, NOT an in-stream terminator). Order end = `$FF` in `progIndexTable` (followed by loop index). Fade sentinel = instr `$3F == $FF` ("no fade").

---

## §6 — Arpeggio ("AR/S DATA")

The instrument-record block is titled **"Index of AR/S table of editor"** in the disasm — i.e. the editor's "AR/S" (Arpeggio/Sound) screen maps to these 64-byte records. No dedicated fast per-frame arpeggio table is read in the Shades play path (arpeggio there is realised through rapid order/column advance + the vibrato `relFreq` mechanism, OR via a feature not exercised in Shades). **OPEN-5:** locate the explicit arpeggio data path. *Closes by:* disassembling a tune that audibly arpeggiates and tracing which `($AB),y` offsets or which table drive the rapid `$D400/01` retriggers; candidate offsets `$39..$3B` ("relative low freq to add") are the most likely arpeggio inputs. Until then, treat arpeggio as: per-tick freq offsets sourced from instr `$39..$3B` and/or the vibrato chain.

---

## §7 — Frequency table  ✅ standard PAL, A4=440

`frequencyLo` / `frequencyHi` are **parallel 95-entry arrays** (8 octaves of 12 minus a few), indexed by `note+transp`. Verbatim first/last:
```
frequencyHi: $01,$01,... ascending ... $DD,$EA,$F8   (95 bytes)
frequencyLo: $16,$27,... ............. $28,$14        (95 bytes)
```
This is the **standard HVSC PAL freq table** (comment: "A4=440 HZ (PAL) | A4=457 HZ (NTSC)"). For USF we don't store it — note indices map to musical pitch directly. Index 0 ≈ lowest note. **OPEN-6:** the exact MIDI anchor of index 0 (which octave). *Closes by:* one `$D400/01` capture vs. the table (trivial once a build runs).

---

## §8 — Ordered EXTRACTION CHECKLIST

1. **Parse PSID** → `init_addr`, `play_addr`, payload; `load = payload[0:2]`; map payload into a 64 KB image at `load`.
2. **Fingerprint** the player at `init_addr`/`play_addr` (reloc-invariant; anchor on the 4-JSR `makeEffects` chain + the `outVoice1` `$D400…$D404`-last write pattern). Reject non-Soundmonitor. Record **build variant** by play-delta (`+$20` vs `+$475` vs other). *(§1, OPEN-1)*
3. **Derive table addresses** from `init_addr` + the matched build's relative offsets (§2 table). For an unknown relocation, locate tables by following the ZP-pointer loads inside `readProgIndex` via a tiny code scan (find the `sta $A5/$A7/$A9/$AB` operands → those are `voiceNTableIndex`/`instrTableIndex`).
4. **Read `progIndexTable`**: walk until `$FF`; capture order sequence + loop index (byte after `$FF`) → USF orderlist + `loop@N`. *(§4)*
5. For each order value, **read the 4 pointer tables** (`voiceN`, `instr`) and the **3 transpose tables** (by order position). *(§4, OPEN-4)*
6. **Collect distinct 64-byte instrument records**; decode per §3 into per-voice instrument + filter-EG + tempo(+fade) USF objects (NOT raw bytes). *(§3, OPEN-3)*
7. For each distinct **bar pointer**, read its 64-byte stream; with `tableSize` (instr `$32`) decode `tableSize` columns per §5 grammar (`$00`=rest, `$80`=tie, `$01-$7F`=note index, `$8x`=portamento-tie). *(§5)*
8. **Frequency**: map note index (+transpose) through the standard PAL table to pitch. *(§7, OPEN-6)*
9. **Arpeggio**: capture instr `$39..$3B` (and resolve OPEN-5).
10. **Verify** by rebuilding and comparing the `$D400-$D418` write stream per `spec_write_model.md` (Mode-1 instruction-stream verdict; `verify_cycle.compare_instruction_stream`). Pick the trichotomy variant if our init differs from the original's.

---

## §9 — Variant / version notes

- **Two replayer builds in HVSC** by play-delta: `play=init+$20` (≈1689 SIDs across `$C000`/`$BFF0`/`$CBD4`/… bases) and `play=init+$475` (≈350+). Same engine family; offset map of the `+$475` build is OPEN-1.
- **Rockmonitor II / V** (`Rockmonitor2.dis`, `Rockmonitor5.dis`): JC64dis applies the **same symbol set** (`playSound`, `makeVibratoEffect`, `makeWavePulseEffect`, `frequencyHi`, `sound00` all present) ⇒ Rockmonitor is a **hacked Soundmonitor** sharing the core write model. Rockmonitor5 even uses `init=$C000`. Treat Rockmonitor as a sub-variant; re-fingerprint and re-derive offsets (they relocate, e.g. Rockmonitor2 `init=$7FDD`). **OPEN-7:** byte-level deltas (do Rockmonitor builds add registers/effects or change the instr stride?) — *closes by* the §2/§3 offset diff on the two local .dis files.
- HVSC `Soundmonitor` = **3625** SIDs, PSID v2, sizes 4.7 KB–52 KB (avg 15 KB). All `load_addr=$0000` (CBM-in-payload).
- The `SoundMonitor_shades.dis` `initSongs` is **stubbed** (`nop×11`) because Shades is a ripped/relocated single-tune PSID; the canonical `$C000` init does more (clears state page $033C-$0379, copies pointers). **OPEN-8:** capture the canonical init's writes from a `$C000` SID for the priming half of the trichotomy. *Closes by:* `siddump --writelog` on the first frames of a `$C000` tune.

---

## Leads to follow

- **OPEN-1** `+$475` build internal offsets — fingerprint + disasm a `play=$C475` DB tune.
- **OPEN-2 / OPEN-4** transpose semantics: stored byte vs editor "TR", and the index-by-order-position vs index-by-order-value distinction — confirm against an emitted `$D400/01` stream.
- **OPEN-3** instr `$0E → $DC05` (Timer A): is tempo CIA-driven *or* the `twoCounter` frame divider (or both)? Census PSID `speed` bits for the engine; ear/trace one tune. (Determines whether to use the CIA per-play verdict path.)
- **OPEN-5** explicit arpeggio data path (instr `$39..$3B`?).
- **OPEN-6** freq-table index→MIDI anchor.
- **OPEN-7** Rockmonitor byte-level deltas (`Rockmonitor2.dis`/`Rockmonitor5.dis`).
- **OPEN-8** canonical `$C000` init writes (priming).
- **BLOG** `namelessalgorithm.com/computer_music/blog/soundmonitor/` is 404/403 + archive blocked here — re-fetch from a network with archive.org access (or Google cache) to cross-check the editor-facing field names; not required for extraction since the disasm is authoritative.
