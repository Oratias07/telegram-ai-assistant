import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from app.config import load_settings
from app.store.db import init_db
from app.store.conversations import ConversationStore
from app.services.llm import GroqClient
from app.services.chat import ChatService
from app.services.images import GeminiImagenGenerator, PollinationsGenerator, FallbackImageGenerator
from app.core.rate_limit import RateLimiter
from app.bot.handlers import message_handler, reset_handler, search_handler, deep_search_handler, image_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I'm your AI assistant. Send a message to chat.")


async def main() -> None:
    settings = load_settings()
    db_path = settings.resolve_database_path()
    init_db(db_path)

    llm = GroqClient(api_key=settings.groq_api_key)
    store = ConversationStore(db_path=db_path)
    chat_service = ChatService(llm=llm, store=store)
    pollinations = PollinationsGenerator(timeout=45)
    if settings.gemini_api_key:
        logger.info("Gemini API key present — using Imagen 3 as primary, Pollinations as fallback")
        image_gen = FallbackImageGenerator(
            primary=GeminiImagenGenerator(api_key=settings.gemini_api_key),
            fallback=pollinations,
        )
    else:
        logger.warning("GEMINI_API_KEY not set — using Pollinations only (may hit 402)")
        image_gen = pollinations
    rate_limiter = RateLimiter(max_requests=3, window_seconds=60)

    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_handler))
    app.add_handler(
        CommandHandler(
            "deep",
            lambda update, context: deep_search_handler(update, context, llm, rate_limiter),
        )
    )
    app.add_handler(
        CommandHandler(
            "image",
            lambda update, context: image_handler(update, context, image_gen, rate_limiter),
        )
    )
    app.add_handler(
        CommandHandler(
            "reset",
            lambda update, context: reset_handler(update, context, store),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda update, context: message_handler(update, context, chat_service),
        )
    )

    async with app:
        await app.start()
        logger.info("Bot started (polling)")
        try:
            await app.updater.start_polling()
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopping...")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
