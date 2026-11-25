# Visual assets made by Codex (F-011)

There is **no limit on decoration** in Fondasi (F-022): every app may be as rich as its identity wants, because all of
it is made and maintained by Codex. Illustrations, paintings, patterns, dividers, special buttons, loaders, skeleton
art, QR designs, animations and 3D scenes of every app are made by **Codex**,
which has access to each app repository and works only from the briefs in that repository. Claude writes the
briefs, reviews the delivery and installs it. Proven in SPMB (D-073, D-075).

## Layout in each app repository

```
AGENTS.md                 points Codex to ai/CODEX.md (template: templates/repo/AGENTS.md)
ai/
  README.md               queue of briefs with status; Codex starter prompt
  CODEX.md                Codex's instructions: scope, git rules, delivery (template: templates/ai/CODEX.md)
  style-guide.md          the app's identity: audience, culture, respect rules, palette, cast, painting and SVG rules
  prompts/NNN-<name>.md   one brief per asset (templates/ai/prompts/_template.md, _template-svg.md)
  generated/              Codex's deliveries: masters, install/ (ready to copy into the app), demo/
  tools/check_assets.py   checks delivered files against their briefs (adapt paths per app)
```

## Workflow

1. **Brief** (Claude): add `ai/prompts/NNN-<name>.md` from a template, a row in the queue with status `requested`,
   grouped into a named batch. Briefs are in English; any text visible in the image is avoided (the app adds
   Indonesian text in HTML) unless the brief says otherwise.
2. **Make** (Codex): the user starts Codex with the starter prompt from `ai/README.md`. Codex makes one batch,
   runs the checker, commits as Arumi Studios on `art/codex-<YYYYMMDD>-<batch>` and opens **one PR into `main`**
   touching only `ai/generated/` and the status lines. Codex never merges and adds no AI attribution.
3. **Install** (Claude): review every file (identity, respect rules, sizes, budgets, safety of SVG/CSS), ask for
   fixes in the PR, copy approved files into the app's asset folders, wire them with Indonesian `alt` text, set
   the status to `done`.

Statuses: `requested` → `generated` → `done`.

## Rules for every app

- The app's identity lives in its own `ai/style-guide.md` (e.g. SPMB: santri, Islamic, NU, Indonesian, Bhinneka;
  an athletics app: Indonesian school athletes, real track and field). Shared across apps: Indonesian people and
  places, modest and respectful depiction, no logos of real schools or organisations unless supplied, no text in
  images, no copyrighted characters, no AI-slop looks ([ui.md](ui.md)).
- Brand colour stays in settings: SVG patterns/dividers are `#000` masks painted with CSS variables; buttons and
  loaders use `currentColor`; paintings keep a swappable accent and get dark variants where the app has dark mode.
- Formats: WebP for paintings (with size budgets), SVG for vectors (no scripts, no external references), CSS for
  buttons/animations (respect `prefers-reduced-motion`).
- Licensed template sources (e.g. Flowbite Pro) and client logos never go into an asset.
- Restrictions a user decided for one app (SPMB D-089: no disability or assistive devices in illustrations) apply
  only there unless recorded here.

## Starter prompt (adapt `<repo>`)

```
Work in the GitHub repository arumiforge/<repo>, starting from the latest main. Read AGENTS.md and ai/CODEX.md and follow them exactly; they point you to ai/style-guide.md and the briefs in ai/prompts/. Make the assets of ONE batch from the queue in ai/README.md (the first batch with status "requested"), check them with python3 ai/tools/check_assets.py, and deliver them only in ai/generated/ (plus the status lines) on a new branch art/codex-<YYYYMMDD>-<batch>, with one pull request into main. Commit as Arumi Studios <arumiforge@gmail.com>. Do not change anything else, do not merge, and add no AI attribution anywhere.
```
