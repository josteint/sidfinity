<!--
provenance:
  source_url: https://github.com/ice00/jc64  (doc/example/MusicAssembler.dis, musicAssembler_.dis, VoiceTracker.dis)
  fetched_via: git clone ice00/jc64 -> gzip-decompress the JC64dis .dis project files ->
               extract author annotations/labels (this session, 2026-06-13).
               Raw string dump saved alongside as jc64dis_MusicAssembler_annotations.txt.
  author: Stefano Tognon (Ice Team), hand-annotated disassemblies of:
            * MC_01.sid — "MC_01" by Marco Swagerman, 1988 Dutch USA Team (load $5000) -> MusicAssembler.dis
            * Magazine_Intro_Tune.sid — Reyn Ouwehand, 1989 (load $1000) -> musicAssembler_.dis
            * 3LUX_Intro.sid — The Bill, 1993-95 (VoiceTracker) -> VoiceTracker.dis
  content_date: 1988 (player); JC64dis project ongoing
  reliability: HIGH — these are author-assigned routine labels + per-write comments for the
               ACTUAL player, independently cross-checked against this session's own
               disassembly of OPM/Sid_Slam.sid (spec_player_RE_grounded.md). Where the two
               sources name the same thing (e.g. voiceSidIndex == $C0C6,X), they agree.
-->

# Music Assembler — authoritative player RE (from JC64dis annotations)

The JC64dis project (Ice Team, GPL-2) ships **hand-annotated disassemblies of
the Music Assembler player** as example `.dis` projects. This is the closest
thing to a public RE writeup of MASM that exists, and it resolves every
"OPEN" item from the GAP analysis: the packed data layout, the full pattern
(sequence) opcode map, and the effect runner. The author's own header reads:

```
=============================================
 MUSIC ASSEMBLER player
 by Marco Swagerman (MC) & Oscar Giesen (OPM)
 1988 Dutch USA Team
=============================================
 The data is structured as follow:
 -> lo/hi pointers for arpeggio table
 -> the lo/hi pointers for track
 -> Pattern data
 -> Tracks (3, 2, 1) pattern data
 -> arpeggio table
 -> hi/lo pointers for pattern table
 -> preset table
=============================================
```

## Packed data section layout (V1.0 / Dutch USA-Team order)

In file order after the player code (all pointer tables are **lo[] then hi[]**
parallel arrays, indexed by table entry number):

1. **arpeggio pointer table** — `arpeggioTableLo[]`, `arpeggioTableHi[]`
2. **track pointer table** — `trackLow[]`, `trackHi[]` (3 tracks)
3. **Pattern (sequence) data** — the byte streams
4. **Tracks pattern data** — the per-track orderlists, stored order **3,2,1**
5. **arpeggio table** — the arpeggio step data
6. **pattern (sequence) pointer table** — `patternTableHi[]`, `patternTableLo[]`
7. **preset table** — 8 bytes/preset

(VoiceTracker reorders this — see "VoiceTracker delta" below.)

## Player structure (labelled routines)

Entry points (confirmed identical to spec_player_RE_grounded.md): IRQ install
at base, `playSound` at base+$21, `initSongs`/`initSound` at base+$48.

Routine inventory (from the JC64dis labels — full list in
`jc64dis_MusicAssembler_annotations.txt`):

- **IRQ / dispatch**: `initSound`, `IRQ`, `playSound`, `speedCounter`
  ("Song speed (coded into the source)"), `reloadVoiceIndex`,
  `nextVoiceDurDelayCheck` ("Note is finished, use instrument again"),
  `loopVoices` ("Cycle all voices"), `durDelayCheck`.
- **init**: `initSongs` — "Max volume and low pass filter", "Select volume and
  filter mode" ($D418), "Filter resonance control/voice input control" ($D417),
  "Clear current voice". "Read first sequence in track / Store sequence to play
  / Store transpose*16 of notes in sequences / Store number of repeat for the
  sequence" = the per-track orderlist priming.
