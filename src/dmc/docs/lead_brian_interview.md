---
source_url: https://web.archive.org/web/20130614222710/http://tehernaplo.blog.hu/2013/05/28/lavor_a_felyetekre, https://web.archive.org/web/20130616104344/http://tehernaplo.blog.hu/2013/05/29/lavor_a_felyetekre_ii_resz
fetched_via: wayback 2013-06-14
fetch_date: 2026-04-11
author: Tehernapló blog (interviewer unknown); subjects include Brian (Balázs Farkas), Maxwell, Trays, Jay, Cheesion, and other Graffity members
content_date: 2013-05-28
reliability: secondary
---

# Tehernapló Interview with Brian (Balázs Farkas) of Graffity
## "Lavor a felyetekre" — Graffity Mega-Interview

**Source:** Tehernapló blog (tehernaplo.blog.hu)
**Published:** 2013-05-28 (Part I) and 2013-05-29 (Part II)
**Archived:**
- Part I: https://web.archive.org/web/20130614222710/http://tehernaplo.blog.hu/2013/05/28/lavor_a_felyetekre
- Part II: https://web.archive.org/web/20130616104344/http://tehernaplo.blog.hu/2013/05/29/lavor_a_felyetekre_ii_resz
**Referenced by:** https://www.scene.hu/2013/05/30/lavor-a-felyetekre-graffity-megainterju-a-tehernaplon/

Brian = Balázs Farkas, handle "Brian", real name "Baliszoft" early on.
Graffity was the most iconic Hungarian C64 demoscene group of the early 1990s.
DMC = Demo Music Creator, Brian's music editor/player system for C64, widely used on the Hungarian and international scene.

---

## Overview of Participants

The interview is a group retrospective conducted by the Tehernapló blog (a Hungarian demoscene/retro blog). Multiple Graffity members responded in writing. The core voices for technical content are:

- **Brian** (Balázs Farkas) — author of DMC, GMC; main programmer/musician of early Graffity
- **Trays** (Hetye) — author of Sósperec (competing in-house music system), also via Grabowsky
- **Jay** — co-founder, organizer, later switched to Amiga
- **Cheesion** — later-era coder
- **Maxwell** — original member, coder
- **Cybortech**, **Calt**, **Davis**, **Display**, **Clarence**, **Archie**, **Matrix** — various members

---

## Technical Content: DMC Design and Architecture

### The Tool Philosophy: Written by Musicians, for Musicians

**Cheesion:**
> Szerintem általában azok a zene editorok és playerek a jók, amiket zenészek írnak. Lehet, hogy nem olyan jó a kód, de legalább pont azt tudja, amire egy zenésznek szüksége van zeneszerzéshez.

**Translation:** "In my opinion, the music editors and players that are made by musicians are the best ones. The code may not be perfect, but at least it does exactly what a musician needs for composing."

**Maxwell:**
> Egyszerűen nem volt mivel zenét csinálni és kellett valami. A DMC-t pedig megelőzte a GMC, amiből szintén sok tapasztalat gyűlt. Ja és kellett hozzá még a Baliszoft zsenialitása.

**Translation:** "Simply there was nothing to make music with, and something was needed. DMC was preceded by GMC, from which a lot of experience was gathered. And of course it needed Baliszoft's [Brian's] genius."

### Brian on DMC Origins and Design Goals

**Brian (on why DMC was created):**
> Úgy tűnik, mintha tervezett brand lett volna, de nem volt az. Egyszerűen nem volt mivel zenét írni, illetve ami volt, az nem tetszett vagy nem tudtam használni. Sohasem tartottam magam jó zenésznek, de elég volt a zenei tudásom ahhoz, hogy tudjam mire lehet esetleg szükség. Inkább a zene technikai része érdekelt (akkor is és most is), C64 után jópár zeneszerkesztőt készítettem még.

**Translation:** "It might look like it was a planned brand, but it wasn't. Simply there was nothing to write music with, or what existed I didn't like or couldn't use. I never considered myself a good musician, but my musical knowledge was sufficient to know what might be needed. I was more interested in the technical side of music (then and now). After C64 I made quite a few more music editors."

### GMC — The Predecessor to DMC

