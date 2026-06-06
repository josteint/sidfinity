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
 *   --subtune N    Select subtune (default: start song)
 *   --duration N   Duration in seconds (default: 60)
 *   --timeout N    Timeout in seconds (default: 0 = no timeout)
 *   --raw          Skip metadata/header lines
 *   --digi         Enable intra-frame write logging
 */

#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
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
            "  --subtune N    Select subtune (default: start song)\n"
            "  --duration N   Duration in seconds (default: 60)\n"
            "  --timeout N    Timeout in seconds (default: 0 = none)\n"
            "  --raw          Skip metadata/header lines\n"
            "  --digi         Enable intra-frame write logging\n"
            "  --writelog     Append full register write stream with cycle timing (ground truth)\n"
            "  --writelog-per-irq  Like --writelog, but each output line is ONE PSID play()\n"
            "                      invocation (not one siddump frame). Eliminates Trap C from\n"
            "                      observation. Implies --writelog. Output prefix changes from\n"
            "                      |W: to |I: to flag the per-IRQ encoding.\n"
            "  --memtrace     Append memory access trace\n"
            "  --pcm          Output raw 16-bit signed PCM to stdout\n"
            "  --force-rsid   Process RSID files (normally skipped)\n"
            "  --pc-trace FILE START END  Dump CPU PC trace to FILE for frames START..END\n"
            "  --memwatch HEX[,HEX...]    Per-frame snapshot of RAM at these addresses (post-play)\n"
            "                             (e.g. --memwatch 90C5,90C8,90CB,9116). Output lines:\n"
            "                             M<frame>:<addr>=<val>[:<addr>=<val>...]\n"
            "                             When --memwatch is on, also emits |P:<count> giving the\n"
            "                             number of PSID play() invocations that fired in this\n"
            "                             siddump frame. Used to diagnose Trap C alignment.\n"
            "  --memwatch-on-write HEX HEX[,HEX...]  Event-driven memwatch. First HEX is the\n"
            "                             trigger address (e.g. D404). The remaining list is the\n"
            "                             RAM addresses to snapshot every time the CPU writes to\n"
            "                             the trigger. Emits one E<idx>:<trigger=val>:<addr=val>...\n"
            "                             line per event. Use for SMC / conditional-update traces.\n",
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
    bool memtrace = false;
    bool pcm = false;
    bool force_rsid = false;
    const char* pc_trace_path = nullptr;
    int pc_trace_start_frame = -1;
    int pc_trace_end_frame = -1;
    std::vector<uint16_t> memwatch_addrs;
    uint16_t memwatch_event_trigger = 0;     // 0 = disabled
    std::vector<uint16_t> memwatch_event_ram;

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
        } else if (strcmp(argv[i], "--memtrace") == 0) {
            memtrace = true;
        } else if (strcmp(argv[i], "--pcm") == 0) {
            pcm = true;
        } else if (strcmp(argv[i], "--force-rsid") == 0) {
            force_rsid = true;
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
        } else if (strcmp(argv[i], "--subtune") == 0 && i + 1 < argc) {
            subtune = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--duration") == 0 && i + 1 < argc) {
            seconds = atof(argv[++i]);
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout = atoi(argv[++i]);
        } else if (atoi(argv[i]) > 0) {
            // Legacy positional: first number = subtune, second = seconds
            if (subtune == 0) subtune = atoi(argv[i]);
            else seconds = atoi(argv[i]);
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

    // Skip multi-SID files
    if (info->sidChips() > 1) {
        fprintf(stderr, "Skipping multi-SID (%d chips): %s\n", info->sidChips(), filename);
        return 3;
    }

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

    // Enable write logging if requested
    if (digi || writelog) {
        engine.enableWriteLog(0, true);
    }

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

    // Initialize mixer (needed for play() to work)
    engine.initMixer(false); // mono

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
            engine.clearWriteLog(0);
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
            const auto& log = engine.getWriteLog(0);
            int writeCounts[32] = {};
            for (const auto& w : log) {
                writeCounts[w.reg]++;
            }
            bool hasMultiWrites = false;
            for (int r = 0; r < NUM_REGS; r++) {
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
            const auto& log = engine.getWriteLog(0);
            if (writelog_per_irq) {
                const auto& irqCycles = engine.getPlayEntryCycles();
                // Each IRQ's writes = log entries whose cycle is between
                // this IRQ entry and the next (or end of log).
                size_t idx = 0;
                for (size_t i = 0; i < irqCycles.size(); i++) {
                    uint64_t end = (i + 1 < irqCycles.size())
                        ? irqCycles[i + 1]
                        : UINT64_MAX;
                    printf("|I");
                    while (idx < log.size() && log[idx].cycle < end) {
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
