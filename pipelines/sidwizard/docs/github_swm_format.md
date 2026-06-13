# SID-Wizard — SWM workfile format spec (`SWM-spec.src` + `swm.h`)

> **Provenance**
> - source_url: https://github.com/anarkiwi/sid-wizard (mirror of https://sourceforge.net/p/sid-wizard/code)
> - raw files: `https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/SWM-spec.src` (`$Id: SWM-spec.src 382 2014-06-23 hermitsoft`), `.../sources/sng2swm/swm.h` (`$Id: swm.h 360 2014-02-15 soci`), cross-checked with `.../sources/SWMconvert.c`, `.../sources/include/player.asm`
> - fetched_via: curl (raw.githubusercontent.com)
> - fetch_date: 2026-06-13
> - author: Hermit (Mihály Horváth); `swm.h`/`SWMconvert.c` co-authored with Soci/Singular
> - content_date: SID-Wizard 1.x (SWM "SWM1" format)
> - reliability: **primary** (the canonical format definition shared between the 64tass editor and the gcc converters)

Defines the **SWM1 workfile** format (`SWM-spec.src` is `#include`d by both the
64tass build and the C tools). This is the *editor's* native format. The
exporter compacts it into the SID binary (header dropped, names stripped, pointer
tables built) — see `github_exporter_layout.md`. The pattern/sequence/instrument
**opcodes here are the same ones the player decodes at runtime**, so this is the
musical-content vocabulary for USF.

The two stereo IDs: `"SWM1"` (mono) and `"SWMS"` (the research.md note; the
canonical tag constant in source is `SW1_TAG = "SWM1"`, `swm.h:106`).

---

## 1. Capacity constants (`SWM-spec.src:4-26`)

```
maxsubtuneamount = 8-1 = 7   ; max $1F theoretical (SUBTUNE_MAX=31); counted from 0
maxptnamount     = 100       ; max patterns
maxinstamount    = 36+1 = 37 ; max instruments (INSTR_MAX=62 theoretical)
seqlength        = 126 ($7E) ; max sequence storage length
seqbound         = 128 ($80) ; sequence boundary (room for jump addr + $00)
maxptnlen        = 250-1 = 249 ($F9) ; max pattern size in bytes
PTNBOUND         = 256 ($100)
maxinstsize      = 128 ($80) ; memory per instrument
instnamelength   = 8         ; DON'T MODIFY (compat) — instrument name length
MAXCHORDAMOUNT   = 64 ($40)  ; incl. dummies at begin/end
maxchordlength   = 32 ($20)
ChordTableLen    = 256 ($100)
MAXTEMPOPRAMOUNT = 64 ($40)
maxtempolength   = 32 ($20)
TempoTableLen    = 128 ($80)
DEFAULTPTNLEN    = 32 ($20)
```
`SW1_PATTERNLENGTH_MAX = 0xF8` (rows), `SW1_PATTERNSIZE_MAX = 0xFA` (bytes)
(`swm.h:13-14`). Channels per SID chip = 3 (`SID_CHNAMOUNT`).

---

## 2. Header — fixed 64 bytes (`SWM-spec.src:30-56`, `swm.h:112`)

`tuneheadersize = 64 ($40)` — do not modify (cross-version compat).

| Off | Const | Field | Notes |
|-----|-------|-------|-------|
| $00-$03 | — | tag | `"SWM1"` (4 bytes) |
| $04 | `FSPEEDPOS` | framespd | frame speed 1..8 (1 = single/vblank; >1 = multispeed). Stashed into player `FRAME_SPD` at export. |
| $05 | `SWM_HILI_POS` | highlight | downbeat/step-highlight (editor; default 4) |
| $06 | `SWM_AUTO_POS` | auto_advance | **obsolete in SWM1** |
| $07 | `SWM_CBIT_POS` | conf_bits | **obsolete in SWM1**. Bit-field: b0 binding, b1 hide-rasters, b2 follow-play, b7 auto-instrument |
| $08-$0A | `SWM_MUTE_POS` | mutesolo[3] | `$FE`=mute, `$FF`=unmute, per track |
| $0B | `SWM_DEFP_POS` | default_ptn | default pattern-length for unspecified patterns |
| $0C | `SEQAMOPOS` | sequence_count | **# sequences** = 3 × (#subtunes); min 1. Calculated by packer. |
| $0D | `PTAMOUPOS` | pattern_count | # patterns (last used); empty-but-lengthy patterns count |
| $0E | `INSTAMPOS` | instrument_count | # non-empty instruments |
| $0F | `CHRDLEPOS` | chordtable_length | length of packed chord table (0 = none) |
| $10 | `TMPLENPOS` | tempotable_length | length of packed tempo-program table (0 = none) |
| $11 | `COLORTHEMEPOS` | colour_theme | **obsolete in SWM1** |
| $12 | `KEYBOARDTYPE_POS` | keyboard_type | **obsolete in SWM1** (GT/DMC jamming kbd) |
| $13 | `DRIVERTYPE_POS` | driver_type | **player variant**: bare/light/medium/normal/extra/demo. Informational in SWM; at export selects player size + `altplayers.inc` tables. |
| $14 | `TUNINGTYPE_POS` | tuning_type | 0 = 440 Hz normal, 1 = 432 Hz Verdi, 2 = Just-intonation (key of C) |
| $15-$17 | — | (reserved) | for later expansion (e.g. 2SID mute/solo) |
| $18-$3F | `AUTHORPOS` (24) | authorinfo | 40 bytes ASCII (`SW1_AUTHORINFO_SIZE`); export parses `title:author` around `:` |

