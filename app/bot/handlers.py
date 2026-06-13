import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from app.services.chat import ChatService
from app.store.conversations import ConversationStore

logger = logging.getLogger(__name__)


async def message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, chat_service: ChatService
) -> None:
    """Handle user text message."""
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    user_text = update.message.text

    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        reply = await chat_service.reply(chat_id, user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        await update.message.reply_text("Sorry, something went wrong. Try again.")


async def reset_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, store: ConversationStore
) -> None:
    """Handle /reset command."""
    chat_id = str(update.message.chat_id)
    store.reset(chat_id)
    await update.message.reply_text("Conversation reset.")
