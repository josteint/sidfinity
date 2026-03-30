/*
 * This file is part of libsidplayfp, a SID player engine.
 *
 * Copyright 2013-2024 Leandro Nini <drfiemost@users.sourceforge.net>
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

#ifndef C64SID_H
#define C64SID_H

#include "Banks/Bank.h"
#include "EventScheduler.h"

#include "sidcxx11.h"

#include <algorithm>
#include <iterator>
#include <cstring>
#include <cstdint>
#include <vector>

namespace libsidplayfp
{

/**
 * Record of a single SID register write with cycle timing.
 */
struct SidWrite {
    uint32_t cycle;      // cycle offset within frame (PHI1 clocks)
    uint8_t  reg;        // register 0x00-0x1f
    uint8_t  value;
};

/**
 * SID interface.
 */
class c64sid : public Bank
{
private:
    uint8_t lastpoke[0x20];

    bool m_logEnabled = false;
    uint32_t m_cycleBase = 0;
    EventScheduler *m_scheduler = nullptr;

public:
    std::vector<SidWrite> writeLog;

protected:
    virtual ~c64sid() = default;

    virtual uint8_t read(uint_least8_t addr) = 0;
    virtual void writeReg(uint_least8_t addr, uint8_t data) = 0;

    virtual void reset(uint8_t volume) = 0;

public:
    void reset()
    {
        std::fill(std::begin(lastpoke), std::end(lastpoke), 0);
        m_logEnabled = false;
        m_cycleBase = 0;
        writeLog.clear();
        reset(0xf);
    }

    /// Set the event scheduler for accurate cycle timing in write logs.
    void setEventScheduler(EventScheduler *scheduler) { m_scheduler = scheduler; }

    // Write logging control
    void enableWriteLog(bool enable) { m_logEnabled = enable; }

    void clearWriteLog()
    {
        writeLog.clear();
        if (m_scheduler)
            m_cycleBase = static_cast<uint32_t>(m_scheduler->getTime(EVENT_CLOCK_PHI1));
        else
            m_cycleBase = 0;
    }

    const std::vector<SidWrite>& getWriteLog() const { return writeLog; }

    // Bank functions
    void poke(uint_least16_t address, uint8_t value) override
    {
        const uint8_t reg = address & 0x1f;
        lastpoke[reg] = value;
        if (m_logEnabled) {
            uint32_t cycle = 0;
            if (m_scheduler)
                cycle = static_cast<uint32_t>(m_scheduler->getTime(EVENT_CLOCK_PHI1)) - m_cycleBase;
            writeLog.push_back({cycle, reg, value});
        }
        writeReg(reg, value);
    }
    uint8_t peek(uint_least16_t address) override { return read(address & 0x1f); }

    void getStatus(uint8_t regs[0x20]) const { std::memcpy(regs, lastpoke, 0x20); }
};

}

#endif // C64SID_H
