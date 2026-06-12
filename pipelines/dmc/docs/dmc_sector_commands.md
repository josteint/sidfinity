---
source_url: https://tnd64.dreamhosters.com/music_scene.html §2.5.2 (DMC 4/7 sector commands) + https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/dmc_5_docs.txt.gz (V5 command list) + DMC 4 Editor 1.1 ReadMe.txt + dmc4editor.exe format strings (csdb.dk/getinternalfile.php/267129)
fetched_via: direct
fetch_date: 2026-06-12
author: synthesis by Claude (sidfinity research wave); underlying texts by Richard Bayliss/TND + Rio/Rattenrudel, The Syndrom, Logan/Slackers
content_date: 1993-2025
reliability: secondary for the command enumerations (multiple independent sources agree); byte-range mapping for $C0-$DF is INFERENCE (flagged); $E0-$FF remains unknown
---

# DMC sector command bytes — what the editor command sets pin down

Targets HOLE 2 ($C0-$DF and $E0-$FF semantics). Key result: the V4 editor
command set is now CLOSED across three independent sources, which constrains
$C0-$DF to a single candidate. V5 uses a different (still unknown) encoding.

## V4/V7: the complete sector command set

Three independent sources enumerate exactly the same commands and nothing
else:

1. TND tutorial §2.5.2 (DMC 4/7): `DUR.xx, SND.xx, GLD.xy, VOL.0x, SWITCH,
   -GATE-, END!`
2. DMC 4 Editor 1.1 by Logan/Slackers (2025 cross-platform reimplementation —
   author necessarily RE'd the byte format): ReadMe lists SND, DUR, VOL, GLD,
   Gate, Switch, End.
3. dmc4editor.exe display format strings (extracted 2026-06-12):
   `%.2X: DUR.%.2X`, `%.2X: SND.%.2X`, `%.2X: GLD.%.2X`, `%.2X: VOL.%.2X`,
   `%.2X: -GATE-`, `%.2X: SWITCH` (plus `NO GATE FX`).

So the V4 sector byte space must cover: notes, DUR, SND, GLD, VOL, SWITCH,
GATE, END, and (editor-visible) the empty step `------`. Mapping against the
already-known ranges:

| Byte range | Command | Status |
|------------|---------|--------|
| $00-$5F | note (96 notes) | known |
| $60-$7C | DUR.xx (AND $1F; 0 = 1 tick) | known |
| $7D | SWITCH (tie / skip ADSR+hard-restart for following notes; toggles off at next SWITCH or sector END) | known, semantics confirmed by TND §2.5.2 |
| $7E | -GATE- (gate off / release; counted as a full step) | known |
| $7F | END of sector | known |
| $80-$9F | SND.xx (AND $1F = instrument 0-31) | known |
| $A0-$BF | GLD.xy — see refinement below | known range, REFINED semantics |
| **$C0-$DF** | **VOL.0x — by elimination, the ONLY remaining V4 command** | **inference, needs 1 binary check** |
| **$E0-$FF** | **no V4 editor command remains → likely unused/invalid in V4** (V5 uses $FF = sector end) | **unknown** |

### GLD refinement (corrects "glide = $A0 + semitones")

TND documents GLD as a TWO-NIBBLE command `GLD.xy`:
- `x` = mode: **0 = glide between two fixed notes** (the next TWO bytes are
  start + destination note, interpreted together as ONE step), **1 = slide
  the currently playing note** to the next note (ONE note follows).
- `y` = speed: 0 = none, 1 = slowest, F = fastest. If the glide isn't
  finished when the next note plays, it keeps gliding into it.

`x` is one bit and `y` is one nibble = exactly 5 bits = the $A0-$BF range:
byte = $A0 | (mode<<4) | speed. The old "$A0 + semitones" reading in
research.md is wrong — the operand is mode+speed, not an interval.

### VOL semantics (TND §2.5.2, for when $C0-$DF is confirmed)

- `VOL.0x` sets the channel volume; in the player it writes the SUSTAIN level,
  so it "works only if no Attack or Decay is set" on the instrument.
- Max $F. The last VOL is stored globally per channel.
- `VOL.00` = reset: following instruments use their own sustain again.
- Only 16 meaningful values → expect either $C0-$CF used / $D0-$DF aliased,
  or AND $1F with values >$0F being garbage. Which one = 1-line check in the
  player's dispatch.

### Open V4 questions

- How is the editor's empty step `------` stored? It consumes a full duration
  tick like a note ("Notes, GATE and --- are interpreted as full played
  notes"). Candidates: a reserved note byte, or one of $E0-$FF. UNKNOWN.
- Whether $E0-$FF do anything at all in the V4 player (junk-tolerant ranges
  matter for the extractor). UNKNOWN.
- Track-level (NOT sector) commands for reference: TR+/TR- transpose, -END-
  with loop-position operand (broken in V7: always loops to line 0), STOP!.

## V5: bigger command set, different encoding (UNKNOWN bytes)

The original V5.0 docs enumerate ~14 sector commands (editor keys in
parentheses), confirmed (with renamings) by TND §3.5:

| Command | Key | Semantics (original docs) |
|---------|-----|---------------------------|
| DUR.xx | Shift+D | duration |
| SND.xx | Shift+S | sound number $00-$1F |
| FD+ | Shift++ | fade in; value = speed (low slow, high fast) |
| FD- | Shift+- | fade out |
| GLD.x | Shift+G | glide; value = speed; TWO notes follow (start, destination) |
| SLD.x | Shift+H | slide; ONE note follows (slides the playing note) |
| ADR.xx | Shift+A | set AD register (place before a note) |
| SRR.xx | Shift+Z | set SR register (live; raising sustain above current resets the voice) |
| FRQ.xx | Shift+Q | base filter frequency, hi-byte only |
| FLT.xy | Shift+F | x = filter type 0-7, y = resonance 0-F |
| VOL.0x | Shift+V | sets sustain 0-F; 00 = instrument's own sustain; place before a note |
| GATE | £ | clear gate bit; a SECOND consecutive GATE retriggers the note |
| SWITCH | Shift+X | disable hard restart → tie notes |
| END | = | end of sector |

(TND's V5 list names ADSR.xx (Shift+Y), FILT.xy, FREQ.xx — likely the same
commands under V5.0+/CreaMD-era labels; the original docs' ADR/SRR split is
first-party and should be trusted for V5.0.)

Byte-level constraints known for V5:
- Parameter values must be ≤ $FE; **$FF = END marker, and the packer scans
  sector data for $FF** → $FF terminates a stored sector.
- 14 commands no longer fit the V4-style $60-$FF window cleanly alongside
  96 notes + 32 instruments; together with V5's switch to 2-byte table
  entries, expect command+operand byte pairs. The exact encoding is
  UNDOCUMENTED anywhere we could find — needs RE from `DMC_V5.prg` /
  packed V5 modules (both in tmp/dmc_hunt/).

## Provenance trail

- TND tutorial: full text saved as `tnd_dmc_tutorial.txt` (§2.5.2 = V4
  commands, §3.5 = V5 commands).
- Original V5 docs: `dmc_v5_docs_original.txt`.
- DMC 4 Editor 1.1: ReadMe + exe strings, zip in tmp/dmc_hunt/ (not
  committed; re-download via csdb.dk/getinternalfile.php/267129).
- CSDb forum search "DMC format": no byte-level threads exist (checked
  2026-06-12).
