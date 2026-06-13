# HardTrack Composer — CSDb & Pouet Releases

> **Provenance**
> - source_url:
>   - https://csdb.dk/release/?id=74928  (HardTrack Composer V1.0, Elysium 1992)
>   - https://csdb.dk/release/?id=36647  (HardTrack Composer V1.0+ [6 speed], BHG)
>   - https://csdb.dk/search/?seinsel=releases&search=hardtrack  (release list)
>   - https://github.com/cadaver/sidid  (engine fingerprint)
>   - https://www.pouet.net  (searched; no entry)
> - fetched_via: WebFetch / WebSearch
> - fetch_date: 2026-06-13
> - author (tool): Brush + Longhair (Elysium / Parados)
> - content_date: 1992 (original); cracks/variants 1994–1998
> - reliability: **primary** for CSDb facts (it is the authoritative scene DB);
>   secondary for the inferred lineage notes.

---

## 1. The canonical release — CSDb #74928

**Hardtrack Composer V1.0** — C64 **Tool** (music editor) — **Elysium (ESM), 1992**.

| Field | Value |
|-------|-------|
| Type | C64 Tool (music composition editor / tracker) |
| Group | Elysium (ESM) |
| Year | 1992 |
| Version | 1.0 |
| Code | **Brush** (Elysium, Parados) |
| Player routine | **Longhair** = Milosz Ignatowski (Elysium, Parados) |
| Demo music | "Frozen Energy" by **The Syndrom** (Crest, The Imperium Arts) — `/MUSICIANS/T/The_Syndrom/Frozen_Energy.sid` |
| Graphics | **Cruise** (Padua) |
| Downloads | ~848 |

User comment (Fred, 2013-08-04): *"I've added Longhair to the credits since he made
the code of the player."* — this is why the player is credited to Longhair while the
editor is Brush's; the two roles are separate, which matches the SDK split
(`EDYTOR.SRC` = Brush's editor, `PLAYER_V1.x` = Longhair's player).

---

## 2. CSDb #36647 — the 6-speed variant

**Hardtrack Composer V1.0+ [6 speed]** — C64 Tool — **Beverly Hills Group (BHG)**.

| Field | Value |
|-------|-------|
| Type | C64 Tool |
| Group | Beverly Hills Group (BHG) |
| Version | V1.0+ "[6 speed]" |
| Code | Brush (Elysium, Parados, Sex Instructors, Success), **Glover** (Samar Productions), Longhair (Elysium, Parados) |
| Downloads | ~727 |

This is a BHG reassembly of V1.0+ enabling **6× multispeed** (the player's frame
divider raised). Glover (Samar) is credited alongside Brush + Longhair — Samar is the
Polish group that also produced the Bzyk-era relocated tunes. The on-disk artifact
`tmp/hardtrack/Hardtrack.Composer.v1.6speed.BHG.zip` corresponds to this release.

---

## 3. Full HardTrack release list on CSDb (search "hardtrack")

| ID | Title | Type | Group | Year |
|----|-------|------|-------|------|
| **74928** | Hardtrack Composer V1.0 | Tool | Elysium (ESM) | 1992 |
| **36647** | Hardtrack Composer V1.0+ [6 speed] | Tool | Beverly Hills Group (BHG) | — |
| 237295 | Hardtrack Composer V1.0+ [4 speed] | Tool | (n/a) | — |
| 13218 | Hardtrack Composer V1.0 [polish] | Crack | Axelerate (AXE) | 1998-11-01 |
| 78857 | Hardtrack Composer V1.0 | Crack | Chromance (<C>) | 1995 |
| 128062 | Hardtrack Composer V1.0 | Crack | Chromance (<C>) | 1995 |
| 135509 | Hardtrack Composer V1.0 | Crack | Alpha Flight (AFL) | 1995 |
| 82834 | Hardtrack Composer V1.0+ | Crack | Fatum (F) | 1994 |

Observations:
- The editor only ever versioned as **V1.0 / V1.0+** publicly; the "+" denotes the
  multispeed-enabled reassemblies ([4 speed], [6 speed]).
- The **player routine** internally versioned 1.0 → 1.1 (see
  `csdb_release_notes_and_versions.md`); that is the embedded driver Longhair shipped,
  distinct from the editor's public version string.
- Heavy crack activity 1994–1998 (Chromance, Alpha Flight, Fatum, Axelerate) reflects
  its popularity on the Polish scene; the 1998 Axelerate "[polish]" crack and the
  Samar/Bzyk relocated layout (≈118 HVSC tunes) date the engine's second wave.

---

## 4. Engine identification (sidid)

`cadaver/sidid` identifies the engine as **`HardTrack_Composer`** via the
reloc-invariant byte signature:
```
0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB 1D ?? ?? 8D ?? ?? 8D 17 D4
```
This is the **filter-resonance emitter** at $1360–$137C in the player (see
`csdb_player_source.md` §4.3): `ASL ASL / STA <selfmod> / PLA / AND #$F0 / … /
LDA $101F / AND #$0F / ORA $FB / ORA $1691,x / STA $101F / STA $D417`. HVSC's
engine attribution (1,170 tunes) derives from this fingerprint.

---

## 5. Pouet

**No Pouet entry.** Pouet indexes demos/intros, not native C64 music editors;
HardTrack Composer is not listed there. (Searched prodlist + name search 2026-06-13.)
The canonical scene record is the CSDb #74928 page in §1.

---

## 6. Top HardTrack composers in HVSC (context)

From the HVSC catalogue: Bzyk (262), Randy (92), Remarque (87), Shapie (81), plus
Wodnik, V-12, Amadeus Attic, Klax and others — a primarily Polish-scene composer base,
consistent with Elysium/Parados/Samar origins.

---

## Sources

- [CSDb #74928 — Hardtrack Composer V1.0 (Elysium, 1992)](https://csdb.dk/release/?id=74928)
- [CSDb #36647 — Hardtrack Composer V1.0+ [6 speed] (BHG)](https://csdb.dk/release/?id=36647)
- [CSDb release search "hardtrack"](https://csdb.dk/search/?seinsel=releases&search=hardtrack)
- [cadaver/sidid — engine fingerprint database](https://github.com/cadaver/sidid)
- [Pouet.net (no HardTrack entry)](https://www.pouet.net)
