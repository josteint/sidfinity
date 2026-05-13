"""Combine 5 V3 sub-PSIDs into a single dispatcher PSID.

The parent SID (5_Title_Tunes.sid) is a dispatcher that JSRs to one of
5 separate Hubbard players based on the requested subtune. We rebuild
each player via `pipelines/five_tt_N`, getting 5 V3 .sid files. This
script:

  1. Reads each five_tt_N.sid, extracts its (load, init, play, code).
  2. Allocates a 64K memory buffer.
  3. Copies the parent's binary into the buffer (preserves dispatcher
     code at $0B10/$0B40 plus unrelated bytes).
  4. Overlays each V3 sub's code at its load address (overwrites the
     parent's original sub-player code, which we're replacing).
  5. Patches the dispatcher's 10 JSR targets (5 init + 5 play) to the
     V3 init/play addresses.
  6. Writes a PSID with the parent's metadata + the combined binary.

Output: five_title_tunes.sid at the repo root.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PARENT_SID = REPO / 'data/C64Music/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid'
SUB_SIDS = [REPO / f'five_tt_{i}.sid' for i in range(5)]
OUT_SID = REPO / 'five_title_tunes.sid'


def parse_psid(path: Path) -> tuple[bytes, int, bytes, int, int]:
    """Return (header[124], load_addr, code_bytes, init_addr, play_addr)."""
    b = path.read_bytes()
    hl = int.from_bytes(b[6:8], 'big')
    load = int.from_bytes(b[8:10], 'big')
    payload = b[hl:]
    if load == 0:
        load = int.from_bytes(payload[:2], 'little')
        payload = payload[2:]
    init = int.from_bytes(b[10:12], 'big')
    play = int.from_bytes(b[12:14], 'big')
    return b[:hl], load, payload, init, play


def find_jsr_targets(buf: bytearray, start: int, count: int) -> list[int]:
    """Walk the dispatcher block from `start`, return offsets of the JSR
    operand low-bytes (so caller can patch them)."""
    offsets: list[int] = []
    i = start
    while len(offsets) < count and i < len(buf) - 8:
        if buf[i] == 0xC9 and buf[i + 2] == 0xD0:
            skip = buf[i + 3]
            j = i + 4
            while j < i + 4 + skip:
                if buf[j] == 0x20:    # JSR
                    offsets.append(j + 1)    # operand low byte
                    break
                j += 1
            i = i + 4 + skip
        else:
            i += 1
    return offsets


def patch_jsr(buf: bytearray, op_lo_offset: int, new_target: int) -> None:
    buf[op_lo_offset]     = new_target & 0xFF
    buf[op_lo_offset + 1] = (new_target >> 8) & 0xFF


def main() -> int:
    # 1. Verify pre-reqs
    if not PARENT_SID.exists():
        sys.exit(f"parent SID not found: {PARENT_SID}")
    missing = [s for s in SUB_SIDS if not s.exists()]
    if missing:
        sys.exit(
            f"sub SIDs missing: {missing}\n"
            "Build them first via `lake build sidgen_five_tt_0 ... 4` "
            "and run each `./.lake/build/bin/sidgen_five_tt_N`."
        )

    # 2. Parse parent + subs
    parent_hdr, parent_load, parent_code, parent_init, parent_play = parse_psid(PARENT_SID)
    subs = [parse_psid(s) for s in SUB_SIDS]

    # 3. 64KB memory layout
    mem = bytearray(0x10000)
    # Copy parent binary
    mem[parent_load:parent_load + len(parent_code)] = parent_code

    # 4. Overlay each V3 sub
    high_water = parent_load + len(parent_code)
    for n, (_h, load, code, _init, _play) in enumerate(subs):
        end = load + len(code)
        if end > 0x10000:
            sys.exit(f"sub {n} overflow: ${load:04X}+{len(code)} > 64K")
        mem[load:end] = code
        if end > high_water:
            high_water = end
        print(f"  sub {n}: V3 code at ${load:04X}..${end - 1:04X} ({len(code)} bytes)")

    # 5. Find + patch the 10 dispatcher JSR targets
    #    Parent's init dispatcher starts a few bytes into the init routine
    #    (after `STA $0B6F`). Walker tolerates the leading bytes.
    init_jsrs = find_jsr_targets(mem, parent_init, 5)
    play_jsrs = find_jsr_targets(mem, parent_play, 5)
    if len(init_jsrs) != 5 or len(play_jsrs) != 5:
        sys.exit(f"dispatcher JSR scan failed: init={len(init_jsrs)} play={len(play_jsrs)}")

    print("  patching dispatcher:")
    for n, (init_off, play_off, (_h, _load, _code, s_init, s_play)) in enumerate(
            zip(init_jsrs, play_jsrs, subs)):
        # original target (for diagnostic)
        orig_init = mem[init_off] | (mem[init_off + 1] << 8)
        orig_play = mem[play_off] | (mem[play_off + 1] << 8)
        patch_jsr(mem, init_off, s_init)
        patch_jsr(mem, play_off, s_play)
        print(f"    sub {n}: init JSR ${orig_init:04X}→${s_init:04X}  "
              f"play JSR ${orig_play:04X}→${s_play:04X}")

    # 6. Build the output PSID. Use the parent's header but tighten the
    #    payload to [parent_load .. high_water).
    combined_payload = bytes(mem[parent_load:high_water])

    out_hdr = bytearray(parent_hdr)
    # Force load addr inline (the parent already has loadAddr=0 + inline)
    out_hdr[8:10] = (0).to_bytes(2, 'big')          # = "use first 2 bytes"
    # First 2 bytes of payload = load addr (little endian)
    final = bytes(out_hdr) + parent_load.to_bytes(2, 'little') + combined_payload

    OUT_SID.write_bytes(final)
    print(f"\nwrote {OUT_SID.relative_to(REPO)}: "
          f"{len(final)} bytes total, "
          f"payload ${parent_load:04X}..${high_water - 1:04X} ({len(combined_payload)} bytes)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
