#!/usr/bin/env python3
"""
Detail comparison around frame 2689 to find the first mismatch.
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


def get_writes_py65(sid_path, n_frames):
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
    run(la, 0)
    play_addr = la + 3
    results = []
    for fr in range(n_frames):
        before = {a: m.memory[a] for a in range(0xD400, 0xD415)}
        run(play_addr)
        writes = []
        for a in range(0xD400, 0xD415):
            if m.memory[a] != before[a]:
                writes.append((a, m.memory[a]))
        results.append(writes)
    return results


def get_writes_hubbard(sid_path, n_frames):
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


def main():
    # Find first mismatch
    NF = 3500
    print(f"Getting {NF} frames...")
    gt = get_writes_hubbard(SID_PATH, NF)
    dm = get_writes_py65(DM_SID, NF)

    reg_names = ['flo', 'fhi', 'plo', 'phi', 'ctl', 'ad ', 'sr ']
    def reg_name(addr):
        off = addr - 0xD400
        v = off // 7
        r = off % 7
        return f"V{v+1}{reg_names[r]}"

    first_mismatch = None
    for fr in range(NF):
        if gt[fr] != dm[fr]:
            first_mismatch = fr
            break

    if first_mismatch is None:
        print("No mismatches found!")
        return

    print(f"\nFirst mismatch at frame {first_mismatch}")

    # Show frames around the mismatch
    for fr in range(max(0, first_mismatch - 5), min(NF, first_mismatch + 20)):
        marker = " <-- FIRST MISMATCH" if fr == first_mismatch else ""
        gt_s = [(f'${a:04X}({reg_name(a)})=${v:02X}') for a,v in gt[fr]]
        dm_s = [(f'${a:04X}({reg_name(a)})=${v:02X}') for a,v in dm[fr]]
        match = "OK" if gt[fr] == dm[fr] else "MISMATCH"
        print(f"\nFrame {fr} [{match}]{marker}")
        if gt[fr] != dm[fr]:
            print(f"  GT: {gt_s}")
            print(f"  DM: {dm_s}")
            gt_set = set(gt[fr])
            dm_set = set(dm[fr])
            gt_only = gt_set - dm_set
            dm_only = dm_set - gt_set
            if gt_set == dm_set:
                print(f"  ** SAME VALUES, DIFFERENT ORDER")
            else:
                if gt_only:
                    print(f"  GT-only: {sorted(gt_only)}")
                if dm_only:
                    print(f"  DM-only: {sorted(dm_only)}")
        else:
            print(f"  BOTH: {gt_s}")


if __name__ == '__main__':
    main()
