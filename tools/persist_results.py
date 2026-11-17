"""Save generated outputs atomically through GitHub API; works without git.exe."""
import base64, hashlib, json, os
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
def api(path,body=None,method=None):
    data=None if body is None else json.dumps(body).encode()
    req=Request("https://api.github.com/repos/"+os.environ["GITHUB_REPOSITORY"]+"/"+path,
      data=data,method=method,headers={"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"],
      "Accept":"application/vnd.github+json","Content-Type":"application/json",
      "User-Agent":"Letna-reproducible-research"})
    with urlopen(req,timeout=60) as r:return json.load(r)
def main():
    ref=api("git/ref/heads/main");head=ref["object"]["sha"]
    # Never apply outputs to a different source revision.
    if head!=os.environ["GITHUB_SHA"]:raise RuntimeError("main advanced; rerun on current source")
    commit=api("git/commits/"+head);base=commit["tree"]["sha"]
    remote={x["path"]:x for x in api("git/trees/"+base+"?recursive=1")["tree"]}
    paths=["data/collection.json","results/estimate.json","results/verification.json",
      "data/gallery_inventory.json","results/reference_areas.json","data/video_locators.json",
      "results/scenario_estimate.json","results/scenario_sectors.csv",
      "results/scenario_check.json","maps/scenario_sectors.geojson","maps/scenario_sectors.svg"]
    paths += [str(p.relative_to(ROOT)).replace("\\","/") for p in (ROOT/"maps").glob("*") if p.is_file()]
    changes=[]
    for path in sorted(set(paths)):
        file=ROOT/path
        if not file.exists():continue
        raw=file.read_bytes()
        sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if remote.get(path,{}).get("sha")==sha:continue
        blob=api("git/blobs",{"content":base64.b64encode(raw).decode(),"encoding":"base64"})
        changes.append({"path":path,"mode":"100644","type":"blob","sha":blob["sha"]})
    if not changes:
        print("No generated output changes");return
    tree=api("git/trees",{"base_tree":base,"tree":changes})
    new=api("git/commits",{"message":"Record reproducible research outputs [skip ci]",
        "tree":tree["sha"],"parents":[head]})
    # A concurrent update is a non-fast-forward failure, never force-pushed.
    api("git/refs/heads/main",{"sha":new["sha"],"force":False},"PATCH")
    print("Saved "+str(len(changes))+" files in "+new["sha"])
if __name__=="__main__":main()
