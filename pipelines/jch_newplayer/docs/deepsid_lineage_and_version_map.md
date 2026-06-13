---
source_url: "https://deepsid.chordian.net/ (player tags via SIDId by Cadaver); https://csdb.dk/release/?id=20112 (NP 21.g4 beta, 2005); http://theyamo.kapsi.fi/ccutter/ (CheeseCutter — kapsi 401 on direct fetch, header read from local source tmp/jch_research/player_v4.acme); WebSearch June 2026 (Lemon64 / Chordian blog / RetroSummit). LOCAL: tmp/jch_research/{player_v4.acme,cc_base.d,cc_dump.d,cc_help.d,cb64_20g4_raw.txt}; pipelines/dmc/docs/research.md (READ-ONLY)"
fetched_via: WebSearch + WebFetch + local read (READ-ONLY)
fetch_date: 2026-06-13
author: synthesis by Claude (sidfinity research wave). Underlying: SIDId by Cadaver/Wilfred Bos; CheeseCutter player by Abaddon based on JCH NP 21.G4 by Laxity/Vibrants; JCH NewPlayer by Jens-Christian Huus (Vibrants); 20.G4 format note by FTC/Hokuto Force; DMC docs by The Syndrom/TIA + TND
content_date: NP 17.G0/20.G4/20.Q0 ~1990s; NP 21.G4 beta = 2005-08-27; CheeseCutter cc4.07 player ~2010s
reliability: primary for CheeseCutter source-header version claim + CSDb 21.g4 metadata + 20.G4 format note; secondary (forum/blog) for "most-known players = 17.G0/20.G4/20.Q0"; DMC→JCH inheritance is structural inference cross-checked against both engines' docs (flagged)
---

# JCH NewPlayer — DeepSID version map + DMC→JCH lineage

Companion to `sidid_variant_taxonomy.md`. Covers: (1) how DeepSID names the
variants, (2) the SIDId V-number ↔ named-release (NP 17 / 20.G4 / 20.Q0 / 21 /
22-25) mapping, (3) what JCH NewPlayer inherited from DMC (already migrated in
`pipelines/dmc/`) versus what is new.

## 1. How DeepSID distinguishes the variants

- DeepSID (Chordian, by JCH himself) runs **SIDId (by Cadaver)** + SIDInfo for
  player detection — i.e. the exact `sidid.cfg` mined in the taxonomy doc.
  (DeepSID credits page lists "SIDId by Cadaver, SIDInfo by ccr".)
- The "Players/Editors" tab shows the matched **signature name**, including the
  sub-signature. A live HVSC tune surfaces as e.g. **"JCH NewPlayer v3"** — that
  string is literally SIDId's sub-sig `(JCH_NewPlayer_V3)` rendered for display.
  So DeepSID's per-tune version tag == the SIDId sub-sig that hit.
- **Consequence for us:** DeepSID does NOT add information beyond what SIDId's
  sub-sigs encode. The per-V-number split is recoverable purely locally by
  running the config (no need to scrape DeepSID). DeepSID is useful as a
  cross-check / human-readable confirmation, not as a separate data source.
- DeepSID also strips JCH's own embedded "player + length" strings from his tunes
  via regex (per the Chordian "more tags" blog) — i.e. some JCH tunes carry a
  literal player-name string in the SID data, but that is cosmetic, not the
  detection basis.

## 2. The version map — SIDId V-number ↔ named NewPlayer release

JCH's NewPlayer is a **family of interchangeable player binaries** merged into one
editor. From JCH's own history (Lemon64 / Chordian): JCH built his editor after
Laxity told him to stop using Laxity's; the editor could "merge different players"
each tuned for a purpose (rastertime / multispeed / generic). So the version axis
is two-dimensional: **a player generation number (17/20/21/22…) × a build letter
(G0/G4/Q0/B4…)**. SIDId only fingerprints the generation's distinctive routine, so
its V-numbers are coarser than the public G4/Q0 build letters.

Named releases I can anchor:

