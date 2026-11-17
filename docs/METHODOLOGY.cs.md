# Reprodukce a pravidla měření

## Co je již provedeno

tools/collect.py provádí HTTP sběr a technický audit. Výsledky ukládá do data/collection.json.
Snímky drží pouze v paměti procesu a nezveřejňuje je. Hash se počítá z přesných obdržených bajtů;
náhled a větší varianta mají různé hashe. Metadata HTML mohou zahrnovat doporučené články,
logotypy a reklamu: image_candidates a link_candidates nejsou ověřené důkazy demonstrace.

## Co zbývá skutečně změřit

1. U každého konkrétního souboru ověřit autora, datum, obsah, polohu, scénu, popisky a případné
   archivní použití. EXIF je podpůrný údaj. Nejprve posoudit původ, potom přijmout pro měření.
2. Zvolit jeden časový řez, zaznamenat viditelné a zakryté části i příchodové cesty.
   Čas publikace ani DateTime úprav nepoužívat jako čas pořízení.
3. Georeferencovat přes stabilní body na povrchu, nikoli vrcholy stožárů nebo hlavy.
   Použít více kontrolních bodů a nezávislé ověřovací body. Uložit souřadnice v pixelech
   i na mapě, použitou projekci, transformaci a chyby v metrech.
4. Rozdělit dav na nepřekrývající se sektory podle pozorované hustoty. Odečíst pódium,
   technické zázemí, volné koridory a neobsazené části. Park pod korunami stromů zůstává
   neznámý, pokud jej neukazují další časově odpovídající záběry.
5. Ve více reprezentativních plochách každého sektoru označit jednotlivé hlavy a doložit
   skutečnou plochu vzorku. Druhý průchod prověří vynechání a duplicity. Evidovat okluze.
   Detektor validovat proti ruční anotaci blízké, vzdálené, řídké i husté oblasti;
   bez odhadu recall nepovažovat výstup modelu za úplný počet.
6. Zdůvodnit dolní, centrální a horní hustoty a nejistotu hranic. Úhel záběru, perspektiva,
   paralaxa hlava–země a stromy jsou systematické chyby, které nemusí zmizet průměrováním.
7. Pro každý čas počítat zvlášť. Maximum z úplných fotografických řezů označit jako pozorované
   maximum; maximum celé události vyžaduje i doložení časového pokrytí.

Oficiální mapové podklady: [IPR Praha – mapové služby](https://geoportalpraha.cz/data-a-sluzby/mapove-sluzby),
[ortofoto](https://geoportalpraha.cz/data-a-sluzby/clanky-a-projekty/ortofoto).
IPR uvádí EPSG:5514 a podporu WGS84. Konkrétní podklad ani jeho výřez zatím nebyl použit k měření;
před užitím uložit URL vrstvy, datum, rozsah, rozlišení, souřadnicový systém a licenci.
Plocha se nepočítá z obrazovkových pixelů Web Mercatoru.

## Vstupy kalkulátoru

data/measurements.json obsahuje snapshots. Každý má:
id, time (ISO čas s pásmem), coverage_evidence, coverage_complete a features.
Volitelné max_skew_seconds je nejvýše 60 s a vyžaduje synchronization_evidence;
ani tato tolerance sama nedokládá neměnnost davu.

Každá feature je GeoJSON Polygon nebo MultiPolygon v pořadí longitude, latitude (WGS84).
Otvory představují odečtené neobsazené plochy. properties obsahují:
id, source_ids, area_evidence, density_evidence, uncertainty_evidence,
area_uncertainty_fraction a density_ppm2 [low, central, high].
Odkazy evidence musí vést ke skutečným kontrolním bodům a anotacím; textové vyplnění
polí samo o sobě není vědeckou validací.

V data/assets.json musí přijatý soubor mít admitted_for_counting=true, pixel_review=true,
authenticity_evidence a capture_time. capture_time_claim z EXIF nepřijímá skript automaticky.
Současné kandidáty tedy nelze omylem zahrnout.

Výstup results/estimate.json:
- při absenci měření observed_max=null a event_peak=null;
- u neúplných sektorů se celkový počet nezveřejní;
- u úplných řezů maximum dolních, centrálních a horních součtů zvlášť;
- event_peak zůstává null: software neprokazuje, zda mezi fotografiemi nastal vyšší stav.

## Nástroje a jejich meze

tools/annotate.html otevřít v prohlížeči, zvolit lokální obrázek, zadat ID a označit body.
Export obsahuje rozměry, pixelové souřadnice a hash souboru, pokud prohlížeč podporuje WebCrypto.
Neprovádí perspektivní transformaci, automatickou detekci, odhad plochy ani korekci okluzí.
Připraven, ale na reálném snímku dosud nepoužit a interaktivně neotestován.

tools/analyze.py používá pyproj a shapely. Testy mají pouze označená syntetická data.
results/verification.json dokládá software, nikoli správnost skutečného odhadu demonstrace.

## Doplněná reprodukce skutečného stažení a prohlížení

Souhrnný seznam skutečně stažených souborů je data/photo_acquisition.json.
python tools/download_photos.py obnoví tyto soubory do private_downloads a ověří SHA-256.
Pro označený vzorek použít:
python tools/render_manual_sample.py private_downloads/SZ-GALLERY-104-UNCROPPED.jpg

Náhledy kontaktů byly použity k výběru vhodných fotografií. Samy nestačí k autentizaci
všech detailů nebo k počítání. data/visual_review.json odděluje kontrolu obrazového obsahu
od způsobilosti pro výpočet. Žádný nový kandidát nebyl automaticky přijat pro počítání.

Referenční plošné měření reprodukuje python tools/reference_geometry.py z uloženého
ortofota a konkrétních pixelových souřadnic v data/reference_regions.json.
Měřítko je 0,899063457 m/pixel; geometrie se převádí do WGS84 až po výpočtu v EPSG:32633.
Ruční nejistota hranice 10 px je analýza citlivosti. Nevztahuje se k hustotě nebo počtu lidí.

Použitý privátní přenos je zdokumentován v tools/review_transport.mjs.
Příkaz keygen vytvoří soukromý klíč pouze lokálně a vypíše veřejný klíč pro review_session.json.
decrypt načte log, lokální soukromý klíč a uloží ověřené náhledy lokálně.
Test self-test ověřuje kryptografické funkce i převody base64 proti Node.
Nešifrované redakční fotografie ani přenosové soukromé klíče do veřejného repozitáře nepatří.

Uchované EXIF neposkytuje automaticky přesnou synchronizaci. Série s +02:00 se bez
dalšího důkazu nepřepočítává na +01:00; přesný čas policejního náhledu zůstává neznámý.
