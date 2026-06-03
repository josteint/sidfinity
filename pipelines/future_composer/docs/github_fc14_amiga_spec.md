---
source_url: https://gist.github.com/RigoLigoRLC/7d2cb2235204c93e8d78228122eb0119
fetched_via: direct (curl raw)
fetch_date: 2026-06-03
author: RigoLigoRLC
content_date: gist (year unspecified, modern)
reliability: secondary  (Amiga FC1.4 — different from C64 MoN/FC, but structurally related)
---

# Future Composer 1.4 (Amiga) module format — verbatim spec

**IMPORTANT CAVEAT**: This is the **Amiga** Future Composer 1.4 by
Sonix / Supersero, **NOT** the C64 MoN/FutureComposer family that
Hawkeye uses. The two are completely unrelated codebases despite
sharing the name. **Do not use this directly for the C64 byte-exact
rebuild** — but the conceptual data hierarchy is similar enough to
hint at what we should look for in the C64 format.

## Why include this anyway?

1. It's one of the very few **complete** FC format specs published
   anywhere, written in ImHex pattern-language so it's unambiguous.
2. The Amiga and C64 FC implementations share the editor UX (32-step
   patterns, voice-transpose per pattern, separate frequency/volume
   sequences, instrument bank) — useful structural reference.
3. **Differences to watch for** when reverse-engineering the C64
   version: Amiga FC uses 4 voices (Paula chips), 8-bit sample
   playback, separate sample/waveform tables. C64 has 3 voices, no
   sample playback (typically), SID synthesis with pulse/filter
   modulation.

## Verbatim ImHex pattern (full)

```c
#include <std/core.pat>

struct fc_pattern_index_entry_channel {
    u8 pattern_id;
    u8 transpose;
    u8 sound_transpose;
};

struct fc_pattern_index_entry {
    fc_pattern_index_entry_channel channel[4];   // <-- 4 voices on Amiga
    u8 speed;
};

bitfield fc_note_info {
    instrument_id : 6;
    bool portamento_off : 1;
    bool portamento_on  : 1;
};

struct fc_note {
    u8 pitch;
    fc_note_info info;     // <-- 2 bytes per note (Amiga FC, NOT C64)
};

struct fc_pattern {
    fc_note notes[32];     // <-- 32 steps/pattern (matches C64 expectation)
};

struct fc_freq_seq {
    u8 freq[64];
};

struct fc_volume_seq {
    u8 volume[64];
};

struct fc_sample_metadata {
    be u16 sample_point_count;
    be u16 loop;
    be u16 loop_point_count;
    if (sample_point_count != 0) {
        be u16 sample_block[sample_point_count + 1] @ _temp_sample_data_ptr;
        _temp_sample_data_ptr += (sample_point_count + 1) * 2;
    }
};

struct fc_waveform_metadata {
    u8 waveform_length;
    if (waveform_length != 0) {
        be u16 waveform_block[waveform_length] @ _temp_sample_data_ptr;
        _temp_sample_data_ptr += waveform_length * 2;
    }
};

u32 _temp_sample_data_ptr;

struct fc14 {
    u32 signature;

    be u32 pattern_index_size;
    be u32 pattern_data_offset;
    be u32 pattern_data_size;
    be u32 frequency_sequence_offset;
    be u32 frequency_sequence_size;
    be u32 volume_sequence_offset;
    be u32 volume_sequence_size;
    be u32 sample_data_offset;
    be u32 waveform_data_offset;

    u32 pattern_index_count      = pattern_index_size      / sizeof(fc_pattern_index_entry);
    u32 pattern_data_count       = pattern_data_size       / sizeof(fc_pattern);
    u32 frequency_sequence_count = frequency_sequence_size / sizeof(fc_freq_seq);
    u32 volume_sequence_count    = volume_sequence_size    / sizeof(fc_volume_seq);

    _temp_sample_data_ptr = sample_data_offset;
    fc_sample_metadata sample_metadata[10];

    _temp_sample_data_ptr = waveform_data_offset;
    fc_waveform_metadata waveform_metadata[80];

    fc_pattern_index_entry pattern_index [pattern_index_count];

    $ = pattern_data_offset;
    fc_pattern patterns [pattern_data_count];

    $ = frequency_sequence_offset;
    fc_freq_seq frequency_sequences [frequency_sequence_count];

    $ = volume_sequence_offset;
    fc_volume_seq volume_sequences [volume_sequence_count];
};

fc14 music @ 0;
```

## Structural hints for the C64 form

| Amiga FC1.4 concept | C64 MoN/FC analog (from realdmx Cybernoid II) |
|---------------------|-----------------------------------------------|
| `signature` (u32 "SMOD"/"FC14") | None — PSID wrapper hides this |
| `pattern_index_size` | Length of `seqXX` lists |
| Per-channel `(pattern_id, transpose, sound_transpose, speed)` | Sequence stream: pattern-id byte, plus `$40-$5F toneadd` (transpose), `$60-$7F voiceinc` (sound_transpose), `$80-$BF repeat`, header `snelheid` (speed). **NOT a fixed struct on C64 — stream-encoded.** |
| `fc_note { pitch, info }` (2 bytes) | C64 patterns are **variable-length**: 1 byte for plain note ($00-$7F), 2 bytes for instrument-change ($C0-$DF + next), 3 bytes for glide ($E0-$EF + 2 next). NOT fixed 2-byte. |
| `freq_seq[64]`, `volume_seq[64]` | On C64 these are the **wave table / pulse table / filter table** — variable-length command streams (1-byte ID + 1-byte param), see realdmx file for full table semantics. |
| `sample_metadata[10]` | C64 has **no sample playback** in standard FC; this maps to nothing (or, for FC4+ packed, the drum waveform/freq tables `dwa/dto`). |
| `waveform_metadata[80]` | C64 instrument bank (`pulsehi/waveform/attdec/...` at 8 bytes each) — up to ~80 instruments. |

## Source quality note

This spec is **unverified secondary source** — a single gist by a
modern user. Cross-check against:
- Hippel's original FC1.4 Amiga release (1991-ish)
- UADE replay source (`uade/src/players/futurecomposer/`)
- NostalgicPlayer Amiga FC source
