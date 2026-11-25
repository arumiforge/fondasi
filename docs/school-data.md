# Detailed student data in internal school apps (F-023)

Public apps (registration, information sites) collect only what their task needs. **Internal school apps** — student
records, homeroom tools, health room (UKS), counselling (BK), athletics, aid administration — may hold much more,
because the school and the students' parents/guardians have agreed on it. This page says how. The reference schema is
the data set [`skema-siswa`](../data/skema-siswa/) (61 fields: identity, family, address, interests and health, aid
and documents); each app adapts it with the school and records its changes.

## The agreement comes first

- The school (the data controller) and the parent/guardian agree in writing on what is collected, why, who sees it and
  how long it is kept. The app stores the agreement's version and when each family accepted it (or the school confirms
  it was signed on paper).
- Each field group shows its purpose to the parent when filled online ("Data kesehatan dipakai UKS dan wali kelas
  untuk menangani keadaan darurat").
- Children's data and **specific personal data** under UU PDP — health (illness, injury, senses, blood type), special
  needs (ABK), religion, biometric — get the strictest handling below. Aid numbers (KIP, KPS), NIK, KK and birth
  certificate numbers are identity data with the same care.

## Who sees what (need to know)

- Fields belong to groups; permissions are given **per group**, not just per page: e.g. homeroom teachers see identity,
  family contact and health summary of their own class; UKS sees health; BK sees family and special needs; the
  athletics coach sees name, class, birth date, height/weight, injuries; the treasurer sees aid fields.
- Lists and exports show only the groups the user may see; NIK, KK and phone numbers are masked unless the role needs
  them in full.
- Editing follows the schema's **units** (`unit=…`): fields that belong together (region picker, origin school) are
  edited and approved as one block; changes by parents can wait for staff approval.

## Protection

- Every view of a sensitive group's detail and every change is in the audit log (who, when, what); exports of
  sensitive groups need their own permission and are logged.
- Sensitive groups are encrypted at rest (field-level or database encryption) when the stack allows; backups are
  encrypted when they leave the server; storage location per [storage.md](storage.md) (public schools: Indonesia).
- No sensitive data in notifications, WhatsApp texts, URLs, logs, AI prompts or staging; demo data uses invented people.

## Lifetime

- Retention per the agreement: e.g. health and counselling data deleted or anonymised a set time after the student
  leaves; identity and academic records kept as school archives require. A scheduled job does it and reports.
- Parents can see their child's data, ask for corrections, and withdraw optional parts; the app records requests and
  how they were handled.

## Forms for many fields

- Long forms are split by group into steps with a summary before saving ([feedback.md](feedback.md) tier 3), keep a
  draft, and show progress ("Langkah 2 dari 5").
- Field formats from the schema (`kapital`, `proper`, `nik`, `nisn`, `wa`, `kode_pos`, relative date ranges), option
  lists stored as the exact option text, "Lainnya" stores the typed text, exclusive options ("Tidak Ada / Sehat")
  clear the others, hidden fields are cleared ([web-baseline.md](web-baseline.md) §5 for identity fields).
- Exports use the Indonesian labels of the schema as headers ([conventions.md](conventions.md), F-012).
