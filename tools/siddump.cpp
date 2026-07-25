/*
 * siddump - Dump SID register writes frame-by-frame
 *
 * Loads a .sid file via libsidplayfp, runs the emulator frame by frame,
 * and outputs the 25 writable SID register values for each frame as
 * comma-separated hex bytes. One line per frame.
 *
 * Output format:
 *   Line 1: JSON metadata (title, author, released, clock, model, songs, etc.)
 *   Line 2: Header naming the 25 registers
 *   Line 3+: One frame per line, registers as hex bytes
 *            Optional |D:cyc:reg:val,... suffix for intra-frame digi writes
 *
 * Exit codes:
 *   0 = success
 *   1 = error (load/config failure)
 *   2 = silent tune (all registers zero)
 *   3 = skipped (RSID or multi-SID)
 *
 * Usage: siddump <file.sid> [options]
 *   --subtune N    Select subtune, 1-BASED (0/absent = the tune's start song).
 *                  NB the rest of the project counts subtunes from 0, so a
 *                  verify/verdict "sub k" is `--subtune k+1`.
 *   --duration N   Duration in seconds (default: 60)
 *   --timeout N    Timeout in seconds (default: 0 = no timeout)
 *   --raw          Skip metadata/header lines
 *   --digi         Enable intra-frame write logging
 */

#include <algorithm>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <utility>
#include <vector>

#include "sidplayfp/sidplayfp.h"
#include "sidplayfp/SidTune.h"
#include "sidplayfp/SidTuneInfo.h"
#include "sidplayfp/SidConfig.h"
#include "sidplayfp/sidbuilder.h"
#include "c64/c64sid.h"
#include "c64/c64cpu.h"
#include "sidlite.h"

// SID register names for the header line
static const char* reg_names[] = {
    // Voice 1 (regs 0-6)
    "V1_FREQ_LO", "V1_FREQ_HI", "V1_PW_LO", "V1_PW_HI",
    "V1_CTRL", "V1_AD", "V1_SR",
    // Voice 2 (regs 7-13)
    "V2_FREQ_LO", "V2_FREQ_HI", "V2_PW_LO", "V2_PW_HI",
    "V2_CTRL", "V2_AD", "V2_SR",
    // Voice 3 (regs 14-20)
    "V3_FREQ_LO", "V3_FREQ_HI", "V3_PW_LO", "V3_PW_HI",
    "V3_CTRL", "V3_AD", "V3_SR",
    // Filter + volume (regs 21-24)
    "FILT_LO", "FILT_HI", "FILT_CTRL", "FILT_MODE_VOL"
};

static const int NUM_REGS = 25;

// Timeout handler
static void timeout_handler(int) { _exit(4); }

// JSON-escape a string (handles quotes, backslashes, control chars)
static std::string json_escape(const char* s)
{
    std::string out;
    if (!s) return out;
    for (; *s; s++) {
        unsigned char c = static_cast<unsigned char>(*s);
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (c < 0x20 || c >= 0x80) {
                    char buf[8];
                    snprintf(buf, sizeof(buf), "\\u%04x", c);
                    out += buf;
                } else {
                    out += static_cast<char>(c);
                }
                break;
        }
    }
    return out;
}

