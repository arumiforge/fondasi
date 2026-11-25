# Web app baseline (F-013)

Rules every Arumi Studios web app follows, whatever its stack and purpose. Apps may be stricter, never looser.
Related: [conventions.md](conventions.md) (language, URLs, exports), [ui.md](ui.md) (design), [settings.md](settings.md),
[storage.md](storage.md), [app-contract.md](app-contract.md) (server).

## 1. Security

- **Transport and cookies**: HTTPS only (Cloudflare "Always Use HTTPS" + HSTS); session cookies `Secure`, `HttpOnly`,
  `SameSite=Lax` (or `Strict` for admin); staff sessions end after inactivity (30–60 minutes) and on password change.
- **Headers**: `Content-Security-Policy` (no inline scripts unless nonced), `Strict-Transport-Security`,
  `frame-ancestors 'self'` (or `X-Frame-Options: SAMEORIGIN`), `Referrer-Policy: strict-origin-when-cross-origin`,
  `Permissions-Policy` (camera/microphone/geolocation off unless used), `X-Content-Type-Options: nosniff`.
- **Forms**: CSRF token on every state-changing request; server-side validation always (client checks are comfort only).
- **Passwords**: argon2id or bcrypt; minimum length 8 with a breached/common-password check instead of complexity rules;
  rate limits on sign-in, password reset, registration, status checks and contact forms (per IP and per account);
  Turnstile on public forms ([settings.md](settings.md)).
- **Staff accounts**: TOTP 2FA available, required for super admins; no shared accounts.
- **Authorization**: permission-based checks (`can('pendaftar.ubah')`), never role-name checks; every record loaded by
  ID is checked for ownership/scope (no IDOR); deny by default.
- **Dependencies**: lock files committed; CI runs the stack's audit (`composer audit`, `npm audit --omit=dev`,
  `pip-audit`…) and fails on high/critical issues.
- **Secrets**: only in server env files or encrypted settings ([settings.md](settings.md)); never in code, logs or URLs.

## 2. Uploaded files

- Check the content (magic bytes / MIME sniffing), not only the extension; allow-list types per field
  (e.g. PDF, JPG, PNG, WebP); size limits per field and in the web server.
- Re-encode images on upload (strips metadata and payloads; also shrinks phone photos); never execute or include uploads.
- Random file names; original name kept only as data; stored outside the web root (or a private bucket) and served
  through a controller that checks permission, with `Content-Disposition` and `X-Content-Type-Options: nosniff`.
