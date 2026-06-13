from app.services.llm import LLMClient
from app.store.conversations import ConversationStore


SYSTEM_PROMPT = (
    "You are an assistant with the following capabilities:\n"
    "- Chat: answer questions and have conversations (that's you).\n"
    "- /search <query>: web search via DuckDuckGo (external tool).\n"
    "- /deep <query>: deep web research with synthesis (external tool).\n"
    "- /image <prompt>: generates images via an external image API — NOT you.\n"
    "  When users ask to generate an image, always direct them to use /image <prompt>.\n"
    "  Never say you cannot generate images — the bot CAN, via the /image command.\n\n"
    "Respond concisely and accurately. If you're unsure about something, say so.\n\n"
    "LIMITATIONS — be upfront about these immediately:\n"
    "You CANNOT analyze, describe, or process images sent by the user.\n"
    "You CANNOT browse the web on your own — direct users to /search or /deep instead.\n"
    "You CANNOT execute code, run programs, or access external systems directly.\n"
    "If asked to do something outside your capabilities, say so and suggest the right command."
)


class ChatService:
    def __init__(self, llm: LLMClient, store: ConversationStore, max_turns: int = 12):
        self.llm = llm
        self.store = store
        self.max_turns = max_turns

    async def reply(self, chat_id: str, user_message: str) -> str:
        """Process user message, get LLM reply, persist both turns."""
        self.store.append(chat_id, "user", user_message)

        history = self.store.history(chat_id, max_turns=self.max_turns)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        reply = await self.llm.complete(messages)
        self.store.append(chat_id, "assistant", reply)

        return reply
