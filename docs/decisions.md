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
