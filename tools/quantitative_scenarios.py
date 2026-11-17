"""Conditional visual scenarios. Assumptions are never passed off as measured densities."""
import csv,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import Polygon,mapping
from shapely.ops import transform
ROOT=Path(__file__).resolve().parents[1]
def main():
    source_path=ROOT/"data/quantitative_scenarios.json"
    raw=source_path.read_bytes();model=json.loads(raw)
    meta=json.loads((ROOT/"maps/cuzk_ortho.json").read_text())
    assert hashlib.sha256((ROOT/"maps/cuzk_ortho.jpg").read_bytes()).hexdigest()==model["map_sha256"]
    extent=meta["export"]["extent"]
    dx=(extent["xmax"]-extent["xmin"])/meta["export"]["width"]
    dy=(extent["ymax"]-extent["ymin"])/meta["export"]["height"]
    assert max(abs(dx-model["pixel_scale_m"][0]),abs(dy-model["pixel_scale_m"][1]))<1e-8
    back=Transformer.from_crs(32633,4326,always_xy=True).transform
    geoms=[];rows=[];features=[]
    overlay=Image.new("RGBA",(2400,1800),(0,0,0,0));draw=ImageDraw.Draw(overlay)
    colors=[(255,90,0),(255,160,0),(240,60,30),(180,30,200),(0,150,240),(0,180,90),(130,100,255)]
    font=ImageFont.load_default(size=23)
    for index,s in enumerate(model["sectors"]):
        pts=s["pixel_coordinates"]
        g=Polygon([(extent["xmin"]+x*dx,extent["ymax"]-y*dy) for x,y in pts])
        assert g.is_valid and g.area>0
        for other in geoms:assert g.intersection(other).area<.01,"Double-counted baseline area"
        geoms.append(g)
        for name in ("area_factor","occupied_fraction","density"):
            p=s[name];assert len(p)==3 and all(math.isfinite(v) and v>=0 for v in p)
            assert p==sorted(p),"Scenario order reversed"
        assert all(v<=1 for v in s["occupied_fraction"])
        values=[]
        for k,scenario in enumerate(model["scenario_order"]):
            net=g.area*s["area_factor"][k]*s["occupied_fraction"][k]
            count=net*s["density"][k]
            values.append(count)
            rows.append({"sector":s["id"],"scenario":scenario,"gross_area_m2":g.area,
                "area_factor":s["area_factor"][k],"occupied_fraction":s["occupied_fraction"][k],
                "effective_occupied_m2":net,"assumed_density_per_m2":s["density"][k],"people":count})
        features.append({"type":"Feature","properties":{**s,"gross_area_m2":g.area,
          "people_scenarios":values,"geometry_status":"Model envelope, not verified occupied boundary"},
          "geometry":mapping(transform(back,g))})
        color=colors[index];ip=[tuple(p) for p in pts]
        draw.polygon(ip,fill=(*color,48))
        draw.line(ip+[ip[0]],fill=(*color,255),width=4)
        cx,cy=Polygon(pts).centroid.coords[0]
        draw.rectangle((cx-15,cy-15,cx+18,cy+17),fill=(255,255,255,255))
        draw.text((cx-10,cy-13),s["id"],fill=(0,0,0,255),font=font)
    im=Image.alpha_composite(Image.open(ROOT/"maps/cuzk_ortho.jpg").convert("RGBA"),overlay).convert("RGB")
    crop=im.crop((430,430,1450,1080));canvas=Image.new("RGB",(1020,910),"white");canvas.paste(crop,(0,60))
    d=ImageDraw.Draw(canvas);small=ImageFont.load_default(size=18)
    d.text((12,9),"CONDITIONAL SCENARIOS - SECTOR ENVELOPES",fill="black",font=font)
    d.text((12,37),"Boundaries and density are uncertain; colored area is NOT all occupied.",fill="black",font=small)
    for i,s in enumerate(model["sectors"]):
        col=i%2;row=i//2;x=12+col*500;y=725+row*34
        d.rectangle((x,y,x+20,y+20),fill=colors[i]);d.text((x+28,y),s["id"]+" "+s["label"],fill="black",font=small)
    d.text((12,874),"Ortofoto CR / CUZK, CC BY 4.0; manual interpretation 2026-11-17",fill="black",font=small)
    d.line((35,675,35+100/dx,675),fill="white",width=6);d.text((35,644),"100 m",fill="white",font=small)
    canvas.save(ROOT/"maps/scenario_sectors.png")
    totals={name:sum(r["people"] for r in rows if r["scenario"]==name) for name in model["scenario_order"]}
    nets={name:sum(r["effective_occupied_m2"] for r in rows if r["scenario"]==name) for name in model["scenario_order"]}
    # Counts frozen above; comparison is a separate, subsequent arithmetic step.
    comparison={str(n):{"required_mean_density_on_central_area":n/nets["central"],
        "within_scenario_envelope":totals["lower"]<=n<=totals["upper"]} for n in (350000,450000)}
    result={"status":model["status"],"input_sha256":hashlib.sha256(raw).hexdigest(),
      "anchor_asset":model["anchor_asset"],"anchor_time":model["anchor_time"],
      "daily_event_peak_measured":None,"conditional_peak_proxy":totals,
      "rounded_to_10000":{k:int(math.floor(v/10000+.5)*10000) for k,v in totals.items()},
      "effective_occupied_m2":nets,"gross_envelope_m2":sum(g.area for g in geoms),
      "central_average_density":totals["central"]/nets["central"],
      "confidence_interval":None,"coverage_probability":None,
      "uncertainty_relative_to_central":{"lower":totals["lower"]/totals["central"]-1,
                                        "upper":totals["upper"]/totals["central"]-1},
      "peak_assumption":model["peak_note"],"parameter_status":model["assumption_type"],
      "claim_comparison":comparison,
      "warning":"Bounds are conditional scenarios, not guaranteed minimum/maximum. No statistical most-likely value or validated percent accuracy is available."}
    checks={"map_hash_verified":True,"map_scale_verified":True,"baseline_sectors_disjoint":True,
      "parameters_finite_and_ordered":True,"fractions_in_0_1":True,"times_not_summed":True}
    evidence=json.loads((ROOT/"data/scenario_evidence.json").read_text())
    anchor=next(r for r in evidence["records"] if r["asset_id"]==model["anchor_asset"])
    from datetime import datetime
    moment=datetime.fromisoformat(model["anchor_time"])
    assert moment.utcoffset() is not None
    assert str(moment.date())==model["date"]==evidence["event_date"]
    assert anchor["capture_time"]==model["anchor_time"] and anchor["admitted_for_visual_scenario"]
    assets=json.loads((ROOT/"data/assets.json").read_text())["assets"]
    asset=next(a for a in assets if a["id"]==model["anchor_asset"])
    assert anchor["sha256"]==asset["observed_sha256"]
    checks["anchor_metadata_consistent"]=True
    result["sensitivity"]={"density_plus_minus_0_5_people":nets["central"]*.5,
                          "area_plus_minus_10_percent":totals["central"]*.1}
    for name in model["scenario_order"]:
        assert totals[name]>=0
    (ROOT/"results/scenario_estimate.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    (ROOT/"results/scenario_check.json").write_text(json.dumps(checks,indent=2)+"\n")
    (ROOT/"maps/scenario_sectors.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},indent=2,ensure_ascii=False)+"\n")
    with (ROOT/"results/scenario_sectors.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print("SCENARIO_RESULT "+json.dumps(result))
    print("SCENARIO_CHECK "+json.dumps(checks))
if __name__=="__main__":main()
