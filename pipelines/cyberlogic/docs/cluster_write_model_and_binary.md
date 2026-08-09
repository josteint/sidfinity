# Cyberlogic SoundStudio — write model, binary layout, and corpus clusters

---

## Provenance

| field | value |
|-------|-------|
| fetched_via | local hvsc85/ binary inspection + sidid.cfg + web search (codebase64, csdb.dk, HVSC) |
| fetch_date | 2026-06-14 |
| author | research agent (claude-sonnet-4-6) |
| content_date | 2026-06-14 |
| reliability | HIGH for binary-derived facts (direct byte inspection of HVSC SIDs); MEDIUM for web-sourced credits and version history |

Primary specimen: `hvsc85/MUSICIANS/N/Nagie_Sascha/A_Real_Compose.sid`
(canonical load=$1000, version label `v_arc_early`; fully inspected)

Secondary specimens inspected: `SID_Nation_IV.sid` ($6000 cluster, newer engine),
`Baroque_Parting.sid` (early Odi-solo version), `Eargasm.sid` (X-Radical variant),
`Plastic_Boots.sid` (CIA multi-tune container), `Timeout_Dang_Flight.sid` ($6000 early).

---

## Authors and tool

**Cyberlogic SoundStudio v4.0** (1991-1992, C64 music editor)

- Player code: **Oliver Klee** (handle Odi, MDG / Demons of Sound)
- Editor + later player revisions: **Sascha Nagie** (handle celticdesign, Demons of Sound -> Genesis Project)
- CSDB release: #170632 (editor tool release; player distributed embedded in SIDs)
- HVSC SID count: 196 (engine field `Cyberlogic_SoundStudio`)
- SIDId signature (single, no sub-variants):
  `9D ?? ?? B0 ?? DE ?? ?? ?? ?? ?? 4A 4A 4A 4A DD ?? ?? D0 ?? A9 ?? 9D END`

The SIDId match fires on the ADSR frame counter section: `STA abs,X; BCS; DEC abs,X;
... NOP; LSR LSR LSR LSR; CMP abs,X; BNE; LDA #$00` — the `4A 4A 4A 4A` (LSR*4) extracting
the hi-nibble as the current ADSR phase is the unique discriminator.

---

## PSID header quirk

All 196 SIDs have `load_addr = 0` in the PSID header. The actual load address is
embedded as the first two bytes of the payload (little-endian, standard C64 PRG prefix).
Parsers must read payload[0:2] as the true load address when `header.load_addr == 0`.

---

## Corpus clusters by load address

| cluster | count | init offset | play offset | examples | engine version |
|---------|-------|-------------|-------------|---------|----------------|
| `$1000` canonical | ~170 | +$A1..+$B6 | +$F0..+$13B | A_Real_Compose, Eargasm, etc. | mixed (v_arc_early, v_xradical, v_celticdesign) |
| `$6000` Nagie late | 9 | +$AE | +$105 | SID*Nation IV-XI | v_celticdesign_ae (newer engine) |
| `$6000` early Timeout | 4 | +$9B | +$F8 | Timeout_Dang_Flight, Timeout_Eternity, etc. | "MINIPLAYER3.0 91 BY TBN" (older, early Oliver Klee line) |
| `$8000` | few | varies | varies | Stroke_World (load=$2100), others | container variants |
| `$0FA0` multi-tune | 2 | varies | varies | Plastic_Boots, Trouble_Three | CIA-wrapper container |

### $6000 Nagie late (SID*Nation IV-XI, 2013-2014)

9 SIDs by Sascha Nagie, 2013-2014. Load=$6000, init=$60AE, play=$6105.
String at load+$12: `*NATIONX(C)ELTICDESIGN201X`.

This is a **different engine version** (v_celticdesign_ae) from the canonical $1000 player:
- Uses LSR*6 (`4A`*6) in init routine ($6185-$61A5) for per-voice instrument field extraction
  (3 instances, one per voice, in init only)
- LSR*4 still appears in 3 play-code locations (same ADSR/vibrato pattern as $1000 engine)
- Voice write order, filter writes, and SIDId pattern are identical to $1000 engine
- Song data differs per member (confirmed IV vs VII: 679 mismatches in first $B00 bytes;
  engine code bytes essentially unchanged across members)

### $6000 early (Timeout series, 1992)

4 SIDs by The_Blue_Ninja, 1992. Load=$6000, init=+$9B, play=+$F8.
String: `MINIPLAYER3.0 91 BY TBN`.

This is the **early Oliver Klee player relocated to $6000** — same short jump table (4 entries,
not 6), same approximate init/play offsets as Baroque_Parting ($1000 base, early Odi).
NOT related to the SID*Nation engine.

