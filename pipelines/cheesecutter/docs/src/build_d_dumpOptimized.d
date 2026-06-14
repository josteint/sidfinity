/*
 * Key excerpt from src/ct/build.d (CheeseCutter 2.x, GPL, (C) Abaddon)
 * source_url: local /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/src/ct/build.d
 * fetch_date: 2026-06-14
 *
 * This excerpt shows:
 *   1. PSID header field offsets (enum block)
 *   2. doBuild() entry point
 *   3. dumpOptimized(): per-tune INCLUDE_* flag detection and injection
 *   4. generatePSIDHeader(): PSID construction from assembled bytes
 *
 * See cluster_native_player_and_export.md §2, §4 for analysis.
 */

// build.d lines 37-50: PSID field offsets
enum {
    PSID_LOAD_ADDR_OFFSET = 0x08,
    PSID_INIT_OFFSET = 0x0a,
    PSID_PLAY_OFFSET = 0x0c,
    PSID_TITLE_OFFSET = 0x16,
    PSID_FLAGS_OFFSET = 0x76,
    PSID_NUM_SONGS = 0x0e,
    PSID_START_SONG = 0x10,
    PSID_SPEED_OFFSET = 0x12,
    PAL_CLOCK = 0x4cc7,
    PSID_DATA_START = 0x7c
}

// build.d lines 114-139: doBuild() and generatePSIDHeader()
ubyte[] doBuild(Song song, int address, int zpAddress,
                bool genPSID, int defaultSubtune,
                bool verbose) {
    // ... (see full file)
    string input = dumpOptimized(song, address, zpAddress, genPSID, verbose);
    ubyte[] assembled = cast(ubyte[])assemble(input);
    return genPSID ? generatePSIDHeader(song, assembled, address, address + 3,
                                        defaultSubtune) : assembled;
}

// build.d lines 141-260: dumpOptimized() — effect-usage scanning + INCLUDE_* injection
string dumpOptimized(Song song, int address, int zpAddress, bool genPSID, bool verbose) {
    string input = playerSource;
    input ~= dumpData(song);

    // INSNO = highest instrument number actually used + 1 (per-tune stride!)
    input = setArgumentValue("INSNO", format("%d", song.numInstr+1), input);

    // Scan all sequence elements to determine which effects are used:
    bool chordUsed, swingUsed, filterUsed, vibratoUsed;
    bool setAttUsed, setDecUsed, setSusUsed, setRelUsed, setVolUsed, setSpeedUsed;
    bool offsetUsed, slideUpUsed, slideDnUsed, lovibUsed, portaUsed, setADSRUsed;

    song.seqIterator((Sequence s, Element e) {
        int val = e.cmd.value;
        if(val == 0) return;
        if(val < 0x40) {
            int cmdval = song.superTable[val];  // look up cmd number for this super index
            if(cmdval < 1) slideUpUsed = true;
            else if(cmdval == 1) slideDnUsed = true;
            else if(cmdval == 2) vibratoUsed = true;
            else if(cmdval == 3) offsetUsed = true;
            else if(cmdval == 4) setADSRUsed = true;
            else if(cmdval == 5) lovibUsed = true;
            else if(cmdval == 7) portaUsed = true;
            return;
        }
        // High-range inline commands ($40+):
        else if(val < 0x60) return;               // $40-$5f: pulse program — not a flag
        else if(val < 0x80) filterUsed = true;    // $60-$7f: filter program
        else if(val < 0xa0) chordUsed = true;     // $80-$9f: chord
        else if(val < 0xb0) setAttUsed = true;    // $a0-$af: set Attack
        else if(val < 0xc0) setDecUsed = true;    // $b0-$bf: set Decay
        else if(val < 0xd0) setSusUsed = true;    // $c0-$cf: set Sustain
        else if(val < 0xe0) setRelUsed = true;    // $d0-$df: set Release
        else if(val < 0xf0) setVolUsed = true;    // $e0-$ef: set Volume
        else {
            if(val == 0xf0 || val == 0xf1) swingUsed = true;  // speed<2 swing
            setSpeedUsed = true;                               // $f0-$ff: set Speed
        }
    });

    // Also check: any subtune speed < 2 → INCLUDE_BREAKSPEED
    for(int i = 0; i < song.subtunes.numOf; i++) {
        if(song.songspeeds[i] < 2) swingUsed = true;
    }
    // Also check: any instrument with non-zero filter pointer → INCLUDE_FILTER
    for(int i = 0; i < 48; i++) {
        if(song.filtertablePointer(i) > 0) filterUsed = true;
    }

    // Inject all INCLUDE_* defines into player source:
    input = setArgumentValue("EXPORT", "TRUE", input);
    setArgVal("INCLUDE_CMD_SLUP",       slideUpUsed  ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_SLDOWN",     slideDnUsed  ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_VIBR",       vibratoUsed  ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_PORTA",      portaUsed    ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_SET_ADSR",   setADSRUsed  ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_CHORD",  chordUsed    ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CHORD",          chordUsed    ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_SET_OFFSET", offsetUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_CMD_SET_LOVIB",  lovibUsed    ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_ATT",    setAttUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_DEC",    setDecUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_SUS",    setSusUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_REL",    setRelUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_VOL",    setVolUsed   ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_SEQ_SET_SPEED",  setSpeedUsed ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_BREAKSPEED",     swingUsed    ? "TRUE" : "FALSE");
    setArgVal("INCLUDE_FILTER",         filterUsed   ? "TRUE" : "FALSE");
    setArgVal("MULTISPEED",             song.multiplier > 1 ? "TRUE" : "FALSE");
    if(song.multiplier > 1) {
        setArgVal("USE_MDRIVER", genPSID ? "TRUE" : "FALSE");
        setArgVal("CIA_VALUE",   format("$%04x", PAL_CLOCK / song.multiplier));
        setArgVal("MULTIPLIER",  format("%d", song.multiplier - 1));
    }
    setArgVal("BASEADDRESS", format("$%04x", address));
    // NOTE: INCLUDE_CMD_SET_WAVE is never set to TRUE — command $06 always absent
    return input;
}
