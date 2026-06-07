"""FC data-section emitters — patterns + sequences + pointer tables, all
from USF content (not verbatim from the orig binary).

This is the principled core of the FC composer's data tail: it turns the
engine-neutral USF (`Orderlist` + `Pattern`/`NoteRow`) back into the FC
byte streams the engine walks, choosing its own dense layout. Per the
CORE TENET the emitted bytes need only reproduce the SID write stream,
not orig's exact byte layout — but where the USF preserved enough, the
encoder reproduces orig's bytes too (the tightest correctness check).

Byte encodings (verified against the engine dispatch in composer_asm.py
and the decoder in engine_model._parse_pattern):

Pattern stream (per note, in dispatch order):
  $F1 v   filter set            (NoteRow fx_flag 'filter=$XX')
  $E0 d p glide (3 bytes)       (fx_flag 'glide=d'; p is the note pitch;
                                 bypasses wave/length/instr for that note)
  $C0|w   wave/inst adjust      (fx_flag 'wave_adjust=w', 0-31)
  $80|(L+1) set note length     (NoteRow.duration; emitted when it changes;
                                 chained $80|n extends for L > 62)
  $70|i   instr / arp select    (NoteRow.instr; i = instr.id-1, 0-15)
  $00-$6F note pitch            (base pitch, transpose applied by the seq)
  $FF     end of pattern

Sequence stream (our own wider partition — the composer emits these bytes
and its own walker reads them, so we are not bound to FC's 64-pattern
$00-$3F limit; see composer_asm h3_command_dispatch):
  $00-$7F pattern jump (= pool slot id, 128 patterns)
  $80|t   transpose (t = transpose & $1F)
  $A0|r   repeat (play count-1; r = plays-1, 0-31 per command)
  $C0|v   voiceinc  (v = voiceinc & $0F)
  $FE     end (stop) / $FF wrap (loop)
"""
from __future__ import annotations

from src.usf.types import VoiceBlock, Orderlist, Pattern, NoteRow, Pitch


_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
_NAME_TO_IDX = {n: i for i, n in enumerate(_NOTE_NAMES)}


def byte_from_pitch(p: Pitch) -> int:
    """`Pitch` → FC pitch byte (inverse of to_usf._pitch_from_byte for the
    0..95 musical range)."""
    return p.octave * 12 + _NAME_TO_IDX[p.name]


def _fx(flags: tuple, prefix: str):
    """Return the int value of the first `prefix=...` fx flag, or None.
    `filter=$XX` is hex; the rest are decimal."""
    for f in flags:
        if f.startswith(prefix):
            v = f.split('=', 1)[1]
            return int(v[1:], 16) if v.startswith('$') else int(v)
    return None


def encode_pattern(rows: list[NoteRow]) -> bytes:
    """Encode a USF pattern body (list of NoteRow) into an FC pattern byte
    stream terminated by $FF."""
    out = bytearray()
    prev_dur = None
    for row in rows:
        filt = _fx(row.fx_flags, 'filter=')
        if filt is not None:
            out += bytes((0xF1, filt & 0xFF))

        wave = _fx(row.fx_flags, 'wave_adjust=')
        if wave is not None:
            out.append(0xC0 | (wave & 0x1F))

        glide = _fx(row.fx_flags, 'glide=')
        if glide is not None:
            # Glide note: the target byte IS the note (3-byte $E0,d,p) and
            # the glide handler jumps straight to note-play, bypassing the
            # instr/arp step — so a glide note carries no instr. The engine
            # reaches the glide handler only via the `skip` re-dispatch, so
            # a length byte ($80-chain, which routes setlen_loop -> skip on
            # the following $Ex) must precede it. Emit the length
            # unconditionally here (idempotent re-set of nootleng) so the
            # routing holds even when wave is present / duration unchanged.
            out += _encode_length(row.duration)
            prev_dur = row.duration
            out += bytes((0xE0, glide & 0xFF, byte_from_pitch(row.pitch)))
            continue

        if row.duration != prev_dur:
            out += _encode_length(row.duration)
            prev_dur = row.duration

        if row.instr is not None:
            out.append(0x70 | ((row.instr.id - 1) & 0x0F))

        out.append(byte_from_pitch(row.pitch))
    out.append(0xFF)
    return bytes(out)


def _row_key(r: NoteRow):
    """Content key for pattern dedup (engine-neutral)."""
    return (r.pitch.name, r.pitch.octave, r.duration,
            r.instr.id if r.instr else None, tuple(sorted(r.fx_flags)))


def build_pattern_pool(music_subtunes: list):
    """Collect every voice's patterns into a global dense pool, deduped by
    content. Returns (slot_streams, localmaps):

      slot_streams[slot] — encoded FC pattern bytes for global slot `slot`
      localmaps[(sub.id, voice.id)][local_pat_id] — global slot for that
        voice's local USF pattern id
    """
    slot_streams: list[bytes] = []
    key_to_slot: dict[tuple, int] = {}
    localmaps: dict[tuple, dict[int, int]] = {}
    for sub in music_subtunes:
        for v in sub.voices:
            lm: dict[int, int] = {}
            for pat in v.patterns:
                key = tuple(_row_key(r) for r in pat.rows)
                slot = key_to_slot.get(key)
                if slot is None:
                    slot = len(slot_streams)
                    key_to_slot[key] = slot
                    slot_streams.append(encode_pattern(pat.rows))
                lm[pat.id] = slot
            localmaps[(sub.id, v.id)] = lm
    return slot_streams, localmaps


