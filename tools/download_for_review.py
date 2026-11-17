"""Download research photos privately on the runner; publish metadata only.
Previews are encrypted to the reviewer's ephemeral public key before entering logs.
No private key, clear photo, thumbnail or image artifact is published.
"""
import base64, hashlib, io, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from PIL import Image, ImageOps, ImageDraw, ExifTags
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

ROOT = Path(__file__).resolve().parents[1]

def emit(preview, public, identifier, session_id, dimensions, crop=None, raw_sha256=None):
    ephemeral = X25519PrivateKey.generate()
    shared = ephemeral.exchange(public)
    key = hashlib.sha256(shared).digest()
    nonce = bytes(8)+os.urandom(8)
    cipher = Cipher(algorithms.ChaCha20(key,nonce),mode=None).encryptor()
    encrypted = cipher.update(preview)+cipher.finalize()
    envelope = {
        "id":identifier,"session_id":session_id,"mime":"image/jpeg",
        "ephemeral_public_key":base64.b64encode(ephemeral.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)).decode(),
        "nonce":base64.b64encode(nonce).decode(),
        "preview_sha256":hashlib.sha256(preview).hexdigest(),
        "preview_crc32":__import__("zlib").crc32(preview),
        "preview_dimensions":dimensions,"crop":crop,
        "raw_sha256":raw_sha256,
        "ciphertext":base64.b64encode(encrypted).decode()
    }
    payload=json.dumps(envelope,separators=(",",":"))
    print("REVIEW_BEGIN "+identifier)
    for index in range(0,len(payload),12000):
        print("REVIEW_PART "+payload[index:index+12000])
    print("REVIEW_END "+identifier,flush=True)
    

def main():
    session_path=ROOT/(sys.argv[1] if len(sys.argv)>1 else "data/review_session.json")
    session = json.loads(session_path.read_text())
    assets = {a["id"]:a for a in json.loads((ROOT/"data/assets.json").read_text())["assets"]}
    if (ROOT/"maps/cuzk_ortho.json").exists():
        mapping=json.loads((ROOT/"maps/cuzk_ortho.json").read_text())
        assets["CUZK-ORTHO"]={"id":"CUZK-ORTHO","url":mapping["url"],"observed_sha256":mapping["sha256"]}
    public = X25519PublicKey.from_public_bytes(base64.b64decode(session["public_key"]))
    private_dir = ROOT/"private_downloads"
    private_dir.mkdir(exist_ok=True)
    records = []
    contact = []
    for item in session["items"]:
        asset = assets[item["asset_id"]]
        record = {"id":item["id"], "asset_id":asset["id"], "url":asset["url"],
            "downloaded_at_utc":datetime.now(timezone.utc).isoformat()}
        try:
            url = asset["url"]
            if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in {
                "d15-a.sdn.cz","d39-a.sdn.cz","www.sinmed.cz","ags.cuzk.gov.cz","1884403144.rsc.cdn77.org"}:
                raise ValueError("Not a reviewed photo host")
            if asset["id"]=="CUZK-ORTHO":
                data=(ROOT/"maps/cuzk_ortho.jpg").read_bytes()
            else:
                req = Request(url,headers={"User-Agent":"Letna20261115-research/0.2"})
                with urlopen(req,timeout=40) as response:
                    data = response.read(32*1024*1024+1)
                    if len(data)>32*1024*1024: raise ValueError("Photo exceeds download limit")
            digest = hashlib.sha256(data).hexdigest()
            expected = asset.get("observed_sha256")
            if expected and digest != expected: raise ValueError("Photo bytes changed; requires renewed review")
            target = private_dir/(item["id"]+".bin")
            target.write_bytes(data)
            im = Image.open(io.BytesIO(data))
            record.update(status="downloaded", bytes=len(data),sha256=digest,
                raw_dimensions=list(im.size),format=im.format,
                stored_in_git=False,local_runner_path=str(target.relative_to(ROOT)))
            ex=im.getexif()
            tags={ExifTags.TAGS.get(k,str(k)):str(v) for k,v in ex.items()}
            try: tags.update({ExifTags.TAGS.get(k,str(k)):str(v) for k,v in ex.get_ifd(ExifTags.IFD.Exif).items()})
            except Exception:pass
            record["exif"]={k:v for k,v in tags.items() if k in {"Artist","Copyright","DateTime","DateTimeOriginal","OffsetTimeOriginal"}}
            im = ImageOps.exif_transpose(im).convert("RGB")
            record["oriented_dimensions"] = list(im.size)
            if item.get("download_only"):
                thumb=im.copy();thumb.thumbnail((300,215))
                contact.append((item["id"],thumb))
                records.append(record)
                continue
            if item.get("crop"):
                crop = item["crop"]
                if not (0<=crop[0]<crop[2]<=im.width and 0<=crop[1]<crop[3]<=im.height):
                    raise ValueError("Crop outside oriented image")
                im=im.crop(crop)
            im.thumbnail((session.get("max_width",1600),session.get("max_height",1200)))
            if item.get("scale"):
                im=im.resize((im.width*item["scale"],im.height*item["scale"]),Image.Resampling.NEAREST)
            output=io.BytesIO()
            im.save(output,format="JPEG",quality=session.get("jpeg_quality",85),subsampling=0)
            preview = output.getvalue()
            emit(preview,public,item["id"],session["session_id"],list(im.size),item.get("crop"),digest)
            record["preview_dimensions"]=list(im.size)
            record["crop"]=item.get("crop")
        except Exception as exc:
            record.update(status="error",error=str(exc))
        records.append(record)
    for offset in range(0,len(contact),16):
        batch=contact[offset:offset+16]
        sheet=Image.new("RGB",(1200,240*((len(batch)+3)//4)),(245,245,245))
        draw=ImageDraw.Draw(sheet)
        for index,(identifier,thumb) in enumerate(batch):
            x=(index%4)*300;y=(index//4)*240
            sheet.paste(thumb,(x,y+25));draw.text((x+4,y+5),identifier,fill=(0,0,0))
        out=io.BytesIO();sheet.save(out,format="JPEG",quality=85)
        emit(out.getvalue(),public,"CONTACT-"+str(offset//16+1),session["session_id"],list(sheet.size))
    manifest={"session_id":session["session_id"],"records":records,
        "storage":"Photos downloaded to ignored runner workspace; public repository retains metadata only."}
    (ROOT/"data/download_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("DOWNLOAD_SUMMARY "+json.dumps(manifest))
    if not all(r["status"]=="downloaded" for r in records): raise SystemExit(1)

if __name__=="__main__":
    main()
