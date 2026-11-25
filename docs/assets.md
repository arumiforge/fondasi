# Front-end assets: minify the served copy, keep the original, version every file (F-018)

Applies to every web app, any stack. Proven in SPMB (D-086, D-094).

## Minify only what the public downloads

| Asset | Original (edited by people, in git) | Served copy (minified) | Tool (any equivalent is fine) |
| --- | --- | --- | --- |
| CSS | `resources/css/` (or the stack's source folder) | `public/build/*.css` | Tailwind `--minify`, Lightning CSS, cssnano |
| JavaScript | `resources/js/` | `public/build/*.js` | esbuild, Terser, Vite/Rollup |
| SVG | `resources/img/**/*.svg` | `public/assets/img/**/*.svg` | svgo (keep `viewBox`, ids used by `<use>`/`<view>`, classes, CSS variables) |
| HTML | templates/views | the HTTP response | a response filter that removes indentation and comments, keeping `pre`, `textarea`, `script`, `style` and whitespace-sensitive blocks |
| Raster images | masters (e.g. Codex's `ai/generated/`) | `public/assets/img/**/*.webp` | already compressed WebP/AVIF; resize to the sizes used |

Rules:
- **Originals stay readable and are never overwritten**: the build reads `resources/` (or equivalent) and writes only
  to the public build folder. Never edit a served copy by hand.
- Build output is generated in CI and in the Docker image; it is git-ignored unless the deploy needs it committed
  (then committed only by the build).
- The build fails when a minifier drops content it should keep (e.g. an SVG `<style>` block).
- External libraries (fonts, charts, icons, editors) are **installed through the package manager, pinned, bundled and
  self-hosted** — no runtime CDN for anything the app needs (privacy, availability, CSP). Licences go into
  `THIRD_PARTY_NOTICES.md`; only the parts in use are shipped (tree-shaking, icon subsets, font subsets).
- Compression (gzip/brotli) by the web server or Cloudflare on top of minification.

## Version every file so changes are never stuck in a cache

- Every served CSS, JS, image, font and SVG URL carries a version that changes when the file changes:
  either a **content hash in the file name** (`app.3f2c1a9b.css`, preferred when the bundler supports it) or a query
  `?v=<hash or modification time>` added by the view helper (SPMB: `?v=<mtime>` from `ui_helper`).
- Versioned files are served with `Cache-Control: public, max-age=31536000, immutable`; unversioned files
  (rare) with a short max-age; **HTML is never cached long** (`no-cache` or a few minutes) so it always points to the
  current versions.
- Uploaded or replaceable files (logos, hero slides, share images) get a version from their stored change time or
  hash, so a new logo appears at once everywhere.
- Service workers (if any) use the same versions and drop old caches on activation.
- Cloudflare: cache rules respect the origin's headers; after a deploy no manual purge is needed because URLs change.
