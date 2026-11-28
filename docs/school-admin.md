# School administration feature catalog (F-040)

A map of the administration work that schools already do, and that can be done digitally, for every Arumi Studios
app that serves schools. Apps pick features from it. For each feature, the catalog says who uses it, how sensitive
its data is, which Fondasi rules and data sets apply, and which sources show the need. Fondasi holds the catalog and
the rules. The features are built in the apps (F-015).

## How the catalog is built

The catalog maps needs that already exist in schools. It does not invent features. Three kinds of sources feed it,
each recorded in the registers at the end of this page:

| Code | Source | What it shows | How it is collected |
| --- | --- | --- | --- |
| **Pr** | Online services and applications offered to schools | Which administration tasks schools pay for or use today | Public pages only: home, features, pricing, FAQ, terms. Never trial accounts, the inside of the app, its data or its code |
| **La** | Field observation in schools | How the task is done now (paper, Excel, WhatsApp, an app), who does it, how often, what goes wrong | Visits and talks with school staff, blank forms and templates; see "Field observation" |
| **Re** | Official documents that set the standard | What the task must contain, its format and its deadlines | Regulations, technical guidelines and official systems; their content goes into Fondasi data sets where it is reference data |

A feature with no source yet is marked **usulan**: it comes from experience and must be confirmed by observation or an
official document before an app relies on it. A feature becomes stronger as more sources confirm it; one product is
enough to list it, not to settle how it should work.

## How an app uses the catalog

1. When adopting Fondasi (`docs/adopting.md`) or planning a school app, go through the catalog with the user. Record in
   the app's own decisions (`D-…`) which features it builds, in which order, and any features it adds.
2. Before building a feature, read its row and the rules it points to. Then apply the app's own UI skill together with
   `fondasi-ui`, `fondasi-feedback` and `bahasa-indonesia-plain`.
3. If a feature proves useful in more than one app and is not listed yet, add it here (new ID, changelog line).

IDs (`ADM-01`…) stay stable: a removed feature keeps its ID, marked `dihapus`. Feature names are the Indonesian names
users see. Apps may word them their own way, but the meaning stays the same.

## Legend

**Sensitivity** of the data the feature holds:

| Level | Meaning | Rules |
| --- | --- | --- |
| **R** (rendah) | No personal data, or only names and roles that staff already see | `web-baseline.md` |
| **P** (pribadi) | Personal data of students, parents or staff | `web-baseline.md` §3–5, `school-data.md` |
| **S** (spesifik) | Specific personal data under UU PDP (health, biometrics, religion, special needs, counselling, finances of a family) or children's records that can harm them | `school-data.md` in full: group permissions, audit of views, encryption at rest, retention |

**Priority** for a new school app: **Inti** (the core most schools ask for first), **Lanjutan** (after the core
works), **Tambahan** (useful, but less urgent).

**Basis**: the sources that show the need, with their register entries (for example `Pr P-01`, `La O-03`, `Re`
with the data set or document). **usulan** = no source recorded yet.

**Roles** used below: kepala sekolah, wakil kepala sekolah (wakasek), guru, wali kelas, guru BK, guru piket, tenaga
kependidikan (TU), operator sekolah, bendahara, pembina ekstrakurikuler, petugas UKS, pustakawan, siswa, orang tua/wali.

## Catalog

### Data induk

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-01 | Data induk siswa | Student records, filled by staff or by parents, imported from Excel or a Dapodik export | operator, TU, wali kelas, orang tua | S | `skema-siswa`, `referensi-dapodik`, `ekspor-dapodik`, `wilayah`, `school-data.md` | Inti | Pr P-01; Re `referensi-dapodik` |
| ADM-02 | Data guru dan tenaga kependidikan | Staff records: identity, employment, education, assignments | operator, TU, kepala sekolah | P | `ekspor-dapodik` (PTK form); schema still missing (follow-up 1) | Inti | Pr P-01; Re `ekspor-dapodik` |
| ADM-03 | Kelas dan rombongan belajar | Classes, homeroom teachers, students per class per school year, moving up a grade | operator, wakasek | P | `tahun-ajaran`, `ekspor-dapodik` | Inti | Pr P-01; Re `ekspor-dapodik` |
| ADM-04 | Mutasi siswa | Students joining, leaving and transferring, with letters and the origin or destination school | operator, TU | P | `sekolah`, `referensi-dapodik` (jenis pendaftaran) | Tambahan | usulan |
| ADM-05 | Data alumni | Graduates and where they continue (school, university, work) | TU, BK | P | `sekolah`, `perguruan-tinggi` (planned, R-09) | Tambahan | usulan |
| ADM-06 | Profil sekolah | NPSN, address, accreditation, letterhead, logo, officials who sign | operator, kepala sekolah | R | `sekolah`, `wilayah`, `batas-wilayah` | Inti | usulan |

