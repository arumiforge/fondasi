---
name: fondasi-visual
description: Request visual assets (illustrations, paintings, patterns, dividers, special buttons, loaders, animations) for any Arumi Studios app by writing Codex briefs in the app's ai/ folder, give the user the Codex starter prompt, then review and install what Codex delivers. Use whenever a page needs a visual; also to set up ai/ in a new repository from Fondasi's templates.
---

# Visual assets through Codex

Follow `docs/visual-assets.md` in Fondasi.

- New repository: copy `templates/repo/AGENTS.md` and `templates/ai/` into the app; fill `<APP>`, the asset folders in
  `ai/CODEX.md`, and write `ai/style-guide.md` with the user (identity and respect rules are an interview, not a guess).
- Brief: `ai/prompts/NNN-<name>.md` from the templates, a queue row (`requested`, batch name). English; no text in
  images; sizes, budgets, variants, alt text idea; the app's identity and the `docs/ui.md` "Never" list.
- Hand-off: give the user the starter prompt from `ai/README.md` (Codex works only from the repository).
- Review Codex's PR: identity and respect rules, file names, budgets, SVG/CSS safety (`check_assets.py`), no AI
  attribution in commits or the PR; ask for fixes in the PR; never merge it yourself unless the user asks.
- Install: copy from `ai/generated/install/`, wire with Indonesian `alt`, set status `done`.
