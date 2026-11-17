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
