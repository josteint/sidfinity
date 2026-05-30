---
name: Hubbard root cause diagnosis
description: Hubbard pipeline: 32 A+S out of 95 RH-engine songs. Arpeggio freq table fixed.
type: project
---

**Hubbard pipeline: rh_decompile → rh_to_usf → usf_to_sid → compare**

Results (2026-04-22): 1S + 31A + 3B + 15C + 40F + 6FAIL out of 95 Rob_Hubbard songs.
(Previous session had 1S + 23A + 2B + 10C + 47F out of 83 songs.)

**Arpeggio freq table fix (this session, 2026-04-22):**

Root cause: instruments with `has_arpeggio=True` use `note_offset=12` in their wave
tables. For notes near note 88, adding 12 gives index 100 — past the end of the 96-entry
freq table. The packed binary had only 96 freq entries; index 100 read garbage, causing
note_wrong on every arpeggio frame.

Fix applied in `rh_to_usf.py`:
- After extracting the 96-entry Hubbard interleaved freq table, detect songs with
  arpeggio instruments and extend freq_lo/freq_hi to 108 entries (indices 0-107).
- Extension values are measured by running the original player in py65 for one play
  frame after INIT: reads the freq table memory at positions 96-107. These locations
  are player state variables (per-voice counters) that get incremented during play.
- Also fixed: load address computation when PSID header la==0 (use embedded la from
  payload, not the header field which is 0). This corrects hub_ft_base_addr.

Fix applied in `usf_to_sid.py`:
- When `freq_lo` is longer than 96 bytes, pass `last_note = len(freq_lo) - 1` to the
  packer so the extended entries are included in the packed binary.

**Result:** Commando.sid: F(60.0) → A(95.2). 13 additional A-grade songs.

**Key discovery about Hubbard arpeggio mechanism:**
- The "+12 arpeggio" does NOT play a musical octave up. It reads memory immediately
  after the 96-note freq table, which happens to be player per-voice state variables.
- These state variables get incremented via `INC abs,X` during play, producing values
  like 0x03, 0x05, 0x07... (very low frequencies = percussive buzzing effect).
- The V3 player wave table advances every FRAME (not every tick), correctly mirroring
  the original Hubbard arpeggio alternation rate. The wave table with note_offset=12
  correctly alternates every frame.
- The extended freq table captures the initial state (after 1 play frame), which is
  the most common value. Dynamic counter changes (0x03→0x05→0x07) cause some
  residual note_wrong on later arpeggio frames, but the dominant value is correct.

**Remaining F-grade contributors:**
- Nested speed counters: 28+ songs with outer DEC/BPL counters causing timing drift
- Dynamic arp state evolution: arp freq changes as counter evolves (0x03→0x05→0x07)
- Non-octave voice transpose: ~4 songs
- Multi-subtune: songs with >5 subtunes, possibly testing wrong one
- RSID play=0: 12 songs, timing less accurate

**Do NOT use regtrace_to_usf as a fallback.** Fix the decompiler/converter.
**Do NOT mix decompiled and trace-detected tempos.** Fix each variant independently.
