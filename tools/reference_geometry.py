"""Measure explicitly traced reference regions; these are not crowd-occupancy polygons."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,mapping
from shapely.ops import transform
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=json.loads((ROOT/"data/reference_regions.json").read_text())
    meta=json.loads((ROOT/"maps/cuzk_ortho.json").read_text())
    extent=meta["export"]["extent"];width=meta["export"]["width"];height=meta["export"]["height"]
    dx=(extent["xmax"]-extent["xmin"])/width;dy=(extent["ymax"]-extent["ymin"])/height
    back=Transformer.from_crs(32633,4326,always_xy=True).transform
    image=Image.open(ROOT/"maps/cuzk_ortho.jpg").convert("RGB")
    draw=ImageDraw.Draw(image)
    font=ImageFont.truetype("DejaVuSans.ttf",18)
    features=[];rows=[]
    for index,feature in enumerate(source["features"]):
        p=feature["properties"];points=p["pixel_coordinates"]
        g=Polygon([(extent["xmin"]+x*dx,extent["ymax"]-y*dy) for x,y in points])
        if not g.is_valid:raise ValueError("Invalid traced reference region")
        e=p["boundary_error_pixels"]*max(dx,dy)
        row={"id":p["id"],"area_m2":g.area,"boundary_sensitivity_m":e,
            "eroded_area_m2":g.buffer(-e).area,"expanded_area_m2":g.buffer(e).area,
            "use":"Reference geometry only; no density and no occupancy asserted."}
        rows.append(row)
        features.append({"type":"Feature","properties":{**p,**row},"geometry":mapping(transform(back,g))})
        color=(255,90,20) if index==0 else (0,210,255)
        draw.line(points+[points[0]],fill=color,width=4)
        x,y=points[0]
        label=f'{index+1}: {g.area/10000:.2f} ha (reference)'
        draw.rectangle((x,y-28,x+350,y-2),fill="white");draw.text((x+3,y-26),label,fill="black",font=font)
    view=image.crop((400,400,1500,1150))
    d=ImageDraw.Draw(view)
    d.rectangle((0,0,1100,55),fill="white")
    d.text((12,8),"REFERENCE AREAS ONLY - NOT A CROWD OCCUPANCY MAP",fill="black",font=font)
    d.text((12,31),"Ortofoto CR / CUZK, CC BY 4.0; manual traces",fill="black",font=font)
    length=100/dx
    d.line((35,710,35+length,710),fill="white",width=8);d.text((35,677),"100 m",fill="white",font=font)
    view.save(ROOT/"maps/reference_areas.png")
    (ROOT/"maps/reference_regions.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},indent=2)+"\n")
    result={"source_map_sha256":meta["sha256"],"pixel_size_m":[dx,dy],"regions":rows,
        "warning":"Cannot convert these areas to demonstrator counts without occupancy and calibrated density."}
    (ROOT/"results/reference_areas.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
