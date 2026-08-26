"""Fetch CCTV-style demo clips from Wikimedia Commons into dashboard/public/cctv/."""
import json
import os
import re
import urllib.parse
import urllib.request

UA = {"User-Agent": "DRISHTI-demo/1.0 (student hackathon project)"}
OUT = os.path.join("dashboard", "public", "cctv")
os.makedirs(OUT, exist_ok=True)

# what we want on the wall: (search query, output name)
WANTED = [
    ("classroom students learning", "cam_classroom"),
    ("office corridor", "cam_corridor"),
    ("people walking street crowd", "cam_street"),
]


def api_search(query, limit=6):
    q = urllib.parse.quote(query)
    url = (f"https://commons.wikimedia.org/w/api.php?action=query"
           f"&generator=search&gsrsearch=filetype:video%20{q}"
           f"&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size"
           f"&format=json")
    req = urllib.request.Request(url, headers=UA)
    data = json.load(urllib.request.urlopen(req, timeout=25))
    pages = data.get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda p: p.get("index", 99))


def transcode_url(original_url, title, size="480p"):
    """Commons transcode pattern: /transcoded/<a>/<ab>/<name>.<size>.vp9.webm"""
    name = title.replace("File:", "").replace(" ", "_")
    name = urllib.parse.quote(name)
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons/)"
                 r"(.)/(.)/(.+)$", original_url)
    if not m:
        return None
    return (f"{m.group(1)}transcoded/{m.group(2)}/{m.group(2)}{m.group(3)}/"
            f"{m.group(4)}/{m.group(4)}.{size}.vp9.webm")


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return os.path.getsize(dest)


for query, name in WANTED:
    dest = os.path.join(OUT, f"{name}.webm")
    if os.path.exists(dest) and os.path.getsize(dest) > 100_000:
        print(f"skip {name} (exists)")
        continue
    print(f"== searching: {query}")
    picked = None
    for page in api_search(query):
        info = page.get("imageinfo", [{}])[0]
        title = page.get("title", "")
        # skip long interviews/talks — we want ambient scene footage
        if re.search(r"interview|wikimedia|wikipedia|conference|talk", title, re.I):
            continue
        if info.get("size", 0) > 80e6:
            continue
        picked = (title, info.get("url"))
        print("   candidate:", title[:70])
        break
    if not picked:
        print("   !! nothing suitable found")
        continue
    t_url = transcode_url(picked[1], picked[0]) or picked[1]
    try:
        size = download(t_url, dest)
        print(f"   saved {name}.webm ({round(size/1e6, 1)} MB)")
    except Exception as e:
        print("   !! transcode download failed:", e, "-> trying original")
        try:
            size = download(picked[1], dest)
            print(f"   saved ORIGINAL {name}.webm ({round(size/1e6, 1)} MB)")
        except Exception as e2:
            print("   !! failed:", e2)

print("done.")
