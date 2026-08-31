# The digi parametrization — one representation for the sample channel

**Status: OPTION A APPROVED AND LANDED (schema 2026-08-29, `532b3931`).**
`DigiConfig` / `SampleInstrument` / `digi_voice` are live in
`src/usf/types.py`; phase 2 (Digi-Organizer) is CLOSED at 39/39 standalone
FULL; phase 3 (Rayden_Digi) is in RE — see `pipelines/rayden_digi/RE_NOTES.md`.
Phases 4-5 remain open. *(This header said "PROPOSAL … nothing here is landed"
until 2026-08-31, five weeks of work after it stopped being true; it misled a
session into telling the owner their approval was still pending. A status line
is load-bearing — see `feedback_deprecate_stale_docs`.)*
This is the design backlog item 5's tripwire demands: the SECOND digi
engine must PARAMETRIZE (`digi { technique, rate }`) instead of adding a
row to `_digi_player_registry`. Two engine families are now waiting on
it at once (backlog items 28 bucket A + 29 bucket A), so it is designed
ONCE for both — and checked against the third (Chimera, already landed).

Owner request 2026-08-29: "go ahead with designing once for both."
Deliverable = this document; schema changes land only after approval.

---

## 1. Scope — the three engine families, measured

| family | technique | carriers | where |
|---|---|---:|---|
| Chimera 1-bit (landed) | wavetoggle_1bit | 1 | `digi_player: chimera_1bit`, DigiSubtune + FLAC sidecar |
| **Rayden_Digi V1/V2** | volume_4bit | **17** (all MUSICIANS/R/Rayden) | 14 f1 partials + Popel (C27 error) + 2 unrouted; 16 beside DMC, 1 beside a Rob_Hubbard player |
| **Digi-Organizer** | volume_4bit | **131** | 51 beside Music_Assembler, 39 standalone, 27 beside other engines (JCH, AMP, OdinTracker…), 14 beside DMC |

The representation therefore serves at least DMC, Music_Assembler and
future families — it must be family-agnostic musical content, never a
DMC-shaped bolt-on. 149 corpus members ride on it.

## 2. Measured anatomy (RE 2026-08-29, static disassembly)

### Rayden_Digi V1 (Boot_Zak_v2, RSID play=$0000)
- Init installs everything and never returns: a raster-synced main
  loop calls the ORDINARY canonical DMC play (`JSR $1003`) then a digi
  sequencer tick per frame. KERNAL banked out; NMI vector → the digi.
- **Playback**: CIA2-timer NMI; one raw 4-bit byte → `$D418` per NMI;
  in-stream terminator byte `$1F`; at end: rest level `$0A` written and
  the timer stopped. SMC stream pointer.
- **Sequencing**: a looping event stream of `(sample#, rate#, duration)`
  triples. sample# indexes a word table of sample start addresses;
  rate# indexes a table of CIA latches (**per-event pitch**); duration
  counts ticks clocked by the DMC tempo variable ($1716); `$FF` = loop.
- **Register ownership**: the DMC player's two canon `$D418` stores are
  re-pointed to the mvol shadow ($1717) — the C19 static-$D418 family;
  Popel's chip-1 probe already reads `master_vol_static: 9`. During
  play, **$D418 belongs exclusively to the digi engine.**
- Also present: an unrolled raster-burst `$D418` player ($2200-$2498,
  3 writes/badline via `($F4),Y`) — a second PACING topology within V1,
  to be measured per member (which parts use it); not a new technique.
- V2 (3 members + Spelling_Around) not yet disassembled — expected the
  same technique with a different pacing/bit layout; measure before
  extract work, but it does not change this design's shape.

### Digi-Organizer (Piano_Fun_93, RSID play=$0000)
- Init RELOCATES player+data to $9000/$A000 (C26 flavor), then the
  same self-driven pattern.
- **Playback**: CIA2-timer NMI, base latch $0070 (~8.8 kHz); samples
  nibble-PACKED two per byte (high nibble then low, two vector-swapped
  NMI handlers); each write is `nibble | $10` → `$D418` (volume + the
  filter-mode bit held).
- **Sequencing is a full tracker channel**: an orderlist ($FE = halt,
  $FF = loop) over 32-row patterns; row byte 0 = empty, else a sample
  trigger; a 4-byte per-sample table = {start, end, **per-sample CIA
  latch = pitch**, …}; a speed byte clocks rows.

### Chimera (landed, the boundary case)
- 1-bit wavetoggle, cycle-strict, digi as a WHOLE SUBTUNE (one sample,
  no concurrent music). DigiSubtune {id, sample} + FLAC sidecar with
  pace/bank extras; player chosen via the `digi_player` registry —
  the tolerated library-of-one this design retires for new engines.

## 3. The union of musical degrees of freedom (Principle §4)

Cluster by BEHAVIOR, not code. Across all three families the musical
content is:

1. **Technique** — how sample values become sound: `wavetoggle_1bit |
   volume_4bit`. A small, musically meaningful enum (each value names a
   physically different synthesis route on the chip). Exactly the §4
   "shape:"-style enum; NOT an engine id.
2. **Rate** — samples per second, per sample or per event (pitched
   playback). The authored quantity in both engines is a CIA timer
   latch (integer cycles/sample); Hz is derived (985248/latch).
3. **Sample content** — the PCM itself. Ledger C7 category C: bytes ARE
   the natural musical form → FLAC sidecars (existing machinery).
4. **The score** — WHICH sample plays WHEN: Rayden = a linear looping
   list of (sample, pitch, duration) events; Digi-Organizer =
   orderlist + patterns of sample-trigger rows. Both are ordinary
   note-event sequencing.
5. **Mixing constants** — idle/rest level ($0A Rayden), held mask bits
   (`| $10` D-O). Trichotomy §4.2 priming-shaped scalars.

NOT musical content (engine mechanism, stays in the composer): NMI vs
IRQ vs raster-burst plumbing, SMC pointers, nibble packing, vector
swapping, CIA register choice, the relocation copy, in-stream
terminator bytes, the sequencer's tick-clock source.

## 4. Options

### Option A — the digi channel is a VOICE (recommended)

The digi channel is scored with the SAME machinery as a SID voice:

- A subtune may carry a **digi voice** beside its SID voices. Its rows
  are ordinary note-events whose "instrument" is a **sample
  instrument** and whose "pitch" is the playback rate.
- New typed pieces (names indicative, final spelling at review):

  ```
  ; tune-level (or subtune-level) block
  digi {
    technique:  volume_4bit          ; wavetoggle_1bit | volume_4bit
    idle_level: $0A                  ; rest value written at sample end
    or_mask:    $10                  ; bits held high on every write
  }

  ; instrument pool
  sample_instrument s1 {
    sample:      "X.sample1.flac"    ; PCM sidecar (C7-C)
    rate_cycles: $0070               ; default CIA latch (cycles/sample)
  }

  ; the digi voice's rows: (instrument, optional rate override,
  ; duration/row position) — reusing orderlist/pattern structures
  ; where the engine has them (Digi-Organizer), a flat event list
  ; where it does not (Rayden).
  ```

- `rate_cycles` follows the Principle §9 tiebreaker: the integer latch
  is the authored, exact, ordered quantity (interpolable — passes the
  parameter test); Hz would be a lossy derivation of it.
- Sidecar naming generalizes from `<base>.sample<subtune>.flac` to
  per-sample-id names; existing Vorbis-comment metadata machinery
  carries native_bits/method as today.
- **Composer synthesizes ONE digi player from `technique` + the score**
  — pacing, packing, pointers are its own choices, verified by the
  write stream. `_digi_player_registry` gains NO second row; DigiCode
  addresses stay unreachable from USF. (Chimera's landed path is left
  untouched for byte-identity; folding it into the general form is a
  Move-1-era carrier refactor, noted in §7.)

Why A: it reuses the score representation instead of minting a
parallel one, lands both engines as points in one parameter space
(§9 test 4), and the ML consumer sees a fourth melodic-ish channel
with sample timbres — learnable structure, no opaque kinds.

### Option B — a separate `digi_track` structure (rejected)
A parallel track/pattern schema just for digi duplicates the orderlist
machinery and invites divergence between the two sequencing grammars —
§4's over-splitting smell at the structural level.

### Option C — extend DigiSubtune with `technique` only (rejected)
DigiSubtune means "this SUBTUNE is one sample playback". The new
classes play digi CONCURRENTLY with music in the same subtune; a
subtune-kind flag cannot express the channel. It would also leave the
score (the actual musical content) unrepresented.

## 5. Verification design

- Digi is cycle-strict (core tenet Mode 2); music is Mode 1. These
  members carry BOTH in one subtune. Measured basis for a clean split:
  in the Rayden members the music player's $D418 stores are patched
  away — **the digi engine owns $D418 exclusively during play**. So:
  split the captured stream by register class ($D418 vs the rest), and
  verify music flat (Mode 1) + digi cycle-strict (Mode 2) — the C27/C28
  "split the stream, verify each in its own mode" shape, applied to
  register ownership instead of chip tag.
- PRECONDITION to confirm per family: the same ownership must hold for
  Digi-Organizer pairings (its `| $10` mask suggests it also owns
  $D418; the paired music engine's mvol behavior must be probed, and
  any member where music still writes $D418 needs an attribution rule
  before this verdict shape is trusted).
- Cycle-strictness on the digi side means the composer must reproduce
  the pacing topology exactly (NMI latch phase, the raster-burst
  variant) — reproduction of mechanism is licensed by the core tenet;
  the topology itself never enters USF.
