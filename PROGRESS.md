# Telegram AI Bot — Build Progress

## Phase 0 (Complete)
- **Date:** 2026-06-13
- **Status:** ✅ COMPLETE — all tests pass, bot runs locally with polling
- **What was built:**
  - git init + `.gitignore`, `.env.example`
  - Project structure: `app/{bot,services,store,core}`, `tests/`
  - `config.py` with pydantic-settings for `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `DATABASE_PATH`
  - Minimal `main.py` with `/start` handler + long-polling entrypoint
  - Tests: config loading/validation (4 tests), start handler (1 test)
- **Tests:** 5 passing, all mocked (no external I/O)
- **Key decisions:**
  - Using long-polling (simplest for local dev, spec-compliant)
  - Storing secrets in `.env` (never committed; `.env.example` provided)
  - pydantic-settings for env-var validation and defaults
  - Fixed ddgs version: spec said `~=6.0` but latest is `~=9.9`
- **To run Phase 0 verification:**
  ```bash
  python -m app.main
  ```
  Bot will start polling for updates. Send `/start` in Telegram to test.

---

## Phase 1 (Ready to start)
**Multi-turn chat state + history window + LLM integration**
- Implement: `store/db.py` (SQLite), `store/conversations.py` (history CRUD), `services/llm.py` (Groq client), `services/chat.py` (orchestrator)
- Handler: any non-command text → `chat.reply()`; `/reset` clears history
- Tests: conversation windowing, chat_id isolation, LLM prompt building, reset behavior
- **Next step (once approved):** Scaffold SQLite table, implement `append/history/reset`, build LLMClient interface + Groq impl

---

## Phase 2 (Not started)
**Shallow web search via ddgs**

## Phase 3 (Not started)
**Deep search: SSRF-safe fetch + trafilatura extraction + LLM synthesis**

## Phase 4 (Not started)
**Image generation via Pollinations**

## Phase 5 (Not started)
**Hardening + rate limiting + full test suite + README**

---

## Blockers / Notes
- None. All Phase 0 requirements met.
- Awaiting approval to proceed to Phase 1.
