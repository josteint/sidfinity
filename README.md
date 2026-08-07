# The SIDfinity Project

The Commodore 64 has a built-in programmable sound generator chip, the Sound Interface Device (SID). Music and sound effects have been written for it since 1982. The [High Voltage SID Collection↗](https://www.hvsc.c64.org/) preserves the vast majority of this content. Much of it comes out of the demoscene, [recognized↗](https://demoscene-the-art-of-coding.net/news/) as national UNESCO cultural heritage in many countries.

A SID file is a standardized container for machine code and data that when run on a C64 writes a timed series of values to the registers of the SID chip which produces audio. [Music Information Retrieval↗](https://en.wikipedia.org/wiki/Music_information_retrieval) (MIR) deals with extracting information from music, like pitch and beat tracking, key and chord estimation, genre classification, structural segmentation, fingerprinting, and transcription.

When doing MIR on SID music there are three natural candidate "information channels" we can try to extract information from: (a) Sampled audio, for example 44.1 kHz 16 bit mono, (b) The timeseries consisting of SID register writes spanning the song length, (c) The SID binary.

There is no well known prior art on (a), and I think that is not surprising. One reason is size: The total size of [Stone Oakvalley's Authentic SID Collection↗](https://www.6581-8580.com/) which in the order of terabytes. Another reason is that going from (c) to (b) to (a) we lose information in each step, so (a) is the most lossy one. For (b) we have several projects that do various kinds of MIR: [siddump↗](https://github.com/cadaver/siddump), [desidulate↗](https://github.com/anarkiwi/desidulate), [sidmancer↗](https://github.com/slajerek/sidmancer), [zig64↗](https://github.com/M64GitHub/zig64), [zak↗](https://github.com/jarikomppa/zak), [sidviz↗](https://github.com/jagenjo/sidviz), [sid-analysis-tools↗](https://github.com/sandlbn/sid-analysis-tools), [nesmdb↗](https://github.com/chrisdonahue/nesmdb). A notable project that does (b) for the NES platform is [NES-MDB↗](https://github.com/chrisdonahue/nesmdb). For (c) 

> [!NOTE]
> The goal of this project is to address this by defining a text format that represents SID music declaratively, as musical events rather than as code.

 

## License

MIT for the SIDfinity code; some bundled components carry their own licenses (GPL, and third-party C64 material kept for preservation). See [LICENSE](LICENSE) for the full breakdown.
