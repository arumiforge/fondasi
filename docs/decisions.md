# Decisions (Fondasi)

IDs `F-001`… are Fondasi's own; apps keep their own logs (SPMB: `D-…`). Newest last.

## F-001 — One shared repository for rules, data and skills (2026-11-25)
Status: accepted (user, 2026-11-25)
Context: Arumi Studios builds several apps with different stacks (SPMB in CodeIgniter, others) that share one VPS, Cloudflare, school and region data and the same Indonesian writing rules. Repositories share nothing, so every repo and every Claude session re-derived them.
Decision: `arumiforge/fondasi` (created as `server`, renamed by the user) holds the server rules and scripts, the app contract, standards for settings and storage, public reference data and shared agent skills. App repos point to it from their `CLAUDE.md`; it is not a runtime dependency.

## F-002 — One server flow (carried over from SPMB D-112) (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: `server/check.sh` (read-only, states S0…S9, next command) is the first command on any server; `server/setup.sh` prepares fresh servers and servers already in use without breaking them (keeps Docker packages, merges `daemon.json`, no Docker restart while containers run, `ALLOW_PORTS`/`FIREWALL`). Every app follows `docs/app-contract.md`. On the VPS the checkout lives at `/opt/apps/_fondasi`.

## F-003 — Apps copy pinned data versions (2026-11-25)
Status: accepted (user, 2026-11-25: "salin versi tertentu")
Decision: Data sets are versioned files in `data/<set>/` with `manifest.json` and `SHA256SUMS`. Apps copy one version with `tools/fondasi-sync` into `data/fondasi/<set>/` and record it in `fondasi.lock`; they import it into their own database their own way. No submodule, no runtime dependency. A central data API on the VPS may come later on top of the same files.

## F-004 — One Cloudflare Tunnel per VPS; routes in the dashboard (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Each VPS runs one remotely managed tunnel (`cloudflared` on the host). A new app = a new *Public Hostname* in the Cloudflare dashboard → `http://127.0.0.1:<port>`, recorded as the third column of `/opt/apps/PORTS`. A separate tunnel only when an app belongs to another client or Cloudflare account, or must be revocable on its own (its own systemd unit, token kept on the server).

## F-005 — Settings: environment wins over the panel (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Integrations (S3/R2 storage, Turnstile, mail, AI providers…) read standard environment variables (`docs/settings.md`). When a variable is set, the app's panel shows the value as "Diatur oleh server" and cannot change it; when it is empty, the panel's value is used, secrets stored encrypted. Developers can lock a setting; schools can still manage their own.

## F-006 — Files: VPS disk by default, S3-compatible optional; public-sector personal data stays in Indonesia (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Uploaded files live on the VPS disk outside the web root by default (in the app's backed-up volume). Any S3-compatible provider may be used per app (Cloudflare R2, AWS S3, Wasabi, Backblaze B2, IDCloudHost, Biznet Gio…) through the standard `STORAGE_*` variables. For clients that are public institutions (sekolah negeri, dinas, government bodies), personal data stays on storage located in Indonesia (PP 71/2019 for public electronic system operators); check each client with a lawyer. Server backups (restic to R2, SPMB D-079) are a separate bucket and key from app files.

## F-007 — Shared data scope (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Fondasi provides: regions (with postal codes), schools of every level (SD, MI, SMP, MTs, SMA, MA, SMK, SLB) from Dapodik and EMIS, education calendars (national holidays and cuti bersama per SKB 3 Menteri; Kaldik Jawa Tengah from Disdikbud; madrasah calendars from Kanwil Kemenag Jawa Tengah; academic-year rules), Dapodik reference lists (religion, occupation, income, education, transport, residence, special needs, levels and grades), Kurikulum Merdeka subjects, higher-education institutions (PDDikti), and athletics references (events, school age groups, result format and rounding, records). The catalogue in `data/README.md` tracks each set's status.

