---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
fetched_via: direct (curl)
fetch_date: 2026-06-15
author: Cadaver (Lasse Öörni) and SIDId contributors
content_date: cumulative (1989-2024)
reliability: primary
---

# SIDId NFO — Authorship Records for Vibrants/Laxity Cluster

Verbatim entries from sidid.nfo for all relevant Vibrants/Laxity cluster entries:

```
Vibrants/Laxity
     NAME: LAXITY editor
   AUTHOR: Thomas Egeskov Petersen (Laxity)
REFERENCE: https://csdb.dk/release/?id=122333

Vibrants/JO
   AUTHOR: Poul-Jesper Olsen (JO)

JCH_OldPlayer
   AUTHOR: Jens-Christian Huus (JCH)

Laxity_NewPlayer_V21
   AUTHOR: Thomas Egeskov Petersen (Laxity)
 RELEASED: 2006
REFERENCE: https://csdb.dk/release/?id=26563

SidFactory/Laxity
   AUTHOR: Thomas Egeskov Petersen (Laxity)
 RELEASED: 2006
REFERENCE: https://csdb.dk/release/?id=39519

SidFactory_II/Laxity
   AUTHOR: Thomas Egeskov Petersen (Laxity)
 RELEASED: 2020
REFERENCE: https://csdb.dk/release/?id=210571
```

## Key facts

1. **`Vibrants/Laxity`** is officially named "LAXITY editor" — Thomas Egeskov Petersen's
   (Laxity's) bespoke C64 player from the late 1980s/1990. Canonical CSDb reference: #122333
   ("Laxity Editor v/32-3.34", 1990).

2. **`Vibrants/JO`** is authored by **Poul-Jesper Olsen (JO)**. JO was a member of Vibrants.
   No CSDb reference or release date given in the nfo. This is a separate player engine
   co-existing in the Vibrants group alongside Laxity's editor.

3. **`JCH_OldPlayer`** is JCH's early compositions IN Laxity's player format — not a
   separate editor, but JCH adapting/using the Laxity player. No release date listed.
   This is the same player binary as Vibrants/Laxity but possibly with JCH's own
   data-encoding adaptations, hence given a separate SIDId name.

4. **`Laxity_NewPlayer_V21`** (2006) and **`SidFactory/Laxity`** (2006) are separate
   later engines — 15+ years after the original Laxity editor. Not in scope for
   the Vibrants/Laxity target.

5. **`SidFactory_II/Laxity`** (2020) is the modern SF2 engine. Separate migration target.

## HVSC classification implications

- `pipelines/vibrants_laxity/` = the target for **`Vibrants/Laxity`** (LAXITY editor,
  CSDb #122333) — 179 HVSC SIDs.
- `Vibrants/JO` (Poul-Jesper Olsen) is a DISTINCT engine — separate `pipelines/vibrants_jo/`
  (already noted in the repo: `pipelines/vibrants_jo/docs/research.md` exists).
- `JCH_OldPlayer` (JCH in Laxity's format) — may share the Vibrants/Laxity player binary
  but with JCH-authored data; could potentially use the same extractor with different
  config. Check HVSC count separately.
