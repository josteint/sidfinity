# Mathematical Framework for SIDfinity

**Status:** Working document. Notation is precise but grounded in the codebase.

## 0. Notation Conventions

| Symbol | Meaning |
|--------|---------|
| $\mathbb{B}$ | $\{0, 1\}$ (single bit) |
| $\mathbb{B}^n$ | Bit-vectors of width $n$ (equivalently $\{0, \ldots, 2^n - 1\}$) |
| $\mathbb{B}^8$ | Bytes. Registers, memory locations. |
| $[n]$ | $\{0, 1, \ldots, n-1\}$ |
| $R$ | The SID register file: a vector in $\mathbb{B}^{8 \times 25}$ (registers $\texttt{\$D400}$--$\texttt{\$D418}$) |
| $T$ | A register trace: a finite sequence $(R_0, R_1, \ldots, R_{N-1}) \in R^*$ |
| $u$ | A USF program (element of the USF language $\mathcal{U}$) |
| $P$ | The SIDfinity playback function $P : \mathcal{U} \to R^*$ |
| $\approx$ | Trace equivalence (audible indistinguishability) |

---

## 1. The Core Problem

**Given:** A 6502 program $\pi$ (a SID file) that, when executed on a C64 with vertical blank interrupts, writes to the 25 memory-mapped SID registers ($\texttt{\$D400}$--$\texttt{\$D418}$) once per video frame.

**Find:** A USF program $u \in \mathcal{U}$ such that

$$P(u) \approx \text{Trace}(\pi)$$

where $\text{Trace}(\pi)$ is the register trace produced by executing $\pi$ under `libsidplayfp` emulation, $P$ is the SIDfinity player's playback function, and $\approx$ is the audible equivalence relation defined in Layer 3.

This factors into a **forward problem** (given $u$, compute $P(u)$ -- implemented in `codegen_v2.py` + `usf_to_sid.py`) and an **inverse problem** (given $\text{Trace}(\pi)$, recover $u$ -- implemented in `gt2_to_usf.py` and `regtrace_to_usf.py`).

The forward problem is deterministic. The inverse problem is not: many USF programs can produce equivalent traces. We seek any $u$ in the preimage $P^{-1}([\text{Trace}(\pi)]_\approx)$, where $[\cdot]_\approx$ denotes the equivalence class.

---

## 2. Layer 1: 6502 + SID Semantics (The Ground Truth Machine)

### 2.1 State Space

A C64 executing a SID player is a deterministic state machine:

$$\sigma = (M, A, X, Y, S, \text{PC}, \text{flags}, \text{cycle}) \in \Sigma$$

where:
- $M : \mathbb{B}^{16} \to \mathbb{B}^8$ is the 64KB memory map
- $A, X, Y \in \mathbb{B}^8$ are CPU registers
- $S \in \mathbb{B}^8$ is the stack pointer
- $\text{PC} \in \mathbb{B}^{16}$ is the program counter
- $\text{flags} = (C, Z, I, D, V, N) \in \mathbb{B}^6$
- $\text{cycle} \in \mathbb{N}$ is the global cycle counter

The transition function is:

$$\delta : \Sigma \to \Sigma$$

One application of $\delta$ executes one 6502 instruction: fetch opcode at $M[\text{PC}]$, decode, execute, update state. The cycle cost $c(\text{opcode}, \text{mode})$ is deterministic (modulo page-crossing penalties, which depend on the effective address).

### 2.2 SID Register Observation

The SID chip is memory-mapped at $\texttt{\$D400}$--$\texttt{\$D418}$. The observable register state at any point is:

$$\text{obs}(\sigma) = (M[\texttt{\$D400}], M[\texttt{\$D401}], \ldots, M[\texttt{\$D418}])$$

A frame boundary occurs every 19656 cycles (PAL) or 17095 cycles (NTSC). The register trace is the sequence of observations sampled at frame boundaries:

$$\text{Trace}(\pi) = (\text{obs}(\sigma_{f_0}), \text{obs}(\sigma_{f_1}), \ldots)$$

where $f_i$ is the state at the $i$-th frame boundary.

### 2.3 IRQ Structure

SID players are interrupt-driven. The typical structure:

1. **Init** ($\texttt{init\_addr}$): called once, sets up player state
2. **Play** ($\texttt{play\_addr}$): called once per frame via VBI (vertical blank interrupt) or CIA timer

For single-speed players, the play routine runs at frame rate (50 Hz PAL). For multispeed players (tempo >= 12 in GT2), a CIA timer fires 2--16x per frame, calling the play routine multiple times between frame boundaries.

The IRQ schedule $\mathcal{I} = (t_0, t_1, \ldots)$ is the sequence of cycle counts at which the play routine is invoked. For VBI-only players, $\mathcal{I}$ is periodic with period = frame cycles. For CIA-timer players, $\mathcal{I}$ has a finer period.

**Key property:** Given $(M_0, \mathcal{I})$ -- the initial memory image and IRQ schedule -- the trace $\text{Trace}(\pi)$ is fully determined. There is no randomness, no external input (ignoring paddle registers), no nondeterminism.