- RSID play=$0000: the rebuild ships as self-driven RSID like Chimera's
  original combined build did; the trichotomy governs init (universal
  reset + priming; the environment block carries the self-drive rate).

  ⚠ **AMENDED 2026-08-31 — the parenthesis above is WRONG for these
  members, and was already wrong when written.** Hours after this document,
  the trichotomy doc gained its **Mode-2 exemption** (recorded 2026-08-29
  from Digi-Organizer): a Mode-2 member is EXEMPT from the universal-init
  verdict shift, because under cycle-strict comparison the init writes'
  CYCLES are signal and a universal reset fails by construction. The
  composer MIRRORS the member's init cycle-shape instead (ledger C40), and
  that is what the landed Digi-Organizer build actually does.

  For the music+digi members this document is about, the resolution is:

  * **Init FORM follows Mode 2 — mirror the cycle shape, do NOT emit a
    universal reset.** The init is one code path serving both sides, and
    C40 is explicit that the init-entry→timer-start cycle count sets the
    interrupt grid's phase. A universal reset would move that phase and
    break the digi verdict even if every music write were perfect.
  * **The trichotomy's CATEGORIES still route the content** — priming to
    `init.sid`, temporal facts to `environment`. The exemption suspends the
    verdict shift, never the classification.

  This is applying existing canon rather than deciding anything new: the
  exemption is owner-recorded and Digi-Organizer already ships it.

  🔶 GENUINELY OPEN, and it is new with Rayden: Digi-Organizer's closed
  members are digi-only, so nothing tested a SHARED init. Here the music
  player's Mode-1 init writes and the digi's Mode-2 cycle-shape come out of
  the same routine. Whether the music side needs any separate treatment —
  or whether mirroring the whole init subsumes it — is unmeasured. Settle
  it on a real member before writing the composer's init path.

## 6. The four tests (Principle §9), run against Option A

1. **Completeness** — provable only by migration; the design carries
   every measured DoF of both engines (technique, per-event rate,
   score, mixing constants) plus Chimera's (pace = rate_cycles).
2. **No escape hatch** — `technique` is a 2-value musical enum; no
   registry row; no field indexes composer code. ⚠ THIS BECAME FALSE
   AND WAS RESTORED (2026-08-30). It held for the PLAYER, which is what
   this document is about, but the migration then grew a DRIVER
   registry — 14 hand-written 6502 templates selected by name from
   `params['digi_driver']`, six of them with a single carrier — and no
   one re-ran this test against it. The driver is now parametrized (a
   generic instruction walk measures each member; one emitter
   synthesises code for it), so the claim holds again; see ledger C40
   points 1-2, which had taught the shortcut and are corrected. The composer branch on
   `technique` is the same class as branching on `shape: triangle` —
   parametric synthesis, not engine sniffing (each value is defined by
   its chip behavior, not by which author's player it came from).
3. **Interpolation** — rate_cycles, idle_level interpolate; averaging
   two scores is as meaningful as averaging two melodies (same status
   as MusicSubtune content). Technique is a genuine categorical.
4. **Cross-engine reuse** — Rayden and Digi-Organizer land as points in
   ONE space (different scores, same parameters); the third family
   (whatever Galway-style $D418 mixer comes next) should land as a new
   RATE/score point or a genuinely new technique value — never a kind.

## 7. Phasing (proposed, post-approval)

1. **Schema** (owner-gated): the `digi {}` block + sample instruments +
   digi-voice rows. Run `usf_corpus_check` + `usf_spec_lint` +
   `composer_param_lint` after.
2. **Digi-Organizer first** (131 carriers, richer sequencing, tests the
   orderlist reuse; standalone members = simplest, no music merge).
3. **Rayden_Digi** (17; needs the DMC pairing + the C19 static-$D418
   knob already probed; V2 disassembly first).
4. Verification split (register-ownership Mode-1/Mode-2) built once,
   shared.
5. Move-1 note: fold Chimera's DigiSubtune path into the general form
   as a byte-identity carrier refactor; delete `_digi_player_registry`.

## 8. Open questions (measure before landing, none block approval)

- Rayden_Digi V2's bit layout/pacing (3 members + 1 non-DMC).
- The Rayden raster-burst mode: per-member schedule, or a fixed part of
  the V1 player? (cycle-strict verify will adjudicate).
- Digi-Organizer standalone members: digi-only files — do they carry a
  silent music side, or is the file pure digi? (affects whether a
  digi-only MusicSubtune-less file shape is needed — Chimera precedent
  suggests yes, already expressible as a digi-voice-only subtune).
- The f2 "bare DMC" suspects (Sax/Digi_Music, Justincase_part_6):
  confirm they are unsignatured Digi-Organizer variants.
- Whether any Digi-Organizer pairing lets the music engine keep its
  $D418 writes (verification precondition, §5).
