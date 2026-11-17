# Letná 15. listopadu 2026: dosavadní výsledek

Stav k 17. 11. 2026. **Dokončen audit části zdrojů a jejich technických metadat.
Vlastní fotogrammetrický odhad počtu účastníků dokončen není.**

| Požadovaný výstup | Doložitelný výsledek |
|---|---|
| Nejpravděpodobnější počet | Neurčen |
| Realistické minimum a maximum | Neurčeno |
| Přesnost v procentech | Nelze vyčíslit |
| Podporují fotografie 350–450 tisíc? | V tomto auditu nerozhodnuto |
| Změřená obsazená plocha | Dosud nezměřena |
| Kalibrované hustoty a počty vzorků | Dosud nezměřeny |

Tento stav neznamená, že číslo organizátorů je nepravdivé, ani že fotografie neumožňují
budoucí měření. Znamená, že zde zatím chybí ověřený výpočet. Jakékoli konkrétní číslo
nebo procentní interval by v této fázi obsahovaly nedoložené vstupy.

## Co bylo skutečně ověřeno

Vyhledány byly redakční galerie, výškové video, 360stupňové záběry a zveřejnění policejního
videa. Přímý HTTP sběr běží přes GitHub Actions; ukládá URL, hash, rozměry a vybrané EXIF,
nikoli obrazové soubory. Rozhodující doklad běhu je [collection.json](../data/collection.json).

Prvních šest náhledů mělo šířku 1200 pixelů a žádný nalezený čas pořízení v EXIF.
Následné požadavky na stejnou cestu CDN bez transformačního dotazu vrátily větší varianty.
„Bez ořezu“ neznamená původní soubor přímo z fotoaparátu.

| Varianta bez transformačního dotazu | Rozměry | Čas pořízení uvedený v EXIF | Omezení |
|---|---:|---|---|
| SZ-ELEVATED-POSTER-UNCROPPED | 2400 × 1600 | 15. 11. 14:22:40, +01:00 | Připsáno Michalu Turkovi; obsah zatím neověřen |
| SZ-GALLERY-102-UNCROPPED | 3000 × 2001 | 15. 11. 14:22:40, +01:00 | Stejný čas jako předchozí; možná stejný záběr |
| SZ-GALLERY-103-UNCROPPED | 2400 × 1600 | 15. 11. 14:24:25, +01:00 | Nelze bez kontroly slučovat s jiným okamžikem |
| SZ-GALLERY-104-UNCROPPED | 2400 × 1600 | 15. 11. 14:21:02, +01:00 | Nelze bez kontroly slučovat s jiným okamžikem |
| SZ-GALLERY-105-UNCROPPED | 3000 × 2001 | 15. 11. 12:56:02, +01:00 | Před plánovaným začátkem; nevhodné k doložení maxima |
| SZ-360-POSTER-UNCROPPED | 3840 × 2160 | 15. 11. 14:55:38, pásmo chybí | Model insta360 x3; neověřena projekce |
| POLICE-POSTER-UNCROPPED | 1920 × 1080 | DateTimeOriginal nenalezen | DateTime 16:14:59 může být čas úpravy |

U snímku 102 se údaj DateTime liší od DateTimeOriginal: 15:45:03 proti 14:22:40.
U snímku 105 je rozdíl 15:44:35 proti 12:56:02. To přímo ukazuje, proč nelze vydávat
čas editace nebo publikace za čas fotografování. EXIF lze upravit; sám o sobě nezaručuje autenticitu.
URL, autor a podklad ke každému záznamu jsou v [assets.json](../data/assets.json).

## Vyřazené a nepřijaté podklady

- Getty Images a jiné fotobanky nejsou vstupem žádného měření.
- Vyhledávání vracelo demonstraci 21. 3. 2026 a 16. 11. 2019; tyto snímky nebyly přijaty.
- [Praha 7](https://www.praha7.cz/demonstrace-11-26/) u titulního snímku výslovně uvádí březen 2026.
  Listopadový článek tedy neověřuje listopadový původ titulní fotografie.
- Galerie Blesku obsahuje také přípravy z 14. 11., fotografie ČTK, PID a Facebooku.
  Nepřijímá se celá galerie; vlastní snímky Davida Malíka zůstávají kandidáty.
  ČTK ani nejasně připsané materiály nebyly použity.
- Původní příspěvek Policie ČR na X nebyl přímo dostupný. Novinky připisují video policii,
  ale tato atribuce nedokládá okamžik jednotlivých snímků.
- SinMed: přímý sběr našel konkrétní listopadovou galerii, zatímco čtečka vyhledávače vracela
  starší index. Je zaznamenána jako další kandidát.

## Co brání číslu

V této relaci nefungovalo místní exekuční prostředí. Prohlížení zdrojů poskytlo texty,
URL a metadata, ale neposkytlo mi použitelný obrazový vstup pro kontrolu pixelů a anotaci.
GitHub runner skutečně stáhl bajty pro technický audit, to však samo neprovedlo vizuální
ověření ani počítání. Žádná detekce osob nebo ruční anotace nebyla vykázána jako provedená.

Chybí georeference konkrétních snímků, polygon skutečně obsazené plochy v jednom okamžiku,
odečtení koridorů a zázemí, reprezentativní spočítané vzorky a ověření obsazenosti parku.
Neznámé jsou také mezery mezi snímkovanými okamžiky; maximum z fotografií nemusí být maximem dne.

## Výpočet a srovnání s tvrzením organizátorů

Výpočet je N(t) = součet A_i(t) × hustota_i(t). Okamžiky se nesčítají.
Připravený skript [analyze.py](../tools/analyze.py) počítá plochy z geometrií v metrickém
S-JTSK, kontroluje překryvy sektorů, datum, přijetí fotografií a časovou shodu.
Při prázdných měřeních vrátí null, nikoli nulu. Dolní a horní scénář nejsou automaticky 95% interval.

Zadání už uvádělo 350–450 tisíc a titulky zdrojů číslo opakují. Analýza proto není slepá;
počet organizátorů nebyl použit k nastavení ploch, hustot ani prioritního odhadu.
Dokud tyto vstupy nejsou změřeny, nebylo provedeno nezávislé potvrzení ani vyvrácení tvrzení.

## Zdroje

- [Seznam Zprávy: vlastní galerie Michala Turka](https://www.seznamzpravy.cz/clanek/obrazem-obrazem-andreji-macinko-okamuro-mame-toho-dost-letna-proti-zestatneni-medii-320577)
- [Seznam Zprávy: záběr z výšky](https://www.seznamzpravy.cz/clanek/domaci-zivot-v-cesku-video-takto-vypada-plna-letna-z-vysky-320595)
- [Seznam Zprávy: 360stupňové záběry](https://www.seznamzpravy.cz/clanek/domaci-zivot-v-cesku-milion-chvilek-plna-letna-podivejte-se-na-360-stupnove-zabery-z-mista-320631)
- [Novinky: zveřejněné policejní video](https://www.novinky.cz/clanek/domaci-zabery-z-dronu-ukazaly-statisice-lidi-na-letne-40608773)
- [iROZHLAS: fotografie Jakuba Jiráska a časová reportáž](https://www.irozhlas.cz/zpravy-domov/zive-na-prazske-letne-se-lide-schazeji-k-protestu-za-nezavislost-verejnopravnich_2611151349_vdv)
- [SinMed: konkrétní galerie](https://www.sinmed.cz/fotogalerie/letna-2026-122.html)

Kompletní registry jsou v data/. Žádný kandidátní snímek zatím není přijat pro počítání.
