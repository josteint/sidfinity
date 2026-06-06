/*
 * This file is part of libsidplayfp, a SID player engine.
 *
 *  Copyright (C) 2012-2026 Leandro Nini
 *
 *  Modified by SIDfinity: added memory read tracing for player analysis.
 */

#ifndef C64CPU_H
#define C64CPU_H

#ifdef HAVE_CONFIG_H
#  include "config.h"
#endif

#include "c64/mmu.h"
#include "CPU/mos6510.h"

#include "sidcxx11.h"

#include <cstdint>
#include <vector>
#include <functional>

namespace libsidplayfp
{

/**
 * Record of a single CPU memory read from the data area.
 */
struct MemRead {
    uint16_t addr;    // address read from
    uint8_t  value;   // value read
};

class c64cpubus final : public CPUDataBus
{
private:
    MMU &m_mmu;

    bool m_traceEnabled = false;
    uint16_t m_traceMinAddr = 0;    // only trace reads >= this address
    uint16_t m_traceMaxAddr = 0xCFFF; // only trace reads <= this address

    // Play-vector entry counter (Trap C diagnostic for siddump).
    // Counts CPU reads at the PSID play vector address — a proxy for
    // "how many times has the play() vector been invoked." See
    // feedback_verification_modes.md (Trap C). When non-zero,
    // m_playAddr is the watched address.
    uint16_t m_playAddr = 0;
    uint64_t m_playCount = 0;

public:
    std::vector<MemRead> readLog;

    // Enable/disable memory read tracing for a specific address range.
    // Typical usage: trace reads from the data area (after player code)
    // up to $CFFF (before I/O at $D000).
    void enableReadTrace(bool enable, uint16_t minAddr = 0, uint16_t maxAddr = 0xCFFF)
    {
        m_traceEnabled = enable;
        m_traceMinAddr = minAddr;
        m_traceMaxAddr = maxAddr;
    }

    void clearReadLog() { readLog.clear(); }

    const std::vector<MemRead>& getReadLog() const { return readLog; }

    // Play-vector tracking. Set the PSID play() vector address (from
    // SidTuneInfo::playAddr()); after each engine.play() call, query
    // getPlayCount() to learn how many IRQs invoked the play vector
    // during the call. Used to detect Trap C (state_diff alignment).
    void setPlayAddr(uint16_t addr) { m_playAddr = addr; }
    uint64_t getPlayCount() const { return m_playCount; }
    void clearPlayCount() { m_playCount = 0; }

protected:
    uint8_t cpuRead(uint_least16_t addr) override
    {
        uint8_t val = m_mmu.cpuRead(addr);
        if (m_traceEnabled && addr >= m_traceMinAddr && addr <= m_traceMaxAddr)
        {
            readLog.push_back({static_cast<uint16_t>(addr), val});
        }
        // Count reads at the PSID play vector — proxy for IRQ invocations
        // of play(). Each opcode-fetch at PC=playAddr fires this; in
        // practice the engine code never reads its own play vector
        // address as data so the count is accurate.
        if (m_playAddr != 0 && addr == m_playAddr)
        {
            ++m_playCount;
        }
        return val;
    }

    void cpuWrite(uint_least16_t addr, uint8_t data) override
    {
        m_mmu.cpuWrite(addr, data);
    }

public:
    c64cpubus (MMU &mmu) :
        m_mmu(mmu) {}
};

}

#endif // C64CPU_H
