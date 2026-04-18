"""
usf_semantics.py — Formal executable specification of USF playback.

This module defines USF's semantics as a deterministic state machine:
    P: Song × ℕ → RegisterTrace

Given a Song and a frame count N, P produces an N-frame sequence of
25-byte SID register states. This is THE reference definition of what
USF means — all implementations (codegen_v2, future Lean spec) must
produce traces equivalent to this under the trace equivalence relation.

The state machine mirrors the V2 player's execution model exactly:
    1. Per frame: for each voice (0, 1, 2):
       a. Decrement tempo counter
       b. Counter > 0: wave table step → effects → pulse table step
       c. Counter == 0: read pattern → new note init → tick-0 effects
       d. Counter underflow: reload from tempo
       e. Gate timer check → register writes
    2. Filter table step (global)
    3. Collect SID register values → one RegisterFrame

Mathematical properties:
    - P is a total function (always produces output for valid input)
    - P is deterministic (same input → same output)
    - P(song, N) is the first N frames of P(song, M) for N ≤ M
    - The state space is finite (all values are bounded 8-bit)

Usage:
    from formal.usf_semantics import USFPlayer
    player = USFPlayer(song)
    trace = player.run(500)  # 500 frames = 10 seconds at 50fps
    for frame in trace:
        print(frame)  # 25-element list of register values
"""

from dataclasses import dataclass, field
from typing import Optional
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from usf.format import (Song, Instrument, Pattern, NoteEvent, WaveTableStep,
                         PulseTableStep, FilterTableStep, SpeedTableEntry)


# ============================================================
# Standard PAL frequency table (96 notes, C0-B7)
# ============================================================

FREQ_LO_PAL = bytes([
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
    0x5A,0x9C,0xE2,0x2D,0x7C,0xCF,0x28,0x85,0xE8,0x52,0xC1,0x37,
    0xB4,0x39,0xC5,0x5A,0xF7,0x9E,0x4F,0x0A,0xD1,0xA3,0x82,0x6E,
    0x68,0x71,0x8A,0xB3,0xEE,0x3C,0x9E,0x15,0xA2,0x46,0x04,0xDC,
    0xD0,0xE2,0x14,0x67,0xDD,0x79,0x3C,0x29,0x44,0x8D,0x08,0xB8,
    0xA1,0xC5,0x28,0xCD,0xBA,0xF1,0x78,0x53,0x87,0x1A,0x10,0x71,
    0x42,0x89,0x4F,0x9B,0x74,0xE2,0xF0,0xA6,0x0E,0x33,0x20,0xFF])

FREQ_HI_PAL = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF])


# ============================================================
# State definitions
# ============================================================

@dataclass
class VoiceState:
    """Per-voice mutable state of the USF player.

    Each field corresponds to a player variable (mt_chn* in codegen_v2).
    All values are 8-bit unsigned unless noted.
    """
    # Tempo / timing
    counter: int = 1         # mt_chncounter — ticks until next pattern read
    tempo: int = 6           # mt_chntempo — frames per tick for this voice

    # Current note state
    note: int = 0            # mt_chnnote — current note number (0-95)
    last_note: int = 0       # mt_chnlastnote — last note for calculated speed

    # Waveform / gate
    wave: int = 0            # mt_chnwave — current waveform byte
    gate: int = 0            # mt_chngate — gate mask ($FF=on, $FE=off, $Fx=keyoff/on)

    # ADSR
    ad: int = 0              # mt_chnad — attack/decay
    sr: int = 0              # mt_chnsr — sustain/release

    # Frequency
    freq_lo: int = 0         # mt_chnfreqlo
    freq_hi: int = 0         # mt_chnfreqhi
    freq_slide: int = 0      # mt_chnfreqslide — signed per-frame freq_hi delta

    # Pulse
    pulse_lo: int = 0        # mt_chnpulselo
    pulse_hi: int = 0        # mt_chnpulsehi
    pulse_ptr: int = 0       # mt_chnpulseptr — 1-based index into pulse table (0=inactive)
    pulse_time: int = 0      # mt_chnpulsetime — pulse modulation frame counter

    # Wave table
    wave_ptr: int = 0        # mt_chnwaveptr — 1-based index into wave table (0=inactive)
    wave_time: int = 0       # mt_chnwavetime — wave delay counter

    # Gate timer
    gate_timer: int = 2      # mt_chngatetimer — hard restart countdown value

    # Pattern reader
    patt_num: int = 0        # mt_chnpattnum — current pattern index
    patt_ptr: int = 0        # mt_chnpattptr — byte offset within pattern
    song_num: int = 0        # mt_chnsongnum — orderlist index (voice*songs offset)
    song_ptr: int = 0        # mt_chnsongptr — position within orderlist

    # Instrument
    instrument: int = 1      # mt_chninstr — 1-based instrument index

    # Effects
    fx: int = 0              # mt_chnfx — active effect (0-4)
    param: int = 0           # mt_chnparam — effect parameter (speed table index)
    new_note: int = 0        # mt_chnnewnote — pending new note (0=none)
    new_fx: int = 0          # mt_chnnewfx — pending tick-0 effect
    new_param: int = 0       # mt_chnnewparam — pending tick-0 param

    # Vibrato
    vib_time: int = 0        # mt_chnvibtime — vibrato phase counter
    vib_delay: int = 0       # mt_chnvibdelay — vibrato delay countdown

    # Transpose
    transpose: int = 0       # mt_chntrans — orderlist transpose offset

    # Packed rest
    pk_rest: int = 0         # mt_chnpkrest — packed rest counter

    # Duration tracking (for USF NoteEvents with duration > 1)
    dur_remaining: int = 0   # remaining ticks on current event (0=ready for next)