- Uploads can be retried after a dropped connection; the user sees progress and a plain error ("Ukuran berkas
  maksimal 2 MB").

## 3. Personal data (UU PDP)

- **Purpose and consent**: say why each item is collected; an explicit consent tick where the law needs it; collect
  only what the purpose needs.
- **Masking**: NIK, KK and phone numbers are masked in lists and exports that do not need them
  (`3319**********0001`, `0812-****-7890`); full values only on detail pages for permitted roles.
- **Retention**: each app documents how long personal data is kept and deletes or anonymises it afterwards (a
  scheduled command); requests to see, correct or delete data have a documented procedure.
- **Logs**: no personal data in application logs, analytics or error trackers (IDs only).
- **Environments**: production personal data never goes to staging or a laptop; demo data uses invented people.
- **Backups**: encrypted when they leave the server; access limited to the developer.
- **Privacy page**: "Kebijakan Privasi" explains what is collected, why, how long, who can see it, and how to ask.

## 4. Audit log

- Every create, change and delete of important data (applicants, results, payments, settings, users, permissions)
  records who, when, from where (IP stored only as needed), what, and before/after values (secrets masked).
- Admins read it in Indonesian ("Siti mengubah tanggal lahir dari 1 Mei 2013 menjadi 2 Mei 2013"), filter by
  record, person and date; entries cannot be edited or deleted from the app.

## 5. Indonesian identity data

| Field | Rule |
| --- | --- |
| NIK | 16 digits; first 6 a valid region code (Fondasi `wilayah`), digits 7–12 a plausible birth date (day + 40 for women); stored as text |
| No. KK | 16 digits, stored as text |
| NISN | 10 digits; NPSN 8 digits; NSM (madrasah) 12 digits; all text |
| Name | One word is valid (many Indonesians have a single name); letters, spaces, apostrophes, dots, hyphens; no forced first/last split; keep the user's capitalisation; length ≥ 2 |
| Address | Street/kampung + RT/RW + region codes from Fondasi `wilayah` (province → village picker) + postal code (`kodepos`) |
| Phone | Stored as `+628…`, accepted as `08…`, `628…`, `+628…`, with spaces or hyphens; shown `0812-3456-7890` |
| WhatsApp | Primary contact channel: "Hubungi lewat WhatsApp" buttons as `https://wa.me/628…?text=…` with an Indonesian prefilled text; email second |
| Time | Stored with an explicit zone (UTC or a timezone-aware column); shown in the app's zone with its label (`07.30 WIB`, `WITA`, `WIT`) from settings |
| Deadlines | Opening and closing times (registration, uploads, results) are enforced on the server, not only hidden in the UI |

## 6. Performance on low-end phones

- Target on a mid/low Android over 4G: Largest Contentful Paint < 2.5 s, interaction delay < 200 ms, no layout shift
  (CLS < 0.1) on the main public pages.
- Images WebP/AVIF with width/height set and `loading="lazy"` below the fold; CSS/JS/SVG minified; long cache for
  versioned assets; HTML compressed by the web server/Cloudflare.
- Lists paginated or virtualised; no N+1 queries (eager loading, indexes on filter columns); heavy work (imports,
  PDF batches, emails) in a queue or command, with progress shown.
- Check with Lighthouse (mobile) and on a real low-end phone before launch.

## 7. Health and monitoring

- `/healthz` (no auth, no data) answers 200 when the app and database are up; used by Docker and the uptime monitor.
- Structured logs (one line per event, level, request ID), rotated, without personal data.
- An external uptime monitor on each production domain alerts the developer (email/WhatsApp/Telegram).
- A friendly maintenance page ("Sedang ada perbaikan, coba lagi pukul 21.00 WIB") during planned work.
- Backups daily with a monthly restore drill on staging ([app-contract.md](app-contract.md)).

## 8. Staging stays closed

- Staging hostnames behind Cloudflare Access; `X-Robots-Tag: noindex, nofollow` on every staging response;
  `robots.txt` and `sitemap.xml` allow indexing only on production.
- Staging runs in production mode (real errors hidden), sends no emails/WhatsApp to real people (sandbox or catch-all).
- Demo and seed data contain no real people.

## 9. Tests and CI (minimum)

- Feature tests for: every permission (allowed and denied), the main user journey of each module, validation of the
  Indonesian identity fields, exports (headers in Indonesian).
- Migrations reversible (or a documented reason), run in CI against the production database engine/version.
- CI must be green before merging: tests, lint, dependency audit, commit policy.
- All user-facing text in language files (`id` first), never hard-coded in controllers or templates.

## 10. Public pages

- Required: **Kebijakan Privasi**, **Syarat Penggunaan**, **Kontak/Bantuan** (WhatsApp, email, hours), friendly
  **404/500** pages with a way back, guides per role (`/panduan`).
- Sharing: `<title>`, meta description, Open Graph and Twitter tags with a share image (1200×630) from white-label
  settings, favicon and app icons (`manifest.webmanifest`), canonical URLs, `lang="id"`.
- Printing: cards, receipts, attendance sheets and certificates print cleanly on A4 and F4 (`@page` sizes), black
  and white readable; QR codes carry a random token, never NIK/NISN.
- Unreliable connections: long forms keep a draft in the browser (no sensitive fields such as passwords or NIK in
  plain storage unless the user is told), uploads can resume or retry, a clear message when offline
  ("Koneksi terputus. Data Anda masih tersimpan di perangkat ini.").