---

## 3. Body — section order in the `.swm` file (`SWM-spec.src:59-106`)

Music data follows the header in this order:

```
1. Sequences  — for each sequence that contained a pattern, the orderlist bytes
                followed by a 1-byte size. e.g.  1,1,1,FE,(4)  2,2,2,FF,01,(5) ...
2. Patterns   — for each referenced pattern, the row bytes with the $FF end-signal
                replaced by a size byte, then expanded with a length byte.
                e.g.  9,2,0,BD,1,9,2,(7),(6)   7D,22,2,2,0,(5),(5) ...
3. Instruments— 16-byte base + variable tables; filter-table $FF end-signal
                replaced by instrument-size (without name); 8-char name appended.
4. Chordtable — chords back-to-back, each ended by $7E or $7F. Size = header $0F.
5. Tempotable — tempo-programs; each program's last byte has bit7 set. Size = $10.
6. Subtune funktempos — left/right (tempo1,tempo2) pair per subtune (#seq/3);
                one pair always stored even with no sequence. e.g. 88,84  08,84  20,90 ...
```

(The exporter reverses some of this and builds explicit lo/hi pointer tables —
parse the *exported* file via the ZP pointers, not these workfile offsets. See
`github_exporter_layout.md` §5-6.)

### 3.1 Sequence (orderlist) opcodes (`swm.h:16-22`, `SWM-spec.src` body)
Per track (3 tracks form one subtune/orderlist). `swm_header.sequence_count`
= total sequences = 3 × subtune count.
```
$01..$7F  pattern number
$80..$8F  transpose DOWN  ($90 = no transpose; $80..$9F is a signed range)
$90..$9F  transpose UP    ($90 = none)
$A0..$AF  volume set
$B0..$EF  track tempo
$FE       end-of-song
$FF       loop-song      (followed by loop position/index byte)
```
(`SW1_SEQUENCE_TRANS_MIN=$80`, `_TRANS=$90`, `_TRANS_MAX=$9F`, `_VOLUME=$A0`,
`_TEMPO=$B0`, `_ENDSONG=$FE`, `_LOOPSONG=$FF`.)

---

## 4. Pattern format (`SWM-spec.src:110-133`, `swm.h:24-90`)

A pattern is a byte stream of rows; each row has 1–4 columns. **Bit7 of a column
chains to the next column** (see player decode, `github_player_writemodel.md` §6).

### 4.1 Note column (column 1) — values
```
$00            REST / NOP (may be RLE-compressed by $70..$77)
$01..$5F       NOTE  (SWM_NOTE_MAX=$5F=95; pitch index into freq table)
$60..$6F       VIBRATO-AMPLITUDE set 0..F in note column (VIBRATOFX base $60)
$70..$77       PACKED rests: N empty rows (PACKEDMIN=$70 => 2 rests .. PACKEDMAX=$77 => 9 rests)
$78            AUTO-PORTAMENTO note-FX  (PORTAMFX; DEFAULTPORTA speed = 110)
$79 / $7A      SYNC on / off            (SYNCONFX / SYNCOFFX)
$7B / $7C      RING on / off            (RINGONFX / RINGOFFX)
$7D / $7E      GATE on (note-start) / GATE off (note-mute)  (GATEONFX / GATEOFFX)
$FF            PATTERN END  ($7F can't be used — it's $FF without bit7)
```
Bit7 set on the note byte (`>= $80`) ⇒ an instrument column follows (player ANDs
off bit7 to recover the note).

### 4.2 Instrument / small-FX column (column 2)
```
$00            NOP
$01..$3E       instrument select (SW1_INSTRUMENT_MIN..MAX)
$3F            LEGATO (SWM_LEGATO_INSFX; no hard-restart, no re-trigger)
$20..$7F       SMALL-FX (when no instrument): base+nibble, see 4.4
```
Bit7 set on this byte (`>= $80`) ⇒ an FX column follows.

### 4.3 FX column (columns 3[/4])
```
(fx & $E0) != 0   => SMALL-FX, value packed in low nibble; END OF ROW (no value byte)
(fx & $E0) == 0   => BIG-FX ($01..$1F); ONE value byte follows (CURVAL)
```

