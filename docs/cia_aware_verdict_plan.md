# Plan: CIA-aware per-play() verdict for `verify_all`

**Status:** designed, not implemented. Engine side is DONE (Human_Race is
proven byte-exact). This plan fixes only the VERIFICATION TOOLING so CIA-timed
Hubbard tunes (Human_Race, Battle_of_Britain) verify correctly.

**Read first:** `.claude/memory/project_hubbard_remaining_partials.md` and
`.claude/memory/feedback_no_snapshot_verdict.md`. Then re-read the CORE TENET +
"two verification modes" in `CLAUDE.md`.

---

## 1. Why this is needed (the problem, precisely)

After Monty was fixed (commit `a47311f`), `tools/regression.py` reports
**Hubbard 65 ok + 6 regressed**. Of the 6:

- **Devils_Galop (1 sub)** — a GENUINE engine bug (vblank; drops a V3 frequency
  glide write). Out of scope here; leave it failing.
- **Human_Race (4 subs) + Battle_of_Britain (1 sub)** — the ENGINE IS CORRECT.
  Their per-`play()` write sequences are byte-identical to the originals. They
  fail only because they are **CIA-timed** (PSID `speed != 0`) and the verdict's
  capture tool (`siddump --writelog`, flat per-50Hz-frame) cannot compare two
  CIA-phase-shifted captures.

**Proof the HR engine is correct (the validation oracle — re-run to confirm):**
`siddump --pc-trace`, segment by the play-entry PC, extract SID writes per
play() → Human_Race subtune 0 matched the original **54/54 plays**. See §4.

**Why flat `--writelog` fails for CIA tunes:** the original's first `play()`
fires at cycle ~15714 within siddump's first 50Hz frame; the rebuild's fires at
~1403 (different init length → different CIA phase). siddump buckets writes per
50Hz frame, so the init + first-play writes land in different buckets for orig
vs rebuild, and the flat streams "diverge at position 0" even though the
per-`play()` sequences are identical. This is Trap C specialized to CIA tunes.

