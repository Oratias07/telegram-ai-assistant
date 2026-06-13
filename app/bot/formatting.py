import re


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """Split message into chunks if it exceeds max_length."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 <= max_length:
            current += line + "\n"
        else:
            if current:
                chunks.append(current.rstrip())
            current = line + "\n"

    if current:
        chunks.append(current.rstrip())

    return chunks
