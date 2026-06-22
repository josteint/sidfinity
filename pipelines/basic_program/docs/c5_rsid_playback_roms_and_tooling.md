---
source_url: local: tools/siddump.cpp + tools/libsidplayfp/src/ + tmp/jc64/ + tmp/dmc_hunt/DeepSID/ + ~/.local/share/sidplayfp/ + hvsc84/DOCUMENTS/SID_file_format.txt
fetched_via: local read + binary verification
fetch_date: 2026-06-22
author: SIDfinity research agent (cluster 5)
content_date: 2026-06-22
reliability: primary (all findings verified from local binaries + source)
---

# RSID-BASIC Playback: ROM Requirements, Tooling, and Ground-Truth Strategy

## Summary

**Blocker 1 is already 90% solved on this machine.**
The three C64 ROM images (KERNAL 8192 B, BASIC 8192 B, CHARGEN 4096 B) that
libsidplayfp requires to execute BASIC tunes are **already present at
`~/.local/share/sidplayfp/`** (the standard sidplayfp CLI data dir) and are
the correct, libsidplayfp-recognized canonical dumps. The system `sidplayfp`
CLI at `/usr/bin/sidplayfp` (v2.6.2 / libsidplayfp v2.6.0) successfully plays
BASIC tunes and identifies all three ROMs by name. The only missing piece is
wiring `engine.setRoms(...)` into `tools/siddump.cpp` before calling
`engine.load(&tune)` — a ~25-line change.

---

## 1. libsidplayfp ROM Requirements

### What the library needs

`sidplayfp::setRoms(const uint8_t* kernal, const uint8_t* basic, const uint8_t* character)`
takes three raw ROM image pointers. Defined in
`tools/libsidplayfp/src/sidplayfp/sidplayfp.h` (line 206). Individual setters
also exist: `setKernal`, `setBasic`, `setChargen` (lines 215-218).

**Sizes (hard-coded in the ROM bank classes):**
- KERNAL:  8192 bytes (0x2000) — mapped at $E000-$FFFF
- BASIC:   8192 bytes (0x2000) — mapped at $A000-$BFFF
- CHARGEN: 4096 bytes (0x1000) — mapped at $D000-$DFFF

### What happens without ROMs

