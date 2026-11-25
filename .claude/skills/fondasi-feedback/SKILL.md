---
name: fondasi-feedback
description: Design, review or audit how an Arumi Studios web app gives feedback — toasts, undo toasts, inline form errors with an error summary, confirmation dialogs and bottom sheets, page banners, result pages — on desktop and phone (long pages, on-screen keyboard, sticky headers, chat widgets). Use when building or changing any message, confirmation or error, when users miss messages, when auditing existing pages, or when the user asks for a feedback PRD or a team audit guide.
---

# Feedback (toast, undo, inline errors, dialogs, banners)

The standard is `docs/feedback.md` in Fondasi (tiers 0–5, placement, copy, accessibility, audit checklist). Apply it;
do not restate or change it here — propose changes to that page instead.

## Pick the output

| The user asks for | Deliver |
| --- | --- |
| A feature with messages (most common) | Map every event to a tier in the plan, build it with the app's components, test at 360/1280 px, keyboard, screen reader |
| "Messages are missed / covered" | Reproduce on a 360 px phone with the keyboard open and on a long page; fix placement, focus and tier; before/after screenshots |
| An audit of existing pages | A table per page: event, current component, correct tier, problem, fix, owner (design/frontend/QA); then the fixes as small PRs |
| A PRD or team guide | A document in the app's `docs/` (English, per Fondasi conventions; Indonesian only if it is for the client): background, tier matrix with the app's real events, placement for the app's layout, copy examples, acceptance criteria per tier, audit checklist, roles. No code unless asked |

## Checks that are easy to miss

- Toast for a permanent delete, a form error, or anything the user must act on → wrong tier.
- Completion of a long flow in a modal → it must be a result page with URL, proof and print.
- Auto-dismiss without pause on hover/focus, or an undo the keyboard cannot reach in time.
- Enter confirming a destructive dialog; initial focus on the destructive button.
- Toast placement colliding with the chat widget, bottom navigation, sticky header or keyboard.
- Flash message lost when JavaScript is off (server-rendered apps).
- One event showing two components; more than 3 toasts stacked.
- Copy that says "Terjadi kesalahan" without what to do next (`bahasa-indonesia-plain`).
