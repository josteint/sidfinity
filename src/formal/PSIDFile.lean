/-
  PSIDFile.lean — PSID v2 file format.

  Produces a valid .sid file from a load address and binary payload.
  The payload contains both the player code and song data.
-/

import Asm6502

-- PSID v2 header (126 bytes)
structure PSIDHeader where
  version    : UInt16 := 2
  dataOffset : UInt16 := 0x7C    -- 124 bytes (v2 header size)
  loadAddr   : UInt16 := 0       -- 0 = use first 2 bytes of data as load address
  initAddr   : UInt16
  playAddr   : UInt16
  songs      : UInt16 := 1
  startSong  : UInt16 := 1
  speed      : UInt32 := 0       -- bit 0 = 0 → VBI (50Hz PAL)
  title      : String := ""
  author     : String := ""
  released   : String := ""

-- Write a big-endian UInt16
def writeBE16 (v : UInt16) : Bytes :=
  #[(v >>> 8).toUInt8, v.toUInt8]

-- Write a big-endian UInt32
def writeBE32 (v : UInt32) : Bytes :=
  #[(v >>> 24).toUInt8, (v >>> 16).toUInt8, (v >>> 8).toUInt8, v.toUInt8]

-- Pad/truncate a string to exactly n bytes
def padString (s : String) (n : Nat) : Bytes :=
  let ba := s.toUTF8
  let result : Bytes := Id.run do
    let mut arr : Bytes := #[]
    for i in [:min ba.size n] do
      arr := arr.push (ba.get! i)
    for _ in [:n - min ba.size n] do
      arr := arr.push 0
    return arr
  result

-- Serialize PSID header to 124 bytes
def serializeHeader (h : PSIDHeader) : Bytes :=
  -- Magic: "PSID"
  #[0x50, 0x53, 0x49, 0x44]          -- offset 0: magic
  ++ writeBE16 h.version              -- offset 4: version
  ++ writeBE16 h.dataOffset           -- offset 6: data offset
  ++ writeBE16 h.loadAddr             -- offset 8: load address
  ++ writeBE16 h.initAddr             -- offset 10: init address
  ++ writeBE16 h.playAddr             -- offset 12: play address
  ++ writeBE16 h.songs                -- offset 14: number of songs
  ++ writeBE16 h.startSong            -- offset 16: start song
  ++ writeBE32 h.speed                -- offset 18: speed flags
  ++ padString h.title 32             -- offset 22: title
  ++ padString h.author 32            -- offset 54: author
  ++ padString h.released 32          -- offset 86: released
  -- v2 fields (offset 118-123)
  ++ #[0, 0]                          -- flags (6581)
  ++ #[0, 0]                          -- start page
  ++ #[0, 0]                          -- page length / reserved

-- Build a complete .sid file
-- payload: the 6502 code + data that will be loaded at loadAddr
def buildSID (h : PSIDHeader) (payload : Bytes) : Bytes :=
  let header := serializeHeader h
  -- When loadAddr in header is 0, first 2 bytes of data are the load address
  if h.loadAddr == 0 then
    header ++ rawWord h.initAddr ++ payload  -- prepend actual load address
  else
    header ++ payload
