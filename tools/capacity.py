"""Reproducible geometric capacity; neither observed attendance nor licensed capacity."""
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pyproj import Geod, Transformer
from shapely.geometry import Polygon, mapping
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[1]


def fmt(value, decimals=0):
    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def shoelace(points):
    pts = [[Decimal(str(x)), Decimal(str(y))] for x, y in points]
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(pts, pts[1:]+pts[:1])))/2


def capacity(area, density, reserved_fraction=0, excluded_m2=0):
    values = (area, density, reserved_fraction, excluded_m2)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite capacity input")
    if area < 0 or density < 0 or not 0 <= reserved_fraction <= 1 or not 0 <= excluded_m2 <= area:
        raise ValueError("Capacity input out of range")
    return math.floor((area-excluded_m2)*(1-reserved_fraction)*density)


def check_disjoint(polygons):
    for i, poly in enumerate(polygons):
        if not poly.is_valid or poly.area <= 0:
            raise ValueError("Invalid polygon")
        for other in polygons[:i]:
            if poly.intersection(other).area > 1e-5:
                raise ValueError("Overlapping area would be counted twice")


def world_scale(meta, world):
    e = meta["export"]["extent"]
    dx = (e["xmax"]-e["xmin"])/meta["export"]["width"]
    dy = (e["ymax"]-e["ymin"])/meta["export"]["height"]
    expected = [dx, 0, 0, -dy, e["xmin"]+dx/2, e["ymax"]-dy/2]
    if len(world) != 6 or any(abs(a-b) > 1e-7 for a, b in zip(world, expected)):
        raise ValueError("World file differs from export extent, including half-pixel origin")
    return dx, dy


