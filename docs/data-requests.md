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
| R-01 | `sekolah` (all levels) | Every school per district with NPSN, name, level, status, address, village, coordinates if shown | `referensi.data.kemendikdasmen.go.id` and `dapo.kemendikdasmen.go.id` are reachable from cloud sessions: **done by a cloud session**, not the browser | **done 2026-11-26** by a cloud session (539,580 units: Dikdas, Dikmen, PAUD, PKBM/SKB) |
| R-02 | `sekolah` (MTs, MA; MI refresh) | Madrasah list per province: NSM, NPSN, name, level, status, address, village/district/regency | EMIS Kemenag public pages (`emis.kemenag.go.id` is blocked from the cloud), or the Kanwil/Kemenag open-data downloads | open — browser |
| R-03 | `kodepos` | Postal code list per village with region codes, and its licence | `github.com/cahyadsn` (wilayah postal-code repository) — reachable from the cloud; licence check first | **done 2026-11-25** by a cloud session (MIT; all 83,762 villages) |
| R-04 | `libur-nasional` | SKB 3 Menteri on national holidays and cuti bersama for 2026, 2027 and 2028 (when signed): the PDF and the announcement page | `kemenkopmk.go.id` (reachable from the cloud), `jdih` pages of the ministries | **done 2026-11-25** by a cloud session (2026, 2027; 2028 not yet signed) |
| R-05 | `kaldik-jateng` | Kalender Pendidikan Jawa Tengah 2025/2026, 2026/2027 (and 2027/2028 when out): PDF/image + the SK | `disdikbud.jatengprov.go.id` (blocked from the cloud) | **done 2026-11-25** (2025/2026, 2026/2027; the site moved to pdk.jatengprov.go.id) |
| R-12 | `kalender-nasional` | The national education calendar for 2026/2027 (and 2027/2028 when out) if Kemendikdasmen publishes one — regulation/circular + its attachment; the Kemenag madrasah calendar guideline for the same years(the SKB 2026 and 2027 are done in R-04) | `kemendikdasmen.go.id`, `jdih.kemendikdasmen.go.id`, `kemenag.go.id`, `kemenkopmk.go.id` | open — browser |
| R-13 | `kaldik-kabupaten` (on demand) | A kabupaten/kota calendar for SD/SMP when an app needs it, starting with the first client's district (Kabupaten Kudus) | the Dinas Pendidikan of that kabupaten/kota | optional |
| R-06 | `kaldik-madrasah-jateng` | Kalender Pendidikan RA dan Madrasah Jawa Tengah 2026/2027 (Keputusan Kakanwil Kemenag Jateng Nomor 1681 Tahun 2026) and 2025/2026, with the Ditjen Pendis national guideline they follow | `jateng.kemenag.go.id` (times out from the cloud since 2026-11-25), `kemenag.go.id` (refused) | open — browser, [brief below](#brief-r-06) |
| R-07 | `referensi-dapodik` | Official code tables: agama, pekerjaan, penghasilan, jenjang pendidikan, alat transportasi, jenis tinggal, kebutuhan khusus, bentuk pendidikan, tingkat pendidikan | Dapodik user manuals (PDF), `dapo`/`referensi` pages, the Dapodik import templates (XLSX) | open — browser |
| R-08 | `mapel` | Regulation on the curriculum structure (Kurikulum Merdeka / its successor) with subject lists per level and phase | `kurikulum.kemendikdasmen.go.id` (blocked), `jdih.kemendikdasmen.go.id` | open — browser |
| R-09 | `perguruan-tinggi` | List of higher-education institutions: code, name, type, status, province | `pddikti.kemdiktisaintek.go.id` (blocked from the cloud) — its download/search pages | open — browser |
| R-10 | `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` | World Athletics Competition and Technical Rules (current edition, PDF), scoring tables for combined events; PASI rules for age groups; O2SN/POPNAS technical handbooks (juknis) for athletics | `worldathletics.org` (reachable), PASI site, Puspresnas/Kemenpora pages | **World Athletics part done 2026-11-26**; PASI/O2SN/POPNAS part → R-10b |
| R-11 | `atletik-rekor` | Current national records (senior, U-20, U-18) and the championships the user runs | PASI announcements; organisers' result books | open — needs the user's list of championships |

When a brief is delivered, the converting session updates its status here and the set in `data/README.md`.

## Brief R-06

Starter prompt for a Claude in Chrome session (the user runs it and uploads the zip to a cloud session):

> Collect the official education calendar of RA and madrasah in Jawa Tengah. Public pages only, no sign-in, at most
> one page every 2 seconds. Save every file unchanged in a folder `R-06-kaldik-madrasah-jateng/`.
>
> 1. On `jateng.kemenag.go.id` (search "kalender pendidikan" or "kaldik"), find the Keputusan Kepala Kantor Wilayah
>    Kementerian Agama Provinsi Jawa Tengah **Nomor 1681 Tahun 2026** tentang Pedoman Kalender Pendidikan Madrasah
>    Tahun Ajaran 2026/2027, with its lampiran (calendar per month, list of activities). Download the PDF (and the
>    Excel attachment if the Kanwil publishes one).
> 2. Do the same for 2025/2026 if it is still published.
> 3. On `kemenag.go.id` or `pendis.kemenag.go.id`, find the national guideline these follow: Keputusan Direktur
>    Jenderal Pendidikan Islam on the Kalender Pendidikan Madrasah Tahun Ajaran 2026/2027 (news sites cite Nomor 4860
>    Tahun 2026; check the number on the document). Download the PDF.
> 4. Only if the Kanwil site has no copy: a copy published by a Kemenag kabupaten/kota office (`*.kemenag.go.id`) is
>    fine. Do **not** use blogs or teacher sites (ayomadrasah, websiteedukasi, …) as the source; note their URLs only
>    if they point to the official file.
> 5. Write `SOURCE.txt`: for each file the page URL, file URL, decree number and signing date as printed, download
>    time (UTC), size and SHA-256. Note anything missing or inconsistent.
> 6. Zip the folder and give it to the user.

The cloud session then transcribes the lampiran into `data/kaldik-madrasah-jateng/` in the same shape as
`kaldik-jateng` (events per level RA/MI/MTs/MA/MAK, `estimate`, `ref`, `skb` check against `libur-nasional`).

## Brief R-10b

Starter prompt for a Claude in Chrome session (public pages only, at most one page every 2 seconds, files unchanged
in `R-10b-atletik/` with `SOURCE.txt`: page URL, file URL, title and date as printed, download time, size, SHA-256):

> 1. PASI (`pasi.or.id` or its official social links): the current rules or circular on age groups (U14, U16, U18,
>    U20) for Kejurnas/Kejurda, with implement weights, hurdle heights and events per group.
> 2. Puspresnas (`pusatprestasinasional.kemendikdasmen.go.id` or the ministry's site): the latest O2SN technical
>    handbooks (juknis) for athletics at SD, SMP and SMA level: events, age limits and reference dates, implements.
> 3. Kemenpora / Dispora Jawa Tengah: the latest POPNAS and POPDA Jawa Tengah technical handbooks for athletics.
> 4. Zip the folder and give it to the user.

