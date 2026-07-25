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
#include "EventScheduler.h"

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

    // Per-IRQ scheduling: cycle (PHI1 clock) at each play vector entry.
    // Used by siddump --writelog-per-irq to split the writelog stream
    // into per-PSID-play() buckets — KILLS Trap C at the source by
    // aligning observation to engine IRQs instead of siddump frame
    // boundaries.
    EventScheduler *m_scheduler = nullptr;
    std::vector<uint64_t> m_playEntryCycles;

    // Memwatch-on-event state.
    uint16_t m_eventWriteAddr = 0;
    std::vector<uint16_t> m_eventRamAddrs;

    // Reinit-ghost snapshot state (SIDfinity). See setReinitSnapshot().
    // Captures a RAM window at two play()-vector-entry-aligned moments so a
    // C19 shape-B $FF-reinit ghost extraction reads from ground truth
    // (libsidplayfp) instead of py65 (whose power-on / environment fill can
    // diverge — see feedback_ground_truth.md). Both snapshots align to play
    // vector ENTRIES (not siddump frames), so they are robust to Trap C.
    uint16_t m_reinitTrigPC = 0;        // wedge PC; 0 = disabled
    uint16_t m_reinitLo = 0;
    uint16_t m_reinitHi = 0;
    bool m_reinitTrigSeen = false;      // wedge PC has been EXECUTED
    uint16_t m_reinitLastRead = 0;      // consecutive-read run tracker
    uint8_t m_reinitRun = 0;            //   (execution-vs-data discriminator)
    bool m_reinitColdDone = false;      // COLD window captured
    bool m_reinitWarmDone = false;      // WARM window captured
    std::vector<uint8_t> m_reinitCold;
    std::vector<uint8_t> m_reinitWarm;

    void snapshotReinitWindow(std::vector<uint8_t>& out)
    {
        out.clear();
        out.reserve(static_cast<size_t>(m_reinitHi - m_reinitLo) + 1);
        for (uint32_t a = m_reinitLo; a <= m_reinitHi; ++a)
            out.push_back(m_mmu.readMemByte(static_cast<uint16_t>(a)));
    }

public:
    // EventRecord declared early so m_eventLog (private) can reference it.
    struct EventRecord {
        uint16_t triggerAddr;
        uint8_t triggerVal;
        std::vector<uint8_t> ramSnapshot;
    };
