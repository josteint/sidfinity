/*
 * Key struct definitions from src/ct/base.d (CheeseCutter 2.x, GPL, (C) Abaddon)
 * source_url: local /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/src/ct/base.d
 * fetch_date: 2026-06-14
 *
 * Captures: Offsets enum, DatafileOffset enum, Element (4-byte on-disk row),
 *           Tracklist.compact(), Sequence.compact(), constants.
 *
 * See cluster_native_player_and_export.md §3, §6 for analysis.
 */

// Constants
enum {
    MAX_SEQ_ROWS      = 0x40,   // 64 rows max per sequence
    MAX_SEQ_NUM       = 0x80,   // 128 sequences max
    TRACK_LIST_LENGTH = 0x200,  // 512 track entries per orderlist (raw; packed much shorter)
    OFFSETTAB_LENGTH  = 16 * 6, // 96 entries in $0fa0 pointer table (editor only)
    SEQ_END_MARK      = 0xbf,   // sequence end marker byte (NOT $7f like NP20!)
    SONG_REVISION     = 12,     // current .ct file version
    NOTE_KEYOFF       = 1,
    NOTE_KEYON        = 2,
    SUBTUNE_MAX       = 32
}

// Editor-only pointer table (at $0fa0 in editor; ABSENT in exported SID)
enum Offsets {
    Features,                    // $0fa0: requestedTables + instrumentFlags + cmdFlags
    Volume, Editorflag,
    Songsets,                    // track1/2/3 pointers + speed (byte 6) + voicemask (byte 7)
    PlaySpeed, Subnoteplay, Submplayplay,
    InstrumentDescriptionsHeader, PulseDescriptionsHeader,
    FilterDescriptionsHeader, WaveDescriptionsHeader, CmdDescriptionsHeader,
    FREQTABLE, FINETUNE,
    Arp1, Arp2,                  // wave col A (256 bytes), col B (256 bytes)
    FILTTAB, PULSTAB,            // filter table (256 bytes = 64×4), pulse table (256 bytes = 64×4)
    Inst,                        // instrument table (8 columns × 48 = 384 bytes in editor)
    Track1, Track2, Track3,      // orderlists (0x400 bytes each)
    SeqLO, SeqHI,                // sequence pointer tables (256 bytes each)
    CMD1,                        // super table (3 × 64 bytes = 192 bytes)
    S00, SPEED, TRACKLO, VOICE, GATE,
    ChordTable,                  // 128 bytes
    TRANS, ChordIndexTable,      // chord index: 32 bytes
    SHTRANS, FOO3, NEXT, CURINST, GEED, NEWSEQ
}

// .ct file offset map (bytes from start of decompressed zlib blob)
enum DatafileOffset {
    Binary    = 0,              // 64KB C64 memory image
    Header    = 65536,          // ver(1) clock(1) mult(1) sidModel(1) fppres(1) [+speeds +highlight]
    Title     = Header + 256 + 5,   // = 65797  (32 bytes)
    Author    = Title + 32,         // = 65829  (32 bytes)
    Release   = Author + 32,        // = 65861  (32 bytes)
    // [message field at Release+32 = 65893, 32 bytes, not in open() but in save()]
    Insnames  = Title + 40 * 4,     // = 65957  (48 × 32 = 1536 bytes instrument labels)
    Subtunes  = Insnames + 1024 * 2 // = 68005  (32 × 3 × 1024 = 98304 bytes orderlist raw data)
}

// On-disk sequence row: 4 bytes per row, MAX_SEQ_ROWS = 64 rows = 256 bytes max
// data[i*4 + 0] = instrument raw value (0xc0+insno or 0xf0 = no instrument)
// data[i*4 + 1] = tie flag (0x5f = tied, 0xf0 = not tied)
// data[i*4 + 2] = note raw value (0x60+semitone; 0x60=rest, 0x61===, 0x62=+++)
// data[i*4 + 3] = command/super index (0 = no command)
struct Element_layout {
    ubyte instr_raw;   // 0xc0+insno (insno < 0x30) or 0xf0 (no instr). instr.value = raw - 0xc0
    ubyte tie_flag;    // 0x5f = tied; anything else = not tied. note.isTied = (data[1]==0x5f)
    ubyte note_raw;    // note.rawValue; note.value = raw % 0x60; range 0x60-0xbe for notes 0-94
    ubyte cmd_raw;     // super/command index (0-255). cmd.value = raw directly
}

// Track (orderlist) on-disk: 2 bytes per entry
// data[0] = trans: 0x80="no change", 0xa0+n=semitone-adj, 0xf0-0xff=end/wrap
// data[1] = number: sequence number (0-127) or wrap offset low byte
// smashedValue = number | (trans << 8) = big-endian 16-bit for wrap: trans=high, num=low

// Tracklist.compact() output (the byte stream written to C64 memory):
//   [trans_byte] seq_number  repeated  ...  $fX  wrap_lo
// - trans_byte only emitted on change (not on 0x80 "keep" unless boundary)
// - $fX wrap_lo: 2-byte end; value = (wrapOffset*2) | 0xf000
//   player decodes: and #$07 gives low bits; full wrap = twrap + smashedValue/2 & 0x7ff

// Sequence.compact() output alphabet:
//   $c0-$ef    set instrument (value - 0xbf = instrument number, so $c0=0)
//   $f0-$ff    set row delay (low nibble = frames 0-15)
//   $5f        TIE prefix (next byte is a tied note)
//   $00        rest (gate off note, value 0)
//   $01        gate-off (===)
//   $02        gate-on/hold (+++)
//   $03-$5e    note semitone (no following command byte)
//   $60-$bf    note semitone (note+$60; followed by super-command index byte)
//   $bf        SEQ_END_MARK (sequence terminator — also in $60-$bf range! emitted last)
// Notes with commands: rawValue >= 0x60 AND cmd > 0 → emit rawValue, then cmd byte
// Notes without commands: rawValue -= 0x60, emit result in $00-$5e range
// Delays > 15: $f0+15 then $00 rest bytes for overflow frames

// Features block (at $0e00 in editor, EXPORT=FALSE only):
// instrumentFlags = [0, 0, 0, 0, 4, 3, 0, 1]  (column index → table type)
//   0 = no table pointer, 1 = wave table pointer, 3 = pulse table pointer, 4 = filter table pointer
// So: inst byte 4 (INS_FLTP) → filter table row index
//     inst byte 5 (INS_PULSP) → pulse table row index ($00-$3f) or $80+ = direct PW
//     inst byte 7 (INS_ARP)   → wave table start position

// Songsets layout in the exported SID (per subtune):
//   +0,+1   track_ptr_voice0  (little-endian absolute address)
//   +2,+3   track_ptr_voice1
//   +4,+5   track_ptr_voice2
//   +6      speed (songspeeds[i])
//   +7      voicemask = 7 hardcoded (all 3 voices on)
// Total: 8 bytes per subtune. player subinit reads y=subtune*8.
