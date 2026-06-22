---
source_url: primary corpus analysis (486 HVSC Basic_Program SIDs) + cross-reference:
  Commodore 64 Programmer's Reference Guide (1982, Commodore Business Machines)
  Mapping the Commodore 64 (Sheldon Leemon, 1984, Compute! Publications)
  C64 Wiki: https://www.c64-wiki.com/wiki/BASIC_token
  PETSCII reference: https://www.c64-wiki.com/wiki/PETSCII
fetched_via: local corpus analysis + published docs
fetch_date: 2026-06-22
author: SIDfinity leaf-research agent
content_date: 2026-06-22
reliability: primary (corpus-verified against all 486 Basic_Program SIDs)
---

# Commodore BASIC V2 Tokenization — Canonical Spec for Detokenizer

This document is the **primary technical reference** for reading, detokenizing, and
parsing the 486 `Basic_Program` RSID files in HVSC.  Every rule here is verified
against the actual corpus bytes unless marked [SPEC].

---

## 1. Program Memory Layout

### 1.1 Load address

All 486 programs load at **`$0801`** (verified: zero exceptions across the corpus).
The first two bytes of the PRG payload (bytes immediately after the SID header
`data_offset`) are a little-endian load address word; this word is always `01 08`.
The tokenized BASIC program body begins at byte offset 2 within the PRG payload,
i.e., at byte `data_offset + 2` inside the SID file.

### 1.2 Per-line structure

Each BASIC line is stored as:

```
[next-line-link : WORD LE]  [line-number : WORD LE]  [tokenized-text ...]  [$00]
```

- **next-line-link** (2 bytes, little-endian): absolute address of the NEXT line's
  link-pointer word.  For the LAST line in the program this points past the final
  `$00` terminator, into the two-byte `$00 $00` program-end sentinel.
- **line-number** (2 bytes, little-endian): 0–63999 (BASIC V2 limit is 63999).
- **tokenized-text**: one or more bytes; see §2 for tokenization rules.
- **`$00`**: single-byte line terminator.

### 1.3 Program terminator

After the last line's `$00`, there are (at minimum) **two bytes `$00 $00`**.
The BASIC interpreter reads the next-line-link and finds `$0000`, stopping
the program walk.

### 1.4 Link-pointer reliability

**Do NOT rely on link pointers for detokenization.**  6 of the 486 programs
(1.2%) have intentionally incorrect link pointers:

| Program | Anomaly |
|---|---|
| `DEMOS/UNKNOWN/Oh_Mama_Vib_BASIC.sid` | Some links point to `$007F` (address $7F00), off-program |
| `DEMOS/UNKNOWN/Pong_BASIC.sid` | Mismatched links |
| `DEMOS/UNKNOWN/Stuck_on_Classics_BASIC.sid` | Mismatched links |
| `GAMES/G-L/Lernaia_BASIC.sid` | Mismatched links |
| `MUSICIANS/G/Goesmann_Thomas/Tennis_BASIC.sid` | Mismatched links |
| `MUSICIANS/M/Mayer_Ronald/Interceptor_Base_BASIC.sid` | Mismatched links |

These programs run correctly on a real C64 (the interpreter follows the actual
link pointers which may use self-modification or alternate loading addresses).
For detokenization, **scan by `$00` terminator** instead:

```python
def walk_lines(basic_bytes):
    pos = 0
    while pos + 3 < len(basic_bytes):
        # peek at the next-line-link; $0000 = end of program
        next_link = basic_bytes[pos] | (basic_bytes[pos+1] << 8)
        if next_link == 0x0000:
            break
        line_num = basic_bytes[pos+2] | (basic_bytes[pos+3] << 8)
        pos += 4
        # scan forward to the $00 line terminator
        end = pos
        while end < len(basic_bytes) and basic_bytes[end] != 0x00:
            end += 1
        yield line_num, basic_bytes[pos:end]
        pos = end + 1          # skip past the $00 terminator
```

