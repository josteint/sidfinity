# Bowden-canonical Companion engine — initial survey

Reverse-engineered from `hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.sid`
(disassembly in `disassembly.s`).

Engine fingerprint: **`c8282844`** (the first 256 bytes at init match
across 7 Vic Berry tunes — see fingerprint scan from the migration
planning session).

## Header

```
load=$C002   init=$C053   play=$C003   songs=1
body 3581 bytes, $C002..$CDFE
```

## Memory map

```
$C002          RTS  (early-return target for tempo-divider gate)
$C003 .. $C016 play entry — tempo divider, jumps to $C080
$C017          V1 position (1 byte)
$C018          (unused / part of V1 block — 7 bytes per voice)
$C019 .. $C01C V1 per-voice timbre: pw_lo, pw_hi, ctrl, ad
$C01D          unused
$C01E .. $C01F V2 position
$C020 .. $C023 V2 timbre
$C024          unused
$C025 .. $C026 V3 position
$C027 .. $C02A V3 timbre
$C02B          unused
$C02C .. $C037 reset_positions sub (init helper)
$C038 .. $C052 ?? (data gap, probably unused)
$C053 .. $C07A init routine (silences $D400-$D418, sets ADSR, calls reset)
$C07B          tempo (frames per note tick)  ← BACH = read this byte
$C07C          tempo counter (runtime)
$C07D .. $C07E unused (probably scratch)
$C07F          scratch for PW load loop
$C080 .. $C107 main per-note play loop + note processor
$C108 ..       data: orderlists + freq tables (described below)
$CA00 .. $CA7F freq_hi table (128 entries, indexed by note byte 0..7F)
$CA80 .. $CAFF freq_lo table (128 entries)
$CB00 ..       V1 orderlist (terminated by $FF)
$CC00 ..       V2 orderlist ($FF-terminated)
$CD00 ..       V3 orderlist ($FF-terminated)
```

## Engine semantics

**Tempo gate (per VBI frame, at `play`):**
```asm
$C003: INC v_tempo_ctr
       CMP v_tempo                ; $C07B = tempo
       BNE -> RTS                 ; not yet — wait
       reset counter; fall through to main play at $C080
```

**Main play (`$C080`) — for each voice independently:**
```asm
LDX v_pos                         ; V1pos = $C017, V2 = $C01E, V3 = $C025
INC v_pos                         ; advance after read
LDY orderlist[v_pos]              ; V1 = $CB00, V2 = $CC00, V3 = $CD00
LDX #(voice_offset: 0, 7, or 14)
JSR proc_note
```

**`proc_note` (`$C0AD`):**

Note byte Y, voice X (0 / 7 / 14):

| Y range | Action |
|---|---|
| $00..$7F | Normal note: write `freq_hi[Y]`/`freq_lo[Y]` to `$D401,X`/`$D400,X`; copy 4-byte timbre slice (`$C019,X` ..) to `$D402,X` .. `$D405,X` (PW_LO, PW_HI, junk-overwritten, AD); set `$D404,X` to ctrl+1 (gate on). |
| $80 | Gate off: write ctrl byte (`$C01B,X`) to `$D404,X` (gate=0). |
| $FF | Loop: reset this voice's position to 1, re-read its first note. |
| other bit-7 | undefined (branches into uninitialised $C108 — likely never fires in well-formed tunes) |

## Comparison to Hubbard '85

| Feature | Hubbard '85 | Bowden-canonical |
|---|---|---|
| Voices | 3 | 3 |
| Per-voice orderlist | yes | yes |
| Pattern indirection | yes | **no — flat orderlist of pitches** |
| Vibrato | yes | **no** |
| Portamento / freq slide | yes | **no** |
| Arpeggio | yes | **no** |
| PWM modulation | yes | **no** (PW fixed per note) |
| Effect flags per instrument | yes | **no instruments at all** — timbre is per-voice global |
| Subtune dispatch | yes | **no — always one tune** |
| Tempo | per-pattern | **single global tempo at `$C07B`** |
| Loop | per-pattern wrap | **single `$FF` sentinel = restart from pos 1** |
| SFX channel | yes | **no** |
| Freq table | 96 entries (8 octaves) | 128 entries |

