# The SIDfinity Project

The Commodore 64 has a built-in programmable sound generator chip, the Sound Interface Device (SID). Music and sound effects have been written for it since 1982, first for games and later also for [demos↗](https://en.wikipedia.org/wiki/Commodore_64_demos). The [High Voltage SID Collection↗](https://www.hvsc.c64.org/) preserves the vast majority of this music. Much of it comes out of the demoscene, [recognized↗](https://demoscene-the-art-of-coding.net/news/) as intangible cultural heritage in eight countries.

A SID file contains music data together with machine code that drives the chip when run on a real or emulated C64. The format is a standard, but only at the container level: the musical content is arbitrary code, so a tune exists only as the side effects of executing it. Being operational rather than declarative, SID resists the symbolic analysis that [Music Information Retrieval↗](https://en.wikipedia.org/wiki/Music_information_retrieval) depends on.

The goal of this project is to address this by defining a text format that represents SID music declaratively, as musical events rather than as code.

 

## License

MIT for the SIDfinity code; some bundled components carry their own licenses (GPL, and third-party C64 material kept for preservation). See [LICENSE](LICENSE) for the full breakdown.