**Goal:** make `verify_all` compare CIA tunes (`speed != 0`) **per `play()`
invocation** (Mode 1, the tenet's intent) instead of per-50Hz-frame. vblank
tunes (`speed == 0`) keep the existing flat path unchanged.

---

## 2. Root cause of the per-irq tool bug (this is the crux to fix)

`siddump --writelog-per-irq` is SUPPOSED to emit one `|I` chunk per `play()`
invocation, but it is currently broken in a way that makes it effectively
identical to `--writelog` (one chunk per frame). The bug is a **cycle-origin
mismatch**:

- **Write-log cycles** (`tools/libsidplayfp-overlay/src/c64/c64sid.h`, ~line
  105): recorded as `getTime(EVENT_CLOCK_PHI1) - m_cycleBase` — **RELATIVE** to
  a per-frame base. `m_cycleBase` is set in `clearWriteLog()` (c64sid.h ~line
  90) = `getTime()` at frame start.
- **Play-entry cycles** (`tools/libsidplayfp-overlay/src/c64/c64cpu.h`, ~line
  142-143): recorded as `m_scheduler->getTime(EVENT_CLOCK_PHI1)` — **ABSOLUTE**.
  Recorded in `cpuRead()` whenever `addr == m_playAddr` (the play vector).
- **The splitter** (`tools/siddump.cpp`, ~line 462-478) does
  `while (log[idx].cycle < irqCycles[i+1])` — comparing RELATIVE write cycles
  against ABSOLUTE play-entry cycles. Since absolute ≫ relative, the condition
  is ALWAYS true → every write lands in chunk 0, all later chunks are empty.
  **So the per-play split never happens.** (That is why earlier per-IRQ
  analyses gave garbage like "orig chunk0=16, reb chunk0=7" — those were whole
  *frames*, not plays.)

**siddump frame loop order** (so the timing is unambiguous), `tools/siddump.cpp`:
- ~line 369: `engine.clearWriteLog(0)` → sets `m_cycleBase = getTime()` (frame start).
- ~line 375: `engine.play(cyclesPerFrame)` → during play(): writes logged
  (relative), play-entries recorded (absolute).
- ~line 462-478: the `--writelog-per-irq` split + output.
- ~line 478: `engine.clearPlayEntryCycles()` (end of frame).

So within one frame's output, `m_cycleBase` = that frame's start and
`getPlayEntryCycles()` = that frame's entries. The fix is to convert the
absolute entries to the same relative origin: `rel_entry = abs_entry - m_cycleBase`.

---

## 3. The fix (siddump / overlay) — and the open subtlety that sank the first try

### 3a. Plumb `m_cycleBase` out (this part worked; mechanical)
Mirror the existing `getWriteLog` plumbing:
1. `c64sid.h`: add `uint32_t getWriteLogCycleBase() const { return m_cycleBase; }`.
2. `player.h` + `player.cpp` (near `getWriteLog`, ~line 607): add
   `uint32_t Player::getWriteLogCycleBase(unsigned int sidNum)` →
   `m_chips[sidNum]->getWriteLogCycleBase()`.
3. `sidplayfp.h` + `sidplayfp.cpp` (near `getWriteLog`, ~line 144): add
   `uint32_t sidplayfp::getWriteLogCycleBase(unsigned int sidNum)` →
   `sidplayer.getWriteLogCycleBase(sidNum)`.

### 3b. Fix the splitter (`tools/siddump.cpp` ~462-478)
```cpp
const auto& irqCycles = engine.getPlayEntryCycles();
uint64_t base = engine.getWriteLogCycleBase(0);
auto rel = [base](uint64_t abs){ return abs > base ? abs - base : 0; };
size_t idx = 0;
for (size_t i = 0; i < irqCycles.size(); i++) {
    uint64_t end = (i + 1 < irqCycles.size()) ? rel(irqCycles[i+1]) : UINT64_MAX;
    printf("|I");
    while (idx < log.size() && log[idx].cycle < end) {
        printf(":%u:%02X:%02X", log[idx].cycle, log[idx].reg, log[idx].value);
        ++idx;
    }
}
```

### 3c. THE OPEN SUBTLETY — do NOT guess; resolve empirically FIRST
My first attempt ALSO added an "init skip" (`while log.cycle < rel(irqCycles[0]) ++idx`)
and the chunks came out EMPTY. Two unresolved questions caused that; resolve
both with measurements BEFORE writing the splitter logic:

1. **Is the base value actually correct at read time?** Empty chunks imply
   `rel(irqCycles[0])` was huge, i.e. `base` was ~0 (stale/wrong). VERIFY:
   temporarily `fprintf(stderr, ...)` `base`, `irqCycles[0]`, and the first few
   `log[].cycle` for one frame. Confirm `irqCycles[0] - base` lands *among* the
   write cycles (not above all of them). If `base` is 0/wrong, the getter or its
   timing is wrong — fix that before anything else.

2. **Where do the tune's init() writes go?** Unknown whether frame 0's
   write-log contains init writes or only play[0]. `Player::initialise()`
   (`player.cpp:124-189`) runs a powerOnDelay loop + installs the psid driver
   + `resetCpu()` BEFORE the frame loop, but the tune's own init typically runs
   via the driver on the first play(). MEASURE: compare frame-0 write count from
   `--writelog` against pc-trace play[0] write count (§4). If equal → no init in
   the frame-0 log, do NOT skip anything. If frame-0 has extra leading writes →
   they are the writes with `cycle < rel(irqCycles[0])`; only THEN add the
   init-skip, and only for chunk 0.

**Decision rule:** only add an init-skip if the measurement in (2) proves init
writes are present in the frame-0 log. Otherwise the plain splitter in §3b is
correct as-is.

---

## 4. The validation oracle (pc-trace) — the source of truth for §3

This is how HR was proven 54/54; use it to VALIDATE the per-irq fix (the per-irq
chunks MUST equal these pc-trace chunks for both orig and rebuild).

```python
# segment a pc-trace by play-entry PC; extract SID writes via the EFFECTIVE
# address shown in the trace's [d4xx] bracket (handles STA abs / abs,x / abs,y).
import re, subprocess
def perplay(sid, sub, frames, play_entry):   # play_entry: header play addr
    subprocess.run(['tools/siddump', sid, '--subtune', str(sub+1),
                    '--pc-trace', '/tmp/t.txt', '0', str(frames)],
                   capture_output=True)
    rows=[]
    for l in open('/tmp/t.txt'):
        p=l.split()
        if len(p)<5: continue
        try: pc=int(p[0],16); A=int(p[2],16)   # p[0]=PC, p[2]=A, p[3]=X, p[4]=Y
        except: continue
        rows.append((pc,A,l))
    plays=[i for i,r in enumerate(rows) if r[0]==play_entry]
    out=[]
    for k in range(len(plays)):
        seg=rows[plays[k]:(plays[k+1] if k+1<len(plays) else len(rows))]
        w=[]
        for pc,A,l in seg:
            m=re.search(r'sta\w*\s+\S*\s*\[(d4[0-9a-f]{2})\]', l.lower())
            if m: w.append((int(m.group(1),16)&0xff, A))   # (reg_offset, value)
        out.append(w)
    return out
```
- Play-entry PC = PSID header play address = bytes 12-13 big-endian. For
  Human_Race orig it is `$0986`; for the rebuild it is `$1003` (a trampoline
  `JMP $10a9` — segment on `$1003`, where every play() call enters).
- **Validation:** for HR and Commando, the §3 per-irq chunks (parsed per §5)
  must equal `perplay(...)` chunk-for-chunk over the first ~50 frames, for BOTH
  orig and rebuild. Only when they match is the per-irq trustworthy.
- pc-trace is the oracle but is HUGE (~16k lines/frame) — fine for ~50 frames of
  validation, NOT usable as the actual verdict.

---

## 5. verify.py integration (after §3 is validated)

In `pipelines/hubbard/verify.py` (`verify_all` / `_capture_music` /
`_music_ok`), add a CIA branch:

- Detect CIA: PSID header `speed` field (bytes 0x12-0x16 big-endian) `!= 0`,
  per subtune bit (bit N = subtune N+1). The USF carries it as `usf.psid.speed`.
- **CIA path:** capture `siddump --writelog-per-irq --raw` for orig + rebuild,
  parse per-play chunks, compare orig[k] vs rebuild[k] over the overlap; pass iff
  all match (and play counts are close, ≤ a small tolerance).
- **vblank path (speed==0):** unchanged — existing flat
  `compare_instruction_stream`.
- Gate TIGHTLY so only CIA subtunes take the new path (zero risk to the 60+
  passing non-CIA subtunes + digi).

**Per-irq output parsing (IMPORTANT):** one output LINE per siddump frame; each
line is `CSV...|I<chunk>|I<chunk>...` with potentially MULTIPLE `|I` chunks per
line (multiple play()s per frame under CIA). Parse: split each line on `'|I'`,
take `parts[1:]` as the chunks; each chunk is `:cyc:reg:val:cyc:reg:val...`.
Flatten chunks across all lines into the per-play sequence.

---

## 6. Test matrix (must all hold)
- **Human_Race (4 subs): PASS.**
- **Battle_of_Britain (1 sub): FIRST verify the engine is correct via the §4
  pc-trace oracle** (I only ever proved HR). If correct → PASS; if it reveals a
  real bug → it SHOULD fail (don't force it).
- **Devils_Galop: still FAIL** (vblank, real V3 bug; uses flat path).
- **Commando, Monty (19/19), all other non-CIA: UNCHANGED.**
- **Chimera / digi: UNCHANGED** (digi path untouched).
- `tools/regression.py`: Hubbard should go 65 → 69 ok (HR 4 + Battle 1), or
  65 → 68 if Battle turns out to have a real bug.

---

## 7. Pitfalls that burned a multi-hour session (avoid these)
1. **`--writelog-per-irq` was never actually splitting per-play** (see §2) — do
   not trust ANY past per-IRQ numbers; they were per-frame.
2. **SID-write extraction from a pc-trace:** use the EFFECTIVE-address `[d4xx]`
   bracket, NOT a mnemonic regex. A regex matching only `STAay` silently misses
   `STAax` (the bounded-PWM PW writes at orig `$0BF7/$0BFE`) and fabricates a
   nonexistent "PWM bug".
3. **The disasm COMMENT** `v_pwperiod=[0,1,$1D]` is a RUNTIME value; the
   load-time bytes at `$0DC8` are all zero (verified). There is no PWM "seed"
   fix — that was a dead end.
4. **Do NOT edit `.cpp/.h` with Python `open().write()`** — it rewrote line
   endings and produced a whole-file diff. Use the Edit tool.
5. **Verify `base` empirically** (§3c.1) before trusting the cycle subtraction.
6. **Build:** only `siddump.cpp` changed → recompile just siddump:
   `cd tools && g++ -std=c++17 -O2 -DNDEBUG -DHAVE_CONFIG_H -I libsidplayfp/src
   -I libsidplayfp/src/builders/sidlite-builder siddump.cpp
   libsidplayfp/build/libsidplayfp.a -o siddump`.
   If overlay headers/.cpp changed → full `bash tools/build.sh` (~1-2 min).
7. **Fallback if §3c stays intractable:** option (b) — a Python flat-stream
   ALIGNMENT verdict. The orig/rebuild flat `--writelog` streams are identical
   modulo the init prefix; find the offset `d` that aligns them (substring-match
   a mid-stream window of the rebuild inside the orig), then compare the aligned
   overlap. Lower-risk (no emulator change) but heuristic; guard against
   false-alignment on looped/repetitive material.

---

## 8. Key file/line index (as of 2026-06-07)
- `tools/siddump.cpp`: per-irq splitter ~462-478; frame loop clears ~369/375/478;
  `--pc-trace` arg ~162; play-entry-count wiring ~329.
- `tools/libsidplayfp-overlay/src/c64/c64cpu.h`: play-entry record ~137-145
  (absolute getTime at `addr == m_playAddr`); `m_playEntryCycles` ~60.
- `tools/libsidplayfp-overlay/src/c64/c64sid.h`: `m_cycleBase` ~56;
  `clearWriteLog`/base-set ~86-93; write-cycle = getTime-base ~105;
  `getWriteLog` ~95.
- `tools/libsidplayfp-overlay/src/player.{h,cpp}`: `getWriteLog` (h~163,
  cpp~607); `getPlayEntryCycles` plumbed via sidplayfp.
- `tools/libsidplayfp-overlay/src/sidplayfp/sidplayfp.{h,cpp}`: `getWriteLog`
  (h~237, cpp~144); `getPlayEntryCycles` cpp~186.
- `pipelines/hubbard/verify.py`: `verify_all`, `_capture_music`, `_music_ok`.
- `pipelines/hubbard/verify_cycle.py`: `writelog_capture`,
  `compare_instruction_stream`.
- `tools/find_first_divergence.py`: flat localizer (duration-parse fixed for
  `M:SS.mmm` in commit `7b29bf3`).
- CIA tunes: Human_Race `speed=0x0000000f` (subs 1-4 CIA), Battle_of_Britain
  `speed=0x00000001`. Commando/Monty/Devils `speed=0` (vblank).
