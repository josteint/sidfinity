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
  $B0+r   repeat (offset-coded, r = plays-1, 0-63)
  $A0|v   voiceinc  (v = voiceinc & $0F)
  $FE     end (stop) / $FF wrap (loop)
"""
from __future__ import annotations

import dataclasses

from src.usf.resolve import needs_resolution, resolve_voice
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


def encode_pattern(rows: list[NoteRow], instr_as_wavecount: bool = False,
                   omit_first_len: bool = False) -> bytes:
    """Encode a USF pattern body (list of NoteRow) into an FC pattern byte
    stream terminated by $FF.

    `instr_as_wavecount` (standard FC player): emit a NoteRow's instrument as
    a $C0|n wavecount-set command (the composer's instrument mechanism) instead
    of the default $70|n arp-program select. The standard player selects its
    instrument via the pattern's $Cx byte, which maps onto the composer's
    wavecount path; the Tel default routes instrument through $7x. (The two
    composer-parser ranges are distinct: $C0-$DF sets wavecount, $70-$7F selects
    an arp program — so the standard instrument MUST ride the $Cx path.)"""
    out = bytearray()
    # omit_first_len (`loop@N len=L`): seed prev_dur with the first row's
    # duration so no $8x is emitted for it — the engine's persisting
    # nootleng then supplies the duration (pass 1: the start state;
    # passes 2+: the carried end-of-list length), exactly the orig's
    # length-inherited loop head.
    prev_dur = rows[0].duration if (omit_first_len and rows) else None
    for row in rows:
        if 'noretrig' in row.fx_flags and instr_as_wavecount:
            # STANDARD tie (orig $18DD/$18F4 -> $1957): the byte AFTER
            # the $Fx prefix IS the note — no re-dispatch — so instr/
            # length must ride BEFORE the prefix: [instr?][len][$F0]
            # [note]. Same emission-order class as the glide rule
            # below. The note byte may be >= $80 (ghost-march ties,
            # Baster_Blaster $C1) — emitting it after the prefix is the
            # only way such a byte can be a note at all.
            if row.instr is not None:
                out.append(0xC0 | ((row.instr.id - 1) & 0x1F))
            if row.duration != prev_dur:
                out += _encode_length(row.duration)
                prev_dur = row.duration
            out += bytes((0xF0, byte_from_pitch(row.pitch)))
            continue
        # $F0 (no-retrigger / legato) goes FIRST (Tel): it sets the
        # engine's newnote flag (skip ADSR/wave reload) then
        # re-dispatches the rest of the note's chain via `skip`, so any
        # wave/length/note that follows still applies.
        if 'noretrig' in row.fx_flags:
            out.append(0xF0)

        filt = _fx(row.fx_flags, 'filter=')
        if filt is not None:
            out += bytes((0xF1, filt & 0xFF))

        wave = _fx(row.fx_flags, 'wave_adjust=')
        if wave is not None:
            out.append(0xC0 | (wave & 0x1F))

        if instr_as_wavecount:
            # standard FC directional portamento: [$Ex][param][note].
            # cmd bit0 = down, bits1-3 = speed hi; param hi nibble =
            # speed lo, lo nibble = onset threshold (elapsed ticks).
            g_up = _fx(row.fx_flags, 'glide_up=')
            g_down = _fx(row.fx_flags, 'glide_down=')
            if g_up is not None or g_down is not None:
                speed = g_down if g_down is not None else g_up
                onset = _fx(row.fx_flags, 'glide_onset=') or 0
                # ORDER MATTERS: [instr][len][$Ex...] — after a $Cx the
                # parser checks only $8x-or-note (orig structure), so an
                # $Ex straight after an instrument would be misread as a
                # length. A length byte re-dispatches fully, so the $Ex
                # must ride behind one — emitted unconditionally
                # (idempotent nootleng re-set, no SID writes).
                if row.instr is not None:
                    out.append(0xC0 | ((row.instr.id - 1) & 0x1F))
                out += _encode_length(row.duration)
                prev_dur = row.duration
                cmd = (0xE0 | (1 if g_down is not None else 0)
                       | (((speed >> 8) & 0x07) << 1))
                out += bytes((cmd, (speed & 0xF0) | (onset & 0x0F),
                              byte_from_pitch(row.pitch)))
                continue

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
            if instr_as_wavecount:
                out.append(0xC0 | ((row.instr.id - 1) & 0x1F))
            else:
                out.append(0x70 | ((row.instr.id - 1) & 0x0F))

        pb = byte_from_pitch(row.pitch)
        if instr_as_wavecount and pb >= 0x80 and row.instr is None:
            # A ghost pitch (>= $80, off-table read) is only a NOTE byte
            # in the tie / after-$Cx / post-glide-param positions — bare,
            # it would dispatch as a command. The tie/glide branches
            # handle theirs above; an instr carrier covers the rest. If
            # this fires, to_usf needs to stamp the resolved instrument
            # on ghost rows (fail loudly rather than corrupt the stream).
            raise ValueError(
                f'ghost pitch {pb:#04x} on a bare row (no instr/tie/'
                f'glide carrier) — unencodable as a note byte')
        out.append(pb)
    out.append(0xFF)
    return bytes(out)


def _row_key(r: NoteRow):
    """Content key for pattern dedup (engine-neutral)."""
    return (r.pitch.name, r.pitch.octave, r.duration,
            r.instr.id if r.instr else None, tuple(sorted(r.fx_flags)))


def build_pattern_pool(music_subtunes: list, instr_as_wavecount: bool = False):
    """Collect every voice's patterns into a global dense pool, deduped by
    content. Returns (slot_streams, localmaps, entrymaps):

      slot_streams[slot] — encoded FC pattern bytes for global slot `slot`
      localmaps[(sub.id, voice.id)][local_pat_id] — global slot for that
        voice's local USF pattern id (legacy fully-stated voices)
      entrymaps[(sub.id, voice.id)] — per-ORDERLIST-ENTRY global slots for
        stated-inherited voices (one USF pattern can materialize
        differently per entry context), or None for legacy voices

    STATED-inherited voices (any row without a duration — D6 piece 2) run
    the shared resolution interpreter (src/usf/resolve.py) and emit each
    entry's MATERIALIZED effective rows — dedup by encoded content
    collapses the (overwhelmingly common) identical materializations. The
    loop-head `omit_first_len` (the engine's persisting nootleng carrying
    the wrap) is DERIVED: the head's first row states no duration and its
    pass-2 resolution differs from pass 1 — replacing the old extract-
    annotated `loop@N len=L`, and extending it to deep inheritance chains
    (the old row-0-only fold's reject class).
    """
    slot_streams: list[bytes] = []
    key_to_slot: dict[tuple, int] = {}
    localmaps: dict[tuple, dict[int, int]] = {}
    entrymaps: dict[tuple, list | None] = {}
    for sub in music_subtunes:
        init_by_id = {iv.id: iv for iv in
                      (sub.init.voices if sub.init else [])}
        for v in sub.voices:
            ol = v.orderlist

            def _intern(rows, omit):
                key = (tuple(_row_key(r) for r in rows), omit)
                slot = key_to_slot.get(key)
                if slot is None:
                    slot = len(slot_streams)
                    key_to_slot[key] = slot
                    slot_streams.append(encode_pattern(
                        rows, instr_as_wavecount=instr_as_wavecount,
                        omit_first_len=omit))
                return slot

            if needs_resolution(v):
                passes = resolve_voice(v, init_by_id.get(v.id),
                                       n_passes=2)
                pass1 = passes[0]
                pat_by_id = {p.id: p for p in v.patterns}
                # loop-head runtime inheritance: head first row inherited
                # AND the carried wrap value actually differs from pass 1
                omit_head = False
                head_rows_m = None
                if (ol.loop_to is not None and len(passes) > 1
                        and passes[1] and pass1):
                    h1 = pass1[ol.loop_to]
                    h2 = passes[1][0]
                    head_src = pat_by_id[ol.entries[ol.loop_to]].rows
                    if (head_src and head_src[0].duration is None
                            and h1 and h2
                            and h2[0].duration != h1[0].duration):
                        omit_head = True
                        head_rows_m = [
                            dataclasses.replace(rr.row, duration=rr.duration)
                            for rr in h1]
                entry_slots = []
                for i, resolved in enumerate(pass1):
                    rows_m = [dataclasses.replace(rr.row,
                                                  duration=rr.duration)
                              for rr in resolved]
                    omit = (omit_head
                            and ol.entries[i] == ol.entries[ol.loop_to]
                            and rows_m == head_rows_m)
                    entry_slots.append(_intern(rows_m, omit))
                entrymaps[(sub.id, v.id)] = entry_slots
                localmaps[(sub.id, v.id)] = {}
                continue

            lm: dict[int, int] = {}
            omit_ids = set()
            if (getattr(ol, 'loop_length', None) is not None
                    and ol.loop_to is not None and ol.entries):
                omit_ids.add(ol.entries[ol.loop_to])
            for pat in v.patterns:
                lm[pat.id] = _intern(pat.rows, pat.id in omit_ids)
            localmaps[(sub.id, v.id)] = lm
            entrymaps[(sub.id, v.id)] = None
    return slot_streams, localmaps, entrymaps


def encode_sequence(orderlist: Orderlist, localmap: dict[int, int],
                    persist_modifiers: bool = False,
                    entry_slots: list | None = None) -> bytes:
    """Encode one voice's orderlist into an FC sequence byte stream.

    Transpose/voiceinc are delta-encoded (emitted only when they change,
    since the engine's toneadd/voiceinc state persists); repeats become a
    $40|r command (r = plays-1). The stream ends in $FE (stop) or $FF
    (wrap to start).

    Tel (`persist_modifiers=False`): the first entry ALWAYS emits both
    modifiers (cur_t/cur_v start at a sentinel) — the sequence
    re-establishes its start state on every loop, so a value set near the
    end of one loop can't leak into the next loop's early patterns.

    Standard (`persist_modifiers=True`): the engine's transpose state
    carries over the $FF wrap. When the USF's `loop_transpose` is set
    (the loop PICKS UP a carried value — `loop@N+T`), the encoder omits
    the head transpose byte so the engine's persistence reproduces the
    pass-2+ behavior (an inherited head always resolved to 0 on pass 1,
    so starting the delta at 0 emits nothing there). When None, the head
    byte is emitted explicitly — re-establish on every pass, like
    originals whose loop head carries an explicit $80."""
    out = bytearray()
    carried = (persist_modifiers
               and getattr(orderlist, 'loop_transpose', None) is not None)
    cur_t = 0 if carried else -1
    cur_v = 0 if persist_modifiers else -1
    for i, pid in enumerate(orderlist.entries):
        t = orderlist.transpose_at(i)
        v = orderlist.voiceinc_at(i)
        rep = orderlist.repeat_at(i)
        if t != cur_t:
            out.append(0x80 | (t & 0x1F))      # $80-$9F transpose
            cur_t = t
        if v != cur_v:
            out.append(0xA0 | (v & 0x0F))      # $A0-$AF voiceinc
            cur_v = v
        if rep > 1:
            r = rep - 1
            if r > 0x3F:
                raise ValueError(f'repeat count {rep} exceeds the $B0-$FD '
                                 f'command (max 64 plays); chaining TODO')
            out.append(0xB0 + r)               # $B0-$FD repeat (offset-coded)
        slot = entry_slots[i] if entry_slots is not None else localmap[pid]
        if slot > 0x7F:
            raise ValueError(f'pattern slot {slot} exceeds 127 (1-byte '
                             f'jump $00-$7F); needs 16-bit pattern index')
        out.append(slot)                       # $00-$7F pattern jump
    out.append(0xFE if orderlist.stop else 0xFF)
    return bytes(out)


def build_music_data(music_subtunes: list, music_base: int,
                     instr_as_wavecount: bool = False) -> dict:
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
    slot_streams, localmaps, entrymaps = build_pattern_pool(
        music_subtunes, instr_as_wavecount=instr_as_wavecount)
    n_slots = len(slot_streams)
    n_sub = max((s.id for s in music_subtunes), default=0)   # 1-based ids

    # Encode each voice's sequence (keyed by engine subtune index + voice).
    seqs: dict[tuple, bytes] = {}
    for sub in music_subtunes:
        for v in sub.voices:
            seqs[(sub.id - 1, v.id - 1)] = encode_sequence(
                v.orderlist, localmaps[(sub.id, v.id)],
                persist_modifiers=instr_as_wavecount,
                entry_slots=entrymaps.get((sub.id, v.id)))

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
    """Encode note length `dur` as $80-chain bytes.

    `dur` is the raw setlen total (engine: nootleng = dur - 1). One byte
    $80|dur carries it directly; values > $3F spill into chained $80-$BF
    bytes that the engine sums (dur = sum of all the (byte & $3F) values).
    """
    if dur <= 0x3F:
        return bytes((0x80 | dur,))
    out = bytearray()
    rem = dur
    while rem > 0:
        step = min(rem, 0x3F)
        out.append(0x80 | step)
        rem -= step
    return bytes(out)
