# DRISHTI — Security QA Script

**Run this before every demo / pitch to prove the security claims
live.** Each step has a `bash` or `pwsh` command you can paste.

If any step FAILS, the demo is unsafe — **do not** present to judges.

## 0. Prereqs
```bash
# Backend running on :8000
# Dashboard running on :5173
# Field-app bundle in build/web/ and served on :5174
```

## 1. Security headers (baseline)
```bash
curl -sI http://127.0.0.1:8000/ | grep -iE 'frame|content-sec|strict|ref'
```
**Expected:**
```
Strict-Transport-Security: max-age=63072000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```

## 2. JWT contains `exp`
```bash
TOK=$(curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' \
  http://127.0.0.1:8000/login | python -c 'import sys,json;print(json.load(sys.stdin)["token"])')
backend/.venv/Scripts/python -c "import jwt,time; p=jwt.decode('$TOK', options={'verify_signature':False}); print('exp:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p['exp'])))"
```
**Expected:** an `exp:` timestamp ~8 hours in the future for admin.

## 3. Expired token → 401
```bash
TOK_BAD=$(backend/.venv/Scripts/python -c "import jwt,time; print(jwt.encode({'sub':'1','role':'admin','exp':int(time.time())-1}, 'whatever', algorithm='HS256'))")
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -H "Authorization: Bearer $TOK_BAD" \
  http://127.0.0.1:8000/institutes
```
**Expected:** `HTTP 401`

## 4. Login rate limit (5/min → 60s lockout)
```bash
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w "attempt $i: HTTP %{http_code}\n" -X POST \
    -H 'Content-Type: application/json' \
    -d '{"username":"admin","password":"WRONG"}' \
    http://127.0.0.1:8000/login
done
```
**Expected:** `HTTP 401` x5 then `HTTP 429`.

## 5. Photo integrity (tampered upload rejected)
```bash
TOK=$(curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"ravi","password":"inspector123"}' \
  http://127.0.0.1:8000/login | python -c 'import sys,json;print(json.load(sys.stdin)["token"])')

# Create a tiny real JPEG with a real hash
python -c "
from PIL import Image
import io
img = Image.new('RGB', (16, 16), (255, 0, 0))
img.save('tmp.jpg', 'JPEG')
" 
REAL=$(python -c "import hashlib; print(hashlib.sha256(open('tmp.jpg','rb').read()).hexdigest())")
echo "Real hash: $REAL"

# Get a real task
TASK=$(curl -s -H "Authorization: Bearer $TOK" http://127.0.0.1:8000/inspections/my \
  | python -c 'import sys,json; t=json.load(sys.stdin); print(t[0]["inspection_id"] if t else "")')
echo "Task: $TASK"

# Send with WRONG hash
curl -s -X POST -H "Authorization: Bearer $TOK" \
  -F "inspection_id=$TASK" -F "geo_lat=28.61" -F "geo_lng=77.20" \
  -F "checklist={}" -F "photo_sha256=0000000000000000000000000000000000000000000000000000000000000000" \
  -F "photo=@tmp.jpg;type=image/jpeg" \
  http://127.0.0.1:8000/reports
```
**Expected:** `{"detail":"Photo integrity check failed ...}`

## 6. RBAC: inspector cannot call admin endpoint
```bash
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -X POST -H "Authorization: Bearer $TOK" \
  http://127.0.0.1:8000/analytics/run-anomaly
```
**Expected:** `HTTP 403`

## 7. CORS: dashboard origin allowed
```bash
curl -s -I -X OPTIONS \
  -H 'Origin: https://drishti-dashboard.onrender.com' \
  -H 'Access-Control-Request-Method: POST' \
  http://127.0.0.1:8000/login | grep -i 'access-control'
```
**Expected:** `access-control-allow-origin: https://drishti-dashboard.onrender.com`

## 8. TLS verification (live, not local)
```bash
echo | openssl s_client -servername drishti-api-u0qf.onrender.com \
  -connect drishti-api-u0qf.onrender.com:443 2>/dev/null | openssl x509 -noout -subject -dates
```
**Expected:**
```
subject=CN = drishti-api-u0qf.onrender.com
notBefore=...
notAfter=...   (a date in the future)
```

## 9. Photo upload size cap
```bash
dd if=/dev/zero bs=1M count=6 2>/dev/null > big.bin
curl -s -X POST -H "Authorization: Bearer $TOK" \
  -F "inspection_id=$TASK" -F "geo_lat=28.61" -F "geo_lng=77.20" \
  -F "checklist={}" \
  -F "photo=@big.bin;type=image/jpeg" \
  http://127.0.0.1:8000/reports
```
**Expected:** `{"detail":"Photo exceeds 5 MB limit"}` (HTTP 413)

## 10. Photo upload: invalid MIME rejected
```bash
echo "not an image" > bad.jpg
curl -s -X POST -H "Authorization: Bearer $TOK" \
  -F "inspection_id=$TASK" -F "geo_lat=28.61" -F "geo_lng=77.20" \
  -F "checklist={}" \
  -F "photo=@bad.jpg;type=image/jpeg" \
  http://127.0.0.1:8000/reports
```
**Expected:** `{"detail":"Uploaded file is not a valid image ..."}`

---

## Summary checklist

| # | Test | Result |
|---|---|---|
| 1 | Security headers present | ☐ |
| 2 | JWT has `exp` claim | ☐ |
| 3 | Expired token → 401 | ☐ |
| 4 | Login rate-limit kicks in at attempt 6 | ☐ |
| 5 | Tampered photo → 400 integrity error | ☐ |
| 6 | Inspector → 403 on admin endpoint | ☐ |
| 7 | CORS allowlist for dashboard origin | ☐ |
| 8 | TLS cert valid for Render domain | ☐ |
| 9 | Oversized upload → 413 | ☐ |
| 10 | Non-image upload → 400 | ☐ |

**Date:** ____________ **Tester:** ____________
