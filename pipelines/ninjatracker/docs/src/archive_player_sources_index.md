---
source_url: https://cadaver.github.io/tools/ninjatr204.zip, https://cadaver.github.io/tools/ninjatrk.zip
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops)
content_date: V1.1=2004-01-25, V2.04=2013-06-19
reliability: primary
---

# NinjaTracker — Player Source Files Index

All files in this directory were extracted from official Covert Bitops release archives.

## NinjaTracker V2.04 (ninjatr204.zip)

Source: https://cadaver.github.io/tools/ninjatr204.zip (downloaded 2026-06-17)

### archive_nt2play_v204.s
The V2 GAMEMUSIC PLAYROUTINE in DASM format. This is the canonical machine-readable
format specification for NinjaTracker V2. Key contents:

**ZP requirement**: 2 consecutive addresses (`nt_zpbase = $fc` default, configurable)

**Entry points**:
- `nt_newmusic`: relocate internal pointers after loading new music data
  Parameters: A = musicdata address lo, X = musicdata address hi
- `nt_playsong`: start playing a subtune
  Parameters: A = tune number (0-15)
- `nt_playsfx`: start a sound effect on a channel (priority: higher address wins)
  Parameters: A = SFX lo, X = SFX hi, Y = channel index (0, 7, 14)
- `nt_music`: play one frame (call from IRQ)

**Data header layout** (musicdata+N):
- The `NT_NUMFIXUPS = 21` fixup table remaps 21 absolute addresses in the player
  code at load time (not relocation — the player uses direct `lda $NNNN,y` mode)
- `NT_HEADERLENGTH = 6` bytes precede the section size table

**Fixup type constants** (NT_ADDZERO=0x80, NT_ADDWAVE=0x00, NT_ADDPULSE=0x04,
NT_ADDFILT=0x08, NT_ADDCMD=0x0c, NT_ADDLEGATOCMD=0x10, NT_ADDPATT=0x14) define
which data section each fixup pointer points into.

**Hard restart parameters**:
- `NT_HRPARAM = $00` (music HR: S/R = $00)
- `NT_FIRSTWAVE = $09` (waveform on first init frame)
- `NT_SFXHRPARAM = $00` (SFX hard restart param)
- `NT_SFXFIRSTWAVE = $09`

**Per-channel state** (stride 7 between channels, channels at offsets 0, 7, 14):
```
nt_chnpattpos   — current position within pattern
nt_chncounter   — frame counter
nt_chnnewnote   — pending note (or $ff = no new note)
nt_chnwavepos   — wavetable position
nt_chnpulsepos  — pulsetable position
nt_chnwave      — current waveform byte
nt_chnpulse     — current pulse value (lobyte, stored to both $D402/$D403)
... (+7 bytes gap) ...
nt_chngate      — gate mask ($fe = off, $ff = on)
nt_chntrans     — transpose
nt_chncmd       — current command (1-indexed into command table)
nt_chnsongpos   — position in song/track order
nt_chnpattnum   — current pattern index
nt_chnduration  — note duration
nt_chnnote      — note number (doubled — freq table is indexed by note*2)
... (+7 bytes gap) ...
nt_chnfreqlo    — current frequency lo
nt_chnfreqhi    — current frequency hi
nt_chnwavetime  — wavetable timer / vibrato direction
nt_chnpulsetime — pulse timer
nt_chnsfx       — SFX state (0=no sfx, 1=init, 2=HR frame, 3+=playing)
nt_chnsfxlo     — SFX data pointer lo
nt_chnsfxhi / nt_chnwaveold — SFX data pointer hi (shares with wave-old for slide)
```

**Global state**:
```
nt_filtpos+1    — filter table position (0 = no filter)
nt_filttime     — filter timer
```

**Sound effect data format** (V2):
```
Byte 0:   Sustain/Release
Byte 1:   Attack/Decay
Byte 2:   Pulsewidth (nybbles reversed — pulse $400 = $04)
Byte 3+:  Note,Wave pairs — note $8C-$DF (C-1 to B-7), wave $01-$81
          (wave can be omitted if unchanged)
Byte N:   $00 = end
```

**Frequency table**: 84 entries (C-1 to B-7 + guard entry $FFFF),
starting at `nt_freqtbl`, accessed as `nt_freqtbl-24,y` (note*2 offset -24).

