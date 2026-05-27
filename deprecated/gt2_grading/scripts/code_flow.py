"""
code_flow.py — Control-flow-based code_end detector for 6502 SID binaries.

Uses recursive descent through 6502 control flow to find all reachable code
bytes, then returns the end of the largest contiguous code region.
"""

# 6502 instruction lengths by opcode
_INST_LEN = [0] * 256
for _op in [0x00, 0x08, 0x0A, 0x18, 0x28, 0x2A, 0x38, 0x40, 0x48, 0x4A,
            0x58, 0x60, 0x68, 0x6A, 0x78, 0x88, 0x8A, 0x98, 0x9A, 0xA8,
            0xAA, 0xB8, 0xBA, 0xC8, 0xCA, 0xD8, 0xE8, 0xEA, 0xF8]:
    _INST_LEN[_op] = 1
for _op in range(256):
    if _INST_LEN[_op] > 0:
        continue
    _mode = _op & 0x1F
    if _mode in (0x00, 0x01, 0x02, 0x04, 0x05, 0x06, 0x09, 0x0A,
                 0x10, 0x11, 0x12, 0x14, 0x15, 0x16):
        _INST_LEN[_op] = 2
for _i in range(256):
    if _INST_LEN[_i] == 0:
        _INST_LEN[_i] = 3

# Branch opcodes (all relative, 2-byte instructions)
_BRANCHES = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}


def trace_code(binary, la, init_addr, play_addr):
    """Trace 6502 control flow from init and play entry points.

    Args:
        binary: raw binary payload (no PSID header)
        la: load address
        init_addr: init entry point (absolute address)
        play_addr: play entry point (absolute address)

    Returns:
        set of byte offsets (into binary) marked as code
    """
    bin_len = len(binary)
    code_bytes = set()

    # Convert addresses to binary offsets; skip invalid ones
    worklist = []
    for addr in (init_addr, play_addr):
        off = addr - la
        if 0 <= off < bin_len:
            worklist.append(off)

    visited = set()

    while worklist:
        pos = worklist.pop()

        if pos in visited:
            continue
        if pos < 0 or pos >= bin_len:
            continue
        visited.add(pos)

        opcode = binary[pos]
        insn_len = _INST_LEN[opcode]

        # Check that the full instruction fits in the binary
        if pos + insn_len > bin_len:
            continue

        # Mark all bytes of this instruction as code
        for b in range(pos, pos + insn_len):
            code_bytes.add(b)

        # Determine successors
        if opcode == 0x60 or opcode == 0x40 or opcode == 0x00:
            # RTS, RTI, BRK — no successor
            continue

        if opcode == 0x4C:
            # JMP absolute — single successor at target
            target = binary[pos + 1] | (binary[pos + 2] << 8)
            target_off = target - la
            if 0 <= target_off < bin_len:
                worklist.append(target_off)
            continue

        if opcode == 0x6C:
            # JMP indirect — can't resolve statically
            continue

        if opcode == 0x20:
            # JSR absolute — target is a new entry point, fall-through continues
            target = binary[pos + 1] | (binary[pos + 2] << 8)
            target_off = target - la
            if 0 <= target_off < bin_len:
                worklist.append(target_off)
            # Fall through after JSR
            worklist.append(pos + insn_len)
            continue

        if opcode in _BRANCHES:
            # Relative branch — two successors: taken and not-taken
            # Branch offset is signed byte
            offset = binary[pos + 1]
            if offset >= 0x80:
                offset -= 0x100
            target_off = pos + insn_len + offset
            if 0 <= target_off < bin_len:
                worklist.append(target_off)
            # Fall through (not-taken)
            worklist.append(pos + insn_len)
            continue

        # All other instructions: fall through to next
        worklist.append(pos + insn_len)

    return code_bytes


def find_code_end(binary, la, init_addr, play_addr):
    """Find the end of the largest contiguous code region.

    Uses trace_code to find all code bytes, groups them into contiguous
    regions (allowing gaps of up to 3 bytes), and returns the end offset
    of the largest region.

    Args:
        binary: raw binary payload (no PSID header)
        la: load address
        init_addr: init entry point (absolute address)
        play_addr: play entry point (absolute address)

    Returns:
        End offset (exclusive, into binary) of the largest code region,
        or None if no code was found.
    """
    code_bytes = trace_code(binary, la, init_addr, play_addr)
    if not code_bytes:
        return None

    # Sort all code byte offsets
    sorted_offsets = sorted(code_bytes)

    # Group into contiguous regions (allow gaps of up to 3 bytes)
    regions = []  # list of (start, end) where end is exclusive
    region_start = sorted_offsets[0]
    region_end = sorted_offsets[0] + 1

    for off in sorted_offsets[1:]:
        if off <= region_end + 3:
            # Within gap tolerance — extend region
            region_end = off + 1
        else:
            # New region
            regions.append((region_start, region_end))
            region_start = off
            region_end = off + 1

    regions.append((region_start, region_end))

    # Return end of the largest region
    largest = max(regions, key=lambda r: r[1] - r[0])
    return largest[1]
