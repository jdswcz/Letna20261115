"""Re-download the 75 recorded file URLs for local analysis, with exact integrity checks."""
import hashlib,json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
def main():
    ledger=json.loads((ROOT/"data/photo_acquisition.json").read_text())
    directory=ROOT/"private_downloads";directory.mkdir(exist_ok=True)
    output=[]
    for record in ledger["records"]:
        item={"id":record["asset_id"],"url":record["url"],"expected_sha256":record["sha256"]}
        try:
            if urlsplit(record["url"]).hostname not in {"d15-a.sdn.cz","d39-a.sdn.cz","www.sinmed.cz"}:
                raise ValueError("URL not on reviewed source host")
            target=directory/(record["asset_id"]+".jpg")
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==record["sha256"]:
                item["status"]="cached"
            else:
                with urlopen(Request(record["url"],headers={"User-Agent":"Letna20261115-research"}),timeout=40) as r:
                    body=r.read(32*1024*1024+1)
                if len(body)>32*1024*1024:raise ValueError("Response too large")
                if hashlib.sha256(body).hexdigest()!=record["sha256"]:raise ValueError("Source bytes changed")
                target.write_bytes(body);item["status"]="downloaded"
            item["path"]=str(target.relative_to(ROOT))
        except Exception as exc:item.update(status="error",error=str(exc))
        output.append(item);print(item["id"],item["status"])
    (directory/"download_results.json").write_text(json.dumps(output,indent=2)+"\n")
    if any(r["status"]=="error" for r in output):raise SystemExit(1)
if __name__=="__main__":main()
