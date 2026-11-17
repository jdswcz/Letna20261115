"""Inventory public gallery APIs and HTML media metadata, without republishing photos."""
import hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
"SZ-GALLERY-API":"https://api-web.seznamzpravy.cz/v1/galleries-image-link/6afb44d083f43ea898a48b49",
"SZ-ELEVATED-API":"https://api-web.seznamzpravy.cz/v1/galleries-image-link/6af9fb7960fa282624089fc7",
"SZ-360-API":"https://api-web.seznamzpravy.cz/v1/galleries-image-link/6afb45051149e943070f00dd",
"SINMED":"https://www.sinmed.cz/fotogalerie/letna-2026-122.html"
}
def slim(value):
    if isinstance(value,dict):
        return {k:slim(v) for k,v in value.items() if k.lower() not in
            {"body","content","text","perex","description","html","headline","title"}}
    if isinstance(value,list): return [slim(x) for x in value[:100]]
    return value
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.images=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="img" and "gallery/" in a.get("src",""):self.images.append(a)
        if tag=="a" and any(s in a.get("href","") for s in ("gallery/","galerie")):self.links.append(a.get("href"))
def main():
    rows=[]
    for id,url in SOURCES.items():
        row={"id":id,"url":url}
        try:
            with urlopen(Request(url,headers={"User-Agent":"Letna research"}),timeout=35) as r:b=r.read()
            row.update(sha256=hashlib.sha256(b).hexdigest(),status="fetched",bytes=len(b))
            try:row["metadata"]=slim(json.loads(b))
            except ValueError:
                p=Parser();p.feed(b.decode("utf8",errors="replace"))
                row["images"]=p.images;row["links"]=p.links
        except Exception as e:row.update(status="error",error=str(e))
        rows.append(row)
    (ROOT/"data/gallery_inventory.json").write_text(json.dumps({"sources":rows},indent=2)+"\n")
    print("GALLERY_INVENTORY "+json.dumps(rows))
if __name__=="__main__":main()
