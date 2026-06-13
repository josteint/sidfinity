# Master Composer — community history & usage (Lemon64 + CSDb)

Provenance
- source_urls:
  - https://csdb.dk/release/?id=31047 (Master Composer crack, International Cracking Group, 1985)
  - https://csdb.dk/release/?id=215363 (Master Composer crack, Eagle Soft Incorporated, 1985)
  - Lemon64 thread leads (NOT yet fetched — see note): t=55611, t=67248, t=82190, t=50178
- fetched_via: WebFetch (CSDb pages) + WebSearch (Lemon64 thread discovery)
- fetch_date: 2026-06-13
- author/handle: CSDb commenters (Fred, Paladin) per below; Lemon64 posters not yet captured
- content_date: CSDb releases dated 1985; CSDb comments dated 2014 / 2022
- reliability: MEDIUM — CSDb release pages + user comments are anecdotal community memory, useful
  for history/usage/context, NOT for byte-level engine facts (use `forum_sidid_fingerprints.md`
  + `forum_hvsc_docs.md` for those).

---

## CSDb release pages — distribution history + one concrete internals fact

### Release #31047 — "Master Composer", crack by International Cracking Group (1985)
- Release type: **C64 Crack**, year **1985**, releasing group **International Cracking Group**.
  (Original author/publisher not stated on the page; commenters reference Paul Kleimeyer.)
- **Built-in player invoked via `SYS 30120`** — verbatim community note:
  > "For the time an absolute godsend having the player code built-in." (commenter)
  `SYS 30120 = $75A8`. With the documented load base **$7580**, that is **load+$28** — i.e. the
  player's interactive/standalone entry sits ~$28 past the load address, in the same ~$7580 region
  the brief and `research.md` give for init ($7580) / play ($7587). Useful anchor: a ripped tune's
  init/play live at the very start of the loaded image, while the editor's playback SYS is +$28.
- A companion tool **"Musictranslator V1.2"** was *"spread together"* with this crack (Fred,
  Oct 2014) — a separate utility, likely for converting/importing tunes. Lead for format research.
- Historical weight (commenter): *"A lot of early famous c64 tracks were written with it."* Names
  surfaced: **Paul Kleimeyer** and **The Mighty Bogg** as heavy users.

### Release #215363 — "Master Composer", crack by Eagle Soft Incorporated (ESI) (1985)
- Release type: **C64 Crack**, year **1985**, group **Eagle Soft Incorporated**. "No credits
  found"; no Access Software/Kleimeyer attribution on the page.
- Only comment, **Paladin (2022-03-15), verbatim:** *"Nice find! I remember this program from back
  in the day. I never could quite figure out how"* to use it (wondered whether ESI shipped docs).
- Takeaway: Master Composer was cracked and re-spread by multiple US groups (ICG, ESI) in 1985 —
  consistent with it being a popular US commercial editor — and the UI was non-obvious without the
  manual (recurring theme; see the Lemon64 manual thread below).

> NOTE on CSDb release #128699 (cited in `research.md`): not directly fetched this session; the
> two cracks above (31047, 215363) are the ones surfaced by search. 128699 is presumably the
> original/import entry — verify when CSDb access is unthrottled.

---

## Lemon64 thread leads (community discussion) — discovered, not yet fetched

Lemon64 was rate-limiting this session (HTTP 503, `Retry-After: 3600`), so these are **leads with
the one snippet search returned**, to be fetched next session:

- **"Master composer manual scan?"** — https://www.lemon64.com/forum/viewtopic.php?t=55611
  (2015). Search snippet: a user notes you **press the 'H' key for the help screen**; the poster
  was hunting for a scanned manual. → Best single thread for UI/workflow + possibly the hum bug.
- **"Comparison of C64 Music Editors"** — https://www.lemon64.com/forum/viewtopic.php?t=67248
  (companion to the Chordian blog comparison). → Where Master Composer sits vs Soundmonitor / FC.
- **"Music Composer (1982)(Commodore)"** — https://www.lemon64.com/forum/viewtopic.php?t=82190.
  ⚠️ DIFFERENT product — Commodore's 1982 "Music Composer" cartridge, NOT Access Software's 1983
  "Master Composer". Another easy name-confusion to avoid.
- **"Best Music composer SOFTWARE"** — https://www.lemon64.com/forum/viewtopic.php?t=50178.

(No Codebase64 / comp.sys.cbm disassembly of the Master Composer player was found — consistent
with the source being non-public per `research.md`. The freely available byte-level knowledge is
the sidid signatures in `forum_sidid_fingerprints.md` plus the HVSC binaries themselves.)

---

## What the community sources add to the engine picture
1. **Player entry geometry corroborated:** built-in player at `SYS 30120` ($75A8 = load+$28),
   reinforcing the $7580 load / $7587 play region.
2. **Companion tool exists ("Musictranslator V1.2")** — a lead for understanding the on-disk
   data/import format.
3. **Wide US distribution + opaque UI** — explains why ~1000 ripped tunes survive while the
   format stayed under-documented (manuals scarce; "couldn't figure out how to use it").
4. **No effect engine, confirmed by silence:** across all community discussion there's never a
   mention of vibrato/arp/PWM — only "direct register" register-snapshot behaviour. Matches VGMPF
   and the sidid disassembly (table-indexed freq + gate-masked control writes, nothing else).
