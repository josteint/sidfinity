"""GoatTracker V1 composer — UsfFile -> our own clean 6502 engine -> xa65 -> PSID.

CLEAN REIMPLEMENTATION of the V1.5 algorithm (RE_NOTES §10), NOT a
transliteration: RAM globals (no SMC), our own data layout (separate
per-field instrument arrays; rts-trick command dispatch), gatetimer/HR/tempo
as plain constants. We reproduce the WRITE STREAM (incl. $D404=$09 testbit on
new-note), not the original's byte tricks. Data tables are regenerated from the
USF musical content — no original bytes are emitted.

The wave-table layout is regenerated in GT's own (wavetbl/notetbl + $FF-marker)
shape so the wave-exec is a direct clean transcription of v153's mt_waveexec —
the lowest-divergence-risk choice for the per-frame (waveform, freq) sequence.

Status: FIRST DRAFT — bring-up against the canary writelog in progress.
"""
from __future__ import annotations

from src.usf.types import UsfFile, Pitch
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header, FLAGS_PAL_6581

LOAD = 0x1000

# The V1.5 freq table is a PLAYER CONSTANT (RE_NOTES §2) — emitted verbatim
# for every tune (engine machinery, not per-tune content).
FREQ_HI = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0a,0x0a,0x0b,0x0c,0x0d,0x0d,0x0e,0x0f,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1a,0x1b,0x1d,0x1f,0x20,
    0x22,0x24,0x27,0x29,0x2b,0x2e,0x31,0x34,0x37,0x3a,0x3e,0x41,
    0x45,0x49,0x4e,0x52,0x57,0x5c,0x62,0x68,0x6e,0x75,0x7c,0x83,
    0x8b,0x93,0x9c,0xa5,0xaf,0xb9,0xc4,0xd0,0xdd,0xea,0xf8,0xff,
]
FREQ_LO = [
    0x17,0x27,0x39,0x4b,0x5f,0x74,0x8a,0xa1,0xba,0xd4,0xf0,0x0e,
    0x2d,0x4e,0x71,0x96,0xbe,0xe8,0x14,0x43,0x74,0xa9,0xe1,0x1c,
    0x5a,0x9c,0xe2,0x2d,0x7c,0xcf,0x28,0x85,0xe8,0x52,0xc1,0x37,
    0xb4,0x39,0xc5,0x5a,0xf7,0x9e,0x4f,0x0a,0xd1,0xa3,0x82,0x6e,
    0x68,0x71,0x8a,0xb3,0xee,0x3c,0x9e,0x15,0xa2,0x46,0x04,0xdc,
    0xd0,0xe2,0x14,0x67,0xdd,0x79,0x3c,0x29,0x44,0x8d,0x08,0xb8,
    0xa1,0xc5,0x28,0xcd,0xba,0xf1,0x78,0x53,0x87,0x1a,0x10,0x71,
    0x42,0x89,0x4f,0x9b,0x74,0xe2,0xf0,0xa6,0x0e,0x33,0x20,0xff,
]

_NOTE_IDX = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def _note_num(p: Pitch) -> int:
    return p.octave * 12 + _NOTE_IDX[p.name]


def _byts(name, data, per=16) -> str:
    """Emit a labelled .byt block."""
    out = [f'{name}:']
    for i in range(0, len(data), per):
        out.append('        .byt ' + ', '.join(f'${b & 0xFF:02x}'
                                                for b in data[i:i + per]))
    if not data:
        out.append('        .byt $00')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Data model: flatten the USF into engine tables
# ---------------------------------------------------------------------------

