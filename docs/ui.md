# UI and UX rules: specific, not generic (F-010)

Every app must look designed for its users (Indonesian schools, parents, coaches, athletes), not like a default
AI-generated template. These rules apply to every stack; apps add their own components and identity
(SPMB: `spmb-ui`, D-070).

## Never ("AI slop" patterns)

| Pattern | Do instead |
| --- | --- |
| Eyebrow labels: small uppercase letter-spaced text above a heading | Say it in the heading or a sentence-case subtitle |
| Short accent bars or lines above/below headings | Spacing and type size create hierarchy |
| Cards with a coloured top or side border; alerts with a side stripe | Neutral full border and/or soft shadow; alerts with a tinted background |
| Icons inside tinted circles or squares; emoji as icons | Lucide icons in `currentColor` directly next to the text |
| Purple–blue gradients, glowing blobs, glassmorphism, floating 3D shapes as decoration | Brand colour from settings, real photos or Codex-made illustrations in the app's own identity |
| The default landing page: centred hero + three feature cards with icons + testimonial carousel + "Get started" | Start from the user's task: what they must do today (register, check status, see the schedule) |
| Vague marketing copy ("Solusi digital terdepan", "Tingkatkan efisiensi Anda", "Seamless") | Concrete words about the task: "Daftar dalam 10 menit", "Cek status pendaftaran" |
| Lorem ipsum, fake numbers, placeholder avatars in production | Real content, or an honest empty state |
| Everything centred, everything in cards, every section the same rhythm | Left-aligned reading, cards only for groups of related data, varied section layouts |
| Decoration that delays or blocks the content | Decoration loads after the content, never in its way; off under `prefers-reduced-motion` ([web-baseline.md](web-baseline.md) §6) |

## Always

- **Task first**: the main action of a page is visible without scrolling on a 360 px phone.
- **Plain Indonesian** (`bahasa-indonesia-plain`): sentence case for headings and buttons; buttons say what happens
  ("Kirim pendaftaran", not "Submit"); error messages say what to do next.
- **Every screen handles**: loading (no layout shift), empty (what it means + the next step), error (plain words + retry),
  success (what happened, what is next), no permission.
- **Feedback by consequence** ([feedback.md](feedback.md)): toast only for light results, undo toast for reversible
  changes, inline errors + summary for forms, a dialog only for irreversible actions, banners for page-wide states,
  a result page (not a modal) at the end of a long flow.
- **Forms**: a visible label for every field (never placeholder-only), hints under the field, errors next to it, the
  first error focused, long forms split into steps with a summary before sending.
- **Responsive**: 360 px → 1920 px; admin dashboards full width; tables become cards or scroll inside their own box
  on phones; charts never overlap text.
- **Accessibility**: WCAG 2.2 AA contrast, visible focus, keyboard reachable, real buttons and links, `alt` text in
  Indonesian, touch targets ≥ 44 px, no information by colour alone.
- **Local formats**: dates `25 November 2026`, times `07.30 WIB`, numbers `1.234.567`, money `Rp1.250.000`, phone `0812-3456-7890`.
- **White label**: names, logos, colours, texts from settings, never hard-coded; brand colour must keep AA contrast
  (pick text colour from its luminance).
- **Navigation**: friendly breadcrumbs on every admin page; the current place is always clear.
- **Decoration without limits** (F-022): illustrations, paintings, patterns, dividers, special buttons, loaders,
  animation and 3D are welcome in any amount, on public pages, dashboards and guides alike — all made by Codex in the
  app's identity ([visual-assets.md](visual-assets.md)). The "Never" table is about generic looks, not about how much
  decoration a page has. Conditions: the page works before decoration loads, skeletons instead of blank areas, no
  layout shift, works on phones, motion off under `prefers-reduced-motion`.

## Review checklist (before a PR with UI)

Screenshots at 360 px and 1280 px, light and dark if the app has both; walk the main task with the keyboard; check
the "Never" table above; read every new text aloud once (RASA check of `bahasa-indonesia-plain`).