This engine is essentially **"play the same timbre per voice, walk a
flat list of pitches, loop at $FF."** It has fewer features than even
the simplest Hubbard tune.

## Scope estimate for the c8282844 cluster (7 SIDs)

Because the 7 SIDs share the EXACT 256-byte engine slice at init, the
engine model can be written ONCE and applied verbatim. Per-tune work
is only the data:

```
1. Extract:        ~3 hours
   - decode the 3 orderlists ($CB00, $CC00, $CD00) up to $FF
   - read freq tables ($CA00..$CB00)
   - read per-voice timbre ($C019-$C02A)
   - read tempo ($C07B)

2. Build engine model + codegen:  ~4-6 hours
   - the engine bytes can be embedded as a verbatim 263-byte blob
     (load to $C108 = $C003..$C107) — no per-tune codegen logic
     needed
   - codegen = stitch (engine bytes) + (per-voice timbre at $C019+) +
     (tempo at $C07B) + (freq tables at $CA00+) + (orderlists at
     $CB00/$CC00/$CD00)

3. USF representation:  ~2 hours
   - 3 flat orderlists of pitches with $80 = rest, $FF = loop
   - 3 timbre records (4 bytes each: pw_lo, pw_hi, ctrl, ad)
   - 1 tempo
   - 128-byte freq table (or share with engine constants)

4. First verify (Bach_Sonata):  ~2 hours
   - probably byte-exact on first try given the simplicity

5. Remaining 6 c8282844 SIDs:  ~1 hour each → 6 hours
   - same engine model, same codegen — just feed new extracted data
```

**Total: ~15-20 hours of focused work** for 7/26 Companion SIDs done.
Much less than the original "1 week" estimate — Bach_Sonata is simple
enough that the cluster's worth of work is genuinely small.

## Approach

Use `pipelines/companion/bowden_canonical/` as the strain dir.
Structure (parallels `pipelines/hubbard/<engine>/`):

```
pipelines/companion/bowden_canonical/
├── SURVEY.md            (this file)
├── disassembly.s        (auto-seed; needs hand annotation)
├── engine_blob.bin      (the 263-byte engine, $C003..$C107)
├── config.py            BowdenCanonicalConfig per-tune fields
├── engine_constants.py  the engine blob + freq table layout
├── codegen.py           stitch engine+data into a PSID
├── build_from_usf.py    USF → assembled SID
├── to_usf.py         USF v2 writer
└── extract/
    ├── engine_model.py  binary → (orderlists, timbre, tempo, freqs)
    └── to_usf.py
```

If we generalise later (e.g. the other 5 Vic Berry variants with
similar shape but different bytes), we factor out the shared parts
into a `pipelines/companion/_shared/` core. Premature for now.

## Open questions

1. **`$C108..` data layout.** I traced 211 reachable code bytes; the
   gap from `$C10C..$CDFE` (3315 bytes) is data. Need to identify
   exactly where the orderlists/freq tables/etc. start.
2. **`$FF` loop semantics.** The engine resets `v_pos = 1` then
   re-reads the first byte — but that means orderlist[0] is *never*
   replayed after the first loop. Is that intentional or am I
   misreading the disasm?
3. **Per-voice timbre is set ONCE at load.** No mechanism to change
   it during play. So all V1 notes share one timbre. (Vic Berry's
   classical-music aesthetic checks out — fixed timbres per voice
   is exactly how baroque/classical scoring works.)
4. **No instrument concept at the engine level.** The "instrument"
   in USF terms is the per-voice 4-byte block. There are exactly 3
   instruments per tune (one per voice). May need a USF-side
   convention to map cleanly.
