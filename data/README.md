# Data catalogue

Public reference data shared by every Arumi Studios app (F-003, F-007). No personal data, ever.
How it works and how apps copy it: [../docs/data.md](../docs/data.md). Fetch briefs for sources this
environment cannot reach: [../docs/data-requests.md](../docs/data-requests.md).

| Set | Content | Version | Status | Source |
| --- | --- | --- | --- | --- |
| `wilayah` | 38 provinces, 514 regencies/cities, 7,285 districts, 83,762 villages: `[code, name]` | 2026-02-13 | ready | Kepmendagri 300.2.2-2138/2025 via cahyadsn/wilayah (MIT) |
| `sekolah` | Schools per province: NPSN, name, level, public/private, village…province | 2026-11-18 | **partial**: SD + MI (177,422) | Dapodik, EMIS (compiled) |
| `skema-siswa` | Student data schema for SMP/MTs: 61 fields in 5 groups, types, validation, conditions, edit units, 17 option lists | 2026-11-25 | ready | Arumi Studios ([school-data.md](../docs/school-data.md)) |
| `tahun-ajaran` | Year format, semesters, grades per level, curriculum phases | 2026-11-25 | ready | rules |
| `sekolah` (all levels) | + SMP, MTs, SMA, MA, SMK, SLB; region codes linking to `wilayah`; address | — | planned (R-01, R-02) | Dapodik (reachable here), EMIS (browser) |
| `kodepos` | Postal code per village code | — | planned (R-03) | cahyadsn wilayah postal list (check licence) |
| `libur-nasional` | National holidays and cuti bersama per year, 2026–2028 | — | planned (R-04) | SKB 3 Menteri (Kemenko PMK) |
| `kaldik-jateng` | Education calendar of Jawa Tengah: 2026/2027 in full (events per level and 5/6 school days, rules), 2025/2026 key dates | 2026-05-29 | ready (2027/2028 not yet published) | Dinas Pendidikan Prov. Jawa Tengah |
| `kalender-nasional` | National education calendar (Kemendikdasmen; Kemenag for madrasah) per academic year | — | planned (R-12) | Kemendikdasmen, Kemenag (browser) |
| `kaldik-madrasah-jateng` | Madrasah calendar of Jawa Tengah per academic year (incl. Ramadan days) | — | planned (R-06) | Kanwil Kemenag Jawa Tengah |
| `referensi-dapodik` | Religion, occupation, income, education, transport, residence, special needs, levels/grades — with official codes | — | planned (R-07) | Dapodik reference tables (browser) |
| `mapel` | Kurikulum Merdeka subjects per level/phase | — | planned (R-08) | Kemendikdasmen regulation on curriculum structure (browser) |
| `perguruan-tinggi` | Higher-education institutions: code, name, type, status, province | — | planned (R-09) | PDDikti (browser) |
| `atletik-nomor` | Events: code, discipline, track/field, result unit, wind rule, implements per age group | — | planned (R-10) | World Athletics rules, PASI |
| `atletik-kelompok-umur` | School age groups (SD/SMP/SMA, U-14…U-20) and age reference date rules | — | planned (R-10) | PASI, Kemenpora/Puspresnas (O2SN, POPNAS) |
| `atletik-hasil` | Result format and rounding, DNS/DNF/DQ/NM, ranking ties, combined-events points tables | — | planned (R-10) | World Athletics Competition Rules, scoring tables |
| `atletik-rekor` | National/regional/championship records per event and age group | — | planned (R-11) | PASI and championship organisers (manual) |

SPMB's form lists (occupation, income) stay in SPMB until `referensi-dapodik` has verified codes.
