<!--
source_url: local /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/  (read-only checkout)
             + https://github.com/theyamo/CheeseCutter  (GPL, Timo Taipalus "Abaddon")
fetched_via: local read-only checkout (Read tool on pre-existing checkout)
fetch_date: 2026-06-14
author: CheeseCutter (C) Abaddon / Timo Taipalus; player "Based on JCH NP 21.G4 by Laxity/VIB"
content_date: CheeseCutter 2.10  (player header "cc4.07", player_v4.acme comment "feb '12")
reliability: PRIMARY — all claims derived directly from D source + ACME source in the local checkout
prior_docs:
  pipelines/jch_newplayer/docs/github_cheesecutter.md       (player effect chain §1-8)
  pipelines/laxity_newplayer/docs/cluster_np21_effect_routines.md  (full tsync/cmd routines)
scope: CheeseCutter-SPECIFIC DELTA not covered by the above two docs:
  1. Exported SID binary data layout (what HVSC's 302 CC2.x tunes actually contain)
  2. Export build path: build.d + dump.d + purge.d
  3. Per-tune INCLUDE_* flag stripping (per-tune player size variation)
  4. .ct on-disk format detail (supplement to github_cheesecutter.md §6)
-->

# CheeseCutter Native Player and Export Format — Delta Analysis

This document covers the CheeseCutter-specific aspects of the exported `.sid` binary and
build pipeline that are NOT already in `github_cheesecutter.md` (which covers the player
effect chain, §1-8) or `cluster_np21_effect_routines.md` (full tsync/cmd detail).

**Do not re-read this as a standalone player reference.** Start with `github_cheesecutter.md`
for the player write model.

---

## 1. Export build path — overview

```
ct2util.d  ExportSID path:
  Song.open(fn)          → load .ct (zlib-decompress, initialize 64KB C64 image)
  [optional] purge.d     → Purge.purgeAll()  (compact unused seqs/instr/tables)
  build.d doBuild(song, address=$1000, zpAddress=0, genPSID=true, ...)
    → dumpOptimized(song, address, zpAddress, genPSID, verbose)
        playerSource (player_v4.acme text)
       + dumpData(song)            ← dump.d: ACME !byte/!word data section
        setArgumentValue(...)      ← text-substitution on ACME defines
        assembles with acme_assemble()  ← bundled ACME C backend
    → generatePSIDHeader(song, assembled, initAddr=address, playAddr=address+3)
  → write assembled bytes to .sid file
```

The CC build is a **text-substitution assembler pipeline**: `player_v4.acme` source is
loaded as a string, define overrides are injected via `setArgumentValue`, song data is
appended as ACME `!byte` / `!word` directives (from `dump.d`), and the combined source
is assembled in-process with the bundled ACME. No pre-built player binary is linked — the
player is re-assembled per export, with per-tune `INCLUDE_*` flags.

---

## 2. Exported SID binary structure

### 2a. PSID header (124 = 0x7c bytes)

Defined by the `SIDHEADER` constant in `build.d`. Offsets:

| Offset | Field | Value / Notes |
|--------|-------|---------------|
| 0x00 | Magic | `PSID` |
| 0x02 | Version | `0x0002` |
| 0x08 | loadAddress | `address` (default `$1000`) |
| 0x0a | initAddress | `address` (`$1000`) |
| 0x0c | playAddress | `address + 3` (`$1003`) — i.e. the `play` JMP |
| 0x0e | numSongs | `song.subtunes.numOf` |
| 0x10 | startSong | `defaultSubtune` (1-based) |
| 0x12 | speed | **`0` (VBI)** for 1× tunes; **`$ffffffff`** for multispeed (all 4 bytes set to 255) |
| 0x16 | title | from `song.title` (32 bytes, NUL-padded) |
| 0x36 | author | from `song.author` (32 bytes, NUL-padded) |
| 0x56 | released | from `song.release` (32 bytes, NUL-padded) |
| 0x76 | flags | `0x04` (PAL) `|` `0x10` (6581) or `0x20` (8580) |
| 0x78-0x7b | unused | 0 |

PSID header size = `PSID_DATA_START = 0x7c`.

**Multispeed PSID `speed`:** `song.multiplier > 1` sets all 4 bytes of
`PSID_SPEED_OFFSET..+4` to `255` ($ff). Libsidplayfp reads this as CIA-triggered for
all subtunes. The CIA timer value is baked into the player code: `CIA_VALUE = PAL_CLOCK /
song.multiplier` where `PAL_CLOCK = $4cc7 = 19655`.

### 2b. C64 binary payload (load address = `address`, default `$1000`)

The C64 binary starts with a 2-byte load address header (`[address & 0xff, address >> 8]`)
prepended by ACME's `!to` mechanism. After the PSID header (`0x7c` bytes), the file
contains:

```
$1000  init  jmp subinit (or jmp cinit if USE_MDRIVER)    ; 3 bytes
$1003  play  jmp subplay (or jmp cplay)                   ; 3 bytes
$1006  mplay jmp submplay  (only if MULTISPEED=TRUE)      ; 3 bytes
$1009  sync  !8 0                                         ; 1 byte
$100a  subinit  [player code...]
...    [all included effect routines]
...    freqtable_lo / freqtable_hi  (96+96 = 192 bytes)
...    [player state variables]

       [SONG DATA — emitted by dump.d, appended after player code]
arp1   = *   wave table col A (up to 256 bytes, trimmed to last non-zero)
arp2   = *   wave table col B (same length as arp1 — same trim point)
filttab= *   filter table rows (4-byte rows, trimmed to last-used+4)
pulstab= *   pulse table rows  (4-byte rows, trimmed to last-used+4)
inst   = *   instrument table header label
inst0  = *   column 0 (AD)     — maxInsno+1 bytes
inst1  = *   column 1 (SR)     — maxInsno+1 bytes
inst2  = *   column 2 (HR)     — maxInsno+1 bytes
inst3  = *   column 3 (INS_4)  — maxInsno+1 bytes
inst4  = *   column 4 (FLTP)   — maxInsno+1 bytes
inst5  = *   column 5 (PULSP)  — maxInsno+1 bytes
inst6  = *   column 6 (INS_7)  — maxInsno+1 bytes
inst7  = *   column 7 (ARP)    — maxInsno+1 bytes
seqlo  = *   sequence pointer low table (numOfSeqs bytes, ACME !8 <sXX)
seqhi  = *   sequence pointer high table (numOfSeqs bytes, ACME !8 >sXX)
cmd1   = *   command table col 0 (cmd number) — tablen bytes
cmd2   = *   command table col 1 (param 1)    — tablen bytes
cmd3   = *   command table col 2 (param 2)    — tablen bytes
songsets=*   per-subtune track pointers + speed (see §3)
track0_0=*   voice 0 orderlist for subtune 0 (compacted)
track0_1=*   voice 1 orderlist for subtune 0
track0_2=*   voice 2 orderlist for subtune 0
track1_0=*   voice 0 orderlist for subtune 1  [...]
...
s00    = *   sequence 0 packed byte stream ($bf-terminated)
s01    = *   sequence 1 packed byte stream
...    [all numOfSeqs sequences]
chord  = *   chord table (up to 128 bytes, trimmed to last non-zero+1)
chordindex=* chord index table (highestChord+1 entries)
```

The player at runtime locates all tables via **ACME labels** resolved at assemble time — no
pointer table is written into the exported binary (the `$0fa0` pointer block is
`EXPORT=FALSE`-only). Labels like `arp1`, `pulstab`, `inst`, `songsets`, `seqlo`, `seqhi`,
`cmd1`, `chord`, `chordindex` are assembled to absolute addresses at their emit position.

---

## 3. Data section detail

### 3a. Instrument table — column-major, stride = `numInstr+1`

**Key difference from the editor's fixed-stride-48 layout:**

At export time, `dump.d` emits each of the 8 instrument columns as `maxInsno+1` bytes
(where `maxInsno` = highest instrument number actually referenced in any sequence).
**The exported stride is variable** — `numInstr+1` — NOT always 48. The player sees
`INSNO = numInstr+1` (injected by `setArgumentValue("INSNO", ...)` in `build.d`).

```d
// build.d line 145:
input = setArgumentValue("INSNO", format("%d", song.numInstr+1), input);

// dump.d lines 69-72:
for(int i = 0; i < 8; i++) {
    append(format("\ninst%d = *\n",i));
    hexdump(sng.instrumentTable[i * 48 .. i * 48 + (maxInsno+1)], 16);
}
```

So `INS_AD = 0`, `INS_SR = 1*INSNO`, `INS_HR = 2*INSNO`, etc., where `INSNO = maxInsno+1`
is specific to each exported tune. A tune using instruments 0–11 has INSNO=12, stride=12.

The editor always stores instruments column-major with stride 48 in the `.ct` file (and in
the 64KB C64 image used by the editor); only the export trims to `maxInsno+1`.

**Instrument byte fields (unchanged from editor; INS_* offsets × stride):**
| Byte index | INS_* | Field |
|---|---|---|
| 0 | AD=0 | Attack/Decay |
| 1 | SR=INSNO | Sustain/Release |
| 2 | HR=2*INSNO | Restart type (bits 7,6,5) + arp delay (low nibble) |
| 3 | INS_4=3*INSNO | Hard-restart waveform |
| 4 | FLTP=4*INSNO | Filter table row index (0 = no filter) |
| 5 | PULSP=5*INSNO | Pulse table row index ($00-$3f) or $80+ = direct PW |
| 6 | INS_7=6*INSNO | Hard-restart SR value |
| 7 | ARP=7*INSNO | Wave table start position |

`features.instrumentFlags = [0,0,0,0,4,3,0,1]` identifies which columns are table
pointers: byte 4=filter-table pointer, byte 5=pulse-table pointer, byte 7=wave-table
pointer.

### 3b. Pulse and filter tables — 4-byte rows, up to 64 rows × 4 = 256 bytes

Emitted trimmed to `getHighestUsed(table) + 4` (last non-zero byte + 4 = include its full
row). Each row = 4 bytes:

**Pulse table row:**
```
Byte 0: bits 7=subtract direction, 6-0=frame count (pulsecnt reload)
Byte 1: add/subtract value (16-bit with carry into pulsehi)
Byte 2: initial PW, nibbles reversed ($ff=skip; $48 → pulselo=$40, pulsehi=$08)
Byte 3: jump ($00=next row, $7f=stop, else×4=target byte offset)
```
Instrument byte5 `$00-$3f` = row index; `$80+` = direct PW (low nibble → pulsehi).

**Filter table row:**
```
Byte 0: $00-$7f=sweep duration; $80+($90-$F0)=INIT row (bits 4-6=passband type)
Byte 1: sweep add value (10-bit encoded) OR (on INIT row) written to $D417
Byte 2: initial cutoff ($ff=skip; else → $D416)
Byte 3: jump ($00=next, $7f=stop, else×4=target)
```
10-bit sweep encoding (from player lines 1421-1431):
```
filtadd+1 = (byte1 & 3) << 1
filtadd   = byte1 >> 1  (via two cmp#$80/ror pairs)
```

### 3c. Wave table — two 256-byte arrays, emitted trimmed

`arp1` and `arp2` are emitted at the same trim length (`getHighestUsed(wave1Table) + 1`).
They are NOT emitted as separate columns; `arp1` immediately precedes `arp2` in the
binary, so the assembled layout is `arp1[0..N]` followed by `arp2[0..N]`.

**Wave table column A (arp1) values:**
- `$00-$5f`: relative transpose up (added to notereal + chordvalue)
- `$80-$df`: absolute pitch (`& $7f` → freq table index, ignores note/transpose)
- `$7e`: loop to previous row (stay at current wavepos)
- `$7f`: loop — the NEXT column A byte is the jump target; jump target = column B value

**Wave table column B (arp2) values:**
- `$00`: no change to waveform
- `$01-$0f`: override wave step delay (`wavecnt`) for this row — NOT a waveform value
- `$10-$df`: SID control register value → `waveform,x`
- `$e0-$ef`: SID control reg `$00-$0f` → `waveform,x` (via `and #$0f`)
- When col A = `$7f`: this byte is the loop target (row index), not a waveform

### 3d. Command (super) table — three parallel byte columns

```d
// dump.d lines 100-105:
append("\ncmd1 = *\n");
hexdump(sng.superTable[0..tablen], 16);      // cmd1: command numbers
append("cmd2 = *\n");
hexdump(sng.superTable[64..64+tablen], 16);  // cmd2: param 1
append("cmd3 = *\n");
hexdump(sng.superTable[128..128+tablen], 16); // cmd3: param 2
```

`tablen` = highest command index actually referenced in sequences + 1 (found by scanning
all sequence elements with `e.cmd.value < 0x40`). **Row 0 is reserved** and always emitted:
`cmd2[0]` = the global hard-restart AD value (player reads `lda cmd2` at line 567).

### 3e. Songsets block — per-subtune track pointers + speed/voicemask

For each subtune `i`:
```
songsets + i*8:   !word  track{i}_0, track{i}_1, track{i}_2   (6 bytes: 3 × 2-byte track ptrs)
               +6: !byte  songspeeds[i]                          (speed value, 1 byte)
               +7: !byte  7                                       (voice mask, hardcoded 7 = all 3 voices on)
```
From `dump.d`:
```d
for(int i = 0; i < sng.subtunes.numOf; i++) {
    append(wordOp ~ "\t");
    for(int voice = 0; voice < 3; voice++) { append("track" ~ i ~ "_" ~ voice); }
    append("\n\t\t" ~ byteOp ~ " %d, 7\n", sng.songspeeds[i]);
}
```
The `7` is hardcoded in the export — all three voices are always enabled. The player reads
`songsets+7,y` at `subinit1` and ANDs it with `bits,x` to set `voicon,x`. With mask `7`,
`bits[0]=1`, `bits[1]=2`, `bits[2]=4`: `voicon[0] = 7&1 = 1`, `[1] = 7&2 = 2 (!=0)`,
`[2] = 7&4 = 4 (!=0)` — all voices enabled.

### 3f. Orderlist (track) compact format

`Tracklist.compact()` emits a variable-length byte stream:
```
[ trans_byte ]  seq_number  [ trans_byte ]  seq_number  ...  $fX  wrap_lo
```
- `trans_byte` only emitted on transpose change (value `$80-$bf`, where `$a0` = no
  transpose, `$a0+n` = semitone adjust). `$80` ("no change") is NOT emitted unless it is
  the initial value or the wrap offset boundary.
- `seq_number`: raw sequence index byte (0-127)
- `$fX wrap_lo`: two-byte end marker. Value = `(wrapOffset * 2) | $f000`, split as
  `[(val >> 8), val & $ff]`. The player decodes: `and #$07` gives the low bits of the
  wrap pointer; the full wrap is reconstructed as `twrap + (lo)` from `smashedValue/2 &
  0x7ff`. Wrap offset is the track position to loop back to (0-based track entry index).

### 3g. Sequence compact format

`Sequence.compact()` emits:
```
[ $c0+ins ]        instrument select (only on change; $c0=inst 0, $ef=inst 47)
[ $f0+delay ]      row delay (0-15 frames, only on change; $f0=0, $ff=15)
[ $5f ]            TIE prefix (optional, before note byte)
note_byte          $00=rest, $01===, $02=+++, $03-$5e=semitone (raw note value)
[ cmd_byte ]       super-command index (only if note $60-$bf AND cmd≠0)
...
$bf                SEQ_END_MARK
```
Delays > 15: emit `$f{0..f}` + `$00` rest bytes for the overflow. The packer counts
consecutive empty rows (same note=0, no cmd, no instr) ahead of the current row and folds
them into the delay counter. `$f0` = 0-frame delay (note fires immediately).

Note byte encoding from `compact()`:
- If `note >= $60` (i.e. `rawValue >= $60`) AND `cmd.rawValue > 0`: note byte is emitted
  as-is (raw value $60-$bf = note+$60), followed immediately by the command index byte.
- Otherwise: `note -= $60` (range 0-$5f), no following command byte.

---

## 4. Per-tune INCLUDE_* flag stripping (player size variation)

`dumpOptimized` in `build.d` (lines 154-258) scans all sequences and instruments before
assembling to determine which effects are actually used. It then sets per-effect ACME
conditionals via `setArgumentValue`. Stripped routines are `!if CONDITION = FALSE {}`
blocks in `player_v4.acme` — the ACME assembler simply does not emit those bytes.

**The flags and their scan triggers:**

| ACME define | Stripped if | Player routine affected |
|---|---|---|
| `INCLUDE_CMD_SLUP` | no seq cmd index with `superTable[val] == 0` (slide up) | `effslideup` |
| `INCLUDE_CMD_SLDOWN` | no slide-down cmd | `effslidedown` |
| `INCLUDE_CMD_VIBR` | no hi-fi vibrato cmd | `effvibrato` (hi-fi) |
| `INCLUDE_CMD_PORTA` | no portamento cmd | `effporta`, `snotporta` |
| `INCLUDE_CMD_SET_ADSR` | no set-ADSR cmd | `iscmd` ADSR branch |
| `INCLUDE_SEQ_SET_CHORD` | no seq cmd `$80-$9f` | chord-set branch in `superparse2` |
| `INCLUDE_CHORD` | same as above (also set jointly) | chord engine in `dowave` |
| `INCLUDE_CMD_SET_OFFSET` | no detune cmd | `CMD_SET_OFFSET` branch |
| `INCLUDE_CMD_SET_LOVIB` | no lo-fi vibrato cmd | `effdo3` |
| `INCLUDE_SEQ_SET_ATT` | no `$a0-$af` in sequences | Attack-set branch |
| `INCLUDE_SEQ_SET_DEC` | no `$b0-$bf` in sequences | Decay-set branch |
| `INCLUDE_SEQ_SET_SUS` | no `$c0-$cf` in sequences | Sustain-set branch |
| `INCLUDE_SEQ_SET_REL` | no `$d0-$df` in sequences | Release-set branch |
| `INCLUDE_SEQ_SET_VOL` | no `$e0-$ef` in sequences | Volume-set branch |
| `INCLUDE_SEQ_SET_SPEED` | no `$f0-$ff` in sequences | Speed-set branch |
| `INCLUDE_BREAKSPEED` | no `speed<2` subtune AND no `$f0/$f1` speed cmds | breakspeed path |
| `INCLUDE_FILTER` | no instrument with `filtertablePointer(i) > 0` | entire filter block, `$D415/$D416/$D417` writes |
| `MULTISPEED` | `song.multiplier == 1` | `mplay` entry, CIA timer |
| `USE_MDRIVER` | `song.multiplier == 1 OR genPSID=false` | CIA init wrapper |

**`INCLUDE_CMD_SET_WAVE` is always FALSE** — this command (`$06`) is never emitted
regardless of tune content (hardcoded default `FALSE` in player, never set by `build.d`).

**Consequence for fingerprinting:** The player byte sequence differs per tune based on
which effects are used. A fingerprint matcher cannot assume a fixed player length or fixed
relative offsets for data tables. The data tables begin immediately after the player code
(no padding), so `arp1` address varies by how many effect routines are included.

The `INSNO` value is also baked in at assemble time (`INS_SR = 1*INSNO` etc.), so
instrument table addressing constants are tune-specific.

---

## 5. Differences from the JCH NP20.G4 layout (the CC-specific delta)

The JCH NP20.G4 format (as documented in `github_cheesecutter.md` §"Cross-checks vs
codebase64") uses a **fixed memory map**: tables at fixed addresses (`$18CB` arp, `$2CCB`
seq data, `$1CCB` instruments). CC's NP21.G4 variant differs in all of these:

| Aspect | JCH NP20.G4 | CheeseCutter NP21.G4 |
|---|---|---|
| Memory layout | Fixed addresses in 64KB C64 image | Relocatable; `BASEADDRESS=$1000` default; data immediately after code |
| Pointer block | Fixed `$0fa0` table (always present) | `$0fa0` table **only when EXPORT=FALSE**; absent from exported SID |
| Instrument stride | 32 (32 instruments) | `numInstr+1` per-tune (up to 48 in editor) |
| Pulse/filter rows | 2-byte rows (NP20) | **4-byte rows** (NP21 CC) |
| Sequence end marker | `$7f` (NP20) | `$bf` (CC) |
| Sequence alphabet | `$A0-$BF`=instrument, `$C0-$DF`=super, `$80`=nothing | `$c0-$ef`=instrument, note+`$60` range + cmd byte, `$5f`=tie prefix |
| Filter sweep resolution | 8-bit | **10-bit** (CC, feb '12) |
| Version string | varies | `"cc4.07"` at `$0fee` (editor only) |
| `INCLUDE_*` per-effect stripping | Not present | Yes — player size varies per tune |
| `cmd2[0]` = global HR-AD | Same | Same |
| Init/play/mplay jump table | Fixed at load address | `$1000/$1003/$1006` (default) |

The **sequence alphabet is a significant break** from NP20: the CC packer stores note
values as `rawValue` which includes the `$60` offset in the `$60-$bf` range for notes-with-commands, but strips the offset for standalone notes. NP20 used a different encoding
(`$80` = nothing, `$90` = tie, `$A0-$BF` = instrument).

---

## 6. .ct on-disk format (supplement to github_cheesecutter.md §6)

The `base.d` `DatafileOffset` constants and `save()`/`open()` code give the exact layout:

```
.ct file:
  [0..2]  "CC2"  (magic, 3 bytes, uncompressed)
  [3..]   zlib-compressed blob:
    [0..65535]       64KB C64 memory image (player + tables at editor addresses)
    [65536]          ver   (SONG_REVISION = 12; <6 rejected; >=128 = stereo, rejected)
    [65537]          clock
    [65538]          multiplier
    [65539]          sidModel  (0=6581, non-zero=8580 → PSID flags 0x10/0x20)
    [65540]          fppres
    [65541..65572]   songspeeds[32]      (if ver >= 6)
    [65573]          highlight           (if ver > 10)
    [65574]          highlightOffset     (if ver > 10)
    [65541..65796]   padding to DatafileOffset.Title = 65797
    [65797..65828]   title[32]
    [65829..65860]   author[32]
    [65861..65892]   release[32]
    [65893..65924]   message[32]         (4th 32-byte string; not shown in editor UI)
    [65925..65956]   padding to DatafileOffset.Insnames = 65957
    [65957..67492]   insLabels[48][32] = 1536 bytes  (instrument name labels)
    [67493..68004]   padding (512 bytes) to DatafileOffset.Subtunes = 68005
    [68005..166308]  subtunes[32][3][1024] = 98304 bytes  (orderlist raw data)
```

The 64KB C64 image (bytes 0..65535) contains the full editor player at `$0e00`-`$1fff` plus
tables at their editor addresses. The table base addresses are read from the `$0fa0` pointer
block when the editor calls `initialize()`. The editor player always uses stride-48 for
instruments and fixed-length (256-byte) arrays for all tables, regardless of actual content.

---

## 7. Relocation and address independence

**Default export address: `$1000`** (confirmed by `ct2util.d` line 93:
`int relocAddress = 0x1000`). The `-r <addr>` flag allows relocation to any address.

At relocation time, ACME resolves all labels (`arp1`, `pulstab`, `inst`, etc.) relative to
`BASEADDRESS`. The player uses **only label-resolved absolute addresses** internally — there
is no relocation table or pointer fixup step. The data layout immediately follows the player
code, so all data addresses shift by the same amount when `BASEADDRESS` changes.

The zero-page register `ZREG` defaults to `$fb` (used as a 2-byte indirect pointer for
`lda (ZREG),y` sequence and orderlist reads). It can be overridden with `-z <zp_addr>`.

**The `$0fa0` pointer table is absent** in exported SIDs — it only exists when
`EXPORT=FALSE` (editor mode). Any extractor relying on `$0fa0` to find tables will fail on
exported tunes. Data addresses must be read from the assembled symbol table (from
`seqlo`/`seqhi` to find sequence addresses, or by parsing the player code's LDA absolute
operands).

---

## 8. Purge step before export

`ct2util.d` calls `Purge.purgeAll()` before `doBuild`:

1. **purgeSeqs**: deduplicates identical sequences; compacts (moves used seqs to lower
   indices). Unused seqs (not referenced by any orderlist) are cleared.
2. **purgeInstruments**: clears and compacts unused instruments (those not referenced in
   used sequences). Updates all sequence instrument references.
3. **purgeWavetable**: removes unused wave programs (those not pointed to by any used
   instrument byte 7). Fixes up `$7f`-loop pointers after deletion.
4. **purgeChordtable**: removes unused chord entries; rebuilds `chordIndexTable`.
5. **purgeCmdtable**: removes unreferenced command-table entries (those with no sequence
   reference `< $40`). Row 0 is never removed (hardcoded `super_used[0]` not set, so it
   stays zeroed — but `cmd2[0]` = HR-AD is preserved because row 0 is always included as
   `tablen` starts at 1 and the loop starts at `i=1`).
6. **purgePulseFilter**: marks reachable pulse/filter rows from instruments and sequences,
   zeros unreachable rows, then compacts (shifts rows down, fixes jump pointers and
   instrument byte4/byte5 references).

After purge, all table indices in sequences and instrument bytes are renumbered to reflect
the compacted positions. The exported data is the purged state.

---

## 9. Multispeed / CIA timer

When `song.multiplier > 1`:
- `MULTISPEED = TRUE` → `mplay jmp submplay` entry at `$1006`
- `USE_MDRIVER = TRUE` (for PSID export) → `init` becomes `jmp cinit`, `play` becomes
  `jmp cplay`
- `cinit`: loads CIA A timer with `CIA_VALUE = $4cc7 / multiplier` (PAL/multiplier)
  (`STA $dc05` high byte, `STA $dc04` low byte), then calls `subinit`
- `cplay`: counts down internal `cntr`; at 0 calls `subplay` (full frame); at non-zero
  calls `submplay` (sound-only, skips sequence/track advance)
- `MULTIPLIER` = `song.multiplier - 1` (the `cntr` reload value)
- PSID `speed` field = `0xffffffff` (all bits set = CIA-triggered for all subtunes)

For standard 1× tunes: `init = jmp subinit`, `play = jmp subplay`, PSID `speed = 0` (VBI).

---

## 10. Known gaps / unresolved questions

1. **Sequence pointer table (`seqlo`/`seqhi`)**: the player reads sequence start addresses
   via `data[seqlo + no]` and `data[seqhi + no]`, i.e. `seqlo[n]` = low byte, `seqhi[n]`
   = high byte of the assembled `sXX` label. These are resolved at assemble time. In the
   exported SID there is no separate pointer fixup — the table is literally the low/high
   bytes of the ACME labels. An extractor must read the seqlo/seqhi tables to find sequence
   starts, since sequences are packed end-to-end without gaps.

2. **`numOfSeqs` determination from binary**: the editor's `numOfSeqs` property scans for
   the first all-`$00` sequence (`data.raw[0..5] != INITIAL_SEQ`). In an exported SID
   the count is implicit from `tablen` in the seqlo/seqhi tables. An extractor should read
   forward from `seqlo[0]..seqlo[N-1]` until a sequence starting with `$bf` (empty) is
   found.

3. **Swing/breakspeed**: when any subtune has `speed < 2`, `INCLUDE_BREAKSPEED = TRUE` and
   the chord table's first entry (index 0) is the tempo program. The chord table and tempo
   data are stored in the same `chord[]` array — tempo bytes at the head, chord arpeggios
   after. An extractor must determine the breakspeed boundary (from `speedsub` usage or
   by inspecting subtune speeds).

4. **The `fppres` field** in the `.ct` header (byte at offset 65540) is loaded but never
   used in the export path — purpose unknown.

5. **Player version mismatch warning**: `build.d` line 146-149 prints a warning if
   `song.playerID[0..6]` (the `"cc4.07"` string from `$0fee` in the `.ct` file) does not
   match the linked player's ID. HVSC tunes built with older CC versions may use a
   slightly different player binary. The player version string is absent from exported SIDs
   (`$0fee` block is `EXPORT=FALSE`-only).

6. **`$D418` initial state**: the first `subplay` call sets `volume = $0f` and writes
   `$D417 = $f0` (filter off). If `INCLUDE_FILTER = FALSE`, `$D418` is written as just
   `lda volume : sta $d418` (no `ora bandpass`). The init value of `bandpass` is 0 in that
   case. Confirms: `$D418 = $0f` on first play() for all CC exports.

---

## Leads to follow

1. **Extractor entry point:** to extract a CC2 export, start by finding `seqlo` and
   `seqhi` table addresses (from the player code's LDA operands at the `seqnext` label, or
   by tracing the `Offsets.SeqLO` / `Offsets.SeqHI` player code path). Then walk
   `seqlo[0..N]` / `seqhi[0..N]` to find each sequence start; decode sequences using the
   compact alphabet (§3g).

2. **INSNO probe:** `INSNO` must be probed per-tune by disassembling the player and reading
   the `INS_SR` = `1*INSNO` constant from the first `lda inst+INS_SR,y` instruction.
   Alternatively: find the `inst` label, then find the next label after it; `(next - inst)
   / 8` = INSNO. (Divide the instrument block by 8 columns.)

3. **Filter presence detection:** `INCLUDE_FILTER` absence means no `$D415`/`$D416`/
   `$D417` writes ever. A per-tune fingerprint should check whether the filter block is
   present by looking for the `dec filtcnt` opcode after the `voice` loop.

4. **`cmd2[0]` = global HR-AD value:** always `superTable[64]` (column 2 of row 0). For
   a tune with no hard-restart instruments, this byte may be `$00` (no HR). Must be read
   and stored regardless as it feeds into `EngineConfig`.

5. **Wave table delimiter detection:** the wave table is shared across all instruments.
   Entries are delimited by `$7e` (loop-prev) or `$7f` (loop-jump) in column A. These
   mark program boundaries. An extractor walking from a wave pointer must follow `$7e`/
   `$7f` links to find the end of a program.

6. **Multispeed detection for PSID capture:** PSID `speed = 0xffffffff` → CIA-triggered.
   The `siddump --writelog-per-irq` path should be used for any CC tune with
   `multiplier > 1`. Detect from PSID `speed` field bits.

7. **Address range validation:** the default load is `$1000`. Any tune with tables
   extending past `$fff9` is rejected at export (`endAddr > 0xfff9` check in
   `generatePSIDHeader`). Maximum usable C64 address space = `$1000...$fff8`.