## F-008 — Several VPS: labels, one tunnel each, an inventory without secrets (2026-11-25)
Status: accepted (user, 2026-11-25: "kemungkinan punya VPS yang berbeda")
Decision: Each VPS has a short label (`SERVER_NAME` in `setup.sh`, recorded in `/opt/apps/.server-setup` and shown by `check.sh`), its own Cloudflare Tunnel, admin hostnames `konsol-<label>.` / `ssh-<label>.` on the admin domain (existing servers keep theirs), its own deploy keys and off-site backup prefix. `docs/servers.md` lists servers and their apps without IPs, ports or secrets, and describes moving an app between servers (backup, set up, restore, move the tunnel route).

## F-009 — Conventions for every repository (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Docs, code, commits and briefs in English; UI text and URL slugs in plain Indonesian (also behind translation prefixes); no personal data in URLs. Arumi Studios is the only author and contributor of every commit: no Claude, Codex or other AI attribution anywhere (commits, PRs, comments, files), enforced by the commit-msg hook and the commit-policy workflow in `templates/repo/`, which now also reject Codex/ChatGPT/Copilot attribution and any `Co-authored-by`. Agents open PRs and never merge unless the user asks. Details: `docs/conventions.md`.

## F-010 — UI and UX rules against generic AI-made design (2026-11-25)
Status: accepted (user, 2026-11-25: "aturan UI/UX umum menghindari desain generik AI slop")
Decision: SPMB's visual rules (D-070) become the base for every app, extended with a "never" list (gradient blobs, glassmorphism, default hero + three cards landing, vague marketing copy, emoji icons, lorem ipsum) and "always" rules (task first at 360 px, all screen states, labelled forms, AA accessibility, Indonesian formats, white label). `docs/ui.md`, skill `fondasi-ui`.

## F-011 — Codex makes visual assets in every app from briefs in the repository (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: The SPMB workflow (D-073, D-075) applies to every app: Claude writes briefs in the app's `ai/` folder, the user starts Codex with the starter prompt, Codex delivers one batch per PR into `ai/generated/` as Arumi Studios without attribution and never merges, Claude reviews and installs. Each app has its own `ai/style-guide.md` for identity and respect rules; templates in `templates/repo/AGENTS.md` and `templates/ai/`. `docs/visual-assets.md`, skill `fondasi-visual`.

## F-012 — Everything users see is Indonesian, including exports (2026-11-25)
Status: accepted (user, 2026-11-25: "ekspor Excel, kolom tetap pakai Indonesia ramah meski variabel dan doc bahasa Inggris")
Decision: Code, variables and docs stay English, but every surface a user sees, downloads or receives is plain Indonesian: page text, messages, emails, notifications, PDFs, download file names, Excel/CSV headers and sheet names, import templates, status labels. Exports follow the table in `docs/conventions.md` (labels not codes, identifiers as text, real date/number cells, `Keterangan` sheet, XLSX first, CSV with BOM and `;`).

## F-013 — Web app baseline for every app (2026-11-25)
Status: accepted (user, 2026-11-25: all sixteen proposed rules)
Decision: Every web app follows `docs/web-baseline.md`: web security basics (HTTPS, cookies, security headers, CSRF, password hashing and rate limits, staff 2FA, permission checks with ownership, dependency audit), safe uploads, personal data under UU PDP (purpose, masking, retention, no personal data in logs or staging, privacy page), an audit log readable in Indonesian, Indonesian identity data rules (NIK, KK, NISN, NPSN, NSM, single-word names, addresses with Fondasi region codes, phones and WhatsApp, time zones, server-enforced deadlines), performance targets for low-end phones, health checks and monitoring, closed staging, minimum tests and CI, required public pages, share previews, print layouts and resilience to bad connections. Skill `fondasi-web`.

