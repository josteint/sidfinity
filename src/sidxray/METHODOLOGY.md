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

## Lessons Learned: GoatTracker V2

What we discovered applying this methodology to `On_a_Sanction_from_CIA.sid`:

### Static analysis failed

- The GT2 packer (`greloc.c`) conditionally strips unused columns, so the number and order of columns varies per file.
- Address gap analysis gave ni=5 (wrong). The first two referenced addresses happened to be 5 apart, but the actual stride was 11.
- The greloc.c source says data order is freq→song→patt→instruments, but this file had freq hi before lo (opposite of what greloc.c emits). Different GT2 versions use different orders.
- Searching for column base addresses as 16-bit operands in the player code only found 3 out of 7 columns — the rest were accessed but not at the expected stride-5 offsets.

### Memtrace succeeded

- Co-occurrence analysis immediately revealed 5 addresses always read on the same 13 frames → these are 5 instrument columns for instrument Y=7.
- The stride between them (11) gave the true ni=11.
- Checking other mod-11 offsets confirmed: Y=8 read 4 times, Y=9 read once — different instruments triggered at different rates.
- High-duty addresses (>80%) at the same base turned out to be per-frame register updates, not instrument triggers — important to separate from note-trigger reads.
- The wave table was identified by sequential stepping (frame-by-frame increment) at addresses right after the instrument columns.

### Key finding: ni ≠ address gap

The GT2 packer can produce ANY ni value depending on how many instruments are defined (not just used). The first two addresses in the data area may have a gap that has nothing to do with ni. Only the co-occurrence stride is reliable.

### What FIXEDPARAMS does

When the GT2 packer determines all instruments share the same gate_timer and first_wave values, it sets FIXEDPARAMS=1 and:
- Removes the gate_timer and first_wave columns entirely
- Embeds them as compile-time constants in the player code (LDA #xx instead of LDA table,Y)
- This reduces column count from 9 to 7 (in this file's case)

The memtrace reveals this because those addresses simply don't appear in the note-trigger co-occurrence group.

## Player Version Detection

Different GT2 player versions produce different audio from identical song data. See `docs/gt2_player_versions.md` for the full analysis. In brief, there are 4 behavior groups (A-D) distinguished by ADSR write order, new-note register behavior, and vibrato handling. Detect the group by examining the hard restart code's STA $D405/$D406 order and the new-note JMP target.

## Tips

- Run with `--duration 30` for better statistics (more note triggers = clearer co-occurrence)
- Compare two files with the same player to find common structure
- Use `--writelog` alongside `--memtrace` to correlate reads with SID writes
- The first frame (init) reads addresses in a different pattern — skip frame 0 in analysis
- High-duty reads at instrument column addresses are per-frame register writes, not note triggers — filter by duty cycle to separate them
- If ni seems wrong, check co-occurrence stride instead of address gaps
