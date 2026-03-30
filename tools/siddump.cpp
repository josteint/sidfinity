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
            "  --digi         Enable intra-frame write logging\n",
            argv[0]);
        return 1;
    }

    const char* filename = argv[1];
    int subtune = 0;
    int seconds = 60;
    int timeout = 0;
    bool raw = false;
    bool digi = false;
    bool writelog = false;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--raw") == 0) {
            raw = true;
        } else if (strcmp(argv[i], "--digi") == 0) {
            digi = true;
        } else if (strcmp(argv[i], "--writelog") == 0) {
            writelog = true;
        } else if (strcmp(argv[i], "--subtune") == 0 && i + 1 < argc) {
            subtune = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--duration") == 0 && i + 1 < argc) {
            seconds = atoi(argv[++i]);
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

    // Skip RSID files
    if (info->compatibility() == SidTuneInfo::COMPATIBILITY_R64) {
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

    // Cycles per frame: use the VIC raster frame length plus a small margin
    // to ensure exactly one VBI fires per play() call.
    // PAL:  63 cycles/line × 312 lines = 19656, + margin
    // NTSC: 65 cycles/line × 263 lines = 17095, + margin
    // The margin ensures we always cross the raster trigger point.
    unsigned int cyclesPerFrame = isPAL ? (63 * 312 + 32) : (65 * 263 + 32);

    int totalFrames = seconds * fps;

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

    // Initialize mixer (needed for play() to work)
    engine.initMixer(false); // mono

    // Run frame by frame and dump registers
    uint8_t regs[32];
    bool anyNonZero = false;

    for (int frame = 0; frame < totalFrames; frame++) {
        if (digi || writelog) {
            engine.clearWriteLog(0);
        }

        int samples = engine.play(cyclesPerFrame);
        if (samples < 0) {
            fprintf(stderr, "Error at frame %d: %s\n", frame, engine.error());
            break;
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

        // Append full write log (all writes with cycle timing)
        if (writelog) {
            const auto& log = engine.getWriteLog(0);
            if (!log.empty()) {
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
