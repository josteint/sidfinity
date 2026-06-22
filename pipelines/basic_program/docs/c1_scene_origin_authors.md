---
source_url: hvsc84.csv (corpus) + CSDb + joeylatimer.com + archive.org + web search
fetched_via: DuckDB + WebSearch + WebFetch
fetch_date: 2026-06-22
author: SIDfinity research agent (leaf, cluster 1)
content_date: 2026-06-22
reliability: high (corpus data primary; web data secondary)
---

# Basic_Program — Author Profiles

## Named Authors in HVSC Corpus (top producers)

| author | n | release group | style |
|--------|---|---------------|-------|
| Alan Bond | 62 | The 100% BASIC Project (2013-2015) | algorithmic + pseudo-RND + ROM-reading |
| Joey Latimer | 22 | Family Computing (1983-1988) | DATA/READ table-driven, 1-3 voices |
| Clark Kidd & Kathy H. Kidd | 21 | COMPUTE! Publications (1984) | game sound effects in BASIC |
| Ulf Tidstrand | 8 | Club 64 (1990 Sweden) | classical/pop covers |
| James Vogel | 8 | Shiva Publishing (1983) | music tutorial book exercises |
| James C. Hilty | 9 (incl. <?>) | MUSICIANS/H/Hilty_James/ | unknown source |
| Joseph R. Charnetski | 4 | unknown | unknown |
| David Estall | 4 | unknown | unknown |
| Ronald Mayer | 4 | Homecomputer/Tronic Verlag 1985 | German magazine games |
| Tim Knight & Darren LaBatt | 3 | Howard W. Sams 1983 | book listings |
| Bob Yewchuk | 3 | self (1982-1984) | early independent |
| Pawel Ruczko (V-12) | 3 | unknown | unknown |

Note: `<?>` author = 120 tunes (25% of corpus) — HVSC has not identified the author.

---

## Alan Bond — The 100% BASIC Project

**Period:** 2013-2015 (BASIC work); earlier PSID work 1988-1993
**Archive:** MUSICIANS/B/Bond_Alan/ (79 total SIDs; 62 are BASIC)
**HVSC:** All 62 BASIC tunes are RSID with `released = "20XX The 100% BASIC Project"`

**Earlier non-BASIC work (PSID):** "Double Lizard" (1988), "Aztec quick-step" (1993),
"Blizzard" (1993), "Brain phone" (1993), "Formula 6" (1993), etc. — these are machine-code
SID compositions from an earlier era, predating the BASIC project by 20 years.

**BASIC programming style summary** (from detokenization of HVSC files):

1. **ROM-peeking melodies** (Two_Lines_of_Code_1, Two_Lines_of_Code_2, etc.):
   Reads bytes from fixed ROM regions ($A000-$BFFF = BASIC ROM, $E000-$FFFF = KERNAL ROM)
   or I/O areas ($DF00-$DFFF) via `PEEK()`, applies arithmetic to get frequencies.
   `M=57272:PEEK(M)/28` — reads $DFF8 area and divides by 28.
   `TI AND PEEK(M+64)` — combines jiffy timer with ROM byte (nondeterministic in replay).

2. **Seeded-RND generative** (Argument_Emulator, Glass_Jaw, High_Five, etc.):
   `S=RND(-N)` seeds with fixed value, then `RND(1)` drives note choices.
   Reproducible with same seed; but `TI` and `GETAA$` calls can introduce replay drift.

3. **Bit-manipulation patterns** (Two_Lines_of_Code_2, Interlace, etc.):
   `T=T+1AND127` — 7-bit counter. `TAND A`, `TAND B` — bitwise AND for index.
   `POKES+L,PEEK(M+Z+L*9)AND28` — ROM byte AND 28 (mask to waveform bits 2,3,4).

4. **Pure expression music** (some tunes): No DATA, no RND seed — uses math expressions
   over loop counters and timer to generate note patterns inline.

**Key tune — No_SID_Pokes_Used_BASIC.sid** (2014): The title claims NO POKE to SID
registers. This implies the music is produced by the BASIC interpreter's bus activity
or by some other side-channel. Needs detokenization to confirm mechanism.

**CSDb status:** Alan Bond appears in the CSDb SID database (search confirms 79 entries),
but has no formal group page. The "100% BASIC Project" is not registered as a group.
He is an independent musician operating outside the formal demoscene group structure.

---

## Joey Latimer — Family Computing / MicroTones

**Period:** 1983-1988 (main active period), family computing era
**Archive:** MUSICIANS/L/Latimer_Joey/ (22 BASIC tunes)
**Website:** https://joeylatimer.com/history.html

**Background:** Founding contributor and editor at Family Computing magazine and
K-Power (Scholastic Inc.) starting 1983. Created "MicroTones" — self-described as
"the first computer music column I know of in a magazine." Column featured type-in
music programs for C64 and other computers.

**Published books (co-authored for Scholastic):**
- The K-Power Collection
- 10 Starter Programs for Family Computing
- The Best of Family Computing Programs (Vol. I and II)
- Amazin' Games

