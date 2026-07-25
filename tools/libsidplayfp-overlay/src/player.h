/*
 * This file is part of libsidplayfp, a SID player engine.
 *
 * Copyright 2011-2025 Leandro Nini <drfiemost@users.sourceforge.net>
 * Copyright 2007-2010 Antti Lankila
 * Copyright 2000-2001 Simon White
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */


#ifndef PLAYER_H
#define PLAYER_H

#include <cstdint>
#include <cstdio>

#include "sidplayfp/siddefs.h"
#include "sidplayfp/SidConfig.h"
#include "sidplayfp/SidTuneInfo.h"

#include "SidInfoImpl.h"
#include "sidrandom.h"
#include "simpleMixer.h"
#include "c64/c64.h"

#ifdef HAVE_CONFIG_H
#  include "config.h"
#endif

#include <atomic>
#include <memory>
#include <vector>

class SidTune;
class SidInfo;
class sidbuilder;


namespace libsidplayfp
{

class sidemu;

class Player
{
private:
    /// Commodore 64 emulator
    c64 m_c64;

    /// Emulator info
    SidTune *m_tune;

    /// User Configuration Settings
    SidInfoImpl m_info;

    /// User Configuration Settings
    SidConfig m_cfg;

    /// Error message
    std::string m_errorString;

    sidrandom m_rand;

    uint_least32_t m_startTime = 0;

    /// PAL/NTSC switch value
    uint8_t m_videoSwitch;

    std::vector<sidemu*> m_chips;

    std::unique_ptr<SimpleMixer> m_simpleMixer;

private:
    /**
     * Get the C64 model for the current loaded tune.
     *
     * @param defaultModel the default model
     * @param forced true if the default model shold be forced in spite of tune model
     */
    c64::model_t c64model(SidConfig::c64_model_t defaultModel, bool forced);

    /**
     * Initialize the emulation.
     *
     * @throw configError
     */
    void initialise();

    /**
     * Release the SID builders.
     */
    void sidRelease();

    /**
     * Create the SID emulation(s).
     *
     * @throw configError
     */
    void sidCreate(sidbuilder *builder, SidConfig::sid_model_t defaultModel, bool digiboost,
                    bool forced, const std::vector<unsigned int> &extraSidAddresses);

    /**
     * Set the SID emulation parameters.
     *
     * @param cpuFreq the CPU clock frequency
     * @param frequency the output sampling frequency
     * @param sampling the sampling method to use
     */
    void sidParams(double cpuFreq, int frequency,
                    SidConfig::sampling_method_t sampling);

    inline void run(unsigned int events);

public:
    Player();
    ~Player() = default;

    const SidConfig &config() const { return m_cfg; }

    const SidInfo &info() const { return m_info; }

    bool config(const SidConfig &cfg, bool force=false);

    bool load(SidTune *tune);

    void buffers(short** buffers) const;

    int play(unsigned int cycles);

    uint_least32_t timeMs() const { return m_c64.getTimeMs() - m_startTime; }

    void debug(const bool enable, FILE *out) { m_c64.debug(enable, out); }

    void mute(unsigned int sidNum, unsigned int voice, bool enable);

    void filter(unsigned int sidNum, bool enable);

    const char *error() const { return m_errorString.c_str(); }

    void setKernal(const uint8_t* rom);
    void setBasic(const uint8_t* rom);
    void setChargen(const uint8_t* rom);

    uint_least16_t getCia1TimerA() const { return m_c64.getCia1TimerA(); }

    bool getSidStatus(unsigned int sidNum, uint8_t regs[32]);

    bool enableWriteLog(unsigned int sidNum, bool enable);
    bool clearWriteLog(unsigned int sidNum);
    const std::vector<libsidplayfp::SidWrite>* getWriteLog(unsigned int sidNum);
    uint32_t getWriteLogCycleBase(unsigned int sidNum);

