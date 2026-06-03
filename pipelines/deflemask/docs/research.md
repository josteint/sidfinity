## DefleMask v12 (245 tunes)

- **Author:** Leonardo Demartino (Delek)
- **Year:** 2013-2016
- **Documentation:** Good - format spec at https://www.deflemask.com/DMF_SPECS.txt
- **Source available:** No (but third-party player exists: https://github.com/chiptunecafe/deflestream64)

Cross-platform multi-system chiptune tracker (Windows/macOS/Linux/iOS/Android). Supports C64 SID (6581 and 8580), plus Genesis, NES, Game Boy, etc. Not a native C64 tool. DMF file format: zlib-compressed binary, 16-byte magic ".DelekDefleMask.", version byte. System IDs: C64 8580=0x07, C64 6581=0x47, both 3 channels. Exports to .SID, .VGM, .WAV, ROM. The 6502 player is embedded in SID exports. SIDId identifies three variants: DefleMask_v1, DefleMask_v2, DefleMask_v12.
