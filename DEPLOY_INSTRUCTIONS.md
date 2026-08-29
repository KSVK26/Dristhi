## Steps to deploy the /docs fix (do this once)

1. Open a fresh PowerShell.
2. Run these commands **in order**:

```powershell
cd D:\Projects\SIH\SIH26095
python fetch_swagger.py        # downloads swagger-ui-bundle.js + .css
git add -A
git status                    # confirm: backend/main.py, fetch_swagger.py,
                              #          fetch_swagger.bat, backend/static/,
                              #          .gitignore, README.md
git commit -m "fix(docs): self-host Swagger UI so /docs works without CDN

- backend/main.py: disable default /docs (which loads cdn.jsdelivr.net
  and silently 404s on Render's outbound network), add a self-hosted
  /docs route that serves assets from backend/static/swagger/, with a
  pure-HTML fallback when the bundle is missing.
- fetch_swagger.py + .bat: one-shot vendoring of swagger-ui-dist 5.17.14
  into backend/static/swagger/.
- .gitignore: comment that backend/static/ IS tracked.
- README: docs the new self-hosted /docs flow."
git push origin main
```

3. Wait ~90s for Render to redeploy.
4. Open `https://drishti-api-u0qf.onrender.com/docs` — you should see
   the full Swagger UI (or the no-JS fallback if the vendored files
   didn't get committed).