private:
    std::vector<EventRecord> m_eventLog;

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

    // Scheduler setter — wires PHI1 cycle access for per-IRQ markers.
    // c64.cpp calls this once after construction.
    void setScheduler(EventScheduler* s) { m_scheduler = s; }

    // Per-IRQ markers — cycles at which the play vector was entered.
    // Used by siddump --writelog-per-irq to split writes by IRQ.
    const std::vector<uint64_t>& getPlayEntryCycles() const
    { return m_playEntryCycles; }
    void clearPlayEntryCycles() { m_playEntryCycles.clear(); }

    // Memwatch-on-event: snapshot specified RAM addresses every time
    // the CPU writes to a trigger address. Use case: "show me the
    // engine state at every write to $D404" for SMC / conditional-
    // update investigations. Per-event records exposed via
    // getEventLog().
    void setMemWatchOnWrite(uint16_t triggerAddr,
                             const std::vector<uint16_t>& ramAddrs)
    {
        m_eventWriteAddr = triggerAddr;
        m_eventRamAddrs = ramAddrs;
    }
    const std::vector<EventRecord>& getEventLog() const { return m_eventLog; }
    void clearEventLog() { m_eventLog.clear(); }

    // Reinit-ghost snapshot: capture RAM[lo..hi] at two play()-vector-entry-
    // aligned moments, to reproduce the C19 shape-B $FF-reinit ghost pokes
    // from ground truth instead of py65:
    //   COLD = the window at the FIRST play-vector entry (post-init, before
    //          any play body runs) — the clean baseline.
    //   WARM = the window at the first play-vector entry AFTER trigPC (the
    //          reinit wedge) has executed — i.e. at the END of the play()
    //          that ran the ghost reinit (matching py65's play()-end capture).
    // Aligning both to play-vector entries (reusing the play counter's
    // opcode-fetch proxy) makes them independent of siddump frame bucketing
    // (Trap C). Observe-only: only READS RAM, never writes emulated state.
    // Requires setPlayAddr() to have been called (the play-entry proxy).
    void setReinitSnapshot(uint16_t trigPC, uint16_t lo, uint16_t hi)
    {
        m_reinitTrigPC = trigPC;
        m_reinitLo = lo;
        m_reinitHi = hi;
    }
    bool reinitColdDone() const { return m_reinitColdDone; }
    bool reinitWarmDone() const { return m_reinitWarmDone; }
    const std::vector<uint8_t>& reinitCold() const { return m_reinitCold; }
    const std::vector<uint8_t>& reinitWarm() const { return m_reinitWarm; }

    // Side-effect-free CPU-eye read (through the MMU: banked ROM + 6510
    // port visible; no trace/play-counter bookkeeping).
    uint8_t peek(uint_least16_t addr) { return m_mmu.cpuRead(addr); }

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
            if (m_scheduler)
            {
                m_playEntryCycles.push_back(
                    m_scheduler->getTime(EVENT_CLOCK_PHI1));
            }
            // Reinit-ghost snapshots are aligned to play-vector entries.
            if (m_reinitTrigPC != 0)
            {
                if (!m_reinitColdDone)
                {
                    snapshotReinitWindow(m_reinitCold);   // first entry = COLD
                    m_reinitColdDone = true;
                }
                else if (m_reinitTrigSeen && !m_reinitWarmDone)
                {
                    // First entry after the wedge fired = end of the reinit
                    // play() = WARM.
                    snapshotReinitWindow(m_reinitWarm);
                    m_reinitWarmDone = true;
                }
            }
        }
        // Reinit wedge detection. The bus cannot tell an opcode fetch from a
        // data read, and the wedge PC IS read as data during normal play
        // (For_Party: a table walk reads $10DD at frame 200, ~9600 frames
        // before the reinit executes it) — so a bare addr==trigPC check
        // false-fires. Discriminate EXECUTION by its bus signature: executing
        // the wedge (`LDA #imm / JMP abs`) produces >=3 consecutive ascending
        // reads (opcode, operand, next opcode) with no intervening read,
        // while a data walk always interleaves its own instruction fetches
        // (an indirect-pointer read yields only a 2-run; an RMW dummy re-read
        // repeats the same address and resets the run). Known miss window:
        // an IRQ landing exactly between the wedge's two instructions breaks
        // the run — the extract's py65 fallback covers that (rare) case.
        if (m_reinitTrigPC != 0 && !m_reinitTrigSeen)
        {
            if (addr == static_cast<uint16_t>(m_reinitLastRead + 1))
            {
                if (m_reinitRun < 0xFF) ++m_reinitRun;
            }
            else
            {
                m_reinitRun = 1;
            }
            m_reinitLastRead = static_cast<uint16_t>(addr);
            if (m_reinitRun >= 3 &&
                addr == static_cast<uint16_t>(m_reinitTrigPC + 2))
            {
                m_reinitTrigSeen = true;
            }
        }
        return val;
    }

    void cpuWrite(uint_least16_t addr, uint8_t data) override
    {
        m_mmu.cpuWrite(addr, data);
        // Memwatch-on-event: if write target matches the watch trigger,
        // snapshot all configured RAM addresses right now.
        if (m_eventWriteAddr != 0 && addr == m_eventWriteAddr)
        {
            EventRecord ev;
            ev.triggerAddr = static_cast<uint16_t>(addr);
            ev.triggerVal = data;
            ev.ramSnapshot.reserve(m_eventRamAddrs.size());
            for (uint16_t a : m_eventRamAddrs)
            {
                ev.ramSnapshot.push_back(m_mmu.readMemByte(a));
            }
            m_eventLog.push_back(std::move(ev));
        }
    }

public:
    c64cpubus (MMU &mmu) :
        m_mmu(mmu) {}
};

}

#endif // C64CPU_H
