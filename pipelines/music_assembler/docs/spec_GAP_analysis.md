<!--
provenance:
  source_url: (synthesis — multiple sources cited inline)
  fetched_via: WebSearch + WebFetch + cadaver/sidid signature + ice00/jc64 source clone + primary disassembly
  fetch_date: 2026-06-13
  author: SIDfinity research session (Claude)
  content_date: 2026-06-13
  reliability: HIGH for "what exists online" (exhaustive search done); the extraction plan
               is grounded in spec_player_RE_grounded.md (one binary traced end-to-end).
-->

# Music Assembler — online-documentation GAP analysis + extraction plan

## Verdict (REVISED): no narrative spec exists, BUT a public hand-annotated disassembly does.

Initial conclusion was "packed format undocumented." That was WRONG in one
important way: **the JC64dis project (`ice00/jc64`, GPL-2) ships hand-annotated
disassemblies of the Music Assembler player** (`doc/example/MusicAssembler.dis`,
`musicAssembler_.dis`, plus `VoiceTracker.dis`) authored by Stefano Tognon
(Ice Team). These resolve the entire packed-format + per-frame-write gap —
data-section layout, the full pattern (sequence) opcode map, the effect runner,
and the preset/arpeggio/track formats. See `spec_player_jc64dis.md` (structured)
and `jc64dis_MusicAssembler_annotations.txt` (raw dump). They are independently
cross-checked against this session's own disassembly (`spec_player_RE_grounded.md`)
and agree (e.g. `voiceSidIndex` == the `$C0C6,X` voice-base array).

So: **NO prose/tutorial spec exists**, but a usable RE artifact does, and we now
have two independent RE traces. The format is effectively documented for our
purposes. What still does NOT exist online:

| Source | What it gives | What it does NOT give |
|--------|---------------|-----------------------|
| MC's official manual (CSDb #94388, vendored here as `csdb_manual_0_01b.*`) | The full EDITOR data model (presets, arps, tracks, sequences, filter). | The packed encoding. Author explicitly: "intricate, to many people unreadable data which is disassembled by the player routine while playing." |
| `cadaver/sidid` `sidid.cfg` (vendored as `tmp_sidid.cfg`) | A 20-byte recognition signature (`Music_Assembler/MC`) = the seq-pointer-fetch routine. | No layout/relocation table. |
| `ice00/jc64` (JC64dis) — GitHub, GPL-2, cloned this session | **`doc/example/MusicAssembler.dis` + `musicAssembler_.dis` + `VoiceTracker.dis`: hand-annotated disassembly projects** (gzip JC64dis format) with full routine labels, per-`$D4xx`-write comments, the data-section layout header, and the pattern opcode map. The single richest RE source found. | The recognition engine itself just loads the sidid.cfg signature at runtime; the structural knowledge lives in the bundled `.dis` example projects, not in code. |
| JITT64 (Ice Team) | Claims to import MASM/VoiceTracker PSIDs into its tracker. | Closed conversion logic; no published format doc. Worth probing as a black-box oracle if needed (see leads). |
| Lemon64 / forum threads | History, "VoiceTracker is based on the MASM player," version list. | No format internals. |

**Conclusion:** the packed format must be reverse-engineered from the HVSC
binaries. This session has already done the first end-to-end trace — see
`spec_player_RE_grounded.md`. That doc, not this one, is the parsing target.

## Version landscape (fingerprint before bulk extraction)

