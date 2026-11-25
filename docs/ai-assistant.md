# AI help assistant (chatbot) (F-019)

Rules for any app that answers users with an AI model. Proven in SPMB (D-110, module Asisten); other apps adapt the
content sources and limits with the user.

## Answer in this order (cheapest and most reliable first)

1. **Quick choices** at the start (the app's top questions) open the right page or a saved answer.
2. **The app's own Q&A** is searched for a typed question; a good match is shown with a link to the full answer.
3. **AI last**, only when nothing matches or the user asks for it, using only the app's own content (Q&A, guides,
   schedules, requirements, contacts) supplied in the prompt; it refuses other topics.
4. **Handover to people** (WhatsApp/contact) when the AI cannot answer, signals "not covered", or a limit is reached.

The widget says it is automatic, asks users not to type NIK or other personal data, and never looks up personal
records (status checks stay in their own authenticated pages).

## Providers: OpenAI-compatible, a list with rotation and failover

- A provider = name, base URL, model, API key (stored encrypted, shown masked, env wins over panel per
  [settings.md](settings.md)), timeout (default 20 s), max tokens, temperature (default 0.3), on/off.
- Requests use only the common Chat Completions fields: `model`, `messages`, `max_tokens`, `temperature`. Anything
  provider-specific is a per-provider option, never sent to all.
- **Round robin with failover**: active providers that are not resting are tried least-recently-used first. A failure
  — HTTP 429, 5xx, 401/403/404, timeout, network error, unreadable or **empty** reply — moves to the next provider
  within the same request and puts the failing one to **rest** (default 5 minutes; longer for 401/403 until fixed).
  The user only sees the handover message when every provider failed.
- Keys and full prompts never appear in logs or error messages (scrub the key from any text before logging).
- A "Coba koneksi" button per provider sends a tiny request and reports the result in plain Indonesian.

### Gemini through its OpenAI-compatible endpoint

Checked against Google's documentation when writing this (2026-11); re-check when adding a provider.

| Setting | Value / rule |
| --- | --- |
| Base URL | `https://generativelanguage.googleapis.com/v1beta/openai/` (Chat Completions at `…/chat/completions`) |
| Key | a Gemini API key from Google AI Studio, sent as `Authorization: Bearer <key>` |
| Model | the exact model ID (e.g. a current `gemini-…-flash` model); no aliases of other providers |
| Thinking models | Gemini 2.5+ "think" before answering and those tokens count against the output budget: with a small `max_tokens` the reply can come back **empty** (`finish_reason: length`). Set the per-provider option `reasoning_effort` to the lowest level the model allows (`none` where supported) or raise `max_tokens` (e.g. ≥ 1024), and treat an empty reply as a failure (failover) |
| Unsupported fields | send only the common fields above; unknown OpenAI fields can be rejected with HTTP 400 |
| Errors | quota errors arrive as 429 (`RESOURCE_EXHAUSTED`); the error body may differ in shape from OpenAI's — parse defensively and fall back to the status code |
| Data use | free-tier requests may be used by Google to improve its products: use a paid tier (or another provider) for anything beyond public Q&A, and never send personal data |

Other OpenAI-compatible providers (OpenAI, Groq, OpenRouter, DeepSeek, local models) follow the same list; record each
provider's quirks in the app's docs when found.

## Limits on answers

| Limit | Default (changeable by the super admin) |
| --- | --- |
| AI answers per visitor per day | 10 (counted by a daily-salted hash, no IP stored) |
| AI answers per site per day | 300 |
| Question length | 500 characters; longer input is cut with a note |
| Answer length | `max_tokens` ~400 (more for thinking models, see above) and the prompt asks for at most ~120 words, plain Indonesian, short paragraphs or a short list |
| Conversation memory | the last 3–4 turns only |
| Topic | only the app's content; everything else gets a polite refusal and the handover button |

Only AI answers count against the limits; quick choices and Q&A matches are free. When a limit is reached the widget
says so plainly and offers the handover.

## Privacy and quality

- Long digit sequences (NIK, NISN, phone), e-mail addresses and similar are masked in the browser **and** on the
  server before matching, sending or storing.
- Questions are logged without IP so the client can improve its Q&A; logs are pruned (e.g. 180 days).
- The model signals "not covered" with a fixed marker (SPMB: `[[TANYA_PANITIA]]`) that the app turns into a prominent
  handover button; answers are rendered from Markdown to safe HTML (no raw HTML from the model).
- AI is off by default; the app works with quick choices and Q&A alone.
