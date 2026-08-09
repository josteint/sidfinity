# Master Composer — sidid player fingerprints (engine internals from byte signatures)

Provenance
- source_url: https://github.com/cadaver/sidid — `sidid.cfg` (signature DB) and `sidid.nfo` (notes),
  fetched via raw.githubusercontent.com
- fetched_via: WebFetch (sidid.cfg, sidid.nfo) + local byte verification against `hvsc85/` SIDs
  (read-only Python, no modification)
- fetch_date: 2026-06-13
- author/handle: Lasse Öörni (cadaver) — sidid is THE player-identification engine HVSC uses to
  populate its engine classification (and the `engine` column in our `hvsc84.db`).
- content_date: sidid is continuously maintained; entries here current as of the master branch.
- reliability: HIGH for the signatures (this is the authoritative source of HVSC's classification);
  the opcode interpretation below is MY disassembly of the signature bytes — flagged as analysis.

---

## Why this matters
HVSC's `Master_Composer` engine tag (1019 tunes in our `hvsc84.db`) comes from these sidid
signatures. They are short machine-code fingerprints of the **play routine**, so they double as a
free partial disassembly of the engine's per-frame voice-control writes. They also settle the
`(Patrick_Payne)` question and the TFMX name-collision.

## The three relevant sidid signatures (verbatim hex from `sidid.cfg`)

```
Master_Composer
F0 ?? C9 64 D0 0E ?? ?? ?? ?? ?? ?? 29 FE 8D 0B D4 4C ?? ?? A8

MasterComposer            ; sidid label: Patrick_Payne (a variant signature of the SAME engine)
29 FE 8D 04 D4 4C ?? ?? A8 B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4

TFMX/MasterComposer       ; a DIFFERENT engine — based on Hülsbeck's TFMX player
F0 26 B1 06 48 4A 4A 4A 4A 9D
```

`sidid.nfo` author/date notes (verbatim):
- Master Composer: **"AUTHOR: Paul Kleimeyer  RELEASED: 1983  Access Software Inc."**
- TFMX/MasterComposer: **"AUTHOR: Playboy & Sir Tippitt  RELEASED: 1990  Bierfront"**, and it is an
  **"Editor that is based on the player of /MUSICIANS/H/Huelsbeck_Chris/Starball.sid."**

## Disassembly of the `Master_Composer` signature (my analysis)
`F0 ??` `C9 64` `D0 0E` … `29 FE` `8D 0B D4` `4C ?? ??` `A8`
- `C9 64` = `CMP #$64` — compare the current note/index against **100 ($64)**. This is the engine's
  note-range gate: valid note indices are **$01..$63** (1..99), exactly matching `research.md`'s
  "$01-$63 = note frequency index" and the "96-entry freq table" sizing.
- `D0 0E` = `BNE +$0E` — branch when not the special value.
- `29 FE` = `AND #$FE` — clear bit 0 (the **gate bit**) of an accumulated control-register value.
- `8D 0B D4` = `STA $D40B` — write **voice-2 control register**. So the player composes a control
  byte and masks the gate off in the "rest/hold" path before storing it.
- `4C ?? ??` = `JMP abs` ; `A8` = `TAY`.

## Disassembly of the `Patrick_Payne` variant signature (my analysis)
`29 FE` `8D 04 D4` `4C ?? ??` `A8` `B9 ?? ??` `8D 00 D4` `B9 ?? ??` `8D 01 D4`
- `AND #$FE : STA $D404` — same gate-mask, but on **voice-1 control register** ($D404).
- `B9 lo,hi : STA $D400` then `B9 lo,hi : STA $D401` — two **absolute-indexed (`,Y`) table loads**
  feeding **$D400 / $D401** (voice-1 frequency lo/hi). I.e. the freq comes straight out of a table
  indexed by the note value — the direct-register, table-driven model with NO effects.

## KEY FINDING — the two signatures are ONE engine, not two
I verified both signatures against actual HVSC binaries (read-only):

| File | `Master_Composer` sig offset | `Patrick_Payne` sig offset | delta |
|---|---|---|---|
| `DEMOS/UNKNOWN/Master_Composer/Mr_Sandman.sid` | 610 | 557 | **53** |
| `…/Kitten_on_the_Keys.sid` | 610 | 557 | **53** |
| `…/Viva.sid` | 610 | 557 | **53** |
| `…/Pan_3.sid` | 610 | 557 | **53** |
| `…/Bread_and_Butter.sid` | 610 | 557 | **53** |
| `…/Superman_2.sid` | 610 | 557 | **53** |
| `GAMES/S-Z/Test_Drive.sid` (Patrick Payne) | 866 | 792 | 74 |

**Both signatures co-occur in every Master Composer file**, separated by a fixed gap. The
`Patrick_Payne` sig (voice-1: `STA $D404` + `STA $D400/$D401`) sits ~53 bytes *before* the
`Master_Composer` sig (voice-2: `STA $D40B`). They are simply **adjacent per-voice slices of the
same contiguous play routine** — the engine writes voice 1's control + frequency, then (53 bytes
on) voice 2's control. This is exactly the "identical player code across all files" the brief
describes. So:

- The HVSC `(Patrick_Payne)` parenthetical and sidid's `Patrick_Payne` signature are **the same
  engine as `Master_Composer`** — NOT a distinct player variant. The label exists because sidid
  carries a second fingerprint anchored on the voice-1 writes (Patrick Payne's Access Software
  game rips were a convenient sample for it), and HVSC uses `(Patrick_Payne)` as the **author
  credit** (he composed/ripped those tunes). See `forum_namecollision_payne.md`.
- The Test Drive delta (74, not 53) shows the **game-embedded** Master Composer rips can have a
  slightly different inter-voice layout / relocation than the standalone editor rips — worth a
  per-file check during extraction, but it is the same engine (both sigs present).

## TFMX/MasterComposer is a genuinely different engine
The `TFMX/MasterComposer` signature `F0 26 B1 06 48 4A 4A 4A 4A 9D` shares NOTHING with the above:
`B1 06` is indirect-indexed `(zp),Y` load (TFMX uses pointer tables in zero page), `4A 4A 4A 4A`
is a 4-bit nibble shift, `9D` is `STA abs,X`. Different dispatch, different data model. sidid keeps
it as a separate entry, and our `hvsc84.db` has it as a separate engine with only **5 tunes**
(vs 1019 for `Master_Composer`). Full disambiguation in `forum_namecollision_payne.md`.

## Implication for our pipeline
- The note-range gate `CMP #$64` (max index $63) + table-indexed `STA $D400/$D401` confirm the
  USF model in `research.md`: notes are **indices into a freq table**, bars hold up to 16 note
  indices, and there are **no per-note effect bytes**. The play routine is three near-identical
  per-voice slices doing {compose control byte, mask gate on rest, store ctrl; load freq lo/hi
  from table, store}. This is the engine to reproduce as a write-stream.
- Because both sidid sigs are the same engine, the extractor should treat `Master_Composer` and
  `(Patrick_Payne)`-credited tunes with ONE code path.