### 2.4 Existing Z3 Model

`src/player/z3_6502.py` implements a subset of $\delta$ as Z3 bit-vector constraints. The state is:

```python
class CPUState:
    A, X, Y: BitVec(8)
    C, Z, N, V: Bool
    mem: Dict[str, BitVec(8)]
    cycles: int
```

The `execute()` function maps $(s, \text{instruction}) \mapsto s'$ symbolically. The `verify_equivalence()` function checks $\forall s_0 : f_1(s_0) =_O f_2(s_0)$ where $=_O$ restricts equality to specified output locations.

**Current scope:** Straight-line code only. No branches, no loops, no indirect addressing. Sufficient for peephole optimization of codegen output (verifying that a 3-instruction sequence can be replaced by a 2-instruction sequence with identical observable effects).

**Extension needed:** Branch handling (BCC/BCS/BEQ/BNE) with path merging, loop invariants for table lookups, indirect addressing via (zp),Y for instrument data reads.

---

## 3. Layer 2: USF Semantics (The Target Machine)

### 3.1 USF as a State Machine

A USF program $u = (\text{instruments}, \text{patterns}, \text{orderlists}, \text{tables}, \text{globals})$ defines a second state machine. The state at any tick is:

$$\mathcal{S} = (\mathcal{V}_0, \mathcal{V}_1, \mathcal{V}_2, \mathcal{G})$$

**Per-voice state** $\mathcal{V}_v$:

| Component | Type | Description |
|-----------|------|-------------|
| $n_v$ | $[96] \cup \{-1\}$ | Current note ($-1$ = no note) |
| $i_v$ | $\mathbb{N}$ | Current instrument index |
| $w_v$ | $\mathbb{N}$ | Wave table position (index into shared wave table) |
| $p_v$ | $\mathbb{N}$ | Pulse table position |
| $f_v$ | $\mathbb{N}$ | Filter table position |
| $g_v$ | $\mathbb{B}$ | Gate state (on/off) |
| $h_v$ | $[64]$ | Gate timer countdown (hard restart frames remaining) |
| $\text{ad}_v, \text{sr}_v$ | $\mathbb{B}^8$ | Current ADSR values |
| $\text{wave}_v$ | $\mathbb{B}^8$ | Current waveform register value |
| $\text{freq}_v$ | $\mathbb{B}^{16}$ | Current frequency |
| $\text{pw}_v$ | $\mathbb{B}^{12}$ | Current pulse width |
| $\text{vib\_phase}_v$ | $\mathbb{Z}$ | Vibrato oscillator phase |
| $\text{vib\_delay}_v$ | $\mathbb{N}$ | Vibrato delay countdown |
| $\text{porta}_v$ | $\mathbb{B}^{16}$ | Portamento target frequency |
| $\text{pat\_pos}_v$ | $\mathbb{N}$ | Position within current pattern |
| $\text{ord\_pos}_v$ | $\mathbb{N}$ | Position within orderlist |
| $\text{dur\_count}_v$ | $\mathbb{N}$ | Ticks remaining on current event |

**Global state** $\mathcal{G}$:

| Component | Type | Description |
|-----------|------|-------------|
| $\tau$ | $\mathbb{N}$ | Tempo (frames per tick) |
| $\tau_{\text{count}}$ | $[tau]$ | Frame counter within current tick |
| $\text{filt\_cut}$ | $\mathbb{B}^{11}$ | Filter cutoff (8-bit high + 3-bit low) |
| $\text{filt\_ctrl}$ | $\mathbb{B}^8$ | Filter routing + resonance |
| $\text{vol}$ | $\mathbb{B}^4$ | Master volume |

### 3.2 The Tick Function

The playback function $P$ is defined by iterating a tick function $\tau_{\text{step}}$:

$$\tau_{\text{step}} : \mathcal{S} \to \mathcal{S} \times R$$

Each application of $\tau_{\text{step}}$ advances the state by one frame and emits a register vector $R \in \mathbb{B}^{8 \times 25}$. The full trace is:

$$P(u) = (R_0, R_1, \ldots, R_{N-1}) \quad \text{where } (\mathcal{S}_{i+1}, R_i) = \tau_{\text{step}}(\mathcal{S}_i)$$

The tick function decomposes into phases, executed in order each frame:

1. **Tempo check:** Decrement $\tau_{\text{count}}$. If zero, reset to $\tau$ and advance to phase 2. Otherwise skip to phase 5.
2. **Event processing:** For each voice, read the next event from the current pattern. Handle note-on (set $n_v$, load instrument, reset gate timer), note-off (clear gate), rest (decrement duration counter).
3. **Table stepping:** Advance wave/pulse/filter table positions. Apply waveform changes, frequency offsets (arpeggios), pulse width modulation, filter cutoff modulation.
4. **Effect processing:** Apply vibrato (sinusoidal frequency modulation from speed table), portamento (frequency slide toward target), funktempo (alternating tempo values).
5. **Register emit:** Compute the 25-byte register vector from current state. Write frequency, pulse width, waveform+gate, ADSR, filter registers.