### archive_v204_readme.txt
The full V2.04 readme.txt (Cadaver, 2013). 273 lines. Includes:
- Complete format specification
- Version history V2.0 through V2.04
- Packing/relocation interface
- Table encoding details

---

## NinjaTracker V1.1 (ninjatrk.zip)

Source: https://cadaver.github.io/tools/ninjatrk.zip (downloaded 2026-06-17)

### archive_ntplay_v11.s
The V1 GAMEMUSIC PLAYROUTINE (DASM format). Key differences from V2:

**ZP requirement**: 5 consecutive addresses (`musiczpbase = $fb` default)

**Entry points**:
- `relocatemusic`: relocate after loading. A,X = musicdata address
- `playtune`: start song. A = song number (0, 1, 2 ...)
- `playsfx`: play SFX. A,X = effect address; Y = channel index (0, 7, 14)
- `music`: play one frame

**Data header layout** (V1 musicdata+N):
- musicdata+0: songtable len (halved)
- musicdata+1: patttable len (halved)
- musicdata+2: wavetable len
- musicdata+3: pulsetable len
- musicdata+4: filttable len
- musicdata+5+: actual data sections

The V1 relocation system (`relocatemusic`) patches absolute load-time addresses
into the player — 23 fixup entries in `reladrtbllo/hi` + `reladdtbl`. Section
layout determines which fixup type applies.

**V1 wavetable format** (3-column):
Left column (`vwavetbl`):
- $00 = hardrestart note init
- $01 = legato note init
- $02 = set ADSR (2nd frame of init)
- $03-$8F = waveform + note change
- $90 = note without waveform change
- $91-$FF = pitch slide (duration as negative value)

Middle column (`vnotetbl`): note / slide speed / parameters
Right column (`vnexttbl`): pointer to next step

**V1 pattern format** (3-column, called "sectors"):
- Column 1: note OR command (Wave, AD, SR, Flt) — encoded as byte
- Column 2: wavetable pointer or command parameter
- Column 3: duration

**V1 track data encoding** (REVERSED from V2!):
- 00: loop
- 01-7F: sector to play
- **80-BF: transpose UPWARDS** (V1 = up; V2 = down)
- **C0-FF: transpose DOWNWARDS** (V1 = down; V2 = up)

**V1 filter table**: first entry is applied at song start (init step).
Resonance hardcoded to $F.

**V1 SFX data format**:
```
Byte 0: Pulsewidth (nybbles reversed)
Byte 1: Attack/Decay
Byte 2: Sustain/Release
Byte 3+: Notes & waves ($8C-$DF = notes, $01-$81 = waveforms, $00 = end)
```

**V1 frequency table** (different values from V2 — different tuning!):
Uses `vfreqtbl` accessed as `vfreqtbl-26,y`.

### archive_v11_readme.txt
Full V1.1 readme.txt (Cadaver, 2004). 297 lines. Complete format spec.

### archive_v11_readgam.txt
V1 gamemusic variant documentation. 81 lines. Describes SFX format + playroutine
interface specifically for the gamemusic (no-player-in-data) mode.

---

## Key Format Differences: V1 vs V2

| Aspect | V1.x | V2.x |
|--------|------|------|
| Player name | ntplay.s | nt2play.s |
| ZP bytes needed | 5 | 2 |
| Pattern columns | 3 (note, wave ptr, duration) | 4 (note, cmd#, duration, cmd name) |
| Pattern name | "sector" | "pattern" |
| Table columns | 3 | 2 |
| Instruments | Wavetable programs | "Commands" (unified instrument+command) |
| ADSR storage | In wavetable (init steps 00/01/02) | In command data |
| Transpose encoding | 80-BF=up, C0-FF=down | 80-BF=down, C0-FF=up |
| Rastertime | 11 lines max | Slower than V1 (per Lasse); ~"bigger" |
| Hard restart | AD+SR = $00 | 2 frames + 1 silent frame (V2.02+) |
| Filter resonance | Hardcoded $F | Configurable per filter step |
| Slide | Duration-based (calculator tool) | Stops at target pitch automatically |
| SFX format | SR, AD, PW, notes (that order) | SR, AD, PW, notes (same order) |
| Frequency table | vfreqtbl-26,y | nt_freqtbl-24,y (different tuning) |
| Data relocation | relocatemusic (5-ZP, 23 fixups) | nt_newmusic (2-ZP, 21 fixups) |
| Init sector | Sector 0 reserved (cannot be in track) | N/A (commands handle init) |
