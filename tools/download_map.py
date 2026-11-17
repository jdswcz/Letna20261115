"""Download an attributed CC BY 4.0 CUZK reference map; not event imagery."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
from pyproj import Transformer,CRS
ROOT=Path(__file__).resolve().parents[1]
def main():
    tr=Transformer.from_crs(4326,32633,always_xy=True)
    corners=[tr.transform(x,y) for x in (14.405,14.435) for y in (50.090,50.104)]
    bbox=[min(x for x,y in corners),min(y for x,y in corners),max(x for x,y in corners),max(y for x,y in corners)]
    url="https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO/MapServer/export?"+urlencode({
        "bbox":",".join(map(str,bbox)),"bboxSR":"32633","imageSR":"32633",
        "size":"2400,1800","format":"jpg","f":"json"})
    with urlopen(Request(url,headers={"User-Agent":"Letna research"}),timeout=60) as response:
        export=json.load(response)
    if "error" in export: raise ValueError(export["error"])
    href=export["href"]
    if not href.startswith("https://ags.cuzk.gov.cz/"):raise ValueError("Unexpected map host")
    with urlopen(href,timeout=60) as response:data=response.read()
    directory=ROOT/"maps";directory.mkdir(exist_ok=True)
    target=directory/"cuzk_ortho.jpg";target.write_bytes(data)
    extent=export["extent"];width=export["width"];height=export["height"]
    dx=(extent["xmax"]-extent["xmin"])/width;dy=(extent["ymax"]-extent["ymin"])/height
    (directory/"cuzk_ortho.jgw").write_text("\n".join(map(str,[dx,0,0,-dy,extent["xmin"]+dx/2,extent["ymax"]-dy/2]))+"\n")
    (directory/"cuzk_ortho.prj").write_text(CRS.from_epsg(32633).to_wkt())
    metadata={"id":"CUZK-ORTHO","url":href,"request_url":url,"export":export,
        "sha256":hashlib.sha256(data).hexdigest(),"downloaded_at_utc":datetime.now(timezone.utc).isoformat(),
        "attribution":"Ortofoto CR, CUZK / Zememericky urad",
        "license":"CC BY 4.0","license_source":"https://ags.cuzk.gov.cz/opendata/",
        "use":"Reference geometry only, not evidence of occupancy on 15 November 2026",
        "acquisition_date_of_map_imagery":None}
    (directory/"cuzk_ortho.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata))
if __name__=="__main__":main()