### 3.3 USF as a Language

The set of all valid USF programs forms a language $\mathcal{U}$. A USF program is valid iff:
- All instrument references in patterns resolve to defined instruments
- All wave/pulse/filter table pointers are within bounds
- All pattern references in orderlists resolve to defined patterns
- All speed table references resolve to defined entries
- Loop targets in tables point to valid indices (no out-of-bounds, no forward jumps past end)

The token representation (Section "Token Format" in `usf_spec.md`) provides a concrete syntax. The set of valid token sequences is a context-free language (nested instrument/pattern/orderlist blocks with cross-references).

---

## 4. Layer 3: Trace Equivalence

### 4.1 Definition

Two register traces $T_1 = (R^1_0, \ldots, R^1_{N-1})$ and $T_2 = (R^2_0, \ldots, R^2_{N-1})$ are **audibly equivalent**, written $T_1 \approx T_2$, iff the number of audibly different frames is below the grade threshold.

Formally, define the per-frame per-voice difference classifier:

$$\text{diff}(R^1_i, R^2_i, v) \in \{\texttt{ok}, \texttt{note\_wrong}, \texttt{note\_jitter}, \texttt{wave\_wrong}, \texttt{wave\_jitter}, \texttt{gate\_diff}, \texttt{env\_wrong}, \texttt{env\_jitter}, \texttt{freq\_fine}, \texttt{pulse\_diff}, \texttt{pulse\_jitter}\}$$

The **audible** categories are: $\texttt{note\_wrong}$, $\texttt{wave\_wrong}$, and $\texttt{env\_wrong}$ (weakly). All others are inaudible.

**Grade A equivalence** (our target):

$$T_1 \approx_A T_2 \iff \forall v \in \{0,1,2\}: \left(\sum_{i} [\text{diff}(R^1_i, R^2_i, v) = \texttt{note\_wrong}] = 0\right) \land \left(\sum_{i} [\text{diff}(R^1_i, R^2_i, v) = \texttt{wave\_wrong}] = 0\right) \land \left(\frac{\sum_{i} [\text{diff}(R^1_i, R^2_i, v) = \texttt{env\_wrong}]}{N \cdot 3} < 0.01\right)$$

### 4.2 The Eight Tolerance Layers

The diff classifier in `sid_compare.py` applies eight layers in sequence. Each layer attempts to reclassify a frame difference from "audible" to "inaudible." The layers form a cascade: if layer $k$ reclassifies a diff, layers $k+1, \ldots, 8$ are not applied to it.

**Layer 1: Sliding window ($\pm 3$ frames).** If the rebuilt's $\text{freq\_hi}$ at frame $i$ appears in the original's frames $[i-3, i+3]$, classify as $\texttt{note\_jitter}$.

*Justification:* IRQ timing differences cause the same note to be written 1--3 frames earlier or later. The note is the same; only the exact frame differs.

**Layer 2: One-frame transient.** If frames $i-1$ and $i+1$ match between original and rebuilt, frame $i$ is a transient (isolated glitch). Classify as $\texttt{note\_jitter}$.

*Justification:* Out-of-bounds wave table reads produce different garbage bytes depending on binary layout, but the musical note is unchanged.

**Layer 3: Test-bit waveform.** If either side shows waveform $\texttt{\$08}$/$\texttt{\$09}$ near a gate transition ($\pm 3$ frames), classify as $\texttt{wave\_jitter}$.

*Justification:* The test bit ($\texttt{\$08}$) is used for hard restart -- it silences the oscillator. Its exact frame placement varies with code layout but is inaudible (the voice is being silenced anyway).

**Layer 4: Silent voice.** If both waveform registers have zero upper nibble (no oscillator active), frequency differences are inaudible. Classify as $\texttt{note\_jitter}$.

*Justification:* When no waveform is selected, the SID oscillator produces no output regardless of frequency.

**Layer 5: Sequence-level matching.** Extract the sequence of note-change events (frame indices where $\text{freq\_hi}$ changes) from both traces. If the value sequences match (same notes in same order, ignoring timing), or have $> 95\%$ LCS overlap, reclassify all $\texttt{note\_wrong}$ as $\texttt{note\_jitter}$.

*Justification:* Code layout changes shift all notes by a consistent offset. The melody is identical; only the phase differs.

**Layer 6: Global value set.** If both traces use the identical set of $\text{freq\_hi}$ values (across all active frames), reclassify $\texttt{note\_wrong}$ as $\texttt{note\_jitter}$.

*Justification:* Arpeggio and vibrato patterns cycle through the same values. Phase drift between original and rebuilt causes per-frame differences, but the set of visited pitches (and hence the perceived timbre) is identical.

**Layer 7: Vibrato phase drift ($\pm 8$ frame window).** For each wrong frame, check if the rebuilt's $\text{freq\_hi}$ appears in the original's $[i-8, i+8]$ window and vice versa. If $\geq 50\%$ of wrong frames satisfy this, reclassify all as $\texttt{note\_jitter}$.

*Justification:* Vibrato is a periodic frequency modulation. Phase drift makes the modulation peaks align to different frame indices, but the audible result (pitch wobble of the same depth and rate) is indistinguishable.

