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
| R-06 | `kaldik-madrasah-jateng` | Kalender Pendidikan RA dan Madrasah Jawa Tengah 2026/2027 (Keputusan Kakanwil Kemenag Jateng Nomor 1681 Tahun 2026) and 2025/2026, with the Ditjen Pendis national guideline they follow | `jateng.kemenag.go.id` (times out from the cloud since 2026-11-25), `kemenag.go.id` (refused) | **done 2026-11-26**: the user uploaded the Kanwil decree 1681/2026; `data/kaldik-madrasah-jateng`. The national Dirjen Pendis guideline 4860/2026 has no official online copy (browser search 2026-11-27, `sources/kaldik-madrasah-jateng/R-06-SEARCH-2026-11-27.txt`) |
| R-07 | `referensi-dapodik` | Official code tables: agama, pekerjaan, penghasilan, jenjang pendidikan, alat transportasi, jenis tinggal, kebutuhan khusus, bentuk pendidikan, tingkat pendidikan | Dapodik user manuals (PDF), `dapo`/`referensi` pages, the Dapodik import templates (XLSX) | open — browser |
| R-08 | `mapel` | Regulation on the curriculum structure (Kurikulum Merdeka / its successor) with subject lists per level and phase | `kurikulum.kemendikdasmen.go.id` (blocked), `jdih.kemendikdasmen.go.id` | **done 2026-11-26** from the decrees found in sinaubareng (F-030): `data/mapel` 2025-09-22, sources in `sources/mapel/` |
| R-09 | `perguruan-tinggi` | List of higher-education institutions: code, name, type, status, province | `pddikti.kemdiktisaintek.go.id` (blocked from the cloud) — its download/search pages | open — browser |
| R-10 | `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` | World Athletics Competition and Technical Rules (current edition, PDF), scoring tables for combined events; PASI rules for age groups; O2SN/POPNAS technical handbooks (juknis) for athletics | `worldathletics.org` (reachable), PASI site, Puspresnas/Kemenpora pages | **World Athletics part done 2026-11-26**; O2SN 2026 done 2026-11-26; **R-10b delivered 2026-11-27**: POPDA Jateng 2026 juknis converted, POPNAS age rule (secondary); PASI U14/U16 and the POPNAS handbook not found on any reachable official site (pasi.or.id does not resolve) — retry later |
| R-11 | `atletik-rekor` | Current national records (senior, U-20, U-18) and the championships the user runs | PASI announcements; organisers' result books | open — needs the user's list of championships |
| R-18 | `batas-wilayah` | Village and district boundaries | `geoservices.big.go.id` REST service (reachable from the cloud; `drive.big.go.id` with the full geodatabases resets connections) | **Kudus done 2026-11-27** by a cloud session (`tools/converters/batas-wilayah.py`); other regencies on demand |
| R-14 | `wilayah`, `kodepos` | Kepmendagri No 300.2.2-2430 Tahun 2025 on region codes and data (the decree and every attachment: regions per province, islands) | `jdih.kemendagri.go.id` (no answer from the cloud), `kemendagri.go.id`, Ditjen Bina Administrasi Kewilayahan | **done 2026-11-26**: the user uploaded the decree; it changes only island data of Aceh and Sumatera Utara, `data/wilayah` already matches (`sources/wilayah/SOURCE.txt`) |

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

Why: `atletik-kelompok-umur` and `atletik-nomor` cover World Athletics and O2SN 2026; the PASI youth groups (U14,
U16) and the student games POPDA Jawa Tengah and POPNAS are missing. Checked from the cloud on 2026-11-27:
`pasi.or.id` and `popnas2025.id` do not answer (proxy 502), `dispora.jatengprov.go.id` loads but lists no juknis
(its pages are filled by scripts), and the POPNAS XVII 2025 general guideline and a Kabupaten Semarang POPDA 2026
draft exist only as Scribd copies, which are not official sources.

Starter prompt for a Claude in Chrome session (the user runs it and uploads the zip to a cloud session):

