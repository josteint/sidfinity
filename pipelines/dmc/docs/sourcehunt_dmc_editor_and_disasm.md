---
source_url: (multiple — see per-section citations and Leads table)
fetched_via: WebSearch + WebFetch (leaf agent, 2026-06-20); confirmed against prior wave docs/provenance_log.md (2026-06-12)
fetch_date: 2026-06-20
author: Claude (sidfinity leaf research agent)
content_date: 1991-2026
reliability: CONFIRMED — all three Q3 sub-questions converge on definitive negative (no source, no disassembly, no parser) plus both specific Q questions are ANSWERED in the local annotated disassembly. External web sources are silent on the two specific questions; the authoritative answers live in pipelines/dmc/v5/disassembly.s + RE_NOTES.md.
---

# DMC editor open-source hunt + disassembly/parser survey — 2026-06-20

This document is a **confirmatory update** of the prior research wave (2026-06-12,
documented in `provenance_log.md`). The 2026-06-20 sweep covers the same targets
with a fresh web search to catch anything released in the 8-day gap and re-verify
the negative conclusions. Result: **no change** — everything found here is consistent
with the prior wave. Both specific questions (Q-freq and Q-offtable) are fully
answered by the local annotated disassembly and are NOT answered by any external source.

---

## Q3a — Is the DMC4 Editor by Logan/Slackers open source?

**VERDICT: NO. Closed-source Windows binary. No source repo found on any
platform (GitHub, GitLab, SourceForge, Codeberg, CSDb). Confirmed by:**

- **CSDb release pages**: id=250645 (v1.0, 2025-03-03) and id=251057 (v1.1,
  2025-03-15). Both pages ship only Win64/Win32/WinXP `.exe+DLL` zips. No
  source link appears on either page or in the changelog.
  Source: https://csdb.dk/release/?id=250645 (fetched 2026-06-20)
  Source: https://csdb.dk/release/?id=251057 (fetched 2026-06-20)

- **Logan/Slackers CSDb scener profile** (id=6117): no GitHub or external
  link of any kind. Shows only CSDb release history.
  Source: https://csdb.dk/scener/?id=6117 (fetched 2026-06-20)