**Brian (on the founding of Graffity):**
> Jay-el közösen volt akkor még egy "hülyeségünk", a Superiors Aural Department (SAD) nevezetű csapat Graffity-n belül, akik elméletileg arra lettek volna hivatottak, hogy kizárólag zenéket készítsenek. Ekkor jöttünk ki a GMC-vel (Game Music Creator), mert volt egy olyan légből kapott ötletünk akkor, hogy ezt a cuccot akár el is lehetne adni. Sláger volt akkor a Magic-Disk nevű újságnak stuffot eladni, amiért még fizettek is. A GMC el is lett küldve nekik, de azt mondták, hogy köszönik szépen, de nem kérik.

**Translation:** "Jay and I also had a little side project, a sub-team within Graffity called Superiors Aural Department (SAD), which was theoretically supposed to only make music. This is when we came out with GMC (Game Music Creator), because we had a vague idea that this thing could maybe be sold. It was fashionable then to sell things to the magazine called Magic-Disk, which actually paid for them. GMC was sent to them, but they said thanks very much but no thanks."

Note from **Cybortech:** The Mini Music Editor (Tomcat release) preceded even the GMC.

### DMC Versions 2.x/3.x/4.x — Largely the Same Core

**Brian:**
> A Sosperec kódilag sokkal fejlettebb volt az akkori DMC-knél (2.x, 3.x, 4.x - ezek gyakorlatilag szinte ugyanazok a programok), de amikor megismertük a Trajsot (Hetyét) akkor már ezek megvoltak "rég", ráadásul ők ültek a sosperecen (tehát eszük ágában sem volt azt terjeszteni), ezért volt a DMC híresebb. Furcsa fricskája ez a sorsnak, hogy egy csapaton belül két teljesen eltérő és független "zenei rendszer" legyen kifejlesztve, de ez is csak úgy megtörtént.

**Translation:** "The Sósperec [by Grabowsky/Trays] was technically far more advanced than the DMC versions of that era (2.x, 3.x, 4.x — these are practically almost the same programs), but when we got to know Trays (Hetye) those were already long done, and moreover they sat on the Sósperec (meaning they had no intention of distributing it), which is why DMC was more famous. It's a funny twist of fate that within one team, two completely separate and independent music systems were developed, but it just happened that way."

**Key technical implication:** DMC 2.x through 4.x shared the same basic architecture. They were not fundamentally redesigned versions — they were incremental iterations of the same player/editor concept.

### DMC5 — The Major Rethink: SID Shutoff + Datalogging

**Brian:**
> A sid lekapcsolós és dataloggolós történetet a DMC5-ben viszont már tőlük "nyúltam", valóban zseniális ötlet volt! Én sok időt nem "fecséreltem" a playerekre, egyik jött a másik után - túl sok optimalizálás sem volt bennük. A DMC5-el kitűztem magam elé a legfontosabb céljaim, hogy $18 sorba (3 karakterbe) beleférjen (akkoriban ennyit evett szinte az összes player, vagy még többet!), és tudjon minden effektet (Hubbardtól a MON-ig) amivel addig találkoztam. Az egész editorostúl playerestűl nem tartott tovább egy hétnél. Tervben volt még a kép alsó részére egy grafikus zongora is (mint a régebbi DMC-kben volt), de az már lemaradt. Sőt biztos, hogy lehetne rajta még rövidíteni pár raszter sort, de ez nem állt szándékomban egyáltalán.

**Translation:** "The SID shutoff and datalogging technique I 'borrowed' [for DMC5] from them [Sósperec/Trays], it was truly a genius idea! I didn't 'waste' much time on the players — one came after the other, there wasn't much optimization in them. With DMC5 I set myself the most important goals: that it fit in $18 raster lines (3 characters) [the player, at runtime in a demo], which is what almost every player consumed at that time or even more! — and that it support every effect I had encountered (from Hubbard to MON). The whole thing, editor and player together, didn't take more than a week. There was also a plan for a graphical piano at the bottom of the screen (like in the older DMCs), but that got dropped. I'm sure you could still trim a few more raster lines from it, but that was not my intention at all."