**BASIC style:** DATA/READ table-driven multi-voice music. Standard recipe:
- Voice frequency tables encoded as DATA HI, LO pairs
- Busy-wait FOR loops for duration/tempo
- Usually 1-2 voices; some 3-voice

**Magazine archive:** All Family Computing issues (Sep 1983 – Dec 1988) available at
https://archive.org/details/FamilyComputingIssue041983Dec (64 issues + specials).
Joey Latimer's PDF archives of specific articles are at joeylatimer.com — includes
his K-Power MicroTones columns with type-in song listings (Curley Calypso etc.).

**Known songs in HVSC (sample):**
- 12 Days of Christmas (1986)
- Christmas Tree (1983 — one of the earliest)
- Hacksville Hoedown (1985 — the "famous" one, mentioned in user memory)
- Hacksville Hoedown is available on YouTube (per his site)
- 22 total tunes spanning 1983-1988

---

## Clark Kidd & Kathy H. Kidd — COMPUTE! Games for Kids

**Period:** 1984
**Archive:** MUSICIANS/K/Kidd_Clark_and_Kathy/ (21 tunes)
**Source:** _Commodore 64 Games for Kids_, COMPUTE! Publications, 1984
**Archive.org:** https://archive.org/details/Compute_s_64_Games_for_Kids

**Context:** Educational programming book — 30 games for children covering
topics (music, astronomy, spelling, math). The 21 BASIC SIDs are the music/sound
components from these games (title screens, sound effects, game audio).

**BASIC style:** Simple game sound in BASIC — POKEs for tones, beeps, simple tunes.
These are NOT standalone music compositions; they are incidental sound within
games. However, they ARE tokenized BASIC with SID POKEs, so HVSC classifies them
as Basic_Program. The Alphabet Soup, Spelling Bee, Element Man, etc. titles confirm
they are game tunes.

---

## James Vogel — The C64 Music Book

**Period:** 1983
**Archive:** MUSICIANS/V/Vogel_James/ (8 tunes)
**Source:** _The Commodore 64 Music Book: A Guide to Programming Music and Sound_,
James Vogel & Nevin B. Scrimshaw, Birkhäuser Boston 1983 (US); Shiva Publishing 1984 (UK)
**Archive.org:** https://archive.org/details/The_Commodore_64_Music_Book
**PDF:** https://c64.xentax.com/images/The_Commodore_64_Music_Book.pdf

**Context:** Dedicated music programming tutorial book (~146 pp). Covers SID chip
registers, waveforms, frequency tables, BASIC music composition. The 8 HVSC tunes
are example programs from the book: Demo, Jazz Bass Line, Musette, Oh Suzannah,
Pots and Pans, Schumann, Sync Bass Line, Untitled.

**BASIC style:** Multi-voice compositions with full SID register setup. The most
musically sophisticated of the book-sourced BASIC programs — "Jazz Bass Line" and
"Sync Bass Line" suggest polyphonic output.

---

## Ulf Tidstrand — Club 64 (1990, Sweden)

**Period:** 1990
**Archive:** MUSICIANS/T/Tidstrand_Ulf/ (8 tunes)
**Source:** Club 64 (Swedish Commodore 64 club/newsletter)
**Archive.org examples:** "Lång eller kort vokal" and "Rysk roulette" by Ulf Tidstrand
& Club 64 archived at archive.org.

**Content:** Classical and pop arrangements in BASIC — "My Bonnie", "Tema Ur Chess",
"Where I Want to Be", "Allt Som Jag". Appears to be a hobby musician in the Swedish
C64 community.

---

## Tim Knight & Darren LaBatt — Howard W. Sams

**Period:** 1983
**Archive:** MUSICIANS/L/LaBatt_Darren/ (4 tunes)
**Source:** _Commodore 64 BASIC Programs_, Timothy Orr Knight & Darren LaBatt,
Howard W. Sams & Co., 1983 (ISBN 0-672-22402-7 / 0-672-26171-5 for 2nd ed.)
**AbeBooks:** https://blackwells.co.uk/bookshop/product/9780672224027

4 tunes: Bach Minuet, Computer Lullaby, Our First Song, Sounds of Dixie.
The authorship of Bach Minuet is Darren LaBatt alone; the others are joint.

---

## UNKNOWN Authors (120 tunes)

120 tunes (24.7% of corpus) have `author = "<?"`. These cluster in:
- `DEMOS/UNKNOWN/` (65 tunes) — unattributed programs, often with known publishers
  (Free Spirit Software, Softidea) but unknown individual authors
- Game tunes (GAMES/ dirs) where the game programmer is unknown
- Some DEMOS/ tunes where the magazine scan is known but author not yet identified

The Softidea "Videobreak" series (9 tunes, 198?) is entirely unattributed.
The Free Spirit Software pack (10 tunes) is entirely unattributed.
These two groups together account for 19 of the 120 unknown-author tunes.
