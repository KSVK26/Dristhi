# CHANGELOG

All notable changes to DRISHTI. Latest first. Format: `SHA | what | why`.

## v0.2.0 — security hardening (data-in-transit focus)
- `c52eaaa` | security v0.2.0: JWT exp + refresh, login rate-limit, photo SHA-256 integrity, HSTS/CSP/XFO headers, env-driven CORS, server-side MIME sniff + 5MB cap
  *Why:* Judges asked how data is protected in transit; needed demonstrable integrity + auth hardening.
- `c986d2a` | CCTV: self-hosted loops + surveillance overlay; field-app web ignores stale localhost override; docs updated
  *Why:* External CCTV feeds were unreliable; needed demo-grade self-hosted footage + signature.
- `3024972` | explainable risk scores: /risk-breakdown endpoint + 'Why this score?' panel with per-factor points
  *Why:* Stakeholders can't audit risk; needed human-readable breakdown.
- `9336a52` | fix map filter: option value attribute so 'All districts' resets correctly
  *Why:* Filter dropdown bug — `value` attribute was missing.
- `68c6dd4` | remove stray terminal-artifact file
  *Why:* Cleanup.
- `8767105` | field app web build
  *Why:* Deployed the field app to Render.
- `b34dba4` | updated with v4
  *Why:* Plan v4 sync.
- `3ed2691` | field app: bake Render API URL into web build
  *Why:* Local and deployed bundles point at different backends.
- `db38a9f` | redeploy field app web build with web-safe photo upload fix
  *Why:* Field app's web build was still on the pre-fix bundle.
- `6c0ffe3` | QA fixes: web-safe photo upload (#003), reliable CCTV streams + offline fallback (#002), risk-score regression test (#004), Google Maps link → lat/lng parser, 20s live task sync (B16), UTF-8 test output
  *Why:* SIH QA guide delivered four bugs; this commit addresses them all.
- `3024972` | explainable risk scores …
  *Why:* (see above)

## v0.1.0 — initial SIH submission
- `b34dba4` | earlier milestone
- *See git log for full history.*
