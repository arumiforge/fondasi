# Visual assets (Codex briefs)

Every illustration, pattern, divider, special button and animation of <APP> is made by **Codex** from the briefs in
this folder (Fondasi `docs/visual-assets.md`). Claude writes the briefs, reviews the delivery and installs it.

| File | For |
| --- | --- |
| [CODEX.md](CODEX.md) | Codex's instructions |
| [style-guide.md](style-guide.md) | The app's identity and rules |
| [prompts/](prompts/) | One brief per asset (`_template.md` painting, `_template-svg.md` SVG/CSS) |
| [generated/](generated/) | Codex's deliveries (`install/` ready to copy) |
| [tools/check_assets.py](tools/check_assets.py) | Checks deliveries against their briefs |

Statuses: `requested` → `generated` (delivered by Codex) → `done` (installed in the app).

## Codex starter prompt

```
Work in the GitHub repository arumiforge/<repo>, starting from the latest main. Read AGENTS.md and ai/CODEX.md and follow them exactly; they point you to ai/style-guide.md and the briefs in ai/prompts/. Make the assets of ONE batch from the queue in ai/README.md (the first batch with status "requested"), check them with python3 ai/tools/check_assets.py, and deliver them only in ai/generated/ (plus the status lines) on a new branch art/codex-<YYYYMMDD>-<batch>, with one pull request into main. Commit as Arumi Studios <arumiforge@gmail.com>. Do not change anything else, do not merge, and add no AI attribution anywhere.
```

## Queue

| ID | Brief | Batch | Status |
| --- | --- | --- | --- |
