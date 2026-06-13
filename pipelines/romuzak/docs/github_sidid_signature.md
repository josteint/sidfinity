---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (primary), https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg (cross-ref)
fetched_via: direct
fetch_date: 2026-06-13
author: cadaver (Lasse Öörni); signature contributors: Ian CooG, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos
content_date: current (living file)
reliability: primary
---

# SIDId signature blocks for RoMuzak

## cadaver/sidid — sidid.cfg

Two distinct entries, one per major version branch:

```
RoMuzak_V6.x
C9 ?? F0 ?? 0A 8D ?? ?? 0A 6D ?? ?? AA A0 00

RoMuzak_V7.x
C9 ?? F0 ?? 48 29 07 0A 8D ?? ?? 0A 6D ?? ?? AA A0
```

### WilfredC64/player-id — config/sidid.cfg (confirmed same content)

The Rust rewrite of player-id (https://github.com/WilfredC64/player-id) uses the same `config/sidid.cfg`
format as cadaver/sidid, and confirmed identical entries for both RoMuzak variants.

---

## sidid.nfo metadata for both entries

From `sidid.nfo` (cadaver/sidid):

```
NAME:      RoMuzak_V6.x
AUTHOR:    Oliver Blasnik (ROM)
RELEASED:  1989 Digital Marketing
REFERENCE: https://csdb.dk/release/?id=17814
COMMENT:   (none)

NAME:      RoMuzak_V7.x
AUTHOR:    Oliver Blasnik (ROM)
RELEASED:  (not specified in nfo — CSDb gives 1990-03-15)
REFERENCE: https://csdb.dk/release/?id=17819
COMMENT:   (none)
```

---

## Signature decode: what 6502 instructions do these bytes represent?

### V6.x pattern: `C9 ?? F0 ?? 0A 8D ?? ?? 0A 6D ?? ?? AA A0 00`

```
C9 ??        CMP #imm       ; compare A with some immediate
F0 ??        BEQ rel        ; branch if equal (skip over next)
0A           ASL A          ; shift A left (multiply note index × 2)
8D ?? ??     STA abs        ; store intermediate to abs address
0A           ASL A          ; shift left again (×2 more, so ×4 total from orig)
6D ?? ??     ADC abs        ; add abs (second table multiply step)
AA           TAX            ; transfer result to X (table index)
A0 00        LDY #$00       ; Y = 0 (first voice / channel select)
```

This is a note-to-frequency-table index computation. The CMP + BEQ suggest a "rest or tie" sentinel check
before the multiply-and-lookup. The `ASL / ADC abs` double-step is a classic 6502 multiply-by-3 or
multiply-by-2 + add pattern to reach a 2-byte pointer table or 2-byte freq-table entry.

### V7.x pattern: `C9 ?? F0 ?? 48 29 07 0A 8D ?? ?? 0A 6D ?? ?? AA A0`

```
C9 ??        CMP #imm       ; same sentinel check
F0 ??        BEQ rel        ; branch if sentinel
48           PHA            ; push A  <-- NEW in V7
29 07        AND #$07       ; mask low 3 bits  <-- NEW: octave/semitone split
0A           ASL A          ; then same multiply steps ...
8D ?? ??     STA abs
0A           ASL A
6D ?? ??     ADC abs
AA           TAX
A0           LDY #imm       ; (next byte not captured — probably #$00 or voice-offset)
```

The V7 addition of `PHA` + `AND #$07` before the multiply sequence indicates a changed note encoding:
V7 packs more information into the note byte (semitone in low 3 bits, octave or effect in upper bits)
and masks before the freq-table lookup. V6 used the raw note byte directly.

**Key discriminator:** `48 29 07` at offset +4 from the CMP is present only in V7.x.

---

## sidid.c scan methodology

(Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.c)

- **Scan scope:** entire file buffer from byte 0 to end. No fixed offset relative to SID load address.
- **Wildcard `??`:** parsed to internal token `ANY`; during matching, `ANY` advances both buffer and
  pattern pointers unconditionally (matches any byte).
- **Matching algorithm:** `identifybytes()` — sequential scan with backtrack. Uses saved positions
  `rc`/`rd` on mismatch. `AND` token in cfg allows multi-clause AND patterns (both must match).
- **Implication for RoMuzak:** the signature can appear anywhere in the binary; sidid does not
  require it at a fixed SID-relative offset. For RoMuzak the signature will always fall inside the
  player code region (not the PSID header).

---

## Confirmed known offset: "ROMUZAK89" at entry+$09

From `pipelines/romuzak/docs/research.md` (existing project note, derived separately):

> +$0009: Signature string `"ROMUZAK89"` (9 bytes)

This is the ASCII string embedded at byte offset +$09 from the SID load/entry point.
The sidid byte patterns above are from the *player code* region (not this string), confirming
sidid detects RoMuzak by player code structure rather than the embedded string.

Cross-reference: the Polish C64 scene forum (https://www.c64scene.pl/viewtopic.php?t=112) quotes
the in-binary header string as: `** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!!`
This appears to be the human-readable banner, longer than just "ROMUZAK89" — likely at a different
offset or the $09 string is the compact machine-readable tag before the longer text.

---

## Version summary

| Variant     | CSDb ID | Year | Load addr (typical) | Key discriminator bytes (sidid) |
|-------------|---------|------|---------------------|---------------------------------|
| V6.3        | 17814   | 1989 | $8000               | `C9 ?? F0 ?? 0A 8D ?? ??`       |
| V7.96       | 17819   | 1990 | $7000               | `C9 ?? F0 ?? 48 29 07 0A`       |

V7 adds `PHA` + `AND #$07` before the note-to-frequency multiply — indicates a note byte
encoding change (semitone packed differently).

---

## Leads to follow

- **OPEN (RE needed):** Confirm exact byte offset of the `C9 ??` sequence relative to the SID
  load address ($8000 / $7000). The sidid scan is position-independent — knowing the offset
  helps anchor the disassembly.
- **OPEN (RE needed):** Determine what the `??` wildcards conceal — is the CMP immediate the
  rest/tie sentinel value? Is it a fixed constant across all tunes or tune-specific?
- **OPEN (RE needed):** Does V7's `AND #$07` mean the note byte now encodes octave + semitone
  packed (3 bits semitone + upper bits octave), or is it a mask on an effect flag?
- **OPEN:** No sidid COMMENT fields — no one has documented additional format notes in that file.
  Could file an issue or PR to cadaver/sidid to add COMMENT fields once format is understood.
- **OPEN:** Fetch the actual D64 from Archive.org
  (https://archive.org/details/d64_Romuzak_Music_Demo-Editor_1989_ACT_501) and extract the
  PRG binary — this is the editor itself, which will contain the player + format documentation
  in-binary. Requires a D64 extraction tool (no emulator needed).