**Layer 8: Init/end grace.** The first 10 frames and last 2 frames are excluded from audible classification.

*Justification:* Init timing differences (player setup code) and dump truncation artifacts are not part of the musical content.

### 4.3 Algebraic Properties

**Reflexivity:** $T \approx T$. Trivially true (all diffs are $\texttt{ok}$).

**Symmetry:** $T_1 \approx T_2 \implies T_2 \approx T_1$. Holds for Layers 1--4 and 8 by inspection (the window checks are symmetric). Layer 5 uses greedy LCS which is not perfectly symmetric in the general case, but the $95\%$ threshold makes asymmetric cases vanishingly rare in practice. Layers 6--7 are explicitly symmetric (set equality, bidirectional window checks).

**Transitivity:** $T_1 \approx T_2 \land T_2 \approx T_3 \implies T_1 \approx T_3$. **Does not hold in general.** Example: $T_1$ has note sequence $[A, B, C]$, $T_2$ has $[A, B, D]$ (95.1% LCS with $T_1$ -- just passes), $T_3$ has $[A, E, D]$ (95.1% LCS with $T_2$), but $T_1$ vs $T_3$ has only 90% LCS (fails). In practice, transitivity failures don't arise because we always compare against the original trace, never chain equivalences.

**Consequence:** $\approx$ is a tolerance relation (reflexive and symmetric), not a full equivalence relation. This is fine for our use case: we only ever ask "is the rebuilt trace equivalent to the original?" -- never "are two rebuilt traces equivalent to each other?"

---

## 5. Layer 4: The Inverse Map (Decompilation as Constraint Satisfaction)

### 5.1 Problem Statement

Given a register trace $T = (R_0, \ldots, R_{N-1})$, find $u \in \mathcal{U}$ such that $P(u) \approx T$.

This is a constraint satisfaction problem (CSP). The variables are the components of $u$: instruments, patterns, orderlists, tables, tempo. The constraints are that $P(u)$ must produce a trace equivalent to $T$ under $\approx$.

### 5.2 Decomposition

The problem decomposes into largely independent sub-problems, each of which can be solved separately:

#### 5.2.1 Tempo Detection

Find $\tau \in [3, 16]$ such that note onsets align to a grid of period $\tau$ frames.

**Current approach** (`detect_tempo_from_frames` in `regtrace_to_usf.py`): For each candidate $\tau$, count how many observed gate-on intervals are divisible by $\tau$ (with $\pm 1$ tolerance). Choose $\tau$ maximizing this count. Prefer $2\tau$ over $\tau$ when the double also scores $> 25\%$.

**Formal model:** Let $G = \{g_0, g_1, \ldots\}$ be the set of frame indices where a gate-on transition occurs (any voice). Define the interval multiset $\Delta G = \{g_{i+1} - g_i\}$. The optimal tempo is:

$$\tau^* = \arg\max_{\tau \in [3,16]} \sum_{d \in \Delta G} \begin{cases} 1 & \text{if } d \equiv 0 \pmod{\tau} \\ 0.5 & \text{if } d \equiv \pm 1 \pmod{\tau} \\ 0 & \text{otherwise} \end{cases}$$

This is a discrete optimization over 14 candidates -- trivially solvable by exhaustive evaluation.

#### 5.2.2 Note Extraction

For each voice $v$, segment the trace into note regions: contiguous frame ranges where the voice is gated on with a stable frequency.

**Formal model:** Define the voice projection $T|_v = ((f^v_0, w^v_0, g^v_0), \ldots)$ where $f^v_i = \text{freq\_hi}(R_i, v)$, $w^v_i = \text{waveform}(R_i, v)$, $g^v_i = \text{gate}(R_i, v)$.

A **note region** is a maximal interval $[a, b)$ such that:
- $g^v_a = 1$ and $g^v_{a-1} = 0$ (gate-on transition at $a$), or $a = 0$
- $\forall i \in [a, b): g^v_i = 1$ and $w^v_i$ has an audible waveform
- The most common $f^v_i$ value in $[a, b)$ determines the note

Complications handled by `extract_voice_events`:
- **Vibrato:** Frequency oscillations of $\pm 1$--$2$ semitones that return within $\tau$ frames are not note boundaries.
- **Arpeggio:** Rapid cycling through 2--4 notes (period 2--4 frames) within a single gated region is a wave table effect, not separate notes.
- **First-wave transients:** A different waveform on frame 0 of a note (e.g., noise $\texttt{\$80}$ for a click) is an attack transient, not a separate note.
- **Legato:** Frequency change while gate stays on, sustained for $\geq \tau/2$ frames, is a new note without retriggering ADSR.

#### 5.2.3 Instrument Identification

Cluster notes by their $(\text{AD}, \text{SR}, \text{waveform})$ tuple. Each unique tuple becomes an instrument.

**Formal model:** Let $\mathcal{N}$ be the multiset of all extracted notes. Define the instrument signature $\text{sig}(n) = (\text{ad}(n), \text{sr}(n), \text{wave}(n)) \in \mathbb{B}^8 \times \mathbb{B}^8 \times \mathbb{B}^8$. The instrument set is:

$$\mathcal{I} = \{\text{sig}(n) : n \in \mathcal{N}\}$$

This gives a many-to-one map $\text{inst} : \mathcal{N} \to \mathcal{I}$.

#### 5.2.4 Wave Table Synthesis

For each instrument, extract the per-frame waveform/frequency pattern across all notes sharing that instrument. Find the consensus pattern (majority vote per frame position).

**Formal model:** For instrument $\iota \in \mathcal{I}$, let $\text{notes}(\iota) = \{n \in \mathcal{N} : \text{sig}(n) = \iota\}$. For each note $n$ of duration $d_n$ frames, extract the per-frame pattern:

$$\text{pat}(n) = ((w_0, \Delta f_0), (w_1, \Delta f_1), \ldots, (w_{\min(d_n, 8)-1}, \Delta f_{\min(d_n, 8)-1}))$$

where $w_j$ is the waveform byte and $\Delta f_j$ is the semitone offset from the settled note at frame $j$.

The consensus pattern at frame $j$ is:

$$\text{consensus}(j) = \text{mode}\{(\text{pat}(n))_j : n \in \text{notes}(\iota), |\text{pat}(n)| > j\}$$

Cycle detection on the consensus sequence yields the wave table loop structure.

#### 5.2.5 Pulse Table Synthesis

Detect pulse width modulation from per-note PW frame sequences. The pulse width on voice $v$ at frame $i$ is $\text{pw}^v_i = (\text{pw\_hi}(R_i, v) \cdot 256) + \text{pw\_lo}(R_i, v)$.

**Current approach** (`_detect_pulse_modulation`): Collect per-frame PW deltas across all notes of an instrument. If $\geq 60\%$ of deltas agree on magnitude, and the PW range exceeds $\texttt{\$100}$, emit a modulation step with that speed.

**Formal model:** For instrument $\iota$, let $\text{pw}(\iota) = \{\text{pw\_seq}(n) : n \in \text{notes}(\iota)\}$ be the set of PW time series. Compute the first difference $\Delta\text{pw}_j = \text{pw}_{j+1} - \text{pw}_j$. If $|\{\Delta\text{pw}_j : j\}|$ is dominated by one value $s$ (the speed), the pulse table is: SET initial\_pw, MODULATE speed=$s$ duration=$\infty$, LOOP.

#### 5.2.6 Filter Table Synthesis

Analogous to pulse, but tracking $\texttt{\$D416}$ (filter cutoff high) and $\texttt{\$D417}$ (filter control). Currently a stub in `regtrace_to_usf.py` (marked TODO).

#### 5.2.7 Orderlist Construction

For register-traced songs, each voice gets a single pattern containing all events. For statically parsed songs (GT2), the original pattern/orderlist structure is preserved.

**Formal model:** The orderlist is a sequence of (pattern\_id, transpose) pairs. Transpose $t$ shifts all notes in the pattern by $t$ semitones. Finding an optimal orderlist (maximizing pattern reuse) is equivalent to finding repeated substrings with transposition -- a variant of the shortest superstring problem. This is NP-hard in general but tractable for typical song structures (pattern counts < 100).

### 5.3 Constraint Formulation

Assembling the sub-problems, the full inverse map is:

$$\text{Find } u = (\tau, \mathcal{I}, \mathcal{W}, \mathcal{P}, \mathcal{F}, \text{pats}, \text{ords}) \text{ such that}$$

$$\forall i \in [N], \forall v \in \{0,1,2\}: \text{diff}(P(u)_i, T_i, v) \notin \{\texttt{note\_wrong}, \texttt{wave\_wrong}\}$$

$$\text{and } \frac{|\{(i,v) : \text{diff}(P(u)_i, T_i, v) = \texttt{env\_wrong}\}|}{3N} < 0.01$$

The decomposition in Section 5.2 makes this tractable: each sub-problem constrains a subset of variables and can be solved independently (tempo first, then notes, then instruments, then tables).

---

## 6. Layer 5: Abstract Interpretation

### 6.1 The Galois Connection

The relationship between 6502 execution and USF can be framed as an abstract interpretation:

**Concrete domain** $\mathcal{C}$: The set of 6502 execution traces (sequences of full CPU+memory states sampled at frame boundaries, projected to SID registers).

**Abstract domain** $\mathcal{A}$: The set of USF programs $\mathcal{U}$.

**Abstraction function** $\alpha : \mathcal{C} \to \mathcal{A}$: Maps a concrete trace to a USF program. This is the inverse map (Layer 4). Note that $\alpha$ is not unique -- many USF programs can represent the same trace.

**Concretization function** $\gamma : \mathcal{A} \to \mathcal{C}$: Maps a USF program to a concrete trace via the SIDfinity player. This is the forward path: $\gamma = P$.

The pair $(\alpha, \gamma)$ forms a Galois connection iff:

$$\forall c \in \mathcal{C}: c \approx \gamma(\alpha(c))$$