### 4.4 Small-FX base values (2nd nibble = value 0..F) (`swm.h:47-62`)
```
$20 ATTACK     $30 DECAY      $40 WAVEFORM   $50 SUSTAIN    $60 RELEASE
$70 SET-CHORD  $80 VIB-AMP    $90 VIB-FREQ   $A0 MAIN-VOL   $B0 FILTER-BAND
$C0 CHORD-SPD  $D0 DETUNE     $E0 WAVE-REG-C $F0 RESONANCE
```
(`SWM_VOLUME_SMALLFX=$50` checked by converter; `SWM_MAIN_VOLUME_SMALLFX=$A0`.)

### 4.5 Big-FX (followed by a value byte) (`swm.h:63-90`)
```
$01 PORT-UP        $02 PORT-DOWN     $03 TONE-PORTAMENTO  $04 WAVE-REG
$05 AD             $06 SR            $07 SET-CHORD        $08 VIBRATO
$09 WAVE-TABLE     $0A PULSE-TABLE   $0B FILTER-TABLE     $0C CHORD-SPEED
$0D DETUNE         $0E PULSE-WIDTH   $0F FILTER-CUTOFF    $10 TEMPO
$11 FUNK-TEMPO     $12 TEMPO-PROG    $13 TRACK-TEMPO      $14 TRACK-FUNK-TEMPO
$15 TRACK-TEMPO-PROG  $16 VIBRATO-TYPE   ($17..$1B reserved)
$1C FILTER-SHIFT   $1D DELAY-TRACK   $1E DELAY-NOTE       $1F FILTER-CONTROL
```
(`SWM_VIBRATO_BIGFX=8`, `SWM_DETUNE_FX=$0D`, `SWM_NOTEDELAY_FX=$1E` are cited by
the converter.)

---

## 5. Instrument format (`SWM-spec.src:71-96`, `swm.h:198-236`)

16-byte fixed base (`SW1_INSTRUMENT_PARAMSIZE=$10`) + variable wave/pulse/filter
tables + 8-byte name (`SW1_INSTRUMENT_NAMESIZE=8`). Max size 128
(`maxinstsize`). On save the filter-table's `$FF` end-signal is replaced by the
instrument size (without name), and the name is appended.

