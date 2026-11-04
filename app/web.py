"""Small web UI for multi-turn chat and prompt comparison."""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from app.chat import Conversation, clean_message, compare_prompts
from app.config import describe_settings
from app.llm import complete
from app.prompts import DEFAULT_PROMPT_ID, list_prompts

ROOT = Path(__file__).resolve().parent.parent
app = Flask(
    __name__,
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
)


def _error(message: str, status: int):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/status")
def status():
    return jsonify(describe_settings())


@app.get("/api/prompts")
def prompts():
    return jsonify({"prompts": list_prompts(), "default": DEFAULT_PROMPT_ID})


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    prompt_id = body.get("prompt_id") or DEFAULT_PROMPT_ID
    history = body.get("history") or []
    if not isinstance(history, list):
        return _error("history must be a list.", 400)
    try:
        message = clean_message(body.get("message", ""))
        conversation = Conversation(prompt_id)
    except ValueError as exc:
        return _error(str(exc), 400)

    for turn in history:
        if not isinstance(turn, dict):
            return _error("Each history turn must be an object.", 400)
        role = turn.get("role")
        content = turn.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            return _error("History turns need role user|assistant and string content.", 400)
        conversation.turns.append({"role": role, "content": content})

    try:
        reply = conversation.ask(message, complete)
    except RuntimeError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        return _error(f"The model request failed: {exc}", 502)

    return jsonify(
        {
            "reply": reply,
            "prompt_id": conversation.prompt_id,
            "history": conversation.turns,
        }
    )


@app.post("/api/compare")
def compare():
    body = request.get_json(silent=True) or {}
    try:
        result = compare_prompts(
            body.get("message", ""),
            body.get("prompt_a") or "helpful",
            body.get("prompt_b") or "concise",
            complete,
        )
    except ValueError as exc:
        return _error(str(exc), 400)
    except RuntimeError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        return _error(f"The model request failed: {exc}", 502)
    return jsonify(result)


def main() -> None:
    # Import for a friendly startup check message; the request handlers report a missing key.
    info = describe_settings()
    if not info["configured"]:
        print("LLM_API_KEY is not set. The page will load, and chat requests will explain how to configure .env.")
    else:
        print(f"Using model {info['model']} at {info['base_url']}")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