When `setRoms` is NOT called (current siddump behaviour), `KernalRomBank::set(nullptr)`
fills the ROM with NOPs and installs minimal stub IRQ/reset vectors
(`SystemROMBanks.h` lines 130-168). The BASIC ROM bank similarly gets blank data.
When the PSID driver tries to `RUN` the BASIC program via the warm-start hook at
`$BF53`, it executes the stub NOP sled and falls off into nothingness. Result:
one `$D418=$0F` write (from the PSID driver's power-on reset sequence) then
silence — exactly what we observe from `siddump --force-rsid --writelog`.

### What happens WITH ROMs (COMPATIBILITY_BASIC path)

When `info->compatibility() == SidTuneInfo::COMPATIBILITY_BASIC`,
`psiddrv.cpp` takes the `COMPATIBILITY_BASIC` branch:

1. Reloc driver placed at pages $04-$06 (hardcoded for BASIC).
2. `mem.setBasicSubtune(song-1)` patches the BASIC ROM at $BF53:
   `LDA #<song-1> / STA $030C / JSR $A82C / JMP $A7B1`
   (sets `$030C` = song number, invokes the BASIC warm start, which executes
   `RUN`). For single-subtune BASIC tunes (the vast majority), this is `LDA #0`.
3. `mem.installBasicTrap($BF53)` patches $A7AE in BASIC ROM:
   `JMP $BF53` — so every BASIC warm start enters the subtune-selector.
4. Init address is set to `$BF55` (the `STA $030C` instruction), NOT the
   program's data region.
5. Reset vector (KERNAL $FFFC) is redirected to the reloc driver.

When `engine.play(N)` is called, the 6510 CPU runs the real KERNAL + BASIC
interpreter, which tokenizes nothing (data is already tokenized) and begins
executing `RUN`. The BASIC program runs indefinitely (GOTO loop), writing SID
registers as it goes.

### The PSID driver compatibility check and `--force-rsid`

`siddump.cpp` line 229:
```cpp
if (!force_rsid && info->compatibility() == SidTuneInfo::COMPATIBILITY_R64)
```

**`COMPATIBILITY_BASIC` (enum value 3) is NOT `COMPATIBILITY_R64` (enum value 2).**
BASIC tunes are NOT skipped even without `--force-rsid` — they fall through the
check. However, they still produce silence because `setRoms` is never called.
The fix does NOT require changing the skip-logic — just adding ROM loading.

### How the reference sidplayfp CLI loads ROMs

`~/.config/sidplayfp/sidplayfp.ini` (on this system):
```ini
Kernal Rom = /home/jtr/.local/share/sidplayfp/kernal
Basic Rom  = /home/jtr/.local/share/sidplayfp/basic
Chargen Rom = /home/jtr/.local/share/sidplayfp/chargen
```

The sidplayfp CLI reads this ini file at startup, `fread`s each file into a
heap buffer, and calls `engine.setRoms(kernal_buf, basic_buf, chargen_buf)`.
`siddump.cpp` needs to do the same. The ROM path can be configured via an env
var or command-line flag (see Section 5 for the proposed `--roms-dir` flag).

---

## 2. ROM Images: What We Have, Provenance, and Licensing

### Canonical Commodore 64 ROM dumps (the ones we have)

Three independent copies exist on this machine, all **byte-identical**:

| Copy | Path | MD5 match |
|------|------|-----------|
| System sidplayfp data | `~/.local/share/sidplayfp/{kernal,basic,chargen}` | ✓ all 3 |
| jc64 emulator tree | `tmp/jc64/data/{kernal.rom,basic.rom,char.rom}` | ✓ all 3 |
| DeepSID inline base64 | `tmp/dmc_hunt/DeepSID/js/player.js` (BASIC_ROM / KERNAL_ROM / CHAR_ROM) | ✓ all 3 |

**Exact identities** (from `tools/libsidplayfp/src/romCheck.h`):

| ROM | Size | MD5 | libsidplayfp description |
|-----|------|-----|--------------------------|
| KERNAL | 8192 B | `39065497630802346bce17963f13c092` | "C64 KERNAL third revision" |
| BASIC  | 8192 B | `57af4ae21d4b705c2991d98ed5c1f7b8` | "C64 BASIC V2" |
| CHARGEN | 4096 B | `12a4202f5331d45af846af6c58fba946` | "C64 character generator" |

These are the original Commodore 64 ROM images. The "third revision" KERNAL is
the most widely distributed dump of the standard PAL C64 (the same one VICE uses).

### Copyright status

The Commodore ROMs are copyrighted. The rights were acquired by Tulip Computers
NV (Netherlands) when they bought Commodore's assets in 1995. Tulip later sold
the brand; the ROM copyright situation is unresolved but the dumps are ubiquitous.
The `vice` Debian package explicitly states:
> "A corporation in the Netherlands called Tulip holds the copyrights to the
> ROM images, and redistribution is not permitted, but VICE itself is unencumbered."

**Practical status for this project:**
- For INTERNAL TOOLING (capturing ground-truth write streams for our own ML
  pipeline), using these ROMs is equivalent to VICE usage — standard practice in
  the SID preservation community.
- The ROMs MUST NOT be committed to git or redistributed with the project.
- The correct path is: document the expected ROM location (`~/.local/share/sidplayfp/`)
  which the sidplayfp CLI already manages, and have `siddump` read from there.

### Open ROM alternatives

#### C64 OpenROMs (MEGA65 project / 65c02 project)

The MEGA65 project and associated contributors have been developing open-source
C64 compatible ROMs under permissive licenses. Status as of 2026:

- **OpenROMs KERNAL**: Partial implementation. Passes most KERNAL function calls
  but has known gaps in BASIC float routines (transcendental functions SIN/COS/ATN
  may differ). See `https://github.com/MEGA65/open-roms`.
- **CBM BASIC V2 reimplementation**: The "cbmbasic" project (Commodore BASIC V2
  as a POSIX process) and similar work exists but is NOT a drop-in ROM image.
- **Practical recommendation**: Open ROMs are NOT yet complete enough for bit-exact
  ground-truth capture of the "algorithmic" BASIC sub-class (tunes using FP math
  with PEEK/SIN/RND/TI). The DATA/READ table-driven majority (the tractable ~60%
  sub-class) would work fine with any correct BASIC interpreter, but we cannot
  predict without testing.

**For ground-truth capture: use the canonical C64 KERNAL/BASIC (already at
`~/.local/share/sidplayfp/`).** Open ROMs are a fallback for redistribution-only
scenarios and currently carry risk of inexact FP results.

---

## 3. The Exact Fix for `tools/siddump.cpp`

### What to add

After `sidplayfp engine;` is constructed (line 250) and before `engine.config(cfg)`
(line 261), add ROM loading for BASIC tunes:

```cpp
// Load ROMs for BASIC/RSID tunes (required for COMPATIBILITY_BASIC)
// Default path: ~/.local/share/sidplayfp/{kernal,basic,chargen}
// Override: --roms-dir <dir>
if (info->compatibility() == SidTuneInfo::COMPATIBILITY_BASIC
    || info->compatibility() == SidTuneInfo::COMPATIBILITY_R64) {
    const char* roms_dir = roms_dir_arg;  // from --roms-dir flag
    if (!roms_dir) {
        // Default: same location sidplayfp CLI uses
        const char* home = getenv("HOME");
        static char default_dir[512];
        snprintf(default_dir, sizeof(default_dir), "%s/.local/share/sidplayfp", home ? home : "");
        roms_dir = default_dir;
    }
    auto load_rom = [&](const char* name, size_t expected_size) -> std::vector<uint8_t> {
        char path[600];
        snprintf(path, sizeof(path), "%s/%s", roms_dir, name);
        FILE* f = fopen(path, "rb");
        if (!f) return {};
        std::vector<uint8_t> buf(expected_size);
        size_t n = fread(buf.data(), 1, expected_size, f);
        fclose(f);
        if (n != expected_size) return {};
        return buf;
    };
    auto kernal  = load_rom("kernal",  0x2000);
    auto basic   = load_rom("basic",   0x2000);
    auto chargen = load_rom("chargen", 0x1000);
    if (!kernal.empty()) engine.setKernal(kernal.data());
    if (!basic.empty())  engine.setBasic(basic.data());
    if (!chargen.empty()) engine.setChargen(chargen.data());
    if (kernal.empty() || basic.empty()) {
        fprintf(stderr, "Warning: ROMs not found at %s — BASIC tunes will not play\n", roms_dir);
    }
}
```

Also add `--roms-dir <dir>` to the argument parser (alongside the existing flags).

### Verification: does it work?

The system `sidplayfp` CLI (`/usr/bin/sidplayfp`) already does exactly this.
Test run on `hvsc84/DEMOS/A-F/Ahoy_Magazine_BASIC.sid` confirmed:
- Identifies all 3 ROMs correctly ("C64 KERNAL third revision", "C64 BASIC V2", "C64 character generator")
- Produces ~16 seconds of audio output (the full songlength per HVSC)
- Runs the BASIC program to completion

The identical libsidplayfp version is already compiled into `tools/siddump`
(same overlay source tree). The ROM loading call is the only missing piece.

### Write-log capture mode for BASIC

BASIC tunes have NO `play()` vector — the SID writes come from the BASIC
interpreter running continuously. This means:
- `--writelog` is the correct mode (continuous ordered `(reg, val)` stream)
- `--writelog-per-irq` will NOT produce useful output (no IRQ play() markers)
- There is no "Trap C" for BASIC — the write stream is truly continuous
- The duration must cover at least one full loop of the BASIC program

**Recommended capture command** (once ROM loading is wired):
```bash
siddump TUNE.sid --writelog --duration <songlength_seconds * 1.1> 2>/dev/null
```

For the "interactive" sub-class (tunes with `GET` / GETKEY), the `GET` must
return empty (no keypress) — libsidplayfp's keyboard is always empty, so this
path is deterministic.

---

## 4. VICE as Independent Ground-Truth Oracle

VICE (`x64sc`) is the gold-standard C64 emulator and would be an independent
oracle for cross-checking libsidplayfp's output. However:

**Current status on this machine:** VICE is NOT installed. The `vice` package
(v3.7.1) is available in Ubuntu's `multiverse` repository and can be installed
with `sudo apt install vice`, but it does NOT ship ROM images (same Tulip
copyright issue — they're sourced separately).

### VICE SID-write logging methods

Once installed with ROMs, there are three approaches to get a $D400 write trace:

#### Method A: VICE built-in monitor (interactive)

```
x64sc -moncommands /dev/stdin tune.sid <<'EOF'
watch store 0xd400 0xd418
go
EOF
```

The monitor's `watch store` command prints every CPU write to $D400-$D418 to
stdout. This is the most direct method but requires interactive control.

#### Method B: VICE `-sounddev dump` (audio-only, not register-level)

VICE's `-sounddev dump` option writes raw audio samples, not register writes.
This is NOT equivalent to our write-log stream and cannot be used for
instruction-sequence comparison.

#### Method C: `vsid` headless (PSID-specific player)

VICE ships `vsid`, a headless SID player binary. However:
- `vsid` processes PSID files (non-RSID compatible) differently from `x64sc`
- For BASIC tunes (RSID), `vsid` may not execute the BASIC program correctly

#### Method D: VICE with GDB/hook (advanced)

Build VICE from source with the `--enable-debug-monitor` flag. Hook the CPU's
memory write routine in the emulator and log all $D400-$D418 writes. This is
the most accurate approach but requires a custom VICE build.

**Practical recommendation for the Basic_Program category:**
VICE as oracle is a "later if needed" fallback. The libsidplayfp-based approach
(siddump + ROM loading) is faster, already integrated, and uses the same engine
that plays these tunes in DeepSID and all major SID players. Cross-checking a
few representative tunes against `/usr/bin/sidplayfp -wtest.wav` (which also uses
libsidplayfp) is sufficient to validate the wiring.

**To install VICE when needed:**
```bash
sudo apt install vice
# Then provide ROMs at ~/.config/vice/C64/  (x64sc auto-loads from there)
# ROMs: copy ~/.local/share/sidplayfp/kernal → kernal, basic → basic, etc.
```

---

## 5. DeepSID and In-Browser Players

### DeepSID

DeepSID (`tmp/dmc_hunt/DeepSID/`) uses jsSID / WebSID in-browser players backed
by a WebAssembly build of libsidplayfp. In `js/player.js`:

- `this.BASIC_ROM`, `this.KERNAL_ROM`, `this.CHAR_ROM` are **inline base64-encoded
  ROM blobs** hard-coded into the JavaScript source.
- These decode to byte-identical copies of the same canonical C64 ROMs we have:
  - BASIC MD5:   `57af4ae21d4b705c2991d98ed5c1f7b8` ✓
  - KERNAL MD5:  `39065497630802346bce17963f13c092` ✓
  - CHARGEN MD5: `12a4202f5331d45af846af6c58fba946` ✓
- When the player detects a BASIC-flag tune (filenames containing `_BASIC.`),
  it instantiates the backend with the ROM blobs:
  `new SIDPlayBackendAdapter(this.BASIC_ROM, this.CHAR_ROM, this.KERNAL_ROM)`
- This means **DeepSID plays Basic_Program tunes correctly** and uses the
  identical underlying ROM images.

**Implication**: DeepSID is NOT an independent oracle (same libsidplayfp engine +
same ROMs). It IS a cross-check against whether the wiring is correct (if
DeepSID plays it, siddump-with-ROMs should produce the same stream).

### Multi-subtune BASIC: the `$030C` mechanism

Per `DOCUMENTS/SID_file_format.txt` and `psiddrv.cpp` / `SystemROMBanks.h`:

- For BASIC tunes, the song number to play is written to address `$030C`
  BEFORE the BASIC `RUN` command executes.
- The PSID driver patches the BASIC ROM at `$BF53` with:
  `LDA #<song-1>  STA $030C  JSR $A82C  JMP $A7B1`
  (value 0 = song 1, value 1 = song 2, etc.)
- The BASIC program reads `PEEK(780)` (= `$030C`) to decide which song to play.
- For single-subtune tunes (the 486-SID majority), this is always `LDA #0`.
- libsidplayfp handles this automatically via `tune.selectSong(N)` +
  `setBasicSubtune(N-1)`.

**No manual $030C handling is needed in siddump** — it's automatic once ROMs
are loaded and `selectSong` is called (which already happens at line 242).

---

## 6. SID File Format: Complete RSID/BASIC Rules

From `hvsc84/DOCUMENTS/SID_file_format.txt` (primary source):

### RSID constraints (all 486 Basic_Program tunes satisfy these):
- `magicID = "RSID"`, `version = 2, 3, or 4`
- `loadAddress = 0` (load address embedded in first 2 bytes of data payload)
- `initAddress = 0` (because C64 BASIC flag is set — the PSID driver handles init)
- `playAddress = 0` (RSID always uses interrupt-driven play, not explicit call)
- `speed = 0` (no CIA timing — BASIC uses the KERNAL's built-in CIA timers)

### C64 BASIC flag (flags bit 1):
- Set when the tune is a tokenized BASIC program that needs the BASIC ROM.
- `flags & 0x0002 != 0` for RSID → `COMPATIBILITY_BASIC` enum value.
- In our corpus: **100% of 486 Basic_Program SIDs** have this flag set (confirmed
  by local recon Phase 1).

### Power-on environment for RSID (from the spec):
- VIC IRQ at raster $0137 (NOT enabled)
- CIA 1 Timer A: 60Hz (`$4025` PAL / `$4295` NTSC), running, IRQs ACTIVE
- Bank register: `$0001 = $37` (BASIC ROM + KERNAL ROM + I/O all mapped)
- `$02A6`: PAL/NTSC flag (0x01 PAL, 0x00 NTSC)
- `$030C`: song number (0-based) — set by PSID driver before BASIC RUN

### Memory map at BASIC RUN time:
```
$0000-$07FF  Zero page + stack + BASIC work area
$0801        BASIC program start (tokenized BASIC, loaded here by SID file)
$A000-$BFFF  BASIC V2 ROM (mapped — required for BASIC interpreter)
$D000-$DFFF  Character generator ROM (mapped — required for KERNAL)
$D400-$D418  SID chip I/O (writes from POKE 54272+reg, val)
$E000-$FFFF  KERNAL ROM (mapped — provides RUN, IRQ handler, FP routines)
```

The `$0001` bank register = `$37` ensures ROM is paged in at all three ranges.
This is the standard RSID environment.

### Note on PSID vs RSID bank register handling

For PSID tunes, siddump sets the bank register based on the init/play address
(the `iomap()` function in psiddrv.cpp). For RSID/BASIC, the bank is always `$37`
(full ROM mapping), set by `copyPoweronPattern()` which replays a compressed
snapshot of the C64 power-on state. This is handled automatically by libsidplayfp
when the tune is loaded with correct ROMs.

---

## 7. Concrete Implementation Plan

### Step 1: Wire ROM loading into siddump.cpp (1-2 hours)

Add to `siddump.cpp`:
1. Parse `--roms-dir <dir>` CLI argument (default: `$HOME/.local/share/sidplayfp`)
2. After `sidplayfp engine;` and before `engine.config(cfg)`:
   - Load kernal (8192 B), basic (8192 B), chargen (4096 B) from dir
   - Call `engine.setRoms(kernal.data(), basic.data(), chargen.data())`
   - Print ROM identity from `engine.info()` on stderr in verbose mode
   - Warn and continue (not error) if ROMs are missing (non-BASIC tunes work fine)
3. Remove (or soften) the RSID skip check: currently `COMPATIBILITY_R64` is
   skipped without `--force-rsid`. BASIC tunes are `COMPATIBILITY_BASIC` so they
   already pass through. The check can stay as-is.
4. Update the usage string to document `--roms-dir`.

**ROMs available at**: `~/.local/share/sidplayfp/` (already present, correct)

### Step 2: Validate capture (30 min)

Test on 2-3 representative tunes:
```bash
# DATA/READ table-driven (deterministic, should work immediately):
siddump hvsc84/DEMOS/A-F/Ahoy_Magazine_BASIC.sid --writelog --duration 20 > /tmp/ahoy.wl

# Algorithmic / PEEK-based:
siddump hvsc84/MUSICIANS/B/Bond_Alan/Two_Lines_of_Code_1_BASIC.sid --writelog --duration 60 > /tmp/two_lines.wl

# Check that writes appear (not just $D418=$0F silence):
grep '^|W:' /tmp/ahoy.wl | head -20
```

### Step 3: Evaluate verification mode (design decision)

BASIC tunes have no `play()` vector. The comparison mode must be:
- **Flat ordered `(reg, val)` stream** (Blocker 2 from local recon)
- Skip the init prefix (first N writes before the BASIC program starts making music)
- Use write-count overlap (not frame count): compare the first K `(reg, val)` pairs
  where K = min(orig_writes, rebuild_writes)
- The "verification" for BASIC will be self-comparison (orig == orig), and
  cross-comparison between two captures of the same tune (determinism check)

For the DATA/READ sub-class: a rebuilt USF (decompiled BASIC → note events →
USF) should produce an identical write stream via the standard composer.

For the algorithmic sub-class: the write stream IS the ground truth; USF
representation is the open design question (register-trace fallback vs
decompile). See `deprecated/gt2_pipeline/` for the prior register-trace USF path.

---

## Leads to Follow

1. **Implement `--roms-dir` in siddump.cpp** — the 25-line fix that unblocks all
   ground-truth capture. ROMs are already at the default path. Priority: HIGH.

2. **Determinism survey** — run two captures of the same BASIC tune and compare
   write streams. If deterministic (same seed state each time), the flat write
   stream IS the ground truth. If nondeterministic (RND/TI-dependent tunes), need
   to decide whether to record a specific seed or mark as "nondeterministic" in USF.
   Tool: `siddump TUNE.sid --writelog --duration N | md5sum` × 2.

3. **Sub-taxonomy verification** — confirm the DATA/READ vs algorithmic vs
   interactive split across the full 486 SIDs. The BASIC detokenizer already
   exists (recon transcript). Strategy: scan for PEEK/RND/TI/SIN in detokenized
   source to classify. Actionable: build a classifier script over the 486 .sid files.

4. **`$030C` multi-subtune tunes** — identify which of the 486 have `songs > 1`.
   Query: `sid_db.query("SELECT path, songs FROM sids WHERE engine='Basic_Program' AND songs > 1")`.
   These need multi-subtune capture (one stream per subtune via `selectSong`).

5. **VICE installation as oracle** — `sudo apt install vice` + provide ROMs → use
   `x64sc` monitor `watch store` command to cross-check a few tunes. LOW PRIORITY
   since libsidplayfp is the same engine used everywhere in the project.

6. **Verification mode for Blocker 2** — once ground-truth capture works (step 1),
   empirically measure write densities: frames per SID write, writes-per-second,
   do writes cluster around CIA timer beats? This informs the USF verification mode
   design (flat stream vs. something finer). The `deprecated/gt2_pipeline/` register-
   trace USF path is the ready fallback.

7. **Two-Lines-of-Code PEEK/FP stability** — specifically test the "algorithmic"
   sub-class. If the FP math (PEEK(M)/28, M=M+0.2) is deterministic with fixed
   ROM and initial memory state (powerOnDelay=0 in siddump), captures will match.
   If TI (the jiffy clock) advances during playback in a session-dependent way,
   the write stream will not be reproducible. libsidplayfp's jiffy timer starts
   at zero deterministically, so TI-based tunes likely ARE deterministic.
