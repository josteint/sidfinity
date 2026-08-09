# Master Composer — SIDId signature analysis + variant/population taxonomy

> **Provenance**
> - **Generated:** 2026-06-13 by the Master Composer research cluster (SIDId + DeepSID + population).
> - **Local sources (READ-ONLY):**
>   - `tmp/dmc_hunt/sidid/sidid.cfg` (cadaver SIDId distribution copy)
>   - `tmp/dmc_hunt/player-id/config/sidid.cfg` (canonical; treated as authoritative)
>   - `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` (DeepSID's bundled SIDId DB)
>   - `hvsc84.db` (opened `file:hvsc84.db?mode=ro`, never writable)
>   - Player image disassembled from `hvsc85/MUSICIANS/E/Ekaitis_Joe/Eleanor_Rigby_Yesterday.sid`
>     (canonical `init=$7580 / play=$7587`) and `hvsc85/MUSICIANS/B/BOGG/Death.sid` (Lope variant).
> - **Web sources:** see `deepsid_master_composer.md` in this dir.
> - All three sidid.cfg files carry the **byte-identical** `Master_Composer` group; the only diff
>   between distributions is a trailing `END` token (sidid/, DeepSID) vs none (player-id/). No semantic
>   difference.

---

## 1. The `Master_Composer` SIDId group

Verbatim from `tmp/dmc_hunt/player-id/config/sidid.cfg` (lines 1257-1262):

```
Master_Composer
F0 ?? C9 64 D0 0E ?? ?? ?? ?? ?? ?? 29 FE 8D 0B D4 4C ?? ?? A8
(Patrick_Payne)
29 FE 8D 04 D4 4C ?? ?? A8 B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 AE ?? ?? BD ?? ?? 29 FE 8D 04 D4 09 01 8D 04 D4
(Lope_Pulse_Sweep)
F0 04 90 02 B0 37 A9 01 8D
```

**Format note (authority: cadaver `sidid/readme.txt`).** A bare name line begins a player; the next
line(s) are byte signatures (`??` = wildcard, `END` terminates). A name in **parentheses** is a
**sub-variant / additional signature of the SAME player** — *not* a separate engine. "Multiple
signatures can exist for one player." A `/` in a name (e.g. `TFMX/MasterComposer`) is a
family/sub-name path; that `/`-form is a *different* engine (see §4).

So this group declares **one player ("Master Composer") with three alternative fingerprint regions**.
The task brief mentioned only two sub-variants; there are in fact **three signatures total** — the head
plus `(Patrick_Payne)` plus a previously-unflagged **`(Lope_Pulse_Sweep)`**.

---

## 2. Disassembly of each signature (6502)

All three are slices of the player's **per-voice note-processing routine**. The canonical player
($7580) has three near-identical copies (one per SID voice); the head signature happens to anchor on
the **voice-2** copy (writes `$D40B`/`$D407`), `(Patrick_Payne)` on a **voice-1** copy (writes
`$D404`/`$D400`/`$D401`). They are the same code body, different voice register offsets + a slightly
different write order across player builds — exactly what produces two co-located SIDId anchors.

### 2a. `Master_Composer` head — voice note dispatch (clear-gate path)

Disassembled at `$7764` in the canonical player:

```
$7764: F0 25        BEQ  $778B      ; note == 0  -> rest, skip voice
$7766: C9 64        CMP  #$64       ; note vs $64  ($01..$63 = real note index)
$7768: D0 0E        BNE  $7778      ; if note != $64 -> play-note path (TAY; freq-table lookup)
$776A: AE 41 79     LDX  $7941      ;   note == $64 (HOLD/gate-off sentinel):
$776D: BD D0 79,X   LDA  $79D0,X    ;   load current waveform-control byte for this voice
$7770: 29 FE        AND  #$FE       ;   clear bit0 = GATE
$7772: 8D 0B D4     STA  $D40B      ;   -> voice-2 control reg, gate OFF (keeps waveform)
$7775: 4C 8B 77     JMP  $778B
$7778: A8           TAY             ; play-note path: note -> Y index
$7779: B9 81 78,Y   LDA  $7881,Y    ; freq LO table[note]
$777C: 8D 07 D4     STA  $D407      ; -> voice-2 freq lo  (NB sig wildcards the STA target byte)
$777F: B9 E0 78,Y   LDA  $78E0,Y    ; freq HI table[note]  ...
```

**Interpretation (matches the brief's hints exactly):**
- `C9 64` / `CMP #$64` = the **$01..$63 note-index vs $64 boundary**. Real note indices are `$01..$63`
  (99 entries); **`$64` is the "hold / gate-off" sentinel** that releases the current note without
  retriggering or changing the waveform.
- `29 FE 8D 0B D4` = `AND #$FE / STA $D40B` = **clear the voice-2 gate bit** (read-modify-write of the
  voice control register, preserving the waveform nibble). This is the engine's note-off mechanism.
- `4C ?? ?? A8` = `JMP` over the play-note path, then `TAY` heads the play branch (note → Y, used to
  index the frequency tables).
- `F0 ??` (head) = the rest test: note `$00` ⇒ skip the voice.

This signature is **structural and reloc-invariant**: every fixed byte is an opcode/immediate
(`F0/C9 64/D0 0E/29 FE/8D 0B D4/4C/A8`); every absolute operand low/high byte is `??`. That is why it
matches across all relocations.

### 2b. `(Patrick_Payne)` — same note core, voice-1 build with inline freq writes

Disassembled at `$772F` (≈ 53 bytes before the head, in the same routine cluster):

```
$772F: 29 FE        AND  #$FE       ; clear gate ...
$7731: 8D 04 D4     STA  $D404      ;   -> voice-1 control reg, gate OFF
$7734: 4C 47 77     JMP  $7747
$7737: A8           TAY             ; play-note path (note -> Y)
$7738: B9 81 78,Y   LDA  $7881,Y    ; freq LO table[note]
$773B: 8D 00 D4     STA  $D400      ;   -> voice-1 freq lo
$773E: B9 E0 78,Y   LDA  $78E0,Y    ; freq HI table[note]
$7741: 8D 01 D4     STA  $D401      ;   -> voice-1 freq hi
$7744: 20 31 78     JSR  $7831      ; (shared voice helper)
$7747: AD 44 79     LDA  $7944      ; later: gate-ON path
... 09 01 8D 04 D4               ; ORA #$01 / STA $D404 = SET voice-1 gate bit
```

**The `(Patrick_Payne)` delta, precisely.** This is the **identical note routine** as 2a, but:
1. it anchors on the **voice-1** copy (`$D404 / $D400 / $D401`, vs voice-2's `$D40B / $D407`); and
2. its signature is **longer** because it captures the *full* note-load sequence — the gate-off
   (`29 FE 8D 04 D4`), the inline freq-lo/hi writes (`B9 ?? ?? 8D 00 D4` / `B9 ?? ?? 8D 01 D4`), and the
   later **gate-on** (`09 01 8D 04 D4` = `ORA #$01 / STA $D404`).

It is **not a separate engine and not even a separate player revision** — it is a *second, longer
anchor into the same player body*, retained so SIDId still IDs builds whose head bytes drift slightly.
The name commemorates the composer **Patrick Payne**, who is independently documented (VGMPF wiki) as
**one of the six named composers who used Master Composer**. cadaver evidently lifted this signature
from Payne's files. **Empirical proof (see §3):** in the canonical player BOTH the head and
`(Patrick_Payne)` regions are present simultaneously, and across HVSC `(Patrick_Payne)` is **never**
seen without the head (0 files). It cannot stand alone.

### 2c. `(Lope_Pulse_Sweep)` — an EXTERNAL pulse-width-sweep add-on (real variant)

`F0 04 90 02 B0 37 A9 01 8D` does **not** appear in the canonical $7580 player. It does appear in the
**BOGG** family (e.g. `MUSICIANS/B/BOGG/Death.sid`, relocated to `$3F60`, `init=$411F`). Disassembled
at `$3F9B`:

```
$3F9B: F0 04        BEQ  $3FA1      ; sweep-direction dispatch (Z/C flags from upstream compare)
$3F9D: 90 02        BCC  $3FA1
$3F9F: B0 37        BCS  $3FD8
$3FA1: A9 01        LDA  #$01
$3FA3: 8D BC 02     STA  $02BC      ; set sweep-active flag
$3FA6: 18           CLC
$3FA7: 90 2F        BCC  $3FD8
$3FA9: AD AA 02     LDA  $02AA      ; 16-bit pulse-width accumulator (lo)
$3FAC: 38           SEC
$3FAD: ED A7 02     SBC  $02A7      ;   -= sweep step
$3FB0: 8D AA 02     STA  $02AA
$3FB3: AD AB 02     LDA  $02AB      ; (hi)
$3FB6: E9 00        SBC  #$00
$3FB8: 8D AB 02     STA  $02AB
$3FBB: AD AB 02     LDA  $02AB
$3FBE: CD B1 02     CMP  $02B1      ; bound-check vs sweep limit
$3FC1: F0 04        BEQ  $3FC7
$3FC3: 90 0E        BCC  $3FD3
$3FC5: B0 11        BCS  $3FD8
```

**Interpretation.** A **16-bit pulse-width sweep**: a running PW accumulator (`$02AA/$02AB`) is
decremented by a per-step value (`$02A7`) each frame, bound-checked against a limit (`$02B1`), with an
active flag (`$02BC`). The base Access player has **no built-in effects** (no vibrato/arp/PWM — VGMPF
+ `research.md`); the VGMPF wiki notes that *"some users added pulse width modulation externally."*
**`(Lope_Pulse_Sweep)` is exactly that external PWM add-on** — a genuine **player revision** (named
after its coder "Lope"), not just a relocation. **Migration consequence:** the 19 Lope-tagged files
emit `$D402/$D403` (PW) write streams the vanilla player never produces; they need a PW-sweep effect in
the rebuild that the base Master Composer config can omit.

---

## 3. Variant taxonomy across HVSC (1,019 files scanned)

Each Master Composer SID's depacked player image was scanned for the presence of each of the three
signature regions (reloc-invariant anchor search over `$1000..$D000`):

| head | (Patrick_Payne) | (Lope_Pulse_Sweep) | count | reading |
|:----:|:---------------:|:------------------:|------:|---------|
| ✔ | ✔ | ✘ | **984** | canonical Access player (the dominant build; both anchors co-located) |
| ✔ | ✔ | ✔ | **19**  | Access player **+ Lope external PW-sweep** (BOGG et al.) |
| ✘ | ✘ | ✘ | **13**  | heavily relocated / packed / RSID outliers — exact byte layout outside the scan, or non-vanilla build |
| ✔ | ✘ | ✘ | **2**   | minor build: head present, Payne anchor drifted |
| ✘ | ✘ | ✔ | **1**   | Lope add-on present, head anchor drifted |

**Conclusions:**
- `(Patrick_Payne)` **never** appears without the head (0 files) → it is a redundant co-anchor of the
  same player, confirming §2b. It is *not* a population in its own right.
- `(Lope_Pulse_Sweep)` is a **true variant population (~20 files)** that adds a real effect — the only
  sub-signature here that changes the emitted write stream.
- ~98.5% of HVSC Master Composer is **one identical vanilla player** (985 head-present + the 19 Lope all
  share that core) — a single migration target, in line with `research.md`'s "identical player code
  across all files (only addresses differ for relocation)."

---

## 4. `TFMX/MasterComposer` is a SEPARATE engine (name collision — confirmed)

From the same sidid.cfg (`player-id/` lines 1990-1991):

```
TFMX/MasterComposer
F0 26 B1 06 48 4A 4A 4A 4A 9D
```

Disassembled:

```
F0 26        BEQ  +$26
B1 06        LDA  ($06),Y     ; ZERO-PAGE INDIRECT note/data fetch via pointer $06
48           PHA
4A 4A 4A 4A  LSR A x4         ; extract high nibble
9D ?? ??     STA  $....,X
```

This is structurally **unrelated** to the Access Software player:

| | Access `Master_Composer` | `TFMX/MasterComposer` |
|---|---|---|
| Data fetch | **absolute-indexed** (`BD D0 79,X`, `B9 81 78,Y`) | **zero-page indirect** (`LDA ($06),Y`) |
| Note boundary | `CMP #$64` ($64 = hold) | `BEQ` + nibble split (`LSR ×4`) |
| Family | Access Software / Paul Kleimeyer (native C64 editor) | **TFMX** driver family (Chris Hülsbeck, Amiga-derived) |

- The `TFMX/MasterComposer` anchor (`F0 26 B1 06 48 4A 4A 4A 4A 9D`) occurs **0 times** in the canonical
  Access player image.
- It sits in the cfg **inside the `TFMX/...` block** (neighbours `TFMX`, `TFMX/TimeComposer`,
  `TFMX/TFX`), i.e. cadaver filed it as a TFMX sub-driver. The shared token "MasterComposer" is a
  **pure name collision** (a TFMX-side tool also called "Master Composer").
- **HVSC keeps them as distinct engine classifications:** `hvsc84.db` has `engine='Master_Composer'`
  = **1,019** and `engine='TFMX/MasterComposer'` = **5** (separate rows). The five TFMX/MC files:
  `MUSICIANS/R/Reason/Holy_Smoke_Intro.sid`, `.../Stagnant_Pictures_tune_1.sid`,
  `.../Stagnant_Pictures_tune_2.sid`, `DEMOS/M-R/MasterComposer_sample.sid`, `DEMOS/M-R/Psycho_Beat.sid`.
- (Likewise `HardTrack_Composer` (1170), `GeniusComposer`, `MusicComposer/FlashInc`, `Power-Composer`,
  etc. share the "Composer" substring but are unrelated engines — see the cfg `Composer` grep.)

**Verdict: `TFMX/MasterComposer` is a separate engine. Exclude its 5 files from any Access Master
Composer migration; they belong to the TFMX driver family.**

---

## 5. Population summary (`hvsc84.db`, read-only)

| Metric | Value |
|---|---|
| Total `engine='Master_Composer'` | **1,019** |
| Single-subtune | 1,003 |
| Multi-subtune | 16 (n=2:9, n=4:2, n=5:1, n=6:2, n=7:1, **n=64:1**) |
| `is_psid` (PSID) | 1,004 |
| RSID (`is_psid=0`) | 15 |
| `psid_version` | **2** for all 1,019 |
| `load_addr` header field | `$0000` for **all** (load addr embedded in data — standard PSID convention) |
| `pipeline` | `NULL` for all (not yet migrated) |
| songlength | min 10 s, avg 178 s, max 11,005 s (a duplicated-page marathon — matches the "~20 min" note) |

**Init/play address spread** (166 distinct init addrs — heavy relocation):

| init | play | count | note |
|---|---|------:|---|
| `$7580` | `$7587` | **751 / 750** | canonical (init/play = init+7) |
| `$4122` | `$4129` | 29 | reloc |
| `$4073` | `$407A` | 22 | reloc |
| `$1A73` | `$1A7A` | 10 | reloc |
| `$17E3` | `$17EA` | 10 | reloc |
| `$411F` | `$4129` | 9 | reloc (BOGG/Lope cluster) |
| `$2200` | — | 7 | reloc |
| `$2073` | `$207A` | 7 | reloc |
| … | | | tail of 166 distinct inits |
| any | `$0000` | 18 | **play vector = $0000** (RSID / engine installs its own IRQ; CIA/raster-driven) |

**The `+7` structural fingerprint:** `play − init == 7` for **962 / 1,019 (94.4%)** — the
"Play = Init + 7 bytes" jump table is the single most reliable structural marker of this engine
(`research.md`: "$7580 init (7 bytes) / $7587 play"). Other deltas: `+10` (13), `+3` (11), large
negatives (relocated builds where init/play live in different pages), and the 18 `play=$0000` cases.

### 5a. PSID **speed-bit** distribution (read directly from each file's header `speed` longword @ offset $12)

> The DB has no speed column; values were read from the 1,019 SID headers directly (READ-ONLY).

| speed field | count | % |
|---|------:|---:|
| `0x00000000` (all subtunes flagged VBlank) | **23** | 2.3% |
| non-zero (≥1 subtune CIA bit set) | **996** | 97.7% |
| — of those, exactly `0x00000001` (subtune 1 only) | 996 | — |

**Important nuance — this does NOT contradict "VBlank-timed".** The brief expected `speed=0` for a
VBlank player; in fact **the opposite holds in HVSC**. The Master Composer player is *played from a
VBlank/raster IRQ* (one `play()` per frame), but the HVSC packagers set the **PSID speed bit = 1**
for nearly all of them. For a **PSID** file, `speed=1` does **not** mean the tune programs a CIA timer
itself — it tells the *PSID host* to call `play()` at the (CIA-default) ~50 Hz rate, which for a
once-per-frame VBlank tune is the correct cadence. The verification consequence:

- These tunes are **once-per-`play()`** (single VBlank call). Per the project's CIA-tune rule
  (CLAUDE.md "CIA-timed tunes (PSID `speed != 0`)"), `verify_all` will route the **996 speed!=0**
  files through the **`siddump --writelog-per-irq`** per-`play()` capture, not the flat 50 Hz path.
  This is a packaging flag, not evidence of real CIA multispeed — but the verdict path keys off the
  bit, so it matters operationally. The 23 `speed=0` files use the flat VBlank path.
- All 15 RSID members have `speed=0` and (per §5) `play=$0000` — they install their own IRQ; expect
  these to need the RSID/own-init handling, not the PSID play-vector path.

---

## 6. Cross-check: signature ↔ documented format

The disassembled absolute operands confirm `research.md`'s memory map (offsets relative to load):

| operand in player | offset from load | `research.md` says |
|---|---|---|
| `$7881` freq LO table | **+$301** | "+$300 freq lo (96 entries)" ✔ |
| `$78E0` freq HI table | **+$360** | "+$360 freq hi" ✔ |
| `$79D0` waveform/control byte | **+$450** | "+$450 block parameter tables" ✔ |
| `$7941` voice-state X index | **+$3C1** | "+$3C0 player variables" ✔ |
| `$7944/$7946` play flag | **+$3C4/+$3C6** | "+$3C0 flags" ✔ |
| `$7588` init flag (`STA $7588`) | **+$008** | within the 7-byte init stub ✔ |

The SIDId signatures are therefore consistent with the documented three-tier (pages→blocks→bars)
format and the `+$300/+$360/+$450` table layout.

## Leads to follow

1. **Migrate the vanilla player as ONE config.** ~985 files (984 head+Payne, plus the 2 head-only and
   most of the 13 outliers once relocation is handled) share one identical player. Pick a clean
   canonical rep (e.g. `MUSICIANS/E/Ekaitis_Joe/Eleanor_Rigby_Yesterday.sid`, `$7580`) and a relocated
   rep to prove reloc-invariance. The `+7` init/play delta + the head signature are the engine gate.
2. **Model `$64` as the gate-off sentinel** in the note codec: notes are `$01..$63` (freq-table index),
   `$00` = rest (skip voice), **`$64` = hold/gate-off** (`AND #$FE` on the voice control reg, waveform
   preserved). No separate "note-off event" needed — it's a reserved note value.
3. **`(Lope_Pulse_Sweep)` ≈ 20 files = a real sub-population needing a PW-sweep effect.** Plan a
   `master_composer/lope/` (or a `pulse_sweep` EngineConfig knob) AFTER the vanilla player verifies.
   16-bit accumulator `$02AA/$02AB`, step `$02A7`, limit `$02B1`, active-flag `$02BC` (in this build's
   zero-page workspace). Disassemble the full sweep + how it feeds `$D402/$D403` from a BOGG file.
4. **Exclude the 5 `TFMX/MasterComposer` files** from the Access migration entirely (separate TFMX
   driver). They are not in the 1,019.
5. **Speed-bit verification path:** treat the 996 `speed=0x00000001` files as the per-`play()`
   (`--writelog-per-irq`) verdict path even though they are musically VBlank once-per-frame — the
   project's CIA-tune branch keys on the bit. Confirm a couple with `siddump --writelog-per-irq` to
   make sure they really are exactly one `play()` per frame (expected) before wiring the verdict.
6. **Investigate the 18 `play=$0000` files** (incl. all 15 RSID) — these install their own IRQ vector;
   verify whether they still reduce to the same per-frame write stream or need RSID/own-init handling.
7. **The n=64-subtune outlier** and the 16 multi-subtune files: confirm whether "subtunes" here are
   real PSID songs or page selections, since Master Composer's "pages" are an internal sequencing tier.