This is exactly the roundtrip property we verify with `sid_compare.py`. A Grade A result proves the Galois connection holds for that specific trace.

### 6.2 Soundness and Completeness

**Soundness:** $\gamma(\alpha(T)) \approx T$ for all traces $T$ in the domain. Currently holds for 59% of GT2 SIDs (Grade A). The remaining 41% have abstraction errors -- information lost in the $\alpha$ step (wrong note extraction, missing effects, unsupported features).

**Completeness:** Every feature expressible in the concrete domain has a representation in $\mathcal{A}$. USF is designed to be complete for the features used by supported players, but is extended incrementally (v0.1 through v0.10) as new features are encountered.

### 6.3 Widening: From Engine-Specific to Universal

Each SID player engine (GT2, DMC, JCH, Rob Hubbard, ...) defines a different concrete program structure, but they all produce traces in the same concrete domain $\mathcal{C}$. The abstraction function $\alpha$ can be implemented in two ways:

**Engine-specific $\alpha_{\text{engine}}$:** Parse the binary format directly (`gt2_to_usf.py`). High quality (lossless for supported features) but requires per-engine implementation.

**Universal $\alpha_{\text{trace}}$:** Analyze only the register trace (`regtrace_to_usf.py`). Lower quality but works for any engine with zero engine-specific code.

The mathematical structure is:

$$\alpha_{\text{engine}} : \text{Binary}_{\text{engine}} \to \mathcal{U}$$
$$\alpha_{\text{trace}} : \mathcal{C} \to \mathcal{U}$$
$$\alpha_{\text{trace}} = \alpha_{\text{engine}} \circ \text{Trace}^{-1} \quad \text{(when } \text{Trace}^{-1} \text{ exists)}$$

The universal path $\alpha_{\text{trace}}$ is the composition of tracing (forward) then inversion. It works for any engine but loses structural information that the engine-specific path preserves (pattern boundaries, instrument names, loop structures).

### 6.4 Abstract Domains for SID Player Analysis

Different abstract domains capture different aspects of player behavior:

| Abstract Domain | What It Captures | Tool |
|----------------|------------------|------|
| Note sequences | Pitch content per voice | `regtrace_to_usf.py` note extraction |
| Instrument signatures | (AD, SR, waveform) clusters | `regtrace_to_usf.py` instrument ID |
| Tempo lattice | Divisibility structure of event intervals | `detect_tempo_from_frames` |
| Wave table programs | Per-frame waveform/pitch programs | `_build_wave_table_from_patterns` |
| Pulse modulation | Linear PW sweep parameters | `_detect_pulse_modulation` |
| Memory access patterns | Read/write regions, periodicity | `sidxray/analyze.py` |
| Data layout | Column-major tables, pointer structures | `sidxray/xray.py` |

Each domain is an independent analysis pass. The full USF reconstruction combines results from all domains.

---

## 7. Practical Tools: Which Math Applies Where

### 7.1 Z3/SMT Solving

**Where:** Codegen verification (Layer 2 to Layer 1) and instruction sequence optimization.

**Current use:** `z3_6502.py` verifies that peephole-optimized instruction sequences produce identical register outputs for all possible input states. `z3_synth.py` synthesizes minimal-cycle instruction sequences for specific computations.

**Future use:**
- **Inverse map verification:** Given a USF program $u$ and a target trace $T$, encode $P(u) \approx T$ as SMT constraints and check satisfiability. If UNSAT, the USF program is provably wrong (useful for debugging).
- **Feature flag inference:** GT2 player variants differ in register write order, gate timing, etc. These are small finite-domain CSPs solvable by Z3.
- **Instruction selection:** The codegen phase (USF to 6502 assembly) involves choosing instruction sequences that implement USF semantics within cycle budgets. This is a bounded synthesis problem.

### 7.2 Symbolic Execution

**Where:** Driver analysis (Layer 5) -- understanding how an arbitrary SID player processes its data.

**Current approach:** Manual reverse engineering aided by `siddump --writelog` (cycle-level register write logs) and `py65` step-debugging. This is the bottleneck: each new player engine requires weeks of manual analysis.

**Proposed approach:** Symbolic execution of the play routine. Start with concrete init state, then execute the play routine symbolically, tracking which memory reads influence which SID register writes. This reveals the data format without manual analysis.

**Key insight:** Most SID players are straight-line code with indexed memory reads (no complex control flow within a single frame). The play routine reads from data tables using index registers (X, Y) and writes results to SID registers. Symbolic execution of one frame reveals the mapping from data bytes to register values.

**Challenges:** Indirect addressing (`LDA (zp),Y` where `zp` is computed from other tables) creates symbolic pointers. Self-modifying code (common in C64 -- `STA target+1` modifies an operand) requires special handling.

### 7.3 Program Synthesis

**Where:** Automated USF construction from partial specifications.

Given incomplete information (e.g., correct notes but unknown wave tables), synthesize the missing components to minimize $\text{diff}(P(u), T)$. This is a program synthesis problem over the USF DSL.

