-- Auto-generated from pipelines/last_v8_c128/extract/emit_usf.py
-- DO NOT EDIT — regenerate via:
--     python -m pipelines.last_v8_c128.extract

namespace LastV8C128NS

/-- RSID header fields, copied verbatim from the original binary. -/
structure Header where
  magic     : String
  loadAddr  : UInt16
  initAddr  : UInt16
  playAddr  : UInt16
  songs     : UInt8
  startSong : UInt8
  name      : String
  author    : String
  released  : String
  deriving Repr

/-- One per subtune (0-indexed). `kind` ∈ {"music","sample","sfx"}. -/
structure SubtuneRoute where
  subtune : Nat
  kind    : String
  deriving Repr

/-- One sample played by the relocated $C000 player. -/
structure SampleRecord where
  subtune       : Nat
  startAddr     : UInt16
  endAddr       : UInt16
  rateConstant  : UInt8
  deriving Repr

/-- Where the static tables of the tracker driver live. -/
structure MusicTables where
  freqTable      : UInt16
  instrumentTable: UInt16
  sfxTable       : UInt16
  orderlistPtrs  : UInt16
  patternPtrLo   : UInt16
  patternPtrHi   : UInt16
  deriving Repr

/-- The fields of a "note" pattern event. -/
structure NoteInfo where
  hold       : Nat
  noRelease  : Bool
  pitch      : Nat
  instrument : Option Nat
  arpMode    : Option Nat
  deriving Repr

/-- A pattern event: a held note or a tie. -/
inductive PatternEvent where
  | note (info : NoteInfo)             : PatternEvent
  | tie  (hold : Nat) (noRel : Bool)   : PatternEvent
  deriving Repr

structure Pattern where
  index   : Nat
  addr    : UInt16
  events  : List PatternEvent
  deriving Repr

structure Orderlist where
  voice      : Nat
  addr       : UInt16
  indices    : List Nat
  terminator : String
  deriving Repr

/-- 8-byte instrument record from $85A1. -/
structure Instrument where
  id          : Nat
  pulseWidth  : UInt16
  ctrl        : UInt8
  ad          : UInt8
  sr          : UInt8
  vibShift    : UInt8
  pwm         : UInt8
  fxFlags     : UInt8
  deriving Repr

structure MusicSubtune where
  subtune : Nat
  voices  : List Orderlist
  deriving Repr

structure EngineModel where
  header         : Header
  relocatorSrc   : UInt16
  relocatorLen   : UInt16
  relocatorDst   : UInt16
  routes         : List SubtuneRoute
  samples        : List SampleRecord
  music          : MusicTables
  freqTable      : List (UInt8 × UInt8)
  patterns       : List Pattern
  musicSubtunes  : List MusicSubtune
  instruments    : List Instrument
  deriving Repr

