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
        fixedparams: 1 (constant waveform/gate), 0 (per-instrument), or None
        simplepulse: 1 (same val to lo+hi), 0 (separate lo/hi), or None (no pulse)
        details: dict of detection evidence
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    code_end = ft[0]

    # Detect ghost buffer for Group C players
    from gt2_parse_direct import detect_ghost_buffer
    ghost_base = detect_ghost_buffer(binary, code_end)

    # --- Detect ADSR write order in hard restart ---
    # HR code uses LDA #ADPARAM / STA $D405,X and LDA #SRPARAM / STA $D406,X.
    # For Group C, these write to ghost_buf+5 / ghost_buf+6 instead.
    # The key is LDA immediate (#) before STA — distinguishes HR from loadregs.
    adsr_order = None
    hr_ad_offset = None
    hr_sr_offset = None
    ad_param = None
    sr_param = None

    def _is_ad_reg(addr):
        """Check if addr is AD register ($D405 or ghost+5, per voice)."""
        if 0xD400 <= addr <= 0xD418 and (addr - 0xD400) % 7 == 5:
            return True
        if ghost_base is not None and ghost_base <= addr <= ghost_base + 0x18:
            return (addr - ghost_base) % 7 == 5
        return False

    def _is_sr_reg(addr):
        """Check if addr is SR register ($D406 or ghost+6, per voice)."""
        if 0xD400 <= addr <= 0xD418 and (addr - 0xD400) % 7 == 6:
            return True
        if ghost_base is not None and ghost_base <= addr <= ghost_base + 0x18:
            return (addr - ghost_base) % 7 == 6
        return False

    # Detect shadow register addresses for BUFFEREDWRITES players.
    # In mt_loadregs with BUFFEREDWRITES: LDA mt_chnad,X / STA $D405,X / LDA mt_chnsr,X / STA $D406,X
    # (or SR-first variant). Extract shadow addresses so we can detect HR writes to them.
    shadow_ad_addr = None
    shadow_sr_addr = None
    loadregs_adsr_order = None
    for i in range(code_end - 12):
        if binary[i] == 0xBD and binary[i + 3] == 0x9D:  # LDA abs,X / STA abs,X
            sta_dst = binary[i + 4] | (binary[i + 5] << 8)
            if sta_dst == 0xD405:  # STA $D405,X (AD register)
                shadow_ad_addr = binary[i + 1] | (binary[i + 2] << 8)
                # Next pair should be LDA abs,X / STA $D406,X
                if (i + 9 < code_end and binary[i + 6] == 0xBD and
                        binary[i + 9] == 0x9D):
                    sta2 = binary[i + 10] | (binary[i + 11] << 8)
                    if sta2 == 0xD406:
                        shadow_sr_addr = binary[i + 7] | (binary[i + 8] << 8)
                        loadregs_adsr_order = 'ad_first'
                        break
            elif sta_dst == 0xD406:  # STA $D406,X (SR register) — sr_first loadregs
                shadow_sr_addr = binary[i + 1] | (binary[i + 2] << 8)
                if (i + 9 < code_end and binary[i + 6] == 0xBD and
                        binary[i + 9] == 0x9D):
                    sta2 = binary[i + 10] | (binary[i + 11] << 8)
                    if sta2 == 0xD405:
                        shadow_ad_addr = binary[i + 7] | (binary[i + 8] << 8)
                        loadregs_adsr_order = 'sr_first'
                        break

    hr_writes = []
    for i in range(code_end - 5):
        if binary[i] == 0xA9 and binary[i + 2] == 0x9D:  # LDA #xx / STA abs,X
            addr = binary[i + 3] | (binary[i + 4] << 8)
            is_ad_direct = _is_ad_reg(addr)
            is_sr_direct = _is_sr_reg(addr)
            is_ad_shadow = (addr == shadow_ad_addr) if shadow_ad_addr else False
            is_sr_shadow = (addr == shadow_sr_addr) if shadow_sr_addr else False

            if is_ad_direct or is_sr_direct:
                # Direct SID register write — always trust
                reg = 'AD' if is_ad_direct else 'SR'
                hr_writes.append((reg, i))
                if reg == 'AD' and hr_ad_offset is None:
                    hr_ad_offset = i
                    ad_param = binary[i + 1]
                elif reg == 'SR' and hr_sr_offset is None:
                    hr_sr_offset = i
                    sr_param = binary[i + 1]
            elif is_ad_shadow or is_sr_shadow:
                # Shadow register write — only trust if the OTHER shadow write
                # is adjacent (5 bytes away), forming the HR ADSR pair.
                j = i + 5  # next instruction position
                if j + 4 < code_end and binary[j] == 0xA9 and binary[j + 2] == 0x9D:
                    next_addr = binary[j + 3] | (binary[j + 4] << 8)
                    pair_ok = False
                    if is_ad_shadow and next_addr == shadow_sr_addr:
                        pair_ok = True
                    elif is_sr_shadow and next_addr == shadow_ad_addr:
                        pair_ok = True
                    if pair_ok:
                        reg1 = 'AD' if is_ad_shadow else 'SR'
                        reg2 = 'SR' if is_ad_shadow else 'AD'
                        hr_writes.append((reg1, i))
                        hr_writes.append((reg2, j))
                        if reg1 == 'AD' and hr_ad_offset is None:
                            hr_ad_offset = i
                            ad_param = binary[i + 1]
                        elif reg1 == 'SR' and hr_sr_offset is None:
                            hr_sr_offset = i
                            sr_param = binary[i + 1]
                        if reg2 == 'AD' and hr_ad_offset is None:
                            hr_ad_offset = j
                            ad_param = binary[j + 1]
                        elif reg2 == 'SR' and hr_sr_offset is None:
                            hr_sr_offset = j
                            sr_param = binary[j + 1]

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
    # LDA abs,X ($BD) / AND abs,X ($3D) / STA waveform_reg,X ($9D) / RTS ($60)
    # For Group C, waveform_reg is ghost_buf+4 instead of $D404
    loadregswaveonly_off = None
    for i in range(code_end - 10):
        if (binary[i] == 0xBD and          # LDA abs,X (mt_chnwave)
                binary[i + 3] == 0x3D and   # AND abs,X (mt_chngate)
                binary[i + 6] == 0x9D and   # STA abs,X
                binary[i + 9] == 0x60):     # RTS
            sta_dst = binary[i + 7] | (binary[i + 8] << 8)
            # Check if it's STA $D404,X or STA ghost+4,X
            is_wave_reg = (sta_dst == 0xD404)
            if ghost_base is not None and ghost_base <= sta_dst <= ghost_base + 0x18:
                is_wave_reg = is_wave_reg or ((sta_dst - ghost_base) % 7 == 4)
            if is_wave_reg:
                loadregswaveonly_off = i
                break

    # Find the mt_loadregs entry point (has freq writes before the wave-only part):
    # ... STA freq_lo_reg,X / ... STA freq_hi_reg,X / [mt_loadregswaveonly]
    # For Group C, freq regs are ghost_buf+0 / ghost_buf+1 instead of $D400/$D401
    loadregs_off = None
    if loadregswaveonly_off is not None:
        # Look backwards from loadregswaveonly for STA freq_lo,X
        for i in range(loadregswaveonly_off - 1, max(0, loadregswaveonly_off - 20), -1):
            if binary[i] == 0x9D:
                sta_dst = binary[i + 1] | (binary[i + 2] << 8)
                is_freq_lo = (sta_dst == 0xD400)
                if ghost_base is not None and sta_dst == ghost_base:
                    is_freq_lo = True
                if is_freq_lo:
                    # Found STA freq_lo,X -- look back further for the entry
                    for j in range(i - 1, max(0, i - 20), -1):
                        if binary[j] == 0xBD:  # LDA abs,X
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

    # --- Detect FIXEDPARAMS ---
    # FIXEDPARAMS=1: initial waveform is a constant: LDA #xx / STA mt_chnwave,X
    # FIXEDPARAMS=0: per-instrument lookup: LDA mt_insfirstwave-1,Y / STA mt_chnwave,X
    #
    # We find mt_chnwave's address from the loadregswaveonly pattern, then search
    # for STA to that address and check the preceding LDA instruction.
    fixedparams = None

    if loadregswaveonly_off is not None:
        # mt_chnwave address is the operand of the LDA at loadregswaveonly
        chnwave_addr = binary[loadregswaveonly_off + 1] | (binary[loadregswaveonly_off + 2] << 8)

        # Find STA mt_chnwave,X in the new-note init area.
        # The new-note code does: LDA ... / [optional BEQ/BCS] / STA mt_chnwave,X
        # We look for all STA mt_chnwave,X and check the preceding LDA.
        for i in range(code_end - 3):
            if (binary[i] == 0x9D and
                    (binary[i + 1] | (binary[i + 2] << 8)) == chnwave_addr):
                # Found STA mt_chnwave,X -- look backwards for the loading instruction
                for j in range(i - 1, max(0, i - 20), -1):
                    if binary[j] == 0xA9:  # LDA #xx (immediate) -> FIXEDPARAMS=1
                        fixedparams = 1
                        break
                    if binary[j] == 0xB9:  # LDA abs,Y (mt_insfirstwave-1,Y) -> FIXEDPARAMS=0
                        fixedparams = 0
                        break
                    if binary[j] == 0xBD:  # LDA abs,X -> not the new-note path
                        break
                if fixedparams is not None:
                    break

    # Fallback: detect via gate timer pattern
    # CMP abs,X / BEQ (DD xx xx F0) -> FIXEDPARAMS=0
    # CMP #xx / BEQ (C9 xx F0) -> FIXEDPARAMS=1
    if fixedparams is None:
        for i in range(code_end - 4):
            if (binary[i] == 0xDD and i + 4 < code_end and binary[i + 3] == 0xF0):
                addr = binary[i + 1] | (binary[i + 2] << 8)
                if addr < 0xD000:
                    fixedparams = 0
                    break
            if (binary[i] == 0xC9 and i + 3 < code_end and binary[i + 2] == 0xF0):
                if 1 <= binary[i + 1] <= 0x20:
                    fixedparams = 1
                    break

    # --- Detect SIMPLEPULSE ---
    # SIMPLEPULSE=1: STA pulse_lo,X / STA pulse_hi,X (same value written to both)
    # SIMPLEPULSE=0: STA pulse_lo,X / LDA abs,X / STA pulse_hi,X (different lo/hi)
    # None if NOPULSE=1 (no STA pulse_hi,X in code at all)
    # For Group C, pulse regs are ghost_buf+2/+3 instead of $D402/$D403
    simplepulse = None
    pulse_hi_addr = 0xD403
    pulse_lo_addr = 0xD402
    if ghost_base is not None:
        pulse_hi_addr = ghost_base + 3
        pulse_lo_addr = ghost_base + 2

    # Search for STA pulse_hi,X and check what precedes it
    for i in range(code_end - 3):
        if binary[i] == 0x9D:
            sta_dst = binary[i + 1] | (binary[i + 2] << 8)
            if sta_dst == pulse_hi_addr or (sta_dst == 0xD403 and ghost_base is None):
                # Found STA pulse_hi,X -- check what's immediately before
                if (i >= 3 and binary[i - 3] == 0x9D and
                        (binary[i - 2] | (binary[i - 1] << 8)) == pulse_lo_addr):
                    simplepulse = 1
                    break
                if (i >= 6 and binary[i - 3] == 0xBD and
                        binary[i - 6] == 0x9D and
                        (binary[i - 5] | (binary[i - 4] << 8)) == pulse_lo_addr):
                    simplepulse = 0
                    break

    # --- Detect pulse speed ASL doubling ---
    # Some players use ASL;BCC to double pulse speed before adding.
    # Others use CLC;BPL (no doubling).
    # Pattern: LDA abs,Y ($B9); ASL ($0A); BCC ($90)
    pulse_speed_asl = False
    for i in range(code_end - 5):
        if (binary[i] == 0xB9 and              # LDA abs,Y
                binary[i + 3] == 0x0A and       # ASL A
                binary[i + 4] == 0x90):         # BCC
            pulse_speed_asl = True
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
    # IMPORTANT: ad_first detected from shadow registers (BUFFEREDWRITES) does NOT
    # indicate Group A. Group A uses unbuffered writes exclusively.
    if adsr_order == 'ad_first' and shadow_ad_addr is None:
        group = 'A'
    elif vibrato_fix:
        group = 'D'
    elif ghost_regs:
        group = 'C'
    elif adsr_order == 'sr_first':
        group = 'B'
    else:
        group = 'B'  # default to most common group when HR pattern not found

    return {
        'group': group,
        'adsr_order': adsr_order,
        'loadregs_adsr_order': loadregs_adsr_order,
        'newnote_regs': newnote_regs,
        'ghost_regs': ghost_regs,
        'vibrato_fix': vibrato_fix,
        'fixedparams': fixedparams,
        'simplepulse': simplepulse,
        'pulse_speed_asl': pulse_speed_asl,
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
                  f'fixedparams={result["fixedparams"]} '
                  f'simplepulse={result["simplepulse"]}')

    if len(files) > 10:
        print(f'\n{sum(counts.values())} GT2 files:')
        for g in sorted(counts.keys()):
            print(f'  Group {g}: {counts[g]}')
