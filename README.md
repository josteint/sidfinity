# The SIDfinity Project

Project goal: An elegant canonical representation of SID files.

The Commodore 64 has a built-in programmable sound generator chip, the Sound Interface Device (SID). Music and sound effects have been written for it since 1982. The [High Voltage SID Collection](https://www.hvsc.c64.org/) preserves almost all of this content. Much of it comes out of the demoscene, [recognized](https://demoscene-the-art-of-coding.net/news/) as national UNESCO cultural heritage in many countries.

A SID file is a container format for machine code and data that when run in a C64 environment writes a timed series of values to the registers of the SID chip which produces audio. [Music Information Retrieval](https://en.wikipedia.org/wiki/Music_information_retrieval) (MIR) deals with extracting information from music.

When doing MIR on SID music, some natural information channels are

- (a) The music source code
- (b) The SID binary
- (c) The timeseries consisting of SID register writes
- (d) Sampled audio

There is no well known prior art on (d), and I think that is not surprising. One reason is size. The total size of [Stone Oakvalley's Authentic SID Collection](https://www.6581-8580.com/) is in the order of terabytes. Another reason is that every step from (a) to (d) loses information and (d) is the most lossy channel.

For (c) some known projects do various kinds of MIR on register write logs from [siddump](https://github.com/cadaver/siddump) or [VICE](https://vice-emu.sourceforge.io/): [desidulate](https://github.com/anarkiwi/desidulate), [SIDmancer](https://theoasisbbs.com/ai-creates-sid-music-inside-sidmancers-machine-learning-demo/), A notable project that does something similar to (c), but for the NES platform is [NES-MDB](https://github.com/chrisdonahue/nesmdb). Representing any SID file as a sequence of register writes is easy but not elegant.

(a) would be the ideal channel for the project goal if the source code for most SID music had been generally available. It isn't, so that leaves us with (b).

... to be continued.

## License

MIT for the SIDfinity code; some bundled components carry their own licenses (GPL, and third-party C64 material kept for preservation). See [LICENSE](LICENSE) for the full breakdown.
