# How DeepSID labels SID-Wizard (player tags, versions, multi-SID)

**Provenance**
- Author of this doc: research agent, 2026-06-13 (SIDfinity SID-Wizard research cluster).
- Primary evidence: the **local DeepSID checkout** at `tmp/dmc_hunt/DeepSID/`
  (READ-ONLY) — source of truth over the live site. Specific files cited inline:
  `js/browser.js`, `js/controls.js`, `js/viz.js`, `php/sid_id.php`, `php/player.php`,
  `php/annex_help.php`, `php/upload_new.php`, `css/style.css`, `changes.htm`,
  `utility/sidid_100/sidid.c`.
- Web corroboration (June 2026): DeepSID project page + the SourceForge SID-Wizard
  page ("Stereo (2SID) and 3SID version included"), CSDb release pages for
  1 Raster-Tracker (#117935, 2013) and FlexSID-1.2 (#220017, 2022). Live URL:
  https://deepsid.chordian.net/.
- This doc is about **DeepSID's labelling mechanism**; the SIDId signature bytes and the
  HVSC population split live in the sibling file `sidid_variant_taxonomy.md`.

---

## 0. TL;DR

| Question | DeepSID's answer |
|---|---|
| How does DeepSID identify the player? | Its own PHP port of **cadaver's SIDId** (`php/sid_id.php`), run once at SID **upload** time (`identifyPlayer()`), result cached in its DB `files.player` column — same signature DB (`sidid.cfg`) HVSC uses. |
| What player string does a SID-Wizard tune get? | The **primary** SIDId name `Hermit/SidWizard_V1.x` — displayed prettified as **"Hermit/SidWizard v1.x"** (regex `_`→space, `V`→`v`). |
| Does DeepSID surface the V-version (1.0/1.2/1.4/1.5)? | **No.** Its SIDId port returns only the first-matching primary key; the parenthetical version sub-sigs are extra signatures under that same key and are discarded. UI shows just "v1.x". |
| Does DeepSID surface 2SID/3SID? | **Yes — but from the FILENAME, not SIDId.** `controls.js` sets `browser.chips = 2/3` purely by testing the filename for `"_2SID"` / `"_3SID"`. |
| Player color strip | SID-Wizard = strip class **`pl-c`**, a cyan/teal (`#7bb` light theme, `#377` dark) — the only visual player tag; not version- or chip-specific. |
| DB field for chips | DeepSID's own DB has a player-metadata `sid_chip_count` field (shown as "Number of SID chips" in the player-info panel), but it describes the *player tool's capability*, not a per-tune flag. Per-tune chip count = filename suffix. |

The net effect mirrors HVSC's `hvsc84.db`: **DeepSID collapses all SID-Wizard versions and
chip counts into one player label `Hermit/SidWizard_V1.x`**, and recovers chip count only
from the HVSC `_2SID`/`_3SID` filename convention.

---

## 1. The identification pipeline (local source walk)

### 1.1 SIDId, re-implemented in PHP
`php/sid_id.php` header comment: *"This was inspired by the SIDId script by Cadaver that
HVSC uses."* It is a faithful port:
- Loads `../sidid.cfg` (the same config analysed in `sidid_variant_taxonomy.md`),
  tokenising `??`→`T_ANY`, `END`→`T_END`, `and`→`T_AND`, hex pairs→bytes
  (`sid_id.php` lines 39–74).
- `identifyBytes()` slides each signature over the whole SID image
  (lines 85–123).
- **Return semantics (lines 127–133):**
  ```php
  foreach ($config_array as $player => $signatures) {
      foreach ($signatures as $signature) {
          if (identifyBytes($chars, $signature, $sid_size))
              return $player;   // ← returns the PRIMARY key, first match wins
      }
  }
  ```
  `$config_array` is keyed by the **bare** player name; the parenthetical sub-sigs
  (`(SidWizard_V1.0)`, `(SidWizard_2SID)`, …) are stored as *additional signatures under
  the same key*. So a SID-Wizard hit returns exactly `Hermit/SidWizard_V1.x` — **the
  version and chip-count sub-signatures never reach the returned label.** (Same C-source
  behaviour as `utility/sidid_100/sidid.c`, SIDId V1.09.)

### 1.2 When it runs + where it's stored
- On upload: `php/upload_new.php` line 121 — `'player' => identifyPlayer($sid['tmp_name'])`.
- HVSC bulk import: `php/utility/update_hvsc_db.php` ("Add SIDId stuff") populates the
  same `player` column for the catalogue.
- The value is cached in DeepSID's MySQL `files.player` and shipped to the browser as
  `file.player`.

### 1.3 Display formatting (`js/browser.js` line ~1985)
```js
player = file.player.replace(/_/g, " ").replace(/(V)(\d)/g, "v$2"),
```
`Hermit/SidWizard_V1.x` → **"Hermit/SidWizard v1.x"** shown in the row's secondary line
(`' in '+player`). No further version parsing.

---

## 2. The player color strip (`pl-c`)

`js/browser.js` defines `playerStrips` and assigns a strip by **substring match** on
`file.player`:
```js
const playerStrips = [
  { type:"GoatTracker",  class:"pl-a" },   // gray
  { type:"NewPlayer",    class:"pl-b" },   // green
  { type:"SidWizard",    class:"pl-c" },   // cyan/teal   ← SID-Wizard
  { type:"SidFactory_II",class:"pl-d" }, { type:"SidFactory II", class:"pl-d" }, // blue
  { type:"DMC",          class:"pl-e" },   // yellow
  { type:"SidTracker64", class:"pl-f" },   // (SidTracker 64)
];
// …
$.each(playerStrips, function(i, strip) {
    if (file.player.indexOf(strip.type) != -1) playerType = " "+strip.class;
});
```
- Match is on the substring **`"SidWizard"`** — so it catches `Hermit/SidWizard_V1.x`.
  Note it would **not** catch `Hermit/FlexSID` or `Hermit/1RasterTracker` (no
  `playerStrips` entry → those sibling Hermit engines get **no color strip** in DeepSID).
- CSS (`css/style.css`): `--color-strip-pl-c: #7bb` (light theme) / `#377` (dark);
  applied via `#songs .pl-c { background: var(--color-strip-pl-c); }` and the annex
  legend `.annex-c:before`.
- `changes.htm` (Sep 25, 2021) documents the feature: *"GoatTracker is gray, NewPlayer is
  green, **Sid-Wizard is cyan**, SID Factory II is blue, and DMC is yellow."* — strips
  were added 2021.

So DeepSID's only *visual* player tag for SID-Wizard is a single cyan strip — version- and
chip-agnostic.

## 3. Player-search tags (the annex / `data-type="player"`)

`php/annex_help.php` (the "Color strips" help block) gives the clickable player searches:
```html
<div class="annex-strip annex-c"> = <b>SID-Wizard</b></div>
  <span class="annex-tiny">
    <a href="sidwizard_v1.x" data-type="player" class="search"><b>v1.x</b></a>
  </span>
```
- The **only** SID-Wizard player-search tag offered is `sidwizard_v1.x` (cf. GoatTracker
  which offers `v1.x` *and* `v2.x`, NewPlayer which offers `v2`/`v3`, DMC `v4.x`/`v5.x`).
  This reflects that SIDId's SID-Wizard signatures all roll up to one primary `V1.x`.
- These player searches expect the **raw SIDId names**, not the prettified display form
  (`annex_help.php` line 201: *"Expects raw SIDId player names, not the prettified
  ones."*). So a search query matches against the stored `Hermit/SidWizard_V1.x`.

## 4. Multi-SID (2SID / 3SID) — filename-driven, not header- or SIDId-driven

This is the important DeepSID quirk for the multi-SID question.

`js/controls.js` (two places, on song load — lines 149–150 and 287–288):
```js
browser.chips = 1;
if      (browser.songs[...].fullname.indexOf("_2SID") != -1) browser.chips = 2;
else if (browser.songs[...].fullname.indexOf("_3SID") != -1) browser.chips = 3;
this.resetStereoPanning();
```
- **Chip count = filename test for `_2SID` / `_3SID`.** DeepSID does *not* parse the PSID
  v3/v4 2nd/3rd-SID address bytes for this (those bytes are honoured by the WASM SID
  emulator for *playback* routing, but the *UI chip count* is the filename). This works
  precisely because HVSC names every multi-SID SID-Wizard file `*_2SID.sid` / `*_3SID.sid`
  (verified: all 38 multi-SID tunes carry the suffix — see `sidid_variant_taxonomy.md` §3.3).
- Downstream of `browser.chips`:
  - `js/controls.js` `resetStereoPanning()` / `enableStereoChip(2|3)` enables stereo
    panning sliders for chips 2/3.
  - `js/viz.js`: a third on-screen keyboard is disabled for 2SID
    (`if (voice==2 && browser.chips==2) return;`); the piano "combine" button is replaced
    with a **2SID/3SID** toggle (`pv-c2sid` / `pv-c3sid` classes, colors
    `--color-piano-vc-on-*-2sid #44d/#66f`, `*-3sid #d44/#f66`); oscilloscope/stereo
    scopes get per-chip per-voice canvases (`scope-s2v1`, `scope-s3v1`, …).
- `php/player.php` line 137 renders a **"Number of SID chips"** row from a player-metadata
  `sid_chip_count` field — but that's part of the *player encyclopedia* entry (describing
  the SID-Wizard *tool's* capability: 1/2/3/4-SID), not a per-tune classification.

**Consequence for SIDfinity:** DeepSID confirms the cheap, reliable multi-SID test is the
`_2SID`/`_3SID` filename suffix (equivalently `psid_version ≥ 3`). DeepSID itself never
needs SIDId to know the chip count, and never exposes which SID-Wizard *version* a tune
used.

## 5. What this means for the SIDfinity migration

1. **Treat DeepSID's player label as engine identity only** — it carries `Hermit/SidWizard
   v1.x` with no version/chip granularity, exactly like `hvsc84.db.engine`. Don't expect
   to scrape sub-version info from DeepSID.
2. **Chip count is a filename/header property, not a player-ID property.** For the
   single-SID in-scope subset (1010 tunes), filter out `*_2SID`/`*_3SID` (= the 38
   multi-SID tunes). This is the same filter DeepSID uses to drive its stereo UI.
3. **The cyan `pl-c` strip = "this is SID-Wizard"** and nothing finer; FlexSID and
   1RasterTracker get *no* DeepSID strip, reinforcing that they're separate engines that a
   SID-Wizard pipeline won't (and shouldn't) absorb.
4. DeepSID's `sid_chip_count` "encyclopedia" value (per-player, not per-tune) corroborates
   that SID-Wizard the *tool* spans 1–4 SID, even though HVSC #84 has no 4SID instance.

## Leads to follow
- **Scrape DeepSID's player-encyclopedia entry for SID-Wizard** (the row behind
  `player.php`'s "Number of SID chips / Channels visible / Speeds / Digi / Import from /
  Save/Export to" fields) — it likely lists the authoritative feature matrix (driver
  variants, XM/MIDI import, chip range) in one place. Path: `deepsid.chordian.net` player
  info panel; or the DB row feeding `php/player.php`.
- **Confirm the live site matches this local checkout** — the checkout is a point-in-time
  clone; spot-check one HVSC SID-Wizard tune's displayed player string + strip color on
  https://deepsid.chordian.net/ to ensure no newer DeepSID build added version tagging.
- **Cross-reference DeepSID's `files.player` against `hvsc84.db.engine`** for the 1048
  tunes to confirm both ran the *same* SIDId config (they should — both cite cadaver's
  SIDId) and that none diverge (e.g. a tune DeepSID tags FlexSID but the DB tags
  SidWizard, or vice-versa).
- **Check whether DeepSID's WASM player (jsSID, Hermit's own) handles the `$DE00` 2nd-SID
  placement** used by the 9 Televicious tunes — relevant only if multi-SID is later
  brought in scope, but DeepSID is the natural reference renderer since both jsSID and
  SID-Wizard are Hermit's.
