const state = { history: [], prompts: [] };

const transcript = document.querySelector("#transcript");
const promptSelect = document.querySelector("#prompt");
const promptText = document.querySelector("#prompt-text");
const chatForm = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message");
const chatError = document.querySelector("#chat-error");
const compareForm = document.querySelector("#compare-form");
const compareError = document.querySelector("#compare-error");
const results = document.querySelector("#compare-results");
const status = document.querySelector("#status");

function showError(node, message) {
  node.hidden = !message;
  node.textContent = message || "";
}

function renderTranscript() {
  transcript.replaceChildren();
  if (state.history.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No messages yet. What you send next is stored and sent back with later turns.";
    transcript.append(empty);
    return;
  }
  for (const turn of state.history) {
    const bubble = document.createElement("div");
    bubble.className = `bubble ${turn.role}`;
    const who = document.createElement("span");
    who.className = "who";
    who.textContent = turn.role === "user" ? "You" : "Assistant";
    bubble.append(who, document.createTextNode(turn.content));
    transcript.append(bubble);
  }
  transcript.scrollTop = transcript.scrollHeight;
}

function selectedPrompt() {
  return state.prompts.find((item) => item.id === promptSelect.value);
}

function fillSelect(select, value) {
  select.replaceChildren();
  for (const item of state.prompts) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name;
    select.append(option);
  }
  select.value = value;
}

async function readJson(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }
  return data;
}

promptSelect.addEventListener("change", () => {
  const prompt = selectedPrompt();
  promptText.textContent = prompt ? prompt.text : "";
});

document.querySelector("#clear").addEventListener("click", () => {
  state.history = [];
  showError(chatError, "");
  renderTranscript();
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  const button = chatForm.querySelector("button[type=submit]");
  button.disabled = true;
  showError(chatError, "");
  try {
    const data = await readJson(await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        prompt_id: promptSelect.value,
        history: state.history,
      }),
    }));
    state.history = data.history;
    messageInput.value = "";
    renderTranscript();
  } catch (error) {
    showError(chatError, error.message);
  } finally {
    button.disabled = false;
  }
});

compareForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = compareForm.querySelector("button[type=submit]");
  button.disabled = true;
  showError(compareError, "");
  try {
    const data = await readJson(await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: document.querySelector("#compare-message").value,
        prompt_a: document.querySelector("#prompt-a").value,
        prompt_b: document.querySelector("#prompt-b").value,
      }),
    }));
    document.querySelector("#name-a").textContent = data.a.name;
    document.querySelector("#reply-a").textContent = data.a.reply;
    document.querySelector("#name-b").textContent = data.b.name;
    document.querySelector("#reply-b").textContent = data.b.reply;
    results.hidden = false;
  } catch (error) {
    results.hidden = true;
    showError(compareError, error.message);
  } finally {
    button.disabled = false;
  }
});

async function init() {
  renderTranscript();
  try {
    const [promptData, statusData] = await Promise.all([
      readJson(await fetch("/api/prompts")),
      readJson(await fetch("/api/status")),
    ]);
    state.prompts = promptData.prompts;
    fillSelect(promptSelect, promptData.default);
    fillSelect(document.querySelector("#prompt-a"), "helpful");
    fillSelect(document.querySelector("#prompt-b"), "concise");
    promptText.textContent = selectedPrompt().text;
    status.textContent = statusData.configured
      ? `${statusData.model} · ${statusData.base_url}`
      : "Add LLM_API_KEY to a .env file before sending.";
  } catch (error) {
    status.textContent = error.message;
  }
}

init();
