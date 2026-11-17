"""Fetch provenance metadata only. Copyrighted bytes never written to repository."""
import hashlib, io, json, re, sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 16 * 1024 * 1024
ALLOWED = {"www.seznamzpravy.cz", "www.novinky.cz", "www.irozhlas.cz",
 "www.blesk.cz", "www.praha7.cz", "letna.milionchvilek.cz", "www.sinmed.cz",
 "d15-a.sdn.cz", "d39-a.sdn.cz"}

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.images, self.iframes, self.links = [], [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("property") or a.get("name") or a.get("itemprop", "")
            if any(s in key.lower() for s in ("image", "date", "time", "author", "title", "video")):
                self.meta.append({"key":key, "value":a.get("content", "")})
        if tag == "img":
            self.images.append({k:v for k,v in a.items()
                if k in ("src", "data-src", "srcset", "alt", "title", "width", "height")})
        if tag == "a" and any(s in a.get("href", "").lower() for s in ("letna", "galer", "video")):
            self.links.append(a.get("href"))
        if tag == "iframe":
            self.iframes.append(a.get("src", ""))

def get(url):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in ALLOWED:
        raise ValueError("URL outside reviewed HTTPS host allowlist")
    req = Request(url, headers={"User-Agent":"Letna20261115-research/0.1 (metadata audit)"})
    with urlopen(req, timeout=35) as response:
        final = response.geturl()
        if urlsplit(final).hostname not in ALLOWED:
            raise ValueError("Redirect outside allowlist")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("Response exceeds limit")
        headers = {k:response.headers.get(k) for k in
            ("Content-Type", "Last-Modified", "ETag", "Content-Length")}
        return body, final, headers

def collect():
    output = {"started_at_utc":datetime.now(timezone.utc).isoformat(),
              "note":"HTTP success, captions and EXIF do not by themselves authenticate pixels.",
              "sources":[], "assets":[]}
    sources = json.loads((ROOT/"data/sources.json").read_text())["sources"]
    assets = json.loads((ROOT/"data/assets.json").read_text())["assets"]
    for source in sources:
        record = {"id":source["id"], "requested_url":source["url"]}
        try:
            body, final, headers = get(source["url"])
            page = Page()
            text = body.decode("utf-8", errors="replace")
            page.feed(text)
            record.update(status="fetched", final_url=final, headers=headers,
                sha256=hashlib.sha256(body).hexdigest(), bytes=len(body),
                metadata=page.meta, image_candidates=page.images[:100],
                iframe_candidates=page.iframes[:12], link_candidates=list(dict.fromkeys(page.links))[:60])
        except Exception as exc:
            record.update(status="error", error=str(exc))
        output["sources"].append(record)
    for asset in assets:
        record = {"id":asset["id"], "requested_url":asset["url"]}
        try:
            body, final, headers = get(asset["url"])
            record.update(status="fetched", final_url=final, headers=headers,
                sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
            from PIL import Image, ExifTags
            with Image.open(io.BytesIO(body)) as im:
                record.update(width=im.width, height=im.height, format=im.format)
                exif = im.getexif()
                tags = {ExifTags.TAGS.get(k, str(k)):str(v) for k,v in exif.items()}
                record["exif"] = {k:v for k,v in tags.items() if k in
                    ("DateTime", "DateTimeOriginal", "DateTimeDigitized", "Make", "Model", "Artist", "Copyright")}
                if hasattr(ExifTags, "IFD"):
                    try:
                        nested = exif.get_ifd(ExifTags.IFD.Exif)
                        for k,v in nested.items():
                            name = ExifTags.TAGS.get(k, str(k))
                            if name in ("DateTimeOriginal", "DateTimeDigitized", "OffsetTimeOriginal"):
                                record["exif"][name] = str(v)
                    except (KeyError, TypeError):
                        pass
        except Exception as exc:
            record.update(status="error", error=str(exc))
        output["assets"].append(record)
    target = ROOT/"data/collection.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"sources":[{"id":s["id"],"status":s["status"],
        "metadata":s.get("metadata",[])} for s in output["sources"]],
        "assets":output["assets"]}, ensure_ascii=False, indent=2))
    return output

if __name__ == "__main__":
    collect()
