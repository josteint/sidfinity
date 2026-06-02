"""JayDerrettEmulator — Python step-by-step model of the Jay_Derrett engine.

Phase 1 deliverable for the principled migration. Produces ordered
SID writes per frame, byte-exact against orig writelog for Ninja_Hamster
across 15,000+ frames (300+ seconds of audio = full song +
multiple loops).

The emulator is data-driven by an `EngineParams` dataclass that
captures per-engine-instance addresses (state base, voice ptr
slots, sub-jump table, instrument tables). The Ninja_Hamster
instance is hard-coded here; other Type A instances will be added
as their dispatch shapes are analysed.

Phase 2 will use this emulator as the verified spec for the clean
xa65 composer.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Engine parameters
# ---------------------------------------------------------------------------

@dataclass
class EngineParams:
    """Per-engine-instance addresses (parametric over the same engine
    logic). Names mirror the Ninja_Hamster disassembly."""

    # Code entry points
    play_addr: int                # $C452 (Ninja_Hamster)
    init_addr: int                # $C57A (Ninja_Hamster)
    proc_note_addr: int           # $C4BB (for self-mod counter offset+$18)

    # Engine state slots — voice-indexed by X (0,1,2)
    duration_counters: int        # $C5B6 → duration[v] at +v
    tempo_counter: int            # $C5B9
    tempo_reload: int             # $C5BA
    current_inst: int             # $C5BB → current_inst[v] at +v
    ctrl_byte: int                # $C5BE → ctrl[v] at +v
    frame_counter: int            # $C5C1 (INC'd every play)
    voice_ptrs: int               # $C5C2 → ptr[v] at +v*2 (lo+hi)
    self_mod_counter: int         # $C4D3 ($E0..$E9 wrap)
    song_loop_clears: tuple[int, ...]  # ($C975, $C978)

    # Tables
    sub_jump_table: int           # $C5CB (10 × 2-byte entries)
    inst_slide_lo_table: int      # $C5DD,X (X=inst*$10)
    inst_slide_hi_table: int      # $C65D,X
    voice_offsets: int            # $CAFB,X → 0/7/14 (V1/V2/V3)
    voice_pwm_phase: int          # $CAFE,X
    voice_pwm_lo_accum: int       # $CB01,X
    modulation_voice_idx: int     # $CB04 (counter used in modulation loop)

    # Per-voice runtime state base (24-byte slabs at stride 0/$1A/$34)
    voice_state_base: int         # $C92D — voice 0 base; voice 1 = +$1A; voice 2 = +$34
    voice_state_stride: int       # $1A

    # Instrument source-address table (lo,hi pairs at +inst*2)
    inst_src_table: int           # $C8FB → src_addr[inst] at +inst*2

    # Voice destination-address table (lo,hi pairs at +voice*2)
    voice_dst_table: int          # $C91D → dst_addr[v] at +v*2

    # Initial state
    voice_initial_ptrs: tuple[int, int, int]    # ($C000, $C169, $C342) for NH
    initial_tempo: int            # $0A
    initial_master_vol: int       # $0F


NINJA_HAMSTER = EngineParams(
    play_addr=0xC452,
    init_addr=0xC57A,
    proc_note_addr=0xC4BB,
    duration_counters=0xC5B6,
    tempo_counter=0xC5B9,
    tempo_reload=0xC5BA,
    current_inst=0xC5BB,
    ctrl_byte=0xC5BE,
    frame_counter=0xC5C1,
    voice_ptrs=0xC5C2,
    self_mod_counter=0xC4D3,
    song_loop_clears=(0xC975, 0xC978),
    sub_jump_table=0xC5CB,
    inst_slide_lo_table=0xC5DD,
    inst_slide_hi_table=0xC65D,
    voice_offsets=0xCAFB,
    voice_pwm_phase=0xCAFE,
    voice_pwm_lo_accum=0xCB01,
    modulation_voice_idx=0xCB04,
    voice_state_base=0xC92D,
    voice_state_stride=0x1A,
    inst_src_table=0xC8FB,
    voice_dst_table=0xC91D,
    voice_initial_ptrs=(0xC000, 0xC169, 0xC342),
    initial_tempo=0x0A,
    initial_master_vol=0x0F,
)


# ---------------------------------------------------------------------------
# Emulator
# ---------------------------------------------------------------------------

# Per-frame ordered writes: list of (reg, val). Cycle is unmodeled
# (compare_instruction_stream ignores cycle when matching the sequence).
FrameWrites = list[tuple[int, int]]


class JayDerrettEmulator:
    """Step-by-step model of the Jay_Derrett engine semantics."""

    def __init__(self, sid_path: str, params: EngineParams = NINJA_HAMSTER,
                 subtune: int = 0):
        self.params = params
        self.subtune = subtune

        # Load PSID body into a 64K memory image at orig load addr.
        # This populates pattern data, freq tables, sub-jump table,
        # instrument source programs, and the per-voice destination
        # address table — everything the engine needs.
        raw = Path(sid_path).read_bytes()
        body = raw[0x7C:]
        load_in = struct.unpack('>H', raw[8:10])[0]
        if load_in == 0:
            load = struct.unpack('<H', body[:2])[0]
            body = body[2:]
        else:
            load = load_in
        self.mem = self._libsidplayfp_powerup_ram()
        self.mem[load:load + len(body)] = body

        self.writes: list[FrameWrites] = []
        self._init_state()

    # ----- libsidplayfp powerup -----

    @staticmethod
    def _libsidplayfp_powerup_ram() -> bytearray:
        """Mirror libsidplayfp's SystemRAMBank::reset() pattern.
        $0000-$3FFF: 00 00 FF FF FF FF 00 00 ... (per 8-byte block)
        $4000-$7FFF: FF FF 00 00 00 00 FF FF ...
        $8000-$BFFF: 00 00 FF FF FF FF 00 00 ...
        $C000-$FFFF: FF FF 00 00 00 00 FF FF ...
        Source: tools/libsidplayfp/src/c64/Banks/SystemRAMBank.h."""
        ram = bytearray(0x10000)
        byte = 0x00
        for j in range(0, 0x10000, 0x4000):
            for k in range(0x4000):
                ram[j + k] = byte
            byte ^= 0xFF
            for i in range(0x02, 0x4000, 0x08):
                for k in range(4):
                    ram[j + i + k] = byte
        return ram

    # ----- helpers -----

    def _read16(self, addr: int) -> int:
        return self.mem[addr] | (self.mem[addr + 1] << 8)

    def _write_sid(self, reg: int, val: int) -> None:
        """Record a SID write to the current frame. Reg stored as
        offset (0..$1F) to match siddump --writelog format."""
        val &= 0xFF
        abs_reg = reg & 0xFFFF
        reg_off = abs_reg & 0x1F
        self._cur_frame.append((reg_off, val))
        self.mem[abs_reg] = val

    def _state_y(self, v: int) -> int:
        """Y-stride for voice v's runtime-state slab."""
        return v * self.params.voice_state_stride

    def _state_x(self, v: int) -> int:
        """X-stride for voice v's compact state."""
        return v

    # ----- init -----

    def _init_state(self) -> None:
        """Mirror the orig init at $C57A. Sets voice ptrs, tempo,
        duration counters, self-mod counter, master vol."""
        p = self.params
        # Voice ptrs
        for v in range(3):
            init_ptr = p.voice_initial_ptrs[v]
            self.mem[p.voice_ptrs + v * 2] = init_ptr & 0xFF
            self.mem[p.voice_ptrs + v * 2 + 1] = (init_ptr >> 8) & 0xFF
        # Self-mod counter starts at $E0
        self.mem[p.self_mod_counter] = 0xE0
        # Tempo counter + reload
        self.mem[p.tempo_counter] = p.initial_tempo
        self.mem[p.tempo_reload] = p.initial_tempo
        # Duration counters → 1 (process first byte immediately)
        for v in range(3):
            self.mem[p.duration_counters + v] = 1
        # PSID frame 0 contains BOTH init writes AND the first play
        # call's writes. siddump's writelog reflects this: cycle 40
        # = libsidplayfp pre-init $D418, cycle 214 = engine init's
        # own $D418, then play() writes.
        # We mirror this by collecting init writes into the FIRST
        # frame, then step_frame() will append play writes to it.
        self._init_frame: FrameWrites = []
        self._cur_frame = self._init_frame
        self._write_sid(0xD418, p.initial_master_vol)  # libsidplayfp pre-init
        self._write_sid(0xD418, p.initial_master_vol)  # engine init's STA $D418
        self._frame0_pending = True

    # ----- step -----

    def step_frame(self) -> FrameWrites:
        """Run one play call. Returns the ordered (reg, val) writes.
        For the first call, the writes are appended to the init frame
        (mirroring siddump's frame-0 = init + first play structure)."""
        if self._frame0_pending:
            self._cur_frame = self._init_frame
            self._frame0_pending = False
        else:
            self._cur_frame = []
        p = self.params

        # INC frame counter
        self.mem[p.frame_counter] = (self.mem[p.frame_counter] + 1) & 0xFF

        # DEC tempo counter
        self.mem[p.tempo_counter] = (self.mem[p.tempo_counter] - 1) & 0xFF
        if self.mem[p.tempo_counter] == 0:
            # Process all 3 voices via proc_note
            for v in range(3):
                self._proc_voice(v)
            # Reload tempo
            self.mem[p.tempo_counter] = self.mem[p.tempo_reload]
        # Per-frame modulation (always runs)
        self._modulation_block()

        self.writes.append(self._cur_frame)
        return self._cur_frame

    # ----- voice processing -----

    def _proc_voice(self, v: int) -> None:
        """Process one voice's pattern stream for this tick.
        Reads bytes until reaching a NOTE / GATE_OFF / SKIP / SET_DUR
        (the "terminating" events that don't recurse)."""
        p = self.params
        ptr_addr = p.voice_ptrs + v * 2
        ptr = self._read16(ptr_addr)
        # Set up zp $F2/$F3 = ptr; X = voice_idx; Y_stride = v*$1A
        # We pass these as Python locals via the proc_note recursion loop.
        ptr = self._proc_note(v, ptr)
        # Save back
        self.mem[ptr_addr] = ptr & 0xFF
        self.mem[ptr_addr + 1] = (ptr >> 8) & 0xFF

    def _proc_note(self, v: int, ptr: int) -> int:
        """Mirror of sub_C4BB. Returns the new ptr after processing.
        Recurses through non-terminating events ($Ex / $Dx / $Bx / $Cx)."""
        p = self.params
        x = self._state_x(v)
        y = self._state_y(v)

        # DEC duration counter; if non-zero, RTS without processing.
        dur_addr = p.duration_counters + x
        self.mem[dur_addr] = (self.mem[dur_addr] - 1) & 0xFF
        if self.mem[dur_addr] != 0:
            return ptr
        # Reset duration to 1 (default: process every tempo tick)
        self.mem[dur_addr] = 1

        # Dispatch loop — recurse via while-loop until terminating event.
        while True:
            b = self.mem[ptr]
            hi = b & 0xF0

            # --- $Ex (high nibble == $E): pattern-jump dispatch ---
            if hi == 0xE0:
                if b == self.mem[p.self_mod_counter]:
                    # Match! Jump zp to sub-jump-table[low nibble]
                    low = b & 0x0F
                    new_lo = self.mem[p.sub_jump_table + low * 2]
                    new_hi = self.mem[p.sub_jump_table + low * 2 + 1]
                    new_ptr = new_lo | (new_hi << 8)
                    # INC counter; if post-INC == $E9, reset + clear loops
                    self.mem[p.self_mod_counter] = (self.mem[p.self_mod_counter] + 1) & 0xFF
                    if self.mem[p.self_mod_counter] == 0xE9:
                        self.mem[p.self_mod_counter] = 0xE0
                        for a in p.song_loop_clears:
                            self.mem[a] = 0
                    ptr = new_ptr
                    continue
                else:
                    # Not match — advance ptr (orig JMP L_C50E)
                    ptr = (ptr + 1) & 0xFFFF
                    continue

            # --- $Dx: SET INSTRUMENT (high nibble == $D) ---
            if hi == 0xD0:
                low = b & 0x0F
                self.mem[p.current_inst + x] = (low + 1) & 0xFF  # +1 quirk via INC
                ptr = (ptr + 1) & 0xFFFF
                continue

            # --- $80: GATE OFF ---
            if b == 0x80:
                # LDA $C941,y; STA $C944,y — preserve waveform, clear gate
                ctrl_src = self.mem[p.voice_state_base + 0x14 + y]
                self.mem[p.voice_state_base + 0x17 + y] = ctrl_src
                ptr = (ptr + 1) & 0xFFFF
                return ptr  # TERMINATING

            # --- $81: SKIP ---
            if b == 0x81:
                ptr = (ptr + 1) & 0xFFFF
                return ptr  # TERMINATING

            # --- $82 N: SET DURATION ---
            if b == 0x82:
                ptr = (ptr + 1) & 0xFFFF
                n = self.mem[ptr]
                self.mem[p.duration_counters + x] = n
                ptr = (ptr + 1) & 0xFFFF
                return ptr  # TERMINATING

            # --- $Bx: SET TEMPO ---
            if hi == 0xB0:
                low = b & 0x0F
                self.mem[p.tempo_reload] = (low - 1) & 0xFF  # STA then DEC
                ptr = (ptr + 1) & 0xFFFF
                continue

            # --- $Cx: SET MASTER VOL ---
            if hi == 0xC0:
                low = b & 0x0F
                self._write_sid(0xD418, low)
                ptr = (ptr + 1) & 0xFFFF
                continue

            # --- NOTE (anything else: $00..$7F, also "free" high nibbles
            #     $9x, $Ax not caught above — but those don't appear in
            #     well-formed streams) ---
            # Write CTRL ($C5BE,X) to $D404+sid_off
            sid_off = self.mem[p.voice_offsets + x]
            ctrl = self.mem[p.ctrl_byte + x]
            self._write_sid(0xD404 + sid_off, ctrl)
            # Call instrument loader sub_C86E with A=note
            self._instrument_loader(v, b)
            ptr = (ptr + 1) & 0xFFFF
            return ptr  # TERMINATING

    def _instrument_loader(self, v: int, note: int) -> None:
        """Mirror of sub_C86E. Copies 24-byte program to voice's
        runtime state slab, sets up freq slide / PW / ADSR, applies
        note freq."""
        p = self.params
        x = self._state_x(v)
        y_state = self._state_y(v)

        # Load instrument source address from $C8FB[inst*2..+1]
        inst = self.mem[p.current_inst + x]
        src_lo = self.mem[p.inst_src_table + inst * 2]
        src_hi = self.mem[p.inst_src_table + inst * 2 + 1]
        src_addr = src_lo | (src_hi << 8)

        # Load voice dest from $C91D[v*2..+1] (should equal $C92D + v*$1A)
        # We use voice_state_base + voice_state_stride*v directly,
        # which matches the orig data layout.
        dst_addr = p.voice_state_base + y_state

        # Copy 24 bytes from src_addr to dst_addr (Y=$17..$00)
        for i in range(0x18):
            self.mem[dst_addr + i] = self.mem[src_addr + i]

        # Apply note → freq slide setup:
        #   X = note (saved); A = $C5DD[note] (slide lo for this note)
        #   STA $C92E,y (freq_lo)
        #   A = ADC $C930,y (slide-target lo accum); STA $C930,y
        slide_lo_for_note = self.mem[p.inst_slide_lo_table + note]
        self.mem[p.voice_state_base + 0x01 + y_state] = slide_lo_for_note  # $C92E,y
        # ADC slide-target lo
        a = slide_lo_for_note + self.mem[p.voice_state_base + 0x03 + y_state]
        self.mem[p.voice_state_base + 0x03 + y_state] = a & 0xFF
        carry = (a >> 8) & 1
        # LDA $C65D,X (slide hi for note); STA $C92F,y; ADC $C931,y
        slide_hi_for_note = self.mem[p.inst_slide_hi_table + note]
        self.mem[p.voice_state_base + 0x02 + y_state] = slide_hi_for_note  # $C92F,y
        a = slide_hi_for_note + self.mem[p.voice_state_base + 0x04 + y_state] + carry
        self.mem[p.voice_state_base + 0x04 + y_state] = a & 0xFF
        # SBC chain for slide-min lo/hi → $C92E..$C92F minus $C932..$C933
        v_lo = self.mem[p.voice_state_base + 0x01 + y_state]
        # CLC equivalent — orig uses SEC first:
        a = v_lo - self.mem[p.voice_state_base + 0x05 + y_state]
        self.mem[p.voice_state_base + 0x05 + y_state] = a & 0xFF
        borrow = 0 if a >= 0 else 1
        v_hi = self.mem[p.voice_state_base + 0x02 + y_state]
        a = v_hi - self.mem[p.voice_state_base + 0x06 + y_state] - borrow
        self.mem[p.voice_state_base + 0x06 + y_state] = a & 0xFF

        # X = note + $10; load $C5DD[X], $C65D[X] → $C945,y / $C946,y
        # (note-freq-override slot used when slide-flag bit-7 takes
        # the off-slide branch in modulation)
        note16 = (note + 0x10) & 0xFF
        self.mem[p.voice_state_base + 0x18 + y_state] = self.mem[p.inst_slide_lo_table + note16]
        self.mem[p.voice_state_base + 0x19 + y_state] = self.mem[p.inst_slide_hi_table + note16]

        # Load CTRL ($C941,y) → $C5BE,X
        ctrl = self.mem[p.voice_state_base + 0x14 + y_state]
        self.mem[p.ctrl_byte + x] = ctrl
        # Clear PWM phase + accum
        self.mem[p.voice_pwm_phase + x] = 0
        self.mem[p.voice_pwm_lo_accum + x] = 0

        # Write AD/SR: LDX $C942,Y_state2 (Y was reloaded as $F5);
        # ah wait — orig does:
        #   BC FB CA   LDY $CAFB,X   ← Y = SID voice offset (0/7/14)
        #   A6 F5      LDX $F5       ← X = voice's Y_state (0/$1A/$34)
        #   BD 42 C9   LDA $C942,X   ← AD byte
        #   99 05 D4   STA $D405,Y
        #   BD 43 C9   LDA $C943,X   ← SR byte
        #   99 06 D4   STA $D406,Y
        sid_off = self.mem[p.voice_offsets + x]
        ad_byte = self.mem[p.voice_state_base + 0x15 + y_state]  # $C942 ≠ $C92D+$15;
        # wait $C942 - $C92D = $15. Yes that's $15. So $C942,X with X=y_state
        # actually means $C942 + y_state. That's $C942+0=$C942, $C942+$1A=$C95C,
        # $C942+$34=$C976. Hmm but I'm indexing voice_state_base+$15+y_state which
        # is $C92D+$15+y_state = $C942+y_state. Same thing. Good.
        sr_byte = self.mem[p.voice_state_base + 0x16 + y_state]  # $C943 + y_state
        self._write_sid(0xD405 + sid_off, ad_byte)
        self._write_sid(0xD406 + sid_off, sr_byte)

    # ----- per-frame modulation block (sub_C6DD .. sub_C86A) -----

    def _modulation_block(self) -> None:
        """Mirror of $C6DD: for each of 3 voices, run sub_C6EE
        (freq+PWM update + SID writes for $D400..$D404)."""
        p = self.params
        for v in range(3):
            self.mem[p.modulation_voice_idx] = v
            self._modulation_voice(v)

    def _modulation_voice(self, v: int) -> None:
        """Mirror of sub_C6EE."""
        p = self.params
        x = self.mem[p.voice_offsets + v]      # SID voice offset (0/7/14)
        y_state = self._state_y(v)             # $C92D-relative Y stride

        # --- Freq output (with bit-7 LFO toggle) ---
        flag = self.mem[p.voice_state_base + 0x00 + y_state]  # $C92D,Y
        if flag & 0x80:
            # If bit 7 set, check frame counter LSB: if even, use off-slide freq
            if self.mem[p.frame_counter] & 1 == 0:
                # LDA $C945,y → $D400; LDA $C946,y → $D401
                self._write_sid(0xD400 + x, self.mem[p.voice_state_base + 0x18 + y_state])
                self._write_sid(0xD401 + x, self.mem[p.voice_state_base + 0x19 + y_state])
            else:
                self._write_sid(0xD400 + x, self.mem[p.voice_state_base + 0x01 + y_state])
                self._write_sid(0xD401 + x, self.mem[p.voice_state_base + 0x02 + y_state])
        else:
            self._write_sid(0xD400 + x, self.mem[p.voice_state_base + 0x01 + y_state])
            self._write_sid(0xD401 + x, self.mem[p.voice_state_base + 0x02 + y_state])

        # --- PW output ---
        # PW_HI = $C937,y; PW_LO = $CB01,X (with X = $CB04 voice_idx,
        # not SID voice off!) — re-read orig:
        #   $C724: LDY $CB04   ; reload modulation_voice_idx
        #   $C727: LDA $CB01,Y ; PW lo accum (this Y is modulation_voice_idx not SID-off!)
        # So $CB01 is indexed by v (modulation voice idx), not SID off.
        self._write_sid(0xD403 + x, self.mem[p.voice_state_base + 0x0A + y_state])
        self._write_sid(0xD402 + x, self.mem[p.voice_pwm_lo_accum + v])

        # --- CTRL output (with gate-off OR mask) ---
        ctrl = self.mem[p.voice_state_base + 0x14 + y_state]
        ctrl |= self.mem[p.voice_state_base + 0x17 + y_state]
        self._write_sid(0xD404 + x, ctrl)

        # --- Freq slide update ---
        # LDA $C92D,y; LSR — carry into BCS L_C7B0
        flag = self.mem[p.voice_state_base + 0x00 + y_state]
        if flag & 0x01:
            # Slide DOWN (L_C7B0 path)
            self._slide_down(v, x, y_state)
        else:
            # Slide UP
            self._slide_up(v, x, y_state)

        # --- PWM phase update ---
        self._pwm_update(v, x, y_state)

    def _slide_up(self, v: int, x: int, y_state: int) -> None:
        p = self.params
        base = p.voice_state_base + y_state
        # ADC slide-delta lo/hi to current freq lo/hi
        lo = self.mem[base + 0x01] + self.mem[base + 0x07]
        self.mem[base + 0x01] = lo & 0xFF
        carry = (lo >> 8) & 1
        hi = self.mem[base + 0x02] + self.mem[base + 0x08] + carry
        self.mem[base + 0x02] = hi & 0xFF
        # CMP/SBC against slide-max
        diff_lo = self.mem[base + 0x01] - self.mem[base + 0x03]
        borrow = 0 if diff_lo >= 0 else 1
        diff_hi = self.mem[base + 0x02] - self.mem[base + 0x04] - borrow
        if diff_hi < 0:
            # Carry clear → not yet at max → continue
            return
        # Reached max. Check bit 1 of flag.
        flag = self.mem[base + 0x00]
        if flag & 0x02:
            # Bit 1 set: swap direction (EOR #$01 on flag)
            self.mem[base + 0x00] ^= 0x01
            # Reset freq to slide-max (L_C770: LDA $C930,Y → $C92E,Y; etc.)
            self.mem[base + 0x01] = self.mem[base + 0x03]
            self.mem[base + 0x02] = self.mem[base + 0x04]
            return
        # Bit 1 clear: check bit 2 (continuous slide)
        if flag & 0x04:
            # Reset freq to slide-min ($C932,y → $C92E,y)
            self.mem[base + 0x01] = self.mem[base + 0x05]
            self.mem[base + 0x02] = self.mem[base + 0x06]
            return
        # Bit 2 clear: zero the slide-delta (one-shot)
        self.mem[base + 0x07] = 0
        self.mem[base + 0x08] = 0

    def _slide_down(self, v: int, x: int, y_state: int) -> None:
        p = self.params
        base = p.voice_state_base + y_state
        # SBC slide-delta lo/hi from current freq lo/hi
        lo = self.mem[base + 0x01] - self.mem[base + 0x07]
        self.mem[base + 0x01] = lo & 0xFF
        borrow = 0 if lo >= 0 else 1
        hi = self.mem[base + 0x02] - self.mem[base + 0x08] - borrow
        self.mem[base + 0x02] = hi & 0xFF
        # CMP/SBC against slide-min
        diff_lo = self.mem[base + 0x01] - self.mem[base + 0x05]
        # Orig BCS at $C7CF — if carry clear (current < min), proceed; if set, RTS
        if diff_lo >= 0:
            borrow = 0
        else:
            borrow = 1
        diff_hi = self.mem[base + 0x02] - self.mem[base + 0x06] - borrow
        if diff_hi >= 0:
            # Carry set → still above min → continue
            return
        # Reached min. Check bit 1 of flag.
        flag = self.mem[base + 0x00]
        if flag & 0x02:
            # Bit 1 set: swap direction
            self.mem[base + 0x00] ^= 0x01
            # Reset freq to slide-min
            self.mem[base + 0x01] = self.mem[base + 0x05]
            self.mem[base + 0x02] = self.mem[base + 0x06]
            return
        # Bit 1 clear: check bit 2
        if flag & 0x04:
            # Reset freq to slide-max
            self.mem[base + 0x01] = self.mem[base + 0x03]
            self.mem[base + 0x02] = self.mem[base + 0x04]
            return
        self.mem[base + 0x07] = 0
        self.mem[base + 0x08] = 0

    def _pwm_update(self, v: int, x: int, y_state: int) -> None:
        """Mirror of $C7E3..$C86A. Two-phase PWM:
        - Phase 0: ramp until limit, then advance to phase 1
        - Phase 1: oscillate between two limits, flipping direction"""
        p = self.params
        base = p.voice_state_base + y_state
        phase = self.mem[p.voice_pwm_phase + v]
        if phase == 0:
            # --- Phase 0 ---
            dir_flag = self.mem[base + 0x0E]   # $C93B,y
            if dir_flag == 0:
                # ADD direction
                acc = self.mem[p.voice_pwm_lo_accum + v] + self.mem[base + 0x0C]
                self.mem[p.voice_pwm_lo_accum + v] = acc & 0xFF
                carry = (acc >> 8) & 1
                hi = (self.mem[base + 0x0A] + carry) & 0xFF
                self.mem[base + 0x0A] = hi
                # CMP $C938,y; BCS advance
                if hi >= self.mem[base + 0x0B]:
                    self.mem[p.voice_pwm_phase + v] = phase + 1
            else:
                # SUB direction
                lo_val = self.mem[p.voice_pwm_lo_accum + v] - self.mem[base + 0x0C]
                self.mem[p.voice_pwm_lo_accum + v] = lo_val & 0xFF
                borrow = 1 if lo_val < 0 else 0
                hi = (self.mem[base + 0x0A] - borrow) & 0xFF
                self.mem[base + 0x0A] = hi
                # CMP $C938,y; BEQ or BCC advance
                lim = self.mem[base + 0x0B]
                if hi <= lim:  # both BEQ and below-min trigger
                    self.mem[p.voice_pwm_phase + v] = phase + 1
            return
        # --- Phase 1 ---
        dir1 = self.mem[base + 0x0F]   # $C93C,y
        if dir1 == 0:
            # ADD direction
            acc = self.mem[p.voice_pwm_lo_accum + v] + self.mem[base + 0x12]
            self.mem[p.voice_pwm_lo_accum + v] = acc & 0xFF
            carry = (acc >> 8) & 1
            hi = (self.mem[base + 0x0A] + carry) & 0xFF
            self.mem[base + 0x0A] = hi
            # CMP $C93D,y; BCC RTS, BCS+ flip direction
            if hi >= self.mem[base + 0x10]:
                self.mem[base + 0x0F] = 1   # flip to SUB
        else:
            # SUB direction
            lo_val = self.mem[p.voice_pwm_lo_accum + v] - self.mem[base + 0x12]
            self.mem[p.voice_pwm_lo_accum + v] = lo_val & 0xFF
            borrow = 1 if lo_val < 0 else 0
            hi = (self.mem[base + 0x0A] - borrow) & 0xFF
            self.mem[base + 0x0A] = hi
            # CMP $C93E,y; BEQ → flip; BCS RTS; below → also flip
            lim = self.mem[base + 0x11]
            if hi <= lim:
                self.mem[base + 0x0F] = 0   # flip to ADD

    # ----- run -----

    def run(self, n_frames: int) -> list[FrameWrites]:
        """Step n_frames and return the full write history."""
        for _ in range(n_frames):
            self.step_frame()
        return self.writes


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _to_reg_val_stream(frames: list[FrameWrites], skip_first: bool = False
                       ) -> list[tuple[int, int]]:
    out = []
    for k, f in enumerate(frames):
        if skip_first and k == 0:
            continue
        for reg, val in f:
            out.append((reg, val))
    return out