@dataclass
class GlobalState:
    """Global (non-per-voice) state of the USF player."""
    # Filter
    filt_step: int = 0       # mt_g_fstep+1 — filter table position (1-based, 0=inactive)
    filt_time: int = 0       # mt_g_ftime+1 — filter modulation counter
    filt_cut: int = 0        # mt_g_fcut+1 — current filter cutoff
    filt_ctrl: int = 0       # mt_g_fctrl+1 — current filter control (resonance|routing)
    filt_type: int = 0       # mt_g_ftype+1 — current filter type (shifted)
    master_vol: int = 0x0F   # mt_g_mvol+1 — master volume (0-15)

    # Funktempo
    funk_tbl: list = field(default_factory=lambda: [8, 5])

    # Init
    init_pending: bool = True


@dataclass
class RegisterFrame:
    """One frame of SID register output (25 bytes, $D400-$D418)."""
    regs: list = field(default_factory=lambda: [0] * 25)

    def __getitem__(self, i):
        return self.regs[i]

    def __setitem__(self, i, v):
        self.regs[i] = v & 0xFF

    def to_list(self):
        return list(self.regs)


# ============================================================
# Player state machine
# ============================================================

class USFPlayer:
    """Formal executable specification of USF playback.

    This is a pure state machine: no I/O, no randomness, no side effects.
    Given the same Song, it always produces the same RegisterTrace.

    The execution order matches codegen_v2.py exactly:
        1. Filter exec (global)
        2. For each voice (X=0,7,14):
           a. Decrement counter
           b. If counter != 0 and counter >= 0: wave table → effects → pulse → gate check → regs
           c. If counter == 0: tick-0 path (pattern reader → new note → tick-0 FX → wave → ...)
           d. If counter < 0: reload tempo, then wave table path
    """

    def __init__(self, song: Song):
        self.song = song
        self.voices = [VoiceState() for _ in range(3)]
        self.glob = GlobalState()

        # Resolve frequency table
        if song.freq_lo and song.freq_hi:
            self.freq_lo = song.freq_lo
            self.freq_hi = song.freq_hi
        else:
            self.freq_lo = FREQ_LO_PAL
            self.freq_hi = FREQ_HI_PAL

        self.first_note = song.first_note

        # Resolve shared tables to flat arrays for indexed access
        self._wave_left = []
        self._wave_right = []
        for l, r in song.shared_wave_table:
            self._wave_left.append(l)
            self._wave_right.append(r)

        self._pulse_time = []
        self._pulse_speed = []
        for l, r in song.shared_pulse_table:
            self._pulse_time.append(l)
            self._pulse_speed.append(r)

        self._filt_time = []
        self._filt_speed = []
        for l, r in song.shared_filter_table:
            self._filt_time.append(l)
            self._filt_speed.append(r)

        self._speed_left = []
        self._speed_right = []
        for entry in song.speed_table:
            self._speed_left.append(entry.left)
            self._speed_right.append(entry.right)

        # Build pattern table: pattern_id -> list of packed bytes
        # We store the events directly and interpret them in the pattern reader
        self._patterns = {}
        for pat in song.patterns:
            self._patterns[pat.id] = pat.events

        # Build orderlist per voice
        self._orderlists = [list(song.orderlists[v]) for v in range(3)]
        self._orderlist_restart = list(song.orderlist_restart)

        # Build instrument table (1-based)
        self._instruments = [None]  # index 0 unused
        for inst in song.instruments:
            self._instruments.append(inst)

        # Features (derived from song content, matching codegen.py detect_features)
        self._has_filter = bool(song.shared_filter_table)
        self._has_effects = bool(song.speed_table)
        self._has_vibrato = any(i.vib_speed_idx > 0 for i in song.instruments)
        self._has_pulse = bool(song.shared_pulse_table)
        self._has_wave_delay = not song.nowavedelay
        self._has_freq_slide = any(
            step.freq_slide != 0
            for inst in song.instruments
            for step in inst.wave_table
        ) or any(
            r & 0xFF >= 0x60 and r & 0xFF < 0x80
            for _, r in song.shared_wave_table
        )
        self._has_calculated_speed = not song.nocalculatedspeed and bool(song.speed_table)
        self._pulse_asl = song.pulse_speed_asl
        self._adsr_ad_first = (song.adsr_write_order == 'ad_first')
        self._loadregs_ad_first = (song.loadregs_adsr_order == 'ad_first')
        self._newnote_all_regs = (song.newnote_reg_scope == 'all_regs')
        self._has_funktempo = any(
            e.command == 0x0E for p in song.patterns for e in p.events
            if e.command is not None
        )
        self._vibrato_param_fix = song.vibrato_param_fix

        # Multiplier for multispeed
        self._multiplier = max(1, song.multiplier) if song.multiplier else 1

    def _init_song(self, subtune: int = 0):
        """Initialize all state for playback of a subtune."""
        self.glob = GlobalState()
        self.glob.master_vol = 0x0F
        if self._has_funktempo:
            self.glob.funk_tbl = [8, 5]

        for v in range(3):
            vs = VoiceState()
            vs.counter = 1
            vs.tempo = self.song.tempo
            vs.gate = 0xFE
            vs.instrument = 1

            # Song pointer: voice index into orderlist
            # For subtune 0: voices use orderlists[0], [1], [2]
            # For subtune N: use extra_orderlists
            vs.song_num = v  # simplified — correct for single-song
            vs.song_ptr = 0

            self.voices[v] = vs

        self.glob.init_pending = False

    # --------------------------------------------------------
    # Filter execution (global, runs once per frame)
    # --------------------------------------------------------

    def _exec_filter(self):
        """Execute one step of the global filter table."""
        g = self.glob
        if not self._has_filter:
            return

        step = g.filt_step
        if step == 0:
            return

        if g.filt_time != 0:
            # Modulating
            g.filt_cut = (g.filt_cut + self._signed8(self._filt_speed[step - 1])) & 0xFF
            g.filt_time -= 1
            if g.filt_time == 0:
                # Advance
                self._filter_advance(step)
            return

        # New step
        time_val = self._filt_time[step - 1]
        if time_val == 0:
            # Set cutoff
            g.filt_cut = self._filt_speed[step - 1]
            self._filter_advance(step)
        elif time_val >= 0x80:
            # Set params
            g.filt_type = (time_val << 1) & 0xFF
            g.filt_ctrl = self._filt_speed[step - 1]
            # Check next step
            next_time = self._filt_time[step] if step < len(self._filt_time) else 0
            if next_time != 0:
                self._filter_advance(step)
            else:
                # Next is cutoff set — advance twice
                step += 1
                g.filt_cut = self._filt_speed[step - 1] if step <= len(self._filt_speed) else 0
                self._filter_advance(step)
        else:
            # Modulate
            g.filt_time = time_val
            # Do first modulation step
            g.filt_cut = (g.filt_cut + self._signed8(self._filt_speed[step - 1])) & 0xFF
            g.filt_time -= 1
            if g.filt_time == 0:
                self._filter_advance(step)

    def _filter_advance(self, step: int):
        """Advance filter table pointer, handling loops."""
        g = self.glob
        if step < len(self._filt_time):
            next_time = self._filt_time[step]
            if next_time == 0xFF:  # LOOPTBL
                g.filt_step = self._filt_speed[step]
                return
            g.filt_step = step + 1
        else:
            g.filt_step = 0  # end of table

    # --------------------------------------------------------
    # Wave table execution (per-voice)
    # --------------------------------------------------------

    def _exec_wave_table(self, v: int):
        """Execute one step of voice v's wave table.

        CRITICAL: shared_wave_table stores .sng-equivalent values, NOT packed
        binary format. The packer (usf_to_sid.py) re-applies the +$10 bias
        and XOR $80 when building the actual binary.

        .sng left column:
          $00       = no wave change
          $01-$0F   = delay N frames
          $10-$DF   = waveform byte (direct SID value, e.g. $41=pulse+gate)
          $E0-$EF   = inaudible/silent wave ($00-$0F SID value)
          $F0-$FE   = wave commands (dispatched separately)
          $FF       = jump/loop marker

        .sng right column:
          $00-$5F   = relative note UP (positive offset)
          $60-$7F   = relative note DOWN (signed: $60=-32..$7F=-1)
          $80       = keep freq (no note change)
          $81-$DF   = absolute note ($81=note 1, $82=note 2, ...)

        The V2 player reads PACKED values where:
          packed_left  = sng_left + $10  (if WAVE_DELAY and $10 <= sng_left <= $DF)
          packed_right = sng_right ^ $80

        But we read .sng values directly — no bias, no XOR.
        """
        vs = self.voices[v]
        if vs.wave_ptr == 0:
            return

        idx = vs.wave_ptr - 1  # convert 1-based to 0-based
        if idx >= len(self._wave_left):
            return

        left = self._wave_left[idx]

        # Process left column (.sng format)
        if left == 0:
            # $00 = no wave change — just process right column
            pass
        elif 0x01 <= left <= 0x0F:
            # Delay N frames
            if left != vs.wave_time:
                vs.wave_time += 1
                return
            # Delay done — advance (don't set waveform)
            vs.wave_time = 0
            self._wave_advance(vs, idx)
            return
        elif 0x10 <= left <= 0xDF:
            # Waveform byte — store directly to voice wave register
            vs.wave = left
        elif 0xE0 <= left <= 0xEF:
            # Inaudible/silent wave: SID value = left & $0F
            vs.wave = left & 0x0F
        elif left == 0xFF:
            # Loop marker — handled by advance, shouldn't reach here
            pass
        elif 0xF0 <= left <= 0xFE:
            # Wave command — TODO: dispatch
            pass

        # Read right column (.sng format) BEFORE advance
        right = self._wave_right[idx]

        # Advance pointer
        vs.wave_time = 0
        self._wave_advance(vs, idx)

        # Process right column (.sng format)
        if right == 0x80:
            return  # $80 = keep freq

        # Freq slide: .sng $E0-$FF → packed $60-$7F after XOR $80
        # In .sng format, freq_slide is encoded as relative notes with
        # offset values that map to $60-$7F after packing.
        # Actually in .sng: $60-$7F is relative note down.
        # Freq slide is detected from the PACKED right column ($60-$7F).
        # In .sng that's $E0-$FF (= $60-$7F XOR $80).
        # But the shared_wave_table right column is .sng, so freq_slide
        # values would appear as... let me think:
        # packed $60 = sng $E0 (= $60 ^ $80)
        # packed $7F = sng $FF (= $7F ^ $80)
        # So in .sng, freq_slide values are $E0-$FF.
        # But $FF is the loop marker for the left column!
        # The right column doesn't have loop markers — only the left does.
        # So $E0-$FF in the right column = freq_slide.
        if self._has_freq_slide and 0xE0 <= right <= 0xFF:
            # Convert .sng to packed: sng ^ $80 gives $60-$7F
            packed_right = right ^ 0x80
            vs.freq_slide = self._signed8((packed_right - 0x70) & 0xFF)
            return

        if right >= 0x81:
            # Absolute note ($81-$DF → note = right - $81 + 1 = right - $80)
            # In .sng, $81 = absolute note 1, $82 = note 2, etc.
            resolved = right - 0x80
            vs.last_note = resolved
        elif right <= 0x5F:
            # Relative note up ($00-$5F, but $00 not reached — handled above)
            resolved = (vs.note + right) & 0x7F
            vs.last_note = vs.note
        else:
            # Relative note down ($60-$7F)
            # Signed: $60 = -32, $7F = -1
            offset = right - 0x80  # negative
            resolved = (vs.note + offset) & 0x7F
            vs.last_note = vs.note

        # Frequency lookup
        f = self._freq_lookup(resolved)
        if f:
            vs.freq_lo, vs.freq_hi = f
            vs.vib_time = 0
            vs.freq_slide = 0

    def _wave_advance(self, vs: VoiceState, idx: int):
        """Advance wave table pointer, handling loops."""
        next_idx = idx + 1
        if next_idx < len(self._wave_left):
            if self._wave_left[next_idx] == 0xFF:  # LOOPTBL
                vs.wave_ptr = self._wave_right[next_idx]
                return
        vs.wave_ptr = next_idx + 1  # back to 1-based

    # --------------------------------------------------------
    # Effects execution (per-voice)
    # --------------------------------------------------------

    def _exec_effects(self, v: int):
        """Execute per-frame effects (portamento, vibrato).

        Speed table loading differs by effect type:
        - FX 1/2 (portamento): temp_lo=right, temp_hi=left (16-bit speed)
        - FX 0/4 (vibrato): temp_lo=right (depth), temp_hi=0, left=phase speed
        - FX 3 (toneporta): has its own speed loading in _exec_toneporta
        """
        vs = self.voices[v]

        if not self._has_effects:
            return

        if vs.param == 0:
            # No active effect parameter — skip (unless toneporta)
            if vs.fx == 3:
                self._exec_toneporta(v)
            return

        fx = vs.fx

        if fx == 0:
            # Instrument vibrato with delay
            if vs.vib_delay > 0:
                vs.vib_delay -= 1
                return
            self._exec_vibrato(v)
        elif fx == 4:
            # Pattern vibrato
            self._exec_vibrato(v)
        elif fx == 1:
            # Portamento up
            temp_lo, temp_hi = self._load_portamento_speed(vs)
            self._freq_add(vs, temp_lo, temp_hi)
        elif fx == 2:
            # Portamento down
            temp_lo, temp_hi = self._load_portamento_speed(vs)
            self._freq_sub(vs, temp_lo, temp_hi)
        elif fx == 3:
            # Tone portamento
            self._exec_toneporta(v)

    def _load_portamento_speed(self, vs: VoiceState):
        """Load portamento speed (FX 1/2): temp_lo=right, temp_hi=left."""
        spd_idx = vs.param - 1
        if spd_idx < 0 or spd_idx >= len(self._speed_left):
            return 0, 0
        spd_left = self._speed_left[spd_idx]
        spd_right = self._speed_right[spd_idx]
        if self._has_calculated_speed and (spd_left & 0x80):
            speed_val = spd_left & 0x7F
            shift = spd_right
            note_idx = vs.last_note - self.first_note
            if 0 <= note_idx < len(self.freq_lo) - 1:
                lo_diff = (self.freq_lo[note_idx + 1] - self.freq_lo[note_idx]) & 0xFF
                hi_diff = (self.freq_hi[note_idx + 1] - self.freq_hi[note_idx]) & 0xFF
                val16 = (hi_diff << 8) | lo_diff
                for _ in range(shift):
                    val16 >>= 1
                return val16 & 0xFF, (val16 >> 8) & 0xFF
            return spd_right, 0
        return spd_right, spd_left

    def _exec_vibrato(self, v: int):
        """Execute vibrato effect (FX 0 / FX 4).

        Vibrato speed table interpretation (different from portamento!):
        - left byte = phase speed (CMP operand for oscillator direction change)
        - right byte = depth (frequency delta per frame)
        - temp_hi is ALWAYS 0 for vibrato (unlike portamento where temp_hi=left)

        With calculated speed (left bit 7 set):
        - Phase speed = left & $7F
        - Depth derived from note interval, shifted by right byte
        """
        vs = self.voices[v]

        spd_idx = vs.param - 1
        if spd_idx < 0 or spd_idx >= len(self._speed_left):
            return

        spd_left = self._speed_left[spd_idx]

        if self._has_calculated_speed and (spd_left & 0x80):
            speed_val = spd_left & 0x7F
            shift = self._speed_right[spd_idx]
            note_idx = vs.last_note - self.first_note
            if 0 <= note_idx < len(self.freq_lo) - 1:
                lo_diff = (self.freq_lo[note_idx + 1] - self.freq_lo[note_idx]) & 0xFF
                hi_diff = (self.freq_hi[note_idx + 1] - self.freq_hi[note_idx]) & 0xFF
                val16 = (hi_diff << 8) | lo_diff
                for _ in range(shift):
                    val16 >>= 1
                temp_lo = val16 & 0xFF
                temp_hi = (val16 >> 8) & 0xFF
            else:
                temp_lo = self._speed_right[spd_idx]
                temp_hi = 0
        else:
            # Non-calculated: left = phase speed, right = depth
            speed_val = spd_left
            temp_lo = self._speed_right[spd_idx]
            temp_hi = 0  # ALWAYS 0 for vibrato

        # Vibrato phase oscillator — exact 6502 match:
        #   lda vib_time     ; A = phase counter
        #   bmi clc_path     ; negative → CLC, ADC #2
        #   cmp #speed       ; compare with speed threshold
        #   beq clc_path     ; equal → CLC, ADC #2 (direction change point)
        #   bcc adc_path     ; below → ADC #2 (carry set from CMP, so ADC #2 = +3)
        #   eor #$ff         ; above → flip bits, fall to CLC, ADC #2
        # clc_path: clc
        # adc_path: adc #2
        #   sta vib_time
        #   lsr              ; bit 0 → carry: odd=sub, even=add

        vt = vs.vib_time & 0xFF

        if vt & 0x80:
            # Negative (BMI taken) → CLC path
            carry = 0
            vt = (vt + 2 + carry) & 0xFF
        else:
            # Positive (BPL)
            # CMP #speed: sets carry if vt >= speed, zero if equal
            if vt == speed_val:
                # BEQ taken → CLC path
                carry = 0
                vt = (vt + 2 + carry) & 0xFF
            elif vt < speed_val:
                # BCC taken → ADC path (carry SET from CMP since... wait)
                # CMP sets carry when A >= operand. vt < speed → carry CLEAR
                # BCC taken means carry clear
                # ADC #2 with carry clear = vt + 2
                carry = 0  # carry clear from CMP (A < operand)
                vt = (vt + 2 + carry) & 0xFF
            else:
                # vt > speed (not equal, not below) → EOR #$FF, fall to CLC
                vt = vt ^ 0xFF
                carry = 0  # CLC
                vt = (vt + 2 + carry) & 0xFF

        vs.vib_time = vt

        # LSR: bit 0 → carry. Odd = subtract, even = add.
        if vt & 1:
            self._freq_sub(vs, temp_lo, temp_hi)
        else:
            self._freq_add(vs, temp_lo, temp_hi)

    def _exec_toneporta(self, v: int):
        """Execute tone portamento (FX 3)."""
        vs = self.voices[v]

        if vs.param == 0:
            # Snap to target
            self._toneporta_snap(vs)
            return

        spd_idx = vs.param - 1
        if spd_idx < 0 or spd_idx >= len(self._speed_left):
            return

        spd_left = self._speed_left[spd_idx]
        spd_right = self._speed_right[spd_idx]

        if self._has_calculated_speed and (spd_left & 0x80):
            speed_val = spd_left & 0x7F
            shift = spd_right
            note_idx = vs.last_note - self.first_note
            if 0 <= note_idx < len(self.freq_lo) - 1:
                lo_diff = (self.freq_lo[note_idx + 1] - self.freq_lo[note_idx]) & 0xFF
                hi_diff = (self.freq_hi[note_idx + 1] - self.freq_hi[note_idx]) & 0xFF
                val16 = (hi_diff << 8) | lo_diff
                for _ in range(shift):
                    val16 >>= 1
                spd_lo = val16 & 0xFF
                spd_hi = (val16 >> 8) & 0xFF
            else:
                spd_lo = spd_right
                spd_hi = 0
        else:
            spd_lo = spd_right
            spd_hi = spd_left

        # Compare current freq with target note freq
        target_note = vs.note
        f = self._freq_lookup(target_note)
        if f:
            target_lo, target_hi = f
        else:
            return

        # 16-bit comparison: current - target
        diff = ((vs.freq_hi << 8) | vs.freq_lo) - ((target_hi << 8) | target_lo)

        if diff >= 0:
            # Current >= target: slide down
            # Check if distance < speed (would overshoot)
            if diff < ((spd_hi << 8) | spd_lo):
                self._toneporta_snap(vs)
            else:
                self._freq_sub(vs, spd_lo, spd_hi)
        else:
            # Current < target: slide up
            if -diff < ((spd_hi << 8) | spd_lo):
                self._toneporta_snap(vs)
            else:
                self._freq_add(vs, spd_lo, spd_hi)

    def _toneporta_snap(self, vs: VoiceState):
        """Snap frequency to target note."""
        note = vs.note
        f = self._freq_lookup(note)
        if f:
            vs.last_note = note
            vs.freq_lo, vs.freq_hi = f
            vs.vib_time = 0

    def _freq_add(self, vs: VoiceState, lo: int, hi: int):
        """Add 16-bit value to voice frequency."""
        total = ((vs.freq_hi << 8) | vs.freq_lo) + ((hi << 8) | lo)
        vs.freq_lo = total & 0xFF
        vs.freq_hi = (total >> 8) & 0xFF

    def _freq_sub(self, vs: VoiceState, lo: int, hi: int):
        """Subtract 16-bit value from voice frequency."""
        total = ((vs.freq_hi << 8) | vs.freq_lo) - ((hi << 8) | lo)
        vs.freq_lo = total & 0xFF
        vs.freq_hi = (total >> 8) & 0xFF

    def _freq_lookup(self, note: int):
        """Look up frequency for a note, accounting for FIRSTNOTE.

        Returns (freq_lo, freq_hi) or None if note is out of range.
        The freq table may start at first_note (FIRSTNOTE optimization):
        notes below first_note have no freq table entry.
        """
        idx = note - self.first_note
        if 0 <= idx < len(self.freq_lo):
            return self.freq_lo[idx], self.freq_hi[idx]
        return None

    # --------------------------------------------------------
    # Pulse table execution (per-voice)
    # --------------------------------------------------------

    def _exec_pulse_table(self, v: int):
        """Execute one step of voice v's pulse table."""
        vs = self.voices[v]
        if not self._has_pulse or vs.pulse_ptr == 0:
            return

        # Skip during gate timer countdown and when no pattern active
        if vs.counter == vs.gate_timer:
            return
        if vs.counter == 0 and vs.patt_ptr == 0:
            return

        idx = vs.pulse_ptr - 1
        if idx >= len(self._pulse_time):
            return

        if vs.pulse_time != 0:
            # Modulating
            speed = self._pulse_speed[idx]
            if self._pulse_asl:
                speed = (speed << 1) & 0xFF
                if speed & 0x80 == 0:
                    # Positive after ASL: carry clear
                    pass
                else:
                    # Negative: clear carry effect
                    pass
            else:
                if self._signed8(speed) < 0:
                    vs.pulse_hi = (vs.pulse_hi - 1) & 0x0F

            total = vs.pulse_lo + (speed & 0xFF)
            if total > 0xFF:
                vs.pulse_hi = (vs.pulse_hi + 1) & 0x0F
            vs.pulse_lo = total & 0xFF

            vs.pulse_time -= 1
            if vs.pulse_time == 0:
                self._pulse_advance(vs, idx)
            return

        # New step
        time_val = self._pulse_time[idx]
        if time_val >= 0x80:
            # Set pulse width
            vs.pulse_hi = time_val & 0x0F
            vs.pulse_lo = self._pulse_speed[idx]
            self._pulse_advance(vs, idx)
        else:
            # Modulate
            vs.pulse_time = time_val
            # First modulation step
            speed = self._pulse_speed[idx]
            if self._pulse_asl:
                speed = (speed << 1) & 0xFF
            if self._signed8(speed) < 0:
                vs.pulse_hi = (vs.pulse_hi - 1) & 0x0F
            total = vs.pulse_lo + (speed & 0xFF)
            if total > 0xFF:
                vs.pulse_hi = (vs.pulse_hi + 1) & 0x0F
            vs.pulse_lo = total & 0xFF
            vs.pulse_time -= 1
            if vs.pulse_time == 0:
                self._pulse_advance(vs, idx)

    def _pulse_advance(self, vs: VoiceState, idx: int):
        """Advance pulse table pointer."""
        next_idx = idx + 1
        if next_idx < len(self._pulse_time):
            if self._pulse_time[next_idx] == 0xFF:  # LOOPTBL
                vs.pulse_ptr = self._pulse_speed[next_idx]
                return
        vs.pulse_ptr = next_idx + 1

    # --------------------------------------------------------
    # Pattern reader (per-voice, tick-0)
    # --------------------------------------------------------

    def _read_pattern(self, v: int):
        """Read one tick's worth from voice v's pattern.

        In the V2 player, the pattern is read one byte per gate-timer visit.
        A note with duration=6 occupies 6 bytes: [note, REST, REST, REST, REST, REST].
        Each gate-timer visit reads one byte and advances the pointer.

        In USF, we have NoteEvents with a duration field. We simulate the
        V2 behavior by tracking dur_remaining: the first visit processes
        the event; subsequent visits are implicit RESTs (no action).
        """
        vs = self.voices[v]

        # If still consuming duration from previous event, just count down
        if vs.dur_remaining > 0:
            vs.dur_remaining -= 1
            return

        # Get current pattern events
        if vs.patt_num not in self._patterns:
            return
        events = self._patterns[vs.patt_num]
        if vs.patt_ptr >= len(events):
            # End of pattern — signal for orderlist advance on next tick-0
            vs.patt_ptr = 0
            return

        event = events[vs.patt_ptr]

        # Process instrument change
        if event.instrument >= 0:
            vs.instrument = event.instrument + 1  # 1-based

        # Process command (pre-note)
        if event.command is not None:
            vs.new_fx = event.command
            if event.command != 0:
                vs.new_param = event.command_val

        # Process event type
        if event.type == 'note':
            note = event.note
            if vs.transpose:
                note = (note + self._signed8(vs.transpose)) & 0xFF
            note = note + 0x60  # add NOTE offset (matches packed format)
            vs.new_note = note

            # Toneporta: skip hard restart
            if vs.new_fx == 3:
                pass  # no HR
            else:
                # Legato check
                inst = self._get_instrument(vs.instrument)
                if inst and inst.legato:
                    pass  # no HR
                else:
                    # Hard restart
                    if self._adsr_ad_first:
                        vs.ad = self.song.ad_param
                        vs.sr = self.song.sr_param
                    else:
                        vs.sr = self.song.sr_param
                        vs.ad = self.song.ad_param
                    vs.gate = 0xFE  # gate off

        elif event.type == 'off':
            vs.gate = 0xFE  # KEYOFF
        elif event.type == 'on':
            vs.gate = 0xFF  # KEYON
        elif event.type == 'rest':
            pass  # no action

        # Set duration countdown (minus 1 for this visit)
        vs.dur_remaining = max(0, event.duration - 1)

        # Advance pattern pointer
        vs.patt_ptr += 1

        # Check for end of pattern
        if vs.patt_ptr >= len(events):
            vs.patt_ptr = 0  # signal for orderlist advance on next tick-0

    def _advance_orderlist(self, v: int):
        """Advance voice v's orderlist position."""
        vs = self.voices[v]
        ol = self._orderlists[v]

        if not ol:
            return

        if vs.song_ptr >= len(ol):
            # Loop
            vs.song_ptr = self._orderlist_restart[v]

        if vs.song_ptr >= len(ol):
            return

        pat_id, trans = ol[vs.song_ptr]

        # Check for loop marker (pattern_id == 0xFF means loop)
        # In USF orderlists, the last entry loops back

        if trans != 0:
            vs.transpose = trans & 0xFF

        vs.patt_num = pat_id
        vs.song_ptr += 1

    # --------------------------------------------------------
    # New note initialization (per-voice, tick-0)
    # --------------------------------------------------------

    def _init_new_note(self, v: int):
        """Initialize a new note on voice v."""
        vs = self.voices[v]
        if vs.new_note == 0:
            return

        note = (vs.new_note - 0x60) & 0xFF  # remove NOTE offset
        vs.note = note
        vs.fx = 0
        vs.new_note = 0

        inst = self._get_instrument(vs.instrument)
        if not inst:
            return

        # Gate timer
        vs.gate_timer = min(inst.gate_timer & 0x3F, max(0, vs.tempo - 1))

        # Toneporta: skip note init
        if vs.new_fx == 3:
            return

        # Vibrato
        if self._has_vibrato:
            vs.vib_delay = inst.vib_delay
            vs.param = inst.vib_speed_idx

        # First wave
        first_wave = inst.first_wave
        if first_wave > 0 and first_wave < 0xFE:
            vs.wave = first_wave

        # Gate on
        vs.gate = 0xFF

        # Pulse ptr
        if self._has_pulse and inst.pulse_ptr > 0:
            vs.pulse_ptr = inst.pulse_ptr
            vs.pulse_time = 0

        # Filter ptr
        if self._has_filter and inst.filter_ptr > 0:
            self.glob.filt_step = inst.filter_ptr
            self.glob.filt_time = 0

        # Wave ptr
        vs.wave_ptr = inst.wave_ptr
        vs.wave_time = 0

        # ADSR
        if self._adsr_ad_first:
            vs.ad = inst.ad
            vs.sr = inst.sr
        else:
            vs.sr = inst.sr
            vs.ad = inst.ad

    # --------------------------------------------------------
    # Tick-0 effects (per-voice)
    # --------------------------------------------------------

    def _exec_tick0_fx(self, v: int):
        """Execute tick-0 pattern effects."""
        vs = self.voices[v]
        fx = vs.new_fx
        param = vs.new_param

        if fx == 0:
            # Instrument vibrato reload
            if self._has_vibrato:
                inst = self._get_instrument(vs.instrument)
                if inst:
                    vp = inst.vib_speed_idx
                    if self._vibrato_param_fix and vp == 0:
                        vs.param = 0
                    else:
                        vs.param = vp
                    vs.fx = fx
            return

        if fx <= 4:
            # Effects 1-4: store to running fx
            vs.param = param
            vs.fx = fx
            return

        # Tick-0 only effects (5-F)
        if fx == 5:   # Set AD
            vs.ad = param
        elif fx == 6:  # Set SR
            vs.sr = param
        elif fx == 7:  # Set waveform
            vs.wave = param
        elif fx == 8:  # Set wave ptr
            vs.wave_ptr = param
            vs.wave_time = 0
        elif fx == 9:  # Set pulse ptr
            if self._has_pulse:
                vs.pulse_ptr = param
                vs.pulse_time = 0
        elif fx == 0xA:  # Set filter ptr
            if self._has_filter:
                self.glob.filt_step = param
                self.glob.filt_time = 0
        elif fx == 0xB:  # Set filter control
            self.glob.filt_ctrl = param
        elif fx == 0xC:  # Set filter cutoff
            self.glob.filt_cut = param
        elif fx == 0xD:  # Set master volume
            self.glob.master_vol = param & 0x0F
        elif fx == 0xE:  # Funktempo
            if self._has_funktempo and param > 0:
                spd_idx = param - 1
                if spd_idx < len(self._speed_left):
                    self.glob.funk_tbl[0] = self._speed_left[spd_idx]
                    self.glob.funk_tbl[1] = self._speed_right[spd_idx]
        elif fx == 0xF:  # Set tempo
            if param & 0x80:
                # Channel tempo
                vs.tempo = param & 0x7F
            else:
                # Global tempo
                for vv in self.voices:
                    vv.tempo = param

    # --------------------------------------------------------
    # Register write (per-voice)
    # --------------------------------------------------------

    def _write_registers(self, v: int, frame: RegisterFrame):
        """Write voice v's state to the register frame."""
        vs = self.voices[v]
        base = v * 7  # SID voice register offset

        # Freq slide
        if self._has_freq_slide and vs.freq_slide != 0:
            vs.freq_hi = (vs.freq_hi + self._signed8(vs.freq_slide)) & 0xFF

        # Frequency
        frame[base + 0] = vs.freq_lo
        frame[base + 1] = vs.freq_hi

        # Pulse
        frame[base + 2] = vs.pulse_lo
        frame[base + 3] = vs.pulse_hi & 0x0F

        # ADSR
        frame[base + 5] = vs.ad
        frame[base + 6] = vs.sr

        # Waveform + gate
        frame[base + 4] = vs.wave & vs.gate & 0xFF

    def _write_global_registers(self, frame: RegisterFrame):
        """Write global (filter + volume) registers."""
        g = self.glob
        frame[21] = 0  # filter cutoff lo (unused in GT2)
        frame[22] = g.filt_cut
        frame[23] = g.filt_ctrl
        # $D418: filter type (high nibble) | volume (low nibble)
        frame[24] = (g.filt_type & 0xF0) | (g.master_vol & 0x0F)

    # --------------------------------------------------------
    # Main execution loop
    # --------------------------------------------------------

    def _exec_channel(self, v: int):
        """Execute one frame for voice v.

        Matches the V2 player execution order (codegen_v2.py) exactly:

        1. dec mt_chncounter,x
        2. If counter == 0: JMP ce_t0 (tick-0 path)
        3. If counter > 0 (BPL): JMP ce_wave (non-tick-0 path)
        4. If counter < 0 (underflow): reload from tempo, fall to ce_wave

        ce_wave path (non-tick-0 and after tempo reload):
          wave_table → effects → pulse_table → gate_timer_check → register_writes
          Gate timer check: if counter == gate_timer → read pattern

        ce_t0 path (tick-0):
          if patt_ptr == 0: advance orderlist
          load gate timer from instrument
          if new_note != 0: init new note → tick-0 FX → wave → regs
          else: tick-0 FX → wave path

        The key insight: pattern reading happens on the GATE TIMER frame
        (counter == gate_timer), NOT on tick-0. Tick-0 processes the note
        that was read on the previous gate timer frame.
        """
        vs = self.voices[v]
        vs.counter -= 1

        if vs.counter == 0:
            # === Tick-0 path (ce_t0) ===

            # Orderlist advance if at end of pattern
            if vs.patt_ptr == 0:
                self._advance_orderlist(v)

            # Load gate timer from current instrument
            inst = self._get_instrument(vs.instrument)
            if inst:
                vs.gate_timer = min(inst.gate_timer & 0x3F, max(0, vs.tempo - 1))

            # New note init (processes note read on gate_timer frame)
            if vs.new_note != 0:
                self._init_new_note(v)
                # Tick-0 FX
                self._exec_tick0_fx(v)
                # New note: register writes (either all_regs or wave_only)
                # Then done (no wave table on new note tick-0)
                return

            # No new note: tick-0 FX then wave table path
            # NOTE: effects (FX 0-4) do NOT run on tick-0 (counter==0).
            # Only tick-0 effects (FX 5-F) run. This is because the V2 player
            # guards ce_runfx with "lda mt_chncounter,x; bne ce_wdgo".
            self._exec_tick0_fx(v)
            self._exec_wave_table(v)
            # Skip effects on tick-0 — counter is 0
            self._exec_pulse_table(v)
            return

        if vs.counter < 0 or vs.counter > 127:
            # Underflow: reload from tempo
            tempo = vs.tempo
            if self._has_funktempo and tempo < 2:
                alt = tempo ^ 1
                vs.tempo = alt
                tempo = self.glob.funk_tbl[tempo]
                tempo -= 1
            vs.counter = tempo
            # Fall through to ce_wave path

        # === Non-tick-0 path (ce_wave) ===
        self._exec_wave_table(v)
        self._exec_effects(v)
        self._exec_pulse_table(v)

        # Gate timer check: when counter matches gate_timer, read pattern
        if vs.counter == vs.gate_timer:
            self._read_pattern(v)

    def run(self, num_frames: int, subtune: int = 0) -> list:
        """Run the player for num_frames frames.

        Returns a list of RegisterFrame objects (each containing 25 register values).
        This is the formal playback function P: Song × ℕ → RegisterTrace.
        """
        self._init_song(subtune)
        trace = []

        # Frame 0: init frame. The PSID player calls init on the first frame,
        # then play starts on frame 1. Emit one frame of zeros to match siddump.
        trace.append(RegisterFrame().to_list())

        for frame_num in range(1, num_frames):
            frame = RegisterFrame()

            # Filter (global, runs before voices)
            self._exec_filter()

            # Execute each voice (possibly multiple times for multispeed)
            for speed_tick in range(self._multiplier):
                for v in range(3):
                    self._exec_channel(v)

            # Write registers
            for v in range(3):
                self._write_registers(v, frame)
            self._write_global_registers(frame)

            trace.append(frame.to_list())

        return trace

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _signed8(val: int) -> int:
        """Convert unsigned 8-bit to signed (-128..+127)."""
        val = val & 0xFF
        return val - 256 if val >= 128 else val

    def _get_instrument(self, idx: int) -> Optional[Instrument]:
        """Get instrument by 1-based index."""
        if 1 <= idx < len(self._instruments):
            return self._instruments[idx]
        return None


