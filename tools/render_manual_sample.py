"""Render the documented sample privately for checking; never add the photo output to Git."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ap=argparse.ArgumentParser()
ap.add_argument("photo")
ap.add_argument("--annotation",default="data/manual_sample.json")
ap.add_argument("--output",default="private_downloads/manual_sample_review.jpg")
args=ap.parse_args()
a=json.loads(Path(args.annotation).read_text())
b=Path(args.photo).read_bytes()
if hashlib.sha256(b).hexdigest()!=a["source_sha256"]:raise SystemExit("Source hash mismatch")
im=ImageOps.exif_transpose(Image.open(args.photo)).convert("RGB").crop(a["crop"]).resize((600,600),Image.Resampling.NEAREST)
d=ImageDraw.Draw(im)
for group,color in (("head_points","lime"),("uncertain_points","orange")):
    for i,(x,y) in enumerate(a[group],1):
        x*=3;y*=3
        d.ellipse((x-6,y-6,x+6,y+6),outline=color,width=2)
        d.text((x+7,y-6),str(i),fill=color)
target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
print("Saved private annotated review:",target)
