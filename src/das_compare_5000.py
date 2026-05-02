#!/usr/bin/env python3
"""
Compare Das Model output vs ground truth (HubbardEmu) for the full song.
Track register VALUE CHANGES only, per user instructions.
"""
import sys
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

SID_PATH = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                         'Hubbard_Rob', 'Commando.sid')
DM_SID   = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_das_model.sid')

NF = 11779  # FULL SONG
STOP_ON_FIRST = False  # set True to stop at first mismatch

def get_writes_py65(sid_path, n_frames):
    """Return per-frame lists of (addr, value) for all register CHANGES."""
    from py65.devices.mpu6502 import MPU

    with open(sid_path, 'rb') as f:
        sid = f.read()
    hl = struct.unpack('>H', sid[6:8])[0]
    la = struct.unpack('>H', sid[8:10])[0]
    code = sid[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]; code = code[2:]
    mem = bytearray(65536); mem[la:la+len(code)] = code
    m = MPU(); m.memory = bytearray(mem); m.memory[0xFFFE] = 0x60

    def run(pc, a=0):
        m.sp = 0xFD; m.memory[0x01FF] = 0xFF; m.memory[0x01FE] = 0xFD
        m.pc = pc; m.a = a
        steps = 0
        while m.pc != 0xFFFE and steps < 2000000:
            m.step(); steps += 1

    # Init
    run(la, 0)
    play_addr = la + 3

    # Track prev SID state
    prev = dict()
    for a in range(0xD400, 0xD415):
        prev[a] = m.memory[a]

    results = []
    for fr in range(n_frames):
        # Capture writes by tracking changes
        before = {a: m.memory[a] for a in range(0xD400, 0xD415)}
        run(play_addr)
        writes = []
        for a in range(0xD400, 0xD415):
            if m.memory[a] != before[a]:
                writes.append((a, m.memory[a]))
        results.append(writes)

    return results


def get_writes_hubbard(sid_path, n_frames):
    """Return per-frame lists of (addr, value) for all register CHANGES using HubbardEmu."""
    from hubbard_emu import HubbardEmu, load_sid

    header, binary, load_addr = load_sid(sid_path)
    emu = HubbardEmu(binary, load_addr, 0)

    results = []
    for fr in range(n_frames):
        prev_sid = bytearray(emu.sid)
        emu.play()
        writes = []
        for i in range(21):
            if emu.sid[i] != prev_sid[i]:
                addr = 0xD400 + i
                writes.append((addr, emu.sid[i]))
        results.append(writes)

    return results


def compare_writes(gt_writes, dm_writes, n_frames, verbose_limit=20):
    """Compare two lists of per-frame writes."""
    mismatches = []
    perfect = 0

    for fr in range(n_frames):
        gt = gt_writes[fr]
        dm = dm_writes[fr]
        if gt == dm:
            perfect += 1
        else:
            mismatches.append((fr, gt, dm))

    pct = 100.0 * perfect / n_frames
    print(f"Perfect: {perfect}/{n_frames} ({pct:.2f}%)")
    print(f"Mismatches: {len(mismatches)}")

    reg_names = ['flo', 'fhi', 'plo', 'phi', 'ctl', 'ad ', 'sr ']
    def reg_name(addr):
        off = addr - 0xD400
        v = off // 7
        r = off % 7
        return f"V{v+1}{reg_names[r]}"

    shown = 0
    for fr, gt, dm in mismatches:
        if shown >= verbose_limit:
            break
        shown += 1
        print(f"\nFrame {fr}:")
        print(f"  GT: {[(f'${a:04X}({reg_name(a)})=${v:02X}' ) for a,v in gt]}")
        print(f"  DM: {[(f'${a:04X}({reg_name(a)})=${v:02X}' ) for a,v in dm]}")

        # Classify
        gt_set = set(gt)
        dm_set = set(dm)
        gt_only = gt_set - dm_set
        dm_only = dm_set - gt_set
        same = gt_set & dm_set
        if gt_set == dm_set:
            print(f"  ** SAME VALUES, DIFFERENT ORDER")
        else:
            if gt_only:
                print(f"  GT-only: {[(f'${a:04X}({reg_name(a)})=${v:02X}') for a,v in sorted(gt_only)]}")
            if dm_only:
                print(f"  DM-only: {[(f'${a:04X}({reg_name(a)})=${v:02X}') for a,v in sorted(dm_only)]}")

    return mismatches


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"Comparing {n} frames...")
    print("Getting GT (HubbardEmu) writes...")
    gt = get_writes_hubbard(SID_PATH, n)
    print("Getting DM (Das Model py65) writes...")
    dm = get_writes_py65(DM_SID, n)
    print("Comparing...")
    compare_writes(gt, dm, n)


if __name__ == '__main__':
    main()
