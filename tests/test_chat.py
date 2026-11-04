import unittest
from unittest.mock import patch

from app.chat import Conversation, compare_prompts
from app.web import app


class ConversationTests(unittest.TestCase):
    def test_second_turn_includes_earlier_context(self):
        seen = []

        def fake_complete(messages):
            seen.append(messages)
            return f"reply-{len(seen)}"

        chat = Conversation("concise")
        self.assertEqual(chat.ask("What is a list?", fake_complete), "reply-1")
        self.assertEqual(chat.ask("Give an example.", fake_complete), "reply-2")

        second = seen[1]
        self.assertEqual(second[0]["role"], "system")
        self.assertIn("one or two sentences", second[0]["content"])
        self.assertEqual(second[1], {"role": "user", "content": "What is a list?"})
        self.assertEqual(second[2], {"role": "assistant", "content": "reply-1"})
        self.assertEqual(second[3], {"role": "user", "content": "Give an example."})

    def test_switching_prompt_keeps_turns_and_replaces_system_text(self):
        chat = Conversation("helpful")
        chat.turns.append({"role": "user", "content": "hi"})
        chat.set_prompt("socratic")
        messages = chat.messages()
        self.assertIn("guiding question", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "hi")

    def test_failed_reply_can_drop_the_unanswered_user_turn(self):
        chat = Conversation()

        def fail(_messages):
            raise RuntimeError("offline")

        with self.assertRaises(RuntimeError):
            chat.ask("hello", fail)
        self.assertEqual(chat.turns[-1]["role"], "user")
        chat.turns.pop()
        self.assertEqual(chat.turns, [])

    def test_compare_uses_isolated_prompts(self):
        calls = []

        def fake_complete(messages):
            calls.append(messages[0]["content"])
            return messages[0]["content"][:12]

        result = compare_prompts("Explain DNS", "concise", "technical", fake_complete)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0], calls[1])
        self.assertEqual(result["a"]["id"], "concise")
        self.assertEqual(result["b"]["id"], "technical")
        self.assertTrue(all(len(call_messages) == 2 for call_messages in (
            [{"role": "system", "content": calls[0]}, {"role": "user", "content": "Explain DNS"}],
        )))

    def test_unknown_prompt_and_blank_message(self):
        with self.assertRaises(ValueError):
            Conversation("nope")
        with self.assertRaises(ValueError):
            compare_prompts("   ", "helpful", "concise", lambda _m: "x")


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_prompts_and_missing_key_error(self):
        prompts = self.client.get("/api/prompts")
        self.assertEqual(prompts.status_code, 200)
        ids = [item["id"] for item in prompts.get_json()["prompts"]]
        self.assertIn("socratic", ids)

        with patch.dict("os.environ", {"LLM_API_KEY": ""}, clear=False):
            response = self.client.post("/api/chat", json={"message": "hi", "history": []})
        self.assertEqual(response.status_code, 400)
        self.assertIn("LLM_API_KEY", response.get_json()["error"])

    def test_chat_returns_model_reply(self):
        with patch("app.web.complete", return_value="mocked answer") as complete:
            response = self.client.post(
                "/api/chat",
                json={
                    "message": "Next question",
                    "prompt_id": "technical",
                    "history": [
                        {"role": "user", "content": "First"},
                        {"role": "assistant", "content": "Earlier answer"},
                    ],
                },
            )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["reply"], "mocked answer")
        sent = complete.call_args.args[0]
        self.assertEqual(sent[0]["role"], "system")
        self.assertIn("technical reviewer", sent[0]["content"])
        self.assertEqual(sent[-1]["content"], "Next question")
        self.assertEqual(len(body["history"]), 4)


if __name__ == "__main__":
    unittest.main()
