"""Persist only the named generated files, using a normal fast-forward push."""
import subprocess
paths=["data/collection.json","results/estimate.json","results/verification.json",
    "data/download_manifest.json","data/gallery_inventory.json","maps",
    "results/reference_areas.json","data/video_locators.json"]
subprocess.run(["git","config","user.name","github-actions[bot]"],check=True)
subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],check=True)
subprocess.run(["git","add","--",*paths],check=True)
if subprocess.run(["git","diff","--cached","--quiet"]).returncode:
    subprocess.run(["git","commit","-m","Record reproducible research outputs [skip ci]"],check=True)
    subprocess.run(["git","push","origin","HEAD:main"],check=True)