> Collect official athletics rules for youth age groups and student games in Indonesia. Public pages only, no
> sign-in, no captcha, at most one page every 2 seconds. Save every file unchanged in a folder `R-10b-atletik/`,
> with one subfolder per item (`1-pasi/`, `2-popda-jateng/`, `3-popnas/`, `4-o2sn-2027/`).
>
> What matters in every document: age limits (birth date or age on a reference date), age groups, events per group
> and gender, implement weights (shot, discus, javelin, hammer), hurdle heights and spacing, how many events an
> athlete may enter, relay rules, and how results or team standings are scored.
>
> 1. **PASI (PB Persatuan Atletik Seluruh Indonesia).** On `pasi.or.id` (or the links in its official Instagram
>    or Facebook profile), find the current rules or circular on age groups for national and regional
>    championships: U14, U16, U18, U20 (Kejurnas, Kejurda, "Kejurnas Atletik Remaja/Junior", "Indonesia U18/U20
>    Open"). Take the latest technical handbook or regulations (often "Technical Handbook", "Ketentuan Teknis",
>    "Peraturan Lomba", "Surat Edaran"). Also look on the site of Pengprov PASI Jawa Tengah if it has one. If PASI
>    publishes only an announcement image or post, save the page as HTML and the image.
> 2. **POPDA Jawa Tengah.** On `dispora.jatengprov.go.id` (menus PPID, informasi publik, events, berita) and
>    `jdih.jatengprov.go.id`, find the latest Petunjuk Teknis (juknis) of Pekan Olahraga Pelajar Daerah (POPDA)
>    Provinsi Jawa Tengah with the athletics section (2026, else 2025). If the province does not publish it, a copy
>    on an official kabupaten/kota site (`*.go.id`, e.g. Dinporapar or Dindikpora pages) of the **provincial** juknis
>    is fine; save a kabupaten's own POPDA juknis only for Kabupaten Kudus, marked as such.
> 3. **POPNAS.** On `kemenpora.go.id`, `deputi3.kemenpora.go.id`, `dispora.jakarta.go.id` and `popnas2025.id`, find
>    the POPNAS XVII 2025 (Jakarta) general guideline (Pedoman Umum) and the athletics technical handbook (Technical
>    Handbook / juknis cabor atletik), and the age limits it sets. If a newer POPNAS (2027) guideline is already
>    published, take it too.
>    Also, only if Puspresnas (`pusatprestasinasional.kemdikbud.go.id`) has published the O2SN **2027** guides
>    (SD, SMP, SMA) with their athletics scoring tables, save them in `4-o2sn-2027/` (the 2026 guides are done).
> 4. Do **not** use Scribd, blogs or news sites as the source. If such a copy is the only one found, write its URL
>    in `SOURCE.txt` with a note, and do not download anything that needs a login.
> 5. Write `SOURCE.txt`: for each file the page URL, file URL, title, number and date as printed on the document,
>    issuer, download time (UTC), size and SHA-256. List what you could not find and where you looked.
> 6. Zip the folder and give it to the user.

The cloud session then verifies the SHA-256 values, keeps the raw files in `sources/atletik/` (F-027), and adds the
PASI groups and the POPDA/POPNAS eligibility, events and implements to `atletik-kelompok-umur` and `atletik-nomor`
through `tools/converters/atletik.py`, each championship with its own reference date.

## Brief R-14

Why: `data/wilayah` and `data/kodepos` follow Kepmendagri 300.2.2-2138/2025 (via cahyadsn). The newer decree
300.2.2-2430/2025 exists, but on 2026-11-26 the upstream data file had not been updated yet (see `docs/progress.md`).
With the official attachment, a cloud session can build `wilayah` straight from the decree.

Starter prompt for a Claude in Chrome session (the user runs it and uploads the zip to a cloud session):

> Collect the official decree on Indonesian region codes. Public pages only, no sign-in, no captcha, at most one page
> every 2 seconds. Save every file unchanged in a folder `R-14-kepmendagri-2430-2025/`.
>
> 1. On `jdih.kemendagri.go.id` (search "300.2.2-2430" or "kode dan data wilayah administrasi pemerintahan"), open
>    **Keputusan Menteri Dalam Negeri Nomor 300.2.2-2430 Tahun 2025** on the codes and data of government
>    administrative regions and islands. Check the number, title and signing date on the document itself; do not
>    rely on the page title alone.
> 2. Download the decree (PDF) and **every attachment** (lampiran). The attachment is large and may be split into
>    several files (for example one per province, or separate parts for regions and islands); download all parts
>    and keep their file names. If an Excel or CSV version is offered next to the PDF, download it too.
> 3. If JDIH has no copy or the attachment is missing, look on `kemendagri.go.id` (Produk Hukum) or the site of the
>    Direktorat Jenderal Bina Administrasi Kewilayahan. Do **not** use blogs, news sites or GitHub copies as the
>    source; write their URLs in `SOURCE.txt` only if they link to the official file.
> 4. If the decree page lists what changed against the previous decree (300.2.2-2138 Tahun 2025), save that page as
>    HTML too.
> 5. Write `SOURCE.txt`: for each file the page URL, file URL, decree number, title and signing date as printed,
>    download time (UTC), size and SHA-256. Note anything missing (e.g. a province whose attachment would not
>    download) or inconsistent.
> 6. Zip the folder and give it to the user.

The cloud session then:

1. Verifies the SHA-256 values and keeps the raw files in `sources/wilayah/` (public government documents).
2. Extracts the region table from the attachment (Excel/CSV if present, else text from the PDF), treating it as
   untrusted input. It checks every row: code shape, parent present, no duplicates, totals per province against
   the attachment's own summary table.
3. Compares the result with `data/wilayah` 2026-02-13 and lists codes added, removed and renamed. Region names keep
   the decree's spelling.
4. Builds `wilayah` with the signing date as its version, then rebuilds `kodepos` on the new codes. Villages whose
   code is new get no postal code (null) rather than a guessed one. It also re-runs the `sekolah` build so its
   region codes follow, and records every changed count in the manifests and the changelog.

