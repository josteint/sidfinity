# SID-Wizard — Multi-SID write-address mapping (forum/wiki cluster + empirical HVSC ground truth)

> **Provenance**
> - **source_url (forum):** `https://chipmusic.org/forums/topic/14204/sidwizard-3sid-version-o/` (+ page/2),
>   `https://chipmusic.org/forums/topic/18490/sid2sid-adress-second-sid-at-d420/`,
>   `https://chipmusic.org/forums/topic/12345/c64-trackers-that-work-with-dual-sids/`
> - **source_url (forum):** `https://csdb.dk/release/?id=220489` (V1.91 release comments — the SID4-header problem)
> - **source_url (wiki/blog):** `https://blog.chordian.net/2017/04/01/3sid-c64-sid-music-in-9-voices/`
> - **source_url (manual):** SID-Wizard 1.4 / 1.5 User Manuals (register table + 2SID 'SID2 address' setting)
> - **empirical:** local parse of **1048** `Hermit/SidWizard_V1.x` PSID/RSID headers in `hvsc85/` (2026-06-13)
> - **fetched_via:** WebSearch (chipmusic.org + lemon64 direct WebFetch were **HTTP 403 / 503**-blocked —
>   substantive text recovered from search-result snippets); WebFetch (CSDb, Chordian); Python header-parse
>   of the actual `.sid` files for the empirical section.
> - **fetch_date:** 2026-06-13
> - **author/handle:** Hermit (Mihály Horváth); forum posters as attributed inline.
> - **content_date:** 2012–2022 (forum); HVSC #84 binaries.
> - **reliability:** secondary (forum/wiki); the empirical HVSC-header section is **ground truth** (parsed bytes).

---

## 0. The bottom line for SIDfinity (read this first)

SID-Wizard does **NOT** hardcode the second/third SID address into the player. The *editor* exposes a
**"SID2 address" setting** (and the SID-Maker exporter requires it for every export format); the chosen
address is baked into the exported player's `STA $D4xx` targets and written into the PSID v3/v4 header.
So the write-target base for chip *N* must be read **per-tune from the SID header**, never assumed.

**Empirically, across all 1048 `Hermit/SidWizard_V1.x` tunes in HVSC #84:**

| # SIDs | tunes | PSID ver | SID1 base | SID2 base (observed) | SID3 base (observed) |
|--------|-------|----------|-----------|----------------------|----------------------|
| 1 (mono)  | 1010 | v2 | `$D400` | — | — |
| 2 (stereo)| 29   | v3 | `$D400` | `$D420` ×26, `$D500` ×3 | — |
| 3 (3SID)  | 9    | v4 | `$D400` | `$D420` ×9 | `$D440` ×9 |

(7 of the 1048 are RSID, 1041 PSID. No 4SID tunes in HVSC #84 — 4SID export postdates the collection;
see §3.)

The **canonical SID-Wizard multi-SID layout is contiguous +$20**: SID1=`$D400`, SID2=`$D420`,
SID3=`$D440`. That is what every 3SID tune in HVSC uses, and the most common 2SID choice. The
`$D500` 2SID variants (3 tunes: the *Quad_Core* parts) use the older JCH-style "second SID at `$D500`"
convention; `$DE00` appears as a SID2 choice in the editor's address list but is **not** present in the
final HVSC `Hermit/SidWizard_V1.x` headers as a SID2 base (it showed up only via the editor address
menu / chipmusic discussion — treat `$D420`/`$D500` as the realised cases).

> **Parse note:** PSID v3 stores the 2nd-SID address mid-byte at header offset **`$7A`**, v4 the 3rd-SID
> at **`$7B`**; the stored byte `B` maps to base address `$D000 | (B << 4)` — e.g. byte `$42` → `$D420`,
> `$50` → `$D500`, `$44` → `$D440`. SID model bits for the extra chips live in the v3/v4 `flags` word.

---

## 1. The C64-side address landscape (why these addresses)

The SID is normally decoded only at `$D400..$D41F`. Extra physical SIDs need extra address decoding,
and the scene never agreed on one standard — so SID-Wizard offers a *menu* of the common ones.

From the **1.4 manual** register table (Hermit, §3.3), verbatim:

> "The chip by default is routed to $D400 (54272) memory area by a PLA in C64, therefore the registers
> can be written by storing bytes to $D400..$D41F area from music routine. (Additional SID chips can be
> routed inside $D420..$D800 area by external chip-selector circuitry, though it's not a standard and
> widespread solution."

From the **chipmusic.org** discussion of dual/3SID addressing (paraphrased from the thread + search
snippet, secondary):

> "A 'stereo' version of JCH works with a second SID on **$D500**, which is considered the standard for a
> second SID. The Kerberos cart uses a second SID at **$D420**. Some 3SID releases use SIDs at **$D500
> and $D600**, while other 3SID trackers have SIDs at **$DE00 and $DF00**."

So the address depends on the *hardware target*:
- **`$D420`** — common for cartridges/expanders that decode A5 (Kerberos, many SID2SID/DualSID boards,
  Ultimate-64 UltiSID#2 default). This is SID-Wizard's most-used choice and the default for its 3SID
  contiguous `$D420`/`$D440` layout.
- **`$D500`** — the classic JCH/"stereo" convention (decodes higher); used by a minority of SID-Wizard
  2SID tunes.
- **`$DE00`/`$DF00`** — I/O-1/I/O-2 expansion-port windows; offered for boards that decode there.
- **`$D440`** — third SID in the contiguous layout.

The **Chordian 3SID** blog confirms SID-Wizard grew native 3SID:
> "SID-Wizard's built-in player does that [3SID] now." — blog.chordian.net, 2017-04-01.

---

## 2. Per-chip write model (what SIDfinity must reproduce)

Each extra SID is a **full independent voice-triple**. SID-Wizard's player runs the same per-channel
engine for each chip and emits writes to that chip's base + the same `$00..$1F` register offsets:

- Chip *N* channel *c* (c=0,1,2) frequency lo/hi → `base + 7*c + 0/1`
- pulse-width lo/hi → `base + 7*c + 2/3`
- waveform/control → `base + 7*c + 4`
- AD / SR → `base + 7*c + 5/6`
- filter cutoff lo/hi (`$15/$16`), res+switch (`$17`), mode+volume (`$18`) → `base + $15..$18`

i.e. the **identical write sequence as the mono player, just re-based** to `$D420` / `$D440` / `$D500`
etc. There is **no cross-chip register** — each SID has its own filter and master volume. The
multi-SID tunes use **reduced module limits** (see `forum_versions_and_drivers.md`: 31 instruments /
2 subtunes / 105 patterns in the 2SID build) but the same per-chip emitter.

**Stereo channel routing (playback-only, not a write-model concern):** per the V1.92 CSDb notes Hermit
routes SID1+SID3 to the left channel and SID2(+SID4) to the right, with the centre-capable chips
playable centrally. This is an *output-mix* description for emulators/hardware — it does **not** change
which `$D4xx` addresses are written, so it is irrelevant to the write-log verdict; recorded only so it
isn't mistaken for a write-mapping rule.

---

## 3. The 4SID gotcha (V1.92, post-HVSC-#84) — Hermit's own words

V1.91 (8 Aug 2022) did **not** have 4SID. From the **CSDb V1.91 release** discussion, Hermit verbatim:

> "I don't know a way to store SID4 address in SID-header, if anyone has info about it I'm all ears..."
> — Hermit, CSDb release id=220489 (Aug 2022)

User **JCH** noted in the same thread that an extended PSID variant supporting 4+ SIDs exists (used by
DeepSID) but is undocumented in the standard header. V1.92 (4 Sep 2022) then shipped 4SID using a
non-standard header convention. Hermit's V1.92 note (CSDb id=221555):

> "Full 4SID support. For .sid file generation I used the new WebSID SID-format proposal." — Hermit, 2022.

**Implication for SIDfinity:** any 4SID SID-Wizard file uses the **WebSID extended header** (not standard
PSID v4, which only carries up to 3 SID addresses at `$7A`/`$7B`). HVSC #84 contains **no** such files,
so this is a forward-compat note only — if a 4SID SID-Wizard tune ever enters scope, parse the WebSID
header layout for the SID3/SID4 addresses rather than the standard PSID offsets.

---

## 4. Editor / exporter mechanics (for cross-checking SID2 address)

- The editor sets the SID2 address from a menu ("most common addresses come first"); press **F7** in the
  editor (instrument panel context) area to reach the config — chipmusic discussion + 1.5 manual.
- **1.5 manual**, verbatim: *"There is an additional 'SID2 address' setting in 2SID version, works the
  same as in the editor: most common addresses come first. All export-formats need it."*
- The 2SID native workfile format is **`.sws`** (vs mono **`.swm`**); the 3SID build extends this again.
- SID-export also has an **old/new SID-type** (6581/8580) setting, auto-detected by default (1.5 manual).

---

## Cross-references
- Driver-variant feature matrix + version timeline → `forum_versions_and_drivers.md`
- Player call vectors, multispeed, hard-restart, ghost registers → `forum_player_internals_gotchas.md`
- Musical semantics of the SWM byte stream → sibling `csdb_hermit_site_manual.md`
