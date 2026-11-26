# Data audit: arumiforge/sinaubareng (2026-11-26)

Scope: the education and curriculum data of the SIGRAK app (`docs/data/`, `docs/sources/`, commit `6238a6b`),
checked for what belongs in Fondasi as shared public reference data (F-003). Outcome recorded in F-030.

## Taken into Fondasi

| What | sinaubareng | Fondasi | Status |
| --- | --- | --- | --- |
| Curriculum structure regulations (Permendikbudristek 12/2024, Permendikdasmen 13/2025, KMA 1503/2025) | `docs/sources/`; SD/MI JP tables structured in `docs/data/regulations/curriculum-structure-permendikdasmen-13-2025.json`, MI tables in `docs/data/curriculum/mi-allocation-kma-1503-2025.json` | `sources/mapel/` → set `mapel` (R-08), all levels | sources copied; set to build |
| Capaian Pembelajaran (Kepka BSKAP 046/H/KR/2025, Kepka BKPDM 020/2026, SK Dirjen Pendis 9941/2025) | `docs/sources/`; SD religion CP and MI Kemenag CP structured in `docs/data/curriculum/cp-*.json` | `sources/capaian-pembelajaran/` → set `capaian-pembelajaran` (R-15) | sources copied; set to build |
| TKA framework (Perka BSKAP 047/H/AN/2025, Kepmendikdasmen 56/2026) | `docs/sources/`; SD part in `docs/data/tka/kerangka-tka-sd.json` | `sources/kerangka-tka/` → set `kerangka-tka` (R-16) | sources copied; set to build |
| School coordinates | `docs/data/schools/{pati,kudus,jepara}.json` (latitude/longitude from referensi.data NPSN pages, `scripts/school-directory/fetch.cjs`) | `sekolah`, new fields for every unit (R-17) | planned (crawl under F-029) |

sinaubareng's structured files are used as a cross-check when Fondasi builds the sets from the PDFs. Its own checks
are useful: the SD/MI tables were compared cell by cell with page images and row sums, and its open points list
source errors (e.g. Tabel 20 SDLB kelas VI prints 54 where 64 makes the totals add up).

## Already in Fondasi, checked

- National holidays 2026/2027 (`docs/data/calendar/national-holidays-2026-2027.json`): all 30 days and kinds match
  `libur-nasional`.
- Jawa Tengah calendar 2026/2027 (`region-jawa-tengah-2026-2027.json`): same source PDF as `kaldik-jateng` (identical
  SHA-256). Its D-323 reading (Maulid on 25 August by the SKB, semester-1 break to 1 January) agrees with
  `kaldik-jateng`, which records the provincial 5 September date and the SKB date with "the national date wins".
- School lists of Pati, Kudus, Jepara: a subset of `sekolah` (except the coordinates above).

## Left in the app

SIGRAK's own curated content is app data, not public reference data: the R1 topics, TP, ATP and fokus
(`sigrak-*.json`), the legacy crosswalk, the subject catalogue with SIGRAK codes and teacher defaults
(`subjects.json`), catalogs (form options, extracurriculars, kokurikuler themes, inventory, administration
components), the taxonomy facets, level profiles, and the regulation digests in `docs/data/regulations/` (summaries
written for the app's content engine). Apps that need these keep them; if a second app needs one, it is
re-evaluated for Fondasi.

## Findings for the app repository

- **Personal data in a public repository**: `docs/sources/Contoh_SK_Pembagian_Tugas_SD_Semester_Genap_2025_2026.pdf`
  holds a real teacher's name and NIP, and the repository is public. The user makes the repository private
  (2026-11-26). Removing the file from history is a separate decision of the app.
- Other sources that are not public government documents (supervision instruments, legacy app documentation,
  owner notes, `usulan-01`) were not taken.
