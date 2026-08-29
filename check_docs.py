import sys, urllib.request
try:
    r = urllib.request.urlopen("https://drishti-api-u0qf.onrender.com/docs", timeout=20)
    html = r.read().decode("utf-8", errors="replace")
    print("STATUS:", r.status)
    print("LENGTH:", len(html))
    print("--- first 2000 chars ---")
    print(html[:2000])
except Exception as e:
    print("ERR:", e)