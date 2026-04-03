#!/usr/bin/env python3
"""
test_songs.py - Generate test SID files exercising individual SIDfinity player features.

Each test:
  1. Generates xa65 assembly (data tables + player include)
  2. Assembles with xa65
  3. Wraps in PSID v2 header
  4. Runs through siddump to capture register output
  5. Checks specific frames for expected values
  6. Prints PASS/FAIL

Usage:
    source src/env.sh
    python3 src/player/test_songs.py
"""

import os
import struct
import subprocess
import sys
import tempfile

# Paths relative to SIDFINITY_ROOT
ROOT = os.environ.get("SIDFINITY_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PLAYER_BRANCH = "sidfinity-player"
PLAYER_FILE = "src/player/sidfinity_player.s"


def find_tool(name, candidates):
    """Find a tool by trying candidates in order, also check PATH via shutil.which."""
    import shutil
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    # Try PATH
    found = shutil.which(name)
    if found:
        return found
    # Last resort: try running the first candidate directly
    for c in candidates:
        try:
            r = subprocess.run([c, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                return c
        except Exception:
            pass
    return candidates[0]  # Return first candidate, let it fail with a clear error


XA = find_tool("xa", [
    os.path.join(ROOT, "tools", "xa65", "xa", "xa"),
    "/home/jtr/sidfinity/tools/xa65/xa/xa",
])
SIDDUMP = find_tool("siddump", [
    os.path.join(ROOT, "tools", "siddump"),
    "/home/jtr/sidfinity/tools/siddump",
])

# PAL frequency table (same as in sidfinity_player.s / sidfinity.asm)
FREQ_LO = [
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
    0x5A,0x9C,0xE2,0x2D,0x7C,0xCF,0x28,0x85,0xE8,0x52,0xC1,0x37,
    0xB4,0x39,0xC5,0x5A,0xF7,0x9E,0x4F,0x0A,0xD1,0xA3,0x82,0x6E,
    0x68,0x71,0x8A,0xB3,0xEE,0x3C,0x9E,0x15,0xA2,0x46,0x04,0xDC,
    0xD0,0xE2,0x14,0x67,0xDD,0x79,0x3C,0x29,0x44,0x8D,0x08,0xB8,
    0xA1,0xC5,0x28,0xCD,0xBA,0xF1,0x78,0x53,0x87,0x1A,0x10,0x71,
    0x42,0x89,0x4F,0x9B,0x74,0xE2,0xF0,0xA6,0x0E,0x33,0x20,0xFF,
]
FREQ_HI = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF,
]

# Note encoding in pattern: $60 + note number (FIRSTNOTE=0)
NOTE_BASE = 0x60
REST = 0xBD
ENDPATT = 0x00
LOOPSONG = 0xFF
LOOPTBL = 0xFF


def bytes_line(data, label=None):
    """Format a .byte line for xa65 assembly."""
    vals = ",".join(f"${b:02x}" for b in data)
    if label:
        return f"{label}\n    .byte {vals}"
    return f"    .byte {vals}"


def make_freq_table_asm():
    """Generate frequency table assembly."""
    lines = ["mt_freqtbllo"]
    for i in range(0, len(FREQ_LO), 12):
        chunk = FREQ_LO[i:i+12]
        lines.append("    .byte " + ",".join(f"${b:02x}" for b in chunk))
    lines.append("mt_freqtblhi")
    for i in range(0, len(FREQ_HI), 12):
        chunk = FREQ_HI[i:i+12]
        lines.append("    .byte " + ",".join(f"${b:02x}" for b in chunk))
    return "\n".join(lines)


def make_instrument_table_asm(instruments):
    """Generate instrument table assembly from list of instrument dicts.

    Each instrument dict has: ad, sr, wave_ptr, pulse_ptr, filt_ptr,
    vib_param, vib_delay, gate_timer, first_wave.
    instruments[0] is instrument 1 (1-indexed in player).
    """
    fields = [
        ("mt_insad",        "ad"),
        ("mt_inssr",        "sr"),
        ("mt_inswaveptr",   "wave_ptr"),
        ("mt_inspulseptr",  "pulse_ptr"),
        ("mt_insfiltptr",   "filt_ptr"),
        ("mt_insvibparam",  "vib_param"),
        ("mt_insvibdelay",  "vib_delay"),
        ("mt_insgatetimer", "gate_timer"),
        ("mt_insfirstwave", "first_wave"),
    ]
    lines = []
    for label, key in fields:
        vals = [inst.get(key, 0) for inst in instruments]
        lines.append(bytes_line(vals, label))
    return "\n".join(lines)


def make_data_asm(orderlists, patterns, instruments, wave_table=None,
                  pulse_table=None, filt_table=None, speed_table=None,
                  base=0x1000, default_tempo=6):
    """Generate complete data section assembly.

    orderlists: list of 3 orderlists (one per channel), each a list of bytes.
                Format: [patt_id, transpose_byte($80-based), ...] + [$FF, restart_pos]
    patterns: list of pattern byte arrays
    instruments: list of instrument dicts (see make_instrument_table_asm)
    wave_table: list of (left, right) byte tuples, or None
    """
    lines = []
    lines.append(f"base = ${base:04x}")
    lines.append(f"DEFAULTTEMPO = {default_tempo}")
    lines.append(f"SIDBASE = $d400")
    lines.append(f"FIRSTNOTE = 0")
    lines.append(f"ADPARAM = $0f")
    lines.append(f"SRPARAM = $00")
    lines.append(f"FIRSTNOHRINSTR = $3f")
    lines.append(f"FIRSTLEGATOINSTR = $3f")
    lines.append("")

    # Orderlist pointers -- 3 channels, song index 0 means ch0=entry0, ch1=entry1, ch2=entry2
    # mt_songtbllo/hi: indexed by song number (channel's mt_chnsongnum)
    # For subtune 0: ch0 gets songidx=0, ch1=1, ch2=2
    lines.append("; Orderlist pointer table (3 entries for 3 channels)")
    ol_labels = []
    for i in range(3):
        ol_labels.append(f"orderlist_{i}")
    lines.append(f"mt_songtbllo\n    .byte {','.join('<' + l for l in ol_labels)}")
    lines.append(f"mt_songtblhi\n    .byte {','.join('>' + l for l in ol_labels)}")
    lines.append("")

    # Pattern pointer table
    lines.append("; Pattern pointer table")
    pat_labels = [f"pattern_{i}" for i in range(len(patterns))]
    lines.append(f"mt_patttbllo\n    .byte {','.join('<' + l for l in pat_labels)}")
    lines.append(f"mt_patttblhi\n    .byte {','.join('>' + l for l in pat_labels)}")
    lines.append("")

    # Instrument tables
    lines.append("; Instrument tables (1-indexed)")
    lines.append(make_instrument_table_asm(instruments))
    lines.append("")

    # Wave table
    lines.append("; Wave table (left=waveform, right=note offset)")
    if wave_table:
        left = [w[0] for w in wave_table]
        right = [w[1] for w in wave_table]
    else:
        left = [0]
        right = [0]
    lines.append(bytes_line(left, "mt_wavetbl"))
    lines.append(bytes_line(right, "mt_notetbl"))
    lines.append("")

    # Pulse table
    lines.append("; Pulse table")
    if pulse_table:
        pt = [p[0] for p in pulse_table]
        ps = [p[1] for p in pulse_table]
    else:
        pt = [0]
        ps = [0]
    lines.append(bytes_line(pt, "mt_pulsetimetbl"))
    lines.append(bytes_line(ps, "mt_pulsespdtbl"))
    lines.append("")

    # Filter table
    lines.append("; Filter table")
    if filt_table:
        ft = [f[0] for f in filt_table]
        fs = [f[1] for f in filt_table]
    else:
        ft = [0]
        fs = [0]
    lines.append(bytes_line(ft, "mt_filttimetbl"))
    lines.append(bytes_line(fs, "mt_filtspdtbl"))
    lines.append("")

    # Speed table
    lines.append("; Speed table")
    if speed_table:
        sl = [s[0] for s in speed_table]
        sr = [s[1] for s in speed_table]
    else:
        sl = [0]
        sr = [0]
    lines.append(bytes_line(sl, "mt_speedlefttbl"))
    lines.append(bytes_line(sr, "mt_speedrighttbl"))
    lines.append("")

    # Frequency table
    lines.append("; Frequency table")
    lines.append(make_freq_table_asm())
    lines.append("")

    # Orderlist data
    lines.append("; Orderlist data")
    for i, ol in enumerate(orderlists):
        lines.append(bytes_line(ol, f"orderlist_{i}"))
    lines.append("")

    # Pattern data
    lines.append("; Pattern data")
    for i, pat in enumerate(patterns):
        lines.append(bytes_line(pat, f"pattern_{i}"))
    lines.append("")

    return "\n".join(lines)


def get_player_source():
    """Get the SIDfinity player source from the sidfinity-player branch."""
    try:
        # Use -C to ensure we reference the main repo where the branch exists
        result = subprocess.run(
            ["git", "-C", "/home/jtr/sidfinity", "show", f"{PLAYER_BRANCH}:{PLAYER_FILE}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def strip_player_defines(player_src):
    """Remove #ifndef/define blocks for symbols we define in data section."""
    lines = player_src.split("\n")
    out = []
    skip_depth = 0
    defines_to_strip = {
        "base", "SIDBASE", "FIRSTNOTE", "DEFAULTTEMPO", "ADPARAM", "SRPARAM",
        "FIRSTNOHRINSTR", "FIRSTLEGATOINSTR",
        "mt_songtbllo",  # triggers the whole dummy data block
    }
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#ifndef"):
            sym = line.split()[1] if len(line.split()) > 1 else ""
            if sym in defines_to_strip:
                # Skip until matching #endif
                depth = 1
                i += 1
                while i < len(lines) and depth > 0:
                    l = lines[i].strip()
                    if l.startswith("#ifndef") or l.startswith("#ifdef"):
                        depth += 1
                    elif l.startswith("#endif"):
                        depth -= 1
                    i += 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def make_psid_header(load_addr, init_addr, play_addr, title="Test", author="test_songs.py", released="2026"):
    """Create a PSID v2 header (124 bytes)."""
    title_b = title.encode("ascii")[:31].ljust(32, b"\x00")
    author_b = author.encode("ascii")[:31].ljust(32, b"\x00")
    released_b = released.encode("ascii")[:31].ljust(32, b"\x00")

    header = struct.pack(">4sHHHHHHHBB",
        b"PSID",       # magicID
        2,             # version
        0x007C,        # dataOffset (124 bytes)
        load_addr,     # loadAddress
        init_addr,     # initAddress
        play_addr,     # playAddress
        1,             # songs
        1,             # startSong
        0x00000000 >> 16,  # speed (0 = VBI for all 32 subtunes)
        0x00000000 & 0xFF
    )
    # speed is 4 bytes
    header = struct.pack(">4sHHHHHHH",
        b"PSID",
        2,
        0x007C,
        load_addr,
        init_addr,
        play_addr,
        1,
        1,
    )
    speed = struct.pack(">I", 0)  # VBI
    header += speed
    header += title_b + author_b + released_b
    # flags: 0x0014 = MOS6581 + PAL
    flags = struct.pack(">H", 0x0014)
    header += flags
    # Pad to 124 bytes
    header += b"\x00" * (124 - len(header))
    return header


def assemble_and_wrap(asm_source, base_addr=0x1000, title="Test"):
    """Assemble xa65 source and wrap in PSID v2 header. Returns .sid bytes or None."""
    with tempfile.NamedTemporaryFile(suffix=".s", mode="w", delete=False) as f:
        f.write(asm_source)
        src_path = f.name

    bin_path = src_path.replace(".s", ".bin")
    try:
        result = subprocess.run(
            [XA, "-o", bin_path, src_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  Assembly FAILED: {result.stderr.strip()}")
            return None

        with open(bin_path, "rb") as f:
            code = f.read()

        init_addr = base_addr  # jmp init is at base+0
        play_addr = base_addr + 3  # jmp play is at base+3

        # PSID header with loadAddress=0 means data has 2-byte load address prefix
        # Use loadAddress=base_addr (non-zero) so no prefix needed
        header = make_psid_header(base_addr, init_addr, play_addr, title=title)
        return header + code
    finally:
        for p in [src_path, bin_path]:
            if os.path.exists(p):
                os.unlink(p)


def run_siddump(sid_bytes, duration=2):
    """Run siddump on a SID file, return list of frame dicts."""
    with tempfile.NamedTemporaryFile(suffix=".sid", delete=False) as f:
        f.write(sid_bytes)
        sid_path = f.name

    try:
        result = subprocess.run(
            [SIDDUMP, sid_path, "--duration", str(duration)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  siddump FAILED (exit {result.returncode}): {result.stderr.strip()}")
            return None

        lines = result.stdout.strip().split("\n")
        if len(lines) < 3:
            print(f"  siddump: too few output lines ({len(lines)})")
            return None

        # Line 0: JSON metadata
        # Line 1: CSV header
        # Lines 2+: data
        header_cols = lines[1].split(",")
        frames = []
        for line in lines[2:]:
            vals = line.split(",")
            frame = {}
            for col, val in zip(header_cols, vals):
                frame[col] = int(val, 16)
            frames.append(frame)
        return frames
    finally:
        os.unlink(sid_path)


def build_full_asm(data_asm, base=0x1000):
    """Combine data definitions with player source into complete assembly."""
    player_src = get_player_source()
    if player_src is None:
        print("ERROR: Cannot get player source from sidfinity-player branch")
        sys.exit(1)

    player_clean = strip_player_defines(player_src)

    # The data section goes first (defines + data), then the player code
    # But the player has `* = base` which sets the origin.
    # We need: data defines first, then player (which includes * = base),
    # then data bytes after the player code.

    # Strategy: put defines at top, player code, then data bytes
    # The data_asm has both defines and .byte data. Split them.

    define_lines = []
    data_lines = []
    in_data = False
    for line in data_asm.split("\n"):
        stripped = line.strip()
        if stripped.startswith(".byte") or stripped.startswith(";") and in_data:
            data_lines.append(line)
            in_data = True
        elif any(stripped.startswith(prefix) for prefix in ["mt_", "orderlist_", "pattern_"]):
            data_lines.append(line)
            in_data = True
        elif stripped.startswith(".byte"):
            data_lines.append(line)
        elif in_data and stripped == "":
            data_lines.append(line)
        else:
            define_lines.append(line)
            in_data = False

    # Actually, simpler approach: put all data AFTER the player, using labels.
    # The player references data by label. xa65 will resolve forward references.

    full = []
    full.append("; === Test song data defines ===")
    # Just the #define-style lines (base, DEFAULTTEMPO, etc)
    for line in data_asm.split("\n"):
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith(";") and not stripped.startswith("."):
            # Check if it's a simple define like "base = $1000"
            parts = stripped.split("=", 1)
            name = parts[0].strip()
            if name in {"base", "DEFAULTTEMPO", "SIDBASE", "FIRSTNOTE", "ADPARAM",
                        "SRPARAM", "FIRSTNOHRINSTR", "FIRSTLEGATOINSTR"}:
                full.append(stripped)
    full.append("")
    full.append("; === Player code ===")
    full.append(player_clean)
    full.append("")
    full.append("; === Test song data ===")
    # Now emit data labels and bytes (skip the defines we already emitted)
    skip_names = {"base", "DEFAULTTEMPO", "SIDBASE", "FIRSTNOTE", "ADPARAM",
                  "SRPARAM", "FIRSTNOHRINSTR", "FIRSTLEGATOINSTR"}
    for line in data_asm.split("\n"):
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith(";") and not stripped.startswith("."):
            parts = stripped.split("=", 1)
            name = parts[0].strip()
            if name in skip_names:
                continue
        full.append(line)

    return "\n".join(full)


def build_full_asm_v2(data_asm, base=0x1000):
    """Simpler approach: emit defines, then player source, then data tables."""
    player_src = get_player_source()
    if player_src is None:
        print("ERROR: Cannot get player source from sidfinity-player branch")
        sys.exit(1)

    player_clean = strip_player_defines(player_src)

    # Extract just the define lines from data_asm
    defines = []
    data_body = []
    for line in data_asm.split("\n"):
        stripped = line.strip()
        # Simple assignment that's a config define
        if "=" in stripped and not stripped.startswith(";") and not stripped.startswith("."):
            parts = stripped.split("=", 1)
            name = parts[0].strip()
            if name in {"base", "DEFAULTTEMPO", "SIDBASE", "FIRSTNOTE", "ADPARAM",
                        "SRPARAM", "FIRSTNOHRINSTR", "FIRSTLEGATOINSTR"}:
                defines.append(line)
                continue
        data_body.append(line)

    asm = "\n".join(defines) + "\n\n" + player_clean + "\n\n" + "\n".join(data_body) + "\n"
    return asm


# =============================================================================
# Silence pattern: just end-of-pattern immediately
# =============================================================================
SILENT_PATTERN = [ENDPATT]

# Orderlist that points to pattern 0 and loops: [patt0, $80(no transpose), $FF, $00]
def silent_orderlist(patt_id=0):
    return [patt_id, 0x80, LOOPSONG, 0x00]


def default_instrument(ad=0x09, sr=0x00, first_wave=0x41, gate_timer=2, wave_ptr=1):
    """Default instrument. wave_ptr=1 means point to wave table row 1 (1-indexed)."""
    return {
        "ad": ad,
        "sr": sr,
        "wave_ptr": wave_ptr,
        "pulse_ptr": 0,
        "filt_ptr": 0,
        "vib_param": 0,
        "vib_delay": 0,
        "gate_timer": gate_timer,
        "first_wave": first_wave,
    }


# Standard wave table: pulse waveform + play note freq, looping
# Row 1: ($51, $80) = waveform $41 (pulse), relative note offset 0 (play base note)
# Row 2: ($FF, $01) = loop to row 1
STANDARD_WAVE_TABLE = [
    (0x51, 0x80),   # row 1: pulse ($41+$10=$51), play note freq ($80=relative 0)
    (LOOPTBL, 0x01),  # row 2: loop to row 1
]


# =============================================================================
# Test 1: Single note
# =============================================================================
def test_single_note():
    """One instrument, one pattern with note C4 (note 48), tempo 6.
    Verify: after init frames, freq_hi=$14 for note 48, waveform=$41."""

    note = 48  # C4
    expected_freq_hi = FREQ_HI[note]  # $14
    expected_freq_lo = FREQ_LO[note]  # $68

    instruments = [default_instrument(ad=0x09, sr=0x00, first_wave=0x41, gate_timer=2)]

    # Pattern: instrument 1, note C4, end
    # Instrument byte = 1 (< $40), note = $60 + 48 = $90
    pattern_data = [0x01, NOTE_BASE + note, ENDPATT]

    # Silent pattern for channels 2 and 3
    patterns = [pattern_data, SILENT_PATTERN]

    # Orderlists: ch0 plays pattern 0 looping, ch1/ch2 play pattern 1 (silent)
    orderlists = [
        [0x00, 0x80, LOOPSONG, 0x00],  # ch0: pattern 0, no transpose, loop to 0
        [0x01, 0x80, LOOPSONG, 0x00],  # ch1: pattern 1 (silent), loop
        [0x01, 0x80, LOOPSONG, 0x00],  # ch2: pattern 1 (silent), loop
    ]

    data_asm = make_data_asm(orderlists, patterns, instruments,
                             wave_table=STANDARD_WAVE_TABLE, default_tempo=6)
    full_asm = build_full_asm_v2(data_asm)

    sid = assemble_and_wrap(full_asm, title="test_single_note")
    if sid is None:
        return False

    frames = run_siddump(sid, duration=1)
    if frames is None:
        return False

    # The player needs a few frames to initialize and read the first note.
    # Frame 0: mt_fullinit runs (counter=1, so tick0 fires on frame 1)
    # Frame 1: tick0 - reads orderlist, loads pattern, reads note, writes regs
    # Frame 2: counter not 0, wave table runs
    # Check frames 2-10 for expected frequency and waveform

    passed = True
    found_note = False
    # Check frames 1-15: freq appears one frame after gate-on (wave table runs next frame)
    for i, f in enumerate(frames[1:16], 1):
        fhi = f.get("V1_FREQ_HI", 0)
        flo = f.get("V1_FREQ_LO", 0)
        ctrl = f.get("V1_CTRL", 0)
        ad = f.get("V1_AD", 0)

        if fhi == expected_freq_hi and (ctrl & 0x01) == 1:
            found_note = True
            # Verify waveform includes pulse ($41) with gate
            if (ctrl & 0xF0) != 0x40:
                print(f"  Frame {i}: expected pulse waveform ($4x), got CTRL=${ctrl:02x}")
                passed = False
            if ad != 0x09:
                print(f"  Frame {i}: expected AD=$09, got ${ad:02x}")
                passed = False
            break

    if not found_note:
        print(f"  Never found note 48 (freq_hi=${expected_freq_hi:02x}) with gate on in frames 1-15")
        for i, f in enumerate(frames[:16]):
            print(f"    Frame {i}: freq=${f.get('V1_FREQ_HI',0):02x}{f.get('V1_FREQ_LO',0):02x} "
                  f"ctrl=${f.get('V1_CTRL',0):02x} ad=${f.get('V1_AD',0):02x} sr=${f.get('V1_SR',0):02x}")
        passed = False

    return passed


# =============================================================================
# Test 2: Wave table
# =============================================================================
def test_wave_table():
    """Instrument with wave table: noise->pulse->loop.
    Wave table (1-indexed): row1=($91,$00), row2=($51,$00), row3=($FF,$01=loop to row1).
    Note: wave table waveforms are stored with +$10 offset in the player
    ($10 is subtracted, values >= $10 are waveforms).
    Actually in the player: values < $10 are delays, >= $10 have $10 subtracted
    and stored as wave. So $91-$10=$81=noise, $51-$10=$41=pulse.

    Verify: waveform alternates $81,$41,$81,$41... (noise, pulse, noise, pulse)."""

    note = 48  # C4

    # Wave table: row1=(noise=$91, note_offset=0), row2=(pulse=$51, note_offset=0), row3=(loop=$FF, target=1)
    # In the player, waveform values have $10 added: $81+$10=$91, $41+$10=$51
    wave_table = [
        (0x91, 0x00),  # row 1: noise ($81 after -$10), no note change (0 = no freq update)
        (0x51, 0x00),  # row 2: pulse ($41 after -$10), no note change
        (LOOPTBL, 0x01),  # row 3: loop back to row 1
    ]

    instruments = [default_instrument(ad=0x09, sr=0x00, first_wave=0x41, gate_timer=2, wave_ptr=1)]

    pattern_data = [0x01, NOTE_BASE + note, ENDPATT]
    patterns = [pattern_data, SILENT_PATTERN]

    orderlists = [
        [0x00, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
    ]

    data_asm = make_data_asm(orderlists, patterns, instruments,
                             wave_table=wave_table, default_tempo=6)
    full_asm = build_full_asm_v2(data_asm)

    sid = assemble_and_wrap(full_asm, title="test_wave_table")
    if sid is None:
        return False

    frames = run_siddump(sid, duration=1)
    if frames is None:
        return False

    # After the note triggers, wave table should cycle: noise, pulse, noise, pulse...
    # The first_wave ($41) is used on the note-trigger frame itself.
    # Then wave table kicks in on subsequent frames.
    # With gate_timer=2 and tempo=6, note triggers on tick 0 (counter==gate_timer).

    # Find the first frame where gate is on
    note_frame = None
    for i, f in enumerate(frames):
        if f.get("V1_CTRL", 0) & 0x01:
            note_frame = i
            break

    if note_frame is None:
        print("  Never found gate-on frame")
        for i, f in enumerate(frames[:15]):
            print(f"    Frame {i}: ctrl=${f.get('V1_CTRL',0):02x}")
        return False

    # Check waveform sequence after note_frame
    # note_frame: first_wave $41 (pulse+gate)
    # note_frame+1: wave table row 1 -> $81 (noise) with gate -> $81
    # note_frame+2: wave table row 2 -> $41 (pulse) with gate -> $41
    # note_frame+3: loop -> row 1 -> $81
    # note_frame+4: row 2 -> $41

    expected_sequence = [0x81, 0x41, 0x81, 0x41]
    actual = []
    passed = True

    for j, exp_wave in enumerate(expected_sequence):
        fi = note_frame + 1 + j
        if fi >= len(frames):
            print(f"  Not enough frames (need {fi}, have {len(frames)})")
            passed = False
            break
        ctrl = frames[fi].get("V1_CTRL", 0)
        actual.append(ctrl)
        # The gate bit should still be on, so expected is wave | gate
        exp_with_gate = exp_wave | 0x01
        if ctrl != exp_with_gate:
            print(f"  Frame {fi}: expected CTRL=${exp_with_gate:02x} ({['noise','pulse','noise','pulse'][j]}+gate), got ${ctrl:02x}")
            passed = False

    if not passed:
        print(f"  Note triggered at frame {note_frame}")
        for i in range(max(0, note_frame-1), min(len(frames), note_frame+8)):
            f = frames[i]
            print(f"    Frame {i}: ctrl=${f.get('V1_CTRL',0):02x} freq=${f.get('V1_FREQ_HI',0):02x}{f.get('V1_FREQ_LO',0):02x}")

    return passed


# =============================================================================
# Test 3: Hard restart
# =============================================================================
def test_hard_restart():
    """Two notes in pattern (C4, C5), gate_timer=2.
    Verify: gate bit toggles off then on, with ADPARAM written during HR."""

    note1 = 48  # C4
    note2 = 60  # C5

    instruments = [default_instrument(ad=0x09, sr=0xA0, first_wave=0x41, gate_timer=2)]

    # Pattern: instr 1, note C4, note C5, end
    pattern_data = [0x01, NOTE_BASE + note1, NOTE_BASE + note2, ENDPATT]
    patterns = [pattern_data, SILENT_PATTERN]

    orderlists = [
        [0x00, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
    ]

    data_asm = make_data_asm(orderlists, patterns, instruments,
                             wave_table=STANDARD_WAVE_TABLE, default_tempo=6)
    full_asm = build_full_asm_v2(data_asm)

    sid = assemble_and_wrap(full_asm, title="test_hard_restart")
    if sid is None:
        return False

    frames = run_siddump(sid, duration=2)
    if frames is None:
        return False

    # Look for the hard restart sequence:
    # When 2nd note is read, HR writes ADPARAM=$0F, SRPARAM=$00 and gate=$FE (gate off)
    # Then on next tick0, the note init fires with proper ADSR and gate on.

    # Find frame where gate goes off (HR) after first note
    found_hr = False
    found_note2 = False
    passed = True

    first_gate_on = None
    for i, f in enumerate(frames):
        ctrl = f.get("V1_CTRL", 0)
        if ctrl & 0x01 and first_gate_on is None:
            first_gate_on = i

    if first_gate_on is None:
        print("  Never found first gate-on")
        return False

    # After the first note, look for gate-off (HR) then gate-on (new note)
    for i in range(first_gate_on + 1, min(len(frames), first_gate_on + 20)):
        ctrl = frames[i].get("V1_CTRL", 0)
        ad = frames[i].get("V1_AD", 0)
        sr = frames[i].get("V1_SR", 0)
        fhi = frames[i].get("V1_FREQ_HI", 0)

        if not (ctrl & 0x01) and not found_hr:
            # Gate off - this is HR frame
            found_hr = True
            # During HR, AD should be ADPARAM ($0F) and SR should be SRPARAM ($00)
            if ad != 0x0F:
                print(f"  HR frame {i}: expected AD=$0F (ADPARAM), got ${ad:02x}")
                passed = False
            if sr != 0x00:
                print(f"  HR frame {i}: expected SR=$00 (SRPARAM), got ${sr:02x}")
                passed = False

        if found_hr and (ctrl & 0x01):
            # Gate back on - new note
            found_note2 = True
            # ADSR should be restored to instrument values on gate-on frame
            if ad != 0x09:
                print(f"  Note2 frame {i}: expected AD=$09, got ${ad:02x}")
                passed = False
            # Freq updates 1 frame after gate-on (wave table delay)
            # Check the next frame for the new frequency
            if i + 1 < len(frames):
                next_fhi = frames[i + 1].get("V1_FREQ_HI", 0)
                exp_fhi = FREQ_HI[note2]
                if next_fhi != exp_fhi:
                    print(f"  Note2 frame {i+1}: expected freq_hi=${exp_fhi:02x}, got ${next_fhi:02x}")
                    passed = False
            break

    if not found_hr:
        print("  Never found hard restart (gate-off) after first note")
        for i in range(max(0,first_gate_on-1), min(len(frames), first_gate_on+15)):
            f = frames[i]
            print(f"    Frame {i}: ctrl=${f.get('V1_CTRL',0):02x} ad=${f.get('V1_AD',0):02x} "
                  f"sr=${f.get('V1_SR',0):02x} fhi=${f.get('V1_FREQ_HI',0):02x}")
        passed = False

    if not found_note2:
        print("  Never found second note (gate-on after HR)")
        passed = False

    return passed


# =============================================================================
# Test 4: Tempo change
# =============================================================================
def test_tempo_change():
    """Pattern with SETTEMPO command (fx=$0F, param=$0C = tempo 12).
    Verify: note spacing changes from 6 frames to 12 frames.

    Pattern format for FX-only command: $5F (FXONLY | $0F), param, then note.
    Actually: FX byte = $40 + (fx_num << 0) ... let me check the player.

    In the player: bytes $40-$4F are FX + param, $50-$5F are FXONLY.
    $50+$0F = $5F means FX $0F (set tempo) with param following, no note.
    """

    note1 = 48  # C4
    note2 = 60  # C5

    instruments = [default_instrument(ad=0x09, sr=0x00, first_wave=0x41, gate_timer=2)]

    # Pattern: instr 1, note C4, settempo(12), note C5, end
    # FX-only byte for tempo: $5F (FXONLY | $0F), then param $0C
    pattern_data = [
        0x01,               # instrument 1
        NOTE_BASE + note1,  # note C4
        0x5F, 0x0C,         # FXONLY + FX $0F (set tempo), param $0C (=12)
        NOTE_BASE + note2,  # note C5
        ENDPATT
    ]
    patterns = [pattern_data, SILENT_PATTERN]

    orderlists = [
        [0x00, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
        [0x01, 0x80, LOOPSONG, 0x00],
    ]

    data_asm = make_data_asm(orderlists, patterns, instruments,
                             wave_table=STANDARD_WAVE_TABLE, default_tempo=6)
    full_asm = build_full_asm_v2(data_asm)

    sid = assemble_and_wrap(full_asm, title="test_tempo_change")
    if sid is None:
        return False

    frames = run_siddump(sid, duration=2)
    if frames is None:
        return False

    # Find when note1 and note2 appear (by frequency change)
    note1_fhi = FREQ_HI[note1]
    note2_fhi = FREQ_HI[note2]

    note1_frame = None
    note2_frame = None

    # Freq appears 1 frame after gate-on due to wave table delay
    # Track gate-on transitions and check freq on next frame
    prev_ctrl = 0
    for i, f in enumerate(frames):
        fhi = f.get("V1_FREQ_HI", 0)
        ctrl = f.get("V1_CTRL", 0)
        if fhi == note1_fhi and note1_frame is None:
            note1_frame = i
        if fhi == note2_fhi and note2_frame is None and note1_frame is not None:
            note2_frame = i
            break
        prev_ctrl = ctrl

    passed = True
    if note1_frame is None:
        print("  Never found note 1")
        passed = False
    if note2_frame is None:
        print("  Never found note 2")
        for i, f in enumerate(frames[:30]):
            print(f"    Frame {i}: fhi=${f.get('V1_FREQ_HI',0):02x} ctrl=${f.get('V1_CTRL',0):02x}")
        passed = False

    if note1_frame is not None and note2_frame is not None:
        spacing = note2_frame - note1_frame
        # The FXONLY command consumes one tick between note1 and note2.
        # With initial tempo 6: note1 fires, then 6 frames later the FX command
        # sets tempo to 12. Then 12 frames later note2's HR fires, then 12 more
        # for note2 init. Total ~6+12+HR frames. We mainly verify the spacing
        # is significantly larger than the initial tempo (6), proving tempo changed.
        # Without tempo change it would be ~12 frames (2 ticks * 6).
        # With tempo change: ~18-24 frames.
        if spacing < 15:
            print(f"  Note spacing: {spacing} frames (expected >15 due to tempo change to 12)")
            passed = False
        elif spacing > 30:
            print(f"  Note spacing: {spacing} frames (expected <30)")
            passed = False

    return passed


# =============================================================================
# Test 5: Orderlist loop
# =============================================================================
def test_orderlist_loop():
    """Two patterns, orderlist [0, 1, loop to start].
    Verify: patterns repeat (note sequence appears twice)."""

    note_a = 48  # C4 in pattern 0
    note_b = 60  # C5 in pattern 1

    instruments = [default_instrument(ad=0x09, sr=0x00, first_wave=0x41, gate_timer=2)]

    # Pattern 0: instr 1, note A, end
    pat0 = [0x01, NOTE_BASE + note_a, ENDPATT]
    # Pattern 1: instr 1, note B, end
    pat1 = [0x01, NOTE_BASE + note_b, ENDPATT]
    patterns = [pat0, pat1, SILENT_PATTERN]

    # Orderlist for ch0: pattern 0, pattern 1, loop to position 0
    # Format: [patt_id, transpose($80), patt_id, transpose($80), $FF, restart_pos]
    orderlists = [
        [0x00, 0x80, 0x01, 0x80, LOOPSONG, 0x00],
        [0x02, 0x80, LOOPSONG, 0x00],  # ch1: silent, loop
        [0x02, 0x80, LOOPSONG, 0x00],  # ch2: silent, loop
    ]

    data_asm = make_data_asm(orderlists, patterns, instruments,
                             wave_table=STANDARD_WAVE_TABLE, default_tempo=6)
    full_asm = build_full_asm_v2(data_asm)

    sid = assemble_and_wrap(full_asm, title="test_orderlist_loop")
    if sid is None:
        return False

    frames = run_siddump(sid, duration=3)
    if frames is None:
        return False

    # Expect sequence: note_a, note_b, note_a, note_b (looping)
    fhi_a = FREQ_HI[note_a]
    fhi_b = FREQ_HI[note_b]

    # Collect all note-change events
    note_events = []
    prev_fhi = 0
    for i, f in enumerate(frames):
        fhi = f.get("V1_FREQ_HI", 0)
        ctrl = f.get("V1_CTRL", 0)
        if fhi != prev_fhi and (ctrl & 0x01):
            note_events.append((i, fhi))
            prev_fhi = fhi

    passed = True
    # Should see at least: A, B, A, B
    expected = [fhi_a, fhi_b, fhi_a, fhi_b]
    actual_fhis = [ev[1] for ev in note_events]

    if len(actual_fhis) < 4:
        print(f"  Only found {len(actual_fhis)} note events, expected at least 4")
        for i, f in enumerate(frames[:40]):
            fhi = f.get("V1_FREQ_HI", 0)
            ctrl = f.get("V1_CTRL", 0)
            if ctrl & 0x01:
                print(f"    Frame {i}: fhi=${fhi:02x} ctrl=${ctrl:02x}")
        passed = False
    else:
        for j in range(4):
            if actual_fhis[j] != expected[j]:
                print(f"  Event {j}: expected fhi=${expected[j]:02x}, got ${actual_fhis[j]:02x}")
                passed = False

    return passed


# =============================================================================
# Main
# =============================================================================
def main():
    # Verify tools exist
    if not os.path.isfile(XA):
        print(f"ERROR: xa65 assembler not found at {XA}")
        print("  Build it: cd tools/xa65/xa && make -j$(nproc)")
        sys.exit(1)
    if not os.path.isfile(SIDDUMP):
        print(f"ERROR: siddump not found at {SIDDUMP}")
        print("  Build it: bash tools/build.sh")
        sys.exit(1)

    # Verify player source is accessible
    if get_player_source() is None:
        print(f"ERROR: Cannot get player from branch '{PLAYER_BRANCH}'")
        sys.exit(1)

    tests = [
        ("test_single_note",    test_single_note),
        ("test_wave_table",     test_wave_table),
        ("test_hard_restart",   test_hard_restart),
        ("test_tempo_change",   test_tempo_change),
        ("test_orderlist_loop", test_orderlist_loop),
    ]

    results = []
    for name, func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        try:
            ok = func()
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            ok = False

        status = "PASS" if ok else "FAIL"
        print(f"  Result: {status}")
        results.append((name, ok))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