## F-014 — Feedback by consequence: tiers, placement and accessibility (2026-11-25)
Status: accepted (user proposal "hybrid UI feedback designer", reviewed and adjusted, 2026-11-25)
Decision: Messages follow `docs/feedback.md`: tier 0 in place, tier 1 toast (≥ 5 s, pauses on hover/focus, close button), tier 2 undo toast (≥ 10 s, keyboard reachable, server-side undo, undo also elsewhere), tier 3 inline errors with an error summary and focus, tier 4 confirmation dialog only for irreversible actions (safe button focused, Enter never destroys), tier 5 page banners; the end of a long flow is a result page, not a modal. Desktop toasts bottom-right clear of floating widgets; phone toasts top-centre in the safe area with swipe and a close button; dialogs as bottom sheets on phones. Flash messages survive without JavaScript. Skill `fondasi-feedback` applies, audits and writes PRDs from it.
Consequences (changes to the proposal): a tier 0 and a tier 5 were added; durations lengthened and made pausable (WCAG 2.2.1); undo preferred over confirmation; Enter no longer confirms destructive dialogs; completion and fatal errors moved out of modals; rules live in one doc that the skill points to, written in English like other Fondasi docs.

## F-015 — Fondasi stays app-neutral; apps plug in (2026-11-25)
Status: accepted (user, 2026-11-25: "aturan tidak hanya untuk repo SPMB tapi bisa diadaptasi untuk repo lain")
Decision: Nothing in Fondasi depends on one app. Rules, scripts and templates are written for any app and any stack; SPMB appears only as a labelled example (its decisions are cited as "SPMB D-…"). App-specific behaviour lives in the app's repository and plugs into Fondasi through defined points: the pointer block in `CLAUDE.md`, `AGENTS.md` and `ai/` from the templates, `fondasi-sync` for data and skills, `/opt/apps/PORTS` lines and an optional `/opt/apps/<app>/check-app` adapter for the server check. `server/check.sh` no longer contains SPMB logic: its states end at S2 (ready), S3 (an app needs attention) and S9 (every app answers). When a rule proves useful in one app and fits others, it moves here; when it fits only one app, it stays there.

## F-016 — Fondasi is the base; each repository adopts it and decides its details (2026-11-25)
Status: accepted (user, 2026-11-25: "Claude yang bekerja untuk tiap repo punya dasar dulu, arah selanjutnya user dan Claude yang menentukan")
Decision: Any repository (new or existing, any stack) adopts Fondasi through `docs/adopting.md` and the `fondasi-adopt` skill: read, audit against Fondasi (report `docs/fondasi-audit.md` in the app), interview the user, set up the base from `templates/repo/` (CLAUDE.md skeleton with placeholders, AGENTS.md, hooks, CI, progress, decisions with D-001 "Adopt Fondasi"), then plan the fixes with the user. Fondasi stays general; app-specific details are decided in the app repository and recorded there.

## F-017 — One way of working for agents in every repository (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: `docs/agent-workflow.md` is the shared way Claude sessions (and Codex) work in any repository: the repository is the memory (`CLAUDE.md`, `AGENTS.md`, `docs/progress.md`, `docs/decisions.md`, interview rounds, `CHANGELOG.md`), the same session start and end, task lists for multi-step work, decisions recorded when made, context kept lean, small pushed steps, coordinator/worker protocol for large rounds, browser sessions for blocked sources. Each repository plants it as its own `<app>-session` skill from `templates/repo/.claude/skills/app-session/`.

## F-018 — Minify only served copies, keep originals, version every asset (2026-11-25)
Status: accepted (user, 2026-11-25; from SPMB D-086, D-094)
Decision: Build tools (any stack) minify CSS, JS, SVG and HTML responses into the served copies only; originals stay readable in the repository and are never overwritten. External libraries are installed, pinned, bundled and self-hosted (no runtime CDN). Every served asset URL carries a content version (hashed file name or `?v=`) so changes are never stuck in caches; versioned assets are cached for a year as immutable, HTML is not cached long. Details: `docs/assets.md`.

