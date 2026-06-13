from app.services.llm import LLMClient
from app.store.conversations import ConversationStore


SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Respond concisely and accurately. "
    "If you're unsure about something, say so.\n\n"
    "CAPABILITIES AND LIMITATIONS — be upfront about these immediately:\n"
    "You CANNOT analyze, describe, or process images sent by the user.\n"
    "You CANNOT browse the web on your own — use only information the user provides.\n"
    "You CANNOT execute code, run programs, or interact with external systems.\n"
    "You CANNOT access files, databases, or services outside this conversation.\n"
    "If asked to do something outside your capabilities, say so directly and immediately. "
    "Do not promise to try and then fail."
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
