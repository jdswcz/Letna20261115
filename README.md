# Letná 15. 11. 2026 – fotografický odhad

**Pracovní odhad: asi 260 tisíc současně přítomných. Široké modelové rozpětí: 140–440 tisíc.**

Podmíněný sektorový model: mapové plochy jsou měřené, hustota a podíl obsazenosti jsou zveřejněné vizuální předpoklady. Nejde o spočítané hlavy, statistický interval ani doložené maximum dne. Ověřenou procentní přesnost určit nelze.

350 tisíc je s modelem slučitelných; 450 tisíc není potvrzeno ani spolehlivě vyloučeno.

- **[Závěrečná zpráva, metoda a nejistoty](reports/REPORT.cs.md)**
- **[Ověřený výpočet plošné kapacity Letenské pláně](reports/CAPACITY.cs.md)** – tři vymezení, hustoty, odpočty a nezávislé výpočetní kontroly
- [Mapa sektorů a měřítko](maps/scenario_sectors.png)
- [Všechny předpoklady](data/quantitative_scenarios.json), [výpočty CSV](results/scenario_sectors.csv), [výsledek JSON](results/scenario_estimate.json)
- [Původ a datum použitých pohledů](data/scenario_evidence.json)
- [75 skutečně stažených souborů, 80,3 MB: URL, metadata, SHA-256](data/photo_acquisition.json)
- [Registr souborů](data/assets.json), [zdroje](data/sources.json), [vyloučení](data/exclusions.json)
- [Kontroly modelu](results/scenario_check.json), [testy přísného kalkulátoru](results/verification.json)

Fotobanky a jiné demonstrace nejsou vstupem výpočtu. Ne všechny stažené fotografie byly přijaty pro odhad. Barevné obálky neznamenají úplnou obsazenost. Fotografie se bez oprávnění nepřetiskují; zachovány jsou odkazy a metadata.

Práce přímo v main a výpočty na self-hosted runneru podle pokynů zadavatele. Bez force push.

## Reprodukce

Python 3.12:

```sh
python -m pip install -r requirements.txt
python tools/verify.py
node tools/review_transport.mjs self-test
python tools/reference_geometry.py
python tools/quantitative_scenarios.py
python tools/capacity.py
python tools/download_photos.py
```

Scénářový výpočet běží z uložené mapy a JSON bez sítě. Poslední příkaz stáhne fotografie do ignorované složky private_downloads a ověří hashe; potřebuje síť.

tools/analyze.py a results/estimate.json zůstávají přísnou cestou pro kalibrovaná měření a stále vracejí null. Číselný pracovní odhad je v results/scenario_estimate.json s označenými předpoklady.
[Metodika](docs/METHODOLOGY.cs.md), [protokol](docs/WORKLOG.cs.md).