### Kurikulum dan pembelajaran

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-07 | Jadwal pelajaran | Timetable built automatically from teaching loads, rooms and teachers' constraints, then adjusted by hand | wakasek kurikulum, guru, siswa | R | `mapel` (lesson hours per week) | Inti | Pr P-01; Re `mapel` |
| ADM-08 | Jurnal mengajar | What was taught in each lesson, filled from the timetable, with student attendance for that lesson | guru, wakasek, kepala sekolah | P | `mapel`, `capaian-pembelajaran` | Inti | Pr P-01 |
| ADM-09 | Perangkat ajar | Help for teachers to write modul ajar, ATP, LKPD and assessments from the official learning outcomes; the teacher decides and edits; export to Word with letterhead | guru | R | `capaian-pembelajaran`, `mapel`, `ai-assistant.md` (if AI helps) | Lanjutan | Pr P-01; Re `capaian-pembelajaran` |
| ADM-10 | Ujian daring (CBT) | Question banks, scheduled tests, automatic marking of objective questions, import from Word | guru, siswa, proktor | P | `kerangka-tka`, `capaian-pembelajaran` | Lanjutan | Pr P-01 |
| ADM-11 | Nilai dan rapor | Grades per learning goal, report descriptions, report PDF with QR verification, export for the official e-Rapor | guru, wali kelas, kepala sekolah, orang tua | P | `mapel`, `capaian-pembelajaran`, `web-baseline.md` §11 | Lanjutan | Pr P-01 |
| ADM-12 | Kalender pendidikan | School calendar on top of the national and provincial layers: holidays, exams, report days, school events | wakasek, semua | R | `tahun-ajaran`, `libur-nasional`, `kaldik-jateng`, `kaldik-madrasah-jateng` | Inti | Re `kaldik-jateng`, `kaldik-madrasah-jateng` |
| ADM-13 | Supervisi dan kinerja guru | Classroom supervision schedules, observation notes, follow-up, teacher performance records | kepala sekolah, wakasek, guru | P | — | Tambahan | usulan |
| ADM-14 | Latihan soal untuk siswa | Public or class practice questions, no login needed for public sets | siswa | R | `kerangka-tka` (sample questions) | Tambahan | Pr P-01; Re `kerangka-tka` |

### Kesiswaan

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-15 | Presensi siswa | Daily and per-lesson attendance: by the teacher, by QR card, or by face recognition; recap per class and per month; notice to parents | guru, wali kelas, piket, orang tua | P, **S** with face recognition | `school-data.md`; see "Attendance with biometrics" | Inti | Pr P-01 |
| ADM-16 | Poin pelanggaran dan prestasi | Rule breaches and achievements as points, thresholds that trigger a warning letter or a call to parents | wali kelas, BK, wakasek kesiswaan, orang tua | S | `school-data.md` | Inti | Pr P-01 |
| ADM-17 | Pembiasaan karakter | Daily habits (for example the 7 Kebiasaan Anak Indonesia Hebat) filled or signed by parents, recap per class | orang tua, wali kelas | P | list of habits still missing (follow-up 4) | Inti | Pr P-01 |
| ADM-18 | Piket guru | Duty roster, duty log: late students, permits to leave, incidents | guru piket, wakasek | P | — | Lanjutan | Pr P-01 |
| ADM-19 | Ekstrakurikuler dan OSIS | Groups, members, schedules, attendance, grades for the report, certificates with QR | pembina, siswa | P | `web-baseline.md` §11 (QR) | Lanjutan | Pr P-01 |
| ADM-20 | Pemilihan OSIS | Candidates and voting for the student council, one vote per student, results after closing | siswa, pembina OSIS | P | `web-baseline.md` (permissions, audit log) | Tambahan | Pr P-01 |
| ADM-21 | Bimbingan konseling | Counselling notes, home visits, referrals, follow-up | guru BK | **S** | `school-data.md` in full; see "Counselling records" | Tambahan | usulan |
| ADM-22 | Kesehatan siswa (UKS) | Health screening, visits to the health room, allergies and emergency contacts | petugas UKS, wali kelas | **S** | `skema-siswa` (health group), `school-data.md` | Tambahan | usulan |
| ADM-23 | Prestasi dan lomba | Competitions entered, results, certificates, school achievements page | pembina, wakasek kesiswaan | P | `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil`, `atletik-rekor` | Tambahan | usulan |

