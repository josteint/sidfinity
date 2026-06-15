---
source_url: https://web.archive.org/web/20010610182700/http://www.inf.bme.hu/~zed/tracker/faq.html
fetched_via: wayback 2026-06-15
fetch_date: 2026-06-15
author: Zed (Zoltán Konyha)
content_date: 2001-03-21
reliability: primary
---

# OdinTracker FAQ (Last updated 21 March 2001)

Archived from http://www.inf.bme.hu/~zed/tracker/faq.html

---

**Q1: What is Odin Tracker?**
A1: Odin Tracker is a music editor for the C64 featuring easy-to-edit MOD-like song structure.
The interface is designed to be user-friendly and powerful and resembles that of PC Fast Tracker.

**Q2: How do I run the tracker?**
A2: Using a C64 emulator, or on a real C64.

**Q3: What emulator should I use?**
A3: CCS64 (Windows/MS-DOS) or VICE (Windows/Linux/MS-DOS).

**Q4: How do I transfer the program to a real C64?**
A4: Use a cable connecting the PC printer port and the 1541 floppy drive, then Star Commander
to transfer data from PC to 1541.

**Q5: How do I play songs outside the tracker? How do I create SIDs?**
A5: Use the Dat2Sid utility:
1. Download Dat2Sid.
2. Pack and save the song from the diskmenu (single file, not split).
3. Run Dat2Sid. Load packed song via "Load DAT" (supports .D64 disk images).
4. Enter song title, composer and copyright info.
5. Click "Save SID".

**Q6: Where is the digi channel?**
A6: Missing. Current workaround: use a utility that mixes digi onto SID songs
(like Padua's Digi Organizer).

**Q7: Why do I get no sound in my emulator?**
A7: Check emulator sound configuration and ensure sound card is not allocated by
another application. CCS64 (July 2000 release) had known sound problems; try
selecting the DirectSound driver.

**Q8: I can't load the demo songs in my emulator. What shall I do?**
A8: Create a disk image and copy the songs and tracker into it; use Star Commander.

**Q9: I downloaded some songs and they sound like crap. What's wrong?**
A9: Possible download corruption. Internet Explorer may do a text download of .PRG files.
Try right-clicking and "Save Target As..." or download the Zipped disk images instead.

**Q10: How do I change octaves?**
A10: The help says CTRL+1..7, but in emulators CTRL is mapped to TAB. In emulators
use TAB+1..7.

---

## Notes for USF Research

- The FAQ confirms the player routine API: pack song from disk menu → Dat2Sid converts to .SID.
- The Dat2Sid tool wraps an OdinTracker packed song + the relocatable player into a PSID file.
- No digi channel in OdinTracker (relevant: OdinTracker SIDs in HVSC use only the standard
  3 SID voices).
- Song format is the C64 memory image from $4000 to the end of the last used track.
