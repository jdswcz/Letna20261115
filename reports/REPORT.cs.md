# Letná 15. 11. 2026 – vyhodnocení fotografických podkladů

**Výsledek: z prověřených podkladů nebyl získán doložitelný celkový počet účastníků.
Tvrzení o 350–450 tisících nebylo tímto výzkumem nezávisle potvrzeno ani vyvráceno.**

Tentokrát byly obrazové soubory skutečně staženy a zobrazeny. Dřívější omezení přístupu
k pixelům se podařilo překonat přes GitHub runner. Zbývající překážkou je kvalita a
pokrytí podkladů, zejména absence kalibrovaných hustot a časově doloženého pokrytí parku.

| Požadavek | Doložitelný výsledek |
|---|---|
| Nejpravděpodobnější počet | Není určen; chybí změřené hustoty |
| Realistické minimum a maximum celé akce | Z tohoto souboru fotografií neurčeno |
| Přesnost v procentech | Není stanovena |
| Fotografie podporují 350–450 tisíc? | Číselné tvrzení nebylo nezávisle ověřeno |
| Stažení a vizuální kontrola | Provedeny; viz níže |
| Referenční mapové měření | Provedeno, nepředstavuje měření skutečné obsazenosti |

Není korektní zaměňovat „neověřeno“ za „nepravdivé“. Současně ani opakování stejného
odhadu v několika médiích nepředstavuje několik nezávislých měření.

## Skutečně získané podklady

Původních sedm větších obrazových souborů bylo doplněno o dalších **68 souborů** z úplné
galerie Seznam Zpráv a SinMedu. Druhý soubor stahování měl **65 262 978 bajtů**, všechny
požadavky uspěly. Jde o soubory, nikoli o 75 nezávislých pohledů: varianty a podobné záběry
se nesmějí považovat za další účastníky ani další nezávislý důkaz.

Přímý veřejný galerijní endpoint Seznamu vrátil 28 položek. Čtyři již byly v evidenci;
24 dalších bylo staženo bez transformačního dotazu CDN. SinMed přidal 44 souborů.
Tyto nové soubory měly šířky 990, 1100, 1200, 2400 nebo 3000 pixelů; žádný neměl šířku
přes 3000 pixelů. Soubory byly nejprve zkontrolovány v přehledech, vhodné přehledové
pohledy také jednotlivě. Kontrola přehledu není plnohodnotná anotace každé fotografie.

Souhrnná evidence skutečného stažení má **75 různých URL souborů a 80 295 295 bajtů**:
[photo_acquisition.json](../data/photo_acquisition.json). Obsahuje rozměry, bajty, SHA-256
 a dostupné EXIF. Poslední relace je v [download_manifest.json](../data/download_manifest.json);
předchozí relace jsou v historii Gitu. Nešifrované fotografie byly uloženy do ignorované pracovní
složky runneru; **nejsou veřejně přiloženy v Git repozitáři**, protože oprávnění
k jejich dalšímu zveřejnění nebylo doloženo. Odkazy a metadata jsou zachovány.

## Původ a datum

- Galerie Seznam Zpráv je dobová redakční reportáž z 15. 11. 2026, u snímků je kredit
  Michala Turka. EXIF část datace potvrzuje; viditelné nápisy 4:36 a scénografie dokládají
  souvislost s konkrétní akcí. Nejde o přijetí libovolné fotografie jen podle data článku.
- Policejní obraz byl získán z článku Novinek, který video připisuje Policii ČR.
  Soubor má 1920 × 1080 pixelů. DateTimeOriginal nebyl nalezen; údaj DateTime 16:14:59
  není sám o sobě doloženým okamžikem pořízení.
- V sérii SinMed má 44 souborů EXIF OffsetTimeOriginal +02:00, zatímco v Praze toho dne
  platil středoevropský čas +01:00. Příčinou může být nastavení fotoaparátu; bez ověření
  nelze časy automaticky posunout ani sloučit s jinou sérií.
- U jednoho dříve nalezeného snímku je DateTimeOriginal 12:56:02 před zahájením programu.
  U jiných se čas editace liší od času fotografování. Všechny tyto položky se evidují odděleně.

Podrobná datace je v [assets.json](../data/assets.json) a [collection.json](../data/collection.json).
EXIF je podpůrný doklad, nikoli záruka nepozměněného obsahu. U nově nalezených souborů
nelze vizuální prohlédnutí malé náhledové tabule vydávat za úplné ověření autenticity.

Fotobanky, březnová akce 2026, demonstrace 2019 a přípravy ze 14. 11. nejsou vstupem
počítání. Seznam známých vyloučení je v [exclusions.json](../data/exclusions.json).

## Co ukázala obrazová kontrola

1. Výškový pohled Michala Turka a policejní letecký pohled zachycují velkou část
   shromáždění. Nelze z nich ale určit všechny účastníky v parku pod stromy.
2. Policejní obraz je již výrazně zpracovaný a detailní výřezy mají nedostatek informace.
   Ve vzorcích P1 a P3 se hlavy a horní části těl slévají do několika pixelů. Přepočet
   bílých skvrn na osoby by neměl doloženou chybovost.
3. Detaily Seznamu umožňují rozpoznávat hlavy v popředí, ale samy nemají určenou
   půdorysnou plochu vzorku. Lze z nich odečítat viditelné osoby v části obrazu,
   nikoli bez další kalibrace osoby na metr čtvereční.
4. 360stupňový náhled je projekce „malé planety“. Plocha pixelů v něm není úměrná
   skutečné ploše země. Bez znalosti projekce není vhodný pro plošný přepočet.