### CIA multi-tune container (Plastic_Boots, Trouble_Three)

Load=$0FA0. $0FA0-$0FCF: CIA/VIC init wrapper; sets $0314/$0315 IRQ vector.
$1000: normal player jump table. Each subtune is a separate song using the standard
$1000-based player. The CIA wrapper drives per-subtune selection.

---

## Player binary layout (canonical $1000-base, v_arc_early)

Specimen: `A_Real_Compose.sid` — see `/pipelines/cyberlogic/docs/src/v_arc_early_bytemap.md`
for full byte dump.

```
$1000-$1011  6-entry jump table (6 JMPs)
$1012-$1031  ASCII ID string: e.g. "MUSIC SASCHA NAGIE,PLAYER O.KL" + padding
$1032-$10A0  Config + per-voice runtime state block (zeroed on init)
$10A1-$112A  Init routine: zero state block, init voices, silence SID chip
$112B-$165F  Play routine: speed counter, 3-voice loop, pattern reader, effect chain
$1660-$169F  Voice write section: STA $D4xx sequence for 3 voices
$16A0-$16FF  Filter and volume writes ($D416, $D417, $D418)
$1700-$17D7  Additional subroutines (vibrato, arp, portamento, gate-off, hw-restart)
$17D8-$191F  Instrument tables: 13 parallel 32-entry arrays (see below)
$1928-$1986  Freq lo table: 95 entries (also pattern pointer lo)
$1987-$19E5  Freq hi table: 95 entries (also pattern pointer hi)
$19E6-$1A9D  Voice 1 section->pattern table: 32 entries
$1A9E-$1B55  Voice 2 section->pattern table: 32 entries
$1B56-$1C0D  Voice 3 section->pattern table: 32 entries
$1C0E-$1C7F  Section metadata tables: 6 parallel arrays (filter, tempo, vol, ...)
$1C80-$1D0D  Additional section/meta or padding
$1D0E-$21XX  Pattern stream data (variable; ends with $2A $2A $2A marker)
```

Jump table entries (6 JMPs in all Nagie-era versions; 4 JMPs in early Odi versions):
```
+$00  JMP init
+$03  JMP play
+$06  JMP voice_reset      (triggered on note-on)
+$09  JMP sub_gate_off     (gate-off helper)
+$0C  JMP sub_adsr_helper
+$0F  JMP sub_pattern_adv  (pattern advance / section transition)
```

---

## Per-frame write model

### Speed counter mechanism

`$1032` = main frame counter. Decremented each play() call.
`$1033` = sub-counter, reloaded from `$1C3E[section]` when $1032 reaches 0.
Typical values: 2 or 3 (= 25 or ~16.7 notes/second at 50Hz).
$1037 != 0 signals song-done; play() returns early.

### Three-voice loop

play() iterates X = 2, 1, 0 (voice 3, 2, 1). For each voice:

1. Read current byte from pattern stream via ZP pointer ($39/$3A = 16-bit ptr).
2. Dispatch by byte value:
   - $00-$5F: note event — trigger gate-off on prev note, load instrument registers,
     set new freq, write attack/decay, set gate-on.
   - $60-$7F: instrument select — update current instrument# (inst = byte & $1F),
     cache instrument table data into voice state slots.
   - $80-$FB: effect commands (arp, vibrato, portamento, filter — semantics TBD).
   - $FC/$FD: commands with 1-byte argument (loop count, transpose).
   - $FA: loop-point marker (set loop-back position in stream).
   - $FF: end of pattern — advance section counter, load next voice patterns,
     reload filter/tempo/vol from section tables, reset stream positions.
3. Decrement duration counter. If zero, advance stream to next byte.

### Voice register write order (confirmed from $1660 byte sequence)

```
STA $D401,Y  freq hi      <- UNUSUAL: high byte before low
STA $D400,Y  freq lo
STA $D402,Y  pulse lo
STA $D403,Y  pulse hi
STA $D405,Y  attack/decay
STA $D406,Y  sustain/release
STA $D404,Y  ctrl/waveform  <- gate bit written last
```

Y = voice# * 7. Voice 3 (X=2) written first, then voice 2 (X=1), then voice 1 (X=0).
Order within a frame: V3 freq_hi, V3 freq_lo, V3 pw_lo, V3 pw_hi, V3 AD, V3 SR, V3 ctrl;
then same for V2, V1; then global filter.

### Filter writes (global, once per frame)

```
STA $D416    filter cutoff hi    (@ $169A in v_arc_early)
STA $D417    filter res+routing  (@ $16A1)
STA $D418    vol + filter mode   (@ $16F4)
```

