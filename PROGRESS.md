# Telegram AI Bot — Build Progress

## Phase 0 ✅ COMPLETE
- git init + `.gitignore`, `.env.example`
- Project structure + config.py (pydantic-settings)
- Minimal bot with `/start` handler + polling
- **Tests:** 5 passing (config, handler)
- **Commit:** e357f0d

## Phase 1 ✅ COMPLETE
- **Date:** 2026-06-13
- **Status:** All 20 tests passing
- **Built:**
  - `store/db.py`: SQLite init, messages table (chat_id, role, content, ts, id)
  - `store/conversations.py`: `ConversationStore` with append/history(max_turns)/reset
  - `services/llm.py`: `LLMClient` interface + `GroqClient` (llama-3.3-70b-versatile, 1024 tokens, temp=0.7)
  - `services/chat.py`: `ChatService` orchestrator (load history window → prepend system prompt → LLM → persist both turns)
  - `bot/handlers.py`: `message_handler` (any text → chat.reply), `reset_handler` (/reset)
  - Updated `main.py` to init DB, services, register handlers
- **Tests (20 total):**
  - conversations: append, history window, chronological order, chat_id isolation, reset, reset isolated
  - chat: user/assistant persistence, LLM response, system prompt inclusion, history building, chat_id isolation
  - llm: abstract interface, Groq implementation
  - config + main: existing tests still passing
- **Key implementation details:**
  - History fetches all messages for chat, slices in Python to get last N*2 (handles windowing)
  - ChatService builds messages = [system_prompt] + history, sends to LLM, appends reply
  - All I/O mocked in tests (no live Groq calls)
  - max_turns defaults to 12 (24 messages if user-assistant pairs)
- **Commit:** a4c0b01
- **Pushed:** Yes

---

## Phase 2 (Ready to start)
**Shallow web search via ddgs**
- Implement: `services/search.py` with `shallow(query, k=5) -> list[Result(title, url, snippet)]` using ddgs
- Handler: `/search <q>` → send TYPING action → return formatted numbered list with links
- Tests: ddgs parsing, empty results, error handling

## Phase 3 (Not started)
**Deep search: SSRF-safe fetch + trafilatura extraction + LLM synthesis**
- `core/security.py`: `is_safe_url()` — block private/loopback/reserved IPs, enforce timeout/redirects/response size
- `services/extract.py`: async fetch + trafilatura, SSRF-guarded
- `services/deep_search.py`: search(k=6) → top 4 URLs → concurrent fetch+extract → LLM synthesis with `<source>` tags → answer + cited sources
- Handler: `/deep <q>` → send "searching…" → fetch+extract → EDIT message with result
- Tests: extract success/fallback/error, synthesis prompt building, no-sources/all-fail paths, SSRF guard blocking private IPs

## Phase 4 (Not started)
**Image generation via Pollinations**
- `services/images.py`: `ImageGenerator` interface + Pollinations impl (returns URL or bytes)
- Handler: `/image <prompt>` → send UPLOAD_PHOTO action → generate → reply_photo with error handling
- Tests: image generation success, provider errors

## Phase 5 (Not started)
**Hardening + rate limiting + README**
- Per-user rate limiting on `/deep` and `/image` (dict of timestamps per chat_id)
- Handle Groq 429 (retry or friendly message)
- Tests: rate limit enforcement, Groq error handling, formatting (4096 char split + MarkdownV2 escaping)
- README: what it does + live bot link, architecture overview, run locally, env vars table, "What I'd do next"

---

## Blockers / Notes
- None. Phase 1 complete. Ready for Phase 2 approval.
