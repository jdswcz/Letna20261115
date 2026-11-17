# Letná 15. 11. 2026 – nezávislý audit podkladů

**Číselný odhad zatím není dokončen.** Nejsou změřené hranice davu ani hustoty.
Nelze poctivě uvést nejpravděpodobnější počet, realistické rozpětí ani potvrdit či vyvrátit 350–450 tisíc.

- [Dosavadní zpráva](reports/REPORT.cs.md)
- [Evidence zdrojů](data/sources.json) a [jednotlivých souborů](data/assets.json)
- [Skutečně získaná HTTP metadata, rozměry, SHA-256 a EXIF](data/collection.json)
- [Strojový stav výpočtu](results/estimate.json)
- [Ověření softwaru](results/verification.json)
- [Metodika a formát měření](docs/METHODOLOGY.cs.md)
- [Protokol práce a omezení](docs/WORKLOG.cs.md)

Přímý sběr našel u několika variant bez ořezu údaj DateTimeOriginal z 15. 11. 2026.
Jeden snímek má čas 12:56:02 před začátkem akce. Dva soubory uvádějí shodně 14:22:40;
jejich nezávislost není doložena. Popisky a EXIF jsou důkazy původu, nenahrazují kontrolu obsahu.

Fotografie se bez doloženého oprávnění nezveřejňují; ukládají se odkazy a metadata.
Prázdné soubory s měřeními znamenají chybějící data, **nikoli nulovou účast**.
Pracuje se přímo v `main` podle následného pokynu zadavatele. Bez force push.

## Reprodukce

Python 3.12:

```sh
python -m pip install -r requirements.txt
python tools/verify.py
python tools/analyze.py
python tools/collect.py
```

Sběr vyžaduje síť; změněné HTML může mít jiný hash. Výsledky jednoho sběru jsou verzované v Gitu.
Původní snímek včetně jeho bajtů není archivován, takže při jeho odstranění samotný hash obraz neobnoví.
Soubor `tools/annotate.html` otevřený lokálně umožňuje označit hlavy a polygon vzorku.
Anotátor je připravený nástroj; žádné reálné anotace ještě nebyly provedeny.