$D418 value sourced from `$1C5E[section]` — observed values: $81 (filter+vol), $80 (vol only),
$41 (filter+vol lower), $40.

---

## Instrument tables (13 parallel 32-entry arrays)

All tables indexed by instrument# (0-31). Identified from play() access trace.

| base addr | name | D4xx target | notes |
|-----------|------|-------------|-------|
| $17D8 | waveform_gate | D404 | Waveform + gate-on. $41=pulse+gate, $11=noise+gate, $40=pulse |
| $17F0 | waveform_release | D404 | Waveform for gate-off (gate bit cleared) |
| $1800 | flags_a | — | Effect enable: bit $40=hw_restart, $08/$04=arp/vibrato enable |
| $1808 | flags_b | — | Effect parameter A (arp table index or vibrato depth select) |
| $1820 | attack_decay | D405 | Attack (hi-nibble) and decay (lo-nibble) |
| $1838 | sustain_release | D406 | Sustain (hi) and release (lo), note-on value |
| $1850 | hw_restart_ad | D405 | Attack/decay used during hard-restart (gate-off phase) |
| $1868 | vibrato_depth | — | Vibrato or arp depth (0=off) |
| $1880 | vibrato_speed | — | Vibrato or arp speed |
| $18B0 | release_sr | D406 | Sustain/release for gate-off. Typical: $F0 = sustain full, instant release |
| $18C8 | filter_cutoff | D416 | Per-instrument filter cutoff value ($00 = no filter write) |
| $18F8 | pulse_width | D402 | Pulse width low byte or PW sweep parameter |
| $1910 | portamento | — | Portamento speed per instrument (0=off) |

Note: $17F8-$17FF (8 bytes) between waveform_gate and the next block are
uncharacterised — possibly part of a 40-byte combined table or alignment padding.

---

## Song structure: section-based architecture

Cyberlogic SoundStudio uses a **section** abstraction (not a flat per-voice orderlist).
A section defines: which pattern each voice plays, plus global properties (filter, tempo, volume).

### Section metadata (6 parallel arrays, indexed by Y = section#)

```
$1C0E[Y]  section loop-count SMC sentinel (dynamically rewrites a CPY operand in play code)
$1C1E[Y]  voice 2 section parameter (role: overlaps section-end detection; partly unclear)
$1C2E[Y]  per-section filter cutoff ($D416); $FF = no change this section
$1C3E[Y]  per-section tempo = speed sub-counter reload (observed: 2 or 3)
$1C4E[Y]  per-section meta flag (purpose TBD)
$1C5E[Y]  per-section $D418 = volume + filter mode
```

### Voice-to-pattern tables (one per voice, 32-entry each)

```
$19E6[Y]  voice 1 pattern# for section Y
$1A9E[Y]  voice 2 pattern# for section Y
$1B56[Y]  voice 3 pattern# for section Y
```

All three voices advance a shared section counter when pattern streams hit $FF.

---

## Pattern stream format

Pattern N starts at `addr = {$1987[N] << 8} | $1928[N]`.
The freq table and pattern pointer table are the SAME 95-entry array.

```
byte       meaning
--------   -------------------------------------------------------
$00-$5F    note event (freq table index 0..94)
           next byte = duration: hi-nibble * 16 + lo-nibble frames
$60-$7F    instrument select: inst# = byte & $1F
$80-$FB    effect command (arp/vibrato/portamento/etc; exact opcodes TBD)
$FC NN     command with argument NN (loop count or transpose; TBD)
$FD NN     command with argument NN (pitch transpose / key shift; TBD)
$FA        loop-point marker (next $FF loops back here instead of ending)
$FF        pattern end -> advance section, load next patterns, reset stream
```

Pattern data ends with `$2A $2A $2A` (ASCII "***") sentinel in all v_arc_early specimens.

---

## Player version variants (fingerprinted across 196 SIDs)

Variants identified by (init_offset, play_offset, lsr6_in_init, jump_table_entries):

| variant label | init off | play off | lsr6 in init | jtable entries | example |
|---------------|----------|----------|-------------|----------------|---------|
| v_odi_early | +$98 | +$F0 | no | 4 | Baroque_Parting |
| v_arc_early | +$A1 | +$12B | no | 6 | A_Real_Compose |
| v_xradical_b6 | +$B6 | +$13B | yes (3x, init only) | 6 | Eargasm |
| v_celticdesign_ae | +$AE | +$105 | yes (3x, init only) | 6 | SID_Nation_IV ($6000) |
| v_tbn_6000 | +$9B | +$F8 | unknown | 4 | Timeout_Dang_Flight ($6000) |

