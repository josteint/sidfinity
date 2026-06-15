---
source_url: https://www.vgmpf.com/Wiki/index.php?title=Ariston + https://github.com/cadaver/sidid/blob/master/sidid.nfo + https://csdb.dk/release/?id=29914 + https://csdb.dk/release/?id=119920 + local HVSC docs
fetched_via: WebFetch + local read
fetch_date: 2026-06-15
author: VGMPF community, CSDb community, sidid (cadaver)
content_date: varies (VGMPF retrieved 2026-06-15; CSDb entries from 1988 era)
reliability: secondary (secondary sources; no primary source code or disassembly)
---

# Ariston Music Driver — Engine Overview

## Origins and authorship

- **Creator:** Ian W. Crabtree (UK), 1987, in 6502 assembly.
- **GUI editor:** Philip Brabbin wrote "the official editor." Most professional composers
  bypassed it and arranged directly in 6502 assembly source.
- **Collaborator:** Wally Beben contributed enhancements and is co-credited as a version author.
- **Driver name origin:** Almost certainly named after the Ariston appliance company whose UK
  TV commercial used the slogan "Ariston...and on...and on and on and Ariston" (confirmed by
  STIL note on Dunn/RoboCop).

## Version lineage (from sidid signatures + VGMPF)

Four distinct code fingerprints are tracked by SIDId:

1. **Ariston** (primary) — the shared base code; 8-byte instrument program copy loop; gate-via-ROR.
2. **Ian_Crabtree_V1** — earliest variant; JSR-based voice dispatch; single SID write per update.
3. **Ian_Crabtree_V2** — adds proper ADSR ($D405/$D406) + double gate-off/gate-on ($D404×2).
4. **Wally_Beben** — adds pulse-width writes ($D402/$D403), note-range gate (CMP #8), 3× $D404
   toggle, per-note DEC timer. This is the "phasing effect" variant.

The sidid.cfg parenthesised naming means V1/V2/Beben are secondary sub-fingerprints of the
primary Ariston match — they refine, not replace, the primary ID.

## Technical characteristics (DERIVED from sidid analysis + VGMPF)

**Tuning:** 424 Hz or 434 Hz (multiple tuned variants exist; VGMPF + Ian Crabtree VGMPF page
states 433.5 Hz PAL / 450 Hz NTSC "sound the same on every SID chip").

**Platform dispatch:** Standard PSID VBI (50 Hz PAL) for 144/147 SIDs. Three Steve Barrett
(Eggman) SIDs use CIA-based timing (speed bit 0x2 = voice 2 CIA). Engine is not inherently
multispeed — the CIA variants are Barrett-specific modifications.

**SID register write model (DERIVED — unconfirmed without disassembly):**
- Voice update loop iterates over 3 voices (X down from 2 or 3, BPL/BNE loop).
- Instrument "program step": 8-byte table copy from instrument data to a working buffer,
  gated by a ROR-based tick/frame counter (not every call runs the copy — suggests sub-rate
  instrument steps).
- Per-voice SID writes: $D402/$D403 (PW), $D404 (control/gate), $D405 (AD), $D406 (SR).
- Write ORDER within a voice (Beben variant, DERIVED):
  PW_lo → PW_hi → gate-off → gate-on → [third $D404 toggle for drums?]
- Filter ($D417, $D418) writes: present but not shown in primary signature region.
  The `LDA #$FF` at end of primary signature may relate to filter/volume reset.
- Frequency writes ($D400/$D401): not visible in fingerprint region — may be written
  separately before or after the shown sequence.

**Instrument format (DERIVED):**
- 8-byte instrument rows (from the E0 08 / loop).
- Likely fields: waveform control, AD, SR, PW lo, PW hi, effect type, effect param, ???
- OPEN: byte count matches common C64 driver instrument rows (e.g. ADSR=4, PW=2, ctrl=1, note=1).

**Phasing effect:** Beben's pulse-width writes per note, combined with the 3× $D404 toggle,
create the characteristic "phasing" — rapid waveform/PW modulation per note that was distinctive
enough for Maniacs of Noise to ask about it. After Beben sent source, MoN added enhanced drums
and sent it back (drums = the third $D404 toggle path behind CMP #$08 gate).

**Relocation:** Heavily relocated engine. No fixed load address — see corpus census for full
scatter. The Brabbin GUI editor defaulted to low memory (~$0832/$0856); professional usage
varied from $0800 to $FF00.

**Platform ports:** Ported to Atari ST and Amiga in 1988 by Wally Beben with "Chris from Bury
St Edmunds, Suffolk" (game programmer). These are separate implementations, not C64 SIDs.

**Source availability:** Not public. The only known distributions are:
- Cracked Ariston Music Editor disk images (CSDb #29914 / #119920), credited to "Criminals in
  Computers" and "Illusion" groups (June 1988). These are the editor + player, not source.
- Private source shared between Crabtree, Beben, and Maniacs of Noise (the "phasing" exchange).

## Scene group: Ariston Design

A C64 scene group named "Ariston Design" (Denis Harris / Moley, Neil Scales / Neil) used the
Ariston driver. Their 12 SIDs cluster at init=$0x856/$0x853 — the Brabbin editor default layout.
They are musically minor contributors but confirm the driver's availability to scene composers.

## CSDb resources

- https://csdb.dk/release/?id=29914 — Ariston Music Editor (Criminals in Computers + Illusion, 24 June 1988). D64 disk image; 920 downloads.
- https://csdb.dk/release/?id=119920 — Ariston Music Editor (Criminals in Computers, 1988). D64 disk image; 245 downloads. "An improved version of the player/editor by Ian Crabtree."

Both are cracked versions; no source code on CSDb.

## Corpus summary

147 SIDs / engine='Ariston' in HVSC #84.
All psid_version=2. Predominantly 1-subtune SIDs; multi-subtune mostly Barrett/Wilson/Beben.
Subtune counts range from 1 to 48 (Wilson_Mixer.sid).
