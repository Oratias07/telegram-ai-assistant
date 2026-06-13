# Telegram AI Bot — Personal AI Assistant

A multi-capability Telegram bot that provides chat, web search, deep search with synthesis, and image generation—all powered by Groq's fast inference.

**Live bot:** [@telegram_ai_assistant_bot](https://t.me/telegram_ai_assistant_bot) (pending deployment)

---

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and usage guide |
| `/search <query>` | Quick DuckDuckGo results in a numbered list |
| `/deep <query>` | Fetch top 4 results, extract content, synthesize answer with citations |
| `/image <prompt>` | Generate image via Pollinations.ai |
| `/reset` | Clear conversation history for the current user |
| _(plain text)_ | Multi-turn chat with Groq LLM |

---

## Features

1. **Chat** — Multi-turn conversation with context history (last 12 turns), persisted across restarts.
2. **Shallow Search** (`/search`) — Quick DuckDuckGo results in a numbered list.
3. **Deep Search** (`/deep`) — Fetch top 4 results, extract content, synthesize an answer with citations.
4. **Image Generation** (`/image`) — Generate images via Pollinations.ai.
5. **Rate Limiting** — 3 requests per 60s on expensive ops (deep search, image generation).
6. **Security** — SSRF guards, prompt-injection defense via source wrapping, MarkdownV2 escaping, input sanitization.

---

## Architecture

```
app/
├── main.py              # Entrypoint: polling + command registration
├── config.py            # pydantic-settings for env vars
├── bot/
│   ├── handlers.py      # Telegram command/message handlers
│   └── formatting.py    # MarkdownV2 escaping, message splitting
├── services/
│   ├── llm.py           # LLMClient interface + Groq implementation
│   ├── chat.py          # Multi-turn orchestration
│   ├── search.py        # DuckDuckGo shallow search
│   ├── deep_search.py   # Pipeline: search → fetch → extract → synthesize
│   ├── extract.py       # SSRF-safe fetch + trafilatura
│   └── images.py        # ImageGenerator interface + Pollinations
├── store/
│   ├── db.py            # SQLite initialization
│   └── conversations.py # Message CRUD + history windowing
└── core/
    ├── security.py      # SSRF guard, input sanitization
    ├── rate_limit.py    # Per-user rate limiter
    └── logging.py       # Structured logging
```

---

## Run Locally

### Prerequisites
- Python 3.11+
- Telegram bot token from [@BotFather](https://t.me/botfather)
- Groq API key from [console.groq.com](https://console.groq.com)

### Setup

```bash
git clone https://github.com/Oratias07/telegram-ai-assistant.git
cd telegram-ai-assistant

# Create venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env

# Edit .env with your tokens
# TELEGRAM_BOT_TOKEN=<your_token>
# GROQ_API_KEY=<your_key>

# Run
python -m app.main
```

Bot will start polling. Send `/start` in Telegram to test.

### Run Tests

```bash
pytest tests/ -v
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | From @BotFather |
| `GROQ_API_KEY` | ✅ | From console.groq.com (free tier) |
| `DATABASE_PATH` | optional | SQLite path (default: `./bot.db`) |

---

## Deployment

### Self-Hosted Windows Service via NSSM (Recommended for local always-on)

Bot runs as a Windows service that auto-starts on boot and auto-restarts on crash.

**Prerequisites:** Download [NSSM](https://nssm.cc/download), extract, add to PATH.

**Install (run PowerShell as Administrator):**

```powershell
cd <repo>
.\scripts\install_windows_service.ps1
```

Script does:
- Installs service `telegram-ai-assistant`
- Auto-start on boot
- Auto-restart on crash (5s delay)
- Logs to `logs/service.out.log` and `logs/service.err.log`

**Verify running:**

```powershell
Get-Service telegram-ai-assistant
Get-Content logs\service.out.log -Tail 20 -Wait
```

**Uninstall (run PowerShell as Administrator):**

```powershell
.\scripts\uninstall_windows_service.ps1
```

**Keep bot alive 24/7 — disable sleep/hibernate (run as Administrator):**

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

To re-enable sleep:

```powershell
powercfg /change standby-timeout-ac 10
powercfg /change hibernate-timeout-ac 10
```

**Alternative — Task Scheduler (no install required):**

1. Open Task Scheduler → Create Basic Task
2. Trigger: At startup
3. Action: `<repo>\venv\Scripts\python.exe` with args `-m app.main`, start in `<repo>`
4. Advanced: "Run whether user is logged on or not"

---

### Railway / Fly.io (Cloud Always-On)

1. Push repo to GitHub
2. Connect GitHub repo to Railway/Fly
3. Set env vars in dashboard
4. Deploy

**Note:** Avoid Render free tier — sleeps after 15 minutes of inactivity.

### Docker

```bash
docker build -t telegram-ai-bot .
docker run -e TELEGRAM_BOT_TOKEN=... -e GROQ_API_KEY=... telegram-ai-bot
```

---

## Security

- **SSRF Guard:** Blocks private/loopback/reserved IPs before fetch
- **Prompt Injection Defense:** Scraped content wrapped in `<source>` tags with explicit ignore-instructions directive
- **MarkdownV2 Escaping:** All user output properly escaped for Telegram
- **Message Splitting:** Long responses automatically split over 4096-char limit
- **Rate Limiting:** Per-user cap on expensive operations (3 req/60s)
- **Groq 429 Handling:** Automatic retry with exponential backoff

---

## API Models & Providers

- **LLM:** Groq `llama-3.3-70b-versatile` (128k context, ~50 tok/sec)
- **Search:** DuckDuckGo (free, no API key)
- **Extraction:** trafilatura + httpx
- **Image Generation:** Pollinations.ai (free)

---

## What I'd Do Next

1. **Embeddings + Reranking** — Use Groq's embeddings to rank deep-search chunks instead of naive truncation.
2. **Conversation Summarization** — Summarize old turns to reduce token cost on long chats.
3. **Intent Routing** — LLM-based command routing instead of explicit commands only.
4. **Async Task Queue** — Celery + Redis for long-running deep searches (don't block update handler).
5. **Analytics Dashboard** — Track query volumes, latency, error rates (Grafana + Prometheus).
6. **Webhook Instead of Polling** — Reduces resource usage on production (Railway/Fly).
7. **Multi-LLM Support** — Swap Groq for Gemini/OpenAI without code changes (interface already supports it).

---

## Testing

- 52 comprehensive tests covering: config, chat, search, deep search, SSRF guards, rate limiting, formatting, LLM interface, image generation.
- All external I/O mocked (Groq, DuckDuckGo, httpx, Telegram).
- Tests run in ~3 seconds.

```bash
pytest tests/ -v --cov=app
```

---

## License

MIT. Free to use and modify.

---

## Support

For issues or questions, open an issue on [GitHub](https://github.com/Oratias07/telegram-ai-assistant/issues).