### 5.1 The 16-byte base
| Off | Const | Field | Detail |
|-----|-------|-------|--------|
| $00 | — | **control/flag byte** | bit0-1 `hrtimer` (HR timer length 0..2; 3 may = NTSC), bit2 `staccato` (HR-phase waveform `$18` test+mute), bit3 `wframe1` (1st waveform = `$09` testbit; SWM2 will move this to byte $F), bit4-5 `vibtype` (`$00` increasing, `$10` normal, `$20` down-oriented, `$30` up-oriented), bit6 `pwreset` (1 = disable PW-table reset until inst re-select), bit7 `flreset` (1 = disable filter-table reset) |
| $01 | — | hr_ad | Hard-restart Attack/Decay |
| $02 | — | hr_sr | Hard-restart Sustain/Release |
| $03 | `SWI_AD_POS` | ad | Attack/Decay on note-start (gate-on) |
| $04 | `SWI_SR_POS` | sr | Sustain/Release |
| $05 | `SWI_INSVIBRATO_POS` | vibrato | hi nibble = amplitude (exp-table scaled), lo nibble = frequency |
| $06 | `SWI_VIBDELAY_POS` | vibrato_delay | or amplitude-increase speed (when vibtype = increasing) |
| $07 | `SWI_ARP_SPEED_POS` | arpchord_speed | 0 = 1×. **bit6 = multispeed PW**, **bit7 = multispeed PW & filter** (read by `MULCNTP`, write-model §10) |
| $08 | `SWI_DEFCHORD_POS` | default_chord | ≥ 1 (chord 0 doesn't exist) |
| $09 | `SWI_OCTAVE_POS` | octave_shift | 2's-complement transpose, **in half-tones** (added to note → freq-table index) |
| $0A | `SWI_PULSETBPT_POS` | pulsetb_index | PW-table start, **relative to instrument base** |
| $0B | — | filtertb_index | filter-table start, relative to instrument base |
| $0C | — | wfgoff | gate-off pointer into WF-arp table (rel. to WF-table pos) |
| $0D | — | pwgoff | gate-off pointer into PW-table |
| $0E | — | fltgoff | gate-off pointer into filter-table |
| $0F | — | frame1_waveform | 1st-frame waveform (only if control bit3 `wframe1` set) |

### 5.2 Variable tables (start at +$10 = `WFTABLEPOS`)
Three tables stored contiguously: **wave-arp table** (hardwired at +$10), then
**pulse table**, then **filter table** (starts given by bytes $A,$B *directly* as
relative indices). Each is `$FF`-terminated in the workfile.

**Wave-arp table opcodes** (`swm.h:96-103`):
```
$00..$7E   positive relative pitch  (SW1_ARP_REL_MAX=$7E)
$7F        chord-call               (SW1_ARP_CHORDCALL)
$80        NOP / hold               (SW1_ARP_NOP)
$81..$DF   absolute note (C-0..; shown as C-1 in editor)  (SW1_ARP_ABS_MIN..MAX)
$E0..$FF   negative relative pitch  (SW1_ARP_REL_MIN=$E0)
$FE        TABLE JUMP   (next byte = table index to jump to)
$FF        TABLE END / loop
```
Wave/pulse/filter items are conceptually `(command, value, detune/kt)` triples
in the editor, but the third byte is always 0 in SWM (`swm.h` `swm_waveitem`
comment "always zero!").

---

## 6. Embedded reference tables (from `player.asm`, transcribed in `swm.h:272-319`)

The note→pitch and modulation math use these tables (SID-Wizard 1.2 values).
**Important for extraction:** a pattern note `$01..$5F` indexes
`FREQTBL`/`FREQTBH` (after adding the instrument's octave_shift, byte $09);
`EXPTABH` is the exponential table used for slides/vibrato/filter-keyboard-track.

```
FREQTBH_POS = 11    ; freq.table starts at index 11 inside SWexpTabH[]
FREQTB_SIZE = 96    ; 8 octaves × 12
EXPTRESHOLD = 107   ; = FREQTB_SIZE + FREQTBH_POS
```
`SWexpTabH[]`/`SWexpTabL[]` (the combined exp+freq table) and
`SWvibFreq[]` (GT→SW vibrato-frequency map `{2,4,5,6,7,8,9,B,C,D,E,F,F,F,F,F}`)
are reproduced verbatim in `swm.h:272-319`. Vibrato amplitude is computed like a
slide but with the **input value halved**.

`DEFAULTHRADSR` (player.asm:1061) = `$0FF0` (AD `$0F`, SR `$F0`) — the fallback
hard-restart ADSR for drivers without per-instrument HR-ADSR.

---

## 7. Chord & tempo tables

- **Chord table** (`SWM-spec.src:98`, `swm.h:240`): chords concatenated, each
  ended by `$7E` or `$7F`; bytes are relative pitch-shifts. e.g.
  `0,3,7,$7E, 0,4,7,$0A,$7F`. Size in header $0F. `MAXCHORDAMOUNT=64`,
  `maxchordlength=32`, `ChordTableLen=256`. Chord 0 doesn't exist (default ≥ 1).
- **Tempo table** (`SWM-spec.src:101`, `swm.h:253`): tempo-programs separated by
  a byte with **bit7 set** (the program's last value). e.g. `08,07,06,$85,
  20,20,10,$90`. Size in header $10. `MAXTEMPOPRAMOUNT=64`, `maxtempolength=32`,
  `TempoTableLen=128`. Tempo-program 0 is absent by convention (exporter
  compensates with a `-1`, `github_exporter_layout.md` §5). The player compares
  `SPDCNT` to a tempo byte; bit7 = single-tempo (write-model §6).
- **Subtune funktempos** (`SWM-spec.src:104`): one `(tempo1,tempo2)` pair per
  subtune; alternated row-by-row (funk tempo). If `tempo1 >= $80` it's a single
  tempo. One pair always present even without a sequence.

---

## 8. SID-count variants (`settings.cfg:36-40`, build-time)

`SID_AMOUNT` (1/2/3/4) is a **compile-time** build of the whole app/player, not a
per-tune SWM flag:
```
SIDBASE         = $D400
defaultSID2BASE = $D420   (2SID)
defaultSID3BASE = $D440   (3SID)
CHN_AMOUNT      = 3 * SID_AMOUNT
PALmaxframespeed= 8 (1SID) / 4 (2SID) / 3 (3SID)
```
Multi-SID builds **always** use ghost registers (`ALLGHOSTREGS`, settings.cfg:245)
and PSID header version 3 with per-chip model nibbles + `SID2sidAdd`/`SID3sidAdd`
at header +7A (`github_exporter_layout.md` §2). The SWM header reserves bytes
$15-$17 for future 2SID mute/solo. For 2/3/4-SID tunes, the orderlist has
`3*SID_AMOUNT` tracks (e.g. 6 sequences per subtune for 2SID).

---

## 9. Cross-references
- Export binary layout / pointer tables / PSID header: `github_exporter_layout.md`
- Per-frame write order / ghost flush / HR / multispeed: `github_player_writemodel.md`
- The C parser/converter `SWMconvert.c` (SWM↔XM/MIDI) corroborates every field
  here and is a working reference implementation of the SWM byte reader.