## F-019 — AI help assistant: OpenAI-compatible providers, round robin, Gemini settings, limits (2026-11-25)
Status: accepted (user, 2026-11-25; from SPMB D-110)
Decision: Apps with an AI assistant follow `docs/ai-assistant.md`: quick choices and the app's own Q&A first, AI last on the app's content only, handover to people; a list of OpenAI-compatible providers (encrypted keys, env wins over panel) used round robin with failover and resting on 429/5xx/auth errors/timeouts/empty replies; Gemini through its OpenAI-compatible endpoint with its own settings (base URL, minimal fields, thinking budget or `reasoning_effort`, empty replies treated as failures, paid tier for anything beyond public Q&A); limits per visitor and per site per day, question and answer length, short memory, topic restriction; personal data masked before matching, sending or storing.

## F-020 — Printing on A4 and F4; unique QR codes with a centred logo; visitor statistics without personal data (2026-11-25)
Status: accepted (user, 2026-11-25)
Decision: Printable documents offer A4 and F4 (215 × 330 mm), A4 by default, generated at exact size. QR codes are unique random tokens resolved on the server; with the app's logo in the centre they use error correction H, logo ≤ 20% of the width with padding, quiet zone kept, tested with two phones. Visitor statistics use a daily-salted hash only (SPMB D-106). Sections 11 and 12 of `docs/web-baseline.md`.

## F-021 — Guide pages in the style of GitHub Docs "Get started" (2026-11-25)
Status: accepted (user, 2026-11-25: "halaman panduan adaptasi dari docs.github.com/en/get-started, UI/UX sangat elegan")
Decision: In-app guides per role follow `docs/guides.md`: a calm landing page (one-sentence lead, "Mulai dari sini", all articles grouped by path with one-line descriptions, search), articles with breadcrumbs, task title, one-sentence lead, "Dalam artikel ini", one idea per section, numbered procedures, three callout kinds, related links, previous/next, "Apakah halaman ini membantu?", last updated; sidebar tree on desktop, collapsible on phones; restraint over decoration; guides change in the same PR as the feature.

## F-022 — Decoration without limits, made by Codex; pages work before decoration loads; skeletons; unique QR designs (2026-11-25)
Status: accepted (user, 2026-11-25; refines F-010, F-013 §6, F-020, F-021)
Decision: Fondasi sets no limit on decoration: illustrations, paintings, patterns, dividers, special buttons, loaders, animation and 3D are welcome everywhere, guides included, all made by Codex in the app's identity. Heavy pages are fine (most users have fast connections), but the page is fully usable before decoration loads: core content first, decoration deferred and lazy, a failed decoration leaves the page intact, skeletons of the final shape instead of blank areas, no layout shift, reduced motion respected. The "Never" list of `ui.md` targets generic looks, not quantity. "Unique QR" means a unique design per app (module and eye shapes, brand colours, centred logo, optional frame) designed through a Codex brief, with scannability rules (level H, quiet zone, contrast, two-phone test); the content stays a random server-side token.

## F-023 — Detailed student data in internal school apps; shared student schema (2026-11-25)
Status: accepted (user, 2026-11-25: "data yang sangat detail biasanya untuk aplikasi internal sekolah yang sudah ada persetujuan")
Decision: Public apps keep data short; internal school apps may hold detailed records under a written school–parent agreement, following `docs/school-data.md`: agreement versions and acceptance stored, purpose shown per group, permissions per field group (need to know), masking, audit of views and changes of sensitive groups, export permissions, encryption at rest where possible, nothing sensitive in notifications/URLs/logs/AI/staging, retention and parents' requests. The reference schema is the data set `skema-siswa` (61 fields, 17 option lists, from the user's file), adapted per app and later mapped to Dapodik codes.

