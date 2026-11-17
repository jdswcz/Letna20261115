# Letná 15. 11. 2026 – fotografický výzkum

**75 obrazových souborů skutečně staženo (80,3 MB), proveden obrazový audit a referenční
mapové měření. Doložitelný celkový počet účastníků dosud nebyl získán.**
Tvrzení o 350–450 tisících nelze z provedených měření potvrdit ani vyvrátit.

- [Zpráva s výsledkem a omezeními](reports/REPORT.cs.md)
- [Souhrn skutečně stažených fotografií](data/photo_acquisition.json)
- [Obrazový audit](data/visual_review.json) a [ručně označený vzorek](data/manual_sample.json)
- [Mapa referenčních ploch](maps/reference_areas.png), [geometrie](maps/reference_regions.geojson), [výpočty ploch](results/reference_areas.json)
- [Zdroje](data/sources.json), [registr souborů](data/assets.json), [metadata](data/collection.json)
- [Stav odhadu](results/estimate.json) a [softwarové testy](results/verification.json)

Fotobanky a starší demonstrace nejsou vstupem počítání. Mapa referenčních ploch
**není mapou skutečné obsazenosti**. Chybějící měření znamená null, nikoli nulovou účast.
Fotografie nejsou bez oprávnění veřejně přiloženy; zachovány jsou URL a SHA-256.
Výzkum je přímo v main podle pokynu zadavatele. Bez force push.

## Reprodukce

Python 3.12:

```sh
python -m pip install -r requirements.txt
python tools/verify.py
node tools/review_transport.mjs self-test
python tools/analyze.py
python tools/reference_geometry.py
python tools/download_photos.py
```

Poslední příkaz stáhne všechny evidované fotografie do ignorované složky private_downloads
a ověří hashe. Vyžaduje síť; odstraněný snímek nelze z hashe obnovit.
Změněný soubor se nesmí tiše považovat za původní.

Nový sběr metadat: python tools/collect.py a python tools/inventory_galleries.py.
Nové mapové podklady: python tools/download_map.py.
Soubory tools/annotate.html a tools/render_manual_sample.py umožňují kontrolu ruční anotace.
Detailní postup a vědecká omezení jsou v docs/METHODOLOGY.cs.md a docs/WORKLOG.cs.md.

CI běžně ověřuje software a uložené výpočty. Síťový sběr spustí workflow_dispatch nebo
push s [acquire] ve zprávě commitu; prohlížení používá veřejný klíč v data/review_session.json.
Soukromý klíč se nikdy neukládá do Gitu.