**Approach:** Counterexample-guided inductive synthesis (CEGIS). Start with a candidate USF program (from note extraction). Compute the trace, find the first divergent frame. Use the divergence to constrain the synthesis of the missing table entries. Repeat.

The USF DSL is small enough (wave table entries have 4 fields, pulse table entries have 5) that bounded synthesis over a few table steps is tractable.

### 7.4 Formal Language Theory

**Where:** Per-driver data format parsing.

Each SID player engine stores its data in a specific binary format (GT2's column-major instrument tables, DMC's interleaved pattern data, JCH's packed event streams). These formats are all regular or context-free languages over byte streams.

**Application:** Parser combinators for binary format extraction. The GT2 format (documented in `docs/gt2_data_layout.md`) is essentially a collection of fixed-width and length-prefixed arrays -- a regular language. DMC and JCH have similar structure.

**Connection to sidxray:** `sidxray/analyze.py` uses autocorrelation and periodicity detection to discover the structure of unknown binary formats. This is equivalent to learning the grammar of the data language from memory access traces.

### 7.5 E-Graphs and Equality Saturation

**Where:** USF normalization for ML training.

Multiple USF programs can represent the same musical content: different wave table implementations of the same arpeggio, different pattern factorizations of the same note sequence, different orderlist structures with transposes.

E-graphs can represent the equivalence class of USF programs compactly. Rewrite rules:

1. **Wave table fusion:** Two instruments with identical (AD, SR, waveform) but different wave tables that produce the same register output $\to$ merge.
2. **Pattern extraction:** A repeated note sequence in a single pattern $\to$ factor into a separate pattern referenced multiple times in the orderlist.
3. **Transpose normalization:** A pattern used at multiple transposes $\to$ normalize to transpose 0 and adjust note values.
4. **Duration normalization:** A sequence of rest events $\to$ single rest with summed duration.

The canonical form (normal form under all rewrite rules) is the input to the ML tokenizer.

### 7.6 Information Theory

**Where:** Choosing canonical USF representations and evaluating compression.

**Token efficiency:** A 3-minute tune at tempo 6, 50 fps = 1500 ticks. Three voices = 4500 ticks. With event-based encoding (durations attached to events, not grid-based), typical compression is 4500 ticks to 300--600 events, encoded in 2000--4000 tokens.

**Entropy bound:** Given the vocabulary of ~300 tokens and typical token sequence statistics, the entropy per token gives a lower bound on the achievable compression. If the per-token entropy is $H \approx 6$ bits, a 3000-token song has $\sim 18$ kbit = 2.25 KB of information content. For comparison, a raw GT2 binary is typically 4--8 KB and the resulting SID is 2--6 KB. USF is near the information-theoretic optimum.

**Mutual information between voices:** In many songs, voices are correlated (same rhythm, harmonically related notes). The mutual information $I(V_1; V_2)$ measures this redundancy. Exploiting it (e.g., representing voice 2 as "voice 1 transposed by a fifth") could further compress the representation, but at the cost of making independent voice editing impossible.

---

## 8. Lean Formalization Roadmap

### 8.1 Priority Order

Formalization should start with the components that are most likely to contain bugs and where machine-checked proofs would save the most debugging time.

**Priority 1: Register equivalence relation** (Layer 3)
- Define the 8 tolerance layers as Lean functions
- Prove reflexivity and symmetry (currently assumed)
- Prove that the relation is a tolerance relation (not full equivalence -- exhibit a transitivity counterexample)
- **Payoff:** Every time `sid_compare.py` is modified, the Lean proofs catch logical errors before running the 33-second regression

**Priority 2: USF tick function** (Layer 2)
- Define the USF state machine in Lean
- Prove that the tick function is total (no infinite loops, no out-of-bounds access on valid USF programs)
- Prove determinism: same initial state + same USF program = same trace
- **Payoff:** Confidence that codegen bugs are in the 6502 translation, not in the USF semantics

**Priority 3: 6502 instruction semantics** (Layer 1)
- Port `z3_6502.py`'s instruction definitions to Lean
- Prove that each instruction model matches the 6502 reference specification
- Prove that `verify_equivalence` is sound: if it returns True, the sequences are truly equivalent for all inputs
- **Payoff:** Z3 already handles this via SMT, but Lean proofs are permanent (no solver timeouts, no bit-width bugs)

**Priority 4: Inverse map correctness** (Layer 4)
- For the tempo detection sub-problem: prove that the optimal $\tau$ is unique when note onsets align perfectly to a grid
- For note extraction: specify the contract (what guarantees does `extract_voice_events` provide?) and verify it
- **Payoff:** Currently the most bug-prone part of the pipeline. Formal specs would clarify edge cases.

### 8.2 Dependency Graph

```
Layer 1 (6502 semantics) ──── standalone, no dependencies
        |
        v
Layer 2 (USF tick function) ── depends on: register type definitions from Layer 1
        |
        v
Layer 3 (Equivalence relation) ── depends on: register type definitions
        |
        v
Layer 4 (Inverse map) ── depends on: Layer 2 (to define P), Layer 3 (to define approx)
        |
        v
Layer 5 (Abstract interpretation) ── depends on: Layers 2, 3, 4 (Galois connection)
```

### 8.3 Estimated Effort

| Component | Lean LoC (est.) | Dependencies | Person-weeks |
|-----------|----------------|--------------|--------------|
| Register types + SID layout | 200 | None | 0.5 |
| Equivalence relation (8 layers) | 800 | Register types | 2 |
| Reflexivity + symmetry proofs | 400 | Equivalence defn | 1 |
| USF state machine | 1500 | Register types | 3 |
| Tick function totality | 500 | USF state machine | 1.5 |
| 6502 instruction model | 1000 | None | 2 |
| z3_6502 soundness proof | 600 | 6502 model | 1.5 |
| **Total** | **5000** | | **12** |

### 8.4 What NOT to Formalize

- **Parser code** (gt2_parse_direct.py, gt2_decompile.py): These are inherently heuristic and change frequently. Formal verification would be invalidated by every GT2 variant encountered.
- **ML training pipeline:** Statistical, not logical. Testing with metrics, not proofs.
- **Audio comparison** (audio_compare.py): PCM cross-correlation is a signal processing problem, not amenable to theorem proving.
- **Build system, CLI tools, file I/O:** Infrastructure, not core logic.

---

## 9. Worked Example: One Song Through the Framework

Consider `data/MUSICIANS/G/GoatTracker/Example.sid`. Trace through each layer:

**Layer 1:** Execute via `siddump` for 10 seconds (500 PAL frames). Produces trace $T_{\text{orig}} \in (\mathbb{B}^{8})^{25 \times 500}$.

**Layer 4 (inverse map):**
- Tempo detection: Gate-on intervals are $\{6, 12, 18, 24\}$. All divisible by 6. $\tau^* = 6$.
- Note extraction (voice 0): Gate transitions at frames $[6, 18, 30, \ldots]$. Each 12-frame region has $\text{freq\_hi}$ stable at a single value. Yields note sequence $[C4, E4, G4, C5, \ldots]$.
- Instrument identification: All notes share $(AD, SR, wave) = (\texttt{\$09}, \texttt{\$00}, \texttt{\$41})$. One instrument.
- Wave table: Frame 0 of each note has waveform $\texttt{\$81}$ (noise + gate), frame 1+ has $\texttt{\$41}$ (pulse + gate). Wave table = $[(\texttt{\$81}, 0), (\texttt{\$41}, 0), \text{LOOP } 1]$.
- Result: USF program $u$ with 1 instrument, 3 patterns, tempo 6.

**Layer 2 (forward):** Feed $u$ through `usf_to_sid.py` + `codegen_v2.py`. Produces rebuilt SID. Execute via `siddump`. Produces trace $T_{\text{rebuilt}}$.

**Layer 3 (comparison):** `sid_compare.py` compares $T_{\text{orig}}$ vs $T_{\text{rebuilt}}$ frame by frame.
- Frames 0--9: Init grace (excluded).
- Frame 12: $\text{freq\_hi}$ differs by 1 frame (original writes at cycle 19600, rebuilt at 19550). Layer 1 reclassifies: rebuilt's value matches original's frame 13. $\to$ $\texttt{note\_jitter}$.
- Frame 47: Pulse width differs by 30 ($< 200$). $\to$ $\texttt{pulse\_jitter}$.
- All other frames: $\texttt{ok}$ or $\texttt{freq\_fine}$.
- Result: 0 $\texttt{note\_wrong}$, 0 $\texttt{wave\_wrong}$, 0 $\texttt{env\_wrong}$. **Grade A.**

**Layer 5 (abstract interpretation):** $\alpha(T_{\text{orig}}) = u$. $\gamma(u) = T_{\text{rebuilt}}$. $T_{\text{orig}} \approx_A T_{\text{rebuilt}}$. The Galois connection holds for this song.

---

## 10. Open Questions

1. **Can the equivalence relation be made transitive?** If we restricted to a subset of the tolerance layers (e.g., only the $\pm 1$ frame window), would the resulting relation be a true equivalence? What is the tradeoff in false positives (songs wrongly graded A) vs false negatives (songs wrongly graded non-A)?

2. **Is the inverse map unique up to equivalence?** For a given trace $T$, is there a canonical USF program (e.g., minimal token count, or lexicographically first) that can serve as a normal form? Can e-graph rewriting reach this normal form from any valid USF program for $T$?

3. **What is the information-theoretic lower bound on USF program size?** Given a trace $T$ of $N$ frames, what is the minimum number of USF tokens needed to produce a trace $T' \approx T$? This depends on the Kolmogorov complexity of $T$ modulo the tolerance relation.

4. **Can symbolic execution of the play routine replace manual reverse engineering?** The play routine of most SID players is < 2KB of 6502 code with < 100 unique paths per frame. Is this within reach of current symbolic execution engines (e.g., angr, KLEE adapted for 6502)?

5. **What fraction of HVSC is reachable via the universal trace path alone?** If `regtrace_to_usf.py` achieves Grade A on $X\%$ of all 50,000+ SIDs without any engine-specific code, what is the theoretical maximum $X$ given USF's current feature set?