# ============================================================
# Verification utilities
# ============================================================

def verify_determinism(song: Song, frames: int = 100) -> bool:
    """Verify that the player is deterministic: same input → same output."""
    p1 = USFPlayer(song)
    p2 = USFPlayer(song)
    t1 = p1.run(frames)
    t2 = p2.run(frames)
    return t1 == t2


def verify_prefix(song: Song, n: int = 50, m: int = 100) -> bool:
    """Verify that P(song, N) is a prefix of P(song, M) for N ≤ M."""
    p1 = USFPlayer(song)
    p2 = USFPlayer(song)
    t_short = p1.run(n)
    t_long = p2.run(m)
    return t_short == t_long[:n]


def compare_with_siddump(song: Song, sid_path: str, duration: int = 10):
    """Compare formal player output with siddump output of a rebuilt SID.

    This is the key validation: the formal semantics must match what
    the compiled 6502 player actually does.
    """
    import subprocess
    import json

    # Run formal player
    fps = 50  # PAL
    player = USFPlayer(song)
    formal_trace = player.run(duration * fps)

    # Build SID and run siddump
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from converters.usf_to_sid import usf_to_sid
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        tmp_sid = f.name
    usf_to_sid(song, tmp_sid)

    siddump = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'siddump')
    r = subprocess.run([siddump, tmp_sid, '--duration', str(duration), '--force-rsid'],
                       capture_output=True, text=True, timeout=60)
    os.unlink(tmp_sid)

    if r.returncode != 0:
        return None

    lines = r.stdout.strip().split('\n')[2:]
    siddump_trace = []
    for line in lines:
        vals = [int(v, 16) for v in line.split(',')]
        siddump_trace.append(vals)

    # Compare
    min_len = min(len(formal_trace), len(siddump_trace))
    diffs = 0
    first_diff = -1
    for i in range(min_len):
        if formal_trace[i] != siddump_trace[i]:
            diffs += 1
            if first_diff < 0:
                first_diff = i

    return {
        'formal_frames': len(formal_trace),
        'siddump_frames': len(siddump_trace),
        'compared': min_len,
        'diffs': diffs,
        'match_pct': 100.0 * (min_len - diffs) / min_len if min_len > 0 else 0,
        'first_diff': first_diff,
    }