| public name | what it is | anchor | likely SIDId sub-sig |
|-------------|-----------|--------|----------------------|
| **NP 17.G0** | "one of the most-known New Players used" | Lemon64/JCH community: "most known are 17.G0, 20.G4, 20.Q0" | `(JCH_NewPlayer_V17)` — the compact 2-guard dispatch with the `CMP #$02` chord/super branch |
| **NP 20.G4** | most-known; documented file format exists | `cb64_20g4_raw.txt` "JCH 20.G4 Player File Format by FTC/HT" (full memory map) | `(JCH_NewPlayer_V20)` — framecall-counter + `CMP #$02; BCS` 2-level speed generation |
| **NP 20.Q0** | most-known; a 20-series build variant ("Q0" letter) | same Lemon64 list | also `(JCH_NewPlayer_V20)` — SIDId does not distinguish G4 vs Q0 (same core routine; build-letter differs) |
| **NP 21.G4 / 21.b4** | 2005 beta, the last classic NP; **CheeseCutter is based on this** | CSDb #20112: "JCH NewPlayer 21.g4 beta (21.b4)", 2005-08-27, **code by Laxity** (Maniacs of Noise + Vibrants); CheeseCutter `player_v4.acme` header: "Based on JCH NP 21.G4 by Laxity/VIB" | top-level `Laxity_NewPlayer_V21` (313 SIDs) + the Glover fork `Glover_NewPlayer_V21` (67). NOT a `JCH_NewPlayer` sub-sig — V21 graduated to its own SIDId name because Laxity rewrote enough |
| **NP 22 – 25** | later/internal build letters past 21 | not present as distinct SIDId sigs locally | folded into `Laxity_NewPlayer_V21` or the SF2 successor; **no separate signature in this config** — see caveat |

**Caveat on 22-25:** the local `sidid.cfg` tops out at SIDId-V20 (sub-sig) and
top-level `*_V21`. There is **no V22/V23/V24/V25 signature** here. Any "NP 22-25"
tunes are either (a) still matched by the V21 signature (the V21 core routine
persisted), or (b) migrated into **SidFactory II** (Laxity's modern successor
editor) — HVSC shows `SidFactory_II/Laxity` = 377 and `SidFactory/Laxity` = 39 as
*separate* engines. SF2 is the spiritual NP 22+; it is a different binary/format
(SF2 has its own .dat + a `converter_jch` to import old JCH .dat — per the DMC
github survey). If the cluster needs true 22-25 coverage, that lives under SF2,
not under this JCH NP config.

**There is no SIDId `V16`** (jumps V15→V17) — a retired/merged signature.
**`(JCH_NewPlayer_V0x)`** is not a generation; it is the universal SID-reset init
prologue (zero $D400-$D418, then `#$88` testbit preset on all 3 ctrl regs).

### The NP 20.G4 on-disk format (from the FTC/HT note — primary)

`cb64_20g4_raw.txt` gives the literal table map for a 20.G4 module loaded at $1000
(tables at fixed +offsets; this is the editor layout — packed modules relocate):

```
Arp table col1  $18CB     Sequence ptrs lo  $1DCB     SeqList V0  $20CB
Arp table col2  $19CB     Sequence ptrs hi  $1ECB     SeqList V1  $24CB
Filter table    $1ACB     Super Table       $1FCB     SeqList V2  $28CB
Pulse table     $1BCB                                  Seq data    $2CCB+
Instrument tab  $1CCB
```

**Sequence stream format (AA/BB byte pairs)** — this is the JCH note encoding,
and it matches the SIDId base-sig sentinels exactly:

```
AA (left column):                         BB (note column):
  $7F  = End of Sequence                    $00     = no note (gate off)
  $90  = Tie note (***)                      $01-..  = note value (trig current instr)
  $A0-$BF = Instrument $00-$1F               $7E     = gate-on hold (+++)
  $C0-$DF = pointer to Super Table
  $80  = "nothing" (no instr/super/tie)
```

The `$7E` hold sentinel and `$7F` end sentinel in BB/AA are the same constants the
SIDId base signature tests (`CMP #$7E`, `CMP #$7F`). This is the engine's
musical-data grammar — the basis for the USF sequence lift.

### CheeseCutter = the open-source NP 21.G4 (the Rosetta stone)

