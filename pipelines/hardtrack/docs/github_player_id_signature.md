# HardTrack Composer — sidid / player-id signature (engine identification)

> **Provenance.** Fetched live 2026-06-13 from the two canonical C64
> playroutine-identity signature databases:
>   - WilfredC64/player-id (modern Rust port, actively maintained) —
>     `config/sidid.cfg` on branch `main`.
>   - cadaver/sidid (the original "quick & dirty" C scanner) —
>     `sidid.cfg` on branch `master`.
> Both are the upstream of HVSC's engine labels and DeepSID's player tags.

## Task 3 result: the canonical HardTrack signature is SINGLE (no sub-variants)

Both databases contain **exactly one** signature block under the name
`HardTrack_Composer`, with **one** byte pattern and **no AND/`&&` continuation**:

```
HardTrack_Composer
0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB 1D ?? ?? 8D ?? ?? 8D 17 D4
```

- WilfredC64/player-id `config/sidid.cfg`: 1 name, 1 pattern. ✔
- cadaver/sidid `sidid.cfg`: 1 name, 1 pattern. ✔ (identical bytes)

This **matches verbatim** the signature quoted in the SIDfinity task brief.
There are no `HardTrack_Composer V1.0` / `V1.1` split signatures, no
`_BHG` / packer variants — the identifier is a single pattern that fires
across the whole ~1,170-tune HVSC corpus. The V1.0 / V1.1 distinction
documented elsewhere (release notes, depacker) is **not** reflected in the
identity DB; both player versions match this one signature.

### Reading the signature (corroborates the write model)

The `??` bytes are wildcards (relocation-variable addresses). The fixed bytes
decode to the engine's per-frame note-load / waveform-select sequence:

| Bytes | 6502 | Meaning |
|---|---|---|
| `0A 0A` | `ASL A` ×2 | scale an index ×4 |
| `8D ?? ??` | `STA $xxxx` | store (reloc addr) |
| `68` | `PLA` | pull (from a `PHA`'d value) |
| `29 F0` | `AND #$F0` | keep hi nibble |
| `85 FB` | `STA $FB` | zero-page scratch |
| `AD ?? ??` | `LDA $xxxx` | load (reloc addr) |
| `29 0F` | `AND #$0F` | keep lo nibble |
| `05 FB` | `ORA $FB` | recombine hi|lo nibble → a control byte |
| `1D ?? ??` | `ORA $xxxx,X` | OR in a per-voice table entry |
| `8D ?? ??` | `STA $xxxx` | store the assembled value |
| **`8D 17 D4`** | **`STA $D417`** | **write SID filter-resonance/routing reg ($D417)** |

The terminal `8D 17 D4` (`STA $D417`) is the anchor: HardTrack's play routine
assembles a nibble-merged control value and lands it in `$D417`. This is a
concrete per-frame write-model touch-point — the extractor/composer must emit a
`$D417` write produced from a hi-nibble | lo-nibble | per-voice-table-`,X`
recombination each frame. (Filter routing / resonance live in `$D417`'s layout:
hi nibble = resonance, lo nibble = filter-enable bits per voice + ext.)

## Downstream consumers (no extra HardTrack metadata)

- **DeepSID** (Chordian/deepsid) surfaces player names via the same sidid
  signature set; no independent HardTrack decoder or richer metadata was found
  in its repo. (Its songlength DB carries no engine strings.)
- **HVSC** engine attribution ("HardTrack_Composer") derives from this same
  signature.

## Sources

- https://github.com/WilfredC64/player-id — `config/sidid.cfg`, `doc/Signature_File_Format.txt`
- https://github.com/cadaver/sidid — `sidid.cfg`, `sidid.nfo`
- https://github.com/Chordian/deepsid