Key evolution:
- v_odi_early: shortest player (~2500 bytes), only 4-entry jump table, Oliver Klee solo
- v_arc_early: Nagie collaboration, 6-entry jump table, ~4500 bytes, more effects
- v_xradical/v_celticdesign: LSR*6 added in init for a 6-bit field (instrument slot? effect param?)
- v_celticdesign_ae ($6000 cluster): newest visible; same as v_xradical in structure, relocated

The SIDId single signature covers all variants (the ADSR LSR*4 site is stable across all versions).

---

## LSR*4 and LSR*6 sites

In v_arc_early ($1000):
```
$12C1  LSR*4: instrument# from note-stream byte hi-nibble -> $1044,X
$14E0  LSR*4: ADSR counter hi-nibble -> ADSR phase (SIDId match here)
$1518  LSR*4: vibrato speed/depth nibble extract
```

In v_celticdesign_ae ($6000, SID_Nation_IV):
```
$6185-$61A5  3x LSR*6 in init (once per voice): 6-bit instrument slot extract
$6296  LSR*4: instrument# (same role as $1000/$12C1)
$653C  LSR*4: ADSR counter (SIDId match)
$6574  LSR*4: vibrato nibble
```

The LSR*6 in init may extract a 6-bit initial instrument# (vs 4-bit in older versions),
supporting up to 63 instruments (though the 32-entry tables cap it at 31 + 1 base).

---

## Gaps and unknowns

1. **$80-$FB effect command opcodes**: exact opcode map for arp, vibrato-on, portamento-trigger,
   tie-note, and any other in-stream commands is not yet decoded. The play code at $1260-$12D0
   dispatches on these but the branch targets were not fully traced.

2. **$FC/$FD argument semantics**: confirmed that $FC and $FD each take one following byte.
   The meaning of that byte (loop count? transpose semitones? both?) is TBD.

3. **Section advance timing**: it is unclear whether the section advances when the FIRST voice
   or the LAST voice finishes its pattern. The $1035 flag mechanism suggests all three voices
   signal done and the third triggers the advance, but this was not confirmed by code trace.

4. **$1C0E/$1C1E role**: the SMC mechanism that dynamically rewrites a `CPY #$0F` operand
   using $1C0E[Y] is understood at the bytecode level but its musical interpretation
   (does it control section repeat count, or something else?) is unclear.

5. **LSR*6 in init (new versions)**: what 6-bit field this extracts and where it is stored
   was not traced; only the byte locations are known.

6. **v_odi_early detailed layout**: only inspected at the jump table level;
   full instrument table / section structure not verified for the early Oliver Klee variant.

7. **$18F8 table semantic**: classified as `pulse_width` by position and access pattern
   but the play code routine that uses it (@ $14A1) was not fully decoded.

8. **Stroke_World.sid (20 subtunes, load=$2100)**: unusual load address; assumed to be
   another container variant. Not inspected.

9. **SIDId `9D END` trailing byte**: the sidid.cfg signature ends with `9D END`
   which implies the full signature requires one more `STA abs,X` byte after `A9 00`.
   The exact match context was not fully disassembled.

---

## Leads to follow

- **Decode $80-$FB effect opcode table** by disassembling $1260-$14FF in A_Real_Compose.
  Use `siddump --pc-trace` on a known-effect SID to attribute register writes to PC,
  then cross-reference the dispatch table branch targets.

- **Section advance mechanism**: trace $1035 usage (BNE $119B at $1187) to determine
  whether section advance is voice-1-driven or all-voices-done. Impacts how USF
  should encode the song structure.

- **$FC/$FD semantics**: inspect patterns containing $FC/$FD with known-good audio playback
  using `siddump --writelog` and identify what changes in the write stream after these bytes.
  Patterns 3, 8, 10, 11 in A_Real_Compose contain $FC/$FD.

- **$1C0E SMC mechanism**: step through section transitions in py65 or with siddump
  `--memwatch-on-write $117A` to capture what value the SMC writes and how it changes behavior.

- **v_odi_early full RE**: Baroque_Parting is a short early SID; complete its instrument table
  mapping to confirm whether the early player has a subset of the 13 tables.

- **LSR*6 in init (new versions)**: trace $6185 in SID_Nation_IV to find where the 6-bit
  result lands (ZP or RAM slot) and what the play() routine does with it.

- **Multi-subtune container (Stroke_World)**: examine how 20 subtunes are addressed;
  compare to Plastic_Boots CIA wrapper to find if there is a third container pattern.

- **Check CSDB #170632** for the full tool release: editor screenshots, format docs,
  or source code fragments that may clarify the $FC/$FD and $80+ effect opcode semantics.

- **DeepSID source** (`github.com/Chordian/deepsid`) may contain a Cyberlogic SoundStudio
  player implementation in JavaScript with comments that document the command set.
