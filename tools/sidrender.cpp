/*
 * sidrender - Render a SID file to raw 16-bit signed PCM (mono, 48kHz)
 *
 * Output goes to stdout as raw PCM bytes (little-endian int16).
 * Pipe to a file or another tool for analysis.
 *
 * Usage: sidrender <file.sid> [options]
 *   --subtune N    Select subtune (default: start song)
 *   --duration N   Duration in seconds (default: 10)
 *   --timeout N    Timeout in seconds (default: 0 = none)
 *
 * Exit codes:
 *   0 = success
 *   1 = error
 *   2 = silent
 *   3 = skipped (RSID or multi-SID)
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
#include "sidlite.h"

static void timeout_handler(int) { _exit(4); }

int main(int argc, char* argv[])
{
    if (argc < 2) {
        fprintf(stderr,
            "Usage: %s <file.sid> [options]\n"
            "  --subtune N    Select subtune (default: start song)\n"
            "  --duration N   Duration in seconds (default: 10)\n"
            "  --timeout N    Timeout in seconds (default: 0 = none)\n"
            "\nOutputs raw 16-bit signed LE mono PCM at 48kHz to stdout.\n",
            argv[0]);
        return 1;
    }

    const char* filename = argv[1];
    int subtune = 0;
    int seconds = 10;
    int timeout = 0;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--subtune") == 0 && i + 1 < argc) {
            subtune = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--duration") == 0 && i + 1 < argc) {
            seconds = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout = atoi(argv[++i]);
        }
    }

    if (timeout > 0) {
        signal(SIGALRM, timeout_handler);
        alarm(timeout);
    }

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

    if (info->compatibility() == SidTuneInfo::COMPATIBILITY_R64) {
        fprintf(stderr, "Skipping RSID: %s\n", filename);
        return 3;
    }

    if (info->sidChips() > 1) {
        fprintf(stderr, "Skipping multi-SID (%d chips): %s\n", info->sidChips(), filename);
        return 3;
    }

    if (subtune == 0) subtune = info->startSong();
    tune.selectSong(subtune);

    info = tune.getInfo();
    bool isPAL = (info->clockSpeed() != SidTuneInfo::CLOCK_NTSC);

    sidplayfp engine;
    SIDLiteBuilder builder("SIDLite");

    SidConfig cfg;
    cfg.defaultC64Model = isPAL ? SidConfig::PAL : SidConfig::NTSC;
    cfg.defaultSidModel = SidConfig::MOS6581;
    cfg.frequency = 48000;
    cfg.sidEmulation = &builder;
    cfg.powerOnDelay = 0;

    if (!engine.config(cfg)) {
        fprintf(stderr, "Error configuring engine: %s\n", engine.error());
        return 1;
    }

    if (!engine.load(&tune)) {
        fprintf(stderr, "Error loading tune: %s\n", engine.error());
        return 1;
    }

    unsigned int cyclesPerFrame = isPAL ? (63 * 312 + 32) : (65 * 263 + 32);
    int fps = isPAL ? 50 : 60;
    int totalFrames = seconds * fps;

    engine.initMixer(false); // mono

    // Allocate mix buffer (max samples per frame at 48kHz/50fps = 960 + margin)
    std::vector<short> mixbuf(2048);
    bool anyNonZero = false;

    for (int frame = 0; frame < totalFrames; frame++) {
        int samples = engine.play(cyclesPerFrame);
        if (samples < 0) {
            fprintf(stderr, "Error at frame %d: %s\n", frame, engine.error());
            break;
        }
        if (samples == 0) continue;

        if ((unsigned)samples > mixbuf.size()) {
            mixbuf.resize(samples);
        }

        unsigned int mixed = engine.mix(mixbuf.data(), samples);
        if (mixed > 0) {
            fwrite(mixbuf.data(), sizeof(short), mixed, stdout);
            if (!anyNonZero) {
                for (unsigned int i = 0; i < mixed; i++) {
                    if (mixbuf[i] != 0) { anyNonZero = true; break; }
                }
            }
        }
    }

    if (!anyNonZero) {
        fprintf(stderr, "Silent tune: %s\n", filename);
        return 2;
    }

    return 0;
}
