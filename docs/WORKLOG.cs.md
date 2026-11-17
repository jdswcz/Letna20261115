# Protokol práce

Datum: 17. 11. 2026, časy fotografií interpretovány jen s doloženým pásmem Europe/Prague.

- Ověřen přístup k repozitáři. Byl úplně prázdný; minimální úvodní commit vytvořil základ main.
- Vytvořena samostatná větev analysis/2026-11-17-photo-estimate; výzkumné změny byly průběžně commitovány.
- Prohledány české redakční zdroje a obrazové výsledky. Fotobanky a výsledky z března 2026 a roku 2019 nebyly přijaty.
- Čteny stránky a popisky. Titulní snímek Prahy 7 je výslovně z března.
- Místní exec_command dvakrát oznámil „No usable execution environment is available“.
- Zprovozněn GitHub Actions sběr. První skutečný běh uložil šest náhledů a jejich technická metadata.
- Druhý skutečný běh prověřil sedm náhledů a sedm větších variant; u části se našel DateTimeOriginal.
- Nalezena konkrétní galerie SinMed přímým HTTP sběrem, přestože čtečka vyhledávače ukazovala starý index.
- Zadavatel následně přikázal „Cpi to rovnou do main.“ Dosavadní historie byla přesunuta
  do main běžným fast-forward, bez force push. Další commity a CI zapisují do main.
  Původní pokyn pro samostatnou větev a PR byl tím pro způsob doručení nahrazen.
- Připraven sektorový kalkulátor, lokální anotátor, testy a dokumentace.
- Neprovedena vizuální anotace reálných snímků, georeference, měření hranic ani kalibrace hustot.
  Přístup k textům a EXIF nesmí být vykazován jako práce s pixely.
- Zpráva je proto výslovně neúplný audit; čísla účasti a procentní přesnost nejsou vymyšlena.

Konkrétní časy sběrů a výsledky testů jsou ve verzovaných JSON a v historii GitHubu.
Bajty fotografií se neukládají. Bez zachovaného originálu nebo oprávněného archivu
nelze z hashů obnovit později odstraněný snímek.

## Navazující práce na přímý pokyn k dokončení

- Práce dále výhradně v main. Místní executor nadále nedostupný; skutečné stažení a výpočty proběhly na GitHub runneru.
- Překonán přístup k obrazovým datům: soukromé šifrované náhledy byly po dešifrování kontrolovány SHA-256 a skutečně zobrazeny.
- Nevyhovující přenosy s chybným hashem byly odmítnuty; při opakovaných přenosech byly získány ověřené náhrady. Přenosový nástroj má vlastní testy.
- Staženo sedm větších souborů a dalších 68 fotografií z úplných galerií; souhrn 75 URL a 80 295 295 bajtů.
- Všech 68 nových souborů bylo zobrazeno v pěti kontaktních tabulích; vybrané přehledové snímky a výřezy také jednotlivě.
- Zjištěno, že SinMed série udává EXIF pásmo +02:00, které bez ověření nelze slučovat s místním časem +01:00.
- Staženo veřejné georeferencované Ortofoto ČR, zaznamenána licence CC BY 4.0, world file, rozsah a hash.
- Na ortofotu ručně obkresleny dvě referenční plochy. Záměrně nejsou vykázány jako obsazené sektory davu.
- V malém čitelném výřezu ručně označeno 23 jistějších hlav a tři nejisté kandidáty. Výběr není úplným počtem lidí ani hustotou.
- Detailní výřezy policejního obrazu se ukázaly nevhodné k spolehlivému oddělení jednotlivých hlav.
- Provedeno prověření veřejných lokátorů policejního videa; výsledek data/video_locators.json.
- Číselný celkový odhad zůstává nedoložený. Chybějící data se nedoplňují předpokládanou hustotou nebo převzatým počtem organizátorů.