class _Tables:
    """Build the engine's data tables from the USF (canary: 1 subtune)."""

    def __init__(self, usf: UsfFile):
        self.usf = usf
        p = usf.params.fields
        self.gatetimer = int(p.get('gatetimer', 2))
        self.hr_ad = int(p.get('hr_ad', 0))
        self.hr_sr = int(p.get('hr_sr', 0))
        self.deftempo = int(p.get('default_tempo', 5))

        # Instruments — separate per-field arrays, indexed by 1-based id.
        insts = {i.id: i for i in usf.instruments}
        self.ninst = (max(insts) + 1) if insts else 1
        self.instad = [0] * self.ninst
        self.instsr = [0] * self.ninst
        self.instpulse = [0] * self.ninst
        self.instpulsespd = [0] * self.ninst
        self.instpulselo = [0] * self.ninst
        self.instpulsehi = [0] * self.ninst
        self.instfilter = [0] * self.ninst
        self.instwave = [0] * self.ninst         # start index into wave arrays

        # Wave arrays (GT shape: wctrl/wnote + $FF marker + relative loop tgt).
        # Index 0 reserved = "no program".
        self.wctrl = [0]
        self.wnote = [0]
        for iid in range(1, self.ninst):
            inst = insts.get(iid)
            if inst is None:
                continue
            ad, sr = inst.adsr
            self.instad[iid] = ad
            self.instsr[iid] = sr
            self.instpulse[iid] = inst.pwm.init
            spd = inst.pwm.speed & 0xFE          # bit0 = hard-restart flag (0 = HR on, the default)
            self.instpulsespd[iid] = spd
            self.instpulselo[iid] = inst.pwm.min_hi
            self.instpulsehi[iid] = inst.pwm.max_hi
            self.instfilter[iid] = inst.filter_prog.program
            steps = list(zip(inst.waveform, inst.wave_freq))
            if steps:
                start = len(self.wctrl)
                self.instwave[iid] = start
                for left, right in steps:
                    self.wctrl.append(left & 0xFF)
                    self.wnote.append(right & 0xFF)
                # loop marker: tgt = loop_step + 2 (newptr = tgt + start - 2)
                lp = inst.loop if inst.loop is not None else (len(steps) - 1)
                self.wctrl.append(0xFF)
                self.wnote.append((lp + 2) & 0xFF)

        # Orderlists + patterns (canary: subtune 0). Per voice: concatenate the
        # per-voice patterns into one byte stream + a pointer table; the
        # orderlist holds offsets. We keep it simple: song table -> per-channel
        # orderlist bytes; pattern table -> per (voice,patternid) byte streams.
        sub = usf.subtunes[0]
        self.voices = []     # list of dict(orderbytes, patterns=[bytes], loop_off)
        for v in sub.voices:
            self.voices.append(self._voice_tables(v))

    def _voice_tables(self, v):
        # Encode each pattern to a GT-style byte stream.
        pat_bytes = []
        for pat in sorted(v.patterns, key=lambda p: p.id):
            pat_bytes.append((pat.id, _encode_pattern(pat.rows)))
        # Orderlist bytes: transpose/repeat prefixes + pattern ids + loop.
        ol = v.orderlist
        order = bytearray()
        entry_off = []      # entry index -> byte offset
        cur_trans = 0
        for i, pn in enumerate(ol.entries):
            t = ol.transpose_at(i)
            if t != cur_trans:
                order.append((t + 0xF0) & 0xFF)     # TRANS ($E0=-16..$FE=+14)
                cur_trans = t
            rep = ol.repeat_at(i)
            if rep > 1:
                order.append((0xD0 + (rep - 1)) & 0xFF)
            entry_off.append(len(order))
            order.append(pn)
        loop_off = entry_off[ol.loop_to] if ol.loop_to is not None and entry_off \
            else 0
        order.append(0xFF)          # LOOPSONG
        order.append(loop_off)
        return {'order': bytes(order), 'patterns': pat_bytes}


def _encode_pattern(rows) -> bytes:
    """USF rows -> GT pattern byte stream (RE_NOTES §4)."""
    out = bytearray()
    for r in rows:
        # decode fx_flags -> (cmd, param)
        cmd, param = _fx_to_cmd(r.fx_flags)
        if r.pitch.is_rest and not r.fx_flags and r.duration > 1:
            # packed rest of N rows
            out.append((256 - r.duration) & 0xFF)
            continue
        if r.pitch.is_rest:
            note = 0x5E if 'keyoff' in r.fx_flags else 0x5F
        else:
            note = _note_num(r.pitch)
        if cmd is not None:
            inst = r.instr.id if r.instr else 0
            out.append(note)                 # note WITH command (<$60)
            out.append(((inst & 0x1F) << 3) | (cmd & 7))
            out.append(param & 0xFF)
        else:
            # note WITHOUT command — but instrument changes need the cmd form.
            inst = r.instr.id if r.instr else 0
            if inst:
                out.append(note)
                out.append(((inst & 0x1F) << 3) | 0)   # cmd 0 (arp) param 0 = noop
                out.append(0)
            else:
                out.append((note + 0x60) & 0xFF)       # note-only ($60-$BF)
    out.append(0xFF)             # ENDPATT
    return bytes(out)


def _fx_to_cmd(flags):
    """fx_flags tuple -> (cmd, param) or (None, None). Inverse of to_usf._row_fx."""
    for f in flags:
        if f == 'keyoff':
            continue
        if f.startswith('arp='):
            x, y, s = (int(t) for t in f[4:].split(','))
            return 0, (s << 7) | ((x & 7) << 4) | (y & 0xF)
        if f.startswith('glide_up='):
            return 1, int(f.split('=')[1])
        if f.startswith('glide_down='):
            return 2, int(f.split('=')[1])
        if f.startswith('porta='):
            return 3, int(f.split('=')[1])
        if f.startswith('vibrato='):
            a, w = (int(t) for t in f[8:].split(','))
            return 4, ((a & 0xF) << 4) | (w & 0xF)
        if f.startswith('filter='):
            return 5, int(f.split('=')[1])
        if f.startswith('srr='):
            return 6, int(f.split('=')[1])
        if f.startswith('tempo='):
            return 7, int(f.split('=')[1])
    return None, None