## F-024 — Student schema corrections; one shared income list (2026-11-25)
Status: accepted (user, 2026-11-25: "NISN 10 digit, NIK siswa wajib, penghasilan ikut skema")
Decision: In `skema-siswa`, NISN is 10 digits (`max_len=10`) and the student's NIK is required; NIK, the mother's NIK and the KK number are 16 digits (`max_len=16`). The schema's `[penghasilan]` list (7 ranges, "Kurang dari Rp500.000 atau Tidak Berpenghasilan" up to "Lebih dari Rp10.000.000") is the shared income list for every app; SPMB's current list (Dapodik ranges with a separate "Tidak berpenghasilan") moves to it, mapping existing answers, and the mapping to official Dapodik codes follows with `referensi-dapodik` (R-07).

## F-025 — Calendars: national first, Jawa Tengah as the only province for now (2026-11-25)
Status: accepted (user, 2026-11-25: "kalender nasional yang mengcover nasional secara umum; untuk spesifik per provinsi cukup Jateng dulu")
Decision: Calendar data has three layers: national (SKB 3 Menteri holidays and cuti bersama, `libur-nasional`; the national education calendar when published, `kalender-nasional`), province (only Jawa Tengah for now, `kaldik-jateng`, plus the Kanwil Kemenag Jateng madrasah calendar) and, on demand, kabupaten/kota calendars for SD/SMP (the provincial regulation covers SMA, SMK and SLB). Apps combine them: national holidays win over provincial estimates; a school can still add its own days. Raw source documents are kept in `sources/<set>/` with their SOURCE.txt when their licence allows.

## F-026 — Sessions in Fondasi may merge their own PRs when CI is green (2026-11-25)
Status: accepted (user, 2026-11-25: "boleh sesi baru me-merge PR-nya sendiri setelah CI hijau")
Decision: In `arumiforge/fondasi` only, a session may merge its own PR into `main` when CI is green on the current head and there is no conflict, then report it to the user. It never merges other people's PRs. App repositories keep "agents never merge unless the user asks" unless they record the same decision. Work for the next rounds runs in the dedicated cloud environment "Fondasi".

## F-027 — World Athletics documents: facts with references, raw PDFs kept privately (2026-11-26)
Status: accepted (user, 2026-11-26: "Fakta + PDF di sources/")
Decision: The athletics sets use World Athletics' Competition & Technical Rules and the Scoring Tables for Combined Events although their licence is not on the list of F-003 (copyright World Athletics). The sets hold facts (weights, heights, rounding, codes, formula parameters) with rule or page references, not rule texts; the raw PDFs are kept in `sources/atletik/` because the repository is private. Athletics championships covered: O2SN, POPDA/POPNAS, PASI Kejurnas/Kejurda and championships run by the user; each championship keeps its own age reference date; combined-events scoring is included.

