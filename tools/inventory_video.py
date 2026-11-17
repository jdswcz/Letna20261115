"""Inspect public article markup for video locators. Does not bypass login or DRM."""
import json,re
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
URL="https://www.novinky.cz/clanek/domaci-zabery-z-dronu-ukazaly-statisice-lidi-na-letne-40608773"
def main():
    with urlopen(Request(URL,headers={"User-Agent":"Letna research"}),timeout=35) as r:text=r.read().decode("utf8")
    decoded=text.replace("\\\\","\\").replace("\\/","/")
    urls=sorted(set(re.findall(r'https?[^\s"<>]+(?:\.mp4|\.m3u8|\.mpd)[^\s"<>]*',decoded)))
    locators=[]
    for match in re.finditer(r'(?:videoId|video_id|episodeId|episode_id|streamId|stream_id|data-video-id|seznam-video)[^\n]{0,120}',decoded):
        locators.append(match.group(0)[:150])
    result={"article_url":URL,"media_urls":urls[:20],"locator_candidates":locators[:30],
        "note":"Locator discovery only; no full-resolution video retrieved by this tool."}
    (ROOT/"data/video_locators.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
