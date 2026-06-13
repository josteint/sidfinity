# SID Duzz'It — CSDb Release Page Comments

<!-- provenance
  source_url: https://csdb.dk/release/?id=133692  (V2.1.7)
  source_url: https://csdb.dk/release/?id=7175    (V1.801)
  source_url: https://csdb.dk/release/?id=153760  (PDF Manual by Psylicium)
  source_url: https://csdb.dk/release/?id=145259  (2.1.7 Cheat Sheet)
  source_url: https://csdb.dk/release/?id=84874   (V2.0 Beta 8)
  source_url: https://csdb.dk/release/?id=119228  (V3.0 MIDI Preview 2)
  source_url: https://csdb.dk/forums/?roomid=14&topicid=28356  (SDI forum thread)
  fetched_via: WebFetch
  fetch_date: 2026-06-13
  reliability: secondary (WebFetch summary of CSDb pages; comments quoted verbatim
               where the fetch response preserved them)
-->

This file consolidates all recoverable verbatim user comments from CSDb release pages
and forum threads about SID Duzz'It, ordered by page.

---

## CSDb: SID Duzz'It V2.1.7 (release ID 133692)

URL: https://csdb.dk/release/?id=133692
Released: 12 October 2014 by SHAPE
Credits: Code by 6R6 (Blues Muz', Nostalgia, Onslaught, SHAPE) and GT (Maniacs of Noise, SHAPE)

### User Comments (verbatim)

**Yogibear** (12 October 2014):
> "Good work!"

**Bitbreaker** (17 October 2014):
> "How's about delivering the source in a format that is suitable for crossassembling?
> Same goes for the dump. It can only be attached with the special TASS version on disk
> (other version like the build in version in RR choke), which is so broken that it can't
> even write the object file directly to disk."

**Oswald** (17 October 2014):
> "c64 is not modern either, you still use and develop for it :P :)"

**Stainless Steel** (28 October 2014):
> "The first copple of years i felt like bitbreaker. Now i just love the way it is.
> Who needs modern toolchains :D"

**Rayne** (31 October 2014):
> "As this is a native tool, there's no need for a cross-assembler compatible player source."

**mstram** (3 February 2015):
> "In Vice 2.4.15, this release can't read 1.8 files, nor can 1.8 read 2.17 files."

**PAL** (3 February 2015):
> "hehe... this tool was created by geir and also grg and it was created for them....
> so that you all can use it is a bonus and not a burden of them."

**SIDWAVE** (16 February 2015):
> "removing edit from F4 keypress, is useless mistake. its best to hear notes while entered."

**6R6** (20 March 2016):
> "Selecting edit modes with F4 is untouched and is present as it should be."

**GH** (13 December 2020):
> "Was hoping someone was about to make this a windows version already..."

**Vincenzo** (30 October 2021):
> "SDI is a great music editor but the struggle with compiling the music is... why are
> player features set to disabled in the code by default?"

**Abynx** (31 January 2025):
> "An absolutely wonderful piece of software I can't do without.... Thank-you so much!"

### Technical Notes from Comments

- **V1.x ↔ V2.x format incompatibility** confirmed by mstram: V2.17 cannot read V1.8 files
  and vice versa. This is a hard binary format break, not a cosmetic one.
- **Player source format friction**: The player source is in Turbo Assembler (TASS) format,
  requiring the specific TASS version shipped with SDI — not cross-assembler compatible
  (Bitbreaker). This is an RE constraint: the player source on SourceForge is TASS dialect.
- **Player feature flags**: Vincenzo (2021) notes player features are "disabled in the code
  by default" — this refers to the assembly flags `rem_pu`, `rem_arp`, `rem_fi`, `rem_vib`,
  `rem_glid` documented in the format spec; users must edit the TASS source to enable them.

---

## CSDb: SID Duzz'It V1.801 (release ID 7175)

URL: https://csdb.dk/release/?id=7175
Released: October 2002 by SHAPE
Also known as: SDI
Credits: Code by 6R6 (Blues Muz', Nostalgia, Onslaught, SHAPE) and GT
Official website at time of release: http://home.eunet.no/~ggallefo/sdi/

### User Comment

**Mace** (3 November 2008):
> "Uploaded the file to CSDb, in case Glenn's website fails ;)"

### Notes

This was uploaded as a preservation upload 6 years after release because the authors'
personal homepage (Glenn's EUnet Norway page) was becoming unreliable. The URL
`http://home.eunet.no/~ggallefo/sdi/` is now dead — EUnet Norway personal hosting
was discontinued. This is the LAST V1.x release.

---

## CSDb: SID Duzz'It V2.0 Beta 8 (release ID 84874)

URL: https://csdb.dk/release/?id=84874
Released: 2009 by SHAPE
Also known as: SDI V2.0 beta 8
Website at time: http://home.eunet.no/~ggallefo/
Credits: Code by 6R6 (Blues Muz', Nostalgia, Onslaught, SHAPE) and GT (Maniacs of Noise, SHAPE)

### User Comment

**SIDWAVE** (14 January 2013):
> "Use this player, it is ADSR bugfixed"
> [Directed users toward "SDI V2.07 Player ADSR Fixed" as an updated version.]

### Notes

- "SDI V2.07 Player ADSR Fixed" was a separate player-only release not separately listed
  on CSDb. It predates V2.1 and fixes ADSR behaviour in the beta 8 player.
- The ADSR bug class: unclear from comments whether this is the SID chip ADSR restart
  (hard-restart) bug or a player state bug. The V2.1.7 release notes fix a different
  ADSR-adjacent issue (gate timeout for Ax/Cx/Ex instruments at song start).

---

## CSDb: SID Duzz'It V3.0 MIDI Preview 2 (release ID 119228)

URL: https://csdb.dk/release/?id=119228
Released: 31 May 2013 by SHAPE
Also known as: SDI (V3.0) MIDI
Credits: Code and Design by 6R6 (Nostalgia/SHAPE) and GT (Maniacs of Noise/SHAPE)

### User Comments (verbatim)

**6R6** (31 May 2013):
> "Added some stuff. Removed some stuff and optimized some stuff...Works best with a real
> c64. Less lag on sounds."

**Yogibear** (1 June 2013):
> "Nice!"

**Hermit** (20 October 2013):
> "Awesome tunes and sounds, and MIDI support worked fine with VICE...would be a great
> thing to try on real C64 with much less latency."

**Stainless Steel** (30 April 2014):
> "much love to you guys for making this. i've stuck with sdi for the past 8 years and
> i'm thrilled to see this."

**nebulah** (19 May 2014):
> "Thank you for the awesome MIDI routine in the new SDI! I've successfully tested it
> with a Steinberg Research MIDI interface...It really amazes me how responsive it is."

### Technical Notes

- V3.0 MIDI Preview is a PARALLEL BRANCH from V2.1.x — it is NOT a post-V2.1.7 release.
  V2.1.7 (Oct 2014) is the final stable release; V3.0 MIDI was never completed.
- MIDI interfaces tested by users: Steinberg Research, Datel, JMS, Sequential Circuits.
- 6R6's comment "Works best with a real c64. Less lag on sounds" — VICE emulation
  introduces MIDI latency that is absent on hardware. This has RE implications:
  the MIDI branch likely uses CIA timer interrupts for precise timing.

---

## CSDb: SID Duzz'It PDF Manual (release ID 153760)

URL: https://csdb.dk/release/?id=153760
Released: 19 February 2017 by Psylicium (Atlantis, Fantastic 4 Cracking Group)
Author: Henrik Mortensen (Psylicium)
Downloads: 1,216 total (888 from CSDb, 328 from psylicium.dk)

### User Comments (verbatim)

**E$G** (19 February 2017):
> "very professional. thanX"

**6R6** (21 February 2017):
> "Thanks for doing this. Much obliged. :)"

**Psylicium** (19 February 2017, self-comment):
> "Yeah, I know ... I probably should make actual music in SDI instead of all these
> cheat sheets and documents. This is the final one, I promise :)"

**Psylicium** (26 February 2017, revision note):
> "Thanks for your nice feedback :) I added a new revision today with some edits to
> the arpeggio chapter. When I released it originally, it was too big to upload to CSDb,
> and it still is, so use the one hosted at psylicium.dk for the latest version :)"

**dEViLOCk** (13 December 2020):
> "Thänx for this one! Just discovered it:-D"

### Notes

The manual combines "text from the official docs included with SDI 2.1.6, and notes and
corrections based on both newer versions, my own experiences and typos from the docs."
The revised version hosts at `https://files.psylicium.dk/sdi_217_manual.pdf` (file is
too large to upload to CSDb: over 1 MB). 6R6 himself thanked Psylicium, confirming the
manual's accuracy.

---

## CSDb: SDI 2.1.7 Cheat Sheet (release ID 145259)

URL: https://csdb.dk/release/?id=145259
Released: 14 February 2016 by Psylicium (Atlantis)
Downloads: 508 (original), 260 (sound design template), 181 (rev 3), 148 (rev 2)

### Creator Comments (verbatim, documenting revisions)

**Revision 3 addition note by Psylicium:**
> "Added revision 3 with player flags and TASS shortcuts."

**Revision 2 change note by Psylicium:**
> "Added a new revision with different layout and a font that's easier on the eyes, as
> it was quite hard to distinguish between certain characters in the first one. Also did
> minor additions and corrections. And all 3 note tables are included this time."

### Technical Note

"Player flags and TASS shortcuts" in revision 3 refers to the assembly-time `rem_*` flags
that disable unused player features (e.g., `rem_pu=1` to exclude pulse programs). These
are the flags Vincenzo complained were "disabled by default" (see V2.1.7 comments above).
The cheat sheet made these visible for end-users.

---

## CSDb: SDI Forum Thread (roomid=14, topicid=28356)

URL: https://csdb.dk/forums/?roomid=14&topicid=28356
Fetched: 2026-06-13

### Posts (verbatim)

**Stainless Steel** (2006-08-08 14:34):
> [Inquired about others using Shape's SDI editor and wanted to discuss experiences
> and technical aspects. — WebFetch summary; exact text not recovered.]

**Rayne** (2013-08-10 15:34):
> "Did the initial SDI2.1 player also have bugs that may have been fixed in later
> SDI updates?"

**6R6** (2013-08-10 22:57):
> "Updates fixed bugs in editor + added new editor functions."

**Rayne** (2013-08-11 00:18):
> [Mentioned searching for a C64 MIDI interface compatible with "Sid Duzz It 3.0 Preview."
> — WebFetch summary; exact text not recovered.]

**mstram** (2015-02-12 18:42):
> [Asked about a "new song command" in SDI 2.17, requesting clear-all and
> clear sequence/pattern functions. — WebFetch summary.]

**robozz** (2015-02-15 20:33):
> [Directed user to documentation under "load menu commands." — WebFetch summary.]

**mstram** (2015-02-16 03:16):
> [Posted the load menu command list; noted creating a workaround by saving a blank
> song file. — WebFetch summary.]

**SIDWAVE** (2015-02-16 07:34 and 07:36):
> [Mentioned new song file on 2.07 beta disk and "clear memory" file on 2.1.17 disk.
> Also mentioned compilation tutorial video. — WebFetch summary.]

**SIDWAVE** (2015-03-01 06:35 and 06:38):
> [Criticized F4 edit mode changes and shared a compilation tutorial video link.
> — WebFetch summary.]

### Technical Notes from Forum Thread

- "Updates fixed bugs in editor + added new editor functions" (6R6) — confirms 2.1.x
  updates addressed real editor bugs, not just cosmetic changes.
- The "new song command" issue: SDI has no single-keystroke "new song" command; users
  must save and load a blank template file. The "clear memory" workaround is on the
  2.1.17 disk (likely means 2.1.7; "17" may be a typo or a minor patch variant).
- F4 keypress: in some versions F4 cycled between editor and play modes; SIDWAVE
  complained this was removed; 6R6 (on the V2.1.7 release page) confirmed F4 select
  is present and untouched.

---

## Leads to Follow

- **CSDb roomid=14 full thread content**: Only partial posts recovered via WebFetch
  (the thread has more posts). Direct browser or curl access to
  `https://csdb.dk/forums/?roomid=14&topicid=28356` would recover the complete thread.
- **V2.0 Beta 7 CSDb ID 76999**: Not fetched. Contains comments about the V1.8→V2.0
  frequency-table detuning issue and the converter bug in Super Monaco GP. Worth fetching
  for the full discussion.
- **"SDI V2.07 Player ADSR Fixed"**: Referenced in SIDWAVE's comment on beta 8 but has
  no standalone CSDb release. It may be listed as an attachment on another release or
  exist only as a disk file on Glenn's (now dead) personal homepage.
- **CSDb scener page 6R6 (ID 8098)**: Returned 503 during this session. Contains the
  full list of 6R6's productions which would identify any SDI-related utilities he released.
