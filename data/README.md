# Data catalogue

Public reference data shared by every Arumi Studios app (F-003, F-007). No personal data, ever.
How it works and how apps copy it: [../docs/data.md](../docs/data.md). Fetch briefs for sources this
environment cannot reach: [../docs/data-requests.md](../docs/data-requests.md).

| Set | Content | Version | Status | Source |
| --- | --- | --- | --- | --- |
| `wilayah` | 38 provinces, 514 regencies/cities, 7,285 districts, 83,762 villages: `[code, name]` | 2026-02-13 | ready | Kepmendagri 300.2.2-2138/2025 via cahyadsn/wilayah (MIT) |
| `sekolah` | Active schools per province (Dikdas + Dikmen): NPSN, name, form, public/private, address, village…province, Kemendagri region codes (97.8 % to the village) | 2026-11-26 | ready for SD, MI, SMP, MTs, SMA, MA, SMK, SLB, SPK, PDF/SPM (283,421); PAUD + PKBM/SKB next (F-028) | Kemendikdasmen Dapodik reference pages |
| `skema-siswa` | Student data schema for SMP/MTs: 61 fields in 5 groups, types, validation, conditions, edit units, 17 option lists | 2026-11-25 | ready | Arumi Studios ([school-data.md](../docs/school-data.md)) |
| `tahun-ajaran` | Year format, semesters, grades per level, curriculum phases | 2026-11-25 | ready | rules |
| `sekolah` (PAUD, NSM) | + TK, KB, RA, TPA, SPS, PKBM, SKB; NSM of madrasah | — | planned (R-01 part 2, R-02) | Dapodik (reachable here), EMIS (browser) |
| `kodepos` | Postal code per village code (83,762 villages, 10,632 codes): `[code, postal_code]` | 2025-06-30 | ready | cahyadsn/wilayah_kodepos (MIT), Kepmendagri 300.2.2-2138/2025 codes |
| `libur-nasional` | National holidays and cuti bersama, one row per day: 2026 (17 + 8 days), 2027 (18 + 8 days) | 2026-09-15 | ready (2028 when signed, ~Sept 2027) | SKB 3 Menteri (Kemenko PMK) |
| `kaldik-jateng` | Education calendar of Jawa Tengah: 2026/2027 in full (events per level and 5/6 school days, rules), 2025/2026 key dates | 2026-09-15 | ready (2027/2028 not yet published); holidays checked against `libur-nasional` | Dinas Pendidikan Prov. Jawa Tengah |
| `kalender-nasional` | National education calendar (Kemendikdasmen; Kemenag for madrasah) per academic year | — | planned (R-12) | Kemendikdasmen, Kemenag (browser) |
| `kaldik-madrasah-jateng` | Madrasah calendar of Jawa Tengah per academic year (incl. Ramadan days) | — | planned (R-06) | Kanwil Kemenag Jawa Tengah |
| `referensi-dapodik` | Religion, occupation, income, education, transport, residence, special needs, levels/grades — with official codes | — | planned (R-07) | Dapodik reference tables (browser) |
| `mapel` | Kurikulum Merdeka subjects per level/phase | — | planned (R-08) | Kemendikdasmen regulation on curriculum structure (browser) |
| `perguruan-tinggi` | Higher-education institutions: code, name, type, status, province | — | planned (R-09) | PDDikti (browser) |
| `atletik-nomor` | 40 events: code, label, result unit, wind; hurdles, steeplechase, implements per category, combined events | 2026-03-20 | ready for WA; U14/U16 and school events pending (R-10b) | World Athletics rules (F-027) |
| `atletik-kelompok-umur` | U18, U20, Senior, Master with reference-date rules | 2026-03-20 | partial: school/PASI groups pending (R-10b) | World Athletics rules; PASI, Puspresnas (browser) |
| `atletik-hasil` | Result codes, rounding (time, distance, wind), ties, combined-events formula + parameters (checked) | 2026-03-20 | ready | World Athletics rules, scoring tables (F-027) |
| `atletik-rekor` | National/regional/championship records per event and age group | — | planned (R-11) | PASI and championship organisers (manual) |

SPMB's form lists (occupation, income) stay in SPMB until `referensi-dapodik` has verified codes.