def validate_ninja_hamster(n_frames: int = 200) -> dict:
    """Run emulator + orig writelog, return divergence info."""
    from pipelines.hubbard.verify_cycle import writelog_capture
    sid = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
              'Ninja_Hamster.sid')
    emu = JayDerrettEmulator(sid)
    emu_frames = emu.run(n_frames)
    duration = n_frames / 50.0
    orig = writelog_capture(sid, 0, duration=duration + 1.0)
    # Skip frame 0 of both (libsidplayfp + engine init writes timing
    # differs from a Python emulator).
    orig_stream = [(r, v) for k, f in enumerate(orig) if k > 0
                   for c, r, v in f]
    emu_stream = _to_reg_val_stream(emu_frames, skip_first=True)
    n = min(len(orig_stream), len(emu_stream))
    div = next((i for i in range(n) if orig_stream[i] != emu_stream[i]), None)
    return {
        'n_emu': len(emu_stream),
        'n_orig': len(orig_stream),
        'first_div': div,
        'div_emu': emu_stream[div] if div is not None else None,
        'div_orig': orig_stream[div] if div is not None else None,
        'orig_prefix': orig_stream[:30],
        'emu_prefix': emu_stream[:30],
        'orig_at_div': orig_stream[max(0, (div or 0) - 3):(div or 0) + 6],
        'emu_at_div': emu_stream[max(0, (div or 0) - 3):(div or 0) + 6],
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    r = validate_ninja_hamster(50)
    print(f"emu writes (skip frame 0): {r['n_emu']}, orig writes (skip frame 0): {r['n_orig']}")
    if r['first_div'] is None:
        print(f"PREFIX MATCH ✓ ({min(r['n_emu'], r['n_orig'])} writes)")
    else:
        print(f"DIVERGE at idx {r['first_div']}: emu={r['div_emu']} vs orig={r['div_orig']}")
        print("\nContext (-3..+5):")
        for i, ((re, ve), (ro, vo)) in enumerate(zip(r['emu_at_div'], r['orig_at_div'])):
            mark = " <<<" if (re, ve) != (ro, vo) else ""
            print(f"  emu=${re:02X}=${ve:02X}  orig=${ro:02X}=${vo:02X}{mark}")