- **V1.0** — Dutch USA-Team, 1989 (CSDb #94388). The grounded trace is a V1.0
  member (`OPM/Sid_Slam.sid`).
- **V1.1** — Triad, 1991 (CSDb #27470).
- **V1.4** — Triad, 1994 (CSDb #27472).
- **VoiceTracker** (Science 451, 1990; CSDb #10756) — derivative engine built
  on the MASM player; the sidid.cfg has a SEPARATE `VoiceTracker` signature
  that overlaps MASM's structure. HVSC may classify some VoiceTracker tunes
  under Music_Assembler — verify.

Treat these like the FC standard-player census: fingerprint the 6,351 HVSC
members (reloc-invariant) into version groups before assuming one layout.
(`project_fc_fingerprint_and_standard` is the template; `pipelines/future_composer/engine_fingerprint.py`.)

## sidid signature decode (the reloc-invariant anchor)

`Music_Assembler/MC`:
```
BC ?? ?? C0 FE D0 09  BD ?? ?? 29 FE 9D ?? ??  60  B9 ?? ?? 85
LDY $C08D,X           ; ?? ?? = seq# array (load-relative)
CPY #$FE / BNE +9     ; $FE = stop sentinel
LDA $C084,X / AND #$FE / STA $C084,X   ; on stop: clear gate bit, fall to RTS
RTS
LDA $C675,Y / STA $..  ; ?? ?? = SEQ POINTER TABLE HI base, indexed by seq#
```
The two `??`-operands you recover from a matched binary give you, directly:
1. the **per-track seq# array** (`$C08D` here), and
2. the **sequence pointer-table HI base** (`$C675` here) — and the LO base is
   the very next `LDA abs,Y` (`$C669`).

That is the reloc-invariant hook into the whole data section: from the seq
pointer tables you can walk every sequence stream; from the voice-update
routine's `LDA presetTable,Y` ($C235) you get the preset table base.

## EXTRACTION CHECKLIST (what to lift from each binary → USF)

Ordered, each item grounded in `spec_player_RE_grounded.md`:

1. **Anchor the player base** by finding the sidid signature; entry offsets
   are base+$00 (IRQ), base+$21 (play), base+$48 (init).
2. **Song speed**: the reload constant at the `LDA #$xx / STA <speed counter>`
   in play() ($C034: `LDA #$02`). One byte → USF tempo.
3. **Track-init tables** (3 entries): pointer table at the init loop's
   `LDA tableLO,X` / `LDA tableHI,X` ($C4B9/$C4BC here) → each track's initial
   (seq#, transpose, repeat). These are the three top-level ORDERLISTS.
4. **Orderlist / track stream**: follow each track's pointer to its
   (seq#, transpose, repeat) list; sentinels `$FE`=stop, `$FF`=loop.
   Transpose is the HIGH nibble (`LSR×4`).
5. **Sequence pointer tables** (LO @ seqPtrLo, HI @ seqPtrHi), indexed by
   seq#. Gives the address of every monophonic sequence stream.
6. **Sequence (pattern) stream decode** — opcode map now AUTHORITATIVE from
   the JC64dis annotation (see `spec_player_jc64dis.md`):
   - `$00..$50` = NOTE (index into freq tables), **followed by** a duration/
     effect byte `BB`: low 5 bits = duration; `BB` `001x`=SLIDE (+2 bytes:
     CC lo-freq, DD hi-freq), `100x`=FILTER (+2 bytes: CC cutoff/speed nibbles,
     DD frame duration), `010x`=HOLD.
   - `$60..$7F` (`011x xxxx`) = REST with release, duration = low 5 bits.
   - `$A0..$AF` (`1010 xxxx`) = PRESET select (id = low nibble).
   - `$80..$9F` / `$B0..$FF` = HOLD/legato (duration = low 5 bits).
   - `$FF` = end of pattern (advance the orderlist).
   ~~OPEN~~ RESOLVED via JC64dis.
7. **Preset table** (8 bytes/preset, base from the `usePreset` `LDA presetTable,Y`):
   AD, SR, waveform/control, pulse amplitude lo/hi, "Vibrato delay+speed value",
   "Fx + arpeggio value" (effect-flags byte + arpeggio-table index), pulse
   level/speed. ~~OPEN~~ the +4/+6 fields are the vibrato-delay+speed byte and
   the Fx+arpeggio byte (JC64dis labels `Vibrato delay+speed value` /
   `Fx + arpeggio value`).
8. **Arpeggio table** (steps of waveform / note-offset (absolute `<` or relative)
   / low-pass filter value; `$FF` loop / `$FE` stop) — `makeArpeggio` confirms
   the 3-field step. Located via the arpeggio pointer table at the head of the
   data section (`arpeggioTableLo[]`/`arpeggioTableHi[]`).
9. **Freq tables** (LO + HI, one entry/note) — operands of the note handler's
   `LDA freqLo,Y` / `LDA freqHi,Y` ($C437/$C1C5). Standard PAL note table;
   likely identical across members → can be a shared constant, verify.

## Per-frame SID write model (for the Mode-1 instruction-stream verdict)

From `spec_player_RE_grounded.md`, the writes the rebuild must reproduce
each play():
- Per voice (Y2 = voice*7 = $00/$07/$0E): `$D400+Y2`/`$D401+Y2` (freq),
  `$D402+Y2`/`$D403+Y2` (PW), `$D404+Y2` (ctrl/gate), `$D405+Y2` (AD),
  `$D406+Y2` (SR).
- Global (absolute, no indexing): `$D416` (cutoff HIGH only — `$D415` never
  written), `$D417` (res+routing, init $F0), `$D418` (mode/vol, init $1F).
- Init prefix every subtune: `$D418=$1F`, `$D417=$F0`. This is exactly the
  kind of fixed init prefix the init-trichotomy comparator handles — capture
  with `siddump --writelog`, verify with `compare_instruction_stream`.

## What is NOT a gap

- Editor model: fully documented (manual). USF mapping is mostly mechanical.
- Entry points + the per-frame register set: now grounded (this session).
- Recognition + version detection: sidid signature + CSDb version list.

## Leads to follow

- **Open the JC64dis `.dis` projects in JC64dis itself** — `ice00/jc64`
  `doc/example/{MusicAssembler,musicAssembler_,VoiceTracker}.dis` are full
  annotated projects (gzip JC64dis format; this session extracted the strings
  to `jc64dis_MusicAssembler_annotations.txt`, but the per-address asm + the
  exact table addresses live in the binary project records). Loading them in
  JC64dis (or parsing the `.dis` cell records) yields the complete labelled
  listing with operands — the highest-fidelity remaining artifact. The three
  examples cover load $5000 (MC), $1000 (Ouwehand), and VoiceTracker.
- **Verify the opcode map against a 2nd binary** — the pattern map in
  `spec_player_jc64dis.md` is from MC_01; confirm against OPM/Sid_Slam by
  finishing the `$C0D2`/`$C150` trace (now just a confirmation, not discovery).
- **JITT64 (Ice Team)** claims MASM/VoiceTracker PSID import — a closed-source
  oracle. If the opcode map proves stubborn, run a known MASM tune through
  JITT64 and diff its imported pattern/instrument view against our decode.
- **VoiceTracker V1.0 (CSDb #10756, Science 451)** + the Pawel Soltysinski
  "Voicetracker v5" on Internet Archive (`d64_Voicetracker_v5_1990_...`) —
  derivative engine; its editor disk may carry a player whose structure
  illuminates the shared MASM lineage. Note the distinct `VoiceTracker` sidid
  signature.
- **MASM V1.1 / V1.4 by Triad (CSDb #27470 / #27472)** — pull these to
  diff against V1.0 for the version-group fingerprint.
- **MC's own channels** — Marco Swagerman's YouTube (user `marcoswagerman`)
  and the CSDb release comments (#94388); the author is active and has
  answered format questions in scene threads. Direct contact is a viable last
  resort for the packed-format details.
- **Non-English scene**: MASM sold "mainly in Germany" via Markt+Technik, so
  forum64.de and German C64 diskmags are the most likely place for a German
  player analysis; not yet found. Polish scene (VoiceTracker v5 is Polish-
  authored) is the most likely VoiceTracker-derivative source.