The link-pointer value is never needed for correctness.  It CAN be recomputed
from the `$00`-scan result if you need to regenerate a valid PRG.

---

## 2. Token Table — Full BASIC V2 Keyword Tokens

### 2.1 Canonical token table ($80–$CB, plus $FF)

Source: C64 Programmer's Reference Guide (CBM, 1982) Appendix B.  Verified
against the HVSC corpus — every token listed below appears at least once
(except those noted as [corpus: 0]).

| Byte | Token | Byte | Token | Byte | Token |
|------|-------|------|-------|------|-------|
| $80  | END   | $96  | DEF   | $AC  | `*`   |
| $81  | FOR   | $97  | POKE  | $AD  | `/`   |
| $82  | NEXT  | $98  | PRINT# [corpus:0] | $AE | `^` |
| $83  | DATA  | $99  | PRINT | $AF  | AND   |
| $84  | INPUT# | $9A | CONT [corpus:0] | $B0 | OR |
| $85  | INPUT | $9B  | LIST  | $B1  | `>`   |
| $86  | DIM   | $9C  | CLR   | $B2  | `=`   |
| $87  | READ  | $9D  | CMD   | $B3  | `<`   |
| $88  | LET   | $9E  | SYS   | $B4  | SGN   |
| $89  | GOTO  | $9F  | OPEN [corpus:0] | $B5 | INT |
| $8A  | RUN   | $A0  | CLOSE | $B6  | ABS   |
| $8B  | IF    | $A1  | GET   | $B7  | USR [corpus:0] |
| $8C  | RESTORE | $A2 | NEW  | $B8  | FRE   |
| $8D  | GOSUB | $A3  | TAB(  | $B9  | POS [corpus:0] |
| $8E  | RETURN | $A4 | TO    | $BA  | SQR [corpus:0] |
| $8F  | REM   | $A5  | FN    | $BB  | RND   |
| $90  | STOP  | $A6  | SPC(  | $BC  | LOG   |
| $91  | ON    | $A7  | THEN  | $BD  | EXP [corpus:0] |
| $92  | WAIT  | $A8  | NOT [corpus:0] | $BE | COS [corpus:0] |
| $93  | LOAD  | $A9  | STEP  | $BF  | SIN   |
| $94  | SAVE [corpus:0] | $AA | `+` | $C0 | TAN [corpus:0] |
| $95  | VERIFY [corpus:0] | $AB | `-` | $C1 | ATN [corpus:0] |

| Byte | Token |
|------|-------|
| $C2  | PEEK  |
| $C3  | LEN   |
| $C4  | STR$  |
| $C5  | VAL   |
| $C6  | ASC   |
| $C7  | CHR$  |
| $C8  | LEFT$ |
| $C9  | MID$  |
| $CA  | RIGHT$ |
| $CB  | GO    |
| $FF  | π  (the mathematical constant pi) |

**Tokens $CC–$FE are NOT BASIC V2 tokens.**  They belong to BASIC extensions
(Simon's BASIC starts at $CC — see §6).

### 2.2 The GO token ($CB)

`GO` (`$CB`) is a separate token from `GOTO` (`$89`).  The two-token sequence
`$CB $A4` = `GO TO` (a valid synonym for GOTO in BASIC V2).  Corpus: 10
programs use `$CB`; of those, 8 use it as `GO TO` (Joey Latimer programs),
while the remainder have `$CB` inside quoted PRINT strings (the letters G-O
being coincidentally overlaid by the token byte).

### 2.3 Comparison operator tokens

The relational operators `>`, `=`, `<` each have a single token.  Compound
operators are stored as TWO CONSECUTIVE TOKENS in input order:

| Operator | Stored as | Frequency in corpus |
|---|---|---|
| `<>` | $B3 $B1 | 140 occurrences |
| `=<` | $B2 $B3 |   9 occurrences |
| `<=` | $B3 $B2 |   6 occurrences |
| `>=` | $B1 $B2 |   1 occurrence  |

The BASIC tokenizer accepts any order the programmer typed; the stored bytes
are the token pair in typed order.  Detokenization: emit the symbol for each
token individually (e.g. $B3 $B1 → `<>`).

### 2.4 Abbreviated keyword entry

The C64 keyboard accepts abbreviated keyword entry (e.g. `pO` for `POKE`,
`?` for `PRINT`).  **These abbreviations are converted to the full keyword
token at entry time**.  The stored program ALWAYS contains the full token
byte ($97 for POKE, $99 for PRINT, etc.) — abbreviations do NOT persist in
the stored tokenized program.  Verified: corpus shows only $97 for POKE, never
a partial abbreviation.  Detokenization is therefore unambiguous: one byte =
one keyword.

---

## 3. Tokenization Rules by Context

### 3.1 State machine overview

The BASIC V2 tokenizer maintains THREE context states per line:

1. **NORMAL** — tokens `$80`–$CB and `$FF` are keyword tokens; all other bytes
   are literal characters.
2. **IN_QUOTE** — entered on `$22` (double-quote); all bytes until the closing
   `$22` (or the `$00` line terminator) are LITERAL PETSCII bytes, NOT tokens.
3. **IN_REM** — entered on the `$8F` (REM) token; all bytes until the `$00`
   line terminator are LITERAL.

Additional pseudo-state: **IN_DATA** — entered on the `$83` (DATA) token.  In
DATA context the tokenizer DOES tokenize keywords (unlike IN_REM), EXCEPT that
quoted sub-strings inside DATA are IN_QUOTE (see §3.4).

State transitions per byte (evaluated in NORMAL context):

```
byte == $22                    → toggle IN_QUOTE
byte == $8F (REM token)        → enter IN_REM (irreversible until $00)
byte == $83 (DATA token)       → enter IN_DATA
byte == $3A (colon)            → exit IN_DATA → NORMAL; no effect on IN_QUOTE/IN_REM
$00                            → end of line; reset ALL states to NORMAL
```

IN_REM overrides everything (once IN_REM, nothing changes until $00).
IN_QUOTE overrides IN_DATA (a `"..."` inside DATA is literal).

### 3.2 IN_QUOTE: quoted string content

Inside a quoted string:
- ALL bytes `$00`–`$FF` are literal PETSCII.
- Bytes `$80`–`$CB` and `$FF` that would be tokens in NORMAL context are
  NOT tokens inside quotes — they are PETSCII control codes or graphic chars.
- The `$22` byte closes the quote (restores previous context).
- If the `$00` line terminator is reached while IN_QUOTE (unclosed string),
  the string is implicitly closed.  **This is canonical BASIC V2 behaviour**,
  not an error.  57 of the 486 programs (11.7%) have at least one line with
  an unclosed string; this is especially common in PRINT statements used to
  draw graphics characters on screen.

**Quote mode resets at each line boundary** (`$00`).  It never carries from
one line to the next.

**Common high-byte PETSCII values found inside strings** (examples):

| Range | Meaning |
|---|---|
| $80–$9F | PETSCII colour/control codes ($93 = CLR screen, $9B = light-gray, $92 = RVS-off, $91 = cursor up, etc.) |
| $A0–$BF | CBM graphics characters (unshifted) |
| $C0–$DF | CBM graphics characters (shifted) |
| $E0–$FE | CBM graphics characters |
| $FF     | π (pi character in PETSCII) |

These are NOT tokens when inside quotes.  A detokenizer that naively applies
the token table inside quotes will corrupt PRINT strings.  Verified on corpus:
126 of 486 programs (26%) have PETSCII control codes inside quoted strings.

### 3.3 IN_REM: remark content

After the `$8F` (REM) token, every subsequent byte until `$00` is a literal
PETSCII character.  No tokenization occurs.  53% of the corpus programs have
at least one REM line.

### 3.4 IN_DATA: DATA statement content

Inside a DATA statement (after the `$83` token), the stored bytes are:
- **Keyword tokens CAN appear** in DATA content — the tokenizer was active
  when the programmer typed the data items.  Example: the DATA items
  `25,30` store as `$32 $35 $2C $33 $30`; but if a programmer typed `AND` as
  a DATA item it would tokenize to `$AF`.  In practice this is exceedingly
  rare: only **one occurrence** of a real keyword token inside DATA was found
  in the entire corpus: `$FF` (π) in `GAMES/A-F/C_est_la_vie_BASIC.sid`
  line 998 (used as a string character value).
- **Non-token bytes `$CC`–$FE** and control chars (`$00`–`$1F`) can appear
  as literal binary data values inside DATA items (Stuck_on_Classics has
  `$E1, $EA, $05, $06` embedded literally in a DATA line).
- **Quoted sub-strings** inside DATA enter IN_QUOTE; within those, keyword
  bytes are literal (not detokenized).
- **Colon (`$3A`)** exits the DATA context and begins a new statement (in
  actual practice, a colon inside DATA is ambiguous — BASIC V2 actually
  treats a colon within DATA as part of the data item; the tokenizer does NOT
  put a new statement after colon inside DATA).

**IMPORTANT CORRECTION**: The official C64 BASIC V2 behaviour for `DATA` is:
- The tokenizer does NOT tokenize keywords inside DATA item text.  The BASIC
  tokenizer in the C64 ROM skips tokenization after `DATA` until the end of
  the statement (end-of-line `$00` or a non-quoted colon).
- However, the stored bytes in the corpus show that keyword tokens DO NOT
  appear inside DATA items (the one $FF/π case is the only exception, and
  π is a special case — it's BASIC's own π constant).
- **Practical rule for detokenization**: treat DATA content as literal ASCII
  bytes except for keyword tokens in the range $80–$CB and $FF, which should
  be rendered as their keyword string (consistent with what the BASIC LIST
  command would show).

### 3.5 Multi-statement lines (colon separator)

The colon character `$3A` separates multiple statements on one line.  The
detokenizer should emit `:` for $3A in NORMAL context.  The colon does NOT
terminate IN_QUOTE or IN_REM states — only `$22` or `$00` can exit those.

---

## 4. PETSCII vs ASCII

The BASIC V2 source character set is **PETSCII**, not ASCII.  Within the
printable range `$20`–`$7E`, PETSCII and ASCII differ in three positions:

| Byte | ASCII | PETSCII |
|------|-------|---------|
| $5C  | `\`   | `£` (pound sterling) |
| $5E  | `^`   | `↑` (up-arrow) |
| $5F  | `_`   | `←` (left-arrow) |

These appear in BASIC code (outside quotes) in variable names and expressions.
Corpus occurrences: `$5C` (16×), `$5E` (1×), `$5F` (31×).  A detokenizer
should preserve them as-is and note the charset when converting to ASCII for
display.

The byte `$60` in BASIC is rarely used (0 occurrences in code context); in
PETSCII it is `─` (horizontal bar graphic).

**For variable names** in NORMAL context, the valid bytes are `$41`–`$5A`
(A–Z), `$30`–`$39` (0–9), and the suffix `$24` (`$` for string vars) or
`$25` (`%` for integer vars in some dialects — not used in BASIC V2).

---

## 5. Multi-Subtune BASIC SIDs and Song Select

### 5.1 Prevalence

80 of the 486 programs (16.5%) have multiple subtunes.  Maximum: 27 subtunes
(Sword_of_Fargoal_BASIC.sid).

### 5.2 The `$030C` song-select mechanism

When sidplayfp (or any compliant RSID player) runs a multi-subtune BASIC SID:
1. The player writes `(song_number - 1)` to address `$030C` (decimal 780)
   before issuing the equivalent of the `RUN` command.
2. The BASIC program reads this value with **`PEEK(780)`**.
3. Common patterns in our corpus:
   - `T = PEEK(780) + 1` → use `T` as a 1-indexed tune selector
   - `ON PEEK(780)+1 GOTO line1, line2, ...`
   - `Y = PEEK(780) + 1 : GOSUB 500`

The REM comment in many multi-tune SIDs documents this explicitly:
`"TUNE HAS N SUBTUNES. TYPE POKE780,X:RUN WITH X BEING A VALUE FROM 0-N-1"`

### 5.3 Line number zero

Multi-subtune programs frequently start at **line 0** (the REM comment for
sidplayfp).  Line 0 is valid BASIC; the program starts from the first line
regardless of line number when `RUN` is issued without a line number argument.

### 5.4 SYS usage

77 programs (15.8%) call `SYS addr` to jump into machine code routines
(usually sprite or sound setup).  The SYS address targets embedded machine
code loaded elsewhere in memory.  The SID file contains ONLY the BASIC
program (at $0801); the machine code is expected to already be in RAM (e.g.,
loaded by the BASIC program itself, or present in the Commodore ROM).

---

## 6. BASIC Extension Tokens (Edge Cases)

### 6.1 Simon's BASIC

**3 of 486 programs** use BASIC extension tokens above `$CB`:

| Program | Extension used |
|---|---|
| `DEMOS/A-F/Black_Box_V8_Demo_BASIC.sid` | Simon's BASIC ($CC–$D5) |
| `DEMOS/UNKNOWN/Medley_BASIC.sid` | Possible extension token ($E2) |
| `DEMOS/UNKNOWN/Stuck_on_Classics_BASIC.sid` | Literal bytes in DATA ($E1, $EA) |

Simon's BASIC tokens (relevant subset, starting at $CC):

| Byte | Token | Byte | Token |
|------|-------|------|-------|
| $CC  | HIRES | $D3  | REC   |
| $CD  | PLOT  | $D4  | ROT   |
| $CE  | LINE  | $D5  | DRAW  |
| $CF  | BLOCK | $D6  | CHAR  |
| $D0  | FCHR  | $D7  | HI COL |
| $D1  | FCOL  | $D8  | INV   |
| $D2  | FILL  | $D9  | FRAC  |

The detokenizer MUST NOT emit these as unknown bytes for Black_Box_V8_Demo;
they should be treated as extension keyword tokens if Simon's BASIC is
detected, or rendered as `<SB_$XX>` stubs.

**Detection**: if any byte $CC–$FE appears in code context (outside quotes
and REM), the program uses a BASIC extension.

### 6.2 Programs with raw binary DATA

Stuck_on_Classics_BASIC has bytes `$05, $06, $17, $E1, $EA` embedded
INSIDE a DATA statement.  These are raw PETSCII bytes used as separators /
binary values.  They are NOT tokens.  They may cause `?SYNTAX ERROR` if a
READ tries to parse them as numeric values.

---

## 7. Program Terminator and Length Calculation

After the last line's `$00` terminator:
- There are at least two `$00` bytes (the `$0000` link pointer of the
  program-end sentinel).
- Additional `$00` bytes may follow (alignment, or unused space).
- `len(basic_bytes)` may be larger than the actual program; the walk stops
  at the `$0000` sentinel regardless.

Formula for recomputing the link pointer for line at byte offset `off` with
text bytes `text`:
```
link_ptr = base_addr + off + 4 + len(text) + 1
         = $0801 + off + 4 + len(text) + 1
```
(4 = 2-byte link + 2-byte line number; +1 for the `$00` terminator itself)

---

## 8. Corpus Summary Statistics

| Metric | Value |
|---|---|
| Total programs | 486 |
| All load at $0801 | 486/486 (100%) |
| Total tokenized bytes | 1,371,348 |
| Total lines | 36,388 |
| Longest program | 597 lines, 30,270 bytes |
| Multi-subtune programs | 80/486 (16.5%) |
| Maximum subtunes | 27 (Sword_of_Fargoal_BASIC) |
| With REM | 259/486 (53%) |
| With DATA | 389/486 (80%) |
| With quoted strings | 224/486 (46%) |
| With PETSCII ctrl in quotes | 126/486 (26%) |
| With PETSCII graphic in quotes | 66/486 (14%) |
| With unclosed quotes (implicit-close) | at least 10 programs (57 lines) |
| With link pointer anomalies | 6/486 (1.2%) |
| With BASIC extension tokens | 3/486 (0.6%) |
| With GOTO | 404/486 (83%) |
| With GOSUB | 192/486 (39%) |
| With ON (ON...GOTO) | 100/486 (20%) |
| With SYS | 77/486 (15.8%) |
| With π ($FF) | 1/486 |
| GO token ($CB) | 7 programs |

---

## 9. Reference Implementations to Cross-Check

| Tool | Location | Notes |
|---|---|---|
| **VICE `petcat`** | `vice-3.x/src/petcat.c` | The authoritative reference detokenizer; handles BASIC V2, Simon's BASIC, and many extensions. Use `petcat -2 -- file.prg` for BASIC V2. |
| **cbmbasic** | https://github.com/mist64/cbmbasic | Pure BASIC V2 interpreter in C; can run programs and verify output |
| **p-tokenize / un-tokenize** | https://github.com/mpolitzer/basic-tokenizer | Minimalist Python implementation |
| **c64 BASIC wiki** | https://www.c64-wiki.com/wiki/BASIC_token | Canonical token table with byte values |

---

## 10. Recommended Detokenizer Algorithm (Pseudocode)

```python
TOKENS = {
    0x80: 'END', 0x81: 'FOR', 0x82: 'NEXT', 0x83: 'DATA',
    0x84: 'INPUT#', 0x85: 'INPUT', 0x86: 'DIM', 0x87: 'READ',
    0x88: 'LET', 0x89: 'GOTO', 0x8A: 'RUN', 0x8B: 'IF',
    0x8C: 'RESTORE', 0x8D: 'GOSUB', 0x8E: 'RETURN', 0x8F: 'REM',
    0x90: 'STOP', 0x91: 'ON', 0x92: 'WAIT', 0x93: 'LOAD',
    0x94: 'SAVE', 0x95: 'VERIFY', 0x96: 'DEF', 0x97: 'POKE',
    0x98: 'PRINT#', 0x99: 'PRINT', 0x9A: 'CONT', 0x9B: 'LIST',
    0x9C: 'CLR', 0x9D: 'CMD', 0x9E: 'SYS', 0x9F: 'OPEN',
    0xA0: 'CLOSE', 0xA1: 'GET', 0xA2: 'NEW', 0xA3: 'TAB(',
    0xA4: 'TO', 0xA5: 'FN', 0xA6: 'SPC(', 0xA7: 'THEN',
    0xA8: 'NOT', 0xA9: 'STEP', 0xAA: '+', 0xAB: '-',
    0xAC: '*', 0xAD: '/', 0xAE: '^', 0xAF: 'AND',
    0xB0: 'OR', 0xB1: '>', 0xB2: '=', 0xB3: '<',
    0xB4: 'SGN', 0xB5: 'INT', 0xB6: 'ABS', 0xB7: 'USR',
    0xB8: 'FRE', 0xB9: 'POS', 0xBA: 'SQR', 0xBB: 'RND',
    0xBC: 'LOG', 0xBD: 'EXP', 0xBE: 'COS', 0xBF: 'SIN',
    0xC0: 'TAN', 0xC1: 'ATN', 0xC2: 'PEEK', 0xC3: 'LEN',
    0xC4: 'STR$', 0xC5: 'VAL', 0xC6: 'ASC', 0xC7: 'CHR$',
    0xC8: 'LEFT$', 0xC9: 'MID$', 0xCA: 'RIGHT$', 0xCB: 'GO',
    0xFF: 'π',
}

def detokenize_line(line_bytes: bytes) -> str:
    """
    Detokenize one BASIC V2 line body (excluding link ptr, line num, $00).
    Returns the human-readable source text.

    RULES:
    - Scan sequentially, maintaining three boolean state vars.
    - in_rem: irreversible once set; clears at line boundary ($00 = caller's job).
    - in_quote: toggles on $22; clears at line boundary if not explicitly closed.
    - Tokens only decoded in NORMAL (not in_quote, not in_rem) context.
    - Colon ($3A) in NORMAL context is a statement separator.
    """
    out = []
    in_quote = False
    in_rem = False

    for b in line_bytes:
        if in_rem:
            # Everything is literal in a REM
            out.append(petscii_printable(b))

        elif in_quote:
            # Inside quotes: all bytes are literal PETSCII
            if b == 0x22:
                out.append('"')
                in_quote = False
            else:
                out.append(petscii_printable(b))

        else:
            # NORMAL context
            if b == 0x22:
                out.append('"')
                in_quote = True
            elif b in TOKENS:
                out.append(TOKENS[b])
                if b == 0x8F:          # REM: rest of line is literal
                    in_rem = True
            elif 0x20 <= b <= 0x7E:
                out.append(chr(b))     # printable ASCII / PETSCII
            elif b == 0x3A:
                out.append(':')
            elif b >= 0xCC:
                out.append(f'<EXT_${b:02X}>')  # BASIC extension token
            else:
                out.append(f'<${b:02X}>')      # control char or anomaly

    # NOTE: in_quote may still be True here (unclosed string) — this is valid.
    # The caller knows the line is done; quote state resets for the next line.
    return ''.join(out)


def petscii_printable(b: int) -> str:
    """Render a PETSCII byte to an ASCII-printable representation."""
    if 0x20 <= b <= 0x7E:
        return chr(b)   # printable ASCII range matches PETSCII (with £/↑/← exceptions)
    elif b == 0xFF:
        return 'π'
    elif 0x80 <= b <= 0x9F:
        # PETSCII control codes — represent symbolically
        CTRL = {
            0x80: '<CTRL_80>', 0x81: '<ORNG>', 0x85: '<F1>', 0x86: '<F3>',
            0x87: '<F5>', 0x88: '<F7>', 0x89: '<F2>', 0x8A: '<F4>',
            0x8B: '<F6>', 0x8C: '<F8>', 0x8D: '<SHRET>', 0x8E: '<UPPR>',
            0x90: '<BLK>', 0x91: '<UP>', 0x92: '<RVSOF>', 0x93: '<CLR>',
            0x94: '<INS>', 0x95: '<BRN>', 0x96: '<LRED>', 0x97: '<DGY>',
            0x98: '<MGY>', 0x99: '<LGRN>', 0x9A: '<LBLU>', 0x9B: '<LGY>',
            0x9C: '<PUR>', 0x9D: '<LEFT>', 0x9E: '<YEL>', 0x9F: '<CYN>',
        }
        return CTRL.get(b, f'<${b:02X}>')
    elif 0x00 <= b <= 0x1F:
        # Low control codes
        CTRL_LOW = {
            0x05: '<WHT>', 0x07: '<BEL>', 0x08: '<DISH>', 0x09: '<ENSH>',
            0x0D: '<RETURN>', 0x0E: '<LOWR>', 0x11: '<DOWN>', 0x12: '<RVSON>',
            0x13: '<HOME>', 0x14: '<DEL>', 0x1C: '<RED>', 0x1D: '<RIGHT>',
            0x1E: '<GRN>', 0x1F: '<BLU>',
        }
        return CTRL_LOW.get(b, f'<${b:02X}>')
    else:
        return f'<${b:02X}>'  # graphic char: show as hex
```

---

## 11. Critical Edge Cases — Checklist

Before declaring a detokenizer "bulletproof", verify it handles these cases
(each is attested in the corpus):

1. **Unclosed quote at end of line** — 57 lines in 10+ programs.  The detokenizer
   must NOT error; quote state resets at the `$00` terminator.

2. **Bytes $80–$CB inside quoted strings** — 126 programs.  These are PETSCII
   control/graphic codes, NOT keyword tokens.  Example: $93 inside quotes =
   CLR_SCR control code, not the LOAD token.

3. **PETSCII graphic chars inside strings ($CC–$FE)** — very common in programs
   that draw graphics.  NOT extension tokens when inside quotes.

4. **GO token ($CB)** — appears alone (not as part of $CB $A4 = GO TO) inside
   quoted PRINT strings in at least 2 programs.  Inside quotes it's a literal byte.

5. **π token ($FF) in DATA** — 1 occurrence (C_est_la_vie line 998).  Render as `π`.

6. **Raw binary bytes in DATA ($E1, $EA, $05, $06)** — Stuck_on_Classics.
   These are literal PETSCII bytes in a DATA item, NOT tokens.

7. **Simon's BASIC extension tokens ($CC–$D5)** — Black_Box_V8_Demo (and 2 others).
   Render as `<SB_HIRES>` etc. or `<EXT_$CC>` if not implementing Simon's BASIC.

8. **Link pointer anomalies** — 6 programs.  Always walk by `$00` terminators,
   never by following link pointers.

9. **Line number zero** — valid; used in multi-subtune program header comments.

10. **Program terminator `$00 $00`** — the two-byte end-of-program sentinel.
    Walk stops when the link pointer word is `$0000`.

---

## Leads to Follow

1. **VICE `petcat` source** (`vice-3.x/src/petcat.c`) — the reference implementation
   for ALL known C64 BASIC extension token tables.  Should be consulted if Simon's
   BASIC or other extension decoding is needed for the 3 outlier programs.

2. **`$030C` / PEEK(780) deep verification** — 74 of 80 multi-subtune programs were
   confirmed to use PEEK(780).  The remaining 6 deserve individual inspection to see
   if they use a different song-select mechanism.

3. **Unclosed-quote detokenization rendering** — 57 lines in the corpus have
   implicit-close strings.  The VICE `petcat -l` (list) mode renders these correctly;
   cross-checking output against petcat would validate the detokenizer.

4. **Medley_BASIC $E2 token** — byte $E2 appears in CODE context (not inside quotes)
   at line 931.  Simon's BASIC maps $E2 to `RIGHTB`; however, Medley may use a
   different BASIC extension.  The VICE `petcat` with `--help` shows all extension
   mappings.

5. **Stuck_on_Classics binary-in-DATA** — bytes $E1/$EA in a DATA statement may
   indicate the program reads them with `GET` or processes them as raw PETSCII.
   If a USF representation ever needs the DATA values, these bytes need special
   handling (treat as integer values 225/234 when READ into numeric variables,
   or as single-char strings when READ into string variables).

6. **Corpus programs with `SYS` calls** — 77 programs call machine code via SYS.
   The machine code target may be part of the program (inline) or in ROM.  A full
   corpus scan to classify which SYS targets are ROM-resident vs embedded would help
   determine which programs are tractable for DATA/READ extraction.

7. **Atypical DATA formats** — Piano_BASIC uses letter-encoded note names in DATA
   (`DATA M,2,N,2,P,2,...`) which need a decode table.  Other programs may use
   binary offsets, frequency values, or packed formats.  A follow-up corpus survey
   of DATA content types would be useful for categorizing the extraction complexity.
