# Electrosound — Disassembly, RE Analysis, and Tool Handling

## Provenance header

| Field | Value |
|---|---|
| fetch_date | 2026-06-14 |
| primary_sources | Lemon64 forum, VGMPf Wiki, cadaver/sidid GitHub, Chordian/deepsid GitHub, c64-music.blogspot.com, remix64.com, HVSC STIL.txt, hvsc84.db (read-only) |
| fetch_via | WebSearch + WebFetch |
| reliability | Community knowledge (high confidence for address structure); published RE writeup (none found) |

---

## 1. What is known — player overview

- **Author:** Steve Mellin / Orpheus Ltd., 1985. UK commercial tool, £14.95.
- **Reputation:** "poorly coded and the slowest known [player] on the C64" (VGMPf Wiki, c64-music blog, TMR on Lemon64). Superseded by Chris Hülsbeck's Soundmonitor in 1987.
- **Tuning:** A = 423.9 Hz (not A=440). This is a fixed constant in the compiled binary, consistent with `A9 64` (`LDA #$64` = LDA #100) in the SIDId signature — `$64` is likely the tempo/clock divisor or a tuning table seed, not a direct pitch register value.
- **Driver behaviour:** Does NOT loop. Once the song sequence list ends, the player stops. The game host must detect this and re-trigger if looping is needed.
- **CIA timer driven:** The player uses CIA1 timer interrupts for its interrupt vector, not VIC raster. Location `$02AD` carries the current tempo during playback and can change mid-song (dynamic tempo changes). This is distinct from most Hubbard-family players.

### Composer model (user-visible)

| Limit | Value |
|---|---|
| Instruments | Up to 10 |
| Sequences | Up to 20 |
| Notes per sequence | Up to 240 |
| Voices per sequence | 3 (fixed-to-SID voices for whole sequence) |
| Drum sounds | 24 (fixed; non-editable; substituted on voice rests) |
| Modulator targets | Pitch, pulse width, filter cutoff, key-on/key-off |
| Modulator parameters | Delay, speed, depth, direction (up/down/vibrato/shuffle), restart-on-note / restart-on-rest / no-restart |

Pattern model: "looks just like a Roland TR 606 drum-machine but with notes instead of drumbeats" (Peter Clarke, Remix64 interview). 16 note lengths per pattern. Pitch-bends and basic effects per note.

**Key structural constraint:** The 3 instrument assignments are fixed per sequence — a voice cannot change timbre within a sequence. This is why composers (e.g. Peter Clarke) noted it was less flexible than Martin Galway's assembler-written driver.

### Compiler output model

The Electrosound editor does NOT embed player code in the song file directly. Instead, a separate **compiler** step converts the composition into a compiled PRG that includes the player routine and all music data in a contiguous block, loadable at a programmer-specified address.

The compiler "doesn't sort out the IRQ routine properly" (Warren Pilkington / Waz, Lemon64 forum, 2008) — two `JMP $EA31` instructions in the IRQ handler must be replaced with `RTS` before use in a real program or SID conversion.

---

## 2. Player memory layout (from Lemon64 forum RE, Warren Pilkington)

Source: Lemon64 thread "Converting Electrosound files to .sid?" (t=19807), primary contributor Warren Pilkington (HVSC admin / SID ripper), 2008.

All offsets are **relative to the compiled PRG load address** (call it `BASE`):

| Offset | Address (if BASE=$1000) | Purpose |
|---|---|---|
| BASE + $0518 | $1518 | **Init routine entry** — JSR here to initialise the player |
| BASE + $0A65 | $1A65 | **Play routine entry** — called every CIA interrupt |
| BASE + $007B | $107B | Patch site: `JMP $EA31` → `RTS` (IRQ handler fix #1) |
| BASE + $0084 | $1084 | Patch site: `JMP $EA31` → `RTS` (IRQ handler fix #2) |

**Zero-page / fixed addresses (absolute, not BASE-relative):**

| Address | Purpose |
|---|---|
| $02AB | Tune number (set to tune_number − 1 before calling init) |
| $02FF | Playback speed / tempo (set before calling init) |
| $02AD | Current tempo during playback (read/write; changes on tempo-change sequences) |
| $02F9 | Playback enable flag (write $01 to start playback) |

**Standard init sequence for a compiled Electrosound PRG:**
```asm
JSR BASE+$0518    ; initialise player
LDA #tune_num-1
STA $02AB         ; select tune (0-based)
LDA #speed_val
STA $02FF         ; set tempo
LDA #$01
STA $02F9         ; enable playback
RTS
```

**Dynamic tempo:** `$02AD` can change during playback. Converting tunes with per-sequence tempo changes to SID requires computing CIA1 timer values for each change point — "not fun" (Pilkington). Static-tempo tunes convert cleanly.

**Play address convention in HVSC SIDs:** Because the IRQ routine sits at BASE+$0A65, and HVSC SID metadata stores the absolute play address, virtually all correctly-converted Electrosound SIDs have `play_addr & 0xFF == 0x65`. Analysis of hvsc84.db confirms: 235 of 294 non-zero-play Electrosound SIDs (80%) end in `0x65`.

---

## 3. Address cluster analysis (hvsc84.db, 297 SIDs)

The wide scatter of init/play address pairs in HVSC is explained by relocation: the same player binary can be compiled to any `BASE`. The player is therefore effectively **relocatable** (via the compiler, not via a runtime reloc table) — different games/demos just compiled it at different base addresses.

Five structural clusters emerge from the delta `init_addr − play_addr`:

| Cluster | Delta | Count | Pattern | Example |
|---|---|---|---|---|
| A | +0x9B (+155) | 83 | `init = play + 0x9B` → init is the loader stub at BASE+$0B00, play at BASE+$0A65 | init=$1B00, play=$1A65 |
| B | −0xA75 (−2677) | 57 | `init = play − 0xA75` → init IS the load address, play at init+$0A75 | init=$3FF0, play=$4A65 |
| C | −0xA7A (−2682) | 17 | `init = play − 0xA7A` → slight variant; init is load addr, play at init+$0A7A | init=$17EB, play=$2265 (Matt composer group) |
| D | +0x2B (+43) | 24 | `init = play + 0x2B` → short init stub only 43 bytes above play | init=$1A90, play=$1A65 |
| E | −3 | 14 | `play = init + 3` → init and play are nearly identical; likely init contains 3 bytes of setup then falls through to play | init=$1B00, play=$1B03 |

**Notes:**
- Cluster B: the `init` address is exactly the PRG load address (e.g. $3FF0). The `$3FF0` is 16 bytes before the standard $4000 page boundary — the first 16 bytes at $3FF0 are likely a short stub or header, then the bulk of the player follows at $4000+. Play sits at $4A65 = $3FF0 + $0A75. The +$10 offset from $0A65 to $0A75 suggests this variant has 16 more bytes before the play routine entry, possibly a different player version.
- Cluster C (Matt group, 17 SIDs): play at init+$0A7A — yet another 5 bytes further, suggesting a third player variant.
- Cluster E (14 SIDs, incl. Jonathan Dunn's `Choroid_5`): init and play only 3 bytes apart. Likely init is `LDA #tune` / `STA $02AB` / `JMP play_addr`, making it a 3-instruction pre-stub before the main play loop.
- ~60 SIDs do not fit any of the above major clusters and have unique or rare address patterns — likely individually ripped with custom stubs or are multi-tune compilations where one player binary plays multiple songs.

**Implication for version variants:** The three different play-entry offsets ($0A65, $0A75, $0A7A from their respective `init` addresses) suggest at minimum **3 distinct compiled player builds** present in HVSC, or a single player with 3 slightly different entry-point positions. The SIDId signature `F0 01 60 A9 64 9D ?? ?? BD ?? ?? C9 01` is a single pattern covering all of them (the wildcard bytes absorb the address bytes).

---

## 4. SIDId / player-id tool handling

### SIDId (cadaver/sidid)

Single entry in `sidid.cfg`:

```
Electrosound

F0 01 60 A9 64 9D ?? ?? BD ?? ?? C9 01 END
```

- **No sub-variants documented.** One signature for all builds.
- **`sidid.nfo` credits:** Entry shows release year 1985, Orpheus, with CSDb reference `https://csdb.dk/release/?id=27433`. No author attribution for the signature itself.
- The `A9 64` = `LDA #$64` (LDA #100) is the tempo or tuning constant mentioned in the known facts. The surrounding `9D ?? ??` (STA abs,X) and `BD ?? ??` (LDA abs,X) with `C9 01` (CMP #$01) form a character of the inner player loop — likely the sequence-step counter comparison or voice dispatch.

### WilfredC64/player-id

Uses the same `sidid.cfg` format. No additional Electrosound-specific information found in the repo.

### DeepSID (Chordian/deepsid)

The GitHub repository contains no files matching "electrosound". DeepSID identifies players via its imported database (sourced from SIDId/HVSC classification), so it delegates to the SIDId classification rather than having its own Electrosound-specific detection code. DeepSID displays the player/editor tag for tunes identified as Electrosound but adds no engine-specific analysis.

### JC64dis (IceTeam)

JC64dis (iterative C64 disassembler, itch.io) includes the Electrosound 64 player as one of its supported format examples:

> "Electrosound 64 player (tune 'Mission of Mercy' by Peter Clarke (c) 1986 Peter Clarke)"

This means JC64dis can disassemble a compiled Electrosound PRG into labelled 6502 assembly. No separate documentation about the disassembly output or the format specifics is published on the tool's page.

---

## 5. Published RE / disassembly writeups

**None found.** After searching CSDb (503 in 2026), Lemon64, codebase64.org, GitHub (cadaver/sidid, realdmx/c64_6581_sid_players, Chordian/deepsid, WilfredC64/player-id), VGMPf, c64crapdebunk, pouet.net (not checked directly), remix64, archive.org disk images, HVSC STIL.txt, and general web searches — there is no published disassembly, annotated listing, or detailed RE writeup of the Electrosound player routine.

**What exists:**
- Warren Pilkington's practical conversion notes (Lemon64 forum, 2008): offsets as documented above.
- VGMPf Wiki and c64-music blog: user-level feature description only.
- c64crapdebunk "Code Notes — Bog Standard Demos" series (2016): tags Electrosound but articles discuss demo coding techniques, not the music player internals.
- Peter Clarke interview (Remix64): user-level description of the editor UX, not player code.
- TMR quote: "Electrosound's compiler was appalling" — no technical elaboration.

The closest thing to a structural analysis is the JC64dis example (which can generate an annotated listing from the PRG binary), but that output has not been published anywhere found.

---

## 6. Per-frame write model — what is known

No direct per-frame writelog analysis found. Inferences from feature list and "slowest player" reputation:

**Per frame (every CIA interrupt), the player likely:**
1. Advances sequence step counter per voice.
2. For each of 3 voices: evaluates up to 4 active modulators (pitch, PW, filter cutoff, key-on/off), applying delay countdown → then depth × direction each tick. Each active modulator writes to a SID register every frame during its active phase.
3. On note events: loads 8+ SID register values from instrument data (attack, decay, sustain, release, waveform, PW hi/lo, filter, control) — a fresh instrument write on every note-on.
4. Drum sounds: writes to the resting voice's registers when a drum slot is used.

**Why it's slow:** The "slowest known" reputation aligns with: (a) up to 4 × 3 = 12 modulator evaluations per frame, each computing the current value from delay/speed/depth/direction state; (b) no optimisation (no dirty-register tracking — likely writes every SID register every frame regardless of change); (c) the compiler generating unoptimised 6502 (TMR: "appalling compiler"). This is a frame-rate budget hog: if the player takes >50% of the VBI cycle budget, it conflicts with any demo effects running concurrently. This is likely why Compunet-era demos using Electrosound tended to be "bog standard" (minimal graphics/effects).

**Tuning:** 423.9 Hz fixed tuning table, not 440 Hz. The frequency table is pre-computed into the compiled binary. This means USF extraction cannot use a standard 440 Hz note codec — the note→SID_freq mapping must use the 423.9 Hz table.

---

## 7. Version variants — working hypothesis

Based on HVSC address analysis and absence of published documentation:

| Working label | Play-from-init offset | HVSC count | Notes |
|---|---|---|---|
| **Standard** (init=play+$9B) | BASE+$0A65 | 83 | Most common single-address pattern; both init stub and play at canonical offsets |
| **Load-at-init** (init=load) | BASE+$0A75 | 57 | Init is the load address itself; 16 extra bytes before play entry |
| **Matt variant** | BASE+$0A7A | 17 | Composer "Matt" group; +5 bytes relative to Standard |
| **Short stub** (init=play+$2B) | BASE+$0A65 | 24 | Init stub minimal (43 bytes); play at same canonical offset |
| **JSR-init** (init=play−3) | BASE+$0A65+3 | 14 | Init is 3 bytes of setup before play entry |
| Other / unique | various | ~60 | Individual rips, custom stubs, multi-song compilations |

Whether the Load-at-init and Matt variants represent different compiled versions of the same player source, or different player revisions, cannot be determined without binary comparison. No v1/v2 version labelling has been found in any public source.

---

## 8. Leads to follow

1. **Binary comparison of cluster B vs cluster A SIDs** — diff the player code starting at `play_addr` for `init=$3FF0/play=$4A65` (cluster B) vs `init=$1B00/play=$1A65` (cluster A). If the bytecodes match after offset adjustment, there is one player version compiled to different addresses. If they differ, there are ≥2 player versions. Tools: `siddump --memwatch` or `python3 tools/seed_disassembly.py` on representative SIDs from each cluster.

2. **JC64dis disassembly of Mission of Mercy** — run JC64dis on a cluster A Electrosound SID (e.g. `DEMOS/A-F/Electrosound_64.sid` or a Peter Clarke SID) and publish the annotated output. This is the only known tool that will auto-label the player structure. Contact IceTeam / Ice00 if their example output for Mission of Mercy can be obtained.

3. **HVSC STIL full search** — the HVSC STIL.txt check above only found 2 entries. A full grep of the STIL.txt for "Electrosound" or for the major MUSICIANS paths may reveal further notes from SID rippers about the player behaviour.

4. **CSDb comments on `?id=27433`** — CSDb was 503 at time of research. The main Electrosound release page may carry comments from coders who used or ripped the player. Check again when CSDb is available, and also check `?id=254231` (Electrosound 64) and `?id=85170` (Electrosound 64 by The Snail).

5. **Modulator byte format** — the number and layout of bytes per modulator (delay, speed, depth, direction, restart-mode) in the compiled binary is entirely undocumented. A `--memwatch-on-write D402` or `D406` investigation on a live SID would expose the per-frame pitch-modulator behaviour and allow back-inference of the data structure.

6. **Frequency table reverse** — the 423.9 Hz note table in the binary can be extracted by finding the table pointed to by the `BD ?? ??` instruction in the SIDId signature (LDA abs,X at that offset). Comparing with the known 440 Hz table formula gives the exact scaling factor and confirms the tuning claim.

7. **$02F9 / $02AB / $02AD zero-page layout** — these fixed absolute addresses suggest the player keeps some global state in zero-page or low RAM (not relocated with BASE). A full listing of what the player uses in this area would be needed for USF extraction of multi-tune compilations.

8. **"Slowest" root cause** — a writelog or effect_chain_profiler run on a representative tune would quantify how many SID writes happen per frame and from which routines, confirming or refining the hypothesis about unoptimised modulator evaluation.

---

## Sources

- Lemon64 forum t=19807 "Converting Electrosound files to .sid?" — https://www.lemon64.com/forum/viewtopic.php?t=19807 (Warren Pilkington, ~2008)
- VGMPf Wiki Electrosound 64 — https://www.vgmpf.com/Wiki/index.php?title=Electrosound_64
- cadaver/sidid `sidid.cfg` + `sidid.nfo` — https://github.com/cadaver/sidid/blob/master/sidid.cfg
- c64-music blog "Electrosound" — https://c64-music.blogspot.com/2009/06/electrosound.html
- Remix64 "An Interview with Peter Clarke" — https://remix64.com/interviews/an-interview-with-peter-clarke.html
- Lemon64 forum t=6458 "Composing Music on C64" (TMR quote) — https://www.lemon64.com/forum/viewtopic.php?t=6458
- HVSC STIL.txt (v84) — https://www.hvsc.de/download/C64Music/DOCUMENTS/STIL.txt
- JC64dis (IceTeam) — https://iceteam.itch.io/jc64dis
- hvsc84.db address cluster analysis (this session, 2026-06-14)
- CSDb release pages: id=27433, id=254231 — both 503 at time of research
