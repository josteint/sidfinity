---
source_url: archive.org + web search results
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-22
author: SIDfinity research agent (leaf, cluster 1)
content_date: 2026-06-22
reliability: medium (confirms existence; content depth not fully verified)
---

# Basic_Program — Online Archives and Source Listings

This file documents WHERE the original source programs can be found online,
for use as ground truth to validate our detokenizer and extractor.

## A. Complete online archives

### Commodore 64 Programmer's Reference Guide (1982)
The exact source for 10 `C_Prog_Ref_Guide_example_XX` SIDs.
- **Full PDF (archive.org):** https://archive.org/details/Commodore_64_Programmers_Reference_Guide_1983_Commodore
- **Chapter 4 online:** https://www.devili.iki.fi/Computers/Commodore/C64/Programmers_Reference/Chapter_4/page_184.html
- **PDF mirror:** https://www.commodore.ca/manuals/c64_programmers_reference/c64-programmers_reference_guide-04-programming_sound.pdf

Music examples are in Chapter 4 "Programming Sound and Music on Your Commodore 64"
starting at page 184. Examples 01-10 in HVSC correspond to numbered program examples
throughout this chapter. Confirmed by detokenization.

### The Commodore 64 Music Book (James Vogel, 1983)
The exact source for 8 `MUSICIANS/V/Vogel_James/` SIDs.
- **archive.org:** https://archive.org/details/The_Commodore_64_Music_Book
- **Full text OCR:** https://archive.org/stream/The_Commodore_64_Music_Book/The_Commodore_64_Music_Book_djvu.txt
- **PDF:** https://c64.xentax.com/images/The_Commodore_64_Music_Book.pdf

Program listings should appear in the text. Cross-referencing the HVSC program names
(Jazz Bass Line, Pots and Pans, Oh Suzannah, Musette, etc.) against the OCR text
would confirm which chapter each tune appears in.

### COMPUTE!'s Gazette (1983-1990)
Source for some COMPUTE!-attributed tunes; also verifiable cross-source.
- **archive.org full run:** https://archive.org/details/compute-gazette
- **Index (searchable):** https://www.atarimagazines.com/compute/gazette/
- **Telarity index:** https://telarity.com/~dan/cbm/compute-gazette.idx

### Family Computing (1983-1988)
Source for Joey Latimer's 22 tunes.
- **archive.org (64 issues + specials):** https://archive.org/details/FamilyComputingIssue041983Dec
- **Joey Latimer's own PDF archives:** https://joeylatimer.com/history.html
  (direct article PDFs including K-Power MicroTones columns with music listings)

### Commodore 64 Games for Kids (Kidd & Kidd, COMPUTE! 1984)
Source for 21 `MUSICIANS/K/Kidd_Clark_and_Kathy/` SIDs.
- **archive.org:** https://archive.org/details/Compute_s_64_Games_for_Kids
  (downloadable PDF, EPUB, plain text)

**NOTE:** Some of the individual game programs from this book are also independently
archived at archive.org. For example:
- A-Maze-Ing: https://archive.org/details/amazeing.c64
- Lawn Mower: https://archive.org/details/lawnmower.c64

These are PRG format files; the BASIC listings in them should match the HVSC SIDs
if the book's D64/T64 disk programs are verbatim rips.

### Howard W. Sams — Commodore 64 BASIC Programs
Source for 4 `MUSICIANS/L/LaBatt_Darren/` SIDs.
- AbeBooks listing: https://blackwells.co.uk/bookshop/product/9780672224027
- No archive.org scan found yet — physical book only (see Leads section).

### Compute mit (German magazine, 1984-1987)
- 1984/38 archive.org: https://archive.org/details/compute-mit-1984-38
- 1985/07: https://archive.org/details/compute-mit-1985-07
- 1985/09: https://archive.org/details/compute-mit-1985-09
- 1985/05: https://archive.org/details/compute-mit-1985-05
- 1985/12: https://archive.org/details/compute-mit-1985-12

### Ahoy! Magazine (1984-1989)
Source for David Barron's 1986 tune and 2 more Ahoy! tunes (1987).
- Complete run: https://www.commodore.ca/commodore-gallery/commodore-ahoy-magazines-issue-31-through-61-special-editions/
- Issues 1-30: https://www.commodore.ca/commodore-gallery/commodore-ahoy-magazines-issue-1-through-30/

## B. CSDb — what IS and IS NOT there