def main():
    input_path = ROOT/"data/capacity.json"
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    meta = json.loads((ROOT/"maps/cuzk_ortho.json").read_text(encoding="utf-8"))
    raw_map = (ROOT/"maps/cuzk_ortho.jpg").read_bytes()
    if hashlib.sha256(raw_map).hexdigest() != spec["map_sha256"] or meta["sha256"] != spec["map_sha256"]:
        raise ValueError("Map bytes or metadata changed")
    world = [float(v) for v in (ROOT/"maps/cuzk_ortho.jgw").read_text().splitlines()]
    dx, dy = world_scale(meta, world)
    extent = meta["export"]["extent"]
    to_geo = Transformer.from_crs(32633, 4326, always_xy=True).transform
    geod = Geod(ellps="WGS84")
    components, shapes, features = {}, {}, []
    for c in spec["components"]:
        points = c["pixel_coordinates"]
        if any(not (0 <= x <= meta["export"]["width"] and 0 <= y <= meta["export"]["height"]) for x,y in points):
            raise ValueError("Point outside map")
        poly = Polygon([(extent["xmin"]+x*dx, extent["ymax"]-y*dy) for x,y in points])
        check_disjoint([*shapes.values(), poly])
        decimal_area = float(shoelace(points)*Decimal(str(dx))*Decimal(str(dy)))
        if abs(decimal_area-poly.area) > .0001:
            raise ValueError("Decimal shoelace and Shapely disagree")
        geographic = transform(to_geo, poly)
        ground = abs(geod.geometry_area_perimeter(geographic)[0])
        if abs(ground/poly.area-1) > .002:
            raise ValueError("Geodesic area differs by more than 0.2 percent")
        components[c["id"]] = {"label":c["label"], "projected_area_m2":poly.area,
            "independent_decimal_area_m2":decimal_area, "ground_geodesic_area_m2":ground}
        shapes[c["id"]] = poly
        features.append({"type":"Feature", "properties":{**c, **components[c["id"]]}, "geometry":mapping(geographic)})
    profiles, rows = [], []
    for p in spec["profiles"]:
        if len(p["components"]) != len(set(p["components"])):
            raise ValueError("Duplicate component")
        union = unary_union([shapes[k] for k in p["components"]])
        if abs(union.area-sum(shapes[k].area for k in p["components"])) > .0001:
            raise ValueError("Union and component sum differ")
        ground = abs(geod.geometry_area_perimeter(transform(to_geo, union))[0])
        if abs(ground-sum(components[k]["ground_geodesic_area_m2"] for k in p["components"])) > .1:
            raise ValueError("Geodesic union not additive")
        variants = []
        for reserve in spec["reserved_fraction_scenarios"]:
            for density in spec["density_scenarios_people_per_m2"]:
                row = {"profile":p["id"], "gross_ground_m2":ground,
                    "assumed_reserved_fraction":reserve, "usable_scenario_m2":ground*(1-reserve),
                    "assumed_density_people_per_m2":density, "capacity_people_floor":capacity(ground,density,reserve)}
                rows.append(row); variants.append(row)
        sensitivity=[]
        # A boundary sensitivity experiment, not alternative verified venue boundaries.
        scale = ground/union.area
        for metres in spec["boundary_sensitivity_m"]:
            sensitivity.append({"boundary_offset_m":metres,
                "approx_ground_m2":union.buffer(metres).area*scale,
                "meaning":"Geometric sensitivity only; expansion can extend beyond usable venue."})
        profiles.append({**p, "projected_area_m2":union.area,"gross_ground_m2":ground,
            "required_density_on_gross":{str(n):n/ground for n in (350000,450000)},
            "required_density_with_10_percent_reserved":{str(n):n/(.9*ground) for n in (350000,450000)},
            "boundary_sensitivity":sensitivity,"capacities":variants})
    checks={"map_sha256_verified":True,"world_file_extent_and_half_pixel_verified":True,
        "decimal_shoelace_matches_shapely":True,"geodesic_projection_difference_below_0_2_percent":True,
        "components_nonoverlapping":True,"profile_union_matches_sum":True,
        "geodesic_union_additive_within_0_1_m2":True}
    inputs=["data/capacity.json","maps/cuzk_ortho.json","maps/cuzk_ortho.jgw","tools/capacity.py"]
    result={"status":"verified_geometric_calculation_with_conditional_density_and_deductions",
        "certified_safe_capacity":None,"actual_attendance":None,
        "primary_area_method":"WGS84 ellipsoidal geodesic area; projected and Decimal areas are independent checks",
        "map_pixel_m":[dx,dy],"map_sha256":spec["map_sha256"],
        "inputs_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        "components":components,"profiles":profiles,"checks":checks,
        "limits":spec["limits"]}
    (ROOT/"results/capacity.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"results/capacity_checks.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    with (ROOT/"results/capacity.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (ROOT/"maps/capacity.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    draw_map(spec,components)
    write_report(spec,result)
    print("CAPACITY_VERIFIED "+json.dumps({"checks":checks,"areas":{p["id"]:p["gross_ground_m2"] for p in profiles}}))


def draw_map(spec,components):
    im=Image.open(ROOT/"maps/cuzk_ortho.jpg").convert("RGBA")
    overlay=Image.new("RGBA",im.size,(0,0,0,0));d=ImageDraw.Draw(overlay)
    font=ImageFont.load_default(size=21)
    colors=[(255,95,0),(110,90,245),(0,165,220)]
    for c,col in zip(spec["components"],colors):
        points=[tuple(p) for p in c["pixel_coordinates"]]
        d.polygon(points,fill=(*col,50));d.line(points+[points[0]],fill=(*col,255),width=4)
        x,y=Polygon(points).centroid.coords[0]
        d.rectangle((x-15,y-15,x+18,y+17),fill="white");d.text((x-9,y-13),c["id"],font=font,fill="black")
    crop=Image.alpha_composite(im,overlay).convert("RGB").crop((450,570,1350,1030))
    canvas=Image.new("RGB",(900,710),"white");canvas.paste(crop,(0,65));d=ImageDraw.Draw(canvas)
    small=ImageFont.load_default(size=17)
    d.text((12,8),"GEOMETRIC CAPACITY - NOT OBSERVED ATTENDANCE",fill="black",font=font)
    d.text((12,38),"C0 = A; C1 = A+N; C2 = A+N+S. Park and eastern wooded apron excluded.",fill="black",font=small)
    for i,(c,col) in enumerate(zip(spec["components"],colors)):
        y=545+35*i;d.rectangle((12,y,32,y+20),fill=col)
        label=f'{c["id"]}: {components[c["id"]]["ground_geodesic_area_m2"]:,.0f} m2 - {c["map_label"]}'
        d.text((42,y),label,fill="black",font=small)
    d.text((12,656),"Ortofoto CR / CUZK, CC BY 4.0; manual boundary interpretation",fill="black",font=small)
    d.text((12,681),"Gross area only; infrastructure and circulation deductions are conditional.",fill="black",font=small)
    dx=json.loads((ROOT/"maps/cuzk_ortho.json").read_text())["export"]["extent"]
    metres_per_pixel=(dx["xmax"]-dx["xmin"])/2400
    d.line((35,490,35+100/metres_per_pixel,490),fill="white",width=6);d.text((35,464),"100 m",fill="white",font=small)
    canvas.save(ROOT/"maps/capacity.png")


def write_report(spec,result):
    out=["# Kolik lidí se vejde na Letenskou pláň", "",
        "**Ověřen je mapový plošný výpočet pro přesně zveřejněné hranice. Kapacita závisí na hustotě a dostupné ploše; jednotné doložené maximum celého místa z těchto dat určit nelze.**", "",
        "Tento výpočet není odhadem účasti 15. 11. 2026. Nepřebírá hustoty, zaplnění ani číslo účasti z předchozí analýzy.", "",
        "## Výsledek při úplně volné ploše", "",
        "| Vymezení | Hrubá plocha m² | Při 2 os./m² | Při 3 os./m² | Při 4 os./m² |", "|---|---:|---:|---:|---:|"]
    for p in result["profiles"]:
        a=p["gross_ground_m2"]
        out.append(f'| {p["id"]}: {p["label"]} | {fmt(a)} | {fmt(capacity(a,2))} | {fmt(capacity(a,3))} | {fmt(capacity(a,4))} |')
    out += ["", "Jde o **hrubou geometrickou kapacitu při zvolené rovnoměrné hustotě**, před odpočty. Není to certifikovaná bezpečná kapacita ani fyzický absolutní strop. C0 není celá Letná; C2 je rozšířené pracovní vymezení, nikoli úřední hranice názvu Letenská pláň.", "",
        "![Vymezení ploch](../maps/capacity.png)", "",
        "## Co přesně počítáme", ""]
    for p in result["profiles"]:out.append(f'- **{p["id"]}** ({" + ".join(p["components"])}): {p["description"]}')
    out += ["", "Jižní park P, východní stromové předpolí F, stadion, vozovka Milady Horákové a celé Letenské sady nejsou do těchto variant zahrnuty. Severní prostor N se počítá podmíněně po uvolnění pro lidi; existující parkování, vybavení a případné bariéry jeho reálnou dostupnost snižují. Travnatý pás S zahrnuje i stromy a mobiliář, které vyžadují odpočty.", "",
        "## Odpočty pro překážky, techniku a průchody", "",
        "**Není doloženo přesné současné rozmístění a plocha všech překážek.** Proto je nulový odpočet v první tabulce výslovně jen hrubou referencí. Následující 10% a 20% rezervy jsou ukázkové předpoklady, nikoli změřený zábor nebo předpis. Pokrývají souhrnně pódium, kluziště, stánky, stromy, techniku a neobsazené průchody; jejich konkrétní plocha se nesmí vymýšlet.", "",
        "| Vymezení | Rezerva | Dostupná plocha m² | 2 os./m² | 3 os./m² | 4 os./m² |", "|---|---:|---:|---:|---:|---:|"]
    for p in result["profiles"]:
        a=p["gross_ground_m2"]
        for f in (.1,.2):out.append(f'| {p["id"]} | {f:.0%} | {fmt(a*(1-f))} | {fmt(capacity(a,2,f))} | {fmt(capacity(a,3,f))} | {fmt(capacity(a,4,f))} |')
    out += ["", "Vzorec: **N = floor[(A − pevně vymezené vyloučené plochy) × (1 − další podíl rezervy) × hustota]**. V tabulkách se používá souhrnná procentní rezerva bez samostatného pevného odpočtu, aby se odpočty nezapočetly dvakrát. Každých vyloučených 1 000 m² odebere při 2/3/4 os./m² právě 2 000/3 000/4 000 míst.", "",
        "## Ověření výpočtu", "",
        "Ortofoto ČÚZK je uloženo v repozitáři, EPSG:32633. Měřítko je odvozené z vráceného rozsahu exportu (asi 0,899063457 m/px), nikoli z velikosti obrázku v prohlížeči. Kontroluje se SHA-256 mapy, úplný world file včetně posunu středu pixelu a souřadnice všech vrcholů.", "",
        "Plochy jsou spočítány třemi cestami: (1) vlastní shoelace s Decimal v pixelech a převod měřítkem; (2) Shapely v metrické projekci; (3) pyproj.Geod na elipsoidu WGS84 po transformaci vrcholů. První dvě implementace musejí souhlasit do 0,0001 m²; geodetická a projekční plocha do 0,2 %. Pro kapacitní tabulky se používá **elipsoidální plocha**, takže drobný rozdíl od dřívější projekční výměry je očekávaný.", "",
        "Kontroluje se také nepřekrývání složek, součet proti sjednocení a geodetická aditivita. Jde o různé výpočetní metody na téže mapě, **nikoli nezávislé geodetické zaměření hranic**. Měření bylo vizuálně zkontrolováno na uloženém ortofotu. Datum pořízení ortofota není doloženo; jde o ověření uložené mapy, nikoli aktuální terénní průzkum.", "",
        "Ručně obkreslená hranice má nejistotu. JSON obsahuje citlivost na posun o ±3 a ±9 m; rozšíření může zasahovat mimo použitelný areál, proto není novou doloženou kapacitou ani statistickým intervalem. Shoda algoritmů neodstraňuje chybu hranice.", "",
        "## Co znamená hustota a bezpečná kapacita", "",
        "[Cornwall Council](https://www.cornwall.gov.uk/business-trading-and-licences/organising-an-event/health-and-safety-for-large-events/) uvádí při plošném plánování stojícího publika 0,5 m² na osobu (2 os./m²) po odečtení zařízení; současně požaduje prověřit evakuaci. Jde o britskou plánovací referenci, nikoli české povolení pro Letnou.", "",
        "[G. Keith Still](https://www.gkstill.com/Support/crowd-density/CrowdDensity-1.html) poskytuje vizuální příklady různých hustot. Hodnoty 3 a 4 v tabulkách jsou matematické varianty hustého stojícího davu, nikoli potvrzení, že jsou vhodné pro celou pláň. CSV zahrnuje také 1 a 5 pouze jako citlivost; 5 není doporučený provozní cíl nebo zjištěné maximum.", "",
        "[HSE](https://www.hse.gov.uk/event-safety/venue-site-design.htm) vyžaduje zohlednit průchody a únikové možnosti. Bez jejich parametrů nemáme ověřenou bezpečnou kapacitu: v JSON je proto certified_safe_capacity=null. Plošný součin sám ji nenahrazuje.", "",
        "## Kontrola tvrzení 350 a 450 tisíc", "",
        "| Vymezení | 350 tisíc: potřebná os./m² bez odpočtů | 450 tisíc: bez odpočtů | 350 tisíc: s 10% rezervou | 450 tisíc: s 10% rezervou |", "|---|---:|---:|---:|---:|"]
    for p in result["profiles"]:
        d=p["required_density_on_gross"];r=p["required_density_with_10_percent_reserved"]
        out.append(f'| {p["id"]} | {fmt(d["350000"],2)} | {fmt(d["450000"],2)} | {fmt(r["350000"],2)} | {fmt(r["450000"],2)} |')
    out += ["", "Vyšší počet může využívat další plochy mimo toto vymezení; nebyl by však kapacitou jen C0/C1/C2. Z kapacity nelze vyvodit, kolik lidí skutečně přišlo, ani ji sčítat s již zahrnutými sektory předchozího modelu.", "",
        "## Reprodukce a soubory", "", "```sh", "python -m pip install -r requirements.txt", "python -m unittest discover -s tests -p test_capacity.py -v", "python tools/capacity.py", "```", "",
        "Vstupy: [capacity.json](../data/capacity.json), [zdroje](../data/capacity_sources.json), [mapová metadata](../maps/cuzk_ortho.json). Výstupy: [JSON s výměrami, kontrolami a hashi](../results/capacity.json), [všechny přepočty CSV](../results/capacity.csv), [kontroly](../results/capacity_checks.json), [GeoJSON](../maps/capacity.geojson). [Spustitelný skript](../tools/capacity.py), [testy](../tests/test_capacity.py).", "",
        "Mapový podklad: [ČÚZK Ortofoto](https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO/MapServer), [licence CC BY 4.0](https://ags.cuzk.gov.cz/opendata/). Zdroje byly otevřeny 17. 11. 2026. Výstup se generuje ze skutečně vypočtených hodnot; tento text se při reprodukci přepíše."]
    (ROOT/"reports/CAPACITY.cs.md").write_text("\n".join(out)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
