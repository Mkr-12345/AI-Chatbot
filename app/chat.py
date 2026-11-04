"""Multi-turn conversation state and single-turn prompt comparison."""

from app.llm import complete
from app.prompts import DEFAULT_PROMPT_ID, get_prompt

MAX_MESSAGE_CHARS = 4000


def clean_message(text: str) -> str:
    message = (text or "").strip()
    if not message:
        raise ValueError("Message is empty.")
    if len(message) > MAX_MESSAGE_CHARS:
        raise ValueError(f"Message is longer than {MAX_MESSAGE_CHARS} characters.")
    return message


class Conversation:
    """Keeps a system prompt plus the user/assistant turns sent back each request."""

    def __init__(self, prompt_id: str = DEFAULT_PROMPT_ID):
        prompt = get_prompt(prompt_id)
        self.prompt_id = prompt["id"]
        self.system_prompt = prompt["text"]
        self.turns: list[dict] = []

    def messages(self) -> list[dict]:
        return [{"role": "system", "content": self.system_prompt}, *self.turns]

    def set_prompt(self, prompt_id: str) -> None:
        prompt = get_prompt(prompt_id)
        self.prompt_id = prompt["id"]
        self.system_prompt = prompt["text"]

    def reset(self) -> None:
        self.turns = []

    def ask(self, user_text: str, complete_fn=complete) -> str:
        message = clean_message(user_text)
        self.turns.append({"role": "user", "content": message})
        reply = complete_fn(self.messages())
        self.turns.append({"role": "assistant", "content": reply})
        return reply


def compare_prompts(user_text: str, prompt_a: str, prompt_b: str, complete_fn=complete) -> dict:
    """Send one message to two prompts with no shared history."""
    message = clean_message(user_text)
    left = get_prompt(prompt_a)
    right = get_prompt(prompt_b)

    def once(prompt_text: str) -> str:
        return complete_fn(
            [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": message},
            ]
        )

    return {
        "message": message,
        "a": {"id": left["id"], "name": left["name"], "reply": once(left["text"])},
        "b": {"id": right["id"], "name": right["name"], "reply": once(right["text"])},
    }
