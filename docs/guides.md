# Guide pages (Panduan) (F-021)

Every app has in-app guides per role (`/panduan` for the public, `/admin/panduan` for staff), modelled on the
structure of GitHub Docs' "Get started" (docs.github.com/en/get-started): a calm landing page, articles grouped by
path, one idea per section, short copy. Adapt the pattern, never its content or branding. Text in
plain Indonesian (`bahasa-indonesia-plain`); design per [ui.md](ui.md). Elegant means a clear structure **richly decorated**: Codex-made art is an important part of
guides (F-022) — the structure below stays calm and readable, the decoration makes it inviting.

## Landing page (per role)

- `h1` title + **one sentence** that says who the guide is for and what it helps with.
- **Mulai dari sini** (recommended): 4–8 articles for the first tasks, each a title link + a one-line description.
- **Semua panduan**: articles grouped by category (categories follow the URL path: `/panduan/<role>/<kategori>/<artikel>`),
  each a title + one line, each category with its own Codex illustration or painted icon.
- Decoration (all by Codex briefs): a hero painting per role landing, a picture per category, pattern backgrounds and
  dividers between sections, painted step pictures in procedures, decorated callouts, an animated loader/skeleton.
- A search box at the top (searches titles, descriptions and headings; also inside an article, SPMB D-097).

## Article anatomy

| Part | Rule |
| --- | --- |
| Breadcrumbs | `Panduan › <Peran> › <Kategori> › <Judul>`, always |
| Title (`h1`) | The task in plain words, sentence case: "Mengunggah berkas pendaftaran" |
| Lead | One sentence: what the reader will be able to do (shown also as the description in lists) |
| "Dalam artikel ini" | A mini table of contents of the `h2`s; right column on desktop, collapsible at the top on phones; highlights the current section |
| Sections | `h2` per idea, short paragraphs (2–4 sentences), lines ≤ ~70 characters wide |
| Procedures | Numbered steps, one action per step, the exact button/menu names in bold as they appear in the app; a screenshot only when it saves words (light and dark when the app has both, alt text in Indonesian) |
| Callouts | Three kinds only: **Catatan**, **Tips**, **Penting** — tinted background, icon + label, no side stripe (ui.md) |
| Tables | Short cells, for comparisons and "what you can do here" |
| Related | "Bacaan lanjutan": 2–5 links |
| Navigation | Previous / next article within the category |
| Feedback | "Apakah halaman ini membantu? Ya / Tidak" (+ optional short text), stored without personal data, shown to admins |
| Footer | "Diperbarui <tanggal>" and a contact link (WhatsApp/help desk) |

## Layout and quality

- Desktop: left sidebar with the category tree of the role (current article marked), content column, right column for
  "Dalam artikel ini". Phone: sidebar and contents collapse into buttons at the top; reading column full width.
- Typography first: a clear type scale, generous line height, consistent spacing; decoration around the text, never
  under it in a way that hurts reading contrast; dark mode if the app has it.
- Printable (`@media print` hides navigation; A4/F4), linkable headings (anchor on hover/focus), fast (static
  rendering; the article is readable before its decoration loads, with skeletons for art), accessible (landmarks, skip link, keyboard, AA contrast).
- Guides live with the code (e.g. Markdown files per module, SPMB `app/Modules/<Name>/Guide/<role>.md`) so a feature
  and its guide change in the same PR; the guide is part of "done".
