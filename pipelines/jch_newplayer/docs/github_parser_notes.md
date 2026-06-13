<!--
source_url:
  - libsidplayfp:  https://github.com/libsidplayfp/libsidplayfp  (local: tools/libsidplayfp/src/sidtune/)
  - sidid:         https://github.com/cadaver/sidid  (sidid.cfg, readme.txt)
  - player-id:     https://github.com/WilfredC64/player-id
local: tools/libsidplayfp/src/sidtune/  (read-only; the libsidplayfp this repo's siddump links against)
fetched_via: local read-only grep (Bash) for libsidplayfp; WebFetch of raw sidid.cfg + readme.txt; WebSearch for player-id
fetch_date: 2026-06-13
author: libsidplayfp (Simon White, Leandro Nini, et al.); sidid (Cadaver); player-id (Wilfred Bos)
content_date: sidid.cfg/readme current master; libsidplayfp as vendored in tools/
reliability: PRIMARY for libsidplayfp source + sidid.cfg signature bytes; SECONDARY (search summary) for player-id corpus description
-->

# libsidplayfp / sidtune handling + canonical JCH player-ID signatures

## 1. libsidplayfp has NO JCH-specific handling (confirmed locally)

The libsidplayfp that this repo's `tools/siddump` links against
(`tools/libsidplayfp/src/sidtune/`) is **engine-agnostic**. A grep for any
JCH/NewPlayer/playroutine/engine-name string across `src/sidtune/` and
`src/sidplayfp/` returns nothing:

```
$ grep -riE 'jch|newplayer|new_player|playroutine|engine.*name' \
      tools/libsidplayfp/src/sidtune/ tools/libsidplayfp/src/sidplayfp/
   (no matches)
```

`PSID.cpp` loads a tune purely from the PSID/RSID header — load/init/play addresses
plus a flat copy of the C64 data — and then runs it on the emulated 6502/SID. There
is no per-engine dispatch, table parsing, or fingerprinting anywhere in the loader:

```cpp
// PSID.cpp
info->m_loadAddr       = pHeader.load;     // from header bytes
info->m_initAddr       = pHeader.init;
info->m_playAddr       = pHeader.play;
info->m_relocStartPage = pHeader.relocStartPage;   // v2NG reloc hint only
...
std::memcpy(hdr.name,   &dataBuf[22], PSID_MAXSTRLEN);   // metadata strings only
```

**Implication for SIDfinity:** to libsidplayfp the JCH NewPlayer is just 6502 code
at `init=$1000`/`play=$1003`. The `siddump --writelog` ground truth captures the
`$D400-$D418` write stream the *running* player emits; it neither knows nor cares
that it is JCH. So the verification path is identical to every other engine family —
no JCH-specific emulator changes are needed, and the extraction must derive structure
from the binary itself (see github_cheesecutter.md / github_sidfactory2.md), not from
the player.

(The `tools/libsidplayfp-overlay/` is the SIDfinity write-log instrumentation overlay;
it also contains no engine-specific code — it only taps the SID register bus.)

---

## 2. Canonical player-ID signatures

Two tools share essentially the same signature corpus. The authoritative, quotable
byte patterns live in **`cadaver/sidid`** (`sidid.cfg`). **`WilfredC64/player-id`** is
a cross-platform reimplementation using the same signature set (credits: "Wilfred
Bos, iAN CooG, Professor Chaos, Cadaver, Ninja, Ice00 and Yodelking").

### sidid.cfg syntax (readme.txt, verbatim)
- "A signature consists of hexadecimal values and `??` to accept any byte at that
  position."
- "`AND` means to skip any number of bytes and then continue when the next byte is
  matched."
- "`END` ends the current signature."
- "player signature names must not contain spaces and should be under 24 letters".
- "Multiple signatures can exist for one player, **see for example JCH_NewPlayer**."

### JCH-family signature entries (from sidid.cfg)

`JCH_NewPlayer` has many versioned patterns (the editor research counts ~20:
V1-V20 + V0x + Dane). Two representative ones:

```
JCH_NewPlayer
4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 48 29 10 END
A2 00 B9 ?? ?? 9D ?? ?? ?? ?? ?? B9 ?? ?? 9D ?? ?? ?? ?? ?? C8 C8 E8 E0 03 D0 END
   ... [additional versioned patterns through V20] ...
```

The first pattern decodes exactly to the player entry/dispatch read from the
CheeseCutter source (github_cheesecutter.md §1-2):
`4C ?? ??` = `JMP subinit/subplay`; then in the `next`/keyjam dispatch
`PHA / AND #$E0 / CMP #$80 / BNE +d / PLA / PHA / AND #$10` — the `state` bit7/bit6
test that steers keyjam vs multiplay. This is a stable, position-independent
fingerprint of the NewPlayer dispatch core.

The second pattern (`A2 00 / LDA abs,Y / STA abs,Y ... / INY INY INX / CPX #$03`) is
the classic NewPlayer **per-voice 3-channel init copy loop** (`ldx #0 … cpx #3`),
matching `subinit0` in the CC source.

Related JCH families also carried in sidid.cfg:

```
JCH_DigiPlayer
D0 ?? AD ?? ?? F0 ?? A0 00 8C ?? ?? B1 ?? 4A 4A 4A 4A 18 END

JCH_OldPlayer
48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D ?? ?? 68 18 6D ?? ?? 8D ?? ?? 68 END

JCH_Protracker
8D ?? ?? AD ?? ?? 8D 18 D4 60 A2 02 BD ?? ?? C9 02 D0 2C BC ?? ?? B9 ?? ?? BC ?? ??
99 05 D4 BC ?? ?? B9 ?? ?? BC ?? ?? 99 06 D4 AD ?? ?? F0 09 AD ?? ?? 99 04 D4 END

Dane_NewPlayer
30 03 4C ?? ?? 4C ?? ?? BD ?? ?? 85 02 BD ?? ?? 85 03 A0 00 98 9D ?? ?? B1 02
10 0F 0A 9D END
```

Notes:
- `Dane_NewPlayer` is a distinct NewPlayer derivative (Dane/Crest) — the research
  note's "Dane_NewPlayer" variant. Its signature shows a different entry shape
  (`30 03 4C ?? ?? 4C ?? ??` = `BMI +3 / JMP / JMP` init-vs-play split, then a
  `BD ?? ?? STA $02 / BD ?? ?? STA $03` zero-page pointer setup, then the 3-voice
  `LDY #0 … 9D` copy).
- `JCH_Protracker` writes are visible in the signature (`99 05 D4`, `99 06 D4`,
  `99 04 D4` = `STA $D405,Y / $D406,Y / $D404,Y`) — a different, older write order
  than NP21's `setsid` block; useful for telling Protracker-era tunes apart from NP.
- `JCH_OldPlayer` / `JCH_DigiPlayer` are pre-NewPlayer engines (not the NP17-25
  target) but share the JCH authorship lineage.

### How to use these in SIDfinity
- For coarse engine bucketing, the `JCH_NewPlayer` dispatch signature
  (`4C ?? ?? 48 29 E0 C9 80 ...`) is the most reliable single fingerprint and is
  reloc-invariant (all addresses are `??`).
- The **version** (NP17 / 20.G4 / 20.Q0 / 21.G4-G6 / 22-25) is NOT distinguished by
  one signature — sidid uses ~20 versioned `JCH_NewPlayer` patterns, and the cleanest
  in-band version marker is the ASCII string at file-offset `$0fee` (`"20.Gx"`,
  `"cc4.07"`, etc. — see github_sidfactory2.md §1). Prefer reading `$0fee` + the
  `$0fa0` pointer-block geometry over signature-version matching when the module is
  intact.

---

## 3. Reconciling the engine count

HVSC classifies JCH NewPlayer as one of the largest families (~3,611-3,678 tunes per
this repo's research). Because libsidplayfp is engine-blind, that classification comes
from external scanners (sidid / player-id) run over HVSC and recorded in HVSC's own
documents and in this repo's `hvsc84.db` `engine` column (populated by `sidid`, per
CLAUDE.md's "After re-running `sidid`" DB-refresh trigger). The signatures above are
the basis of that count.

---

## Leads to follow
- Pull the full `JCH_NewPlayer` block from `cadaver/sidid` `sidid.cfg` (all ~20
  versioned patterns) and map each to a version (NP17/20/21/22-25) by disassembling
  one HVSC representative per pattern; this gives a version classifier finer than the
  single dispatch signature.
- `WilfredC64/player-id` ships the same corpus in its own config format — cross-check
  it for any JCH patterns sidid lacks (and for the Laxity/Vibrants attribution split).
- Decode the remaining `JCH_NewPlayer` patterns (the `A2 00 …` copy-loop one, etc.)
  against the CheeseCutter `player_v4.acme` routines to confirm which player region
  each pins — useful for locating tables when the `$0fa0` block has been stripped by a
  packer.
- Confirm `hvsc84.db`'s JCH `engine` label spelling and count with a read-only query
  (`file:hvsc84.db?mode=ro`) before any wide-batch JCH work — do NOT write the DB.
