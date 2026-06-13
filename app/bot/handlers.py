import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from app.services.chat import ChatService
from app.services import search as search_service
from app.services import deep_search as deep_search_service
from app.store.conversations import ConversationStore
from app.bot.formatting import escape_markdown_v2, split_message

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


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search <query> command."""
    if not update.message or not context.args:
        await update.message.reply_text("Usage: /search <query>")
        return

    query = " ".join(context.args)

    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        results = await search_service.shallow(query, k=5)

        if not results:
            await update.message.reply_text("No results found.")
            return

        lines = ["*Search Results*\n"]
        for i, result in enumerate(results, 1):
            title = escape_markdown_v2(result.title[:50])
            url = escape_markdown_v2(result.url)
            lines.append(f"{i}\\. [{title}]({url})")

        reply = "\n".join(lines)
        for chunk in split_message(reply):
            await update.message.reply_text(chunk, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Error in search: {e}", exc_info=True)
        await update.message.reply_text("Search failed. Try again.")


async def deep_search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, llm_client
) -> None:
    """Handle /deep <query> command."""
    if not update.message or not context.args:
        await update.message.reply_text("Usage: /deep <query>")
        return

    query = " ".join(context.args)

    try:
        status_msg = await update.message.reply_text("🔎 Searching and synthesizing...")
        result = await deep_search_service.deep_search(query, llm_client)

        lines = [escape_markdown_v2(result.answer)]
        lines.append("\n\n*Sources:*")
        for i, source in enumerate(result.sources, 1):
            title = escape_markdown_v2(source.title[:50])
            url = escape_markdown_v2(source.url)
            lines.append(f"{i}\\. [{title}]({url})")

        reply = "\n".join(lines)
        for chunk in split_message(reply):
            await status_msg.edit_text(chunk, parse_mode="MarkdownV2")
            status_msg = await update.message.reply_text(chunk, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Error in deep search: {e}", exc_info=True)
        await update.message.reply_text("Search failed. Try again.")


async def image_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, image_gen: ImageGenerator
) -> None:
    """Handle /image <prompt> command."""
    if not update.message or not context.args:
        await update.message.reply_text("Usage: /image <prompt>")
        return

    prompt = " ".join(context.args)[:500]

    try:
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        image_url = await image_gen.generate(prompt)

        if not image_url:
            await update.message.reply_text("Image generation failed. Try again.")
            return

        await update.message.reply_photo(photo=image_url, caption=escape_markdown_v2(prompt[:1024]))

    except Exception as e:
        logger.error(f"Error in image generation: {e}", exc_info=True)
        await update.message.reply_text("Image generation failed. Try again.")