- **CSDb SID search for "Alan Bond"** returns 79 entries, all with audio playback.
  URL form: https://csdb.dk/sid/?id=NNNNN (e.g. 51267 = No SID Pokes Used)
- **"The 100% BASIC Project"** does NOT have a group page on CSDb. Not registered.
- **Alan Bond** does NOT have a scener profile page linked from search results.
  (The scener ID 14973 for "Bond" on CSDb is a DIFFERENT person: Houbba/Newness, Sweden.)
- CSDb SID entries do link to HVSC paths but do not store source BASIC listings.

## C. Source listings as HVSC files themselves

Because these are RSID format with a tokenized BASIC payload at $0801, the HVSC .sid
files ARE the source code archives — the tokenized BASIC program can be extracted by:
1. Skip the 124-byte PSID v2 header
2. Skip the 2-byte PRG load address ($01 $08 = $0801)
3. Walk the BASIC link-pointer chain
4. Detokenize via the Commodore BASIC V2 token table ($80-$CB)

Our working detokenizer (proven in `00_local_recon_findings.md`) handles this correctly.
So for any BASIC_Program SID in HVSC, we already have the source listing.

The external book/magazine archives are valuable for:
- Confirming we detokenized correctly (compare with scanned listing)
- Finding any CORRECTIONS (typos in BASIC that were fixed by HVSC ripper)
- Identifying which specific issue/page a tune came from (provenance)
- Finding tunes that may be in the magazines but NOT yet in HVSC

## D. Potential unlisted tunes

The magazine archives are large and our 486-tune HVSC set may not be exhaustive.
Known gaps:
- Ahoy! printed BASIC music listings beyond David Barron's 1986 entry
- COMPUTE!'s Gazette has music programs not yet in HVSC (too much work to rip per FAQ)
- 64'er magazine has music listings (only 4 identified in HVSC so far)
- Hebdogiciel had a full run; only 8 of its BASIC programs appear in HVSC

## Leads to follow

1. **Alan Bond on CSDb** — find his actual scener profile page (not ID 14973). Try
   searching https://csdb.dk/search/?stype=sid&search=Two+Lines+of+Code and follow
   the author link. His scener ID is likely different from 14973.

2. **Howard W. Sams book archive** — no archive.org scan found. Search:
   - "Commodore 64 Basic Programs" Knight LaBatt site:archive.org
   - DLH's Commodore Archive: https://commodore.ca/manuals/ (may have it)

3. **Free Spirit Software Inc.** — 10 music tunes, no source found. Likely from a 1985
   "BASIC Music" software product. Search:
   - "Free Spirit Software" Commodore 64 1985 music BASIC site:archive.org
   - Possibly part of their "Sound FX" or "Music Composer" package line.

4. **Softidea "Videobreak" series** — 9 unnamed tunes from "198? Softidea". Videobreak
   sounds like a Belgian/Dutch interactive slideshow/music product.
   Search: "Softidea" "Videobreak" Commodore 64 Belgian Dutch.

5. **Joey Latimer's book archives** — "The Best of Family Computing Programs Vol. I & II"
   likely contains more of his music listings. Check:
   - https://joeylatimer.com/history.html for download links
   - Search archive.org for "Best of Family Computing"

6. **DEMOS/UNKNOWN detokenize sweep** — 65 tunes in DEMOS/UNKNOWN have no author/source.
   A bulk detokenization of all 65, followed by searching for distinctive phrases
   (REM comments, magazine-style variable names) could identify sources.
   Many likely have REM lines with author names or magazine credits.

7. **Commodore 64 User's Guide (1982)** — the M5, M6, M7, M8 demo disk programs.
   The User's Guide is archived at:
   https://archive.org/details/c64_basic (and similar archive.org entries)
   Cross-reference against M1-M8 series to confirm which User's Guide vs. demo disk.

8. **Hebdogiciel archive** — 8 tunes identified; archive may have more.
   Search archive.org for "Hebdogiciel" for scanned issues.

9. **Club 64 Swedish club** — Ulf Tidstrand + Club 64 archive.org entries exist
   (langkortvokal, rysk_roulette). May have more music tunes not yet in HVSC.
   https://archive.org/details/langkortvokal

10. **COMPUTE!'s First Book of Commodore 64 Sound and Graphics (1983)**
    The OCR text at archive.org contains SID POKE examples by C. Regena and others.
    Full text: https://archive.org/stream/COMPUTES_First_Book_of_64_Sound_and_Graphics_1983_COMPUTE_Publications/...
    Check if any of those programs match tunes in the corpus.
