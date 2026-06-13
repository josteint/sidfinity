---
source_url: "local: tmp/dmc_hunt/player-id/config/sidid.cfg (lines 946-1005); cross-checked against tmp/dmc_hunt/sidid/sidid.cfg + tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg. Sig-file format spec: tmp/dmc_hunt/player-id/doc/Signature_File_Format.txt"
fetched_via: local read (READ-ONLY); HVSC population from local hvsc84.db (mode=ro)
fetch_date: 2026-06-13
author: synthesis by Claude (sidfinity research wave); underlying sidid.cfg signatures by the player-id / SIDId community (Wilfred Bos / DeepSID Chordian distribution), JCH NewPlayer by Jens-Christian Huus (JCH/Vibrants) + later maintainers Laxity/Vibrants
content_date: signatures cumulative ~1989-2020; sig-file format V2.0
reliability: primary for the signature bytes (verbatim copy of the distributed config) + 6502 disassembly of each signature is my own inference (clearly flagged); population counts are primary (direct DB query)
---

# JCH NewPlayer — SIDId variant taxonomy

The complete `JCH_NewPlayer` signature block plus every adjacent NewPlayer-family
signature, taken verbatim from the SIDId config, with each signature interpreted
as 6502 to say WHICH player generation / routine it fingerprints.

## Config provenance + the three copies agree

Three `sidid.cfg` copies exist locally; **they are the same taxonomy**:

| copy | path | form |
|------|------|------|
| player-id | `tmp/dmc_hunt/player-id/config/sidid.cfg` | `&&` token, optional `END` (format V2.0) |
| DeepSID 100 | `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` | byte-identical to player-id except every line carries a trailing ` END` marker |
| sidid | `tmp/dmc_hunt/sidid/sidid.cfg` | identical signatures, but spells the skip operator `AND` (format V1.0 style) instead of `&&` |

Same signature set, same order, **same V-numbering** (V1..V20 + V0x + Dane_NewPlayer).
Citations below use the player-id copy.

### Signature-file grammar (from `Signature_File_Format.txt`, V2.0)

- A signature is space-separated 2-hex-digit bytes. `??` = one wildcard **byte**
  (nibble wildcards are not allowed).
- `AND` / `&&` = "skip an arbitrary number of bytes until the next group matches"
  (so a single named signature can be two code fragments with a gap between them).
- A name in `(parentheses)` is a **sub-signature**: a more specific variant of the
  player that the base signature already covers. This is exactly how the V1..V20
  rows are encoded — they are sub-sigs under the base `JCH_NewPlayer` name.
- Convention: addresses + zero-page are wildcarded (`??`); **only $D4xx SID I/O
  addresses are kept literal**. So every literal `04 D4`, `12 D4`, `18 D4` etc. in
  a signature is a real SID register write and is the most load-bearing part.
- All sub-sigs are OR-ed: if ANY of the base or sub lines hits, the file is reported
  as `JCH_NewPlayer`. The sub-name is what DeepSID/player-id surface as the version
  tag. **SIDId does not export the sub-name into HVSC's STIL/engine field** — HVSC
  collapses everything to `JCH_NewPlayer` (see population, below).

## The base signature (the dispatch fingerprint)

```
JCH_NewPlayer
4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 48 29 10
A2 00 B9 ?? ?? 9D ?? ?? ?? ?? ?? B9 ?? ?? 9D ?? ?? ?? ?? ?? C8 C8 E8 E0 03 D0
B1 ?? 30 ?? F0 ?? C9 7E F0
AD ?? ?? F0 26 A2 03 B9 ?? ?? 3D ?? ?? 9D ?? ?? CA D0 F4 B9 ?? ?? 10 13 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? C8 C8 E8 E0 03 D0 ED A9 0F 8D
```

These four lines are four OR-ed base fingerprints. Disassembled:

- **Line 1 — the play-entry / multispeed dispatch.**
  `JMP play_real` then on a later entry `PHA; AND #$E0; CMP #$80; BNE …; PLA; PHA;
  AND #$10`. This is the **subtune/multispeed-call discriminator**: the play vector
  is entered with a code byte in A; bits 5-7 (`#$E0`) select call-type, `#$80`
  marks one mode, `#$10` another. This is the structural "JCH NewPlayer call
  convention" — also the shape of the V4 sub-sig (line `(JCH_NewPlayer_V4)` repeats
  `4C ?? ?? 48 29 E0 C9 80 …`).
- **Line 2 — the 3-voice init copy loop.**
  `LDX #$00; loop: LDA tbl1,Y; STA dst1,X; LDA tbl2,Y; STA dst2,X; INY INY INX;
  CPX #$03; BNE loop`. The `E0 03` (CPX #$03) + double `B9../9D..` is the
  **per-voice state-table initialiser for 3 voices** — copies two parallel tables
  (lo/hi pointer pairs) into the 3 voice slots. This is the NewPlayer "songsets →
  twraplo/twraphi" init.
- **Line 3 — the sequence-fetch core.**
  `LDA (ptr),Y; BMI …; BEQ …; CMP #$7E; BEQ …`. `$7E` is the **gate-on-hold (+++)
  sentinel** in the BB note byte (see lineage doc). This is the inner note reader.
- **Line 4 — the wave/arpeggio + master-volume tail.**
  `LDA flag; BEQ +$26; LDX #$03; loop: LDA src,Y; AND dst,X; STA dst,X; DEX; BNE…`
  then `… A9 0F 8D` = `LDA #$0F; STA $D4xx` — the **master-volume = $0F write**
  ($D418 low nibble). The `3D ?? ??` (AND abs,X) is the per-voice gate-mask AND.

**Read:** the base sig pins down the engine by (a) its 5/6/7-bit play-call
dispatch, (b) the 3-voice double-table init, (c) the `$7E` hold sentinel in the
sequence stream, and (d) the `#$0F` master-volume write. Those are the four
invariants of the whole NP family.

## The sub-variant table (V1 … V20, V0x, Dane)

Each sub-sig isolates ONE distinctive routine of a particular player generation.
SIDId's V-numbers are **routine-fingerprint generations, not a clean linear
version axis** — several share a base and differ only in how one effect is coded
(table width / 8- vs 16-bit counters / where the `STA $D4xx` lands). My reading of
the load-bearing opcodes:

| sub-sig | first bytes (key opcodes) | what routine it fingerprints | distinguishing feature |
|---------|---------------------------|------------------------------|------------------------|
| `(JCH_NewPlayer_V1)` | `BC?? B9?? 48 29 0F 9D?? 68 29 F0 …` | **pulse-program unpack**: split a packed pulse byte into lo-nibble (`AND #$0F`) and hi-nibble (`AND #$F0`, `LSR LSR`) into two voice slots, then `38 FD` (SEC; SBC abs,X) signed pulse add | early/pre-21 pulse handling, nibble-packed pulse value |
| `(JCH_NewPlayer_V2)` | `38 FD?? 9D?? … 68 29 F0 18 6D?? 8D 18 D4` | **filter/master-vol add**: `… 18 6D?? 8D 18 D4` = add then `STA $D418` | writes $D418 via an additive (`ADC`) path — older filter-cutoff-into-volume coupling |
| `(JCH_NewPlayer_V3)` | `DE?? 30?? BD?? 85?? BD?? 85?? 4C … C9 FD … 8D 12 D4` | **gate/note-off branch**: `DEC dur,X; BMI …` then ptr reload `LDA…STA zp; LDA…STA zp; JMP`; the `C9 FD … 8D 12 D4` is the **$FD command → zero $D412** (voice-3 ctrl reset) | distinct gate-off opcode `$FD` writing $D412 (V3 ctrl) |
| `(JCH_NewPlayer_V4)` | `4C?? 48 29 E0 C9 80 … 68 29 1F 38 E9 0C 0A …` | **the canonical multispeed dispatch** (same head as base line 1) then `PLA; AND #$1F; SEC; SBC #$0C; ASL` = decode a call-index, scale ×2 into a jump slot | the "standard" NP call-convention generation; `#$1F` index mask, `−$0C` bias |
| `(JCH_NewPlayer_V5)` | `C9 FF … BD?? 9D?? 85?? … 4C … 29 7F 0A 9D?? FE?? … A8 B9?? 85` (+ 2nd line) | **note/transpose fetch with `$FF` restart command**, `AND #$7F; ASL` note→index, `INC ptr,X` advance; 2nd line `… 4C … 48 29 E0 C9 C0` adds a `#$C0` call-type | adds `$FF` = restart and a `#$C0` dispatch class on top of V4 |
| `(JCH_NewPlayer_V6)` | `C9 FF … 85?? A0 00 B1?? 10?? C9 FF F0?? 29 7F 0A …` | as V5 but the sequence read is `LDY #$00; LDA (ptr),Y; BPL …; CMP #$FF; BEQ …` | indirect-Y `(zp),Y` sequence read (vs V5's `BD abs,X`) — a memory-model change |
| `(JCH_NewPlayer_V7)` | `A2 02 CE?? 10?? A9 01 8D?? F0?? 4C … C9 03 …` | **speed/framecall counter**: `LDX #$02; DEC cnt; BPL…; LDA #$01; STA flag`; `CMP #$03` selects a play-mode | introduces the `LDX #$02` per-voice down-counter loop driven by a frame counter (multispeed scaffolding) |
| `(JCH_NewPlayer_V8)` | `B1?? C9 7F D0?? A9 00 9D?? BD?? 18 69 01 9D?? 85?? BD?? 69 00 9D?? 85?? …` | **portamento / 16-bit pitch slide**: `LDA (ptr),Y; CMP #$7F` (end), then 16-bit `ADC #$01 / ADC #$00` pitch accumulate into two voice bytes | first generation with an explicit 16-bit add slide (low byte `+1`, carry into hi) |
| `(JCH_NewPlayer_V9)` | `A2 02 CE?? 10?? AD?? 8D?? D0?? BD?? D0?? 4C … BD && B1?? C9 7F …` (+ line) | V7 counter + `&&`-skip to a `(ptr),Y; CMP #$7F` reader + 16-bit slide | combines V7 counter with V8 slide; `&&` = gap between the two fragments |
| `(JCH_NewPlayer_V10)` | `B1?? C9 FF … C9 FE D0?? A9 00 9D?? BC?? 99 04 D4 …` (+ line) | **two commands `$FF` and `$FE`**; `$FE` → `LDY tbl,X; STA $D404,Y` = **per-voice ctrl write to $D404 indexed by Y** | adds the `$FE` command writing $D404 (voice-1 control) via Y-index — a wave/ctrl effect |
| `(JCH_NewPlayer_V11)` | `8A A8 BD?? F0?? D9?? D0?? 8D?? BC?? B9?? 29 F0 C9 F0 D0?? AD?? 9D?? …` | **command-table compare**: `TXA; TAY; LDA cmd,X; …; CMP tbl,Y`; `AND #$F0; CMP #$F0` = test the **super-table hi-nibble `$Fx` marker** | super/cmd-table dispatch with `$Fx` markers — the "supertable" generation begins |
| `(JCH_NewPlayer_V12)` | `A2 02 BD?? D0 03 4C?? BD?? F0 08 A9 00 9D?? 4C … C9 01 D0 05 FE?? D0 06 DE?? 4C …` | **per-voice command opcodes 0/1**: `LDX #$02; LDA cmd,X; BNE +3; JMP…; CMP #$01 → INC/DEC` counters | explicit numbered command bytes ($00/$01) with INC/DEC dispatch — modern cmd format |
| `(JCH_NewPlayer_V13)` | `A2 02 BD?? C9 02 D0?? BC?? B9?? BC?? 99?? BC?? B9?? BC?? 99?? A9 09 99?? CA 10 D9 A5?? 48 A5?? 48` | **command `$02` = double table-copy** (two `LDY tbl; LDA src,Y; LDY tbl2; STA dst,Y` pairs) + `LDA #$09; STA …,Y`; tail `LDA zp;PHA;LDA zp;PHA` = **push 2 zp regs (re-entrant)** | introduces re-entrant zp save (`A5/48`) — the hallmark of the 20.x/21.x supertable players |
| `(JCH_NewPlayer_V14)` | as V13 head, then `AD?? F0 09 AD && 98 9D?? B1?? 10 0F 0A 9D?? FE?? D0 03 FE?? C8 B1?? A8` | V13 + a wave-table stepper: `(ptr),Y; BPL; ASL; STA; INC ptr…` with a `&&` skip | V13 with the wave-table arpeggio stepper attached |
| `(JCH_NewPlayer_V15)` | `A2 02 A5?? 48 A5?? 48 BD?? D0 03 4C && BD?? F0 19 DD?? D0 0E A9 00 9D?? BD?? BC?? 99?? DE?? 4C` | **re-entrant zp save FIRST** (`A5/48 A5/48`) then cmd dispatch with `DD?? ` (CMP abs,X) table compare | V15 moves the zp-save to the top of play — structural refactor of V13's tail |
| `(JCH_NewPlayer_V17)` | `A5?? 48 A5?? 48 A2 02 BD?? D0 03 4C?? BD?? D0 03 4C?? C9 02 F0 06 DE?? 4C` | re-entrant zp save + **double early-out** (`LDA cmd,X; BNE; JMP` twice) then `CMP #$02; BEQ; DEC; JMP` | **THIS IS "NP 17"** — the compact dispatch with two guard branches before the `$02` chord/super path (see mapping doc) |
| `(JCH_NewPlayer_V18)` | `A5?? 48 A5?? 48 BD?? D0 03 4C?? BD?? 30 17 BD?? F0 59 DD?? D0 26 A9?? 9D` | zp save + `LDA cmd,X; BMI +$17` (negative-command branch) + `BEQ +$59` (long skip) + `CMP abs,X` | larger command space; signed command bytes (`BMI`) — a superset of V17 |
| `(JCH_NewPlayer_V19)` | `4C?? DE?? 4C?? DE?? BD?? 85?? BD?? 85?? A0 00 98 9D?? B1?? 10 0F` | tail-only fingerprint: two `JMP…; DEC dur,X` arms then ptr reload + `LDY#0; TYA; STA…; LDA(ptr),Y; BPL+$0F` | the duration-counter + sequence-advance tail (shared shape with Dane below) |
| `(JCH_NewPlayer_V20)` | `48 A5?? 48 CE?? 10 1D AD?? 8D?? C9 02 B0 13 AC?? B9?? 8D?? CE?? 10 05 A9` | `PHA; LDA zp; PHA` + `DEC cnt; BPL +$1D`; `LDA flag; STA…; CMP #$02; BCS +$13`; `LDY idx; LDA tbl,Y; STA…; DEC cnt2` | **THIS IS "NP 20.x"** — the framecall-counter + 2-level speed (`CMP #$02; BCS`) generation; the 20.G4 / 20.Q0 sub-revisions live here (see mapping doc) |
| `(JCH_NewPlayer_V0x)` | `98 99 00 D4 C8 C0 19 D0 F8 A9 88 8D 04 D4 8D 0B D4 8D 12 D4 A9?? 8D 05 D4 8D 0C D4 && 8D 13 D4 A9` | **the silence/clear init**: `TYA; STA $D400,Y; INY; CPY #$19; BNE` (zero all 25 SID regs $D400-$D418), then `LDA #$88; STA $D404/$D40B/$D412` (TEST+gate-off on all 3 ctrl regs) + write AD ($D405/0C/13) | the **universal SID-reset / init prologue** ("V0x" = the init half, not a play generation). `#$88` = test bit + triangle gate-off hard-restart preset. Maps to our `init_style='universal_reset'` |
| `(Dane_NewPlayer)` | `30 03 4C?? 4C?? BD?? 85 02 BD?? 85 03 A0 00 98 9D?? B1 02 10 0F 0A 9D` (+ `0A 8D?? EE?? D0?? EE?? 4C`) | `BMI +3; JMP/JMP` then ptr reload into **fixed zp $02/$03** + `LDY#0; (ptr=$02),Y; BPL; ASL` + `INC/INC` 16-bit advance | **Dane's NewPlayer fork** — same engine but ptr hardwired to zp `$02/$03` (vs wildcarded zp elsewhere). HVSC labels these `Dane` (8) / `(Dane_NewPlayer)` (5) |

### Numbering gap
There is **no `V16`** in the config — SIDId jumps V15 → V17. (Likely a retired/merged
signature; not an HVSC label.) V0x is an init prologue, not a play-routine generation.

## Adjacent NewPlayer-family signatures (same block / nearby)

These are SEPARATE top-level signatures (not sub-sigs of JCH_NewPlayer), all part
of the same Danish NewPlayer tradition:

| signature | bytes (key) | reading | HVSC count |
|-----------|-------------|---------|-----------:|
| `JCH_DigiPlayer` | `D0?? AD?? F0?? A0 00 8C?? B1?? 4A 4A 4A 4A 18` | sample player: read byte, `LSR×4` (hi-nibble), add — 4-bit sample unpack | 4 |
| `JCH_OldPlayer` | `48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D?? 68 18 6D?? 8D?? 68` | pre-NewPlayer: `LSR×4; AND #$07; ASL×3` index build — the older table model | 32 |
| `JCH_Protracker` | `8D?? AD?? 8D 18 D4 60 A2 02 BD?? C9 02 D0 2C BC?? B9?? BC?? 99 05 D4 …99 06 D4 …F0 09 AD?? 99 04 D4` | a Protracker-style variant writing $D405/$D406/$D404 per voice via `LDY tbl` index — note the explicit `STA $D418`, `STA $D405,Y`, `STA $D406,Y`, `STA $D404,Y` | 94 |
| `Glover_NewPlayer_V21` | `B9?? 85?? 29 F0 C9 20 F0?? B0?? 9D?? B9?? 9D?? A5?? 29 0F 9D?? A9?? 9D` | a NewPlayer **V21 fork by Glover**: `LDA tbl; AND #$F0; CMP #$20` super-table marker test, `AND #$0F` lo-nibble | 67 |
| `Laxity_NewPlayer_V21` | `99 04 D4 BD?? C9 FF F0?? 4C?? DE?? BD?? D0?? 4C` | **THE V21 player by Laxity** — `STA $D404,Y` (ctrl write) + `CMP #$FF` (end) + `DEC dur` advance. This is the player CheeseCutter is "based on" (see lineage doc) | 313 |
| `Vibrants/Laxity` (5 sigs) | `18 7D?? 0A A8 B9?? 48 B9?? AC?? 99 01 D4 68 99 00 D4 …` + 4 more lines | Laxity's Vibrants-era player: `ADC abs,X; ASL; TAY; …; STA $D401; STA $D400` (16-bit freq via table), plus a `STA $D404,Y` ctrl arm and a `STA $D416` filter arm | 179 |
| `Vibrants/JO` (7 sigs) | `C9 80 D0?? BC?? C8 B1 …` (+6) | JO/Vibrants player; `CMP #$80` command class + `(ptr),Y` sequence read; multiple effect arms (`STA $D404`, freq adds, `$F0`/`$FF` sentinels) | 130 |

For completeness, two non-JCH `Glover` / `Dane` base sigs sit nearby:
- `Glover` (`D0 10 BD?? F0 08 A9 00 9D 05 D4 9D 06 D4 …`) — Glover's own pre-V21
  player (writes $D405/$D406 directly). HVSC: `Glover`=13, `Randy_Glover`=2, `Roy_Glover`=2.
- `Dane` (`AA 29 E0 C9 80 D0 12 8A 29 10 8D`) — note this is **the same `29 E0 / C9 80 / 29 10`
  dispatch as the JCH base line 1**, confirming Dane's player is a direct JCH-NewPlayer
  relative. HVSC: `Dane`=8.

## HVSC population (local hvsc84.db, mode=ro)

```
3611  JCH_NewPlayer          (load=$0000→$1000 ×3611; init=$1000 ×3212, play=$1003 ×3220;
                              186 multi-subtune; only 10 RSID. Alt bases: $E000/$5000/$8000)
 377  SidFactory_II/Laxity   (the SF2 successor — separate engine, listed for context)
 313  Laxity_NewPlayer_V21   (init=$1000 ×289, play=$1003; 6 multi-subtune, 1 RSID) = NP 21
 179  Vibrants/Laxity        (init=$1000 ×97 / $4000 ×52; play=$1006 ×89 — note +6 play offset)
 130  Vibrants/JO            (mixed bases $1000/$3000/$4000; play=$1003 or $1006)
  94  JCH_Protracker
  67  Glover_NewPlayer_V21   (init=$1000 ×64, no multi-subtune, no RSID) = NP 21 (Glover fork)
  39  SidFactory/Laxity      (SF1 — separate engine, context)
  32  JCH_OldPlayer
  13  Glover
   8  Dane
   5  (Dane_NewPlayer)
   4  JCH_DigiPlayer
   2  256bytes/Laxity
   2  Randy_Glover
   2  Roy_Glover
```

**Migration-target totals (NewPlayer core):** `JCH_NewPlayer` 3611 + `Laxity_NewPlayer_V21`
313 + `Glover_NewPlayer_V21` 67 + `Dane`/`(Dane_NewPlayer)` 13 = **~4004 SIDs** of the
core NP lineage; +179 `Vibrants/Laxity` +130 `Vibrants/JO` if those forks are folded in.

**Crucial caveat:** HVSC does NOT split `JCH_NewPlayer` by V-number. All 3611 carry the
single label `JCH_NewPlayer`. The V1..V20 split exists ONLY inside SIDId's sub-sigs and in
DeepSID's player-name tag. To get per-V-number population you must **re-run SIDId locally
against the HVSC binaries** (the sub-sig that hits = the version). This is the highest-value
next step for migration sequencing — see Leads.

## Address convention (matches DMC)

Standard NP layout is identical to DMC's entry convention:
`load $1000` (PSID 2-byte prefix → load_addr stored as $0000), **init = base+$0000
($1000)**, **play = base+$0003 ($1003)**, extra/multispeed entry at base+$0006.
This 1:1 matches `pipelines/dmc/docs/research.md` "Entry Points" — see the lineage doc.

## Leads to follow

- **Re-run SIDId per-binary over HVSC's 3611 JCH_NewPlayer SIDs** to get the V1..V20
  population histogram (sub-sig hit = version). Without this the per-variant migration
  order is blind. Tool: the `player-id` binary or a small Python sig-matcher over the
  config (the byte grammar is simple — `??`=skip-1, `&&`=skip-N).
- **Disassemble one representative per dominant V-number** (likely V20 + V21 dominate
  modern tunes) and confirm my opcode readings above against real code.
- The `V16` gap and the `V0x` init-only sig: confirm V0x ≈ our `universal_reset` init so
  the trichotomy comparator applies directly (it almost certainly does — `#$88` testbit
  preset on all 3 ctrl regs is the classic NP hard-restart).
- Fold `Vibrants/Laxity` (+6 play offset) and `Vibrants/JO` decisions: are these in-scope
  for the JCH composer or separate engines? The +$06 play offset suggests a different
  header (init/play/mplay/sync table) but the same core.
