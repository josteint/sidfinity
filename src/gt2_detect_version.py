"""
gt2_detect_version.py — Detect which GT2 player behavior group a SID uses.

Groups (from docs/gt2_player_versions.md):
  A (2.65-2.67): AD-before-SR, new-note writes all regs
  B (2.68-2.72): SR-before-AD, new-note writes wave-only
  C (2.73-2.74): B + ghost reg support, partial ADSR revert
  D (2.76-2.77): C + vibrato param fix
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table


def detect_gt2_player_group(sid_path):
    """Detect GT2 player behavior group from a SID file.

    Returns dict with:
        group: 'A', 'B', 'C', 'D', or None if not GT2/unknown
        adsr_order: 'ad_first' or 'sr_first'
        newnote_regs: 'all_regs' or 'wave_only'
        ghost_regs: True/False
        vibrato_fix: True/False
        ad_param: int (0x00-0xFF, default 0x0F if not detected)
        sr_param: int (0x00-0xFF, default 0x00 if not detected)
        details: dict of detection evidence
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    code_end = ft[0]

    # --- Detect ADSR write order in hard restart ---
    # HR code uses LDA #ADPARAM / STA $D405,X and LDA #SRPARAM / STA $D406,X.
    # The key is LDA immediate (#) before STA — distinguishes HR from loadregs.
    adsr_order = None
    hr_ad_offset = None
    hr_sr_offset = None
    ad_param = None  # ADPARAM: the AD value written during hard restart
    sr_param = None  # SRPARAM: the SR value written during hard restart

    hr_writes = []
    for i in range(code_end - 5):
        if binary[i] == 0xA9 and binary[i + 2] == 0x9D:  # LDA #xx / STA abs,X
            addr = binary[i + 3] | (binary[i + 4] << 8)
            if addr == 0xD405:
                hr_writes.append(('AD', i))
                if hr_ad_offset is None:
                    hr_ad_offset = i
                    ad_param = binary[i + 1]
            elif addr == 0xD406:
                hr_writes.append(('SR', i))
                if hr_sr_offset is None:
                    hr_sr_offset = i
                    sr_param = binary[i + 1]

    if hr_writes:
        adsr_order = 'ad_first' if hr_writes[0][0] == 'AD' else 'sr_first'

    # --- Detect new-note register writes ---
    # After new-note init, the code does JMP to either:
    #   mt_loadregs (Group A): writes freq + pulse + wave + ADSR
    #   mt_loadregswaveonly (Group B+): writes wave only
    #
    # Detect by finding the JMP instruction after the wave_ptr store.
    # The wave_ptr store is: STA mt_chnwaveptr,X (0x9D addr addr)
    # followed by JMP target.
    #
    # mt_loadregswaveonly has pattern: LDA mt_chnwave,X / AND mt_chngate,X / STA $D404,X / RTS
    # mt_loadregs starts with: LDA mt_chnad,X (or LDA mt_chnsr,X for B+)
    newnote_regs = None

    # Find all JMP instructions and their targets
    jmp_targets = {}
    for i in range(code_end - 3):
        if binary[i] == 0x4C:  # JMP abs
            target = binary[i + 1] | (binary[i + 2] << 8)
            target_off = target - la
            if 0 <= target_off < code_end:
                jmp_targets[i] = target_off

    # Find the mt_loadregswaveonly entry point:
    # LDA abs,X ($BD) / AND abs,X ($3D) / STA $D404,X ($9D $04 $D4) / RTS ($60)
    loadregswaveonly_off = None
    for i in range(code_end - 10):
        if (binary[i] == 0xBD and          # LDA abs,X (mt_chnwave)
                binary[i + 3] == 0x3D and   # AND abs,X (mt_chngate)
                binary[i + 6] == 0x9D and   # STA abs,X
                binary[i + 7] == 0x04 and binary[i + 8] == 0xD4 and  # $D404
                binary[i + 9] == 0x60):     # RTS
            loadregswaveonly_off = i
            break

    # Find the mt_loadregs entry point (has freq writes before the wave-only part):
    # ... STA $D400,X / ... STA $D401,X / [mt_loadregswaveonly]
    loadregs_off = None
    if loadregswaveonly_off is not None:
        # Look backwards from loadregswaveonly for STA $D401,X / STA $D400,X
        for i in range(loadregswaveonly_off - 1, max(0, loadregswaveonly_off - 20), -1):
            if (binary[i] == 0x9D and binary[i + 1] == 0x00 and binary[i + 2] == 0xD4):
                # Found STA $D400,X — look back further for the entry
                # The entry is the LDA before the first STA in this block
                for j in range(i - 1, max(0, i - 20), -1):
                    if binary[j] == 0xBD:  # LDA abs,X (could be mt_chnad or mt_chnfreqlo)
                        loadregs_off = j
                        break
                break

    # Now check: which JMP target does the new-note code use?
    # Find JMPs that target loadregswaveonly vs loadregs
    if loadregswaveonly_off is not None:
        jmp_to_waveonly = [off for off, target in jmp_targets.items()
                          if target == loadregswaveonly_off]
        jmp_to_loadregs = [off for off, target in jmp_targets.items()
                          if loadregs_off and target == loadregs_off]

        # The new-note init JMP is typically the first JMP to either target
        # that's in the new-note code area (after note frequency setup)
        if jmp_to_waveonly and not jmp_to_loadregs:
            newnote_regs = 'wave_only'
        elif jmp_to_loadregs and not jmp_to_waveonly:
            newnote_regs = 'all_regs'
        elif jmp_to_waveonly and jmp_to_loadregs:
            # Both exist — the new-note one is typically earlier in the code
            # (the later one is from the wave table execution path)
            newnote_regs = 'wave_only'  # B+ has both paths
        else:
            newnote_regs = 'all_regs'  # fallback

    # --- Detect ghost register mode ---
    # Look for: LDX #$18 (24) / LDA ghostregs,X / STA SIDBASE,X / DEX / BPL
    ghost_regs = False
    for i in range(code_end - 8):
        if (binary[i] == 0xA2 and binary[i + 1] == 0x18 and  # LDX #24
                binary[i + 2] == 0xBD and                      # LDA abs,X
                binary[i + 5] == 0x9D and                      # STA abs,X
                binary[i + 6] == 0x00 and binary[i + 7] == 0xD4 and  # $D400
                binary[i + 8] == 0xCA and                      # DEX
                binary[i + 9] == 0x10):                        # BPL
            ghost_regs = True
            break

    # --- Detect vibrato param fix ---
    # In the effect 0 handler (instrument vibrato), look for:
    # LDA #$00 / JMP mt_tick0_34
    # The unfixed version just has JMP mt_tick0_34 without the LDA #$00
    #
    # The effect 0 code is: NOINSTRVIB check → (optional LDA #$00) → JMP
    # Find by looking for the pattern: A9 00 4C xx xx (LDA #0, JMP)
    # near effect handling code
    vibrato_fix = False
    # The tick0_0 handler stores/loads vibrato param. Look for LDA #$00
    # followed by JMP where the JMP target is shared with the vibrato path.
    for i in range(code_end - 5):
        if (binary[i] == 0xA9 and binary[i + 1] == 0x00 and  # LDA #$00
                binary[i + 2] == 0x4C):                        # JMP
            # Check if this is in the right area (effect processing)
            # The JMP target should be mt_tick0_34 which stores to mt_chnparam
            target_off = (binary[i + 3] | (binary[i + 4] << 8)) - la
            if 0 < target_off < code_end:
                # Check if target has STA abs,X (storing param)
                if target_off + 2 < code_end and binary[target_off] == 0x9D:
                    vibrato_fix = True
                    break
                # Also check: target might be LDA/STA pair
                if (target_off + 5 < code_end and
                        binary[target_off] in (0x8D, 0x9D)):
                    vibrato_fix = True
                    break

    # --- Determine group ---
    # ADSR order in the HR code is the primary discriminator:
    #   ad_first → Group A (v2.65-2.67)
    #   sr_first → Group B/C/D (v2.68+)
    # Secondary: vibrato fix (D), ghost regs (C)
    if adsr_order == 'ad_first':
        group = 'A'
    elif vibrato_fix:
        group = 'D'
    elif ghost_regs:
        group = 'C'
    elif adsr_order == 'sr_first':
        group = 'B'
    else:
        group = None

    return {
        'group': group,
        'adsr_order': adsr_order,
        'newnote_regs': newnote_regs,
        'ghost_regs': ghost_regs,
        'vibrato_fix': vibrato_fix,
        'ad_param': ad_param if ad_param is not None else 0x0F,
        'sr_param': sr_param if sr_param is not None else 0x00,
        'details': {
            'hr_ad_offset': hr_ad_offset,
            'hr_sr_offset': hr_sr_offset,
            'loadregswaveonly_off': loadregswaveonly_off,
            'loadregs_off': loadregs_off,
            'code_end': code_end,
        }
    }


if __name__ == '__main__':
    import glob

    if len(sys.argv) < 2:
        print("Usage: gt2_detect_version.py <file.sid | glob_pattern>")
        sys.exit(1)

    path = sys.argv[1]
    if '*' in path or '?' in path:
        files = sorted(glob.glob(path, recursive=True))
    else:
        files = [path]

    from gt2_parse_direct import parse_gt2_direct

    counts = {}
    for f in files:
        r = parse_gt2_direct(f)
        if r is None:
            continue
        result = detect_gt2_player_group(f)
        if result is None:
            continue
        g = result['group'] or '?'
        counts[g] = counts.get(g, 0) + 1

        if len(files) <= 10:
            name = os.path.basename(f)
            print(f'{name}: group={result["group"]} '
                  f'adsr={result["adsr_order"]} '
                  f'newnote={result["newnote_regs"]} '
                  f'ghost={result["ghost_regs"]} '
                  f'vibfix={result["vibrato_fix"]} '
                  f'ad_param=${result["ad_param"]:02X} '
                  f'sr_param=${result["sr_param"]:02X}')

    if len(files) > 10:
        print(f'\n{sum(counts.values())} GT2 files:')
        for g in sorted(counts.keys()):
            print(f'  Group {g}: {counts[g]}')
