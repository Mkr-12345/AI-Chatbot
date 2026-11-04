"""Named system prompts. Swapping these changes how the model answers."""

PROMPTS = {
    "helpful": {
        "name": "Helpful",
        "text": (
            "You are a clear, friendly assistant. Answer the user's question directly. "
            "Use short paragraphs or a short list when it makes the answer easier to scan. "
            "If you are unsure, say so."
        ),
    },
    "concise": {
        "name": "Concise",
        "text": (
            "Reply in one or two sentences. No greeting, no preamble, and no closing offer "
            "to help further. Include only the information needed to answer the question."
        ),
    },
    "socratic": {
        "name": "Socratic",
        "text": (
            "Help the user reach the answer themselves. Ask one focused guiding question "
            "before giving a full explanation. If they already stated the answer, confirm "
            "it briefly and add one useful detail."
        ),
    },
    "technical": {
        "name": "Technical",
        "text": (
            "Answer as a precise technical reviewer. State assumptions, prefer concrete "
            "terms over metaphors, and mention one edge case when it changes the answer. "
            "Do not add motivational language."
        ),
    },
}

DEFAULT_PROMPT_ID = "helpful"


def list_prompts() -> list[dict]:
    return [
        {"id": prompt_id, "name": item["name"], "text": item["text"]}
        for prompt_id, item in PROMPTS.items()
    ]


def get_prompt(prompt_id: str) -> dict:
    try:
        item = PROMPTS[prompt_id]
    except KeyError as exc:
        known = ", ".join(PROMPTS)
        raise ValueError(f"Unknown prompt '{prompt_id}'. Choose one of: {known}.") from exc
    return {"id": prompt_id, "name": item["name"], "text": item["text"]}
