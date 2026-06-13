import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from app.config import load_settings
from app.store.db import init_db
from app.store.conversations import ConversationStore
from app.services.llm import GroqClient
from app.services.chat import ChatService
from app.services.images import PollinationsGenerator
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
    init_db(settings.database_path)

    llm = GroqClient(api_key=settings.groq_api_key)
    store = ConversationStore(db_path=settings.database_path)
    chat_service = ChatService(llm=llm, store=store)
    image_gen = PollinationsGenerator(timeout=30)

    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_handler))
    app.add_handler(
        CommandHandler(
            "deep",
            lambda update, context: deep_search_handler(update, context, llm),
        )
    )
    app.add_handler(
        CommandHandler(
            "image",
            lambda update, context: image_handler(update, context, image_gen),
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
        await app.updater.start_polling()
        await app.idle()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
