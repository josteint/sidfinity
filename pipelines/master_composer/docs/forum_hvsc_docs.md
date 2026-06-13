# Master Composer — HVSC bundled documentation

Provenance
- local: `hvsc84/DOCUMENTS/BUGlist.txt` and `hvsc84/DOCUMENTS/Update_Announcements/20231224.txt`
- fetched_via: local file read (grep + Read), read-only
- fetch_date: 2026-06-13
- author/handle: BUGlist maintained by iAN CooG <hvsc.crew (sid) gmail.com>; Update #80 announcement by the HVSC Crew
- content_date: BUGlist "Last Updated: June 15, 2025"; Update #80 dated December 24, 2023
- reliability: HIGH — primary HVSC project documentation, authoritative for the collection's own files

---

## 1. BUGlist.txt — Master Composer entries

There is **no `BUGlist` entry describing a "hum" / "decaying hum" playback bug** for the
Master Composer player itself in HVSC #84. The grep for "Master Composer" in BUGlist matches
**only a block of eight truncated rips** under `/DEMOS/UNKNOWN/Master_Composer/`. All eight share
the identical bug note and reporter:

```
/DEMOS/UNKNOWN/Master_Composer/Devoted_to_You.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/Every_Breath_You_Take.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/I_Want_You.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/Loving_Feeling.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/Only_You.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/Pink_Panther.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/Take_Me_Home.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)

/DEMOS/UNKNOWN/Master_Composer/We_Two.sid
    BUG: File seems truncated, lacks lots of data at end. No good source known.
(iAN CooG)
```

**Technical reading:** these are *data* bugs (the rip is missing trailing bytes), NOT engine
bugs. "Lacks lots of data at end" is consistent with the Master Composer format storing its
note/music data in a trailing region (see `research.md`: music data at `+$A80`); a short rip
truncates the page/block/bar tables or note stream and the tune runs off the end of valid data.
This is distinct from the "decaying hum after final page completes" engine behaviour described
in the background brief.

Note the canonical HVSC home of these eight tunes is `/DEMOS/UNKNOWN/Master_Composer/` — i.e.
the engine is folded into the "UNKNOWN" demos tree (composer not identified per-tune), not under
a `MUSICIANS/` author. This matters for any HVSC-DB engine-coverage query.

---

## 2. Update_Announcements — the hum / end-of-tune bug fix (Update #80)

`Update_Announcements/20231224.txt` is the **HVSC Update #80** announcement
(Date: December 24, 2023; resulting version 80, previous 79; ~58,150 SID files after update).

In the section documenting the **Prg2Sid 1.15** tool (the HVSC PSID-header/identification tool by
iAN CooG), the changelog records the Master Composer end-of-tune fix verbatim:

```
################
# Prg2Sid 1.15 #
################

Prg2Sid is a tool that attaches a PSID header to a ripped (prg) tune. It
identifies some players and sets init/play accordingly. It also patches
the header and code if needed.

Since 1.08 the following has been changed:

- Added optional parameters Subtunes and StartSong (suggested by Encore/Undone)
- MusicAssembler & MusicMixer init/play addresses now are checked at $1000/$1003
  and kept if the 2 JMPs are correct, else they are set in the sid header to
  the actual addresses
- Master Composer bug in the end of tune code fixed, thanks to Prof Chaos/HVSC
- new players identified:
  SidFactory II (v3)
  StarBars (v1.1/1.2/1.3/1.4)
- improved detections:
  SidFactory II (v1 & v2), more variants

Check out: https://csdb.dk/release/?id=235041
```

**Technical reading — this is the hum bug, and it lives in "the end of tune code":**
- The fix is described as being **in the end-of-tune code** of the Master Composer player. This
  strongly corroborates the background brief's "decaying hum after final page completes": after
  the last page, the player's end-of-tune handling leaves the SID in a non-silent state (e.g.
  fails to gate-off the voices / clear the control or volume registers), so the chip continues to
  emit a decaying tone — a hum.
- The fix is applied by **Prg2Sid 1.15** as a **code patch** ("It also patches the header and
  code if needed"). So in HVSC #80+, Master Composer rips are typically **patched** at the
  end-of-tune routine rather than carrying the original buggy player verbatim. **This is a direct
  implication for our pipeline:** the HVSC binaries we extract from may already contain a
  Prg2Sid-patched end-of-tune routine, not the pristine 1983/84 Access Software player. Compare a
  pre-#80 rip against a #80+ rip to recover the exact byte patch and the unpatched behaviour.
- Credit: the bug was diagnosed/fixed by **Prof Chaos/HVSC** (HVSC musician dir
  `MUSICIANS/P/Professor_Chaos/` exists), with the patch landed in Prg2Sid by iAN CooG.
- Prg2Sid release reference: https://csdb.dk/release/?id=235041 (CSDb).

**Action item for the migration:** obtain Prg2Sid 1.15 (or its source/changelog at CSDb release
235041) and a pre-#80 vs post-#80 Master Composer rip; diff the end-of-tune bytes to see exactly
what the patch writes (almost certainly a gate-off / register-clear inserted at the song-end
branch). That patch IS the documented hum-bug mechanism.
