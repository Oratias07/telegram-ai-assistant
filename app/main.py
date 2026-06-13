import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import load_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I'm your AI assistant. Send a message to chat.")


async def main() -> None:
    settings = load_settings()
    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))

    async with app:
        await app.start()
        logger.info("Bot started (polling)")
        await app.updater.start_polling()
        await app.idle()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
