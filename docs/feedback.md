# User feedback: messages, confirmations, errors (F-014)

How every Arumi Studios app tells users what happened, whatever the stack. Part of [ui.md](ui.md); text follows
`bahasa-indonesia-plain`. Applied and audited with the `fondasi-feedback` skill.

## Pick the component by consequence, not by habit

| Tier | When | Component | Behaviour |
| --- | --- | --- | --- |
| 0 — In place | The result is visible where the user looks (a toggle, a saved row, a counter) | The change itself + a short status text next to it ("Tersimpan") | No extra pop-up. Announced with `aria-live="polite"` |
| 1 — Low | A light action succeeded, nothing to do next (copy link, draft saved) | **Toast** | Disappears after **5 s + 1 s per 10 words** (minimum 5 s); **pauses on hover and focus**; close button; never holds the only copy of important information |
| 2 — Reversible | A change or removal that can be undone (archive, remove from list, move) | **Toast with "Batalkan"** | Stays **at least 10 s** and until hover/focus leave; the undo is reachable by keyboard; the server keeps the change undoable (soft delete or delayed commit) and the same undo exists elsewhere (Riwayat, Sampah) for users who miss the toast |
| 3 — Form errors | Validation fails, above all on long or multi-step forms | **Inline error under the field + error summary** at the top of the form (or step) | After submit: summary with links to each field, focus moves to the summary, the first field is scrolled into view (centred, clear of sticky headers and the on-screen keyboard); `aria-invalid` + `aria-describedby`; validate on blur/submit, not on every keystroke; server errors map to the same fields; the user's input is kept |
| 4 — Blocking decision | Irreversible or destructive action that cannot be undone (delete permanently, publish results, send to all parents) | **Confirmation dialog** (desktop: centred modal; phone: bottom sheet) | Says exactly what will happen and how many items ("Hapus permanen 12 pendaftar?"); the destructive button names the verb, the safe button ("Batal") has the **initial focus**; Esc and the backdrop cancel; **Enter never confirms a destructive action by default**; focus trapped inside and returned afterwards; very large or irreversible actions ask to type a word ("HAPUS") |
| 5 — Page-level state | Something about the whole page or system: offline, maintenance, registration closed, deadline today, a background job running | **Banner** at the top of the content (not floating), or a **status page** | Persistent until the state changes; dismissible only when harmless; background jobs show progress and finish with a toast (tier 1) or a banner if it failed |

**Completion of a long flow** (registration sent, payment proof uploaded, results published) is **not a modal**: it is
a result page with its own URL, the proof (number, QR, summary), print/download and the next step, so it survives a
refresh, a closed tab and a screenshot. Fatal errors are a friendly error page or a tier-5 banner, never a modal
the user can only close.

Prefer undo (tier 2) over confirmation (tier 4) whenever the action can be made reversible: fewer interruptions,
fewer reflexive "OK" clicks.

## Placement

All floating components are fixed to the viewport (not the document), above headers, sidebars and bottom bars,
inside the safe areas (`env(safe-area-inset-*)`).

| | Desktop | Phone |
| --- | --- | --- |
| Toast | Bottom-right, fixed width (~360 px), newest at the bottom, **at most 3**, identical messages merged | Top-centre, full width minus 16 px margins, below the status bar and the sticky header's actions; swipe up **and** a close button |
| Collisions | Stay clear of floating widgets (chat assistant, back-to-top, cookie notice): offset above them | Never over the bottom navigation, the main action button or the on-screen keyboard |
| Dialog | Centred modal, max ~560 px wide; buttons right-aligned, "Batal" first, the action last | Bottom sheet for confirmations; centred modal only for a critical warning; buttons stacked full width (≥ 44 px), the destructive action in red on top, "Batal" at the bottom where the thumb rests |
| Inline error | Scroll so the field sits in the middle third | Scroll with `scroll-margin` for the sticky header and the keyboard height (`visualViewport`) |
| Banner | Top of the main content, full width of the content column | Same, below the header; never sticky over the form |

One placement per app: choose once in the app's UI rules and keep it on every page.

## Writing the message

- What happened + what to do next, in plain Indonesian: "Berkas belum terunggah karena ukurannya lebih dari 2 MB.
  Pilih berkas yang lebih kecil." — not "Error 413", not "Terjadi kesalahan".
- Sentence case, no exclamation marks for errors, no blaming ("Anda salah…"), no jargon; numbers and dates in local format.
- Success messages are short ("Draf tersimpan"); error messages are specific; one message per event.
- Never only colour: an icon (Lucide) + text; AA contrast; motion off under `prefers-reduced-motion`.

## Accessibility and robustness

- Toasts and status texts live in a container rendered on page load with `role="status"` / `aria-live="polite"`;
  urgent errors that are not form errors use `role="alert"` sparingly.
- Every timed message can be paused and reached by keyboard (WCAG 2.2.1); every gesture has a button (WCAG 2.5.1).
- Server-rendered apps: messages after a redirect (flash) render as a toast with JavaScript and as an inline alert at
  the top of the content without it — the message is never lost.
- The same event never fires two components (no toast + modal for one save).

## Audit checklist (existing pages)

1. List every action and message of the page; map each to a tier; flag mismatches (toast for a permanent delete,
   modal for a draft save, toast for a form error).
2. Long forms: submit empty at 360 px with the keyboard open — is the summary focused and the first field visible?
3. Toasts: duration, pause on hover/focus, close button, keyboard reach of "Batalkan", screen-reader announcement.
4. Dialogs: initial focus on the safe button, Enter does not destroy, Esc cancels, focus returns.
5. Placement: no overlap with chat widget, bottom bar, keyboard, sticky header; one placement on every page.
6. Without JavaScript: flash messages still visible.
7. Copy: every message says what happened and what to do, in plain Indonesian.

Roles when a team does the audit: design (tier map, copy, placement), frontend (components, focus, live regions,
no-JS fallback), QA (checklist at 360 px and 1280 px, keyboard only, screen reader, slow network).