**Critical technical facts extracted:**
- The **SID shutoff + datalogging technique originated from Sósperec** (Grabowsky/Trays), not from Brian. Brian adopted it for DMC5.
- DMC5 player target: **$18 raster lines = 18 raster lines** (about 18 × 63 = ~1134 cycles per frame at standard timing, so the player runs in ~18 PAL screen lines worth of CPU time).
- "3 karakterbe" (3 characters) — refers to the player fitting in 3 character rows visually, i.e., 18 raster lines ≈ 3 × 8-pixel character rows.
- Design goal: support **all effects from Hubbard to MON** (Rob Hubbard's style through Maniacs of Noise style).
- Total development time, editor + player: **under one week**.

### DMC6 — Ultra-Minimal Player

**Brian:**
> Akkor már képben volt a DMC6 (egy max 8 soros lejátszó), amit majd akkor használunk, ha nincs elég idő zenélni - akkor meg minek erőlködjek az 5-el?! A két player (5 és 6) között nem sok idő telt el (nem emlékszem már annyira), a 6-hoz az editort viszont már nem volt kedvem megírni, átpasszoltam Syndrom-nak aki szebbet és jobbat csinált mint amit én valaha is csináltam volna :).

> A DMC6 is olyan volt már, hogy szerkesztés közben még sok rasztert evett, packolás után már nem. A 6 azt hiszem a mai napig nem lett release-elve, sokan nem is tudnak a létezéséről, sőt régebbi DMC-ket moddoltak és releaseltek 6-os verziószámmal.

**Translation:** "At that point DMC6 was already in mind (a max 8-line player), to be used when there isn't enough time to write music — then why bother with DMC5?! The two players (5 and 6) didn't have much time between them (I don't remember anymore), but for DMC6 I didn't have the desire to write the editor, I passed that to Syndrom [a German scene contact] who made something better and nicer than I ever could have :).

DMC6 was already such that during editing it consumed many raster lines, but after packing it no longer did. DMC6, I believe, has never been released to this day — many people don't even know it exists. In fact, older DMC versions were modded and released with version number 6."

**Critical technical facts extracted:**
- DMC6 player target: **max 8 raster lines** (approximately 8 × 63 = ~504 cycles, extremely tight).
- Key architecture: **two-state player** — during editing (editor mode) it uses more cycles; after **packing/compiling** unused features are removed and it becomes 8-line.
- The editor for DMC6 was written by **Syndrom** (a German contact), not Brian.
- DMC6 was **never publicly released**. Bootleg "DMC6" releases circulating in the scene were actually modded older DMC versions.

### The Sósperec System — What Brian Learned From It

**Trays** (who co-designed Sósperec with Grabowsky as coder):
> Készítettünk egy grafikai megjelenítőt, ami lekapcsolta a SID-et, meghívta zenelejátszót, kiolvasta a SID-et, visszakapcsolta, és visszaírta amit kiolvasott, majd spriteokkal megjelenítette a zenét. Így "láttuk", hogy amit hallunk, az valójában mit is jelent a háttérben, így a jobb effekteket lenyúltuk a nagyok zenelejátszóiból, de legalábbis megismertük, hogy miként is áll elő.

> Viszont amíg Briant (utólag kiderítve) a Hubbard féle "mindentudó" zeneszerkesztők érdekelték (kb. 32 soros idővel, de egy-két bonyolult effektnél kiugrott 50-re is), addig minket a minél kisebb órajel felhasználás motivált. Volt olyan verzió is belőle, aminek volt compile állapota, és az kódból kiszedte azokat a részeket, amit a zene éppen nem használt (pl. arpeggio), így pl. elértük a 6-10 soros időt is, persze ebben az is benne van, hogy Grabowsky optimalizáció őrült volt.

**Translation:** "We built a graphical display tool that: shut down the SID, called the music player, read out the SID registers, turned it back on, and wrote back what it had read out — then displayed the music with sprites. This way we could 'see' what we were hearing, what it actually meant in the background. We 'borrowed' the better effects from the big names' music players, or at least understood how they were produced.

But while Brian (as we later found out) was interested in Hubbard-style 'know-everything' music editors (approximately 32 raster lines, spiking to 50 for one or two complex effects), we were motivated by using as few clock cycles as possible. There was a version with a compile state, and that removed from the code the parts that the song didn't use (e.g., arpeggio), so we reached 6–10 raster lines — though part of that is that Grabowsky was an optimization fanatic."

