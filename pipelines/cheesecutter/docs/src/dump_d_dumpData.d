/*
 * Key excerpt from src/ct/dump.d (CheeseCutter 2.x, GPL, (C) Abaddon)
 * source_url: local /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/src/ct/dump.d
 * fetch_date: 2026-06-14
 *
 * dumpData() is the ACME assembly source emitter for song data.
 * It produces the data section appended after playerSource in dumpOptimized().
 * The emit ORDER defines the runtime memory layout of the exported SID.
 *
 * See cluster_native_player_and_export.md §2b, §3 for analysis.
 */

string dumpData(Song sng) {
    // --- Wave table (col A then col B, trimmed to last non-zero) ---
    append("arp1 = *\n");
    tablen = getHighestUsed(sng.wave1Table) + 1;
    hexdump(sng.wave1Table[0 .. tablen], 16);
    append("arp2 = *\n");
    hexdump(sng.wave2Table[0 .. tablen], 16);  // SAME trim point as arp1

    // --- Filter table (4-byte rows, trimmed to last row boundary) ---
    append("filttab = *\n");
    hexdump(sng.filterTable[0 .. getHighestUsed(sng.filterTable) + 4], 4);

    // --- Pulse table (4-byte rows, trimmed) ---
    append("pulstab = *\n");
    hexdump(sng.pulseTable[0 .. getHighestUsed(sng.pulseTable) + 4], 4);

    // --- Instrument table: 8 columns, each maxInsno+1 bytes ---
    // column-major: instrumentTable[col*48 .. col*48 + (maxInsno+1)]
    // INSNO = maxInsno+1 is set separately in build.d
    append("inst = *\n");
    int maxInsno = sng.numInstr;  // highest instrument number referenced in sequences
    for(int i = 0; i < 8; i++) {
        append(format("\ninst%d = *\n", i));
        hexdump(sng.instrumentTable[i * 48 .. i * 48 + (maxInsno+1)], 16);
    }

    // --- Sequence pointer tables (one byte per seq: lo then hi) ---
    // ACME: !8 <s00,<s01,...  (low bytes)
    // ACME: !8 >s00,>s01,...  (high bytes)
    // Resolved by ACME to absolute addresses of sXX labels
    append("\nseqlo = *\n\t\t!8 ");
    for(int i = 0; i < sng.numOfSeqs(); i++) { append(format("<s%02x", i)); ... }
    append("\nseqhi = *\n\t\t!8 ");
    for(int i = 0; i < sng.numOfSeqs(); i++) { append(format(">s%02x", i)); ... }

    // --- Command (super) table: 3 columns, tablen entries each ---
    // tablen = highest sequence cmd index < $40 + 1 (so includes row 0 always)
    // superTable layout: cmd1[0..64] | cmd2[64..128] | cmd3[128..192]
    // cmd2[0] = global HR-AD value (reserved row 0)
    append("\ncmd1 = *\n"); hexdump(sng.superTable[0..tablen], 16);
    append("cmd2 = *\n");   hexdump(sng.superTable[64..64+tablen], 16);
    append("cmd3 = *\n");   hexdump(sng.superTable[128..128+tablen], 16);

    // --- Songsets: per-subtune track pointers + speed/voicemask ---
    // Format per subtune: !word track{i}_0, track{i}_1, track{i}_2
    //                     !byte songspeeds[i], 7
    // 8 bytes per subtune: 3 × 2-byte ptr + speed + voicemask(=7 hardcoded)
    append("songsets = *\n");
    for(int i = 0; i < sng.subtunes.numOf; i++) {
        append("!word " + tracks...);
        append(format("\n\t\t!byte %d, 7\n", sng.songspeeds[i]));
    }

    // --- Per-subtune orderlists (compacted Tracklist.compact() output) ---
    // Each is a variable-length byte stream: [trans] seqno ... $fX wrap
    foreach(i, subtune; packedTracks) {
        foreach(j, voice; subtune) {
            append(format("track%d_%d = *\n", i, j));
            hexdump(voice, 16);
        }
    }

    // --- Packed sequences (Sequence.compact() output) ---
    for(int i = 0; i < sng.numOfSeqs(); i++) {
        append(format("s%02x = *\n", i));
        hexdump(sng.seqs[i].compact(), 16);
    }

    // --- Chord table (trimmed to last non-zero + 1) ---
    tablen = getHighestUsed(sng.chordTable) + 1;
    append("\nchord");
    hexdump(sng.chordTable[0..tablen], 16);

    // --- Chord index table (entries 0..highestChord, where highestChord =
    //     max (cmd.value & $1f) for all $80-$9f commands seen in sequences) ---
    append("\nchordindex");
    hexdump(sng.chordIndexTable[0..highestChord+1], 16);
}

/*
 * EMIT ORDER SUMMARY (= runtime memory layout after player code):
 *   arp1        wave col A    [0..N bytes, N = getHighestUsed(wave1Table)+1]
 *   arp2        wave col B    [same N bytes]
 *   filttab     filter rows   [4-byte rows, trimmed]
 *   pulstab     pulse rows    [4-byte rows, trimmed]
 *   inst0..7    instrument columns 0-7  [maxInsno+1 bytes each]
 *   seqlo       seq ptr low   [numOfSeqs bytes]
 *   seqhi       seq ptr high  [numOfSeqs bytes]
 *   cmd1/2/3    super table   [tablen bytes each]
 *   songsets    per-subtune   [8 bytes × numSubtunes]
 *   track{i}_{v} orderlists  [variable length × numSubtunes × 3 voices]
 *   s00..sNN    sequences     [variable length × numOfSeqs]
 *   chord       chord data    [variable]
 *   chordindex  chord index   [highestChord+1 bytes]
 */
