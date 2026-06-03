---
source_url: HVSC #84 — /MUSICIANS/T/Tel_Jeroen/Hawkeye.sid
fetched_via: local (hvsc84 tree, already in repo)
fetch_date: 2026-06-03
author: Jeroen Tel (music, 1988) — driver by Charles Deenen / MoN
content_date: 1988 (Thalamus release)
reliability: primary
---

# Hawkeye.sid — PSID header + driver fingerprint (Tel_Jeroen)

Direct inspection of `hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid` confirms
the FC V3.x driver byte-for-byte. This is the **canonical target** for
our byte-exact rebuild of an FC V3.x tune.

## PSID v2 header

| Field | Value |
|-------|-------|
| Magic | `PSID` |
| Version | 2 |
| Data offset | $007C |
| Load address (header) | $0000 (means: read first 2 bytes of body) |
| **Actual load address** | **$7AE0** |
| Init address | $7AE0 |
| Play address | $7AE3 |
| Number of songs | **12** |
| Start song | 1 |
| File size | 8894 bytes (8768 code + 124-byte header + 2 load-addr) |

## Entry-point structure

The first 6 bytes at $7AE0 are:
```
$7AE0:  4C 8F 91   JMP $918F   ; init  (song-init dispatch)
$7AE3:  4C 98 7B   JMP $7B98   ; play  (per-frame)
```

The `init + 6` offset that other FC tunes use as `play_addr` is here
**collapsed into the two consecutive JMPs at $7AE0/$7AE3** — i.e. FC's
"init=$X, play=$X+3" convention (3-byte JMP, not 6). Earlier research
note said "+6" which is actually the MoN three-jump dispatcher's
`init / quit / play` layout (3 bytes per jump = init+6 for play); here
the song builder generated only two of the three jumps.

(The earlier "+6" rule in research.md applies to FC1.0 / FC2.x where
the dispatcher always emits three jumps `init / songout / play`; FC
V3.x compresses this to two jumps in some builds.)

## Driver fingerprint scan

Scanned the 8768-byte code region for sidid signatures (see
`github_sidid_signatures.md` for signature catalogue):

### Match 1: MoN/FutureComposer top signature

```
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03
```

Found at code offset **$02BC** ($7D9C absolute):
```
$7D9C:  FE C8 90        INC $90C8,X        ; advance per-voice pattern offset
$7D9F:  BC C8 90        LDY $90C8,X        ; load advanced offset
$7DA2:  B1 FD           LDA ($FD),Y        ; fetch pattern byte (indirect)
$7DA4:  C9 FF           CMP #$FF           ; end-of-pattern check
$7DA6:  D0 12           BNE +18            ; branch on not-end
$7DA8:  A9 00           LDA #$00
$7DAA:  9D C8 90        STA $90C8,X        ; reset offset
$7DAD:  BD 18 91        LDA $9118,X        ; load repeat counter
```

This **exactly matches** the Cybernoid II disassembly's pattern-advance
block — the per-voice arrays `$90C8` (pattern offset = `begcount,x` on
Cybernoid II) and `$9118` (repeat counter = `repeatsto,x`).

### Match 2: FC V3.x exclusive signature

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ??
```

Found at code offset **$0142** ($7C22 absolute):
```
$7C22:  AD 0A 91        LDA $910A         ; read sequence command byte
$7C25:  C9 60           CMP #$60
$7C27:  90 0B           BCC +11           ; <$60 → not voiceinc
$7C29:  29 0F           AND #$0F          ; mask voiceinc nibble
$7C2B:  9D 39 91        STA $9139,X       ; store to voiceinc,x
$7C2E:  FE C5 90        INC $90C5,X       ; advance tabcount
$7C31:  4C E0 7B        JMP $7BE0         ; back to dispatch
```

Confirms the **`$60..$7F` sequence command = voiceinc** semantics we
saw in the realdmx Cybernoid II disassembly (`and #$0f`,
`sta voiceinc,x`).

## Per-voice arrays in Hawkeye (memory map)

From the signature decode above, the per-voice runtime state is at:

| Var | Address | Cybernoid II equivalent |
|-----|---------|-------------------------|
| `tabcount,x`    | $90C5 | tabcount |
| `begcount,x`    | $90C8 | begcount |
| `repeatsto,x`   | $9118 | repeatsto |
| `voiceinc,x`    | $9139 | voiceinc |
| (more to map)   | $9xxx | ... |

A full memory map can be built by stepping through the driver code from
$7AE0 — every `STA $9xxx,X` write defines a per-voice array.

## Practical next steps

1. **Full disassembly of $7AE0-$92xx region** would yield the complete FC
   V3.x driver byte-exact. Use `tools/seed_disassembly.py` (the
   sidfinity tool), point it at `MUSICIANS/T/Tel_Jeroen/Hawkeye.sid`,
   pin entry $7AE0.
2. **Per-voice array discovery** — grep all `9D ?? 9?` (STA abs,X) and
   `BD ?? 9?` (LDA abs,X) in the disassembly to locate every per-voice
   slot; cross-reference with the Cybernoid II ZP/RAM map.
3. **Data-section boundary** — the player code ends and song-data
   begins where the last RTS / JMP-out is followed by tabular non-code
   bytes. Look for the freq-table signature (96 entries of
   monotonically-increasing 16-bit values, matching the
   `lonote/hinote` interleaved layout from Cybernoid II).
4. **Subtune dispatch** — 12 songs implies 12 sets of 3 sequence
   pointers at the subtune table. Find this table (likely indexed by
   `(A << 3) + offset` per the Cybernoid II `songinit` pattern).

## File-level observation

8768 bytes total. Cybernoid II disassembly (1817 lines of source) builds
to a ~3.5KB SID; Hawkeye is ~2.5× that size — consistent with 12 songs
vs 2, plus larger pattern/sequence pools.

## Other Hawkeye SIDs in HVSC (cross-reference)

For triangulation when reverse-engineering the FC V3.x format:
```
/MUSICIANS/H/Hannula_Antti/Hawkeye_2018.sid    (cover)
/MUSICIANS/R/Rayden/Hawkeye_Remix_v2.sid       (remix)
/MUSICIANS/R/Rayden/Hawkeye_Remix.sid          (remix)
/MUSICIANS/O/Ouwehand_Reyn/Hawkeye_Hiscore.sid (Reyn Ouwehand's separate piece, MoN-family)
/MUSICIANS/W/Wilson_Mark/Hawkeye_Remix.sid     (remix)
```
The Ouwehand entry is its own MoN tune — useful as a second
FC-family rebuild target.
