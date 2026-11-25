# Conventions for every repository (F-009)

Apply to every Arumi Studios repository, app or not. An app may add rules, never loosen these.

## Language

| Surface | Language |
| --- | --- |
| `docs/`, `*.md`, code, identifiers, code comments, commit messages, PR titles and bodies, briefs for Codex | **English** |
| UI text, emails, PDFs, notifications, in-app guides, error messages | Friendly, plain **Indonesian** (`bahasa-indonesia-plain`); other languages only as translations of it |
| URL paths and route slugs | **Indonesian** (rules below), also on translated pages |
| Database tables and columns | English (`applicants`, `birth_date`); values shown to users stay Indonesian |
| Replies to the user in chat | Indonesian when the user asks for it (current preference), otherwise English |

Users are non-technical (school staff, students, parents, coaches, athletes): no jargon outside super-admin screens.

**Rule of thumb: whatever a user can see, read, download or receive is Indonesian**, even when the code behind it
is English. That covers page text, buttons, validation and error messages, empty states, emails (subject too),
WhatsApp/notification templates, PDFs, file names of downloads, export headers and sheet names, import templates,
audit-log descriptions shown to admins, status and enum labels (`Diterima`, not `accepted`), and HTTP error pages.

## Exports and imports (Excel, CSV, PDF)

| Rule | Example |
| --- | --- |
| Column headers in friendly Indonesian, sentence case, never the variable name | `Nama lengkap`, `Tanggal lahir`, `Sekolah asal` — not `full_name`, `birth_date` |
| Values as users read them: labels, not codes or booleans | `Laki-laki`, `Ya`/`Tidak`, `Diterima` — not `L`, `1`, `accepted`; empty cells stay empty (never `null`) |
| File and sheet names in Indonesian with the date | `daftar-pendaftar-2026-11-25.xlsx`, sheet `Pendaftar` |
| Real types in XLSX: dates as date cells shown `25/11/2026`, money and counts as numbers (`Rp#,##0`) | Sorting and sums work in Excel |
| Identifiers as **text** so leading zeros survive | NIK, NISN, NPSN, phone numbers, postal codes |
| Header row frozen, filter on, sensible column widths; an info sheet `Keterangan` with export time (WIB), the filters used and who exported | Readable without explanation |
| XLSX first. CSV only on request: UTF-8 with BOM, `;` separator (Indonesian Excel), same headers | Opens correctly in Excel with Indonesian settings |
| Import templates use the same Indonesian headers; the importer accepts them (and the old ones) and reports errors per row in plain Indonesian | `Baris 12: tanggal lahir belum diisi` |
| PDFs: A4, Indonesian, school/app identity from settings, page numbers `Halaman 1 dari 3` | Printable as is |
| Exports with personal data need a permission, are written to the audit log, and are never cached in a public place | UU PDP |

## URLs

- Indonesian, lowercase, words joined by hyphens: `/daftar`, `/cek-status`, `/admin/sekolah-asal`, `/jadwal-tes`.
- Nouns for pages, verbs for actions: `/admin/pendaftar`, `/admin/pendaftar/{id}/ubah`, `/admin/pendaftar/tambah`.
  Standard words: `tambah`, `ubah`, `hapus`, `lihat`, `unduh`, `cetak`, `impor`, `ekspor`, `cari`, `pengaturan`, `panduan`.
- No personal data in a URL (no NIK, NISN, name, phone): use a random token or an internal ID behind a permission check.
- Translated public pages keep the Indonesian slug behind a language prefix (`/en/jadwal`, `/ar/jadwal`, SPMB D-109).
- Admin area under `/admin`, guides under `/panduan` (public) and `/admin/panduan` (staff).
- An old URL that changes answers 301 to the new one.

## Commits, pull requests, contributors

- Author and committer of every commit: `Arumi Studios <arumiforge@gmail.com>`. Arumi Studios is the **only**
  contributor: no Claude, Codex, Copilot or other AI as author, co-author or contributor.
- **No AI attribution anywhere**: no `Co-Authored-By`, `Claude-Session`, "Generated with/by Claude/Codex/ChatGPT",
  tool links or footers in commits, PR titles, bodies, comments or files. Tools that add a footer automatically
  (e.g. a PR-creation tool) must have it removed right after.
- Enforced by `templates/repo/.githooks/commit-msg` (`git config core.hooksPath .githooks`) and
  `templates/repo/.github/workflows/commit-policy.yml`; copy both into every new repository.
- Conventional Commits in English: `feat(<area>): …`, `fix:`, `docs:`, `chore:`, `ci:`, `refactor:`, `test:`.
- Work on a branch, open a PR into `main`. Agents never merge unless the user asks in their own words.
- Repositories are private and proprietary (`LICENSE`); never publish contents; check dependency licences
  (MIT, BSD, Apache-2.0, ISC fine; ask before GPL/AGPL/commercial) and list them in `THIRD_PARTY_NOTICES.md`.

## Agent files in every repository

| File | For |
| --- | --- |
| `CLAUDE.md` | Claude: project guide + the Fondasi pointer block ([app-pointer.md](app-pointer.md)) |
| `AGENTS.md` | Codex (and other agents): scope and git rules; template `templates/repo/AGENTS.md` |
| `ai/` | Codex briefs for visual assets ([visual-assets.md](visual-assets.md)); template `templates/ai/` |
| `docs/progress.md` | Shared memory between sessions and accounts |
