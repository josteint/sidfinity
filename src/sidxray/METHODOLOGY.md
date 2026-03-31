# SID X-Ray: Reverse Engineering Methodology

How to use sidxray to understand an unknown SID player and build an X→USF converter.

## Step 1: Run sidxray

```bash
python3 -m src.sidxray.xray file.sid --duration 10 -v
```

Get the region map, sequential table access, and per-address stats.

## Step 2: Identify the frequency table

The freq table is ~96×2 bytes read on most frames. sidxray labels it `freq_table?`. Verify: values should match known PAL/NTSC frequency bytes. This is also the boundary between player code and data.

## Step 3: Find instrument columns via co-occurrence

Look for groups of addresses that are **always read on the same frames** at low duty (2-15%). These are instrument column accesses — the player reads multiple fields for one instrument on note-trigger frames.

The **stride** between co-occurring addresses = `ni` (number of instruments). The number of addresses in the group = number of instrument columns.

## Step 4: Determine ni (instrument count)

From the co-occurrence group: addresses are at `base + col * ni + Y` where Y is the instrument number. The stride between consecutive addresses in the group = ni.

Verify: check other instrument numbers by looking for the same stride pattern at different offsets (Y values).

## Step 5: Identify which column is which

Known column order (GT2): AD, SR, wave_ptr, pulse_ptr, filter_ptr, vib_param, vib_delay, gate_timer, first_wave. Some may be stripped.

Heuristics by value:
- **AD/SR**: $00-$FF, every combination valid. AD often has high nibble ≥ 4.
- **wave_ptr**: small integers (0-30ish) or remapped indices. 0 = no wave table.
- **pulse_ptr/filter_ptr**: similar small integers or 0.
- **gate_timer**: 0-63. Often 1-3.
- **first_wave**: SID waveform byte ($10=tri, $21=saw, $41=pulse, $81=noise, $09=test+gate).

Cross-reference with SID register writes: if a column value appears in a SID write on the same frame, that identifies the column (e.g., value written to $D405 = AD column).

## Step 6: Find wave/pulse/filter/speed tables

Look for **sequential table access** — addresses that increment by 1 across consecutive frames. These are tables being stepped through frame-by-frame.

Also look for addresses in the co-occurrence group that are read on note triggers AND on subsequent frames. These are table pointer initializations.

Table structure: typically paired (left column, right column) at consecutive addresses. The left column contains the "command" (waveform, duration, set/modulate), right column the "parameter" (note offset, speed, value).

## Step 7: Find pattern data and orderlists

**Pattern data**: medium-duty reads (10-20%) with variable values. Read on tick boundaries (every N frames where N = tempo). Values include note bytes, instrument changes, rest markers.

**Orderlists**: low-duty reads (< 5%) that happen when patterns end. Each voice has its own orderlist. Values are pattern indices.

**Song table**: pair of addresses (lo/hi) read on orderlist access. Points to orderlist start positions.

**Pattern table**: pair of addresses (lo/hi) read when loading patterns. Points to pattern data positions.

## Step 8: Verify with register comparison

Once you've identified all structures, build the X→USF converter and test:

```bash
python3 src/usf_to_sid.py original.sid output.sid
```

Compare register output frame-by-frame. Focus on freq_hi first (easiest to match), then waveform, then ADSR.

## Step 9: Iterate

Common issues:
- **Wrong ni**: re-check stride in co-occurrence groups
- **Wrong column assignment**: cross-reference with SID writes
- **Missing tables**: check for addresses read every frame that aren't freq table
- **Timing mismatch**: check tempo/speed detection

## Tips

- Run with `--duration 30` for better statistics (more note triggers = clearer co-occurrence)
- Compare two files with the same player to find common structure
- Use `--writelog` alongside `--memtrace` to correlate reads with SID writes
- The first frame (init) reads addresses in a different pattern — skip frame 0 in analysis