CheeseCutter (by Abaddon, GPL) is "CCUTTER 2.x musicplayer based on JCH NP 21.G4 by
Laxity/VIB". Its source (`player_v4.acme`, `cc_base.d`, `cc_dump.d`) is the single
best spec for the modern NP because it is *exactly the player with full editor
annotations*. Key facts pulled from it (primary, since it's source):

**Instrument table — 8 columns × `INSNO`(48) rows, column-major** (`INS_x = n*INSNO`):

| col | enum | editor description (from `idescrN` strings) |
|----:|------|---------------------------------------------|
| 0 | INS_AD | Attack/Decay → $D405 |
| 1 | INS_SR | Sustain/Release → $D406 |
| 2 | INS_HR | "Restart type / arp speed": `$00`=3-frame restart, `$40`=soft, `$80`=hard; lo-nibble `$00-$0F`=arp delay |
| 3 | INS_4 | Hard-restart waveform |
| 4 | INS_FLTP | Filter-table pointer |
| 5 | INS_PULSP | Pulse-table pointer `$00-$3F` |
| 6 | INS_7 | Hard-restart SR envelope value |
| 7 | INS_ARP | Wave-table pointer |

(Note: CheeseCutter uses 48 instruments / col stride 48; the 20.G4 era used 32
instruments `$00-$1F` per the AA-byte `$A0-$BF` range. The stride is a per-build
constant — a config field, not a structural difference.)

**Pulse table — 4 bytes/entry** (`pdescrN`): [0]=duration+direction
($00-$7F add / $80-$FF subtract frames), [1]=add value, [2]=initial pulse
(**nibbles reversed**: $48 = $8400), [3]=next-set ptr $00-$3F or `$7F`=stop.

**Filter table — 4 bytes/entry** (`fdescrN`): [0]=duration or `$90-$F0` filter-type
select, [1]=add or resonance+channel mask, [2]=initial value or `$FF`=skip,
[3]=next-set ptr or `$7F`=stop.

**Wave table — 2 cols** (`wdescrN`): col0 = transpose/loop ($00-$5F relative up,
$80-$DF absolute, `$7E` loop-prev, `$7F` loop-to-row); col1 = waveform/wave-delay/
loop-ptr ($00 nop, $01-$0F override wave delay, $10-$DF SID ctrl value, $E0-$EF
ctrl $00-$0F, or loop ptr if col0==$7F).

**Super/Command table — the effect dispatch** (`mdescrN`, `CMD_*` enums). The
NewPlayer effect set:

| cmd | name | param |
|----:|------|-------|
| $0 | Slide up | signed 16-bit speed |
| $1 | Slide down | signed 16-bit speed |
| $2 | Hi-fi vibrato | byte0 lo-nibble = "feel"; byte1 hi-nibble = speed, lo-nibble = depth divider |
| $3 | Detune current note | signed 16-bit |
| $4 | Set ADSR for current note | ADSR |
| $5 | Lo-fi vibrato | speed / depth |
| $6 | Set wave | waveform |
| $7 | Portamento to a tie note | porta speed (runs until cmd 8) |
| $8 | Stop portamento/slide | — |

These 9 commands are the entire JCH NP effect catalogue. Each maps cleanly to a
parametric USF effect (slide/vibrato/detune/porta/set-ADSR/set-wave) — none is an
indexed engine-library lookup, so they satisfy the USF representation principle.

**Multispeed:** `MULTISPEED=TRUE`, `CIA_VALUE=$4cc7`, `MULTIPLIER`. The play vector
has a dedicated `mplay = JMP submplay` entry (base+$0006) and the play-call
dispatch (`AND #$E0; CMP #$80` / `AND #$10`) is the multispeed framecall selector
the SIDId base sig fingerprints. **This means JCH NP CIA-timed/multispeed tunes
will need the same per-`play()` verdict path DMC/Hubbard CIA tunes use**
(`siddump --writelog-per-irq`) — 186 of 3611 JCH_NewPlayer SIDs are multi-subtune,
and an unknown subset are multispeed.

## 3. DMC → JCH lineage: what transfers to our extract logic

Both DMC and JCH NewPlayer are the **Danish editor tradition** (the DMC docs and
the github survey both flag CheeseCutter as "the JCH-NewPlayer lineage" and note
"the modern testbit method (shared with JCH player)"). They are **sibling engines,
not parent/child** — there is no evidence JCH NP is literally derived from DMC code;
rather they co-evolved and share idioms. What that means concretely:

### Shared with DMC (extract logic likely transfers)

- **Entry-point convention — IDENTICAL.** DMC: init=base+$0000 ($1000),
  play=base+$0003, extra entries +$0006/+$0009. JCH NP: same — init=$1000
  (3212/3611), play=$1003 (3220/3611), multispeed entry +$0006. The PSID
  header parsing + subtune-select path from `pipelines/dmc/` should drop in.
- **Hard-restart / "modern testbit method" — SHARED (DMC docs say so explicitly).**
  Note-fetch frame writes `$08`/`#$88` (TEST + gate-off) to ctrl + a hard-restart
  ADSR preset; next frame writes the real AD/SR. JCH's `INS_HR` column ($00=3-frame
  restart / $40 soft / $80 hard) + `INS_7` (HR SR value) + `INS_4` (HR waveform) is
  the *parameterised* form of exactly DMC's testbit hard-restart. Our DMC
  hard-restart modelling is directly reusable as a parametric feature.
- **2-byte programmable sub-tables (pulse/filter/wave-arp) with a "next ptr / stop"
  terminator.** DMC V5 moved pulse/filter into "fully programmable tables (start,
  per-frame add, frame count, loop)"; JCH's pulse/filter tables are 4-byte entries
  [duration/dir, add, init, next-ptr/$7F-stop] — the *same idea* (a tiny per-step
  program with a loop/stop link). The DMC table-program lifter concept transfers;
  the byte widths differ (config fields).