    void enableReadTrace(bool enable, uint16_t minAddr = 0, uint16_t maxAddr = 0xCFFF)
    { m_c64.getCpuBus().enableReadTrace(enable, minAddr, maxAddr); }
    void clearReadLog() { m_c64.getCpuBus().clearReadLog(); }
    const std::vector<libsidplayfp::MemRead>& getReadLog() const
    { return m_c64.getCpuBus().getReadLog(); }

    uint8_t peekRam(uint16_t addr) { return m_c64.getMemInterface().readMemByte(addr); }

    // Play-vector entry counter (Trap C diagnostic — see
    // feedback_verification_modes.md). Set the play vector address
    // (e.g. from SidTuneInfo::playAddr()); after each play() call,
    // query getPlayCount() to learn how many IRQs entered the
    // play vector during the call. Used by siddump --memwatch to
    // detect IRQ-count drift between mine and orig.
    void setPlayAddr(uint16_t addr) { m_c64.getCpuBus().setPlayAddr(addr); }
    uint64_t getPlayCount() const { return m_c64.getCpuBus().getPlayCount(); }
    void clearPlayCount() { m_c64.getCpuBus().clearPlayCount(); }

    // Per-IRQ play-entry cycles — PHI1 clocks at each play vector entry.
    // Used by siddump --writelog-per-irq to split the writelog stream
    // into per-PSID-play() buckets, eliminating Trap C at the source.
    const std::vector<uint64_t>& getPlayEntryCycles() const
    { return m_c64.getCpuBus().getPlayEntryCycles(); }
    void clearPlayEntryCycles() { m_c64.getCpuBus().clearPlayEntryCycles(); }

    // CPU-eye byte read (through the MMU: banked ROM + 6510 port visible).
    uint8_t cpuPeek(uint_least16_t addr)
    { return m_c64.getCpuBus().peek(addr); }

    // Memwatch-on-event: see c64cpubus::setMemWatchOnWrite.
    void setMemWatchOnWrite(uint16_t triggerAddr,
                             const std::vector<uint16_t>& ramAddrs)
    { m_c64.getCpuBus().setMemWatchOnWrite(triggerAddr, ramAddrs); }
    const std::vector<libsidplayfp::c64cpubus::EventRecord>& getEventLog() const
    { return m_c64.getCpuBus().getEventLog(); }
    void clearEventLog() { m_c64.getCpuBus().clearEventLog(); }

    // PC-watch: see c64cpubus::setPcWatch.
    void setPcWatch(const std::vector<uint16_t>& exactPCs,
                    const std::vector<uint8_t>& lowBytes,
                    uint16_t before, uint16_t after, bool firstOnly,
                    uint32_t absLo = 1, uint32_t absHi = 0)
    { m_c64.getCpuBus().setPcWatch(exactPCs, lowBytes, before, after,
                                   firstOnly, absLo, absHi); }
    const std::vector<libsidplayfp::c64cpubus::PcWatchEvent>&
    getPcWatchEvents() const
    { return m_c64.getCpuBus().getPcWatchEvents(); }
    void clearPcWatchEvents() { m_c64.getCpuBus().clearPcWatchEvents(); }

    // Reinit-ghost snapshot: see c64cpubus::setReinitSnapshot.
    void setReinitSnapshot(uint16_t trigPC, uint16_t lo, uint16_t hi)
    { m_c64.getCpuBus().setReinitSnapshot(trigPC, lo, hi); }
    bool reinitColdDone() const { return m_c64.getCpuBus().reinitColdDone(); }
    bool reinitWarmDone() const { return m_c64.getCpuBus().reinitWarmDone(); }
    const std::vector<uint8_t>& reinitCold() const
    { return m_c64.getCpuBus().reinitCold(); }
    const std::vector<uint8_t>& reinitWarm() const
    { return m_c64.getCpuBus().reinitWarm(); }

    unsigned int installedSIDs() const { return m_chips.size(); }

    void initMixer(bool stereo);

    unsigned int mix(short *buffer, unsigned int samples);

    bool reset();

    int getBufSize(unsigned int cycles);
};

}

#endif // PLAYER_H
