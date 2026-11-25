# Data requests (briefs for browser sessions)

Each brief can be handed to a **Claude in Chrome** session on the developer's computer (or done by hand). The
browser session only **collects raw files**; a cloud session converts and checks them. Rules for every brief:

- Public pages only; no sign-in, no captcha solving, no scraping faster than one page every 2 seconds.
- Save raw files unchanged (PDF, XLSX, CSV, JSON, saved HTML) with the page URL and date in `SOURCE.txt`.
- No personal data. If a file contains names of people (e.g. officials' signatures), that is fine to keep raw,
  but nothing personal goes into a data set.
- Deliver: zip the folder `R-xx-<set>/` and give it to a cloud session (upload, or commit to `sources/<set>/`
  on a branch when it is small).

| ID | Set | What to collect | Where to look | Status |
| --- | --- | --- | --- | --- |
| R-01 | `sekolah` (SMP, SMA, SMK, SLB) | Every school per district with NPSN, name, level, status, address, village, coordinates if shown | `referensi.data.kemendikdasmen.go.id` and `dapo.kemendikdasmen.go.id` are reachable from cloud sessions: **done by a cloud session**, not the browser | open |
| R-02 | `sekolah` (MTs, MA; MI refresh) | Madrasah list per province: NSM, NPSN, name, level, status, address, village/district/regency | EMIS Kemenag public pages (`emis.kemenag.go.id` is blocked from the cloud), or the Kanwil/Kemenag open-data downloads | open — browser |
| R-03 | `kodepos` | Postal code list per village with region codes, and its licence | `github.com/cahyadsn` (wilayah postal-code repository) — reachable from the cloud; licence check first | open |
| R-04 | `libur-nasional` | SKB 3 Menteri on national holidays and cuti bersama for 2026, 2027 and 2028 (when signed): the PDF and the announcement page | `kemenkopmk.go.id` (reachable from the cloud), `jdih` pages of the ministries | **done 2026-11-25** by a cloud session (2026, 2027; 2028 not yet signed) |
| R-05 | `kaldik-jateng` | Kalender Pendidikan Jawa Tengah 2025/2026, 2026/2027 (and 2027/2028 when out): PDF/image + the SK | `disdikbud.jatengprov.go.id` (blocked from the cloud) | **done 2026-11-25** (2025/2026, 2026/2027; the site moved to pdk.jatengprov.go.id) |
| R-12 | `kalender-nasional` | The national education calendar for 2026/2027 (and 2027/2028 when out) if Kemendikdasmen publishes one — regulation/circular + its attachment; the Kemenag madrasah calendar guideline for the same years(the SKB 2026 and 2027 are done in R-04) | `kemendikdasmen.go.id`, `jdih.kemendikdasmen.go.id`, `kemenag.go.id`, `kemenkopmk.go.id` | open — browser |
| R-13 | `kaldik-kabupaten` (on demand) | A kabupaten/kota calendar for SD/SMP when an app needs it, starting with the first client's district (Kabupaten Kudus) | the Dinas Pendidikan of that kabupaten/kota | optional |
| R-06 | `kaldik-madrasah-jateng` | Kalender Pendidikan Madrasah Jawa Tengah for the same years + the SK | `jateng.kemenag.go.id` (reachable), Kanwil announcements | open |
| R-07 | `referensi-dapodik` | Official code tables: agama, pekerjaan, penghasilan, jenjang pendidikan, alat transportasi, jenis tinggal, kebutuhan khusus, bentuk pendidikan, tingkat pendidikan | Dapodik user manuals (PDF), `dapo`/`referensi` pages, the Dapodik import templates (XLSX) | open — browser |
| R-08 | `mapel` | Regulation on the curriculum structure (Kurikulum Merdeka / its successor) with subject lists per level and phase | `kurikulum.kemendikdasmen.go.id` (blocked), `jdih.kemendikdasmen.go.id` | open — browser |
| R-09 | `perguruan-tinggi` | List of higher-education institutions: code, name, type, status, province | `pddikti.kemdiktisaintek.go.id` (blocked from the cloud) — its download/search pages | open — browser |
| R-10 | `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` | World Athletics Competition and Technical Rules (current edition, PDF), scoring tables for combined events; PASI rules for age groups; O2SN/POPNAS technical handbooks (juknis) for athletics | `worldathletics.org` (reachable), PASI site, Puspresnas/Kemenpora pages | open |
| R-11 | `atletik-rekor` | Current national records (senior, U-20, U-18) and the championships the user runs | PASI announcements; organisers' result books | open — needs the user's list of championships |

When a brief is delivered, the converting session updates its status here and the set in `data/README.md`.
