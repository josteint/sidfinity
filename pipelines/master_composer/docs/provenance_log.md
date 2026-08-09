# Provenance log — Master Composer research sweep (2026-06-13)

Roll-up across the six-cluster sweep. Per-file provenance headers carry exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| local JC64dis `tmp/jc64/doc/example/Master_Composer.dis` | local decode (gzip + JC64dis project reader) | 22 routine labels + per-`$D4xx` comments; the player annotation |
| HVSC `Maniac.sid` (+ Star_Trek_II) | local disasm (py65) + `siddump --writelog`/`--writelog-per-irq`/`--memwatch` | byte-exact data layout + write model + CIA dispatch + the hum bug |
| local `sidid.cfg` ×3 | local read (read-only) | `Master_Composer` + `(Patrick_Payne)` + `(Lope_Pulse_Sweep)` sigs; TFMX separation |
| `hvsc85/DOCUMENTS/BUGlist.txt` + Update_Announcements #80 | local read (read-only) | 8 truncated-rip entries; the hum-bug fix note (Prg2Sid 1.15) |
| `hvsc84.db` | read-only (`mode=ro`) | census: 1019; speed-bit (996 = $1), init/play (+7 delta 962/1019) |
| archive.org `d64_Master_Composer_v1.0_19xx_Playboy` + preservation64 G64 | curl | editor disk + 29 UI screenshots (de-facto manual); original-dump provenance |
| VGMPF, DeepSID, Commodore Music Software Guide (1986) | direct | engine model corroboration; player-name; vendor listing |
| GitHub (player-id, sidid, ChiptuneSAK, sid2midi, libsidplayfp) | direct | NEGATIVE: no format-aware Master Composer parser anywhere |

## Attempted but blocked / negative

| Source | Status |
|---|---|
| CSDb release HTML | 503 / anti-bot to WebFetch; curl Firefox-UA worked for some |
| Lemon64 threads (t=55611 manual scan, t=67248 editor comparison) | 503, Retry-After 3600 |
| Printed manual (scanned PDF) | does not exist online (confirmed); only the in-program "H" help screen |
| Pouet | no match (Amiga/PC-skewed) |
| 4am crack write-up | Apple-II-only for this title |

## Unfetched leads (see README "Top leads")

Music Translator V1.2 (format converter, on the ICG crack d64); Prg2Sid 1.15
hum-patch diff (CSDb #235041); the editor "H" help-screen dump; the
`Star_Trek_II.sid` second-variant disasm; Compute!'s Gazette 1984 ads.

## Note

All six agents honored the no-git / write-scoped / read-only-DB constraints, and
followed the updated skill guidance — kept source went to `docs/src/`
(`Maniac_seed_disasm.s`, `jc64dis_labels.txt`), scratch to a `tmp/` workdir; no
tracked file outside the docs dir was touched.