- **sequence fetch / decode** (the sidid signature region): `useSequence`,
  `sequenceIndex`, `trackIndex`, `noteDuration`, `sequence`, `noNote`,
  `testPreset` ("Preset mark?"), `extractPreset` ("index is *8"),
  `outNote` ("Add the transpose (high nibble to move as low nibble)"),
  `readParEffectSlide`, `isFilterEffect`, `setRelease`, `checkEndSeq`,
  `updateTrackIndex`, `clearSeqIndex`, `updateSeqIndex`, `usePreset`,
  `useNextPreset` ("Load actual preset to use (already *8)").
- **per-voice SID output** (`playSound` body): comments name each write —
  "Generator 1: Sustain/Release" ($D406), "Generator 1: Attack/Decay" ($D405),
  "Voice 1: Control registers" ($D404), "Voice 1: Frequency control (lo/hi
  byte)" ($D400/$D401), "Voice 1: Wave form pulsation amplitude (hi/lo byte)"
  ($D403/$D402). `voiceSidIndex` = "index for voice in Sid registers (fixed)"
  == the `$C0C6,X` voice-base array ($00/$07/$0E) found independently.
- **effects**: `checkVibSpeedCounter`/`makeFreqVibrato`/`addVibrato`/
  `subVibrato`/`vibDirectionIndex` (frequency vibrato; "Change direction based
  onto table of values"); `checkPulseSlide`/`makePulseSlide` (add pulse byte/
  frame); `checkPulseVibrato`/`makePulseVibrato`/`addPulse`/`subPulse`/
  `pulseDir`/`resetPulse` (pulse vibrate); `rattlingSlide`/`addSlide`
  ("On odd value apply a Rattling slide every two frames"); `makeArpeggio`/
  `checkArpeggio`/`skipArpeggio`/`goNextArpeggio`/`stopArpeggio`/`noteArpPos`
  (arpeggio: "Read waveform / Read note offset (absolute or relative) / Read
  filter low pass value / Stop arpeggio? / Restart arpeggio (it was FF)");
  `setFilterResCtrl`/`stopFilterVoice`/`filterCutOff`/`filterFrameDur`/
  `filterVelocity` ("Subtract 10 by the velocity"), `filterHiPos`
  ("Filter cut frequency: hi byte" -> $D416), `filterRes`.

## Pattern (sequence) byte opcode map — AUTHORITATIVE

The JC64dis annotation gives the exact decode for the pattern byte stream
(`AA` = the dispatched byte; `BB`,`CC`,`DD` = following bytes):

```
1010 xxxx        -> Preset xxxx                 (byte $Ax: select preset, low nibble = preset id)
101x xxxx        -> HOLD, Duration xxxxx         (legato hold; note "101x" overlaps $Ax — see note)
AA <= 0101 0000  -> NOTE  (AA <= $50)            ; a note index into the freq table
    BB yyyx xxxx -> Duration xxxxx               ; following byte: low 5 bits = duration
       010x xxxx -> Hold xxxxx                   ; (BB bit pattern selects sub-effect)
       001x      -> Slide                        ; then CC = slide low freq, DD = slide high freq
       100  xxxx -> Filter                       ; then CC = cut off/speed, DD = duration of effect
AA >= 011x xxxx  -> REST, Duration xxxxx with release   (AA >= $60: rest, kicks Release phase)
$FF              -> End of pattern
```

Read alongside this session's own dispatch trace (spec_player_RE_grounded.md
$C0F9/$C0D2), which agrees: notes are `< $60`, the `$60..$7F` range is a
duration/rest class (`AND #$1F`), `$80..$FF` are commands sub-dispatched at
`CMP #$A0`. The `1010 xxxx -> Preset` and the slide/filter follow-bytes match
exactly. So a complete pattern stream is:

- `$00..$50` NOTE byte, **followed by** a duration/effect byte `BB`:
  - `BB` low 5 bits = note duration (matches manual `$00..$1F`).
  - `BB` bit pattern selects an inline effect attached to the note:
    `001x` = SLIDE → consume 2 more bytes (CC=lo freq, DD=hi freq);
    `100x` = FILTER → consume 2 more bytes (CC=cutoff nibble+speed nibble,
    DD=frame duration); `010x` = HOLD.
- `$60..$7F` (`011x xxxx`) = REST with release, duration = low 5 bits.
- `$A0..$AF` (`1010 xxxx`) = PRESET select, id = low nibble.
- `$80..$9F` / `$B0..$FF` (`101x xxxx` overlap) = HOLD/legato duration.
- `$FF` = end of pattern (track advances to next orderlist entry).

(The `$Ax` preset vs `101x` hold overlap is resolved by the player's two-stage
`BMI` then `CMP #$A0` dispatch — see $C0D2 in the grounded doc. Treat
`$A0..$AF` as PRESET and `$80..$9F`,`$B0..$FF` as HOLD when implementing.)

## Track (orderlist) format

Per the init annotations: each track entry primes "sequence to play",
"transpose*16 of notes" (transpose stored in the HIGH nibble — matches the
grounded `LSR×4` read of `$C0E6,X`), and "number of repeat for the sequence".
Sentinels: `$FE` stop, `$FF` loop track. **VoiceTracker adds `$FD` = "restart
from command".**

## Preset (instrument) 8-byte layout — corroborated

From `usePreset`/`extractPreset` ("index is *8") + the per-write comments, the
8-byte preset feeds: AD ($D405), SR ($D406), waveform/control ($D404), pulse
amplitude lo/hi ($D402/$D403), plus the work fields the effect runners read:
"Vibrato delay+speed value", "Fx + arpeggio value" (a byte combining effect
flags and the arpeggio-table index), pulse level/speed. This matches the
manual's documented preset fields (ADSR, waveform, pulse rate+effect, vibrato
delay/speed/level, arpeggio link). The grounded doc's tentative +4/+6 mapping
is the vibrato-delay+speed byte and the Fx+arpeggio byte.

## Arpeggio table format — corroborated

`makeArpeggio` reads per step: "Read waveform for arpeggio", "Read note offset
(absolute or relative) for arpeggio" (absolute = `<`, else added to current
note), "Read filter low pass value". "Stop arpeggio? / Restart arpeggio (it
was FF)" → `$FF` loop / `$FE` stop. Exactly the manual's 3-field arpeggio step.

## Freq tables

`freqLo`/`freqHi` labelled, comment "Notes in 8 octaves" → a 96-entry
(8 octaves × 12) note frequency table, lo[] + hi[]. The grounded doc located
these at `$C437`/`$C1C5` for the Sid_Slam build; standard C64 PAL note table.

## VoiceTracker delta (Science 451 / Pawel Soltysinski "Polonus", 1991)

JC64dis's VoiceTracker.dis header states it "extends the Music Assembler
player of MC & OPM". Initial VoiceTracker = **player code UNCHANGED**, only a
**data-structure reordering**:
```
 -> lo/hi pointers for arpeggio table
 -> lo/hi pointers for track
 -> arpeggio table
 -> preset table
 -> Tracks (1, 2, 3) pattern data        (note: 1,2,3 order, vs MASM's 3,2,1)
 -> Pattern data
 -> hi/lo pointers for pattern table
```
Plus one player feature: **track command `$FD` = "restart from command"** (a
new orderlist sentinel). When extracting HVSC, fingerprint MASM-vs-VoiceTracker
by data order + presence of `$FD` track bytes.

## Cross-reference

- This session's independent disassembly: `spec_player_RE_grounded.md`
  (load-relative offsets in OPM/Sid_Slam.sid; the per-frame `$D4xx` write set).
- Raw annotation dump: `jc64dis_MusicAssembler_annotations.txt`.
- Editor model: `spec_editor_model.md`.
