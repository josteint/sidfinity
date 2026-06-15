# SIDfinity

SIDfinity's goal is **machine learning on C64 SID music** — training models on
the tens of thousands of tunes in the
[High Voltage SID Collection](https://www.hvsc.c64.org/).

Doing that requires the music in a form a model can learn from, independent of
the many different C64 player engines it was originally written with. So the
foundation is the **Unified SID Format (USF)**: an engine-neutral
representation of a tune's musical content.

## Status

⚠️ **Alpha — Stage 1: developing USF.** Current work is building the USF
representation and the pipeline that translates SID player engines into it.
The machine-learning stage comes later, once USF is in place.

## License

MIT for the SIDfinity code; some bundled components carry their own licenses
(GPL, and third-party C64 material kept for preservation).
See [LICENSE](LICENSE) for the full breakdown.