def lastV8C128Model : EngineModel :=
  let h : Header := {
    magic     := "RSID"
    loadAddr  := 0x4800
    initAddr  := 0x7F40
    playAddr  := 0x0000
    songs     := 18
    startSong := 1
    name      := "The Last V8 (C128 version)"
    author    := "Rob Hubbard"
    released  := "1985 MAD/Mastertronic"
  }
  let routes : List SubtuneRoute := [
  { subtune := 0, kind := "music" },
  { subtune := 1, kind := "music" },
  { subtune := 2, kind := "music" },
  { subtune := 3, kind := "sample" },
  { subtune := 4, kind := "sample" },
  { subtune := 5, kind := "sample" },
  { subtune := 6, kind := "sfx" },
  { subtune := 7, kind := "sfx" },
  { subtune := 8, kind := "sfx" },
  { subtune := 9, kind := "sfx" },
  { subtune := 10, kind := "sfx" },
  { subtune := 11, kind := "sfx" },
  { subtune := 12, kind := "sfx" },
  { subtune := 13, kind := "sfx" },
  { subtune := 14, kind := "sfx" },
  { subtune := 15, kind := "sfx" },
  { subtune := 16, kind := "sfx" },
  { subtune := 17, kind := "sfx" }
  ]
  let samples : List SampleRecord := [
  { subtune := 3, startAddr := 0x4800, endAddr := 0x582F, rateConstant := 0xC0 },
  { subtune := 4, startAddr := 0x5830, endAddr := 0x690D, rateConstant := 0xC0 },
  { subtune := 5, startAddr := 0x690E, endAddr := 0x7B2F, rateConstant := 0xC0 }
  ]
  let m : MusicTables := {
    freqTable       := 0x843B
    instrumentTable := 0x85A1
    sfxTable        := 0x8699
    orderlistPtrs   := 0x8791
    patternPtrLo    := 0x87A9
    patternPtrHi    := 0x87C6
  }
  let patterns : List Pattern := [
  { index := 0, addr := 0x88AE, events := [
  PatternEvent.tie 31 false
  ] },
  { index := 1, addr := 0x8A0F, events := [
  PatternEvent.note ⟨3, false, 21, some 2, none⟩,
  PatternEvent.note ⟨3, false, 33, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 21, some 2, none⟩,
  PatternEvent.note ⟨3, false, 33, none, none⟩,
  PatternEvent.note ⟨3, false, 45, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 33, some 2, none⟩
  ] },
  { index := 2, addr := 0x8AD0, events := [
  PatternEvent.note ⟨3, false, 69, some 0, none⟩,
  PatternEvent.note ⟨3, false, 71, some 1, none⟩,
  PatternEvent.note ⟨3, false, 76, none, none⟩,
  PatternEvent.note ⟨3, false, 64, some 0, none⟩,
  PatternEvent.note ⟨3, false, 76, some 1, none⟩,
  PatternEvent.note ⟨3, false, 71, none, none⟩,
  PatternEvent.note ⟨3, false, 57, some 0, none⟩,
  PatternEvent.note ⟨3, false, 76, some 1, none⟩,
  PatternEvent.note ⟨3, false, 81, some 0, none⟩,
  PatternEvent.note ⟨3, false, 71, some 1, none⟩,
  PatternEvent.note ⟨3, false, 69, some 0, none⟩,
  PatternEvent.note ⟨3, false, 76, some 1, none⟩,
  PatternEvent.note ⟨3, false, 57, some 0, none⟩,
  PatternEvent.note ⟨3, false, 71, some 1, none⟩,
  PatternEvent.note ⟨3, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 71, none, none⟩
  ] },
  { index := 3, addr := 0x8A25, events := [
  PatternEvent.note ⟨3, false, 28, some 2, none⟩,
  PatternEvent.note ⟨3, false, 40, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 28, some 2, none⟩,
  PatternEvent.note ⟨3, false, 40, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 40, some 2, none⟩
  ] },
  { index := 4, addr := 0x88DA, events := [
  PatternEvent.note ⟨3, false, 69, some 6, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨7, false, 72, none, none⟩,
  PatternEvent.note ⟨3, false, 71, none, none⟩,
  PatternEvent.note ⟨7, false, 67, none, none⟩,
  PatternEvent.note ⟨7, false, 69, none, none⟩,
  PatternEvent.note ⟨15, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 67, none, none⟩,
  PatternEvent.note ⟨3, false, 68, none, none⟩,
  PatternEvent.note ⟨3, false, 69, some 6, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨7, false, 72, none, none⟩,
  PatternEvent.note ⟨3, false, 71, none, none⟩,
  PatternEvent.note ⟨7, false, 67, none, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.tie 3 false,
  PatternEvent.note ⟨7, false, 50, some 9, none⟩,
  PatternEvent.note ⟨7, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 47, none, none⟩,
  PatternEvent.note ⟨7, false, 56, some 10, none⟩
  ] },
  { index := 5, addr := 0x8932, events := [
  PatternEvent.note ⟨3, false, 62, some 4, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, true, 62, none, some 176⟩,
  PatternEvent.note ⟨11, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 62, some 4, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, true, 58, none, some 167⟩,
  PatternEvent.note ⟨11, false, 57, none, none⟩,
  PatternEvent.note ⟨3, false, 62, some 4, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, true, 62, none, some 176⟩,
  PatternEvent.note ⟨11, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 62, some 4, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨7, false, 64, none, none⟩,
  PatternEvent.note ⟨3, true, 67, none, some 192⟩,
  PatternEvent.note ⟨11, false, 68, none, none⟩
  ] },
  { index := 6, addr := 0x8A3B, events := [
  PatternEvent.note ⟨31, true, 21, some 8, none⟩,
  PatternEvent.note ⟨11, false, 21, none, none⟩,
  PatternEvent.note ⟨3, false, 23, none, none⟩,
  PatternEvent.note ⟨7, false, 24, none, none⟩,
  PatternEvent.note ⟨7, false, 23, none, none⟩,
  PatternEvent.note ⟨31, true, 19, none, none⟩,
  PatternEvent.note ⟨11, false, 19, none, none⟩,
  PatternEvent.note ⟨3, false, 23, none, none⟩,
  PatternEvent.note ⟨7, false, 24, none, none⟩,
  PatternEvent.note ⟨7, false, 23, none, none⟩,
  PatternEvent.note ⟨31, true, 18, none, none⟩,
  PatternEvent.note ⟨11, false, 18, none, none⟩,
  PatternEvent.note ⟨3, false, 23, none, none⟩,
  PatternEvent.note ⟨7, false, 24, none, none⟩,
  PatternEvent.note ⟨7, false, 23, none, none⟩,
  PatternEvent.note ⟨31, true, 17, none, none⟩,
  PatternEvent.note ⟨11, false, 17, none, none⟩,
  PatternEvent.note ⟨3, false, 23, none, none⟩,
  PatternEvent.note ⟨7, false, 24, none, none⟩,
  PatternEvent.note ⟨7, false, 23, none, none⟩
  ] },
  { index := 7, addr := 0x898B, events := [
  PatternEvent.tie 15 false,
  PatternEvent.note ⟨3, true, 64, some 7, none⟩,
  PatternEvent.note ⟨7, false, 69, none, none⟩,
  PatternEvent.note ⟨3, false, 77, none, none⟩,
  PatternEvent.note ⟨31, true, 76, none, none⟩
  ] },
  { index := 8, addr := 0x8996, events := [
  PatternEvent.tie 15 false,
  PatternEvent.note ⟨3, true, 69, some 7, none⟩,
  PatternEvent.note ⟨7, false, 76, none, none⟩,
  PatternEvent.note ⟨3, false, 84, none, none⟩,
  PatternEvent.note ⟨31, true, 83, none, none⟩
  ] },
  { index := 9, addr := 0x8A65, events := [
  PatternEvent.note ⟨31, true, 26, none, none⟩,
  PatternEvent.note ⟨11, false, 26, none, none⟩,
  PatternEvent.note ⟨3, false, 28, none, none⟩,
  PatternEvent.note ⟨7, false, 29, none, none⟩,
  PatternEvent.note ⟨7, false, 28, none, none⟩,
  PatternEvent.note ⟨31, true, 24, none, none⟩,
  PatternEvent.note ⟨11, false, 24, none, none⟩,
  PatternEvent.note ⟨3, false, 28, none, none⟩,
  PatternEvent.note ⟨7, false, 29, none, none⟩,
  PatternEvent.note ⟨7, false, 28, none, none⟩,
  PatternEvent.note ⟨31, true, 23, none, none⟩,
  PatternEvent.note ⟨11, false, 23, none, none⟩,
  PatternEvent.note ⟨3, false, 28, none, none⟩,
  PatternEvent.note ⟨7, false, 29, none, none⟩,
  PatternEvent.note ⟨7, false, 28, none, none⟩,
  PatternEvent.note ⟨31, true, 16, none, none⟩,
  PatternEvent.note ⟨11, false, 16, none, none⟩,
  PatternEvent.note ⟨3, false, 28, none, none⟩,
  PatternEvent.note ⟨7, false, 29, none, none⟩,
  PatternEvent.note ⟨7, false, 28, none, none⟩
  ] },
  { index := 10, addr := 0x8908, events := [
  PatternEvent.note ⟨11, false, 52, some 5, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 55, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨7, false, 54, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨7, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨7, false, 48, none, none⟩,
  PatternEvent.note ⟨3, false, 45, none, none⟩,
  PatternEvent.note ⟨3, false, 0, some 11, none⟩,
  PatternEvent.note ⟨27, false, 0, none, some 240⟩
  ] },
  { index := 11, addr := 0x88B0, events := [
  PatternEvent.note ⟨11, false, 52, some 5, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 55, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨7, false, 54, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨3, false, 52, none, none⟩,
  PatternEvent.note ⟨7, false, 57, none, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨7, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 57, none, none⟩,
  PatternEvent.note ⟨3, false, 0, some 11, none⟩,
  PatternEvent.note ⟨27, false, 48, none, some 241⟩
  ] },
  { index := 12, addr := 0x8A8E, events := [
  PatternEvent.note ⟨3, false, 26, some 2, none⟩,
  PatternEvent.note ⟨3, false, 38, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 26, some 2, none⟩,
  PatternEvent.note ⟨3, false, 38, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 38, some 2, none⟩
  ] },
  { index := 13, addr := 0x8AA4, events := [
  PatternEvent.note ⟨3, false, 19, some 2, none⟩,
  PatternEvent.note ⟨3, false, 31, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 19, some 2, none⟩,
  PatternEvent.note ⟨3, false, 31, none, none⟩,
  PatternEvent.note ⟨3, false, 43, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 31, some 2, none⟩
  ] },
  { index := 14, addr := 0x8ABA, events := [
  PatternEvent.note ⟨3, false, 23, some 2, none⟩,
  PatternEvent.note ⟨3, false, 35, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 23, some 2, none⟩,
  PatternEvent.note ⟨3, false, 35, none, none⟩,
  PatternEvent.note ⟨3, false, 47, none, none⟩,
  PatternEvent.note ⟨3, false, 47, some 3, none⟩,
  PatternEvent.note ⟨3, false, 35, some 2, none⟩
  ] },
  { index := 15, addr := 0x89A1, events := [
  PatternEvent.note ⟨3, false, 50, some 5, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 53, none, none⟩,
  PatternEvent.note ⟨7, false, 60, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨7, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨3, false, 50, none, none⟩,
  PatternEvent.note ⟨7, false, 53, none, none⟩,
  PatternEvent.note ⟨7, false, 60, none, none⟩,
  PatternEvent.note ⟨3, false, 55, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨31, false, 74, some 15, none⟩
  ] },
  { index := 16, addr := 0x89C8, events := [
  PatternEvent.note ⟨3, false, 59, some 5, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 68, none, none⟩,
  PatternEvent.note ⟨3, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨7, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨3, false, 64, none, none⟩,
  PatternEvent.note ⟨3, false, 59, none, none⟩,
  PatternEvent.note ⟨3, false, 68, none, none⟩,
  PatternEvent.note ⟨31, false, 76, some 15, none⟩
  ] },
  { index := 17, addr := 0x8AFD, events := [
  PatternEvent.note ⟨3, false, 69, some 0, none⟩,
  PatternEvent.note ⟨3, false, 69, some 1, none⟩,
  PatternEvent.note ⟨3, false, 74, none, none⟩,
  PatternEvent.note ⟨3, false, 64, some 0, none⟩,
  PatternEvent.note ⟨3, false, 74, some 1, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩,
  PatternEvent.note ⟨3, false, 57, some 0, none⟩,
  PatternEvent.note ⟨3, false, 74, some 1, none⟩,
  PatternEvent.note ⟨3, false, 81, some 0, none⟩,
  PatternEvent.note ⟨3, false, 69, some 1, none⟩,
  PatternEvent.note ⟨3, false, 69, some 0, none⟩,
  PatternEvent.note ⟨3, false, 74, some 1, none⟩,
  PatternEvent.note ⟨3, false, 57, some 0, none⟩,
  PatternEvent.note ⟨3, false, 69, some 1, none⟩,
  PatternEvent.note ⟨3, false, 62, none, none⟩,
  PatternEvent.note ⟨3, false, 69, none, none⟩
  ] },
  { index := 18, addr := 0x89F9, events := [
  PatternEvent.note ⟨31, true, 124, some 13, none⟩,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true
  ] },
  { index := 19, addr := 0x8A04, events := [
  PatternEvent.note ⟨31, true, 33, some 14, none⟩,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true,
  PatternEvent.tie 31 true
  ] },
  { index := 20, addr := 0x8B2A, events := [
  PatternEvent.note ⟨2, false, 48, some 16, none⟩,
  PatternEvent.note ⟨2, false, 50, none, none⟩,
  PatternEvent.note ⟨2, false, 55, none, none⟩,
  PatternEvent.note ⟨2, false, 60, none, none⟩,
  PatternEvent.note ⟨2, false, 62, none, none⟩,
  PatternEvent.note ⟨2, false, 67, none, none⟩,
  PatternEvent.note ⟨2, false, 72, none, none⟩,
  PatternEvent.note ⟨2, false, 74, none, none⟩,
  PatternEvent.note ⟨2, false, 79, none, none⟩,
  PatternEvent.note ⟨2, false, 74, none, none⟩,
  PatternEvent.note ⟨2, false, 72, none, none⟩,
  PatternEvent.note ⟨2, false, 67, none, none⟩,
  PatternEvent.note ⟨2, false, 62, none, none⟩,
  PatternEvent.note ⟨2, false, 60, none, none⟩,
  PatternEvent.note ⟨2, false, 55, none, none⟩,
  PatternEvent.note ⟨2, false, 52, none, none⟩
  ] },
  { index := 21, addr := 0x8B4C, events := [
  PatternEvent.note ⟨31, true, 57, some 4, none⟩,
  PatternEvent.note ⟨31, true, 57, none, some 254⟩,
  PatternEvent.note ⟨31, true, 60, none, none⟩,
  PatternEvent.note ⟨31, false, 60, none, none⟩
  ] },
  { index := 22, addr := 0x8B57, events := [
  PatternEvent.note ⟨5, false, 50, some 9, none⟩,
  PatternEvent.note ⟨11, false, 50, none, none⟩,
  PatternEvent.note ⟨11, false, 47, none, none⟩,
  PatternEvent.note ⟨5, false, 47, none, none⟩,
  PatternEvent.note ⟨11, false, 44, none, none⟩,
  PatternEvent.note ⟨11, true, 31, some 8, none⟩,
  PatternEvent.note ⟨5, true, 34, none, none⟩,
  PatternEvent.note ⟨5, true, 34, none, some 133⟩,
  PatternEvent.note ⟨5, true, 33, none, none⟩,
  PatternEvent.note ⟨11, true, 29, none, none⟩,
  PatternEvent.note ⟨11, true, 31, none, none⟩,
  PatternEvent.note ⟨11, true, 27, none, none⟩,
  PatternEvent.note ⟨5, false, 26, none, none⟩,
  PatternEvent.note ⟨23, true, 24, none, none⟩,
  PatternEvent.note ⟨23, true, 19, none, none⟩,
  PatternEvent.note ⟨23, true, 19, none, none⟩,
  PatternEvent.note ⟨31, true, 19, none, none⟩,
  PatternEvent.note ⟨31, true, 19, none, some 136⟩,
  PatternEvent.note ⟨31, true, 24, none, none⟩,
  PatternEvent.note ⟨31, false, 24, none, none⟩
  ] },
  { index := 23, addr := 0x8B84, events := [
  PatternEvent.tie 23 false,
  PatternEvent.tie 23 false,
  PatternEvent.note ⟨23, true, 50, some 10, none⟩,
  PatternEvent.note ⟨23, true, 50, none, none⟩,
  PatternEvent.note ⟨23, true, 50, none, none⟩,
  PatternEvent.tie 23 false,
  PatternEvent.note ⟨11, false, 60, some 4, none⟩,
  PatternEvent.note ⟨5, true, 63, none, none⟩,
  PatternEvent.note ⟨5, true, 63, none, some 151⟩,
  PatternEvent.note ⟨5, false, 62, none, none⟩,
  PatternEvent.note ⟨11, false, 58, none, none⟩,
  PatternEvent.note ⟨5, false, 55, none, none⟩,
  PatternEvent.note ⟨31, true, 60, none, none⟩,
  PatternEvent.note ⟨31, true, 60, none, some 254⟩,
  PatternEvent.note ⟨31, true, 63, none, none⟩,
  PatternEvent.note ⟨31, false, 63, none, none⟩
  ] },
  { index := 24, addr := 0x8BB8, events := [
  PatternEvent.note ⟨11, false, 28, some 8, none⟩,
  PatternEvent.note ⟨5, true, 31, none, none⟩,
  PatternEvent.note ⟨5, true, 31, none, some 133⟩,
  PatternEvent.note ⟨5, true, 30, none, none⟩,
  PatternEvent.note ⟨11, true, 26, none, none⟩,
  PatternEvent.note ⟨5, true, 23, none, none⟩,
  PatternEvent.note ⟨23, true, 28, none, none⟩,
  PatternEvent.note ⟨23, true, 28, none, none⟩,
  PatternEvent.note ⟨23, true, 33, none, none⟩,
  PatternEvent.note ⟨23, true, 33, none, none⟩,
  PatternEvent.note ⟨23, true, 28, none, none⟩,
  PatternEvent.note ⟨23, true, 28, none, none⟩,
  PatternEvent.note ⟨23, true, 28, none, none⟩,
  PatternEvent.note ⟨23, false, 33, none, none⟩
  ] },
  { index := 25, addr := 0x8BD7, events := [
  PatternEvent.tie 23 false,
  PatternEvent.tie 23 false,
  PatternEvent.note ⟨5, false, 57, some 18, none⟩,
  PatternEvent.note ⟨5, false, 57, none, none⟩,
  PatternEvent.note ⟨11, false, 60, none, none⟩,
  PatternEvent.note ⟨5, false, 59, none, none⟩,
  PatternEvent.note ⟨11, false, 55, none, none⟩,
  PatternEvent.note ⟨11, false, 57, none, none⟩,
  PatternEvent.note ⟨23, false, 50, none, none⟩,
  PatternEvent.note ⟨5, false, 55, none, none⟩,
  PatternEvent.note ⟨5, false, 52, none, none⟩,
  PatternEvent.note ⟨5, false, 51, none, none⟩,
  PatternEvent.note ⟨5, false, 50, none, none⟩,
  PatternEvent.note ⟨2, false, 51, none, none⟩,
  PatternEvent.note ⟨2, false, 52, none, none⟩,
  PatternEvent.note ⟨2, false, 53, none, none⟩,
  PatternEvent.note ⟨2, false, 54, none, none⟩,
  PatternEvent.note ⟨2, false, 55, none, none⟩,
  PatternEvent.note ⟨2, false, 56, none, none⟩,
  PatternEvent.note ⟨2, false, 57, none, none⟩,
  PatternEvent.note ⟨2, false, 58, none, none⟩,
  PatternEvent.note ⟨2, false, 59, none, none⟩,
  PatternEvent.note ⟨2, false, 60, none, none⟩,
  PatternEvent.note ⟨2, false, 61, none, none⟩,
  PatternEvent.note ⟨2, false, 62, none, none⟩,
  PatternEvent.note ⟨2, false, 63, none, none⟩,
  PatternEvent.note ⟨2, false, 64, none, none⟩,
  PatternEvent.note ⟨2, false, 65, none, none⟩,
  PatternEvent.note ⟨2, false, 66, none, none⟩,
  PatternEvent.note ⟨2, false, 67, none, none⟩,
  PatternEvent.note ⟨2, false, 68, none, none⟩,
  PatternEvent.note ⟨2, false, 69, none, none⟩,
  PatternEvent.note ⟨2, false, 70, none, none⟩,
  PatternEvent.note ⟨2, false, 71, none, none⟩,
  PatternEvent.note ⟨2, false, 72, none, none⟩,
  PatternEvent.note ⟨23, false, 73, none, none⟩
  ] },
  { index := 26, addr := 0x8C1F, events := [
  PatternEvent.note ⟨5, false, 35, some 4, none⟩,
  PatternEvent.note ⟨2, false, 36, none, none⟩,
  PatternEvent.note ⟨2, false, 37, none, none⟩,
  PatternEvent.note ⟨2, false, 38, none, none⟩,
  PatternEvent.note ⟨2, false, 39, none, none⟩,
  PatternEvent.note ⟨2, false, 40, none, none⟩,
  PatternEvent.note ⟨2, false, 41, none, none⟩,
  PatternEvent.note ⟨2, false, 42, none, none⟩,
  PatternEvent.note ⟨2, false, 43, none, none⟩,
  PatternEvent.note ⟨2, false, 44, none, none⟩,
  PatternEvent.note ⟨2, false, 45, none, none⟩,
  PatternEvent.note ⟨2, false, 46, none, none⟩,
  PatternEvent.note ⟨2, false, 47, none, none⟩,
  PatternEvent.note ⟨2, false, 48, none, none⟩,
  PatternEvent.note ⟨2, false, 49, none, none⟩,
  PatternEvent.note ⟨2, false, 50, none, none⟩,
  PatternEvent.note ⟨2, false, 51, none, none⟩,
  PatternEvent.note ⟨2, false, 52, none, none⟩,
  PatternEvent.note ⟨2, false, 53, none, none⟩,
  PatternEvent.note ⟨2, false, 54, none, none⟩,
  PatternEvent.note ⟨2, false, 55, none, none⟩,
  PatternEvent.note ⟨2, false, 56, none, none⟩,
  PatternEvent.note ⟨2, false, 57, none, none⟩,
  PatternEvent.note ⟨23, false, 57, some 4, none⟩
  ] },
  { index := 27, addr := 0x8BA6, events := [
  PatternEvent.note ⟨2, false, 57, some 17, none⟩,
  PatternEvent.note ⟨2, false, 64, none, none⟩,
  PatternEvent.note ⟨2, false, 69, none, none⟩,
  PatternEvent.note ⟨2, false, 76, none, none⟩,
  PatternEvent.note ⟨2, false, 81, none, none⟩,
  PatternEvent.note ⟨2, false, 76, none, none⟩,
  PatternEvent.note ⟨2, false, 69, none, none⟩,
  PatternEvent.note ⟨2, false, 64, none, none⟩
  ] }
  ]
  let musicSubtunes : List MusicSubtune := [
  { subtune := 0,
    voices := [
    { voice := 0, addr := 0x87E3, indices := [0, 0, 0, 0, 7, 7, 7, 7, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 10, 4, 11, 4, 15, 15, 16, 16, 4, 4, 5, 5, 4, 4, 18], terminator := "restart" },
    { voice := 1, addr := 0x8809, indices := [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 17, 17, 17, 17, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], terminator := "restart" },
    { voice := 2, addr := 0x8840, indices := [0, 0, 0, 0, 6, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 19], terminator := "restart" }
    ]
  },
  { subtune := 1,
    voices := [
    { voice := 0, addr := 0x8898, indices := [23], terminator := "end_song" },
    { voice := 1, addr := 0x889A, indices := [20, 20, 20, 20, 21], terminator := "end_song" },
    { voice := 2, addr := 0x88A0, indices := [22], terminator := "end_song" }
    ]
  },
  { subtune := 2,
    voices := [
    { voice := 0, addr := 0x88A2, indices := [25], terminator := "end_song" },
    { voice := 1, addr := 0x88A4, indices := [27, 27, 27, 27, 27, 27, 26], terminator := "end_song" },
    { voice := 2, addr := 0x88AC, indices := [24], terminator := "end_song" }
    ]
  }
  ]
  let instruments : List Instrument := [
  { id := 0, pulseWidth := 0x0800, ctrl := 0x11, ad := 0x04, sr := 0x0F, vibShift := 0x02, pwm := 0x00, fxFlags := 0x01 },
  { id := 1, pulseWidth := 0x0DC0, ctrl := 0x41, ad := 0x04, sr := 0x09, vibShift := 0x00, pwm := 0x79, fxFlags := 0x05 },
  { id := 2, pulseWidth := 0x01E8, ctrl := 0x41, ad := 0x09, sr := 0x70, vibShift := 0x00, pwm := 0x08, fxFlags := 0x08 },
  { id := 3, pulseWidth := 0x0200, ctrl := 0x81, ad := 0x0A, sr := 0x09, vibShift := 0x00, pwm := 0x00, fxFlags := 0x05 },
  { id := 4, pulseWidth := 0x0300, ctrl := 0x41, ad := 0x09, sr := 0x90, vibShift := 0x02, pwm := 0x00, fxFlags := 0x00 },
  { id := 5, pulseWidth := 0x0154, ctrl := 0x41, ad := 0x09, sr := 0x00, vibShift := 0x02, pwm := 0x08, fxFlags := 0x08 },
  { id := 6, pulseWidth := 0x0980, ctrl := 0x41, ad := 0x07, sr := 0x00, vibShift := 0x02, pwm := 0x41, fxFlags := 0x04 },
  { id := 7, pulseWidth := 0x0C20, ctrl := 0x41, ad := 0x1B, sr := 0x6F, vibShift := 0x01, pwm := 0xE1, fxFlags := 0x00 },
  { id := 8, pulseWidth := 0x0B80, ctrl := 0x41, ad := 0x2F, sr := 0xFF, vibShift := 0x00, pwm := 0x81, fxFlags := 0x00 },
  { id := 9, pulseWidth := 0x0800, ctrl := 0x41, ad := 0x08, sr := 0x0A, vibShift := 0x00, pwm := 0x00, fxFlags := 0x01 },
  { id := 10, pulseWidth := 0x0800, ctrl := 0x81, ad := 0x0F, sr := 0xFF, vibShift := 0x00, pwm := 0x00, fxFlags := 0x01 },
  { id := 11, pulseWidth := 0x0800, ctrl := 0x81, ad := 0x0F, sr := 0xF8, vibShift := 0x00, pwm := 0x00, fxFlags := 0x00 },
  { id := 12, pulseWidth := 0x0800, ctrl := 0x41, ad := 0x05, sr := 0x0A, vibShift := 0x00, pwm := 0x00, fxFlags := 0x01 },
  { id := 13, pulseWidth := 0x0100, ctrl := 0x17, ad := 0x0F, sr := 0x0F, vibShift := 0x01, pwm := 0x00, fxFlags := 0x02 },
  { id := 14, pulseWidth := 0x0180, ctrl := 0x41, ad := 0x0F, sr := 0x0F, vibShift := 0x02, pwm := 0x00, fxFlags := 0x04 },
  { id := 15, pulseWidth := 0x0000, ctrl := 0x11, ad := 0x0F, sr := 0xF0, vibShift := 0x02, pwm := 0x00, fxFlags := 0x02 },
  { id := 16, pulseWidth := 0x0000, ctrl := 0x15, ad := 0x0F, sr := 0x0F, vibShift := 0x00, pwm := 0x00, fxFlags := 0x01 },
  { id := 17, pulseWidth := 0x0800, ctrl := 0x43, ad := 0x06, sr := 0x08, vibShift := 0x00, pwm := 0x00, fxFlags := 0x01 },
  { id := 18, pulseWidth := 0x0800, ctrl := 0x41, ad := 0x05, sr := 0x89, vibShift := 0x02, pwm := 0x00, fxFlags := 0x05 }
  ]
  {
    header         := h
    relocatorSrc   := 0x7B40
    relocatorLen   := 0x0400
    relocatorDst   := 0xC000
    routes         := routes
    samples        := samples
    music          := m
    freqTable      := [
  (22, 1),
  (39, 1),
  (56, 1),
  (75, 1),
  (95, 1),
  (115, 1),
  (138, 1),
  (161, 1),
  (186, 1),
  (212, 1),
  (240, 1),
  (14, 2),
  (45, 2),
  (78, 2),
  (113, 2),
  (150, 2),
  (189, 2),
  (231, 2),
  (19, 3),
  (66, 3),
  (116, 3),
  (169, 3),
  (224, 3),
  (27, 4),
  (90, 4),
  (155, 4),
  (226, 4),
  (44, 5),
  (123, 5),
  (206, 5),
  (39, 6),
  (133, 6),
  (232, 6),
  (81, 7),
  (193, 7),
  (55, 8),
  (180, 8),
  (55, 9),
  (196, 9),
  (87, 10),
  (245, 10),
  (156, 11),
  (78, 12),
  (9, 13),
  (208, 13),
  (163, 14),
  (130, 15),
  (110, 16),
  (104, 17),
  (110, 18),
  (136, 19),
  (175, 20),
  (235, 21),
  (57, 23),
  (156, 24),
  (19, 26),
  (161, 27),
  (70, 29),
  (4, 31),
  (220, 32),
  (208, 34),
  (220, 36),
  (16, 39),
  (94, 41),
  (214, 43),
  (114, 46),
  (56, 49),
  (38, 52),
  (66, 55),
  (140, 58),
  (8, 62),
  (184, 65),
  (160, 69),
  (184, 73),
  (32, 78),
  (188, 82),
  (172, 87),
  (228, 92),
  (112, 98),
  (76, 104),
  (132, 110),
  (24, 117),
  (16, 124),
  (112, 131),
  (64, 139),
  (112, 147),
  (64, 156),
  (120, 165),
  (88, 175),
  (200, 185),
  (224, 196),
  (152, 208),
  (8, 221),
  (48, 234),
  (32, 248),
  (46, 253)
]
    patterns       := patterns
    musicSubtunes  := musicSubtunes
    instruments    := instruments
  }

end LastV8C128NS