### Tata usaha

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-24 | Surat masuk dan keluar | Letter register, automatic letter numbers, templates with letterhead, signature by the official, QR verification page, archive | TU, kepala sekolah | P | `web-baseline.md` §11 (A4/F4, QR); classification codes still missing (follow-up 3) | Inti | Pr P-01 |
| ADM-25 | Kepegawaian | Staff attendance, leave and permits, duty letters (SK and surat tugas), file of each staff member | TU, kepala sekolah, guru | P | `ekspor-dapodik` (PTK form) | Tambahan | usulan |
| ADM-26 | Sarana dan prasarana | Inventory of rooms and goods, condition checks, borrowing and repairs | TU, wakasek sarpras | R | — | Tambahan | usulan |
| ADM-27 | Perpustakaan | Catalogue, loans and returns, overdue notices, visit log | pustakawan, siswa, guru | P | — | Tambahan | usulan |
| ADM-28 | Rapat dan notulen | Meeting invitations, attendance, minutes, decisions and who follows them up | kepala sekolah, guru | R | — | Tambahan | usulan |

### Keuangan

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-29 | Kas dan laporan BOSP | Cash book, bank book, spending by component, BOSP reports with receipts attached | bendahara, kepala sekolah | R | components and codes still missing (follow-up 2); see "Money" | Lanjutan | Pr P-01 |
| ADM-30 | Tagihan siswa | Fees agreed by the school committee, bills per student, payments, receipts, reminders to parents | bendahara, orang tua | **S** | `school-data.md`; see "Money" | Lanjutan | Pr P-01 |
| ADM-31 | Tabungan siswa | Deposits and withdrawals per student, passbook print, parents can see the balance | bendahara, wali kelas, orang tua | **S** | `school-data.md`; see "Money" | Tambahan | Pr P-01 |
| ADM-32 | Gaji dan honor | Pay and honoraria for non-civil-servant staff, deductions, pay slips | bendahara, kepala sekolah | **S** | see "Money" | Lanjutan | Pr P-01 |

### Komunikasi

| ID | Fitur | What it does | Users | Data | Fondasi | Priority | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-33 | Portal orang tua | One place for parents: attendance, points, habits, grades, bills, announcements of their own child only | orang tua | P/S (by what it shows) | `school-data.md` (need to know), `web-baseline.md` | Inti | Pr P-01 |
| ADM-34 | Notifikasi WhatsApp | Messages to parents and staff from the other features | semua | P | `web-baseline.md`; see "Notifications" | Lanjutan | Pr P-01 |
| ADM-35 | Situs web sekolah | Public profile, news, agenda, achievements, contacts, required public pages | publik | R | `web-baseline.md` §10, `ui.md`, `visual-assets.md`, `guides.md` | Lanjutan | Pr P-01 |
| ADM-36 | Pengumuman | Announcements to classes, roles or everyone, read receipts | semua | R | `feedback.md` (banners) | Inti | usulan |
| ADM-37 | Penerimaan murid baru | Registration of new students | calon siswa, orang tua, panitia | S | the SPMB app | Inti (own app) | Re (SPMB app sources) |
| ADM-38 | Panduan dan bantuan | In-app guide per role, help assistant with handover to WhatsApp | semua | R | `guides.md`, `ai-assistant.md` | Inti | usulan |

## Rules for the sensitive features

### Attendance with biometrics (ADM-15)

- A face template is biometric data, which UU PDP treats as specific personal data. Use it only with the written
  agreement (`school-data.md`) and only for attendance. Students whose parents do not agree get another way (QR card,
  roll call by the teacher), and the app treats both the same.
- Keep the templates encrypted, on servers in Indonesia for public schools (`storage.md`). Never put them in exports,
  logs or AI prompts. Delete them when the student leaves or the agreement is withdrawn.
- Attendance must still work when the camera, the network or the recognition fails: a manual entry by the teacher,
  marked as manual.