- **Internal project name "dmcproxy"**: the exe's PDB path
  `E:\Projects\VS2022\dmcproxy\x64\Release\dmc4editor.pdb` (found by prior
  wave's string analysis of dmc4editor.exe). Searching "dmcproxy" + "dmc4editor"
  on GitHub/GitLab returns zero results.

- **ReadMe.txt** (both versions) references only
  https://tnd64.unikat.sk/music_scene.html for DMC usage; no source/spec link.

### What the editor's binary DOES reveal (without source)

Captured in `dmc4editor_embedded_player_notes.md` and `dmc4_editor_2025.md`
from the prior wave. Summary:

- The editor is a **wxWidgets + PortAudio + embedded libsidplayfp/ReSIDfp**
  application that proxies the real 6502 DMC4 player via emulation — it does
  NOT reimplement the player in C/C++. The player binary is Brian's original
  1991 code embedded verbatim in the exe.
- Two player RTTI classes: `PlayerDmc4` and `PlayerDmc7` — i.e. V7 is
  treated as a V4 variant (matches the scene-research finding that V7 reused
  V4's player).
- UI format strings reveal the COMPLETE track/sector command vocabulary:
  `TR+xx/TR-xx/-END-/STOP!` (track); `note+octave/SND.xx/DUR.xx/GLD.xx/VOL.xx/
  -GATE-/SWITCH/------/-END!-` (sector). These CONFIRM the command set in
  `dmc_sector_commands.md`.
- Instrument flag names: `DRUM EFFECT / NO GATE FX / HOLDING FX / NO FILT RES
  / NO PULS RES / CYMBAL FX / FILTER FX / DUAL EFFECT / Req Filter`.
- Import: V4.0, V7.0A, V7.0B (SID + PRG). Export: PRG + relocator.
- Embedded V4 player at exe offset 0x7F300, load $1000 — carved and saved as
  `dmc4_player_embedded_1000.bin` (prior wave; the canonical V4 player binary
  for seeding disassembly.s if needed).

---

## Q3b — Annotated DMC4/DMC5 player disassembly in public?

**VERDICT: NONE FOUND. Confirmed by the 2026-06-12 wave (deep sweep) and
re-verified by the 2026-06-20 search. No public annotated disassembly of any
DMC player version exists anywhere online.**

| Source checked (2026-06-20) | Result |
|---|---|
| GitHub full-text search: "demo music creator" + C64 player/disassembly | No hits |
| `realdmx/c64_6581_sid_players` | Annotated ASM for 12 composers (Galway, Hubbard, Whittaker, etc.) — **no DMC/Graffity** |
| `iceteam.itch.io/jc64dis` | 80+ player examples in their disassembler — **DMC absent** |
| CSDb forum search "DMC format" | No byte-level format threads |
| Codebase64 wiki (pokefinder mirror) | No DMC internals |
| archive.org advanced search | No annotated DMC disassembly documents |
| Lemon64, ChipMusic.org, pouet.net | General usage discussion only |

The most relevant external resource found is `realdmx/c64_6581_sid_players` —
it is a growing collection of annotated 6502 ASM reconstructions. It is worth
monitoring for future DMC additions.

**The only annotated disassembly that exists** is the project-internal one:
`pipelines/dmc/v5/disassembly.s` (Katusha.sid / family-3/5 canonical player,
hand-annotated in prior sessions). This is the PRIMARY source for both specific
questions below.

---

## Q3c — Open-source tools that parse/detect DMC?

**VERDICT: DETECTION SIGNATURES ONLY — no parser, no byte-layout reconstruction.**

| Tool | DMC content | Source URL |
|---|---|---|
| `cadaver/sidid` (+ mirror in `WilfredC64/player-id`, `Chordian/deepsid`) | 4 detection signatures: `DMC`, `DMC_V4.x`, `DMC_V5.x`, `DMC_V6.x` — opcode pattern only, no layout info | https://github.com/cadaver/sidid/blob/master/sidid.cfg |
| `Chordian/sidfactory2` | Zero DMC content; JCH converter is closest cross-format precedent | https://github.com/Chordian/sidfactory2 |
| `theyamo/CheeseCutter` | Zero DMC content (JCH-NewPlayer lineage) | https://github.com/theyamo/CheeseCutter |
| `libsidplayfp/libsidplayfp` | Player-agnostic emulator; no per-player handling | https://github.com/libsidplayfp/libsidplayfp |
| `realdmx/c64_6581_sid_players` | No DMC (Hubbard, Tel, Gray, Galway, etc. present) | https://github.com/realdmx/c64_6581_sid_players |
| GoatTracker source | No DMC import | (not re-checked 2026-06-20; confirmed negative 2026-06-12) |

### The sidid DMC V5.x signature — what it reveals

```
(DMC_V5.x)
BC ?? ??    ; LDY abs,X      — load wave-table index Y from some table[X]
B9 ?? ??    ; LDA abs,Y      — load a byte indexed by that Y (from a table)
C9 90       ; CMP #$90       — is this byte == $90 ?
D0 AND      ; BNE …          — if not $90, continue (conditional: AND = opcode-level gate)
BD ?? ??    ; LDA abs,X
3D ?? ??    ; AND abs,X
99 ?? ??    ; STA abs,Y
60          ; RTS
END
```

The `C9 90` = `CMP #$90` is the **wave-table loop sentinel**: when the ctrl byte
equals $90, the engine jumps to the absolute entry given by the following FREQ
byte (the `$90-00` loop construct from the first-party V5.0 docs). This is a
standard marker byte, NOT a bounds check on the freq-table index. The sidid
signature matches this exact two-byte sequence as a reliable fingerprint of the
V5 player.

---

## Specific question answers

### Q-freq: What is stored immediately AFTER the 96-entry freq table?

**ANSWERED in `layout_offtable_research.md` (primary: `disassembly.s` + `RE_NOTES.md`).**

Short answer: **Per-voice work RAM state block** — NOT a second music table.

- `freqlo[96]` ends at `$170F + 96 - 1 = $176E`.
- `freqhi[96]` ends at `$176F + 96 - 1 = $17CE`.
- $17CF onward: `track_ptr_lo/hi[3], sector_pos[3], dur_counter[3], dur_reload[3],
  cur_instrument[3], transpose[3], vol_override[3], gate_off_flag[3], glide_speed[3],
  glide_target[3], wave_table_pos[3], pulse_table_pos[3], filter_table_pos[1],
  vibrato_delay[3], vibrato_speed[3]` + more per-voice scratch (vib step, note
  counters, freq accumulators, pulse accumulators, filter counters, flags).
- Then at $1878: the track-pointer record (packer-placed music data).
- The layout order (freq→state→orderlist_rec→sector_ptrs→instr→wave→pulse→filter)
  appears consistent across members; absolute addresses vary (packer patches all
  data-table operands per-song).

No external source mentions this layout. The authoritative source is the annotated
disassembly.

### Q-offtable: What does the player do when (wave_freq + note) > 95?

**ANSWERED in `layout_offtable_research.md` (primary: `disassembly.s` lines 620-640).**

Short answer: **Unchecked 8-bit overrun into the work-RAM state block.**

The melodic wave path at $139D-$13AE:
```asm
LDA $19ab,y   ; wave_freq[wavepos] (arp semitone offset)
CLC
ADC $100f,x   ; + curnote (current note#)
TAY           ; Y = (wave_freq + note) & $FF  — NO bounds check
LDA $170f,y   ; freqlo[Y]  ← Y can be > 95
STA …
LDA $176f,y   ; freqhi[Y]  ← Y can be > 95
STA …
```

There is no CMP/BCC/bounds check. The result is an 8-bit unsigned add; if
`(wave_freq[step] + curnote) > 95`, Y indexes past the 96 freq entries into
the per-voice work RAM described above. Those bytes happen to be nonzero
integers (state counters/pointers), so the engine reads them as freq-hi bytes
and produces a distinct (lower) pitch. This is NOT a design feature — it is an
unguarded side-effect. The fix in this codebase (`freq_overrun` block in
`engine_model.py`) captures the reachable off-table bytes per-song and emits
them contiguously after `freqhi` so they resolve correctly.

No external source describes this behaviour. The first-party docs (V5.0
instruction text by The Syndrom) say only "FOR A NORMAL MINOR-CHORD, USE LIKE
THIS: `00 21-00 / 01 21-03 / 02 21-07 / 03 90-00`" — small offsets (0, 3, 7)
that stay within the 96-entry table. No warning about large offsets, no mention
of table bounds.

---

## Summary verdict

| Question | Answer | Source |
|---|---|---|
| Q3a: Editor open source? | **NO** — closed-source Windows binary; no source repo on any platform | CSDb pages, scener profile, web search (all negative) |
| Q3b: Public annotated disassembly? | **NONE** — confirmed re-sweep 2026-06-20 | GitHub, archive.org, codebase64, CSDb (all negative) |
| Q3c: Open-source tool with DMC parser? | **NO parser** — detection signatures only (sidid.cfg) | cadaver/sidid, player-id, DeepSID (sig only); SF2, CheeseCutter, libsidplayfp (zero DMC) |
| Q-freq: What follows freq table? | **Per-voice work RAM block** ($17CF-$1877) then track-pointer record at $1878 | `disassembly.s` + `RE_NOTES.md` (PRIMARY) — external: SILENT |
| Q-offtable: Index > 95 behaviour? | **Unchecked 8-bit ADC overrun** into work RAM; reads state bytes as freq-hi | `disassembly.s` lines 620-640 (PRIMARY) — external: SILENT |

**No readable external implementation exists.** The authoritative source for the
DMC V5 player internals is the project's own annotated disassembly
(`pipelines/dmc/v5/disassembly.s`) which was built by hand-annotating the HVSC
binary. The DMC4 Editor binary (`dmc4_player_embedded_1000.bin`) is available as
a seed for a future V4 disassembly if needed.

---

## Leads to follow

1. **Monitor `realdmx/c64_6581_sid_players`** — best-in-class 6502 disassembly
   collection; no DMC as of 2026-06-20 but the maintainer is active.
   URL: https://github.com/realdmx/c64_6581_sid_players

2. **DMC V4 player disassembly from the carved binary**: `dmc4_player_embedded_1000.bin`
   ($1000 base, JMP table at $1000/$1003/$1006/$1009) is a clean seed for
   `tools/seed_disassembly.py` if family-1 V4 work needs a hand-annotated
   `disassembly.s` to match the V5 model.

3. **DMC V5 depacker binary** (`tmp/dmc_hunt/DMC_V5_Depacker.prg_`) encodes the
   packed-module layout knowledge as 6502 code — disassembling it would yield
   the authoritative layout spec from the tool that UNPACKS it. Not done yet.

4. **DMC V5.0 Scanner** (`tmp/dmc_hunt/DMC_5.0_SCANNER.prg`) scans RAM for DMC
   data structures — its search heuristics encode layout offsets. Another
   potential format oracle.

5. **Logan's "DMC Tune Seeker"** inside DMC 4 Editor: a binary oracle that
   classifies SID/PRG files as DMC 4.x or not. Comparing our detector's
   accept/reject set against it would validate the fingerprint factory.

6. **family-4 (Jupiter41, 686 SIDs, play+$95)** freq-table size and off-table
   path — does it share the same unchecked arp-add at the analogous code location?
   Needs a disassembly of a family-4 member.
