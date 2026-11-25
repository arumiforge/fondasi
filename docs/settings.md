# Integration settings: environment first, panel second (F-005)

Every app reads integrations (file storage, Turnstile, mail, AI providers…) the same way, whatever its stack.

## Precedence

1. **Environment variable set** (in the server's env file of that environment) → that value is used. The app's
   panel shows the field filled in, read-only, with the note **"Diatur oleh server"**; secrets show only
   `••••` plus the last 4 characters.
2. **Environment variable empty or absent** → the panel's value is used. Secrets are stored encrypted with the
   app's own key (SPMB: `encryption.key`), never shown again after saving, replaceable at any time.
3. **Neither** → the feature is off and says so in plain words ("Penyimpanan awan belum diatur").

Every change in the panel goes to the app's audit log (who, when, which field — never the secret itself).
A **"Coba koneksi"** button tests the active settings and reports in plain Indonesian.

## Standard variable names

Names are the same in every app, so one server env file template fits all. An app may support only part of them.

| Group | Variables |
| --- | --- |
| File storage ([storage.md](storage.md)) | `STORAGE_DRIVER` (`local` \| `s3`), `STORAGE_S3_ENDPOINT`, `STORAGE_S3_REGION`, `STORAGE_S3_BUCKET`, `STORAGE_S3_ACCESS_KEY_ID`, `STORAGE_S3_SECRET_ACCESS_KEY`, `STORAGE_S3_PATH_STYLE` (`true`/`false`), `STORAGE_S3_PREFIX` |
| Turnstile | `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`, `TURNSTILE_ENABLED` (`true`/`false`) |
| Mail (SMTP) | `MAIL_HOST`, `MAIL_PORT`, `MAIL_ENCRYPTION` (`tls`/`ssl`/`none`), `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME` |
| AI providers | `AI_PROVIDERS` is not used: AI connections are a list, managed in the panel only (SPMB D-110); env may set `AI_ENABLED=false` to switch AI off server-wide |
| Server backups (not the app) | restic settings in a root-only file per app (`/opt/apps/<app>/offsite.env`), never in the app's env |

Rules: no secret in the repository, in examples (use `<…>` placeholders) or in a chat; staging and production
have **separate** keys and buckets; one key per app, limited to what it needs.

## Turnstile

- One Turnstile widget per app (Cloudflare → Turnstile), hostnames: the production domain and the staging
  domain. Development uses Cloudflare's test keys (site key `1x00000000000000000000AA`, secret
  `1x0000000000000000000000000000000AA`, always pass) — never a real key on a laptop.
- Use it on public forms that create data or try passwords: registration, sign-in, status check, contact.
  Not on pages behind a staff sign-in.
- Verify on the server for every submit (`https://challenges.cloudflare.com/turnstile/v0/siteverify`):
  check `success`, the `hostname` and, when set, the `action`. A token is single-use and expires after
  5 minutes; the form says plainly what to do when it fails ("Mohon centang kotak verifikasi lagi").
- If Cloudflare cannot be reached, the form refuses with a friendly message (fail closed) and the event is
  logged; rate limiting stays on as the second line.
