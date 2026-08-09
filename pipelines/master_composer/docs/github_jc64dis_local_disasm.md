# Master Composer — JC64dis annotated disassembly (decoded)

> **Provenance**
> - source: `local: tmp/jc64/doc/example/Master_Composer.dis` (JC64dis project file, gzip'd custom serialization), cross-checked against the live binary `hvsc85/MUSICIANS/K/Kleimeyer_Paul/Maniac.sid`
> - fetched_via: `gunzip -c` of the .dis (2,903,414 bytes uncompressed) + record parse for labels/comments; `tools/seed_disassembly.py` on Maniac.sid for the ground-truth instruction listing; `tools/siddump --writelog` to validate the write model
> - fetch_date: 2026-06-13
> - author of the JC64dis project: Stefano Tognon / Ice Team (the JC64dis "doc/example" annotation set). Engine by Paul Kleimeyer / Access Software Inc., 1983.
> - content_date: JC64dis distribution snapshot (the `.dis` ships with JC64dis); engine 1983–1984
> - reliability: **PRIMARY**. The annotations are a hand-labelled RE of the actual player; every address/data claim here is re-derived from the real `Maniac.sid` bytes and the libsidplayfp writelog, not taken on faith from the .dis.

The JC64dis `.dis` is a hand-annotated reverse-engineering of the Master Composer player as it appears in **Maniac.sid** by Paul Kleimeyer (the file JC64dis annotated). Maniac.sid relocates to **load $7580** — which is the canonical/dominant relocation for the family (init $7580 / play $7587). So the addresses below are directly usable; for other family members add the per-file relocation delta.

## 0. How the .dis was decoded (for re-running)

```
gunzip -c tmp/jc64/doc/example/Master_Composer.dis > Master_Composer.dis.raw   # 2.9 MB
```

The raw stream is a JC64dis `MemoryDasm` serialization: PSID-header text, then the relocated memory image, then a per-byte attribute table (the long `DDDD…`/`!!!!`/`AAAA…` runs are JC64dis data-type/comment-index arrays), then a per-location record block (offset ≈ 886000 → EOF). Each location record carries: byte value, type marker (`NONE` / `REL` — `REL` = a relocatable byte), an optional **comment**, an optional **label** (`\x05'W'<4hex>` user address token followed by `\x01\x00\x09<label>`), and optional **block-comment** (`=====` banner). 22 user labels and the full per-register comment set were recovered. The instruction listing here is re-disassembled from `Maniac.sid` itself (authoritative) and cross-named with the JC64dis labels — saved at `docs/src/Maniac_seed_disasm.s` and `docs/src/jc64dis_labels.txt`.

## 1. Routine label map (JC64dis labels, grounded to real addresses)

For Maniac (load $7580). Offsets are relative to load.

| Addr | +off | JC64dis label | Role |
|------|------|---------------|------|
| $7580 | +$000 | (init) | Init: `LDA #$01 / STA $7588 / BNE $75A8`. $7588 = "song active" flag. |
| $7587 | +$007 | `playSound` | Play entry: `LDA #$00 / BNE $75BC` (the `#$00` then `BNE` is a relocation-friendly always-branch; falls to the speed-counter path). |
| $758D | +$00D | `gateOff` | Gate-off all voices: `AND #$FE` on $D404, $D40B, $D412. (**Engine bug**: the third result is written back to **$D404**, not $D412 — JC64dis comments all three as "Voice 1: Control registers". The decaying-hum-at-song-end bug.) |
| $75A8 | +$028 | — | Init tail: clears $7944/$7946, `JMP $77E5`. |
| $75B3 | +$033 | `sub_75B3` | Reload speed counter from bar-duration table. |
| $75BC | +$03C | — | Per-frame head: `DEC $7945` (speed counter); if not 0 → `RTS` (hold). |
| $75C4 | +$044 | — | Counter expired → advance note: reload counter, `INC $7943` (note idx), end-of-bar / end-of-block tests. |
| $75F1 | +$071 | `nextBlock` | `INC $7941` (block idx); compare to page block-end table `$7FE8,y`; else `nextPage`. |
| $7602 | +$082 | (nextPage) | `INC $7940` (page idx); compare to `$794A` (last page); else `stopSound`. |
| $7610 | +$090 | `stopSound` | **PSID-patched**: writes CIA1 timer `$DC04=$1B / $DC05=$41`, clears $7588, then `JMP gateOff`. JC64dis comment: *"PSID hack: this was a SEI"*. |
| $762A | +$0AA | `outTimbre` | **THE block-register-write routine.** Full 3-voice SID snapshot from the per-block tables, indexed by block# in X. Detailed in §3. |
| $7690 | +$110 | (setPage) | Load page's first block: `LDY $7940; LDA $7FD0,y → $7941`. |
| $7699 | +$119 | (startBlock) | Per-block setup: load CIA timer from `$7F50,y`/`$7F90,y` (**tempo**), set CIA1 ICR bit ($DC0E ORA #$10), reload speed via sub_75B3, load #notes `$7E50,y → $7942` and note-start `$7ED0,y → $7943`. |
| $76C4 | +$144 | `loopMulty` | Compute current-bar data pointer: `ASL a ×6 / ROL $7948` (= measure×64) then `+ $7F` hi → bar-data base in $7947/$7948. |
| $76DC | +$15C | — | Editor keyboard decode (keys $40/$03/$08/$3B/$38 → action codes). Not musically active under PSID. |
| $7700 | +$180 | `noUsedKey` | "Stop sound" key action. |
| $7702 | +$182 | — | Store key action → $7944. |
| $7729 | +$1A9 | `releaseV1` | V1 gate-off keeping waveform: `LDX $7941; LDA $7990,x; AND #$FE → $D404`. |
| $7737 | +$1B7 | `outNoteV1` | V1 note: freq lo `$7881,note → $D400`, hi `$78E0,note → $D401`, then `outCtrlV1`. |
| $776A | +$1EA | `releaseV2` | V2 gate-off: `$79D0,x AND #$FE → $D40B`. |
| $7778 | +$1F8 | `outNoteV2` | V2 note: `$7881,note → $D407`, `$78E0,note → $D408`, then `outCtrlV2`. |
| $77AE | +$22E | `releaseV3` | V3 gate-off: `$7A10,x AND #$FE → $D412`. |
| $77BC | +$23C | `outNoteV3` | V3 note: `$7881,note → $D40E`, `$78E0,note → $D40F`, then `outCtrlV3`. |
| $77CF | +$24F | — | If $7946≠0 `JSR $CB51` (editor-only external routine; $7946=0 under PSID so skipped). `RTS`. |
| $77DA | +$25A | — | End-of-bar → next measure: `INC $7942; LDA #$01 → $7943; JMP $76BF`. |
| $77E5 | +$265 | — | Init body: JC64dis comment *"This block set up IRQ (patched into PSID to be avoided)"*. NOP'd; `JMP $77F8`. |
| $77F8 | +$278 | — | Init: reload speed from `$7950,$7FD1`, clear CIA1 TOD ($DC08-$DC0B), `LDA #$01 → $7940` (start at page 1), `JMP $7690`. |
| $7828 | +$2A8 | `sub_7828` | Clear $7948 hi, load #notes. |
| $7831 | +$2B1 | `outCtrlV1` | V1 retrigger: `LDX $7941; LDA $7990,x; AND #$FE → $D404` (gate off) then `ORA #$01 → $D404` (gate on). |
| $7842 | +$2C2 | `outCtrlV2` | V2 retrigger via `$79D0,x → $D40B`. |
| $7853 | +$2D3 | `outCtrlV3` | V3 retrigger via `$7A10,x → $D412`. |
| $7864 | +$2E4 | — | Editor/player mode branch on $7946. |
| $7940 | +$3C0 | `pageIndex` | **Player state vars start here** (see §4). |
| $7943 | +$3C3 | `noteIndex` | Note index within current bar (Y for bar reads). |
| $7944 | +$3C4 | `keyAction` | Last keyboard action code (editor). |
| $7D51 | +$7D1 | `filterRes` | Per-block filter resonance/routing table. |
| $7D91 | +$811 | `filterVol` | Per-block filter-mode/volume ($D418) table. |
| $7ED1 | +$951 | `noteTable` | Per-block note-start-index table base. |
| $8012 | +$A92 | `irqRetVal` | IRQ-vector save/restore stub (editor; patched out under PSID). |

## 2. Per-frame `$D400-$D418` write model (the verification target)

`play()` ($7587) runs once per VBlank (PAL 50 Hz). Each invocation:

1. **`DEC $7945`** (speed/duration counter). If still nonzero → frame emits **only the gate-off writes** of the current note row's voices (`outCtrlV*`'s `AND #$FE` half can fire on transitions) and returns. Most frames are pure holds (no writes).
2. **When the counter hits 0** → advance to the next 16th-note row (`INC $7943`). Then for each voice V1/V2/V3 read the bar byte and emit:
   - byte `$00` → **rest/hold**: no write (note sustains).
   - byte `$64` → **gate release**: `LDA $79x0,blk; AND #$FE; STA $D4xx` (waveform kept, gate bit cleared). One write.
   - byte `$01..$63` → **note on**: `freq_lo = $7881,byte → $D4xx+0`, `freq_hi = $78E0,byte → $D4xx+1`, then **`outCtrlV*` retrigger**: `ctrl = $79x0,blk; AND #$FE → $D4xx` (gate off) then `ORA #$01 → $D4xx` (gate on). Four writes: freq lo, freq hi, ctrl-off, ctrl-on.
3. **On block change** (`nextBlock`/`startBlock`) → **`outTimbre` dumps a full 17-register snapshot** (see §3) before the note row.

**The per-voice control register ($D404/$D40B/$D412) waveform comes from the block table** (`$7990`/`$79D0`/`$7A10` indexed by block#), gate bit toggled per note. So a "block" is exactly an instrument-state snapshot, swapped wholesale.

### Validation against libsidplayfp writelog (Maniac, frame 0)

`tools/siddump Maniac.sid --writelog` first frame, decoded `cycle:reg:val` (reg = $D4xx low byte):

```
40:18:0F                                   ; VOL=$0F (init/gateOff)
321:05:09  329:0C:4A  337:13:4B            ; V1/V2/V3 AD   ($D405/$D40C/$D413)
345:06:00  353:0D:09  361:14:09            ; V1/V2/V3 SR   ($D406/$D40D/$D414)
369:02:99  377:09:FF  385:10:99            ; V1/V2/V3 PW_LO($D402/$D409/$D410)
393:03:01  401:0A:07  409:11:05            ; V1/V2/V3 PW_HI($D403/$D40A/$D411)
417:17:00                                  ; RES/FILT ($D417)
429:18:4C                                  ; VOL/MODE ($D418)  ← per-block
437:15:03  445:16:28                       ; FC_LO/FC_HI ($D415/$D416)
                                           ; ── then the first note row ──
665:00:30  673:01:04                       ; V1 freq lo/hi (note play)
693:04:40  699:04:41                       ; V1 ctrl off($40) then on($41) = retrigger
758:07:1E  767:08:19  787:0B:40  793:0B:41 ; V2 freq + ctrl retrigger
858:0E:1F  867:0F:15  887:12:40  893:12:41 ; V3 freq + ctrl retrigger
```

A later sustaining frame emits only `…:04:40 …:0B:40 …:12:40` (gate-off on the three voices) — confirming the hold/retrigger model exactly.

## 3. `outTimbre` — the block-register-write routine (+$0AA)

`LDX $7941` (current block index, 0-based into 64-entry tables), then 17 stores in this fixed order:

| Source table (Maniac addr / +off) | → SID reg | meaning |
|---|---|---|
| `$7A50,x` /+$4D0 | `$D405` | V1 Attack/Decay |
| `$7A90,x` /+$510 | `$D40C` | V2 Attack/Decay |
| `$7AD0,x` /+$550 | `$D413` | V3 Attack/Decay |
| `$7B10,x` /+$590 | `$D406` | V1 Sustain/Release |
| `$7B50,x` /+$5D0 | `$D40D` | V2 Sustain/Release |
| `$7B90,x` /+$610 | `$D414` | V3 Sustain/Release |
| `$7BD0,x` /+$650 | `$D402` | V1 PW lo |
| `$7C10,x` /+$690 | `$D409` | V2 PW lo |
| `$7C50,x` /+$6D0 | `$D410` | V3 PW lo |
| `$7C90,x` /+$710 | `$D403` | V1 PW hi |
| `$7CD0,x` /+$750 | `$D40A` | V2 PW hi |
| `$7D10,x` /+$790 | `$D411` | V3 PW hi |
| `$7D50,x` /+$7D0 | `$D417` | RES/filter-routing |
| `$7D90,x` /+$810 | `$D418` | filter-mode + master volume (two `NOP`s before the `STA` — patched space) |
| `$7DD0,x` /+$850 | `$D415` | filter cutoff lo |
| `$7E10,x` /+$890 | `$D416` | filter cutoff hi |

Waveform/control ($D404/$D40B/$D412) is **not** in `outTimbre` — it is applied per-note in `outCtrl*` from the three control tables at `$7990`/`$79D0`/`$7A10`.

JC64dis names each `STA` site exactly as above ("Generator 1: Attack/Decay", "Voice 1: Wave form pulsation amplitude (lo byte)", "Filter resonance control/voice input control", "Select volume and filter mode", "Filter cut frequency: lo byte (bit 2-0)", "Filter cut frequency: hi byte", "Voice N: Control registers").

## 4. Binary data layout (the extraction target) — Maniac, load $7580

All offsets relative to load. Verified by reading the actual bytes.

| Region | +off (Maniac addr) | Size | Layout |
|---|---|---|---|
| Init / play / gateOff | +$000 ($7580) | ~13 B | entry stubs |
| Player code | +$00D … +$2FF | ~755 B | the routines in §1 (player ≈ 768 B) |
| **freq LO table** | +$301 ($7881) | 96 B | note-freq low bytes; **indexed by note value 1..$5F directly** (`$7881,note`). Index 0 unused. |
| **freq HI table** | +$360 ($78E0) | 96 B | note-freq high bytes (`$78E0,note`). For Maniac a clean 8-octave chromatic ramp ($00,$01,…$EE). Tuning per file (≈ 450 Hz NTSC / 433.5 Hz PAL default). |
| **player state vars** | +$3C0 ($7940) | 16 B | live state, see below. |
| **bar-duration table** | +$3D0 ($7950) | up to 127 B | duration (in VBlank ticks) per bar/measure; the speed counter $7945 is loaded from here. |
| **block param tables** | +$410 … +$8CF | 19 × 64 B | the per-block SID-register columns of §3 **plus** the 3 control tables $7990/$79D0/$7A10. Each column is 64 bytes (one per block 0..63). |
| **sequence/page tables** | +$8D0 … +$A7F | several × ≤64 B | per-block #notes `$7E50`, per-block note-start `$7ED0`, per-page CIA-lo `$7F50` / CIA-hi `$7F90`, per-page first-block `$7FD0`, per-page last-block `$7FE8`. |
| `irqRetVal` IRQ stub | +$A92 ($8012) | ~36 B | editor IRQ save/restore; NOP'd / patched under PSID. A "MANIAC"/title string sits in the slack just before it ($8001). |
| **bar / measure note data** | from +$ABF ($803F) onward | 64 B × N bars | the music. Maniac: bar M (1-based) base = `$803F + (M-1)*$40`. 80 bars fit. |

### Player state vars ($7940, +$3C0)

```
$7940 pageIndex   current page (1-based; init sets #$01)
$7941             current block index (into 64-entry param tables)
$7942             current measure/bar index (drives loopMulty pointer)
$7943 noteIndex   current 16th-note row within the bar (1..16)
$7944 keyAction   editor key action (player: stop code)
$7945             speed/duration counter (DEC each frame; reload from bar-duration table)
$7946             editor-mode flag (0 under PSID → skips $CB51 editor call)
$7947/$7948       bar-data pointer (lo/hi), = measure*64 + base; voices read base+$10/$20/$30
$7949             #notes of current block (copy of $7E50,x)
$794A             last page of tune (page-end test)
```

### Bar / measure note data — 64-byte stride

Each bar is **64 bytes**: a 16-byte header (control/accent markers; mostly `$00` with `$04` flags) at +$00, then **three 16-byte voice rows**:

- `base + $10` … V1 row (16 sixteenth-note slots, read as `(base+$10),Y` with Y = noteIndex 1..16)
- `base + $20` … V2 row
- `base + $30` … V3 row

Each slot byte: `$00` = hold/rest, note index = freq-table index (note on), `$64` = gate release. Example (Maniac bar 1, V1): `18 64 18 64 …` = note $18 then release, eight times = quarter-note pulses at 16th resolution.

**Note-index range.** The freq tables are 96 entries each (`$7881..$78DF` lo, `$78E0..$793F` hi — the byte right after the hi table is `pageIndex` at $7940). So musically-valid note indices are **`$01..$5F`** (95 notes). `$00` = hold and `$64` = gate-release are the two sentinels. The family-profile figure "`$01..$63`" is the nominal note space; indices `$60..$63` would read the hi-byte past the table into the vars page and are not used by real tunes. An extractor should treat 1..$5F as notes and $00/$64 as the sentinels.

**The bar-data pointer math** (`loopMulty`, $76C4): `A = measure; A <<= 6 (×64) with ROL into $7948; A = A + $FF (lo, with carry); $7948 = $7948 + $7F + carry`. Net: bar base = `$7F00 + measure*64 + $FF` ≈ `$803F` for measure 1, stepping $40. (i.e. the music data region begins right after the page tables.)

## 5. Relocation & single-player confirmation

- The .dis is for **load $7580**, the family's dominant relocation (init $7580 / play $7587). Other HVSC members relocate the same code+data elsewhere; **the player logic is identical across the family** — only absolute addresses shift (JC64dis marks every relocatable operand byte with `REL`). This is consistent with the family profile ("identical player code across all files, only relocation differs"). One disasm therefore covers the family; an extractor must read the PSID load address and apply the delta to every table base in §4.
- **CIA vs VBlank**: the original editor was IRQ/CIA-driven (the SEI, the `$DC04/$DC05` timer writes in `stopSound`/`startBlock`, the `$DC0E ORA #$10`, the $DC08-$DC0B TOD clears, and the `irqRetVal` vector stub). The PSID conversion **patched these out** (JC64dis: *"PSID hack: this was a SEI"*, *"this block set up IRQ (patched into PSID to be avoided)"*) so `play()` is called by the host at 50 Hz. The residual CIA writes (e.g. `$DC04=$1B/$DC05=$41`, per-page `$7F50/$7F90` → `$DC04/$DC05`) are leftover tempo state and still appear in the writelog but no longer drive timing under PSID. Maniac's PSID header has `speed=$01` (a CIA-speed flag bit set on subtune 1), so verification of this family should use the CIA-aware per-`play()` capture path (`siddump --writelog-per-irq`) rather than the flat per-VBI capture — see CLAUDE.md "CIA-timed tunes".

## 6. USF-relevance notes (for the eventual migration)

- **No effects engine** (no vibrato/arp/PWM/glide). Everything heard is: per-block SID-register snapshot + per-16th-note freq index + gate retrigger. This maps to USF very directly: blocks ≈ instrument/timbre presets, bars ≈ 16-step patterns at fixed 16th resolution, pages ≈ orderlist with start/end block ranges, bar-duration table ≈ per-bar tempo. Tempo lives per page (CIA timer columns) and the bar-duration counter sets note length in VBlank ticks.
- The `$64` gate-release sentinel and `$00` hold are the only two "commands"; everything else is a literal note index into the file's own freq table (so freq tables are **content, carried by value**, not engine-positional).
- The gateOff "write V3 result to $D404" quirk (the decaying-hum bug) is part of the original instruction stream and must be reproduced as-emitted for an exact writelog match (do not "fix" it).