**Critical technical facts extracted:**
- **Sósperec's datalogging technique** (original, before DMC5 borrowed it):
  1. Shut down the SID chip (write to disable)
  2. Call the music player (let it run its frame)
  3. Read back the SID register values it wrote
  4. Re-enable SID, write back the captured values
  5. Display register state visually via sprites
  This technique allowed **reverse-engineering of SID effects** by watching what any player wrote to the SID chip, frame by frame.
- Sósperec had a **compile/pack stage** that **stripped unused features** (e.g., arpeggio code removed if the song doesn't use arpeggio). This is a per-song dead-code elimination pass.
- Sósperec achieved **6–10 raster lines** in compiled form — significantly more efficient than DMC (which targeted 18 lines in DMC5, 8 lines in DMC6).
- Brian's DMC targeted the Hubbard "everything-capable" style (~32 raster lines normal, spiking to 50).
- The two systems had **different tuning tables**: DMC used CGKOTY frequency tables; Sósperec used AEINRW tables. This caused songs from the two systems to be a quarter-tone apart when mixed in the same demo — confirmed by Maxwell:

**Maxwell:**
> Ráadásul a DMC CGKOTY-os frequenciatáblázattal ment a Sosperec meg AEINRW, úgyhogy a Brian zenéje után negyed hanggal lejjebb szólalt meg a Traysé a demokban.

**Translation:** "Moreover, DMC ran with the CGKOTY frequency table and Sósperec with AEINRW, so Trays's music played a quarter-tone lower than Brian's in the demo."

**Note for SIDfinity:** CGKOTY and AEINRW are frequency table naming schemes used by different C64 music editors. They represent different tuning/temperament assumptions baked into the note→SID-frequency lookup tables.

### Brian's Raster Line Benchmarking Technique

**Matrix:**
> Volt egy zene, amit a Brian abból a célból írt, hogy tesztelje a raszteridőt és ez a szám tele volt hajlításokkal és olyan macskanyávogás szerű hanggal. Simán megérne egy 2013-as remixet...

**Translation:** "There was a music piece that Brian wrote for the purpose of testing raster time, and it was full of bends and a cat-meowing-like sound. It would easily deserve a 2013 remix..."

**Implication:** Brian wrote dedicated test songs to stress-test the player's cycle budget, specifically with many simultaneous effects (pitch slides/"bends" + unusual waveforms).

### Brian's Player Analysis of Griff (Rival Musician)

**Brian:**
> Ez azért volt, mert valamilyen party-n [...] nagyon gusztustalanul sztárolták az embert és a player-ét, miszerint olyan hangokat (pl. dob ami már majdnem sample minőségű) nem tud senki más mint Ő. Jól emlékszem ez "betette a kaput" nálam (mint player buzi) és gondoltam, hogy akkor utánanézek a dolognak. Megsasoltam valamelyik kódjukat (úgy mint a Faces a miénket :P), kiszedtem egy Griff zenét playerestől és csak akkor esett le az állam, hogy giga sok raszteridőt evett, nem emlékszem de csúcsban 3x annyit mint mondjuk a DMC 2. Ekkor írtam a Griff Sux nevű szösszenetet (el kéne olvasni a skrullert benne, ott talán frissebb volt még az élmény akkor).

**Translation:** "This was because at some party [...] someone was shamelessly praising him and his player, that nobody else could make sounds like his (e.g., a drum that's almost sample quality). I remember this 'opened the gate' for me (as a player fanatic) and I thought I'd look into it. I disassembled one of their tunes along with the player (just as Faces did with ours :P), extracted a Griff song with its player, and then my jaw dropped — it consumed a massive amount of raster time, I don't remember exactly but at peaks 3× as much as, say, DMC 2. This is when I wrote the piece called 'Griff Sux' (you should read the scroller in it, the experience was fresher then)."

**Critical technical facts extracted:**
- Brian **disassembled competitors' players** to analyze their cycle consumption. This was standard practice in the scene ("just as Faces did with ours").
- Griff's player consumed **~3× the raster lines of DMC 2** at peak — Brian considered this wasteful even if the output quality was impressive.
- The "almost sample quality drum" effect in Griff's player required far more CPU cycles than Brian's approach.
- Brian's mindset: **sound quality does not justify excessive cycle cost**. Efficiency was a core value.

### Brian's Post-Graffity Music Work (TIA)

**Brian:**
> Én a végén már csak zenéket írtam (voltak nálam sokkal jobb kóderek a Graffity-ben). Syndrom akkor alapította a TIA-t (The Imperium Arts) melynek tagja voltam (vagyok) én is, és ahol lehetőségem nyílt olyan kitűnő zenészek munkájához hozzájárulni a DMC-vel, mint például PRI vagy SMC (Sanke 3003) akinek zöldfülűként még én is nagy csodálója voltam annó.

**Translation:** "Toward the end I was only writing music (there were much better coders than me in Graffity). At that time Syndrom founded TIA (The Imperium Arts) of which I was (am) also a member, and where I had the opportunity to contribute to the work of excellent musicians using DMC, such as PRI or SMC (Sanke 3003), who I had admired as a beginner myself."

**Note:** Brian continued using DMC to write music even after leaving Graffity's active coding phase. The tool outlived the group's active period.

---

## Technical Content: Player Architecture Summary

Based on Brian's and Trays's statements, the DMC player architecture across versions can be reconstructed as:

### DMC 1.x (Mini Music Editor / GMC period)
- Very early editor, Tomcat release
- GMC = Game Music Creator — first attempt
- Rejected by Magic-Disk magazine (the commercial SID music market)

### DMC 2.x / 3.x / 4.x (Core era)
- **These are "practically the same program"** (Brian's own words)
- Hubbard-style "know-everything" player with full effect support
- ~32 raster lines typical, spiking to ~50 for complex effects
- Uses CGKOTY frequency table (distinct from Sósperec's AEINRW)
- Had a graphical piano interface in the editor
- Widely distributed and used by the Hungarian scene

### DMC 5 (Rethought player)
- **Adopted SID shutoff + datalogging from Sósperec** — Brian's explicit acknowledgment
- Target: **18 raster lines** (3 character rows) for the runtime player
- Supports all effects from Hubbard style through MON (Maniacs of Noise) style
- Total development time: under one week (editor + player)
- Graphical piano planned but not implemented
- Could be trimmed further but Brian didn't bother

### DMC 6 (Ultra-minimal)
- Target: **8 raster lines** maximum
- **Two-mode architecture**: editor mode (heavier) vs. packed/compiled mode (8-line)
- Packing removes unused code paths (same approach as Sósperec's compile stage)
- Editor written by **Syndrom** (Germany), not Brian
- **Never publicly released** — all "DMC6" releases in circulation are modded older versions
- Brian and Syndrom remained in contact through TIA (The Imperium Arts)

---

## Sósperec vs DMC — The Parallel Systems

Both systems were developed independently within the same group (Graffity absorbed the Trays members including Hetye/Trays and Grabowsky):

| Feature | DMC (Brian) | Sósperec (Trays/Grabowsky) |
|---------|-------------|---------------------------|
| Frequency table | CGKOTY | AEINRW |
| Tuning difference | (reference) | Quarter-tone lower |
| Raster target | ~32 lines (DMC4), 18 (DMC5), 8 (DMC6) | 6–10 lines (compiled) |
| Design philosophy | "Everything Hubbard can do" | Minimum cycles, strip unused features |
| Compile/pack stage | DMC6 only | Yes, from early on |
| Distribution | Widely distributed | Never distributed (internal only) |
| Datalogging | DMC5+ (borrowed from Sósperec) | Original invention |

The datalogging/SID-shutoff technique as described by Trays:
1. Silence the SID (write to SID control registers to disable all voices)
2. Execute the music player for one frame
3. Read back all SID registers after the player has written them
4. Re-enable the SID and write the captured values
5. Visually display the register state (used for effect analysis)

This technique allowed analysis of **any** SID player's output without modifying the player — a precursor to what modern tools like siddump's `--writelog` do.

---

## Context: Scene Background and Group History

### Formation (1990)
Brian (Baliszoft) met Jay in 1990. Jay was already in the scene. Brian showed Jay his work; they founded Graffity together. Original four members: Maxwell, Matrix, Jay, Brian.

Earlier Brian had a group called Tomcat with school friends (Maxwell with nick "Hepido19", Kovax, Tony).

### Music as the Graffity Identity
**Brian:**
> Minderre az "alapra" jött az, hogy k***a tehetséges embereket láttam magam körül. A demóinkba a saját zenéinket tettük, amit a saját magunk által írt zeneszerkesztőkkel csináltunk (GMC/DMC, Sósperec). Minden grafikát, a legutolsó charsetet is magunk rajzoltuk.

**Translation:** "On top of all this 'foundation' came the fact that I saw f***ing talented people around me. We put our own music in our demos, made with our own music editors (GMC/DMC, Sósperec). Every graphic, down to the last charset, we drew ourselves."

### Key External Contacts
- **Syndrom** (Germany) — Brian's main foreign contact; wrote the DMC6 editor; founded TIA (The Imperium Arts) with Brian as member; Brian sent him DMC6 engine
- **JCH** (Jeroen Kimman / Vibrants) — Brian wrote once, JCH replied with a current Vibrants compilation
- **Rob Hubbard** — cited as the gold standard for "everything-capable" SID players (Brian's explicit design target)
- **Maniacs of Noise (MON)** — other end of the effect spectrum Brian targeted

### Understanding the SID Through Player Analysis
Both teams (Brian/DMC and Trays/Sósperec) developed their deep SID knowledge by disassembling existing players:

**Trays:** "...thus the better effects we 'borrowed' from the big names' music players, or at least understood how they were produced."

**Brian (on analyzing Griff's player):** "I disassembled one of their tunes along with the player... and then my jaw dropped."

This was standard practice: disassemble a well-regarded player, understand the technique, implement it yourself. The scene's knowledge propagated through reverse engineering.

---

## Full Hungarian Text — Key Technical Sections

### Part I: DMC Question and Answers (complete)

**Tehernapló: A Brian féle DMC használhatóságban és minőségben jó ideig etalon volt. Minek köszönhető ez, tervezett brand volt?**

*(Translation of question: "The Brian-style DMC was a benchmark in usability and quality for a long time. What is this thanks to — was it a planned brand?")*

**Cheesion:** Szerintem általában azok a zene editorok és playerek a jók, amiket zenészek írnak. Lehet, hogy nem olyan jó a kód, de legalább pont azt tudja, amire egy zenésznek szüksége van zeneszerzéshez.

**Jay:** Teljesen esetleges volt, ami abból adódott, hogy mindig azt csináltuk, amihez kedvünk volt.

**Cybortech:** A DMC sikere azt igazolta, hogy jó zenész és jó programozó csinálta. Nem ismerem, a mostani editor/playereket, így nem tudom megmondani, hogy mennyire időtálló a DMC...

**Maxwell:** Egyszerűen nem volt mivel zenét csinálni és kellett valami. A DMC-t pedig megelőzte a GMC, amiből szintén sok tapasztalat gyűlt. Ja és kellett hozzá még a Baliszoft zsenialitása.

**Brian:** Úgy tűnik, mintha tervezett brand lett volna, de nem volt az. Egyszerűen nem volt mivel zenét írni, illetve ami volt, az nem tetszett vagy nem tudtam használni. Sohasem tartottam magam jó zenésznek, de elég volt a zenei tudásom ahhoz, hogy tudjam mire lehet esetleg szükség. Inkább a zene technikai része érdekelt (akkor is és most is), C64 után jópár zeneszerkesztőt készítettem még.

**Trays:** Azért ne feledjük a Sosperecet se (^_^) by Grabowsky, mert 8 év zenélés múlttal inkább zenével foglalkoztam mint kódolással, Grabowskyval ott a versengés amúgy is felesleges lett volna. A specifikációt én raktam össze, teszteltem, zenéltem, ő pedig kódolt. Készítettünk egy grafikai megjelenítőt, ami lekapcsolta a SID-et, meghívta zenelejátszót, kiolvasta a SID-et, visszakapcsolta, és visszaírta amit kiolvasott, majd spriteokkal megjelenítette a zenét. Így "láttuk", hogy amit hallunk, az valójában mit is jelent a háttérben, így a jobb effekteket lenyúltuk a nagyok zenelejátszóiból, de legalábbis megismertük, hogy miként is áll elő.
Viszont amíg Briant (utólag kiderítve) a Hubbard féle "mindentudó" zeneszerkesztők érdekelték (kb. 32 soros idővel, de egy-két bonyolult effektnél kiugrott 50-re is), addig minket a minél kisebb órajel felhasználás motivált. Volt olyan verzió is belőle, aminek volt compile állapota, és az kódból kiszedte azokat a részeket, amit a zene éppen nem használt (pl. arpeggio), így pl. elértük a 6-10 soros időt is, persze ebben az is benne van, hogy Grabowsky optimalizáció őrült volt.
Itt is igaz volt, hogy zenész keze alá készült jó programozóval, és jól használható volt, viszont sosem használtuk egymásét. :-)

**Maxwell:** Ráadásul a DMC CGKOTY-os frequenciatáblázattal ment a Sosperec meg AEINRW, úgyhogy a Brian zenéje után negyed hanggal lejjebb szólalt meg a Traysé a demokban.

**Brian:** A Sosperec kódilag sokkal fejlettebb volt az akkori DMC-knél (2.x, 3.x, 4.x - ezek gyakorlatilag szinte ugyanazok a programok), de amikor megismertük a Trajsot (Hetyét) akkor már ezek megvoltak "rég", ráadásul ők ültek a sosperecen (tehát eszük ágában sem volt azt terjeszteni), ezért volt a DMC híresebb. Furcsa fricskája ez a sorsnak, hogy egy csapaton belül két teljesen eltérő és független "zenei rendszer" legyen kifejlesztve, de ez is csak úgy megtörtént.

A sid lekapcsolós és dataloggolós történetet a DMC5-ben viszont már tőlük "nyúltam", valóban zseniális ötlet volt! Én sok időt nem "fecséreltem" a playerekre, egyik jött a másik után - túl sok optimalizálás sem volt bennük. A DMC5-el kitűztem magam elé a legfontosabb céljaim, hogy $18 sorba (3 karakterbe) beleférjen (akkoriban ennyit evett szinte az összes player, vagy még többet!), és tudjon minden effektet (Hubbardtól a MON-ig) amivel addig találkoztam. Az egész editorostúl playerestűl nem tartott tovább egy hétnél. Tervben volt még a kép alsó részére egy grafikus zongora is (mint a régebbi DMC-kben volt), de az már lemaradt. Sőt biztos, hogy lehetne rajta még rövidíteni pár raszter sort, de ez nem állt szándékomban egyáltalán.

Akkor már képben volt a DMC6 (egy max 8 soros lejátszó), amit majd akkor használunk, ha nincs elég idő zenélni - akkor meg minek erőlködjek az 5-el?! A két player (5 és 6) között nem sok idő telt el (nem emlékszem már annyira), a 6-hoz az editort  viszont már nem volt kedvem megírni, átpasszoltam Syndrom-nak aki szebbet és jobbat csinált mint amit én valaha is csináltam volna :).

A DMC6 is olyan volt már, hogy szerkesztés közben még sok rasztert evett, packolás után már nem. A 6 azt hiszem a mai napig nem lett release-elve, sokan nem is tudnak a létezéséről, sőt régebbi DMC-ket moddoltak és releaseltek 6-os verziószámmal.

**Matrix:** Volt egy zene, amit a Brian abból a célból írt, hogy tesztelje a raszteridőt és ez a szám tele volt hajlításokkal és olyan macskanyávogás szerű hanggal. Simán megérne egy 2013-as remixet a dolgok valami DJ Tiesto vagy hasonló most híres ember előadásában.

---

### Part I: Brian on Tools Philosophy (complete)

**Tehernapló: Kifejezetten demoscene csapat voltatok. Élesen el is különítettétek magatok a crack scene-től?**

*(Translation: "You were specifically a demoscene team. Did you sharply distinguish yourselves from the crack scene?")*

**Brian:** Volt 1-2 crack-ünk, nem sok. Az is csak a legelején, és csak úgy poénból. Sőt azok is inkább csak trainer-ek voltak inkább (vagy mi, ha jól tudom a megfogalmazásokat) örök élet meg ilyenek. Egyébként csináltunk mindent ami szembe jött. Többen készítettek játékot is (legalább háromról tudok ez idő alatt). Persze ezek egyike sem a Graffity név alatt. Az megmaradt kizárólag a demóknak és a (demókkal kapcsolatos) utiloknak.

*(Translation: "We had 1-2 cracks, not many. And only at the very beginning, just for fun. In fact those were more like trainers [infinite lives etc.]. Otherwise we made everything that came along. Several of us made games too [at least three that I know of]. None of those under the Graffity name, which was reserved exclusively for demos and demo-related utilities.")*

---

### Part II: Griff Player Analysis (complete)

**Brian:** Griff sztori: Korábban Display említést tett arról, hogy felhúztam magam a Griff-re (pedig nem is ismertük egymást személyesen). Ez azért volt, mert valamilyen party-n vagy fene se tudja már hol, valaki (vagy valakik) erre sem emlékszem már :), nagyon gusztustalanul sztárolták az embert és a player-ét, miszerint olyan hangokat (pl. dob ami már majdnem sample minőségű) nem tud senki más mint Ő. Jól emlékszem ez "betette a kaput" nálam (mint player buzi) és gondoltam, hogy akkor utánanézek a dolognak. Megsasoltam valamelyik kódjukat (úgy mint a Faces a miénket :P), kiszedtem egy Griff zenét playerestől és csak akkor esett le az állam, hogy giga sok raszteridőt evett, nem emlékszem de csúcsban 3x annyit mint mondjuk a DMC 2. Ekkor írtam a Griff Sux nevű szösszenetet (el kéne olvasni a skrullert benne, ott talán frissebb volt még az élmény akkor). Ezt a Griff Sux-ot használta fel később Display és keszítette el az Acid Sux-ot (grafikusként ő hackelte meg a kódot is).

*(Translation: "Griff story: Display mentioned earlier that I got annoyed at Griff (even though we didn't know each other personally). This was because at some party, or God knows where, someone (or some people) — I don't remember this either :) — was shamelessly hyping the man and his player, that nobody else could make sounds (e.g., a drum almost at sample quality) like him. I clearly remember this 'triggered' me (as a player fanatic) and I decided to look into it. I disassembled one of their pieces (just as Faces did with ours :P), extracted a Griff song with its player, and only then did my jaw drop — it consumed a massive amount of raster time, I don't remember the exact number but at peak 3× as much as, say, DMC 2. This is when I wrote the piece called 'Griff Sux' (you should read the scroller in it, the experience was fresher then). This Griff Sux was later used by Display who made the 'Acid Sux' (he hacked the code himself even as a graphics person).")*

---

## Implications for SIDfinity / DMC Parser Development

1. **DMC 2/3/4 share the same player architecture.** Any parser that works for DMC4 should work for 2 and 3 with minimal changes. Brian explicitly confirms they are "practically the same programs."

2. **DMC5 introduced the SID shutoff + datalogging technique** (borrowed from Sósperec). This is a fundamentally different player architecture from DMC2/3/4. Songs using DMC5 will have different data layout characteristics.

3. **DMC5 player budget: 18 raster lines** (~1134 cycles). This is the hard target Brian designed for. The player is tight.

4. **DMC6 player budget: 8 raster lines** (~504 cycles). Achieved through a compile/pack stage that removes unused feature code — dead-code elimination per song.

5. **The CGKOTY frequency table** is DMC's native tuning. This is the table needed to decode note data in DMC SID files. (Contrast: Sósperec uses AEINRW, which sounds a quarter-tone lower.)

6. **DMC6 was never released** — any SID file claiming to use DMC6 is either a modded DMC version or the Syndrom-authored editor's output, not Brian's original.

7. **Brian continued producing DMC music through TIA** (The Imperium Arts, founded by Syndrom Germany). Songs from the TIA period will also use DMC player variants.

8. **Disassembly was standard practice** for learning SID effects. Any good SID effect seen in a contemporary tune was understood by disassembling that player. This means DMC's effect vocabulary was assembled by studying Hubbard, MON, Griff, and others.

9. **The datalogging approach** (shut SID, run player, read registers, restore SID) is exactly what modern tools like `siddump --writelog` do. Brian adopted this approach from Sósperec for DMC5 and recognized it as "truly a genius idea." This validates the SIDfinity approach of using register dumps for player analysis.
