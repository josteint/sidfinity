---
source_url: multiple (synthesised from CSDb, sidid.nfo, Remix64 interview, SID Preservation, Demozoo, VGMPF)
fetched_via: WebFetch / WebSearch
fetch_date: 2026-06-13
author/handle: various
content_date: 1988–2026
reliability: secondary (synthesis); individual facts sourced per entry
---

# SoedeSoft vs. Soundmaster — Naming, Versioning, and Succession

## The naming situation

Three names for one software lineage:

| Name | Who used it | Context |
|------|------------|---------|
| SoedeSound Editor V1.0 | Soedesoft CSDb entry #117095 | 1988 copyright, earliest name found on screen |
| Soundmaster V1.0 | Fire-Eagle CSDb entry #10735 | Name used on disk release, Feb 1989 |
| Sound Editor from FE | CSDb alt-name for #10735 | Fire-Eagle in-scene abbreviation |

CSDb user Fred (24 Mar 2013) confirmed: "This release uses the exact same player/editor as Soundmaster V1.0 but is released under a different name." — CSDb #117095 vs #10735.

sidid.nfo annotation: "The editor is also known as Soundmaster or SoedeSound Editor."

**Conclusion:** "SoedeSoft" is the group/company name; "SoedeSound Editor" is the product name in its earliest form; "Soundmaster" is the trade name used for public scene distribution. They are the same software. The distinction may be: "SoedeSound Editor" was the name on the program's title screen or docs; "Soundmaster" was the disk label / scene name.

## Version numbering (reconstructed timeline)

| Version | Date (on-screen) | Public? | Distributor | CSDb ID |
|---------|-----------------|---------|-------------|---------|
| SoedeSound Editor V1.0 | 1988 | Yes (limited?) | Soedesoft | #117095 |
| Soundmaster V1.0 | (1989 release) | Yes | Fire-Eagle, later Rage for Order | #10735, #180209 |
| Soundmaster V3.2 | 1988 (on screen) | No — internal only | Fire-Eagle members only | #117086 |
| Soundmaster V3.1 | 1989 | Yes — wide public | Magic Disk 64 | #90307 |
| SoedeSound Editor V1.1 | 1992? | Scene | Unknown distributor | (no dedicated CSDb page found) |

**Key insight from Fred's CSDb comment:**
> "Although this version [V3.2] has 1988 on screen, Soundmaster V3.1 is released in 1989 by Magic Disk 64."

So V3.2 > V3.1 in development order, but V3.1 is the public release. The numbering suggests V3.2 was the live development branch ("next version in progress") while V3.1 was branched off and published. Standard scene practice: the internal copy carries a higher version number.

**The jump from V1.0 to V3.x** is unexplained in public sources. No V2.x entries exist in CSDb. Possible explanations:
- V2.x was never formally released, or internal-only versions exist between V1.0 and V3.x
- The version numbering was not sequential (perhaps months/build numbers)
- V1.0 (as the public name) is actually V3.x internally, with "V1.0" being the public edition number

OPEN: Was there a V2.x? What changed between V1.0 and V3.1?

## "Soede Editor" successor

SID Preservation (Xiny6581, sidpreservation.6581.org):
> "The next step and successor to 'Sound Master', was 'Soede Editor'. The GUI was bigger and it added more possibilities to the Bar Editor, as well for the Sound Design. [...] it was possible to define Bars to be longer and not locked to 4/4 per Bar."

sidid.nfo lists a variant "Soede Editor TURBO GTI SSS" — a hacked/improved community version consistent with:
> "Many big groups wanted to make their own special versions and it was very often done by 'hacking' or 'improve' the official versions." (Xiny6581)

No CSDb entry found for "Soede Editor" or "Soede Editor TURBO GTI SSS" during this session. RE-OPEN.

## Demozoo S.F.X. Editor (1989)

Demozoo (https://demozoo.org/groups/7598/) lists *S.F.X. Editor* (1989) as a Soedesoft tool. This is not "Soundmaster" per the naming conventions but may be a companion SFX/sound-effect authoring tool used alongside Soundmaster for non-musical sound effects. Or it could be an alias for Soundmaster at a different stage. OPEN — needs CSDb lookup to confirm.

## SoedeSound Editor V1.1 (1992)

Listed in Michiel Soede's CSDb scener profile (#6063) with Music credit. A decade-later minor update to the editor. No release page found. Its player routine may or may not differ from V3.1. If the player routine did not change, it would still be identified as "Soundmaster" by sidid. OPEN.

## The Amiga successor: SoundMaster II / SoundMaster Professional

Michiel Soede (Remix64 interview):
> "I also made music on the Amiga, again using our own music routine – called SoundMaster II, which was based on our C64 routine."

VGMPF Wiki: "For Amiga development, the brothers used 'their own driver and editor called SoundMaster Professional' along with a Kawai K4 synthesizer."

So C64 Soundmaster → Amiga SoundMaster II → Amiga SoundMaster Professional. This lineage is relevant for understanding the C64 design since the Amiga port preserved the structure. Outside scope for SIDfinity (Amiga is not the target), but confirms the C64 routine was architecturally sound enough to port.

## SIDmaster Rack Extension (modern)

SoedeSoft released a Reason Rack Extension plugin called "SIDmaster" which:
> "implements effects used in the old days of the C64 based on SoedeSoft's original music routine of the 80's, such as arpeggios, wave patterns, modulating the pulse width or filter."
(Reason Studios product page, https://www.reasonstudios.com/shop/rack-extension/soedesoft-sidmaster/)

This confirms the canonical effect list from SoedeSoft themselves: **arpeggios, wave patterns (waveform cycling), pulse width modulation, filter modulation.** The SIDmaster plugin architecture exposes:
- Per-voice: ADSR, waveform selection (tri/saw/pulse/noise/combos)
- Arpeggiator (per-voice, different per voice)
- Waveform effects (alternates waveforms/frequencies sequentially)
- Ring modulation and hard sync (inter-voice)
- Pulse width modulation (LFO or controller)
- Filter: cutoff, resonance, LP/HP/BP/notch, LFO modulation

The plugin is not a literal translation of the 6502 player's data format, but its feature set maps directly to what the C64 routine supported.
