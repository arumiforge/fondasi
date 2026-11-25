---
name: fondasi-web
description: Baseline rules for every Arumi Studios web app, any stack — security headers, cookies, CSRF, passwords and rate limits, 2FA, permission and ownership checks, safe uploads, UU PDP personal data (masking, retention, logs, staging), audit log, Indonesian identity fields (NIK, KK, NISN, NPSN, NSM, names, addresses, phones, WhatsApp, time zones), performance on low-end phones, health checks, closed staging, minimum tests, required public pages, share previews, printing, offline resilience. Use when starting an app, adding a feature that touches any of these, or reviewing a PR.
---

# Web baseline

Read `docs/web-baseline.md` in Fondasi and apply the sections the change touches; with `docs/conventions.md`
(Indonesian for everything users see, exports) and `docs/ui.md` (design). New app: walk all ten sections and record in
the app's decisions which ones are done, planned or not applicable (with the reason). PR review: name the sections
checked in the PR body.
