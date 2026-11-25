---
name: fondasi-ai
description: Build or review an AI help assistant (chatbot) in any Arumi Studios app — quick choices and Q&A first, AI last on the app's own content, OpenAI-compatible providers in round robin with failover, Gemini's OpenAI-compatible settings (base URL, thinking budget, empty replies), answer limits per visitor and per day, masking personal data, handover to WhatsApp. Use for any chatbot, AI answer, provider or AI limit work.
---

# AI assistant

Follow `docs/ai-assistant.md` in Fondasi. Re-check a provider's current documentation before adding it (especially
Gemini's OpenAI-compatible endpoint) and record quirks in the app's docs. Test failover with a provider that returns
429 and one that returns an empty reply; never log keys or full prompts.
