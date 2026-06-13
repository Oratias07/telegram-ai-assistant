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

## Phase 2 ✅ COMPLETE
- **Date:** 2026-06-13
- **Status:** All 31 tests passing
- **Built:**
  - `services/search.py`: `shallow(query, k=5)` using DDGS → list[Result(title, url, snippet)]
  - `bot/formatting.py`: `escape_markdown_v2()` (special char escaping), `split_message()` (4096 char limit)
  - `bot/handlers.py`: `search_handler(/search <q>)` → TYPING action → numbered markdown list
  - Updated `main.py` to register `/search` command
- **Tests (11 new):**
  - search: returns results, handles empty results, error handling, respects k parameter
  - formatting: escape special chars, split long messages, handle edge cases
- **Key implementation:**
  - DDGS with 10-second timeout, returns empty list on error (graceful fallback)
  - MarkdownV2 escape for title/URL, split output if > 4096 chars
  - No synthesis yet — just search results in formatted list
- **Commit:** cb55953
- **Pushed:** Yes

## Phase 3 ✅ COMPLETE
- **Date:** 2026-06-13
- **Status:** All 49 tests passing
- **Built:**
  - `core/security.py`: `is_safe_url()` (blocks private/loopback/reserved/multicast IPs), `sanitize_input()` (null-byte removal + truncation)
  - `services/extract.py`: `fetch_and_extract(url, timeout=10, max_size=5MB)` - SSRF-guarded httpx async fetch + trafilatura extraction
  - `services/deep_search.py`: `deep_search(query, llm) → DeepResult` - shallow(k=6) → top 4 URLs → `asyncio.gather()` fetch+extract concurrently → fallback snippets if extraction fails → LLM synthesis with `<source id=N>` wrapping → cited answer + sources list
  - `bot/handlers.py`: `deep_search_handler(/deep <q>)` - send "🔎 Searching…", run pipeline, EDIT original message with result + sources
  - Updated `main.py` to register `/deep` command
- **Tests (28 new):**
  - security (10): valid/invalid URLs, schemes, localhost/127, private IPs (10.x, 192.168.x), metadata IP (169.254.169.254), input sanitization
  - deep_search (8): no results, no extracted content (fallback snippets), successful extraction+synthesis, top 4 URLs, synthesis prompt building
- **Key implementation:**
  - SSRF check: DNS resolve + ipaddress module, blocks private/loopback/link-local/reserved/multicast
  - Extract: 10s timeout, 5MB size limit, 5 redirect max, fallback to snippet if trafilatura returns None
  - Deep search: concurrent fetch with `asyncio.gather(return_exceptions=True)`, truncate each doc to 2500 chars
  - Synthesis prompt: system instruction to ignore instructions in source tags (prompt-injection defense), user message wraps sources in `<source id=N url="...">content</source>`
  - Handler: send status message, run async pipeline, edit status with final result
- **Commit:** e972188
- **Pushed:** Yes

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
