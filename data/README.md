# Data catalogue

Public reference data shared by every Arumi Studios app (F-003, F-007). No personal data, ever.
How it works and how apps copy it: [../docs/data.md](../docs/data.md). Fetch briefs for sources this
environment cannot reach: [../docs/data-requests.md](../docs/data-requests.md).

| Set | Content | Version | Status | Source |
| --- | --- | --- | --- | --- |
| `wilayah` | 38 provinces, 514 regencies/cities, 7,285 districts, 83,762 villages: `[code, name]` | 2026-02-13 | ready; matches Kepmendagri 300.2.2-2430/2025 (it changes islands only) | Kepmendagri 300.2.2-2138/2025 via cahyadsn/wilayah (MIT) |
| `sekolah` | Active education units per province: NPSN, name, form, public/private, address, village…province, Kemendagri region codes (98.0 % to the village) | 2026-11-26 | ready (539,580): SD, MI, SMP, MTs, SMA, MA, SMK, SLB, SPK, PDF/SPM; TK, KB, RA, TPA, SPS, PAUDQ; PKBM, SKB (F-028) | Kemendikdasmen Dapodik reference pages |
| `skema-siswa` | Student data schema for SMP/MTs: 61 fields in 5 groups, types, validation, conditions, edit units, 17 option lists | 2026-11-25 | ready | Arumi Studios ([school-data.md](../docs/school-data.md)) |
| `tahun-ajaran` | Year format, semesters, grades per level, curriculum phases | 2026-11-25 | ready | rules |
| `sekolah` (NSM) | + NSM of madrasah and RA | — | planned (R-02) | EMIS (browser) |
| `sekolah` (coordinates) | + latitude/longitude per unit | — | planned (R-17, F-030) | referensi.data NPSN pages (crawl, F-029) |
| `kodepos` | Postal code per village code (83,762 villages, 10,632 codes): `[code, postal_code]` | 2025-06-30 | ready | cahyadsn/wilayah_kodepos (MIT), Kepmendagri 300.2.2-2138/2025 codes |
| `libur-nasional` | National holidays and cuti bersama, one row per day: 2026 (17 + 8 days), 2027 (18 + 8 days) | 2026-09-15 | ready (2028 when signed, ~Sept 2027) | SKB 3 Menteri (Kemenko PMK) |
| `kaldik-jateng` | Education calendar of Jawa Tengah: 2026/2027 in full (events per level and 5/6 school days, rules), 2025/2026 key dates | 2026-09-15 | ready (2027/2028 not yet published); holidays checked against `libur-nasional` | Dinas Pendidikan Prov. Jawa Tengah |
| `kalender-nasional` | National education calendar (Kemendikdasmen; Kemenag for madrasah) per academic year | — | planned (R-12) | Kemendikdasmen, Kemenag (browser) |
| `kaldik-madrasah-jateng` | Madrasah calendar of Jawa Tengah (RA, MI, MTs, MA, MAK): 2026/2027 in full, 45 events, rules, HK/HL/HE per month | 2026-06-29 | ready for 2026/2027; holidays checked against `libur-nasional` | Keputusan Kakanwil Kemenag Jateng 1681/2026 |
| `referensi-dapodik` | Religion, occupation, income, education, transport, residence, special needs, levels/grades — with official codes | — | planned (R-07) | Dapodik reference tables (browser) |
| `mapel` | Subjects and JP per year (intrakurikuler, kokurikuler) per level and grade: SD, SMP, SMA, SMK, SDLB, SMPLB, SMALB, Paket A/B/C (SKK), madrasah MI, MTs, MA, MAK, MILB, MTsLB, MALB; electives, phases, footnotes, rules, errata | 2025-09-22 | ready (54 tables, 144 printed totals checked; F-031 errata) | Permendikdasmen 13/2025, Permendikbudristek 12/2024 Pasal 33, KMA 1503/2025 |
| `capaian-pembelajaran` | Capaian Pembelajaran per subject and phase, all levels: PAUD, general subjects, religion (six religions, SD–SMA/SMK), SMK programmes, kesetaraan, special education, madrasah subjects (RA–MA, MAPK); rasional, tujuan, karakteristik, elements, CP per phase and element; 299 subjects, 2,624 outcomes | 2026-06-11 | ready except the special-education religion CP (020 Lampiran II, next step, F-032) | Kepka BSKAP 046/H/KR/2025, SK Dirjen Pendis 9941/2025, Kepka BKPDM 020/2026 |
| `kerangka-tka` | TKA framework SD/MI and SMP/MTs: subjects, content, competencies, item types, durations, score categories | — | planned (R-16, F-030); sources in `sources/kerangka-tka/` | Perka BSKAP 047/H/AN/2025, Kepmendikdasmen 56/2026 |
| `perguruan-tinggi` | Higher-education institutions: code, name, type, status, province | — | planned (R-09) | PDDikti (browser) |
| `atletik-nomor` | 44 events: code, label, result unit, wind; hurdles, steeplechase, implements per category, combined events; O2SN 2026 per level (events, implements, trials, Kids' Athletics courses, qualifying marks) | 2026-11-26 | ready for WA and O2SN 2026; PASI U14/U16, POPDA/POPNAS pending (R-10b) | World Athletics rules; Puspresnas O2SN guides (F-027) |
| `atletik-kelompok-umur` | U18, U20, Senior, Master with reference-date rules; O2SN 2026 SD/SMP/SMA (birth date limit, grades) | 2026-11-26 | partial: PASI U14/U16, POPDA/POPNAS pending (R-10b) | World Athletics rules; Puspresnas O2SN guides |
| `atletik-hasil` | Result codes, rounding (time, distance, wind), ties, combined-events formula + parameters (checked); O2SN Trilomba/Pancalomba scoring (17,595 table rows checked) | 2026-11-26 | ready | World Athletics rules, scoring tables; O2SN scoring tables (F-027) |
| `atletik-rekor` | National/regional/championship records per event and age group | — | planned (R-11) | PASI and championship organisers (manual) |

SPMB's form lists (occupation, income) stay in SPMB until `referensi-dapodik` has verified codes.