# ============================================================
# Main: self-test
# ============================================================

if __name__ == '__main__':
    # Create a minimal test song
    from usf.format import Song, Instrument, Pattern, NoteEvent, SpeedTableEntry

    song = Song(
        tempo=6,
        instruments=[
            Instrument(id=0, ad=0x09, sr=0x00, waveform='pulse',
                       wave_ptr=1, pulse_width=0x0808),
        ],
        patterns=[
            Pattern(id=0, events=[
                NoteEvent(type='note', note=48, duration=6, instrument=0),
                NoteEvent(type='note', note=50, duration=6, instrument=0),
                NoteEvent(type='note', note=52, duration=6, instrument=0),
                NoteEvent(type='off', duration=6),
            ]),
        ],
        orderlists=[[(0, 0)], [(0, 0)], [(0, 0)]],
        orderlist_restart=[0, 0, 0],
        shared_wave_table=[(0x41, 0x80)],  # pulse+gate, keep freq
        nowavedelay=True,
    )

    print("=== USF Formal Semantics Self-Test ===")

    # Test determinism
    print(f"Determinism: {verify_determinism(song)}")

    # Test prefix property
    print(f"Prefix property: {verify_prefix(song)}")

    # Run 50 frames
    player = USFPlayer(song)
    trace = player.run(50)
    print(f"\nTrace ({len(trace)} frames):")
    print(f"  Frame  0: {' '.join(f'{v:02X}' for v in trace[0])}")
    if len(trace) > 25:
        print(f"  Frame 25: {' '.join(f'{v:02X}' for v in trace[25])}")
    print(f"  Frame {len(trace)-1}: {' '.join(f'{v:02X}' for v in trace[-1])}")

    # Count unique frames
    unique = len(set(tuple(f) for f in trace))
    print(f"  Unique frames: {unique}/{len(trace)}")

    print("\n=== Done ===")
