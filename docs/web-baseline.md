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
  what the agreed purpose needs. Public apps keep it short; **internal school apps** may hold detailed records
  (health, family, aid, special needs) under a school–parent agreement — rules in [school-data.md](school-data.md).
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

## 6. Performance: rich pages that work at once (F-022)

- Pages may be **heavy with decoration** (Codex illustrations, patterns, animation): most users have fast connections.
  What must never wait for decoration is the page itself: text, navigation, forms and buttons work as soon as the HTML
  and the core CSS/JS arrive.
- **Load order**: core content and functionality first; decorative images, animations, three.js/canvas scenes, video
  and background patterns after (`loading="lazy"`, `decoding="async"`, deferred scripts, `fetchpriority="low"`,
  started after first paint or when visible). A decoration that fails to load leaves the page intact.
- **Never blank**: every area that waits for data or a heavy asset shows a **skeleton** of its final shape (lists,
  cards, charts, tables, hero art) instead of an empty space or a lone spinner; skeletons reserve the exact size, so
  nothing jumps (CLS < 0.1); a shimmer is allowed, off under `prefers-reduced-motion`.
- Targets on the main public pages over 4G: content readable (LCP of the main text/heading) < 2.5 s and interactive
  < 200 ms delay, regardless of how much decoration follows.
- Images WebP/AVIF with width/height set; CSS/JS/SVG minified and versioned ([assets.md](assets.md)); HTML compressed
  by the web server/Cloudflare.
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
- Printing: see section 11.
- Unreliable connections: long forms keep a draft in the browser (no sensitive fields such as passwords or NIK in
  plain storage unless the user is told), uploads can resume or retry, a clear message when offline
  ("Koneksi terputus. Data Anda masih tersimpan di perangkat ini.").

## 11. Printing and QR codes (F-020)

- **Paper**: Indonesian offices print on **A4** (210 × 297 mm) and **F4/Folio** (215 × 330 mm). Every printable document
  (cards, receipts, attendance sheets, letters, certificates, reports) offers both, A4 by default (a setting per app or
  per document); PDFs are generated at the exact size, not scaled.
- Margins ≥ 15 mm (20 mm on the binding side for letters), fonts embedded, readable in black and white, no content
  cut at page breaks (tables repeat their header row), page numbers `Halaman 1 dari 3`, identity (name, logo) from
  white-label settings; HTML print views use `@page { size: A4 }` / `size: 215mm 330mm` and hide navigation.
- **QR design is unique per app** (F-022): never the default black-square QR. Each app has its own QR style, designed
  through a Codex brief: module shape (rounded, dots), finder-eye shape, brand colours from settings (dark on light, AA
  contrast), the app's or client's **logo in the centre** when there is one, and optionally a frame with a short
  Indonesian label ("Pindai untuk cek kartu"). Rendered by a styling library or the app's own renderer from that
  design, the same on screen and in PDFs.
- Scannability comes first: error correction level **H** with a logo (logo ≤ 20% of the width on a padded background),
  quiet zone of 4 modules, no gradients or low contrast inside the modules, printed size ≥ 2 × 2 cm; every design is
  test-scanned with at least two phones (Android and iOS camera apps), on screen and printed in black and white.
- Content stays safe: a random, unguessable token (≥ 128 bits) resolved on the server — never NIK, NISN, names or
  sequential IDs; tokens can be revoked or replaced.

## 12. Visitor statistics without personal data (F-020)

- Public apps count page views and unique visitors per day from a one-way hash of IP + browser with a **salt that
  changes every day**; no IP address, browser string, cookie ID or other personal data is stored (proven in SPMB D-106).
- Bots, staff pages and signed-in staff are not counted; the same page in different languages counts as one page.
- Admins see a summary (today, this month, total), a daily chart and the most opened pages; the public footer may show
  "Pengunjung hari ini / bulan ini / total" (a setting, default on).
- No third-party analytics scripts by default (privacy, CSP, speed); if a client needs one, record it as a decision
  and mention it in the privacy page.