- Photos taken at the scan are not kept after the match, unless the agreement says otherwise and for how long.

### Counselling records (ADM-21) and points (ADM-16)

- Counselling notes are visible to the counsellor who wrote them and to whom the agreement names. Homeroom teachers
  see that a case exists, not the notes. Every view is in the audit log.
- Points and warning letters can hurt a child. Wording follows `bahasa-indonesia-plain` (neutral, no labels on the
  child). Notices to parents state facts and the next step. Public lists of offenders are never shown.

### Grades and reports (ADM-11)

- An internal report tool does not replace the official e-Rapor or Dapodik. It exports in the form they accept, and
  the export is checked by a person before upload.
- Dapodik has no public API for third-party apps. Data moves through exports and imports that a person runs
  (`ekspor-dapodik`, F-038). Never store a school's export in Fondasi.

### Money (ADM-29–ADM-32)

- Transactions are never deleted or edited after closing. A correction is a new entry that points to the old one. The
  audit log records who entered and who approved.
- Every spending entry has its receipt as a file (`storage.md`). The BOSP report follows the official guideline in
  force for that year; the app shows which guideline version it uses.
- A family's bills, savings and aid are specific data: only the treasurer and the family see the details; homeroom
  teachers see at most "sudah/belum lunas" if the school decides so.

### Notifications (ADM-34)

- Messages say that something happened and link to the app after login. They do not carry grades, points, health,
  counselling, amounts owed, NIK or other sensitive content (`school-data.md`).
- Parents choose which notices they get. The app works fully without WhatsApp.

## Follow-ups in Fondasi

Gaps the catalog shows. Each one becomes its own PR, with a decision when it needs one:

1. **`skema-ptk`**: a schema for staff data like `skema-siswa`, based on the Dapodik PTK form (`ekspor-dapodik`)
   (ADM-02, ADM-25).
2. **BOSP components and codes**: from the official BOSP technical guideline (ADM-29).
3. **Archive classification codes** for letter numbers: from the official classification for the education
   ministry or the regional government (ADM-24).
4. **Character habits**: the 7 Kebiasaan Anak Indonesia Hebat with their indicators, from the ministry's official
   guideline (ADM-17).
5. **Assessment and report rules**: the parts of the official assessment guideline that a report tool needs, such as
   the report's sections and the description rules (ADM-11).

Official sources only. If a source is blocked from cloud sessions, it goes through a browser brief in
`data-requests.md`.

## Field observation

How to record what a school does today, so observations can be compared:

- One entry per visit or conversation in the register below: date, level and form (SD, SMP, MTs…), regency code from
  `wilayah`, the roles spoken to (wali kelas, operator, bendahara…), and the catalog IDs it concerns.
- For each task: how it is done now (paper book, Excel, WhatsApp group, an app), who does it, how often, how long it
  takes, what document comes out, who receives it, and what goes wrong.
- New tasks get a new ID in the catalog, first as **usulan** with this observation as their basis.
- No personal data in Fondasi: no names of staff, students or parents, no photos of filled forms, no school
  exports. Photos or copies of **blank** forms and templates may be kept in the app repository that needs them.
  The school's name may be noted only if the school agrees; otherwise the level and regency are enough.

## Source registers

### Pr — online services and applications

| ID | Service | Read | Pages read | Taken |
| --- | --- | --- | --- | --- |
| P-01 | SiTuntas (situntas.id), web app for school administration | 2026-11-28 | home, harga, syarat-ketentuan, tentang | Public list of modules and their purpose |

Add other services the same way (public pages only, date read). Comparing several services shows which tasks are
common and which are one vendor's idea.

### La — field observation

| ID | Date | Level, regency | Roles | Catalog IDs | Notes |
| --- | --- | --- | --- | --- | --- |
| — | | | | | none yet |

### Re — official documents

Already in Fondasi as data sets, with their sources in each `manifest.json`: `mapel`, `capaian-pembelajaran`,
`kerangka-tka`, `kaldik-jateng`, `kaldik-madrasah-jateng`, `tahun-ajaran`, `libur-nasional`, `referensi-dapodik`,
`ekspor-dapodik`. Still to find are the documents behind the follow-ups above (BOSP guideline, archive
classification, character habits, assessment guideline) and the rules for staff administration (attendance, leave,
performance). Add each document here with its number, date and the catalog IDs it governs when it is read.