# ---------------------------------------------------------------------------
# Engine assembly (clean transcription of v1_player1_v153.s)
# ---------------------------------------------------------------------------

def compose_v1_asm(usf: UsfFile) -> str:
    t = _Tables(usf)

    # Build per-voice data sections + the song/pattern pointer tables.
    order_blocks = []
    patt_ptr_lo, patt_ptr_hi, patt_blocks = [], [], []
    song_lo, song_hi = [], []
    pat_label_id = 0
    for ch, vt in enumerate(t.voices):
        song_lo.append(f'<order_{ch}')
        song_hi.append(f'>order_{ch}')
        order_blocks.append(_byts(f'order_{ch}', vt['order']))
        # patterns for this voice, keyed by USF pattern id -> global label
        for pid, pb in vt['patterns']:
            lbl = f'patt_{ch}_{pid}'
            patt_blocks.append(_byts(lbl, pb))
    # Pattern pointer table indexed by (voice, pattern id). The engine reads
    # chnpattnum directly; we build a flat per-voice scheme: chnpattnum stores
    # a global pattern slot. Simpler: build one pattern pointer table over all
    # (voice,pid) slots, and the orderlist entries already store the USF pid;
    # but pids repeat across voices. Use a per-voice base offset.
    # --- flatten: assign every (voice,pid) a global slot ---
    slot_lo, slot_hi = [], []
    voice_base = []
    slot = 0
    for ch, vt in enumerate(t.voices):
        voice_base.append(slot)
        # map pid -> slot in order of pid
        pids = sorted(pid for pid, _ in vt['patterns'])
        for pid in pids:
            slot_lo.append(f'<patt_{ch}_{pid}')
            slot_hi.append(f'>patt_{ch}_{pid}')
            slot += 1

    asm = []
    A = asm.append
    A(f'        * = ${LOAD:04x}')
    A('        jmp init')
    A('        jmp play')
    A('')
    A(f'GATETIMER = ${t.gatetimer:02x}')
    A(f'HR_AD = ${t.hr_ad:02x}')
    A(f'HR_SR = ${t.hr_sr:02x}')
    A(f'DEFTEMPO = ${t.deftempo:02x}')
    A('temp1 = $fc')
    A('temp2 = $fd')
    A('')
    A(_ENGINE)
    A('')
    # ---- data ----
    A(_byts('freqlo', FREQ_LO))
    A(_byts('freqhi', FREQ_HI))
    A(_byts('instad', t.instad))
    A(_byts('instsr', t.instsr))
    A(_byts('instpulse', t.instpulse))
    A(_byts('instpulsespd', t.instpulsespd))
    A(_byts('instpulselo', t.instpulselo))
    A(_byts('instpulsehi', t.instpulsehi))
    A(_byts('instfilter', t.instfilter))
    A(_byts('instwave', t.instwave))
    A(_byts('wctrl', t.wctrl))
    A(_byts('wnote', t.wnote))
    # song table (per-channel orderlist pointers)
    A('songlo:\n        .byt ' + ', '.join(song_lo))
    A('songhi:\n        .byt ' + ', '.join(song_hi))
    # pattern pointer table (flat slots)
    A('pattlo:\n        .byt ' + (', '.join(slot_lo) if slot_lo else '$00'))
    A('patthi:\n        .byt ' + (', '.join(slot_hi) if slot_hi else '$00'))
    # per-voice pattern base offsets (slot = voice_base[ch] + pid)
    A('voicebase:\n        .byt ' + ', '.join(str(b) for b in voice_base))
    A('')
    for b in order_blocks:
        A(b)
    for b in patt_blocks:
        A(b)
    return '\n'.join(asm)


# The engine — placeholder for the clean transcription (next iteration writes
# the full mt_play flow). Kept minimal so the data layout + build harness
# assemble and we can diff incrementally.
_ENGINE = """
init:
        rts
play:
        rts
"""


def build_v1_sid(usf: UsfFile) -> bytes:
    asm = compose_v1_asm(usf)
    code = assemble(asm)
    header = build_header(
        load=0, init=LOAD, play=LOAD + 3,
        songs=len(usf.subtunes), start_song=usf.psid.start_song,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, flags=FLAGS_PAL_6581)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code


if __name__ == '__main__':
    import sys
    from pipelines.goattracker.v1.extract.engine_model import parse_sid, extract
    from pipelines.goattracker.v1.extract.to_usf import model_to_usf
    path = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/T/Topaz/Joker.sid'
    usf = model_to_usf(extract(parse_sid(path)))
    asm = compose_v1_asm(usf)
    print(f'asm {len(asm.splitlines())} lines')
    sid = build_v1_sid(usf)
    print(f'built SID: {len(sid)} bytes (header 124 + load 2 + code {len(sid)-126})')