- **Wave/arpeggio table with relative-transpose + absolute-tuning + loop sentinels.**
  DMC wave table uses test-bit-in-first-byte for drum mode + transpose; JCH wave
  col0 = relative ($00-$5F) / absolute ($80-$DF) / loop ($7E/$7F). Same dual
  transpose-mode + loop-pointer structure.
- **Pulse "nibbles reversed" storage** ($48 = $8400) — a known C64-editor idiom; the
  DMC pulse handling already deals with nibble-packed pulse, so the unpack logic is
  familiar.
- **Frequency table:** DMC uses a 96-entry PAL hi/lo split (custom tables possible).
  JCH NP likewise uses a standard PAL freq table (CheeseCutter has `FREQTABLE` +
  `FINETUNE` offsets). The freq-table extraction approach transfers.

### New / different in JCH NP (DMC logic does NOT cover)

- **The sequence (note-list) grammar is different.** DMC uses sector/orderlist
  commands ($Bx tempo, FLT/FRQ, SWITCH, step directions). JCH uses the **AA/BB byte
  pair** stream ($7F end, $90 tie, $A0-$BF instrument, $C0-$DF super-table ptr, $80
  nothing | BB: $00 off, note, $7E hold). This is a **new pattern decoder** — the
  most significant new extract component.
- **The Super/Command table effect dispatch** ($Cx-pointer → 3-row cmd1/cmd2/cmd3
  tables, 9 numbered commands with signed-16-bit params). DMC's effect model is
  fx-flag-bits + sector commands; JCH's is a separate indexed command program per
  sequence step. New emitter + new extract path, though each *effect* maps to an
  existing parametric USF effect (slide/vibrato/porta/detune/ADSR/wave).
- **Chord table** (`ChordTable`/`ChordIndexTable`, cmd $80-$9F) — a JCH feature for
  per-step chord arpeggios distinct from the wave-table arp. New.
- **Instrument layout is column-major 8×N** (INS_x = n*48), vs DMC's row-major
  8-byte-per-instrument ($4000+8*i). Mechanical difference for the lifter — a
  stride/transpose of the read, not a semantic one.
- **Multispeed is first-class** (CIA_VALUE, MULTIPLIER, dedicated mplay entry). DMC
  has multi-player mode but JCH's multispeed framecall counter is built into the
  play dispatch. Verdict path must use per-IRQ capture for these.

### Net assessment for migration

The **runtime/SID-side modelling transfers well** (entry points, hard-restart
testbit, programmable pulse/filter/wave-arp tables, freq table, $D418 master-vol).
The **data-side lift is mostly new**: a fresh AA/BB sequence decoder + super-table
command lifter + chord table. CheeseCutter's source (`player_v4.acme` + `cc_base.d`
+ `cc_dump.d`) is a near-complete spec and even contains a *data dumper*
(`dumpData` in cc_dump.d) that shows the exact serialization — invaluable as the
extract oracle. The effect catalogue is small (9 commands) and each is a clean
parametric effect, so the USF representation should be straightforward and
principle-compliant.

## Leads to follow

- **Pull CheeseCutter's full `player_v4.acme` play routine** (only the header +
  effect-command descriptors were read here; the actual per-voice play loop after
  `subinit` at $1000 is the real write-model). It is the open-source NP 21.G4 — the
  exact spec for the dominant modern variant. Local copy: `tmp/jch_research/player_v4.acme`.
- **Map the AA/BB sequence grammar + super-table commands to USF** before any code
  — they are the new pieces. The `cc_dump.d` `dumpData()` serializer is the ground
  truth for byte order (arp1/arp2/filttab/pulstab/inst[8×48]/seqlo/seqhi/cmd1-3/
  songsets/tracks/seqs/chord/chordindex).
- **Reconcile the 32-vs-48 instrument stride** (20.G4 = 32 `$A0-$BF`; CheeseCutter =
  48). Make stride a per-build config field, not a branch.
- **Acquire the NP 17.G0 + 20.Q0 binaries** and disassemble — confirm V17/V20 SIDId
  readings, and whether 20.G4 and 20.Q0 truly share the V20 core (build-letter only).
- **Decide SF2 scope:** `SidFactory_II/Laxity` (377) is the NP 22+ successor but a
  distinct engine with its own format + a `converter_jch`. Out of scope for the JCH
  NP composer unless explicitly folded in.
- The CheeseCutter `about.html` fetch returned HTTP 401 (kapsi blocks the bot) —
  retry via `gh`/archive.org or read `tmp/jch_research/cc_ccutter.1` (the man page)
  if more provenance on Abaddon/version is needed.
