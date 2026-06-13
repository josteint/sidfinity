---
source_url: https://github.com/Chordian/sidfactory2 (packer.cpp, auxilary_data_songs.cpp, driver_info.h)
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (Chordian)
content_date: unknown (master branch as of 2026-06-13)
reliability: primary
---

# SID Factory II — Multi-Song (Multi-Subtune) Mechanics

## How multi-song works in the editor

`AuxilaryDataSongs` tracks `m_SongCount` (default 1). When a second song is added, the editor allocates a second set of `TrackCount` order lists interleaved in memory starting at `OrderListTrack1Address + OrderListSize * TrackCount`:

From `FetchOrderLists()`:
```cpp
for (int i = 0; i < music_data.m_TrackCount * song_count; ++i)
{
    const unsigned short order_list_address = music_data.m_OrderListTrack1Address
                                            + music_data.m_OrderListSize * i;
    m_OrderListDataSectionIDList.push_back(AddDataSection(order_list_address, ...));
}
```

So for N songs and T tracks, the in-editor memory has `N*T` consecutive order-list slots:
```
[track0_song0][track1_song0][track2_song0]
[track0_song1][track1_song1][track2_song1]
...
```

Each slot has a fixed `OrderListSize` allocation in-editor (even if the order list is shorter).

## What the packer emits for multi-song

The packer detects multi-song via:
```cpp
const bool requires_multi_song_patch = m_DriverInfo.GetAuxilaryDataCollection().GetSongs().GetSongCount() > 1;
```

If true, it appends to the packed binary (immediately after the normal data sections) a **multi-song stub** consisting of:

### Part 1: Order-list pointer table

Size = `SongCount * TrackCount * 2` bytes:
```
[SongCount * TrackCount bytes]  Low bytes of all order-list addresses (all songs, all tracks)
[SongCount * TrackCount bytes]  High bytes of all order-list addresses (all songs, all tracks)
```

Order: all order lists in song-major order (song 0 tracks 0..T-1, song 1 tracks 0..T-1, ...).

### Part 2: Multi-song patch code (32 bytes)

The hardcoded 6502 stub from `packer.cpp` (shown with placeholder addresses before fixup):

```asm
; On entry: A = song index (0-based, passed by PSID player as subtune number - 1)
c000  STA $FE        ; save song index in ZP (lowest ZP, patched to actual m_LowestZP)
c002  ASL A          ; A = song_index * 2
c003  CLC
c004  ADC $FE        ; A = song_index * 3  (3 tracks per voice)
c006  TAX
c007  LDY #$00
; Loop: copy 3 order-list pointers for this song into the driver's pointer tables
c009  LDA $C100,X   ; order_list_ptr_low_table[X]   (patched to actual address)
c00c  STA $C200,Y   ; driver's orderlist_ptr_low[Y]  (patched to actual address)
c00f  LDA $C110,X   ; order_list_ptr_high_table[X]  (patched to actual address)
c012  STA $C203,Y   ; driver's orderlist_ptr_high[Y] (patched to actual address)
c015  INX
c016  INY
c017  CPY #$03       ; done all 3 tracks?
c019  BNE $C009
c01b  LDA $FE        ; restore A = song index (ZP, patched)
c01d  JMP $1000      ; jump to original init entry (patched to original JMP target)
```

Total patch code: 32 bytes (`sizeof(multi_song_patch_code)` in the source).

### Fixup applied by `ApplyMultiSongPatch`

After copying the stub, the packer patches these locations within the code:

| Offset in stub | What is patched |
|----------------|----------------|
| +0x01, +0x05, +0x1C | ZP byte in `STA $ZP` / `ADC $ZP` / `LDA $ZP` → `m_LowestZP` (user-chosen ZP base) |
| +0x0A, +0x0B | Low 2 bytes of `LDA $xxxx,X` (ptr table low read) → absolute address of the low-byte table in packed binary |
| +0x10, +0x11 | Low 2 bytes of `LDA $xxxx,X` (ptr table high read) → absolute address of high-byte table |
| +0x0D, +0x0E | Low 2 bytes of `STA $xxxx,Y` (driver ptr low write) → absolute address of driver's order-list ptr low array |
| +0x13, +0x14 | Low 2 bytes of `STA $xxxx,Y` (driver ptr high write) → absolute address of driver's order-list ptr high array |
| +0x1E, +0x1F | 2-byte jump target of final `JMP` → original JMP target that was at `InitAddress+1` in the driver |

Additionally, the **driver's init routine** is patched: the 2-byte operand of the `JMP` at `m_DriverCommon.m_InitAddress` is replaced with the absolute address of this stub, so that when PSID calls init(song), execution flows through the stub first.

### How PSID subtune selection works

The PSID player calls `init(A)` with `A = subtune_number - 1` (0-based). The stub:
1. Multiplies by 3 (= TrackCount, hardcoded in the patch — implies 3 tracks/voices in standard SF2 drivers)
2. Copies the 3 order-list pointers for that song into the driver's normal pointer slots
3. Restores A and jumps to the real driver init

This means the packed multi-song binary is transparent to the driver: it always sees a single set of order-list pointers and initialises normally.

**Important limitation**: the TrackCount is hardcoded as 3 in the stub logic (`CPY #$03`). Drivers with a different voice/track count would need a different stub. Standard SF2 drivers use exactly 3 tracks.

## Single-song case

If `SongCount == 1`, no stub is appended and the init address in the PSID header points directly to the driver's original init entry. The PSID `SongCount` field is set to 1, `DefaultSong` to 1.

## What the PSID header says for multi-song

From `PSIDFile` constructor:
```cpp
m_Header.m_SongCount = endian_convert(inSongCount);   // actual song count
m_Header.m_DefaultSong = endian_convert(1);            // always 1
m_Header.m_SpeedFlags = 0;                             // VBlank for all subtunes
```

The `InitAddress` points to the stub for multi-song, or directly to the driver's init for single-song.

## Implications for HVSC extraction

For multi-song HVSC .sid files:
- The PSID `SongCount` field is the authoritative source for the number of songs.
- The `InitAddress` will point to the multi-song stub (not the driver's init). The stub is identifiable by its fixed byte pattern (the `multi_song_patch_code` array above, with ZP and absolute addresses varying).
- The order-list pointer table immediately precedes the stub in memory: `SongCount * TrackCount * 2` bytes before the stub start.
- The per-song order lists are inside the normal packed data (interleaved by track, song-major), but their absolute addresses can be read from the order-list pointer table embedded in the binary.

## Leads to follow

- Verify the `CPY #$03` hardcoding by inspecting actual multi-song HVSC SF2 files — does any SF2 driver in HVSC use a track count other than 3?
- Identify the stub in real HVSC files by searching for the byte pattern `85 ?? 0A 18 65 ?? AA A0 00 BD` at known offsets after the packed data sections.
- Check whether the `inInitOffset` and `inUpdateOffset` passed to `PSIDFile` are actually `DriverCommon.m_InitAddress - m_DriverCodeTop` (offset from load address) or absolute addresses. From the constructor: `endian_convert(driver_address + inInitOffset)` where `driver_address` is the PRG load address — so they are offsets from the load address, and the caller computes them as `m_InitAddress - m_DriverCodeTop`.
