import subprocess, sys
subprocess.run([sys.executable, r"D:\Projects\SIH\SIH26095\check_docs.py"], check=False)
# also do the backend test
import urllib.request
try:
    r = urllib.request.urlopen("https://drishti-api-u0qf.onrender.com/docs", timeout=20)
    html = r.read().decode("utf-8", errors="replace")
    open(r"D:\Projects\SIH\SIH26095\docs_dump.txt", "w", encoding="utf-8").write(
        "STATUS=" + str(r.status) + "\nLEN=" + str(len(html)) + "\n\n" + html[:3000]
    )
    print("wrote docs_dump.txt")
except Exception as e:
    open(r"D:\Projects\SIH\SIH26095\docs_dump.txt", "w", encoding="utf-8").write("ERR: " + str(e))