def encode_sequence(orderlist: Orderlist, localmap: dict[int, int]) -> bytes:
    """Encode one voice's orderlist into an FC sequence byte stream.

    Transpose/voiceinc are delta-encoded (emitted only when they change,
    since the engine's toneadd/voiceinc state persists); repeats become a
    $40|r command (r = plays-1). The stream ends in $FE (stop) or $FF
    (wrap to start).

    The first entry ALWAYS emits both modifiers (cur_t/cur_v start at a
    sentinel): toneadd/voiceinc persist across the $FF wrap, so the
    sequence must re-establish its start state on every loop — otherwise
    a value set near the end of one loop leaks (invisibly, since these
    commands emit no SID write) into the next loop's early patterns."""
    out = bytearray()
    cur_t = -1
    cur_v = -1
    for i, pid in enumerate(orderlist.entries):
        t = orderlist.transpose_at(i)
        v = orderlist.voiceinc_at(i)
        rep = orderlist.repeat_at(i)
        if t != cur_t:
            out.append(0x80 | (t & 0x1F))      # $80-$9F transpose
            cur_t = t
        if v != cur_v:
            out.append(0xC0 | (v & 0x0F))      # $C0-$CF voiceinc
            cur_v = v
        if rep > 1:
            r = rep - 1
            if r > 0x1F:
                raise ValueError(f'repeat count {rep} exceeds single $A0 '
                                 f'command (max 32 plays); chaining TODO')
            out.append(0xA0 | r)               # $A0-$BF repeat
        slot = localmap[pid]
        if slot > 0x7F:
            raise ValueError(f'pattern slot {slot} exceeds 127 (1-byte '
                             f'jump $00-$7F); needs 16-bit pattern index')
        out.append(slot)                       # $00-$7F pattern jump
    out.append(0xFE if orderlist.stop else 0xFF)
    return bytes(out)


def build_music_data(music_subtunes: list, music_base: int) -> dict:
    """Lay out the full FC music data block (seq_table + pattern_ptr_table +
    pattern streams + sequence streams) starting at `music_base`.

    Returns a dict with the assembled `block` bytes and the resolved
    `seq_table_addr` / `pattern_ptr_addr` (which the engine code's song-init
    + pattern_ptr_table equate point at) and `n_slots`.

    Layout (all pointers absolute, so streams can live anywhere):
      seq_table          6 bytes/subtune: [v1lo,v2lo,v3lo, v1hi,v2hi,v3hi]
      pattern_ptr_table 2 bytes/slot: lo,hi of the slot's pattern stream
      pattern streams   concatenated, one per global slot
      sequence streams  concatenated, one per (subtune, voice)
    """
    slot_streams, localmaps = build_pattern_pool(music_subtunes)
    n_slots = len(slot_streams)
    n_sub = max((s.id for s in music_subtunes), default=0)   # 1-based ids

    # Encode each voice's sequence (keyed by engine subtune index + voice).
    seqs: dict[tuple, bytes] = {}
    for sub in music_subtunes:
        for v in sub.voices:
            seqs[(sub.id - 1, v.id - 1)] = encode_sequence(
                v.orderlist, localmaps[(sub.id, v.id)])

    seq_table_addr = music_base
    seq_table_size = 6 * n_sub
    pattern_ptr_addr = seq_table_addr + seq_table_size
    pattern_ptr_size = 2 * n_slots

    cur = pattern_ptr_addr + pattern_ptr_size
    slot_addr: list[int] = []
    pat_bytes = bytearray()
    for st in slot_streams:
        slot_addr.append(cur)
        pat_bytes += st
        cur += len(st)

    seq_addr: dict[tuple, int] = {}
    seq_bytes = bytearray()
    for key in sorted(seqs):
        seq_addr[key] = cur
        seq_bytes += seqs[key]
        cur += len(seqs[key])

    pattern_ptr = bytearray()
    for a in slot_addr:
        pattern_ptr += bytes((a & 0xFF, (a >> 8) & 0xFF))

    seq_table = bytearray()
    for si in range(n_sub):
        los = [seq_addr[(si, vi)] & 0xFF for vi in range(3)]
        his = [(seq_addr[(si, vi)] >> 8) & 0xFF for vi in range(3)]
        seq_table += bytes(los + his)

    block = bytes(seq_table) + bytes(pattern_ptr) + bytes(pat_bytes) + \
        bytes(seq_bytes)
    return {
        'block': block,
        'base': music_base,
        'seq_table_addr': seq_table_addr,
        'pattern_ptr_addr': pattern_ptr_addr,
        'n_slots': n_slots,
        'size': len(block),
    }


def _encode_length(dur: int) -> bytes:
    """Encode note length `dur` (frames) as $80-chain bytes.

    Decoder: first byte sets nootleng = (b & $3F) - 1; each chained
    $80-$BF adds (b & $3F). So the first byte carries dur+1 (clamped to
    $3F) and overflow spills into extension bytes.
    """
    first = dur + 1
    if first <= 0x3F:
        return bytes((0x80 | first,))
    # Chain: first byte maxes at $3F (nootleng = 62), rest add.
    out = bytearray((0x80 | 0x3F,))
    rem = dur - 0x3E
    while rem > 0:
        step = min(rem, 0x3F)
        out.append(0x80 | step)
        rem -= step
    return bytes(out)