5. Pohledy po setmění obsahují rozsvícené telefony. Počet světel není počtem lidí:
   někteří telefon nezvedají, jiné světlo nemusí představovat dalšího člověka.

Ve výřezu 200 × 200 pixelů fotografie SZ-GALLERY-104-UNCROPPED bylo ručně označeno
23 rozeznatelných hlav a 3 nejisté kandidáty; [souřadnice jsou uložené](../data/manual_sample.json).
Jde o výběr výslovně označených viditelných hlav, nikoli úplný počet všech lidí ve výřezu.
Plocha výřezu v m² ani počet zakrytých osob nejsou známy, takže z něj nebyla spočítána hustota.

Nebylo provedeno úplné ruční počítání, nebyl vydáván výstup nevalidovaného detektoru
za počet lidí a nebyla doplněna „běžná hustota“ jako údaj naměřený z této akce.

Reprodukovatelné výřezy policejního originálu (souřadnice x0,y0,x1,y1, po EXIF orientaci):
P1 = [800,550,880,630], P2 = [550,450,630,530], P3 = [1100,750,1180,830].
Zvětšení 6× metodou nearest-neighbour nevytvořilo nové obrazové informace.
Podrobný výřez Turka: [400,600,1000,1200] ze SZ-GALLERY-104-UNCROPPED.

## Mapové měření

Bylo staženo georeferencované **Ortofoto ČR od ČÚZK**, EPSG:32633, 2400 × 1800 pixelů.
Služba uvádí otevřená data CC BY 4.0. Úplný dotaz, rozsah, hash a world file jsou v maps/.
Podklad byl použit k referenční geometrii; není to fotografie demonstrace ani důkaz
obsazenosti k 15. 11. 2026.

Ručně byly obkresleny dvě vyznačené referenční oblasti:
- otevřený povrch pláně: přibližně **5,6 ha**;
- sousední jižní travnatý pás: přibližně **1,7 ha**.

Přesné souřadnice bodů a strojové výpočty jsou v
[reference_regions.json](../data/reference_regions.json),
[reference_regions.geojson](../maps/reference_regions.geojson) a
[reference_areas.json](../results/reference_areas.json).
[Mapa referenčních oblastí](../maps/reference_areas.png) výslovně uvádí,
že nejde o mapu obsazeného davu. Citlivost hranic na posun o 10 pixelů je geometrický
scénář, nikoli statistický interval nebo chyba počtu lidí.

Tyto plochy nelze jednoduše vynásobit jedním číslem a nazvat celkovou účastí.
Nezahrnují všechny možné účastníky v parku a okolí, naopak jejich části mohlo zabírat
technické zázemí, pódium, volné koridory nebo neobsazená místa.
Organizační plánek sloužil pouze k orientaci, nikoli jako důkaz skutečného zaplnění sektorů.

## Proč zde není číselný odhad

Pro sektorový výpočet N(t) = součet A_i(t) × d_i(t) potřebujeme **současně**
obsazené A_i i nezávisle kalibrované hustoty d_i. Referenční geometrie sama nestačí.
Použití předpokládaných hustot by bylo reprodukovatelným scénářem, ale stále nikoli
nezávislým měřením této demonstrace.

Není také doloženo, že nejvyšší stav na zveřejněných fotografiích byl maximem dne.
Nelze sestavit součet maxim různých částí v různých časech.
Současný [estimate.json](../results/estimate.json) proto správně obsahuje null,
nikoli nulu a nikoli zvolené „kompromisní“ číslo.

K obhajitelnému odhadu chybí především původní detailnější letecká série nebo video
s ověřeným časem, pohledy na zaplněné i prázdné okraje a park v témže okamžiku,
georeferenční kontrolní body a reprezentativní spočítané vzorky známé plochy.
Bez nich nelze určit ani věrohodnou procentní přesnost nebo realistické celkové minimum a maximum.

## Reprodukce

README a docs/METHODOLOGY.cs.md popisují kroky. tools/download_for_review.py skutečně
stahuje soubory; tools/review_transport.mjs umožňuje kontrolované prohlížení bez publikace
cizích fotografií. Soukromý přenosový klíč nepatří do repozitáře.
tools/reference_geometry.py vytváří referenční mapu a výpočty. tools/analyze.py odmítá
neověřené nebo chybějící měření. Softwarové testy ověřují výpočet a ochranu před
dvojím započtením; jejich úspěch sám neověřuje počet demonstrantů.

## Primární obrazové zdroje

- [Seznam Zprávy – galerie](https://www.seznamzpravy.cz/clanek/obrazem-obrazem-andreji-macinko-okamuro-mame-toho-dost-letna-proti-zestatneni-medii-320577)
- [Seznam Zprávy – výškový pohled](https://www.seznamzpravy.cz/clanek/domaci-zivot-v-cesku-video-takto-vypada-plna-letna-z-vysky-320595)
- [Seznam Zprávy – 360stupňový záběr](https://www.seznamzpravy.cz/clanek/domaci-zivot-v-cesku-milion-chvilek-plna-letna-podivejte-se-na-360-stupnove-zabery-z-mista-320631)
- [Novinky – video připsané Policii ČR](https://www.novinky.cz/clanek/domaci-zabery-z-dronu-ukazaly-statisice-lidi-na-letne-40608773)
- [SinMed – galerie](https://www.sinmed.cz/fotogalerie/letna-2026-122.html)
- [ČÚZK – mapová služba](https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO/MapServer)
- [ČÚZK – otevřená data a licence](https://ags.cuzk.gov.cz/opendata/)
