# AI Chatbot

A small Python chatbot that sends natural-language messages to an OpenAI-compatible LLM API. Each request includes the system prompt plus earlier user and assistant turns, so later replies can use the conversation. A prompt lab sends the same question to two system prompts with no shared history, which makes the effect of the prompt easy to see.

## What it does

- Accepts a plain-language message from a terminal or a web page.
- Builds a chat-completions request: system prompt, then the full turn history, then the new message.
- Keeps that history for the next turn until you clear it.
- Lets you switch the system prompt without deleting earlier turns.
- Compares two prompts on one message so the answers differ only by the instruction.

## Setup

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

macOS or Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

To install the exact package versions this project was built with, use the pinned list instead of `requirements.txt`:

```bash
pip install -r requirements-lock.txt
```

The `.venv` folder itself is not committed. It is machine-specific, so each person creates their own from these files.

Edit `.env`:

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEY` | API key. Required. For a local Ollama server, any non-empty placeholder works. |
| `LLM_BASE_URL` | OpenAI-compatible base URL. Default `https://api.openai.com/v1`. |
| `LLM_MODEL` | Model name on that server. Default `gpt-4o-mini`. |

Examples of `LLM_BASE_URL`:

- OpenAI: `https://api.openai.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- Ollama: `http://localhost:11434/v1`

`.env` is gitignored. Do not commit your key.

## Run the terminal chat

```bash
python -m app
```

```text
you> What is a Python list?
you> How is that different from a tuple?
you> /prompt concise
you> How is that different from a tuple?
you> /compare concise socratic What is an API?
you> /reset
you> /quit
```

`/prompt` replaces the system instruction and keeps the existing turns. `/compare` does not use that history.

## Run the web page

```bash
python -m app.web
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The left side is the multi-turn conversation. The right side is the prompt lab.

## Tests

```bash
python -m unittest discover -s tests
```

The tests fake the model call. They check that later requests include earlier turns, that a prompt switch changes the system message, and that comparison calls use separate prompts.

## Layout

```text
app/chat.py      conversation history and prompt comparison
app/llm.py       chat-completions request
app/prompts.py   the system prompts you can switch
app/cli.py       terminal commands
app/web.py       browser UI and JSON API
```