## F-028 — `sekolah`: which forms and regions are kept (2026-11-26)
Status: accepted (user, 2026-11-26: "Masukkan semua", "PKBM dan SKB saja", Luar Negeri "Tidak")
Decision: The `sekolah` set keeps every form that referensi.data.kemendikdasmen.go.id lists under Dikdas, Dikmen and PAUD, including SPK (cooperation schools, e.g. "SPK SMP") and Pendidikan Diniyah Formal ("PDF Wustha", "PDF Ulya"); apps filter by `bentuk_pendidikan`. From Dikmas (non-formal) only PKBM and SKB are kept; courses (LKP/"Kursus") are left out. Schools abroad (the source's "Luar Negeri" group, Sekolah Indonesia Luar Negeri) are left out because they have no Kemendagri region code.

## F-029 — Crawls of government reference sites: parallel workers (2026-11-26)
Status: accepted (user, 2026-11-26: "3 proses", then "coba 20 kali, saya dapat informasi server terbuka untuk pengambilan informasi"; 2026-11-27, R-17: "maksimalkan, gunakan resource penuh", then 40 workers, then "batasan tidak berlaku, karena web publik pemerintah ditujukan untuk itu")
Decision: A crawl of a public government reference site (R-01 and later sets) may run as many workers as the site serves well on referensi.data.kemendikdasmen.go.id (no fixed cap since 2026-11-27; twenty until then; the session raises the count while throughput still grows and stops where response times climb, e.g. R-17: 80 threads 843 pages/min, 160 threads 1,086 pages/min with 4–14 s responses, kept at 160), which the user was told is open for data retrieval (other sites: three unless the user says otherwise), each waiting at least one second between its requests and each fetching its own regencies, so no page is fetched twice. Before, crawls were strictly sequential (user, 2026-11-25). Pages that the parent page shows to hold none of the kept forms are not fetched (Dikmas districts without PKBM or SKB). A crawl slows down or stops when the site answers with errors or rate limits: workers pause a minute on 429/502/503/504, and the session lowers the number of workers when retries pile up.

## F-030 — Curriculum data from the sinaubareng audit: mapel for all levels, CP, TKA; school coordinates later (2026-11-26)
Status: accepted (user, 2026-11-26: "Semua jenjang", "CP agama SD & MI, CP semua mapel, Kerangka TKA", coordinates "Nanti, semua sekolah")
Decision: Fondasi takes public curriculum data found in arumiforge/sinaubareng (audit in `docs/sinaubareng-audit.md`): the source regulations are copied to `sources/` and three sets are built from them, each in its own PR: `mapel` (R-08) for every level — SD, SMP, SMA, SMK, SLB, kesetaraan from Permendikdasmen 13/2025 (with 12/2024) and RA/MI/MTs/MA/MAK from KMA 1503/2025 — with sinaubareng's checked SD/MI and MI tables used as a cross-check, not copied blindly; `capaian-pembelajaran` (R-15) for all subjects and phases from Kepka BSKAP 046/H/KR/2025, its amendment Kepka BKPDM 020/2026 (religion) and SK Dirjen Pendis 9941/2025 (madrasah); `kerangka-tka` (R-16) from Perka BSKAP 047/H/AN/2025 and Kepmendikdasmen 56/2026. App content curated by SIGRAK (topics, TP/ATP, catalogs, taxonomy, level profiles, regulation digests) stays in the app. School coordinates (latitude/longitude from referensi.data NPSN pages) are added to `sekolah` later for all units, as a separate crawl under F-029 (R-17). The user makes sinaubareng private because its sources include personal data.

## F-031 — Printed errors in official tables; Bahasa Inggris transition for SD/MI only (2026-11-26)
Status: accepted (user, 2026-11-26: "64, catat yang tercetak", "Hanya SD/MI", "Pasal 33 sudah cukup")
Decision: When a cell of an official table contradicts the table's own printed totals and the arithmetic shows which value is meant (e.g. Permendikdasmen 13/2025 Tabel 20 prints intrakurikuler 54 where the row total 64 and the table total 992 need 64), a data set stores the value the totals require, keeps the printed one beside it (`printed_*`) and lists the case in the set's `errata` with page and reason. When the totals cannot tell which cell is wrong, rows and totals stay as printed and the erratum is marked `unresolved`. Nothing is corrected silently. In `mapel`, Bahasa Inggris in SD/MI grades III–VI carries the transition of Permendikbudristek 12/2024 Pasal 33 huruf a (elective by school readiness until 2026/2027, compulsory from 2027/2028); SDLB/MILB tables keep Bahasa Inggris as printed, without that transition.

## F-032 — `capaian-pembelajaran`: full content; religion CP from Kepka BKPDM 020/2026 in a second, checked step (2026-11-26)
Status: accepted (user, 2026-11-26: "Bertahap, diperiksa", "Lengkap")
Decision: The set keeps, per subject, Rasional, Tujuan, Karakteristik, the element table with descriptions, and the CP per phase and element, from Kepka BSKAP 046/H/KR/2025 (Lampiran I–V, parsed from the text layer) and SK Dirjen Pendis 9941/2025 (madrasah). The religion CP of 046 (Lampiran II I.1–I.6, Lampiran V I.1–I.6) is left out because Kepka BKPDM 020/2026 replaced it; 020 is a scan, and its OCR has systematic errors (Al-Our'an, lost diacritics, ; read as ,), so it comes in a later PR: SD phases A–C from sinaubareng's word-by-word checked transcription, phases D–F and the special-education religion CP read and checked against the page images. Raw OCR text is never published as data.

## F-033 — `kerangka-tka`: sample questions included; category limits from press reports, marked secondary; SMA/SMK later (2026-11-27)
Status: accepted (user, 2026-11-27: "sma/smka nanti. contoh soal ikut dimasukkan. Batas nilai untuk kategori Baik/Memadai/Kurang"; "Masukkan, tandai sekunder")
Decision: `kerangka-tka` keeps the sample questions of Perka BSKAP 047/H/AN/2025 part IV in full (stimuli with their texts, questions, options or statements, keys as printed, figures cut from the page renders), with mislabelled item forms recorded as errata rather than corrected. The category limits for TKA results are not stated in any regulation found (Kepmendikdasmen 56/2026, Juknis 017/F/AN/2026), so the 2026 limits reported from the Pusmendik briefing (Kurang < 50, Memadai 50–< 76,67, Baik ≥ 76,67, istimewa ≥ 95, every subject, SD/MI and SMP/MTs) are stored with `confidence: secondary` and their sources, and the conflicting report for Matematika SMP (33,33 / 56,67) is kept beside them, unresolved. Replace both with an official document when one appears. The SMA/SMK framework is added later, when BSKAP publishes one.

## F-034 — Third-party works for education, with credit (2026-11-27)
Status: accepted (user, 2026-11-27: "teks puisi dan ulasan, juga semua hal karya pihak lain yang bisa digunakan dengan menyertakan pemilik asli bisa digunakan. dan tujuan besarnya untuk pendidikan.")
Decision: Fondasi data may include works of third parties (poems, articles, screenshots, images) when they serve education and their owners are credited. Each such item carries an `attribution` (credit line naming the owner and where it was published or printed; owner and URL where known) and THIRD_PARTY_NOTICES.md lists it; apps that show the item show the credit with it. Where no owner is printed, the publishing document (e.g. the regulation) is credited. Licences that forbid this use, or a request by an owner, still win: such an item is removed. First applied to the sample questions of `kerangka-tka` (F-033).

## F-035 — Administrative boundaries from BIG, simplified, added per regency (2026-11-27)
Status: accepted (user, 2026-11-27: "Tingkat ketelitian: ±11 m. sementara untuk kudus dulu.")
Decision: Village and district boundaries come from Badan Informasi Geospasial's Basis Data Batas Wilayah
Administrasi (Edisi Juni 2026), the official source keyed by Kemendagri codes; it is Informasi Geospasial Dasar and
open by law (UU 4/2011 Pasal 12 huruf e, Pasal 42), credited as "Sumber: Badan Informasi Geospasial". GADM
(no redistribution), OpenStreetMap (ODbL, incomplete) and the 2020 BPS/OCHA set (BPS codes) are not used;
cahyadsn/wilayah_boundaries (MIT) may serve as a cross-check. `data/batas-wilayah` holds GeoJSON per regency for
desa and kecamatan, simplified to about 11 m on shared arcs so neighbours stay together; districts are the union of
their villages. Regencies are added on demand, Kabupaten Kudus first, then all 35 regencies of Jawa Tengah (user,
2026-11-27: "tambahkan juga untuk seluruh jawa tengah"); the set stops there until the user asks for more (user,
2026-11-27: "cukup jawa tengah dulu"). Full-precision downloads are kept outside the repository
(65 MB for Jawa Tengah); `sources/batas-wilayah/SOURCE.txt` records the fetch time and `content_sha256` of every
regency, and only Kudus's download stays in `sources/batas-wilayah/` as a sample that rebuilds its files. Coordinates
have 6 decimals; arcs where rounding to 6 decimals would make a ring cross itself (BIG's own rings do not) keep up to
9 decimals, listed per regency in the manifest (`villages_with_more_decimals`). Full precision for apps is not stored in Fondasi or in
any bucket or drive: each server fetches it from BIG itself with `batas-wilayah.py presisi`, which refuses content
that differs from the `content_sha256` Fondasi recorded per regency (user, 2026-11-27: "pilih A, server ambil
langsung dari BIG"). Apps show the boundary status and never present a boundary as legal.

## F-036 — `sekolah` coordinates: nothing guessed, outliers kept and flagged, sign and swap fixed only when they fit (2026-11-27)
Status: accepted (user, 2026-11-27: "Null + alasan", "Simpan titik + tandai", "Perbaiki bila pas")
Decision: R-17 adds `lintang`/`bujur` from each unit's detail page (`/satpen/detail/<npsn>`) to `sekolah`, with `koordinat_cek`, `koordinat_perbaikan` and `koordinat_sama`. A unit whose page prints no pair or 0 keeps `null` with the reason (`kosong`, `nol`); no point is estimated from region centroids. A pair that lies in Indonesia but outside the unit's regency is kept as printed and flagged (`provinsi`, `luar_provinsi`), so apps can filter it; nothing is moved silently. A pair whose latitude sign was lost or whose Lintang/Bujur are swapped is corrected only when the corrected pair lies in the unit's own regency; the rule goes to `koordinat_perbaikan` and the printed values to the manifest's `coordinate_errata` (as F-031 does for tables). Any other pair outside Indonesia is `null` (`luar_indonesia`). The region check uses simplified regency boundaries (cahyadsn/wilayah_boundaries, MIT) with a 5 km margin and, for points at sea or on small islands, the nearest regency within 50 km. `koordinat_sama` counts units sharing exactly the same pair. Default pairs the source fills in (a pair used by 10 or more units in 3 or more regencies, e.g. -5.443757, 114.421127 at sea off Sumenep, used by about 4,900 PAUD units across Indonesia) are not locations: they become `null` with `koordinat_cek: bawaan` and are listed in the manifest (user, 2026-11-27: "Null, alasan 'bawaan'").

## F-037 — `atletik-rekor`: PASI and World Athletics lists, holders as published, championship records later (2026-11-28)
Status: accepted (user, 2026-11-28: "daftar kejuaraan gunakan seadanya dulu"; World Athletics lists "Rekor dunia
senior, Rekor dunia U20, Prestasi terbaik dunia U18, Rekor Asia"; holders "Lengkap dengan tanggal lahir"; national
records from Wikipedia marked secondary when PASI is not reachable)
Decision: R-11 uses the championships already covered (F-027) and does not wait for the user's list. `atletik-rekor`
holds the Indonesian national records senior, U20 and U18 from PASI's own tables at www.pbpasi.org (the federation's
site; pasi.or.id, tried before, does not resolve), and World Athletics' world records, world U20 records, world U18
best performances and Asian records from worldathletics.org/records. Because PASI's official tables were found,
Wikipedia's list is not used as data: it only cross-checks the PASI senior tables, and every difference is listed
in the manifest's `cross_check_wikipedia` without changing the PASI values. Holders appear exactly as the federations
publish them: name, birth date (or year), PASI province (mapped to the `wilayah` code) or World Athletics country.
This is an exception to the rule "no athletes' private details" for record holders only, because the records are
public results the federations publish with these fields; nothing else about a holder is stored, and a holder who
asks to be removed is removed from the set (as F-034 does for owners). PASI's printing errors follow F-031: a mark
with only one possible reading is normalised with a `resolved` erratum; impossible dates, holders older than the age
group on the day of the record, and one athlete printed with different birth dates stay as printed with
`unresolved` errata. Championship records (O2SN, POPDA, POPNAS, championships the user runs) and U16/U14 national
records are added when an organiser publishes them or the user gives the list.