int main(int argc, char* argv[])
{
    if (argc < 2) {
        fprintf(stderr,
            "Usage: %s <file.sid> [options]\n"
            "  --subtune N    Select subtune, 1-BASED (0/absent = start song).\n"
            "                 NB the rest of the project counts subtunes from\n"
            "                 0 — a verdict's \"sub k\" is `--subtune k+1`.\n"
            "  --duration N   Duration in seconds (default: 60)\n"
            "  --timeout N    Timeout in seconds (default: 0 = none)\n"
            "  --raw          Skip metadata/header lines\n"
            "  --digi         Enable intra-frame write logging\n"
            "  --writelog     Append full register write stream with cycle timing (ground truth)\n"
            "  --writelog-per-irq  Like --writelog, but writes are bucketed PER PSID play()\n"
            "                      invocation (|I chunk), not per siddump frame. Eliminates\n"
            "                      Trap C. Splits by play-entry cycle (origin-corrected) and\n"
            "                      drops the init prefix (writes before the first play-entry).\n"
            "                      Implies --writelog; prefix changes from |W: to |I.\n"
            "  --per-irq-debug  --writelog-per-irq + stderr dump of base/entry/write cycles\n"
            "  --memtrace     Append memory access trace\n"
            "  --pcm          Output raw 16-bit signed PCM to stdout\n"
            "  --force-rsid   Process RSID files (normally skipped)\n"
            "  --roms-dir DIR Dir with C64 kernal/basic/chargen ROM files (needed to\n"
            "                 actually run RSID + C64-BASIC tunes; defaults to\n"
            "                 $SIDFINITY_ROMS_DIR, else $HOME/.local/share/sidplayfp)\n"
            "  --pc-trace FILE START END  Dump CPU PC trace to FILE for frames START..END\n"
            "  --memwatch HEX[,HEX...]    Per-frame snapshot of RAM at these addresses (post-play)\n"
            "                             (e.g. --memwatch 90C5,90C8,90CB,9116). Output lines:\n"
            "                             M<frame>:<addr>=<val>[:<addr>=<val>...]\n"
            "                             When --memwatch is on, also emits |P:<count> giving the\n"
            "                             number of PSID play() invocations that fired in this\n"
            "                             siddump frame. Used to diagnose Trap C alignment.\n"
            "  --peek-post-init HEX-HEX[,HEX-HEX...]  Print CPU-EYE bytes (through the MMU:\n"
            "                             banked ROM incl. psiddrv-patched vectors, 6510 port,\n"
            "                             power-on RAM pattern) for the ranges after init, then\n"
            "                             exit. One PEEK:AAAA=VV,... line.\n"
            "  --memwatch-on-write HEX HEX[,HEX...]  Event-driven memwatch. First HEX is the\n"
            "                             trigger address (e.g. D404). The second argument is ONE\n"
            "                             COMMA-separated list (NO spaces) of the RAM addresses to\n"
            "                             snapshot every time the CPU writes to the trigger.\n"
            "                             Emits one E<idx>:<trigger=val>:<addr=val>... line per\n"
            "                             event. Use for SMC / conditional-update traces.\n"
            "  --reinit-snapshot PC LO-HI  Capture RAM[LO..HI] at (COLD) the first play-vector\n"
            "                             entry and (WARM) the first play-vector entry after PC\n"
            "                             (a reinit wedge) executes, then exit. One\n"
            "                             SNAP:COLD=<hex>|WARM=<hex> line (WARM omitted if PC never\n"
            "                             hit). Ground-truth C19 shape-B $FF-reinit ghost capture.\n"
            "  --pc-watch LIST BEFORE-AFTER  Record an event whenever a watched PC EXECUTES\n"
            "                             (data reads rejected — C36 bus signature). LIST is ONE\n"
            "                             comma-list of hex PCs and/or *XX low-byte patterns;\n"
            "                             BEFORE-AFTER sizes the RAM window [pc-BEFORE, pc+AFTER]\n"
            "                             captured per event. Emits per frame:\n"
            "                             |PW:<pc>:<a>:<x>:<y>:<playidx>:<relwin>:<abswin>\n"
            "                             (playidx 0 = during init). Options: --pc-watch-first\n"
            "                             (dedupe per PC), --pc-watch-abs LO-HI (also capture an\n"
            "                             absolute RAM window per event).\n",
            argv[0]);
        return 1;
    }

    const char* filename = argv[1];
    int subtune = 0;
    double seconds = 60;
    int timeout = 0;
    bool raw = false;
    bool digi = false;
    bool writelog = false;
    bool writelog_per_irq = false;
    bool perirq_debug = false;
    bool memtrace = false;
    bool pcm = false;
    bool force_rsid = false;
    const char* roms_dir = nullptr;          // null -> default ~/.local/share/sidplayfp
    const char* pc_trace_path = nullptr;
    int pc_trace_start_frame = -1;
    int pc_trace_end_frame = -1;
    std::vector<uint16_t> memwatch_addrs;
    uint16_t memwatch_event_trigger = 0;     // 0 = disabled
    std::vector<uint16_t> memwatch_event_ram;
    std::vector<std::pair<uint16_t, uint16_t>> peek_ranges;
    bool reinit_on = false;                  // --reinit-snapshot
    uint16_t reinit_trig = 0;
    uint16_t reinit_lo = 0, reinit_hi = 0;
    bool pcwatch_on = false;                 // --pc-watch
    bool pcwatch_first = false;              // --pc-watch-first
    std::vector<uint16_t> pcwatch_exact;
    std::vector<uint8_t> pcwatch_low;
    uint16_t pcwatch_before = 0, pcwatch_after = 0;
    uint32_t pcwatch_abs_lo = 1, pcwatch_abs_hi = 0;   // lo>hi = off

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--raw") == 0) {
            raw = true;
        } else if (strcmp(argv[i], "--digi") == 0) {
            digi = true;
        } else if (strcmp(argv[i], "--writelog") == 0) {
            writelog = true;
        } else if (strcmp(argv[i], "--writelog-per-irq") == 0) {
            writelog = true;
            writelog_per_irq = true;
        } else if (strcmp(argv[i], "--per-irq-debug") == 0) {
            writelog = true;
            writelog_per_irq = true;
            perirq_debug = true;
        } else if (strcmp(argv[i], "--memtrace") == 0) {
            memtrace = true;
        } else if (strcmp(argv[i], "--pcm") == 0) {
            pcm = true;
        } else if (strcmp(argv[i], "--force-rsid") == 0) {
            force_rsid = true;
        } else if (strcmp(argv[i], "--roms-dir") == 0 && i + 1 < argc) {
            roms_dir = argv[++i];
        } else if (strcmp(argv[i], "--pc-trace") == 0 && i + 3 < argc) {
            pc_trace_path = argv[++i];
            pc_trace_start_frame = atoi(argv[++i]);
            pc_trace_end_frame = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--memwatch") == 0 && i + 1 < argc) {
            // Comma-separated list of hex addresses to snapshot each frame
            const char* p = argv[++i];
            while (*p) {
                char* end = nullptr;
                unsigned long addr = strtoul(p, &end, 16);
                if (end == p) break;
                memwatch_addrs.push_back(static_cast<uint16_t>(addr));
                p = end;
                if (*p == ',') ++p;
            }
        } else if (strcmp(argv[i], "--memwatch-on-write") == 0 && i + 2 < argc) {
            // Trigger addr (hex) + comma-list of RAM addrs to snapshot
            memwatch_event_trigger = static_cast<uint16_t>(strtoul(argv[++i], nullptr, 16));
            const char* p = argv[++i];
            while (*p) {
                char* end = nullptr;
                unsigned long addr = strtoul(p, &end, 16);
                if (end == p) break;
                memwatch_event_ram.push_back(static_cast<uint16_t>(addr));
                p = end;
                if (*p == ',') ++p;
            }
        } else if (strcmp(argv[i], "--peek-post-init") == 0 && i + 1 < argc) {
            // ONE comma-separated list of AAAA-BBBB hex ranges (inclusive)
            const char* p = argv[++i];
            while (*p) {
                char* end = nullptr;
                unsigned long lo = strtoul(p, &end, 16);
                if (end == p) break;
                p = end;
                unsigned long hi = lo;
                if (*p == '-') {
                    ++p;
                    hi = strtoul(p, &end, 16);
                    if (end == p) break;
                    p = end;
                }
                peek_ranges.emplace_back(static_cast<uint16_t>(lo),
                                         static_cast<uint16_t>(hi));
                if (*p == ',') ++p;
            }
        } else if (strcmp(argv[i], "--reinit-snapshot") == 0 && i + 2 < argc) {
            // PC (hex) + one AAAA-BBBB hex RAM range (inclusive). Captures the
            // window at (COLD) the first play-vector entry and (WARM) the first
            // play-vector entry after PC executes; see the run block below.
            reinit_on = true;
            reinit_trig = static_cast<uint16_t>(strtoul(argv[++i], nullptr, 16));
            const char* p = argv[++i];
            char* end = nullptr;
            reinit_lo = static_cast<uint16_t>(strtoul(p, &end, 16));
            if (end != p && *end == '-')
                reinit_hi = static_cast<uint16_t>(strtoul(end + 1, nullptr, 16));
            else
                reinit_hi = reinit_lo;
        } else if (strcmp(argv[i], "--pc-watch") == 0 && i + 2 < argc) {
            // ONE comma-list of watch items (hex PC, or *XX = low-byte
            // pattern) + ONE BEFORE-AFTER hex pair for the relative RAM
            // window captured per event.
            pcwatch_on = true;
            const char* p = argv[++i];
            while (*p) {
                if (*p == '*') {
                    ++p;
                    char* end = nullptr;
                    unsigned long lb = strtoul(p, &end, 16);
                    if (end == p) break;
                    pcwatch_low.push_back(static_cast<uint8_t>(lb));
                    p = end;
                } else {
                    char* end = nullptr;
                    unsigned long pc = strtoul(p, &end, 16);
                    if (end == p) break;
                    pcwatch_exact.push_back(static_cast<uint16_t>(pc));
                    p = end;
                }
                if (*p == ',') ++p;
            }
            const char* w = argv[++i];
            char* end = nullptr;
            pcwatch_before = static_cast<uint16_t>(strtoul(w, &end, 16));
            if (end != w && *end == '-')
                pcwatch_after = static_cast<uint16_t>(strtoul(end + 1, nullptr, 16));
        } else if (strcmp(argv[i], "--pc-watch-first") == 0) {
            pcwatch_first = true;
        } else if (strcmp(argv[i], "--pc-watch-abs") == 0 && i + 1 < argc) {
            // Optional absolute RAM window captured with every event.
            const char* p = argv[++i];
            char* end = nullptr;
            pcwatch_abs_lo = strtoul(p, &end, 16);
            if (end != p && *end == '-')
                pcwatch_abs_hi = strtoul(end + 1, nullptr, 16);
            else
                pcwatch_abs_hi = pcwatch_abs_lo;
        } else if (strcmp(argv[i], "--subtune") == 0 && i + 1 < argc) {
            subtune = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--duration") == 0 && i + 1 < argc) {
            seconds = atof(argv[++i]);
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout = atoi(argv[++i]);
        } else {
            // HARD ERROR on anything unrecognised. This used to be a legacy
            // positional catch-all (`atoi(argv[i]) > 0` -> subtune, then
            // seconds) with unknown FLAGS silently dropped, which made a
            // mistyped invocation produce a plausible WRONG dump instead of a
            // failure: `--memwatch-on-write D40F 1707 1708 170A` (spaces where
            // the option wants ONE comma-separated list) watched only $1707
            // and silently ran subtune 1708 -> 1707. Measurement tools must
            // refuse rather than answer confidently (cf. dmc_state_addr.py).
            fprintf(stderr, "Unrecognised argument: %s\n", argv[i]);
            if (atoi(argv[i]) > 0)
                fprintf(stderr, "  (bare numbers are no longer accepted — use "
                                "--subtune N / --duration N; note --memwatch "
                                "and --memwatch-on-write take ONE "
                                "COMMA-separated address list)\n");
            return 1;
        }
    }

    // Set timeout if requested
    if (timeout > 0) {
        signal(SIGALRM, timeout_handler);
        alarm(timeout);
    }

    // Load the SID tune
    SidTune tune(filename);
    if (!tune.getStatus()) {
        fprintf(stderr, "Error loading %s: %s\n", filename, tune.statusString());
        return 1;
    }

    const SidTuneInfo* info = tune.getInfo();
    if (!info) {
        fprintf(stderr, "Error: could not get tune info\n");
        return 1;
    }

    // Skip RSID files (unless --force-rsid is specified)
    if (!force_rsid && info->compatibility() == SidTuneInfo::COMPATIBILITY_R64) {
        fprintf(stderr, "Skipping RSID: %s\n", filename);
        return 3;
    }

    // Multi-SID files (PSID v3/v4 2SID/3SID) are supported: every chip's
    // writes land in the write log, tagged reg = chip*0x20 + reg.

    // Select subtune
    if (subtune == 0) subtune = info->startSong();
    tune.selectSong(subtune);

    // Re-read info after selecting song
    info = tune.getInfo();
    bool isPAL = (info->clockSpeed() != SidTuneInfo::CLOCK_NTSC);
    int fps = isPAL ? 50 : 60;

    // Set up the emulator
    sidplayfp engine;

    SIDLiteBuilder builder("SIDLite");

    SidConfig cfg;
    cfg.defaultC64Model = isPAL ? SidConfig::PAL : SidConfig::NTSC;
    cfg.defaultSidModel = SidConfig::MOS6581;
    cfg.frequency = 48000;
    cfg.sidEmulation = &builder;
    cfg.powerOnDelay = 0;  // deterministic

    // Load real C64 ROMs (KERNAL / BASIC / CHARGEN) so RSID tunes — and in
    // particular the C64-BASIC family (RSID flags bit 1, load=init=play=0,
    // tokenized BASIC at $0801) — actually execute. Without them libsidplayfp
    // runs with stub ROMs and the BASIC interpreter never runs, so the tune
    // emits ~nothing (a single $D418 write then silence). setRoms() stores the
    // pointers (no copy), so the buffers MUST outlive playback -> static.
    // Default dir matches the sidplayfp CLI data dir; override with --roms-dir.
    static uint8_t kernalRom[8192];
    static uint8_t basicRom[8192];
    static uint8_t chargenRom[4096];
    {
        // Resolution order: --roms-dir, then $SIDFINITY_ROMS_DIR, then the
        // sidplayfp CLI data dir. The env var lets the repo keep its own ROMs
        // (tools/c64roms, exported by src/env.sh) instead of depending on
        // ~/.local/share, which is not stable on every host — when it
        // vanishes, RSID/C64-BASIC tunes silently emit nothing and every
        // Basic_Program member reports `unsupported:too_few_steps`.
        std::string dir;
        const char* env_dir = getenv("SIDFINITY_ROMS_DIR");
        if (roms_dir) {
            dir = roms_dir;
        } else if (env_dir && *env_dir) {
            dir = env_dir;
        } else {
            const char* home = getenv("HOME");
            dir = std::string(home ? home : ".") + "/.local/share/sidplayfp";
        }
        auto loadRom = [&](const char* name, uint8_t* buf, size_t sz) -> bool {
            std::string path = dir + "/" + name;
            FILE* f = fopen(path.c_str(), "rb");
            if (!f) return false;
            size_t n = fread(buf, 1, sz, f);
            fclose(f);
            return n == sz;
        };
        bool haveK = loadRom("kernal",  kernalRom,  sizeof kernalRom);
        bool haveB = loadRom("basic",   basicRom,   sizeof basicRom);
        bool haveC = loadRom("chargen", chargenRom, sizeof chargenRom);
        if (haveK && haveB && haveC) {
            engine.setRoms(kernalRom, basicRom, chargenRom);
        } else {
            fprintf(stderr,
                "Warning: C64 ROMs not fully loaded from %s "
                "(kernal=%d basic=%d chargen=%d); RSID/BASIC tunes may be silent. "
                "Pass --roms-dir <dir> with kernal/basic/chargen files.\n",
                dir.c_str(), haveK, haveB, haveC);
        }
    }

    if (!engine.config(cfg)) {
        fprintf(stderr, "Error configuring engine: %s\n", engine.error());
        return 1;
    }

    if (!engine.load(&tune)) {
        fprintf(stderr, "Error loading tune into engine: %s\n", engine.error());
        return 1;
    }

    // Cycles per frame: VIC raster frame length + small margin.
    // PAL:  63 cycles/line × 312 lines = 19656, + 32 margin
    // NTSC: 65 cycles/line × 263 lines = 17095, + 32 margin
    // The margin ensures we always cross the raster trigger point.
    //
    // *** TRAP C — read .claude/memory/feedback_verification_modes.md ***
    // The +32 margin means each siddump "frame" processes usually 1,
    // sometimes 0, sometimes 2 PSID `play()` invocations. This is fine
    // for `--writelog` (the flat-prefix comparator in verify_cycle is
    // robust to bucket shifts). But for `--memwatch`, RAM is sampled at
    // the end of each `engine.play(cyclesPerFrame)` call, NOT at IRQ
    // boundaries — state at siddump-frame N can differ from state-after-
    // IRQ-N even when the engines are equivalent under Mode 1.
    //
    // Real fix: hook the PSID play() entry, sample writes+RAM per
    // invocation, emit one record per IRQ. Tracked in
    // tools/INVESTIGATION_BACKLOG.md under "siddump --play-aligned".
    unsigned int cyclesPerFrame = isPAL ? (63 * 312 + 32) : (65 * 263 + 32);

    int totalFrames = static_cast<int>(seconds * fps);

    // Output metadata as JSON
    if (!raw) {
        const char* title = (info->numberOfInfoStrings() > 0) ? info->infoString(0) : "";
        const char* author = (info->numberOfInfoStrings() > 1) ? info->infoString(1) : "";
        const char* released = (info->numberOfInfoStrings() > 2) ? info->infoString(2) : "";

        std::string esc_title = json_escape(title);
        std::string esc_author = json_escape(author);
        std::string esc_released = json_escape(released);

        printf("{\"title\":\"%s\",\"author\":\"%s\",\"released\":\"%s\","
               "\"clock\":\"%s\",\"fps\":%d,\"subtune\":%d,\"songs\":%d,"
               "\"sid_model\":\"%s\",\"format\":\"%s\",\"frames\":%d}\n",
               esc_title.c_str(), esc_author.c_str(), esc_released.c_str(),
               isPAL ? "PAL" : "NTSC", fps, subtune, info->songs(),
               (info->sidModel(0) == SidTuneInfo::SIDMODEL_8580) ? "8580" : "6581",
               info->formatString(),
               totalFrames);

        // Header line
        for (int r = 0; r < NUM_REGS; r++) {
            if (r > 0) printf(",");
            printf("%s", reg_names[r]);
        }
        printf("\n");
    }

    // Enable write logging if requested. Multi-SID tunes (PSID v3/v4
    // 2SID/3SID) log EVERY installed chip; each write is tagged with its
    // chip by encoding reg as chip*0x20 + (reg & 0x1F), so a single-chip
    // tune's output is byte-identical to the untagged format and the
    // flat (reg, val) comparators key multi-chip streams correctly.
    const int nChips = info->sidChips();
    if (digi || writelog) {
        for (int c = 0; c < nChips; c++)
            engine.enableWriteLog(c, true);
    }

    // Merged, chip-tagged write log for one frame: every chip's writes in
    // one cycle-ordered stream (ties resolve by chip index — deterministic).
    // For a single-chip tune this is exactly chip 0's log.
    struct TaggedWrite { uint32_t cycle; uint8_t reg; uint8_t value; };
    std::vector<TaggedWrite> mergedLog;
    auto mergeWriteLogs = [&engine, nChips, &mergedLog]() {
        mergedLog.clear();
        for (int c = 0; c < nChips; c++) {
            const auto& log = engine.getWriteLog(c);
            for (const auto& w : log)
                mergedLog.push_back({w.cycle,
                                     (uint8_t)(c * 0x20 + (w.reg & 0x1F)),
                                     w.value});
        }
        std::stable_sort(mergedLog.begin(), mergedLog.end(),
            [](const TaggedWrite& a, const TaggedWrite& b) {
                return a.cycle < b.cycle;
            });
    };

    // Enable memory read tracing if requested
    if (memtrace) {
        // Trace reads from $0000 to $FFFF (excludes I/O region $D000-$D3FF
        // but we trace everything so high-load SIDs like $E000 are covered)
        engine.enableReadTrace(true, 0x0000, 0xFFFF);
    }

    // Wire the play-vector counter so --memwatch can emit per-frame IRQ
    // counts (Trap C diagnostic). The PSID's playAddr is the address the
    // IRQ handler jumps to — counting reads at that address counts play()
    // invocations. See feedback_verification_modes.md.
    // --writelog-per-irq also needs this to know where to split.
    if (!memwatch_addrs.empty() || writelog_per_irq) {
        engine.setPlayAddr(info->playAddr());
    }

    // Wire memwatch-on-write event capture
    if (memwatch_event_trigger != 0 && !memwatch_event_ram.empty()) {
        engine.setMemWatchOnWrite(memwatch_event_trigger, memwatch_event_ram);
    }

    // Wire the PC-watch (executed-PC events with A/X/Y + RAM windows).
    // setPlayAddr gives each event its play-invocation index (0 = init).
    if (pcwatch_on) {
        engine.setPlayAddr(info->playAddr());
        engine.setPcWatch(pcwatch_exact, pcwatch_low,
                          pcwatch_before, pcwatch_after, pcwatch_first,
                          pcwatch_abs_lo, pcwatch_abs_hi);
    }

    // Initialize mixer (needed for play() to work)
    engine.initMixer(false); // mono

    // --peek-post-init: run two frames (init completes inside the first
    // play() call), then print CPU-EYE bytes for the requested ranges —
    // through the MMU, so banked-in ROM (including psiddrv's patched KERNAL
    // vectors), the 6510 port, and the power-on RAM pattern are all returned
    // exactly as an engine LDA would see them — then exit. Built for the
    // sonified-environment sector windows (Super_Seven's $FFEF window).
    if (!peek_ranges.empty()) {
        engine.play(cyclesPerFrame);
        engine.play(cyclesPerFrame);
        printf("PEEK:");
        bool first = true;
        for (auto& r : peek_ranges) {
            for (unsigned int a = r.first; a <= r.second; a++) {
                printf(first ? "%04X=%02X" : ",%04X=%02X",
                       a & 0xFFFF, engine.cpuPeek(a & 0xFFFF));
                first = false;
                if (a == 0xFFFF) break;   // unsigned wrap guard
            }
        }
        printf("\n");
        return 0;
    }

    // --reinit-snapshot: capture RAM[lo..hi] at (COLD) the first play-vector
    // entry (post-init, before any play body) and (WARM) the first play-vector
    // entry AFTER the wedge PC has executed (= end of the reinit play()), then
    // exit. Reproduces the C19 shape-B $FF-reinit ghost cold/warm windows from
    // ground truth (libsidplayfp) instead of py65 — see
    // docs/siddump_native_capture_plan.md. Both moments align to play-vector
    // entries, so the capture is robust to siddump frame bucketing (Trap C).
    if (reinit_on) {
        engine.setPlayAddr(info->playAddr());   // the play-entry proxy
        engine.setReinitSnapshot(reinit_trig, reinit_lo, reinit_hi);
        for (int frame = 0; frame < totalFrames; frame++) {
            if (engine.play(cyclesPerFrame) < 0) break;
            if (engine.reinitWarmDone()) break; // both windows captured
        }
        auto emitWindow = [](const char* tag, const std::vector<uint8_t>& w) {
            printf("%s=", tag);
            for (uint8_t b : w) printf("%02X", b);
        };
        printf("SNAP:");
        if (engine.reinitColdDone()) emitWindow("COLD", engine.reinitCold());
        if (engine.reinitWarmDone()) { printf("|"); emitWindow("WARM", engine.reinitWarm()); }
        printf("\n");
        return 0;
    }

    // PCM output mode: render audio and write raw 16-bit samples to stdout
    if (pcm) {
        for (int frame = 0; frame < totalFrames; frame++) {
            int samples = engine.play(cyclesPerFrame);
            if (samples <= 0) break;
            short buf[65536];
            unsigned int mixed = engine.mix(buf, samples);
            fwrite(buf, sizeof(short), mixed, stdout);
        }
        return 0;
    }

    // Run frame by frame and dump registers
    uint8_t regs[32];
    bool anyNonZero = false;

    // --writelog-per-irq: the writes that precede the FIRST play() entry of
    // the whole run are the tune's init writes (gate-off / vol-set tail that
    // flushes at frame-0 start, before the first CIA play IRQ fires). They
    // are NOT part of any play() and their count differs between orig and a
    // rebuild with a different init length — so they are dropped, once, from
    // the very first chunk. Pre-entry writes in LATER frames are legitimate
    // straddle tails (a play that began in the prior frame) and are kept.
    bool firstIrqChunkPending = true;

    FILE* pcTraceFile = nullptr;
    for (int frame = 0; frame < totalFrames; frame++) {
        if (pc_trace_path) {
            if (frame == pc_trace_start_frame) {
                pcTraceFile = fopen(pc_trace_path, "w");
                if (pcTraceFile) engine.debug(true, pcTraceFile);
            } else if (frame == pc_trace_end_frame) {
                engine.debug(false, nullptr);
                if (pcTraceFile) { fclose(pcTraceFile); pcTraceFile = nullptr; }
            }
        }
        if (digi || writelog) {
            for (int c = 0; c < nChips; c++)
                engine.clearWriteLog(c);
        }
        if (memtrace) {
            engine.clearReadLog();
        }

        int samples = engine.play(cyclesPerFrame);
        if (samples < 0) {
            fprintf(stderr, "Error at frame %d: %s\n", frame, engine.error());
            break;
        }

        // In memtrace mode, output reads instead of registers
        if (memtrace) {
            const auto& rlog = engine.getReadLog();
            if (!rlog.empty()) {
                printf("F%d", frame);
                for (const auto& r : rlog) {
                    printf(" %04X=%02X", r.addr, r.value);
                }
                printf("\n");
            }
            anyNonZero = true;
            continue;
        }

        // Read current SID register state
        engine.getSidStatus(0, regs);

        // Output the 25 writable registers
        for (int r = 0; r < NUM_REGS; r++) {
            if (r > 0) printf(",");
            printf("%02X", regs[r]);
            if (regs[r] != 0) anyNonZero = true;
        }

        // Append digi writes if any register was written more than once
        if (digi && !writelog) {
            mergeWriteLogs();
            const auto& log = mergedLog;
            int writeCounts[0x60] = {};
            for (const auto& w : log) {
                writeCounts[w.reg]++;
            }
            bool hasMultiWrites = false;
            for (int r = 0; r < 0x60; r++) {
                if (writeCounts[r] > 1) { hasMultiWrites = true; break; }
            }
            if (hasMultiWrites) {
                printf("|D");
                for (const auto& w : log) {
                    if (writeCounts[w.reg] > 1) {
                        printf(":%u:%02X:%02X", w.cycle, w.reg, w.value);
                    }
                }
            }
        }

        // Append per-frame memwatch snapshot of requested RAM addresses
        if (!memwatch_addrs.empty()) {
            printf("|M");
            for (uint16_t a : memwatch_addrs) {
                printf(":%04X=%02X", a, engine.peekRam(a));
            }
            // Per-frame PSID play() invocation count (Trap C diagnostic).
            // Normally 1; 0 or 2+ means siddump's frame bucket is
            // misaligned with engine IRQs.
            printf("|P:%llu", (unsigned long long) engine.getPlayCount());
            engine.clearPlayCount();
            anyNonZero = true;  // memwatch alone counts as "doing something"
        }

        // Append per-frame PC-watch events:
        //   |PW:<pc>:<a>:<x>:<y>:<playidx>:<relwin hex>:<abswin hex>
        if (pcwatch_on) {
            size_t n = engine.getPcWatchEventCount();
            for (size_t e = 0; e < n; e++) {
                auto ev = engine.getPcWatchEvent(e);
                printf("|PW:%04X:%02X:%02X:%02X:%llu:",
                       (unsigned) ev.pc, ev.a, ev.x, ev.y,
                       (unsigned long long) ev.playIdx);
                for (uint8_t b : ev.relWin) printf("%02X", b);
                printf(":");
                for (uint8_t b : ev.absWin) printf("%02X", b);
            }
            engine.clearPcWatchEvents();
            if (n > 0) anyNonZero = true;
        }

        // Append per-frame memwatch-on-write events
        if (memwatch_event_trigger != 0 && !memwatch_event_ram.empty()) {
            size_t n = engine.getMemWatchEventCount();
            for (size_t e = 0; e < n; e++) {
                auto ev = engine.getMemWatchEvent(e);
                printf("|E%zu:%04X=%02X", e, (unsigned) ev.triggerAddr, ev.triggerVal);
                for (size_t k = 0; k < ev.ramSnapshot.size(); k++) {
                    printf(":%04X=%02X",
                           memwatch_event_ram[k], ev.ramSnapshot[k]);
                }
            }
            engine.clearMemWatchEvents();
            if (n > 0) anyNonZero = true;
        }

        // Append full write log. Two encodings:
        //   --writelog: one |W: chunk per siddump frame
        //   --writelog-per-irq: one |I: chunk per PSID play() invocation
        //     (the writes that occurred during that invocation), split
        //     by the play-entry cycle markers. Eliminates Trap C.
        if (writelog) {
            mergeWriteLogs();
            const auto& log = mergedLog;
            if (writelog_per_irq) {
                const auto& irqCycles = engine.getPlayEntryCycles();
                // Play-entry cycles are ABSOLUTE (PHI1 clock); write-log
                // cycles are RELATIVE to the per-frame base. Bring the
                // entries into the write-log origin before comparing.
                uint64_t base = engine.getWriteLogCycleBase(0);
                auto rel = [base](uint64_t abs) -> uint64_t {
                    return abs > base ? abs - base : 0;
                };
                if (perirq_debug && !irqCycles.empty()) {
                    fprintf(stderr, "[per-irq] frame=%d base=%llu "
                            "nentries=%zu entry0=%llu rel0=%llu "
                            "nwrites=%zu w0=%u w1=%u w2=%u\n",
                            frame, (unsigned long long) base,
                            irqCycles.size(),
                            (unsigned long long) irqCycles[0],
                            (unsigned long long) rel(irqCycles[0]),
                            log.size(),
                            log.size() > 0 ? log[0].cycle : 0,
                            log.size() > 1 ? log[1].cycle : 0,
                            log.size() > 2 ? log[2].cycle : 0);
                }
                // Each IRQ's writes = log entries whose cycle is between
                // this IRQ entry and the next (or end of log).
                size_t idx = 0;
                // Drop the init prefix: writes before the global first
                // play() entry (frame-0 chunk only — see firstIrqChunkPending).
                if (firstIrqChunkPending && !irqCycles.empty()) {
                    uint64_t firstEntry = rel(irqCycles[0]);
                    while (idx < log.size() && log[idx].cycle < firstEntry)
                        ++idx;
                    firstIrqChunkPending = false;
                }
                for (size_t i = 0; i < irqCycles.size(); i++) {
                    uint64_t end = (i + 1 < irqCycles.size())
                        ? rel(irqCycles[i + 1])
                        : UINT64_MAX;
                    printf("|I");
                    while (idx < log.size() && log[idx].cycle < end) {
                        printf(":%u:%02X:%02X",
                               log[idx].cycle, log[idx].reg, log[idx].value);
                        ++idx;
                    }
                }
                // A frame with writes but NO play entry (possible when the
                // CIA period exceeds the 50 Hz frame) holds the straddle tail
                // of a play that entered in the prior frame. Emit it as a
                // continuation chunk so no write is ever silently dropped —
                // unless we have not yet seen the first play (firstIrqChunk
                // Pending), in which case these are still init writes.
                if (irqCycles.empty() && !firstIrqChunkPending
                        && idx < log.size()) {
                    printf("|I");
                    while (idx < log.size()) {
                        printf(":%u:%02X:%02X",
                               log[idx].cycle, log[idx].reg, log[idx].value);
                        ++idx;
                    }
                }
                engine.clearPlayEntryCycles();
            } else if (!log.empty()) {
                printf("|W");
                for (const auto& w : log) {
                    printf(":%u:%02X:%02X", w.cycle, w.reg, w.value);
                }
            }
        }

        printf("\n");
    }

    if (!anyNonZero) {
        fprintf(stderr, "Silent tune (all registers zero): %s\n", filename);
        return 2;
    }

    return 0;
}
