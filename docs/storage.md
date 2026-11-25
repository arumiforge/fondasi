# File storage (F-006)

Uploaded files (applicants' documents, photos, generated PDFs, school logos) follow one rule set in every app.

## Default: the VPS disk

- Files live outside the web root, in the app's persistent volume (SPMB: `writable/uploads`), and are served
  only through a controller that checks permission. Names are random IDs, never a NIK, NISN or person's name.
- They are inside the app's daily backup (and its off-site copy).
- `STORAGE_DRIVER=local` (or unset).

## Optional: any S3-compatible provider

Set `STORAGE_DRIVER=s3` and the `STORAGE_S3_*` variables ([settings.md](settings.md)), in env or in the panel.

| Provider | Region / location | `STORAGE_S3_ENDPOINT` | Notes |
| --- | --- | --- | --- |
| Cloudflare R2 | Cloudflare decides (location hint APAC); no Indonesian jurisdiction | `https://<account id>.r2.cloudflarestorage.com` | `STORAGE_S3_REGION=auto`; no egress fees |
| AWS S3 | `ap-southeast-3` (Jakarta) | `https://s3.ap-southeast-3.amazonaws.com` | Indonesia region available |
| Google Cloud Storage (XML API, HMAC keys) | `asia-southeast2` (Jakarta) | `https://storage.googleapis.com` | Indonesia region available |
| IDCloudHost Object Storage | Indonesia | from the provider panel | Indonesian provider |
| Biznet Gio NEO Object Storage | Indonesia | from the provider panel | Indonesian provider |
| Wasabi, Backblaze B2 | no Indonesia region | from the provider panel | Fine for non-personal files |

Endpoints change: always copy the endpoint and region from the provider's panel and test with "Coba koneksi".

### Rules for S3

- **Private buckets only.** Files reach users through the app (permission check, then a stream or a pre-signed
  URL valid ≤ 5 minutes). Only deliberately public assets (logos, banners) may use a public bucket of their own.
- **One bucket per app and environment** (`<app>-production`, `<app>-staging`), or one bucket with
  `STORAGE_S3_PREFIX=<app>/<env>/`; one API key per bucket with object read/write only.
- **Not a backup.** Production files on S3 get a nightly copy to a second location (another bucket/provider,
  or the VPS backup), encrypted when it leaves the provider.
- **Server backups are separate**: the restic off-site bucket (SPMB D-079) has its own bucket and key, never
  shared with app files.
- Switching driver needs a copy step (local ↔ S3) that the app provides as a command; never switch with files
  in place without it.

## Where personal data may live

| Client | Personal data files |
| --- | --- |
| Private schools, foundations, clubs, event organisers | VPS disk or any provider above |
| Public institutions (sekolah negeri, dinas pendidikan, KONI/government bodies) | Storage located in Indonesia: the VPS disk when the VPS is in Indonesia, AWS/GCP Jakarta, IDCloudHost, Biznet Gio (PP 71/2019 on public electronic system operators) |

This table is the working rule, not legal advice: confirm each public-sector client with a lawyer and
record the outcome in the app's decisions. UU PDP applies to every client (consent, purpose, deletion).
