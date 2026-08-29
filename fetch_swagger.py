"""Vendor Swagger UI assets into backend/static/swagger/ so the API docs
work without any CDN dependency. Run once after cloning:

    Windows:  fetch_swagger.bat
    Linux:    python fetch_swagger.py

The script is idempotent: if the files already exist and are large
enough, it skips re-downloading.
"""
import os
import sys
import urllib.request

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "backend", "static", "swagger")
os.makedirs(DEST, exist_ok=True)

# Pinned versions — we control the version, no surprise breakage.
ASSETS = {
    "swagger-ui-bundle.js":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js",
    "swagger-ui.css":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css",
}

ua = {"User-Agent": "DRISHTI/0.2 (vendoring swagger)"}
ok = True
for name, url in ASSETS.items():
    out = os.path.join(DEST, name)
    if os.path.exists(out) and os.path.getsize(out) > 50_000:
        print(f"skip {name} ({os.path.getsize(out)//1024} KB already vendored)")
        continue
    try:
        print(f"fetching {url}  ->  {out}")
        req = urllib.request.Request(url, headers=ua)
        with urllib.request.urlopen(req, timeout=60) as r, open(out, "wb") as f:
            f.write(r.read())
        size = os.path.getsize(out)
        print(f"  saved {name}: {size//1024} KB")
        if size < 50_000:
            ok = False
    except Exception as e:
        print(f"  FAILED to download {name}: {e}")
        ok = False

# Write a placeholder README so the folder exists in the repo even if
# the network fetch failed. The backend serves a no-JS fallback page when
# the swagger-ui-bundle.js is missing.
readme = os.path.join(DEST, "README.txt")
if not os.path.exists(readme) or ok:
    with open(readme, "w", encoding="utf-8") as f:
        f.write(
            "Swagger UI assets are vendored here at build time.\n"
            "Re-run fetch_swagger.py if the bundle is missing.\n"
        )

if not ok:
    print("WARNING: one or more assets failed to download. "
          "The /docs route will serve a no-JS fallback.")
    sys.exit(1)
print("done.")