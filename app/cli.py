"""Terminal chat with slash commands for prompts and comparison."""

import shlex

from app.chat import Conversation, compare_prompts
from app.prompts import DEFAULT_PROMPT_ID, list_prompts

HELP = """
Commands:
  /help                         show this list
  /prompts                      list system prompts
  /prompt <id>                  switch the system prompt (history is kept)
  /reset                        clear conversation history
  /compare <id> <id> <message>  answer one message under two prompts
  /quit                         exit
""".strip()


def _print_prompts() -> None:
    for item in list_prompts():
        print(f"  {item['id']:10} {item['name']}")
        print(f"             {item['text']}")


def run() -> None:
    conversation = Conversation(DEFAULT_PROMPT_ID)
    print("AI chatbot. Type a message, or /help.")
    print(f"System prompt: {conversation.prompt_id}")
    while True:
        try:
            line = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return
        if not line:
            continue
        if line in {"/quit", "/exit"}:
            print("bye")
            return
        if line == "/help":
            print(HELP)
            continue
        if line == "/prompts":
            _print_prompts()
            continue
        if line == "/reset":
            conversation.reset()
            print("History cleared.")
            continue
        if line.startswith("/prompt "):
            prompt_id = line.split(maxsplit=1)[1].strip()
            try:
                conversation.set_prompt(prompt_id)
            except ValueError as exc:
                print(exc)
            else:
                print(f"System prompt is now {conversation.prompt_id}. Earlier turns are still in context.")
            continue
        if line.startswith("/compare "):
            _run_compare(line)
            continue
        if line.startswith("/"):
            print("Unknown command. Type /help.")
            continue
        try:
            reply = conversation.ask(line)
        except Exception as exc:
            print(f"error: {exc}")
            if conversation.turns and conversation.turns[-1]["role"] == "user":
                conversation.turns.pop()
            continue
        print(f"\nbot> {reply}")


def _run_compare(line: str) -> None:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        print(f"Could not parse command: {exc}")
        return
    if len(parts) < 4:
        print("Usage: /compare <prompt-id> <prompt-id> <message>")
        return
    _, prompt_a, prompt_b, *words = parts
    try:
        result = compare_prompts(" ".join(words), prompt_a, prompt_b)
    except Exception as exc:
        print(f"error: {exc}")
        return
    print(f"\n[{result['a']['name']}]\n{result['a']['reply']}")
    print(f"\n[{result['b']['name']}]\n{result['b']['reply']}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
